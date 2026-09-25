"""Stage 1: parliamentary questions and answers (Houses of the Oireachtas).

Official open-data API: https://api.oireachtas.ie/v1/swagger.json
Endpoint /questions returns each PQ with its topic heading (debateSection) and,
with show_answers=true, the Minister's full answer text - which is where the
statistical tables laid before the Houses actually live.

There is no server-side text filter, so we page through every PQ in the window
and keep only those whose topic heading or question text concerns migration.
Each retained PQ keeps its own citable oireachtas.ie URL.

Resumable: one JSON file per month under data/raw/oireachtas/; re-running skips
months already fetched.

Updating an existing harvest:
    python scripts/07_fetch_oireachtas_pqs.py --refresh 5
re-fetches the most recent N months even if already on disk. Answers are often
published days or weeks after the question is asked, so the last few months keep
growing and a plain re-run (which skips existing files) would miss them.
"""
import calendar, datetime, json, re, sys, time, pathlib, urllib.parse, urllib.request, urllib.error
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import HEADERS

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "data" / "raw" / "oireachtas"
OUTDIR.mkdir(parents=True, exist_ok=True)
API = "https://api.oireachtas.ie/v1/questions"

START_YEAR = 2016
# Always run up to the current month rather than a hardcoded end, so re-running
# later picks up everything published since.
_today = datetime.date.today()
END = (_today.year, _today.month)

# --refresh N : re-fetch the most recent N months even if cached.
REFRESH = 0
if "--refresh" in sys.argv:
    REFRESH = int(sys.argv[sys.argv.index("--refresh") + 1])

# Topic headings the Oireachtas itself assigns to migration PQs, plus free-text
# fallbacks for questions filed under a generic heading.
TOPIC_RE = re.compile(
    r"asylum|citizenship|naturalis|naturaliz|immigration|international protection|"
    r"refugee|deportation|visa|work permit|employment permit|migrant|migration|"
    r"direct provision|permission to remain|family reunification|residence permit|"
    r"eu treaty rights|temporary protection|ipas|accommodation for", re.I)


def api_get(params, retries=4):
    url = API + "?" + urllib.parse.urlencode(params, doseq=True)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=300) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as exc:                          # noqa: BLE001
            if attempt == retries - 1:
                print(f"    ERROR {exc} :: {url}", flush=True)
                return None
            time.sleep(5 * (attempt + 1))


def months(y0, end):
    y, m = y0, 1
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def strip_tags(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def matches(q):
    sect = (q.get("debateSection") or {}).get("showAs") or ""
    return bool(TOPIC_RE.search(sect) or TOPIC_RE.search(q.get("showAs") or ""))


all_months = list(months(START_YEAR, END))
refresh_set = set(all_months[-REFRESH:]) if REFRESH else set()
if refresh_set:
    print(f"refreshing {len(refresh_set)} most recent months: "
          f"{', '.join(f'{y}-{m:02d}' for y, m in sorted(refresh_set))}")

total_kept, prior_counts = 0, {}
for y, m in all_months:
    out = OUTDIR / f"pqs_{y}_{m:02d}.json"
    if out.exists():
        existing = len(json.loads(out.read_text()))
        if (y, m) not in refresh_set:
            total_kept += existing
            continue
        prior_counts[(y, m)] = existing
    d0 = f"{y}-{m:02d}-01"
    d1 = f"{y}-{m:02d}-{calendar.monthrange(y, m)[1]:02d}"
    kept, skip, seen, failed = [], 0, 0, False
    while True:
        js = api_get({"date_start": d0, "date_end": d1, "show_answers": "true",
                      "limit": 1000, "skip": skip})
        if not js:
            failed = True
            break
        results = js.get("results", [])
        if not results:
            break
        seen += len(results)
        for r in results:
            q = r.get("question") or {}
            if not matches(q):
                continue
            date = q.get("date")
            qno = q.get("questionNumber")
            kept.append({
                "date": date,
                "question_number": qno,
                "chamber": (q.get("house") or {}).get("showAs"),
                "topic": (q.get("debateSection") or {}).get("showAs"),
                "asked_by": (q.get("by") or {}).get("showAs"),
                "answered_by": (q.get("to") or {}).get("showAs"),
                "question_type": q.get("questionType"),
                "question": strip_tags(q.get("showAs")),
                "answer": strip_tags(q.get("answerText")),
                "uri": q.get("uri"),
                # Citable public page for this exact PQ:
                "url": f"https://www.oireachtas.ie/en/debates/question/{date}/{qno}/"
                       if date and qno else None,
            })
        total = js.get("head", {}).get("counts", {}).get("resultCount", 0)
        skip += 1000
        if skip >= total:
            break
    if failed:
        print(f"{y}-{m:02d}: request failed, not caching - rerun to retry", flush=True)
        continue
    out.write_text(json.dumps(kept, indent=1))
    total_kept += len(kept)
    delta = ""
    if (y, m) in prior_counts:
        d = len(kept) - prior_counts[(y, m)]
        delta = f"  [was {prior_counts[(y, m)]:,}, {d:+,}]"
    print(f"{y}-{m:02d}: scanned {seen:6,} PQs, kept {len(kept):5,}  "
          f"(running total {total_kept:,}){delta}", flush=True)

print(f"\nDONE. {total_kept:,} migration-related PQs saved to {OUTDIR}")

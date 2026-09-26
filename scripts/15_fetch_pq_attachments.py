"""Stage 1 (extension): supporting documents attached to parliamentary answers.

When a PQ answer is too large to print in the record, the Minister supplies a
spreadsheet, and the Oireachtas publishes it at
  https://data.oireachtas.ie/ie/oireachtas/debates/questions/supportingDocumentation/...
The /questions API strips these links out of answerText, so they are only
visible on the PQ's own web page. These attachments are the only public source
of employment permit data broken down BY PERMIT TYPE (Critical Skills, General,
Intra-Company Transfer, etc.) - the Department's annual spreadsheets are not
broken down that way.

Scope: by default every permit-related question in the harvest. Pass
    --since YYYY-MM-DD
to additionally scrape ALL migration PQs from that date onwards, which is how
recent citizenship/naturalisation attachments are picked up (for example the
country-of-origin breakdowns attached to PQ 2026-09-16 #891).

Resumable: pages already scraped are recorded in _scraped_pages.json and skipped,
so re-running only costs the new pages.
"""
import json, glob, re, sys, time, pathlib, urllib.request
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch, HEADERS

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "data" / "raw" / "pq_attachments" / "_scraped_pages.json"
STATE.parent.mkdir(parents=True, exist_ok=True)

TOPIC = re.compile(r"work permit|employment permit|labour market|critical skill", re.I)
TEXT = re.compile(r"employment permit|critical skills", re.I)

SINCE = None
if "--since" in sys.argv:
    SINCE = sys.argv[sys.argv.index("--since") + 1]
DOC = re.compile(r'href="(https://data\.oireachtas\.ie/[^"]*supportingDocumentation/[^"]+)"')

pqs = []
for f in sorted(glob.glob(str(ROOT / "data/raw/oireachtas/pqs_*.json"))):
    pqs.extend(json.load(open(f)))
def in_scope(q):
    if TOPIC.search(q["topic"] or "") or TEXT.search((q.get("answer") or "") + (q.get("question") or "")):
        return True
    # everything in the migration harvest from the --since date onwards
    return bool(SINCE and (q.get("date") or "") >= SINCE)


cand = [q for q in pqs if in_scope(q)]
# newest first: recent answers are far likelier to carry attachments
cand.sort(key=lambda q: (q.get("date") or ""), reverse=True)
print(f"{len(cand)} PQs in scope to check for attachments"
      + (f" (all migration PQs since {SINCE}, plus permit-related across the full harvest)" if SINCE else ""))

seen = json.loads(STATE.read_text()) if STATE.exists() else {}
found = {}
for i, q in enumerate(cand, 1):
    url = q["url"]
    if not url:
        continue
    if url in seen:
        for d in seen[url]:
            found[d] = q
        continue
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            html = r.read().decode("utf-8", "replace")
        # Some pages escape underscores in the href ("...2026-07-28\_pq-2407..."),
        # which 403s if requested verbatim; strip the escaping backslashes.
        docs = sorted({d.replace("\\", "") for d in DOC.findall(html)})
    except Exception as exc:                                   # noqa: BLE001
        print(f"  page fail {url}: {exc}", flush=True)
        continue
    seen[url] = docs
    for d in docs:
        found[d] = q
    if i % 200 == 0:
        STATE.write_text(json.dumps(seen))
        print(f"  {i}/{len(cand)} pages scraped, {len(found)} distinct attachments so far", flush=True)
    time.sleep(0.25)

STATE.write_text(json.dumps(seen))
print(f"\n{len(found)} distinct supporting documents found; downloading")

for url, q in sorted(found.items()):
    name = url.rsplit("/", 1)[-1]
    fetch(url, f"pq_attachments/{name}", source_page=q["url"],
          note=f"Supporting document to PQ {q['date']} #{q['question_number']} ({q['topic']})")

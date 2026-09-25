"""Stage 1: curated annual series taken from named parliamentary answers.

Where a statistic has no machine-readable release (naturalisation is the main
case), the authoritative published figure is the table the Minister lays before
the Dail in answer to a PQ. Each series below names the exact PQ; the values are
parsed from that answer's text rather than typed in, and every row carries the
PQ's public URL so it can be checked.
"""
import csv, glob, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"

# (series, unit, PQ date, PQ number, regex matching the table's COLUMN HEADER).
# The scan starts after the header so that years appearing in a caption
# ("IP Applications 2011 to 2026") are not mistaken for data.
TARGETS = [
    ("International protection applications received", "applications",
     "2026-06-23", 515, r"IP Applications 2011 to 2026\*?"),
    ("Certificates of naturalisation issued", "certificates",
     "2023-11-28", 424, r"Year\s+Total\b"),
    ("Citizenship (naturalisation) applications received", "applications",
     "2026-09-07", 2397, r"Year\s+Applications Received"),
    ("International protection refusals (refugee status and subsidiary protection)", "refusals",
     "2022-12-06", 481, r"Year\s+Total number of refusals of Refugee Status and Subsidiary Protection Status"),
    ("Deportation orders issued", "orders",
     "2021-11-23", 474, r"Year\s+DOs Issued"),
    # superseded by the 24 Sep 2026 answer below, which extends the series to 2026
    ("Deportation orders revoked", "orders",
     "2026-09-24", 378, r"Year\s+Deportation Orders revoked"),
    ("Certificates of naturalisation refused", "refusals",
     "2026-09-16", 891, r"Year\s+Refused"),
    ("IPAT appeals completed", "appeals",
     "2026-09-24", 381, r"Year\s+Total Completed"),
    ("Judicial reviews against IPAT decisions", "judicial reviews",
     "2026-09-24", 381, r"Year\s+Judicial Reviews taken against decisions of IPAT"),
    ("Citizenship applications: median processing time", "months",
     "2026-09-17", 277, r"Year\s+Median Processing time in months"),
    ("Declarations of intention to retain Irish citizenship (Form 5)", "declarations",
     "2026-09-17", 274, r"Year\s+Form 5"),
    ("Employment permits issued (as stated to the Dail)", "permits",
     "2026-06-23", 289, r"Year\s+Number of Employment Permits Issued"),
]

pqs = {}
for f in sorted(glob.glob(str(ROOT / "data/raw/oireachtas/pqs_*.json"))):
    for q in json.load(open(f)):
        pqs[(q["date"], q["question_number"])] = q

PAIR = re.compile(
    r"(20[0-2]\d)"                                        # the year
    r"((?:\s*(?:\*+|YTD|\([^)]{1,18}\)))*)"              # annotation: "YTD", "*", "(16/09/26)", "(to date)"
    r"\s+([\d][\d,]{0,12})")                              # the value

# An annotation like "(YTD)", "(to date)" or an explicit cut-off date means the
# year is incomplete, so the figure must not be compared with full years.
PARTIAL = re.compile(r"YTD|to date|\d{1,2}[/-]\d{1,2}", re.I)
# Some answers mark the incomplete year only in the table's caption
# ("... from 2011 to 31 May 2026", "... and to date in 2026"), leaving the row
# itself annotated with a bare asterisk or nothing. In that case the series'
# final year is the partial one.
PARTIAL_CAPTION = re.compile(r"to date|YTD|to \d{1,2}\s+\w+\s+20\d\d|as at|as of", re.I)

rows = []
for series, unit, date, qno, anchor in TARGETS:
    q = pqs.get((date, qno))
    if not q:
        print(f"!! PQ {date} #{qno} not in harvest")
        continue
    ans = q["answer"]
    m = re.search(anchor, ans)
    if not m:
        print(f"!! anchor not found for '{series}' in {date} #{qno}")
        continue
    caption = ans[max(0, m.start() - 320):m.end()]
    caption_partial = bool(PARTIAL_CAPTION.search(caption))
    tail = ans[m.end():]
    prev, n = None, 0
    target_rows = []
    for pm in PAIR.finditer(tail):
        y = int(pm.group(1))
        annot = re.sub(r"\s+", " ", pm.group(2)).strip()
        v = int(pm.group(3).replace(",", ""))
        # stop once the year sequence stops advancing - that means the table ended
        if prev is not None and not (prev < y <= prev + 3):
            break
        prev = y
        n += 1
        rows.append({"series": series, "unit": unit, "year": y, "value": v,
                     "year_annotation": annot,
                     "is_partial_year": bool(PARTIAL.search(annot)),
                     "source": "Parliamentary answer (Houses of the Oireachtas)",
                     "pq_date": date, "pq_number": qno,
                     "answered_by": q["answered_by"], "topic": q["topic"],
                     "pq_url": q["url"]})
        target_rows.append(rows[-1])

    # caption-level partial marker applies to the last year in the table
    if caption_partial and target_rows:
        last = max(target_rows, key=lambda r: r["year"])
        if not last["is_partial_year"]:
            last["is_partial_year"] = True
            last["year_annotation"] = (last["year_annotation"] + " [part-year per table caption]").strip()
    print(f"{series[:60]:62} {n:3} years from PQ {date} #{qno}"
          + ("  (final year part-year)" if caption_partial else ""))

rows.sort(key=lambda r: (r["series"], r["year"]))
with open(OUT / "pq_curated_series.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nwrote pq_curated_series.csv ({len(rows)} rows)")
part = [r for r in rows if r["is_partial_year"]]
if part:
    print(f"\n{len(part)} part-year figures flagged (is_partial_year=True):")
    for r in sorted(part, key=lambda r: (r["series"], r["year"])):
        print(f"  {r['year']} {r['series'][:52]:54} {r['value']:>9,}  {r['year_annotation']}")

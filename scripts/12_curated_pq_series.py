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
    ("Deportation orders revoked", "orders",
     "2025-05-07", 316, r"Year\s+Deportation Orders revoked"),
    ("Employment permits issued (as stated to the Dail)", "permits",
     "2026-06-23", 289, r"Year\s+Number of Employment Permits Issued"),
]

pqs = {}
for f in sorted(glob.glob(str(ROOT / "data/raw/oireachtas/pqs_*.json"))):
    for q in json.load(open(f)):
        pqs[(q["date"], q["question_number"])] = q

PAIR = re.compile(r"(20[0-2]\d)(?:\s*\(to date\)\*?|\s*\*)?\s+([\d][\d,]{0,12})")

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
    tail = ans[m.end():]
    prev, n = None, 0
    for pm in PAIR.finditer(tail):
        y, v = int(pm.group(1)), int(pm.group(2).replace(",", ""))
        # stop once the year sequence stops advancing - that means the table ended
        if prev is not None and not (prev < y <= prev + 3):
            break
        prev = y
        n += 1
        rows.append({"series": series, "unit": unit, "year": y, "value": v,
                     "source": "Parliamentary answer (Houses of the Oireachtas)",
                     "pq_date": date, "pq_number": qno,
                     "answered_by": q["answered_by"], "topic": q["topic"],
                     "pq_url": q["url"]})
    print(f"{series[:60]:62} {n:3} years from PQ {date} #{qno}")

rows.sort(key=lambda r: (r["series"], r["year"]))
with open(OUT / "pq_curated_series.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"\nwrote pq_curated_series.csv ({len(rows)} rows)")

"""Stage 1: pull year-by-year tables out of parliamentary answers.

The Oireachtas API returns answer text with table markup stripped, so a table
laid before the House arrives as a run of "<year> <value>" pairs. We detect runs
of three or more such pairs, take the preceding sentence as the caption, and
keep the PQ's own URL against every figure.

These are machine-extracted from prose and are therefore marked as such: each
row carries the caption and the PQ link so any figure can be checked against the
original answer. They are a complement to, not a replacement for, the structured
sources (CSO / data.gov.ie / DETE).
"""
import csv, glob, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"

PAIR = r"(20[0-2]\d)(?:\s*\(to date\)|\s*\*)?\s+([\d][\d,]{0,12})"
RUN = re.compile(rf"(?:{PAIR}\s+){{2,}}{PAIR}")
PAIR_RE = re.compile(PAIR)

pqs = []
for f in sorted(glob.glob(str(ROOT / "data/raw/oireachtas/pqs_*.json"))):
    pqs.extend(json.load(open(f)))

rows, tables = [], 0
for q in pqs:
    ans = q.get("answer") or ""
    if not ans:
        continue
    for m in RUN.finditer(ans):
        block = m.group(0)
        pairs = PAIR_RE.findall(block)
        years = [int(y) for y, _ in pairs]
        # require a plausible ascending/descending run of distinct years
        if len(set(years)) < 3 or max(years) > 2026 or min(years) < 2000:
            continue
        caption = re.sub(r"\s+", " ", ans[max(0, m.start() - 260):m.start()]).strip()
        caption = caption[-240:]
        tables += 1
        for y, v in pairs:
            rows.append({
                "year": int(y),
                "value": int(v.replace(",", "")),
                "caption_before_table": caption,
                "topic": q["topic"],
                "pq_date": q["date"],
                "pq_number": q["question_number"],
                "answered_by": q["answered_by"],
                "pq_url": q["url"],
                "extraction": "machine-extracted from PQ answer text; verify at pq_url",
            })

with open(OUT / "pq_extracted_tables.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote pq_extracted_tables.csv: {tables:,} tables, {len(rows):,} year-value pairs")

import collections
print("\nby topic:")
for t, n in collections.Counter(r["topic"] for r in rows).most_common(15):
    print(f"  {n:6,}  {t}")

"""Stage 1: index the harvested parliamentary questions.

Produces a citable CSV (one row per PQ, with its oireachtas.ie URL) plus a
shortlist of answers that actually contain year-by-year statistics, which is
where the Department's own numbers are placed on the record.
"""
import csv, json, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "oireachtas"
OUT = ROOT / "data" / "processed"

pqs = []
for f in sorted(RAW.glob("pqs_*.json")):
    pqs.extend(json.loads(f.read_text()))
print(f"loaded {len(pqs):,} PQs from {len(list(RAW.glob('pqs_*.json')))} monthly files")

YEAR_RUN = re.compile(r"\b20(1[0-9]|2[0-6])\b")


def stats_score(ans):
    """Rough flag for 'this answer contains a multi-year statistical table'."""
    if not ans:
        return 0
    years = set(YEAR_RUN.findall(ans))
    numbers = re.findall(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{3,}\b", ans)
    return len(years) * 10 + min(len(numbers), 60)


rows = []
for q in pqs:
    ans = q.get("answer") or ""
    rows.append({
        "date": q["date"], "question_number": q["question_number"],
        "chamber": q["chamber"], "topic": q["topic"],
        "question_type": q["question_type"],
        "asked_by": q["asked_by"], "answered_by": q["answered_by"],
        "question": (q["question"] or "")[:600],
        "answer_chars": len(ans),
        "distinct_years_in_answer": len(set(YEAR_RUN.findall(ans))),
        "stats_score": stats_score(ans),
        "url": q["url"],
    })
rows.sort(key=lambda r: (r["date"], r["question_number"] or 0))

with open(OUT / "oireachtas_pq_index.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote oireachtas_pq_index.csv ({len(rows):,} rows)")

# Full text of the most statistics-dense answers, for traceable quoting.
top = sorted(pqs, key=lambda q: stats_score(q.get("answer") or ""), reverse=True)[:400]
with open(OUT / "oireachtas_pq_statistical_answers.json", "w", encoding="utf-8") as fh:
    json.dump(top, fh, indent=1)
print(f"wrote oireachtas_pq_statistical_answers.json (top {len(top)} data-bearing answers)")

print("\nTop 25 topics:")
for t, n in collections.Counter(r["topic"] for r in rows).most_common(25):
    print(f"  {n:6,}  {t}")
print("\nPQs per year:")
for y, n in sorted(collections.Counter(r["date"][:4] for r in rows).items()):
    print(f"  {y}: {n:,}")

"""Stage 1: cross-source validation.

Several indicators are published by two independent bodies. Comparing them is
the main quality check on both the sources and this repo's parsing.
"""
import csv, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"


def load(f):
    return list(csv.DictReader(open(P / f, encoding="utf-8")))


head = collections.defaultdict(dict)
for r in load("headline_series.csv"):
    head[r["indicator"]][int(r["year"])] = float(r["value"])
pq = collections.defaultdict(dict)
for r in load("pq_curated_series.csv"):
    # part-year figures must never be compared against full calendar years
    if r.get("is_partial_year") in ("True", "true"):
        continue
    pq[r["series"]][int(r["year"])] = float(r["value"])

CHECKS = [
    ("Employment permits issued",
     "DETE spreadsheets (parsed here)", head["Employment permits issued"],
     "Minister's answer, PQ 2026-06-23 #289", pq["Employment permits issued (as stated to the Dail)"],
     2015, 2025),
    ("Asylum / international protection applications",
     "Eurostat migr_asyappctza", head["Asylum applicants"],
     "Minister's answer, PQ 2026-06-23 #515", pq["International protection applications received"],
     2015, 2025),
    ("Acquisitions of citizenship / certificates of naturalisation",
     "Eurostat migr_acq", head["Acquisitions of Irish citizenship"],
     "Minister's answer, PQ 2023-11-28 #424", pq["Certificates of naturalisation issued"],
     2015, 2022),
]

out = []
for name, src_a, a, src_b, b, y0, y1 in CHECKS:
    print(f"\n=== {name} ===")
    print(f"  A = {src_a}")
    print(f"  B = {src_b}")
    print(f"  {'year':6}{'A':>10}{'B':>10}{'diff':>8}{'pct':>8}")
    for y in range(y0, y1 + 1):
        if y in a and y in b:
            d = a[y] - b[y]
            pct = 100 * d / b[y] if b[y] else 0
            print(f"  {y:<6}{a[y]:10,.0f}{b[y]:10,.0f}{d:+8,.0f}{pct:+7.2f}%")
            out.append({"check": name, "year": y, "source_a": src_a, "value_a": a[y],
                        "source_b": src_b, "value_b": b[y], "difference": d,
                        "pct_difference": round(pct, 3)})

with open(P / "cross_source_validation.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
    w.writeheader()
    w.writerows(out)
exact = sum(1 for r in out if r["difference"] == 0)
print(f"\nwrote cross_source_validation.csv: {len(out)} comparisons, "
      f"{exact} exact matches, max |diff| = {max(abs(r['pct_difference']) for r in out):.2f}%")

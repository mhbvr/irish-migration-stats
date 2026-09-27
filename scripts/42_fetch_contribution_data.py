"""Contribution evidence, step 1: official tables on what migrants contribute.

  CSO QLF48  Labour Force Survey - persons 15+ by ILO status and citizenship, 2021Q1-      (employment rates)
  CSO QLF59  Labour Force Survey - employment by citizenship and sector, 2019Q1-          (share of each sector; growth)
  CSO UA29   employees among arrivals from Ukraine, 2022-                                  (s.16A: Ukrainians at work)
  CSO UA30   social welfare beneficiaries among arrivals from Ukraine, 2022-              (s.16A: reliance over time)
  CSO UA20   employments of arrivals from Ukraine by sector                               (where they work)
Provenance for every download goes to data/raw/manifest.jsonl.
"""
import csv, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch
from jsonstat import flatten

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "contribution"
OUT.mkdir(parents=True, exist_ok=True)
CSO = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{m}/JSON-stat/2.0/en"
TABLES = {"QLF48": "LFS: persons 15+ by ILO economic status and citizenship",
          "QLF59": "LFS: persons in employment by citizenship and NACE sector",
          "UA29": "Employments and employees among arrivals from Ukraine",
          "UA30": "Social welfare beneficiaries among arrivals from Ukraine",
          "UA20": "Employments of arrivals from Ukraine by sector"}
for m, note in TABLES.items():
    p = fetch(CSO.format(m=m), f"contribution/cso_{m}.json", source_page=f"https://data.cso.ie/table/{m}", note=f"CSO {m}: {note}")
    if not p:
        continue
    rows = flatten(json.loads(p.read_text()))
    with open(OUT / f"cso_{m}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    print(f"  -> cso_{m}.csv  {len(rows):,} rows")

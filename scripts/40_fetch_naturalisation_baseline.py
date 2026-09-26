"""Naturalisation baseline, step 1: download the additional official tables
needed to measure the population and processes the 2026 Bill would change.

  CSO F5065   Census 2022 - non-Irish residents by country of citizenship   (denominator for naturalisation rates)
  CSO F5015   Census 2022 - ability to speak English, by citizenship         (language test)
  CSO PEA27   non-EU/EFTA/candidate-country citizens, 2023-2024, by age     (current non-EU stock)
  CSO VSAS80  births registered by nationality of mother                    (s.6B - citizenship at birth)
  Eurostat migr_acqs     naturalisation rate: acquisitions per 100 non-citizen residents (IE and EU27)
  Eurostat migr_resvalid valid residence permits by reason and length        (the pipeline of future applicants)
  Eurostat migr_reslong  long-term residents                                  (settled non-EU population)

Every file is logged in data/raw/manifest.jsonl (URL, time, SHA-256) and flattened to
data/processed/naturalisation_baseline/<name>.csv.
"""
import csv, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch
from jsonstat import flatten

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed" / "naturalisation_baseline"
OUT.mkdir(parents=True, exist_ok=True)
CSO = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{m}/JSON-stat/2.0/en"
EUR = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}?geo={geo}&format=JSON&lang=EN"

TABLES = [
    ("cso_F5065", CSO.format(m="F5065"), "https://data.cso.ie/table/F5065", "Census 2022: non-Irish citizens usually resident, by citizenship"),
    ("cso_F5015", CSO.format(m="F5015"), "https://data.cso.ie/table/F5015", "Census 2022: speakers of other languages, by ability to speak English and citizenship"),
    ("cso_PEA27", CSO.format(m="PEA27"), "https://data.cso.ie/table/PEA27", "Non-EU/EFTA/candidate-country citizens, 2023-2024"),
    ("cso_VSAS80", CSO.format(m="VSAS80"), "https://data.cso.ie/table/VSAS80", "Births registered, by nationality of mother"),
    ("eurostat_migr_acqs_IE", EUR.format(ds="migr_acqs", geo="IE"), "https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en", "Naturalisation rate, Ireland"),
    # Eurostat publishes no EU aggregate for this rate, so take every country and rank Ireland
    ("eurostat_migr_acqs_all", "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/migr_acqs?format=JSON&lang=EN&sex=T",
     "https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en", "Naturalisation rate, all reporting countries"),
    ("eurostat_migr_resvalid_IE", EUR.format(ds="migr_resvalid", geo="IE"), "https://ec.europa.eu/eurostat/databrowser/view/migr_resvalid/default/table?lang=en", "Valid residence permits, Ireland"),
    ("eurostat_migr_reslong_IE", EUR.format(ds="migr_reslong", geo="IE"), "https://ec.europa.eu/eurostat/databrowser/view/migr_reslong/default/table?lang=en", "Long-term residents, Ireland"),
]
for name, url, page, note in TABLES:
    p = fetch(url, f"naturalisation_baseline/{name}.json", source_page=page, note=note)
    if not p:
        continue
    rows = flatten(json.loads(p.read_text()), codes=True)
    if not rows:
        print(f"  !! {name}: the API returned no values")
        continue
    with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"  -> {name}.csv  {len(rows):,} rows")

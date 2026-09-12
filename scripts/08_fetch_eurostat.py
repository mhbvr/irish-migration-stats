"""Stage 1: Eurostat cross-check series for Ireland.

Ireland's Immigration Service Delivery supplies asylum and managed-migration
data to Eurostat under statutory EU reporting obligations - the Department of
Justice's own statistics page points users here:
  https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/publications/departmental-data-and-statistical-reports/
These give a consistent annual series where the Irish publications are either
stale (the DoJ international-protection CSV stops in March 2021) or published
only as chart-based PDFs.

API: https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/<dataset>?geo=IE&format=JSON
"""
import csv, json, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"
API = "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/{ds}?geo=IE&format=JSON&lang=EN"

DATASETS = {
    "migr_asyappctza": "Asylum applicants by type, citizenship, age and sex (annual)",
    "migr_acq": "Acquisition of citizenship by age, sex and former citizenship (annual)",
    "migr_resfirst": "First residence permits by reason, validity and citizenship (annual)",
}


def flatten(js):
    """JSON-stat 2.0 -> list of dict rows (nulls dropped)."""
    import itertools
    dims, sizes = js["id"], js["size"]
    labels, cats = {}, {}
    for d in dims:
        dd = js["dimension"][d]
        labels[d] = dd.get("label", d)
        idx = dd["category"]["index"]
        order = sorted(idx, key=lambda k: idx[k]) if isinstance(idx, dict) else list(idx)
        lab = dd["category"].get("label", {})
        cats[d] = [(k, lab.get(k, k)) for k in order]
    values = js["value"]
    rows = []
    for flat, combo in enumerate(itertools.product(*[range(s) for s in sizes])):
        v = values.get(str(flat)) if isinstance(values, dict) else values[flat]
        if v is None:
            continue
        row = {}
        for d, i in zip(dims, combo):
            code, lbl = cats[d][i]
            row[labels[d]] = lbl
            row[labels[d] + "_code"] = code
        row["value"] = v
        rows.append(row)
    return rows


for ds, desc in DATASETS.items():
    url = API.format(ds=ds)
    page = f"https://ec.europa.eu/eurostat/databrowser/view/{ds}/default/table?lang=en"
    print(f"[{ds}] {desc}")
    path = fetch(url, f"eurostat/{ds}.json", source_page=page, note=f"Eurostat {ds} (geo=IE): {desc}")
    if not path:
        continue
    rows = flatten(json.loads(path.read_text()))
    cols = [c for c in rows[0] if c != "value"] + ["value"]
    with open(OUT / f"eurostat_{ds}_IE.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"  -> eurostat_{ds}_IE.csv  {len(rows):,} rows")

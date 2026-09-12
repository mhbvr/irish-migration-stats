"""Stage 1: CSO (Central Statistics Office) PxStat tables via the open REST API.

API docs: https://data.cso.ie/  |  endpoint pattern:
  https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<MATRIX>/JSON-stat/2.0/en
Each matrix also has a human-readable landing page at https://data.cso.ie/table/<MATRIX>
which is what we cite in the report so figures can be checked by hand.
"""
import csv, itertools, json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/{m}/JSON-stat/2.0/en"

MATRICES = {
    "PEA03":  "Estimated migration by age group, sex and inward/outward flow (April, annual)",
    "PEA18":  "Estimated migration by sex and country of origin/destination (April, annual)",
    "PEA23":  "Estimated emigration by sex and citizenship (April, annual)",
    "PEA24":  "Estimated immigration by sex and citizenship (April, annual)",
    "PEA27":  "Persons with citizenship of countries other than EU/EFTA/EU candidate countries",
    "MEASQ01": "Estimated migration flows (experimental, admin-data based)",
    "MEASQ02": "Estimated migration flows (experimental, admin-data based)",
    "MEASQ03": "Estimated migration flows (experimental, admin-data based)",
    "FNA06":  "PPSN allocations to foreign nationals",
    "FNA10":  "PPSN allocations to foreign nationals",
    "IAIP01": "International protection applicants identified using administrative data",
    "IAIP02": "International protection applicants identified using administrative data",
    "IAIP11": "International protection applicants identified using administrative data",
    "IAIP12": "International protection applicants identified using administrative data",
}


def flatten(js):
    """JSON-stat 2.0 -> list of dict rows (one per cell, nulls dropped)."""
    dims = js["id"]
    sizes = js["size"]
    labels, cat_labels = {}, {}
    for d in dims:
        dd = js["dimension"][d]
        labels[d] = dd.get("label", d)
        idx = dd["category"]["index"]
        if isinstance(idx, dict):
            order = sorted(idx, key=lambda k: idx[k])
        else:
            order = list(idx)
        lab = dd["category"].get("label", {})
        cat_labels[d] = [lab.get(k, k) for k in order]

    values = js["value"]
    rows = []
    for flat, combo in enumerate(itertools.product(*[range(s) for s in sizes])):
        v = values.get(str(flat)) if isinstance(values, dict) else values[flat]
        if v is None:
            continue
        row = {labels[d]: cat_labels[d][i] for d, i in zip(dims, combo)}
        row["value"] = v
        rows.append(row)
    return rows


summary = []
for matrix, desc in MATRICES.items():
    url = API.format(m=matrix)
    page = f"https://data.cso.ie/table/{matrix}"
    print(f"[{matrix}] {desc}")
    path = fetch(url, f"cso/{matrix}.json", source_page=page, note=f"CSO {matrix}: {desc}")
    if not path:
        continue
    js = json.loads(path.read_text())
    rows = flatten(js)
    if not rows:
        print("  (no data cells)")
        continue
    cols = [c for c in rows[0] if c != "value"] + ["value"]
    with open(OUT / f"cso_{matrix}.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    yrs = [r.get("Year") or r.get("Quarter") or "" for r in rows]
    yrs = sorted({y for y in yrs if y})
    span = f"{yrs[0]}–{yrs[-1]}" if yrs else "n/a"
    print(f"  -> cso_{matrix}.csv  {len(rows):,} rows, period {span}")
    summary.append({"matrix": matrix, "label": js.get("label", ""), "description": desc,
                    "rows": len(rows), "period": span, "api_url": url, "table_page": page,
                    "updated": js.get("updated", "")})

with open(OUT / "cso_tables_index.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["matrix", "label", "description", "rows", "period",
                                       "updated", "table_page", "api_url"])
    w.writeheader()
    w.writerows(summary)
print(f"\nwrote cso_tables_index.csv ({len(summary)} tables)")

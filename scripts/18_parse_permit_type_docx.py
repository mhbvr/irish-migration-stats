"""Stage 1 parsing: permit-type tables inside .docx attachments to PQs.

Some supporting documents are Word files rather than spreadsheets. The one that
matters here gives employment permits issued broken down by permit type AND by
SOC occupation code - the finest public breakdown of the Critical Skills and
General permit streams.

Layout:  [blank] [blank] [blank] <year>
         Permit Type | Soc Code | Soc Title | Issued
with the permit type written only on the first row of each block.
"""
import csv, glob, json, pathlib, re
import docx

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "pq_attachments"
OUT = ROOT / "data" / "processed"

man = {}
for line in (ROOT / "data" / "raw" / "manifest.jsonl").read_text().splitlines():
    e = json.loads(line)
    if e.get("status") == "ok" and e["file"].startswith("pq_attachments/"):
        man[e["file"].split("/", 1)[1]] = e


def num(s):
    s = (s or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


rows = []
for path in sorted(glob.glob(str(RAW / "*.docx*"))):
    name = pathlib.Path(path).name
    try:
        doc = docx.Document(path)
    except Exception:                                       # noqa: BLE001
        continue
    meta = man.get(name, {}) or man.get(name.strip(), {})
    for tbl in doc.tables:
        grid = [[c.text.strip() for c in r.cells] for r in tbl.rows]
        if len(grid) < 3:
            continue
        hdr_i = next((i for i, r in enumerate(grid[:4])
                      if r and r[0].lower().startswith("permit type")), None)
        if hdr_i is None:
            continue
        hdr = [h.lower() for h in grid[hdr_i]]
        # the year sits in the row above the header, in the value column
        year = None
        if hdr_i > 0:
            for cell in grid[hdr_i - 1]:
                if re.fullmatch(r"20\d\d", cell.strip()):
                    year = int(cell.strip())
        ci = {k: next((j for j, h in enumerate(hdr) if h.startswith(k)), None)
              for k in ("permit type", "soc code", "soc title", "issued")}
        cur = ""
        for r in grid[hdr_i + 1:]:
            ptype = r[ci["permit type"]].strip() if ci["permit type"] is not None else ""
            ptype = ptype or cur
            cur = ptype
            if ptype.lower().startswith("grand total"):
                continue
            v = num(r[ci["issued"]]) if ci["issued"] is not None else None
            if v is None:
                continue
            rows.append({
                "year": year, "permit_type": ptype,
                "soc_code": r[ci["soc code"]].strip() if ci["soc code"] is not None else "",
                "soc_title": r[ci["soc title"]].strip() if ci["soc title"] is not None else "",
                "issued": v,
                "source_file": f"data/raw/pq_attachments/{name}",
                "source_url": meta.get("url", ""), "pq_url": meta.get("source_page", ""),
            })

if rows:
    with open(OUT / "employment_permits_by_type_occupation.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote employment_permits_by_type_occupation.csv ({len(rows):,} rows)")
    import collections
    for (y, t), n in sorted(collections.Counter((r["year"], r["permit_type"]) for r in rows).items()):
        tot = sum(r["issued"] for r in rows if r["year"] == y and r["permit_type"] == t)
        print(f"  {y}  {t[:44]:46} {n:4} occupations, {tot:,} permits")
else:
    print("no permit-type docx tables found")

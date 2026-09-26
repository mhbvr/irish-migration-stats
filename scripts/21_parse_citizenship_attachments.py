"""Stage 1 parsing: certificates of naturalisation by nationality and by category.

Source: spreadsheet and Word file attached to PQs 482/483 of 22 January 2026
  https://www.oireachtas.ie/en/debates/question/2026-01-22/483/
The spreadsheet holds one sheet per year (2016-2025), each listing nationality
and the number of certificates issued. The Word file holds the annual totals and
a breakdown by route (Standard Adult, s.15 residency, Granted International
Protection, Minors, Other).

This is the only public nationality-level breakdown of Irish naturalisation.
"""
import csv, glob, json, pathlib, re
import openpyxl

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "pq_attachments"
OUT = ROOT / "data" / "processed"

man = {}
for line in (ROOT / "data" / "raw" / "manifest.jsonl").read_text().splitlines():
    e = json.loads(line)
    if e.get("status") == "ok" and e["file"].startswith("pq_attachments/"):
        man[e["file"].split("/", 1)[1]] = e


def num(v):
    s = str(v or "").strip().replace(",", "")
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


rows = []
for path in sorted(glob.glob(str(RAW / "*2026-01-22*.xlsx"))):
    name = pathlib.Path(path).name
    meta = man.get(name, {})
    wb = openpyxl.load_workbook(path, data_only=True)
    for sheet in wb.sheetnames:
        y = sheet.strip()
        if not re.fullmatch(r"20\d\d", y):
            continue                       # skips the single-nationality "Indian" sheet
        ws = wb[sheet]
        for r in ws.iter_rows(min_row=2, values_only=True):
            nat = str(r[0] or "").strip()
            v = num(r[1]) if len(r) > 1 else None
            if not nat or v is None or nat.lower() in ("nationality", "total", "grand total"):
                continue
            rows.append({"year": int(y), "nationality": nat, "certificates_issued": v,
                         "source_file": f"data/raw/pq_attachments/{name}",
                         "source_url": meta.get("url", ""),
                         "pq_url": meta.get("source_page", "")})
    wb.close()

if not rows:
    print("no citizenship-by-nationality data found")
    raise SystemExit

with open(OUT / "naturalisation_by_nationality.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote naturalisation_by_nationality.csv ({len(rows):,} rows)")

# --- route/category breakdown from the companion Word file --------------------
import docx
cat_rows = []
for path in sorted(glob.glob(str(RAW / "*2026-01-22*.docx"))):
    name = pathlib.Path(path).name
    meta = man.get(name, {})
    for tbl in docx.Document(path).tables:
        grid = [[c.text.strip() for c in r.cells] for r in tbl.rows]
        if not grid or grid[0][0].lower() != "year":
            continue
        hdr = [h.rstrip("*").strip() for h in grid[0]]
        if not any("standard adult" in h.lower() for h in hdr):
            continue
        for r in grid[1:]:
            if not re.fullmatch(r"20\d\d", r[0].strip()):
                continue
            for j, h in enumerate(hdr[1:], start=1):
                raw = r[j].strip() if j < len(r) else ""
                if not raw or h.lower() == "total":
                    continue
                # "<10" is disclosure control, not a value
                suppressed = raw.startswith("<")
                cat_rows.append({
                    "year": int(r[0]), "route": h,
                    "certificates_issued": "" if suppressed else (num(raw) if num(raw) is not None else ""),
                    "suppressed": suppressed,
                    "source_file": f"data/raw/pq_attachments/{name}",
                    "source_url": meta.get("url", ""), "pq_url": meta.get("source_page", "")})

if cat_rows:
    with open(OUT / "naturalisation_by_route.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cat_rows[0].keys()))
        w.writeheader()
        w.writerows(cat_rows)
    print(f"wrote naturalisation_by_route.csv ({len(cat_rows)} rows)")

import collections
tot = collections.defaultdict(int)
for r in rows:
    tot[r["year"]] += r["certificates_issued"]

# Cross-check the per-nationality sums against the curated certificates series.
cur = {}
for r in csv.DictReader(open(OUT / "pq_curated_series.csv")):
    if r["series"] == "Certificates of naturalisation issued" and r["is_partial_year"] != "True":
        cur[int(r["year"])] = int(r["value"])
print(f"\n{'year':6}{'sum by nationality':>20}{'curated series':>16}{'diff':>8}  top nationality")
for y in sorted(tot):
    top = max((r for r in rows if r["year"] == y), key=lambda r: r["certificates_issued"])
    c = cur.get(y)
    d = f"{tot[y]-c:+,}" if c else "n/a"
    print(f"{y:<6}{tot[y]:20,}{(c if c else 0):16,}{d:>8}  {top['nationality']} ({top['certificates_issued']:,})")

if cat_rows:
    print("\ncertificates by route:")
    routes = list(dict.fromkeys(r["route"] for r in cat_rows))
    print(f"  {'year':6}" + "".join(f"{r[:15]:>17}" for r in routes))
    for y in sorted({r["year"] for r in cat_rows}):
        line = f"  {y:<6}"
        for rt in routes:
            v = next((r["certificates_issued"] for r in cat_rows if r["year"] == y and r["route"] == rt), "")
            line += f"{(f'{v:,}' if isinstance(v, int) else '<10'):>17}"
        print(line)

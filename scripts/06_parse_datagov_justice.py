"""Stage 1 parsing: Department of Justice immigration CSVs -> tidy long format.

Two wide shapes are published:
  year x nationality : Type, Status, [Last Updated,] Nationality, 2017..2026
  year x month       : Type, Status, [Last Updated,] year, Jan..Dec
Both are melted to one row per (stream, type, status, nationality|month, year).
Files are cp1252-encoded (e.g. "Aland Islands"), not UTF-8.

Disclosure control: the by-nationality files mask small counts with "*". These
are kept as rows with value="" and suppressed=True rather than dropped, so the
shortfall against the by-month files stays visible instead of silently
under-counting. Annual totals are therefore taken from the by-month files.
"""
import csv, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "datagov_justice"
OUT = ROOT / "data" / "processed"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

index = json.loads((OUT / "datagov_justice_index.json").read_text())
srcmap = {e["file"]: e for e in index}


def stream_of(fname):
    e = srcmap.get(fname, {})
    return e.get("title", fname)


SUPPRESSED = {"*", "**", "<5"}


def num(s):
    """Returns (value, suppressed_flag). value is None when absent or masked."""
    s = (s or "").strip().replace(",", "")
    if s in SUPPRESSED:
        return None, True
    if s in ("", "-", "n/a", "N/A", ".."):
        return None, False
    try:
        return int(float(s)), False
    except ValueError:
        return None, False


nat_rows, month_rows = [], []
for path in sorted(RAW.glob("*.csv")):
    with open(path, encoding="cp1252") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        continue
    cols = list(rows[0].keys())
    src = srcmap.get(path.name, {})
    meta = {"source_file": f"data/raw/datagov_justice/{path.name}",
            "source_url": src.get("resource_url", ""),
            "portal_page": src.get("portal_page", ""),
            "dataset_title": src.get("title", "")}

    if "Nationality" in cols:
        years = [c for c in cols if re.fullmatch(r"20\d\d", c)]
        for r in rows:
            for y in years:
                v, masked = num(r[y])
                if v is None and not masked:
                    continue
                nat_rows.append({"dataset": meta["dataset_title"], "type": r["Type"].replace("\t", " ").strip(),
                                 "status": r["Status"].strip(), "nationality": r["Nationality"].strip(),
                                 "year": int(y), "value": "" if v is None else v,
                                 "suppressed": masked,
                                 "last_updated": r.get("Last Updated", ""), **meta})
    elif "year" in cols:
        for r in rows:
            for m in MONTHS:
                v, masked = num(r.get(m))
                if v is None:
                    continue
                month_rows.append({"dataset": meta["dataset_title"], "type": r["Type"].replace("\t", " ").strip(),
                                   "status": r["Status"].strip(), "year": int(r["year"]),
                                   "month": MONTHS.index(m) + 1, "value": v, "suppressed": masked,
                                   "last_updated": r.get("Last Updated", ""), **meta})

for name, rows in (("justice_by_nationality_year.csv", nat_rows),
                   ("justice_by_year_month.csv", month_rows)):
    cols = list(rows[0].keys())
    with open(OUT / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {name}  ({len(rows):,} rows)")

# Headline annual totals per stream/status, from the year x month files
# (monthly files are the authoritative shape for whole-year totals).
agg = {}
for r in month_rows:
    agg.setdefault((r["dataset"], r["type"], r["status"], r["year"]), 0)
    agg[(r["dataset"], r["type"], r["status"], r["year"])] += r["value"]
with open(OUT / "justice_annual_totals.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["dataset", "type", "status", "year", "value", "note"])
    for k in sorted(agg):
        w.writerow([*k, agg[k], "summed from published monthly figures"])
print(f"wrote justice_annual_totals.csv  ({len(agg):,} rows)")

nsup = sum(1 for r in nat_rows if r["suppressed"])
print(f"\nsuppressed ('*') cells in by-nationality files: {nsup:,} of {len(nat_rows):,}")

print("\nVisa applications received (sum of monthly, all visa types):")
for y in range(2017, 2027):
    tot = sum(v for (d, t, s, yy), v in agg.items()
              if s == "Received" and "visa" in t and yy == y)
    print(f"  {y}: {tot:,}")

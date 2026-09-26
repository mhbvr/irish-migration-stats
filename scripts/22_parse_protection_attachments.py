"""Stage 1 parsing: international-protection and enforcement tables from PQ attachments.

Several Word attachments hold wide tables with years across the columns and a
metric per row, e.g.

    All First instance decisions | 2020 | 2021 | ... | 2026
    Granted (RS, SP, PTR)        |  725 | 1,521| ... | 1,428
    Percentage                   | 32.17% | 61.78% | ...

This parser finds any table whose header carries three or more years, then melts
it to one row per (table, metric, year). Values that combine a count and a
percentage in one cell ("1,521\\n61.77%") are split into both fields.
Every row keeps the attachment and the PQ URL.
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

# Attachments covering protection decisions, appeals and removals.
WANTED = ["*2026-07-14*", "*2026-02-11*", "*2026-05-06*616*"]
YEAR = re.compile(r"\*?(20[12]\d)\*?")


def parse_cell(txt):
    """-> (count, percent, raw). Cells may hold one, the other, or both."""
    raw = re.sub(r"\s+", " ", txt or "").strip()
    if not raw or raw.upper() in ("N/A", "NA", "-"):
        return None, None, raw
    pct = None
    m = re.search(r"(\d+(?:\.\d+)?)\s*%", raw)
    if m:
        pct = float(m.group(1))
    cnt = None
    m = re.search(r"(?<![\d.])(\d[\d,]*)(?!\s*%)(?![\d.])", raw.replace("%", " %"))
    if m:
        try:
            cnt = int(m.group(1).replace(",", ""))
        except ValueError:
            cnt = None
    if pct is not None and cnt is None and re.fullmatch(r"[\d.]+\s*%", raw):
        cnt = None
    return cnt, pct, raw


rows = []
for pat in WANTED:
    for path in sorted(glob.glob(str(RAW / pat))):
        if not path.strip().endswith(".docx"):
            continue
        name = pathlib.Path(path).name
        meta = man.get(name, {})
        try:
            doc = docx.Document(path)
        except Exception:                                     # noqa: BLE001
            continue
        for ti, tbl in enumerate(doc.tables):
            grid = [[c.text.strip() for c in r.cells] for r in tbl.rows]
            if len(grid) < 2:
                continue
            hdr_i = None
            for i, r in enumerate(grid[:3]):
                yrs = [c for c in r if YEAR.fullmatch(c.strip())]
                if len(set(yrs)) >= 3:
                    hdr_i = i
                    break
            if hdr_i is None:
                continue
            hdr = grid[hdr_i]
            year_cols = [(j, int(YEAR.fullmatch(c.strip()).group(1)))
                         for j, c in enumerate(hdr) if YEAR.fullmatch(c.strip())]
            # de-duplicate merged header cells that repeat the same year
            seen_y, cols = set(), []
            for j, y in year_cols:
                if y not in seen_y:
                    seen_y.add(y)
                    cols.append((j, y))
            label = re.sub(r"\s+", " ", hdr[0]).strip() or f"table {ti}"
            for r in grid[hdr_i + 1:]:
                metric = re.sub(r"\s+", " ", r[0]).strip()
                if not metric or YEAR.fullmatch(metric):
                    continue
                for j, y in cols:
                    if j >= len(r):
                        continue
                    cnt, pct, raw = parse_cell(r[j])
                    if cnt is None and pct is None:
                        continue
                    rows.append({
                        "table_label": label, "metric": metric, "year": y,
                        "count": "" if cnt is None else cnt,
                        "percent": "" if pct is None else pct,
                        "raw_cell": raw,
                        "source_file": f"data/raw/pq_attachments/{name}",
                        "source_url": meta.get("url", ""),
                        "pq_url": meta.get("source_page", ""),
                    })

if not rows:
    print("no protection/enforcement tables found")
    raise SystemExit

with open(OUT / "protection_and_enforcement_from_pq_attachments.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote protection_and_enforcement_from_pq_attachments.csv ({len(rows):,} rows)")

import collections
print("\ntables captured:")
for (lbl, src), n in collections.Counter((r["table_label"][:52], r["source_file"].rsplit("/", 1)[-1][:34])
                                         for r in rows).most_common():
    print(f"  {n:4}  {lbl:54} {src}")

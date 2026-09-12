"""Stage 1: permit-type tables printed inline in parliamentary answers.

Complements script 16 (which reads the attached spreadsheets). Where a Minister
prints the type breakdown directly in the answer, it arrives as

    <year header>  2023 2024 2025 2026
    Critical Skills Employment Permit  17,496 17,548 12622 6047
    General Employment Permit          18,056 25,785 23371 14864

We find a year header, then read the permit-type rows that follow it, requiring
the count of numbers per row to match the count of years. Each value keeps the
PQ URL it came from.
"""
import csv, glob, json, pathlib, re, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "processed"

TYPES = [
    "Contract for Services Employment Permit",
    "Critical Skills Employment Permit",
    "Dependant/Partner/Spouse Employment Permit",
    "Dependent/Partner/Spouse Employment Permit",
    "Exchange Agreement Employment Permit",
    "General Employment Permit",
    "Internship Employment Permit",
    "Intra-Company Transfer (Training) Employment Permit",
    "Intra-Company Transfer Employment Permit",
    "Reactivation Employment Permit",
    "Sport and Cultural Employment Permit",
    "Sports and Cultural Employment Permit",
    "Seasonal Employment Permit",
]
# longest first so "Intra-Company Transfer (Training)" wins over "Intra-Company Transfer"
TYPE_RE = re.compile("(" + "|".join(re.escape(t) for t in sorted(TYPES, key=len, reverse=True)) + ")", re.I)
YEARS_RE = re.compile(r"((?:20[12]\d[ ,]+){1,9}20[12]\d)")
NUM = r"[\d][\d,]{0,9}"


def canon(t):
    t = re.sub(r"\s+", " ", t).strip()
    t = t.replace("Dependent/", "Dependant/").replace("Sports and", "Sport and")
    return t.title().replace("Intra-Company Transfer (Training) Employment Permit",
                             "Intra-Company Transfer (Training) Employment Permit")


pqs = []
for f in sorted(glob.glob(str(ROOT / "data/raw/oireachtas/pqs_*.json"))):
    pqs.extend(json.load(open(f)))

rows = []
for q in pqs:
    ans = re.sub(r"\s+", " ", q.get("answer") or "")
    if not ans or not TYPE_RE.search(ans):
        continue
    for ym in YEARS_RE.finditer(ans):
        years = [int(y) for y in re.findall(r"20[12]\d", ym.group(1))]
        if not 2 <= len(years) <= 9 or len(set(years)) != len(years):
            continue
        # caption: text just before the year header identifies what is counted
        caption = ans[max(0, ym.start() - 200):ym.start()].strip()[-180:]
        pos = ym.end()
        block = ans[pos:pos + 2500]
        row_re = re.compile(TYPE_RE.pattern + r"\s+((?:" + NUM + r"\s+){" + str(len(years) - 1) + r"}" + NUM + r")(?!\d)", re.I)
        found = 0
        for rm in row_re.finditer(block):
            ptype = canon(rm.group(1))
            vals = [int(v.replace(",", "")) for v in re.findall(NUM, rm.group(2))]
            if len(vals) != len(years):
                continue
            found += 1
            for y, v in zip(years, vals):
                rows.append({"permit_type": ptype, "year": y, "value": v,
                             "caption_before_table": caption, "topic": q["topic"],
                             "pq_date": q["date"], "pq_number": q["question_number"],
                             "pq_url": q["url"],
                             "extraction": "machine-extracted from PQ answer text; verify at pq_url"})
        if found >= 3:
            break        # a real type table; don't also match later year headers

with open(OUT / "employment_permits_by_type_from_pq_text.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote employment_permits_by_type_from_pq_text.csv ({len(rows):,} rows)")

tables = {(r["pq_date"], r["pq_number"]) for r in rows}
print(f"from {len(tables)} distinct parliamentary answers")
print("\nyears covered:", sorted({r["year"] for r in rows}))
print("\npermit types found:")
for t, n in collections.Counter(r["permit_type"] for r in rows).most_common():
    print(f"  {n:5}  {t}")

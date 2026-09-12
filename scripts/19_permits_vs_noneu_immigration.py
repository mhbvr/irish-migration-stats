"""Analysis: employment permits against non-EU immigration.

Comparing these two directly is misleading, so this makes three adjustments and
reports the effect of each.

1. TIMING. The CSO estimate is a year to April; permits are calendar-year. A
   CSO "2024" figure covers May 2023 - April 2024, i.e. 8 months of calendar
   2023 and 4 of 2024. We therefore also show a blended permit figure,
   (8/12)*permits(Y-1) + (4/12)*permits(Y), aligned to the CSO window.

2. UKRAINE. Beneficiaries of temporary protection are inside the CSO's non-EU
   immigration estimate but need no employment permit. We subtract grants of
   temporary protection made in each year-to-April window (CSO UA37).

3. RENEWALS. "Permits issued" includes renewals to people already resident, who
   are not new arrivals. DETE published the new/renewal split only to 2019,
   when renewals were 14-18% of permits; after that it cannot be separated, so
   the permit count overstates arrivals by an unknown but material margin.

Outputs data/processed/permits_vs_noneu_immigration.csv.
"""
import csv, collections, datetime, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"


def read(f):
    return list(csv.DictReader(open(P / f, encoding="utf-8")))


# --- CSO non-EU immigration (thousands, year to April) -----------------------
imm = collections.defaultdict(dict)
for r in read("cso_PEA24.csv"):
    if r["Sex"] == "Both sexes":
        imm[r["Citizenship"]][int(r["Year"])] = float(r["value"])
NONEU = next(k for k in imm if k.startswith("All countries excluding"))
noneu = {y: v * 1000 for y, v in imm[NONEU].items()}

# --- permits ----------------------------------------------------------------
tot = {int(r["year"]): int(r["issued"]) for r in read("employment_permits_annual_totals.csv") if r["issued"]}
newren = {int(r["year"]): (int(r["new"]), int(r["renewal"]))
          for r in read("employment_permits_annual_totals.csv") if r["new"] and r["renewal"]}
ty = collections.defaultdict(dict)
for r in read("employment_permits_by_type_annual.csv"):
    if r["preferred_for_year"] == "True":
        ty[int(r["year"])][r["permit_type"]] = int(r["issued"])
cg = {y: d.get("Critical Skills Employment Permit", 0) + d.get("General Employment Permit", 0)
      for y, d in ty.items()}

# --- Ukraine temporary protection granted per year-to-April ------------------
ua = []
with open(ROOT / "data/raw/datagov_justice/en", encoding="utf-8-sig") as fh:
    for r in csv.DictReader(fh):
        if r["STATISTIC"] != "UA37C01":          # cumulative "to date"
            continue
        d = datetime.datetime.strptime(r["Day"].strip(), "%Y %B %d").date()
        ua.append((d, int(r["VALUE"])))
ua.sort()


def cum_at(target):
    """Cumulative grants at the last observation on or before `target`."""
    v = 0
    for d, n in ua:
        if d <= target:
            v = n
        else:
            break
    return v


ua_year = {}
for y in range(2022, 2027):
    ua_year[y] = cum_at(datetime.date(y, 4, 30)) - cum_at(datetime.date(y - 1, 4, 30))

PARTIAL = {2026}          # 2026 permit file covers Jan-Aug only
rows = []
for y in sorted(noneu):
    if y < 2015:
        continue
    ni = noneu[y]
    ni_adj = ni - ua_year.get(y, 0)
    blended = (None if (y - 1) not in tot or y not in tot or y in PARTIAL
               else round(tot[y - 1] * 8 / 12 + tot[y] * 4 / 12))
    rows.append({
        "year_to_april": y,
        "noneu_immigration": round(ni),
        "ukraine_temp_protection_granted": ua_year.get(y, 0),
        "noneu_immigration_ex_ukraine": round(ni_adj),
        "permits_issued_calendar_year": tot.get(y, ""),
        "permits_blended_to_cso_window": blended if blended else "",
        "csep_plus_general": cg.get(y, ""),
        "permits_pct_of_noneu_ex_ukraine": round(100 * tot[y] / ni_adj, 1) if y in tot and ni_adj > 0 else "",
        "blended_pct_of_noneu_ex_ukraine": round(100 * blended / ni_adj, 1) if blended and ni_adj > 0 else "",
        "csep_gep_pct_of_noneu_ex_ukraine": round(100 * cg[y] / ni_adj, 1) if y in cg and ni_adj > 0 else "",
        "permits_are_partial_year": y in PARTIAL,
    })

with open(P / "permits_vs_noneu_immigration.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"wrote permits_vs_noneu_immigration.csv ({len(rows)} rows)\n")

print(f"{'YE Apr':7}{'non-EU':>9}{'Ukr TP':>9}{'ex-Ukr':>9}{'permits':>9}{'blended':>9}{'CSEP+GEP':>10}{'bl/ex-U':>9}")
for r in rows:
    b = r["permits_blended_to_cso_window"]
    print(f"{r['year_to_april']:<7}{r['noneu_immigration']:9,}{r['ukraine_temp_protection_granted']:9,}"
          f"{r['noneu_immigration_ex_ukraine']:9,}{r['permits_issued_calendar_year'] or 0:9,}"
          f"{b or 0:9,}{r['csep_plus_general'] or 0:10,}"
          f"{str(r['blended_pct_of_noneu_ex_ukraine'] or '-'):>8}%")

print("\nrenewal share of permits issued (published only to 2019):")
for y in sorted(newren):
    n, rn = newren[y]
    print(f"  {y}: new {n:,}  renewal {rn:,}  ({100*rn/(n+rn):.1f}% renewals)")

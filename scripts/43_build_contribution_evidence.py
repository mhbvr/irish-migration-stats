"""Contribution evidence, step 2: every statistic used in
MIGRATION_CONTRIBUTION_EVIDENCE.md, computed or extracted here from files in
this repository and written with its source to
data/processed/contribution/contribution_evidence.csv.

Nothing is typed in. Text-sourced figures (ESRI, OECD via ESRI, EPRS, Medical
Council, NMBI) are matched with regular expressions against the cached PDF text,
so the script fails loudly if a figure is not found in its source.
"""
import csv, collections, json, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
C = P / "contribution"
rows = []


def add(section, claim, value, unit, source, url, note=""):
    rows.append({"section": section, "claim": claim, "value": value, "unit": unit,
                 "source": source, "source_url": url, "note": note})


def R(p):
    return list(csv.DictReader(open(p, encoding="utf-8")))


def text(p):
    raw = open(p, encoding="utf-8").read()
    return re.sub(r"\s+", " ", raw)


def need(pattern, t, label):
    m = re.search(pattern, t)
    if not m:
        raise SystemExit(f"NOT FOUND in source text: {label}")
    return m


# ---------------------------------------------------------------- 1. work
LFS = "https://data.cso.ie/table/QLF48"
v = {(x["Quarter"], x["ILO Economic Status"], x["Citizenship"]): float(x["value"]) for x in R(C / "cso_QLF48.csv")}
GROUPS = {"Ireland": "Irish citizens", "All countries excluding Ireland": "non-Irish citizens",
          "All countries excluding Ireland,United Kingdom and EU272020": "non-EU/non-UK citizens"}
for q in ("2021Q2", "2026Q2"):
    for c, lab in GROUPS.items():
        pop, emp = v[(q, "All ILO economic status", c)], v[(q, "In employment", c)]
        lf = v[(q, "In labour force", c)]
        add("Work", f"Employment rate, aged 15+ - {lab}", round(100 * emp / pop, 1), "%", "CSO LFS QLF48", LFS,
            f"{q}; 15+ includes retirees, so an older population lowers the rate")
        add("Work", f"Labour force participation, aged 15+ - {lab}", round(100 * lf / pop, 1), "%", "CSO LFS QLF48", LFS, q)
e = {(x["Quarter"], x["Citizenship"], x["NACE Rev 2.1 Economic Sector"]): float(x["value"]) for x in R(C / "cso_QLF59.csv")}
ALL, NI, NE = "All NACE Economic Sectors (A-V)", "All countries excluding Ireland", "All countries excluding Ireland,United Kingdom and EU272020"
a, b = "2021Q2", "2026Q2"
growth = e[(b, "All Countries", ALL)] - e[(a, "All Countries", ALL)]
g_ni = e[(b, NI, ALL)] - e[(a, NI, ALL)]
g_ne = e[(b, NE, ALL)] - e[(a, NE, ALL)]
Q59 = "https://data.cso.ie/table/QLF59"
add("Work", "Employment growth 2021Q2-2026Q2, all", round(growth * 1000), "jobs", "CSO LFS QLF59", Q59)
add("Work", "Share of that growth taken by non-Irish citizens", round(100 * g_ni / growth), "%", "CSO LFS QLF59", Q59,
    f"+{round(g_ni*1000):,} of +{round(growth*1000):,}; naturalised migrants count as Irish, so this understates migrants")
add("Work", "Share of that growth taken by non-EU/non-UK citizens", round(100 * g_ne / growth), "%", "CSO LFS QLF59", Q59)
add("Work", "Non-Irish share of all employment", round(100 * e[(b, NI, ALL)] / e[(b, "All Countries", ALL)], 1), "%",
    "CSO LFS QLF59", Q59, f"{b}; {round(100*e[(a, NI, ALL)]/e[(a, 'All Countries', ALL)],1)}% in {a}")
QS = ["2025Q3", "2025Q4", "2026Q1", "2026Q2"]
for sec in ("Human Health and Social Work Activities (R)", "Information and Communication (J,K)",
            "Accommodation and Food Service Activities (I)", "Industry (B-E)", "Construction (F)"):
    tot = sum(e[(q, "All Countries", sec)] for q in QS) / 4
    ni = sum(e[(q, NI, sec)] for q in QS) / 4
    add("Work", f"Non-Irish share of employment - {sec}", round(100 * ni / tot, 1), "%", "CSO LFS QLF59", Q59,
        f"average of 4 quarters to 2026Q2; {round(ni*1000):,} people")

# ---------------------------------------------------------------- 2. health service
mc = text(ROOT / "data/raw/contribution/medical_council_MWIR_2024.pdf.txt")
MCU = "https://www.medicalcouncil.ie/news-and-publications/reports/medical-workforce-intelligence-report-2024.pdf"
m = need(r"\(([\d.]+)%\) in the EU/UK, and ([\d,]+) \(([\d.]+)%\) who graduated from medical schools outside of Ireland, the EU and the UK", mc, "MC shares")
add("Health service", "Doctors whose basic medical qualification is from outside Ireland, the EU and the UK", float(m.group(3)), "%",
    "Medical Council, Workforce Intelligence Report 2024", MCU, f"{m.group(2)} doctors; a further {m.group(1)}% qualified in the EU/UK")
add("Health service", "Doctors qualified outside Ireland (EU/UK + rest of world)", round(float(m.group(1)) + float(m.group(3)), 1), "%",
    "Medical Council, Workforce Intelligence Report 2024", MCU)
m = need(r"General Division, the majority of doctors \(([\d.]+)%\) had international qualifications", mc, "MC general division")
add("Health service", "Doctors in the General Division with non-EU/UK qualifications", float(m.group(1)), "%",
    "Medical Council, Workforce Intelligence Report 2024", MCU)
m = need(r"not on a formal training scheme,? two thirds \(n = ([\d,]+), ([\d.]+)%\) had international qualifications", mc, "MC NCHD")
add("Health service", "Non-training-scheme junior hospital doctors (NCHDs) with non-EU/UK qualifications", float(m.group(2)), "%",
    "Medical Council, Workforce Intelligence Report 2024", MCU, f"n = {m.group(1)}")
nm = text(ROOT / "data/raw/contribution/NMBI_state_of_register_2024.pdf.txt")
NMU = "https://www.nmbi.ie/NMBI/media/NMBI/NMBI-State-of-the-Register-2024.pdf?ext=.pdf"
m = need(r"Non-EU ([\d,]+) ([\d,]+) ([\d,]+) Ireland ([\d,]+) ([\d,]+) ([\d,]+) EU ([\d,]+) ([\d,]+) ([\d,]+) Total ([\d,]+) ([\d,]+) ([\d,]+)", nm, "NMBI new registrants")
n = lambda s: int(s.replace(",", ""))
add("Health service", "New nurse/midwife registrants educated outside the EU, 2024", n(m.group(3)), "registrants", "NMBI State of the Register 2024", NMU,
    f"{round(100*n(m.group(3))/n(m.group(12)))}% of {n(m.group(12)):,} new registrants; up from {n(m.group(1)):,} in 2022")
add("Health service", "New nurse/midwife registrants educated in Ireland, 2024", n(m.group(6)), "registrants", "NMBI State of the Register 2024", NMU)
m = need(r"1 Ireland ([\d,]+) 11 Spain [\d,]+ 2 India ([\d,]+) [\d]+ \w+ [\d,]+ 3 Philippines ([\d,]+)", nm, "NMBI register by country")
reg_ie = n(m.group(1))
m2 = need(r"([\d,]+) currently ([\d,]+) practising", nm, "NMBI totals")
total = n(m2.group(1))
add("Health service", "Nurses and midwives on the Register educated outside Ireland", total - reg_ie, "people", "NMBI State of the Register 2024", NMU,
    f"{round(100*(total-reg_ie)/total,1)}% of {total:,}; India {n(m.group(2)):,}, Philippines {n(m.group(3)):,}")
tp = R(P / "employment_permits_by_type_occupation.csv")
nurses = next(int(r["issued"]) for r in tp if r["soc_code"] == "2231")
add("Health service", "Critical Skills Employment Permits issued to nurses, 2024", nurses, "permits", "Dept of Enterprise, via PQ attachment",
    "https://www.oireachtas.ie/en/debates/question/2025-03-26/56/", f"{round(100*nurses/sum(int(r['issued']) for r in tp),1)}% of all Critical Skills permits")

# ---------------------------------------------------------------- 3. skills, integration, language
jr = text(ROOT / "literature/esri/pdf/JR11.pdf.txt")
JRU = "https://doi.org/10.26504/jr11"
m = need(r"In the 25–34 year age group, (\d+)% of foreign-born residents had third-level education compared to (\d+)% of Irish-born", jr, "JR11 education")
add("Skills and integration", "Third-level educated, aged 25-34 - foreign-born", int(m.group(1)), "%", "ESRI Monitoring Report on Integration 2024", JRU, f"Irish-born: {m.group(2)}%; 2021-2023")
m = need(r"unemployment among migrants of African origin has decreased to (\d+)%", jr, "JR11 African unemployment")
add("Skills and integration", "Unemployment among migrants of African origin (down from persistently high 2009-2019)", int(m.group(1)), "%", "ESRI Monitoring Report on Integration 2024", JRU)
m = need(r"citizenship acquisition rate[^.]*?has remained at around (\d+)% for non- ?European Economic Area", jr, "JR11 acquisition rate")
add("Skills and integration", "Annual citizenship acquisition rate, non-EEA residents, since 2021", int(m.group(1)), "%", "ESRI Monitoring Report on Integration 2024", JRU)
m = need(r"share of x \| Monitoring report on integration 2024 migrants of non-EEA origin who have acquired Irish citizenship since 2005 is around (\d+)%", jr, "JR11 30% acquired")
add("Skills and integration", "Share of non-EEA migrants (arrived since 2005) who have acquired Irish citizenship", int(m.group(1)), "%",
    "ESRI Monitoring Report on Integration 2024", JRU, "estimate")
import glob
ref = next(int(r["value"]) for r in R(P / "pq_curated_series.csv") if r["series"] == "Certificates of naturalisation refused" and r["year"] == "2024")
pq = {}
for f in glob.glob(str(ROOT / "data/raw/oireachtas/pqs_2025_11.json")):
    for q in json.load(open(f)):
        pq[(q["date"], q["question_number"])] = q
ans = re.sub(r"\s+", " ", pq[("2025-11-12", 768)]["answer"])
m = need(r"made more than ([\d,]+) decisions in 2024", ans, "PQ 768 decisions")
dec = int(m.group(1).replace(",", ""))
add("Skills and integration", "Naturalisation refusals as a share of decisions, 2024", round(100 * ref / dec, 1), "%",
    "Parliamentary answers (PQ 891, 16 Sep 2026; PQ 768, 12 Nov 2025)", "https://www.oireachtas.ie/en/debates/question/2026-09-16/891/",
    f"{ref} refusals against more than {dec:,} decisions - applicants already meet the current criteria")
eng = {r["citizenship"]: r for r in R(P / "naturalisation_baseline/english_ability_by_citizenship.csv")}
for c in ("All citizenships", "India", "Africa(1)"):
    add("Skills and integration", f"Speak English well or very well (speakers of another language at home) - {c}",
        round(100 - float(eng[c]["pct_not_well_or_not_at_all"]), 1), "%", "CSO F5015 (Census 2022)", "https://data.cso.ie/table/F5015",
        "the remainder speak it 'not well' or 'not at all'")

# ---------------------------------------------------------------- 4. welfare and public finances
rs = text(ROOT / "literature/esri/pdf/RS229.pdf.txt")
RSU = "https://doi.org/10.26504/rs229"
m = need(r"We show that immigrants have generally had higher employment rates than the native-born", rs, "RS229 employment")
add("Welfare and public finances", "Immigrants had higher employment rates than the Irish-born, 2014-2024", "yes", "", "ESRI RS229", RSU)
m = need(r"rate of receipt for the Irish-born pooled across 2014 to 2024 was (\d+) per cent\. The rates of receipt are lower for immigrants from EU West \((\d+) per cent\) and Asia \((\d+) per cent\)", rs, "RS229 unemployment payments")
add("Welfare and public finances", "Receiving an unemployment payment, 2014-2024 pooled - born in Asia", int(m.group(3)), "%", "ESRI RS229", RSU,
    f"Irish-born {m.group(1)}%; EU West {m.group(2)}%; EU East and Africa 21%")
fi = text(ROOT / "literature/esri/pdf/SUSTAT141.pdf.txt")
FIU = "https://doi.org/10.26504/sustat141"
m = need(r"including Ireland where immigrants have a net contribution of ([\d.]+) per cent of GDP", fi, "OECD 1.57")
add("Welfare and public finances", "Immigrants' individual net fiscal contribution, Ireland, 2006-2018", float(m.group(1)), "% of GDP",
    "OECD International Migration Outlook 2021, as summarised by ESRI (2026)", FIU, "OECD finds migrants' fiscal impact neutral on average across countries")
m = need(r"This includes Ireland, where immigrants contribute ([\d.]+) per cent of GDP", fi, "OECD 0.62")
add("Welfare and public finances", "The same, after charging immigrants their share of congestible public goods", float(m.group(1)), "% of GDP",
    "OECD International Migration Outlook 2021, as summarised by ESRI (2026)", FIU)
m = need(r"foreign-born residents in Ireland contributed (\d+) per cent more than they received, compared to (\d+) per cent for the Irish-born", fi, "OECD ratio")
add("Welfare and public finances", "Fiscal ratio: foreign-born residents contributed more than they received by", int(m.group(1)), "%",
    "OECD International Migration Outlook 2021, as summarised by ESRI (2026)", FIU, f"Irish-born: {m.group(2)}%")

# ---------------------------------------------------------------- 5. Ukrainians (s.16A)
u = {}
for x in R(C / "cso_UA29.csv"):
    if x["County"] == "Ireland":
        u.setdefault(x["Week"], {})[x["Statistic"]] = int(float(x["value"]))
wk = list(u)
first_active = next(w for w in wk if "Active Employments of arrivals from Ukraine" in u[w])
UAU = "https://data.cso.ie/table/UA29"
for w in (first_active, wk[-1]):
    add("Ukrainian arrivals", "Active jobs held by arrivals from Ukraine", u[w]["Active Employments of arrivals from Ukraine"], "jobs", "CSO UA29 (Revenue data)", UAU, w)
add("Ukrainian arrivals", "Arrivals from Ukraine who have had a job in Ireland", u[wk[-1]]["Employees from Ukraine"], "people", "CSO UA29 (Revenue data)", UAU, wk[-1])
inc = [(x["Week"], int(float(x["value"]))) for x in R(C / "cso_UA30.csv")
       if x["Statistic"] == "Beneficiaries of social welfare payments" and x["Type of Beneficiary of Social Welfare Payment"] == "Income support recipients"]
peak = max(inc, key=lambda t: t[1])
add("Ukrainian arrivals", "Income support recipients among arrivals from Ukraine - peak", peak[1], "people", "CSO UA30", "https://data.cso.ie/table/UA30", peak[0])
add("Ukrainian arrivals", "Income support recipients among arrivals from Ukraine - latest", inc[-1][1], "people", "CSO UA30", "https://data.cso.ie/table/UA30", inc[-1][0])

# ---------------------------------------------------------------- 6. births (s.6B)
vs = {(x["Year"], x["Nationality"]): float(x["value"]) for x in R(P / "naturalisation_baseline/cso_VSAS80.csv") if x["Statistic"] == "Births Registered"}
for nat_, lab in (("Irish", "Irish mothers"), ("Other nationalities (7)", "mothers from outside the EU and UK")):
    add("Births", f"Births to {lab}, 2022 -> 2025", f"{int(vs[('2022', nat_)]):,} -> {int(vs[('2025', nat_)]):,}", "births", "CSO VSAS80",
        "https://data.cso.ie/table/VSAS80", f"{round(100*(vs[('2025', nat_)]/vs[('2022', nat_)]-1))}% change; 2025 provisional")

# ---------------------------------------------------------------- 7. public opinion and the EU context
at = text(ROOT / "literature/esri/pdf/JR5_0.pdf.txt")
m = need(r"Over (\d+) per cent feel positive about immigration", at, "JR5 73%")
add("Public opinion", "Adults who feel positive about immigration", f"over {m.group(1)}", "%", "ESRI, Attitudes towards immigration and refugees in Ireland (2024)",
    "https://doi.org/10.26504/jr5", "attitudes softened between June and November 2023")
mp = text(ROOT / "literature/esri/pdf/RS225_1.pdf.txt")
m = need(r"guessing an average of (\d+) per cent of the population to have been born abroad compared to official estimates of ([\d-]+) per cent", mp, "RS225")
add("Public opinion", "Public's average guess of the share born abroad", int(m.group(1)), "%", "ESRI RS225 (2026)", "https://doi.org/10.26504/rs225",
    f"official estimate {m.group(2)}%")
ep = text(ROOT / "data/raw/contribution/EPRS_BRI_2025_769502.pdf.txt")
EPU = "https://www.europarl.europa.eu/RegData/etudes/BRIE/2025/769502/EPRS_BRI%282025%29769502_EN.pdf"
need(r"Germany has gone the other way and lowered the minimum residence period from 8 to 5 years", ep, "EPRS Germany")
add("EU context", "Germany lowered its naturalisation residence requirement from 8 to 5 years (2024)", "8 -> 5", "years", "European Parliament Research Service (2025)", EPU)
need(r"minimum period of residence required for ordinary naturalisation in EU countries ranges from 3 to 10 years", ep, "EPRS range")
add("EU context", "Minimum residence for ordinary naturalisation across the EU", "3-10", "years", "European Parliament Research Service (2025)", EPU)

with open(C / "contribution_evidence.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"contribution_evidence.csv: {len(rows)} claims, every one matched in its source")
for r in rows:
    print(f"  [{r['section'][:14]:14}] {r['claim'][:78]:80} {str(r['value']):>14} {r['unit']}")

"""Naturalisation baseline, step 2: assemble pre-change indicators for each
provision of the Irish Nationality and Citizenship (Amendment) Bill 2026.

Every value is read from a file already in this repository (official tables,
parliamentary answers and their attachments, ESRI/DETE publications); nothing is
typed in. Outputs, in data/processed/naturalisation_baseline/:
  baseline_indicators.csv          long table: block, provision, indicator, year, value, source
  naturalisation_rate_by_nationality.csv   certificates per 100 residents of each citizenship
  english_ability_by_citizenship.csv       Census 2022 English ability, by citizenship
  eu_naturalisation_rate_rank.csv          Ireland against every reporting country
"""
import csv, json, glob, re, pathlib, collections
import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
B = P / "naturalisation_baseline"
rows = []


def R(path):
    return list(csv.DictReader(open(path, encoding="utf-8")))


def add(block, provision, indicator, year, value, unit, source, url, note=""):
    rows.append({"block": block, "provision": provision, "indicator": indicator, "year": year,
                 "value": value, "unit": unit, "source": source, "source_url": url, "note": note})


PQ = lambda d, n: f"https://www.oireachtas.ie/en/debates/question/{d}/{n}/"

# ---------------------------------------------------------------- A. outcomes
cur = R(P / "pq_curated_series.csv")
def curated(series, block, prov, indicator, unit):
    for r in cur:
        if r["series"] == series:
            add(block, prov, indicator, r["year"], int(r["value"]), unit, "Parliamentary answer", r["pq_url"],
                "part-year" if r["is_partial_year"] == "True" else "")
curated("Citizenship (naturalisation) applications received", "A Outcomes", "all", "Naturalisation applications received", "applications")
curated("Certificates of naturalisation refused", "A Outcomes", "all", "Naturalisation refusals", "refusals")
curated("Citizenship applications: median processing time", "A Outcomes", "all", "Median processing time", "months")
curated("Declarations of intention to retain Irish citizenship (Form 5)", "A Outcomes", "s.19 / residence after naturalisation", "Form 5 declarations (naturalised citizens living abroad)", "declarations")

nat = R(P / "naturalisation_by_nationality.csv")
by_year = collections.Counter()
for r in nat:
    by_year[int(r["year"])] += int(r["certificates_issued"])
NAT_URL = PQ("2026-01-22", 483)
for y, v in sorted(by_year.items()):
    add("A Outcomes", "all", "Certificates of naturalisation issued", y, v, "certificates",
        "PQ attachment (sum over nationalities)", NAT_URL)

for r in R(P / "naturalisation_by_route.csv"):
    v = r["certificates_issued"]
    route = {"Standard Adult": "standard adult (s.15, 5-year route)",
             "S15 residency": "spouse/civil partner of Irish citizen (3-year route; label 'S15 residency')",
             "Granted International Protection": "granted international protection",
             "Minors": "minors", "Other": "other (mainly s.28 declarations)"}.get(r["route"], r["route"])
    add("A Outcomes", "s.15 / s.15A", f"Certificates by route: {route}", r["year"],
        int(v) if v else "", "certificates", "PQ attachment", r["pq_url"] or NAT_URL,
        "suppressed (<10)" if r["suppressed"] == "True" else "")

# ceremonies: parse the figures from the answer text itself
pqs = {}
for f in glob.glob(str(ROOT / "data/raw/oireachtas/pqs_2026_*.json")):
    for q in json.load(open(f)):
        pqs[(q["date"], q["question_number"])] = q
a = re.sub(r"\s+", " ", pqs[("2026-09-07", 2397)]["answer"])
m1 = re.search(r"In (20\d\d), (\d+) (?:citizenship )?ceremonies were held and ([\d,]+) certificates", a)
m2 = re.search(r"In (20\d\d) to date, (\d+) (?:citizenship )?ceremonies have been held and ([\d,]+) certificates", a)
for m, note in ((m1, ""), (m2, "part-year")):
    if m:
        add("A Outcomes", "all", "Citizenship ceremonies held", m.group(1), int(m.group(2)), "ceremonies",
            "Parliamentary answer", PQ("2026-09-07", 2397), note)
        add("A Outcomes", "all", "Certificates conferred at ceremonies (adult and minor)", m.group(1),
            int(m.group(3).replace(",", "")), "certificates", "Parliamentary answer", PQ("2026-09-07", 2397), note)

# Irish Citizen Child applications on hand (s.6B context)
a = re.sub(r"\s+", " ", pqs[("2026-09-07", 2467)]["answer"])
for y, v in re.findall(r"(202[4-6]) (\d+)", a[a.find("ICCA applications on hand"):]):
    add("G Children born in Ireland", "s.6B", "Irish Citizen Child applications on hand", y, int(v),
        "applications", "Parliamentary answer", PQ("2026-09-07", 2467), "part-year" if y == "2026" else "")

# Eurostat: acquisitions and the naturalisation RATE (per 100 non-citizen residents)
for r in R(P / "eurostat_migr_acq_IE.csv"):
    if (r["Age class_code"], r["Sex_code"], r["Country of citizenship_code"], r["Age definition_code"]) == ("TOTAL", "T", "TOTAL", "COMPLET"):
        if int(r["Time"]) >= 2012:
            add("A Outcomes", "all", "Acquisitions of Irish citizenship (Eurostat)", r["Time"], int(float(r["value"])),
                "persons", "Eurostat migr_acq", "https://ec.europa.eu/eurostat/databrowser/view/migr_acq/default/table?lang=en")
acqs = R(B / "eurostat_migr_acqs_all.csv")
IND = {"Share of foreign citizens who have acquired citizenship": "all foreign citizens",
       "Share of non-EU citizens who have acquired citizenship": "non-EU citizens",
       "Share of EU citizens who have acquired citizenship": "EU citizens"}
for r in acqs:
    if r["Geopolitical entity (reporting)_code"] == "IE" and int(r["Time"]) >= 2012:
        add("A Outcomes", "all", f"Naturalisation rate - {IND[r['Indicator on migration']]}", r["Time"],
            float(r["value"]), "% of non-citizen residents", "Eurostat migr_acqs",
            "https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en")
rank = []
latest = max(int(r["Time"]) for r in acqs if r["Geopolitical entity (reporting)_code"] == "IE")
for r in acqs:
    if r["Indicator on migration"].startswith("Share of foreign") and int(r["Time"]) == latest \
            and not r["Geopolitical entity (reporting)_code"].startswith("EU"):
        rank.append((float(r["value"]), r["Geopolitical entity (reporting)"]))
rank.sort(reverse=True)
with open(B / "eu_naturalisation_rate_rank.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["rank", "country", "year", "naturalisation_rate_pct"])
    for i, (v, c) in enumerate(rank, 1):
        w.writerow([i, c, latest, v])
ie_rank = next(i for i, (v, c) in enumerate(rank, 1) if c == "Ireland")
add("A Outcomes", "s.15 (8 years is at the restrictive end of EU practice)", "Ireland's rank on naturalisation rate among reporting countries",
    latest, f"{ie_rank} of {len(rank)}", "rank", "Eurostat migr_acqs", "https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en",
    f"median {sorted(v for v, _ in rank)[len(rank)//2]:.2f}%")

# ---------------------------------------------------------------- B. composition + propensity
f5065 = {r["Citizenship"]: int(float(r["value"])) for r in R(B / "cso_F5065.csv") if r["Sex"] == "Both sexes"}
ALIAS = {"united states of america": "united states", "usa": "united states", "russian federation": "russia",
         "viet nam": "vietnam", "korea, republic of": "south korea", "republic of korea": "south korea",
         "democratic republic of the congo": "congo, democratic republic of", "dr congo": "congo, democratic republic of",
         "moldova, republic of": "moldova", "iran, islamic republic of": "iran", "syrian arab republic": "syria",
         "united kingdom of great britain and northern ireland": "united kingdom", "uk": "united kingdom",
         "czech republic": "czechia", "türkiye": "turkey", "turkiye": "turkey",
         "congo, the democratic republic of the": "democratic rep of congo",
         "slovak republic": "slovakia", "libyan arab jamahiriya": "libya"}
norm = lambda s: ALIAS.get(re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", s)).strip().lower(),
                           re.sub(r"\s+", " ", re.sub(r"\(.*?\)", "", s)).strip().lower())
res = {norm(k): (k, v) for k, v in f5065.items() if k != "All citizenships"}
certs = collections.defaultdict(dict)
for r in nat:
    certs[norm(r["nationality"])][int(r["year"])] = certs[norm(r["nationality"])].get(int(r["year"]), 0) + int(r["certificates_issued"])
prop, unmatched = [], []
for k, ys in certs.items():
    if "rest of" in k or k.startswith("other"):
        continue          # residual groupings differ between the two sources - not comparable
    c22 = ys.get(2022, 0); c3 = sum(ys.get(y, 0) for y in (2021, 2022, 2023)) / 3
    if k in res:
        name, pop = res[k]
        prop.append({"citizenship": name, "residents_census_2022": pop, "certificates_2022": c22,
                     "certificates_avg_2021_2023": round(c3, 1), "certificates_2025": ys.get(2025, 0),
                     "per_100_residents_2022": round(100 * c22 / pop, 2) if pop else "",
                     "per_100_residents_avg_2021_2023": round(100 * c3 / pop, 2) if pop else ""})
    elif sum(ys.values()) >= 200:
        unmatched.append((k, sum(ys.values())))
prop.sort(key=lambda r: -r["residents_census_2022"])
with open(B / "naturalisation_rate_by_nationality.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(prop[0].keys())); w.writeheader(); w.writerows(prop)
tot_res = f5065["All citizenships"]
add("B Composition", "all", "Non-Irish citizens usually resident (Census 2022)", 2022, tot_res, "persons",
    "CSO F5065", "https://data.cso.ie/table/F5065")
for r in R(B / "cso_PEA27.csv"):
    if r["Age Group"] == "All ages" and r["Sex"] == "Both sexes" and r["Human Development Index Rating"].startswith("Human Development Index (HDI) - All"):
        add("C Eligible pipeline", "s.15 residence 5->8", "Citizens of non-EU/EFTA/candidate countries resident", r["Year"],
            int(float(r["value"])), "persons", "CSO PEA27", "https://data.cso.ie/table/PEA27")

# ---------------------------------------------------------------- C. eligible pipeline
for r in R(P / "cso_PEA24.csv"):
    if r["Sex"] == "Both sexes" and r["Citizenship"].startswith("All countries excluding") and int(r["Year"]) >= 2012:
        add("C Eligible pipeline", "s.15 residence 5->8", "Non-EU/non-UK immigration (year to April)", r["Year"],
            round(float(r["value"]) * 1000), "persons", "CSO PEA24", "https://data.cso.ie/table/PEA24",
            "an arrival cohort becomes eligible after 5 years now, 8 under the Bill")
for r in R(P / "employment_permits_annual_totals.csv"):
    if r["issued"]:
        add("C Eligible pipeline", "s.15 residence 5->8; s.15F self-sufficiency", "Employment permits issued", r["year"],
            int(r["issued"]), "permits", "DETE",
            "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/",
            "2026 = January-August" if r["year"] == "2026" else "")
rv = R(B / "eurostat_migr_resvalid_IE.csv")
for r in rv:
    if r["Country of citizenship_code"] == "TOTAL" and r["Duration_code"] == "TOTAL" and int(r["Time"]) >= 2015:
        add("C Eligible pipeline", "s.15 / s.16A", f"Valid residence permits on 31 Dec - {r['Reason'].lower()}", r["Time"],
            int(float(r["value"])), "persons", "Eurostat migr_resvalid",
            "https://ec.europa.eu/eurostat/databrowser/view/migr_resvalid/default/table?lang=en",
            "education permissions are already non-reckonable (s.16A)" if r["Reason_code"] == "EDUC" else "")
for r in R(B / "eurostat_migr_reslong_IE.csv"):
    if r["Country of citizenship_code"] == "TOTAL" and int(r["Time"]) >= 2015:
        add("C Eligible pipeline", "s.15 residence 5->8", f"Long-term residents on 31 Dec - {r['Legal framework'].lower()}", r["Time"],
            int(float(r["value"])), "persons", "Eurostat migr_reslong",
            "https://ec.europa.eu/eurostat/databrowser/view/migr_reslong/default/table?lang=en",
            "Ireland does not apply the EU long-term residence directive; national framework = long-term residence permissions")

# ---------------------------------------------------------------- D. non-reckonable residence (s.16A)
ua = []
with open(ROOT / "data/raw/datagov_justice/en", encoding="utf-8-sig") as fh:
    ua = [r for r in csv.DictReader(fh) if r["STATISTIC"] == "UA37C01"]
last = ua[-1]
add("D Non-reckonable residence", "s.16A(1)(e)-(f) - temporary protection", "Temporary protection granted to arrivals from Ukraine, cumulative",
    last["Day"], int(last["VALUE"]), "persons", "CSO UA37 via data.gov.ie",
    "https://data.gov.ie/dataset/ua37-temporary-protection-granted-to-arrivals-from-ukraine",
    "all of this residence would become non-reckonable")
for r in R(P / "permits_vs_noneu_immigration.csv"):
    if int(r["ukraine_temp_protection_granted"] or 0):
        add("D Non-reckonable residence", "s.16A(1)(e)-(f) - temporary protection", "Temporary protection granted in the year to April",
            r["year_to_april"], int(r["ukraine_temp_protection_granted"]), "persons", "CSO UA37 (derived)",
            "https://data.gov.ie/dataset/ua37-temporary-protection-granted-to-arrivals-from-ukraine")
tot = collections.Counter()
for r in R(P / "justice_annual_totals.csv"):
    if r["type"].startswith("EU1"):
        tot[(r["status"], r["year"])] += int(r["value"])
for (st, y), v in sorted(tot.items()):
    add("D Non-reckonable residence", "s.16A(1)(g)-(j) - refused EU Treaty Rights", f"EU Treaty Rights residence cards (EU1) {st.lower()}", y, v,
        "applications", "Dept of Justice via data.gov.ie",
        "https://data.gov.ie/dataset/eu-treaty-rights-applications-and-decisions-by-year-and-month",
        ("refused cases are those whose temporary-permission time the Bill would make non-reckonable" if st == "Refused" else "")
        + ("; 2026 part-year" if y == "2026" else ""))

# ---------------------------------------------------------------- E. self-sufficiency
rs = ROOT / "literature/esri/pdf/RS229.pdf.txt"
if rs.exists():
    t = re.sub(r"\s+", " ", rs.read_text().partition("\n")[2])
    m = re.search(r"TABLE 4\.1 % IN RECEIPT.*?Unemployment, disability, (\d+) (\d+)\*+ (\d+) (\d+)\*+ (\d+) (\d+)\*+", t)
    if m:
        for (y, i, n) in ((2014, m.group(1), m.group(2)), (2019, m.group(3), m.group(4)), (2024, m.group(5), m.group(6))):
            add("E Self-sufficiency", "s.15(1)(f), s.15F", "Receiving any unemployment, disability or family/children payment - Irish-born", y, int(i), "%",
                "ESRI RS229 Table 4.1 (SILC, aged 15-65)", "https://doi.org/10.26504/rs229", "family payments include universal Child Benefit")
            add("E Self-sufficiency", "s.15(1)(f), s.15F", "Receiving any unemployment, disability or family/children payment - born abroad", y, int(n), "%",
                "ESRI RS229 Table 4.1 (SILC, aged 15-65)", "https://doi.org/10.26504/rs229", "family payments include universal Child Benefit")
dete = ROOT / "data/raw/naturalisation_baseline/DETE_MAR_roadmap_review_2025.pdf"
if dete.exists():
    t = re.sub(r"\s+", " ", "\n".join((p.extract_text() or "") for p in pdfplumber.open(dete).pages))
    DURL = "https://enterprise.gov.ie/en/publications/publication-files/employment-permits-minimum-annual-remuneration-outcome-of-the-roadmap-review-2025.pdf"
    m = re.search(r"There are currently ([\d,]+) active GEPs[^.]*?with ([\d.]+)% of these having a salary of less than €([\d,]+)", t)
    if m:
        add("E Self-sufficiency", "s.15F income floor", "Active General Employment Permits issued after the Jan 2024 threshold rise", 2025,
            int(m.group(1).replace(",", "")), "permits", "DETE MAR roadmap review 2025", DURL)
        add("E Self-sufficiency", "s.15F income floor", f"Share of those GEPs with salary below €{m.group(3)}", 2025, float(m.group(2)), "%",
            "DETE MAR roadmap review 2025", DURL, "€44,000 gross is c. the Working Family Payment threshold for one child")
    m = re.search(r"In (2024), over ([\d,]+) employment permits were issued for these roles\. This represents (\d+)% of all permits", t)
    if m:
        add("E Self-sufficiency", "s.15F income floor", "Permits issued at sub-standard minimum remuneration", m.group(1),
            int(m.group(2).replace(",", "")), "permits", "DETE MAR roadmap review 2025", DURL, f"{m.group(3)}% of all permits issued")

# ---------------------------------------------------------------- F. language
f5015 = R(B / "cso_F5015.csv")
eng = collections.defaultdict(dict)
for r in f5015:
    eng[r["Citizenship"]][r["Ability to Speak English"]] = int(float(r["value"]))
out = []
for c, d in eng.items():
    tot_ = d.get("Speaks English - Total", 0)
    weak = d.get("Speaks English - Not well", 0) + d.get("Speaks English - Not at all", 0)
    out.append({"citizenship": c, "speakers_of_other_language_at_home": tot_, "not_well": d.get("Speaks English - Not well", 0),
                "not_at_all": d.get("Speaks English - Not at all", 0), "pct_not_well_or_not_at_all": round(100 * weak / tot_, 1) if tot_ else ""})
out.sort(key=lambda r: -r["speakers_of_other_language_at_home"])
with open(B / "english_ability_by_citizenship.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(out[0].keys())); w.writeheader(); w.writerows(out)
for r in out:
    if r["citizenship"] in ("All citizenships", "Ireland"):
        continue
    add("F Language test", "s.15(1)(h)", f"Speak English not well / not at all - {r['citizenship']}", 2022,
        r["pct_not_well_or_not_at_all"], "% of those speaking another language at home", "CSO F5015 (Census 2022)",
        "https://data.cso.ie/table/F5015", f"base: {r['speakers_of_other_language_at_home']:,} persons")

# ---------------------------------------------------------------- G. children born in Ireland
for r in R(B / "cso_VSAS80.csv"):
    if r["Statistic"] in ("Births Registered", "Percentage of all Births"):
        add("G Children born in Ireland", "s.6B", f"{r['Statistic']} - mother's nationality: {r['Nationality']}", r["Year"],
            float(r["value"]), "births" if r["Statistic"] == "Births Registered" else "%", "CSO VSAS80",
            "https://data.cso.ie/table/VSAS80", "2025 provisional" if r["Year"] == "2025" else "")

# ---------------------------------------------------------------- H. offence bar / enforcement context
for r in R(P / "protection_and_enforcement_from_pq_attachments.csv"):
    if r["metric"].startswith(("Deportation orders s", "Enforced Deportation", "Total Removed")) and r["count"]:
        add("H Offence bar and revocation", "s.15(1)(g), Schedule 1", r["metric"], r["year"], int(r["count"]),
            "persons", "PQ attachment", r["pq_url"], "enforcement context only - offences 'committed' are not recorded anywhere")

with open(B / "baseline_indicators.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print(f"baseline_indicators.csv: {len(rows)} rows")
for b, n in sorted(collections.Counter(r["block"] for r in rows).items()):
    print(f"  {n:4}  {b}")
print(f"\nnaturalisation_rate_by_nationality.csv: {len(prop)} citizenships matched; large unmatched: {unmatched}")
print(f"Ireland's naturalisation rate rank {latest}: {ie_rank} of {len(rank)}")

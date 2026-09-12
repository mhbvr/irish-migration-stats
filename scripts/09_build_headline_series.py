"""Stage 1 output: one tidy headline table across all sources.

Every row carries the indicator, year, value, the publishing body and a URL that
a reader can open to check the number. Nothing is entered by hand: each value is
read back out of the processed CSVs produced by the earlier scripts.
"""
import csv, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
P = ROOT / "data" / "processed"
rows = []


def add(indicator, unit, year, value, source, url, note=""):
    rows.append({"indicator": indicator, "unit": unit, "year": int(year),
                 "value": value, "source": source, "source_url": url, "note": note})


def read(name):
    with open(P / name, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ---- CSO Population and Migration Estimates (April, annual) -------------------
CSO_NOTE = ("CSO Population and Migration Estimates; figures in thousands, "
            "year to April. 2022-2026 reflect Census 2022 rebasing.")
for m, ind in (("PEA24", "Immigration (CSO estimate)"), ("PEA23", "Emigration (CSO estimate)")):
    for r in read(f"cso_{m}.csv"):
        if r["Sex"] == "Both sexes" and r["Citizenship"] == "All Countries":
            add(ind, "thousands", r["Year"], float(r["value"]), "CSO",
                f"https://data.cso.ie/table/{m}", CSO_NOTE)

for r in read("cso_PEA03.csv"):
    if (r["Sex"] == "Both sexes" and r["Age Group"] == "All ages"
            and r["Inward or Outward Flow"] == "Net migration"):
        add("Net migration (CSO estimate)", "thousands", r["Year"], float(r["value"]),
            "CSO", "https://data.cso.ie/table/PEA03", CSO_NOTE)

# ---- Employment permits (DETE) ----------------------------------------------
EP_URL = "https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/"
for r in read("employment_permits_annual_totals.csv"):
    y = r["year"]
    part = "2026 is year-to-date (the published file covers Jan-Aug 2026)." if y == "2026" else ""
    for field, ind in (("issued", "Employment permits issued"),
                       ("refused", "Employment permit applications refused"),
                       ("withdrawn", "Employment permit applications withdrawn")):
        if r[field] not in ("", None):
            add(ind, "permits", y, int(r[field]), "DETE", EP_URL,
                ("Grand Total row of the Department's own spreadsheet. " + part).strip())

# ---- Visas, residence permissions, family reunification (DoJ via data.gov.ie)-
tot = {}
for r in read("justice_annual_totals.csv"):
    tot.setdefault((r["type"], r["status"], r["year"]), 0)
    tot[(r["type"], r["status"], r["year"])] += int(r["value"])
VISA_URL = "https://data.gov.ie/dataset/visa-applications-and-decisions-year-and-month"
DRP_URL = "https://data.gov.ie/dataset/domestic-residence-permissions-applications-and-decisions-year-and-month"
FRU_URL = "https://data.gov.ie/dataset/family-reunification-applications-and-decisions-by-year-and-month"
years = sorted({k[2] for k in tot})
for y in years:
    pt = ("2026 is a part-year figure (source last updated 31/07/2026)." if y == "2026" else "")
    for status, lbl in (("Received", "applications received"), ("Granted", "granted"), ("Refused", "refused")):
        v = sum(n for (t, s, yy), n in tot.items() if s == status and yy == y and "visa" in t)
        if v:
            add(f"Visa {lbl} (all visa types)", "applications", y, v, "Dept of Justice / data.gov.ie",
                VISA_URL, ("Summed from published monthly figures. " + pt).strip())
    for status, lbl in (("Received", "applications received"), ("Granted", "granted")):
        v = sum(n for (t, s, yy), n in tot.items() if s == status and yy == y and t.startswith("Domestic"))
        if v:
            add(f"Domestic residence permission {lbl}", "applications", y, v,
                "Dept of Justice / data.gov.ie", DRP_URL,
                ("Summed from published monthly figures. " + pt).strip())
    v = sum(n for (t, s, yy), n in tot.items()
            if s == "Received" and yy == y and t == "FRU - International Protection by Applicant")
    if v:
        add("Family reunification applications received (international protection, by applicant)",
            "applications", y, v, "Dept of Justice / data.gov.ie", FRU_URL,
            ("Summed from published monthly figures. " + pt).strip())

# ---- Asylum + citizenship + first permits (Eurostat, supplied by Irish ISD) ---
def euro(fname, filt, indicator, unit, url, note):
    for r in read(fname):
        if all(r.get(k) == v for k, v in filt.items()):
            add(indicator, unit, r["Time"], int(float(r["value"])), "Eurostat (data supplied by Irish ISD)",
                url, note)

EU_NOTE = ("Ireland reports this to Eurostat under EU statutory reporting; the Department of "
           "Justice's statistics page directs users to these datasets.")
euro("eurostat_migr_asyappctza_IE.csv",
     {"Age class_code": "TOTAL", "Sex_code": "T", "Country of citizenship_code": "TOTAL",
      "Applicant type_code": "TOTAL"},
     "Asylum applicants", "persons",
     "https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctza/default/table?lang=en", EU_NOTE)
euro("eurostat_migr_asyappctza_IE.csv",
     {"Age class_code": "TOTAL", "Sex_code": "T", "Country of citizenship_code": "TOTAL",
      "Applicant type_code": "FRST"},
     "Asylum applicants (first-time)", "persons",
     "https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctza/default/table?lang=en", EU_NOTE)
euro("eurostat_migr_acq_IE.csv",
     {"Age class_code": "TOTAL", "Sex_code": "T", "Country of citizenship_code": "TOTAL",
      "Age definition_code": "COMPLET"},
     "Acquisitions of Irish citizenship", "persons",
     "https://ec.europa.eu/eurostat/databrowser/view/migr_acq/default/table?lang=en", EU_NOTE)
for code, lbl in (("TOTAL", "all reasons"), ("EMP", "employment"), ("FAM", "family"), ("EDUC", "education")):
    euro("eurostat_migr_resfirst_IE.csv",
         {"Reason_code": code, "Country of citizenship_code": "TOTAL", "Duration_code": "TOTAL"},
         f"First residence permits issued ({lbl})", "permits",
         "https://ec.europa.eu/eurostat/databrowser/view/migr_resfirst/default/table?lang=en", EU_NOTE)

rows.sort(key=lambda r: (r["indicator"], r["year"]))
with open(P / "headline_series.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["indicator", "unit", "year", "value", "source", "source_url", "note"])
    w.writeheader()
    w.writerows(rows)

inds = sorted({r["indicator"] for r in rows})
print(f"wrote headline_series.csv  ({len(rows):,} rows, {len(inds)} indicators)")
for i in inds:
    ys = sorted(r["year"] for r in rows if r["indicator"] == i)
    print(f"  {i:70} {ys[0]}-{ys[-1]}")

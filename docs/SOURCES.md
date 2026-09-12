# Sources

Every source is an official publisher. Each downloaded file's exact URL,
retrieval timestamp and SHA-256 are in
[`../data/processed/sources_register.csv`](../data/processed/sources_register.csv).
Retrieved 12 September 2026.

## 1. Central Statistics Office (CSO)

Ireland's national statistical authority. Accessed through the PxStat open REST
API; each table also has a human-readable page.

- Portal: https://data.cso.ie/
- API pattern: `https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadDataset/<MATRIX>/JSON-stat/2.0/en`

| Table | Contents | Page |
|---|---|---|
| PEA03 | Estimated migration by age, sex, flow | https://data.cso.ie/table/PEA03 |
| PEA18 | Migration by sex and country of origin/destination | https://data.cso.ie/table/PEA18 |
| PEA23 | Emigration by sex and citizenship | https://data.cso.ie/table/PEA23 |
| PEA24 | Immigration by sex and citizenship | https://data.cso.ie/table/PEA24 |
| PEA27 | Persons with non-EU/EFTA citizenship | https://data.cso.ie/table/PEA27 |
| MEASQ01–03 | Estimated migration flows (experimental, admin data) | https://data.cso.ie/table/MEASQ01 |
| FNA06, FNA10 | PPSN allocations to foreign nationals (ends 2018) | https://data.cso.ie/table/FNA06 |
| IAIP01/02/11/12 | International protection applicants in administrative data | https://data.cso.ie/table/IAIP01 |

## 2. Department of Enterprise, Tourism and Employment (DETE)

Employment permits. One publication page per year, each with XLSX tables by
nationality, sector, county and company.

- Hub: https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/
- Years collected: 2015–2026 (48 files)
- Example: https://enterprise.gov.ie/en/publications/employment-permit-statistics-2025.html

## 3. Department of Justice, Home Affairs and Migration

### via data.gov.ie (Ireland's open data portal)

- Publisher page: https://data.gov.ie/organization/department-of-justice
- CKAN API: `https://data.gov.ie/api/3/action/package_search?q=organization:department-of-justice`

| Dataset | Coverage |
|---|---|
| https://data.gov.ie/dataset/visa-applications-and-decisions-year-and-month | 2017–2026 |
| https://data.gov.ie/dataset/visa-applications-and-decisions-year-and-nationality | 2017–2026 |
| https://data.gov.ie/dataset/domestic-residence-permissions-applications-and-decisions-year-and-month | 2017–2024 |
| https://data.gov.ie/dataset/eu-treaty-rights-applications-and-decisions-by-year-and-month | 2017–2026 |
| https://data.gov.ie/dataset/family-reunification-applications-and-decisions-by-year-and-month | 2017–2026 |

### Directly from gov.ie

- Statistics page: https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/publications/departmental-data-and-statistical-reports/
- International Protection in Numbers (26 monthly PDF reports, Apr 2024 – May 2026):
  https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/collections/international-protection-in-numbers/

## 4. Houses of the Oireachtas

Parliamentary questions and the Ministers' answers — the publication route for
statistics that have no machine-readable release (naturalisation in particular).

- API spec: https://api.oireachtas.ie/v1/swagger.json
- Endpoint used: `https://api.oireachtas.ie/v1/questions?date_start=…&date_end=…&show_answers=true`
- Harvested: 2016-01-01 → 2026-09-12; 24,628 migration-related PQs retained
- Each PQ is citable at `https://www.oireachtas.ie/en/debates/question/<date>/<number>/`

### Supporting documents attached to answers

When an answer is too large to print in the record, the Minister supplies a
spreadsheet or Word file, published under
`https://data.oireachtas.ie/ie/oireachtas/debates/questions/supportingDocumentation/`.
**The /questions API strips these links out of the answer text**, so they are
only discoverable by scraping each PQ's own web page (script 15). 2,038
permit-related PQ pages were scraped, yielding 37 distinct attachments.

These are the only public source for employment permits **by permit type**
(Critical Skills, General, Intra-Company Transfer, etc.) — DETE's annual
publication has no type dimension at all.

| Attachment | Contents | Parliamentary answer |
|---|---|---|
| `2025-05-20_pq381-20-05-25_en.xlsx` | Permits issued by permit type × nationality × year, and by permit type × economic sector × year, 2020–2024 | https://www.oireachtas.ie/en/debates/question/2025-05-20/381/ |
| `2025-03-26_pq56-26-03-2025_en.docx` | Critical Skills permits issued by SOC occupation code, 2024 (137 occupations) | https://www.oireachtas.ie/en/debates/question/2025-03-26/56/ |
| `2025-05-20_pq-388-390-20-05-25_en.xlsx` | Permits cancelled / revoked / suspended by nationality, 2020–2024 | https://www.oireachtas.ie/en/debates/question/2025-05-20/388/ |
| `2019-01-16_pq-159-16-1-19_en.xlsx` | Permits by economic sector and occupation, 2010–2018 | https://www.oireachtas.ie/en/debates/question/2019-01-16/159/ |

Permit-type figures printed inline in answers (rather than attached) are in
`employment_permits_by_type_from_pq_text.csv`. **Read the `caption_before_table`
column before using these** — most are narrow subsets (for example Critical
Skills permits issued to doctors only), not whole-system totals. The one full
breakdown is PQ 194 of 16 June 2026, giving applications by type for 2023–2026.

Series quoted in the report come from these specific answers:

| Series | Parliamentary answer |
|---|---|
| International protection applications, 2011–2026 | https://www.oireachtas.ie/en/debates/question/2026-06-23/515/ |
| Employment permits issued, 2011–2026 | https://www.oireachtas.ie/en/debates/question/2026-06-23/289/ |
| Certificates of naturalisation issued, 2013–2022 | https://www.oireachtas.ie/en/debates/question/2023-11-28/424/ |
| Citizenship applications received, 2021–2026 | https://www.oireachtas.ie/en/debates/question/2026-09-07/2397/ |
| International protection refusals, 2013–2022 | https://www.oireachtas.ie/en/debates/question/2022-12-06/481/ |
| Deportation orders issued, 2011–2021 | https://www.oireachtas.ie/en/debates/question/2021-11-23/474/ |
| Deportation orders revoked, 2015–2024 | https://www.oireachtas.ie/en/debates/question/2025-05-07/316/ |
| Employment permits by type (issued), 2020–2024 | https://www.oireachtas.ie/en/debates/question/2025-05-20/381/ |
| Employment permits by type (applications), 2023–2026 | https://www.oireachtas.ie/en/debates/question/2026-06-16/194/ |
| Critical Skills permits by occupation, 2024 | https://www.oireachtas.ie/en/debates/question/2025-03-26/56/ |

## 5. Eurostat

Used where Irish publications are stale or chart-only. Ireland's Immigration
Service Delivery supplies these under statutory EU reporting, and the Department
of Justice's own statistics page directs users to them.

| Dataset | Contents |
|---|---|
| https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctza/default/table?lang=en | Asylum applicants, 2008–2025 |
| https://ec.europa.eu/eurostat/databrowser/view/migr_acq/default/table?lang=en | Acquisitions of citizenship, to 2024 |
| https://ec.europa.eu/eurostat/databrowser/view/migr_resfirst/default/table?lang=en | First residence permits, 2008–2025 |

## Notes and caveats

1. **`ipo.gov.ie` served an expired TLS certificate on 12 September 2026** (valid
   Sectigo certificate for the right host, expired 5 September 2026). The
   gov.ie-hosted copies of the same IPO reports were used instead.
2. **The Department's international-protection CSV stops in March 2021.** Later
   IPO output is chart-based PDF, so the continuous annual series comes from the
   parliamentary answer of 23 June 2026 and from Eurostat.
3. **Suppressed cells.** The by-nationality DoJ files mask small counts with
   `*` (8,162 cells). These are kept as `suppressed=True` rather than dropped,
   so annual totals are taken from the by-month files, which are unsuppressed.
4. **Part-year figures.** 2026 employment permits cover January–August 2026;
   2026 visa figures were last updated 31 July 2026; the CSO's 2026 estimates
   are for the year to April 2026.
5. **CSO estimates are rebased.** Figures from 2022 onwards reflect Census 2022;
   they are estimates in thousands, not administrative counts.
6. **Eurostat rounds** asylum figures to the nearest 5, which is why it differs
   from the Irish source by up to 0.34% (see `cross_source_validation.csv`).
7. **Permit-type totals come from a different vintage** than the DETE annual
   files. The PQ attachment was extracted in May 2025 and its yearly totals
   differ from the current DETE spreadsheets by −56 to +8 permits (at most
   0.34%), because administrative figures are revised continuously. Use the
   DETE totals for headline counts and the attachment for the type split.

# Irish migration statistics, 2015–2026: what the official data shows

Compiled 12 September 2026 from Irish government sources. Every figure below is
linked to the body that published it, and is reproduced in
[`data/processed/headline_series.csv`](data/processed/headline_series.csv) with
its source URL. Method and caveats: [`docs/SOURCES.md`](docs/SOURCES.md).

Read the units carefully: the CSO publishes *estimates in thousands* for the
year to April, while the departments publish *administrative counts* for the
calendar year. They measure different things and should not be added together.

---

## 1. Headline: the migration surge peaked in 2024 and is now unwinding

CSO Population and Migration Estimates, thousands, year to April
([PEA24](https://data.cso.ie/table/PEA24), [PEA23](https://data.cso.ie/table/PEA23),
[PEA03](https://data.cso.ie/table/PEA03)):

| Year to April | Immigration | Emigration | Net |
|---|---|---|---|
| 2015 | 75.9 | 70.0 | **+5.9** |
| 2017 | 95.3 | 56.1 | +39.2 |
| 2020 | 95.6 | 50.9 | +44.7 |
| 2021 | 74.1 | 52.3 | +21.8 |
| 2022 | 107.8 | 56.1 | +51.7 |
| 2023 | 141.6 | 64.0 | +77.6 |
| 2024 | **149.2** | 69.9 | **+79.3** |
| 2025 | 125.3 | 65.6 | +59.7 |
| 2026 | 110.6 | 62.5 | +48.1 |

Three phases stand out. Recovery from the post-crash emigration era (2015–2019),
when net migration went from near zero to roughly +44,000 as emigration fell by
a quarter. A pandemic interruption in 2021. Then a sharp surge to a **record
149,200 immigrants in the year to April 2024** — the highest in the CSO series —
followed by two consecutive years of decline, down 26% to 110,600 by April 2026.

The correction is on the inflow side. Emigration has barely moved (69,900 to
62,500); the entire swing is fewer arrivals.

## 2. The composition changed more than the total

Immigration by citizenship ([PEA24](https://data.cso.ie/table/PEA24), thousands):

| Year to April | Irish | UK | EU14 | EU15–EU27 | Rest of world |
|---|---|---|---|---|---|
| 2015 | 26.6 | 5.0 | 10.2 | 12.2 | **21.9** |
| 2020 | 33.6 | 5.5 | 9.2 | 9.9 | 37.4 |
| 2022 | 23.5 | 3.8 | 13.2 | 8.6 | 58.8 |
| 2024 | 30.0 | 5.4 | 14.0 | 13.0 | **86.8** |
| 2026 | 30.2 | 4.3 | 11.5 | 9.2 | 55.5 |

Non-EU, non-UK immigration rose from **21,900 (29% of arrivals) in 2015 to
86,800 (58%) in 2024** — a fourfold increase that accounts for essentially all
the growth in the total. Returning Irish citizens were remarkably stable
throughout at 23,000–36,000 a year, and EU flows were flat. The decline since
2024 is likewise concentrated in the non-EU category, down to 55,500.

## 3. Employment permits: a step change, not a trend

Department of Enterprise, Tourism and Employment,
[statistics hub](https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/):

| Year | Issued | Refused | Withdrawn |
|---|---|---|---|
| 2015 | 7,253 | 797 | 166 |
| 2016 | 9,373 | 1,321 | 206 |
| 2017 | 11,361 | 1,458 | 319 |
| 2018 | 13,398 | 1,247 | 542 |
| 2019 | 16,383 | 1,364 | 848 |
| 2020 | 16,419 | 956 | 660 |
| 2021 | 16,275 | 957 | 736 |
| 2022 | **39,955** | 3,476 | 1,705 |
| 2023 | 30,981 | 1,575 | 641 |
| 2024 | 39,390 | 2,456 | 1,064 |
| 2025 | 31,044 | 3,432 | — |
| 2026 (Jan–Aug) | 26,629 | 2,967 | — |

Permits issued rose **4.3× between 2015 and 2025**. The striking feature is the
discontinuity: a smooth climb to about 16,400 by 2019, a flat pandemic plateau,
then a near-instant jump to 39,955 in 2022 when the quota and occupations lists
were loosened. Since then the level has oscillated between roughly 31,000 and
39,000 rather than continuing to grow. At 26,629 in the first eight months,
2026 is running ahead of 2025's pace.

**India supplies about a third of all permits** — 9,947 in 2025 (32.0%), up from
2,112 in 2015 (29.1%). The rest of the top five has turned over substantially:
the Philippines (3,398) and Brazil (3,381) are now second and third, together
21.8%, where in 2015 the runners-up were Pakistan and the United States.

By sector in 2025, **health and social work takes 25.6%** (7,948 permits), ahead
of ICT (3,630, 11.7%) and accommodation and food services (3,499, 11.3%). The
permit system is now primarily a healthcare-staffing instrument.

### 3a. By permit type: General has overtaken Critical Skills

DETE's annual publication has **no permit-type dimension**. The breakdown below
comes from the spreadsheet the Minister attached to
[PQ 381 of 20 May 2025](https://www.oireachtas.ie/en/debates/question/2025-05-20/381/),
which is the only public source giving permits issued by type
([`employment_permits_by_type_annual.csv`](data/processed/employment_permits_by_type_annual.csv)):

| Permit type | 2020 | 2021 | 2022 | 2023 | 2024 |
|---|---|---|---|---|---|
| Critical Skills (CSEP) | 8,199 | 9,435 | **21,448** | 15,673 | 17,168 |
| General (GEP) | 6,958 | 5,899 | 16,184 | 12,903 | **19,478** |
| Intra-Company Transfer | 899 | 663 | 1,876 | 1,924 | 1,911 |
| Sport and Cultural | 93 | 165 | 164 | 184 | 482 |
| Reactivation | 29 | 24 | 69 | 98 | 170 |
| Contract for Services | 105 | 58 | 60 | 86 | 74 |
| Intra-Company Transfer (Training) | 37 | 1 | 74 | 32 | 42 |
| Internship | 20 | 25 | 43 | 55 | 42 |
| Dependant/Partner/Spouse | 15 | 6 | 23 | 23 | 30 |
| Exchange Agreement | 8 | 7 | 20 | 1 | 1 |
| **Total** | **16,363** | **16,283** | **39,961** | **30,979** | **39,398** |
| *CSEP share* | *50.1%* | *57.9%* | *53.7%* | *50.6%* | *43.6%* |
| *GEP share* | *42.5%* | *36.2%* | *40.5%* | *41.7%* | *49.4%* |

Two types are 93% of the system, and **their balance has inverted**. Critical
Skills peaked at 57.9% of permits in 2021 and fell to 43.6% by 2024; General rose
from 36.2% to 49.4% and **overtook Critical Skills in 2024** for the first time
in the period. The 2022 surge was disproportionately a Critical Skills event
(CSEP more than doubled, +12,013); the 2024 recovery was a General one
(GEP +6,575 while CSEP rose only 1,495).

Applications confirm the trend has continued, from
[PQ 194 of 16 June 2026](https://www.oireachtas.ie/en/debates/question/2026-06-16/194/):

| Applications received | 2023 | 2024 | 2025 | 2026 (to mid-June) |
|---|---|---|---|---|
| Critical Skills | 17,496 | 17,548 | 12,622 | 6,047 |
| General | 18,056 | 25,785 | 23,371 | 14,864 |
| Intra-Company Transfer | 2,039 | 1,949 | 1,238 | 628 |
| **All types** | **38,211** | **46,379** | **38,459** | **22,202** |

**Critical Skills applications fell 28% between 2023 and 2025** while General rose
29%. By mid-2026 General applications were running at 2.5× Critical Skills. The
same answer records processing times of **10 working days for Critical Skills
against 33 for General**, and decisions of 31,145 issued / 3,274 refused in 2025.

### 3b. The two streams draw on different countries and different sectors

Permits issued in 2024 by type and nationality
([`employment_permits_by_type_nationality.csv`](data/processed/employment_permits_by_type_nationality.csv)):

| Critical Skills (17,168) | | General (19,478) | |
|---|---|---|---|
| India | 9,068 (52.8%) | Brazil | 3,797 (19.5%) |
| Philippines | 1,365 (8.0%) | India | 3,767 (19.3%) |
| Brazil | 657 (3.8%) | Philippines | 2,641 (13.6%) |
| Pakistan | 607 (3.5%) | Pakistan | 1,105 (5.7%) |
| South Africa | 572 (3.3%) | China | 1,091 (5.6%) |

**Critical Skills is overwhelmingly an India pipeline** — more than half of all
such permits — whereas General is spread across Brazil, India and the
Philippines in roughly equal thirds at the top.

By sector, the split is close to a clean division of labour
([`employment_permits_by_type_sector.csv`](data/processed/employment_permits_by_type_sector.csv), 2024):

| Sector | Total | Critical Skills | General |
|---|---|---|---|
| Health & Social Work | 12,507 | 5,917 (47.3%) | 6,556 (52.4%) |
| Information & Communication | 6,787 | 4,932 (72.7%) | 1,040 (15.3%) |
| Agriculture, Forestry & Fishing | 3,625 | 28 (0.8%) | 3,536 (97.5%) |
| Accommodation & Food Services | 3,359 | 97 (2.9%) | 3,219 (95.8%) |
| Financial & Insurance | 2,318 | 1,979 (85.4%) | 237 (10.2%) |
| Construction | 1,525 | 778 (51.0%) | 714 (46.8%) |
| Transport & Storage | 1,282 | 132 (10.3%) | 1,139 (88.8%) |

ICT and financial services run almost entirely on Critical Skills; agriculture,
hospitality and transport almost entirely on General. Health is the one large
sector that uses both about equally — and it is the largest, which is why the
General stream has grown fastest.

### 3c. Within Critical Skills, nursing dominates

A further attachment, to
[PQ 56 of 26 March 2025](https://www.oireachtas.ie/en/debates/question/2025-03-26/56/),
breaks 2024 Critical Skills permits down to SOC occupation — 137 occupations in
all ([`employment_permits_by_type_occupation.csv`](data/processed/employment_permits_by_type_occupation.csv)):

| SOC | Occupation | Permits | Share |
|---|---|---|---|
| 2231 | Nurses | 5,031 | 29.3% |
| 2136 | Programmers and software development professionals | 2,247 | 13.1% |
| 2135 | IT business analysts, architects and systems designers | 936 | 5.5% |
| 2424 | Business and financial project management professionals | 789 | 4.6% |
| 2423 | Management consultants and business analysts | 706 | 4.1% |
| 2421 | Chartered and certified accountants | 657 | 3.8% |

**Nurses alone are 29.3% of all Critical Skills permits**, and the top ten
occupations account for 71.6%. The "critical skills" route, despite covering 137
distinct occupations, is in practice concentrated in nursing and software.

## 4. International protection: a spike that has half-receded

From the table given to the Dáil on
[23 June 2026](https://www.oireachtas.ie/en/debates/question/2026-06-23/515/):

| Year | Applications | | Year | Applications |
|---|---|---|---|---|
| 2015 | 3,276 | | 2021 | 2,647 |
| 2016 | 2,244 | | 2022 | **13,642** |
| 2017 | 2,920 | | 2023 | 13,271 |
| 2018 | 3,674 | | 2024 | **18,553** |
| 2019 | 4,783 | | 2025 | 13,162 |
| 2020 | 1,565 | | 2026 (to 31 May) | 5,135 |

Applications ran at 1,500–4,800 a year for the whole of 2015–2021, then jumped
**5.2× in a single year** to 13,642 in 2022, peaking at 18,553 in 2024 before
falling 29% to 13,162 in 2025. The 2026 partial figure implies broad stability
rather than a further fall.

This is a separate stream from the Ukrainian displacement: **129,161 grants of
temporary protection** to 27 August 2026
([UA37](https://data.gov.ie/dataset/ua37-temporary-protection-granted-to-arrivals-from-ukraine)),
now arriving at about 110 a week against a 2022 peak of 5,037.

The origin mix is volatile, which is itself the main characteristic. Georgia and
Algeria led in 2022 (19.8% and 12.9%); Nigeria and Jordan led in 2024 (21.7% and
15.4%); Somalia, Nigeria and Pakistan led in 2025
([Eurostat migr_asyappctza](https://ec.europa.eu/eurostat/databrowser/view/migr_asyappctza/default/table?lang=en)).
Jordan went from negligible to 2,860 applications and back within two years.

The processing backlog has been falling: applications pending at the
International Protection Office dropped from 23,863 at end-September 2024 to
**12,869 in May 2026**, though median processing time for standard cases was
still 76 weeks
([IPO summary report, May 2026](https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/collections/international-protection-in-numbers/)).

## 5. Naturalisation: the fastest-moving series of all

Certificates of naturalisation issued
([PQ, 28 November 2023](https://www.oireachtas.ie/en/debates/question/2023-11-28/424/);
2023–24 from [Eurostat migr_acq](https://ec.europa.eu/eurostat/databrowser/view/migr_acq/default/table?lang=en)):

| Year | Certificates | | Year | Certificates |
|---|---|---|---|---|
| 2013 | 24,202 | | 2020 | 5,468 |
| 2015 | 13,532 | | 2021 | 9,776 |
| 2017 | 8,186 | | 2022 | 13,601 |
| 2019 | 5,781 | | 2023 | 18,265 |
| | | | 2024 | **24,059** |

Naturalisations collapsed by 77% from 2013 to 2020, then quadrupled to 24,059 by
2024 — back to the level of a decade earlier.

Applications are rising faster still
([PQ, 7 September 2026](https://www.oireachtas.ie/en/debates/question/2026-09-07/2397/)):

| 2021 | 2022 | 2023 | 2024 | 2025 | 2026 (to date) |
|---|---|---|---|---|---|
| 11,975 | 17,202 | 22,690 | 27,032 | **41,511** | 22,055 |

**2025 applications were 3.5× the 2021 level.** The Department reports that
digitisation cut median processing time from 19 months (2022) to 15 (2023) to
**8 months (2024)**, with 31,000 decisions made in 2024
([PQ, 12 November 2025](https://www.oireachtas.ie/en/debates/question/2025-11-12/768/)).
This is the lagged consequence of the 2015–2019 arrivals reaching the five-year
residency threshold, and it will keep climbing.

## 6. Visas: record volumes, tightening decisions

Department of Justice, [data.gov.ie](https://data.gov.ie/dataset/visa-applications-and-decisions-year-and-month):

| Year | Received | Granted | Refused | Grant rate |
|---|---|---|---|---|
| 2017 | 125,676 | 110,552 | 15,973 | 87.4% |
| 2019 | 155,760 | 137,603 | 18,504 | 88.1% |
| 2020 | 43,871 | 37,962 | 5,752 | 86.8% |
| 2021 | 52,253 | 42,674 | 4,565 | 90.3% |
| 2023 | 166,656 | 138,502 | 21,610 | 86.5% |
| 2024 | 201,687 | 159,790 | 28,841 | 84.7% |
| 2025 | **205,618** | 161,497 | 35,913 | **81.8%** |
| 2026 (to 31 Jul) | 124,315 | 85,704 | 18,866 | 82.0% |

Visa applications fell 72% in 2020 and took until 2023 to pass their pre-pandemic
peak; 2025 set a record at 205,618. Against that, **the grant rate has fallen
every year since 2021, from 90.3% to 81.8%** — refusals more than doubled from
15,973 in 2017 to 35,913 in 2025. Rising volume and rising refusal are happening
together.

First residence permits show the same post-2021 plateau
([Eurostat migr_resfirst](https://ec.europa.eu/eurostat/databrowser/view/migr_resfirst/default/table?lang=en)):
38,433 in 2015, peaking at 88,595 in 2023, easing to 72,978 in 2025. Education
is consistently the largest single reason (34,729 in 2025), ahead of employment
(16,759).

---

## How reliable is this?

Three of these indicators are published independently by two bodies, so they can
be checked against each other
([`cross_source_validation.csv`](data/processed/cross_source_validation.csv)):

| Indicator | Sources | Agreement |
|---|---|---|
| Employment permits, 2015–2025 | DETE spreadsheets vs. Minister's answer to the Dáil | **exact, all 11 years** |
| Asylum applications, 2015–2025 | Eurostat vs. Minister's answer | within 0.34% |
| Citizenship, 2015–2022 | Eurostat vs. Minister's answer | within 0.24% |

The small residuals are explained: Eurostat rounds asylum counts to the nearest
5, and administrative totals are revised after publication. Within each source,
our parsed per-nationality figures also reconcile exactly to the publisher's own
"Grand Total" row for all 12 years of permit data.

Four limits are worth stating plainly:

1. **The 2026 figures are part-year** and not comparable with full years:
   permits cover January–August, visas to 31 July, protection applications to
   31 May, CSO estimates to April.
2. **No single Irish source gives a continuous 10-year asylum series.** The
   Department's own CSV stops in March 2021 and later IPO reporting is
   chart-based PDF, so the series here rests on a parliamentary answer,
   corroborated by Eurostat.
3. **Small counts are suppressed.** The Department's by-nationality files mask
   8,162 cells with `*`; nationality breakdowns therefore understate totals by
   0.1–21% depending on the stream, and annual totals here are taken from the
   unsuppressed monthly files instead.
4. **CSO estimates are estimates**, rebased on Census 2022 from 2022 onward, and
   are not interchangeable with the departments' administrative counts.

## Verifying any number here

Every downloaded file is listed in
[`data/processed/sources_register.csv`](data/processed/sources_register.csv)
with its URL, retrieval timestamp and SHA-256 (103 files, no failures). Every
row of `headline_series.csv` carries a `source_url`. All 24,628 parliamentary
questions consulted are indexed in
[`oireachtas_pq_index.csv`](data/processed/oireachtas_pq_index.csv), each with a
direct `oireachtas.ie` link to the answer.

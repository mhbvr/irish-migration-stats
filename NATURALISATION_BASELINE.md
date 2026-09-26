# A baseline for the 2026 naturalisation law changes: what data exists

**Purpose.** To identify the data that can serve as a **pre-change baseline**
for the Irish Nationality and Citizenship (Amendment) Bill 2026, so that its
effects can later be measured against how the system behaved before it.

**Status of the law (27 September 2026).** Government approved priority drafting
in September 2026 and published the
[General Scheme](https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/publications/general-scheme-of-the-irish-nationality-and-citizenship-amendment-bill-2026/)
([PDF](https://assets.gov.ie/static/documents/cadca21c/General_Scheme_of_the_Irish_Nationality_and_Citizenship_Amendment_Bill_2026.pdf))
on 21 September; it goes to pre-legislative scrutiny next. There is no Bill text
yet, and commencement will be **by ministerial order, provision by provision**.
The provisions below are taken from that Scheme.

Every figure here is read from a file in this repository and carries its
source; the full set is in
[`data/processed/naturalisation_baseline/baseline_indicators.csv`](data/processed/naturalisation_baseline/baseline_indicators.csv)
(423 values), with provenance for every download in
[`sources_register.csv`](data/processed/sources_register.csv).

---

## 1. Summary: provision by provision

| Provision (General Scheme) | What it could change | Baseline available? |
|---|---|---|
| **s.15** residence 5 → 8 years | fewer eligible; fewer applications; later naturalisation | **Good** for outcomes; **partial** for the eligible population |
| **s.15A** spouses 3 → 5 years | fewer spouse-route certificates | **Good** — route series 2016–2025 |
| **s.15(1)(f), s.15F** self-sufficiency (income floor + welfare/housing bar) | exclusion of lower-paid and welfare-receiving residents | **Partial** — population-level only |
| **s.15(1)(h)–(i)** language and civics tests | exclusion by language ability; slower processing | **Partial** — Census proxy; no applicant data |
| **s.15(1)(g), Sch. 1** lifetime immigration-offence bar | refusals | **None** — offences are not recorded |
| **s.16A** seven new non-reckonable categories | Ukrainians and refused EU Treaty Rights applicants lose accrued time | **Good** for the populations affected |
| **s.6B** children born in Ireland | fewer children entitled to citizenship at birth | **Partial** — births by mother's nationality, not by parents' permission |
| **s.19** new revocation ground | revocations | **None** — no series published |
| Administration | processing time, backlog, ceremonies | **Good**, except backlog |

---

## 2. What the system looks like now

### 2.1 Outcomes (all provisions)

Certificates of naturalisation issued, 2016–2025, from the file attached to
[PQ 483 of 22 January 2026](https://www.oireachtas.ie/en/debates/question/2026-01-22/483/),
with applications from [PQ 2397 of 7 September 2026](https://www.oireachtas.ie/en/debates/question/2026-09-07/2397/):

| | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|
| Applications received | — | — | 11,975 | 17,202 | 22,690 | 27,032 | **41,511** | 22,055 (to 7 Sep) |
| Certificates issued | 5,778 | 5,465 | 9,766 | 13,596 | 18,265 | 24,068 | **29,919** | 6,750 conferred (to Sep) |
| Refusals | 50 | 8 | 696 | 404 | 129 | 187 | 377 | — |
| Median processing time (months) | — | — | 24 | 19 | 15 | 8 | 8 | — |

Refusals: [PQ 891](https://www.oireachtas.ie/en/debates/question/2026-09-16/891/);
processing time: [PQ 277](https://www.oireachtas.ie/en/debates/question/2026-09-17/277/).
In 2025, **25 citizenship ceremonies** conferred **29,300 certificates**; in 2026 to
September, 5 ceremonies and 6,750 ([PQ 2397](https://www.oireachtas.ie/en/debates/question/2026-09-07/2397/)).

**By route** (same attachment), the split that s.15 and s.15A act on separately:

| Route | 2016 | 2020 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|
| Standard adult (s.15, 5 years) | 5,709 | 3,657 | 9,862 | 15,999 | **19,329** |
| Spouse / civil partner of Irish citizen (3 years)¹ | 2,001 | 1,203 | 2,470 | 3,791 | **2,929** |
| Granted international protection | 200 | 121 | 954 | 1,197 | 712 |
| Minors | 2,061 | 481 | 4,950 | 3,081 | **6,949** |

¹ The Department labels this column "S15 residency"; the accompanying answer ties
section 15 to the 3-year spouse rule, so this is read as the spouse route. That
reading should be confirmed with the Department before it is relied on.

**The naturalisation rate** — acquisitions per 100 non-citizen residents — is the
best single comparable indicator, because it adjusts for the size of the
non-citizen population
([Eurostat migr_acqs](https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en)):

| | 2013 | 2016 | 2019 | 2020 | 2022 | 2024 |
|---|---|---|---|---|---|---|
| All non-citizens | 4.52% | 1.84% | 0.95% | 0.85% | 2.07% | **2.94%** |
| Non-EU citizens | 16.09% | 5.24% | 1.63% | 1.18% | 3.33% | **4.25%** |
| EU citizens | 0.45% | 0.80% | 0.65% | 0.55% | 0.84% | 1.25% |

In 2024 Ireland ranked **9th of 31** reporting countries (median 1.41%; Sweden
highest at 7.55%) — the position the Scheme's own comparisons with other EU
states can be tested against ([`eu_naturalisation_rate_rank.csv`](data/processed/naturalisation_baseline/eu_naturalisation_rate_rank.csv)).

### 2.2 Who naturalises (nationality)

Certificates per 100 residents of each citizenship, dividing 2022 certificates by
the Census 2022 count of residents
([CSO F5065](https://data.cso.ie/table/F5065); 631,785 non-Irish citizens in all)
— [`naturalisation_rate_by_nationality.csv`](data/processed/naturalisation_baseline/naturalisation_rate_by_nationality.csv), 109 citizenships:

| Citizenship | Residents 2022 | Certificates 2022 | per 100 residents | Certificates 2025 |
|---|---|---|---|---|
| Poland | 93,680 | 874 | 0.93 | 1,386 |
| United Kingdom | 83,347 | 1,255 | 1.51 | 1,605 |
| **India** | 45,449 | 1,177 | 2.59 | **6,298** |
| Romania | 43,323 | 893 | 2.06 | 1,752 |
| Brazil | 27,338 | 523 | 1.91 | 2,353 |
| China | 13,050 | 389 | 2.98 | 1,073 |
| Ukraine | 11,791 | 177 | 1.50 | 354 |
| **Pakistan** | 9,309 | 1,065 | **11.44** | 839 |
| **Nigeria** | 8,368 | 784 | **9.37** | 1,074 |

Propensity varies tenfold. EU citizens, who gain little from naturalising, sit
below 1 per 100; long-settled non-EU groups (Pakistan, Nigeria) near 10. **The
2025 surge is Indian**: 6,298 certificates against 45,449 Indian residents in
2022. Indian nationals also held 52.8% of Critical Skills Employment Permits in
2024 (see [`REPORT.md`](REPORT.md) §3b), so much of this pipeline is recent
arrivals on permits — the group a longer residence period reaches first.

### 2.3 The pipeline of future applicants (s.15 residence 5 → 8)

A person arriving in year *t* can apply after five years under current law, after
eight under the Scheme. So the arrival cohorts of 2018–2021, currently becoming
eligible, are the ones that would be pushed back.

| | 2016 | 2018 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Non-EU/non-UK immigration, year to April ([CSO PEA24](https://data.cso.ie/table/PEA24)) | 23,600 | 36,900 | 37,400 | 16,100 | 58,800 | 81,100 | 86,800 | 63,600 |
| Employment permits issued ([DETE](https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/)) | 9,373 | 13,398 | 16,419 | 16,275 | 39,955 | 30,981 | 39,390 | 31,044 |

Stock of valid residence permits on 31 December
([Eurostat migr_resvalid](https://ec.europa.eu/eurostat/databrowser/view/migr_resvalid/default/table?lang=en)):

| Reason | 2019 | 2022 | 2025 |
|---|---|---|---|
| **All** | 168,297 | 234,057 | **331,623** |
| Employment | 39,404 | 62,200 | 96,023 |
| Family | 34,317 | 52,854 | 56,972 |
| Education (already non-reckonable) | 50,946 | 52,449 | 62,997 |
| Other | 40,419 | 60,547 | 103,537 |
| Refugee status | 2,406 | 5,297 | 10,863 |
| Subsidiary protection | 805 | 710 | 1,231 |

The CSO counts 356,968 residents with non-EU/EFTA/candidate-country citizenship
in 2024 ([PEA27](https://data.cso.ie/table/PEA27)). (Eurostat's "long-term
resident" count for Ireland is only 1,731, because Ireland does not apply the EU
long-term residence directive; it is not a usable measure of the settled
population.)

### 2.4 Populations whose residence would stop counting (s.16A)

- **Ukrainian temporary protection** — every year becomes non-reckonable:
  **129,161** grants to 27 August 2026 ([CSO UA37](https://data.gov.ie/dataset/ua37-temporary-protection-granted-to-arrivals-from-ukraine)),
  granted 24,371 / 55,623 / 25,786 / 9,239 / 11,624 in the years to April
  2022–2026. None of this cohort has yet reached five years, so the change
  forecloses future applications rather than current ones — the baseline is the
  size of the cohort, not its applications.
- **Refused EU Treaty Rights applicants** — time on a temporary permission while
  a case is examined would be lost if the case is refused. EU1 residence-card
  refusals ([Dept of Justice via data.gov.ie](https://data.gov.ie/dataset/eu-treaty-rights-applications-and-decisions-by-year-and-month)):
  1,563 (2017), 735 (2019), 563 (2022), 340 (2024), **551 (2025)**; received
  4,689 and granted 4,506 in 2025.

### 2.5 Self-sufficiency (s.15(1)(f), s.15F)

No data exist on the welfare or housing-support receipt of naturalisation
applicants. Two population-level baselines do:

- **Welfare receipt** — share aged 15–65 receiving any unemployment, disability
  or family/children payment ([ESRI RS229, Table 4.1](https://doi.org/10.26504/rs229), SILC):
  Irish-born 69% / 65% / **56%** and born abroad 76% / 71% / **61%** in
  2014 / 2019 / 2024. This set includes universal Child Benefit; whether that
  counts as a "prescribed" payment is left to regulations.
- **Earnings of permit holders** — of **21,600** active General Employment
  Permits issued after the January 2024 threshold rise, **86.5% pay under
  €44,000**, roughly the gross income at which a one-child family qualifies for
  Working Family Payment; and **7,700** permits (20%) were issued in 2024 at
  sub-standard thresholds ([DETE MAR roadmap review 2025](https://enterprise.gov.ie/en/publications/publication-files/employment-permits-minimum-annual-remuneration-outcome-of-the-roadmap-review-2025.pdf)).
  These are the workers an income floor would bind.

### 2.6 Language (s.15(1)(h))

Among residents who speak a language other than English or Irish at home, the
share who speak English "not well" or "not at all", Census 2022
([CSO F5015](https://data.cso.ie/table/F5015); [`english_ability_by_citizenship.csv`](data/processed/naturalisation_baseline/english_ability_by_citizenship.csv)):

| Citizenship | Speakers | Not well / not at all |
|---|---|---|
| All | 751,507 | 12.7% |
| Ukraine | 5,437 | **49.8%** |
| China | 11,204 | 25.4% |
| Romania | 35,425 | 22.9% |
| Brazil | 22,395 | 20.5% |
| Poland | 79,680 | 15.6% |
| Africa | 21,464 | 7.4% |
| India | 37,420 | **5.0%** |

This is self-reported ability, not a test result, and Ukrainian figures reflect
the first months after arrival. It still identifies who a language test is most
likely to affect: among non-EU groups, Chinese and Brazilian residents, not the
Indian residents who dominate current applications.

### 2.7 Children born in Ireland (s.6B)

Births by mother's nationality ([CSO VSAS80](https://data.cso.ie/table/VSAS80)):

| Mother's nationality | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|
| All births | 57,540 | 54,678 | 54,062 | 54,125 |
| Irish | 75.9% | 74.2% | 72.2% | 70.2% |
| Outside EU and UK | 11.6% | 14.2% | 16.0% | **18.5%** (10,030) |

The rule turns on the *parents' permission type*, which birth registration does
not record, so this bounds the affected group from above. Irish Citizen Child
applications on hand rose from 15 (2024) to 85 (2025) and 191 (2026 to date)
([PQ 2467](https://www.oireachtas.ie/en/debates/question/2026-09-07/2467/)).

### 2.8 Offence bar and revocation (s.15(1)(g), Sch. 1; s.19)

No baseline exists. Offences "committed" are not recorded anywhere, and no
annual series of revocations has been published. Enforcement data are context
only: 4,700 deportation orders signed and 185 enforced deportations in 2025
([PQ 228](https://www.oireachtas.ie/en/debates/question/2026-02-11/228/)).

---

## 3. Gaps, and how to fill them

| Gap | Why it matters | Where to get it |
|---|---|---|
| **Monthly applications received** | Anticipation: applications lodged before commencement keep the s.16A saver, so a pre-commencement rush is likely and must be separated from the effect of the law | PQ or FOI to Citizenship Division, monthly from 2023 |
| **Applications on hand (backlog)** | Processing effects of three new tests | PQ; last public figure is a 2023 mention |
| **Residents by years of reckonable residence** | The direct measure of who crosses 5 vs 8 years | ISD registration data (IRP first-registration date), or a CSO request for Census 2022 by year of arrival |
| **Applications and decisions by route × nationality** | The route and nationality tables exist separately, not together | PQ on the same basis as PQ 483 |
| **Welfare/housing receipt of applicants** | The self-sufficiency test applies to applicants, not the population | Would need DoJ–DSP data linkage; request that the Department publish it in the regulatory impact assessment |
| **Revocations under s.19, by year** | Baseline for the new "public policy" ground | PQ |
| **Spouse-route label** | Confirms that "S15 residency" is the 3-year spouse route | PQ |
| **Births by parents' permission type** | The s.6B test | DoJ; not collected at birth registration |

The research literature does not fill these gaps: none of the 296 publications
since 2023 in the [literature review](literature/LITERATURE_REVIEW.md) studies
naturalisation outcomes.

---

## 4. How to use this as a baseline

1. **Fix the pre-period.** 2016–2025 annually, with **2023–2025** as the
   immediate pre-change level (after the 2020 trough, and after digitisation
   cut processing times). The first year after commencement cannot be compared directly with
   2025: processing time fell from 24 to 8 months in 2021–2024, so decisions
   now follow applications much more closely than they did.
2. **Watch for anticipation.** Applications in 2026 (22,055 to 7 September) are
   the first data point after the announcement. Monthly counts are needed to see
   whether applicants rush to apply before commencement.
3. **Use internal comparison groups** where the law bites differently:
   - standard adult route (5 → 8 years) against the spouse route (3 → 5);
   - nationalities with high vs low English ability (§2.6) for the language test;
   - EU citizens, for whom naturalisation rarely matters, against non-EU
     citizens;
   - arrival cohorts before and after the commencement date, since the
     residence change has no transitional saver.
4. **Report rates as well as counts.** The Eurostat naturalisation rate (§2.1)
   and the per-100-residents rates by nationality (§2.2) adjust for a
   non-citizen population that is growing fast: valid residence permits nearly
   doubled, from 168,297 at end-2019 to 331,623 at end-2025 (§2.3).

---

## Reproducing

```bash
.venv/bin/python scripts/40_fetch_naturalisation_baseline.py   # CSO + Eurostat tables, with provenance
.venv/bin/python scripts/41_build_naturalisation_baseline.py   # builds the indicator files
```

Outputs are in `data/processed/naturalisation_baseline/`: `baseline_indicators.csv`
(423 values, each with its source link), `naturalisation_rate_by_nationality.csv`,
`english_ability_by_citizenship.csv` and `eu_naturalisation_rate_rank.csv`.
The provisions of the General Scheme are summarised from its published text; a
clause-by-clause reading is in the separate `citizenship-bill-2026` project.

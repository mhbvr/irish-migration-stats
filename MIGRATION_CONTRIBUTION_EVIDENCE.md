# What migrants contribute: official statistics against the 2026 naturalisation changes

An evidence base from **official sources only** — the CSO, Revenue (via CSO),
the Medical Council, the Nursing and Midwifery Board, the ESRI, the Department
of Enterprise, the OECD and the European Parliament's research service — on the
contribution of the people the
[General Scheme of the Irish Nationality and Citizenship (Amendment) Bill 2026](https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/publications/general-scheme-of-the-irish-nationality-and-citizenship-amendment-bill-2026/)
would affect. It is organised by the change each set of figures answers.

Every number below is computed or quoted by
[`scripts/43_build_contribution_evidence.py`](scripts/43_build_contribution_evidence.py)
and listed with its source in
[`contribution_evidence.csv`](data/processed/contribution/contribution_evidence.csv)
(53 claims). The script matches each quoted figure against the source text and
stops if it cannot find it.

---

## The headline

- Non-Irish citizens took **47% of all new jobs** created between 2021 and 2026.
- **74%** of non-Irish residents aged 15+ are in work, against **60%** of Irish
  citizens.
- **42%** of doctors qualified outside Ireland; **76%** of new nurses and
  midwives registering in 2024 were educated outside the EU.
- The OECD found immigrants in Ireland contributed **52% more** in taxes than
  they received in benefits and services, against 14% for the Irish-born.
- Of those who already apply for citizenship, only **0.6%** are refused.

---

## 1. Against 5 → 8 years' residence: migrants are already working and contributing

**Work.** Labour Force Survey, April–June 2026 ([CSO QLF48](https://data.cso.ie/table/QLF48)):

| Aged 15+ | Employment rate | Labour force participation |
|---|---|---|
| Irish citizens | 60.0% | 63.0% |
| **Non-Irish citizens** | **74.4%** | **79.3%** |
| of whom non-EU/non-UK | 73.7% | 79.9% |

The rate for non-Irish citizens rose from 68.4% in 2021. (Rates for everyone
aged 15+ include retired people, so the younger migrant population lifts its
rate; the direction of the gap is not in doubt.)

**Growth.** Employment rose by **457,100** between the second quarters of 2021
and 2026; **non-Irish citizens took 215,900 of those jobs — 47%** — and
non-EU/non-UK citizens 35%. Their share of all employment rose from 16.6% to
**21.5%** ([CSO QLF59](https://data.cso.ie/table/QLF59)). Because people who
have naturalised are counted as Irish, these figures *understate* the
contribution of migrants.

**Where they work** (non-Irish share of employment, average of the four
quarters to mid-2026, [QLF59](https://data.cso.ie/table/QLF59)):

| Sector | Non-Irish share |
|---|---|
| Information & communication | **34.4%** |
| Accommodation & food | **33.0%** |
| Health & social work | **25.0%** (97,200 people) |
| Industry | 24.7% |
| Construction | 20.6% |

**Skills.** Among 25–34-year-olds, **70% of the foreign-born have a third-level
qualification, against 58% of the Irish-born**
([ESRI Monitoring Report on Integration 2024](https://doi.org/10.26504/jr11)).
Unemployment among migrants of African origin has fallen to **6%**, having been
persistently high throughout 2009–2019.

**Other EU countries are moving the other way.** Minimum residence for
naturalisation ranges from 3 to 10 years across the EU; **Germany lowered its
requirement from 8 to 5 years in 2024**, while Finland and Cyprus raised theirs
from 5 to 8 ([European Parliament Research Service, 2025](https://www.europarl.europa.eu/RegData/etudes/BRIE/2025/769502/EPRS_BRI%282025%29769502_EN.pdf)).

---

## 2. The health service depends on the people the Bill targets

- **Doctors.** 27.8% of registered doctors took their primary medical degree
  outside Ireland, the EU and the UK, and a further 13.8% in the EU or UK —
  **41.6% qualified outside Ireland**. In the General Division (doctors registered neither as
  specialists nor as trainees) **58.7%** hold non-EU/UK qualifications, as do **66.6%**
  of junior hospital doctors not on a training scheme
  ([Medical Council, Workforce Intelligence Report 2024](https://www.medicalcouncil.ie/news-and-publications/reports/medical-workforce-intelligence-report-2024.pdf)).
- **Nurses and midwives.** Of 7,120 new registrants in 2024, **5,426 (76%) were
  educated outside the EU**, against 1,569 educated in Ireland; the non-EU
  figure has risen from 3,021 in 2022. **30,146 of the 84,213** on the Register
  (35.8%) were educated outside Ireland — 18,464 in India alone
  ([NMBI, State of the Register 2024](https://www.nmbi.ie/NMBI/media/NMBI/NMBI-State-of-the-Register-2024.pdf?ext=.pdf)).
- **Permits.** Nurses received **5,031 Critical Skills Employment Permits in
  2024** — 29.3% of all such permits
  ([Dept of Enterprise data, PQ 56 of 26 March 2025](https://www.oireachtas.ie/en/debates/question/2025-03-26/56/)).
  Health and social work took 25.6% of all employment permits issued in 2025
  (see [`REPORT.md`](REPORT.md) §3).

A longer, harder road to citizenship makes Ireland a less attractive
destination for exactly these workers — and the NMBI and Medical Council
figures show the health service could not currently be staffed without them.

---

## 3. Against the self-sufficiency test: migrants pay in more than they take out

- **Public finances.** In the OECD's comparison of 25 countries (2006–2018),
  immigrants in Ireland made a **net fiscal contribution of 1.57% of GDP**;
  still **+0.62% of GDP** after being charged their share of public services
  such as health and education. Foreign-born residents contributed **52% more
  than they received**, against 14% for the Irish-born (OECD *International
  Migration Outlook 2021*, as summarised in
  [ESRI, Literature review on the fiscal impacts of immigration, 2026](https://doi.org/10.26504/sustat141)).
- **Welfare.** Immigrants had **higher employment rates than the Irish-born
  throughout 2014–2024**. People born in Asia were *less* likely to receive an
  unemployment payment (12%) than the Irish-born (16%), as were those from
  Western EU countries (13%)
  ([ESRI, Social transfers utilisation among migrants and Irish-born, 2026](https://doi.org/10.26504/rs229)).
- **The State set their pay.** 86.5% of General Employment Permits issued since
  the January 2024 threshold rise pay under €44,000 — the Department's own
  minimum-salary thresholds
  ([DETE, Minimum Annual Remuneration review 2025](https://enterprise.gov.ie/en/publications/publication-files/employment-permits-minimum-annual-remuneration-outcome-of-the-roadmap-review-2025.pdf)).
  An income floor or in-work-benefit bar would exclude workers the State itself
  admitted on those terms.

---

## 4. Against writing off Ukrainian temporary-protection time: they work

Revenue data on arrivals from Ukraine ([CSO UA29](https://data.cso.ie/table/UA29),
[UA30](https://data.cso.ie/table/UA30)):

| | First / peak | Latest (Aug 2026) |
|---|---|---|
| Active jobs held | 12,963 (May 2023) | **32,595** (+151%) |
| People who have held a job in Ireland | — | **45,650** |
| Receiving income support | 38,763 (peak, Feb 2024) | **26,888** (−31%) |

Since May 2025, Ukrainian arrivals have held more active jobs than there are
Ukrainians on income support (26,725 jobs against 26,451 recipients then;
32,595 against 27,057 in August 2026). Most work in hospitality, retail and
manufacturing ([CSO UA20](https://data.cso.ie/table/UA20)). Under the Scheme,
none of these years would count toward citizenship.

---

## 5. Against the language test: most already speak English well

Of residents who speak a language other than English or Irish at home,
**87.3% speak English well or very well** — **95.0%** of Indian citizens and
**92.6%** of African citizens ([CSO F5015, Census 2022](https://data.cso.ie/table/F5015)).

---

## 6. Against the s.6B change: migrant families are sustaining births

Births to Irish mothers **fell 13%** between 2022 and 2025, from 43,651 to
37,982. Births to mothers from outside the EU and UK **rose 50%**, from 6,688
to 10,030 — **18.5% of all births** in 2025 ([CSO VSAS80](https://data.cso.ie/table/VSAS80)).
Restricting these children's citizenship at birth reaches into nearly one in
five of the State's births.

---

## 7. The current system already works — and the public supports migration

- **Refusals are rare because applicants already qualify:** 187 refusals
  against more than 31,000 decisions in 2024 — **0.6%**
  ([PQ 891, 16 Sep 2026](https://www.oireachtas.ie/en/debates/question/2026-09-16/891/);
  [PQ 768, 12 Nov 2025](https://www.oireachtas.ie/en/debates/question/2025-11-12/768/)).
  The refusal rate gives no sign that the current criteria are failing.
- **Citizenship is not over-supplied:** the annual acquisition rate for non-EEA
  residents has held at about **4%** since 2021, and only about **30%** of
  non-EEA migrants who arrived since 2005 have become citizens
  ([ESRI Monitoring Report on Integration 2024](https://doi.org/10.26504/jr11)).
- **Public opinion.** Over **73%** of adults feel positive about immigration
  ([ESRI, Attitudes towards immigration and refugees, 2024](https://doi.org/10.26504/jr5)).
  The public overestimates the migrant population — an average guess of **28%**
  born abroad against official estimates of 19–22%
  ([ESRI, The role of misperceptions in attitudes to immigration, 2026](https://doi.org/10.26504/rs225)) —
  so public concern may be responding to a larger migrant population than
  actually exists.

---

## Figures the other side will cite — and their context

These come from the same sources, and a credible case should expect them:

| They will say | The context, from the same source |
|---|---|
| Migrants have a higher poverty rate (14.5% vs 11%) and more deprivation (23% vs 16%) | Driven by **lower wages** and the **private rental sector**: 36% of migrants spend over 30% of income on housing, against 9% of the Irish-born ([ESRI Monitoring Report 2024](https://doi.org/10.26504/jr11)). That is a case for the self-sufficiency test being unfair, not for it being needed. |
| 61% of immigrants received some welfare payment in 2024, against 56% of the Irish-born | The measure includes **universal Child Benefit**; migrants are younger and more likely to have children. On *unemployment* payments, Asian and Western EU immigrants rely *less* than the Irish-born ([ESRI RS229](https://doi.org/10.26504/rs229)). |
| The OECD found migrants' fiscal impact "neutral" on average | True across the 25 countries; **for Ireland specifically** the contribution was positive (+1.57% of GDP) ([ESRI 2026](https://doi.org/10.26504/sustat141)). |
| Attitudes are hardening | Positivity toward non-EU immigration fell 6 points between June and November 2023 — but from a high base; over 73% remain positive ([ESRI 2024](https://doi.org/10.26504/jr5)). |
| Ireland's naturalisation rate (2.94%) is above the EU median (1.41%) | The rate is high now because applications are being processed faster after years of backlog; it was just 0.85% in 2020 ([Eurostat](https://ec.europa.eu/eurostat/databrowser/view/migr_acqs/default/table?lang=en); [`NATURALISATION_BASELINE.md`](NATURALISATION_BASELINE.md)). |

**Figures not used here.** The claim that "54% of nurses trained abroad",
quoted in the Seanad, is not what the NMBI publishes; its own figures (76% of
new registrants, 35.8% of the Register) are used instead.

---

## Reproducing

```bash
.venv/bin/python scripts/42_fetch_contribution_data.py      # CSO LFS and Ukraine tables
.venv/bin/python scripts/43_build_contribution_evidence.py  # all 53 claims, each matched in its source
```

Source documents downloaded for this report (Medical Council, NMBI, EPRS,
DETE) are listed with their SHA-256 in
[`sources_register.csv`](data/processed/sources_register.csv). The companion
[`NATURALISATION_BASELINE.md`](NATURALISATION_BASELINE.md) sets out the neutral
before-and-after baseline for the same provisions.

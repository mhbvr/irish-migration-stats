# Research on migration, migrants and naturalisation in Ireland, 2023–2026

A systematic search of academic and research-institute publications with data
about Ireland, published from 1 January 2023 to 25 September 2026. Every
publication named here links to its source; all 296 are listed, with links, in
[`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) and [`catalogue.csv`](catalogue.csv).

**Headline.** Research output grew fast — 54 publications in 2023, 80 in 2024,
106 in 2025 — and it followed the politics: asylum and reception, health, and
anti-immigrant mobilisation dominate. **Naturalisation is almost entirely
absent.** Not one of the 296 publications has naturalisation in its title or
abstract, even though certificates of naturalisation rose 5.5-fold between 2020
and 2025 to a record 29,919 (see the main [`REPORT.md`](../REPORT.md)). The
employment permit system is similarly unstudied.

---

## 1. How the search was done

| | Stage 1: ESRI | Stage 2: broad search |
|---|---|---|
| Sources | ESRI publications listing — research-area route + 38 keyword routes | Semantic Scholar, Crossref, DOAJ, Europe PMC |
| Records screened | 419 candidates | 4,928 distinct works (after de-duplication across indexes) |
| Included | **39** | **257** new (18 more were already in stage 1) |
| Set aside as historical | — | 180 (pre-1960 subject matter; [appendix](BIBLIOGRAPHY.md#appendix-historical-studies)) |

A publication was included only if all three held:

1. **Topic** — migration, migrants, asylum or naturalisation in the social sense
   (not cell, animal or data migration; not "global citizenship");
2. **Irish data** — it carries evidence about Ireland or Northern Ireland, not
   merely a mention (pooled 20-country studies with no Irish-specific result
   were excluded);
3. **Date** — published on or after 1 January 2023.

Rules were applied to title and abstract, and for ESRI to the full text of 67
PDFs. Every borderline case was read and decided by hand — 465 decisions in all,
each recorded with its reason in [`manual_decisions.csv`](manual_decisions.csv).
Spot-checks of rule-based inclusions removed about 60 false positives (England &
Wales mortality studies, UK asylum law, a plant "naturalised" in Morocco, and a
geology paper on "Irish-type" ore deposits whose title spoke of the "Irish
diaspora").

**Verification.** Every DOI in the bibliography (448) was checked against the DOI
registry; one supplied by an index had never been registered and that entry links
to the journal's own copy instead. All 63 links in this review resolve. Some
*full-text* links on publisher sites (Wiley, Taylor & Francis, MDPI, Oxford,
SAGE) refuse automated checks with HTTP 403 but open normally in a browser.

**What this search does not cover.** OpenAlex, the largest open index, could not
be used: its anonymous daily allowance was exhausted, and the script is ready to
re-run with a key. Grey literature from NGOs and government departments was out
of scope by design. 2,288 stage-2 records had no abstract in any index; they were
screened on title, so work whose title mentions neither migration nor Ireland may
have been missed.

---

## 2. The shape of the field

**Output is rising steeply.** 54 → 80 → 106 publications a year (2023–2025);
56 more by late September 2026.

**By main theme** (one per publication, assigned from the title):

| Theme | Publications |
|---|---|
| Asylum, international protection & reception | 75 |
| Health, care & health workforce | 49 |
| Education, children & young people | 37 |
| Migrant communities, identity & family life | 25 |
| Attitudes, racism, discrimination & far right | 24 |
| Integration, housing, welfare & inclusion | 22 |
| Labour market & work | 18 |
| Emigration, diaspora & return | 12 |
| Migration policy & law | 9 |
| Language & multilingualism | 9 |
| Naturalisation & citizenship | 8 |
| Ukrainian temporary protection | 6 |

Cutting across themes: 26 publications concern Ukrainian arrivals, 22 COVID-19,
20 far-right mobilisation or riots, 19 the migration of doctors and nurses,
18 Polish migrants, and 15 Direct Provision / IPAS.

**Methods.** Qualitative work leads (73), then quantitative (65), policy / legal
/ document analysis (49) and mixed methods (46). Interviews and focus groups
are the commonest data source (71). **Only 24 studies use Census, microdata or
administrative data**, and only 3 use Department of Justice / IPO data — a
striking gap given how much administrative data exists
([see stage 1 of this project](../README.md)).

**Where.** 223 are about the State, 19 about Northern Ireland alone, 17 cover the
whole island, and 35 set Ireland alongside other countries.

**Where it is published.** The *Irish Journal of Sociology* (11) and ESRI's own
series lead, followed by the *European Journal of Public Health* (8),
*Irish Educational Studies* (5) and *Ethnic and Racial Studies* (5). Two-thirds
(202) have a free full text.

---

## 3. Stage 1 — ESRI

ESRI produced 39 qualifying publications, and its role is distinctive: it is
almost the only producer of **nationally representative quantitative evidence**
on migrants in Ireland, and, as Ireland's European Migration Network contact
point, of the annual statutory record of migration and asylum policy.

**Standing series.** The *Annual Report on Migration and Asylum*
([Murphy et al. 2025](https://doi.org/10.26504/sustat137)) records statistics, policy
and case law each year; the *Monitoring Report on Integration*
([McGinnity et al. 2025](https://doi.org/10.26504/jr11)) compares migrants with
the Irish-born across employment, education, social inclusion and active
citizenship — the one regular source that tracks citizenship acquisition as an
integration outcome. Nine EMN Migration Memos set Irish practice against other
Member States (e.g. [asylum-centre distribution](https://www.esri.ie/publications/how-do-emn-member-countries-distribute-asylum-centres-and-manage-relationships-with)).

**Key findings.**
- **Labour market.** From 2016 Census microdata, East European EEA migrants have
  low unemployment but few professional jobs; non-EEA migrants have higher
  unemployment *and* high professional shares; Black respondents fare worse
  regardless of origin or migration route ([Privalko et al. 2023](https://doi.org/10.1080/15562948.2023.2196664)).
  Over 2014–2024 immigrants had both higher employment *and* higher unemployment
  than the Irish-born, because more of them are in the labour force
  ([Alamir et al. 2026](https://doi.org/10.26504/rs229), using SILC).
- **Asylum.** 12,180 international protection applicants received first-time
  permission to work between the 2018 Supreme Court ruling and end-2022
  ([Polakowski & Cunniffe 2023](https://doi.org/10.26504/rs160)). The 2022 surge —
  13,651 applications, +186% on 2019 — had no single dominant nationality and
  was unusual because Ireland had long been insulated from EU-wide increases
  ([Potter & Murphy 2024](https://www.esri.ie/publications/what-caused-the-large-increase-in-international-protection-applications-in-ireland-in)).
  Refugees leaving reception face severe barriers to housing
  ([Murphy & Stapleton 2024](https://doi.org/10.26504/rs184)).
- **Irregular work.** No reliable estimate of irregular employment of non-EU
  nationals exists; inspections find it across sectors, most often in food
  service ([Stapleton et al. 2024](https://doi.org/10.26504/rs189)).
- **Attitudes.** A programme of work finds Irish attitudes still comparatively
  positive despite protests, hate crime and misinformation
  ([Laurence et al. 2024](https://doi.org/10.26504/jr5);
  [Timmons et al. 2026](https://doi.org/10.26504/rs225)). The local share of
  migrants has no overall link with attitudes, but a rapid *increase* is linked
  to more negative attitudes in disadvantaged communities, as is residential
  segregation ([Laurence et al. 2025](https://doi.org/10.1080/1369183X.2025.2487198)).
- **Children and young people.** Migrant-origin young people have high
  educational aspirations that are not always realised
  ([McGinnity et al. 2023](https://doi.org/10.4324/9781003279303-3)); differences
  in childcare use by migration background
  ([2023](https://doi.org/10.1016/j.rssm.2023.100773)); and their wellbeing
  during COVID-19 ([Smyth & Darmody 2024](https://doi.org/10.1080/00131911.2024.2341037)).
- **The island.** A North–South comparison of integration, attitudes and
  experience of the border ([McGinnity et al. 2023](https://doi.org/10.26504/rs158));
  student migration and "brain drain" from Northern Ireland
  ([Devlin & Hoyle 2026](https://doi.org/10.26504/rs234)).
- **Fiscal impact.** A 2026 literature review sets out what is and is not known
  about the fiscal effects of immigration in Ireland, stressing how much the
  answer depends on methodological choices ([Murphy et al. 2026](https://doi.org/10.26504/sustat141)).

---

## 4. Stage 2 — the wider literature, by theme

### Asylum, reception and Direct Provision (75)

The largest body of work, overwhelmingly qualitative and critical of the
reception system. Studies document care deficits in Direct Provision during
COVID-19 ([Daly & O'Riordan 2024](https://doi.org/10.1016/j.jmh.2024.100255)),
housing precarity on exiting IPAS ([O'Boyle 2024](https://doi.org/10.2478/admin-2024-0024)),
the experience of front-line workers in Ireland's privatised system compared with
Italy's non-profit one ([Peroni et al. 2025](https://doi.org/10.1177/00380385251373006)),
family reunification for young refugees ([Smith et al. 2023](https://doi.org/10.1111/ijsw.12604)),
and the slow implementation of the White Paper on ending Direct Provision
([Thornton & Ogunsanya 2024](https://doi.org/10.2139/ssrn.4688677)). Health research
adds screening and service data (e.g. Syrian refugees'
[health status](https://doi.org/10.22605/rrh8119)). Legal scholarship tracks
Ireland's 2024 opt-in to most of the EU Pact on Migration and Asylum — a
shift from *à la carte* participation ([Smyth 2025](https://doi.org/10.54648/cola2025068);
[Guild 2025](https://doi.org/10.1163/15718166-12340194)).

### Ukrainian arrivals (26 across themes)

Research on Ukrainian arrivals — 129,161 grants of temporary protection by August 2026 (stage 1 of this project) — is
health-heavy and quick-response: GP access ([O'Reilly et al. 2025](https://doi.org/10.1093/fampra/cmaf012)),
mental health of Ukrainian women (N = 656; [Mazhak & Sudyn 2025](https://doi.org/10.3390/socsci14120714)),
language use, and the divisive way the Temporary Protection Directive was
implemented relative to asylum seekers ([Zubareva & Minescu 2024](https://doi.org/10.3389/frsps.2024.1267365)).
ESRI assessed the Directive's application directly
([Stapleton & Dalton 2024](https://doi.org/10.26504/rs185)).

### Health and the health workforce (49)

Two distinct strands. **Migrant health:** tuberculosis epidemiology comparing
migrant and Irish-born cases ([Jackson et al. 2025](https://doi.org/10.1016/j.ijregi.2025.100763)),
longitudinal oral health of migrant children ([HagOmer & Hannigan 2025](https://doi.org/10.1111/ipd.70016)),
and repeated findings that **migrants are poorly recorded in Irish health data**
([Vishwakarma et al. 2025](https://doi.org/10.1186/s12939-025-02701-1);
[Cronin et al. 2024 scoping review](https://doi.org/10.1186/s12889-024-18920-0)).
**Health-workforce migration** — Ireland as both source and destination — is one
of the best-evidenced topics: two decades of dependence on migrant nurses
([Chima et al. 2026](https://doi.org/10.1016/j.hpopen.2026.100161)), a health
system in which a large share of workers are migrants
([Hanlon & Humphries 2024](https://doi.org/10.1093/eurpub/ckae144.267)),
GP emigration ([Hanlon et al. 2024](https://doi.org/10.1186/s12913-024-12117-2)),
and the outflow and return of trainee and specialist doctors
([Pierse et al. 2023](https://doi.org/10.1007/s11845-023-03288-8);
[Pierse et al. 2025](https://doi.org/10.1186/s12960-025-01025-z)).
Filipino and Indian migrant nurses are studied in their own right.

### Education, children and young people (37)

Mostly school-based: host-language achievement gaps by migration background from
*Growing Up in Ireland* data (N = 7,577; [Sprong & Skopek 2023](https://doi.org/10.1002/berj.3897)),
social inclusion of immigrant primary pupils by school type
([Jones et al. 2025](https://doi.org/10.3390/socsci14100612)), migrant parents'
involvement in schools ([Martin et al. 2025](https://doi.org/10.1080/00131881.2025.2529240)),
teachers' responses to linguistic diversity, and the arrival of Ukrainian pupils.
Higher education appears through international students and refugee access.

### Attitudes, racism and the far right (24; 20 on mobilisation)

A clear post-2022 growth area, tracking the protests and riots. Work analyses
far-right Twitter campaigning in the 2020 election
([Phelan & Kerrigan 2024](https://doi.org/10.55650/igj.2023.1479)), what
protesters at asylum accommodation actually demand
([Cannon & Murphy 2024](https://doi.org/10.1177/07916035241259252);
[Nightingale & Jay 2026](https://doi.org/10.1111/bjso.70045)),
"Ireland is full" discourse ([Dikwal-Bot & McIntyre 2025](https://doi.org/10.1177/13675494251396218)),
and the 2025 Ballymena riots in Northern Ireland
([Gutiérrez et al. 2026](https://doi.org/10.1177/13691481261481106)).

### Labour market and work (18)

Small and mostly qualitative: precarity produced by policies not aimed at migrants
at all, among Brazilians ([Machado 2024](https://doi.org/10.1111/imig.13323));
migrant fishers and "racial capitalism" ([Marschke & Vandergeest 2023](https://doi.org/10.1332/27523349y2023d000000003));
hospitality workers in Galway ([Ogunpaimo & Ebenade 2024](https://doi.org/10.1080/22243534.2024.2435382)).

### Communities, emigration and language (46 together)

Polish migrants — twenty years after EU accession — are the most-studied national
group (18), from family language loss in the "1.5 generation"
([Toth & Riordan 2024](https://doi.org/10.35903/teanga.v31i.7695)) to housing
([Szast 2026](https://doi.org/10.4467/25444972smpp.26.010.23756)); Brazilians in
Gort and their remittances are a second cluster
([De Farias 2025](https://doi.org/10.5216/sec.v28.81017)). **Emigration** research is
now mainly about health workers leaving (above) and about the State's diaspora
policy as soft power ([Coakley 2024](https://doi.org/10.1080/13562576.2024.2412579)).

### Naturalisation and citizenship (8)

Four articles — most of them in one 2025–26 special issue of the *Irish Journal
of Sociology* — re-read the **2004 Citizenship Referendum**, which ended
birthright citizenship, as a racial project
([White 2026](https://doi.org/10.1177/07916035261455230);
[Mullen 2026](https://doi.org/10.1177/07916035261429379);
[Lentin 2025](https://doi.org/10.1177/07916035251409730)). Others study
**citizenship by descent** sought by Britons after Brexit
([Scully 2024](https://doi.org/10.1111/pops.13026)); the law of acquiring and
losing nationality North and South ([Dickson & Hickey 2024](https://doi.org/10.1353/isia.2024.a932295));
Irish citizens' rights in the UK under the Common Travel Area
([O'Connor 2023](https://doi.org/10.1177/20319525231222165)); marriage-based
routes to residence ([Hanlon 2026](https://doi.org/10.1007/s10612-026-09884-1));
and migrant voting in the 2019 Dublin local elections
([Durkan & Kavanagh 2025](https://doi.org/10.22409/geographia2025.v27i58.a66947)).

---

## 5. Gaps

Set against the administrative data collected in stage 1 of this project, the
research record has four clear gaps.

1. **Naturalisation outcomes.** Not one publication studies who naturalises, why,
   how long it takes, or what citizenship changes for people — in a period when
   applications rose from 11,975 (2021) to 41,511 (2025) and processing time fell
   from 24 to 8 months. The nationality and route breakdowns obtained for this
   project (India now the largest group; minors 23% of certificates) have no
   counterpart in the research literature. The only regular quantitative
   treatment is the citizenship indicator in ESRI's integration monitoring.
2. **The employment permit system.** Five publications mention permits; none
   examines the system itself — the shift of permits from Critical Skills to
   General, the concentration in health care and on India, or what happens to
   permit holders. The labour-market literature is small and mostly qualitative.
3. **Administrative data are barely used.** Only 24 studies use Census,
   microdata or administrative records, and 3 use Department of Justice / IPO
   data. The best work (ESRI on SILC and Census microdata; health-workforce
   studies on registration records; Northern Ireland's census-linked mortality
   studies, [McKenna et al. 2025](https://doi.org/10.23889/ijpds.v10i3.3039))
   shows how much is possible.
4. **Northern Ireland and the island.** 19 NI-only studies and 17 all-island
   ones — thin, given the Common Travel Area and the post-Brexit border, and
   growing mainly in reaction to the 2024–25 riots.

---

## Files

| File | Contents |
|---|---|
| [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) | all 296 publications with links, by theme; historical appendix (180) |
| [`catalogue.csv`](catalogue.csv) | one row per publication: theme, evidence type, jurisdiction, data sources, DOI, full-text link, screening note |
| [`historical_appendix.csv`](historical_appendix.csv) | 180 historical studies set aside |
| [`manual_decisions.csv`](manual_decisions.csv) | 465 hand-made screening decisions, each with its reason |
| [`screening_flow.json`](screening_flow.json), [`analysis_tables.json`](analysis_tables.json) | counts behind this review |
| `esri/esri_screened.csv`, `broad/broad_screened.csv` | every candidate screened, with the rule outcome |

Themes, evidence types and jurisdictions are assigned by keyword rules and are
indicative; the screening note in `catalogue.csv` shows the basis for each entry.

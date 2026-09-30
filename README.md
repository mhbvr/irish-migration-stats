# Irish migration statistics, 2015–2026

Official statistics on immigration, employment permits, international protection
(asylum), visas and naturalisation in Ireland, collected from primary government
sources with full provenance.

Everything here is downloaded and parsed by the scripts in `scripts/`. No figure
is typed in by hand: each value in `data/processed/` is read out of a file whose
URL, retrieval time and SHA-256 are recorded in
[`data/processed/sources_register.csv`](data/processed/sources_register.csv).

**Collected 12 September 2026.** 140 source files, 85.7 MB, no failed downloads.

## Website

The data is published as a website on GitHub Pages at
<https://mhbvr.github.io/irish-migration-stats/>, built from this repository.
It has one tab per source (parliamentary questions, CSO, Department of Justice,
DETE, Eurostat, research articles). Each dataset has a page with a viewer that
loads the whole file in the browser, with search, a drop-down filter per column,
sorting, paging and a download of the filtered rows. The parliamentary question
index is split into subject groups (a `split` entry in the catalogue), and each
answer that contains statistics has its own page.

- `site/catalog.json`: the sources, and a title and description for each data file
- `site/assets/`: stylesheet, `viewer.js` (the data viewer) and `site.js`
- `scripts/50_build_site.py`: builds the site into `_site/`
- `.github/workflows/pages.yml`: rebuilds and publishes the site on every push to `main`

To add a new data file, add it to a source in `site/catalog.json`; files that
are not data (derived analysis tables, raw search dumps) go in its
`not_catalogued` list. The build fails if a CSV or JSON file in `data/processed/`
or `literature/` is in neither. To preview locally:

```bash
python3 scripts/50_build_site.py && python3 -m http.server -d _site 8000
```

## Sources

Only official publishers: the Central Statistics Office, the Department of
Enterprise, Tourism and Employment, the Department of Justice, Home Affairs and
Migration (directly and via data.gov.ie), the Houses of the Oireachtas, and
Eurostat (to which Ireland reports under statutory EU obligations). No press,
blog or social-media material is used. See [`docs/SOURCES.md`](docs/SOURCES.md).

## Reproducing

```bash
python3 -m venv .venv && .venv/bin/pip install openpyxl pdfplumber
for s in 01 03 04 04b 05 07 08 15; do .venv/bin/python scripts/${s}_*.py; done      # fetch
for s in 02 06 10 11 12 16 17 18 20 21 22 09 13 14 19; do .venv/bin/python scripts/${s}_*.py; done # parse
```

Downloads are cached, so re-running is cheap. `scripts/07` (parliamentary
questions) takes roughly 40 minutes on a first run and is resumable month by
month.

To bring the parliamentary data up to date later:

```bash
.venv/bin/python scripts/07_fetch_oireachtas_pqs.py --refresh 5   # re-fetch recent months
.venv/bin/python scripts/15_fetch_pq_attachments.py --since 2026-01-01
for s in 10 11 12 16 17 18 20 21 22 09 13 14; do .venv/bin/python scripts/${s}_*.py; done
```

| Script | What it does |
|---|---|
| `01`,`02` | Employment permit spreadsheets (DETE), 2015–2026 → tidy CSV |
| `03` | CSO PxStat migration / PPSN / international-protection tables via API |
| `04`,`04b` | International Protection monthly reports + DoJ statistics CSVs |
| `05`,`06` | Visa, residence, EU treaty rights, family reunification (data.gov.ie) |
| `07` | Harvests 10 years of migration-related parliamentary questions + answers |
| `15` | Scrapes PQ pages for attached spreadsheets (the only source of permit-type data) |
| `16`,`17`,`18` | Parses permit type × nationality / sector / occupation from those attachments |
| `19` | Compares permits with CSO non-EU immigration (timing / Ukraine / renewal caveats) |
| `20` | Indexes every PQ attachment (xlsx/docx/pdf) with a summary of its tables |
| `21`,`22` | Parses naturalisation by nationality/route, and protection/enforcement tables |
| `08` | Eurostat cross-check series for Ireland |
| `09` | Builds the consolidated `headline_series.csv` |
| `10`,`11`,`12` | Indexes PQs; extracts and curates the statistical tables in answers |
| `13` | Cross-source validation |
| `14` | Builds the sources register |

## Key outputs

| File | Contents |
|---|---|
| `data/processed/headline_series.csv` | 19 indicators, every row with source + URL |
| `data/processed/employment_permits_by_nationality.csv` | Permits by nationality, 2015–2026 |
| `data/processed/employment_permits_by_type_annual.csv` | Permits issued by permit type (CSEP/General/…), 2020–2024 |
| `data/processed/employment_permits_by_type_nationality.csv` | Permit type × nationality × year |
| `data/processed/employment_permits_by_type_sector.csv` | Permit type × economic sector × year |
| `data/processed/employment_permits_by_type_occupation.csv` | Critical Skills permits by SOC occupation, 2024 |
| `data/processed/justice_by_nationality_year.csv` | Visa / residence / FRU caseload by nationality |
| `data/processed/cso_*.csv` | CSO migration tables, flattened from JSON-stat |
| `data/processed/oireachtas_pq_index.csv` | 25,016 migration PQs, each with its URL |
| `data/processed/pq_curated_series.csv` | Annual series quoted from named PQs, with part-year flags |
| `data/processed/naturalisation_by_nationality.csv` | Certificates of naturalisation by nationality, 2016–2025 |
| `data/processed/naturalisation_by_route.csv` | Certificates by route (adult / s.15 / protection / minors) |
| `data/processed/protection_and_enforcement_from_pq_attachments.csv` | Protection decisions, grant rates, removals |
| `data/processed/pq_attachments_index.csv` | All 111 PQ attachments, summarised, with links |
| `data/processed/permits_vs_noneu_immigration.csv` | Permits vs CSO non-EU immigration, adjusted for timing and Ukraine |
| `data/processed/cross_source_validation.csv` | Independent sources compared |
| `data/processed/sources_register.csv` | Every download: URL, time, SHA-256 |

The findings are in [`REPORT.md`](REPORT.md).

## Evidence of migrants' contribution (against the 2026 changes)

[`MIGRATION_CONTRIBUTION_EVIDENCE.md`](MIGRATION_CONTRIBUTION_EVIDENCE.md) sets
out official statistics on what migrants contribute - employment, the health
workforce, public finances, Ukrainian arrivals at work, English ability, births -
organised against each change in the Bill, with the counter-arguments and their
context. All 53 figures are in `data/processed/contribution/contribution_evidence.csv`
with sources; built by `scripts/42_*` and `scripts/43_*`.

## Baseline for the 2026 naturalisation law changes

[`NATURALISATION_BASELINE.md`](NATURALISATION_BASELINE.md) sets out which data
can serve as a pre-change baseline for the Irish Nationality and Citizenship
(Amendment) Bill 2026, provision by provision, with the current values and the
gaps. Built by `scripts/40_fetch_naturalisation_baseline.py` and
`scripts/41_build_naturalisation_baseline.py`; the indicators are in
`data/processed/naturalisation_baseline/`.

## Literature on migration in Ireland (2023–2026)

[`literature/LITERATURE_REVIEW.md`](literature/LITERATURE_REVIEW.md) reviews 296
academic and research-institute publications with data about Ireland, found in
two stages: ESRI first (39), then Semantic Scholar, Crossref, DOAJ and Europe PMC
(257 more). Every publication is listed with a link in
[`literature/BIBLIOGRAPHY.md`](literature/BIBLIOGRAPHY.md); every hand-made
screening decision is in `literature/manual_decisions.csv` with its reason.

```bash
.venv/bin/python scripts/30_fetch_esri_publications.py      # stage 1 candidates
.venv/bin/python scripts/31_screen_esri.py                  # screen (downloads PDFs)
.venv/bin/python scripts/34_fetch_s2_europepmc.py           # stage 2 indexes
.venv/bin/python scripts/35_fetch_crossref_doaj.py
.venv/bin/python scripts/36_enrich_abstracts.py             # fill missing abstracts
.venv/bin/python literature/record_esri_decisions.py
.venv/bin/python literature/record_broad_decisions.py
.venv/bin/python scripts/33_screen_broad.py
.venv/bin/python scripts/37_build_literature_catalogue.py   # catalogue + DOI check
.venv/bin/python scripts/38_write_bibliography.py
```

OpenAlex (`scripts/32_fetch_openalex.py`) is wired in but was not used: its
anonymous daily budget ran out. Set `OPENALEX_API_KEY` and re-run it, then the
screening steps, to add it.

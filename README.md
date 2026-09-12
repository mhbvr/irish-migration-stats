# Irish migration statistics, 2015–2026

Official statistics on immigration, employment permits, international protection
(asylum), visas and naturalisation in Ireland, collected from primary government
sources with full provenance.

Everything here is downloaded and parsed by the scripts in `scripts/`. No figure
is typed in by hand: each value in `data/processed/` is read out of a file whose
URL, retrieval time and SHA-256 are recorded in
[`data/processed/sources_register.csv`](data/processed/sources_register.csv).

**Collected 12 September 2026.** 140 source files, 85.7 MB, no failed downloads.

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
for s in 02 06 10 11 12 16 17 18 09 13 14; do .venv/bin/python scripts/${s}_*.py; done # parse
```

Downloads are cached, so re-running is cheap. `scripts/07` (parliamentary
questions) takes roughly 40 minutes on a first run and is resumable month by
month.

| Script | What it does |
|---|---|
| `01`,`02` | Employment permit spreadsheets (DETE), 2015–2026 → tidy CSV |
| `03` | CSO PxStat migration / PPSN / international-protection tables via API |
| `04`,`04b` | International Protection monthly reports + DoJ statistics CSVs |
| `05`,`06` | Visa, residence, EU treaty rights, family reunification (data.gov.ie) |
| `07` | Harvests 10 years of migration-related parliamentary questions + answers |
| `15` | Scrapes PQ pages for attached spreadsheets (the only source of permit-type data) |
| `16`,`17`,`18` | Parses permit type × nationality / sector / occupation from those attachments |
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
| `data/processed/oireachtas_pq_index.csv` | 24,628 migration PQs, each with its URL |
| `data/processed/pq_curated_series.csv` | Annual series quoted from named PQs |
| `data/processed/cross_source_validation.csv` | Independent sources compared |
| `data/processed/sources_register.csv` | Every download: URL, time, SHA-256 |

The findings are in [`REPORT.md`](REPORT.md).

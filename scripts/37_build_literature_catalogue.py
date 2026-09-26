"""Literature: merge both stages into one catalogue and derive the analysis tables.

Inputs : literature/esri/esri_screened.csv   (stage 1, ESRI)
         literature/broad/broad_screened.csv (stage 2, broad search)
Outputs: literature/catalogue.csv            every included publication, both stages
         literature/historical_appendix.csv  historical studies (kept, not analysed)
         literature/analysis_tables.json     counts used by LITERATURE_REVIEW.md
         literature/screening_flow.json      records in / out at each step

Classification is rule-based on title + abstract (+ ESRI full text where held)
and every label can be traced to the keyword that triggered it.
"""
import csv, json, re, pathlib, collections

ROOT = pathlib.Path(__file__).resolve().parent.parent
L = ROOT / "literature"

THEMES = collections.OrderedDict([
    ("Naturalisation & citizenship", r"naturali[sz]|citizenship|nationality law|citizenship referendum|Stamp 4|long-term residen"),
    ("Asylum, international protection & reception", r"asylum|international protection|refugee|Direct Provision|IPAS|reception|displaced|deportation|forced migration|sanctuary"),
    ("Ukrainian temporary protection", r"Ukrain|temporary protection"),
    ("Labour market, work & permits", r"labour market|labor market|employment|work permit|employment permit|migrant workers?|occupation|wages?|earnings|skills|workforce|irregular employment|services sector|entrepreneur|sex workers?"),
    ("Health, care & health workforce", r"health|mental|maternity|perinatal|nurs(?:e|es|ing)|doctors?|clinic|patients?|GP|psychiatr|HIV|care\b|dermatolog|tuberculosis|\bTB\b"),
    ("Education, children & young people", r"school|pupils?|students?|teachers?|educat|children|child|young people|youth|adolescen|higher education|universit|Growing Up in Ireland"),
    ("Attitudes, racism, discrimination & far right", r"attitudes?|racism|racis|discriminat|far[- ]right|populis|anti-immigra\w*|opponents of immigration|nationalis\w*|protest|riot|hostil|prejudice|whiteness|immigration scuppers|media|Irish Times|Twitter"),
    ("Integration, housing, welfare & inclusion", r"integration|inclusion|housing|homeless|poverty|welfare|social transfer|deprivation|belonging|civic"),
    ("Emigration, diaspora & return", r"emigra|diaspora|return migration|returnees?|brain drain|Irish abroad|Irish-trained"),
    ("Language & multilingualism", r"language|multilingual|bilingual|linguistic|English classes|Polish-English"),
    ("Migration policy, law & governance", r"policy|polic(?:ies)|law|legal|legislat|EU Pact|Pact on Migration|opt-in|regulation|family reunification|strategy|governance|court|Brexit|border|search and rescue|marriage"),
    ("Migrant communities, identity & family life", r"famil|identit|communit|organi[sz]ations|belonging|transnational|religio|Muslim|Polish|Croatian|Brazilian|Lithuanian|Chinese|Nigerian|sport|footballers|politicians|remitt"),
    ("Population, flows & statistics", r"population projection|census|flows?|estimates?|demograph|statistic|microdata"),
])
EVIDENCE = [
    ("Quantitative", r"regression|survey|dataset|data from|microdata|administrative data|census|longitudinal|panel|cohort|N\s*=|\bn\s*=|estimat|statistic|quantitative|Labour Force Survey|EU-SILC|SILC|Growing Up in Ireland|questionnaire"),
    ("Qualitative", r"interview|focus group|ethnograph|qualitative|narratives?|thematic analysis|case stud|autoethnograph|phenomenolog|action research|fieldwork"),
    ("Policy / legal / document analysis", r"policy|legal|law|legislat|court|judg|Act\b|referendum|document|media analysis|manifesto|memo"),
    ("Review / overview", r"review|overview|scoping|literature|state of the art|synthesis"),
]
DATA_SOURCES = collections.OrderedDict([
    ("Census (CSO/NISRA)", r"\bcensus"), ("Growing Up in Ireland", r"Growing Up in Ireland|\bGUI\b"),
    ("Labour Force Survey", r"Labour Force Survey|\bLFS\b"), ("EU-SILC / SILC", r"\bSILC\b|EU-SILC"),
    ("European Social Survey", r"European Social Survey|\bESS\b"), ("Healthy Ireland", r"Healthy Ireland"),
    ("PISA / TIMSS", r"\bPISA\b|\bTIMSS\b"), ("Administrative / register data", r"administrative data|register data|PPSN|Revenue|records of|probate"),
    ("IPO / Department of Justice data", r"International Protection Office|\bIPO\b|Department of Justice|Immigration Service"),
    ("Eurostat", r"Eurostat"), ("Interviews / focus groups", r"interview|focus group"),
    ("Original survey", r"online survey|we surveyed|survey of \d|\d+ (?:respondents|participants|clinicians)"),
])


def labels(text, table, multi=True):
    out = [(k, re.search(p, text, re.I)) for k, p in table.items()] if isinstance(table, dict) else \
          [(k, re.search(p, text, re.I)) for k, p in table]
    hits = [k for k, m in out if m]
    return hits if multi else (hits[0] if hits else "")


def evidence(text):
    ks = [k for k, p in EVIDENCE if re.search(p, text, re.I)]
    if "Quantitative" in ks and "Qualitative" in ks:
        return "Mixed methods"
    for k in ("Quantitative", "Qualitative", "Policy / legal / document analysis", "Review / overview"):
        if k in ks:
            return k
    return "Other / unclear"


rows, hist = [], []
flow = {}

# ---------------- stage 1: ESRI
esri = list(csv.DictReader(open(L / "esri/esri_screened.csv", encoding="utf-8")))
flow["stage1_candidates"] = len(esri)
flow["stage1_status"] = dict(collections.Counter(r["status"] for r in esri))
esri_keys = set()
for r in esri:
    if r["status"] not in ("include", "historical"):
        continue
    text = f"{r['title']} {r['abstract']}"
    rec = {"stage": "1 - ESRI", "date": r["date"], "year": r["date"][:4], "title": r["title"],
           "authors": r["authors"], "publication_type": r["series"], "venue": f"ESRI ({r['series']})",
           "publisher": "ESRI", "doi": r["doi"], "url": r["url"], "full_text": r["pdf_url"],
           "jurisdiction": r.get("jurisdiction", ""), "abstract": r["abstract"],
           "screening_note": r["reasons"]}
    (hist if r["status"] == "historical" else rows).append(rec)
    esri_keys.add(re.sub(r"[^a-z0-9]", "", r["title"].lower())[:90])
    if r["doi"]:
        esri_keys.add(r["doi"].lower())

# ---------------- stage 2: broad
broad = list(csv.DictReader(open(L / "broad/broad_screened.csv", encoding="utf-8")))
flow["stage2_records_merged"] = len(broad)
flow["stage2_status"] = dict(collections.Counter(r["status"] for r in broad))
flow["stage2_by_index_found"] = dict(collections.Counter(
    idx for r in broad for idx in {f.split(":")[0] for f in r["found_by"].split("; ")}))
dup_esri = 0
for r in broad:
    if r["status"] not in ("include", "historical"):
        continue
    tkey = re.sub(r"[^a-z0-9]", "", r["title"].lower())[:90]
    if r["also_in_esri_stage"] == "True" or tkey in esri_keys or (r["doi"] and r["doi"].lower() in esri_keys):
        dup_esri += 1
        continue
    rec = {"stage": "2 - broad", "date": r["date"], "year": (r["date"] or "")[:4], "title": r["title"],
           "authors": r["authors"], "publication_type": r["type"], "venue": r["source"], "publisher": r["publisher"],
           "doi": r["doi"], "url": r["url"], "full_text": r["oa_url"], "jurisdiction": r["jurisdiction"],
           "abstract": r["abstract"], "screening_note": r["reasons"],
           "institutions": r["institutions"], "found_in": r["found_by"]}
    (hist if r["status"] == "historical" else rows).append(rec)
flow["stage2_included_also_in_esri"] = dup_esri

# ---------------- de-duplicate by DOI (an ESRI Research Bulletin often carries the DOI of the
# article it summarises); keep the non-bulletin record and note the bulletin on it
by_doi = {}
for rec in list(rows):
    d = (rec.get("doi") or "").lower().replace("https://doi.org/", "")
    if not d:
        continue
    if d in by_doi:
        a, b = by_doi[d], rec
        drop, keep = (a, b) if "Bulletin" in a["publication_type"] else (b, a)
        keep["screening_note"] = (keep["screening_note"] + f"; also summarised as: {drop['publication_type']} ({drop['url']})").strip("; ")
        rows.remove(drop)
        by_doi[d] = keep
        flow.setdefault("duplicates_removed_by_doi", []).append(drop["title"][:80])
    else:
        by_doi[d] = rec

# ---------------- DOI validation against the DOI registry (cached). An index can
# carry a DOI that was never registered; such records fall back to the landing
# page recorded by the index that found them, and are flagged.
import urllib.request, urllib.parse
dc_path = L / "doi_check.json"
dc = json.loads(dc_path.read_text()) if dc_path.exists() else {}
landing = {}
for f in ("s2_raw.json", "crossref_raw.json", "doaj_raw.json", "europepmc_raw.json", "openalex_raw.json"):
    fp = L / "broad" / f
    if fp.exists():
        for w in json.loads(fp.read_text())["works"]:
            if w.get("landing_page"):
                landing[re.sub(r"[^a-z0-9]", "", (w.get("title") or "").lower())[:90]] = w["landing_page"]
for rec in rows + hist:
    d = (rec.get("doi") or "").lower().replace("https://doi.org/", "")
    if not d:
        rec["doi_registered"] = ""
        continue
    if d not in dc:
        try:
            with urllib.request.urlopen("https://doi.org/api/handles/" + urllib.parse.quote(d, safe="/()"), timeout=30) as r:
                dc[d] = json.loads(r.read()).get("responseCode") == 1
        except Exception:                                     # noqa: BLE001
            dc[d] = False
    rec["doi_registered"] = dc[d]
    if not dc[d]:
        alt = landing.get(re.sub(r"[^a-z0-9]", "", rec["title"].lower())[:90])
        rec["screening_note"] = (rec["screening_note"] + f"; DOI {d} is not registered - linking the index landing page").strip("; ")
        rec["url"] = alt or rec["url"]
        rec["doi"] = ""
dc_path.write_text(json.dumps(dc, indent=0))
flow["dois_not_registered"] = [d for d, ok in dc.items() if not ok]

# ---------------- classification
for rec in rows + hist:
    t = f"{rec['title']} {rec['abstract']}"
    rec["themes"] = "; ".join(labels(t, THEMES)) or "Other"
    rec["primary_theme"] = labels(rec["title"], THEMES, multi=False) or labels(t, THEMES, multi=False) or "Other"
    rec["evidence_type"] = evidence(t)
    rec["data_sources"] = "; ".join(labels(t, DATA_SOURCES))
    j = rec.get("jurisdiction") or ""
    # everything here already has Irish data; flag work that also covers other countries
    if re.search(r"\b(EU countries|EEA|cross-national|comparative|Member (?:States|Countries)|"
                 r"European countries|Spain|Finland|Germany|Hungary|UK and Ireland|Netherlands)\b", t):
        j = (j + "; cross-national").strip("; ")
    rec["jurisdiction"] = j or "Ireland (State)"

cols = ["stage", "year", "date", "title", "authors", "primary_theme", "themes", "evidence_type",
        "data_sources", "jurisdiction", "publication_type", "venue", "publisher", "doi", "doi_registered", "url",
        "full_text", "institutions", "found_in", "screening_note", "abstract"]
rows.sort(key=lambda r: (r["date"] or ""), reverse=True)
for fname, data in (("catalogue.csv", rows), ("historical_appendix.csv", hist)):
    with open(L / fname, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader(); w.writerows(data)

# ---------------- analysis tables
C = collections.Counter
tables = {
    "n_included": len(rows), "n_historical": len(hist),
    "by_stage": dict(C(r["stage"] for r in rows)),
    "by_year": dict(sorted(C(r["year"] for r in rows).items())),
    "by_primary_theme": dict(C(r["primary_theme"] for r in rows).most_common()),
    "by_theme_any": dict(C(t for r in rows for t in r["themes"].split("; ")).most_common()),
    "by_evidence": dict(C(r["evidence_type"] for r in rows).most_common()),
    "by_jurisdiction": dict(C(r["jurisdiction"] for r in rows).most_common()),
    "by_type": dict(C(r["publication_type"] for r in rows).most_common(12)),
    "by_data_source": dict(C(d for r in rows for d in r["data_sources"].split("; ") if d).most_common()),
    "top_venues": dict(C(r["venue"] for r in rows if r["venue"]).most_common(15)),
    "theme_by_year": {th: dict(sorted(C(r["year"] for r in rows if th in r["themes"]).items()))
                      for th in THEMES},
    "open_full_text": sum(1 for r in rows if r["full_text"]),
    "without_abstract": sum(1 for r in rows if not r["abstract"]),
}
(L / "analysis_tables.json").write_text(json.dumps(tables, indent=1, ensure_ascii=False))
(L / "screening_flow.json").write_text(json.dumps(flow, indent=1))
print(f"catalogue.csv: {len(rows)} publications  |  historical_appendix.csv: {len(hist)}")
for k in ("by_stage", "by_year", "by_primary_theme", "by_evidence", "by_jurisdiction", "by_data_source"):
    print(f"\n{k}: {tables[k]}")
print(f"\nflow: {json.dumps(flow)}")

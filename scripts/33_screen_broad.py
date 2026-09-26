"""Literature stage 2: screen the broad-search results (OpenAlex, Semantic
Scholar, Europe PMC - scripts 32 and 34).

Same rules as stage 1 (litscreen.assess), plus:
  - document types: keep articles, books, chapters, reports, preprints, theses
    and reviews; drop editorials, errata, letters, paratext, peer-review
    records and bare datasets;
  - de-duplication against the ESRI stage by DOI and by normalised title, so
    stage 2 reports only what is new beyond ESRI;
  - OpenAlex's own subject classification is recorded; items it files under
    Life or Physical Sciences need a strong migration term to survive.
Manual decisions in literature/manual_decisions.csv (keyed by DOI or OpenAlex
id) override the rules, and the reason is carried into the output.
"""
import csv, json, re, sys, pathlib, collections
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from litscreen import assess

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "literature"
KEEP_TYPES = {"article", "book", "book-chapter", "report", "preprint", "dissertation", "review"}

def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())[:90]


def norm_doi(d):
    return (d or "").lower().replace("https://doi.org/", "").strip()


# Merge every index that has been fetched (OpenAlex may be missing if its daily
# budget ran out). Duplicates are matched on DOI, then on normalised title; the
# record with an abstract wins and the indexes that found it are all listed.
INDEXES = [("OpenAlex", "openalex_raw.json"), ("SemanticScholar", "s2_raw.json"),
           ("EuropePMC", "europepmc_raw.json"), ("Crossref", "crossref_raw.json"),
           ("DOAJ", "doaj_raw.json")]
works, by_key, present = [], {}, []
for idx, fname in INDEXES:
    f = D / "broad" / fname
    if not f.exists():
        print(f"(index {idx} not fetched yet - {fname} missing)")
        continue
    present.append(idx)
    for w in json.loads(f.read_text())["works"]:
        w["found_by"] = [f"{idx}:{q}" for q in w["found_by"]]
        keys = [k for k in (norm_doi(w["doi"]), norm_title(w["title"])) if k]
        hit = next((by_key[k] for k in keys if k in by_key), None)
        if hit is None:
            works.append(w)
            for k in keys:
                by_key[k] = w
        else:
            hit["found_by"] += w["found_by"]
            for fld in ("abstract", "abstract_source", "doi", "oa_url", "source", "publisher", "institutions",
                        "author_countries", "field", "domain"):
                if not hit.get(fld) and w.get(fld):
                    hit[fld] = w[fld]
print(f"merged {len(works):,} distinct works from: {', '.join(present)}")

# Abstracts recovered by script 36 (Semantic Scholar / Europe PMC, looked up by DOI)
ac = D / "broad" / "abstract_cache.json"
cache = json.loads(ac.read_text()) if ac.exists() else {}
filled = 0
for w in works:
    if not w.get("abstract"):
        hit = cache.get(norm_doi(w.get("doi")), {})
        if hit.get("abstract"):
            w["abstract"], w["abstract_source"] = hit["abstract"], hit["source"]; filled += 1
    elif not w.get("abstract_source"):
        w["abstract_source"] = w["found_by"][0].split(":")[0]
print(f"abstracts filled from cache: {filled}; still without abstract: {sum(1 for w in works if not w.get('abstract'))}")


esri_doi, esri_title = set(), set()
ef = D / "esri" / "esri_screened.csv"
if ef.exists():
    for r in csv.DictReader(open(ef, encoding="utf-8")):
        if r["doi"]:
            esri_doi.add(norm_doi(r["doi"]))
        esri_title.add(norm_title(r["title"]))

manual = {}
mf = D / "manual_decisions.csv"
if mf.exists():
    for r in csv.DictReader(open(mf, encoding="utf-8")):
        manual[r["url"]] = r

rows = []
for w in works:
    doi = norm_doi(w["doi"])
    key = f"https://doi.org/{doi}" if doi else w["openalex_id"]
    base = {"date": w["date"], "year": w["year"], "title": w["title"], "type": w["type"],
            "source": w["source"] or "", "publisher": w["publisher"] or "",
            "authors": "; ".join(w["authors"][:12]) + (" et al." if len(w["authors"]) > 12 else ""),
            "institutions": "; ".join(w["institutions"][:8]),
            "author_countries": ", ".join(w["author_countries"]),
            "openalex_field": w["field"] or "", "openalex_domain": w["domain"] or "",
            "doi": doi, "url": key, "oa_url": w["oa_url"] or "", "is_oa": w["is_oa"],
            "cited_by": w["cited_by"], "language": w["language"] or "",
            "found_by": "; ".join(w["found_by"]), "abstract": w["abstract"],
            "abstract_source": w.get("abstract_source", "")}
    also_esri = doi in esri_doi or norm_title(w["title"]) in esri_title
    if (w["date"] or "") < "2023-01-01":
        rows.append({**base, "status": "exclude", "reasons": "published before 2023"}); continue
    if w["type"] not in KEEP_TYPES:
        rows.append({**base, "status": "exclude", "reasons": f"document type '{w['type']}'"}); continue

    a = assess(w["title"], w["abstract"])
    status, why = a["status"], [a["reasons"]] if a["reasons"] else []
    if w["domain"] in ("Life Sciences", "Physical Sciences") and status != "exclude":
        strong_core = re.search(r"\b(migrants?|immigra\w+|emigra\w+|asylum|refugees?|naturali[sz]\w+|"
                                r"citizenship|international protection|diaspora)\b",
                                f"{w['title']} {w['abstract']}", re.I)
        if not strong_core:
            status = "exclude"
            why.append(f"OpenAlex files it under {w['domain']} and no core migration term")
    if also_esri:
        why.append("also found in stage 1 (ESRI)")
    if key in manual:
        status = manual[key]["decision"]
        why.append(f"MANUAL: {manual[key]['reason']}")
    rows.append({**base, **a, "status": status, "reasons": "; ".join(x for x in why if x),
                 "also_in_esri_stage": also_esri})

cols = ["status", "date", "title", "type", "source", "publisher", "authors", "reasons", "strong_terms", "strong_mentions", "migration_terms",
        "ireland_terms", "empirical_signals", "jurisdiction", "era", "also_in_esri_stage",
        "abstract_source", "institutions", "author_countries", "openalex_field", "openalex_domain", "doi", "url",
        "oa_url", "is_oa", "cited_by", "language", "found_by", "abstract"]
rows.sort(key=lambda r: (r["status"] != "include", r["status"] != "review", r["date"] or ""), reverse=False)
with open(D / "broad" / "broad_screened.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    wr.writeheader(); wr.writerows(rows)

print(f"wrote literature/broad/broad_screened.csv ({len(rows):,} works)")
for s, n in collections.Counter(r["status"] for r in rows).most_common():
    print(f"  {n:6,}  {s}")
inc = [r for r in rows if r["status"] == "include"]
print(f"\nincluded and NOT already in ESRI stage: {sum(1 for r in inc if not r.get('also_in_esri_stage')):,}")
print("top exclusion reasons:")
for why, n in collections.Counter(r["reasons"].split(";")[0] for r in rows if r["status"] == "exclude").most_common(8):
    print(f"  {n:6,}  {why}")

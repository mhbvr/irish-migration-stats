"""Literature stage 2 (continued): Semantic Scholar and Europe PMC.

Used alongside OpenAlex (script 32), and needed because anonymous OpenAlex use
has a small daily budget. Both APIs are open and return abstracts.
  - Semantic Scholar bulk search  https://api.semanticscholar.org/api-docs/graph
    (boolean syntax: "+" AND, "|" OR; year filter "2023-")
  - Europe PMC REST               https://europepmc.org/RestfulWebService
    (biomedical + health/social-care literature; strong on migrant health)
Records are written in the same shape as OpenAlex records so that script 33
screens all three indexes with identical rules.
"""
import json, re, sys, time, pathlib, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "literature" / "broad"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {"User-Agent": "irish-migration-stats literature search (research use)"}


def get_json(url, tries=6):
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            wait = 10 * 2 ** k if e.code == 429 else 5 * (k + 1)
            print(f"    HTTP {e.code}; retry in {wait}s", flush=True)
            time.sleep(wait)
        except Exception as e:                                  # noqa: BLE001
            print(f"    {type(e).__name__}; retry", flush=True)
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"gave up: {url}")


def record(**kw):
    base = dict(openalex_id="", doi=None, title="", year=None, date="", type="", language="",
                source="", publisher="", authors=[], author_countries=[], institutions=[],
                abstract="", topic="", field="", domain="", is_oa=None, oa_url="",
                landing_page="", cited_by=None, found_by=[])
    base.update(kw)
    return base


# ------------------------------------------------------------ Semantic Scholar
S2 = "https://api.semanticscholar.org/graph/v1/paper/search/bulk"
S2_TERMS = ("(migrant | migrants | migration | immigrant | immigrants | immigration | emigrant | "
            "emigration | asylum | refugee | refugees | naturalisation | naturalization | citizenship | "
            "diaspora | \"international protection\" | \"temporary protection\" | \"ethnic minority\")")
S2_QUERIES = {
    "S2_terms_and_Ireland": f"{S2_TERMS} + (Ireland | Irish)",
    # "IPAS" and "Stamp 4" are deliberately absent: Semantic Scholar stems IPAS to
    # "IPA" (tens of thousands of unrelated hits) and splits "Stamp 4".
    "S2_irish_specific": "(\"direct provision\" | \"International Protection Accommodation\" | "
                         "\"Irish Refugee Protection Programme\" | \"Critical Skills Employment Permit\")",
}
S2_TYPES = {"JournalArticle": "article", "Review": "review", "Book": "book", "BookSection": "book-chapter",
            "Conference": "article", "Dataset": "dataset", "Editorial": "editorial", "LettersAndComments": "letter",
            "News": "other", "Study": "article", "CaseReport": "article", "ClinicalTrial": "article"}
s2 = {}
for qname, q in S2_QUERIES.items():
    token, n = None, 0
    while True:
        params = {"query": q, "year": "2023-", "fields": "title,year,publicationDate,abstract,externalIds,"
                  "venue,publicationVenue,publicationTypes,authors,openAccessPdf,citationCount,fieldsOfStudy,url"}
        if token:
            params["token"] = token
        js = get_json(S2 + "?" + urllib.parse.urlencode(params))
        for p in js.get("data", []):
            key = p["paperId"]
            if key in s2:
                s2[key]["found_by"].append(qname); continue
            types = p.get("publicationTypes") or []
            doi = (p.get("externalIds") or {}).get("DOI")
            s2[key] = record(
                openalex_id=f"S2:{key}", doi=f"https://doi.org/{doi}" if doi else None,
                title=p.get("title") or "", year=p.get("year"),
                date=p.get("publicationDate") or (f"{p['year']}-01-01" if p.get("year") else ""),
                type=S2_TYPES.get(types[0], "article") if types else "article",
                source=p.get("venue") or ((p.get("publicationVenue") or {}).get("name") or ""),
                authors=[a.get("name") for a in (p.get("authors") or [])],
                abstract=p.get("abstract") or "",
                field=", ".join(p.get("fieldsOfStudy") or []),
                is_oa=bool(p.get("openAccessPdf")), oa_url=(p.get("openAccessPdf") or {}).get("url") or "",
                landing_page=p.get("url"), cited_by=p.get("citationCount"), found_by=[qname])
            n += 1
        token = js.get("token")
        if not token:
            break
        time.sleep(3)
    print(f"{qname}: {js.get('total', 0):,} hits ({n:,} new)", flush=True)
    time.sleep(3)
(OUT / "s2_raw.json").write_text(json.dumps({"meta": {"api": S2, "queries": S2_QUERIES,
    "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, "works": list(s2.values())},
    ensure_ascii=False, indent=1))
print(f"wrote literature/broad/s2_raw.json ({len(s2):,})\n")

# ------------------------------------------------------------ Europe PMC
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
EPMC_Q = ('(TITLE_ABS:(migrant OR migrants OR immigrant OR immigrants OR immigration OR emigration '
          'OR asylum OR refugee OR refugees OR "international protection" OR "temporary protection" '
          'OR "ethnic minority" OR "ethnic minorities" OR "direct provision" OR "non-Irish" OR "Ukrainian")) '
          'AND (TITLE_ABS:(Ireland OR Irish)) AND (FIRST_PDATE:[2023-01-01 TO 2026-12-31])')
ep, cursor = {}, "*"
while True:
    js = get_json(EPMC + "?" + urllib.parse.urlencode({"query": EPMC_Q, "format": "json",
                  "resultType": "core", "pageSize": 1000, "cursorMark": cursor}))
    for r in js.get("resultList", {}).get("result", []):
        key = r.get("id")
        if key in ep:
            continue
        doi = r.get("doi")
        ptypes = [t.lower() for t in (r.get("pubTypeList") or {}).get("pubType", [])]
        typ = ("preprint" if r.get("source") == "PPR" else "review" if "review" in " ".join(ptypes)
               else "editorial" if "editorial" in ptypes else "letter" if "letter" in ptypes else "article")
        ft = [u.get("url") for u in (r.get("fullTextUrlList") or {}).get("fullTextUrl", [])
              if u.get("availabilityCode") in ("OA", "F")]
        ep[key] = record(
            openalex_id=f"EPMC:{r.get('source')}:{key}", doi=f"https://doi.org/{doi}" if doi else None,
            title=re.sub(r"<[^>]+>", "", r.get("title") or ""), year=int(r["pubYear"]) if r.get("pubYear") else None,
            date=r.get("firstPublicationDate") or "", type=typ,
            source=(r.get("journalInfo") or {}).get("journal", {}).get("title") or r.get("bookOrReportDetails", {}).get("publisher", ""),
            authors=[a.get("fullName") for a in (r.get("authorList") or {}).get("author", []) if a.get("fullName")],
            abstract=re.sub(r"<[^>]+>", " ", r.get("abstractText") or ""),
            institutions=sorted({(a.get("authorAffiliationDetailsList") or {}).get("authorAffiliation", [{}])[0].get("affiliation", "")
                                 for a in (r.get("authorList") or {}).get("author", [])} - {""})[:10],
            is_oa=r.get("isOpenAccess") == "Y", oa_url=ft[0] if ft else "",
            landing_page=f"https://europepmc.org/article/{r.get('source')}/{key}",
            cited_by=r.get("citedByCount"), found_by=["EPMC_terms_and_Ireland"])
    nxt = js.get("nextCursorMark")
    if not nxt or nxt == cursor or not js.get("resultList", {}).get("result"):
        break
    cursor = nxt
    time.sleep(1)
print(f"EPMC_terms_and_Ireland: {js.get('hitCount', 0):,} hits ({len(ep):,} kept)")
(OUT / "europepmc_raw.json").write_text(json.dumps({"meta": {"api": EPMC, "query": EPMC_Q,
    "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, "works": list(ep.values())},
    ensure_ascii=False, indent=1))
print(f"wrote literature/broad/europepmc_raw.json ({len(ep):,})")

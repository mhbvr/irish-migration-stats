"""Literature stage 2 (continued): Crossref and DOAJ, plus abstract enrichment.

- Crossref (https://api.crossref.org) is the DOI registry: it covers almost all
  journal articles, books, chapters and many reports, but matches loosely and
  ranks by relevance, so we run focused queries and keep the top 300 of each.
- DOAJ (https://doaj.org/api/docs) indexes open-access journals with abstracts;
  its field-restricted search is precise, so every hit is kept.
- Many Crossref records carry no abstract. For those we look the DOI up in the
  Semantic Scholar batch API and take its abstract, recording where it came from.
Records use the same shape as scripts 32/34 so script 33 screens everything alike.
No e-mail address or API key is sent.
"""
import json, re, sys, time, pathlib, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "literature" / "broad"
HEADERS = {"User-Agent": "irish-migration-stats literature search (research use)"}
SINCE = "2023-01-01"


def http(url, data=None, tries=6):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=data, headers={**HEADERS,
                  **({"Content-Type": "application/json"} if data else {})})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if 400 <= e.code < 500 and e.code != 429:      # a bad request will never succeed
                raise RuntimeError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")
            wait = 10 * 2 ** k if e.code == 429 else 5 * (k + 1)
            print(f"    HTTP {e.code}; retry in {wait}s", flush=True); time.sleep(wait)
        except Exception as e:                                    # noqa: BLE001
            print(f"    {type(e).__name__}; retry", flush=True); time.sleep(5 * (k + 1))
    raise RuntimeError(f"gave up: {url}")


def record(**kw):
    base = dict(openalex_id="", doi=None, title="", year=None, date="", type="", language="",
                source="", publisher="", authors=[], author_countries=[], institutions=[],
                abstract="", abstract_source="", topic="", field="", domain="", is_oa=None,
                oa_url="", landing_page="", cited_by=None, found_by=[])
    base.update(kw)
    return base


def strip(x):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", x or "")).strip()


MONTHS = {m: i for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july",
                                       "august", "september", "october", "november", "december"], 1)}


def month_num(m):
    """DOAJ months arrive as '12', 12 or 'December'."""
    s = str(m or "").strip().lower()
    if s.isdigit():
        return int(s)
    return next((i for name, i in MONTHS.items() if s and name.startswith(s[:3])), 1)


# ------------------------------------------------------------------ Crossref
CR = "https://api.crossref.org/works"
CR_QUERIES = [
    "migrants Ireland", "immigration Ireland", "immigrants Irish", "refugees Ireland",
    "asylum seekers Ireland", "international protection applicants Ireland",
    "naturalisation citizenship Ireland", "direct provision Ireland",
    "Ukrainian refugees Ireland temporary protection", "emigration Ireland diaspora",
    "ethnic minorities Ireland", "migrant workers Ireland employment permits",
    "international students Ireland", "integration of migrants Ireland",
    "racism discrimination migrants Ireland", "migrant health Ireland",
]
if (OUT / "crossref_raw.json").exists() and "--refetch-crossref" not in sys.argv:
    print("crossref_raw.json exists - skipping Crossref (pass --refetch-crossref to redo)")
    CR_QUERIES = []
CR_TYPES = ("journal-article,book-chapter,book,monograph,edited-book,report,posted-content,"
            "dissertation,proceedings-article,reference-entry")
TYPE_MAP = {"journal-article": "article", "posted-content": "preprint", "monograph": "book",
            "edited-book": "book", "proceedings-article": "article", "reference-entry": "book-chapter"}
cr = {}
for q in CR_QUERIES:
    params = {"query.bibliographic": q, "filter": f"from-pub-date:{SINCE}," +
              ",".join(f"type:{t}" for t in CR_TYPES.split(",")), "rows": 300,
              "select": "DOI,title,abstract,type,issued,published,container-title,publisher,author,URL"}
    js = http(CR + "?" + urllib.parse.urlencode(params))
    new = 0
    for it in js["message"]["items"]:
        doi = it["DOI"].lower()
        if doi in cr:
            cr[doi]["found_by"].append(f"q:{q}"); continue
        dp = (it.get("issued") or it.get("published") or {}).get("date-parts", [[None]])[0]
        date = "-".join(f"{int(x):02d}" if i else str(x) for i, x in enumerate(dp) if x) if dp and dp[0] else ""
        cr[doi] = record(openalex_id=f"CR:{doi}", doi=f"https://doi.org/{doi}",
                         title=strip((it.get("title") or [""])[0]), year=dp[0] if dp else None,
                         date=date + ("-01-01" if len(date) == 4 else "-01" if len(date) == 7 else ""),
                         type=TYPE_MAP.get(it.get("type"), it.get("type")),                          source=strip((it.get("container-title") or [""])[0]), publisher=it.get("publisher") or "",
                         authors=[" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in it.get("author", [])],
                         abstract=strip(it.get("abstract")), abstract_source="Crossref" if it.get("abstract") else "",
                         landing_page=it.get("URL"), found_by=[f"q:{q}"])
        new += 1
    print(f"Crossref '{q}': {js['message']['total-results']:,} matches, top 300 taken ({new} new)", flush=True)
    time.sleep(1)

# --- enrich missing abstracts from Semantic Scholar, by DOI (batch of <=500)
missing = [d for d, r in cr.items() if not r["abstract"]] if cr else []
print(f"\n{len(missing)} Crossref records lack an abstract; looking them up in Semantic Scholar", flush=True)
got = 0
for i in range(0, len(missing), 400):
    chunk = missing[i:i + 400]
    res = http("https://api.semanticscholar.org/graph/v1/paper/batch?fields=abstract,openAccessPdf",
               data=json.dumps({"ids": [f"DOI:{d}" for d in chunk]}).encode())
    for d, p in zip(chunk, res):
        if p and p.get("abstract"):
            cr[d]["abstract"] = p["abstract"]; cr[d]["abstract_source"] = "Semantic Scholar (by DOI)"; got += 1
        if p and p.get("openAccessPdf"):
            cr[d]["oa_url"] = p["openAccessPdf"].get("url") or ""
    time.sleep(3)
print(f"  abstracts recovered: {got}", flush=True)
for r in cr.values():
    r["found_by"] = ["Crossref:" + "|".join(r["found_by"])]
if cr:
    (OUT / "crossref_raw.json").write_text(json.dumps({"meta": {"api": CR, "queries": CR_QUERIES, "rows_per_query": 300,
    "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, "works": list(cr.values())}, ensure_ascii=False, indent=1))
    print(f"wrote literature/broad/crossref_raw.json ({len(cr):,})\n")

# ------------------------------------------------------------------ DOAJ
DOAJ = "https://doaj.org/api/search/articles/"
DOAJ_Q = ("bibjson.abstract:(migrant OR migrants OR immigrant OR immigrants OR immigration OR emigration OR "
          "refugee OR refugees OR asylum OR naturalisation OR naturalization OR citizenship OR diaspora OR "
          "\"international protection\" OR \"direct provision\" OR \"ethnic minority\") AND "
          "(bibjson.abstract:(Ireland OR Irish) OR bibjson.title:(Ireland OR Irish)) AND bibjson.year:[2023 TO 2026]")
dj, page = {}, 1
while True:
    js = http(DOAJ + urllib.parse.quote(DOAJ_Q) + f"?pageSize=100&page={page}")
    for r in js.get("results", []):
        b = r["bibjson"]
        doi = next((i["id"].lower() for i in b.get("identifier", []) if i.get("type") == "doi"), None)
        link = next((l.get("url") for l in b.get("link", []) if l.get("url")), "")
        y = b.get("year")
        dj[r["id"]] = record(openalex_id=f"DOAJ:{r['id']}", doi=f"https://doi.org/{doi}" if doi else None,
                             title=strip(b.get("title")), year=int(y) if y else None,
                             date=f"{y}-{month_num(b.get('month')):02d}-01" if y else "", type="article",
                             source=(b.get("journal") or {}).get("title", ""), publisher=(b.get("journal") or {}).get("publisher", ""),
                             authors=[a.get("name") for a in b.get("author", []) if a.get("name")],
                             institutions=sorted({a.get("affiliation") for a in b.get("author", []) if a.get("affiliation")})[:10],
                             abstract=strip(b.get("abstract")), abstract_source="DOAJ", is_oa=True, oa_url=link,
                             landing_page=link, found_by=["DOAJ:terms_and_Ireland"])
    if page * 100 >= js.get("total", 0):
        break
    page += 1; time.sleep(1)
print(f"DOAJ: {js.get('total', 0)} hits")
(OUT / "doaj_raw.json").write_text(json.dumps({"meta": {"api": DOAJ, "query": DOAJ_Q,
    "retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}, "works": list(dj.values())}, ensure_ascii=False, indent=1))
print(f"wrote literature/broad/doaj_raw.json ({len(dj):,})")

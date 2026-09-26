"""Literature stage 2: broad search via OpenAlex (https://openalex.org), an open
index of scholarly works (journal articles, books and chapters, reports,
preprints, theses) built from Crossref, PubMed, institutional repositories etc.

API docs: https://docs.openalex.org  -  endpoint https://api.openalex.org/works
No API key or e-mail address is sent.

Queries (all restricted to works published on or after 2023-01-01):
  Q1  migration / naturalisation / asylum vocabulary  AND  (Ireland OR Irish)
      in title or abstract - the main net;
  Q2  the same vocabulary, by any author with an Irish institutional
      affiliation, whether or not "Ireland" appears in the abstract;
  Q3  Ireland-specific institutional terms that imply Ireland on their own
      ("direct provision", "IPAS", "Stamp 4", ...).
Nothing is filtered here beyond the query: every hit is stored with the query
that found it, and relevance is decided transparently in script 33.

Anonymous OpenAlex use now has a small daily credit budget (HTTP 429 with
"dailyRemainingUsd": 0 once spent; it resets at midnight UTC). Each query is
therefore checkpointed to literature/broad/openalex_<query>.json as soon as it
completes, and a re-run skips finished queries. On a 429 that reports an
exhausted daily budget the script stops cleanly instead of retrying for hours.
Set OPENALEX_API_KEY to use a (free) personal key with its own budget.
"""
import json, os, sys, time, pathlib, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "literature" / "broad"
OUT.mkdir(parents=True, exist_ok=True)
API = "https://api.openalex.org/works"
SINCE = "2023-01-01"

MIG = ("(migrant OR migrants OR migration OR immigrant OR immigrants OR immigration OR "
       "emigrant OR emigrants OR emigration OR naturalisation OR naturalization OR "
       "citizenship OR asylum OR refugee OR refugees OR \"international protection\" OR "
       "\"temporary protection\" OR diaspora OR \"third-country nationals\" OR "
       "\"employment permit\" OR \"work permit\" OR undocumented OR \"ethnic minority\" OR "
       "\"ethnic minorities\")")
QUERIES = {
    "Q1_terms_and_Ireland": f"title_and_abstract.search:{MIG} AND (Ireland OR Irish)",
    "Q2_terms_irish_affiliation": f"title_and_abstract.search:{MIG},institutions.country_code:IE",
    "Q3_irish_specific_terms": "title_and_abstract.search:(\"direct provision\" OR IPAS OR "
                               "\"International Protection Accommodation\" OR \"Stamp 4\" OR "
                               "\"Irish Refugee Protection Programme\" OR \"Critical Skills Employment Permit\")",
}
SELECT = ("id,doi,title,publication_year,publication_date,type,language,primary_location,"
          "open_access,authorships,abstract_inverted_index,primary_topic,cited_by_count,"
          "best_oa_location")
HEADERS = {"User-Agent": "irish-migration-stats literature search (research use)"}


class BudgetExhausted(Exception):
    pass


def call(params, tries=6):
    if os.environ.get("OPENALEX_API_KEY"):
        params = dict(params, api_key=os.environ["OPENALEX_API_KEY"])
    url = API + "?" + urllib.parse.urlencode(params)
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                body = e.read().decode("utf-8", "replace")
                if '"dailyRemainingUsd":0' in body.replace(" ", ""):
                    raise BudgetExhausted(body[:300])
            wait = 5 * 2 ** k if e.code == 429 else 5 * (k + 1)
            print(f"    HTTP {e.code}; retry in {wait}s", flush=True)
            time.sleep(wait)
        except Exception as e:                                  # noqa: BLE001
            print(f"    {type(e).__name__}; retry", flush=True)
            time.sleep(5 * (k + 1))
    raise RuntimeError(f"gave up on {url}")


def parse(w):
    loc = w.get("primary_location") or {}
    src = loc.get("source") or {}
    pt = w.get("primary_topic") or {}
    oa = w.get("best_oa_location") or {}
    return {
        "openalex_id": w["id"], "doi": w.get("doi"), "title": w.get("title"),
        "year": w.get("publication_year"), "date": w.get("publication_date"),
        "type": w.get("type"), "language": w.get("language"),
        "source": src.get("display_name"), "publisher": src.get("host_organization_name"),
        "authors": [a["author"]["display_name"] for a in w.get("authorships", [])],
        "author_countries": sorted({c for a in w.get("authorships", []) for c in (a.get("countries") or [])}),
        "institutions": sorted({i["display_name"] for a in w.get("authorships", [])
                                for i in (a.get("institutions") or [])}),
        "abstract": abstract(w.get("abstract_inverted_index")),
        "topic": pt.get("display_name"), "field": (pt.get("field") or {}).get("display_name"),
        "domain": (pt.get("domain") or {}).get("display_name"),
        "is_oa": (w.get("open_access") or {}).get("is_oa"),
        "oa_url": oa.get("pdf_url") or oa.get("landing_page_url") or (w.get("open_access") or {}).get("oa_url"),
        "landing_page": loc.get("landing_page_url"),
        "cited_by": w.get("cited_by_count"),
    }


def abstract(inv):
    if not inv:
        return ""
    pos = [(i, w) for w, idx in inv.items() for i in idx]
    return " ".join(w for _, w in sorted(pos))


works = {}
done = {}
for qname in QUERIES:
    ck = OUT / f"openalex_{qname}.json"
    if ck.exists():
        done[qname] = json.loads(ck.read_text())
        for w in done[qname]:
            rec = works.setdefault(w["openalex_id"], {**w, "found_by": []})
            if qname not in rec["found_by"]:
                rec["found_by"].append(qname)
        print(f"{qname}: {len(done[qname]):,} works loaded from checkpoint", flush=True)

for qname, filt in QUERIES.items():
    if qname in done:
        continue
    cursor, n, this_q = "*", 0, []
    try:
        while cursor:
            js = call({"filter": f"from_publication_date:{SINCE},{filt}", "per-page": 200,
                       "cursor": cursor, "select": SELECT})
            for w in js["results"]:
                this_q.append(parse(w))
            cursor = js["meta"].get("next_cursor")
            time.sleep(1.5)
    except BudgetExhausted as e:
        print(f"{qname}: OpenAlex daily budget exhausted - stopping; re-run after midnight UTC "
              f"or set OPENALEX_API_KEY.\n  {e}", flush=True)
        break
    (OUT / f"openalex_{qname}.json").write_text(json.dumps(this_q, ensure_ascii=False))
    for rec in this_q:
        if rec["openalex_id"] in works:
            works[rec["openalex_id"]]["found_by"].append(qname)
        else:
            works[rec["openalex_id"]] = {**rec, "found_by": [qname]}
            n += 1
    print(f"{qname}: {js['meta']['count']:,} hits ({n:,} new) - checkpointed", flush=True)


meta = {"retrieved": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "api": API,
        "since": SINCE, "queries": QUERIES}
(OUT / "openalex_raw.json").write_text(json.dumps({"meta": meta, "works": list(works.values())},
                                                  ensure_ascii=False, indent=1))
print(f"\nwrote literature/broad/openalex_raw.json ({len(works):,} distinct works)")

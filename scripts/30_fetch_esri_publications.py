"""Literature stage 1: ESRI (Economic and Social Research Institute) publications
on migration, migrants and naturalisation in Ireland, published 2023 onwards.

Discovery uses the ESRI "browse" listing (https://www.esri.ie/publications/browse),
which robots.txt permits; /search is disallowed so it is not used. Two routes:
  1. everything tagged with the research area "Migration, Integration and
     Demography" (term 67) since 2023-01-01;
  2. keyword searches across ALL research areas since 2023-01-01, because
     migration work is often filed under labour markets, health, education or
     social inclusion instead.
The keyword filter matches whole (stemmed) words, not prefixes, so every
variant is listed explicitly. It also over-matches (e.g. "naturalisation"
pulls in "natural"), so everything here is a CANDIDATE list; relevance is
decided in the screening step (script 31).

For every candidate the publication page is fetched for date, series, authors,
research areas, abstract, DOI and PDF link, and the PDF itself is downloaded
with provenance (URL, time, SHA-256) via fetchlib.
"""
import html as htmllib, json, re, sys, time, pathlib, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch, get

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "literature" / "esri"
OUT.mkdir(parents=True, exist_ok=True)
BASE = "https://www.esri.ie"
SINCE = "2023-01-01"

KEYWORDS = [
    "migrant", "migration", "immigrant", "immigration", "emigrant", "emigration",
    "naturalisation", "citizenship", "asylum", "international protection",
    "refugee", "Ukraine", "Ukrainian", "nationality", "non-Irish", "ethnic",
    "ethnicity", "integration", "third country", "employment permit",
    "work permit", "visa", "diaspora", "direct provision", "racism",
    "discrimination", "foreign", "born abroad", "temporary protection",
    "family reunification", "undocumented", "irregular", "labour migration",
    "student migration", "return migration", "trafficking", "deportation",
]


def clean(s):
    return re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def listing(params):
    """Yield (url, listing-metadata) over every page of a browse query."""
    page = 0
    while True:
        q = dict(params, **{"published_after[date]": SINCE, "page": page})
        h = get(f"{BASE}/publications/browse?" + urllib.parse.urlencode(q, doseq=True))
        items = re.findall(r'<article class="teaser node--type-publication">(.*?)</footer>', h, re.S)
        if not items:
            return
        for it in items:
            m = re.search(r'<a\s+href="(/publications/[^"]+)"', it)
            if not m:
                continue
            yield BASE + m.group(1), {
                "date": (re.search(r'datetime="([^"]+)"', it) or [None, ""])[1][:10],
                "series": clean((re.search(r'teaser__esri-series">(.*?)</div>', it, re.S) or [None, ""])[1]),
            }
        page += 1
        time.sleep(1)


# ---------------------------------------------------------------- discovery
cands = {}
routes = [("research_area:67", {"research_areas[]": "67"})] + \
         [(f"keyword:{k}", {"keywords": k}) for k in KEYWORDS]
for label, params in routes:
    n = 0
    for url, meta in listing(params):
        c = cands.setdefault(url, {"url": url, **meta, "found_by": []})
        c["found_by"].append(label)
        n += 1
    print(f"  {n:4} results  {label}", flush=True)
print(f"\n{len(cands)} distinct candidate publications since {SINCE}")

# ---------------------------------------------------------------- details
for i, (url, c) in enumerate(sorted(cands.items()), 1):
    try:
        h = get(url)
    except Exception as exc:                                   # noqa: BLE001
        c["error"] = str(exc)
        continue
    c["title"] = clean((re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S) or [None, ""])[1])
    c["date"] = c.get("date") or (re.search(r'datetime="([^"]+)"', h) or [None, ""])[1][:10]
    c["abstract"] = clean((re.search(r'class="publication__abstract field">(.*?)</div>\s*<div class="publication__building', h, re.S) or [None, ""])[1])
    c["authors"] = [clean(a) for a in re.findall(r'<a\s+href="/people/[^"]+"[^>]*>(.*?)</a>',
                    (re.search(r'field--name-field-authors(.*?)</div>\s*</div>\s*</div>', h, re.S) or [None, ""])[1])]
    c["research_areas"] = [clean(a) for a in re.findall(r'<a\s+href="/taxonomy/term/\d+"[^>]*>(.*?)</a>',
                           (re.search(r'field--name-field-research-areas(.*?)</div>\s*</div>', h, re.S) or [None, ""])[1])]
    c["pdf_urls"] = sorted(set(re.findall(r'href="(https?://[^"]+\.pdf)"',
                           (re.search(r'class="publication__files field">(.*?)</div>', h, re.S) or [None, ""])[1])))
    dois = re.findall(r'(?:doi\.org/|DOI:?\s*)(10\.\d{4,9}/[^\s"<>]+)', h)
    c["doi"] = dois[0].rstrip(".,;)") if dois else ""
    c["external_links"] = sorted({u for u in re.findall(r'href="(https?://[^"]+)"', h)
                                  if not u.startswith(BASE) and any(k in u for k in
                                  ("doi.org", "sciencedirect", "springer", "tandfonline", "wiley",
                                   "sagepub", "oup.com", "cambridge.org", "emerald", "jstor",
                                   "mdpi", "ssrn", "emn", "ec.europa.eu/home-affairs"))})
    if i % 25 == 0:
        print(f"  details {i}/{len(cands)}", flush=True)
    time.sleep(1)

(OUT / "esri_candidates.json").write_text(json.dumps(list(cands.values()), indent=1, ensure_ascii=False))
print(f"wrote literature/esri/esri_candidates.json ({len(cands)} records)")

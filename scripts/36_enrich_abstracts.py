"""Literature stage 2: fill in missing abstracts before screening.

Screening on title alone throws away relevant work (a paper titled
"Migrants' neighbourhood experiences" never says "Ireland" in its title). So
for every broad-search record that has a DOI but no abstract, we ask:
  1. Semantic Scholar batch API (500 DOIs per call), then
  2. Europe PMC (by DOI) for anything still missing.
Results are cached in literature/broad/abstract_cache.json (DOI -> abstract +
source), so the step is resumable and never re-asks for a DOI it has tried.
Script 33 reads the cache and records which source each abstract came from.
"""
import json, sys, time, pathlib, urllib.error, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
B = ROOT / "literature" / "broad"
CACHE = B / "abstract_cache.json"
HEADERS = {"User-Agent": "irish-migration-stats literature search (research use)"}
cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}

need = set()
for f in ("s2_raw.json", "europepmc_raw.json", "crossref_raw.json", "doaj_raw.json", "openalex_raw.json"):
    p = B / f
    if not p.exists():
        continue
    for w in json.loads(p.read_text())["works"]:
        doi = (w.get("doi") or "").lower().replace("https://doi.org/", "")
        if doi and not w.get("abstract") and doi not in cache:
            need.add(doi)
need = sorted(need)
print(f"{len(need)} DOIs without an abstract and not yet tried", flush=True)


def post(url, body, tries=8):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                         headers={**HEADERS, "Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code != 429 and 400 <= e.code < 500:
                raise
            wait = min(15 * 2 ** k, 300)
            print(f"    HTTP {e.code}; waiting {wait}s", flush=True); time.sleep(wait)
        except Exception as e:                                        # noqa: BLE001
            print(f"    {type(e).__name__}; retry", flush=True); time.sleep(10)
    return None


# 1. Semantic Scholar batch
for i in range(0, len(need), 500):
    chunk = need[i:i + 500]
    res = post("https://api.semanticscholar.org/graph/v1/paper/batch?fields=abstract", {"ids": [f"DOI:{d}" for d in chunk]})
    if res is None:
        print("  Semantic Scholar unavailable for this batch; will retry on next run", flush=True)
        continue
    for d, p in zip(chunk, res):
        cache[d] = {"abstract": (p or {}).get("abstract") or "", "source": "Semantic Scholar (by DOI)"}
    CACHE.write_text(json.dumps(cache))
    print(f"  S2 batch {i // 500 + 1}: {sum(1 for d in chunk if cache[d]['abstract'])}/{len(chunk)} found", flush=True)
    time.sleep(5)

# 2. Europe PMC for what is still empty
still = [d for d in need if d in cache and not cache[d]["abstract"]]
print(f"{len(still)} still without abstract; trying Europe PMC", flush=True)
found = 0
for d in still:
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": f'DOI:"{d}"', "format": "json", "resultType": "core"})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=60) as r:
            res = json.loads(r.read()).get("resultList", {}).get("result", [])
    except Exception:                                                  # noqa: BLE001
        continue
    if res and res[0].get("abstractText"):
        cache[d] = {"abstract": res[0]["abstractText"], "source": "Europe PMC (by DOI)"}; found += 1
    time.sleep(0.3)
CACHE.write_text(json.dumps(cache))
print(f"  Europe PMC: {found} found")
have = sum(1 for d in need if cache.get(d, {}).get("abstract"))
print(f"\nabstracts now available for {have}/{len(need)} of the DOIs that lacked one")

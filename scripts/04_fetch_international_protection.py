"""Stage 1: international protection (asylum) statistics.

Primary source: Department of Justice, Home Affairs and Migration collection
"International Protection in Numbers", which hosts the IPO's monthly
International Protection Summary Reports as PDFs on assets.gov.ie.
Collection: https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/collections/international-protection-in-numbers/

Note: the IPO's own site (ipo.gov.ie) was serving an expired TLS certificate on
2026-09-12, so we take the gov.ie-hosted copies of the same documents instead.
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch, get

COLLECTION = ("https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/"
              "collections/international-protection-in-numbers/")

html = get(COLLECTION)
links = re.findall(r'<a [^>]*href="(https://assets\.gov\.ie/[^"]+\.pdf)"[^>]*>([^<]+)</a>', html)
seen, n = set(), 0
print(f"{len(links)} PDF links found in the collection")
for url, title in links:
    if url in seen:
        continue
    seen.add(url)
    name = url.rsplit("/", 1)[-1]
    if fetch(url, f"international_protection/{name}", source_page=COLLECTION,
             note=title.strip()):
        n += 1
print(f"downloaded/cached {n} reports")

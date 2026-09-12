"""Stage 1: employment permits.

Source: Department of Enterprise, Tourism and Employment (DETE) employment
permit statistics hub, which links one publication page per year, each holding
the official XLSX tables (by nationality / sector / county / company).
Hub: https://enterprise.gov.ie/en/what-we-do/workplace-and-skills/employment-permits/statistics/
"""
import re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch, get

BASE = "https://enterprise.gov.ie"
HUB = BASE + "/en/what-we-do/workplace-and-skills/employment-permits/statistics/"

html = get(HUB)
year_pages = sorted(set(re.findall(
    r'href="(/en/[Pp]ublications/[Ee]mployment-[Pp]ermit-[Ss]tatis\w*-(\d{4})\.html)"', html)),
    key=lambda t: t[1])
print(f"Found {len(year_pages)} annual publication pages on the DETE hub")

for rel, year in year_pages:
    if int(year) < 2015:          # keep a 10-year window (+ context year)
        continue
    page_url = BASE + rel
    print(f"[{year}] {page_url}")
    try:
        page = get(page_url)
    except Exception as exc:                          # noqa: BLE001
        print(f"  page FAIL {exc}")
        continue
    files = sorted(set(re.findall(r'href="([^"]+\.(?:xlsx|xls|csv))"', page, re.I)))
    if not files:
        print("  (no data files linked)")
    for rel_file in files:
        url = rel_file if rel_file.startswith("http") else BASE + rel_file
        name = url.rsplit("/", 1)[-1]
        fetch(url, f"employment_permits/{year}/{name}", source_page=page_url,
              note=f"DETE employment permit statistics {year}")

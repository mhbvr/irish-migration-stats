"""Stage 1: the two international-protection CSVs published directly on the
Department of Justice statistics page (monthly applications, and top-5
nationalities). These stop in March 2021 but are the Department's own
machine-readable release for the earlier part of the window.

Page: https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/publications/departmental-data-and-statistical-reports/
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch

PAGE = ("https://www.gov.ie/en/department-of-justice-home-affairs-and-migration/"
        "publications/departmental-data-and-statistical-reports/")
FILES = {
    "applications-for-international-protection.csv":
        "Total monthly applications for a declaration of International Protection",
    "applications-for-international-protection-top-5-nationalities.csv":
        "Top 5 nationalities applying for International Protection, monthly YTD",
}
for name, note in FILES.items():
    fetch(f"https://assets.gov.ie/static/documents/{name}",
          f"doj_stats/{name}", source_page=PAGE, note=note, force=True)

# The CSO's full dataset catalogue, used to locate the migration tables.
fetch("https://ws.cso.ie/public/api.restful/PxStat.Data.Cube_API.ReadCollection",
      "cso_collection.json", source_page="https://data.cso.ie/",
      note="CSO PxStat full dataset catalogue (13,008 tables) - used to locate migration tables", force=True)

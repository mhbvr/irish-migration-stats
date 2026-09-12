"""Stage 1: immigration operational data from data.gov.ie (Ireland's open data portal).

The Department of Justice, Home Affairs and Migration publishes its visa,
residence-permission, EU-treaty-rights and family-reunification caseload data
here as CSV. Portal org page:
  https://data.gov.ie/organization/department-of-justice
CKAN API: https://data.gov.ie/api/3/action/package_search?q=organization:department-of-justice
"""
import json, sys, time, pathlib, urllib.parse
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch, get

CKAN = "https://data.gov.ie/api/3/action/"
ORG = "department-of-justice"

url = CKAN + "package_search?" + urllib.parse.urlencode({"q": f"organization:{ORG}", "rows": 200})
pkgs = json.loads(get(url))["result"]["results"]
print(f"{len(pkgs)} datasets published by {ORG}")

KEEP = ("visa", "residence", "treaty", "reunification", "temporary-protection",
        "permission", "ukraine")
index = []
for p in pkgs:
    if not any(k in p["name"] for k in KEEP):
        print(f"  skip  {p['name']}")
        continue
    page = f"https://data.gov.ie/dataset/{p['name']}"
    for res in p["resources"]:
        if res.get("format", "").upper() != "CSV":
            continue
        name = res["url"].rsplit("/", 1)[-1]
        got = fetch(res["url"], f"datagov_justice/{name}", source_page=page,
                    note=f"{p['title']} (data.gov.ie, publisher: {p['organization']['title']})")
        index.append({"dataset": p["name"], "title": p["title"], "portal_page": page,
                      "resource_url": res["url"], "file": name,
                      "last_modified": res.get("last_modified") or res.get("created"),
                      "downloaded": bool(got)})
    time.sleep(1)

out = pathlib.Path(__file__).resolve().parent.parent / "data" / "processed" / "datagov_justice_index.json"
out.write_text(json.dumps(index, indent=2))
print(f"\nindexed {len(index)} CSV resources -> {out.name}")

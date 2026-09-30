"""Build the data website published on GitHub Pages.

Reads site/catalog.json, which groups the data files by source, and writes a
plain HTML site to _site/: a home page listing the sources, one tab per source
listing its datasets, and one page per dataset showing the data itself. Rows,
years and table contents are read from the files, so the site never drifts from
the repository.

    python scripts/50_build_site.py            # writes _site/
    python scripts/50_build_site.py --strict   # also fail on uncatalogued files

.github/workflows/pages.yml runs this on every push to main and deploys _site/.
"""
import argparse
import csv
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "site"
OUT = ROOT / "_site"

csv.field_size_limit(sys.maxsize)

# Files larger than this are downloaded from GitHub instead of being copied into the site.
COPY_LIMIT = 20 * 1024 * 1024
# Rows shown on a dataset page; the full file is one click away.
SHOW_ROWS = 500
# Folders whose data files must all be in the catalogue or its not_catalogued list (--strict).
CATALOGUED_DIRS = ["data/processed", "literature"]
YEAR_COL = re.compile(r"year|^time$|^quarter$|^date$|^week$|^day$|pq_date", re.I)
YEAR_VAL = re.compile(r"(?<!\d)(19[5-9]\d|20[0-4]\d)(?!\d)")


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def human_size(n):
    for unit in ("B", "KB", "MB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} GB"


def read_table(path):
    """Return (header, first SHOW_ROWS rows, total rows, (first year, last year) or None)."""
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        data = [d for d in data if isinstance(d, dict)] if isinstance(data, list) else []
        header = []
        for d in data:
            header += [k for k in d if k not in header]
        rows = [[str(d.get(k, "")) for k in header] for d in data]
    else:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            rows = list(reader)
    years = set()
    for i, h in enumerate(header):
        if YEAR_COL.search(h.strip()):
            for r in rows:
                if i < len(r):
                    years.update(int(y) for y in YEAR_VAL.findall(r[i]))
    span = (min(years), max(years)) if years else None
    return header, rows[:SHOW_ROWS], len(rows), span


def years_text(span):
    if not span:
        return ""
    return str(span[0]) if span[0] == span[1] else f"{span[0]}–{span[1]}"


class Site:
    def __init__(self, catalog):
        self.cat = catalog
        self.repo = os.environ.get("GITHUB_REPOSITORY") or catalog["repo"]
        self.branch = catalog.get("branch", "main")

    def gh_blob(self, path):
        return f"https://github.com/{self.repo}/blob/{self.branch}/{path}"

    def gh_raw(self, path):
        return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{path}"

    def page(self, rel_out, title, body, current=""):
        up = "../" * rel_out.count("/")
        tabs = [("index.html", "Home", "")] + [
            (f"sources/{s['id']}.html", s["title"], s["id"]) for s in self.cat["sources"]
        ]
        nav = "".join(
            f'<a href="{up}{href}"{" aria-current=page" if key == current else ""}>{esc(label)}</a>'
            for href, label, key in tabs
        )
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(self.cat['tagline'])}">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="brand" href="{up}index.html">{esc(self.cat['title'])}</a>
  <nav class="tabs">{nav}</nav>
</div></header>
<main class="wrap">
{body}
</main>
<footer class="site-footer"><div class="wrap">
  Files, and the scripts that collected them, are in <a href="https://github.com/{self.repo}">{esc(self.repo)}</a>.
</div></footer>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""
        dest = OUT / rel_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(doc, encoding="utf-8")


def build_home(site):
    items = "".join(
        f'<li><a href="sources/{s["id"]}.html">{esc(s["title"])}</a>'
        f'<span class="muted"> · {len(s["datasets"])} datasets</span><br>'
        f'<span class="small">{esc(s["summary"])}</span></li>'
        for s in site.cat["sources"]
    )
    body = f"""<h1>{esc(site.cat['title'])}</h1>
<p class="lede">{esc(site.cat['tagline'])}</p>
<ul class="source-list">{items}</ul>"""
    site.page("index.html", site.cat["title"], body)


def build_source(site, src):
    rows = []
    for ds in src["datasets"]:
        rows.append(
            f'<tr><td><a href="../{ds["page"]}">{esc(ds["title"])}</a>'
            f'<div class="small muted">{esc(ds["description"])}</div></td>'
            f'<td class="num">{years_text(ds["years"])}</td>'
            f'<td class="num">{ds["rows"]:,}</td>'
            f'<td><a href="{esc(ds["href"])}" download>{ds["ext"].upper()}</a> '
            f'<span class="muted small">{human_size(ds["bytes"])}</span></td></tr>'
        )
    pubs = ""
    if src.get("publications"):
        pubs = build_publications(src["publications"])
    body = f"""<h1>{esc(src['title'])}</h1>
<p class="lede">{esc(src['summary'])}</p>
<p class="small">Publisher: <a href="{esc(src['url'])}">{esc(src['publisher'])}</a></p>
{pubs}
<h2>{'Data files' if pubs else 'Datasets'}</h2>
<div class="table-scroll"><table class="datasets">
<thead><tr><th>Dataset</th><th>Years</th><th>Rows</th><th>Download</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></div>"""
    site.page(f"sources/{src['id']}.html", f"{src['title']} · {site.cat['title']}", body, src["id"])


def build_publications(path):
    keep = ["year", "title", "authors", "primary_theme", "evidence_type", "venue", "publisher",
            "doi", "url", "full_text", "abstract"]
    recs = []
    for r in csv.DictReader(open(ROOT / path, encoding="utf-8")):
        rec = {k: (r.get(k) or "").strip() for k in keep}
        rec["abstract"] = rec["abstract"][:1500]
        recs.append(rec)
    recs.sort(key=lambda r: (r["year"], r["title"]), reverse=True)
    opt = lambda key, rev=False: "".join(
        f'<option value="{esc(v)}">{esc(v)}</option>'
        for v in sorted({r[key] for r in recs if r[key]}, reverse=rev)
    )
    data = json.dumps(recs, ensure_ascii=False).replace("</", "<\\/")
    return f"""<form class="filters" onsubmit="return false">
  <label>Search<input id="lq" type="search" placeholder="Title, author, abstract…"></label>
  <label>Theme<select id="lt"><option value="">All themes</option>{opt('primary_theme')}</select></label>
  <label>Evidence<select id="le"><option value="">All types</option>{opt('evidence_type')}</select></label>
  <label>Year<select id="ly"><option value="">All years</option>{opt('year', True)}</select></label>
</form>
<p id="lcount" class="small muted" aria-live="polite"></p>
<ol id="lit" class="lit"></ol>
<script id="lit-data" type="application/json">{data}</script>"""


def build_dataset(site, src, ds, header, rows):
    link = f' · <a href="{esc(ds["source_url"])}">original table</a>' if ds.get("source_url") else ""
    facts = " · ".join(
        x for x in [years_text(ds["years"]), f'{ds["rows"]:,} rows', f'{len(header)} columns'] if x
    )
    note = (
        f"Showing the first {len(rows):,} of {ds['rows']:,} rows. Download the file for all of them."
        if len(rows) < ds["rows"] else ""
    )
    thead = "".join(f"<th>{esc(h)}</th>" for h in header)
    tbody = "".join(
        "<tr>" + "".join(f"<td>{esc(v[:300])}</td>" for v in r) + "</tr>" for r in rows
    )
    body = f"""<p class="crumbs"><a href="../sources/{src['id']}.html">{esc(src['title'])}</a></p>
<h1>{esc(ds['title'])}</h1>
<p class="lede">{esc(ds['description'])}</p>
<p class="small muted">{facts} · <code>{esc(ds['path'])}</code>{link}</p>
<p class="actions"><a class="button" href="{esc(ds['href'])}" download>Download {ds['ext'].upper()} ({human_size(ds['bytes'])})</a>
<a class="button secondary" href="{esc(site.gh_blob(ds['path']))}">View on GitHub</a></p>
<label class="search"><span class="sr-only">Filter rows</span>
<input id="rowq" type="search" placeholder="Filter rows, e.g. India or 2024" autocomplete="off"></label>
<p class="small muted"><span id="rowcount"></span> {note}</p>
<div class="table-scroll data"><table id="data"><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></div>"""
    site.page(ds["page"], f"{ds['title']} · {site.cat['title']}", body, src["id"])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="fail if a data file is missing from the catalogue")
    args = ap.parse_args()

    catalog = json.loads((SITE_SRC / "catalog.json").read_text(encoding="utf-8"))
    site = Site(catalog)

    missing = [ds["path"] for s in catalog["sources"] for ds in s["datasets"] if not (ROOT / ds["path"]).exists()]
    if missing:
        sys.exit("catalog.json lists files that do not exist:\n  " + "\n  ".join(missing))

    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(SITE_SRC / "assets", OUT / "assets")
    (OUT / ".nojekyll").write_text("")

    slugs = set()
    for src in catalog["sources"]:
        for ds in src["datasets"]:
            path = ROOT / ds["path"]
            slug = slugify(path.stem)
            if slug in slugs:
                slug = slugify(ds["path"].rsplit(".", 1)[0])
            slugs.add(slug)
            ds["page"] = f"data/{slug}.html"
            ds["bytes"] = path.stat().st_size
            ds["ext"] = path.suffix.lstrip(".")
            if ds["bytes"] <= COPY_LIMIT:
                dest = OUT / "files" / ds["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                ds["href"] = "../files/" + ds["path"]
            else:
                ds["href"] = site.gh_raw(ds["path"])
            header, rows, ds["rows"], ds["years"] = read_table(path)
            build_dataset(site, src, ds, header, rows)
            print(f"  {ds['path']}: {ds['rows']:,} rows {years_text(ds['years'])}")
        build_source(site, src)
    build_home(site)

    listed = {ds["path"] for s in catalog["sources"] for ds in s["datasets"]} | set(catalog.get("not_catalogued", []))
    uncatalogued = sorted(
        p.relative_to(ROOT).as_posix()
        for d in CATALOGUED_DIRS
        for p in (ROOT / d).rglob("*")
        if p.suffix in (".csv", ".json") and p.stat().st_size > 0 and p.relative_to(ROOT).as_posix() not in listed
    )
    n = sum(len(s["datasets"]) for s in catalog["sources"])
    print(f"Built {len(catalog['sources'])} source tabs and {n} dataset pages into {OUT.relative_to(ROOT)}/")
    if uncatalogued:
        print("Not in site/catalog.json (add to a source or to not_catalogued):\n  " + "\n  ".join(uncatalogued))
        if args.strict:
            sys.exit(1)


if __name__ == "__main__":
    main()

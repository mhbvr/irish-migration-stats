"""Build the static catalogue website published on GitHub Pages.

Reads site/catalog.json (topics, datasets, reports) and the files it points to,
and writes a plain HTML site to _site/. Row counts, columns, year coverage and
previews are computed from the data files themselves, so the site never drifts
from the repository.

    pip install markdown
    python scripts/50_build_site.py            # writes _site/
    python scripts/50_build_site.py --strict   # also fail on uncatalogued files

The GitHub Actions workflow .github/workflows/pages.yml runs this on every push
to main and deploys _site/.
"""
import argparse
import csv
import html
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SITE_SRC = ROOT / "site"
OUT = ROOT / "_site"

csv.field_size_limit(sys.maxsize)

# Files larger than this are linked to GitHub instead of being copied into the site.
COPY_LIMIT = 20 * 1024 * 1024
PREVIEW_ROWS = 12
# Folders whose data files must all appear in the catalogue (checked with --strict).
CATALOGUED_DIRS = ["data/processed", "literature"]
# Columns whose values carry a year, used for the "years covered" field.
YEAR_COL = re.compile(r"year|^time$|^quarter$|^date$|^week$|^day$|pq_date", re.I)
YEAR_VAL = re.compile(r"(?<!\d)(19[5-9]\d|20[0-4]\d)(?!\d)")
# Headline figures shown on the home page: (indicator in headline_series.csv, label).
KEY_FIGURES = [
    ("Immigration (CSO estimate)", "Immigration", "thousand people, year to April"),
    ("Net migration (CSO estimate)", "Net migration", "thousand people, year to April"),
    ("Employment permits issued", "Employment permits issued", "permits"),
    ("Asylum applicants", "Asylum applicants", "people"),
    ("Acquisitions of Irish citizenship", "New Irish citizens", "people"),
    ("Visa applications received (all visa types)", "Visa applications", "applications"),
]


def esc(s):
    return html.escape(str(s), quote=True)


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def human_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


def fmt_int(n):
    return f"{n:,}"


# ---------------------------------------------------------------- data profiling

def profile_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None) or []
        n = 0
        preview = []
        distinct = [dict() for _ in header]
        years = set()
        year_idx = [i for i, h in enumerate(header) if YEAR_COL.search(h.strip())]
        for row in reader:
            n += 1
            if len(preview) < PREVIEW_ROWS:
                preview.append(row)
            for i, v in enumerate(row[: len(header)]):
                d = distinct[i]
                if d is not None:
                    d[v] = d.get(v, 0) + 1
                    if len(d) > 60:
                        distinct[i] = None
            for i in year_idx:
                if i < len(row):
                    years.update(int(y) for y in YEAR_VAL.findall(row[i]))
    columns = []
    for i, h in enumerate(header):
        d = distinct[i]
        if d is None:
            columns.append({"name": h, "distinct": None, "values": []})
        else:
            vals = sorted(d, key=lambda v: (-d[v], v))
            columns.append({"name": h, "distinct": len(d), "values": vals})
    return {
        "kind": "csv",
        "rows": n,
        "columns": columns,
        "preview": preview,
        "years": (min(years), max(years)) if years else None,
    }


def profile_json(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    info = {"kind": "json", "rows": None, "columns": [], "preview": [], "years": None}
    if isinstance(data, list):
        info["rows"] = len(data)
        keys = []
        for item in data[:200]:
            if isinstance(item, dict):
                keys += [k for k in item if k not in keys]
        info["columns"] = [{"name": k, "distinct": None, "values": []} for k in keys]
        years = set()
        for item in data:
            if isinstance(item, dict):
                for k, v in item.items():
                    if YEAR_COL.search(k) and isinstance(v, (str, int)):
                        years.update(int(y) for y in YEAR_VAL.findall(str(v)))
        info["years"] = (min(years), max(years)) if years else None
        info["preview"] = [
            [str(item.get(k, ""))[:200] for k in keys] for item in data[:PREVIEW_ROWS] if isinstance(item, dict)
        ]
    return info


def profile(path):
    if path.suffix == ".csv":
        return profile_csv(path)
    if path.suffix == ".json":
        return profile_json(path)
    return {"kind": "file", "rows": None, "columns": [], "preview": [], "years": None}


# ---------------------------------------------------------------- page chrome

def git_commit():
    sha = os.environ.get("GITHUB_SHA")
    if sha:
        return sha
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


class Site:
    def __init__(self, catalog):
        self.cat = catalog
        self.repo = os.environ.get("GITHUB_REPOSITORY") or catalog["repo"]
        self.branch = catalog.get("branch", "main")
        self.commit = git_commit()
        self.built = datetime.now(timezone.utc).strftime("%d %B %Y")
        # repo path -> site page (relative to site root), filled in as pages are planned
        self.page_for = {}

    def gh_blob(self, path):
        return f"https://github.com/{self.repo}/blob/{self.branch}/{path}"

    def gh_raw(self, path):
        return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}/{path}"

    def page(self, rel_out, title, body, depth, description=""):
        up = "../" * depth
        nav = [
            ("index.html", "Catalogue"),
            ("reports.html", "Reports"),
            ("literature.html", "Research"),
            ("about.html", "About"),
        ]
        nav_html = "".join(
            f'<a href="{up}{href}"{" aria-current=page" if href == rel_out else ""}>{esc(label)}</a>'
            for href, label in nav
        )
        commit = (
            f' · built from <a href="https://github.com/{self.repo}/commit/{self.commit}">{self.commit[:7]}</a>'
            if self.commit else ""
        )
        doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description or self.cat['tagline'])}">
<link rel="stylesheet" href="{up}assets/style.css">
<link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{up}index.html">{esc(self.cat['title'])}</a>
    <nav>{nav_html}<a href="https://github.com/{self.repo}">GitHub</a></nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="site-footer">
  <div class="wrap">
    Data from official Irish and EU publishers; see <a href="{up}reports/sources.html">sources</a>.
    Updated {esc(self.built)}{commit}.
  </div>
</footer>
<script src="{up}assets/site.js"></script>
</body>
</html>
"""
        dest = OUT / rel_out
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(doc, encoding="utf-8")


# ---------------------------------------------------------------- builders

def dataset_meta_line(ds):
    p = ds["profile"]
    bits = []
    if p["years"]:
        a, b = p["years"]
        bits.append(f"{a}–{b}" if a != b else str(a))
    if p["rows"] is not None:
        bits.append(f"{fmt_int(p['rows'])} {'row' if p['rows'] == 1 else 'rows'}")
    bits.append(ds["ext"].upper())
    bits.append(human_size(ds["bytes"]))
    return " · ".join(bits)


def build_dataset_page(site, ds, topic):
    p = ds["profile"]
    depth = 1
    up = "../"
    download = ds["download"] if ds["download"].startswith("http") else up + ds["download"]
    src = esc(ds.get("source", ""))
    if ds.get("source_url"):
        src = f'<a href="{esc(ds["source_url"])}">{src}</a>'

    facts = [("Topic", f'<a href="{up}index.html#{topic["id"]}">{esc(topic["title"])}</a>'), ("Source", src)]
    if p["years"]:
        a, b = p["years"]
        facts.append(("Years covered", f"{a}–{b}" if a != b else str(a)))
    if p["rows"] is not None:
        facts.append(("Rows", fmt_int(p["rows"])))
    if p["columns"]:
        facts.append(("Columns", str(len(p["columns"]))))
    facts.append(("File", f'<code>{esc(ds["path"])}</code> ({ds["ext"].upper()}, {human_size(ds["bytes"])})'))
    facts_html = "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in facts)

    cols_html = ""
    if p["columns"]:
        rows = []
        for c in p["columns"]:
            if c["distinct"] is None:
                vals = '<span class="muted">many values</span>'
            else:
                shown = c["values"][:8]
                vals = ", ".join(f"<code>{esc(v[:60])}</code>" for v in shown if v != "")
                if c["distinct"] > len(shown):
                    vals += f' <span class="muted">+{c["distinct"] - len(shown)} more</span>'
                vals = f'<span class="muted">{c["distinct"]} values:</span> {vals}'
            rows.append(f"<tr><th scope=row><code>{esc(c['name'])}</code></th><td>{vals}</td></tr>")
        cols_html = f"""<h2>Columns</h2>
<div class="table-scroll"><table class="cols"><tbody>{''.join(rows)}</tbody></table></div>"""

    preview_html = ""
    if p["preview"]:
        head = "".join(f"<th>{esc(c['name'])}</th>" for c in p["columns"])
        body = "".join(
            "<tr>" + "".join(f"<td>{esc(v[:120])}</td>" for v in r) + "</tr>" for r in p["preview"]
        )
        preview_html = f"""<h2>First {len(p['preview'])} rows</h2>
<div class="table-scroll"><table class="preview"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>"""

    extra = ""
    if ds.get("page"):
        extra = f' <a class="button secondary" href="{up}{ds["page"]}">Browse</a>'
    body = f"""<p class="crumbs"><a href="{up}index.html">Catalogue</a> › <a href="{up}index.html#{topic['id']}">{esc(topic['title'])}</a></p>
<h1>{esc(ds['title'])}</h1>
<p class="lede">{esc(ds['description'])}</p>
<p class="actions"><a class="button" href="{esc(download)}" download>Download {ds['ext'].upper()}</a>
<a class="button secondary" href="{esc(site.gh_blob(ds['path']))}">View on GitHub</a>{extra}</p>
<dl class="facts">{facts_html}</dl>
{cols_html}
{preview_html}
"""
    site.page(ds["page_path"], f"{ds['title']} · {site.cat['title']}", body, depth, ds["description"])


def key_figures(site):
    path = ROOT / "data/processed/headline_series.csv"
    if not path.exists():
        return ""
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    tiles = []
    for indicator, label, unit in KEY_FIGURES:
        pts = [
            r for r in rows
            if r["indicator"] == indicator
            and not re.search(r"year-to-date|part-year|partial", r.get("note", ""), re.I)
        ]
        if not pts:
            continue
        pts.sort(key=lambda r: int(r["year"]))
        last = pts[-1]
        prev = pts[-2] if len(pts) > 1 else None
        v = float(last["value"])
        value = f"{v:,.1f}" if v != int(v) else f"{int(v):,}"
        change = ""
        if prev and float(prev["value"]):
            pct = (v - float(prev["value"])) / float(prev["value"]) * 100
            arrow = "▲" if pct > 0 else "▼" if pct < 0 else "="
            change = f'<span class="change">{arrow} {abs(pct):.0f}% on {prev["year"]}</span>'
        tiles.append(
            f'<div class="tile"><div class="tile-label">{esc(label)}, {esc(last["year"])}</div>'
            f'<div class="tile-value">{value}</div><div class="tile-unit">{esc(unit)}</div>{change}'
            f'<a class="tile-src" href="{esc(last["source_url"])}">{esc(last["source"])}</a></div>'
        )
    if not tiles:
        return ""
    ds_page = site.page_for.get("data/processed/headline_series.csv", "")
    return f"""<section class="keyfigs" aria-labelledby="kf">
<h2 id="kf">Latest figures</h2>
<div class="tiles">{''.join(tiles)}</div>
<p class="small muted">Latest complete year of each series. All values and their sources are in the
<a href="{ds_page}">headline indicators</a> dataset.</p>
</section>"""


def build_index(site, topics):
    toc = "".join(
        f'<a class="chip" href="#{t["id"]}">{esc(t["title"])} <span>{len(t["datasets"])}</span></a>'
        for t in topics
    )
    sections = []
    for t in topics:
        cards = []
        for ds in t["datasets"]:
            search = " ".join(
                [ds["title"], ds["description"], ds.get("source", ""), t["title"], ds["path"]]
                + [c["name"] for c in ds["profile"]["columns"]]
            ).lower()
            feat = " featured" if ds.get("featured") else ""
            cards.append(
                f'<article class="card{feat}" data-search="{esc(search)}">'
                f'<h3><a href="{ds["page_path"]}">{esc(ds["title"])}</a></h3>'
                f'<p>{esc(ds["description"])}</p>'
                f'<p class="meta">{esc(dataset_meta_line(ds))}</p>'
                f'<p class="meta source">{esc(ds.get("source", ""))}</p></article>'
            )
        sections.append(
            f'<section class="topic" id="{t["id"]}"><h2>{esc(t["title"])}</h2>'
            f'<p class="topic-summary">{esc(t["summary"])}</p>'
            f'<div class="cards">{"".join(cards)}</div></section>'
        )
    report_cards = "".join(
        f'<a class="report" href="reports/{r["slug"]}.html"><strong>{esc(r["title"])}</strong>'
        f'<span>{esc(r["summary"])}</span></a>'
        for r in site.cat["reports"][:4]
    )
    n_ds = sum(len(t["datasets"]) for t in topics)
    body = f"""<section class="hero">
<h1>{esc(site.cat['title'])}</h1>
<p class="lede">{esc(site.cat['tagline'])}</p>
<p class="small muted">{n_ds} datasets in {len(topics)} topics. Every figure is read from an official source file,
recorded with its URL and checksum.</p>
</section>
{key_figures(site)}
<section aria-labelledby="rp"><h2 id="rp">Reports</h2><div class="reports">{report_cards}</div>
<p class="small"><a href="reports.html">All reports and sources →</a></p></section>
<section class="finder" aria-labelledby="cat">
<h2 id="cat">Data catalogue</h2>
<label class="search"><span class="sr-only">Search datasets</span>
<input id="q" type="search" placeholder="Search datasets, e.g. nationality, sector, Ukraine, visa" autocomplete="off"></label>
<p id="q-status" class="small muted" aria-live="polite"></p>
<nav class="chips" aria-label="Topics">{toc}</nav>
</section>
{''.join(sections)}
"""
    site.page("index.html", site.cat["title"], body, 0)


def rewrite_links(site, html_text, md_path):
    """Point relative links in a rendered report at the site's own pages, or at GitHub."""
    base = (ROOT / md_path).parent

    def fix(m):
        attr, href = m.group(1), html.unescape(m.group(2))
        if re.match(r"^[a-z][a-z0-9+.-]*:", href, re.I) and not re.match(r"^(S2|DOAJ):", href):
            return m.group(0)
        if href.startswith("#"):
            return m.group(0)
        target, _, anchor = href.partition("#")
        try:
            rel = (base / target).resolve().relative_to(ROOT).as_posix()
        except ValueError:
            rel = None
        if rel is None or not (ROOT / rel).exists():
            return f'{attr}="#" data-broken="1"'
        if rel in site.page_for:
            new = "../" + site.page_for[rel] + (f"#{anchor}" if anchor else "")
        else:
            new = site.gh_blob(rel) + (f"#{anchor}" if anchor else "")
        return f'{attr}="{esc(new)}"'

    out = re.sub(r'(href)="([^"]*)"', fix, html_text)
    # Drop links that could not be resolved, keeping their text.
    return re.sub(r'<a href="#" data-broken="1">(.*?)</a>', r"\1", out, flags=re.S)


def build_reports(site):
    cards = []
    for r in site.cat["reports"]:
        path = ROOT / r["path"]
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"])
        rendered = md.convert(path.read_text(encoding="utf-8"))
        rendered = rewrite_links(site, rendered, r["path"])
        rendered = rendered.replace("<table>", '<div class="table-scroll"><table>').replace(
            "</table>", "</table></div>"
        )
        toc = md.toc if md.toc_tokens and sum(len(t["children"]) for t in md.toc_tokens) > 2 else ""
        aside = f'<aside class="toc"><h2>Contents</h2>{toc}</aside>' if toc else ""
        body = f"""<p class="crumbs"><a href="../reports.html">Reports</a></p>
<div class="report-layout{' has-toc' if toc else ''}">{aside}<article class="prose">{rendered}
<p class="small muted source-note">Source: <a href="{esc(site.gh_blob(r['path']))}"><code>{esc(r['path'])}</code></a> in the repository.</p>
</article></div>"""
        site.page(f"reports/{r['slug']}.html", f"{r['title']} · {site.cat['title']}", body, 1, r["summary"])
        cards.append(
            f'<a class="report" href="reports/{r["slug"]}.html"><strong>{esc(r["title"])}</strong>'
            f'<span>{esc(r["summary"])}</span></a>'
        )
    body = f"""<h1>Reports</h1>
<p class="lede">Written analyses built on the data in the catalogue. Every figure in them links back to a dataset or an official source.</p>
<div class="reports">{''.join(cards)}</div>"""
    site.page("reports.html", f"Reports · {site.cat['title']}", body, 0)


def build_literature(site):
    path = ROOT / "literature/catalogue.csv"
    if not path.exists():
        return
    keep = ["year", "title", "authors", "primary_theme", "evidence_type", "data_sources",
            "publication_type", "venue", "publisher", "doi", "url", "full_text", "stage", "abstract"]
    records = []
    for r in csv.DictReader(open(path, encoding="utf-8")):
        rec = {k: (r.get(k) or "").strip() for k in keep}
        rec["abstract"] = rec["abstract"][:1500]
        records.append(rec)
    records.sort(key=lambda r: (r["year"], r["title"]), reverse=True)
    themes = sorted({r["primary_theme"] for r in records if r["primary_theme"]})
    evid = sorted({r["evidence_type"] for r in records if r["evidence_type"]})
    years = sorted({r["year"] for r in records if r["year"]}, reverse=True)
    opt = lambda vals: "".join(f'<option value="{esc(v)}">{esc(v)}</option>' for v in vals)
    data = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    cat_page = site.page_for.get("literature/catalogue.csv", "")
    body = f"""<h1>Research on migration in Ireland</h1>
<p class="lede">{len(records)} academic and research-institute publications with data about Ireland, published 2023–2026.
Found in two stages: ESRI first, then Semantic Scholar, Crossref, DOAJ and Europe PMC.</p>
<p class="small">Read the <a href="reports/literature-review.html">literature review</a> for the synthesis,
or download the <a href="{cat_page}">full catalogue</a>.</p>
<form class="filters" onsubmit="return false">
  <label>Search<input id="lq" type="search" placeholder="Title, author, abstract…"></label>
  <label>Theme<select id="lt"><option value="">All themes</option>{opt(themes)}</select></label>
  <label>Evidence<select id="le"><option value="">All types</option>{opt(evid)}</select></label>
  <label>Year<select id="ly"><option value="">All years</option>{opt(years)}</select></label>
</form>
<p id="lcount" class="small muted" aria-live="polite"></p>
<ol id="lit" class="lit"></ol>
<script id="lit-data" type="application/json">{data}</script>
"""
    site.page("literature.html", f"Research · {site.cat['title']}", body, 0)


def build_about(site, topics, uncatalogued):
    body = f"""<div class="prose">
<h1>About this site</h1>
<p>This site is a readable front end to the
<a href="https://github.com/{site.repo}">{esc(site.repo)}</a> repository. The data, the scripts that
produced it and this website all live in the same repository: the site is rebuilt and published by
GitHub Actions each time the <code>{esc(site.branch)}</code> branch changes, so it always reflects what is in the repository.</p>
<h2>Where the numbers come from</h2>
<p>Only official publishers are used: the Central Statistics Office, the Department of Enterprise,
Tourism and Employment, the Department of Justice, Home Affairs and Migration (directly and via
data.gov.ie), the Houses of the Oireachtas and Eurostat. No figure is typed in by hand; each file's URL,
retrieval time and SHA-256 are in the <a href="{site.page_for.get('data/processed/sources_register.csv', '')}">sources register</a>.
See <a href="reports/sources.html">Sources</a> for details.</p>
<h2>Using the data</h2>
<p>Each dataset page has a download button, a list of columns with example values and a preview of the
first rows. CSV files open in any spreadsheet program. Files larger than {human_size(COPY_LIMIT)} are
downloaded directly from GitHub.</p>
<h2>Adding a dataset to the catalogue</h2>
<p>Add an entry for the file to <code>site/catalog.json</code> under the right topic, with a title,
description and source. Row counts, columns, years and previews are worked out automatically by
<code>scripts/50_build_site.py</code>.</p>
{"<p class='small muted'>Files not yet catalogued: " + ", ".join(f"<code>{esc(u)}</code>" for u in uncatalogued) + "</p>" if uncatalogued else ""}
</div>"""
    site.page("about.html", f"About · {site.cat['title']}", body, 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--strict", action="store_true", help="fail if a data file is missing from the catalogue")
    args = ap.parse_args()

    catalog = json.loads((SITE_SRC / "catalog.json").read_text(encoding="utf-8"))
    site = Site(catalog)

    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets").mkdir(parents=True)
    for f in (SITE_SRC / "assets").iterdir():
        shutil.copy2(f, OUT / "assets" / f.name)
    (OUT / ".nojekyll").write_text("")

    # Plan pages first so links between pages can be resolved.
    missing = []
    for r in catalog["reports"]:
        site.page_for[r["path"]] = f"reports/{r['slug']}.html"
    seen_slugs = set()
    for t in catalog["topics"]:
        for ds in t["datasets"]:
            path = ROOT / ds["path"]
            if not path.exists():
                missing.append(ds["path"])
                continue
            slug = slugify(Path(ds["path"]).stem)
            if slug in seen_slugs:
                slug = slugify(ds["path"].rsplit(".", 1)[0])
            seen_slugs.add(slug)
            ds["page_path"] = f"datasets/{slug}.html"
            site.page_for.setdefault(ds["path"], ds["page_path"])
    if missing:
        sys.exit("catalog.json lists files that do not exist:\n  " + "\n  ".join(missing))

    # Profile and copy data files.
    total = 0
    for t in catalog["topics"]:
        for ds in t["datasets"]:
            path = ROOT / ds["path"]
            ds["bytes"] = path.stat().st_size
            ds["ext"] = path.suffix.lstrip(".")
            ds["profile"] = profile(path)
            if ds["bytes"] <= COPY_LIMIT:
                dest = OUT / "files" / ds["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(path, dest)
                ds["download"] = f"files/{ds['path']}"
            else:
                ds["download"] = site.gh_raw(ds["path"])
            total += 1
            print(f"  {ds['path']}: {dataset_meta_line(ds)}")

    catalogued = {ds["path"] for t in catalog["topics"] for ds in t["datasets"]}
    ignored = set(catalog.get("not_catalogued", []))
    uncatalogued = sorted(
        p.relative_to(ROOT).as_posix()
        for d in CATALOGUED_DIRS
        for p in (ROOT / d).rglob("*")
        if p.suffix in (".csv", ".json") and p.stat().st_size > 0
        and p.relative_to(ROOT).as_posix() not in catalogued | ignored
    )

    for t in catalog["topics"]:
        for ds in t["datasets"]:
            build_dataset_page(site, ds, t)
    build_index(site, catalog["topics"])
    build_reports(site)
    build_literature(site)
    build_about(site, catalog["topics"], uncatalogued)

    # Machine-readable catalogue for anyone who wants to script against the site.
    machine = [
        {
            "topic": t["title"], "title": ds["title"], "description": ds["description"],
            "source": ds.get("source", ""), "source_url": ds.get("source_url", ""),
            "path": ds["path"], "download": ds["download"], "page": ds["page_path"],
            "rows": ds["profile"]["rows"], "years": ds["profile"]["years"],
            "columns": [c["name"] for c in ds["profile"]["columns"]], "bytes": ds["bytes"],
        }
        for t in catalog["topics"] for ds in t["datasets"]
    ]
    (OUT / "catalog.json").write_text(json.dumps(machine, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"Built {total} dataset pages and {len(catalog['reports'])} reports into {OUT.relative_to(ROOT)}/")
    if uncatalogued:
        print("Not in site/catalog.json:\n  " + "\n  ".join(uncatalogued))
        if args.strict:
            sys.exit(1)


if __name__ == "__main__":
    main()

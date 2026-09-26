"""Literature: render catalogue.csv as a browsable, linked bibliography
(literature/BIBLIOGRAPHY.md), grouped by primary theme, newest first."""
import csv, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
L = ROOT / "literature"
rows = list(csv.DictReader(open(L / "catalogue.csv", encoding="utf-8")))
hist = list(csv.DictReader(open(L / "historical_appendix.csv", encoding="utf-8")))


def authors(a):
    xs = [x.strip() for x in (a or "").replace(" et al.", "").split(";") if x.strip()]
    return (", ".join(xs[:3]) + (" et al." if len(xs) > 3 else "")) or "—"


def safe(u):
    """Percent-encode characters that break a Markdown link target, e.g. DOIs
    such as 10.1016/s0167-8140(24)02251-5."""
    return (u or "").replace("(", "%28").replace(")", "%29").replace(" ", "%20")


def link(r):
    u = r["doi"] and f"https://doi.org/{r['doi'].replace('https://doi.org/', '')}" or r["url"]
    return f"[{r['title'].strip()}]({safe(u)})"


def entry(r):
    bits = [f"{authors(r['authors'])} ({r['year']}). {link(r)}."]
    if r["venue"]:
        bits.append(f"*{r['venue']}*.")
    tags = [r["evidence_type"], r["jurisdiction"]]
    if r.get("data_sources"):
        tags.append("data: " + r["data_sources"])
    bits.append(" · ".join(t for t in tags if t))
    if r.get("full_text") and r["full_text"] != r["url"]:
        bits.append(f"[full text]({safe(r['full_text'])})")
    return "- " + " ".join(bits)


groups = collections.defaultdict(list)
for r in rows:
    groups[r["primary_theme"]].append(r)
order = sorted(groups, key=lambda k: (-len(groups[k]), k))

out = ["# Bibliography: migration, migrants and naturalisation in Ireland (published 2023–2026)", "",
       f"{len(rows)} publications. Stage 1 = ESRI; stage 2 = Semantic Scholar, Crossref, DOAJ, Europe PMC. "
       "Grouped by primary theme (keyword-assigned from the title); newest first. "
       "Evidence type, jurisdiction and data sources are keyword-derived from the abstract - "
       "see `catalogue.csv` for the screening note behind every entry.", ""]
out += ["## Contents", ""] + [f"- {k} ({len(groups[k])})" for k in order] + \
       [f"- Appendix: historical studies ({len(hist)})", ""]
for k in order:
    out += [f"## {k} ({len(groups[k])})", ""]
    out += [entry(r) for r in sorted(groups[k], key=lambda r: r["date"] or "", reverse=True)]
    out.append("")
out += ["## Appendix: historical studies", "",
        "Published 2023+ but about migration before c.1960 (mostly the 19th–20th-century Irish diaspora). "
        "Kept for completeness; not included in the analysis.", ""]
out += [f"- {authors(r['authors'])} ({r['year']}). {link(r)}." + (f" *{r['venue']}*." if r["venue"] else "")
        for r in sorted(hist, key=lambda r: r["date"] or "", reverse=True)]
(L / "BIBLIOGRAPHY.md").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"wrote literature/BIBLIOGRAPHY.md ({len(rows)} entries + {len(hist)} historical)")

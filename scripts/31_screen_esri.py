"""Literature stage 1: screen the ESRI candidates (from script 30).

Steps
  1. Drop items that are not research publications (newspaper/magazine pieces,
     corporate information, policy submissions, index reports) - recorded, not
     silently removed.
  2. Apply the shared topic rule (litscreen.assess) to title + abstract.
  3. For topic-relevant items, download the PDF (provenance logged) and extract
     its text, then count how often Ireland is actually discussed. Every ESRI
     PDF carries Dublin/Ireland boilerplate on the cover and imprint, so a
     handful of mentions proves nothing; the counts are reported so the
     threshold can be checked.
       >= 25 mentions and empirical signals  -> include
       8-24                                   -> review (by hand)
       < 8                                    -> review, likely no Irish data
Outputs literature/esri/esri_screened.csv (every candidate, with the reason).
"""
import csv, json, re, sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from fetchlib import fetch
from litscreen import assess, IRELAND
import pdfplumber

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "literature" / "esri"
NOT_RESEARCH = {"Newspaper/Magazine Article", "Corporate Information", "ESRI Submission", "Indices Report"}

cands = json.loads((D / "esri_candidates.json").read_text())
manual = {}
mf = ROOT / "literature" / "manual_decisions.csv"
if mf.exists():
    for r in csv.DictReader(open(mf, encoding="utf-8")):
        manual[r["url"]] = r


def pdf_text(path, max_pages=80):
    """Extracted text is cached beside the PDF (<name>.txt, first line = page
    count) because pdfplumber takes ~30 s per long report."""
    cache = pathlib.Path(str(path) + ".txt")
    if cache.exists():
        pages, _, text = cache.read_text(encoding="utf-8").partition("\n")
        return text, int(pages or 0)
    try:
        with pdfplumber.open(path) as pdf:
            text, pages = "\n".join((p.extract_text() or "") for p in pdf.pages[:max_pages]), len(pdf.pages)
    except Exception:                                           # noqa: BLE001
        return "", 0
    cache.write_text(f"{pages}\n{text}", encoding="utf-8")
    return text, pages


rows = []
for c in sorted(cands, key=lambda c: c.get("date", ""), reverse=True):
    base = {"url": c["url"], "date": c.get("date", ""), "title": c.get("title", ""),
            "series": c.get("series", ""), "authors": "; ".join(c.get("authors", [])),
            "research_areas": "; ".join(c.get("research_areas", [])),
            "doi": c.get("doi", ""), "pdf_url": (c.get("pdf_urls") or [""])[0],
            "found_by": "; ".join(c.get("found_by", [])), "abstract": c.get("abstract", "")}
    if c.get("date", "") < "2023-01-01":
        rows.append({**base, "status": "exclude", "reasons": "published before 2023"}); continue
    if base["series"] in NOT_RESEARCH:
        rows.append({**base, "status": "exclude", "reasons": f"not a research publication ({base['series']})"}); continue

    a = assess(base["title"], base["abstract"])
    topical = not a["reasons"].startswith(("non-human", "no migration"))
    if not topical:
        rows.append({**base, **a, "status": "exclude"}); continue

    text, pages, ire_pdf = "", 0, ""
    if base["pdf_url"]:
        name = re.sub(r"[^A-Za-z0-9._-]", "_", base["pdf_url"].rsplit("/", 1)[-1])
        p = fetch(base["pdf_url"], f"../../literature/esri/pdf/{name}",
                  source_page=base["url"], note=f"ESRI publication PDF: {base['title'][:120]}")
        if p:
            text, pages = pdf_text(p)
            ire_pdf = len(IRELAND.findall(text))
    a = assess(base["title"], base["abstract"], extra_text=text)
    status = a["status"]
    why = [a["reasons"]] if a["reasons"] else []
    if ire_pdf != "":
        why.append(f"PDF: {pages} pages, {ire_pdf} Ireland mentions")
        # full text can upgrade a "review" only when an unambiguous migration term
        # is present AND migration is a focus of the document
        focused = a["strong_in_title"] or a["strong_mentions"] >= 3 or a["strong_mentions_fulltext"] >= 30
        if ire_pdf >= 25 and a["empirical_signals"] and a["strong_terms"] and focused:
            status = "include"
        elif status == "include":
            status = "review"
    elif not base["pdf_url"]:
        why.append("no PDF on ESRI page (journal article or external)")

    if c["url"] in manual:
        m = manual[c["url"]]
        status, why = m["decision"], why + [f"MANUAL: {m['reason']}"]
    rows.append({**base, **a, "status": status, "reasons": "; ".join(w for w in why if w),
                 "pdf_pages": pages or "", "ireland_mentions_pdf": ire_pdf})

cols = ["status", "date", "title", "series", "authors", "reasons", "strong_terms", "strong_mentions",
        "strong_mentions_fulltext", "migration_terms",
        "ireland_mentions_pdf", "pdf_pages", "empirical_signals", "jurisdiction", "era",
        "research_areas", "doi", "url", "pdf_url", "found_by", "abstract"]
with open(D / "esri_screened.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)

import collections
print(f"wrote literature/esri/esri_screened.csv ({len(rows)} candidates)")
for s, n in collections.Counter(r["status"] for r in rows).most_common():
    print(f"  {n:4}  {s}")

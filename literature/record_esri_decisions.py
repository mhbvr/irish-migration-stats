"""Manual screening decisions for stage 1 (ESRI) - the refined-rule review queue.
Earlier stage-1 decisions (first review pass) are kept; this adds/overrides by URL.
Each fragment must match exactly one ESRI candidate."""
import csv, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
esri = list(csv.DictReader(open(ROOT / "literature/esri/esri_screened.csv", encoding="utf-8")))
ws = lambda t: re.sub(r"\s+", " ", t or "").strip().lower()

DEC = {
 "Student mobility into and out of Northern Ireland: What brain drain?": ("include", "student migration into/out of NI (brain drain)"),
 "Student mobility in Ireland and Northern Ireland": ("include", "cross-border student migration, island of Ireland"),
 "How do EMN Countries monitor the integration of non-EU nationals?": ("include", "EMN comparative memo; describes Ireland's own practice"),
 "The experience of housing discrimination and housing deprivation across social groups in Ireland": ("include", "housing discrimination compared across groups incl. migrants/ethnic minorities (same decision as stage 2)"),
 "Understanding attitudes to Travellers and Roma in Ireland": ("include", "attitudes to Roma, a largely migrant-origin population in Ireland (Traveller component noted)"),
 "The macroeconomic impact of tariffs on Northern Ireland": ("exclude", "not migration"),
 "Motivations for car ownership": ("exclude", "not migration"),
 "Perceived discrimination and young people’s health and wellbeing in Ireland": ("exclude", "immigrant adolescents one of five groups; migration incidental (12 mentions in 97 pp.)"),
 "How do disability rates differ across the island of Ireland?": ("exclude", "not migration"),
 "Trends in disability prevalence among young people": ("exclude", "not migration"),
 "Population projections, the flow of new households and structural housing demand": ("exclude", "housing demand; migration only an input assumption"),
 "Quarterly Economic Commentary, Summer 2024": ("exclude", "macro commentary; migration incidental"),
 "Gender and labour market inclusion on the island of Ireland": ("exclude", "migration incidental"),
 "Housing adequacy and child outcomes in early and middle childhood": ("exclude", "not migration"),
 "The long-term outcomes of school absence": ("exclude", "migrant status used only as a control variable"),
}
out = []
for frag, (dec, why) in DEC.items():
    hits = [x for x in esri if ws(x["title"]) == ws(frag)] or [x for x in esri if ws(frag) in ws(x["title"])]
    if len(hits) != 1:
        sys.exit(f"{len(hits)} matches for {frag!r}: {[h['title'][:60] for h in hits]}")
    out.append({"url": hits[0]["url"], "decision": dec, "reason": why, "stage": "1-ESRI",
                "decided_by": "manual review of abstract/PDF", "date": "2026-09-26"})

mf = ROOT / "literature/manual_decisions.csv"
prev = list(csv.DictReader(open(mf, encoding="utf-8")))
new_urls = {r["url"] for r in out}
keep = [r for r in prev if r["url"] not in new_urls]
with open(mf, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["url", "decision", "reason", "stage", "decided_by", "date"])
    w.writeheader(); w.writerows(keep + out)
print(f"stage-1 decisions added/updated: {len(out)}")

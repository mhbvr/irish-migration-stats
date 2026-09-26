"""Shared screening rules for the literature search (used by scripts 31 and 33).

A publication is IN SCOPE only if all three hold:
  1. topic   - it is about migration / migrants / naturalisation in the social
               sense (not cell, animal, chemical or data migration);
  2. Ireland - it carries data or evidence about Ireland (the State, or Northern
               Ireland / the island, which is tagged separately);
  3. date    - published on or after 2023-01-01 (enforced by the queries).

Each rule returns its evidence, so every decision in the output can be read and
challenged. Borderline cases get status "review" and are decided by hand in
literature/manual_decisions.csv, with the reason recorded.
"""
import re

STRONG = re.compile(
    r"\b(migrants?|immigrants?|immigration|emigrants?|emigration|naturali[sz]ation|"
    r"naturali[sz]ed (?:citizens?|Irish|persons?|people)|asylum|refugees?|international protection|"
    r"temporary protection|IPAS|diaspora|third[- ]country nationals?|non-Irish nationals?|foreign[- ]born|"
    r"born abroad|ethnic minorit(?:y|ies)|employment permits?|work permits?|visas?|deportation|"
    r"Ukrainians?|displaced (?:persons|people)|beneficiar(?:y|ies) of temporary protection|"
    r"undocumented|family reunification|newcomers?|returnees?|return migration|"
    r"international students?|seasonal workers?|migrant workers?|trafficking|"
    # citizenship only in the legal sense (not "global/digital/active citizenship")
    r"Irish citizenship|citizenship (?:applications?|acquisition|law|referendum|ceremon(?:y|ies)|by descent)|"
    r"acquisition of citizenship)\b"
    # "Direct Provision" only as the asylum reception system, which is capitalised
    r"|\bdirect provision (?:centres?|system|accommodation)\b", re.I)
DP_CAPS = re.compile(r"\bDirect Provision\b")          # case-sensitive: the asylum system
WEAK = re.compile(r"\b(migration|migrat(?:e|ed|ing)|integration|mobility|nationality|ethnicity|racism|discrimination)\b", re.I)
NON_HUMAN = re.compile(
    r"\b(cell migration|neural crest|tumou?r|metasta\w+|salmon|trout|eels?|birds?|avian|larva\w*|"
    r"fish(?:es)?|whales?|bats?|insects?|species|seed dispersal|leaching|contaminant|nanoparticle|"
    r"data migration|cloud migration|database|software|legacy system|electromigration|"
    r"ion migration|plasticiser|chromatograph\w*|groundwater|sediment|glacial)\b", re.I)

IRELAND = re.compile(
    r"\b(Ireland|Irish|Dublin|Cork|Galway|Limerick|Waterford|Kerry|Donegal|Mayo|Sligo|"
    r"Wexford|Kilkenny|Tipperary|Clare|Leinster|Munster|Connacht|Ulster|Oireachtas|Dáil|"
    r"Tusla|HSE|Gardaí?|CSO)\b")
NI_ONLY = re.compile(r"\b(Northern Ireland|Belfast|Derry|Londonderry|Northern Irish)\b", re.I)
ROI = re.compile(r"\b(Republic of Ireland|the State|Dublin|Cork|Galway|Limerick|Waterford|Oireachtas|"
                 r"Dáil|Tusla|HSE|Garda|CSO|Irish Government|Government of Ireland|Ireland's)\b")

EMPIRICAL = re.compile(
    r"\b(data|dataset|survey|surveys|interview\w*|focus groups?|census|sample|respondents?|"
    r"participants?|administrative|register|records|statistics|estimat\w+|regression|"
    r"quantitative|qualitative|mixed[- ]methods?|ethnograph\w*|fieldwork|case stud(?:y|ies)|"
    r"analysis of|we analy[sz]e|we find|findings|results show|evidence|cohort|longitudinal|"
    r"questionnaire|panel|microdata|PAYE|Revenue|Growing Up in Ireland|Labour Force Survey|"
    r"EU-SILC|SILC|n\s*=\s*\d+|\d+ (?:people|persons|participants|respondents|migrants|refugees))\b", re.I)

LITERARY = re.compile(
    r"\b(novels?|novelists?|poetry|poems?|poets?|fiction|literary|literature of|film|films|cinema|"
    r"theatre|drama|playwright|songs?|memoir|autobiograph\w*|cartoon|adaptation|James Joyce|"
    r"Beckett|Yeats|short stor(?:y|ies)|travel narratives?|reading of|close reading)\b", re.I)
HISTORICAL = re.compile(r"\b(1[5-8]\d\d|19[0-6]\d)s?\b|\b(famine|nineteenth[- ]century|"
                        r"eighteenth[- ]century|medieval|early modern|Victorian)\b", re.I)


def assess(title, abstract, extra_text=""):
    """Return dict with status in {include, exclude, review} plus evidence."""
    t = f"{title or ''} . {abstract or ''}"
    full = t + " " + (extra_text or "")
    strong = sorted({m.group(0).lower() for m in STRONG.finditer(t)} |
                    ({"direct provision"} if DP_CAPS.search(t) else set()))
    weak = sorted({m.group(0).lower() for m in WEAK.finditer(t)})
    nonhuman = sorted({m.group(0).lower() for m in NON_HUMAN.finditer(t)})
    ire = sorted({m.group(0) for m in IRELAND.finditer(full)})
    ire_n = len(IRELAND.findall(full))
    emp = sorted({m.group(0).lower() for m in EMPIRICAL.finditer(full)})[:8]
    ni = bool(NI_ONLY.search(full))
    roi = bool(ROI.search(full)) or bool(re.search(r"\bIreland\b", full.replace("Northern Ireland", "")))
    jurisdiction = ("NI and ROI/island" if ni and roi else "Northern Ireland" if ni
                    else "Ireland (State)" if roi or ire else "")
    era = "historical" if HISTORICAL.search(t) and not re.search(r"\b20[12]\d\b", t) else "contemporary"

    # Focus: is migration the SUBJECT, or just a covariate / passing mention?
    strong_n = len(STRONG.findall(t)) + len(DP_CAPS.findall(t))
    migr_n = strong_n + len(re.findall(r"\bmigrat\w*", t, re.I))
    strong_in_title = bool(STRONG.search(title or ""))
    strong_in_extra = len(STRONG.findall(extra_text or ""))

    reasons = []
    topic_ok = bool(strong) or (bool(weak) and not nonhuman)
    if nonhuman and not strong:
        topic_ok = False
        reasons.append(f"non-human sense of migration ({', '.join(nonhuman[:3])})")
    if not topic_ok and not nonhuman:
        reasons.append("no migration vocabulary")
    if not ire:
        reasons.append("no Ireland reference")

    if not abstract and not extra_text:
        status = "review" if topic_ok and ire else "exclude"
        reasons.append("no abstract to verify")
    elif topic_ok and ire and emp and strong:
        status = "include"
    elif not topic_ok or not ire:
        status = "exclude"
    else:
        status = "review"
        if not emp:
            reasons.append("no sign of empirical data")
        if not strong:
            reasons.append("only ambiguous migration terms")
    focused = strong_in_title or strong_n >= 3 or strong_in_extra >= 30
    if status == "include" and not focused:
        # Incidental mention: excluded unless migration vocabulary as a whole is
        # frequent (catches e.g. "migration patterns of training doctors")
        if migr_n >= 3:
            status = "review"
            reasons.append(f"migration partly incidental ({strong_n} core + {migr_n - strong_n} 'migrat*' mentions)")
        else:
            status = "exclude"
            reasons.append(f"migration incidental ({strong_n} core-term mention(s), not in title)")
    literary = bool(LITERARY.search(t)) and not re.search(
        r"\b(survey|interview\w*|respondents?|participants?|census|dataset|regression)\b", t, re.I)
    if status != "exclude" and literary:
        status = "exclude"
        reasons.append("literary/cultural analysis without data")
    if status != "exclude" and era == "historical":
        status = "historical"
        reasons.append("historical study (subject before 1960) - listed in the historical appendix")
    return {"status": status, "reasons": "; ".join(reasons),
            "strong_terms": ", ".join(strong), "strong_mentions": strong_n,
            "strong_in_title": strong_in_title, "strong_mentions_fulltext": strong_in_extra,
            "migration_terms": ", ".join(strong or weak), "ireland_terms": ", ".join(ire),
            "ireland_mentions": ire_n, "empirical_signals": ", ".join(emp),
            "jurisdiction": jurisdiction, "era": era}

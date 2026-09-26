"""Manual screening decisions for stage 2 (broad search), written to
literature/manual_decisions.csv keyed by each record's URL/DOI.

Each fragment must match exactly ONE record in the review set, otherwise this
script stops - a guard against a short title fragment silently matching two
publications.
"""
import csv, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
rev = [x for x in csv.DictReader(open(ROOT / "literature/broad/broad_screened.csv", encoding="utf-8"))
       if x["status"] in ("review", "include", "exclude", "historical")]

INC_MIG = "contemporary migration in Ireland/NI is the subject; Irish-specific evidence"
DEC = {
 # ---- ambiguous-terms-only bucket, rescued after reading the abstract
 "Language-sensitive teaching as an emergent response": ("include", "survey/fieldwork with teachers & managers in Irish post-primary schools on migration-driven linguistic diversity"),
 "Developing culturally responsive school leaders in Ireland and Spain": ("include", "interviews with 30 principals/teachers in Ireland & Spain on migration-driven diversity"),
 "Perceptions of and preparedness for cross-cultural care": ("include", "survey of final-year medical students in ROI on care for a migration-diversified population"),
 "Investigating Language and Culture Awareness of Pre-Service Science Teachers": ("include", "Irish study of teacher preparedness for migrant-origin pupils"),
 "Nationality and Citizenship in Ireland, North and South": ("include", "legal analysis of acquisition/loss of Irish and British nationality (citizenship law, North and South)"),
 "The Experience of Housing Discrimination and Housing Deprivation Across Social Groups in Ireland": ("include", "ESRI analysis comparing housing discrimination across groups incl. migrants/ethnic minorities in Ireland"),
 "Perezhivanie and Multilingual Adolescents": ("include", "qualitative study of multilingual/migrant adolescents' school belonging in Northern Ireland"),
 "Language assessment of Polish": ("include", "Polish-English bilingual (migrant-origin) children assessed by SLTs in Ireland"),
 "A qualitative study exploring the migration decisions of Irish-trained specialist doctors": ("include", "27 interviews on emigration/return decisions of Irish-trained doctors"),
 "A discovery into the levels of work engagement of young Irish nurses": ("include", "interviews with Irish nurses who emigrated to Australia (emigration)"),
 "Workforce Shortages, Transnational Mobility and Professional Regulation in Social Work": ("include", "Ireland case study of internationally qualified social workers"),
 "Inclusion is not enough: a qualitative study of leadership": ("include", "qualitative study of school leaders responding to inward migration in Northern Ireland"),
 "A novel data resource: Developing the Census 2021 Comprehensive Microdata": ("include", "NI Census 2021 microdata resource for the (largely migrant-origin) minority ethnic population"),
 "They Started School and Then English Crept in at Home": ("include", "focus group/interviews with Polish transnational families in Ireland"),
 "Practices and perspectives of speech-language pathologists in the assessment of multilingual": ("include", "survey of 131 clinicians in ROI assessing multilingual migrant-origin children"),
 "Exploring intersectional inequalities in students' sense of belonging": ("include", "cross-national incl. Ireland; migration background is an analysed axis"),
 "The role of non‐resident family ties in rural staying": ("include", "internal migration / staying intentions, survey+interviews incl. Northern Ireland"),
 "The Irish in England": ("historical", "Irish emigrants in England 1838-2018 from probate/vital registers - historical appendix"),
 "EUPopLink Country report": ("exclude", "populism/Euroscepticism report; migration only as a campaign topic"),
 "The nexus of Family Language Policy": ("exclude", "special-issue introduction; no Irish data"),
 # ---- no-empirical-signal bucket: includes
 "My Health, My Language": ("include", "multilingual health messaging for migrants in Ireland (12% foreign-born)"),
 "chasing integration policy in Northern Ireland": ("include", "asylum seekers and refugees in Northern Ireland and integration policy"),
 "Defying Davy Jones": ("include", "Irish Naval Service role in Mediterranean search & rescue and irregular migration"),
 "Workforce retention of junior doctors in Ireland": ("include", "review of Irish evidence on junior doctor retention and emigration"),
 "Starting a conversation about racism with teenagers": ("include", "Irish social work research on racism amid migration-driven diversity"),
 "Interfaith Dialogue Reflected in The Irish Times": ("include", "document analysis of Irish Times coverage of Romanian immigrants in Ireland"),
 "Ireland’s Emerging Cyber Crisis": ("include", "online anti-immigrant/nationalist mobilisation in Ireland"),
 "Quasi (-social) citizenship, the common travel area": ("include", "legal analysis of Irish citizens' migration rights in the UK under the Common Travel Area"),
 "Carceralities and Approved Gender Violence": ("include", "Direct Provision in Ireland (asylum reception)"),
 "Connecting with the Diaspora and Promoting Economic Development": ("include", "analysis of the Irish State's diaspora strategy"),
 "Irish Diaspora Business Elite philanthropy": ("include", "Irish diaspora philanthropy and State engagement"),
 "Minority Religions and Immigration in Ireland": ("include", "overview of immigrant/minority religions on the island of Ireland"),
 "We’re not right-wing or racist but": ("include", "protests around asylum-seeker accommodation in the Republic of Ireland"),
 "Irish diaspora policy and soft power projection": ("include", "Irish State diaspora policy"),
 "“Ireland for the Irish”": ("include", "anti-immigrant far-right campaigning on Twitter in the 2020 Irish election"),
 "Root Shock as Social Discipline": ("include", "Irish social, asylum and refugee policy"),
 "Transformation of Migration Policy of the Republic of Ireland": ("include", "analysis of Irish migration policy after the 2023 Dublin riots"),
 "Valuing women’s spaces and communities": ("include", "refugee women's integration in Northern Ireland"),
 "Stories of hospitality": ("include", "action research with international protection applicants (Direct Provision) at an Irish University of Sanctuary"),
 "Spaces of teaching and (un)learning": ("include", "Irish Refugee Integration Network English classes at DCU"),
 "Higher Education Inclusion for Refugees and International Protection Applicants in Ireland": ("include", "refugee/IP applicant access to higher education in Ireland"),
 "Pregnancy and birth are uncertain anyway": ("include", "practitioner accounts on perinatal mental health of migrant women in ROI"),
 "Navigating the challenges of teaching about racism": ("include", "Irish social work education responding to migration-driven ethnic diversity"),
 "The EU’s New Asylum Pact and Ireland’s Opt-in": ("include", "legal/policy analysis of Ireland's opt-in to the 2024 EU asylum measures"),
 "Life as a Migrant Muslim Woman in Sectarian Northern Ireland": ("include", "migrant Muslim women in Northern Ireland"),
 "UKRAINIAN LANGUAGE IN THE MODERN LINGUISTIC LANDSCAPE OF IRELAND": ("include", "Ukrainian displaced population's language in Ireland's linguistic landscape"),
 "Bordering, belonging, beyond surviving": ("include", "migrant women settling in Ireland"),
 "Race, gender, and the immigrant student": ("include", "international/immigrant students in Irish universities"),
 "White (inter)nationalism, Europe": ("include", "anti-immigrant protest in Belfast after Southport (commentary)"),
 "‘What is your name?’ Migrant identity": ("include", "migrant political identity in Belfast"),
 "Dining With a New Partner?": ("include", "legal analysis of Ireland's opt-in to the EU Pact on Migration and Asylum"),
 "Understanding a Minority Group's (Roma) Experiences": ("include", "Roma (largely migrant-origin in Ireland) access to maternity services"),
 "Reclaiming Black Irish school narratives": ("include", "autoethnography of racialised (migrant-origin) schooling in Ireland"),
 "The politics of navigating complaint": ("include", "asylum seekers in Irish international protection accommodation during COVID-19"),
 "Building trust and warmth: Co-designing energy solutions": ("include", "co-design with asylum seekers/displaced communities in Ireland (MOBILISE)"),
 "‘Ireland is full’": ("include", "populist anti-immigrant mobilisation in Ireland"),
 "The coloniality of citizenship": ("include", "2004 Irish Citizenship Referendum"),
 "Nursing shortages and migration": ("include", "two-decade analysis of Ireland's dependence on migrant nurses"),
 "Mental Health Care for Forcibly Displaced Migrants in Ireland": ("include", "perspective review on mental health care for displaced migrants in Ireland"),
 "The 2004 Irish citizenship referendum: A case of stealth White supremacy": ("include", "2004 Irish Citizenship Referendum"),
 "The 2004 Citizenship Referendum: A pivotal moment": ("include", "2004 Irish Citizenship Referendum"),
 "From Bombay Street to Ballymena": ("include", "2025 anti-migrant riots in Ballymena, Northern Ireland"),
 # ---- no-empirical-signal bucket: historical appendix
 "Ireland and Argentina in the Twentieth Century": ("historical", "20th-century Irish diaspora in Argentina"),
 "La maldición de los Archer": ("historical", "17th-century Irish exiles in Bilbao"),
 "The Irish in Bolivia": ("historical", "history of Irish immigration to Bolivia"),
 "Networks between Ireland and the Irish American Diaspora during the Northern Ireland Peace": ("historical", "Irish-American diaspora networks, 1990s peace process"),
 "Putting Their Hands on Race": ("historical", "19th/20th-century Irish immigrant women in the US"),
 "Slow (Bio)archaeology": ("historical", "19th-century Irish immigrants (anatomical collection, US)"),
 "Positively Irish Action on AIDS": ("historical", "Irish diaspora in London, HIV activism (1980s-90s)"),
 "Irish Immigrants in the 1980s": ("historical", "Irish emigrants' immigration-reform advocacy in the US, 1980s"),
 "Bound for Australia": ("historical", "1840 Irish emigrant to Australia"),
 "Racialised from the past": ("historical", "Irish genealogies of Caribbean slavery"),
 # ---- partly-incidental bucket
 "The retention of training doctors in the Irish health system": ("include", "administrative data on trainee doctors leaving and returning to the Irish health system"),
 "We are always planning trips to Poland": ("include", "Polish transnational families in the Republic of Ireland"),
 "MIGRATION WORKERS IN NORTHERN IRELAND": ("include", "migrant workers and community inclusion in Northern Ireland"),
 "The Determinants of Brazilian Migration to Ireland": ("include", "interviews/questionnaires on Brazilian migration from Anápolis to Gort, Co. Galway"),
 "Romani in Ireland": ("include", "Romani language use and attitudes among Roma (migrant) speakers in Ireland"),
 "Crucifixes and Snowflakes": ("include", "children of migrant backgrounds in Irish schools"),
 "The development of host language achievement gaps by migration background": ("include", "Growing Up in Ireland longitudinal data (N=7,577) on host-language gaps by migration background"),
 "Penal Contradictions and the Pre-emptive Criminalisation": ("include", "Irish migration policy on 'marriages of convenience' and citizenship through marriage"),
 "Ethical dilemmas or uneasy situations?": ("include", "methodological reflection on fieldwork with male migrants in the UK and Ireland"),
 "Bad Bridget: Crime, Mayhem": ("exclude", "book review; no data"),
 "Bad Bridget—An unexplored aspect": ("historical", "museum exhibition on incarcerated Irish emigrant women (19th/20th c.)"),
 "Interaction between English and Irish as a Factor of Irish Migration": ("historical", "14th-15th century migration"),
 # ---- no-abstract bucket (decided on the title; no abstract exists in any index)
 "ListenHere: a CALL integration resource for migrants in Ireland": ("include", "language-learning integration resource for migrants in Ireland (title-only)"),
 "Selfies that Pay": ("include", "migrant male sex workers in Ireland (title-only)"),
 "Childcare Utilisation by Migration Background": ("include", "Irish cohort study of childcare use by migration background (title-only)"),
 "Comparing migrant integration in Ireland and Northern Ireland": ("include", "ESRI comparison of migrant integration, Ireland and NI (title-only)"),
 "Labour market integration of international protection applicants in Ireland": ("include", "ESRI study (title-only)"),
 "Post-school expectations and outcomes among migrant-origin young people in Ireland": ("include", "ESRI chapter (title-only)"),
 "Parental and professional perspectives on educational integration of migrant and refugee children in Ireland": ("include", "title-only"),
 "Second language identities among recently-arrived migrants in Dublin": ("include", "title-only"),
 "Migrant dermatology": ("include", "clinical experience with migrant patients in an Irish dermatology department (title-only)"),
 "Survey Experiments: Muslim Migrants in the United States, Ireland, and the Netherlands": ("include", "survey experiments incl. Ireland (cross-national; title-only)"),
 "School leaders' experiences and perceptions of the movement of Ukrainian child refugees": ("include", "title-only"),
 "The problems of emigration in the Republic of Ireland": ("include", "contemporary emigration and diaspora (title-only)"),
 "Pandemic Perspectives on the Irish Diaspora in Germany": ("include", "contemporary Irish emigrants in Germany (title-only)"),
 "Moving Through Ireland: Narratives of Polish Multiple Migrants": ("include", "title-only"),
 "If You Are Moving Forward Then You Are Not Going Backwards": ("include", "longitudinal study of Polish migrant families in Ireland (title-only)"),
 "Conclusion: Converging Paths and New Directions of Polish Migrant Families in Ireland": ("include", "conclusion of an Ireland-specific book on Polish migrant families (title-only)"),
 "Attitudes towards immigration and refugees in Ireland: Understanding recent trends": ("include", "ESRI report (title-only)"),
 "Sport, migration and national identity in contemporary Irish media": ("include", "media analysis (title-only)"),
 "The application of the temporary protection directive": ("include", "ESRI report (title-only)"),
 "Immigration and housing in the Republic of Ireland": ("include", "title-only"),
 "A field of broken dreams?": ("include", "male migrant footballers from Northern Ireland (emigration; title-only)"),
 "Strengthening supports for families living in international protection accommodation services": ("include", "families in IPAS (title-only)"),
 "From Emigration to National Resilience": ("include", "migration and identity in contemporary Ireland (title-only)"),
 "EU Medical Movers": ("include", "Polish migrants' transnational healthcare practices in Ireland (title-only)"),
 "Foregrounding loneliness of PhDing of a migrant woman academic": ("include", "autoethnography, Irish academia (title-only)"),
 "Ireland: immigration scuppers the Sinn Féin challenge": ("include", "immigration in the 2024 Irish general election (title-only)"),
 "Northern Ireland’s Migrant Muslim Population": ("include", "title-only"),
 "Chapter 2 Northern Ireland’s Migrant Muslim Population": ("exclude", "duplicate record of the same chapter"),
 "Immigrant optimism in Ireland": ("include", "parental educational expectations of immigrants in Ireland (title-only)"),
 "Barriers ethnic minority patients face communicating and accessing healthcare services in Ireland": ("include", "title-only"),
 "Ultra-Nationalism in Ireland: Anti-Immigration and the Response of the State": ("include", "title-only"),
 "THREE Ultra-Nationalism in Ireland": ("exclude", "duplicate record of the same chapter"),
 "Frames of forced migration": ("include", "political and media discourse, Italy and Ireland (cross-national; title-only)"),
 "Negotiating belonging through civic participation: Polish migrant workers in Northern Ireland": ("include", "title-only"),
 "Volunteering as a pathway to integration and belonging": ("include", "migrant experiences in Ireland (title-only)"),
 "Podcasting, Emigration, Return Migration": ("include", "emigration and return after 2008 (title-only)"),
 "The Impact of Demography and Migration on Employment in Ireland": ("include", "title-only"),
 "Home-school partnership with migrant families": ("include", "island of Ireland (title-only)"),
 "From Immigration to Integration: The Narrative of Afghan Elites in Ireland": ("include", "title-only"),
 "Humanism versus Educational Rights for Ukrainian Refugee Children in Ireland": ("include", "AERA 2026 paper (title-only)"),
 "Migrants and Migrations on the Island of Ireland Before and After Brexit": ("include", "title-only"),
 "Education of Newly Arrived Migrant Students in Sweden and Ireland": ("include", "cross-national incl. Ireland (title-only)"),
 "Ireland and Entrepreneurship: From Cultural Barriers to Diaspora-Driven Innovation": ("include", "diaspora (title-only)"),
 "Opponents of immigration in Ireland": ("include", "title-only"),
 "In Their Own Words: Muslim Migrant Women": ("include", "title-only"),
 "I wouldn’t say there’s outright racism": ("include", "Irish teachers and racism in schools (title-only)"),
 "Horizontal hostility among historically present Black Irish": ("include", "title-only"),
 "Do Indian migrant nurses in Ireland face elevated stress": ("include", "cross-sectional survey (title-only)"),
 "An Irish solution to an Irish problem": ("include", "migration marriage and citizenship in Ireland (title-only)"),
 "Migrant women in the Irish services sector": ("include", "title-only"),
 "Integrating Language, Art and Well-Being": ("include", "families seeking international protection in Ireland (title-only)"),
 "Migrants, Immigration and Diversity in Twentieth-century Northern Ireland: British, Irish or 'Other’?": ("historical", "20th-century NI immigration (book)"),
 "The Evolution of Northern Irish Immigration: Trends, Statistics and Demographics": ("historical", "chapter of the 20th-century NI immigration book"),
 "A Good Idea of Colonial Life": ("historical", "19th-century Irish migration to New Zealand"),
 "From Dublin to \"the Wild Western Desert\"": ("historical", "historical emigrant diary"),
 "The Emigrant Shipping News": ("historical", "historical emigration to London"),
 "Russian emigration in Ireland": ("historical", "mid-19th to mid-20th century"),
 "Radical Women of the Irish Diaspora": ("historical", "historical diaspora figures"),
 "The Irish Exodus—Emigration from Ireland Overseas": ("historical", "historical emigration to Britain"),
 "The Road to Migration": ("historical", "historical causes of emigration"),
 "The Immigration of Irish Lawyers to Australia in the 19th Century": ("historical", "19th century"),
 "Ireland, Argentina, and the Formation of a Southern Diaspora": ("historical", "historical diaspora"),
 "Rituals of migration: Italians and Irish on the move": ("historical", "historical migration"),
 "Death, Silence, and Belonging": ("historical", "Irish diaspora in Argentina"),
 "Irish Paupers in Scotland Between the Wars": ("historical", "interwar deportation and citizenship"),
 "Tables of Emigration from Irish Ports": ("historical", "19th-century primary source"),
 "Irish Immigration": ("historical", "19th-century primary source"),
 "Correspondence Relative to Recent Immigration of Destitute Irish": ("historical", "19th-century primary source"),
 "Emigration from Ireland": ("historical", "19th-century primary source"),
 # ---- corrections to RULE-based includes (spot-check of all 219; context of "Ireland" read in each abstract)
 "Millard, Candice River of the Gods": ("exclude", "book review; not about migration in Ireland"),
 "Early to Mid-Holocene Tree Immigration": ("exclude", "non-human: tree species colonisation"),
 "The Diaspora and Sociopolitical Mobilisations in Nigeria": ("exclude", "focus is Nigeria; Ireland only one respondent location"),
 "The Newfoundland and Labrador mosaic founder population": ("exclude", "population genetics of 18th-century settlers"),
 "Immigration and Entrepreneurship: The Role of Enclaves": ("exclude", "Irish Polish-immigration data used only as an instrument"),
 "Findings From the World Mental Health Surveys of Civil Violence": ("exclude", "not about migration"),
 "Ancestral Tourism: A Novel Market of Isfahan Tourism": ("exclude", "Iran; Ireland only in references"),
 "Restrictive points of entry into abortion care in Ireland": ("exclude", "abortion policy; migration not the subject"),
 "Refugee Chronicles: excerpt from the diary": ("exclude", "personal diary excerpt, not research"),
 "Editorial": ("exclude", "editorial; no data"),
 "Migration typology of the world’s coastal exclaves": ("exclude", "global typology; NI a passing example"),
 "Push and pull factors in return migration intentions among first‐generation Croa": ("exclude", "Croatian migrants in Germany; no Irish data"),
 "Female immigrant entrepreneurship – predicted by women’s empowerment": ("exclude", "pooled 25-country analysis; no Ireland-specific result"),
 "“Just a knife wound this week, nothing too painful”: An ethnographic": ("exclude", "duplicate record of the same study"),
 "A scoping review of academic and grey literature on migrant health research conducted in Scotland": ("exclude", "Scotland"),
 "Embodying intimate border violence": ("exclude", "no Irish data (Irish only in team description)"),
 "Ireland: Political Developments and Data in 2023": ("exclude", "annual political yearbook; migration incidental"),
 "Ethnicity and suicide in England and Wales": ("exclude", "England and Wales"),
 "Poor Employment Conditions and Immigrant Health in Europe": ("exclude", "pooled European analysis; no Ireland-specific result"),
 "ETHNICITY, MOTIVATION AND CULTURAL CAPITAL": ("exclude", "UK lifelong learning"),
 "Suicide literacy, suicide stigma, and help-seeking attitudes among men": ("exclude", "migration not the subject"),
 "Two Key Legal Issues for US Study Abroad in the EU": ("exclude", "US study-abroad law; not migration in Ireland"),
 "Fleshing Out the Invisible": ("exclude", "artistic practice; no data"),
 "AND EMPLOYMENT INNOVATIONS": ("exclude", "digital 'virtual emigration' policy; Ireland a passing case"),
 "Israelis abroad": ("exclude", "Israeli diaspora; Ireland only a statistic"),
 "ECONOMIC RESTRUCTURING AND MIGRATION ASSIMILATION IN THE EU": ("exclude", "pooled EU analysis; Ireland an example"),
 "MIGRANT ORGANIZATIONS AND THE PURSUIT FOR SOCIAL AND CULTURAL SECURITY": ("exclude", "overview across many countries"),
 "Cross-Border Migration: Challenges and Experiences of Nigerians in the United Ki": ("exclude", "UK-wide"),
 "Beyond trucks and tariffs": ("exclude", "border/Brexit, not migration"),
 "Addressing Gender Issues in Education, Training for Vietnam": ("exclude", "Vietnam"),
 "Comparative analysis of legal regulation of requirements for candidates for civil service": ("exclude", "not migration"),
 "Traces of the Past, Visions of the Future": ("exclude", "'Dublin' refers to the EU Dublin Regulation; not Ireland"),
 "Fruit and vegetable intake in minority ethnic groups in the UK": ("exclude", "UK"),
 "From Solidarity to Exclusion: The ‘Safe Country’ Concept in UK Asylum Law": ("exclude", "UK asylum law"),
 "Unemployment and attitudes to immigrants in Europe": ("exclude", "pooled European analysis; Ireland an example"),
 "Round table: Nationalism, populism and migrant healthcare workers": ("exclude", "conference round table; no data"),
 "Decent Pay and Access to Justice for Labour Migrants in the EAEU": ("exclude", "Eurasian Economic Union"),
 "396 WHO collaborating centre for participatory health research": ("exclude", "description of a research centre; no data"),
 "325 Music and singing as arts-based methods": ("exclude", "conference-abstract version of an included article"),
 "Distribution and naturalisation of Heterotheca subaxillaris": ("exclude", "non-human: plant in Morocco"),
 "How does mortality compare between different countries/regions of birth": ("exclude", "England and Wales"),
 "Regional language as heritage languages": ("exclude", "minority languages, not migration"),
 "Housing Shortage: A Serious Social Problem in Ireland": ("exclude", "general housing; migration incidental"),
 "Mapping Access to Abortion from Prisons and Immigration Removal Centres": ("exclude", "abortion access; UK-focused"),
 "Uptake of cervical screening and attitudes to HPV self-sampling in Irish Traveller": ("exclude", "Irish Travellers are an indigenous minority, not migrants"),
 "Empathy, Perceived Injustice and Solidarity‐Based Action": ("exclude", "not migration"),
 "Immigrant life expectancy and disability-free life expectancy": ("exclude", "England and Wales"),
 "Intersectional Barriers to Protection: Service Providers": ("exclude", "US/Canada providers; not migration in Ireland"),
 "A Corpus-Pragmatic Examination of the Mental Verb Think in Irish Emigrant": ("historical", "19th-century emigrant letters"),
 "Linguistic Perceptions of Irish English in Nineteenth-century Emigrant Letters": ("historical", "19th-century emigrant letters"),
 "CHARACTERISTICS OF IRISH IDENTITYAND THE PARTICIPATION OF THE IRISH DIASPORA": ("historical", "Irish-American politics, 19th-20th c."),
 "Travelling memories, the afterlife of feelings": ("historical", "Troubles-era emigrants from NI to Britain (oral history)"),
 "'I felt like I just belonged': urban multiculture and black Irish migrants": ("historical", "post-war Irish migrants in Britain"),
 "Anxieties of Belonging: Ulster Protestant Migrants": ("historical", "Ulster Protestant migrants in post-war England"),
 # ---- corrections found while reading abstracts for the synthesis
 "Resilience in the Face of War: a Collaborative Autoethnography": ("exclude", "set in Croatia; no Irish data"),
 "Ukraine Trauma Project": ("exclude", "trauma-care training inside Ukraine; not migration to Ireland"),
 "Refugees and Forced Displacement in Northern Ireland's Troubles": ("historical", "displacement during the Troubles (1969+)"),
 "Global Irish – Diversity of the diaspora": ("exclude", "geology: 'Irish-type' zinc-lead deposits; 'diaspora' is a metaphor"),
 "Ključni čimbenici iseljavanja iz Hrvatske": ("exclude", "emigration from Croatia; Ireland only named as a destination"),
 "Leveraging an intelligent career framework": ("exclude", "management briefing summarising others' research; no data"),
 "Finding home in Irish and German migrant letters": ("historical", "historical emigrant letters"),
}
DEFAULT_EXCLUDE_REVIEW = "reviewed: not about contemporary migration in Ireland, or no Irish data"

def ws(t):
    """Case- and whitespace-insensitive form: titles contain non-breaking and em spaces."""
    return re.sub(r"\s+", " ", t or "").strip().lower()


out, used = [], set()
for frag, (dec, why) in DEC.items():
    # an exact title match wins (e.g. a book vs. a "Book review of <book>")
    hits = [x for x in rev if ws(x["title"]) == ws(frag)] or \
           [x for x in rev if ws(frag) in ws(x["title"])]
    if len(hits) != 1:
        sys.exit(f"fragment matches {len(hits)} records, must be exactly 1: {frag!r}")
    used.add(hits[0]["url"])
    out.append({"url": hits[0]["url"], "decision": dec, "reason": why, "stage": "2-broad",
                "decided_by": "manual review of abstract", "date": "2026-09-26"})

# Everything else still in the review set from the two buckets reviewed here
# Idempotent: decide from the RULE reasons (the text before any "MANUAL:" note),
# not from the current status - after one run these records are no longer
# "review", and they must not silently fall back to review on the next run.
for x in rev:
    if x["url"] in used:
        continue
    rs = x["reasons"].split("MANUAL:")[0]
    if "literary" in rs or "historical study" in rs:
        continue                                 # already decided by rule
    if "only ambiguous" in rs:
        out.append({"url": x["url"], "decision": "exclude",
                    "reason": "no unambiguous migration term; not about migration (checked by title)",
                    "stage": "2-broad", "decided_by": "manual review of title list", "date": "2026-09-26"})
    elif "partly incidental" in rs:
        out.append({"url": x["url"], "decision": "exclude", "reason": "reviewed: migration incidental or not about Ireland",
                    "stage": "2-broad", "decided_by": "manual review of abstract", "date": "2026-09-26"})
    elif "no abstract" in rs and not any(k in rs for k in ("no Ireland reference", "no migration vocabulary", "non-human")):
        # only the no-abstract records the RULES sent to review (title had both a
        # migration term and an Ireland reference); rule-excluded ones stay rule-excluded
        out.append({"url": x["url"], "decision": "exclude",
                    "reason": "reviewed by title: book review, correction/commentary, or not contemporary migration in Ireland",
                    "stage": "2-broad", "decided_by": "manual review of title (no abstract available)", "date": "2026-09-26"})
    elif "no sign of empirical" in rs:
        out.append({"url": x["url"], "decision": "exclude", "reason": DEFAULT_EXCLUDE_REVIEW,
                    "stage": "2-broad", "decided_by": "manual review of title/abstract list", "date": "2026-09-26"})

mf = ROOT / "literature/manual_decisions.csv"
prev = [r for r in csv.DictReader(open(mf, encoding="utf-8")) if r["stage"] != "2-broad"] if mf.exists() else []
with open(mf, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["url", "decision", "reason", "stage", "decided_by", "date"])
    w.writeheader(); w.writerows(prev + out)
import collections
print(f"stage-2 decisions written: {len(out)}  {dict(collections.Counter(r['decision'] for r in out))}")

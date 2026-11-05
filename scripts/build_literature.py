"""Build process_safety/data/literature.json: the curated literature/source index. Edit ENTRIES, run, then run check_literature_urls.py.

kind: regulation | standard | guidance | investigation | database | journal | association | news | data-tool
read:  "text" (document text read for the toolkit) | "page" (the page/article read) | "no" (listed only; URL checked, not read)
access: free | paywalled | mixed
"""
import json
import os

E = []


def add(id, title, publisher, kind, url, access, read, topics, modules=(), note="", region="global"):
    E.append(dict(id=id, title=title, publisher=publisher, kind=kind, url=url, access=access, read=read, region=region,
                  topics=list(topics), modules=list(modules), note=note))


# ---- regulations and regulators
add("osha-1910-119", "29 CFR 1910.119 Process safety management of highly hazardous chemicals", "OSHA (US)", "regulation", "https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119", "free", "text", ["psm", "regulation"], ["psm"], "14 elements, Appendix A", "US")
add("osha-psm-home", "OSHA Process Safety Management topic page", "OSHA (US)", "guidance", "https://www.osha.gov/process-safety-management", "free", "no", ["psm", "regulation"], ["psm"], "enforcement directives and NEP are linked from here", "US")
add("epa-rmp", "EPA Risk Management Program (40 CFR 68)", "EPA (US)", "regulation", "https://www.epa.gov/rmp", "free", "text", ["rmp", "regulation", "consequence"], ["rmp"], "2026 revision proposal pending (see DESIGN_AWARENESS.md)", "US")
add("phmsa-home", "PHMSA pipeline and LNG safety", "PHMSA (US)", "regulation", "https://www.phmsa.dot.gov/", "free", "no", ["pipeline", "lng", "regulation"], ["pipeline", "lng"], "49 CFR 192/193 read; Oct 2026 LNG NPRM proposed", "US")
add("natlaw-phmsa-lng", "PHMSA proposes comprehensive revisions to safety regulations for LNG facilities", "National Law Review / Van Ness Feldman", "news", "https://natlawreview.com/article/phmsa-proposes-comprehensive-revisions-safety-regulations-lng-facilities", "free", "page", ["lng", "regulation"], ["lng"], "law-firm summary of the 28 Oct 2026 NPRM", "US")
add("seveso-iii", "Directive 2012/18/EU (Seveso III)", "European Union", "regulation", "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018", "free", "text", ["seveso", "regulation"], ["mah"], "Annex I parsed into data/seveso_iii_annex_i.json", "EU")
add("hse-comah", "COMAH Regulations 2015 guidance", "HSE (UK)", "regulation", "https://www.hse.gov.uk/comah/comah15.htm", "free", "page", ["comah", "regulation", "safety-case"], ["mah", "qra"], "", "UK")
add("hse-comah-home", "HSE COMAH home (Buncefield, competent authority material)", "HSE (UK)", "guidance", "https://www.hse.gov.uk/comah/", "free", "no", ["comah", "incident"], ["overfill"], "", "UK")
add("hse-hsg254", "HSG254 Developing process safety indicators", "HSE (UK)", "guidance", "https://www.hse.gov.uk/pubns/books/hsg254.htm", "mixed", "no", ["psm", "indicators", "management"], ["psm"], "", "UK")
add("hse-risk", "HSE risk management pages (ALARP, tolerability)", "HSE (UK)", "guidance", "https://www.hse.gov.uk/risk/", "free", "no", ["risk-criteria", "alarp", "qra"], ["qra"], "the R2P2 criteria used as QRA presets came from secondary sources; the old direct R2P2 URL returned 404 on 2026-11-06", "UK")
add("mom-mhi", "Major Hazard Installations: safety case regime", "Ministry of Manpower (Singapore)", "regulation", "https://www.mom.gov.sg/maintenance/workplace-safety-and-health/major-hazard-installations", "free", "page", ["safety-case", "regulation", "qra"], ["qra"], "", "SG")
add("safework-mhf", "Major hazard facilities", "Safe Work Australia", "guidance", "https://safeworkaustralia.gov.au/safety-topic/industry-and-business/major-hazard-facilities", "free", "no", ["safety-case", "regulation"], [], "fetch timed out on 2026-11-06; verify access", "AU")
add("nopsema", "NOPSEMA offshore safety case regime", "NOPSEMA (Australia)", "regulation", "https://www.nopsema.gov.au/", "free", "no", ["safety-case", "offshore", "regulation"], [], "", "AU")
add("oisd-standards", "OISD standards list (105 standards)", "OISD (India)", "standard", "https://www.oisd.gov.in/oisd-standards", "mixed", "page", ["india", "standards", "oil-gas"], ["standards"], "list and editions in data/oisd_standards.json; contents not read", "IN")
add("peso", "Petroleum and Explosives Safety Organisation", "PESO (India)", "regulation", "https://peso.gov.in/", "free", "no", ["india", "regulation", "explosives"], [], "", "IN")
add("pngrb", "Petroleum and Natural Gas Regulatory Board", "PNGRB (India)", "regulation", "https://www.pngrb.gov.in/", "free", "no", ["india", "regulation", "gas"], [], "", "IN")
add("dgfasli", "Directorate General Factory Advice Service and Labour Institutes", "DGFASLI (India)", "regulation", "https://dgfasli.gov.in/", "free", "no", ["india", "regulation", "factories"], [], "", "IN")
add("ilo-c174", "ILO Convention 174, Prevention of Major Industrial Accidents", "ILO", "regulation", "https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C174", "free", "no", ["regulation", "international"], [], "ratification counts differ between sources; check NORMLEX", "global")
add("oecd-chem-accidents", "OECD Guiding Principles for Chemical Accident Prevention, Preparedness and Response", "OECD", "guidance", "https://www.oecd.org/en/topics/chemical-accidents.html", "free", "no", ["international", "guidance", "psm"], [], "third edition supports the 2023 Council Recommendation", "global")
# ---- investigation bodies and incident databases
add("csb-investigations", "CSB investigations", "US Chemical Safety Board", "investigation", "https://www.csb.gov/investigations/", "free", "no", ["incident", "investigation"], ["psm", "overfill"], "CSB investigates and recommends; it does not regulate", "US")
add("csb-recommendations", "CSB recommendations", "US Chemical Safety Board", "investigation", "https://www.csb.gov/recommendations/", "free", "no", ["incident", "investigation"], [], "", "US")
add("emars", "eMARS major accident reporting system", "EU Joint Research Centre", "database", "https://emars.jrc.ec.europa.eu/", "free", "no", ["incident", "database", "seveso"], ["mah"], "", "EU")
add("aria", "ARIA accident database (BARPI)", "French Ministry of Ecological Transition", "database", "https://www.aria.developpement-durable.gouv.fr/", "free", "no", ["incident", "database"], [], "", "FR")
add("jpt-bp-oregon", "Investigators find operating, training deficiencies contributed to fatal refinery explosion", "Journal of Petroleum Technology (SPE)", "news", "https://jpt.spe.org/investigators-find-operating-training-deficiencies-contributed-to-fatal-refinery-explosion", "free", "page", ["incident", "overfill", "relief", "psm"], ["relief", "overfill"], "BP Oregon, Ohio 2022; OSHA findings", "US")
add("jpt-adnoc-psm", "Approach aims to prevent process safety incidents (ADNOC PSM framework)", "Journal of Petroleum Technology (SPE)", "news", "https://jpt.spe.org/approach-aims-to-prevent-process-safety-incidents", "free", "page", ["psm", "incident", "company"], ["psm"], "15 elements; 50+ event review; SPE paper 210971", "ME")
add("jpt-energy-transition", "Are process safety standards and practices ready for the energy transition?", "Journal of Petroleum Technology (SPE)", "news", "https://jpt.spe.org/are-process-safety-standards-and-practices-ready-for-the-energy-transition", "free", "no", ["psm", "management-of-change", "energy-transition"], [], "", "global")
# ---- associations, centres, journals
add("spe-focus-ps", "SPE In Focus: Process Safety", "Society of Petroleum Engineers", "association", "https://www.spe.org/en/focus/process-safety/", "free", "page", ["psm", "oil-gas"], [], "index of articles, papers on OnePetro (many paywalled)", "global")
add("afpm-ps", "AFPM process safety", "American Fuel & Petrochemical Manufacturers", "association", "https://www.afpm.org/issues/safety-health/process-safety", "free", "page", ["psm", "refining", "rmp"], ["rmp"], "industry-association position", "US")
add("ccps", "Center for Chemical Process Safety", "AIChE", "association", "https://www.aiche.org/ccps", "mixed", "no", ["psm", "guidelines", "rbps"], ["psm", "hazop", "sil"], "books are paywalled", "global")
add("ccps-beacon", "Process Safety Beacon", "CCPS", "news", "https://ccps.aiche.org/process-safety-beacon", "free", "no", ["incident", "awareness"], [], "returned a bot check (HTTP 403) on 2026-11-06; not read, no bypass", "global")
add("tamu-mkopsc", "Mary Kay O'Connor Process Safety Center", "Texas A&M University", "association", "https://psc.tamu.edu/", "free", "no", ["research", "psm"], [], "", "US")
add("icheme-safety", "IChemE Safety Centre", "IChemE", "association", "https://www.icheme.org/knowledge/safety-centre/", "mixed", "no", ["psm", "incident", "lessons"], [], "", "UK")
add("energy-inst", "Energy Institute technical publications", "Energy Institute", "association", "https://www.energyinst.org/technical", "mixed", "no", ["guidelines", "oil-gas", "psm"], [], "", "UK")
add("iogp-safety", "IOGP safety, including Life-Saving Rules and process safety reports", "IOGP", "association", "https://www.iogp.org/safety/", "free", "no", ["life-saving-rules", "psm", "oil-gas"], [], "", "global")
add("sigma-hse-articles", "Sigma-HSE news and insights", "Sigma-HSE", "news", "https://sigma-hse.com/news-insights/", "free", "page", ["psm", "hazop", "dust", "atex", "reaction-hazard"], ["atex", "reaction_hazard"], "titles only", "UK")
add("sigma-early-design", "Why are early-stage design decisions critical for process safety?", "Sigma-HSE", "news", "https://sigma-hse.com/news-insights/early-stage-design-decisions/", "free", "page", ["reaction-hazard", "design", "scale-up"], ["reaction_hazard", "thermal_runaway"], "statistics quoted by the article, not checked", "UK")
add("psmnews", "PSM News (James Klein)", "Process Safety Priorities LLC", "news", "https://psmnews.com/", "free", "page", ["psm", "blog"], [], "single-author blog; low weight; nothing used", "US")
add("jlppi", "Journal of Loss Prevention in the Process Industries", "Elsevier", "journal", "https://www.sciencedirect.com/journal/journal-of-loss-prevention-in-the-process-industries", "paywalled", "no", ["research", "consequence", "qra"], [], "", "global")
add("psep", "Process Safety and Environmental Protection", "Elsevier / IChemE", "journal", "https://www.sciencedirect.com/journal/process-safety-and-environmental-protection", "paywalled", "no", ["research", "psm"], [], "", "global")
add("psp", "Process Safety Progress", "AIChE / Wiley", "journal", "https://aiche.onlinelibrary.wiley.com/journal/15475913", "paywalled", "no", ["research", "psm"], [], "", "global")
# ---- data and tools used as references
add("coolprop", "CoolProp", "CoolProp project", "data-tool", "https://coolprop.org/", "free", "text", ["properties", "validation"], ["fluiddata", "props"], "MIT; source of data/fluid_screening.json and test oracle", "global")
add("fluids", "fluids (ChEDL)", "Caleb Bell", "data-tool", "https://fluids.readthedocs.io/", "free", "text", ["validation", "relief", "hydraulics"], ["relief", "hydraulics", "separator"], "MIT; test oracle only", "global")
add("thermo", "thermo (ChEDL)", "Caleb Bell", "data-tool", "https://thermo.readthedocs.io/", "free", "text", ["properties", "validation"], ["props"], "MIT; test oracle only", "global")
add("bibmon", "BibMon (Petrobras)", "Petrobras", "data-tool", "https://github.com/petrobras/BibMon", "free", "no", ["monitoring", "fault-detection"], [], "Apache-2.0; complementary, not integrated", "BR")
add("otsafe", "OTsafe", "p4lsec", "data-tool", "https://github.com/p4lsec/otsafe", "free", "no", ["ot-security", "safety-modelling"], [], "Apache-2.0; complementary, not integrated", "global")
add("doe-hdbk-1101", "DOE-HDBK-1101-96 Process safety management for highly hazardous chemicals", "US DOE", "guidance", "https://www.energy.gov/documents/doe-hdbk-1101-96", "free", "page", ["psm", "audit"], ["psm"], "", "US")
add("aiga-99", "AIGA 99/20 Process safety management", "AIGA", "guidance", "https://asiaiga.org/uploaded_docs/en_AIGA_99_20_Process_Safety_Mangement.pdf", "free", "page", ["psm"], ["psm"], "", "global")
add("cfr-193", "49 CFR 193 LNG facilities: federal safety standards", "eCFR", "regulation", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-D/part-193", "free", "text", ["lng", "regulation"], ["lng"], "current text; NPRM would replace", "US")
add("cfr-192", "49 CFR 192 Transportation of natural and other gas by pipeline", "eCFR", "regulation", "https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-D/part-192", "free", "text", ["pipeline", "regulation"], ["pipeline"], "", "US")

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "literature.json")
ids = [e["id"] for e in E]
assert len(ids) == len(set(ids)), "duplicate id"
json.dump({"compiled": "2026-11-06", "note": "read=text/page means that material was read for the toolkit; read=no means the URL was checked but the content was not read.", "entries": E}, open(out, "w"), indent=1)
print("wrote", len(E), "entries")

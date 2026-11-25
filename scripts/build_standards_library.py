"""Build process_safety/data/standards_library.json: a catalogue of process-safety and design standards, codes, regulations,
guidance, books, databases and journals, with links.

The catalogue is an index only. No third-party text is copied into the repository, and only publisher, regulator or other
rights-holder pages are linked (no unofficial copies of paid standards).

Row format inside each group: "designation | title | note" (note optional). An ASTM title is left empty here on purpose:
scripts/check_standards_library.py reads it from the ASTM page. Editions are deliberately not recorded; confirm the current one.

Re-running keeps the link-check results already in the JSON for rows whose URL is unchanged.
Standard library only.
"""
import json
import os
import re
from urllib.parse import quote

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "standards_library.json")

ENTRIES: list[dict] = []


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def add(category, body, rows, url=None, access="paid", kind="standard", region="global", link="catalogue", tags=""):
    """url: a fixed string, or a callable(designation) -> str. link='document' means the URL is specific to that row."""
    for line in rows.strip().splitlines():
        parts = [p.strip() for p in line.split("|")]
        desig, title = parts[0], parts[1] if len(parts) > 1 else ""
        note = parts[2] if len(parts) > 2 else ""
        u = url(desig) if callable(url) else url
        ENTRIES.append({"id": slug(f"{body}-{desig}")[:90], "designation": desig, "title": title, "body": body,
                        "category": category, "kind": kind, "access": access, "region": region, "url": u, "link": link,
                        "topics": [t for t in tags.split() if t], "note": note})


def doc(category, body, rows, access="free", kind="guidance", region="global", tags=""):
    """Rows with their own URL: 'designation | title | url | note'."""
    for line in rows.strip().splitlines():
        parts = [p.strip() for p in line.split("|")]
        desig, title, u = parts[:3]
        note = parts[3] if len(parts) > 3 else ""
        ENTRIES.append({"id": slug(f"{body}-{desig}")[:90], "designation": desig, "title": title, "body": body,
                        "category": category, "kind": kind, "access": access, "region": region, "url": u,
                        "link": "document", "topics": [t for t in tags.split() if t], "note": note})


# ---------------------------------------------------------------------------------------------------------------- publisher links
# Dual-unit (inch-pound / SI) ASTM standards live at /standards/<code>_<code>m (found by the link check, 2026-11-25).
ASTM_DUAL = set("""
a1016 a105 a123 a153 a178 a179 a181 a182 a192 a194 a197 a20 a202 a203 a204 a209 a210 a213 a214 a216 a217 a225
a234 a240 a249 a250 a266 a268 a278 a283 a299 a302 a312 a320 a334 a335 a336 a350 a351 a352 a353 a358 a36 a369
a376 a387 a388 a395 a403 a409 a420 a435 a437 a450 a453 a47 a479 a480 a484 a487 a494 a508 a515 a516 a517 a522
a530 a533 a537 a540 a542 a543 a553 a564 a571 a577 a578 a6 a609 a638 a645 a653 a662 a675 a688 a694 a707 a727
a737 a744 a745 a774 a789 a790 a803 a815 a841 a860 a890 a913 a928 a962 a965 a992 a999 b152 b171 b241 b26 b345
b466 b491 b523 b547 b550 b551 b658 d2846 e2905 f1959 f2675 f441
""".split())


def astm(category, codes, tags=""):
    for c in codes.split():
        add(category, "ASTM", f"ASTM {c.upper()}", url=f"https://store.astm.org/standards/{c.lower()}" + (f"_{c.lower()}m" if c.lower() in ASTM_DUAL else ""), link="document", tags=tags)


def nfpa_url(d):
    n = re.sub(r"[^0-9A-Z]", "", d.replace("NFPA", "").strip()).lower()
    return f"https://www.nfpa.org/codes-and-standards/nfpa-{n}-standard-development/{n}"


def nfpa(category, rows, tags=""):
    add(category, "NFPA", rows, url=nfpa_url, access="mixed", link="document", tags=tags + " nfpa")


API = "https://publications.api.org/"
ASME = "https://www.asme.org/codes-standards"
ISO = lambda d: "https://www.iso.org/search.html?q=" + quote(d)
IEC = "https://webstore.iec.ch/"
ISA = "https://www.isa.org/standards-and-publications/isa-standards"
EN = "https://standards.cencenelec.eu/"
CCPS = "https://www.aiche.org/ccps/publications"
ICHEME = "https://www.icheme.org/"
EI = "https://www.energyinst.org/technical/publications"
IOGP = "https://www.iogp.org/bookstore/"
AMPP = "https://www.ampp.org/standards"
EIGA = "https://www.eiga.eu/publications/"
CGA = "https://portal.cganet.com/Publication/index.aspx"
NORSOK = "https://standard.no/en/sectors/petroleum/norsok-standards/"
DNV = "https://www.dnv.com/rules-standards/"
OISD = "https://www.oisd.gov.in/"
BIS = "https://standards.bis.gov.in/"
EEMUA = "https://www.eemua.org/"
PNGRB = "https://www.pngrb.gov.in/"
PESO = "https://peso.gov.in/"

# ================================================================================================ regulations by jurisdiction
doc("regulation", "OSHA", """
29 CFR 1910.119 | Process safety management of highly hazardous chemicals | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119
29 CFR 1910.106 | Flammable liquids | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.106
29 CFR 1910.109 | Explosives and blasting agents | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.109
29 CFR 1910.110 | Storage and handling of liquefied petroleum gases | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.110
29 CFR 1910.111 | Storage and handling of anhydrous ammonia | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.111
29 CFR 1910.103 | Hydrogen | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.103
29 CFR 1910.104 | Oxygen | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.104
29 CFR 1910.120 | Hazardous waste operations and emergency response | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.120
29 CFR 1910.146 | Permit-required confined spaces | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.146
29 CFR 1910.147 | Control of hazardous energy (lockout/tagout) | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147
29 CFR 1910.252 | Welding, cutting and brazing: general requirements | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.252
29 CFR 1910.307 | Hazardous (classified) locations | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.307
29 CFR 1910.1200 | Hazard communication | https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1200
""", kind="regulation", region="US", tags="psm osha")
add("regulation", "EPA", """
40 CFR Part 68 | Chemical accident prevention provisions (Risk Management Program) |
40 CFR Part 112 | Oil pollution prevention (SPCC) |
40 CFR Part 355 | Emergency planning and notification (EPCRA) |
""", url="https://www.ecfr.gov/current/title-40", access="free", kind="regulation", region="US", tags="rmp environment")
add("regulation", "PHMSA", """
49 CFR Part 192 | Transportation of natural and other gas by pipeline: minimum federal safety standards |
49 CFR Part 193 | Liquefied natural gas facilities: federal safety standards |
49 CFR Part 195 | Transportation of hazardous liquids by pipeline |
49 CFR Parts 171-180 | Hazardous materials regulations (transport) |
""", url="https://www.ecfr.gov/current/title-49", access="free", kind="regulation", region="US", tags="pipeline transport lng")
add("regulation", "USCG", """
33 CFR Part 127 | Waterfront facilities handling LNG and liquefied hazardous gas |
""", url="https://www.ecfr.gov/current/title-33", access="free", kind="regulation", region="US", tags="lng marine")
doc("regulation", "EU", """
Directive 2012/18/EU | Control of major-accident hazards involving dangerous substances (Seveso III) | https://eur-lex.europa.eu/eli/dir/2012/18/oj
Directive 2014/34/EU | Equipment and protective systems for potentially explosive atmospheres (ATEX equipment) | https://eur-lex.europa.eu/eli/dir/2014/34/oj
Directive 1999/92/EC | Protection of workers at risk from explosive atmospheres (ATEX workplace) | https://eur-lex.europa.eu/eli/dir/1999/92/oj
Directive 2014/68/EU | Pressure Equipment Directive | https://eur-lex.europa.eu/eli/dir/2014/68/oj
Directive 2006/42/EC | Machinery Directive | https://eur-lex.europa.eu/eli/dir/2006/42/oj | Being replaced by Regulation (EU) 2023/1230.
Regulation (EU) 2023/1230 | Machinery Regulation | https://eur-lex.europa.eu/eli/reg/2023/1230/oj
Directive 98/24/EC | Chemical agents at work | https://eur-lex.europa.eu/eli/dir/1998/24/oj
Directive 89/391/EEC | Framework directive on safety and health at work | https://eur-lex.europa.eu/eli/dir/1989/391/oj
Directive 2013/30/EU | Safety of offshore oil and gas operations | https://eur-lex.europa.eu/eli/dir/2013/30/oj
Regulation (EC) 1272/2008 | Classification, labelling and packaging (CLP) | https://eur-lex.europa.eu/eli/reg/2008/1272/oj
Regulation (EC) 1907/2006 | REACH | https://eur-lex.europa.eu/eli/reg/2006/1907/oj
Directive (EU) 2022/2555 | NIS2 cybersecurity directive | https://eur-lex.europa.eu/eli/dir/2022/2555/oj
""", kind="regulation", region="EU", tags="seveso atex ped")
doc("regulation", "UK legislation", """
SI 2015/483 | Control of Major Accident Hazards Regulations 2015 (COMAH) | https://www.legislation.gov.uk/uksi/2015/483/contents
SI 2002/2776 | Dangerous Substances and Explosive Atmospheres Regulations 2002 (DSEAR) | https://www.legislation.gov.uk/uksi/2002/2776/contents
SI 2000/128 | Pressure Systems Safety Regulations 2000 | https://www.legislation.gov.uk/uksi/2000/128/contents
SI 1996/825 | Pipelines Safety Regulations 1996 | https://www.legislation.gov.uk/uksi/1996/825/contents
SI 2015/398 | Offshore Installations (Offshore Safety Directive) (Safety Case etc.) Regulations 2015 | https://www.legislation.gov.uk/uksi/2015/398/contents
SI 2015/51 | Construction (Design and Management) Regulations 2015 | https://www.legislation.gov.uk/uksi/2015/51/contents
""", kind="regulation", region="UK", tags="comah dsear pssr")
add("regulation", "India", """
MSIHC Rules 1989 | Manufacture, Storage and Import of Hazardous Chemicals Rules |
EPPR Rules 1996 | Chemical Accidents (Emergency Planning, Preparedness and Response) Rules |
""", url="https://moef.gov.in/", access="free", kind="regulation", region="IN", tags="msihc mah")
add("regulation", "India", """
Factories Act 1948 | Factories Act, including hazardous-process provisions (Chapter IVA) |
OSH Code 2020 | Occupational Safety, Health and Working Conditions Code, 2020 | Check which provisions and state rules are in force before relying on either law.
""", url="https://www.indiacode.nic.in/", access="free", kind="regulation", region="IN", tags="factories")
add("regulation", "PESO", """
SMPV(U) Rules 2016 | Static and Mobile Pressure Vessels (Unfired) Rules |
Petroleum Rules 2002 | Petroleum Rules |
Gas Cylinders Rules 2016 | Gas Cylinders Rules |
Explosives Rules 2008 | Explosives Rules |
Ammonium Nitrate Rules 2012 | Ammonium Nitrate Rules |
Calcium Carbide Rules 1987 | Calcium Carbide Rules |
""", url=PESO, access="free", kind="regulation", region="IN", tags="peso")
add("regulation", "PNGRB", """
PNGRB T4S: petroleum and gas installations | Technical standards and specifications including safety standards for refineries, terminals, pipelines and city gas distribution |
PNGRB ERDMP Regulations | Emergency response and disaster management plan regulations |
PNGRB Integrity Management System Regulations | Integrity management system for pipelines and city gas networks |
""", url=PNGRB, access="free", kind="regulation", region="IN", tags="pngrb pipeline cgd")
add("regulation", "CEA", """
CEA Safety Regulations | Central Electricity Authority (Measures relating to Safety and Electric Supply) Regulations |
""", url="https://cea.nic.in/", access="free", kind="regulation", region="IN", tags="electrical")
doc("regulation", "Other jurisdictions", """
Singapore MHI | Workplace Safety and Health (Major Hazard Installations) regime | https://www.mom.gov.sg/workplace-safety-and-health/major-hazard-installations
Australia MHF | Safe Work Australia: major hazard facilities | https://www.safeworkaustralia.gov.au/safety-topic/industry-and-business/major-hazard-facilities
Australia NOPSEMA | Offshore safety case regime | https://www.nopsema.gov.au/
Canada E2 | Environmental Emergency Regulations | https://laws-lois.justice.gc.ca/eng/regulations/SOR-2019-51/
Brazil NRs | Regulatory standards (NR-13 pressure equipment, NR-20 flammables, NR-33 confined spaces) | https://www.gov.br/trabalho-e-emprego/pt-br
Malaysia DOSH | Department of Occupational Safety and Health (CIMAH regulations) | https://www.dosh.gov.my/
Korea KOSHA | Korea Occupational Safety and Health Agency (PSM system and KOSHA guides) | https://www.kosha.or.kr/english/index.do
Japan KHK | High Pressure Gas Safety Institute of Japan | https://www.khk.or.jp/english/
China GB portal | National standards full-text disclosure system (GB standards) | https://openstd.samr.gov.cn/
Saudi HCIS | High Commission for Industrial Security (security and safety directives) | https://www.hcis.gov.sa/
Abu Dhabi OSHAD | Occupational safety and health system framework | https://www.adphc.gov.ae/
""", kind="regulation", region="intl", tags="jurisdiction")

# ================================================================================================ PSM frameworks and guidance
add("psm", "CCPS", """
CCPS RBPS | Guidelines for Risk Based Process Safety |
CCPS Management of Change | Guidelines for the Management of Change for Process Safety |
CCPS Process Safety Metrics | Guidelines for Process Safety Metrics |
CCPS Auditing | Guidelines for Auditing Process Safety Management Systems |
CCPS Incident Investigation | Guidelines for Investigating Process Safety Incidents |
CCPS Conduct of Operations | Conduct of Operations and Operational Discipline |
CCPS Asset Integrity | Guidelines for Asset Integrity Management |
CCPS Operating Procedures | Guidelines for Writing Effective Operating and Maintenance Procedures |
CCPS Pre-Startup | Guidelines for Performing Effective Pre-Startup Safety Reviews |
CCPS Emergency Planning | Guidelines for Technical Planning for On-Site Emergencies |
CCPS Engineering Design | Guidelines for Engineering Design for Process Safety |
CCPS Design Solutions | Guidelines for Design Solutions for Process Equipment Failures |
CCPS Safe Automation | Guidelines for Safe Automation of Chemical Processes |
CCPS Inherently Safer | Inherently Safer Chemical Processes: A Life Cycle Approach |
CCPS Capital Projects | Guidelines for Integrating Process Safety into Engineering Projects |
""", url=CCPS, kind="book", tags="psm ccps design")
doc("psm", "OSHA", """
OSHA 3132 | Process Safety Management (booklet) | https://www.osha.gov/sites/default/files/publications/osha3132.pdf
OSHA 3133 | Process Safety Management Guidelines for Compliance | https://www.osha.gov/sites/default/files/publications/osha3133.pdf
OSHA PSM topic page | Process safety management topic page, directives and emphasis programme | https://www.osha.gov/process-safety-management
""", region="US", tags="psm")
add("psm", "DOE", """
DOE-HDBK-1101 | Process Safety Management for Highly Hazardous Chemicals |
DOE-HDBK-1100 | Chemical Process Hazards Analysis |
DOE-STD-1189 | Integration of Safety into the Design Process |
DOE-STD-3009 | Preparation of nonreactor nuclear facility documented safety analysis |
DOE-HDBK-3010 | Airborne release fractions/rates and respirable fractions for nonreactor nuclear facilities |
""", url="https://www.standards.doe.gov/", access="free", kind="guidance", region="US", tags="psm design")
add("psm", "HSE", """
HSG65 | Managing for health and safety |
HSG254 | Developing process safety indicators |
HSG48 | Reducing error and influencing behaviour |
HSG253 | The safe isolation of plant and equipment |
HSG250 | Guidance on permit-to-work systems |
HSG176 | The storage of flammable liquids in tanks |
HSG51 | The storage of flammable liquids in containers |
HSG140 | Safe use and handling of flammable liquids |
HSG71 | Chemical warehousing: the storage of packaged dangerous substances |
HSG103 | Safe handling of combustible dusts |
HSG244 | Remotely operated shutoff valves (ROSOVs) for emergency isolation |
HSG143 | Designing and operating safe chemical reaction processes |
L111 | The Control of Major Accident Hazards Regulations 2015: guidance on regulations |
L138 | Dangerous substances and explosive atmospheres: approved code of practice and guidance |
L122 | Safety of pressure systems: approved code of practice |
INDG370 | Controlling fire and explosion risks in the workplace |
""", url=lambda d: f"https://www.hse.gov.uk/pubns/books/{d.lower()}.htm" if not d.startswith("INDG") else f"https://www.hse.gov.uk/pubns/{d.lower()}.htm",
    access="free", kind="guidance", region="UK", link="document", tags="hse")
doc("psm", "HSE", """
HSE COMAH | COMAH guidance pages | https://www.hse.gov.uk/comah/
HSE PCAG advice | Land use planning advice around major hazard sites | https://www.hse.gov.uk/landuseplanning/
HSE research reports | Research report series (RR) | https://www.hse.gov.uk/research/rrhtm/
""", region="UK", tags="hse comah")
doc("psm", "IFC / World Bank", """
IFC EHS Guidelines | Environmental, Health and Safety Guidelines (general and industry-sector) | https://www.ifc.org/content/dam/ifc/doc/2023/ifc-general-ehs-guidelines.pdf
""", tags="lender ehs")
doc("psm", "ILO", """
ILO C174 | Prevention of Major Industrial Accidents Convention | https://normlex.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C174
""", tags="international")
doc("psm", "OECD", """
OECD chemical accidents | Programme on chemical accidents: guiding principles for prevention, preparedness and response | https://www.oecd.org/en/topics/sub-issues/chemical-accidents.html
""", tags="international")
doc("psm", "UNECE", """
GHS (Purple Book) | Globally Harmonized System of Classification and Labelling of Chemicals | https://unece.org/about-ghs
UN Model Regulations (Orange Book) | Recommendations on the Transport of Dangerous Goods | https://unece.org/transport/dangerous-goods
UN Manual of Tests and Criteria | Test methods for classifying explosives, self-reactives, peroxides and flammables | https://unece.org/transport/dangerous-goods/un-manual-tests-and-criteria
TEIA Convention | Convention on the Transboundary Effects of Industrial Accidents | https://unece.org/environment-policy/industrial-accidents
""", tags="classification transport")
add("psm", "ISO", """
ISO 45001 | Occupational health and safety management systems |
ISO 14001 | Environmental management systems |
ISO 55001 | Asset management: management system requirements |
ISO 22301 | Business continuity management systems |
ISO 9001 | Quality management systems |
ISO 29001 | Quality management for the petroleum, petrochemical and natural gas industries |
""", url=ISO, tags="management-system")
add("psm", "API", """
API RP 754 | Process safety performance indicators for the refining and petrochemical industries |
API RP 75 | Safety and environmental management system for offshore operations and assets |
API RP 1173 | Pipeline safety management systems |
""", url=API, tags="psm api")
add("psm", "AIGA", """
AIGA 099 | Process safety management guideline for industrial gases |
""", url="https://www.asiaiga.org/", access="free", kind="guidance", tags="psm industrial-gas")
add("psm", "Energy Institute", """
EI PSM Framework | High level framework for process safety management |
""", url=EI, access="mixed", kind="guidance", tags="psm")
add("psm", "IOGP", """
IOGP 456 | Process safety: recommended practice on key performance indicators |
IOGP 510 | Operating Management System Framework |
IOGP 459 | Life-Saving Rules |
IOGP 415 | Asset integrity: the key to managing major incident risks |
IOGP 544 | Standardization of barrier definitions |
""", url=IOGP, access="free", kind="guidance", tags="psm barriers")

# ================================================================================================ hazard identification and risk
add("hazard-risk", "IEC", """
IEC 61882 | Hazard and operability studies (HAZOP studies): application guide |
IEC 60812 | Failure modes and effects analysis (FMEA and FMECA) |
IEC 61025 | Fault tree analysis |
IEC 62502 | Event tree analysis |
IEC 61078 | Reliability block diagrams |
IEC 61165 | Application of Markov techniques |
IEC 31010 | Risk management: risk assessment techniques |
IEC 62740 | Root cause analysis |
IEC 62508 | Guidance on human aspects of dependability |
""", url=IEC, tags="hazop fmea fta eta")
add("hazard-risk", "ISO", """
ISO 31000 | Risk management: guidelines |
ISO 17776 | Offshore installations: major accident hazard management during design |
ISO 12100 | Safety of machinery: risk assessment and risk reduction |
ISO 14224 | Collection and exchange of reliability and maintenance data for equipment |
ISO 20815 | Production assurance and reliability management |
""", url=ISO, tags="risk reliability")
add("hazard-risk", "CCPS", """
CCPS HEP | Guidelines for Hazard Evaluation Procedures |
CCPS CPQRA | Guidelines for Chemical Process Quantitative Risk Analysis |
CCPS LOPA | Layer of Protection Analysis: Simplified Process Risk Assessment |
CCPS IEs and IPLs | Guidelines for Initiating Events and Independent Protection Layers in LOPA |
CCPS Enabling Conditions | Guidelines for Enabling Conditions and Conditional Modifiers in LOPA |
CCPS Bow Ties | Bow Ties in Risk Management |
CCPS Risk Criteria | Guidelines for Developing Quantitative Safety Risk Criteria |
CCPS PERD | Guidelines for Process Equipment Reliability Data |
CCPS Revalidating PHA | Revalidating Process Hazard Analyses |
""", url=CCPS, kind="book", tags="lopa qra pha")
add("hazard-risk", "TNO / PGS", """
PGS 3 (CPR 18E) Purple Book | Guidelines for quantitative risk assessment |
PGS 4 (CPR 16E) Red Book | Methods for determining and processing probabilities |
PGS 1 (CPR 16) Green Book | Methods for the determination of possible damage to people and objects |
PGS 2 (CPR 14E) Yellow Book | Methods for the calculation of physical effects |
""", url="https://publicatiereeksgevaarlijkestoffen.nl/", access="free", kind="guidance", region="NL", tags="qra consequence frequency")
doc("hazard-risk", "RIVM", """
Reference Manual Bevi Risk Assessments | Dutch reference manual for quantitative risk assessment | https://www.rivm.nl/en
""", region="NL", tags="qra frequency")
add("hazard-risk", "IOGP", """
IOGP 434 series | Risk Assessment Data Directory (process release, ignition, vulnerability and other data sheets) | Some sheets have been revised or withdrawn; check the bookstore.
""", url=IOGP, access="free", kind="database", tags="qra frequency ignition")
add("hazard-risk", "SINTEF", """
PDS Data Handbook | Reliability data for safety equipment |
PDS Method Handbook | Reliability prediction method for safety instrumented systems |
""", url="https://www.sintef.no/en/", kind="database", region="NO", tags="sil reliability-data")
add("hazard-risk", "OREDA", """
OREDA Handbook | Offshore and onshore reliability data |
""", url="https://www.oreda.com/", kind="database", tags="reliability-data")
add("hazard-risk", "exida", """
exida SERH | Safety Equipment Reliability Handbook |
""", url="https://www.exida.com/", kind="database", tags="sil reliability-data")
add("hazard-risk", "Energy Institute", """
EI Ignition probability review | Model for estimating ignition probability (IP research report and look-up correlations) |
EI Bow tie guidance | Hazard management barrier model guidance (with CCPS) |
""", url=EI, access="mixed", kind="guidance", tags="ignition barriers")
add("hazard-risk", "NORSOK", """
NORSOK Z-013 | Risk and emergency preparedness assessment |
NORSOK Z-008 | Risk based maintenance and consequence classification |
""", url=NORSOK, access="mixed", region="NO", tags="qra offshore")

# ================================================================================================ functional safety, alarms, control, cyber
add("instrumented-safety", "IEC", """
IEC 61508 (all parts) | Functional safety of electrical/electronic/programmable electronic safety-related systems |
IEC 61511 (all parts) | Functional safety: safety instrumented systems for the process industry sector |
IEC 62061 | Safety of machinery: functional safety of safety-related control systems |
IEC 62682 | Management of alarm systems for the process industries |
IEC 62443 (series) | Security for industrial automation and control systems |
IEC TS 63069 | Framework for functional safety and security |
IEC 61513 | Nuclear power plants: instrumentation and control important to safety |
IEC 60534 (series) | Industrial-process control valves |
IEC 60584 | Thermocouples |
IEC 60529 | Degrees of protection provided by enclosures (IP code) |
""", url=IEC, tags="sil sis alarm cyber")
add("instrumented-safety", "ISA", """
ISA-84.00.01 | Functional safety: safety instrumented systems for the process industry sector (adoption of IEC 61511) |
ISA-TR84.00.02 | Safety integrity level verification of safety instrumented functions |
ISA-TR84.00.04 | Guidelines for implementation of ISA-84.00.01 |
ISA-TR84.00.07 | Guidance on the evaluation of fire, combustible gas and toxic gas system effectiveness |
ISA-18.2 | Management of alarm systems for the process industries |
ISA-101.01 | Human machine interfaces for process automation systems |
ISA-5.1 | Instrumentation symbols and identification |
ISA-62443 (series) | Security for industrial automation and control systems |
ISA-106 | Procedure automation for continuous process operations |
""", url=ISA, tags="sil alarm hmi fgs")
add("instrumented-safety", "API", """
API RP 554 | Process control systems |
API RP 551 | Process measurement |
API RP 556 | Instrumentation, control and protective systems for gas fired heaters |
API STD 670 | Machinery protection systems |
API RP 14C | Analysis, design, installation and testing of safety systems for offshore production facilities |
API STD 2350 | Overfill prevention for storage tanks in petroleum facilities |
""", url=API, tags="instrumentation overfill")
add("instrumented-safety", "EEMUA", """
EEMUA 191 | Alarm systems: a guide to design, management and procurement |
EEMUA 201 | Control rooms: a guide to their specification, design, commissioning and operation |
EEMUA 222 | Guide to the application of IEC 61511 |
""", url=EEMUA, tags="alarm hmi")
doc("instrumented-safety", "NIST", """
NIST SP 800-82 | Guide to Operational Technology (OT) Security | https://csrc.nist.gov/pubs/sp/800/82/r3/final | This link is Revision 3.
""", region="US", tags="cyber ot")
add("instrumented-safety", "NAMUR", """
NAMUR recommendations | Process automation worksheets and recommendations (e.g. NE 43, NE 107) |
""", url="https://www.namur.net/", access="mixed", kind="guidance", region="EU", tags="instrumentation")

# ================================================================================================ relief, flare, depressuring
add("relief-flare", "API", """
API STD 520 Part I | Sizing, selection and installation of pressure-relieving devices: sizing and selection |
API RP 520 Part II | Sizing, selection and installation of pressure-relieving devices: installation |
API STD 521 | Pressure-relieving and depressuring systems |
API STD 526 | Flanged steel pressure-relief valves |
API STD 527 | Seat tightness of pressure relief valves |
API STD 537 | Flare details for petroleum, petrochemical and natural gas industries |
API STD 2000 | Venting atmospheric and low-pressure storage tanks |
API RP 576 | Inspection of pressure-relieving devices |
""", url=API, tags="relief psv flare tank-venting")
add("relief-flare", "ISO", """
ISO 4126 (all parts) | Safety devices for protection against excessive pressure |
ISO 28300 | Venting of atmospheric and low-pressure storage tanks |
""", url=ISO, tags="relief")
add("relief-flare", "ASME", """
ASME BPVC XIII | Rules for overpressure protection |
ASME PTC 25 | Pressure relief devices: performance test codes |
""", url=ASME, tags="relief")
add("relief-flare", "DIERS / CCPS", """
CCPS Pressure Relief and Effluent Handling | Guidelines for Pressure Relief and Effluent Handling Systems |
DIERS Project Manual | Emergency relief system design using DIERS technology |
""", url=CCPS, kind="book", tags="relief diers two-phase runaway")
add("relief-flare", "AIChE DIERS", """
DIERS Users Group | Design Institute for Emergency Relief Systems users group |
""", url="https://www.aiche.org/diers", access="mixed", kind="association", tags="relief two-phase")
add("relief-flare", "EEMUA", """
EEMUA 231 | Mechanical integrity of plant containing hazardous substances: a guide to periodic examination and testing |
""", url=EEMUA, tags="integrity inspection")

# ================================================================================================ pressure equipment, piping, tanks, rotating
add("equipment-codes", "ASME", """
ASME BPVC I | Rules for construction of power boilers |
ASME BPVC III | Rules for construction of nuclear facility components |
ASME BPVC IV | Rules for construction of heating boilers |
ASME BPVC VIII Div 1 | Rules for construction of pressure vessels |
ASME BPVC VIII Div 2 | Pressure vessels: alternative rules |
ASME BPVC VIII Div 3 | Pressure vessels: alternative rules for high pressure |
ASME BPVC X | Fiber-reinforced plastic pressure vessels |
ASME BPVC XII | Rules for construction and continued service of transport tanks |
ASME B31.1 | Power piping |
ASME B31.3 | Process piping |
ASME B31.4 | Pipeline transportation systems for liquids and slurries |
ASME B31.5 | Refrigeration piping and heat transfer components |
ASME B31.8 | Gas transmission and distribution piping systems |
ASME B31.8S | Managing system integrity of gas pipelines |
ASME B31.9 | Building services piping |
ASME B31.12 | Hydrogen piping and pipelines |
ASME B31G | Manual for determining the remaining strength of corroded pipelines |
ASME B16.5 | Pipe flanges and flanged fittings (NPS 1/2 through NPS 24) |
ASME B16.47 | Large diameter steel flanges |
ASME B16.9 | Factory-made wrought buttwelding fittings |
ASME B16.11 | Forged fittings, socket-welding and threaded |
ASME B16.20 | Metallic gaskets for pipe flanges |
ASME B16.21 | Nonmetallic flat gaskets for pipe flanges |
ASME B16.34 | Valves: flanged, threaded and welding end |
ASME B16.48 | Line blanks |
ASME B36.10M | Welded and seamless wrought steel pipe (dimensions) |
ASME B36.19M | Stainless steel pipe (dimensions) |
ASME B73.1 | Horizontal end suction centrifugal pumps for chemical process |
ASME B30 (series) | Cableways, cranes, derricks, hoists and related equipment |
ASME A13.1 | Scheme for the identification of piping systems |
ASME PCC-1 | Pressure boundary bolted flange joint assembly |
ASME PCC-2 | Repair of pressure equipment and piping |
ASME PCC-3 | Inspection planning using risk-based methods |
ASME BPE | Bioprocessing equipment |
ASME RTP-1 | Reinforced thermoset plastic corrosion-resistant equipment |
ASME NM.1 | Thermoplastic piping systems |
ASME STS-1 | Steel stacks |
""", url=ASME, tags="asme vessel piping valve flange")
add("equipment-codes", "API", """
API STD 650 | Welded tanks for oil storage |
API STD 620 | Design and construction of large, welded, low-pressure storage tanks |
API STD 625 | Tank systems for refrigerated liquefied gas storage |
API STD 2510 | Design and construction of LPG installations |
API STD 660 | Shell-and-tube heat exchangers |
API STD 661 | Air-cooled heat exchangers for general refinery service |
API STD 662 | Plate heat exchangers |
API STD 560 | Fired heaters for general refinery service |
API STD 530 | Calculation of heater-tube thickness in petroleum refineries |
API STD 610 | Centrifugal pumps for petroleum, petrochemical and natural gas industries |
API STD 617 | Axial and centrifugal compressors and expander-compressors |
API STD 618 | Reciprocating compressors |
API STD 619 | Rotary-type positive-displacement compressors |
API STD 674 | Positive displacement pumps: reciprocating |
API STD 675 | Positive displacement pumps: controlled volume |
API STD 676 | Positive displacement pumps: rotary |
API STD 685 | Sealless centrifugal pumps |
API STD 682 | Pumps: shaft sealing systems for centrifugal and rotary pumps |
API STD 614 | Lubrication, shaft-sealing and oil-control systems and auxiliaries |
API STD 612 | Special-purpose steam turbines |
API STD 616 | Gas turbines for the petroleum, chemical and gas industry services |
API STD 672 | Packaged, integrally geared centrifugal air compressors |
API STD 673 | Centrifugal fans |
API RP 686 | Machinery installation and installation design |
API SPEC 5L | Line pipe |
API SPEC 6A | Wellhead and tree equipment |
API SPEC 6D | Pipeline and piping valves |
API STD 594 | Check valves: flanged, lug, wafer and butt-welding |
API STD 598 | Valve inspection and testing |
API STD 599 | Metal plug valves |
API STD 600 | Steel gate valves with flanged and butt-welding ends |
API STD 602 | Compact steel gate, globe and check valves |
API STD 603 | Corrosion-resistant, bolted bonnet gate valves |
API STD 607 | Fire test for quarter-turn valves and valves with nonmetallic seats |
API SPEC 6FA | Fire test for valves |
API STD 608 | Metal ball valves |
API STD 609 | Butterfly valves |
API STD 623 | Steel globe valves |
API STD 624 | Type testing of rising stem valves with graphite packing for fugitive emissions |
API STD 641 | Type testing of quarter-turn valves for fugitive emissions |
API RP 14E | Design and installation of offshore production platform piping systems |
API RP 574 | Inspection practices for piping system components |
""", url=API, tags="api tank pump compressor valve heater")
add("equipment-codes", "TEMA", """
TEMA Standards | Standards of the Tubular Exchanger Manufacturers Association |
""", url="https://www.tema.org/", tags="heat-exchanger")
add("equipment-codes", "HEI", """
HEI Standards | Heat Exchange Institute standards (condensers, ejectors, deaerators) |
""", url="https://www.heatexchange.org/", tags="heat-exchanger")
add("equipment-codes", "Hydraulic Institute", """
ANSI/HI Pump Standards | Pump standards, including NPSH margin and intake design |
""", url="https://www.pumps.org/", tags="pump npsh")
add("equipment-codes", "MSS", """
MSS SP-6 | Standard finishes for contact faces of pipe flanges |
MSS SP-25 | Standard marking system for valves, fittings, flanges and unions |
MSS SP-44 | Steel pipeline flanges |
MSS SP-58 | Pipe hangers and supports: materials, design, manufacture, selection |
MSS SP-97 | Integrally reinforced forged branch outlet fittings |
""", url="https://msshq.org/", tags="piping valve")
add("equipment-codes", "EJMA", """
EJMA Standards | Standards of the Expansion Joint Manufacturers Association |
""", url="https://www.ejma.org/", tags="expansion-joint")
add("equipment-codes", "WRC", """
WRC 107 / 537 | Local stresses in shells due to external loadings on attachments |
WRC 297 | Local stresses in cylindrical shells due to external loadings on nozzles |
""", url="https://www.forengineers.org/", kind="guidance", tags="vessel stress")
add("equipment-codes", "EN", """
EN 13445 (series) | Unfired pressure vessels |
EN 13480 (series) | Metallic industrial piping |
EN 12952 (series) | Water-tube boilers |
EN 12953 (series) | Shell boilers |
EN 14015 | Site-built, vertical, cylindrical, flat-bottomed, above ground welded steel tanks |
EN 14620 (series) | Site-built tanks for refrigerated liquefied gases |
EN 1473 | Installation and equipment for LNG: design of onshore installations |
EN 764-7 | Pressure equipment: safety systems for unfired pressure equipment |
EN 1591-1 | Flanges and their joints: design rules for gasketed circular flange connections |
EN 1594 | Gas infrastructure: pipelines for maximum operating pressure over 16 bar |
""", url=EN, region="EU", tags="en ped vessel piping tank")
add("equipment-codes", "BSI", """
PD 5500 | Specification for unfired fusion welded pressure vessels |
BS 7910 | Guide to methods for assessing the acceptability of flaws in metallic structures |
BS EN 14161 / PD 8010 | Code of practice for pipelines |
""", url="https://knowledge.bsigroup.com/", region="UK", tags="vessel ffs pipeline")
add("equipment-codes", "UL", """
UL 142 | Steel aboveground tanks for flammable and combustible liquids |
UL 58 | Steel underground tanks for flammable and combustible liquids |
UL 2085 | Protected aboveground tanks for flammable and combustible liquids |
""", url="https://www.shopulstandards.com/", access="mixed", region="US", tags="tank")
add("equipment-codes", "AD 2000 / TRBS", """
AD 2000 Merkblatt | German pressure vessel code |
TRGS / TRBS | German technical rules for hazardous substances and operational safety | Free from BAuA.
""", url="https://www.baua.de/EN", access="mixed", region="EU", tags="germany vessel")
add("equipment-codes", "PIP", """
PIP Practices | Process Industry Practices (engineering practices for piping, vessels, instrumentation, civil and safety) |
""", url="https://www.pip.org/", tags="engineering-practice")

# ================================================================================================ mechanical integrity, inspection, FFS
add("integrity-inspection", "API", """
API 510 | Pressure vessel inspection code: in-service inspection, rating, repair and alteration |
API 570 | Piping inspection code: in-service inspection, rating, repair and alteration |
API STD 653 | Tank inspection, repair, alteration and reconstruction |
API RP 580 | Risk-based inspection |
API RP 581 | Risk-based inspection methodology |
API 579-1/ASME FFS-1 | Fitness-for-service |
API RP 571 | Damage mechanisms affecting fixed equipment in the refining industry |
API RP 572 | Inspection practices for pressure vessels |
API RP 573 | Inspection of fired boilers and heaters |
API RP 575 | Inspection practices for atmospheric and low-pressure storage tanks |
API RP 577 | Welding processes, inspection and metallurgy |
API RP 578 | Guidelines for a material verification program for new and existing assets |
API RP 583 | Corrosion under insulation and fireproofing |
API RP 584 | Integrity operating windows |
API RP 585 | Pressure equipment integrity incident investigation |
API RP 588 | Source inspection and quality surveillance of fixed equipment |
""", url=API, tags="inspection rbi ffs damage-mechanism")
add("integrity-inspection", "EEMUA", """
EEMUA 159 | Above ground flat bottomed storage tanks: a guide to inspection, maintenance and repair |
""", url=EEMUA, tags="tank inspection")
add("integrity-inspection", "NBBI", """
NBIC (NB-23) | National Board Inspection Code |
""", url="https://www.nationalboard.org/", region="US", tags="boiler vessel repair")
doc("integrity-inspection", "HSE", """
HSE technical measures: NDT | COMAH technical measures document on inspection and non-destructive testing | https://www.hse.gov.uk/comah/sragtech/techmeasndt.htm
""", region="UK", tags="inspection ageing")

# ================================================================================================ materials selection and corrosion
add("corrosion-materials-selection", "AMPP / ISO", """
NACE MR0175 / ISO 15156 | Materials for use in H2S-containing environments in oil and gas production |
NACE MR0103 / ISO 17945 | Metallic materials resistant to sulfide stress cracking in corrosive petroleum refining environments |
""", url=AMPP, tags="sour-service ssc h2s")
add("corrosion-materials-selection", "AMPP", """
NACE SP0472 | Methods and controls to prevent in-service environmental cracking of carbon steel weldments in refining |
NACE SP0198 | Control of corrosion under thermal insulation and fireproofing materials |
NACE SP0403 | Avoiding caustic stress corrosion cracking of carbon steel refinery equipment and piping |
NACE SP0169 | Control of external corrosion on underground or submerged metallic piping systems |
NACE SP0170 | Protection of austenitic stainless steels from polythionic acid stress corrosion cracking |
NACE SP0294 | Design, fabrication and inspection of storage tank systems for concentrated sulfuric acid and oleum |
NACE SP0502 | Pipeline external corrosion direct assessment methodology |
NACE SP0206 | Internal corrosion direct assessment for pipelines carrying normally dry natural gas |
NACE SP0775 | Preparation, installation, analysis and interpretation of corrosion coupons in oilfield operations |
NACE TM0177 | Laboratory testing of metals for resistance to sulfide stress cracking and stress corrosion cracking in H2S |
NACE TM0284 | Evaluation of pipeline and pressure vessel steels for resistance to hydrogen-induced cracking |
NACE TM0316 | Four-point bend testing of materials for oil and gas applications |
NACE 34101 | Refinery injection and process mix points |
""", url=AMPP, tags="corrosion ampp")
add("corrosion-materials-selection", "API", """
API RP 941 | Steels for hydrogen service at elevated temperatures and pressures in petroleum refineries and petrochemical plants |
API RP 939-C | Guidelines for avoiding sulfidation corrosion failures in oil refineries |
API RP 932-B | Design, materials, fabrication, operation and inspection guidelines for corrosion control in hydroprocessing reactor effluent air cooler systems |
API RP 934 (series) | Materials and fabrication of 1.25Cr, 2.25Cr and 3Cr steel heavy wall pressure vessels for high-temperature, high-pressure hydrogen service |
API RP 945 | Avoiding environmental cracking in amine units |
API RP 751 | Safe operation of hydrofluoric acid alkylation units |
API RP 970 | Corrosion control documents |
API RP 582 | Welding guidelines for the chemical, oil and gas industries |
API TR 938-B | Use of 9Cr-1Mo-V steel in the refining industry |
API TR 938-C | Use of duplex stainless steels in the oil refining industry |
API RP 2611 | Terminal piping inspection |
""", url=API, tags="htha sulfidation amine hf corrosion")
add("corrosion-materials-selection", "ASME", """
ASME BPVC II Part A | Materials: ferrous material specifications (SA) |
ASME BPVC II Part B | Materials: nonferrous material specifications (SB) |
ASME BPVC II Part C | Materials: specifications for welding rods, electrodes and filler metals (SFA) |
ASME BPVC II Part D | Materials: properties (allowable stresses, external pressure charts) |
""", url=ASME, tags="materials allowable-stress")
add("corrosion-materials-selection", "ISO", """
ISO 21457 | Materials selection and corrosion control for oil and gas production systems |
ISO 23936 (series) | Non-metallic materials in contact with media related to oil and gas production |
ISO 15649 | Petroleum and natural gas industries: piping |
ISO 12944 (series) | Corrosion protection of steel structures by protective paint systems |
ISO 8501-1 | Preparation of steel substrates: visual assessment of surface cleanliness |
ISO 19840 | Protective paint systems: measurement of dry film thickness |
ISO 9223 | Corrosivity of atmospheres: classification |
ISO 15589-1 | Cathodic protection of pipeline systems: on-land pipelines |
ISO 11114 (series) | Gas cylinders: compatibility of cylinder and valve materials with gas contents |
""", url=ISO, tags="materials coating compatibility")
add("corrosion-materials-selection", "NORSOK", """
NORSOK M-001 | Materials selection |
NORSOK M-501 | Surface preparation and protective coating |
NORSOK M-601 | Welding and inspection of piping |
NORSOK M-630 | Material data sheets and element data sheets for piping |
NORSOK M-650 | Qualification of manufacturers of special materials |
NORSOK M-710 | Qualification of non-metallic materials and manufacturers |
NORSOK M-101 | Structural steel fabrication |
NORSOK M-120 | Material data sheets for structural steel |
NORSOK M-506 | CO2 corrosion rate calculation model |
""", url=NORSOK, access="mixed", region="NO", tags="materials norsok offshore")
add("corrosion-materials-selection", "DNV", """
DNV-RP-O501 | Managing sand production and erosion |
DNV-RP-F101 | Corroded pipelines |
DNV-RP-F112 | Duplex stainless steel: design against hydrogen induced stress cracking |
DNV-RP-B401 | Cathodic protection design |
""", url=DNV, access="free", kind="guidance", tags="erosion corrosion")
add("corrosion-materials-selection", "EN", """
EN 10028 (series) | Flat products made of steels for pressure purposes |
EN 10216 (series) | Seamless steel tubes for pressure purposes |
EN 10217 (series) | Welded steel tubes for pressure purposes |
EN 10222 (series) | Steel forgings for pressure purposes |
EN 10213 | Steel castings for pressure purposes |
EN 10204 | Metallic products: types of inspection documents (material certificates) |
EN 1092-1 | Flanges: steel flanges, PN designated |
EN 10269 | Steels and nickel alloys for fasteners with specified elevated and low temperature properties |
EN 10088 (series) | Stainless steels |
""", url=EN, region="EU", tags="materials en")
add("corrosion-materials-selection", "MTI", """
MTI publications | Materials Technology Institute guidance for the chemical process industries |
""", url="https://www.mti-global.org/", access="mixed", kind="guidance", tags="materials chemical")
add("corrosion-materials-selection", "Nickel Institute", """
Nickel Institute guides | Technical guides on stainless steels and nickel alloys in corrosive service |
""", url="https://nickelinstitute.org/en/library/", access="free", kind="guidance", tags="stainless nickel")
add("corrosion-materials-selection", "Euro Chlor", """
Euro Chlor GEST publications | Chlorine industry materials, equipment and safety recommendations |
""", url="https://www.eurochlor.org/", access="mixed", kind="guidance", region="EU", tags="chlorine materials")

# ------------------------------------------------------------------------------------------------ ASTM material specifications
astm("astm-pipe-tube", "a53 a106 a312 a333 a335 a358 a369 a376 a381 a409 a524 a671 a672 a691 a790 a928 a999 a530", "pipe steel")
astm("astm-pipe-tube", "a178 a179 a192 a209 a210 a213 a214 a249 a250 a268 a269 a270 a334 a450 a688 a789 a803 a1016", "tube boiler exchanger")
astm("astm-plate-structural", "a6 a20 a36 a202 a203 a204 a225 a240 a263 a264 a265 a283 a285 a299 a302 a353 a387 a480 a515 a516 a517 a533 a537 a542 a543 a553 a578 a612 a645 a662 a737 a841", "plate vessel-steel")
astm("astm-plate-structural", "a123 a153 a435 a500 a501 a572 a588 a653 a913 a992", "structural coating")
astm("astm-forging-casting-fitting", "a105 a181 a182 a216 a217 a234 a266 a336 a350 a351 a352 a403 a420 a487 a494 a508 a522 a694 a707 a727 a744 a774 a815 a860 a890 a961 a965 a995", "flange fitting forging casting")
astm("astm-forging-casting-fitting", "a47 a48 a126 a197 a278 a395 a536 a571", "cast-iron ductile-iron")
astm("astm-bolting-bar", "a193 a194 a276 a307 a320 a354 a437 a449 a453 a479 a484 a540 a563 a564 a574 a638 a675 a696 a962 a1014 f436 f467 f468 f593 f594 f606 f1554 f2281 f3125", "bolting bar fastener")
astm("astm-nonferrous", "b127 b160 b161 b162 b163 b164 b165 b166 b167 b168 b333 b335 b366 b407 b408 b409 b423 b424 b425 b434 b435 b443 b444 b446 b462 b463 b464 b468 b473 b514 b515 b564 b572 b573 b574 b575 b619 b622 b626 b637 b668 b673 b674 b675 b677 b704 b705 b709", "nickel-alloy")
astm("astm-nonferrous", "b265 b338 b348 b363 b367 b381 b861 b862 b863 b493 b523 b550 b551 b658", "titanium zirconium")
astm("astm-nonferrous", "b26 b209 b210 b211 b221 b234 b241 b247 b345 b361 b491 b547 b928", "aluminium")
astm("astm-nonferrous", "b42 b43 b61 b62 b68 b75 b88 b111 b148 b152 b169 b171 b280 b395 b466 b467 b543 b584 b819", "copper-alloy")
astm("astm-nonmetallic", "d1248 d1598 d1599 d1784 d1785 d2000 d2105 d2241 d2310 d2412 d2467 d2513 d2564 d2837 d2846 d2992 d2996 d2997 d3035 d3299 d3350 d3517 d3982 d4024 d4097 d5685 f423 f437 f438 f439 f441 f491 f492 f546 f714 f1055 f1281 f1545", "plastic frp lined-pipe")
astm("astm-nonmetallic", "d395 d412 d471 d573 d1149 d1329 d1418 d2240 f36 f37 f104 f146 f152", "elastomer gasket")
astm("astm-nonmetallic", "c167 c533 c547 c552 c591 c610 c692 c795 c871 c1055 c1057 c1617 e605 e736", "insulation cui burn-protection fireproofing")

# ------------------------------------------------------------------------------------------------ ASTM test methods
astm("astm-test-mechanical", "a370 a751 a941 e3 e8 e10 e18 e21 e23 e29 e45 e92 e112 e139 e140 e190 e208 e292 e384 e399 e407 e436 e466 e562 e606 e647 e1049 e1221 e1290 e1820 e1823 e1921 e415 e1086 e1476", "mechanical-test toughness fatigue pmi")
astm("astm-test-corrosion", "a262 a380 a763 a923 a967 a1084 b117 g1 g3 g4 g5 g15 g16 g28 g30 g31 g32 g34 g36 g37 g38 g39 g40 g41 g44 g46 g47 g48 g49 g51 g52 g57 g58 g59 g61 g64 g71 g73 g76 g78 g102 g106 g108 g110 g111 g123 g129 g150 g157 g170 g184 g185 g189 g192 g193 g199 g205", "corrosion-test scc pitting")
astm("astm-test-hydrogen-oxygen", "g63 g72 g74 g86 g88 g93 g94 g124 g125 g126 g128 g142 g146 g148 f519 f1459 f1624 f1940", "oxygen-compatibility hydrogen-embrittlement")
astm("astm-test-nde", "a388 a577 a609 a745 e94 e114 e125 e164 e165 e186 e213 e280 e309 e317 e426 e432 e446 e498 e499 e515 e543 e569 e650 e709 e797 e1002 e1003 e1030 e1067 e1118 e1139 e1316 e1417 e1419 e1444 e1962 e2007 e2096 e2375 e2491 e2700 e2884 e2905", "nde ultrasonic radiography leak-test acoustic-emission")
astm("astm-test-flammability-reactivity", "d56 d86 d92 d93 d240 d323 d1310 d2863 d2879 d2887 d3278 d3828 d3941 d4206 d4809 d5191 d6450 d7094 d7236", "flash-point vapour-pressure combustibility")
astm("astm-test-flammability-reactivity", "e476 e487 e537 e582 e659 e681 e698 e711 e918 e1226 e1231 e1232 e1445 e1491 e1515 e1641 e1981 e2012 e2019 e2021 e2046 e2070 e2079 e2550", "thermal-stability dust explosion mie kst loc autoignition")
astm("astm-test-fire", "e84 e108 e119 e136 e162 e648 e662 e814 e1317 e1321 e1354 e1529 e1537 e1623 e1725 e1966 e2032 e2058 e2174 e2307 e2393 e2652 e2768 d635 d1929 d3801 e759 e760 e761 e859 e937", "fire-test reaction-to-fire fire-resistance")
astm("astm-test-electrical-ppe", "d149 d257 d877 d1816 d120 f478 f496 f696 f855 f887 f1236 f1506 f1891 f1930 f1959 f2178 f2412 f2413 f2621 f2675 f2676 f2757 f739 f903 f1001 f1342 f2700 f2703 f2733", "electrical arc-flash chemical-protective-clothing ppe")
astm("astm-test-gas-analysis", "d1945 d1946 d3588 d4468 d5504 d6228 d7833", "gas-composition heating-value sulfur")

# ================================================================================================ welding, NDE qualification
add("welding-nde", "ASME", """
ASME BPVC V | Nondestructive examination |
ASME BPVC IX | Welding, brazing and fusing qualifications |
""", url=ASME, tags="welding nde")
add("welding-nde", "AWS", """
AWS D1.1 | Structural welding code: steel |
AWS D1.6 | Structural welding code: stainless steel |
AWS B2.1 | Welding procedure and performance qualification |
AWS D10.4 | Welding austenitic chromium-nickel stainless steel piping and tubing |
AWS A5 (series) | Filler metal specifications |
""", url="https://pubs.aws.org/", tags="welding")
add("welding-nde", "API", """
API STD 1104 | Welding of pipelines and related facilities |
API RP 2201 | Safe hot tapping practices in the petroleum and petrochemical industries |
API RP 2009 | Safe welding, cutting and hot work practices in the petroleum and petrochemical industries |
""", url=API, tags="welding hot-work hot-tap")
add("welding-nde", "ISO", """
ISO 15614 (series) | Specification and qualification of welding procedures: welding procedure test |
ISO 9606 (series) | Qualification testing of welders: fusion welding |
ISO 3834 (series) | Quality requirements for fusion welding of metallic materials |
ISO 5817 | Welding: quality levels for imperfections |
ISO 9712 | Non-destructive testing: qualification and certification of personnel |
ISO 17635 | Non-destructive testing of welds: general rules |
""", url=ISO, tags="welding nde")
add("welding-nde", "ASNT", """
ASNT SNT-TC-1A | Personnel qualification and certification in nondestructive testing |
""", url="https://www.asnt.org/", tags="nde")

# ================================================================================================ fire protection, detection, PFP
nfpa("fire-protection", """
NFPA 1 | Fire Code |
NFPA 10 | Portable Fire Extinguishers |
NFPA 11 | Low-, Medium-, and High-Expansion Foam |
NFPA 12 | Carbon Dioxide Extinguishing Systems |
NFPA 12A | Halon 1301 Fire Extinguishing Systems |
NFPA 13 | Installation of Sprinkler Systems |
NFPA 14 | Installation of Standpipe and Hose Systems |
NFPA 15 | Water Spray Fixed Systems for Fire Protection |
NFPA 16 | Installation of Foam-Water Sprinkler and Foam-Water Spray Systems |
NFPA 17 | Dry Chemical Extinguishing Systems |
NFPA 20 | Installation of Stationary Pumps for Fire Protection |
NFPA 22 | Water Tanks for Private Fire Protection |
NFPA 24 | Installation of Private Fire Service Mains and Their Appurtenances |
NFPA 25 | Inspection, Testing, and Maintenance of Water-Based Fire Protection Systems |
NFPA 72 | National Fire Alarm and Signaling Code |
NFPA 750 | Water Mist Fire Protection Systems |
NFPA 770 | Hybrid (Water and Inert Gas) Fire-Extinguishing Systems |
NFPA 2001 | Clean Agent Fire Extinguishing Systems |
NFPA 2010 | Fixed Aerosol Fire-Extinguishing Systems |
NFPA 80 | Fire Doors and Other Opening Protectives |
NFPA 101 | Life Safety Code |
NFPA 221 | High Challenge Fire Walls, Fire Walls, and Fire Barrier Walls |
NFPA 251 | Standard Methods of Tests of Fire Resistance of Building Construction and Materials | Withdrawn; shown for legacy references.
NFPA 600 | Facility Fire Brigades |
NFPA 1081 | Facility Fire Brigade Member Professional Qualifications |
NFPA 551 | Evaluation of Fire Risk Assessments |
NFPA 921 | Fire and Explosion Investigations |
NFPA 5000 | Building Construction and Safety Code |
""", "fire")
add("fire-protection", "API", """
API RP 2001 | Fire protection in refineries |
API RP 2021 | Management of atmospheric storage tank fires |
API RP 2030 | Application of fixed water spray systems for fire protection in the petroleum and petrochemical industries |
API RP 2218 | Fireproofing practices in petroleum and petrochemical processing plants |
API PUBL 2510A | Fire-protection considerations for the design and operation of LPG storage facilities |
API RP 14G | Fire prevention and control on open type offshore production platforms |
""", url=API, tags="fire pfp")
add("fire-protection", "ISO", """
ISO 13702 | Control and mitigation of fires and explosions on offshore production installations |
ISO 22899 (series) | Determination of the resistance to jet fires of passive fire protection materials |
ISO 834 (series) | Fire-resistance tests: elements of building construction |
ISO 20088 (series) | Resistance to cryogenic spillage of insulation materials |
ISO 10497 | Testing of valves: fire type-testing requirements |
ISO 7240 (series) | Fire detection and alarm systems |
ISO 14520 (series) | Gaseous fire-extinguishing systems |
""", url=ISO, tags="fire pfp jet-fire cryogenic")
add("fire-protection", "UL", """
UL 1709 | Rapid rise fire tests of protection materials for structural steel |
UL 263 | Fire tests of building construction and materials |
UL 162 | Foam equipment and liquid concentrates |
UL 521 | Heat detectors for fire protective signaling systems |
UL 2075 | Gas and vapor detectors and sensors |
""", url="https://www.shopulstandards.com/", access="mixed", region="US", tags="fire test listing")
add("fire-protection", "FM", """
FM Global Property Loss Prevention Data Sheets | Loss-prevention data sheets (e.g. DS 7-14 fire protection for chemical plants, DS 7-32 ignitable liquid operations, DS 7-45 safety controls and protective systems, DS 7-76 combustible dust) | Free with registration; confirm each data sheet number and title on the FM site.
""", url="https://www.fm.com/resources/fm-data-sheets", access="free-registration", kind="guidance", tags="fire loss-prevention insurance")
add("fire-protection", "Energy Institute", """
EI Model Code of Safe Practice Part 19 | Fire precautions at petroleum refineries and bulk storage installations |
EI Guidelines for design and protection against severe fires | Guidelines for the design and protection of pressure systems to withstand severe fires |
EI Guidance on passive fire protection | Availability and selection of passive and active fire protection for process equipment |
EI 15 | Model Code of Safe Practice Part 15: area classification for installations handling flammable fluids |
""", url=EI, access="mixed", kind="guidance", tags="fire pfp")
add("fire-protection", "EN", """
EN 1991-1-2 | Eurocode 1: actions on structures exposed to fire |
EN 1993-1-2 | Eurocode 3: design of steel structures, structural fire design |
EN 1363 (series) | Fire resistance tests |
EN 13501 (series) | Fire classification of construction products and building elements |
EN 54 (series) | Fire detection and fire alarm systems |
EN 12845 | Fixed firefighting systems: automatic sprinkler systems |
EN 13565 (series) | Fixed firefighting systems: foam systems |
""", url=EN, region="EU", tags="fire eurocode")
doc("fire-protection", "US NRC", """
NUREG-1805 | Fire Dynamics Tools: quantitative fire hazard analysis methods | https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1805/index.html
""", region="US", tags="fire-modelling")
doc("fire-protection", "NIST", """
FDS and Smokeview | Fire Dynamics Simulator and visualisation tool, with user and validation guides | https://pages.nist.gov/fds-smv/
""", kind="data-tool", region="US", tags="fire-modelling cfd")

# ================================================================================================ explosion, dust, deflagration
nfpa("explosion-dust", """
NFPA 67 | Explosion Protection for Gaseous Mixtures in Pipe Systems |
NFPA 68 | Explosion Protection by Deflagration Venting |
NFPA 69 | Explosion Prevention Systems |
NFPA 660 | Combustible Dusts and Particulate Solids | Consolidates the former NFPA 61, 484, 652, 654, 655 and 664 (2025 edition).
NFPA 652 | Fundamentals of Combustible Dust | Consolidated into NFPA 660; shown for legacy references.
NFPA 654 | Prevention of Fire and Dust Explosions from the Manufacturing, Processing, and Handling of Combustible Particulate Solids | Consolidated into NFPA 660; shown for legacy references.
NFPA 484 | Combustible Metals | Consolidated into NFPA 660; shown for legacy references.
NFPA 61 | Prevention of Fires and Dust Explosions in Agricultural and Food Processing Facilities | Consolidated into NFPA 660; shown for legacy references.
NFPA 664 | Prevention of Fires and Explosions in Wood Processing and Woodworking Facilities | Consolidated into NFPA 660; shown for legacy references.
NFPA 495 | Explosive Materials Code |
NFPA 85 | Boiler and Combustion Systems Hazards Code |
NFPA 86 | Ovens and Furnaces |
NFPA 87 | Fluid Heaters |
NFPA 91 | Exhaust Systems for Air Conveying of Vapors, Gases, Mists, and Particulate Solids |
""", "explosion dust")
add("explosion-dust", "EN", """
EN 1127-1 | Explosive atmospheres: explosion prevention and protection, basic concepts and methodology |
EN 14491 | Dust explosion venting protective systems |
EN 14994 | Gas explosion venting protective systems |
EN 14373 | Explosion suppression systems |
EN 14797 | Explosion venting devices |
EN 15089 | Explosion isolation systems |
EN 14460 | Explosion resistant equipment |
EN 14034 (series) | Determination of explosion characteristics of dust clouds |
EN 15967 | Determination of maximum explosion pressure and rate of pressure rise of gases and vapours |
EN 1839 | Determination of explosion limits and limiting oxygen concentration for gases and vapours |
""", url=EN, region="EU", tags="atex venting suppression isolation")
add("explosion-dust", "ISO / IEC", """
ISO/IEC 80079-20-2 | Explosive atmospheres: material characteristics, combustible dusts test methods |
IEC 80079-20-1 | Explosive atmospheres: material characteristics for gas and vapour classification |
ISO 16852 | Flame arresters: performance requirements, test methods and limits for use |
ISO 6184 (series) | Explosion protection systems |
""", url=ISO, tags="atex flame-arrester dust-test")
add("explosion-dust", "CCPS", """
CCPS VCE/BLEVE/Flash Fire | Guidelines for Vapor Cloud Explosion, Pressure Vessel Burst, BLEVE and Flash Fire Hazards |
CCPS Combustible Dust | Guidelines for Combustible Dust Hazard Analysis |
CCPS Deflagration and Detonation | Deflagration and detonation flame arresters (concept book) |
""", url=CCPS, kind="book", tags="vce bleve dust")
doc("explosion-dust", "US DoD", """
UFC 3-340-02 | Structures to Resist the Effects of Accidental Explosions | https://www.wbdg.org/dod/ufc/ufc-3-340-02
""", region="US", tags="blast structural")
add("explosion-dust", "ASCE", """
ASCE Blast Design | Design of Blast-Resistant Buildings in Petrochemical Facilities |
ASCE/SEI 59 | Blast protection of buildings |
ASCE/SEI 7 | Minimum design loads and associated criteria for buildings and other structures |
""", url="https://ascelibrary.org/", tags="blast structural loads")
add("explosion-dust", "FABIG", """
FABIG Technical Notes | Fire and Blast Information Group technical notes and guidance |
""", url="https://www.fabig.com/", access="mixed", kind="guidance", tags="fire blast offshore")
doc("explosion-dust", "IFA / DGUV", """
GESTIS-DUST-EX | Database of combustion and explosion characteristics of dusts | https://www.dguv.de/ifa/gestis/gestis-staub-ex/index-2.jsp
""", kind="database", region="EU", tags="dust kst mie")
doc("explosion-dust", "OSHA", """
OSHA combustible dust | Combustible dust topic page and guidance | https://www.osha.gov/combustible-dust
""", region="US", tags="dust")

# ================================================================================================ hazardous area, electrical, static, lightning
add("hazardous-area-electrical", "IEC", """
IEC 60079-0 | Explosive atmospheres: equipment, general requirements |
IEC 60079-1 | Equipment protection by flameproof enclosures "d" |
IEC 60079-2 | Equipment protection by pressurized enclosure "p" |
IEC 60079-7 | Equipment protection by increased safety "e" |
IEC 60079-10-1 | Classification of areas: explosive gas atmospheres |
IEC 60079-10-2 | Classification of areas: explosive dust atmospheres |
IEC 60079-11 | Equipment protection by intrinsic safety "i" |
IEC 60079-13 | Equipment protection by pressurized room "p" and artificially ventilated room "v" |
IEC 60079-14 | Electrical installations design, selection and erection |
IEC 60079-15 | Equipment protection by type of protection "n" |
IEC 60079-17 | Electrical installations inspection and maintenance |
IEC 60079-18 | Equipment protection by encapsulation "m" |
IEC 60079-19 | Equipment repair, overhaul and reclamation |
IEC 60079-25 | Intrinsically safe electrical systems |
IEC 60079-29 (series) | Gas detectors: performance, selection, installation, use and maintenance |
IEC 60079-31 | Equipment dust ignition protection by enclosure "t" |
IEC TS 60079-32-1 | Electrostatic hazards: guidance |
IEC 62305 (series) | Protection against lightning |
IEC 61936-1 | Power installations exceeding 1 kV a.c. |
IEC 60364 (series) | Low-voltage electrical installations |
IEC 61482 (series) | Live working: protective clothing against the thermal hazards of an electric arc |
""", url=IEC, tags="atex iecex electrical static lightning")
nfpa("hazardous-area-electrical", """
NFPA 70 | National Electrical Code |
NFPA 70B | Electrical Equipment Maintenance |
NFPA 70E | Electrical Safety in the Workplace |
NFPA 77 | Static Electricity |
NFPA 496 | Purged and Pressurized Enclosures for Electrical Equipment |
NFPA 497 | Classification of Flammable Liquids, Gases, or Vapors and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas |
NFPA 499 | Classification of Combustible Dusts and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas |
NFPA 780 | Installation of Lightning Protection Systems |
""", "electrical")
add("hazardous-area-electrical", "API", """
API RP 500 | Classification of locations for electrical installations at petroleum facilities classified as Class I, Division 1 and 2 |
API RP 505 | Classification of locations for electrical installations at petroleum facilities classified as Class I, Zone 0, 1 and 2 |
API RP 2003 | Protection against ignitions arising out of static, lightning and stray currents |
API RP 545 | Lightning protection of aboveground storage tanks for flammable or combustible liquids |
API RP 540 | Electrical installations in petroleum processing plants |
API RP 2216 | Ignition risk of hydrocarbon liquids and vapors by hot surfaces in the open air |
""", url=API, tags="area-classification static lightning ignition")
add("hazardous-area-electrical", "IEEE", """
IEEE 1584 | Guide for performing arc-flash hazard calculations |
IEEE 80 | Guide for safety in AC substation grounding |
IEEE 142 | Grounding of industrial and commercial power systems |
IEEE C2 | National Electrical Safety Code |
IEEE 242 | Protection and coordination of industrial and commercial power systems |
""", url="https://standards.ieee.org/", tags="arc-flash earthing protection")
doc("hazardous-area-electrical", "IECEx", """
IECEx system | International certification system for equipment used in explosive atmospheres, with certificate database | https://www.iecex.com/
""", kind="database", tags="certification")

# ================================================================================================ layout, siting, buildings, human factors
add("layout-human-factors", "API", """
API RP 752 | Management of hazards associated with location of process plant permanent buildings |
API RP 753 | Management of hazards associated with location of process plant portable buildings |
API RP 756 | Management of hazards associated with location of process plant tents |
API RP 755 | Fatigue risk management systems for personnel in the refining and petrochemical industries |
""", url=API, tags="facility-siting buildings fatigue")
add("layout-human-factors", "CCPS", """
CCPS Facility Siting | Guidelines for Siting and Layout of Facilities |
CCPS Occupied Buildings | Guidelines for Evaluating Process Plant Buildings for External Explosions, Fires, and Toxic Releases |
CCPS Human Factors | Human Factors Methods for Improving Performance in the Process Industries |
CCPS Human Reliability | Guidelines for Preventing Human Error in Process Safety |
""", url=CCPS, kind="book", tags="siting human-factors")
add("layout-human-factors", "GAPS / industry", """
GAP.2.5.2 | Oil and chemical plant layout and spacing | Insurer guideline (originally IRI/GE GAP, now AXA XL); obtain from the owner.
""", url="https://axaxl.com/", access="mixed", kind="guidance", tags="spacing insurance")
add("layout-human-factors", "ISO", """
ISO 15544 | Offshore production installations: emergency response requirements and guidelines |
ISO 11064 (series) | Ergonomic design of control centres |
ISO 7010 | Graphical symbols: registered safety signs |
ISO 14122 (series) | Safety of machinery: permanent means of access to machinery |
ISO 7731 | Danger signals for public and work areas |
ISO 9241 (series) | Ergonomics of human-system interaction |
""", url=ISO, tags="ergonomics egress signs")
nfpa("layout-human-factors", """
NFPA 704 | Identification of the Hazards of Materials for Emergency Response |
""", "labelling")
add("layout-human-factors", "NORSOK", """
NORSOK S-001 | Technical safety |
NORSOK S-002 | Working environment |
NORSOK C-001 | Living quarters area |
""", url=NORSOK, access="mixed", region="NO", tags="offshore technical-safety")

# ================================================================================================ reactive hazards and chemical testing
add("reactive-hazards", "CCPS", """
CCPS Reactivity Essential Practices | Essential Practices for Managing Chemical Reactivity Hazards |
CCPS Reactive Evaluation | Guidelines for Chemical Reactivity Evaluation and Application to Process Design |
CCPS Safe Storage Reactive | Guidelines for Safe Storage and Handling of Reactive Materials |
CCPS Batch Reactions | Guidelines for Process Safety in Batch Reaction Systems |
""", url=CCPS, kind="book", tags="reactivity runaway")
add("reactive-hazards", "Wiley", """
Stoessel, Thermal Safety of Chemical Processes | Thermal Safety of Chemical Processes: Risk Assessment and Process Design (F. Stoessel) |
Barton and Rogers | Chemical Reaction Hazards: A Guide to Safety (IChemE) |
Urben, Bretherick | Bretherick's Handbook of Reactive Chemical Hazards (Elsevier) |
""", url=ICHEME, kind="book", tags="reactivity calorimetry")
nfpa("reactive-hazards", """
NFPA 400 | Hazardous Materials Code |
NFPA 30 | Flammable and Combustible Liquids Code |
NFPA 30B | Manufacture and Storage of Aerosol Products |
NFPA 33 | Spray Application Using Flammable or Combustible Materials |
NFPA 34 | Dipping, Coating, and Printing Processes Using Flammable or Combustible Liquids |
NFPA 35 | Manufacture of Organic Coatings |
NFPA 36 | Solvent Extraction Plants |
NFPA 45 | Fire Protection for Laboratories Using Chemicals |
NFPA 430 | Storage of Liquid and Solid Oxidizers | Incorporated into NFPA 400; legacy reference.
NFPA 432 | Storage of Organic Peroxide Formulations | Incorporated into NFPA 400; legacy reference.
""", "storage flammable")
doc("reactive-hazards", "NOAA / EPA", """
CAMEO Chemicals | Hazardous material datasheets and reactivity compatibility prediction | https://cameochemicals.noaa.gov/
Chemical Reactivity Worksheet | Tool to predict reactive incompatibilities (distributed by CCPS) | https://www.aiche.org/ccps/resources/chemical-reactivity-worksheet
""", kind="data-tool", tags="reactivity compatibility")
doc("reactive-hazards", "CSB", """
CSB reactive hazard study | Hazard investigation: improving reactive hazard management | https://www.csb.gov/improving-reactive-hazard-management/
""", kind="investigation", region="US", tags="reactivity")

# ================================================================================================ substance-specific and energy-transition
nfpa("substance-specific", """
NFPA 2 | Hydrogen Technologies Code |
NFPA 51 | Design and Installation of Oxygen-Fuel Gas Systems for Welding, Cutting, and Allied Processes |
NFPA 51B | Fire Prevention During Welding, Cutting, and Other Hot Work |
NFPA 53 | Materials, Equipment, and Systems Used in Oxygen-Enriched Atmospheres |
NFPA 54 | National Fuel Gas Code |
NFPA 55 | Compressed Gases and Cryogenic Fluids Code |
NFPA 56 | Fire and Explosion Prevention During Cleaning and Purging of Flammable Gas Piping Systems |
NFPA 58 | Liquefied Petroleum Gas Code |
NFPA 59 | Utility LP-Gas Plant Code |
NFPA 59A | Production, Storage, and Handling of Liquefied Natural Gas (LNG) |
NFPA 52 | Vehicular Natural Gas Fuel Systems Code |
NFPA 37 | Installation and Use of Stationary Combustion Engines and Gas Turbines |
NFPA 820 | Fire Protection in Wastewater Treatment and Collection Facilities |
NFPA 855 | Installation of Stationary Energy Storage Systems |
NFPA 850 | Fire Protection for Electric Generating Plants and High Voltage Direct Current Converter Stations |
NFPA 75 | Fire Protection of Information Technology Equipment |
NFPA 76 | Fire Protection of Telecommunications Facilities |
""", "gas hydrogen lng lpg bess")
add("substance-specific", "CGA", """
CGA G-4 | Oxygen |
CGA G-4.4 | Oxygen pipeline and piping systems |
CGA G-5 | Hydrogen |
CGA G-5.4 | Standard for hydrogen piping systems at user locations |
CGA G-2 | Anhydrous ammonia |
CGA G-6 | Carbon dioxide |
CGA P-1 | Safe handling of compressed gases in containers |
CGA S-1.1 | Pressure relief device standards: cylinders for compressed gases |
CGA S-1.2 | Pressure relief device standards: portable containers |
CGA S-1.3 | Pressure relief device standards: stationary storage containers |
CGA G-4.1 | Cleaning of equipment for oxygen service |
""", url=CGA, access="mixed", region="US", tags="industrial-gas relief oxygen hydrogen")
add("substance-specific", "EIGA", """
EIGA Doc 13 | Oxygen pipeline and piping systems |
EIGA Doc 04 | Fire hazards of oxygen and oxygen enriched atmospheres |
EIGA Doc 121 | Hydrogen pipeline systems |
EIGA Doc 33 | Cleaning of equipment for oxygen service |
""", url=EIGA, access="free", kind="guidance", region="EU", tags="oxygen hydrogen industrial-gas")
add("substance-specific", "Chlorine Institute", """
Chlorine Institute pamphlets | Chlorine safety, piping, materials, transport and emergency pamphlets (e.g. Pamphlet 1 Chlorine Basics, Pamphlet 6 piping systems) |
""", url="https://www.chlorineinstitute.org/", access="mixed", kind="guidance", region="US", tags="chlorine")
add("substance-specific", "ANSI/IIAR", """
IIAR 2 | Safe design of closed-circuit ammonia refrigeration systems |
IIAR 6 | Inspection, testing and maintenance of closed-circuit ammonia refrigeration systems |
IIAR 9 | Minimum system safety requirements for existing ammonia refrigeration systems |
""", url="https://www.iiar.org/", access="mixed", region="US", tags="ammonia refrigeration")
add("substance-specific", "ASHRAE", """
ASHRAE 15 | Safety standard for refrigeration systems |
ASHRAE 34 | Designation and safety classification of refrigerants |
""", url="https://www.ashrae.org/technical-resources/standards-and-guidelines", access="mixed", tags="refrigerant")
add("substance-specific", "ISO", """
ISO/TR 15916 | Basic considerations for the safety of hydrogen systems |
ISO 19880-1 | Gaseous hydrogen fuelling stations: general requirements |
ISO 22734 | Hydrogen generators using water electrolysis |
ISO 19881 | Gaseous hydrogen land vehicle fuel containers |
ISO 16111 | Transportable gas storage devices: hydrogen absorbed in reversible metal hydride |
ISO 19884 (series) | Gaseous hydrogen stationary storage |
ISO 14687 | Hydrogen fuel quality |
ISO 26142 | Hydrogen detection apparatus: stationary applications |
ISO 16924 | Natural gas fuelling stations: LNG stations |
ISO 20519 | Ships and marine technology: bunkering of LNG fuelled vessels |
ISO 20088-1 | Resistance to cryogenic spillage: liquid phase |
ISO 24252 | Biogas systems: non-household and non-gasification |
ISO 27913 | Carbon dioxide capture, transportation and geological storage: pipeline transportation systems |
""", url=ISO, tags="hydrogen lng biogas ccus")
add("substance-specific", "DNV", """
DNV-RP-F104 | Design and operation of carbon dioxide pipelines |
DNV-ST-F101 | Submarine pipeline systems |
DNV-RP-A203 | Technology qualification |
""", url=DNV, access="free", kind="guidance", tags="ccus pipeline")
add("substance-specific", "Energy Institute", """
EI CO2 pipeline hazard guidance | Hazard analysis for offshore carbon capture platforms and offshore pipelines |
EI Model Code of Safe Practice Part 9 | Large bulk pressure storage and refrigerated LPG |
EI Battery storage guidance | Battery storage guidance notes |
""", url=EI, access="mixed", kind="guidance", tags="ccus lpg bess")
doc("substance-specific", "US sources", """
H2Tools | Hydrogen safety best practices and lessons learned portal (PNNL) | https://h2tools.org/
NASA NSS 1740.16 | Safety Standard for Hydrogen and Hydrogen Systems | https://ntrs.nasa.gov/citations/19970033338 | Check whether a later NASA standard supersedes it for your use.
AIAA G-095 | Guide to Safety of Hydrogen and Hydrogen Systems | https://arc.aiaa.org/doi/book/10.2514/4.105197 | Paid.
UL 9540A | Test method for evaluating thermal runaway fire propagation in battery energy storage systems | https://www.ul.com/services/ul-9540a-test-method | Paid standard; the page is a description.
""", access="mixed", region="US", tags="hydrogen bess")
add("substance-specific", "SIGTTO", """
SIGTTO publications | Liquefied gas terminal and ship safety publications |
""", url="https://www.sigtto.org/", access="mixed", kind="guidance", tags="lng lpg marine")
add("substance-specific", "OCIMF / ICS / IAPH", """
ISGOTT | International Safety Guide for Oil Tankers and Terminals |
""", url="https://www.ocimf.org/", access="paid", kind="guidance", tags="marine terminal")
add("substance-specific", "IMO", """
IGC Code | International Code for the Construction and Equipment of Ships Carrying Liquefied Gases in Bulk |
IGF Code | International Code of Safety for Ships using Gases or other Low-flashpoint Fuels |
IBC Code | International Code for ships carrying dangerous chemicals in bulk |
IMDG Code | International Maritime Dangerous Goods Code |
""", url="https://www.imo.org/", access="paid", kind="regulation", tags="marine transport")

# ================================================================================================ pipelines and offshore
add("pipeline-offshore", "API", """
API STD 1160 | Managing system integrity for hazardous liquid pipelines |
API RP 1162 | Public awareness programs for pipeline operators |
API RP 1165 | Pipeline SCADA displays |
API RP 1168 | Pipeline control room management |
API RP 1175 | Pipeline leak detection program management |
API STD 1163 | In-line inspection systems qualification |
API RP 1102 | Steel pipelines crossing railroads and highways |
API RP 1110 | Pressure testing of steel pipelines |
API RP 14J | Design and hazards analysis for offshore production facilities |
API RP 2A-WSD | Planning, designing and constructing fixed offshore platforms: working stress design |
API RP 2FB | Design of offshore facilities against fire and blast loading |
API STD 53 | Well control equipment systems for drilling wells |
""", url=API, tags="pipeline offshore")
add("pipeline-offshore", "ISO", """
ISO 13623 | Pipeline transportation systems |
ISO 10418 | Offshore production installations: process safety systems |
ISO 19900 (series) | Offshore structures |
ISO 16708 | Pipeline transportation systems: reliability-based limit state methods |
""", url=ISO, tags="pipeline offshore")
add("pipeline-offshore", "DNV", """
DNV-OS-A101 | Safety principles and arrangements |
DNV-OS-D101 | Marine and machinery systems and equipment |
DNV-OS-D202 | Automation, safety and telecommunication systems |
DNV-OS-D301 | Fire protection |
DNV-OS-E201 | Oil and gas processing systems |
DNV-RP-C204 | Design against accidental loads |
DNV-RP-F107 | Risk assessment of pipeline protection |
DNV-RP-F116 | Integrity management of submarine pipeline systems |
DNV-RP-F113 | Pipeline subsea repair |
""", url=DNV, access="free", kind="standard", tags="offshore pipeline accidental-loads")
add("pipeline-offshore", "NORSOK", """
NORSOK P-002 | Process system design |
NORSOK P-001 | Process design |
NORSOK L-001 | Piping and valves |
NORSOK N-001 | Integrity of offshore structures |
NORSOK N-004 | Design of steel structures |
NORSOK I-002 | Industrial automation and control systems |
NORSOK D-010 | Well integrity in drilling and well operations |
NORSOK R-002 | Lifting equipment |
""", url=NORSOK, access="mixed", region="NO", tags="offshore norsok")
doc("pipeline-offshore", "ABS / LR / BV", """
ABS rules and guides | ABS rules, guides and guidance notes (many free) | https://ww2.eagle.org/en/rules-and-resources/rules-and-guides.html
Lloyd's Register rules | Classification rules and guidance | https://www.lr.org/
Bureau Veritas marine rules | Rules and guidance notes | https://marine-offshore.bureauveritas.com/
""", access="mixed", tags="class-society offshore")

# ================================================================================================ operations and safe work
add("safe-operations", "API", """
API STD 2015 | Requirements for safe entry and cleaning of petroleum storage tanks |
API RP 2016 | Guidelines and procedures for entering and cleaning petroleum storage tanks |
API RP 2027 | Ignition hazards and safe work practices for abrasive blasting of atmospheric storage tanks |
API RP 2026 | Safe access and egress involving floating roofs of storage tanks in petroleum service |
API RP 2217A | Safe work in inert confined spaces in the petroleum and petrochemical industries |
API RP 2219 | Safe operation of vacuum trucks in petroleum service |
""", url=API, tags="confined-space tank-entry")
add("safe-operations", "CCPS", """
CCPS Safe Work Practices | Guidelines for Safe Work Practices and non-routine operations |
CCPS Startup and Shutdown | Guidelines for Safe Process Operations and Maintenance |
CCPS Process Safety Culture | Essential Practices for Creating, Strengthening, and Sustaining Process Safety Culture |
CCPS Transient Operations | Guidelines for process safety during transient operating modes |
""", url=CCPS, kind="book", tags="operations culture")
nfpa("safe-operations", """
NFPA 306 | Control of Gas Hazards on Vessels |
NFPA 326 | Safeguarding of Tanks and Containers for Entry, Cleaning, or Repair |
NFPA 329 | Handling Releases of Flammable and Combustible Liquids and Gases |
NFPA 350 | Safe Confined Space Entry and Work |
NFPA 470 | Hazardous Materials/Weapons of Mass Destruction Standard for Responders |
""", "operations")
doc("safe-operations", "NIOSH / PHMSA", """
NIOSH Pocket Guide | NIOSH Pocket Guide to Chemical Hazards | https://www.cdc.gov/niosh/npg/default.html
Emergency Response Guidebook | PHMSA Emergency Response Guidebook (initial isolation and protective action distances) | https://www.phmsa.dot.gov/training/hazmat/erg/emergency-response-guidebook-erg
""", region="US", tags="exposure emergency")

# ================================================================================================ consequence modelling, properties, exposure data
doc("data-tools", "NOAA / EPA", """
ALOHA | Areal Locations of Hazardous Atmospheres dispersion and consequence model | https://www.epa.gov/cameo/aloha-software
RMP*Comp | EPA offsite consequence analysis tool | https://www.epa.gov/rmp/rmpcomp
EPA OCA guidance | Risk Management Program guidance for offsite consequence analysis | https://www.epa.gov/rmp/rmp-guidance-offsite-consequence-analysis
AEGL values | Acute Exposure Guideline Levels for airborne chemicals | https://www.epa.gov/aegl
EPA SCRAM | Air dispersion modelling downloads (AERMOD and related) | https://www.epa.gov/scram
""", kind="data-tool", region="US", tags="dispersion toxic consequence")
doc("data-tools", "Exposure limits", """
AIHA ERPG | Emergency Response Planning Guidelines | https://www.aiha.org/ | Mixed access.
DOE PACs | Protective Action Criteria for chemicals | https://pacteels.pnnl.gov/
GESTIS substances | GESTIS database on hazardous substances | https://gestis.dguv.de/
ECHA CHEM | European Chemicals Agency substance information | https://chem.echa.europa.eu/
PubChem | Chemical data including safety sections | https://pubchem.ncbi.nlm.nih.gov/
NIOSH IDLH | Immediately Dangerous to Life or Health values | https://www.cdc.gov/niosh/idlh/default.html
""", kind="database", tags="toxic exposure-limit")
doc("data-tools", "Properties", """
NIST Chemistry WebBook | Thermophysical and thermochemical data | https://webbook.nist.gov/chemistry/
DIPPR 801 | AIChE evaluated process design data (paid) | https://www.aiche.org/dippr
CoolProp | Open-source thermophysical property library | https://coolprop.org/
fluids (ChEDL) | Open-source fluid dynamics library, including relief sizing | https://github.com/CalebBell/fluids
thermo (ChEDL) | Open-source thermodynamics library | https://github.com/CalebBell/thermo
Cantera | Open-source kinetics and thermodynamics toolkit | https://cantera.org/
OpenFOAM | Open-source CFD toolkit | https://www.openfoam.com/
HyRAM+ | Hydrogen and alternative fuels risk assessment models (Sandia) | https://energy.sandia.gov/programs/sustainable-transportation/hydrogen/hydrogen-safety-codes-and-standards/hyram/
""", access="mixed", kind="data-tool", tags="properties modelling")

# ================================================================================================ incident and loss databases
doc("incidents", "Investigators and databases", """
CSB investigations | US Chemical Safety Board investigations and videos | https://www.csb.gov/investigations/
CSB recommendations | US Chemical Safety Board recommendations | https://www.csb.gov/recommendations/
eMARS | EU Major Accident Reporting System | https://emars.jrc.ec.europa.eu/
ARIA | French accident database (BARPI) | https://www.aria.developpement-durable.gouv.fr/the-barpi/the-aria-database/?lang=en
ZEMA | German central reporting and evaluation office for major accidents | https://www.infosis.uba.de/index.php/en/site/12981/zema/index.html
NTSB investigations | US National Transportation Safety Board, including pipeline accidents | https://www.ntsb.gov/investigations/Pages/Investigations.aspx
PHMSA incident data | Pipeline incident and accident data | https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data
EPA RMP accident data | Risk Management Plan five-year accident history information | https://www.epa.gov/rmp
OSHA accident search | OSHA fatality and catastrophe investigation summaries | https://www.osha.gov/ords/imis/accidentsearch.html
NRC (US) National Response Center | Release reports | https://nrc.uscg.mil/
JST Failure Knowledge Database | Japanese failure case database | https://www.shippai.org/fkd/en/
HIAD | European Hydrogen Incidents and Accidents Database | https://minerva.jrc.ec.europa.eu/en/shorturl/capri/hiadpt
HSE offshore releases | Offshore hydrocarbon releases statistics | https://www.hse.gov.uk/offshore/statistics.htm
Buncefield investigation | Buncefield Major Incident Investigation Board material (HSE) | https://www.hse.gov.uk/comah/buncefield/
Piper Alpha / Cullen | Public Inquiry into the Piper Alpha disaster (HSE copy) | https://www.hse.gov.uk/offshore/piper-alpha-disaster-public-inquiry.htm
""", kind="database", tags="incident lessons")
add("incidents", "IChemE", """
IChemE Loss Prevention Bulletin | Incident case studies bulletin |
""", url="https://www.icheme.org/knowledge/loss-prevention-bulletin/", access="mixed", kind="journal", tags="incident lessons")
add("incidents", "CCPS", """
CCPS Process Safety Beacon | Monthly one-page process safety lessons |
CCPS Incidents That Define Process Safety | Case histories of defining incidents |
""", url="https://www.aiche.org/ccps/resources/process-safety-beacon", access="mixed", kind="guidance", tags="lessons")
add("incidents", "Marsh", """
Marsh 100 Largest Losses | Largest property damage losses in the hydrocarbon industry |
""", url="https://www.marsh.com/", access="free-registration", kind="guidance", tags="loss insurance")

# ================================================================================================ India
add("india-standards", "OISD", """
OISD standards list | Oil Industry Safety Directorate standards, guidelines and recommended practices | See process_safety/data/oisd_standards.json for the numbered list already in this toolkit.
""", url=OISD, access="mixed", region="IN", tags="oisd")
add("india-standards", "BIS", """
IS 2825 | Code for unfired pressure vessels |
IS 15656 | Hazard identification and risk analysis: code of practice |
IS 14489 | Code of practice on occupational safety and health audit |
IS 18001 | Occupational health and safety management systems | Superseded by the IS adoption of ISO 45001; confirm status.
IS 5571 | Guide for selection of electrical equipment for hazardous areas |
IS 5572 | Classification of hazardous areas (other than mines) having flammable gases and vapours for electrical installation |
IS/IEC 60079 (series) | Explosive atmospheres (Indian adoptions) |
IS/IEC 61511 | Functional safety for the process industry (Indian adoption) |
IS/IEC 62305 | Protection against lightning (Indian adoption) |
IS 3043 | Code of practice for earthing |
IS 732 | Code of practice for electrical wiring installations |
IS 2189 | Selection, installation and maintenance of automatic fire detection and alarm systems |
IS 2190 | Selection, installation and maintenance of first-aid fire extinguishers |
IS 15105 | Design and installation of fixed automatic sprinkler fire extinguishing systems |
IS 15325 | Design and installation of fixed automatic high and medium velocity water spray system |
IS 13039 | Code of practice for provision and maintenance of external hydrant system |
IS 1239 | Steel tubes, tubulars and other wrought steel fittings |
IS 3589 | Steel pipes for water and sewage |
IS 2062 | Hot rolled medium and high tensile structural steel |
IS 2002 | Steel plates for pressure vessels for intermediate and high temperature service |
IS 2041 | Steel plates for pressure vessels used at moderate and low temperature |
IS 803 | Code of practice for design, fabrication and erection of vertical mild steel cylindrical welded oil storage tanks |
IS 4503 | Shell and tube type heat exchangers |
IS 875 | Code of practice for design loads for buildings and structures |
IS 1893 | Criteria for earthquake resistant design of structures |
SP 30 | National Electrical Code of India |
SP 7 | National Building Code of India (Part 4: fire and life safety) |
""", url=BIS, access="mixed", region="IN", tags="bis india")
add("india-standards", "DGFASLI", """
DGFASLI | Directorate General Factory Advice Service and Labour Institutes |
""", url="https://dgfasli.gov.in/", access="free", kind="guidance", region="IN", tags="factories")
add("india-standards", "NDMA", """
NDMA chemical disaster guidelines | National Disaster Management Guidelines: Chemical Disasters (Industrial) |
""", url="https://ndma.gov.in/", access="free", kind="guidance", region="IN", tags="emergency")
add("india-standards", "CPCB", """
CPCB standards and guidelines | Environmental standards, hazardous waste rules and industry guidelines |
""", url="https://cpcb.nic.in/", access="free", kind="guidance", region="IN", tags="environment")

# ================================================================================================ books and handbooks
add("books", "Elsevier", """
Lees' Loss Prevention | Lees' Loss Prevention in the Process Industries (S. Mannan, ed.) |
Kletz, What Went Wrong? | What Went Wrong? Case Histories of Process Plant Disasters (T. Kletz, P. Amyotte) |
Kletz and Amyotte, Inherently Safer | Process Plants: A Handbook for Inherently Safer Design |
Sanders, Chemical Process Safety Case Histories | Chemical Process Safety: Learning from Case Histories (R. Sanders) |
Casal, Effects and Consequences | Evaluation of the Effects and Consequences of Major Accidents in Industrial Plants (J. Casal) |
Smith and Simpson | Safety Critical Systems Handbook |
Towler and Sinnott | Chemical Engineering Design |
Ludwig / Coker | Ludwig's Applied Process Design for Chemical and Petrochemical Plants |
""", url="https://shop.elsevier.com/", kind="book", tags="textbook")
add("books", "Pearson", """
Crowl and Louvar | Chemical Process Safety: Fundamentals with Applications |
""", url="https://www.pearson.com/", kind="book", tags="textbook")
add("books", "McGraw-Hill", """
Perry's Handbook | Perry's Chemical Engineers' Handbook (process safety section) |
""", url="https://www.mheducation.com/", kind="book", tags="handbook")
add("books", "Crane", """
Crane TP-410 | Flow of Fluids Through Valves, Fittings and Pipe |
""", url="https://www.flowoffluids.com/", kind="book", tags="hydraulics")
add("books", "GPSA", """
GPSA Engineering Data Book | Gas Processors Suppliers Association Engineering Data Book |
""", url="https://www.gpamidstream.org/", kind="book", tags="gas-processing")
add("books", "SFPE", """
SFPE Handbook | SFPE Handbook of Fire Protection Engineering |
""", url="https://www.sfpe.org/", kind="book", tags="fire-engineering")
doc("books", "Open learning", """
NPTEL | Free engineering courses, including chemical process safety | https://nptel.ac.in/
SAChE | AIChE Safety and Chemical Engineering Education resources | https://www.aiche.org/ccps/education/sache
MIT OpenCourseWare | Free course materials (search process safety) | https://ocw.mit.edu/
""", kind="course", tags="learning")

# ================================================================================================ journals, conferences, research centres
doc("journals-research", "Journals", """
Journal of Loss Prevention in the Process Industries | Peer-reviewed journal | https://www.sciencedirect.com/journal/journal-of-loss-prevention-in-the-process-industries
Process Safety and Environmental Protection | Peer-reviewed journal (IChemE) | https://www.sciencedirect.com/journal/process-safety-and-environmental-protection
Process Safety Progress | Peer-reviewed journal (AIChE) | https://aiche.onlinelibrary.wiley.com/journal/15475913
Journal of Hazardous Materials | Peer-reviewed journal | https://www.sciencedirect.com/journal/journal-of-hazardous-materials
Fire Safety Journal | Peer-reviewed journal | https://www.sciencedirect.com/journal/fire-safety-journal
Reliability Engineering and System Safety | Peer-reviewed journal | https://www.sciencedirect.com/journal/reliability-engineering-and-system-safety
Safety Science | Peer-reviewed journal | https://www.sciencedirect.com/journal/safety-science
Combustion and Flame | Peer-reviewed journal | https://www.sciencedirect.com/journal/combustion-and-flame
International Journal of Hydrogen Energy | Peer-reviewed journal | https://www.sciencedirect.com/journal/international-journal-of-hydrogen-energy
Engineering Failure Analysis | Peer-reviewed journal | https://www.sciencedirect.com/journal/engineering-failure-analysis
Corrosion Science | Peer-reviewed journal | https://www.sciencedirect.com/journal/corrosion-science
Journal of Chemical Health and Safety | ACS journal | https://pubs.acs.org/journal/jchas
""", access="mixed", kind="journal", tags="research")
doc("journals-research", "Open access", """
Chemical Engineering Transactions | Open-access proceedings (AIDIC), including loss prevention symposia | https://www.cetjournal.it/
Safety (MDPI) | Open-access journal | https://www.mdpi.com/journal/safety
Processes (MDPI) | Open-access journal | https://www.mdpi.com/journal/processes
IChemE Hazards papers | IChemE Hazards symposium paper archive | https://www.icheme.org/knowledge/safety-centre/resources/
CORE | Aggregator of open-access research papers | https://core.ac.uk/
OpenAlex | Open index of scholarly works with open-access locations | https://openalex.org/
OSTI.gov | US Department of Energy research reports | https://www.osti.gov/
NTRS | NASA Technical Reports Server | https://ntrs.nasa.gov/
Semantic Scholar | Literature search | https://www.semanticscholar.org/
""", kind="database", tags="open-access research")
doc("journals-research", "Research centres and associations", """
CCPS | Center for Chemical Process Safety | https://www.aiche.org/ccps
Mary Kay O'Connor Process Safety Center | Research centre at Texas A&M | https://psc.tamu.edu/
IChemE Safety Centre | Industry safety centre | https://www.icheme.org/knowledge/safety-centre/
European Process Safety Centre | EPSC publications and working groups | https://epsc.be/
EFCE Loss Prevention | European Federation of Chemical Engineering | https://efce.info/
HSE Science and Research Centre | UK research and testing | https://www.hsl.gov.uk/
INERIS | French industrial environment and risk institute | https://www.ineris.fr/en
BAM | German Federal Institute for Materials Research and Testing | https://www.bam.de/
TNO | Netherlands research organisation | https://www.tno.nl/en/
Gexcon knowledge base | Consequence modelling and explosion research (vendor) | https://www.gexcon.com/
""", access="mixed", kind="association", tags="research")

# ================================================================================================ lawful ways to read standards
doc("access-routes", "Free and lawful access", """
NIST: standards incorporated by reference | How to find free read-only copies of standards cited in US regulations | https://www.nist.gov/standardsgov/accessing-standards-incorporated-reference
NIST SIBR database | Standards Incorporated by Reference database, searchable by CFR citation | https://sibr.nist.gov/
ANSI IBR portal | Read-only access to many standards incorporated by reference (registration) | https://ibr.ansi.org/
API IBR reading room | Read-only access to API standards incorporated in US regulations and safety documents (registration) | https://publications.api.org/
ASTM Reading Room | Read-only access to ASTM standards incorporated by reference (registration) | https://www.astm.org/products-services/reading-room.html
NFPA free access | Read-only online access to NFPA codes (free account) | https://www.nfpa.org/for-professionals/codes-and-standards/list-of-codes-and-standards/free-access
ICC public access codes | Read-only International Codes | https://codes.iccsafe.org/
BIS standards portal | Indian Standards search and download service | https://standards.bis.gov.in/
ISO Online Browsing Platform | Free preview of scope, terms and contents of ISO standards | https://www.iso.org/obp/ui
IEC webstore previews | Free preview pages of IEC standards | https://webstore.iec.ch/
NORSOK overview | NORSOK standards list and access options from Standards Norway | https://standard.no/en/sectors/petroleum/norsok-standards/
DNV rules and standards | DNV rules, standards and recommended practices portal | https://www.dnv.com/rules-standards/
EUR-Lex | Official EU legislation | https://eur-lex.europa.eu/
eCFR | US Code of Federal Regulations, current text | https://www.ecfr.gov/
UK legislation | Official UK legislation | https://www.legislation.gov.uk/
HSE publications | Free HSE books and leaflets | https://www.hse.gov.uk/pubns/
""", kind="access-route", tags="access free")
doc("access-routes", "Paid distributors", """
ANSI Webstore | Standards store for many US and international developers | https://webstore.ansi.org/
Accuris Standards Store | Standards distributor (formerly Techstreet) | https://store.accuristech.com/
BSI Knowledge | British, European and international standards | https://knowledge.bsigroup.com/
Intertek Inform | Standards distributor | https://www.intertekinform.com/
DIN Media | German and international standards | https://www.dinmedia.de/en
ASTM Compass | ASTM subscription platform | https://www.astm.org/products-services/enterprise-solutions.html
""", access="paid", kind="access-route", tags="access paid")


# ================================================================================================ free official PDFs
# HSE books that HSE publishes free of charge as PDF. Kept only where the checker confirms a PDF (see --pdf results).
HSE_PDF = ["HSG65", "HSG254", "HSG48", "HSG253", "HSG250", "HSG176", "HSG51", "HSG140", "HSG71", "HSG103", "HSG244", "HSG143", "L111",
           "L138", "L122", "INDG370"]
PDF_URL = {f"HSE-{d}": f"https://www.hse.gov.uk/pubns/{'priced/' if not d.startswith('INDG') else ''}{d.lower()}.pdf" for d in HSE_PDF}
PDF_URL.update({
    "OSHA-OSHA 3132": "https://www.osha.gov/sites/default/files/publications/osha3132.pdf",
    "OSHA-OSHA 3133": "https://www.osha.gov/sites/default/files/publications/osha3133.pdf",
    "NIST-NIST SP 800-82": "https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf",
    "US DoD-UFC 3-340-02": "https://www.wbdg.org/FFC/DOD/UFC/ufc_3_340_02_2008_c2.pdf",
    "US sources-NASA NSS 1740.16": "https://ntrs.nasa.gov/api/citations/19970033338/downloads/19970033338.pdf",
    "NIOSH / PHMSA-NIOSH Pocket Guide": "https://www.cdc.gov/niosh/docs/2005-149/pdfs/2005-149.pdf",
    "NIOSH / PHMSA-Emergency Response Guidebook": "https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/2024-04/ERG2024-Eng-Web-a.pdf",
    "US NRC-NUREG-1805": "https://www.nrc.gov/docs/ML0434/ML043410399.pdf",
})

doc("psm", "OSHA", """
OSHA 3918 | Process Safety Management for Petroleum Refineries | https://www.osha.gov/sites/default/files/publications/OSHA3918.pdf
OSHA 3908 | Process Safety Management for Small Businesses | https://www.osha.gov/sites/default/files/publications/OSHA3908.pdf
OSHA 3909 | Process Safety Management for Storage Facilities | https://www.osha.gov/sites/default/files/publications/OSHA3909.pdf
OSHA 3912 | Process Safety Management for Explosives and Pyrotechnics Manufacturing | https://www.osha.gov/sites/default/files/publications/OSHA3912.pdf
""", region="US", tags="psm pdf")
doc("consequence-reports", "HSE", """
HSE RR1229 | Revised fireball and jet fire models for pipelines | https://www.hse.gov.uk/research/assets/docs/rr1229.pdf
HSE RR1196 | Radiation calculations for fireball and jet fire models: a literature review | https://www.hse.gov.uk/research/assets/docs/rr1196.pdf
""", kind="guidance", region="UK", tags="fire consequence pdf")
doc("consequence-reports", "RIVM", """
RIVM 620550005 | A comparison of jet fire models for horizontal two-phase and liquid releases | https://www.rivm.nl/bibliotheek/rapporten/620550005.pdf
""", kind="guidance", region="NL", tags="fire consequence pdf")
doc("consequence-reports", "IChemE", """
IChemE Hazards XXI paper 088 | Two-phase jet releases and droplet dispersion | https://www.icheme.org/media/9584/xxi-paper-088.pdf
""", kind="guidance", region="global", tags="two-phase pdf")


# ================================================================================================ Digital Refining articles
# Titles and links come from web-search result listings (2026-11-25). digitalrefining.com's robots.txt disallows Claude agents, so no
# page there was requested: nothing was read, links are unchecked, and selection is by title and search snippet. Rows: (tags, id, title, url).
DIGITAL_REFINING = [
    ('relief flare depressuring', '1000394', 'Optimising safety relief and flare systems', 'https://www.digitalrefining.com/article/1000394/optimising-safety-relief-and-flare-systems'),
    ('relief flare depressuring', '1002334', 'Sizing relief valves for real gas or vapour', 'https://www.digitalrefining.com/article/1002334/sizing-relief-valves-for-real-gas-or-vapour'),
    ('relief flare depressuring', '1001088', 'Applying relief load calculation methods', 'https://www.digitalrefining.com/article/1001088/applying-relief-load-calculation-methods'),
    ('relief flare depressuring', '1002809', 'Stationing an operator at a pressure safety valve bypass', 'https://www.digitalrefining.com/article/1002809/stationing-an-operator-at-a-pressure-safety-valve-bypass'),
    ('relief flare depressuring', '1000961', 'Accurate prediction of tower relief', 'https://www.digitalrefining.com/article/1000961/accurate-prediction-of-tower-relief'),
    ('relief flare depressuring', '1002247', 'Pressure relief with rupture discs', 'https://www.digitalrefining.com/article/1002247/pressure-relief-with-rupture-discs'),
    ('relief flare depressuring', '1001532', 'Dynamic column simulation delivers reduced relief load', 'https://www.digitalrefining.com/article/1001532/dynamic-column-simulation-delivers-reduced-relief-load'),
    ('relief flare depressuring', '1002252', 'Dynamic simulation to estimate tower relief', 'https://www.digitalrefining.com/article/1002252/dynamic-simulation-to-estimate-tower-relief'),
    ('relief flare depressuring', '1003294', 'When dynamic relief calculations give unexpected results', 'https://www.digitalrefining.com/article/1003294/when-dynamic-relief-calculations-give-unexpected-results'),
    ('relief flare depressuring', '1000487', 'Calculating column relief loads', 'https://www.digitalrefining.com/article/1000487/calculating-column-relief-loads'),
    ('relief flare depressuring', '1000458', 'Are there alternatives to an expensive overhaul of a bottlenecked flare system?', 'https://www.digitalrefining.com/article/1000458/are-there-alternatives-to-an-expensive-overhaul-of-a-bottlenecked-flare-system'),
    ('relief flare depressuring', '1001215', 'Tube rupture in a natural gas heater', 'https://www.digitalrefining.com/article/1001215/tube-rupture-in-a-natural-gas-heater'),
    ('relief flare depressuring', '1002294', 'Protecting against high pressure rupture (TIA)', 'https://www.digitalrefining.com/article/1002294/protecting-against-high-pressure-rupture-ti'),
    ('relief flare depressuring', '1003013', 'Assessing LNG feed gas depressurisation', 'https://www.digitalrefining.com/article/1003013/assessing-lng-feed-gas-depressurisation'),
    ('process-safety-management incidents', '1000455', 'Achieving excellence in process safety management', 'https://www.digitalrefining.com/article/1000455/achieving-excellence-in-process-safety-management'),
    ('process-safety-management incidents', '1003592', 'Identifying patterns in recent refinery incidents', 'https://www.digitalrefining.com/article/1003592/identifying-patterns-in-recent-refinery-incidents'),
    ('process-safety-management incidents', '1003519', 'Procedure management in refinery operations', 'https://www.digitalrefining.com/article/1003519/procedure-management-in-refinery-operations'),
    ('process-safety-management incidents', '1001225', 'Enabling the refinery of the future: safety first', 'https://www.digitalrefining.com/article/1001225/enabling-the-refinery-of-the-future-safety-first'),
    ('process-safety-management incidents', '1003135', 'Fundamentals of refinery safety', 'https://www.digitalrefining.com/article/1003135/fundamentals-of-refinery-safety'),
    ('process-safety-management incidents', '1003336', 'Avoid utility disruptions in refinery operations', 'https://www.digitalrefining.com/article/1003336/avoid-utility-disruptions-in-refinery-operations'),
    ('functional-safety machinery', '1000949', 'What does SIL and functional safety mean to operators of rotating equipment?', 'https://www.digitalrefining.com/article/1000949/what-does-sil-and-functional-safety-mean-to-operators-of-rotating-equipment'),
    ('functional-safety machinery', '1001303', 'SIL and functional safety in rotating equipment', 'https://www.digitalrefining.com/article/1001303/sil-and-functional-safety-in-rotating-equipment'),
    ('functional-safety machinery', '1001238', 'Safety system separation: examination of three types of machinery protection systems', 'https://www.digitalrefining.com/article/1001238/safety-system-separation-examination-of-three-types-of-machinery-protection-systems'),
    ('functional-safety machinery', '1002560', 'Process safety time for fired heaters', 'https://www.digitalrefining.com/article/1002560/process-safety-time-for-fired-heaters'),
    ('functional-safety machinery', '1000749', 'Hazardous or harmless? Machinery has not changed, but demands have', 'https://www.digitalrefining.com/article/1000749/hazardous-or-harmless-machinery-has-not-changed-but-demands-have'),
    ('alarm control-room human-factors cyber', '1003301', 'Operator performance advances enable safer operations', 'https://www.digitalrefining.com/article/1003301/operator-performance-advances-enable-safer-operations'),
    ('alarm control-room human-factors cyber', '1000936', 'High-fidelity operator training simulators', 'https://www.digitalrefining.com/article/1000936/high-fidelity-operator-training-simulators'),
    ('alarm control-room human-factors cyber', '1001190', 'Cyber security in the refining world', 'https://www.digitalrefining.com/article/1001190/cyber-security-in-the-refining-world'),
    ('fired-heater combustion', '1000852', 'Role of fired heater safety systems', 'https://www.digitalrefining.com/article/1000852/role-of-fired-heater-safety-systems'),
    ('fired-heater combustion', '1000366', 'Useful tips for fired heater optimisation', 'https://www.digitalrefining.com/article/1000366/useful-tips-for-fired-heater-optimisation'),
    ('fired-heater combustion', '1003209', 'Fired heater design: a multidisciplinary engineering effort', 'https://www.digitalrefining.com/article/1003209/fired-heater-design-a-multidisciplinary-engineering-effort'),
    ('fired-heater combustion', '1002511', 'The hazards of fired heater flooding', 'https://www.digitalrefining.com/article/1002511/the-hazards-of-fired-heater-flooding'),
    ('fired-heater combustion', '1001457', 'Retrofitting crude furnace burners', 'https://www.digitalrefining.com/article/1001457/retrofitting-crude-furnace-burners'),
    ('fired-heater combustion', '1000131', 'Avoiding FCC regenerator upsets', 'https://www.digitalrefining.com/article/1000131/avoiding-fcc-regenerator-upsets'),
    ('hydroprocessing reactor runaway', '1002948', 'Proactively preventing reactor runaway events', 'https://www.digitalrefining.com/article/1002948/proactively-preventing-reactor-runaway-events'),
    ('hydroprocessing reactor runaway', '1002911', 'Reactor runaways: automatic or manual depressuring?', 'https://www.digitalrefining.com/article/1002911/reactor-runaways-automatic-or-manual-depressuring'),
    ('hydroprocessing reactor runaway', '1000173', 'Operational life improvements in modern hydroprocessing reactors', 'https://www.digitalrefining.com/article/1000173/operational-life-improvements-in-modern-hydroprocessing-reactors'),
    ('corrosion materials', '1000862', 'Reactor effluent air cooler safety through design', 'https://www.digitalrefining.com/article/1000862/reactor-effluent-air-cooler-safety-through-design'),
    ('corrosion materials', '1002512', 'Mitigating corrosion with a digital twin', 'https://www.digitalrefining.com/article/1002512/mitigating-corrosion-with-a-digital-twin'),
    ('corrosion materials', '1003119', 'Navigating corrosion challenges in column overhead systems', 'https://www.digitalrefining.com/article/1003119/navigating-corrosion-challenges-in-column-overhead-systems'),
    ('corrosion materials', '1003344', 'Corrosion control in refinery distillation', 'https://www.digitalrefining.com/article/1003344/corrosion-control-in-refinery-distillation'),
    ('corrosion materials', '1001756', 'Low cost revamp to process heavy sour crudes', 'https://www.digitalrefining.com/article/1001756/low-cost-revamp-to-process-heavy-sour-crudes'),
    ('corrosion materials', '1003262', 'Synergistic multifunctional corrosion inhibitors for high-acid crudes', 'https://www.digitalrefining.com/article/1003262/synergistic-multifunctional-corrosion-inhibitors-for-high-acid-crudes'),
    ('corrosion materials', '1002331', 'Development of a naphthenic acid corrosion model', 'https://www.digitalrefining.com/article/1002331/development-of-a-naphthenic-acid-corrosion-model'),
    ('corrosion materials', '1001550', 'The corrosion-fouling cycle in amine systems', 'https://www.digitalrefining.com/article/1001550/the-corrosion-fouling-cycle-in-amine-systems'),
    ('corrosion materials', '1000902', 'Distribution of HCN in sour water systems', 'https://www.digitalrefining.com/article/1000902/distribution-of-hcn-in-sour-water-systems'),
    ('corrosion materials', '1000879', 'HCN in amine systems', 'https://www.digitalrefining.com/article/1000879/hcn-in-amine-systems'),
    ('corrosion materials', '1000551', 'Minimise corrosion while maximising distillate', 'https://www.digitalrefining.com/article/1000551/minimise-corrosion-while-maximising-distillate'),
    ('corrosion materials', '1003471', 'Hydrogen blistering in rich amine flash drum of VGO HDS unit', 'https://www.digitalrefining.com/article/1003471/hydrogen-blistering-in-rich-amine-flash-drum-of-vgo-hds-unit'),
    ('corrosion materials', '1000598', 'Multiple corrosion mechanisms in crude distillation overhead system', 'https://www.digitalrefining.com/article/1000598/multiple-corrosion-mechanisms-in-crude-distillation-overhead-system'),
    ('corrosion materials', '1001747', 'Addressing corrosion challenges in refineries', 'https://www.digitalrefining.com/article/1001747/addressing-corrosion-challenges-in-refineries'),
    ('corrosion materials', '1003488', 'Risk-based integrity approach to vessel life extension', 'https://www.digitalrefining.com/article/1003488/risk-based-integrity-approach-to-vessel-life-extension'),
    ('corrosion materials', '1003293', 'Digital twin corrosion monitoring for CDU overhead systems', 'https://www.digitalrefining.com/article/1003293/digital-twin-corrosion-monitoring-for-cdu-overhead-systems'),
    ('corrosion materials', '1002501', 'Real-time crude and desalter monitoring', 'https://www.digitalrefining.com/article/1002501/real-time-crude-and-desalter-monitoring'),
    ('corrosion materials', '1002630', 'Amine anomaly in a mild hydrocracker', 'https://www.digitalrefining.com/article/1002630/amine-anomaly-in-a-mild-hydrocracker'),
    ('renewable-fuels corrosion design', '1003203', 'Plan for corrosion when co-processing renewable feedstocks (ERTC 2024)', 'https://www.digitalrefining.com/article/1003203/plan-for-corrosion-when-co-processing-renewable-feedstocks-ertc-202'),
    ('renewable-fuels corrosion design', '1003085', 'Co-processing renewable feeds in hydrodesulphurisation units', 'https://www.digitalrefining.com/article/1003085/co-processing-renewable-feeds-in-hydrodesulphurisation-units'),
    ('renewable-fuels corrosion design', '1003123', 'Co-processing renewable feeds in hydrodesulphurisation units: Part 2', 'https://www.digitalrefining.com/article/1003123/co-processing-renewable-feeds-in-hydrodesulphurisation-units-part-2'),
    ('renewable-fuels corrosion design', '1002659', 'Key considerations for design and operation of a renewable diesel unit', 'https://www.digitalrefining.com/article/1002659/key-considerations-for-design-and-operation-of-a-renewable-diesel-unit'),
    ('renewable-fuels corrosion design', '1003094', 'SAF production via co-processing in the kerosene hydrotreater', 'https://www.digitalrefining.com/article/1003094/saf-production-via-co-processing-in-the-kerosene-hydrotreater'),
    ('sulphur h2s', '1000244', 'Improving sulphur recovery units', 'https://www.digitalrefining.com/article/1000244/improving-sulphur-recovery-units'),
    ('sulphur h2s', '1002462', 'Revamping the sulphur plant', 'https://www.digitalrefining.com/article/1002462/revamping-the-sulphur-plant'),
    ('sulphur h2s', '1000498', 'Designing for sulphur removal and storage: part II', 'https://www.digitalrefining.com/article/1000498/designing-for-sulphur-removal-and-storage-part-ii'),
    ('sulphur h2s', '1000464', 'Processing NH3 acid gas in a sulphur recovery unit', 'https://www.digitalrefining.com/article/1000464/processing-nh3-acid-gas-in-a-sulphur-recovery-unit'),
    ('sulphur h2s', '1000747', 'Sulphur tail gas thermal oxidiser systems', 'https://www.digitalrefining.com/article/1000747/sulphur-tail-gas-thermal-oxidiser-systems'),
    ('sulphur h2s', '1001113', 'Linings for sulphur storage tanks', 'https://www.digitalrefining.com/article/1001113/linings-for-sulphur-storage-tanks'),
    ('sulphur h2s', '1000917', 'Risks of accumulated sulphur in sulphur recovery units', 'https://www.digitalrefining.com/article/1000917/risks-of-accumulated-sulphur-in-sulphur-recovery-units'),
    ('sulphur h2s', '1001233', 'Importance of heat maintenance in sulphur recovery units', 'https://www.digitalrefining.com/article/1001233/importance-of-heat-maintenance-in-sulphur-recovery-units'),
    ('sulphur h2s', '1000874', 'Loading up liquid', 'https://www.digitalrefining.com/article/1000874/loading-up-liquid'),
    ('delayed-coker', '1000212', 'Delayed coker design and project execution', 'https://www.digitalrefining.com/article/1000212/delayed-coker-design-and-project-execution'),
    ('delayed-coker', '1000176', 'Coke drum design', 'https://www.digitalrefining.com/article/1000176/coke-drum-design'),
    ('delayed-coker', '1000046', 'Delayed coking: valves make the difference', 'https://www.digitalrefining.com/article/1000046/delayed-coking-valves-make-the-difference'),
    ('alkylation hf acid', '1000242', 'A flexible approach to refinery olefin alkylation', 'https://www.digitalrefining.com/article/1000242/a-flexible-approach-to-refinery-olefin-alkylation'),
    ('alkylation hf acid', '1002350', 'Removing acid droplets produced by alkylation reaction', 'https://www.digitalrefining.com/article/1002350/removing-acid-droplets-produced-by-alkylation-reaction'),
    ('alkylation hf acid', '1001555', 'Hydrofluoric acid alkylation conversion and expansion', 'https://www.digitalrefining.com/article/1001555/hydrofluoric-acid-alkylation-conversion-and-expansion'),
    ('turnaround confined-space inert', '1001490', 'Catalyst passivation for safer, more efficient turnarounds', 'https://www.digitalrefining.com/article/1001490/catalyst-passivation-for-safer-more-efficient-turnarounds'),
    ('turnaround confined-space inert', '1001032', 'Reducing reactor turnaround time', 'https://www.digitalrefining.com/article/1001032/reducing-reactor-turnaround-time'),
    ('turnaround confined-space inert', '1001469', 'Eliminating inert entry for catalyst changeout (TIA)', 'https://www.digitalrefining.com/article/1001469/eliminating-inert-entry-for-catalyst-changeout-ti'),
    ('turnaround confined-space inert', '1003127', 'Vessel internals enhance worker safety during plant turnarounds (TIA)', 'https://www.digitalrefining.com/article/1003127/vessel-internals-enhance-worker-safety-during-plant-turnarounds-ti'),
    ('turnaround confined-space inert', '1003058', 'Worker safety when entering reactors with an inert atmosphere (TIA)', 'https://www.digitalrefining.com/article/1003058/worker-safety-when-entering-reactors-with-an-inert-atmosphere-ti'),
    ('fire-gas-detection layout siting', '1001110', 'Gas and fire detection in a tankage area', 'https://www.digitalrefining.com/article/1001110/gas-and-fire-detection-in-a-tankage-area'),
    ('fire-gas-detection layout siting', '1002430', 'Refinery protection with gas detection', 'https://www.digitalrefining.com/article/1002430/refinery-protection-with-gas-detection'),
    ('fire-gas-detection layout siting', '1001033', 'Determining safety distance in process design', 'https://www.digitalrefining.com/article/1001033/determining-safety-distance-in-process-design'),
    ('fire-gas-detection layout siting', '1002772', 'Economical structural design of natural gas processing plants', 'https://www.digitalrefining.com/article/1002772/economical-structural-design-of-natural-gas-processing-plants'),
    ('hydrogen energy-transition ccus ammonia lng', '1003470', 'Transitioning refinery hydrogen systems from grey to green', 'https://www.digitalrefining.com/article/1003470/transitioning-refinery-hydrogen-systems-from-grey-to-green'),
    ('hydrogen energy-transition ccus ammonia lng', '1002868', 'Introducing hydrogen into refinery boilers, turbines and HRSGs (TIA)', 'https://www.digitalrefining.com/article/1002868/introducing-hydrogen-into-refinery-boilers-turbines-and-hrsgs-ti'),
    ('hydrogen energy-transition ccus ammonia lng', '1002449', 'CCS from refinery emissions: CO2 purity must be analysed and controlled', 'https://www.digitalrefining.com/article/1002449/ccs-from-refinery-emissions-co2-purity-must-be-analysed-and-controlled'),
    ('hydrogen energy-transition ccus ammonia lng', '1003307', 'Cracking the challenge of green energy: the vital role ammonia has to play', 'https://www.digitalrefining.com/article/1003307/cracking-the-challenge-of-green-energy-the-vital-role-ammonia-has-to-play'),
    ('hydrogen energy-transition ccus ammonia lng', '1000299', 'Catalyst catastrophes in hydrogen plants', 'https://www.digitalrefining.com/article/1000299/catalyst-catastrophes-in-hydrogen-plants'),
    ('hydrogen energy-transition ccus ammonia lng', '1000924', 'Reformer monitoring via in-tube temperature measurement', 'https://www.digitalrefining.com/article/1000924/reformer-monitoring-via-in-tube-temperature-measurement'),
    ('hydrogen energy-transition ccus ammonia lng', '1003081', 'Steam methane reformer tube lifecycle improvement best practices', 'https://www.digitalrefining.com/article/1003081/steam-methane-reformer-tube-lifecycle-improvement-best-practices'),
]
for _tags, _num, _title, _url in DIGITAL_REFINING:
    ENTRIES.append({"id": f"digital-refining-{_num}", "designation": f"DR {_num}", "title": _title, "body": "Digital Refining",
                    "category": "articles-digital-refining", "kind": "article", "access": "mixed", "region": "global", "url": _url,
                    "link": "document", "topics": _tags.split(), "note": "", "title_source": "search-listing"})


def main() -> None:
    old = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as fh:
            old = {e["id"]: e for e in json.load(fh)["entries"]}
    entries = ENTRIES
    wanted = dict(PDF_URL)
    for e in entries:
        key = f"{e['body']}-{e['designation']}"
        if key in wanted:
            e["pdf_url"] = wanted.pop(key)
    if wanted:
        raise SystemExit(f"PDF_URL keys with no entry: {sorted(wanted)}")
    ids = [e["id"] for e in entries]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        raise SystemExit(f"duplicate ids: {dup}")
    for e in entries:
        prev = old.get(e["id"])
        if prev and prev.get("url") == e["url"] and "http_status" in prev:
            keys = ["http_status", "check", "checked", "final_url"]
            if prev.get("pdf_url") == e.get("pdf_url"):
                keys.append("pdf_check")
            for k in keys:
                if k in prev:
                    e[k] = prev[k]
            if not e["title"] and prev.get("title"):
                e["title"], e["title_source"] = prev["title"], prev.get("title_source", "compiler")
            if prev.get("title_source") == "publisher-page":
                e["title"], e["title_source"] = prev["title"], "publisher-page"
        e.setdefault("title_source", "compiler")
    data = {"note": ("Index of standards, codes, regulations, guidance, books, databases and journals. No third-party text is "
                     "reproduced. Editions are not recorded: confirm the current edition and the edition your regulator or "
                     "contract cites. title_source 'compiler' means the title was typed by the compiler and not compared with "
                     "the publisher's page."),
            "entries": entries}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    print(len(entries), "entries written")


if __name__ == "__main__":
    main()

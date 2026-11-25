# Standards and literature library

Generated from `process_safety/data/standards_library.json`: 1521 entries. Regenerate with `python -m process_safety library --markdown > docs/STANDARDS_LIBRARY.md`. Search with `python -m process_safety library WORDS [--category C] [--body B] [--region R] [--kind K] [--access A]`.
The reading map by design activity is in [DESIGN_STANDARDS_RECOMMENDATIONS.md](DESIGN_STANDARDS_RECOMMENDATIONS.md).

## How far to trust an entry

* **Not a complete list of everything published.** It is a curated index; add missing documents in `scripts/build_standards_library.py`.
* **Editions are not recorded.** Confirm the current edition, and the edition your regulator or contract cites.
* **Title**: 565 titles were read from the publisher's page (marked `P`); 91 came from web-search result listings (`S`). The other 865 were typed by the compiler (`C`) and not compared with the publisher; confirm before citing. No document text was read for this library.
* **Link**: `document` links point to a page for that document. `catalogue` links point to the publisher's search or catalogue page: search there for the designation.
* **Check** (one automated request, 2026-11-25): blocked 128, error 16, ok 1057, pdf 11, robots 309. `blocked` means the site refuses automated clients (not bypassed): open it in a browser. `robots` means the site's robots.txt disallows this kind of agent, so the page was not requested. A reachable catalogue page does not show that a designation or title is right.
* **Access**: `free`, `free-registration`, `mixed` (some free, or free read-only), `paid`. Only publisher, regulator or rights-holder pages are linked. Paid standards are not copied into this repository.
* **PDFs**: 30 free official PDF links were confirmed to return a PDF. `python3 scripts/check_standards_library.py --pdf` rechecks them.

## Contents

* [Laws and regulations by jurisdiction](#laws-and-regulations-by-jurisdiction) (64)
* [Process safety management frameworks and guidance](#process-safety-management-frameworks-and-guidance) (69)
* [Hazard identification, risk assessment and reliability](#hazard-identification-risk-assessment-and-reliability) (37)
* [Functional safety, instrumentation, alarms and control-system security](#functional-safety-instrumentation-alarms-and-control-system-security) (30)
* [Relief, depressuring, venting and flare](#relief-depressuring-venting-and-flare) (16)
* [Pressure equipment, piping, tanks, heat transfer and rotating equipment codes](#pressure-equipment-piping-tanks-heat-transfer-and-rotating-equipment-codes) (109)
* [Mechanical integrity, inspection and fitness for service](#mechanical-integrity-inspection-and-fitness-for-service) (19)
* [Materials selection, corrosion and damage mechanisms](#materials-selection-corrosion-and-damage-mechanisms) (64)
* [ASTM steel pipe and tube specifications](#astm-steel-pipe-and-tube-specifications) (36)
* [ASTM plate and structural steel specifications](#astm-plate-and-structural-steel-specifications) (42)
* [ASTM forging, casting, flange and fitting specifications](#astm-forging-casting-flange-and-fitting-specifications) (36)
* [ASTM bolting, bar and fastener specifications](#astm-bolting-bar-and-fastener-specifications) (29)
* [ASTM nickel, titanium, zirconium, aluminium and copper specifications](#astm-nickel-titanium-zirconium-aluminium-and-copper-specifications) (94)
* [ASTM plastics, FRP, elastomer, gasket and insulation standards](#astm-plastics-frp-elastomer-gasket-and-insulation-standards) (65)
* [ASTM mechanical, metallurgical and chemical-analysis test methods](#astm-mechanical-metallurgical-and-chemical-analysis-test-methods) (35)
* [ASTM corrosion test methods and practices](#astm-corrosion-test-methods-and-practices) (57)
* [ASTM oxygen-compatibility and hydrogen-embrittlement standards](#astm-oxygen-compatibility-and-hydrogen-embrittlement-standards) (18)
* [ASTM nondestructive examination standards](#astm-nondestructive-examination-standards) (43)
* [ASTM flash point, flammability, dust and thermal-reactivity test methods](#astm-flash-point-flammability-dust-and-thermal-reactivity-test-methods) (43)
* [ASTM fire test methods](#astm-fire-test-methods) (31)
* [ASTM electrical, arc-flash and protective-equipment standards](#astm-electrical-arc-flash-and-protective-equipment-standards) (29)
* [ASTM gas analysis methods](#astm-gas-analysis-methods) (7)
* [Welding, hot work and examination qualification](#welding-hot-work-and-examination-qualification) (17)
* [Fire protection: active, passive, detection and fire modelling](#fire-protection-active-passive-detection-and-fire-modelling) (60)
* [Explosion, deflagration, blast and combustible dust](#explosion-deflagration-blast-and-combustible-dust) (38)
* [Hazardous areas, electrical safety, static and lightning](#hazardous-areas-electrical-safety-static-and-lightning) (41)
* [Layout, facility siting, buildings and human factors](#layout-facility-siting-buildings-and-human-factors) (19)
* [Reactive hazards, flammable liquids and hazardous materials storage](#reactive-hazards-flammable-liquids-and-hazardous-materials-storage) (20)
* [Substance-specific and energy-transition safety](#substance-specific-and-energy-transition-safety) (67)
* [Pipelines and offshore](#pipelines-and-offshore) (36)
* [Safe work and operations](#safe-work-and-operations) (17)
* [Open research reports on fire and release modelling](#open-research-reports-on-fire-and-release-modelling) (4)
* [Modelling tools, chemical property and exposure data](#modelling-tools-chemical-property-and-exposure-data) (19)
* [Incident investigations and loss databases](#incident-investigations-and-loss-databases) (19)
* [India: standards and agencies](#india-standards-and-agencies) (31)
* [Books, handbooks and learning](#books-handbooks-and-learning) (16)
* [Journals, open-access repositories and research centres](#journals-open-access-repositories-and-research-centres) (31)
* [Digital Refining articles on safety and design (unread; found by search)](#digital-refining-articles-on-safety-and-design-unread-found-by-search) (91)
* [Where to read or buy standards lawfully](#where-to-read-or-buy-standards-lawfully) (22)

## Laws and regulations by jurisdiction

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [29 CFR 1910.119](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) | Process safety management of highly hazardous chemicals | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.106](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.106) | Flammable liquids | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.109](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.109) | Explosives and blasting agents | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.110](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.110) | Storage and handling of liquefied petroleum gases | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.111](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.111) | Storage and handling of anhydrous ammonia | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.103](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.103) | Hydrogen | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.104](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.104) | Oxygen | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.120](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.120) | Hazardous waste operations and emergency response | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.146](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.146) | Permit-required confined spaces | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.147](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.147) | Control of hazardous energy (lockout/tagout) | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.252](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.252) | Welding, cutting and brazing: general requirements | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.307](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.307) | Hazardous (classified) locations | OSHA | US | free | document | C | ok |  |
| [29 CFR 1910.1200](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.1200) | Hazard communication | OSHA | US | free | document | C | ok |  |
| [40 CFR Part 68](https://www.ecfr.gov/current/title-40) | Chemical accident prevention provisions (Risk Management Program) | EPA | US | free | catalogue | C | ok |  |
| [40 CFR Part 112](https://www.ecfr.gov/current/title-40) | Oil pollution prevention (SPCC) | EPA | US | free | catalogue | C | ok |  |
| [40 CFR Part 355](https://www.ecfr.gov/current/title-40) | Emergency planning and notification (EPCRA) | EPA | US | free | catalogue | C | ok |  |
| [49 CFR Part 192](https://www.ecfr.gov/current/title-49) | Transportation of natural and other gas by pipeline: minimum federal safety standards | PHMSA | US | free | catalogue | C | ok |  |
| [49 CFR Part 193](https://www.ecfr.gov/current/title-49) | Liquefied natural gas facilities: federal safety standards | PHMSA | US | free | catalogue | C | ok |  |
| [49 CFR Part 195](https://www.ecfr.gov/current/title-49) | Transportation of hazardous liquids by pipeline | PHMSA | US | free | catalogue | C | ok |  |
| [49 CFR Parts 171-180](https://www.ecfr.gov/current/title-49) | Hazardous materials regulations (transport) | PHMSA | US | free | catalogue | C | ok |  |
| [33 CFR Part 127](https://www.ecfr.gov/current/title-33) | Waterfront facilities handling LNG and liquefied hazardous gas | USCG | US | free | catalogue | C | ok |  |
| [Directive 2012/18/EU](https://eur-lex.europa.eu/eli/dir/2012/18/oj) | Control of major-accident hazards involving dangerous substances (Seveso III) | EU | EU | free | document | C | ok |  |
| [Directive 2014/34/EU](https://eur-lex.europa.eu/eli/dir/2014/34/oj) | Equipment and protective systems for potentially explosive atmospheres (ATEX equipment) | EU | EU | free | document | C | ok |  |
| [Directive 1999/92/EC](https://eur-lex.europa.eu/eli/dir/1999/92/oj) | Protection of workers at risk from explosive atmospheres (ATEX workplace) | EU | EU | free | document | C | ok |  |
| [Directive 2014/68/EU](https://eur-lex.europa.eu/eli/dir/2014/68/oj) | Pressure Equipment Directive | EU | EU | free | document | C | ok |  |
| [Directive 2006/42/EC](https://eur-lex.europa.eu/eli/dir/2006/42/oj) | Machinery Directive | EU | EU | free | document | C | ok | Being replaced by Regulation (EU) 2023/1230. |
| [Regulation (EU) 2023/1230](https://eur-lex.europa.eu/eli/reg/2023/1230/oj) | Machinery Regulation | EU | EU | free | document | C | ok |  |
| [Directive 98/24/EC](https://eur-lex.europa.eu/eli/dir/1998/24/oj) | Chemical agents at work | EU | EU | free | document | C | ok |  |
| [Directive 89/391/EEC](https://eur-lex.europa.eu/eli/dir/1989/391/oj) | Framework directive on safety and health at work | EU | EU | free | document | C | ok |  |
| [Directive 2013/30/EU](https://eur-lex.europa.eu/eli/dir/2013/30/oj) | Safety of offshore oil and gas operations | EU | EU | free | document | C | ok |  |
| [Regulation (EC) 1272/2008](https://eur-lex.europa.eu/eli/reg/2008/1272/oj) | Classification, labelling and packaging (CLP) | EU | EU | free | document | C | ok |  |
| [Regulation (EC) 1907/2006](https://eur-lex.europa.eu/eli/reg/2006/1907/oj) | REACH | EU | EU | free | document | C | ok |  |
| [Directive (EU) 2022/2555](https://eur-lex.europa.eu/eli/dir/2022/2555/oj) | NIS2 cybersecurity directive | EU | EU | free | document | C | ok |  |
| [SI 2015/483](https://www.legislation.gov.uk/uksi/2015/483/contents) | Control of Major Accident Hazards Regulations 2015 (COMAH) | UK legislation | UK | free | document | C | blocked |  |
| [SI 2002/2776](https://www.legislation.gov.uk/uksi/2002/2776/contents) | Dangerous Substances and Explosive Atmospheres Regulations 2002 (DSEAR) | UK legislation | UK | free | document | C | blocked |  |
| [SI 2000/128](https://www.legislation.gov.uk/uksi/2000/128/contents) | Pressure Systems Safety Regulations 2000 | UK legislation | UK | free | document | C | blocked |  |
| [SI 1996/825](https://www.legislation.gov.uk/uksi/1996/825/contents) | Pipelines Safety Regulations 1996 | UK legislation | UK | free | document | C | blocked |  |
| [SI 2015/398](https://www.legislation.gov.uk/uksi/2015/398/contents) | Offshore Installations (Offshore Safety Directive) (Safety Case etc.) Regulations 2015 | UK legislation | UK | free | document | C | blocked |  |
| [SI 2015/51](https://www.legislation.gov.uk/uksi/2015/51/contents) | Construction (Design and Management) Regulations 2015 | UK legislation | UK | free | document | C | blocked |  |
| [MSIHC Rules 1989](https://moef.gov.in/) | Manufacture, Storage and Import of Hazardous Chemicals Rules | India | IN | free | catalogue | C | ok |  |
| [EPPR Rules 1996](https://moef.gov.in/) | Chemical Accidents (Emergency Planning, Preparedness and Response) Rules | India | IN | free | catalogue | C | ok |  |
| [Factories Act 1948](https://www.indiacode.nic.in/) | Factories Act, including hazardous-process provisions (Chapter IVA) | India | IN | free | catalogue | C | ok |  |
| [OSH Code 2020](https://www.indiacode.nic.in/) | Occupational Safety, Health and Working Conditions Code, 2020 | India | IN | free | catalogue | C | ok | Check which provisions and state rules are in force before relying on either law. |
| [SMPV(U) Rules 2016](https://peso.gov.in/) | Static and Mobile Pressure Vessels (Unfired) Rules | PESO | IN | free | catalogue | C | error |  |
| [Petroleum Rules 2002](https://peso.gov.in/) | Petroleum Rules | PESO | IN | free | catalogue | C | error |  |
| [Gas Cylinders Rules 2016](https://peso.gov.in/) | Gas Cylinders Rules | PESO | IN | free | catalogue | C | error |  |
| [Explosives Rules 2008](https://peso.gov.in/) | Explosives Rules | PESO | IN | free | catalogue | C | error |  |
| [Ammonium Nitrate Rules 2012](https://peso.gov.in/) | Ammonium Nitrate Rules | PESO | IN | free | catalogue | C | error |  |
| [Calcium Carbide Rules 1987](https://peso.gov.in/) | Calcium Carbide Rules | PESO | IN | free | catalogue | C | error |  |
| [PNGRB T4S: petroleum and gas installations](https://www.pngrb.gov.in/) | Technical standards and specifications including safety standards for refineries, terminals, pipelines and city gas distribution | PNGRB | IN | free | catalogue | C | ok |  |
| [PNGRB ERDMP Regulations](https://www.pngrb.gov.in/) | Emergency response and disaster management plan regulations | PNGRB | IN | free | catalogue | C | ok |  |
| [PNGRB Integrity Management System Regulations](https://www.pngrb.gov.in/) | Integrity management system for pipelines and city gas networks | PNGRB | IN | free | catalogue | C | ok |  |
| [CEA Safety Regulations](https://cea.nic.in/) | Central Electricity Authority (Measures relating to Safety and Electric Supply) Regulations | CEA | IN | free | catalogue | C | ok |  |
| [Singapore MHI](https://www.mom.gov.sg/workplace-safety-and-health/major-hazard-installations) | Workplace Safety and Health (Major Hazard Installations) regime | Other jurisdictions | intl | free | document | C | ok |  |
| [Australia MHF](https://www.safeworkaustralia.gov.au/safety-topic/industry-and-business/major-hazard-facilities) | Safe Work Australia: major hazard facilities | Other jurisdictions | intl | free | document | C | error |  |
| [Australia NOPSEMA](https://www.nopsema.gov.au/) | Offshore safety case regime | Other jurisdictions | intl | free | document | C | error |  |
| [Canada E2](https://laws-lois.justice.gc.ca/eng/regulations/SOR-2019-51/) | Environmental Emergency Regulations | Other jurisdictions | intl | free | document | C | ok |  |
| [Brazil NRs](https://www.gov.br/trabalho-e-emprego/pt-br) | Regulatory standards (NR-13 pressure equipment, NR-20 flammables, NR-33 confined spaces) | Other jurisdictions | intl | free | document | C | ok |  |
| [Malaysia DOSH](https://www.dosh.gov.my/) | Department of Occupational Safety and Health (CIMAH regulations) | Other jurisdictions | intl | free | document | C | error |  |
| [Korea KOSHA](https://www.kosha.or.kr/english/index.do) | Korea Occupational Safety and Health Agency (PSM system and KOSHA guides) | Other jurisdictions | intl | free | document | C | ok |  |
| [Japan KHK](https://www.khk.or.jp/english/) | High Pressure Gas Safety Institute of Japan | Other jurisdictions | intl | free | document | C | error |  |
| [China GB portal](https://openstd.samr.gov.cn/) | National standards full-text disclosure system (GB standards) | Other jurisdictions | intl | free | document | C | ok |  |
| [Saudi HCIS](https://www.hcis.gov.sa/) | High Commission for Industrial Security (security and safety directives) | Other jurisdictions | intl | free | document | C | error |  |
| [Abu Dhabi OSHAD](https://www.adphc.gov.ae/) | Occupational safety and health system framework | Other jurisdictions | intl | free | document | C | ok |  |

## Process safety management frameworks and guidance

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [CCPS RBPS](https://www.aiche.org/ccps/publications) | Guidelines for Risk Based Process Safety | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Management of Change](https://www.aiche.org/ccps/publications) | Guidelines for the Management of Change for Process Safety | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Process Safety Metrics](https://www.aiche.org/ccps/publications) | Guidelines for Process Safety Metrics | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Auditing](https://www.aiche.org/ccps/publications) | Guidelines for Auditing Process Safety Management Systems | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Incident Investigation](https://www.aiche.org/ccps/publications) | Guidelines for Investigating Process Safety Incidents | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Conduct of Operations](https://www.aiche.org/ccps/publications) | Conduct of Operations and Operational Discipline | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Asset Integrity](https://www.aiche.org/ccps/publications) | Guidelines for Asset Integrity Management | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Operating Procedures](https://www.aiche.org/ccps/publications) | Guidelines for Writing Effective Operating and Maintenance Procedures | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Pre-Startup](https://www.aiche.org/ccps/publications) | Guidelines for Performing Effective Pre-Startup Safety Reviews | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Emergency Planning](https://www.aiche.org/ccps/publications) | Guidelines for Technical Planning for On-Site Emergencies | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Engineering Design](https://www.aiche.org/ccps/publications) | Guidelines for Engineering Design for Process Safety | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Design Solutions](https://www.aiche.org/ccps/publications) | Guidelines for Design Solutions for Process Equipment Failures | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Safe Automation](https://www.aiche.org/ccps/publications) | Guidelines for Safe Automation of Chemical Processes | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Inherently Safer](https://www.aiche.org/ccps/publications) | Inherently Safer Chemical Processes: A Life Cycle Approach | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Capital Projects](https://www.aiche.org/ccps/publications) | Guidelines for Integrating Process Safety into Engineering Projects | CCPS | global | paid | catalogue | C | robots |  |
| [OSHA 3132](https://www.osha.gov/sites/default/files/publications/osha3132.pdf) | Process Safety Management (booklet) | OSHA | US | free | document | C | pdf |  |
| [OSHA 3133](https://www.osha.gov/sites/default/files/publications/osha3133.pdf) | Process Safety Management Guidelines for Compliance | OSHA | US | free | document | C | pdf |  |
| [OSHA PSM topic page](https://www.osha.gov/process-safety-management) | Process safety management topic page, directives and emphasis programme | OSHA | US | free | document | C | ok |  |
| [DOE-HDBK-1101](https://www.standards.doe.gov/) | Process Safety Management for Highly Hazardous Chemicals | DOE | US | free | catalogue | C | ok |  |
| [DOE-HDBK-1100](https://www.standards.doe.gov/) | Chemical Process Hazards Analysis | DOE | US | free | catalogue | C | ok |  |
| [DOE-STD-1189](https://www.standards.doe.gov/) | Integration of Safety into the Design Process | DOE | US | free | catalogue | C | ok |  |
| [DOE-STD-3009](https://www.standards.doe.gov/) | Preparation of nonreactor nuclear facility documented safety analysis | DOE | US | free | catalogue | C | ok |  |
| [DOE-HDBK-3010](https://www.standards.doe.gov/) | Airborne release fractions/rates and respirable fractions for nonreactor nuclear facilities | DOE | US | free | catalogue | C | ok |  |
| [HSG65](https://www.hse.gov.uk/pubns/books/hsg65.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg65.pdf)) | Managing for health and safety | HSE | UK | free | document | C | ok |  |
| [HSG254](https://www.hse.gov.uk/pubns/books/hsg254.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg254.pdf)) | Developing process safety indicators | HSE | UK | free | document | C | ok |  |
| [HSG48](https://www.hse.gov.uk/pubns/books/hsg48.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg48.pdf)) | Reducing error and influencing behaviour | HSE | UK | free | document | C | ok |  |
| [HSG253](https://www.hse.gov.uk/pubns/books/hsg253.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg253.pdf)) | The safe isolation of plant and equipment | HSE | UK | free | document | C | ok |  |
| [HSG250](https://www.hse.gov.uk/pubns/books/hsg250.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg250.pdf)) | Guidance on permit-to-work systems | HSE | UK | free | document | C | ok |  |
| [HSG176](https://www.hse.gov.uk/pubns/books/hsg176.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg176.pdf)) | The storage of flammable liquids in tanks | HSE | UK | free | document | C | ok |  |
| [HSG51](https://www.hse.gov.uk/pubns/books/hsg51.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg51.pdf)) | The storage of flammable liquids in containers | HSE | UK | free | document | C | ok |  |
| [HSG140](https://www.hse.gov.uk/pubns/books/hsg140.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg140.pdf)) | Safe use and handling of flammable liquids | HSE | UK | free | document | C | ok |  |
| [HSG71](https://www.hse.gov.uk/pubns/books/hsg71.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg71.pdf)) | Chemical warehousing: the storage of packaged dangerous substances | HSE | UK | free | document | C | ok |  |
| [HSG103](https://www.hse.gov.uk/pubns/books/hsg103.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg103.pdf)) | Safe handling of combustible dusts | HSE | UK | free | document | C | ok |  |
| [HSG244](https://www.hse.gov.uk/pubns/books/hsg244.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg244.pdf)) | Remotely operated shutoff valves (ROSOVs) for emergency isolation | HSE | UK | free | document | C | ok |  |
| [HSG143](https://www.hse.gov.uk/pubns/books/hsg143.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/hsg143.pdf)) | Designing and operating safe chemical reaction processes | HSE | UK | free | document | C | ok |  |
| [L111](https://www.hse.gov.uk/pubns/books/l111.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/l111.pdf)) | The Control of Major Accident Hazards Regulations 2015: guidance on regulations | HSE | UK | free | document | C | ok |  |
| [L138](https://www.hse.gov.uk/pubns/books/l138.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/l138.pdf)) | Dangerous substances and explosive atmospheres: approved code of practice and guidance | HSE | UK | free | document | C | ok |  |
| [L122](https://www.hse.gov.uk/pubns/books/l122.htm) ([PDF](https://www.hse.gov.uk/pubns/priced/l122.pdf)) | Safety of pressure systems: approved code of practice | HSE | UK | free | document | C | ok |  |
| [INDG370](https://www.hse.gov.uk/pubns/indg370.htm) ([PDF](https://www.hse.gov.uk/pubns/indg370.pdf)) | Controlling fire and explosion risks in the workplace | HSE | UK | free | document | C | ok |  |
| [HSE COMAH](https://www.hse.gov.uk/comah/) | COMAH guidance pages | HSE | UK | free | document | C | ok |  |
| [HSE PCAG advice](https://www.hse.gov.uk/landuseplanning/) | Land use planning advice around major hazard sites | HSE | UK | free | document | C | ok |  |
| [HSE research reports](https://www.hse.gov.uk/research/rrhtm/) | Research report series (RR) | HSE | UK | free | document | C | ok |  |
| [IFC EHS Guidelines](https://www.ifc.org/content/dam/ifc/doc/2023/ifc-general-ehs-guidelines.pdf) | Environmental, Health and Safety Guidelines (general and industry-sector) | IFC / World Bank | global | free | document | C | pdf |  |
| [ILO C174](https://normlex.ilo.org/dyn/normlex/en/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C174) | Prevention of Major Industrial Accidents Convention | ILO | global | free | document | C | blocked |  |
| [OECD chemical accidents](https://www.oecd.org/en/topics/sub-issues/chemical-accidents.html) | Programme on chemical accidents: guiding principles for prevention, preparedness and response | OECD | global | free | document | C | blocked |  |
| [GHS (Purple Book)](https://unece.org/about-ghs) | Globally Harmonized System of Classification and Labelling of Chemicals | UNECE | global | free | document | C | blocked |  |
| [UN Model Regulations (Orange Book)](https://unece.org/transport/dangerous-goods) | Recommendations on the Transport of Dangerous Goods | UNECE | global | free | document | C | blocked |  |
| [UN Manual of Tests and Criteria](https://unece.org/transport/dangerous-goods/un-manual-tests-and-criteria) | Test methods for classifying explosives, self-reactives, peroxides and flammables | UNECE | global | free | document | C | blocked |  |
| [TEIA Convention](https://unece.org/environment-policy/industrial-accidents) | Convention on the Transboundary Effects of Industrial Accidents | UNECE | global | free | document | C | blocked |  |
| [ISO 45001](https://www.iso.org/search.html?q=ISO%2045001) | Occupational health and safety management systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 14001](https://www.iso.org/search.html?q=ISO%2014001) | Environmental management systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 55001](https://www.iso.org/search.html?q=ISO%2055001) | Asset management: management system requirements | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 22301](https://www.iso.org/search.html?q=ISO%2022301) | Business continuity management systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 9001](https://www.iso.org/search.html?q=ISO%209001) | Quality management systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 29001](https://www.iso.org/search.html?q=ISO%2029001) | Quality management for the petroleum, petrochemical and natural gas industries | ISO | global | paid | catalogue | C | blocked |  |
| [API RP 754](https://publications.api.org/) | Process safety performance indicators for the refining and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [API RP 75](https://publications.api.org/) | Safety and environmental management system for offshore operations and assets | API | global | paid | catalogue | C | robots |  |
| [API RP 1173](https://publications.api.org/) | Pipeline safety management systems | API | global | paid | catalogue | C | robots |  |
| [AIGA 099](https://www.asiaiga.org/) | Process safety management guideline for industrial gases | AIGA | global | free | catalogue | C | error |  |
| [EI PSM Framework](https://www.energyinst.org/technical/publications) | High level framework for process safety management | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [IOGP 456](https://www.iogp.org/bookstore/) | Process safety: recommended practice on key performance indicators | IOGP | global | free | catalogue | C | ok |  |
| [IOGP 510](https://www.iogp.org/bookstore/) | Operating Management System Framework | IOGP | global | free | catalogue | C | ok |  |
| [IOGP 459](https://www.iogp.org/bookstore/) | Life-Saving Rules | IOGP | global | free | catalogue | C | ok |  |
| [IOGP 415](https://www.iogp.org/bookstore/) | Asset integrity: the key to managing major incident risks | IOGP | global | free | catalogue | C | ok |  |
| [IOGP 544](https://www.iogp.org/bookstore/) | Standardization of barrier definitions | IOGP | global | free | catalogue | C | ok |  |
| [OSHA 3918](https://www.osha.gov/sites/default/files/publications/OSHA3918.pdf) | Process Safety Management for Petroleum Refineries | OSHA | US | free | document | C | pdf |  |
| [OSHA 3908](https://www.osha.gov/sites/default/files/publications/OSHA3908.pdf) | Process Safety Management for Small Businesses | OSHA | US | free | document | C | pdf |  |
| [OSHA 3909](https://www.osha.gov/sites/default/files/publications/OSHA3909.pdf) | Process Safety Management for Storage Facilities | OSHA | US | free | document | C | pdf |  |
| [OSHA 3912](https://www.osha.gov/sites/default/files/publications/OSHA3912.pdf) | Process Safety Management for Explosives and Pyrotechnics Manufacturing | OSHA | US | free | document | C | pdf |  |

## Hazard identification, risk assessment and reliability

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [IEC 61882](https://webstore.iec.ch/) | Hazard and operability studies (HAZOP studies): application guide | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60812](https://webstore.iec.ch/) | Failure modes and effects analysis (FMEA and FMECA) | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61025](https://webstore.iec.ch/) | Fault tree analysis | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62502](https://webstore.iec.ch/) | Event tree analysis | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61078](https://webstore.iec.ch/) | Reliability block diagrams | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61165](https://webstore.iec.ch/) | Application of Markov techniques | IEC | global | paid | catalogue | C | ok |  |
| [IEC 31010](https://webstore.iec.ch/) | Risk management: risk assessment techniques | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62740](https://webstore.iec.ch/) | Root cause analysis | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62508](https://webstore.iec.ch/) | Guidance on human aspects of dependability | IEC | global | paid | catalogue | C | ok |  |
| [ISO 31000](https://www.iso.org/search.html?q=ISO%2031000) | Risk management: guidelines | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 17776](https://www.iso.org/search.html?q=ISO%2017776) | Offshore installations: major accident hazard management during design | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 12100](https://www.iso.org/search.html?q=ISO%2012100) | Safety of machinery: risk assessment and risk reduction | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 14224](https://www.iso.org/search.html?q=ISO%2014224) | Collection and exchange of reliability and maintenance data for equipment | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 20815](https://www.iso.org/search.html?q=ISO%2020815) | Production assurance and reliability management | ISO | global | paid | catalogue | C | blocked |  |
| [CCPS HEP](https://www.aiche.org/ccps/publications) | Guidelines for Hazard Evaluation Procedures | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS CPQRA](https://www.aiche.org/ccps/publications) | Guidelines for Chemical Process Quantitative Risk Analysis | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS LOPA](https://www.aiche.org/ccps/publications) | Layer of Protection Analysis: Simplified Process Risk Assessment | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS IEs and IPLs](https://www.aiche.org/ccps/publications) | Guidelines for Initiating Events and Independent Protection Layers in LOPA | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Enabling Conditions](https://www.aiche.org/ccps/publications) | Guidelines for Enabling Conditions and Conditional Modifiers in LOPA | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Bow Ties](https://www.aiche.org/ccps/publications) | Bow Ties in Risk Management | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Risk Criteria](https://www.aiche.org/ccps/publications) | Guidelines for Developing Quantitative Safety Risk Criteria | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS PERD](https://www.aiche.org/ccps/publications) | Guidelines for Process Equipment Reliability Data | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Revalidating PHA](https://www.aiche.org/ccps/publications) | Revalidating Process Hazard Analyses | CCPS | global | paid | catalogue | C | robots |  |
| [PGS 3 (CPR 18E) Purple Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Guidelines for quantitative risk assessment | TNO / PGS | NL | free | catalogue | C | ok |  |
| [PGS 4 (CPR 16E) Red Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for determining and processing probabilities | TNO / PGS | NL | free | catalogue | C | ok |  |
| [PGS 1 (CPR 16) Green Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for the determination of possible damage to people and objects | TNO / PGS | NL | free | catalogue | C | ok |  |
| [PGS 2 (CPR 14E) Yellow Book](https://publicatiereeksgevaarlijkestoffen.nl/) | Methods for the calculation of physical effects | TNO / PGS | NL | free | catalogue | C | ok |  |
| [Reference Manual Bevi Risk Assessments](https://www.rivm.nl/en) | Dutch reference manual for quantitative risk assessment | RIVM | NL | free | document | C | ok |  |
| [IOGP 434 series](https://www.iogp.org/bookstore/) | Risk Assessment Data Directory (process release, ignition, vulnerability and other data sheets) | IOGP | global | free | catalogue | C | ok | Some sheets have been revised or withdrawn; check the bookstore. |
| [PDS Data Handbook](https://www.sintef.no/en/) | Reliability data for safety equipment | SINTEF | NO | paid | catalogue | C | blocked |  |
| [PDS Method Handbook](https://www.sintef.no/en/) | Reliability prediction method for safety instrumented systems | SINTEF | NO | paid | catalogue | C | blocked |  |
| [OREDA Handbook](https://www.oreda.com/) | Offshore and onshore reliability data | OREDA | global | paid | catalogue | C | ok |  |
| [exida SERH](https://www.exida.com/) | Safety Equipment Reliability Handbook | exida | global | paid | catalogue | C | ok |  |
| [EI Ignition probability review](https://www.energyinst.org/technical/publications) | Model for estimating ignition probability (IP research report and look-up correlations) | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI Bow tie guidance](https://www.energyinst.org/technical/publications) | Hazard management barrier model guidance (with CCPS) | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [NORSOK Z-013](https://standard.no/en/sectors/petroleum/norsok-standards/) | Risk and emergency preparedness assessment | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK Z-008](https://standard.no/en/sectors/petroleum/norsok-standards/) | Risk based maintenance and consequence classification | NORSOK | NO | mixed | catalogue | C | ok |  |

## Functional safety, instrumentation, alarms and control-system security

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [IEC 61508 (all parts)](https://webstore.iec.ch/) | Functional safety of electrical/electronic/programmable electronic safety-related systems | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61511 (all parts)](https://webstore.iec.ch/) | Functional safety: safety instrumented systems for the process industry sector | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62061](https://webstore.iec.ch/) | Safety of machinery: functional safety of safety-related control systems | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62682](https://webstore.iec.ch/) | Management of alarm systems for the process industries | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62443 (series)](https://webstore.iec.ch/) | Security for industrial automation and control systems | IEC | global | paid | catalogue | C | ok |  |
| [IEC TS 63069](https://webstore.iec.ch/) | Framework for functional safety and security | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61513](https://webstore.iec.ch/) | Nuclear power plants: instrumentation and control important to safety | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60534 (series)](https://webstore.iec.ch/) | Industrial-process control valves | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60584](https://webstore.iec.ch/) | Thermocouples | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60529](https://webstore.iec.ch/) | Degrees of protection provided by enclosures (IP code) | IEC | global | paid | catalogue | C | ok |  |
| [ISA-84.00.01](https://www.isa.org/standards-and-publications/isa-standards) | Functional safety: safety instrumented systems for the process industry sector (adoption of IEC 61511) | ISA | global | paid | catalogue | C | ok |  |
| [ISA-TR84.00.02](https://www.isa.org/standards-and-publications/isa-standards) | Safety integrity level verification of safety instrumented functions | ISA | global | paid | catalogue | C | ok |  |
| [ISA-TR84.00.04](https://www.isa.org/standards-and-publications/isa-standards) | Guidelines for implementation of ISA-84.00.01 | ISA | global | paid | catalogue | C | ok |  |
| [ISA-TR84.00.07](https://www.isa.org/standards-and-publications/isa-standards) | Guidance on the evaluation of fire, combustible gas and toxic gas system effectiveness | ISA | global | paid | catalogue | C | ok |  |
| [ISA-18.2](https://www.isa.org/standards-and-publications/isa-standards) | Management of alarm systems for the process industries | ISA | global | paid | catalogue | C | ok |  |
| [ISA-101.01](https://www.isa.org/standards-and-publications/isa-standards) | Human machine interfaces for process automation systems | ISA | global | paid | catalogue | C | ok |  |
| [ISA-5.1](https://www.isa.org/standards-and-publications/isa-standards) | Instrumentation symbols and identification | ISA | global | paid | catalogue | C | ok |  |
| [ISA-62443 (series)](https://www.isa.org/standards-and-publications/isa-standards) | Security for industrial automation and control systems | ISA | global | paid | catalogue | C | ok |  |
| [ISA-106](https://www.isa.org/standards-and-publications/isa-standards) | Procedure automation for continuous process operations | ISA | global | paid | catalogue | C | ok |  |
| [API RP 554](https://publications.api.org/) | Process control systems | API | global | paid | catalogue | C | robots |  |
| [API RP 551](https://publications.api.org/) | Process measurement | API | global | paid | catalogue | C | robots |  |
| [API RP 556](https://publications.api.org/) | Instrumentation, control and protective systems for gas fired heaters | API | global | paid | catalogue | C | robots |  |
| [API STD 670](https://publications.api.org/) | Machinery protection systems | API | global | paid | catalogue | C | robots |  |
| [API RP 14C](https://publications.api.org/) | Analysis, design, installation and testing of safety systems for offshore production facilities | API | global | paid | catalogue | C | robots |  |
| [API STD 2350](https://publications.api.org/) | Overfill prevention for storage tanks in petroleum facilities | API | global | paid | catalogue | C | robots |  |
| [EEMUA 191](https://www.eemua.org/) | Alarm systems: a guide to design, management and procurement | EEMUA | global | paid | catalogue | C | blocked |  |
| [EEMUA 201](https://www.eemua.org/) | Control rooms: a guide to their specification, design, commissioning and operation | EEMUA | global | paid | catalogue | C | blocked |  |
| [EEMUA 222](https://www.eemua.org/) | Guide to the application of IEC 61511 | EEMUA | global | paid | catalogue | C | blocked |  |
| [NIST SP 800-82](https://csrc.nist.gov/pubs/sp/800/82/r3/final) ([PDF](https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-82r3.pdf)) | Guide to Operational Technology (OT) Security | NIST | US | free | document | C | ok | This link is Revision 3. |
| [NAMUR recommendations](https://www.namur.net/) | Process automation worksheets and recommendations (e.g. NE 43, NE 107) | NAMUR | EU | mixed | catalogue | C | ok |  |

## Relief, depressuring, venting and flare

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [API STD 520 Part I](https://publications.api.org/) | Sizing, selection and installation of pressure-relieving devices: sizing and selection | API | global | paid | catalogue | C | robots |  |
| [API RP 520 Part II](https://publications.api.org/) | Sizing, selection and installation of pressure-relieving devices: installation | API | global | paid | catalogue | C | robots |  |
| [API STD 521](https://publications.api.org/) | Pressure-relieving and depressuring systems | API | global | paid | catalogue | C | robots |  |
| [API STD 526](https://publications.api.org/) | Flanged steel pressure-relief valves | API | global | paid | catalogue | C | robots |  |
| [API STD 527](https://publications.api.org/) | Seat tightness of pressure relief valves | API | global | paid | catalogue | C | robots |  |
| [API STD 537](https://publications.api.org/) | Flare details for petroleum, petrochemical and natural gas industries | API | global | paid | catalogue | C | robots |  |
| [API STD 2000](https://publications.api.org/) | Venting atmospheric and low-pressure storage tanks | API | global | paid | catalogue | C | robots |  |
| [API RP 576](https://publications.api.org/) | Inspection of pressure-relieving devices | API | global | paid | catalogue | C | robots |  |
| [ISO 4126 (all parts)](https://www.iso.org/search.html?q=ISO%204126%20%28all%20parts%29) | Safety devices for protection against excessive pressure | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 28300](https://www.iso.org/search.html?q=ISO%2028300) | Venting of atmospheric and low-pressure storage tanks | ISO | global | paid | catalogue | C | blocked |  |
| [ASME BPVC XIII](https://www.asme.org/codes-standards) | Rules for overpressure protection | ASME | global | paid | catalogue | C | ok |  |
| [ASME PTC 25](https://www.asme.org/codes-standards) | Pressure relief devices: performance test codes | ASME | global | paid | catalogue | C | ok |  |
| [CCPS Pressure Relief and Effluent Handling](https://www.aiche.org/ccps/publications) | Guidelines for Pressure Relief and Effluent Handling Systems | DIERS / CCPS | global | paid | catalogue | C | robots |  |
| [DIERS Project Manual](https://www.aiche.org/ccps/publications) | Emergency relief system design using DIERS technology | DIERS / CCPS | global | paid | catalogue | C | robots |  |
| [DIERS Users Group](https://www.aiche.org/diers) | Design Institute for Emergency Relief Systems users group | AIChE DIERS | global | mixed | catalogue | C | robots |  |
| [EEMUA 231](https://www.eemua.org/) | Mechanical integrity of plant containing hazardous substances: a guide to periodic examination and testing | EEMUA | global | paid | catalogue | C | blocked |  |

## Pressure equipment, piping, tanks, heat transfer and rotating equipment codes

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASME BPVC I](https://www.asme.org/codes-standards) | Rules for construction of power boilers | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC III](https://www.asme.org/codes-standards) | Rules for construction of nuclear facility components | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC IV](https://www.asme.org/codes-standards) | Rules for construction of heating boilers | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC VIII Div 1](https://www.asme.org/codes-standards) | Rules for construction of pressure vessels | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC VIII Div 2](https://www.asme.org/codes-standards) | Pressure vessels: alternative rules | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC VIII Div 3](https://www.asme.org/codes-standards) | Pressure vessels: alternative rules for high pressure | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC X](https://www.asme.org/codes-standards) | Fiber-reinforced plastic pressure vessels | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC XII](https://www.asme.org/codes-standards) | Rules for construction and continued service of transport tanks | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.1](https://www.asme.org/codes-standards) | Power piping | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.3](https://www.asme.org/codes-standards) | Process piping | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.4](https://www.asme.org/codes-standards) | Pipeline transportation systems for liquids and slurries | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.5](https://www.asme.org/codes-standards) | Refrigeration piping and heat transfer components | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.8](https://www.asme.org/codes-standards) | Gas transmission and distribution piping systems | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.8S](https://www.asme.org/codes-standards) | Managing system integrity of gas pipelines | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.9](https://www.asme.org/codes-standards) | Building services piping | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31.12](https://www.asme.org/codes-standards) | Hydrogen piping and pipelines | ASME | global | paid | catalogue | C | ok |  |
| [ASME B31G](https://www.asme.org/codes-standards) | Manual for determining the remaining strength of corroded pipelines | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.5](https://www.asme.org/codes-standards) | Pipe flanges and flanged fittings (NPS 1/2 through NPS 24) | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.47](https://www.asme.org/codes-standards) | Large diameter steel flanges | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.9](https://www.asme.org/codes-standards) | Factory-made wrought buttwelding fittings | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.11](https://www.asme.org/codes-standards) | Forged fittings, socket-welding and threaded | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.20](https://www.asme.org/codes-standards) | Metallic gaskets for pipe flanges | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.21](https://www.asme.org/codes-standards) | Nonmetallic flat gaskets for pipe flanges | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.34](https://www.asme.org/codes-standards) | Valves: flanged, threaded and welding end | ASME | global | paid | catalogue | C | ok |  |
| [ASME B16.48](https://www.asme.org/codes-standards) | Line blanks | ASME | global | paid | catalogue | C | ok |  |
| [ASME B36.10M](https://www.asme.org/codes-standards) | Welded and seamless wrought steel pipe (dimensions) | ASME | global | paid | catalogue | C | ok |  |
| [ASME B36.19M](https://www.asme.org/codes-standards) | Stainless steel pipe (dimensions) | ASME | global | paid | catalogue | C | ok |  |
| [ASME B73.1](https://www.asme.org/codes-standards) | Horizontal end suction centrifugal pumps for chemical process | ASME | global | paid | catalogue | C | ok |  |
| [ASME B30 (series)](https://www.asme.org/codes-standards) | Cableways, cranes, derricks, hoists and related equipment | ASME | global | paid | catalogue | C | ok |  |
| [ASME A13.1](https://www.asme.org/codes-standards) | Scheme for the identification of piping systems | ASME | global | paid | catalogue | C | ok |  |
| [ASME PCC-1](https://www.asme.org/codes-standards) | Pressure boundary bolted flange joint assembly | ASME | global | paid | catalogue | C | ok |  |
| [ASME PCC-2](https://www.asme.org/codes-standards) | Repair of pressure equipment and piping | ASME | global | paid | catalogue | C | ok |  |
| [ASME PCC-3](https://www.asme.org/codes-standards) | Inspection planning using risk-based methods | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPE](https://www.asme.org/codes-standards) | Bioprocessing equipment | ASME | global | paid | catalogue | C | ok |  |
| [ASME RTP-1](https://www.asme.org/codes-standards) | Reinforced thermoset plastic corrosion-resistant equipment | ASME | global | paid | catalogue | C | ok |  |
| [ASME NM.1](https://www.asme.org/codes-standards) | Thermoplastic piping systems | ASME | global | paid | catalogue | C | ok |  |
| [ASME STS-1](https://www.asme.org/codes-standards) | Steel stacks | ASME | global | paid | catalogue | C | ok |  |
| [API STD 650](https://publications.api.org/) | Welded tanks for oil storage | API | global | paid | catalogue | C | robots |  |
| [API STD 620](https://publications.api.org/) | Design and construction of large, welded, low-pressure storage tanks | API | global | paid | catalogue | C | robots |  |
| [API STD 625](https://publications.api.org/) | Tank systems for refrigerated liquefied gas storage | API | global | paid | catalogue | C | robots |  |
| [API STD 2510](https://publications.api.org/) | Design and construction of LPG installations | API | global | paid | catalogue | C | robots |  |
| [API STD 660](https://publications.api.org/) | Shell-and-tube heat exchangers | API | global | paid | catalogue | C | robots |  |
| [API STD 661](https://publications.api.org/) | Air-cooled heat exchangers for general refinery service | API | global | paid | catalogue | C | robots |  |
| [API STD 662](https://publications.api.org/) | Plate heat exchangers | API | global | paid | catalogue | C | robots |  |
| [API STD 560](https://publications.api.org/) | Fired heaters for general refinery service | API | global | paid | catalogue | C | robots |  |
| [API STD 530](https://publications.api.org/) | Calculation of heater-tube thickness in petroleum refineries | API | global | paid | catalogue | C | robots |  |
| [API STD 610](https://publications.api.org/) | Centrifugal pumps for petroleum, petrochemical and natural gas industries | API | global | paid | catalogue | C | robots |  |
| [API STD 617](https://publications.api.org/) | Axial and centrifugal compressors and expander-compressors | API | global | paid | catalogue | C | robots |  |
| [API STD 618](https://publications.api.org/) | Reciprocating compressors | API | global | paid | catalogue | C | robots |  |
| [API STD 619](https://publications.api.org/) | Rotary-type positive-displacement compressors | API | global | paid | catalogue | C | robots |  |
| [API STD 674](https://publications.api.org/) | Positive displacement pumps: reciprocating | API | global | paid | catalogue | C | robots |  |
| [API STD 675](https://publications.api.org/) | Positive displacement pumps: controlled volume | API | global | paid | catalogue | C | robots |  |
| [API STD 676](https://publications.api.org/) | Positive displacement pumps: rotary | API | global | paid | catalogue | C | robots |  |
| [API STD 685](https://publications.api.org/) | Sealless centrifugal pumps | API | global | paid | catalogue | C | robots |  |
| [API STD 682](https://publications.api.org/) | Pumps: shaft sealing systems for centrifugal and rotary pumps | API | global | paid | catalogue | C | robots |  |
| [API STD 614](https://publications.api.org/) | Lubrication, shaft-sealing and oil-control systems and auxiliaries | API | global | paid | catalogue | C | robots |  |
| [API STD 612](https://publications.api.org/) | Special-purpose steam turbines | API | global | paid | catalogue | C | robots |  |
| [API STD 616](https://publications.api.org/) | Gas turbines for the petroleum, chemical and gas industry services | API | global | paid | catalogue | C | robots |  |
| [API STD 672](https://publications.api.org/) | Packaged, integrally geared centrifugal air compressors | API | global | paid | catalogue | C | robots |  |
| [API STD 673](https://publications.api.org/) | Centrifugal fans | API | global | paid | catalogue | C | robots |  |
| [API RP 686](https://publications.api.org/) | Machinery installation and installation design | API | global | paid | catalogue | C | robots |  |
| [API SPEC 5L](https://publications.api.org/) | Line pipe | API | global | paid | catalogue | C | robots |  |
| [API SPEC 6A](https://publications.api.org/) | Wellhead and tree equipment | API | global | paid | catalogue | C | robots |  |
| [API SPEC 6D](https://publications.api.org/) | Pipeline and piping valves | API | global | paid | catalogue | C | robots |  |
| [API STD 594](https://publications.api.org/) | Check valves: flanged, lug, wafer and butt-welding | API | global | paid | catalogue | C | robots |  |
| [API STD 598](https://publications.api.org/) | Valve inspection and testing | API | global | paid | catalogue | C | robots |  |
| [API STD 599](https://publications.api.org/) | Metal plug valves | API | global | paid | catalogue | C | robots |  |
| [API STD 600](https://publications.api.org/) | Steel gate valves with flanged and butt-welding ends | API | global | paid | catalogue | C | robots |  |
| [API STD 602](https://publications.api.org/) | Compact steel gate, globe and check valves | API | global | paid | catalogue | C | robots |  |
| [API STD 603](https://publications.api.org/) | Corrosion-resistant, bolted bonnet gate valves | API | global | paid | catalogue | C | robots |  |
| [API STD 607](https://publications.api.org/) | Fire test for quarter-turn valves and valves with nonmetallic seats | API | global | paid | catalogue | C | robots |  |
| [API SPEC 6FA](https://publications.api.org/) | Fire test for valves | API | global | paid | catalogue | C | robots |  |
| [API STD 608](https://publications.api.org/) | Metal ball valves | API | global | paid | catalogue | C | robots |  |
| [API STD 609](https://publications.api.org/) | Butterfly valves | API | global | paid | catalogue | C | robots |  |
| [API STD 623](https://publications.api.org/) | Steel globe valves | API | global | paid | catalogue | C | robots |  |
| [API STD 624](https://publications.api.org/) | Type testing of rising stem valves with graphite packing for fugitive emissions | API | global | paid | catalogue | C | robots |  |
| [API STD 641](https://publications.api.org/) | Type testing of quarter-turn valves for fugitive emissions | API | global | paid | catalogue | C | robots |  |
| [API RP 14E](https://publications.api.org/) | Design and installation of offshore production platform piping systems | API | global | paid | catalogue | C | robots |  |
| [API RP 574](https://publications.api.org/) | Inspection practices for piping system components | API | global | paid | catalogue | C | robots |  |
| [TEMA Standards](https://www.tema.org/) | Standards of the Tubular Exchanger Manufacturers Association | TEMA | global | paid | catalogue | C | ok |  |
| [HEI Standards](https://www.heatexchange.org/) | Heat Exchange Institute standards (condensers, ejectors, deaerators) | HEI | global | paid | catalogue | C | ok |  |
| [ANSI/HI Pump Standards](https://www.pumps.org/) | Pump standards, including NPSH margin and intake design | Hydraulic Institute | global | paid | catalogue | C | ok |  |
| [MSS SP-6](https://msshq.org/) | Standard finishes for contact faces of pipe flanges | MSS | global | paid | catalogue | C | blocked |  |
| [MSS SP-25](https://msshq.org/) | Standard marking system for valves, fittings, flanges and unions | MSS | global | paid | catalogue | C | blocked |  |
| [MSS SP-44](https://msshq.org/) | Steel pipeline flanges | MSS | global | paid | catalogue | C | blocked |  |
| [MSS SP-58](https://msshq.org/) | Pipe hangers and supports: materials, design, manufacture, selection | MSS | global | paid | catalogue | C | blocked |  |
| [MSS SP-97](https://msshq.org/) | Integrally reinforced forged branch outlet fittings | MSS | global | paid | catalogue | C | blocked |  |
| [EJMA Standards](https://www.ejma.org/) | Standards of the Expansion Joint Manufacturers Association | EJMA | global | paid | catalogue | C | ok |  |
| [WRC 107 / 537](https://www.forengineers.org/) | Local stresses in shells due to external loadings on attachments | WRC | global | paid | catalogue | C | robots |  |
| [WRC 297](https://www.forengineers.org/) | Local stresses in cylindrical shells due to external loadings on nozzles | WRC | global | paid | catalogue | C | robots |  |
| [EN 13445 (series)](https://standards.cencenelec.eu/) | Unfired pressure vessels | EN | EU | paid | catalogue | C | robots |  |
| [EN 13480 (series)](https://standards.cencenelec.eu/) | Metallic industrial piping | EN | EU | paid | catalogue | C | robots |  |
| [EN 12952 (series)](https://standards.cencenelec.eu/) | Water-tube boilers | EN | EU | paid | catalogue | C | robots |  |
| [EN 12953 (series)](https://standards.cencenelec.eu/) | Shell boilers | EN | EU | paid | catalogue | C | robots |  |
| [EN 14015](https://standards.cencenelec.eu/) | Site-built, vertical, cylindrical, flat-bottomed, above ground welded steel tanks | EN | EU | paid | catalogue | C | robots |  |
| [EN 14620 (series)](https://standards.cencenelec.eu/) | Site-built tanks for refrigerated liquefied gases | EN | EU | paid | catalogue | C | robots |  |
| [EN 1473](https://standards.cencenelec.eu/) | Installation and equipment for LNG: design of onshore installations | EN | EU | paid | catalogue | C | robots |  |
| [EN 764-7](https://standards.cencenelec.eu/) | Pressure equipment: safety systems for unfired pressure equipment | EN | EU | paid | catalogue | C | robots |  |
| [EN 1591-1](https://standards.cencenelec.eu/) | Flanges and their joints: design rules for gasketed circular flange connections | EN | EU | paid | catalogue | C | robots |  |
| [EN 1594](https://standards.cencenelec.eu/) | Gas infrastructure: pipelines for maximum operating pressure over 16 bar | EN | EU | paid | catalogue | C | robots |  |
| [PD 5500](https://knowledge.bsigroup.com/) | Specification for unfired fusion welded pressure vessels | BSI | UK | paid | catalogue | C | ok |  |
| [BS 7910](https://knowledge.bsigroup.com/) | Guide to methods for assessing the acceptability of flaws in metallic structures | BSI | UK | paid | catalogue | C | ok |  |
| [BS EN 14161 / PD 8010](https://knowledge.bsigroup.com/) | Code of practice for pipelines | BSI | UK | paid | catalogue | C | ok |  |
| [UL 142](https://www.shopulstandards.com/) | Steel aboveground tanks for flammable and combustible liquids | UL | US | mixed | catalogue | C | ok |  |
| [UL 58](https://www.shopulstandards.com/) | Steel underground tanks for flammable and combustible liquids | UL | US | mixed | catalogue | C | ok |  |
| [UL 2085](https://www.shopulstandards.com/) | Protected aboveground tanks for flammable and combustible liquids | UL | US | mixed | catalogue | C | ok |  |
| [AD 2000 Merkblatt](https://www.baua.de/EN) | German pressure vessel code | AD 2000 / TRBS | EU | mixed | catalogue | C | blocked |  |
| [TRGS / TRBS](https://www.baua.de/EN) | German technical rules for hazardous substances and operational safety | AD 2000 / TRBS | EU | mixed | catalogue | C | blocked | Free from BAuA. |
| [PIP Practices](https://www.pip.org/) | Process Industry Practices (engineering practices for piping, vessels, instrumentation, civil and safety) | PIP | global | paid | catalogue | C | ok |  |

## Mechanical integrity, inspection and fitness for service

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [API 510](https://publications.api.org/) | Pressure vessel inspection code: in-service inspection, rating, repair and alteration | API | global | paid | catalogue | C | robots |  |
| [API 570](https://publications.api.org/) | Piping inspection code: in-service inspection, rating, repair and alteration | API | global | paid | catalogue | C | robots |  |
| [API STD 653](https://publications.api.org/) | Tank inspection, repair, alteration and reconstruction | API | global | paid | catalogue | C | robots |  |
| [API RP 580](https://publications.api.org/) | Risk-based inspection | API | global | paid | catalogue | C | robots |  |
| [API RP 581](https://publications.api.org/) | Risk-based inspection methodology | API | global | paid | catalogue | C | robots |  |
| [API 579-1/ASME FFS-1](https://publications.api.org/) | Fitness-for-service | API | global | paid | catalogue | C | robots |  |
| [API RP 571](https://publications.api.org/) | Damage mechanisms affecting fixed equipment in the refining industry | API | global | paid | catalogue | C | robots |  |
| [API RP 572](https://publications.api.org/) | Inspection practices for pressure vessels | API | global | paid | catalogue | C | robots |  |
| [API RP 573](https://publications.api.org/) | Inspection of fired boilers and heaters | API | global | paid | catalogue | C | robots |  |
| [API RP 575](https://publications.api.org/) | Inspection practices for atmospheric and low-pressure storage tanks | API | global | paid | catalogue | C | robots |  |
| [API RP 577](https://publications.api.org/) | Welding processes, inspection and metallurgy | API | global | paid | catalogue | C | robots |  |
| [API RP 578](https://publications.api.org/) | Guidelines for a material verification program for new and existing assets | API | global | paid | catalogue | C | robots |  |
| [API RP 583](https://publications.api.org/) | Corrosion under insulation and fireproofing | API | global | paid | catalogue | C | robots |  |
| [API RP 584](https://publications.api.org/) | Integrity operating windows | API | global | paid | catalogue | C | robots |  |
| [API RP 585](https://publications.api.org/) | Pressure equipment integrity incident investigation | API | global | paid | catalogue | C | robots |  |
| [API RP 588](https://publications.api.org/) | Source inspection and quality surveillance of fixed equipment | API | global | paid | catalogue | C | robots |  |
| [EEMUA 159](https://www.eemua.org/) | Above ground flat bottomed storage tanks: a guide to inspection, maintenance and repair | EEMUA | global | paid | catalogue | C | blocked |  |
| [NBIC (NB-23)](https://www.nationalboard.org/) | National Board Inspection Code | NBBI | US | paid | catalogue | C | ok |  |
| [HSE technical measures: NDT](https://www.hse.gov.uk/comah/sragtech/techmeasndt.htm) | COMAH technical measures document on inspection and non-destructive testing | HSE | UK | free | document | C | ok |  |

## Materials selection, corrosion and damage mechanisms

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [NACE MR0175 / ISO 15156](https://www.ampp.org/standards) | Materials for use in H2S-containing environments in oil and gas production | AMPP / ISO | global | paid | catalogue | C | ok |  |
| [NACE MR0103 / ISO 17945](https://www.ampp.org/standards) | Metallic materials resistant to sulfide stress cracking in corrosive petroleum refining environments | AMPP / ISO | global | paid | catalogue | C | ok |  |
| [NACE SP0472](https://www.ampp.org/standards) | Methods and controls to prevent in-service environmental cracking of carbon steel weldments in refining | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0198](https://www.ampp.org/standards) | Control of corrosion under thermal insulation and fireproofing materials | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0403](https://www.ampp.org/standards) | Avoiding caustic stress corrosion cracking of carbon steel refinery equipment and piping | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0169](https://www.ampp.org/standards) | Control of external corrosion on underground or submerged metallic piping systems | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0170](https://www.ampp.org/standards) | Protection of austenitic stainless steels from polythionic acid stress corrosion cracking | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0294](https://www.ampp.org/standards) | Design, fabrication and inspection of storage tank systems for concentrated sulfuric acid and oleum | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0502](https://www.ampp.org/standards) | Pipeline external corrosion direct assessment methodology | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0206](https://www.ampp.org/standards) | Internal corrosion direct assessment for pipelines carrying normally dry natural gas | AMPP | global | paid | catalogue | C | ok |  |
| [NACE SP0775](https://www.ampp.org/standards) | Preparation, installation, analysis and interpretation of corrosion coupons in oilfield operations | AMPP | global | paid | catalogue | C | ok |  |
| [NACE TM0177](https://www.ampp.org/standards) | Laboratory testing of metals for resistance to sulfide stress cracking and stress corrosion cracking in H2S | AMPP | global | paid | catalogue | C | ok |  |
| [NACE TM0284](https://www.ampp.org/standards) | Evaluation of pipeline and pressure vessel steels for resistance to hydrogen-induced cracking | AMPP | global | paid | catalogue | C | ok |  |
| [NACE TM0316](https://www.ampp.org/standards) | Four-point bend testing of materials for oil and gas applications | AMPP | global | paid | catalogue | C | ok |  |
| [NACE 34101](https://www.ampp.org/standards) | Refinery injection and process mix points | AMPP | global | paid | catalogue | C | ok |  |
| [API RP 941](https://publications.api.org/) | Steels for hydrogen service at elevated temperatures and pressures in petroleum refineries and petrochemical plants | API | global | paid | catalogue | C | robots |  |
| [API RP 939-C](https://publications.api.org/) | Guidelines for avoiding sulfidation corrosion failures in oil refineries | API | global | paid | catalogue | C | robots |  |
| [API RP 932-B](https://publications.api.org/) | Design, materials, fabrication, operation and inspection guidelines for corrosion control in hydroprocessing reactor effluent air cooler systems | API | global | paid | catalogue | C | robots |  |
| [API RP 934 (series)](https://publications.api.org/) | Materials and fabrication of 1.25Cr, 2.25Cr and 3Cr steel heavy wall pressure vessels for high-temperature, high-pressure hydrogen service | API | global | paid | catalogue | C | robots |  |
| [API RP 945](https://publications.api.org/) | Avoiding environmental cracking in amine units | API | global | paid | catalogue | C | robots |  |
| [API RP 751](https://publications.api.org/) | Safe operation of hydrofluoric acid alkylation units | API | global | paid | catalogue | C | robots |  |
| [API RP 970](https://publications.api.org/) | Corrosion control documents | API | global | paid | catalogue | C | robots |  |
| [API RP 582](https://publications.api.org/) | Welding guidelines for the chemical, oil and gas industries | API | global | paid | catalogue | C | robots |  |
| [API TR 938-B](https://publications.api.org/) | Use of 9Cr-1Mo-V steel in the refining industry | API | global | paid | catalogue | C | robots |  |
| [API TR 938-C](https://publications.api.org/) | Use of duplex stainless steels in the oil refining industry | API | global | paid | catalogue | C | robots |  |
| [API RP 2611](https://publications.api.org/) | Terminal piping inspection | API | global | paid | catalogue | C | robots |  |
| [ASME BPVC II Part A](https://www.asme.org/codes-standards) | Materials: ferrous material specifications (SA) | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC II Part B](https://www.asme.org/codes-standards) | Materials: nonferrous material specifications (SB) | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC II Part C](https://www.asme.org/codes-standards) | Materials: specifications for welding rods, electrodes and filler metals (SFA) | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC II Part D](https://www.asme.org/codes-standards) | Materials: properties (allowable stresses, external pressure charts) | ASME | global | paid | catalogue | C | ok |  |
| [ISO 21457](https://www.iso.org/search.html?q=ISO%2021457) | Materials selection and corrosion control for oil and gas production systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 23936 (series)](https://www.iso.org/search.html?q=ISO%2023936%20%28series%29) | Non-metallic materials in contact with media related to oil and gas production | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 15649](https://www.iso.org/search.html?q=ISO%2015649) | Petroleum and natural gas industries: piping | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 12944 (series)](https://www.iso.org/search.html?q=ISO%2012944%20%28series%29) | Corrosion protection of steel structures by protective paint systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 8501-1](https://www.iso.org/search.html?q=ISO%208501-1) | Preparation of steel substrates: visual assessment of surface cleanliness | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 19840](https://www.iso.org/search.html?q=ISO%2019840) | Protective paint systems: measurement of dry film thickness | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 9223](https://www.iso.org/search.html?q=ISO%209223) | Corrosivity of atmospheres: classification | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 15589-1](https://www.iso.org/search.html?q=ISO%2015589-1) | Cathodic protection of pipeline systems: on-land pipelines | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 11114 (series)](https://www.iso.org/search.html?q=ISO%2011114%20%28series%29) | Gas cylinders: compatibility of cylinder and valve materials with gas contents | ISO | global | paid | catalogue | C | blocked |  |
| [NORSOK M-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Materials selection | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-501](https://standard.no/en/sectors/petroleum/norsok-standards/) | Surface preparation and protective coating | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-601](https://standard.no/en/sectors/petroleum/norsok-standards/) | Welding and inspection of piping | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-630](https://standard.no/en/sectors/petroleum/norsok-standards/) | Material data sheets and element data sheets for piping | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-650](https://standard.no/en/sectors/petroleum/norsok-standards/) | Qualification of manufacturers of special materials | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-710](https://standard.no/en/sectors/petroleum/norsok-standards/) | Qualification of non-metallic materials and manufacturers | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-101](https://standard.no/en/sectors/petroleum/norsok-standards/) | Structural steel fabrication | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-120](https://standard.no/en/sectors/petroleum/norsok-standards/) | Material data sheets for structural steel | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK M-506](https://standard.no/en/sectors/petroleum/norsok-standards/) | CO2 corrosion rate calculation model | NORSOK | NO | mixed | catalogue | C | ok |  |
| [DNV-RP-O501](https://www.dnv.com/rules-standards/) | Managing sand production and erosion | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-F101](https://www.dnv.com/rules-standards/) | Corroded pipelines | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-F112](https://www.dnv.com/rules-standards/) | Duplex stainless steel: design against hydrogen induced stress cracking | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-B401](https://www.dnv.com/rules-standards/) | Cathodic protection design | DNV | global | free | catalogue | C | ok |  |
| [EN 10028 (series)](https://standards.cencenelec.eu/) | Flat products made of steels for pressure purposes | EN | EU | paid | catalogue | C | robots |  |
| [EN 10216 (series)](https://standards.cencenelec.eu/) | Seamless steel tubes for pressure purposes | EN | EU | paid | catalogue | C | robots |  |
| [EN 10217 (series)](https://standards.cencenelec.eu/) | Welded steel tubes for pressure purposes | EN | EU | paid | catalogue | C | robots |  |
| [EN 10222 (series)](https://standards.cencenelec.eu/) | Steel forgings for pressure purposes | EN | EU | paid | catalogue | C | robots |  |
| [EN 10213](https://standards.cencenelec.eu/) | Steel castings for pressure purposes | EN | EU | paid | catalogue | C | robots |  |
| [EN 10204](https://standards.cencenelec.eu/) | Metallic products: types of inspection documents (material certificates) | EN | EU | paid | catalogue | C | robots |  |
| [EN 1092-1](https://standards.cencenelec.eu/) | Flanges: steel flanges, PN designated | EN | EU | paid | catalogue | C | robots |  |
| [EN 10269](https://standards.cencenelec.eu/) | Steels and nickel alloys for fasteners with specified elevated and low temperature properties | EN | EU | paid | catalogue | C | robots |  |
| [EN 10088 (series)](https://standards.cencenelec.eu/) | Stainless steels | EN | EU | paid | catalogue | C | robots |  |
| [MTI publications](https://www.mti-global.org/) | Materials Technology Institute guidance for the chemical process industries | MTI | global | mixed | catalogue | C | ok |  |
| [Nickel Institute guides](https://nickelinstitute.org/en/library/) | Technical guides on stainless steels and nickel alloys in corrosive service | Nickel Institute | global | free | catalogue | C | robots |  |
| [Euro Chlor GEST publications](https://www.eurochlor.org/) | Chlorine industry materials, equipment and safety recommendations | Euro Chlor | EU | mixed | catalogue | C | ok |  |

## ASTM steel pipe and tube specifications

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A53](https://store.astm.org/standards/a53) | Standard Specification for Pipe, Steel, Black And Hot- Dipped, Zinc- Coated Welded And Seamless | ASTM | global | paid | document | P | ok |  |
| [ASTM A106](https://store.astm.org/standards/a106) | Standard Specification for Seamless Carbon Steel Pipe for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A312](https://store.astm.org/standards/a312_a312m) | Standard Specification for Seamless, Welded, and Heavily Cold Worked Austenitic Stainless Steel Pipes | ASTM | global | paid | document | P | ok |  |
| [ASTM A333](https://store.astm.org/standards/a333) | Standard Specifications For Seamless And Welded Steel Pipe For Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A335](https://store.astm.org/standards/a335_a335m) | Standard Specification for Seamless Ferritic Alloy-Steel Pipe for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A358](https://store.astm.org/standards/a358_a358m) | Standard Specification for Electric-Fusion-Welded Austenitic Chromium-Nickel Stainless Steel Pipe for High-Temperature Service and General Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A369](https://store.astm.org/standards/a369_a369m) | Standard Specification for Carbon and Ferritic Alloy Steel Forged and Bored Pipe for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A376](https://store.astm.org/standards/a376_a376m) | Standard Specification for Seamless Austenitic Steel Pipe for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A381](https://store.astm.org/standards/a381) | Standard Specification for Metal-Arc-Welded Steel Pipe for Use With High-Pressure Transmission Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM A409](https://store.astm.org/standards/a409_a409m) | Standard Specification for Welded Large Diameter Austenitic Steel Pipe for Corrosive or High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A524](https://store.astm.org/standards/a524) | Standard Specification for Seamless Carbon Steel Pipe for Atmospheric and Lower Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A671](https://store.astm.org/standards/a671) | Standard Specification for Electric-Fusion-Welded Steel Pipe for Atmospheric and Lower Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A672](https://store.astm.org/standards/a672) | Standard Specification for Electric-Fusion-Welded Steel Pipe for High-Pressure Service at Moderate Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A691](https://store.astm.org/standards/a691) | Standard Specification for Carbon and Alloy Steel Pipe, Electric-Fusion-Welded for High-Pressure Service at High Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A790](https://store.astm.org/standards/a790_a790m) | Standard Specification for Seamless and Welded Ferritic/Austenitic Stainless Steel Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM A928](https://store.astm.org/standards/a928_a928m) | Standard Specification for Ferritic/Austenitic (Duplex) Stainless Steel Pipe Electric Fusion Welded with Addition of Filler Metal | ASTM | global | paid | document | P | ok |  |
| [ASTM A999](https://store.astm.org/standards/a999_a999m) | Standard Specification for General Requirements for Alloy and Stainless Steel Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM A530](https://store.astm.org/standards/a530_a530m) | Standard Specification for General Requirements for Specialized Carbon and Alloy Steel Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM A178](https://store.astm.org/standards/a178_a178m) | Standard Specification for Electric-Resistance-Welded Carbon Steel and Carbon-Manganese Steel Boiler and Superheater Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A179](https://store.astm.org/standards/a179_a179m) | Standard Specification for Seamless Cold-Drawn Low-Carbon Steel Heat-Exchanger and Condenser Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A192](https://store.astm.org/standards/a192_a192m) | Standard Specification for Seamless Carbon Steel Boiler Tubes for High-Pressure Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A209](https://store.astm.org/standards/a209_a209m) | Standard Specification for Seamless Carbon-Molybdenum Alloy-Steel Boiler and Superheater Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A210](https://store.astm.org/standards/a210_a210m) | Standard Specification for Seamless Medium-Carbon Steel Boiler and Superheater Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A213](https://store.astm.org/standards/a213_a213m) | Standard Specification for Seamless Ferritic and Austenitic Alloy-Steel Boiler, Superheater, and Heat-Exchanger Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A214](https://store.astm.org/standards/a214_a214m) | Standard Specification for Electric-Resistance-Welded Carbon Steel Heat-Exchanger and Condenser Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A249](https://store.astm.org/standards/a249_a249m) | Standard Specification for Welded Austenitic Steel Boiler, Superheater, Heat-Exchanger, and Condenser Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A250](https://store.astm.org/standards/a250_a250m) | Standard Specification for Electric-Resistance-Welded Ferritic Alloy-Steel Boiler and Superheater Tubes (Withdrawn 2017) | ASTM | global | paid | document | P | ok |  |
| [ASTM A268](https://store.astm.org/standards/a268_a268m) | Standard Specification for Seamless and Welded Ferritic and Martensitic Stainless Steel Tubing for General Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A269](https://store.astm.org/standards/a269) | Standard Specification for Seamless and Welded Austenitic Stainless Steel Tubing for General Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A270](https://store.astm.org/standards/a270) | Standard Specification for Seamless and Welded Austenitic Stainless Steel Sanitary Tubing | ASTM | global | paid | document | P | ok |  |
| [ASTM A334](https://store.astm.org/standards/a334_a334m) | Standard Specification for Seamless and Welded Carbon and Alloy-Steel Tubes for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A450](https://store.astm.org/standards/a450_a450m) | Standard Specification for General Requirements for Carbon and Low Alloy Steel Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A688](https://store.astm.org/standards/a688_a688m) | Standard Specification for Seamless and Welded Austenitic Stainless Steel Feedwater Heater Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A789](https://store.astm.org/standards/a789_a789m) | Standard Specification for Seamless and Welded Ferritic/Austenitic Stainless Steel Tubing for General Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A803](https://store.astm.org/standards/a803_a803m) | Standard Specification for Seamless and Welded Ferritic Stainless Steel Feedwater Heater Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM A1016](https://store.astm.org/standards/a1016_a1016m) | Standard Specification for General Requirements for Ferritic Alloy Steel, Austenitic Alloy Steel, and Stainless Steel Tubes | ASTM | global | paid | document | P | ok |  |

## ASTM plate and structural steel specifications

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A6](https://store.astm.org/standards/a6_a6m) | Standard Specification for General Requirements for Rolled Structural Steel Bars, Plates, Shapes, and Sheet Piling | ASTM | global | paid | document | P | ok |  |
| [ASTM A20](https://store.astm.org/standards/a20_a20m) | Standard Specification for General Requirements for Steel Plates for Pressure Vessels | ASTM | global | paid | document | P | ok |  |
| [ASTM A36](https://store.astm.org/standards/a36_a36m) | Standard Specification for Carbon Structural Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM A202](https://store.astm.org/standards/a202_a202m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Chromium-Manganese-Silicon (Withdrawn 2004) | ASTM | global | paid | document | P | ok |  |
| [ASTM A203](https://store.astm.org/standards/a203_a203m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A204](https://store.astm.org/standards/a204_a204m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Molybdenum | ASTM | global | paid | document | P | ok |  |
| [ASTM A225](https://store.astm.org/standards/a225_a225m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Manganese-Vanadium-Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A240](https://store.astm.org/standards/a240_a240m) | Standard Specification for Chromium and Chromium-Nickel Stainless Steel Plate, Sheet, and Strip for Pressure Vessels and for General Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A263](https://store.astm.org/standards/a263) | Standard Specification for Stainless Chromium Steel-Clad Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM A264](https://store.astm.org/standards/a264) | Standard Specification for Stainless Chromium-Nickel Steel-Clad Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM A265](https://store.astm.org/standards/a265) | Standard Specification for Nickel and Nickel-Base Alloy-Clad Steel Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM A283](https://store.astm.org/standards/a283_a283m) | Standard Specification for Low and Intermediate Tensile Strength Carbon Steel Plates | ASTM | global | paid | document | P | ok |  |
| [ASTM A285](https://store.astm.org/standards/a285) | Standard Specification for Pressure Vessel Plates, Carbon Steel, Low- and Intermediate-Tensile Strength | ASTM | global | paid | document | P | ok |  |
| [ASTM A299](https://store.astm.org/standards/a299_a299m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, Manganese-Silicon | ASTM | global | paid | document | P | ok |  |
| [ASTM A302](https://store.astm.org/standards/a302_a302m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Manganese-Molybdenum and Manganese-Molybdenum-Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A353](https://store.astm.org/standards/a353_a353m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Double-Normalized and Tempered 9 % Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A387](https://store.astm.org/standards/a387_a387m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Chromium-Molybdenum | ASTM | global | paid | document | P | ok |  |
| [ASTM A480](https://store.astm.org/standards/a480_a480m) | Standard Specification for General Requirements for Flat-Rolled Stainless and Heat-Resisting Steel Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM A515](https://store.astm.org/standards/a515_a515m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, for Intermediate- and Higher-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A516](https://store.astm.org/standards/a516_a516m) | Standard Specification for Pressure Vessel Plates, Carbon Steel, for Moderate- and Lower-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A517](https://store.astm.org/standards/a517_a517m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, High-Strength, Quenched and Tempered | ASTM | global | paid | document | P | ok |  |
| [ASTM A533](https://store.astm.org/standards/a533_a533m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched and Tempered, Manganese-Molybdenum and Manganese-Molybdenum-Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A537](https://store.astm.org/standards/a537_a537m) | Standard Specification for Pressure Vessel Plates, Heat-Treated, Carbon-Manganese-Silicon Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM A542](https://store.astm.org/standards/a542_a542m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched-and-Tempered, Chromium-Molybdenum, and Chromium-Molybdenum-Vanadium | ASTM | global | paid | document | P | ok |  |
| [ASTM A543](https://store.astm.org/standards/a543_a543m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched and Tempered Nickel-Chromium-Molybdenum | ASTM | global | paid | document | P | ok |  |
| [ASTM A553](https://store.astm.org/standards/a553_a553m) | Standard Specification for Pressure Vessel Plates, Alloy Steel, Quenched and Tempered 7 %, 8 %, and 9 % Nickel | ASTM | global | paid | document | P | ok |  |
| [ASTM A578](https://store.astm.org/standards/a578_a578m) | Standard Specification for Straight-Beam Ultrasonic Examination of Rolled Steel Plates for Special Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A612](https://store.astm.org/standards/a612) | Standard Specification for High-Strength Steel Plates for Pressure Vessels for Moderate- and Lower-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A645](https://store.astm.org/standards/a645_a645m) | Standard Specification for Pressure Vessel Plates, 5 % and 51 2 % Nickel Alloy Steels, Specially Heat Treated | ASTM | global | paid | document | P | ok |  |
| [ASTM A662](https://store.astm.org/standards/a662_a662m) | Standard Specification for Pressure Vessel Plates, Carbon-Manganese-Silicon Steel, for Moderate and Lower Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A737](https://store.astm.org/standards/a737_a737m) | Standard Specification for Pressure Vessel Plates, High-Strength, Low-Alloy Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM A841](https://store.astm.org/standards/a841_a841m) | Standard Specification for Steel Plates for Pressure Vessels, Produced by Thermo-Mechanical Control Process (TMCP) | ASTM | global | paid | document | P | ok |  |
| [ASTM A123](https://store.astm.org/standards/a123_a123m) | Standard Specification for Zinc (Hot-Dip Galvanized) Coatings on Iron and Steel Products | ASTM | global | paid | document | P | ok |  |
| [ASTM A153](https://store.astm.org/standards/a153_a153m) | Standard Specification for Zinc Coating (Hot-Dip) on Iron and Steel Hardware | ASTM | global | paid | document | P | ok |  |
| [ASTM A435](https://store.astm.org/standards/a435_a435m) | Standard Specification for Straight-Beam Ultrasonic Examination of Steel Plates | ASTM | global | paid | document | P | ok |  |
| [ASTM A500](https://store.astm.org/standards/a500) | Standard Specification for Cold-Formed Welded and Seamless Carbon Steel Structural Tubing in Rounds and Shapes | ASTM | global | paid | document | P | ok |  |
| [ASTM A501](https://store.astm.org/standards/a501) | Standard Specification for Hot-Formed Welded and Seamless Carbon Steel Structural Tubing | ASTM | global | paid | document | P | ok |  |
| [ASTM A572](https://store.astm.org/standards/a572) | Standard Specification for High-Strength Low-Alloy Columbium-Vanadium Steels Of Structural Quality | ASTM | global | paid | document | P | ok |  |
| [ASTM A588](https://store.astm.org/standards/a588) | Standard Specification for High-Strength Low-Alloy Structural Steel With 50 Ksi Minimum Yield Point To 4 In. Thick | ASTM | global | paid | document | P | ok |  |
| [ASTM A653](https://store.astm.org/standards/a653_a653m) | Standard Specification for Steel Sheet, Zinc-Coated (Galvanized) or Zinc-Iron Alloy-Coated (Galvannealed) by the Hot-Dip Process | ASTM | global | paid | document | P | ok |  |
| [ASTM A913](https://store.astm.org/standards/a913_a913m) | Standard Specification for High-Strength Low-Alloy Steel Shapes of Structural Quality, Produced by Quenching and Self-Tempering Process (QST) | ASTM | global | paid | document | P | ok |  |
| [ASTM A992](https://store.astm.org/standards/a992_a992m) | Standard Specification for Structural Steel Shapes | ASTM | global | paid | document | P | ok |  |

## ASTM forging, casting, flange and fitting specifications

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A105](https://store.astm.org/standards/a105_a105m) | Standard Specification for Carbon Steel Forgings for Piping Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A181](https://store.astm.org/standards/a181_a181m) | Standard Specification for Carbon Steel Forgings, for General-Purpose Piping | ASTM | global | paid | document | P | ok |  |
| [ASTM A182](https://store.astm.org/standards/a182_a182m) | Standard Specification for Forged or Rolled Alloy and Stainless Steel Pipe Flanges, Forged Fittings, and Valves and Parts for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A216](https://store.astm.org/standards/a216_a216m) | Standard Specification for Steel Castings, Carbon, Suitable for Fusion Welding, for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A217](https://store.astm.org/standards/a217_a217m) | Standard Specification for Steel Castings, Martensitic Stainless and Alloy, for Pressure-Containing Parts, Suitable for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A234](https://store.astm.org/standards/a234_a234m) | Standard Specification for Piping Fittings of Wrought Carbon Steel and Alloy Steel for Moderate and High Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A266](https://store.astm.org/standards/a266_a266m) | Standard Specification for Carbon Steel Forgings for Pressure Vessel Components | ASTM | global | paid | document | P | ok |  |
| [ASTM A336](https://store.astm.org/standards/a336_a336m) | Standard Specification for Alloy Steel Forgings for Pressure and High-Temperature Parts | ASTM | global | paid | document | P | ok |  |
| [ASTM A350](https://store.astm.org/standards/a350_a350m) | Standard Specification for Carbon and Low-Alloy Steel Forgings, Requiring Notch Toughness Testing for Piping Components | ASTM | global | paid | document | P | ok |  |
| [ASTM A351](https://store.astm.org/standards/a351_a351m) | Standard Specification for Castings, Austenitic, for Pressure-Containing Parts | ASTM | global | paid | document | P | ok |  |
| [ASTM A352](https://store.astm.org/standards/a352_a352m) | Standard Specification for Steel Castings, Ferritic and Martensitic, for Pressure-Containing Parts, Suitable for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A403](https://store.astm.org/standards/a403_a403m) | Standard Specification for Wrought Austenitic Stainless Steel Piping Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM A420](https://store.astm.org/standards/a420_a420m) | Standard Specification for Piping Fittings of Wrought Carbon Steel and Alloy Steel for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A487](https://store.astm.org/standards/a487_a487m) | Standard Specification for Steel Castings Suitable for Pressure Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A494](https://store.astm.org/standards/a494_a494m) | Standard Specification for Castings, Nickel and Nickel Alloy | ASTM | global | paid | document | P | ok |  |
| [ASTM A508](https://store.astm.org/standards/a508_a508m) | Standard Specification for Quenched and Tempered Vacuum-Treated Carbon and Alloy Steel Forgings for Pressure Vessels | ASTM | global | paid | document | P | ok |  |
| [ASTM A522](https://store.astm.org/standards/a522_a522m) | Standard Specification for Forged or Rolled 8 and 9% Nickel Alloy Steel Flanges, Fittings, Valves, and Parts for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A694](https://store.astm.org/standards/a694_a694m) | Standard Specification for Carbon and Alloy Steel Forgings for Pipe Flanges, Fittings, Valves, and Parts for High-Pressure Transmission Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A707](https://store.astm.org/standards/a707_a707m) | Standard Specification for Forged Carbon and Alloy Steel Flanges for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A727](https://store.astm.org/standards/a727_a727m) | Standard Specification for Carbon Steel Forgings for Piping Components with Inherent Notch Toughness (Withdrawn 2024) | ASTM | global | paid | document | P | ok |  |
| [ASTM A744](https://store.astm.org/standards/a744_a744m) | Standard Specification for Castings, Iron-Chromium-Nickel, Corrosion Resistant, for Severe Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A774](https://store.astm.org/standards/a774_a774m) | Standard Specification for As-Welded Wrought Austenitic Stainless Steel Fittings for General Corrosive Service at Low and Moderate Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A815](https://store.astm.org/standards/a815_a815m) | Standard Specification for Wrought Ferritic, Ferritic/Austenitic, and Martensitic Stainless Steel Piping Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM A860](https://store.astm.org/standards/a860_a860m) | Standard Specification for Wrought High-Strength Ferritic Steel Butt-Welding Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM A890](https://store.astm.org/standards/a890_a890m) | Standard Specification for Castings, Iron-Chromium-Nickel-Molybdenum Corrosion-Resistant, Duplex (Austenitic/Ferritic) for General Application | ASTM | global | paid | document | P | ok |  |
| [ASTM A961](https://store.astm.org/standards/a961) | Standard Specification for Common Requirements for Steel Flanges, Forged Fittings, Valves, and Parts for Piping Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A965](https://store.astm.org/standards/a965_a965m) | Standard Specification for Steel Forgings, Austenitic, for Pressure and High Temperature Parts | ASTM | global | paid | document | P | ok |  |
| [ASTM A995](https://store.astm.org/standards/a995) | Standard Specification for Castings, Austenitic-Ferritic (Duplex) Stainless Steel, for Pressure-Containing Parts | ASTM | global | paid | document | P | ok |  |
| [ASTM A47](https://store.astm.org/standards/a47_a47m) | Standard Specification for Ferritic Malleable Iron Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM A48](https://store.astm.org/standards/a48) | Standard Specification for Gray Iron Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM A126](https://store.astm.org/standards/a126) | Standard Specification for Gray Iron Castings for Valves, Flanges, and Pipe Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM A197](https://store.astm.org/standards/a197_a197m) | Standard Specification for Cupola Malleable Iron | ASTM | global | paid | document | P | ok |  |
| [ASTM A278](https://store.astm.org/standards/a278_a278m) | Standard Specification for Gray Iron Castings for Pressure-Containing Parts for Temperatures Up to 650 °F [350 °C] | ASTM | global | paid | document | P | ok |  |
| [ASTM A395](https://store.astm.org/standards/a395_a395m) | Standard Specification for Ferritic Ductile Iron Pressure-Retaining Castings for Use at Elevated Temperatures | ASTM | global | paid | document | P | ok |  |
| [ASTM A536](https://store.astm.org/standards/a536) | Standard Specification for Ductile Iron Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM A571](https://store.astm.org/standards/a571_a571m) | Standard Specification for Austenitic Ductile Iron Castings for Pressure-Containing Parts Suitable for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |

## ASTM bolting, bar and fastener specifications

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A193](https://store.astm.org/standards/a193) | Standard Specification for Alloy-Steel and Stainless Steel Bolting Materials for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A194](https://store.astm.org/standards/a194_a194m) | Standard Specification for Carbon Steel, Alloy Steel, and Stainless Steel Nuts for Bolts for High Pressure or High Temperature Service, or Both | ASTM | global | paid | document | P | ok |  |
| [ASTM A276](https://store.astm.org/standards/a276) | Standard Specification for Stainless Steel Bars and Shapes | ASTM | global | paid | document | P | ok |  |
| [ASTM A307](https://store.astm.org/standards/a307) | Standard Specification for Carbon Steel Bolts, Studs, and Threaded Rod 60 000 PSI Tensile Strength | ASTM | global | paid | document | P | ok |  |
| [ASTM A320](https://store.astm.org/standards/a320_a320m) | Standard Specification for Alloy-Steel and Stainless Steel Bolting for Low-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A354](https://store.astm.org/standards/a354) | Standard Specification for Quenched and Tempered Alloy Steel Bolts, Studs, and Other Externally Threaded Fasteners | ASTM | global | paid | document | P | ok |  |
| [ASTM A437](https://store.astm.org/standards/a437_a437m) | Standard Specification for Stainless and Alloy-Steel Turbine-Type Bolting Specially Heat Treated for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A449](https://store.astm.org/standards/a449) | Standard Specification for Hex Cap Screws, Bolts and Studs, Steel, Heat Treated, 120/105/90 ksi Minimum Tensile Strength, General Use | ASTM | global | paid | document | P | ok |  |
| [ASTM A453](https://store.astm.org/standards/a453_a453m) | Standard Specification for High-Temperature Bolting, with Expansion Coefficients Comparable to Austenitic Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM A479](https://store.astm.org/standards/a479_a479m) | Standard Specification for Stainless Steel Bars and Shapes for Use in Boilers and Other Pressure Vessels | ASTM | global | paid | document | P | ok |  |
| [ASTM A484](https://store.astm.org/standards/a484_a484m) | Standard Specification for General Requirements for Stainless Steel Bars, Billets, Shapes, and Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM A540](https://store.astm.org/standards/a540_a540m) | Standard Specification for Alloy-Steel Bolting for Special Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM A563](https://store.astm.org/standards/a563) | Standard Specification for Carbon and Alloy Steel Nuts | ASTM | global | paid | document | P | ok |  |
| [ASTM A564](https://store.astm.org/standards/a564_a564m) | Standard Specification for Hot-Rolled and Cold-Finished Age-Hardening Stainless Steel Bars and Shapes | ASTM | global | paid | document | P | ok |  |
| [ASTM A574](https://store.astm.org/standards/a574) | Standard Specification for Alloy Steel Socket-Head Cap Screws | ASTM | global | paid | document | P | ok |  |
| [ASTM A638](https://store.astm.org/standards/a638_a638m) | Standard Specification for Precipitation Hardening Iron Base Superalloy Bars, Forgings, and Forging Stock for High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM A675](https://store.astm.org/standards/a675_a675m) | Standard Specification for Steel Bars, Carbon, Hot-Wrought, Special Quality, Mechanical Properties | ASTM | global | paid | document | P | ok |  |
| [ASTM A696](https://store.astm.org/standards/a696) | Standard Specification for Steel Bars, Carbon, Hot-Wrought or Cold-Finished, Special Quality, for Pressure Piping Components | ASTM | global | paid | document | P | ok |  |
| [ASTM A962](https://store.astm.org/standards/a962_a962m) | Standard Specification for Common Requirements for Bolting Intended for Use at Any Temperature from Cryogenic to the Creep Range | ASTM | global | paid | document | P | ok |  |
| [ASTM A1014](https://store.astm.org/standards/a1014) | Standard Specification for Precipitation-Hardening Bolting Material (UNS N07718) for High Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM F436](https://store.astm.org/standards/f436) | Standard Specification for Hardened Steel Washers | ASTM | global | paid | document | P | ok |  |
| [ASTM F467](https://store.astm.org/standards/f467) | Standard Specification for Nonferrous Nuts for General Use | ASTM | global | paid | document | P | ok |  |
| [ASTM F468](https://store.astm.org/standards/f468) | Standard Specification for Nonferrous Bolts, Hex Cap Screws, Socket Head Cap Screws, and Studs for General Use | ASTM | global | paid | document | P | ok |  |
| [ASTM F593](https://store.astm.org/standards/f593) | Standard Specification for Stainless Steel Bolts, Hex Cap Screws, and Studs | ASTM | global | paid | document | P | ok |  |
| [ASTM F594](https://store.astm.org/standards/f594) | Standard Specification for Stainless Steel Nuts | ASTM | global | paid | document | P | ok |  |
| [ASTM F606](https://store.astm.org/standards/f606) | Standard Test Methods for Determining the Mechanical Properties of Externally and Internally Threaded Fasteners, Washers, Direct Tension Indicators, and Rivets | ASTM | global | paid | document | P | ok |  |
| [ASTM F1554](https://store.astm.org/standards/f1554) | Standard Specification for Anchor Bolts, Steel, 36, 55, and 105-ksi Yield Strength | ASTM | global | paid | document | P | ok |  |
| [ASTM F2281](https://store.astm.org/standards/f2281) | Standard Specification for Stainless Steel and Nickel Alloy Bolts, Hex Cap Screws, and Studs, for Heat Resistance and High Temperature Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM F3125](https://store.astm.org/standards/f3125) | Standard Specification for High Strength Structural Bolts, Steel and Alloy Steel, Heat Treated, 120 ksi (830 MPa) and 150 ksi (1040 MPa) Minimum Tensile Strength, Inch and Metric Dimensions | ASTM | global | paid | document | P | ok |  |

## ASTM nickel, titanium, zirconium, aluminium and copper specifications

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM B127](https://store.astm.org/standards/b127) | Standard Specification for Nickel-Copper Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B160](https://store.astm.org/standards/b160) | Standard Specification for Nickel Rod and Bar | ASTM | global | paid | document | P | ok |  |
| [ASTM B161](https://store.astm.org/standards/b161) | Standard Specification for Nickel Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B162](https://store.astm.org/standards/b162) | Standard Specification for Nickel Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B163](https://store.astm.org/standards/b163) | Standard Specification for Seamless Nickel and Nickel Alloy Condenser and Heat-Exchanger Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B164](https://store.astm.org/standards/b164) | Standard Specification for Nickel-Copper Alloy Rod, Bar, and Wire | ASTM | global | paid | document | P | ok |  |
| [ASTM B165](https://store.astm.org/standards/b165) | Standard Specification for Nickel-Copper Alloy Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B166](https://store.astm.org/standards/b166) | Standard Specification for Nickel-Chromium-Aluminum Alloy, Nickel-Chromium-Iron Alloys, Nickel-Chromium-Cobalt-Molybdenum Alloy, Nickel-Iron-Chromium-Tungsten Alloy, and Nickel-Chromium-Molybdenum-Copper Alloy Rod, Bar, and Wire | ASTM | global | paid | document | P | ok |  |
| [ASTM B167](https://store.astm.org/standards/b167) | Standard Specification for Nickel-Chromium-Aluminum Alloys, Nickel-Chromium-Iron Alloys, Nickel-Chromium-Cobalt-Molybdenum Alloy, Nickel-Iron-Chromium-Tungsten Alloy, and Nickel-Chromium-Molybdenum-Copper Alloy Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B168](https://store.astm.org/standards/b168) | Standard Specification for Nickel-Chromium-Aluminum Alloys, Nickel-Chromium-Iron Alloys, Nickel-Chromium-Cobalt-Molybdenum Alloy, Nickel-Iron-Chromium-Tungsten Alloy, and Nickel-Chromium-Molybdenum-Copper Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B333](https://store.astm.org/standards/b333) | Standard Specification for Nickel-Molybdenum Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B335](https://store.astm.org/standards/b335) | Standard Specification for Nickel-Molybdenum Alloy Rod | ASTM | global | paid | document | P | ok |  |
| [ASTM B366](https://store.astm.org/standards/b366) | Standard Specification for Factory-Made Wrought Nickel and Nickel Alloy Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM B407](https://store.astm.org/standards/b407) | Standard Specification for Nickel-Iron-Chromium Alloy Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B408](https://store.astm.org/standards/b408) | Standard Specification for Nickel-Iron-Chromium Alloy Rod and Bar | ASTM | global | paid | document | P | ok |  |
| [ASTM B409](https://store.astm.org/standards/b409) | Standard Specification for Nickel-Iron-Chromium Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B423](https://store.astm.org/standards/b423) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Copper Alloy Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B424](https://store.astm.org/standards/b424) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Copper Alloys Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B425](https://store.astm.org/standards/b425) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Copper Alloys Rod and Bar | ASTM | global | paid | document | P | ok |  |
| [ASTM B434](https://store.astm.org/standards/b434) | Standard Specification for Nickel-Molybdenum-Chromium-Iron Alloys Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B435](https://store.astm.org/standards/b435) | Standard Specification for Heat and Corrosion Resistant High Temperature Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B443](https://store.astm.org/standards/b443) | Standard Specification for Nickel-Chromium-Molybdenum-Columbium Alloy and Nickel-Chromium-Molybdenum-Silicon Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B444](https://store.astm.org/standards/b444) | Standard Specification for Nickel-Chromium-Molybdenum-Niobium Alloys and Nickel-Chromium-Molybdenum-Silicon Alloy Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B446](https://store.astm.org/standards/b446) | Standard Specification for Nickel-Chromium-Molybdenum-Niobium Alloy, Nickel-Chromium-Molybdenum-Silicon Alloy, and Nickel-Chromium-Molybdenum-Tungsten Alloy Rod and Bar | ASTM | global | paid | document | P | ok |  |
| [ASTM B462](https://store.astm.org/standards/b462) | Standard Specification for Forged or Rolled Nickel Alloy Pipe Flanges, Forged Fittings, and Valves and Parts for Corrosive High-Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM B463](https://store.astm.org/standards/b463) | Standard Specification for UNS N08020 Alloy Plate, Sheet, and Strip (Withdrawn 2026) | ASTM | global | paid | document | P | ok |  |
| [ASTM B464](https://store.astm.org/standards/b464) | Standard Specification for Welded UNS N08020 Alloy Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B468](https://store.astm.org/standards/b468) | Standard Specification for Welded UNS N08020 Alloy Tubes (Withdrawn 2025) | ASTM | global | paid | document | P | ok |  |
| [ASTM B473](https://store.astm.org/standards/b473) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Copper Alloy Bar and Wire (Withdrawn 2026) | ASTM | global | paid | document | P | ok |  |
| [ASTM B514](https://store.astm.org/standards/b514) | Standard Specification for Welded Nickel-Iron-Chromium Alloy Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B515](https://store.astm.org/standards/b515) | Standard Specification for Welded Nickel-Iron-Chromium Alloy Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B564](https://store.astm.org/standards/b564) | Standard Specification for Nickel Alloy Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM B572](https://store.astm.org/standards/b572) | Standard Specification for Heat and Corrosion Resistant High Temperature Alloy Bar or Rod | ASTM | global | paid | document | P | ok |  |
| [ASTM B573](https://store.astm.org/standards/b573) | Standard Specification for Nickel-Molybdenum-Chromium-Iron Alloys Bar or Rod | ASTM | global | paid | document | P | ok |  |
| [ASTM B574](https://store.astm.org/standards/b574) | Standard Specification for Low-Carbon Nickel-Chromium-Molybdenum, Low-Carbon Nickel-Molybdenum-Chromium, Low-Carbon Nickel-Molybdenum-Chromium-Tantalum, Low-Carbon Nickel-Chromium-Molybdenum-Copper, and Low-Carbon Nickel-Chromium-Molybdenum-Tungsten | ASTM | global | paid | document | P | ok |  |
| [ASTM B575](https://store.astm.org/standards/b575) | Standard Specification for Low-Carbon Nickel-Chromium-Molybdenum, Low-Carbon Nickel-Chromium-Molybdenum-Copper, Low-Carbon Nickel-Chromium-Molybdenum-Tantalum, Low-Carbon Nickel-Chromium-Molybdenum-Tungsten, and Low-Carbon Nickel-Molybdenum-Chromium | ASTM | global | paid | document | P | ok |  |
| [ASTM B619](https://store.astm.org/standards/b619) | Standard Specification for Welded Nickel and Nickel-Cobalt Alloy Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B622](https://store.astm.org/standards/b622) | Standard Specification for Seamless Nickel and Nickel-Cobalt Alloy Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B626](https://store.astm.org/standards/b626) | Standard Specification for Welded Nickel and Nickel-Cobalt Alloy Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B637](https://store.astm.org/standards/b637) | Standard Specification for Precipitation-Hardening and Cold Worked Nickel Alloy Bars, Forgings, and Forging Stock for Moderate or High Temperature Service | ASTM | global | paid | document | P | ok |  |
| [ASTM B668](https://store.astm.org/standards/b668) | Standard Specification for Iron-Nickel-Chromium-Molybdenum Alloy Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B673](https://store.astm.org/standards/b673) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Nitrogen Alloy Welded Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B674](https://store.astm.org/standards/b674) | Standard Specification for Nickel-Iron-Chromium-Molybdenum and Iron-Nickel-Chromium-Molybdenum-Copper Welded Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B675](https://store.astm.org/standards/b675) | Standard Specification for Iron-Nickel-Chromium-Molybdenum Alloy Welded Pipe (Withdrawn 2026) | ASTM | global | paid | document | P | ok |  |
| [ASTM B677](https://store.astm.org/standards/b677) | Standard Specification for Nickel-Iron-Chromium-Molybdenum-Nitrogen Seamless Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B704](https://store.astm.org/standards/b704) | Standard Specification for Welded Nickel Alloy Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B705](https://store.astm.org/standards/b705) | Standard Specification for Nickel-Chromium-Molybdenum-Niobium Alloy, Nickel-Chromium-Molybdenum-Silicon Alloy, and Nickel-Iron-Chromium-Molybdenum-Copper Alloy Welded Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B709](https://store.astm.org/standards/b709) | Standard Specification for Iron-Nickel-Chromium-Molybdenum Alloy Plate, Sheet, and Strip | ASTM | global | paid | document | P | ok |  |
| [ASTM B265](https://store.astm.org/standards/b265) | Standard Specification for Titanium and Titanium Alloy Strip, Sheet, and Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM B338](https://store.astm.org/standards/b338) | Standard Specification for Seamless and Welded Titanium and Titanium Alloy Tubes for Condensers and Heat Exchangers | ASTM | global | paid | document | P | ok |  |
| [ASTM B348](https://store.astm.org/standards/b348) | Standard Specification for Titanium and Titanium Alloy Bars and Billets | ASTM | global | paid | document | P | ok |  |
| [ASTM B363](https://store.astm.org/standards/b363) | Standard Specification for Seamless and Welded Unalloyed Titanium and Titanium Alloy Welding Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM B367](https://store.astm.org/standards/b367) | Standard Specification for Titanium and Titanium Alloy Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM B381](https://store.astm.org/standards/b381) | Standard Specification for Titanium and Titanium Alloy Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM B861](https://store.astm.org/standards/b861) | Standard Specification for Titanium and Titanium Alloy Seamless Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B862](https://store.astm.org/standards/b862) | Standard Specification for Titanium and Titanium Alloy Welded Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B863](https://store.astm.org/standards/b863) | Standard Specification for Titanium and Titanium Alloy Wire | ASTM | global | paid | document | P | ok |  |
| [ASTM B493](https://store.astm.org/standards/b493) | Standard Specification for Zirconium and Zirconium Alloy Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM B523](https://store.astm.org/standards/b523_b523m) | Standard Specification for Seamless and Welded Zirconium and Zirconium Alloy Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B550](https://store.astm.org/standards/b550_b550m) | Standard Specification for Zirconium and Zirconium Alloy Bar and Wire | ASTM | global | paid | document | P | ok |  |
| [ASTM B551](https://store.astm.org/standards/b551_b551m) | Standard Specification for Zirconium and Zirconium Alloy Strip, Sheet, and Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM B658](https://store.astm.org/standards/b658_b658m) | Standard Specification for Seamless and Welded Zirconium and Zirconium Alloy Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B26](https://store.astm.org/standards/b26_b26m) | Standard Specification for Aluminum-Alloy Sand Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM B209](https://store.astm.org/standards/b209) | Standard Specification for Aluminum and Aluminum-Alloy Sheet and Plate | ASTM | global | paid | document | P | ok |  |
| [ASTM B210](https://store.astm.org/standards/b210) | Standard Specification for Aluminum and Aluminum-Alloy Drawn Seamless Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B211](https://store.astm.org/standards/b211) | Standard Specification for Aluminum and Aluminum-Alloy Rolled or Cold Finished Bar, Rod, and Wire | ASTM | global | paid | document | P | ok |  |
| [ASTM B221](https://store.astm.org/standards/b221) | Standard Specification for Aluminum and Aluminum-Alloy Extruded Bars, Rods, Wire, Profiles, and Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B234](https://store.astm.org/standards/b234) | Standard Specification for Aluminum and Aluminum-Alloy Drawn Seamless Tubes for Surface Condensers, Evaporators, and Heat Exchangers | ASTM | global | paid | document | P | ok |  |
| [ASTM B241](https://store.astm.org/standards/b241_b241m) | Standard Specification for Aluminum and Aluminum-Alloy Seamless Pipe and Seamless Extruded Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B247](https://store.astm.org/standards/b247) | Standard Specification for Aluminum and Aluminum-Alloy Die Forgings, Hand Forgings, and Rolled Ring Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM B345](https://store.astm.org/standards/b345_b345m) | Standard Specification for Aluminum and Aluminum-Alloy Seamless Pipe and Seamless Extruded Tube for Gas and Oil Transmission and Distribution Piping Systems (Withdrawn 2017) | ASTM | global | paid | document | P | ok |  |
| [ASTM B361](https://store.astm.org/standards/b361) | Standard Specification for Factory-Made Wrought Aluminum and Aluminum-Alloy Welding Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM B491](https://store.astm.org/standards/b491_b491m) | Standard Specification for Aluminum and Aluminum-Alloy Extruded Round Tubes for General-Purpose Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM B547](https://store.astm.org/standards/b547_b547m) | Standard Specification for Aluminum and Aluminum-Alloy Formed and Arc-Welded Round Tube (Withdrawn 2019) | ASTM | global | paid | document | P | ok |  |
| [ASTM B928](https://store.astm.org/standards/b928) | Standard Specification for High Magnesium Aluminum-Alloy Sheet and Plate for Marine Service | ASTM | global | paid | document | P | ok |  |
| [ASTM B42](https://store.astm.org/standards/b42) | Standard Specification for Seamless Copper Pipe, Standard Sizes | ASTM | global | paid | document | P | ok |  |
| [ASTM B43](https://store.astm.org/standards/b43) | Standard Specification for Seamless Red Brass Pipe, Standard Sizes | ASTM | global | paid | document | P | ok |  |
| [ASTM B61](https://store.astm.org/standards/b61) | Standard Specification for Steam or Valve Bronze Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM B62](https://store.astm.org/standards/b62) | Standard Specification for Composition Bronze or Ounce Metal Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM B68](https://store.astm.org/standards/b68) | Standard Specification for Seamless Copper Tube, Bright Annealed | ASTM | global | paid | document | P | ok |  |
| [ASTM B75](https://store.astm.org/standards/b75) | Standard Specification for Seamless Copper Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B88](https://store.astm.org/standards/b88) | Standard Specification for Seamless Copper Water Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B111](https://store.astm.org/standards/b111) | Standard Specification for Copper and Copper-Alloy Seamless Condenser Tubes and Ferrule Stock | ASTM | global | paid | document | P | ok |  |
| [ASTM B148](https://store.astm.org/standards/b148) | Standard Specification for Aluminum-Bronze Sand Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM B152](https://store.astm.org/standards/b152_b152m) | Standard Specification for Copper Sheet, Strip, Plate, and Rolled Bar | ASTM | global | paid | document | P | ok |  |
| [ASTM B169](https://store.astm.org/standards/b169) | Standard Specification for Aluminum Bronze Sheet, Strip, and Rolled Bar (Withdrawn 2001) | ASTM | global | paid | document | P | ok |  |
| [ASTM B171](https://store.astm.org/standards/b171_b171m) | Standard Specification for Copper-Alloy Plate and Sheet for Pressure Vessels, Condensers, and Heat Exchangers | ASTM | global | paid | document | P | ok |  |
| [ASTM B280](https://store.astm.org/standards/b280) | Standard Specification for Seamless Copper Tube for Air Conditioning and Refrigeration Field Service | ASTM | global | paid | document | P | ok |  |
| [ASTM B395](https://store.astm.org/standards/b395) | Standard Specification for U-Bend Seamless Copper and Copper Alloy Heat Exchanger and Condenser Tubes | ASTM | global | paid | document | P | ok |  |
| [ASTM B466](https://store.astm.org/standards/b466_b466m) | Standard Specification for Seamless Copper-Nickel Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B467](https://store.astm.org/standards/b467) | Standard Specification for Welded Copper-Nickel Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM B543](https://store.astm.org/standards/b543) | Standard Specification for Welded Copper and Copper-Alloy Heat Exchanger Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM B584](https://store.astm.org/standards/b584) | Standard Specification for Copper Alloy Sand Castings for General Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM B819](https://store.astm.org/standards/b819) | Standard Specification for Seamless Copper Tube for Medical Gas Systems | ASTM | global | paid | document | P | ok |  |

## ASTM plastics, FRP, elastomer, gasket and insulation standards

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM D1248](https://store.astm.org/standards/d1248) | Standard Specification for Polyethylene Plastics Extrusion Materials for Wire and Cable | ASTM | global | paid | document | P | ok |  |
| [ASTM D1598](https://store.astm.org/standards/d1598) | Standard Test Method for Time-to-Failure of Plastic Pipe Under Constant Internal Pressure | ASTM | global | paid | document | P | ok |  |
| [ASTM D1599](https://store.astm.org/standards/d1599) | Standard Test Method for Resistance to Short-Time Hydraulic Pressure of Plastic Pipe, Tubing, and Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM D1784](https://store.astm.org/standards/d1784) | Standard Classification System and Basis for Specification for Rigid Poly(Vinyl Chloride) (PVC) Compounds and Chlorinated Poly(Vinyl Chloride) (CPVC) Compounds | ASTM | global | paid | document | P | ok |  |
| [ASTM D1785](https://store.astm.org/standards/d1785) | Standard Specification for Poly(Vinyl Chloride) (PVC) Plastic Pipe, Schedules 40, 80, and 120 | ASTM | global | paid | document | P | ok |  |
| [ASTM D2000](https://store.astm.org/standards/d2000) | Standard Classification System for Rubber Products in Automotive Applications | ASTM | global | paid | document | P | ok |  |
| [ASTM D2105](https://store.astm.org/standards/d2105) | Standard Test Method for Longitudinal Tensile Properties of “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe and Tube | ASTM | global | paid | document | P | ok |  |
| [ASTM D2241](https://store.astm.org/standards/d2241) | Standard Specification for Poly(Vinyl Chloride) (PVC) Pressure-Rated Pipe (SDR Series) | ASTM | global | paid | document | P | ok |  |
| [ASTM D2310](https://store.astm.org/standards/d2310) | Standard Classification for Machine-Made “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe (Withdrawn 2017) | ASTM | global | paid | document | P | ok |  |
| [ASTM D2412](https://store.astm.org/standards/d2412) | Standard Test Method for Determination of External Loading Characteristics of Plastic Pipe by Parallel-Plate Loading | ASTM | global | paid | document | P | ok |  |
| [ASTM D2467](https://store.astm.org/standards/d2467) | Standard Specification for Poly(Vinyl Chloride) (PVC) Plastic Pipe Fittings, Schedule 80 | ASTM | global | paid | document | P | ok |  |
| [ASTM D2513](https://store.astm.org/standards/d2513) | Standard Specification for Polyethylene (PE) Gas Pressure Pipe, Tubing, and Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM D2564](https://store.astm.org/standards/d2564) | Standard Specification for Solvent Cements for Poly(Vinyl Chloride) (PVC) Plastic Piping Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM D2837](https://store.astm.org/standards/d2837) | Standard Test Method for Obtaining Hydrostatic Design Basis for Thermoplastic Pipe Materials or Pressure Design Basis for Thermoplastic Pipe Products | ASTM | global | paid | document | P | ok |  |
| [ASTM D2846](https://store.astm.org/standards/d2846_d2846m) | Standard Specification for Chlorinated Poly(Vinyl Chloride) (CPVC) Plastic Hot- and Cold-Water Distribution Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM D2992](https://store.astm.org/standards/d2992) | Standard Practice for Obtaining Hydrostatic or Pressure Design Basis for “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe and Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM D2996](https://store.astm.org/standards/d2996) | Standard Specification for Filament-Wound “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM D2997](https://store.astm.org/standards/d2997) | Standard Specification for Centrifugally Cast “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM D3035](https://store.astm.org/standards/d3035) | Standard Specification for Polyethylene (PE) Plastic Pipe (DR-PR) Based on Controlled Outside Diameter | ASTM | global | paid | document | P | ok |  |
| [ASTM D3299](https://store.astm.org/standards/d3299) | Standard Specification for Glass-Fiber-Reinforced Thermoset Resin Corrosion-Resistant Tanks | ASTM | global | paid | document | P | ok |  |
| [ASTM D3350](https://store.astm.org/standards/d3350) | Standard Specification for Polyethylene Plastics Pipe and Fittings Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM D3517](https://store.astm.org/standards/d3517) | Standard Specification for “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pressure Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM D3982](https://store.astm.org/standards/d3982) | Standard Specification for Contact Molded “Fiberglass” (Glass Fiber Reinforced Thermosetting Resin) Ducts | ASTM | global | paid | document | P | ok |  |
| [ASTM D4024](https://store.astm.org/standards/d4024) | Standard Specification for Machine Made “Fiberglass” (Glass-Fiber-Reinforced Thermosetting Resin) Flanges | ASTM | global | paid | document | P | ok |  |
| [ASTM D4097](https://store.astm.org/standards/d4097) | Standard Specification for Contact-Molded Glass-Fiber-Reinforced Thermoset Resin Corrosion-Resistant Tanks (Withdrawn 2026) | ASTM | global | paid | document | P | ok |  |
| [ASTM D5685](https://store.astm.org/standards/d5685) | Standard Specification for “Fiberglass” (Glass-Fiber-Reinforced Thermosetting-Resin) Pressure Pipe Fittings | ASTM | global | paid | document | P | ok |  |
| [ASTM F423](https://store.astm.org/standards/f423) | Standard Specification for Polytetrafluoroethylene (PTFE) Plastic-Lined Ferrous Metal Pipe, Fittings, and Flanges (Withdrawn 2002) | ASTM | global | paid | document | P | ok |  |
| [ASTM F437](https://store.astm.org/standards/f437) | Standard Specification for Threaded Chlorinated Poly(Vinyl Chloride) (CPVC) Plastic Pipe Fittings, Schedule 80 | ASTM | global | paid | document | P | ok |  |
| [ASTM F438](https://store.astm.org/standards/f438) | Standard Specification for Socket-Type Chlorinated Poly(Vinyl Chloride) (CPVC) Plastic Pipe Fittings, Schedule 40 | ASTM | global | paid | document | P | ok |  |
| [ASTM F439](https://store.astm.org/standards/f439) | Standard Specification for Chlorinated Poly (Vinyl Chloride) (CPVC) Plastic Pipe Fittings, Schedule 80 | ASTM | global | paid | document | P | ok |  |
| [ASTM F441](https://store.astm.org/standards/f441_f441m) | Standard Specification for Chlorinated Poly(Vinyl Chloride) (CPVC) Plastic Pipe, Schedules 40 and 80 | ASTM | global | paid | document | P | ok |  |
| [ASTM F491](https://store.astm.org/standards/f491) | Standard Specification for Poly(Vinylidene Fluoride) (PVDF) Plastic-Lined Ferrous Metal Pipe and Fittings (Withdrawn 2002) | ASTM | global | paid | document | P | ok |  |
| [ASTM F492](https://store.astm.org/standards/f492) | Standard Specification for Propylene and Polypropylene (PP) Plastic-Lined Ferrous Metal Pipe and Fittings (Withdrawn 2004) | ASTM | global | paid | document | P | ok |  |
| [ASTM F546](https://store.astm.org/standards/f546) | Standard Specification for Perfluoro (Ethylene-Propylene) Copolymer (FEP) Plastic-Lined Ferrous Metal Pipe and Fittings (Withdrawn 2002) | ASTM | global | paid | document | P | ok |  |
| [ASTM F714](https://store.astm.org/standards/f714) | Standard Specification for Polyethylene (PE) Plastic Pipe (DR-PR) Based on Outside Diameter | ASTM | global | paid | document | P | ok |  |
| [ASTM F1055](https://store.astm.org/standards/f1055) | Standard Specification for Electrofusion Type Polyethylene Fittings for Outside Diameter Controlled Polyethylene and Crosslinked Polyethylene (PEX) Pipe and Tubing | ASTM | global | paid | document | P | ok |  |
| [ASTM F1281](https://store.astm.org/standards/f1281) | Standard Specification for Crosslinked Polyethylene/Aluminum/Crosslinked Polyethylene (PEX-AL-PEX) Pressure Pipe | ASTM | global | paid | document | P | ok |  |
| [ASTM F1545](https://store.astm.org/standards/f1545) | Standard Specification for Plastic-Lined Ferrous Metal Pipe, Fittings, and Flanges | ASTM | global | paid | document | P | ok |  |
| [ASTM D395](https://store.astm.org/standards/d395) | Standard Test Methods for Rubber Property—Compression Set | ASTM | global | paid | document | P | ok |  |
| [ASTM D412](https://store.astm.org/standards/d412) | Standard Test Methods for Vulcanized Rubber and Thermoplastic Elastomers—Tension | ASTM | global | paid | document | P | ok |  |
| [ASTM D471](https://store.astm.org/standards/d471) | Standard Test Method for Rubber Property—Effect of Liquids | ASTM | global | paid | document | P | ok |  |
| [ASTM D573](https://store.astm.org/standards/d573) | Standard Test Method for Rubber—Deterioration in an Air Oven | ASTM | global | paid | document | P | ok |  |
| [ASTM D1149](https://store.astm.org/standards/d1149) | Standard Test Methods for Rubber Deterioration—Cracking in an Ozone Controlled Environment | ASTM | global | paid | document | P | ok |  |
| [ASTM D1329](https://store.astm.org/standards/d1329) | Standard Test Method for Evaluating Rubber Property—Retraction at Lower Temperatures (TR Test) | ASTM | global | paid | document | P | ok |  |
| [ASTM D1418](https://store.astm.org/standards/d1418) | Standard Practice for Rubber and Rubber Latices—Nomenclature | ASTM | global | paid | document | P | ok |  |
| [ASTM D2240](https://store.astm.org/standards/d2240) | Standard Test Method for Rubber Property—Durometer Hardness | ASTM | global | paid | document | P | ok |  |
| [ASTM F36](https://store.astm.org/standards/f36) | Standard Test Method for Compressibility and Recovery of Gasket Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM F37](https://store.astm.org/standards/f37) | Standard Test Methods for Sealability of Gasket Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM F104](https://store.astm.org/standards/f104) | Standard Classification System for Nonmetallic Gasket Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM F146](https://store.astm.org/standards/f146) | Standard Test Methods for Fluid Resistance of Gasket Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM F152](https://store.astm.org/standards/f152) | Standard Test Methods for Tension Testing of Nonmetallic Gasket Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM C167](https://store.astm.org/standards/c167) | Standard Test Methods for Thickness and Density of Blanket or Batt Thermal Insulations | ASTM | global | paid | document | P | ok |  |
| [ASTM C533](https://store.astm.org/standards/c533) | Standard Specification for Calcium Silicate Block and Pipe Thermal Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM C547](https://store.astm.org/standards/c547) | Standard Specification for Mineral Fiber Pipe Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM C552](https://store.astm.org/standards/c552) | Standard Specification for Cellular Glass Thermal Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM C591](https://store.astm.org/standards/c591) | Standard Specification for Unfaced Preformed Rigid Cellular Polyisocyanurate Thermal Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM C610](https://store.astm.org/standards/c610) | Standard Specification for Molded Expanded Perlite Block and Pipe Thermal Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM C692](https://store.astm.org/standards/c692) | Standard Test Method for Evaluating the Influence of Thermal Insulations on External Stress Corrosion Cracking Tendency of Austenitic Stainless Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM C795](https://store.astm.org/standards/c795) | Standard Specification for Thermal Insulation for Use in Contact with Austenitic Stainless Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM C871](https://store.astm.org/standards/c871) | Standard Test Methods for Chemical Analysis of Thermal Insulation Materials for Leachable Chloride, Fluoride, Silicate, and Sodium Ions | ASTM | global | paid | document | P | ok |  |
| [ASTM C1055](https://store.astm.org/standards/c1055) | Standard Guide for Heated System Surface Conditions that Produce Contact Burn Injuries | ASTM | global | paid | document | P | ok |  |
| [ASTM C1057](https://store.astm.org/standards/c1057) | Standard Practice for Determination of Skin Contact Temperature from Heated Surfaces Using a Mathematical Model and Thermesthesiometer | ASTM | global | paid | document | P | ok |  |
| [ASTM C1617](https://store.astm.org/standards/c1617) | Standard Test Method for Quantitative Accelerated Laboratory Evaluation of Extraction Solutions Containing Ions Leached from Thermal Insulation on Aqueous Corrosion of Carbon Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM E605](https://store.astm.org/standards/e605) | Standard Test Methods for Thickness and Density of Sprayed Fire-Resistive Material (SFRM) Applied to Structural Members | ASTM | global | paid | document | P | ok |  |
| [ASTM E736](https://store.astm.org/standards/e736) | Standard Test Method for Cohesion/Adhesion of Sprayed Fire-Resistive Materials Applied to Structural Members | ASTM | global | paid | document | P | ok |  |

## ASTM mechanical, metallurgical and chemical-analysis test methods

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A370](https://store.astm.org/standards/a370) | Standard Test Methods and Definitions for Mechanical Testing of Steel Products | ASTM | global | paid | document | P | ok |  |
| [ASTM A751](https://store.astm.org/standards/a751) | Standard Test Methods and Practices for Chemical Analysis of Steel Products | ASTM | global | paid | document | P | ok |  |
| [ASTM A941](https://store.astm.org/standards/a941) | Standard Terminology Relating to Steel, Stainless Steel, Related Alloys, and Ferroalloys | ASTM | global | paid | document | P | ok |  |
| [ASTM E3](https://store.astm.org/standards/e3) | Standard Guide for Preparation of Metallographic Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM E8](https://store.astm.org/standards/e8) | Standard Test Methods for Tension Testing of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E10](https://store.astm.org/standards/e10) | Standard Test Method for Brinell Hardness of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E18](https://store.astm.org/standards/e18) | Standard Test Methods for Rockwell Hardness of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E21](https://store.astm.org/standards/e21) | Standard Test Methods for Elevated Temperature Tension Tests of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E23](https://store.astm.org/standards/e23) | Standard Test Methods for Notched Bar Impact Testing of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E29](https://store.astm.org/standards/e29) | Standard Practice for Using Significant Digits in Test Data to Determine Conformance with Specifications | ASTM | global | paid | document | P | ok |  |
| [ASTM E45](https://store.astm.org/standards/e45) | Standard Test Methods for Determining the Inclusion Content of Steel | ASTM | global | paid | document | P | ok |  |
| [ASTM E92](https://store.astm.org/standards/e92) | Standard Test Methods for Vickers Hardness and Knoop Hardness of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E112](https://store.astm.org/standards/e112) | Standard Test Methods for Determining Average Grain Size | ASTM | global | paid | document | P | ok |  |
| [ASTM E139](https://store.astm.org/standards/e139) | Standard Test Methods for Conducting Creep, Creep-Rupture, and Stress-Rupture Tests of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E140](https://store.astm.org/standards/e140) | Standard Hardness Conversion Tables for Metals Relationship Among Brinell Hardness, Vickers Hardness, Rockwell Hardness, Superficial Hardness, Knoop Hardness, Scleroscope Hardness, and Leeb Hardness | ASTM | global | paid | document | P | ok |  |
| [ASTM E190](https://store.astm.org/standards/e190) | Standard Test Method for Guided Bend Test for Ductility of Welds | ASTM | global | paid | document | P | ok |  |
| [ASTM E208](https://store.astm.org/standards/e208) | Standard Test Method for Conducting Drop-Weight Test to Determine Nil-Ductility Transition Temperature of Ferritic Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM E292](https://store.astm.org/standards/e292) | Standard Test Methods for Conducting Time-for-Rupture Notch Tension Tests of Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E384](https://store.astm.org/standards/e384) | Standard Test Method for Microindentation Hardness of Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E399](https://store.astm.org/standards/e399) | Standard Test Method for Linear-Elastic Plane-Strain Fracture Toughness of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E407](https://store.astm.org/standards/e407) | Standard Practice for Microetching Metals and Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM E436](https://store.astm.org/standards/e436) | Standard Test Method for Drop-Weight Tear Tests of Ferritic Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM E466](https://store.astm.org/standards/e466) | Standard Practice for Conducting Force Controlled Constant Amplitude Axial Fatigue Tests of Metallic Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E562](https://store.astm.org/standards/e562) | Standard Test Method for Determining Volume Fraction by Systematic Manual Point Count | ASTM | global | paid | document | P | ok |  |
| [ASTM E606](https://store.astm.org/standards/e606) | Standard Practice for Strain-Controlled Fatigue Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E647](https://store.astm.org/standards/e647) | Standard Test Method for Measurement of Fatigue Crack Growth Rates | ASTM | global | paid | document | P | ok |  |
| [ASTM E1049](https://store.astm.org/standards/e1049) | Standard Practices for Cycle Counting in Fatigue Analysis | ASTM | global | paid | document | P | ok |  |
| [ASTM E1221](https://store.astm.org/standards/e1221) | Standard Test Method for Determining Plane-Strain Crack-Arrest Fracture Toughness, KIa, of Ferritic Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM E1290](https://store.astm.org/standards/e1290) | Standard Test Method for Crack-Tip Opening Displacement (CTOD) Fracture Toughness Measurement | ASTM | global | paid | document | P | ok |  |
| [ASTM E1820](https://store.astm.org/standards/e1820) | Standard Test Method for Measurement of Fracture Toughness | ASTM | global | paid | document | P | ok |  |
| [ASTM E1823](https://store.astm.org/standards/e1823) | Standard Terminology Relating to Fatigue and Fracture Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E1921](https://store.astm.org/standards/e1921) | Standard Test Method for Determination of Reference Temperature, T0, for Ferritic Steels in the Transition Range | ASTM | global | paid | document | P | ok |  |
| [ASTM E415](https://store.astm.org/standards/e415) | Standard Test Method for Analysis of Carbon and Low-Alloy Steel by Spark Atomic Emission Spectrometry | ASTM | global | paid | document | P | ok |  |
| [ASTM E1086](https://store.astm.org/standards/e1086) | Standard Test Method for Analysis of Austenitic Stainless Steel by Spark Atomic Emission Spectrometry | ASTM | global | paid | document | P | ok |  |
| [ASTM E1476](https://store.astm.org/standards/e1476) | Standard Guide for Metals Identification, Grade Verification, and Sorting | ASTM | global | paid | document | P | ok |  |

## ASTM corrosion test methods and practices

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A262](https://store.astm.org/standards/a262) | Standard Practices for Detecting Susceptibility to Intergranular Attack in Austenitic Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM A380](https://store.astm.org/standards/a380) | Standard Practice for Cleaning, Descaling, and Passivation of Stainless Steel Parts, Equipment, and Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM A763](https://store.astm.org/standards/a763) | Standard Practices for Detecting Susceptibility to Intergranular Attack in Ferritic Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM A923](https://store.astm.org/standards/a923) | Standard Test Methods for Detecting Detrimental Intermetallic Phase in Duplex Austenitic/Ferritic Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM A967](https://store.astm.org/standards/a967) | Standard Specification for Chemical Passivation Treatments for Stainless Steel Parts | ASTM | global | paid | document | P | ok |  |
| [ASTM A1084](https://store.astm.org/standards/a1084) | Standard Test Method for Detecting Detrimental Phases in Lean Duplex Austenitic/Ferritic Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM B117](https://store.astm.org/standards/b117) | Standard Practice for Operating Salt Spray (Fog) Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM G1](https://store.astm.org/standards/g1) | Standard Practice for Preparing, Cleaning, and Evaluating Corrosion Test Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM G3](https://store.astm.org/standards/g3) | Standard Practice for Conventions Applicable to Electrochemical Measurements in Corrosion Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM G4](https://store.astm.org/standards/g4) | Standard Guide for Conducting Corrosion Tests in Field Applications (Withdrawn 2023) | ASTM | global | paid | document | P | ok |  |
| [ASTM G5](https://store.astm.org/standards/g5) | Standard Reference Test Method for Making Potentiodynamic Anodic Polarization Measurements | ASTM | global | paid | document | P | ok |  |
| [ASTM G15](https://store.astm.org/standards/g15) | Standard Terminology Relating to Corrosion and Corrosion Testing (Withdrawn 2010) | ASTM | global | paid | document | P | ok |  |
| [ASTM G16](https://store.astm.org/standards/g16) | Standard Guide for Applying Statistics to Analysis of Corrosion Data | ASTM | global | paid | document | P | ok |  |
| [ASTM G28](https://store.astm.org/standards/g28) | Standard Test Methods for Detecting Susceptibility to Intergranular Corrosion in Wrought, Nickel-Rich, Chromium-Bearing Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM G30](https://store.astm.org/standards/g30) | Standard Practice for Making and Using U-Bend Stress-Corrosion Test Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM G31](https://store.astm.org/standards/g31) | Standard Guide for Laboratory Immersion Corrosion Testing of Metals | ASTM | global | paid | document | P | ok |  |
| [ASTM G32](https://store.astm.org/standards/g32) | Standard Test Method for Cavitation Erosion Using Vibratory Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM G34](https://store.astm.org/standards/g34) | Standard Test Method for Exfoliation Corrosion Susceptibility in 2XXX and 7XXX Series Aluminum Alloys (EXCO Test) | ASTM | global | paid | document | P | ok |  |
| [ASTM G36](https://store.astm.org/standards/g36) | Standard Practice for Evaluating Stress-Corrosion-Cracking Resistance of Metals and Alloys in a Boiling Magnesium Chloride Solution | ASTM | global | paid | document | P | ok |  |
| [ASTM G37](https://store.astm.org/standards/g37) | Standard Practice for Use of Mattsson's Solution of pH 7.2 to Evaluate the Stress-Corrosion Cracking Susceptibility of Copper-Zinc Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM G38](https://store.astm.org/standards/g38) | Standard Practice for Making and Using C-Ring Stress-Corrosion Test Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM G39](https://store.astm.org/standards/g39) | Standard Practice for Preparation and Use of Bent-Beam Stress-Corrosion Test Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM G40](https://store.astm.org/standards/g40) | Standard Terminology Relating to Wear and Erosion | ASTM | global | paid | document | P | ok |  |
| [ASTM G41](https://store.astm.org/standards/g41) | Standard Practice for Determining Cracking Susceptibility of Metals Exposed Under Stress to a Hot Salt Environment | ASTM | global | paid | document | P | ok |  |
| [ASTM G44](https://store.astm.org/standards/g44) | Standard Practice for Exposure of Metals and Alloys by Alternate Immersion in Neutral 3.5 % Sodium Chloride Solution | ASTM | global | paid | document | P | ok |  |
| [ASTM G46](https://store.astm.org/standards/g46) | Standard Guide for Examination and Evaluation of Pitting Corrosion | ASTM | global | paid | document | P | ok |  |
| [ASTM G47](https://store.astm.org/standards/g47) | Standard Test Method for Determining Susceptibility to Stress-Corrosion Cracking of 2XXX and 7XXX Aluminum Alloy Products | ASTM | global | paid | document | P | ok |  |
| [ASTM G48](https://store.astm.org/standards/g48) | Standard Test Methods for Pitting and Crevice Corrosion Resistance of Stainless Steels and Related Alloys by Use of Ferric Chloride Solution | ASTM | global | paid | document | P | ok |  |
| [ASTM G49](https://store.astm.org/standards/g49) | Standard Practice for Preparation and Use of Direct Tension Stress-Corrosion Test Specimens | ASTM | global | paid | document | P | ok |  |
| [ASTM G51](https://store.astm.org/standards/g51) | Standard Test Method for Measuring pH of Soil for Use in Corrosion Evaluations | ASTM | global | paid | document | P | ok |  |
| [ASTM G52](https://store.astm.org/standards/g52) | Standard Practice for Exposing and Evaluating Metals and Alloys in Surface Seawater | ASTM | global | paid | document | P | ok |  |
| [ASTM G57](https://store.astm.org/standards/g57) | Standard Test Method for Measurement of Soil Resistivity Using the Wenner Four-Electrode Method | ASTM | global | paid | document | P | ok |  |
| [ASTM G58](https://store.astm.org/standards/g58) | Standard Practice for Preparation of Stress-Corrosion Test Specimens for Weldments | ASTM | global | paid | document | P | ok |  |
| [ASTM G59](https://store.astm.org/standards/g59) | Standard Test Method for Conducting Potentiodynamic Polarization Resistance Measurements | ASTM | global | paid | document | P | ok |  |
| [ASTM G61](https://store.astm.org/standards/g61) | Standard Test Method for Conducting Cyclic Potentiodynamic Polarization Measurements for Localized Corrosion Susceptibility of Iron-, Nickel-, or Cobalt-Based Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM G64](https://store.astm.org/standards/g64) | Standard Classification of Resistance to Stress-Corrosion Cracking of Heat-Treatable Aluminum Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM G71](https://store.astm.org/standards/g71) | Standard Guide for Conducting and Evaluating Galvanic Corrosion Tests in Electrolytes | ASTM | global | paid | document | P | ok |  |
| [ASTM G73](https://store.astm.org/standards/g73) | Standard Test Method for Liquid Impingement Erosion Using Rotating Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM G76](https://store.astm.org/standards/g76) | Standard Test Method for Conducting Erosion Tests by Solid Particle Impingement Using Gas Jets | ASTM | global | paid | document | P | ok |  |
| [ASTM G78](https://store.astm.org/standards/g78) | Standard Guide for Crevice Corrosion Testing of Iron-Base and Nickel-Base Stainless Alloys in Seawater and Other Chloride-Containing Aqueous Environments | ASTM | global | paid | document | P | ok |  |
| [ASTM G102](https://store.astm.org/standards/g102) | Standard Practice for Calculation of Corrosion Rates and Related Information from Electrochemical Measurements | ASTM | global | paid | document | P | ok |  |
| [ASTM G106](https://store.astm.org/standards/g106) | Standard Practice for Verification of Algorithm and Equipment for Electrochemical Impedance Measurements | ASTM | global | paid | document | P | ok |  |
| [ASTM G108](https://store.astm.org/standards/g108) | Standard Test Methods for Electrochemical Reactivation (EPR) for Detecting Sensitization of AISI Type 304 and 304L Stainless Steels | ASTM | global | paid | document | P | ok |  |
| [ASTM G110](https://store.astm.org/standards/g110) | Standard Practice for Evaluating Intergranular Corrosion Resistance of Heat Treatable Aluminum Alloys by Immersion in Sodium Chloride + Hydrogen Peroxide Solution | ASTM | global | paid | document | P | ok |  |
| [ASTM G111](https://store.astm.org/standards/g111) | Standard Guide for Corrosion Tests in High Temperature or High Pressure Environment, or Both | ASTM | global | paid | document | P | ok |  |
| [ASTM G123](https://store.astm.org/standards/g123) | Standard Test Method for Evaluating Stress-Corrosion Cracking of Stainless Alloys with Different Nickel Content in Boiling Acidified Sodium Chloride Solution | ASTM | global | paid | document | P | ok |  |
| [ASTM G129](https://store.astm.org/standards/g129) | Standard Practice for Slow Strain Rate Testing to Evaluate the Susceptibility of Metallic Materials to Environmentally Assisted Cracking | ASTM | global | paid | document | P | ok |  |
| [ASTM G150](https://store.astm.org/standards/g150) | Standard Test Method for Electrochemical Critical Pitting Temperature Testing of Stainless Steels and Related Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM G157](https://store.astm.org/standards/g157) | Standard Guide for Evaluating Corrosion Properties of Wrought Iron- and Nickel-Based Corrosion Resistant Alloys for Chemical Process Industries | ASTM | global | paid | document | P | ok |  |
| [ASTM G170](https://store.astm.org/standards/g170) | Standard Guide for Evaluating and Qualifying Oilfield and Refinery Corrosion Inhibitors in the Laboratory | ASTM | global | paid | document | P | ok |  |
| [ASTM G184](https://store.astm.org/standards/g184) | Standard Practice for Evaluating and Qualifying Oil Field and Refinery Corrosion Inhibitors Using Rotating Cage | ASTM | global | paid | document | P | ok |  |
| [ASTM G185](https://store.astm.org/standards/g185) | Standard Practice for Evaluating and Qualifying Oil Field and Refinery Corrosion Inhibitors Using the Rotating Cylinder Electrode | ASTM | global | paid | document | P | ok |  |
| [ASTM G189](https://store.astm.org/standards/g189) | Standard Guide for Laboratory Simulation of Corrosion Under Insulation | ASTM | global | paid | document | P | ok |  |
| [ASTM G192](https://store.astm.org/standards/g192) | Standard Test Method for Determining the Crevice Repassivation Potential of Corrosion-Resistant Alloys Using a Potentiodynamic-Galvanostatic-Potentiostatic Technique | ASTM | global | paid | document | P | ok |  |
| [ASTM G193](https://store.astm.org/standards/g193) | Standard Terminology and Acronyms Relating to Corrosion | ASTM | global | paid | document | P | ok |  |
| [ASTM G199](https://store.astm.org/standards/g199) | Standard Guide for Electrochemical Noise Measurement | ASTM | global | paid | document | P | ok |  |
| [ASTM G205](https://store.astm.org/standards/g205) | Standard Guide for Determining Emulsion Properties, Wetting Behavior, and Corrosion-Inhibitory Properties of Crude Oils | ASTM | global | paid | document | P | ok |  |

## ASTM oxygen-compatibility and hydrogen-embrittlement standards

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM G63](https://store.astm.org/standards/g63) | Standard Guide for Evaluating Nonmetallic Materials for Oxygen Service | ASTM | global | paid | document | P | ok |  |
| [ASTM G72](https://store.astm.org/standards/g72) | Standard Test Method for Autogenous Ignition Temperature of Liquids and Solids in a High-Pressure Oxygen-Enriched Environment | ASTM | global | paid | document | P | ok |  |
| [ASTM G74](https://store.astm.org/standards/g74) | Standard Test Method for Ignition Sensitivity of Nonmetallic Materials and Components by Gaseous Fluid Impact | ASTM | global | paid | document | P | ok |  |
| [ASTM G86](https://store.astm.org/standards/g86) | Standard Test Method for Determining Ignition Sensitivity of Materials to Mechanical Impact in Ambient Liquid Oxygen and Pressurized Liquid and Gaseous Oxygen Environments | ASTM | global | paid | document | P | ok |  |
| [ASTM G88](https://store.astm.org/standards/g88) | Standard Guide for Designing Systems for Oxygen Service | ASTM | global | paid | document | P | ok |  |
| [ASTM G93](https://store.astm.org/standards/g93) | Standard Practice for Cleaning Methods and Cleanliness Levels for Material and Equipment Used in Oxygen-Enriched Environments | ASTM | global | paid | document | P | ok |  |
| [ASTM G94](https://store.astm.org/standards/g94) | Standard Guide for Evaluating Metals for Oxygen Service | ASTM | global | paid | document | P | ok |  |
| [ASTM G124](https://store.astm.org/standards/g124) | Standard Test Method for Determining the Combustion Behavior of Metallic Materials in Oxygen-Enriched Atmospheres | ASTM | global | paid | document | P | ok |  |
| [ASTM G125](https://store.astm.org/standards/g125) | Standard Test Method for Measuring Liquid and Solid Material Fire Limits in Gaseous Oxidants | ASTM | global | paid | document | P | ok |  |
| [ASTM G126](https://store.astm.org/standards/g126) | Standard Terminology Relating to the Compatibility and Sensitivity of Materials in Oxygen Enriched Atmospheres | ASTM | global | paid | document | P | ok |  |
| [ASTM G128](https://store.astm.org/standards/g128) | Standard Guide for Control of Hazards and Risks in Oxygen Enriched Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM G142](https://store.astm.org/standards/g142) | Standard Test Method for Determination of Susceptibility of Metals to Embrittlement in Hydrogen Containing Environments at High Pressure, High Temperature, or Both | ASTM | global | paid | document | P | ok |  |
| [ASTM G146](https://store.astm.org/standards/g146) | Standard Practice for Evaluation of Disbonding of Bimetallic Stainless Alloy/Steel Plate for Use in High-Pressure, High-Temperature Refinery Hydrogen Service | ASTM | global | paid | document | P | ok |  |
| [ASTM G148](https://store.astm.org/standards/g148) | Standard Practice for Evaluation of Hydrogen Uptake, Permeation, and Transport in Metals by an Electrochemical Technique | ASTM | global | paid | document | P | ok |  |
| [ASTM F519](https://store.astm.org/standards/f519) | Standard Test Method for Mechanical Hydrogen Embrittlement Evaluation of Plating/Coating Processes and Service Environments | ASTM | global | paid | document | P | ok |  |
| [ASTM F1459](https://store.astm.org/standards/f1459) | Standard Test Method for Determination of the Susceptibility of Metallic Materials to Hydrogen Gas Embrittlement (HGE) | ASTM | global | paid | document | P | ok |  |
| [ASTM F1624](https://store.astm.org/standards/f1624) | Standard Test Method for Measurement of Hydrogen Embrittlement Threshold in Steel by the Incremental Step Loading Technique | ASTM | global | paid | document | P | ok |  |
| [ASTM F1940](https://store.astm.org/standards/f1940) | Standard Test Method for Process Control Verification to Prevent Hydrogen Embrittlement in Plated or Coated Fasteners | ASTM | global | paid | document | P | ok |  |

## ASTM nondestructive examination standards

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM A388](https://store.astm.org/standards/a388_a388m) | Standard Practice for Ultrasonic Examination of Steel Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM A577](https://store.astm.org/standards/a577_a577m) | Standard Specification for Ultrasonic Angle-Beam Examination of Steel Plates | ASTM | global | paid | document | P | ok |  |
| [ASTM A609](https://store.astm.org/standards/a609_a609m) | Standard Practice for Castings, Carbon, Low-Alloy, and Martensitic Stainless Steel, Ultrasonic Examination Thereof | ASTM | global | paid | document | P | ok |  |
| [ASTM A745](https://store.astm.org/standards/a745_a745m) | Standard Practice for Ultrasonic Examination of Austenitic Steel Forgings | ASTM | global | paid | document | P | ok |  |
| [ASTM E94](https://store.astm.org/standards/e94) | Standard Guide for Radiographic Examination | ASTM | global | paid | document | P | ok |  |
| [ASTM E114](https://store.astm.org/standards/e114) | Standard Practice for Ultrasonic Pulse-Echo Straight-Beam Contact Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E125](https://store.astm.org/standards/e125) | Standard Reference Photographs for Magnetic Particle Indications on Ferrous Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM E164](https://store.astm.org/standards/e164) | Standard Practice for Contact Ultrasonic Testing of Weldments | ASTM | global | paid | document | P | ok |  |
| [ASTM E165](https://store.astm.org/standards/e165) | Standard Practice for Liquid Penetrant Examination for General Industry | ASTM | global | paid | document | P | ok |  |
| [ASTM E186](https://store.astm.org/standards/e186) | Standard Reference Radiographs for Heavy-Walled (2 to 412 in. (50.8 to 114 mm)) Steel Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM E213](https://store.astm.org/standards/e213) | Standard Practice for Ultrasonic Testing of Metal Pipe and Tubing | ASTM | global | paid | document | P | ok |  |
| [ASTM E280](https://store.astm.org/standards/e280) | Standard Reference Radiographs for Heavy-Walled (412 to 12 in. (114 to 305 mm)) Steel Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM E309](https://store.astm.org/standards/e309) | Standard Practice for Eddy Current Examination of Steel Tubular Products | ASTM | global | paid | document | P | ok |  |
| [ASTM E317](https://store.astm.org/standards/e317) | Standard Practice for Evaluating Performance Characteristics of Ultrasonic Pulse-Echo Testing Instruments and Systems without the Use of Electronic Measurement Instruments | ASTM | global | paid | document | P | ok |  |
| [ASTM E426](https://store.astm.org/standards/e426) | Standard Practice for Electromagnetic (Eddy Current) Examination of Seamless and Welded Tubular Products, Titanium, Austenitic Stainless Steel and Similar Alloys | ASTM | global | paid | document | P | ok |  |
| [ASTM E432](https://store.astm.org/standards/e432) | Standard Guide for Selection of a Leak Testing Method | ASTM | global | paid | document | P | ok |  |
| [ASTM E446](https://store.astm.org/standards/e446) | Standard Reference Radiographs for Steel Castings Up to 2 in. (50.8 mm) in Thickness | ASTM | global | paid | document | P | ok |  |
| [ASTM E498](https://store.astm.org/standards/e498) | Standard Test Methods for Leaks Using the Mass Spectrometer Leak Detector or Residual Gas Analyzer in the Tracer Probe Mode | ASTM | global | paid | document | P | ok |  |
| [ASTM E499](https://store.astm.org/standards/e499) | Standard Test Methods for Leaks Using the Mass Spectrometer Leak Detector in the Detector Probe Mode | ASTM | global | paid | document | P | ok |  |
| [ASTM E515](https://store.astm.org/standards/e515) | Standard Practice for Leaks Using Bubble Emission Techniques | ASTM | global | paid | document | P | ok |  |
| [ASTM E543](https://store.astm.org/standards/e543) | Standard Specification for Agencies Performing Nondestructive Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E569](https://store.astm.org/standards/e569) | Standard Practice for Acoustic Emission Monitoring of Structures During Controlled Stimulation | ASTM | global | paid | document | P | ok |  |
| [ASTM E650](https://store.astm.org/standards/e650) | Standard Guide for Mounting Piezoelectric Acoustic Emission Sensors | ASTM | global | paid | document | P | ok |  |
| [ASTM E709](https://store.astm.org/standards/e709) | Standard Guide for Magnetic Particle Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E797](https://store.astm.org/standards/e797) | Standard Practice for Measuring Thickness by Manual Ultrasonic Pulse-Echo Contact Method | ASTM | global | paid | document | P | ok |  |
| [ASTM E1002](https://store.astm.org/standards/e1002) | Standard Practice for Leaks Using Ultrasonics | ASTM | global | paid | document | P | ok |  |
| [ASTM E1003](https://store.astm.org/standards/e1003) | Standard Practice for Hydrostatic Leak Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E1030](https://store.astm.org/standards/e1030) | Standard Test Method for Radiographic Examination of Metallic Castings | ASTM | global | paid | document | P | ok |  |
| [ASTM E1067](https://store.astm.org/standards/e1067) | Standard Practice for Acoustic Emission Examination of Fiberglass Reinforced Plastic Resin (FRP) Tanks/Vessels | ASTM | global | paid | document | P | ok |  |
| [ASTM E1118](https://store.astm.org/standards/e1118) | Standard Practice for Acoustic Emission Examination of Reinforced Thermosetting Resin Pipe (RTRP) | ASTM | global | paid | document | P | ok |  |
| [ASTM E1139](https://store.astm.org/standards/e1139) | Standard Practice for Continuous Monitoring of Acoustic Emission from Metal Pressure Boundaries | ASTM | global | paid | document | P | ok |  |
| [ASTM E1316](https://store.astm.org/standards/e1316) | Standard Terminology for Nondestructive Examinations | ASTM | global | paid | document | P | ok |  |
| [ASTM E1417](https://store.astm.org/standards/e1417) | Standard Practice for Liquid Penetrant Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E1419](https://store.astm.org/standards/e1419) | Standard Practice for Examination of Seamless, Gas-Filled, Pressure Vessels Using Acoustic Emission | ASTM | global | paid | document | P | ok |  |
| [ASTM E1444](https://store.astm.org/standards/e1444) | Standard Practice for Magnetic Particle Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E1962](https://store.astm.org/standards/e1962) | Standard Practice for Ultrasonic Surface Testing Using Electromagnetic Acoustic Transducer (EMAT) Techniques | ASTM | global | paid | document | P | ok |  |
| [ASTM E2007](https://store.astm.org/standards/e2007) | Standard Guide for Computed Radiography | ASTM | global | paid | document | P | ok |  |
| [ASTM E2096](https://store.astm.org/standards/e2096) | Standard Practice for In Situ Examination of Ferromagnetic Heat-Exchanger Tubes Using Remote Field Testing | ASTM | global | paid | document | P | ok |  |
| [ASTM E2375](https://store.astm.org/standards/e2375) | Standard Practice for Ultrasonic Testing of Wrought Products | ASTM | global | paid | document | P | ok |  |
| [ASTM E2491](https://store.astm.org/standards/e2491) | Standard Guide for Evaluating Performance Characteristics of Phased-Array Ultrasonic Testing Instruments and Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM E2700](https://store.astm.org/standards/e2700) | Standard Practice for Contact Ultrasonic Testing of Welds Using Phased Arrays | ASTM | global | paid | document | P | ok |  |
| [ASTM E2884](https://store.astm.org/standards/e2884) | Standard Guide for Eddy Current Testing of Electrically Conducting Materials Using Conformable Sensor Arrays | ASTM | global | paid | document | P | ok |  |
| [ASTM E2905](https://store.astm.org/standards/e2905_e2905m) | Standard Practice for Examination of Mill and Kiln Girth Gear Teeth—Electromagnetic Methods | ASTM | global | paid | document | P | ok |  |

## ASTM flash point, flammability, dust and thermal-reactivity test methods

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM D56](https://store.astm.org/standards/d56) | Standard Test Method for Flash Point by Tag Closed Cup Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D86](https://store.astm.org/standards/d86) | Standard Test Method for Distillation of Petroleum Products and Liquid Fuels at Atmospheric Pressure | ASTM | global | paid | document | P | ok |  |
| [ASTM D92](https://store.astm.org/standards/d92) | Standard Test Method for Flash and Fire Points by Cleveland Open Cup Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D93](https://store.astm.org/standards/d93) | Standard Test Methods for Flash Point by Pensky-Martens Closed Cup Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D240](https://store.astm.org/standards/d240) | Standard Test Method for Heat of Combustion of Liquid Hydrocarbon Fuels by Bomb Calorimeter | ASTM | global | paid | document | P | ok |  |
| [ASTM D323](https://store.astm.org/standards/d323) | Standard Test Method for Vapor Pressure of Petroleum Products (Reid Method) | ASTM | global | paid | document | P | ok |  |
| [ASTM D1310](https://store.astm.org/standards/d1310) | Standard Test Method for Flash Point and Fire Point of Liquids by Tag Open-Cup Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM D2863](https://store.astm.org/standards/d2863) | Standard Test Method for Measuring the Minimum Oxygen Concentration to Support Candle-Like Combustion of Plastics (Oxygen Index) | ASTM | global | paid | document | P | ok |  |
| [ASTM D2879](https://store.astm.org/standards/d2879) | Standard Test Method for Vapor Pressure-Temperature Relationship and Initial Decomposition Temperature of Liquids by Isoteniscope | ASTM | global | paid | document | P | ok |  |
| [ASTM D2887](https://store.astm.org/standards/d2887) | Standard Test Method for Boiling Range Distribution of Petroleum Fractions by Gas Chromatography | ASTM | global | paid | document | P | ok |  |
| [ASTM D3278](https://store.astm.org/standards/d3278) | Standard Test Methods for Flash Point of Liquids by Small Scale Closed-Cup Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM D3828](https://store.astm.org/standards/d3828) | Standard Test Methods for Flash Point by Small Scale Closed Cup Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D3941](https://store.astm.org/standards/d3941) | Standard Test Method for Flash Point by the Equilibrium Method With a Closed-Cup Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM D4206](https://store.astm.org/standards/d4206) | Standard Test Method for Sustained Burning of Liquid Mixtures Using the Small Scale Open-Cup Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM D4809](https://store.astm.org/standards/d4809) | Standard Test Method for Heat of Combustion of Liquid Hydrocarbon Fuels by Bomb Calorimeter (Precision Method) | ASTM | global | paid | document | P | ok |  |
| [ASTM D5191](https://store.astm.org/standards/d5191) | Standard Test Method for Vapor Pressure of Petroleum Products and Liquid Fuels (Mini Method) | ASTM | global | paid | document | P | ok |  |
| [ASTM D6450](https://store.astm.org/standards/d6450) | Standard Test Method for Flash Point by Continuously Closed Cup (CCCFP) Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D7094](https://store.astm.org/standards/d7094) | Standard Test Method for Flash Point by Modified Continuously Closed Cup (MCCCFP) Tester | ASTM | global | paid | document | P | ok |  |
| [ASTM D7236](https://store.astm.org/standards/d7236) | Standard Test Method for Flash Point by Small Scale Closed Cup Tester (Ramp Method) | ASTM | global | paid | document | P | ok |  |
| [ASTM E476](https://store.astm.org/standards/e476) | Standard Test Method for Thermal Instability of Confined Condensed Phase Systems (Confinement Test) | ASTM | global | paid | document | P | ok |  |
| [ASTM E487](https://store.astm.org/standards/e487) | Standard Test Methods for Constant-Temperature Stability of Chemical Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E537](https://store.astm.org/standards/e537) | Standard Test Method for Thermal Stability of Chemicals by Differential Scanning Calorimetry | ASTM | global | paid | document | P | ok |  |
| [ASTM E582](https://store.astm.org/standards/e582) | Standard Test Method for Minimum Ignition Energy and Quenching Distance in Gaseous Mixtures | ASTM | global | paid | document | P | ok |  |
| [ASTM E659](https://store.astm.org/standards/e659) | Standard Test Method for Autoignition Temperature of Chemicals | ASTM | global | paid | document | P | ok |  |
| [ASTM E681](https://store.astm.org/standards/e681) | Standard Test Method for Concentration Limits of Flammability of Chemicals (Vapors and Gases) | ASTM | global | paid | document | P | ok |  |
| [ASTM E698](https://store.astm.org/standards/e698) | Standard Test Method for Kinetic Parameters for Thermally Unstable Materials Using Differential Scanning Calorimetry and the Flynn/Wall/Ozawa Method | ASTM | global | paid | document | P | ok |  |
| [ASTM E711](https://store.astm.org/standards/e711) | Standard Test Method for Gross Calorific Value of Refuse-Derived Fuel by the Bomb Calorimeter | ASTM | global | paid | document | P | ok |  |
| [ASTM E918](https://store.astm.org/standards/e918) | Standard Practice for Determining Limits of Flammability of Chemicals at Elevated Temperature and Pressure | ASTM | global | paid | document | P | ok |  |
| [ASTM E1226](https://store.astm.org/standards/e1226) | Standard Test Method for Explosibility of Dust Clouds | ASTM | global | paid | document | P | ok |  |
| [ASTM E1231](https://store.astm.org/standards/e1231) | Standard Practice for Calculation of Hazard Potential Figures of Merit for Thermally Unstable Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E1232](https://store.astm.org/standards/e1232) | Standard Test Method for Temperature Limit of Flammability of Chemicals | ASTM | global | paid | document | P | ok |  |
| [ASTM E1445](https://store.astm.org/standards/e1445) | Standard Terminology Relating to Hazard Potential of Chemicals | ASTM | global | paid | document | P | ok |  |
| [ASTM E1491](https://store.astm.org/standards/e1491) | Standard Test Method for Minimum Autoignition Temperature of Dust Clouds | ASTM | global | paid | document | P | ok |  |
| [ASTM E1515](https://store.astm.org/standards/e1515) | Standard Test Method for Minimum Explosible Concentration of Combustible Dusts | ASTM | global | paid | document | P | ok |  |
| [ASTM E1641](https://store.astm.org/standards/e1641) | Standard Test Method for Decomposition Kinetics by Thermogravimetry Using the Ozawa/Flynn/Wall Method | ASTM | global | paid | document | P | ok |  |
| [ASTM E1981](https://store.astm.org/standards/e1981) | Standard Guide for Assessing Thermal Stability of Materials by Methods of Accelerating Rate Calorimetry | ASTM | global | paid | document | P | ok |  |
| [ASTM E2012](https://store.astm.org/standards/e2012) | Standard Guide for the Preparation of a Binary Chemical Compatibility Chart | ASTM | global | paid | document | P | ok |  |
| [ASTM E2019](https://store.astm.org/standards/e2019) | Standard Test Method for Minimum Ignition Energy of a Dust Cloud in Air | ASTM | global | paid | document | P | ok |  |
| [ASTM E2021](https://store.astm.org/standards/e2021) | Standard Test Method for Hot-Surface Ignition Temperature of Dust Layers | ASTM | global | paid | document | P | ok |  |
| [ASTM E2046](https://store.astm.org/standards/e2046) | Standard Test Method for Reaction Induction Time by Thermal Analysis | ASTM | global | paid | document | P | ok |  |
| [ASTM E2070](https://store.astm.org/standards/e2070) | Standard Test Methods for Kinetic Parameters by Differential Scanning Calorimetry Using Isothermal Methods | ASTM | global | paid | document | P | ok |  |
| [ASTM E2079](https://store.astm.org/standards/e2079) | Standard Test Methods for Limiting Oxygen (Oxidant) Concentration in Gases and Vapors | ASTM | global | paid | document | P | ok |  |
| [ASTM E2550](https://store.astm.org/standards/e2550) | Standard Test Method for Thermal Stability by Thermogravimetry | ASTM | global | paid | document | P | ok |  |

## ASTM fire test methods

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM E84](https://store.astm.org/standards/e84) | Standard Test Method for Surface Burning Characteristics of Building Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E108](https://store.astm.org/standards/e108) | Standard Test Methods for Fire Tests of Roof Coverings | ASTM | global | paid | document | P | ok |  |
| [ASTM E119](https://store.astm.org/standards/e119) | Standard Test Methods for Fire Tests of Building Construction and Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E136](https://store.astm.org/standards/e136) | Standard Test Method for Assessing Combustibility of Materials Using a Vertical Tube Furnace at 750 °C | ASTM | global | paid | document | P | ok |  |
| [ASTM E162](https://store.astm.org/standards/e162) | Standard Test Method for Surface Flammability of Materials Using a Radiant Heat Energy Source | ASTM | global | paid | document | P | ok |  |
| [ASTM E648](https://store.astm.org/standards/e648) | Standard Test Method for Critical Radiant Flux of Floor-Covering Systems Using a Radiant Heat Energy Source | ASTM | global | paid | document | P | ok |  |
| [ASTM E662](https://store.astm.org/standards/e662) | Standard Test Method for Specific Optical Density of Smoke Generated by Solid Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM E814](https://store.astm.org/standards/e814) | Standard Test Method for Fire Tests of Penetration Firestop Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM E1317](https://store.astm.org/standards/e1317) | Standard Test Method for Flammability of Surface Finishes | ASTM | global | paid | document | P | ok |  |
| [ASTM E1321](https://store.astm.org/standards/e1321) | Standard Test Method for Determining Material Ignition and Flame Spread Properties | ASTM | global | paid | document | P | ok |  |
| [ASTM E1354](https://store.astm.org/standards/e1354) | Standard Test Method for Heat and Visible Smoke Release Rates for Materials and Products Using an Oxygen Consumption Calorimeter | ASTM | global | paid | document | P | ok |  |
| [ASTM E1529](https://store.astm.org/standards/e1529) | Standard Test Methods for Determining Effects of Large Hydrocarbon Pool Fires on Structural Members and Assemblies | ASTM | global | paid | document | P | ok |  |
| [ASTM E1537](https://store.astm.org/standards/e1537) | Standard Test Method for Fire Testing of Upholstered Furniture | ASTM | global | paid | document | P | ok |  |
| [ASTM E1623](https://store.astm.org/standards/e1623) | Standard Test Method for Determination of Fire and Thermal Parameters of Materials, Products, and Systems Using an Intermediate Scale Calorimeter (ICAL) | ASTM | global | paid | document | P | ok |  |
| [ASTM E1725](https://store.astm.org/standards/e1725) | Standard Test Methods for Fire Tests of Fire-Resistive Barrier Systems for Electrical System Components | ASTM | global | paid | document | P | ok |  |
| [ASTM E1966](https://store.astm.org/standards/e1966) | Standard Test Method for Fire-Resistive Joint Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM E2032](https://store.astm.org/standards/e2032) | Standard Practice for Extension of Data From Fire Resistance Tests Conducted in Accordance with ASTM E 119 | ASTM | global | paid | document | P | ok |  |
| [ASTM E2058](https://store.astm.org/standards/e2058) | Standard Test Methods for Measurement of Material Flammability Using a Fire Propagation Apparatus (FPA) | ASTM | global | paid | document | P | ok |  |
| [ASTM E2174](https://store.astm.org/standards/e2174) | Standard Practice for On-Site Inspection of Installed Firestop Systems | ASTM | global | paid | document | P | ok |  |
| [ASTM E2307](https://store.astm.org/standards/e2307) | Standard Test Method for Determining Fire Resistance of Perimeter Fire Barriers Using Intermediate-Scale, Multi-story Test Apparatus | ASTM | global | paid | document | P | ok |  |
| [ASTM E2393](https://store.astm.org/standards/e2393) | Standard Practice for On-Site Inspection of Installed Fire Resistive Joint Systems and Perimeter Fire Barriers | ASTM | global | paid | document | P | ok |  |
| [ASTM E2652](https://store.astm.org/standards/e2652) | Standard Test Method for Assessing Combustibility of Materials Using a Tube Furnace with a Cone-shaped Airflow Stabilizer, at 750 °C | ASTM | global | paid | document | P | ok |  |
| [ASTM E2768](https://store.astm.org/standards/e2768) | Standard Test Method for Extended Duration Surface Burning Characteristics of Building Materials (30 min Tunnel Test) | ASTM | global | paid | document | P | ok |  |
| [ASTM D635](https://store.astm.org/standards/d635) | Standard Test Method for Rate of Burning and/or Extent and Time of Burning of Plastics in a Horizontal Position | ASTM | global | paid | document | P | ok |  |
| [ASTM D1929](https://store.astm.org/standards/d1929) | Standard Test Method for Determining Ignition Temperature of Plastics | ASTM | global | paid | document | P | ok |  |
| [ASTM D3801](https://store.astm.org/standards/d3801) | Standard Test Method for Measuring the Comparative Burning Characteristics of Solid Plastics in a Vertical Position | ASTM | global | paid | document | P | ok |  |
| [ASTM E759](https://store.astm.org/standards/e759) | Standard Test Method for Effect of Deflection on Sprayed Fire-Resistive Material Applied to Structural Members | ASTM | global | paid | document | P | ok |  |
| [ASTM E760](https://store.astm.org/standards/e760) | Standard Test Method for Effect of Impact on Bonding of Sprayed Fire-Resistive Material Applied to Structural Members | ASTM | global | paid | document | P | ok |  |
| [ASTM E761](https://store.astm.org/standards/e761) | Standard Test Method for Compressive Strength of Sprayed Fire-Resistive Material Applied to Structural Members | ASTM | global | paid | document | P | ok |  |
| [ASTM E859](https://store.astm.org/standards/e859) | Standard Test Method for Air Erosion of Sprayed Fire-Resistive Materials (SFRMs) Applied to Structural Members | ASTM | global | paid | document | P | ok |  |
| [ASTM E937](https://store.astm.org/standards/e937) | Standard Test Method for Corrosion of Steel by Sprayed Fire-Resistive Material (SFRM) Applied to Structural Members | ASTM | global | paid | document | P | ok |  |

## ASTM electrical, arc-flash and protective-equipment standards

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM D149](https://store.astm.org/standards/d149) | Standard Test Method for Dielectric Breakdown Voltage and Dielectric Strength of Solid Electrical Insulating Materials at Commercial Power Frequencies | ASTM | global | paid | document | P | ok |  |
| [ASTM D257](https://store.astm.org/standards/d257) | Standard Test Methods for DC Resistance or Conductance of Insulating Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM D877](https://store.astm.org/standards/d877) | Standard Test Method for Dielectric Breakdown Voltage of Insulating Liquids Using Disk Electrodes | ASTM | global | paid | document | P | ok |  |
| [ASTM D1816](https://store.astm.org/standards/d1816) | Standard Test Method for Dielectric Breakdown Voltage of Insulating Liquids Using VDE Electrodes | ASTM | global | paid | document | P | ok |  |
| [ASTM D120](https://store.astm.org/standards/d120) | Standard Specification for Rubber Insulating Gloves | ASTM | global | paid | document | P | ok |  |
| [ASTM F478](https://store.astm.org/standards/f478) | Standard Specification for In-Service Care of Insulating Line Hose and Covers | ASTM | global | paid | document | P | ok |  |
| [ASTM F496](https://store.astm.org/standards/f496) | Standard Specification for In-Service Care of Insulating Gloves and Sleeves | ASTM | global | paid | document | P | ok |  |
| [ASTM F696](https://store.astm.org/standards/f696) | Standard Specification for Leather Protectors for Rubber Insulating Gloves | ASTM | global | paid | document | P | ok |  |
| [ASTM F855](https://store.astm.org/standards/f855) | Standard Specifications for Temporary Protective Grounds to Be Used on De-energized Electric Power Lines and Equipment | ASTM | global | paid | document | P | ok |  |
| [ASTM F887](https://store.astm.org/standards/f887) | Standard Specifications for Personal Climbing Equipment | ASTM | global | paid | document | P | ok |  |
| [ASTM F1236](https://store.astm.org/standards/f1236) | Standard Guide for Visual Inspection of Electrical Protective Rubber Products | ASTM | global | paid | document | P | ok |  |
| [ASTM F1506](https://store.astm.org/standards/f1506) | Standard Performance Specification for Flame Resistant and Electric Arc Rated Protective Clothing Worn by Workers Exposed to Flames and Electric Arcs | ASTM | global | paid | document | P | ok |  |
| [ASTM F1891](https://store.astm.org/standards/f1891) | Standard Specification for Arc and Flame Resistant Rainwear | ASTM | global | paid | document | P | ok |  |
| [ASTM F1930](https://store.astm.org/standards/f1930) | Standard Test Method for Evaluation of Flame-Resistant Clothing for Protection Against Fire Simulations Using an Instrumented Manikin | ASTM | global | paid | document | P | ok |  |
| [ASTM F1959](https://store.astm.org/standards/f1959_f1959m) | Standard Test Method for Determining the Arc Rating of Materials for Clothing | ASTM | global | paid | document | P | ok |  |
| [ASTM F2178](https://store.astm.org/standards/f2178) | Standard Test Method for Determining the Arc Rating and Standard Specification for Eye or Face Protective Products | ASTM | global | paid | document | P | ok |  |
| [ASTM F2412](https://store.astm.org/standards/f2412) | Standard Test Methods for Foot Protection | ASTM | global | paid | document | P | ok |  |
| [ASTM F2413](https://store.astm.org/standards/f2413) | Standard Specification for Performance Requirements for Protective (Safety) Toe Cap Footwear | ASTM | global | paid | document | P | ok |  |
| [ASTM F2621](https://store.astm.org/standards/f2621) | Standard Practice for Determining Response Characteristics and Design Integrity of Arc Rated Finished Products in an Electric Arc Exposure | ASTM | global | paid | document | P | ok |  |
| [ASTM F2675](https://store.astm.org/standards/f2675_f2675m) | Standard Test Method for Determining Arc Ratings of Hand Protective Products Developed and Used for Electrical Arc Flash Protection | ASTM | global | paid | document | P | ok |  |
| [ASTM F2676](https://store.astm.org/standards/f2676) | Standard Test Method for Determining the Protective Performance of an Arc Protective Blanket for Electric Arc Hazards | ASTM | global | paid | document | P | ok |  |
| [ASTM F2757](https://store.astm.org/standards/f2757) | Standard Guide for Home Laundering Care and Maintenance of Flame Resistant or Arc Rated Clothing | ASTM | global | paid | document | P | ok |  |
| [ASTM F739](https://store.astm.org/standards/f739) | Standard Test Method for Permeation of Liquids and Gases Through Protective Clothing Materials Under Conditions of Continuous Contact | ASTM | global | paid | document | P | ok |  |
| [ASTM F903](https://store.astm.org/standards/f903) | Standard Test Method for Resistance of Materials Used in Protective Clothing to Penetration by Liquids | ASTM | global | paid | document | P | ok |  |
| [ASTM F1001](https://store.astm.org/standards/f1001) | Standard Guide for Selection of Chemicals to Evaluate Protective Clothing Materials | ASTM | global | paid | document | P | ok |  |
| [ASTM F1342](https://store.astm.org/standards/f1342) | Standard Test Method for Protective Clothing Material Resistance to Puncture | ASTM | global | paid | document | P | ok |  |
| [ASTM F2700](https://store.astm.org/standards/f2700) | Standard Test Method for Unsteady-State Heat Transfer Evaluation of Flame-Resistant Materials for Clothing with Continuous Heating | ASTM | global | paid | document | P | ok |  |
| [ASTM F2703](https://store.astm.org/standards/f2703) | Standard Test Method for Unsteady-State Heat Transfer Evaluation of Flame-Resistant Materials for Clothing with Burn Injury Prediction | ASTM | global | paid | document | P | ok |  |
| [ASTM F2733](https://store.astm.org/standards/f2733) | Standard Specification for Flame-Resistant Rainwear for Protection Against Flame Hazards | ASTM | global | paid | document | P | ok |  |

## ASTM gas analysis methods

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASTM D1945](https://store.astm.org/standards/d1945) | Standard Test Method for Analysis of Natural Gas by Gas Chromatography | ASTM | global | paid | document | P | ok |  |
| [ASTM D1946](https://store.astm.org/standards/d1946) | Standard Practice for Analysis of Gaseous Fuels by Gas Chromatography | ASTM | global | paid | document | P | ok |  |
| [ASTM D3588](https://store.astm.org/standards/d3588) | Standard Practice for Calculating Heat Value, Compressibility Factor, and Relative Density of Gaseous Fuels | ASTM | global | paid | document | P | ok |  |
| [ASTM D4468](https://store.astm.org/standards/d4468) | Standard Test Method for Total Sulfur in Gaseous Fuels by Hydrogenolysis and Rateometric Colorimetry | ASTM | global | paid | document | P | ok |  |
| [ASTM D5504](https://store.astm.org/standards/d5504) | Standard Test Method for Determination of Sulfur Compounds in Natural Gas and Gaseous Fuels by Gas Chromatography and Chemiluminescence | ASTM | global | paid | document | P | ok |  |
| [ASTM D6228](https://store.astm.org/standards/d6228) | Standard Test Method for Determination of Sulfur Compounds in Natural Gas and Gaseous Fuels by Gas Chromatography and Flame Photometric Detection | ASTM | global | paid | document | P | ok |  |
| [ASTM D7833](https://store.astm.org/standards/d7833) | Standard Test Method for Determination of Hydrocarbons and Non-Hydrocarbon Gases in Gaseous Mixtures by Gas Chromatography | ASTM | global | paid | document | P | ok |  |

## Welding, hot work and examination qualification

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ASME BPVC V](https://www.asme.org/codes-standards) | Nondestructive examination | ASME | global | paid | catalogue | C | ok |  |
| [ASME BPVC IX](https://www.asme.org/codes-standards) | Welding, brazing and fusing qualifications | ASME | global | paid | catalogue | C | ok |  |
| [AWS D1.1](https://pubs.aws.org/) | Structural welding code: steel | AWS | global | paid | catalogue | C | ok |  |
| [AWS D1.6](https://pubs.aws.org/) | Structural welding code: stainless steel | AWS | global | paid | catalogue | C | ok |  |
| [AWS B2.1](https://pubs.aws.org/) | Welding procedure and performance qualification | AWS | global | paid | catalogue | C | ok |  |
| [AWS D10.4](https://pubs.aws.org/) | Welding austenitic chromium-nickel stainless steel piping and tubing | AWS | global | paid | catalogue | C | ok |  |
| [AWS A5 (series)](https://pubs.aws.org/) | Filler metal specifications | AWS | global | paid | catalogue | C | ok |  |
| [API STD 1104](https://publications.api.org/) | Welding of pipelines and related facilities | API | global | paid | catalogue | C | robots |  |
| [API RP 2201](https://publications.api.org/) | Safe hot tapping practices in the petroleum and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [API RP 2009](https://publications.api.org/) | Safe welding, cutting and hot work practices in the petroleum and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [ISO 15614 (series)](https://www.iso.org/search.html?q=ISO%2015614%20%28series%29) | Specification and qualification of welding procedures: welding procedure test | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 9606 (series)](https://www.iso.org/search.html?q=ISO%209606%20%28series%29) | Qualification testing of welders: fusion welding | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 3834 (series)](https://www.iso.org/search.html?q=ISO%203834%20%28series%29) | Quality requirements for fusion welding of metallic materials | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 5817](https://www.iso.org/search.html?q=ISO%205817) | Welding: quality levels for imperfections | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 9712](https://www.iso.org/search.html?q=ISO%209712) | Non-destructive testing: qualification and certification of personnel | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 17635](https://www.iso.org/search.html?q=ISO%2017635) | Non-destructive testing of welds: general rules | ISO | global | paid | catalogue | C | blocked |  |
| [ASNT SNT-TC-1A](https://www.asnt.org/) | Personnel qualification and certification in nondestructive testing | ASNT | global | paid | catalogue | C | ok |  |

## Fire protection: active, passive, detection and fire modelling

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [NFPA 1](https://www.nfpa.org/codes-and-standards/nfpa-1-standard-development/1) | Fire Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 10](https://www.nfpa.org/codes-and-standards/nfpa-10-standard-development/10) | Portable Fire Extinguishers | NFPA | global | mixed | document | C | ok |  |
| [NFPA 11](https://www.nfpa.org/codes-and-standards/nfpa-11-standard-development/11) | Low-, Medium-, and High-Expansion Foam | NFPA | global | mixed | document | C | ok |  |
| [NFPA 12](https://www.nfpa.org/codes-and-standards/nfpa-12-standard-development/12) | Carbon Dioxide Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 12A](https://www.nfpa.org/codes-and-standards/nfpa-12a-standard-development/12a) | Halon 1301 Fire Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 13](https://www.nfpa.org/codes-and-standards/nfpa-13-standard-development/13) | Installation of Sprinkler Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 14](https://www.nfpa.org/codes-and-standards/nfpa-14-standard-development/14) | Installation of Standpipe and Hose Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 15](https://www.nfpa.org/codes-and-standards/nfpa-15-standard-development/15) | Water Spray Fixed Systems for Fire Protection | NFPA | global | mixed | document | C | ok |  |
| [NFPA 16](https://www.nfpa.org/codes-and-standards/nfpa-16-standard-development/16) | Installation of Foam-Water Sprinkler and Foam-Water Spray Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 17](https://www.nfpa.org/codes-and-standards/nfpa-17-standard-development/17) | Dry Chemical Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 20](https://www.nfpa.org/codes-and-standards/nfpa-20-standard-development/20) | Installation of Stationary Pumps for Fire Protection | NFPA | global | mixed | document | C | ok |  |
| [NFPA 22](https://www.nfpa.org/codes-and-standards/nfpa-22-standard-development/22) | Water Tanks for Private Fire Protection | NFPA | global | mixed | document | C | ok |  |
| [NFPA 24](https://www.nfpa.org/codes-and-standards/nfpa-24-standard-development/24) | Installation of Private Fire Service Mains and Their Appurtenances | NFPA | global | mixed | document | C | ok |  |
| [NFPA 25](https://www.nfpa.org/codes-and-standards/nfpa-25-standard-development/25) | Inspection, Testing, and Maintenance of Water-Based Fire Protection Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 72](https://www.nfpa.org/codes-and-standards/nfpa-72-standard-development/72) | National Fire Alarm and Signaling Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 750](https://www.nfpa.org/codes-and-standards/nfpa-750-standard-development/750) | Water Mist Fire Protection Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 770](https://www.nfpa.org/codes-and-standards/nfpa-770-standard-development/770) | Hybrid (Water and Inert Gas) Fire-Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 2001](https://www.nfpa.org/codes-and-standards/nfpa-2001-standard-development/2001) | Clean Agent Fire Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 2010](https://www.nfpa.org/codes-and-standards/nfpa-2010-standard-development/2010) | Fixed Aerosol Fire-Extinguishing Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 80](https://www.nfpa.org/codes-and-standards/nfpa-80-standard-development/80) | Fire Doors and Other Opening Protectives | NFPA | global | mixed | document | C | ok |  |
| [NFPA 101](https://www.nfpa.org/codes-and-standards/nfpa-101-standard-development/101) | Life Safety Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 221](https://www.nfpa.org/codes-and-standards/nfpa-221-standard-development/221) | High Challenge Fire Walls, Fire Walls, and Fire Barrier Walls | NFPA | global | mixed | document | C | ok |  |
| [NFPA 251](https://www.nfpa.org/codes-and-standards/nfpa-251-standard-development/251) | Standard Methods of Tests of Fire Resistance of Building Construction and Materials | NFPA | global | mixed | document | C | ok | Withdrawn; shown for legacy references. |
| [NFPA 600](https://www.nfpa.org/codes-and-standards/nfpa-600-standard-development/600) | Facility Fire Brigades | NFPA | global | mixed | document | C | ok |  |
| [NFPA 1081](https://www.nfpa.org/codes-and-standards/nfpa-1081-standard-development/1081) | Facility Fire Brigade Member Professional Qualifications | NFPA | global | mixed | document | C | ok |  |
| [NFPA 551](https://www.nfpa.org/codes-and-standards/nfpa-551-standard-development/551) | Evaluation of Fire Risk Assessments | NFPA | global | mixed | document | C | ok |  |
| [NFPA 921](https://www.nfpa.org/codes-and-standards/nfpa-921-standard-development/921) | Fire and Explosion Investigations | NFPA | global | mixed | document | C | ok |  |
| [NFPA 5000](https://www.nfpa.org/codes-and-standards/nfpa-5000-standard-development/5000) | Building Construction and Safety Code | NFPA | global | mixed | document | C | ok |  |
| [API RP 2001](https://publications.api.org/) | Fire protection in refineries | API | global | paid | catalogue | C | robots |  |
| [API RP 2021](https://publications.api.org/) | Management of atmospheric storage tank fires | API | global | paid | catalogue | C | robots |  |
| [API RP 2030](https://publications.api.org/) | Application of fixed water spray systems for fire protection in the petroleum and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [API RP 2218](https://publications.api.org/) | Fireproofing practices in petroleum and petrochemical processing plants | API | global | paid | catalogue | C | robots |  |
| [API PUBL 2510A](https://publications.api.org/) | Fire-protection considerations for the design and operation of LPG storage facilities | API | global | paid | catalogue | C | robots |  |
| [API RP 14G](https://publications.api.org/) | Fire prevention and control on open type offshore production platforms | API | global | paid | catalogue | C | robots |  |
| [ISO 13702](https://www.iso.org/search.html?q=ISO%2013702) | Control and mitigation of fires and explosions on offshore production installations | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 22899 (series)](https://www.iso.org/search.html?q=ISO%2022899%20%28series%29) | Determination of the resistance to jet fires of passive fire protection materials | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 834 (series)](https://www.iso.org/search.html?q=ISO%20834%20%28series%29) | Fire-resistance tests: elements of building construction | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 20088 (series)](https://www.iso.org/search.html?q=ISO%2020088%20%28series%29) | Resistance to cryogenic spillage of insulation materials | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 10497](https://www.iso.org/search.html?q=ISO%2010497) | Testing of valves: fire type-testing requirements | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 7240 (series)](https://www.iso.org/search.html?q=ISO%207240%20%28series%29) | Fire detection and alarm systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 14520 (series)](https://www.iso.org/search.html?q=ISO%2014520%20%28series%29) | Gaseous fire-extinguishing systems | ISO | global | paid | catalogue | C | blocked |  |
| [UL 1709](https://www.shopulstandards.com/) | Rapid rise fire tests of protection materials for structural steel | UL | US | mixed | catalogue | C | ok |  |
| [UL 263](https://www.shopulstandards.com/) | Fire tests of building construction and materials | UL | US | mixed | catalogue | C | ok |  |
| [UL 162](https://www.shopulstandards.com/) | Foam equipment and liquid concentrates | UL | US | mixed | catalogue | C | ok |  |
| [UL 521](https://www.shopulstandards.com/) | Heat detectors for fire protective signaling systems | UL | US | mixed | catalogue | C | ok |  |
| [UL 2075](https://www.shopulstandards.com/) | Gas and vapor detectors and sensors | UL | US | mixed | catalogue | C | ok |  |
| [FM Global Property Loss Prevention Data Sheets](https://www.fm.com/resources/fm-data-sheets) | Loss-prevention data sheets (e.g. DS 7-14 fire protection for chemical plants, DS 7-32 ignitable liquid operations, DS 7-45 safety controls and protective systems, DS 7-76 combustible dust) | FM | global | free-registration | catalogue | C | blocked | Free with registration; confirm each data sheet number and title on the FM site. |
| [EI Model Code of Safe Practice Part 19](https://www.energyinst.org/technical/publications) | Fire precautions at petroleum refineries and bulk storage installations | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI Guidelines for design and protection against severe fires](https://www.energyinst.org/technical/publications) | Guidelines for the design and protection of pressure systems to withstand severe fires | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI Guidance on passive fire protection](https://www.energyinst.org/technical/publications) | Availability and selection of passive and active fire protection for process equipment | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI 15](https://www.energyinst.org/technical/publications) | Model Code of Safe Practice Part 15: area classification for installations handling flammable fluids | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EN 1991-1-2](https://standards.cencenelec.eu/) | Eurocode 1: actions on structures exposed to fire | EN | EU | paid | catalogue | C | robots |  |
| [EN 1993-1-2](https://standards.cencenelec.eu/) | Eurocode 3: design of steel structures, structural fire design | EN | EU | paid | catalogue | C | robots |  |
| [EN 1363 (series)](https://standards.cencenelec.eu/) | Fire resistance tests | EN | EU | paid | catalogue | C | robots |  |
| [EN 13501 (series)](https://standards.cencenelec.eu/) | Fire classification of construction products and building elements | EN | EU | paid | catalogue | C | robots |  |
| [EN 54 (series)](https://standards.cencenelec.eu/) | Fire detection and fire alarm systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 12845](https://standards.cencenelec.eu/) | Fixed firefighting systems: automatic sprinkler systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 13565 (series)](https://standards.cencenelec.eu/) | Fixed firefighting systems: foam systems | EN | EU | paid | catalogue | C | robots |  |
| [NUREG-1805](https://www.nrc.gov/reading-rm/doc-collections/nuregs/staff/sr1805/index.html) | Fire Dynamics Tools: quantitative fire hazard analysis methods | US NRC | US | free | document | C | blocked |  |
| [FDS and Smokeview](https://pages.nist.gov/fds-smv/) | Fire Dynamics Simulator and visualisation tool, with user and validation guides | NIST | US | free | document | C | ok |  |

## Explosion, deflagration, blast and combustible dust

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [NFPA 67](https://www.nfpa.org/codes-and-standards/nfpa-67-standard-development/67) | Explosion Protection for Gaseous Mixtures in Pipe Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 68](https://www.nfpa.org/codes-and-standards/nfpa-68-standard-development/68) | Explosion Protection by Deflagration Venting | NFPA | global | mixed | document | C | ok |  |
| [NFPA 69](https://www.nfpa.org/codes-and-standards/nfpa-69-standard-development/69) | Explosion Prevention Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 660](https://www.nfpa.org/codes-and-standards/nfpa-660-standard-development/660) | Combustible Dusts and Particulate Solids | NFPA | global | mixed | document | C | ok | Consolidates the former NFPA 61, 484, 652, 654, 655 and 664 (2025 edition). |
| [NFPA 652](https://www.nfpa.org/codes-and-standards/nfpa-652-standard-development/652) | Fundamentals of Combustible Dust | NFPA | global | mixed | document | C | ok | Consolidated into NFPA 660; shown for legacy references. |
| [NFPA 654](https://www.nfpa.org/codes-and-standards/nfpa-654-standard-development/654) | Prevention of Fire and Dust Explosions from the Manufacturing, Processing, and Handling of Combustible Particulate Solids | NFPA | global | mixed | document | C | ok | Consolidated into NFPA 660; shown for legacy references. |
| [NFPA 484](https://www.nfpa.org/codes-and-standards/nfpa-484-standard-development/484) | Combustible Metals | NFPA | global | mixed | document | C | ok | Consolidated into NFPA 660; shown for legacy references. |
| [NFPA 61](https://www.nfpa.org/codes-and-standards/nfpa-61-standard-development/61) | Prevention of Fires and Dust Explosions in Agricultural and Food Processing Facilities | NFPA | global | mixed | document | C | ok | Consolidated into NFPA 660; shown for legacy references. |
| [NFPA 664](https://www.nfpa.org/codes-and-standards/nfpa-664-standard-development/664) | Prevention of Fires and Explosions in Wood Processing and Woodworking Facilities | NFPA | global | mixed | document | C | ok | Consolidated into NFPA 660; shown for legacy references. |
| [NFPA 495](https://www.nfpa.org/codes-and-standards/nfpa-495-standard-development/495) | Explosive Materials Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 85](https://www.nfpa.org/codes-and-standards/nfpa-85-standard-development/85) | Boiler and Combustion Systems Hazards Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 86](https://www.nfpa.org/codes-and-standards/nfpa-86-standard-development/86) | Ovens and Furnaces | NFPA | global | mixed | document | C | ok |  |
| [NFPA 87](https://www.nfpa.org/codes-and-standards/nfpa-87-standard-development/87) | Fluid Heaters | NFPA | global | mixed | document | C | ok |  |
| [NFPA 91](https://www.nfpa.org/codes-and-standards/nfpa-91-standard-development/91) | Exhaust Systems for Air Conveying of Vapors, Gases, Mists, and Particulate Solids | NFPA | global | mixed | document | C | ok |  |
| [EN 1127-1](https://standards.cencenelec.eu/) | Explosive atmospheres: explosion prevention and protection, basic concepts and methodology | EN | EU | paid | catalogue | C | robots |  |
| [EN 14491](https://standards.cencenelec.eu/) | Dust explosion venting protective systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 14994](https://standards.cencenelec.eu/) | Gas explosion venting protective systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 14373](https://standards.cencenelec.eu/) | Explosion suppression systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 14797](https://standards.cencenelec.eu/) | Explosion venting devices | EN | EU | paid | catalogue | C | robots |  |
| [EN 15089](https://standards.cencenelec.eu/) | Explosion isolation systems | EN | EU | paid | catalogue | C | robots |  |
| [EN 14460](https://standards.cencenelec.eu/) | Explosion resistant equipment | EN | EU | paid | catalogue | C | robots |  |
| [EN 14034 (series)](https://standards.cencenelec.eu/) | Determination of explosion characteristics of dust clouds | EN | EU | paid | catalogue | C | robots |  |
| [EN 15967](https://standards.cencenelec.eu/) | Determination of maximum explosion pressure and rate of pressure rise of gases and vapours | EN | EU | paid | catalogue | C | robots |  |
| [EN 1839](https://standards.cencenelec.eu/) | Determination of explosion limits and limiting oxygen concentration for gases and vapours | EN | EU | paid | catalogue | C | robots |  |
| [ISO/IEC 80079-20-2](https://www.iso.org/search.html?q=ISO/IEC%2080079-20-2) | Explosive atmospheres: material characteristics, combustible dusts test methods | ISO / IEC | global | paid | catalogue | C | blocked |  |
| [IEC 80079-20-1](https://www.iso.org/search.html?q=IEC%2080079-20-1) | Explosive atmospheres: material characteristics for gas and vapour classification | ISO / IEC | global | paid | catalogue | C | blocked |  |
| [ISO 16852](https://www.iso.org/search.html?q=ISO%2016852) | Flame arresters: performance requirements, test methods and limits for use | ISO / IEC | global | paid | catalogue | C | blocked |  |
| [ISO 6184 (series)](https://www.iso.org/search.html?q=ISO%206184%20%28series%29) | Explosion protection systems | ISO / IEC | global | paid | catalogue | C | blocked |  |
| [CCPS VCE/BLEVE/Flash Fire](https://www.aiche.org/ccps/publications) | Guidelines for Vapor Cloud Explosion, Pressure Vessel Burst, BLEVE and Flash Fire Hazards | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Combustible Dust](https://www.aiche.org/ccps/publications) | Guidelines for Combustible Dust Hazard Analysis | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Deflagration and Detonation](https://www.aiche.org/ccps/publications) | Deflagration and detonation flame arresters (concept book) | CCPS | global | paid | catalogue | C | robots |  |
| [UFC 3-340-02](https://www.wbdg.org/dod/ufc/ufc-3-340-02) ([PDF](https://www.wbdg.org/FFC/DOD/UFC/ufc_3_340_02_2008_c2.pdf)) | Structures to Resist the Effects of Accidental Explosions | US DoD | US | free | document | C | ok |  |
| [ASCE Blast Design](https://ascelibrary.org/) | Design of Blast-Resistant Buildings in Petrochemical Facilities | ASCE | global | paid | catalogue | C | blocked |  |
| [ASCE/SEI 59](https://ascelibrary.org/) | Blast protection of buildings | ASCE | global | paid | catalogue | C | blocked |  |
| [ASCE/SEI 7](https://ascelibrary.org/) | Minimum design loads and associated criteria for buildings and other structures | ASCE | global | paid | catalogue | C | blocked |  |
| [FABIG Technical Notes](https://www.fabig.com/) | Fire and Blast Information Group technical notes and guidance | FABIG | global | mixed | catalogue | C | ok |  |
| [GESTIS-DUST-EX](https://www.dguv.de/ifa/gestis/gestis-staub-ex/index-2.jsp) | Database of combustion and explosion characteristics of dusts | IFA / DGUV | EU | free | document | C | ok |  |
| [OSHA combustible dust](https://www.osha.gov/combustible-dust) | Combustible dust topic page and guidance | OSHA | US | free | document | C | ok |  |

## Hazardous areas, electrical safety, static and lightning

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [IEC 60079-0](https://webstore.iec.ch/) | Explosive atmospheres: equipment, general requirements | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-1](https://webstore.iec.ch/) | Equipment protection by flameproof enclosures "d" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-2](https://webstore.iec.ch/) | Equipment protection by pressurized enclosure "p" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-7](https://webstore.iec.ch/) | Equipment protection by increased safety "e" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-10-1](https://webstore.iec.ch/) | Classification of areas: explosive gas atmospheres | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-10-2](https://webstore.iec.ch/) | Classification of areas: explosive dust atmospheres | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-11](https://webstore.iec.ch/) | Equipment protection by intrinsic safety "i" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-13](https://webstore.iec.ch/) | Equipment protection by pressurized room "p" and artificially ventilated room "v" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-14](https://webstore.iec.ch/) | Electrical installations design, selection and erection | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-15](https://webstore.iec.ch/) | Equipment protection by type of protection "n" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-17](https://webstore.iec.ch/) | Electrical installations inspection and maintenance | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-18](https://webstore.iec.ch/) | Equipment protection by encapsulation "m" | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-19](https://webstore.iec.ch/) | Equipment repair, overhaul and reclamation | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-25](https://webstore.iec.ch/) | Intrinsically safe electrical systems | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-29 (series)](https://webstore.iec.ch/) | Gas detectors: performance, selection, installation, use and maintenance | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60079-31](https://webstore.iec.ch/) | Equipment dust ignition protection by enclosure "t" | IEC | global | paid | catalogue | C | ok |  |
| [IEC TS 60079-32-1](https://webstore.iec.ch/) | Electrostatic hazards: guidance | IEC | global | paid | catalogue | C | ok |  |
| [IEC 62305 (series)](https://webstore.iec.ch/) | Protection against lightning | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61936-1](https://webstore.iec.ch/) | Power installations exceeding 1 kV a.c. | IEC | global | paid | catalogue | C | ok |  |
| [IEC 60364 (series)](https://webstore.iec.ch/) | Low-voltage electrical installations | IEC | global | paid | catalogue | C | ok |  |
| [IEC 61482 (series)](https://webstore.iec.ch/) | Live working: protective clothing against the thermal hazards of an electric arc | IEC | global | paid | catalogue | C | ok |  |
| [NFPA 70](https://www.nfpa.org/codes-and-standards/nfpa-70-standard-development/70) | National Electrical Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 70B](https://www.nfpa.org/codes-and-standards/nfpa-70b-standard-development/70b) | Electrical Equipment Maintenance | NFPA | global | mixed | document | C | ok |  |
| [NFPA 70E](https://www.nfpa.org/codes-and-standards/nfpa-70e-standard-development/70e) | Electrical Safety in the Workplace | NFPA | global | mixed | document | C | ok |  |
| [NFPA 77](https://www.nfpa.org/codes-and-standards/nfpa-77-standard-development/77) | Static Electricity | NFPA | global | mixed | document | C | ok |  |
| [NFPA 496](https://www.nfpa.org/codes-and-standards/nfpa-496-standard-development/496) | Purged and Pressurized Enclosures for Electrical Equipment | NFPA | global | mixed | document | C | ok |  |
| [NFPA 497](https://www.nfpa.org/codes-and-standards/nfpa-497-standard-development/497) | Classification of Flammable Liquids, Gases, or Vapors and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas | NFPA | global | mixed | document | C | ok |  |
| [NFPA 499](https://www.nfpa.org/codes-and-standards/nfpa-499-standard-development/499) | Classification of Combustible Dusts and of Hazardous (Classified) Locations for Electrical Installations in Chemical Process Areas | NFPA | global | mixed | document | C | ok |  |
| [NFPA 780](https://www.nfpa.org/codes-and-standards/nfpa-780-standard-development/780) | Installation of Lightning Protection Systems | NFPA | global | mixed | document | C | ok |  |
| [API RP 500](https://publications.api.org/) | Classification of locations for electrical installations at petroleum facilities classified as Class I, Division 1 and 2 | API | global | paid | catalogue | C | robots |  |
| [API RP 505](https://publications.api.org/) | Classification of locations for electrical installations at petroleum facilities classified as Class I, Zone 0, 1 and 2 | API | global | paid | catalogue | C | robots |  |
| [API RP 2003](https://publications.api.org/) | Protection against ignitions arising out of static, lightning and stray currents | API | global | paid | catalogue | C | robots |  |
| [API RP 545](https://publications.api.org/) | Lightning protection of aboveground storage tanks for flammable or combustible liquids | API | global | paid | catalogue | C | robots |  |
| [API RP 540](https://publications.api.org/) | Electrical installations in petroleum processing plants | API | global | paid | catalogue | C | robots |  |
| [API RP 2216](https://publications.api.org/) | Ignition risk of hydrocarbon liquids and vapors by hot surfaces in the open air | API | global | paid | catalogue | C | robots |  |
| [IEEE 1584](https://standards.ieee.org/) | Guide for performing arc-flash hazard calculations | IEEE | global | paid | catalogue | C | ok |  |
| [IEEE 80](https://standards.ieee.org/) | Guide for safety in AC substation grounding | IEEE | global | paid | catalogue | C | ok |  |
| [IEEE 142](https://standards.ieee.org/) | Grounding of industrial and commercial power systems | IEEE | global | paid | catalogue | C | ok |  |
| [IEEE C2](https://standards.ieee.org/) | National Electrical Safety Code | IEEE | global | paid | catalogue | C | ok |  |
| [IEEE 242](https://standards.ieee.org/) | Protection and coordination of industrial and commercial power systems | IEEE | global | paid | catalogue | C | ok |  |
| [IECEx system](https://www.iecex.com/) | International certification system for equipment used in explosive atmospheres, with certificate database | IECEx | global | free | document | C | ok |  |

## Layout, facility siting, buildings and human factors

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [API RP 752](https://publications.api.org/) | Management of hazards associated with location of process plant permanent buildings | API | global | paid | catalogue | C | robots |  |
| [API RP 753](https://publications.api.org/) | Management of hazards associated with location of process plant portable buildings | API | global | paid | catalogue | C | robots |  |
| [API RP 756](https://publications.api.org/) | Management of hazards associated with location of process plant tents | API | global | paid | catalogue | C | robots |  |
| [API RP 755](https://publications.api.org/) | Fatigue risk management systems for personnel in the refining and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [CCPS Facility Siting](https://www.aiche.org/ccps/publications) | Guidelines for Siting and Layout of Facilities | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Occupied Buildings](https://www.aiche.org/ccps/publications) | Guidelines for Evaluating Process Plant Buildings for External Explosions, Fires, and Toxic Releases | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Human Factors](https://www.aiche.org/ccps/publications) | Human Factors Methods for Improving Performance in the Process Industries | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Human Reliability](https://www.aiche.org/ccps/publications) | Guidelines for Preventing Human Error in Process Safety | CCPS | global | paid | catalogue | C | robots |  |
| [GAP.2.5.2](https://axaxl.com/) | Oil and chemical plant layout and spacing | GAPS / industry | global | mixed | catalogue | C | ok | Insurer guideline (originally IRI/GE GAP, now AXA XL); obtain from the owner. |
| [ISO 15544](https://www.iso.org/search.html?q=ISO%2015544) | Offshore production installations: emergency response requirements and guidelines | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 11064 (series)](https://www.iso.org/search.html?q=ISO%2011064%20%28series%29) | Ergonomic design of control centres | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 7010](https://www.iso.org/search.html?q=ISO%207010) | Graphical symbols: registered safety signs | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 14122 (series)](https://www.iso.org/search.html?q=ISO%2014122%20%28series%29) | Safety of machinery: permanent means of access to machinery | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 7731](https://www.iso.org/search.html?q=ISO%207731) | Danger signals for public and work areas | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 9241 (series)](https://www.iso.org/search.html?q=ISO%209241%20%28series%29) | Ergonomics of human-system interaction | ISO | global | paid | catalogue | C | blocked |  |
| [NFPA 704](https://www.nfpa.org/codes-and-standards/nfpa-704-standard-development/704) | Identification of the Hazards of Materials for Emergency Response | NFPA | global | mixed | document | C | ok |  |
| [NORSOK S-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Technical safety | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK S-002](https://standard.no/en/sectors/petroleum/norsok-standards/) | Working environment | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK C-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Living quarters area | NORSOK | NO | mixed | catalogue | C | ok |  |

## Reactive hazards, flammable liquids and hazardous materials storage

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [CCPS Reactivity Essential Practices](https://www.aiche.org/ccps/publications) | Essential Practices for Managing Chemical Reactivity Hazards | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Reactive Evaluation](https://www.aiche.org/ccps/publications) | Guidelines for Chemical Reactivity Evaluation and Application to Process Design | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Safe Storage Reactive](https://www.aiche.org/ccps/publications) | Guidelines for Safe Storage and Handling of Reactive Materials | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Batch Reactions](https://www.aiche.org/ccps/publications) | Guidelines for Process Safety in Batch Reaction Systems | CCPS | global | paid | catalogue | C | robots |  |
| [Stoessel, Thermal Safety of Chemical Processes](https://www.icheme.org/) | Thermal Safety of Chemical Processes: Risk Assessment and Process Design (F. Stoessel) | Wiley | global | paid | catalogue | C | ok |  |
| [Barton and Rogers](https://www.icheme.org/) | Chemical Reaction Hazards: A Guide to Safety (IChemE) | Wiley | global | paid | catalogue | C | ok |  |
| [Urben, Bretherick](https://www.icheme.org/) | Bretherick's Handbook of Reactive Chemical Hazards (Elsevier) | Wiley | global | paid | catalogue | C | ok |  |
| [NFPA 400](https://www.nfpa.org/codes-and-standards/nfpa-400-standard-development/400) | Hazardous Materials Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 30](https://www.nfpa.org/codes-and-standards/nfpa-30-standard-development/30) | Flammable and Combustible Liquids Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 30B](https://www.nfpa.org/codes-and-standards/nfpa-30b-standard-development/30b) | Manufacture and Storage of Aerosol Products | NFPA | global | mixed | document | C | ok |  |
| [NFPA 33](https://www.nfpa.org/codes-and-standards/nfpa-33-standard-development/33) | Spray Application Using Flammable or Combustible Materials | NFPA | global | mixed | document | C | ok |  |
| [NFPA 34](https://www.nfpa.org/codes-and-standards/nfpa-34-standard-development/34) | Dipping, Coating, and Printing Processes Using Flammable or Combustible Liquids | NFPA | global | mixed | document | C | ok |  |
| [NFPA 35](https://www.nfpa.org/codes-and-standards/nfpa-35-standard-development/35) | Manufacture of Organic Coatings | NFPA | global | mixed | document | C | ok |  |
| [NFPA 36](https://www.nfpa.org/codes-and-standards/nfpa-36-standard-development/36) | Solvent Extraction Plants | NFPA | global | mixed | document | C | ok |  |
| [NFPA 45](https://www.nfpa.org/codes-and-standards/nfpa-45-standard-development/45) | Fire Protection for Laboratories Using Chemicals | NFPA | global | mixed | document | C | ok |  |
| [NFPA 430](https://www.nfpa.org/codes-and-standards/nfpa-430-standard-development/430) | Storage of Liquid and Solid Oxidizers | NFPA | global | mixed | document | C | ok | Incorporated into NFPA 400; legacy reference. |
| [NFPA 432](https://www.nfpa.org/codes-and-standards/nfpa-432-standard-development/432) | Storage of Organic Peroxide Formulations | NFPA | global | mixed | document | C | ok | Incorporated into NFPA 400; legacy reference. |
| [CAMEO Chemicals](https://cameochemicals.noaa.gov/) | Hazardous material datasheets and reactivity compatibility prediction | NOAA / EPA | global | free | document | C | ok |  |
| [Chemical Reactivity Worksheet](https://www.aiche.org/ccps/resources/chemical-reactivity-worksheet) | Tool to predict reactive incompatibilities (distributed by CCPS) | NOAA / EPA | global | free | document | C | robots |  |
| [CSB reactive hazard study](https://www.csb.gov/improving-reactive-hazard-management/) | Hazard investigation: improving reactive hazard management | CSB | US | free | document | C | ok |  |

## Substance-specific and energy-transition safety

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [NFPA 2](https://www.nfpa.org/codes-and-standards/nfpa-2-standard-development/2) | Hydrogen Technologies Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 51](https://www.nfpa.org/codes-and-standards/nfpa-51-standard-development/51) | Design and Installation of Oxygen-Fuel Gas Systems for Welding, Cutting, and Allied Processes | NFPA | global | mixed | document | C | ok |  |
| [NFPA 51B](https://www.nfpa.org/codes-and-standards/nfpa-51b-standard-development/51b) | Fire Prevention During Welding, Cutting, and Other Hot Work | NFPA | global | mixed | document | C | ok |  |
| [NFPA 53](https://www.nfpa.org/codes-and-standards/nfpa-53-standard-development/53) | Materials, Equipment, and Systems Used in Oxygen-Enriched Atmospheres | NFPA | global | mixed | document | C | ok |  |
| [NFPA 54](https://www.nfpa.org/codes-and-standards/nfpa-54-standard-development/54) | National Fuel Gas Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 55](https://www.nfpa.org/codes-and-standards/nfpa-55-standard-development/55) | Compressed Gases and Cryogenic Fluids Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 56](https://www.nfpa.org/codes-and-standards/nfpa-56-standard-development/56) | Fire and Explosion Prevention During Cleaning and Purging of Flammable Gas Piping Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 58](https://www.nfpa.org/codes-and-standards/nfpa-58-standard-development/58) | Liquefied Petroleum Gas Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 59](https://www.nfpa.org/codes-and-standards/nfpa-59-standard-development/59) | Utility LP-Gas Plant Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 59A](https://www.nfpa.org/codes-and-standards/nfpa-59a-standard-development/59a) | Production, Storage, and Handling of Liquefied Natural Gas (LNG) | NFPA | global | mixed | document | C | ok |  |
| [NFPA 52](https://www.nfpa.org/codes-and-standards/nfpa-52-standard-development/52) | Vehicular Natural Gas Fuel Systems Code | NFPA | global | mixed | document | C | ok |  |
| [NFPA 37](https://www.nfpa.org/codes-and-standards/nfpa-37-standard-development/37) | Installation and Use of Stationary Combustion Engines and Gas Turbines | NFPA | global | mixed | document | C | ok |  |
| [NFPA 820](https://www.nfpa.org/codes-and-standards/nfpa-820-standard-development/820) | Fire Protection in Wastewater Treatment and Collection Facilities | NFPA | global | mixed | document | C | ok |  |
| [NFPA 855](https://www.nfpa.org/codes-and-standards/nfpa-855-standard-development/855) | Installation of Stationary Energy Storage Systems | NFPA | global | mixed | document | C | ok |  |
| [NFPA 850](https://www.nfpa.org/codes-and-standards/nfpa-850-standard-development/850) | Fire Protection for Electric Generating Plants and High Voltage Direct Current Converter Stations | NFPA | global | mixed | document | C | ok |  |
| [NFPA 75](https://www.nfpa.org/codes-and-standards/nfpa-75-standard-development/75) | Fire Protection of Information Technology Equipment | NFPA | global | mixed | document | C | ok |  |
| [NFPA 76](https://www.nfpa.org/codes-and-standards/nfpa-76-standard-development/76) | Fire Protection of Telecommunications Facilities | NFPA | global | mixed | document | C | ok |  |
| [CGA G-4](https://portal.cganet.com/Publication/index.aspx) | Oxygen | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-4.4](https://portal.cganet.com/Publication/index.aspx) | Oxygen pipeline and piping systems | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-5](https://portal.cganet.com/Publication/index.aspx) | Hydrogen | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-5.4](https://portal.cganet.com/Publication/index.aspx) | Standard for hydrogen piping systems at user locations | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-2](https://portal.cganet.com/Publication/index.aspx) | Anhydrous ammonia | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-6](https://portal.cganet.com/Publication/index.aspx) | Carbon dioxide | CGA | US | mixed | catalogue | C | ok |  |
| [CGA P-1](https://portal.cganet.com/Publication/index.aspx) | Safe handling of compressed gases in containers | CGA | US | mixed | catalogue | C | ok |  |
| [CGA S-1.1](https://portal.cganet.com/Publication/index.aspx) | Pressure relief device standards: cylinders for compressed gases | CGA | US | mixed | catalogue | C | ok |  |
| [CGA S-1.2](https://portal.cganet.com/Publication/index.aspx) | Pressure relief device standards: portable containers | CGA | US | mixed | catalogue | C | ok |  |
| [CGA S-1.3](https://portal.cganet.com/Publication/index.aspx) | Pressure relief device standards: stationary storage containers | CGA | US | mixed | catalogue | C | ok |  |
| [CGA G-4.1](https://portal.cganet.com/Publication/index.aspx) | Cleaning of equipment for oxygen service | CGA | US | mixed | catalogue | C | ok |  |
| [EIGA Doc 13](https://www.eiga.eu/publications/) | Oxygen pipeline and piping systems | EIGA | EU | free | catalogue | C | ok |  |
| [EIGA Doc 04](https://www.eiga.eu/publications/) | Fire hazards of oxygen and oxygen enriched atmospheres | EIGA | EU | free | catalogue | C | ok |  |
| [EIGA Doc 121](https://www.eiga.eu/publications/) | Hydrogen pipeline systems | EIGA | EU | free | catalogue | C | ok |  |
| [EIGA Doc 33](https://www.eiga.eu/publications/) | Cleaning of equipment for oxygen service | EIGA | EU | free | catalogue | C | ok |  |
| [Chlorine Institute pamphlets](https://www.chlorineinstitute.org/) | Chlorine safety, piping, materials, transport and emergency pamphlets (e.g. Pamphlet 1 Chlorine Basics, Pamphlet 6 piping systems) | Chlorine Institute | US | mixed | catalogue | C | ok |  |
| [IIAR 2](https://www.iiar.org/) | Safe design of closed-circuit ammonia refrigeration systems | ANSI/IIAR | US | mixed | catalogue | C | ok |  |
| [IIAR 6](https://www.iiar.org/) | Inspection, testing and maintenance of closed-circuit ammonia refrigeration systems | ANSI/IIAR | US | mixed | catalogue | C | ok |  |
| [IIAR 9](https://www.iiar.org/) | Minimum system safety requirements for existing ammonia refrigeration systems | ANSI/IIAR | US | mixed | catalogue | C | ok |  |
| [ASHRAE 15](https://www.ashrae.org/technical-resources/standards-and-guidelines) | Safety standard for refrigeration systems | ASHRAE | global | mixed | catalogue | C | robots |  |
| [ASHRAE 34](https://www.ashrae.org/technical-resources/standards-and-guidelines) | Designation and safety classification of refrigerants | ASHRAE | global | mixed | catalogue | C | robots |  |
| [ISO/TR 15916](https://www.iso.org/search.html?q=ISO/TR%2015916) | Basic considerations for the safety of hydrogen systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 19880-1](https://www.iso.org/search.html?q=ISO%2019880-1) | Gaseous hydrogen fuelling stations: general requirements | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 22734](https://www.iso.org/search.html?q=ISO%2022734) | Hydrogen generators using water electrolysis | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 19881](https://www.iso.org/search.html?q=ISO%2019881) | Gaseous hydrogen land vehicle fuel containers | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 16111](https://www.iso.org/search.html?q=ISO%2016111) | Transportable gas storage devices: hydrogen absorbed in reversible metal hydride | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 19884 (series)](https://www.iso.org/search.html?q=ISO%2019884%20%28series%29) | Gaseous hydrogen stationary storage | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 14687](https://www.iso.org/search.html?q=ISO%2014687) | Hydrogen fuel quality | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 26142](https://www.iso.org/search.html?q=ISO%2026142) | Hydrogen detection apparatus: stationary applications | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 16924](https://www.iso.org/search.html?q=ISO%2016924) | Natural gas fuelling stations: LNG stations | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 20519](https://www.iso.org/search.html?q=ISO%2020519) | Ships and marine technology: bunkering of LNG fuelled vessels | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 20088-1](https://www.iso.org/search.html?q=ISO%2020088-1) | Resistance to cryogenic spillage: liquid phase | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 24252](https://www.iso.org/search.html?q=ISO%2024252) | Biogas systems: non-household and non-gasification | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 27913](https://www.iso.org/search.html?q=ISO%2027913) | Carbon dioxide capture, transportation and geological storage: pipeline transportation systems | ISO | global | paid | catalogue | C | blocked |  |
| [DNV-RP-F104](https://www.dnv.com/rules-standards/) | Design and operation of carbon dioxide pipelines | DNV | global | free | catalogue | C | ok |  |
| [DNV-ST-F101](https://www.dnv.com/rules-standards/) | Submarine pipeline systems | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-A203](https://www.dnv.com/rules-standards/) | Technology qualification | DNV | global | free | catalogue | C | ok |  |
| [EI CO2 pipeline hazard guidance](https://www.energyinst.org/technical/publications) | Hazard analysis for offshore carbon capture platforms and offshore pipelines | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI Model Code of Safe Practice Part 9](https://www.energyinst.org/technical/publications) | Large bulk pressure storage and refrigerated LPG | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [EI Battery storage guidance](https://www.energyinst.org/technical/publications) | Battery storage guidance notes | Energy Institute | global | mixed | catalogue | C | blocked |  |
| [H2Tools](https://h2tools.org/) | Hydrogen safety best practices and lessons learned portal (PNNL) | US sources | US | mixed | document | C | robots |  |
| [NASA NSS 1740.16](https://ntrs.nasa.gov/citations/19970033338) ([PDF](https://ntrs.nasa.gov/api/citations/19970033338/downloads/19970033338.pdf)) | Safety Standard for Hydrogen and Hydrogen Systems | US sources | US | mixed | document | C | error | Check whether a later NASA standard supersedes it for your use. |
| [AIAA G-095](https://arc.aiaa.org/doi/book/10.2514/4.105197) | Guide to Safety of Hydrogen and Hydrogen Systems | US sources | US | mixed | document | C | blocked | Paid. |
| [UL 9540A](https://www.ul.com/services/ul-9540a-test-method) | Test method for evaluating thermal runaway fire propagation in battery energy storage systems | US sources | US | mixed | document | C | ok | Paid standard; the page is a description. |
| [SIGTTO publications](https://www.sigtto.org/) | Liquefied gas terminal and ship safety publications | SIGTTO | global | mixed | catalogue | C | ok |  |
| [ISGOTT](https://www.ocimf.org/) | International Safety Guide for Oil Tankers and Terminals | OCIMF / ICS / IAPH | global | paid | catalogue | C | ok |  |
| [IGC Code](https://www.imo.org/) | International Code for the Construction and Equipment of Ships Carrying Liquefied Gases in Bulk | IMO | global | paid | catalogue | C | ok |  |
| [IGF Code](https://www.imo.org/) | International Code of Safety for Ships using Gases or other Low-flashpoint Fuels | IMO | global | paid | catalogue | C | ok |  |
| [IBC Code](https://www.imo.org/) | International Code for ships carrying dangerous chemicals in bulk | IMO | global | paid | catalogue | C | ok |  |
| [IMDG Code](https://www.imo.org/) | International Maritime Dangerous Goods Code | IMO | global | paid | catalogue | C | ok |  |

## Pipelines and offshore

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [API STD 1160](https://publications.api.org/) | Managing system integrity for hazardous liquid pipelines | API | global | paid | catalogue | C | robots |  |
| [API RP 1162](https://publications.api.org/) | Public awareness programs for pipeline operators | API | global | paid | catalogue | C | robots |  |
| [API RP 1165](https://publications.api.org/) | Pipeline SCADA displays | API | global | paid | catalogue | C | robots |  |
| [API RP 1168](https://publications.api.org/) | Pipeline control room management | API | global | paid | catalogue | C | robots |  |
| [API RP 1175](https://publications.api.org/) | Pipeline leak detection program management | API | global | paid | catalogue | C | robots |  |
| [API STD 1163](https://publications.api.org/) | In-line inspection systems qualification | API | global | paid | catalogue | C | robots |  |
| [API RP 1102](https://publications.api.org/) | Steel pipelines crossing railroads and highways | API | global | paid | catalogue | C | robots |  |
| [API RP 1110](https://publications.api.org/) | Pressure testing of steel pipelines | API | global | paid | catalogue | C | robots |  |
| [API RP 14J](https://publications.api.org/) | Design and hazards analysis for offshore production facilities | API | global | paid | catalogue | C | robots |  |
| [API RP 2A-WSD](https://publications.api.org/) | Planning, designing and constructing fixed offshore platforms: working stress design | API | global | paid | catalogue | C | robots |  |
| [API RP 2FB](https://publications.api.org/) | Design of offshore facilities against fire and blast loading | API | global | paid | catalogue | C | robots |  |
| [API STD 53](https://publications.api.org/) | Well control equipment systems for drilling wells | API | global | paid | catalogue | C | robots |  |
| [ISO 13623](https://www.iso.org/search.html?q=ISO%2013623) | Pipeline transportation systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 10418](https://www.iso.org/search.html?q=ISO%2010418) | Offshore production installations: process safety systems | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 19900 (series)](https://www.iso.org/search.html?q=ISO%2019900%20%28series%29) | Offshore structures | ISO | global | paid | catalogue | C | blocked |  |
| [ISO 16708](https://www.iso.org/search.html?q=ISO%2016708) | Pipeline transportation systems: reliability-based limit state methods | ISO | global | paid | catalogue | C | blocked |  |
| [DNV-OS-A101](https://www.dnv.com/rules-standards/) | Safety principles and arrangements | DNV | global | free | catalogue | C | ok |  |
| [DNV-OS-D101](https://www.dnv.com/rules-standards/) | Marine and machinery systems and equipment | DNV | global | free | catalogue | C | ok |  |
| [DNV-OS-D202](https://www.dnv.com/rules-standards/) | Automation, safety and telecommunication systems | DNV | global | free | catalogue | C | ok |  |
| [DNV-OS-D301](https://www.dnv.com/rules-standards/) | Fire protection | DNV | global | free | catalogue | C | ok |  |
| [DNV-OS-E201](https://www.dnv.com/rules-standards/) | Oil and gas processing systems | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-C204](https://www.dnv.com/rules-standards/) | Design against accidental loads | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-F107](https://www.dnv.com/rules-standards/) | Risk assessment of pipeline protection | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-F116](https://www.dnv.com/rules-standards/) | Integrity management of submarine pipeline systems | DNV | global | free | catalogue | C | ok |  |
| [DNV-RP-F113](https://www.dnv.com/rules-standards/) | Pipeline subsea repair | DNV | global | free | catalogue | C | ok |  |
| [NORSOK P-002](https://standard.no/en/sectors/petroleum/norsok-standards/) | Process system design | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK P-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Process design | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK L-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Piping and valves | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK N-001](https://standard.no/en/sectors/petroleum/norsok-standards/) | Integrity of offshore structures | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK N-004](https://standard.no/en/sectors/petroleum/norsok-standards/) | Design of steel structures | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK I-002](https://standard.no/en/sectors/petroleum/norsok-standards/) | Industrial automation and control systems | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK D-010](https://standard.no/en/sectors/petroleum/norsok-standards/) | Well integrity in drilling and well operations | NORSOK | NO | mixed | catalogue | C | ok |  |
| [NORSOK R-002](https://standard.no/en/sectors/petroleum/norsok-standards/) | Lifting equipment | NORSOK | NO | mixed | catalogue | C | ok |  |
| [ABS rules and guides](https://ww2.eagle.org/en/rules-and-resources/rules-and-guides.html) | ABS rules, guides and guidance notes (many free) | ABS / LR / BV | global | mixed | document | C | ok |  |
| [Lloyd's Register rules](https://www.lr.org/) | Classification rules and guidance | ABS / LR / BV | global | mixed | document | C | ok |  |
| [Bureau Veritas marine rules](https://marine-offshore.bureauveritas.com/) | Rules and guidance notes | ABS / LR / BV | global | mixed | document | C | ok |  |

## Safe work and operations

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [API STD 2015](https://publications.api.org/) | Requirements for safe entry and cleaning of petroleum storage tanks | API | global | paid | catalogue | C | robots |  |
| [API RP 2016](https://publications.api.org/) | Guidelines and procedures for entering and cleaning petroleum storage tanks | API | global | paid | catalogue | C | robots |  |
| [API RP 2027](https://publications.api.org/) | Ignition hazards and safe work practices for abrasive blasting of atmospheric storage tanks | API | global | paid | catalogue | C | robots |  |
| [API RP 2026](https://publications.api.org/) | Safe access and egress involving floating roofs of storage tanks in petroleum service | API | global | paid | catalogue | C | robots |  |
| [API RP 2217A](https://publications.api.org/) | Safe work in inert confined spaces in the petroleum and petrochemical industries | API | global | paid | catalogue | C | robots |  |
| [API RP 2219](https://publications.api.org/) | Safe operation of vacuum trucks in petroleum service | API | global | paid | catalogue | C | robots |  |
| [CCPS Safe Work Practices](https://www.aiche.org/ccps/publications) | Guidelines for Safe Work Practices and non-routine operations | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Startup and Shutdown](https://www.aiche.org/ccps/publications) | Guidelines for Safe Process Operations and Maintenance | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Process Safety Culture](https://www.aiche.org/ccps/publications) | Essential Practices for Creating, Strengthening, and Sustaining Process Safety Culture | CCPS | global | paid | catalogue | C | robots |  |
| [CCPS Transient Operations](https://www.aiche.org/ccps/publications) | Guidelines for process safety during transient operating modes | CCPS | global | paid | catalogue | C | robots |  |
| [NFPA 306](https://www.nfpa.org/codes-and-standards/nfpa-306-standard-development/306) | Control of Gas Hazards on Vessels | NFPA | global | mixed | document | C | ok |  |
| [NFPA 326](https://www.nfpa.org/codes-and-standards/nfpa-326-standard-development/326) | Safeguarding of Tanks and Containers for Entry, Cleaning, or Repair | NFPA | global | mixed | document | C | ok |  |
| [NFPA 329](https://www.nfpa.org/codes-and-standards/nfpa-329-standard-development/329) | Handling Releases of Flammable and Combustible Liquids and Gases | NFPA | global | mixed | document | C | ok |  |
| [NFPA 350](https://www.nfpa.org/codes-and-standards/nfpa-350-standard-development/350) | Safe Confined Space Entry and Work | NFPA | global | mixed | document | C | ok |  |
| [NFPA 470](https://www.nfpa.org/codes-and-standards/nfpa-470-standard-development/470) | Hazardous Materials/Weapons of Mass Destruction Standard for Responders | NFPA | global | mixed | document | C | ok |  |
| [NIOSH Pocket Guide](https://www.cdc.gov/niosh/npg/default.html) | NIOSH Pocket Guide to Chemical Hazards | NIOSH / PHMSA | US | free | document | C | blocked |  |
| [Emergency Response Guidebook](https://www.phmsa.dot.gov/training/hazmat/erg/emergency-response-guidebook-erg) | PHMSA Emergency Response Guidebook (initial isolation and protective action distances) | NIOSH / PHMSA | US | free | document | C | blocked |  |

## Open research reports on fire and release modelling

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [HSE RR1229](https://www.hse.gov.uk/research/assets/docs/rr1229.pdf) | Revised fireball and jet fire models for pipelines | HSE | UK | free | document | C | pdf |  |
| [HSE RR1196](https://www.hse.gov.uk/research/assets/docs/rr1196.pdf) | Radiation calculations for fireball and jet fire models: a literature review | HSE | UK | free | document | C | pdf |  |
| [RIVM 620550005](https://www.rivm.nl/bibliotheek/rapporten/620550005.pdf) | A comparison of jet fire models for horizontal two-phase and liquid releases | RIVM | NL | free | document | C | pdf |  |
| [IChemE Hazards XXI paper 088](https://www.icheme.org/media/9584/xxi-paper-088.pdf) | Two-phase jet releases and droplet dispersion | IChemE | global | free | document | C | pdf |  |

## Modelling tools, chemical property and exposure data

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [ALOHA](https://www.epa.gov/cameo/aloha-software) | Areal Locations of Hazardous Atmospheres dispersion and consequence model | NOAA / EPA | US | free | document | C | ok |  |
| [RMP*Comp](https://www.epa.gov/rmp/rmpcomp) | EPA offsite consequence analysis tool | NOAA / EPA | US | free | document | C | ok |  |
| [EPA OCA guidance](https://www.epa.gov/rmp/rmp-guidance-offsite-consequence-analysis) | Risk Management Program guidance for offsite consequence analysis | NOAA / EPA | US | free | document | C | ok |  |
| [AEGL values](https://www.epa.gov/aegl) | Acute Exposure Guideline Levels for airborne chemicals | NOAA / EPA | US | free | document | C | ok |  |
| [EPA SCRAM](https://www.epa.gov/scram) | Air dispersion modelling downloads (AERMOD and related) | NOAA / EPA | US | free | document | C | ok |  |
| [AIHA ERPG](https://www.aiha.org/) | Emergency Response Planning Guidelines | Exposure limits | global | free | document | C | ok | Mixed access. |
| [DOE PACs](https://pacteels.pnnl.gov/) | Protective Action Criteria for chemicals | Exposure limits | global | free | document | C | error |  |
| [GESTIS substances](https://gestis.dguv.de/) | GESTIS database on hazardous substances | Exposure limits | global | free | document | C | ok |  |
| [ECHA CHEM](https://chem.echa.europa.eu/) | European Chemicals Agency substance information | Exposure limits | global | free | document | C | ok |  |
| [PubChem](https://pubchem.ncbi.nlm.nih.gov/) | Chemical data including safety sections | Exposure limits | global | free | document | C | robots |  |
| [NIOSH IDLH](https://www.cdc.gov/niosh/idlh/default.html) | Immediately Dangerous to Life or Health values | Exposure limits | global | free | document | C | blocked |  |
| [NIST Chemistry WebBook](https://webbook.nist.gov/chemistry/) | Thermophysical and thermochemical data | Properties | global | mixed | document | C | ok |  |
| [DIPPR 801](https://www.aiche.org/dippr) | AIChE evaluated process design data (paid) | Properties | global | mixed | document | C | robots |  |
| [CoolProp](https://coolprop.org/) | Open-source thermophysical property library | Properties | global | mixed | document | C | ok |  |
| [fluids (ChEDL)](https://github.com/CalebBell/fluids) | Open-source fluid dynamics library, including relief sizing | Properties | global | mixed | document | C | ok |  |
| [thermo (ChEDL)](https://github.com/CalebBell/thermo) | Open-source thermodynamics library | Properties | global | mixed | document | C | ok |  |
| [Cantera](https://cantera.org/) | Open-source kinetics and thermodynamics toolkit | Properties | global | mixed | document | C | ok |  |
| [OpenFOAM](https://www.openfoam.com/) | Open-source CFD toolkit | Properties | global | mixed | document | C | ok |  |
| [HyRAM+](https://energy.sandia.gov/programs/sustainable-transportation/hydrogen/hydrogen-safety-codes-and-standards/hyram/) | Hydrogen and alternative fuels risk assessment models (Sandia) | Properties | global | mixed | document | C | ok |  |

## Incident investigations and loss databases

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [CSB investigations](https://www.csb.gov/investigations/) | US Chemical Safety Board investigations and videos | Investigators and databases | global | free | document | C | ok |  |
| [CSB recommendations](https://www.csb.gov/recommendations/) | US Chemical Safety Board recommendations | Investigators and databases | global | free | document | C | ok |  |
| [eMARS](https://emars.jrc.ec.europa.eu/) | EU Major Accident Reporting System | Investigators and databases | global | free | document | C | ok |  |
| [ARIA](https://www.aria.developpement-durable.gouv.fr/the-barpi/the-aria-database/?lang=en) | French accident database (BARPI) | Investigators and databases | global | free | document | C | ok |  |
| [ZEMA](https://www.infosis.uba.de/index.php/en/site/12981/zema/index.html) | German central reporting and evaluation office for major accidents | Investigators and databases | global | free | document | C | ok |  |
| [NTSB investigations](https://www.ntsb.gov/investigations/Pages/Investigations.aspx) | US National Transportation Safety Board, including pipeline accidents | Investigators and databases | global | free | document | C | ok |  |
| [PHMSA incident data](https://www.phmsa.dot.gov/data-and-statistics/pipeline/distribution-transmission-gathering-lng-and-liquid-accident-and-incident-data) | Pipeline incident and accident data | Investigators and databases | global | free | document | C | blocked |  |
| [EPA RMP accident data](https://www.epa.gov/rmp) | Risk Management Plan five-year accident history information | Investigators and databases | global | free | document | C | ok |  |
| [OSHA accident search](https://www.osha.gov/ords/imis/accidentsearch.html) | OSHA fatality and catastrophe investigation summaries | Investigators and databases | global | free | document | C | robots |  |
| [NRC (US) National Response Center](https://nrc.uscg.mil/) | Release reports | Investigators and databases | global | free | document | C | ok |  |
| [JST Failure Knowledge Database](https://www.shippai.org/fkd/en/) | Japanese failure case database | Investigators and databases | global | free | document | C | ok |  |
| [HIAD](https://minerva.jrc.ec.europa.eu/en/shorturl/capri/hiadpt) | European Hydrogen Incidents and Accidents Database | Investigators and databases | global | free | document | C | ok |  |
| [HSE offshore releases](https://www.hse.gov.uk/offshore/statistics.htm) | Offshore hydrocarbon releases statistics | Investigators and databases | global | free | document | C | ok |  |
| [Buncefield investigation](https://www.hse.gov.uk/comah/buncefield/) | Buncefield Major Incident Investigation Board material (HSE) | Investigators and databases | global | free | document | C | ok |  |
| [Piper Alpha / Cullen](https://www.hse.gov.uk/offshore/piper-alpha-disaster-public-inquiry.htm) | Public Inquiry into the Piper Alpha disaster (HSE copy) | Investigators and databases | global | free | document | C | ok |  |
| [IChemE Loss Prevention Bulletin](https://www.icheme.org/knowledge/loss-prevention-bulletin/) | Incident case studies bulletin | IChemE | global | mixed | catalogue | C | ok |  |
| [CCPS Process Safety Beacon](https://www.aiche.org/ccps/resources/process-safety-beacon) | Monthly one-page process safety lessons | CCPS | global | mixed | catalogue | C | robots |  |
| [CCPS Incidents That Define Process Safety](https://www.aiche.org/ccps/resources/process-safety-beacon) | Case histories of defining incidents | CCPS | global | mixed | catalogue | C | robots |  |
| [Marsh 100 Largest Losses](https://www.marsh.com/) | Largest property damage losses in the hydrocarbon industry | Marsh | global | free-registration | catalogue | C | ok |  |

## India: standards and agencies

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [OISD standards list](https://www.oisd.gov.in/) | Oil Industry Safety Directorate standards, guidelines and recommended practices | OISD | IN | mixed | catalogue | C | ok | See process_safety/data/oisd_standards.json for the numbered list already in this toolkit. |
| [IS 2825](https://standards.bis.gov.in/) | Code for unfired pressure vessels | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 15656](https://standards.bis.gov.in/) | Hazard identification and risk analysis: code of practice | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 14489](https://standards.bis.gov.in/) | Code of practice on occupational safety and health audit | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 18001](https://standards.bis.gov.in/) | Occupational health and safety management systems | BIS | IN | mixed | catalogue | C | ok | Superseded by the IS adoption of ISO 45001; confirm status. |
| [IS 5571](https://standards.bis.gov.in/) | Guide for selection of electrical equipment for hazardous areas | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 5572](https://standards.bis.gov.in/) | Classification of hazardous areas (other than mines) having flammable gases and vapours for electrical installation | BIS | IN | mixed | catalogue | C | ok |  |
| [IS/IEC 60079 (series)](https://standards.bis.gov.in/) | Explosive atmospheres (Indian adoptions) | BIS | IN | mixed | catalogue | C | ok |  |
| [IS/IEC 61511](https://standards.bis.gov.in/) | Functional safety for the process industry (Indian adoption) | BIS | IN | mixed | catalogue | C | ok |  |
| [IS/IEC 62305](https://standards.bis.gov.in/) | Protection against lightning (Indian adoption) | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 3043](https://standards.bis.gov.in/) | Code of practice for earthing | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 732](https://standards.bis.gov.in/) | Code of practice for electrical wiring installations | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 2189](https://standards.bis.gov.in/) | Selection, installation and maintenance of automatic fire detection and alarm systems | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 2190](https://standards.bis.gov.in/) | Selection, installation and maintenance of first-aid fire extinguishers | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 15105](https://standards.bis.gov.in/) | Design and installation of fixed automatic sprinkler fire extinguishing systems | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 15325](https://standards.bis.gov.in/) | Design and installation of fixed automatic high and medium velocity water spray system | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 13039](https://standards.bis.gov.in/) | Code of practice for provision and maintenance of external hydrant system | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 1239](https://standards.bis.gov.in/) | Steel tubes, tubulars and other wrought steel fittings | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 3589](https://standards.bis.gov.in/) | Steel pipes for water and sewage | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 2062](https://standards.bis.gov.in/) | Hot rolled medium and high tensile structural steel | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 2002](https://standards.bis.gov.in/) | Steel plates for pressure vessels for intermediate and high temperature service | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 2041](https://standards.bis.gov.in/) | Steel plates for pressure vessels used at moderate and low temperature | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 803](https://standards.bis.gov.in/) | Code of practice for design, fabrication and erection of vertical mild steel cylindrical welded oil storage tanks | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 4503](https://standards.bis.gov.in/) | Shell and tube type heat exchangers | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 875](https://standards.bis.gov.in/) | Code of practice for design loads for buildings and structures | BIS | IN | mixed | catalogue | C | ok |  |
| [IS 1893](https://standards.bis.gov.in/) | Criteria for earthquake resistant design of structures | BIS | IN | mixed | catalogue | C | ok |  |
| [SP 30](https://standards.bis.gov.in/) | National Electrical Code of India | BIS | IN | mixed | catalogue | C | ok |  |
| [SP 7](https://standards.bis.gov.in/) | National Building Code of India (Part 4: fire and life safety) | BIS | IN | mixed | catalogue | C | ok |  |
| [DGFASLI](https://dgfasli.gov.in/) | Directorate General Factory Advice Service and Labour Institutes | DGFASLI | IN | free | catalogue | C | ok |  |
| [NDMA chemical disaster guidelines](https://ndma.gov.in/) | National Disaster Management Guidelines: Chemical Disasters (Industrial) | NDMA | IN | free | catalogue | C | ok |  |
| [CPCB standards and guidelines](https://cpcb.nic.in/) | Environmental standards, hazardous waste rules and industry guidelines | CPCB | IN | free | catalogue | C | error |  |

## Books, handbooks and learning

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [Lees' Loss Prevention](https://shop.elsevier.com/) | Lees' Loss Prevention in the Process Industries (S. Mannan, ed.) | Elsevier | global | paid | catalogue | C | ok |  |
| [Kletz, What Went Wrong?](https://shop.elsevier.com/) | What Went Wrong? Case Histories of Process Plant Disasters (T. Kletz, P. Amyotte) | Elsevier | global | paid | catalogue | C | ok |  |
| [Kletz and Amyotte, Inherently Safer](https://shop.elsevier.com/) | Process Plants: A Handbook for Inherently Safer Design | Elsevier | global | paid | catalogue | C | ok |  |
| [Sanders, Chemical Process Safety Case Histories](https://shop.elsevier.com/) | Chemical Process Safety: Learning from Case Histories (R. Sanders) | Elsevier | global | paid | catalogue | C | ok |  |
| [Casal, Effects and Consequences](https://shop.elsevier.com/) | Evaluation of the Effects and Consequences of Major Accidents in Industrial Plants (J. Casal) | Elsevier | global | paid | catalogue | C | ok |  |
| [Smith and Simpson](https://shop.elsevier.com/) | Safety Critical Systems Handbook | Elsevier | global | paid | catalogue | C | ok |  |
| [Towler and Sinnott](https://shop.elsevier.com/) | Chemical Engineering Design | Elsevier | global | paid | catalogue | C | ok |  |
| [Ludwig / Coker](https://shop.elsevier.com/) | Ludwig's Applied Process Design for Chemical and Petrochemical Plants | Elsevier | global | paid | catalogue | C | ok |  |
| [Crowl and Louvar](https://www.pearson.com/) | Chemical Process Safety: Fundamentals with Applications | Pearson | global | paid | catalogue | C | ok |  |
| [Perry's Handbook](https://www.mheducation.com/) | Perry's Chemical Engineers' Handbook (process safety section) | McGraw-Hill | global | paid | catalogue | C | ok |  |
| [Crane TP-410](https://www.flowoffluids.com/) | Flow of Fluids Through Valves, Fittings and Pipe | Crane | global | paid | catalogue | C | ok |  |
| [GPSA Engineering Data Book](https://www.gpamidstream.org/) | Gas Processors Suppliers Association Engineering Data Book | GPSA | global | paid | catalogue | C | blocked |  |
| [SFPE Handbook](https://www.sfpe.org/) | SFPE Handbook of Fire Protection Engineering | SFPE | global | paid | catalogue | C | ok |  |
| [NPTEL](https://nptel.ac.in/) | Free engineering courses, including chemical process safety | Open learning | global | free | document | C | ok |  |
| [SAChE](https://www.aiche.org/ccps/education/sache) | AIChE Safety and Chemical Engineering Education resources | Open learning | global | free | document | C | robots |  |
| [MIT OpenCourseWare](https://ocw.mit.edu/) | Free course materials (search process safety) | Open learning | global | free | document | C | ok |  |

## Journals, open-access repositories and research centres

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [Journal of Loss Prevention in the Process Industries](https://www.sciencedirect.com/journal/journal-of-loss-prevention-in-the-process-industries) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Process Safety and Environmental Protection](https://www.sciencedirect.com/journal/process-safety-and-environmental-protection) | Peer-reviewed journal (IChemE) | Journals | global | mixed | document | C | blocked |  |
| [Process Safety Progress](https://aiche.onlinelibrary.wiley.com/journal/15475913) | Peer-reviewed journal (AIChE) | Journals | global | mixed | document | C | blocked |  |
| [Journal of Hazardous Materials](https://www.sciencedirect.com/journal/journal-of-hazardous-materials) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Fire Safety Journal](https://www.sciencedirect.com/journal/fire-safety-journal) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Reliability Engineering and System Safety](https://www.sciencedirect.com/journal/reliability-engineering-and-system-safety) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Safety Science](https://www.sciencedirect.com/journal/safety-science) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Combustion and Flame](https://www.sciencedirect.com/journal/combustion-and-flame) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [International Journal of Hydrogen Energy](https://www.sciencedirect.com/journal/international-journal-of-hydrogen-energy) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Engineering Failure Analysis](https://www.sciencedirect.com/journal/engineering-failure-analysis) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Corrosion Science](https://www.sciencedirect.com/journal/corrosion-science) | Peer-reviewed journal | Journals | global | mixed | document | C | blocked |  |
| [Journal of Chemical Health and Safety](https://pubs.acs.org/journal/jchas) | ACS journal | Journals | global | mixed | document | C | blocked |  |
| [Chemical Engineering Transactions](https://www.cetjournal.it/) | Open-access proceedings (AIDIC), including loss prevention symposia | Open access | global | free | document | C | ok |  |
| [Safety (MDPI)](https://www.mdpi.com/journal/safety) | Open-access journal | Open access | global | free | document | C | blocked |  |
| [Processes (MDPI)](https://www.mdpi.com/journal/processes) | Open-access journal | Open access | global | free | document | C | blocked |  |
| [IChemE Hazards papers](https://www.icheme.org/knowledge/safety-centre/resources/) | IChemE Hazards symposium paper archive | Open access | global | free | document | C | ok |  |
| [CORE](https://core.ac.uk/) | Aggregator of open-access research papers | Open access | global | free | document | C | ok |  |
| [OpenAlex](https://openalex.org/) | Open index of scholarly works with open-access locations | Open access | global | free | document | C | ok |  |
| [OSTI.gov](https://www.osti.gov/) | US Department of Energy research reports | Open access | global | free | document | C | ok |  |
| [NTRS](https://ntrs.nasa.gov/) | NASA Technical Reports Server | Open access | global | free | document | C | error |  |
| [Semantic Scholar](https://www.semanticscholar.org/) | Literature search | Open access | global | free | document | C | ok |  |
| [CCPS](https://www.aiche.org/ccps) | Center for Chemical Process Safety | Research centres and associations | global | mixed | document | C | robots |  |
| [Mary Kay O'Connor Process Safety Center](https://psc.tamu.edu/) | Research centre at Texas A&M | Research centres and associations | global | mixed | document | C | ok |  |
| [IChemE Safety Centre](https://www.icheme.org/knowledge/safety-centre/) | Industry safety centre | Research centres and associations | global | mixed | document | C | ok |  |
| [European Process Safety Centre](https://epsc.be/) | EPSC publications and working groups | Research centres and associations | global | mixed | document | C | ok |  |
| [EFCE Loss Prevention](https://efce.info/) | European Federation of Chemical Engineering | Research centres and associations | global | mixed | document | C | robots |  |
| [HSE Science and Research Centre](https://www.hsl.gov.uk/) | UK research and testing | Research centres and associations | global | mixed | document | C | ok |  |
| [INERIS](https://www.ineris.fr/en) | French industrial environment and risk institute | Research centres and associations | global | mixed | document | C | ok |  |
| [BAM](https://www.bam.de/) | German Federal Institute for Materials Research and Testing | Research centres and associations | global | mixed | document | C | ok |  |
| [TNO](https://www.tno.nl/en/) | Netherlands research organisation | Research centres and associations | global | mixed | document | C | ok |  |
| [Gexcon knowledge base](https://www.gexcon.com/) | Consequence modelling and explosion research (vendor) | Research centres and associations | global | mixed | document | C | ok |  |

## Digital Refining articles on safety and design (unread; found by search)

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [DR 1000394](https://www.digitalrefining.com/article/1000394/optimising-safety-relief-and-flare-systems) | Optimising safety relief and flare systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002334](https://www.digitalrefining.com/article/1002334/sizing-relief-valves-for-real-gas-or-vapour) | Sizing relief valves for real gas or vapour | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001088](https://www.digitalrefining.com/article/1001088/applying-relief-load-calculation-methods) | Applying relief load calculation methods | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002809](https://www.digitalrefining.com/article/1002809/stationing-an-operator-at-a-pressure-safety-valve-bypass) | Stationing an operator at a pressure safety valve bypass | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000961](https://www.digitalrefining.com/article/1000961/accurate-prediction-of-tower-relief) | Accurate prediction of tower relief | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002247](https://www.digitalrefining.com/article/1002247/pressure-relief-with-rupture-discs) | Pressure relief with rupture discs | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001532](https://www.digitalrefining.com/article/1001532/dynamic-column-simulation-delivers-reduced-relief-load) | Dynamic column simulation delivers reduced relief load | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002252](https://www.digitalrefining.com/article/1002252/dynamic-simulation-to-estimate-tower-relief) | Dynamic simulation to estimate tower relief | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003294](https://www.digitalrefining.com/article/1003294/when-dynamic-relief-calculations-give-unexpected-results) | When dynamic relief calculations give unexpected results | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000487](https://www.digitalrefining.com/article/1000487/calculating-column-relief-loads) | Calculating column relief loads | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000458](https://www.digitalrefining.com/article/1000458/are-there-alternatives-to-an-expensive-overhaul-of-a-bottlenecked-flare-system) | Are there alternatives to an expensive overhaul of a bottlenecked flare system? | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001215](https://www.digitalrefining.com/article/1001215/tube-rupture-in-a-natural-gas-heater) | Tube rupture in a natural gas heater | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002294](https://www.digitalrefining.com/article/1002294/protecting-against-high-pressure-rupture-ti) | Protecting against high pressure rupture (TIA) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003013](https://www.digitalrefining.com/article/1003013/assessing-lng-feed-gas-depressurisation) | Assessing LNG feed gas depressurisation | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000455](https://www.digitalrefining.com/article/1000455/achieving-excellence-in-process-safety-management) | Achieving excellence in process safety management | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003592](https://www.digitalrefining.com/article/1003592/identifying-patterns-in-recent-refinery-incidents) | Identifying patterns in recent refinery incidents | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003519](https://www.digitalrefining.com/article/1003519/procedure-management-in-refinery-operations) | Procedure management in refinery operations | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001225](https://www.digitalrefining.com/article/1001225/enabling-the-refinery-of-the-future-safety-first) | Enabling the refinery of the future: safety first | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003135](https://www.digitalrefining.com/article/1003135/fundamentals-of-refinery-safety) | Fundamentals of refinery safety | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003336](https://www.digitalrefining.com/article/1003336/avoid-utility-disruptions-in-refinery-operations) | Avoid utility disruptions in refinery operations | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000949](https://www.digitalrefining.com/article/1000949/what-does-sil-and-functional-safety-mean-to-operators-of-rotating-equipment) | What does SIL and functional safety mean to operators of rotating equipment? | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001303](https://www.digitalrefining.com/article/1001303/sil-and-functional-safety-in-rotating-equipment) | SIL and functional safety in rotating equipment | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001238](https://www.digitalrefining.com/article/1001238/safety-system-separation-examination-of-three-types-of-machinery-protection-systems) | Safety system separation: examination of three types of machinery protection systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002560](https://www.digitalrefining.com/article/1002560/process-safety-time-for-fired-heaters) | Process safety time for fired heaters | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000749](https://www.digitalrefining.com/article/1000749/hazardous-or-harmless-machinery-has-not-changed-but-demands-have) | Hazardous or harmless? Machinery has not changed, but demands have | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003301](https://www.digitalrefining.com/article/1003301/operator-performance-advances-enable-safer-operations) | Operator performance advances enable safer operations | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000936](https://www.digitalrefining.com/article/1000936/high-fidelity-operator-training-simulators) | High-fidelity operator training simulators | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001190](https://www.digitalrefining.com/article/1001190/cyber-security-in-the-refining-world) | Cyber security in the refining world | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000852](https://www.digitalrefining.com/article/1000852/role-of-fired-heater-safety-systems) | Role of fired heater safety systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000366](https://www.digitalrefining.com/article/1000366/useful-tips-for-fired-heater-optimisation) | Useful tips for fired heater optimisation | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003209](https://www.digitalrefining.com/article/1003209/fired-heater-design-a-multidisciplinary-engineering-effort) | Fired heater design: a multidisciplinary engineering effort | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002511](https://www.digitalrefining.com/article/1002511/the-hazards-of-fired-heater-flooding) | The hazards of fired heater flooding | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001457](https://www.digitalrefining.com/article/1001457/retrofitting-crude-furnace-burners) | Retrofitting crude furnace burners | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000131](https://www.digitalrefining.com/article/1000131/avoiding-fcc-regenerator-upsets) | Avoiding FCC regenerator upsets | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002948](https://www.digitalrefining.com/article/1002948/proactively-preventing-reactor-runaway-events) | Proactively preventing reactor runaway events | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002911](https://www.digitalrefining.com/article/1002911/reactor-runaways-automatic-or-manual-depressuring) | Reactor runaways: automatic or manual depressuring? | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000173](https://www.digitalrefining.com/article/1000173/operational-life-improvements-in-modern-hydroprocessing-reactors) | Operational life improvements in modern hydroprocessing reactors | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000862](https://www.digitalrefining.com/article/1000862/reactor-effluent-air-cooler-safety-through-design) | Reactor effluent air cooler safety through design | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002512](https://www.digitalrefining.com/article/1002512/mitigating-corrosion-with-a-digital-twin) | Mitigating corrosion with a digital twin | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003119](https://www.digitalrefining.com/article/1003119/navigating-corrosion-challenges-in-column-overhead-systems) | Navigating corrosion challenges in column overhead systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003344](https://www.digitalrefining.com/article/1003344/corrosion-control-in-refinery-distillation) | Corrosion control in refinery distillation | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001756](https://www.digitalrefining.com/article/1001756/low-cost-revamp-to-process-heavy-sour-crudes) | Low cost revamp to process heavy sour crudes | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003262](https://www.digitalrefining.com/article/1003262/synergistic-multifunctional-corrosion-inhibitors-for-high-acid-crudes) | Synergistic multifunctional corrosion inhibitors for high-acid crudes | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002331](https://www.digitalrefining.com/article/1002331/development-of-a-naphthenic-acid-corrosion-model) | Development of a naphthenic acid corrosion model | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001550](https://www.digitalrefining.com/article/1001550/the-corrosion-fouling-cycle-in-amine-systems) | The corrosion-fouling cycle in amine systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000902](https://www.digitalrefining.com/article/1000902/distribution-of-hcn-in-sour-water-systems) | Distribution of HCN in sour water systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000879](https://www.digitalrefining.com/article/1000879/hcn-in-amine-systems) | HCN in amine systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000551](https://www.digitalrefining.com/article/1000551/minimise-corrosion-while-maximising-distillate) | Minimise corrosion while maximising distillate | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003471](https://www.digitalrefining.com/article/1003471/hydrogen-blistering-in-rich-amine-flash-drum-of-vgo-hds-unit) | Hydrogen blistering in rich amine flash drum of VGO HDS unit | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000598](https://www.digitalrefining.com/article/1000598/multiple-corrosion-mechanisms-in-crude-distillation-overhead-system) | Multiple corrosion mechanisms in crude distillation overhead system | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001747](https://www.digitalrefining.com/article/1001747/addressing-corrosion-challenges-in-refineries) | Addressing corrosion challenges in refineries | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003488](https://www.digitalrefining.com/article/1003488/risk-based-integrity-approach-to-vessel-life-extension) | Risk-based integrity approach to vessel life extension | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003293](https://www.digitalrefining.com/article/1003293/digital-twin-corrosion-monitoring-for-cdu-overhead-systems) | Digital twin corrosion monitoring for CDU overhead systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002501](https://www.digitalrefining.com/article/1002501/real-time-crude-and-desalter-monitoring) | Real-time crude and desalter monitoring | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002630](https://www.digitalrefining.com/article/1002630/amine-anomaly-in-a-mild-hydrocracker) | Amine anomaly in a mild hydrocracker | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003203](https://www.digitalrefining.com/article/1003203/plan-for-corrosion-when-co-processing-renewable-feedstocks-ertc-202) | Plan for corrosion when co-processing renewable feedstocks (ERTC 2024) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003085](https://www.digitalrefining.com/article/1003085/co-processing-renewable-feeds-in-hydrodesulphurisation-units) | Co-processing renewable feeds in hydrodesulphurisation units | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003123](https://www.digitalrefining.com/article/1003123/co-processing-renewable-feeds-in-hydrodesulphurisation-units-part-2) | Co-processing renewable feeds in hydrodesulphurisation units: Part 2 | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002659](https://www.digitalrefining.com/article/1002659/key-considerations-for-design-and-operation-of-a-renewable-diesel-unit) | Key considerations for design and operation of a renewable diesel unit | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003094](https://www.digitalrefining.com/article/1003094/saf-production-via-co-processing-in-the-kerosene-hydrotreater) | SAF production via co-processing in the kerosene hydrotreater | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000244](https://www.digitalrefining.com/article/1000244/improving-sulphur-recovery-units) | Improving sulphur recovery units | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002462](https://www.digitalrefining.com/article/1002462/revamping-the-sulphur-plant) | Revamping the sulphur plant | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000498](https://www.digitalrefining.com/article/1000498/designing-for-sulphur-removal-and-storage-part-ii) | Designing for sulphur removal and storage: part II | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000464](https://www.digitalrefining.com/article/1000464/processing-nh3-acid-gas-in-a-sulphur-recovery-unit) | Processing NH3 acid gas in a sulphur recovery unit | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000747](https://www.digitalrefining.com/article/1000747/sulphur-tail-gas-thermal-oxidiser-systems) | Sulphur tail gas thermal oxidiser systems | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001113](https://www.digitalrefining.com/article/1001113/linings-for-sulphur-storage-tanks) | Linings for sulphur storage tanks | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000917](https://www.digitalrefining.com/article/1000917/risks-of-accumulated-sulphur-in-sulphur-recovery-units) | Risks of accumulated sulphur in sulphur recovery units | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001233](https://www.digitalrefining.com/article/1001233/importance-of-heat-maintenance-in-sulphur-recovery-units) | Importance of heat maintenance in sulphur recovery units | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000874](https://www.digitalrefining.com/article/1000874/loading-up-liquid) | Loading up liquid | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000212](https://www.digitalrefining.com/article/1000212/delayed-coker-design-and-project-execution) | Delayed coker design and project execution | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000176](https://www.digitalrefining.com/article/1000176/coke-drum-design) | Coke drum design | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000046](https://www.digitalrefining.com/article/1000046/delayed-coking-valves-make-the-difference) | Delayed coking: valves make the difference | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000242](https://www.digitalrefining.com/article/1000242/a-flexible-approach-to-refinery-olefin-alkylation) | A flexible approach to refinery olefin alkylation | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002350](https://www.digitalrefining.com/article/1002350/removing-acid-droplets-produced-by-alkylation-reaction) | Removing acid droplets produced by alkylation reaction | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001555](https://www.digitalrefining.com/article/1001555/hydrofluoric-acid-alkylation-conversion-and-expansion) | Hydrofluoric acid alkylation conversion and expansion | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001490](https://www.digitalrefining.com/article/1001490/catalyst-passivation-for-safer-more-efficient-turnarounds) | Catalyst passivation for safer, more efficient turnarounds | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001032](https://www.digitalrefining.com/article/1001032/reducing-reactor-turnaround-time) | Reducing reactor turnaround time | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001469](https://www.digitalrefining.com/article/1001469/eliminating-inert-entry-for-catalyst-changeout-ti) | Eliminating inert entry for catalyst changeout (TIA) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003127](https://www.digitalrefining.com/article/1003127/vessel-internals-enhance-worker-safety-during-plant-turnarounds-ti) | Vessel internals enhance worker safety during plant turnarounds (TIA) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003058](https://www.digitalrefining.com/article/1003058/worker-safety-when-entering-reactors-with-an-inert-atmosphere-ti) | Worker safety when entering reactors with an inert atmosphere (TIA) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001110](https://www.digitalrefining.com/article/1001110/gas-and-fire-detection-in-a-tankage-area) | Gas and fire detection in a tankage area | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002430](https://www.digitalrefining.com/article/1002430/refinery-protection-with-gas-detection) | Refinery protection with gas detection | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1001033](https://www.digitalrefining.com/article/1001033/determining-safety-distance-in-process-design) | Determining safety distance in process design | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002772](https://www.digitalrefining.com/article/1002772/economical-structural-design-of-natural-gas-processing-plants) | Economical structural design of natural gas processing plants | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003470](https://www.digitalrefining.com/article/1003470/transitioning-refinery-hydrogen-systems-from-grey-to-green) | Transitioning refinery hydrogen systems from grey to green | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002868](https://www.digitalrefining.com/article/1002868/introducing-hydrogen-into-refinery-boilers-turbines-and-hrsgs-ti) | Introducing hydrogen into refinery boilers, turbines and HRSGs (TIA) | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1002449](https://www.digitalrefining.com/article/1002449/ccs-from-refinery-emissions-co2-purity-must-be-analysed-and-controlled) | CCS from refinery emissions: CO2 purity must be analysed and controlled | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003307](https://www.digitalrefining.com/article/1003307/cracking-the-challenge-of-green-energy-the-vital-role-ammonia-has-to-play) | Cracking the challenge of green energy: the vital role ammonia has to play | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000299](https://www.digitalrefining.com/article/1000299/catalyst-catastrophes-in-hydrogen-plants) | Catalyst catastrophes in hydrogen plants | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1000924](https://www.digitalrefining.com/article/1000924/reformer-monitoring-via-in-tube-temperature-measurement) | Reformer monitoring via in-tube temperature measurement | Digital Refining | global | mixed | document | S | robots |  |
| [DR 1003081](https://www.digitalrefining.com/article/1003081/steam-methane-reformer-tube-lifecycle-improvement-best-practices) | Steam methane reformer tube lifecycle improvement best practices | Digital Refining | global | mixed | document | S | robots |  |

## Where to read or buy standards lawfully

| Document | Title | Body | Region | Access | Link | Title | Check | Note |
|---|---|---|---|---|---|---|---|---|
| [NIST: standards incorporated by reference](https://www.nist.gov/standardsgov/accessing-standards-incorporated-reference) | How to find free read-only copies of standards cited in US regulations | Free and lawful access | global | free | document | C | ok |  |
| [NIST SIBR database](https://sibr.nist.gov/) | Standards Incorporated by Reference database, searchable by CFR citation | Free and lawful access | global | free | document | C | ok |  |
| [ANSI IBR portal](https://ibr.ansi.org/) | Read-only access to many standards incorporated by reference (registration) | Free and lawful access | global | free | document | C | blocked |  |
| [API IBR reading room](https://publications.api.org/) | Read-only access to API standards incorporated in US regulations and safety documents (registration) | Free and lawful access | global | free | document | C | robots |  |
| [ASTM Reading Room](https://www.astm.org/products-services/reading-room.html) | Read-only access to ASTM standards incorporated by reference (registration) | Free and lawful access | global | free | document | C | ok |  |
| [NFPA free access](https://www.nfpa.org/for-professionals/codes-and-standards/list-of-codes-and-standards/free-access) | Read-only online access to NFPA codes (free account) | Free and lawful access | global | free | document | C | ok |  |
| [ICC public access codes](https://codes.iccsafe.org/) | Read-only International Codes | Free and lawful access | global | free | document | C | ok |  |
| [BIS standards portal](https://standards.bis.gov.in/) | Indian Standards search and download service | Free and lawful access | global | free | document | C | ok |  |
| [ISO Online Browsing Platform](https://www.iso.org/obp/ui) | Free preview of scope, terms and contents of ISO standards | Free and lawful access | global | free | document | C | blocked |  |
| [IEC webstore previews](https://webstore.iec.ch/) | Free preview pages of IEC standards | Free and lawful access | global | free | document | C | ok |  |
| [NORSOK overview](https://standard.no/en/sectors/petroleum/norsok-standards/) | NORSOK standards list and access options from Standards Norway | Free and lawful access | global | free | document | C | ok |  |
| [DNV rules and standards](https://www.dnv.com/rules-standards/) | DNV rules, standards and recommended practices portal | Free and lawful access | global | free | document | C | ok |  |
| [EUR-Lex](https://eur-lex.europa.eu/) | Official EU legislation | Free and lawful access | global | free | document | C | ok |  |
| [eCFR](https://www.ecfr.gov/) | US Code of Federal Regulations, current text | Free and lawful access | global | free | document | C | ok |  |
| [UK legislation](https://www.legislation.gov.uk/) | Official UK legislation | Free and lawful access | global | free | document | C | blocked |  |
| [HSE publications](https://www.hse.gov.uk/pubns/) | Free HSE books and leaflets | Free and lawful access | global | free | document | C | ok |  |
| [ANSI Webstore](https://webstore.ansi.org/) | Standards store for many US and international developers | Paid distributors | global | paid | document | C | blocked |  |
| [Accuris Standards Store](https://store.accuristech.com/) | Standards distributor (formerly Techstreet) | Paid distributors | global | paid | document | C | robots |  |
| [BSI Knowledge](https://knowledge.bsigroup.com/) | British, European and international standards | Paid distributors | global | paid | document | C | ok |  |
| [Intertek Inform](https://www.intertekinform.com/) | Standards distributor | Paid distributors | global | paid | document | C | blocked |  |
| [DIN Media](https://www.dinmedia.de/en) | German and international standards | Paid distributors | global | paid | document | C | ok |  |
| [ASTM Compass](https://www.astm.org/products-services/enterprise-solutions.html) | ASTM subscription platform | Paid distributors | global | paid | document | C | ok |  |

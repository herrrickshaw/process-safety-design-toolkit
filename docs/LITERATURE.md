# Literature and source index

Generated from `process_safety/data/literature.json` (compiled 2026-11-06). 64 sources, 25 read for the toolkit, the rest URL-checked only.
Regenerate: `python -m process_safety literature --markdown > docs/LITERATURE.md`. Search: `python -m process_safety literature TEXT [--topic T] [--module M]`.

* **read**: `text` = document text read for the toolkit; `page` = the page or article read; `no` = listed, URL checked, content not read.
* **HTTP**: status of an automated request on the checked date. 403 usually means the site blocks automated clients (open in a browser); 0 a timeout; 202/302 are redirects or challenges that still resolve in a browser.
* Paywalled standards and books are listed so you know they exist; their content is not reproduced here.

## Regulation

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [NOPSEMA offshore safety case regime](https://www.nopsema.gov.au/) | NOPSEMA (Australia) | AU | free | no | 0 | safety-case, offshore, regulation |  |  |
| [Directive 2012/18/EU (Seveso III)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | European Union | EU | free | text | 202 | seveso, regulation | mah | Annex I parsed into data/seveso_iii_annex_i.json |
| [Directorate General Factory Advice Service and Labour Institutes](https://dgfasli.gov.in/) | DGFASLI (India) | IN | free | no | 200 | india, regulation, factories |  |  |
| [Petroleum and Explosives Safety Organisation](https://peso.gov.in/) | PESO (India) | IN | free | no | 0 | india, regulation, explosives |  |  |
| [Petroleum and Natural Gas Regulatory Board](https://www.pngrb.gov.in/) | PNGRB (India) | IN | free | no | 200 | india, regulation, gas |  |  |
| [Major Hazard Installations: safety case regime](https://www.mom.gov.sg/maintenance/workplace-safety-and-health/major-hazard-installations) | Ministry of Manpower (Singapore) | SG | free | page | 200 | safety-case, regulation, qra | qra |  |
| [COMAH Regulations 2015 guidance](https://www.hse.gov.uk/comah/comah15.htm) | HSE (UK) | UK | free | page | 200 | comah, regulation, safety-case | mah, qra |  |
| [29 CFR 1910.119 Process safety management of highly hazardous chemicals](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) | OSHA (US) | US | free | text | 200 | psm, regulation | psm | 14 elements, Appendix A |
| [49 CFR 192 Transportation of natural and other gas by pipeline](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-D/part-192) | eCFR | US | free | text | 200 | pipeline, regulation | pipeline |  |
| [49 CFR 193 LNG facilities: federal safety standards](https://www.ecfr.gov/current/title-49/subtitle-B/chapter-I/subchapter-D/part-193) | eCFR | US | free | text | 200 | lng, regulation | lng | current text; NPRM would replace |
| [EPA Risk Management Program (40 CFR 68)](https://www.epa.gov/rmp) | EPA (US) | US | free | text | 200 | rmp, regulation, consequence | rmp | 2026 revision proposal pending (see DESIGN_AWARENESS.md) |
| [PHMSA pipeline and LNG safety](https://www.phmsa.dot.gov/) | PHMSA (US) | US | free | no | 403 | pipeline, lng, regulation | pipeline, lng | 49 CFR 192/193 read; Oct 2026 LNG NPRM proposed |
| [ILO Convention 174, Prevention of Major Industrial Accidents](https://normlex.ilo.org/dyn/nrmlx_en/f?p=NORMLEXPUB:12100:0::NO::P12100_ILO_CODE:C174) | ILO | global | free | no | 403 | regulation, international |  | ratification counts differ between sources; check NORMLEX |

## Standard

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [OISD standards list (105 standards)](https://www.oisd.gov.in/oisd-standards) | OISD (India) | IN | mixed | page | 200 | india, standards, oil-gas | standards | list and editions in data/oisd_standards.json; contents not read |
| [AACE RP 18R-97 Cost estimate classification system, process industries](https://library.aacei.org/pgd01/pgd01.shtml) | AACE International | global | paywalled | no | 200 | cost-estimation, aace, accuracy | lng_cost | copyrighted; class ranges used in docs/COST_ESTIMATION.md are those quoted in the ORIMIZ factor file and NETL, not read from AACE |

## Guidance

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [Major hazard facilities](https://safeworkaustralia.gov.au/safety-topic/industry-and-business/major-hazard-facilities) | Safe Work Australia | AU | free | no | 302 | safety-case, regulation |  | fetch timed out on 2026-11-06; verify access |
| [HSE COMAH home (Buncefield, competent authority material)](https://www.hse.gov.uk/comah/) | HSE (UK) | UK | free | no | 200 | comah, incident | overfill |  |
| [HSE risk management pages (ALARP, tolerability)](https://www.hse.gov.uk/risk/) | HSE (UK) | UK | free | no | 200 | risk-criteria, alarp, qra | qra | the R2P2 criteria used as QRA presets came from secondary sources; the old direct R2P2 URL returned 404 on 2026-11-06 |
| [HSG254 Developing process safety indicators](https://www.hse.gov.uk/pubns/books/hsg254.htm) | HSE (UK) | UK | mixed | no | 200 | psm, indicators, management | psm |  |
| [DOE-HDBK-1101-96 Process safety management for highly hazardous chemicals](https://www.energy.gov/documents/doe-hdbk-1101-96) | US DOE | US | free | page | 200 | psm, audit | psm |  |
| [OSHA Process Safety Management topic page](https://www.osha.gov/process-safety-management) | OSHA (US) | US | free | no | 200 | psm, regulation | psm | enforcement directives and NEP are linked from here |
| [QGESS: Capital cost scaling methodology, Revision 4](https://www.osti.gov/servlets/purl/1573493) | US DOE NETL | US | free | no | 200 | cost-estimation, scaling, escalation | lng_cost | scaling of legacy estimates by size, date and location; not read |
| [QGESS: Cost estimation methodology for NETL assessments of power plant performance](https://netl.doe.gov/projects/files/QGESSCostEstMethodforNETLAssessmentsofPowerPlantPerformance_022621.pdf) | US DOE NETL | US | free | no | 200 | cost-estimation, aace, methodology | recommendation_cost, lng_cost | public worked methodology (bare erected cost to total overnight cost, AACE Class 4 target); power-plant context; not read |
| [AIGA 99/20 Process safety management](https://asiaiga.org/uploaded_docs/en_AIGA_99_20_Process_Safety_Mangement.pdf) | AIGA | global | free | page | 200 | psm | psm |  |
| [LNG Plant Cost Reduction 2014-18 (OIES NG137)](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2018/10/LNG-Plant-Cost-Reduction-2014%E2%80%9318-NG137.pdf) | Oxford Institute for Energy Studies | global | free | no | 200 | cost-estimation, lng | lng_cost | origin of most plant-only analog figures and factors; not read in full |
| [Learn how to easily design and evaluate the cost of your projects (UniSim + Cleopatra)](https://cleopatraenterprise.com/webinar-learn-how-to-easily-design-and-evaluate-the-cost-of-your-projects) | Cleopatra Enterprise / Honeywell | global | free | no | 200 | cost-estimation, simulation, vendor |  | webinar page; the data flow between simulator and costing software was not found |
| [Monte Carlo is not magic](https://www.somaprojectcontrols.com/resources/guides/monte-carlo-is-not-magic/) | SOMA Project Controls | global | free | no | 200 | schedule-risk, cost-risk, monte-carlo, shutdown | shutdown_risk | consultancy guide; not read |
| [OECD Guiding Principles for Chemical Accident Prevention, Preparedness and Response](https://www.oecd.org/en/topics/chemical-accidents.html) | OECD | global | free | no | 403 | international, guidance, psm |  | third edition supports the 2023 Council Recommendation |
| [QCRA explained: quantitative cost risk analysis](https://iqrm.net/blog/qcra-explained-quantitative-cost-risk-analysis-2026) | IQRM | global | free | no | 200 | schedule-risk, cost-risk, monte-carlo, shutdown | shutdown_risk | vendor blog; method background; not read |
| [UniSim Design R460 brochure (sizing, rating and costing; Cleopatra Enterprise integration)](https://process.honeywell.com/content/dam/process/en/documents/document-lists/hon-ia-hps-bro-unisim-design-r460-vcma.pdf) | Honeywell | global | free | page | 200 | cost-estimation, simulation, vendor | lng_cost, recommendation_cost | vendor brochure: states integration with Cost Engineering's Cleopatra Enterprise for costing; older release |
| [UniSim Design external FAQ](https://hcenews.honeywell.com/rs/093-RAU-212/images/UNISIM_External_FAQ.pdf) | Honeywell | global | free | page | 200 | cost-estimation, simulation, vendor |  | vendor FAQ: lists Cleopatra Plus for cost estimating and Capex optimisation use |

## Investigation

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [CSB investigations](https://www.csb.gov/investigations/) | US Chemical Safety Board | US | free | page | 200 | incident, investigation | psm, overfill, relief | CSB investigates and recommends; it does not regulate. 17 investigations read for docs/INCIDENTS.md |
| [CSB recommendations](https://www.csb.gov/recommendations/) | US Chemical Safety Board | US | free | no | 200 | incident, investigation |  |  |

## Database

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [eMARS major accident reporting system](https://emars.jrc.ec.europa.eu/) | EU Joint Research Centre | EU | free | no | 200 | incident, database, seveso | mah |  |
| [ARIA accident database (BARPI)](https://www.aria.developpement-durable.gouv.fr/) | French Ministry of Ecological Transition | FR | free | no | 200 | incident, database |  |  |

## Association

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [Energy Institute technical publications](https://www.energyinst.org/technical) | Energy Institute | UK | mixed | no | 403 | guidelines, oil-gas, psm |  |  |
| [IChemE Safety Centre](https://www.icheme.org/knowledge/safety-centre/) | IChemE | UK | mixed | no | 200 | psm, incident, lessons |  |  |
| [AFPM process safety](https://www.afpm.org/issues/safety-health/process-safety) | American Fuel & Petrochemical Manufacturers | US | free | page | 200 | psm, refining, rmp | rmp | industry-association position |
| [Mary Kay O'Connor Process Safety Center](https://psc.tamu.edu/) | Texas A&M University | US | free | no | 200 | research, psm |  |  |
| [Center for Chemical Process Safety](https://www.aiche.org/ccps) | AIChE | global | mixed | no | 403 | psm, guidelines, rbps | psm, hazop, sil | books are paywalled |
| [IOGP safety, including Life-Saving Rules and process safety reports](https://www.iogp.org/safety/) | IOGP | global | free | no | 200 | life-saving-rules, psm, oil-gas |  |  |
| [SPE In Focus: Process Safety](https://www.spe.org/en/focus/process-safety/) | Society of Petroleum Engineers | global | free | page | 200 | psm, oil-gas |  | index of articles, papers on OnePetro (many paywalled) |

## Journal

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [Journal of Loss Prevention in the Process Industries](https://www.sciencedirect.com/journal/journal-of-loss-prevention-in-the-process-industries) | Elsevier | global | paywalled | no | 403 | research, consequence, qra |  |  |
| [Process Safety Progress](https://aiche.onlinelibrary.wiley.com/journal/15475913) | AIChE / Wiley | global | paywalled | no | 403 | research, psm |  |  |
| [Process Safety and Environmental Protection](https://www.sciencedirect.com/journal/process-safety-and-environmental-protection) | Elsevier / IChemE | global | paywalled | no | 403 | research, psm |  |  |

## News

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [Approach aims to prevent process safety incidents (ADNOC PSM framework)](https://jpt.spe.org/approach-aims-to-prevent-process-safety-incidents) | Journal of Petroleum Technology (SPE) | ME | free | page | 200 | psm, incident, company | psm | 15 elements; 50+ event review; SPE paper 210971 |
| [Sigma-HSE news and insights](https://sigma-hse.com/news-insights/) | Sigma-HSE | UK | free | page | 200 | psm, hazop, dust, atex, reaction-hazard | atex, reaction_hazard | titles only |
| [Why are early-stage design decisions critical for process safety?](https://sigma-hse.com/news-insights/early-stage-design-decisions/) | Sigma-HSE | UK | free | page | 200 | reaction-hazard, design, scale-up | reaction_hazard, thermal_runaway | statistics quoted by the article, not checked |
| [Investigators find operating, training deficiencies contributed to fatal refinery explosion](https://jpt.spe.org/investigators-find-operating-training-deficiencies-contributed-to-fatal-refinery-explosion) | Journal of Petroleum Technology (SPE) | US | free | page | 200 | incident, overfill, relief, psm | relief, overfill | BP Oregon, Ohio 2022; OSHA findings |
| [PHMSA proposes comprehensive revisions to safety regulations for LNG facilities](https://natlawreview.com/article/phmsa-proposes-comprehensive-revisions-safety-regulations-lng-facilities) | National Law Review / Van Ness Feldman | US | free | page | 200 | lng, regulation | lng | law-firm summary of the 28 Oct 2026 NPRM |
| [PSM News (James Klein)](https://psmnews.com/) | Process Safety Priorities LLC | US | free | page | 200 | psm, blog |  | single-author blog; low weight; nothing used |
| [Are process safety standards and practices ready for the energy transition?](https://jpt.spe.org/are-process-safety-standards-and-practices-ready-for-the-energy-transition) | Journal of Petroleum Technology (SPE) | global | free | no | 200 | psm, management-of-change, energy-transition |  |  |
| [Benchmarking study compares LNG plant costs](https://ogj.com/drilling-production/production-operations/article/17239949/benchmarking-study-compares-lng-plant-costs) | Oil & Gas Journal | global | mixed | no | 200 | cost-estimation, lng, benchmark | lng_cost | older trade article; not read |
| [Process Safety Beacon](https://ccps.aiche.org/process-safety-beacon) | CCPS | global | free | no | 403 | incident, awareness |  | returned a bot check (HTTP 403) on 2026-11-06; not read, no bypass |
| [Project Controls Online](https://projectcontrolsonline.com) | projectcontrolsonline.com | global | free | no | 200 | schedule-risk, cost-risk, shutdown | shutdown_risk | project controls community site; not read |

## Data tool

| Source | Publisher | Region | Access | Read | HTTP | Topics | Modules | Note |
|---|---|---|---|---|---|---|---|---|
| [BibMon (Petrobras)](https://github.com/petrobras/BibMon) | Petrobras | BR | free | no | 200 | monitoring, fault-detection |  | Apache-2.0; complementary, not integrated |
| [BioSTEAM techno-economic analysis tutorial](https://biosteam.readthedocs.io/en/latest/tutorial/Techno-economic_analysis.html) | BioSTEAM (Univ. of Illinois) | global | free | no | 200 | cost-estimation, tea, lang-factor | recommendation_cost | open-source Python TEA: installed cost via Lang factor or bare-module factors, cash-flow analysis; licence not checked here |
| [CoolProp](https://coolprop.org/) | CoolProp project | global | free | text | 200 | properties, validation | fluiddata, props | MIT; source of data/fluid_screening.json and test oracle |
| [OTsafe](https://github.com/p4lsec/otsafe) | p4lsec | global | free | no | 200 | ot-security, safety-modelling |  | Apache-2.0; complementary, not integrated |
| [Open FEL1 LNG Cost (ORIMIZ Consulting)](https://github.com/ORIMIZ-Consulting/open-fel1-lng-cost) | ORIMIZ Consulting / S. Z. Haider | global | free | page | 200 | cost-estimation, lng, analog | lng_cost | MIT; README, factors and analog table read as text; code not run |
| [Open Plant Cost Index (OPCI)](https://github.com/ORIMIZ-Consulting/open-plant-cost-index) | ORIMIZ Consulting | global | free | no | 200 | cost-estimation, escalation, location-factors | lng_cost | source of ORIMIZ escalation and location factors; not read |
| [QSDsan techno-economic analysis tutorial](https://qsdsan.readthedocs.io/en/latest/tutorials/7_TEA.html) | QSDsan | global | free | no | 200 | cost-estimation, tea, cepci |  | builds on BioSTEAM TEA; exposes a CEPCI input and Lang factor; licence not checked here |
| [fluids (ChEDL)](https://fluids.readthedocs.io/) | Caleb Bell | global | free | text | 200 | validation, relief, hydraulics | relief, hydraulics, separator | MIT; test oracle only |
| [thermo (ChEDL)](https://thermo.readthedocs.io/) | Caleb Bell | global | free | text | 200 | properties, validation | props | MIT; test oracle only |

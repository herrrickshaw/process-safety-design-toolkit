# Regulatory landscape: countries, governing bodies and company policies

Compiled 2026-11-06 for design teams who need to know which regime a facility falls under and who sets the rules. Read the
confidence column before relying on a row.

| Confidence | Meaning |
|---|---|
| **A** | Rule text read for the toolkit (see `SOURCES.md`): OSHA 1910.119, EPA 40 CFR 68, 49 CFR 192/193, Seveso III Annex I |
| **B** | Official regulator page read on 2026-11-06 |
| **C** | Web-search summary of secondary sources; primary text not read. Use to orient, then check the regulator |
| **N** | Looked for, not found or not verified. Left blank on purpose |

Nothing here is legal advice, and it is not a compliance checklist.

## 1. By country or region

| Jurisdiction | Core regime | Regulator(s) | What the operator must produce | Conf. |
|---|---|---|---|---|
| United States | OSHA PSM (29 CFR 1910.119, 14 elements, Appendix A chemicals); EPA Risk Management Program (40 CFR 68); pipeline safety (49 CFR 192) and LNG (49 CFR 193) | OSHA; EPA; PHMSA; the CSB investigates but does not regulate | PSM programme and PHA with 5-year revalidation; RMP with worst-case and alternative-release analysis; LNG per Part 193 (a PHMSA proposal of 28 Oct 2026 would move it to NFPA 59A-2026, comments due 4 Jan 2027; not final) | A (PHMSA proposal: C, a law-firm summary) |
| European Union | Seveso III, Directive 2012/18/EU: Annex I qualifying quantities, sum rule, lower and upper tier | Member-state competent authorities | lower tier: prevention policy; upper tier: safety report, emergency plans, public information (detail per member state) | A for Annex I; tier duties B via the UK page below |
| United Kingdom | COMAH Regulations 2015 (in force 1 June 2015; implements Seveso III except land-use planning) | HSE (ONR for nuclear sites) jointly with the Environment Agency (England), SEPA (Scotland) or Natural Resources Wales | all operators: notification and public information; lower tier: major accident prevention policy; upper tier: safety report (reviewed at least every 5 years), internal emergency plan, information for external emergency planning | B |
| Netherlands / UK risk criteria | Bevi (NL) and HSE R2P2 tolerability criteria are used by the QRA module as presets | not researched here | risk evaluation against individual and societal risk lines | C (via `SOURCES.md`) |
| India | no single PSM law. MSIHC Rules 1989 (under the Environment (Protection) Act 1986); Factories Act chapter IV-A with state rules; CIMAH-type rules for major accident hazard installations; Petroleum, Explosives and Gas Cylinders rules; OISD standards for oil and gas (105 listed in `data/oisd_standards.json`) | MoEFCC (MSIHC); state factory inspectorates and pollution boards; DGFASLI at major ports; PESO (petroleum, explosives, compressed gas); OISD (standards); PNGRB (referenced in the coverage map, not read) | safety reports and audit reports for major accident hazard installations; site appraisal for hazardous plants; compliance with the sector standard | C (OISD list itself: A) |
| Australia | model WHS Regulations, chapter 9, Schedule 15 chemicals: major hazard facility licence and safety case (state and territory regulators); offshore: OPGGS safety regulations (2024) | state WHS regulators (e.g. Queensland, NT, WA); Safe Work Australia (model laws); NOPSEMA (offshore petroleum) | MHF: notify above 10% of a Schedule 15 threshold, licence and safety case above the threshold; offshore: NOPSEMA-accepted safety case | C (the Safe Work Australia page timed out) |
| Singapore | Workplace Safety and Health (Major Hazard Installations) Regulations, from 1 Sept 2017: safety case regime | Ministry of Manpower, Major Hazards Department | safety case, QRA, incident reporting, information to affected workplaces; MOM sets no fixed format | B for scope (MOM index page); C for dates |
| South Korea | PSM under the Industrial Safety and Health Act (basis set Jan 1995, process safety report review from 1996); Chemicals Control Act (2015) with off-site consequence analysis and risk management plans | Ministry of Employment and Labor and KOSHA (roles not confirmed by a primary source); Ministry of Environment for chemicals | process safety report to the government; off-site consequence analysis | C |
| China | identification of major hazard installations for dangerous chemicals, GB 18218-2018 (in force Mar 2019; production and storage units; graded, level 1 highest) under the Interim Provisions on supervision of such installations | Ministry of Emergency Management | registration and grading, responsible persons named for each installation | C |
| Gulf (Saudi Arabia, UAE) | no national major-hazard law confirmed. Saudi: Royal Commission Environmental Regulations (RCER-2015) for Jubail, Yanbu and Ras Al Khair; Aramco SAES/SAEP engineering standards for Aramco work. UAE: Abu Dhabi OSHAD-SF (v3.1, March 2017); Emirates Fire and Life Safety Code (2017 update). See section 6 | Royal Commission for Jubail and Yanbu; Abu Dhabi Public Health Center (reported supervisor of OSHAD-SF); UAE Civil Defence (fire code) | no PSM text found in RCER or OSHAD-SF searches | C / N |
| Canada, Japan | looked for (CEPA environmental emergency regulations, High Pressure Gas Safety Act), nothing usable returned | | | N |

## 2. By governing body

| Body | Kind | What it governs | Conf. |
|---|---|---|---|
| OSHA | US regulator | PSM for highly hazardous chemicals | A |
| EPA | US regulator | RMP for off-site consequences | A |
| PHMSA | US regulator | pipelines and LNG facilities | A / C |
| CSB | US independent investigator | root-cause reports, recommendations; no enforcement | C |
| HSE with EA, SEPA, NRW | UK competent authority | COMAH | B |
| European Commission and member states | supranational and national | Seveso III | A |
| Ministry of Manpower | Singapore regulator | MHI safety case | B |
| Ministry of Emergency Management | China regulator | major hazard installations | C |
| State WHS regulators, NOPSEMA | Australian regulators | MHF licences; offshore safety cases | C |
| MoEFCC, state inspectorates, DGFASLI, PESO, OISD | Indian authorities | MSIHC, Factories Act, petroleum and explosives, oil and gas standards | C |
| ILO (Convention 174, 1993) | international | prevention of major industrial accidents. Sources conflict on how many states ratified (19 against 23 in different statements): check ILO NORMLEX | C |
| OECD | international | Guiding Principles for Chemical Accident Prevention, Preparedness and Response (1992, 2003; third edition supports the 2023 Council Recommendation) | C |
| IOGP | industry association | Life-Saving Rules, report 459 (nine rules, version 3.0, Aug 2018) | C |
| API, NFPA, IEC, ISO, CCPS | standards and guidance bodies | the design standards the modules cite (`docs/SOURCES.md`); mostly paywalled and not read | n/a |

## 3. By company (public statements only)

Company systems sit on top of law: they set stricter or more uniform internal rules. Only what each company publishes is covered.

| Company | Public framework | Note | Conf. |
|---|---|---|---|
| ExxonMobil | Operations Integrity Management System (OIMS), developed 1992, 11 elements; refreshed in 2024 to add a Personnel Safety Management System; life-saving rules follow the IOGP programme | | C |
| Chevron | Operational Excellence Management System (OEMS), launched 2004: leadership accountability, a management-system process, and OE expectations | an older internal overview lists 13 elements; recent materials use focus areas, so the count may have changed | C |
| Shell | Goal Zero ambition (no harm to people, no leaks); HSSE and SP Control Framework launched 2009 with manuals including process safety; process-safety fundamentals such as two barriers on hydrocarbon drains and vents | the Life-Saving Rules text was not retrieved | C |
| BP | The Baker panel (after Texas City 2005, 15 killed) told the board to establish an integrated process safety management system, board-level process safety goals, knowledge and expertise at all levels, process safety auditing, and an independent monitor reporting annually | BP's own operating management system documents were not retrieved | C |
| ADNOC, SABIC | ADNOC's safety standards draw on OSHAD and list PSM as an operational standard; SABIC states its sites follow PSM programmes consistent with international standards | secondary summaries | C |
| Indian operators (IOCL, Reliance, ONGC and others) | not researched | | N |

## 4. What the three lenses show

* **Three regulatory styles.** (1) Prescriptive PSM programme: US OSHA, South Korea. (2) Safety case, where the operator demonstrates control of major accident risk to the regulator: UK upper tier, Australia MHF and offshore, Singapore. (3) Threshold listing and registration with inspection: EU lower tier, China grading, India's rules. Many countries mix them; the Seveso family sits between (2) and (3).
* **Thresholds decide the paperwork early.** Seveso, OSHA Appendix A, EPA RMP, Schedule 15 and GB 18218 all start from a substance quantity. The toolkit's `seveso`, `psm-check` and `rmp-check` commands implement three of these; Australian, Chinese, Korean and Indian thresholds are not implemented.
* **Safety case regimes want quantified risk.** Singapore lists QRA as a requirement topic and the UK criteria used here come from R2P2. The `qra` workflow with R2P2 and Bevi presets fits this style; an India or Singapore criterion has to be supplied as a custom one.
* **Company systems converge on the same shape.** ExxonMobil, Chevron, Shell and the Baker recommendations all combine leadership accountability, a management-system standard, and auditing, and since Texas City the emphasis includes process safety, not only personal safety. A design team inside such a company designs to the stricter of law and company standard.
* **Regulation is moving.** The 2026 PHMSA proposal for LNG would borrow PSM-style elements (PHA, management of change, mechanical integrity) into a risk-based option, an example of style (1) entering style (3) territory.

## 6. OSHA and Middle East sources

### OSHA (United States)
| Source | What it is | Status |
|---|---|---|
| [29 CFR 1910.119, Process safety management](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) | the standard: 14 elements, Appendix A list of 134 chemicals, the 10,000 lb flammables rule | A: read for `psm.py` and `data/osha_psm_appendix_a.json` |
| [OSHA CPL 02-02-045 (1994 PSM compliance directive)](https://www.osha.gov/enforcement/directives/cpl-02-02-045) | older enforcement guidance, listed on osha.gov | C: reported superseded by CPL 02-01-065 (revised PSM directive issued 26 Jan 2024, per a law-firm alert); confirm on osha.gov before citing |
| PSM Covered Chemical Facilities National Emphasis Program, CPL 03-00-021 (17 Jan 2017) | inspection targeting programme | C: reported still in effect; status in Nov 2026 not confirmed |
| [OSHA refinery NEP, CPL 03-00-004](https://www.osha.gov/enforcement/directives/cpl-03-00-004) | separate 2007 programme for refineries | C: listed, not read |
| State plans | states running their own OSHA-approved programmes issue their own PSM directives (for example the [Washington L&I directive](https://lni.wa.gov/dA/547a1e8103/DD2440.pdf)) | C: listed, not read |

The toolkit encodes the standard (A). The directives govern how inspectors apply it, so they matter for audit preparation but change no calculation here.

### Middle East
| Source | What it is | Status |
|---|---|---|
| [Royal Commission for Jubail and Yanbu](https://saudipedia.com/en/the-royal-commission-for-jubail-and-yanbu) and its Royal Commission Environmental Regulations (RCER-2015, replacing RCER-2010; Volume III covers penalties) | rules for operators in Jubail, Yanbu and, per one source, Ras Al Khair | C: general description only; no PSM requirement text found, and the available copies are unofficial (Scribd). Get the volumes from rcjy.gov.sa |
| Saudi Aramco Engineering Standards (SAES/SAEP) | company standards for Aramco work, for example SAES-A-005 safety instruction sheets and SAES-B-057 refrigerated and pressure storage | C: found only through unofficial copies; many search hits list invented numbers, so verify on Aramco's own portal |
| Abu Dhabi OSHAD-SF, [Elements v3.1](https://pdfcoffee.com/oshad-sf-elements-v31-english-pdf-free.html) (March 2017) | occupational safety and health framework: mechanisms, elements, codes of practice (Element 2 risk management, 5 training, 7 monitoring, investigating and reporting) | C: unofficial copy; no dedicated process-safety element found; check for a newer version |
| ADNOC HSE and safety standards | company standards drawing on OSHAD-SF; one secondary source says the HSE management system is built on ISO 45001 and ISO 14001 and lists PSM as an operational standard | C: no official ADNOC document retrieved |
| [UAE Fire and Life Safety Code](https://www.thenationalnews.com/uae/environment/uae-fire-safety-and-life-protection-code-undergoes-major-changes-1.643989) | Civil Defence code (2011, updated 2017; includes flammable liquid storage) | C: news coverage only |
| Qatar, Kuwait, Oman, Bahrain; Saudi environment ministry rules | | N: searched, nothing returned |

Takeaway for design teams in the region: expect project requirements to arrive through the owner company's standards (Aramco, ADNOC) and the industrial-city authority, with US and European standards (API, NFPA, IEC) as the technical base, rather than through one national process-safety statute. That is an inference from the sources above and has not been checked against the primary texts.

## 5. Gaps and what to read next

Primary texts not read: Safe Work Australia Schedule 15 and the MHF guides, MOM's safety case technical guidance, Korean PSM notices, GB 18218-2018, India's MSIHC schedules and OISD contents, Gulf regulations, Canada and Japan. Company management-system documents were not obtained beyond public summaries. Add rows only once the source is read, and keep the confidence column honest.

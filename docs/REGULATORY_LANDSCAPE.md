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
| Gulf (Saudi Arabia, UAE) | not verified. Secondary mentions: Abu Dhabi OSHAD framework behind ADNOC standards; Saudi sites follow company PSM aligned with international practice | not verified | | N |
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

## 5. Gaps and what to read next

Primary texts not read: Safe Work Australia Schedule 15 and the MHF guides, MOM's safety case technical guidance, Korean PSM notices, GB 18218-2018, India's MSIHC schedules and OISD contents, Gulf regulations, Canada and Japan. Company management-system documents were not obtained beyond public summaries. Add rows only once the source is read, and keep the confidence column honest.

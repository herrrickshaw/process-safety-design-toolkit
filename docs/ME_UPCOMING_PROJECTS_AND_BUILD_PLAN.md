# Middle East upcoming projects, HAZOP and QRA study potential, and a plan for new toolkit functionality

Written 2026-11-09 on branch `feature/project-pipeline-planning`. This is a **generic Middle East view**, not specific to one consultancy: which projects are coming, what HAZOP, QRA and related studies they imply and when, what new functionality the toolkit could gain to monitor and plan for them, a schedule for building it, and the inputs each item needs. Nothing here was built or run except the schedule, which was produced with the toolkit's own `schedule` tool.

**Read this with its limits.** Project facts come from press reports and search summaries; no operator document was read. Study potential is **my inference** from each project's stage and the order of studies in `docs/DESIGN_LIFECYCLE_PLAN.md`. It is not a forecast of awards, fees or who will win. Grades: **B** = a page or article I read; **C** = a search summary or an aggregator I did not open.

## Market context
* MEED's 2026 GCC oil and gas outlook page puts the project pipeline at more than $234.3bn, and reports 2025 GCC oil and gas contract awards of $48.5bn, down 26% from the 2024 record of $66bn (grade C: search summary of a MEED page; detail is paywalled).
* A "$353bn approved GCC hydrocarbon capital" article that a search returned was published in January 2012 and is **not used**.
* Award activity has cooled while the long-term plans stay large, so near-term study demand is concentrated in projects already awarded.

## Upcoming and ongoing projects
| # | Project | Country | Scope | Stage (as of the source) | Key dates | Source |
|---|---|---|---|---|---|---|
| P1 | North Field West LNG (QatarEnergy) | Qatar | Two 8 MTPA trains (16 MTPA), gas treatment, NGL, helium | EPC awarded to a Technip Energies, CCC and GAC joint venture, 25 Feb 2026. Offshore jackets EPCI awarded Dec 2025; topside bids still open Oct 2026 (C) | First LNG by end of 2031 | B: [Peninsula, 25 Feb 2026](https://thepeninsulaqatar.com/article/25/02/2026/qatarenergy-awards-epc-contract-for-the-north-field-west-16-mtpa-lng-project) |
| P2 | Ras Laffan Petrochemicals Complex (QatarEnergy 70%, CPChem 30%) | Qatar | 2.1 Mtpa ethylene, 1.7 Mtpa HDPE; about $6bn | EPC awarded 2023 (Samsung Engineering and CTCI for the ethylene plant) | Start-up targeted 2026 in 2023 reports; current status not found | C |
| P3 | Ruwais LNG (ADNOC Gas) | UAE | Two 4.8 Mtpa trains, more than doubling ADNOC LNG capacity | FID June 2024; $5.5bn EPC to a Technip Energies, JGC and NMDC joint venture; about $2.1bn more awarded Jan 2025 (Habshan 5 preconditioning, pipelines, compression) | Start-up late 2028 (C) | B: [The Energy Year, 9 Jan 2025](https://theenergyyear.com/news/adnoc-gas-awards-2-1-billion-in-ruwais-lng-contracts/) |
| P4 | Ruwais NGL-5 (ADNOC Gas) | UAE | NGL train | Tecnimont EPC about $4.3bn; award year not stated | Not found | C |
| P5 | Jafurah gas and Master Gas System expansion (Aramco) | Saudi Arabia | $12.4bn Jafurah, $8.8bn Master Gas System, $2.4bn gas rigs (about $25bn in total) | Construction awards 30 June 2024; no contractors named; Master Gas System adds about 4,000 km of pipeline and 17 compression trains by 2028 (C) | Gas output up more than 60% by 2030 | B: [Gulf News, 30 Jun 2024](https://gulfnews.com/business/markets/saudi-aramco-awards-25b-in-contracts-for-gas-expansion-1.103366754) |
| P6 | Amiral complex (Aramco and TotalEnergies, Jubail) | Saudi Arabia | About $11bn petrochemicals | EPC awarded 2023 | Current status not found | C |
| P7 | Marsa LNG (TotalEnergies 80%, OQEP 20%) | Oman | 1 Mtpa liquefaction, 165,000 m3 tank, 500 m jetty, LNG bunkering | Under construction; $1.6bn | LNG production expected Q1 2028; bunkering vessel mid-2028 | B: [Oman Observer, 1 May 2025](https://www.omanobserver.om/article/1169888/business/energy/oman-marks-groundbreaking-on-16-billion-marsa-lng-project) |
| P8 | Duqm petrochemicals (OQ8, OQ and KPI 50:50) | Oman | Original plan about $7bn mixed-feed cracker, polypropylene, HDPE, aromatics; current scope not stated | Feed-to-EPC contest: tender mid-March 2026, proposals reported due 6 May 2026; SABIC reportedly withdrew Dec 2025 | EPC award and start-up not stated | B: [MEED, 27 Apr 2026](https://guest.meed.com/partners-launch-feed-to-epc-contest-for-duqm-petrochemicals-project/) |
| P9 | Duqm refinery (OQ8) | Oman | 230,000 bpd | Trial operations and commissioning (date unclear) | Not found | C |
| P10 | GPIC aromatics facility, Sitra (Bapco Energies, SABIC Agri-Nutrients, Kuwait's PIC) | Bahrain | About 1.2 Mtpa paraxylene and 0.5 Mtpa benzene | FEED awarded to Fluor, about 21 to 23 July 2026 | EPC not yet | C: several outlets in search results |
| P11 | Al-Zour hydrogen unit upgrade (KIPIC, merged into KNPC) | Kuwait | Hydrogen unit upgrade; a $150 to 200m feed-system tender relaunched Feb 2026 | Re-tender after all five technical bids from Sept 2024 were ruled non-compliant | Not found | C: one Italian-language aggregator |
| P12 | Mesaieed refinery HAZOP revalidation and other safety studies (QatarEnergy) | Qatar | HAZOP revalidation, SIL for new SIFs, PSV review, EERA, pre-incident plans; baseline HAZOP and SIL for QATEX | International competitive bid, closed 25 Nov 2024 (award not found) | Offer validity 120 days | B: [TenderDetail listing](https://www.tenderdetail.com/Global-Tenders/TenderNotice/87894343/3DD34C2B-E3A1-4435-B5FC-C72857C4A137) |
| P13 | KIPIC refinery process-unit HAZOP | Kuwait | HAZOP study of refinery process units | A six-month lump-sum tender planned for April 2024 in the KIPIC annual plan (status unknown) | Not found | C: search summary; the PDF would not open |

Not found: any 2026 Kuwait or Bahrain project beyond the items above, any Oman green hydrogen FEED or EPC detail (BP exited the Duqm project; seven other awarded projects are described as on track), and any HAZOP or QRA tender notices for 2026.

## Study potential
Stage-to-study order follows `docs/DESIGN_LIFECYCLE_PLAN.md`: HAZID in concept to FEED; HAZOP once the P&IDs are frozen; relief, flare and blowdown; LOPA and SIL after HAZOP; QRA and siting; fire and gas; then SIL verification, factory and site tests and the pre-start-up safety review (PSSR) before commissioning; HAZOP revalidation in operation. **Potential** is High, Medium or Low by stage and scale, my judgement.

| # | Stage now | Studies likely due in the next 12 to 24 months | Likely route | Potential |
|---|---|---|---|---|
| P1 | EPC, detailed engineering | HAZOP of process units and utilities, LOPA and SIL, relief and flare, QRA, FERA and EERA updates, fire and gas mapping; PSSR comes later (2030 to 2031) | EPC joint venture or owner's engineer | High, long-running |
| P2 | Construction, near start-up (unconfirmed) | PSSR, SIL verification, closure of HAZOP actions, QRA update for operation | Owner or operator | Medium, near-term |
| P3 | EPC since 2024 | Detailed-design HAZOP and SIL for the added packages; SIL verification, SIMOPS and PSSR in 2027 to 2028 | EPC contractors; ADNOC standards | High |
| P4 | EPC (details unknown) | As P3, scope unknown | EPC | Medium |
| P5 | Construction through about 2028 | HAZOP and SIL for 17 compression trains; pipeline QRA for about 4,000 km of line; SIMOPS with live plants; PSSR 2027 to 2028 | EPC contractors; Aramco standards | High, large |
| P6 | Construction or commissioning (unknown) | PSSR and commissioning-phase closure | Owner | Medium |
| P7 | Construction | PSSR and SIL verification before 2028; QRA for the jetty and LNG bunkering interface; FERA and EERA | Owner, EPC | Medium |
| P8 | FEED-to-EPC contest | HAZID, FEED-stage QRA and siting, FERA, early HAZOP once P&IDs freeze | FEED contractors; owner | High if it proceeds; scope and partners unsettled |
| P9 | Commissioning and early operation | PSSR closure, management-of-change reviews; revalidation scheduling from about five years after start-up (interval is the operator's rule) | Operator | Low to Medium |
| P10 | FEED | HAZID, FEED HAZOP, QRA and siting inside an operating complex, SIMOPS and MOC interface studies | FEED contractor; owner | High, near-term |
| P11 | Tender | HAZOP of the modification and tie-ins, SIL review, MOC; timing uncertain | Owner | Medium |
| P12, P13 | Operating plants | Recurring HAZOP revalidation, SIL baseline and revalidation, EERA, PSV review | Operator tenders | Recurring, tender-driven |

**Reading it:** three of the projects are LNG (P1, P3, P7), and P5 includes about 4,000 km of gas pipeline. The toolkit's limits line up with that demand: LNG near-field dispersion and LNG flammable-limit distances are not covered, and there is no pipeline QRA.

## New functionality that could be built
Classes follow `docs/FEATURE_GAP_ANALYSIS.md`.

| # | Functionality | Class | Inputs needed |
|---|---|---|---|
| F1 | Upcoming-project register (`project_register`): project, country, operator, scope, stage, key dates, source and grade, last checked | Build now | Project facts with sources (rows P1 to P13 above are the first entries); a refresh routine |
| F2 | Study-trigger rules: from a project's stage and dates, list the studies due and their window | Build now | The stage-to-study table (from the lifecycle plan); offsets in months are inputs, none coded; operator-specific rules need N1 |
| F3 | Study-demand roll-up per quarter against team capacity, using the `schedule` load | Build now | Effort per study type (hours per node or P&ID) from company records; team capacity |
| F4 | Gulf bid mechanics in `tender_register`: document-purchase window, registration status, bond and validity, local-content status | Build now | Per-tender dates and amounts |
| F5 | Eligibility checker against a reference register | Build now | The reference register; each tender's criteria |
| F6 | Bid compliance matrix | Build now | Each tender's requirement list |
| F7 | WBS templates by study type: HAZOP revalidation, SIL for new SIFs, EERA, FERA | Build now | Structure only; effort is an input |
| F8 | P&ID register to HAZOP nodes to WBS | Build now | Client P&ID registers |
| F9 | Gulf QRA criteria set and contour-confinement check | Needs information | Operator or regulator criteria (not found), site boundary and land-use data |
| F10 | PSV staggered set-point review | Needs information | API 520 and 521 text |
| F11 | Risk-based inspection screening | Needs information | API RP 580 and 581, SAEP-343 text |
| F12 | Pipeline QRA screening for long gas lines (P5) | Needs information | Pipeline-assessment standards, failure-frequency data, route and population data |
| F13 | LNG consequence extensions: spill, pool fire and vapour dispersion near field (P1, P3, P7) | Needs information | A read, open method source for LNG spill and dispersion; the repo lists none as implemented |
| F14 | Hydrogen and ammonia quantitative consequences (Oman hydrogen programme) | Needs information | Open method sources; HyRAM+ is GPL and stays an external tool |
| F15 | Operator standards embedded as rules | Protected | Confidential; obtained only through registration or contracts |

## Schedule
Produced with `python3 -m process_safety tool schedule docs/plans/me_build_plan.json`; input in [docs/plans/me_build_plan.json](plans/me_build_plan.json). **Every duration is a planning assumption** by the author of this plan, to be replaced by the build team's own. One developer and one domain reviewer, Monday to Friday, no holidays entered (so 25 December and 1 January count as working days). The tool's checks pass and it reports no overload. Total: 67 working days, 16 Nov 2026 to 17 Feb 2027.

| Block | Activities | Start | Finish |
|---|---|---|---|
| Spec and rules | S1 spec, S2 read lifecycle rules and operator sources | 16 Nov 2026 | 24 Nov 2026 |
| A: register and triggers (F1 to F3) | A1 register, A2 trigger rules, A3 demand roll-up, A4 wiring and scenarios, A5 docs and gates; R1 domain review | 19 Nov 2026 | 10 Dec 2026 |
| B: bid tools (F4 to F6) | B1 mechanics, B2 eligibility, B3 compliance matrix, B4 wiring | 11 Dec 2026 | 29 Dec 2026 |
| C: study templates (F7, F8) | C1 WBS templates, C2 P&ID to WBS, C3 gates | 30 Dec 2026 | 12 Jan 2027 |
| Build-now scope complete | Milestone | 13 Jan 2027 | 13 Jan 2027 |
| Gated: inputs gate | G0, a placeholder date of 4 Jan 2027, not a forecast | 4 Jan 2027 | 4 Jan 2027 |
| Gated: F9, F10, F11, F12 | G1 criteria set, G2 PSV review, G3 RBI screening, G4 pipeline QRA screening | 13 Jan 2027 | 16 Feb 2027 |

The critical path is the developer chain. F13 and F14 are not scheduled: they wait on method sources that have not been found.

## Inputs needed, by supplier
| From | Inputs | Items |
|---|---|---|
| Project facts | A maintained list of projects with stage, dates and sources, refreshed on a routine | F1, F2 |
| Company records | Hours per study type; team capacity; reference register; registration and certificate status | F3, F4, F5 |
| Tender packages | Requirement lists and dates for each tender | F4, F5, F6 |
| Operators and regulators | Criteria, operator standards, procedures (not public) | F2 (operator rules), F9, F15 |
| Paywalled standards | API 520, 521, 580, 581; pipeline-assessment standards | F10, F11, F12 |
| Open method sources to find | LNG spill and dispersion; hydrogen and ammonia consequence methods | F13, F14 |

## Not checked
Current construction status of P2, P4, P6 and P9; 2026 status of Jafurah and the Master Gas System; any Kuwait, Bahrain or Iraq project beyond the items listed; any tender notices for the studies above; the PDF of the KIPIC plan; how much of each project's safety study work is already complete or placed; the build team's real estimates.

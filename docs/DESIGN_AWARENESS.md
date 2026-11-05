# Process safety awareness for design: review steps and incidents that lead to design choices

One page for a design team: which process safety review (PSR) step asks which question, what design choice it forces, and
which part of this toolkit gives the first-pass number. Incident rows come from `docs/SECTORS_AND_LESSONS.md` (public investigation
material, summarised, **not all reports were read**: verify against the reports before quoting). Commands are written with a `cmd:` prefix and
a test checks each one exists. Everything here is screening support, not a safety case.

## 1. Review steps in the order a design meets them

| Step | Question it asks | Typical design choice it drives | Toolkit |
|---|---|---|---|
| 1. Concept / inherent safety | Can the hazard be removed, reduced, substituted or moderated before adding protection? | smaller inventory, lower pressure or temperature, less hazardous material, simpler layout | `cmd:seveso`, `cmd:psm-check`, `cmd:rmp-check`, `cmd:lpg`, `cmd:lng` |
| 2. Regulatory screen | Which regimes apply (Seveso, OSHA PSM, EPA RMP, pipeline rules)? | design basis documents, safety report, PHA cadence | `cmd:seveso`, `cmd:psm-check`, `cmd:psm-due`, `cmd:rmp-check`, `cmd:pipeline` |
| 3. HAZID | What can go wrong, where, with what consequence class? | list of major accident scenarios and the loss-of-containment register | `cmd:hazop-csv`, `cmd:qra` (hazid) |
| 4. Consequence screening | How far do fire, explosion and toxic effects reach? | plot layout, separation, building siting, escape routes | `cmd:pool-fire`, `cmd:flame-flux`, `cmd:fireball`, `cmd:plume`, `cmd:flare` |
| 5. HAZOP / what-if | What deviations from design intent can occur and are they protected? | added instruments, relief paths, interlocks, procedures | `cmd:hazop-csv`, `cmd:tool` (pha) |
| 6. Relief and flare design | What is the worst credible overpressure and does the valve and header handle it? | PSV area and orifice, two-phase sizing, inlet and outlet piping, flare header and KO drum | `cmd:relief-gas`, `cmd:relief-steam`, `cmd:relief-liquid`, `cmd:relief-fire`, `cmd:twophase`, `cmd:tank-normal`, `cmd:tank-fire` |
| 7. Fire protection and depressuring | Does the vessel survive the fire long enough for relief or blowdown to work? | blowdown valve, passive fire protection, fire water, steel section | `cmd:vapour-fire`, `cmd:depressure`, `cmd:blowdown`, `cmd:steel-fire` |
| 8. LOPA and SIL | How much risk reduction does each scenario need and who provides it? | safety instrumented function with a target SIL, architecture, proof-test interval | `cmd:lopa`, `cmd:pfd`, `cmd:tool` (sif) |
| 9. QRA and ALARP | Is the individual and societal risk tolerable, and what mitigation is worth its cost? | siting changes, occupied-building rating, mitigation package | `cmd:qra`, `cmd:tool` (bowtie) |
| 10. Detection and emergency response | Will a release be seen in time and who responds? | detector layout, voting, emergency zones | `cmd:tool` (fg), `cmd:qra` (emergency) |
| 11. Electrical, mechanical and occupational | Ignition sources, arc flash, earthing, noise, guarding | equipment protection, relay settings, earthing, guard distance | `cmd:arc-flash`, `cmd:idmt`, `cmd:earthing`, `cmd:noise`, `cmd:safeguard` |
| 12. PSSR, MOC and revalidation | Is it built as designed, and does every change and the five-year cycle get re-reviewed? | commissioning checklist, change control, revalidation dates | `cmd:psm-due`, `cmd:tool` (pha) |

## 2. Design choices the toolkit's own results illustrate

These are from `docs/USE_CASES.md` (real runs, screening inputs):

* **Relief is not protection.** A J-orifice fire-case valve held pressure at about 1503 kPag but the 20 mm wall vessel still ruptured at 700 s; opening a blowdown valve at 60 s avoided rupture. Design choice: depressuring or passive fire protection in addition to the valve (step 7).
* **Flashing changes the valve.** The same 8 kg/s needs 657, 977 or 1611 mm2 as omega goes 2, 6, 20. Design choice: decide the fluid state at relief first, size for two-phase if the liquid can flash (step 6).
* **Test interval is a design variable.** A 1oo2 pair gave PFDavg 5.3e-4 with a yearly proof test and 2.1e-3 with a three-yearly one, one SIL band lost. Design choice: access for online testing and the interval written into the safety requirement (step 8).
* **Models disagree; show both.** Point-source and solid-flame pool-fire radiation differ about four times in the far field. Design choice: siting uses the conservative model until a specialist picks one (step 4).
* **Applicability decides the paperwork.** 700 kg chlorine is above the OSHA PSM threshold and 1200 kg above the RMP threshold. Design choice: PSM elements and an RMP are scoped at concept, not after detailed design (steps 1 and 2).

## 3. Incident instances and the design question each should raise

| Incident (as summarised in `SECTORS_AND_LESSONS.md`) | What went wrong | Design / review step to ask at | Toolkit |
|---|---|---|---|
| LG Polymers styrene tank, Visakhapatnam, India, 2020 | polymerisation runaway in an idle tank; inhibitor depletion; one local temperature sensor; no HAZOP or pre-start review after lockdown | steps 5, 8, 12: independent temperature monitoring and alarm, venting for runaway, pre-start review after long idle | `reaction_hazard`, `thermal_runaway`, `tank_venting`, `psm` |
| Husky Superior refinery FCC explosion, 2018 | transient operations without explicit hazard analysis | steps 5 and 12: analyse start-up, shutdown and abnormal modes, not only steady state | `hazop`, `psm`, `plant_units` |
| Tesoro Anacortes, 2010 | high-temperature hydrogen attack not assessed | steps 5 and 12: damage mechanisms in the mechanical integrity scope | `psm`, `hazop` |
| Buncefield 2005, IOC Jaipur 2009, BP Texas City 2005 (reports not fetched) | overfill leading to a large vapour release and explosion; blowdown to atmosphere | steps 4, 6, 8: independent high-level protection, blowdown to a closed system, siting of occupied buildings | `overfill`, `separator`, `explosion`, `flare_system`, `qra.buildings` |
| BP Products refinery, Oregon, Ohio, Sept 2022 (as summarised by [JPT](https://jpt.spe.org/investigators-find-operating-training-deficiencies-contributed-to-fatal-refinery-explosion); CSB report not read) | two workers fatally burned: flow-control valves opened to relieve a rising level in a fuel gas mix drum let naphtha into the fuel gas system, and a vapour cloud ignited. OSHA cited 10 serious PSM violations, including no documented PSV design for an overpressure scenario, overfill hazards not addressed, a PHA inaccurate on the level indicator safeguard, and a control-board screen that loaded slowly | steps 5, 6, 8: document the PSV basis for each overpressure case, protect against overfill independently of the operator, check the PHA against the as-built safeguards, design the control room display for upset conditions | `relief`, `overfill`, `separator`, `hazop`, `psm` |

Rows for other incidents are not added until their investigation reports are read.

## 5. External material read on 2026-11-06

| Source | Status | What it adds for design |
|---|---|---|
| [National Law Review, Van Ness Feldman: PHMSA proposes comprehensive revisions to LNG safety regulations](https://natlawreview.com/article/phmsa-proposes-comprehensive-revisions-safety-regulations-lng-facilities) (2 Nov 2026) | read in full (a law-firm summary of the NPRM, not the NPRM text) | PHMSA released a proposed rule on 28 Oct 2026 to rewrite 49 CFR 193 around NFPA 59A-2026 (replacing the 2001 and 2006 editions); comments are due 4 Jan 2027. It is **proposed, not final**. Siting would follow NFPA 59A chapter 5 plus new hazard-analysis and exclusion-zone sections, with an optional QRA route (chapter 19), and would apply to facilities designed or significantly altered five years after a final rule. A risk-based operations and maintenance option (subpart F) would borrow from OSHA PSM: PHA, pre-startup review, mechanical integrity, management of change, audits. |
| [Sigma-HSE, why early-stage design decisions are critical](https://sigma-hse.com/news-insights/early-stage-design-decisions/) (27 Nov 2025) | read in full; a consultancy article, its statistics are quoted from it and not checked | Bench work masks thermal hazards; scale-up is where runaway shows. Design choice: thermal screening and calorimetry before scale-up, check cooling, mixing and dosing against loss-of-cooling and misdosing, and keep dust, vapour and gas explosion evidence in the safety management file. It cites the 2008 Imperial Sugar explosion as a dust example (not read here). |
| [SPE In Focus: Process Safety](https://www.spe.org/en/focus/process-safety/) and the [JPT ADNOC article](https://jpt.spe.org/approach-aims-to-prevent-process-safety-incidents) (10 Oct 2023) | index page and one article read | ADNOC's PSM framework has 15 elements. A review of more than 50 of its process safety events, mapped to the CCPS elements, found inadequate identification of worksite or job hazards was the top root cause (26%), and 55% of causes fell under hazard identification and risk analysis, auditing, and asset integrity and reliability (SPE paper 210971; the paper itself was not read). Design implication: invest the most review effort in hazard identification (steps 3 and 5). |
| [AFPM process safety page](https://www.afpm.org/issues/safety-health/process-safety) | page and one statement read; industry-association position, not neutral | US refiners and petrochemical makers state they are regulated by OSHA PSM and EPA RMP and audited regularly. AFPM backs EPA's February 2026 RMP revision proposal (see below). Its issue list names alkylation, FCC and cybersecurity as process-safety topics. |
| EPA RMP revision proposal, "Common Sense Approach to Chemical Accident Prevention" (published 24 Feb 2026; comments extended to 11 May 2026) | summary from law-firm and advocacy sources via [AFPM](https://www.afpm.org/newsroom/news/afpm-revised-rmp-would-set-strong-standard-safety-enable-safety-innovation-0) and search; Federal Register text not read | reported to roll back parts of the 2024 rule: safer technology and alternatives analysis kept only for newly covered Program 3 processes, natural-hazard and power-loss evaluation requirements removed, third-party audits rescinded or narrowed. Proposed, final rule not confirmed. The toolkit's `rmp` command uses the substance lists and worst-case criteria, which these reports do not describe as changing; check the docket (EPA-HQ-OLEM-2025-0313) before relying on any prevention-programme assumption. |
| [PSM News (James Klein)](https://psmnews.com/) | home page read only | author's blog with publications list; some posts had editorial help from an AI tool, per its own disclaimer. Low weight; nothing used. |
| [Sigma-HSE news and insights index](https://sigma-hse.com/news-insights/) | titles only; other articles not read | Topic list worth reading next: startup and shutdown hazards, management of change ("the stealth of small changes"), a basis of safety that survives scale-up, "compliant does not mean safe". |
| [CCPS Process Safety Beacon](https://ccps.aiche.org/process-safety-beacon) | **not read**: the site returned a bot-check page (HTTP 403) | No bypass attempted. Beacon issues can be added if you supply the PDFs. |

What this changes in the toolkit's advice:
* **LNG users:** `lng` and `docs/SECTORS_AND_LESSONS.md` cite the current 49 CFR 193 text (for example 193.2181 impoundment). If the proposal is finalised, section numbers and the governing NFPA edition change, and impoundment moves into the incorporated NFPA 59A chapter 13 and new supplementary sections. Treat the `lng` numbers as the current-rule screen and re-check after the final rule.
* **Reactive chemistry:** the Sigma-HSE point is the same one `reaction_hazard` and `thermal_runaway` encode (MTSR against decomposition onset). Step 1 and step 5 of section 1 should carry calorimetry data as an input, not an assumption.

## 4. Habits that keep design choices defensible

* State the standard and edition, and what was not read, beside every number (the toolkit refuses defaults where a vendor or standard value governs).
* Run range checks on, and read warnings (`docs/RANGES.md`).
* Record the model's limit with the result (`cmd:coverage` lists what is not implemented).
* Keep a decision log of the alternatives rejected, as `CHANGELOG.md` does.

# Feature gap analysis: what can be built, what needs more information, what stays protected

Written 2026-11-09. Inputs: the toolkit's own "Not implemented" list in `README.md`, the capability map in `docs/SIMULATION_TOOLS.md`, and the licence texts of the open tools, read today (ledger below). This is a planning document: **nothing here was built or run**, and the licence readings are mine, not legal advice.

## How features are sorted
| Class | Meaning | Test applied |
|---|---|---|
| **Build now** | The method can be implemented in stdlib Python with tests on identities | A source the repo has already read, or open-access material, or no external constant is needed because every number is an input |
| **Needs information** | The method is known but a source, dataset or input is missing | The source is paywalled or unofficial, the data does not exist publicly, or the client or study must supply it |
| **Protected** | Cannot be copied into this MIT, dependency-free repo | Copyleft source, proprietary model or database, copyrighted standard text, company practice, or a draft marked not for reproduction |

Rules behind the sort come from `CLAUDE.md`: every number needs a source; a paywalled value is made an input or the topic is marked not implemented; licensed standard text and company practices are never committed; optional libraries live only in `tests/crosscheck/`.

## Licence ledger (texts read 2026-11-09 unless noted)
| Tool | Licence text | What it allows this toolkit |
|---|---|---|
| HyRAM+ (Sandia) | GPL-3.0 (GitHub metadata) | external tool or cross-check run as a separate program; no copying of code into the MIT tree |
| SCRAM (fault and event trees) | GPL-3.0 (GitHub metadata); last push 2023-09-19 | same; also inactive |
| DWSIM | GPL-3.0 (stated in `docs/SIMULATION_TOOLS.md`, not re-read); repository archived | same |
| OpenFOAM | GPL-3.0 or later (COPYING, first lines read) | same; CFD is out of scope anyway |
| JuPedSim | LGPL-3.0 or later (LICENSE, first lines read) | may be called as a library from `tests/crosscheck/`; its code is not copied |
| FDS (NIST) | short NIST "public service" notice: use, copy, modify and distribute, keep the notice, mark modified works (first lines read only) | permissive with conditions; still a Fortran LES code, so an external check, not a port |
| thermopack | Apache-2.0 (header read) | permissive; optional cross-check library |
| pandapipes | BSD-style text, Fraunhofer IEE and University of Kassel (first lines read; clause list not checked) | optional cross-check library |
| Cantera | BSD-style text (first lines read; clause list not checked) | optional cross-check library |
| `fluids`, `ht`, `thermo`, `chemicals` | MIT (GitHub metadata) | optional cross-check libraries |
| BowtieRisk.jl | MPL-2.0 (from `docs/RELATED_PROJECTS.md`) | file-level copyleft; read the terms before reusing anything |
| Phast, Safeti, FLACS, exSILentia, BowTieXP, FaultTree+, PHAWorks, SuperChems, Pathfinder, buildingEXODUS, STEPS, PyroSim, HYSYS, Aspen Plus | proprietary (vendor products) | published theory documents only; no code or data |

Working rule: published equations may be implemented from the paper or report. Do not read copyleft source and re-type it; if a method exists only in GPL code, find the paper behind it first.

## Comparison: feature areas across the tools
| Feature area | Seen in | Toolkit today | Class |
|---|---|---|---|
| Near-horizontal vapour jet fire (Johnson correlations) | Phast | `jet_flame` says "not implemented", Chamberlain and Cook only | Build now |
| Single-phase flare network solver (tree and looped) | Aspen Flare System Analyzer | `flare_system` aggregates loads and sizes the header; `hydraulics` has isothermal compressible lines | Build now (single phase); multiphase needs a located source |
| Barrier health tracking (test dates, overdue, degraded) | BowTieXP | `bowtie` quantifies barriers but does not track them | Build now |
| Two-phase release feeding the QRA consequence step | Phast, Safeti | `expansion` and `twophase` exist but are not wired into `qra` | Build now (integration, no new source) |
| Cross-check harness against open tools | all | `tests/crosscheck/` for some libraries | Build now |
| Pool fire with wind tilt, drag and spreading pool | Phast | `pool_fire` has no wind or spreading | Locate a source first, then build |
| Fireball model per the public DNV document, alongside the Roberts-style one | Phast | `fireball` is the Roberts-style model | Locate and read the DNV document (already cited), then build |
| Egress with merging flows and stairs | Pathfinder, EXODUS, STEPS | `egress` is RSET against ASET arithmetic | Structure is buildable with inputs; coefficients need a read source |
| Domino escalation, LNG rollover and rapid phase transition, boilover | Phast, literature | qualitative entries in `scenario_library` only | Locate sources first |
| SIL systematic capability and proof-test coverage | exSILentia | not in `sil_lifecycle` | Needs information (IEC 61508/61511 text) |
| Multi-energy and Baker-Strehlow vapour cloud explosions | Phast, FLACS | `explosion` is TNT equivalence only | Needs information: the repo found no open blast curves |
| BLEVE blast and fragments | Phast | `fireball` only | Needs information |
| Hazardous-area extents | exSILentia-class suites, ATEX tools | duration rule only | Needs information (IEC 60079-10-1 and EI 15 are paywalled) |
| Layout and separation distances | OISD tools | none | Needs information (official OISD-STD-118 edition) |
| Dust explosion vent sizing | NFPA 68 tools | KSt arithmetic only | Needs information (NFPA 68/660) |
| Clean-agent room design, arc flash by IEEE 1584, pulsation studies | vendor tools | not implemented | Needs information (NFPA 2001, IEEE 1584, API 618/674/688) |
| Pump, compressor, valve and flange generic frequencies | QRA suites | none | Needs information (no verified public rows) |
| Runaway-reaction relief (DIERS) | SuperChems | none | Needs information; the DIERS database is protected |
| Dynamic flowsheet simulation, operator training | HYSYS Dynamics | none | Protected in effect: vendor product; open tools exist (DWSIM GPL, NeqSim, OpenModelica) |
| 3D CFD fire and explosion | FLACS, FDS, PyroSim | none | Out of scope; FDS and OpenFOAM stay external |
| Agent-based pedestrian dynamics | Pathfinder, EXODUS, JuPedSim | none | Protected or out of scope: LGPL library, not stdlib |
| Certified SIL, certified QRA output | exSILentia, Safeti | screening only | Protected: certification belongs to the vendor and assessor |
| Vendor databases (SuperChems properties, generic failure data, IPL libraries) | many | inputs only | Protected |

## A. Build now (details)
| # | Feature | Extends | Source status | Tests on identities |
|---|---|---|---|---|
| A1 | Johnson near-horizontal vapour jet fire | `jet_flame` | DNV jet-fire theory document, already read for Chamberlain and Cook; the Johnson section has **not** been read for this | reduces to the vertical case at the limit angle; length monotone in release rate; continuous at the switch between models |
| A2 | Single-phase flare network: Newton or Hardy-Cross solve of looped compressible headers, with allowable Mach and back-pressure as inputs | `flare_system`, `hydraulics` | Darcy-Weisbach and isothermal compressible flow are already in `hydraulics`; API 521 limits stay inputs | mass balance at every node; loop pressure drops sum to zero; one-pipe case equals `hydraulics` |
| A3 | Barrier health: test interval, last test, overdue flag, degraded-barrier effect on top-event frequency | `bowtie` | no external constant: dates and credits are inputs | frequency monotone in barrier failure probability; overdue barrier never improves the result |
| A4 | Wire `expansion` and `twophase` into the QRA release step | `qra.effects` | existing modules and their sources | airborne plus rainout equals the total release; one-phase limits equal the current result |
| A5 | Open-tool cross-checks: `fluids`, `thermo`, Cantera, pandapipes, thermopack, HydDown (MIT per `docs/SIMULATION_TOOLS.md`), SCRAM as a separate process for one published fault tree | `tests/crosscheck/` | licences above | agreement within a stated tolerance, never replacing the identity tests |
| A6 | Locate-first group: pool fire wind and spreading, DNV fireball, domino escalation, LNG rollover, boilover, egress coefficients | various | no source in hand yet; step one is finding and reading an open-access method document, recording title and clause as `CLAUDE.md` requires | defined once the method is read |

## B. Needs additional information
| Feature | What is missing | Who or what supplies it |
|---|---|---|
| Multi-energy / Baker-Strehlow blast | the repo's search found no open source for the blast curves | TNO Yellow Book or the Baker-Strehlow papers, if obtainable and read; otherwise stays input-only |
| BLEVE blast and fragments | no verified open correlation | open-access papers to be located and read; the flashing-liquid energy needs a verified route |
| Hazardous-area extents | IEC 60079-10-1 and EI 15 are paywalled | purchased copy read by the user's organisation |
| Layout distances | only unofficial OISD-STD-118 copies were found; `docs/DATA_REGISTER.md` section E records the official purchase route | purchased current edition |
| Dust explosion vent sizing | NFPA 68/660 paywalled | purchased copy |
| SIL systematic capability, proof-test coverage | IEC 61508/61511 text paywalled | purchased copy or a read open derivation |
| Clean-agent design, IEEE 1584 arc flash, API 618/674/688 | standards paywalled | purchased copies; vendor calculation governs clean agents |
| Generic frequencies for pumps, compressors, valves, flanges | no verified public rows | study-specific data or a licensed database |
| DIERS runaway relief | method literature to be located; data are lab-specific | calorimetry from the client |
| Dense-phase CO2 decompression | equation of state and fracture data | open EOS source to be read, plus pipe data |
| Barrier audit integration | client systems | client |

## C. Stays protected
| Item | Why | What to do instead |
|---|---|---|
| GPL code (HyRAM+, SCRAM, DWSIM, OpenFOAM) | cannot join an MIT tree without relicensing | run as separate programs for cross-checks; implement published equations independently |
| LGPL JuPedSim | LGPL and not stdlib | optional call from `tests/crosscheck/` only |
| Phast, Safeti, FLACS, exSILentia, BowTieXP, FaultTree+, PHAWorks, SuperChems, Pathfinder, EXODUS, STEPS, HYSYS, Aspen Plus | proprietary code, tuned parameter sets and databases | implement only from published theory documents; the override hook accepts their results |
| Text of NFPA, IEC, API, ISA, ISO standards | copyright | cite clause and edition; code the equation only after reading it |
| Company design practices (Shell DEPs and similar) | `CONTRIBUTING.md` hard rule | none |
| OISD drafts marked not for reproduction | the 2026-11-07 changelog entries say extracted text stays in the gitignored `standards_private/` | keep private |
| SIL and QRA certification | the vendor and the independent assessor own it | the toolkit keeps its screening disclaimer |
| FDS-class CFD | licence is permissive, but it is a large Fortran code | external check only |

## Suggested order
1. A4 and A5 first: no new source, and they make later work checkable.
2. A1 after reading the Johnson section; A2 and A3 next.
3. A6 sources, then B items, as the user obtains the paywalled standards.

## Not checked
The pool-fire theory document in DNV's public folder was not located. Vadere's repository and AERMOD's public-domain status remain unconfirmed (`docs/SIMULATION_TOOLS.md`). The `coverage` command's topic map still disagrees with the README module table in places (README note, 2026-11-07).

# From process flow to safe operation: a structured plan

How a project team typically goes from a process idea to a plant that is designed and run safely, and where the safety studies feed back into the design. Written as a checklist-style plan: for each stage, the inputs, the work, the deliverables, the gate, the safety questions that drive design tweaks, and what this toolkit already does for it.

**Basis.** (1) The order of work seen in the folder structure of an operator's FEED package (names only; the contents were not read): process flow schemes, heat and material balance, process engineering flow schemes, HAZOP, safeguarding flow schemes, cause-and-effect, process control network scope, QRA, surge analysis, boil-off calculations, double-block-and-bleed philosophy, design-practice gap analysis, technical queries. (2) A published flowsheet simulation paper (hierarchical conceptual design, fluid package choice, cross-simulator comparison). (3) The toolkit's own refinery design notes (design element to standards map). (4) The public sources in `docs/LITERATURE.md`. Abbreviation expansions for PFS, PEFS and PSFS (process flow scheme; process engineering flow scheme, i.e. the P&ID-level document; process safeguarding flow scheme) are inferred from common usage and the folder names: confirm them against your company's document control terms. Company standards govern.

```
 0 Concept / FEL1 --> 1 PFS / PFD --> 2 HMB simulation --> 3 Equipment design --> 4 PEFS (P&ID) + control scope
     design basis        flow scheme      cases, margins       datasheets, sizing       isolation, relief devices,
     class 5 cost                                                                          instruments, PCN, C&E
                                                                                               |
 8 Operate safely  <-- 7 Build / commission <-- 6 Recommendations <-- 5 Safety studies <--------+
   envelope, MOC,        PSSR, proof tests,       rank, ALARP cost,     HAZID, HAZOP, LOPA/SIL,
   learning loop         training                 MOC, update 1-4       relief/flare, QRA, PSFS, C&E
        ^______________________________ revalidation, incident learning _______________________________|
```

## Stage 0: Concept and design basis (FEL 1)
| | |
|---|---|
| Inputs | feed and product specifications, capacity and turndown, site and climate, utilities, applicable laws and company standards, licensor options |
| Work | choose the process route by a hierarchy of decisions (input-output structure, recycle, separation, heat integration); screen inherent safety (smaller inventory, milder conditions, safer material); concept cost (class 5) and economic potential |
| Deliverables | design basis memorandum, concept block diagram, option comparison, concept estimate with range |
| Gate | option selected; regulatory screen done (which regimes apply); main hazards listed |
| Safety questions | Can the hazard be removed or reduced? Which regime applies (Seveso, PSM, RMP, MSIHC)? Is any reactive or toxic material present? |
| Toolkit | `seveso`, `psm-check`, `rmp-check`, `lpg`, `lng`, `lng_cost` / `tool lngcost`, `docs/REGULATORY_LANDSCAPE.md` |

## Stage 1: Process flow scheme (PFS / PFD)
| | |
|---|---|
| Work | main equipment, stream numbering, normal operating conditions, control philosophy outline, utility interfaces, battery limits |
| Deliverables | PFS with stream table skeleton, equipment list, preliminary operating modes (start-up, normal, turndown, upset) |
| Gate | frozen enough to simulate; equipment list agreed |
| Toolkit | ingest as plain streams and units (planned `plant` ingest); `docs/WORKFLOW.md` shows the data each unit needs |

## Stage 2: Heat and material balance (HMB) simulation
| | |
|---|---|
| Work | build the flowsheet in a simulator; choose and justify the fluid package; run normal, minimum, maximum (design margin) and upset cases; close mass and energy balances; compare against a second package or data where results are sensitive |
| Deliverables | HMB stream tables for every case, utility balance, simulator model under revision control |
| Gate | balances close, key results cross-checked, case list agreed with the safety team |
| Safety questions | Do the maximum and upset cases change phase, pressure or temperature of any stream? Are any streams flammable or toxic at what inventory? Where does a high-pressure stream meet low-pressure equipment? |
| Evidence to expect | different fluid packages can differ materially: a published example comparing two commercial simulators on the same amine CO2 removal flowsheet reported an 18.7% deviation on treated-gas CO2, attributed to fluid package and pressure differences |
| Toolkit | `fluid-data`, `docs/SIMULATION_TOOLS.md` (open simulators), cross-check approach in `docs/VALIDATION.md`; HMB ingest and scenario generation are being added |

## Stage 3: Equipment design
| | |
|---|---|
| Work | size vessels, columns, exchangers, pumps, compressors; set design pressure and temperature (operating plus company margin), MDMT, materials and corrosion allowance; line sizing and surge analysis; boil-off and fuel-gas balances where relevant |
| Deliverables | equipment datasheets, line list basis, design pressure / temperature philosophy |
| Gate | datasheets issued for vendor enquiry; design margins documented |
| Safety questions | Design pressure against the highest pressure any connected source can deliver; MDMT against auto-refrigeration on depressuring; liquid-full cases and thermal expansion |
| Toolkit | `vessel_mech`, `hydraulics`, `separator`, `depressuring` (MDMT screen), `props` |

## Stage 4: Process engineering flow schemes (P&ID level) and control scope
| | |
|---|---|
| Work | add valves, instruments, relief devices and their discharge routes, isolation philosophy (including double block and bleed), drains and vents, control loops, interlocks and shutdown levels; define the process control network scope, cause-and-effect matrix and alarm philosophy |
| Deliverables | PEFS, line list, instrument index, relief device register, cause-and-effect, I/O list, control narrative |
| Gate | frozen for HAZOP |
| Safety questions | Is every closed-in volume protected? Where does each relief device discharge? Which functions are in the control system and which in an independent safety system? |
| Toolkit | `relief`, `relief_piping`, `flare_system`, `sil_lifecycle`, `fg_mapping`; P&ID register and Proteus XML ingest are being added |

## Stage 5: Safety studies
Run in this order because each needs the previous one's output.
| Study | Question | Input from | Toolkit |
|---|---|---|---|
| HAZID | What major hazards exist and how big? | stages 0-2 | `hazop-csv` (hazid), `qra hazid` |
| HAZOP | What deviations can occur and are they protected? | PEFS, HMB | `hazop`, `pha` (worksheets, SIMOPS) |
| Relief, flare and blowdown | Does every overpressure scenario have a sized, routed relief path? | HMB, datasheets, PEFS | `relief`, `twophase`, `vapour_fire`, `depressuring`, `flare_system`, `tool workflow` |
| LOPA and SIL | How much risk reduction is needed and who provides it? | HAZOP scenarios | `lopa`, `pfd`, `sil_lifecycle`, `tool sif` |
| QRA and siting | Is the risk tolerable and ALARP? | layout, inventories, HMB | `qra`, `tool bowtie` |
| Fire and gas, fire protection | Detection coverage, passive and active protection | layout, hazards | `fg_mapping`, `structural_fire`, `fire_water` |
| Safeguarding review (PSFS) | Does every safeguard in the study appear on the drawings and in cause-and-effect, and is it independent? | HAZOP, LOPA, PEFS | `recommendation_catalog` (types), `docs/RECOMMENDATIONS_CATALOG.md` |
| Standards gap analysis | Where does the design fall short of company and national standards? | all of the above | `standards` (coverage map), OISD list |
Deliverable of the stage: a register of findings and recommendations, each with its scenario, the numbers behind it, and the proposed response.

## Stage 6: Recommendations and design tweaks
| Finding | Typical tweak (try these in this order: remove, reduce, protect, procedure) | Cost scope in the toolkit |
|---|---|---|
| Relief load higher than installed capacity | reduce the load (inventory, control philosophy, HIPPS), then resize or add devices, then fix inlet and outlet piping | `device` |
| Vapour-filled vessel fails in a fire | depressuring, passive fire protection, remote isolation to cut inventory | `device`, mechanical |
| Short time to overfill | independent high-level protection with trip | `sensors`, `pcn` |
| High/low pressure interface | raise downstream design pressure or add relief/check valves | `device` |
| MDMT / cold depressuring | materials, depressuring rate limit, warm-up procedure | mechanical, `none` |
| Detector gaps | add detectors with voting and executive actions | `sensors`, `pcn` |
| Relief discharge or header limits | reroute, add header or knock-out drum | `reroute` |
Process: rank by risk reduction and cost (ALARP cost-benefit is one input; legal and good-practice items are not optional), assign owners, run management of change, update stages 1-4 and re-run the affected studies (iterate until no open high-priority items). Toolkit: `tool workflow`, `tool recs`, `recommendation_cost`, `shutdown_risk`, `docs/RECOMMENDATION_COSTS.md`.

## Stage 7: Build, commission and hand over
Procurement and fabrication to the datasheets; SIL verification with vendor data; factory and site acceptance tests for control and safety systems; pre-startup safety review (PSSR) with all high-priority recommendations closed or formally risk-accepted; proof-test and inspection plans loaded; operating procedures and training complete; as-built drawings match the safeguards the studies relied on. Toolkit: `psm` (PSSR, due dates), `pha` worksheets, `docs/DESIGN_AWARENESS.md`.

## Stage 8: Operate safely
| Element | What it means | Toolkit |
|---|---|---|
| Safe operating envelope | limits for pressure, temperature, level, composition with the consequence of exceeding each and the required response | `ranges` (input checks as a model), HMB cases |
| Safeguard integrity | proof tests and inspection at the intervals the studies assumed; bypass and override control | `sil`, `psm-due`, `pha` actions |
| Management of change | any change to process, equipment, procedures or safeguards reviewed first; small changes accumulate | `psm`, `pha` carry-forward |
| Transient modes | start-up, shutdown and abnormal modes analysed, not only steady state | `hazop`, `pha` (SIMOPS) |
| Shutdowns and turnarounds | plan and risk the outage; protect safety-critical activities from schedule pressure | `shutdown_risk` |
| Learning loop | near misses, incidents and audits feed the next HAZOP revalidation (five-year cycle under OSHA PSM) | `docs/INCIDENTS.md`, `incidents`, `psm-due` |

## Governance across all stages
Document control and revision of the HMB, PEFS and study registers; a single owner for each recommendation; stage gates with named approvers; a technical query log; independent verification for safety-critical calculations; and a record of every assumption that rests on judgment (the toolkit's own ranges, factors and defaults are labelled for this reason).

## What the toolkit covers today, and what is being added
Covered: stages 0 (screening and concept cost), 2 (property data, cross-checks), 3 (selected sizing and MDMT screen), 5 (relief, SIL, QRA, fire and gas, worksheets), 6 (design tweaks, capex, opex, ALARP, shutdown merge), 8 (PSM dates, shutdown risk, incident learning). Being added: ingestion of PFS/HMB stream tables, P&ID registers (and Proteus XML) and PHA registers, automatic scenario generation from the HMB, and a catalogue of common recommendation types with the reasoning behind each. Not covered: detailed equipment design beyond the screens above, dynamic process simulation, network hydraulics for flare systems, operator training content.

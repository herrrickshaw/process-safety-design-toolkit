# Ingesting the plant data and explaining why studies recommend what they do

`python -m process_safety tool plant` reads what a project already has (a process flow scheme / HMB stream table, P&ID registers or a Proteus XML export, and a HAZOP/LOPA register), checks it, regenerates the scenarios a study would run, and reports **why** each recommendation type is expected, which of them your register already contains, and which it does not mention. It also drafts the input for `tool workflow`, so the cost and opex of the changes follow directly.

## What it reads
| Input | Content | Notes |
|---|---|---|
| `units`, `streams` | the PFS / PFD and HMB: unit tags, design pressure and temperature, MDMT, volumes; streams with phase, T, P, mass flow, molecular weight, k, density, components | numbers from your simulator export (`docs/SIMULATION_TOOLS.md`) |
| `lines`, `relief_devices`, `instruments`, `valves`, `exchangers` | P&ID level registers: line list, PSV/BDV register (orifice letter becomes area), instrument index with loop and voting, shutdown valves, HP/LP exchangers | CSV or inline JSON |
| `proteus_xml` | a ProteusXML (DEXPI) P&ID export, schema 4.2: equipment with design pressure/temperature, piping segments and connections, valves and relief devices, instrumentation functions | element names from the published XSD; tested on a synthetic file only; pressure basis is not in the file (gauge assumed); pyDEXPI is AGPL and is not used |
| `register` | the PHA register: id, node, deviation, cause, consequence, safeguards, recommendation, owner, status | CSV or inline |

PFS (process flow scheme), PEFS (process engineering flow scheme, P&ID level) and PSFS (process safeguarding flow scheme) are the document names used in some operators' FEED packages; here the PFS/HMB maps to `units` + `streams`, the PEFS to the registers, and the PSFS to the cross-check of safeguards against the register.

## What it does
1. **Checks:** references resolve; mass balance closes per unit; hazard flags from component names (EPA RMP lists).
2. **HMB scenarios** computed with the toolkit's models: blocked outlet (API 520 gas sizing), overfill (time to fill against operator response plus valve closure, times a safety factor of 2 that is a judgment), interface overpressure, tube rupture (10/13 rule and rupture flow), MDMT on depressuring, and fire (through `design_workflow`). A scenario that lacks an input says `cannot_assess` and lists what is missing; nothing is guessed.
3. **P&ID review rules** R1 to R7 (relief device missing, atmospheric discharge in flammable or toxic service, level only in the control system, single-sensor trip where SIL 2 is required, no detector, line rated above downstream equipment, no shutdown valve on a large flammable inventory).
4. **Rationale table:** per unit and recommendation type, every reason (from the drawings review and from the HMB) with its numbers, the usual response, the cost scope it maps to in `design_workflow`, and whether your register mentions the topic at that node.
5. **Register analysis:** each recommendation is classified into the catalogue (`docs/RECOMMENDATIONS_CATALOG.md`) and tallied; rows with a consequence but no safeguard and no recommendation are listed.
6. **Workflow skeleton:** units with device-type triggers, filled from the model, with the remaining inputs listed as todo.

## Worked example (illustrative plant: five streams, four units, a six-row register)
Triggered recommendation types: INTERFACE-DP 2, PSV-ADD 2, PSV-UPSIZE 2, DETECT 2, FLARE-LOAD 1, HLL-SIF 1, ISOLATION 1, MATERIAL 1. Your register's recommendation types: PSV-ADD 3, FLARE-LOAD 1, HLL-SIF 1, SIF-UPGRADE 1, INTERFACE-DP 1, FIRE-PROT 1, PROCEDURE 1. 6 triggered (unit, type) pairs are not mentioned in the register at their node.

| Unit | Recommendation type | Found by | In register | First reason |
|---|---|---|---|---|
| E-301 | Protect the high/low pressure interface | hmb | yes | HMB tube_rupture (gap): double-ended tube rupture sends 5.0 kg/s into the LP side: needs 522 mm2 against 0 mm2 installed (LP design 5,000 < 10/13 of HP 9,000 kPag) |
| E-301 | Add a pressure relief device | pid_review | yes | P&ID R1 (gap): E-301 (exchanger, design 9,000 kPag) has no relief device in the register |
| E-301 | Resize the relief device | hmb | no | HMB tube_rupture (gap): double-ended tube rupture sends 5.0 kg/s into the LP side: needs 522 mm2 against 0 mm2 installed (LP design 5,000 < 10/13 of HP 9,000 kPag) |
| T-201 | Add gas, fire or flame detection | pid_review | no | P&ID R5 (review): T-201 is in flammable service and no gas or fire detector is registered against it |
| T-201 | Check flare/vent header capacity or route relief to a safe location | pid_review | no | P&ID R2 (review): PSV-201 on T-201 discharges to atmosphere in flammable service (Butane, Propane) |
| T-201 | Independent high-level protection (alarm and trip) | hmb, pid_review | yes | P&ID R3 (review): T-201 receives liquid and level is measured only in the control system (LT-201): no independent high-level trip registered |
| T-201 | Remote / emergency isolation of inventory | pid_review | no | P&ID R7 (review): T-201 holds 45,000 kg flammable (limit 20,000) and no shutdown valve is registered |
| V-101 | Materials, MDMT, damage mechanisms and inspection | hmb | no | HMB mdmt (gap): depressuring 1,400 kPag gas to atmosphere cools it (ideal-gas isentropic lower bound) to -105 C against an MDMT of -20 C: check the metal temperature prop |
| V-101 | Resize the relief device | hmb | yes | HMB blocked_outlet (gap): blocked outlet sends 50,000 kg/h to the relief device: needs 4,398 mm2 (Q orifice) at 1,751 kPa abs against 830 mm2 installed |
| V-102 | Add gas, fire or flame detection | pid_review | no | P&ID R5 (review): V-102 is in flammable service and no gas or fire detector is registered against it |
| V-102 | Protect the high/low pressure interface | hmb, pid_review | yes | P&ID R6 (gap): line L-2001 is rated 1,700 kPag but V-102 is designed for 700 kPag and has no relief device |
| V-102 | Add a pressure relief device | hmb, pid_review | yes | P&ID R1 (gap): V-102 (drum, design 700 kPag) has no relief device in the register |

How to read a row: the reason is the chain *condition -> scenario -> gap*: for example the separator V-101 receives 50,000 kg/h of vapour, a blocked outlet needs several times the installed relief area, and so a study would recommend resizing; the propane bullet T-201 has 15 minutes to overfill against 22 needed, with level measured only in the control system, so a study would recommend an independent high-level trip. "Found by pid_review and hmb" means two independent routes reach the same recommendation. "In register: no" is a prompt to look at that node, not proof that the study missed it: matching is by keyword and node name.

## Common recommendations
`python -m process_safety catalog` lists 21 recommendation types. There is no published frequency benchmark to rank them: the practitioner papers found describe categories and good practice but no counts. The catalogue rests on what the toolkit's models can trigger, the 17 CSB recommendations (hand-mapped; 10 map cleanly) and practitioner categories. For real frequencies, run this tool on your own registers; the tally above is the pattern.

## Limits
Screening scenarios only (no coincident loads, no back-pressure build-up, no transient dynamics beyond the vapour-fire model); the interface check uses the stream's operating pressure, not the maximum a failed-open control valve could deliver; Z defaults to 1 with a flag; hazard flags use name matching on the RMP lists; keyword classification will miss unusual wording and will over-match generic words; the Proteus reader has not seen a real export.

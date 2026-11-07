# process-safety-design-toolkit

Dependency-free (Python stdlib only) calculators for the equations and screening models used in process-safety and relief-system
design, tied to the standards engineers are held to: API 520/521/526/2000, IEC 61511/CCPS LOPA, and the Indian OISD list.
Built from the safety scope of a typical process-safety consultancy brochure (HAZOP/QRA/SIL, relief and flare, F&G, loss prevention).

> **Not a safety case.** The standards are paywalled and were not read, except API 2000 5th ed. (1998, publicly posted). Equations are
> derived from first principles where possible and unit-tested against the standards' own constants/tables; every remaining
> coefficient is flagged in the module docstring. Verify against your edition; a qualified engineer owns the result.

## Install / run
```bash
pip install -e .            # or just: python3 -m process_safety ...
python3 -m unittest discover tests
python3 -m process_safety coverage      # topic -> standard -> code map, with what is NOT implemented
```

## Modules
| Module | What it does | Standard / basis | Status |
|---|---|---|---|
| `relief` | Gas (critical + subcritical), steam, liquid PSV area; API 526 orifice; accumulation; liquid-wetted fire case; wetted area | API 520-I, 521, 526 | equations tested vs API SI constants 13160 / 17.9 / 11.78 / 190.5 |
| `tank_venting` | Normal (thermal + liquid movement) and fire venting for atmospheric/low-pressure tanks | API 2000 **5th ed. 1998 (text read)** | reproduces Table 3B (two printed-table quirks documented) |
| `vapour_fire` | Transient wall/gas model for vapour-filled vessels in fire: PSV vs rupture vs blowdown | first principles + Safety 2018, 4(1), 11 | screening; API 521 F' shortcut deliberately not coded |
| `scenarios` | Scenario catalogue; blocked-in thermal expansion; tube rupture (10/13 rule + break flow); flare header Mach sizing | API 521 Part I | partial |
| `flare` | Point-source radiation, safe distances, radiant fraction, tip diameter | API 521 | allowable levels from secondary sources |
| `sil` | LOPA, required SIL, PFDavg 1oo1/1oo2/2oo2/2oo3 with beta, proof-test interval | IEC 61511, CCPS | no HFT/SFF check |
| `fireball` | BLEVE fireball size, duration, flux, dose | CCPS / Roberts 1982 | coefficients from secondary sources |
| `separator` | Souders-Brown vertical/horizontal separator, flare knock-out drum, droplet settling | API 12J-style K inputs | conceptual only |
| `hydraulics` | Darcy-Weisbach/Colebrook liquid dP, isothermal compressible gas line, erosional velocity, liquid Kv + choking, NPSHa, pump power/affinity, water-hammer wave speed and Joukowsky surge | textbook physics, IEC 60534 liquid definitions, API RP 14E | tested vs identities; criteria are inputs |
| `fire_water` | Hazen-Williams (NFPA 13 SI), nozzle flow, spray demand, simultaneous-demand/storage arithmetic | NFPA; OISD rates not read | rates are inputs |
| `vessel_mech` | Cylinder/sphere/2:1 head thickness, MAWP, hydrotest pressure, holdup volume | ASME VIII-1 UG-27/32 | S is an input; not a code calc |
| `release` | Liquid/gas hole releases, drain time, adiabatic blowdown (numeric vs analytic) | first principles | no flashing/two-phase |
| `dispersion` | Gaussian plume, Briggs sigmas and plume rise, distance to threshold, ppm conversion | Briggs/Pasquill-Gifford | neutral gas only; verify coefficients |
| `explosion` | TNT equivalence, Kinney-Graham overpressure, Brode burst energy | CCPS/TNO style | screening; no multi-energy |
| `consequence` | Thermal and toxic probits, fatality fraction, exposure time / concentration for a fraction | Eisenberg, TNO | verify constants |
| `reliability` | Availability, k-out-of-n, fault tree (exact, cut sets, Birnbaum), event tree, FMEA RPN, risk matrix | IEC 61025 / 62502 / 60812 methods | independence assumed |
| `hazop` | HAZOP worksheet generator (CSV for Excel) with generic cause prompts | IEC 61882 guidewords | skeleton only |
| `emissions` | Combustion CO2 by element balance, flare emissions with efficiency/GWP, SO2 | stoichiometry | efficiency/GWP are inputs |
| `reaction_hazard` | Adiabatic temperature rise, MTSR and screening flags | Stoessel-style | needs calorimetry |
| `pool_fire` | Burning rate (Burgess), flame height (Thomas), Mudan-Croce SEP, point-source flux and distances | CCPS-style | screening; no wind/spreading |
| `flammability` | Le Chatelier LFL/UFL, LOC, sweep/pressure/vacuum purge, charge relaxation, v.d check, zone-duration rule | NFPA 69 / API 2003 criteria are inputs | limits are inputs |
| `structural_fire` | ISO 834 and hydrocarbon curves, steel temperature (unprotected + insulated), time to critical temperature | EN 1993-1-2 forms | simplified; certification governs |
| `depressuring` | Time to target pressure (isothermal/adiabatic bounds, numeric + closed form), orifice for a target time, isentropic minimum temperature | API 521 criteria are inputs | gas phase only |
| `overfill` | Time to overfill, alarm margin and alarm height | API 2350 criteria are inputs | arithmetic |
| `relief_piping` | Inlet loss 3% check, outlet reaction force, exit Mach/velocity | API 520-II | no AIV/FIV |
| `psm` | OSHA PSM 14 elements, Appendix A applicability (134 chemicals) and the flammables rule, due-date tracking, AIGA 99 / RBPS crosswalk, gap scoring | OSHA 1910.119 (read), AIGA 99 (titles read) | cadences verified against OSHA text |
| `mah` | Seveso III sum-rule tier classification | Directive 2012/18/EU Annex I (parsed from official text) | EU thresholds only; India MSIHC schedules not read |
| `pipeline` | Gas pipeline design pressure, wall thickness, temperature derating, potential impact radius | 49 CFR 192.105/111/113/115/903 (read) | US rule; natural-gas PIR |
| `props` | Lee-Kesler vapour pressure, Rackett liquid density for light hydrocarbons/cryogens, saturation temperature | open-literature correlations, tested vs known values | non-polar only |
| `lng` | Impoundment capacity (49 CFR 193.2181), 193.2059 dispersion parameters, boil-off, regas duty and seawater/fuel, ideal liquefaction work | 49 CFR 193 (read) | siting models not reproduced |
| `lpg` | Vapour pressure, density, thermodynamic maximum filling ratio, refrigerated boil-off | props correlations | code limits are inputs |
| `rmp` | EPA RMP (77 toxics, 63 flammables, endpoints) threshold check and worst-case criteria (10 min release, 1.5 m/s F, 10% VCE yield, 1 psi) | 40 CFR 68 (read) | toxic distance = order-of-magnitude flag only |
| `flare_system` | Coincident-load aggregation per event, governing event, header size by Mach | API 521 practice | coincidence is an input |
| `plant_units` | Furnace purge time, H2O2 decomposition O2/heat/steam, adiabatic exotherm, hydrogenation heat | first principles | project data required |
| `electrical` | Fault levels, cable CSA/voltage drop, power factor, motor start dip, IEC 60255 relay curves + grading, IEEE 80 tolerable voltages and rod resistance, lightning rolling sphere and collection area, Ex T-class/gas group/EPL, Lee arc flash with OSHA applicability | OSHA 1910.269 App. E (read); IEEE 80, IEC 60255, 62305 (corroborated) | no IEEE 1584; not studies |
| `noise` | OSHA permissible exposure, dose, TWA, NIOSH 3 dB criterion, level summation and attenuation | OSHA 1910.95 + App. A (read) | environmental noise limits not implemented |
| `mechanical_safety` | ISO 13849-1 required PL and PFHd bands, ISO 13855 safeguard distance, sling tension, dropped-object/vehicle/ship energy, pipe span, thermal growth, guided cantilever, bolt torque | ISO texts paywalled (corroborated by search) | pre-2024 ISO 13855; screening forms |
| `qra` (package) | Six-step QRA: HAZID/HAZOP + LOC register, parts-count frequencies, fault trees, Cox ignition event trees, consequence footprints, LSIR grid, IRPA, F-N, PLL, R2P2/Bevi evaluation, mitigation re-runs with ALARP cost-benefit; HTML/Excel/CSV report; sample-first runs with progress, ETA and convergence check | HSE R2P2, Bevi, PHMSA failure-rate table, Cox-Lees-Ang | screening QRA; see `docs/QRA.md` |
| `bowtie` | Quantified bow-tie: threats/fault trees, prevention and mitigation barriers, escalation factors, RRW/RAW, SCE list, SVG | CCPS bow-tie practice | barrier independence assumed |
| `qra.buildings` | Occupied-building risk and building radiation impact from QRA events (Purple Book or custom vulnerability), exceedance curves | Purple Book (via DNV note), API 752/753 curves as inputs | blast field TNT-based, capped |
| `qra.emergency` | MCLS consequence distances, emergency planning zones A/B/C, ERDMP-style Level 1/2/3 | MoEF EIA TGM damage criteria | zones as circles |
| `sil_lifecycle` | SIL from RRF, IEC 61511 Table 6 HFT, Route 1H SFF, SIF verification, spurious trips, calibrated risk graph, SRS skeleton | IEC 61511-1:2016 COR1 Table 6 (read) | no SC / proof-test coverage |
| `fg_mapping` | F&G geographic coverage (point, open path, flame with line of sight), voting coverage vs targets, greedy optimiser | ISA TR84.00.07 style | 2D geographic only |
| `pha` | CHAZOP / What-if / SWIFT / PSSR worksheets, SIMOPS matrix and clash check, action tracker, revalidation, carry-forward | OSHA 1910.119(e)(6) cadence | checklists |
| `thermal_runaway` | TMRad, TD24, Stoessel criticality class, Semenov critical ambient | Stoessel (TUV SUD lecture examples reproduced) | zero-order kinetics |
| `atex` | KSt class, zone by grade, EPL / ATEX category, FIBC screening, EPD register | KSt classes (read) | no zone extent, no vent sizing |
| `ram` | Monte Carlo RAM with k-of-n stages, analytic check, criticality, sample-first run planning | binomial availability identity | unlimited crews |
| `twophase` | Two-phase / flashing discharge by the omega method: critical pressure ratio and mass flux by maximising the energy-balance flux, subcritical flux, relief area | homogeneous equilibrium; closed-form checks in tests | omega and Kd are inputs; no subcooled or DIERS runaway sizing |
| `shutdown_risk` | Shutdown/turnaround schedule and cost risk: Monte Carlo on a CPM network with three-point durations and costs, risk events, common-cause factor, **opportunity cost of lost operating days**, P10-P90, contingency, S-curve, criticality, tornado, safety-critical flags; `tool shutdown` | closed-form checks in tests; method background in `docs/SHUTDOWN_RISK.md` | calendar days, no resource levelling; all rates and margins are inputs |
| `plant_model`, `hmb`, `pid_review`, `scenario_ingest`, `recommendation_catalog` | Ingest PFS/HMB stream tables, P&ID registers or Proteus (DEXPI) XML and a PHA register; mass-balance and hazard checks; blocked outlet, overfill, interface, tube rupture, MDMT and fire scenarios; P&ID review rules; the reason behind each recommendation type and which ones the register misses; draft input for `tool workflow`; `tool plant` | each scenario recomputed from the underlying models in tests | screening; keyword matching; Proteus reader untested on real exports |
| `design_workflow` | Safety simulation -> equipment resizing and design -> bill of quantities -> capex and opex, for devices (PSV, inlet line, blowdown valve), pipeline rerouting, additional sensors and PCN modification; ALARP package test with risk benefit from sensor voting; shutdown merge; `tool workflow` | chains tested modules; closed-form arithmetic checks | screening models; you supply all rates; no two-phase in the chain |
| `lng_cost` | Concept-stage (FEL 1, Class 5 style) capital cost of an onshore LNG liquefaction plant from 26 public analogs (MIT-licensed ORIMIZ table), scaled for size, escalation, location and site type, Monte Carlo range; also `daily_margin` for the shutdown model; `tool lngcost` | analog data with sources; closed-form tests | you must supply a cost index and location factors; screening only |
| `recommendation_cost` | Cost of implementing study recommendations (piping, civil, electrical, instrumentation): quantity x rate lines with three-point uncertainty, indirects, shared rate factor, shutdown dependency merged into `shutdown_risk`, ALARP cost-benefit; `tool recs` | closed-form tests; ALARP via `qra.alarp` | no rates shipped; no resource-loaded schedule |
| `fluiddata` | Bundled saturated-liquid data for 18 fluids from CoolProp (omega, density, latent heat, cp, HEM flux), interpolated in ln P; `twophase --fluid`, `fluid-data` | CoolProp (MIT), regenerated by `scripts/gen_fluid_table.py` | pure fluids, saturated liquid only |
| `viewfactor` | Numerical view factor from flat rectangular flame faces to a target, incident flux = tau x SEP x F | integration checked vs Howell and far-field limits | no tilt, no blockage |
| `datacentre` | PUE, cooling-water flow, evaporative water per kWh, UPS battery energy, diesel storage, N+1/2N availability, generic data-centre HAZID prompts | energy balance and first principles | no tier/ASHRAE/NFPA values coded; see `docs/DATACENTRE.md` |
| `standards` | Topic coverage map + OISD list (105 standards, titles/editions from oisd.gov.in, 2026-09-21) | OISD | list verified, contents not read |

## Industries
Oil and gas upstream/midstream/downstream (relief, flare, tank venting, separators, blowdown, fire water, QRA inputs), refining and
petrochemicals (vapour-filled fire, LOPA/SIL, hazard studies), LNG/terminals (tank venting, fireballs, dispersion screening), chemicals and
pharma (reaction hazard, HAZOP, runaway screening, probits), power/utilities (surge, hydraulics, reliability), and general plant
(vessel thickness, emissions, availability). `python3 -m process_safety coverage` lists each topic with its status.

## Units: SI and US customary

Every command works in SI; add `--units us` before the command and type psig, degF, ft, in, lb, gpm ... instead. Results gain US sibling keys.
`template <command>` writes a fill-in input file (SI or US), `run <file>` executes it, `convert 150 psig kPag` prepares numbers for the JSON tools.
The differences that cause mistakes (gauge versus absolute, temperature reading versus rise, lb versus lbf, standard volumes) are in
[docs/UNITS.md](docs/UNITS.md); every parameter with its units and ranges is in [docs/INPUT_TEMPLATES.md](docs/INPUT_TEMPLATES.md)
and `templates/inputs_all.csv`. The scenario suite (`python scripts/run_scenarios.py --check`, report in
[docs/SCENARIO_REPORT.md](docs/SCENARIO_REPORT.md)) runs 150+ design cases, each command-line case in both unit systems.
Escape-time (`egress`) and lumen-method lighting (`illumination`) checks were added with it.
MATLAB and GNU Octave users: [matlab/](matlab/README.md) has the relief, two-phase flux, flame view-factor, depressuring, escape-time, lighting and unit tools as plain `.m` files, tested against the Python models.

## Examples
```bash
python3 -m process_safety relief-fire --D 2.5 --L 8 --level 1.5 --latent 330
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1000 --case fire --M 44 --k 1.13 --Z 0.9
python3 -m process_safety vapour-fire --volume 15 --area 36 --D 2 --wall-mm 20 --M 20 --k 1.3 --p0-g 1000 --psv-area 500 --psv-set-g 1500
python3 -m process_safety tank-fire --shape vertical --D 20 --L 15 --F bare --normal-capacity 1500
python3 -m process_safety flare --mass 20 --lhv 46 --mw 30 --flame-length 40
python3 -m process_safety pool-fire --area 300 --hc 44000 --hv 350 --cp 2.2 --tb 400
python3 -m process_safety depressure --volume 30 --p0 5000 --pt 1000 --T0 300 --M 20 --k 1.3 --area 800
python3 -m process_safety steel-fire --am-v 150
python3 -m process_safety psm-check --chemical chlorine --kg 700
python3 -m process_safety psm-due --pha 2021-03-15 --audit 2023-06-01 --today 2026-11-03
python3 -m process_safety seveso Chlorine:H=6 "Hydrogen sulphide:H=3"
python3 -m process_safety pipeline --smys 448 --wall 12.7 --od 610 --buildings 25
python3 -m process_safety rmp-check chlorine --kg 1200
python3 -m process_safety twophase --fluid propane --P0 1900 --W 8 --Kd 0.85   # flashing LPG relief area, data from the bundled CoolProp table
python3 -m process_safety fluid-data propane --P 1900
python3 -m process_safety flame-flux --width 20 --height 31 --distance 15 --sep 30.9 --tau 0.8   # near-field solid flame
python3 -m process_safety datacentre --it-kw 10000 --facility-kw 13000 --delta-t 8 --autonomy-min 10 --gen-hours 48 --sfc 210
python3 -m process_safety rmp-worst propane --kg 20000 --hc 46.3
python3 -m process_safety lng --tanks 160000 --heat-kw 100 --regas-kg-s 100
python3 -m process_safety lpg propane --fill-C 15 --max-C 50
python3 -m process_safety h2o2 --kg-h 1000
python3 -m process_safety arc-flash --kv 0.48 --ka 20 --t 0.2 --dist-mm 455
python3 -m process_safety idmt --i 2000 --pickup 200 --tms 0.3
python3 -m process_safety noise 95:2 90:4 100:0.5
python3 -m process_safety safeguard --stop-s 0.2 --d-mm 30
python3 -m process_safety earthing --rho-s 3000 --t 0.5 --rho 75 --hs 0.2
python3 -m process_safety lopa --ie 0.1 --ipl 0.1 0.01 --target 1e-6
python3 -m process_safety plume --Q 50 --u 2 --H 10 --stability F --M 34.08 --threshold-ppm 10
python3 -m process_safety blowdown --volume 20 --p0 2000 --T0 300 --M 20 --k 1.3 --hole-d 0.05
python3 -m process_safety hazop-csv --node "Node 1" --intent "Feed naphtha to surge drum" --out node1_hazop.csv
python3 -m process_safety --units us relief-gas --W 26455.5 --T 260.33 --set-g 217.557 --case fire --M 44 --k 1.13 --Z 0.9   # same case in US units
python3 -m process_safety egress --distance 60 --speed 1.2 --people 200 --width 2 --specific-flow 1.3 --detect-s 30 --premove-s 60 --aset-s 300
python3 -m process_safety illumination --area 100 --flux 3000 --uf 0.6 --mf 0.8 --target 300
python3 -m process_safety qra example --out study.json          # worked LPG/fuel terminal study to edit
python3 -m process_safety qra validate study.json               # input consistency checks
python3 -m process_safety qra hazid study.json --out hazid/     # HAZID register, HAZOP worksheet, LOC register (CSV)
python3 -m process_safety qra run study.json --sample 3 --out sample/   # small sample: checks, convergence, projected run time
python3 -m process_safety qra run study.json --out qra_out/     # full study: qra_report.html, qra_results.xlsx, CSVs, buildings, emergency
python3 -m process_safety tool example bowtie && python3 -m process_safety tool bowtie bowtie.json --out out/   # also sif fg thermal atex ram shutdown recs lngcost workflow plant pha
```
Python API (not all exposed on the CLI): `scenarios.thermal_expansion_relief_m3h`, `scenarios.tube_rupture_flow_kg_s`,
`separator.vertical_separator`, `separator.horizontal_separator`, `separator.knockout_drum_vertical`, `fireball.fireball`.

## Worked finding (vapour-filled fire, 15 m3 vessel, 20 mm wall, 1000 kPag, 100 kW/m2 pool fire)
No relief: ruptures at ~600 s. PSV 500 mm2 set 1500 kPag: lifts at ~320 s, holds 1502 kPag, **still ruptures at ~700 s** as the wall
weakens. Blowdown opened at 60 s: no rupture within the hour. Reproduces, qualitatively, the open-literature conclusion that a PSV
alone often does not protect a gas-filled vessel. Inputs (flux, internal film coefficient, strength curve) are assumptions: see
`vapour_fire.py`.

## Input checks, glossary
* Every numeric CLI input is checked against `docs/RANGES.md`: impossible values (negative absolute temperature, Cp/Cv of 1.0 or less) stop the run with exit 2; atypical ones warn on stderr and still run. `--no-range-check` skips the checks. `python -m process_safety ranges [NAME]` lists them. Core library functions raise `ranges.RangeError` on impossible values.
* `python -m process_safety glossary TERM` searches `docs/GLOSSARY.md` (about 115 terms and abbreviations).

## Docs
* `docs/PUBLIC_REQUIREMENTS_SURVEY.md`: counts of normative statements by recommendation type across 23 public oil, gas, LNG and safety-in-design documents (counts only, no quoted text).
* `docs/REQUIREMENTS_EXTRACT.md`: a local extractor for "shall"/"should" statements in standards and design practices you hold (private output only), with the project documents it connects to.
* `docs/INSURANCE_IMPACT.md`: actuarial view of how derogations, compensating measures and better-documented risk change a project's insurance cost (`insurance` command).
* `docs/LEGAL_CLAUSES.md`: legal provisions on general duty, change control, notification and exemption by jurisdiction (`legal-clauses` command): what a derogation cannot waive.
* `docs/COMPLIANCE.md`: requirement tiers (must / should / can) and derogations: what a departure from each tier needs, and a register check with gate readiness.
* `docs/PLANT_INGEST.md`: ingesting flow-scheme/HMB data, P&ID registers and a PHA register, and the reasoning chain for why studies recommend what they do.
* `docs/DESIGN_LIFECYCLE_PLAN.md`: a structured plan from process concept through flow scheme, heat and material balance, equipment design, P&ID-level design and safety studies to design tweaks and safe operation, mapped to the toolkit.
* `docs/RECOMMENDATIONS_CATALOG.md`: 21 common safety-study recommendation types with triggers, usual responses and cost scopes (`python -m process_safety catalog TEXT` classifies a recommendation).
* `docs/WORKFLOW.md`: the end-to-end workflow from safety simulation through resizing and design to capex and opex (pipeline rerouting, additional sensors, PCN modification), with a worked example and its limits.
* `docs/SIMULATION_TOOLS.md`: open-source simulators, property libraries, blowdown tools and costing/TEA packages (with licences and activity checked on GitHub) that can feed or cross-check this toolkit.
* `docs/COST_ESTIMATION.md`: the three cost estimators (plant, recommendations, shutdown) and how they connect; a review of the reference LNG cost notebook against published analogs; limits and attribution.
* `docs/RECOMMENDATION_COSTS.md`: what it costs to implement HAZOP/LOPA/QRA recommendations (piping, civil, electrical, instrumentation), with ranges, shutdown dependency and ALARP cost-benefit.
* `docs/SHUTDOWN_RISK.md`: shutdown schedule and cost risk, including the opportunity cost of lost operating days, with a worked example and its limits.
* `docs/INCIDENTS.md`: 17 CSB investigations (date, place, deaths where stated, an example recommendation, design lesson, toolkit modules, review steps), searchable with `python -m process_safety incidents [TEXT] [--module M] [--step N]`.
* `docs/LITERATURE.md`: 49 curated sources (regulations, regulators, investigation bodies, incident databases, associations, journals, reference tools) with topic and module links, what was read versus URL-checked only, and the HTTP status on 2026-11-06. Search with `python -m process_safety literature TEXT [--topic T] [--module M] [--region R]`.
* `docs/REGULATORY_LANDSCAPE.md`: process safety regimes by country, governing body and company, with a confidence grade per row (rule text read, regulator page read, search summary, or not found).
* `docs/DESIGN_AWARENESS.md`: process safety review steps, the design choices each drives, results from the use cases, and incident instances, with the toolkit command for each.
* `docs/USE_CASES.md`: eight worked scenarios (refinery fire case, flashing LPG relief, terminal siting, LOPA to proof-test interval, regulatory screen, electrical, data centre, occupational) with the real commands and outputs; every command is run by the tests.
* `docs/VALIDATION.md`: 186 cross-checks against fluids, thermo, CoolProp and closed-form literature formulas, with the differences to know about.
* `docs/ARCHITECTURE.md`: module layout, SOLID mapping, the command registry, range policy. `CONTRIBUTING.md`: checks to run, releasing.
* `docs/RANGES.md`, `docs/GLOSSARY.md`: generated from `ranges.py` and `glossary.py`; a test keeps them in sync.
* `docs/STUDIES.md`: bow-tie, occupied buildings, emergency zones/MCLS, SIL lifecycle, F&G mapping, PHA management, thermal runaway/ATEX, RAM.
* `docs/IFLUIDS_SERVICES.md`: the iFluids Engineering brochure service list mapped to modules, with what is not covered.
* `docs/DATACENTRE.md`: data-centre helpers, inputs, and what is deliberately not coded.
* `docs/QRA.md`: the QRA workflow, study file format, models and their limits, worked example results.
* `docs/RELATED_PROJECTS.md`: other open-source process-safety and engineering projects found on GitHub, with licences and how each relates to this toolkit.
* `docs/ELECTRICAL_MECHANICAL.md`: electrical and mechanical safety scope, which formulas were read versus corroborated, and the limits.
* `docs/SECTORS_AND_LESSONS.md`: LNG, LPG, refinery, petrochemical and chemicals coverage, public sources, and incident lessons mapped to modules.
* `docs/PSM_FRAMEWORKS.md`: OSHA, AIGA 99, CCPS RBPS, CSChE, DOE handbook, Indian rules and Seveso, and how each is used.
* `SOURCES.md`: what was verified, from where, at what confidence.
* `docs/TOOLKIT_SURVEY.md`: other open-source and spreadsheet toolkits found.
* `CHANGELOG.md`: decisions, including alternatives rejected.

## Not implemented (see `coverage`)
Dense-gas dispersion (the QRA uses neutral Gaussian plumes and Bernoulli liquid flow, flagged; override with Phast) and two-phase discharge inside the QRA (the standalone `twophase` command covers relief sizing only),
pump/compressor/valve/flange generic frequencies (no verified public row: give per study), pool/jet-fire geometry, multi-energy explosions,
layout distances (OISD-STD-118), hazardous area classification, F&G mapping, HAZOP worksheets, runaway-reaction relief (DIERS),
API 2000 7th-edition thermal method, vent/PV-valve flow curves, SIL architectural constraints.

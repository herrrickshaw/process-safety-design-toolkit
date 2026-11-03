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
| `standards` | Topic coverage map + OISD list (105 standards, titles/editions from oisd.gov.in, 2026-09-21) | OISD | list verified, contents not read |

## Industries
Oil and gas upstream/midstream/downstream (relief, flare, tank venting, separators, blowdown, fire water, QRA inputs), refining and
petrochemicals (vapour-filled fire, LOPA/SIL, hazard studies), LNG/terminals (tank venting, fireballs, dispersion screening), chemicals and
pharma (reaction hazard, HAZOP, runaway screening, probits), power/utilities (surge, hydraulics, reliability), and general plant
(vessel thickness, emissions, availability). `python3 -m process_safety coverage` lists each topic with its status.

## Examples
```bash
python3 -m process_safety relief-fire --D 2.5 --L 8 --level 1.5 --latent 330
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1000 --case fire --M 44 --k 1.13 --Z 0.9
python3 -m process_safety vapour-fire --volume 15 --area 36 --D 2 --wall-mm 20 --M 20 --k 1.3 --p0-g 1000 --psv-area 500 --psv-set-g 1500
python3 -m process_safety tank-fire --shape vertical --D 20 --L 15 --F bare --normal-capacity 1500
python3 -m process_safety flare --mass 20 --lhv 46 --mw 30 --flame-length 40
python3 -m process_safety lopa --ie 0.1 --ipl 0.1 0.01 --target 1e-6
python3 -m process_safety plume --Q 50 --u 2 --H 10 --stability F --M 34.08 --threshold-ppm 10
python3 -m process_safety blowdown --volume 20 --p0 2000 --T0 300 --M 20 --k 1.3 --hole-d 0.05
python3 -m process_safety hazop-csv --node "Node 1" --intent "Feed naphtha to surge drum" --out node1_hazop.csv
```
Python API (not all exposed on the CLI): `scenarios.thermal_expansion_relief_m3h`, `scenarios.tube_rupture_flow_kg_s`,
`separator.vertical_separator`, `separator.horizontal_separator`, `separator.knockout_drum_vertical`, `fireball.fireball`.

## Worked finding (vapour-filled fire, 15 m3 vessel, 20 mm wall, 1000 kPag, 100 kW/m2 pool fire)
No relief: ruptures at ~600 s. PSV 500 mm2 set 1500 kPag: lifts at ~320 s, holds 1502 kPag, **still ruptures at ~700 s** as the wall
weakens. Blowdown opened at 60 s: no rupture within the hour. Reproduces, qualitatively, the open-literature conclusion that a PSV
alone often does not protect a gas-filled vessel. Inputs (flux, internal film coefficient, strength curve) are assumptions: see
`vapour_fire.py`.

## Docs
* `SOURCES.md`: what was verified, from where, at what confidence.
* `docs/TOOLKIT_SURVEY.md`: other open-source and spreadsheet toolkits found.
* `CHANGELOG.md`: decisions, including alternatives rejected.

## Not implemented (see `coverage`)
Full QRA (frequency data, ignition and population modelling), dense-gas and two-phase release, pool/jet-fire geometry, multi-energy explosions,
layout distances (OISD-STD-118), hazardous area classification, F&G mapping, HAZOP worksheets, two-phase/runaway relief (DIERS),
API 2000 7th-edition thermal method, vent/PV-valve flow curves, SIL architectural constraints.

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
| `standards` | Topic coverage map + OISD list (105 standards, titles/editions from oisd.gov.in, 2026-09-21) | OISD | list verified, contents not read |

## Examples
```bash
python3 -m process_safety relief-fire --D 2.5 --L 8 --level 1.5 --latent 330
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1000 --case fire --M 44 --k 1.13 --Z 0.9
python3 -m process_safety vapour-fire --volume 15 --area 36 --D 2 --wall-mm 20 --M 20 --k 1.3 --p0-g 1000 --psv-area 500 --psv-set-g 1500
python3 -m process_safety tank-fire --shape vertical --D 20 --L 15 --F bare --normal-capacity 1500
python3 -m process_safety flare --mass 20 --lhv 46 --mw 30 --flame-length 40
python3 -m process_safety lopa --ie 0.1 --ipl 0.1 0.01 --target 1e-6
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
QRA consequence suite (pool/jet fire, explosion, toxic dispersion: use DNV Phast/Safeti or a validated tool), fire-water hydraulics,
layout distances (OISD-STD-118), hazardous area classification, F&G mapping, HAZOP worksheets, two-phase/runaway relief (DIERS),
API 2000 7th-edition thermal method, vent/PV-valve flow curves, SIL architectural constraints.

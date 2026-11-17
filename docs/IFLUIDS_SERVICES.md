# iFluids Engineering service list mapped to this toolkit

The scope below is the service list in iFluids Engineering's public company brochure (Chennai; process safety, engineering design,
asset integrity, environment, training). It is a **coverage map, not an endorsement or a claim of equivalence**: the toolkit gives
screening arithmetic and worksheets, while a consultancy delivers signed studies with software, site data and judgement.
`python3 -m process_safety coverage` prints the same status per topic.

Status: **yes** = a module covers the calculation; **partial** = screening only or part of the method; **no** = not implemented.

## Process and piping
| Brochure service | Toolkit | Status | Limit |
|---|---|---|---|
| Hydraulic analysis, pump sizing, valve sizing | `hydraulics` | yes | liquid Kv only; gas Cv not |
| Surge and water hammer analysis | `hydraulics.surge_screen` | partial | Joukowsky screening; no method of characteristics |
| Flow assurance / transient analysis | none | no | needs a transient solver |
| Flare and cold-vent network design and analysis | `flare`, `flare_system`, `scenarios` | partial | header Mach sizing and coincident loads; no network solve |
| Piping stress analysis | `mechanical_safety` (spans, thermal growth, torque) | partial | screening forms only |
| Vibration and pulsation study | none | no | API 618/674 style studies need software |
| Process simulation, PFD/P&ID | none | no | drawing and simulation tools |

## Electrical and power system studies
| Brochure service | Toolkit | Status | Limit |
|---|---|---|---|
| Cable sizing, voltage drop | `electrical` | yes | hand-calculation forms |
| Short circuit | `electrical` | partial | fault-level arithmetic, not a network study |
| Motor starting | `electrical` | partial | voltage-dip arithmetic |
| Protection relay coordination | `electrical.idmt_time_s`, `grading_check` | partial | curves and grading, not a study |
| Arc flash assessment | `electrical.lee_*` | partial | Lee method with OSHA applicability limits; IEEE 1584 not implemented |
| Lightning protection study | `electrical` | partial | geometry and strike frequency; IEC 62305 risk assessment not implemented |
| Earthing | `electrical` | partial | tolerable voltages and rod only |
| Load flow, harmonic, transient stability, switching transient | none | no | software studies |
| Illumination study | none | no | |

## Process safety and risk management
| Brochure service | Toolkit | Status | Limit |
|---|---|---|---|
| HAZID, HAZOP workshop, What-if, CHAZOP, SWIFT | `hazop`, `pha`, `qra.hazid` | partial | worksheets and action tracking; the study is a team exercise |
| FMEA, fault tree, event tree | `reliability`, `qra.eta` | yes | independence assumed |
| Bow-tie analysis | `bowtie` | yes | barrier independence assumed |
| Quantitative risk assessment | `qra` | partial | screening QRA; no dense-gas model (override hook for Phast/RISKCURVES) |
| SIL assessment, functional safety | `sil`, `sil_lifecycle` | partial | no proof-test coverage or systematic capability |
| Fire and explosion risk analysis | `pool_fire`, `explosion`, `fireball`, `qra.effects` | partial | screening models |
| Passive fire protection assessment | `structural_fire` | partial | lumped steel temperature; test certification governs |
| Smoke and gas detection study | `fg_mapping` | partial | 2D geographic coverage |
| TRIA / building risk, shelter in place | `qra.buildings` | partial | Purple Book curves; no API 752/753 |
| Emergency response and disaster management plan | `qra.emergency`, `psm` | partial | zones and levels approximate PNGRB ERDMP |
| H2S zoning, toxic risk | `dispersion`, `consequence`, `qra.emergency` | partial | neutral-buoyancy plume |
| Dropped object, vehicle impact, ship collision | `mechanical_safety` | partial | energy arithmetic |
| Escape, evacuation and rescue; emergency system survivability | none | no | |
| Process safety management | `psm`, `mah` | yes / partial | OSHA verified; Indian MSIHC schedules not implemented |
| PNGRB regulatory compliance, asset integrity | none | no | |

## Environment and water
| Brochure service | Toolkit | Status | Limit |
|---|---|---|---|
| Emissions (combustion, flare) | `emissions` | yes | efficiencies and GWP are inputs |
| Water management, zero liquid discharge | `datacentre.evaporative_water_l_per_kwh_it` (water use only) | partial | no treatment design |

## Data centre support (new)
The same disciplines apply to a data centre. `datacentre.py` and `docs/DATACENTRE.md` add the arithmetic and a HAZID prompt list; see
that file for scope and limits.

| Data centre need | iFluids discipline | Toolkit |
|---|---|---|
| Cooling-water flow, pump and pipe sizing, surge | Process hydraulics | `datacentre.cooling_water_flow_m3_h` then `hydraulics` |
| Diesel storage, fire, overfill, battery hazards | Process safety | `datacentre.diesel_storage_m3`, `overfill`, `pool_fire`, `thermal_runaway`, `HAZID_PROMPTS` |
| Substation, protection, arc flash | Power system studies | `electrical` |
| Redundancy (N+1, 2N) availability | Reliability | `datacentre.k_of_n_availability`, `dual_path_availability` |
| Water use of evaporative cooling | Environment | `datacentre.evaporative_water_l_per_kwh_it` |
| HVAC and cooling design, tier credentials | not offered | none |

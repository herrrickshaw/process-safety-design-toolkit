# Sector coverage, public sources, and lessons from incidents

Compiled 2026-11-03. "Read" = fetched and read in full or in the relevant sections; "found" = surfaced by web search, **not** read.
Open design guides for these sectors are scarce (most are paywalled: NFPA 59A, EN 1473, API 2510, OISD standards, CCPS books), so the
toolkit rests on the primary regulations that are free (49 CFR 193, 49 CFR 192, 40 CFR 68, OSHA 1910.119, Seveso III) plus textbook physics.

| Sector | Typical hazards | Toolkit modules | Public sources |
|---|---|---|---|
| LNG liquefaction | flammable refrigerants (propane, ethylene), cryogenic spill, brittle fracture, cold-box fires/BAHX fatigue, vapour dispersion, VCE | `lng`, `props`, `dispersion`*, `explosion`, `depressuring`, `relief`, `flare` | read: 49 CFR 193.2057/2059/2181; found: [AIChE refrigerant hazard ranking & siting presentation](https://www.aiche.org/conferences/videos/conference-presentations/guidelines-relative-hazard-ranking-refrigerants-and-siting-considerations-lng-liquefaction-units) (paywalled), vendor posters/patents |
| LNG regasification / terminals | boil-off, ORV/SCV operation, rapid phase transition, tank overpressure, ship transfer | `lng`, `tank_venting`, `depressuring`, `pool_fire` | found: [UT Austin LNG safety update 2012](https://www.beg.utexas.edu/files/cee/legacy/LNG_Safety_and_Security_Update_2012.pdf), [Primatech note on rapid phase transition](https://www.primatech.com/technical/pt-notes/390) |
| LPG (spheres, bullets, mounded, refrigerated, bottling) | BLEVE, overfilling/over-pressure, jet and pool fire, cold boil-off | `lpg`, `props`, `fireball`, `pool_fire`, `relief`, `overfill`, `structural_fire` | found: [BLEVE prevention for LPG storage, CPSS presentation](https://tiche.org/wp-content/uploads/2022/03/5.7th-CPSS-BLEVE-Prevention-on-Liquefied-Petroleum-Gas-Storage_SCG.pdf), [Aston thesis on LPG hazard assessment](https://publications.aston.ac.uk/id/eprint/21678/3/A.M_Nasir_1987_reduced.pdf); standards named: API 2510/2510A, NFPA 58, OISD-STD-144/150/236 (not read) |
| Refinery | transient operations (start-up/shutdown), HTHA and other damage mechanisms, FCC and coker hazards, flare coincident loads, fired heaters, hydroprocessing exotherms | `flare_system`, `plant_units`, `psm`, `vapour_fire`, `depressuring`, `hazop`, `relief` | found: [CSB Husky Superior refinery report](https://www.csb.gov/assets/1/6/husky_superior_refinery_report_2022-12-23_(1).pdf); CSB Tesoro Anacortes (HTHA) and Chevron Richmond materials |
| Petrochemicals | polymerisation runaway, ethylene/propylene handling, polymer storage, reactive monomers (styrene), peroxides | `reaction_hazard`, `plant_units`, `hazop`, `tank_venting`, `pool_fire`, `psm` | found: coverage of the LG Polymers Visakhapatnam 2020 styrene release ([PMC article](https://pmc.ncbi.nlm.nih.gov/articles/PMC9920456/), [Down To Earth](https://www.downtoearth.org.in/news/pollution/vizag-gas-leak-curtain-calls-on-the-accountability-of-lg-polymers-72222)) |
| Other chemicals (toxic, reactive, ammonia, chlorine, peroxides) | toxic release, runaway, decomposition venting | `rmp`, `mah`, `psm`, `consequence`, `dispersion`*, `plant_units`, `reaction_hazard` | read: 40 CFR 68 (68.10, 68.22, 68.25, 68.115, 68.130, Appendix A), OSHA 1910.119 + Appendix A, Seveso III Annex I |

\\* The neutral-gas Gaussian model is **not** valid for cold or heavy clouds (LNG vapour, chlorine, LPG). It is an order-of-magnitude flag only: use a dense-gas
model (DEGADIS, ALOHA, Phast) for anything that matters.

## Incident lessons mapped to modules
Summaries are from public investigation material; verify details against the reports before quoting.

| Incident | Lesson | Where in this toolkit |
|---|---|---|
| Vizag (LG Polymers) styrene tank, India, 2020 (found: committee findings via news/PMC) | polymerisation runaway in an idle tank: inhibitor depletion, single local temperature sensor, no HAZOP or pre-start review after lockdown | `reaction_hazard`, `psm` (PSSR, MOC), `hazop`, `tank_venting` |
| Husky Superior refinery FCC explosion, 2018 (found: CSB report) | transient operations need explicit hazard analysis; understand why venting/purging steps exist | `psm`, `hazop`, `plant_units` |
| Tesoro Anacortes, 2010 (found: CSB) | high-temperature hydrogen attack was not assessed | `psm` (mechanical integrity), `hazop` (damage mechanisms) |
| Buncefield 2005 (UK), IOC Jaipur 2009, BP Texas City 2005 (well-documented; reports not fetched here) | overfill of a tank or column leading to a large vapour release/explosion; blowdown to atmosphere | `overfill`, `separator.knockout_drum_vertical`, `explosion`, `tank_venting`, `flare_system` |

## Not covered (needs paywalled standards or validated models)
NFPA 59A / EN 1473 design spills and siting distances, OISD-STD-194/150/144/236 requirements, API 2510 spacing, HF alkylation, FCC afterburn and coker
models, Indian MSIHC schedules, LNG pool-fire (LNGFIRE3) and dense-gas dispersion, rapid-phase-transition energetics, two-phase/runaway relief (DIERS).

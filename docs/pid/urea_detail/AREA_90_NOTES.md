# Area 90 Offsites and safety systems: unit notes (coal-to-urea, 3,850 t/d urea, Talcher-class)

Generated with `scripts/urea_area_90.py` (16 sheets, numbers 901-916). Basis: Rev B balance x K = 1.2784 (D); urea 160.4 t/h. No document was fetched for this area: fire-water, foam/deluge, detector thresholds, relief-sizing and storage-code content is a GAP and no value from memory is typed. Laboratory and utility buildings are out of scope.

## Sheets
| No. | Tag | Content |
|---|---|---|
| 901 | FLR-901 | flare system topology: HP/LP headers, KO-101, V-901, FL-101 (block) |
| 902 | KO-101, P-901A/B | flare knock-out drum and slop pumps (local drawing: no ESD valve in the relief path) |
| 903 | V-901 | flare water seal drum |
| 904 | FL-101 | elevated flare with pilots, ignition, purge (package) |
| 905 | V-902, P-902A/B | closed-drain drum with vent to LP flare and ESD inlet valve |
| 906 | OWS-901 | open drains and oily-water separation (package) |
| 907 | RHB-901 | relief header sizing basis: load cases and data needed, NOT sized |
| 908 | T-902 | urea bulk store (package) |
| 909 | CV-901 | urea conveyor train (package) |
| 910 | BAG-901 | bagging lines (package) |
| 911 | LD-901 | truck and rail loading (package) |
| 912 | FW-901 | fire-water topology: tanks, jockey, electric and diesel pumps, ring main (all quantities gap) |
| 913 | FD-901 | foam and deluge for NH3 and coal areas (qualitative table) |
| 914 | FGD-901 | fire and gas detection layout logic (vapour density ratios D from molar mass) |
| 915 | ESD-901 | ESD hierarchy ESD-0 to ESD-5 and PSD |
| 916 | CE-901 | plant cause-and-effect summary, qualitative |

## Key numbers
- Flare SCREENING REFERENCE LOAD (not a relief load): HP 30.6 t/h = 10 % (A 5-25 %) of raw syngas (Rev B stream 4, 306 t/h) plus LP 12.7 t/h (Rev B S11+S13+S16 diverted); header 2 bar abs, 60 C (A). Rev B has no relief loads, so KO-101, V-901 and the FL-101 tip diameter scale with this placeholder and must be redone with real loads.
- KO-101: D = sqrt(4Q/(pi vmax)), vmax = K sqrt((rho_L-rho_G)/rho_G), K = 0.10 m/s (A 0.05-0.15), liquid carry-over 3 % (A). V-901: seal 0.15 bar (A) so the seal leg is dP/(rho g). Tip: velocity 0.2 of sonic (A), gamma 1.3 (A). Stack height and radiation: gap.
- Urea train: stream 22 160.4 t/h; store 7 days = 26,950 t = 35,933 m3 (2,994 m2 at 12 m pile); conveyors 201 t/h (1.25 x); bagging 2,888 bags/h = 3 lines + 1 spare at 1,200 bags/h each; dispatch 77 trucks/day and 32 wagons/day. Mass closure asserted: 22 = 921 = 922 + 923 = 925 + 926.
- Detector placement ratios (molar mass / 28.96, D): NH3 0.59, H2 0.07, CO 0.97, H2S 1.18, CO2 1.52, N2 0.97, O2 1.10.
- ESD levels: ESD-1 to ESD-4 and HS-001 from the Rev B P&ID; ESD-0 (total) and ESD-5 (utilities) are new in this package (A).

## A assumptions and ranges
| Name | Value | Range | Meaning |
|---|---|---|---|
| FLARE_FRAC | 0.1 | 0.05 - 0.25 | screening reference HP release as fraction of raw syngas (Rev B stream 4); NOT a relief load |
| KO_CARRY | 0.03 | 0.01 - 0.1 | liquid carry-over / condensate as fraction of KO inlet mass |
| K_SB | 0.1 | 0.05 - 0.15 | Souders-Brown velocity coefficient, m/s (screening, to be confirmed by vendor/standard) |
| HOLD_KO | 30 | 20 - 60 | KO drum liquid hold-up, minutes of liquid inflow |
| SEAL_DP | 0.15 | 0.1 - 0.3 | seal drum water-seal pressure, bar |
| SEAL_CARRY | 0.005 | 0.001 - 0.02 | condensate / entrained liquid at seal drum as fraction of gas |
| MACH_TIP | 0.2 | 0.1 - 0.5 | flare tip exit velocity as fraction of sonic velocity |
| GAMMA | 1.3 | 1.2 - 1.4 | heat-capacity ratio of flare gas |
| PILOT | 0.03 | 0.01 - 0.06 | pilot fuel gas total, t/h (vendor to confirm) |
| PURGE | 0.05 | 0.02 - 0.2 | continuous flare purge gas, t/h (vendor to confirm) |
| CD_FLOW | 10 | 2 - 50 | closed-drain average drain-down flow, t/h (needs largest vessel inventory and drain time: gap) |
| OWS_FLOW | 100 | 20 - 500 | oily/contaminated runoff to open-drain sewer, t/h (rainfall and area data: gap) |
| OIL_F | 0.01 | 0.002 - 0.05 | oil fraction of OWS inflow |
| BULK | 0.75 | 0.7 - 0.8 | urea granule bulk density, t/m3 |
| DAYS | 7 | 3 - 14 | urea bulk store capacity, days of production |
| PILE_H | 12 | 8 - 15 | pile height, m |
| CV_F | 1.25 | 1.1 - 1.5 | conveyor design capacity factor on production rate |
| BAG_F | 0.9 | 0.5 - 1 | bagged fraction of urea dispatch |
| BAG_KG | 50 | 45 - 50 | bag mass, kg |
| BAG_RATE | 1200 | 800 - 1800 | bags/h per bagging line (vendor to confirm) |
| ROAD_F | 0.5 | 0 - 1 | road share of dispatch (rest by rail) |
| TRUCK_T | 25 | 20 - 30 | truck payload, t |
| WAGON_T | 60 | 50 - 65 | rail wagon payload, t |

## Gaps
- Relief loads, header back-pressure limits and simultaneity (sheet 907); flare stack height, radiation and noise; H2S/SO2 flaring policy.
- Fire-water volumes, flows, pressures, pump counts, ring main; foam/deluge rates and durations; detector thresholds and spacing; SIL and voting study; fire-water run-off retention. None of these documents was fetched; to close, fetch the owner's site standard or an open code and enter the values as inputs.
- Rainfall and catchment for open drains; drain-down basis for the closed-drain drum (placeholder 10 t/h A); urea store code, cooler before storage, bag and logistics data (all A).

## Design decisions recorded
- Flare path: no ESD closure valve. The standard vessel template always draws a fail-closed XV on the inlet (wrong for a KO drum in a relief path), so KO-101 and V-901 are drawn locally with car-sealed-open block valves (`LO-` tags, valve register patched). Lint rule "toxic/flammable gas inventory has an ESD valve" is applied to V-902 (XV-90502) and not to the flare path, by design.
- ESD hierarchy sheet and cause-and-effect are qualitative (A): they extend the Rev B matrix to utilities and offsites.

## Template defects met (library not edited)
1. `sheet_vessel` forces an ESD inlet valve (see above); sizes by liquid residence only (KO-101 minimum would be 0.8 m ID).
2. `sheet_package`: PSV label/destination fixed as flare (area 90 sheets avoid package PSVs); solids drawn as pipes with NPS and velocity (CV-901 / T-902 / BAG-901 / LD-901 line lists: ignore the NPS columns); an isolation valve is always drawn on every package inlet, so FL-101's flare-gas valve is re-labelled car-sealed open in the register only.
3. `data_panel` column widths truncate text over 25/38/14 characters (a check in the file warns).
4. Cosmetic: valve and diamond overlap on short vertical segments (sheet 902 gas outlet, sheet 903 bottom).

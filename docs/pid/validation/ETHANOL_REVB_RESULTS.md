# ETHANOL (grain 1G distillery, 100 KLPD) P&ID set, Rev B results

Generator `scripts/gen_pid_ethanol.py`; set `docs/pid/ETHANOL_PID_Set_RevB.html/.pdf` (9 sheets). Metric table: `ETHANOL_REVB_RESULTS.csv` (written by `--csv`). Frozen tool scripts: `/private/tmp/claude-501/val_ethanol/revb/` (`rect_check.py`, `bst_corn_detail.py`). Rev A files removed from docs/pid (git history keeps them). Nothing committed.

## (a) Corrections applied (all in the generator calculation)

| Item | Rev A | Rev B | Source | Effect |
|---|---|---|---|---|
| A11 overall Y (starch to ethanol + CO2) | 0.90 | 0.93 (range 0.88 to 0.95) | BioSTEAM corn run implies 0.930 (SSF 0.95 on glucose, rest to yeast); ANL 2.81 gal/bu implies at least 0.916; Indian EIA grain/L implies 0.88 to 0.91 | grain 81.9 to 79.3 kt/yr, DDGS 0.907 to 0.822 t/KL, steam 6.33 to 6.28 kg/L; CO2 unchanged |
| A16 rectifier reflux R | 3.0 | 3.5 | own NRTL McCabe-Thiele (thermo 0.6.1, CoolProp 8.0.0): Rmin 2.71, 66 ideal stages at 3.0, 48 at 3.25, 39 at 3.5, 31 at 4.0 | R/Rmin 1.11 to 1.29; E-103 -3,119 to -3,675 kW (CoolProp recheck 3,690, +0.4 %); E-106 +1,076 to +1,632 kW |
| A18 ethanol latent heat | 840 | 849.8 | CoolProp 8.0.0 at NBP 351.57 K | duties < 1 % |
| Closure | mass, C | mass, C, H, O | derived | all 0.00 % |
| Fermenter count | not set | N = 4 x 612 m3 gross | BioSTEAM SSF defaults (tau 60 h, V_wf 0.83) + A turnaround, max size | basis for PVRV-201 sizing |
| Evaporator economy 2.5 | 2.5 | 2.5 (range 2.5 to 3.0) | Dale and Tyner default (low-medium) | not applied; 3.0 would save 0.56 MW |
| Steam benchmark box | none | added | ANL, Dale and Tyner, IGL, PR, BioSTEAM | no value changed |

Finding that corrects GAP_CLOSURE_BIO: raising Y does not raise CO2 (CO2 is fixed by ethanol output); the model shows 0.7517 t/KL at every Y.

Metric table (Rev A | Rev B | reference | deviation before / after | status):

| Metric | Rev A | Rev B | Reference | Dev. A / B | Status |
|---|---|---|---|---|---|
| Grain kg/L | 2.481 | 2.401 | 2.465 IGL; 2.553 PR | +0.7 / -2.6 %; -2.8 / -5.9 % | agrees, inside 10 % |
| Yield L/t grain | 403 | 416 | 418.8 ANL (denatured) | -3.8 / -0.6 % | closed |
| DDGS t/KL, 10 % moisture | 0.907 | 0.822 | VV 0.609; PR 0.700; ANL 0.786 | +49 / +35 %; +30 / +18 %; +15 / +4.6 % | reduced; closed against ANL only |
| DDGS dry kg/L | 0.816 | 0.740 | 0.707 ANL | +15 / +4.7 % | closed (inside ANL range) |
| CO2 t/KL | 0.752 | 0.752 | 0.763 VV; 0.740 PR | -1.5 %; +1.6 % | agrees |
| LP steam kg/L | 6.33 | 6.28 | 6.6 IGL; 5.04 PR | -4.1 / -4.8 %; +26 / +25 % | IGL agrees; PR unchanged (scope unknown) |
| Thermal MJ/L | 13.3 | 13.2 | 7.7 ANL fuel; BioSTEAM 8.78 | +73 / +72 % | unchanged: steam vs fuel, US sells 36.7 % DDGS wet |
| Slurry water L/L | 5.79 | 5.60 | 6.49 IGL | -10.7 / -13.6 % | worse, now outside 10 %; A9 slurry 30 % unsourced |
| Grain t/yr vs template 86,800 | 81,888 | 79,250 | template | -5.7 / -8.7 % | template is the high figure |
| DDGS t/yr vs template 26,000 | 29,924 | 27,140 | template | +15 / +4.4 % | reduced |
| Rectifier R/Rmin | 1.11 | 1.29 | NRTL | | closed |
| S9 dew T | 95 C | 95 C | 92.0 | +3.3 K | unchanged, explained (A superheat) |
| Lint: devices absent from sheet 1 | 8 | 0 | | | closed |

## (b) Not closed and why
- DDGS vs VV 0.609 and PR 0.700: with grain at 2.40 kg/L and every non-starch solid going to DDGS, the floor is 0.624 kg dry/L = 0.69 t/KL at any Y (derived). The references need non-starch solids removed (corn oil: BioSTEAM recovers 0.036 kg/L; fibre, protein feed, wet sales) or a different grain. A7 starch 62 % and A8 moisture 12 % have no source.
- Steam and thermal energy: no heat integration beyond E-101 (A); dryer 37 % of steam against 27.5 % in Dale and Tyner. Economy 3.0 and dryer efficiency 0.80 shown as sensitivity (sheet 2), not applied.
- Fermentation heat 85 kJ/mol, dryer efficiency 0.65: no source, stay A.
- Slurry water -13.6 %: A9 unchanged.
- DWSIM not installed: no DWSIM result claimed.

## (c) Safety items now present
Sheet 1 devices (all drawn with tags): PSV-301/302/303/401/501, PVRV-201/401/402, EVH-401, TSV-101/102/103, VT-101..103, XP-101/102/501/502/503, RV-501, SD-501, DL-501, XV-201/301A/301B/401/402/404/501, GD-201/301/302/401/402, FD-401, LAHH-401/402, LSHH-201, PAHH-301/302, TAHH-501, BD-401 bund with DV-401, FC-401, FW-401, VH-101/ST-101.
- Sheet 5: relief schedule, 29 rows (every vessel, column, reactor, tank, exchanger, dust item).
- Sheet 6: sizing with `process_safety` (API 520-I gas, API 2000 5th ed.): PSV-301 4,564 mm2, PSV-302 8,124 mm2, PSV-303 1,805 mm2, PVRV-201 1,635 mm2 per fermenter; fire vent T-201A/B 10,615 and T-101 8,155 Nm3/h; normal venting; bund 415 m3 (110 % of largest tank, S1 para 157). All pressures and geometry A.
- Sheet 7: ESD matrix (10 initiators x 11 final elements), 6 SIFs (SIL targets A, no verification).
- Sheet 8: detection, isolation, bund, distances, fire water and foam, ventilation, area classification, dryer; 6 inherently safer options (ISD-4: sell wet cake removes the dryer, 37 % of steam).
- Sheet 9: 9 HAZID nodes.
Lint: stream diamonds 20 = HMB columns 20, no duplicates; every device tag on sheets 3 to 9 exists on sheet 1; relief coverage: every pressure item has a device or a stated reason.

Still gaps: standards not obtained (NFPA 30/68/11/15, API 520/521/2000/2350/650 text, IEC 61511 and 60079, OISD-STD-116/117/118/144, BIS, PESO, boiler code); dust explosion vent areas (no Kst, Pmax); fires on columns, beds, fermenters; foam-over; thermal-expansion valves; fire-water rates; CO2 toxic limits; area classification; steam header and boiler valves; layout distances except T-201A/B band.

## (d) Verify with a licensor or vendor
Overall yield Y and grain composition (starch, oil, fibre); DDGS definition and by-products (oil, wet cake); rectifier stages and tray efficiency (39 ideal); evaporator effects and economy; dryer type and efficiency; fermenter count, volume, foam behaviour and CO2 peak factor; column design and set pressures; tank sizes; vent and stack height and destination; dust test data; boiler fuel and code.

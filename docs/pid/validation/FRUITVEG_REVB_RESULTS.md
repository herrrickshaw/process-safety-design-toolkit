# FRUITVEG Rev B results

Generator `scripts/gen_pid_fruitveg.py`, output `docs/pid/FRUITVEG_PID_Set_RevB.html/.pdf` (8 sheets). Closure: in 17,489.9 kg/h, out 17,489.9 kg/h, error 0.000 %; water, dry matter and soil close separately (asserted). Detail: `FRUITVEG_REVB_RESULTS.csv`.

## (a) Flagged metrics, Rev A vs Rev B

| Metric | Rev A | Rev B | Reference | Dev before | Dev after | Status |
|---|---|---|---|---|---|---|
| COD load, plant per t product | 3.03 kg/t | 11.5 kg/t (peeled IQF line 38.7) | 36.5 kg/t half pears; 66.3 caustic (BREF Tab 8.3, 8.4) | -91.7 % | plant -68 %; peeled line +6 % | reduced (plant); closed (peeled IQF line). Pulp line is unpeeled (A15, crop open) |
| Untreated effluent COD | 568 mg/L mixed | 1,503 mg/L mixed; peel stream 5,000 mg/L at 3.34 m3/h | 4,000-5,000 mg/L peeling wastewater (BREF 8.2.1) | -86 % | peel stream 0 % (S input); mixed explained by dilution | closed as a basis: ETP sized from the peel stream, not the mixed average |
| Removal needed to 250 mg/L | 56 % | 83 % | IFC Table 1 | n/a | n/a | updated |
| IQF cooler water | 0.3 kg/kg | 3.0 kg/kg (drum cooler) | 2-4 L/kg (BREF 8.2.2.4) | -90 % | 0 % (mid range) | closed |
| Fresh water per t product | 5.11 m3/t | 7.45 m3/t | frozen F&V 5.0-8.5 (BREF Tab 8.10) | +1.4 % vs top of mix-weighted | inside range | closed (in range; above the cans 2.5-4.0) |
| IQF blancher steam | 0.160 t/t frozen | 0.163 t/t (option 0.09 needs recovery, 41 kg/h vs 75) | 0.09 belt+water; 0.16 belt+air (BREF Tab 8.6, 8.7) | +77 % / 0 % | +81 % / +2 % | unchanged: direct-steam bath without heat recovery; recovery not drawn |
| IQF refrigeration electricity | 62-70 kWhe/t implied, not shown | 63-72 compressor-only; 37-128 kW BREF total shown | 80-280 kWhe/t (BREF 8.1, fans incl.) | -12.5 % | -10 % (explained) | reduced: line added; compressor-only vs BREF total |
| Solid by-product | 194 kg/t product | 186 kg/t product | peaches 180, carrots 200 (IFC Tab 2) | +7.6 % | +3.4 % | closed (crop-dependent) |
| Pulp-line yield | 83.9 % | 83.9 % | 77.9 % mango (grade C) | +7.7 % | +7.7 % | unchanged: crop open, grade C reference |
| Ice cp | 1.9 (unverifiable) | 2.025 mean -18..-1.5 C | IAPWS R10-06(2009) Eq. 6, check value reproduced to 1e-9 | not verifiable | verified | closed; thermo 1.26 is wrong for solid ice |
| Fruit cp | 3.60 | 3.73 | composition (validation recompute) | -3.5 % | 0 % | closed |
| hfg at 0.2 bar | 2300 | 2357.5 | CoolProp 8.0 | -2.4 % | 0 % | closed |
| Effluent temperature | 40 C (A) | 35.6 C (D) | 36.7 C validation mix | +9.1 % | -3 % | closed |
| Lint: pressure items without relief or reason | 4 (E-301, F-401/CS-401, DA-201/VC-201) | 0 | checklist | 4 | 0 | closed (PSV-301, PSV-401/402, VB-201, written reasons) |
| Lint: ESD items not on sheet 1 | EF-701, ESD-701, BMS-501, TCV-301 | 0 | scenarios | 4 | 0 | closed |
| Lint: equipment missing from list | P-601, CIP-901, BH-501 | 0 (instruments and valves by tag on drawing) | drawing | 3 | 0 | closed |

Biggest effects: ETP COD 5.9 to 22.6 kg/h and 568 to 1,503 mg/L (flow 10.4 to 15.1 m3/h); IQF cooler water 0.3 to 3.0 kg/kg (fresh water 5.11 to 7.45 m3/t); freezing load 40.1 to 40.8 kW, steam 456 to 468 kg/h, boiler fuel 351 to 360 kW.

## (b) Not closed
- Plant-wide COD stays at 11.5 kg/t product because the pulp line is modelled unpeeled; peeling the whole plant at 36.5 kg/t needs 65 kg/h of dry matter against 57 kg/h of by-product, so flesh loss would also be needed (sheet 3 bounds, 36.5 to 66.3 kg/t gives 77 to 136 kg COD/h).
- Blancher steam 0.163 t/t versus 0.09: needs cooling-water-to-preheat recovery, not drawn.
- Compressor electricity 63-72 versus BREF 80-280 kWhe/t: BREF includes fans and auxiliaries; refrigerant still generic (ammonia only a conditional case for COP).
- Pulp yield 83.9 % (crop open; mango 77.9 % is grade C). IQF share 25 % has no source (10-50 % sensitivity on sheet 3). Cold-store load: no source in BREF, IFC, MSAMB, NABARD. Pasteuriser steam per t, hot-fill/aseptic split, boiler fuel: no source.
- By-product falls 3 % against Rev A (1,458 vs 1,518 t/yr; template 1,500) because the peel-water dry matter comes out of the trim.

## (c) Safety items
Present: relief schedule (11 rows) with PSV-301, PSV-401/402, VB-201, PSV-501/502/701, RH-701 header; indicative PSV-501 area 150 mm2, orifice F, for an assumed 585 kg/h rated output (A; `process_safety.relief.steam_area`); ESD matrix 10 rows by 8 final elements; 7 SIFs with assumed SIL; 10 HAZOP nodes; 6 inherently-safer options; detection and mitigation table (machinery-room detectors AT-701/702, EF-701, ROSOVs, bund rule, layout, fire NOC, sterility CCP, CIP chemicals). Ammonia appears only as a labelled conditional case (S6, S7 as reported).
Still gaps: IIAR 2 / EN 378 (detector set points, ventilation rate, refrigerant relief), IEC 61511 and LOPA, API 520/521/526 sizing for fire and blocked-outlet cases (not sized: refrigerant, charge, pump shut-off head, control-valve Cv missing), boiler code and burner standard (HSE PM5 404), FSSAI/process-authority critical limits, CIP chemical source, food-plant fire water, SIP supply to AF-301.

## (d) Verify with a licensor or vendor
Refrigerant, charge and machinery-room design; boiler capacity, fuel and code relief; E-301 and P-201 data for PSV-301; hold-tube design and validated sterility limits; crop and peeling method (steam, abrasion, caustic) and peel-water volume; IQF line share; cooler type (drum versus belt with recovery); cold-store load; ETP sizing from peel stream and peak days.

## Independent re-check after rebuild
`/private/tmp/claude-501/gap_bio/fv_revb/lint.py` (CoolProp 8.0): Tsat 143.61 and hfg 2133.4 at 4 bar, hfg 2357.5 at 0.2 bar, deaerator outlet 70.53 C, E-301 hot-fill 19.06 kW, drum cooler 24.86 kW and outlet 43.5 C, peel COD 16.69 kg/h and 3.338 m3/h all agree with the sheet values. Ice cp from IAPWS R10-06 reproduces its Table 6 check value to 1e-9. Lint: 36 stream diamonds vs 36 HMB columns, none missing; scenario valves and detectors all on sheet 1.

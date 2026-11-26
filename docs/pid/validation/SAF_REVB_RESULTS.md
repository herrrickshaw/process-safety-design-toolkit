# SAF P&ID set Rev B: results (2026-11-11)

Generator `scripts/gen_pid_saf.py`, output `docs/pid/SAF_PID_Set_RevB.html/.pdf` (8 sheets). Thermo check: `tests/crosscheck/saf_revb_thermo.py` (venv: thermo 0.6.1 PR kij 0, chemicals, CoolProp 8.0; DWSIM not used). Screening aid.

Basis (default pending owner confirmation): feed 30,000 t/yr UCO (template S); product slate NREL TP-5100-87803 Table G-1 jet mode (S). The DPR's 24,000 t/yr SAF is not used: it is 80 wt % of the oil, above IEA Task 39 (about 15 % default), IATA (15-50 % text, about 55 % max-SAF figure), NREL (46.1 %) and Tao (57-65 %). Rev B SAF 13,388 t/yr, RD 8,828, naphtha 2,468, LPG 1,742, fuel gas 436. Closure: mass 0.000 %, C/H/O each < 0.001 %, all 11 nodes < 0.001 %. Sensitivities (sheet 3): diesel mode (NREL: diesel 85 %, no SAF; with a splitter about 15 % of HT paraffin = 3,785 t/yr SAF); holding 24,000 t/yr SAF needs 53,781 t/yr UCO in this model (52,060 by the NREL ratio), every unit scaling x1.79. The template revenue line (24,000 t/yr at INR 165/kg) is overstated by 44 % at 30,000 t/yr feed.

## (a) Every metric the validator flagged

| Metric | Rev A | Rev B | Reference | Dev. before | Dev. after | Status |
|---|---|---|---|---|---|---|
| Stage-1 H2 | 123.45 kg/h | 123.45 kg/h | 123.45 (own stoichiometry) | 0.0 % | 0.0 % | unchanged (agreed) |
| Stage-1 heat of reaction | 312 kW (0.30 MJ/kg) | 1106 kW (1.07 MJ/kg) | 1,059-1,151 kW (Hf, two routes) | -70 % | +0.1 % vs route mean | closed (+/-10 %) |
| No-diluent runaway rise | 112 K | 230 K | 316-344 K (validator, liquid only) | -64 % | basis changed (gas heat capacity included) | closed by derivation |
| No-quench rise | 64 K | 75 K | 144-156 K at R=1.5 (validator) | -55 % | n/a: recycle now 5.9 | closed by derivation, not a reference match |
| Liquid cp in duties | 2.3 kJ/kg/K | 3.23 hot, 2.83 feed, 2.86 cool | 3.23 (CoolProp n-dodecane 250-340 C) | -29 % | 0 % (hot) | closed |
| E-202 duty | 667 kW | 1177 kW | PR check 1,123 kW (re-run) | 0.4 % | +4.8 % | agrees (now includes paraffin condensing) |
| K-201 shaft | 25.5 kW | 25.4 kW | 26.1 (CoolProp real-gas H2) | -2.7 % | -2.7 % | agrees |
| C-401 SAF draw T | 210 C | 212 C | 211.8-212.5 C | -1.2 % | 0 % | closed |
| Naphtha dew T | 120 C | 112 C | 112.4 C (CoolProp, PR) | +6.7 % | 0 % | closed |
| RD bottoms T | 320 C | 303 C | 303.1 C bubble n-C16 | +5.6 % | 0 % | closed |
| E-401 | 4.7 kW | 87 kW | 87.2 kW (PR energy balance) | -1.9 % (vs 4.8) | 0 % (frozen) | closed; naphtha flow grew 5.6x |
| E-403 | 420 kW | 462 kW (feed 210 C, 52 mol % vapour) | 696 kW at 250 C (100 % vapour) | -39.7 % | not comparable: feed T changed | reduced: 250 C gives negative reboiler duty (-118 kW) |
| E-402 | 0 kW (clamped) | 160 kW | column energy balance | clamp | n/a | closed (no clamp) |
| V-201 paraffin to vapour | 0 % (sharp) | 9.0 % | 26.6 % (Rev A flows, PR) | disagrees | PR at Rev B flows: 9.0 % | closed: carry-over modelled (stream 25) |
| SAF yield | 0.80 t/t UCO (24,000 t/yr) | 0.446 t/t (13388 t/yr) | 0.45-0.58 derived; NREL 0.461 (13,830 t/yr) | +38 % | -3.2 % vs NREL on raw oil | closed (clean-oil basis explains the gap) |
| SAF share of liquids | 96.4 % | 54.2 % | 60-70 % (Tao) | unexplained | about 54 %, below Tao range; NREL jet mode 46.1/85.0 = 54 % | reduced; Tao is a hydrocracked upper bound |
| Naphtha share of liquids | 0.9 % | 10.0 % | 10 % (NREL 8.5/85.0); 32 % Tao jatropha | unexplained | agrees with NREL | closed vs NREL; Tao 32 % not followed |
| Hydrocracking loss | 1.4 % | stage-2 H2 0.45 wt % of oil; C4+C2 2.3 % of oil | about 8 wt % (CBSCI); NREL light ends +9 points | -82 % | reduced, not reproduced | unchanged-ish: pseudo-cuts under-predict cracking; licensor item |
| Total H2 | 3.77 wt % of oil | 3.76 wt % | 4.5 (NREL jet), 1.5-3.8 (Ecofining) | -16 % vs NREL | -16 % vs NREL | unchanged: stage-2 H2 0.45 wt % |
| H2 per t SAF | 46.4 kg | 83 kg | 55-60 (OIES net); about 98 NREL total-oil basis | -16 % | above OIES, below NREL basis | reduced; bases differ |
| Propane | 5.06 wt % | 5.06 wt % | 5-5.2 | 1.1 % | 1.1 % | unchanged (agrees) |
| HT paraffin | 85.4 wt % | 85.4 wt % | 75-85 | 3.4 % | 3.4 % | unchanged (agrees) |
| CO + CO2 | 1.89 wt % | 1.89 wt % | 1.8 (CBSCI); NREL 4.0 | 4.8 % | -54 % vs NREL | unchanged: A pathway shares, not tuned |
| Reaction water | 11.0 wt % | 10.8 wt % of raw | NREL aqueous 8.0 | n/a | +35 % | new comparison, unchanged |
| PSV coverage V-102, V-201, V-401 | none, no reason | PSV-207, PSV-204, zone PSV-205 (stated reason) | lint | 3 failures | 0 failures | closed |

Notes. The runaway rises are not directly comparable with the validator's: Rev B recycle is 5.91 (derived from Q for a 45 K bed rise) and the rise includes circulating-gas heat capacity. With recycle 1:1 (NREL text) the unquenched rise would be 135 K.

## (b) What could not be closed

- Recycle 5.9 (derived) vs NREL "up to 1:1 with interbed gas quench": not reconciled; heat of reaction needs licensor confirmation (triglyceride Hf are group-contribution estimates; two routes differ 8 %).
- Stage-2 H2, cracking-gas yield, CO+CO2 and water split: pseudo-cut model and A pathway shares do not reproduce NREL (total H2 -16 %, CO+CO2 -54 %, water +35 %). Not tuned to match.
- Fractionator: 250 C feed (validator, E-403 696 kW) gives a negative reboiler duty, so Rev B uses 210 C (A). Reflux ratio 1.0 and draw temperatures need a simulator.
- V-201 carry-over 9.0 % is PR with kij = 0; water/H2 solubility unreliable. Heat of reaction at 25 C without temperature correction.

## (c) Safety items now present vs gaps

Present (sheets 1, 6, 7, 8): relief schedule of 19 rows covering every vessel, column, reactor, tank and exchanger group; new PSV-204 (V-201), PSV-207 (V-102), PVRV-101/401/402/403, HV-301, XV-402, XV-403, E-404; screening sizes via `process_safety.relief` for PSV-202, PSV-203 (K-201 blocked discharge) and PSV-205; 7 SIFs with assumed SIL (A); ESD matrix 12 initiators x 11 final elements; F&G, isolation, bund (110 % / 25 %, HSG176), layout (EIGA, HSG176), 9 HAZOP-style nodes, 5 inherent-safety options. Free sources used (R): OSHA 1910.119, HSG176, HSG238, EIGA Doc 15/21, CSB Kuraray, HSE COMAH layout.
Gaps: fire-case and runaway relief loads (need vessel dimensions, kinetics); TSV on exchangers not drawn; tank emergency vents and rundown isolation valves (TK-401/403); flare radiation and KOD size; SIL verification and LOPA (IEC 61511, CCPS not obtained); API 520/521/2000, OISD (106/116/118/144/163/241), PESO, NFPA not obtained; fire-water rate; detector voting, set points and H2-flame detector type.

## (d) To verify with a licensor or vendor

Heat of reaction and bed limits; recycle vs interbed-quench design; stage-2 selectivity and H2 use; V-201/V-202 VLE (three-phase); column design and feed condition; catalyst and metallurgy limits (hydrogen attack); runaway relief load and depressuring rate; hot-oil system; H2 unit scope.

## Independent re-checks after the rebuild

Frozen constants reproduced on re-run (PHI 0.0904, E-403 462.5, E-402 160.3, E-401 87.2 kW). Bubble/dew at 1.5 bar: C11 211.8 C, C16 303.1 C, C7 112.4 C. CoolProp cp 3.232. K-201 26.1 vs 25.4 kW. E-202 PR 1,123 vs generator 1,177 kW (+4.8 %).

## Lint

Stream diamonds on sheet 1: 25; HMB columns: 25 (one to one). 0 duplicate drawing tags; every tag named on sheets 3 to 8 is drawn on sheet 1. V-102, V-201, V-401 now covered; E-404 drawn; P-101, P-402A/B, E-405, V-501, FL-501 in the equipment list.

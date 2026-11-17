# CBG 10 TPD P&ID set, Rev B results (generator `scripts/gen_pid_cbg.py`, 11 Nov 2026)

Outputs: `docs/pid/CBG_PID_Set_RevB.html/.pdf` (7 sheets). Screening aid, not certified design. Deviation = (ours - reference) / reference. Table also in `CBG_REVB_RESULTS.csv`.

## (a) Metrics flagged by the validator

| Metric | Rev A | Rev B | Reference | Dev. before | Dev. after | Status |
|---|---|---|---|---|---|---|
| Feed per t CBG | 16.0 t/t (S) | 20.0 t/t (input A0 = 50 % press mud) | press mud 25; napier 16.7 (CSE slide 24; Bawase p1654) | -36 % vs 25 | 0 % vs blend of the two references (by construction); -20 % vs press-mud-only 25 | closed as a model input; the mix share is still A |
| Raw biogas per t feed | 144.6 Nm3/t | 108 Nm3/t | 92.6 (CSE-derived, press mud); blend of sources 118 to 122 | +56 % | -8 to -11 % vs blend | reduced; residual from napier CH4 55 % (A) and D yields |
| Press mud per Nm3 raw biogas | 6.91 kg | 9.25 kg (blend feed); 12.7 kg press-mud-only | 2.27 kg (Bawase LCI input) | +204 % | +308 % | unchanged: reference implies 441 Nm3/t, outlier against CSE and Bawase p1654 napier figure |
| Methane slip | 1.5 % | 0.64 % (membrane); PSA case 1.25 % | membrane 0.5 to 1.0 (Task 37 slide 15); permits 0.2 to 1 | +50 % above membrane range | inside range | closed |
| CH4 raw per CH4 product | 1.015 | 1.0064 | 1.006 (Bawase) | +0.9 % | +0.04 % | closed |
| Upgrader specific power | 0.240 kWh/Nm3 (shaft) | 0.575 kWh/Nm3 electrical (input); K-201 + K-301 shaft = 0.225 | 0.575 membrane (Bawase p1656); PSA below 0.19 (D) | -58 % | 0 % as input; physics explains 39 % of it | closed as input (single LCI source); 191 kW other load has unstated scope (A) |
| Upgrader power per raw biogas | 0.136 kWh/Nm3 raw | 0.347 | 0.21 to 0.30 (review snippet, grade C) | below range | +16 % above upper bound | unchanged status: grade C reference, not used to set a value |
| FOM per feed mass | 34.1 % | 35.3 % | 45 to 55 (CSE case 4, straw + dung) | -24 % | -21 % | unchanged: reference feed differs |
| FOM cake total solids | 40.5 % | 28.7 % | 28.7 % industrial (Romio 2024 Table 2) | +41 % | 0 % | closed |
| TS capture in cake | 85 % (A11) | 26.8 % (lab 51.8 %) | 26.84 % industrial | +217 % | 0 % | closed |
| FOM mass vs DPR | 18,000 t/yr (S, fixed) | 23,359 t/yr (derived) | DPR 18,000 t/yr | 0 % (input) | +30 % | shown as residual: DPR figure may be after curing |
| K-202 cooling duty | 71.8 kW | 87.6 kW | 87.6 (CoolProp HEOS) | -18 % | 0 % | closed |
| 10 mm hole at 251 bara | 2.87 kg/s | 3.55 kg/s | 3.55 (CoolProp mixture flux x 78.5 mm2 x 0.85); 3.40 pure CH4 | -15.6 % | 0 % (mixture) | closed |
| Z at 251 bara, 40 C | 0.90 (A27) | 0.8776 | 0.878 | +2.5 % | 0 % | closed |
| Off-gas CH4 / oxidiser | 1.9 mol %, 'needs support fuel' | 0.95 mol %, RTO, no support fuel | RTO autothermic from 0.37 vol % (Task 37 slides 10, 18) | flagged | above 0.37 %, RTO limit 10 kW or 1 m3/h exceeded (33 kW, 3.4 m3/h) | closed (conditional on oxidiser type: flare or simple oxidiser would need fuel) |
| K-201 shaft / cooling | 120.0 / 90.7 kW before fix | 120.2 / 106.0 kW | 118.1 / 107.7 (CoolProp, CH4 58.3 %) | fixed in Rev A late | -1.8 % / -1.6 % | closed (agrees within 10 %) |
| Relief on R-301, E-301, M-401, K-201 discharge, CAS-601 | none or text only | PSV-301, PSV-302, PSV-401, PSV-402, PSV-601, TPRD-601 | lint | missing | present on sheet 1 and sheet 6 | closed (drawn); sizing only for PSV-401, PSV-501 |

Closure (asserted in code): mass 0.0000 %, CH4, C, S (H2S), TS (feed less VS destroyed) and water all below 0.001 %. Recomputed independently (own stoichiometry, CoolProp psat, t/t blend, FOM = cake TS / 0.287): raw gas 901.6 Nm3/h and off-gas 0.946 mol % agree to 4 digits.

## (b) What could not be closed

- Napier-class raw CH4 (55 %, A): 150 m3/t with 60 kg CBG/t implies about 50 %; no document gives the napier CH4. Agri residue has no source and is lumped with napier.
- Press-mud mass per Nm3 (Bawase 2.27 kg/Nm3) conflicts with CSE and Bawase's own 25 t/t; treated as an outlier.
- Upgrader power: 0.575 kWh/Nm3 is one LCI inventory with unstated scope; 191 kW of the 313 kW is not explained by K-201 and K-301. Range 0.30 (A) to 0.575; PSA 0.19 (D). Not a plant meter.
- Feed and FOM now differ from the DPR: 200 TPD vs 160 (+25 %), FOM 23,359 vs 18,000 t/yr (+30 %). The DPR 160 TPD fits only an all-napier feed (167 TPD).
- Fire case on gas-filled vessels, TPRD sizing, tube rupture at E-301, tank venting, low-pressure holder venting: no free documented method here, shown as not sized.

## (c) Safety items present vs gaps

Present (sheets 1, 6, 7): relief schedule 15 rows; 11 devices drawn with tags (PRV-201A/B with FA-201A/B, PSV-301, 302, 401, 402, 501, 601, TPRD-601, PVRV-501/502, VT-101, OF-201A/B, FA-401, FA-901); ESD matrix 16 initiators x 11 final elements; 7 SIFs with assumed SIL (A); 8 hazard nodes; 6 inherently safer options; hazardous-area table from Bergin et al. (HSE, IChemE Hazards 33, read in full); detection logic (CH4 at high and low level, H2S) and isolation basis.
Sized with toolkit gas_area: PSV-401 70 mm2 orifice D (set 17.6 barg, A), PSV-501 2.2 mm2 orifice D (set 275 barg, A). API 520 text not read; coefficients unverified.
Gaps (standard not obtained): API 520/521/526/2000, OISD-STD-106/116/118/144/163, PESO SMPV(U) 2016, IEC 61511 / LOPA, IEC 60079-10-1 / Indian hazardous-area code, TPRD and cylinder standards, fire water and layout distances. SIL targets are assumed, no verification.

## (d) Verify with licensor / vendor

Feedstock mix, TS, BMP and CH4 per feed; membrane slip guarantee and electrical kWh/Nm3 including scope; digestate separator cake TS and capture; RTO type and off-gas turndown; holder, digester and blower design and shut-off pressures; compressor package (interstage coolers, separators, relief); cascade tube and TPRD data; filling bay layout and PESO conditions.

## Lint

Stream diamonds 17 of 17 vs HMB columns; every tag named in the relief schedule, SIF list and ESD matrix exists on sheet 1 (68 base tags, 0 missing); every pressure item has a device or a stated reason (sheet 6 rows). Not run: project test suite. Frozen tool run: `/private/tmp/claude-501/venv_val/bin/python /private/tmp/claude-501/cbg_revb/cbg_realgas.py` (CoolProp 8.0.0).

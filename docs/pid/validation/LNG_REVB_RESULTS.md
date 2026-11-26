# LNG liquefaction set Rev B: results (11 Nov 2026)

Generator `scripts/gen_pid_lng.py`; outputs `docs/pid/LNG_PID_Set_RevB.html/.pdf` (7 sheets). CoolProp script kept as `docs/pid/validation/LNG_thermo_revB.py` (run with the venv_val python, `final2`). Repo files were not edited; repo defects are listed in (e).

## (a) Metrics flagged by the validator
| Metric | Rev A | Rev B | Reference | Source | Deviation before | Deviation after | Status |
|---|---|---|---|---|---|---|---|
| NG cooling 233-173 K (kW) | 11,027 | 25,915 at 63.376 kg/s (24,781 at 60.6 kg/s cold-train gas) | 25,915 | CoolProp HEOS enthalpy, LNG_VALIDATION.md | -57.4 | 0.0 | closed |
| NG cooling 173-114 K (kW) | 10,844 | 12,165 at 63.376 (11,633 actual) | 12,165 | same | -10.9 | 0.0 | closed |
| MR loop pressure ratio / suction | 589 / 0.0909 bar(a) | 12.9 in 3 stages / 3.5 bar(a) | physical suction a few bar; Freeport multi-stage MR | LNG_VALIDATION.md; GAP_CLOSURE_THERMO.md (Pe not sourced) | unsound | sound by construction (Pe is A, 3-5 bar) | closed, Pe assumed |
| K-202 propane suction vs frame 55,000-110,000 m3/h | 236,297 (2.1x range) | max stage 93,385 (levels 4-1, 1 casing each) | <=110,000 | repo frame range S[2] | +115 % over range | within range | closed |
| MR LP-stage suction volume (m3/h) | ~700,000 (hand calc) | 97,779 (1 casing, top of range; double-flow LP casing as Qatargas) | <=110,000 | GAP_CLOSURE_THERMO.md (Qatargas 3 casings) | ~6x over range | within range | closed |
| C3:MR shaft power split | propane 36,720 : MR 27,219 kW (MR 43 %) | 26,139 : 40,835 kW (MR 61 %, 1:1.56) | 1:2 to 3 (MR 67-75 %); Qatargas 27:64 MW | Aoki and Kikkawa INIS QA9700008 | MR share 43 % vs 67-75 % | MR share 61 % vs 67-75 % | reduced (not closed: needs licensor split-flow cycle) |
| Specific power, all loops (kWh/t) | 297 (421 with omitted subcool loop) | 323 (324 incl. K-401, K-501) | 300-350 (Qatargas-derived 317-347; Air Products 275-375 C) | GAP_CLOSURE_THERMO.md | +12 % above band with loop | inside band | closed (eta_II 0.40 assumed inside band) |
| V-102 residence time (s) | 97 (47.3 m3, both circuits) | 300 (261 m3, 4,563 mm x 16.0 m) | 300 | repo 300 s basis; validator | -68 % | 0 | closed |
| TK-501 boil-off (%/day) | 0.122 | 0.050 | 0.03-0.05 (design <0.05; 0.02-0.1 range) | GAP_CLOSURE_THERMO.md | +144 % over 0.05 | 0 at upper end | closed |
| Driver fuel | not computed (header 81 MW vs 195 MW need) | 203 MW LHV, tap 2.77 kg/s = 4.4 % of sweet gas; LNG shipped 1.819 mtpa | Freeport electric 1.8 %; GT efficiency 0.33-0.38 (A) | FERC FEIS EIS-0487; GAP_CLOSURE_THERMO.md | -58 % coverage | covered (GT 0.33 assumed) | closed as stated, driver type is A |
| Compression arrangement | single-stage LRC, PR 589 | 3-stage MR, 4-level propane, 2 + 3 casings | multi-stage MR and propane | FERC FEIS Freeport | unexplained | explained | closed |
| Lint: diamonds 6 and 18, XV-504, 6 vessels without relief, PSV-501 naming | 10 failures | 0 failures (diamonds 1-20 match HMB; XV-504 drawn; PSVs drawn; PSV-501A/B drawn twice) | - | generator lint run | 10 | 0 | closed |

Closure after the rebuild (asserted in code): mass 269,003 in / 269,003 out kg/h (error 0.0000 %); elements C, H, N, O max error 0.0008 %; heat 0.0000 % including an explicit unallocated MR refrigeration term of 12,672 kW; propane cascade Qe + W = Qc to 1e-6; MR loop energy equals m (h_cold - h_hot) to 1e-3; NG duties reproduce the validator CoolProp values to 0.3 %.

## (b) Not closed, and why
- C3:MR split 1:1.56 against 1:2 to 3. The MR loop at this flow could deliver 49,085 kW to the cold box against 36,413 kW of NG demand (ratio 1.35). A single-JT MR cycle test (CoolProp, 24 blends, Pe 3 and 5 bar, Pc 45 bar) never met the pinch (minimum approach -3.5 K at best), so the MR flow is derived from power, not from duty. A split-flow C3MR cycle from a licensor is needed.
- Specific power rests on an assumed second-law efficiency 0.40 (A) chosen inside the sourced band; the ideal work 129.1 kWh/t is CoolProp (matches the validator).
- MR blend (N2 4, CH4 32, C2H6 61, C3H8 3 mol %), Pe 3.5 bar, Pc 45 bar, propane levels, GT efficiency 0.33: assumed (A), no source obtained. No C3MR document with per-casing suction volumes was obtained (Air Products PDFs 404, other hosts blocked; stopped there).
- Boil-off 0.05 %/day is the upper end of the sourced range (63,827 m3 tank is smaller than the 260,000 m3 reference).
- Tank and K-501 volume kept at the repo 2 mtpa size; stream 10 phase not computed; CO2 freeze-out not quantified; suction knock-out drums and anti-surge not drawn.

## (c) Safety items now present
- Relief schedule: 19 rows (every vessel, exchanger, tank, bullet, stub, compressor group, flare header); 16 PSV symbols drawn on sheet 1 (PSV-101, 201, 202, 203, 211A/B, 301-305, 401, 501A/B, 701, 702) to F1/F2 headers; sized with the toolkit: V-101 blocked-outlet gas 5,207 mm2 (orifice Q), V-102 fire 1,744 mm2 (orifice L, wetted 178 m2, 36,515 kg/h), TK-501 compressor-trip case 630 mm2 (not governing). Others stated "not sized: needs ...".
- ESD matrix 16 initiators x 13 final elements; 9 SIFs with assumed SIL targets (A); detection and mitigation table (impoundment 110 % = 70,210 m3, exclusion-zone basis 49 CFR 193.2057/2059 with no distances computed, cryogenic embrittlement and RPT, BOG overpressure/vacuum, fire water, ROSOV, F&G logic, layout); 9 HAZOP-style nodes; 5 inherently safer notes.
- Still gaps (standard not obtained): API 520/521/2000/620, NFPA 59A/11/72, EN 1473/14620, IEC 61511, LOPA, OISD, PESO; set pressures and design pressures; flare and fire-water sizing; exclusion distances; ship-shore link.

## (d) To verify with a licensor / vendor
MR composition and split-flow cycle, C3:MR power, per-casing suction volumes and driver selection (GT vs electric), MCHE duty and tube-rupture loads, PSV design pressures and sizes, tank design pressure and rollover/ship-vapour relief, impoundment and exclusion-zone calculations (LNGFIRE3, DEGADIS or validated equivalent).

## (e) Repo defects for the lead (not edited)
1. `liquefaction.py` NG duty ledger uses constant cp (misses condensation: -57 % in the 233-173 K span); replace by an enthalpy integral.
2. LRC loop evaporating pressure 0.0909 bar(a) (dew point of a heavy N2/CH4/C2H6/C3H8 5/30/35/30 blend), pressure ratio 589 in one machine; staging does not fix it.
3. `total_compression_power_kW` omits the PMR (propane) compressor K-202 and the subcooling loop.
4. V-102 sized on the precool propane flow only (97 s on the combined flow).
5. No driver fuel demand or feed-gas draw; shipped LNG overstated.
6. Tank boil-off 0.122 %/day against a sourced design below 0.05 %/day.
7. End-flash inlet -160 C vs MCHE target -159 C (1 K).

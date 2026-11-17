# REFINERY Rev B results

Set: `docs/pid/REFINERY_PID_Set_RevB.{html,pdf}` (8 sheets, generator `scripts/gen_pid_refinery.py`), 2026-11-11. Screening aid. Full rows: `REFINERY_REVB_RESULTS.csv`.

## (a) Metrics flagged by the validator

| Metric | Rev A | Rev B | Reference | Dev. A % | Dev. B % | Status |
|---|---|---|---|---|---|---|
| Crude slate S, wt% | 2.90 | 2.26 | 2.264 (2.10-2.39) IOCL EC report 2020 Annex-4 | 28.25 | 0.00 | closed (fitted to it; two-target refit, a fit not a purchase list) |
| Petcoke, % of crude | 11.92 | 8.20 | 7.77 (7.2-8.2) EC report; 8.0 investor slide 7 | 53.39 | 5.53 | closed (within 7.2-8.2, top edge) |
| Coker coke, wt% of VR | 43.60 | 30.00 | 27-35, central 30 (UOP 2021, JIP T41, WRI); PTQ 1.23 x CCR = 30.7 | 30.16 | 0.00 | closed |
| Coker gas, wt% of VR | 11.72 | 9.07 | PTQ 7.8+0.051 CCR (9.19 at CCR 27.25) | 27.58 | 0.00 | closed (equals the correlation at the new CCR by construction) |
| Coker naphtha, wt% of VR | 9.83 | 11.09 | PTQ 25.37-0.573 CCR (9.75 at CCR 27.25) | 0.80 | 0.00 | unchanged in kind: tracks the correlation; value rises because the slate CCR fell to 24.9 |
| Coker gas oil, wt% of VR | 34.84 | 49.84 | 47.5 (by difference at coke 33.5) | -26.64 | 4.93 | reduced to +5 % (by difference; follows coke 30 vs 33.5) |
| SR naphtha to NHT, Mt/yr | 1.61 | 1.28 | 3.96 NHT nameplate (IOCL OEP sec 1.2) | -59.33 | -67.76 | unchanged cause, WORSE: lighter-end-poor slate; 200 C end point reaches 2.05 (2.50 with coker naphtha); no source explains nameplate |
| Treated VGO to FCC, Mt/yr | 4.10 | 4.49 | 4.17 INDMAX (OEP) | -1.66 | 7.57 | WORSE but within 10 %: cost of the sulphur fit |
| Vacuum residue to coker, Mt/yr | 4.10 | 4.10 | 4.4 DCU nameplate | -6.82 | -6.82 | unchanged (fitted to 4.1/15) |
| HT sulphur to SRU, t/d | 481.30 | 374.63 | 696 t/d product S (EC report) | -30.85 | -46.17 | unchanged cause, WORSE: coker and FCC sulphur routing not modelled |
| LPG+gasoline+middle distillate, % crude | 79.34 | 83.58 | 81 (investor slide 7) | -2.06 | 3.19 | within 10 % before and after |
| Crude heater duty, MW | 216.59 | 210.56 | independent PR flash 183-199 MW (ideal-gas n-alkane: 202) | 7.22 | +6 to +15 | unchanged (no plant value); independent route is now Peng-Robinson |
| HT H2, scf/bbl (diesel / VGO) | S-only 167 / 358 (Rev A) | S-only 123 / 255 | 150-300 scf/bbl (ENERGY STAR, secondary) |  |  | unchanged (floor kept, range on sheet 3) |
| FCC yields | reference case | reference case | none found; repo run on this VGO differs (LPG -5, LCO+slurry +7 points) |  |  | unchanged; stated as reference case, not run on this VGO |

Corrections applied: 6 (slate refit, coke 30 wt%, coker gas, coker naphtha slope, gas oil by difference, closure asserts extended with a hydrogen balance); 3 range or check tables added (H2 band, naphtha end point, PR-flash heater duty) plus the FCC repo-run comparison. Biggest effects: petcoke 11.9 to 8.2 % of crude; crude S 2.90 to 2.26 wt%; coker gas oil 34.8 to 49.8 wt% of VR.

## (b) Not closed, and why
- NHT feed: no source explains the 3.96 Mt/yr nameplate; the end-point sweep reaches about half (and Rev B is further away, 68 % low, because the refit slate is poorer in naphtha).
- FCC yields: no open table; reference case kept; repo run with CoolProp for this VGO gives 69.9 % conversion and a 757 C regenerator (Rev A basket 772 C).
- Heater duty: repo 210.6 MW is 6 to 15 % above the PR-flash range 183-199 MW; surrogates and coil pressure are assumed.
- H2 (A3): floor kept; no service-specific band. SRU sulphur: coker and FCC routing not modelled.
- Side effects of the S refit: treated VGO to FCC is now +7.6 % against INDMAX (was -2 %); HT sulphur is 46 % below the SRU product sulphur.
- Not checked: carbon and energy balances.

## (c) Safety items now present vs gaps
Present: relief schedule with 26 items (14 PSV tags drawn plus HV-204; was 4 PSVs); ESD cause-and-effect matrix (15 initiators, 15 columns, fail positions); 9 SIFs with assumed SIL (A) and a fire-protection row; detection and mitigation basis; 9 hazard-identification nodes; 6 inherently safer design notes; new sheet-1 tags AT-101A, AT-204A/B, LHD-001/801, LAHH-901, LAHH-401A/B, FSLL-401, XV-404, XV-302, XV-001, TAHH-302, PDALL-301, ESD-4. Lint: 0 scenario tags missing from sheet 1; 24 stream diamonds = 24 HMB columns; every schedule item has a device or a written reason.
Gaps: no item is sized (no vessel dimensions or loads); OISD-STD-106/108/111/112/116/117/118/129/133/152/153/163/164/241 not read (INR 10,500 each plus registration); API 520/521/526/2000/941, IEC 61511, LOPA, NFPA not obtained; SIL targets are assumed; bund volume, fire-water and foam demand, safety distances for large tanks, alarm philosophy, independent tank overfill trip, coker blowdown D-402 and T-801 outlet ROSOV not drawn or computed.

## (d) To verify with a licensor or vendor
Coker yields on the real feed assay and CCR; actual crude basket; FCC yield and SIS logic; hydrotreater H2 including aromatics and nitrogen; crude heater duty from an assay-based flash; relief loads and the simultaneous flare case; SIL by LOPA; NHT feed definition.

## Independent re-checks after the rebuild (CoolProp 8.0, chemicals; script in session scratch)
H2S from S removed 16,593 vs 16,591 kg/h (+0.013 %); chemical H2 2,944.7 vs 2,944.1; petcoke 8.20 % reproduced; sulphur closure -0.013 %; scf of H2 2.410 g vs CoolProp density 2.408 g. Previously failing: crude S (now 2.26) and petcoke (8.2 %) pass; coker coke, gas now within the references; NHT, SRU S and FCC-feed deviations did not improve (see above).

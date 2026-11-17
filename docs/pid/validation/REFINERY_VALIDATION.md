# REFINERY P&ID set: validation against an independent calculation and public documents

Set: `docs/pid/REFINERY_PID_Set_RevA` (generator `scripts/gen_pid_refinery.py`), validated 2026-11-11. Screening aid. Full rows: `REFINERY_comparisons.csv`.

## Verdicts

| Check | Verdict |
|---|---|
| 1 Independent recomputation | 15 quantities, 15 agree. But 14 are re-evaluations of the generator's own formulae (they test arithmetic and units, not the model). Only the crude heater duty is a different route: +7.2 %, inside the 10 % tolerance, with the weak assumptions listed below. |
| 2 Real-world documents | 24 comparisons, all grade A (document text read): 8 within tolerance, 12 explained, 4 unexplained. No reference found for FCC yields, CDU duty, or the assay values. |
| 3 Structural lint | 2 failures found and fixed (stream 14 had no diamond; 5 scenario valves and ESD-3 were absent from sheet 1). 1 open design gap (relief coverage). 3 minor text overflows. |

Honest reading: the mass balance is internally consistent and the unit throughputs line up with Paradip's nameplates (VR to coker 4.10 vs 4.4 Mt/yr, FCC feed 4.10 vs 4.17). The yields downstream of the coker are the weak part, and the slate is sourer and heavier than the real Paradip mix.

## 1 Independent recomputation (venv_val: CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2; script `val_refinery/chk1.py` in the session scratch dir)

| Quantity | Ours | Independent | Dev | Note |
|---|---|---|---|---|
| H2S from S removed, 4 HT units (kg/h) | 21,320 | 21,318 | +0.01 % | MW from CoolProp H2S and chemicals S, vs 34.08/32.06 |
| Chemical H2, 3 mol/mol S (kg/h) | 3,783 | 3,782 | +0.02 % | re-evaluation |
| HT reactor volumes R-201..204 (m3) | 49.5 / 87.1 / 241.6 / 535.4 | same | 0.00 % | feed volume from bpd and LHSV; re-evaluation |
| Coker coke / gas / naphtha (kg/h) | 204,080 / 54,874 / 45,998 | same | 0.00 % | G&H forms as stated in A5; re-evaluation |
| Coke drum volume (m3) | 6,122 | 6,122 | 0.00 % | 18 h, 800 kg/m3, 75 % fill |
| Crude kg/h, bpd, API | 1,712,329 / 289,820 / 26.99 | same | <0.01 % | 15 Mt/yr / 8,760 h |
| Sulphur in cuts vs crude (kg/h) | 49,709 | 49,716 | -0.0135 % | residual is LPG S taken as zero |
| Crude heater duty 250 to 360 C (MW) | 216.6 | 202.0 | +7.2 % | surrogates n-C4, C8, C12, C16, C24; ideal-gas vapour; 47.6 wt% vapour = all light cuts + 10.7 % of VGO (my assumption); residue cp taken as n-C24 liquid |

Not recomputable here: FCC yields (no kinetics), reactor heats of reaction, K-201 power (no delivery pressure), relief sizing (no relief loads).

## 2 Documents (selected rows; all in the CSV)

| Metric | Ours | Reference | Dev | Source (grade A) | Verdict |
|---|---|---|---|---|---|
| Crude S | 2.90 wt% | 2.26 (mean Dec19-Apr20; range 2.10-2.39) | +28 % | IOCL Paradip EC compliance report 2020, Annexure-4 | explained: slate heavier |
| Petcoke, % crude | 11.9 | 7.8 (monthly 7.2-8.2); slide 8 | +53 % | same; IOCL investor presentation Jun 2017 slide 7 | explained: slate plus coker coke eq. |
| LPG pool, % crude | 8.4 | 8.1 | +3 % | EC report | within |
| Gasoline range / middle distillate, % crude | 26.9 / 44.0 | 25 (MS) / 46.5 (HSD+ATF+SKO) | +8 % / -5 % | slide 7; EC report | within |
| LPG+gasoline+distillate | 79.3 | 81 | -2 % | slide 7 | within |
| VR to coker | 4.10 Mt/yr | DCU 4.4 | -7 % | IOCL Paradip On-Site Emergency Plan sec 1.2 | explained (HVGO blend-in) |
| Treated VGO to FCC | 4.10 | INDMAX 4.17 | -2 % | same | within |
| SR naphtha to NHT | 1.61 | NHT 3.96 | -59 % | same | unexplained |
| Coker coke / gas / naphtha / gas oil, wt% feed at CCR 27.25 | 43.6 / 11.7 / 9.8 / 34.8 | 33.5 / 9.2 / 9.8 / 47.5 | +30 / +28 / +1 / -27 % | PTQ Q1 2020 "Estimating delayed coker yields", Table 1 (CCR 10-29) | coke, gas, gas oil unexplained |
| Diesel HT chemical H2 | 0.29 kg/100 kg; 167 scf/bbl | 0.37-0.82 kg/100 kg (lab); 150-300 scf/bbl | -22 to -65 % | PTQ Q3 2018 Tables 1-2; ENERGY STAR guide 2015 (quotes Gary 2007, secondary) | explained (A3: S-only stoichiometry) |
| VGO HT H2 | 358 scf/bbl | 150-300 | +19 % | ENERGY STAR | explained |

Not used: nsenergybusiness.com returned 403 (stopped on that host); its 4.1 Mt/yr coker figure is search-snippet only, not cited. The PTQ paper is a correlation paper, not plant data; "explained" verdicts are plausibility arguments, not proof.

## 3 Structural lint (stdlib script `val_refinery/lint.py`, run on the regenerated HTML)

- Stream diamonds on sheet 1: 28 markers, 24 distinct numbers; HMB columns: 24. Before fix: stream 14 (H2 purge) had a column but no diamond. After: 0 mismatches. Streams 7 and 13 carry repeated diamonds on purpose.
- Equipment-list tags (11 rows) all appear on the drawing; 0 duplicate tags. 12 drawn tags are not in the equipment list (P-101, E-101/102/103, D-101, D-102, H-102, R-302, K-301, H-401, C-401, SV-301/302): informational.
- Relief: 4 PSVs (101, 204, 301, 401) for 14 pressure items (C-101, C-102, C-301, C-401, D-101, D-102, D-401A/B, D-901, R-201..204, R-301, R-302). 10 have no PSV and no stated reason. OPEN. All 4 PSVs have a drawn discharge (3 to the relief riser or header, PSV-401 to a local "FL" tie).
- ESD-type tags named on sheets 3 and 4: before fix XV-102, XV-103, XV-205, XV-206, XV-301 and ESD-3 existed only on sheet 3. After fix: 0 missing.
- Text clipping: nothing beyond the frame. 7 overlapping text pairs by width estimate: 3 loop-table rows (function text runs into the Basis column), 3 on sheet 2 (closure box lines touch the column border; confirmed by rendering one), 1 on sheet 4 (T-801 label vs "bund (A)"). Not fixed.

## Generator fix made (outright tag mismatches only)

`scripts/gen_pid_refinery.py`: added diamond 14 with an H2 purge stub on sheet 1; added XV-102/103/205/206, XV-301 and the ESD-3 box with its signal line to sheet 1 (same coordinates as sheet 3), plus two rows in the loop table. HTML and PDF regenerated (4 pages), closure asserts pass (closure 0.0000 %, S error -0.0135 %). New valves sit close to existing bubbles on sheet 1 (XV-103 beside TIC-101, XV-301 beside the signal line); legible but crowded. No A value changed.

## What to change (ranked)

1. Coker yields (A5): coke is +30 % vs the high-CCR correlation and 11.9 % of crude vs 7.2-8.2 % at the real unit. Use a correlation valid at CCR 27 (or run the repo's coker with 1.23 x CCR) and report both; this also moves gas oil, FCC feed and the light-product pools.
2. Slate: the 57/43 Upper Zakum / Cold Lake blend gives 2.90 wt% S vs 2.1-2.4 at Paradip. State on sheet 1 that it is a heavy-case basket, or refit to S and petcoke 8 %.
3. Naphtha cut: SR naphtha is 1.6 Mt/yr vs NHT nameplate 3.96 and CCR 2.98; check the 150 C end point.
4. Relief coverage: add PSVs or stated reasons for the 10 vessels without one (sheet 1 and the equipment list).
5. H2 (A3): S-only stoichiometry under-states naphtha, kerosene and diesel consumption; add an aromatics term or label the H2 figure as a floor.
6. Sulphur: add coker and FCC sulphur routing so SRU load can be compared with 2 x 525 t/d.
7. FCC yields (A4) and CDU duty remain unvalidated; the duty check used surrogates, so treat +7 % as plausibility only.
8. Tidy the 7 text overlaps and add the 12 unlisted tags to the equipment list.

# SAF (HEFA, 30,000 t/yr UCO) P&ID set: validation against references and an independent calculation

Generator: `scripts/gen_pid_saf.py`. Date of check: 2026-11-11. Screening-aid validation only. All comparison rows are in `SAF_comparisons.csv`.

## Verdicts

| Check | Verdict |
|---|---|
| 1 Independent recomputation | 16 quantities recomputed (CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2): 10 agree, 6 disagree. Stoichiometry, H2 demand, E-202, K-201, C-401 temperatures agree. Heat of reaction, runaway temperature rise, liquid cp, E-403 and the V-201 split do not. |
| 2 Real-world references | 14 comparisons (grade A: 10, grade C: 4). Within tolerance 5, explained 3, unexplained 6. By-product and H2 ratios agree with commercial HEFA data. The SAF-heavy slate does not. |
| 3 Structural lint | Streams 24/24 match HMB columns; 26/26 listed tags are on the drawing; 0 duplicate drawing tags; 4/4 PSV have a drawn flare destination. 1 failure fixed (XV-401 was named on sheet 4 but absent from sheet 1). 3 open (V-102, V-201, V-401 have no PSV and no stated reason). |

## Known open item: can the template yields close? No.

Template: 30,000 t/yr UCO, SAF 24,000, RD + naphtha 4,500. The generator holds SAF at 24,000 (S) and computes only 891 t/yr of RD + naphtha. Both numbers fail against the stoichiometric ceiling:

- Hydrotreated n-paraffin is 85.4 % of clean UCO by our own and an independent stoichiometry (3,186 of 3,731 kg/h); propane 5.06 %, CO + CO2 1.9 %, water 11.0 % take the rest. Commercial HEFA data give 75-85 % (Ecofining), 82.6 % (Neste) (CBSCI 2019, Table 2) and about 1.2 t oil per t liquid fuel, i.e. 83 % (OIES ET-51).
- SAF + RD + naphtha in the template = 28,500 t/yr = 95 % of raw UCO. That exceeds the 83-85 % ceiling by 10 to 12 points, so no slate can close it.
- Credible slate for 30,000 t/yr UCO in max-jet mode: liquids 75-83 % (hydrocracking costs about 8 wt%, CBSCI 2019) times jet share 60-70 % (Tao 2017) gives SAF 0.45-0.58 t/t, i.e. about 13,500 to 17,500 t/yr SAF, with roughly 5,000 to 11,000 t/yr of naphtha, RD and light ends and about 1,500 t/yr propane. For 24,000 t/yr SAF the UCO need is about 41,000 to 53,000 t/yr. In diesel-lean mode (SAF a small fraction) the 4,500 t/yr RD + naphtha is plausible but SAF would be far below 24,000.
- Likely cause in the generator: the S quantities themselves, then A inputs `CG_OF_SAF = 2 %` and `N_SAF = 11` (hydrocracking yield loss 1.4 % of paraffin vs about 8 wt% reported; one C11 pseudo-component per cut, which needs more C11 molecules than the parent paraffins can supply by single scission: 19.4 kmol/h SAF vs 12.8 kmol/h parent chains).

## Check 1: independent recomputation (tolerance 2 % stoichiometry, 10 % duties)

| Quantity | Ours | Independent | Dev. | Verdict |
|---|---|---|---|---|
| Mean chain molar mass | 290.64 g/mol | 290.63 (chemicals MW of 4 TG) | 0.0 % | agrees |
| Stage-1 H2 | 123.45 kg/h | 123.45 | 0.0 % | agrees |
| Propane / water / CO2+CO / HT paraffin | 188.7 / 409.3 / 70.4 / 3,186 kg/h | identical | 0.0 % | agrees |
| E-202 duty | 667 kW | 665 kW (CoolProp, dew 165 C at p_w 7.05 bar) | 0.4 % | agrees |
| K-201 work, discharge T | 25.5 kW, 65.3 C | 26.2 kW, 65.2 C (CoolProp real H2) | 2.7 % | agrees |
| C-401 draws | SAF 210 C | bubble n-C11 211.8-212.5 C; naphtha dew 112.4 C (ours 120) | -1.2 % | agrees |
| E-401 | 4.7 kW | 4.8 kW | 1.9 % | agrees |
| Stage-1 heat of reaction | 312 kW (0.30 MJ/kg) | 1,059-1,151 kW (1.02-1.11 MJ/kg, two Hf routes) | -70 % | disagrees |
| No-diluent runaway rise | 112 K | 316-344 K | -64 % | disagrees |
| No-quench rise | 64 K | 144-156 K | -55 % | disagrees |
| Liquid cp in duties | 2.3 kJ/kg/K | 3.23 (CoolProp n-dodecane, 250-340 C, 50 bar) | -29 % | disagrees |
| E-403 | 420 kW | 696 kW (feed is 100 % vapour at 250 C, 1.5 bar; SAF latent heat 214 kW alone) | -40 % | disagrees |
| V-201 split | sharp (0 % paraffin to vapour) | 27 % of paraffin in vapour (PR EOS, kij = 0; screening) | n/a | disagrees |

Notes. (a) The "R-201 heat release" is not a heat of reaction: it is sensible heat for the assumed 45 K bed rise, so DT_R1, R_TOT and CP_L are mutually inconsistent with the reaction enthalpy. With the computed heat, holding a 45 K rise needs total liquid-to-fresh feed of about 6.6 to 7.2 (R_TOT about 5.6 to 6.2) rather than 2.5. Sheet 4 runaway numbers are therefore understated by a factor 2.3 to 2.9. (b) The two heat-of-reaction routes differ by 8 %: the triglyceride Hf values in `chemicals` are group-contribution estimates, so treat 1.0 to 1.1 MJ/kg as +/-10 %. (c) Not recomputable here: licensor-grade hydrocracking selectivity, and hydrogen/water phase behaviour in the separators (PR with kij = 0 is unreliable for water and H2). E-402 is clamped at 0 kW in the generator; with a fully vaporised feed that is not meaningful.

## Check 2: real-world references

See the CSV for the full table with sources and grades. Summary:

| Metric | Ours | Reference | Source | Grade | Verdict |
|---|---|---|---|---|---|
| H2, all stages | 3.77 wt% of UCO | 1.5-3.8 (Ecofining), 3.2 (Neste), 2.5 (Topsoe) | CBSCI 2019, Table 2 | A | explained, top of range |
| H2 per t SAF | 46.4 kg/t | 55-60 kg/t | OIES ET-51, Table 5 | A | explained (-16 %) |
| Propane | 5.06 wt% | 5 to 5.2 | CBSCI Table 2 | A | agrees |
| HT paraffin | 85.4 wt% | 75-85, 82.6 | CBSCI Table 2; PNNL-38096 | A | agrees |
| CO + CO2 | 1.89 wt% | 1.8 | CBSCI Table 2 | A | agrees |
| Liquid fuel per oil | 84.2 % | 83.3 % | OIES ET-51 | A | agrees |
| SAF share of liquids | 96.4 % | 60-70 % | Tao 2017 | A | unexplained |
| SAF per t UCO | 0.80 | 0.45-0.58 (derived) | CBSCI, OIES, Tao | A | unexplained |
| Naphtha share (max-jet) | 0.9 % | 32 % (jatropha case) | Tao 2017 | A | unexplained |
| Hydrocracking loss | 1.4 % | about 8 wt% | CBSCI 2019 | A | unexplained |
| Four grade-C rows | see CSV | palm 0.44 t/t; jet 59.9 % of liquids; UCO Aspen 2.9 wt% H2, 5.4 % propane | search excerpts | C | 2 unexplained, 1 explained, 1 agrees |

Not found: steam, power or cooling-water per tonne product, equipment sizes or counts, and a yield statement in any Indian project document. IndianOil Panipat (UCO to 30,000 t/yr SAF, Reuters 10 Jul 2025) and NRL (EOI for 24,000 t/yr UCO, 27 Jun 2025) are co-processing in existing hydrotreaters and publish no yield; Neste's interim report gives sales volumes only. IFPEN OGST 2016 (Starck et al.) sits behind a DataDome challenge and ICAO's India feasibility study behind a Cloudflare challenge; both were not bypassed. The ICAO study and the Starck stoichiometry remain unread.

## Check 3: structural lint (stdlib script, regenerated HTML)

- 24 diamonds on sheet 1, 24 HMB columns on sheet 2, one-to-one; no repeated numbers.
- Equipment list: 24 rows (26 tags after expanding TK-401/402/403): all on the drawing. 0 duplicate tags on the drawing.
- Drawn but not in the equipment list (warning): P-101, P-402A/B (named only in a note), E-405, V-501, FL-501. E-404 is in the duty list and not drawn (the sheet says so).
- PSV: 4 (PSV-201, -202, -203, -205), each with a drawn line to the flare header. No PSV-204 (numbering gap). V-301 is covered by the text "PSV-203 (R-301 loop)"; V-102, V-201, V-401 have no PSV and no stated reason (3 failures). Tanks carry PVRV in the list.
- ESD valves: XV-201, XV-202, HV-201 present. XV-401 (sheet 4 scenario S4) was missing from sheet 1: fixed, 0 failures now.
- Text clipping: estimate from 0.53 em per character found 0 texts beyond the page, the drawing frame, or an HMB column. Not a rendered check.

## Generator fix made

`scripts/gen_pid_saf.py`: added the bottoms shutdown valve XV-401 (actuated ball valve, red, label) on the RD bottoms line of C-401 on sheet 1 so that the scenario S4 text matches the drawing. Regenerated `docs/pid/SAF_PID_Set_RevA.html` and `.pdf`; closure assert passed ("ok 4 closure in 3,929 out 3,929 err 0.000 %"). No A value was changed.

## What to change, ranked

1. Resolve the template yields (S): SAF 24,000 + RD/naphtha 4,500 cannot close at 30,000 t/yr UCO. Choose either UCO about 41,000-53,000 t/yr for 24,000 t/yr SAF, or SAF about 13,500-17,500 t/yr at 30,000 t/yr UCO, and re-state RD/naphtha/light ends from a max-jet slate (Tao 2017: naphtha about 30 %, jet 60-70 % of liquid).
2. Derive R-201 heat release from the reaction enthalpy (about 1.0-1.1 MJ/kg UCO), not from DT_R1 = 45 K; recheck R_TOT (1.5 gives about 110 K total rise), CP_L (3.2 not 2.3) and the sheet 4 runaway figures (understated 2.3-2.9 times). Likely A causes: DT_R1, R_TOT, CP_L.
3. Replace CG_OF_SAF = 2 % and the single C11 pseudo-component with a cracking yield that reproduces about 8 wt% loss and a C9-C15 jet cut.
4. Redo the C-401 duties with a vapour or partly vapour feed (E-403 about 700 kW, E-402 not clamped), or lower the feed temperature or raise the column pressure.
5. Allow hydrocarbon carry-over in V-201 (about 27 % of paraffin by PR screening) and a hydrocarbon liquid outlet on V-202; confirm in a process simulator.
6. Add PSV or a stated protection reason for V-102, V-201, V-401; add P-101, P-402A/B, E-405, V-501, FL-501 to the equipment list; draw or delete E-404.
7. Add a sourced benchmark line for stage-2 H2 (OIES 55-60 kg/t SAF vs ours 46).

## Sources read (grade A unless stated)

CBSCI, HEFA Production and Feedstock Selection (2019), Table 2 and section 2.2.1; OIES ET-51 Drop-In Decarbonization (Dec 2025), sections 3.2.1 and 3.3, Table 5; Tao et al., Techno-economic and resource analysis of hydroprocessed renewable jet fuel, Biotechnol Biofuels 10:261 (2017), text and Table 3; PNNL-38096 (Nov 2025), restating Rispoli (2015) ranges. Grade C: search excerpts of MDPI Sustainability 17(4):1584, Biomass and Bioenergy S0961953424001223, Energy Conversion and Management S0196890425009847, Reuters (Panipat). Fetched into `<scratch>/val_saf/`. Independent scripts: `<scratch>/val_saf/calc/` and `<scratch>/val_saf/lint/lint.py`.

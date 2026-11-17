# CBG 10 TPD P&ID set: validation (generator `scripts/gen_pid_cbg.py`, 11 Nov 2026)

Per-comparison rows with sources: `CBG_comparisons.csv`. Screening aid, not certified design.

## Verdicts

| Check | Verdict |
|---|---|
| 1 Independent recomputation | 17 quantities recomputed (CoolProp 8.0, own stoichiometry). 14 agree, 3 disagree. One real arithmetic fault (K-201 stage-2 inlet temperature) found and fixed; two disagreements are explained by ideal-gas formulas at 250 bar. |
| 2 Real-world references | Weak. 9 comparisons (8 grade A, 1 grade C): 1 within tolerance, 4 explained (hypotheses, unconfirmed), 4 unexplained. No project report (DPR/EIA) with plant mass balance was found; the gaps are in feed per product, cake solids and upgrader power. |
| 3 Structural lint | 3 failure groups found before the fix; 2 fixed, 1 reported (relief coverage). |

## Check 1: recomputation (tolerance 2 % stoichiometry, 10 % duties)

| Quantity | Generator | Independent | Dev % | Verdict |
|---|---|---|---|---|
| CBG molar mass | 17.1616 | 17.1615 | 0.0 | agrees |
| Raw biogas dry | 964.3 Nm3/h | 964.3 | 0.0 | agrees |
| Off-gas CH4 (stream 12) | 1.902 mol % | 1.902 | 0.0 | agrees (confirms the open item: oxidiser needs support fuel) |
| Water at 38 C saturation | 4.00 mass % | 4.10 | +2.5 | agrees |
| Condensed at 5 C | 90 % | 87.8 % | -2.4 | agrees; residual vapour 6.4 vs 5.1 kg/h |
| E-301 duty | 45.3 kW | 47.1 | +3.9 | agrees |
| K-201 shaft | 121.0 kW | 126.4 | -4.3 | within tolerance but formula wrong (see fix); now 128.6 (+1.7 %) |
| K-201 cooling | 90.7 kW | 115.4 | -21.4 | disagrees; same fault; now 113.4 (-1.7 %) |
| K-202 shaft | 71.8 kW | 68.2 (pure CH4 73.3) | +5.2 | agrees |
| K-202 cooling | 71.8 kW | 87.6 | -18.0 | explained: ideal-gas cp, real gas enthalpy departure at 250 bar |
| Z at 251 bar, 40 C | 0.90 | 0.878 | +2.5 | agrees |
| Cascade 3 m3 inventory | 551.5 kg | 565.6 | -2.5 | agrees |
| 10 mm hole at 251 bar | 2.87 kg/s | 3.40 (real gas, pure CH4) | -15.6 | explained: ideal-gas orifice formula (already an open data need on sheet 4) |
| 100 mm hole, holder | 0.171 kg/s | 0.1713 | -0.2 | agrees |
| D-201 heating | 112.1 kW | 108.1 | +3.7 | agrees |
| K-301 blower | 2.16 kW | 2.16 | 0.0 | agrees |
| Hydrolysis water (C-H-O) | 199.4 kg/h | 198.3 | +0.6 | agrees (implied VS: C 50, H 7.1, O 42.9 mass %, plausible) |

Own estimate, not in generator: off-gas combustion heat 79 kW gives an adiabatic rise of about 314 K from 40 C (to about 350 C), so a thermal oxidiser needs support fuel (the ignition temperature for a thermal oxidiser is general knowledge, not sourced here).

Not recomputable here: membrane stage count and permeate recycle (no membrane model in the libraries); PSA/membrane power.

## Check 2: real-world references

| Metric | Ours | Reference | Source | Grade | Dev % | Verdict |
|---|---|---|---|---|---|---|
| Press-mud feed per t CBG | 16.0 t/t (S, mixed feed) | 25 t/t | CSE India CBG National Blueprint, webinar slides 24 Jul 2026, 5-TPD model slide | A | -36 | explained (mix; unconfirmed) |
| Raw biogas per t feed | 144.6 Nm3/t | 92.6 (derived from 25 t/t with our composition) | same | A | +56 | explained (mix; unconfirmed) |
| Press mud per Nm3 biogas | 6.91 kg | 2.27 kg | Bawase et al., Int. J. Des. Nat. Ecodyn. 21(6) 2026, doi 10.18280/ijdne.210612, p1654 | A | -67 | unexplained; reference implies 441 Nm3/t, an outlier against CSE |
| Methane slip | 1.5 % | membrane 0.5-1.0, PSA <2 | IEA Bioenergy Task 37 methane-slip slides, Jan 2023, slide 15 | A | +50 | explained (A4 conservative for membrane) |
| CH4 in raw per CH4 product | 1.015 | 1.006 | Bawase et al. p1655-1656 | A | +0.9 | agrees |
| Upgrader power | 0.240 kWh/Nm3 CBG | 0.575 (membrane) | Bawase et al. p1656 | A | -58 | unexplained |
| Upgrader power per raw | 0.136 kWh/Nm3 | 0.21-0.30 | search summary of a review, not fetched | C | n/a | unexplained |
| FOM per feed | 34 % | 45-55 % | CSE case study 4 (Sampurn, straw + dung) | A | -24 | explained (different feed) |
| FOM cake solids | 40.5 % | 28.7 % industrial average | Front. Sustain. Food Syst. 2024, doi 10.3389/fsufs.2024.1415508 | A | +41 | unexplained |

Fetched but unusable: Praj BioCNG brochure (June 2022; no ratios in the text). Global Methane CBG report URL returned 404. Vendor figures (membrane 0.15-0.20 kWh/Nm3, screw-press up to 40 % solids) were snippets from search results and are not used as references.

## Check 3: structural lint (stdlib script over the generated HTML)

| Test | Result before fix | After fix |
|---|---|---|
| Stream diamonds vs HMB columns (17) | 16 diamonds; stream 10 had a column but no diamond | 17 / 17 |
| Equipment-list tags on drawing (18 rows) | 18 / 18 present | same |
| Duplicate tags | 0 (P-101 and R-301 repeat only as references in ESD / analyser text) | 0 |
| ESD valves named in scenarios on sheet 1 | XV-201 and XV-101A/B tagged; XV-501 and XV-601 drawn as red valves but untagged | all four tagged |
| PSV discharge destination | PSV-501 arrow had no destination | labelled "vent (A)" |
| Text clipping | none outside the 1600 x 1130 frame | one label shortened to stay inside the panel |
| Relief on pressure equipment | not fixed (design change): D-201A/B via holder PRVs and V-501 via PSV-501 are covered; R-301, E-301, M-401 (16 barg), K-201 discharge and CAS-601 (250 barg, TPRD only in text) show no PSV or stated reason | unchanged |

## Generator fix made (arithmetic, not an A value)

`comp()` in `scripts/gen_pid_cbg.py` used the stage-1 inlet temperature (5 C) for every stage, although the intercooler returns gas to 40 C. K-201 shaft work rose 121.0 to 128.6 kW and cooling 90.7 to 113.4 kW; K-201 outlet temperature 145 to 197 C (stage-2 discharge). K-202 unchanged (inlet already 40 C). Also added diamond 10, tags XV-501/XV-601 and the PSV-501 vent label. Mass closure assert still passes (0.0000 %); `docs/pid/CBG_PID_Set_RevA.html` and `.pdf` regenerated. Not run: the project test suite.

## What to change (ranked)

1. Feed per product: ours needs 16 t feed per t CBG against 25 t/t (CSE, press mud). The yield of 145 Nm3 biogas per t feed is 56 % above the CSE-implied 93. Obtain feedstock mix, TS/VS and BMP from the owner, or lower the yield (the 160 TPD and 18,000 t/yr FOM are S values from the DPR template).
2. FOM cake: 40 % solids and 85 % capture (A11) are above measured industrial separation (28.7 % solids). Test 25-30 % solids, which changes FOM mass split, centrate recycle and slurry water.
3. Upgrader power: single-pass membrane with no recycle gives 0.24 kWh/Nm3 CBG against 0.575 in the one fetched reference; add a recycle ratio or a power input per licensor, and quote electrical not shaft power.
4. Methane slip 1.5 % is high for a membrane (0.5-1 %); keep it only if PSA is the base case. Off-gas stays 1.9 mol % CH4, so the oxidiser needs support fuel (sheet 2 note).
5. Add PSVs or stated reasons for M-401/K-201 discharge (16 barg), R-301, E-301 and CAS-601.
6. Use real-gas rates at 250 barg (about 16 % higher) and real-gas cooling duty for K-202 (about 22 % higher).

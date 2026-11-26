# ETHANOL (grain 1G distillery, 100 KLPD) P&ID set: validation

Generator `scripts/gen_pid_ethanol.py`, set `docs/pid/ETHANOL_PID_Set_RevA.html/.pdf`. Comparison rows: `ETHANOL_comparisons.csv`. Recompute script: `<scratch>/val_ethanol/recompute.py`; lint script: `<scratch>/val_ethanol/lint.py`.

## Verdicts

| Check | Verdict |
|---|---|
| 1 Independent recompute | 10 quantities recomputed (CoolProp 8.0, thermo 0.6.1 NRTL, chemicals). 8 agree within tolerance, 1 arithmetic error found and fixed (EV-101 duty +7.5 %), 1 design flag (rectifier R only 1.11 x Rmin). |
| 2 Real-world references | 13 comparisons from 4 fetched documents, all grade A. Mass ratios (grain, CO2, yield) agree. DDGS is high (+30 to +49 %). Steam agrees with Indian EC documents but is about 2x US dry-mill energy. |
| 3 Structural lint | Streams, tags, frame: clean. 8 failures: scenarios name devices absent from sheet 1, two vessels have no relief device or stated reason. |

## Check 1: recomputation (tolerance 2 % stoichiometry, 10 % duties)

| Quantity | Ours | Independent | Dev. | Verdict |
|---|---|---|---|---|
| Grain, t/yr | 81,888 | 81,914 | 0.0 % | agrees |
| CO2, kg/h | 3,131.9 | 3,132.9 | 0.0 % | agrees |
| E-102 beer reboiler, kW | 3,514 | 3,453 (CoolProp H, vapour 95 C) | +1.8 % | agrees |
| E-103 condenser, kW (RR 3) | 3,119 | 3,162 (latent heat at NRTL bubble T 78.2 C) | -1.4 % | agrees |
| E-106 reboiler, kW | 1,076 | 1,119 | -3.9 % | agrees |
| EV-101 steam duty, kW | 3,641 (before fix) | 3,388 (14,520 kg/h / 2.5 x 2,100 kJ/kg) | +7.5 % | ERROR, fixed |
| D-101 latent part, kW | 4,065 | 4,064 | 0.0 % | agrees (the 0.65 efficiency is A, untestable) |
| 94 wt% overhead vs azeotrope | 94 wt% | 94.75 wt% at 78.18 C (NRTL) | | feasible, just below azeotrope |
| S9 dew T | 95 C | 92.0 C | +3 K | explained (A superheat) |
| Rectifier R | 3.0 | Rmin 2.41 (q-line), 2.71 (tangent pinch); 66 ideal stages at R 3.0, 39 at 3.5, 31 at 4.0 | R/Rmin 1.11 | flag |

Not recomputable here: fermentation heat (85 kJ/mol, A; `chemicals` has only gas-phase Hf for glucose), H-101 duty (dry-solids cp not in the libraries; bounds 977 to 1,200 kW bracket the 1,149 kW used), dryer efficiency, evaporator economy.

Generator fix: `EV-101` used `lam_w` (2,257) where the steam latent heat `lam_st` (2,100) applies, so the stated economy of 2.5 was really 2.33. Now `ev_w / econ * lam_st`. Effect: EV-101 3,641 to 3,388 kW, total LP steam 26.8 to 26.4 t/h, 6.43 to 6.33 kg/L. Regenerated HTML and PDF; closure asserts pass (mass 0.00 %, carbon 0.00 %). No A value changed.

## Check 2: real-world references (all fetched and read, grade A)

Sources: IGL = India Glycols PFR/EMP, 200 KLD grain distillery, Kashipur (environmentclearance.nic.in, Apr 2022, tables 06, 09, sec 3.7.2). PR = Pernod Ricard Nashik draft EIA executive summary, 60 to 250 KLPD (MPCB, 2024-05). VV = Veer Vallabh Green draft EIA executive summary, 207 KLPD (MPCB, 2025-12). ANL = M. Wu, Analysis of the Efficiency of the U.S. Ethanol Industry 2007 (Argonne for RFA, 2008, tables 3, 4, 6). Full URLs are in the CSV.

| Metric | Ours | Reference | Dev. | Verdict |
|---|---|---|---|---|
| Grain, maize, kg/L | 2.48 (D) | 2.465 IGL; 2.553 PR | +0.7 %; -2.8 % | agrees |
| Yield, L/t grain | 403 | 419 ANL (2.81 gal/bu, denatured) | -3.8 % | agrees |
| CO2, t/KL | 0.752 | 0.763 VV; 0.740 PR | -1.5 %; +1.6 % | agrees |
| DDGS, t/KL at 10 % moisture | 0.907 | 0.609 VV; 0.700 PR (total) | +49 %; +30 % | VV unexplained residual; PR explained |
| DDGS dry, kg/L | 0.816 | 0.707 ANL (range 0.56 to 0.97) | +15 % | explained, inside range |
| LP steam, kg/L | 6.33 | 6.60 IGL (55 TPH / 200 KLD); 5.04 PR (52.5 TPH / 250 KLPD) | -4.1 %; +26 % | agrees with IGL; PR scope unclear |
| Boiler capacity, kg/L | 6.33 | 5.22 VV (45 TPH incl. 6 MW cogeneration; capacity not use) | +21 % | explained |
| Thermal energy, MJ/L | 13.3 steam | 7.7 fuel (ANL, 27,589 Btu/gal NG) | +73 % | explained: US plants sell 37 % DDGS wet, no ENA columns |
| Slurry water, L/L | 5.79 | 6.49 IGL (1,297 KLD / 200) | -10.7 % | explained (A slurry 30 % vs about 27.5 % implied) |

The open items:
- Grain 81,888 vs template 86,800 t/yr: the template implies 2.63 kg/L; the fetched Indian maize figures are 2.47 to 2.55, i.e. 81 to 84 kt/yr for 33,000 KL. Our figure sits inside that band. The template is the high one (about 380 L/t). Likely cause on our side is none; do not tune.
- DDGS 29,924 vs template 26,000 t/yr: the references (0.61 to 0.79 t/KL, i.e. 20 to 26 kt/yr) support the template, not ours. Likely cause: A "Y = 0.90" leaves 712 kg/h of glucose (19 % of DDGS) unfermented in the DDGS. Without it DDGS is about 0.717 t/KL (23.7 kt/yr). Real unfermented sugar is a few percent; the rest of the 10 % goes to yeast, glycerol, CO2 side paths, which do not all end up in DDGS.
- Steam 6.4 kg/L: not an error against Indian RS/ENA documents (5.0 to 6.6 kg/L, which include turbine steam and extra columns); it is about 2x the US dry-mill mean. Largest shares: dryer 41 %, beer reboiler 23 %, evaporator 22 %. No multi-effect or vapour-recompression integration is modelled (A).

## Check 3: structural lint (sheet text parsed with stdlib)

- Stream diamonds on sheet 1: 20; HMB columns on sheet 2: 20; no unmatched, no duplicate diamonds.
- Equipment-list tags: 35 (T-201A/B counted once); all appear on the drawing; no tag on the drawing is missing from the list; no duplicate labels.
- Frame: no text outside the 1600 x 1130 frame (estimated widths; not a pixel render).
- FAILURES (8):
  1. XV-201, XV-301, XV-501 are named as ESD/trip valves in sheets 3 and 4 but are not on sheet 1.
  2. GD-201, TAHH-501, LAHH-401 are named in scenarios but are not on sheet 1.
  3. T-101 day tank: no PVRV or stated reason (only T-201A/B carries PVRV-401).
  4. MS-101A/B sieve beds: no relief device or stated reason.
- Relief destinations: PSV-301, PSV-302 say "to vent (A)", PVRV-201 goes to the scrubber vent, PVRV-401 is to atmosphere with a flame arrestor. All four have a stated destination, but "to vent" is generic and flagged as an open item on the sheet.
- Caveat: I did not render the pages; devices may be drawn on the scenario overlays only.

## What to change (ranked)

1. DDGS: revisit A "Y = 0.90" and route only the realistic residual sugar (1 to 3 %) to DDGS. This brings DDGS to about 0.72 t/KL and removes the 30 to 49 % gap. Needs the owner's decision (it is an A).
2. Add XV-201, XV-301, XV-501, GD-201, TAHH-501, LAHH-401 to sheet 1, or reword the scenarios so they refer only to devices on sheet 1.
3. Give T-101 and MS-101A/B a relief device or a one-line reason.
4. Raise rectifier R to at least 3.5 (R/Rmin 1.3) or state the tray count; R 3.0 needs 66 ideal stages. Cost: about 520 kW more condenser and reboiler duty per +0.5 R.
5. Replace the generic "to vent (A)" with a named destination, or leave as open.
6. Steam: keep; note on sheet 2 that it includes no heat integration and is about 2x US dry-mill thermal energy but within Indian EIA figures (a benchmark box was not added).

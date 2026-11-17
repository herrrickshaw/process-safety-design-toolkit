# FRUITVEG validation: 10,000 t/yr fruit and vegetable pulp + IQF plant

Set under test: `scripts/gen_pid_fruitveg.py`, `docs/pid/FRUITVEG_PID_Set_RevA.html/.pdf` (validated 2026-11-11). Detail rows: `FRUITVEG_comparisons.csv`.

## Verdict per check

| Check | Verdict |
|---|---|
| 1 Independent recomputation | PASS. 14 quantities recomputed with CoolProp / thermo / chemicals, 14 agree (largest gap 9.1 %, an assumed effluent temperature). 1 quantity (ice cp) cannot be recomputed with these libraries. |
| 2 Real-world references | PARTIAL. 13 comparisons, 12 grade A (documents read), 1 grade C (search snippet). 5 agree, 5 explained, 1 not comparable, 2 unexplained (IQF cooler water, effluent COD load). |
| 3 Structural lint | 1 tag mismatch (fixed), 3 other findings (below). Stream diamonds vs HMB columns 34/34. No clipped text. |

The mass and heat balance is arithmetically sound; its weak points are the assumed inputs, not the arithmetic. Agreement of the yield chain with an independent re-run (row "yields") only proves arithmetic: the A inputs were not tested by it.

## Check 1: independent recomputation

Tool: `/private/tmp/claude-501/venv_val/bin/python` (CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2). Script: `/private/tmp/claude-501/val_fruitveg/recompute.py`.

| Quantity | Ours | Independent | Dev % | Note |
|---|---|---|---|---|
| Tsat, 4 bar(a) | 144.0 C | 143.61 C | +0.3 | |
| hfg, 4 bar(a) | 2133 kJ/kg | 2133.4 | 0.0 | |
| Steam enthalpy into 90 C bath | 2358.7 | 2360.9 | -0.1 | |
| B-201 duty / steam | 201.8 kW / 308 kg/h | 206.7 kW / 315.1 kg/h | -2.3 | fruit cp 3.73 (water + sugar solids) vs A 3.6 |
| E-301 hot-fill / aseptic | 18.46 / 25.97 kW | 19.14 / 26.93 | -3.5 / -3.6 | same cp |
| Deaerator outlet T | 70.42 C | 70.53 | -0.15 | hfg at 0.2 bar is 2357.5 vs A 2300 (-2.4 %), effect on T small |
| E-402 duty | 34.58 kW | 35.85 | -3.5 | |
| IQF freezing load | 40.10 kW | 40.65 | -1.4 | latent 333.6 kJ/kg; ice cp not independent |
| COD factor | 1.10 kg/kg | sucrose 1.122, glucose 1.066, cellulose 1.184, citric acid 0.749 | -2.0 | A13 sits in the sugar-to-fibre range; acid-rich fruit is lower |
| Boiler heat to steam | 298.5 kW | 298.7 | -0.1 | |
| Yield chain (pulp / by-product / IQF) | 6008 / 1518 / 1829 t/yr | same | 0.0 | arithmetic only |
| Effluent mix temperature | 40 C (A) | 36.7 C | +9.1 | enthalpy-weighted over streams 5,10,14,25,28,30,33 |
| Aseptic hold pressure | 3 bar | Psat(105 C) = 1.21 bar | n/a | 3 bar is adequate (no flashing) |

Not recomputable: ice cp (A11 = 1.9 kJ/kg/K). thermo returns 1.22 to 1.29, which is inconsistent with a solid-water value and is not trusted. Its effect is about 10 % of the 314 kJ/kg freezing load.

## Check 2: real-world references

Documents read (grade A): [BREF] EU JRC Food, Drink and Milk Industries BAT Reference Document, Dec 2019, `eippcb.jrc.ec.europa.eu/sites/default/files/2020-01/JRC118627_FDM_Bref_2019_published.pdf`; [IFC] IFC / World Bank Group EHS Guidelines, Food and Beverage Processing, 30 Apr 2007, `ifc.org/content/dam/ifc/doc/2000/2007-food-and-beverage-processing-ehs-guidelines-en.pdf`; [MSAMB] Maharashtra State Agricultural Marketing Board, Model DPR Secondary Processing Project for Oranges, Oct 2024; [NABARD] Model Project Report, Fruit Vegetable Processing Unit (NABARD-linked, hosted at pashudhanpraharee.com). Grade C: AgriEngineering 2021 mango pulp extractor study (search snippet only).

| Metric | Ours | Reference | Source | Grade | Dev % | Verdict |
|---|---|---|---|---|---|---|
| Fresh water per t product | 5.11 m3/t (D) | fruit cans 2.5-4.0, frozen F&V 5.0-8.5; mix-weighted 3.1-5.0 | BREF Table 8.10 | A | +1.4 vs top | agrees, top of range |
| Fresh water per t raw | 4.0 m3/t | frozen F&V 5, washing 3, cans 1-16 | BREF Table 8.10 | A | in range | agrees |
| IQF blancher steam | 0.160 t/t frozen | 0.09 (belt + water cooler, 7 bar) | BREF Table 8.6 | A | +77 | explained: direct-steam bath, 15 % loss (A9), no heat recovery |
| IQF blancher steam | 0.160 t/t frozen | 0.16 (belt + air cooling) | BREF Table 8.7 | A | 0 | agrees |
| IQF cooler water | 0.3 kg/kg (A12) | 2-4 L/kg drum cooler | BREF 8.2.2.4 | A | -90 | UNEXPLAINED; A12 is the cause |
| IQF refrigeration electricity | 62-70 kWhe/t (implied: NH3, -35/-40 C, eta 0.7, COP 1.56-1.76) | 80-280 kWhe/t frozen veg | BREF sec 8.1 | A | -12 | explained: compressor only, no fans or auxiliaries |
| Solid by-product | 194 kg/t product | strawberries 60, apples 90, peaches 180, carrots 200 kg/t | IFC Table 2 | A | +7.6 vs peaches | agrees (crop-dependent) |
| COD load | 3.03 kg COD/t product | 36.5 kg COD/t (half pears, abrasion + knife peeling) | BREF Table 8.3 | A | -92 | UNEXPLAINED: model counts leach only, no peeling water |
| Untreated effluent COD | 568 mg/L | about 4,000-5,000 mg/L peeling wastewater | BREF sec 8.2.1 | A | -86 | explained: ours is a diluted total, no peeling stream |
| Discharge limit | 568 mg/L raw | 250 mg/L COD | IFC Table 1 | A | n/a | ETP needs at least 56 % removal |
| Pulp-line yield | 83.9 % of fruit to line | 77.9 % max, mango extractor | AgriEngineering 2021 via DOAJ snippet | C | +7.7 | explained: crop unspecified |
| Juice/pulp recovery | 83.9 % | 40 % of oranges | MSAMB DPR | A | n/a | not like-for-like (citrus) |
| Process water, micro unit | 4-5 m3/t | about 1 m3/t (1,000 L/day, 300 t/yr) | NABARD model | A | n/a | not comparable, no basis given |

No reference found for: pasteuriser steam per t pulp, hot-fill versus aseptic split, cold-store load, boiler fuel per t. Plant electricity in total (not in the HMB) is not compared.

## Check 3: structural lint (Python stdlib, Chrome for text extents)

Script: `/private/tmp/claude-501/val_fruitveg/lint.py`.

| Test | Result |
|---|---|
| Sheet 1 stream diamonds vs HMB columns | 34 numbered diamonds, 34 HMB columns, 0 missing either way, 0 duplicates (35th diamond is the legend "n") |
| Equipment-list tags on the drawing | 36 tags, 1 failure: BT-301 appeared only on sheet 4 (FIXED: list now says "sheet 4 only") |
| Duplicate tags | 0 duplicate equipment boxes (repeats are cross-references in notes; counted by text only) |
| Drawing equipment missing from the list | P-601, CIP-901, BH-501 (3, minor) |
| Pressure items with relief or stated reason | PSV-501 (boiler), PSV-502 (header), PSV-701 (receiver) present. No relief and no stated reason: E-301 (3 bar product, 4 bar steam), F-401 / CS-401 evaporators, DA-201 / VC-201 vacuum set (no vacuum breaker), E-701 / C-701 only by implication. Count: 4 |
| PSV discharge | 3 of 3 end in a vent cap and the notes say "safe outdoor location" |
| ESD valves named in scenarios on sheet 1 | XV-501, XV-502, SV-701, FDV-301: 4 of 4. Not on sheet 1 or in the list: EF-701 fan, ESD-701, BMS-501 logic, TCV-301 (steam valve of E-301, sheet 4 only) |
| Clipped text | 0 text boxes outside the sheet frame (Chrome bounding boxes, all 4 sheets) |

## What to change, ranked

1. Effluent COD is too low by an order of magnitude against BREF Table 8.3. Add a peel/cut-water stream and make A4/A13 larger, or relabel sheet 2 and scenario 4 "leach-only COD, lower bound" prominently (the notes already say lower bound, the table does not). Do not size the ETP from 568 mg/L.
2. IQF cooler water (A12, 0.3 kg/kg) is 7-13 times below BREF 2-4 L/kg. State whether it is purge or fresh water; the freshwater total and ETP flow move by about 0.5-1.5 m3/h.
3. Refrigerant electricity is not given, only thermal load; add the implied 60-70 kWhe/t with the refrigerant choice, and note BREF 80-280 includes fans.
4. Relief philosophy: add a reason or a device for E-301, evaporators F-401/CS-401 and DA-201 vacuum set, or a note that the common refrigerant PSV protects the system.
5. Put EF-701, ESD-701, BMS-501, TCV-301, P-601, CIP-901, BH-501 in the equipment list.
6. Crop is unspecified, so by-product (14 % / 22 %) and yield are only crop-agnostic; a mango case (25-40 % by-product reported in snippets, grade C) would give a pulp yield of 60-75 %, not 84 %.
7. Property inputs (A11): fruit cp 3.6 is about 3.5 % below the composition value; hfg_vac 2300 is 2.4 % below the 0.2 bar value. Low priority.

## Generator fix made

`scripts/gen_pid_fruitveg.py`: equipment-list entry "BT-301 balance tank (A)" now reads "BT-301 balance tank (A; sheet 4 only)" because the tank is not drawn on sheet 1. Regenerated `docs/pid/FRUITVEG_PID_Set_RevA.html` and `.pdf`; closure asserts pass (in 12,897.7 kg/h, out 12,897.7 kg/h, error 0.000 %). No A value was changed.

## Still unvalidated

IQF share (23 % of product, 25 % of fruit) and the 75:25 split have no source (tuned to the template). Refrigerant, boiler fuel, plant electricity, hot-fill/aseptic split, hold-tube time and sterility limits. Ice cp. Peak effluent loads.

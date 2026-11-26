# Gap closure for the four bio-based P&ID sets (ethanol, CBG, biodiesel, fruit and veg)

Date 2026-11-11. Baselines: `ETHANOL_VALIDATION.md`, `CBG_VALIDATION.md`, `BIODIESEL_VALIDATION.md`, `FRUITVEG_VALIDATION.md`. One row per gap with source, grade and proposed value: `GAP_CLOSURE_BIO.csv` (22 rows). No generator was edited. Proposed values are for the owner to adopt; A-values stay A until then.

Grades: A = document text fetched and read (page or table cited). C = search snippet or a vendor claim quoted inside a read document. D = derived here from read values plus the generator (arithmetic shown). Source files are in `<scratch>/{val_*,gap_bio}/`.

## Tally

| Status | n | Gaps |
|---|---|---|
| Closed with a sourced value | 11 | CBG feed per t, CBG yield, FOM cake, methane slip, oxidiser fuel; biodiesel methanol recovery, FFA limit, wash water; fruit-veg COD, IQF/blancher cooler water, blancher steam |
| Partly closed | 8 | ethanol DDGS, steam, evaporator economy; CBG upgrader power; biodiesel crude glycerol, utilities; fruit-veg pulp yield, refrigeration/cold store |
| Not closable | 3 | ethanol rectifier stages, fermentation heat, dryer efficiency |

## Ethanol

**DDGS (partly closed).** Ours 0.907 t/KL (dry 0.816 kg/L). ANL (Wu 2008, Table 3) gives 5.9 dry lb/gal, range 4.7 to 8.1, i.e. 0.707 kg/L (0.56 to 0.97), 0.786 t/KL at 10 % moisture. The generator's dry DDGS is two parts: non-fermentable solids 0.645 kg/L (A7 starch 0.62, A8 moisture 0.12; D) and residual glucose 0.171 kg/L (712 kg/h over 4,167 L/h; D). ANL leaves room for only about 0.062 kg/L of residue, 36 % of ours. Raising `Y` (line 40) from 0.90 to 0.93 to 0.95 scales ethanol to 419 to 425 L/t (ANL 419 denatured) and DDGS to 0.84 to 0.81 t/KL (D, linear scaling, recompute in the generator). Side effect: CO2 rises to 0.78 to 0.79 t/KL against 0.74 to 0.763 in the references. The remaining gap to 0.71 to 0.79 needs real corn composition, which was not fetched. Dale and Tyner (Purdue SP 06-04, 2006) state commercial conversion at "75 to 85 % of theoretical", which conflicts with ANL's measured yield; not used. Confidence medium-low.

**Steam (partly closed).** Ours 6.33 kg/L. ANL Table 6: 14.47 lb/gal mean (1.73 kg/L), range 0.60 to 29.60 lb/gal, SD 7.63, so the mean is weak. Dale and Tyner: 36,000 Btu thermal per gallon in 1998 (10.0 MJ/L, about 4.8 kg/L at 2,100 kJ/kg, D); shares distillation 32 %, DDGS drying 27.5 %, thin-stillage evaporation 26.4 %. Ours: dryer 41 %, beer reboiler 23 %, evaporator 22 %. The dryer is the outlier, and 36.7 % of US DDGS is sold wet (ANL Table 3). Proposal: keep 6.3 as the Indian zero-liquid-discharge base (IGL 6.6) and add a note with the US range 1.7 to 4.8 kg/L. No A change.

**Evaporator economy (partly closed).** Dale and Tyner's model default is 3 evaporation passes. Moving A economy from 2.5 to 3.0 cuts EV-101 from 3,388 to 2,821 kW, about 0.97 t/h or 0.23 kg/L (3.7 %). A default is not a plant measurement; low confidence.

**Not closable.** Rectifier stage count and reflux (the one candidate paper, Kansas State salt-extractive distillation, returned an HTML page, not read); fermentation heat 85 kJ/mol; dryer efficiency 0.65 (Dale and Tyner use an efficiency parameter but no value was read). Keep the validation advice: R at least 3.5 or state tray count (own calculation).

## CBG

**Feed per t CBG and yield (closed).** CSE blueprint slide 24: 25 t per t CBG for both press mud and MSW. Bawase et al. (Int J Des Nat Ecodyn 21(6), 2026, p1654): about 25 t press mud per t CBG; Napier grass biogas about 150 m3/t, equal to 60 kg CBG, i.e. 16.7 t/t. Our 16.0 t/t and 144.6 Nm3/t are therefore a Napier-class feed, not press mud. Press mud derived: 40 kg CBG/t, at 63.3 % CH4 raw gas and 1.536 raw per Nm3 biomethane (Bawase), gives 86 to 93 Nm3/t (D). Proposal: make the feed mix an input; press mud 25 t/t, Napier 16.7 t/t, mix by mass. Medium confidence (CSE and Bawase may quote one rule of thumb).

**Upgrader power (partly closed).** Bawase p1656: membrane 0.575 kWh/m3 biomethane, "more than three times" PSA (so PSA below 0.19, D), amine wash 0.116 kWh/m3 plus 3.852 MJ heat. Proposal: 0.24 stands only for PSA-class; membrane 0.3 to 0.575, report electrical per Nm3 biomethane. The second source (SGC "Biogas upgrading, review of commercial technologies") returned HTTP 403; stopped. The 0.575 is one LCI inventory, not a plant meter.

**FOM cake (closed).** Romio, Ward and Moller (Front Sustain Food Syst 2024), Tables 2 and 3: industrial separation gives solid fraction at 286.97 g/kg TS (28.7 %), only 7.24 % of digestate mass and 26.84 % of TS; lab scale gives 128 g/kg and 51.8 % of TS. Our 40.5 % and 85 % capture are well outside. Proposal: A11 cake 28.7 % (25 to 30), capture 0.27 (0.2 to 0.5); recompute FOM split, centrate recycle and slurry water. Caveat: European manure plants.

**Methane slip (closed).** IEA Bioenergy Task 37 slides (Liebetrau, 25 Oct 2023), slides 15 to 17: membrane 0.5 to 1 %, PSA below 2 % (1.8 to 2), water scrubber 1.1 to 2, amine 0.04 to 0.07. Bawase: membrane 0.64 %, multi-stage PSA 1.25 %. A4 1.5 % is right for PSA, high for membrane.

**Off-gas and oxidiser (closed).** Same slides, slides 10 and 18: regenerative thermal oxidation runs from 0.37 vol % CH4 (autothermic at 0.37 %); recuperative oxidation needs 6 % (3 % with fuel-gas recuperation); flare 25 % (12 % with air control); RTO has a manufacturer limit below 10 kW. Our off-gas is 1.9 mol % CH4 and about 79 kW, so an RTO needs no support fuel; the sheet 2 note should be conditional on oxidiser type.

## Biodiesel

**Methanol recovery (closed, direction high confidence).** Alam (MASc thesis, Univ. Regina 2014) simulated single flash: 90 % recovery at 0.2 atm costs 1.45 MJ/kg methanol; at 1.0 atm product purity degrades beyond about 91 % recovery (3.3 MJ/kg); distillation 3.71 and stripping 1.80 MJ/kg at 0.2 atm and 90 %. Vendor claims quoted in its Table 1.4 (grade C): vacuum flash above 99 % in 1 to 3 stages, distillation above 99.9 %. Sheehan (NREL/SR-580-24089, 5.5.1.5) recovers methanol by distillation of the wash and glycerol streams (bottoms below 0.5 % methanol, molar reflux 3.66). Our own UNIFAC-Dortmund recompute (`<scratch>/gap_bio/bd/flash.py`) reproduces the 14.5 % at 80 C and 1 bar and gives the ester-phase single-stage recovery by pressure:

| P, bar(a) at 80 C | 1.0 | 0.5 | 0.2 | 0.1 | 0.05 | 0.02 |
|---|---|---|---|---|---|---|
| Recovery, % | 14.5 | 69.9 | 89.6 | 95.0 | 97.6 | 99.0 |

At 120 C: 77.6 % at 1 bar, 96 % at 0.2 bar. The 89.6 % at 0.2 bar agrees with Alam's 90 %, two independent models. Proposal: A11 99.5 % to 95 % base (90 to 99 %), streams 13/14 to 0.1 bar(a), add a vacuum package, or add stripping or a second stage for 99 %. The residual methanol goes to the wash or glycerol side.

**FFA limit (closed, one source).** Van Gerpen et al. (NREL/SR-510-36240): fats above about 1 % FFA must be pretreated before base catalysis, or soap and water form. A1 2 % should become 1 % or less, or add acid esterification (which the same text says needs 20:1 or more alcohol).

**Wash water (closed).** Sheehan p148: continuous countercurrent 20 % of ester mass, batch 30 to 40 % (10 % of the wash entrained, then vacuum dried). Our 5 % is below both. Proposal 20 % (20 to 40 %); if a no-wash scheme is kept, state how soap and Na meet spec (IS 15607 not read).

**Crude glycerol (partly closed).** Sheehan Tables 13 and 14: 0.15 kg per kg biodiesel (13 % of products), against our 137 kg/t: fine. Table 102 lists 212.8 kg/t at "80 wt %", which would exceed stoichiometric glycerol (about 103.5 kg/t), so that table's label looks inconsistent; not used.

**Utilities (partly closed).** Sheehan: steam 327,980 kcal/t (1.37 GJ/t, Table 96) against Ballestra 96,023, Florys 166,290, IFP 237,557 and the Kansas City plant 617,922 kcal/t (0.40 to 2.59 GJ/t); electricity 28.9 kWh/t (Tables 95, 101) but 0.23 MJ/kg (63.9 kWh/t) in Table 13, Ballestra 30, Florys 40, IFP 9. Different scheme from ours (wash plus distillation); use as a benchmark band only.

## Fruit and vegetables

**Effluent COD (closed on order of magnitude).** EU JRC FDM BREF (Dec 2019): Table 8.3, abrasion plus knife peeling, half pears in syrup, 36.5 kg COD/t (BOD 21.6, SS 21.5); Table 8.4, caustic peeling 66.3 kg COD/t; peeling wastewater COD about 4,000 mg/L (steam) and 5,000 mg/L (mechanical); in fruit processing, peeling can be 10 % of the flow and 60 % of the BOD. Ours 3.03 kg/t is leach-only. Proposal: for peeled fruit use 36.5 to 66.3 kg/t; for a no-peel case keep 3 to 15 (the 15 applies the BOD peeling share to COD, D, weak) and add a peel and cut-water stream. BREF Tables 8.11 and 8.12 (33 to 61 mg/L) are treated discharge, not raw load.

**Cooler water (closed).** The BREF 2 to 4 L/kg is the countercurrent drum cooler after the blancher (8.2.2.4), not the IQF freezer; belt coolers reuse water into preheat (no litres/kg given). Ours 0.3 kg/kg: use 2 to 4 kg/kg for a drum cooler (+3.1 to +6.8 thousand m3/yr on 1,829 t/yr IQF, D), or document a belt cooler with full recirculation.

**Blancher steam (closed).** BREF Tables 8.5 to 8.8: 0.09 t/t frozen (belt, water cooling, 7 bar), 0.16 (belt with air cooling, drum, and caustic peel prior to freezing). Ours 0.160 stays valid for a bath without heat recovery; 0.09 needs cooling-water-to-preheat recovery.

**Pulp yield (partly closed).** BREF: knife peeling loss 16 to 17 %, caustic about 17 %; IFC Table 2 by-product 60 (strawberry) to 200 (carrot) kg/t. Our 83.9 % to the line agrees with 83 % for a peeled fruit; crop is unspecified, so make yield a crop input. Mango 77.9 % is grade C. No pulp-recovery document for Indian mango or guava was fetched.

**Refrigeration (partly closed).** BREF sec. 8.1: deep freezing 80 to 280 kWhe/t frozen vegetables (includes fans); ours implied 62 to 70 is compressor only. Cold-store load: none of the BREF, IFC, MSAMB, NABARD or EBRD texts gives a figure; not closable here.

## Highest-impact corrections

1. Biodiesel V-401/V-402: 99.5 % flash at 1 bar is infeasible (14.5 %); operate at 0.1 bar(a) for about 95 %, or add stripping.
2. CBG FOM separation: cake 28.7 % and TS capture about 27 %, not 40.5 % and 85 %; and make feed mix an input (our 16 t/t is Napier-class, press mud is 25 t/t).
3. Fruit and veg effluent: COD 36.5 to 66.3 kg/t for peeled fruit, 10 to 20 times the present 3.0; and cooler water 2 to 4 kg/kg.

## Unresolved

Ethanol DDGS residual after raising `Y` (needs corn composition); rectifier stages; upgrader power beyond one LCI source; cold-store load; Indian pulp yields; SGC review (HTTP 403) and Kansas State paper (blocked) were not retried. OpenAlex search was paused during the run; Europe PMC searches added nothing usable.

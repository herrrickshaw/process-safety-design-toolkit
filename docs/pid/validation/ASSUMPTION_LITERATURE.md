# Literature check of the assumed (A) values in the nine conceptual P&ID sets

Date: 2026-11-11. Method: documents fetched with curl or Europe PMC full text, extracted with pdftotext, values read from the text. Page numbers are PDF page numbers unless marked 'printed'. Recommendations only; no generator was changed.

Rows: 31. Grade A (text read) 20; grade C 1; rows with no source 10. Verdicts: edge 6, inside 8, no direct test 2, no source 11, outside 4.

Not reached (walls or wrong files, stopped at the host, nothing bypassed): sgc.se / Lund portal (Cloudflare), MDPI (access denied), ageconsearch (challenge page), polimi repository (challenge), Dobrota 2013 (hrcak returned a different paper), EU JRC BREFs and Fertilizers Europe booklet (404). LNG, urea and fruit and vegetable rows therefore have no literature test yet.

Assumptions were taken from the A lists on sheet 2 of each generator (scripts/gen_pid_*.py) and the A dictionaries in the code; ranking by effect on the headline result is my judgement, not a sensitivity run.

## Sources

- NREL: Sustainable Aviation Fuel State-of-Industry Report: Hydroprocessed Esters and Fatty Acids Pathway, NREL/TP-5100-87803 (rev. Sept 2026), doi:10.2172/2426563, https://www.osti.gov/servlets/purl/2426563
- VG: Van Gerpen, Shanks, Pruszko, Biodiesel Production Technology, NREL/SR-510-36244, 2004, https://www.osti.gov/servlets/purl/15008801
- LIN: Lin T., MS thesis, Engineering economic analysis of the quick-germ/quick-fiber modified dry grind ethanol fractionation process, Univ. Illinois 2010, https://www.ideals.illinois.edu/items/16936 (survey figures quoted second-hand: Shapouri and Gallagher 2005 USDA; RFA 2008; Tiffany and Eidman 2003)
- KS: Dry-grind processing using amylase corn and superior yeast to reduce the exogenous enzyme requirements in bioethanol production (authors per article text: D. Kumar, V. Singh), Biotechnology for Biofuels 2016, doi:10.1186/s13068-016-0648-1 (Europe PMC PMC5078892 full text)
- ROUF: Rouf, Bajpai, Jotshi, Optimization of biogas generation from press mud in batch reactor, Bangladesh J. Sci. Ind. Res. 45(4):371-376, 2010, doi:10.3329/bjsir.v45i4.7383
- T37: IEA Bioenergy Task 37, Reduction of methane emissions from biogas systems and landfills: methane oxidation treatment for low gas fluxes, 2025, https://task37.ieabioenergy.com/wp-content/uploads/sites/32/2025/03/IEA-Bioenergy-Task-37-Methane-oxidation-20250224.pdf
- PB: Purple Book PGS 3 (CPR 18E), Guidelines for quantitative risk assessment, https://content.publicatiereeksgevaarlijkestoffen.nl/documents/PGS3/PGS3-1999-v0.1-quantitative-risk-assessment.pdf
- YB: TNO Yellow Book CPR 14E, ch. 6, eq. 6.90-6.91, https://content.publicatiereeksgevaarlijkestoffen.nl/documents/PGS2/PGS2-1997-v0.1-physical-effects.pdf
- LBNL: Worrell and Galitsky, Energy Efficiency Improvement and Cost Saving Opportunities for Petroleum Refineries, LBNL-56183, 2005, https://www.osti.gov/servlets/purl/862119 (hydrogen figures quoted from Gary and Handwerk 1994)

## Ethanol

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| Dry-grind thermal duty (LP steam 6.33 kg/L x 2100 kJ/kg) | 13.3 MJ/L ethanol | USDA survey 7.2 to 15.1, mean 9.7; RFA 2008 survey 4.9 to 12.3, mean 8.7 | LIN pdf p.17-18 | A (thesis text read; survey values quoted second-hand) | edge (above both means, inside USDA range) | Keep as conservative; check heat integration (evaporator economy, DDGS dryer) before quoting utilities |
| Product per kg grain as received (starch 62 %, moisture 12 %, Y 0.90) | 0.403 (0.458 dry basis) L/kg | 0.41 L/kg corn (Tiffany and Eidman 2003, via thesis); lab 2.72 to 3.09 gal/bu dry = 0.405 to 0.460 L/kg dry | LIN pdf p.24; KS Table 2 | A | inside | Keep |
| Y: glucose fermented to ethanol + CO2 | 0.90 fraction | Lab SSF conversion efficiency 77.6 to 88.5 % of theoretical (conventional and amylase corn, yeast variants) | KS Table 2 | A | edge (above lab maximum 88.5 %; plant data not read) | Keep 0.90 only if licensor guarantees; sensitivity at 0.85 |
| Starch in grain 0.62; DDGS 0.365 kg per kg grain | 0.62; 0.365 wt fraction | - | - | - | no source found | Ask licensor / find USDA or university corn composition table |
| Beer-column, rectifier reflux 3.0, evaporator economy 2.5, dryer efficiency 0.65 | 3.0; 2.5; 0.65 - | - | - | - | no source found | Ask licensor; these drive the steam figure above |

## CBG

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| A2 raw biogas CH4, dry basis | 55 mol % | Press mud batch digestion 63.4 to 66.8 % CH4 (64.1 % for press mud alone) | ROUF Table IV (pdf p.4) | A | outside (ours is 9 points lower) | Change to about 60 to 65 for press mud; 55 stays valid only for mixed or napier feed (not read) |
| Biogas yield on press mud (not an input; sets digester size) | derived L biogas/g | 0.241 L/g press mud at 6 % solids, VS degradation 49.4 %; 0.24 to 0.38 with cane pith | ROUF p.3, Table IV | A (lab batch, 2-L reactor) | no direct A value to test | Use as bound when sizing digesters; ask for plant data |
| A4 methane slip of upgrader | 1.5 % of CH4 fed | Permit limits: Germany 0.2 % (grid subsidy), Austria 0.2, France 0.5 to 1, Denmark 1; RED II default 3 vol % of biomethane; amine scrubbing meets 0.2 | T37 pdf p.12 and p.24 | A | outside (above every national limit except the RED II default) | Keep OX-401 oxidiser on the off-gas; ask membrane vendor for guaranteed slip; design to 1 % or less |
| A3 H2S raw 2000 ppmv; A6 H2S removal 99 % | 0.002; 0.99 mol/mol; fraction | - | - | - | no source found | Find press-mud / napier H2S measurement; ask vendor |
| A8 feed total solids 0.30; A10 slurry 0.12; A11 press capture 0.85; A9 VS carbon 0.50 | as listed  | - | - | - | no source found | Find digestate dewatering and feed TS data |

## Biodiesel

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| A1 free fatty acid in oil | 2.0 wt % | Base-catalysed transesterification needs FFA below about 1 %; above that pre-esterify or remove FFA (soap forms) | VG pdf p.37 | A | outside | Add acid esterification step or specify UCO FFA below 1 %; ask licensor |
| A5 methanol:triglyceride mole ratio | 6:1 mol/mol | 4:1 to 20:1 reported, 6:1 most common; process uses 6:1 vs 3:1 stoichiometry | VG pdf p.35 and p.38 | A | inside | Keep |
| A4 triglyceride conversion in R-301 | 98 % | Ester yield must reach about 99.7 % to meet the total-glycerol standard; historic 98 % conversion (1940s patent) | VG pdf p.36 and p.60 | A | edge (below the 99.7 % product need) | Use 99 % or add polishing step; ask licensor |
| Catalyst NaOH loading (DPR 1 % of biodiesel, S) | 1.0 % of biodiesel | 0.3 to 1.5 % typical | VG pdf p.38 | A | inside | Keep |
| Reactor temperature (S from DPR) | 40 deg C | About 65 usual; 25 to 85 reported | VG pdf p.38 | A | inside | Keep |
| A8 unreacted methanol to glycerol phase | 70 % | Biodiesel phase keeps up to 40 % of the excess methanol, so glycerol phase holds at least about 60 % | VG pdf p.106 | A | inside | Keep |
| A11 methanol flashed 99.5 %; A13 wash 5 %; A14 water 0.3/0.05 % | as listed  | - | - | - | no source found | Find ester-wash and dryer data |

## SAF

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| Jet (kerosene) yield, SAF 24,000 t/yr on 30,000 t/yr UCO (S from DPR, ours 0.80 of raw UCO) | 80 wt % of feed | Maximum-jet case: kerosene 46.1, diesel 30.4, naphtha 8.5, LPG 6.0, fuel gas 1.5; RD case diesel 85 wt % | NREL Table G-1 (printed p.118) | A | outside (jet 1.7 times the reference) | Flag the DPR figure; re-balance to about 46 % jet or accept as RD-plus-jet; ask licensor (largest single issue) |
| Hydrogen consumption (total, 140.7 kg/h on 3,731 kg/h feed) | 3.8 wt % of feed | 4.0 (RD) to 4.5 (jet) wt % of feed; 2,400 to 2,800 scf/bbl = 57 to 67 scf/gal; ours about 55 scf/gal (my conversion) | NREL Table G-1 and printed p.30 | A | edge (slightly low) | Raise to about 4.5 wt % for jet mode; size H2 plant on 4.5 |
| F_HDO / F_DCO2 / F_DCO split 0.85 / 0.08 / 0.07 (CO+CO2 = 1.9 wt % of feed) | 0.85 HDO fraction | CO and CO2 4.0 wt % of feed in both RD and jet cases (implies roughly 74 % HDO, my derivation) | NREL Table G-1 | A | edge (ours has less CO+CO2) | Use 0.75 HDO to 0.25 decarboxylation as sensitivity; moves H2 and water |
| Naphtha 0.25 of (RD+naphtha); cracking gas 2 % of SAF; reflux, recycle 1.5, bed rise 45 K | as listed  | - | - | - | no source found | Ask licensor |

## Fruit and veg

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| Pulp 14 % by-product, IQF trim 22 %, COD 1.1 kg/kg dry matter, blanch steam, IQF energy | as listed  | - | - | - | no source found | Attempted: Stellenbosch fruit/veg wastewater thesis (fetch gave no PDF), OpenAlex results on mango waste (publisher walls); ask owner for FAO or WRC report |

## LNG

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| Specific power of liquefaction; static boil-off of tank at 90 % fill | repo model kWh/t; %/day | - | - | - | no source found | Attempted: Pellegrini 2014 weathering (Cloudflare wall), Dobrota 2013 (wrong file returned), MDPI BOG paper (access denied). Stopped on those hosts. Ask owner for the PDFs |

## Urea

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| NH3 and CO2 per tonne urea; reactor conversion; carbon conversion 0.90; CGE 64 % | repo model - | - | - | - | no source found | Attempted: EU LVIC-AAF BREF and Fertilizers Europe booklet (URLs 404); eurjchem BAT review has no consumption figures. Stoichiometry (2 NH3 + CO2 gives 0.567 t NH3 and 0.733 t CO2 per t urea) is derivation, not literature |

## Refinery

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| A3 hydrotreater H2 use 3 mol H2/mol S | 3 mol/mol S | Hydrotreating 150 to 300 scf/bbl feed (27 to 54 Nm3/bbl); whole plant 1,000 to 3,000 scf/bbl | LBNL pdf p.20 | A (figure is quoted from Gary and Handwerk 1994) | no direct comparison (ours is per mole S; convert to scf/bbl first) | Convert ours to scf/bbl on each cut and compare to 150-300 |
| A4 FCC yields (3.6 dry gas, 17.8 LPG, 49.4 gasoline, 5.95 coke) | as listed  | - | - | - | no source found | Ask owner for ANL/ Elgowainy refinery paper (publisher wall) or JRC REF BREF (URL 404) |

## LPG

| Assumption | Ours | Literature range | Source and location | Grade | Verdict | What to do |
|---|---|---|---|---|---|---|
| Delayed ignition split flash fire 0.6 : VCE 0.4 | 0.6 / 0.4 - | 60/40 (DNV 96) or 30/70 (LPG-Integraal), 'one chosen arbitrarily' | PB App. 4.C.10 (pdf p.110) | A | inside (at the 60/40 end) | Keep; show 30/70 as sensitivity |
| BLEVE fireball radius 106 m, 14 s for about 45 t | 3.24 m^0.325; 0.852 m^0.26 m; s | r = 3.24 m^0.325, t = 0.852 m^0.26 (m = mass in kg) | YB eq 6.90, 6.91 (pdf p.642) | A | inside (same equations) | Keep |
| BLEVE occurrence after instantaneous release with direct ignition; failure at 1.21 x set | 1.21 - | P(BLEVE) 0.7 stationary, 1.0 transport; failure pressure 1.21 x relief opening pressure | PB pdf p.76 | A | inside (1.21 matches) | Add P = 0.7 if frequencies are quoted |
| Hole sizes 10, 25, 168 mm; direct ignition by UKOOA / Cox | 25 mm | Purple Book set: 10 mm hole, 10-minute release, instantaneous; direct ignition gas of average reactivity under 10 kg/s: 0.2 (propane, butane are 'average') | PB Table 4.5 (pdf p.75), pdf p.42 | A | edge (25 mm not in the Purple Book set; ignition model differs) | State the model used; show 0.2 as a cross-check |
| Jet flame length 10.8 m for 2.34 kg/s propane; surface emissive power | 10.8 m | Yellow Book jet-flame method (Chamberlain) located but steps 10 to 23 not read | YB section 6.5.3 | C | no source found | Read Yellow Book steps 10-12 and 22-23 and rerun |

## Outside the literature range, ranked by effect

1. SAF jet yield 80 % of feed (DPR S value) against 46.1 % in the NREL maximum-jet balance: changes product slate, H2, and every downstream size.
2. Biodiesel oil FFA 2.0 wt % against a base-catalysis limit of about 1 %: needs pre-esterification, which the sheet does not draw.
3. CBG methane slip 1.5 % against national limits of 0.2 to 1 %: OX-401 carries the compliance; vendor guarantee needed.
4. CBG raw biogas CH4 55 mol % against 63 to 67 % measured on press mud: oversizes gas handling (conservative).
5. Edge cases that should be re-run: SAF H2 3.8 against 4.0 to 4.5 wt %; biodiesel conversion 98 % against 99.7 % needed; ethanol Y 0.90 against 88.5 % lab maximum; ethanol steam 13.3 MJ/L against 9.7 mean.

Open: LNG, urea, gasification, fruit and vegetable, refinery FCC and jet-flame rows still need a fetched source.

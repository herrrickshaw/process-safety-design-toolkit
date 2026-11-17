# Gap closure: heat and material balance, SAF / urea / refinery / LNG

Date 2026-11-11. Companion table: `GAP_CLOSURE_THERMO.csv` (28 rows, same wording). Screening aid. Nothing in the generators was changed.

Grades: A = document text read (fetched PDF, `pdftotext`) by this pass, or read by the validator and quoted from the `*_VALIDATION.md` file (marked "validator"); C = search snippet only; "computed" = recomputed with CoolProp/thermo, not a literature value.

Tally: 17 gaps closed with a sourced or computed value, 7 partly closed, 4 not closable.

## SAF (HEFA, 30,000 t/yr UCO)

Main source: NREL/TP-5100-87803, *SAF State-of-Industry Report: HEFA Pathway* (rev. 2024), fetched from osti.gov/servlets/purl/2426563.

| Gap | Ours | Sourced value | Proposed | Generator change | Confidence |
|---|---|---|---|---|---|
| Slate / yield | SAF 24,000 t/yr, 0.80 t/t | Table G-1 (p.118), jet mode, wt % of oil: jet 46.1, diesel 30.4, naphtha 8.5, LPG 6.0, fuel gas 1.5, CO+CO2 4.0, aqueous 8.0, H2 in 4.5. RD mode: diesel 85.0, jet 0 | SAF 13,800 t/yr (13,500-17,500 incl. earlier derivation), diesel 9,100, naphtha 2,550, LPG 1,800. 24,000 t/yr SAF needs about 52,000 t/yr UCO | S quantities become outputs of a yield vector (SAF = 0.461 x UCO) | high |
| Hydrocracking / light ends | CG_OF_SAF 2 %, N_SAF 11, loss 1.4 % | Light ends 16.0 wt % (jet) vs 7.0 wt % (RD): jet severity adds 9 points | Calibrate cracking to +9 points of oil | A: CG_OF_SAF, N_SAF | medium-high |
| H2 consumption | 3.77 wt % of UCO | 4.0 (RD) / 4.5 (jet) wt % of oil (Table G-1); 57-67 scf H2/gal feedstock (p.30) | 4.0-4.6 wt %, jet 4.5; 1,200-1,380 t/yr H2. 57-67 scf/gal equals 3.9-4.6 wt % at 0.92 kg/L (density is my assumption) | H2 totals, split chemical vs make-up | medium-high |
| Stage-1 heat of reaction | 0.30 MJ/kg | None read as a number for triglycerides. Sulzer white paper: exotherms upwards of 200 C; NREL: liquid recycle up to 1:1 for about 10 wt % O removal. Validator computed 1.02-1.11 MJ/kg | 1.0-1.1 MJ/kg (1,060-1,150 kW at 3,731 kg/h), +/-10 % | DT_R1, R_TOT, CP_L must follow from Q, not the reverse | medium (partial) |
| Bed rise, quench | 45 K, R_TOT 2.5 | NREL App. D.2 (p.103): deoxygenation 300-350 C, 35-50 bar, multiple fixed beds, H2 recycle to interbed quenches; isomerization/hydrocracking 570-650 F, 500-1,100 psia | 3-4 beds with interbed H2 quench plus recycle <= 1:1; unquenched rise 316-344 K means quench gas is needed, not only liquid recycle | Sheet 4 runaway numbers (understated 2.3-2.9x) | medium (partial) |
| Liquid cp | 2.3 kJ/kg/K | 3.23 (CoolProp, validator) | 3.0-3.3 | A: CP_L | high |
| Fractionator feed | sharp V-201 split, E-403 420 kW | NREL says only "cooled and flashed, then fractionated"; no T or vapour fraction | Keep computed 696 kW and 27 % paraffin to vapour as unsourced; use an EOS flash | remove E-402 clamp | not closable |

Unresolved: OIES gives 55-60 kg H2 per t SAF; NREL Table G-1 gives about 98 kg per t SAF on a total-oil basis. The two use different bases (net vs total, co-products); not reconciled. No open triglyceride reaction-enthalpy figure was read (the IntechOpen value of -115.0 kJ/mol for stearic acid hydrogenation is a snippet, grade C).

## Coal-to-urea (Talcher-class)

Sources: Talcher Fertilizers pre-feasibility report and EIA summary (validator); UBA *German Notes on BAT, Urea* (2001, fetched copy re-read here); EFMA Booklet 1 (2000, re-read); TDA/DOE final report DE-FE-0026142 (2019, osti.gov/servlets/purl/1572476); Fleck and Eckel, Fuel 2018 (elib.dlr.de/118959).

| Gap | Ours | Sourced value | Proposed | Generator change | Confidence |
|---|---|---|---|---|---|
| NH3 per t urea | 1.70 | 0.571 (2,200/3,850 TPD); stoichiometric 0.567 | 0.57 | A7: add stripper/carbamate recycle; S24 returns to reactor | high |
| CO2 per t urea | 1.25 | 0.740 (60,480 Nm3/h over 3,850 TPD); stoichiometric 0.733 | 0.733-0.74 | same | high |
| Coal per t urea | 4.17 (1.39 after recycle fix) | 0.902 feed incl. pet coke; 1.74 including 134.0 t/h fuel coal | 0.9-1.74 depending on blend and whether fuel is counted | pet-coke blend and fuel-coal inputs | medium (partial) |
| ASU power | 733.8 kWh/t O2 (210.7 MW) | "250-300 kWh per ton of O2 instead of 30 kWh per ton" (TDA/DOE report, background text near Fig. 6) | 250-300 kWh/t O2: 72-86 MW for the same O2 | A8 / ASU input | medium (single source; "ton" undefined) |
| WGS K at 1673 K | Moe 0.2031 | Validator thermodynamic K 0.3068. DLR rig reaches WGS equilibrium at 1495 K, K defined from species ratios (Eq. 18). Moe stated valid 600-2000 K only in a secondary snippet (C) | Use polynomial-based K, about 0.31; downstream H2 changes only -0.2 % | gasifier K correlation | medium (partial) |
| Loop make-up and purge | 2,856 Nm3/t NH3 | Talcher 2,651; EFMA: 20-30 % per pass, purge holds inerts at 10-15 % | 2,630-2,660 with purge recovery | A6 | high |
| Steam per t urea | not computed | UBA: 0.92 Stamicarbon, 0.85 Snam, median 1.3 t/t | 0.85-1.3 | add steam line | high |
| Power per t urea | not computed | UBA: 43 kWh/t excl. CO2 compressor (+23 granulation); 115 incl. CO2 compressor; BASF about 70 | 43-115 kWh/t; CO2 compression 126 kWh/t CO2 | add power line, multi-stage K-601 | medium-high |

Unresolved: the TDA figure of 30 kWh per ton theoretical differs from the validator's 52.7 kWh/t O2 minimum (different separation basis); a second, independent ASU source (for example an NETL baseline exhibit) was not obtained.

## Refinery (Paradip-class)

Sources: WRI-02-R012 (osti.gov/servlets/purl/822151); *Fundamentals of Delayed Coking* JIP, DOE/BC/15182-2 (osti.gov/servlets/purl/807578), Tables 39-41; Honeywell UOP Apr 2021 (digitalrefining 1002610); ENERGY STAR petroleum refinery guide; Paradip documents read by the validator.

| Gap | Ours | Sourced value | Proposed | Generator change | Confidence |
|---|---|---|---|---|---|
| Coker coke | 43.6 wt % of VR (1.6 x CCR at 27.25) | 1.6 x CCR is the Gary and Handwerk 1975 ratio quoted in WRI-02-R012. Pilot coke vs MCR (JIP Table 41): 25.74 gives 32.7, 29.4 gives 38.8, 21.77 gives 29.6, 20.25 gives 30.7 wt % (ratios 1.27-1.52). UOP: a delayed coker typically converts about 30 wt % of VR to coke. Paradip petcoke 7.8 % of crude over 4.4 Mt/yr coker feed = 26.6 % (derived) | 27-35 wt % of VR, central 30 (about 1.2-1.4 x CCR) | A5 | high |
| Petcoke % crude | 11.9 | 7.8 (7.2-8.2) validator | 7-9 | follows from coke and slate | medium-high |
| Crude sulphur | 2.90 | 2.26 (2.10-2.39) validator | 2.1-2.4 | refit blend fractions or label heavy case | high |
| Hydrotreater H2 (A3) | 167 / 358 scf/bbl | 150-300 scf/bbl hydrotreating (ENERGY STAR quoting Gary, secondary); kerosene HT 4-12, cracked distillate 17-41 scf/gal (NREL p.30 fn 16) | add aromatics term, keep S-only as floor | A3 | medium (partial) |
| NHT feed | 1.61 Mt/yr vs 3.96 nameplate | no source explains it | none | check 150 C end point | not closable |
| FCC yields (A4) | reference case | no open yield table found (two searches) | none | A4 stays unvalidated | not closable |
| Crude heater duty | 216.6 MW | only the validator's surrogate route (+7.2 %) | none | none | not closable |

Note on the coker: the Tulsa pilot ratios (1.27-1.52) bracket the 1.6 rule from below; the real-plant ratio is lower still (26.6 % of feed), which also implies the coker feed CCR is below the 27.25 used. Slate CCR should be checked before the yield is trusted.

## LNG (2.0 mtpa, C3MR-class)

Sources: Aoki and Kikkawa (Chiyoda), *LNG Plant Combined with Power Plant*, INIS QA9700008 (inis.iaea.org/records/4rqyy-29d76); IJCEA vol. 5 no. 1 (2014), paper 343-CA423; Energies 13(21):5578 (2020); CoolProp recomputation from `LNG_VALIDATION.md`.

| Gap | Ours | Sourced value | Proposed | Generator change | Confidence |
|---|---|---|---|---|---|
| NG cooling 233-173 K | 11,027 kW | 25,915 kW (CoolProp, computed); 173-114 K 12,165 kW | 25,900 + 12,200 kW | `liquefaction.py` enthalpy integral | high |
| Propane vs MR split | propane 36.7 MW, LRC 27.2 MW | C3:MR power ratio 1:2 to 3; Qatargas 2.3 MTA train C3 27 MW, MR 64 MW | propane 25-33 % of shaft power | A6 and loop sizing | medium-high |
| Specific power, all loops | 297 (421 with subcool loop) | Qatargas 91 MW per 2.3 MTA = 317-347 kWh/t at 8,000-8,760 h/yr (derived; hours are my assumption); Timor-Leste C3MR 5.83 kWh/MMBTU-LNG; Air Products 275-375 (C) | 300-350 kWh/t | total-power ledger incl. K-202 and subcool loop | medium |
| Staging, suction volume | single-stage PR 589; K-202 236,297 m3/h | Qatargas MR in three casings (low-pressure double flow, intermediate, high-pressure) on three Frame 5 drivers; propane multi-casing plus booster; no volumes | 3 MR casings, K-202 in parallel casings; MR evaporating pressure of a few bar is not sourced here | MR loop Pe, staging | partial |
| Tank boil-off | 0.122 %/day | design below 0.05 %/day; 0.02-0.1 wt %/day; 260,000 m3 full-containment: 0.012 (80 % fill), 0.026 (50 %), 0.12 (10 %) | 0.03-0.05 %/day | TK-501 heat ingress | high |
| Driver fuel gas | not computed | no GT heat rate read; electric drive 1.8 % (Freeport) | state driver type; fuel = shaft / 0.33-0.38 (assumed) | fuel line, shipped-LNG basis | partial |

Unresolved: no open C3MR document with per-casing suction volumes was obtained (Air Products PDFs 404, ScienceDirect 403, ifpenergiesnouvelles 403 challenge; stopped on those hosts).

## Highest-impact corrections

1. Urea train: single pass to full recycle (NH3 1.70 to 0.57, CO2 1.25 to 0.74 t/t urea).
2. SAF slate: 24,000 t/yr SAF is not possible from 30,000 t/yr UCO; the sourced jet-mode slate gives about 13,800 t/yr, and 24,000 t/yr needs about 52,000 t/yr UCO.
3. LNG refrigeration: NG cooling duty about 2.3x higher in the 233-173 K span, with MR taking 67-75 % of shaft power. (The coker coke correction, 43.6 to about 30 wt % of VR, is a close fourth.)

Sources not usable: Schabron (OGST 1997) 403 challenge; sciencedirect.com 403; Chulalongkorn thesis redirect with no file; no CAPTCHA or login was bypassed.

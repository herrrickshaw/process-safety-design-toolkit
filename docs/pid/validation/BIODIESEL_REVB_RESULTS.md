# BIODIESEL (B100, 20 KLPD) P&ID Rev B: results, 11 Nov 2026

Generator `scripts/gen_pid_biodiesel.py`, output `docs/pid/BIODIESEL_PID_Set_RevB.html/.pdf` (8 sheets). Closure 0.00 % (mass), element balance C, H, O, Na closed (asserted in code). Frozen tool runs: `BIODIESEL_REVB_flash_check.py` (thermo 0.6.1 UNIFAC-Dortmund, CoolProp 8.0). Same table as CSV: `BIODIESEL_REVB_RESULTS.csv`.

## (a) Every flagged metric

| metric | Rev A | Rev B | reference | deviation before | deviation after | status |
|---|---|---|---|---|---|---|
| E-501 ester cooler duty, MJ/batch | 176.1 | 200.5 | 202.0 (thermo cp methyl oleate); Rev B independent re-run 202.2 | -12.9 % | -0.8 % | closed (species cp, D) |
| E-602 product cooler duty, MJ/batch | 176.0 | 200.3 | 199.3 | -11.7 % | +0.5 % | closed |
| V-401 coil duty, MJ/batch | 522.9 | 569.3 | 572.6 (Rev A basis); Rev B independent 570.0 | -8.7 % | -0.1 % vs independent | closed (basis changed: 0.10 bar flash with water) |
| V-402 coil duty, MJ/batch | 446.7 | 493.8 | 458.7 (Rev A basis) | -2.6 % | basis changed | agrees; not re-compared on identical basis |
| V-401 methanol recovery, ester phase | 99.5 % at 80 C, 1.0 bar(a) | 95.1 % at 0.10 bar(a) | UNIFAC-Dortmund 14.5 % at 1 bar; 95.1 % at 0.1 bar (Rev B composition); Alam about 90 % at 0.2 atm | +586 % (infeasible) | about 0 % (95.06 vs 95.1) | closed: pressure changed, 99.5 % no longer claimed |
| V-402 methanol recovery, glycerol phase | 99.5 % at 1.0 bar(a) (needs 0.011 bar) | 96.6 % at 0.10 bar(a) | UNIFAC 96.6 % at 0.1 bar; 99.3 % at 0.02 bar | infeasible | reduced: 3.4 % of its methanol stays in crude glycerol (2.1 wt% of stream 17) | reduced: 99 % needs about 0.02 bar; accepted residual to be agreed with the glycerol buyer |
| Methanol condensing at 0.10 bar | CW condenser 80 to 40 C (not stated as infeasible) | chilled glycol 5 C; Tsat(0.10 bar) 15.2 C | CoolProp 15.18 C | new finding | closed | closed (E-401 now chilled, RU-401 and VP-401 added) |
| FFA in oil, single-stage NaOH | 2.0 wt% | 1.0 wt% acceptance limit | pretreat above about 1 % (Van Gerpen NREL/SR-510-36240) | +100 % | 0 % | closed (limit; acid pretreatment not drawn) |
| Wash water, % of ester | 5 | 20 (and 5 % of aqueous to dryer) | 20 continuous, 30-40 batch (Sheehan p148); DPR none | -75 % | 0 vs Sheehan | closed vs Sheehan; unchanged conflict with DPR no-wash (chosen and stated) |
| Fresh methanol per t B100, kg/t | 106.6 | 111.2 | 110.2 (Sheehan Tbl 13, my sum) | -3.3 % | +0.9 % | closed (better) |
| Crude glycerol per t B100, kg/t | 137.2 | 124.0 | 150 (Sheehan Tbl 13; purity basis not read) | -8.5 % | -17.3 % | unchanged / worse: vacuum flash strips methanol and water from the crude; reference basis unknown; pure-glycerol basis stated (10.1 %) |
| Methanol recovery heat, MJ/t B100 | 220.4 (V-401 + V-402 coils) | 242 coils; 557 reboiler (C-401); 799 total | 224.7 (Sheehan Tbl 94, methanol dryer column only) | -1.9 % | reboiler +148 % | open: Reboiler is 2.4x Sheehan: our recovered methanol is 105 kg/t (6:1 excess), Sheehan duty implies 44 kg/t at the same reflux. Verify with licensor |
| Total thermal oil duty, MJ/batch | 1,097.6 | 3718 | - | - | - | new load: thermopack about 3.4x larger; CW 958 to 2899; new chilled glycol 679 |
| Relief or vent for 9 vessels (V-302, V-401, V-402, M-301, V-601, V-901, T-101, T-701A/B, T-801) | none or no stated reason | relief schedule rows for all 22 items, devices drawn | lint | 9 gaps | 0 gaps | closed (vendor package items: V-901, VP-401/601 not drawn) |
| Instrument tags not in a list (FCV-501, LIC-501, AT-501, LSH-311, PAL-951, ...) | family rows only | instrument index, 33 tags, sheet 7 | lint | gap | closed | closed |
| Crude glycerin vs EIA 0.20 m3/KL; reaction T; oil heating | as Rev A | unchanged | Al Hind EIA (typo above stoichiometric); DPR 40 C scheme | -52 / -38 / -78 % | unchanged | unchanged, explained in the validation |

## (b) What could not be closed

- Methanol column duty is 2.4x the Sheehan column figure (cause not identified; 6:1 excess gives 105 kg/t of recovered methanol). Stage count not computed (Sheehan Fig 66 axis not reliably read); reflux 3.665 taken as molar.
- V-402 does not reach 99.5 %: 96.6 % at 0.10 bar; 99 % needs about 0.02 bar. UNIFAC on methanol/water/glycerol only; soap, NaOH and salts ignored; no measured data.
- Crude glycerol basis (Sheehan 150 kg/t, purity not read) and Table 102 (212.8 kg/t at 80 %) unresolved; Rev B gives 124 kg/t crude.
- Wash vs DPR no-wash: chosen wash (20 %, Sheehan); the DPR no-wash B100 quality route is not documented (IS 15607 not read).
- Acid esterification pretreatment is not drawn (1 % FFA is a feed acceptance limit). Thermopack fuel, TO type and temperature, column and vessel volumes, design pressures, PESO class and distances, bund volume of T-201 are open.
- Utilities per tonne (steam, power): no independent reference for this scheme; Sheehan 0.40 to 2.59 GJ/t steam, 9 to 64 kWh/t power are bands only.

## (c) Safety items present vs gaps

Present (sheet 6 to 8): relief schedule 22 rows (22 items; PSV-301A/B, 401/402, 403, 601; PVRV-101, 201, 202, 301, 302, 501, 701A/B, 801 drawn; TSVs and vendor packages listed, not drawn); two toolkit screening sizes (R-301 fire case, C-401 loss of cooling; inputs A); ESD matrix 13 initiators x 12 final elements; 9 SIFs with assumed SIL (A); instrument index 33 tags; bund rule and example, safety-distance basis, detection and isolation logic, vacuum-system, thermopack and caustic notes, hazardous-area zones from release grade; 9 HAZOP-style nodes; 6 inherently safer options.
Gaps (standard not obtained): API 520/521/2000 current editions, IEC 61511 and LOPA, OISD standards, PESO / Petroleum Rules 2002 and SMPV(U), NFPA 30, fire-water rates, area-classification standard (IEC 60079-10-1), flammable limits and gas group of methanol, Indian boiler / thermal-fluid heater rules.

## (d) Verify with a licensor or vendor

Vacuum flash design (thin-film vs pot) and achievable methanol recovery at 0.1 bar; chiller and vacuum pump (leak rate sets vent loss, A 1 %); column stage count, reflux and reboiler duty; wash scheme and B100 quality route; FFA specification and pretreatment; thermopack sizing (about 3.7 GJ/batch, 172 kW average) and heating medium choice; relief design pressures and set points; effluent load from a 20 % wash (about 3.5 t/d) and column bottoms.

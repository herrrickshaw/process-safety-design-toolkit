> **Rev C2 note:** the balance was rebased on sourced values after this file was written (see REBASE_REVC.md). Flow and duty numbers quoted below are from the earlier Rev B balance and are superseded by the registers and the sheets; assumptions and open items still apply.

# Area 60 - ammonia synthesis loop, refrigeration, storage (sheets 601-619)

Built by `scripts/urea_area_60.py` (`build(pkg)`; run the file to render `/tmp/area60.html` and the lint). Basis: Rev B balance x K = 1.2784 (3,850 t/d urea).
Tags: S sourced, D derived, A assumed. `CP8` = value computed in this session with CoolProp 8.0 (HEOS) and typed as a constant (same practice as `gen_pid_urea.py`).
No document was fetched in this session: nothing here is cited to a standard, licensor or vendor. Licensor names (KBR for ammonia) are public; no licensor data used.

## Sheets
| No. | Unit | Template | Rev B streams / new streams |
|---|---|---|---|
| 601 | K-401A make-up compressor, LP casing 40 to 89.4 bar | compressor | 15, 611 |
| 602 | K-401B, HP casing 89.4 to 200 bar | compressor | 611, 612 |
| 603 | K-402 loop circulator | package | 613, 27 |
| 604 | E-403 feed / effluent exchanger | hx | 616, 614, 618, 619 |
| 605 | R-401 converter, 3 beds, cold quench | reactor | 614, 615, 617 |
| 606 | E-404 waste-heat boiler (50 bar steam) | hx | 617, 618, 644, 645 |
| 607 | E-405 loop water cooler | hx | 619, 620, 640, 641 |
| 608 | E-406 cold interchanger | hx | 620, 621, 623, 613 |
| 609 | E-401 loop chiller (NH3 at -10 C) | hx | 621, 622, 637, 633 |
| 610 | V-401 NH3 separator | vessel | 622, 623, 624, 625 |
| 611 | V-402 letdown drum | vessel | 646, 626, 627 |
| 612 | PGR-401 purge-gas recovery | package | 625, 626 in; 30, 16 out |
| 613 | V-403 auto-refrigeration flash drum | vessel | 629, 630, 17 |
| 614 | K-501 refrigeration compressor (2 stages, BOG duty) | package | 632-635 |
| 615 | E-503 refrigerant condenser | hx | 647, 636, 642, 643 |
| 616 | V-404 refrigerant flash drum | vessel | 639, 634, 637 |
| 617 | T-501 refrigerated tank + P-501A/B | tank | 17, 648 |
| 618 | K-502 standby BOG compressor, flare route | package | 649, 650 |
| 619 | C-501 NH3 vent absorber | column | 651-654 |

Every sheet carries the template instruments, PSV with destination, ESD valve (XV-xx5x), drains/vents and a local NH3 (or H2/NH3) detector pair with 2oo2 HH to ESD (alarm limits A, HSE to confirm). Stream 29 (V-302 condensate, area 40) is not an area 60 unit and is not drawn.

## Balance (all asserted in code)
Converter inlet = effluent mass = stream 15 + 27 (478.8 t/h). Stream 15 = 17 + 16 + 30 (N and H closure from Rev B). V-401 liquid = stream 17 + dissolved gas; loop purge + flash gas = Rev B 16 + 30. R-401 feed + quench = effluent. Refrigerant: K-501 HP-stage mass = chiller + V-404 flash + LP stage; condenser liquid = V-404 branch + V-403 branch.
Key numbers: R-401 heat 77.7 MW (Rev B n(NH3) x 52.34 kJ/mol x K); quench 26 t/h; WHB 56.7 MW, 87 t/h steam at 50 bar; E-403 118 MW; E-405 26.9 MW; E-406 11.5 MW; E-401 25.3 MW; refrigerant 70 t/h at -10 C; K-501 9.8 MW (LP 0.7, HP 9.1); E-503 38 MW; K-401 24.0 MW (Rev B S value x K); K-402 power from Q dP/eta; tank 35,300 m3 (10 days), boil-off 0.2 t/h.

## Assumptions (A, with ranges)
Separator 0 C (-10 to 10); refrigerant evaporates at -10 C (-20 to 0), condenses at 40 C (CW 30 to 42 C); converter nozzle inlet 300 C (280-340), WHB gas outlet 330 C (300-360); loop dP 8 bar (5-15); GHSV 20,000 1/h (10,000-25,000, catalyst volume 63 m3); dissolved gas in NH3 0.3 mass % (0.1-1); mean gas cp 3.55 kJ/kg/K (CP8) with NH3 ignored; compressor eta 0.75; U for 200 bar gas 300 W/m2/K (200-500); letdown pressure 25 bar (15-30); ideal-gas Raoult condensation (real gas condenses more); tank 10 days (5-15), 8 W/m2 ingress (5-12); P-501 delivers at 25 bar (20-30); vent absorber water 20 t/t NH3 (10-30), 0.5 % NH3 slip; recovery 90 % in PGR (Rev B).

## Overrides of Rev B values (Rev C items)
Stream 27 temperature = K-402 discharge 34.7 C (Rev B 40 C), because Rev B has no refrigerated separator. Stream 16 pressure = 5 bar (Rev B 200 bar is the take-off pressure). Stream 17 flow includes the boil-off return (+0.2 %); net to urea (18) stays Rev B. Residual NH3 in the separator gas (about 2 mol % at 0 C, ideal) is not in Rev B stream 27.

## Gaps (not sized or not sourced)
Relief loads for every PSV (fire, tube rupture, runaway) - "not sized" in the relief schedule; ammonia relief / vent scrubbing and water-spray / deluge protection (no document fetched); bund volume rule; tank containment class and "type A" definition; converter mechanical layout (bed split, internal exchanger, 450 C limit); refrigeration compressor type and oil system; PGR technology and power; drier / CO2 guard bed; steam drum and BFW for E-404; real-gas NH3 equilibrium (H2-NH3 has no CoolProp binary, so effluent density uses the H2:N2 compressibility); tube-rupture analysis for E-404 (200 bar vs 50 bar); K-501 stage-B inlet superheat; flare as final NH3 destination (HSE decision).

## Template defects found (not fixed; drawn around locally)
1. `sheet_tank`: volume = flow(t/h) x 24 x days / rho(kg/m3) lacks x1000 (35 m3 instead of 35,000 m3). Text, panel and equipment row are patched in `urea_area_60.py` (`fix_text`).
2. `sheet_vessel`: level control valve is drawn only with pumps; vessels without pumps get a local `lvalve` (V-401, V-402, V-403, V-404).
3. `sheet_compressor` always draws an aftercooler; K-402 and K-501 therefore use `sheet_package`. The compressor equipment row is built from the cooled discharge temperature (design T too low); patched for K-401A/B.
4. `sheet_hx` U_SCREEN gas_gas = 60 is a low-pressure value; added keys `gas_gas_hp` / `gas_liq_hp` at runtime (not in the file).
5. Hazard text longer than about 44 characters overflows the data panel.
Cosmetic (engine): line labels run into the KO drum on 601/602; PSV label overlaps stream diamond on 604; tank label overlaps the bund box on 617; LIC/LAHH bubbles overlap on column sheets; LV drawn locally sits close to the HV on vessel sheets.

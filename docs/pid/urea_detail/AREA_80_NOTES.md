# Area 80 Utilities: unit notes (coal-to-urea, 3,850 t/d urea, Talcher-class)

Generated with `scripts/urea_area_80.py` (20 sheets, numbers 801-820). Basis: Rev B balance x K = 1.2784 (D); urea 160.4 t/h. Tags: S sourced, D derived, A assumed (range given).
Sourced figures are only those already read for Rev B in `gen_pid_urea.py` (UBA 2001 steam 0.92 t/t, cooling water 70 t/t, power 43+23 kWh/t, process water 0.46-0.65 m3/t; TDA ASU 275 kWh/t O2). No new document was fetched for this area.

## Sheets
| No. | Tag | Content |
|---|---|---|
| 801 | SH-801 | HP/MP/LP steam headers (local drawing), PSVs, header trips |
| 802 | PRDS-801 | HP to MP letdown with desuperheater (spray ratio, mass closure asserted) |
| 803 | PRDS-802 | MP to LP letdown with desuperheater |
| 804 | V-801, P-801A/B | condensate collection tank, transfer pumps |
| 805 | D-801, P-802A/B | deaerator with BFW storage and BFW pumps (steam sparger drawn locally) |
| 806 | BFW-801 | BFW header, drum feed, spray take-off |
| 807 | V-803 | HP blowdown flash drum |
| 808 | B-801 | auxiliary boiler, coal-fired CFB assumed |
| 809 | T-801, P-805A/B | raw water storage and pumps |
| 810 | DM-801 | DM plant (cation, anion, mixed bed, packaged) |
| 811 | T-802, P-806A/B | DM water storage and pumps |
| 812 | CT-801 | cooling tower, water balance (evaporation, drift, blowdown, makeup) |
| 813 | P-803 | CW circulating pumps (3 duty + 1 spare) |
| 814 | DOS-801 | CW chemical dosing skid |
| 815 | K-801 | instrument and plant air compressors and dryers |
| 816 | V-804 | air receiver (local drawing, gas hold-up sizing) |
| 817 | N2-801 | nitrogen distribution (slip of Rev B stream 26, compression, header) |
| 818 | SLD-801 | power distribution single-line block diagram (no standards text) |
| 819 | ETP-801 | effluent treatment and ZLD concept (packaged) |
| 820 | UB-801 | plant utility balance table |

## Key numbers (all asserted to close in code)
- HP steam to gasifier and shift (Rev B streams 3+6+8 x K): 135.8 t/h (D). MP steam to the urea stripper: 147.6 t/h (0.92 t/t, S UBA; range 136-209 t/h from 0.85-1.30 t/t).
- Letdown worst case (all MP and LP through the stations): HP header 312.9 t/h, spray water 16.9 + 6.2 t/h, BFW 342.3 t/h, DM makeup 123.2 t/h, deaerator steam 23.2 t/h.
- Cooling water: central 16,764 t/h (195 MW); range 11,229-21,793 t/h (130-253 MW). Low end = UBA urea train alone (70 t/t x urea, dT 10 K); central adds 85 % of ASU, K-401 and K-601 shaft power as cooler duty (ASU 37, K-401 24, K-601 15 MW, Rev B x K); high end = central + 30 % for the E-102/E-103/C-302/refrigeration gaps. Tower: evaporation 292, blowdown 70, makeup 365 t/h.
- Auxiliary boiler: assumed coal-fired (coal is on site, Rev B has no natural-gas supply); 99 t/h = 0.35 x (HP + MP demand); coal 18.3 t/h at the Rev B coal HHV 17.59 MJ/kg (S, Dulong). A gas-fired package boiler would replace stream 827 by fuel gas.
- Identified electric load 91 MW (ASU, K-401, K-601, urea+granulation from UBA, area 80 pumps/compressors); gasification island, coal handling and HVAC are not in Rev B.
- Raw water abstraction 409 t/h (DM feed + net cooling-tower makeup); ETP inflow 86 t/h, recovered 85 t/h, salt cake 0.23 t/h.

## A assumptions and ranges
| Name | Value | Range | Meaning |
|---|---|---|---|
| P_MP | 25 | 18 - 30 | MP header pressure, bar abs (not sourced; urea stripper steam) |
| T_MP | 300 | 250 - 350 | MP header temperature, C |
| P_LP | 4.5 | 3.5 - 6 | LP header pressure, bar abs; carbamate-condenser steam side is 4 bar per UBA (via gen_pid_urea) |
| T_LP | 160 | 150 - 200 | LP header temperature, C |
| LP_FRAC | 0.2 | 0.1 - 0.3 | LP users (C-302 reboiler etc., excl. deaerator) as fraction of MP urea steam; C-302 duty is NOT computed in Rev B |
| CP_S | 2.2 | 2 - 2.6 | cp of superheated steam, kJ/kg/K (screening) |
| LAM | 2300 | 2100 - 2500 | spray water: sensible heating from ~105 C to saturation plus latent heat, kJ/kg (screening) |
| BD_F | 0.02 | 0.01 - 0.03 | boiler blowdown fraction of steam raised |
| FL_F | 0.25 | 0.15 - 0.35 | fraction of blowdown flashing to LP header at V-803 |
| RET_MP | 0.9 | 0.8 - 0.95 | condensate return fraction of MP urea steam |
| RET_LP | 0.8 | 0.6 - 0.9 | condensate return fraction of LP user steam |
| PC_REUSE | 0.9 | 0.6 - 0.95 | fraction of process water (stream 23) reused as BFW after hydrolysis/desorption |
| COND_FLASH | 0.02 | 0.01 - 0.05 | flash steam at V-801 as fraction of returned condensate (not credited to the LP header, conservative) |
| VENT_F | 0.002 | 0.001 - 0.005 | deaerator vent as fraction of BFW |
| DM_RAW_WASTE | 0.05 | 0.03 - 0.1 | DM plant regeneration/rinse waste as fraction of raw-water feed |
| CW_DT | 10 | 8 - 12 | CW temperature rise across users, K (wet-bulb for Talcher not sourced) |
| T_CWS | 32 | 30 - 35 | CW supply temperature, C |
| HEAT_REJ | 0.85 | 0.8 - 0.95 | fraction of compressor/ASU shaft power rejected to CW through inter/after-coolers |
| LAM_EV | 2400 | 2300 - 2450 | latent heat of evaporation at cooling-tower water temperature, kJ/kg |
| COC | 5 | 4 - 6 | cycles of concentration (raw water analysis is a gap) |
| DRIFT_F | 0.0002 | 0.0001 - 0.0005 | drift loss as fraction of circulation |
| TDS_F | 0.002 | 0.001 - 0.005 | dissolved solids in ETP inflow, mass fraction (raw water analysis is a gap) |
| CAKE_SOL | 0.75 | 0.6 - 0.9 | solids fraction of the salt cake |
| IA_NM3 | 6000 | 3000 - 10000 | instrument air Nm3/h (control-valve count not available at this level) |
| PA_NM3 | 3000 | 1500 - 6000 | plant (service) air Nm3/h |
| N2_NM3 | 2000 | 500 - 5000 | continuous plant nitrogen Nm3/h (blanketing, seals, purges; start-up inerting is intermittent and a gap) |
| AUX_F | 0.35 | 0.25 - 0.5 | start-up/standby steam as fraction of (HP gasifier+shift steam + MP urea steam) |
| DH_HP | 2.76 | 2.6 - 2.9 | enthalpy rise BFW(105 C) to 50 bar 400 C steam, MJ/kg (steam-table check pending) |
| ETA_B | 0.85 | 0.8 - 0.9 | aux boiler efficiency on HHV |
| EXC | 0.2 | 0.15 - 0.3 | excess air, CFB |
| HOLD_MIN | 2 | 1 - 5 | air receiver hold-up time on compressor trip, minutes at design demand |
| P_AIR_MIN | 6 | 5 - 7 | lowest acceptable instrument-air pressure, bar abs |
Other A values fixed in code: deaerator 105 C, condensate 90 C, DM 30 C, steam latent for the deaerator 2,200 kJ/kg, BFW pump dP 65 bar, CW dP 3.5 bar, MP 25 bar / 300 C, LP 4.5 bar / 160 C (HP 50 bar / 400 C is the Rev B stream condition).

## Gaps (not sized or sourced)
- No steam generation balance: E-101/E-102/E-103 and E-601 steam raising, turbine extraction and the C-302 reboiler duty are not in Rev B (no property model). The steam system is sized on demand.
- No steam-table enthalpies: desuperheater spray and deaerator heat use screening constants (cp 2.2 kJ/kg/K, 2,300 and 2,200 kJ/kg, A) and the aux-boiler enthalpy rise (2.76 MJ/kg, A 2.6-2.9): replace by a steam-table balance.
- Raw water source, analysis, permit; DM resin and regenerant data; boiler water chemistry limits; ETP discharge limits; wet-bulb temperature for the tower; instrument-air demand (needs the control valve count): all gaps, no document available.
- Power route (grid / captive), voltage levels, protection and earthing: electrical design, not set.
- Utilities-building and laboratory are out of scope.

## Template defects met (library not edited; drawn around locally)
1. `sheet_package`: PSV set pressure is the design pressure of the FIRST inlet and the destination is always "flare / safe location". Wrong for letdown stations, air and N2 headers: the register rows are patched (`fixrelief`), the drawing shows the tag only.
2. `sheet_package`: five outlets overlap labels with diamonds (spacing 40 px); with more than 4 interlocks the bubbles reach the utility labels; "0.0 gap" utility arrows add noise (removed). Sheet 801 drawn locally for this reason.
3. `sheet_package`/`run`: solids, flue-gas and air ducts are sized as pipes (NPS capped at 48): B-801 flue gas and combustion air show NPS 48 at 23-38 m/s; read them as ducts.
4. `sheet_vessel`/`sheet_tank`: PSV line is always labelled "PSV to flare header (A)" and the vent label "N2 purge"; `relief_dest` changes only the register. Steam/condensate/air vessels therefore carry a wrong drawn label (noted on the sheets).
5. `sheet_vessel` sizes by liquid residence only: an air receiver comes out 0.0 m3 (sheet 816 drawn locally with a gas hold-up volume).
6. `sheet_column` sets diameter from a 2 m/s vapour rule applied to the liquid flow: a deaerator would be 0.2 m ID, so D-801 uses `sheet_vessel` with a locally drawn steam sparger.
7. `data_panel` columns are 150/215/80 px: text longer than 25/38/14 characters overflows (a check in the area file warns).
8. Cosmetic (engine owner): diamond and valve clusters on short or vertical segments (sheets 805, 816 outlets, 819 inlets with 4 lines).

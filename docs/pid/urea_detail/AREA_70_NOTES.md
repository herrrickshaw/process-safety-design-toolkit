# Area 70 - urea synthesis, recovery, concentration, granulation (sheets 701-722)

Built by `scripts/urea_area_70.py` (`build(pkg)`; run the file to render `/tmp/area70.html` and the lint). Basis: Rev B balance x K = 1.2784 (3,850 t/d urea).
Sourced inputs: Rev B streams 18, 19, 21, 22, 23, 24; UBA (2001) steam 0.92 t/t urea, CW 70 t/t, process water 0.46-0.65 m3/t and 126 kWh/t CO2 (via `gen_pid_urea.py`, S, p.19-25); CO2-stripping family (Stamicarbon is the public licensor name only, no licensor data). `CP8` = CoolProp 8.0 value computed in this session, typed as constant. No document was fetched in this session.

## Sheets
| No. | Unit | Template | Streams (new ids 700-760) |
|---|---|---|---|
| 701 | K-601A CO2 compressor LP casing 1.5 to 15 bar | compressor | 700, 702 |
| 702 | K-601B HP casing 15 to 150 bar | compressor | 702, 19 |
| 703 | TG-601 steam turbine + surface condenser | package | 751T-754T |
| 704 | V-601 NH3 vessel + P-601A/B HP NH3 pumps 25 to 150 bar | vessel+pumps | 18 |
| 705 | R-601 urea reactor 180 C, 150 bar | vessel | 705, 21 |
| 706 | C-601 HP CO2 stripper | column | 19, 21, 706, 707, 708 |
| 707 | E-601 HP carbamate condenser (LP steam raising) | hx | 710-713 |
| 708 | C-603 HP scrubber | column | 714-716, 704 |
| 709 | C-602 MP decomposer | column | 717-720 |
| 710 | E-603 MP carbamate condenser | hx | 721-724 |
| 711 | V-603 MP carbamate vessel + P-602A/B | vessel+pumps | 733, 716 |
| 712 | C-604 LP decomposer / rectifier | column | 727-730 |
| 713 | E-604 LP carbamate condenser | hx | 728, 731, 725, 726 |
| 714 | V-604 LP carbamate vessel + P-603A/B | vessel+pumps | 731, 732 |
| 715 | E-602 evaporator heater | hx | 734-737 |
| 716 | V-605 vacuum separator + P-604A/B melt pumps | vessel+pumps | 735, 738, 739, 740 |
| 717 | VAC-601 vacuum condenser + ejectors | package | 738, 741-745 |
| 718 | G-601 fluid-bed granulator | package | 740, 746, 22, 747 |
| 719 | C-605 dust scrubber | column | 747-750 |
| 720 | R-602 urea hydrolyser | package | 751, 752, 753 |
| 721 | C-606 NH3/CO2 desorber | column | 754-757 |
| 722 | CV-601 urea conveying to storage | package | 758-760 |

Stream 20 (surplus CO2) and 28 (area 40 condensate) are not area 70 units and are not drawn.

## Split of Rev B stream 24 (new, closure asserted at every node)
Rev B lumps all unconverted NH3 + CO2 into stream 24 (anhydrous). Here: stripper overhead O = CO2 (19) + passivation air + F_HP x 24, F_HP = 0.80 (A 0.7-0.9); decomposer gas G = (1 - F_HP) x 24, MP share 0.75 (A 0.6-0.9). R-601 feed = E-601 condensate + HP scrubber bottoms = Rev B 21 (473.9 t/h); stripper bottoms = 22 + 23 + G = 261.6 t/h; LP bottoms = 22 + 23 = 208.5 t/h = 76.9 wt % urea. Passivation air (0.5 mol % of CO2, A 0.2-1.0, a placeholder: the real rate is a licensor item) enters at K-601A and leaves in the HP scrubber vent (air in = air out).
Evaporation: melt 96 wt % (A 95-99.7) -> melt 167.9 t/h, water left in melt 6.7 t/h, evaporated 48.6 t/h (includes 7.2 t/h scrubber wash recycled). G-601: melt = granules + water + dust (asserted). Rev B stream 23 (48.1 t/h) = net clean condensate 42.4 + granulator water vapour 6.7 + desorber gas 0.25, less the ejector steam net of vent (1.2 t/h, A) (asserted).
Energy: K-601 14.8 MW (Rev B S 126 kWh/t CO2 x K); turbine steam 65 t/h at 50 bar/400 C -> 0.1 bar, eta 0.75 (A), condenser 39.6 MW. CoolProp 4-stage isentropic gives 105 kWh/t CO2 (17 % below UBA): both shown. Steam: UBA total 147.6 t/h x K-scaled; evaporator takes D = duty / hfg(4 bar); the rest split stripper 60 / MP 18 / LP 12 / hydrolyser-desorber 10 % (A). E-601 raises about 177 t/h LP steam (D, from A heat of carbamate formation 100 kJ/mol CO2, range 80-130, NOT sourced).

## Assumptions (A, ranges)
MP 18 bar (12-25), LP 4 bar (2-6), vacuum 0.3 bar abs (0.05-0.4), melt 138 C (135-145), stripper bottoms 185 C, steam headers 25 / 12 / 4 bar sat., carbamate density 1000, urea solution 1150, melt 1230 kg/m3, dense gas 300 kg/m3 (line sizing only), reactor residence 30 min, V7 vent 0.5 % of overhead (0.2-1.0), dust 0.5 % of product (0.2-1.0), scrubber liquor 10 wt % (5-20), air flow from humidity 0.05 kg/kg (0.03-0.08, lower bound), desorber feed NH3 + CO2 0.5 wt % (0.2-1.0), hydrolyser 190 C / 20 bar (170-230 C), ejector steam 1.5 t/h, vent 0.3 t/h, condensing pressure 0.1 bar, turbine eta 0.75, pump eta 0.70.

## Hazards and protection drawn
NH3 and CO2 detectors (2oo2 HH to ESD) on each sheet; ESD valves on K-601 inlet/outlet, P-601 NH3 line, C-601, E-601, C-603, C-602, C-604, E-603, E-604, R-601, G-601, R-602, C-606; PSVs with destinations (HP scrubber / MP absorber / flare); interlocks: vibration, surge, level HH, bed temperature HH, vacuum loss, defluidisation (PDAL), off-gas T high, belt misalignment, hot spot. Dust-explosion venting / isolation named but not sized (no standard read). Units without an XV by design: TG-601 (steam), E-602 (urea solution, steam heated), VAC-601 and C-605 (trace NH3 only), CV-601 (solids).

## Gaps
Heat of carbamate formation and all HP-loop conditions beyond Rev B 180 C / 150 bar (A only); water in the carbamate recycle (Rev B recycle is anhydrous, real recycle adds reactor water and lowers conversion); biuret and hydrolysis losses; scrubber and absorber efficiency / emission limits; melt freezing point and melt concentration for fluid-bed granulation; granulator air, seed recycle, product cooler (not in Rev B, stream 22 is 60 C); urea dust Kst and vent areas; vacuum system vendor data; corrosion materials (stainless / duplex / Zr: licensor); passivation air rate; MP / LP absorbers and the vent stack (not in Rev B); urea store; hydrolyser kinetics; NH3 preheater E-607 (duty 8.5 MW, D) and steam balance (E-601 LP steam 177 t/h exceeds the net UBA import, reuse not drawn); UBA process water 0.46-0.65 t/t vs 0.30 t/t in Rev B (other waste waters not in Rev B).

## Template defects found (not fixed)
1. `sheet_vessel` draws the level valve on the pump discharge; for 125-132 bar discharges (704, 711) this is an artefact. 2. `sheet_vessel` design pressure = operating + 2 bar is wrong for the vacuum vessel (716). 3. `sheet_column` diameter from 2 m/s on the ideal or dense gas gives 0.5 m for the stripper tube bundle (706); PSV/PIC are generic on atmospheric scrubber 719; trays/packing only. 4. No solids class in `St`/RULES: solids use `slurry` (conveyor and granules on 718, 722). 5. Line NPS table stops at 48 in: vacuum vapour (716, 717) and 150 t/h air lines show 61-71 m/s. 6. `sheet_package` utility rows print 0.0 for gap quantities. 7. `St.phase` 'solid' (used by Rev B) is not accepted by `vel_rule`.
Cosmetic (engine): stream label runs into PSV / valves at column tops (706, 719); LIC/LAHH bubbles overlap on columns; detector block added locally at the lower right of each sheet.

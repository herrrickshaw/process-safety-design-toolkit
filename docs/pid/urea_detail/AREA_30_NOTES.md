> **Rev C2 note:** the balance was rebased on sourced values after this file was written (see REBASE_REVC.md). Flow and duty numbers quoted below are from the earlier Rev B balance and are superseded by the registers and the sheets; assumptions and open items still apply.

# Area 30 notes: gasification, slag, syngas cooling, scrubbing, black/grey/sour water, relief, N2

Generator: `scripts/urea_area_30.py` (`build(pkg)`; `python3 scripts/urea_area_30.py [--registers DIR]` writes `/tmp/area30.html` and per-sheet previews and runs the lint). Standard library only. Basis: Rev B balance scaled K = 1.2784 to 3,850 t/d urea (see `urea_basis.py`). Screening aid, not certified design.

## Sheets (22; sheet number = area x 10 + seq, loop numbers 30x..32x)

| Sheet | Tag | Unit | Template |
|---|---|---|---|
| 301 | R-101 (+ V-131 bath) | entrained-flow slagging gasifier: membrane wall, quench zone, burners, slag bath, EDV, PSV, ESD/F&G bubbles | local drawing (head/run/finish) |
| 302 | BR-131 | burner management and start-up fuel skid (BSLL, DBB proof, purge permissive) | package |
| 303 | K-132 (+KO, AC) | quench-gas recycle compressor | compressor |
| 304 | E-131 | slag-bath water cooler | hx |
| 305 | V-102 | slag lock hopper (cycled) | vessel |
| 306 | DW-147 | slag dewatering bin and drag conveyor | package |
| 307 | E-101 | syngas cooler, HP steam raising (evaporator) | hx |
| 308 | E-132 | syngas economiser (BFW preheat) | hx |
| 309 | D-133 + P-134A/B | HP steam drum, forced circulation, BFW and blowdown lines | vessel + added lines |
| 310 | F-135 | hot-gas fine-ash candle filter | package |
| 311 | VS-136 | venturi scrubber | package |
| 312 | C-137 | scrubber column | column |
| 313 / 314 / 315 | V-139 / V-140 / V-141 (+P-141A/B) | black-water HP, LP, vacuum flash drums | vessel |
| 316 | E-142 | flash-steam condenser | hx |
| 317 | CL-143 | grey-water clarifier | package |
| 318 | FP-145 | sludge filter press | package |
| 319 | T-144 + P-144A/B | grey-water tank and HP wash/bath water pumps | tank |
| 320 | C-146 | sour-water stripper | column |
| 321 | EDV-149 | gasifier emergency depressurisation and flare tie-in | package + red EDV symbol |
| 322 | N2-150 | nitrogen purge and inerting header | package + ESD valve |

## What the numbers are (tags)

* **R-101 closure (D)**: Rev B 1+2+3 = 4 + 311 + 312, residual 0.05 % (asserted below 0.2 %). Rev B stream 5 (95.3 t/h x K, solids, 80 C) is split: 311 coarse slag to the bath, 312 fly slag leaving with the gas. Dry-solids closure 5 = slag cake 326 + press cake 349 + fly ash 313 is asserted.
* **Gas train from stream 4 (D)**: stream 4 (1400 C, 45 bar, Rev B S) is cooled stage by stage in `balance()` with duty = sum n_i [H_i(T1) - H_i(T2)] (= m cp dT with the mean cp implied by the ideal-gas enthalpy table of the HMB species; table is a frozen CoolProp 8.0.0 run, 12 Nov 2026, tag S as tool run; H2O put on the steam-table scale with HG25). Stages: 301 quench recycle (250 t/h at 190 C) mixes 4 to 302 (900 C); E-101 to 303 (341 C = Tsat(100 bar) + 30 K); E-132 to 304 (243 C, a RESULT of the BFW duty); F-135 to 309; venturi 308; C-137 outlet 305 at 181.5 C (adiabatic saturation solved by bisection with saturation y = Psat/P). 305 = 306 net (321.5 t/h to area 40) + 307 recycle. Gas dew point of 302 is 178.7 C; margin >15 K at 303/304 asserted.
* **Duties (D)**: E-101 150.8 MW, E-132 24.4 MW, membrane wall 17.8 MW (A 1.5 % of coal input 1,189 MW = CO+H2 HHV / repo cold-gas efficiency 0.6407, S), steam 368.7 t/h saturated 100 bar, bath cooler 28.1 MW, E-142 3.76 MW, K-132 1.4 MW.
* **Water network (D, all closures asserted)**: wash water 43.2 t/h (30.2 to venturi 331, 13.0 stripped water to column top 330); 15.4 t/h evaporated into the gas; black-water bleed 28.6 t/h; flash drums 6 / 1.5 / 0.3 bar a (flash fractions from enthalpy); clarifier, press, grey-water tank (make-up 351 comes out 0, stripped water covers it, 13.7 t/h exported), sour-water stripper feed = Rev B stream 28 (58.6 t/h) + flash condensate.
* Streams used from Rev B: 1, 2, 3, 4, 5 (split), 28 (feed to C-146). New ids: 301-309, 311-314, 321-328, 329-336, 341-354, 360-369, 371-374, 380-384, 385-388, 391-396, 397-399.

## Assumptions (A) with ranges

Quench mix temperature 900 C (800-950); E-101 pinch 30 K (20-50); drum 100 bar (80-120); BFW 200 C from area-70 HP heaters (150-230); economiser outlet 250 C (230-280); blowdown 2 % (1-3); circulation ratio 8 (5-15); wall loss 1.5 % of coal input (1-3); fly slag share of stream 5 30 % (15-50); candle-filter capture 97 % (95-99.5); black-water solids 3 wt % (1-5); cp of ash/char 1.1 kJ/kg/K (1.0-1.3), heat of fusion ignored (would add 5-10 %); wash water 70 C; stripped-water share at column top 30 %; K-132 rise 8 K; lock-hopper cycle 30 min (20-60), slurry 40 wt % solids (30-60), solids density 2,500 kg/m3 (2,000-2,800); cake moisture 25 wt % (15-30); bath loop 105 to 80 C; clarifier underflow 10 wt % (5-15); press cake 55 wt % (45-65); stripper overhead 3 % of feed (2-5) and steam 0.15 t/t (0.10-0.25); start-up burner 0.5 % of coal input (0.3-1), LHV 43 MJ/kg; EDV gas inventory 400 m3 (250-600), 15 min, peak = 2 x average; N2 users R-101 purge 2.0, F-135 pulse 1.2, other 0.8 t/h; N2 header 56 bar; reaction residence 3 s (2-5); dense-phase coal density 400 kg/m3 (300-450). Alarm, trip and design margins are the screening rules in `pid_unit.RULES`.

## Licensor-owned (Air Products ex-Shell at Talcher; NAME only, no data used)

Burner number and design, membrane-wall circuit and pressure drop, slag-tap and bath internals, quench geometry, ash fusion and slag chemistry, light-up/trip sequences, carbon conversion, black-water chloride/ammonia bleed, relief loads. None is invented here.

## Inconsistencies with Rev B and hand-offs (need a decision)

1. Rev B draws E-101 straight into R-201 at 350 C. A wet scrub with fine-ash removal leaves the gas at 181.5 C, saturated, so area 40 must reheat (shift feed/effluent exchange or stream 6) before R-201.
2. Stream 306 carries 15.4 t/h more steam than Rev B stream 4 (humidity 0.34 vs 0.26 mol/mol dry); stream 6 (77.8 t/h HP steam to R-201) can fall by about this much.
3. Pressure to area 40 is 41 bar (E-101 1.5, E-132 0.5, F-135 0.5, scrubber 1.0 and 0.5 bar quench-line allowance) against the Rev B A1 basis of 45 bar.
4. Rev B tag map: XV-101 = XV-30152 (O2), XV-102 = XV-30151 (coal), XV-103 = XV-30153 (steam), BDV-101 = XV-30160, PSV-101 = PSV-30101, PSV-102 = PSV-30501 (V-102). Rev B "E-101 syngas cooler / quench" is split into quench zone (301), E-101 evaporator (307) and E-132 (308).
5. Steam raised (369 t/h) greatly exceeds stream 3 (24 t/h); surplus to the area-70 steam system. BFW at 200 C and 110 bar is an area-70 assumption. N2 at 56 bar needs an N2 compressor (Rev B stream 26 is 1 bar).
6. New equipment tags in the 13x-15x band (BR-131, V-131, K-132, E-131, D-133, P-134, E-132, F-135, VS-136, C-137, V-139/140/141, P-141, E-142, CL-143, T-144, P-144, FP-145, C-146, DW-147, EDV-149, N2-150): check against other areas for collisions.

## Gaps (not sized or not sourced)

PSVs not sized (all `not sized` with the reason); dissolved H2S/NH3/HCN/CO2 in black water and flash vapour not quantified (no solubility data), so flash-vapour vent and stripper overhead composition are a gap; no sourced licensor figure; no published number was fetched for this area (the only external numbers are the CoolProp tool run above and Rev B/repo values); bath circulation pumps P-131A/B, liquid-ring vacuum package, fly-ash lock hopper and silo, KO-101/FL-101 (area 90) not drawn; venturi, candle-filter area, clarifier and press sizes need vendor/settling data; sludge and cake (V, Ni from petcoke) disposal route not defined.

## Template defects seen (not hacked around; engine owner to fix)

* sheet_column: PDI and LIC bubbles collide (same y); the unit tag/name block collides with the top-feed line when `feed2` is used; the PSV and top-line diamond overlap the line label; diameter uses overhead vapour only (C-146 shows 0.5 m, vapour traffic implies ~1.0 m, see sheet 320 notes).
* sheet_hx: hot-side service code hard-wired to "PG" (a water or slurry hot side shows PG); the PSV and its label overlap the cold-return diamond and label; the exchanger annotation overlaps the drain/vent valves; TIC dashed leader crosses the shell.
* sheet_compressor: suction line label overlaps the ESD valve label; unit name text is overlapped by PAHH/VAHH bubbles.
* sheet_package: interlock bubbles (x = 150 + 60 i, y = 600) collide with utility labels (x = 440 + 70 i) from the 6th bubble, so at most 5 are used; with 4 outlets the label of each overlaps the diamond above (50 px pitch); utility quantity printed with one decimal (0.0 for small values, kg/h or kW used instead).
* sheet_tank: tank height fixed at 20 m (grey-water tank 5 m x 20 m); vent label hard-wired "vent / BOG header", pump discharge line has no label or diamond; storage text overflows the data panel for long stream names.
* sheet_vessel: BFW/blowdown (extra) lines are added after `finish`, so they are in the line list register but not in that sheet's bottom table; mass table of the sheet shows inlet vs gas+liq only.
* Data panel: values longer than about 38 characters overflow the panel (hazard/material strings were shortened).

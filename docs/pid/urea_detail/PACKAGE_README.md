# Coal-to-urea unit-by-unit P&ID package, Rev C0 (pilot of the 200-300 sheet format)

Basis: Talcher-class nameplate, 3,850 t/d urea and 2,200 t/d NH3 (1.27 Mt/yr at 330 d). Sources: ICRA, Feb 2025 (as quoted in the coal-to-urea-design-opensource repo, docs/VALIDATION.md; grade secondary) and PIB releases of 13 Mar 2026 and 24 Jul 2026 (12.7 LMTPA; excerpt grade C). See `docs/pid/analogues/` for the full capacity shortlist.
Balance: the Rev B balance (`scripts/gen_pid_urea.py`) scaled by K = 3850 / 3011.6 = 1.2784 (linear in coal feed), then split into unit-level streams by each area file. Every unit asserts mass closure in code.
Status: CONCEPTUAL, SCREENING BASIS, NOT FOR CONSTRUCTION. Every number is tagged S (sourced), D (derived) or A (assumed screening rule or range); no licensor or vendor data is used; relief loads are not sized.

## Contents
| Area | Sheets | Content |
|---|---|---|
| 10 Coal and petcoke | 101-113 | receipt, crushing, stockyard, petcoke blend, drying/milling, lock hoppers, dense-phase feed, dust protection |
| 20 Air separation | 201-216 | air compression, purification, cold box, columns, LOX/LIN storage, O2 and N2 compression |
| 30 Gasification | 301-322 | gasifier, burners, quench, syngas cooler, scrubber, black-water flash, clarifier, sour-water stripper, EDV |
| 40 Shift | 401-415 | two-bed HT and LT shift, interstage and heat-recovery exchangers, V-203 |
| 50 AGR, sulphur, methanation | 501-526 | absorber and regenerator, refrigeration, CO2 dryer, Claus, tail-gas, methanator |
| 60 Ammonia | 601-619 | make-up and loop compressors, converter, chillers, separators, purge-gas recovery, refrigerated storage |
| 70 Urea | 701-722 | CO2 compressor, reactor, stripper, carbamate condenser, decomposers, evaporation, granulation, condensate treatment |
| 80 Utilities | 801-820 | steam, BFW, DM, cooling water, air, nitrogen, ETP/ZLD, power block |
| 90 Offsites and safety | 901-916 | flare, drains, urea store and bagging, fire protection concept, ESD hierarchy |
Total 169 sheets, 550 lines, 750 instruments, 204 equipment items, 138 relief devices, 1,058 valves, 462 streams. Registers: `registers/*.csv`, generated from the same data as the drawings.

Rebuild: `python3 scripts/gen_pid_urea_package.py docs/pid/UREA_UnitPID_RevC0.html --registers docs/pid/urea_detail/registers` (then print to PDF with headless Chrome).
Lint (0 errors, 63 advisories): no duplicate equipment, instrument, valve or line tags; every relief device has a destination; every stream number used is registered. Advisories: sheets without an ESD valve (mostly utilities and solids; area notes say where) and gas lines above 60 m/s (large air/N2 and urea off-gas lines are ducts: the pipe table stops at 48 in).

## Rev B conflicts to resolve (found by the area builders)
1. Area 30: after the wet scrub the syngas is 181.5 C and 41 bar, but Rev B sends it to R-201 at 350 C and 45 bar. Area 40 must reheat it; the Rev B stream table needs updating.
2. Area 30: stream 306 carries 15.4 t/h more steam than stream 4; stream 6 could drop by about that amount.
3. Area 20: bottom-up ASU train power is 61.7 MW (461 kWh/t O2) against Rev B 36.8 MW. Stream 26 is split (43.4 t/h HP N2 to area 10, rest vented).
4. Area 10: the mill dries coal to 2 %, so pulverised coal to the burners is 26.8 t/h lighter than stream 1.
5. Area 40: a single adiabatic bed cannot give the Rev B shift conversions; two beds per stage with interbed cooling are drawn (R-201 bed-1 exit 505 C against the 520 C screening limit).
6. Area 50: stream 11 is pure H2S in Rev B, a real acid gas carries co-stripped CO2; lean solvent keeps about 3,000 ppm H2S so 99.9 % removal is not shown; methanator feed has 3.9 mol % oxides (241 K adiabatic rise).
7. Area 60: stream 27 temperature changed to 34.7 C.
8. Area 80: steam is sized on demand only, Rev B has no steam generation balance; cooling water 16,764 t/h central (range 11,229 to 21,793).
9. Area 90: flare loads are a screening placeholder (10 % of raw syngas), not relief loads.

## Not sized or not sourced (open)
Relief loads (all PSVs), dust-explosion vent areas, limiting oxygen and CO alarm levels, fire water, foam/deluge and detector thresholds (no standard fetched), ammonia vent scrubbing and bund volume rules, raw water analysis and resin data, power route, cold-box refrigeration, carbamate heat (100 kJ/mol, assumed), black-water dissolved gases, venturi/filter/clarifier/press sizing.

## Shared-template defects still to fix (cosmetic or generic)
Bund box overprints labels (tank); relief destination hard-wired to "flare" (column, compressor, package); hot-side service hard-wired to process gas (exchanger); package sheets draw a gate valve on every line and print "0.0" utilities; vessel template forces a fail-closed ESD inlet valve; column diameter from vapour velocity only; pipe table stops at 48 in and has no solids class; label overlaps with four or more nozzles; data-panel text overflows; design pressure for vacuum service is op + 2 bar. About 100 of 169 sheets were viewed as images by the builders and 2 by me; the rest are unchecked visually.

## What a licensor-grade 200-300 sheet package adds
Vendor and licensor data (internals, catalyst volumes, nozzle schedules, equipment data sheets), P&IDs per pump/exchanger train with spares and tie-ins, instrument loop diagrams, cause-and-effect and SIL verification, relief and flare network sizing, plot plan and area classification. None of these can be generated from public data.

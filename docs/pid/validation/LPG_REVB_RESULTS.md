# LPG set Rev B results

Screening aid, not certified design. Generator `scripts/gen_pid_lpg.py`; outputs `docs/pid/LPG_PID_Set_RevB.html/.pdf` (9 sheets). No heat and material balance: storage and loss-of-containment set. Labels: S sourced, D derived, A assumed, R required by a named free source.

## (a) Items flagged by the standards map (STANDARDS_MAP.md C13, C15, section d) and the relief basis
See `LPG_REVB_RESULTS.csv`. Summary:
- C13 direct ignition: Purple Book Table 4.5 (read, PDF p.75) gives 0.2 for propane or butane below 10 kg/s (both listed 'average' reactivity). Sheet 4 now shows both bases. Same IOGP 10-50 mm class (3.25e-4 /yr): UKOOA large 1.9e-6 (propane) and 8.4e-7 (butane), UKOOA small 3.1e-6 and 8.6e-7, Cox 2.3e-5, Purple Book direct ignition 6.5e-5 /yr. The bases are not like-for-like: UKOOA and Cox are total ignition, PGS 3 direct ignition is immediate only.
- C15 full-bore rupture: 3e-7 /m/yr x 200 m = 6.0e-5 /yr (Table 3.7, PDF p.47). Jet fire 3.0e-5 /yr at P 0.5 (Table 4.5 band 10-100 kg/s; the band is A, orifice-only bound 84 kg/s propane, 37 butane), 1.2e-5 if the rate is under 10 kg/s. Purple Book leak + rupture jet fire 1.1e-4 /yr.
- Correction to STANDARDS_MAP C14: the Purple Book leak LOC is 10 % of the nominal diameter, maximum 50 mm, so 15 mm for DN150, not 10 mm.
- Sheet 6: chain 5e-7 x 0.7 x 0.7 = 2.45e-7 /yr; the other Table 3.3 values are continuous releases. 1.21 x set labelled a convention.
- Relief: Rev A's table used Z = 0.673 / 0.807 (reproduced to 1227 and 2414 mm2). The workbook and slide 10 use Z = 1.0 (API 520-I 5.6.3.2.2; calculated Z lies outside the 5.6.1 range). Rev B follows that: V3 1,496 / 2,688 mm2, orifices L / N unchanged, margin 23 % / 4 %. Real-gas flux areas 1,321 / 2,528 shown.

## (b) Not closed
- Relief cases without data: overfill, blocked inflow, vacuum, hot-day liquid expansion, trapped fill line and drain. TSV-102 not sized (heat input undefined; 4.65 bar/K and 0.0100 m3/h per kW propane given).
- Which ignition basis suits an Indian onshore site (UKOOA is offshore data): open, spread 3x to 77x.
- PFP rating, water demand duration, bund and spacing values for pressurised LPG, vent stack height, SIL targets (assumed only).

## (c) Safety items present
Relief schedule 12 rows (10 pressure items and cases, 6 of 6 items covered); ESD matrix 9 initiator rows; SIF list 4 (SIL 1 assumed, A); 3 gas detectors 2oo3 (A), flame detector, HS-101, FM-101, TSV-102; 8 HAZOP nodes; 6 inherently-safer notes. Still gaps: API 520/521/526/2000/2350/2510, NFPA 15/58, OISD-116/118/144/163, IEC 61511 and LOPA, UL 1709 / ISO 22899-1, API RP 505.
Lint: 28 tags drawn, none referenced elsewhere but undrawn; all drawn tags in the equipment list; stream diamonds vs HMB not applicable.

## (d) Verify with licensor / vendor
PSV orifice and Kd (vendor), MAWP of vessel and line classes, fireproofing test rating, valve closing times, detector coverage mapping, unloading pressure and flow, minimum and maximum ambient.

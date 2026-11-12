# Mistakes found in the earlier urea package by the PSFS linter (second pass, Rev C2)

Each was found by `scripts/psfs_lint.py` on the package as committed in 18a7de8, then fixed at its source and the package rebuilt (0 lint errors afterwards; advisories 63 -> 53).

| # | Where | Mistake | Rule | Fix |
|---|---|---|---|---|
| 1 | `urea_area_30.py`, VALVE_LIST / RELIEF_SCHEDULE | XV-30160 (the EDV, ESD-1) was registered twice: on sheet 301 as `FO` without the ESD flag, and on sheet 321 with free text in the tag field (`XV-30160 (BDV-101, symbol on sheet 301)`), which also hid it from the duplicate-tag check. The relief row carried the same free-text tag. | P01, P02, P05, P06 | one valve row (sheet 301, `FO (ESD)`), clean relief tag `XV-30160` |
| 2 | `urea_area_70.py`, R-602 hydrolyser | design pressure 22 bar g (from the 20 bar process pressure) was below its PSV set (27.5 bar g), its PAHH trip (25 bar) and the 25 bar saturated heating steam | P10 | design 27.5 bar g / 250 C from the steam side |
| 3 | `urea_area_70.py`, VAC-601 | PSV-71701 set 6.5 bar g (taken from the ejector motive steam inlet) above the assumed 3 bar g design | P10 | set 3.0 bar g (A) through a `relief_set` override in `pid_unit2.py` |
| 4 | `pid_unit2.py`, every vessel and compressor | the generic PAHH setpoint was 1.1 x operating pressure, rounded: it equalled or passed the design pressure and the PSV set. 17 of 38 PAHH trips were at or above 95 % of design, three (G-201, R-201, R-202, sheets 401/405/409) above design (50 bar vs 49.5 bar g) | P30 | trip = lower of 1.05 x operating and 0.95 x design; 20 setpoints changed, area 40 hand-set trip 50 -> 47 bar |
| 5 | `PACKAGE_README.md` | stale numbers: 190 sheets, 1,058 valves, 63 advisories | (test) | 199 sheets, 1,057 valves, 53 advisories; `test_psfs.py` now fails when they drift |
| 6 | `urea_psfs.py` (my own earlier PSFS sheets) | listed at most two relief devices, two ESD valves and four trips per unit with a "+ n more" line, cut equipment names at 40-56 characters, left out control-valve fail action and discharge interfaces; symbols collided with section headers in the first template draft | P08 and the public rule A-D | all safeguards listed in four sections, text wrapped, rows sized to their symbols |

Layout sweep (`PSFS_VARIANTS.md`): boxes 300 and 340 px wide were rejected by the linter (169 and 338 text-overflow errors); 380 px with tallest-first packing won (21 sheets, 0 errors, 0 overlaps).

Open (advisories, not drawing mistakes): 133 relief capacities not sized, 9 set pressures by vendor, the >25 % capacity-determining screen not performed on 134 units.

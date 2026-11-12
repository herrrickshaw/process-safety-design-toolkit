# How to edit a PSFS (Process Safeguarding Flow Scheme)

Sources read: EnggCyclopedia, "Process Deliverables: Relief devices / Safeguarding Memorandum" (https://enggcyclopedia.com/2012/05/safeguarding-memorandum, section 8 of the typical memorandum contents); POSC Caesar ISO 15926-4 class definition (https://posccaesar.org/ontology/15926-4/4.0/PROCESS_SAFEGUARDING_FLOW_SCHEME). Not found: the operator standard that defines PSFS symbols, layout and a review checklist (proprietary). Nothing below uses it.

## What the PSFS is
A diagram of the penultimate and ultimate safeguards against uncontrolled loss of containment (ISO 15926-4). It is a simplified view of several P&IDs and part of the Safeguarding Memorandum, which the process engineer prepares from the P&IDs; the control engineer documents the instrumented protective functions separately in the Control and Safeguarding Narratives.

## What it must show (public description)
| Section | Content | Rule |
|---|---|---|
| A Final safeguards | relief valves, rupture disks, thermal expansion valves, instrumented protective functions | pump and cooling-water thermal-expansion valves may be omitted; every other one is shown |
| B Capacity-determining components | trip, control and bypass valves and restrictions that, opened inadvertently, give relief flow above 25 % of the device capacity; the relief device capacity | each control valve shown carries spring action, stay-put device, minimum stop |
| C Mitigating systems | ESD valves with spring action; remotely operated valves installed for emergencies | |
| D Interfaces | other units, utilities, flare and relief systems | |

## How to edit one in this package
1. Do not edit the sheet. The PSFS is drawn from `RELIEF_SCHEDULE`, `VALVE_LIST`, `INSTRUMENT_INDEX` and `EQUIPMENT_LIST`, which come from the area modules (`scripts/urea_area_NN.py`, `pid_unit2.py`). Change the data at its source: a relief device is a `psv_at(...)` call, a valve a `blockv(...)` call, a trip a `bub(...)`/`interlocks` entry.
2. Rebuild and lint: `python3 scripts/psfs_lint.py` (errors exit 1). `--fix` redraws every PSFS sheet from the registers and clears all drawing-level errors; a register-level error (P04, P07, P09, P10, P14, P30) prints the area module to edit.
3. Layout: `python3 scripts/psfs_variants.py` rebuilds with box widths 300-460 and two packing orders, lints and scores each, `--apply` writes the winner into `scripts/urea_psfs.py`.
4. Add a unit by adding its sheet to the registers; the model (`scripts/psfs_model.py`) creates its box. Use `PSFS_TEMPLATE.html` as the paper form for a unit drawn by hand.
5. Run `cd tests && PYTHONPATH=../scripts:.. python3 -m unittest test_psfs` (21 tests; seeds each mistake, checks the linter finds it and the fix clears it).

## Rules checked (`scripts/psfs_lint.py`)
P01-P03 relief device, ESD valve, trip missing from its box; P04 destination blank or unrecognised; P05 tag drawn that is not a register entry of the sheet; P06 tag drawn twice; P07 control valve without fail action; P08 truncation ("+ n more"); P09 ESD valve not FC/FO; P10 relief set above the protected equipment's design pressure; P11 unit without a box; P12 text overflow, box overlap or off-page; P13 sheet title/legend; P14 duplicate relief tag; P30 high-high pressure trip above the design pressure. Advisories (open gaps, not drawing mistakes): P20 capacity not sized (133), P21 set pressure by vendor (9), P22 the >25 % capacity-determining screen not performed (one per unit with a relief device).

## Not covered
The >25 % screen itself (needs relief-case calculations), non-return valve identification, unit-to-unit connectivity, the standard's own symbols and layout.

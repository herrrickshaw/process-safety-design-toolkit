# Process-simulation tool survey for the nine conceptual HMBs

Date 2026-11-11. Scope: find free or open tools that could rebuild or check our hand-built heat and material balances, try the pip-installable ones, record results next to our numbers. Companion file: `TOOLS_SURVEY.csv` (one row per tool, same verdicts).

Environment: macOS arm64, Python 3.15 system, `uv` venvs under `/private/tmp/claude-501/venv_tools/` (`bst` = biosteam, biorefineries, thermo; `alt` = idaes-pse, cantera, pyomo, openpytea, ht, fluids, pint). `venv_val` untouched. Nothing was added to the repo toolkit; the repo stays standard-library only and these tools belong, if anywhere, in `tests/crosscheck/`.

Source grades: licence, version and release dates come from the PyPI JSON API and GitHub API / LICENSE files fetched on 2026-11-11 (grade A for those fields). Commercial tools were not researched (no vendor page read) and are listed only as "not verified".

## 1. Tool table

| Tool | Licence | Fit per process | Installed | Ran | Result vs ours | Verdict |
|---|---|---|---|---|---|---|
| BioSTEAM 2.54.0 / Thermosteam 0.54.2 (2026-09) | UIUC/NCSA (LICENSE.txt); PyPI says MIT | Ethanol, biodiesel, generic unit-op HMB, steam/power ledgers. No LNG, urea, refinery, relief | yes | yes | Section 2 | **adopt** |
| biorefineries 2.35.1 (2026-04-13) | MIT | corn dry-grind, cornstover, sugarcane, oilcane, lipidcane, biodiesel, fatty alcohols, lactic, LAOs. **No HEFA/SAF, no biogas/CBG, no fruit-veg** (checked package directory and a text search) | yes | corn after a patch; biodiesel standalone | Section 2 | **adopt** as reference models |
| thermo 0.6.1, chemicals 1.5.2, fluids 1.3.1, ht 1.2.0 | MIT | Flash and UNIFAC-Dortmund (biodiesel, ethanol columns), PR EOS (LNG), pipe/relief/exchanger helpers | yes | thermo yes; fluids, ht import only | Section 3 | **adopt** (crosscheck) |
| CoolProp 8.0.0 | MIT | LNG/NG, refrigerants, steam | yes | yes | PR within 3.3 % of CoolProp (section 3) | adopt (already used) |
| Cantera 3.2.0 (2025-11) | BSD-3 | SAF reaction heats (gas-phase NASA polynomials), urea/ammonia equilibria | yes | smoke test only | n/a | maybe |
| IDAES-PSE 2.13.0, Pyomo 6.10.1 | BSD-style / BSD-3 | Equation-oriented loops (urea/ammonia synthesis, LNG MR) in principle | yes | import only | n/a | maybe (heavy) |
| OpenPyTEA 3.2.2, pint 0.26.2 | MIT, BSD-3 | Economics only; unit audit | yes | import only | n/a | maybe |
| DWSIM 9.0.5 (2025-10-03) | GPL-3.0 | Sequential-modular GUI plus .NET/Python scripting; rigorous columns, MR LNG, refinery columns, methanol recovery | no (macOS .dmg app, not pip) | no | n/a | **maybe-adopt**: owner installs the .dmg |
| COCO/COFE, ChemSep LITE | free of charge; ChemSep LITE limited to 40 components / 300 stages | Rigorous columns | no | no | n/a | skip on macOS (platform not verified; no Wine tried) |
| OpenModelica 1.27.2, OMPython 4.1.0 | OSMC / GPL (GitHub: NOASSERTION) | Dynamic relief, depressurisation, storage | no | no | n/a | skip for now |
| pyromat 2.2.6 | GPLv3 | steam/refrigerant properties | no | no | n/a | skip (CoolProp covers it) |
| pyDWSIM | not on PyPI (404) | n/a | no | no | n/a | skip; does not exist as a package |
| Aspen, gPROMS, ProMax, UniSim, SimSci, ProSimPlus, Bryan, draw.io, ISA-5.1 sets | not read | not read | no | no | n/a | not verified; read vendor terms before any use |

## 2. BioSTEAM benchmark runs

### 2a. Corn dry-grind ethanol (`biorefineries.corn`, "conventional dry-grind")

Command: `/private/tmp/claude-501/venv_tools/bst/bin/python -I /private/tmp/claude-501/venv_tools/run_corn.py`

Attempt 1 failed on arm64/Python 3.12 with biosteam 2.54.0:
`RuntimeError: at most 1 streams expected; 2 given` in `corn/units.py:305` (`SSF.__init__` -> `BatchBioreactor`). Cause: `biorefineries` 2.35.1 SSF subclass does not declare two inlets for the newer biosteam. Attempt 2 worked with a two-line runtime patch in the runner (no package file edited): `corn.SSF._N_ins = 2; corn.SSF._ins_size_is_fixed = False`. The model then builds (operating hours 7,920/yr per its TEA) and simulates.

BioSTEAM plant: 15,000 kg/h anhydrous ethanol (19,012 L/h at 789 kg/m3; 456 KLPD), corn 46,375 kg/h at 15 % moisture. Per-litre values scaled to our 33,000 KL/yr (100 KLPD x 330 d).

| Metric | Ours | BioSTEAM | Dev % | Reading |
|---|---|---|---|---|
| Grain, kg/L anhydrous EtOH | 2.481 (81,888 t / 33,000 KL) | 2.439 | +1.7 | agrees |
| Grain, t/yr at 33,000 KL | 81,888 | 80,497 | +1.7 | agrees |
| DDGS, 10 % moisture, t/KL | 0.907 (29,924 t/yr) | 0.622 (20,520 t/yr at 33,000 KL) | +46 | confirms the ETHANOL_VALIDATION gap (+30 to +49 %) |
| DDGS dry, kg/L | 0.816 | 0.560 | +46 | same |
| LP steam (utility) kg/L | 6.33 (all thermal as steam, dryer included) | 2.78 steam plus natural gas | n/a | different scope |
| Thermal energy, MJ/L | 13.3 (steam, 6.33 kg/L x 2,100 kJ/kg) | 8.78 (5.86 steam duty + 2.92 from NG at an assumed 50 MJ/kg LHV) | +51 | ours is high; dryer fuelled by NG in BioSTEAM; ANL figure in our file is 7.7 MJ/L fuel |
| Power, kWh/L | not stated in our file | 0.085 | n/a | for later comparison |

Reading: the BioSTEAM Humbird/Bioindustrial-Park corn model independently confirms that our DDGS is about 45 % high, which supports the A "Y = 0.90" diagnosis in ETHANOL_VALIDATION. Grain per litre is right. Thermal energy 51 % above a rigorous model with heat integration is consistent with the "no heat integration, 2x US dry mill" finding. The LHV of 50 MJ/kg for natural gas is my assumption (not from a fetched table); treat 8.78 MJ/L as +/- 5 %.

### 2b. Biodiesel transesterification (`biorefineries.biodiesel.create_transesterification_and_biodiesel_separation_system`)

Command: `/private/tmp/claude-501/venv_tools/bst/bin/python -I /private/tmp/claude-501/venv_tools/run_bd.py`

Setup: oilcane chemical set (triolein as TAG), 764 kg/h oil with 0.16 % water, scaled to about 20 KLPD B100 (about 757 kg/h of product, not exactly 20 KLPD). Converged first time, no patch.

| Metric | Ours | BioSTEAM | Dev % | Reading |
|---|---|---|---|---|
| Oil / B100 | 1.0417 t/t | 1.011 t/t | +3.0 | ours higher (our FFA 2 % scheme and losses) |
| Crude glycerol / B100 | 13.7 % (137 kg/t in our file) | 13.0 % (98.2 kg/h glycerol stream, 80 % glycerol) | +5.7 | agrees; pure glycerol 10.4 % vs ours 10.1 % |
| Pure glycerol / B100 | 10.1 % | 10.4 % | -2.6 | agrees |
| Fresh methanol, kg/t B100 | 106.6 | about 108.7 inferred (see caveat) | -2 | agrees |
| Recycled methanol (D401 distillate) | not comparable | 100.2 kg/h, 99.9 % methanol | n/a | BioSTEAM recovers methanol with a distillation column, not an 80 C atmospheric flash |
| LP steam, MJ/t B100 | not stated | 778 (163.6 kW) | n/a | for comparison with our E-401/V-401 duties |
| Power, kWh/t | not stated | 19.7 | n/a | |

Caveat: the printed `methanol` feed stream is 32.04 kg/h (the construction placeholder; the biosteam MassBalance spec adjusts a copy), and system feeds minus products is -50.2 kg/h, which equals the stoichiometric methanol consumed (82.3 kg/h) minus 32.04. I therefore infer fresh methanol = 32.04 + 50.16 = 82.2 kg/h = 108.7 kg/t. This inference was not confirmed by reading the spec code; the check is that it equals 3 mol MeOH per mol triolein. Treat the 108.7 as grade B.

What it confirms: BioSTEAM closes methanol recovery with a distillation column (D401), which is the route our flash lacks.

## 3. thermo: flash test of our open biodiesel gap

Command: `/private/tmp/claude-501/venv_tools/bst/bin/python -I /private/tmp/claude-501/venv_tools/run_flash.py`

Model: methanol / glycerol / methyl oleate, UNIFAC-Dortmund (DOUFIP2016), ideal gas, thermo `FlashVL`, 80 C. Dortmund groups assigned by hand (methanol CH3OH; methyl oleate 2 CH3, 13 CH2, CH=CH, CH2COO; glycerol 2 CH2, CH, 2 OH(P), OH(S)); a wrong assignment would move numbers, so these are grade B. This is a second route to the validator result, not new evidence on real behaviour (no measured data used).

| Phase | P, bar | Methanol recovered | Residual x_MeOH in liquid |
|---|---|---|---|
| Ester phase, feed x_MeOH 0.238 | 1.013 | 14.2 % | 0.211 |
| | 0.20 | 89.5 % | 0.032 |
| | 0.10 | 95.0 % | 0.015 |
| | 0.05 | 97.5 % | 0.0076 |
| Glycerol phase, feed x_MeOH 0.30, rest glycerol (assumed composition) | 1.013 | no vapour | |
| | 0.20 | 59.0 % | 0.150 |
| | 0.05 | 90.4 % | 0.040 |

Result: ester phase 14.2 % at 1 bar matches the validator's 14.5 %, so V-401's 99.5 % claim fails by an independent run; 0.05 bar reaches 97.5 %, not 99.5 %, so even vacuum flash needs a stripper or two stages. The glycerol phase is harder still.

LNG constant-cp gap (pure methane stand-in, not our mixture), command `.../bst/bin/python -I .../run_ng.py`: 233 K to 173 K at 50 bar: CoolProp 441.6 kJ/kg, thermo PR 6,851 J/mol vs CoolProp 7,085 J/mol (PR 3.3 % low), ideal-gas constant cp x 60 K gives 2,036 J/mol, i.e. 71 % below CoolProp. This reproduces the direction and rough size of the LNG finding (-57 % with the real mixture), so a cubic EOS enthalpy integral in `thermo` is a sound replacement for the constant-cp ledger.

## 4. Gaps no tool covered

- SAF-HEFA: no HEFA/SAF module in `biorefineries` 2.35.1; reaction heat 2.3-2.9x low can be checked with Cantera or thermo group-contribution heats of formation, but nothing was run.
- Urea single-pass train, refinery 15 Mt/yr, LPG storage and relief/fire, CBG, fruit and veg: no ready model found.
- DWSIM (GPL-3.0, v9.0.5) is the likely route for rigorous columns, MR LNG and refinery crude units; not installed here because it is a macOS application, and the brief excluded installing apps.

## 5. Recommended toolchain

1. **Ethanol and biodiesel HMB**: rebuild or cross-check in BioSTEAM + `biorefineries` (corn dry-grind and biodiesel system). Keep as `tests/crosscheck/` scripts, outside the stdlib-only core. Use it to fix DDGS (Y), add heat integration, and replace the biodiesel methanol flash with a column.
2. **Property and flash checks (all processes)**: `thermo` + `chemicals` + CoolProp: replace constant-cp ledgers (LNG, SAF) with enthalpy integrals; keep `fluids`/`ht` for relief and exchanger spot checks (not benchmarked).
3. **LNG, refinery columns, urea loop**: DWSIM (owner installs .dmg) for a sequential-modular second opinion; IDAES only if an equation-oriented loop is justified.
4. **SAF/HEFA reaction heats**: Cantera or `thermo` heats of formation, hand-built balance retained.
5. **Stay hand-built**: P&ID drawing and generators, CBG, fruit and veg, LPG storage, relief/fire sizing, simple duty ledgers where a rigorous model adds no information.

## 6. Reproduction and side effects

- Installs: `uv venv --python 3.12 bst; uv pip install --python bst/bin/python biosteam biorefineries thermo` (27 s, no compilation); `alt` venv: `uv pip install idaes-pse cantera openpytea pyomo ht fluids pint` (no errors).
- Side effect to disclose: I ran `idaes get-extensions` in the `alt` venv. It is a download of solver binaries and refreshed files in the existing `~/.idaes/bin/` (outside the venv; includes `idaes-lib-darwin-aarch64.tar.gz` dated today). This was beyond the "pip into the venv only" brief; no other file outside `/private/tmp/claude-501/` and these two docs was changed. The binaries can be removed by the owner if unwanted.
- Scripts are in `/private/tmp/claude-501/venv_tools/` (`run_corn.py`, `run_bd.py`, `run_flash.py`, `run_ng.py`), not in the repo.

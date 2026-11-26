# Reference list: standards, papers and formulae that reduce the model error

Purpose: one place that ties each calculation step to the document that fixes its equation or data, whether the toolkit authors have read it, and which of the open comparison errors it addresses. Status words: **read** = the text was opened and the equation checked; **extract** = only a preview or extract was seen; **outputs only** = published results used, equations not seen; **not obtained** = paywalled or unavailable. Nothing marked "not obtained" is implemented from memory (CONTRIBUTING rule). Error percentages come from the 36-row validation sheet (`Detailed_Calculation_Breakdown.xlsx`, sheet Validation).

## A. Release rate and flash

| Step | Formula or method | Source | Status | Toolkit | Error it addresses |
|---|---|---|---|---|---|
| Flashing choked flux | omega method, eq 31 (Leung) with Cd | Leung 1986; Melhem white paper on API 520 Annex C / ISO 4126-10 | Melhem paper read; API 520 Part I and ISO 4126-10 not obtained | `twophase.py`, `flash_release.py` | tank-orifice flux (exact reproduction in tests) |
| Liquid orifice flow | q = Cd A sqrt(2 rho dP) | Yellow Book (CPR 14E) ch. 2 | read | `yb_annex.py` | over-prediction 2 to 5 times for line-fed tests until the line is modelled |
| **Line friction + flashing (HEM)** | Darcy-Weisbach, Colebrook, HEM momentum with choke where 1 + G^2 dv/dP = 0 | standard HEM pipe-flow equations; DNV DISC line-rupture description in the JFSH Validation document (section on discharge) | geometry read; HEM equations written from standard fluid mechanics, DISC itself not seen | `line_flow.py` (new) | AA 3026 +114 % to -8 %; AA 3029 now -14 %; JIVE 8051 still +516 % |
| Fittings loss coefficients K | tabulated K for valves, bends, entrance, contraction | Crane TP-410 and Perry's Handbook are the usual sources; the contraction loss in `line_flow.py` follows the form quoted in Perry and was not checked against the book | not obtained (caller must supply) | `k_fittings` input | JIVE 8051 (implied K 73 means something is missing from the rig description) |
| Flash fraction, ATEX expansion | isenthalpic flash; energy-balance expansion to atmosphere | Yellow Book 2.5.x; CCPS Guidelines for CPQRA | Yellow Book read | `atex.py`, `expansion.py` | jet velocity (match DNV 153 vs 75 m/s depends on the state used) |
| Pressure/temperature at orifice for pipe tests | upstream pressure tuned to match rate | DNV JFSH Validation, section on discharge | read | not reproduced | explains why DNV agrees with rate by construction |

## B. Droplets, rain-out

| Step | Formula | Source | Status | Error it addresses |
|---|---|---|---|---|
| Weber breakup diameter | d = We_c sigma / (rho_air u^2), C_ds 15 | Yellow Book eq 2.143b | read | droplet SMD 27 to 71 % off the EEC STEP data |
| Flashing SMD | d = 0.833e-3 - 0.0734e-3 ln Ep | CCPS RELEASE correlation as printed in DNV eq 11 | read (as printed) | range limit about Ep 8.5e4 J/kg |
| Fully-flashed SMD | about 80 micron | Witlox Phase III as cited in DNV | read (citation only) | order of magnitude only |
| Rain-out by fall and evaporation | integration of terminal velocity and d^2 law | Yellow Book 2.5.x | read | none above 10 % (rain-out is zero for hot leaks) |
| Rain-out correlations | Kletz, Lautkaski | Kletz 1977; Lautkaski 1992 via Yellow Book | read | comparison only |
| STEP measurements | SMD 30 to 49 micron at 60 mm | HSE CRR 403/2002 (archived summary) | summary read | validation data |

## C. Jet fire

| Step | Formula | Source | Status | Error it addresses |
|---|---|---|---|---|
| Flame length, tilt, frustum | Kalghatgi / Chamberlain eqs 3, 4, 15 to 28, 31 to 33, 38 | DNV Jet Fire Model Theory (Dec 2023) | read | length within 2 % of DNV |
| Two-phase source diameter | eq 58, rho_vap at Tsat(P0) | DNV theory | read | reproduces DNV lengths within 2 % (pure-vapour diameter overshot by more than 20 %) |
| Flammable mass | eq 59, m = Md min[1, 3 (1 - rain-out)] | DNV theory | read | rain-out handling |
| Cook radiant fraction, base width | eq 33 (MW form), eq 26 | DNV theory (Cook et al. 1987) | DNV text read, Cook paper not obtained | SEP and width |
| Barker model | equations | Barker, Shell | **outputs only** (RIVM Tables 5, 7) | Barker's own lengths are 21 to 50 % over measured (RIVM Table 5) |
| Cracknell model | equations | Cracknell and Carsley; Shell FRED | **outputs only** | closest to measured length; not implemented |
| Measured jet fires | AA 3026/3029, JIVE 8051 | RIVM 620550005; Bennett et al. | read | validation |
| INERIS vertical LPG fires | length vs rate | INERIS test report as supplied | read | passes within 10 % |
| Line-source radiation | point sources along axis | DNV theory | read | harm distances |
| API 521 flame models | not applicable to jets | API 521 | not obtained | relief only |

Open data that would reduce flame-length error: Cracknell/Carsley and Barker papers (full equations), Cook et al. 1987, HSE Jet fire RR 1996 series, and the unpublished flame-length observation method behind the 31.1/30.7/18.3 m figures.

## D. Pool fire, BLEVE, VCE

| Step | Formula | Source | Status |
|---|---|---|---|
| Pool burning rate, flame height, SEP | Mudan and Croce; Thomas | Yellow Book 6.5.x | read |
| BLEVE fireball | r = 3.24 m^0.325, t = 0.852 m^0.26, SEP, view factor, atmospheric transmissivity | Yellow Book 6.5.7 (worked example 6.6.5 reproduced) | read |
| BLEVE frequencies and ignition | Table 3.3, Table 4.5, P_BLEVE 0.7 | Purple Book (CPR 18E) | read |
| BLEVE test data | HSL 2-tonne propane tests | HSL | read |
| Vapour cloud explosion | multi-energy class 10, radii R0.3, R0.1 | Purple Book 4.8; Yellow Book ch. 5 | read |
| Blast and fragments | Baker curves; Yellow Book ch. 7 | Baker et al. 1983 | **not obtained**; screening only |

## E. Harm and frequency

| Step | Source | Status |
|---|---|---|
| Thermal probit, TDU 2000 | Yellow Book / Purple Book | read |
| Leak and ignition frequencies | IOGP 434-01, IOGP 434-06, UKOOA ignition curves, Cox-Lees-Ang | IOGP 434-06 table read, registration form for the full data not filled |
| Failure rates for pressure vessels | HSE failure rate data, Purple Book | HSE download timed out; Purple Book read |

## F. Relief and storage

| Step | Formula | Source | Status |
|---|---|---|---|
| Fire heat input | Q = 43,200 F A_wet^0.82 (W, A in m2) | API 521 | quoted in secondary sources; the standard itself **not obtained** |
| Vapour relief area, choked | API 520 Part I equations | API 520 | **not obtained**; limits via Melhem paper |
| Orifice letters, balanced bellows | API 526 | **not obtained** |
| Storage practice, spacing, water spray | API 2510 (2001) | **read** (supplied) |
| LPG storage rule | NFPA 58 capacity 22.11 A^0.82 CFM air | secondary source only |
| Liquid expansion, fill limits | hydraulic expansion, 85 % fill | CoolProp; ISO 4126 | partial |

## G. Dispersion hand-off

| Step | Source | Status |
|---|---|---|
| Passive Gaussian not valid for flashing LPG | DNV UDM description; Ricou-Spalding entrainment | read |
| Dense-gas screening | Britter-McQuaid | read (committed module) |
| Validated tools: Phast UDM, DEGADIS, SLAB | DNV; EPA/Havens | DEGADIS report supplied, not run |
| Experiments: Thorney Island, Burro, Maplin Sands, EEC propane jet | named in DNV submission | not obtained |

## H. Priority list to close the largest remaining errors

1. Full text of Barker and Cracknell (Shell FRED) jet models and Cook et al. 1987: flame-length and SEP bias (25 to 85 %).
2. Fittings and valve layout of the JIVE 8051 and Project AA rigs, or the original test reports: line-fed release rates.
3. API 520 Part I, API 521 and API 526 current editions, ISO 4126-10: relief sizing without secondary sources.
4. Baker blast and fragment tables (Yellow Book ch. 7): BLEVE blast and fragments.
5. A validated dense-gas dispersion run (Phast or DEGADIS) for the LFL extents.
6. HSE failure rate data, IOGP 434-06 full tables.

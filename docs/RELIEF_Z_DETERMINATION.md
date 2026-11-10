# Compressibility factor Z for fire-case vapour relief: determination from API 520 Part I

Basis: API Standard 520 Part I, *Sizing and Selection* (the owner-supplied copy, 146 pages, scanned; read by OCR and by eye on the pages cited). Clause numbers are given so the text can be checked; none of the standard's text is reproduced here. API 521 and API 526 were not read.

## What the standard says (5.6, Annex B)

| Point | Clause | Consequence for the toolkit |
|---|---|---|
| Z in the critical-flow equations (eq 2 to 7) is the compressibility of the vapour **at inlet relieving conditions** (relieving pressure P1 and relieving temperature) | 5.6.3.1, definitions after eq 7 | Z is needed at P1 and T of the saturated vapour at the relieving pressure, not at storage conditions |
| k is the **ideal-gas** specific heat ratio at the relieving temperature; real-gas k from process simulators must not be used | 5.6.2.4 | The workbooks already use the ideal-gas k (propane 1.115, n-butane 1.08) |
| The equations assume P v^k = constant; the assumption weakens near the critical locus; **Z below about 0.8 or above about 1.1 is the stated indicator** that the user must establish the limits of applicability and use Annex B | 5.6.1 | Calculated Z of saturated propane at 21.9 bar(a) is 0.673: outside the range. n-Butane at 9.4 bar(a) is 0.807: just inside |
| If a calculated Z is not available, use **Z = 1.0** | worked examples 5.6.3.2.2 (b) | Default when no valid calculated Z exists |
| For typical refinery hydrocarbons the ideal-gas treatment (ideal k, ideal specific volume with Z = 1) is adequate when Z is above 0.8 | Annex B.3.5.1 and B.3.5.2 | Z = 1 with ideal k is the method the standard blesses for the ideal-gas route |
| The general method for non-ideal vapour is direct numerical integration of the isentropic nozzle flux with an equation of state, taking the maximum flux over pressure | Annex B.1 (B.1 to B.4) | Reproduced here with CoolProp (tests/crosscheck/check_real_gas_flux.py) |

## Result for the two fluids at the workbook conditions (fire accumulation 21 %)

| | Propane (set 1,724 kPag) | n-Butane (set 690 kPag) |
|---|---|---|
| Relieving pressure P1, saturated vapour temperature | 2,187 kPa abs, 334.8 K | 936 kPa abs, 349.6 K |
| Calculated Z of the saturated vapour | **0.673** (below 0.8) | 0.807 |
| Real-gas isentropic flux (Annex B integration) | 6,225 kg/m2/s | 2,778 kg/m2/s |
| Ideal-gas flux with Z = 1.0 | 5,498: area **+13.2 %** over the real-gas area (conservative) | 2,613: area **+6.3 %** (conservative) |
| Ideal-gas flux with the calculated Z | 6,704: area **-7.1 %** (unsafe) | 2,908: area **-4.5 %** (unsafe) |
| Z that reproduces the real-gas flux | 0.780 | 0.885 |

## Decision

1. **Use Z = 1.0** in the relief workbooks and in `relief.gas_area`. It is the standard's default, it is the only option that stays on the safe side for both fluids (13 % and 6 % over-sized against the best available flux), and it is the value the HSL propane trial calculation reproduces (Roberts et al. 2003: 296 and 486 mm2 matched within 5 % with Z = 1).
2. **Do not use the calculated Z** (0.673, 0.807) in the equation: for propane it is outside the clause 5.6.1 range and under-sizes by about 7 %.
3. **Report the Annex B real-gas area alongside** (`Sizing` column R in both workbooks; `relief.gas_area_from_flux`). It is the best estimate (propane V3: 1,321 mm2 against 1,496 mm2 at Z = 1); the equivalent Z is 0.78 (propane) and 0.885 (n-butane).
4. **Orifice letters** (propane, bare): V1 G, V2 J and V3 L are unchanged from the earlier Z = 0.673 results (V3: 1,841 mm2 against 1,496 required); V4 moves from M to N and V5 from G to H. n-Butane V3 stays N.
5. The relief rate (heat input / latent heat) is unaffected; this is an area decision only.

Limits: two fluids, one relieving state each; flux integration assumes equilibrium homogeneous flow with no liquid carry-over (a two-phase relief case, API 520 5.10 and Annex C, is not covered); Kd, Kb and Kc are the workbook defaults (Kd 0.975); API 526 orifice areas are from a secondary source; API 521 environment factors, the 7.62 m wetted height and the jet-fire limits of API 521 were not read.

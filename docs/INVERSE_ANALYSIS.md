# Inverse analysis: which parameter estimates would close each large deviation

Method: for every comparison that deviates by more than 10 %, one uncertain parameter at a time is solved for (all others at baseline) so that the model hits the reference. Script: `tests/crosscheck/inverse_analysis.py` (identities in `tests/test_inverse_analysis.py`); the same numbers are on the `Inverse_Analysis` sheet of `Final_Calculation_Workbook_VertiStrat.xlsx` (generated report, not included in this repository), with the analytic ones as live formulas.

**These are fit values.** They say what would have to be true. They are not validation, they are not adopted as defaults, and a parameter is only worth changing if the required value is physically plausible and independently measurable. Plausibility is judged against a documented range, not against whether it closes the gap.

## 1. Flame length against the measured visible length (+25 %, +64 %, +85 %)

| Test | Model / measured (m) | Flammable mass multiplier needed (rain-out equivalent) | Final jet velocity needed (m/s) | Release-to-wind angle needed (deg) | Wind speed needed (m/s) |
|---|---|---|---|---|---|
| AA 3026 | 39.0 / 31.1 | 0.59 (rain-out 80 %) | 458 (baseline 153) | 65 (baseline 16) | above 30 (baseline 3.7) |
| AA 3029 | 50.3 / 30.7 | 0.32 (rain-out 89 %) | 439 (146) | 105 (9) | above 30 (2.0) |
| JIVE 8051 | 33.9 / 18.3 | 0.23 (rain-out 92 %) | 139 (46) | 157 (73; the report mentions 40) | 17.7 (0.5) |

Verdict: **no single plausible parameter closes the flame-length gap.** Velocities of 440 to 460 m/s exceed the speed of sound of the jet; the rain-out fractions would have to be 80 to 92 % of a jet that is ignited at the orifice; the angles contradict the documented 16, 9 and 73 degrees (and 40 degrees for 8051 would lengthen the flame, not shorten it); the winds are far outside the measured 0.5 to 3.7 m/s. The gap is structural: a flame model with no lift-off or buoyancy compared with a visible-flame horizontal length (RIVM; DNV's own model is +25, +63, +81 %). The one lever with a documented basis is the **definition of length**: dividing by the measured/model ratios 1.25, 1.64, 1.85 gives the "visible-flame factor" the Cook form would need.

## 2. Surface emissive power

| Comparison | Model | Reference | Radiant fraction needed (baseline) | Flame area needed (baseline) |
|---|---|---|---|---|
| AA 3026 against measured mean 331 | 268 | 331 | 0.427 (0.345) | 773 m2 (955) |
| AA 3029 against measured mean 294 | 214 | 294 | 0.479 (0.349) | 983 m2 (1,349) |
| AA 3029 against DNV Phast 192.5 | 214 | 192.5 | 0.314 (0.349) | 1,502 m2 (1,349) |
| JIVE 8051 against DNV Phast 234.9 | 259 | 234.9 | 0.438 (0.484) | 648 m2 (587) |

* Against the **measurements**, a radiant fraction of 0.43 to 0.48 (24 to 37 % above Cook's 0.345) or a flame area 19 to 27 % smaller than eq 38 would be needed. Shell's own models give lower fractions (Barker 0.26, Cracknell 0.31), so the fraction is not the lever; the area is, and it is the same cause as the flame-length excess. Verdict: explained, not fixable by a fraction.
* Against **DNV Phast** the model is 9 to 11 % high and the required correction is almost the same constant for the three tests: model / DNV = 1.09, 1.11, 1.10. Eq 38 as printed in the DNV theory document is identical to the toolkit's (checked against the printed equation), the length matches DNV to 0.3 %, 0.6 % and 2 %, and Cook's radiant fraction matches. So the missing constant sits in a quantity DNV does not print for these runs: heat of combustion (would be 42 MJ/kg against 46.0), a radiant fraction 9 to 10 % lower, or a flame area 9 to 11 % larger. Request DNV's intermediate values (area, Fs, W2) for B3026 to settle it. Verdict: **one constant factor of about 0.905, source unidentified.**

## 3. Line-fed release rate

| Test | Model / measured (kg/s) | Vessel pressure needed (baseline), bar abs | Fittings loss needed | Verdict |
|---|---|---|---|---|
| AA 3026 | 14.7 / 16.1 (-9 %) | within the 10 % margin | none | no change needed |
| AA 3029 | 15.4 / 18.0 (-14 %) | 8.08 (7.34): +10 % | none (no loss can raise the flow) | plausible only if the recorded pressure were 0.7 bar low; both propane tests fall 9 to 14 % short in the same direction, so a common cause (no slip or nucleation delay, missing vessel head) is more likely than two bad pressure records |
| JIVE 8051 | 42.3 / 6.86 (+517 %) | **1.62 (19.85)** | **K = 73** | the needed driving pressure equals the 1.62 figure DNV lists as the pressure near the orifice; if that DNV figure is bar absolute rather than barg, the effective pressure at the discharge was about 0.6 barg, which fits. K = 73 is a throttled valve (open valves 0.04 to 5) |

No friction or roughness parameter can fix the propane under-prediction (smooth pipe already; entrance K 0.5 to 0 moves it under 1 %). The flow shortfall must come from higher driving pressure or less flashing back-pressure (slip, nucleation delay), neither of which the HEM model has.

## 4. Droplet size (Weber branch, d = C_ds sigma / (u_f^2 rho_a))

| Point | Model at C_ds 15 (micron) | Measured (micron) | C_ds needed | Plausible? |
|---|---|---|---|---|
| STEP 5 bar | 56 | 44 | 11.8 | yes, inside the 10 to 20 range |
| STEP 11 bar | 20 | 30.5 | 22.9 | just above the range |

One constant cannot serve both points (the measured SMD falls less with pressure than d proportional to 1/u^2), which confirms that the Weber branch has the wrong pressure dependence for a flashing jet. A pressure-independent C_ds would need the flashing-regime correlation (equations not in hand).

## 5. DNV's post-expansion velocity (an input, not an output)

DNV's final jet velocities (152.74, 146.47, 46.22 m/s) imply, through the atmospheric-expansion momentum balance from a liquid exit state, pre-expansion pressures of **11.5, 12.1 and 3.0 bar abs**. The vessel pressures were 7.5, 7.3 and 19.9 bar abs and the HEM exit pressures 5.6, 5.2 and 1.1 bar abs. DNV varied the upstream pressure in its line-rupture model until the measured flow rate was reproduced (its own validation text), so the propane velocities contain the pressure it had to assume to make up for a flow shortfall of its discharge model: the two velocities are an artefact of that tuning, not a measurement. Our line model gives 79 and 72 m/s with a single-phase liquid exit; reproducing 152 m/s would need the exit pressure of 11.5 bar that no vessel reading supports.

## Summary of what the inverse analysis says

| Deviation | Fixable by a plausible parameter? | Best lever |
|---|---|---|
| Flame length (+25 to +85 %) | No | Definition of length; model structure (lift-off) |
| SEP against measurement (-19, -27 %) | No | Flame area, the same cause as length |
| SEP against DNV Phast (+9 to +11 %) | Yes, one constant of 0.905 | Heat of combustion, radiant fraction or area; needs DNV intermediate values |
| AA 3029 release rate (-14 %) | Marginal (+10 % vessel pressure) | Slip or nucleation delay in the line model |
| JIVE 8051 rate (+517 %) | Yes | Effective discharge pressure 1.62 bar abs (or K = 73) |
| Droplet size at STEP | Partly | C_ds 11.8 at 5 bar, 22.9 at 11 bar: no single value |
| DNV velocity (-48 to -51 % for propane) | Only by assuming DNV's tuned pressure | Not a physical parameter |

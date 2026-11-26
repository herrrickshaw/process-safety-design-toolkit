# Check of the thermodynamic property correlations (2026-11-10)

Reference: CoolProp (Helmholtz-energy equations of state, the usual reference-quality source), run in a scratch environment; reproducible with `tests/crosscheck/check_properties.py`. Toolkit side: `yb_annex.py` (Yellow Book Annex correlations), ideal-gas vapour volume in `line_flow.py`, and the cp/Lv flash estimate.

## Propane: sound
| Property | Deviation from CoolProp, 220 to 310 K | Note |
|---|---|---|
| Vapour pressure | within 0.1 % (to 0.0 %) | correlation ends at 323 K |
| Liquid density | +0.3 to +0.6 % | |
| Heat of vaporisation | -1.4 to +0.4 % | |
| Liquid cp | -1.0 to -2.1 % (-5.8 % at 330 K) | |
| Viscosity | -0.6 % to -7.8 % (-11 % at 330 K) | worsens above ~290 K |
| Surface tension | -2 to -3 % | |
| Molar mass, boiling point | 44.096 (CoolProp 44.096), 230.9 K (231.04 K) | |

## n-butane: not good enough, and not reproducible from the stated source
| Property | Deviation | Effect |
|---|---|---|
| Vapour pressure | **+19.7 % at 220 K, +10 % at 240 K, +3 to +4 % at 275 to 330 K** | JIVE 8051 and any butane leak at 5 to 40 C start with a vapour pressure 3 to 4 % high; flash and subcooling shift accordingly |
| Heat of vaporisation | -1.9 to -2.7 % | |
| Liquid cp | +0.7 % at 220 K rising to +7.4 % at 330 K | flash fraction from cp/Lv is +5.8 % high at 40.7 C |
| Viscosity | -2 to -17 % | friction factor in `line_flow` |
| Surface tension | +5 to +8 % | droplet Weber diameter |
| Density | within 0.6 % | |

The butane coefficients in `yb_annex.py` include placeholder-looking terms (vapour pressure `1e-20, 1e-20, 1e-20`; viscosity and surface-tension coefficients with the same shape as propane). The module header says all were transcribed from the Annex page, but the deviations above are larger than propane's by a factor of 30 to 100, so the butane transcription (or the Annex's own butane page) should be re-checked against the book before more butane results are relied on. This is a finding, not yet a fix: the Annex PDF page was not re-opened in this review.

## Ideal-gas assumptions
* Saturated-vapour compressibility Z: propane 0.79 at 307.5 K (12 bar), 0.88 at 278 K, 0.96 at the boiling point; butane 0.90 at 313.9 K. Ideal-gas vapour volume is therefore **+27 % (propane at 12 bar) and +12 % (butane at 4 bar) too high** in the stored state. Used in `line_flow` and in the vapour density of the omega and DNV eq 58 steps. For the Project AA line test the change is nil (flashing starts at the exit; 14.7 and 15.5 kg/s unchanged with the vapour volume scaled by 0.9), but for the omega parameter at storage temperature it is not negligible. Open: apply a real-gas Z (needs a sourced correlation, e.g. generalised Pitzer, not typed from memory).
* Flash fraction from the Annex cp and Lv to atmospheric pressure: propane 0.4404 against CoolProp 0.4480 (-1.7 %); butane 0.2738 against 0.2589 (+5.8 %).

## Not checked
Net heat of combustion (46.013 and 45.86 MJ/kg), critical temperatures, air properties, gas viscosity (not in the property set; `line_flow` uses liquid viscosity for the Reynolds number), vapour heat capacities.

## Fix applied (same day)
* New `process_safety/props_ref.py`: saturated liquid and vapour properties of propane (150 to 350 K) and n-butane (150 to 370 K) tabulated at 10 K steps from the NIST Chemistry WebBook fluid-data service (retrieved 2026-11-10, vapour density is real-gas). Against CoolProp over the table range the worst case is 0.05 to 0.5 % for vapour pressure, densities and latent heat, 0.1 to 1.5 % for heat capacity and surface tension, and 1.3 to 1.7 % for viscosity (linear interpolation between 10 K points). The NIST Antoine fits were also read for vapour pressure (n-butane A 4.35576, B 1175.581, C -2.071, 272.66 to 425 K) but the table is used instead because it also supplies the vapour side.
* The Yellow Book transcription itself was re-checked on the Annex page (annex-17 of `TNO-2005-yellow.pdf`): the toolkit coefficients match the book exactly, including the odd vapour-pressure terms (7.3, -1200, then three 1e-20 placeholders). **The source is crude, not the transcription**; the earlier suspicion of a transcription error is withdrawn.
* `lg_release` takes `property_basis: "reference"` (default stays `"yb_annex"` because the Yellow Book worked examples are its oracle); `line_flow` uses the reference set by default (`props="yb_annex"` available). With the reference set the example propane (12 bar) and butane (4 bar) leaks change by 0 to 8 % in droplet size and under 1 % in rate and flame length. For the Project AA line tests the line model moves from 14.74 and 15.46 to 14.68 and 15.39 kg/s.

## Follow-up (same day)
* `property_basis` now defaults to `auto` in `lg_release`: the NIST reference table for n-butane, the Annex correlations for propane (they agree within about 2 %). Set `yb_annex` or `reference` explicitly to override.
* Vapour viscosity added from Annex formula 7 (`yb_annex.vapour_viscosity_Pa_s`); it reproduces the Annex's printed 288.15 K values exactly and is within 1 to 4 % of CoolProp at 240 to 300 K (propane -8 % at 330 K). Used for the McAdams two-phase Reynolds number in `line_flow`.

# Validation

Run on 2026-11-06 against independent libraries and closed-form literature formulas. **186 of 186 checks are within their stated tolerance.** Reproduce with `pip install fluids thermo CoolProp scipy` then `python tests/crosscheck/validate.py` (CI job `crosscheck`); regenerate this page with `scripts/gen_validation.py`.

## What this does and does not show

* It shows the toolkit's equations and constants agree with independent implementations to the stated tolerance. The tolerance is set per check (0.1% for closed-form identities, 5% for property correlations against an equation of state, 12% where the reference is itself a range).
* It does **not** show that a result is right for a plant. Inputs, scenario selection and the standard edition a project cites are outside the check.
* References: `fluids` (API 520 gas, steam and liquid sizing, Darcy friction, separators, drag, tank geometry, valve units), `thermo` and `CoolProp` (vapour pressure, density, latent heat, real-gas isentropes, and a direct homogeneous-equilibrium integration for two-phase flow), and closed-form formulas typed from the open literature (API 521 fire heat input, Kinney-Graham, Roberts fireball, Burgess/Thomas/Mudan-Croce, IEC 60255, IEEE 80, OSHA 1910.95, Briggs dispersion coefficients, Eisenberg probit, IEC 61508-6, 49 CFR 192/193). Paywalled standards were not read; where a check uses one it is the formula as published in the open literature or in `fluids`.

## Differences to know about

* **Liquid relief area** is about 4.7% lower than `fluids.API520_A_l` for the two cases checked (within the 5% tolerance, but consistently one-sided). The cause was not resolved here (overpressure-correction or discharge-coefficient handling are the likely places). Treat the toolkit's liquid area as a screening value and confirm against the vendor's sizing.
* **Steam relief area** uses the Napier form with the older constant; `fluids` implements the 10th-edition form. They agree within the 5% tolerance for the cases checked; use the edition your project cites.
* **API 2000 fire heat input** has a boundary at exactly 0.07 barg design pressure for wetted areas of 260 m2 and above, where the published table switches formula; the toolkit follows the table as read and the cross-check avoids the boundary.
* **TNT energy** is compared with the literature range 4.184 to 4.69 MJ/kg, not a single value.
* **Two-phase omega method.** With the two-point omega (isentropic, at 90% of the inlet pressure) the choked flux is within 0.7% of a direct CoolProp integration for propane, n-butane and ammonia, and within 2.2% across all 252 rows of the bundled table (18 fluids, up to 90% of the critical pressure). The single-point saturated omega is within 4% of the direct integration below 0.3 of the critical pressure and 7% below 0.5, then degrades toward the critical point (about 13% at 0.7 Pc, up to 38% at 0.9 Pc): use the two-point basis (the default) there.
* **Depressuring minimum temperature.** The ideal-gas isentrope with the inlet-state k is 5 to 9% (10 to 20 K) colder than the real-gas isentrope for methane and nitrogen from 50 to 10 bar. The toolkit value is the lower, so it is conservative for MDMT screening; it is not the metal temperature. The check tolerance is set to 10% for that reason.
* **Lee-Kesler and Rackett** correlations (`props`) agree with the CoolProp reference EOS within 4% (observed worst case 2.1%) for the seven hydrocarbons at Tr 0.6 to 0.8; they are not for polar fluids or near the critical point.

## All checks

| # | Check | Toolkit | Reference | Difference % | Tolerance % | Reference source |
|---|---|---|---|---|---|---|
| 1 | relief.gas_area (critical) | 1071.58 mm2 | 1071.6 | -0.002 | 1 | fluids.safety_valve.API520_A_g |
| 2 | relief.gas_area (critical_hi) | 2914.32 mm2 | 2914.37 | -0.002 | 1 | fluids.safety_valve.API520_A_g |
| 3 | relief.gas_area (subcritical) | 2247.84 mm2 | 2246.57 | 0.057 | 1 | fluids.safety_valve.API520_A_g |
| 4 | relief.steam_area (set 1500 kPag) | 557.819 mm2 | 557.819 | 0.000 | 5 | fluids API520_A_steam, 10th ed. (toolkit uses Napier, 7th-ed. constant) |
| 5 | relief.steam_area (set 3000 kPag) | 1148.87 mm2 | 1148.87 | 0.000 | 5 | fluids API520_A_steam, 10th ed. (toolkit uses Napier, 7th-ed. constant) |
| 6 | relief.steam_area (set 800 kPag) | 1592.82 mm2 | 1592.82 | 0.000 | 5 | fluids API520_A_steam, 10th ed. (toolkit uses Napier, 7th-ed. constant) |
| 7 | relief.liquid_area (Q 50 m3/h, Kv~1) | 380.917 mm2 | 399.509 | -4.654 | 5 | fluids API520_A_l |
| 8 | relief.liquid_area (Q 120 m3/h, Kv~1) | 891.813 mm2 | 935.398 | -4.660 | 5 | fluids API520_A_l |
| 9 | relief.fire_heat_input_W (A=20) | 503881 W | 503881 | 0.000 | 0.1 | API 521: Q=43,200*F*A^0.82 W (adequate drainage) |
| 10 | relief.fire_heat_input_W (A=43.93) | 960612 W | 960612 | 0.000 | 0.1 | API 521: Q=43,200*F*A^0.82 W (adequate drainage) |
| 11 | relief.fire_heat_input_W (A=119) | 2.17486e+06 W | 2.17486e+06 | 0.000 | 0.1 | API 521: Q=43,200*F*A^0.82 W (adequate drainage) |
| 12 | relief.fire_heat_input_W (A=500) | 7.05731e+06 W | 7.05731e+06 | 0.000 | 0.1 | API 521: Q=43,200*F*A^0.82 W (adequate drainage) |
| 13 | hydraulics.friction_factor (Re=5000, e/D=4.6e-04) | 0.0379041  | 0.0379041 | 0.000 | 2 | fluids.friction.friction_factor (Clamond) |
| 14 | hydraulics.friction_factor (Re=100000, e/D=2.3e-04) | 0.0191473  | 0.0191473 | -0.000 | 2 | fluids.friction.friction_factor (Clamond) |
| 15 | hydraulics.friction_factor (Re=1e+06, e/D=3.0e-04) | 0.0156634  | 0.0156634 | -0.000 | 2 | fluids.friction.friction_factor (Clamond) |
| 16 | hydraulics.isothermal_gas_outlet_kpa | 990.541 kPa | 990.541 | 0.000 | 1 | fluids.compressible.isothermal_gas |
| 17 | props.vapour_pressure_bar methane 115 K | 1.30906 bar | 1.32214 | -0.989 | 5 | CoolProp (Helmholtz EOS) |
| 18 | props.liquid_density_kg_m3 methane 115 K | 416.39 kg/m3 | 417.448 | -0.253 | 5 | CoolProp (Helmholtz EOS) |
| 19 | props.vapour_pressure_bar methane 130 K | 3.67267 bar | 3.6732 | -0.014 | 5 | CoolProp (Helmholtz EOS) |
| 20 | props.liquid_density_kg_m3 methane 130 K | 392.811 kg/m3 | 394.037 | -0.311 | 5 | CoolProp (Helmholtz EOS) |
| 21 | props.vapour_pressure_bar methane 160 K | 15.9437 bar | 15.9208 | 0.144 | 5 | CoolProp (Helmholtz EOS) |
| 22 | props.liquid_density_kg_m3 methane 160 K | 335.221 kg/m3 | 336.315 | -0.325 | 5 | CoolProp (Helmholtz EOS) |
| 23 | props.vapour_pressure_bar ethane 200 K | 2.16306 bar | 2.17233 | -0.427 | 5 | CoolProp (Helmholtz EOS) |
| 24 | props.liquid_density_kg_m3 ethane 200 K | 521.124 kg/m3 | 523.977 | -0.544 | 5 | CoolProp (Helmholtz EOS) |
| 25 | props.vapour_pressure_bar ethane 240 K | 9.70896 bar | 9.66788 | 0.425 | 5 | CoolProp (Helmholtz EOS) |
| 26 | props.liquid_density_kg_m3 ethane 240 K | 462.568 kg/m3 | 465.309 | -0.589 | 5 | CoolProp (Helmholtz EOS) |
| 27 | props.vapour_pressure_bar ethane 270 K | 22.1304 bar | 22.0998 | 0.138 | 5 | CoolProp (Helmholtz EOS) |
| 28 | props.liquid_density_kg_m3 ethane 270 K | 405.646 kg/m3 | 407.718 | -0.508 | 5 | CoolProp (Helmholtz EOS) |
| 29 | props.vapour_pressure_bar ethylene 180 K | 1.80831 bar | 1.81842 | -0.556 | 5 | CoolProp (Helmholtz EOS) |
| 30 | props.liquid_density_kg_m3 ethylene 180 K | 547.707 kg/m3 | 552.198 | -0.813 | 5 | CoolProp (Helmholtz EOS) |
| 31 | props.vapour_pressure_bar ethylene 220 K | 9.5733 bar | 9.56617 | 0.075 | 5 | CoolProp (Helmholtz EOS) |
| 32 | props.liquid_density_kg_m3 ethylene 220 K | 483.463 kg/m3 | 486.669 | -0.659 | 5 | CoolProp (Helmholtz EOS) |
| 33 | props.vapour_pressure_bar ethylene 260 K | 29.9963 bar | 30.0349 | -0.128 | 5 | CoolProp (Helmholtz EOS) |
| 34 | props.liquid_density_kg_m3 ethylene 260 K | 392.518 kg/m3 | 393.467 | -0.241 | 5 | CoolProp (Helmholtz EOS) |
| 35 | props.vapour_pressure_bar propane 250 K | 2.17561 bar | 2.17964 | -0.185 | 5 | CoolProp (Helmholtz EOS) |
| 36 | props.liquid_density_kg_m3 propane 250 K | 556.82 kg/m3 | 558.337 | -0.272 | 5 | CoolProp (Helmholtz EOS) |
| 37 | props.vapour_pressure_bar propane 280 K | 5.84342 bar | 5.81686 | 0.457 | 5 | CoolProp (Helmholtz EOS) |
| 38 | props.liquid_density_kg_m3 propane 280 K | 517.372 kg/m3 | 519.175 | -0.347 | 5 | CoolProp (Helmholtz EOS) |
| 39 | props.vapour_pressure_bar propane 300 K | 10.0209 bar | 9.97683 | 0.442 | 5 | CoolProp (Helmholtz EOS) |
| 40 | props.liquid_density_kg_m3 propane 300 K | 487.51 kg/m3 | 489.447 | -0.396 | 5 | CoolProp (Helmholtz EOS) |
| 41 | props.vapour_pressure_bar propane 320 K | 16.0311 bar | 15.9886 | 0.266 | 5 | CoolProp (Helmholtz EOS) |
| 42 | props.liquid_density_kg_m3 propane 320 K | 453.082 kg/m3 | 454.936 | -0.408 | 5 | CoolProp (Helmholtz EOS) |
| 43 | props.vapour_pressure_bar propylene 250 K | 2.73555 bar | 2.7316 | 0.145 | 5 | CoolProp (Helmholtz EOS) |
| 44 | props.liquid_density_kg_m3 propylene 250 K | 575.638 kg/m3 | 578.623 | -0.516 | 5 | CoolProp (Helmholtz EOS) |
| 45 | props.vapour_pressure_bar propylene 280 K | 7.1603 bar | 7.12849 | 0.446 | 5 | CoolProp (Helmholtz EOS) |
| 46 | props.liquid_density_kg_m3 propylene 280 K | 533.409 kg/m3 | 535.802 | -0.446 | 5 | CoolProp (Helmholtz EOS) |
| 47 | props.vapour_pressure_bar propylene 300 K | 12.1226 bar | 12.0858 | 0.304 | 5 | CoolProp (Helmholtz EOS) |
| 48 | props.liquid_density_kg_m3 propylene 300 K | 501.175 kg/m3 | 503.053 | -0.373 | 5 | CoolProp (Helmholtz EOS) |
| 49 | props.vapour_pressure_bar n-butane 280 K | 1.32101 bar | 1.32817 | -0.539 | 5 | CoolProp (Helmholtz EOS) |
| 50 | props.liquid_density_kg_m3 n-butane 280 K | 594.14 kg/m3 | 593.294 | 0.143 | 5 | CoolProp (Helmholtz EOS) |
| 51 | props.vapour_pressure_bar n-butane 300 K | 2.5831 bar | 2.57596 | 0.277 | 5 | CoolProp (Helmholtz EOS) |
| 52 | props.liquid_density_kg_m3 n-butane 300 K | 571.063 kg/m3 | 570.679 | 0.067 | 5 | CoolProp (Helmholtz EOS) |
| 53 | props.vapour_pressure_bar n-butane 330 K | 5.94985 bar | 5.90446 | 0.769 | 5 | CoolProp (Helmholtz EOS) |
| 54 | props.liquid_density_kg_m3 n-butane 330 K | 533.011 kg/m3 | 533.375 | -0.068 | 5 | CoolProp (Helmholtz EOS) |
| 55 | props.vapour_pressure_bar isobutane 270 K | 1.41888 bar | 1.40169 | 1.226 | 5 | CoolProp (Helmholtz EOS) |
| 56 | props.liquid_density_kg_m3 isobutane 270 K | 585.847 kg/m3 | 584.171 | 0.287 | 5 | CoolProp (Helmholtz EOS) |
| 57 | props.vapour_pressure_bar isobutane 300 K | 3.75186 bar | 3.69996 | 1.403 | 5 | CoolProp (Helmholtz EOS) |
| 58 | props.liquid_density_kg_m3 isobutane 300 K | 549.518 kg/m3 | 548.321 | 0.218 | 5 | CoolProp (Helmholtz EOS) |
| 59 | props.vapour_pressure_bar isobutane 330 K | 8.16196 bar | 8.07609 | 1.063 | 5 | CoolProp (Helmholtz EOS) |
| 60 | props.liquid_density_kg_m3 isobutane 330 K | 508.116 kg/m3 | 507.43 | 0.135 | 5 | CoolProp (Helmholtz EOS) |
| 61 | lng methane latent heat at NBP | 510 kJ/kg | 510.828 | -0.162 | 3 | CoolProp |
| 62 | lpg propane latent heat at NBP (default 425) | 425 kJ/kg | 425.592 | -0.139 | 3 | CoolProp |
| 63 | explosion.kinney_graham_kpa W=1000 kg R=50 m | 29.2381 kPa | 29.2381 | 0.000 | 1 | Kinney-Graham (1985), as in CCPS/TNO |
| 64 | explosion.kinney_graham_kpa W=1000 kg R=100 m | 9.98536 kPa | 9.98536 | 0.000 | 1 | Kinney-Graham (1985), as in CCPS/TNO |
| 65 | explosion.kinney_graham_kpa W=5000 kg R=200 m | 8.17148 kPa | 8.17148 | -0.000 | 1 | Kinney-Graham (1985), as in CCPS/TNO |
| 66 | explosion.kinney_graham_kpa W=100 kg R=20 m | 38.7078 kPa | 38.7078 | -0.000 | 1 | Kinney-Graham (1985), as in CCPS/TNO |
| 67 | explosion TNT energy (MJ/kg) | 4.5 MJ/kg | 4.184 | 7.553 | 12 | literature range 4.184-4.69 MJ/kg |
| 68 | fireball diameter M=1000 | 58 m | 58 | 0.000 | 1 | Roberts (1982) / CCPS |
| 69 | fireball duration M=1000 | 4.5 s | 4.5 | 0.000 | 1 | Roberts (1982) / CCPS |
| 70 | fireball diameter M=20000 | 157.436 m | 157.436 | 0.000 | 1 | Roberts (1982) / CCPS |
| 71 | fireball duration M=20000 | 12.2149 s | 12.2149 | 0.000 | 1 | Roberts (1982) / CCPS |
| 72 | pool_fire burning rate (Burgess/Hottel) | 0.0766457 kg/m2/s | 0.0766457 | 0.000 | 0.1 | Burgess et al. / Mudan: m''=0.001 Hc/(Hv+cp(Tb-Ta)) |
| 73 | pool_fire Mudan-Croce SEP D=5 | 85.8574 kW/m2 | 85.8574 | 0.000 | 0.1 | Mudan & Croce (SFPE handbook) |
| 74 | pool_fire Mudan-Croce SEP D=20 | 30.8862 kW/m2 | 30.8862 | 0.000 | 0.1 | Mudan & Croce (SFPE handbook) |
| 75 | pool_fire Mudan-Croce SEP D=40 | 20.9876 kW/m2 | 20.9876 | 0.000 | 0.1 | Mudan & Croce (SFPE handbook) |
| 76 | pool_fire Thomas flame height | 31.3537 m | 31.3504 | 0.010 | 1 | Thomas (1963): H/D=42(m''/(rho_a sqrt(gD)))^0.61 |
| 77 | electrical.idmt_time_s standard_inverse | 0.680917 s | 0.680917 | 0.000 | 0.1 | IEC 60255-151 constants |
| 78 | electrical.idmt_time_s very_inverse | 0.415385 s | 0.415385 | 0.000 | 0.1 | IEC 60255-151 constants |
| 79 | electrical.idmt_time_s extremely_inverse | 0.289593 s | 0.289593 | 0.000 | 0.1 | IEC 60255-151 constants |
| 80 | electrical.idmt_time_s long_time_inverse | 3.69231 s | 3.69231 | 0.000 | 0.1 | IEC 60255-151 constants |
| 81 | electrical.tolerable_touch_V 50kg rho_s=3000 t=0.5 | 902.268 V | 902.268 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 32 |
| 82 | electrical.tolerable_step_V 50kg rho_s=3000 t=0.5 | 3116.93 V | 3116.93 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 29 |
| 83 | electrical.tolerable_touch_V 50kg rho_s=100 t=1.0 | 133.4 V | 133.4 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 32 |
| 84 | electrical.tolerable_step_V 50kg rho_s=100 t=1.0 | 185.6 V | 185.6 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 29 |
| 85 | electrical.tolerable_touch_V 50kg rho_s=2500 t=0.3 | 1005.98 V | 1005.98 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 32 |
| 86 | electrical.tolerable_step_V 50kg rho_s=2500 t=0.3 | 3388.58 V | 3388.58 | 0.000 | 0.1 | IEEE Std 80-2013 eq. 29 |
| 87 | noise.dose 90dBA/8h + 95dBA/2h | 150 % | 150 | 0.000 | 0.1 | OSHA 1910.95 App. A: 100%+50% |
| 88 | dispersion.sigmas y A x=100 | 21.8908 m | 21.8908 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 89 | dispersion.sigmas z A x=100 | 20 m | 20 | 0.000 | 2 | Briggs (1973) open-country |
| 90 | dispersion.sigmas y A x=1000 | 209.762 m | 209.762 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 91 | dispersion.sigmas z A x=1000 | 200 m | 200 | 0.000 | 2 | Briggs (1973) open-country |
| 92 | dispersion.sigmas y B x=100 | 15.9206 m | 15.9206 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 93 | dispersion.sigmas z B x=100 | 12 m | 12 | 0.000 | 2 | Briggs (1973) open-country |
| 94 | dispersion.sigmas y B x=1000 | 152.554 m | 152.554 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 95 | dispersion.sigmas z B x=1000 | 120 m | 120 | 0.000 | 2 | Briggs (1973) open-country |
| 96 | dispersion.sigmas y C x=100 | 10.9454 m | 10.9454 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 97 | dispersion.sigmas z C x=100 | 7.92118 m | 7.92118 | 0.000 | 2 | Briggs (1973) open-country |
| 98 | dispersion.sigmas y C x=1000 | 104.881 m | 104.881 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 99 | dispersion.sigmas z C x=1000 | 73.0297 m | 73.0297 | 0.000 | 2 | Briggs (1973) open-country |
| 100 | dispersion.sigmas y D x=100 | 7.9603 m | 7.9603 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 101 | dispersion.sigmas z D x=100 | 5.59503 m | 5.59503 | 0.000 | 2 | Briggs (1973) open-country |
| 102 | dispersion.sigmas y D x=1000 | 76.277 m | 76.277 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 103 | dispersion.sigmas z D x=1000 | 37.9473 m | 37.9473 | 0.000 | 2 | Briggs (1973) open-country |
| 104 | dispersion.sigmas y E x=100 | 5.97022 m | 5.97022 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 105 | dispersion.sigmas z E x=100 | 2.91262 m | 2.91262 | 0.000 | 2 | Briggs (1973) open-country |
| 106 | dispersion.sigmas y E x=1000 | 57.2078 m | 57.2078 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 107 | dispersion.sigmas z E x=1000 | 23.0769 m | 23.0769 | 0.000 | 2 | Briggs (1973) open-country |
| 108 | dispersion.sigmas y F x=100 | 3.98015 m | 3.98015 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 109 | dispersion.sigmas z F x=100 | 1.5534 m | 1.5534 | 0.000 | 2 | Briggs (1973) open-country |
| 110 | dispersion.sigmas y F x=1000 | 38.1385 m | 38.1385 | 0.000 | 2 | Briggs (1973) open-country, as tabulated in Turner/Wikipedia |
| 111 | dispersion.sigmas z F x=1000 | 12.3077 m | 12.3077 | 0.000 | 2 | Briggs (1973) open-country |
| 112 | dispersion.concentration_g_m3 centreline ground | 0.0624968 g/m3 | 0.0624968 | 0.000 | 0.1 | Gaussian plume with ground reflection (Turner) |
| 113 | consequence.probit_thermal I=10 t=30 | 1.66656  | 1.66656 | 0.000 | 0.1 | Eisenberg et al. (1975): Pr=-14.9+2.56 ln(t I^4/3 /1e4) |
| 114 | consequence.probit_thermal I=25 t=10 | 1.98171  | 1.98171 | 0.000 | 0.1 | Eisenberg et al. (1975): Pr=-14.9+2.56 ln(t I^4/3 /1e4) |
| 115 | consequence.probit_thermal I=5 t=60 | 1.07507  | 1.07507 | 0.000 | 0.1 | Eisenberg et al. (1975): Pr=-14.9+2.56 ln(t I^4/3 /1e4) |
| 116 | sil.pfd_avg 1oo1 | 0.00876  | 0.00876 | 0.000 | 0.1 | IEC 61508-6 Annex B: PFD=lambda_DU*TI/2 |
| 117 | sil.pfd_avg 1oo2 (beta=0.05) | 0.000530341  | 0.000530341 | 0.000 | 1 | IEC 61508-6 Annex B simplified 1oo2 with beta |
| 118 | sil.pfd_avg 2oo2 | 0.01752  | 0.01752 | 0.000 | 0.1 | IEC 61508-6 Annex B |
| 119 | sil.pfd_avg 2oo3 (beta=0.05) | 0.000715023  | 0.000715023 | 0.000 | 1 | IEC 61508-6 Annex B simplified 2oo3 with beta |
| 120 | pipeline.design_pressure_kpa class 1 | 13431.2 kPa | 13431.2 | 0.000 | 0.1 | 49 CFR 192.105: P=(2St/D)FET, F=0.72 |
| 121 | pipeline.potential_impact_radius_m | 222.082 m | 222.082 | 0.000 | 1 | 49 CFR 192.903: r=0.69 d sqrt(p) (ft, in, psig) |
| 122 | lng.impoundment_capacity_m3 single tank | 176000 m3 | 176000 | 0.000 | 0.1 | 49 CFR 193.2181: 110% of single-container capacity |
| 123 | psm threshold chlorine kg (1,500 lb) | 680.389 kg | 680.389 | 0.000 | 0.1 | 29 CFR 1910.119 App. A |
| 124 | fire_water.hazen_williams_bar_per_m | 0.0055625 bar/m | 0.0055625 | 0.000 | 0.1 | NFPA 13: p=6.05*Q^1.85/(C^1.85 d^4.87)*1e5 (bar/m) |
| 125 | twophase flux, two-point omega (Propane sat. liquid, 1000 kPa) | 6897.52 kg/m2/s | 6861.74 | 0.522 | 20 | CoolProp isentropic HEM, maximum of rho*sqrt(2 dh) over P |
| 126 | twophase flux, saturated omega (Propane, 1000 kPa) | 6825.61 kg/m2/s | 6861.74 | -0.527 | 5 | CoolProp isentropic HEM (single-point omega) |
| 127 | twophase flux, two-point omega (Propane sat. liquid, 1900 kPa) | 10531 kg/m2/s | 10469.6 | 0.587 | 20 | CoolProp isentropic HEM, maximum of rho*sqrt(2 dh) over P |
| 128 | twophase flux, saturated omega (Propane, 1900 kPa) | 10181.4 kg/m2/s | 10469.6 | -2.753 | 5 | CoolProp isentropic HEM (single-point omega) |
| 129 | twophase flux, two-point omega (n-Butane sat. liquid, 1000 kPa) | 6465.46 kg/m2/s | 6435.76 | 0.461 | 20 | CoolProp isentropic HEM, maximum of rho*sqrt(2 dh) over P |
| 130 | twophase flux, saturated omega (n-Butane, 1000 kPa) | 6407.91 kg/m2/s | 6435.76 | -0.433 | 5 | CoolProp isentropic HEM (single-point omega) |
| 131 | twophase flux, two-point omega (Ammonia sat. liquid, 1500 kPa) | 8793.77 kg/m2/s | 8731.99 | 0.707 | 20 | CoolProp isentropic HEM, maximum of rho*sqrt(2 dh) over P |
| 132 | twophase flux, saturated omega (Ammonia, 1500 kPa) | 8764.26 kg/m2/s | 8731.99 | 0.370 | 5 | CoolProp isentropic HEM (single-point omega) |
| 133 | props.vapour_pressure_bar methane Tr=0.6 | 1.24236 bar | 1.25551 | -1.047 | 4 | CoolProp (Helmholtz EOS) |
| 134 | props.liquid_density_kg_m3 methane Tr=0.6 | 417.383 kg/m3 | 418.433 | -0.251 | 4 | CoolProp (Helmholtz EOS) |
| 135 | props.vapour_pressure_bar methane Tr=0.7 | 4.48403 bar | 4.47914 | 0.109 | 4 | CoolProp (Helmholtz EOS) |
| 136 | props.liquid_density_kg_m3 methane Tr=0.7 | 387.122 kg/m3 | 388.379 | -0.324 | 4 | CoolProp (Helmholtz EOS) |
| 137 | props.vapour_pressure_bar methane Tr=0.8 | 11.6266 bar | 11.5982 | 0.245 | 4 | CoolProp (Helmholtz EOS) |
| 138 | props.liquid_density_kg_m3 methane Tr=0.8 | 351.649 kg/m3 | 352.9 | -0.354 | 4 | CoolProp (Helmholtz EOS) |
| 139 | props.vapour_pressure_bar ethane Tr=0.6 | 0.926262 bar | 0.940125 | -1.475 | 4 | CoolProp (Helmholtz EOS) |
| 140 | props.liquid_density_kg_m3 ethane Tr=0.6 | 542.593 kg/m3 | 545.548 | -0.542 | 4 | CoolProp (Helmholtz EOS) |
| 141 | props.vapour_pressure_bar ethane Tr=0.7 | 3.87896 bar | 3.87428 | 0.121 | 4 | CoolProp (Helmholtz EOS) |
| 142 | props.liquid_density_kg_m3 ethane Tr=0.7 | 502.429 kg/m3 | 505.254 | -0.559 | 4 | CoolProp (Helmholtz EOS) |
| 143 | props.vapour_pressure_bar ethane Tr=0.8 | 11.0463 bar | 11.0018 | 0.404 | 4 | CoolProp (Helmholtz EOS) |
| 144 | props.liquid_density_kg_m3 ethane Tr=0.8 | 455.435 kg/m3 | 458.138 | -0.590 | 4 | CoolProp (Helmholtz EOS) |
| 145 | props.vapour_pressure_bar ethylene Tr=0.6 | 1.00542 bar | 1.01476 | -0.921 | 4 | CoolProp (Helmholtz EOS) |
| 146 | props.liquid_density_kg_m3 ethylene Tr=0.6 | 562.681 kg/m3 | 567.618 | -0.870 | 4 | CoolProp (Helmholtz EOS) |
| 147 | props.vapour_pressure_bar ethylene Tr=0.7 | 4.12596 bar | 4.12944 | -0.084 | 4 | CoolProp (Helmholtz EOS) |
| 148 | props.liquid_density_kg_m3 ethylene Tr=0.7 | 521.148 kg/m3 | 525.036 | -0.741 | 4 | CoolProp (Helmholtz EOS) |
| 149 | props.vapour_pressure_bar ethylene Tr=0.8 | 11.6004 bar | 11.5949 | 0.048 | 4 | CoolProp (Helmholtz EOS) |
| 150 | props.liquid_density_kg_m3 ethylene Tr=0.8 | 472.54 kg/m3 | 475.545 | -0.632 | 4 | CoolProp (Helmholtz EOS) |
| 151 | props.vapour_pressure_bar propane Tr=0.6 | 0.653626 bar | 0.664517 | -1.639 | 4 | CoolProp (Helmholtz EOS) |
| 152 | props.liquid_density_kg_m3 propane Tr=0.6 | 589.884 kg/m3 | 591.311 | -0.241 | 4 | CoolProp (Helmholtz EOS) |
| 153 | props.vapour_pressure_bar propane Tr=0.7 | 2.99361 bar | 2.99046 | 0.105 | 4 | CoolProp (Helmholtz EOS) |
| 154 | props.liquid_density_kg_m3 propane Tr=0.7 | 545.668 kg/m3 | 547.262 | -0.291 | 4 | CoolProp (Helmholtz EOS) |
| 155 | props.vapour_pressure_bar propane Tr=0.8 | 9.02024 bar | 8.97852 | 0.465 | 4 | CoolProp (Helmholtz EOS) |
| 156 | props.liquid_density_kg_m3 propane Tr=0.8 | 493.992 kg/m3 | 495.913 | -0.387 | 4 | CoolProp (Helmholtz EOS) |
| 157 | props.vapour_pressure_bar propylene Tr=0.6 | 0.736612 bar | 0.743176 | -0.883 | 4 | CoolProp (Helmholtz EOS) |
| 158 | props.liquid_density_kg_m3 propylene Tr=0.6 | 614.351 kg/m3 | 618.153 | -0.615 | 4 | CoolProp (Helmholtz EOS) |
| 159 | props.vapour_pressure_bar propylene Tr=0.7 | 3.31717 bar | 3.30873 | 0.255 | 4 | CoolProp (Helmholtz EOS) |
| 160 | props.liquid_density_kg_m3 propylene Tr=0.7 | 568.409 kg/m3 | 571.284 | -0.503 | 4 | CoolProp (Helmholtz EOS) |
| 161 | props.vapour_pressure_bar propylene Tr=0.8 | 9.88926 bar | 9.85143 | 0.384 | 4 | CoolProp (Helmholtz EOS) |
| 162 | props.liquid_density_kg_m3 propylene Tr=0.8 | 514.706 kg/m3 | 516.818 | -0.409 | 4 | CoolProp (Helmholtz EOS) |
| 163 | props.vapour_pressure_bar n-butane Tr=0.6 | 0.482233 bar | 0.492629 | -2.110 | 4 | CoolProp (Helmholtz EOS) |
| 164 | props.liquid_density_kg_m3 n-butane Tr=0.6 | 621.019 kg/m3 | 619.753 | 0.204 | 4 | CoolProp (Helmholtz EOS) |
| 165 | props.vapour_pressure_bar n-butane Tr=0.7 | 2.39519 bar | 2.39039 | 0.201 | 4 | CoolProp (Helmholtz EOS) |
| 166 | props.liquid_density_kg_m3 n-butane Tr=0.7 | 573.935 kg/m3 | 573.491 | 0.077 | 4 | CoolProp (Helmholtz EOS) |
| 167 | props.vapour_pressure_bar n-butane Tr=0.8 | 7.59574 bar | 7.53701 | 0.779 | 4 | CoolProp (Helmholtz EOS) |
| 168 | props.liquid_density_kg_m3 n-butane Tr=0.8 | 518.965 kg/m3 | 519.56 | -0.114 | 4 | CoolProp (Helmholtz EOS) |
| 169 | props.vapour_pressure_bar isobutane Tr=0.6 | 0.507994 bar | 0.504238 | 0.745 | 4 | CoolProp (Helmholtz EOS) |
| 170 | props.liquid_density_kg_m3 isobutane Tr=0.6 | 613.645 kg/m3 | 611.793 | 0.303 | 4 | CoolProp (Helmholtz EOS) |
| 171 | props.vapour_pressure_bar isobutane Tr=0.7 | 2.42698 bar | 2.39374 | 1.389 | 4 | CoolProp (Helmholtz EOS) |
| 172 | props.liquid_density_kg_m3 isobutane Tr=0.7 | 567.374 kg/m3 | 565.924 | 0.256 | 4 | CoolProp (Helmholtz EOS) |
| 173 | props.vapour_pressure_bar isobutane Tr=0.8 | 7.51028 bar | 7.42692 | 1.122 | 4 | CoolProp (Helmholtz EOS) |
| 174 | props.liquid_density_kg_m3 isobutane Tr=0.8 | 513.326 kg/m3 | 512.592 | 0.143 | 4 | CoolProp (Helmholtz EOS) |
| 175 | depressuring.min_gas_temperature_K Methane 50->10 bar | 180.809 K | 198.256 | -8.801 | 10 | KNOWN DIFFERENCE: ideal-gas isentrope with inlet-state k is 5-9% (10-20 K) colder than the real-gas isentrope at 50 bar; conservative for MDMT |
| 176 | depressuring.min_gas_temperature_K Nitrogen 50->10 bar | 177.408 K | 187.364 | -5.314 | 10 | KNOWN DIFFERENCE: ideal-gas isentrope with inlet-state k is 5-9% (10-20 K) colder than the real-gas isentrope at 50 bar; conservative for MDMT |
| 177 | release.gas_release_kg_s Methane 20 bar 10 mm hole | 0.274546 kg/s | 0.271641 | 1.069 | 5 | CoolProp real-gas isentropic choked flux |
| 178 | release.gas_release_kg_s Nitrogen 20 bar 10 mm hole | 0.363915 kg/s | 0.362949 | 0.266 | 5 | CoolProp real-gas isentropic choked flux |
| 179 | separator.souders_brown_velocity | 0.623912 m/s | 0.623912 | 0.000 | 0.1 | fluids.separator.v_Sounders_Brown |
| 180 | separator.droplet_terminal_velocity 100 um | 0.135568 m/s | 0.131188 | 3.338 | 15 | fluids.drag.v_terminal (default drag correlation) |
| 181 | separator.droplet_terminal_velocity 300 um | 0.408699 m/s | 0.421286 | -2.988 | 15 | fluids.drag.v_terminal (default drag correlation) |
| 182 | hydraulics.incompressible_dp_kpa 100 m, 100 mm | 48.1935 kPa | 48.1935 | -0.000 | 1 | fluids.friction.one_phase_dP |
| 183 | hydraulics.cv_from_kv | 115.61  | 115.61 | 0.000 | 0.1 | fluids.control_valve.Kv_to_Cv |
| 184 | vessel_mech.liquid_inventory_m3 horizontal fill 0.25 | 3.68511 m3 | 3.68511 | 0.000 | 0.1 | fluids.geometry.TANK (plain cylinder, flat ends excluded) |
| 185 | vessel_mech.liquid_inventory_m3 horizontal fill 0.5 | 9.42478 m3 | 9.42478 | 0.000 | 0.1 | fluids.geometry.TANK (plain cylinder, flat ends excluded) |
| 186 | vessel_mech.liquid_inventory_m3 horizontal fill 0.8 | 16.1658 m3 | 16.1658 | 0.000 | 0.1 | fluids.geometry.TANK (plain cylinder, flat ends excluded) |

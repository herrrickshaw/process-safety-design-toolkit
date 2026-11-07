# MATLAB / Octave tools

Plain function files that run in **MATLAB** and in free **GNU Octave** (no toolboxes, no `arguments` blocks, no nested functions). They
port the toolkit's models so engineers who live in MATLAB can call them, script studies and plot, and they are cross-checked against
the Python models by `tests/test_matlab.py` (skipped when Octave and MATLAB are absent).

| File | What it does | Python original |
|---|---|---|
| `ps_units` | SI / US-customary conversion from exact definitions; refuses gauge to absolute; temperature readings versus differences | `process_safety/units.py` |
| `ps_gauge_to_abs`, `ps_abs_to_gauge` | add or subtract the standard atmosphere, explicitly | `units.gauge_to_abs` |
| `ps_relief_gas` | gas/vapour PSV required area, critical and subcritical orifice flux | `relief.gas_area` |
| `ps_omega_flux` | two-phase / flashing mass flux by the omega method; choked flux found by maximising G (`fminbnd`) | `twophase.mass_flux` |
| `ps_view_factor` | solid-flame view factor from a flat rectangular face to a target, vectorised midpoint rule | `viewfactor.view_factor` |
| `ps_depressure` | depressuring time, isothermal or adiabatic, numerical (`ode45` with an event) plus the choked closed form and isentropic minimum temperature | `depressuring.py` |
| `ps_egress` | RSET against an ASET you supply | `egress.py` |
| `ps_illumination` | lumen-method luminaire count and achieved lux | `illumination.py` |
| `ps_pool_fire` | pool fire: Burgess burning rate, Thomas flame height, Mudan-Croce surface emissive power, point-source flux at distances, distance to a flux target | `pool_fire.py` |
| `ps_fireball` | fireball / BLEVE radiation: diameter, duration, SEP, flux and thermal dose at distances, distance to a flux target | `fireball.py` |
| `ps_jet_fire` | jet fire: heat release, flame length 0.00326 Q^0.478, Hajek-Ludwig radiant fraction, point-source flux, safe distance for allowable levels, warnings inside 2 flame lengths | `flare.py`, `qra/effects.py` jet fire |
| `ps_blast` | TNT equivalence, Kinney-Graham overpressure, distance to an overpressure, Brode burst energy | `explosion.py` |
| `ps_bleve` | BLEVE screening: the fireball plus the blast of the vapour space at burst. The blast is a lower bound (flashing liquid and fragments are not modelled) | `fireball.py` + `explosion.py` |
| `ps_run_tests` | identity tests: unit definitions, flux continuity at the critical ratio, omega limits, Howell view factor, closed-form depressuring, scaling laws | scenario suite style |

```matlab
addpath('matlab')
r = ps_relief_gas(12000, 400, 1500*1.21+101.325, 101.325, 44, 1.13, 0.9);   % W kg/h, T K, P1 and P2 kPa abs, M, k, Z
r.area_mm2
p = ps_units(217.557, 'psig', 'kPag')                                         % 1500 kPag
t = ps_depressure(30, 5000, 1000, 300, 20, 1.3, 800, 0.85, 'adiabatic');      % V m3, P0, Pt kPa abs, T0 K, M, k, area mm2
ps_run_tests                                                                  % ALL PASSED n checks
```

From a shell: `octave-cli --eval "addpath('matlab'); ps_run_tests"`.

The fire and blast correlations (Thomas, Mudan-Croce, the Roberts-style fireball coefficients, `0.00326 Q^0.478`, Kinney-Graham) are the
toolkit's own values, which its Python docstrings mark as recalled from secondary sources: verify them against the primary papers before
design use. The identity tests prove the models are internally consistent (energy conservation, inverse-square, scaling laws, round trips)
but cannot pin a recalled constant; only the comparison with the Python models in `tests/test_matlab.py` does that, and a wrong constant
in both would pass both.

Same rules as the rest of the toolkit: every number is an input or a definition (no remembered example values), screening models with
the limits stated in each file's help text (`help ps_omega_flux`), and the Python package stays the reference implementation.

"""Compare the Yellow Book Annex property correlations (`yb_annex`) with CoolProp (optional; not a toolkit dependency).
Run: PYTHONPATH=. python3 tests/crosscheck/check_properties.py   (prints and exits 0; skips cleanly when CoolProp is absent)"""
try:
    from CoolProp.CoolProp import PropsSI as CP
except ImportError:
    print("CoolProp not installed: skipped")
    raise SystemExit(0)
from process_safety import yb_annex as y

NAMES = {"propane": "Propane", "n-butane": "n-Butane"}
QTY = (("Pv", y.vapour_pressure_Pa, lambda c, T: CP("P", "T", T, "Q", 0, c)),
       ("rho_L", y.liquid_density_kg_m3, lambda c, T: CP("Dmass", "T", T, "Q", 0, c)),
       ("Lv", y.heat_of_vaporisation_J_kg, lambda c, T: CP("Hmass", "T", T, "Q", 1, c) - CP("Hmass", "T", T, "Q", 0, c)),
       ("cp_L", y.liquid_heat_capacity_J_kgK, lambda c, T: CP("Cpmass", "T", T, "Q", 0, c)),
       ("mu_L", y.liquid_viscosity_Pa_s, lambda c, T: CP("V", "T", T, "Q", 0, c)),
       ("sigma", y.surface_tension_N_m, lambda c, T: CP("surface_tension", "T", T, "Q", 0, c)))
for fl, cn in NAMES.items():
    print(fl)
    for T in (240.0, 275.0, 290.0, 310.0):
        row = []
        for nm, f, ref in QTY:
            try:
                row.append("%s %+.1f%%" % (nm, 100 * (f(fl, T) / ref(cn, T) - 1)))
            except ValueError:
                row.append("%s out of range" % nm)
        print("  %5.0f K  " % T + "  ".join(row))

"""Generate process_safety/data/fluid_screening.json from CoolProp (dev-time only; the toolkit itself stays dependency-free).

Run:  python scripts/gen_fluid_table.py   (needs CoolProp; MIT licence, Helmholtz-energy EOS)
For each fluid and a log-spaced grid of relieving pressures up to 90% of the critical pressure, the saturated-liquid state:
temperature, liquid density, latent heat, liquid cp, omega (two-point, isentropic, and single-point saturated formula) and the
critical HEM mass flux from direct isentropic integration. Used by `fluiddata` and `twophase --fluid`.
"""
import datetime
import json
import math
import os

import CoolProp
from CoolProp.CoolProp import PropsSI

FLUIDS = {"methane": "Methane", "ethane": "Ethane", "ethylene": "Ethylene", "propane": "Propane", "propylene": "Propylene",
          "n-butane": "n-Butane", "isobutane": "IsoButane", "ammonia": "Ammonia", "water": "Water", "carbon-dioxide": "CarbonDioxide",
          "hydrogen-sulfide": "HydrogenSulfide", "methanol": "Methanol", "benzene": "Benzene", "toluene": "Toluene",
          "n-hexane": "n-Hexane", "acetone": "Acetone", "hydrogen": "Hydrogen", "n-pentane": "n-Pentane"}


def hem_flux(fl, P0, n=400):
    h0, s0 = PropsSI("H", "P", P0, "Q", 0, fl), PropsSI("S", "P", P0, "Q", 0, fl)
    best = 0.0
    for i in range(1, n):
        P = P0 * (1 - 0.9 * i / n)
        try:
            best = max(best, PropsSI("D", "P", P, "S", s0, fl) * math.sqrt(max(2 * (h0 - PropsSI("H", "P", P, "S", s0, fl)), 0.0)))
        except ValueError:
            continue
    return best


def row(fl, P):
    T = PropsSI("T", "P", P, "Q", 0, fl)
    rho = PropsSI("D", "P", P, "Q", 0, fl)
    vl, vg = 1 / rho, 1 / PropsSI("D", "P", P, "Q", 1, fl)
    hlg = PropsSI("H", "P", P, "Q", 1, fl) - PropsSI("H", "P", P, "Q", 0, fl)
    cp = PropsSI("C", "P", P, "Q", 0, fl)
    s0 = PropsSI("S", "P", P, "Q", 0, fl)
    v9 = 1 / PropsSI("D", "P", 0.9 * P, "S", s0, fl)
    w2 = 9 * (v9 / vl - 1)
    ws = cp * T * P / vl * ((vg - vl) / hlg) ** 2
    return {"P_kPa": round(P / 1e3, 3), "T_K": round(T, 3), "rho_liq_kg_m3": round(rho, 3), "h_lg_kJ_kg": round(hlg / 1e3, 3),
            "cp_liq_kJ_kgK": round(cp / 1e3, 4), "omega_two_point": round(w2, 4), "omega_saturated": round(ws, 4),
            "G_hem_kg_m2_s": round(hem_flux(fl, P), 1)}


def main():
    out = {"source": f"CoolProp {CoolProp.__version__} (MIT), Helmholtz-energy equations of state, saturated liquid",
           "generated": datetime.date.today().isoformat(),
           "note": "screening data for relief sizing and fire cases; verify against your property package and design conditions",
           "fluids": {}}
    for key, fl in FLUIDS.items():
        try:
            Tc, Pc, M = PropsSI("Tcrit", fl), PropsSI("pcrit", fl), PropsSI("M", fl) * 1000
            Tb = PropsSI("T", "P", 101325, "Q", 0, fl)
        except ValueError:
            continue
        lo = max(PropsSI("ptriple", fl) * 1.5, 1.0e5)
        hi = 0.9 * Pc
        if lo >= hi:
            continue
        grid = [lo * (hi / lo) ** (i / 13) for i in range(14)]
        rows = []
        for P in grid:
            try:
                rows.append(row(fl, P))
            except ValueError:
                continue
        if len(rows) >= 4:
            out["fluids"][key] = {"coolprop_name": fl, "M_kg_kmol": round(M, 4), "Tc_K": round(Tc, 3), "Pc_kPa": round(Pc / 1e3, 2),
                                  "Tb_K": round(Tb, 3), "rows": rows}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "fluid_screening.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", len(out["fluids"]), "fluids,", sum(len(f["rows"]) for f in out["fluids"].values()), "rows")


if __name__ == "__main__":
    main()

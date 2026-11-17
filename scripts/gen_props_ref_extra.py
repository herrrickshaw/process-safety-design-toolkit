"""Generate process_safety/data/props_ref_extra.json: saturation-property tables for further liquefied gases, in the layout of `props_ref._TABLE`.

Source: CoolProp (MIT licence, https://github.com/CoolProp/CoolProp) high-accuracy equations of state with CoolProp's transport and surface-tension
correlations, run with CoolProp.CoolProp.PropsSI. CoolProp is NOT a runtime dependency: only this script needs it, the toolkit reads the JSON.
Rows at the cold end where CoolProp cannot return a property (propylene vapour viscosity below about 170 K) are left out.
Fluids: isobutane, propylene, ammonia, ethane. 10 K steps; range from the first multiple of 10 K at or above the triple point + 5 K to the last multiple of
10 K at or below Tc - 10 K. Each row: T, P, rho_l, rho_v, h_l, h_v, cp_l, mu_l, sigma, mu_v. No heat of combustion is generated: CoolProp does not hold one,
and the toolkit takes it from the caller (`fire.Hc_J_kg`) rather than a remembered value.
Run: <venv with CoolProp>/bin/python scripts/gen_props_ref_extra.py
"""
import json
import math
import os

import CoolProp
from CoolProp.CoolProp import PropsSI

FLUIDS = {"isobutane": "IsoButane", "propylene": "Propylene", "ammonia": "Ammonia", "ethane": "Ethane"}
OUT = os.path.join(os.path.dirname(__file__), "..", "process_safety", "data", "props_ref_extra.json")


def main():
    out = {"_source": "CoolProp %s (MIT) via scripts/gen_props_ref_extra.py" % CoolProp.__version__, "_columns": "T,P,rho_l,rho_v,h_l,h_v,cp_l,mu_l,sigma,mu_v", "fluids": {}}
    for name, cp in FLUIDS.items():
        Tt, Tc = PropsSI("Ttriple", cp), PropsSI("Tcrit", cp)
        T0 = math.ceil((Tt + 5.0) / 10.0) * 10.0
        T1 = math.floor((Tc - 10.0) / 10.0) * 10.0
        rows, T = [], T0
        while T <= T1 + 1e-9:
            g = lambda k, q: PropsSI(k, "T", T, "Q", q, cp)
            try:
                rows.append([T, g("P", 0), g("D", 0), g("D", 1), g("H", 0), g("H", 1), g("C", 0), g("V", 0), g("I", 0), g("V", 1)])
            except ValueError:
                rows.append(None)
            T += 10.0
        last_bad = max([i for i, r in enumerate(rows) if r is None], default=-1)
        if last_bad >= len(rows) // 2:
            raise RuntimeError("%s: CoolProp fails in the upper half of the range" % name)
        rows = rows[last_bad + 1:]
        out["fluids"][name] = {"M_kg_mol": PropsSI("M", cp), "Tc_K": Tc, "rows": [[float("%.6g" % v) for v in r] for r in rows]}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=0)
    print({k: len(v["rows"]) for k, v in out["fluids"].items()})


if __name__ == "__main__":
    main()

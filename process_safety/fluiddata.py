"""Saturated-liquid screening data for common process fluids, generated from CoolProp (see scripts/gen_fluid_table.py).

The toolkit stays dependency-free: the table ships as JSON (`data/fluid_screening.json`, 18 fluids, 14 pressures each, from about
100 kPa to 90% of the critical pressure). Values between grid pressures are interpolated linearly in ln(P). Outside the grid the
functions raise ValueError rather than extrapolate. Use for first-pass relief and fire-case work, and replace with your property
package for design: mixtures, impurities, and states away from saturated liquid are not covered.
"""
from __future__ import annotations

import bisect
import json
import math
import os

_PATH = os.path.join(os.path.dirname(__file__), "data", "fluid_screening.json")
_CACHE: dict | None = None
FIELDS = ("T_K", "rho_liq_kg_m3", "h_lg_kJ_kg", "cp_liq_kJ_kgK", "omega_two_point", "omega_saturated", "G_hem_kg_m2_s")


def _data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def names() -> list[str]:
    return sorted(_data()["fluids"])


def source() -> str:
    d = _data()
    return f"{d['source']}, generated {d['generated']}"


def fluid_constants(fluid: str) -> dict:
    f = _fluid(fluid)
    return {k: f[k] for k in ("coolprop_name", "M_kg_kmol", "Tc_K", "Pc_kPa", "Tb_K")}


def _fluid(fluid: str) -> dict:
    try:
        return _data()["fluids"][fluid.lower()]
    except KeyError:
        raise ValueError(f"unknown fluid {fluid!r}; available: {', '.join(names())}") from None


def at_pressure(fluid: str, P_kPa: float) -> dict:
    """Saturated-liquid properties at an absolute pressure (kPa), interpolated in ln P between grid rows."""
    rows = _fluid(fluid)["rows"]
    ps = [r["P_kPa"] for r in rows]
    if not ps[0] <= P_kPa <= ps[-1]:
        raise ValueError(f"{fluid}: {P_kPa:g} kPa abs is outside the table range {ps[0]:g} to {ps[-1]:g} kPa")
    i = min(max(bisect.bisect_right(ps, P_kPa) - 1, 0), len(rows) - 2)
    a, b = rows[i], rows[i + 1]
    t = (math.log(P_kPa) - math.log(a["P_kPa"])) / (math.log(b["P_kPa"]) - math.log(a["P_kPa"]))
    out = {k: a[k] + t * (b[k] - a[k]) for k in FIELDS}
    out["P_kPa"] = P_kPa
    return out

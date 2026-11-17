"""Pure-component property estimates for light hydrocarbons and cryogens: Lee-Kesler vapour pressure and Rackett liquid density.

Both are standard open-literature correlations from critical constants (Tc, Pc, acentric factor omega), so no data files are needed:
    ln Pr = f0 + omega f1, f0 = 5.92714 - 6.09648/Tr - 1.28862 ln Tr + 0.169347 Tr^6,
                          f1 = 15.2518 - 15.6875/Tr - 13.4721 ln Tr + 0.43577 Tr^6        (Lee-Kesler)
    V_sat = (R Tc/Pc) Zra^(1 + (1 - Tr)^(2/7)), Zra = 0.29056 - 0.08775 omega                (Rackett)
Accuracy: a few percent for non-polar hydrocarbons (checked in tests against well-known values: propane ~10 bar at 300 K,
normal boiling points reproducing 1.013 bar, methane liquid ~422 kg/m3 at 111.7 K). NOT for polar/associating fluids (ammonia, water,
alcohols, HF), mixtures, or near the critical point. Critical constants are recalled from standard tables: verify for your design basis.
"""
from __future__ import annotations

import math

from .constants import R

# Tc [K], Pc [bar], omega, M [kg/kmol], normal boiling point [K] (recalled standard values)
COMPONENTS = {
    "methane": (190.56, 45.99, 0.011, 16.043, 111.66),
    "ethane": (305.32, 48.72, 0.099, 30.070, 184.55),
    "ethylene": (282.34, 50.41, 0.087, 28.054, 169.42),
    "propane": (369.83, 42.48, 0.152, 44.097, 231.04),
    "propylene": (364.90, 46.00, 0.142, 42.081, 225.43),
    "n-butane": (425.12, 37.96, 0.200, 58.123, 272.65),
    "isobutane": (408.10, 36.48, 0.177, 58.123, 261.40),
}


def vapour_pressure_bar(component: str, T_K: float) -> float:
    Tc, Pc, w, _, _ = COMPONENTS[component]
    Tr = T_K / Tc
    f0 = 5.92714 - 6.09648 / Tr - 1.28862 * math.log(Tr) + 0.169347 * Tr ** 6
    f1 = 15.2518 - 15.6875 / Tr - 13.4721 * math.log(Tr) + 0.43577 * Tr ** 6
    return Pc * math.exp(f0 + w * f1)


def saturation_temperature_K(component: str, P_bar: float) -> float:
    lo, hi = 0.35 * COMPONENTS[component][0], 0.999 * COMPONENTS[component][0]
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if vapour_pressure_bar(component, mid) < P_bar else (lo, mid)
    return (lo + hi) / 2


def liquid_density_kg_m3(component: str, T_K: float) -> float:
    Tc, Pc, w, M, _ = COMPONENTS[component]
    Tr = T_K / Tc
    Zra = 0.29056 - 0.08775 * w
    V = R * Tc / (Pc * 1e5) * Zra ** (1 + (1 - Tr) ** (2 / 7))
    return M / 1000 / V

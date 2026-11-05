"""Pool-fire screening: burning rate (Burgess/Zabetakis), flame height (Thomas, no wind), point-source radiation, Mudan-Croce SEP.

Point-source radiation is conservative-to-fair at > ~2-3 pool diameters and unreliable near the pool; wind tilt, flame drag and
smoke obscuration are not modelled. Radiant fraction and transmissivity are inputs. Correlation constants are recalled from the
open literature (CCPS/Mudan-Croce/Thomas): verify before use. Spreading of unbunded spills is not modelled: give the pool area.
"""
from __future__ import annotations

import math

from .constants import G
RHO_AIR = 1.2


def burning_rate_kg_m2_s(Hc_kJ_kg: float, Hv_kJ_kg: float, cp_kJ_kgK: float, Tb_K: float, Ta_K: float = 298.15) -> float:
    """Burgess: m'' = 0.001 Hc / [Hv + cp (Tb - Ta)] (sensible term dropped when Tb < Ta, i.e. cryogenic pools)."""
    return 0.001 * Hc_kJ_kg / (Hv_kJ_kg + cp_kJ_kgK * max(Tb_K - Ta_K, 0.0))


def pool_diameter_m(area_m2: float) -> float:
    return math.sqrt(4 * area_m2 / math.pi)


def flame_height_m(D_m: float, m_dot_kg_m2_s: float) -> float:
    """Thomas (no wind): H/D = 42 (m''/(rho_a sqrt(g D)))^0.61."""
    return D_m * 42 * (m_dot_kg_m2_s / (RHO_AIR * math.sqrt(G * D_m))) ** 0.61


def mudan_croce_sep_kW_m2(D_m: float) -> float:
    """Average surface emissive power: 140 exp(-0.12 D) + 20 (1 - exp(-0.12 D)) (hydrocarbon pools; soot shielding grows with D)."""
    e = math.exp(-0.12 * D_m)
    return 140 * e + 20 * (1 - e)


def pool_fire(area_m2, Hc_kJ_kg, Hv_kJ_kg, cp_kJ_kgK, Tb_K, Ta_K=298.15, radiant_fraction=0.25, tau=1.0) -> dict:
    D = pool_diameter_m(area_m2)
    m = burning_rate_kg_m2_s(Hc_kJ_kg, Hv_kJ_kg, cp_kJ_kgK, Tb_K, Ta_K)
    H = flame_height_m(D, m)
    Q_kW = m * area_m2 * Hc_kJ_kg
    return {"diameter_m": D, "burning_rate_kg_m2_s": m, "mass_burn_rate_kg_s": m * area_m2, "flame_height_m": H,
            "heat_release_MW": Q_kW / 1e3, "sep_mudan_croce_kW_m2": mudan_croce_sep_kW_m2(D),
            "radiant_fraction": radiant_fraction, "tau": tau, "Q_kW": Q_kW}


def incident_kW_m2(pf: dict, ground_distance_m: float) -> float:
    """Point source at mid-flame height above the pool centre; incident flux on a surface facing it (cosine factor ignored = conservative)."""
    r = math.hypot(ground_distance_m, pf["flame_height_m"] / 2)
    return pf["tau"] * pf["radiant_fraction"] * pf["Q_kW"] / (4 * math.pi * r * r)


def distance_to_flux_m(pf: dict, target_kW_m2: float) -> float:
    lo, hi = 0.0, 1e4
    if incident_kW_m2(pf, 0.0) < target_kW_m2:
        return 0.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if incident_kW_m2(pf, mid) > target_kW_m2 else (lo, mid)
    return (lo + hi) / 2

"""Flare radiation and tip sizing (API 521 point-source method, Hajek & Ludwig radiant fraction).

Point-source model: K = tau * F * Q / (4 pi D^2), D measured from the flame centre. It is least accurate close to the flame
(search-sourced guidance: point of interest >= ~2-3 flame lengths away); `radiation_checks` returns that warning. Wind tilt is
handled by letting the caller supply the flame-centre coordinates. Verify allowable levels against your API 521 edition.
"""
from __future__ import annotations

import math

R = 8.314462618

# kW/m2 -> exposure class (API 521 table, solar radiation excluded/included varies by edition - verify)
ALLOWABLE_KW_M2 = {
    1.58: "continuous exposure",
    4.73: "emergency actions up to several minutes, no shielding",
    6.31: "emergency actions up to ~1 min, with shielding",
    9.46: "escape only, a few seconds",
}


def radiant_fraction(mw: float) -> float:
    """Hajek & Ludwig: F = 0.048 sqrt(MW), capped at 0.40 (gives ~0.19 methane, ~0.32 propane)."""
    return min(0.40, 0.048 * math.sqrt(mw))


def heat_release_W(mass_kg_s: float, lhv_MJ_kg: float) -> float:
    return mass_kg_s * lhv_MJ_kg * 1e6


def radiation_kW_m2(Q_W: float, distance_m: float, F: float, tau: float = 1.0) -> float:
    """Incident radiation at `distance_m` from the flame centre. tau=1 is conservative."""
    return tau * F * Q_W / (4 * math.pi * distance_m ** 2) / 1e3


def safe_distance_m(Q_W: float, allowable_kW_m2: float, F: float, tau: float = 1.0) -> float:
    return math.sqrt(tau * F * Q_W / (4 * math.pi * allowable_kW_m2 * 1e3))


def radiation_checks(Q_W, F, flame_length_m=None, tau=1.0) -> dict:
    """Safe distance (from flame centre) for each allowable level, plus point-source validity warnings."""
    out = {"distance_m": {f"{k} kW/m2 ({v})": round(safe_distance_m(Q_W, k, F, tau), 1) for k, v in ALLOWABLE_KW_M2.items()},
           "warnings": []}
    if flame_length_m:
        d_min = 2 * flame_length_m
        for label, d in out["distance_m"].items():
            if d < d_min:
                out["warnings"].append(f"{label}: {d} m is < 2 flame lengths ({d_min:.0f} m) - point-source result unreliable; use a distributed-source model")
    return out


def flame_centre_distance(horizontal_m: float, receptor_height_m: float, flame_centre_height_m: float) -> float:
    return math.hypot(horizontal_m, flame_centre_height_m - receptor_height_m)


def tip_diameter_m(mass_kg_s: float, mw: float, T_K: float, k: float, mach: float) -> float:
    """Flare tip diameter for a target Mach number at the tip (isentropic sonic speed c = sqrt(kRT/M)).
    Common practice (API 521): ~0.5 Mach at maximum relief, much lower for continuous smokeless flow - verify."""
    c = math.sqrt(k * R * T_K / (mw / 1000))
    # tip static pressure ~ atmospheric; ideal gas density at tip
    rho = 101_325 * (mw / 1000) / (R * T_K)
    v = mach * c
    return math.sqrt(4 * mass_kg_s / (math.pi * rho * v))

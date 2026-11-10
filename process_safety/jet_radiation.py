"""Incident thermal radiation field around a vertical vapour jet flame (multi-point line source along the Chamberlain flame axis).

Geometry (from `jet_flame.chamberlain`, DNV Theory - Jet Fire, eq. (20)-(23)): the release point O is at height z_rel above ground; the
centre of the flame base is at distance B from O along the hole axis (vertical here); the flame axis leaves the base at angle alpha from the hole
axis toward the downwind (+x) direction and has length R_L, so the tip is at distance L_B from O (law of cosines, eq. 23).

Radiation: the radiated power Q = F_s m Hc (`radiated_power_kW` of the flame result) is shared equally by N point sources placed at the
mid-points of N equal segments of the flame axis. The flux at a target is  q = tau * sum_i (Q/N) / (4 pi r_i^2),  with the target taken to
face every source (conservative). Checks in the tests: the source powers add up to Q; far from the flame q tends to tau Q /(4 pi r^2); the
field is symmetric in the crosswind direction; the result converges as N grows.

Limits: vertical release only (other release angles need the horizontal-release correlations that `jet_flame` does not implement); wind in the
plane x-z; no ground impingement; no flame-body shielding or atmospheric attenuation beyond the constant tau you pass; a point-source model is
not reliable inside about one flame width of the flame, so the result flags that zone. Screening aid, not certified design.
"""
from __future__ import annotations

import math


def source_points(flame: dict, release_height_m: float, n: int = 60) -> list[tuple[float, float, float]]:
    """Point-source positions (x downwind, y crosswind, z up) along the flame axis of a `chamberlain` result for a vertical release."""
    if n < 1 or release_height_m < 0:
        raise ValueError("n must be at least 1 and the release height must not be negative")
    a = math.radians(flame["alpha_deg"])
    zb = release_height_m + flame["B_m"]
    L = flame["R_L_m"]
    return [(math.sin(a) * L * (i + 0.5) / n, 0.0, zb + math.cos(a) * L * (i + 0.5) / n) for i in range(n)]


def flux_kW_m2(flame: dict, release_height_m: float, x_m: float, y_m: float, z_m: float = 1.5, tau: float = 1.0, n: int = 60) -> float:
    """Incident flux (kW/m2) at (x, y, z) from the line-source model; tau is the atmospheric transmissivity (0, 1]."""
    if not 0 < tau <= 1:
        raise ValueError("tau must be in (0, 1]")
    q = flame["radiated_power_kW"] / n
    total = 0.0
    for px, py, pz in source_points(flame, release_height_m, n):
        r2 = (x_m - px) ** 2 + (y_m - py) ** 2 + (z_m - pz) ** 2
        if r2 < 1e-6:
            raise ValueError("target coincides with a source point")
        total += q / (4.0 * math.pi * r2)
    return tau * total


def reach_m(flame: dict, release_height_m: float, threshold_kW_m2: float, direction: str, z_m: float = 1.5, tau: float = 1.0, n: int = 60,
            s_max_m: float = 2000.0) -> float:
    """Distance from the release point along the ground to the first point where the flux falls to `threshold` (bisection from 0.5 m outward).

    direction: 'downwind' (+x), 'upwind' (-x) or 'crosswind' (+y). Returns 0.0 if the flux is already below the threshold at 0.5 m."""
    if threshold_kW_m2 <= 0:
        raise ValueError("threshold must be positive")
    if direction not in ("downwind", "upwind", "crosswind"):
        raise ValueError("direction must be downwind, upwind or crosswind")

    def f(s):
        x, y = (s, 0.0) if direction == "downwind" else (-s, 0.0) if direction == "upwind" else (0.0, s)
        return flux_kW_m2(flame, release_height_m, x, y, z_m, tau, n)

    lo, hi = 0.5, s_max_m
    if f(lo) < threshold_kW_m2:
        return 0.0
    if f(hi) > threshold_kW_m2:
        raise ValueError("flux still above the threshold at s_max")
    for _ in range(100):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > threshold_kW_m2 else (lo, mid)
    return 0.5 * (lo + hi)


def near_field_radius_m(flame: dict) -> float:
    """Screening convention (not a sourced limit): inside one tip width W2 of the flame axis the point-source sum should not be trusted."""
    return flame["W2_m"]

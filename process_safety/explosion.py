"""Vapour-cloud / vessel-burst blast screening: TNT equivalence, Kinney-Graham free-air overpressure, Brode burst energy.

TNT-equivalency yield for a VCE is highly uncertain (commonly a few percent of the combustion energy); multi-energy / Baker-Strehlow
methods are better for confined/congested clouds and are NOT implemented. Kinney-Graham coefficients are recalled from the open
literature. Damage criteria are not tabulated here: pass the overpressure your acceptance criteria use.
"""
from __future__ import annotations

import math

TNT_MJ_PER_KG = 4.5  # heat of detonation, MJ/kg; sources quote ~4.1-4.68, choose per your basis


def tnt_equivalent_kg(fuel_kg, heat_of_combustion_MJ_kg, yield_fraction=0.05, tnt_MJ_kg=TNT_MJ_PER_KG) -> float:
    return yield_fraction * fuel_kg * heat_of_combustion_MJ_kg / tnt_MJ_kg


def scaled_distance(R_m, W_tnt_kg) -> float:
    return R_m / W_tnt_kg ** (1 / 3)


def kinney_graham_kpa(W_tnt_kg, R_m, Pa_kpa=101.325) -> float:
    """Incident overpressure: Ps/Pa = 808[1+(Z/4.5)^2] / sqrt([1+(Z/0.048)^2][1+(Z/0.32)^2][1+(Z/1.35)^2]), Z in m/kg^(1/3) (free-air burst)."""
    Z = scaled_distance(R_m, W_tnt_kg)
    num = 808 * (1 + (Z / 4.5) ** 2)
    den = math.sqrt((1 + (Z / 0.048) ** 2) * (1 + (Z / 0.32) ** 2) * (1 + (Z / 1.35) ** 2))
    return Pa_kpa * num / den


def distance_for_overpressure_m(W_tnt_kg, target_kpa) -> float:
    """Distance at which the overpressure falls to target (bisection; monotone for Z > ~0.3)."""
    lo, hi = 0.5 * W_tnt_kg ** (1 / 3), 1e5
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if kinney_graham_kpa(W_tnt_kg, mid) > target_kpa else (lo, mid)
    return (lo + hi) / 2


def brode_burst_energy_J(P1_kpa_abs, P0_kpa_abs, V_m3, gamma) -> float:
    """Brode energy of a pressurised-gas vessel burst: E = (P1 - P0) V/(gamma - 1). Ground reflection: double the equivalent charge."""
    return (P1_kpa_abs - P0_kpa_abs) * 1e3 * V_m3 / (gamma - 1)


def burst_tnt_equivalent_kg(E_J, tnt_MJ_kg=TNT_MJ_PER_KG, ground_burst=True) -> float:
    w = E_J / (tnt_MJ_kg * 1e6)
    return 2 * w if ground_burst else w

"""BLEVE / fireball radiation (CCPS-style empirical correlations descended from Roberts 1982).

D_max = 5.8 m^(1/3) [m], duration t = 0.45 m^(1/3) s for m < 30 t, 2.6 m^(1/6) s above. These coefficients are the widely
quoted CCPS/TNO values, taken from memory of secondary sources - verify against Roberts (IChemE Symp. Ser. 71, 1982; open PDF)
before use. Surface emissive power from the radiated fraction of combustion energy; solid-sphere view factor, no atmospheric
attenuation unless tau is supplied. Overpressure/fragment effects of the BLEVE are NOT modelled.
"""
from __future__ import annotations

from .ranges import validated

import math


@validated(mass_kg="mass_kg", heat_of_combustion_MJ_kg="heat_of_combustion_MJ_kg", radiated_fraction="fraction_0_1")
def fireball(mass_kg: float, heat_of_combustion_MJ_kg: float, radiated_fraction: float = 0.30) -> dict:
    D = 5.8 * mass_kg ** (1 / 3)
    t = 0.45 * mass_kg ** (1 / 3) if mass_kg < 30_000 else 2.6 * mass_kg ** (1 / 6)
    sep = radiated_fraction * mass_kg * heat_of_combustion_MJ_kg * 1e6 / (math.pi * D * D * t) / 1e3  # kW/m2
    return {"diameter_m": D, "duration_s": t, "surface_emissive_power_kW_m2": sep, "centre_height_m": D / 2 * 1.0}


def incident_kW_m2(fb: dict, ground_distance_m: float, tau: float = 1.0) -> float:
    """Incident flux at a receptor at ground_distance from the point below the fireball centre (vertical receptor facing it).
    View factor of a sphere: (D/2)^2 / r^2 with r from the centre (receptor at ground level)."""
    r = math.hypot(ground_distance_m, fb["diameter_m"] / 2)
    return tau * fb["surface_emissive_power_kW_m2"] * (fb["diameter_m"] / 2) ** 2 / r ** 2 * (ground_distance_m / r)


def thermal_dose(flux_kW_m2: float, duration_s: float) -> float:
    """Dose in (kW/m2)^(4/3) s, the quantity used with probit injury relations (Eisenberg)."""
    return flux_kW_m2 ** (4 / 3) * duration_s


def distance_to_flux_m(fb: dict, target_kW_m2: float, tau: float = 1.0) -> float | None:
    """Ground distance at which incident flux drops to target (bisection); None if never reached even at the base."""
    f = lambda d: incident_kW_m2(fb, d, tau)
    lo, hi = 0.0, fb["diameter_m"] * 100
    if f(hi) > target_kW_m2:
        return None
    # flux is not monotone near the centre (cos factor); search outward from the peak
    d_peak = max((i * fb["diameter_m"] / 200 for i in range(1, 2000)), key=f)
    if f(d_peak) < target_kW_m2:
        return None
    lo = d_peak
    for _ in range(80):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if f(mid) > target_kW_m2 else (lo, mid)
    return (lo + hi) / 2

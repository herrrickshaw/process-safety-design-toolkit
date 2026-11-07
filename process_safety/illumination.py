"""Lumen-method illumination: average maintained illuminance E = N x flux x UF x MF / A.

Utilisation factor UF (from the luminaire's photometric table for the room index) and maintenance factor MF (lamp depreciation and
dirt) are inputs from the luminaire data and the maintenance plan; the target illuminance is an input from the standard the
site follows (emergency escape routes and hazardous-area work have their own targets). Uniformity, glare and emergency-lighting
duration are not checked. Hazardous-area luminaires also need the right Ex protection (see `atex`).
"""
from __future__ import annotations

import math


def average_lux(n: int, flux_lm: float, uf: float, mf: float, area_m2: float) -> float:
    if n < 0 or flux_lm <= 0 or not 0 < uf <= 1 or not 0 < mf <= 1 or area_m2 <= 0:
        raise ValueError("flux and area positive, UF and MF in (0, 1], count not negative")
    return n * flux_lm * uf * mf / area_m2


def luminaires_needed(target_lux: float, flux_lm: float, uf: float, mf: float, area_m2: float) -> dict:
    if target_lux <= 0:
        raise ValueError("target illuminance must be positive")
    exact = target_lux * area_m2 / (flux_lm * uf * mf)
    n = math.ceil(exact - 1e-12)
    return {"n_exact": exact, "n_luminaires": n, "achieved_lux": average_lux(n, flux_lm, uf, mf, area_m2)}

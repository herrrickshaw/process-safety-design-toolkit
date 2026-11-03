"""Injury/lethality probits for thermal radiation and toxic exposure (Eisenberg / TNO / CCPS forms).

Probit constants are recalled from the open literature (CCPS CPQRA, TNO Purple Book): VERIFY against the source for the chemical and
population you assess, and note they are population-average lethality, not regulatory limits. Use your jurisdiction's acceptance
criteria (e.g. AEGL/ERPG/IDLH, PNGRB/MSIHC rules) for decisions.
"""
from __future__ import annotations

import math

# a, b, n for Pr = a + b ln(C^n t) with C in ppm, t in minutes
TOXIC_PROBITS = {
    "chlorine": (-8.29, 0.92, 2.0),
    "ammonia": (-15.6, 1.0, 2.0),
    "hydrogen sulfide": (-31.42, 3.008, 1.43),
}


def probit_thermal(I_kW_m2: float, t_s: float) -> float:
    """Eisenberg: Pr = -14.9 + 2.56 ln(t I^(4/3) / 1e4), I in W/m2, t in s (unprotected skin, fatality)."""
    I = I_kW_m2 * 1e3
    return -14.9 + 2.56 * math.log(t_s * I ** (4 / 3) / 1e4)


def probit_toxic(C_ppm: float, t_min: float, a: float, b: float, n: float) -> float:
    return a + b * math.log(C_ppm ** n * t_min)


def probit_toxic_named(chemical: str, C_ppm: float, t_min: float) -> float:
    return probit_toxic(C_ppm, t_min, *TOXIC_PROBITS[chemical.lower()])


def fraction_from_probit(pr: float) -> float:
    """Probability (0-1) corresponding to a probit value: 0.5 (1 + erf((Pr - 5)/sqrt 2))."""
    return 0.5 * (1 + math.erf((pr - 5) / math.sqrt(2)))


def probit_from_fraction(p: float) -> float:
    lo, hi = -5.0, 15.0
    for _ in range(100):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if fraction_from_probit(mid) < p else (lo, mid)
    return (lo + hi) / 2


def time_to_fraction_thermal_s(I_kW_m2: float, p: float = 0.5) -> float:
    """Exposure time at constant flux giving fatality fraction p."""
    pr = probit_from_fraction(p)
    I = I_kW_m2 * 1e3
    return math.exp((pr + 14.9) / 2.56) * 1e4 / I ** (4 / 3)


def concentration_for_fraction_ppm(chemical: str, t_min: float, p: float = 0.5) -> float:
    a, b, n = TOXIC_PROBITS[chemical.lower()]
    pr = probit_from_fraction(p)
    return (math.exp((pr - a) / b) / t_min) ** (1 / n)

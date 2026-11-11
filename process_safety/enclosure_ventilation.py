"""Enclosure ventilation against a flammable-gas source: steady-state air flow to hold the gas below a fraction of its lower flammable
limit (LFL), and the time for a well-mixed room to reach that fraction. Applies to battery rooms and containers (hydrogen-rich vent gas),
compressor and upgrading rooms (biogas, methane), hydrogen enclosures and any small room with a steady gas source.

Model (well-mixed room, volume V, ventilation air Q, gas added at volume rate g, gas leaves with the air):
    gas balance   V dC/dt = g - C (Q + g)         steady   C_ss = g / (Q + g)
    time to C*    t = -V/(Q + g) ln(1 - C*/C_ss)  (infinite when C* >= C_ss)
    required Q    Q = g (1/C* - 1)                 with C* = fraction x LFL
`mixing_factor` k >= 1 divides the effective air flow (Q/k) for poor mixing or short-circuiting; it is an input, not a default of
engineering practice. The target fraction of the LFL is also an input: a search summary of one vendor article names 25 percent under
NFPA 69 for battery enclosures, but the standard was not read, so no value is coded. The gas generation rate must come from your source
term (for example UL 9540A test data for a battery); it is not estimated here. Ideal gas, constant temperature, uniform mixing: a lighter-
than-air gas can stratify near the ceiling, so a local concentration can exceed this mean. Screening arithmetic, not an NFPA 69 design.
"""
from __future__ import annotations

import math

from .constants import ATM_KPA, R

R_KMOL = R * 1000.0


def gas_volume_rate_m3_s(mass_rate_kg_s: float, Mw: float, T_K: float, P_kPa: float = ATM_KPA) -> float:
    """Volume rate of a gas at T and P from its mass rate (ideal gas): m R T / (Mw P)."""
    if min(mass_rate_kg_s, Mw, T_K, P_kPa) <= 0:
        raise ValueError("mass rate, Mw, T and P must be positive")
    return mass_rate_kg_s / Mw * R_KMOL * T_K / (P_kPa * 1000.0)


def _check(g: float, lfl: float, mixing_factor: float) -> None:
    if g <= 0:
        raise ValueError("gas generation rate must be positive")
    if not 0 < lfl < 1:
        raise ValueError("lfl_vol_frac must be a volume fraction in (0, 1)")
    if mixing_factor < 1.0:
        raise ValueError("mixing_factor must be at least 1 (1 = perfect mixing)")


def required_ventilation_m3_s(gen_m3_s: float, lfl_vol_frac: float, fraction_of_lfl: float, mixing_factor: float = 1.0) -> float:
    """Air flow that holds the steady mean concentration at fraction_of_lfl x LFL: Q = k g (1/C* - 1)."""
    _check(gen_m3_s, lfl_vol_frac, mixing_factor)
    if not 0 < fraction_of_lfl < 1:
        raise ValueError("fraction_of_lfl must be in (0, 1)")
    c = fraction_of_lfl * lfl_vol_frac
    return mixing_factor * gen_m3_s * (1.0 / c - 1.0)


def steady_fraction_of_lfl(gen_m3_s: float, vent_m3_s: float, lfl_vol_frac: float, mixing_factor: float = 1.0) -> float:
    """Steady mean concentration as a fraction of the LFL for a given ventilation flow."""
    _check(gen_m3_s, lfl_vol_frac, mixing_factor)
    if vent_m3_s < 0:
        raise ValueError("ventilation flow must not be negative")
    return gen_m3_s / (vent_m3_s / mixing_factor + gen_m3_s) / lfl_vol_frac


def time_to_fraction_of_lfl_s(volume_m3: float, gen_m3_s: float, vent_m3_s: float, lfl_vol_frac: float, fraction_of_lfl: float,
                              mixing_factor: float = 1.0) -> float:
    """Seconds for an initially clean, well-mixed room to reach fraction_of_lfl x LFL (math.inf if ventilation holds it below)."""
    _check(gen_m3_s, lfl_vol_frac, mixing_factor)
    if volume_m3 <= 0 or vent_m3_s < 0 or not 0 < fraction_of_lfl < 1:
        raise ValueError("volume must be positive, ventilation not negative, fraction in (0, 1)")
    q = vent_m3_s / mixing_factor
    c_star = fraction_of_lfl * lfl_vol_frac
    c_ss = gen_m3_s / (q + gen_m3_s)
    if c_star >= c_ss:
        return math.inf
    return -volume_m3 / (q + gen_m3_s) * math.log(1.0 - c_star / c_ss)

"""Emergency depressuring (blowdown) of a segment: time to a target pressure, orifice for a target time, minimum gas temperature.

Two bounding cases through a fixed orifice (Cd input): ISOTHERMAL (wall/fluid heat input holds temperature: slower) and ADIABATIC
isentropic (no heat input: faster, but the gas gets very cold). Real depressuring lies between and also depends on liquid
inventory (flashing) which is NOT modelled: this is for gas-phase segments. The minimum gas temperature is the isentropic value and is
a screening input for the MDMT / brittle-fracture check, not a metal temperature (walls re-heat the gas).
Common design criteria (e.g. API 521: reach a stated fraction of design pressure within a stated time) are inputs here.
"""
from __future__ import annotations

import math

from .relief import ATM, R, gas_mass_flux

PHI = lambda k: (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))


def choke_pressure_kpa(k: float) -> float:
    """Downstream-atmospheric choking holds while P > ATM/rc."""
    return ATM / (2 / (k + 1)) ** (k / (k - 1))


def depressuring_time_s(V_m3, P0_kpa, Pt_kpa, T0_K, M, k, area_mm2, Cd=0.85, mode="adiabatic", dt=0.05, t_max=36000.0) -> float:
    """Time for the segment to fall from P0 to Pt (kPa abs). Numerical; accurate through the choked and subcritical regimes."""
    Rs = R / (M / 1000)
    A = area_mm2 * 1e-6
    m0 = P0_kpa * 1e3 * V_m3 / (Rs * T0_K)
    m, t = m0, 0.0
    while t < t_max:
        x = m / m0
        if mode == "adiabatic":
            P, T = P0_kpa * x ** k, T0_K * x ** (k - 1)
        else:
            P, T = P0_kpa * x, T0_K
        if P <= Pt_kpa:
            return t
        g, _ = gas_mass_flux(P, ATM, T, M, k)
        mdot = Cd * A * g
        step = min(dt, 0.01 * m / mdot)
        m -= mdot * step
        t += step
    raise ValueError("target not reached")


def closed_form_time_s(V_m3, P0_kpa, Pt_kpa, T0_K, M, k, area_mm2, Cd=0.85, mode="adiabatic") -> float:
    """Choked closed forms (valid while Pt > choke pressure): isothermal t = tau ln(P0/Pt); adiabatic t = 2/((k-1)c)[(P0/Pt)^((k-1)/2k) - 1]."""
    inv_tau = Cd * area_mm2 * 1e-6 * PHI(k) * math.sqrt(k * R * T0_K / (M / 1000)) / V_m3
    if mode == "isothermal":
        return math.log(P0_kpa / Pt_kpa) / inv_tau
    return 2 / ((k - 1) * inv_tau) * ((P0_kpa / Pt_kpa) ** ((k - 1) / (2 * k)) - 1)


def required_area_mm2(V_m3, P0_kpa, Pt_kpa, T0_K, M, k, target_time_s, Cd=0.85, mode="isothermal") -> float:
    """Orifice area that reaches Pt within target_time_s (bisection on the monotone time). Isothermal is the conservative sizing basis."""
    lo, hi = 1.0, 1e6
    for _ in range(60):
        mid = math.sqrt(lo * hi)
        t = depressuring_time_s(V_m3, P0_kpa, Pt_kpa, T0_K, M, k, mid, Cd, mode, dt=0.2)
        lo, hi = (lo, mid) if t <= target_time_s else (mid, hi)
    return hi


def min_gas_temperature_K(T0_K, P0_kpa, Pt_kpa, k) -> float:
    """Isentropic end temperature T0 (Pt/P0)^((k-1)/k): lower bound for MDMT screening (walls and heat input warm the real gas)."""
    return T0_K * (Pt_kpa / P0_kpa) ** ((k - 1) / k)

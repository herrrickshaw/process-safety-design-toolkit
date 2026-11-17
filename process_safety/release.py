"""Release source terms for consequence modelling: hole releases (liquid/gas), vessel blowdown through a hole, tank drain time. SI.

Discharge coefficients are inputs (0.6-0.65 sharp-edged liquid; ~0.85-1.0 gas): choose per your consequence-modelling basis (e.g. a
Phast/CCPS-style scenario set). Flashing/two-phase and rainout are NOT modelled: a liquid stored above its boiling point needs a
flash/aerosol model.
"""
from __future__ import annotations

import math

from .relief import ATM, R, gas_mass_flux

from .constants import G


def hole_area_m2(d_m: float) -> float:
    return math.pi * d_m * d_m / 4


def liquid_release_kg_s(hole_d_m, rho, dP_Pa, head_m=0.0, Cd=0.62) -> float:
    """Bernoulli orifice flow with gauge overpressure dP and liquid head above the hole: Cd A sqrt(2 rho (dP + rho g h))."""
    return Cd * hole_area_m2(hole_d_m) * math.sqrt(2 * rho * (dP_Pa + rho * G * head_m))


def gas_release_kg_s(hole_d_m, P_kpa_abs, T_K, M, k, Cd=0.85, Z=1.0) -> float:
    """Gas release to atmosphere (choked or subcritical as pressure demands)."""
    g, _ = gas_mass_flux(P_kpa_abs, ATM, T_K, M, k, Z)
    return Cd * hole_area_m2(hole_d_m) * g


def tank_drain_time_s(A_tank_m2, hole_d_m, h0_m, Cd=0.62) -> float:
    """Time to drain an open atmospheric tank through a bottom hole (Torricelli): (A/(Cd a)) sqrt(2 h0/g)."""
    return A_tank_m2 / (Cd * hole_area_m2(hole_d_m)) * math.sqrt(2 * h0_m / G)


def blowdown_adiabatic(V_m3, P0_kpa_abs, T0_K, M, k, hole_d_m, Cd=0.85, t_end_s=600.0, dt=0.05) -> dict:
    """Adiabatic (isentropic gas) vessel blowdown through a hole, integrated numerically; returns rate-vs-time samples and totals.
    Isothermal blowdown (heat input) releases more slowly; the adiabatic case is the conservative-fast rate for the early release."""
    Rs = R / (M / 1000)
    rho0 = P0_kpa_abs * 1e3 / (Rs * T0_K)
    m0 = rho0 * V_m3
    m, t, series = m0, 0.0, []
    while t < t_end_s:
        x = m / m0
        P = P0_kpa_abs * x ** k
        T = T0_K * x ** (k - 1)
        if P <= ATM * 1.0005:
            break
        mdot = gas_release_kg_s(hole_d_m, P, T, M, k, Cd)
        series.append((t, mdot, P))
        step = min(dt, 0.02 * m / mdot)
        m -= mdot * step
        t += step
    return {"initial_rate_kg_s": series[0][1] if series else 0.0, "initial_mass_kg": m0, "released_kg": m0 - m,
            "time_to_atm_s": t, "series": series[::max(1, len(series) // 200)]}


def blowdown_adiabatic_analytic_P_ratio(t_s, V_m3, P0_kpa_abs, T0_K, M, k, hole_d_m, Cd=0.85) -> float:
    """Closed form for choked adiabatic blowdown: P/P0 = (1 + (k-1)/2 t/tau)^(-2k/(k-1)), 1/tau = Cd A P0 sqrt(kM/(R T0)) Phi /(V rho0)."""
    Rs = R / (M / 1000)
    rho0 = P0_kpa_abs * 1e3 / (Rs * T0_K)
    phi = (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1)))
    inv_tau = Cd * hole_area_m2(hole_d_m) * P0_kpa_abs * 1e3 * math.sqrt(k * (M / 1000) / (R * T0_K)) * phi / (V_m3 * rho0)
    return (1 + (k - 1) / 2 * t_s * inv_tau) ** (-2 * k / (k - 1))

"""Steel temperature in fire and passive fire protection (PFP) screening: lumped-capacitance model per EN 1993-1-2 forms.

Unprotected: dTa = k_sh (Am/V)/(ca rho_a) h_net dt, h_net = alpha_c (Tg - Ta) + eps sigma (Tg^4 - Ta^4).
Protected (light insulation): dTa = [lam_p/d_p (Ap/V)/(ca rho_a (1+phi/3))] (Tg - Ta) dt - (exp(phi/10) - 1) dTg.
Simplifications: constant steel specific heat (the standard uses a temperature-dependent value), k_sh = 1, no member-specific
section-factor shadow effects, no insulation moisture. Critical temperatures depend on load ratio (550 C is a common default
for loaded steel; vessels/pipes need their own limit). The gas temperature curve is the design basis: pool fire ~ hydrocarbon curve,
jet fire is more severe (supply constant temperature and a higher convective coefficient). Fire-test certification governs real PFP.
"""
from __future__ import annotations

import math

SIGMA = 5.670374e-8


def iso834_C(t_min: float) -> float:
    return 20 + 345 * math.log10(8 * t_min + 1)


def hydrocarbon_C(t_min: float) -> float:
    return 20 + 1080 * (1 - 0.325 * math.exp(-0.167 * t_min) - 0.675 * math.exp(-2.5 * t_min))


def steel_temperature_history(Am_over_V: float, gas_curve=hydrocarbon_C, protection: dict | None = None, t_end_min: float = 120.0,
                              dt_s: float = 1.0, alpha_c: float = 50.0, emissivity: float = 0.7, ca: float = 600.0,
                              rho_a: float = 7850.0, T0_C: float = 20.0) -> list[tuple[float, float]]:
    """Returns [(t_min, steel_C)]. protection = {'lambda': W/mK, 'thickness_m': ..., 'cp': J/kgK, 'rho': kg/m3, 'Ap_over_V': 1/m}."""
    out, Ta, t = [(0.0, T0_C)], T0_C, 0.0
    g_prev = gas_curve(0.0)
    while t < t_end_min * 60:
        t += dt_s
        Tg = gas_curve(t / 60)
        dTg = Tg - g_prev
        g_prev = Tg
        if protection is None:
            h = alpha_c * (Tg - Ta) + emissivity * SIGMA * ((Tg + 273.15) ** 4 - (Ta + 273.15) ** 4)
            dT = Am_over_V / (ca * rho_a) * h * dt_s
        else:
            d, lam, Apv = protection["thickness_m"], protection["lambda"], protection["Ap_over_V"]
            phi = protection["cp"] * protection["rho"] / (ca * rho_a) * d * Apv
            dT = lam / d * Apv / (ca * rho_a * (1 + phi / 3)) * (Tg - Ta) * dt_s - (math.exp(phi / 10) - 1) * dTg
            dT = max(dT, 0.0) if Tg > Ta else dT
        Ta += dT
        if abs(t / 60 - round(t / 60)) < dt_s / 120:  # record each minute
            out.append((round(t / 60), Ta))
    return out


def time_to_critical_min(history: list[tuple[float, float]], T_crit_C: float = 550.0):
    for t, T in history:
        if T >= T_crit_C:
            return t
    return None

"""Gaussian plume screening model (neutrally/passively buoyant gas): Briggs open-country sigmas, Briggs plume rise, concentration
and distance-to-threshold. SI (g, m, s); ppm helper at 25 C.

SCREENING ONLY. Not valid for dense/heavier-than-air gases (chlorine, LPG, cold LNG, ammonia clouds), calm winds < ~1 m/s, buildings
wakes, complex terrain, or averaging-time effects. H2S/toxic zoning and QRA need a validated dense-gas-capable tool (e.g. Phast).
Briggs sigma coefficients and the plume-rise constants are recalled from the open literature: verify before regulatory use.
"""
from __future__ import annotations

import math

# Briggs (1973) open-country sigma_y, sigma_z (m) as functions of downwind distance x (m)
_SIGMA = {
    "A": (lambda x: 0.22 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.20 * x),
    "B": (lambda x: 0.16 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.12 * x),
    "C": (lambda x: 0.11 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.08 * x * (1 + 0.0002 * x) ** -0.5),
    "D": (lambda x: 0.08 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.06 * x * (1 + 0.0015 * x) ** -0.5),
    "E": (lambda x: 0.06 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.03 * x * (1 + 0.0003 * x) ** -1),
    "F": (lambda x: 0.04 * x * (1 + 0.0001 * x) ** -0.5, lambda x: 0.016 * x * (1 + 0.0003 * x) ** -1),
}


def sigmas(x_m: float, stability: str = "D") -> tuple[float, float]:
    sy, sz = _SIGMA[stability.upper()]
    return sy(x_m), sz(x_m)


def buoyancy_flux(v_exit_m_s, d_m, T_stack_K, T_amb_K) -> float:
    """F = g v d^2/4 (Ts - Ta)/Ts  (m4/s3)."""
    return 9.80665 * v_exit_m_s * d_m ** 2 / 4 * (T_stack_K - T_amb_K) / T_stack_K


def plume_rise_m(F: float, u_m_s: float, stability: str = "D", T_amb_K: float = 293.15) -> float:
    """Briggs final rise: neutral/unstable F<55: 21.425 F^0.75/u, else 38.71 F^0.6/u; stable (E,F): 2.6 (F/(u s))^(1/3), s=g/Ta dtheta/dz
    with dtheta/dz = 0.02 (E) or 0.035 (F) K/m."""
    if F <= 0:
        return 0.0
    if stability.upper() in ("E", "F"):
        s = 9.80665 / T_amb_K * (0.02 if stability.upper() == "E" else 0.035)
        return 2.6 * (F / (u_m_s * s)) ** (1 / 3)
    return (21.425 * F ** 0.75 if F < 55 else 38.71 * F ** 0.6) / u_m_s


def concentration_g_m3(Q_g_s, u_m_s, H_m, x_m, y_m=0.0, z_m=0.0, stability="D") -> float:
    """Gaussian plume with total ground reflection."""
    if x_m <= 0:
        return 0.0
    sy, sz = sigmas(x_m, stability)
    lateral = math.exp(-y_m ** 2 / (2 * sy ** 2))
    vertical = math.exp(-(z_m - H_m) ** 2 / (2 * sz ** 2)) + math.exp(-(z_m + H_m) ** 2 / (2 * sz ** 2))
    return Q_g_s / (2 * math.pi * u_m_s * sy * sz) * lateral * vertical


def max_ground_concentration(Q_g_s, u_m_s, H_m, stability="D", x_max=20000.0) -> tuple[float, float]:
    """(max ground-level centreline concentration g/m3, distance m) by scanning x."""
    best = (0.0, 0.0)
    x = 5.0
    while x < x_max:
        c = concentration_g_m3(Q_g_s, u_m_s, H_m, x, stability=stability)
        if c > best[0]:
            best = (c, x)
        x *= 1.03
    return best


def distance_to_threshold_m(Q_g_s, u_m_s, H_m, threshold_g_m3, stability="D", x_max=50000.0):
    """Farthest downwind distance at which the ground-level centreline concentration still exceeds the threshold (None if never)."""
    far, x = None, 5.0
    while x < x_max:
        if concentration_g_m3(Q_g_s, u_m_s, H_m, x, stability=stability) >= threshold_g_m3:
            far = x
        x *= 1.01
    return far


def ppm_to_mg_m3(ppm: float, M: float, T_K: float = 298.15, P_kPa: float = 101.325) -> float:
    return ppm * M * P_kPa / (8.314462618 * T_K)


def mg_m3_to_ppm(mg_m3: float, M: float, T_K: float = 298.15, P_kPa: float = 101.325) -> float:
    return mg_m3 * 8.314462618 * T_K / (M * P_kPa)

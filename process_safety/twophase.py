"""Two-phase and flashing discharge by the omega method (homogeneous equilibrium, Leung-type single parameter).

The fluid is described by one number, omega, through  v/v0 = omega (P0/P - 1) + 1  (specific volume against pressure). Integrating
the mechanical energy balance gives the mass flux at pressure ratio eta = P/P0:

    G(eta) = sqrt(2 P0/v0) * sqrt(omega ln(1/eta) - (omega - 1)(1 - eta)) / (omega (1/eta - 1) + 1)

so nothing is recalled from a table: the critical (choked) flux is found by maximising G over eta, and the result is checked in the
tests against the closed-form critical-ratio equation published for the omega method and against two exact limits (omega -> 0
is incompressible liquid flow; omega = 1 is isothermal ideal-gas choking at eta = exp(-1/2)).

Limits: homogeneous (no slip), equilibrium, no non-condensables, inlet is saturated liquid, low-subcooled or two-phase. Highly
subcooled liquid (flashing only near the exit), reactive systems (DIERS runaway sizing) and long pipes (flashing in the line)
need other methods. omega is an input or is computed from fluid properties you supply; no property data are coded. The discharge
coefficient Kd is an input (the valve vendor / API 520 value for two-phase service), not a default.
"""
from __future__ import annotations

import math

from .ranges import validated

_GOLD = (math.sqrt(5) - 1) / 2


def omega_two_point(v0_m3_kg: float, v9_m3_kg: float) -> float:
    """omega = 9 (v9/v0 - 1), from the specific volume at the inlet pressure and at 90% of it (both at equal enthalpy/entropy)."""
    if v0_m3_kg <= 0 or v9_m3_kg <= 0:
        raise ValueError("specific volumes must be positive")
    return 9.0 * (v9_m3_kg / v0_m3_kg - 1.0)


def omega_saturated_liquid(cp_l_J_kgK: float, T_K: float, P_Pa: float, v_l_m3_kg: float, v_lg_m3_kg: float, h_lg_J_kg: float) -> float:
    """Flashing saturated liquid: omega = (cp T P / v_l) (v_lg / h_lg)^2. Properties are at the inlet saturation state (SI)."""
    for x in (cp_l_J_kgK, T_K, P_Pa, v_l_m3_kg, v_lg_m3_kg, h_lg_J_kg):
        if x <= 0:
            raise ValueError("all properties must be positive")
    return cp_l_J_kgK * T_K * P_Pa / v_l_m3_kg * (v_lg_m3_kg / h_lg_J_kg) ** 2


def _g_dimensionless(eta: float, omega: float) -> float:
    """G / sqrt(2 P0 / v0) at pressure ratio eta."""
    num = omega * math.log(1.0 / eta) - (omega - 1.0) * (1.0 - eta)
    return math.sqrt(max(num, 0.0)) / (omega * (1.0 / eta - 1.0) + 1.0)


def critical_pressure_ratio(omega: float) -> float:
    """eta_c that maximises the mass flux (golden-section on ln eta; the flux has one maximum)."""
    if omega <= 0:
        raise ValueError("omega must be positive")
    a, b = math.log(1e-12), 0.0
    c, d = b - _GOLD * (b - a), a + _GOLD * (b - a)
    fc, fd = _g_dimensionless(math.exp(c), omega), _g_dimensionless(math.exp(d), omega)
    for _ in range(200):
        if fc > fd:
            b, d, fd = d, c, fc
            c = b - _GOLD * (b - a)
            fc = _g_dimensionless(math.exp(c), omega)
        else:
            a, c, fc = c, d, fd
            d = a + _GOLD * (b - a)
            fd = _g_dimensionless(math.exp(d), omega)
        if b - a < 1e-13:
            break
    return math.exp((a + b) / 2)


@validated(P0_kPa="pressure_abs_kPa")
def mass_flux(P0_kPa: float, rho0_kg_m3: float, omega: float, P_back_kPa: float | None = None) -> dict:
    """Mass flux G (kg/m2/s) through a frictionless nozzle. Choked when the back pressure is at or below eta_c * P0."""
    if rho0_kg_m3 <= 0 or omega <= 0:
        raise ValueError("rho0 and omega must be positive")
    P0 = P0_kPa * 1000.0
    scale = math.sqrt(2.0 * P0 * rho0_kg_m3)          # sqrt(2 P0 / v0)
    eta_c = critical_pressure_ratio(omega)
    eta_b = None if P_back_kPa is None else P_back_kPa / P0_kPa
    if eta_b is not None and not 0 < eta_b <= 1:
        raise ValueError("back pressure must be above 0 and not above the inlet pressure")
    choked = eta_b is None or eta_b <= eta_c
    eta = eta_c if choked else eta_b
    return {"G_kg_m2_s": scale * _g_dimensionless(eta, omega), "eta_critical": eta_c, "eta_used": eta,
            "regime": "choked" if choked else "subcritical", "omega": omega}


def relief_area_mm2(W_kg_s: float, G_kg_m2_s: float, Kd: float) -> float:
    """Required effective area A = W / (Kd G). Kb and Kc (back pressure, rupture disk) are not applied: state them yourself."""
    if W_kg_s <= 0 or G_kg_m2_s <= 0 or not 0 < Kd <= 1:
        raise ValueError("W and G must be positive and Kd in (0, 1]")
    return W_kg_s / (Kd * G_kg_m2_s) * 1e6

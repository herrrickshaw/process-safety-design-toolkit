"""PSV inlet/outlet piping checks and reaction forces.

API 520 Part II practice: inlet line loss <= 3% of set pressure (checked here); built-up back pressure on a conventional valve
<= ~10% of set (checked in relief.gas_area). Outlet reaction force of an open discharge uses the momentum balance F = m v + (Pe - Pa) Ae;
exit conditions are inputs (take from the discharge-line hydraulics). Acoustic-induced vibration, flow-induced vibration and
piping stress are NOT assessed.
"""
from __future__ import annotations

import math

from .relief import ATM, R


def inlet_loss_check(dp_inlet_kpa: float, set_kpag: float, limit_fraction: float = 0.03) -> dict:
    frac = dp_inlet_kpa / set_kpag
    return {"inlet_loss_fraction": frac, "limit": limit_fraction, "ok": frac <= limit_fraction,
            "action": "ok" if frac <= limit_fraction else "shorten/enlarge inlet line, relocate valve, or use a pilot-operated valve (API 520-II)"}


def reaction_force_N(mass_flow_kg_s: float, v_exit_m_s: float, P_exit_kpa_abs: float, A_exit_m2: float) -> float:
    """Open-discharge thrust on the outlet elbow/stack: m v + (Pe - Patm) Ae."""
    return mass_flow_kg_s * v_exit_m_s + (P_exit_kpa_abs - ATM) * 1e3 * A_exit_m2


def exit_state_from_mach(mass_flow_kg_s, D_exit_m, P_exit_kpa_abs, T_exit_K, M, k) -> dict:
    """Exit velocity/Mach for a given mass flow at stated exit static pressure and temperature (ideal gas)."""
    A = math.pi * D_exit_m ** 2 / 4
    rho = P_exit_kpa_abs * 1e3 * (M / 1000) / (R * T_exit_K)
    v = mass_flow_kg_s / (rho * A)
    c = math.sqrt(k * R * T_exit_K / (M / 1000))
    return {"velocity_m_s": v, "mach": v / c, "area_m2": A, "density_kg_m3": rho}

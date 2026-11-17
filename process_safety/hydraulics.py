"""Line hydraulics, control-valve liquid sizing, pump NPSH/power, and water-hammer (surge) screening. SI units.

Everything here is textbook physics (Darcy-Weisbach, isothermal compressible flow, Joukowsky, IEC 60534 liquid definitions) and is
checked against first-principles identities in the tests. Colebrook is solved iteratively. Roughness, K-values and the erosional C
constant are inputs: confirm against your client's line-sizing criteria (velocity / dP per 100 m limits are project specific).
"""
from __future__ import annotations

import math

from .constants import G
from .constants import R


def reynolds(rho, v, D, mu_Pa_s) -> float:
    return rho * v * D / mu_Pa_s


def friction_factor(Re: float, D: float, eps: float = 4.6e-5) -> float:
    """Darcy friction factor: 64/Re laminar; Colebrook (iterated) for Re >= 2300 (the transition zone uses the turbulent value)."""
    if Re < 2300:
        return 64 / Re
    f = 0.25 / math.log10(eps / (3.7 * D) + 5.74 / Re ** 0.9) ** 2  # Swamee-Jain start
    for _ in range(60):
        f_new = 1 / (-2 * math.log10(eps / (3.7 * D) + 2.51 / (Re * math.sqrt(f)))) ** 2
        if abs(f_new - f) < 1e-12:
            break
        f = f_new
    return f


def incompressible_dp_kpa(Q_m3_s, D, L, rho, mu_Pa_s, eps=4.6e-5, K_total=0.0, dz=0.0) -> dict:
    """Pressure drop (kPa) of a liquid line: friction + fittings (sum K) + static head (dz positive = uphill)."""
    A = math.pi * D * D / 4
    v = Q_m3_s / A
    Re = reynolds(rho, v, D, mu_Pa_s)
    f = friction_factor(Re, D, eps)
    dyn = rho * v * v / 2
    dp_fric = f * L / D * dyn
    dp_fit = K_total * dyn
    dp_static = rho * G * dz
    return {"velocity_m_s": v, "Re": Re, "f": f, "dp_friction_kPa": dp_fric / 1e3, "dp_fittings_kPa": dp_fit / 1e3,
            "dp_static_kPa": dp_static / 1e3, "dp_total_kPa": (dp_fric + dp_fit + dp_static) / 1e3,
            "dp_per_100m_kPa": f / D * dyn * 100 / 1e3}


def isothermal_gas_outlet_kpa(mass_kg_s, D, L, P1_kpa, T_K, M, mu_Pa_s, eps=4.6e-5) -> dict:
    """Outlet pressure of a long gas line, isothermal ideal gas (Z=1): P1^2-P2^2 = G^2 Rs T [f L/D + 2 ln(P1/P2)] (solved by bisection).
    Raises if the flow exceeds choked capacity for this line."""
    Rs = R / (M / 1000)
    Gm = mass_kg_s / (math.pi * D * D / 4)
    Re = Gm * D / mu_Pa_s
    f = friction_factor(Re, D, eps)
    P1 = P1_kpa * 1e3

    def resid(P2):
        return P1 ** 2 - P2 ** 2 - Gm ** 2 * Rs * T_K * (f * L / D + 2 * math.log(P1 / P2))

    lo, hi = 1.0, P1
    if resid(lo) < 0:
        raise ValueError("flow exceeds what the line can pass at this inlet pressure (choked)")
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if resid(mid) > 0 else (lo, mid)
    P2 = (lo + hi) / 2
    rho2 = P2 * (M / 1000) / (8.314462618 * T_K)
    v2 = Gm / rho2
    c = math.sqrt(Rs * T_K)  # isothermal sonic speed
    return {"P2_kPa": P2 / 1e3, "f": f, "Re": Re, "outlet_velocity_m_s": v2, "outlet_mach_isothermal": v2 / c,
            "dp_kPa": (P1 - P2) / 1e3}


def erosional_velocity_m_s(rho_kg_m3: float, C_us: float = 100.0) -> float:
    """API RP 14E style limit Ve = C/sqrt(rho) with C in US units (ft/s, lb/ft3); C=100 continuous, up to ~125 intermittent
    (clean, non-corrosive service may allow more). Converted to SI exactly here; confirm C against the client criterion."""
    rho_lb_ft3 = rho_kg_m3 * 0.0624279606
    return C_us / math.sqrt(rho_lb_ft3) * 0.3048


# --- control valve (liquids, IEC 60534 definitions) ------------------------------------------------------------------

def kv_liquid(Q_m3_h, rho, dP_bar) -> float:
    """Kv (m3/h of water at 15 C per 1 bar) for a non-choked liquid: Kv = Q sqrt((rho/1000)/dP)."""
    return Q_m3_h * math.sqrt((rho / 1000) / dP_bar)


def liquid_choked_dp_bar(P1_bar_abs, Pv_bar_abs, Pc_bar_abs, FL=0.9) -> float:
    """Maximum useful dP before choking: FL^2 (P1 - FF Pv), FF = 0.96 - 0.28 sqrt(Pv/Pc) (IEC 60534-2-1 liquid critical pressure ratio)."""
    FF = 0.96 - 0.28 * math.sqrt(Pv_bar_abs / Pc_bar_abs)
    return FL ** 2 * (P1_bar_abs - FF * Pv_bar_abs)


def cv_from_kv(kv: float) -> float:
    return kv * 1.1561  # 1 Cv = 0.865 Kv


# --- pumps -------------------------------------------------------------------------------------------------------------

def npsha_m(P_suction_kpa_abs, Pv_kpa_abs, rho, static_head_m, line_loss_m) -> float:
    """NPSH available = (Ps - Pv)/(rho g) + static head above pump centreline - suction line losses (all metres of liquid)."""
    return (P_suction_kpa_abs - Pv_kpa_abs) * 1e3 / (rho * G) + static_head_m - line_loss_m


def pump_hydraulic_kW(Q_m3_h, head_m, rho) -> float:
    return rho * G * (Q_m3_h / 3600) * head_m / 1e3


def pump_affinity(Q1, H1, P1, N1, N2, D1=None, D2=None) -> dict:
    """Speed change (and optional impeller trim): Q ~ N D, H ~ (N D)^2, P ~ N^3 D^3 (similar-impeller approximation)."""
    r = (N2 / N1) * ((D2 / D1) if D1 and D2 else 1.0)
    return {"Q": Q1 * r, "H": H1 * r * r, "P": P1 * r ** 3}


# --- water hammer ------------------------------------------------------------------------------------------------------

def wave_speed_m_s(K_fluid_Pa, rho, D, wall_m, E_pipe_Pa, c1=1.0) -> float:
    """Pressure-wave speed in a liquid-filled elastic pipe: a = sqrt((K/rho) / (1 + c1 K D /(E e)))."""
    return math.sqrt((K_fluid_Pa / rho) / (1 + c1 * K_fluid_Pa * D / (E_pipe_Pa * wall_m)))


def joukowsky_kpa(rho, a_m_s, dv_m_s) -> float:
    """Surge pressure rise from an instantaneous velocity change: rho a dv."""
    return rho * a_m_s * dv_m_s / 1e3


def surge_screen(L_m, a_m_s, closure_s, rho, dv_m_s) -> dict:
    """Instantaneous (Joukowsky) if closure <= 2L/a; otherwise a linear-closure estimate scaled by (2L/a)/closure (screening only;
    a method-of-characteristics surge analysis is needed for real systems, column separation, pumps trips)."""
    tc = 2 * L_m / a_m_s
    full = joukowsky_kpa(rho, a_m_s, dv_m_s)
    return {"critical_time_s": tc, "joukowsky_kPa": full, "estimated_kPa": full if closure_s <= tc else full * tc / closure_s,
            "rapid_closure": closure_s <= tc}

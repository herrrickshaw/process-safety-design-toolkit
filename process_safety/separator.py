"""Gas-liquid separator / flare knock-out drum sizing: Souders-Brown gas capacity + liquid holdup (conceptual sizing).

Souders-Brown: v_t = K sqrt((rho_L - rho_G)/rho_G); K is a design input. API 12J K-ranges quoted by search summaries for vertical
vessels with a mesh pad: 0.061-0.107 m/s (these are the SI K in m/s; K for horizontal and for no-demister cases differs; confirm
against API 12J / your client's guideline - the standard was not read). Vessel geometry heuristics (disengagement heights,
L/D 2.5-5) are common practice, not code requirements, and are parameters you can override. Conceptual only: final sizing needs
mist-extractor vendor data, inlet device, slug volume and surge, and mechanical design (ASME VIII).
"""
from __future__ import annotations

import math

from .constants import G


def souders_brown_velocity(rho_L: float, rho_G: float, K: float) -> float:
    return K * math.sqrt((rho_L - rho_G) / rho_G)


def droplet_terminal_velocity(d_um: float, rho_L: float, rho_G: float, mu_G: float) -> float:
    """Terminal settling velocity of a liquid droplet in gas (m/s): iterate with the Schiller-Naumann drag law (Re < 1000)."""
    d = d_um * 1e-6
    v = math.sqrt(4 * G * d * (rho_L - rho_G) / (3 * 0.44 * rho_G))  # Newton regime start
    for _ in range(200):
        Re = max(rho_G * v * d / mu_G, 1e-9)
        Cd = 24 / Re * (1 + 0.15 * Re ** 0.687) if Re < 1000 else 0.44
        v_new = math.sqrt(4 * G * d * (rho_L - rho_G) / (3 * Cd * rho_G))
        if abs(v_new - v) < 1e-9:
            break
        v = 0.5 * (v + v_new)
    return v


def _round_up(x: float, step: float = 0.05) -> float:
    return math.ceil(x / step - 1e-9) * step


def vertical_separator(Qg_m3_s: float, Ql_m3_s: float, rho_L: float, rho_G: float, K: float = 0.0762,
                       holdup_s: float = 300.0, gas_design_fraction: float = 1.0, h_low_m: float = 0.3,
                       h_disengage_min_m: float = 0.9, h_mist_m: float = 0.3) -> dict:
    """Vertical separator: D from gas capacity, liquid height from holdup (NLL), tangent-to-tangent height from heuristics."""
    vt = souders_brown_velocity(rho_L, rho_G, K) * gas_design_fraction
    D = _round_up(math.sqrt(4 * Qg_m3_s / (math.pi * vt)))
    h_liq = holdup_s * Ql_m3_s / (math.pi * D * D / 4)
    h_dis = max(h_disengage_min_m, 0.5 * D)
    H = h_low_m + h_liq + h_dis + h_mist_m
    return {"diameter_m": D, "tangent_height_m": H, "liquid_height_m": h_liq, "design_gas_velocity_m_s": vt,
            "actual_gas_velocity_m_s": Qg_m3_s / (math.pi * D * D / 4), "L_over_D": H / D,
            "notes": [] if 2 <= H / D <= 6 else ["L/D outside 2-6: revisit holdup, K, or use a horizontal vessel"]}


def _segment_area(D: float, h: float) -> float:
    """Area of the circular segment of liquid depth h in a horizontal vessel of diameter D."""
    h = min(max(h, 0.0), D)
    return D * D / 4 * math.acos(1 - 2 * h / D) - (D / 2 - h) * math.sqrt(max(h * (D - h), 0.0))


def horizontal_separator(Qg_m3_s: float, Ql_m3_s: float, rho_L: float, rho_G: float, K: float = 0.15,
                         holdup_s: float = 300.0, level_fraction: float = 0.5, ld_range=(2.5, 5.0)) -> dict:
    """Horizontal separator: smallest D (50 mm steps) whose gas-space velocity <= Souders-Brown limit and whose
    length (from holdup volume at the chosen liquid depth) gives L/D within ld_range; K default is a placeholder, set it per guideline."""
    vt = souders_brown_velocity(rho_L, rho_G, K)
    V_hold = holdup_s * Ql_m3_s
    D = 0.3
    for _ in range(400):
        A = math.pi * D * D / 4
        A_liq = _segment_area(D, level_fraction * D)
        A_gas = A - A_liq
        L = V_hold / A_liq if A_liq > 0 else float("inf")
        ok_gas = Qg_m3_s / A_gas <= vt
        if ok_gas and L / D <= ld_range[1]:
            L = max(L, ld_range[0] * D)
            return {"diameter_m": D, "length_m": _round_up(L), "L_over_D": L / D, "gas_velocity_m_s": Qg_m3_s / A_gas,
                    "design_gas_velocity_m_s": vt, "notes": ["length is tangent-to-tangent; add inlet/outlet allowances"]}
        D += 0.05
    raise ValueError("no horizontal solution in range")


def knockout_drum_vertical(Qg_m3_s: float, rho_L: float, rho_G: float, mu_G: float, droplet_um: float = 300.0,
                           velocity_fraction: float = 1.0) -> dict:
    """Vertical flare knock-out drum: gas velocity at/below the settling velocity of a droplet of the design size
    (300-600 um is the commonly quoted flare-KO design range; confirm against API 521)."""
    vt = droplet_terminal_velocity(droplet_um, rho_L, rho_G, mu_G) * velocity_fraction
    D = _round_up(math.sqrt(4 * Qg_m3_s / (math.pi * vt)))
    return {"diameter_m": D, "settling_velocity_m_s": vt, "droplet_um": droplet_um}

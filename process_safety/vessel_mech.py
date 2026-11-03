"""Pressure-vessel shell/head thickness and MAWP: ASME BPVC VIII-1 UG-27 / UG-32 thin-wall formulas (inside-radius basis).

Allowable stress S (Section II-D) is an INPUT, not tabulated here; joint efficiency E, corrosion allowance and tolerances are the
designer's. Valid for t <= R/2 and P <= 0.385 S E (cylinders). External pressure, nozzle reinforcement, loadings, torispherical heads,
flanges and fatigue are not covered: this is a sizing check, not a code calculation. Edition: confirm the formulas against yours.
"""
from __future__ import annotations


def cylinder_thickness_mm(P_kpag, R_in_mm, S_MPa, E=1.0, CA_mm=0.0) -> dict:
    """Circumferential: t = P R/(S E - 0.6 P); longitudinal: t = P R/(2 S E + 0.4 P). The larger governs."""
    P = P_kpag / 1000.0  # MPa
    if P > 0.385 * S_MPa * E:
        raise ValueError("P > 0.385 S E: thick-wall rules apply")
    t_circ = P * R_in_mm / (S_MPa * E - 0.6 * P)
    t_long = P * R_in_mm / (2 * S_MPa * E + 0.4 * P)
    t = max(t_circ, t_long)
    return {"t_circumferential_mm": t_circ, "t_longitudinal_mm": t_long, "t_required_mm": t, "t_with_CA_mm": t + CA_mm}


def sphere_thickness_mm(P_kpag, R_in_mm, S_MPa, E=1.0, CA_mm=0.0) -> float:
    P = P_kpag / 1000.0
    return P * R_in_mm / (2 * S_MPa * E - 0.2 * P) + CA_mm


def ellipsoidal_head_thickness_mm(P_kpag, D_in_mm, S_MPa, E=1.0, CA_mm=0.0) -> float:
    """2:1 ellipsoidal head: t = P D/(2 S E - 0.2 P)."""
    P = P_kpag / 1000.0
    return P * D_in_mm / (2 * S_MPa * E - 0.2 * P) + CA_mm


def cylinder_mawp_kpag(t_mm, R_in_mm, S_MPa, E=1.0, CA_mm=0.0) -> float:
    """MAWP of the cylinder from the corroded thickness: lesser of circumferential P = S E t/(R + 0.6 t) and longitudinal P = 2 S E t/(R - 0.4 t)."""
    t = t_mm - CA_mm
    p_c = S_MPa * E * t / (R_in_mm + 0.6 * t)
    p_l = 2 * S_MPa * E * t / (R_in_mm - 0.4 * t)
    return min(p_c, p_l) * 1000.0


def hydrotest_kpag(MAWP_kpag, stress_ratio=1.0) -> float:
    """Standard hydrostatic test pressure 1.3 x MAWP x (S at test temperature / S at design temperature) (UG-99(b)); verify edition."""
    return 1.3 * MAWP_kpag * stress_ratio


def liquid_inventory_m3(D_m, L_m, fill_fraction=1.0, orientation="horizontal") -> float:
    """Cylindrical shell volume (heads excluded) at a fill fraction of diameter (horizontal) or height (vertical)."""
    import math
    if orientation == "vertical":
        return math.pi * D_m ** 2 / 4 * L_m * fill_fraction
    h = fill_fraction * D_m
    seg = D_m ** 2 / 4 * math.acos(1 - 2 * h / D_m) - (D_m / 2 - h) * math.sqrt(max(h * (D_m - h), 0.0))
    return seg * L_m

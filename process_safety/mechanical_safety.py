"""Mechanical and machinery safety: ISO 13849-1 performance level, ISO 13855 safeguard distance, lifting, dropped-object and impact energy,
pipe span and thermal flexibility screening, and bolt torque.

NOTES: ISO 13849-1 risk-graph corners (S2F2P2 -> e; S2F1P1 -> c) were corroborated by search; the rest of the graph and the PFHd bands are recalled
from the standard: verify. ISO 13855 is implemented in its pre-2024 form S = K T + C (K = 2000 mm/s, 1600 mm/s beyond 500 mm; C = 8 (d - 14), >= 0, for d <= 40 mm);
the 2024 edition changed the formula (S = K T + DDS + Z): confirm the edition your project cites. Structural, pressure-part and foundation
design are not covered here (see vessel_mech and a structural code).
"""
from __future__ import annotations

import math

from .constants import G

# --- ISO 13849-1 --------------------------------------------------------------------------------------------------------

_RISK_GRAPH = {("S1", "F1", "P1"): "a", ("S1", "F1", "P2"): "b", ("S1", "F2", "P1"): "b", ("S1", "F2", "P2"): "c",
               ("S2", "F1", "P1"): "c", ("S2", "F1", "P2"): "d", ("S2", "F2", "P1"): "d", ("S2", "F2", "P2"): "e"}
_PFH_BANDS = [("e", 1e-8, 1e-7), ("d", 1e-7, 1e-6), ("c", 1e-6, 3e-6), ("b", 3e-6, 1e-5), ("a", 1e-5, 1e-4)]  # PL, lower (>=), upper (<)


def required_pl(severity: str, frequency: str, possibility: str) -> str:
    """S1 slight / S2 serious injury; F1 seldom or short / F2 frequent or long exposure; P1 avoidance possible / P2 scarcely possible."""
    return _RISK_GRAPH[(severity, frequency, possibility)]


def pl_from_pfhd(pfhd_per_h: float) -> str | None:
    for pl, lo, hi in _PFH_BANDS:
        if lo <= pfhd_per_h < hi:
            return pl
    return None


def pl_meets(achieved: str, required: str) -> bool:
    return achieved >= required  # letters a < b < ... < e


# --- ISO 13855 (pre-2024 form) ---------------------------------------------------------------------------------------------

def safeguard_distance_mm(stopping_time_s: float, detection_capability_mm: float) -> float:
    """S = K T + C. K = 2000 mm/s first; if S > 500 mm use K = 1600 mm/s (S not below 500 mm). C = 8 (d - 14) >= 0. T = total time from
    actuation of the sensing device to the end of the hazardous motion."""
    C = max(0.0, 8 * (detection_capability_mm - 14))
    S = 2000 * stopping_time_s + C
    if S > 500:
        S = max(1600 * stopping_time_s + C, 500)
    return S


# --- lifting -----------------------------------------------------------------------------------------------------------

def sling_leg_tension_N(load_kg: float, legs_bearing: int, angle_from_vertical_deg: float) -> float:
    """Tension in each bearing leg: T = W/(n cos(theta)), theta measured from the vertical. In 3- and 4-leg slings do not assume more than
    the legs that actually bear (often 2 or 3); the load can be shared unequally."""
    return load_kg * G / (legs_bearing * math.cos(math.radians(angle_from_vertical_deg)))


def required_wll_N(tension_N: float, dynamic_factor: float = 1.0) -> float:
    return tension_N * dynamic_factor


# --- dropped objects and impacts ------------------------------------------------------------------------------------------

def terminal_velocity_m_s(mass_kg: float, Cd: float, area_m2: float, rho_air: float = 1.2) -> float:
    return math.sqrt(2 * mass_kg * G / (rho_air * Cd * area_m2))


def drop_velocity_m_s(height_m: float, mass_kg: float = 0.0, Cd: float = 0.0, area_m2: float = 0.0, rho_air: float = 1.2) -> float:
    """Impact velocity after a free fall of height h: sqrt(2 g h) in vacuum; with drag v = vt sqrt(1 - exp(-2 g h/vt^2))."""
    if not (mass_kg and Cd and area_m2):
        return math.sqrt(2 * G * height_m)
    vt = terminal_velocity_m_s(mass_kg, Cd, area_m2, rho_air)
    return vt * math.sqrt(1 - math.exp(-2 * G * height_m / vt ** 2))


def impact_energy_kJ(mass_kg: float, v_m_s: float) -> float:
    return 0.5 * mass_kg * v_m_s ** 2 / 1000


def ship_collision_energy_kJ(displacement_t: float, speed_m_s: float, added_mass_factor: float = 1.4) -> float:
    """E = 1/2 (1 + Ca) m v^2: Ca ~ 0.4 sideways, ~0.1 head-on/stern (commonly quoted offshore values, recalled); only the portion NOT
    dissipated in the ship's own deformation reaches the structure: that split is a design-code or FE matter."""
    return 0.5 * added_mass_factor * displacement_t * 1000 * speed_m_s ** 2 / 1000


# --- piping mechanics --------------------------------------------------------------------------------------------------------

def pipe_section(OD_mm: float, wall_mm: float) -> dict:
    do, di = OD_mm / 1000, (OD_mm - 2 * wall_mm) / 1000
    I = math.pi / 64 * (do ** 4 - di ** 4)
    return {"I_m4": I, "Z_m3": I / (do / 2), "steel_area_m2": math.pi / 4 * (do ** 2 - di ** 2), "flow_area_m2": math.pi / 4 * di ** 2}


def pipe_weight_N_m(OD_mm: float, wall_mm: float, fluid_density: float = 0.0, insulation_kg_m: float = 0.0, steel_density: float = 7850.0) -> float:
    s = pipe_section(OD_mm, wall_mm)
    return (s["steel_area_m2"] * steel_density + s["flow_area_m2"] * fluid_density + insulation_kg_m) * G


def max_pipe_span_m(OD_mm, wall_mm, fluid_density=0.0, insulation_kg_m=0.0, E_GPa=200.0, deflection_limit_mm=10.0, allowable_MPa=50.0) -> dict:
    """Simply supported uniformly loaded span limited by deflection (5 w L^4/(384 E I)) and bending stress (w L^2/(8 Z)).
    Conservative versus continuous multi-support lines; allowable sustained stress and deflection limit are project criteria
    (B31.3 sustained-stress limits apply to the combined longitudinal stress, not just bending)."""
    s = pipe_section(OD_mm, wall_mm)
    w = pipe_weight_N_m(OD_mm, wall_mm, fluid_density, insulation_kg_m)
    L_defl = (384 * E_GPa * 1e9 * s["I_m4"] * deflection_limit_mm / 1000 / (5 * w)) ** 0.25
    L_str = math.sqrt(8 * allowable_MPa * 1e6 * s["Z_m3"] / w)
    return {"w_N_m": w, "L_deflection_m": L_defl, "L_stress_m": L_str, "max_span_m": min(L_defl, L_str)}


def thermal_growth_mm(length_m: float, delta_T_K: float, alpha_per_K: float = 12e-6) -> float:
    """Free thermal expansion; carbon steel ~12e-6 per K (stainless ~17e-6): use the code's expansion data."""
    return alpha_per_K * length_m * delta_T_K * 1000


def guided_cantilever_leg_m(OD_mm: float, delta_mm: float, allowable_MPa: float = 150.0, E_GPa: float = 200.0) -> float:
    """Minimum leg length L = sqrt(3 E D delta / sigma) for a guided cantilever absorbing delta (Kellogg-style flexibility screening).
    Allowable displacement stress is the B31.3 SA (code value, an input); a stress analysis supersedes this."""
    return math.sqrt(3 * E_GPa * 1e9 * (OD_mm / 1000) * (delta_mm / 1000) / (allowable_MPa * 1e6))


def bolt_torque_Nm(bolt_diameter_mm: float, target_load_N: float, nut_factor: float = 0.2) -> float:
    """T = K d F (K ~ 0.2 for lightly lubricated steel; scatter of +-25-30%: use tensioning or measured friction for critical joints)."""
    return nut_factor * bolt_diameter_mm / 1000 * target_load_N

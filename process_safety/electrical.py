"""Electrical safety design: fault levels, cable checks, overcurrent relay grading, earthing (IEEE 80 tolerable voltages), lightning
(rolling sphere), hazardous-area equipment selection (Ex), and arc-flash screening (Lee method with OSHA's applicability limits).

CORROBORATED from public sources (fetched/searched 2026-11-03): Lee equation E = 2.142e6 V Ibf t / D^2 (J/cm2; V in kV, Ibf in kA, t in s,
D in mm) and the 5.02 J/cm2 (1.2 cal/cm2) second-degree-burn threshold; OSHA 1910.269 App. E Table 3 on where the Lee equation is acceptable
(open-air 3-phase to 15 kV; NOT enclosed equipment, NOT above 15 kV); IEEE 80 touch/step formulas and the Cs derating (worked example
Cs = 0.82 reproduced); IEC 60255 inverse-time constants; rolling-sphere radii 20/30/45/60 m. The IEC 62305-2 collection area and
Ng = 0.1 Td, IEC 60364 k-factors, and Ex temperature classes are recalled and flagged. IEEE 1584 empirical arc-flash equations are NOT
implemented: use IEEE 1584-2018 software for enclosed equipment (switchgear, MCCs). Not a substitute for an arc-flash study, a protection
coordination study, an earthing design to IEEE 80/IEC 61936/EN 50522, or a lightning risk assessment to IEC 62305-2.
"""
from __future__ import annotations

from .ranges import validated

import math

# --- short circuit and cable ----------------------------------------------------------------------------------------

def fault_current_kA(V_ll_kV: float, Z_ohm: float) -> float:
    """Balanced three-phase fault current I = V/(sqrt(3) Z) with Z referred to the fault voltage."""
    return V_ll_kV / (math.sqrt(3) * Z_ohm)


def transformer_fault_kA(S_MVA: float, V_ll_kV: float, z_percent: float, source_fault_MVA: float | None = None) -> float:
    """Secondary three-phase fault current of a transformer: I = S/(sqrt3 V (z_t + z_source)) with per-unit impedances on the transformer base.
    source_fault_MVA = upstream fault level (None = infinite bus)."""
    z_pu = z_percent / 100.0
    if source_fault_MVA:
        z_pu += S_MVA / source_fault_MVA
    return S_MVA / (math.sqrt(3) * V_ll_kV * z_pu)


def full_load_current_A(P_kW: float, V_ll_V: float, pf: float, efficiency: float = 1.0, phases: int = 3) -> float:
    k = math.sqrt(3) if phases == 3 else 1.0
    return P_kW * 1000 / (k * V_ll_V * pf * efficiency)


def voltage_drop_pct(I_A, L_km, R_ohm_km, X_ohm_km, pf, V_ll_V, phases=3) -> float:
    """Voltage drop (%) = k I L (R cos phi + X sin phi)/V, k = sqrt(3) (3-phase, V line-to-line) or 2 (single-phase, V line-to-neutral)."""
    sin = math.sqrt(1 - pf * pf)
    k = math.sqrt(3) if phases == 3 else 2.0
    return k * I_A * L_km * (R_ohm_km * pf + X_ohm_km * sin) / V_ll_V * 100


# k in S = I sqrt(t)/k (A s^0.5 / mm2) for the adiabatic short-circuit withstand of conductors, IEC 60364-4-43 style (recalled)
K_ADIABATIC = {("copper", "PVC"): 115, ("copper", "XLPE"): 143, ("aluminium", "PVC"): 76, ("aluminium", "XLPE"): 94}


def min_csa_mm2(I_fault_kA: float, t_s: float, conductor="copper", insulation="XLPE") -> float:
    """Smallest cross-section that withstands a fault of duration t: S >= I sqrt(t)/k."""
    return I_fault_kA * 1000 * math.sqrt(t_s) / K_ADIABATIC[(conductor, insulation)]


def pf_correction_kvar(P_kW: float, pf_from: float, pf_to: float) -> float:
    return P_kW * (math.tan(math.acos(pf_from)) - math.tan(math.acos(pf_to)))


def motor_start_dip_pct(S_start_MVA: float, S_fault_MVA: float) -> float:
    """Approximate voltage dip at the bus on direct-on-line starting: S_start/(S_start + S_fault). Ignores pre-load and cable drop."""
    return S_start_MVA / (S_start_MVA + S_fault_MVA) * 100


# --- overcurrent protection (IEC 60255-151 inverse-time characteristics) -----------------------------------------------

IDMT = {"standard_inverse": (0.14, 0.02), "very_inverse": (13.5, 1.0), "extremely_inverse": (80.0, 2.0), "long_time_inverse": (120.0, 1.0)}


@validated(I_A="current_A", I_pickup_A="current_A", tms="relay_tms")
def idmt_time_s(I_A: float, I_pickup_A: float, tms: float, curve: str = "standard_inverse") -> float:
    """t = TMS k / ((I/Is)^alpha - 1); infinite at or below pickup."""
    k, a = IDMT[curve]
    r = I_A / I_pickup_A
    return float("inf") if r <= 1 else tms * k / (r ** a - 1)


def grading_check(t_upstream_s: float, t_downstream_s: float, margin_s: float = 0.3) -> dict:
    """Discrimination margin between upstream and downstream devices at the same fault current. The margin (typ. 0.3-0.5 s for relay-relay;
    set by relay overshoot, breaker time and CT errors) is a study input."""
    m = t_upstream_s - t_downstream_s
    return {"margin_s": m, "required_s": margin_s, "ok": m >= margin_s}


# --- earthing (IEEE 80-2000 forms) --------------------------------------------------------------------------------------

def rod_resistance_ohm(rho_ohm_m: float, length_m: float, radius_m: float) -> float:
    """Dwight: R = rho/(2 pi L) [ln(4L/a) - 1] for a vertical rod."""
    return rho_ohm_m / (2 * math.pi * length_m) * (math.log(4 * length_m / radius_m) - 1)


def surface_layer_factor(rho_soil: float, rho_surface: float, h_surface_m: float) -> float:
    """Cs = 1 - 0.09 (1 - rho/rho_s)/(2 h_s + 0.09) (IEEE 80-2000). Use Cs = 1 with no surface layer."""
    return 1 - 0.09 * (1 - rho_soil / rho_surface) / (2 * h_surface_m + 0.09)


def tolerable_touch_V(rho_s: float, t_s: float, Cs: float = 1.0, body_kg: int = 50) -> float:
    k = {50: 0.116, 70: 0.157}[body_kg]
    return (1000 + 1.5 * Cs * rho_s) * k / math.sqrt(t_s)


def tolerable_step_V(rho_s: float, t_s: float, Cs: float = 1.0, body_kg: int = 50) -> float:
    k = {50: 0.116, 70: 0.157}[body_kg]
    return (1000 + 6.0 * Cs * rho_s) * k / math.sqrt(t_s)


def ground_potential_rise_V(I_grid_A: float, R_grid_ohm: float) -> float:
    return I_grid_A * R_grid_ohm


# --- lightning (rolling sphere, IEC 62305 style) ------------------------------------------------------------------------

ROLLING_SPHERE_RADIUS_M = {1: 20.0, 2: 30.0, 3: 45.0, 4: 60.0}  # lightning protection level -> radius


def protected_radius_at_ground_m(h_mast_m: float, R_sphere_m: float) -> float:
    """Horizontal protected radius at ground level of a single vertical air terminal: sqrt(h(2R - h)) for h <= R, else R."""
    return math.sqrt(h_mast_m * (2 * R_sphere_m - h_mast_m)) if h_mast_m <= R_sphere_m else R_sphere_m


def protected_radius_at_height_m(h_mast_m: float, z_m: float, R_sphere_m: float) -> float:
    """Protected radius at height z below the tip (h <= R): sqrt(h(2R-h)) - sqrt(z(2R-z)); zero at and above the tip."""
    if z_m >= h_mast_m:
        return 0.0
    return protected_radius_at_ground_m(h_mast_m, R_sphere_m) - math.sqrt(z_m * (2 * R_sphere_m - z_m))


def collection_area_m2(L_m: float, W_m: float, H_m: float) -> float:
    """Equivalent collection area of an isolated structure: L W + 2 (3H)(L + W) + pi (3H)^2 (IEC 62305-2, recalled)."""
    return L_m * W_m + 2 * (3 * H_m) * (L_m + W_m) + math.pi * (3 * H_m) ** 2


def ground_flash_density_from_thunderdays(Td: float) -> float:
    """Ng ~ 0.1 Td per km2 per year when no local data exist (IEC 62305-2, recalled; local flash-counter data are preferred)."""
    return 0.1 * Td


def strikes_per_year(Ng_per_km2_yr: float, collection_area: float, location_factor: float = 1.0) -> float:
    return Ng_per_km2_yr * collection_area * location_factor * 1e-6


# --- hazardous-area equipment ------------------------------------------------------------------------------------------

T_CLASS_MAX_C = {"T1": 450, "T2": 300, "T3": 200, "T4": 135, "T5": 100, "T6": 85}
ZONE_EPL = {0: "Ga", 1: "Gb", 2: "Gc"}


def allowed_t_classes(autoignition_C: float, margin_C: float = 0.0) -> list[str]:
    """T classes whose maximum surface temperature is below the lowest autoignition temperature of the gas (less an optional margin,
    which client specifications often add)."""
    return [k for k, v in T_CLASS_MAX_C.items() if v + margin_C < autoignition_C]


def gas_group_from_mesg(mesg_mm: float) -> str:
    """IIC (MESG <= 0.5 mm, e.g. hydrogen, acetylene), IIB (0.5-0.9 mm, e.g. ethylene), IIA (>= 0.9 mm, e.g. propane, methane)."""
    return "IIC" if mesg_mm <= 0.5 else "IIB" if mesg_mm < 0.9 else "IIA"


def min_epl_for_zone(zone: int) -> str:
    return ZONE_EPL[zone]


# --- arc flash (screening) ---------------------------------------------------------------------------------------------

CAL_PER_J = 1 / 4.184
SECOND_DEGREE_BURN_J_CM2 = 5.02    # 1.2 cal/cm2
OSHA_ASSESSMENT_THRESHOLD_CAL_CM2 = 2.0  # 1910.269 App. E table note


def lee_applicable(voltage_V: float, phases: int, enclosed: bool) -> dict:
    """OSHA 1910.269 App. E Table 3 for the Lee equation: single-phase <= 15 kV only 'with conditions'; three-phase OPEN AIR yes up to 15 kV
    (conditional above 600 V); enclosed three-phase NO; above 15 kV NO."""
    if voltage_V > 15000:
        return {"ok": False, "why": "above 15 kV the Lee equation is not recommended (results extremely conservative)"}
    if enclosed and phases == 3:
        return {"ok": False, "why": "enclosed three-phase equipment (switchgear, MCC, panels): use IEEE 1584"}
    if phases == 1:
        return {"ok": True, "conditional": True, "why": "single-phase: OSHA marks Y-C (conditions apply)"}
    return {"ok": True, "conditional": voltage_V > 600, "why": "open-air three-phase"}


def lee_incident_energy_J_cm2(V_kV: float, Ibf_kA: float, t_s: float, D_mm: float) -> float:
    """E = 2.142e6 V Ibf t / D^2."""
    return 2.142e6 * V_kV * Ibf_kA * t_s / D_mm ** 2


def lee_boundary_mm(V_kV: float, Ibf_kA: float, t_s: float, E_J_cm2: float = SECOND_DEGREE_BURN_J_CM2) -> float:
    """Distance at which the incident energy falls to E (default the 5.02 J/cm2 = 1.2 cal/cm2 second-degree burn onset)."""
    return math.sqrt(2.142e6 * V_kV * Ibf_kA * t_s / E_J_cm2)

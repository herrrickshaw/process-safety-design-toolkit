"""Pressure-relief device sizing: API 520 Part I (gas, steam, liquid), API 521 fire case, API 526 orifice selection.

SI units throughout: kg/h, kPa (ABSOLUTE unless named *_g), K, mm2, kg/kmol.

The gas/liquid equations are derived from isentropic orifice flow rather than copied as lumped constants; the tests check that
they reproduce the API 520 SI constants (13160, 17.9, 11.78, 190.5), which is the cross-check that the derivation is right.
The standards text itself is paywalled and was not read: confirm coefficients, Kd and the F-factor against your edition.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

R = 8.314462618  # J/mol/K
ATM = 101.325    # kPa

# ASME VIII / API 520 allowable accumulation as fraction of set pressure (gauge) - secondary-source figures, verify.
ACCUMULATION = {"single_non_fire": 0.10, "multiple_non_fire": 0.16, "fire": 0.21}

# API 526 standard effective orifice areas, in2 -> mm2
_API526_IN2 = {"D": 0.110, "E": 0.196, "F": 0.307, "G": 0.503, "H": 0.785, "J": 1.287, "K": 1.838, "L": 2.853,
               "M": 3.60, "N": 4.34, "P": 6.38, "Q": 11.05, "R": 16.00, "T": 26.00}
API526_ORIFICES_MM2 = {k: v * 645.16 for k, v in _API526_IN2.items()}


@dataclass
class ReliefResult:
    required_area_mm2: float
    orifice: str | None
    n_valves: int
    regime: str
    notes: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)


def relieving_pressure_kpa(set_g_kpa: float, case: str = "single_non_fire") -> float:
    """Absolute relieving pressure = set pressure (gauge) x (1 + accumulation) + atmospheric."""
    return set_g_kpa * (1 + ACCUMULATION[case]) + ATM


def select_orifice(area_mm2: float) -> tuple[str | None, int]:
    """Smallest single API 526 orifice >= area; if none, the number of 'T' valves needed."""
    for letter, a in sorted(API526_ORIFICES_MM2.items(), key=lambda kv: kv[1]):
        if a >= area_mm2:
            return letter, 1
    n = math.ceil(area_mm2 / API526_ORIFICES_MM2["T"])
    return "T", n


def _finish(area, regime, notes, detail) -> ReliefResult:
    orifice, n = select_orifice(area)
    return ReliefResult(area, orifice, n, regime, notes, detail)


def gas_mass_flux(P1_kpa, P2_kpa, T_K, M, k, Z=1.0) -> tuple[float, str]:
    """Ideal isentropic orifice mass flux G (kg/m2/s) and regime ('critical'/'subcritical'); P1/P2 kPa abs, M kg/kmol."""
    r = P2_kpa / P1_kpa
    rc = (2 / (k + 1)) ** (k / (k - 1))
    P1 = P1_kpa * 1e3
    if r <= rc:
        return P1 * math.sqrt(k * (M / 1000) / (Z * R * T_K)) * (2 / (k + 1)) ** ((k + 1) / (2 * (k - 1))), "critical"
    rho1 = P1 * (M / 1000) / (Z * R * T_K)
    return math.sqrt(2 * P1 * rho1 * (k / (k - 1)) * (r ** (2 / k) - r ** ((k + 1) / k))), "subcritical"


def gas_area(W_kg_h, T_K, P1_kpa, P2_kpa, M, k, Z=1.0, Kd=0.975, Kb=1.0, Kc=1.0,
             set_g_kpa: float | None = None, valve: str = "conventional") -> ReliefResult:
    """API 520-I gas/vapour sizing. P1 = relieving pressure, P2 = total back pressure (both kPa abs).
    Critical vs subcritical flow is chosen from P2/P1. Kb applies to balanced-bellows valves in critical flow only."""
    notes = []
    r = P2_kpa / P1_kpa
    rc = (2 / (k + 1)) ** (k / (k - 1))
    G, regime = gas_mass_flux(P1_kpa, P2_kpa, T_K, M, k, Z)
    if regime == "critical":
        kb = Kb
    else:
        kb = 1.0  # back-pressure effect is already in the subcritical flux
        if valve == "conventional" and set_g_kpa and (P2_kpa - ATM) > 0.10 * set_g_kpa:
            notes.append("conventional valve with built-up back pressure > 10% of set: consider balanced bellows or pilot (API 520-II)")
    A = W_kg_h / 3600 / (Kd * kb * Kc * G) * 1e6
    return _finish(A, regime, notes, {"G_kg_m2_s": G, "pressure_ratio": r, "critical_ratio": rc, "Kd": Kd, "Kb": kb, "Kc": Kc})


def steam_area(W_kg_h, P1_kpa, Ksh=1.0, Kd=0.975, Kb=1.0, Kc=1.0) -> ReliefResult:
    """API 520-I steam (Napier). Ksh = 1 for saturated steam; take superheat factor from API 520 table for superheated."""
    notes = []
    if P1_kpa <= 10339:
        Kn = 1.0
    elif P1_kpa <= 22060:
        Kn = (0.02764 * P1_kpa - 1000) / (0.03324 * P1_kpa - 1061)
    else:
        raise ValueError("Napier correction not defined above 22 060 kPa abs (API 520)")
    if Ksh == 1.0:
        notes.append("Ksh=1 assumes saturated steam")
    A = 190.5 * W_kg_h / (P1_kpa * Kd * Kb * Kc * Kn * Ksh)
    return _finish(A, "napier", notes, {"Kn": Kn})


def liquid_area(Q_m3_h, rho, P1_kpa, P2_kpa, mu_cP=1.0, Kd=0.65, Kw=1.0, Kc=1.0) -> ReliefResult:
    """API 520-I liquid sizing with iterative viscosity correction Kv (valid Re >= 100)."""
    dP = (P1_kpa - P2_kpa) * 1e3
    if dP <= 0:
        raise ValueError("P1 must exceed P2")
    Q = Q_m3_h / 3600
    base = Q * math.sqrt(rho / (2 * dP)) * 1e6  # mm2 for Kd=Kw=Kc=Kv=1
    Kv, Re = 1.0, float("inf")
    for _ in range(50):
        A = base / (Kd * Kw * Kc * Kv)
        Re = 2 * Q * rho / ((mu_cP * 1e-3) * math.sqrt(math.pi * A * 1e-6))
        kv_new = 1.0 if Re > 1e7 else min(1.0, 1 / (0.9935 + 2.878 / Re ** 0.5 + 342.75 / Re ** 1.5))
        if abs(kv_new - Kv) < 1e-9:
            break
        Kv = kv_new
    notes = ["Re < 100: Kv correlation out of range; use API 520 guidance"] if Re < 100 else []
    return _finish(base / (Kd * Kw * Kc * Kv), "liquid", notes, {"Kv": Kv, "Re": Re})


# --- API 521 external fire -------------------------------------------------------------------------------------------

def wetted_area_cylinder(D, L, level, orientation="horizontal", elevation_above_grade=0.0, max_height=7.6) -> float:
    """Approximate wetted area (m2) of a cylindrical vessel with 2:1 elliptical heads, only the part within
    max_height (API 521: 7.6 m) of the fire source. level = liquid height from the vessel bottom (m).
    Head areas are approximated; use the vessel drawing for a final value."""
    head = 1.084 * D * D  # surface of a 2:1 ellipsoidal head
    cap = max(0.0, max_height - elevation_above_grade)
    if orientation == "vertical":
        h = min(level, cap)
        return math.pi * D * h + (head if h > 0 else 0.0)
    h = min(level, D, cap)
    if h <= 0:
        return 0.0
    theta = 2 * math.acos(1 - 2 * h / D)
    seg = (D * D / 8) * (theta - math.sin(theta))  # wetted cross-section segment, m2
    frac = seg / (math.pi * D * D / 4)
    return L * D * theta / 2 + 2 * head * frac


def fire_heat_input_W(A_wet_m2, F=1.0, adequate_drainage_and_firefighting=True) -> float:
    """API 521 liquid-wetted: Q = C F A^0.82, C = 43 200 W (drainage + prompt fire fighting) or 70 900 W (otherwise).
    F = environment factor (1.0 for a bare vessel; insulation credit must be justified per API 521)."""
    C = 43_200 if adequate_drainage_and_firefighting else 70_900
    return C * F * A_wet_m2 ** 0.82


def fire_relief_rate_kg_h(A_wet_m2, latent_heat_kJ_kg, F=1.0, adequate_drainage_and_firefighting=True) -> float:
    return fire_heat_input_W(A_wet_m2, F, adequate_drainage_and_firefighting) * 3.6 / latent_heat_kJ_kg


# --- scenario governing-case helper ------------------------------------------------------------------------------------

def governing_case(cases: dict[str, ReliefResult]) -> tuple[str, ReliefResult]:
    """Largest required area governs (API 521 workflow: size for every credible scenario, take the maximum)."""
    name = max(cases, key=lambda n: cases[n].required_area_mm2)
    return name, cases[name]

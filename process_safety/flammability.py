"""Flammability, inerting and ignition-control arithmetic: Le Chatelier LFL/UFL, limiting oxygen concentration, purge calculations,
static-charge relaxation, and the zone-by-release-duration rule of thumb.

LFL/UFL values per fuel are INPUTS (take them from a data source); the stoichiometric z uses the element balance of the formula.
Inerting targets (a margin below LOC) and the v.d charging limit are client/standard criteria (NFPA 69, API 2003, OISD-RP-110):
pass the one you are required to apply. Zone thresholds are informative, not a classification.
"""
from __future__ import annotations

import math
import re

EPS0 = 8.8541878128e-12


def le_chatelier(fractions: list[float], limits: list[float]) -> float:
    """Mixture limit (vol%) = 1/sum(y_i/L_i), y_i the mole fractions of the COMBUSTIBLE components (sum normalised to 1)."""
    s = sum(fractions)
    return 1 / sum((y / s) / L for y, L in zip(fractions, limits))


def oxygen_stoich_z(formula: str) -> float:
    """Moles O2 per mole of fuel for complete combustion of CxHyOz (z = x + y/4 - o/2)."""
    el = {k: float(n) if n else 1.0 for k, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula)}
    return el.get("C", 0) + el.get("H", 0) / 4 - el.get("O", 0) / 2


def loc_vol_pct(lfl_vol_pct: float, formula: str) -> float:
    """Zabetakis/CCPS estimate LOC ~ z x LFL (vol% O2). Prefer measured LOC for the inert gas actually used."""
    return oxygen_stoich_z(formula) * lfl_vol_pct


def sweep_through_conc(C0: float, C_in: float, Q_m3_h: float, t_h: float, V_m3: float) -> float:
    """Well-mixed sweep purge: C = C_in + (C0 - C_in) exp(-Q t/V)."""
    return C_in + (C0 - C_in) * math.exp(-Q_m3_h * t_h / V_m3)


def sweep_through_time_h(C0: float, C_target: float, C_in: float, Q_m3_h: float, V_m3: float) -> float:
    return V_m3 / Q_m3_h * math.log((C0 - C_in) / (C_target - C_in))


def pressure_purge_cycles(y0: float, y_target: float, P_high_kpa: float, P_low_kpa: float) -> int:
    """Pressurise with pure inert to P_high, vent to P_low: y_n = y0 (P_low/P_high)^n; same form for vacuum purge (P_high = atmosphere)."""
    return math.ceil(math.log(y_target / y0) / math.log(P_low_kpa / P_high_kpa) - 1e-12)


def relaxation_time_s(conductivity_S_m: float, eps_r: float = 2.0) -> float:
    """Charge relaxation time tau = eps0 eps_r / kappa (hydrocarbons eps_r ~ 2). Low-conductivity liquids (< ~50 pS/m) relax slowly."""
    return EPS0 * eps_r / conductivity_S_m


def pipe_charging_check(v_m_s: float, d_m: float, vd_limit_m2_s: float = 0.5) -> dict:
    """Velocity-diameter screening for low-conductivity liquid filling/pipework (commonly quoted limit v.d <= 0.5 m2/s; confirm criterion)."""
    return {"v_times_d_m2_s": v_m_s * d_m, "limit": vd_limit_m2_s, "ok": v_m_s * d_m <= vd_limit_m2_s}


def zone_from_release_hours(hours_per_year: float) -> str:
    """Informative duration rule often quoted from IP/EI 15: >=1000 h/y Zone 0; 10-1000 Zone 1; <10 Zone 2 (negligible releases excluded)."""
    return "Zone 0" if hours_per_year >= 1000 else "Zone 1" if hours_per_year >= 10 else "Zone 2"

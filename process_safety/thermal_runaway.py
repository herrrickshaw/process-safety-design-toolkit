"""Thermal runaway screening: time to maximum rate under adiabatic conditions (TMRad), TD24, Stoessel criticality class, and the
Semenov critical ambient temperature for storage / hold-up. Extends reaction_hazard.py (dT_ad, MTSR).

Zero-order Arrhenius heat release fitted to one calorimetry point (q_ref at T_ref) and an activation energy:
    q(T) = q_ref exp(-Ea/R (1/T - 1/T_ref))                        [W/kg]
    TMRad(T0) = cp R T0^2 / (q(T0) Ea)                              [s]   (Semenov approximation, zero order, adiabatic)
    TD24: TMRad(TD24) = 24 h (bisection)
Stoessel criticality classes (TU Masaryk lecture notes / TUV SUD Schweiz EPSC 2020 award lecture; cooling-failure scenario):
    1  MTSR < MTT, MTT <= TD24      (MTSR below TD24)
    2  MTSR < MTT, TD24 < MTT       (MTSR below TD24)
    3  MTT <= MTSR < TD24
    4  MTT < TD24 <= MTSR
    5  TD24 <= MTSR and TD24 <= MTT (decomposition triggered on loss of control)
Semenov (lumped mass m, cooling U A to ambient Ta): the critical ambient is reached when the generation curve m q(T) touches the
cooling line U A (T - Ta): solve m q(T) Ea/(R T^2) = U A for T_NR, then Ta,crit = T_NR - m q(T_NR)/(U A) (~ T_NR - R T_NR^2/Ea).
Inputs come from DSC / ARC / RC1 work; zero-order kinetics over-predicts TMRad for autocatalytic decompositions.
"""
from __future__ import annotations

import math

R = 8.314462618


def q_W_kg(T_K: float, q_ref_W_kg: float, T_ref_K: float, Ea_J_mol: float) -> float:
    return q_ref_W_kg * math.exp(-Ea_J_mol / R * (1 / T_K - 1 / T_ref_K))


def tmr_ad_s(T0_K: float, cp_J_kgK: float, q_ref_W_kg: float, T_ref_K: float, Ea_J_mol: float) -> float:
    return cp_J_kgK * R * T0_K ** 2 / (q_W_kg(T0_K, q_ref_W_kg, T_ref_K, Ea_J_mol) * Ea_J_mol)


def td_hours_K(hours: float, cp_J_kgK: float, q_ref_W_kg: float, T_ref_K: float, Ea_J_mol: float) -> float:
    target = hours * 3600
    lo, hi = 150.0, 1200.0
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if tmr_ad_s(mid, cp_J_kgK, q_ref_W_kg, T_ref_K, Ea_J_mol) > target else (lo, mid)
    return (lo + hi) / 2


def stoessel_class(MTSR: float, MTT: float, TD24: float) -> int:
    if MTSR >= TD24:
        return 4 if MTT < TD24 else 5
    if MTSR < MTT:
        return 1 if MTT <= TD24 else 2
    return 3


CLASS_GUIDANCE = {1: "Low risk: no special measures beyond normal; avoid long heat accumulation.",
                  2: "Low risk if not held long under heat accumulation; ensure MTT barrier (e.g. evaporative cooling) works.",
                  3: "Critical: safety relies on the technical limit at MTT (boiling / relief); size it for the synthesis rate at MTT.",
                  4: "Critical: secondary reaction may be triggered; technical measures (relief / emergency cooling / quench) needed.",
                  5: "Inherently unsafe on loss of control: redesign (semi-batch, lower accumulation) or emergency measures."}


def semenov_critical_ambient_K(mass_kg: float, UA_W_K: float, q_ref_W_kg: float, T_ref_K: float, Ea_J_mol: float) -> dict:
    f = lambda T: mass_kg * q_W_kg(T, q_ref_W_kg, T_ref_K, Ea_J_mol) * Ea_J_mol / (R * T * T) - UA_W_K
    lo, hi = 150.0, 1500.0
    if f(lo) > 0:
        return {"T_no_return_K": lo, "Ta_critical_K": None, "note": "self-heating already exceeds cooling at 150 K - check inputs"}
    for _ in range(200):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if f(mid) > 0 else (mid, hi)
    T = (lo + hi) / 2
    return {"T_no_return_K": T, "Ta_critical_K": T - mass_kg * q_W_kg(T, q_ref_W_kg, T_ref_K, Ea_J_mol) / UA_W_K,
            "Ta_critical_approx_K": T - R * T * T / Ea_J_mol}


def assess(case: dict) -> dict:
    """case = {"T_process_C", "dT_ad_K", "accumulation", "MTT_C", "cp_J_kgK", "q_ref_W_kg", "T_ref_C", "Ea_kJ_mol",
               optional TD24_C (measured, overrides the fit), storage: {mass_kg, UA_W_K, T_ambient_C}}"""
    mtsr = case["T_process_C"] + case.get("accumulation", 1.0) * case["dT_ad_K"]
    Ea = case["Ea_kJ_mol"] * 1e3
    Tref = case["T_ref_C"] + 273.15
    td24 = case.get("TD24_C")
    if td24 is None:
        td24 = td_hours_K(24, case["cp_J_kgK"], case["q_ref_W_kg"], Tref, Ea) - 273.15
    tmr_at_mtsr = tmr_ad_s(mtsr + 273.15, case["cp_J_kgK"], case["q_ref_W_kg"], Tref, Ea) / 3600
    cls = stoessel_class(mtsr, case["MTT_C"], td24)
    out = {"MTSR_C": mtsr, "TD24_C": td24, "TD8_C": td_hours_K(8, case["cp_J_kgK"], case["q_ref_W_kg"], Tref, Ea) - 273.15,
           "TMRad_at_MTSR_h": tmr_at_mtsr, "MTT_C": case["MTT_C"], "criticality_class": cls, "guidance": CLASS_GUIDANCE[cls]}
    if "storage" in case:
        st = case["storage"]
        sm = semenov_critical_ambient_K(st["mass_kg"], st["UA_W_K"], case["q_ref_W_kg"], Tref, Ea)
        out["storage"] = {**sm, "Ta_critical_C": None if sm["Ta_critical_K"] is None else sm["Ta_critical_K"] - 273.15,
                          "T_ambient_C": st.get("T_ambient_C"),
                          "margin_K": None if sm["Ta_critical_K"] is None or st.get("T_ambient_C") is None else sm["Ta_critical_K"] - 273.15 - st["T_ambient_C"]}
    return out

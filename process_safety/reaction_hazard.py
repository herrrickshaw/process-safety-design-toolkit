"""Reaction-hazard screening basics for chemicals/pharma: adiabatic temperature rise and MTSR (Stoessel-style).

dT_ad = (-dHr) c / (rho cp); MTSR = Tprocess + X_accumulated x dT_ad. Comparing MTSR with the boiling point, the maximum technical
temperature and the decomposition onset (TD24) requires calorimetry (DSC/ARC/RC1): this module does only the arithmetic and the
comparison flags. Full criticality classification, runaway vent sizing (DIERS) and dust-explosion vent design are NOT implemented.
"""
from __future__ import annotations


def adiabatic_temperature_rise_K(delta_H_kJ_mol: float, conc_mol_L: float, rho_kg_m3: float, cp_kJ_kgK: float) -> float:
    """dH is the reaction enthalpy per mole of limiting reactant, negative for exothermic (sign handled: heat = -dH)."""
    heat_kJ_m3 = -delta_H_kJ_mol * conc_mol_L * 1000.0
    return heat_kJ_m3 / (rho_kg_m3 * cp_kJ_kgK)


def mtsr_C(T_process_C: float, dT_ad_K: float, accumulation_fraction: float) -> float:
    """Maximum temperature of the synthesis reaction if cooling fails with `accumulation_fraction` (0-1) of the reagent unreacted."""
    return T_process_C + accumulation_fraction * dT_ad_K


def screen(T_process_C, dT_ad_K, accumulation_fraction, T_boiling_C, MTT_C, TD24_C) -> dict:
    m = mtsr_C(T_process_C, dT_ad_K, accumulation_fraction)
    flags = []
    if m > MTT_C:
        flags.append("MTSR exceeds MTT: containment/relief must handle the runaway")
    if m > T_boiling_C:
        flags.append("MTSR above boiling point: solvent boil-off pressurisation")
    if m > TD24_C:
        flags.append("MTSR above TD24: secondary decomposition possible within 24 h")
    return {"MTSR_C": m, "flags": flags or ["MTSR below MTT, boiling point and TD24 (subject to calorimetry quality)"]}

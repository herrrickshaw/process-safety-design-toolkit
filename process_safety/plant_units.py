"""Unit-specific arithmetic for refineries and chemical plants: furnace purge time, peroxide decomposition load, hydroprocessing/exotherm rise.

First-principles bookkeeping only; the safe numbers (purge volume changes, catalyst limits, decomposition kinetics) are project data.
"""
from __future__ import annotations

M_H2O2 = 34.0147
M_O2 = 31.998
LATENT_WATER_kJ_kg = 2257.0
DH_DECOMP_kJ_mol = 98.2  # H2O2(l) -> H2O(l) + 1/2 O2(g), recalled; exothermic


def furnace_purge_time_s(firebox_volume_m3: float, purge_flow_m3_s: float, volume_changes: float = 5.0) -> float:
    """Pre-ignition purge: t = N V/Q. N (commonly 4-5 volume changes) and the minimum flow are set by NFPA 86/85 / API 556 or the
    heater vendor: confirm; also count the convection section and stack volume."""
    return volume_changes * firebox_volume_m3 / purge_flow_m3_s


def h2o2_decomposition(rate_kg_h_pure: float, solution_wt_fraction: float = 1.0) -> dict:
    """Gas and heat from decomposition of `rate_kg_h_pure` of PURE H2O2 per hour (diluted stock: the water is a heat sink). Returns the
    oxygen mass flow, heat release, and the steam that the heat could boil off if the water were at its boiling point: an UPPER bound on
    the vent load (O2 + steam). Two-phase flow, catalytic acceleration and tank vent sizing need DIERS methods, not covered."""
    mol_h = rate_kg_h_pure * 1000 / M_H2O2
    o2_kg_h = mol_h * 0.5 * M_O2 / 1000
    heat_kW = mol_h * DH_DECOMP_kJ_mol / 3600
    steam_kg_h = heat_kW * 3600 / LATENT_WATER_kJ_kg
    return {"o2_kg_h": o2_kg_h, "o2_per_kg_h2o2": o2_kg_h / rate_kg_h_pure, "heat_kW": heat_kW, "max_steam_kg_h": steam_kg_h,
            "solution_wt_fraction": solution_wt_fraction}


def adiabatic_rise_K(heat_released_kJ_per_kg_feed: float, cp_kJ_kgK: float) -> float:
    """Generic adiabatic temperature rise of a bed or batch for a given heat release per kg of feed (hydrogenation, hydrocracking,
    polymerisation, decomposition)."""
    return heat_released_kJ_per_kg_feed / cp_kJ_kgK


def hydrogenation_heat_kJ_kg_feed(h2_consumption_nm3_per_m3_feed: float, feed_density_kg_m3: float, dH_kJ_per_mol_H2: float) -> float:
    """Heat release from chemical hydrogen consumption (Nm3 H2 per m3 feed at 0 C, 1 atm: 22.414 L/mol). dH per mole H2 is a process-specific input."""
    mol_per_m3 = h2_consumption_nm3_per_m3_feed * 1000 / 22.414
    return mol_per_m3 * dH_kJ_per_mol_H2 / feed_density_kg_m3

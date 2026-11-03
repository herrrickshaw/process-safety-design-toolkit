"""LNG: boil-off, impoundment capacity (49 CFR 193), regasification duty, ideal liquefaction work, siting criteria and screening.

VERIFIED from the primary text (49 CFR 193.2181 impoundment capacity; 193.2059 dispersion parameters, fetched from Cornell LII 2026-11-03).
The 49 CFR 193 siting analyses themselves require specific validated models (GTI LNGFIRE3 thermal radiation; DEGADIS or equivalent dense-gas
dispersion; NFPA 59A design spill) that are NOT reproduced here. This package's neutral-gas Gaussian screening ignores cold dense-gas slumping and is
unreliable for LNG vapour clouds (the error can go either way): never use it for a siting submission. Methane properties are recalled values (+-3%);
use project data for real LNG compositions.
"""
from __future__ import annotations

import math

from . import props

# methane defaults at 1 atm (kJ/kg, kJ/kg/K, K): latent heat at the boiling point, liquid and gas cp, net heating value (MJ/kg)
METHANE = {"latent_kJ_kg": 510.0, "cp_liq": 3.5, "cp_gas": 2.2, "Tb_K": 111.66, "lhv_MJ_kg": 50.0}

# 49 CFR 193.2059 dispersion parameters (verified from the text)
DISPERSION_RULE = {"average_concentration_vol_pct": 2.5, "receptor_height_m": 0.5, "surface_roughness_m": 0.03, "stability": "F",
                   "wind_speed_m_s": 2.01, "relative_humidity_pct": 50.0}


def impoundment_capacity_m3(tank_capacities_m3: list[float], surge_accounted: bool = False) -> float:
    """49 CFR 193.2181: single tank 110% of its maximum liquid capacity; several tanks the greater of 100% of all or 110% of the
    largest; the single-tank factor may be 100% if the dike is designed for a catastrophic-failure surge."""
    if len(tank_capacities_m3) == 1:
        return tank_capacities_m3[0] * (1.0 if surge_accounted else 1.10)
    return max(sum(tank_capacities_m3), 1.10 * max(tank_capacities_m3))


def boil_off_rate_kg_s(heat_ingress_kW: float, latent_kJ_kg: float = METHANE["latent_kJ_kg"]) -> float:
    return heat_ingress_kW / latent_kJ_kg


def boil_off_pct_per_day(heat_ingress_kW: float, tank_volume_m3: float, liquid_density=422.0, latent_kJ_kg=METHANE["latent_kJ_kg"],
                         fill_fraction=1.0) -> float:
    mass = tank_volume_m3 * fill_fraction * liquid_density
    return boil_off_rate_kg_s(heat_ingress_kW, latent_kJ_kg) * 86400 / mass * 100


def regas_duty_kW(mass_kg_s: float, T_in_K: float, T_out_K: float, p=METHANE) -> float:
    """Heat to warm liquid to its boiling point, vaporise, and superheat to T_out (atmospheric-pressure properties; at send-out pressure the
    latent heat is lower, so this is conservative for high-pressure regasification)."""
    return mass_kg_s * (p["cp_liq"] * max(p["Tb_K"] - T_in_K, 0) + p["latent_kJ_kg"] + p["cp_gas"] * (T_out_K - p["Tb_K"]))


def seawater_flow_m3_s(duty_kW: float, delta_T_K: float, cp_kJ_kgK: float = 3.99, rho: float = 1025.0) -> float:
    """Seawater flow for an open-rack vaporiser given the permitted seawater temperature drop (an environmental-permit input)."""
    return duty_kW / (cp_kJ_kgK * delta_T_K) / rho


def scv_fuel_gas_kg_s(duty_kW: float, efficiency: float = 0.98, lhv_MJ_kg: float = METHANE["lhv_MJ_kg"]) -> float:
    """Submerged-combustion vaporiser fuel consumption; the efficiency is an input (vendor data)."""
    return duty_kW / (efficiency * lhv_MJ_kg * 1000)


def ideal_liquefaction_work_kJ_kg(T_feed_K: float = 300.0, p=METHANE, T_ambient_K: float | None = None) -> float:
    """Minimum (reversible) work to cool an ideal-gas feed at ~1 atm from T_feed to the boiling point and condense it, rejecting heat at
    ambient: W = integral (T0/T - 1) dQ. A LOWER BOUND for a 1 atm feed; real plants liquefy pressurised feed with mixed refrigerants and are
    a multiple of this. Not a plant efficiency benchmark."""
    T0 = T_ambient_K or T_feed_K
    Tb = p["Tb_K"]
    sensible = p["cp_gas"] * (T0 * math.log(T_feed_K / Tb) - (T_feed_K - Tb))
    latent = p["latent_kJ_kg"] * (T0 / Tb - 1)
    return sensible + latent


def kWh_per_tonne(work_kJ_kg: float) -> float:
    """kJ/kg -> kWh per tonne (x 1000 kg/t / 3600 kJ/kWh)."""
    return work_kJ_kg * 1000 / 3600

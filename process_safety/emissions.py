"""Combustion and flaring emissions arithmetic (GHG and unburned hydrocarbon), by element balance.

Stoichiometry is exact; combustion efficiency, GWP and fuel composition are inputs (use your reporting protocol's values, e.g. flare
efficiency 98% is a common default, GWP per the IPCC assessment your regulator specifies). Not an EIA or dispersion study.
"""
from __future__ import annotations

import re

ATOMIC = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007, "S": 32.06}
M_CO2 = 44.009


def molar_mass(formula: str) -> float:
    return sum(ATOMIC[el] * (int(n) if n else 1) for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula))


def co2_per_kg_fuel(formula: str) -> float:
    """kg CO2 per kg of a pure compound burned completely, e.g. 'CH4' -> 2.74."""
    n_c = sum(int(n) if n else 1 for el, n in re.findall(r"([A-Z][a-z]?)(\d*)", formula) if el == "C")
    return n_c * M_CO2 / molar_mass(formula)


def co2_from_mixture_kg(mass_kg: float, carbon_mass_fraction: float) -> float:
    return mass_kg * carbon_mass_fraction * M_CO2 / ATOMIC["C"]


def flare_emissions(gas_kg: float, carbon_mass_fraction: float, combustion_efficiency: float = 0.98, gwp_unburned: float = 28.0,
                    unburned_is_methane: bool = True) -> dict:
    """Carbon burned (efficiency) -> CO2; the unburned fraction is emitted as hydrocarbon (treated as methane for CO2e if requested)."""
    co2 = co2_from_mixture_kg(gas_kg * combustion_efficiency, carbon_mass_fraction)
    unburned = gas_kg * (1 - combustion_efficiency)
    co2e = co2 + (unburned * gwp_unburned if unburned_is_methane else 0.0)
    return {"co2_kg": co2, "unburned_hc_kg": unburned, "co2e_kg": co2e}


def sox_from_sulfur_kg(fuel_kg: float, sulfur_mass_fraction: float, conversion_to_so2: float = 1.0) -> float:
    """SO2 mass (S + O2 -> SO2: 64.06/32.06 per kg S)."""
    return fuel_kg * sulfur_mass_fraction * conversion_to_so2 * (ATOMIC["S"] + 2 * ATOMIC["O"]) / ATOMIC["S"]

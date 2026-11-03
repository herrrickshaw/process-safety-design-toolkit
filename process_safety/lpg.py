"""LPG / light-hydrocarbon storage arithmetic: vapour pressure, liquid density, maximum filling ratio, refrigerated boil-off.

Built on `props` (Lee-Kesler, Rackett). Filling limit: fill the tank so that, after the liquid warms from the filling temperature to the
design maximum temperature and expands, it just stays below liquid-full: f_max = rho_L(T_fill)/rho_L(T_max)... equivalently
f_max = rho(Tmax)/rho(Tfill) (the fraction of volume that may be liquid at the fill temperature). A further margin (and the codes, e.g.
API 2510 / OISD-STD-144/150 / IS 2825, set the practical limit): this is only the thermodynamic ceiling.
"""
from __future__ import annotations

from . import props


def max_fill_fraction(component: str, T_fill_K: float, T_max_K: float) -> float:
    return props.liquid_density_kg_m3(component, T_max_K) / props.liquid_density_kg_m3(component, T_fill_K)


def vapour_pressure_kPag(component: str, T_K: float) -> float:
    return props.vapour_pressure_bar(component, T_K) * 100 - 101.325


def design_pressure_for_max_temperature_kPag(component: str, T_max_K: float, margin: float = 1.0) -> float:
    """Gauge vapour pressure at the maximum design temperature (x margin): the starting point for the storage design pressure of a
    pressurised vessel (propane/butane mixtures need composition-specific data)."""
    return vapour_pressure_kPag(component, T_max_K) * margin


def liquid_mass_kg(component: str, volume_m3: float, T_K: float, fill_fraction: float) -> float:
    return volume_m3 * fill_fraction * props.liquid_density_kg_m3(component, T_K)


def refrigerated_boil_off_kg_s(heat_ingress_kW: float, component: str = "propane", latent_kJ_kg: float = 425.0) -> float:
    """Boil-off of a refrigerated tank at its boiling point (latent heat default for propane ~425 kJ/kg at the normal boiling point: recalled)."""
    return heat_ingress_kW / latent_kJ_kg

"""Data-centre engineering arithmetic that reuses the process-safety toolkit: cooling-water heat balance, PUE, evaporative water use,
battery and diesel backup sizing, redundancy availability, and a generic HAZID prompt list.

All numbers a project must own are inputs (efficiencies, ageing, specific fuel consumption, redundancy topology). Nothing here reproduces
Uptime Institute tier percentages, ASHRAE thermal envelopes or NFPA 75/76/2001 design values: those documents were not read, so they
are not coded. Independence of units is assumed in the availability helpers (no common cause), which overstates availability.
"""
from __future__ import annotations

from . import reliability

HOURS_PER_YEAR = 8760.0
MJ_PER_KWH = 3.6


def pue(total_facility_kw: float, it_kw: float) -> float:
    """Power usage effectiveness = total facility power / IT power (>= 1)."""
    if it_kw <= 0 or total_facility_kw < it_kw:
        raise ValueError("need it_kw > 0 and total_facility_kw >= it_kw")
    return total_facility_kw / it_kw


def cooling_water_flow_m3_h(heat_kw: float, delta_t_k: float, cp_kj_kg_k: float = 4.18, rho_kg_m3: float = 1000.0) -> float:
    """Chilled/cooling water flow to carry a heat load: m = Q / (cp dT). Use hydraulics.* for the pipe and pump."""
    if delta_t_k <= 0:
        raise ValueError("delta_t_k must be > 0")
    kg_s = heat_kw / (cp_kj_kg_k * delta_t_k)
    return kg_s / rho_kg_m3 * 3600.0


def evaporative_water_l_per_kwh_it(heat_rejected_kwh_per_kwh_it: float, cycles_of_concentration: float, evap_fraction: float = 0.85,
                                   latent_mj_kg: float = 2.43) -> float:
    """Open evaporative tower make-up water per kWh of IT load, including blowdown at the given cycles of concentration.

    evaporated = heat * evap_fraction * 3.6 MJ/kWh / latent heat (kg == L); make-up = evaporated * C / (C - 1).
    latent_mj_kg 2.43 is water near 30 C; heat rejected is IT heat plus the cooling plant's own work (an input, ~1.16 for a water-cooled plant).
    """
    if cycles_of_concentration <= 1:
        raise ValueError("cycles_of_concentration must be > 1")
    evaporated = heat_rejected_kwh_per_kwh_it * evap_fraction * MJ_PER_KWH / latent_mj_kg
    return evaporated * cycles_of_concentration / (cycles_of_concentration - 1)


def battery_energy_kwh(load_kw: float, autonomy_min: float, inverter_efficiency: float, usable_dod: float, ageing_factor: float = 1.0) -> float:
    """Nameplate battery energy for a UPS autonomy: E = P t / (eta * usable DoD) * ageing factor (>= 1 for end-of-life margin)."""
    for name, v in (("inverter_efficiency", inverter_efficiency), ("usable_dod", usable_dod)):
        if not 0 < v <= 1:
            raise ValueError(f"{name} must be in (0, 1]")
    return load_kw * autonomy_min / 60.0 / (inverter_efficiency * usable_dod) * ageing_factor


def diesel_storage_m3(load_kw: float, hours: float, sfc_g_per_kwh: float, density_kg_m3: float = 840.0, reserve_fraction: float = 0.0) -> float:
    """On-site diesel volume for a number of hours at a generator electrical load. sfc is vendor data (no default); density default is a typical diesel value."""
    if sfc_g_per_kwh <= 0:
        raise ValueError("sfc_g_per_kwh is vendor data and must be > 0")
    kg = load_kw * hours * sfc_g_per_kwh / 1000.0
    return kg / density_kg_m3 * (1.0 + reserve_fraction)


def k_of_n_availability(k_required: int, n: int, unit_availability: float) -> float:
    """N, N+1, N+2 style capacity redundancy: system works if at least k of n identical independent units work."""
    return 1.0 - reliability.koon_failure_probability(k_required, n, 1.0 - unit_availability)


def dual_path_availability(path_component_availabilities: list[list[float]]) -> float:
    """2N style: each path is a series of components; the site works if any path works (independent paths)."""
    return reliability.parallel_availability([reliability.series_availability(p) for p in path_component_availabilities])


def downtime_h_per_year(availability: float) -> float:
    return (1.0 - availability) * HOURS_PER_YEAR


# Generic checklist to seed a HAZID/HAZOP, not a study: every line needs project data, and the standard text governs.
HAZID_PROMPTS = [
    {"area": "Diesel generators and fuel storage", "hazard": "Fuel leak, pool fire, tank overfill, static during filling", "toolkit": "pool_fire, overfill, flammability, qra.effects", "note": "PESO licensing applies in India"},
    {"area": "UPS battery rooms", "hazard": "Thermal runaway (Li-ion), hydrogen from lead-acid charging, toxic or flammable gas build-up", "toolkit": "thermal_runaway, flammability, atex", "note": "chemistry-specific data required"},
    {"area": "Gas suppression rooms", "hazard": "Agent discharge, over-pressure, asphyxiation/decomposition products, false discharge", "toolkit": "none (NFPA 2001 / ISO 14520 not read)", "note": "manufacturer calculation governs"},
    {"area": "Electrical rooms and substations", "hazard": "Arc flash, protection mal-coordination, loss of both feeds", "toolkit": "electrical.lee_*, idmt, grading_check, earthing", "note": "full coordination and IEEE 1584 studies need software"},
    {"area": "Chilled-water and liquid-cooling loops", "hazard": "Surge, water hammer, leak onto live equipment, loss of flow", "toolkit": "hydraulics.surge_screen, pump_affinity, npsha_m", "note": "transient analysis beyond Joukowsky needs software"},
    {"area": "Cooling towers and water treatment", "hazard": "Legionella, chemical dosing, blowdown disposal, water shortage", "toolkit": "datacentre.evaporative_water_l_per_kwh_it", "note": "regulatory limits are inputs"},
    {"area": "Lightning and external events", "hazard": "Direct strike, surge, flood, heat, dust", "toolkit": "electrical (rolling sphere, collection area)", "note": "IEC 62305 risk assessment not implemented"},
    {"area": "Common cause across redundant paths", "hazard": "Shared cable route, shared fire compartment, shared control system", "toolkit": "reliability, qra.frequency (beta factor in sil)", "note": "availability helpers here assume independence"},
]


def summary(it_kw: float, facility_kw: float | None = None, delta_t_k: float | None = None, heat_kw: float | None = None, autonomy_min: float | None = None,
            battery_eff: float = 0.95, battery_dod: float = 0.8, gen_load_kw: float | None = None, gen_hours: float | None = None,
            sfc_g_kwh: float | None = None) -> dict:
    """Run whichever of the helpers the supplied inputs allow."""
    out: dict = {"it_kw": it_kw}
    if facility_kw is not None:
        out["pue"] = pue(facility_kw, it_kw)
    if delta_t_k is not None:
        out["cooling_water_m3_h"] = cooling_water_flow_m3_h(heat_kw if heat_kw is not None else it_kw, delta_t_k)
    if autonomy_min is not None:
        out["battery_nameplate_kwh"] = battery_energy_kwh(it_kw, autonomy_min, battery_eff, battery_dod)
    if gen_hours is not None:
        out["diesel_m3"] = diesel_storage_m3(gen_load_kw if gen_load_kw is not None else (facility_kw or it_kw), gen_hours, sfc_g_kwh or 0.0)
    return out

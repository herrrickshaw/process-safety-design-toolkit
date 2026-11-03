"""Flare / relief-system load aggregation for refineries, gas plants and petrochemical complexes.

API 521 practice: for each credible single-cause event (power failure, cooling-water failure, instrument-air failure, fire in one zone,
...), sum the relief loads that event releases from ALL affected units, with the heaviest realistic coincidence; the flare header and
tip are sized for the governing event. This module does the arithmetic (flow, molecular-weight-weighted mixture, header size by Mach
limit); which valves open together for each event is the engineering input and must come from the cause-and-effect study.
"""
from __future__ import annotations

from .scenarios import flare_header_diameter_m


def event_load(devices: list[dict]) -> dict:
    """devices: [{'name','kg_s','mw','T_K'}...] -> total mass flow, mole-based mixture MW, enthalpy-weighted (mass) temperature."""
    m = sum(d["kg_s"] for d in devices)
    mol = sum(d["kg_s"] / d["mw"] for d in devices)
    return {"kg_s": m, "mw": m / mol, "T_K": sum(d["kg_s"] * d["T_K"] for d in devices) / m, "n": len(devices)}


def governing_event(events: dict[str, list[dict]]) -> tuple[str, dict, dict]:
    loads = {k: event_load(v) for k, v in events.items()}
    name = max(loads, key=lambda k: loads[k]["kg_s"])
    return name, loads[name], loads


def header_for_event(load: dict, P_kpa_abs: float, k: float, mach: float) -> float:
    """Header diameter that holds the Mach number at the governing load."""
    return flare_header_diameter_m(load["kg_s"], P_kpa_abs, load["T_K"], load["mw"], k, mach)

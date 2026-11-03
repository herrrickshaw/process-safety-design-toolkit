"""Common relief scenarios: catalogue of how each relieving rate is determined, plus calculators for the ones that reduce to
first-principles physics (blocked-in liquid thermal expansion, tube rupture, flare-header Mach sizing).

The catalogue is a checklist of what to evaluate per API 521 Part I (the list is a secondary-source summary: blocked outlet, external
fire, control-valve failure, tube rupture, thermal expansion, cooling/reflux/cold-feed loss, utility failure, runaway reaction,
inadvertent valve opening, check-valve failure); the standard's own table was not read. Two-phase and runaway reactions need DIERS
methods and are NOT calculated here. Size for every credible scenario and take the largest (relief.governing_case).
"""
from __future__ import annotations

import math

from .relief import R, gas_mass_flux

SCENARIOS = {
    "Blocked outlet": ("Relieve the maximum credible inflow at relieving pressure (pump deadhead flow from the curve, compressor "
                       "maximum flow, upstream source at its maximum pressure); credit only unquestionable outlets", "user input -> relief.gas_area / liquid_area"),
    "External fire (liquid-wetted)": ("Heat input Q = C F A^0.82 -> vapour rate Q/latent heat", "relief.fire_relief_rate_kg_h"),
    "External fire (vapour-filled)": ("Transient wall/gas heating; check rupture vs relief; depressuring", "vapour_fire.simulate"),
    "Fire on atmospheric/low-pressure tank": ("API 2000 emergency venting", "tank_venting.fire_venting_Nm3h"),
    "Blocked-in liquid thermal expansion": ("Volumetric expansion rate = alpha . heat input /(rho cp)", "scenarios.thermal_expansion_relief_m3h"),
    "Heat-exchanger tube rupture": ("Double-ended tube break flow from the high-pressure side unless the 10/13 rule exempts it", "scenarios.tube_rupture_flow_kg_s"),
    "Control valve failure open (gas breakthrough)": ("Flow of the failed valve at maximum travel and relieving upstream pressure, less normal outflow", "user input (valve data)"),
    "Control valve failure closed": ("Treat as blocked outlet", "blocked outlet"),
    "Cooling water / reflux / cold-feed failure": ("Heat balance: vapour = unremoved duty / latent heat (plus lights not condensed)", "user heat balance"),
    "Utility failure (power, instrument air, steam)": ("Evaluate each failure mode; fail-safe positions decide the rate", "user input"),
    "Inadvertent valve opening / check-valve failure": ("Flow from the higher-pressure source through the open path", "user input"),
    "Runaway reaction / two-phase": ("DIERS vent sizing (Fauske, Leung); not in this package", "not implemented"),
    "Abnormal heat input (fired heater, reboiler)": ("Maximum duty / latent heat", "user heat balance"),
}


def thermal_expansion_relief_m3h(heat_input_W: float, alpha_per_K: float, rho: float, cp_J_kgK: float) -> float:
    """Volumetric rate (m3/h) at which a blocked-in liquid must be relieved: dV/dt = alpha . Phi /(rho cp).
    Typical alpha ~ 1e-3 /K for hydrocarbons, ~2e-4 for water (use property data)."""
    return alpha_per_K * heat_input_W / (rho * cp_J_kgK) * 3600


def tube_rupture_exempt(P_hp_design_kpag: float, P_lp_design_kpag: float) -> bool:
    """API 521 '10/13 rule': no tube-rupture relief needed if the low-pressure side design pressure >= 10/13 of the
    high-pressure side design pressure (equivalently, LP hydrotest 1.3 x design >= HP design). Older practice used a 2/3 rule."""
    return P_lp_design_kpag >= P_hp_design_kpag * 10 / 13


def tube_rupture_flow_kg_s(tube_id_m: float, P_hp_kpa: float, P_lp_kpa: float, phase: str, rho: float | None = None,
                           T_K: float | None = None, M: float | None = None, k: float | None = None, n_ends: int = 2,
                           Cd: float = 0.62) -> float:
    """Flow through a double-ended tube break (n_ends=2) into the low-pressure side. Cd = 0.62 is a generic sharp-edged orifice value,
    not an API figure; the real break is partly throttled by the tube, so this is conservative. Absolute pressures (kPa)."""
    A = n_ends * math.pi * tube_id_m ** 2 / 4
    if phase == "liquid":
        return Cd * A * math.sqrt(2 * rho * (P_hp_kpa - P_lp_kpa) * 1e3)
    G, _ = gas_mass_flux(P_hp_kpa, P_lp_kpa, T_K, M, k)
    return Cd * A * G


def flare_header_diameter_m(mass_kg_s: float, P_kpa_abs: float, T_K: float, M: float, k: float, mach: float) -> float:
    """Pipe diameter that holds the header at a chosen Mach number. Designers commonly cap peak-flow header Mach well below 1
    (a limit such as 0.5-0.7 is common; confirm your client's criterion). Static pressure/temperature at the section assumed."""
    rho = P_kpa_abs * 1e3 * (M / 1000) / (R * T_K)
    c = math.sqrt(k * R * T_K / (M / 1000))
    return math.sqrt(4 * mass_kg_s / (math.pi * rho * mach * c))

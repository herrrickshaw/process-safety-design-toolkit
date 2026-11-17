"""Vapour cloud explosion (VCE) and flash fire after delayed ignition: the Purple Book (PGS 3 / CPR 18E) section 4.8 screening method.

Read from the supplied text (section 4.8 and appendix 4.C.10):
  Ignition of an unconfined cloud is split into two independent events: a pure flash fire (probability 0.6) and a pure explosion (probability 0.4)
  [the 'LPG-Integraal' study uses 0.3 / 0.7: the book says the figures are uncertain];
  the mass in the cloud is the mass within the LFL contour; the explosion is a multi-energy blast of the highest strength (class 10), where the scaled
  distances for the 0.3 barg and 0.1 barg side-on overpressures are 1.5 and 3 (Yellow Book Figure 5.8A, read by the Purple Book);
  R_0.3bar = 1.5 (f_obstr E / Pa)^(1/3),  R_0.1bar = 3 (f_obstr E / Pa)^(1/3)       (4.5), (4.6)
  E = combustion energy of the flammable mass; f_obstr = fraction of the flammable mass in obstructed regions, default 0.08, explosion centred on the cloud.
  The book notes the result is comparable to a TNT-equivalent method with a factor of 20 % between 10 and 100 kPa, and that the older formulas
  R_0.3 = 0.03 (eta E)^(1/3), R_0.1 = 0.06 (eta E)^(1/3) with eta = 0.1 are reproduced by f_obstr = 0.08.
Not included: the full multi-energy curves for other blast strengths (Yellow Book graphs), the flame speed and congestion description of the site, deflagration
to detonation transition, the lethality of the blast (Purple Book Figure 5.5, a graph) and the mass within the LFL contour (needs a validated dispersion
model, see `dispersion` and `dense_gas`; `jet_flammable_mass_kg` below is a screening estimate for a momentum jet only).
Screening aid, not certified design.
"""
from __future__ import annotations

PA = 101325.0
P_FLASH_FIRE = 0.6
P_EXPLOSION = 0.4
BLAST_SCALED_DISTANCE_0P3_BAR = 1.5
BLAST_SCALED_DISTANCE_0P1_BAR = 3.0
F_OBSTRUCTED_DEFAULT = 0.08


def combustion_energy_J(mass_kg: float, heat_of_combustion_J_kg: float) -> float:
    if mass_kg < 0 or heat_of_combustion_J_kg <= 0:
        raise ValueError("mass must not be negative and the heat of combustion must be positive")
    return mass_kg * heat_of_combustion_J_kg


def blast_radii_m(mass_kg: float, heat_of_combustion_J_kg: float, f_obstructed: float = F_OBSTRUCTED_DEFAULT, Pa: float = PA) -> dict:
    """(4.5), (4.6): distances to 0.3 barg and 0.1 barg peak side-on overpressure."""
    if not 0 < f_obstructed <= 1:
        raise ValueError("f_obstructed must be in (0, 1]")
    E = combustion_energy_J(mass_kg, heat_of_combustion_J_kg)
    L = (f_obstructed * E / Pa) ** (1.0 / 3.0)
    return {"E_J": E, "R_0.3bar_m": BLAST_SCALED_DISTANCE_0P3_BAR * L, "R_0.1bar_m": BLAST_SCALED_DISTANCE_0P1_BAR * L}


def old_formula_radii_m(mass_kg: float, heat_of_combustion_J_kg: float, eta: float = 0.1) -> dict:
    """The earlier Purple Book formulas, kept for the equivalence check: R_0.3 = 0.03 (eta E)^(1/3), R_0.1 = 0.06 (eta E)^(1/3)."""
    E = combustion_energy_J(mass_kg, heat_of_combustion_J_kg)
    return {"R_0.3bar_m": 0.03 * (eta * E) ** (1 / 3), "R_0.1bar_m": 0.06 * (eta * E) ** (1 / 3)}


def event_frequencies(frequency_of_cloud_ignition_per_y: float, p_explosion: float = P_EXPLOSION) -> dict:
    """Split of an ignited-cloud frequency into a pure flash fire and a pure explosion (section 4.8)."""
    if not 0 <= p_explosion <= 1 or frequency_of_cloud_ignition_per_y < 0:
        raise ValueError("probability must be in [0, 1] and the frequency not negative")
    return {"flash_fire_per_y": (1 - p_explosion) * frequency_of_cloud_ignition_per_y, "explosion_per_y": p_explosion * frequency_of_cloud_ignition_per_y}


def lfl_mass_fraction(lfl_volume_fraction: float, fuel_molar_mass_kg_kmol: float, air_molar_mass_kg_kmol: float = 28.96) -> float:
    """Fuel mass fraction in a mixture at the LFL: w = yM / (yM + (1 - y) Ma)."""
    y = lfl_volume_fraction
    if not 0 < y < 1:
        raise ValueError("LFL must be a fraction between 0 and 1")
    return y * fuel_molar_mass_kg_kmol / (y * fuel_molar_mass_kg_kmol + (1 - y) * air_molar_mass_kg_kmol)


def jet_flammable_mass_kg(m_dot_kg_s: float, d_star_m: float, u0_m_s: float, w_lfl: float, entrainment: float = 0.32) -> float:
    """Screening estimate of the fuel mass inside the LFL boundary of a momentum jet in still air. Ricou-Spalding entrainment (m(z)/m0 = 0.32 z/d*, as quoted in the
    INERIS paper) with momentum conserved (u(z) = u0 m0/m(z)) gives fuel per metre of jet m(z)/u0; integrating to the LFL distance z_L = (1/w)/0.32 d* gives
    M = 0.5 * 0.32 * m0 * z_L^2 / (d* u0). Mean-concentration estimate, no wind, no buoyancy, ignores the rich core above the UFL: order of magnitude only."""
    if min(m_dot_kg_s, d_star_m, u0_m_s, w_lfl, entrainment) <= 0:
        raise ValueError("all inputs must be positive")
    z_lfl = (1.0 / w_lfl) / entrainment * d_star_m
    return entrainment * m_dot_kg_s * z_lfl * z_lfl / (2.0 * d_star_m * u0_m_s)

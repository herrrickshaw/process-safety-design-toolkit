"""Atmospheric expansion of an orifice release: post-expansion velocity, temperature, density, area (and flash fraction for a flashing liquid).

Source (read for this module): Witlox and Fernandez, "Modelling and validation of atmospheric expansion and near-field dispersion for
pressurised vapour or two-phase orifice releases", IChemE Symposium Series 161 (Hazards 26), 2016 (open PDF on icheme.org), the ATEX
model: equations (1)-(10). The release is taken from the vena contracta (area Cd Ao) to a plane final surface at ambient pressure with

  (1) mass          rho_f A_f u_f = rho_vc A_vc u_vc
  (2) momentum      rho_f A_f u_f^2 = rho_vc A_vc u_vc^2 + (P_vc - P_f) A_vc          [P_f = ambient]
  (3) energy        h_f + u_f^2/2 = h_vc + u_vc^2/2

Combining (1) and (2): u_f = u_vc + (P_vc - P_a) / (rho_vc u_vc). For an ideal gas (8) gives h_f - h_vc = Cp (T_f - T_vc), so
(3) gives T_f = T_vc + (u_vc^2 - u_f^2)/(2 Cp), and rho_f = P_a Mw / (R T_f); A_f follows from (1). Choked ideal-gas vena contracta
is (6)-(7) of the paper. The paper's optional velocity cap (Phast default 500 m/s) is available as `u_cap_m_s` and is applied through
the energy equation as the paper describes; by default there is no cap. The paper notes u_f is a "pseudo-velocity" for choked flow:
it is the value that gives the right entrainment in a dispersion model, not a measured jet velocity.

Flashing liquid (this module's reading, derived from the same equations): the vena contracta is metastable liquid at ambient pressure
(the paper's DISC/TVDI assumption for liquid storage), so (2) gives u_f = u_vc with u_vc from Bernoulli, and (3) makes the expansion
isenthalpic. With constant liquid cp and latent heat that is the adiabatic flash fraction x = cp (T0 - Tb)/h_fg and a final state at
the normal boiling point Tb; the mixture density is 1/rho_f = x/rho_v + (1-x)/rho_L with ideal-gas vapour.

Limits: ideal gas (no real-gas Z, no condensation); no two-phase choking inside the orifice (a liquid very near saturation chokes at
the orifice and needs `twophase`); no droplet size and no rainout prediction. The paper reports a modified CCPS droplet-size correlation
as the best predictor of rainout in the DNV JIP, but that correlation was not read, so `rainout_fraction` is an INPUT. Liquid cp,
latent heat, boiling point and density are inputs (no property data are coded); flash fraction above 1 is refused. Its output feeds
`jet_flame` only for gas releases: the DNV two-phase source diameter and Cook correlations are not implemented, so a flashing result is
not a jet-flame input. Screening aid; the paper itself shows the choice of expansion method matters for the answer.
"""
from __future__ import annotations

import math

from .constants import ATM_KPA, R

R_KMOL = R * 1000.0          # J/(kmol K)


def _positive(**kw) -> None:
    for k, v in kw.items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")


def atex_gas(P_st_kPa: float, T_st_K: float, Mw: float, gamma: float, area_m2: float, Cd: float = 0.85,
             P_amb_kPa: float = ATM_KPA, u_cap_m_s: float | None = None) -> dict:
    """Choked ideal-gas orifice release expanded to ambient pressure. P_st_kPa is absolute stagnation pressure.

    Cd is an input (the toolkit codes no discharge coefficient). Returns the vena contracta state, mass rate and the final state."""
    _positive(P_st_kPa=P_st_kPa, T_st_K=T_st_K, Mw=Mw, area_m2=area_m2, P_amb_kPa=P_amb_kPa)
    if not gamma > 1.0:
        raise ValueError("gamma must exceed 1")
    if not 0 < Cd <= 1:
        raise ValueError("Cd must be in (0, 1]")
    if u_cap_m_s is not None and not u_cap_m_s > 0:
        raise ValueError("u_cap_m_s must be positive")
    p_ratio = (2.0 / (gamma + 1.0)) ** (gamma / (gamma - 1.0))
    if P_st_kPa * p_ratio < P_amb_kPa:
        raise ValueError("flow is not choked at this stagnation pressure; this model covers choked releases only")
    Rs = R_KMOL / Mw
    cp = gamma * Rs / (gamma - 1.0)
    T_vc = T_st_K * 2.0 / (gamma + 1.0)
    P_vc = P_st_kPa * p_ratio
    u_vc = math.sqrt(gamma * Rs * T_vc)
    rho_vc = P_vc * 1000.0 / (Rs * T_vc)
    a_vc = Cd * area_m2
    G = rho_vc * a_vc * u_vc
    u_f = u_vc + (P_vc - P_amb_kPa) * 1000.0 / (rho_vc * u_vc)
    capped = u_cap_m_s is not None and u_f > u_cap_m_s
    if capped:
        u_f = u_cap_m_s
    T_f = T_vc + (u_vc ** 2 - u_f ** 2) / (2.0 * cp)
    if T_f <= 0:
        raise ValueError("energy balance gives a non-positive final temperature: use a velocity cap or a non-ideal model")
    rho_f = P_amb_kPa * 1000.0 / (Rs * T_f)
    A_f = G / (rho_f * u_f)
    return {"G_kg_s": G, "P_vc_kPa": P_vc, "T_vc_K": T_vc, "u_vc_m_s": u_vc, "rho_vc_kg_m3": rho_vc, "A_vc_m2": a_vc,
            "u_f_m_s": u_f, "T_f_K": T_f, "rho_f_kg_m3": rho_f, "A_f_m2": A_f, "D_f_m": 2.0 * math.sqrt(A_f / math.pi),
            "capped": capped, "cp_J_kgK": cp,
            "notes": ["Ideal gas, choked, plane final surface (ATEX); u_f is a pseudo-velocity for choked flow.",
                      "Screening aid: expansion method choice changes the answer (Witlox and Fernandez 2016)."]}


def adiabatic_flash_fraction(cp_L_J_kgK: float, T0_K: float, Tb_K: float, h_fg_J_kg: float) -> float:
    """Vapour mass fraction from isenthalpic flash of liquid at T0 to its boiling point Tb: x = cp (T0 - Tb) / h_fg (zero if T0 <= Tb).

    Constant cp and h_fg over the range (inputs). Refuses x > 1 (the liquid is more than fully vaporised: treat as vapour)."""
    _positive(cp_L_J_kgK=cp_L_J_kgK, T0_K=T0_K, Tb_K=Tb_K, h_fg_J_kg=h_fg_J_kg)
    x = max(cp_L_J_kgK * (T0_K - Tb_K) / h_fg_J_kg, 0.0)
    if x > 1.0:
        raise ValueError("flash fraction exceeds 1: the release is all vapour, use the gas model")
    return x


def atex_flashing_liquid(P0_kPa: float, T0_K: float, rho_L_kg_m3: float, cp_L_J_kgK: float, Tb_K: float, h_fg_J_kg: float,
                         Mw: float, area_m2: float, Cd: float = 0.62, P_amb_kPa: float = ATM_KPA,
                         rainout_fraction: float = 0.0) -> dict:
    """Subcooled liquid released through an orifice and flashing to ambient (see the module docstring for the assumptions).

    P0_kPa is absolute storage pressure. rainout_fraction is the fraction of the mass that falls out as liquid (INPUT)."""
    _positive(P0_kPa=P0_kPa, T0_K=T0_K, rho_L_kg_m3=rho_L_kg_m3, Mw=Mw, area_m2=area_m2, P_amb_kPa=P_amb_kPa)
    if not 0 < Cd <= 1:
        raise ValueError("Cd must be in (0, 1]")
    if not 0 <= rainout_fraction < 1:
        raise ValueError("rainout_fraction must be in [0, 1)")
    if P0_kPa <= P_amb_kPa:
        raise ValueError("storage pressure must exceed ambient")
    x = adiabatic_flash_fraction(cp_L_J_kgK, T0_K, Tb_K, h_fg_J_kg)
    u_vc = math.sqrt(2.0 * (P0_kPa - P_amb_kPa) * 1000.0 / rho_L_kg_m3)
    a_vc = Cd * area_m2
    G = rho_L_kg_m3 * a_vc * u_vc
    rho_v = P_amb_kPa * 1000.0 * Mw / (R_KMOL * Tb_K)
    rho_f = 1.0 / (x / rho_v + (1.0 - x) / rho_L_kg_m3)
    u_f = u_vc
    A_f = G / (rho_f * u_f)
    return {"G_kg_s": G, "airborne_kg_s": G * (1.0 - rainout_fraction), "x_vapour": x, "u_vc_m_s": u_vc, "u_f_m_s": u_f,
            "T_f_K": Tb_K if x > 0 else T0_K, "rho_f_kg_m3": rho_f, "rho_vapour_kg_m3": rho_v, "A_f_m2": A_f,
            "D_f_m": 2.0 * math.sqrt(A_f / math.pi), "rainout_fraction": rainout_fraction,
            "notes": ["Metastable-liquid vena contracta, isenthalpic flash at the boiling point; no in-orifice flashing or choking.",
                      "Rainout is an input, not predicted; droplet size not modelled.",
                      "Two-phase jet fire (DNV section 3, Cook) is not implemented: do not feed this result to jet_flame as a vapour."]}


def jet_flame_inputs(result: dict) -> dict:
    """Keyword arguments for `jet_flame.chamberlain` from a GAS result (mass rate, post-expansion density and velocity)."""
    if "x_vapour" in result:
        raise ValueError("a flashing-liquid result is not a vapour jet-flame input")
    return {"m_kg_s": result["G_kg_s"], "rho_j_kg_m3": result["rho_f_kg_m3"], "v_j_m_s": result["u_f_m_s"]}

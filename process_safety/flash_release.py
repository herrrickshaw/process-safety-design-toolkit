"""Saturated-liquid (flashing) orifice release: omega-method discharge, choke state, atmospheric expansion and flash fraction.

Why this exists: `expansion.atex_flashing_liquid` takes the liquid at the vena contracta as unflashed (Bernoulli), which is right for a
liquid well above its saturation pressure. A liquid stored AT its saturation pressure (pressurised LPG, ammonia) flashes inside the orifice
and chokes there; its mass flux is the omega-method (homogeneous equilibrium) value, several times smaller than the Bernoulli value.

Equations (all derived from balances; sources in docs/SOURCE_TERM_SOURCES.md):
  discharge   G = G_choked(omega, P0, rho0) from `twophase.mass_flux`; W = Cd A G
  choke state P_c = eta_c P0;  v_c = v0 [omega (P0/P_c - 1) + 1];  u_c = G / rho_c   (the omega relation of Leung; Melhem 2023, eq. 37)
  expansion   momentum (ATEX, Witlox and Fernandez 2016, eq. 2, see `expansion`):  u_f = u_c + (P_c - P_a)/G   since rho_c u_c = G
  flash       energy (ATEX eq. 3, stagnation enthalpy conserved): x = [cp_mean (T0 - Tb) - u_f^2/2] / h_fg(Tb)
              (x_H = cp_mean (T0 - Tb)/h_fg is the isenthalpic flash fraction of DNV, Phast droplet-size theory report, eq. 55)
  mixture     1/rho_f = x/rho_V(Tb) + (1 - x)/rho_L(Tb);  A_f = W/(rho_f u_f)

Limits: homogeneous, no slip, no pipe friction, saturated or low-subcooled inlet, pure fluid. Valid-range check from ISO 4126-10 as
quoted by Melhem (2023, Table 1): T/Tc < 0.9, P/Pc < 0.5, omega between 0 and 100 (`iso4126_10_check`).
Constant mean cp between T0 and Tb is an approximation (DNV takes cp at the mean temperature). Screening aid, not certified design.
"""
from __future__ import annotations

import math

from . import twophase
from .constants import ATM_KPA


def iso4126_10_check(T_K: float, Tc_K: float, P_kPa: float, Pc_kPa: float, omega: float) -> list[str]:
    """Messages for the flashing-flow limits of ISO 4126-10 as quoted by Melhem (2023, Table 1). Empty list = inside."""
    out = []
    if not T_K / Tc_K < 0.9:
        out.append(f"T/Tc = {T_K / Tc_K:.3f} is not below 0.9 (omega method limit)")
    if not P_kPa / Pc_kPa < 0.5:
        out.append(f"P/Pc = {P_kPa / Pc_kPa:.3f} is not below 0.5 (omega method limit)")
    if not 0 <= omega <= 100:
        out.append(f"omega = {omega:.3g} is outside 0 to 100")
    return out


def saturated_liquid_release(P0_kPa: float, rho0_kg_m3: float, omega: float, area_m2: float, Cd: float, T0_K: float, Tb_K: float,
                             cp_mean_J_kgK: float, h_fg_Tb_J_kg: float, rho_L_Tb_kg_m3: float, rho_V_Tb_kg_m3: float,
                             P_amb_kPa: float = ATM_KPA) -> dict:
    """Release of a saturated liquid at P0 (kPa abs), T0, through a hole of area `area_m2` to ambient. SI. Returns W, the choke and final states."""
    for k, v in dict(P0_kPa=P0_kPa, rho0=rho0_kg_m3, omega=omega, area=area_m2, T0=T0_K, Tb=Tb_K, cp=cp_mean_J_kgK, h_fg=h_fg_Tb_J_kg,
                     rho_L=rho_L_Tb_kg_m3, rho_V=rho_V_Tb_kg_m3, P_amb=P_amb_kPa).items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")
    if not 0 < Cd <= 1:
        raise ValueError("Cd must be in (0, 1]")
    if P0_kPa <= P_amb_kPa:
        raise ValueError("P0 must exceed ambient pressure")
    if T0_K <= Tb_K:
        raise ValueError("T0 must exceed the normal boiling point Tb: this model is for a superheated (flashing) liquid")
    m = twophase.mass_flux(P0_kPa, rho0_kg_m3, omega, P_back_kPa=P_amb_kPa)
    G = m["G_kg_m2_s"]
    eta = m["eta_used"]
    Pc = eta * P0_kPa
    v0 = 1.0 / rho0_kg_m3
    v_c = v0 * (omega * (P0_kPa / Pc - 1.0) + 1.0)
    rho_c = 1.0 / v_c
    u_c = G / rho_c
    u_f = u_c + (Pc - P_amb_kPa) * 1000.0 / G
    W = Cd * area_m2 * G
    xH = cp_mean_J_kgK * (T0_K - Tb_K) / h_fg_Tb_J_kg
    x = (cp_mean_J_kgK * (T0_K - Tb_K) - 0.5 * u_f * u_f) / h_fg_Tb_J_kg
    if not 0 <= x < 1:
        raise ValueError(f"flash fraction {x:.3f} is outside [0, 1): check Tb, cp and h_fg (kinetic energy may exceed the superheat)")
    rho_f = 1.0 / (x / rho_V_Tb_kg_m3 + (1.0 - x) / rho_L_Tb_kg_m3)
    A_f = W / (rho_f * u_f)
    return {"G_kg_m2_s": G, "W_kg_s": W, "regime": m["regime"], "eta_c": m["eta_critical"], "P_choke_kPa": Pc, "rho_choke_kg_m3": rho_c,
            "u_choke_m_s": u_c, "u_f_m_s": u_f, "x_isenthalpic": xH, "x_vapour": x, "rho_f_kg_m3": rho_f, "A_f_m2": A_f,
            "D_f_m": 2.0 * math.sqrt(A_f / math.pi), "KE_share_of_h_fg": 0.5 * u_f * u_f / h_fg_Tb_J_kg,
            "notes": ["Omega-method (homogeneous equilibrium) discharge; no slip, no line friction.",
                      "Constant mean cp between T0 and Tb; ideal-gas vapour density unless supplied.",
                      "Screening aid, not certified design."]}

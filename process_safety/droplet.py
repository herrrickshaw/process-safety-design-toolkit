"""Aerosol droplet size, evaporation-before-ground check and rainout screening for flashing or non-flashing liquid jets.

Sources (public documents read; see docs/SOURCE_TERM_SOURCES.md; the TNO Yellow Book and CCPS books themselves were NOT obtained):
  DNV, Phast "Droplet size model: theory and validation" (JIP Phase IV report): eq. (10) mechanical (Weber) break-up
      d = sigma We_crit / (u_f^2 rho_a), rho_a = AMBIENT AIR density, u_f = post-expansion velocity, sigma at the post-expansion temperature;
      We_crit = 12.5 as the DNV report attributes it to the Yellow Book (Brown and York 1962, Hinze 1955); Melhem quotes 10 to 20. NOTE: the Yellow Book
      text itself (section 2.5.3.7, eq. 2.143b) writes d = C_ds sigma / (u_f^2 rho_a) and recommends C_ds = 15 (literature 10 to 20); the tool `lgrelease`
      uses that, through `yb_spray`. This module is kept for the simple DNV correlations and as a cross-check.
      eq. (11) flashing SMD (CCPS RELEASE book, Woodward and Papadourakis): d = 0.833e-3 - 0.0734e-3 ln(Ep) m, Ep in J/kg
      eq. (12)-(13) partial expansion energy Ep; modified-CCPS rule: mechanical size for subcooled, flashing size for superheated releases.
      Section 6.1 rainout correlations: Kletz eta_R = max(0, 1 - 2 xH) (1 if subcooled); Lautkaski eta_R = 0.6 (1 - 3 xH), xH < 1/3, else 0;
      xH = cp (T_st - T_sat(P_a)) / dH_vap. Validity quoted there (Ramsdale and Tickle): release height about 1.22 m, horizontal release,
      orifice 3.2 to 12.7 mm, pressure 26.7 to 979 kPa.
Derived here from balances (no outside constant): droplet heat-up-limited evaporation (d-squared law) and settling.
  d^2 = d0^2 - 4 Nu k dT t / (rho_L h_fg), so t_evap = rho_L h_fg d^2 / (4 Nu k dT) (Nu = 2 is the stagnant-gas conduction limit).
  Settling: (pi/6) d^3 (rho_L - rho_g) g = (1/2) rho_g v^2 Cd(Re) (pi/4) d^2, with a drag law the caller supplies (`stokes_drag` is exact for
  Re << 1; `schiller_naumann(c1, c2)` takes its two constants as arguments because they were not read at the source).

What it does NOT do: predict a rainout FRACTION from a droplet size distribution (that needs the droplet-trajectory model of the UDM); it
screens: is the maximum or Sauter-mean droplet small enough to evaporate before it falls to the ground, and what the two published simple
correlations give. Droplet evaporation is conduction-limited from still air (no jet entrainment), so it is conservative toward rainout.
Screening aid, not certified design.
"""
from __future__ import annotations

import math
from typing import Callable

from .constants import G as g_acc

WEBER_CRIT_DNV = 12.5          # quoted value (see module docstring); callers still pass it explicitly
VALID_ORIFICE_MM = (3.2, 12.7)
VALID_PRESSURE_KPA = (26.7, 979.0)
VALID_HEIGHT_M = 1.22


def weber_max_diameter_m(sigma_N_m: float, u_f_m_s: float, rho_air_kg_m3: float, We_crit: float) -> float:
    """Largest aerodynamically stable droplet d = sigma We_crit / (u_f^2 rho_a). We_crit is an input (12.5 quoted; 10 to 20 in the literature)."""
    for k, v in dict(sigma=sigma_N_m, u_f=u_f_m_s, rho_air=rho_air_kg_m3, We_crit=We_crit).items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")
    return sigma_N_m * We_crit / (u_f_m_s ** 2 * rho_air_kg_m3)


def partial_expansion_energy_J_kg(P_st_Pa: float, P_a_Pa: float, v_st_m3_kg: float, P_vap_Tst_Pa: float, dh_J_kg: float) -> float:
    """Partial expansion energy Ep (DNV eq. 12 as printed). dh = h_final - h_stagnation (J/kg; for energy-conserving expansion -u_f^2/2).

    P_vap_Tst_Pa is the saturation pressure at the stagnation temperature. Three cases: two-phase (P_vap >= P_st), superheated liquid
    (P_a < P_vap < P_st) and subcooled liquid (P_vap <= P_a)."""
    if min(P_st_Pa, P_a_Pa, v_st_m3_kg, P_vap_Tst_Pa) <= 0 or P_st_Pa <= P_a_Pa:
        raise ValueError("pressures and specific volume must be positive and P_st above P_a")
    if P_vap_Tst_Pa >= P_st_Pa:
        return -dh_J_kg - (P_st_Pa - P_a_Pa) * v_st_m3_kg
    if P_vap_Tst_Pa > P_a_Pa:
        return -dh_J_kg - (P_vap_Tst_Pa - P_a_Pa) * v_st_m3_kg + (P_st_Pa - P_vap_Tst_Pa) * v_st_m3_kg
    return (P_st_Pa - P_a_Pa) * v_st_m3_kg


def flashing_smd_m(Ep_J_kg: float) -> float:
    """Flashing Sauter mean diameter d = 0.833e-3 - 0.0734e-3 ln(Ep) metres (CCPS RELEASE correlation as printed by DNV, eq. 11)."""
    if not Ep_J_kg > 0:
        raise ValueError("Ep must be positive")
    d = 0.833e-3 - 0.0734e-3 * math.log(Ep_J_kg)
    if d <= 0:
        raise ValueError("correlation gives a non-positive diameter: Ep is above its fitted range (about 8.5e4 J/kg)")
    return d


def stokes_drag(Re: float) -> float:
    """Cd = 24/Re: exact for Re << 1 (derived), unreliable above about Re = 1."""
    return 24.0 / Re


def schiller_naumann(c1: float, c2: float) -> Callable[[float], float]:
    """Drag law Cd = 24/Re (1 + c1 Re^c2). The constants are arguments: the usual values were not read at the source."""
    if not (c1 > 0 and c2 > 0):
        raise ValueError("constants must be positive")
    return lambda Re: 24.0 / Re * (1.0 + c1 * Re ** c2)


def evaporation_time_s(d_m: float, rho_L: float, h_fg_J_kg: float, k_gas_W_mK: float, dT_K: float, Nu: float = 2.0) -> float:
    """Time to evaporate a droplet of diameter d: rho_L h_fg d^2 / (4 Nu k dT); droplet at its boiling point, gas at dT above it."""
    for k, v in dict(d=d_m, rho_L=rho_L, h_fg=h_fg_J_kg, k=k_gas_W_mK, dT=dT_K, Nu=Nu).items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")
    return rho_L * h_fg_J_kg * d_m * d_m / (4.0 * Nu * k_gas_W_mK * dT_K)


def terminal_velocity_m_s(d_m: float, rho_L: float, rho_g: float, mu_g_Pa_s: float, drag: Callable[[float], float] = stokes_drag) -> float:
    """Settling speed from the force balance, by bisection on v (drag(Re) supplied by the caller; Stokes by default)."""
    for k, v in dict(d=d_m, rho_L=rho_L, rho_g=rho_g, mu=mu_g_Pa_s).items():
        if not (v > 0 and math.isfinite(v)):
            raise ValueError(f"{k} must be positive")
    if rho_L <= rho_g:
        raise ValueError("liquid must be denser than the gas")
    weight = math.pi / 6 * d_m ** 3 * (rho_L - rho_g) * g_acc

    def net(v):
        Re = rho_g * v * d_m / mu_g_Pa_s
        return weight - 0.5 * rho_g * v * v * drag(Re) * math.pi / 4 * d_m * d_m

    lo, hi = 1e-9, 1.0
    while net(hi) > 0:
        hi *= 2.0
        if hi > 1e4:
            raise ValueError("terminal velocity did not bracket")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if net(mid) > 0 else (lo, mid)
    return 0.5 * (lo + hi)


def critical_diameter_m(fall_height_m: float, rho_L: float, rho_g: float, mu_g: float, h_fg: float, k_gas: float, dT_K: float,
                        drag: Callable[[float], float] = stokes_drag, Nu: float = 2.0) -> float:
    """Diameter at which evaporation time equals fall time from `fall_height_m`: smaller droplets evaporate first."""
    if fall_height_m <= 0:
        raise ValueError("fall height must be positive")

    def f(d):
        return evaporation_time_s(d, rho_L, h_fg, k_gas, dT_K, Nu) - fall_height_m / terminal_velocity_m_s(d, rho_L, rho_g, mu_g, drag)

    lo, hi = 1e-7, 1e-2
    if f(lo) > 0 or f(hi) < 0:
        raise ValueError("no crossover between 0.1 micrometre and 10 mm: check inputs")
    for _ in range(100):
        mid = math.sqrt(lo * hi)
        lo, hi = (mid, hi) if f(mid) < 0 else (lo, mid)
    return math.sqrt(lo * hi)


def isenthalpic_flash_fraction(cp_mean_J_kgK: float, T_st_K: float, T_sat_Pa_K: float, dH_vap_J_kg: float) -> float:
    """xH = cp (T_st - T_sat(P_a)) / dH_vap (DNV eq. 55); zero when T_st <= T_sat."""
    if min(cp_mean_J_kgK, dH_vap_J_kg) <= 0:
        raise ValueError("cp and latent heat must be positive")
    return max(0.0, cp_mean_J_kgK * (T_st_K - T_sat_Pa_K) / dH_vap_J_kg)


def rainout_kletz(xH: float, subcooled: bool = False) -> float:
    """Kletz rule: 1 for a subcooled release, else max(0, 1 - 2 xH) (DNV eq. 56)."""
    return 1.0 if subcooled else max(0.0, 1.0 - 2.0 * xH)


def rainout_lautkaski(xH: float) -> float:
    """Lautkaski: 0.6 (1 - 3 xH) for xH < 1/3, else 0 (DNV eq. 60); fitted to the corrected CCPS data."""
    return 0.6 * (1.0 - 3.0 * xH) if xH < 1.0 / 3.0 else 0.0


def validity_warnings(orifice_mm: float, P_kPa: float, release_height_m: float, horizontal: bool) -> list[str]:
    """Where the simple rainout correlations leave the range they were fitted on (Ramsdale and Tickle, as quoted by DNV)."""
    w = []
    if not VALID_ORIFICE_MM[0] <= orifice_mm <= VALID_ORIFICE_MM[1]:
        w.append(f"orifice {orifice_mm:g} mm is outside the fitted {VALID_ORIFICE_MM[0]} to {VALID_ORIFICE_MM[1]} mm")
    if not VALID_PRESSURE_KPA[0] <= P_kPa <= VALID_PRESSURE_KPA[1]:
        w.append(f"pressure {P_kPa:g} kPa is outside the fitted {VALID_PRESSURE_KPA[0]} to {VALID_PRESSURE_KPA[1]} kPa")
    if abs(release_height_m - VALID_HEIGHT_M) > 0.5:
        w.append(f"release height {release_height_m:g} m differs from the fitted about {VALID_HEIGHT_M} m")
    if not horizontal:
        w.append("correlations were fitted to horizontal releases")
    return w


def screen(*, sigma_N_m: float, u_f_m_s: float, rho_air: float, mu_air: float, k_air: float, We_crit: float, rho_L: float, h_fg_J_kg: float,
           dT_K: float, fall_height_m: float, superheated: bool, x_isenthalpic: float, Ep_J_kg: float | None = None,
           drag: Callable[[float], float] = stokes_drag, orifice_mm: float | None = None, P_kPa: float | None = None,
           horizontal: bool = True) -> dict:
    """Droplet and rainout screen for one release. Returns maximum Weber-stable diameter, flashing SMD (superheated, if Ep given),
    the evaporate-before-ground diameter, a verdict, and the Kletz and Lautkaski values with their validity warnings."""
    d_mech = weber_max_diameter_m(sigma_N_m, u_f_m_s, rho_air, We_crit)
    d_flash = flashing_smd_m(Ep_J_kg) if (superheated and Ep_J_kg is not None) else None
    d_design = d_flash if d_flash is not None else d_mech       # modified CCPS rule: flashing size for superheated, mechanical otherwise
    d_crit = critical_diameter_m(fall_height_m, rho_L, rho_air, mu_air, h_fg_J_kg, k_air, dT_K, drag)
    ratio = d_design / d_crit
    verdict = ("droplets evaporate before the ground: rainout expected small" if ratio < 0.5 else
               "droplets are near the evaporate-or-fall limit: rainout uncertain" if ratio < 2.0 else
               "droplets are larger than the evaporate-or-fall limit: significant rainout expected")
    out = {"d_weber_max_m": d_mech, "d_flashing_smd_m": d_flash, "d_used_m": d_design, "d_critical_m": d_crit, "d_over_d_critical": ratio,
           "verdict": verdict, "kletz": rainout_kletz(x_isenthalpic, not superheated),
           "lautkaski": rainout_lautkaski(x_isenthalpic), "x_isenthalpic": x_isenthalpic,
           "notes": ["Conduction-limited evaporation in still air; no jet entrainment (conservative toward rainout).",
                     "A rainout fraction needs the droplet size distribution; the correlations below are the published simple alternatives."]}
    if orifice_mm is not None and P_kPa is not None:
        out["validity_warnings"] = validity_warnings(orifice_mm, P_kPa, fall_height_m, horizontal)
    return out

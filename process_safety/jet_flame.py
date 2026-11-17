"""Vapour jet-fire flame geometry and surface emissive power: Chamberlain conical-frustum model (pure vapour, no crosswind plane).

Source (read in full for this module): DNV, "Theory - Jet Fire", Phast/Safeti JFSH model, December 2023 (companion to the JFSH validation
document), section 2 equations (1)-(4), (15)-(18), (20), (21), (23), (25), (28), (31)-(33) and (38). The original correlations are
Chamberlain (1987, Shell) and Kalghatgi (1984) for the still-air length; they were NOT read at the original. Only the equations are
used; no DNV text is reproduced. Equation numbers below are DNV's.

What it does: from the post-expansion state (mass rate, density, and velocity or radius) it gives the effective source diameter Ds (3),
still-air flame length L_B0 by solving Kalghatgi's correlation (15)/(17), flame length in wind and at a release angle (4), the angle
alpha between hole axis and flame axis (18), lift-off B (20)-(21), frustum length R_L (23), base and tip widths W1 (25) and W2 (28), the
fraction of heat radiated F_s (32) or the Cook molecular-weight form (33), and the surface emissive power SEP = F_s m Hc / A (31) with
A from (38), capped at a maximum SEP.

Limits (all also returned in `notes`): pure vapour only (the liquid / two-phase Ds and mass-rate changes of DNV section 3 are not
implemented); the still-air length uses beta = 2.85 and Chamberlain's W_st for paraffins, so non-paraffins (hydrogen, CO, ammonia)
need their own beta, W_st and a low-luminosity model (DNV section 4, not implemented); there is no crosswind plane, so the wind is taken
in the plane of the release (theta_jv = theta_j); the Johnson horizontal-release correlations DNV recommends for near-horizontal vapour
releases (6)-(14), (22), (27), (29) are not implemented; no ground impingement; the post-expansion density and velocity must come from a
discharge/expansion model (e.g. `release`, `twophase`, an ATEX-type expansion): they are inputs. Screening aid, not a substitute for
a validated consequence tool.

Two readings of the extracted equations were settled by checks rather than assumed: (18) uses 1726*sqrt(R - 0.026) + 134 because only
that form is continuous at R = 0.05 with the 8000 R branch (a test checks it); (25) uses xi(Ds)**C as the exponent factor. Both are
flagged in the changelog for confirmation against the Chamberlain original.
"""
from __future__ import annotations

import math

from .constants import G

BETA_PARAFFIN = 2.85            # DNV: JFSH assumes beta = 2.85 (valid for paraffins burning at typical atmospheric conditions)
SEP_MAX_KW_M2 = 350.0           # DNV: default maximum surface emissive power in later releases (was 400 kW/m2 in Phast 7.2)


def stoichiometric_mass_fraction_paraffin(MW: float) -> float:
    """Chamberlain (16): W_st = MW / (15.816 MW + 39.5), valid for paraffins only."""
    return MW / (15.816 * MW + 39.5)


def _richardson(Ds: float, vj: float) -> float:
    return (G / (Ds * Ds * vj * vj)) ** (1.0 / 3.0)


def still_air_length_m(Ds_m: float, v_j_m_s: float, W_st: float, beta: float = BETA_PARAFFIN) -> float:
    """Solve Kalghatgi (15): (Ds beta / (L W_st))**(2/3) = 0.2 + 0.024 N L  for L_B0, with N = (g / (Ds^2 vj^2))**(1/3).

    The right side rises and the left side falls with L, so the root is unique; found by bisection on log L."""
    n = _richardson(Ds_m, v_j_m_s)
    a = (Ds_m * beta / W_st) ** (2.0 / 3.0)

    def f(L: float) -> float:
        return 0.2 + 0.024 * n * L - a * L ** (-2.0 / 3.0)

    lo, hi = math.log(1e-9 * Ds_m), math.log(1e9 * Ds_m)
    for _ in range(300):
        mid = 0.5 * (lo + hi)
        if f(math.exp(mid)) > 0:
            hi = mid
        else:
            lo = mid
        if hi - lo < 1e-14:
            break
    return math.exp(0.5 * (lo + hi))


def frustum_area_m2(W1: float, W2: float, R_L: float) -> float:
    """DNV (38): total frustum area including both end discs: pi/4 (W1^2 + W2^2) + pi/2 (W1 + W2) sqrt(R_L^2 + (W2 - W1)^2 / 4)."""
    return math.pi / 4 * (W1 * W1 + W2 * W2) + math.pi / 2 * (W1 + W2) * math.sqrt(R_L * R_L + (W2 - W1) ** 2 / 4)


def _fs(vj: float, MW: float, model: str) -> float:
    base = 0.21 * math.exp(-0.00323 * vj) + 0.11                      # (32)
    if model == "chamberlain":
        return base
    if MW < 21:                                                        # (33)
        return base
    if MW <= 60:
        return base * math.sqrt(MW / 21.0)
    return 1.69 * base


def chamberlain(m_kg_s: float, rho_j_kg_m3: float, rho_amb_kg_m3: float, MW: float, Hc_J_kg: float, wind_m_s: float,
                release_angle_deg: float, v_j_m_s: float | None = None, r_j_m: float | None = None, W_st: float | None = None,
                beta: float = BETA_PARAFFIN, fs_model: str = "chamberlain", sep_max_kW_m2: float = SEP_MAX_KW_M2) -> dict:
    """Chamberlain vapour jet flame. SI. Give exactly one of v_j_m_s (post-expansion velocity) or r_j_m (expanded radius).

    release_angle_deg: angle of the hole axis above the horizontal, -90..90 (90 = vertical up, 0 = horizontal).
    W_st: stoichiometric fuel mass fraction; default is Chamberlain's paraffin form (16) from MW.
    Hc_J_kg: heat of combustion of the fuel (an input; no default). fs_model: 'chamberlain' (32) or 'cook' (33).
    """
    if min(m_kg_s, rho_j_kg_m3, rho_amb_kg_m3, MW, Hc_J_kg, beta, sep_max_kW_m2) <= 0 or wind_m_s < 0:
        raise ValueError("mass rate, densities, MW, Hc, beta and the SEP cap must be positive; wind must not be negative")
    if not -90.0 <= release_angle_deg <= 90.0:
        raise ValueError("release_angle_deg must lie in -90..90 (measured from the horizontal)")
    if fs_model not in ("chamberlain", "cook"):
        raise ValueError("fs_model must be 'chamberlain' or 'cook'")
    if (v_j_m_s is None) == (r_j_m is None):
        raise ValueError("give exactly one of v_j_m_s and r_j_m")
    if v_j_m_s is not None:
        if v_j_m_s <= 0:
            raise ValueError("v_j_m_s must be positive")
        r_j = math.sqrt(m_kg_s / (rho_j_kg_m3 * math.pi * v_j_m_s))        # (2)
        v_j = v_j_m_s
    else:
        if r_j_m <= 0:
            raise ValueError("r_j_m must be positive")
        r_j = r_j_m
        v_j = m_kg_s / (rho_j_kg_m3 * math.pi * r_j * r_j)                  # (1)
    wst = stoichiometric_mass_fraction_paraffin(MW) if W_st is None else W_st
    if not 0 < wst < 1:
        raise ValueError("W_st must be between 0 and 1")

    Ds = 2.0 * r_j * math.sqrt(rho_j_kg_m3 / rho_amb_kg_m3)                 # (3)
    L0 = still_air_length_m(Ds, v_j, wst, beta)
    n_ri = _richardson(Ds, v_j)
    xi = n_ri * L0                                                           # xi(L_B0) = N_Richardson * L_B0
    th = release_angle_deg
    L_B = L0 * (0.51 * math.exp(-0.4 * wind_m_s) + 0.49) * (1.0 - 0.00607 * (th - 90.0))   # (4), theta_jv = theta_j
    R = wind_m_s / v_j
    if R <= 0.05:                                                            # (18)
        alpha = 8000.0 * R / xi + (th - 90.0) * (1.0 - math.exp(-25.6 * R))
    else:
        alpha = (1726.0 * math.sqrt(R - 0.026) + 134.0) / xi + (th - 90.0) * (1.0 - math.exp(-25.6 * R))
    alpha_raw = alpha
    alpha = min(max(alpha, 0.0), 180.0)
    k = 0.185 * math.exp(-20.0 * R) + 0.015
    if alpha < 1e-6:                                                         # (21), limit of (20)
        B = L_B * k
    elif alpha > 180.0 - 1e-6:
        B = 0.015 * L_B
    else:
        a = math.radians(alpha)
        B = L_B * math.sin(k * a) / math.sin(a)                              # (20) with alpha in radians inside sin(k alpha)
    a = math.radians(alpha)
    R_L = math.sqrt(max(L_B * L_B - B * B * math.sin(a) ** 2, 0.0)) - B * math.cos(a)   # (23)
    xi_ds = n_ri * Ds
    c = 1000.0 * math.exp(-100.0 * R) + 0.8
    W1 = Ds * (13.5 * math.exp(-6.0 * R) + 1.5) * (1.0 - (1.0 - math.sqrt(rho_amb_kg_m3 / rho_j_kg_m3) / 15.0)
                                                   * math.exp(-70.0 * R * xi_ds ** c))      # (25)
    W2 = L_B * (0.18 * math.exp(-1.5 * R) + 0.31) * (1.0 - 0.47 * math.exp(-25.0 * R))       # (28)
    area = frustum_area_m2(W1, W2, R_L)
    fs = _fs(v_j, MW, fs_model)
    power_kW = fs * m_kg_s * Hc_J_kg / 1000.0
    sep_raw = power_kW / area
    sep = min(sep_raw, sep_max_kW_m2)

    notes = ["Pure-vapour Chamberlain model; wind in the plane of the release; no ground impingement; paraffin beta and W_st unless given.",
             "Screening aid: validate against a consequence tool before design use."]
    if th < 30.0:
        notes.append("Near-horizontal release: DNV recommends the Johnson horizontal-vapour correlations, which are not implemented here.")
    if alpha_raw < 0.0:
        notes.append("Equation (18) gave a negative angle for this release direction and wind; alpha was set to 0 (flame along the release axis).")
    if alpha > 90.0:
        notes.append("Flame axis points back toward the wind (alpha > 90 deg): lazy-flame regime, treat the lift-off with caution.")
    return {"m_kg_s": m_kg_s, "rho_j_kg_m3": rho_j_kg_m3, "v_j_m_s": v_j, "r_j_m": r_j, "Ds_m": Ds, "W_st": wst, "beta": beta,
            "L_B0_m": L0, "L_B_m": L_B, "alpha_deg": alpha, "B_m": B, "R_L_m": R_L, "W1_m": W1, "W2_m": W2, "area_m2": area,
            "F_s": fs, "radiated_power_kW": power_kW, "SEP_uncapped_kW_m2": sep_raw, "SEP_kW_m2": sep, "sep_capped": sep_raw > sep_max_kW_m2,
            "notes": notes}

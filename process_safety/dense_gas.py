"""Dense-gas screening: Britter-McQuaid correlations for continuous (plume) and instantaneous (puff) releases, far-field regime only.

Source (read for this module): US EPA, "Workbook of Screening Techniques for Assessing Impacts of Toxic Air Pollutants (Revised)"
(the TSCREEN workbook, EPA-454/B-94-023 text, gaftp.epa.gov/aqmg/SCRAM/models/screening/tscreen/tscrd.pdf), section 5.4, which reproduces
Britter and McQuaid, "Workbook on the Dispersion of Dense Gases", HSE Contract Research Report 17/1988. The HSE report itself was NOT
read: its only open copy (ramp.nrc-gateway.gov) returned HTTP 403 to an automated request, and that block was not bypassed.

Dimensionless groups (EPA 5.4-9, 5.4-15, checked against the worked examples in the same document):
  g'      = g (rho2 - rho_a) / rho_a
  plume   alpha_c = (g'^2 q0 / Ur^5)^(1/5),  beta_c = x / (q0 / Ur)^(1/2),   q0 = Qm / rho2
  puff    alpha_i = (g' (Q/rho2)^(1/3))^(1/2) / Ur,  beta_i = x / (Q/rho2)^(1/3)
Dense-gas behaviour is ignored (use a passive model) when  Ur / (g' q0 / D)^(1/3) > 6  (plume, D = sqrt(2 q0 / Ur) when not known) or
alpha_i <= 0.2 (puff).

IMPLEMENTED (only what could be recovered and checked): the far-field fitted regimes, i.e. low target concentration ratios:
  plume, Cm/Co <= 0.002 and alpha_c >= 1:   beta_c = 22.6 (Cm/Co)^(-1/2) alpha_c^(-1/2)       (EPA 5.4-10)
  puff,  Cm/Co <= 0.001:  alpha_i > 1: beta_i = 10.2 (Cm/Co)^(-0.4) alpha_i^(-1/2) (alpha_i capped at 10), 0.2 < alpha_i <= 1: beta_i = 10.2 (Cm/Co)^(-0.4)
The exponent signs were lost in the PDF text extraction and were fixed by the document's own worked examples. With the averaging-time and
non-isothermal corrections switched off (the examples round Cm to 1 ppm), the plume equation reproduces the chlorine-leak example (1.10 kg/s,
2 m/s) to 0.13 percent in both heat-transfer cases. The puff equation is LESS well verified: for the aerosol-chlorine puff (1380 kg) it gives
6320 m against the example's 6480 m (2.4 percent low), and the document's second puff case quotes alpha_i 2.97 where its own left-hand
value is 2.53, so that case cannot be used. The non-isothermal correction (5.4-13) is applied by default, as the procedure says, although the
examples do not apply it; it lowers the equivalent Cm and so lengthens the distance (conservative: about 1 percent for the plume example, about
8 percent for the cold puff). Averaging time (Cm(10 min) = Cm (t_av/10)^0.05, reproduces the example's 1.020), the cold-gas heat-transfer
limiting cases (5.4-1) and the duration test (Ur Td / x above 2.5 continuous, below 0.6 instantaneous, otherwise take the larger) are included.

REFUSED, not guessed: target concentrations above the fit (the correlation there is the EPA/B&M figure, whose curve data are not in the
text, so flammable lower-flammable-limit distances for LNG or LPG are NOT covered), the plume band alpha_c < 1 (equation 5.4-11, exponent
unreadable), and passive releases (use `dispersion`). The EPA aerosol correction (5.4-2 to 5.4-6) is NOT implemented: equation 5.4-2 was
unreadable and an energy-balance reconstruction did not reproduce the document's example, so supply an already-adjusted density, mass and
temperature if you apply it yourself. Britter-McQuaid excludes jets and source momentum, buildings and terrain, humidity condensation, and
non-ideal behaviour, and the EPA text warns it is less justified for ammonia, LNG and HF. Within a factor of two is the stated aim of the
correlation. Screening aid only.
"""
from __future__ import annotations

import math

from .constants import G

PLUME_FIT_MAX_CM_CO = 0.002
PUFF_FIT_MAX_CM_CO = 0.001
PLUME_PASSIVE_RATIO = 6.0      # EPA 5.4-7: ignore dense effects when Ur / (g' q0 / D)^(1/3) exceeds this
PUFF_PASSIVE_ALPHA = 0.2       # EPA 5.4-14


def reduced_gravity(rho2_kg_m3: float, rho_a_kg_m3: float) -> float:
    """g' = g (rho2 - rho_a) / rho_a (zero or negative for a gas no denser than air)."""
    if rho2_kg_m3 <= 0 or rho_a_kg_m3 <= 0:
        raise ValueError("densities must be positive")
    return G * (rho2_kg_m3 - rho_a_kg_m3) / rho_a_kg_m3


def source_dimension_m(Qm_kg_s: float, rho2_kg_m3: float, Ur_m_s: float) -> float:
    """Screening horizontal source dimension (EPA 5.4-8): D = sqrt(2 (Qm/rho2) / Ur), for a low-momentum source with height about D/2."""
    if min(Qm_kg_s, rho2_kg_m3, Ur_m_s) <= 0:
        raise ValueError("Qm, rho2 and Ur must be positive")
    return math.sqrt(2.0 * (Qm_kg_s / rho2_kg_m3) / Ur_m_s)


def plume_is_dense(Qm_kg_s: float, rho2_kg_m3: float, rho_a_kg_m3: float, Ur_m_s: float, D_m: float | None = None) -> dict:
    """EPA 5.4-7: dense-gas effects matter unless Ur / (g' q0 / D)^(1/3) > 6. Also returns the Richardson form g' q0 / (D Ur^3)."""
    gp = reduced_gravity(rho2_kg_m3, rho_a_kg_m3)
    q0 = Qm_kg_s / rho2_kg_m3
    d = source_dimension_m(Qm_kg_s, rho2_kg_m3, Ur_m_s) if D_m is None else D_m
    if d <= 0:
        raise ValueError("D must be positive")
    if gp <= 0:
        return {"dense": False, "ratio": math.inf, "richardson": gp * q0 / (d * Ur_m_s ** 3), "D_m": d, "g_prime": gp}
    ratio = Ur_m_s / (gp * q0 / d) ** (1.0 / 3.0)
    return {"dense": ratio <= PLUME_PASSIVE_RATIO, "ratio": ratio, "richardson": gp * q0 / (d * Ur_m_s ** 3), "D_m": d, "g_prime": gp}


def puff_alpha_i(Q_kg: float, rho2_kg_m3: float, rho_a_kg_m3: float, Ur_m_s: float) -> float:
    gp = reduced_gravity(rho2_kg_m3, rho_a_kg_m3)
    if gp <= 0:
        return 0.0
    return math.sqrt(gp * (Q_kg / rho2_kg_m3) ** (1.0 / 3.0)) / Ur_m_s


def puff_is_dense(Q_kg: float, rho2_kg_m3: float, rho_a_kg_m3: float, Ur_m_s: float) -> dict:
    """EPA 5.4-14: dense-gas effects matter when alpha_i = sqrt(g' (Q/rho2)^(1/3)) / Ur exceeds 0.2."""
    if min(Q_kg, rho2_kg_m3, rho_a_kg_m3, Ur_m_s) <= 0:
        raise ValueError("Q, densities and Ur must be positive")
    a = puff_alpha_i(Q_kg, rho2_kg_m3, rho_a_kg_m3, Ur_m_s)
    return {"dense": a > PUFF_PASSIVE_ALPHA, "alpha_i": a}


def cold_gas_cases(rho2_kg_m3: float, T2_K: float, Ta_K: float) -> list[tuple[float, float]]:
    """EPA 5.4-1: the two limiting heat-transfer cases as (density, temperature): unchanged, and all heat exchanged at the source."""
    if min(rho2_kg_m3, T2_K, Ta_K) <= 0:
        raise ValueError("density and temperatures must be positive")
    return [(rho2_kg_m3, T2_K), (rho2_kg_m3 * T2_K / Ta_K, Ta_K)]


def concentration_for_10min(Cm: float, t_av_min: float) -> float:
    """Cm to use in the correlation (a 10-minute average) for a target Cm over t_av: Cm (t_av / 10)^0.05 (EPA 5.4-12 as fixed by its example)."""
    if Cm <= 0 or t_av_min <= 0:
        raise ValueError("Cm and the averaging time must be positive")
    return Cm * (t_av_min / 10.0) ** 0.05


def nonisothermal_mole_fraction(Cni: float, Ta_K: float, T2_K: float) -> float:
    """EPA 5.4-13: Cm = Cni / (Cni + (Ta / T2)(1 - Cni)), the equivalent mole fraction for a source colder or hotter than ambient."""
    if not 0 < Cni < 1 or min(Ta_K, T2_K) <= 0:
        raise ValueError("Cni must be in (0, 1) and temperatures positive")
    return Cni / (Cni + (Ta_K / T2_K) * (1.0 - Cni))


def release_regime(Ur_m_s: float, Td_s: float, x_m: float) -> str:
    """Duration test: Ur Td / x above 2.5 'continuous', below 0.6 'instantaneous', between them 'both' (report the larger distance)."""
    if min(Ur_m_s, Td_s, x_m) <= 0:
        raise ValueError("inputs must be positive")
    r = Ur_m_s * Td_s / x_m
    return "continuous" if r > 2.5 else ("instantaneous" if r < 0.6 else "both")


_NOTES = ["Britter-McQuaid screening: within a factor of two is the aim of the correlation; no jets or source momentum, no obstacles or terrain,"
          " no humidity condensation, no non-ideal behaviour.",
          "Aerosol releases need an externally adjusted source state (the EPA aerosol correction is not implemented).",
          "Far-field fit only: target concentrations above the fit limit are refused (flammable-limit distances are not covered).",
          "Screening aid, not a substitute for a validated dense-gas model (for example DEGADIS, SLAB or a CFD tool)."]


def _cases(rho2: float, T2: float, Ta: float, heat_transfer: str) -> list[tuple[str, float, float]]:
    if heat_transfer not in ("both", "none", "full"):
        raise ValueError("heat_transfer must be 'both', 'none' or 'full'")
    (a, b) = cold_gas_cases(rho2, T2, Ta)
    out = []
    if heat_transfer in ("both", "none"):
        out.append(("no_heat_transfer", a[0], a[1]))
    if heat_transfer in ("both", "full"):
        out.append(("full_heat_transfer", b[0], b[1]))
    return out


def continuous_distance_m(Qm_kg_s: float, rho2_kg_m3: float, T2_K: float, Ta_K: float, rho_a_kg_m3: float, Ur_m_s: float,
                          Cm_mole_fraction: float, Co: float = 1.0, t_av_min: float = 10.0, heat_transfer: str = "both",
                          apply_nonisothermal: bool = True) -> dict:
    """Downwind distance to a concentration Cm (mole fraction, averaged over t_av) from a continuous dense-gas release, far-field regime.

    Co is the source mole fraction of contaminant (1 for pure gas). Both heat-transfer limiting cases are run and the larger distance is
    reported. Ur is the wind speed at 10 m."""
    if min(Qm_kg_s, rho2_kg_m3, T2_K, Ta_K, rho_a_kg_m3, Ur_m_s, Cm_mole_fraction) <= 0 or not 0 < Co <= 1:
        raise ValueError("inputs must be positive and Co in (0, 1]")
    cases = []
    for name, rho, T in _cases(rho2_kg_m3, T2_K, Ta_K, heat_transfer):
        if not plume_is_dense(Qm_kg_s, rho, rho_a_kg_m3, Ur_m_s)["dense"]:
            raise ValueError("dense-gas effects are not important for this release (passive): use a passive dispersion model (`dispersion`)")
        cm = concentration_for_10min(Cm_mole_fraction, t_av_min)
        cm = nonisothermal_mole_fraction(cm, Ta_K, T) if (apply_nonisothermal and cm < 1) else cm
        ratio = cm / Co
        if ratio > PLUME_FIT_MAX_CM_CO:
            raise ValueError(f"Cm/Co = {ratio:.3g} is above {PLUME_FIT_MAX_CM_CO}: only the far-field fit was recovered, not the correlation curves")
        q0 = Qm_kg_s / rho
        alpha = (reduced_gravity(rho, rho_a_kg_m3) ** 2 * q0 / Ur_m_s ** 5) ** 0.2
        if alpha < 1.0:
            raise ValueError(f"alpha_c = {alpha:.3g} is below 1: the fit for that band was not recoverable, use a passive model or a validated tool")
        beta = 22.6 * ratio ** -0.5 * alpha ** -0.5
        x = beta * math.sqrt(q0 / Ur_m_s)
        cases.append({"case": name, "rho2_kg_m3": rho, "T2_K": T, "alpha_c": alpha, "beta_c": beta, "x_m": x,
                      "extrapolated": alpha > 3.0})
    return {"x_m": max(c["x_m"] for c in cases), "cases": cases, "Cm_for_10min": cm, "notes": list(_NOTES)}


def instantaneous_distance_m(Q_kg: float, rho2_kg_m3: float, T2_K: float, Ta_K: float, rho_a_kg_m3: float, Ur_m_s: float,
                             Cm_mole_fraction: float, Co: float = 1.0, heat_transfer: str = "both",
                             apply_nonisothermal: bool = True) -> dict:
    """Downwind distance to Cm from an instantaneous dense-gas release of Q kg, far-field regime. Averaging time is not applied
    (conservative, per the EPA text); the non-isothermal correction is."""
    if min(Q_kg, rho2_kg_m3, T2_K, Ta_K, rho_a_kg_m3, Ur_m_s, Cm_mole_fraction) <= 0 or not 0 < Co <= 1:
        raise ValueError("inputs must be positive and Co in (0, 1]")
    cases = []
    for name, rho, T in _cases(rho2_kg_m3, T2_K, Ta_K, heat_transfer):
        alpha = puff_alpha_i(Q_kg, rho, rho_a_kg_m3, Ur_m_s)
        if alpha <= PUFF_PASSIVE_ALPHA:
            raise ValueError("dense-gas effects are not important for this release (passive): use a passive dispersion model (`dispersion`)")
        cm = nonisothermal_mole_fraction(Cm_mole_fraction, Ta_K, T) if (apply_nonisothermal and Cm_mole_fraction < 1) else Cm_mole_fraction
        ratio = cm / Co
        if ratio > PUFF_FIT_MAX_CM_CO:
            raise ValueError(f"Cm/Co = {ratio:.3g} is above {PUFF_FIT_MAX_CM_CO}: only the far-field fit was recovered, not the correlation curves")
        used = min(alpha, 10.0)
        beta = 10.2 * ratio ** -0.4 * (used ** -0.5 if used > 1.0 else 1.0)
        x = beta * (Q_kg / rho) ** (1.0 / 3.0)
        cases.append({"case": name, "rho2_kg_m3": rho, "T2_K": T, "alpha_i": alpha, "alpha_used": used, "beta_i": beta, "x_m": x})
    worst = max(cases, key=lambda c: c["x_m"])
    return {"x_m": worst["x_m"], "alpha_i": worst["alpha_i"], "alpha_used": worst["alpha_used"], "cases": cases, "notes": list(_NOTES)}

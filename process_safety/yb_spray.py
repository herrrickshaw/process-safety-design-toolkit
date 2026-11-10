"""Finite-duration spray release of a pressurised liquefied gas: jet state after flashing, droplet diameter, droplet evaporation and rain-out.

Source: TNO Yellow Book (CPR 14E, third edition, second print 2005), Chapter 2, section 2.5.3.7 "Finite duration spray releases", Diagram 2.8
steps 1 to 3 and the worked butane example of section 2.6.3.5 (Table 2.6), read from the PDF supplied by the owner and from the TNO and
PGS publisher copies (identical). Equation numbers below are the Yellow Book's.

  Step 1 (2.138-2.141)  exit density, jet velocity u_f = (P_e - P_a) A_e / q + u_e, vapour fraction after flashing
                        Phi_f = 1 - [H_V,f - H_V,e + (1 - Phi_e) L_v,e + (u_f^2 - u_e^2)/2] / L_v,f, jet area A_f = rho_e u_e A_e / (rho_f u_f)
                        (the book's worked example prints (1 + Phi_e) in the formula; (1 - Phi_e) is what reproduces its own numbers.)
  Step 2 (2.142-2.143)  Re_f, We_f; d_d = 3.78 b_f sqrt(1 + 3 We_f/Re_f) if We_f < Re_f^-0.45 1e6 and T_e < 1.11 T_B, else d_d = C_ds sigma/(u_f^2 rho_a),
                        C_ds = 15 recommended (literature 10 to 20)
  Step 3 (2.144-2.151)  free-fall velocity (Stokes) u_d = rho_L g d^2 / (18 nu_a rho_a); coefficient k_B; droplet temperature depression T_d;
                        maximum rain-out diameter d_M (valid for Re_d < 4); otherwise integrate d(d)/dt = -(k_B/d)(1 + 0.28 Re_d^0.5 Sc^(1/3)) while the
                        droplet falls from h_s; rain-out mass flow = (1 - Phi_f)(d_ground/d_d)^3 q (complement of 2.151).

Sign note: (2.146) prints ln(1 - P_s/P_a), which is negative; the worked example gives a positive k_B = 2.87e-8 m2/s, which this module reproduces
with k_B = (4 mu_i D P_a / (rho_L R T_a)) * (-ln(1 - P_s/P_a)). The example's "d_M = 47 mm" is a misprint for about 0.47 mm (the zeroth-order
result (72 rho_a nu_a k_B h_s/(rho_L g))^(1/4) = 0.29 mm times the convection factor 1.63 gives 0.47 mm), and its quoted Re_d of 3671 does not
follow from either; the integration route is what the book actually uses there.

Limits: one representative droplet size; horizontal release with no initial vertical velocity; still-air fall with no jet entrainment or wind;
break-up of large droplets at their free-fall speed is not iterated (reported as a flag). Screening aid, not certified design.
"""
from __future__ import annotations

import math
from typing import Callable

R_GAS = 8.31434          # J/mol/K, the value printed with (2.146)
C_DS_RECOMMENDED = 15.0  # (2.143b) "a value of 15 is recommended"; literature 10 to 20
G_ACC = 9.81


def jet_after_flash(q_kg_s, A_e_m2, P_e_Pa, P_a_Pa, Phi_e, rho_L_e, rho_V_e, dH_V_f_minus_e_J_kg, L_v_e, L_v_f, rho_L_f, rho_V_f) -> dict:
    """Step 1. dH_V_f_minus_e = H_V,f - H_V,e (vapour enthalpy at boiling minus at exit temperature, negative when the liquid cools)."""
    for k, v in dict(q=q_kg_s, A_e=A_e_m2, P_e=P_e_Pa, P_a=P_a_Pa, rho_L_e=rho_L_e, rho_V_e=rho_V_e, L_v_e=L_v_e, L_v_f=L_v_f, rho_L_f=rho_L_f, rho_V_f=rho_V_f).items():
        if not v > 0:
            raise ValueError(f"{k} must be positive")
    if not 0 <= Phi_e < 1:
        raise ValueError("Phi_e must be in [0, 1)")
    rho_e = 1.0 / ((1.0 - Phi_e) / rho_L_e + Phi_e / rho_V_e)
    u_e = q_kg_s / (rho_e * A_e_m2)
    u_f = (P_e_Pa - P_a_Pa) * A_e_m2 / q_kg_s + u_e
    Phi_f = 1.0 - (dH_V_f_minus_e_J_kg + (1.0 - Phi_e) * L_v_e + 0.5 * (u_f ** 2 - u_e ** 2)) / L_v_f
    if not 0 <= Phi_f < 1:
        raise ValueError(f"vapour fraction after flashing {Phi_f:.3f} is outside [0, 1)")
    rho_f = 1.0 / ((1.0 - Phi_f) / rho_L_f + Phi_f / rho_V_f)
    A_f = rho_e * u_e / (rho_f * u_f) * A_e_m2
    return {"rho_e_kg_m3": rho_e, "u_e_m_s": u_e, "u_f_m_s": u_f, "Phi_f": Phi_f, "rho_f_kg_m3": rho_f, "A_f_m2": A_f, "b_f_m": math.sqrt(A_f / math.pi)}


def droplet_diameter_m(b_f_m, u_f_m_s, nu_L_m2_s, rho_L_f, sigma_N_m, rho_a, T_e_K, T_B_K, C_ds: float = C_DS_RECOMMENDED) -> dict:
    """Step 2, (2.142)-(2.143). nu_L is the kinematic viscosity of the liquid."""
    Re_f = 2.0 * b_f_m * u_f_m_s / nu_L_m2_s
    We_f = 2.0 * b_f_m * u_f_m_s ** 2 * rho_L_f / sigma_N_m
    if We_f < Re_f ** -0.45 * 1e6 and T_e_K < 1.11 * T_B_K:
        d, branch = 3.78 * b_f_m * math.sqrt(1.0 + 3.0 * We_f / Re_f), "a"
    else:
        d, branch = C_ds * sigma_N_m / (u_f_m_s ** 2 * rho_a), "b"
    return {"d_d_m": d, "Re_f": Re_f, "We_f": We_f, "branch": branch}


def free_fall_velocity_m_s(d_m, rho_L_f, nu_a, rho_a, g: float = G_ACC) -> float:
    """(2.145), Stokes regime."""
    return rho_L_f * g * d_m ** 2 / (18.0 * nu_a * rho_a)


def k_B_m2_s(mu_i_kg_mol, D_m2_s, P_a_Pa, rho_L_f, T_a_K, P_sat_Td_Pa) -> float:
    """(2.146) with the sign that gives the book's positive worked-example value."""
    if not 0 <= P_sat_Td_Pa < P_a_Pa:
        raise ValueError("saturation pressure at the droplet temperature must be below ambient pressure")
    return 4.0 * mu_i_kg_mol * D_m2_s * P_a_Pa / (rho_L_f * R_GAS * T_a_K) * (-math.log(1.0 - P_sat_Td_Pa / P_a_Pa))


def droplet_temperature_K(T_a_K, Re_d, Sc, Pr, lam_air, L_v_d_func: Callable[[float], float], rho_L_f, kB_func: Callable[[float], float],
                          T_low_K: float = 195.0, tol: float = 1e-7) -> tuple[float, float]:
    """(2.147), solved by bisection (the saturation pressure inside k_B depends strongly on T_d):
    T_d = T_a - L_v(T_d) k_B(T_d) rho_L [1 + 0.28 Re^0.5 Sc^(1/3)] / (4 lambda [1 + 0.28 Re^0.5 Pr^(1/3)]). Returns (T_d, k_B)."""
    num = 1.0 + 0.28 * math.sqrt(Re_d) * Sc ** (1.0 / 3.0)
    den = 1.0 + 0.28 * math.sqrt(Re_d) * Pr ** (1.0 / 3.0)

    def g(T):
        try:
            kB = kB_func(T)
        except ValueError:          # saturation pressure at or above ambient: the droplet cannot be that warm
            return 1.0
        return T - (T_a_K - L_v_d_func(T) * kB * rho_L_f * num / (4.0 * lam_air * den))

    lo, hi = T_low_K, T_a_K
    if g(lo) > 0 or g(hi) < 0:
        raise ValueError("droplet temperature is not bracketed between T_low and T_a: check the property data")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if g(mid) < 0 else (lo, mid)
        if hi - lo < tol:
            break
    T = 0.5 * (lo + hi)
    return T, kB_func(T)


def max_rainout_diameter_m(rho_a, nu_a, kB, h_s, rho_L_f, Sc, g: float = G_ACC) -> float:
    """(2.148), valid only when Re_d (from the free-fall velocity at this diameter) is below 4."""
    a = 9.0 * rho_a * nu_a * kB * h_s / (2.0 * rho_L_f * g)
    corr = 1.0 - 0.204 * Sc ** (1.0 / 3.0) * (rho_L_f * g / (18.0 * rho_a * nu_a ** 2)) ** 0.5 * (72.0 * rho_a * nu_a * kB * h_s / (rho_L_f * g)) ** (3.0 / 8.0)
    if corr <= 0:
        raise ValueError("(2.148) correction factor is not positive: outside the formula's range, integrate (2.149)")
    return 2.0 * (a / corr) ** 0.25


def fall_and_evaporate(d0_m, h_s_m, kB, Sc, rho_L_f, rho_a, nu_a, g: float = G_ACC, dt_s: float | None = None) -> dict:
    """(2.149)-(2.150): integrate the droplet diameter while it falls from h_s. Returns the diameter at the ground (0 if it evaporates first)."""
    d, h, t = d0_m, h_s_m, 0.0
    dt = dt_s if dt_s else max(min(d0_m ** 2 / (2 * kB) / 20000.0, 1e-3), 1e-6)
    while h > 0 and d > 1e-9:
        ud = free_fall_velocity_m_s(d, rho_L_f, nu_a, rho_a, g)
        Re = ud * d / nu_a
        rate = -kB / d * (1.0 + 0.28 * math.sqrt(Re) * Sc ** (1.0 / 3.0))
        step = dt
        if d + rate * step <= 1e-9:
            step = max((d - 1e-9) / -rate, 1e-12)
        h -= ud * step
        d += rate * step
        t += step
    return {"d_ground_m": max(d, 0.0) if h <= 0 else 0.0, "fall_time_s": t, "evaporated": h > 0 or d <= 1e-9}


def rainout(*, jet: dict, d_d_m: float, q_kg_s: float, h_s_m: float, kB: float, Sc: float, rho_L_f: float, rho_a: float, nu_a: float, g: float = G_ACC) -> dict:
    """Step 3 and (2.151)/(2.152): rain-out mass flow and the airborne remainder."""
    ud = free_fall_velocity_m_s(d_d_m, rho_L_f, nu_a, rho_a, g)
    Re_d = ud * d_d_m / nu_a
    try:
        dM = max_rainout_diameter_m(rho_a, nu_a, kB, h_s_m, rho_L_f, Sc, g)
        Re_M = free_fall_velocity_m_s(dM, rho_L_f, nu_a, rho_a, g) * dM / nu_a
    except ValueError:
        dM, Re_M = None, float("inf")
    fall = fall_and_evaporate(d_d_m, h_s_m, kB, Sc, rho_L_f, rho_a, nu_a, g)
    ratio = fall["d_ground_m"] / d_d_m
    liquid = (1.0 - jet["Phi_f"]) * q_kg_s
    rain = liquid * ratio ** 3
    return {"u_d_m_s": ud, "Re_d": Re_d, "d_M_m": dM, "Re_at_d_M": Re_M, "d_ground_m": fall["d_ground_m"], "fall_time_s": fall["fall_time_s"],
            "rainout_kg_s": rain, "rainout_fraction_of_release": rain / q_kg_s, "q_nett_air_kg_s": q_kg_s - rain,
            "breakup_flag": "free-fall break-up (2.143b with u_f replaced by u_d) is not iterated",
            "formula_applicable_d_M": bool(dM is not None and Re_M < 4)}

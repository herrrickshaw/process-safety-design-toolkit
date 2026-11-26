"""BLEVE fireball (TNO Yellow Book CPR 14E ch. 6.5.7) and the Purple Book (CPR 18E) event framework for a catastrophic failure of a pressurised vessel.

Fireball (Yellow Book 2005, section 6.5.7, equations as printed; all read from the text and reproduced in the book's own worked example, section 6.6.5):
  m = f V rho                       (6.89)  mass released = filling degree x volume x liquid density
  r_fb = 3.24 m^0.325   [m]         (6.90)  fireball radius (diameter 6.48 m^0.325, the Prugh/CCPS form)
  t = 0.852 m^0.26      [s]         (6.91)  duration
  H = 2 r_fb            [m]         (6.22)  centre height (Bagster); Prugh uses 0.75 D, measured lift-off in HSL tests 22 to 49 m for 279 to 1708 kg
  F_s = 0.00325 P_sv^0.32           (6.21)  fraction of the combustion heat radiated, P_sv in Pa (Roberts 1982)
  dH = dHc - dHv - cp dT            (6.94)  net heat, dT = 1700 K by default (flame minus ambient)
  SEP = dH m F_s / (4 pi r_fb^2 t)  (6.95)
  F_view = (r_fb / X)^2, X = sqrt(x^2 + H^2)   (6.93, 6.92)   maximum view factor, receptor facing the fireball centre
  tau = 2.02 (p_w x)^-0.09          (6.29)  valid for 1e4 < p_w x < 1e5 N/m; the book's own example applies it outside that range
  q = SEP F_view tau                (6.4)
The book also gives tau from graphs (Figures 6.2 and 6.3, eq 6.24); the graphs are not reproduced here, so `transmissivity` uses (6.29) or a constant.

Purple Book (PGS 3 / CPR 18E) framework, read from the supplied text:
  frequency of a catastrophic failure of a pressure vessel (Table 3.3): instantaneous release of the complete inventory 5e-7 per year, release in 10 min 5e-7,
  10 mm hole 1e-5; add 5e-6 to each of the first two if external impact or operating errors cannot be excluded; leak under a pressurised tank igniting
  and heating it: 1e-6 per year;
  direct ignition probability of an instantaneous release (Table 4.5, average/high reactive gas such as propane and butane): 0.2 below 1000 kg, 0.5 for 1000 to 10,000 kg, 0.7 above;
  given instantaneous release with direct ignition: BLEVE and fireball with probability 0.7 (stationary installations), mass = whole inventory, failure pressure 1.21 x the
  relief opening pressure (external fire), else cloud and pool; mass in the cloud from the adiabatic flash fraction (Table 4.8).
NOT modelled: BLEVE blast and fragments (Yellow Book chapter 7 uses Baker et al. curves and tables that are graphs), rocketing, delayed-ignition cloud explosion
after a rupture, lift-off drift and the time dependence of SEP (the HSL tests show SEP peaks before maximum size).
Screening aid, not certified design.
"""
from __future__ import annotations

import math

C9 = 3.24            # m / kg^0.325 (6.90)
C10 = 0.852          # s / kg^0.26  (6.91)
C6 = 0.00325         # (N/m2)^-0.32 (6.21)
DT_FLAME_K = 1700.0  # K, "assume dT = 1700 K" (6.94)

# Purple Book Table 3.3: pressure vessel
FREQ_PRESSURE_VESSEL = {"instantaneous_per_y": 5e-7, "ten_minute_per_y": 5e-7, "hole_10mm_per_y": 1e-5}
FREQ_EXTRA_IMPACT_OR_OPERATING_ERROR_PER_Y = 5e-6
FREQ_LEAK_UNDER_PRESSURISED_TANK_FIRE_PER_Y = 1e-6
P_BLEVE_GIVEN_DIRECT_IGNITION_STATIONARY = 0.7
FAILURE_PRESSURE_FACTOR_EXTERNAL_FIRE = 1.21
_DIRECT_IGNITION_AVG_HIGH = ((1000.0, 0.2), (10000.0, 0.5), (math.inf, 0.7))      # Table 4.5, instantaneous source mass bands
_DIRECT_IGNITION_LOW = ((1000.0, 0.02), (10000.0, 0.04), (math.inf, 0.09))


def released_mass_kg(volume_m3: float, fill_fraction: float, liquid_density_kg_m3: float) -> float:
    """(6.89): m = f V rho."""
    if not (volume_m3 > 0 and 0 < fill_fraction <= 1 and liquid_density_kg_m3 > 0):
        raise ValueError("volume and density must be positive and the filling degree in (0, 1]")
    return fill_fraction * volume_m3 * liquid_density_kg_m3


def radius_m(m_kg: float) -> float:
    return C9 * m_kg ** 0.325


def duration_s(m_kg: float) -> float:
    return C10 * m_kg ** 0.26


def centre_height_m(m_kg: float) -> float:
    return 2.0 * radius_m(m_kg)


def radiated_fraction(P_sv_Pa: float) -> float:
    """(6.21). The book's own range of validity for the vapour pressure is not stated; Roberts' fit is for P below 6 MPa (HSL, Hazards XV)."""
    if P_sv_Pa <= 0:
        raise ValueError("vapour pressure must be positive")
    return C6 * P_sv_Pa ** 0.32


def net_heat_J_kg(dHc_J_kg: float, dHv_J_kg: float, cp_J_kgK: float, dT_K: float = DT_FLAME_K) -> float:
    """(6.94)."""
    return dHc_J_kg - dHv_J_kg - cp_J_kgK * dT_K


def sep_W_m2(m_kg: float, dH_J_kg: float, F_s: float, r_m: float, t_s: float) -> float:
    """(6.95)."""
    return dH_J_kg * m_kg * F_s / (4.0 * math.pi * r_m * r_m * t_s)


def view_factor(r_m: float, x_ground_m: float, H_m: float) -> float:
    """(6.92), (6.93): maximum view factor of a sphere seen from a point at ground distance x below-and-beside a centre at height H."""
    X = math.hypot(x_ground_m, H_m)
    if X <= r_m:
        raise ValueError("receptor is inside the fireball")
    return (r_m / X) ** 2


def transmissivity(pw_x_N_m: float | None = None, constant: float | None = None) -> float:
    """(6.29) tau = 2.02 (p_w x)^-0.09, or a constant. (6.29) is stated for 1e4 < p_w x < 1e5 N/m; a value outside is returned but flagged by `transmissivity_in_range`."""
    if constant is not None:
        if not 0 < constant <= 1:
            raise ValueError("tau must be in (0, 1]")
        return constant
    if pw_x_N_m is None or pw_x_N_m <= 0:
        raise ValueError("give pw_x or a constant tau")
    return min(1.0, 2.02 * pw_x_N_m ** -0.09)


def transmissivity_in_range(pw_x_N_m: float) -> bool:
    return 1e4 < pw_x_N_m < 1e5


def flux_W_m2(m_kg: float, P_sv_Pa: float, dHc_J_kg: float, dHv_J_kg: float, cp_J_kgK: float, x_ground_m: float, tau: float = 1.0, dT_K: float = DT_FLAME_K) -> dict:
    """Heat flux at ground distance x from the point below the fireball centre, all steps of section 6.5.7."""
    r, t, H = radius_m(m_kg), duration_s(m_kg), centre_height_m(m_kg)
    Fs = radiated_fraction(P_sv_Pa)
    dH = net_heat_J_kg(dHc_J_kg, dHv_J_kg, cp_J_kgK, dT_K)
    if dH <= 0:
        raise ValueError("net heat is not positive")
    sep = sep_W_m2(m_kg, dH, Fs, r, t)
    F = view_factor(r, x_ground_m, H)
    return {"r_fb_m": r, "duration_s": t, "H_m": H, "X_m": math.hypot(x_ground_m, H), "F_view": F, "F_s": Fs, "dH_J_kg": dH,
            "SEP_W_m2": sep, "tau": tau, "q_W_m2": sep * F * tau}


def distance_to_flux_m(m_kg: float, P_sv_Pa: float, dHc_J_kg: float, dHv_J_kg: float, cp_J_kgK: float, target_W_m2: float, tau: float = 1.0) -> float | None:
    """Ground distance at which the maximum flux falls to `target` (bisection, outward from the fireball edge); None if the flux at the edge is already below it."""
    r, H = radius_m(m_kg), centre_height_m(m_kg)
    lo = math.sqrt(max(r * r * 1.0000001 - H * H, 0.0)) if r > H else 0.0
    f = lambda x: flux_W_m2(m_kg, P_sv_Pa, dHc_J_kg, dHv_J_kg, cp_J_kgK, x, tau)["q_W_m2"]
    if f(lo) < target_W_m2:
        return None
    hi = 100.0 * r
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if f(mid) > target_W_m2 else (lo, mid)
    return 0.5 * (lo + hi)


def direct_ignition_probability(mass_kg: float, reactivity: str = "average_high") -> float:
    """Purple Book Table 4.5, instantaneous release of a gas (propane and butane are average reactive)."""
    bands = {"average_high": _DIRECT_IGNITION_AVG_HIGH, "low": _DIRECT_IGNITION_LOW}.get(reactivity)
    if bands is None:
        raise ValueError("reactivity must be 'average_high' or 'low'")
    if mass_kg <= 0:
        raise ValueError("mass must be positive")
    for upper, p in bands:
        if mass_kg <= upper:
            return p
    raise AssertionError("unreachable")


def failure_pressure_Pa(prv_set_gauge_Pa: float, atmospheric_Pa: float = 101325.0) -> float:
    """Purple Book 4.7.1: pressure at failure from external fire = 1.21 x the relief opening pressure (taken here as absolute, set pressure gauge plus atmosphere)."""
    return FAILURE_PRESSURE_FACTOR_EXTERNAL_FIRE * (prv_set_gauge_Pa + atmospheric_Pa)


def cloud_mass_fraction(adiabatic_flash_fraction: float) -> float:
    """Purple Book Table 4.8: fraction of the inventory in the vapour cloud after an instantaneous release without a BLEVE."""
    x = adiabatic_flash_fraction
    if not 0 <= x <= 1:
        raise ValueError("flash fraction must be in [0, 1]")
    if x < 0.1:
        return 2.0 * x
    if x < 0.36:
        return (0.8 * x - 0.028) / 0.26
    return 1.0


def catastrophic_failure_outcomes(mass_kg: float, impact_or_operating_error_possible: bool = False, reactivity: str = "average_high") -> dict:
    """Annual frequencies of the outcomes of a catastrophic failure of a pressure vessel (Purple Book G.1 and G.2), BLEVE by the 0.7 rule."""
    f_inst = FREQ_PRESSURE_VESSEL["instantaneous_per_y"] + (FREQ_EXTRA_IMPACT_OR_OPERATING_ERROR_PER_Y if impact_or_operating_error_possible else 0.0)
    f_10 = FREQ_PRESSURE_VESSEL["ten_minute_per_y"] + (FREQ_EXTRA_IMPACT_OR_OPERATING_ERROR_PER_Y if impact_or_operating_error_possible else 0.0)
    pd = direct_ignition_probability(mass_kg, reactivity)
    pb = P_BLEVE_GIVEN_DIRECT_IGNITION_STATIONARY
    return {"f_instantaneous_per_y": f_inst, "f_ten_minute_per_y": f_10, "P_direct_ignition": pd, "P_BLEVE_given_direct": pb,
            "f_BLEVE_fireball_per_y": f_inst * pd * pb, "f_cloud_and_pool_direct_ignition_per_y": f_inst * pd * (1 - pb),
            "f_no_direct_ignition_per_y": f_inst * (1 - pd),
            "note": "The no-direct-ignition branch leads to delayed ignition (flash fire, explosion) or dispersion: see the dispersion analysis; not modelled here."}

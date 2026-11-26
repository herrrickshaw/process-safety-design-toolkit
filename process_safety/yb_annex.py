"""Pure-component property correlations for propane and n-butane, and air constants, from the TNO Yellow Book (CPR 14E, 2005 second print)
Annex "Physical properties of chemicals" (C.J.H. van den Bosch), pages annex-47 (propane), annex-17 (n-butane), annex-13 (air).

Each correlation is transcribed with its coefficients; the tests reproduce the values the Annex prints at 288.15 K, which checks the
transcription. Temperatures in K, results in SI. Valid only inside the temperature ranges printed in the Annex (raised as ValueError outside).
Formulas (Annex numbering): 1 density rho = A B^-((1-T/C)^(2/7)) g/cm3; 2 vapour pressure log10 P = A + B/T + C log10 T + D T + E T^2 (mm Hg);
3 heat of vaporisation Hv = A ((C-T)/(C-B))^D cal/g; 4 liquid heat capacity polynomial cal/g/K; 6 liquid viscosity
log10 mu = Ea + Eb/T + Ed T + Ee T^2 (cP); 8 surface tension sigma = A ((C-T)/(C-B))^D dyn/cm. The calorie (4.186 J) and mm Hg (133.3 Pa) are the
values that reproduce the Annex's own printed SI figures.
"""
from __future__ import annotations

import math

CAL = 4.186           # J/cal (reproduces the Annex's own SI values to about 1e-5)
MMHG = 133.3         # Pa per mm Hg (reproduces the Annex's printed vapour pressures)

DATA = {
    "propane": {
        "M_kg_kmol": 44.096, "Tc_K": 369.7, "Tb_K": 230.9, "net_heat_of_combustion_J_kg": 4.6013e7,
        "rho": ((0.2204, 0.2753, 369.7), (85.3, 369.7)),
        "vp": ((36.007, -1737.2, -11.666, 8.5187e-3, 0.0), (144.1, 323.0)),
        "hv": ((101.8, 230.9, 369.7, 0.38), (85.3, 369.7)),
        "cpl": ((0.3326, 2.332e-3, -1.336e-5, 3.016e-8), (85.3, 353.0)),
        "mu": ((-3.372, 313.5, 1.034e-2, -2.026e-5), (85.3, 369.7)),
        "sigma": ((22.0, 183.0, 369.7, 1.1982), (85.3, 369.7)),
        "mug": ((4.912, 0.2712, -3.806e-5), (193.0, 1273.0)),
    },
    "n-butane": {
        "M_kg_kmol": 58.1, "Tc_K": 425.2, "Tb_K": 272.7, "net_heat_of_combustion_J_kg": 4.586e7,
        "rho": ((0.2415, 0.2948, 425.2), (120.0, 400.0)),
        "vp": ((7.3, -1200.0, 1e-20, 1e-20, 1e-20), (195.0, 400.0)),
        "hv": ((90.0, 272.7, 425.2, 0.37), (200.0, 500.0)),
        "cpl": ((0.3, 2.5e-3, -1.3e-5, 2.7e-8), (120.0, 400.0)),
        "mu": ((-3.168, 313.5, 1.034e-2, -2.026e-5), (120.0, 400.0)),
        "sigma": ((22.0, 225.0, 425.2, 1.1982), (120.0, 400.0)),
        "mug": ((0.3762, 0.2491, 9.901e-6), (200.0, 800.0)),
    },
}
AIR = {"rho_288K_kg_m3": 1.225, "nu_288K_m2_s": 1.4607e-5, "Pr": 0.7104, "M_kg_kmol": 28.96, "cp_J_kgK": 1003.217, "mu_Pa_s": 1.66836e-5}


def _fl(fluid: str) -> dict:
    if fluid not in DATA:
        raise ValueError(f"{fluid!r} is not in the transcribed Annex data (propane, n-butane)")
    return DATA[fluid]


def _in(fluid, key, T):
    lo, hi = _fl(fluid)[key][1]
    if not lo <= T <= hi:
        raise ValueError(f"{fluid} {key}: {T:g} K is outside the Annex range {lo:g} to {hi:g} K")
    return _fl(fluid)[key][0]


def liquid_density_kg_m3(fluid: str, T_K: float) -> float:
    A, B, C = _in(fluid, "rho", T_K)
    return 1000.0 * A * B ** (-((1.0 - T_K / C) ** (2.0 / 7.0)))


def vapour_pressure_Pa(fluid: str, T_K: float) -> float:
    A, B, C, D, E = _in(fluid, "vp", T_K)
    return MMHG * 10.0 ** (A + B / T_K + C * math.log10(T_K) + D * T_K + E * T_K ** 2)


def heat_of_vaporisation_J_kg(fluid: str, T_K: float) -> float:
    A, B, C, D = _in(fluid, "hv", T_K)
    return A * ((C - T_K) / (C - B)) ** D * CAL * 1000.0


def liquid_heat_capacity_J_kgK(fluid: str, T_K: float) -> float:
    A, B, C, D = _in(fluid, "cpl", T_K)
    return (A + B * T_K + C * T_K ** 2 + D * T_K ** 3) * CAL * 1000.0


def liquid_viscosity_Pa_s(fluid: str, T_K: float) -> float:
    Ea, Eb, Ed, Ee = _in(fluid, "mu", T_K)
    return 10.0 ** (Ea + Eb / T_K + Ed * T_K + Ee * T_K ** 2) * 1e-3


def vapour_viscosity_Pa_s(fluid: str, T_K: float) -> float:
    """Low-pressure vapour viscosity, Annex formula 7: mu = A + B T + C T^2 in micropoise (propane page annex-47, n-butane annex-17); 1 micropoise = 1e-7 Pa s."""
    A, B, C = _in(fluid, "mug", T_K)
    return (A + B * T_K + C * T_K * T_K) * 1e-7


def surface_tension_N_m(fluid: str, T_K: float) -> float:
    A, B, C, D = _in(fluid, "sigma", T_K)
    return A * ((C - T_K) / (C - B)) ** D * 1e-3


def air_conductivity_W_mK() -> float:
    """Derived from the Annex air Prandtl number: lambda = cp mu / Pr (cp and mu at 288.15 K from the Annex air page)."""
    return AIR["cp_J_kgK"] * AIR["mu_Pa_s"] / AIR["Pr"]


def normal_boiling_point_K(fluid: str) -> float:
    return _fl(fluid)["Tb_K"]


def molar_mass_kg_mol(fluid: str) -> float:
    return _fl(fluid)["M_kg_kmol"] / 1000.0


def net_heat_of_combustion_J_kg(fluid: str) -> float:
    """Standard net (lower) heat of combustion printed in the Annex."""
    return _fl(fluid)["net_heat_of_combustion_J_kg"]


def liquid_enthalpy_change_J_kg(fluid: str, T1_K: float, T2_K: float) -> float:
    """h_L(T2) - h_L(T1) = integral of the Annex liquid heat-capacity polynomial (both temperatures inside its range)."""
    A, B, C, D = _in(fluid, "cpl", T1_K)
    _in(fluid, "cpl", T2_K)

    def F(T):
        return A * T + B * T ** 2 / 2 + C * T ** 3 / 3 + D * T ** 4 / 4
    return (F(T2_K) - F(T1_K)) * CAL * 1000.0


def saturation_temperature_K(fluid: str, P_Pa: float) -> float:
    """Inverse of the Annex vapour-pressure correlation by bisection inside its temperature range."""
    lo, hi = _fl(fluid)["vp"][1]
    if not vapour_pressure_Pa(fluid, lo) <= P_Pa <= vapour_pressure_Pa(fluid, hi):
        raise ValueError(f"{P_Pa:g} Pa is outside the vapour-pressure range of the Annex correlation for {fluid}")
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if vapour_pressure_Pa(fluid, mid) < P_Pa else (lo, mid)
    return 0.5 * (lo + hi)

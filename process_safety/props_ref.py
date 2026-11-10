"""Saturation properties of propane and n-butane tabulated from the NIST Chemistry WebBook fluid-data service (Thermophysical Properties of
Fluid Systems, https://webbook.nist.gov/chemistry/fluid/), retrieved 2026-11-10: saturated liquid and vapour, 10 K steps from 150 K.

Why this module exists: the Yellow Book Annex n-butane correlations (`yb_annex`) are crude (vapour pressure log10 P = 7.3 - 1200/T, viscosity and
surface-tension terms shaped like propane's) and differ from NIST by up to +20 % in vapour pressure; the ideal-gas vapour volume is 12 to 27 % high at
storage conditions. This module gives real-gas vapour density from the same source. `yb_annex` stays the default because the Yellow Book worked
examples are its oracle; `lg_release` takes `property_basis: "reference"` to use this module, and `line_flow` uses it by default.

Each row: (T K, P Pa, rho_liquid kg/m3, rho_vapour kg/m3, h_liquid J/kg, h_vapour J/kg, cp_liquid J/kg/K, mu_liquid Pa s, sigma N/m).
Interpolation: ln P linear in 1/T; all other quantities linear in T. The interpolation error is checked against CoolProp in `tests/crosscheck/check_properties.py`.
Enthalpies share NIST's default reference state; only differences are used.
"""
from __future__ import annotations

import math

from . import yb_annex as _yb

R = 8.314462618

_TABLE = {
    "n-butane": (
        (150.0, 8.5728, 720.880, 0.00040, -59926.0, 423210.0, 1986.1, 1.3866e-03, 0.030361),
        (160.0, 34.6120, 711.570, 0.00151, -40013.0, 434950.0, 1996.6, 1.0477e-03, 0.029031),
        (170.0, 116.1600, 702.240, 0.00478, -19986.0, 446990.0, 2009.1, 8.2690e-04, 0.027713),
        (180.0, 334.7600, 692.880, 0.01301, 176.9, 459330.0, 2024.0, 6.7470e-04, 0.026405),
        (190.0, 849.7600, 683.470, 0.03130, 20503.0, 471940.0, 2041.6, 5.6451e-04, 0.025108),
        (200.0, 1939.0000, 673.990, 0.06792, 41020.0, 484810.0, 2062.1, 4.8138e-04, 0.023823),
        (210.0, 4042.6000, 664.440, 0.13510, 61759.0, 497940.0, 2085.8, 4.1653e-04, 0.022550),
        (220.0, 7804.5000, 654.770, 0.24959, 82753.0, 511300.0, 2112.7, 3.6457e-04, 0.021289),
        (230.0, 14106.0000, 644.990, 0.43303, 104040.0, 524880.0, 2142.9, 3.2203e-04, 0.020040),
        (240.0, 24086.0000, 635.060, 0.71204, 125640.0, 538640.0, 2176.4, 2.8660e-04, 0.018805),
        (250.0, 39153.0000, 624.950, 1.11820, 147600.0, 552570.0, 2213.3, 2.5665e-04, 0.017584),
        (260.0, 60977.0000, 614.650, 1.68800, 169950.0, 566630.0, 2253.6, 2.3101e-04, 0.016378),
        (270.0, 91481.0000, 604.110, 2.46290, 192730.0, 580790.0, 2297.4, 2.0882e-04, 0.015186),
        (280.0, 132820.0000, 593.290, 3.48960, 215970.0, 595030.0, 2344.7, 1.8941e-04, 0.014011),
        (290.0, 187340.0000, 582.170, 4.82080, 239710.0, 609310.0, 2395.9, 1.7226e-04, 0.012852),
        (300.0, 257600.0000, 570.680, 6.51640, 264000.0, 623580.0, 2451.2, 1.5698e-04, 0.011711),
        (310.0, 346280.0000, 558.770, 8.64500, 288860.0, 637790.0, 2511.2, 1.4323e-04, 0.010589),
        (320.0, 456240.0000, 546.360, 11.28700, 314350.0, 651910.0, 2576.6, 1.3076e-04, 0.009488),
        (330.0, 590450.0000, 533.380, 14.54000, 340520.0, 665840.0, 2648.5, 1.1934e-04, 0.008408),
        (340.0, 752010.0000, 519.690, 18.52200, 367420.0, 679530.0, 2728.6, 1.0882e-04, 0.007351),
        (350.0, 944170.0000, 505.180, 23.38900, 395140.0, 692840.0, 2819.7, 9.9020e-05, 0.006320),
        (360.0, 1170400.0000, 489.630, 29.34700, 423770.0, 705640.0, 2925.9, 8.9826e-05, 0.005318),
        (370.0, 1434300.0000, 472.760, 36.68900, 453440.0, 717690.0, 3054.8, 8.1114e-05, 0.004347),
    ),
    "propane": (
        (150.0, 283.4500, 667.460, 0.01003, -70535.0, 430620.0, 2006.0, 6.6505e-04, 0.026292),
        (160.0, 850.2200, 657.270, 0.02821, -50378.0, 441800.0, 2025.4, 5.4261e-04, 0.025052),
        (170.0, 2204.1000, 647.000, 0.06891, -30019.0, 453230.0, 2046.7, 4.5226e-04, 0.023781),
        (180.0, 5067.8000, 636.620, 0.14993, -9432.7, 464880.0, 2070.3, 3.8346e-04, 0.022484),
        (190.0, 10547.0000, 626.100, 0.29650, 11406.0, 476690.0, 2096.8, 3.2971e-04, 0.021168),
        (200.0, 20192.0000, 615.420, 0.54171, 32532.0, 488630.0, 2126.7, 2.8682e-04, 0.019837),
        (210.0, 36032.0000, 604.550, 0.92641, 53981.0, 500640.0, 2160.5, 2.5192e-04, 0.018497),
        (220.0, 60574.0000, 593.450, 1.49900, 75797.0, 512690.0, 2198.6, 2.2301e-04, 0.017154),
        (230.0, 96775.0000, 582.080, 2.31520, 98027.0, 524710.0, 2241.3, 1.9868e-04, 0.015811),
        (240.0, 148000.0000, 570.390, 3.43830, 120720.0, 536650.0, 2289.2, 1.7788e-04, 0.014473),
        (250.0, 217960.0000, 558.340, 4.94020, 143930.0, 548450.0, 2342.7, 1.5985e-04, 0.013145),
        (260.0, 310680.0000, 545.840, 6.90330, 167720.0, 560050.0, 2402.6, 1.4401e-04, 0.011831),
        (270.0, 430430.0000, 532.820, 9.42350, 192160.0, 571370.0, 2470.1, 1.2993e-04, 0.010535),
        (280.0, 581680.0000, 519.170, 12.61600, 217310.0, 582320.0, 2546.8, 1.1728e-04, 0.009262),
        (290.0, 769140.0000, 504.780, 16.62300, 243270.0, 592780.0, 2635.3, 1.0580e-04, 0.008016),
        (300.0, 997680.0000, 489.450, 21.63000, 270150.0, 602600.0, 2739.6, 9.5274e-05, 0.006802),
        (310.0, 1272400.0000, 472.950, 27.88300, 298100.0, 611600.0, 2866.4, 8.5533e-05, 0.005624),
        (320.0, 1598900.0000, 454.940, 35.74200, 327300.0, 619470.0, 3027.9, 7.6410e-05, 0.004490),
        (330.0, 1982800.0000, 434.860, 45.75700, 358050.0, 625800.0, 3248.4, 6.7744e-05, 0.003407),
        (340.0, 2431000.0000, 411.770, 58.88000, 390860.0, 629800.0, 3584.7, 5.9336e-05, 0.002386),
        (350.0, 2951400.0000, 383.770, 77.02800, 426700.0, 629950.0, 4207.6, 5.0870e-05, 0.001443),
    ),
}
DATA = {fl: {"vp": (None, (rows[0][0], rows[-1][0])), "hv": (None, (rows[0][0], rows[-1][0]))} for fl, rows in _TABLE.items()}
AIR = _yb.AIR


def _rows(fluid: str):
    if fluid not in _TABLE:
        raise ValueError(f"{fluid!r} is not tabulated (propane, n-butane)")
    return _TABLE[fluid]


def _interp(fluid: str, T: float, col: int, log_inv_T: bool = False) -> float:
    rows = _rows(fluid)
    if not rows[0][0] <= T <= rows[-1][0]:
        raise ValueError(f"{fluid}: {T:g} K is outside the tabulated range {rows[0][0]:g} to {rows[-1][0]:g} K")
    for a, b in zip(rows, rows[1:]):
        if a[0] <= T <= b[0]:
            if log_inv_T:
                f = (1.0 / T - 1.0 / a[0]) / (1.0 / b[0] - 1.0 / a[0])
                return math.exp(math.log(a[col]) + f * (math.log(b[col]) - math.log(a[col])))
            f = (T - a[0]) / (b[0] - a[0])
            return a[col] + f * (b[col] - a[col])
    return rows[-1][col]


def vapour_pressure_Pa(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 1, True)


def liquid_density_kg_m3(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 2)


def vapour_density_kg_m3(fluid: str, T_K: float) -> float:
    """Saturated-vapour (real-gas) density."""
    return _interp(fluid, T_K, 3, True)


def heat_of_vaporisation_J_kg(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 5) - _interp(fluid, T_K, 4)


def liquid_heat_capacity_J_kgK(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 6)


def liquid_viscosity_Pa_s(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 7)


def surface_tension_N_m(fluid: str, T_K: float) -> float:
    return _interp(fluid, T_K, 8)


def liquid_enthalpy_change_J_kg(fluid: str, T1_K: float, T2_K: float) -> float:
    """h_L(T2) - h_L(T1) from the tabulated saturated-liquid enthalpy (includes the small pressure term along the saturation line)."""
    return _interp(fluid, T2_K, 4) - _interp(fluid, T1_K, 4)


def saturation_temperature_K(fluid: str, P_Pa: float) -> float:
    rows = _rows(fluid)
    if not rows[0][1] <= P_Pa <= rows[-1][1]:
        raise ValueError(f"{P_Pa:g} Pa is outside the tabulated vapour-pressure range for {fluid}")
    lo, hi = rows[0][0], rows[-1][0]
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if vapour_pressure_Pa(fluid, mid) < P_Pa else (lo, mid)
    return 0.5 * (lo + hi)


def compressibility_saturated_vapour(fluid: str, T_K: float) -> float:
    """Z = P / (rho_v R T / M) of the saturated vapour."""
    return vapour_pressure_Pa(fluid, T_K) * _yb.molar_mass_kg_mol(fluid) / (vapour_density_kg_m3(fluid, T_K) * R * T_K)


def molar_mass_kg_mol(fluid: str) -> float:
    return _yb.molar_mass_kg_mol(fluid)


def normal_boiling_point_K(fluid: str) -> float:
    return saturation_temperature_K(fluid, 101325.0)


def net_heat_of_combustion_J_kg(fluid: str) -> float:
    return _yb.net_heat_of_combustion_J_kg(fluid)


def air_conductivity_W_mK() -> float:
    return _yb.air_conductivity_W_mK()

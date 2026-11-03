"""Steel gas-pipeline design pressure and impact radius, from the freely published US pipeline safety rules (49 CFR Part 192).

VERIFIED against the regulation text (Cornell LII copy of the eCFR, fetched 2026-11-03): design formula P = (2 S t / D) F E T (192.105);
design factors by class location 0.72 / 0.60 / 0.50 / 0.40 (192.111, with the lower-factor exceptions in paragraphs (b)-(d), e.g.
0.50 or less for uncased steel in Class 2 crossing roads/railways); longitudinal joint factors (192.113, subset); temperature
derating (192.115); potential impact radius r = 0.69 sqrt(p d^2) ft for NATURAL GAS (192.903), p in psi MAOP, d in inches.
This is US regulation, not the Indian PNGRB/OISD-226 requirements (not read); ASME B31.8/B31.4 differ in places. S is the SMYS
(yield) per 192.107, an input. Not a pipeline design: no hydrotest, stress analysis, crossings, or fracture control.
"""
from __future__ import annotations

import math

DESIGN_FACTOR = {1: 0.72, 2: 0.60, 3: 0.50, 4: 0.40}
JOINT_FACTOR = {"seamless": 1.00, "electric resistance welded": 1.00, "double submerged arc welded": 1.00, "electric fusion welded": 1.00,
                "furnace butt welded (ASTM A53)": 0.60}
_TEMP = [(121.0, 1.000), (149.0, 0.967), (177.0, 0.933), (204.0, 0.900), (232.0, 0.867)]  # deg C -> T (192.115)
PSI_PER_KPA = 0.1450377377
HCA_PIR_M = 200.0  # 660 ft
HCA_BUILDINGS = 20


def temperature_derating(T_C: float) -> float:
    """192.115 table with linear interpolation between tabulated temperatures; beyond 232 C the rule gives no factor."""
    if T_C <= _TEMP[0][0]:
        return 1.0
    if T_C > _TEMP[-1][0]:
        raise ValueError("above 232 C (450 F): no factor in 192.115; special design required")
    for (t0, f0), (t1, f1) in zip(_TEMP, _TEMP[1:]):
        if T_C <= t1:
            return f0 + (f1 - f0) * (T_C - t0) / (t1 - t0)


def design_pressure_kpa(SMYS_MPa, t_mm, D_mm, class_location=1, joint_factor=1.0, T_C=20.0, design_factor=None) -> float:
    """P = (2 S t / D) F E T, returned in kPa gauge (S in MPa, t and D in mm)."""
    F = design_factor if design_factor is not None else DESIGN_FACTOR[class_location]
    return 2 * SMYS_MPa * t_mm / D_mm * F * joint_factor * temperature_derating(T_C) * 1000.0


def required_wall_mm(P_kpa, SMYS_MPa, D_mm, class_location=1, joint_factor=1.0, T_C=20.0, design_factor=None) -> float:
    F = design_factor if design_factor is not None else DESIGN_FACTOR[class_location]
    return (P_kpa / 1000.0) * D_mm / (2 * SMYS_MPa * F * joint_factor * temperature_derating(T_C))


def potential_impact_radius_m(MAOP_kpag, D_mm) -> float:
    """Natural-gas PIR (192.903): r[ft] = 0.69 sqrt(p[psi] d[in]^2), returned in metres. Other gases: ASME B31.8S section 3.2."""
    p = MAOP_kpag * PSI_PER_KPA
    d = D_mm / 25.4
    return 0.69 * math.sqrt(p * d * d) * 0.3048


def hca_by_pir(PIR_m: float, buildings_in_impact_circle: int, class_location: int = 1) -> bool:
    """The 192.903 high-consequence-area criterion (iii) for Class 1/2: PIR > 200 m (660 ft) and >= 20 buildings intended for human occupancy
    in the potential impact circle. (Other HCA criteria - class 3/4, identified sites - are not evaluated here.)"""
    return class_location in (1, 2) and PIR_m > HCA_PIR_M and buildings_in_impact_circle >= HCA_BUILDINGS

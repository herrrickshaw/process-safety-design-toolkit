"""Atmospheric / low-pressure tank venting: API Std 2000, 5th edition (April 1998) - metric tables and equations.

Basis: the 1998 text, which is publicly posted (law.resource.org/pub/us/cfr/ibr/002/api.2000.1998.pdf) and was READ for this module.
The current edition is the 7th (2014, reaffirmed 2020) and it changed the thermal-venting method (latitude/vapour-pressure
factors, Annex G); that text is paywalled and NOT implemented here. Treat results as 5th-edition values and confirm against the
edition your client/OISD-STD-108 invokes. Flows are Nm3/h of air. Pressure scope: tank design pressure <= 1.034 barg only
(above that: API 620 / API 521 vessel relief, see relief.py).
"""
from __future__ import annotations

import bisect
import math

# Table 2B: tank capacity m3 -> (inbreathing, outbreathing for FP >= 37.8 C, outbreathing for FP < 37.8 C), Nm3/h
_T2B = [
    (10, 1.69, 1.01, 1.69), (20, 3.37, 2.02, 3.37), (100, 16.9, 10.1, 16.9), (200, 33.7, 20.2, 33.7), (300, 50.6, 30.3, 50.6),
    (500, 84.3, 50.6, 84.3), (700, 118, 70.8, 118), (1000, 169, 101, 169), (1500, 253, 152, 253), (2000, 337, 202, 337),
    (3000, 506, 303, 506), (3180, 536, 388, 536), (4000, 647, 472, 647), (5000, 787, 537, 787), (6000, 896, 602, 896),
    (7000, 1003, 646, 1003), (8000, 1077, 682, 1077), (9000, 1136, 726, 1136), (10000, 1210, 807, 1210),
    (12000, 1345, 888, 1345), (14000, 1480, 969, 1480), (16000, 1615, 1047, 1615), (18000, 1745, 1126, 1745),
    (20000, 1877, 1307, 1877), (25000, 2179, 1378, 2179), (30000, 2495, 1497, 2495),
]
# Table 3B: wetted area m2 -> Nm3/h (hexane basis, F = 1)
_T3B = [(2, 608), (3, 913), (4, 1217), (5, 1521), (6, 1825), (7, 2130), (8, 2434), (9, 2738), (11, 3347), (13, 3955), (15, 4563),
        (17, 5172), (19, 5780), (22, 6217), (25, 6684), (30, 7411), (35, 8086), (40, 8721), (45, 9322), (50, 9895), (60, 10971),
        (70, 11971), (80, 12911), (90, 13801), (110, 15461), (130, 15751), (150, 16532), (175, 17416), (200, 18220), (230, 19102),
        (260, 19910)]

LIQUID_OUT_INBREATHING = 0.94      # Nm3/h per m3/h pumped out, any flash point (4.3.2.1.1)
LIQUID_IN_OUTBREATHING = 1.01      # per m3/h pumped in, FP >= 37.8 C or BP >= 148.9 C (4.3.2.2.1)
LIQUID_IN_OUTBREATHING_VOLATILE = 2.02  # FP < 37.8 C or BP < 148.9 C (4.3.2.3.1)
MAX_HEIGHT_M = 9.14                # 30 ft above grade (Table 3 footnote a)
HEXANE = {"L_kJ_kg": 334.9, "T_K": 288.7, "M": 86.17}  # basis of constants 1107 / 208.2

# Table 4B environmental factors F (insulation conductance W/m2K -> F)
F_FACTORS = {"bare": 1.0, "insulated_22.7": 0.3, "insulated_11.4": 0.15, "insulated_5.7": 0.075, "insulated_3.8": 0.05,
             "insulated_2.8": 0.0375, "insulated_2.3": 0.03, "insulated_1.9": 0.025, "water_spray": 1.0, "depressuring": 1.0,
             "underground": 0.0, "earth_covered_above_grade": 0.03, "impoundment_away_from_tank": 0.5}


def _interp(table, x, col):
    xs = [r[0] for r in table]
    if x > xs[-1]:
        raise ValueError(f"{x} above table range ({xs[-1]}); individual study required (API 2000 Table 2 note d)")
    if x <= xs[0]:
        return table[0][col] * x / xs[0]  # proportional below the table: assumption, not in the standard
    i = bisect.bisect_left(xs, x)
    x0, x1 = xs[i - 1], xs[i]
    y0, y1 = table[i - 1][col], table[i][col]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def thermal_venting(volume_m3: float, volatile: bool) -> dict:
    """Table 2B thermal in/outbreathing (linear interpolation, as the standard directs). volatile = FP < 37.8 C or BP < 148.9 C."""
    notes = ["capacity below 10 m3 scaled proportionally (not tabulated)"] if volume_m3 < 10 else []
    return {"inbreathing_Nm3h": _interp(_T2B, volume_m3, 1),
            "outbreathing_Nm3h": _interp(_T2B, volume_m3, 3 if volatile else 2), "notes": notes}


def normal_venting(volume_m3, max_fill_m3h, max_empty_m3h, volatile: bool) -> dict:
    """Total normal venting = liquid movement + thermal (4.3.2). Reductions for self-venting vapour are NOT credited."""
    th = thermal_venting(volume_m3, volatile)
    liq_in = (LIQUID_IN_OUTBREATHING_VOLATILE if volatile else LIQUID_IN_OUTBREATHING) * max_fill_m3h
    liq_out = LIQUID_OUT_INBREATHING * max_empty_m3h
    notes = list(th["notes"])
    if volatile:
        notes.append("feed near/above boiling point can need more outbreathing than 2.02 x fill rate (4.3.2.3.1)")
    notes.append("heated uninsulated tanks with vapour space > 48.9 C need an engineering review (4.3.2.1.2)")
    return {"outbreathing_Nm3h": liq_in + th["outbreathing_Nm3h"], "inbreathing_Nm3h": liq_out + th["inbreathing_Nm3h"],
            "breakdown": {"liquid_in": liq_in, "thermal_out": th["outbreathing_Nm3h"], "liquid_out": liq_out,
                          "thermal_in": th["inbreathing_Nm3h"]}, "notes": notes}


def fire_heat_input_W(A_m2: float, design_barg: float = 0.07) -> float:
    """Heat absorbed from fire, Q (W), 4.3.3.2.1 summary table; valid for design pressure <= 1.034 barg."""
    if design_barg > 1.034:
        raise ValueError("above 1.034 barg is outside API 2000: use API 620 / API 521")
    if A_m2 < 18.6:
        return 63_150 * A_m2
    if A_m2 < 93:
        return 224_200 * A_m2 ** 0.566
    if A_m2 < 260:
        return 630_400 * A_m2 ** 0.338
    return 4_129_700 if design_barg <= 0.07 else 43_200 * A_m2 ** 0.82


def fire_venting_Nm3h(A_m2, F=1.0, L_kJ_kg=HEXANE["L_kJ_kg"], T_K=HEXANE["T_K"], M=HEXANE["M"], design_barg=0.07) -> float:
    """Equation 1B: Nm3/h = 881.55 (Q F / L) (T/M)^0.5, with L effectively in J/kg (the standard prints kJ/kg but its own note
    uses 334 900 J/kg for hexane; only J/kg reproduces constants 208.2 and Table 3B). T = relieving-vapour temperature (normally
    the boiling point at relieving pressure), M = vapour molecular weight."""
    return 881.55 * fire_heat_input_W(A_m2, design_barg) * F / (L_kJ_kg * 1000) * math.sqrt(T_K / M)


def fire_venting_simplified(A_m2, F=1.0, design_barg=0.07) -> float:
    """Table 3B / Eq 2B / 19 910 Nm3/h (hexane basis) scaled by F (Q is proportional to F)."""
    if A_m2 < 260:
        return F * _interp(_T3B, A_m2, 1)
    return F * (19_910 if design_barg <= 0.07 else 208.2 * A_m2 ** 0.82)


def wetted_area_m2(shape: str, D: float, L: float = 0.0, elevation_m: float = 0.0, grounded: bool = True) -> float:
    """Wetted area per Table 3 footnote a. shape: sphere | horizontal | vertical. Heads of horizontal tanks taken flat.
    Vertical: shell to 9.14 m above grade only; the bottom of an elevated tank must be assessed by engineering judgment."""
    cap = max(0.0, MAX_HEIGHT_M - elevation_m)
    if shape == "sphere":
        total = math.pi * D * D
        return max(0.55 * total, math.pi * D * min(D, cap))  # spherical cap area = pi D h
    if shape == "horizontal":
        total = math.pi * D * L + math.pi * D * D / 2
        h = min(D, cap)
        theta = 2 * math.acos(1 - 2 * h / D) if h > 0 else 0.0
        return max(0.75 * total, L * D * theta / 2)
    if shape == "vertical":
        return math.pi * D * min(L, cap)
    raise ValueError(shape)


def emergency_vent_shortfall_Nm3h(fire_required: float, normal_capacity_outbreathing: float) -> float:
    """Normal vents get full credit during fire, thermal effect and liquid movement disregarded (4.3.3.2.4); any shortfall needs
    emergency vents (4.3.3.2.5). A frangible roof-to-shell joint (API 650) may serve instead of emergency vents (4.3.3.1)."""
    return max(0.0, fire_required - normal_capacity_outbreathing)

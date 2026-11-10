"""Ignition probability look-up correlations (Energy Institute / UKOOA model, 2006) as reproduced in an open conference paper.

Source: "Practical application of the UKOOA ignition model", IChemE Symposium Series 158 (Hazards XXIII), 2012, `icheme.org/media/9183/paper47-hazards-23.pdf`,
Table 2 (the 30 curves as release-rate and ignition-probability points) and the interpolation equation printed beside it:
    P_ign = exp( ln P_n + (ln Q - ln Q_n)(ln P_{n+1} - ln P_n) / (ln Q_{n+1} - ln Q_n) ),  Q_n <= Q <= Q_{n+1}
(log-log interpolation between adjacent points). The paper's Table 2 lists points 2 and 1 of curves 14, 15, 16 and 19 out of order (point 2 at a lower Q than
point 1); this module sorts the points by Q. The paper also gives the way to treat a two-phase release (combine gas and liquid curves as
1 - (1 - P_gas)(1 - P_liquid), or take the larger) and notes the original report is the Energy Institute's "Ignition Probability Review, Model Development and
Look-Up Correlations" (January 2006), which was not read. The probabilities are TOTAL (immediate plus delayed) ignition.
Limits: onshore and offshore curves for hydrocarbon releases; not suitable for refrigerated condensed gases, subsonic gas or non-momentum-driven releases (stated
for the model in the Norwegian DSB guideline, section 3.6.3). Screening aid, not certified design.
"""
from __future__ import annotations

import math

CASES = {
    1: ("Pipe Liquid Industrial", [(0.01, 0.001), (0.03493, 0.001), (0.1, 0.0018), (70, 0.07), (100000, 0.07)]),
    2: ("Pipe Liquid Rural", [(0.01, 0.001), (0.03787, 0.001), (0.1, 0.0018), (0.3, 0.0035), (70, 0.007), (70, 0.007), (100000, 0.007)]),
    3: ("Pipe Gas LPG Industrial", [(0.01, 0.001), (0.08791, 0.001), (0.1, 0.0011), (1000, 1), (100000, 1)]),
    4: ("Pipe Gas LPG Rural", [(0.01, 0.001), (0.04799, 0.001), (0.1, 0.0011), (10, 0.002), (1000, 0.08), (23408.5, 1), (100000, 1)]),
    5: ("Small Plant Gas LPG", [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (3, 0.014), (498.991, 0.6), (100000, 0.6)]),
    6: ("Small Plant Liquid", [(0.01, 0.001), (0.07548, 0.001), (0.1, 0.0011), (1, 0.0024), (100, 0.1), (100000, 0.1)]),
    7: ("Small Plant Liquid Bund", [(0.01, 0.001), (0.07548, 0.001), (0.1, 0.0011), (1, 0.0024), (8.053, 0.013), (100, 0.013), (100000, 0.013)]),
    8: ("Large Plant Gas LPG", [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (100, 0.25), (260, 0.65), (100000, 0.65)]),
    9: ("Large Plant Liquid", [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (100, 0.12), (109.99, 0.13), (100000, 0.13)]),
    10: ("Large Plant Liquid Bund", [(0.01, 0.001), (0.07548, 0.001), (0.1, 0.0011), (1, 0.0024), (42.492, 0.05), (100, 0.05), (100000, 0.05)]),
    11: ("Large Plant Confined Gas LPG", [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (70, 0.43), (325.028, 0.7), (100000, 0.7)]),
    12: ("Tank Liquid 300 × 300 m Bund", [(0.01, 0.001), (0.0525, 0.001), (0.1, 0.00105), (1, 0.00125), (7, 0.0027), (519.617, 0.12), (100000, 0.12)]),
    13: ("Tank Liquid 100 × 100 m Bund", [(0.01, 0.001), (0.0525, 0.001), (0.1, 0.00105), (1, 0.00125), (7, 0.0027), (49.035, 0.015), (100000, 0.015)]),
    14: ("Tank Gas LPG Storage Plant", [(0.01, 0.00104), (0.0016, 0.001), (0.1, 0.0011), (1, 0.00116), (100, 0.96), (102.838, 1), (100000, 1)]),
    15: ("Tank Gas LPG Storage", [(0.01, 0.00104), (0.0016, 0.001), (0.1, 0.0011), (1, 0.00116), (100, 0.227), (988.106, 1), (100000, 1)]),
    16: ("Tank Gas LPG Storage Rural", [(0.01, 0.00104), (0.0016, 0.001), (0.1, 0.0011), (1, 0.00116), (10, 0.0154), (52551.5, 0.5), (100000, 0.5)]),
    17: ("Offshore Process Liquid", [(0.01, 0.001), (0.07882, 0.001), (0.1, 0.0011), (100, 0.0175), (100000, 0.0175)]),
    18: ("Offshore Process Liquid NUI", [(0.01, 0.001), (0.07882, 0.001), (0.1, 0.0011), (24.731, 0.01), (100, 0.01), (100000, 0.01)]),
    19: ("Offshore Process Gas", [(0.01, 0.00101), (0.00803, 0.001), (0.1, 0.0011), (1, 0.0012), (30, 0.024), (31.423, 0.025), (100000, 0.025)]),
    20: ("Offshore Process Gas Typical", [(0.01, 0.001), (0.08833, 0.001), (0.1, 0.0011), (3, 0.015), (10, 0.024), (37.008, 0.04), (100000, 0.04)]),
    21: ("Offshore Process Gas", [(0.01, 0.001), (0.08933, 0.001), (0.1, 0.0011), (5, 0.03), (30, 0.05), (100000, 0.05)]),
    22: ("Offshore Process Gas", [(0.01, 0.001), (0.09194, 0.001), (0.1, 0.0011), (1, 0.015), (50, 0.035), (92.624, 0.04), (100000, 0.04)]),
    23: ("Offshore Riser", [(0.01, 0.001), (0.0834, 0.001), (0.1, 0.0011), (30, 0.022), (38.267, 0.025), (100000, 0.025)]),
    24: ("Offshore FPSO Gas", [(0.01, 0.001), (0.02688, 0.001), (0.1, 0.0011), (1, 0.0013), (50, 0.15), (100000, 0.15)]),
    25: ("Offshore FPSO Gas Wall", [(0.01, 0.001), (0.08393, 0.001), (0.1, 0.0011), (0.3, 0.002), (10, 0.15), (100000, 0.15)]),
    26: ("Offshore FPSO Liquid", [(0.01, 0.001), (0.0816, 0.001), (0.1, 0.0011), (100, 0.028), (100000, 0.028)]),
    27: ("Offshore Engulf_blowout_riser", [(0.01, 0.001), (0.08642, 0.001), (0.1, 0.0011), (100, 0.1), (100000, 0.1)]),
    28: ("Cox, Lees, Ang – Gas", [(0.01, 0.00081), (0.5, 0.01), (100, 0.3), (100000, 0.3)]),
    29: ("Cox, Lees, Ang – Liquid", [(0.01, 0.00215), (0.5, 0.01), (100, 0.08), (100000, 0.08)]),
    30: ("Tank Liquid – diesel, fuel oil", [(0.01, 0.001), (0.1, 0.001), (1, 0.00103), (7, 0.00117), (25.551, 0.0024), (100000, 0.0024)]),
}


def case_names() -> dict[int, str]:
    return {k: v[0] for k, v in CASES.items()}


def points(case: int) -> list[tuple[float, float]]:
    if case not in CASES:
        raise ValueError(f"case must be 1 to 30, got {case}")
    return sorted(CASES[case][1])


def ignition_probability(rate_kg_s: float, case: int) -> float:
    """Total ignition probability for release rate Q (kg/s) on curve `case` (log-log interpolation; constant beyond the end points)."""
    if not rate_kg_s > 0:
        raise ValueError("rate must be positive")
    pts = points(case)
    if rate_kg_s <= pts[0][0]:
        return pts[0][1]
    if rate_kg_s >= pts[-1][0]:
        return pts[-1][1]
    for (q0, p0), (q1, p1) in zip(pts, pts[1:]):
        if q0 <= rate_kg_s <= q1 and q1 > q0:
            return math.exp(math.log(p0) + (math.log(rate_kg_s) - math.log(q0)) * (math.log(p1) - math.log(p0)) / (math.log(q1) - math.log(q0)))
    raise ValueError("no segment found")


def combine_gas_and_liquid(p_gas: float, p_liquid: float) -> float:
    """Overall probability for simultaneous gas and liquid releases treated separately: 1 - (1 - P_gas)(1 - P_liquid) (the paper notes the sum overstates when the areas overlap)."""
    if not (0 <= p_gas <= 1 and 0 <= p_liquid <= 1):
        raise ValueError("probabilities must be in [0, 1]")
    return 1.0 - (1.0 - p_gas) * (1.0 - p_liquid)

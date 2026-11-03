"""Occupational noise: OSHA permissible exposure (Table G-16 / App. A dose formulas, verified from the text), NIOSH-style 3 dB criterion
(recalled), level combination and point-source attenuation.

OSHA (1910.95, fetched 2026-11-03): reference duration T = 8/2^((L-90)/5) hours (Table G-16: 90 dBA 8 h ... 115 dBA 1/4 h or less);
mixed exposure sum C/T must not exceed 1; dose D = 100 C/T; TWA = 16.61 log10(D/100) + 90; 85 dBA 8-h TWA is the hearing-conservation action
level; impulsive noise must not exceed 140 dB peak. Environmental noise limits (e.g. CPCB/IS, BS 7445 assessment) are a different framework.
"""
from __future__ import annotations

import math

OSHA_ACTION_LEVEL_DBA = 85.0
OSHA_PEL_DBA = 90.0
OSHA_PEAK_LIMIT_DB = 140.0


def osha_permissible_hours(L_dBA: float) -> float:
    return 8 / 2 ** ((L_dBA - 90) / 5)


def niosh_permissible_hours(L_dBA: float) -> float:
    """NIOSH recommended exposure limit: 85 dBA for 8 h with a 3 dB exchange rate (recalled)."""
    return 8 / 2 ** ((L_dBA - 85) / 3)


def dose_pct(exposures: list[tuple[float, float]], permissible=osha_permissible_hours) -> float:
    """exposures = [(level dBA, hours)]; dose = 100 sum C/T."""
    return 100 * sum(c / permissible(L) for L, c in exposures)


def twa_dBA(dose_percent: float) -> float:
    """OSHA 8-h TWA from dose: 16.61 log10(D/100) + 90."""
    return 16.61 * math.log10(dose_percent / 100) + 90


def sum_levels_dB(levels: list[float]) -> float:
    return 10 * math.log10(sum(10 ** (L / 10) for L in levels))


def point_source_level_dB(L1: float, r1_m: float, r2_m: float, extra_attenuation_dB: float = 0.0) -> float:
    """Free-field point source: L2 = L1 - 20 log10(r2/r1) - extra (ground, air absorption and barriers are the extra term)."""
    return L1 - 20 * math.log10(r2_m / r1_m) - extra_attenuation_dB


def distance_for_level_m(L1: float, r1_m: float, L_target: float) -> float:
    return r1_m * 10 ** ((L1 - L_target) / 20)

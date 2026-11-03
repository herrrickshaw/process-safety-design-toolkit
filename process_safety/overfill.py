"""Tank / vessel overfill protection arithmetic (high-level alarm placement, overfill time, spill volume).

Response and closure times are site data; the levels you adopt (critical high, safe fill, high-level alarm) follow your standard
(e.g. API 2350, OISD-STD-108/116, IEC 61511 for an overfill SIF): this module only does the volume/time arithmetic.
"""
from __future__ import annotations

import math


def time_to_overfill_s(spare_volume_m3: float, fill_rate_m3_h: float) -> float:
    return spare_volume_m3 / (fill_rate_m3_h / 3600)


def alarm_margin_m3(fill_rate_m3_h: float, operator_response_s: float, valve_closure_s: float, safety_factor: float = 1.0) -> float:
    """Volume that arrives between alarm and flow actually stopping."""
    return fill_rate_m3_h / 3600 * (operator_response_s + valve_closure_s) * safety_factor


def alarm_height_m(critical_high_m: float, tank_area_m2: float, fill_rate_m3_h: float, operator_response_s: float,
                   valve_closure_s: float, safety_factor: float = 1.0) -> float:
    """Highest level at which the high-level alarm may sit so the tank does not reach critical high before flow stops."""
    return critical_high_m - alarm_margin_m3(fill_rate_m3_h, operator_response_s, valve_closure_s, safety_factor) / tank_area_m2


def tank_area_m2(D_m: float) -> float:
    return math.pi * D_m * D_m / 4

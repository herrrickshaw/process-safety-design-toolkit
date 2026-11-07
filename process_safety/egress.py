"""Escape time arithmetic: required safe egress time (RSET) against available safe egress time (ASET).

    RSET = t_detect + t_premove + max(t_travel, t_flow)       t_travel = distance / speed       t_flow = people / (specific_flow x width)

The `max` form is the simple hydraulic bound: the last person is either limited by walking the distance or by the flow through the
narrowest exit, not by both added together. It ignores merging flows, stairs, queues that form upstream, and slower or assisted
people, so it is a screening check. Every number is an input (walking speed, specific flow through a door, pre-movement time,
ASET from a fire or smoke study); none is coded, because the values depend on the occupants and on the code the site follows.
Escape and rescue analysis (ESSA, EERA) is a team study, and this check does not replace it.
"""
from __future__ import annotations


def rset_s(distance_m: float, speed_m_s: float, people: int, width_m: float, specific_flow_per_m_s: float,
           detect_s: float, premove_s: float) -> dict:
    if min(distance_m, speed_m_s, width_m, specific_flow_per_m_s) <= 0 or people < 1 or detect_s < 0 or premove_s < 0:
        raise ValueError("distance, speed, width and specific flow must be positive, people at least 1, times not negative")
    t_travel = distance_m / speed_m_s
    t_flow = people / (specific_flow_per_m_s * width_m)
    governing = "flow through the exit" if t_flow > t_travel else "travel distance"
    return {"t_travel_s": t_travel, "t_flow_s": t_flow, "governing": governing, "rset_s": detect_s + premove_s + max(t_travel, t_flow)}


def margin(rset: float, aset_s: float) -> dict:
    """Margin = ASET - RSET and ratio ASET/RSET. Whether the ratio is enough is a criterion you supply, not one coded here."""
    if rset <= 0 or aset_s <= 0:
        raise ValueError("RSET and ASET must be positive")
    return {"aset_s": aset_s, "margin_s": aset_s - rset, "aset_over_rset": aset_s / rset, "escape_before_untenable": aset_s > rset}

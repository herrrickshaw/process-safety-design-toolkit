"""Fire-water hydraulics and demand arithmetic. SI units.

Hazen-Williams (NFPA 13 SI form) and orifice-nozzle flow are standard. REQUIRED APPLICATION RATES are NOT hard-coded as law:
the example 10.2 L/min/m2 vessel-exposure density is a widely quoted NFPA 15 figure; OISD-STD-116/117 requirements were not
read, so pass the density, simultaneous-area and duration your standard and the client specification require.
"""
from __future__ import annotations

import math


def hazen_williams_bar_per_m(Q_lpm: float, d_mm: float, C: float = 120.0) -> float:
    """NFPA 13 SI: p = 6.05e5 Q^1.85 / (C^1.85 d^4.87) bar/m (Q L/min, d mm internal)."""
    return 6.05e5 * Q_lpm ** 1.85 / (C ** 1.85 * d_mm ** 4.87)


def line_loss_bar(Q_lpm, d_mm, L_m, C=120.0, equivalent_length_m=0.0) -> float:
    return hazen_williams_bar_per_m(Q_lpm, d_mm, C) * (L_m + equivalent_length_m)


def velocity_m_s(Q_lpm: float, d_mm: float) -> float:
    return Q_lpm / 60000 / (math.pi * (d_mm / 1000) ** 2 / 4)


def nozzle_flow_lpm(d_mm: float, P_bar: float, Cd: float = 0.97, rho: float = 1000.0) -> float:
    """Plain orifice/nozzle discharge Q = Cd A sqrt(2 dP/rho); Cd is an input (vendor/NFPA K-factor if using spray nozzles)."""
    return Cd * math.pi * (d_mm / 1000) ** 2 / 4 * math.sqrt(2 * P_bar * 1e5 / rho) * 60000


def spray_demand_lpm(area_m2: float, density_lpm_m2: float = 10.2) -> float:
    return area_m2 * density_lpm_m2


def demand_summary(zones: dict[str, float], simultaneous: list[str], duration_h: float = 4.0, hose_streams_lpm: float = 0.0) -> dict:
    """Sum the demand of the zones that must run simultaneously (+ hose/monitor allowance); returns pump capacity and storage."""
    q = sum(zones[z] for z in simultaneous) + hose_streams_lpm
    return {"design_flow_lpm": q, "design_flow_m3_h": q * 0.06, "storage_m3": q * 0.06 * duration_h,
            "largest_zone": max(simultaneous, key=lambda z: zones[z])}


def pump_head_bar(residual_bar, loss_bar, static_bar=0.0) -> float:
    """Required pump discharge pressure = residual at the most remote point + pipe/fitting losses + static lift."""
    return residual_bar + loss_bar + static_bar

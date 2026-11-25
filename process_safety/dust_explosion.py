"""Dust explosion arithmetic from the cubic law: the deflagration index KSt and scaling of the maximum rate of pressure rise with volume.

Cubic law (the definition of the index): KSt = (dP/dt)max x V^(1/3), with (dP/dt)max in bar/s and V in m3, so KSt is in bar m/s and a dust
measured in a 20 L sphere can be compared with a larger vessel. The classes (St1 to St3) come from `atex.kst_class`. The cubic law is
conservative for scale-up because real vessels, with non-uniform clouds, rarely reach the sphere value.

NOT implemented: explosion vent area (NFPA 68, EN 14491) and suppression or isolation design. Those standards are paywalled and were not
read; NFPA 660 (2025) merged six legacy dust codes. A powderprocess.net guide lists the inputs such a calculation needs (Kst, Pmax, Pred,
Pstat, L/D) but gives no equations that were checked here. Use licensed software or a vendor, and treat this module as data handling.
"""
from __future__ import annotations

from . import atex


def kst_bar_m_s(dpdt_max_bar_s: float, volume_m3: float) -> float:
    if dpdt_max_bar_s <= 0 or volume_m3 <= 0:
        raise ValueError("dP/dt and volume must be positive")
    return dpdt_max_bar_s * volume_m3 ** (1.0 / 3.0)


def dpdt_max_bar_s(kst: float, volume_m3: float) -> float:
    if kst <= 0 or volume_m3 <= 0:
        raise ValueError("KSt and volume must be positive")
    return kst / volume_m3 ** (1.0 / 3.0)


def scale_dpdt_bar_s(dpdt_bar_s: float, from_volume_m3: float, to_volume_m3: float) -> float:
    """Maximum rate of pressure rise in another volume by the cubic law."""
    return dpdt_max_bar_s(kst_bar_m_s(dpdt_bar_s, from_volume_m3), to_volume_m3)


def explosion_class(kst: float) -> str:
    return atex.kst_class(kst)

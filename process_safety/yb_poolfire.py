"""Pool-fire burning rate, equilibrium pool size for a continuous spill, flame length and tilt (TNO Yellow Book, CPR 14E 2005, chapter 6).

Source (read from the owner-supplied PDF and the TNO and PGS copies): section 6.5.4 "Pool fires on land (confined)", steps 2 to 6.
  (6.66) m'' = m_inf'' (1 - exp(-k beta D));  Table 6.5 (Babrauskas 1983): LPG m_inf'' = 0.099 kg/m2 s, k beta = 1.4 1/m; butane 0.078 and 2.7
         (the table's "LPG" composition is not stated; propane is mapped to it here)
  (6.14) u_c = (g m'' D / rho_air)^(1/3);  (6.13) u* = u_w / u_c, taken as 1 when u_w < u_c (section 6.3.4.5)
  (6.12) L/D = 55 (m'' / (rho_air (g D)^(1/2)))^0.67 (u*)^-0.21
  (6.68-6.70) Fr = u_w^2/(g D); Re = u_w D / nu; tan(Theta)/cos(Theta) = 0.666 Fr^0.333 Re^0.117; Theta = asin(((4 c^2 + 1)^(1/2) - 1)/(2 c))
Equilibrium size of a continuously fed pool: the diameter where m''(D) pi D^2 / 4 equals the feed (the book describes this maximum pool size for a
spill fed from a tank, section 6.3.4.5). Wind enhancement of the burning rate (6.10) is not applied: the book states the wind influence is already
inside the flame-length correlation. Limits: confined-pool correlations applied to a free-spreading pool; not for alcohols; wind above about 5 m/s
may blow the fire out (book). Screening aid, not certified design.
"""
from __future__ import annotations

import math

from .constants import G as g_acc

LARGE_POOL = {"propane": (0.099, 1.4), "n-butane": (0.078, 2.7)}


def burning_flux_kg_m2_s(D_m: float, m_inf: float, k_beta: float) -> float:
    if not (D_m > 0 and m_inf > 0 and k_beta > 0):
        raise ValueError("D, m_inf and k_beta must be positive")
    return m_inf * (1.0 - math.exp(-k_beta * D_m))


def equilibrium_diameter_m(feed_kg_s: float, m_inf: float, k_beta: float) -> float:
    """Diameter at which burning removes the feed: m''(D) pi D^2 / 4 = feed (bisection; the left side increases with D)."""
    if not feed_kg_s > 0:
        raise ValueError("feed must be positive")
    lo, hi = 1e-6, 1e4
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        lo, hi = (mid, hi) if burning_flux_kg_m2_s(mid, m_inf, k_beta) * math.pi * mid * mid / 4.0 < feed_kg_s else (lo, mid)
    return 0.5 * (lo + hi)


def flame_length_m(D_m: float, m_flux: float, rho_air: float, wind_m_s: float) -> dict:
    """(6.12)-(6.14). Returns L, the characteristic wind speed and the scaled wind speed used."""
    uc = (g_acc * m_flux * D_m / rho_air) ** (1.0 / 3.0)
    ustar = max(1.0, wind_m_s / uc)
    L = D_m * 55.0 * (m_flux / (rho_air * math.sqrt(g_acc * D_m))) ** 0.67 * ustar ** -0.21
    return {"L_m": L, "u_c_m_s": uc, "u_star": ustar}


def flame_tilt_deg(D_m: float, wind_m_s: float, nu_air_m2_s: float) -> float:
    """(6.68)-(6.70). Zero wind gives zero tilt."""
    if wind_m_s <= 0:
        return 0.0
    Fr = wind_m_s ** 2 / (g_acc * D_m)
    Re = wind_m_s * D_m / nu_air_m2_s
    c = 0.666 * Fr ** 0.333 * Re ** 0.117
    return math.degrees(math.asin((math.sqrt(4.0 * c * c + 1.0) - 1.0) / (2.0 * c)))

"""Vapour-filled (unwetted) vessel in a fire: transient wall/gas model - does the PSV protect the vessel, or does it rupture first?

WHY A TRANSIENT MODEL AND NOT THE API 521 SHORTCUT. API 521 sizes the PSV for a gas-filled vessel with an empirical expression
A = F'.A_s/sqrt(P1). Its constants could not be verified from any open source here and its SI/US unit handling is easy to get wrong
(an error undersizes a safety device), so it is deliberately NOT coded. The open-access study Safety 2018, 4(1), 11
(doi:10.3390/safety4010011; ABSTRACT ONLY was retrievable) reports that for many gas-filled vessels the wall reaches rupture
temperature before the relieving pressure is reached, so a PSV alone gives "an unfounded sense of security". This model lets you
test exactly that for a given vessel, and compare a PSV with depressuring (blowdown).

Model (lumped, deliberately simple, SI):
  wall  : rho cp delta dTw/dt = q_abs - eps sigma (Tw^4 - T0^4) - h_in (Tw - Tg)
          q_abs = flux absorbed by a COLD wall (input; e.g. ~100 kW/m2 pool fire, ~250 kW/m2 jet fire - Scandpower-type values,
          from memory of secondary sources, verify). The radiative term caps Tw near the flame temperature.
  gas   : constant volume ideal gas (Z=1), m cv dTg/dt = h_in A (Tw - Tg) - mdot R_s Tg ; P = m R_s Tg / V
  valves: PSV opens at set pressure, recloses at 90% of set; blowdown valve (BDV) opens after a delay. Flow = Kd A G(P,T) with the
          isentropic orifice flux from relief.gas_mass_flux, discharging to atmosphere.
  fail  : thin-wall hoop stress P_g D/(2 delta) >= k_y(Tw) * strength, k_y = EN 1993-1-2 yield retention vs temperature
          (structural steel, recalled from memory - verify; strength defaults to a conservative 260 MPa minimum yield).
Assumptions you must own: h_in (internal gas film coefficient) is a guess; only the exposed wall is heated and no heat is
conducted to the unexposed wall or liquid; Z = 1; no creep (so rupture is predicted late for thick walls); flame flux constant.
Use for screening and for comparing options, not as a rupture-time guarantee.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from .relief import ATM, R, gas_mass_flux

SIGMA = 5.670374e-8

# EN 1993-1-2 yield strength retention factor vs steel temperature (deg C)
_KY = [(20, 1.0), (400, 1.0), (500, 0.78), (600, 0.47), (700, 0.23), (800, 0.11), (900, 0.06), (1000, 0.04), (1100, 0.02), (1200, 0.0)]


def ky(Tw_K: float) -> float:
    c = Tw_K - 273.15
    if c <= _KY[0][0]:
        return 1.0
    for (t0, k0), (t1, k1) in zip(_KY, _KY[1:]):
        if c <= t1:
            return k0 + (k1 - k0) * (c - t0) / (t1 - t0)
    return 0.0


@dataclass
class Vessel:
    volume_m3: float
    exposed_area_m2: float      # unwetted wall exposed to the fire
    diameter_m: float
    wall_mm: float
    M: float                    # kg/kmol
    k: float                    # Cp/Cv
    P0_kpag: float              # initial gauge pressure
    T0_K: float = 323.15        # initial gas and wall temperature
    strength_MPa: float = 260.0
    wall_rho: float = 7850.0
    wall_cp: float = 600.0


@dataclass
class FireResult:
    t_rupture_s: float | None
    t_relief_onset_s: float | None
    t_wall_593C_s: float | None
    peak_pressure_kpag: float
    peak_wall_K: float
    mass_discharged_kg: float
    final_pressure_kpag: float
    protected: bool
    notes: list[str] = field(default_factory=list)


def simulate(v: Vessel, q_kw_m2: float, psv_area_mm2: float = 0.0, psv_set_kpag: float | None = None, kd: float = 0.975,
             bdv_area_mm2: float = 0.0, bdv_open_s: float = 900.0, h_in: float = 20.0, emissivity: float = 0.8,
             t_end_s: float = 3600.0, dt_max: float = 1.0) -> FireResult:
    Rs = R / (v.M / 1000)           # J/kg/K
    cv = Rs / (v.k - 1)
    T0 = v.T0_K
    m = (v.P0_kpag + ATM) * 1e3 * v.volume_m3 / (Rs * T0)
    m0, Tg, Tw = m, T0, T0
    m_wall = v.wall_rho * v.wall_mm / 1000 * v.exposed_area_m2
    A = v.exposed_area_m2
    q_abs = q_kw_m2 * 1e3
    t = 0.0
    psv_open = False
    t_rupt = t_rel = t_593 = None
    pmax = v.P0_kpag
    twmax = Tw
    notes = []
    while t < t_end_s:
        P_abs = m * Rs * Tg / v.volume_m3 / 1e3  # kPa abs
        P_g = P_abs - ATM
        pmax, twmax = max(pmax, P_g), max(twmax, Tw)
        if t_593 is None and Tw >= 866.15:
            t_593 = t
        if psv_area_mm2 > 0 and psv_set_kpag is not None:
            if P_g >= psv_set_kpag:
                if not psv_open and t_rel is None:
                    t_rel = t
                psv_open = True
            elif P_g < 0.9 * psv_set_kpag:
                psv_open = False
        mdot = 0.0
        if P_abs > ATM * 1.0005:
            G, _ = gas_mass_flux(P_abs, ATM, Tg, v.M, v.k, 1.0)
            area = (kd * psv_area_mm2 if psv_open else 0.0) + (kd * bdv_area_mm2 if t >= bdv_open_s else 0.0)
            mdot = area * 1e-6 * G
        # rupture check (thin-wall hoop stress vs retained strength)
        hoop = max(P_g, 0.0) * 1e3 * v.diameter_m / (2 * v.wall_mm / 1000) / 1e6  # MPa
        if hoop >= ky(Tw) * v.strength_MPa and t > 0:
            t_rupt = t
            break
        dt = dt_max if mdot <= 0 else min(dt_max, 0.05 * m / mdot)
        q_rad = emissivity * SIGMA * (Tw ** 4 - T0 ** 4)
        q_to_gas = h_in * A * (Tw - Tg)
        dTw = (q_abs * A - q_rad * A - q_to_gas) / (m_wall * v.wall_cp)
        dTg = (q_to_gas - mdot * Rs * Tg) / (m * cv)
        Tw += dTw * dt
        Tg += dTg * dt
        m = max(m - mdot * dt, 1e-9)
        t += dt
    P_end = m * Rs * Tg / v.volume_m3 / 1e3 - ATM
    if t_rupt is None and t_593 is not None and P_end > 0.5 * (psv_set_kpag or v.P0_kpag):
        notes.append("wall passed 593 C (1100 F) with pressure still above half the set/initial value: high rupture risk even if no rupture was predicted (no creep modelled)")
    if t_rupt is not None and (t_rel is None or t_rupt <= t_rel):
        notes.append("vessel ruptured BEFORE the PSV relieved: the PSV did not protect it; use depressuring and/or passive fire protection (API 521)")
    if t_rupt is not None and t_rel is not None and t_rupt > t_rel:
        notes.append("PSV lifted and held pressure but the vessel still ruptured later as the wall lost strength: a PSV alone is not "
                     "sufficient; add depressuring, passive fire protection or fire-water (API 521)")
    return FireResult(t_rupt, t_rel, t_593, pmax, twmax, m0 - m, P_end, t_rupt is None, notes)

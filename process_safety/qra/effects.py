"""Step 3 - consequence analysis: source terms and lethality footprints built on the toolkit's existing models.

Every outcome becomes an `Effect` that answers p_fatal(dx, dy) for a person outdoors at (dx downwind, dy crosswind) metres from
the release point. Fires and fireballs are radial (wind-independent here); flash fires and toxic clouds follow the plume.

Models (all screening; each flagged in its own module):
* source term   - release.gas_release_kg_s / release.liquid_release_kg_s, adiabatic flash fraction cp(T-Tb)/Hv with an aerosol
                  multiplier (default 2, a common rule of thumb, flagged), duration = isolatable inventory / initial rate.
* jet fire      - point source, Q = m_air x Hc, radiant fraction flare.radiant_fraction(M) (Hajek-Ludwig), flame length
                  L = 0.00326 Q^0.478 (Q in W; the API 521 Figure fit as reproduced by TCEQ, 4.56e-3 q^0.478 in cal/s for a 45 deg
                  flame height, which is the same curve), engulfment p = 1 within L/2 in every direction (direction unknown).
* pool fire     - pool_fire.pool_fire (Burgess / Thomas / point source); area = bund, else steady burn-off area of the rained-out
                  rate, capped at max_pool_area_m2; p = 1 inside the pool.
* fireball      - fireball.fireball (CCPS / Roberts); dose over the fireball duration; p = 1 under the ball.
* flash fire    - p = flash_fire_lethality (default 1) inside the ground-level LFL footprint (Gaussian plume, dispersion.py:
                  NEUTRAL GAS - a dense gas such as propane spreads wider and shorter); instantaneous clouds as an undiluted
                  hemisphere at LFL concentration.
* VCE           - flammable mass = airborne rate x travel time to the LFL distance (or the instantaneous airborne mass), TNT
                  equivalence (explosion.py, yield an input), Eisenberg lung-haemorrhage probit Pr = -77.1 + 6.91 ln P[Pa],
                  composite with p = 1 inside the cloud. Optional blast_threshold_kpa sets p = 1 above a chosen overpressure.
* toxic         - Gaussian plume of the toxic component and consequence.TOXIC_PROBITS (or study-supplied a, b, n).
Thermal lethality: Eisenberg probit (consequence.probit_thermal) with exposure time `thermal_s` (escape time, input).

`override` lets a study replace any computed effect with external results (e.g. DNV Phast / RISKCURVES distances):
    {"type": "radial", "table": [[r_m, p], ...]}   or   {"type": "footprint", "length_m": L, "half_width_m": W, "p": 1.0}
"""
from __future__ import annotations

import bisect
import math

from .. import consequence, dispersion, explosion, fireball, flare, pool_fire, release

R = 8.314462618
ATM_KPA = 101.325
P_MIN = 1e-6


def _frac(pr: float) -> float:
    return consequence.fraction_from_probit(pr)


def thermal_p(I_kW_m2: float, t_s: float) -> float:
    if I_kW_m2 <= 0.05:
        return 0.0
    return _frac(consequence.probit_thermal(I_kW_m2, t_s))


def lung_p(P_kpa: float) -> float:
    """Eisenberg probit for death by lung haemorrhage, P = peak side-on overpressure in Pa."""
    return 0.0 if P_kpa <= 1 else _frac(-77.1 + 6.91 * math.log(P_kpa * 1e3))


# ------------------------------------------------------------------ source term
def source_term(section: dict, material: dict, hole_mm: float, instantaneous: bool, conv: dict) -> dict:
    """Release rate, duration, airborne (vapour + aerosol) and rained-out fractions for one hole size."""
    phase = material["phase_stored"]
    P_g = section["P_kpag"]
    T = section["T_K"]
    inv = section["inventory_kg"]
    hole_m = hole_mm / 1000
    if instantaneous or hole_m <= 0:
        rate = flash = air = 0.0
        if phase == "gas":
            flash = air = 1.0
        else:
            flash = max(0.0, min(1.0, material["cp_liquid_kJ_kgK"] * (T - material["Tb_K"]) / material["Hv_kJ_kg"]))
            air = min(1.0, conv["aerosol_factor"] * flash) if flash > 0 else 0.0
        return {"hole_mm": hole_mm, "instantaneous": True, "rate_kg_s": 0.0, "rate_for_ignition_kg_s": inv / conv["instantaneous_below_s"],
                "duration_s": 0.0, "exposure_duration_s": 0.0, "mass_kg": inv, "flash_fraction": flash, "airborne_fraction": air,
                "airborne_rate_kg_s": 0.0, "rainout_rate_kg_s": 0.0, "phase": phase}
    if phase == "gas":
        rate = release.gas_release_kg_s(hole_m, P_g + ATM_KPA, T, material["M"], material["k"], Cd=conv["Cd_gas"])
        flash = air = 1.0
    else:
        rate = release.liquid_release_kg_s(hole_m, material["rho_liquid"], P_g * 1e3, section.get("liquid_head_m", 0.0), Cd=conv["Cd_liquid"])
        flash = max(0.0, min(1.0, material["cp_liquid_kJ_kgK"] * (T - material["Tb_K"]) / material["Hv_kJ_kg"]))
        air = min(1.0, conv["aerosol_factor"] * flash) if flash > 0 else 0.0
    duration = inv / rate if rate > 0 else float("inf")
    inst = instantaneous or duration < conv["instantaneous_below_s"]
    if inst:
        rate_eq = inv / conv["instantaneous_below_s"]  # equivalent rate, used only to pick ignition-probability bands
        duration = 0.0
    else:
        rate_eq = rate
    return {"hole_mm": hole_mm, "instantaneous": inst, "rate_kg_s": rate, "rate_for_ignition_kg_s": rate_eq,
            "duration_s": duration, "exposure_duration_s": min(duration, conv["max_duration_s"]) if not inst else 0.0,
            "mass_kg": inv if inst else min(inv, rate * conv["max_duration_s"]), "flash_fraction": flash, "airborne_fraction": air,
            "airborne_rate_kg_s": rate * air, "rainout_rate_kg_s": rate * (1 - air), "phase": phase}


# ------------------------------------------------------------------ effect primitives
class Effect:
    kind = "effect"
    directional = False
    reach = 0.0            # max downwind (or radial) distance with p > P_MIN
    half_width = 0.0       # crosswind half-width bound (directional only)
    x_back = 0.0           # upwind extent (directional only)

    def p(self, dx: float, dy: float) -> float:  # pragma: no cover - interface
        raise NotImplementedError


class Radial(Effect):
    """Radially symmetric lethality, tabulated; centre may be offset downwind by xc (then it becomes directional)."""

    def __init__(self, p_of_r, kind: str, xc: float = 0.0, r_max: float = 20000.0, n: int = 400, engulf_r: float = 0.0):
        self.kind = kind
        self.xc = xc
        r = 1.0
        last_pos = 0.0
        while r < r_max:  # outward scan to find reach
            if p_of_r(r) > P_MIN:
                last_pos = r
            elif r > 4 * max(last_pos, 1.0) and r > 50:
                break
            r *= 1.05
        self.reach_r = max(last_pos * 1.06, engulf_r)
        rs = [self.reach_r * i / n for i in range(n + 1)]
        ps = [1.0 if r_ <= engulf_r else min(1.0, max(0.0, p_of_r(max(r_, 0.1)))) for r_ in rs]
        for i in range(n - 1, -1, -1):  # lethality must not increase with distance (fireball cos factor, near-field quirks)
            ps[i] = max(ps[i], ps[i + 1])
        self.rs, self.ps = rs, ps
        self.directional = xc != 0.0
        self.reach = xc + self.reach_r
        self.x_back = max(0.0, self.reach_r - xc)
        self.half_width = self.reach_r

    def p_r(self, r: float) -> float:
        if r >= self.reach_r:
            return 0.0
        i = bisect.bisect_right(self.rs, r) - 1
        r0, r1 = self.rs[i], self.rs[i + 1]
        return self.ps[i] + (self.ps[i + 1] - self.ps[i]) * (r - r0) / (r1 - r0)

    def p(self, dx, dy):
        return self.p_r(math.hypot(dx - self.xc, dy))


class Plume(Effect):
    """Continuous ground-level footprint from the Gaussian plume. mode='threshold' (p = p_in where C >= c_thr) or 'probit'."""
    directional = True

    def __init__(self, Q_g_s, u, H, stability, kind, c_thr_g_m3, mode="threshold", p_in=1.0, probit=None, M=None, t_min=None):
        self.kind, self.Q, self.u, self.H, self.st = kind, Q_g_s, u, H, stability
        self.c_thr, self.mode, self.p_in, self.probit, self.M, self.t_min = c_thr_g_m3, mode, p_in, probit, M, t_min
        far, w, x = 0.0, 0.0, 1.0
        while x < 30000:
            c = dispersion.concentration_g_m3(Q_g_s, u, H, x, stability=stability)
            if c >= c_thr_g_m3:
                far = x
                sy, _ = dispersion.sigmas(x, stability)
                w = max(w, sy * math.sqrt(2 * math.log(c / c_thr_g_m3)))
            elif far and x > 3 * far:
                break
            x *= 1.03
        self.reach, self.half_width = far, w

    def p(self, dx, dy):
        if dx <= 0 or dx > self.reach or abs(dy) > self.half_width:
            return 0.0
        c = dispersion.concentration_g_m3(self.Q, self.u, self.H, dx, dy, 0.0, self.st)
        if c < self.c_thr:
            return 0.0
        if self.mode == "threshold":
            return self.p_in
        ppm = dispersion.mg_m3_to_ppm(c * 1e3, self.M)
        return _frac(consequence.probit_toxic(ppm, self.t_min, *self.probit))


class Footprint(Effect):
    """External (e.g. Phast) cloud footprint: ellipse of length L downwind, half-width W, lethality p inside."""
    directional = True

    def __init__(self, L, W, p_in, kind):
        self.kind, self.reach, self.half_width, self.p_in = kind, L, W, p_in

    def p(self, dx, dy):
        if dx <= 0 or dx > self.reach:
            return 0.0
        a = self.reach / 2
        return self.p_in if ((dx - a) / a) ** 2 + (dy / self.half_width) ** 2 <= 1 else 0.0


class Composite(Effect):
    """Several simultaneous effects on one branch (e.g. flash fire + pool fire): p = 1 - prod(1 - p_i)."""

    def __init__(self, parts: list[Effect], kind: str):
        self.parts = [e for e in parts if e is not None]
        self.kind = kind
        self.directional = any(e.directional for e in self.parts)
        self.reach = max((e.reach for e in self.parts), default=0.0)
        self.half_width = max((e.half_width if e.directional else e.reach for e in self.parts), default=0.0)
        self.x_back = max((e.x_back if e.directional else e.reach for e in self.parts), default=0.0)

    def p(self, dx, dy):
        q = 1.0
        for e in self.parts:
            q *= 1 - e.p(dx, dy)
        return 1 - q


def from_override(ov: dict, kind: str) -> Effect:
    if ov["type"] == "radial":
        tab = sorted(ov["table"])
        rs = [r for r, _ in tab]
        ps = [p for _, p in tab]

        def f(r):
            if r >= rs[-1]:
                return 0.0
            if r <= rs[0]:
                return ps[0]
            i = bisect.bisect_right(rs, r) - 1
            return ps[i] + (ps[i + 1] - ps[i]) * (r - rs[i]) / (rs[i + 1] - rs[i])
        return Radial(f, kind, r_max=rs[-1] * 1.01)
    if ov["type"] == "footprint":
        return Footprint(ov["length_m"], ov["half_width_m"], ov.get("p", 1.0), kind)
    raise ValueError(f"unknown override type {ov['type']!r}")


# ------------------------------------------------------------------ outcome builders
def lfl_g_m3(material: dict, T_K: float = 298.15) -> float:
    return material["LFL_vol"] * ATM_KPA * 1e3 * material["M"] / (R * T_K)


def jet_fire(st: dict, material: dict, conv: dict) -> Radial | None:
    m = st["airborne_rate_kg_s"] if st["phase"] != "gas" else st["rate_kg_s"]
    if m <= 0:
        return None
    Q = m * material["Hc_MJ_kg"] * 1e6
    L = 0.00326 * Q ** 0.478
    F = flare.radiant_fraction(material["M"]) if material.get("radiant_fraction") is None else material["radiant_fraction"]
    t = conv["thermal_s"]
    e = Radial(lambda r: thermal_p(flare.radiation_kW_m2(Q, max(r, 0.5), F), t), "jet_fire", engulf_r=L / 2)
    e.info = {"Q_MW": Q / 1e6, "flame_length_m": L, "radiant_fraction": F}
    return e


def pool_area(st: dict, section: dict, material: dict) -> float:
    """Instantaneous: the bund (or max_pool_area_m2 if unbunded). Continuous: the steady burn-off area rained-out rate / m'',
    capped by the bund / max_pool_area_m2 - a small leak inside a large bund makes a small pool."""
    cap = section.get("bund_area_m2") or section.get("max_pool_area_m2", 1000.0)
    if st["instantaneous"]:
        return cap
    m2 = pool_fire.burning_rate_kg_m2_s(material["Hc_MJ_kg"] * 1e3, material["Hv_kJ_kg"], material["cp_liquid_kJ_kgK"], material["Tb_K"])
    return min(cap, st["rainout_rate_kg_s"] / m2) if m2 > 0 else cap


def pool(st: dict, section: dict, material: dict, conv: dict) -> Radial | None:
    if st["phase"] == "gas" or (not st["instantaneous"] and st["rainout_rate_kg_s"] <= 0) or (st["instantaneous"] and st["airborne_fraction"] >= 1):
        return None
    A = pool_area(st, section, material)
    pf = pool_fire.pool_fire(A, material["Hc_MJ_kg"] * 1e3, material["Hv_kJ_kg"], material["cp_liquid_kJ_kgK"], material["Tb_K"],
                             radiant_fraction=material.get("pool_radiant_fraction", 0.25))
    t = conv["thermal_s"]
    e = Radial(lambda r: thermal_p(pool_fire.incident_kW_m2(pf, r), t), "pool_fire", engulf_r=pf["diameter_m"] / 2)
    e.info = {"area_m2": A, "diameter_m": pf["diameter_m"], "flame_height_m": pf["flame_height_m"], "Q_MW": pf["heat_release_MW"]}
    return e


def fireball_effect(st: dict, material: dict, conv: dict) -> Radial | None:
    m = st["mass_kg"] * (1.0 if st["phase"] == "gas" else conv["fireball_mass_fraction"])  # CCPS practice: whole contents
    if m <= 0:
        return None
    fb = fireball.fireball(m, material["Hc_MJ_kg"])
    e = Radial(lambda r: thermal_p(fireball.incident_kW_m2(fb, r), fb["duration_s"]), "fireball", engulf_r=fb["diameter_m"] / 2)
    e.info = {"mass_kg": m, **fb}
    return e


def flash_fire(st, section, material, wx, conv):
    c_lfl = lfl_g_m3(material)
    if st["instantaneous"]:
        m = st["mass_kg"] * st["airborne_fraction"]
        if m <= 0:
            return None
        Rh = (3 * m * 1e3 / (2 * math.pi * c_lfl)) ** (1 / 3)
        e = Radial(lambda r: 0.0, "flash_fire", engulf_r=Rh)
        e.ps = [conv["flash_fire_lethality"] if p > 0 else 0 for p in e.ps]
        e.info = {"cloud_radius_m": Rh, "airborne_kg": m}
        return e
    q = st["airborne_rate_kg_s"]
    if q <= 0:
        return None
    e = Plume(q * 1e3, wx["u"], section.get("release_height_m", 1.0), wx["stability"], "flash_fire", c_lfl, p_in=conv["flash_fire_lethality"])
    e.info = {"lfl_distance_m": e.reach, "half_width_m": e.half_width}
    return e


def vce(st, section, material, wx, conv):
    ff = flash_fire(st, section, material, wx, conv)
    if ff is None:
        return None
    if st["instantaneous"]:
        m, xc = st["mass_kg"] * st["airborne_fraction"], 0.0
    else:
        x_lfl = ff.reach
        m = min(st["airborne_rate_kg_s"] * x_lfl / wx["u"], st["mass_kg"] * st["airborne_fraction"])
        xc = x_lfl / 2
    if m <= 0:
        return ff
    W = explosion.tnt_equivalent_kg(m, material["Hc_MJ_kg"], conv["vce_yield"])
    thr = conv.get("blast_threshold_kpa")

    def p_blast(r):
        P = explosion.kinney_graham_kpa(W, max(r, 0.5 * W ** (1 / 3)))
        return 1.0 if thr and P >= thr else lung_p(P)
    blast = Radial(p_blast, "vce_blast", xc=xc)
    e = Composite([ff, blast], "vce")
    e.info = {"flammable_mass_kg": m, "tnt_kg": W, "centre_downwind_m": xc, **getattr(ff, "info", {})}
    return e


def toxic(st, section, material, wx, conv):
    tox = material.get("toxic")
    if not tox or st["instantaneous"]:
        return None
    w = tox["mole_fraction"] * tox["M"] / material.get("M", tox["M"]) if "mole_fraction" in tox else tox["mass_fraction"]
    Q = st["airborne_rate_kg_s"] * w * 1e3
    if Q <= 0:
        return None
    probit = tuple(tox["probit"]) if "probit" in tox else consequence.TOXIC_PROBITS[tox["component"].lower()]
    t_min = max(st["exposure_duration_s"], 60.0) / 60
    a, b, n = probit
    c_ppm_thr = (math.exp((consequence.probit_from_fraction(1e-4) - a) / b) / t_min) ** (1 / n)
    c_thr = dispersion.ppm_to_mg_m3(c_ppm_thr, tox["M"]) / 1e3
    e = Plume(Q, wx["u"], section.get("release_height_m", 1.0), wx["stability"], "toxic", c_thr, mode="probit", probit=probit, M=tox["M"], t_min=t_min)
    e.info = {"toxic_rate_g_s": Q, "exposure_min": t_min, "reach_m": e.reach}
    return e

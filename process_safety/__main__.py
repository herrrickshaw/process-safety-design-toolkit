"""CLI: python -m process_safety <relief-gas|relief-steam|relief-liquid|relief-fire|tank-normal|tank-fire|vapour-fire|plume|blowdown|hazop-csv|pool-fire|depressure|steel-fire|flare|lopa|pfd|fireball|coverage> ..."""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys

from . import depressuring, dispersion, fireball, flare, hazop, pool_fire, relief, release, sil, standards, structural_fire, tank_venting, vapour_fire


def _out(obj):
    print(json.dumps(dataclasses.asdict(obj) if dataclasses.is_dataclass(obj) else obj, indent=2, default=float))


def main(argv=None):
    p = argparse.ArgumentParser(prog="process_safety", description=__doc__)
    s = p.add_subparsers(dest="cmd", required=True)

    g = s.add_parser("relief-gas", help="API 520-I gas/vapour PSV area")
    g.add_argument("--W", type=float, required=True, help="required relieving rate kg/h")
    g.add_argument("--T", type=float, required=True, help="relieving temperature K")
    g.add_argument("--set-g", type=float, required=True, help="set pressure kPag")
    g.add_argument("--back-g", type=float, default=0.0, help="total back pressure kPag")
    g.add_argument("--case", choices=list(relief.ACCUMULATION), default="single_non_fire")
    g.add_argument("--M", type=float, required=True)
    g.add_argument("--k", type=float, required=True, help="Cp/Cv")
    g.add_argument("--Z", type=float, default=1.0)
    g.add_argument("--Kb", type=float, default=1.0)
    g.add_argument("--Kc", type=float, default=1.0, help="0.9 if rupture disk upstream")

    st = s.add_parser("relief-steam")
    st.add_argument("--W", type=float, required=True)
    st.add_argument("--set-g", type=float, required=True)
    st.add_argument("--case", choices=list(relief.ACCUMULATION), default="single_non_fire")
    st.add_argument("--Ksh", type=float, default=1.0)

    li = s.add_parser("relief-liquid")
    li.add_argument("--Q", type=float, required=True, help="m3/h")
    li.add_argument("--rho", type=float, required=True)
    li.add_argument("--set-g", type=float, required=True)
    li.add_argument("--back-g", type=float, default=0.0)
    li.add_argument("--mu", type=float, default=1.0, help="cP")

    f = s.add_parser("relief-fire", help="API 521 liquid-wetted fire case")
    f.add_argument("--wetted-area", type=float, help="m2 (else give vessel geometry)")
    f.add_argument("--D", type=float); f.add_argument("--L", type=float); f.add_argument("--level", type=float)
    f.add_argument("--orientation", choices=["horizontal", "vertical"], default="horizontal")
    f.add_argument("--elevation", type=float, default=0.0)
    f.add_argument("--latent", type=float, required=True, help="latent heat kJ/kg at relieving conditions")
    f.add_argument("--F", type=float, default=1.0)
    f.add_argument("--no-drainage", action="store_true")

    tn = s.add_parser("tank-normal", help="API 2000 normal (thermal + liquid movement) venting")
    tn.add_argument("--volume", type=float, required=True, help="tank capacity m3")
    tn.add_argument("--fill", type=float, default=0.0, help="max filling rate m3/h")
    tn.add_argument("--empty", type=float, default=0.0, help="max emptying rate m3/h")
    tn.add_argument("--volatile", action="store_true", help="flash point < 37.8 C or boiling point < 148.9 C")

    tf = s.add_parser("tank-fire", help="API 2000 emergency venting for fire exposure")
    tf.add_argument("--shape", choices=["sphere", "horizontal", "vertical"])
    tf.add_argument("--D", type=float); tf.add_argument("--L", type=float, default=0.0)
    tf.add_argument("--elevation", type=float, default=0.0)
    tf.add_argument("--wetted-area", type=float)
    tf.add_argument("--F", default="1.0", help=f"number or one of: {', '.join(tank_venting.F_FACTORS)}")
    tf.add_argument("--design-barg", type=float, default=0.07)
    tf.add_argument("--normal-capacity", type=float, default=0.0, help="outbreathing capacity of installed normal vents, Nm3/h")
    tf.add_argument("--L-kj-kg", type=float, help="latent heat (default hexane basis)")
    tf.add_argument("--T", type=float, help="relieving vapour temperature K")
    tf.add_argument("--M", type=float, help="vapour molecular weight")

    vf = s.add_parser("vapour-fire", help="transient vapour-filled vessel fire: PSV vs rupture vs blowdown")
    for n, d, t in (("volume", None, float), ("area", None, float), ("D", None, float), ("wall-mm", None, float), ("M", None, float),
                    ("k", None, float), ("p0-g", None, float)):
        vf.add_argument("--" + n, type=t, required=True)
    vf.add_argument("--q", type=float, default=100.0, help="absorbed flux kW/m2 (pool ~100, jet ~250: verify)")
    vf.add_argument("--psv-area", type=float, default=0.0, help="mm2"); vf.add_argument("--psv-set-g", type=float)
    vf.add_argument("--bdv-area", type=float, default=0.0, help="mm2"); vf.add_argument("--bdv-open-s", type=float, default=900.0)
    vf.add_argument("--strength", type=float, default=260.0, help="MPa (min yield; conservative)")
    vf.add_argument("--h-in", type=float, default=20.0); vf.add_argument("--t-end", type=float, default=3600.0)

    pl = s.add_parser("plume", help="Gaussian plume screening (neutral gas): max ground conc and distance to a threshold")
    pl.add_argument("--Q", type=float, required=True, help="release g/s"); pl.add_argument("--u", type=float, default=3.0)
    pl.add_argument("--H", type=float, default=0.0, help="effective release height m"); pl.add_argument("--stability", default="D")
    pl.add_argument("--threshold-ppm", type=float); pl.add_argument("--M", type=float, help="molar mass for ppm conversion")

    bd = s.add_parser("blowdown", help="adiabatic vessel blowdown through a hole")
    for n in ("volume", "p0", "T0", "M", "k", "hole-d"):
        bd.add_argument("--" + n, type=float, required=True)
    bd.add_argument("--t-end", type=float, default=600.0)

    hz = s.add_parser("hazop-csv", help="write a HAZOP worksheet skeleton (CSV, opens in Excel)")
    hz.add_argument("--node", required=True); hz.add_argument("--intent", default="")
    hz.add_argument("--params", nargs="*"); hz.add_argument("--out", required=True)

    pf = s.add_parser("pool-fire", help="pool fire burn rate, flame height, distances to radiation levels")
    for n in ("area", "hc", "hv", "cp", "tb"):
        pf.add_argument("--" + n, type=float, required=True)
    pf.add_argument("--fraction", type=float, default=0.25)

    dp = s.add_parser("depressure", help="time to target pressure through an orifice (isothermal and adiabatic) + min gas temperature")
    for n in ("volume", "p0", "pt", "T0", "M", "k", "area"):
        dp.add_argument("--" + n, type=float, required=True)

    sf = s.add_parser("steel-fire", help="steel temperature vs time in a hydrocarbon fire; time to critical temperature")
    sf.add_argument("--am-v", type=float, required=True, help="section factor Am/V 1/m"); sf.add_argument("--crit", type=float, default=550.0)
    sf.add_argument("--minutes", type=float, default=120.0)
    sf.add_argument("--iso", action="store_true", help="use ISO 834 instead of the hydrocarbon curve")

    fl = s.add_parser("flare", help="API 521 point-source radiation")
    fl.add_argument("--mass", type=float, required=True, help="kg/s")
    fl.add_argument("--lhv", type=float, required=True, help="MJ/kg")
    fl.add_argument("--mw", type=float, required=True)
    fl.add_argument("--flame-length", type=float)
    fl.add_argument("--tau", type=float, default=1.0)

    lo = s.add_parser("lopa")
    lo.add_argument("--ie", type=float, required=True, help="initiating event freq /yr")
    lo.add_argument("--ipl", type=float, nargs="*", default=[], help="PFD of each independent protection layer")
    lo.add_argument("--target", type=float, required=True, help="tolerable frequency /yr")
    lo.add_argument("--modifier", type=float, default=1.0)

    pf = s.add_parser("pfd")
    pf.add_argument("--arch", choices=["1oo1", "1oo2", "2oo2", "2oo3"], required=True)
    pf.add_argument("--lambda-du", type=float, required=True, help="per hour")
    pf.add_argument("--ti-years", type=float, required=True)
    pf.add_argument("--beta", type=float, default=0.0)

    fb = s.add_parser("fireball")
    fb.add_argument("--mass", type=float, required=True, help="kg")
    fb.add_argument("--hc", type=float, required=True, help="MJ/kg")
    fb.add_argument("--fraction", type=float, default=0.3)

    s.add_parser("coverage")
    a = p.parse_args(argv)

    if a.cmd == "relief-gas":
        P1 = relief.relieving_pressure_kpa(a.set_g, a.case)
        _out(relief.gas_area(a.W, a.T, P1, a.back_g + relief.ATM, a.M, a.k, a.Z, Kb=a.Kb, Kc=a.Kc, set_g_kpa=a.set_g))
    elif a.cmd == "relief-steam":
        _out(relief.steam_area(a.W, relief.relieving_pressure_kpa(a.set_g, a.case), Ksh=a.Ksh))
    elif a.cmd == "relief-liquid":
        P1 = a.set_g * 1.10 + relief.ATM
        _out(relief.liquid_area(a.Q, a.rho, P1, a.back_g + relief.ATM, a.mu))
    elif a.cmd == "relief-fire":
        A = a.wetted_area or relief.wetted_area_cylinder(a.D, a.L, a.level, a.orientation, a.elevation)
        W = relief.fire_relief_rate_kg_h(A, a.latent, a.F, not a.no_drainage)
        _out({"wetted_area_m2": A, "heat_input_kW": relief.fire_heat_input_W(A, a.F, not a.no_drainage) / 1e3,
              "relief_rate_kg_h": W, "note": "relieving pressure for fire = set x 1.21 + atm; feed W to relief-gas"})
    elif a.cmd == "tank-normal":
        _out(tank_venting.normal_venting(a.volume, a.fill, a.empty, a.volatile))
    elif a.cmd == "tank-fire":
        A = a.wetted_area or tank_venting.wetted_area_m2(a.shape, a.D, a.L, a.elevation)
        F = tank_venting.F_FACTORS.get(a.F) if a.F in tank_venting.F_FACTORS else float(a.F)
        kw = {k: v for k, v in (("L_kJ_kg", a.L_kj_kg), ("T_K", a.T), ("M", a.M)) if v}
        req = tank_venting.fire_venting_Nm3h(A, F, design_barg=a.design_barg, **kw)
        _out({"wetted_area_m2": A, "F": F, "required_Nm3h_eq1B": req,
              "required_Nm3h_simplified": tank_venting.fire_venting_simplified(A, F, a.design_barg),
              "additional_emergency_vent_Nm3h": tank_venting.emergency_vent_shortfall_Nm3h(req, a.normal_capacity),
              "note": "API 2000 5th ed. (1998); a frangible roof-to-shell joint may replace emergency vents (4.3.3.1)"})
    elif a.cmd == "vapour-fire":
        v = vapour_fire.Vessel(a.volume, a.area, a.D, a.wall_mm, a.M, a.k, a.p0_g, strength_MPa=a.strength)
        _out(vapour_fire.simulate(v, a.q, a.psv_area, a.psv_set_g, bdv_area_mm2=a.bdv_area, bdv_open_s=a.bdv_open_s,
                                  h_in=a.h_in, t_end_s=a.t_end))
    elif a.cmd == "plume":
        c, x = dispersion.max_ground_concentration(a.Q, a.u, a.H, a.stability)
        out = {"max_ground_conc_g_m3": c, "at_distance_m": x}
        if a.M:
            out["max_ground_conc_ppm"] = dispersion.mg_m3_to_ppm(c * 1000, a.M)
        if a.threshold_ppm and a.M:
            out["farthest_distance_above_threshold_m"] = dispersion.distance_to_threshold_m(
                a.Q, a.u, a.H, dispersion.ppm_to_mg_m3(a.threshold_ppm, a.M) / 1000, a.stability)
        out["warning"] = "neutral-buoyancy screening only; dense gases need a dense-gas model"
        _out(out)
    elif a.cmd == "blowdown":
        r = release.blowdown_adiabatic(a.volume, a.p0, a.T0, a.M, a.k, a.hole_d, t_end_s=a.t_end)
        r.pop("series"); _out(r)
    elif a.cmd == "hazop-csv":
        n = hazop.to_csv(hazop.generate(a.node, a.intent, a.params), a.out)
        _out({"rows": n, "file": a.out})
    elif a.cmd == "pool-fire":
        r = pool_fire.pool_fire(a.area, a.hc, a.hv, a.cp, a.tb, radiant_fraction=a.fraction)
        r["distance_m"] = {str(q): round(pool_fire.distance_to_flux_m(r, q), 1) for q in (37.5, 12.5, 4.73, 1.58)}
        r["note"] = "point-source: unreliable inside ~2 pool diameters; no wind tilt"
        _out(r)
    elif a.cmd == "depressure":
        k = a.k
        _out({"isothermal_s": depressuring.depressuring_time_s(a.volume, a.p0, a.pt, a.T0, a.M, k, a.area, mode="isothermal"),
              "adiabatic_s": depressuring.depressuring_time_s(a.volume, a.p0, a.pt, a.T0, a.M, k, a.area, mode="adiabatic"),
              "min_gas_temperature_K_isentropic": depressuring.min_gas_temperature_K(a.T0, a.p0, a.pt, k),
              "note": "gas phase only; the isentropic temperature is a screening lower bound for MDMT, not metal temperature"})
    elif a.cmd == "steel-fire":
        h = structural_fire.steel_temperature_history(a.am_v, structural_fire.iso834_C if a.iso else structural_fire.hydrocarbon_C,
                                                      t_end_min=a.minutes)
        _out({"time_to_critical_min": structural_fire.time_to_critical_min(h, a.crit), "critical_C": a.crit,
              "steel_C_at": {str(t): round(T) for t, T in h if t in (5, 10, 15, 30, 60, 120)}})
    elif a.cmd == "flare":
        F = flare.radiant_fraction(a.mw); Q = flare.heat_release_W(a.mass, a.lhv)
        _out({"heat_release_MW": Q / 1e6, "radiant_fraction": F, **flare.radiation_checks(Q, F, a.flame_length, a.tau)})
    elif a.cmd == "lopa":
        _out(sil.lopa(a.ie, a.ipl, a.target, a.modifier))
    elif a.cmd == "pfd":
        v = sil.pfd_avg(a.arch, a.lambda_du, a.ti_years * 8760, a.beta)
        _out({"pfd_avg": v, "rrf": 1 / v, "achieves": sil.sil_for_pfd(v)})
    elif a.cmd == "fireball":
        b = fireball.fireball(a.mass, a.hc, a.fraction)
        _out({**b, "distance_to_kW_m2": {str(k): fireball.distance_to_flux_m(b, k) for k in (37.5, 12.5, 4.0)}})
    elif a.cmd == "coverage":
        for t, (stds, mod, status) in standards.TOPICS.items():
            print(f"- {t}\n    standards: {', '.join(stds)}\n    code: {mod or '-'}\n    status: {status}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

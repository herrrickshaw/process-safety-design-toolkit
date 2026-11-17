"""CLI: python -m process_safety <relief-gas|relief-steam|relief-liquid|relief-fire|tank-normal|tank-fire|vapour-fire|plume|blowdown|hazop-csv|pool-fire|depressure|steel-fire|psm-check|psm-due|seveso|pipeline|rmp-check|rmp-worst|lng|lpg|h2o2|arc-flash|idmt|noise|safeguard|earthing|datacentre|flare|lopa|pfd|fireball|qra|coverage> ..."""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys

import datetime as _dt

from . import datacentre, depressuring, dispersion, electrical, fireball, flare, hazop, lng, lpg, mah, mechanical_safety, noise, pipeline, plant_units, pool_fire, props, psm, relief, release, rmp, sil, standards, structural_fire, tank_venting, vapour_fire


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

    pc = s.add_parser("psm-check", help="OSHA PSM applicability: Appendix A chemical or the 10,000 lb flammables rule")
    pc.add_argument("--chemical", help="name or CAS"); pc.add_argument("--kg", type=float, required=True)
    pc.add_argument("--flammable", action="store_true"); pc.add_argument("--workplace-fuel", action="store_true"); pc.add_argument("--atmospheric-below-bp", action="store_true")

    pd = s.add_parser("psm-due", help="next due dates (ISO dates) for PHA revalidation, procedure certification, refresher training, compliance audit")
    for n in ("pha", "procedures", "training", "audit"):
        pd.add_argument("--" + n, help="last done YYYY-MM-DD")
    pd.add_argument("--today")

    sv = s.add_parser("seveso", help="Seveso III sum-rule tier; items as KEY=tonnes, KEY=P2 (category) or Name:H=tonnes (substance:group)")
    sv.add_argument("items", nargs="+")

    pp = s.add_parser("pipeline", help="49 CFR 192 design pressure and potential impact radius (natural gas)")
    for n in ("smys", "wall", "od"):
        pp.add_argument("--" + n, type=float, required=True, help={"smys": "MPa", "wall": "mm", "od": "mm"}[n])
    pp.add_argument("--class-location", type=int, default=1); pp.add_argument("--joint", type=float, default=1.0)
    pp.add_argument("--temp", type=float, default=20.0); pp.add_argument("--buildings", type=int, default=0)

    rc = s.add_parser("rmp-check", help="EPA RMP (40 CFR 68) threshold check for a regulated toxic/flammable substance")
    rc.add_argument("substance"); rc.add_argument("--kg", type=float, required=True); rc.add_argument("--weight-fraction", type=float, default=1.0)

    rw = s.add_parser("rmp-worst", help="RMP worst-case criteria: toxic gas (10 min, 1.5 m/s, F) or flammable VCE (10%% yield, 1 psi)")
    rw.add_argument("substance"); rw.add_argument("--kg", type=float, required=True)
    rw.add_argument("--hc", type=float, help="heat of combustion MJ/kg (flammables)")

    lg = s.add_parser("lng", help="LNG: impoundment (49 CFR 193.2181), boil-off, regas duty")
    lg.add_argument("--tanks", type=float, nargs="+", required=True, help="tank capacities m3"); lg.add_argument("--surge", action="store_true")
    lg.add_argument("--heat-kw", type=float, help="heat ingress kW (boil-off)"); lg.add_argument("--regas-kg-s", type=float)
    lg.add_argument("--sw-dT", type=float, default=5.0)

    lp = s.add_parser("lpg", help="LPG/hydrocarbon: vapour pressure, density, max fill fraction")
    lp.add_argument("component"); lp.add_argument("--fill-C", type=float, default=15.0); lp.add_argument("--max-C", type=float, default=50.0)

    hp = s.add_parser("h2o2", help="hydrogen peroxide decomposition: O2, heat and max steam per hour")
    hp.add_argument("--kg-h", type=float, required=True, help="pure H2O2 decomposing, kg/h")

    af = s.add_parser("arc-flash", help="Lee-method incident energy and boundary (open-air 3-phase; OSHA applicability limits enforced)")
    af.add_argument("--kv", type=float, required=True); af.add_argument("--ka", type=float, required=True); af.add_argument("--t", type=float, required=True)
    af.add_argument("--dist-mm", type=float, required=True); af.add_argument("--phases", type=int, default=3); af.add_argument("--enclosed", action="store_true")

    im = s.add_parser("idmt", help="IEC 60255 inverse-time overcurrent relay operating time")
    im.add_argument("--i", type=float, required=True, help="fault current A"); im.add_argument("--pickup", type=float, required=True); im.add_argument("--tms", type=float, required=True)
    im.add_argument("--curve", default="standard_inverse", choices=list(electrical.IDMT))

    nz = s.add_parser("noise", help="OSHA noise dose and TWA; items LEVEL_dBA:HOURS")
    nz.add_argument("items", nargs="+")

    sg = s.add_parser("safeguard", help="ISO 13855 (pre-2024 form) minimum distance for an electro-sensitive protective device")
    sg.add_argument("--stop-s", type=float, required=True, help="total stopping time incl. response, s"); sg.add_argument("--d-mm", type=float, required=True, help="detection capability mm")

    er = s.add_parser("earthing", help="IEEE 80 tolerable touch and step voltages (50 and 70 kg)")
    er.add_argument("--rho-s", type=float, required=True, help="surface layer resistivity ohm-m"); er.add_argument("--t", type=float, required=True, help="fault duration s")
    er.add_argument("--rho", type=float, help="underlying soil resistivity (with --hs for the Cs derating)"); er.add_argument("--hs", type=float, help="surface layer thickness m")

    dcp = s.add_parser("datacentre", help="data-centre screening: PUE, cooling-water flow, UPS battery energy, diesel storage (supply only the inputs you have)")
    dcp.add_argument("--it-kw", type=float, required=True); dcp.add_argument("--facility-kw", type=float); dcp.add_argument("--delta-t", type=float, help="cooling water dT, K")
    dcp.add_argument("--heat-kw", type=float, help="heat to remove (default: IT load)"); dcp.add_argument("--autonomy-min", type=float)
    dcp.add_argument("--battery-eff", type=float, default=0.95); dcp.add_argument("--battery-dod", type=float, default=0.8)
    dcp.add_argument("--gen-hours", type=float); dcp.add_argument("--gen-load-kw", type=float); dcp.add_argument("--sfc", type=float, help="specific fuel consumption, g/kWh (vendor data)")

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

    q = s.add_parser("qra", help="quantitative risk assessment workflow (HAZID -> frequency -> consequence -> risk -> ALARP -> mitigation)")
    q.add_argument("action", choices=["example", "validate", "run", "hazid", "buildings", "emergency"])
    q.add_argument("study", nargs="?", help="study JSON (see process_safety/qra/examples/lpg_terminal.json)")
    q.add_argument("--out", default="qra_out", help="output folder (run/hazid) or file (example)")
    q.add_argument("--sample", type=int, help="run only N LOC scenarios on a 2x coarser grid and project the full run time")
    q.add_argument("--grid-step", type=float, help="override grid step, m")
    q.add_argument("--no-mitigation", action="store_true")
    q.add_argument("--no-xlsx", action="store_true")
    q.add_argument("--quiet", action="store_true", help="no progress bar")

    tl = s.add_parser("tool", help="JSON-driven study tools: bowtie, sif, fg, thermal, atex, ram, pha (see process_safety/tools.py)")
    tl.add_argument("name", choices=["bowtie", "sif", "fg", "thermal", "atex", "ram", "pha", "example"])
    tl.add_argument("input", nargs="?", help="input JSON (tool example <name> copies a worked example)")
    tl.add_argument("--out", default="tool_out")
    tl.add_argument("--quiet", action="store_true")

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
    elif a.cmd == "psm-check":
        if a.flammable:
            _out(psm.covered_flammable(a.kg, workplace_fuel_only=a.workplace_fuel, atmospheric_tank_below_boiling_point=a.atmospheric_below_bp))
        else:
            _out(psm.covered_chemical(a.chemical, a.kg))
    elif a.cmd == "psm-due":
        last = {k: _dt.date.fromisoformat(v) for k, v in (("pha_revalidation", a.pha), ("operating_procedure_certification", a.procedures),
                                                          ("refresher_training", a.training), ("compliance_audit", a.audit)) if v}
        _out(psm.due_dates(last, _dt.date.fromisoformat(a.today) if a.today else None))
    elif a.cmd == "seveso":
        inv = []
        for it in a.items:
            key, val = it.split("=", 1)
            if ":" in key:
                name, grp = key.split(":"); inv.append({"substance": name, "group": grp, "tonnes": float(val)})
            else:
                inv.append({"category": key, "tonnes": float(val)})
        r = mah.classify(inv)
        _out({"tier": r["tier"], "sums": {g: {"lower": round(v["lower"], 3), "upper": round(v["upper"], 3)} for g, v in r["sums"].items() if v["items"]},
              "note": "Seveso III Annex I, 2012 text; MSIHC 1989 schedules not reproduced"})
    elif a.cmd == "pipeline":
        P = pipeline.design_pressure_kpa(a.smys, a.wall, a.od, a.class_location, a.joint, a.temp)
        r = pipeline.potential_impact_radius_m(P, a.od)
        _out({"design_pressure_kPag": P, "design_pressure_bar": P / 100, "potential_impact_radius_m_natural_gas_at_that_pressure": r,
              "hca_criterion_iii": pipeline.hca_by_pir(r, a.buildings, a.class_location), "note": "49 CFR 192 basis (US), natural gas only"})
    elif a.cmd == "rmp-check":
        _out(rmp.threshold_check(a.substance, a.kg, a.weight_fraction))
    elif a.cmd == "rmp-worst":
        f = rmp.find(a.substance)
        if f is None:
            raise SystemExit(f"{a.substance!r} not in the parsed RMP tables")
        _out(rmp.worst_case_toxic_gas(a.substance, a.kg) if f["kind"] == "toxic" else rmp.worst_case_flammable_vce(a.kg, a.hc))
    elif a.cmd == "lng":
        out = {"impoundment_m3": lng.impoundment_capacity_m3(a.tanks, a.surge), "basis": "49 CFR 193.2181"}
        if a.heat_kw:
            out["boil_off_kg_s"] = lng.boil_off_rate_kg_s(a.heat_kw)
            out["boil_off_pct_per_day_largest_tank"] = lng.boil_off_pct_per_day(a.heat_kw, max(a.tanks))
        if a.regas_kg_s:
            d = lng.regas_duty_kW(a.regas_kg_s, 111.66, 283.15)
            out.update({"regas_duty_MW": d / 1000, "seawater_m3_s_open_rack": lng.seawater_flow_m3_s(d, a.sw_dT)})
        _out(out)
    elif a.cmd == "lpg":
        Tf, Tm = a.fill_C + 273.15, a.max_C + 273.15
        _out({"vapour_pressure_kPag_at_max": lpg.vapour_pressure_kPag(a.component, Tm), "liquid_density_kg_m3_at_fill": props.liquid_density_kg_m3(a.component, Tf),
              "max_fill_fraction_thermodynamic_ceiling": lpg.max_fill_fraction(a.component, Tf, Tm), "note": "codes (API 2510, OISD-STD-144/150, IS 2825) set the practical limit"})
    elif a.cmd == "h2o2":
        _out(plant_units.h2o2_decomposition(a.kg_h))
    elif a.cmd == "arc-flash":
        ok = electrical.lee_applicable(a.kv * 1000, a.phases, a.enclosed)
        out = {"applicability": ok}
        if ok["ok"]:
            E = electrical.lee_incident_energy_J_cm2(a.kv, a.ka, a.t, a.dist_mm)
            out.update({"incident_energy_J_cm2": E, "incident_energy_cal_cm2": E * electrical.CAL_PER_J,
                        "boundary_mm_second_degree_burn": electrical.lee_boundary_mm(a.kv, a.ka, a.t), "note": "screening; arc-flash study per IEEE 1584 for enclosed equipment"})
        _out(out)
    elif a.cmd == "idmt":
        _out({"operating_time_s": electrical.idmt_time_s(a.i, a.pickup, a.tms, a.curve), "multiple_of_pickup": a.i / a.pickup})
    elif a.cmd == "noise":
        ex = [(float(x.split(":")[0]), float(x.split(":")[1])) for x in a.items]
        d = noise.dose_pct(ex)
        _out({"dose_pct": d, "twa_dBA": noise.twa_dBA(d), "exceeds_pel": d > 100, "above_action_level": d >= 50, "basis": "OSHA 1910.95 Table G-16 / App. A"})
    elif a.cmd == "safeguard":
        _out({"min_distance_mm": mechanical_safety.safeguard_distance_mm(a.stop_s, a.d_mm), "note": "pre-2024 ISO 13855 form; confirm the edition your project cites"})
    elif a.cmd == "earthing":
        Cs = electrical.surface_layer_factor(a.rho, a.rho_s, a.hs) if a.rho and a.hs else 1.0
        _out({"Cs": Cs, "touch_V_50kg": electrical.tolerable_touch_V(a.rho_s, a.t, Cs, 50), "step_V_50kg": electrical.tolerable_step_V(a.rho_s, a.t, Cs, 50),
              "touch_V_70kg": electrical.tolerable_touch_V(a.rho_s, a.t, Cs, 70), "step_V_70kg": electrical.tolerable_step_V(a.rho_s, a.t, Cs, 70)})
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
    elif a.cmd == "qra":
        return _qra(a)
    elif a.cmd == "datacentre":
        if a.gen_hours is not None and not a.sfc:
            p.error("--gen-hours needs --sfc (vendor data, no default)")
        _out(datacentre.summary(a.it_kw, a.facility_kw, a.delta_t, a.heat_kw, a.autonomy_min, a.battery_eff, a.battery_dod, a.gen_load_kw, a.gen_hours, a.sfc))
    elif a.cmd == "tool":
        return _tool(a)
    elif a.cmd == "coverage":
        for t, (stds, mod, status) in standards.TOPICS.items():
            print(f"- {t}\n    standards: {', '.join(stds)}\n    code: {mod or '-'}\n    status: {status}")
    return 0


def _qra(a):
    import os
    import shutil
    from .qra import frequency as qfreq, hazid as qhazid, report as qreport, study as qstudy, validate as qvalidate
    ex = os.path.join(os.path.dirname(__file__), "qra", "examples", "lpg_terminal.json")
    if a.action == "example":
        dst = a.out if a.out.endswith(".json") else "qra_study.json"
        shutil.copy(ex, dst)
        print(f"wrote {dst} - edit it, then: python3 -m process_safety qra validate {dst}")
        return 0
    if not a.study:
        print("give a study JSON (or run: python3 -m process_safety qra example)", file=sys.stderr)
        return 2
    st = qstudy.load(a.study)
    ds = qfreq.load_dataset(st.get("frequency_dataset"))
    if a.action == "validate":
        rep = qvalidate.inputs(st, ds)
        sc = qstudy.build_scenarios(st, ds) if rep else []
        _out({**rep.as_dict(), "loc_scenarios": len(sc), "total_loc_frequency_per_yr": sum(x["frequency_per_yr"] for x in sc)})
        return 0 if rep else 1
    if a.action == "hazid":
        os.makedirs(a.out, exist_ok=True)
        n1 = qhazid.write_csv(qhazid.hazid_register(st["sections"]), os.path.join(a.out, "hazid_register.csv"), qhazid.HAZID_COLUMNS)
        n2 = qhazid.write_csv(qhazid.hazop_rows(st["sections"]), os.path.join(a.out, "hazop_worksheet.csv"))
        sc = qstudy.build_scenarios(st, ds)
        qreport._csv(os.path.join(a.out, "loc_register.csv"), [{k: x[k] for k in ("id", "section", "equipment", "hole", "hole_mm", "instantaneous", "frequency_per_yr", "basis", "source")} for x in sc])
        print(f"{n1} HAZID rows, {n2} HAZOP rows, {len(sc)} LOC scenarios -> {a.out}/")
        return 0
    from .qra import buildings as qbuild, emergency as qemerg
    out = qstudy.run(st, sample=a.sample, grid_step=a.grid_step, progress=not a.quiet, mitigate=not a.no_mitigation and a.action == "run",
                     dataset=ds)
    if a.action == "buildings":
        res = qbuild.assess(out, st, progress=not a.quiet)
        os.makedirs(a.out, exist_ok=True)
        _out({"buildings": res["buildings"], "files": qbuild.write(res, os.path.join(a.out, "qra"))})
        return 0
    if a.action == "emergency":
        res = qemerg.assess(out, st)
        os.makedirs(a.out, exist_ok=True)
        _out({"site_emergency_level": res["site_level"], "mcls": res["mcls"], "files": qemerg.write(res, st, os.path.join(a.out, "qra"))})
        return 0
    files = qreport.write_all(out, st, a.out, xlsx=not a.no_xlsx)
    if st.get("buildings"):
        files["buildings"] = qbuild.write(qbuild.assess(out, st, progress=not a.quiet), os.path.join(a.out, "qra"))[1]
    files["emergency"] = qemerg.write(qemerg.assess(out, st), st, os.path.join(a.out, "qra"))[2]
    _out(qstudy.summary(out))
    print("\n".join(f"{k}: {v}" for k, v in files.items()), file=sys.stderr)
    return 1 if out["validation_results"]["errors"] else 0


def _tool(a):
    import os
    import shutil
    from .tools import run_tool
    exdir = os.path.join(os.path.dirname(__file__), "examples")
    if a.name == "example":
        if not a.input:
            print("tool example <bowtie|sif|fg|thermal|atex|ram|pha>", file=sys.stderr)
            return 2
        shutil.copy(os.path.join(exdir, f"{a.input}.json"), f"{a.input}.json")
        print(f"wrote {a.input}.json - run: python3 -m process_safety tool {a.input} {a.input}.json")
        return 0
    with open(a.input or os.path.join(exdir, f"{a.name}.json"), encoding="utf-8") as fh:
        data = json.load(fh)
    summ = run_tool(a.name, data, a.out, progress=not a.quiet)
    _out(summ)
    return 1 if any(str(c).startswith("FAIL") for c in summ.get("checks", [])) else 0


if __name__ == "__main__":
    sys.exit(main())

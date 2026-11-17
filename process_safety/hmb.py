"""Heat and material balance (HMB) checks and scenario generation from a plant model (see `plant_model`).

Checks: mass balance closure per unit; operating against design pressure; hazard flags from component names (EPA RMP lists). Scenarios
(each computed with the toolkit's own models and returned with the numbers, the status and the plain-language reason a study would give):
    blocked_outlet   vapour inlet flow against the installed relief area (API 520 gas sizing at the single-case relieving pressure)
    overfill         time to fill the spare volume against operator response plus valve closure, times a safety factor
    interface        a stream whose operating pressure exceeds the design pressure of the unit it feeds
    tube_rupture     the 10/13 rule and the rupture flow against the low-pressure side relief
    mdmt             isentropic cooling on depressuring to atmosphere against the unit MDMT
    fire             liquid-wetted or vapour-filled fire through `design_workflow.screen_unit` when a `fire` block is given
A scenario returns status "adequate", "gap", "review" or "cannot_assess" (with the missing inputs listed). Screening models only: relief
loads are conservative-or-simple and the coincident-load, back-pressure and transient aspects are for the relief study proper.
"""
from __future__ import annotations

import math

from . import depressuring, design_workflow, overfill, relief, rmp, scenarios
from .relief import ATM

DEFAULTS = {"closure_tol": 0.01, "overfill_safety_factor": 2.0, "pressure_margin_warn": 0.9}   # overfill factor and margin are judgment


def _units(m):
    return {u["tag"]: u for u in m["units"]}


def balance(m: dict, tol: float = DEFAULTS["closure_tol"]) -> list[dict]:
    rows = []
    for u in m["units"]:
        i = sum(s.get("mass_kg_h") or 0.0 for s in m["streams"] if s.get("to") == u["tag"])
        o = sum(s.get("mass_kg_h") or 0.0 for s in m["streams"] if s.get("from") == u["tag"])
        if i == 0 and o == 0:
            continue
        c = (i - o) / i if i else math.inf
        rows.append({"unit": u["tag"], "in_kg_h": i, "out_kg_h": o, "closure": c,
                     "status": "ok" if abs(c) <= tol else ("no_outlet" if o == 0 else "no_inlet" if i == 0 else "check"),
                     "why": f"inlet {i:,.0f} against outlet {o:,.0f} kg/h ({100 * c:+.2f}%)"})
    return rows


def stream_hazard(s: dict) -> dict:
    flam = tox = False
    names = []
    for comp, frac in (s.get("components") or {}).items():
        r = rmp.find(comp)
        if r and (frac or 0) >= 0.01:
            names.append(r["name"])
            flam |= r["kind"] == "flammable"
            tox |= r["kind"] == "toxic"
    if s.get("hazard"):
        flam |= "flam" in str(s["hazard"]).lower()
        tox |= "tox" in str(s["hazard"]).lower()
    return {"flammable": flam, "toxic": tox, "listed": names}


def unit_hazards(m: dict) -> dict:
    out = {u["tag"]: {"flammable": False, "toxic": False, "listed": []} for u in m["units"]}
    for s in m["streams"]:
        h = stream_hazard(s)
        for e in (s.get("from"), s.get("to")):
            if e in out:
                out[e]["flammable"] |= h["flammable"]
                out[e]["toxic"] |= h["toxic"]
                out[e]["listed"] = sorted(set(out[e]["listed"]) | set(h["listed"]))
    for u in m["units"]:
        if u.get("service_hazard"):
            out[u["tag"]]["flammable"] |= "flam" in str(u["service_hazard"]).lower()
            out[u["tag"]]["toxic"] |= "tox" in str(u["service_hazard"]).lower()
    return out


def device_area(m: dict, tag: str) -> tuple[float, list[dict]]:
    ds = [d for d in m["relief_devices"] if d.get("unit") == tag and str(d.get("type", "PSV")).upper() in ("PSV", "PRV", "RD")]
    return sum(d.get("area_mm2") or 0.0 for d in ds), ds


def _row(unit, scen, status, numbers, rec_ids, why, missing=None):
    return {"unit": unit, "scenario": scen, "status": status, "numbers": numbers, "rec_ids": rec_ids, "why": why, "missing": missing or []}


def blocked_outlet(m, u):
    ins = [s for s in m["streams"] if s.get("to") == u["tag"] and str(s.get("phase", "")).startswith("vap")]
    if not ins:
        return None
    area, devs = device_area(m, u["tag"])
    s = max(ins, key=lambda x: x.get("mass_kg_h") or 0)
    miss = [k for k in ("mass_kg_h", "mw", "k", "T_C") if s.get(k) is None]
    if not devs:
        return _row(u["tag"], "blocked_outlet", "gap", {"inlet_vapour_kg_h": s.get("mass_kg_h")}, ["PSV-ADD"],
                    f"a blocked outlet leaves {s.get('mass_kg_h') or 0:,.0f} kg/h of vapour with nowhere to go and no relief device is registered for {u['tag']}")
    if miss:
        return _row(u["tag"], "blocked_outlet", "cannot_assess", {}, [], f"vapour inlet stream {s.get('id')} lacks {', '.join(miss)}", miss)
    set_k = min(d["set_kpag"] for d in devs if d.get("set_kpag") is not None)
    P1 = relief.relieving_pressure_kpa(set_k, "single_non_fire")
    P2 = (devs[0].get("back_pressure_kpag") or 0.0) + ATM
    r = relief.gas_area(s["mass_kg_h"], s["T_C"] + 273.15, P1, P2, s["mw"], s["k"], s.get("Z") or 1.0, set_g_kpa=set_k)
    ok = area >= r.required_area_mm2
    return _row(u["tag"], "blocked_outlet", "adequate" if ok else "gap",
                {"required_area_mm2": r.required_area_mm2, "installed_area_mm2": area, "orifice": r.orifice, "relieving_kpa_abs": P1, "assumed_Z": s.get("Z") is None},
                [] if ok else ["PSV-UPSIZE"],
                f"blocked outlet sends {s['mass_kg_h']:,.0f} kg/h to the relief device: needs {r.required_area_mm2:,.0f} mm2 ({r.orifice} orifice) at {P1:,.0f} kPa abs against {area:,.0f} mm2 installed")


def overfill_scn(m, u, p):
    ins = [s for s in m["streams"] if s.get("to") == u["tag"] and str(s.get("phase", "")).startswith("liq")]
    if not ins or u.get("volume_m3") is None or u.get("level_pct") is None:
        return None
    miss = [k for k in ("rho_kg_m3", "mass_kg_h") if any(s.get(k) is None for s in ins)] + [k for k in ("operator_response_min",) if u.get(k) is None]
    if miss:
        return _row(u["tag"], "overfill", "cannot_assess", {}, [], f"missing {', '.join(miss)}", miss)
    fill = sum(s["mass_kg_h"] / s["rho_kg_m3"] for s in ins)
    spare = u["volume_m3"] * (1 - u["level_pct"] / 100.0)
    t = overfill.time_to_overfill_s(spare, fill)
    need = (u["operator_response_min"] * 60.0 + (u.get("valve_closure_s") or 0.0)) * p["overfill_safety_factor"]
    trips = [i for i in m["instruments"] if i.get("unit") == u["tag"] and str(i.get("type", "")).upper().startswith("LS") and str(i.get("function", "")).lower() in ("trip", "sis")]
    ok = t > need
    if ok:
        st, rec = "adequate", []
    elif trips:
        st, rec = "review", []
    else:
        st, rec = "gap", ["HLL-SIF"]
    return _row(u["tag"], "overfill", st, {"time_to_overfill_min": t / 60, "needed_min": need / 60, "fill_m3_h": fill, "spare_m3": spare, "registered_trips": [i["tag"] for i in trips]}, rec,
                f"fill {fill:,.1f} m3/h into {spare:,.1f} m3 spare gives {t / 60:,.1f} min to overfill against {need / 60:,.1f} min needed (operator response plus valve closure, x{p['overfill_safety_factor']:g})"
                + (f"; a registered high-level trip ({', '.join(i['tag'] for i in trips)}) is there: verify it is independent and tested" if (not ok and trips) else ""))


def interface_scn(m, u, p):
    if u.get("design_P_kpag") is None:
        return []
    out = []
    area, devs = device_area(m, u["tag"])
    for s in m["streams"]:
        if s.get("to") == u["tag"] and s.get("P_kpag") is not None and s["P_kpag"] > u["design_P_kpag"]:
            prot = [d["tag"] for d in devs if d.get("set_kpag") is not None and d["set_kpag"] <= u["design_P_kpag"]]
            out.append(_row(u["tag"], "interface", "review" if prot else "gap", {"stream": s.get("id"), "stream_P_kpag": s["P_kpag"], "design_P_kpag": u["design_P_kpag"], "relief": prot},
                            ["INTERFACE-DP"], f"stream {s.get('id')} arrives at {s['P_kpag']:,.0f} kPag but {u['tag']} is designed for {u['design_P_kpag']:,.0f} kPag"
                            + (f"; {', '.join(prot)} registered: size it for the blow-by" if prot else " and no relief device is registered below design pressure")))
        if s.get("to") == u["tag"] and s.get("P_kpag") is not None and p["pressure_margin_warn"] * u["design_P_kpag"] < s["P_kpag"] <= u["design_P_kpag"]:
            out.append(_row(u["tag"], "operating_margin", "review", {"ratio": s["P_kpag"] / u["design_P_kpag"]}, [],
                            f"operating pressure is {100 * s['P_kpag'] / u['design_P_kpag']:.0f}% of design: little margin to the relief set point"))
    return out


def tube_rupture_scn(m):
    out = []
    for x in m["exchangers"]:
        try:
            hp, lp = x["hp_design_kpag"], x["lp_design_kpag"]
        except KeyError:
            out.append(_row(x.get("tag", "?"), "tube_rupture", "cannot_assess", {}, [], "needs hp_design_kpag and lp_design_kpag", ["hp_design_kpag", "lp_design_kpag"]))
            continue
        if scenarios.tube_rupture_exempt(hp, lp):
            out.append(_row(x["tag"], "tube_rupture", "adequate", {"lp_over_hp": lp / hp}, [], f"LP design {lp:,.0f} is at least 10/13 of HP design {hp:,.0f} kPag: tube rupture relief not required by the 10/13 rule"))
            continue
        need = [k for k in ("tube_id_mm", "hp_P_kpag", "lp_P_kpag", "phase") if x.get(k) is None]
        if x.get("phase") == "liquid" and x.get("rho_kg_m3") is None:
            need.append("rho_kg_m3")
        if x.get("phase", "").startswith("vap") and any(x.get(k) is None for k in ("T_K", "M", "k")):
            need += ["T_K", "M", "k"]
        lpu = next((u for u in m["units"] if u["tag"] == x.get("lp_unit")), None)
        area = device_area(m, x["lp_unit"])[0] if lpu else 0.0
        if need:
            out.append(_row(x["tag"], "tube_rupture", "gap" if not area else "review", {"lp_over_hp": lp / hp, "installed_lp_area_mm2": area}, ["INTERFACE-DP"],
                            f"LP design {lp:,.0f} is below 10/13 of HP design {hp:,.0f} kPag: tube rupture must be relieved on the LP side; flow not computed (missing {', '.join(need)})", need))
            continue
        W = scenarios.tube_rupture_flow_kg_s(x["tube_id_mm"] / 1000, x["hp_P_kpag"] + ATM, x["lp_P_kpag"] + ATM, x["phase"], x.get("rho_kg_m3"), x.get("T_K"), x.get("M"), x.get("k"))
        set_lp = min([d["set_kpag"] for d in device_area(m, x["lp_unit"])[1] if d.get("set_kpag") is not None] or [lp])
        P1 = relief.relieving_pressure_kpa(set_lp, "single_non_fire")
        if x["phase"] == "liquid":
            r = relief.liquid_area(W * 3600 / x["rho_kg_m3"], x["rho_kg_m3"], P1, ATM)
        else:
            r = relief.gas_area(W * 3600, x["T_K"], P1, ATM, x["M"], x["k"], x.get("Z") or 1.0, set_g_kpa=set_lp)
        ok = area >= r.required_area_mm2
        out.append(_row(x["tag"], "tube_rupture", "adequate" if ok else "gap", {"rupture_flow_kg_s": W, "required_area_mm2": r.required_area_mm2, "installed_lp_area_mm2": area}, [] if ok else ["INTERFACE-DP", "PSV-UPSIZE"],
                        f"double-ended tube rupture sends {W:,.1f} kg/s into the LP side: needs {r.required_area_mm2:,.0f} mm2 against {area:,.0f} mm2 installed (LP design {lp:,.0f} < 10/13 of HP {hp:,.0f} kPag)"))
    return out


def mdmt_scn(m, u):
    if u.get("mdmt_C") is None:
        return None
    vs = [s for s in m["streams"] if s.get("from") == u["tag"] and str(s.get("phase", "")).startswith("vap") and s.get("k") and s.get("P_kpag") is not None and s.get("T_C") is not None]
    if not vs:
        return None
    s = vs[0]
    t = depressuring.min_gas_temperature_K(s["T_C"] + 273.15, s["P_kpag"] + ATM, ATM, s["k"]) - 273.15
    low = t < u["mdmt_C"]
    return _row(u["tag"], "mdmt", "gap" if low else "adequate", {"min_gas_temp_C": t, "mdmt_C": u["mdmt_C"]}, ["MATERIAL"] if low else [],
                f"depressuring {s['P_kpag']:,.0f} kPag gas to atmosphere cools it (ideal-gas isentropic lower bound) to {t:,.0f} C against an MDMT of {u['mdmt_C']:,.0f} C"
                + ("" if not low else ": check the metal temperature properly, or limit the depressuring rate / upgrade materials"))


def fire_scn(m, u):
    f = u.get("fire")
    if not f:
        return None
    unit = {"tag": u["tag"], "mode": f["mode"], "set_kpag": f.get("set_kpag") or next((d["set_kpag"] for d in device_area(m, u["tag"])[1] if d.get("set_kpag")), None),
            "fluid": f.get("fluid", {}), "vessel": f.get("vessel", {}), "existing": {"psv_area_mm2": device_area(m, u["tag"])[0], "bdv_area_mm2": f.get("bdv_area_mm2", 0.0),
                                                                                    "inlet_id_m": f.get("inlet_id_m"), "inlet_length_m": f.get("inlet_length_m", 0.0)},
            "inlet_candidates": f.get("inlet_candidates", []), "depressure": f.get("depressure"), "bdv_open_s": f.get("bdv_open_s", 60.0), "back_pressure_kpag": f.get("back_pressure_kpag", 0.0)}
    if unit["set_kpag"] is None:
        return _row(u["tag"], "fire", "cannot_assess", {}, [], "no relief device set pressure", ["set_kpag"])
    try:
        r = design_workflow.screen_unit(unit)
    except (KeyError, ValueError, TypeError) as e:
        return _row(u["tag"], "fire", "cannot_assess", {}, [], f"fire block incomplete: {e!r}", [str(e)])
    rz = r["resize"]
    recs = (["PSV-UPSIZE"] if "psv_new" in rz else []) + (["BDV"] if "bdv_new" in rz else []) + (["RELIEF-PIPING"] if rz.get("inlet_new") else [])
    return _row(u["tag"], "fire", "gap" if recs else "adequate", {"simulate": r["simulate"], "resize": {k: v for k, v in rz.items() if k in ("psv_ok", "psv_new", "bdv_new", "inlet_new")}}, recs,
                "fire exposure: " + ("; ".join([f"needs a {rz['psv_new']['orifice']} orifice" if "psv_new" in rz else "", "the vessel ruptures without depressuring: add a blowdown valve" if "bdv_new" in rz else "",
                                                "inlet line fails the 3% rule" if rz.get("inlet_new") else ""]).strip("; ") or "installed devices are adequate"))


def scenarios_for(m: dict, params: dict | None = None) -> list[dict]:
    p = {**DEFAULTS, **(params or {})}
    out = []
    for u in m["units"]:
        for fn in (blocked_outlet, mdmt_scn, fire_scn):
            r = fn(m, u)
            if r:
                out.append(r)
        r = overfill_scn(m, u, p)
        if r:
            out.append(r)
        out += interface_scn(m, u, p)
    out += tube_rupture_scn(m)
    return out

"""End-to-end workflow: safety simulation -> equipment resizing and design -> capex and opex of the installation.

Stages (each result is kept so the chain can be audited):
    1. SIMULATE / SCREEN   per unit: fire-case relief load and required PSV area (liquid-wetted vessels, API 520/521), or the transient
                           vapour-filled fire simulation (PSV only against rupture). Inputs come from your process simulator
                           (DWSIM, NeqSim, UniSim, ...) as plain numbers: relieving rate or vessel/fluid data, set pressure, back pressure.
    2. RESIZE / DESIGN     PSV orifice (API 526 letter) against the installed one; inlet line size against the 3% rule from your list
                           of candidate pipe sizes; blowdown valve area for a target depressuring time and re-simulated until the vessel
                           is protected (vapour-filled). Result: before -> after for each device.
    3. BILL OF QUANTITIES  the resized devices and the scopes you describe become estimate lines, priced from YOUR rate book:
                           device scope (PSV, inlet line, blowdown valve), pipeline REROUTING (demolition, new pipe, fittings, supports,
                           tie-ins, civil), ADDITIONAL SENSORS (instruments, cable, junction boxes, loop checks) and PROCESS CONTROL
                           NETWORK (PCN) modification (I/O, controllers, switches, firewalls, engineering, FAT/SAT). Each scope carries its own
                           shutdown flag and duration.
    4. CAPEX               `recommendation_cost.estimate`: Monte Carlo on quantities and rates, indirects, P50/P80, contingency.
    5. OPEX                annual testing, inspection and maintenance of the NEW devices from YOUR opex book, lifecycle cost at your discount rate.
    6. ALARP               package cost-benefit per unit (all scopes together) from a risk reduction you give or one derived from the sensor
                           voting change (PFDavg before and after, demand rate, fatalities per event); uses `qra.alarp`.
    7. SHUTDOWN (optional) shutdown-dependent items merged into a `shutdown_risk` model: schedule, lost operating days, opportunity cost.
The toolkit ships no rates. Screening models only: relief sizing needs a code-compliant calculation and vendor data before purchase.
"""
from __future__ import annotations

import math

from . import depressuring, hydraulics, recommendation_cost, relief, relief_piping, sil, vapour_fire
from .qra import alarp
from .relief import ATM


def check(data: dict) -> list[str]:
    errs = []
    if not data.get("units"):
        return ["no units"]
    book = data.get("rate_book", {})
    for u in data["units"]:
        t = u.get("tag", "?")
        if u.get("mode") not in ("liquid_wetted", "vapour_filled"):
            errs.append(f"{t}: mode must be liquid_wetted or vapour_filled")
            continue
        for k in ("set_kpag", "fluid", "vessel", "existing"):
            if k not in u:
                errs.append(f"{t}: missing {k}")
        if u["mode"] == "liquid_wetted" and "latent_heat_kJ_kg" not in u.get("vessel", {}):
            errs.append(f"{t}: liquid_wetted needs vessel.latent_heat_kJ_kg")
        inst = u.get("install", {})
        keys = set()

        def walk(o):
            if isinstance(o, dict):
                for k, v in o.items():
                    if k.endswith("rate_key") and isinstance(v, str):
                        keys.add(v)
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(inst)
        for c in u.get("inlet_candidates", []):
            if c.get("rate_key"):
                keys.add(c["rate_key"])
        for key in sorted(keys):
            if key not in book:
                errs.append(f"{t}: rate key {key} not in rate_book")
    if "opex_book" not in data:
        errs.append("opex_book is required (annual test and maintenance costs have no defaults)")
    return errs


def _inlet_line(u, W_kg_s, P1_kpa, length_m=None):
    """Smallest candidate inlet ID meeting the 3% rule; returns the chosen candidate and the loss for the existing line."""
    f, ex, vs = u["fluid"], u["existing"], u["set_kpag"]
    cands = sorted(u.get("inlet_candidates", []), key=lambda c: c["id_m"])
    mu = f.get("mu_Pa_s", 1.2e-5)
    L = ex.get("inlet_length_m", 0.0) if length_m is None else length_m

    def loss(d):
        r = hydraulics.isothermal_gas_outlet_kpa(W_kg_s, d, L, P1_kpa, f["relieving_T_K"], f["M"], mu)
        return relief_piping.inlet_loss_check(r["dp_kPa"], vs) | {"dp_kPa": r["dp_kPa"], "id_m": d}
    cur = None
    if ex.get("inlet_id_m"):
        try:
            cur = loss(ex["inlet_id_m"])
        except ValueError as e:                       # the existing line cannot pass the relieving flow at all
            cur = {"ok": False, "id_m": ex["inlet_id_m"], "error": str(e), "action": "existing inlet line is choked at the relieving flow: enlarge it"}
    chosen = None
    for c in cands:
        try:
            r = loss(c["id_m"])
        except ValueError:
            continue
        if r["ok"]:
            chosen = c | {"check": r}
            break
    return cur, chosen


def screen_unit(u: dict) -> dict:
    f, v, ex, vs = u["fluid"], u["vessel"], u["existing"], u["set_kpag"]
    out = {"tag": u["tag"], "mode": u["mode"], "set_kpag": vs}
    if u["mode"] == "liquid_wetted":
        A = v.get("wetted_area_m2") or relief.wetted_area_cylinder(v["D_m"], v["L_m"], v["level_m"], v.get("orientation", "horizontal"), v.get("elevation_m", 0.0))
        W = relief.fire_relief_rate_kg_h(A, v["latent_heat_kJ_kg"], v.get("F", 1.0), v.get("adequate_drainage", True))
        P1 = relief.relieving_pressure_kpa(vs, "fire")
        P2 = u.get("back_pressure_kpag", 0.0) + ATM
        r = relief.gas_area(W, f["relieving_T_K"], P1, P2, f["M"], f["k"], f.get("Z", 1.0), set_g_kpa=vs)
        out["simulate"] = {"wetted_area_m2": A, "relief_rate_kg_h": W, "relieving_P_kpa_abs": P1, "required_area_mm2": r.required_area_mm2,
                           "required_orifice": r.orifice, "n_valves": r.n_valves, "regime": r.regime}
        have = ex.get("psv_area_mm2", 0.0)
        ok = have >= r.required_area_mm2
        out["resize"] = {"psv_installed_area_mm2": have, "psv_ok": ok}
        if not ok:
            out["resize"]["psv_new"] = {"orifice": r.orifice, "n_valves": r.n_valves, "area_mm2": relief.API526_ORIFICES_MM2[r.orifice] * r.n_valves}
        new_area = relief.API526_ORIFICES_MM2[r.orifice] * r.n_valves if not ok else have
        W_check = W / 3600.0 * max(1.0, new_area / r.required_area_mm2)     # API 520 checks the line at the valve's RATED capacity
        out["resize"]["inlet_check_flow_kg_s"] = W_check
        try:
            cur, chosen = _inlet_line(u, W_check, P1)
        except ValueError as e:
            cur, chosen = None, None
            out["resize"]["inlet_note"] = str(e)
        rr = u.get("install", {}).get("reroute", {})
        if rr.get("new_inlet_length_m") is not None:
            try:
                cur2, chosen2 = _inlet_line(u, W_check, P1, rr["new_inlet_length_m"])
                out["resize"]["inlet_after_reroute"] = {"length_m": rr["new_inlet_length_m"], "existing_size": cur2, "ok": bool(cur2 and cur2["ok"]),
                                                        "needs_size": None if (cur2 and cur2["ok"]) else chosen2}
            except ValueError as e:
                out["resize"]["inlet_after_reroute"] = {"error": str(e)}
        if cur:
            out["resize"]["inlet_existing"] = cur
        if cur and not cur["ok"]:
            out["resize"]["inlet_new"] = chosen
            if chosen is None:
                out["resize"]["inlet_note"] = "no candidate inlet size meets the 3% rule: relocate the valve, shorten the line or use a pilot-operated valve"
    else:
        vess = vapour_fire.Vessel(v["volume_m3"], v["exposed_area_m2"], v["D_m"], v["wall_mm"], f["M"], f["k"], vs if "p0_kpag" not in v else v["p0_kpag"],
                                  strength_MPa=v.get("strength_MPa", 260.0))
        q = v.get("flux_kW_m2", 100.0)
        base = vapour_fire.simulate(vess, q, ex.get("psv_area_mm2", 0.0), vs + 0.0, bdv_area_mm2=ex.get("bdv_area_mm2", 0.0),
                                    bdv_open_s=u.get("bdv_open_s", 60.0), t_end_s=u.get("t_end_s", 3600.0))
        out["simulate"] = {"protected_as_installed": base.protected, "t_rupture_s": base.t_rupture_s, "peak_pressure_kpag": base.peak_pressure_kpag}
        out["resize"] = {"psv_installed_area_mm2": ex.get("psv_area_mm2", 0.0), "bdv_installed_area_mm2": ex.get("bdv_area_mm2", 0.0), "psv_ok": base.protected}
        if not base.protected:
            d = u.get("depressure", {})
            area = depressuring.required_area_mm2(v["volume_m3"], vs + ATM, d["target_kpag"] + ATM, v.get("T0_K", 323.15), f["M"], f["k"], d["target_time_s"])
            min_d = u.get("min_bdv_diameter_mm")
            governed = False
            if min_d and area < math.pi * min_d ** 2 / 4:
                area, governed = math.pi * min_d ** 2 / 4, True
            tries = 0
            res = None
            while tries < 12:
                res = vapour_fire.simulate(vess, q, ex.get("psv_area_mm2", 0.0), vs, bdv_area_mm2=area, bdv_open_s=u.get("bdv_open_s", 60.0), t_end_s=u.get("t_end_s", 3600.0))
                if res.protected:
                    break
                area *= 1.25
                tries += 1
            out["resize"]["bdv_new"] = {"area_mm2": area, "equivalent_diameter_mm": math.sqrt(4 * area / math.pi), "opens_at_s": u.get("bdv_open_s", 60.0),
                                        "protected_after": bool(res and res.protected), "iterations": tries,
                                        "governed_by_minimum_practical_size": governed}
    return out


def _qrange(q, rng):
    if isinstance(q, dict):
        return q
    lo, hi = rng.get("min_pct", 0.0), rng.get("max_pct", 0.0)
    return {"min": q * (1 + lo / 100), "mode": q, "max": q * (1 + hi / 100)}


def _scope_lines(u, s, rng):
    """Estimate lines per scope: device, reroute, sensors, pcn. Returns {scope: dict(lines, requires_shutdown, work_duration_days)}."""
    inst = u.get("install", {})
    rz = s["resize"]
    scopes = {}
    dev = []
    if "psv_new" in rz:
        dev.append({"discipline": "mechanical", "description": f"PSV {rz['psv_new']['orifice']} x{rz['psv_new']['n_valves']}",
                    "rate_key": inst.get("psv_rate_prefix", "psv_") + rz["psv_new"]["orifice"], "qty": _qrange(rz["psv_new"]["n_valves"], rng)})
    if rz.get("inlet_new"):
        c = rz["inlet_new"]
        dev.append({"discipline": "piping", "description": f"inlet line to ID {c['id_m'] * 1000:.0f} mm", "rate_key": c["rate_key"], "qty": _qrange(u["existing"].get("inlet_length_m", 0.0), rng)})
    if "bdv_new" in rz:
        dev.append({"discipline": "piping", "description": "blowdown valve", "rate_key": inst["bdv_rate_key"], "qty": _qrange(1, rng)})
        if inst.get("bdv_pipe_length_m"):
            dev.append({"discipline": "piping", "description": "blowdown line to flare", "rate_key": inst["bdv_pipe_rate_key"], "qty": _qrange(inst["bdv_pipe_length_m"], rng)})
    dev += inst.get("extra_lines", [])
    if dev:
        scopes["device"] = {"lines": dev, "requires_shutdown": bool(inst.get("requires_shutdown")), "work_duration_days": inst.get("work_duration_days")}
    rr = inst.get("reroute")
    if rr:
        L = []
        if rr.get("remove_length_m"):
            L.append({"discipline": "piping", "description": "demolish and remove old line", "rate_key": rr["remove_rate_key"], "qty": _qrange(rr["remove_length_m"], rng)})
        L.append({"discipline": "piping", "description": "new routed line", "rate_key": rr["new_rate_key"], "qty": _qrange(rr["new_length_m"], rng)})
        for fit in rr.get("fittings", []):
            L.append({"discipline": "piping", "description": fit["description"], "rate_key": fit["rate_key"], "qty": _qrange(fit["qty"], rng)})
        if rr.get("supports_qty"):
            L.append({"discipline": "mechanical", "description": "pipe supports", "rate_key": rr["supports_rate_key"], "qty": _qrange(rr["supports_qty"], rng)})
        if rr.get("tie_ins"):
            L.append({"discipline": "piping", "description": "tie-ins", "rate_key": rr["tie_in_rate_key"], "qty": _qrange(rr["tie_ins"], rng)})
        if rr.get("civil_m3"):
            L.append({"discipline": "civil", "description": "foundations and rack civil", "rate_key": rr["civil_rate_key"], "qty": _qrange(rr["civil_m3"], rng)})
        scopes["reroute"] = {"lines": L, "requires_shutdown": bool(rr.get("requires_shutdown", True)), "work_duration_days": rr.get("work_duration_days")}
    sn = inst.get("sensors")
    if sn:
        L = []
        for it in sn["items"]:
            L.append({"discipline": "instrumentation", "description": it["type"], "rate_key": it["rate_key"], "qty": _qrange(it["qty"], rng)})
            if it.get("cable_m_each"):
                L.append({"discipline": "electrical", "description": f"cable for {it['type']}", "rate_key": it["cable_rate_key"], "qty": _qrange(it["qty"] * it["cable_m_each"], rng)})
        if sn.get("junction_boxes"):
            L.append({"discipline": "electrical", "description": "junction boxes", "rate_key": sn["jb_rate_key"], "qty": _qrange(sn["junction_boxes"], rng)})
        if sn.get("commissioning_loops"):
            L.append({"discipline": "instrumentation", "description": "loop check and commissioning", "rate_key": sn["loop_rate_key"], "qty": _qrange(sn["commissioning_loops"], rng)})
        scopes["sensors"] = {"lines": L, "requires_shutdown": bool(sn.get("requires_shutdown", False)), "work_duration_days": sn.get("work_duration_days")}
    pc = inst.get("pcn")
    if pc:
        L = [{"discipline": it.get("discipline", "instrumentation"), "description": it["description"], "rate_key": it["rate_key"], "qty": _qrange(it["qty"], rng)} for it in pc["items"]]
        scopes["pcn"] = {"lines": L, "requires_shutdown": bool(pc.get("requires_shutdown", True)), "work_duration_days": pc.get("work_duration_days")}
    return scopes


def build_recommendations(data: dict, screened: list[dict]) -> dict:
    """Turn the design changes and the described scopes into recommendation_cost estimate lines priced from the rate book."""
    rng = data.get("quantity_uncertainty", {})
    recs = []
    for u, s in zip(data["units"], screened):
        for scope, sc in _scope_lines(u, s, rng).items():
            rec = {"id": f"{u['tag']}:{scope}", "title": f"{u['tag']} {scope}", "source": "design workflow", "lines": sc["lines"], "unit": u["tag"], "scope": scope,
                   "requires_shutdown": sc["requires_shutdown"], "life_years": data.get("life_years", 25)}
            if sc["requires_shutdown"]:
                if not sc.get("work_duration_days"):
                    raise ValueError(f"{rec['id']}: requires shutdown, so give work_duration_days")
                rec["work_duration_days"] = sc["work_duration_days"]
            recs.append(rec)
    est_in = {k: data[k] for k in ("currency", "rate_book", "indirects", "rate_factor", "distribution", "capex_basis") if k in data}
    est_in["recommendations"] = recs
    return est_in


def sif_benefit(sif: dict) -> dict:
    """PFDavg before and after a voting change and the resulting fatality-frequency change (demand rate x PFD x fatalities per event)."""
    ti_h = sif["ti_years"] * 8760.0
    before = sil.pfd_avg(sif["arch_before"], sif["lambda_du_per_h"], ti_h, sif.get("beta", 0.0))
    after = sil.pfd_avg(sif["arch_after"], sif["lambda_du_per_h"], ti_h, sif.get("beta", 0.0))
    d, nf = sif["demand_per_yr"], sif["fatalities_per_event"]
    return {"pfd_before": before, "pfd_after": after, "rrf_gain": before / after if after else math.inf, "pll_before": d * before * nf, "pll_after": d * after * nf,
            "note": "architectural constraints (HFT/SFF), common cause beyond beta, and spurious trips are not assessed here; see sil_lifecycle"}


def _mode_cost(rec, data, scope_filter=None):
    book = data.get("rate_book", {})
    tot = 0.0
    for ln in rec["lines"]:
        q = ln["qty"]["mode"] if isinstance(ln["qty"], dict) else ln["qty"]
        r = book[ln["rate_key"]]["rate"] if "rate_key" in ln else ln["rate"]
        r = r["mode"] if isinstance(r, dict) else r
        tot += q * r
    return tot


def opex_for(data: dict, screened: list[dict], est: dict, est_in: dict) -> dict:
    ob = data["opex_book"]
    rate = data.get("discount_rate", 0.0)
    years = data.get("life_years", 25)
    pv = alarp.present_value_factor(years, rate)
    cap = {r["id"]: r["capex"]["P50"] for r in est["recommendations"]}
    rows = []
    for u, s in zip(data["units"], screened):
        rz = s["resize"]
        inst = u.get("install", {})
        parts = {}
        if "bdv_new" in rz:
            parts["bdv_proof_test"] = ob.get("bdv_test_cost", 0.0) / ob.get("bdv_test_interval_years", 1.0)
        if "psv_new" in rz and ob.get("count_replaced_psv_tests", False):
            parts["psv_test"] = ob.get("psv_test_cost", 0.0) * rz["psv_new"]["n_valves"] / ob.get("psv_test_interval_years", 1.0)
        sn = inst.get("sensors")
        if sn:
            n = sum(it["qty"] if not isinstance(it["qty"], dict) else it["qty"]["mode"] for it in sn["items"])
            parts["sensor_calibration_and_proof_test"] = n * ob.get("sensor_test_cost", 0.0) / ob.get("sensor_test_interval_years", 1.0)
        if inst.get("pcn"):
            rec = next(r for r in est_in["recommendations"] if r["id"] == f"{u['tag']}:pcn")
            parts["pcn_support_and_licences"] = ob.get("pcn_support_pct_of_pcn_capex", 0.0) / 100.0 * cap.get(f"{u['tag']}:pcn", _mode_cost(rec, data))
            parts["pcn_cybersecurity_monitoring_and_patching"] = ob.get("pcn_cyber_annual_per_change", 0.0)
        maint = sum(cap.get(f"{u['tag']}:{sc}", 0.0) for sc in ("device", "reroute", "sensors", "pcn")) * ob.get("maintenance_pct_of_capex", 0.0) / 100.0
        if maint:
            parts["maintenance_of_new_equipment"] = maint
        annual = sum(parts.values())
        rows.append({"tag": u["tag"], "annual_opex": annual, "parts": parts, "lifecycle_opex_pv": annual * pv,
                     "capex_P50": sum(cap.get(f"{u['tag']}:{sc}", 0.0) for sc in ("device", "reroute", "sensors", "pcn"))})
    tot = sum(r["annual_opex"] for r in rows)
    extra = sum(e["annual"] for e in data.get("extra_opex", []))
    return {"units": rows, "annual_opex_total": tot + extra, "lifecycle_opex_pv_total": (tot + extra) * pv, "years": years, "discount_rate": rate, "extra_opex_annual": extra,
            "note": "incremental opex of the new equipment only; replacing an installed PSV adds no test cost unless count_replaced_psv_tests is true"}


def package_alarp(data: dict, screened: list[dict], ox: dict) -> list[dict]:
    al = data.get("alarp")
    if not al:
        return []
    rows = []
    for u, o in zip(data["units"], ox["units"]):
        risk = u.get("risk")
        derived = None
        if "sif" in u:
            derived = sif_benefit(u["sif"])
            risk = {"pll_before": derived["pll_before"], "pll_after": derived["pll_after"]}
        if not risk or o["capex_P50"] == 0:
            continue
        cb = alarp.cost_benefit(risk["pll_before"] - risk["pll_after"], o["capex_P50"], o["annual_opex"], al["vpf"], data.get("life_years", 25),
                                al.get("disproportion_factor", 3.0), data.get("discount_rate", al.get("discount_rate", 0.0)))
        for k in ("benefit", "cost", "cost_benefit_ratio", "ICAF"):
            if cb[k] == math.inf:
                cb[k] = None
        rows.append({"tag": u["tag"], "package_capex_P50": o["capex_P50"], "annual_opex": o["annual_opex"], "pll_before": risk["pll_before"], "pll_after": risk["pll_after"],
                     "sif": derived, **cb})
    return rows


def run(data: dict, runs: int = 5000) -> dict:
    errs = check(data)
    if errs:
        raise ValueError("; ".join(errs))
    screened = [screen_unit(u) for u in data["units"]]
    est_in = build_recommendations(data, screened)
    out = {"stage1_2_screen_and_resize": screened}
    if not est_in["recommendations"]:
        out["note"] = "no design changes needed: every device screened adequate"
        return out
    est = recommendation_cost.estimate(est_in, runs=runs)
    out["stage3_bill_of_quantities"] = [{"id": r["id"], "lines": r["lines"]} for r in est_in["recommendations"]]
    out["stage4_capex"] = est
    out["stage5_opex"] = ox = opex_for(data, screened, est, est_in)
    out["lifecycle"] = {"capex_P50": est["portfolio"]["capex"]["P50"], "capex_P80": est["portfolio"]["capex"]["P80"],
                        "lifecycle_cost_P50_pv": est["portfolio"]["capex"]["P50"] + ox["lifecycle_opex_pv_total"] + ox["extra_opex_annual"] * alarp.present_value_factor(ox["years"], ox["discount_rate"]),
                        "years": ox["years"], "discount_rate": ox["discount_rate"]}
    out["stage6_alarp_per_unit_package"] = package_alarp(data, screened, ox)
    out["notes"] = est["notes"] + ["design values are screening results from the toolkit's models: obtain code-compliant sizing and vendor quotes before purchase"]
    return out

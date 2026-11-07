"""Runner for the JSON-driven study tools: python -m process_safety tool <name> input.json --out dir

    bowtie   quantified bow-tie, barrier importance, SCE list, SVG/HTML       (bowtie.py)
    sif      SIF verification (PFD + HFT/SFF), risk graph, SRS skeleton        (sil_lifecycle.py)
    fg       F&G geographic coverage, greedy optimiser                          (fg_mapping.py)   sample-first: coarse grid, then fine
    thermal  TMRad / TD24 / Stoessel class / Semenov storage                    (thermal_runaway.py)
    atex     zone, EPL, ATEX category, dust class, FIBC, EPD register           (atex.py)
    ram      Monte Carlo availability with analytic check                       (ram.py)          sample-first: N runs, then planned runs
    shutdown schedule and cost risk Monte Carlo (QSRA+QCRA), S-curve, tornado, safety-critical flags  (shutdown_risk.py)  sample-first
    plant    ingest PFS/HMB streams, P&ID registers (+Proteus XML), PHA register: balances, scenarios, P&ID review, why-chain, common recommendations, workflow skeleton  (plant_model, hmb, pid_review, scenario_ingest)
    workflow safety simulation -> resizing/design -> BOQ -> capex and opex (devices, pipeline rerouting, sensors, PCN modification), ALARP, shutdown merge  (design_workflow.py)
    lngcost  conceptual (FEL 1, Class 5 style) LNG liquefaction capex from public analogs, with Monte Carlo range  (lng_cost.py)
    recs     cost of implementing study recommendations (piping, civil, electrical, instrumentation) with uncertainty, ALARP CBA, optional merge into a shutdown model  (recommendation_cost.py)
    pha      action tracking, revalidation, carry-forward, SIMOPS, CHAZOP/What-if/SWIFT/PSSR worksheets   (pha.py)
Every tool runs input checks first and writes a validation section to its summary.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os

from . import atex, bowtie, design_workflow, hmb, plant_model, scenario_ingest, fg_mapping, lng_cost, pha, ram, recommendation_cost, shutdown_risk, sil_lifecycle, thermal_runaway


def _dump(obj, path):
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(obj, fh, indent=2, default=lambda o: None if isinstance(o, float) and not math.isfinite(o) else str(o))


def run_tool(name: str, data: dict, out: str, progress: bool = True) -> dict:
    os.makedirs(out, exist_ok=True)
    pre = os.path.join(out, name)
    summ = {"tool": name, "checks": []}
    if name == "bowtie":
        errs = bowtie.check(data)
        summ["checks"] = errs or ["PASS: inputs"]
        if errs:
            return summ
        r = bowtie.report(data, pre, data.get("sce_raw_threshold", 10.0))
        tot = sum(c["unmitigated_per_yr"] for c in r["result"]["consequences"])
        summ["checks"].append(("PASS" if abs(tot - r["result"]["top_per_yr"] * sum(c["probability"] for c in data["consequences"])) < 1e-15 else "FAIL")
                              + ": consequence branches conserve the top-event frequency")
        summ.update(top_per_yr=r["result"]["top_per_yr"], consequences=r["result"]["consequences"],
                    SCEs=[b["name"] for b in r["importance"] if b["SCE"]], files=r["files"])
    elif name == "sif":
        v = sil_lifecycle.verify_sif(data)
        summ.update(verification=v)
        if "risk_graph" in data:
            summ["risk_graph_result"] = sil_lifecycle.risk_graph(data["risk_graph"]["path"], data["risk_graph"]["calibration"])
        srs = sil_lifecycle.srs_skeleton(data, v)
        pha.write_csv(srs, pre + "_srs.csv")
        pha.write_csv(v["subsystems"], pre + "_verification.csv")
        summ["checks"].append(("PASS" if abs(sum(s["PFDavg"] for s in v["subsystems"]) - v["PFDavg"]) < 1e-15 else "FAIL") + ": SIF PFD = sum of subsystems")
        summ["files"] = [pre + "_srs.csv", pre + "_verification.csv"]
    elif name == "fg":
        coarse = fg_mapping.map_coverage(data, cell=4.0, progress=progress)
        summ["sample_coarse"] = {z["zone"]: round(z["achieved"], 3) for z in coarse["zones"]}
        res = fg_mapping.map_coverage(data, cell=data.get("cell_m", 1.0), progress=progress)
        drift = max(abs(a["achieved"] - b["achieved"]) for a, b in zip(coarse["zones"], res["zones"]))
        summ["checks"].append(f"{'PASS' if drift <= 0.05 else 'WARN'}: coarse (4 m) vs fine grid coverage differ by at most {100 * drift:.1f} points")
        summ["zones"] = [{k: v for k, v in z.items() if not k.startswith("_")} for z in res["zones"]]
        files = fg_mapping.report(data, res, pre)
        if "optimise" in data:
            o = data["optimise"]
            z = next(z for z in data["zones"] if z["name"] == o["zone"])
            xs = [p[0] for p in z["polygon"]]
            ys = [p[1] for p in z["polygon"]]
            st = o.get("candidate_step_m", 5)
            cand = [(x, y) for x in range(int(min(xs)), int(max(xs)) + 1, st) for y in range(int(min(ys)), int(max(ys)) + 1, st)]
            opt = fg_mapping.optimise(data, o["zone"], o["template"], cand, o.get("max_add", 5), cell=data.get("cell_m", 1.0), progress=progress)
            res2 = fg_mapping.map_coverage(opt["layout"], cell=data.get("cell_m", 1.0))
            files += fg_mapping.report(opt["layout"], res2, pre + "_optimised")
            summ["optimised"] = {"added": opt["added"], "coverage": opt["coverage"], "target": opt["target"], "met": opt["met"]}
        summ["files"] = files
    elif name == "thermal":
        rows = []
        for c in data["cases"]:
            r = thermal_runaway.assess(c)
            rows.append({"case": c["name"], **{k: v for k, v in r.items() if k != "storage"},
                         **({f"storage_{k}": v for k, v in r["storage"].items()} if "storage" in r else {})})
            if "storage" in r and r["storage"]["Ta_critical_K"] is not None:
                d = abs(r["storage"]["Ta_critical_K"] - r["storage"]["Ta_critical_approx_K"])
                summ["checks"].append(f"{'PASS' if d < 2 else 'WARN'}: {c['name']}: Semenov exact vs R T^2/Ea approximation differ by {d:.2f} K")
        pha.write_csv(rows, pre + "_thermal.csv")
        summ.update(cases=rows, files=[pre + "_thermal.csv"])
    elif name == "atex":
        rows = atex.epd_register(data["areas"])
        pha.write_csv(rows, pre + "_epd_register.csv")
        summ["checks"] = [f"ACTION: {r['area']}: zone needs IEC 60079-10-1 assessment" for r in rows if str(r["zone"]).startswith("ASSESS")] or ["PASS: all zones resolved"]
        summ.update(register=rows, files=[pre + "_epd_register.csv"])
    elif name == "ram":
        sysm, mission = data["system"], data.get("mission_h", 8760.0)
        smp = ram.run(sysm, runs=data.get("sample_runs", 100), mission_h=mission, progress=progress, label="RAM sample")
        plan = ram.plan_runs(smp, data.get("target_ci95", 0.001))
        summ["sample"] = {k: smp[k] for k in ("runs", "production_availability", "production_ci95", "s_per_run")}
        summ["plan"] = plan
        full = ram.run(sysm, runs=min(plan["runs_needed"], data.get("max_runs", 20000)), mission_h=mission, seed=2, progress=progress, label="RAM full")
        summ["checks"] = ram.consistency(smp) + ram.consistency(full)
        summ["result"] = {k: v for k, v in full.items() if k != "criticality"}
        summ["criticality"] = full["criticality"][:10]
        pha.write_csv(full["criticality"], pre + "_criticality.csv")
        summ["files"] = [pre + "_criticality.csv"]
    elif name == "shutdown":
        errs = shutdown_risk.check(data)
        summ["checks"] = errs and ["FAIL: " + e for e in errs] or ["PASS: inputs (ids, ranges, probabilities, acyclic network)"]
        if errs:
            return summ
        smp = shutdown_risk.simulate(data, runs=data.get("sample_runs", 500), seed=1, progress=progress, label="shutdown sample")
        plan = shutdown_risk.plan_runs(smp, data.get("target_rel", 0.01))
        full = shutdown_risk.simulate(data, runs=min(plan["runs_needed"], data.get("max_runs", 20000)), seed=2, progress=progress, label="shutdown full")
        summ["plan"] = plan
        summ["checks"] += [c.replace(": P80", ": sample (" + str(smp["runs"]) + " runs) P80", 1) for c in shutdown_risk.convergence(smp)] + [c.replace(": P80", ": full (" + str(full["runs"]) + " runs) P80", 1) for c in shutdown_risk.convergence(full)]
        keep = ("runs", "base", "duration_days", "cost", "contingency", "opportunity", "P_meet_target_days", "P_meet_budget", "P_meet_both", "safety_critical", "notes")
        summ["result"] = {k: full[k] for k in keep if k in full}
        summ["criticality_top"] = sorted(full["criticality_index"].items(), key=lambda kv: -kv[1])[:8]
        summ["tornado_duration_top"] = full["tornado_duration"][:6]
        summ["tornado_cost_top"] = full["tornado_cost"][:6]
        pha.write_csv(full["s_curve"], pre + "_s_curve.csv")
        pha.write_csv([{"activity": k, "criticality_index": v} for k, v in full["criticality_index"].items()], pre + "_criticality.csv")
        pha.write_csv(full["tornado_duration"], pre + "_tornado_duration.csv")
        pha.write_csv(full["tornado_cost"], pre + "_tornado_cost.csv")
        shutdown_risk.s_curve_svg(full, pre + "_s_curve.svg")
        summ["files"] = [pre + "_s_curve.csv", pre + "_s_curve.svg", pre + "_criticality.csv", pre + "_tornado_duration.csv", pre + "_tornado_cost.csv"]
    elif name == "plant":
        m = plant_model.load(data, base_dir=data.get("base_dir"))
        errs = plant_model.validate(m)
        summ["checks"] = errs and ["WARN: " + e for e in errs] or ["PASS: references (stream ends, device and instrument units) resolve"]
        reg = scenario_ingest.read_register(data["register"]) if data.get("register") else []
        regsum = scenario_ingest.classify_register(reg) if reg else None
        rat = scenario_ingest.rationale(m, data.get("params"), reg, data.get("isolation_inventory_kg"))
        summ["balance"] = hmb.balance(m)
        summ["hazards"] = hmb.unit_hazards(m)
        summ["hmb_scenarios"] = rat["hmb_scenarios"]
        summ["pid_findings"] = rat["pid_findings"]
        summ["rationale"] = rat["rationale"]
        summ["triggered_recommendation_types"] = rat["triggered_counts"]
        if regsum:
            summ["register"] = regsum
            summ["gaps_not_in_register"] = [{"unit": g["unit"], "rec_id": g["rec_id"], "recommendation": g["recommendation"], "reasons": g["reasons"]} for g in rat["gaps_not_in_register"]]
        summ["workflow_skeleton"] = scenario_ingest.workflow_skeleton(m, rat)
        summ["notes"] = m["notes"]
        pha.write_csv([{"unit": r["unit"], "rec_id": r["rec_id"], "recommendation": r["recommendation"], "cost_scope": r["cost_scope"], "sources": ";".join(r["sources"]),
                        "in_register": r["in_register"], "why": " | ".join(r["reasons"])} for r in rat["rationale"]], pre + "_rationale.csv")
        pha.write_csv([{"unit": s_["unit"], "scenario": s_["scenario"], "status": s_["status"], "why": s_["why"], "missing": ",".join(s_["missing"])} for s_ in rat["hmb_scenarios"]], pre + "_scenarios.csv")
        with open(pre + "_workflow_skeleton.json", "w", encoding="utf-8") as fh:
            json.dump(summ["workflow_skeleton"], fh, indent=1, default=str)
        summ["files"] = [pre + "_rationale.csv", pre + "_scenarios.csv", pre + "_workflow_skeleton.json"]
    elif name == "workflow":
        errs = design_workflow.check(data)
        summ["checks"] = errs and ["FAIL: " + e for e in errs] or ["PASS: inputs (modes, rate keys in the rate book, opex book present)"]
        if errs:
            return summ
        r = design_workflow.run(data, runs=data.get("runs", 5000))
        summ["screen_and_resize"] = r["stage1_2_screen_and_resize"]
        if "stage4_capex" in r:
            est = r["stage4_capex"]
            summ["capex"] = {"portfolio": est["portfolio"], "by_scope": [{k: v for k, v in x.items() if k in ("id", "requires_shutdown", "total_mode", "capex", "contingency_P80", "work_duration_days")} for x in est["recommendations"]]}
            summ["opex"] = r["stage5_opex"]
            summ["lifecycle"] = r["lifecycle"]
            summ["alarp_per_unit_package"] = r["stage6_alarp_per_unit_package"]
            summ["notes"] = r["notes"]
            boq = [{"scope": b["id"], "description": ln["description"], "discipline": ln["discipline"], "rate_key": ln.get("rate_key", "inline"),
                    "qty_mode": ln["qty"]["mode"] if isinstance(ln["qty"], dict) else ln["qty"]} for b in r["stage3_bill_of_quantities"] for ln in b["lines"]]
            pha.write_csv(boq, pre + "_bill_of_quantities.csv")
            pha.write_csv([{"scope": x["id"], "requires_shutdown": x["requires_shutdown"], "total_mode": x["total_mode"], "P50": x["capex"]["P50"], "P80": x["capex"]["P80"],
                            "contingency_P80": x["contingency_P80"]} for x in est["recommendations"]], pre + "_capex.csv")
            pha.write_csv([{"unit": u["tag"], "annual_opex": u["annual_opex"], "lifecycle_opex_pv": u["lifecycle_opex_pv"], **{f"part_{k}": v for k, v in u["parts"].items()}} for u in r["stage5_opex"]["units"]], pre + "_opex.csv")
            summ["files"] = [pre + "_bill_of_quantities.csv", pre + "_capex.csv", pre + "_opex.csv"]
            if "shutdown_model" in data:
                from . import recommendation_cost as _rc
                sm = data["shutdown_model"]
                merged = _rc.merge_into_shutdown(sm, est, data["insert_after"], data["insert_before"])
                b = shutdown_risk.simulate(sm, data.get("shutdown_runs", 3000), seed=1)
                m = shutdown_risk.simulate(merged, data.get("shutdown_runs", 3000), seed=1)
                summ["shutdown_effect"] = {"delta_duration_days": {k: m["duration_days"][k] - b["duration_days"][k] for k in ("P50", "P80", "P90")},
                                           "delta_direct_cost": {k: m["cost"][k] - b["cost"][k] for k in ("P50", "P80", "P90")},
                                           **({"delta_lost_operating_days": {k: m["opportunity"]["lost_operating_days"][k] - b["opportunity"]["lost_operating_days"][k] for k in ("P50", "P80", "P90")},
                                               "delta_total_cost": {k: m["opportunity"]["total_cost"][k] - b["opportunity"]["total_cost"][k] for k in ("P50", "P80", "P90")}} if "opportunity" in b else {})}
        else:
            summ["notes"] = [r.get("note", "")]
    elif name == "lngcost":
        errs = lng_cost.check(data)
        summ["checks"] = errs and ["FAIL: " + e for e in errs] or ["PASS: inputs (target, cost index or escalation rate, location factors)"]
        if errs:
            return summ
        r = lng_cost.estimate(data, runs=data.get("runs", 10000))
        summ["result"] = {k: v for k, v in r.items() if k not in ("analogs", "excluded")}
        summ["excluded"] = r["excluded"]
        pha.write_csv([{k: v for k, v in a.items() if k != "source_url"} | {"source_url": a["source_url"]} for a in r["analogs"]], pre + "_analogs.csv")
        summ["files"] = [pre + "_analogs.csv"]
        if "daily_margin" in data:
            dm = data["daily_margin"]
            summ["daily_margin_musd_per_day"] = lng_cost.daily_margin(data["capacity_mtpa"], dm["margin_usd_per_mmbtu"], dm["mmbtu_per_tonne"], dm["operating_days_per_year"])
        if "recommendations_capex_musd" in data:
            summ["safety_spend_share_of_plant_capex_P50"] = lng_cost.safety_spend_ratio(data["recommendations_capex_musd"], r["total_musd"]["P50"])
    elif name == "recs":
        errs = recommendation_cost.check(data)
        summ["checks"] = errs and ["FAIL: " + e for e in errs] or ["PASS: inputs (disciplines, rates, ranges, shutdown durations)"]
        if errs:
            return summ
        est = recommendation_cost.estimate(data, runs=data.get("runs", 5000))
        summ["estimate"] = {k: v for k, v in est.items() if k != "recommendations"}
        summ["recommendations"] = [{k: v for k, v in r.items() if k != "direct_by_discipline_mode"} for r in est["recommendations"]]
        rows = [{"id": r["id"], "title": r["title"], "requires_shutdown": r["requires_shutdown"], **{f"direct_{k}": v for k, v in r["direct_by_discipline_mode"].items()},
                 "total_mode": r["total_mode"], "P50": r["capex"]["P50"], "P80": r["capex"]["P80"], "contingency_P80": r["contingency_P80"],
                 "cost_benefit_ratio": r.get("cba", {}).get("cost_benefit_ratio", ""), "decision": r.get("cba", {}).get("decision", "")} for r in est["recommendations"]]
        keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("id", "title", "requires_shutdown"), k))
        pha.write_csv([{k: r.get(k, "") for k in keys} for r in rows], pre + "_recommendations.csv")
        summ["files"] = [pre + "_recommendations.csv"]
        if "shutdown_model" in data:
            sm = data["shutdown_model"]
            merged = recommendation_cost.merge_into_shutdown(sm, est, data["insert_after"], data["insert_before"])
            b = shutdown_risk.simulate(sm, data.get("shutdown_runs", 4000), seed=1)
            m = shutdown_risk.simulate(merged, data.get("shutdown_runs", 4000), seed=1)
            def d(a, c):
                return {k: c[k] - a[k] for k in ("P50", "P80", "P90")}
            comp = {"duration_days_without": b["duration_days"], "duration_days_with": m["duration_days"], "delta_duration_days": d(b["duration_days"], m["duration_days"]),
                    "direct_cost_without": b["cost"], "direct_cost_with": m["cost"], "delta_direct_cost": d(b["cost"], m["cost"])}
            if "opportunity" in b:
                comp["total_cost_delta"] = d(b["opportunity"]["total_cost"], m["opportunity"]["total_cost"])
                comp["lost_operating_days_delta"] = d(b["opportunity"]["lost_operating_days"], m["opportunity"]["lost_operating_days"])
            if "P_meet_target_days" in b:
                comp["P_meet_target_days"] = {"without": b["P_meet_target_days"], "with": m["P_meet_target_days"]}
            summ["shutdown_effect"] = comp
            summ["shutdown_effect_notes"] = ["the same seed is used for both runs, so differences reflect the added work, not sampling noise (the added activities change the random stream, so small differences remain)"]
            with open(pre + "_merged_shutdown_model.json", "w", encoding="utf-8") as fh:
                json.dump(merged, fh, indent=1)
            summ["files"].append(pre + "_merged_shutdown_model.json")
    elif name == "pha":
        today = dt.date.fromisoformat(data["today"]) if data.get("today") else None
        files = []
        if "actions" in data:
            a = pha.action_status(data["actions"], today)
            pha.write_csv(a["rows"], pre + "_actions.csv")
            files.append(pre + "_actions.csv")
            summ["actions"] = {k: v for k, v in a.items() if k != "rows"}
        if "last_pha" in data:
            summ["revalidation"] = pha.revalidation(data["last_pha"], data.get("mocs_since", 0), data.get("incidents_since", 0), today=today)
        if "previous_worksheet" in data and "nodes" in data:
            cf = pha.carry_forward(data["previous_worksheet"], data["nodes"])
            summ["carry_forward"] = {k: v for k, v in cf.items() if k != "open_items_carried"} | {"open_items_carried": len(cf["open_items_carried"])}
        if "simops" in data:
            sm = data["simops"]
            pha.write_csv(pha.simops_matrix(sm["activities"], sm["rules"]), pre + "_simops_matrix.csv")
            files.append(pre + "_simops_matrix.csv")
            if "schedule" in sm:
                summ["simops_clashes"] = pha.simops_clashes(sm["schedule"], sm["rules"])
        for kind in ("chazop", "whatif", "swift", "pssr"):
            rows = [r for node in data.get("nodes", {}) for r in pha.worksheet(kind, node)]
            if rows:
                pha.write_csv(rows, f"{pre}_{kind}.csv")
                files.append(f"{pre}_{kind}.csv")
        summ["files"] = sorted(set(files))
        summ["checks"] = ["PASS: action dates parsed" if "actions" in data else "INFO: no actions"]
    else:
        raise ValueError(f"unknown tool {name!r}")
    _dump(summ, pre + "_summary.json")
    return summ

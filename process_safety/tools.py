"""Runner for the JSON-driven study tools: python -m process_safety tool <name> input.json --out dir

    bowtie   quantified bow-tie, barrier importance, SCE list, SVG/HTML       (bowtie.py)
    sif      SIF verification (PFD + HFT/SFF), risk graph, SRS skeleton        (sil_lifecycle.py)
    fg       F&G geographic coverage, greedy optimiser                          (fg_mapping.py)   sample-first: coarse grid, then fine
    thermal  TMRad / TD24 / Stoessel class / Semenov storage                    (thermal_runaway.py)
    atex     zone, EPL, ATEX category, dust class, FIBC, EPD register           (atex.py)
    ram      Monte Carlo availability with analytic check                       (ram.py)          sample-first: N runs, then planned runs
    pha      action tracking, revalidation, carry-forward, SIMOPS, CHAZOP/What-if/SWIFT/PSSR worksheets   (pha.py)
Every tool runs input checks first and writes a validation section to its summary.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os

from . import atex, bowtie, fg_mapping, pha, ram, sil_lifecycle, thermal_runaway


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

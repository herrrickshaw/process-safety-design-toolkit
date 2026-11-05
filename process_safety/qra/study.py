"""QRA orchestrator: one JSON study -> the six steps -> results (+ outputs via report.py).

    1 HAZID/HAZOP   hazid.py      checklist register, HAZOP worksheets, LOC scenario register
    2 Frequency     frequency.py  parts count, fault trees, IPLs; eta.py event trees (Cox ignition)
    3 Consequence   effects.py    source terms and lethality footprints (or external Phast/RISKCURVES overrides)
    4 Risk          risk.py       LSIR grid, receptor LSIR/IRPA, F-N, PLL, scenario contributions
    5 Evaluation    alarp.py      tolerability regions and ALARP
    6 Mitigation    mitigation.py measures re-run on a copy of the study, delta risk and cost-benefit

Workflow (small sample first, then scale):  run(study, sample=3) runs a subset of LOC scenarios on a coarser grid, checks every
consistency rule, and projects the full-run time from the measured throughput; run(study) then does the full study.
"""
from __future__ import annotations

import copy
import json
import math
import time

from . import alarp, effects, eta, frequency, hazid, mitigation, risk, validate

DEFAULT_CONVENTIONS = {
    "Cd_gas": 0.85, "Cd_liquid": 0.62,           # discharge coefficients (release.py defaults)
    "aerosol_factor": 2.0,                       # airborne = min(1, factor x flash fraction): rule of thumb, flagged
    "instantaneous_below_s": 20.0,               # releases emptying the inventory faster than this are treated as instantaneous
    "max_duration_s": 3600.0,                    # cap on release / exposure duration
    "thermal_s": 20.0,                           # exposure (escape) time for jet and pool fires
    "flash_fire_lethality": 1.0,                 # p inside the LFL footprint (common QRA convention)
    "vce_yield": 0.05,                           # TNT yield on combustion energy (explosion.py default; highly uncertain)
    "fireball_mass_fraction": 1.0,               # share of a liquefied inventory in the fireball (CCPS practice: whole contents)
    "blast_threshold_kpa": None,                 # optional: p = 1 above this overpressure (e.g. building-collapse basis)
    "vce_overpressure_cap_kpa": 800.0,           # TNT near-field is unphysical for deflagrations: field capped (buildings/EPZ only)
    "sector_subdivisions": 12,                   # sub-directions per wind sector (spreads plumes over the sector width)
}


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def conventions(study: dict) -> dict:
    return {**DEFAULT_CONVENTIONS, **study.get("conventions", {})}


def build_scenarios(study: dict, dataset: dict) -> list[dict]:
    conv = conventions(study)
    ign = study["ignition"]
    secs = {s["id"]: s for s in study["sections"]}
    locs = []
    for s in study["sections"]:
        locs += frequency.loc_scenarios(s, dataset)
    locs += [frequency.extra_scenario(x) for x in study.get("extra_scenarios", [])]
    for sc in locs:
        sec = secs[sc["section"]]
        mat = study["materials"][sec["material"]]
        sc["x"], sc["y"], sc["material"] = sec["x"], sec["y"], sec["material"]
        sc["source_term"] = effects.source_term(sec, mat, sc["hole_mm"], sc["instantaneous"], conv)
        sc["branches"] = eta.branches(sc["source_term"], sec, mat, conv, ign)
    return locs


def pick_sample(scenarios: list[dict], n: int) -> list[dict]:
    """Evenly spaced subset that keeps at least one scenario per section where n allows."""
    if n >= len(scenarios):
        return scenarios
    by_sec = {}
    for s in scenarios:
        by_sec.setdefault(s["section"], []).append(s)
    out = [v[len(v) // 2] for v in by_sec.values()][:n]
    rest = [s for s in scenarios if s not in out]
    k = n - len(out)
    if k > 0:
        step = len(rest) / k
        out += [rest[int(i * step)] for i in range(k)]
    return out


def _effect_builder(study):
    ov = study.get("overrides", {})

    def build(s, o, w):
        spec = ov.get(s["id"], {}).get(o["outcome"])
        if isinstance(spec, dict) and w is not None and w["name"] in spec:
            spec = spec[w["name"]]
        if spec:
            return effects.from_override(spec, o["outcome"].split("+")[0])
        return o["build"](w)
    return build


def core(study: dict, dataset: dict, scenarios: list[dict], grid_spec: dict, progress=True, label="risk integration") -> dict:
    g = risk.Grid(grid_spec["x_min"], grid_spec["x_max"], grid_spec["y_min"], grid_spec["y_max"], grid_spec["step"])
    res = risk.integrate(scenarios, study["weather"], study["wind_rose"], g, study.get("receptors", []), study.get("population", []),
                         study.get("indoor_vulnerability", {}), _effect_builder(study), progress=progress, label=label,
                         sub=int(conventions(study)["sector_subdivisions"]))
    res["fn_curve"] = risk.fn_curve(res["fn_events"])
    return res


def evaluate(study: dict, res: dict) -> dict:
    crit = alarp.get_criteria(study.get("criteria", "uk_hse_r2p2"))
    rec = []
    for r in study.get("receptors", []):
        lsir = res["receptor_lsir"][r["name"]]
        irpa = lsir * r.get("occupancy", 1.0)
        rec.append({"name": r["name"], "group": r["group"], "x": r["x"], "y": r["y"], "LSIR_per_yr": lsir, "occupancy": r.get("occupancy", 1.0),
                    "IRPA_per_yr": irpa, "region": alarp.classify_ir(irpa, r["group"], crit)})
    return {"criteria": crit, "receptors": rec, "societal": alarp.classify_fn(res["fn_curve"], crit)}


def run(study: dict, sample: int | None = None, grid_step: float | None = None, progress=True, strict=True, dataset=None,
        mitigate=True) -> dict:
    t0 = time.perf_counter()
    dataset = dataset or frequency.load_dataset(study.get("frequency_dataset"))
    vin = validate.inputs(study, dataset)
    if strict and not vin:
        raise ValueError("input validation failed:\n  " + "\n  ".join(vin.errors))
    all_sc = build_scenarios(study, dataset)
    scen = pick_sample(all_sc, sample) if sample else all_sc
    gspec = dict(study["grid"])
    if sample and not grid_step:
        gspec["step"] = gspec["step"] * 2
    if grid_step:
        gspec["step"] = grid_step
    res = core(study, dataset, scen, gspec, progress, "base case" + (f" (sample {len(scen)}/{len(all_sc)})" if sample else ""))
    vres = validate.results(res, scen)
    ev = evaluate(study, res)
    out = {"study": study.get("name", "QRA"), "mode": "sample" if sample else "full", "n_scenarios_total": len(all_sc),
           "scenarios": scen, "results": res, "evaluation": ev, "validation_inputs": vin.as_dict(), "validation_results": vres.as_dict(),
           "conventions": conventions(study), "grid_used": gspec, "dataset_sources": dataset["sources"],
           "hazid": hazid.hazid_register(study["sections"]), "hazop": hazid.hazop_rows(study["sections"])}
    if sample:
        b, memo = _effect_builder(study), {}

        def mb(s_, o_, w_):
            k = (s_["id"], o_["outcome"], w_["name"] if w_ else None)
            if k not in memo:
                memo[k] = b(s_, o_, w_)
            return memo[k]
        full_events = risk.count_events(all_sc, study["weather"], study["wind_rose"], int(conventions(study)["sector_subdivisions"]), mb)
        g_full = study["grid"]
        cells_full = ((g_full["x_max"] - g_full["x_min"]) / g_full["step"] + 1) * ((g_full["y_max"] - g_full["y_min"]) / g_full["step"] + 1)
        ratio = (full_events / max(res["events"], 1)) * (cells_full / res["grid"].cells)
        out["projection"] = {"sample_events": res["events"], "full_events": full_events, "sample_s": res["elapsed_s"],
                             "projected_full_base_s": res["elapsed_s"] * ratio,
                             "projected_full_with_mitigation_s": res["elapsed_s"] * ratio * (1 + len(study.get("mitigation", [])))}
        # angular-resolution convergence on the sample: double the wind sub-directions and compare
        s2 = copy.deepcopy(study)
        s2.setdefault("conventions", {})["sector_subdivisions"] = 2 * int(conventions(study)["sector_subdivisions"])
        ids = {y["id"] for y in scen}
        r2 = core(s2, dataset, [x for x in build_scenarios(s2, dataset) if x["id"] in ids], gspec, False)
        rel = lambda a, b: abs(a - b) / max(abs(a), abs(b), 1e-300)
        worst = max([rel(res["pll"], r2["pll"])] + [rel(res["receptor_lsir"][k], r2["receptor_lsir"][k]) for k in res["receptor_lsir"]
                                                    if max(res["receptor_lsir"][k], r2["receptor_lsir"][k]) > 1e-8])
        out["projection"]["angular_convergence_max_change"] = worst
        (vres.ok if worst <= 0.10 else vres.warn)(
            f"angular convergence: doubling wind sub-directions changes PLL/receptor LSIR by at most {100 * worst:.1f}%"
            + ("" if worst <= 0.10 else " - raise conventions.sector_subdivisions before the full run"))
        out["validation_results"] = vres.as_dict()
    mit = []
    if mitigate and study.get("mitigation"):
        al = study["alarp"]
        for m in study["mitigation"]:
            ms = mitigation.apply(study, m)
            msc = build_scenarios(ms, dataset)
            ids = {s["id"] for s in scen}
            msc = [s for s in msc if s["id"] in ids]
            r2 = core(ms, dataset, msc, gspec, progress, f"measure: {m['name'][:12]}")
            v2 = validate.results(r2, msc)
            ev2 = evaluate(ms, r2)
            d_pll = res["pll"] - r2["pll"]
            cba = alarp.cost_benefit(d_pll, m.get("capex", 0.0), m.get("opex_per_yr", 0.0), al["vpf"], al.get("lifetime_yr", 25),
                                     al.get("disproportion_factor", 3.0), al.get("discount_rate", 0.0))
            mit.append({"name": m["name"], "description": m.get("description", ""), "pll_before": res["pll"], "pll_after": r2["pll"],
                        "delta_pll": d_pll, "receptors_after": ev2["receptors"], "societal_after": ev2["societal"], "cba": cba,
                        "max_lsir_after": risk.max_ir(r2["grid"])[0], "validation": v2.as_dict(), "fn_curve_after": r2["fn_curve"],
                        "capex": m.get("capex", 0.0), "opex_per_yr": m.get("opex_per_yr", 0.0)})
    out["mitigation"] = mit
    out["elapsed_total_s"] = time.perf_counter() - t0
    return out


def summary(out: dict) -> dict:
    res, ev = out["results"], out["evaluation"]
    mx = risk.max_ir(res["grid"])
    s = {"study": out["study"], "mode": out["mode"], "scenarios_run": len(out["scenarios"]), "scenarios_total": out["n_scenarios_total"],
         "total_loc_frequency_per_yr": sum(x["frequency_per_yr"] for x in out["scenarios"]), "max_LSIR_per_yr": mx[0], "max_LSIR_at": mx[1:],
         "PLL_per_yr": res["pll"], "events_integrated": res["events"], "effects_built": res["effects_built"],
         "runtime_s": round(out["elapsed_total_s"], 2),
         "receptors": [{k: r[k] for k in ("name", "group", "IRPA_per_yr", "region")} for r in ev["receptors"]],
         "societal_region": ev["societal"]["region"],
         "validation": {"input_errors": len(out["validation_inputs"]["errors"]), "input_warnings": len(out["validation_inputs"]["warnings"]),
                        "result_errors": len(out["validation_results"]["errors"]), "checks_passed": len(out["validation_results"]["passed"])}}
    if "projection" in out:
        s["projection"] = out["projection"]
    if out["mitigation"]:
        s["mitigation"] = [{"name": m["name"], "delta_pll": m["delta_pll"], "cost_benefit_ratio": m["cba"]["cost_benefit_ratio"],
                            "decision": m["cba"]["decision"]} for m in out["mitigation"]]
    return s

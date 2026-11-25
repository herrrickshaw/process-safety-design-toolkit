"""Shutdown / turnaround schedule and cost risk by Monte Carlo (QSRA + QCRA on one CPM network), with a process-safety lens.

Model
    * Activities with three-point durations (min, mode, max; triangular or PERT-beta) joined by finish-to-start precedence.
    * Optional three-point fixed cost and a cost per day of own duration.
    * Duration-driven cost for the whole shutdown (standby crews, scaffolding hire, cranes) and an extra cost per day of overrun
      beyond the target (deferred production, penalties). Both are inputs: the toolkit has no rate data.
    * Opportunity cost of lost plant operation (`opportunity`): margin lost per operating day the plant is not running, charged on
      every day of the shutdown plus ramp-down and ramp-up losses (in equivalent full-rate days), less a recoverable fraction (make-up
      from spare capacity or inventory). Margin is an input. Reported separately from the direct cost, with the lost operating days,
      the on-stream factor for the year and the value of one day.
    * Discrete risk events: probability, which activities they delay (the delay is added to each listed activity), delay and extra
      cost three-point ranges.
    * Optional common-cause factor: one sampled multiplier on all activity durations (weather, labour productivity), which is the
      simplest way to put positive correlation between durations. Without it the activities are independent, which makes the
      spread too narrow: the model says so in its notes.
Outputs: base (all modes, no risk) duration and cost, P10/P50/P80/P90 (and chosen percentiles), contingency = P80 minus base,
probability of meeting the target duration, budget and both, S-curve points, criticality index per activity (share of runs on a
zero-float path), Spearman rank-correlation tornado for duration and cost, and a split-half convergence check.
Process-safety lens: activities flagged `safety_critical` (isolation, gas-free certificate, pre-start safety review) are reported
with their criticality index, because the schedule pressure lands on them; the summary warns when they are on the critical path in
many runs, and states that the contingency must not be bought by shortening them.
Not modelled: resource limits and levelling, calendars (work in calendar days), start-to-start or lag links, correlation other
than the common factor, scope growth beyond the listed risks. A risk register is only as good as the people who filled it in.
"""
from __future__ import annotations

import math
import random
import time

from .qra.progress import Progress


def _tri(rng, r, kind="triangular"):
    a, m, b = r["min"], r["mode"], r["max"]
    if b == a:
        return a
    if kind == "pert":
        mu = (a + 4 * m + b) / 6
        if m == mu:
            alpha = beta = 3.0
        else:
            alpha = (mu - a) * (2 * m - a - b) / ((m - mu) * (b - a))
            beta = alpha * (b - mu) / (mu - a)
        if alpha <= 0 or beta <= 0:
            return rng.triangular(a, b, m)
        return a + (b - a) * rng.betavariate(alpha, beta)
    return rng.triangular(a, b, m)


def check(data: dict) -> list[str]:
    errs = []
    ids = [a["id"] for a in data.get("activities", [])]
    if not ids:
        return ["no activities"]
    if len(ids) != len(set(ids)):
        errs.append("duplicate activity id")
    for a in data["activities"]:
        d = a["duration_days"]
        if not (0 <= d["min"] <= d["mode"] <= d["max"]):
            errs.append(f"{a['id']}: duration needs 0 <= min <= mode <= max")
        for p in a.get("predecessors", []):
            if p not in ids:
                errs.append(f"{a['id']}: unknown predecessor {p}")
        c = a.get("cost_fixed")
        if c and not (0 <= c["min"] <= c["mode"] <= c["max"]):
            errs.append(f"{a['id']}: cost_fixed needs min <= mode <= max")
    for r in data.get("risks", []):
        if not 0 <= r["probability"] <= 1:
            errs.append(f"risk {r['id']}: probability must be in [0, 1]")
        for t in r.get("affects", []):
            if t not in ids:
                errs.append(f"risk {r['id']}: unknown activity {t}")
        for k in ("delay_days", "extra_cost"):
            if k in r and not (0 <= r[k]["min"] <= r[k]["mode"] <= r[k]["max"]):
                errs.append(f"risk {r['id']}: {k} needs 0 <= min <= mode <= max")
    o = data.get("opportunity")
    if o:
        if o.get("margin_per_day", 0) < 0:
            errs.append("opportunity: margin_per_day must be >= 0")
        if not 0 <= o.get("recoverable_fraction", 0.0) <= 1:
            errs.append("opportunity: recoverable_fraction must be in [0, 1]")
        for k in ("ramp_down_days", "ramp_up_days"):
            if k in o and not (0 <= o[k]["min"] <= o[k]["mode"] <= o[k]["max"]):
                errs.append(f"opportunity: {k} needs 0 <= min <= mode <= max")
        if o.get("operating_days_per_year", 365) <= 0:
            errs.append("opportunity: operating_days_per_year must be positive")
    if not errs and _topo(data) is None:
        errs.append("precedence network has a cycle")
    return errs


def _topo(data):
    acts = {a["id"]: a for a in data["activities"]}
    indeg = {i: len(a.get("predecessors", [])) for i, a in acts.items()}
    succ = {i: [] for i in acts}
    for i, a in acts.items():
        for p in a.get("predecessors", []):
            succ[p].append(i)
    order, q = [], [i for i, d in indeg.items() if d == 0]
    while q:
        n = q.pop(0)
        order.append(n)
        for s in succ[n]:
            indeg[s] -= 1
            if indeg[s] == 0:
                q.append(s)
    return order if len(order) == len(acts) else None


def _cpm(order, acts, dur):
    """Forward and backward pass; returns project duration and the set of zero-float activities."""
    es, ef = {}, {}
    for i in order:
        es[i] = max((ef[p] for p in acts[i].get("predecessors", [])), default=0.0)
        ef[i] = es[i] + dur[i]
    T = max(ef.values())
    succ = {i: [] for i in order}
    for i in order:
        for p in acts[i].get("predecessors", []):
            succ[p].append(i)
    lf = {}
    for i in reversed(order):
        lf[i] = min((lf[s] - dur[s] for s in succ[i]), default=T)
    crit = {i for i in order if lf[i] - ef[i] < 1e-9}
    return T, crit


def base_case(data: dict) -> dict:
    """All modes, no risk events, common factor 1."""
    order = _topo(data)
    acts = {a["id"]: a for a in data["activities"]}
    dur = {i: acts[i]["duration_days"]["mode"] for i in order}
    T, crit = _cpm(order, acts, dur)
    cost = sum((acts[i].get("cost_fixed", {}).get("mode", 0.0)) + acts[i].get("cost_per_day", 0.0) * dur[i] for i in order)
    cost += data.get("duration_cost_per_day", 0.0) * T + data.get("overrun_cost_per_day", 0.0) * max(0.0, T - data.get("target_days", T))
    return {"duration_days": T, "cost": cost, "critical_path": [i for i in order if i in crit]}


def pct(sorted_vals, p):
    n = len(sorted_vals)
    if n == 0:
        return float("nan")
    k = (n - 1) * p / 100
    lo = int(math.floor(k))
    hi = min(lo + 1, n - 1)
    return sorted_vals[lo] + (sorted_vals[hi] - sorted_vals[lo]) * (k - lo)


def _ranks(x):
    idx = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(idx):
        j = i
        while j + 1 < len(idx) and x[idx[j + 1]] == x[idx[i]]:
            j += 1
        for k in range(i, j + 1):
            r[idx[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x, y):
    rx, ry = _ranks(x), _ranks(y)
    n = len(x)
    mx, my = sum(rx) / n, sum(ry) / n
    sxx = sum((a - mx) ** 2 for a in rx)
    syy = sum((b - my) ** 2 for b in ry)
    if sxx == 0 or syy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(rx, ry)) / math.sqrt(sxx * syy)


def simulate(data: dict, runs: int = 10000, seed: int = 1, progress=None, label: str = "shutdown risk") -> dict:
    errs = check(data)
    if errs:
        raise ValueError("; ".join(errs))
    rng = random.Random(seed)
    order = _topo(data)
    acts = {a["id"]: a for a in data["activities"]}
    kind = data.get("distribution", "triangular")
    target = data.get("target_days")
    budget = data.get("budget")
    cf = data.get("common_factor")
    risks = data.get("risks", [])
    opp = data.get("opportunity")
    durs, costs, opps, lost, crit_count = [], [], [], [], {i: 0 for i in order}
    inputs = {f"activity {i}": [] for i in order}
    inputs.update({f"risk {r['id']}": [] for r in risks})
    pg = Progress(runs, label) if progress else None
    for n in range(runs):
        f = _tri(rng, cf, kind) if cf else 1.0
        dur = {i: _tri(rng, acts[i]["duration_days"], kind) * f for i in order}
        cost = 0.0
        for i in order:
            a = acts[i]
            if "cost_fixed" in a:
                cost += _tri(rng, a["cost_fixed"], kind)
        for r in risks:
            hit = rng.random() < r["probability"]
            d = _tri(rng, r["delay_days"], kind) if (hit and "delay_days" in r) else 0.0
            c = _tri(rng, r["extra_cost"], kind) if (hit and "extra_cost" in r) else 0.0
            for t in r.get("affects", []):
                dur[t] += d
            cost += c
            inputs[f"risk {r['id']}"].append(d or c or (1.0 if hit else 0.0))
        for i in order:
            cost += acts[i].get("cost_per_day", 0.0) * dur[i]
            inputs[f"activity {i}"].append(dur[i])
        T, crit = _cpm(order, acts, dur)
        for i in crit:
            crit_count[i] += 1
        cost += data.get("duration_cost_per_day", 0.0) * T
        if target is not None:
            cost += data.get("overrun_cost_per_day", 0.0) * max(0.0, T - target)
        durs.append(T)
        costs.append(cost)
        if opp:
            ld = T + (_tri(rng, opp["ramp_down_days"], kind) if "ramp_down_days" in opp else 0.0) + (_tri(rng, opp["ramp_up_days"], kind) if "ramp_up_days" in opp else 0.0)
            lost.append(ld)
            opps.append(ld * opp.get("margin_per_day", 0.0) * (1 - opp.get("recoverable_fraction", 0.0)))
        if pg:
            pg.update(n + 1)
    if pg:
        pg.done()
    sd, sc = sorted(durs), sorted(costs)
    base = base_case(data)
    ps = data.get("percentiles", [10, 50, 80, 90])
    out = {"runs": runs, "seed": seed, "base": base,
           "duration_days": {"mean": sum(durs) / runs, **{f"P{p}": pct(sd, p) for p in ps}},
           "cost": {"mean": sum(costs) / runs, **{f"P{p}": pct(sc, p) for p in ps}}}
    out["contingency"] = {"duration_days_P80": pct(sd, 80) - base["duration_days"], "cost_P80": pct(sc, 80) - base["cost"],
                          "duration_days_P50": pct(sd, 50) - base["duration_days"], "cost_P50": pct(sc, 50) - base["cost"]}
    if target is not None:
        out["P_meet_target_days"] = sum(1 for x in durs if x <= target) / runs
    if budget is not None:
        out["P_meet_budget"] = sum(1 for x in costs if x <= budget) / runs
    if target is not None and budget is not None:
        out["P_meet_both"] = sum(1 for d, c in zip(durs, costs) if d <= target and c <= budget) / runs
    if opp:
        tot = [c + o for c, o in zip(costs, opps)]
        so, st, sl = sorted(opps), sorted(tot), sorted(lost)
        days = opp.get("operating_days_per_year", 365.0)
        f = 1 - opp.get("recoverable_fraction", 0.0)
        out["opportunity"] = {
            "lost_operating_days": {"mean": sum(lost) / runs, **{f"P{p}": pct(sl, p) for p in ps}},
            "opportunity_cost": {"mean": sum(opps) / runs, **{f"P{p}": pct(so, p) for p in ps}},
            "total_cost": {"mean": sum(tot) / runs, **{f"P{p}": pct(st, p) for p in ps}},
            "on_stream_factor_year": {"base": 1 - (base["duration_days"] + sum(opp[k]["mode"] for k in ("ramp_down_days", "ramp_up_days") if k in opp)) / days,
                                      "P50": 1 - pct(sl, 50) / days, "P80": 1 - pct(sl, 80) / days},
            "value_of_one_day": {"opportunity": opp.get("margin_per_day", 0.0) * f, "duration_cost": data.get("duration_cost_per_day", 0.0),
                                 "overrun_penalty_per_day_beyond_target": data.get("overrun_cost_per_day", 0.0),
                                 "total_per_day_before_target": opp.get("margin_per_day", 0.0) * f + data.get("duration_cost_per_day", 0.0),
                                 "total_per_day_beyond_target": opp.get("margin_per_day", 0.0) * f + data.get("duration_cost_per_day", 0.0) + data.get("overrun_cost_per_day", 0.0)},
            "base_total_cost": base["cost"] + (base["duration_days"] + sum(opp[k]["mode"] for k in ("ramp_down_days", "ramp_up_days") if k in opp)) * opp.get("margin_per_day", 0.0) * f,
            "contingency_total_P80": pct(st, 80) - (base["cost"] + (base["duration_days"] + sum(opp[k]["mode"] for k in ("ramp_down_days", "ramp_up_days") if k in opp)) * opp.get("margin_per_day", 0.0) * f),
            "share_of_total_P50_that_is_opportunity": pct(so, 50) / pct(st, 50) if pct(st, 50) else None}
        if data.get("total_budget") is not None:
            out["opportunity"]["P_meet_total_budget"] = sum(1 for x in tot if x <= data["total_budget"]) / runs
        out["s_curve_total"] = [{"p": p, "total_cost": pct(st, p)} for p in range(0, 101, 5)]
        cost_series = tot
    else:
        cost_series = costs
    out["criticality_index"] = {i: crit_count[i] / runs for i in order}
    out["tornado_duration"] = sorted(({"input": k, "spearman": spearman(v, durs)} for k, v in inputs.items()), key=lambda r: -abs(r["spearman"]))
    out["tornado_cost"] = sorted(({"input": k, "spearman": spearman(v, cost_series)} for k, v in inputs.items()), key=lambda r: -abs(r["spearman"]))
    out["s_curve"] = [{"p": p, "duration_days": pct(sd, p), "cost": pct(sc, p)} for p in range(0, 101, 5)]
    out["safety_critical"] = {i: {"name": acts[i].get("name", i), "criticality_index": out["criticality_index"][i]}
                              for i in order if acts[i].get("safety_critical")}
    out["notes"] = notes(data, out)
    h = runs // 2
    out["convergence"] = {"P80_duration_first_half": pct(sorted(durs[:h]), 80), "P80_duration_second_half": pct(sorted(durs[h:]), 80),
                          "P80_cost_first_half": pct(sorted(costs[:h]), 80), "P80_cost_second_half": pct(sorted(costs[h:]), 80)}
    return out


def notes(data, out) -> list[str]:
    n = []
    if "opportunity" in out:
        n.append("tornado_cost ranks inputs against total cost (direct + opportunity) because an opportunity block is present")
        if data["opportunity"].get("recoverable_fraction", 0.0) == 0.0:
            n.append("recoverable_fraction is 0: every lost day is treated as permanently lost margin; if spare capacity or inventory can make production up, say so")
        if data.get("total_budget") is None:
            n.append("no total_budget given: P_meet_budget compares direct cost only")
    if not data.get("common_factor"):
        n.append("no common_factor: durations are independent, so the spread is narrower than real projects show; add a factor for weather or productivity")
    if out["duration_days"]["P50"] <= out["base"]["duration_days"] * 1.0001:
        n.append("P50 duration is not above the base case: risk events and skew are small, or the distributions are symmetric; check that the ranges are not too tight")
    for i, v in out["safety_critical"].items():
        if v["criticality_index"] >= 0.5:
            n.append(f"safety-critical activity '{v['name']}' is on the critical path in {100 * v['criticality_index']:.0f}% of runs: schedule pressure will land on it; do not buy schedule by shortening it")
    n.append("work in calendar days; no resource limits or calendars; contingency is P80 minus the all-modes base case, not an allowance for unknown unknowns")
    return n


def convergence(out: dict, tol: float = 0.01) -> list[str]:
    c = out["convergence"]
    res = []
    for k in ("duration", "cost"):
        a, b = c[f"P80_{k}_first_half"], c[f"P80_{k}_second_half"]
        d = abs(a - b) / max(abs(b), 1e-12)
        res.append(f"{'PASS' if d <= tol else 'WARN'}: P80 {k} halves differ by {100 * d:.2f}% (tolerance {100 * tol:.0f}%)")
    return res


def plan_runs(sample: dict, target_rel: float = 0.01, minimum: int = 2000) -> dict:
    """Runs needed so the P80 duration and cost are stable to ~target_rel, from the split-half differences of a small sample
    (sampling error of a percentile falls as 1/sqrt(N)); never fewer than `minimum`."""
    c = sample["convergence"]
    d = max(abs(c["P80_duration_first_half"] - c["P80_duration_second_half"]) / max(abs(c["P80_duration_second_half"]), 1e-12),
            abs(c["P80_cost_first_half"] - c["P80_cost_second_half"]) / max(abs(c["P80_cost_second_half"]), 1e-12), 1e-6)
    need = int(min(200000, max(minimum, sample["runs"] * (d / target_rel) ** 2)))
    return {"sample_runs": sample["runs"], "observed_half_difference": d, "runs_needed": need}


def run_timed(data, runs, seed=1, progress=False):
    t0 = time.time()
    r = simulate(data, runs, seed, progress)
    r["seconds"] = time.time() - t0
    return r


def s_curve_svg(out: dict, path: str, width: int = 640, height: int = 360) -> None:
    """Duration S-curve (cumulative probability against days) with base, P50 and P80 marked. Plain SVG, no dependencies."""
    pts = out["s_curve"]
    xs = [p["duration_days"] for p in pts]
    lo, hi = min(xs), max(xs)
    span = (hi - lo) or 1.0
    L, R, T, B = 60, 20, 20, 50
    X = lambda v: L + (v - lo) / span * (width - L - R)          # noqa: E731
    Y = lambda p: height - B - p / 100 * (height - T - B)       # noqa: E731
    poly = " ".join(f"{X(p['duration_days']):.1f},{Y(p['p']):.1f}" for p in pts)
    marks = [("base", out["base"]["duration_days"], "#555"), ("P50", out["duration_days"]["P50"], "#12355B"), ("P80", out["duration_days"]["P80"], "#E07A1F")]
    g = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" font-family="Arial" font-size="12">',
         f'<rect width="{width}" height="{height}" fill="white"/>',
         f'<line x1="{L}" y1="{Y(0)}" x2="{width - R}" y2="{Y(0)}" stroke="#999"/><line x1="{L}" y1="{Y(0)}" x2="{L}" y2="{Y(100)}" stroke="#999"/>',
         f'<polyline points="{poly}" fill="none" stroke="#12355B" stroke-width="2.5"/>']
    for lab, v, col in marks:
        if lo <= v <= hi:
            g.append(f'<line x1="{X(v):.1f}" y1="{Y(0)}" x2="{X(v):.1f}" y2="{Y(100)}" stroke="{col}" stroke-dasharray="4 3"/><text x="{X(v) + 3:.1f}" y="{Y(100) + 12}" fill="{col}">{lab} {v:.1f}</text>')
    for p in (0, 25, 50, 75, 100):
        g.append(f'<text x="{L - 8}" y="{Y(p) + 4}" text-anchor="end">{p}%</text>')
    g.append(f'<text x="{(L + width - R) / 2}" y="{height - 12}" text-anchor="middle">shutdown duration, days (S-curve, {out["runs"]} runs)</text></svg>')
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(g))

"""Reliability, availability and maintainability (RAM): Monte Carlo of a series-of-stages system with k-out-of-n redundancy and
capacity, exponential failures and exponential or lognormal repairs, with an analytic cross-check, downtime criticality ranking,
confidence intervals, and a small-sample-first workflow (projection of runs and time needed for a target precision).

System model:  stages in series; stage s has n_s identical-or-listed units, needs k_s up for full capacity;
               stage capacity = min(1, up_s / k_s) (degraded operation pro rata) or 0/1 if capacity_mode = "binary".
               production availability = time-average of min_s capacity_s, minus planned shutdown fraction.
Analytic check (exponential failures and repairs, independent units, unlimited repair crews, long mission):
               P(stage up) = sum_{j>=k} C(n,j) A^j (1-A)^(n-j), A = MTBF/(MTBF+MTTR); P(system fully up) = prod_s P(stage up).
               The simulated 'full-capacity availability' must agree within its confidence interval - checked by consistency().
"""
from __future__ import annotations

import math
import random
import time

from .qra.progress import Progress


def _units(stage):
    if "units" in stage:
        return stage["units"]
    return [{"name": f"{stage['name']}-{i + 1}", "mtbf_h": stage["mtbf_h"], "mttr_h": stage["mttr_h"], "repair": stage.get("repair", "exp"),
             "repair_cv": stage.get("repair_cv", 1.0)} for i in range(stage["n"])]


def _repair(rng, u):
    if u.get("repair", "exp") == "exp":
        return rng.expovariate(1 / u["mttr_h"])
    cv = u.get("repair_cv", 1.0)
    s2 = math.log(1 + cv * cv)
    mu = math.log(u["mttr_h"]) - s2 / 2
    return rng.lognormvariate(mu, math.sqrt(s2))


def simulate_once(system: dict, mission_h: float, rng: random.Random) -> dict:
    stages = system["stages"]
    events = []  # (time, stage_idx, unit_idx, +1 up / -1 down)
    for si, st in enumerate(stages):
        for ui, u in enumerate(_units(st)):
            t = 0.0
            while True:
                t += rng.expovariate(1 / u["mtbf_h"])
                if t >= mission_h:
                    break
                events.append((t, si, ui, -1))
                t += _repair(rng, u)
                if t >= mission_h:
                    break
                events.append((t, si, ui, +1))
    events.sort()
    ups = [len(_units(st)) for st in stages]
    down_units = [set() for _ in stages]
    ks = [st["k"] for st in stages]
    binary = system.get("capacity_mode", "proportional") == "binary"

    def cap():
        c = []
        for s, k in enumerate(ks):
            c.append((1.0 if ups[s] >= k else 0.0) if binary else min(1.0, ups[s] / k))
        return min(c)
    t_prev, prod, full_up, lost_by_unit = 0.0, 0.0, 0.0, {}
    c = cap()
    for t, si, ui, d in events + [(mission_h, -1, -1, 0)]:
        dt = t - t_prev
        prod += c * dt
        full_up += dt if c >= 1.0 else 0.0
        if c < 1.0:  # attribute lost production to the down units of the limiting stage(s), shared equally
            caps = [(1.0 if ups[s] >= k else 0.0) if binary else min(1.0, ups[s] / k) for s, k in enumerate(ks)]
            lim = [s for s, v in enumerate(caps) if v == c]
            culprits = [(s, u) for s in lim for u in down_units[s]]
            for cu in culprits:
                lost_by_unit[cu] = lost_by_unit.get(cu, 0.0) + (1 - c) * dt / len(culprits)
        if si < 0:
            break
        ups[si] += d
        (down_units[si].discard if d > 0 else down_units[si].add)(ui)
        c = cap()
        t_prev = t
    failures = sum(1 for e in events if e[3] < 0)
    return {"production": prod / mission_h, "full_capacity": full_up / mission_h, "failures": failures, "lost": lost_by_unit}


def analytic_full_capacity(system: dict) -> float:
    p = 1.0
    for st in system["stages"]:
        us = _units(st)
        if any(u.get("repair", "exp") != "exp" for u in us) or len({(u["mtbf_h"], u["mttr_h"]) for u in us}) > 1:
            return float("nan")
        A = us[0]["mtbf_h"] / (us[0]["mtbf_h"] + us[0]["mttr_h"])
        n, k = len(us), st["k"]
        p *= sum(math.comb(n, j) * A ** j * (1 - A) ** (n - j) for j in range(k, n + 1))
    return p


def run(system: dict, runs: int = 200, mission_h: float = 8760.0, seed: int = 1, progress=True, label="RAM Monte Carlo") -> dict:
    rng = random.Random(seed)
    prog = Progress(runs, label, enabled=progress)
    t0 = time.perf_counter()
    P, F, N, lost = [], [], [], {}
    for _ in range(runs):
        r = simulate_once(system, mission_h, rng)
        P.append(r["production"])
        F.append(r["full_capacity"])
        N.append(r["failures"])
        for k, v in r["lost"].items():
            lost[k] = lost.get(k, 0.0) + v / mission_h / runs
        prog.update()
    prog.done()
    el = time.perf_counter() - t0
    mean = lambda x: sum(x) / len(x)
    sd = lambda x: math.sqrt(sum((v - mean(x)) ** 2 for v in x) / max(len(x) - 1, 1))
    planned = system.get("planned_shutdown_fraction", 0.0)
    names = {(si, ui): u["name"] for si, st in enumerate(system["stages"]) for ui, u in enumerate(_units(st))}
    crit = sorted(({"unit": names[k], "production_loss_share": v} for k, v in lost.items()), key=lambda r: -r["production_loss_share"])
    pm, ps = mean(P), sd(P)
    half = 1.96 * ps / math.sqrt(runs)
    return {"runs": runs, "mission_h": mission_h, "production_availability": pm * (1 - planned), "production_unplanned": pm, "production_ci95": half * (1 - planned),
            "full_capacity_availability": mean(F), "full_capacity_ci95": 1.96 * sd(F) / math.sqrt(runs),
            "analytic_full_capacity": analytic_full_capacity(system), "failures_per_mission": mean(N), "criticality": crit,
            "elapsed_s": el, "s_per_run": el / runs, "sd_production": ps}


def plan_runs(sample: dict, target_ci95: float) -> dict:
    """From a small sample run, the runs (and time) needed for a production-availability CI95 half-width of target_ci95."""
    n = math.ceil((1.96 * sample["sd_production"] / target_ci95) ** 2) if sample["sd_production"] > 0 else sample["runs"]
    return {"runs_needed": max(n, sample["runs"]), "projected_s": max(n, sample["runs"]) * sample["s_per_run"]}


def consistency(res: dict) -> list[str]:
    """Identities: (1) attributed loss shares sum to 1 - unplanned production availability (every lost hour is assigned to the
    down units of the limiting stage); (2) simulated full-capacity availability agrees with the analytic value (exponential,
    identical units) within 3 x CI95 + 0.2 % (finite-mission start-up bias: all units start up)."""
    msgs = []
    share = sum(c["production_loss_share"] for c in res["criticality"])
    gap = abs(share - (1 - res["production_unplanned"]))
    msgs.append(("PASS" if gap < 1e-9 else "FAIL") + f": attributed loss {share:.6f} = 1 - production availability {1 - res['production_unplanned']:.6f}")
    a = res["analytic_full_capacity"]
    if a == a:
        tol = 3 * res["full_capacity_ci95"] + 0.002
        ok = abs(res["full_capacity_availability"] - a) <= tol
        msgs.append(("PASS" if ok else "FAIL") + f": simulated full-capacity availability {res['full_capacity_availability']:.5f} vs analytic {a:.5f} (tol {tol:.5f})")
    if not 0 <= res["production_availability"] <= 1:
        msgs.append("FAIL: production availability outside [0, 1]")
    return msgs

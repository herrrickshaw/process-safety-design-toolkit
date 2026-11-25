"""Cost estimate for implementing process-safety study recommendations (HAZOP / LOPA / QRA / PSSR actions): piping changes, civil work,
electrical changes, instrumentation and other construction modifications, with uncertainty, shutdown dependency and ALARP cost-benefit.

Method
    * Each recommendation has estimate lines: discipline, quantity (number or min/mode/max), unit rate (number or min/mode/max, either
      given on the line or looked up in a `rate_book` you supply). The toolkit ships NO unit rates; the example file is illustrative.
    * Direct cost = sum of quantity x rate. Indirects are percentages of direct cost that you supply (engineering, procurement,
      construction management, owner's cost, commissioning, escalation); none is defaulted.
    * Uncertainty: Monte Carlo on quantities and rates (independent per line) plus an optional `rate_factor` multiplier for market
      conditions, shared by all lines (positive correlation). Contingency is then P-value minus the all-modes base, not a flat percentage.
    * Shutdown dependency: a recommendation that `requires_shutdown` carries a work duration and can be merged into a `shutdown_risk`
      model (`merge_into_shutdown`), so its duration, cost and the lost operating days feed the turnaround schedule and cost risk.
    * Benefit and ALARP: with `pll_before` and `pll_after` (potential loss of life per year) and the study's VPF, disproportion factor,
      life and discount rate, the existing `qra.alarp.cost_benefit` gives the cost-benefit ratio. A measure is expected unless its cost is
      grossly disproportionate to its benefit; CBA is one input: relevant good practice, legal requirements and measures that bring a risk
      from intolerable to tolerable are expected regardless (see docs/QRA.md).
Not modelled: resource-loaded construction schedules, productivity, access and congestion factors, hazardous-area work-permit delays
(put those in the shutdown risk register), and the cost of the management of change and pre-startup review themselves unless you add lines.
"""
from __future__ import annotations

import copy
import random

from .qra import alarp
from .shutdown_risk import _tri, pct

DISCIPLINES = ("piping", "civil", "electrical", "instrumentation", "mechanical", "other")
INDIRECTS = ("engineering_pct", "procurement_pct", "construction_mgmt_pct", "owner_pct", "commissioning_pct", "escalation_pct")


def _r3(x):
    """Number or {min, mode, max} -> three-point dict."""
    return {"min": x, "mode": x, "max": x} if isinstance(x, (int, float)) else x


def _line_rate(line, book):
    if "rate" in line:
        return _r3(line["rate"])
    if "rate_key" in line:
        return _r3(book[line["rate_key"]]["rate"])
    raise KeyError(f"line {line.get('description', '?')}: give rate or rate_key")


def check(data: dict) -> list[str]:
    errs = []
    book = data.get("rate_book", {})
    ids = [r["id"] for r in data.get("recommendations", [])]
    if not ids:
        return ["no recommendations"]
    if len(ids) != len(set(ids)):
        errs.append("duplicate recommendation id")
    for r in data["recommendations"]:
        if not r.get("lines"):
            errs.append(f"{r['id']}: no estimate lines")
        for ln in r.get("lines", []):
            if ln.get("discipline") not in DISCIPLINES:
                errs.append(f"{r['id']}: discipline must be one of {', '.join(DISCIPLINES)}")
            if "rate" not in ln and ln.get("rate_key") not in book:
                errs.append(f"{r['id']}: line '{ln.get('description', '?')}' has no rate and rate_key is not in rate_book")
                continue
            for nm, v in (("qty", _r3(ln["qty"])), ("rate", _line_rate(ln, book))):
                if not 0 <= v["min"] <= v["mode"] <= v["max"]:
                    errs.append(f"{r['id']}: {ln.get('description', '?')}: {nm} needs 0 <= min <= mode <= max")
        if r.get("requires_shutdown") and "work_duration_days" not in r:
            errs.append(f"{r['id']}: requires_shutdown needs work_duration_days")
        if "pll_before" in r and not (0 <= r.get("pll_after", 0) <= r["pll_before"]):
            errs.append(f"{r['id']}: pll_after must be between 0 and pll_before")
    for k in INDIRECTS:
        if data.get("indirects", {}).get(k, 0) < 0:
            errs.append(f"indirects.{k} must be >= 0")
    return errs


def _indirect_factor(data):
    ind = data.get("indirects", {})
    f = 1.0 + sum(ind.get(k, 0.0) for k in INDIRECTS if k != "escalation_pct") / 100.0
    return f * (1.0 + ind.get("escalation_pct", 0.0) / 100.0)


def _base(rec, data):
    book = data.get("rate_book", {})
    by = {d: 0.0 for d in DISCIPLINES}
    for ln in rec["lines"]:
        by[ln["discipline"]] += _r3(ln["qty"])["mode"] * _line_rate(ln, book)["mode"]
    direct = sum(by.values())
    return by, direct, direct * _indirect_factor(data)


def estimate(data: dict, runs: int = 5000, seed: int = 1) -> dict:
    errs = check(data)
    if errs:
        raise ValueError("; ".join(errs))
    rng = random.Random(seed)
    kind = data.get("distribution", "pert")
    book = data.get("rate_book", {})
    fac = _indirect_factor(data)
    rf = data.get("rate_factor")
    recs = data["recommendations"]
    samples = {r["id"]: [] for r in recs}
    portfolio = []
    for _ in range(runs):
        k = _tri(rng, rf, kind) if rf else 1.0
        tot = 0.0
        for r in recs:
            d = 0.0
            for ln in r["lines"]:
                d += _tri(rng, _r3(ln["qty"]), kind) * _tri(rng, _line_rate(ln, book), kind) * k
            c = d * fac
            samples[r["id"]].append(c)
            tot += c
        portfolio.append(tot)
    al = data.get("alarp")
    basis = data.get("capex_basis", "P50")
    rows = []
    for r in recs:
        by, direct, base_total = _base(r, data)
        s = sorted(samples[r["id"]])
        row = {"id": r["id"], "title": r.get("title", r["id"]), "source": r.get("source", ""), "requires_shutdown": bool(r.get("requires_shutdown")),
               "direct_by_discipline_mode": {k: v for k, v in by.items() if v}, "direct_mode": direct, "total_mode": base_total,
               "capex": {"mean": sum(s) / runs, "P10": pct(s, 10), "P50": pct(s, 50), "P80": pct(s, 80), "P90": pct(s, 90)},
               "contingency_P80": pct(s, 80) - base_total}
        if r.get("requires_shutdown"):
            row["work_duration_days"] = r["work_duration_days"]
        if al and "pll_before" in r:
            capex = row["capex"][basis] if basis in row["capex"] else base_total
            years = r.get("life_years", al.get("lifetime_yr", 25))
            opex = capex * r.get("opex_pct_of_capex", 0.0) / 100.0
            cb = alarp.cost_benefit(r["pll_before"] - r.get("pll_after", 0.0), capex, opex, al["vpf"], years, al.get("disproportion_factor", 3.0), al.get("discount_rate", 0.0))
            row["cba"] = {"capex_basis": basis, "capex_used": capex, "delta_pll_per_yr": r["pll_before"] - r.get("pll_after", 0.0), **cb}
        rows.append(row)
    sp = sorted(portfolio)
    online = [x for x in rows if not x["requires_shutdown"]]
    by_disc = {d: sum(x["direct_by_discipline_mode"].get(d, 0.0) for x in rows) for d in DISCIPLINES}
    out = {"runs": runs, "seed": seed, "currency": data.get("currency", ""),
           "recommendations": rows,
           "portfolio": {"total_mode": sum(x["total_mode"] for x in rows), "capex": {"mean": sum(portfolio) / runs, "P10": pct(sp, 10), "P50": pct(sp, 50), "P80": pct(sp, 80), "P90": pct(sp, 90)},
                         "contingency_P80": pct(sp, 80) - sum(x["total_mode"] for x in rows),
                         "shutdown_work_total_mode": sum(x["total_mode"] for x in rows if x["requires_shutdown"]),
                         "online_work_total_mode": sum(x["total_mode"] for x in online),
                         "direct_by_discipline_mode": {k: v for k, v in by_disc.items() if v}},
           "indirect_factor": fac}
    if al:
        ranked = [x for x in rows if "cba" in x]
        out["ranking_by_ICAF"] = sorted(
            ({"id": x["id"], "title": x["title"], "ICAF": None if x["cba"]["ICAF"] == float("inf") else x["cba"]["ICAF"],
              "cost_benefit_ratio": None if x["cba"]["cost_benefit_ratio"] == float("inf") else x["cba"]["cost_benefit_ratio"], "decision": x["cba"]["decision"]} for x in ranked),
            key=lambda y: (y["ICAF"] is None, y["ICAF"] or 0))
    out["notes"] = notes(data, out)
    return out


def notes(data, out) -> list[str]:
    n = []
    if not data.get("indirects"):
        n.append("no indirects given: engineering, procurement, construction management, owner's cost and commissioning are all zero, so the estimate is direct cost only")
    if not data.get("rate_factor"):
        n.append("no rate_factor: line costs are independent, so the portfolio spread is narrower than market-driven reality; add a shared rate factor")
    if any(r.get("requires_shutdown") for r in data["recommendations"]):
        n.append("shutdown-dependent items add duration and lost operating days: merge them into the shutdown model (tool recs with shutdown_model) rather than reading their cost alone")
    n.append("every modification needs management of change and a pre-startup safety review before start-up; add those lines or schedule activities if they are not already in the estimate")
    n.append("CBA is one input to ALARP: legal requirements, relevant good practice and measures that remove an intolerable risk are expected regardless of the ratio")
    return n


def merge_into_shutdown(shutdown: dict, est: dict, insert_after: list[str], insert_before: list[str], recs: dict | None = None) -> dict:
    """Return a copy of the shutdown model with each shutdown-dependent recommendation added as an activity after `insert_after` and
    before `insert_before`; the activity cost is the recommendation's capex (P10 / P50 / P90 as min / mode / max)."""
    m = copy.deepcopy(shutdown)
    ids = {a["id"] for a in m["activities"]}
    new = []
    for row in est["recommendations"]:
        if not row["requires_shutdown"]:
            continue
        aid = "MOD-" + row["id"]
        if aid in ids:
            raise ValueError(f"activity {aid} already exists")
        c = row["capex"]
        new.append({"id": aid, "name": "Modification: " + row["title"], "predecessors": list(insert_after), "duration_days": _r3(row["work_duration_days"]),
                    "cost_fixed": {"min": c["P10"], "mode": c["P50"], "max": max(c["P90"], c["P50"])}})
    for a in m["activities"]:
        if a["id"] in insert_before:
            a["predecessors"] = list(a.get("predecessors", [])) + [x["id"] for x in new]
    m["activities"] += new
    return m

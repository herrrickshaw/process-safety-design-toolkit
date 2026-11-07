"""Conceptual (FEL 1, AACE Class 5 style) capital cost of an onshore LNG liquefaction plant from past projects (analogs).

Method (a simplified, dependency-free version of the analog approach documented by ORIMIZ-Consulting/open-fel1-lng-cost, MIT licence):
    1. take each analog's published plant-only cost, in the dollars of its cost year (`data/lng_analogs.json`, 24 projects);
    2. escalate to the target year with a cost index or a constant rate that YOU supply;
    3. correct for location with factors that YOU supply for the target and for each analog's location code;
    4. bring the site type to a greenfield basis (published OIES / guideline factors, editable) and back to the target's site type;
    5. scale for train size: unit cost x (target train / analog train)^(n - 1), n = 0.7 by default (common practice, 0.6 to 0.8 shown);
    6. read the central value from the adjusted analogs and range it by Monte Carlo (analog choice, size exponent, location factor,
       escalation rate, definition growth).
What the toolkit does NOT ship: a cost index and location factors. Without them the estimate cannot be made, which is deliberate: the two
largest judgments in the method are yours. The result is a screening number for comparing concepts and sizing contingency for safety
studies; it is not a budget and must not be used for an investment decision. Scope differs between analogs (some plant-only figures are
OIES splits of integrated projects), final costs are usually higher than FID budgets, and 2014-18 conditions shape the published factors.
"""
from __future__ import annotations

import json
import math
import os
import random

from .shutdown_risk import _tri, pct

_PATH = os.path.join(os.path.dirname(__file__), "data", "lng_analogs.json")
_CACHE: dict | None = None
# Brings each site type to a greenfield basis (multiply). Values and sources: ORIMIZ factors.py citing OIES NG137 (brownfield 1.50, partly
# brownfield 1.15) and a stated judgment (brownfield_partial 1.25). Override with site_factors.
SITE_TO_GREENFIELD = {"greenfield": 1.00, "greenfield_industrial": 1.15, "brownfield_partial": 1.25, "brownfield": 1.50}
DEFAULT_EXPONENT = 0.7
EXPONENT_RANGE = (0.6, 0.8)
DEFINITION_GROWTH = (0.0, 0.15)          # guideline range (judgment), applied as a multiplier of 1 + g
CLASS5_TYPICAL = (-0.30, 0.50)           # ORIMIZ default for Class 5; AACE RP 18R-97 quotes wider ranges (not read here)


def data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def analogs() -> list[dict]:
    return list(data()["analogs"])


def _escalation(cfg: dict, from_year: int, to_year: int, rate: float | None = None) -> float:
    """Ratio of the cost level in to_year to that in from_year."""
    if "cost_index" in cfg:
        ix = {int(k): v for k, v in cfg["cost_index"].items()}
        if from_year not in ix or to_year not in ix:
            raise ValueError(f"cost_index needs values for {from_year} and {to_year}")
        return ix[to_year] / ix[from_year]
    r = cfg["escalation_pct_per_year"] if rate is None else rate
    return (1 + r / 100.0) ** (to_year - from_year)


def check(cfg: dict) -> list[str]:
    errs = []
    for k in ("capacity_mtpa", "trains", "site_type", "target_year", "location_code"):
        if k not in cfg:
            errs.append(f"missing {k}")
    if errs:
        return errs
    if cfg["capacity_mtpa"] <= 0 or cfg["trains"] < 1:
        errs.append("capacity_mtpa must be positive and trains at least 1")
    sf = {**SITE_TO_GREENFIELD, **cfg.get("site_factors", {})}
    if cfg["site_type"] not in sf:
        errs.append(f"site_type must be one of {', '.join(sf)}")
    if "cost_index" not in cfg and "escalation_pct_per_year" not in cfg:
        errs.append("give cost_index {year: value} or escalation_pct_per_year: the toolkit ships no cost index")
    if "location_factors" not in cfg or cfg["location_code"] not in cfg.get("location_factors", {}):
        errs.append("location_factors must include the target location_code: the toolkit ships no location factors")
    return errs


def adjust(cfg: dict) -> dict:
    """Deterministic analog table at the central settings. Returns rows (kept and excluded with reasons) and summary values."""
    errs = check(cfg)
    if errs:
        raise ValueError("; ".join(errs))
    sf = {**SITE_TO_GREENFIELD, **cfg.get("site_factors", {})}
    n = cfg.get("exponent", DEFAULT_EXPONENT)
    loc = cfg["location_factors"]
    band = cfg.get("size_band", (0.5, 2.0))
    ty = cfg["target_year"]
    train = cfg["capacity_mtpa"] / cfg["trains"]
    esc_rate = cfg.get("escalation_pct_per_year")
    mid_rate = esc_rate["mode"] if isinstance(esc_rate, dict) else esc_rate
    kept, dropped = [], []
    for a in analogs():
        why = None
        if cfg.get("exclude_scopes") and a["scope"] in cfg["exclude_scopes"]:
            why = f"scope {a['scope']} excluded"
        elif a["location_code"] not in loc:
            why = f"no location factor for {a['location_code']}"
        elif not band[0] <= a["train_size_mtpa"] / train <= band[1]:
            why = f"train size {a['train_size_mtpa']:.1f} MTPA outside {band[0]}-{band[1]}x of target {train:.1f}"
        elif cfg.get("max_age_years") and ty - a["fid_year"] > cfg["max_age_years"]:
            why = f"FID {a['fid_year']} older than {cfg['max_age_years']} years"
        elif a["site_type"] not in sf:
            why = f"unknown site type {a['site_type']}"
        if why:
            dropped.append({"id": a["id"], "reason": why})
            continue
        unit0 = a["plant_only_musd"] / a["capacity_mtpa"]
        e = _escalation(cfg, a["cost_year"], ty, mid_rate)
        l = loc[cfg["location_code"]] / loc[a["location_code"]]            # noqa: E741
        s = sf[a["site_type"]] / sf[cfg["site_type"]]
        z = (train / a["train_size_mtpa"]) ** (n - 1)
        unit = unit0 * e * l * s * z
        kept.append({"id": a["id"], "project": a["project"], "unit_musd_per_mtpa_published": unit0, "cost_year": a["cost_year"], "escalation": e,
                     "location": l, "site_type": s, "size_scaling": z, "unit_musd_per_mtpa_adjusted": unit, "total_musd": unit * cfg["capacity_mtpa"],
                     "grade": a["grade"], "scope": a["scope"], "source_url": a["source_url"]})
    if not kept:
        raise ValueError("no analogs left after filters: " + "; ".join(d["reason"] for d in dropped[:5]))
    u = sorted(k["unit_musd_per_mtpa_adjusted"] for k in kept)
    return {"kept": kept, "excluded": dropped, "median_unit": pct(u, 50), "mean_unit": sum(u) / len(u),
            "median_total_musd": pct(u, 50) * cfg["capacity_mtpa"], "mean_total_musd": sum(u) / len(u) * cfg["capacity_mtpa"]}


def estimate(cfg: dict, runs: int = 10000, seed: int = 1) -> dict:
    adj = adjust(cfg)
    rng = random.Random(seed)
    ty = cfg["target_year"]
    train = cfg["capacity_mtpa"] / cfg["trains"]
    sf = {**SITE_TO_GREENFIELD, **cfg.get("site_factors", {})}
    loc = cfg["location_factors"]
    lr = cfg.get("location_factor_range")            # {min, mode, max} for the target factor
    er = cfg.get("escalation_pct_per_year")
    dg = cfg.get("definition_growth", {"min": DEFINITION_GROWTH[0], "mode": sum(DEFINITION_GROWTH) / 2, "max": DEFINITION_GROWTH[1]})
    exr = cfg.get("exponent_range", EXPONENT_RANGE)
    pool = [a for a in analogs() if a["id"] in {k["id"] for k in adj["kept"]}]
    totals = []
    for _ in range(runs):
        a = rng.choice(pool)
        n = rng.uniform(*exr)
        tl = _tri(rng, lr) if lr else loc[cfg["location_code"]]
        rate = _tri(rng, er) if isinstance(er, dict) else None
        e = _escalation(cfg, a["cost_year"], ty, rate)
        unit = (a["plant_only_musd"] / a["capacity_mtpa"]) * e * (tl / loc[a["location_code"]]) * (sf[a["site_type"]] / sf[cfg["site_type"]]) \
            * (train / a["train_size_mtpa"]) ** (n - 1) * (1 + _tri(rng, dg))
        totals.append(unit * cfg["capacity_mtpa"])
    s = sorted(totals)
    res = {"runs": runs, "seed": seed, "n_analogs": len(adj["kept"]), "n_excluded": len(adj["excluded"]),
           "central": {"median_total_musd": adj["median_total_musd"], "mean_total_musd": adj["mean_total_musd"], "median_unit_musd_per_mtpa": adj["median_unit"]},
           "total_musd": {"mean": sum(totals) / runs, **{f"P{p}": pct(s, p) for p in (10, 50, 80, 90)}},
           "unit_musd_per_mtpa": {f"P{p}": pct(s, p) / cfg["capacity_mtpa"] for p in (10, 50, 80, 90)},
           "contingency_P80_over_central_median": pct(s, 80) - adj["median_total_musd"],
           "analogs": adj["kept"], "excluded": adj["excluded"]}
    notes = ["screening number, AACE Class 5 style: not a budget and not for an investment decision",
             "published costs are mostly FID budgets or reported outturns with differing scope; read each source_url",
             "the cost index, location factors and site-type factors are the largest judgments: change them and look at the sensitivity"]
    lo, hi = pct(s, 10) / pct(s, 50) - 1, pct(s, 90) / pct(s, 50) - 1
    if lo > CLASS5_TYPICAL[0] / 1.5 or hi < CLASS5_TYPICAL[1] / 1.5:
        notes.append(f"P10-P90 spread ({100 * lo:.0f}% / +{100 * hi:.0f}%) is narrower than typical Class 5 ranges ({100 * CLASS5_TYPICAL[0]:.0f}% / +{100 * CLASS5_TYPICAL[1]:.0f}% at the extremes): the inputs may be too tight or the analog set too small")
    if len(adj["kept"]) < 5:
        notes.append(f"only {len(adj['kept'])} analogs after filters: the spread is not reliable")
    if not cfg.get("location_factor_range"):
        notes.append("no location_factor_range: the target location uncertainty is not in the range")
    if "cost_index" in cfg and not isinstance(er, dict):
        notes.append("cost_index is applied as a fixed path: no escalation uncertainty in the range")
    res["notes"] = notes
    if "compare_total_musd" in cfg:
        c = cfg["compare_total_musd"]
        res["compare"] = {"value_musd": c, "percentile_in_distribution": 100.0 * sum(1 for x in s if x <= c) / runs,
                          "unit_musd_per_mtpa": c / cfg["capacity_mtpa"],
                          "ratio_to_median": c / adj["median_total_musd"]}
    return res


def daily_margin(capacity_mtpa: float, margin_usd_per_mmbtu: float, mmbtu_per_tonne: float, operating_days_per_year: float) -> float:
    """Margin per operating day (USD million) for shutdown_risk's `opportunity.margin_per_day`: tonnes per day x MMBtu per tonne x margin.
    mmbtu_per_tonne depends on composition (the notebook this was checked against uses 52); no default is assumed here."""
    for v in (capacity_mtpa, margin_usd_per_mmbtu, mmbtu_per_tonne, operating_days_per_year):
        if v <= 0 or not math.isfinite(v):
            raise ValueError("all arguments must be positive")
    return capacity_mtpa * 1e6 / operating_days_per_year * mmbtu_per_tonne * margin_usd_per_mmbtu / 1e6


def safety_spend_ratio(recommendations_capex_musd: float, plant_capex_musd: float) -> float:
    """Share of the plant capex that a set of safety modifications represents (a sanity check, not a design basis)."""
    if plant_capex_musd <= 0:
        raise ValueError("plant capex must be positive")
    return recommendations_capex_musd / plant_capex_musd

"""Actuarial view of how safety-study outcomes (derogations, compensating measures, better-documented risk) change the insurance cost of a project.

Method: exposure rating from scenarios, not from claims history (a project has none; see `credibility`). Each scenario has a frequency per
year and a loss (physical damage plus business interruption days x value per day). For a policy with a deductible and a limit:

    layer loss of a scenario   = min(max(L - deductible, 0), limit)
    layer expected loss  EL    = sum f x layer loss                       (events as a compound Poisson process)
    variance of annual layer loss = sum f x layer loss^2                  -> SD
    parameter uncertainty: frequencies are best-estimate medians with a lognormal error factor EF = P95/P50; the mean is then higher than
        the median by m = exp(sigma^2 / 2), sigma = ln(EF) / 1.645. A study that narrows the error factor lowers m.
    technical premium = (EL x m + k x SD) / (1 - expense ratio)           (standard-deviation principle; k is the risk-load multiple)
    retained loss = ground-up expected loss x m - layer EL x m            (the deductible and anything above the limit stay with the owner)

Cases are compared with the first one (`baseline`). A scenario can carry, per case, a barrier PFD (frequency scales as PFD_case / PFD_baseline,
so a derogated trip or a compensating measure moves the frequency through its integrity) and a loss factor (for example larger damage
when separation distance is derogated). The present value of the premium difference over the horizon is compared with the cost of the
compensating measures. Everything is an input: the toolkit ships no market rates, loadings, deductibles or loss data, and a modelled premium
is not a quotation. Insurers also price on risk-engineering grades, policy conditions and capacity, which are not modelled; whether a
departure from a legal or policy requirement affects cover depends on the policy wording, which only you and the insurer can read.
"""
from __future__ import annotations

import math

Z95 = 1.645


def lognormal_mean_factor(error_factor: float) -> float:
    """m = exp(sigma^2/2) for a lognormal with P95/P50 = error_factor (1 means no parameter uncertainty)."""
    if error_factor < 1:
        raise ValueError("error factor is P95/P50 and cannot be below 1")
    sigma = math.log(error_factor) / Z95
    return math.exp(sigma * sigma / 2)


def layer_loss(loss: float, deductible: float, limit: float) -> float:
    return min(max(loss - deductible, 0.0), limit)


def credibility(n_claim_years: float, k: float = 10.0) -> float:
    """Buhlmann-type credibility weight Z = n / (n + k) given to the project's own claims experience (k is a judgement: larger for noisier losses)."""
    if n_claim_years < 0 or k <= 0:
        raise ValueError("years must be >= 0 and k > 0")
    return n_claim_years / (n_claim_years + k)


def blended_premium(experience: float, exposure: float, n_claim_years: float, k: float = 10.0) -> float:
    z = credibility(n_claim_years, k)
    return z * experience + (1 - z) * exposure


def _case_scenarios(inp: dict, case: str, base: str) -> list[dict]:
    value_day = inp.get("value_per_day", 0.0)
    out = []
    for s in inp["scenarios"]:
        for k in ("name", "freq_per_yr"):
            if k not in s:
                raise ValueError(f"scenario missing '{k}'")
        f = s["freq_per_yr"]
        pfd = s.get("pfd") or {}
        if case in pfd and base in pfd:
            if pfd[base] <= 0 or pfd[case] <= 0:
                raise ValueError(f"{s['name']}: PFD must be positive")
            f *= pfd[case] / pfd[base]
        loss = s.get("pd_loss", 0.0) + s.get("bi_days", 0.0) * value_day
        loss *= (s.get("loss_factor") or {}).get(case, 1.0)
        if f < 0 or loss < 0:
            raise ValueError(f"{s['name']}: negative frequency or loss")
        out.append({"name": s["name"], "freq": f, "loss": loss})
    return out


def evaluate_case(inp: dict, case: str, base: str) -> dict:
    prog, pr = inp["programme"], inp["pricing"]
    ded, lim = prog.get("deductible", 0.0), prog["limit"]
    sc = _case_scenarios(inp, case, base)
    m = lognormal_mean_factor((inp.get("error_factor") or {}).get(case, 1.0))
    ground = sum(s["freq"] * s["loss"] for s in sc)
    el = sum(s["freq"] * layer_loss(s["loss"], ded, lim) for s in sc)
    var = sum(s["freq"] * layer_loss(s["loss"], ded, lim) ** 2 for s in sc)
    sd = math.sqrt(var)
    prem = (el * m + pr["risk_load_k"] * sd) / (1 - pr["expense_ratio"])
    rp = inp.get("pml_return_period", 1000)
    pml_pool = [s["loss"] for s in sc if s["freq"] >= 1.0 / rp]
    return {"case": case, "ground_up_expected_loss": ground * m, "layer_expected_loss": el * m, "retained_expected_loss": (ground - el) * m,
            "layer_sd": sd, "mean_factor_from_uncertainty": m, "technical_premium": prem,
            "pml_at_return_period": {"return_period_years": rp, "loss": max(pml_pool) if pml_pool else 0.0},
            "scenario_frequencies": {s["name"]: s["freq"] for s in sc}}


def evaluate(inp: dict) -> dict:
    for k in ("programme", "pricing", "scenarios"):
        if k not in inp:
            raise ValueError(f"input needs '{k}'")
    if not inp["scenarios"]:
        raise ValueError("input needs at least one scenario")
    pr = inp["pricing"]
    if not 0 <= pr.get("expense_ratio", -1) < 0.9 or pr.get("risk_load_k", -1) < 0:
        raise ValueError("pricing needs expense_ratio in [0, 0.9) and risk_load_k >= 0")
    if inp["programme"].get("limit", 0) <= 0 or inp["programme"].get("deductible", 0) < 0:
        raise ValueError("programme needs limit > 0 and deductible >= 0")
    cases = list(inp.get("cases") or ["baseline"])
    base = cases[0]
    res = [evaluate_case(inp, c, base) for c in cases]
    b = res[0]["technical_premium"]
    for r in res:
        r["premium_change_vs_baseline"] = r["technical_premium"] - b
        r["premium_change_pct"] = round(100 * (r["technical_premium"] - b) / b, 2) if b else None
        r["retained_loss_change_vs_baseline"] = r["retained_expected_loss"] - res[0]["retained_expected_loss"]
    out = {"currency": inp.get("currency", ""), "baseline": base, "cases": res}
    years, rate = pr.get("years"), pr.get("discount_rate")
    if years and rate is not None and len(res) >= 3:
        af = sum(1 / (1 + rate) ** t for t in range(1, int(years) + 1))
        d, c = res[1], res[2]
        saving = d["technical_premium"] - c["technical_premium"]
        retained = d["retained_expected_loss"] - c["retained_expected_loss"]
        out["compensating_measures"] = {
            "from": d["case"], "to": c["case"], "annuity_factor": af,
            "pv_premium_saving": saving * af, "pv_retained_loss_saving": retained * af,
            "pv_total_saving": (saving + retained) * af, "measure_cost": inp.get("measure_cost"),
            "net_value": (saving + retained) * af - inp["measure_cost"] if inp.get("measure_cost") is not None else None}
    out["notes"] = ["A modelled premium is not a quotation: market capacity, risk-engineering grades and policy wording also set price and cover.",
                    "Retained loss (deductible and excess of limit) changes with the case even when the premium does not; it is the owner's cost.",
                    "Premium differences here come from the inputs you give; the toolkit contains no market rates or loss data."]
    return out

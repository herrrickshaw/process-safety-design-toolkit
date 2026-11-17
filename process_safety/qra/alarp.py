"""Step 5 - evaluation against tolerability criteria and the ALARP test.

Presets (checked against public sources on 2026-11-05; see SOURCES.md):
* uk_hse_r2p2 - HSE 'Reducing Risks, Protecting People' (2001): individual risk of death per year intolerable above 1e-3
  (workers) / 1e-4 (public), broadly acceptable below 1e-6. Societal: R2P2 treats >= 50 fatalities at more than 1 in 5000 per
  year (2e-4) as intolerable. The F-N lines here (intolerable F = 1e-2/N, broadly acceptable F = 1e-4/N, slope -1) are the
  IGEM rendering that passes through that R2P2 anchor point; R2P2 itself gives only the point.
* nl_bevi - Netherlands (Bevi): location-specific risk 1e-6 per year limit at vulnerable objects; societal-risk orientation
  (guide) value F = 1e-3/N^2 for N >= 10 per installation (a guide value, not a hard limit).
* custom  - pass your own dict with the same keys.
India: there is no single national number. OISD-STD-118, PNGRB T4S, MSIHC/EIA conditions and client standards each set their own
basis, which was not read for this toolkit; use 'custom' with the governing document's values.

ALARP cost-benefit (HSE-style): a measure is reasonably practicable unless its cost is grossly disproportionate to its benefit,
    benefit = delta PLL x VPF x years (optionally discounted),  cost = capex + opex x years (same discounting)
    implement if cost / benefit <= disproportion factor (DF; HSE practice ~ 1-10, rising with the risk level).
VPF (value of preventing a fatality) has no default: it is a policy input in the study currency.
"""
from __future__ import annotations

import math

PRESETS = {
    "uk_hse_r2p2": {
        "name": "UK HSE R2P2 (2001); F-N lines per IGEM through the R2P2 50-fatality anchor",
        "ir": {"worker": {"intolerable": 1e-3, "broadly_acceptable": 1e-6}, "public": {"intolerable": 1e-4, "broadly_acceptable": 1e-6}},
        "fn": {"intolerable": {"F1": 1e-2, "slope": 1.0, "n_min": 1}, "broadly_acceptable": {"F1": 1e-4, "slope": 1.0, "n_min": 1}},
    },
    "nl_bevi": {
        "name": "Netherlands Bevi: LSIR 1e-6 limit; societal guide value 1e-3/N^2 (N >= 10)",
        "ir": {"worker": {"intolerable": 1e-6, "broadly_acceptable": 1e-6}, "public": {"intolerable": 1e-6, "broadly_acceptable": 1e-6}},
        "fn": {"intolerable": {"F1": 1e-3, "slope": 2.0, "n_min": 10}},
    },
}


def get_criteria(spec) -> dict:
    if isinstance(spec, dict):
        return spec
    if spec not in PRESETS:
        raise KeyError(f"unknown criteria preset {spec!r}; choose {sorted(PRESETS)} or give a dict")
    return PRESETS[spec]


def classify_ir(value: float, group: str, criteria: dict) -> str:
    c = criteria["ir"][group]
    if value > c["intolerable"]:
        return "INTOLERABLE"
    if value > c["broadly_acceptable"]:
        return "TOLERABLE IF ALARP"
    return "BROADLY ACCEPTABLE"


def fn_line(n: float, line: dict) -> float:
    return line["F1"] / n ** line["slope"]


def classify_fn(curve: list[tuple[float, float]], criteria: dict) -> dict:
    """Worst ratio F(N)/F_line(N) for each criterion line, and the resulting region."""
    out = {}
    for name, line in criteria["fn"].items():
        pts = [(n, F, F / fn_line(n, line)) for n, F in curve if n >= line.get("n_min", 1) and F > 0]
        worst = max(pts, key=lambda t: t[2]) if pts else (None, 0.0, 0.0)
        out[name] = {"max_ratio": worst[2], "at_N": worst[0], "F_at_N": worst[1], "exceeded": worst[2] > 1}
    if out.get("intolerable", {}).get("exceeded"):
        region = "INTOLERABLE"
    elif "broadly_acceptable" in out and not out["broadly_acceptable"]["exceeded"]:
        region = "BROADLY ACCEPTABLE"
    elif "broadly_acceptable" in out:
        region = "TOLERABLE IF ALARP"
    else:
        region = "BELOW GUIDE VALUE"
    out["region"] = region
    return out


def present_value_factor(years: float, rate: float) -> float:
    return years if rate == 0 else (1 - (1 + rate) ** -years) / rate


def cost_benefit(delta_pll: float, capex: float, opex_per_yr: float, vpf: float, years: float, df: float, rate: float = 0.0) -> dict:
    pv = present_value_factor(years, rate)
    benefit = delta_pll * vpf * pv
    cost = capex + opex_per_yr * pv
    ratio = cost / benefit if benefit > 0 else math.inf
    icaf = cost / (delta_pll * years) if delta_pll > 0 else math.inf  # implied cost of averting a fatality (undiscounted lives)
    return {"benefit": benefit, "cost": cost, "cost_benefit_ratio": ratio, "ICAF": icaf, "disproportion_factor": df,
            "decision": "IMPLEMENT (cost not grossly disproportionate)" if ratio <= df else "NOT REASONABLY PRACTICABLE on CBA alone"}

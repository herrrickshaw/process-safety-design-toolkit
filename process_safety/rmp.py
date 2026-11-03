"""US EPA Risk Management Program (40 CFR Part 68) screening: substance applicability and offsite-consequence worst-case criteria.

VERIFIED from the primary text (Cornell LII copy of the eCFR, fetched 2026-11-03): 68.115 (1% by weight mixture rule, exemptions),
68.130 Tables 1 and 3 (77 toxics and 63 flammables with threshold quantities, parsed into data/epa_rmp_substances.json) with the Appendix A toxic
endpoints (mg/L), 68.22 (endpoints: 1 psi overpressure, 5 kW/m2 for 40 s, LFL; wind 1.5 m/s and stability F; 25 C and 50% humidity;
ground-level release), 68.25 (gases released over 10 minutes; 1 cm pool depth unless contained; flammable vapour-cloud explosion
with a 10% yield factor).

Distance calculations here use this package's NEUTRAL-GAS Gaussian screening and a TNT-equivalent blast curve. EPA requires dense-gas
treatment for heavier-than-air toxics (68.22(f)). At the worst-case conditions (1.5 m/s, F stability) a steady Gaussian plume is outside
its validity: it ignores dense-gas slumping and treats a 10-minute release as a continuous plume, so it can badly OVER- or UNDER-predict
(chlorine screening distances come out tens of km). Use the toxic-distance output only as an order-of-magnitude flag, never for a filing
(use EPA's RMP*Comp / ALOHA or a validated dense-gas model). The flammable 1 psi explosion distance (TNT-equivalent) is more robust.
"""
from __future__ import annotations

import json
from importlib import resources

from . import dispersion, explosion

LB_PER_KG = 2.2046226218
ENDPOINT_OVERPRESSURE_KPA = 6.894757  # 1 psi
ENDPOINT_RADIANT_KW_M2 = 5.0
ENDPOINT_RADIANT_SECONDS = 40
WORST_CASE_WIND_M_S = 1.5
WORST_CASE_STABILITY = "F"
RELEASE_DURATION_S = 600.0  # gases released over 10 minutes
POOL_DEPTH_M = 0.01
EXPLOSION_YIELD = 0.10


def _data() -> dict:
    return json.loads(resources.files("process_safety").joinpath("data/epa_rmp_substances.json").read_text())


def _norm(name: str) -> str:
    import re
    return re.sub(r"\s*\[.*?\]", "", name).strip().lower()


def find(name_or_cas: str) -> dict | None:
    """Look up by CAS number, then exact name, then name prefix, then substring (names normalised without [synonym] parts).
    Ambiguous partial names return the first hit: pass a CAS number to be unambiguous."""
    q = _norm(name_or_cas)
    d = _data()
    rows = [({**r, "kind": kind[:-1]}) for kind in ("toxics", "flammables") for r in d[kind]]
    for test in (lambda r: r["cas"] == name_or_cas.strip(), lambda r: _norm(r["name"]) == q,
                 lambda r: _norm(r["name"]).startswith(q), lambda r: q in _norm(r["name"])):
        for r in rows:
            if test(r):
                return r
    return None


def threshold_check(name_or_cas: str, quantity_kg: float, weight_fraction: float = 1.0) -> dict:
    """68.115: a threshold quantity is present if the total in a process EXCEEDS it. A substance below 1% by weight in a mixture need not be
    counted (toxics may be counted at the substance's weight; flammable mixtures count the ENTIRE mixture weight if >= 1% and the mixture
    meets the flammability criteria: the mixture rule is simplified here, read 68.115(b)). Exemptions (gasoline in distribution, naturally
    occurring hydrocarbons before a refining unit, retail fuel, articles, laboratories...) are NOT evaluated."""
    r = find(name_or_cas)
    if r is None:
        return {"found": False}
    if weight_fraction < 0.01:
        return {"found": True, "name": r["name"], "covered": False, "reason": "below 1% by weight in a mixture (68.115(b))"}
    tq_kg = r["tq_lb"] / LB_PER_KG
    counted = quantity_kg * (weight_fraction if r["kind"] == "toxic" else 1.0)
    return {"found": True, "name": r["name"], "kind": r["kind"], "threshold_lb": r["tq_lb"], "threshold_kg": tq_kg,
            "quantity_counted_kg": counted, "covered": counted > tq_kg}


def worst_case_toxic_gas(name: str, quantity_kg: float) -> dict:
    """Gas (or liquefied under pressure) released over 10 min at ground level, 1.5 m/s, F stability; distance to the Appendix A endpoint
    from the neutral-gas Gaussian screening (order-of-magnitude flag only; see the module docstring)."""
    r = find(name)
    if r is None or r["kind"] != "toxic":
        raise KeyError(f"{name!r} is not an RMP toxic substance in the parsed table")
    rate_g_s = quantity_kg * 1000 / RELEASE_DURATION_S
    end_g_m3 = r["toxic_endpoint_mg_L"]  # mg/L == g/m3
    dist = dispersion.distance_to_threshold_m(rate_g_s, WORST_CASE_WIND_M_S, 0.0, end_g_m3, WORST_CASE_STABILITY, x_max=200000.0)
    return {"substance": r["name"], "release_rate_kg_s": rate_g_s / 1000, "endpoint_mg_L": end_g_m3, "screening_distance_m_neutral_gas": dist,
            "beyond_model_range": dist is not None and dist > 50000,
            "warning": "neutral-gas Gaussian screening is outside its validity at 1.5 m/s F-stability and ignores dense-gas behaviour (EPA 68.22(f)): order-of-magnitude flag only; use RMP*Comp/ALOHA or a dense-gas model"}


def worst_case_flammable_vce(quantity_kg: float, heat_of_combustion_MJ_kg: float, yield_fraction: float = EXPLOSION_YIELD) -> dict:
    """68.25(e): total quantity in the vapour cloud explosion, 10% yield (TNT-equivalent method); distance to 1 psi overpressure."""
    w = explosion.tnt_equivalent_kg(quantity_kg, heat_of_combustion_MJ_kg, yield_fraction)
    return {"tnt_equivalent_kg": w, "distance_to_1psi_m": explosion.distance_for_overpressure_m(w, ENDPOINT_OVERPRESSURE_KPA)}


def pool_area_m2(volume_m3: float, contained_depth_m: float | None = None) -> float:
    """68.25: an uncontained liquid spreads to 1 cm deep; a contained one uses the contained surface area (here depth-based)."""
    return volume_m3 / (contained_depth_m if contained_depth_m else POOL_DEPTH_M)

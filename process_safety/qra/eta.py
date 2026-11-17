"""Step 2b - event tree analysis: LOC -> outcome probabilities (ignition, timing, explosion), with outcome effects from effects.py.

    LOC --ignited (Cox)--> immediate (immediate_fraction) --> jet fire [+ pool] | fireball (instantaneous) | pool fire (liquid)
                      \\                 --> delayed --> VCE (Cox explosion|ignition) [+ pool] | flash fire [+ pool] | late pool fire
                       \\--not ignited--> toxic cloud (if toxic component) | no lethal effect
Branch probabilities sum to 1 for every LOC (checked). P(VCE) = P(ign) x P(expl|ign) is capped at the delayed-ignition
probability, so a very small delayed share cannot make the flash-fire branch negative.
"""
from __future__ import annotations

from . import effects
from .frequency import cox_explosion_given_ignition, cox_ignition


def _composite(kind, *builders):
    def build(wx):
        parts = [b(wx) for b in builders]
        parts = [p for p in parts if p is not None]
        if not parts:
            return None
        return parts[0] if len(parts) == 1 else effects.Composite(parts, kind)
    return build


def branches(st: dict, section: dict, material: dict, conv: dict, ign: dict) -> list[dict]:
    """List of {"outcome", "prob", "build": f(weather) -> Effect|None, "weather_dependent": bool}. Probabilities sum to 1."""
    flammable = material.get("LFL_vol") is not None and material.get("Hc_MJ_kg") is not None
    has_toxic = bool(material.get("toxic"))
    cloud = st["airborne_fraction"] > 0
    rainout = st["phase"] != "gas" and (st["airborne_fraction"] < 1)
    jf = lambda wx: effects.jet_fire(st, material, conv)
    pf = lambda wx: effects.pool(st, section, material, conv)
    fb = lambda wx: effects.fireball_effect(st, material, conv)
    ff = lambda wx: effects.flash_fire(st, section, material, wx, conv)
    vx = lambda wx: effects.vce(st, section, material, wx, conv)
    tx = lambda wx: effects.toxic(st, section, material, wx, conv)
    out = []
    if not flammable:
        out.append({"outcome": "toxic" if has_toxic else "no_lethal_effect", "prob": 1.0, "build": tx if has_toxic else (lambda wx: None),
                    "weather_dependent": has_toxic})
        return out
    if "p_total" in ign:
        p_ign = ign["p_total"]
    else:
        p_ign = cox_ignition(st["rate_for_ignition_kg_s"], "gas" if cloud else "liquid") * ign.get("factor", 1.0)
    p_ign = min(1.0, max(0.0, p_ign))
    f_imm = ign["immediate_fraction"]
    p_imm, p_del = p_ign * f_imm, p_ign * (1 - f_imm)
    if st["instantaneous"] and cloud:
        out.append({"outcome": "fireball", "prob": p_imm, "build": fb, "weather_dependent": False})
    elif cloud:
        out.append({"outcome": "jet_fire" + ("+pool_fire" if rainout else ""), "prob": p_imm,
                    "build": _composite("jet_fire", jf, pf) if rainout else jf, "weather_dependent": False})
    else:
        out.append({"outcome": "pool_fire", "prob": p_imm, "build": pf, "weather_dependent": False})
    if cloud:
        p_vce = min(p_del, p_ign * cox_explosion_given_ignition(st["rate_for_ignition_kg_s"]) * ign.get("explosion_factor", 1.0))
        out.append({"outcome": "vce" + ("+pool_fire" if rainout else ""), "prob": p_vce,
                    "build": _composite("vce", vx, pf) if rainout else vx, "weather_dependent": True})
        out.append({"outcome": "flash_fire" + ("+pool_fire" if rainout else ""), "prob": p_del - p_vce,
                    "build": _composite("flash_fire", ff, pf) if rainout else ff, "weather_dependent": True})
    else:
        out.append({"outcome": "pool_fire_delayed", "prob": p_del, "build": pf, "weather_dependent": False})
    out.append({"outcome": "toxic" if has_toxic else "no_ignition", "prob": 1 - p_ign, "build": tx if has_toxic else (lambda wx: None),
                "weather_dependent": has_toxic})
    return [o for o in out if o["prob"] > 0]

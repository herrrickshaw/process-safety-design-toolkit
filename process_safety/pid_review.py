"""P&ID-register review: rules a drawing review would apply, run on the registers in a plant model (see `plant_model`).

Each finding says what was found, with the numbers, and which recommendation type (catalogue id) a study would raise. Rules:
    R1 no relief device on a closed-in vessel, column, exchanger, drum or reactor that has a design pressure
    R2 relief device discharging to atmosphere from a unit in flammable or toxic service
    R3 liquid-fed unit with no level measurement, or with level only in the control system (no independent trip registered)
    R4 trip using a single sensor (1oo1) on a unit that has a required SIL of 2 or more
    R5 unit in flammable or toxic service with no gas or fire detector registered
    R6 a line rated above the downstream unit's design pressure when that unit has no relief device
    R7 remote isolation: flammable inventory above a limit you give, with no shutdown valve registered
They are completeness and consistency checks on what the registers say, not a substitute for a drawing review.
"""
from __future__ import annotations

from .hmb import device_area, unit_hazards

CLOSED = ("vessel", "column", "exchanger", "drum", "reactor", "separator", "sphere", "bullet")


def _f(unit, rule, sev, msg, recs):
    return {"unit": unit, "rule": rule, "severity": sev, "message": msg, "rec_ids": recs}


def review(m: dict, isolation_inventory_kg: float | None = None) -> list[dict]:
    haz = unit_hazards(m)
    out = []
    for u in m["units"]:
        t, h = u["tag"], haz.get(u["tag"], {})
        area, devs = device_area(m, t)
        closed = str(u.get("type", "")).lower() in CLOSED
        if closed and u.get("design_P_kpag") is not None and not devs:
            out.append(_f(t, "R1", "gap", f"{t} ({u.get('type')}, design {u['design_P_kpag']:,.0f} kPag) has no relief device in the register", ["PSV-ADD"]))
        for d in devs:
            if str(d.get("outlet_to", "")).lower() == "atmosphere" and (h.get("flammable") or h.get("toxic")):
                kind = "flammable" if h.get("flammable") else "toxic"
                out.append(_f(t, "R2", "review", f"{d.get('tag')} on {t} discharges to atmosphere in {kind} service ({', '.join(h.get('listed', [])) or 'service flag'})", ["FLARE-LOAD"]))
        liq_in = [s for s in m["streams"] if s.get("to") == t and str(s.get("phase", "")).startswith("liq")]
        ins = [i for i in m["instruments"] if i.get("unit") == t]
        lev = [i for i in ins if str(i.get("type", "")).upper().startswith("L")]
        if liq_in and closed:
            if not lev:
                out.append(_f(t, "R3", "gap", f"{t} receives liquid but no level instrument is registered", ["HLL-SIF", "ALARM"]))
            elif not any(str(i.get("function", "")).lower() in ("trip", "sis") or str(i.get("loop", "")).upper() == "SIS" for i in lev):
                out.append(_f(t, "R3", "review", f"{t} receives liquid and level is measured only in the control system ({', '.join(i['tag'] for i in lev)}): no independent high-level trip registered", ["HLL-SIF"]))
        if (u.get("sil_required") or 0) >= 2:
            for i in ins:
                if str(i.get("voting", "")).lower() == "1oo1" and str(i.get("function", "")).lower() in ("trip", "sis"):
                    out.append(_f(t, "R4", "review", f"{i['tag']} is a single-sensor (1oo1) trip on {t}, which needs SIL {u['sil_required']}", ["SIF-UPGRADE"]))
        if (h.get("flammable") or h.get("toxic")) and not any(str(i.get("type", "")).upper().startswith(("AT", "GD", "FD", "UV", "AIT")) or str(i.get("loop", "")).upper() == "F&G" for i in m["instruments"] if i.get("unit") == t):
            out.append(_f(t, "R5", "review", f"{t} is in {'flammable' if h.get('flammable') else 'toxic'} service and no gas or fire detector is registered against it", ["DETECT"]))
        if isolation_inventory_kg and h.get("flammable") and (u.get("inventory_kg") or 0) > isolation_inventory_kg:
            if not any(str(v.get("type", "")).upper() in ("SDV", "ESD", "XV") for v in m["valves"] if v.get("unit") == t):
                out.append(_f(t, "R7", "review", f"{t} holds {u['inventory_kg']:,.0f} kg flammable (limit {isolation_inventory_kg:,.0f}) and no shutdown valve is registered", ["ISOLATION"]))
    units = {u["tag"]: u for u in m["units"]}
    for ln in m["lines"]:
        v = units.get(ln.get("to"))
        if v and ln.get("design_P_kpag") is not None and v.get("design_P_kpag") is not None and ln["design_P_kpag"] > v["design_P_kpag"] and not device_area(m, v["tag"])[1]:
            out.append(_f(v["tag"], "R6", "gap", f"line {ln.get('line_no')} is rated {ln['design_P_kpag']:,.0f} kPag but {v['tag']} is designed for {v['design_P_kpag']:,.0f} kPag and has no relief device", ["INTERFACE-DP"]))
    return out

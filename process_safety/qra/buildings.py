"""Occupied-building risk assessment (OBRA) and building radiation-impact assessment, run on a finished QRA.

For every QRA event (scenario x outcome x weather x wind ray, frequency f) the physical effect at each building is read from the
footprint (`Effect.field`): peak side-on overpressure, incident heat flux, flame engulfment, flammable-cloud entry.
A vulnerability model turns that into an occupant fatality probability v, and
    building individual risk (occupant, 100% present)  = sum f v
    building PLL                                       = occupants x occupancy x sum f v
    exceedance curves                                  = frequency that overpressure / flux at the building >= x

Default vulnerability ("purple_book"), as reproduced in DNV's Phast vulnerability theory note and US QRA filings:
    overpressure > 0.3 barg -> 1 ; 0.1-0.3 barg -> 0.025 (indoors) ; < 0.1 barg -> 0
    inside a flame / fireball or > 35 kW/m2 -> 1 ; inside a flash-fire cloud -> 1 ; otherwise 0 indoors (ASSUMED: the building
    shields occupants from lower fluxes - not verified against the Purple Book text, override per building)
Custom buildings give piecewise-linear curves: {"overpressure_kpa": [[P, v], ...], "flux_kW_m2": [[q, v], ...]} - e.g. derived
from API RP 752/753 building damage levels or a blast consultant's pressure-impulse assessment, which this module does NOT compute.
Blast loads use the TNT/Kinney-Graham field of the QRA (no impulse, no reflection, no confinement).
"""
from __future__ import annotations

import bisect
import csv
import html
import math

from . import risk
from .progress import Progress

PURPLE_BOOK = {"overpressure_kpa": [[0, 0], [9.999, 0], [10, 0.025], [29.999, 0.025], [30, 1.0]],
               "flux_kW_m2": [[0, 0], [34.999, 0], [35, 1.0]], "in_cloud": 1.0, "engulfed": 1.0}


def _interp(curve, x):
    xs = [c[0] for c in curve]
    if x <= xs[0]:
        return curve[0][1]
    if x >= xs[-1]:
        return curve[-1][1]
    i = bisect.bisect_right(xs, x) - 1
    (x0, y0), (x1, y1) = curve[i], curve[i + 1]
    return y0 + (y1 - y0) * (x - x0) / (x1 - x0)


def vulnerability(fld: dict, model: dict) -> float:
    v = 0.0
    if "overpressure_kpa" in fld and "overpressure_kpa" in model:
        v = max(v, _interp(model["overpressure_kpa"], fld["overpressure_kpa"]))
    if "flux_kW_m2" in fld and "flux_kW_m2" in model:
        v = max(v, _interp(model["flux_kW_m2"], fld["flux_kW_m2"]))
    if fld.get("in_cloud"):
        v = max(v, model.get("in_cloud", 1.0))
    if fld.get("engulfed"):
        v = max(v, model.get("engulfed", 1.0))
    return min(1.0, v)


def _local(b, s, toward):
    X, Y = b["x"] - s["x"], b["y"] - s["y"]
    if toward is None:
        return math.hypot(X, Y), 0.0
    t = math.radians(toward)
    return X * math.sin(t) + Y * math.cos(t), X * math.cos(t) - Y * math.sin(t)


def assess(out: dict, study: dict, buildings: list[dict] | None = None, progress=True) -> dict:
    """out = study.run(...) result. Buildings: [{name, x, y, occupants, occupancy (0-1), vulnerability: 'purple_book' | {...},
    target_ir_per_yr (optional), overpressure_levels_kpa, flux_levels_kW_m2}]"""
    from .study import conventions
    buildings = buildings or study.get("buildings", [])
    cache = out["results"]["effects"]
    sub = int(conventions(study)["sector_subdivisions"])

    def cb(s, o, w):
        return cache.get((s["id"], o["outcome"], w["name"] if w else None))
    total = risk.count_events(out["scenarios"], study["weather"], study["wind_rose"], sub, cb)
    prog = Progress(total, "building assessment", enabled=progress)
    acc = {}
    for b in buildings:
        acc[b["name"]] = {"ir": 0.0, "op_events": [], "flux_events": [], "contrib": {}, "worst": {"overpressure_kpa": 0.0, "flux_kW_m2": 0.0}}
    for s, o, w, toward, f, e in risk.enumerate_events(out["scenarios"], study["weather"], study["wind_rose"], cb, sub):
        for b in buildings:
            dx, dy = _local(b, s, toward)
            fld = e.field(dx, dy)
            if not fld:
                continue
            model = PURPLE_BOOK if b.get("vulnerability", "purple_book") == "purple_book" else b["vulnerability"]
            v = vulnerability(fld, model)
            a = acc[b["name"]]
            if v > 0:
                a["ir"] += f * v
                a["contrib"][s["id"]] = a["contrib"].get(s["id"], 0.0) + f * v
            if fld.get("overpressure_kpa"):
                a["op_events"].append((fld["overpressure_kpa"], f, s["id"], o["outcome"]))
                a["worst"]["overpressure_kpa"] = max(a["worst"]["overpressure_kpa"], fld["overpressure_kpa"])
            if fld.get("flux_kW_m2") or fld.get("engulfed"):
                q = fld.get("flux_kW_m2", 0.0)
                a["flux_events"].append((q, f, s["id"], o["outcome"]))
                a["worst"]["flux_kW_m2"] = max(a["worst"]["flux_kW_m2"], q)
        prog.update()
    prog.done()
    rows = []
    for b in buildings:
        a = acc[b["name"]]
        occ = b.get("occupancy", 1.0)
        op_lv = b.get("overpressure_levels_kpa", [3, 10, 30])
        fx_lv = b.get("flux_levels_kW_m2", [4, 12.5, 37.5])
        exc_p = {f"F(P>={x}kPa)": sum(f for P, f, *_ in a["op_events"] if P >= x) for x in op_lv}
        exc_q = {f"F(q>={x}kW/m2)": sum(f for q, f, *_ in a["flux_events"] if q >= x) for x in fx_lv}
        top = sorted(a["contrib"].items(), key=lambda kv: -kv[1])[:3]
        tgt = b.get("target_ir_per_yr")
        rows.append({"building": b["name"], "occupants": b.get("occupants", 0), "occupancy": occ, "IR_occupant_per_yr": a["ir"],
                     "IRPA_per_yr": a["ir"] * occ, "PLL_per_yr": a["ir"] * occ * b.get("occupants", 0),
                     "worst_overpressure_kpa": a["worst"]["overpressure_kpa"], "worst_flux_kW_m2": a["worst"]["flux_kW_m2"],
                     **exc_p, **exc_q, "top_contributors": "; ".join(f"{k} ({v:.1e})" for k, v in top),
                     "meets_target": "" if tgt is None else ("YES" if a["ir"] * occ <= tgt else "NO"),
                     "vulnerability": b.get("vulnerability", "purple_book") if isinstance(b.get("vulnerability", "purple_book"), str) else "custom"})
    curves = {b["name"]: {"overpressure": _exceedance(acc[b["name"]]["op_events"]), "flux": _exceedance(acc[b["name"]]["flux_events"])}
              for b in buildings}
    return {"buildings": rows, "exceedance_curves": curves, "events": total}


def _exceedance(events, n=40):
    if not events:
        return []
    mx = max(x for x, *_ in events)
    if mx <= 0:
        return []
    xs = [mx * 10 ** (-3 + 3 * i / (n - 1)) for i in range(n)]
    return [(x, sum(f for v, f, *_ in events if v >= x)) for x in xs]


def write(res: dict, prefix: str) -> list[str]:
    rows = res["buildings"]
    with open(prefix + "_buildings.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["building"])
        w.writeheader()
        w.writerows(rows)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(f'{v:.2e}' if isinstance(v, float) else str(v))}</td>" for v in r.values()) + "</tr>" for r in rows)
    head = "".join(f"<th>{html.escape(k)}</th>" for k in (rows[0] if rows else {}))
    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Occupied building risk</title><style>body{font-family:Helvetica,Arial;"
           "margin:20px;color:#1f2933}table{border-collapse:collapse;font-size:12px}th{background:#14284b;color:#fff;padding:5px}"
           "td{border-bottom:1px solid #e3e6ea;padding:4px}</style></head><body><h1 style='color:#14284b'>Occupied building risk and "
           f"building radiation impact</h1><p>{res['events']} QRA events evaluated at each building. Screening: TNT/Kinney-Graham blast "
           f"field, point-source fires; Purple Book discrete vulnerability unless a building curve is given.</p><table><tr>{head}</tr>{body}</table></body></html>")
    with open(prefix + "_buildings.html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    return [prefix + "_buildings.csv", prefix + "_buildings.html"]

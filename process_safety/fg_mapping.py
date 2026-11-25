"""Fire & gas (F&G) detector coverage mapping in 2D plan view (geographic coverage, ISA TR84.00.07 style), with obstruction
shadowing, voting coverage (>=1 and >=2 detectors) per zone, target checks, and a greedy placement optimiser.

Detector models (all parameters are inputs; vendor data / company F&G philosophy govern):
* point gas      - covers cells within `radius_m` (no default: commonly a few metres by company practice); gas reaches it around
                   obstacles, so line-of-sight blocking is off unless "line_of_sight": true
* open path gas  - covers cells within `width_m` of the beam segment between its two ends
* flame          - cone from (x, y) toward `azimuth_deg` with half-angle `fov_deg`/2 and `range_m` (for the fire size of the zone),
                   blocked by obstructions (polygons) along the line of sight
Zones are polygons with a grade, required voting ("1ooN" or "2ooN") and target coverage fraction (e.g. 0.6 / 0.8 / 0.9 by grade
in many F&G philosophies - set yours). Scenario coverage (release-rate / dispersion based) is NOT computed: this is geographic.

Run small first: map(..., cell=2.0) on a coarse grid, then refine; optimise() prints progress and ETA.
"""
from __future__ import annotations

import csv
import html
import math

from .qra.progress import Progress


def _seg_intersect(p1, p2, q1, q2) -> bool:
    def orient(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    d1, d2, d3, d4 = orient(q1, q2, p1), orient(q1, q2, p2), orient(p1, p2, q1), orient(p1, p2, q2)
    return (d1 * d2 < 0) and (d3 * d4 < 0)


def _blocked(a, b, obstructions) -> bool:
    for poly in obstructions:
        for q1, q2 in zip(poly, poly[1:] + poly[:1]):
            if _seg_intersect(a, b, q1, q2):
                return True
    return False


def _inside(pt, poly) -> bool:
    x, y = pt
    ins = False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            ins = not ins
    return ins


def _dist_seg(p, a, b) -> float:
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((p[0] - ax) * dx + (p[1] - ay) * dy) / L2))
    return math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)


def sees(det: dict, pt, obstructions) -> bool:
    k = det["kind"]
    if k == "point_gas":
        if math.hypot(pt[0] - det["x"], pt[1] - det["y"]) > det["radius_m"]:
            return False
        return not (det.get("line_of_sight", False) and _blocked((det["x"], det["y"]), pt, obstructions))
    if k == "open_path":
        return _dist_seg(pt, det["a"], det["b"]) <= det["width_m"]
    if k == "flame":
        dx, dy = pt[0] - det["x"], pt[1] - det["y"]
        r = math.hypot(dx, dy)
        if r > det["range_m"] or r == 0:
            return r == 0
        bearing = math.degrees(math.atan2(dx, dy)) % 360
        off = abs((bearing - det["azimuth_deg"] + 180) % 360 - 180)
        if off > det["fov_deg"] / 2:
            return False
        return not _blocked((det["x"], det["y"]), pt, obstructions)
    raise ValueError(f"unknown detector kind {k!r}")


def _cells(zone, cell):
    xs = [p[0] for p in zone["polygon"]]
    ys = [p[1] for p in zone["polygon"]]
    out = []
    x = min(xs) + cell / 2
    while x < max(xs):
        y = min(ys) + cell / 2
        while y < max(ys):
            if _inside((x, y), zone["polygon"]) and not any(_inside((x, y), ob) for ob in zone.get("_obs", [])):
                out.append((x, y))
            y += cell
        x += cell
    return out


def _required(zone):
    return int(zone.get("voting", "1ooN")[0])


def map_coverage(layout: dict, cell: float = 1.0, progress=False) -> dict:
    """layout = {"zones": [{name, polygon, grade, voting, target, detector_kinds}], "detectors": [...], "obstructions": [poly, ...]}"""
    obs = layout.get("obstructions", [])
    res = []
    prog = Progress(len(layout["zones"]), "F&G coverage", enabled=progress)
    for z in layout["zones"]:
        z = {**z, "_obs": obs}
        cells = _cells(z, cell)
        kinds = set(z.get("detector_kinds", ["point_gas", "open_path", "flame"]))
        dets = [d for d in layout["detectors"] if d["kind"] in kinds]
        counts = [sum(1 for d in dets if sees(d, c, obs)) for c in cells]
        n = max(len(cells), 1)
        c1 = sum(1 for v in counts if v >= 1) / n
        c2 = sum(1 for v in counts if v >= 2) / n
        req = _required(z)
        achieved = c1 if req == 1 else c2
        res.append({"zone": z["name"], "grade": z.get("grade", ""), "voting": z.get("voting", "1ooN"), "cells": len(cells),
                    "coverage_1": c1, "coverage_2": c2, "target": z.get("target"), "achieved": achieved,
                    "meets_target": None if z.get("target") is None else achieved >= z["target"], "_counts": counts, "_cells": cells})
        prog.update()
    prog.done()
    return {"zones": res, "cell_m": cell}


def optimise(layout: dict, zone_name: str, template: dict, candidates: list[tuple[float, float]], max_add: int = 10,
             cell: float = 1.0, progress=True) -> dict:
    """Greedy: repeatedly add the candidate detector (template + position) that most raises the zone's voting coverage,
    until the zone target is met or max_add detectors are added."""
    added = []
    lay = {**layout, "detectors": list(layout["detectors"])}
    zone = next(z for z in layout["zones"] if z["name"] == zone_name)
    target = zone.get("target", 1.0)
    prog = Progress(max_add * len(candidates), f"optimise {zone_name}"[:22], enabled=progress)
    cur = map_coverage({**lay, "zones": [zone]}, cell)["zones"][0]["achieved"]
    candidates = [c for c in candidates if not any(_inside(c, ob) for ob in layout.get("obstructions", []))]
    for _ in range(max_add):
        if cur >= target:
            break
        best, best_cov = None, cur
        for (x, y) in candidates:
            det = {**template, "x": x, "y": y}
            cov = map_coverage({**lay, "zones": [zone], "detectors": lay["detectors"] + [det]}, cell)["zones"][0]["achieved"]
            prog.update()
            if cov > best_cov + 1e-12:
                best, best_cov = det, cov
        if best is None:
            break
        lay["detectors"].append(best)
        added.append(best)
        cur = best_cov
    prog.done()
    return {"added": added, "coverage": cur, "target": target, "met": cur >= target, "layout": lay}


def svg(layout: dict, res: dict, W: int = 640) -> str:
    pts = [p for z in layout["zones"] for p in z["polygon"]]
    x0, x1 = min(p[0] for p in pts) - 5, max(p[0] for p in pts) + 5
    y0, y1 = min(p[1] for p in pts) - 5, max(p[1] for p in pts) + 5
    sc = W / (x1 - x0)
    H = (y1 - y0) * sc
    X = lambda x: (x - x0) * sc
    Y = lambda y: H - (y - y0) * sc
    cell = res["cell_m"] * sc
    s = [f'<svg viewBox="0 0 {W} {H + 18}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica" font-size="11"><rect width="{W}" height="{H}" fill="#fff"/>']
    cols = {0: "#e74c3c", 1: "#f5c242", 2: "#58b368"}
    for z in res["zones"]:
        for (cx, cy), n in zip(z["_cells"], z["_counts"]):
            s.append(f'<rect x="{X(cx) - cell / 2:.1f}" y="{Y(cy) - cell / 2:.1f}" width="{cell + .2:.1f}" height="{cell + .2:.1f}" fill="{cols[min(n, 2)]}" fill-opacity="0.7"/>')
    for z in layout["zones"]:
        s.append('<polygon points="' + " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in z["polygon"]) + '" fill="none" stroke="#14284b" stroke-width="1.5"/>')
    for ob in layout.get("obstructions", []):
        s.append('<polygon points="' + " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in ob) + '" fill="#555"/>')
    for d in layout["detectors"]:
        if d["kind"] == "open_path":
            s.append(f'<line x1="{X(d["a"][0]):.1f}" y1="{Y(d["a"][1]):.1f}" x2="{X(d["b"][0]):.1f}" y2="{Y(d["b"][1]):.1f}" stroke="#14284b" stroke-width="2"/>')
        else:
            s.append(f'<circle cx="{X(d["x"]):.1f}" cy="{Y(d["y"]):.1f}" r="4" fill="{"#c9a227" if d["kind"] == "flame" else "#14284b"}"/>')
    s.append(f'<text x="4" y="{H + 13}">red = no detector, yellow = 1, green = 2 or more; gold = flame detector, navy = gas</text></svg>')
    return "".join(s)


def report(layout: dict, res: dict, prefix: str) -> list[str]:
    rows = [{k: v for k, v in z.items() if not k.startswith("_")} for z in res["zones"]]
    with open(prefix + "_fg_coverage.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    trs = "".join(f"<tr><td>{html.escape(r['zone'])}</td><td>{r['grade']}</td><td>{r['voting']}</td><td>{100 * r['coverage_1']:.1f}%</td>"
                  f"<td>{100 * r['coverage_2']:.1f}%</td><td>{'' if r['target'] is None else format(100 * r['target'], '.0f') + '%'}</td>"
                  f"<td>{'' if r['meets_target'] is None else ('YES' if r['meets_target'] else 'NO')}</td></tr>" for r in rows)
    doc = (f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>F&amp;G mapping</title><style>body{{font-family:Helvetica;max-width:900px;"
           f"margin:20px auto}}table{{border-collapse:collapse;width:100%;font-size:12px}}th{{background:#14284b;color:#fff;padding:5px}}"
           f"td{{border-bottom:1px solid #ddd;padding:4px}}</style></head><body><h1 style='color:#14284b'>Fire &amp; gas geographic coverage</h1>"
           f"{svg(layout, res)}<table><tr><th>Zone</th><th>Grade</th><th>Voting</th><th>&#8805;1</th><th>&#8805;2</th><th>Target</th><th>Met</th></tr>{trs}</table></body></html>")
    with open(prefix + "_fg_coverage.html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    return [prefix + "_fg_coverage.csv", prefix + "_fg_coverage.html"]

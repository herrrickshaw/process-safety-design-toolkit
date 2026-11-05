"""Emergency planning outputs from a finished QRA: consequence-distance (MCLS) tables, emergency planning zones (EPZ) and an
ERDMP-style emergency level per scenario.

Thresholds (defaults = damage criteria tabulated in MoEF's EIA Technical Guidance Manual and widely used in Indian MCLS reports
and off-site emergency plans; set your own under study["emergency"]):
    heat flux        37.5 / 12.5 / 4.0 kW/m2           (Zone A / B / C)
    overpressure     0.3 / 0.1 / 0.03 bar  (30/10/3 kPa)  (heavy damage / repairable damage / glass breakage)
    flammable cloud  LFL footprint -> Zone A
    toxic            study-supplied ppm levels per zone (e.g. ERPG-3 / ERPG-2 / ERPG-1 or AEGL / IDLH - not defaulted)
Distances are maxima along the downwind centreline (fires and blasts are radial). Zones are drawn as circles around the release
point (conservative: any wind direction).

"Maximum credible loss scenario" (MCLS): the largest distance per threshold among outcomes whose frequency >= credible_cutoff
(default 1e-6 /yr - a study choice, not a regulatory value); the worst case ignores the cutoff.

Emergency level (configurable approximation of the PNGRB ERDMP Level 1/2/3 idea - verify against the regulation and your ERDMP):
    Level 3  Zone C reaches beyond the site boundary and touches public population or receptors (off-site / district help)
    Level 2  Zone B reaches beyond the unit (unit_radius_m) but stays on site (site-wide response, mutual aid)
    Level 1  otherwise (handled by the unit)
"""
from __future__ import annotations

import csv
import html
import math

DEFAULTS = {"flux_kW_m2": [37.5, 12.5, 4.0], "overpressure_kpa": [30.0, 10.0, 3.0], "credible_cutoff_per_yr": 1e-6, "unit_radius_m": 50.0}
ZONES = ["A", "B", "C"]


def distance_to(e, key: str, thr, r_max: float = 20000.0) -> float:
    """Farthest centreline distance (m) at which field[key] >= thr (or is True for boolean keys). Upwind for radial offsets too."""
    far, r = 0.0, 0.5
    while r < r_max:
        for dx in (r, -r) if getattr(e, "directional", False) else (r,):
            v = e.field(dx, 0.0).get(key)
            if v is not None and ((v is True) if isinstance(thr, bool) else (not isinstance(v, bool) and v >= thr)):
                far = max(far, r)
        if far and r > 4 * far + 100:
            break
        r *= 1.03
    return far


def _circle_inside(x, y, b):
    if b is None:
        return True
    if b.get("type", "circle") == "circle":
        return math.hypot(x - b["x"], y - b["y"]) <= b["r"]
    poly, inside = b["points"], False
    for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]):
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def _zone_leaves(sx, sy, R, b, n=72):
    return any(not _circle_inside(sx + R * math.cos(2 * math.pi * k / n), sy + R * math.sin(2 * math.pi * k / n), b) for k in range(n))


def assess(out: dict, study: dict) -> dict:
    cfg = {**DEFAULTS, **study.get("emergency", {})}
    cache = out["results"]["effects"]
    wx = {w["name"]: w for w in study["weather"]}
    tox = cfg.get("toxic_ppm", {})
    rows = []
    for s in out["scenarios"]:
        for o in s["branches"]:
            for wname in ([None] if not o["weather_dependent"] else list(wx)):
                e = cache.get((s["id"], o["outcome"], wname))
                if e is None:
                    continue
                f = s["frequency_per_yr"] * o["prob"] * (wx[wname]["p"] if wname else 1.0)
                d = {"scenario": s["id"], "section": s["section"], "outcome": o["outcome"], "weather": wname or "all", "frequency_per_yr": f}
                zone_r = [0.0, 0.0, 0.0]
                for k, thr in enumerate(cfg["flux_kW_m2"]):
                    v = distance_to(e, "flux_kW_m2", thr)
                    d[f"d_{thr}kW_m2"] = v
                    zone_r[k] = max(zone_r[k], v)
                for k, thr in enumerate(cfg["overpressure_kpa"]):
                    v = distance_to(e, "overpressure_kpa", thr)
                    d[f"d_{thr / 100:g}bar"] = v
                    zone_r[k] = max(zone_r[k], v)
                v = distance_to(e, "in_cloud", True)
                d["d_LFL"] = v
                zone_r[0] = max(zone_r[0], v)
                mat = study["materials"][s["material"]].get("toxic") or {}
                levels = tox.get(mat.get("component", ""), [])
                for k, thr in enumerate(levels[:3]):
                    v = distance_to(e, "conc_ppm", thr)
                    d[f"d_{thr}ppm"] = v
                    zone_r[k] = max(zone_r[k], v)
                for k, z in enumerate(ZONES):
                    d[f"zone_{z}_m"] = zone_r[k]
                rows.append(d)
    # enforce nesting A <= B <= C
    for d in rows:
        d["zone_B_m"] = max(d["zone_B_m"], d["zone_A_m"])
        d["zone_C_m"] = max(d["zone_C_m"], d["zone_B_m"])
    secs = {s["id"]: s for s in study["sections"]}
    people = [{**p, "kind": "population"} for p in study.get("population", [])] + [{**r, "kind": "receptor", "people": 0}
                                                                                     for r in study.get("receptors", [])]
    boundary = cfg.get("site_boundary")
    for d in rows:
        sec = secs[d["section"]]
        exposed = {z: [p["name"] for p in people if math.hypot(p["x"] - sec["x"], p["y"] - sec["y"]) <= d[f"zone_{z}_m"]] for z in ZONES}
        d.update({f"in_zone_{z}": "; ".join(exposed[z]) for z in ZONES})
        public_out = [p for p in people if math.hypot(p["x"] - sec["x"], p["y"] - sec["y"]) <= d["zone_C_m"] and not _circle_inside(p["x"], p["y"], boundary)]
        leaves_site = boundary is not None and _zone_leaves(sec["x"], sec["y"], d["zone_C_m"], boundary)
        if leaves_site and public_out:
            lvl = 3
        elif d["zone_B_m"] > sec.get("unit_radius_m", cfg["unit_radius_m"]):
            lvl = 2
        else:
            lvl = 1
        d["emergency_level"] = lvl
    allk = list(dict.fromkeys(k for d in rows for k in d))
    keys = [k for k in allk if k.startswith("d_") or k.startswith("zone_")]
    mcls = {}
    for k in keys:
        cred = [d for d in rows if d["frequency_per_yr"] >= cfg["credible_cutoff_per_yr"]]
        wc = max(rows, key=lambda d: d.get(k, 0.0)) if rows else None
        mc = max(cred, key=lambda d: d.get(k, 0.0)) if cred else None
        mcls[k] = {"worst_case_m": wc.get(k, 0.0) if wc else 0.0, "worst_case_scenario": f"{wc['scenario']} {wc['outcome']} {wc['weather']}" if wc else "",
                   "credible_m": mc.get(k, 0.0) if mc else 0.0, "credible_scenario": f"{mc['scenario']} {mc['outcome']} {mc['weather']}" if mc else ""}
    return {"rows": rows, "mcls": mcls, "config": cfg,
            "site_level": max((d["emergency_level"] for d in rows if d["frequency_per_yr"] >= cfg["credible_cutoff_per_yr"]), default=1)}


def write(res: dict, study: dict, prefix: str) -> list[str]:
    rows = res["rows"]
    with open(prefix + "_consequence_distances.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dict.fromkeys(k for d in rows for k in d)) or ["scenario"], restval="")
        w.writeheader()
        w.writerows(rows)
    with open(prefix + "_mcls.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh)
        w.writerow(["metric", "worst_case_m", "worst_case_scenario", "credible_m", "credible_scenario"])
        for k, v in res["mcls"].items():
            w.writerow([k, round(v["worst_case_m"], 1), v["worst_case_scenario"], round(v["credible_m"], 1), v["credible_scenario"]])
    # zone map: credible maximum zone per section
    secs = {s["id"]: s for s in study["sections"]}
    cut = res["config"]["credible_cutoff_per_yr"]
    zmax = {}
    for d in rows:
        if d["frequency_per_yr"] < cut:
            continue
        z = zmax.setdefault(d["section"], [0, 0, 0])
        for k, n in enumerate(ZONES):
            z[k] = max(z[k], d[f"zone_{n}_m"])
    pts = [(s["x"], s["y"]) for s in study["sections"]] + [(p["x"], p["y"]) for p in study.get("population", [])]
    R = max([max(v) for v in zmax.values()] + [100])
    x0, x1 = min(p[0] for p in pts) - R, max(p[0] for p in pts) + R
    y0, y1 = min(p[1] for p in pts) - R, max(p[1] for p in pts) + R
    W = 620
    sc = W / (x1 - x0)
    H = (y1 - y0) * sc
    X = lambda x: (x - x0) * sc
    Y = lambda y: H - (y - y0) * sc
    cols = ["#c0392b", "#e67e22", "#f1c40f"]
    svg = [f'<svg viewBox="0 0 {W} {H + 20}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica" font-size="11"><rect width="{W}" height="{H}" fill="#f7f8fa"/>']
    for sid, z in zmax.items():
        s = secs[sid]
        for k in (2, 1, 0):
            if z[k] > 0:
                svg.append(f'<circle cx="{X(s["x"]):.1f}" cy="{Y(s["y"]):.1f}" r="{z[k] * sc:.1f}" fill="{cols[k]}" fill-opacity="0.18" stroke="{cols[k]}"/>')
        svg.append(f'<rect x="{X(s["x"]) - 4:.1f}" y="{Y(s["y"]) - 4:.1f}" width="8" height="8" fill="#14284b"/><text x="{X(s["x"]) + 6:.1f}" y="{Y(s["y"]) - 6:.1f}">{sid}</text>')
    b = res["config"].get("site_boundary")
    if b and b.get("type", "circle") == "circle":
        svg.append(f'<circle cx="{X(b["x"]):.1f}" cy="{Y(b["y"]):.1f}" r="{b["r"] * sc:.1f}" fill="none" stroke="#14284b" stroke-dasharray="6,4"/>')
    elif b:
        svg.append('<polygon points="' + " ".join(f"{X(x):.1f},{Y(y):.1f}" for x, y in b["points"]) + '" fill="none" stroke="#14284b" stroke-dasharray="6,4"/>')
    for p in study.get("population", []):
        svg.append(f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="4" fill="none" stroke="#1f2933"/><text x="{X(p["x"]) + 6:.1f}" y="{Y(p["y"]) + 4:.1f}">{html.escape(p["name"])}</text>')
    svg.append(f'<text x="5" y="{H + 15}">Zone A (red) / B (orange) / C (yellow): credible-scenario maxima; dashed = site boundary</text></svg>')
    mrows = "".join(f"<tr><td>{k}</td><td>{v['worst_case_m']:.0f}</td><td>{html.escape(v['worst_case_scenario'])}</td><td>{v['credible_m']:.0f}</td>"
                    f"<td>{html.escape(v['credible_scenario'])}</td></tr>" for k, v in res["mcls"].items())
    lv = "".join(f"<tr><td>{html.escape(d['scenario'])}</td><td>{d['outcome']}</td><td>{d['weather']}</td><td>{d['frequency_per_yr']:.1e}</td>"
                 f"<td>{d['zone_A_m']:.0f}</td><td>{d['zone_B_m']:.0f}</td><td>{d['zone_C_m']:.0f}</td><td>{d['emergency_level']}</td>"
                 f"<td>{html.escape(d['in_zone_C'])}</td></tr>" for d in sorted(rows, key=lambda d: (-d["emergency_level"], -d["zone_C_m"]))[:40])
    doc = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>Emergency planning zones</title><style>body{font-family:Helvetica,Arial;"
           "max-width:1100px;margin:20px auto;color:#1f2933}table{border-collapse:collapse;width:100%;font-size:12px}th{background:#14284b;"
           "color:#fff;padding:5px;text-align:left}td{border-bottom:1px solid #e3e6ea;padding:4px}</style></head><body>"
           f"<h1 style='color:#14284b'>Consequence distances, MCLS and emergency planning zones</h1><p>Highest credible emergency level: "
           f"<b>Level {res['site_level']}</b> (credible cut-off {cut:.0e}/yr). Thresholds: {res['config']['flux_kW_m2']} kW/m2, "
           f"{[x / 100 for x in res['config']['overpressure_kpa']]} bar, LFL.</p>{''.join(svg)}"
           f"<h2>Maximum credible loss scenario (MCLS) distances</h2><table><tr><th>Metric</th><th>Worst case m</th><th>Scenario</th>"
           f"<th>Credible m</th><th>Scenario</th></tr>{mrows}</table><h2>Scenarios by emergency level (top 40)</h2><table><tr><th>Scenario</th>"
           f"<th>Outcome</th><th>Weather</th><th>Freq /yr</th><th>Zone A m</th><th>Zone B m</th><th>Zone C m</th><th>Level</th><th>In zone C</th></tr>{lv}</table></body></html>")
    with open(prefix + "_emergency.html", "w", encoding="utf-8") as fh:
        fh.write(doc)
    return [prefix + "_consequence_distances.csv", prefix + "_mcls.csv", prefix + "_emergency.html"]

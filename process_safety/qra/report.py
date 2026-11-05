"""Outputs: summary JSON, CSV tables, optional Excel workbook (openpyxl if installed), and a self-contained HTML report with an
LSIR contour-band map and F-N chart drawn as inline SVG (no plotting library needed)."""
from __future__ import annotations

import csv
import html
import json
import math
import os

from . import alarp, hazid
from .study import summary

NAVY, GOLD, INK, GREY = "#14284b", "#c9a227", "#1f2933", "#8a94a6"
BANDS = [(1e-3, "#7a0019"), (1e-4, "#c0392b"), (1e-5, "#e67e22"), (1e-6, "#f1c40f"), (1e-7, "#d5e8d4")]


def _fmt(v):
    return f"{v:.2e}" if isinstance(v, float) else v


def scenario_rows(out):
    res = out["results"]
    recs = [r["name"] for r in out["evaluation"]["receptors"]]
    rows = []
    for s in out["scenarios"]:
        st = s["source_term"]
        c = res["contributions"].get(s["id"], {"pll": 0.0, "receptor_ir": {}})
        row = {"id": s["id"], "section": s["section"], "equipment": s["equipment"], "hole": s["hole"], "hole_mm": round(s["hole_mm"], 1),
               "instantaneous": st["instantaneous"], "frequency_per_yr": s["frequency_per_yr"], "basis": s["basis"], "source": s["source"],
               "release_kg_s": round(st["rate_kg_s"], 2), "duration_s": round(st["duration_s"], 0), "mass_kg": round(st["mass_kg"], 0),
               "airborne_fraction": round(st["airborne_fraction"], 3),
               "outcomes": "; ".join(f"{b['outcome']}={b['prob']:.3g}" for b in s["branches"]), "PLL_per_yr": c["pll"]}
        for n in recs:
            row[f"LSIR@{n}"] = c["receptor_ir"].get(n, 0.0)
        rows.append(row)
    tot = res["pll"] or 1.0
    for r in rows:
        r["PLL_share_pct"] = round(100 * r["PLL_per_yr"] / tot, 2)
    return sorted(rows, key=lambda r: -r["PLL_per_yr"])


def _csv(path, rows, cols=None):
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=cols or list(rows[0]), extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def _svg_map(out, w=560):
    g = out["results"]["grid"]
    nx, ny = len(g.xs), len(g.ys)
    xs0, xs1, ys0, ys1 = g.xs[0], g.xs[-1], g.ys[0], g.ys[-1]
    sc = w / (xs1 - xs0 + g.step)
    h = (ys1 - ys0 + g.step) * sc
    X = lambda x: (x - xs0 + g.step / 2) * sc
    Y = lambda y: h - (y - ys0 + g.step / 2) * sc
    parts = [f'<svg viewBox="0 0 {w + 170} {h + 30}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="11">',
             f'<rect x="0" y="0" width="{w}" height="{h}" fill="#f7f8fa" stroke="{GREY}"/>']
    cell = g.step * sc
    for j in range(ny):
        for i in range(nx):
            v = g.ir[j][i]
            col = next((c for lv, c in BANDS if v >= lv), None)
            if col:
                parts.append(f'<rect x="{X(g.xs[i]) - cell / 2:.1f}" y="{Y(g.ys[j]) - cell / 2:.1f}" width="{cell + .3:.1f}" height="{cell + .3:.1f}" fill="{col}"/>')
    seen = set()
    for s in out["scenarios"]:
        if s["section"] in seen:
            continue
        seen.add(s["section"])
        parts.append(f'<rect x="{X(s["x"]) - 4}" y="{Y(s["y"]) - 4}" width="8" height="8" fill="{NAVY}"/>'
                     f'<text x="{X(s["x"]) + 6}" y="{Y(s["y"]) - 5}" fill="{NAVY}" font-weight="bold">{html.escape(s["section"])}</text>')
    for p in out.get("_population", []):
        parts.append(f'<circle cx="{X(p["x"]):.1f}" cy="{Y(p["y"]):.1f}" r="5" fill="none" stroke="{INK}" stroke-width="1.5"/>'
                     f'<text x="{X(p["x"]) + 7:.1f}" y="{Y(p["y"]) + 4:.1f}" fill="{INK}">{html.escape(p["name"])} ({p["people"]:g})</text>')
    for r in out["evaluation"]["receptors"]:
        parts.append(f'<path d="M{X(r["x"]):.1f},{Y(r["y"]) - 6:.1f} l5,9 h-10 z" fill="{GOLD}" stroke="{NAVY}"/>')
    lx = w + 12
    parts.append(f'<text x="{lx}" y="14" font-weight="bold" fill="{NAVY}">LSIR per year</text>')
    for k, (lv, col) in enumerate(BANDS):
        parts.append(f'<rect x="{lx}" y="{24 + 18 * k}" width="14" height="12" fill="{col}"/><text x="{lx + 20}" y="{34 + 18 * k}">&#8805; {lv:.0e}</text>')
    yb = 24 + 18 * len(BANDS) + 10
    parts.append(f'<rect x="{lx}" y="{yb}" width="10" height="10" fill="{NAVY}"/><text x="{lx + 20}" y="{yb + 9}">release section</text>'
                 f'<path d="M{lx + 5},{yb + 16} l5,9 h-10 z" fill="{GOLD}" stroke="{NAVY}"/><text x="{lx + 20}" y="{yb + 26}">IR receptor</text>'
                 f'<circle cx="{lx + 5}" cy="{yb + 38}" r="5" fill="none" stroke="{INK}"/><text x="{lx + 20}" y="{yb + 42}">population (people)</text>')
    bar = 100
    parts.append(f'<line x1="10" y1="{h + 15}" x2="{10 + bar * sc}" y2="{h + 15}" stroke="{INK}" stroke-width="2"/><text x="{14 + bar * sc}" y="{h + 19}">100 m</text>'
                 f'<text x="{w - 40}" y="{h + 19}">N &#8593;</text></svg>')
    return "".join(parts)


def _svg_fn(out, extra_curves=(), w=560, h=360):
    crit = out["evaluation"]["criteria"]
    curve = out["results"]["fn_curve"]
    L, B, R, T = 60, 40, 15, 15
    x0, x1, y0, y1 = 0, 4, -9, -1  # log10 N, log10 F
    X = lambda n: L + (math.log10(n) - x0) / (x1 - x0) * (w - L - R)
    Y = lambda f: T + (y1 - math.log10(f)) / (y1 - y0) * (h - T - B)
    p = [f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg" font-family="Helvetica,Arial" font-size="11">',
         f'<rect x="{L}" y="{T}" width="{w - L - R}" height="{h - T - B}" fill="#fbfbfc" stroke="{GREY}"/>']
    for e in range(x0, x1 + 1):
        p.append(f'<line x1="{X(10 ** e)}" y1="{T}" x2="{X(10 ** e)}" y2="{h - B}" stroke="#e3e6ea"/><text x="{X(10 ** e) - 8}" y="{h - B + 14}">{10 ** e}</text>')
    for e in range(y0, y1 + 1):
        p.append(f'<line x1="{L}" y1="{Y(10 ** e)}" x2="{w - R}" y2="{Y(10 ** e)}" stroke="#e3e6ea"/><text x="{L - 40}" y="{Y(10 ** e) + 4}">1e{e}</text>')
    p.append(f'<text x="{w / 2 - 70}" y="{h - 6}">N (fatalities, expected per event)</text>'
             f'<text transform="translate(14,{h / 2 + 50}) rotate(-90)">F (frequency of N or more, /yr)</text>')
    styles = {"intolerable": ("#c0392b", "6,0"), "broadly_acceptable": ("#27ae60", "6,4")}
    for name, line in crit["fn"].items():
        n_lo = max(1, line.get("n_min", 1))
        pts = [(n, alarp.fn_line(n, line)) for n in (n_lo, 10 ** x1)]
        col, dash = styles.get(name, (GREY, "2,2"))
        p.append(f'<polyline points="{" ".join(f"{X(n):.1f},{Y(max(f, 10 ** y0)):.1f}" for n, f in pts)}" fill="none" stroke="{col}" stroke-dasharray="{dash}" stroke-width="1.5"/>'
                 f'<text x="{X(pts[0][0]) + 4}" y="{Y(pts[0][1]) - 4}" fill="{col}">{name.replace("_", " ")}</text>')

    def step_path(c, col, width, dash="0"):
        c = [(n, f) for n, f in c if f > 0]
        if not c:
            return ""
        d = []
        for k, (n, f) in enumerate(c):
            n_next = c[k + 1][0] if k + 1 < len(c) else n * 1.25
            d.append(f"{X(n):.1f},{Y(max(f, 10 ** y0)):.1f} {X(min(n_next, 10 ** x1)):.1f},{Y(max(f, 10 ** y0)):.1f}")
        return f'<polyline points="{" ".join(d)}" fill="none" stroke="{col}" stroke-width="{width}" stroke-dasharray="{dash}"/>'
    p.append(step_path(curve, NAVY, 2.5))
    leg_y = T + 14
    p.append(f'<line x1="{w - 190}" y1="{leg_y}" x2="{w - 170}" y2="{leg_y}" stroke="{NAVY}" stroke-width="2.5"/><text x="{w - 165}" y="{leg_y + 4}">base case</text>')
    for k, (label, c) in enumerate(extra_curves):
        col = [GOLD, "#7f8c8d", "#8e44ad", "#16a085"][k % 4]
        p.append(step_path(c, col, 1.6, "5,3"))
        p.append(f'<line x1="{w - 190}" y1="{leg_y + 14 * (k + 1)}" x2="{w - 170}" y2="{leg_y + 14 * (k + 1)}" stroke="{col}" stroke-dasharray="5,3" stroke-width="1.6"/>'
                 f'<text x="{w - 165}" y="{leg_y + 4 + 14 * (k + 1)}">{html.escape(label[:28])}</text>')
    p.append("</svg>")
    return "".join(p)


def _table(rows, cols, fmt=None):
    fmt = fmt or {}
    head = "".join(f"<th>{html.escape(c)}</th>" for c in cols)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(fmt.get(c, _fmt)(r.get(c, ''))))}</td>" for c in cols) + "</tr>" for r in rows)
    return f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>"


def html_report(out: dict) -> str:
    sm = summary(out)
    ev = out["evaluation"]
    res = out["results"]
    rows = scenario_rows(out)
    soc = ev["societal"]
    reg_col = {"INTOLERABLE": "#c0392b", "TOLERABLE IF ALARP": "#e67e22", "BROADLY ACCEPTABLE": "#27ae60"}
    badge = lambda r: f'<span class="badge" style="background:{reg_col.get(r, GREY)}">{html.escape(r)}</span>'
    rec_rows = "".join(f"<tr><td>{html.escape(r['name'])}</td><td>{r['group']}</td><td>{r['LSIR_per_yr']:.2e}</td><td>{r['occupancy']:g}</td>"
                       f"<td>{r['IRPA_per_yr']:.2e}</td><td>{badge(r['region'])}</td></tr>" for r in ev["receptors"])
    mit_rows = "".join(
        f"<tr><td>{html.escape(m['name'])}</td><td>{m['pll_before']:.2e}</td><td>{m['pll_after']:.2e}</td><td>{m['delta_pll']:.2e}</td>"
        f"<td>{m['cba']['cost']:,.0f}</td><td>{m['cba']['benefit']:,.0f}</td><td>{m['cba']['cost_benefit_ratio']:.2f}</td>"
        f"<td>{m['cba']['ICAF']:,.3g}</td><td>{html.escape(m['cba']['decision'])}</td></tr>" for m in out["mitigation"])
    outc = "".join(f"<tr><td>{k}</td><td>{v['frequency_per_yr']:.2e}</td><td>{v['pll']:.2e}</td><td>{100 * v['pll'] / (res['pll'] or 1):.1f}%</td></tr>"
                   for k, v in sorted(res["by_outcome"].items(), key=lambda kv: -kv[1]["pll"]))
    fn_items = []
    for k, v in soc.items():
        if not isinstance(v, dict):
            continue
        at = f" at N = {v['at_N']:.3g}" if v["at_N"] else ""
        fn_items.append(f"<li>{k.replace('_', ' ')} line: worst F/F<sub>line</sub> = {v['max_ratio']:.2f}{at}{' (exceeded)' if v['exceeded'] else ''}</li>")
    fn_lines = "".join(fn_items)
    vi, vr = out["validation_inputs"], out["validation_results"]
    val = "".join(f'<li class="err">ERROR: {html.escape(m)}</li>' for m in vi["errors"] + vr["errors"]) + \
        "".join(f'<li class="warn">WARNING: {html.escape(m)}</li>' for m in vi["warnings"] + vr["warnings"]) + \
        "".join(f'<li class="ok">PASS: {html.escape(m)}</li>' for m in vi["passed"] + vr["passed"])
    proj = ""
    if "projection" in out:
        pj = out["projection"]
        proj = (f"<p class='note'>SAMPLE RUN: {pj['sample_events']} of {pj['full_events']} events on a coarser grid in {pj['sample_s']:.2f} s. "
                f"Projected full run: ~{pj['projected_full_base_s']:.1f} s base case, ~{pj['projected_full_with_mitigation_s']:.1f} s with all measures.</p>")
    extra = [(m["name"], m["fn_curve_after"]) for m in out["mitigation"]]
    conv = "".join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in out["conventions"].items())
    srcs = "".join(f"<li><b>{k}</b>: {html.escape(v)}</li>" for k, v in out["dataset_sources"].items())
    top = rows[:12]
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{html.escape(out['study'])} - QRA</title>
<style>body{{font-family:Helvetica,Arial,sans-serif;color:{INK};max-width:1100px;margin:24px auto;padding:0 16px;line-height:1.45}}
h1{{color:{NAVY};border-bottom:3px solid {GOLD};padding-bottom:6px}}h2{{color:{NAVY};margin-top:30px}}
table{{border-collapse:collapse;width:100%;font-size:12px;margin:8px 0}}th{{background:{NAVY};color:#fff;text-align:left;padding:5px}}
td{{border-bottom:1px solid #e3e6ea;padding:4px 5px}}.badge{{color:#fff;padding:2px 7px;border-radius:3px;font-size:11px}}
.kpi{{display:flex;gap:12px;flex-wrap:wrap}}.kpi div{{border-left:4px solid {GOLD};background:#f4f6f9;padding:8px 14px;min-width:150px}}
.kpi b{{display:block;font-size:20px;color:{NAVY}}}.note{{background:#fff8e1;border-left:4px solid {GOLD};padding:8px 12px;font-size:13px}}
li.err{{color:#c0392b}}li.warn{{color:#b9770e}}li.ok{{color:#1e8449}}ul{{font-size:13px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
@media(max-width:800px){{.grid2{{grid-template-columns:1fr}}}}</style></head><body>
<h1>{html.escape(out['study'])}</h1>
<p class="note"><b>Screening QRA.</b> Built with process-safety-design-toolkit (stdlib models). Neutral-gas dispersion, point-source fires, TNT
blast and generic frequencies: replace with validated tools (e.g. DNV Phast/Safeti) and site data before a decision. Criteria: {html.escape(ev['criteria']['name'])}.</p>
{proj}
<div class="kpi"><div>Max LSIR<b>{sm['max_LSIR_per_yr']:.2e}</b>/yr</div><div>PLL<b>{sm['PLL_per_yr']:.2e}</b>/yr</div>
<div>LOC scenarios<b>{sm['scenarios_run']}</b>of {sm['scenarios_total']}</div><div>Total LOC freq.<b>{sm['total_loc_frequency_per_yr']:.2e}</b>/yr</div>
<div>Societal<b style="font-size:14px">{badge(soc['region'])}</b></div></div>
<h2>1-4. Risk picture</h2><div class="grid2"><div><h3>Location-specific individual risk</h3>{_svg_map(out)}</div>
<div><h3>Societal risk (F-N)</h3>{_svg_fn(out, extra)}<ul>{fn_lines}</ul></div></div>
<h2>5. Evaluation against criteria</h2><table><thead><tr><th>Receptor</th><th>Group</th><th>LSIR /yr</th><th>Occupancy</th><th>IRPA /yr</th><th>Region</th></tr></thead><tbody>{rec_rows}</tbody></table>
<h3>Risk by outcome</h3><table><thead><tr><th>Outcome</th><th>Frequency /yr</th><th>PLL /yr</th><th>Share of PLL</th></tr></thead><tbody>{outc}</tbody></table>
<h3>Top scenarios by PLL</h3>{_table(top, ['id', 'frequency_per_yr', 'release_kg_s', 'duration_s', 'airborne_fraction', 'PLL_per_yr', 'PLL_share_pct', 'outcomes'])}
<h2>6. Mitigation and ALARP cost-benefit</h2>
<p style="font-size:13px">VPF = {out.get('_alarp', {}).get('vpf', 'n/a'):,} {html.escape(str(out.get('_alarp', {}).get('currency', '')))}; disproportion factor {out.get('_alarp', {}).get('disproportion_factor', '')}; {out.get('_alarp', {}).get('lifetime_yr', '')} years.
A measure is reasonably practicable unless cost / benefit exceeds the disproportion factor. CBA is one input: measures that are relevant good practice, or that move a receptor out of the intolerable region, are expected regardless.</p>
<table><thead><tr><th>Measure</th><th>PLL before</th><th>PLL after</th><th>&#916;PLL</th><th>Cost</th><th>Benefit</th><th>Cost/benefit</th><th>ICAF</th><th>Decision</th></tr></thead><tbody>{mit_rows or '<tr><td colspan=9>none defined</td></tr>'}</tbody></table>
<h2>Data consistency checks</h2><ul>{val}</ul>
<h2>Assumptions and conventions</h2><table><tbody>{conv}</tbody></table>
<h3>Frequency data sources</h3><ul>{srcs}</ul>
<p style="font-size:12px;color:{GREY}">Grid step {out['grid_used']['step']} m; {res['events']} events integrated; {res['effects_built']} footprints built; runtime {sm['runtime_s']} s.</p>
</body></html>"""


def write_all(out: dict, study: dict, outdir: str, xlsx: bool = True) -> dict:
    os.makedirs(outdir, exist_ok=True)
    out["_population"] = study.get("population", [])
    out["_alarp"] = study.get("alarp", {})
    files = {}
    sm = summary(out)
    p = os.path.join(outdir, "summary.json")
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(sm, fh, indent=2, default=str)
    files["summary"] = p
    rows = scenario_rows(out)
    _csv(os.path.join(outdir, "scenarios.csv"), rows)
    files["scenarios"] = os.path.join(outdir, "scenarios.csv")
    _csv(os.path.join(outdir, "receptors.csv"), out["evaluation"]["receptors"])
    _csv(os.path.join(outdir, "fn_curve.csv"), [{"N": n, "F_per_yr": f} for n, f in out["results"]["fn_curve"]])
    g = out["results"]["grid"]
    _csv(os.path.join(outdir, "lsir_grid.csv"), [{"x": g.xs[i], "y": g.ys[j], "LSIR_per_yr": g.ir[j][i]} for j in range(len(g.ys)) for i in range(len(g.xs)) if g.ir[j][i] > 0])
    mit = [{"measure": m["name"], "description": m["description"], "capex": m["capex"], "opex_per_yr": m["opex_per_yr"], "PLL_before": m["pll_before"],
            "PLL_after": m["pll_after"], "delta_PLL": m["delta_pll"], **{k: v for k, v in m["cba"].items()}} for m in out["mitigation"]]
    _csv(os.path.join(outdir, "mitigation.csv"), mit)
    hazid.write_csv(out["hazid"], os.path.join(outdir, "hazid_register.csv"), hazid.HAZID_COLUMNS)
    hazid.write_csv(out["hazop"], os.path.join(outdir, "hazop_worksheet.csv"))
    val = [{"stage": st, "level": lv, "message": m} for st, v in (("inputs", out["validation_inputs"]), ("results", out["validation_results"]))
           for lv in ("errors", "warnings", "passed") for m in v[lv]]
    _csv(os.path.join(outdir, "validation.csv"), val)
    p = os.path.join(outdir, "qra_report.html")
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(html_report(out))
    files["report"] = p
    if xlsx:
        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill
        except ImportError:
            xlsx = False
    if xlsx:
        wb = openpyxl.Workbook()
        sheets = [("Summary", [{"metric": k, "value": json.dumps(v, default=str) if isinstance(v, (list, dict)) else v} for k, v in sm.items()]),
                  ("Scenarios", rows), ("Receptors", out["evaluation"]["receptors"]),
                  ("FN curve", [{"N": n, "F_per_yr": f} for n, f in out["results"]["fn_curve"]]), ("Mitigation", mit),
                  ("Validation", val), ("HAZID", out["hazid"]), ("HAZOP", out["hazop"])]
        wb.remove(wb.active)
        hdr = PatternFill("solid", fgColor=NAVY[1:])
        for name, data in sheets:
            ws = wb.create_sheet(name)
            if not data:
                continue
            cols = list(data[0])
            ws.append(cols)
            for c in ws[1]:
                c.font, c.fill = Font(bold=True, color="FFFFFF"), hdr
            for r in data:
                ws.append([r.get(c) if not isinstance(r.get(c), (list, dict, tuple)) else json.dumps(r.get(c), default=str) for c in cols])
            for k, c in enumerate(cols, 1):
                ws.column_dimensions[openpyxl.utils.get_column_letter(k)].width = min(48, max(10, len(str(c)) + 2))
            ws.freeze_panes = "A2"
        p = os.path.join(outdir, "qra_results.xlsx")
        wb.save(p)
        files["xlsx"] = p
    return files

"""Reports for `hmb_audit.audit`: an Excel workbook, a findings CSV and a self-contained visual HTML page (inline SVG, no scripts).

HTML layout: each section is headed by a sentence stating what the data shows (the assertion-evidence slide idea), with the
evidence under it: verdict tiles, a mass-flow Sankey, closure bars against the tolerance band, a check-coverage grid, a
design-versus-model deviation heatmap, then the full findings table. Status is always icon plus word, never colour alone.
"""
from __future__ import annotations

from html import escape

from . import pha
from .hmb_audit import FAIL, NC, PASS, REVIEW
from .xlsx_write import write_xlsx

LABEL = {PASS: "PASS", FAIL: "FAIL", NC: "NOT CHECKED", REVIEW: "REVIEW"}
ICON = {PASS: "&#10003;", FAIL: "&#10007;", NC: "?", REVIEW: "!"}
KINDS = ("mass", "component", "energy")


# ---- workbook ---------------------------------------------------------------------------------------------------
def hmb_table(r: dict) -> list[list]:
    """The compiled HMB: one column per stream, as engineering stream tables are laid out."""
    S = r["streams"]
    link = {x["stream"]: x for x in r["links"]}

    def row(label, fn):
        return [label] + [fn(s) for s in S]

    rows = [row("Stream", lambda s: str(s["id"])), row("From", lambda s: s.get("from")), row("To", lambda s: s.get("to")),
            row("Phase", lambda s: s.get("phase")), row("Temperature (degC)", lambda s: s.get("T_C")),
            row("Pressure (kPag)", lambda s: s.get("P_kpag")), row("Mass flow (kg/h)", lambda s: s.get("mass_kg_h")),
            row("Enthalpy flow (kW)", lambda s: s.get("H_kW")),
            row("P&ID line", lambda s: link[s["id"]]["line_no"]), row("P&ID link check", lambda s: LABEL[link[s["id"]]["status"]]),
            row("P&ID tags on line", lambda s: ", ".join(link[s["id"]]["line_tags"])),
            row("Composition basis", lambda s: (s.get("component_basis") or r["component_basis"] or "NOT DECLARED") if s.get("components") else None)]
    names = list(dict.fromkeys(c for s in S for c in (s.get("components") or {})))
    for c in names:
        rows.append(row(f"Fraction {c}", lambda s: (s.get("components") or {}).get(c)))
    rows.append(row("Source of row data", lambda s: s.get("source")))
    return rows


def sheets(r: dict) -> list[tuple[str, list[list]]]:
    summary = [["Item", "Value"], ["Plant", r["name"]], ["Verdict", LABEL[r["verdict"]]],
               ["Findings: fail", r["counts"][FAIL]], ["Findings: not checked", r["counts"][NC]], ["Findings: review", r["counts"][REVIEW]],
               ["Enthalpy basis", r["enthalpy_basis"] or "NOT DECLARED"], ["Composition basis", r["component_basis"] or "NOT DECLARED"],
               ["Limits of this audit", r["limits"]]]
    summary += [[f"Tolerance {k} (judgment default unless overridden)", v] for k, v in r["tolerances"].items()]
    summary += [["Note", n] for n in r["notes"]]
    bal = [["Unit", "Reactive", "Mass", "Mass in kg/h", "Mass out kg/h", "Mass residual kg/h", "Mass residual fraction", "Mass note",
            "Component", "Component note", "Energy", "H in kW", "Duty kW", "Work kW", "H out kW", "Energy residual kW", "Energy limit kW", "Energy note"]]
    comp = [["Unit", "Component", "In kg/h", "Generation kg/h", "Out kg/h", "Residual kg/h", "Limit kg/h", "Check"]]
    for u in r["units"] + [r["overall"]]:
        m, c, e = (u[k] for k in KINDS)
        bal.append([u["unit"], "yes" if u["reactive"] else "no", LABEL[m["status"]], m.get("in_kg_h"), m.get("out_kg_h"), m.get("residual_kg_h"),
                    m.get("residual_rel"), m["reason"], LABEL[c["status"]], c["reason"], LABEL[e["status"]], e.get("H_in_kW"), e.get("duty_kW"),
                    e.get("work_kW"), e.get("H_out_kW"), e.get("residual_kW"), e.get("limit_kW"), e["reason"]])
        comp += [[u["unit"], x["component"], x["in_kg_h"], x["generation_kg_h"], x["out_kg_h"], x["residual_kg_h"], x["limit_kg_h"],
                  LABEL[x["status"]]] for x in c["components"]]
    links = [["Stream", "P&ID line", "Matched by", "Check", "Note", "Tags on line"]]
    links += [[x["stream"], x["line_no"], x["method"], LABEL[x["status"]], x["reason"], ", ".join(x["line_tags"])] for x in r["links"]]
    equip = [["Unit", "Type", "Instruments", "Valves", "Relief devices"]]
    equip += [[x["unit"], x["type"], ", ".join(x["instruments"]), ", ".join(x["valves"]), ", ".join(x["relief_devices"])] for x in r["equipment"]]
    cmp_ = [["Stream", "Property", "Design", "Model", "Model minus design", "Limit", "Difference / limit", "Check"]]
    cmp_ += [[x["stream"], x["property"], x["design"], x["model"], x["difference"], x["limit"], x["ratio"], LABEL[x["status"]]] for x in r["comparison"]]
    find = [["Check", "Area", "Item", "Finding"]] + [[LABEL[f["status"]], f["area"], f["item"], f["message"]] for f in r["findings"]]
    return [("Summary", summary), ("HMB", hmb_table(r)), ("Balances", bal), ("Component balances", comp), ("P&ID links", links),
            ("Equipment tags", equip), ("Design vs model", cmp_), ("Findings", find)]


# ---- visual page ------------------------------------------------------------------------------------------------
def _chip(status: str, extra: str = "") -> str:
    return f'<span class="chip {status}">{ICON[status]} {LABEL[status]}{extra}</span>'


def _layers(nodes: list, edges: list) -> tuple[dict, set]:
    """Longest-path layering; edges that close a loop (found by depth-first search) are returned as recycle indices."""
    out = {n: [] for n in nodes}
    for i, (a, b, _) in enumerate(edges):
        out[a].append((i, b))
    state, back, order = {}, set(), []
    indeg = {n: 0 for n in nodes}
    for _, b, _s in edges:
        indeg[b] += 1
    for start in sorted(nodes, key=lambda n: indeg[n] > 0):
        if start in state:
            continue
        state[start] = 1
        stack = [(start, iter(out[start]))]
        while stack:
            n, it = stack[-1]
            step = next(it, None)
            if step is None:
                state[n] = 2
                order.append(n)
                stack.pop()
                continue
            i, b = step
            if state.get(b) == 1:
                back.add(i)
            elif b not in state:
                state[b] = 1
                stack.append((b, iter(out[b])))
    layer = {n: 0 for n in nodes}
    for n in reversed(order):
        for i, b in out[n]:
            if i not in back:
                layer[b] = max(layer[b], layer[n] + 1)
    return layer, back


def sankey_svg(r: dict) -> str:
    unit_row = {u["unit"]: u for u in r["units"]}
    nodes, edges, kind = [], [], {}

    def node(key, k):
        if key not in kind:
            kind[key] = k
            nodes.append(key)
        return key

    for s in r["streams"]:
        a = ("u", s["from"]) if s.get("from") in unit_row else ("feed", s["id"])
        b = ("u", s["to"]) if s.get("to") in unit_row else ("prod", s["id"])
        edges.append((node(a, a[0]), node(b, b[0]), s))
    layer, back = _layers(nodes, edges)
    for a, b, _ in edges:                       # pull each feed next to the unit it enters
        if kind[a] == "feed" and kind[b] == "u":
            layer[a] = max(0, layer[b] - 1)

    def mass(s):
        v = s.get("mass_kg_h")
        return v if isinstance(v, (int, float)) and v > 0 else None

    big = max((sum(mass(s) or 0 for a, b, s in edges if (b if side else a) == n) for n in nodes for side in (0, 1)), default=0) or 1.0
    scale = 120.0 / big

    def width(s):
        return max(2.0, mass(s) * scale) if mass(s) else 2.0

    cols = {}
    for n in nodes:
        cols.setdefault(layer[n], []).append(n)
    height = {n: max(14.0, sum(width(s) for a, _, s in edges if a == n), sum(width(s) for _, b, s in edges if b == n)) for n in nodes}
    gap, step_x, nw = 46.0, 230.0, 14.0
    total = max(sum(height[n] for n in c) + gap * (len(c) - 1) for c in cols.values())
    pos, centre = {}, {}
    for L in sorted(cols):
        def bary(n):
            ys = [centre[a] for a, b, _ in edges if b == n and a in centre]
            return sum(ys) / len(ys) if ys else total / 2
        col = sorted(cols[L], key=bary)
        y = 40 + (total - sum(height[n] for n in col) - gap * (len(col) - 1)) / 2
        for n in col:
            pos[n] = (70 + L * step_x, y)
            centre[n] = y + height[n] / 2
            y += height[n] + gap
    out_y = {n: pos[n][1] for n in nodes}
    in_y = dict(out_y)
    svg, labels, n_back = [], [], 0
    for i, (a, b, s) in sorted(enumerate(edges), key=lambda e: (pos[e[1][1]][1], pos[e[1][0]][1])):
        w = width(s)
        x1, y1 = pos[a][0] + nw, out_y[a] + w / 2
        x2, y2 = pos[b][0], in_y[b] + w / 2
        out_y[a] += w
        in_y[b] += w
        val = f"{mass(s):,.0f} kg/h" if mass(s) else ("0 kg/h" if s.get("mass_kg_h") == 0 else "mass not given")
        cls = "flow" if mass(s) else "flow unknown"
        if i in back:
            n_back += 1
            low = 40 + total + 22 * n_back
            d = f"M{x1:.1f},{y1:.1f} C{x1 + 90:.1f},{y1:.1f} {x1 + 90:.1f},{low:.1f} {x1:.1f},{low:.1f} L{x2:.1f},{low:.1f} C{x2 - 90:.1f},{low:.1f} {x2 - 90:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
            cls += " recycle"
            lx, ly = (x1 + x2) / 2, low - 4
        else:
            mid = (x1 + x2) / 2
            d = f"M{x1:.1f},{y1:.1f} C{mid:.1f},{y1:.1f} {mid:.1f},{y2:.1f} {x2:.1f},{y2:.1f}"
            lx, ly = mid, (y1 + y2) / 2 - w / 2 - 3
        tip = escape(f"Stream {s['id']}: {val}" + (" (recycle)" if i in back else ""))
        svg.append(f'<path class="{cls}" d="{d}" stroke-width="{w:.1f}"><title>{tip}</title></path>')
        labels.append(f'<text class="slabel" x="{lx:.1f}" y="{ly:.1f}">{escape(str(s["id"]))} &#183; {escape(val)}</text>')
    for n in nodes:
        x, y = pos[n]
        if kind[n] != "u":
            svg.append(f'<rect class="bnode" x="{x}" y="{y:.1f}" width="{nw}" height="{height[n]:.1f}" rx="2"/>')
            tx, anchor = (x - 6, "end") if kind[n] == "feed" else (x + nw + 6, "start")
            labels.append(f'<text class="blabel" x="{tx}" y="{y + height[n] / 2 + 4:.1f}" text-anchor="{anchor}">{"Feed" if kind[n] == "feed" else "Out"}</text>')
            continue
        st = unit_row[n[1]]["mass"]["status"]
        svg.append(f'<rect class="unode {st}" x="{x}" y="{y:.1f}" width="{nw}" height="{height[n]:.1f}" rx="3"><title>{escape(str(n[1]))}: mass balance {LABEL[st]}</title></rect>')
        labels.append(f'<text class="ulabel" x="{x + nw / 2}" y="{y - 6:.1f}">{escape(str(n[1]))} {ICON[st]}</text>')
    W = 140 + (max(cols) if cols else 0) * step_x + nw
    H = 70 + total + 22 * n_back
    return (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" style="width:100%;min-width:{min(W, 760):.0f}px;max-width:{W:.0f}px;height:auto" role="img" aria-label="Mass flow between units">'
            + "".join(svg) + "".join(labels) + "</svg>")


def closure_svg(r: dict) -> str:
    rows = r["units"] + [r["overall"]]
    tol = r["tolerances"]["mass_tol"]
    vals = [abs(u["mass"]["residual_rel"]) for u in rows if "residual_rel" in u["mass"]]
    span = max([tol * 3] + vals) * 1.05
    x0, half, rh = 420.0, 240.0, 26
    h = rh * len(rows) + 30
    band = half * tol / span
    out = [f'<rect class="band" x="{x0 - band:.1f}" y="4" width="{2 * band:.1f}" height="{h - 28}"/>',
           f'<line class="axis" x1="{x0}" y1="4" x2="{x0}" y2="{h - 24}"/>',
           f'<text class="tick" x="{x0}" y="{h - 8}">0 (shaded: &#177;{100 * tol:g}% limit; scale &#177;{100 * span:.3g}%)</text>']
    for i, u in enumerate(rows):
        y, m = 8 + i * rh, u["mass"]
        out.append(f'<text class="rlabel" x="8" y="{y + 13}">{ICON[m["status"]]} {escape(str(u["unit"]))}</text>')
        if "residual_rel" not in m:
            out.append(f'<text class="nc" x="{x0 + band + 8:.1f}" y="{y + 13}">not checked<title>{escape(m["reason"])}</title></text>')
            continue
        v = m["residual_rel"]
        w = half * abs(v) / span
        x = x0 if v >= 0 else x0 - w
        tip = escape(f"{u['unit']}: in {m['in_kg_h']:,.1f}, out {m['out_kg_h']:,.1f} kg/h, residual {100 * v:+.3f}%")
        out.append(f'<rect class="bar {m["status"]}" x="{x:.1f}" y="{y + 2}" width="{max(w, 1.5):.1f}" height="14" rx="3"><title>{tip}</title></rect>')
        out.append(f'<text class="val" x="{x0 + half + 12}" y="{y + 13}">{100 * v:+.2f}% &#183; {LABEL[m["status"]]}</text>')
    return f'<svg viewBox="0 0 800 {h}" width="800" height="{h}" role="img" aria-label="Mass closure residual by unit">' + "".join(out) + "</svg>"


def _heatmap(r: dict) -> str:
    rows = r["comparison"]
    if not rows:
        return '<p class="muted">No model results were compared.</p>'
    props = list(dict.fromkeys(x["property"] for x in rows))
    cell = {(x["stream"], x["property"]): x for x in rows}
    out = ["<table><tr><th>Stream</th>" + "".join(f"<th>{escape(p)}</th>" for p in props) + "</tr>"]
    for sid in dict.fromkeys(x["stream"] for x in rows):
        tds = []
        for p in props:
            x = cell.get((sid, p))
            if x is None:
                tds.append("<td></td>")
            elif x["ratio"] is None:
                tds.append('<td class="hm nc" title="a number is missing on one side">?</td>')
            else:
                a = min(abs(x["ratio"]) / 2.0, 1.0) * 0.6
                rgb = "227,73,72" if x["ratio"] > 0 else "42,120,214"
                txt = ">999x" if abs(x["ratio"]) > 999 else f'{x["ratio"]:+.1f}x'
                mark = " &#10007;" if x["status"] == FAIL else ""
                tip = escape(f'design {x["design"]:.6g}, model {x["model"]:.6g}, limit {x["limit"]:.4g}')
                tds.append(f'<td class="hm" style="background:rgba({rgb},{a:.2f})" title="{tip}">{txt}{mark}</td>')
        out.append(f"<tr><th>{escape(str(sid))}</th>{''.join(tds)}</tr>")
    return "".join(out) + "</table>"


def _headlines(r: dict) -> dict:
    n = len(r["units"])

    def tally(rows, key=None):
        st = [(u[key] if key else u)["status"] for u in rows]
        return st.count(PASS), st.count(FAIL), st.count(NC)

    p, f, nc = tally(r["units"], "mass")
    checks = [u[k]["status"] for u in r["units"] + [r["overall"]] for k in KINDS]
    lp, lf, lnc = tally(r["links"])
    cf = sum(1 for x in r["comparison"] if x["status"] == FAIL)
    cn = sum(1 for x in r["comparison"] if x["status"] == NC)
    return {
        "top": {PASS: "Every check that ran passed, and nothing was left unchecked",
                FAIL: f"The audit fails: {r['counts'][FAIL]} finding(s) need correction",
                NC: f"No failure found, but the audit is incomplete: {r['counts'][NC]} item(s) not checked"}[r["verdict"]],
        "closure": f"Mass closes on {p} of {n} units; {f} fail and {nc} could not be checked",
        "coverage": f"{len(checks) - checks.count(NC)} of {len(checks)} balance checks could be run; {checks.count(FAIL)} of those failed",
        "compare": (f"Model results differ from the design beyond the limit in {cf} value(s)" + (f"; {cn} value(s) could not be compared" if cn else ""))
        if r["comparison"] else "Model results were not audited",
        "links": f"{lp} of {len(r['links'])} streams are linked to a P&ID line; {lf} conflict(s), {lnc} unlinked",
    }


CSS = """:root{--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--flow:#2a78d6;--good:#0ca30c;--warn:#fab219;--bad:#d03b3b}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#2c2c2a;--flow:#3987e5}}
:root[data-theme="dark"]{--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink2:#c3c2b7;--grid:#2c2c2a;--flow:#3987e5}
body{margin:0;padding:24px 16px;background:var(--page);color:var(--ink);font:14px/1.45 system-ui,-apple-system,"Segoe UI",sans-serif}
main{max-width:1100px;margin:0 auto}section{background:var(--surface);border:1px solid var(--grid);border-radius:8px;padding:16px;margin:0 0 16px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:0 0 12px}.muted{color:var(--ink2)}.scroll{overflow-x:auto}
.tiles{display:flex;gap:12px;flex-wrap:wrap;margin-top:12px}.tile{border:1px solid var(--grid);border-radius:8px;padding:10px 18px;min-width:130px}.tile b{display:block;font-size:30px}
.chip{display:inline-block;border:2px solid var(--muted);border-radius:12px;padding:0 8px;font-size:12px;white-space:nowrap}
.chip.pass{border-color:var(--good)}.chip.fail{border-color:var(--bad)}.chip.not_checked{border-color:var(--warn);border-style:dashed}.chip.review{border-color:var(--flow)}
table{border-collapse:collapse;font-variant-numeric:tabular-nums}th,td{border:1px solid var(--grid);padding:4px 8px;text-align:left;vertical-align:top}
.hm{text-align:center;min-width:64px}.hm.nc{border:2px dashed var(--warn)}
svg text{fill:var(--ink);font:12px system-ui,sans-serif}
.flow{fill:none;stroke:var(--flow);stroke-opacity:.45}.flow:hover{stroke-opacity:.85}.flow.unknown{stroke:var(--muted);stroke-dasharray:3 4}.flow.recycle{stroke-dasharray:8 3}
.unode{fill:var(--ink2);stroke-width:3}.unode.pass{stroke:var(--good)}.unode.fail{stroke:var(--bad)}.unode.not_checked{stroke:var(--warn)}.bnode{fill:var(--muted)}
svg .ulabel{text-anchor:middle;font-weight:700}svg .slabel{text-anchor:middle;fill:var(--ink2);font-size:11px;paint-order:stroke;stroke:var(--surface);stroke-width:3px}svg .blabel,svg .tick,svg .nc{fill:var(--ink2)}svg .tick{text-anchor:middle;font-size:11px}
.band{fill:var(--grid)}.axis{stroke:var(--muted)}.bar.pass{fill:var(--good)}.bar.fail{fill:var(--bad)}
@media print{section{break-inside:avoid}}"""


def html_page(r: dict) -> str:
    h = _headlines(r)
    tiles = "".join(f'<div class="tile">{_chip(k)}<b>{r["counts"][k]}</b><span class="muted">finding(s)</span></div>' for k in (FAIL, NC, REVIEW))
    cov = ["<table><tr><th>Unit</th>" + "".join(f"<th>{k.title()} balance</th>" for k in KINDS) + "</tr>"]
    for u in r["units"] + [r["overall"]]:
        cells = "".join(f'<td title="{escape(u[k]["reason"])}">{_chip(u[k]["status"])}</td>' for k in KINDS)
        cov.append(f"<tr><th>{escape(str(u['unit']))}{' (reactive)' if u['reactive'] else ''}</th>{cells}</tr>")
    links = ["<table><tr><th>Stream</th><th>P&amp;ID line</th><th>Check</th><th>Note</th><th>Tags on line</th></tr>"]
    links += [f"<tr><td>{escape(str(x['stream']))}</td><td>{escape(str(x['line_no'] or ''))}</td><td>{_chip(x['status'])}</td><td>{escape(x['reason'])}</td>"
              f"<td>{escape(', '.join(x['line_tags']))}</td></tr>" for x in r["links"]]
    finds = ["<table><tr><th>Check</th><th>Area</th><th>Item</th><th>Finding</th></tr>"]
    finds += [f"<tr><td>{_chip(f['status'])}</td><td>{escape(f['area'])}</td><td>{escape(f['item'])}</td><td>{escape(f['message'])}</td></tr>" for f in r["findings"]]
    tol = ", ".join(f"{k}={v:g}" for k, v in r["tolerances"].items())

    def sec(title, body, note=""):
        return f'<section><h2>{escape(title)}</h2>{f"<p class=muted>{note}</p>" if note else ""}<div class="scroll">{body}</div></section>'

    return ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            f"<title>HMB audit: {escape(str(r['name']))}</title><style>{CSS}</style></head><body><main>"
            f"<section><p class=\"muted\">HMB audit &#183; {escape(str(r['name']))}</p><h1>{escape(h['top'])}</h1>{_chip(r['verdict'])}<div class=\"tiles\">{tiles}</div></section>"
            + sec(h["closure"], closure_svg(r), "Residual = (in &#8722; out) / larger of the two. Hover a bar for flows.")
            + sec("Where the mass goes", sankey_svg(r), "Line width is mass flow; very small flows are drawn at a minimum width. Long dashes: recycle. Dotted grey: no mass given. Unit marks show the mass check.")
            + sec(h["coverage"], "".join(cov) + "</table>", "Hover a cell for the reason. A reactive unit needs a declared generation.")
            + sec(h["compare"], _heatmap(r), "Cell = (model &#8722; design) / limit; beyond &#177;1.0x fails. Red: model higher. Blue: model lower.")
            + sec(h["links"], "".join(links) + "</table>")
            + sec("All findings, failures first", "".join(finds) + "</table>")
            + f'<section><p class="muted">{escape(r["limits"])}</p><p class="muted">Tolerances (judgment defaults unless overridden): {escape(tol)}</p></section>'
            "</main></body></html>")


def write(r: dict, prefix: str) -> list[str]:
    files = [prefix + "_report.xlsx", prefix + "_report.html", prefix + "_findings.csv"]
    write_xlsx(files[0], sheets(r))
    with open(files[1], "w", encoding="utf-8") as fh:
        fh.write(html_page(r))
    pha.write_csv([["status", "area", "item", "message"]] + [[f["status"], f["area"], f["item"], f["message"]] for f in r["findings"]], files[2])
    return files

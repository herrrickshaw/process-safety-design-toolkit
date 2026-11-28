"""Simulator-style views of an `hmb_audit.audit` result: flowsheet, stream and unit property tables, run summary, text report.

The arrangement follows conventions common to commercial steady-state simulators (stream flags on a flowsheet, streams as table
columns with a units column and selectable property lists, a run summary, a paged text report). Drawing and layout are our own.
The flowsheet is generated from stream connectivity: it is not the PFD or P&ID drawing. Standard library only, no scripts.
"""
from __future__ import annotations

import math
import textwrap
from html import escape

from .hmb_audit import FAIL, NC, PASS, REVIEW

LABEL = {PASS: "PASS", FAIL: "FAIL", NC: "NOT CHECKED", REVIEW: "REVIEW"}
ICON = {PASS: "&#10003;", FAIL: "&#10007;", NC: "?", REVIEW: "!"}
KINDS = ("mass", "component", "energy")
_RANK = {PASS: 0, REVIEW: 1, NC: 2, FAIL: 3}
WIDTH = 100                      # text report page width, characters
_LABEL_W, _UNIT_W, _COL_W, _PER_PAGE = 28, 10, 13, 4


def chip(status: str, extra: str = "") -> str:
    return f'<span class="chip {status}">{ICON[status]} {LABEL[status]}{extra}</span>'


def _worst(statuses) -> str:
    return max(statuses, key=_RANK.__getitem__)


def stream_status(r: dict, sid) -> str:
    """Worst of the P&ID link, input findings and model comparison. A stream never compared with a model is not a pass."""
    found = [x["status"] for x in r["links"] if x["stream"] == sid]
    found += [f["status"] for f in r["findings"] if f["item"] == str(sid) and f["area"] in ("input", "design vs model")]
    if not any(x["stream"] == sid for x in r["comparison"]):
        found.append(NC)
    return _worst(found or [NC])


def unit_status(u: dict) -> str:
    found = [u[k]["status"] for k in KINDS]
    if u.get("generation"):
        found.append(u["generation"]["status"])
    return _worst(found)


def _fmt(v) -> str:
    """Display text for a table cell. A missing value is "-", never zero."""
    if v is None or v == "":
        return "-"
    if isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v):
        if abs(v) >= 1e9:
            return f"{v:.6g}"
        if v == int(v):
            return f"{int(v):,}"
        return f"{v:,.1f}" if abs(v) >= 1000 else f"{v:.4g}"
    return " ".join(str(v).split())


# ---- property lists ---------------------------------------------------------------------------------------------
def property_lists(r: dict) -> list[tuple[str, list[dict]]]:
    """[(list name, rows)]; each row is {label, unit, values (one per stream), model {stream index: model value that failed}}."""
    S = r["streams"]
    index = {s["id"]: i for i, s in enumerate(S)}
    failed = {}
    for x in r["comparison"]:
        if x["status"] == FAIL and x["stream"] in index:
            failed.setdefault(x["property"], {})[index[x["stream"]]] = x["model"]
    link = {x["stream"]: x for x in r["links"]}

    def row(label, unit, values, model=None):
        return {"label": label, "unit": unit, "values": values, "model": model or {}}

    def col(label, unit, key, prop=None):
        return row(label, unit, [s.get(key) for s in S], failed.get(prop or key))

    summary = [row("From", "", [s.get("from") for s in S]), row("To", "", [s.get("to") for s in S]), col("Phase", "", "phase"),
               col("Temperature", "degC", "T_C"), col("Pressure", "kPag", "P_kpag"), col("Mass flow", "kg/h", "mass_kg_h"),
               col("Enthalpy flow", "kW", "H_kW")]

    names = list(dict.fromkeys(c for s in S for c in (s.get("components") or {})))
    flows = [r["component_kg_h"][s["id"]] for s in S]
    material = [col("Mass flow", "kg/h", "mass_kg_h")]
    material += [row(f"Component {c}", "kg/h", [None if f is None else f.get(c, 0.0) for f in flows]) for c in names]
    bases = [(s.get("component_basis") or r["component_basis"]) if s.get("components") else None for s in S]
    used = {b for b in bases if b}
    frac_unit = f"{used.pop()} frac" if len(used) == 1 else "frac"
    material.append(row("Composition basis", "", [(b or "NOT DECLARED") if s.get("components") else None for s, b in zip(S, bases)]))
    for c in names:
        model = {}
        for prop, hit in failed.items():
            if prop.startswith(f"x[{c}] ("):
                model.update(hit)
        fractions = [(s.get("components") or {}).get(c, 0.0 if f else None) for s, f in zip(S, flows)]
        material.append(row(f"Fraction {c}", frac_unit, fractions, model))

    pid = [row("P&ID line", "", [link[s["id"]]["line_no"] for s in S]),
           row("Link check", "", [LABEL[link[s["id"]]["status"]] for s in S]),
           row("Tags on line", "", [", ".join(link[s["id"]]["line_tags"]) for s in S]),
           row("Source of row data", "", [s.get("source") for s in S])]
    return [("Summary", summary), ("Material balance", material), ("P&ID", pid)]


def stream_table_html(r: dict) -> str:
    """Streams as columns. The property list is switched with radio buttons and CSS only."""
    lists = property_lists(r)
    out = ['<div class="plists">']
    out += [f'<input type="radio" name="plist" id="plist-{n}"{" checked" if n == 0 else ""}><label for="plist-{n}">{escape(name)}</label>'
            for n, (name, _) in enumerate(lists)]
    for n, (name, rows) in enumerate(lists):
        head = []
        for i, s in enumerate(r["streams"]):
            target = f' id="stream-{i}"' if n == 0 else ""
            head.append(f'<th{target}><span class="sid">{escape(str(s["id"]))}</span><br>{chip(stream_status(r, s["id"]))}</th>')
        body = [f'<tr><th class="prop">{escape(name)}</th><th>Units</th>{"".join(head)}</tr>']
        for x in rows:
            cells = []
            for i, v in enumerate(x["values"]):
                if i in x["model"]:
                    cells.append(f'<td class="differs">{escape(_fmt(v))}<small>{ICON[FAIL]} model {escape(_fmt(x["model"][i]))}</small></td>')
                else:
                    cells.append(f"<td>{escape(_fmt(v))}</td>")
            body.append(f'<tr><th class="prop">{escape(x["label"])}</th><td class="uom">{escape(x["unit"])}</td>{"".join(cells)}</tr>')
        out.append(f'<div class="panel panel-{n} scroll"><table class="props">{"".join(body)}</table></div>')
    return "".join(out) + "</div>"


def unit_table_html(r: dict) -> str:
    equip = {x["unit"]: x for x in r["equipment"]}
    out = ["<table class=\"props\"><tr><th class=\"prop\">Unit</th><th>Type</th><th>Inlets</th><th>Outlets</th><th>Mass in kg/h</th>"
           "<th>Mass out kg/h</th><th>Mass residual</th><th>Duty kW</th><th>Work kW</th><th>Mass</th><th>Component</th><th>Energy</th>"
           "<th>Instruments, valves, relief</th></tr>"]
    for n, u in enumerate(r["units"] + [r["overall"]]):
        e = equip.get(u["unit"], {})
        m = u["mass"]
        rel = f'{100 * m["residual_rel"]:+.2f}%' if "residual_rel" in m else "-"
        tags = ", ".join(e.get("instruments", []) + e.get("valves", []) + e.get("relief_devices", []))
        cells = [e.get("type"), ", ".join(map(str, u["inlets"])), ", ".join(map(str, u["outlets"])), m.get("in_kg_h"), m.get("out_kg_h"),
                 rel, e.get("duty_kW"), e.get("work_kW")]
        checks = "".join(f'<td title="{escape(u[k]["reason"])}">{chip(u[k]["status"])}</td>' for k in KINDS)
        target = f' id="unit-{n}"' if n < len(r["units"]) else ""
        out.append(f'<tr><th class="prop"{target}>{escape(str(u["unit"]))}</th>' + "".join(f"<td>{escape(_fmt(c))}</td>" for c in cells)
                   + checks + f"<td>{escape(tags or '-')}</td></tr>")
    return "".join(out) + "</table>"


# ---- run summary ------------------------------------------------------------------------------------------------
def run_summary(r: dict) -> list[tuple[str, str]]:
    """What a simulator run log leads with: status, size and the largest deviation of each kind."""
    rows = r["units"] + [r["overall"]]
    states = [u[k]["status"] for u in rows for k in KINDS]
    facts = [("Run status", f"AUDIT COMPLETED - {LABEL[r['verdict']]}"),
             ("Case size", f"{len(r['units'])} units, {len(r['streams'])} streams"),
             ("Balance checks", f"{len(states) - states.count(NC)} of {len(states)} run, {states.count(FAIL)} failed"),
             ("Messages", f"{r['counts'][FAIL]} fail, {r['counts'][NC]} not checked, {r['counts'][REVIEW]} review")]

    def times(value, limit):
        return abs(value) / limit if limit else (math.inf if value else 0.0)

    def x_limit(ratio):
        return "over a zero limit" if math.isinf(ratio) else (">999 x limit" if ratio > 999 else f"{ratio:.2f} x limit")

    mass = [u for u in rows if "residual_rel" in u["mass"]]
    if mass:
        u = max(mass, key=lambda u: abs(u["mass"]["residual_rel"]))
        facts.append(("Largest mass residual", f"{u['unit']} {100 * u['mass']['residual_rel']:+.2f}% "
                      f"(limit {100 * r['tolerances']['mass_tol']:g}%)"))
    else:
        facts.append(("Largest mass residual", "not computed: no unit mass balance could be run"))
    comp = [(times(c["residual_kg_h"], c["limit_kg_h"]), u["unit"], c) for u in rows for c in u["component"]["components"]]
    if comp:
        ratio, tag, c = max(comp, key=lambda t: t[0])
        facts.append(("Largest component residual", f"{tag} {c['component']} {c['residual_kg_h']:+.4g} kg/h ({x_limit(ratio)})"))
    else:
        facts.append(("Largest component residual", "not computed: no component balance could be run"))
    energy = [(times(u["energy"]["residual_kW"], u["energy"]["limit_kW"]), u) for u in rows if "residual_kW" in u["energy"]]
    if energy:
        ratio, u = max(energy, key=lambda t: t[0])
        facts.append(("Largest energy residual", f"{u['unit']} {u['energy']['residual_kW']:+.4g} kW ({x_limit(ratio)})"))
    else:
        facts.append(("Largest energy residual", "not computed: no energy balance could be run"))
    dev = [x for x in r["comparison"] if x["ratio"] is not None]
    if dev:
        x = max(dev, key=lambda x: abs(x["ratio"]))
        facts.append(("Largest model deviation", f"{x['stream']} {x['property']} {x['difference']:+.4g} "
                      f"({x_limit(abs(x['ratio']))})"))
    else:
        facts.append(("Largest model deviation", "not computed: no values were compared"))
    return facts


# ---- flowsheet --------------------------------------------------------------------------------------------------
def layers(nodes: list, edges: list) -> tuple[dict, set]:
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


def graph(r: dict) -> tuple[list, list, dict, dict, set]:
    """Units and plant-boundary ends as nodes, streams as edges. Returns nodes, edges, node kind, layer, recycle edge indices."""
    tags = {u["unit"] for u in r["units"]}
    nodes, edges, kind = [], [], {}

    def node(key):
        if key not in kind:
            kind[key] = key[0]
            nodes.append(key)
        return key

    for s in r["streams"]:
        a = ("u", s["from"]) if s.get("from") in tags else ("feed", s["id"])
        b = ("u", s["to"]) if s.get("to") in tags else ("prod", s["id"])
        edges.append((node(a), node(b), s))
    layer, back = layers(nodes, edges)
    for a, b, _ in edges:                       # pull each feed next to the unit it enters
        if kind[a] == "feed" and kind[b] == "u":
            layer[a] = max(0, layer[b] - 1)
    return nodes, edges, kind, layer, back


_SLOT, _STEP, _GAP, _LEFT, _TOP = 64.0, 220.0, 56.0, 40.0, 30.0


def flowsheet_layout(r: dict) -> tuple[list[dict], list[dict], tuple[float, float]]:
    """Boxes, orthogonal stream routes and drawing size. Streams that skip a column or recycle run in a channel below the units."""
    nodes, edges, kind, layer, back = graph(r)
    ins = {n: [i for i, e in enumerate(edges) if e[1] == n] for n in nodes}
    outs = {n: [i for i, e in enumerate(edges) if e[0] == n] for n in nodes}
    size = {n: ((_SLOT, max(_SLOT, 30.0 * max(len(ins[n]), len(outs[n])) + 12)) if kind[n] == "u" else (44.0, 22.0)) for n in nodes}
    cols = {}
    for n in nodes:
        cols.setdefault(layer[n], []).append(n)
    total = max(sum(size[n][1] for n in c) + _GAP * (len(c) - 1) for c in cols.values())
    box, centre = {}, {}
    for L in sorted(cols):
        def bary(n):
            ys = [centre[edges[i][0]] for i in ins[n] if edges[i][0] in centre]
            return sum(ys) / len(ys) if ys else total / 2
        col = sorted(cols[L], key=bary)
        y = _TOP + (total - sum(size[n][1] for n in col) - _GAP * (len(col) - 1)) / 2
        for n in col:
            w, h = size[n]
            box[n] = {"key": n, "kind": kind[n], "x": _LEFT + L * _STEP + (_SLOT - w) / 2, "y": y, "w": w, "h": h, "layer": L}
            centre[n] = y + h / 2
            y += h + _GAP

    def ports(n, which, far):
        order = sorted(which, key=lambda i: (i in back, centre[edges[i][far]], i))
        return {i: box[n]["y"] + box[n]["h"] * (k + 1) / (len(order) + 1) for k, i in enumerate(order)}

    y_out, y_in = {}, {}
    for n in nodes:
        y_out.update(ports(n, outs[n], 1))
        y_in.update(ports(n, ins[n], 0))
    paths, in_gap, channel = [], {}, 0
    for i, (a, b, s) in enumerate(edges):
        x1, x2, y1, y2 = box[a]["x"] + box[a]["w"], box[b]["x"], y_out[i], y_in[i]
        if i not in back and layer[b] - layer[a] == 1:
            k = in_gap[layer[a]] = in_gap.get(layer[a], -1) + 1
            mid = _LEFT + layer[a] * _STEP + _SLOT + (_STEP - _SLOT) / 2 + ((k % 5) - 2) * 9
            points = [(x1, y1), (mid, y1), (mid, y2), (x2, y2)]
            lx = (x2 + mid) / 2 if kind[b] == "prod" else (x1 + mid) / 2
            ly = y2 if kind[b] == "prod" else y1
        else:
            channel += 1
            low = _TOP + total + 36 * channel
            xo = _LEFT + layer[a] * _STEP + _SLOT + 8 + 5 * (channel % 6)
            xi = _LEFT + layer[b] * _STEP - 8 - 5 * (channel % 6)
            points = [(x1, y1), (xo, y1), (xo, low), (xi, low), (xi, y2), (x2, y2)]
            lx, ly = (xo + xi) / 2, low
        paths.append({"stream": s["id"], "index": i, "points": points, "recycle": i in back, "label_at": (lx, ly)})
    width = _LEFT * 2 + max(cols) * _STEP + _SLOT
    height = _TOP + total + 36 * channel + 30
    return [box[n] for n in nodes], paths, (width, height)


_GLYPHS = (                                   # (words in the unit type, glyph drawn about the box centre, corner radius)
    (("pump",), '<circle r="14"/><path d="M-7,-10 L13,0 L-7,10 Z"/>', 6),
    (("compressor", "blower"), '<path d="M-14,-15 L14,-7 L14,7 L-14,15 Z"/>', 6),
    (("expander", "turbine"), '<path d="M-14,-7 L14,-15 L14,15 L-14,7 Z"/>', 6),
    (("exchanger", "heater", "cooler", "condenser", "reboiler"), '<circle r="15"/><path d="M-15,0 L-7,-8 L0,8 L7,-8 L15,0"/>', 6),
    (("column", "tower", "absorber", "stripper"), '<rect x="-8" y="-22" width="16" height="44" rx="8"/><path d="M-8,-7 H8 M-8,3 H8"/>', 6),
    (("reactor",), '<rect x="-12" y="-18" width="24" height="36" rx="10"/><path d="M-12,-8 L12,8 M12,-8 L-12,8"/>', 6),
    (("drum", "vessel", "separator", "flash", "tank", "knockout"), '<path d="M-12,5 H12"/>', 24),
    (("mixer", "splitter", "tee"), '<path d="M-13,-13 L13,0 L-13,13 Z"/>', 6),
)


def _glyph(unit_type: str) -> tuple[str, int]:
    t = unit_type.lower()
    for words, shape, radius in _GLYPHS:
        if any(w in t for w in words):
            return shape, radius
    return "", 3


def flowsheet_svg(r: dict) -> str:
    boxes, paths, (W, H) = flowsheet_layout(r)
    units = {u["unit"]: (n, u) for n, u in enumerate(r["units"])}
    types = {x["unit"]: str(x.get("type") or "") for x in r["equipment"]}
    link = {x["stream"]: x for x in r["links"]}
    lines, marks = [], []
    for p in paths:
        st = stream_status(r, p["stream"])
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p["points"])
        x, y = p["points"][-1]
        cls = f"pipe {st}" + (" recycle" if p["recycle"] else "")
        lines.append(f'<path class="{cls}" d="{d}"/><path class="head {st}" d="M{x:.1f},{y:.1f} l-8,-4 v8 Z"/>')
        sid, (lx, ly) = str(p["stream"]), p["label_at"]
        w = 7.2 * len(sid) + 24
        tip = escape(f"Stream {sid}: {LABEL[st]}. Opens its column in the stream table.")
        line_no = link[p["stream"]]["line_no"]
        under = f'<text class="lineno" x="{lx:.1f}" y="{ly + 21:.1f}">{escape(str(line_no))}</text>' if line_no else ""
        marks.append(f'<a href="#stream-{p["index"]}"><title>{tip}</title><rect class="flag {st}" x="{lx - w / 2:.1f}" y="{ly - 10:.1f}" '
                     f'width="{w:.1f}" height="20" rx="3"/><text class="flagtext" x="{lx:.1f}" y="{ly + 4:.1f}">{escape(sid)} {ICON[st]}</text></a>{under}')
    for b in boxes:
        x, y, w, h = b["x"], b["y"], b["w"], b["h"]
        if b["kind"] != "u":
            word = "Feed" if b["kind"] == "feed" else "Out"
            marks.append(f'<path class="terminal" d="M{x:.1f},{y:.1f} h{w - 9:.1f} l9,{h / 2:.1f} l-9,{h / 2:.1f} h-{w - 9:.1f} Z"/>'
                         f'<text class="termtext" x="{x + w / 2 - 3:.1f}" y="{y + h / 2 + 4:.1f}">{word}</text>')
            continue
        tag = b["key"][1]
        n, u = units[tag]
        st = unit_status(u)
        shape, radius = _glyph(types.get(tag, ""))
        detail = ", ".join(f"{k} {LABEL[u[k]['status']]}" for k in KINDS)
        title = f"{tag} {types.get(tag, '')}: {detail}"
        marks.append(f'<a href="#unit-{n}"><title>{escape(title)}</title>'
                     f'<rect class="equip {st}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{radius}"/>'
                     f'<g class="glyph" transform="translate({x + w / 2:.1f},{y + h / 2:.1f})">{shape}</g>'
                     f'<text class="tag" x="{x + w / 2:.1f}" y="{y - 8:.1f}">{escape(str(tag))} {ICON[st]}</text></a>')
    return (f'<svg class="pfd" viewBox="0 0 {W:.0f} {H:.0f}" style="width:100%;min-width:{min(W, 900):.0f}px;max-width:{W:.0f}px;height:auto" '
            f'role="group" aria-label="Flowsheet generated from stream connectivity">' + "".join(lines) + "".join(marks) + "</svg>")


# ---- text report ------------------------------------------------------------------------------------------------
def _wrap(text: str, indent: str = "", hang: str | None = None) -> list[str]:
    return textwrap.wrap(" ".join(str(text).split()), WIDTH, initial_indent=indent,
                         subsequent_indent=indent if hang is None else hang) or [indent.rstrip()]


def _row(label: str, unit: str, cells: list[str]) -> list[str]:
    """One table row; a cell too wide for its column continues on the next line, nothing is cut off."""
    parts = [textwrap.wrap(label, _LABEL_W) or [""], textwrap.wrap(unit, _UNIT_W) or [""]]
    parts += [textwrap.wrap(c, _COL_W) or [""] for c in cells]
    widths = [_LABEL_W, _UNIT_W] + [_COL_W] * len(cells)
    out = []
    for n in range(max(map(len, parts))):
        piece = [p[n] if n < len(p) else "" for p in parts]
        line = " ".join(f"{v:<{w}}" if k < 2 else f"{v:>{w}}" for k, (v, w) in enumerate(zip(piece, widths)))
        out.append(line.rstrip())
    return out


def text_report(r: dict) -> str:
    """Fixed-width report for printing or diffing between revisions."""
    out = ["=" * WIDTH] + _wrap(f"HEAT AND MATERIAL BALANCE AUDIT - {r['name']}") + ["=" * WIDTH]

    def section(name):
        out.extend(["", name, "-" * WIDTH])

    section("RUN SUMMARY")
    for k, v in run_summary(r):
        out.extend(textwrap.wrap(" ".join(v.split()), WIDTH, initial_indent=f"{k + ':':<30}", subsequent_indent=" " * 30))
    section("MESSAGES")
    if not r["findings"]:
        out.append("None.")
    for f in r["findings"]:
        out.extend(_wrap(f"[{LABEL[f['status']]}] {f['area']} - {f['item']}: {f['message']}", "", "    "))
    section("STREAM SUMMARY")
    out.append("A dash means the value was not given or could not be worked out. It does not mean zero.")
    lists = property_lists(r)
    ids = [str(s["id"]) for s in r["streams"]]
    for start in range(0, len(ids), _PER_PAGE):
        page = slice(start, start + _PER_PAGE)
        for name, rows in lists:
            out.extend(["", f"[{name}]"])
            out.extend(_row("Stream", "Units", ids[page]))
            for x in rows:
                out.extend(_row(x["label"], x["unit"], [_fmt(v) for v in x["values"][page]]))
    section("UNIT SUMMARY")
    equip = {x["unit"]: x for x in r["equipment"]}
    for u in r["units"] + [r["overall"]]:
        e = equip.get(u["unit"], {})
        out.extend(["", f"{u['unit']}  {e.get('type', '')}".rstrip()])
        m = u["mass"]
        numbers = f"in {_fmt(m['in_kg_h'])} out {_fmt(m['out_kg_h'])} kg/h, residual {100 * m['residual_rel']:+.2f}%" if "residual_rel" in m else ""
        out.extend(_wrap(f"mass: {LABEL[m['status']]} {numbers or m['reason']}", "  ", "      "))
        out.extend(_wrap(f"component: {LABEL[u['component']['status']]} {u['component']['reason']}", "  ", "      "))
        q = u["energy"]
        numbers = f"residual {q['residual_kW']:+.4g} kW, limit {q['limit_kW']:.4g} kW" if "residual_kW" in q else q["reason"]
        out.extend(_wrap(f"energy: {LABEL[q['status']]} {numbers}", "  ", "      "))
        tags = e.get("instruments", []) + e.get("valves", []) + e.get("relief_devices", [])
        if tags:
            out.extend(_wrap("tags: " + ", ".join(tags), "  ", "      "))
    section("P&ID LINKS")
    for x in r["links"]:
        out.extend(_wrap(f"{x['stream']}  line {x['line_no'] or '-'}  {LABEL[x['status']]}  {x['reason']}", "", "    "))
    section("DESIGN VS MODEL")
    if not r["comparison"]:
        out.append("Not compared: no model results.")
    else:
        passed = sum(1 for x in r["comparison"] if x["status"] == PASS)
        out.append(f"{passed} of {len(r['comparison'])} values within limits. Others:")
        for x in r["comparison"]:
            if x["status"] != PASS:
                out.extend(_wrap(f"{x['stream']} {x['property']}: design {_fmt(x['design'])}, model {_fmt(x['model'])} {LABEL[x['status']]}",
                                 "  ", "      "))
    section("TOLERANCES AND LIMITS")
    for k, v in r["tolerances"].items():
        out.append(f"{k:<30}{v:g}")
    out.append("")
    out.extend(_wrap("Tolerances are judgment defaults unless overridden. " + r["limits"]))
    return "\n".join(out) + "\n"

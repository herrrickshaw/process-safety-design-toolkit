"""urea_psfs.py - Process Safeguarding Flow Scheme (PSFS) sheets for the coal-to-urea package, drawn from the package registers (psfs_model.py).

One box per unit sheet, four sections after the public description of the PSFS (enggcyclopedia.com 'Safeguarding Memorandum' section 8):
  A final safeguards (relief devices with set pressure, capacity and destination; instrumented protective functions)
  B capacity-determining components (control valves with fail action; the >25 % screen is NOT performed, stated on the box)
  C mitigating systems (ESD valves with fail action)
  D interfaces (discharge destinations: flare, atmosphere, closed drain, ...)
Every safeguard is listed: nothing is truncated into a '+ n more' line (psfs_lint.py rule P08 fails the build on that). The same drawing routine draws
the blank template (psfs_template.py), so the template and the real sheets cannot drift apart.
Not covered (gap): the capacity-determining >25 % screen, non-return valve identification, unit-to-unit connectivity; the defining standard's symbol
and layout rules are proprietary and were not used.
"""
import textwrap, collections
from pid_unit import *
import pid_rec
import psfs_model as M

COLW, GAP, X0, TOP, BOTTOM = 380, 10, 20, 96, 945
PACK = "ffd"                 # "shelf" keeps register order, "ffd" sorts each area tallest first (psfs_variants.py picks the better)
WRAPN = 73                      # characters per text line inside a box (8.6 px text, 0.52 em)
HEAD_H, SEC_H, LINE_H, ROW_PAD = 40, 16, 11, 7
NAMES = {1: "Coal and petcoke handling", 2: "Air separation", 3: "Gasification and water systems", 4: "Shift and heat recovery",
         5: "Acid gas removal, sulphur, methanation", 6: "Ammonia synthesis and storage", 7: "Urea synthesis and finishing", 8: "Utilities",
         9: "Offsites and safety systems"}


def _wrap(t): return textwrap.wrap(str(t), WRAPN, break_long_words=True) or [""]


def _short(t, n): t = str(t).strip(); return t if len(t) <= n else t[:n - 1] + "..."


def _capacity(r):
    s = r["sizing_status"].strip()
    return "capacity: not sized" if s.startswith("not sized") or "not sized" in s else "capacity: " + _short(s, 40)


def rows_of(u):
    """list of (section letter or None, kind, [text lines]) for a unit: the single source for both box height and drawing"""
    out = []
    out.append(("A", "head", ["A  Final safeguards: relief devices and instrumented protective functions"]))
    for r in u.A_relief:
        out.append(("A", "psv", _wrap(f"{r['tag']}  set {r['set_bar_g']} bar g, {_capacity(r)}  >  {r['destination']}")))
    for i in u.A_trips:
        out.append(("A", "trip", _wrap(f"{i['tag']}  {i['function']}  {i['alarm_trip']}  ({i['service']})")))
    if u.det: out.append(("A", "det", _wrap(f"{len(u.det)} gas / analyser detector(s), e.g. {u.det[0]['tag']}")))
    if not (u.A_relief or u.A_trips or u.det): out.append(("A", "txt", ["none on this unit sheet"]))
    out.append(("B", "head", ["B  Capacity-determining components and control valve fail action"]))
    for v in u.B_control:
        out.append(("B", "ctl", _wrap(f"{v['tag']}  control valve, fail {v['fail_position']}  ({v['service']})")))
    out.append(("B", "txt", ["relief-case screen (>25 % of device capacity): not performed"] if u.A_relief else ["no relief device on this sheet"]))
    out.append(("C", "head", ["C  Mitigating systems: ESD valves"]))
    for v in u.C_esd: out.append(("C", "esd", _wrap(f"{v['tag']}  {v['type']}, fail {v['fail_position']}  ({v['service']})")))
    if not u.C_esd: out.append(("C", "txt", ["none on this unit sheet"]))
    out.append(("D", "head", ["D  Interfaces: discharge destinations"]))
    for d, tags in u.interfaces.items(): out.append(("D", "txt", _wrap(f"{d}: {', '.join(tags)}")))
    if not u.A_relief: out.append(("D", "txt", ["no relief discharge"]))
    return out


MIN_H = {"psv": 26, "ctl": 32, "esd": 24, "trip": 24, "det": 24}     # symbol rows are at least as tall as their symbol (valve actuators rise above the centre)


def row_h(kind, lines): return SEC_H if kind == "head" else max(len(lines) * LINE_H + ROW_PAD, MIN_H.get(kind, 0))


def box_height(u):
    return HEAD_H + 6 + sum(row_h(kind, lines) for sec, kind, lines in rows_of(u)) + 4


def _mini_psv(sh, x, y):
    sh.add(f'<g transform="translate({x},{y}) scale(0.55)" stroke="{INK}" stroke-width="2.2" fill="#fff"><polygon points="-10,16 10,16 0,-2"/><polygon points="0,-2 18,-10 18,10"/>'
           f'<polyline points="0,-2 0,-8 -6,-12 6,-17 -6,-22 6,-27 0,-31" fill="none"/></g>')
    pid_rec.rec(sh, "valve", x - 6, y - 17, x + 10, y + 9)


def draw_unit_box(sh, x, y, u, title=None, subtitle=None):
    """draw one unit box at (x, y), record its rectangle in sh.psfs_boxes, return its height"""
    h = box_height(u); eq = u.equip[0] if u.equip else None
    R(sh, x, y, COLW, h, "#fff", INK, 1.2); R(sh, x, y, COLW, HEAD_H, "#e8eaf0", INK, 1.2)
    T(sh, x + 6, y + 15, title or _short(f"{eq['tag']}  {eq['name']}", 56), 10.5, 700)
    T(sh, x + 6, y + 31, subtitle or f"sheet {u.sheet}  |  {_short(eq['type'], 50)}", 8.8, 400, fill=GREY)
    yy = y + HEAD_H + 6
    for sec, kind, lines in rows_of(u):
        if kind == "head":
            R(sh, x + 1, yy, COLW - 2, SEC_H - 2, "#f2f2f2", "none"); T(sh, x + 6, yy + 11, lines[0], 8.8, 700, fill="#1a237e"); yy += SEC_H; continue
        rh = row_h(kind, lines); ry = yy + rh / 2 + (4 if kind == "ctl" else 0)
        if kind == "psv": _mini_psv(sh, x + 14, ry + 2)
        elif kind == "esd": valve(sh, x + 14, ry, 0, "ball", False, RED)
        elif kind == "ctl": valve(sh, x + 14, ry, 0, "gate", True, INK)
        elif kind == "trip": bubble(sh, x + 14, ry, "SIS", "", False, INK, 8)
        elif kind == "det": bubble(sh, x + 14, ry, "AT", "", False, GREEN, 8)
        y0 = yy + (rh - len(lines) * LINE_H) / 2 + 8
        for k, ln in enumerate(lines):
            T(sh, x + (34 if kind != "txt" else 12), y0 + k * LINE_H, ln, 8.6, 400, fill=(GREY if kind == "txt" else INK))
        yy += rh
    sh.psfs_boxes.append(dict(x=x, y=y, w=COLW, h=h, sheet=u.sheet))
    return h


def legend(sh, ly=962):
    section(sh, 20, ly - 2, 1100, "Legend")
    _mini_psv(sh, 40, ly + 46); T(sh, 56, ly + 46, "relief device > set, capacity, destination", 9.5)
    valve(sh, 330, ly + 40, 0, "ball", False, RED); T(sh, 348, ly + 44, "ESD valve (fail action)", 9.5)
    valve(sh, 520, ly + 40, 0, "gate", True, INK); T(sh, 538, ly + 44, "control valve (fail action)", 9.5)
    bubble(sh, 720, ly + 40, "SIS", "", False, INK, 8); T(sh, 736, ly + 44, "instrumented protective function", 9.5)
    bubble(sh, 940, ly + 40, "AT", "", False, GREEN, 8); T(sh, 956, ly + 44, "gas / analyser detector", 9.5)
    T(sh, 20, ly + 72, "Derived from RELIEF_SCHEDULE, VALVE_LIST, INSTRUMENT_INDEX and EQUIPMENT_LIST of this build. Gaps: capacity-determining screen (>25 %), non-return valve", 8.8, 400, fill=GREY)
    T(sh, 20, ly + 84, "identification, unit-to-unit connectivity; the standard that defines the PSFS format is proprietary and was not used. Checked by scripts/psfs_lint.py.", 8.8, 400, fill=GREY)


def new_sheet(pkg, no, title, sub):
    sh = USheet(pkg, no, title, sub, None); sh.docs = True; sh.psfs = True; sh.psfs_boxes = []
    return sh


def pack(units):
    """shelf-pack (sheet, Unit) pairs into pages of [(col, y, sheet, Unit)]"""
    if PACK == "ffd": units = sorted(units, key=lambda p: -box_height(p[1]))      # tallest first: fewer gaps in each shelf row
    ncols = (1600 - 2 * X0 + GAP) // (COLW + GAP); pages = [[]]; y = TOP; xi = 0; rowh = 0
    for n, u in units:
        hh = box_height(u)
        if xi >= ncols: xi = 0; y += rowh + GAP; rowh = 0
        if y + hh > BOTTOM and pages[-1]: pages.append([]); y = TOP; xi = 0; rowh = 0
        pages[-1].append((xi, y, n, u)); xi += 1; rowh = max(rowh, hh)
    return pages


def apply(pkg, first_no=971):
    regs = M.Regs.from_pkg(pkg); U = M.build(regs); by_area = collections.OrderedDict()
    for n, u in U.items(): by_area.setdefault(n // 100, []).append((n, u))
    no = first_no; made = 0; stats = []
    for a, units in by_area.items():
        pages = pack(units)
        for pi, items in enumerate(pages):
            title = f"Safeguarding  -  Process Safeguarding Flow Scheme (conceptual view), area {a}0 {NAMES.get(a, '')}" + (f" ({pi + 1} of {len(pages)})" if len(pages) > 1 else "")
            sh = new_sheet(pkg, no, title, f"final safeguards of area {a}0 units"); no += 1
            for xi, yy, n, u in items: draw_unit_box(sh, X0 + xi * (COLW + GAP), yy, u)
            legend(sh); frame(sh, pkg.total); pkg.add_sheet(sh); made += 1
        stats.append((a, len(units), sum(len(u.A_relief) for _, u in units), sum(len(u.C_esd) for _, u in units), sum(len(u.A_trips) for _, u in units)))
    return dict(psfs_sheets=made, areas=stats)


def remove(pkg):
    """drop every PSFS sheet from the package (used by the linter's fix mode before it redraws them)"""
    pkg.sheets[:] = [s for s in pkg.sheets if not getattr(s, "psfs", False)]

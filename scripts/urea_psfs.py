"""urea_psfs.py - Process Safeguarding Flow Scheme (PSFS) sheets for the coal-to-urea package, derived from the package's own registers.

A PSFS is a simplified view of the P&IDs that shows only the final safeguards of each unit: relief devices with their discharge destination, trip / ESD isolation
valves and the instrumented protective functions (summary of the public description at enggcyclopedia.com 'Safeguarding Memorandum'). This module builds that view
for every unit sheet of the package: one box per unit (primary equipment tag and name, sheet reference) with its relief devices, ESD valves and trips listed beside
mini symbols. Nothing is added to the design: every row comes from RELIEF_SCHEDULE, VALVE_LIST and INSTRUMENT_INDEX data of the same build.
Not covered (gap): capacity-determining components (control and bypass valves whose opening can exceed 25 % of the relief flow), non-return valve identification,
the flowsheet connectivity between units, and the standard's own symbol and layout rules (the defining standard is proprietary and was not used).
"""
import re, math, collections
from pid_unit import *
import pid_rec

TRIPS = {"LAHH", "LALL", "TAHH", "PAHH", "PALL", "TALL", "VAHH", "PDAHH", "FALL", "BSLL", "XA", "PAH"}
COLW, GAP, X0, TOP = 300, 10, 20, 96


def _short(t, n): t = str(t).strip(); return t if len(t) <= n else t[:n - 1] + "..."


def _dest(d):
    d = str(d)
    for k, v in (("flare", "flare"), ("atmosphere", "atmosphere"), ("safe", "safe place"), ("drain", "closed drain"), ("slop", "slop"), ("retention", "retention"),
                 ("scrubber", "scrubber"), ("vent", "vent"), ("BOG", "BOG header"), ("KO", "KO drum")):
        if k.lower() in d.lower(): return v
    return _short(d, 18)


def _units(pkg):
    """unit sheet -> dict(equipment rows, relief rows, ESD valves, trips, detectors)"""
    U = collections.OrderedDict()
    for e in sorted(pkg.equip, key=lambda r: int(r[-1])):
        if int(e[-1]) >= 950: continue
        U.setdefault(int(e[-1]), dict(eq=[], psv=[], esd=[], trip=[], det=[]))["eq"].append(e)
    for r in pkg.relief:
        if int(r[7]) in U: U[int(r[7])]["psv"].append(r)
    for v in pkg.valves:
        if "ESD" in str(v[5]) and int(v[6]) in U: U[int(v[6])]["esd"].append(v)
    for i in pkg.inst:
        n = int(i[7])
        if n not in U: continue
        if i[3] in TRIPS or re.search(r"trip", str(i[5]), re.I) and i[3] not in ("AT", "AAH", "AAHH"): U[n]["trip"].append(i)
        elif i[3] in ("AT", "AAH", "AAHH"): U[n]["det"].append(i)
    return U


def _mini_psv(sh, x, y):
    sh.add(f'<g transform="translate({x},{y}) scale(0.55)" stroke="{INK}" stroke-width="2.2" fill="#fff"><polygon points="-10,16 10,16 0,-2"/><polygon points="0,-2 18,-10 18,10"/>'
           f'<polyline points="0,-2 0,-8 -6,-12 6,-17 -6,-22 6,-27 0,-31" fill="none"/></g>')
    pid_rec.rec(sh, "valve", x - 6, y - 17, x + 10, y + 9)


def _box(pkg, sh, x, y, u):
    """draw one unit box at (x, y); returns its height"""
    eq = u["eq"][0]; rows = []
    for r in u["psv"][:2]:
        st = "" if not str(r[6]).startswith("not sized") else " (not sized)"
        rows.append(("psv", f"{r[0]}  {_short(r[3], 8)} bar g > {_dest(r[5])}{st}"))
    if len(u["psv"]) > 2: rows.append(("txt", f"+ {len(u['psv']) - 2} more relief device(s)"))
    for v in u["esd"][:2]: rows.append(("esd", f"{v[0]}  ESD isolation, {_short(v[5], 10)}"))
    if len(u["esd"]) > 2: rows.append(("txt", f"+ {len(u['esd']) - 2} more ESD valve(s)"))
    for i in u["trip"][:4]: rows.append(("trip", f"{i[0]}  {_short(i[5], 30)}"))
    if len(u["trip"]) > 4: rows.append(("txt", f"+ {len(u['trip']) - 4} more trip(s)"))
    if u["det"]: rows.append(("det", f"{len(u['det'])} gas / analyser detector(s), e.g. {u['det'][0][0]}"))
    if not rows: rows.append(("txt", "no final safeguard on this unit sheet"))
    h = 46 + len(rows) * 22 + 6
    R(sh, x, y, COLW, h, "#fff", INK, 1.2); R(sh, x, y, COLW, 40, "#e8eaf0", INK, 1.2)
    T(sh, x + 6, y + 15, _short(f"{eq[0]}  {eq[1]}", 46), 10.5, 700)
    T(sh, x + 6, y + 31, f"sheet {eq[-1]}  |  {_short(eq[3], 40)}", 8.8, 400, fill=GREY)
    yy = y + 46
    for kind, txt in rows:
        cy = yy + 11
        if kind == "psv": _mini_psv(sh, x + 14, cy + 4)
        elif kind == "esd":
            valve(sh, x + 14, cy, 0, "ball", False, RED)
        elif kind == "trip":
            bubble(sh, x + 14, cy, "SIS", "", False, INK, 9)
        elif kind == "det":
            bubble(sh, x + 14, cy, "AT", "", False, GREEN, 9)
        T(sh, x + 36 if kind != "txt" else x + 10, cy + 3.5, txt, 8.6, 400, fill=(GREY if "not sized" in txt or kind == "txt" else INK))
        yy += 22
    return h


def apply(pkg):
    U = _units(pkg); by_area = collections.OrderedDict()
    for n, u in U.items(): by_area.setdefault(n // 100, []).append((n, u))
    NAMES = {1: "Coal and petcoke handling", 2: "Air separation", 3: "Gasification and water systems", 4: "Shift and heat recovery", 5: "Acid gas removal, sulphur, methanation",
             6: "Ammonia synthesis and storage", 7: "Urea synthesis and finishing", 8: "Utilities", 9: "Offsites and safety systems"}
    no = 971; made = 0; stats = []
    ncols = (1600 - 2 * X0 + GAP) // (COLW + GAP)
    for a, units in by_area.items():
        pages = [[]]; ys = [TOP]; col = 0; rowh = 0; y = TOP; cur = pages[0]
        # simple shelf packing: fill columns left to right, then a new row
        x_i = 0
        for n, u in units:
            hh = 46 + (min(len(u["psv"]), 2) + (len(u["psv"]) > 2) + min(len(u["esd"]), 2) + (len(u["esd"]) > 2) + min(len(u["trip"]), 4) + (len(u["trip"]) > 4) + (1 if u["det"] else 0) or 1) * 22 + 6
            if x_i >= ncols: x_i = 0; y += rowh + GAP; rowh = 0
            if y + hh > 945: pages.append([]); cur = pages[-1]; y = TOP; x_i = 0; rowh = 0
            cur.append((x_i, y, n, u)); x_i += 1; rowh = max(rowh, hh)
        for pi, items in enumerate(pages):
            if not items: continue
            title = f"Safeguarding  -  Process Safeguarding Flow Scheme (conceptual view), area {a}0 {NAMES.get(a, '')}" + (f" ({pi + 1} of {len(pages)})" if len(pages) > 1 else "")
            sh = USheet(pkg, no, title, f"final safeguards of area {a}0 units", None); sh.docs = True; no += 1
            for xi, yy, n, u in items: _box(pkg, sh, X0 + xi * (COLW + GAP), yy, u)
            ly = 962
            section(sh, 20, ly - 2, 1100, "Legend")
            _mini_psv(sh, 40, ly + 46); T(sh, 56, ly + 46, "relief device > discharge", 9.5)
            valve(sh, 250, ly + 40, 0, "ball", False, RED); T(sh, 268, ly + 44, "ESD / trip isolation valve", 9.5)
            bubble(sh, 450, ly + 40, "SIS", "", False, INK, 9); T(sh, 466, ly + 44, "instrumented protective function (trip)", 9.5)
            bubble(sh, 700, ly + 40, "AT", "", False, GREEN, 9); T(sh, 716, ly + 44, "gas detector / analyser", 9.5)
            T(sh, 20, ly + 72, "Derived from RELIEF_SCHEDULE, VALVE_LIST and INSTRUMENT_INDEX of this build. Gap: capacity-determining components, non-return valve identification and unit-to-unit connectivity; "
                               "the standard that defines the PSFS format is proprietary and was not used.", 8.8, 400, fill=GREY)
            frame(sh, pkg.total); pkg.add_sheet(sh); made += 1
        stats.append((a, len(units), sum(len(u["psv"]) for _, u in units), sum(len(u["esd"]) for _, u in units), sum(len(u["trip"]) for _, u in units)))
    return dict(psfs_sheets=made, areas=stats)

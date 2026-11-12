#!/usr/bin/env python3
"""psfs_lint.py - linter and fixer for the Process Safeguarding Flow Scheme (PSFS) sheets of the coal-to-urea package.

Checks the DRAWN sheets (the text actually placed in each unit box) against the registers (RELIEF_SCHEDULE, VALVE_LIST, INSTRUMENT_INDEX,
EQUIPMENT_LIST), then the registers themselves for the mistakes a PSFS reviewer looks for. Rules follow the public description of the PSFS
(enggcyclopedia.com/2012/05/safeguarding-memorandum, section 8: A final safeguards, B capacity-determining components and control-valve fail action,
C mitigating systems, D interfaces; ISO 15926-4 definition). The defining standard's own checklist is proprietary and was not available.

Usage: python3 scripts/psfs_lint.py [--fix] [--report out.md] [--json out.json] [--strict]
  builds the package in memory, lints it, and with --fix redraws the PSFS sheets from the registers (the correction for every drawing-level error)
  and lints again. Register-level errors cannot be fixed on the drawing: each carries the register and area module to edit.
  exit 1 when any error remains (and, with --strict, any advisory).

Rules (E = error, A = advisory)
  P01 E relief device in RELIEF_SCHEDULE not drawn in its unit box      P02 E ESD valve not drawn          P03 E instrumented trip not drawn
  P04 E relief destination blank or not a recognised destination         P05 E tag drawn that is not a register entry of that unit sheet
  P06 E safeguard drawn twice in one box, or a unit drawn in two boxes   P07 E control valve shown without fail action
  P08 E truncation text ('+ n more', '...') in a box                     P09 E ESD valve fail action is not FC / FO
  P10 E relief set pressure above the equipment design pressure          P11 E unit sheet has no PSFS box
  P12 E box text overflows its box, boxes overlap, or a box leaves the sheet     P13 E PSFS sheet without title phrase / legend
  P14 E duplicate relief tag in the register       P30 E high-pressure trip set above the design pressure of its equipment
  P20 A relief device capacity not sized      P21 A relief set pressure not numeric (per vendor)    P22 A capacity-determining (>25 %) screen not performed on a unit
"""
import sys, os, re, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import psfs_model as M
import urea_psfs
from pid_unit import *

Finding = collections.namedtuple("Finding", "code sev sheet tag msg fix")
FIXABLE_BY_REDRAW = {"P01", "P02", "P03", "P05", "P06", "P08", "P11", "P12", "P13"}
TRUNC = re.compile(r"\+\s*\d+\s+more|\.\.\.$")
HEAD_SKIP = urea_psfs.HEAD_H


def _area_module(sheet): return f"scripts/urea_area_{int(sheet) // 100}0.py"


def _text_boxes(sh):
    import gen_pid_urea_package as G
    return G.text_boxes(sh)


def drawn(sh):
    """for each box of a PSFS sheet: the texts inside it below the box header, as [(x0, y0, x1, y1, text)]"""
    tb = _text_boxes(sh); out = []
    for b in sh.psfs_boxes:
        inside = [t for t in tb if b["x"] <= (t[0] + t[2]) / 2 <= b["x"] + b["w"] and b["y"] + HEAD_SKIP <= (t[1] + t[3]) / 2 <= b["y"] + b["h"] + 6]
        out.append((b, inside))
    return out


def lint(pkg):
    F = []; regs = M.Regs.from_pkg(pkg); U = M.build(regs)
    psfs = [s for s in pkg.sheets if getattr(s, "psfs", False)]
    seen = collections.defaultdict(list)       # unit sheet -> [(psfs sheet, box, texts)]
    # ---- sheet level
    for sh in psfs:
        if "Process Safeguarding Flow Scheme" not in sh.title: F.append(Finding("P13", "E", sh.no, "", "title lacks 'Process Safeguarding Flow Scheme'", "redraw"))
        if not any("Legend" in t[4] for t in _text_boxes(sh)): F.append(Finding("P13", "E", sh.no, "", "no legend on the sheet", "redraw"))
        D = drawn(sh)
        for b, texts in D: seen[b["sheet"]].append((sh, b, texts))
        for i, (b, _) in enumerate(D):                                   # P12 geometry
            if b["x"] < 8 or b["x"] + b["w"] > 1592 or b["y"] < 80 or b["y"] + b["h"] > urea_psfs.BOTTOM + 2:
                F.append(Finding("P12", "E", sh.no, str(b["sheet"]), f"box of unit sheet {b['sheet']} leaves the drawing area (y {b['y']:.0f}..{b['y'] + b['h']:.0f})", "redraw (page break) or split the unit"))
            for c, _ in D[i + 1:]:
                if min(b["x"] + b["w"], c["x"] + c["w"]) > max(b["x"], c["x"]) and min(b["y"] + b["h"], c["y"] + c["h"]) > max(b["y"], c["y"]):
                    F.append(Finding("P12", "E", sh.no, str(b["sheet"]), f"boxes of unit sheets {b['sheet']} and {c['sheet']} overlap", "redraw"))
    # ---- unit level
    for n, u in U.items():
        boxes = seen.get(n, [])
        if not boxes: F.append(Finding("P11", "E", n, "", f"unit sheet {n} has no PSFS box", "redraw")); continue
        if len(boxes) > 1: F.append(Finding("P06", "E", n, "", f"unit sheet {n} is drawn in {len(boxes)} PSFS boxes", "redraw"))
        sh, b, texts = boxes[0]
        rows = collections.Counter(); dtags = set()
        for x0, y0, x1, y1, tx in texts:
            m = M.TAG.match(tx)
            if m: rows[m.group()] += 1
            elif re.match(r"^(flare|atmosphere|safe place|closed drain|slop|retention|scrubber|vent|BOG header|KO drum|UNKNOWN):", tx): dtags |= set(M.TAG.findall(tx))
            if TRUNC.search(tx.strip()): F.append(Finding("P08", "E", sh.no, str(n), f"truncation text {tx.strip()!r} hides safeguards", "redraw: every safeguard must be listed"))
            if x1 > b["x"] + b["w"] - 2 or y1 > b["y"] + b["h"]:
                F.append(Finding("P12", "E", sh.no, str(n), f"text {tx[:40]!r} overflows its box", "redraw (wrap)"))
        for need, code, what in ((u.A_relief, "P01", "relief device"), (u.C_esd, "P02", "ESD valve"), (u.A_trips, "P03", "instrumented trip")):
            for r in need:
                if rows[r["tag"]] == 0: F.append(Finding(code, "E", sh.no, r["tag"], f"{what} {r['tag']} (register sheet {n}) is not drawn in its PSFS box", "redraw"))
        for v in u.B_control:
            if rows[v["tag"]] == 0: F.append(Finding("P07", "E", sh.no, v["tag"], f"control valve {v['tag']} (register sheet {n}) is not drawn in its PSFS box with its fail action", "redraw"))
        for t, k in rows.items():
            if t not in u.tags: F.append(Finding("P05", "E", sh.no, t, f"{t} drawn in the box of unit sheet {n} but not a register entry of that sheet", "redraw (or fix the register sheet number)"))
            if k > 1: F.append(Finding("P06", "E", sh.no, t, f"{t} drawn {k} times in the box of unit sheet {n}", "redraw"))
        for t in dtags - {r["tag"] for r in u.A_relief}: F.append(Finding("P05", "E", sh.no, t, f"{t} listed under D interfaces of unit sheet {n} but not a relief device of it", "redraw"))
    # ---- register level
    rt = collections.Counter(r["tag"] for r in regs.relief)
    for t, k in rt.items():
        if k > 1: F.append(Finding("P14", "E", "", t, f"relief tag {t} appears {k} times in RELIEF_SCHEDULE", "RELIEF_SCHEDULE: tags must be unique"))
    design = collections.defaultdict(list)
    for e in regs.equip:
        d = M.design_bar_g(e)
        if d is not None: design[int(e["sheet"])].append((d, e["tag"]))

    def protected(r):
        """design pressure of the equipment a relief device protects: the equipment tag named in 'protects' (whole token), else the only equipment of the sheet"""
        n = int(r["sheet"]); hit = [(d, t) for d, t in design.get(n, []) if re.search(rf"(?<![\w-]){re.escape(t)}(?![\w-])", r["protects"])]
        if hit: return hit[0]
        eqs = [e for e in regs.equip if int(e["sheet"]) == n]
        return design[n][0] if len(eqs) == 1 and design.get(n) else None
    for r in regs.relief:
        n = int(r["sheet"]); where = f"{_area_module(n)} (psv_at call for {r['tag']})"
        if not M.dest_class(r["destination"]): F.append(Finding("P04", "E", n, r["tag"], f"relief {r['tag']} destination {r['destination']!r} is blank or not a recognised destination", where))
        sp = M.first_number(r["set_bar_g"])
        if sp is None: F.append(Finding("P21", "A", n, r["tag"], f"relief {r['tag']} set pressure {r['set_bar_g']!r} is not numeric", where))
        elif protected(r) and sp > protected(r)[0] + 1e-9:
            lo = protected(r); F.append(Finding("P10", "E", n, r["tag"], f"relief {r['tag']} set {sp:g} bar g exceeds design {lo[0]:g} bar g of {lo[1]} on the same sheet", where))
        if "not sized" in r["sizing_status"]: F.append(Finding("P20", "A", n, r["tag"], f"relief {r['tag']} capacity not sized", "needs vendor data / standard not obtained"))
    for i in regs.inst:   # P30: a high-pressure trip set above the design pressure of the equipment it protects
        if i["function"] in ("PAHH", "PAH") and re.search(r"bar", i["alarm_trip"]):
            ed = [M.design_bar_g(e) for e in regs.equip if e["tag"] == i["equipment"]]; tp = M.first_number(i["alarm_trip"])
            if ed and ed[0] is not None and tp is not None and tp > ed[0] + 1e-9:
                F.append(Finding("P30", "E", i["sheet"], i["tag"], f"{i['tag']} trips at {tp:g} bar, above the design pressure {ed[0]:g} bar g of {i['equipment']}", f"{_area_module(i['sheet'])} (interlocks / design of {i['equipment']})"))
    for v in regs.valves:
        n = int(v["sheet"]); where = f"{_area_module(n)} (blockv/valve call for {v['tag']})"
        if v["type"] == "control" and v["fail_position"] in ("", "-") and n in U and U[n].A_relief:
            F.append(Finding("P07", "E", n, v["tag"], f"control valve {v['tag']} on a sheet with a relief device has no fail action", where))
        if "ESD" in v["fail_position"] and not re.match(r"^(FC|FO) \(ESD\)$", v["fail_position"].strip()):
            F.append(Finding("P09", "E", n, v["tag"], f"ESD valve {v['tag']} fail action {v['fail_position']!r} is not FC (ESD) / FO (ESD)", where))
    for n, u in U.items():
        if u.A_relief: F.append(Finding("P22", "A", n, "", f"unit sheet {n}: capacity-determining (>25 % of device capacity) screen not performed", "needs relief-case calculations"))
    return sorted(F, key=lambda f: (f.sev, f.code, str(f.sheet), f.tag))


def fix(pkg):
    """redraw every PSFS sheet from the registers; returns the findings after the redraw"""
    urea_psfs.remove(pkg); urea_psfs.apply(pkg)
    pkg.sheets.sort(key=lambda s: s.no); pkg.total = len(pkg.sheets)
    return lint(pkg)


def summary(F):
    c = collections.Counter((f.sev, f.code) for f in F)
    return ", ".join(f"{s}:{k}={n}" for (s, k), n in sorted(c.items()))


def report_md(F, title="PSFS lint report"):
    err = [f for f in F if f.sev == "E"]; adv = [f for f in F if f.sev == "A"]
    L = [f"# {title}", "", f"{len(err)} error(s), {len(adv)} advisory(ies). Rules are listed in the header of `scripts/psfs_lint.py`.", ""]
    L += ["## Errors", ""] + ([f"- **{f.code}** sheet {f.sheet} `{f.tag}`: {f.msg}. Fix: {f.fix}" for f in err] or ["none"])
    ac = collections.Counter(f.code for f in adv)
    L += ["", "## Advisories (counts)", ""] + [f"- **{k}**: {n}" for k, n in sorted(ac.items())]
    L += ["", "Advisories are open engineering gaps, not drawing mistakes (capacity not sized, set pressure by vendor, >25 % screen not performed)."]
    return "\n".join(L) + "\n"


def main():
    argv = sys.argv[1:]
    import gen_pid_urea_package as G
    pkg = G.build_package()[0]
    F = lint(pkg); print("lint:", summary(F))
    if "--fix" in argv:
        n0 = len([f for f in F if f.sev == "E"]); F = fix(pkg); print(f"fix: errors {n0} -> {len([f for f in F if f.sev == 'E'])};", summary(F))
    for f in [f for f in F if f.sev == "E"][:60]: print(f"  ERROR {f.code} sheet {f.sheet} {f.tag}: {f.msg}  [fix: {f.fix}]")
    if "--report" in argv: open(argv[argv.index("--report") + 1], "w").write(report_md(F))
    if "--json" in argv: json.dump([f._asdict() for f in F], open(argv[argv.index("--json") + 1], "w"), indent=1)
    errs = [f for f in F if f.sev == "E"]
    return 1 if errs or ("--strict" in argv and F) else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Assemble the coal-to-urea unit-by-unit P&ID package (Talcher-class, 3,850 t/d urea) from the area modules urea_area_NN.py.

Usage: python3 scripts/gen_pid_urea_package.py <out.html> [--previews] [--registers <dir>] [--areas 10,20,...]

Runs every area's build(pkg), then a whole-package lint (duplicate tags, relief destinations, stream registry, loop-number collisions,
ESD valve per sheet, line-size and velocity sanity), writes one printable HTML and the registers (line list, instrument index, equipment
list, relief schedule, valve list, stream table). Conceptual, screening basis, not for construction.
"""
import sys, os, importlib, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *

AREAS = ["10", "20", "30", "40", "50", "60", "70", "80", "90"]
AREA_NAMES = {"10": "Coal and petcoke handling", "20": "Air separation", "30": "Gasification and water systems", "40": "Shift and heat recovery",
              "50": "Acid gas removal, sulphur, methanation", "60": "Ammonia synthesis and storage", "70": "Urea synthesis and finishing",
              "80": "Utilities", "90": "Offsites and safety systems"}


def lint(pkg):
    """returns (errors, advisories). Errors: duplicate tags/numbers, missing relief destination, unregistered stream. Advisories: sheet without ESD valve
    (many utility/solids sheets legitimately have none, the area notes say where), gas velocity above 60 m/s (large air/N2 lines are ducts, pipe table stops at 48 in)"""
    out = []; adv = []
    tags = collections.Counter(r[0] for r in pkg.equip)
    for t, n in tags.items():
        if n > 1: out.append(f"duplicate equipment tag {t} x{n}")
    for r in pkg.relief:
        if not r[5]: out.append(f"relief {r[0]} has no destination")
    sid = {k[0] for k in STREAMS}
    for r in pkg.lines:
        if str(r[4]) not in sid: out.append(f"line {r[0]} stream {r[4]} not in registry")
    inst = collections.Counter(r[0] for r in pkg.inst)
    for t, n in inst.items():
        if n > 1: out.append(f"duplicate instrument tag {t} x{n}")
    vt = collections.Counter(r[0] for r in pkg.valves)
    for t, n in vt.items():
        if n > 1 and t != "-": out.append(f"duplicate valve tag {t} x{n}")
    lines = collections.Counter(r[0] for r in pkg.lines)
    for t, n in lines.items():
        if n > 1: out.append(f"duplicate line number {t} x{n}")
    for sh in pkg.sheets:
        if not any(r[6] == sh.no and "ESD" in str(r[5]) for r in pkg.valves): adv.append(f"sheet {sh.no} has no ESD valve")
    for r in pkg.lines:
        try:
            if float(r[10]) > 60: adv.append(f"line {r[0]} velocity {r[10]} m/s (> 60) on sheet {r[-1]}")
        except ValueError: pass
    return out, adv


def main():
    argv = sys.argv[1:]
    out = argv[0] if argv and not argv[0].startswith("--") else "urea_package.html"
    areas = argv[argv.index("--areas") + 1].split(",") if "--areas" in argv else AREAS
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class): unit-by-unit conceptual P&IDs",
              f"Rev B balance x{K:.4f}; capacity ICRA Feb 2025 / PIB 2026; areas 10-90", rev="C0")
    built = []
    for a in areas:
        try: m = importlib.import_module(f"urea_area_{a}")
        except ModuleNotFoundError: print(f"area {a}: module not present, skipped"); continue
        n0 = len(pkg.sheets); m.build(pkg); built.append((a, len(pkg.sheets) - n0))
    pkg.sheets.sort(key=lambda sh: sh.no); pkg.total = len(pkg.sheets)
    nos = [sh.no for sh in pkg.sheets]; assert len(nos) == len(set(nos)), "duplicate sheet numbers"
    problems, adv = lint(pkg)
    write_html(pkg.sheets, out, "Coal-to-urea unit-by-unit P&IDs (Rev C0)", previews="--previews" in argv)
    if "--registers" in argv: pkg.write_registers(argv[argv.index("--registers") + 1])
    print("areas:", ", ".join(f"{a}={n}" for a, n in built))
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief, {len(pkg.valves)} valves, {len(STREAMS)} streams")
    print(f"lint: {len(problems)} error(s), {len(adv)} advisory(ies)")
    for p in problems[:60]: print("  ERROR -", p)
    for p in adv[:80]: print("  advisory -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

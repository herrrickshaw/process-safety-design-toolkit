#!/usr/bin/env python3
"""Assemble the coal-to-urea unit-by-unit P&ID package (Talcher-class, 3,850 t/d urea) from the area modules urea_area_NN.py.

Usage: python3 scripts/gen_pid_urea_package.py <out.html> [--previews] [--registers <dir>] [--areas 10,20,...]

Runs every area's build(pkg), then a whole-package lint (duplicate tags, relief destinations, stream registry, loop-number collisions,
ESD valve per sheet, line-size and velocity sanity), writes one printable HTML and the registers (line list, instrument index, equipment
list, relief schedule, valve list, stream table). Conceptual, screening basis, not for construction.
"""
import sys, os, importlib, collections, re, html
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
import urea_safety, urea_psfs

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
        if getattr(sh, "docs", False): continue
        if not any(r[6] == sh.no and "ESD" in str(r[5]) for r in pkg.valves): adv.append(f"sheet {sh.no} has no ESD valve")
    for r in pkg.lines:
        try:
            if float(r[10]) > 60: adv.append(f"line {r[0]} velocity {r[10]} m/s (> 60) on sheet {r[-1]}")
        except ValueError: pass
    return out, adv


TXT = re.compile(r'<text x="([-\d.]+)" y="([-\d.]+)" font-size="([\d.]+)" font-weight="(\d+)" text-anchor="(\w+)"[^>]*>([^<]*)</text>')


def text_boxes(sh):
    """approximate bounding boxes of every text element of a sheet (width = chars x size x 0.52, bold 0.56; screening estimate)"""
    out = []
    for e in sh.p:
        for x, y, sz, w, an, tx in TXT.findall(e):
            x, y, sz = float(x), float(y), float(sz); tx = html.unescape(tx)
            wd = len(tx) * sz * (0.56 if int(w) >= 600 else 0.52)
            x0 = x - wd if an == "end" else x - wd / 2 if an == "middle" else x
            out.append((x0, y - sz * 0.8, x0 + wd, y + sz * 0.25, tx))
    return out


def overlaps(sh, min_area=6.0):
    """pairs of text boxes that overlap by more than min_area px2, and boxes that leave the sheet frame (1600 x 1130)"""
    b = [x for x in text_boxes(sh) if x[1] > 80]; bad = []   # header band excluded (title font is shrunk at render time)
    for i in range(len(b)):
        for j in range(i + 1, len(b)):
            a, c = b[i], b[j]
            w = min(a[2], c[2]) - max(a[0], c[0]); h = min(a[3], c[3]) - max(a[1], c[1])
            if w > 0 and h > 0 and w * h > min_area and a[4] != c[4]: bad.append((a[4][:28], c[4][:28]))
    out = [f"{t[:28]!r} leaves the frame" for t in (x[4] for x in b if x[2] > 1592 or x[0] < 8 or x[3] > 1122)]
    return bad, out


def build_package(areas=None, safety=True, psfs=True):
    """run the area builders, the safety overlay and the PSFS sheets; returns (pkg, built, safety stats, psfs stats)"""
    areas = areas or AREAS
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class): unit-by-unit conceptual P&IDs",
              f"Rev C rebased balance x{K:.4f}; capacity ICRA Feb 2025 / PIB 2026; areas 10-90", rev="C2")
    built = []
    for a in areas:
        try: m = importlib.import_module(f"urea_area_{a}")
        except ModuleNotFoundError: print(f"area {a}: module not present, skipped"); continue
        n0 = len(pkg.sheets); m.build(pkg); built.append((a, len(pkg.sheets) - n0))
    st = urea_safety.apply(pkg) if safety else {}
    pf = urea_psfs.apply(pkg) if psfs else {}
    pkg.sheets.sort(key=lambda sh: sh.no); pkg.total = len(pkg.sheets)
    nos = [sh.no for sh in pkg.sheets]; assert len(nos) == len(set(nos)), "duplicate sheet numbers"
    return pkg, built, st, pf


def main():
    argv = sys.argv[1:]
    if "--labels" in argv:      # record every drawn symbol with its bounding box (detector training data); must be installed before the area modules draw
        import pid_rec; pid_rec.install()
    out = argv[0] if argv and not argv[0].startswith("--") else "urea_package.html"
    areas = argv[argv.index("--areas") + 1].split(",") if "--areas" in argv else AREAS
    pkg, built, safety, psfs = build_package(areas, safety="--no-safety" not in argv, psfs="--no-psfs" not in argv)
    problems, adv = lint(pkg)
    write_html(pkg.sheets, out, "Coal-to-urea unit-by-unit P&IDs (Rev C2)", previews="--previews" in argv)
    if "--labels" in argv:
        import json, pid_rec
        os.makedirs(argv[argv.index("--labels") + 1], exist_ok=True)
        lab = {str(sh.no): pid_rec.BOXES.get(id(sh), []) for sh in pkg.sheets}
        json.dump(lab, open(os.path.join(argv[argv.index("--labels") + 1], "labels.json"), "w"))
        print("symbol labels:", sum(len(v) for v in lab.values()), "on", sum(1 for v in lab.values() if v), "sheets")
    if "--registers" in argv: pkg.write_registers(argv[argv.index("--registers") + 1])
    print("areas:", ", ".join(f"{a}={n}" for a, n in built))
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief, {len(pkg.valves)} valves, {len(STREAMS)} streams")
    ov = {sh.no: overlaps(sh) for sh in pkg.sheets}
    tot = sum(len(v[0]) for v in ov.values()); worst = sorted(ov.items(), key=lambda kv: -len(kv[1][0]) - len(kv[1][1]))[:15]
    print(f"text overlaps: {tot} pairs on {sum(1 for v in ov.values() if v[0])} sheets; frame overruns: {sum(len(v[1]) for v in ov.values())}")
    for no, (a, b) in worst:
        if a or b: print(f"  sheet {no}: {len(a)} overlaps, {len(b)} overruns; e.g. {a[0] if a else b[0]}")
    print("safety overlay:", safety); print("PSFS:", {k: v for k, v in psfs.items() if k != "areas"}, "units/PSV/ESD/trips by area:", psfs.get("areas"))
    print(f"lint: {len(problems)} error(s), {len(adv)} advisory(ies)")
    for p in problems[:60]: print("  ERROR -", p)
    for p in adv[:80]: print("  advisory -", p)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Randomised synthetic P&ID sheets drawn with the toolkit's pidlib symbols, with exact symbol labels from pid_rec.

Why: the unit-by-unit urea package gives 2,651 exactly labelled symbols but only 52 pumps and 67 tanks, the two classes the detector misses on real drawings.
This generator places many pumps, vessels, tanks, compressors, valves, relief valves and instrument bubbles on jittered grids joined by orthogonal lines,
with random line weights, valve kinds and label text, so the rare classes are well covered. Conceptual training data only: symbols are the toolkit's own glyphs.
Usage: python3 synth_pid_sheets.py <out.html> <labels.json> [n_sheets] [seed]  (writes <out>_s<no>.html previews, 1600 x 1130 each)"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, "..", "..", "scripts"))
import pid_rec; pid_rec.install()
import pidlib as P


def sheet(no, rnd):
    s = P.Sheet(no, "synthetic", "training sheet", code="SYN")
    sw = rnd.choice([1.6, 2.0, 2.6, 3.0]); cw, ch = rnd.choice([(210, 190), (240, 210), (190, 170)])
    cols, rows = (1560 // cw), (1000 // ch)
    cells = [(c, r) for c in range(cols) for r in range(rows)]; rnd.shuffle(cells)
    kinds = ["pump"] * 5 + ["hvessel"] * 2 + ["vvessel"] * 2 + ["tank"] * 2 + ["compressor"] + ["reactor"] + ["hx"]
    placed = []
    for (c, r) in cells[: rnd.randint(int(len(cells) * 0.5), int(len(cells) * 0.85))]:
        k = rnd.choice(kinds); x = 40 + c * cw + cw // 2 + rnd.randint(-14, 14); y = 100 + r * ch + ch // 2 + rnd.randint(-12, 12)
        if k == "pump": P.pump(s, x, y, rnd.choice([12, 14, 16]), f"P-{rnd.randint(100, 999)}{rnd.choice('AB')}")
        elif k == "hvessel": P.hvessel(s, x, y, rnd.randint(70, 110), rnd.randint(34, 50), f"V-{rnd.randint(100, 999)}")
        elif k == "vvessel": P.vvessel(s, x, y - 50, rnd.randint(34, 56), rnd.randint(70, 100), f"C-{rnd.randint(100, 999)}", trays=rnd.choice([0, 0, 4]))
        elif k == "tank": P.tank(s, x, y + 40, rnd.randint(60, 90), rnd.randint(50, 70), f"T-{rnd.randint(100, 999)}", roof=rnd.choice(["cone", "dome", "floating"]))
        elif k == "compressor": P.compressor(s, x, y, rnd.choice([15, 17, 20]), f"K-{rnd.randint(100, 999)}")
        elif k == "reactor": P.reactor(s, x, y, rnd.randint(40, 60), rnd.randint(60, 90), f"R-{rnd.randint(100, 999)}")
        else: P.hx(s, x, y, rnd.randint(64, 90), 26, f"E-{rnd.randint(100, 999)}")
        placed.append((x, y, k))
        # lines and fittings around it
        ln = rnd.randint(46, 80); yl = y + rnd.choice([0, -8, 8])
        P.PL(s, [(x - 120, yl), (x - ln, yl)], sw); P.PL(s, [(x + ln, yl), (x + 120, yl)], sw)
        for vx in (x - 100, x + 100):
            if rnd.random() < 0.8: P.valve(s, vx, yl, 0, rnd.choice(["gate", "gate", "ball", "check"]), rnd.random() < 0.2)
        if rnd.random() < 0.55: P.ctrlvalve(s, x + rnd.randint(70, 100), yl) if rnd.random() < 0.3 else None
        if rnd.random() < 0.7: P.bubble(s, x + rnd.randint(-30, 30), y - rnd.randint(55, 75), rnd.choice(["LIC", "PIC", "TIC", "FI", "LT", "PT", "TAHH", "LAHH"]), str(rnd.randint(1000, 9999)), rnd.random() < 0.3, P.INK, rnd.choice([11, 13, 15]))
        if rnd.random() < 0.25: P.psv(s, x + rnd.randint(-20, 20), y - rnd.randint(70, 90))
        if rnd.random() < 0.3: P.valve(s, x - 3, y + rnd.randint(52, 64), 90, "gate")
        if rnd.random() < 0.4: P.T(s, x - 100, yl - 14, f"{rnd.choice([2, 3, 4, 6, 8])}\"-{rnd.choice(['PL', 'PG', 'CW', 'ST'])}-{rnd.randint(1000, 9999)}-A1", 9)
    return s


def main():
    out, labf = sys.argv[1], sys.argv[2]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 200; rnd = random.Random(int(sys.argv[4]) if len(sys.argv) > 4 else 7)
    sheets = [sheet(i + 1, rnd) for i in range(n)]
    for sh in sheets:     # no frame: a bare drawing area, like a cropped sheet; title/frame text would add unlabelled clutter
        pass
    P.write_html(sheets, out, "synthetic P&ID training sheets", previews=True)
    json.dump({str(sh.no): pid_rec.BOXES.get(id(sh), []) for sh in sheets}, open(labf, "w"))
    import collections
    c = collections.Counter(b[0] for sh in sheets for b in pid_rec.BOXES.get(id(sh), [])); print("sheets", n, dict(c))


if __name__ == "__main__": main()

#!/usr/bin/env python3
"""pidlib: small standard-library SVG toolkit for conceptual P&ID / PFD sheets (A3 landscape, 1600 x 1130 user units).
Used by scripts/gen_pid_*.py. Draws symbols and tables; it holds no process data. Every number on a sheet must come from
the generator that calls it (sourced, derived, or marked as an assumption)."""
import html, math, textwrap, sys, os

W, H = 1600, 1130
FONT = "Helvetica, Arial, sans-serif"
INK = "#111"; RED = "#c62828"; BLUE = "#1565c0"; GREY = "#666"; GREEN = "#2e7d32"; AMBER = "#b26a00"
DATE = "11 Nov 2026"


def esc(s): return html.escape(str(s), quote=False)


class Sheet:
    def __init__(self, no, title, sub, code="VS-PID", project="Propane / n-butane loss of containment (PR 7)",
                 basis="Final summary + calc workbook, 10 Nov 2026"):
        self.no, self.title, self.sub = no, title, sub
        self.code, self.project, self.basis = code, project, basis
        self.p = []

    def add(self, s): self.p.append(s)

    def svg(self):
        defs = f'''<defs>
<pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" stroke="#b26a00" stroke-width="2"/></pattern>
<linearGradient id="flame" x1="0" y1="1" x2="0" y2="0"><stop offset="0" stop-color="#ffd54f"/><stop offset=".45" stop-color="#ff8f00"/><stop offset="1" stop-color="#d84315"/></linearGradient>
<radialGradient id="ball" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#ffe082"/><stop offset=".6" stop-color="#ff9800"/><stop offset="1" stop-color="#d84315"/></radialGradient>
<marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>
<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{RED}"/></marker>
<marker id="ahb" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{BLUE}"/></marker>
</defs>'''
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="420mm" height="297mm" '
                f'font-family="{FONT}">{defs}<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(self.p) + '</svg>')


# ---------- primitives ----------
def T(s, x, y, t, size=12, weight=400, anchor="start", fill=INK, extra=""):
    s.add(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{fill}" {extra}>{esc(t)}</text>')


def TL(s, x, y, lines, size=12, lh=None, weight=400, fill=INK, anchor="start"):
    lh = lh or size * 1.3
    for i, t in enumerate(lines): T(s, x, y + i * lh, t, size, weight, anchor, fill)


def WRAP(s, x, y, text, width=60, size=11.5, lh=15, fill=INK, weight=400, bullet=False):
    lines = textwrap.wrap(text, width=width)
    for i, t in enumerate(lines):
        T(s, x + (10 if bullet and i > 0 else 0), y + i * lh, (("• " if bullet and i == 0 else "") + t), size, weight, "start", fill)
    return y + len(lines) * lh


def R(s, x, y, w, h, fill="none", stroke=INK, sw=1.2, dash=None, rx=0, op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    o = f' opacity="{op}"' if op else ""
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}{o}/>')


def PL(s, pts, sw=2.6, stroke=INK, dash=None, marker=None, fill="none", op=None):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    m = f' marker-end="url(#{marker})"' if marker else ""
    o = f' opacity="{op}"' if op else ""
    s.add(f'<polyline points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"{d}{m}{o}/>')


def valve(s, x, y, rot=0, kind="gate", act=False, color=INK):
    g = f'<g transform="translate({x},{y}) rotate({rot})" stroke="{color}" stroke-width="1.8" fill="#fff">'
    if kind == "check":
        g += '<polygon points="-9,-7 -9,7 9,0"/><line x1="9" y1="-7" x2="9" y2="7"/>'
    else:
        g += '<polygon points="-11,-7 11,7 11,-7 -11,7"/>'
        if kind == "ball": g += f'<circle r="3.4" fill="{color}"/>'
    if act:
        g += f'<line x1="0" y1="0" x2="0" y2="-15"/><path d="M-9,-15 A9,9 0 0 1 9,-15 Z" fill="#fff"/>'
    s.add(g + "</g>")


def psv(s, x, y, color=INK):
    """angle-type relief valve, inlet below (x,y+18), outlet to the right at y"""
    s.add(f'<g transform="translate({x},{y})" stroke="{color}" stroke-width="1.8" fill="#fff">'
          f'<polygon points="-10,16 10,16 0,-2"/><polygon points="0,-2 18,-10 18,10" />'
          f'<polyline points="0,-2 0,-8 -6,-12 6,-17 -6,-22 6,-27 0,-31" fill="none"/></g>')


def bubble(s, x, y, a, b, panel=False, color=INK, r=15):
    s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" stroke="{color}" stroke-width="1.6"/>')
    if panel: s.add(f'<line x1="{x-r}" y1="{y}" x2="{x+r}" y2="{y}" stroke="{color}" stroke-width="1.2"/>')
    T(s, x, y - 2 if panel else y - 0.5, a, 8 if len(a) > 3 else 9.5, 700, "middle", color)
    T(s, x, y + 10 if panel else y + 9.5, b, 9, 400, "middle", color)


def arrow(s, x, y, d="r", color=INK, size=9):
    pts = {"r": [(x - size, y - size / 2), (x, y), (x - size, y + size / 2)], "l": [(x + size, y - size / 2), (x, y), (x + size, y + size / 2)],
           "d": [(x - size / 2, y - size), (x, y), (x + size / 2, y - size)], "u": [(x - size / 2, y + size), (x, y), (x + size / 2, y + size)]}[d]
    s.add(f'<polygon points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="{color}"/>')


def star(s, x, y, r=22, fill="#ffeb3b", stroke=RED):
    pts = []
    for i in range(16):
        rr = r if i % 2 == 0 else r * 0.5
        a = math.pi * i / 8
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a)))
    s.add(f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')


def flame(s, x, y, ang_deg, length, width=34, op=0.95):
    """teardrop flame from base (x,y), leaning ang_deg from vertical to the right"""
    a = math.radians(ang_deg); ux, uy = math.sin(a), -math.cos(a); px, py = -uy, ux
    def P(t, w): return (x + ux * t + px * w, y + uy * t + py * w)
    b1, b2 = P(0, -width * .25), P(0, width * .25)
    m1, m2 = P(length * .45, -width * .5), P(length * .45, width * .5)
    tip = P(length, 0)
    s.add(f'<path d="M{b1[0]:.1f},{b1[1]:.1f} Q{m1[0]:.1f},{m1[1]:.1f} {tip[0]:.1f},{tip[1]:.1f} Q{m2[0]:.1f},{m2[1]:.1f} {b2[0]:.1f},{b2[1]:.1f} Z" '
          f'fill="url(#flame)" stroke="{RED}" stroke-width="1.2" opacity="{op}" transform="rotate(0)"/>')


def table(s, x, y, colw, rows, rh=19, size=11, head=True, bold_first_col=False, zebra=True, fills=None):
    tw = sum(colw)
    for i, r in enumerate(rows):
        yy = y + i * rh
        if head and i == 0: R(s, x, yy, tw, rh, "#e8eaf0", "none")
        elif zebra and i % 2 == 0: R(s, x, yy, tw, rh, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(r):
            wgt = 700 if (head and i == 0) or (bold_first_col and j == 0) else 400
            T(s, cx + 4, yy + rh - 6, c, size, wgt)
            cx += colw[j]
    R(s, x, y, tw, rh * len(rows), "none", "#9aa", 1)
    return y + rh * len(rows)


def section(s, x, y, w, title, color="#1a237e"):
    R(s, x, y, w, 22, color, "none")
    T(s, x + 8, y + 16, title, 12.5, 700, fill="#fff")
    return y + 22


# ---------- frame, header, title block ----------
def frame(s, total=6):
    R(s, 8, 8, W - 16, H - 16, "none", INK, 2.2)
    R(s, 8, 8, W - 16, 66, "#0d1b3e", "none")
    T(s, 24, 38, "VertiStrat Solutions LLP", 13, 700, fill="#9fb4ff")
    T(s, 24, 62, s.title, 21, 700, fill="#fff")
    T(s, W - 24, 38, f"Sheet {s.no} of {total}  |  Drawing {s.code}-00{s.no}  |  Rev A", 13, 400, "end", "#fff")
    T(s, W - 24, 62, "CONCEPTUAL P&ID - SCREENING BASIS - NOT FOR CONSTRUCTION", 13, 700, "end", "#ffcc80")
    # title block
    x, y, w = 1135, 960, 445
    R(s, x, y, w, 140, "#fff", INK, 1.6)
    rows = [("Project", s.project), ("Sheet", s.sub),
            ("Basis", s.basis), ("Prepared", f"Claude Sonnet 5.5 for owner review, {DATE}"),
            ("Status", "Draft A. Screening aid, not certified design")]
    for i, (a, b) in enumerate(rows):
        yy = y + 8 + i * 25
        T(s, x + 8, yy + 13, a, 10.5, 700, fill=GREY)
        WRAP(s, x + 70, yy + 13, b, 58, 11, 12)
        if i < 4: PL(s, [(x, yy + 24), (x + w, yy + 24)], 0.6, "#bbb")


def panel_box(s, x=1135, y=84, w=445, h=866):
    R(s, x, y, w, h, "#fff", INK, 1.2)



def legend_mini(s, x, y):
    items = [("process line", INK, None), ("ESD output", RED, "6 4"), ("instrument signal", BLUE, "5 4")]
    for i, (t, c, d) in enumerate(items):
        PL(s, [(x, y + i * 14), (x + 30, y + i * 14)], 2 if c == INK else 1.4, c, d)
        T(s, x + 36, y + 4 + i * 14, t, 9.5)
    s.add(f'<rect x="{x+150}" y="{y-6}" width="30" height="10" fill="url(#hatch)"/>'); T(s, x + 186, y + 4, "jet-rated PFP (R)", 9.5)
    T(s, x + 150, y + 22, "R = recommended in summary (slide 10)", 9.5); T(s, x + 150, y + 35, "A = assumed by this drawing", 9.5)



# ---------- equipment symbols (return a dict of connection ports) ----------
def hvessel(s, cx, cy, w, h, label=None, sub=None, fill="#fff", hatch=False):
    """horizontal drum with elliptical heads; w = tangent length, h = diameter"""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    e = h * 0.3
    d = f"M{x0},{y0} H{x1} A{e},{h/2} 0 0 1 {x1},{y1} H{x0} A{e},{h/2} 0 0 1 {x0},{y0} Z"
    s.add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="2.4"/>')
    for sx in (x0 + w * 0.2, x1 - w * 0.2):
        s.add(f'<polygon points="{sx-h*0.12},{y1} {sx+h*0.12},{y1} {sx+h*0.2},{y1+h*0.25} {sx-h*0.2},{y1+h*0.25}" fill="#eee" stroke="{INK}" stroke-width="1.3"/>')
    if label: T(s, cx, cy - 2, label, 11, 700, "middle")
    if sub: T(s, cx, cy + 11, sub, 9.5, 400, "middle")
    return dict(top=(cx, y0), bottom=(cx, y1), left=(x0 - e, cy), right=(x1 + e, cy), cx=cx, cy=cy, x0=x0, x1=x1, y0=y0, y1=y1)


def vvessel(s, cx, top, w, h, label=None, sub=None, trays=0, fill="#fff", packing=False):
    """vertical vessel / column with elliptical heads; top = y of top tangent line"""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, top, top + h
    e = w * 0.28
    d = f"M{x0},{y0} A{w/2},{e} 0 0 1 {x1},{y0} V{y1} A{w/2},{e} 0 0 1 {x0},{y1} Z"
    s.add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="2.4"/>')
    if trays:
        gap = (h - 20) / (trays + 1)
        for i in range(1, trays + 1):
            yy = y0 + 10 + i * gap
            PL(s, [(x0 + 3, yy), (x1 - 3, yy)], 1.1, "#555")
    if packing:
        s.add(f'<rect x="{x0+3}" y="{y0+h*0.25}" width="{w-6}" height="{h*0.5}" fill="url(#hatch)" opacity=".5"/>')
    if label: T(s, cx, y1 + e + 16, label, 11, 700, "middle")
    if sub: T(s, cx, y1 + e + 29, sub, 9.5, 400, "middle")
    return dict(top=(cx, y0 - e), bottom=(cx, y1 + e), left=(x0, (y0 + y1) / 2), right=(x1, (y0 + y1) / 2), cx=cx, y0=y0, y1=y1, x0=x0, x1=x1, w=w)


def tank(s, cx, base, w, h, label=None, sub=None, roof="cone", level=0.7, liquid="#cfe6f7"):
    """atmospheric storage tank; base = y of the floor line"""
    x0, x1, y0 = cx - w / 2, cx + w / 2, base - h
    s.add(f'<rect x="{x0}" y="{base-h*level}" width="{w}" height="{h*level}" fill="{liquid}"/>')
    s.add(f'<polyline points="{x0},{base} {x0},{y0} {x1},{y0} {x1},{base}" fill="none" stroke="{INK}" stroke-width="2.4"/>')
    PL(s, [(x0 - 6, base), (x1 + 6, base)], 2.4)
    if roof == "cone": PL(s, [(x0, y0), (cx, y0 - h * 0.14), (x1, y0)], 2.2)
    elif roof == "dome": s.add(f'<path d="M{x0},{y0} Q{cx},{y0-h*0.3} {x1},{y0}" fill="none" stroke="{INK}" stroke-width="2.2"/>')
    elif roof == "floating": PL(s, [(x0, y0 + h * 0.08), (x1, y0 + h * 0.08)], 2.6, AMBER)
    if label: T(s, cx, base + 15, label, 11, 700, "middle")
    if sub: T(s, cx, base + 28, sub, 9.5, 400, "middle")
    return dict(top=(cx, y0 - h * 0.14), bottom=(cx, base), left=(x0, base - h * 0.2), right=(x1, base - h * 0.2), cx=cx, x0=x0, x1=x1, y0=y0, base=base)


def reactor(s, cx, cy, w, h, label=None, sub=None, jacket=False, fill="#fff", agitator=True, dome=False):
    """stirred vessel (CSTR / fermenter / digester): body, optional jacket, agitator and motor"""
    x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    e = w * 0.2
    d = f"M{x0},{y0} A{w/2},{e} 0 0 1 {x1},{y0} V{y1} A{w/2},{e} 0 0 1 {x0},{y1} Z"
    if jacket: s.add(f'<path d="M{x0-6},{cy-h*0.1} V{y1-4} A{w/2+6},{e+4} 0 0 0 {x1+6},{y1-4} V{cy-h*0.1}" fill="none" stroke="{AMBER}" stroke-width="2"/>')
    s.add(f'<path d="{d}" fill="{fill}" stroke="{INK}" stroke-width="2.4"/>')
    if dome: s.add(f'<path d="M{x0},{y0} A{w/2},{w*0.38} 0 0 1 {x1},{y0}" fill="#f3e5f5" stroke="{INK}" stroke-width="2"/>')
    if agitator:
        PL(s, [(cx, y0 - e - 8), (cx, y1 - h * 0.15)], 2)
        PL(s, [(cx - w * 0.22, y1 - h * 0.15), (cx + w * 0.22, y1 - h * 0.15)], 3)
        s.add(f'<circle cx="{cx}" cy="{y0-e-18}" r="9" fill="#fff" stroke="{INK}" stroke-width="1.6"/><text x="{cx}" y="{y0-e-14.5}" font-size="9" font-weight="700" text-anchor="middle">M</text>')
    if label: T(s, cx, y1 + e + 16, label, 11, 700, "middle")
    if sub: T(s, cx, y1 + e + 29, sub, 9.5, 400, "middle")
    return dict(top=(cx, y0 - e), bottom=(cx, y1 + e), left=(x0, cy), right=(x1, cy), cx=cx, cy=cy, x0=x0, x1=x1, y0=y0, y1=y1)


def pump(s, cx, cy, r=14, label=None, color=INK):
    """centrifugal pump: suction left, discharge up"""
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{color}" stroke-width="2"/>')
    s.add(f'<polygon points="{cx-r*0.7},{cy-r*0.7} {cx+r*0.7},{cy-r*0.7} {cx},{cy+r*0.3}" fill="none" stroke="{color}" stroke-width="1.4" transform="rotate(-90 {cx} {cy})"/>')
    PL(s, [(cx, cy - r), (cx + r, cy - r)], 2, color)
    if label: T(s, cx, cy + r + 13, label, 10, 700, "middle")
    return dict(inlet=(cx - r, cy), outlet=(cx + r, cy - r), cx=cx, cy=cy)


def compressor(s, cx, cy, r=17, label=None):
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    PL(s, [(cx - r * 0.7, cy - r * 0.7), (cx + r * 0.9, cy - r * 0.35)], 1.8)
    PL(s, [(cx - r * 0.7, cy + r * 0.7), (cx + r * 0.9, cy + r * 0.35)], 1.8)
    if label: T(s, cx, cy + r + 13, label, 10, 700, "middle")
    return dict(inlet=(cx - r, cy), outlet=(cx + r, cy), cx=cx, cy=cy)


def hx(s, cx, cy, w=80, h=28, label=None, sub=None, color=INK):
    """shell-and-tube exchanger, horizontal"""
    x0, y0 = cx - w / 2, cy - h / 2
    s.add(f'<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="{h/2}" fill="#fff" stroke="{color}" stroke-width="2"/>')
    pts = [(x0 + 4, cy)]
    for i in range(1, 6): pts.append((x0 + w * i / 6, cy + (-1) ** i * h * 0.28))
    pts.append((x1 := x0 + w - 4, cy))
    PL(s, pts, 1.3, color)
    if label: T(s, cx, y0 - 6, label, 10, 700, "middle")
    if sub: T(s, cx, cy + h / 2 + 13, sub, 9, 400, "middle")
    return dict(left=(x0, cy), right=(x0 + w, cy), top=(cx, y0), bottom=(cx, cy + h / 2), cx=cx, cy=cy)


def ctrlvalve(s, x, y, rot=0, color=INK):
    """control valve: bowtie with diaphragm actuator"""
    valve(s, x, y, rot, "gate", act=True, color=color)


def flare(s, x, base, h=120, label="Flare"):
    PL(s, [(x, base), (x, base - h)], 4)
    flame(s, x, base - h, 5, 30, 14)
    T(s, x + 10, base - h + 18, label, 10, 700)
    return dict(inlet=(x, base))


def strm(s, x, y, n, color=INK):
    """stream-number marker (diamond); pair with an HMB column of the same number"""
    s.add(f'<polygon points="{x},{y-11} {x+11},{y} {x},{y+11} {x-11},{y}" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
    T(s, x, y + 3.5, str(n), 9.5 if len(str(n)) < 3 else 8, 700, "middle", color)


def pipe(s, pts, sw=2.6, color=INK, arrow_=True, dash=None, op=None):
    """process line; arrowhead at the end of the last segment"""
    PL(s, pts, sw, color, dash, None, "none", op)
    if arrow_ and len(pts) >= 2:
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        if abs(xb - xa) >= abs(yb - ya): arrow(s, xb, yb, "r" if xb > xa else "l", color)
        else: arrow(s, xb, yb, "d" if yb > ya else "u", color)


def hmb_table(s, x, y, labels, rows, first_w=190, col_w=None, rh=17, size=9.5, title=None, max_w=None):
    """Heat-and-material-balance stream table. labels = list of column headers (stream numbers),
    rows = list of (property label, [values...]) ; section rows: (label, None). Returns the y below the table."""
    n = len(labels)
    col_w = col_w or max(46, min(78, ((max_w or 1100) - first_w) / max(n, 1)))
    tw = first_w + col_w * n
    if title: y = section(s, x, y, tw, title)
    R(s, x, y, tw, rh, "#e8eaf0", "none")
    T(s, x + 4, y + rh - 5, "Stream", size, 700)
    for j, lb in enumerate(labels): T(s, x + first_w + col_w * j + col_w / 2, y + rh - 5, str(lb), size, 700, "middle")
    yy = y + rh
    for i, (lab, vals) in enumerate(rows):
        if vals is None:
            R(s, x, yy, tw, rh, "#dfe3ee", "none"); T(s, x + 4, yy + rh - 5, lab, size, 700, fill="#1a237e")
        else:
            if i % 2 == 0: R(s, x, yy, tw, rh, "#f6f7fa", "none")
            T(s, x + 4, yy + rh - 5, lab, size, 400)
            for j, v in enumerate(vals): T(s, x + first_w + col_w * j + col_w / 2, yy + rh - 5, v, size, 400, "middle")
        yy += rh
    R(s, x, y, tw, yy - y, "none", "#9aa", 1)
    return yy


def write_html(sheets, out, title, previews=False):
    """write one printable HTML (A3 landscape pages); print to PDF with a headless browser"""
    css = ("@page{size:420mm 297mm;margin:0}html,body{margin:0;background:#cfd3da}"
           ".sheet{width:420mm;height:297mm;margin:0 auto 10mm;background:#fff;page-break-after:always;break-after:page;overflow:hidden}"
           "@media print{html,body{background:#fff}.sheet{margin:0}}svg{display:block}")
    body = "".join(f'<section class="sheet" id="s{sh.no}">{sh.svg()}</section>' for sh in sheets)
    with open(out, "w") as f:
        f.write(f'<!doctype html><html><head><meta charset="utf-8"><title>{esc(title)}</title><style>{css}</style></head><body>{body}</body></html>')
    if previews:  # one 1600 x 1130 px page per sheet, for screenshots
        for sh in sheets:
            with open(out.replace(".html", f"_s{sh.no}.html"), "w") as f:
                f.write('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0}svg{display:block;width:1600px;height:1130px}</style></head><body>'
                        + sh.svg().replace(' width="420mm" height="297mm"', "") + "</body></html>")

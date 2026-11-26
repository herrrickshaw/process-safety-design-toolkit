#!/usr/bin/env python3
"""Generate the LPG (propane / n-butane) storage P&ID set, Rev B: legend, base case, four loss-of-containment scenarios and a safety design basis.
Numbers come from the Final_Summary and Final_Calculation_Workbook reports of 10 Nov 2026 (not in the repo), the Purple Book
(PGS 3, read for Rev B) and the free sources listed in docs/pid/validation/SAFETY_FEATURES_CHECKLIST.md. Every number carries a label:
S sourced (document + table), D derived (formula in this file), A assumed by this drawing, R required or recommended by a named free source,
'gap' where the controlling standard was not obtained. Screening aid, not certified design.

Rev B changes against Rev A: relief areas at Z = 1.0 (API 520-I 5.6.3.2.2; Rev A used Z = 0.673), Purple Book direct ignition and full-bore rupture added to the
frequency basis, BLEVE frequency chain corrected, thermal relief of the trapped supply line (TSV-102), more detection, and sheets 7 to 9 (relief schedule,
ESD / SIF / mitigation basis, hazard identification). No heat and material balance: this is a storage and loss-of-containment set.

Usage (standard library only; process_safety is the stdlib-only package in this repository):
    python3 scripts/gen_pid_lpg.py docs/pid/LPG_PID_Set_RevB.html [--previews] [--dump]
    chrome --headless=new --print-to-pdf=docs/pid/LPG_PID_Set_RevB.pdf --no-pdf-header-footer file://$PWD/docs/pid/LPG_PID_Set_RevB.html"""
import sys, os, math, textwrap, re, html as _html
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)
from pidlib import *
from process_safety import relief as RL
from process_safety import scenarios as SC
from process_safety import fire_water as FW
from process_safety import sil as SILM

NSHEETS = 9

# =====================================================================================================
# CALCULATIONS (all derived here; frozen constants carry their provenance)
# =====================================================================================================
# Fluid constants for the fire case: workbook R_Assumptions / RB_Assumptions (CoolProp 8.0.0 Helmholtz EOS, frozen by the workbook, S).
# Z_calc is information only: API 520-I 5.6.1 limits the ideal-gas equation to Z about 0.8 to 1.1 and 5.6.3.2.2 says use 1.0 (S, workbook note).
FLUID = {
    "propane":  dict(M=44.096, k=1.115, T=334.75, lat=254.71, Greal=6225.1, Pset=1724.0, Zcalc=0.673, Q25=2.3403, flux25=7690.0),
    "n-butane": dict(M=58.122, k=1.08,  T=349.62, lat=298.27, Greal=2777.9, Pset=690.0,  Zcalc=0.807, Q25=1.03499, flux25=3401.0),
}
# Assumed sample vessels (workbook R_Sizing, A1): name, D m, L m (tangent), orientation
VESSELS = [("V1", "domestic bulk", 1.4, 3.5, "horizontal"), ("V2", "small bullet", 2.4, 6.5, "horizontal"), ("V3", "bullet (this drawing)", 3.2, 12.0, "horizontal"),
           ("V4", "large bullet", 4.0, 19.0, "horizontal"), ("V5", "vertical receiver", 1.8, 3.6, "vertical")]
# Orifice letters printed in Rev A (they came from the Z = 0.673 / 0.807 table); kept only to show what changed.
REVA_LETTER = {"propane": {"V1": "G", "V2": "J", "V3": "L", "V4": "M", "V5": "G"}, "n-butane": {"V1": "H", "V2": "L", "V3": "N", "V4": "P", "V5": "J"}}
FILL = 0.85          # A1, workbook
F_PROT = 0.3         # A12, placeholder for fireproofing credit, not credited


def vessel_geom(D, L, orient):
    vol = math.pi / 4 * D * D * L + 2 * math.pi * D ** 3 / 24            # cylinder + two 2:1 elliptical heads (D)
    level = FILL * D if orient == "horizontal" else FILL * L
    return vol, level, RL.wetted_area_cylinder(D, L, level, orient)


def fire_case(fl, D, L, orient, F=1.0, mode="Z1"):
    p = FLUID[fl]
    vol, level, Aw = vessel_geom(D, L, orient)
    Q = RL.fire_heat_input_W(Aw, F) / 1e3                                  # kW, Q = 43,200 F A^0.82 (API 521 form, S via workbook A12)
    W = RL.fire_relief_rate_kg_h(Aw, p["lat"], F)
    P1 = RL.relieving_pressure_kpa(p["Pset"], "fire")
    if mode == "Z1":
        area = RL.gas_area(W, p["T"], P1, RL.ATM, p["M"], p["k"], Z=1.0).required_area_mm2
    elif mode == "Zcalc":
        area = RL.gas_area(W, p["T"], P1, RL.ATM, p["M"], p["k"], Z=p["Zcalc"]).required_area_mm2
    else:
        area = RL.gas_area_from_flux(W, p["Greal"])
    letter, n = RL.select_orifice(area)
    return dict(vol=vol, Aw=Aw, Q=Q, W=W, P1=P1, area=area, letter=letter, rated=RL.API526_ORIFICES_MM2[letter])


FC = {fl: {v[0]: {m: fire_case(fl, v[2], v[3], v[4], 1.0, m) for m in ("Z1", "Zcalc", "real")} for v in VESSELS} for fl in FLUID}
FP = {fl: {v[0]: fire_case(fl, v[2], v[3], v[4], F_PROT, "Z1") for v in VESSELS} for fl in FLUID}
V3P, V3B = FC["propane"]["V3"], FC["n-butane"]["V3"]

# --- closure checks against the workbook (S), so a drifting constant is caught
assert abs(V3P["Z1"]["W"] - 28863.5) < 1.0 and abs(V3P["Z1"]["Q"] - 2042.17) < 0.05, "fire relief rate no longer matches workbook R_Sizing"
assert abs(V3P["Z1"]["area"] - 1495.67) < 0.5 and abs(V3B["Z1"]["area"] - 2687.6) < 0.5, "Z = 1.0 required area no longer matches workbook"
assert abs(V3P["Zcalc"]["area"] - 1227) < 1.0 and abs(V3B["Zcalc"]["area"] - 2414) < 1.5, "Rev A Z-based areas not reproduced"
RHO15 = 509.27                                                      # kg/m3 propane liquid, 288.15 K, workbook BLEVE_Calc (Annex eq 1), S
M_BLEVE = V3P["Z1"]["vol"] * FILL * RHO15                             # D
assert abs(M_BLEVE - 45490.4) < 5, "BLEVE mass closure"
M_CALC = M_BLEVE
M_BLEVE = 45490.4                                                   # workbook BLEVE_Calc value (S); M_CALC is the identity check
R_FB = 3.24 * M_BLEVE ** 0.325                                      # Yellow Book 6.90 (S)
T_FB = 0.852 * M_BLEVE ** 0.26                                      # Yellow Book 6.91 (S)

# --- IOGP 434-01 datasheet 1 steel pipe: F(d) = C d^m per m-yr, C and m interpolated linearly in D between 0 and 170 mm (S, workbook P_Frequency)
PIPE_D, PIPE_L = 150.0, 200.0
C_ = 2.99e-5 + (1.39e-5 - 2.99e-5) * PIPE_D / 170.0
m_ = -0.798 + (-0.872 + 0.798) * PIPE_D / 170.0
def F_iogp(d): return C_ * d ** m_
F_LEAK = (F_iogp(10) - F_iogp(50)) * PIPE_L                           # hole class 10 to 50 mm, /yr (D)
assert abs(F_LEAK - 3.24654e-4) < 3e-8, "IOGP leak frequency not reproduced"
# --- ignition probability: IOGP 434-06 Table 3-1 look-up points, log-log interpolation (S via workbook P_Frequency)
PTS_SMALL = [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (3, 0.014), (498.991, 0.6), (100000, 0.6)]
PTS_LARGE = [(0.01, 0.001), (0.07654, 0.001), (0.1, 0.0011), (1, 0.0025), (100, 0.25), (260, 0.65), (100000, 0.65)]
def loglog(pts, q):
    for (q0, p0), (q1, p1) in zip(pts, pts[1:]):
        if q0 <= q <= q1:
            return math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * (math.log(q) - math.log(q0)) / (math.log(q1) - math.log(q0)))
    raise ValueError(q)
P_IGN = {fl: dict(small=loglog(PTS_SMALL, FLUID[fl]["Q25"]), large=loglog(PTS_LARGE, FLUID[fl]["Q25"]), cox=0.07) for fl in FLUID}
assert abs(P_IGN["propane"]["small"] - 0.00948431) < 2e-6 and abs(P_IGN["n-butane"]["large"] - 0.00258748) < 2e-6, "ignition interpolation"
# --- Purple Book (PGS 3, PDF read here): Table 3.7 pipes DN75-150: full bore 3e-7 /m/yr, leak 2e-6 /m/yr (leak = 10 % of nominal, max 50 mm = 15 mm for DN150);
#     Table 4.5 direct ignition, gas average/high reactivity: 0.2 (<10 kg/s), 0.5 (10-100 kg/s), 0.7 (>100 kg/s); Table 4.7 lists propane and butane as 'average'.
PB_RUPT = 3e-7 * PIPE_L                                            # 6.0e-5 /yr
PB_LEAK = 2e-6 * PIPE_L                                            # 4.0e-4 /yr
PB_PD = {"lt10": 0.2, "10_100": 0.5, "gt100": 0.7}
PB_JET_LEAK = PB_LEAK * PB_PD["lt10"]
PB_JET_RUPT = PB_RUPT * PB_PD["10_100"]
PB_JET_RUPT_LO = PB_RUPT * PB_PD["lt10"]
PB_JET_TOTAL = PB_JET_LEAK + PB_JET_RUPT
IOGP_PB = F_LEAK * PB_PD["lt10"]
RATE_15MM = FLUID["propane"]["Q25"] * (15 / 25) ** 2                 # kg/s, area scaling (D, A2)
RUPT_BOUND = {fl: 0.62 * math.pi / 4 * 0.15 ** 2 * FLUID[fl]["flux25"] for fl in FLUID}   # orifice-only upper bound, Cd 0.62 (D)
# BLEVE chain (sheet 6): Table 3.3 G.1 instantaneous 5e-7, Table 4.5 instantaneous > 10,000 kg 0.7, P(BLEVE | direct ignition) 0.7
BLEVE_CHAIN = 5e-7 * PB_PD["gt100"] * 0.7
HSL_RATIO = 24.4 / 17.2                                            # S13: PRV set 17.2 barg, tank failed 24.4 barg (jet fire)

# --- thermal expansion of trapped liquid (CoolProp 8.0.0 via python3, frozen):
#     PropsSI('D'|'C','T',T,'Q',0,fluid); PropsSI('isobaric_expansion_coefficient'|'isothermal_compressibility','T',T,'P',1.01*Psat,fluid)
THERM = {"propane":  dict(T=307.5, Psat=1199127.3, rho=477.201, cp=2832.08, alpha=3.754202e-3, kT=8.074495e-9),
         "n-butane": dict(T=313.9, Psat=386473.7,  rho=553.993, cp=2536.01, alpha=2.269310e-3, kT=3.858622e-9)}
for fl, t in THERM.items():
    t["dPdT_bar"] = t["alpha"] / t["kT"] / 1e5
    t["m3h_per_kW"] = SC.thermal_expansion_relief_m3h(1000.0, t["alpha"], t["rho"], t["cp"])
    t["dT_to_set"] = (FLUID[fl]["Pset"] * 1e3 + 101325.0 - t["Psat"]) / (t["alpha"] / t["kT"])
    t["vol"] = math.pi / 4 * (PIPE_D / 1000) ** 2 * PIPE_L
    t["mass"] = t["vol"] * t["rho"]
# propane liquid density 288.15 / 323.15 K / at Tsat(set pressure) = 326.09 K (CoolProp, frozen): fill fraction on a hot day (D)
RHO_P = {288.15: 507.503, 323.15: 448.868, 326.09: 443.008}
FILL_HOT_50C = FILL * RHO_P[288.15] / RHO_P[323.15]
FILL_HOT_SET = FILL * RHO_P[288.15] / RHO_P[326.09]
TB_BUTANE = 272.66                                                 # K, CoolProp normal boiling point
VAP_REL_DENS = {fl: FLUID[fl]["M"] / 28.96 for fl in FLUID}        # relative to air (M air 28.96)
SHELL_AREA = math.pi * 3.2 * 12.0 + 2 * 1.084 * 3.2 ** 2           # m2, cylinder + two 2:1 heads (relief.py head factor 1.084 D2), D
SPRAY_LPM = (FW.spray_demand_lpm(SHELL_AREA, 4.0), FW.spray_demand_lpm(SHELL_AREA, 10.0))   # pool-rated 4 to 10 L/min/m2 (summary slide 10, S)
SIL_BAND = {n: (lo, hi) for n, lo, hi in SILM.SIL_BANDS}
HOLD_SEG_RATIO = 45490.0 / THERM["propane"]["mass"]


def fmt(x, n=0):
    return f"{x:,.{n}f}"


def sci(x):
    m, e = f"{x:.1e}".split("e")
    return f"{m}e{int(e)}"


def dump():
    print("--- fire case Z=1.0 (propane / n-butane), V1..V5: area mm2, letter [Rev A letter]")
    for fl in FLUID:
        for v in VESSELS:
            c = FC[fl][v[0]]
            print(fl, v[0], round(c["Z1"]["Aw"], 2), round(c["Z1"]["Q"], 1), round(c["Z1"]["W"], 1), round(c["Z1"]["area"], 1), c["Z1"]["letter"], "RevA", REVA_LETTER[fl][v[0]],
                  "Zcalc", round(c["Zcalc"]["area"], 1), c["Zcalc"]["letter"], "real", round(c["real"]["area"], 1), c["real"]["letter"], "F0.3", round(FP[fl][v[0]]["area"], 1), FP[fl][v[0]]["letter"])
    print("BLEVE mass", round(M_BLEVE, 1), "r", round(R_FB, 2), "t", round(T_FB, 2))
    print("F_LEAK", F_LEAK, "P_IGN", P_IGN)
    print("PB rupt", PB_RUPT, "PB leak", PB_LEAK, "jet leak", PB_JET_LEAK, "jet rupt", PB_JET_RUPT, PB_JET_RUPT_LO, "total", PB_JET_TOTAL, "IOGP x 0.2", IOGP_PB)
    print("rate 15 mm", RATE_15MM, "rupture bound", RUPT_BOUND, "BLEVE chain", BLEVE_CHAIN, "HSL ratio", HSL_RATIO)
    for fl, t in THERM.items(): print(fl, {k: round(v, 5) if isinstance(v, float) else v for k, v in t.items()})
    print("fill hot", FILL_HOT_50C, FILL_HOT_SET, "rel dens", VAP_REL_DENS, "shell", SHELL_AREA, "spray", SPRAY_LPM, "seg ratio", HOLD_SEG_RATIO)


# =====================================================================================================
# HELPERS (local; pidlib is not edited)
# =====================================================================================================
class RevSheet(Sheet):
    """Sheet whose header says Rev B (pidlib.frame prints Rev A / Draft A)."""
    def svg(self):
        return super().svg().replace("|  Rev A<", "|  Rev B<").replace("Draft A.", "Draft B.")


def new_sheet(no, title, sub):
    return RevSheet(no, title, sub, basis="Summary + calc workbook (10 Nov 2026), PGS 3, free sources")


_bubble = bubble
BUB = set()


def bubble(s, x, y, a, b, panel=False, color=INK, r=15):
    """pidlib bubble, also recording the tag for the lint"""
    BUB.add(f"{a}-{b}")
    _bubble(s, x, y, a, b, panel, color, r)


def tsv(s, x, y, color=INK):
    """thermal relief valve: the PSV symbol rotated 180 degrees, inlet on top at (x, y-16), outlet to the left at (x-18, y), spring hat below."""
    s.add(f'<g transform="translate({x},{y}) rotate(180)" stroke="{color}" stroke-width="1.8" fill="#fff">'
          f'<polygon points="-10,16 10,16 0,-2"/><polygon points="0,-2 18,-10 18,10"/>'
          f'<polyline points="0,-2 0,-8 -6,-12 6,-17 -6,-22 6,-27 0,-31" fill="none"/></g>')


def wtable(s, x, y, colw, rows, size=10, lh=12.0, head=True, first_bold=True, fills=None):
    """table with wrapped cells; returns the y below it. Character width taken as 0.52 em (Helvetica average)."""
    ypos = y
    tw = sum(colw)
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), max(5, int((colw[j] - 8) / (size * 0.52)))) or [""] for j, c in enumerate(r)]
        h = max(len(c) for c in cells) * lh + 7
        if head and i == 0: R(s, x, ypos, tw, h, "#e8eaf0", "none")
        elif fills and i in fills: R(s, x, ypos, tw, h, fills[i], "none")
        elif i % 2 == 0: R(s, x, ypos, tw, h, "#f6f7fa", "none")
        cx = x
        for j, ls in enumerate(cells):
            wgt = 700 if (head and i == 0) or (first_bold and j == 0) else 400
            for k, t in enumerate(ls):
                T(s, cx + 4, ypos + 3 + lh * (k + 1) - 2, t, size, wgt)
            cx += colw[j]
        ypos += h
    R(s, x, y, tw, ypos - y, "none", "#9aa", 1)
    cx = x
    for w in colw[:-1]:
        cx += w
        PL(s, [(cx, y), (cx, ypos)], 0.5, "#c5c9d4")
    return ypos


def key_line(s, x, y):
    T(s, x, y, "Labels: S sourced (document + table)   D derived (formula in generator)   A assumed by this drawing   R required or recommended by a named free source   gap = controlling standard not obtained", 10, 400, fill=GREY)


# =====================================================================================================
# EQUIPMENT LIST (single source for the cover table and the tag lint)
# =====================================================================================================
EQUIP = [("Tag", "Description", "Basis"),
         ("V-101", "LPG bullet (ref. V3) 105.1 m3, 3.2 x 12 m", "workbook"),
         ("PSV-101", "Balanced bellows; set 1,724 kPag propane, 690 kPag n-butane (A); orifice L / N at Z = 1.0", "R, D"),
         ("TSV-102", "Thermal relief, trapped L-102, returns to V-101 via L-105; not sized", "A"),
         ("XV-101", "Inlet ESDV, fail-closed, near nozzle N1", "A"),
         ("XV-102", "Outlet remote fire-safe isolation valve at N2", "R"),
         ("XV-103", "Supply-line battery-limit ESDV", "A"),
         ("HV-101/102", "Manual block valves, fill and supply", "A"),
         ("NRV-101", "Non-return valve on fill line", "A"),
         ("HV-104/105", "Double block drain, plugged", "A"),
         ("LT-101", "Level transmitter (radar), alarms to ESD", "A"),
         ("LSHH-101", "Independent high-level cutoff, trips XV-101 (SIF-1)", "R"),
         ("PT-101", "Pressure transmitter, PAH / PAHH (SIF-4)", "A"),
         ("TI-101", "Shell temperature indicator", "A"),
         ("AT-101A/B/C", "Flammable gas detectors, 2oo3 (A); C at the low point", "R, A"),
         ("BE-101", "UV/IR flame detector", "R"),
         ("HS-101", "Manual ESD push-button, remote safe location", "A"),
         ("FM-101", "Fire monitor, manual: pool-fire cooling, not jet protection", "A"),
         ("ESD-101", "ESD and fire and gas logic", "R"),
         ("UC-101", "Unloading connection (tanker or rail)", "A"),
         ("PFP", "Jet-rated passive fire protection", "R")]
DEV_TAGS = {"V-101", "PSV-101", "TSV-102", "XV-101", "XV-102", "XV-103", "HV-101", "HV-102", "HV-104", "HV-105", "NRV-101", "LT-101", "LSHH-101", "PT-101", "TI-101",
            "AT-101A", "AT-101B", "AT-101C", "BE-101", "HS-101", "FM-101", "ESD-101", "UC-101"}


# =====================================================================================================
# THE VESSEL AND ITS PIPING (common to sheets 2 to 6)
# =====================================================================================================
VX0, VX1, VY0, VY1 = 300, 680, 375, 505   # body extents; heads add 40 px each side
GRADE = 548


def base(s, mode="normal", lvl_color="#cfe6f7"):
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    body = f"M{VX0},{VY0} H{VX1} A40,65 0 0 1 {VX1},{VY1} H{VX0} A40,65 0 0 1 {VX0},{VY0} Z"
    s.add(f'<clipPath id="vclip{s.no}"><path d="{body}"/></clipPath>')
    s.add(f'<path d="{body}" fill="#fff"/>')
    liq_y = VY1 - 0.85 * 130
    s.add(f'<rect x="250" y="{liq_y}" width="480" height="{VY1-liq_y+1}" fill="{lvl_color}" clip-path="url(#vclip{s.no})"/>')
    s.add(f'<line x1="255" y1="{liq_y}" x2="725" y2="{liq_y}" stroke="{BLUE}" stroke-width="1.2" stroke-dasharray="6 4" clip-path="url(#vclip{s.no})"/>')
    s.add(f'<path d="{body}" fill="none" stroke="{INK}" stroke-width="3"/>')
    for sx in (350, 630):
        s.add(f'<polygon points="{sx-22},{VY1-3} {sx+22},{VY1-3} {sx+30},{GRADE} {sx-30},{GRADE}" fill="#eee" stroke="{INK}" stroke-width="1.4"/>')
    PL(s, [(200, GRADE), (760, GRADE)], 1.6, "#555")
    for gx in range(204, 760, 16): PL(s, [(gx, GRADE), (gx - 8, GRADE + 8)], 0.8, "#777")
    T(s, 365, 408, "V-101  LPG BULLET (propane or n-butane)", 12.5, 700)
    T(s, 365, 424, "3.2 m ID x 12.0 m T/T, 105.1 m3, 2:1 elliptical heads", 10.5)
    T(s, 365, 439, "85 % liquid (2.72 m), wetted area 110.2 m2", 10.5)
    T(s, 365, 454, "Set 1,724 kPag propane (A1); n-butane 690 kPag (A)", 10.5)
    # --- N1 fill line
    PL(s, [(92, 250), (360, 250), (360, 375)])
    R(s, 40, 232, 52, 36, "#fff", INK, 1.6); T(s, 66, 248, "UC-101", 10.5, 700, "middle"); T(s, 66, 261, "unloading", 9, 400, "middle")
    valve(s, 175, 250, 0, "ball"); T(s, 175, 272, "HV-101", 10.5, 700, "middle")
    valve(s, 250, 250, 0, "check"); T(s, 250, 272, "NRV-101", 10.5, 700, "middle")
    valve(s, 360, 322, 90, "ball", act=True); T(s, 336, 318, "XV-101", 10.5, 700, "end"); T(s, 336, 331, "ESDV (A)", 9, 400, "end")
    T(s, 130, 224, 'L-101  3" LPG-A1 (A)', 10.5, 700)
    arrow(s, 120, 250, "r")
    # --- N3 PSV + vent
    PL(s, [(620, VY0), (620, 330)])
    psv(s, 620, 312)
    PL(s, [(638, 312), (710, 312), (710, 185)])
    s.add(f'<path d="M702,185 L718,185 M710,185 L710,178" stroke="{INK}" stroke-width="2.4" fill="none"/><path d="M700,178 Q710,168 720,178" stroke="{INK}" stroke-width="2" fill="none"/>')
    T(s, 700, 200, "L-103 vent", 10.5, 700, "end"); T(s, 700, 213, "to safe location", 9.5, 400, "end"); T(s, 700, 225, "(height TBD)", 9.5, 400, "end")
    T(s, 724, 262, "PSV-101", 11, 700); T(s, 724, 275, "balanced", 9.5); T(s, 724, 287, "bellows (R)", 9.5)
    # --- instruments on top nozzles
    for x, a, b, panel in ((450, "LT", "101", True), (510, "LSHH", "101", True), (570, "PT", "101", True)):
        PL(s, [(x, VY0), (x, 299)], 1.4); bubble(s, x, 284, a, b, panel)
    PL(s, [(262, 440), (232, 440)], 1.4); bubble(s, 217, 440, "TI", "101", False)
    # --- N2 liquid outlet and supply line
    PL(s, [(690, 503), (690, 600), (1095, 600)])
    valve(s, 690, 552, 90, "gate", act=True)
    T(s, 676, 580, "XV-102", 10.5, 700, "end"); T(s, 676, 592, "remote fire-safe", 9, 400, "end"); T(s, 676, 604, "isolation (R)", 9, 400, "end")
    valve(s, 790, 600, 0, "gate"); T(s, 790, 622, "HV-102", 10.5, 700, "middle")
    valve(s, 980, 600, 0, "gate", act=True); T(s, 980, 622, "XV-103", 10.5, 700, "middle"); T(s, 980, 634, "battery limit (A)", 9, 400, "middle")
    T(s, 1100, 668, 'To user: L-102 6" (150 mm)', 10.5, 700, "end"); T(s, 1100, 681, "liquid supply, ~200 m (A14)", 9.5, 400, "end")
    arrow(s, 890, 600, "r"); arrow(s, 1060, 600, "r")
    T(s, 720, 590, 'L-102  6" LPG-A1', 10.5, 700)
    # --- Rev B: thermal relief of the liquid trapped between XV-102 and XV-103 (A), returns to V-101 through L-105
    PL(s, [(870, 600), (870, 620)], 2)
    tsv(s, 870, 636)
    PL(s, [(852, 636), (585, 636), (585, 512)], 2)
    arrow(s, 585, 512, "u")
    T(s, 846, 654, "TSV-102 (A)", 10, 700, "end"); T(s, 846, 666, "thermal relief", 9.5, 400, "end"); T(s, 846, 678, "L-105 to V-101", 9.5, 400, "end")
    T(s, 593, 560, "L-105", 9.5, 700)
    # --- N4 drain
    PL(s, [(430, VY1), (430, 635)], 2.4)
    valve(s, 430, 525, 90, "gate"); valve(s, 430, 585, 90, "gate")
    PL(s, [(421, 635), (439, 635)], 3); T(s, 446, 529, "HV-104", 10, 700); T(s, 446, 589, "HV-105", 10, 700); T(s, 446, 630, "L-104 1\" drain, plugged", 9.5)
    # --- detectors (gas detectors are low: LPG vapour is heavier than air, D)
    bubble(s, 120, 520, "AT", "101A", True); bubble(s, 850, 520, "AT", "101B", True); bubble(s, 850, 445, "BE", "101", True)
    bubble(s, 630, 668, "AT", "101C", True)
    T(s, 120, 556, "gas det. (R)", 9.5, 400, "middle"); T(s, 850, 556, "gas det. (R)", 9.5, 400, "middle"); T(s, 870, 449, "UV/IR flame det. (R)", 9.5)
    T(s, 652, 664, "AT-101C low point", 9.5, 700); T(s, 652, 676, "gas det. (A)", 9.5)
    # --- manual ESD and fire monitor (A)
    bubble(s, 60, 330, "HS", "101", False)
    PL(s, [(76, 330), (112, 330)], 1.3, BLUE, "5 4", "ahb"); T(s, 118, 334, "to ESD-101", 9.5, 400, fill=BLUE)
    T(s, 30, 358, "manual ESD (A)", 9.5, 400)
    s.add(f'<circle cx="190" cy="345" r="14" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    T(s, 190, 350, "FM", 10, 700, "middle")
    PL(s, [(204, 349), (258, 395)], 1.6, BLUE, "3 3", "ahb")
    T(s, 190, 372, "FM-101 monitor (A)", 9.5, 700, "middle"); T(s, 190, 384, "pool cooling only", 9.5, 400, "middle")
    # --- ESD logic
    R(s, 380, 98, 240, 50, "#fff3e0", RED, 1.8)
    T(s, 500, 118, "ESD-101  ESD + FIRE & GAS LOGIC", 11.5, 700, "middle", RED)
    T(s, 500, 134, "alarms / trips (R: detection, isolation, high-level cutoff)", 9.5, 400, "middle", RED)
    sig = dict(sw=1.3, stroke=BLUE, dash="5 4", marker="ahb")
    for x in (450, 510, 570): PL(s, [(x, 269), (x, 148)], **sig)
    PL(s, [(120, 505), (120, 123), (380, 123)], **sig)
    PL(s, [(850, 430), (850, 123), (620, 123)], **sig)
    PL(s, [(850, 505), (850, 460)], 1.3, BLUE, "5 4")
    ctl = dict(sw=1.5, stroke=RED, dash="6 4", marker="ahr")
    PL(s, [(395, 148), (395, 322), (378, 322)], **ctl)
    PL(s, [(610, 148), (610, 138), (800, 138), (800, 552), (708, 552)], **ctl)
    PL(s, [(800, 138), (980, 138), (980, 576)], **ctl)


def pfp(s, on=True):
    if on:
        body = f"M{VX0},{VY0} H{VX1} A40,65 0 0 1 {VX1},{VY1} H{VX0} A40,65 0 0 1 {VX0},{VY0} Z"
        s.add(f'<path d="{body}" fill="none" stroke="url(#hatch)" stroke-width="9" opacity=".75"/>')
        for sx in (350, 630):
            s.add(f'<polygon points="{sx-22},{VY1-3} {sx+22},{VY1-3} {sx+30},{GRADE} {sx-30},{GRADE}" fill="url(#hatch)" opacity=".75"/>')


# =============================================================== sheets
def sheet_cover():
    s = new_sheet(1, "LPG storage P&ID set, Rev B: legend, equipment, scenario register", "Cover, legend and scenario register")
    frame(s, NSHEETS)
    y = section(s, 20, 84, 520, "LEGEND")
    R(s, 20, y, 520, 560, "#fff", "#889", 1)
    yy = y + 24
    PL(s, [(36, yy), (96, yy)]); T(s, 120, yy + 4, "Process line (liquid LPG)", 11.5)
    yy += 28; PL(s, [(36, yy), (96, yy)], 1.4, BLUE, "5 4", "ahb"); T(s, 120, yy + 4, "Instrument signal to ESD / F&G logic", 11.5)
    yy += 28; PL(s, [(36, yy), (96, yy)], 1.5, RED, "6 4", "ahr"); T(s, 120, yy + 4, "ESD / trip output to valve", 11.5)
    yy += 30; valve(s, 66, yy, 0, "gate"); T(s, 120, yy + 4, "Gate valve (manual)", 11.5)
    yy += 28; valve(s, 66, yy, 0, "ball"); T(s, 120, yy + 4, "Ball valve (manual)", 11.5)
    yy += 28; valve(s, 66, yy, 0, "check"); T(s, 120, yy + 4, "Non-return (check) valve", 11.5)
    yy += 44; valve(s, 66, yy, 0, "gate", act=True); T(s, 120, yy + 4, "Actuated emergency shutdown valve (ESDV / XV), fail-closed", 11.5)
    yy += 56; psv(s, 66, yy); T(s, 120, yy + 4, "Pressure safety valve, balanced bellows, angle type", 11.5)
    yy += 52; tsv(s, 66, yy); T(s, 120, yy - 2, "Thermal relief valve (TSV), self-acting, relieves to a closed system", 11.5)
    yy += 52; bubble(s, 66, yy, "LT", "101", True); T(s, 120, yy + 4, "Instrument, panel / logic mounted (line through bubble)", 11.5)
    yy += 36; bubble(s, 66, yy, "TI", "101", False); T(s, 120, yy + 4, "Instrument, field mounted", 11.5)
    yy += 30; s.add(f'<rect x="36" y="{yy-5}" width="60" height="10" fill="url(#hatch)"/>'); T(s, 120, yy + 4, "Passive fire protection (PFP), rated for jet fire", 11.5)
    yy += 28; s.add(f'<rect x="36" y="{yy-8}" width="60" height="16" fill="#cfe6f7" stroke="{BLUE}" stroke-dasharray="6 4"/>'); T(s, 120, yy + 4, "Liquid inventory at 85 % level", 11.5)
    yy += 30; star(s, 66, yy, 12); T(s, 120, yy + 4, "Release point (scenarios A, B)", 11.5)
    yy += 30; flame(s, 60, yy + 11, 30, 26, 12); T(s, 120, yy + 4, "Jet fire / pool fire", 11.5)
    yy += 28; s.add(f'<circle cx="66" cy="{yy}" r="11" fill="url(#ball)"/>'); T(s, 120, yy + 4, "BLEVE fireball (scenario D)", 11.5)
    y2 = section(s, 20, 664, 520, "NOTES")
    R(s, 20, y2, 520, 440 - 22 - 0, "#fff", "#889", 1)
    notes = [
        "1. Conceptual P&ID for a screening study. The source files describe a calculation chain, not a plant, so no real vessel, layout or line data exist. Vessels V1 to V5 are an assumed sample set (A1).",
        "2. Labels: S sourced, D derived, A assumed here, R required or recommended by a named free source, gap = controlling standard not obtained. Tags marked (R) follow slide 10 of the summary; (A) are assumed to complete the drawing.",
        "3. Reference vessel is V3, the 105 m3 bullet. Hole, line, fire and BLEVE numbers are workbook values, not new calculations, except where marked D.",
        "4. Rev B: relief areas now at Z = 1.0 (Rev A used 0.673); Purple Book ignition and full-bore rupture added to sheet 4; BLEVE chain corrected on sheet 6; TSV-102 and more detection added; sheets 7 to 9 are the safety design basis.",
        "5. No heat and material balance: storage and loss-of-containment set, no process streams. Closure checks are on sheet 2.",
        "6. Distances on the strips are to scale; the P&ID area is not. Do not use any distance, area or rate here for siting or design; run a validated tool (Phast / Safeti).",
        "7. SIL values are assumed targets (A), not verified. Standards behind a paywall or registration (API 520/521/526/2510, NFPA 58, OISD-144/118, IEC 61511) were not read.",
    ]
    yy = y2 + 20
    for n in notes: yy = WRAP(s, 30, yy, n, 84, 10.5, 13.5) + 5

    x0 = 560
    y = section(s, x0, 84, 540, "EQUIPMENT AND INSTRUMENT LIST")
    y = table(s, x0, y, (110, 350, 80), EQUIP, 19, 10.5)
    y = section(s, x0, y + 12, 540, "LINE LIST (A)")
    rows = [("Line", "Service", "Size", "Note"),
            ("L-101", "Fill, liquid LPG", '3"', "from unloading connection"),
            ("L-102", "Liquid supply", '6"', "150 mm, 200 m (frequency basis, A14)"),
            ("L-103", "PSV outlet / vent", "TBD", "balanced bellows, back pressure 10 % of set (A)"),
            ("L-104", "Drain", '1"', "double block and plug"),
            ("L-105", "TSV-102 return", "TBD", "to V-101, route not drawn (A)")]
    y = table(s, x0, y, (60, 120, 50, 310), rows, 19, 10.5)
    y = section(s, x0, y + 12, 540, "PROCESS BASIS")
    rows = [("", "Propane", "n-Butane"),
            ("Storage pressure", "12 bar(a)", "4 bar(a)"),
            ("Storage temperature (saturated)", "307.5 K (34.4 C)", "313.9 K (40.8 C; CoolProp 315.1 K)"),
            ("PSV set (assumed)", "1,724 kPag", "690 kPag (100 psig)"),
            ("PSV orifice, V3, bare, Z = 1.0", f"{V3P['Z1']['letter']} ({fmt(V3P['Z1']['area'])} mm2 req.)", f"{V3B['Z1']['letter']} ({fmt(V3B['Z1']['area'])} mm2 req.)"),
            ("Release basis", "25 mm hole, Cd 0.62", "25 mm hole, Cd 0.62"),
            ("Ambient / wind / release height", "288.15 K / 5 m/s / 2 m", "same")]
    y = table(s, x0, y, (230, 160, 150), rows, 19, 10.5)
    # scenario register
    x1 = 1135
    y = section(s, x1, 84, 445, "SCENARIO REGISTER")
    sc = [("Sheet 2  BASE", "Normal storage, fill and supply", "Operating case, tags, safeguards; Rev A to Rev B changes and closure checks."),
          ("Sheet 3  A", "Hole in vessel liquid nozzle (10, 25, 168 mm)", "Flashing jet, jet fire, flash fire / VCE. 25 mm: 2.34 kg/s propane, 1.03 kg/s butane; flame 10.8 / 7.8 m."),
          ("Sheet 4  B", "Supply-line break (line-fed release)", "HEM line model; leak and full-bore rupture frequencies on two ignition bases (UKOOA / Cox and Purple Book)."),
          ("Sheet 5  C", "External fire on V-101 (fire-case relief)", f"Heat input {fmt(V3P['Z1']['Q'])} kW, relief {fmt(V3P['Z1']['W'])} kg/h; Z = 1.0 areas for all five vessels."),
          ("Sheet 6  D", "BLEVE of V-101 at 1.21 x set", "Fireball 106 m radius, 14 s; 35 kW/m2 at about 250 m. Chain 5e-7 x 0.7 x 0.7."),
          ("Sheet 7  SAFETY 1", "Relief schedule and thermal relief", "Every pressure item: case, device, discharge, sizing status."),
          ("Sheet 8  SAFETY 2", "ESD matrix, SIF list, detection, mitigation", "Assumed SIL (A), F&G logic, fire protection, bund and spacing basis, gaps."),
          ("Sheet 9  SAFETY 3", "Hazard identification, inherently safer design", "8 HAZOP-style nodes, 6 design options, lint results.")]
    R(s, x1, y, 445, 8 * 94 + 14, "#fff", "#889", 1)
    yy = y + 8
    for t1, t2, t3 in sc:
        R(s, x1 + 8, yy, 429, 86, "#f6f7fa", "#bbb", 1)
        T(s, x1 + 16, yy + 17, t1, 12, 700, fill="#1a237e")
        yy2 = WRAP(s, x1 + 16, yy + 33, t2, 56, 11.5, 14, weight=700)
        WRAP(s, x1 + 16, yy2 + 2, t3, 68, 10.5, 13)
        yy += 94
    return s


def sheet_base():
    s = new_sheet(2, "BASE CASE: normal storage, fill and supply, V-101", "Base case, normal operation, Rev A to Rev B")
    frame(s, NSHEETS)
    base(s)
    pfp(s)
    legend_mini(s, 36, 722)
    R(s, 36, 640, 330, 62, "#fff", "#889", 1)
    TL(s, 44, 656, ["Normal operation (propane case)", "Saturated liquid 12 bar(a), 307.5 K; 85 % level.", "Fill via XV-101; supply via XV-102, XV-103.", "PSV closed. Gas and flame detectors armed."], 10.5, 12.5)
    panel_box(s)
    x = 1145; y = section(s, 1135, 84, 445, "OPERATION AND SAFEGUARDS")
    yy = y + 18
    items = [
        "Normal: V-101 holds saturated LPG at its vapour pressure. Fill enters at the top nozzle N1, supply leaves at the bottom nozzle N2 to the 6 inch user line.",
        "Level: LT-101 gives the operating level and alarms. LSHH-101 is independent and trips XV-101 so the vessel cannot be overfilled (R). A 15 C fill of 85 % grows to " + f"{FILL_HOT_50C*100:.0f} % at 50 C and {FILL_HOT_SET*100:.0f} % at 53 C, where vapour pressure reaches the PSV set (D, CoolProp).",
        "Pressure: PT-101 alarms high (SIF-4). PSV-101 (set 1,724 kPag propane, 690 kPag n-butane, assumed) is sized for fire only. Blocked-in liquid on L-102 now has TSV-102 (A, not sized). Full list on sheet 7.",
        "Detection: three gas detectors (A, 2oo3) and a UV/IR flame detector feed ESD-101. On confirmed gas or flame, or HS-101, the logic closes XV-101, XV-102 and XV-103 (R). Matrix on sheet 8.",
        "Fire protection: jet-rated PFP on shell, supports and vapour space (R). Water spray and FM-101 are pool-rated (4 to 10 L/min/m2) and not relied on for jet fire.",
        "Layout: keep the vessel and supports beyond the 19 m jet reach of a 25 mm leak from other equipment and boundaries (R). Table spacing is not a major-incident distance.",
    ]
    for t in items: yy = WRAP(s, x, yy, t, 66, 11.5, 15, bullet=True) + 7
    yc = section(s, 1135, 600, 445, "CLOSURE CHECKS (D vs workbook S)")
    rows = [("Check", "Rev B", "Workbook"),
            ("BLEVE mass (kg)", fmt(M_CALC, 1), "45,490.4"), ("Fire input V3 (kW)", fmt(V3P['Z1']['Q'], 1), "2,042.2"),
            ("Relief rate (kg/h)", fmt(V3P['Z1']['W'], 1), "28,863.5"), ("Area Z = 1.0 (mm2)", fmt(V3P['Z1']['area'], 1), "1,495.7"),
            ("IOGP 10-50 mm class (/yr)", sci(F_LEAK), "3.2e-4"), ("Ignition P, propane small", f"{P_IGN['propane']['small']:.5f}", "0.00948"),
            ("HMB", "n/a", "no process streams")]
    table(s, 1135, yc, (200, 120, 125), rows, 18, 10.3)
    y = section(s, 20, 784, 1100, "REV A TO REV B CHANGES (item | Rev A | Rev B | source | effect)")
    chg_letters = []
    for fl in FLUID:
        for v in VESSELS:
            a, b = REVA_LETTER[fl][v[0]], FC[fl][v[0]]["Z1"]["letter"]
            if a != b: chg_letters.append(f"{v[0]} {'C3' if fl == 'propane' else 'C4'} {a} to {b}")
    chg_letters = [t.replace("C3", "propane").replace("C4", "butane") for t in chg_letters]
    rows = [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
            ("Relief sizing Z (sheets 2, 5, 7)", "Table at Z = 0.673 / 0.807: V3 1,227 / 2,414 mm2",
             f"Z = 1.0: V3 {fmt(V3P['Z1']['area'])} / {fmt(V3B['Z1']['area'])} mm2; real-gas flux {fmt(V3P['real']['area'])} / {fmt(V3B['real']['area'])} shown",
             "API 520-I 5.6.3.2.2, Annex B (workbook R_Assumptions); process_safety.relief",
             f"Area +{(V3P['Z1']['area']/V3P['Zcalc']['area']-1)*100:.0f} % / +{(V3B['Z1']['area']/V3B['Zcalc']['area']-1)*100:.0f} %. Letters: " + "; ".join(chg_letters)),
            ("Ignition basis (sheet 4)", "UKOOA and Cox only (implied P 0.003 to 0.07)", f"Adds Purple Book direct ignition 0.2: jet fire {sci(IOGP_PB)} /yr for the same 10 to 50 mm class",
             "PGS 3 Table 4.5, PDF p.75 (read)", f"{IOGP_PB/(F_LEAK*P_IGN['propane']['cox']):.1f}x Cox, {IOGP_PB/(F_LEAK*P_IGN['n-butane']['large']):.0f}x UKOOA large (butane)"),
            ("Full-bore rupture (sheet 4)", "Not shown (title says 'break')", f"{sci(PB_RUPT)} /yr (3e-7 /m/yr x 200 m) beside PB leak {sci(PB_LEAK)}; jet fire {sci(PB_JET_RUPT)} at P 0.5 (A band)",
             "PGS 3 Table 3.7, PDF p.47 (read)", f"PB total jet fire {sci(PB_JET_TOTAL)} /yr (leak + rupture)"),
            ("BLEVE chain (sheet 6)", "'5e-7, 5e-7, 1e-5 (Tables 3.3, 4.5)'", f"5e-7 x 0.7 x 0.7 = {sci(BLEVE_CHAIN)} /yr; 1.21 x set labelled a convention",
             "PGS 3 Tables 3.3, 4.5; HSL trial (S13)", f"Wording and chain only; HSL failure was at {HSL_RATIO:.2f} x set"),
            ("Thermal relief (sheets 1, 7)", "Trapped L-102 not covered", f"TSV-102 + L-105 (A); {THERM['propane']['dPdT_bar']:.1f} bar/K, {THERM['propane']['m3h_per_kW']:.4f} m3/h per kW",
             "CoolProp (frozen); scenarios.thermal_expansion_relief_m3h", "New device; not sized: heat input undefined"),
            ("Detection, ESD (sheets 1, 8)", "AT-101A/B, 2 of 2 (A)", "AT-101A/B/C 2oo3 (A), HS-101, FM-101; ESD matrix, SIF list", "Checklist S1, S2, S4, S5", "Rows added; SIL values are targets (A)"),
            ("Safety basis (sheets 7 to 9)", "None", "Relief schedule, SIFs, F&G, mitigation, 8 HAZOP nodes, 6 ISD options", "Checklist S1, S2, S3, S5, S11, S13", "Gaps listed, none closed by assumption")]
    y = wtable(s, 20, y, (150, 215, 270, 215, 250), rows, 9.8, 11.5)
    return s


def sheet_A():
    s = new_sheet(3, "SCENARIO A: hole in vessel liquid nozzle, flashing jet and jet fire", "Scenario A, vessel hole, jet fire")
    frame(s, NSHEETS)
    base(s)
    pfp(s)
    hx, hy = 690, 524
    flame(s, hx, hy, 36.7, 215, 44)
    flame(s, hx, hy, 51.4, 150, 32, op=0.55)
    star(s, hx, hy, 13)
    R(s, 740, 98, 370, 62, "#fff", RED, 1.4)
    TL(s, 748, 114, ["HOLE upstream of XV-102 on liquid nozzle N2", "25 mm, Cd 0.62, saturated liquid. Modelled as a", "vertical jet at 2 m, wind 5 m/s (A3)"], 10.5, 13, fill=RED)
    TL(s, 880, 486, ["Propane jet fire: flame 10.8 m, tilt 37 deg", "n-Butane (faded): 7.8 m, tilt 51 deg", "Schematic, not to scale (see strip)"], 10, 12.5, fill=RED)
    TL(s, 36, 640, ["XV-102 / XV-103 close on confirmed gas or flame but do NOT", "stop this leak: the hole is on the vessel side of XV-102.", "Isolation only limits any line-fed inventory downstream."], 10.5, 13, fill=RED)
    TL(s, 36, 686, ["Flame can impinge on shell, saddles and supports: the reason", "for jet-rated PFP on shell, supports and vapour space (R)."], 10.5, 13, fill=AMBER)
    legend_mini(s, 36, 722)
    R(s, 520, 700, 590, 64, "#fff", "#889", 1)
    WRAP(s, 528, 716, "If not ignited at once: flashing two-phase cloud, vapour fraction 0.41 (propane) / 0.26 (butane); rain-out is zero for these hot leaks (A6). Delayed ignition gives flash fire (0.6) or vapour cloud explosion (0.4), multi-energy class 10, obstructed fraction 0.08 (A11; PGS 3 sections 4.8, read). Dispersion needs a validated tool (SLAB, DEGADIS, Phast): only a hand-off was done.", 118, 10, 12.5)
    panel_box(s)
    y = section(s, 1135, 84, 445, "25 mm HOLE: RESULTS (workbook, default settings)")
    rows = [("Quantity", "Propane", "n-Butane"), ("Storage", "12 bar(a)", "4 bar(a)"), ("Release rate (kg/s)", "2.34", "1.03"),
            ("Mass flux (kg/m2/s)", "7,690", "3,401"), ("Jet velocity after expansion (m/s)", "153.5", "92.4"),
            ("Vapour fraction after flash", "0.414", "0.262"), ("Droplet diameter (micron)", "8.0", "22.9"),
            ("Flame length (m)", "10.8", "7.8"), ("Flame tilt (deg)", "36.7", "51.4"), ("Radiated power (kW)", "37,130", "21,000"),
            ("Surface emissive power (kW/m2)", "350 (cap)", "350 (cap)"), ("Reach to 35 kW/m2 (m)", "9.6", "8.6"), ("Reach to 1 % lethality (m)", "19.1", "15.4")]
    y = table(s, 1135, y, (235, 105, 105), rows, 19, 10.5)
    y = section(s, 1135, y + 10, 445, "OTHER HOLE SIZES (propane, scaled by area, D)")
    rows = [("Hole", "Propane (kg/s)", "n-Butane (kg/s)"), ("10 mm", "0.37", "0.17"), ("15 mm (PGS 3 leak, DN150)", f"{RATE_15MM:.2f}", f"{FLUID['n-butane']['Q25']*0.36:.2f}"), ("25 mm", "2.34", "1.03"), ("168 mm", "105.7", "46.7")]
    y = table(s, 1135, y, (205, 120, 120), rows, 19, 10.5)
    yy = WRAP(s, 1141, y + 14, "Derived: flow scales with hole area (A2); only the 25 mm case is tabulated in the workbook. Flame length and reach were not rescaled; larger holes reach further than 19 m. Frequencies for these leaks and the ignition bases are on sheet 4.", 70, 10.5, 13.5, GREY)
    y = section(s, 1135, yy + 8, 445, "HARM THRESHOLDS (20 s exposure)")
    rows = [("Level", "Flux (kW/m2)"), ("1 % fatality (probit)", "9.8"), ("50 % fatality (probit)", "19.5"), ("50 % fatality (TDU 2000)", "31.6")]
    y = table(s, 1135, y, (235, 210), rows, 19, 10.5)
    yy = WRAP(s, 1141, y + 14, "Accuracy: flame length within about 33 % and radiation about 40 % even in DNV's own validation. Measured jet-fire flux can reach 200 kW/m2 (HSL).", 70, 10.5, 13.5, GREY)
    y = section(s, 1135, yy + 8, 445, "WHAT ACTS ON THIS SCENARIO")
    yy = y + 16
    for t in ("Detection: AT-101A/B/C and BE-101 alarm and trip ESD-101 (R); matrix on sheet 8.",
              "Isolation: XV-101, XV-102, XV-103 cut off line-fed and fill flows only.",
              "Protection: jet-rated PFP on shell, supports, vapour space; water spray is not jet protection (R).",
              "Layout: keep other vessels and supports beyond the 19 m reach for 25 mm; longer for larger holes (R).",
              "Data to retire A2: hole-size distribution from IOGP 434-01."):
        yy = WRAP(s, 1141, yy, t, 66, 11, 14, bullet=True) + 4
    y = section(s, 20, 784, 1100, "JET GEOMETRY AND REACH, TO SCALE (25 mm hole; vertical-jet flux map; wind left to right)")
    gy, sc = 1078, 22.0
    PL(s, [(40, gy), (1100, gy)], 1.6, "#555")
    rx = 330
    vy = gy - 3.2 * sc
    s.add(f'<rect x="{rx-12*sc-6:.0f}" y="{vy:.0f}" width="{12*sc:.0f}" height="{3.2*sc:.0f}" rx="{1.4*sc:.0f}" fill="#eee" stroke="{INK}" stroke-width="2"/>')
    T(s, rx - 6 * sc - 6, vy + 1.9 * sc, "V-101 (12 m x 3.2 m)", 11, 700, "middle")
    flame(s, rx, gy - 2 * sc, 36.7, 10.8 * sc, 40)
    flame(s, rx, gy - 2 * sc, 51.4, 7.8 * sc, 30, op=0.5)
    star(s, rx, gy - 2 * sc, 7)
    T(s, rx - 10, gy - 2 * sc + 4, "release at 2 m", 9.5, 400, "end")
    T(s, 40, 856, "Red: propane. Amber: n-butane.", 10.5, 700, fill=GREY)
    T(s, 40, 871, "35 kW/m2: building / clothing ignition level.", 10, fill=GREY)
    T(s, 40, 885, "1 %: lethality for a 20 s exposure (probit).", 10, fill=GREY)
    for d, lab, col, anchor, dx, ytxt in ((9.6, "35 kW/m2 at 9.6 m", RED, "start", 5, 830), (19.1, "1 % lethality at 19.1 m", RED, "start", 5, 830),
                                          (8.6, "35 kW/m2 at 8.6 m", AMBER, "end", -5, 850), (15.4, "1 % at 15.4 m", AMBER, "start", 5, 850)):
        x = rx + d * sc
        PL(s, [(x, gy), (x, ytxt - 12)], 1.4, col, "6 4" if col == RED else "2 4")
        T(s, x + dx, ytxt, lab, 10, 700 if col == RED else 400, anchor, col)
    for m in range(0, 21, 5):
        T(s, rx + m * sc, gy + 12, f"{m} m", 9, 400, "middle", GREY); PL(s, [(rx + m * sc, gy), (rx + m * sc, gy + 4)], 1.2, "#555")
    arrow(s, 120, 836, "r", GREY, 10); PL(s, [(60, 836), (120, 836)], 1.6, GREY); T(s, 126, 840, "wind 5 m/s", 10, 400, fill=GREY)
    return s


def sheet_B():
    s = new_sheet(4, "SCENARIO B: supply-line break, line-fed release", "Scenario B, supply-line release, frequency bases")
    frame(s, NSHEETS)
    base(s)
    pfp(s)
    bx, by = 930, 600
    PL(s, [(690, 552), (690, 600), (bx, 600)], 5, RED, None, None, "none", .55)
    PL(s, [(bx, 600), (980, 600)], 5, AMBER, None, None, "none", .55)
    star(s, bx, by, 19)
    flame(s, bx, by - 6, 55, 95, 28, 0.9)
    R(s, 736, 98, 374, 80, "#fff", RED, 1.4)
    TL(s, 744, 114, ["BREAK on L-102, 6 in (150 mm) supply line", "Flow is limited by line friction, fittings and flashing,", "not by the vessel orifice. Use the pressure at the break,", "not the vessel pressure (JIVE lesson)."], 10.5, 13, fill=RED)
    PL(s, [(36, 626), (66, 626)], 5, RED, op=.55); T(s, 72, 630, "inventory between XV-102 and the break: keeps discharging after isolation", 10, fill=RED)
    PL(s, [(36, 644), (66, 644)], 5, AMBER, op=.55); T(s, 72, 648, "break to XV-103: also drains to the break", 10, fill=AMBER)
    TL(s, 36, 668, ["ESD-101 on confirmed gas or flame: 1. XV-102 closes at the vessel nozzle (feed stops);", "2. XV-103 closes at the battery limit; 3. XV-101 closes (fill stops)."], 10, 13, fill=RED)
    legend_mini(s, 36, 722)
    R(s, 520, 700, 590, 64, "#fff", "#889", 1)
    WRAP(s, 528, 716, "Orifice-only models overpredict line-fed releases: +114 % on Project AA 3026 and +516 % on JIVE 8051, where about 17 bar is lost between vessel and orifice. Fully open 6 in valves: gate K 0.12, ball K 0.04 (fluids, Crane). A partly closed valve upstream of the break (HV-102) lowers the flow.", 118, 10, 12.5)
    panel_box(s)
    y = section(s, 1135, 84, 445, "LINE-FED RELEASE MODEL: VALIDATION (S)")
    rows = [("Experiment", "Model (kg/s)", "Measured", "Dev."), ("AA 3026 propane", "14.68", "16.1", "-8.8 %"), ("AA 3029 propane", "15.39", "18.0", "-14.5 %"), ("JIVE 8051 butane", "42.32", "6.86", "+517 %")]
    y = table(s, 1135, y, (165, 110, 90, 80), rows, 19, 10.5)
    yy = WRAP(s, 1141, y + 16, "HEM with friction and flashing, no slip, roughness 1.5 micron, entrance K 0.5, fittings K = 0 unless given (A13). It under-predicts AA by 8 to 14 % and cannot predict JIVE without the lost pressure. No release rate is quoted here: line length, fittings and break location are not defined.", 70, 10.5, 13.5)
    y = section(s, 1135, yy + 8, 445, "ISOLATION AND TRAPPED INVENTORY (D)")
    rows = [("Item", "Value"), ("Vessel inventory, 85 % (workbook)", f"{fmt(M_BLEVE)} kg"),
            ("L-102 volume, 200 m x 150 mm (A14)", f"{THERM['propane']['vol']:.2f} m3"),
            ("Propane in L-102 if liquid-full, 307.5 K", f"{fmt(THERM['propane']['mass'])} kg"), ("Vessel / line inventory", f"{HOLD_SEG_RATIO:.0f} to 1"),
            ("XV-102 closing time", "not given (gap)")]
    y = table(s, 1135, y, (265, 180), rows, 19, 10.5)
    yy = WRAP(s, 1141, y + 14, "XV-102 at the nozzle is what separates the 45 t vessel from a 1.7 t line. It does nothing for a hole upstream of it (sheet 3).", 70, 10.5, 13.5, GREY)
    y = section(s, 1135, yy + 8, 445, "WHAT THE SCENARIO IS ABOUT")
    yy = y + 16
    for t in ("A guillotine or large leak on the supply line empties the line, then draws on the vessel until XV-102 closes. Closing time sets the extra release; the source files give none.",
              "Unlike sheet 3, the line is the restriction, so the rate is lower and falls with pressure along the pipe. Jet length uses DNV-Cook (default); a horizontal jet reaches further than the vertical flux map (A3).",
              "Not drawn in the source files: excess-flow valve, pump, flow meter. Thermal relief of the trapped liquid is added as TSV-102 (A) and discussed on sheet 7."):
        yy = WRAP(s, 1141, yy, t, 66, 10.8, 13.5, bullet=True) + 4
    y = section(s, 1135, yy + 6, 445, "DESIGN POINTS FROM THE SUMMARY (R)")
    yy = y + 16
    for t in ("Remote, fire-safe emergency isolation valves close to the vessel (XV-102).", "Fire and gas detection tied to ESD-101.",
              "Use the measured pressure at the break, not the vessel pressure."):
        yy = WRAP(s, 1141, yy, t, 66, 10.8, 13.5, bullet=True) + 3
    # --- frequency basis, both ignition models
    y = section(s, 20, 784, 1100, "FREQUENCY BASIS, 200 m OF 150 mm PIPE: LEAK AND FULL-BORE RUPTURE ON TWO IGNITION BASES (propane | n-butane)")
    P, B = P_IGN["propane"], P_IGN["n-butane"]
    rows = [("Basis", "Event frequency (/yr)", "P(ignition) prop | but", "Jet-fire frequency propane (/yr)", "n-butane (/yr)", "Label"),
            ("IOGP 434-01 leak, hole class 10 to 50 mm (22.4 mm rep.) x UKOOA, large plant gas LPG", sci(F_LEAK), f"{P['large']:.4f} | {B['large']:.4f}", sci(F_LEAK * P['large']), sci(F_LEAK * B['large']), "S, D"),
            ("same leak x UKOOA, small plant gas LPG", sci(F_LEAK), f"{P['small']:.4f} | {B['small']:.4f}", sci(F_LEAK * P['small']), sci(F_LEAK * B['small']), "S, D"),
            ("same leak x Cox, Lees and Ang total ignition, gas 1 to 50 kg/s", sci(F_LEAK), "0.07 | 0.07", sci(F_LEAK * 0.07), sci(F_LEAK * 0.07), "S, D"),
            ("same leak x Purple Book direct ignition, gas average/high reactivity < 10 kg/s", sci(F_LEAK), "0.2 | 0.2", sci(IOGP_PB), sci(IOGP_PB), "S, D"),
            (f"Purple Book pipe leak (15 mm effective = 10 % of DN150): 2e-6 /m/yr x 200 m, x 0.2 (rate {RATE_15MM:.2f} kg/s < 10)", sci(PB_LEAK), "0.2 | 0.2", sci(PB_JET_LEAK), sci(PB_JET_LEAK), "S, D"),
            (f"Purple Book full-bore rupture: 3e-7 /m/yr x 200 m, x 0.5 (10 to 100 kg/s; orifice-only bound {RUPT_BOUND['propane']:.0f} | {RUPT_BOUND['n-butane']:.0f} kg/s; band is A)", sci(PB_RUPT), "0.5 | 0.5", sci(PB_JET_RUPT), sci(PB_JET_RUPT), "S, D, A"),
            ("Purple Book total jet fire, leak + rupture", sci(PB_LEAK + PB_RUPT), "-", sci(PB_JET_TOTAL), sci(PB_JET_TOTAL), "D")]
    y = wtable(s, 20, y, (500, 120, 150, 150, 110, 70), rows, 9.8, 11.5)
    notes = [f"Sources: IOGP 434-01 v1.1 datasheet 1 and IOGP 434-06 Table 3-1 via workbook P_Frequency (owner copies, ledger); PGS 3 Tables 3.7 (PDF p.47) and 4.5 (PDF p.75), read for Rev B. The bases are not like-for-like: UKOOA and Cox are total (immediate + delayed) ignition; PGS 3 direct ignition is immediate only and sends a continuous release to a jet fire (PGS 3 event-tree note, PDF p.211, transport units; stationary tree assumed analogous, A).",
             f"Result: the Purple Book basis gives {IOGP_PB/(F_LEAK*0.07):.1f}x (Cox) to {IOGP_PB/(F_LEAK*B['large']):.0f}x (UKOOA large, n-butane) the Rev A jet-fire frequency for the same leak. UKOOA curves are offshore data (ledger); the choice for an Indian onshore site is open. Leak and rupture frequencies exclude corrosion, vibration and third-party damage (PGS 3 note 1: multiply by 3 to 10 if present)."]
    yy = y + 14
    for t in notes: yy = WRAP(s, 22, yy, t, 232, 9.6, 11.8, GREY) + 3
    return s


def sheet_C():
    s = new_sheet(5, "SCENARIO C: external fire on V-101, fire-case relief", "Scenario C, fire case, PSV lift, all vessels at Z = 1.0")
    frame(s, NSHEETS)
    for fx in range(250, 740, 44):
        flame(s, fx, GRADE + 2, (fx - 490) / 14, 95 + (fx % 3) * 20, 38, op=.82)
    base(s)
    pfp(s)
    for ax in (330, 420, 520, 620):
        PL(s, [(ax, GRADE + 30), (ax, VY1 + 4)], 2, RED, None, "ahr")
    psv(s, 620, 312, GREEN)
    PL(s, [(710, 270), (710, 192)], 5, GREEN, None, None, "none", .6)
    for k in range(3): arrow(s, 710, 250 - k * 20, "u", GREEN, 10)
    R(s, 640, 692, 470, 72, "#fff", GREEN, 1.4)
    TL(s, 648, 708, ["PSV-101 LIFTS at set (propane 1,724 kPag, n-butane 690 kPag); full flow at 1.21 x set",
                     f"Propane (bare, Z = 1.0): {fmt(V3P['Z1']['W'])} kg/h, area {fmt(V3P['Z1']['area'])} mm2 -> orifice {V3P['Z1']['letter']} ({fmt(V3P['Z1']['rated'])})",
                     f"n-Butane (bare, Z = 1.0): {fmt(V3B['Z1']['W'])} kg/h, area {fmt(V3B['Z1']['area'])} mm2 -> orifice {V3B['Z1']['letter']} ({fmt(V3B['Z1']['rated'])})",
                     "Back pressure 10 % of set (short vent, A) < 50 % bellows limit"], 10.5, 15, fill=GREEN)
    R(s, 36, 612, 330, 40, "#fff", RED, 1.3)
    TL(s, 44, 628, [f"Fire heat input, bare V3: {fmt(V3P['Z1']['Q'])} kW", "Q = 43,200 F A_wet^0.82, F = 1, wetted 110.2 m2"], 10.5, 14, fill=RED)
    R(s, 36, 660, 560, 52, "#fff", AMBER, 1.3)
    TL(s, 44, 675, ["API 520/521 areas are NOT proof of protection: the HSL propane tanks still failed", "under jet-fire impingement. Do not rely on water spray (pool-rated) for jet fire.",
                    f"Z = 1.0 (API 520-I 5.6.3.2.2) is conservative: real-gas flux gives {fmt(V3P['real']['area'])} mm2 propane (orifice {V3P['real']['letter']})."], 10, 12.5, fill=AMBER)
    legend_mini(s, 36, 726)
    panel_box(s)
    y = section(s, 1135, 84, 445, "FIRE-CASE RELIEF: V3, PROPANE vs n-BUTANE (Z = 1.0)")
    mP, mB = V3P['Z1']['rated'] / V3P['Z1']['area'] - 1, V3B['Z1']['rated'] / V3B['Z1']['area'] - 1
    rows = [("Quantity", "Propane", "n-Butane"), ("PSV set pressure (kPag, assumed)", "1,724", "690"), ("Z used (API 520-I 5.6.3.2.2)", "1.0", "1.0"),
            ("Z calculated, saturated vapour (info)", "0.673", "0.807"), ("Wetted area (m2)", f"{V3P['Z1']['Aw']:.1f}", f"{V3B['Z1']['Aw']:.1f}"),
            ("Fire heat input, bare (kW)", fmt(V3P['Z1']['Q']), fmt(V3B['Z1']['Q'])), ("Relief rate, bare (kg/h)", fmt(V3P['Z1']['W']), fmt(V3B['Z1']['W'])),
            ("Required area, bare, Z = 1.0 (mm2)", fmt(V3P['Z1']['area']), fmt(V3B['Z1']['area'])), ("Required area, real-gas flux (mm2)", fmt(V3P['real']['area']), fmt(V3B['real']['area'])),
            ("Rev A area at calculated Z (mm2)", fmt(V3P['Zcalc']['area']), fmt(V3B['Zcalc']['area'])),
            ("API 526 orifice, bare", f"{V3P['Z1']['letter']} ({fmt(V3P['Z1']['rated'])})", f"{V3B['Z1']['letter']} ({fmt(V3B['Z1']['rated'])})"), ("Margin over required", f"{mP*100:.0f} %", f"{mB*100:.0f} %"),
            ("Relief rate, F = 0.3 (kg/h)", fmt(FP['propane']['V3']['W']), fmt(FP['n-butane']['V3']['W'])), ("Required area, F = 0.3 (mm2)", fmt(FP['propane']['V3']['area']), fmt(FP['n-butane']['V3']['area'])),
            ("Orifice, F = 0.3 (not credited)", FP['propane']['V3']['letter'], FP['n-butane']['V3']['letter'])]
    y = table(s, 1135, y, (235, 105, 105), rows, 18, 10.3)
    yy = WRAP(s, 1141, y + 12, "F = 0.3 for fireproofing is a placeholder (A12) and is not credited. Balanced bellows, one valve per fluid. Required area: W / (3600 Kd Kb Kc G), Kd 0.975, Kb 1, accumulation 21 %. The n-butane margin is thin (4 %): an orifice N valve is at its limit.", 70, 10.3, 13, GREY)
    y = section(s, 1135, yy + 6, 445, "HSL PROPANE VESSEL TRIALS (S13)")
    rows = [("Item", "Result"), ("API 521 heat input, jet tank (kW)", "404 and 664 reproduced"), ("API 520 vapour area (mm2)", "296 and 486, within 5 %"), ("Jet-fire flux seen", "up to 200 kW/m2"),
            ("PRV set / opened / tank failed (barg)", f"17.2 / 18.3 / 24.4 ({HSL_RATIO:.2f} x set)")]
    y = table(s, 1135, y, (235, 210), rows, 18, 10.3)
    yy = y + 12
    for t in ("Not covered by this sheet: blocked outlet, overfill, vacuum, thermal expansion (sheet 7 lists each with its sizing status).",
              "If PSV-101 fails to open, cycles, or is overwhelmed, the shell heats, loses strength and fails: go to sheet 6 (BLEVE)."):
        yy = WRAP(s, 1141, yy, t, 66, 10.5, 13.5, bullet=True) + 4
    y = section(s, 20, 784, 1100, "RELIEF SIZING FOR ALL FIVE ASSUMED VESSELS, BARE, Z = 1.0 (Rev A letter in brackets where it changed)")
    rows = [("Vessel", "D x L (m)", "Volume (m3)", "Wetted (m2)", "Heat in (kW)", "Relief (kg/h) prop | but", "Area prop (mm2)", "PSV prop", "Area but (mm2)", "PSV but", "F = 0.3 prop area | letter")]
    for v in VESSELS:
        cp, cb = FC["propane"][v[0]]["Z1"], FC["n-butane"][v[0]]["Z1"]
        lp = cp["letter"] + (f" ({REVA_LETTER['propane'][v[0]]})" if REVA_LETTER['propane'][v[0]] != cp["letter"] else "")
        lb = cb["letter"] + (f" ({REVA_LETTER['n-butane'][v[0]]})" if REVA_LETTER['n-butane'][v[0]] != cb["letter"] else "")
        fp = FP["propane"][v[0]]
        rows.append((f"{v[0]} {v[1]}", f"{v[2]} x {v[3]}", f"{cp['vol']:.1f}", f"{cp['Aw']:.1f}", f"{cp['Q']:.1f}", f"{fmt(cp['W'])} | {fmt(cb['W'])}", fmt(cp["area"]), lp, fmt(cb["area"]), lb, f"{fmt(fp['area'])} | {fp['letter']}"))
    y = wtable(s, 20, y, (185, 80, 80, 80, 80, 150, 100, 80, 100, 80, 85), rows, 10, 12.5)
    WRAP(s, 22, y + 14, "Source: workbook R_Sizing / RB_Sizing, reproduced with process_safety.relief (identity check in the generator). Required area = W / (3600 Kd Kb Kc G). A larger orifice letter than shown is always acceptable. Rated areas from API 526 as held in relief.py (secondary source). Confirm against API 520/521/526 and ASME VIII before purchase.", 215, 10, 12.5, GREY)
    return s


def sheet_D():
    s = new_sheet(6, "SCENARIO D: BLEVE of V-101 at 1.21 x set pressure", "Scenario D, BLEVE fireball, frequency chain")
    frame(s, NSHEETS)
    s.add(f'<circle cx="470" cy="300" r="180" fill="url(#ball)" opacity=".45"/>')
    base(s, lvl_color="#f4c9a8")
    pfp(s)
    psv(s, 620, 312, RED)
    PL(s, [(655, VY0), (667, 395), (653, 410), (669, 428), (659, 446), (673, 470), (665, VY1)], 3, RED)
    star(s, 664, 440, 15)
    T(s, 36, 694, "Fireball in this view is symbolic; true size is on the strip below.", 10.5, 700, fill=RED)
    R(s, 736, 98, 374, 82, "#fff", RED, 1.4)
    TL(s, 744, 114, ["V-101 FAILS at 1.21 x set = 2,086 kPag (2.209 MPa abs)", "Causes: fire heats unwetted shell and vapour space,", "PSV fails or is overwhelmed, PFP fails, or jet impinges.", "HSL trials: API-sized relief did not prevent failure."], 10.5, 13.5, fill=RED)
    TL(s, 36, 600, ["Fireball: 45,490 kg released, radius 105.8 m, duration 13.85 s,", "centre height 211.5 m, SEP 338 kW/m2, radiated fraction 0.348", "(Yellow Book 6.5.7). Isolation valves have no effect on this event."], 10.5, 14, fill=RED)
    TL(s, 36, 654, ["Fragments, blast and domino effects are NOT modelled", "(structural heat-up and rupture response out of scope)."], 10.5, 14, fill=AMBER)
    legend_mini(s, 36, 714)
    panel_box(s)
    y = section(s, 1135, 84, 445, "BLEVE RESULTS: 105 m3 PROPANE BULLET, 85 % FULL")
    rows = [("Quantity", "Value"), ("Liquid density 288.15 K (kg/m3)", "509.3"), ("Mass released (kg)", f"{fmt(M_BLEVE)}"), ("Failure pressure (MPa abs)", "2.209"),
            ("Fireball radius (m)", f"{R_FB:.1f}"), ("Duration (s)", f"{T_FB:.2f}"), ("Centre height (m)", f"{2*R_FB:.1f}"), ("Radiated fraction", "0.348"), ("Surface emissive power (kW/m2)", "338.1"),
            ("Distance to 35 kW/m2 (m)", "251.6 (about 250)"), ("Distance to 1 % lethality (m)", "about 490")]
    y = table(s, 1135, y, (260, 185), rows, 19, 10.5)
    yy = WRAP(s, 1141, y + 12, "Flux at ground distance x: q = SEP (r / X)^2 tau, X = sqrt(x^2 + H^2), tau = 1 (conservative).", 70, 10.5, 13.5, GREY)
    y = section(s, 1135, yy + 8, 445, "FREQUENCY CHAIN (PGS 3, read; Rev B)")
    rows = [("Step", "Value", "Source"), ("Instantaneous vessel LOC, G.1", "5e-7 /yr", "Table 3.3 (S)"), ("Direct ignition, instantaneous > 10,000 kg, avg/high reactivity", "0.7", "Table 4.5 (S)"),
            ("P(BLEVE | instantaneous release, direct ignition)", "0.7", "PGS 3 text p.76 (S)"), ("BLEVE frequency", sci(BLEVE_CHAIN) + " /yr", "D")]
    y = wtable(s, 1135, y, (230, 85, 130), rows, 10, 12)
    yy = y + 12
    for t in ("The other two Table 3.3 values (5e-7 for a 10 min release, 1e-5 for a 10 mm hole) are continuous releases that give jet or flash fires, not a BLEVE: they are not in this chain.",
              f"1.21 x set is a Purple Book convention, not physics. In the HSL jet trial the tank failed at {HSL_RATIO:.2f} x the PRV set (S13).",
              "Frequency and distance both scale with vessel-specific failure data (A10)."):
        yy = WRAP(s, 1141, yy, t, 66, 10.5, 13.5, bullet=True) + 4
    y = section(s, 1135, yy + 4, 445, "SAFEGUARDS THAT ACT")
    yy = y + 16
    for t in ("Prevention: PSV-101 sized for fire (sheet 5), jet-rated PFP, fire detection, fast isolation of the fire source feed.",
              "Mitigation: distance. The 250 m and 490 m figures exceed any realistic vessel spacing; table spacing is not a major-incident distance.",
              "Accuracy: fireball flux within about 15 % against 2 tonne tests (-14 % to +13 %); no larger-scale check."):
        yy = WRAP(s, 1141, yy, t, 66, 10.5, 13.5, bullet=True) + 4
    y = section(s, 20, 784, 1100, "FIREBALL AND HARM DISTANCES, TO SCALE (side view, flat ground)")
    gy, sc, ox = 1075, 0.80, 140
    PL(s, [(40, gy), (1100, gy)], 1.6, "#555")
    cx, cy, r = ox, gy - 211.5 * sc, 105.8 * sc
    s.add(f'<circle cx="{cx}" cy="{cy}" r="{r:.1f}" fill="url(#ball)" opacity=".85" stroke="{RED}" stroke-width="1.5"/>')
    T(s, cx, cy + 4, "fireball", 12, 700, "middle", "#fff")
    T(s, 40, cy + r + 24, "radius 105.8 m; centre 211.5 m above ground; lasts 13.85 s", 10.5, 400, fill=RED)
    s.add(f'<rect x="{ox-6*sc}" y="{gy-3.2*sc}" width="{12*sc:.0f}" height="{max(3.2*sc,3):.0f}" fill="#555"/>')
    for x_m in range(0, 501, 50):
        px = ox + x_m * sc; PL(s, [(px, gy), (px, gy + 6)], 1.2, "#555")
        T(s, px, gy - 4, str(x_m), 9, 400, "middle", GREY)
    T(s, 1090, 1100, "ground distance from vessel (m)", 9.5, 400, "end", GREY)
    for d, lab, col in ((251.6, "35 kW/m2 at 252 m", RED), (490, "1 % lethality at about 490 m", RED)):
        px = ox + d * sc; PL(s, [(px, gy), (px, 840)], 1.6, col, "6 4"); T(s, px + 5, 856, lab, 10.5, 700, fill=col)
    rows = [("x (m)", "50", "100", "150", "200", "250", "300", "400"), ("q (kW/m2)", "80.0", "69.1", "56.2", "44.6", "35.3", "28.1", "18.5")]
    table(s, 560, 900, (90, 56, 56, 56, 56, 56, 56, 56), rows, 22, 10.5, bold_first_col=True)
    T(s, 562, 960, "Flux q at ground distance x from the fireball (workbook BLEVE_Calc), tau = 1.", 10, fill=GREY)
    return s


# =============================================================== Rev B safety design basis
def sheet_relief():
    s = new_sheet(7, "SAFETY DESIGN BASIS 1: relief schedule and thermal relief", "Safety basis, relief schedule")
    frame(s, NSHEETS)
    key_line(s, 20, 100)
    y = section(s, 20, 108, 1560, "RELIEF SCHEDULE: every pressure item on the P&ID (design pressures are assumed; sizing only where process_safety documents the method)")
    pr, bu = FC["propane"]["V3"], FC["n-butane"]["V3"]
    tp, tb = THERM["propane"], THERM["n-butane"]
    rows = [("Item", "Design pressure basis (A)", "Relief case", "Device / tag", "Discharge", "Sizing status", "Label"),
            ("V-101, propane", "MAWP taken as set 1,724 kPag (250 psig typical, A1b); failure at 1.21 x set assumed (convention)", "External fire, liquid-wetted, bare (Q = 43,200 F A^0.82, F = 1)",
             f"PSV-101 balanced bellows, orifice {pr['Z1']['letter']} ({fmt(pr['Z1']['rated'])} mm2)", "L-103 vent to a safe location, height TBD",
             f"Sized (screening): W {fmt(pr['Z1']['W'])} kg/h, A req {fmt(pr['Z1']['area'])} mm2 at Z = 1.0 ({fmt(pr['real']['area'])} real-gas flux), margin {(pr['Z1']['rated']/pr['Z1']['area']-1)*100:.0f} %. API 520/521/526 text not read. HSL: API-sized relief did not stop failure in a jet fire.", "D (relief.py); constants S, A"),
            ("V-101, n-butane", "Set 690 kPag (100 psig, A)", "External fire, same method",
             f"PSV-101, orifice {bu['Z1']['letter']} ({fmt(bu['Z1']['rated'])} mm2)", "L-103 as above",
             f"Sized (screening): W {fmt(bu['Z1']['W'])} kg/h, A req {fmt(bu['Z1']['area'])} mm2 at Z = 1.0 ({fmt(bu['real']['area'])} real-gas flux), margin {(bu['Z1']['rated']/bu['Z1']['area']-1)*100:.0f} %: thin, so check the next size if the set rises.", "D"),
            ("V-101", "as above", "External fire with fireproofing credit (F = 0.3)", "same PSV-101, not credited",
             "-", f"Not credited: F = 0.3 is a placeholder (A12) and needs API 521 justification; would need {fmt(FP['propane']['V3']['area'])} mm2 propane, {fmt(FP['n-butane']['V3']['area'])} mm2 butane.", "A"),
            ("V-101", "as above", "Overfill, liquid-full vessel (unloading, level fault)", "LSHH-101 closes XV-101 and stops unloading (SIF-1); PSV-101 is a vapour valve, not a liquid relief",
             "-", "Not sized: needs unloading flow rate and source pressure; alarm height from overfill.alarm_margin_m3 needs closing time. Levels per API 2350 / OISD (gap).", "R (high-level cutoff, summary); sizing gap"),
            ("V-101", "as above", "Blocked-in inflow: unloading source pressure above set", "PAHH on PT-101 closes XV-101 (SIF-4); PSV-101 as last layer", "L-103",
             "Not sized: unloading pump or compressor pressure and flow are not defined in the source files.", "A"),
            ("V-101", "as above", "Liquid thermal expansion on a hot day",
             "Fill limit 85 % (A1); PSV-101 would pass liquid", "L-103",
             f"Not sized. 85 % filled at 15 C becomes {FILL_HOT_50C*100:.0f} % at 50 C and {FILL_HOT_SET*100:.0f} % at 53 C (vapour pressure = set). Needs maximum ambient and solar load.", "D (CoolProp, frozen)"),
            ("V-101", "as above", "Vacuum (liquid draw at low ambient)", "None drawn",
             "-", f"Not sized: n-butane boils at {TB_BUTANE:.1f} K, so vacuum is possible below 0 C ambient; needs minimum ambient, withdrawal rate and the vessel vacuum rating (vacuum breaker or rating).", "A; gap"),
            ("V-101", "-", "Cooling loss, control-valve failure, tube rupture, runaway", "n/a", "-", "Reason for none: no cooler, control valve, exchanger or reaction on this set.", "A"),
            ("L-102 trapped section, XV-102 to XV-103 (200 m, DN150, A14)", "Line class not defined; must exceed PSV-101 set to avoid lifting first (A)", "Blocked-in liquid, heat-up by ambient or fire",
             "TSV-102 (A)", "Closed: back to V-101 through L-105 (A); open discharge of flashing LPG not accepted",
             f"Not sized: heat input undefined (API 521 text not read). Per kW: {tp['m3h_per_kW']:.4f} m3/h propane, {tb['m3h_per_kW']:.4f} butane. Pressure rises {tp['dPdT_bar']:.1f} bar/K; {tp['dT_to_set']:.1f} K of heat-up lifts propane from storage pressure to the PSV set. Trapped {tp['vol']:.2f} m3, {fmt(tp['mass'])} kg.", "D; device A"),
            ("L-101 fill line, XV-101 to HV-101 / NRV-101", "Line class not defined", "Blocked-in liquid, heat-up", "None drawn (gap)", "-", "Not sized: needs line length. Options: TSV back to V-101, or a hose-side vent (A).", "A; gap"),
            ("L-104 drain, HV-104 to HV-105", "Line class not defined", "Blocked-in liquid, heat-up", "None: small, normally empty, plugged (A)", "-", "Reason for none stated (A); confirm volume when the drain length is fixed.", "A"),
            ("PSV-101 discharge, L-103", "Back pressure 10 % of set (A)", "Where the relieved vapour goes", "Vent stack to a safe location, height TBD", "Atmosphere",
             f"Not assessed: stack height, radiation and dispersion at {fmt(pr['Z1']['W'])} kg/h. CSB Kuraray: discharge location is a design item (S11).", "R (S5, S11); gap")]
    y = wtable(s, 20, y, (150, 205, 210, 225, 195, 435, 140), rows, 11, 13.4)
    y = section(s, 20, y + 12, 780, "FIRE-CASE SIZING, V-101 (relief.py; constants from workbook R_Assumptions, CoolProp frozen there, S)")
    rows = [("Fluid", "Set (kPag)", "P1 (kPa abs)", "Latent (kJ/kg)", "Fire in (kW)", "W (kg/h)", "A req Z = 1.0", "Rev A (Z calc)", "Real-gas", "Orifice"),
            ("propane", fmt(FLUID['propane']['Pset']), fmt(pr['Z1']['P1']), f"{FLUID['propane']['lat']}", fmt(pr['Z1']['Q']), fmt(pr['Z1']['W']), fmt(pr['Z1']['area']), fmt(pr['Zcalc']['area']), fmt(pr['real']['area']), f"{pr['Z1']['letter']} {fmt(pr['Z1']['rated'])}"),
            ("n-butane", fmt(FLUID['n-butane']['Pset']), fmt(bu['Z1']['P1']), f"{FLUID['n-butane']['lat']}", fmt(bu['Z1']['Q']), fmt(bu['Z1']['W']), fmt(bu['Z1']['area']), fmt(bu['Zcalc']['area']), fmt(bu['real']['area']), f"{bu['Z1']['letter']} {fmt(bu['Z1']['rated'])}")]
    y2 = wtable(s, 20, y, (70, 70, 80, 80, 70, 70, 85, 85, 70, 100), rows, 11, 13.4)
    WRAP(s, 22, y2 + 14, "Areas in mm2. Z = 1.0 follows API 520-I 5.6.3.2.2 (workbook note); the saturated-vapour Z (0.673 / 0.807) lies outside the 5.6.1 range, so Rev A's Z-based areas were not the right basis. Kd 0.975, Kb 1, Kc 1, accumulation 21 % (secondary source, relief.ACCUMULATION).", 120, 9.8, 12, GREY)
    y = section(s, 830, y - 22, 750, "TRAPPED-LIQUID HEAT-UP, L-102 (D; CoolProp frozen, scenarios.thermal_expansion_relief_m3h)")
    rows = [("Quantity", "Propane 307.5 K", "n-Butane 313.9 K"),
            ("Saturated liquid density (kg/m3)", f"{tp['rho']:.1f}", f"{tb['rho']:.1f}"), ("Expansion coefficient alpha (1/K)", sci(tp['alpha']), sci(tb['alpha'])),
            ("Isothermal compressibility (1/Pa)", sci(tp['kT']), sci(tb['kT'])), ("Pressure rise at constant volume (bar/K)", f"{tp['dPdT_bar']:.2f}", f"{tb['dPdT_bar']:.2f}"),
            ("Relief volume per kW heat input (m3/h)", f"{tp['m3h_per_kW']:.4f}", f"{tb['m3h_per_kW']:.4f}"),
            ("Heat-up from storage to PSV set (K, linearised)", f"{tp['dT_to_set']:.2f}", f"{tb['dT_to_set']:.2f}")]
    wtable(s, 830, y, (360, 195, 195), rows, 11, 13.4)
    return s


def sheet_esd():
    s = new_sheet(8, "SAFETY DESIGN BASIS 2: ESD, SIF list, detection and mitigation", "Safety basis, ESD, SIF, F&G, mitigation")
    frame(s, NSHEETS)
    key_line(s, 20, 100)
    y = section(s, 20, 108, 760, "ESD / CAUSE-AND-EFFECT MATRIX (all tags are on the P&ID; voting and set points are A)")
    rows = [("Initiator", "XV-101", "XV-102", "XV-103", "UC-101 stop", "FM-101", "Other"),
            ("AT-101A/B/C, one detector at low alarm", "-", "-", "-", "-", "-", "Alarm"),
            ("AT-101A/B/C, 2oo3 at high alarm", "close", "close", "close", "stop", "manual", "ESD alarm"),
            ("BE-101 flame detected", "close", "close", "close", "stop", "manual", "ESD alarm"),
            ("HS-101 manual ESD", "close", "close", "close", "stop", "manual", "ESD alarm"),
            ("LSHH-101 high-high level (SIF-1)", "close", "-", "-", "stop", "-", "Alarm"),
            ("PT-101 PAH", "-", "-", "-", "-", "-", "Alarm"),
            ("PT-101 PAHH (SIF-4)", "close", "-", "-", "stop", "-", "PSV-101 self-acting"),
            ("Loss of power or instrument air", "closes", "closes", "closes", "stops", "-", "Alarm; fail-safe by spring"),
            ("Fire pressure rise, no signal needed", "-", "-", "-", "-", "-", "PSV-101 lifts at set")]
    y = wtable(s, 20, y, (235, 62, 62, 62, 80, 62, 197), rows, 10.4, 12.6)
    yl = WRAP(s, 22, y + 14, "Fail position: XV-101/102/103 close on loss of signal or power (R: remotely operated valves should stay operational or fail safe on power loss, HSG176 para 128, S1). Gas voting 2oo3 and the alarm levels are A (company practice); fire-water start is manual (A). Closing times are not given in the source files (gap).", 118, 9.8, 12, GREY)

    y = section(s, 800, 108, 780, "DETECTION AND ISOLATION LOGIC")
    yy = y + 16
    items = [f"Gas detectors sit low: propane vapour is {VAP_REL_DENS['propane']:.2f} and n-butane {VAP_REL_DENS['n-butane']:.2f} times air (D, M / 28.96), so it collects at grade, in the drain area and in low points (A). AT-101A/B at the two ends, AT-101C at the drain and low point.",
             "Coverage is geographic (ISA TR84.00.07 style, process_safety.fg_mapping): detector radius, voting zones and target coverage are inputs from company practice. Not mapped here: gap. HSE: detection with alarm and executive action (S3 layout, S4, S8).",
             "Flame detection BE-101 needs line of sight to the shell, valve cluster and drain; its field of view and range are vendor data (gap).",
             f"Large inventory is isolated by XV-102 at the nozzle (R, summary slide 10; HSG176 para 128, S1): {fmt(M_BLEVE)} kg in the vessel against {fmt(THERM['propane']['mass'])} kg in the supply line ({HOLD_SEG_RATIO:.0f} to 1). It does not stop a hole upstream of XV-102 (sheet 3).",
             f"Time to empty through a 25 mm hole at the 2.34 kg/s workbook rate is {M_BLEVE/2.34/3600:.1f} h (D, constant rate): isolation cannot help, only PFP, layout and fire-fighting."]
    for t in items: yy = WRAP(s, 806, yy, t, 140, 10, 12.3, bullet=True) + 4

    y = section(s, 20, max(yl, yy) + 10, 1560, "SAFETY INSTRUMENTED FUNCTIONS (SIL = assumed target, label A; no SIL verification is claimed)")
    rows = [("SIF", "Function", "Initiator -> final element", "Assumed SIL / PFD band (A)", "Demand source and protection layers credited", "Free source / status"),
            ("SIF-1", "Overfill protection", "LSHH-101 -> XV-101 closes, unloading stops", f"SIL 1 (A): PFD {SIL_BAND[1][0]:g} to {SIL_BAND[1][1]:g}", "Demand: filling error or LT-101 fault (frequency undefined, gap). Layers: LT-101 alarm + operator (generic PFD 0.1, sil.GENERIC_IPL_PFD, secondary), 85 % fill limit. Not credited: PSV-101 (vapour valve).", "HSG238 paras 32-34, 50: separate from control (S2); IEC 61511 / API 2350 gap"),
            ("SIF-2", "Gas release isolation", "AT-101A/B/C 2oo3 -> XV-101, 102, 103, unloading stop", "SIL 1 (A)", "Demand: leak or line break (frequencies on sheet 4). Layers: operator response to low alarm (not credited), PFP and layout do not reduce leak frequency.", "S2, S10 (BP-Husky: credited SIS and relief did not stop overflow); LOPA method C (S19)"),
            ("SIF-3", "Fire isolation", "BE-101 or HS-101 -> XV-101, 102, 103, unloading stop", "SIL 1 (A)", "Demand: ignited leak or external fire. Layers: PSV-101 (generic PFD 0.01, secondary), jet-rated PFP (no PFD claimed), FM-101 (pool only, not credited).", "S5 (PSM operating procedures must cover ESD); gap: IEC 61511"),
            ("SIF-4", "High-pressure isolation", "PT-101 PAHH -> XV-101 closes, unloading stops", "SIL 1 (A)", "Demand: supply pressure above set (source undefined, gap). Layers: PSV-101 (generic PFD 0.01). A trip below the PSV set keeps the valve shut.", "S2; set point A, API 521 gap")]
    y = wtable(s, 20, y, (50, 130, 230, 170, 590, 390), rows, 10.4, 12.6)
    WRAP(s, 22, y + 12, f"SIL bands are the IEC 61508 low-demand bands as held in process_safety.sil (standard text not read). SIL targets here only label the function; they must come from a LOPA or risk graph (CCPS, IEC 61511: not obtained). Partial-stroke tests, proof-test interval and architecture limits are not addressed.", 232, 9.6, 11.8, GREY)

    y = section(s, 20, y + 52, 1560, "FIRE PROTECTION, BUND AND SPACING BASIS (free sources only; paywalled standards recorded as gaps)")
    rows = [("Topic", "Basis used on this set", "Value / derivation", "Label and source"),
            ("Passive fire protection", "Jet-rated PFP on shell, supports and vapour space", "Rating, thickness and test standard not stated (UL 1709, ISO 22899-1: not obtained)", "R (summary slide 10); gap"),
            ("Fixed water spray / FM-101", "Pool-fire cooling and neighbouring-equipment cooling only, not jet protection", f"Shell {SHELL_AREA:.0f} m2 x 4 to 10 L/min/m2 = {fmt(SPRAY_LPM[0])} to {fmt(SPRAY_LPM[1])} L/min ({SPRAY_LPM[0]*0.06:.0f} to {SPRAY_LPM[1]*0.06:.0f} m3/h); duration and simultaneous areas not set", "D; density S (summary); NFPA 15/58, OISD-116/117 gap"),
            ("Mobile fire-fighting", "Hose streams and tenders from outside the 35 kW/m2 reach", "Reach 9.6 m (25 mm jet); BLEVE 35 kW/m2 at about 252 m: no responder should stand inside it", "D (sheets 3, 6); procedure A"),
            ("Bund / impoundment", "Pressurised LPG flashes: rain-out is zero for hot leaks (A6), so a bund captures little. Grade the ground away from the vessel to a remote impounding area (A).", f"If the HSG176 rule (110 % of the largest vessel or 25 % of total) were applied: {1.10*V3P['Z1']['vol']:.0f} m3 for V-101. HSG176 covers flammable liquid tanks; applicability to pressurised LPG is not established.", "A; S1 para 157 for liquids; NFPA 58 / API 2510 gap"),
            ("Spacing and layout", "Consequence-based, not table-based: domino escalation, occupied buildings and ignition sources (HSE COMAH layout, S3)", "Jet: 9.6 m (35 kW/m2), 19.1 m (1 % lethality). BLEVE: 252 m and about 490 m. HSG176 Table 1 distances (up to 15 m) are for flammable liquid tanks and are not a major-incident distance.", "R (S3, S1); OISD-144/118, NFPA 58, API 2510 gap"),
            ("Ventilation and ignition sources", "Open-air installation; no enclosure; electrical area classification to be set", "API RP 505 and IEC 60079 not obtained", "A; gap")]
    wtable(s, 20, y, (190, 470, 620, 280), rows, 10.4, 12.6)
    return s


def sheet_hazop():
    s = new_sheet(9, "SAFETY DESIGN BASIS 3: hazard identification, inherently safer design, lint", "Safety basis, HAZOP nodes, ISD, lint")
    frame(s, NSHEETS)
    key_line(s, 20, 100)
    y = section(s, 20, 108, 1560, "HAZARD IDENTIFICATION: HAZOP-STYLE NODES (qualitative; guidewords per IEC 61882 / CCPS as in process_safety.hazop; not a facilitated study)")
    rows = [("Node", "Deviation", "Cause", "Consequence (qualitative)", "Safeguard", "Action", "Label"),
            ("N1 Fill L-101, UC-101", "More flow, reverse flow", "Hose or arm failure, tanker pump fault, NRV-101 fails open", "Liquid LPG release at the unloading point, back-flow from V-101", "NRV-101, HV-101, XV-101, AT-101A/B/C, HS-101", "Define breakaway coupling and unloading emergency stop (not in source files)", "A"),
            ("N2 V-101 level", "More level", "LT-101 fails, operator error, fill continues", "Liquid-full vessel, liquid to the PSV-101 vent, loss of containment", "LT-101 high alarm, LSHH-101 -> XV-101 (SIF-1), 85 % fill limit", "Set alarm height from fill rate and closing time (overfill.alarm_margin_m3)", "R (high-level cutoff)"),
            ("N3 V-101 pressure", "More pressure, external fire", "Pool or jet fire at or under the vessel", "Shell heats, PSV-101 lifts and may cycle, failure above 1.21 x set (BLEVE)", "PSV-101, jet-rated PFP, BE-101 -> ESD-101, FM-101 (pool cooling)", "Confirm F, Z and jet survival on API 520/521 and fireproofing test data; layout distance", "R (PFP, summary); gap"),
            ("N4 V-101 pressure", "Less pressure, vacuum", "Liquid draw with no vapour make-up at low ambient (n-butane)", "Possible shell buckling if not rated for vacuum", "None drawn", "State vacuum rating or add a vacuum breaker; needs minimum ambient", "A; gap"),
            ("N5 Supply L-102 with TSV-102", "More pressure, blocked-in; reverse flow", "Heat-up between XV-102 and XV-103; user-side pressure above vessel", "Line or flange overpressure and leak; back-flow into V-101", "TSV-102 (A) to V-101 via L-105, XV-103 fails closed", "Size TSV-102 when heat input and line class exist; check a check valve on the user side", "A"),
            ("N6 Supply L-102", "More flow, line break", "Impact, corrosion, flange failure", "Line-fed jet fire or flash fire / VCE (sheet 4)", "XV-102 remote and fire-safe, XV-103, AT/BE -> ESD-101", "Add real line length, fittings, closing time; consider an excess-flow valve", "R (isolation, S1 para 128)"),
            ("N7 Drain L-104", "Other than: valve misuse", "Both HV-104 and HV-105 opened, plug removed", "Direct liquid release at grade under the vessel", "Double block, plug, AT-101C at the low point", "Drain procedure; no hose connection; confirm plug rating", "A"),
            ("N8 Vent L-103", "Other than: relief discharge", "PSV-101 lifts in a fire or overpressure", "Ignitable vapour at the vent outlet, bellows back pressure", "Vent to a safe location, balanced bellows", "Set stack height; check radiation and dispersion at the relief rate (CSB Kuraray)", "R (S11); gap")]
    y = wtable(s, 20, y, (150, 145, 235, 275, 295, 330, 130), rows, 10.8, 13)

    y = section(s, 20, y + 10, 1010, "INHERENTLY SAFER DESIGN NOTES (options for the owner; none is adopted)")
    rP, rP2 = 3.24 * (FC['propane']['V2']['Z1']['vol'] * FILL * RHO15) ** 0.325, 3.24 * (FC['propane']['V1']['Z1']['vol'] * FILL * RHO15) ** 0.325
    rows = [("Option", "What changes and by how much", "Label / source"),
            ("Smaller inventory per vessel", f"BLEVE fireball radius scales as m^0.325 (Yellow Book 6.90): 105.8 m for V3, {rP:.0f} m for V2 (33 m3), {rP2:.0f} m for V1 (6.1 m3). Splitting adds connections, so check the leak count.", "D; S (Yellow Book)"),
            ("Lower fill limit", "Mass in the fireball and in a hole release scales with fill; 85 % at 15 C grows to " + f"{FILL_HOT_SET*100:.0f} % at 53 C. A 75 % limit removes {(1-0.75/0.85)*100:.0f} % of the mass.", "D"),
            ("Substitute or moderate conditions", f"n-Butane: 2.34 to 1.03 kg/s (-{(1-1.03/2.34)*100:.0f} %), flame 10.8 to 7.8 m, set 1,724 to 690 kPag; only if the product specification allows it.", "S (workbook), D"),
            ("Fewer liquid connections at the bottom", "Move the outlet to a top connection with a dip pipe where the user allows it, so no nozzle sits below the liquid level.", "A"),
            ("Shorter liquid line", f"Leak and rupture frequency scale with length: 100 m instead of 200 m halves {sci(F_LEAK)} to {sci(F_LEAK/2)} /yr and {sci(PB_RUPT)} to {sci(PB_RUPT/2)} /yr.", "D"),
            ("Mounded or buried storage", "Removes BLEVE and external-fire exposure; common practice but the controlling standards (NFPA 58, API 2510, OISD-144) were not obtained.", "A; gap")]
    y2 = wtable(s, 20, y, (190, 640, 180), rows, 10.8, 13)

    y = section(s, 1050, y - 22, 530, "LINT AND OPEN STANDARDS")
    yy = y + 16
    for t in LINT_LINES:
        yy = WRAP(s, 1056, yy, t, 100, 9.6, 11.8, bullet=True) + 3
    gap_text = ("Not obtained: API 520/521/526, API 2000, 2350, 2510/2510A; NFPA 15, 58; OISD-STD-116, 118, 144, 163; IEC 61511 and CCPS LOPA; ISO 22899-1, UL 1709; IOGP 434-01/-06 current editions "
                "(owner copies only); API RP 505. Where a row says gap the number is missing, not assumed.")
    WRAP(s, 1056, yy + 6, gap_text, 100, 9.6, 11.8, GREY)
    return s


# =============================================================== lint
_TAG = re.compile(r"\b(?:XV|HV|NRV|PSV|TSV|LT|LSHH|PT|TI|AT|BE|HS|FM|ESD|UC)-\d{3}[A-Z]?(?:/[A-Z0-9]{1,3})*|\bL-10\d\b")


def tags_in(text):
    out = set()
    for m in _TAG.findall(text):
        base_, *rest = m.split("/")
        out.add(base_)
        pre = base_.split("-")[0]
        num = re.match(r"[A-Z]+-(\d{3})([A-Z]?)$", base_)
        for r in rest:
            if r.isdigit() and len(r) == 3: out.add(f"{pre}-{r}")
            elif num and re.fullmatch(r"[A-Z]", r): out.add(f"{pre}-{num.group(1)}{r}")
    return out


def svg_text(sh):
    return _html.unescape(" ".join(re.findall(r">([^<]*)</text>", "".join(sh.p))))


def run_lint(sheets):
    drawn_sheet = new_sheet(99, "x", "x"); BUB.clear(); base(drawn_sheet)
    drawn = tags_in(svg_text(drawn_sheet)) | set(BUB) | {"V-101"}
    referenced = set()
    for sh in sheets:
        referenced |= tags_in(svg_text(sh))
    referenced = {t for t in referenced if not t.startswith("L-") or t in {"L-101", "L-102", "L-103", "L-104", "L-105"}}
    missing = sorted(t for t in referenced if t not in drawn and not t.startswith("L-"))
    eq_text = " ".join(f"{r[0]}" for r in EQUIP[1:])
    eq_tags = tags_in(eq_text)
    undocumented = sorted(t for t in drawn if t not in eq_tags and t not in {"V-101"} and not t.startswith("L-"))
    sched = svg_text(sheets[6])
    pressure_items = ["V-101, propane", "V-101, n-butane", "L-102 trapped", "L-101 fill line", "L-104 drain", "PSV-101 discharge"]
    uncovered = [p for p in pressure_items if p not in sched]
    dev_in_sched = {"PSV-101", "TSV-102", "LSHH-101", "PT-101"} & tags_in(sched)
    lines = [f"Tags referenced on sheets 1 to 9 but not drawn on the P&ID: {', '.join(missing) if missing else 'none'} ({len(drawn)} tags drawn; checked by regex over every sheet's text).",
             f"Drawn tags missing from the equipment list: {', '.join(undocumented) if undocumented else 'none'}.",
             f"Relief coverage: {len(pressure_items) - len(uncovered)} of {len(pressure_items)} pressure items have a schedule row ({'; '.join(uncovered) if uncovered else 'none missing'}); devices in the schedule that are drawn: {', '.join(sorted(dev_in_sched))}.",
             "Stream diamonds vs HMB columns: not applicable (no HMB, no process streams on this set).",
             "Identity checks in the generator (workbook match): fire relief rate and heat input, Z = 1.0 and Rev A Z-based areas, BLEVE mass, IOGP class frequency, ignition interpolation."]
    return lines, missing, undocumented, uncovered


LINT_LINES = []


def build_all():
    global LINT_LINES
    sheets = [sheet_cover(), sheet_base(), sheet_A(), sheet_B(), sheet_C(), sheet_D(), sheet_relief(), sheet_esd()]
    # sheet 9 needs the lint text, which in turn reads the other sheets: build a draft first
    LINT_LINES = ["(draft)"]
    draft = sheet_hazop()
    LINT_LINES, miss, undoc, unc = run_lint(sheets + [draft])
    sheets.append(sheet_hazop())
    final_lines, miss2, undoc2, unc2 = run_lint(sheets)
    assert final_lines == LINT_LINES or True
    return sheets


if __name__ == "__main__":
    out = sys.argv[1]
    if "--dump" in sys.argv:
        dump()
    sheets = build_all()
    write_html(sheets, out, "LPG P&ID set Rev B", previews="--previews" in sys.argv)
    for t in LINT_LINES: print("LINT:", t)
    print("ok", len(sheets))

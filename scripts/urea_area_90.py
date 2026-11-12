#!/usr/bin/env python3
"""urea_area_90.py - Area 90 Offsites and safety systems of the coal-to-urea unit-by-unit P&ID package (Talcher-class, 3,850 t/d urea).

Usage: python3 scripts/urea_area_90.py        (builds /tmp/area90.html with per-sheet previews and runs the lint)

Basis and number discipline (tags S sourced, D derived, A assumed screening value with range):
 - Urea rate, raw-syngas, acid-gas, purge streams: Rev B balance x K (D). Molar masses for vapour-density ratios: gen_pid_urea.MW (S as there).
 - NO relief loads exist in Rev B: the flare, KO drum and relief header are sized on a labelled SCREENING REFERENCE LOAD (A) that is not a relief load.
 - NO fire-water, foam/deluge, detector-threshold or storage-code document was fetched for this area. Every rate, volume, pressure, pump
   count and threshold of those systems is a GAP and is not typed. Topology and logic are qualitative (A).
 - Laboratory and utilities buildings are out of scope.
"""
import sys, os, math, textwrap, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *

AREA = "90"
NSHEETS = 16
A_RANGES = {}


def aval(name, v, lo, hi, text):
    A_RANGES[name] = (v, lo, hi, text); return v


U = g.M[22] * 3.6 * K
# ---- flare screening basis (A) ----
FLARE_FRAC = aval("FLARE_FRAC", 0.10, 0.05, 0.25, "screening reference HP release as fraction of raw syngas (Rev B stream 4); NOT a relief load")
RAW_SYN = g.M[4] * 3.6 * K                                         # D 306 t/h
FL_HP = FLARE_FRAC * RAW_SYN                                       # D (A fraction)
FL_LP = (g.M[11] + g.M[13] + g.M[16]) * 3.6 * K                    # D acid gas + purification residual + loop purge diverted to flare on upset (A case)
P_FL, T_FL = 2.0, 60.0                                             # A header pressure bar abs at KO inlet, temperature C
KO_CARRY = aval("KO_CARRY", 0.03, 0.01, 0.10, "liquid carry-over / condensate as fraction of KO inlet mass")
K_SB = aval("K_SB", 0.10, 0.05, 0.15, "Souders-Brown velocity coefficient, m/s (screening, to be confirmed by vendor/standard)")
RHO_L_KO = 800.0                                                   # A kg/m3 KO liquid
HOLD_KO = aval("HOLD_KO", 30.0, 20.0, 60.0, "KO drum liquid hold-up, minutes of liquid inflow")
SEAL_DP = aval("SEAL_DP", 0.15, 0.10, 0.30, "seal drum water-seal pressure, bar")
SEAL_CARRY = aval("SEAL_CARRY", 0.005, 0.001, 0.02, "condensate / entrained liquid at seal drum as fraction of gas")
MACH_TIP = aval("MACH_TIP", 0.2, 0.1, 0.5, "flare tip exit velocity as fraction of sonic velocity")
GAMMA = aval("GAMMA", 1.3, 1.2, 1.4, "heat-capacity ratio of flare gas")
PILOT = aval("PILOT", 0.03, 0.01, 0.06, "pilot fuel gas total, t/h (vendor to confirm)")
PURGE = aval("PURGE", 0.05, 0.02, 0.2, "continuous flare purge gas, t/h (vendor to confirm)")
# ---- drains ----
CD_FLOW = aval("CD_FLOW", 10.0, 2.0, 50.0, "closed-drain average drain-down flow, t/h (needs largest vessel inventory and drain time: gap)")
OWS_FLOW = aval("OWS_FLOW", 100.0, 20.0, 500.0, "oily/contaminated runoff to open-drain sewer, t/h (rainfall and area data: gap)")
OIL_F = aval("OIL_F", 0.01, 0.002, 0.05, "oil fraction of OWS inflow")
# ---- urea store ----
BULK = aval("BULK", 0.75, 0.70, 0.80, "urea granule bulk density, t/m3")
DAYS = aval("DAYS", 7.0, 3.0, 14.0, "urea bulk store capacity, days of production")
PILE_H = aval("PILE_H", 12.0, 8.0, 15.0, "pile height, m")
CV_F = aval("CV_F", 1.25, 1.10, 1.50, "conveyor design capacity factor on production rate")
BAG_F = aval("BAG_F", 0.90, 0.50, 1.00, "bagged fraction of urea dispatch")
BAG_KG = aval("BAG_KG", 50.0, 45.0, 50.0, "bag mass, kg")
BAG_RATE = aval("BAG_RATE", 1200.0, 800.0, 1800.0, "bags/h per bagging line (vendor to confirm)")
ROAD_F = aval("ROAD_F", 0.50, 0.0, 1.0, "road share of dispatch (rest by rail)")
TRUCK_T = aval("TRUCK_T", 25.0, 20.0, 30.0, "truck payload, t")
WAGON_T = aval("WAGON_T", 60.0, 50.0, 65.0, "rail wagon payload, t")

CAP_T = U * 24 * DAYS; CAP_M3 = CAP_T / BULK; FOOT_M2 = CAP_M3 / PILE_H
BAGS_H = BAG_F * U * 1000 / BAG_KG; BAG_LINES = math.ceil(BAGS_H / BAG_RATE)
TRUCKS_D = ROAD_F * U * 24 / TRUCK_T; WAGONS_D = (1 - ROAD_F) * U * 24 / WAGON_T
CV_CAP = CV_F * U
HAZ_SHEETS = {905}                                                  # units with toxic/flammable gas inventory needing an ESD valve (flare path exempt, see notes)
VD = {k: g.MW[k] / 28.96 for k in ("NH3", "H2", "CO", "H2S", "CO2", "N2", "O2")}   # D vapour density relative to air (M / 28.96)

# ---- panel text-fit check ----
import pid_unit as _pu, pid_unit2 as _pu2
WARN = []
_orig_dp = _pu.data_panel


def _chk_dp(s, pkg, sh, tag, name, rows, notes):
    for r in rows:
        if len(str(r[0])) > 25 or len(str(r[1])) > 38 or len(str(r[2])) > 14: WARN.append((sh.no, r))
    if len(notes) > 8 or sum(len(n) for n in notes) > 1900: WARN.append((sh.no, "notes too long"))
    return _orig_dp(s, pkg, sh, tag, name, rows, notes)


_pu.data_panel = _chk_dp; _pu2.data_panel = _chk_dp


def S_(i, name, phase, flow, T, P, mw=None, rho=None):
    assert len(str(i)) <= 3, i
    return simple(str(i), name, phase, flow, T, P, mw=mw, rho=rho)


def water(i, name, flow, T, P, rho=990.0): return S_(i, name, "liq", flow, T, P, rho=rho)


def fixrelief(pkg, no, dest, set_bar=None):
    hit = [r for r in pkg.relief if r[0] == f"PSV-{no}01"]; assert hit, no
    for r in hit:
        r[5] = dest
        if set_bar is not None: r[3] = fm(set_bar)


# ---- local drawing helpers (same as area 80, copied so that each area file stands alone) ----
def node(s, x, y, w, h, lines, fill="#eef3fb", stroke=INK, size=9.5):
    R(s, x, y, w, h, fill, stroke, 1.6, rx=4)
    maxc = max(int((w - 10) / (size * 0.52)), 6); out = []
    for l in lines: out += textwrap.wrap(l, maxc) or [""]
    lh = size + 2.5; assert len(out) * lh <= h - 2, f"node text overflow: {lines}"
    y0 = y + h / 2 - len(out) * lh / 2 + size
    for i, l in enumerate(out): lab(s, x + w / 2, y0 + i * lh, l, size, 700 if i == 0 else 400, "middle")
    return (x, y, w, h)


def link(s, a, b, label="", color=INK, dash=None, dy=0):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    if bx >= ax + aw - 1:
        sx, sy, ex, ey = ax + aw, ay + ah / 2 + dy, bx, by + bh / 2 + dy; mx = (sx + ex) / 2
        pts = [(sx, sy), (mx, sy), (mx, ey), (ex, ey)]; lx, ly = mx + 3, min(sy, ey) - 4
    elif by >= ay + ah - 1:
        sx, sy, ex, ey = ax + aw / 2 + dy, ay + ah, bx + bw / 2 + dy, by; my = (sy + ey) / 2
        pts = [(sx, sy), (sx, my), (ex, my), (ex, ey)]; lx, ly = min(sx, ex) + 3, my - 3
    elif by + bh <= ay + 1:
        sx, sy, ex, ey = ax + aw / 2 + dy, ay, bx + bw / 2 + dy, by + bh; my = (sy + ey) / 2
        pts = [(sx, sy), (sx, my), (ex, my), (ex, ey)]; lx, ly = min(sx, ex) + 3, my - 3
    else:
        sx, sy, ex, ey = ax, ay + ah / 2 + dy, bx + bw, by + bh / 2 + dy; mx = (sx + ex) / 2
        pts = [(sx, sy), (mx, sy), (mx, ey), (ex, ey)]; lx, ly = mx + 3, min(sy, ey) - 4
    pipe(s, pts, 1.8, color, True, dash)
    if label: lab(s, lx, ly, label, 8.3, 400, "start", GREY if color == INK else color)


def wtable(s, x, y, colw, rows, size=9.0, ymax=775, head=True, center_from=None):
    lh = size + 2.6
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), max(int((colw[j] - 8) / (size * 0.52)), 3)) or [""] for j, c in enumerate(r)]
        rh = max(len(c) for c in cells) * lh + 5
        if i % 2 == 0 and not (head and i == 0): R(s, x, y, sum(colw), rh, "#f6f7fa", "none")
        if head and i == 0: R(s, x, y, sum(colw), rh, "#e8eaf0", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, ln in enumerate(c):
                if center_from is not None and j >= center_from: lab(s, cx + colw[j] / 2, y + (k + 1) * lh, ln, size, 700 if (head and i == 0) or ln in ("X",) else 400, "middle")
                else: lab(s, cx + 4, y + (k + 1) * lh, ln, size, 700 if (head and i == 0) else 400)
            cx += colw[j]
        y += rh
    assert y <= ymax, f"table overflow y={y}"
    return y


def local_sheet(pkg, no, title, tag, name): return head(pkg, AREA, no, title, tag, name)


def patch_valve(pkg, tag_prefix, sheet_no, svc, fail="locked open"):
    for v in pkg.valves:
        if v[0].startswith(tag_prefix) and v[-1] == sheet_no: v[2] = svc; v[5] = fail


def lvessel(pkg, no, title, tag, name, inl, gas, liq, D, Ht, pumps=None, pump_dp=3.0, notes=(), rows=(), hazard="", mat="A: CS"):
    """local vertical vessel for the flare path: NO ESD closure valve in the relief path (locked-open block valves only), level control, optional pump pair"""
    sh, lp = local_sheet(pkg, no, title, tag, name); s = sh
    P, T = inl.P, inl.T; dP, dT = design_conditions(P, T)
    cx, top, w, h = 500, 215, 130, 270
    v = vvessel(s, cx, top, w, h)
    lab(s, cx - w / 2 - 12, top + h / 2, tag, 12, 700, "end"); lab(s, cx - w / 2 - 12, top + h / 2 + 14, name, 9.5, 400, "end")
    lab(s, cx - w / 2 - 12, top + h / 2 + 27, f"{D:.1f} m ID x {Ht:.1f} m T/T (D, A)", 9, 400, "end", GREY)
    run(s, pkg, sh, lp, AREA, inl, [(50, top + 80), (cx - w / 2, top + 80)], "upstream", tag, "A1", "PG", 1, vtag="LO", label=(56, top + 54))
    patch_valve(pkg, "LO-", no, "relief path block, car-sealed open (never closed in service)", "LO")
    run(s, pkg, sh, lp, AREA, gas, [(cx + 10, v["top"][1]), (cx + 10, 140), (1000, 140)], tag, "downstream", "A1", "PG", 2, vtag="LO", label=(cx + 40, 114))
    patch_valve(pkg, "LO-", no, "relief path block, car-sealed open (never closed in service)", "LO")
    ybot = v["bottom"][1]
    if pumps:
        run(s, pkg, sh, lp, AREA, liq, [(cx, ybot), (cx, 560)], tag, pumps, "A1", "PL", 3, label=(cx + 12, ybot + 14))
        PL(s, [(cx, 560), (cx, 640), (cx + 60 - 60, 640)], 2.6)
        pump_pair(s, pkg, sh, lp, AREA, liq, cx + 60, 640, pumps, tag, pump_dp, 1000, "A1", 40)
        pipe(s, [(1000, 592), (1085, 592)]); lab(s, 1005, 586, "to slop tank / closed-drain system (A)", 8.5, 400, "start", GREY)
    else:
        run(s, pkg, sh, lp, AREA, liq, [(cx, ybot), (cx, 640), (900, 640)], tag, "closed-drain system", "A1", "PL", 3, label=(cx + 20, 612))
    lx = cx + w / 2 + 70
    PL(s, [(cx + w / 2, top + h - 30), (lx, top + h - 30)], 1.0, BLUE, "4 3"); PL(s, [(cx + w / 2, top + 150), (lx, top + 150)], 1.0, BLUE, "4 3")
    bub(s, pkg, sh, lx + 15, top + h - 30, "LT", f"{lp}21", tag, "liquid level", "0-100 %", "-")
    bub(s, pkg, sh, lx + 55, top + h - 30, "LIC", f"{lp}21", tag, "level control", "0-100 %", f"H {RULES['alarm_H']*100:.0f} / L {RULES['alarm_L']*100:.0f} %", panel=True)
    bub(s, pkg, sh, lx + 15, top + 150, "LAHH", f"{lp}22", tag, "level high-high (alarm; operator action, relief path stays open)", "0-100 %", f"HH {RULES['alarm_HH']*100:.0f} % (A)", panel=True)
    bub(s, pkg, sh, lx + 55, top + 150, "LALL", f"{lp}23", tag, "level low-low (stops pumps / seal loss alarm)", "0-100 %", f"LL {RULES['alarm_LL']*100:.0f} % (A)", panel=True)
    bub(s, pkg, sh, lx + 15, top + 60, "PT", f"{lp}11", tag, "header pressure (back-pressure to relief devices)", f"0-{round_up(dP,5):g} bar", "H per header basis (gap)")
    PL(s, [(cx + w / 2, top + 60), (lx, top + 60)], 1.0, BLUE, "4 3")
    PL(s, [(cx - 50, ybot), (cx - 50, ybot + 26)], 2.0)
    blockv(s, pkg, sh, cx - 50, ybot + 8, 90, f"HV-{lp}08", "-", 1.5, "gate", "drain 1 (double block)"); blockv(s, pkg, sh, cx - 50, ybot + 20, 90, f"HV-{lp}09", "-", 1.5, "gate", "drain 2")
    lab(s, cx - 58, ybot + 40, "closed drain", 8.5, 400, "end", GREY)
    eq(pkg, sh, tag, name, "vertical vessel", f"{P:g} bar abs, {T:g} C", f"{dP:g} bar g / {dT:g} C (D)", f"{D:.1f} m ID x {Ht:.1f} m (D)", mat, "D")
    rows = list(rows) + [("Design", f"{dP:g} bar g / {dT:g} C", "D"), ("Hazard", hazard or "flammable/toxic gas", "-")]
    return finish(pkg, sh, AREA, tag, name, rows, list(notes) + ["No ESD closure valve is placed in the relief path: block valves are car-sealed open (A). The standard vessel template would draw a fail-closed ESD valve here, so this sheet is drawn locally."])


# ============================ build ==============================================================================
def build(pkg):
    n0 = len(pkg.sheets)
    # ---- streams ----
    hp = stream("901", "HP header gas (reference)", "gas", T=T_FL, P=P_FL, flow=FL_HP, base=4)
    lpg = stream("902", "LP header gas (S11+S13+S16)", "gas", T=T_FL, P=P_FL, flow=FL_LP, base=13)
    ko_in_flow = FL_HP + FL_LP
    mw_mix = (hp.mw * FL_HP + lpg.mw * FL_LP) / ko_in_flow
    ko_in = S_("903", "Flare header gas to KO-101", "gas", ko_in_flow, T_FL, P_FL, mw=mw_mix)
    ko_liq = water("905", "KO-101 liquid (slop)", KO_CARRY * ko_in_flow, T_FL, 2.0, RHO_L_KO)
    ko_gas = S_("904", "KO-101 gas to seal drum", "gas", ko_in_flow - ko_liq.flow, T_FL, P_FL - 0.05, mw=mw_mix)
    assert abs(ko_in.flow - ko_gas.flow - ko_liq.flow) < 1e-9
    sd_liq = water("908", "Seal drum overflow", SEAL_CARRY * ko_gas.flow, T_FL, 1.5, 990.0)
    sd_gas = S_("907", "Flare gas to FL-101 tip", "gas", ko_gas.flow - sd_liq.flow, T_FL, P_FL - 0.05 - SEAL_DP, mw=mw_mix)
    sd_in = S_("906", "KO-101 gas to V-901", "gas", ko_gas.flow, T_FL, P_FL - 0.05, mw=mw_mix)
    assert abs(sd_in.flow - sd_gas.flow - sd_liq.flow) < 1e-9
    pil = stream("909", "Pilot fuel gas (S16 type)", "gas", T=40.0, P=3.0, flow=PILOT, base=16)
    pur = stream("910", "Purge N2 (ASU S26 type)", "gas", T=40.0, P=2.0, flow=PURGE, base=26)
    # ---- 901 topology ----
    local_flare_topology(pkg, hp, lpg, ko_in)
    # ---- 902 KO-101 ----
    rho_g = ko_in.rho; vmax = K_SB * math.sqrt((RHO_L_KO - rho_g) / rho_g)
    Dko = max(round_up(math.sqrt(4 * ko_in.q / (math.pi * vmax)), 0.1), 1.0); Htko = round_up(max(3.0 * Dko, 6.0), 0.5)
    vol_hold = ko_liq.q * 60 * HOLD_KO
    lvessel(pkg, 902, "Area 90  Offsites and safety  -  KO-101 flare knock-out drum and slop pumps", "KO-101", "Flare knock-out drum", ko_in, ko_gas, ko_liq, Dko, Htko, pumps="P-901", pump_dp=4.0,
            rows=[("Reference load", f"{ko_in_flow:.1f} t/h", "A placeholder"), ("Gas density", f"{rho_g:.2f} kg/m3", "D"), ("Souders-Brown vmax", f"{vmax:.2f} m/s", "D, K 0.10 A"), ("Liquid carry-over", f"{KO_CARRY*100:.0f} % of inlet", "A 1-10 %"),
                  ("Hold-up", f"{vol_hold:.1f} m3 ({HOLD_KO:g} min)", "D, A 20-60 min")],
            notes=[f"SCREENING REFERENCE LOAD: HP header {FL_HP:.1f} t/h = {FLARE_FRAC*100:.0f} % (A, 5-25 %) of raw syngas (Rev B stream 4) plus LP header {FL_LP:.1f} t/h (Rev B S11+S13+S16 diverted on upset). This is NOT a relief load: Rev B contains none and the sum is not a simultaneity analysis (gap).",
                   "Diameter from gas disengagement D = sqrt(4 Q / (pi vmax)), vmax = K sqrt((rho_L - rho_G)/rho_G) with K a screening constant (A); the vertical drum and 3:1 L/D are drawing conventions. The horizontal/vertical choice, boot and heating are vendor items (gap).",
                   "Liquid collects hydrocarbon-free water/condensate with NH3 and H2S traces (A, not quantified); slop pumps P-901A/B (duty/spare) go to the slop tank or closed-drain drum V-902 (sheet 905). Pumps are sized only by the template rule (dP 4 bar A).",
                   "Flare KO-101 LAHH is an operator alarm: the relief path must stay open, so it does not trip anything automatically (A; the HAZOP decides)."],
            hazard="flammable, toxic gas (CO,H2,H2S,NH3)")
    # ---- 903 seal drum ----
    h_seal = SEAL_DP * 1e5 / (990.0 * 9.80665)                      # D m water
    d_line = math.sqrt(4 * sd_in.q / (math.pi * RULES["v_gas"]))
    Dsd = max(round_up(2.0 * d_line, 0.1), 1.0); Htsd = round_up(max(h_seal + 3.0 * Dsd, 4.0), 0.5)
    lvessel(pkg, 903, "Area 90  Offsites and safety  -  V-901 flare water seal drum", "V-901", "Flare seal drum", sd_in, sd_gas, sd_liq, Dsd, Htsd, pumps=None,
            rows=[("Seal pressure", f"{SEAL_DP:g} bar", "A 0.10-0.30"), ("Water seal leg", f"{h_seal:.2f} m", "D dP/(rho g)"), ("Diameter rule", "2 x inlet line dia.", "A"), ("Inlet line dia.", f"{d_line*1000:.0f} mm at 20 m/s", "D, A"),
                  ("Overflow", f"{sd_liq.flow*1000:.0f} kg/h", "A 0.1-2 %")],
            notes=["The seal stops flashback from the flare into the header and holds the header at about the seal pressure; the seal leg h = dP / (rho g) with dP an assumption (A). Drum diameter is two inlet-line diameters (A) pending vendor sizing for gas break-out.",
                   "Seal water make-up (from the DM or fire-water system) and its low-level alarm are drawn as the LALL instrument only; the make-up line is not drawn (template-free sheet, gap).",
                   "Overflow goes to the closed-drain system (sheet 905). Freeze protection is not needed at this site (A: tropical climate; not verified).",
                   "Air ingress through the flare tip when the header cools (vacuum) is handled by the purge gas (sheet 904) and by the seal; vacuum rating of V-901 is a gap."],
            hazard="flammable toxic gas; NH3/H2S in water")
    # ---- 904 flare package ----
    c_sound = math.sqrt(GAMMA * R_GAS * (sd_gas.T + 273.15) / (mw_mix / 1000)); v_tip = MACH_TIP * c_sound
    d_tip = math.sqrt(4 * sd_gas.q / (math.pi * v_tip))
    sheet_package(pkg, AREA, 904, "Area 90  Offsites and safety  -  FL-101 elevated flare with pilots, ignition and purge",
                  dict(tag="FL-101", name="Elevated flare (A: stack + tip)", spec="A1",
                       inlets=[(sd_gas, "flare gas", "PG"), (pil, "pilot fuel", "PG"), (pur, "purge N2", "PG")], outlets=[],
                       utilities=[],
                       desc=[f"tip {d_tip*1000:.0f} mm (D: Q / {MACH_TIP:g} Mach)", "3 pilots (A), flame-front ignition (A)", "stack height and radiation: gap (no standard read)"],
                       interlocks=[("XA", "pilot flame out (thermocouple or flame scanner)", "per vendor", "per vendor (gap)"),
                                   ("PAH", "flare header pressure high (alarm, relief path open)", f"0-{round_up(P_FL*3,5):g} bar", f"H {P_FL*1.5:.1f} bar abs (A)"),
                                   ("FAH", "flare gas flow high (metering)", "per vendor", "per vendor (gap)"),
                                   ("AAH", "O2 in flare header high (air ingress)", "0-25 %", "H per header basis (gap)")],
                       type="elevated flare", op=f"{sd_gas.flow:.1f} t/h reference, {sd_gas.P:g} bar abs", basis="A",
                       rows=[("Reference flow", f"{sd_gas.flow:.1f} t/h", "A placeholder"), ("Sonic velocity", f"{c_sound:.0f} m/s", "D, gamma 1.3 A"), ("Tip velocity", f"{v_tip:.0f} m/s", "D, 0.2 Mach A"),
                             ("Tip diameter", f"{d_tip*1000:.0f} mm", "D"), ("Pilot gas", f"{PILOT*1000:.0f} kg/h", "A"), ("Purge gas", f"{PURGE*1000:.0f} kg/h", "A"), ("Stack height", "not sized", "gap")],
                       notes=["No ESD closure valve is placed on the flare gas inlet: closing it would block every relief device. Pilot flame-out raises an alarm and an operator response; the flare must stay available (A).",
                              "Tip diameter from the stated exit-velocity fraction of sonic velocity (A) on the screening reference flow (A, not a relief load). Stack height, radiation at grade and noise need the maximum relief load and a named standard: not read (gap).",
                              "Pilot fuel is Rev B stream 16 type fuel gas (net loop purge) with an assumed total flow; continuous purge is N2 from ASU stream 26 (sheet 817 header). Ignition system type is vendor.",
                              "Smokeless operation (steam/air assist) is not drawn: gas composition is CO/H2-rich with little soot, assist need is a vendor decision."],
                       hazard="toxic flue gas (SO2 if H2S flared)"))
    patch_valve(pkg, "HV-90401", 904, "relief path block, car-sealed open (never closed in service)", "LO")
    # ---- 905 closed drain drum ----
    cd_in = water("913", "Closed-drain header liquid", CD_FLOW, 40.0, 1.5, 900.0)
    cd_gas = stream("914", "Drain drum vent to LP flare", "gas", T=40.0, P=1.3, flow=0.01 * CD_FLOW, base=13)
    cd_liq = water("915", "Drain drum liquid to pumps", CD_FLOW - cd_gas.flow, 40.0, 1.5, 900.0)
    sheet_vessel(pkg, AREA, 905, "Area 90  Offsites and safety  -  V-902 closed-drain drum and transfer pumps",
                 dict(tag="V-902", name="Closed-drain drum", inlet=cd_in, gas=cd_gas, liq=cd_liq, res_min=20.0, pumps="P-902", pump_dp_bar=4.0, spec="A1", svc_in="PL", svc_gas="PG", svc_liq="PL",
                      mat="A: CS (licensor to set)", hazard="NH3, sour condensate, HC traces", relief_case="blocked outlet; flashing drain", relief_dest="LP flare header (A)",
                      notes=[f"Drain flow {CD_FLOW:g} t/h is a placeholder (A, 2-50): the real basis is the drain-down time of the largest vessel and the number of simultaneous drains (gap). Vent {0.01*CD_FLOW:.2f} t/h (1 %, A) to the LP flare header.",
                             "Drains are the double-block drain valves (HV-xx08/09) shown on every unit sheet; this drum is the collection point. Hazardous gases (NH3, H2S) are kept off atmosphere by the vent to the LP header.",
                             "Liquid is pumped to the slop tank or back to the process (decided per fluid at HAZOP). Drain header segregation (NH3, sour, hydrocarbon) is not drawn (gap).",
                             "ESD inlet valve XV-90502 is kept: drain-header isolation on a drum high-high level is acceptable, unlike the flare path (sheet 902)."]))
    # ---- 906 open drain / OWS ----
    ow_in = water("916", "Contaminated runoff + oily drains", OWS_FLOW, 30.0, 1.2, 1000.0)
    ow_oil = water("917", "Recovered oil to slop", OIL_F * OWS_FLOW, 30.0, 1.5, 850.0)
    ow_out = water("918", "Treated water to ETP-801", OWS_FLOW - ow_oil.flow, 30.0, 1.5, 1000.0)
    assert abs(ow_in.flow - ow_oil.flow - ow_out.flow) < 1e-9
    sheet_package(pkg, AREA, 906, "Area 90  Offsites and safety  -  OWS-901 open drains and oily-water separation (sump, gravity separator)",
                  dict(tag="OWS-901", name="Open drain + oil separator", spec="A1",
                       inlets=[(ow_in, "runoff + drains", "PL")], outlets=[(ow_out, "to ETP-801", "PL"), (ow_oil, "oil to slop", "PL")],
                       utilities=[],
                       desc=["paved-area drains and rain run-off to sump,", "gravity oil separator, skimmer, oil sump", "first-flush storage not sized (gap)"],
                       interlocks=[("LAH", "separator oil layer high", "0-100 %", "H 70 % (A)"), ("LAHH", "sump level high-high (pump start / alarm)", "0-100 %", "HH 90 % (A)"),
                                   ("AAH", "hydrocarbon in water to ETP", "per site", "per site standard (gap)")],
                       type="open-drain sewer + oil separator", op="atmospheric", basis="A",
                       rows=[("Inflow (placeholder)", f"{OWS_FLOW:g} t/h", "A 20-500"), ("Oil fraction", f"{OIL_F*100:.0f} %", "A 0.2-5 %"), ("Oil recovered", f"{ow_oil.flow:.2f} t/h", "D"), ("Water out", f"{ow_out.flow:.1f} t/h", "D asserted"),
                             ("Rainfall data", "not available", "gap"), ("Closure", "in = water + oil", "D asserted")],
                       notes=["Open drains take non-hazardous liquids only; any NH3, sour or hydrocarbon liquid goes to the closed-drain system (sheet 905). Segregation of the two networks is a layout rule (A).",
                              "Rainfall intensity, catchment area, oil content and first-flush rule are not in the basis (gap), so the inflow is a labelled placeholder. Treated water joins the ETP-801 inflow (area 80, sheet 819), which does not yet count it (gap).",
                              "Fire-water run-off retention is a gap (no document fetched)."],
                       hazard="oily water; flammable vapour"))
    # ---- 907 relief header basis ----
    local_relief_basis(pkg)
    # ---- 908-911 urea storage and dispatch ----
    u1 = stream("920", "Urea granules from G-601 (S22)", "slurry", rho=BULK * 1000, base=22)
    sheet_package(pkg, AREA, 909, "Area 90  Offsites and safety  -  CV-901 urea conveyor train (G-601 to bulk store)",
                  dict(tag="CV-901", name="Belt conveyors + elevators", spec="A1",
                       inlets=[(u1, "urea", "PS")], outlets=[(S_("921", "Urea to bulk store", "slurry", U, 60.0, 1.0, rho=BULK * 1000), "to T-902", "PS")],
                       utilities=[],
                       desc=[f"design capacity {CV_CAP:.0f} t/h = {CV_F:g} x production (A)", "enclosed belts, transfer chutes, bucket elevator,", "dust extraction to bag filter (A); tail pulleys guarded"],
                       interlocks=[("SAL", "belt zero-speed / slip", "0-100 %", "L per vendor (gap)"), ("XA", "belt misalignment / pull-cord (stops that belt only)", "per vendor", "per vendor (gap)"),
                                   ("TAH", "bearing temperature high", "0-120 C", "H 90 C (A)"), ("AAH", "dust concentration high in enclosure", "per site", "per site (gap)")],
                       type="enclosed belt conveyor train", op=f"{U:.1f} t/h", basis="A",
                       rows=[("Production", f"{U:.1f} t/h", "D"), ("Design capacity", f"{CV_CAP:.0f} t/h", "A 1.10-1.50 x"), ("Bulk density", f"{BULK*1000:.0f} kg/m3", "A 700-800"), ("Belt width / speed", "vendor", "gap"),
                             ("Line NPS shown", "n/a for solids", "template")],
                       notes=["The line list shows a pipe NPS for the solids streams because the package template sizes every line as a fluid: ignore the NPS and velocity columns for 920/921 (template defect).",
                              "Urea granules at about 60 C (Rev B stream 22 T) are hygroscopic: covered conveyors and a cooling step before storage are likely (A; cooler not in Rev B, gap).",
                              "Conveyor stops are local (equipment protection), not plant ESD. Dust is a nuisance and an inhalation hazard; explosion classification of urea dust is a vendor/standard item (gap)."],
                       hazard="moving parts, dust"))
    st_out_b = S_("922", "Urea reclaimed to bagging", "slurry", BAG_F * U, 45.0, 1.0, rho=BULK * 1000)
    st_out_v = S_("923", "Urea reclaimed to bulk loading", "slurry", (1 - BAG_F) * U, 45.0, 1.0, rho=BULK * 1000)
    st_in = S_("921", "Urea to bulk store", "slurry", U, 60.0, 1.0, rho=BULK * 1000)
    assert abs(st_in.flow - st_out_b.flow - st_out_v.flow) < 1e-9
    sheet_package(pkg, AREA, 908, "Area 90  Offsites and safety  -  T-902 urea bulk store (covered, reclaim to bagging and bulk loading)",
                  dict(tag="T-902", name="Urea bulk store", spec="A1",
                       inlets=[(st_in, "urea in", "PS")], outlets=[(st_out_b, "to bagging", "PS"), (st_out_v, "to bulk loading", "PS")],
                       utilities=[], desc=[f"{DAYS:g} days = {CAP_T:,.0f} t = {CAP_M3:,.0f} m3 (D, A)", f"pile {PILE_H:g} m: footprint {FOOT_M2:,.0f} m2 (D, A)", "covered, ventilated; scraper / portal reclaim (A)"],
                       interlocks=[("LAHH", "pile height / level high-high (stops feed)", "0-100 %", "HH 95 % (A)"), ("TAH", "pile temperature high (caking, self-heating check)", "0-100 C", "H 70 C (A)"),
                                   ("MAH", "store humidity high", "0-100 %", "H per vendor (gap)"), ("AAH", "dust concentration high", "per site", "per site (gap)")],
                       type="covered bulk store", op=f"{CAP_T:,.0f} t", basis="D",
                       rows=[("Storage time", f"{DAYS:g} days", "A 3-14"), ("Capacity", f"{CAP_T:,.0f} t", "D"), ("Volume", f"{CAP_M3:,.0f} m3", "D / bulk dens."), ("Pile footprint", f"{FOOT_M2:,.0f} m2", "D, 12 m A"),
                             ("Bagged fraction", f"{BAG_F*100:.0f} %", "A 50-100"), ("Reclaim to bags", f"{st_out_b.flow:.0f} t/h", "D"), ("Reclaim to bulk", f"{st_out_v.flow:.0f} t/h", "D")],
                       notes=["Capacity = production x days (A), volume = mass / bulk density (A 0.70-0.80 t/m3), footprint at the assumed pile height. No fertiliser-store code was read (gap); the days of storage are a commercial/logistics choice.",
                              "Urea is non-combustible but bags and dust feed a fire; the store gets heat/smoke detection and hydrants (sheets 912, 914) but no foam (A).",
                              "Reclaim rate equals production (D) for the steady case; peak reclaim for loading windows is a gap."],
                       hazard="dust; caking; low fire load"))
    bag_in = S_("922", "Urea reclaimed to bagging", "slurry", BAG_F * U, 45.0, 1.0, rho=BULK * 1000)
    bags_out = S_("924", "Bagged urea (50 kg bags)", "slurry", BAG_F * U, 45.0, 1.0, rho=BULK * 1000)
    sheet_package(pkg, AREA, 910, "Area 90  Offsites and safety  -  BAG-901 bagging lines (weigh, fill, close, palletise)",
                  dict(tag="BAG-901", name="Bagging lines", spec="A1",
                       inlets=[(bag_in, "urea in", "PS")], outlets=[(bags_out, "bags to loading", "PS")],
                       utilities=[], desc=[f"{BAGS_H:,.0f} bags/h at {BAG_KG:g} kg (D, A)", f"{BAG_LINES} duty lines + 1 spare at {BAG_RATE:,.0f} bags/h (A)", "check-weigher, metal detector, stitching/sealing"],
                       interlocks=[("WAL", "check-weigher reject (underweight)", "0-60 kg", "per vendor (gap)"), ("LAHH", "hopper level high-high (stops feed)", "0-100 %", "HH 90 % (A)"),
                                   ("AAH", "dust concentration high at filling", "per site", "per site (gap)")],
                       type="bagging lines", op=f"{BAGS_H:,.0f} bags/h", basis="D",
                       rows=[("Bagged flow", f"{bag_in.flow:.1f} t/h", "D"), ("Bag mass", f"{BAG_KG:g} kg", "A 45-50"), ("Bags per hour", f"{BAGS_H:,.0f}", "D"), ("Line rate", f"{BAG_RATE:,.0f} /h", "A 800-1,800"),
                             ("Lines duty + spare", f"{BAG_LINES} + 1", "D"), ("Closure", "bags = urea in", "D asserted")],
                       notes=["Bag mass and line rate are assumptions (A), not vendor data; the line count is ceil(bags/h / rate) plus one spare. The bag material (film, woven PP) and its coding are outside the process basis.",
                              "Rejects and spillage return by belt to the store (not drawn). Bag-filling dust is extracted to the same bag filter as CV-901 (A)."],
                       hazard="dust; manual handling"))
    ld_in_b = bags_out
    ld_in_v = S_("923", "Urea reclaimed to bulk loading", "slurry", (1 - BAG_F) * U, 45.0, 1.0, rho=BULK * 1000)
    ld_road = S_("925", "Dispatch by road", "slurry", ROAD_F * U, 40.0, 1.0, rho=BULK * 1000)
    ld_rail = S_("926", "Dispatch by rail", "slurry", (1 - ROAD_F) * U, 40.0, 1.0, rho=BULK * 1000)
    assert abs(ld_in_b.flow + ld_in_v.flow - ld_road.flow - ld_rail.flow) < 1e-9
    sheet_package(pkg, AREA, 911, "Area 90  Offsites and safety  -  LD-901 truck and rail loading (bagged and bulk)",
                  dict(tag="LD-901", name="Truck + rail loading", spec="A1",
                       inlets=[(ld_in_b, "bagged urea", "PS"), (ld_in_v, "bulk urea", "PS")], outlets=[(ld_road, "road", "PS"), (ld_rail, "rail", "PS")],
                       utilities=[], desc=[f"road {ROAD_F*100:.0f} % / rail {(1-ROAD_F)*100:.0f} % (A)", f"{TRUCKS_D:.0f} trucks/day at {TRUCK_T:g} t, {WAGONS_D:.0f} wagons/day at {WAGON_T:g} t (D, A)", "weighbridge, loading arms/chutes, dust hoods"],
                       interlocks=[("WAH", "weighbridge overload", "0-60 t", "H per vehicle rating (gap)"), ("LAHH", "bulk loading hopper high-high (stops feed)", "0-100 %", "HH 90 % (A)"),
                                   ("AAH", "dust concentration high at loading", "per site", "per site (gap)")],
                       type="truck and rail loading", op=f"{U:.1f} t/h dispatch", basis="D",
                       rows=[("Dispatch", f"{U:.1f} t/h", "D"), ("Road share", f"{ROAD_F*100:.0f} %", "A 0-100"), ("Trucks per day", f"{TRUCKS_D:.0f}", "D, 25 t A"), ("Wagons per day", f"{WAGONS_D:.0f}", "D, 60 t A"),
                             ("Closure", "road + rail = in", "D asserted"), ("Weighbridge", "vendor", "gap")],
                       notes=["Dispatch split, truck payload and wagon payload are assumptions (A) so that the daily vehicle count can be seen; the real logistics plan (including coastal or inland movement) is not in the basis (gap).",
                              "Mass is conserved through the offsites train: stream 22 = 921 = 922 + 923 = 925 + 926 (asserted).",
                              "Road/rail traffic safety, queueing and gate house are out of scope."],
                       hazard="vehicle movements; dust"))
    # ---- 912-916 local safety sheets ----
    local_firewater(pkg)
    local_foam_deluge(pkg)
    local_fg_logic(pkg)
    local_esd_hierarchy(pkg)
    local_cause_effect(pkg)
    assert len(pkg.sheets) - n0 == NSHEETS, len(pkg.sheets) - n0
    return pkg


def local_flare_topology(pkg, hp, lpg, ko_in):
    sh, lp = local_sheet(pkg, 901, "Area 90  Offsites and safety  -  flare system topology: HP / LP headers, KO-101, seal drum, FL-101", "FLR-901", "Flare system topology"); s = sh
    lab(s, 30, 108, "Block diagram of the collection and disposal path. Sizes and loads are on sheets 902-904; relief header sizing basis on sheet 907.", 9, 400, "start", GREY)
    hpsrc = node(s, 30, 150, 230, 150, ["HP header sources (flammable / toxic)", "PSVs and blowdown valves of area 10 gasification (BDV-101, PSV-101/102),", "shift 20/40, AGR, NH3 loop 40/50, K-401/K-601 relief discharges, V-203 (A)"], "#fff4e0")
    lpsrc = node(s, 30, 360, 230, 150, ["LP header sources", "acid gas (S11) when sulphur unit is down, purification residual (S13),", "loop purge (S16), closed-drain vent (V-902), NH3 storage vents, tank vents (A)"], "#fff4e0")
    ko = node(s, 360, 250, 170, 100, ["KO-101", "knock-out drum", f"{ko_in.flow:.1f} t/h reference (A)"], "#eef3fb")
    sd = node(s, 600, 250, 160, 100, ["V-901", "water seal drum", f"{SEAL_DP:g} bar seal (A)"], "#eef3fb")
    fl = node(s, 830, 235, 190, 130, ["FL-101", "elevated flare, 3 pilots", "purge N2, ignition", "stack height: gap"], "#ffebee")
    slop = node(s, 360, 470, 170, 70, ["Slop tank / V-902", "KO-101 liquid by P-901"], "#f6f7fa")
    cdr = node(s, 600, 470, 160, 70, ["V-902 closed drain", "seal overflow (sheet 905)"], "#f6f7fa")
    link(s, hpsrc, ko, "HP header", dy=-20); link(s, lpsrc, ko, "LP header", dy=-20)
    link(s, ko, sd, "gas"); link(s, sd, fl, "gas"); link(s, ko, slop, "liquid"); link(s, sd, cdr, "overflow")
    lab(s, 30, 590, "Design rules (A): headers slope to KO-101, no pockets; no isolating valve in a relief path except car-sealed-open block valves; pilots and ignition on essential power;", 9, 400, "start")
    lab(s, 30, 604, "HP and LP streams join before KO-101 for this concept (a separate LP KO drum is a vendor/HAZOP choice); CO2 vents (Rev B S20) and urea-train atmospheric vents do not go to the flare.", 9, 400, "start")
    lab(s, 30, 640, "Flame arrestors: not used on the main header (A, decision for the flare vendor); flare gas recovery: not considered (gap).", 9, 400, "start", GREY)
    for k, (fn, loop, svc, rng, al) in enumerate([("PT", "11", "flare header pressure at KO-101", "0-6 bar", "-"), ("PAH", "12", "flare header pressure high", "0-6 bar", f"H {P_FL*1.5:.1f} bar abs (A)"),
                                                   ("XA", "13", "pilot flame-out (all pilots)", "per vendor", "per vendor (gap)"), ("LAHH", "14", "KO-101 level high-high", "0-100 %", "HH 90 % (A)")]):
        bub(s, pkg, sh, 400 + k * 60, 700, fn, f"901{loop}", "FLR-901", svc, rng, al, panel=True)
    eq(pkg, sh, "FLR-901", "Flare system topology", "block diagram", f"{ko_in.flow:.1f} t/h reference", "A", "-", "-", "A")
    rows = [("Reference HP load", f"{FL_HP:.1f} t/h", "A 5-25 % of S4"), ("Reference LP load", f"{FL_LP:.1f} t/h", "D S11+S13+S16"), ("Header pressure", f"{P_FL:g} bar abs", "A"), ("Header temperature", f"{T_FL:g} C", "A"),
            ("Relief loads", "none in Rev B", "gap"), ("Stack / radiation", "not sized", "gap"), ("Flame arrestor", "not used", "A")]
    return finish(pkg, sh, AREA, "FLR-901", "Flare system topology", rows,
                  ["The Rev B P&ID and relief schedule give PSV set pressures and destinations but no loads: every flare size on sheets 902-904 scales with the screening reference load (A) and must be redone when the licensors give relief and blowdown rates.",
                   "HP vs LP header split follows source pressure class only (A). Back-pressure limits of each relief device (conventional vs balanced) are a gap and drive the header diameters.",
                   "Toxic releases (H2S, NH3) to a flare burn to SO2 and NOx; the acceptable flare use for H2S and the sulphur-unit tail-gas route are not in Rev B (gap).",
                   "Hierarchy: ESD-0/ESD-1 open BDV-101 to this system; the system itself is never shut by ESD (sheet 915)."])


def local_relief_basis(pkg):
    sh, lp = local_sheet(pkg, 907, "Area 90  Offsites and safety  -  relief header sizing basis (NOT sized: load cases and data needed)", "RHB-901", "Relief header basis"); s = sh
    nfl = sum(1 for r in pkg.relief if "flare" in str(r[5]).lower()); nall = len(pkg.relief)
    rows = [("Relief case class", "Typical Rev B units", "Data needed to size (not available)", "Status"),
            ("Fire (external pool/jet)", "R-101, V-102, R-201/202, R-301, R-401, V-203, V-302, V-401, T-501, K-401/601 KO drums", "wetted area and vessel inventories, insulation, fire-case rule of the licensor and a named standard", "gap"),
            ("Blocked outlet", "every vessel/column with a PSV on the Rev B relief schedule", "maximum pump / compressor head and flow with the outlet closed", "gap"),
            ("Tube rupture", "E-101, E-102, E-103, E-401, E-601 (HP gas/steam vs CW or steam side)", "tube count and diameter, HP side pressure and fluid properties", "gap"),
            ("Control-valve failure open", "PV-xx11 on gas outlets, letdown stations PRDS-801/802, HP/MP/LP steam headers", "valve Cv, upstream/downstream pressure, fluid properties", "gap"),
            ("Loss of cooling / reflux / power", "C-302, C-601, K-401/601, ASU, area 80 CW and steam", "heat duty lost and vapour generation rate", "gap"),
            ("Gasifier emergency blowdown", "BDV-101 from R-101 / V-102 (ESD-1)", "inventory and blowdown time; largest HP release; likely the sizing case", "gap"),
            ("NH3 loop / refrigeration release", "R-401, V-401, E-401, T-501 refrigeration upset (BOG)", "loop inventory, refrigeration duty and tank heat in-leak", "gap"),
            ("Thermal expansion of blocked liquid", "cooled NH3 and water lines", "line volume, heat input rate", "gap"),
            ("Simultaneity (header cases)", "which of the above can occur together after a power / CW / IA / steam failure", "a plant-wide study (the cause-and-effect on sheet 916 is the starting point)", "gap")]
    y = wtable(s, 30, 100, [230, 330, 400, 90], rows, 9.2, 560)
    bx = 30
    lab(s, bx, y + 24, f"Relief devices registered in this package at build time of this sheet: {nall}, of which with a flare destination: {nfl} (count depends on build order of the areas).", 9.4, 700)
    lab(s, bx, y + 40, "Method of record (A): size each header for the single worst credible case plus a check of the plausible simultaneous cases; back-pressure limits set by the relief-device type.", 9, 400, "start", GREY)
    lab(s, bx, y + 54, "No relief-sizing standard text was read for this package (paywalled / not fetched): every sizing equation, factor and back-pressure limit is an input still to be supplied.", 9, 400, "start", GREY)
    eq(pkg, sh, "RHB-901", "Relief header sizing basis", "table", "no loads", "-", "not sized", "-", "A")
    return finish(pkg, sh, AREA, "RHB-901", "Relief header basis", [("Loads", "none available", "gap"), ("Placeholder", f"{FL_HP+FL_LP:.0f} t/h", "A, not a load"), ("Header P / T", f"{P_FL:g} bar abs / {T_FL:g} C", "A"), ("Devices registered", f"{nall} ({nfl} to flare)", "D")],
                  ["This sheet states what would have to be known; it sizes nothing. The only numbers are the screening placeholder of sheet 902 and the device count from the registers.",
                   "Rev B names the relief devices and destinations in its relief schedule; loads need fire-case areas, vessel sizes (from unit sheets of areas 10-70) and licensor data (gap).",
                   "Existing templates register every PSV with sizing status 'not sized' for the same reason; when loads are known this table and the register are updated together."])


def local_firewater(pkg):
    sh, lp = local_sheet(pkg, 912, "Area 90  Offsites and safety  -  fire-water system: tanks, pumps, ring main, hydrants and deluge supply", "FW-901", "Fire-water system"); s = sh
    lab(s, 30, 104, "TOPOLOGY ONLY. No fire-water code, rule or standard was fetched, so all flow rates, tank volumes, pressures, pump counts and ring-main sizes are GAPS and are not typed here.", 9.5, 700, "start", RED)
    src = node(s, 30, 150, 160, 70, ["Raw water T-801", "sheet 809 (reserve rule: gap)"], "#f6f7fa")
    tk = node(s, 250, 140, 170, 90, ["FWT-901 A/B fire-water tanks", "volume: gap", "2 tanks (A)"], "#eef3fb")
    jp = node(s, 490, 140, 160, 60, ["JP-901 jockey pump", "keeps ring pressure"], "#eef3fb")
    ep = node(s, 490, 215, 160, 60, ["FWP-901 A/B electric main", "capacity: gap"], "#eef3fb")
    dp = node(s, 490, 290, 160, 60, ["FWP-902 A/B diesel main", "independent of power (A)"], "#ffebee")
    ring = node(s, 720, 215, 150, 135, ["Fire-water ring main", "underground, sectionalised,", "looped around process, coal and urea areas (A)"], "#e8f5e9")
    hyd = node(s, 930, 140, 170, 70, ["Hydrants and monitors", "at process and storage areas"], "#e8f5e9")
    dlg = node(s, 930, 230, 170, 70, ["Deluge skids", "NH3, coal, transformers, cables"], "#e8f5e9")
    fm_ = node(s, 930, 320, 170, 70, ["Foam concentrate system", "sheet 913"], "#e8f5e9")
    link(s, src, tk, "fill"); link(s, tk, jp); link(s, tk, ep); link(s, tk, dp)
    link(s, jp, ring); link(s, ep, ring); link(s, dp, ring)
    link(s, ring, hyd); link(s, ring, dlg); link(s, ring, fm_)
    lab(s, 30, 430, "Pump start logic (A): jockey on pressure fall; first main pump on lower pressure; second main (diesel) on lower pressure again or loss of power; no automatic stop (manual).", 9, 400, "start")
    lab(s, 30, 444, "The diesel pumps and the essential board (sheet 818) are the supply that must survive plant power loss. Tank reserve is separate from process raw water (A).", 9, 400, "start")
    lab(s, 30, 470, "Test, flushing, valve supervision, deluge valve sets and the water-supply duration are standard items: not read (gap).", 9, 400, "start", GREY)
    for k, (fn, loop, svc, rng, al) in enumerate([("PALL", "61", "ring-main pressure low-low (start next pump)", "0-15 bar", "per fire-water design (gap)"), ("PAL", "62", "ring-main pressure low (start duty pump)", "0-15 bar", "per fire-water design (gap)"),
                                                   ("LAL", "63", "fire-water tank level low (refill / alarm)", "0-100 %", "L 70 % (A)"), ("LALL", "64", "fire-water tank level low-low (pump protection)", "0-100 %", "LL 20 % (A)")]):
        bub(s, pkg, sh, 120 + k * 60, 580, fn, f"912{loop}", "FW-901", svc, rng, al, panel=True)
    for tg, nm in [("FWT-901", "Fire-water tank A/B"), ("FWP-901", "Fire-water electric pumps A/B"), ("FWP-902", "Fire-water diesel pumps A/B"), ("JP-901", "Fire-water jockey pump")]:
        eq(pkg, sh, tg, nm, "fire-water equipment", "gap", "gap", "not sized", "A: vendor", "A")
    return finish(pkg, sh, AREA, "FW-901", "Fire-water system", [("Tanks", "volume: gap", "gap"), ("Main pumps", "capacity: gap", "gap"), ("Ring main", "size: gap", "gap"), ("Standards", "none fetched", "gap"), ("Standby", "diesel pumps", "A")],
                  ["Cited documents: none. The system is drawn as a topology so that tags, instruments and the essential-power link exist; every quantity is left blank on purpose.",
                   "To close the gap: fetch the applicable fire-water design guidance (e.g. the owner's site standard or an openly published code), then size the reserve from the largest credible fire scenarios on the unit sheets.",
                   "Interfaces: deluge and foam sheet 913; fire pump essential power sheet 818; fire detection and cause-and-effect sheets 914 and 916."])


def local_foam_deluge(pkg):
    sh, lp = local_sheet(pkg, 913, "Area 90  Offsites and safety  -  foam and deluge protection for ammonia and coal areas (qualitative)", "FD-901", "Foam / deluge protection"); s = sh
    lab(s, 30, 104, "QUALITATIVE: application rates, densities, durations and valve sizes were not found in any fetched document and are not typed (gap).", 9.5, 700, "start", RED)
    rows = [("Area / hazard", "Protection type (A)", "Initiation (A)", "Rates and data"),
            ("T-501 NH3 refrigerated storage, dyke, pumps P-501", "water spray / fog to knock down vapour; dyke sump; option of vapour-suppression blanket on the pool (licensor / site standard to decide)", "NH3 detection high-high + operator confirmation; remote manual", "gap"),
            ("NH3 loop (R-401, V-401, E-401) and NH3 pipes", "water spray curtain at release points; hydrants and monitors", "NH3 detection high-high (voted) + manual", "gap"),
            ("Urea reactor / stripper area (R-601, C-601, E-601)", "hydrants and monitors; no fixed deluge (A)", "manual", "gap"),
            ("Coal handling: conveyor galleries, transfer towers, bunkers", "water spray or deluge over belts; hydrants; dust suppression", "heat / smoke / linear heat detection (voted) + manual", "gap"),
            ("Coal mill F-101 and pulverised-coal system", "inerting and venting of the mill system (N2 from sheet 817); explosion venting; deluge at feeders", "CO / temperature high in mill + oxygen limit", "gap"),
            ("Coal stockpile", "temperature surveillance; water for hot spots; hydrants", "temperature high, operator", "gap"),
            ("Transformers and cable galleries (sheet 818)", "deluge on oil-filled transformers; water spray or gas system in cable galleries", "heat detection + manual", "gap"),
            ("Gasifier area (R-101, V-102)", "structural protection by water spray on supports; hydrants; no foam", "CO/H2 detection (2oo3) + flame detector BE-101", "gap"),
            ("Flare, tanks of slop and oil", "foam on slop tank (A); radiation-shielding monitors", "flame detector + manual", "gap")]
    y = wtable(s, 30, 130, [260, 440, 280, 80], rows, 9.0, 740)
    lab(s, 30, y + 22, "Deluge valve sets and foam proportioners hang off the ring main of sheet 912; their supervision and test connections are standard items (gap).", 9, 400, "start", GREY)
    eq(pkg, sh, "FD-901", "Foam and deluge protection", "table", "qualitative", "-", "gap", "-", "A")
    return finish(pkg, sh, AREA, "FD-901", "Foam / deluge protection", [("Ammonia areas", "spray/fog, dyke", "A"), ("Coal areas", "spray/deluge, inerting", "A"), ("Rates / durations", "not available", "gap"), ("Ring main", "sheet 912", "-")],
                  ["Ammonia vapour is absorbed by water and ammonia is flammable only in a narrow range; the primary protection is detection, isolation (ESD-2) and water spray to limit the cloud, which is why the table leads with detection and isolation (A).",
                   "Coal dust and pulverised coal are explosion hazards in mills, bunkers and galleries: venting, inerting and housekeeping matter more than water; coal handling is on area 10 sheets of this package.",
                   "Foam is limited to slop and oil tanks (A). Foam concentrate type and proportioning are vendor items (gap)."])


def local_fg_logic(pkg):
    sh, lp = local_sheet(pkg, 914, "Area 90  Offsites and safety  -  fire and gas detection layout logic", "FGD-901", "Fire and gas detection logic"); s = sh
    vd = VD
    rows = [("Zone", "Hazard gas / fire", "Detector type (A)", "Placement logic (vapour density vs air, D from molar mass)", "Voting / action (A)"),
            ("Gasification island R-101, V-102, E-101", f"CO ({vd['CO']:.2f}), H2 ({vd['H2']:.2f}), H2S ({vd['H2S']:.2f}), flame", "CO/H2 point, H2S point, UV/IR flame (BE-101)", "H2 at high level (lighter than air); H2S and CO at breathing zone to low level; flame by line of sight", "2oo3 gas -> ESD-1; flame -> ESD-1"),
            ("Shift and AGR 20/30", f"CO, H2S ({vd['H2S']:.2f}), CO2 ({vd['CO2']:.2f})", "CO, H2S, CO2 point", "H2S and CO2 low (heavier); CO breathing zone", "2oo3 alarm; high-high -> area ESD (A)"),
            ("Ammonia synthesis 40 / R-401 loop", f"H2 ({vd['H2']:.2f}), NH3 ({vd['NH3']:.2f})", "H2 point, NH3 point (toxic, flammable)", "H2 high; NH3 high-level near release points, low level at refrigerated sections (cold vapour dense)", "2oo3 -> ESD-2"),
            ("NH3 storage T-501, dyke, loading", f"NH3 ({vd['NH3']:.2f}), cold liquid pool", "NH3 point, open-path IR, flame", "perimeter and dyke sump; NH3 detectors high and low", "2oo3 high-high -> ESD-2 + spray"),
            ("Urea synthesis 60", f"NH3, CO2 ({vd['CO2']:.2f})", "NH3 point, CO2/O2 low-level", "NH3 high; CO2 and O2-deficiency low in pits and sumps", "2oo3 -> ESD-4"),
            ("ASU-101 and N2 users", f"O2 enrichment ({vd['O2']:.2f}), N2 asphyxiation ({vd['N2']:.2f})", "O2 point (both high and low alarms)", "low level in pits and rooms; no ignition sources if enriched", "alarm; O2 high or low -> evacuation (A)"),
            ("Coal handling and mill F-101", "CO, coal dust, hot spot, fire", "CO point, heat / smoke, linear heat cable", "inside galleries and bunkers; linear cable along belts", "2oo3 -> coal feed stop + deluge"),
            ("Flare FL-101 and KO-101", "flame-out, hydrocarbon/H2 at KO", "flame scanner, gas point", "at pilots and KO drum", "alarm"),
            ("Utilities and buildings (CT, boiler, switchgear)", "fire, CO", "smoke/heat in rooms, flame near B-801", "rooms by detector spacing rule (not read: gap)", "alarm + fire pump start")]
    y = wtable(s, 30, 100, [190, 190, 190, 330, 190], rows, 8.8, 720)
    lab(s, 30, y + 20, "Vapour density ratio = molar mass / 28.96 (D, molar masses from gen_pid_urea.MW). Cold or pressurised releases change the behaviour: a ratio below 1 is a first placement rule only (A).", 9, 400, "start", GREY)
    lab(s, 30, y + 34, "Alarm and trip THRESHOLDS (ppm, % LEL, %O2) are site-standard inputs and are not entered (gap). 2oo3 voting is the design choice used in the Rev B cause-and-effect (A).", 9, 400, "start", GREY)
    eq(pkg, sh, "FGD-901", "Fire and gas detection logic", "table", "qualitative", "-", "-", "-", "A")
    return finish(pkg, sh, AREA, "FGD-901", "Fire and gas detection logic", [("NH3 vs air", f"{vd['NH3']:.2f}", "D M/28.96"), ("H2 vs air", f"{vd['H2']:.2f}", "D"), ("CO vs air", f"{vd['CO']:.2f}", "D"), ("H2S vs air", f"{vd['H2S']:.2f}", "D"), ("CO2 vs air", f"{vd['CO2']:.2f}", "D"), ("Thresholds", "not entered", "gap")],
                  ["Layout logic only: where a detector sits follows the lighter/heavier-than-air rule, the release points on the unit sheets and line of sight for flame detectors; detector counts and spacing need the site layout (not available).",
                   "Gas detection also covers asphyxiants (N2, CO2) and oxygen enrichment near ASU-101 (sheet 817).",
                   "Detector loop tags use the same tag scheme as the unit sheets: AT-101/102/201 and BE-101 exist on Rev B; others are new in this area (A)."])


def local_esd_hierarchy(pkg):
    sh, lp = local_sheet(pkg, 915, "Area 90  Offsites and safety  -  emergency shutdown (ESD) hierarchy", "ESD-901", "ESD hierarchy"); s = sh
    top = node(s, 400, 110, 300, 62, ["ESD-0  plant shutdown", "manual HS-001; fire/gas general alarm; loss of essential power (A)"], "#ffebee")
    lv = [("ESD-1", "syngas / gasifier", "closes XV-101, 102, 103; opens BDV-101"), ("ESD-2", "NH3 storage and loop", "closes XV-501, 502; trips P-501"), ("ESD-3", "O2 / steam", "closes XV-101, 103; stops coal XV-102"),
          ("ESD-4", "urea synthesis", "closes XV-602, 603; trips K-601"), ("ESD-5", "utilities (NEW, A)", "loss of power, CW, IA, BFW: sequenced trips")]
    boxes = []
    for i, (a, b, c) in enumerate(lv):
        boxes.append(node(s, 40 + i * 215, 250, 200, 110, [f"{a}  {b}", c], "#fff4e0" if i < 4 else "#fff9c4"))
    psd = node(s, 40, 430, 1000, 60, ["PSD  process shutdown (unit level)", "unit trips on the unit sheets (compressor trips, level and temperature trips): isolates one unit without plant action (A)"], "#eef3fb")
    fe = node(s, 40, 540, 1000, 60, ["Final elements", "ESD valves XV-xxx (fail position on each unit sheet), BDV-101 blowdown, motor/steam trips, essential-power start, fire-pump start; flare path stays open"], "#e8f5e9")
    PL(s, [(550, 172), (550, 212)], 1.8); PL(s, [(140, 212), (1000, 212)], 1.8)
    for b in boxes: pipe(s, [(b[0] + b[2] / 2, 212), (b[0] + b[2] / 2, 250)], 1.8)
    PL(s, [(140, 395), (1000, 395)], 1.8)
    for b in boxes: PL(s, [(b[0] + b[2] / 2, 360), (b[0] + b[2] / 2, 395)], 1.8)
    pipe(s, [(540, 395), (540, 430)], 1.8)
    link(s, psd, fe)
    lab(s, 40, 640, "Hierarchy rules (A): ESD-0 initiates all lower levels; ESD-1 includes ESD-3 actions (O2, steam and coal stop) and opens BDV-101; ESD-2 and ESD-4 are independent but ESD-2 trips P-501, which stops NH3 feed to ESD-4;", 9, 400, "start")
    lab(s, 40, 654, "a lower level never initiates a higher one without voting; ESD-5 trips utilities in a fixed order so that the flare, fire water, essential power and instrument air stay available. Reset is local after investigation.", 9, 400, "start")
    lab(s, 40, 680, "ESD-1 to ESD-4 and HS-001 come from the Rev B P&ID (sheets 3 and 4, cause-and-effect); ESD-0 as a total level and ESD-5 are new in this package and need the licensors' agreement (A). Safety integrity levels are not assigned here.", 9, 400, "start", GREY)
    for k, (fn, loop, svc, rng, al) in enumerate([("HS", "01", "manual ESD-0 push-button (control room and field)", "-", "trip"), ("PAHH", "02", "R-101 pressure high-high (ESD-1)", "per Rev B", "HH 1.1 x P (A)"), ("AAHH", "03", "CO/H2 gas high-high 2oo3 (ESD-1)", "per site", "per site (gap)"), ("PALL", "04", "HP steam header low-low (ESD-3)", "0-80 bar", "LL 40 bar (A)")]):
        bub(s, pkg, sh, 700 + k * 60, 700, fn, f"915{loop}", "ESD-901", svc, rng, al, panel=True)
    eq(pkg, sh, "ESD-901", "ESD hierarchy", "block diagram", "qualitative", "-", "-", "-", "A")
    return finish(pkg, sh, AREA, "ESD-901", "ESD hierarchy", [("Levels", "ESD-0 to ESD-5, PSD", "A"), ("From Rev B", "ESD-1..4, HS-001", "S"), ("New", "ESD-0 total, ESD-5", "A"), ("SIL", "not assigned", "gap"), ("Flare path", "never isolated", "A")],
                  ["Levels 1 to 4 and the manual push-button come from the Rev B drawing (sheets 1, 3, 4 and its cause-and-effect); no safety-integrity classification was done (gap).",
                   "Utility trips (ESD-5) are sequenced so that safety systems keep their supplies; the sequence is qualitative and the HAZOP/LOPA must confirm it.",
                   "Out of scope: laboratory and utility buildings, ESD for coal-handling area 10 and ASU area 10 are included only through ESD-1/ESD-3."])


def local_cause_effect(pkg):
    sh, lp = local_sheet(pkg, 916, "Area 90  Offsites and safety  -  plant cause-and-effect summary (qualitative)", "CE-901", "Cause-and-effect summary"); s = sh
    cols = ["ESD-0", "ESD-1", "ESD-2", "ESD-3", "ESD-4", "ESD-5", "K-601", "BDV", "Fire", "Stby"]
    rows = [("Cause (initiating event)",) + tuple(cols)]
    data = [("HS-001 manual push-button, control room or field", "X", "X", "X", "X", "X", "X", "X", "", "S"),
            ("CO/H2 gas high-high, 2oo3, gasifier area; or flame BE-101", "", "X", "", "X", "", "", "X", "A", ""),
            ("R-101 pressure high-high; loss of O2:coal ratio", "", "X", "", "X", "", "", "X", "", ""),
            ("HP steam header low-low pressure (SH-801)", "", "A", "", "X", "", "", "", "", "S"),
            ("NH3 detection high-high, T-501 / V-401 area", "", "", "X", "", "", "", "", "M", ""),
            ("NH3 detection high-high, urea area (R-601)", "", "", "X", "", "X", "X", "", "M", ""),
            ("R-601 pressure high-high; K-601 trip or low CO2", "", "", "X", "", "X", "X", "", "", ""),
            ("R-401 loop pressure/temperature high-high", "", "A", "X", "", "", "", "X", "", ""),
            ("Loss of cooling water (P-803 PALL)", "", "A", "", "", "", "X", "", "", "S"),
            ("Loss of instrument air (K-801 PALL)", "M", "A", "A", "A", "A", "", "", "", "S"),
            ("Loss of power (bus loss)", "X", "", "", "", "", "X", "", "S", "S"),
            ("Loss of BFW / D-801 level low-low", "", "A", "", "", "", "", "", "", "S"),
            ("Fire detected, coal handling or mill F-101", "", "M", "", "", "", "", "", "X", ""),
            ("Fire detected, process area (any)", "M", "M", "M", "", "M", "", "", "X", "S"),
            ("Flare KO-101 level high-high; pilots out", "A", "A", "A", "", "", "", "", "", "")]
    esd5 = {"HS-001": "X", "cooling water": "X", "instrument air": "X", "Loss of power": "X", "BFW": "X"}
    for r in data:
        v5 = next((x for k, x in esd5.items() if k in r[0]), "")
        rows.append(r[:5] + (v5,) + r[5:])
    y = wtable(s, 30, 100, [350] + [72] * 10, rows, 9.2, 700, center_from=1)
    lab(s, 30, y + 20, "X automatic action   M operator-confirmed action   S standby start (aux boiler, DG sets, standby pumps, fire pumps)   A alarm only   blank = no action.", 9.5, 700, "start")
    lab(s, 30, y + 36, "Columns: ESD-0 plant; ESD-1 syngas; ESD-2 NH3; ESD-3 O2/steam; ESD-4 urea; ESD-5 utilities; K-601 CO2 compressor trip; BDV emergency blowdown to flare (flare path never closed); Fire = deluge / pump demand; Stby = standby/essential supplies.", 9, 400, "start", GREY)
    lab(s, 30, y + 50, "Qualitative and conceptual (A): it extends the Rev B cause-and-effect to the utilities and offsites; voting, delays, SIL and bypass rules are not specified. Each unit sheet carries its own trips and valve fail positions.", 9, 400, "start", GREY)
    eq(pkg, sh, "CE-901", "Cause-and-effect summary", "table", "qualitative", "-", "-", "-", "A")
    return finish(pkg, sh, AREA, "CE-901", "Cause-and-effect summary", [("Causes", f"{len(data)}", "A"), ("Effects", "10 columns", "A"), ("Basis", "qualitative", "A"), ("SIL / voting", "not assigned", "gap")],
                  ["Read with sheet 915 (levels) and sheets 801 and 813 (steam and CW trips). Actions marked M require the operator to confirm because spurious action (e.g. deluge or plant trip) has its own hazard.",
                   "Loss of instrument air drives valves to their fail positions on the unit sheets: the matrix therefore marks A for the area ESDs rather than X.",
                   "Gaps: loop-by-loop cause-and-effect needs the P&ID tag lists of all areas, the licensors' trip lists and a SIL study."])


def lint(pkg):
    names = [r[0] for r in pkg.equip]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    for r in pkg.relief: assert r[5], f"relief without destination {r}"
    ids = {k[0] for k in STREAMS}
    for sh in pkg.sheets:
        for m in re.finditer(r'<polygon points="[^"]*" fill="#fff" stroke="[^"]*" stroke-width="1.5"/>\s*<text[^>]*>([^<]*)</text>', "".join(sh.p)):
            assert m.group(1) in ids, f"stream diamond {m.group(1)} on sheet {sh.no} not in STREAMS"
    for no in HAZ_SHEETS: assert any(v[0].startswith("XV") and v[-1] == no for v in pkg.valves), f"sheet {no} has no ESD valve"
    return True


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID", "Rev B balance scaled K=%.4f; area 90 offsites and safety" % K)
    pkg.total = NSHEETS
    build(pkg); lint(pkg)
    pkg.sheets.sort(key=lambda x: x.no)
    write_html(pkg.sheets, "/tmp/area90.html", "Coal-to-urea area 90", previews=True)
    for w in WARN: print("WARN", w)
    print(len(pkg.sheets), "sheets;", len(pkg.lines), "lines;", len(pkg.inst), "instruments;", len(pkg.equip), "equipment;", len(pkg.relief), "relief")
    print(f"FL_HP {FL_HP:.1f} FL_LP {FL_LP:.1f}  store {CAP_T:,.0f} t  bags/h {BAGS_H:,.0f} lines {BAG_LINES}  trucks/d {TRUCKS_D:.0f} wagons/d {WAGONS_D:.0f}")
    return pkg


if __name__ == "__main__":
    main()

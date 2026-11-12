#!/usr/bin/env python3
"""urea_area_80.py - Area 80 Utilities of the coal-to-urea unit-by-unit P&ID package (Talcher-class, 3,850 t/d urea).

Usage: python3 scripts/urea_area_80.py        (builds /tmp/area80.html with per-sheet previews and runs the lint)

Basis and number discipline (tags S sourced, D derived, A assumed screening value with range):
 - Urea rate U, gasifier/shift steam (Rev B streams 3, 6, 8), process water (stream 23), O2/N2 streams: Rev B balance x K (D).
 - Urea-train steam 0.92 t/t (0.85-1.30) and cooling water 70 t/t (75 Snam): UBA 2001 as already read in gen_pid_urea.py (S).
 - Compressor/ASU power: gen_pid_urea.ASU_MW, K401_MW, K601_MW, ELEC_OTHER_MW (S/D) x K.
 - There is NO steam generation balance in Rev B (E-101/E-102/E-103/E-601 duties are not computed, no property model in the
   stdlib toolkit). The steam system is therefore sized on the DEMAND side with the letdown/aux-boiler worst case (A).
 - Steam and water enthalpy values are not typed: the desuperheater spray and deaerator steam use two screening constants
   (cp of steam 2.2 kJ/kg/K, effective spray latent+sensible 2,300 kJ/kg) tagged A; replace by a steam-table enthalpy balance.
"""
import sys, os, math, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *

AREA = "80"
NSHEETS = 20

# ============================ basis (all tagged) =================================================================
A_RANGES = {}   # name -> (value, lo, hi, text) for the notes file


def aval(name, v, lo, hi, text):
    A_RANGES[name] = (v, lo, hi, text); return v


U = g.M[22] * 3.6 * K                                             # D urea t/h (160.4)
HP_RB = (g.M[3] + g.M[6] + g.M[8]) * 3.6 * K                      # D Rev B streams 3+6+8 (gasifier + shift steam), consumed, no condensate
MP_U = g.UBA_STEAM_T_PER_T * U                                    # D 0.92 t/t (S UBA 2001 p.19) x U
MP_LO, MP_HI = g.UBA_STEAM_RANGE[0] * U, g.UBA_STEAM_RANGE[1] * U
P_HP, T_HP = 50.0, 400.0                                          # Rev B streams 3/6/8 conditions (A in Rev B)
P_MP = aval("P_MP", 25.0, 18.0, 30.0, "MP header pressure, bar abs (not sourced; urea stripper steam)")
T_MP = aval("T_MP", 300.0, 250.0, 350.0, "MP header temperature, C")
P_LP = aval("P_LP", 4.5, 3.5, 6.0, "LP header pressure, bar abs; carbamate-condenser steam side is 4 bar per UBA (via gen_pid_urea)")
T_LP = aval("T_LP", 160.0, 150.0, 200.0, "LP header temperature, C")
LP_FRAC = aval("LP_FRAC", 0.20, 0.10, 0.30, "LP users (C-302 reboiler etc., excl. deaerator) as fraction of MP urea steam; C-302 duty is NOT computed in Rev B")
CP_S = aval("CP_S", 2.2, 2.0, 2.6, "cp of superheated steam, kJ/kg/K (screening)")
LAM = aval("LAM", 2300.0, 2100.0, 2500.0, "spray water: sensible heating from ~105 C to saturation plus latent heat, kJ/kg (screening)")
BD_F = aval("BD_F", 0.02, 0.01, 0.03, "boiler blowdown fraction of steam raised")
FL_F = aval("FL_F", 0.25, 0.15, 0.35, "fraction of blowdown flashing to LP header at V-803")
RET_MP = aval("RET_MP", 0.90, 0.80, 0.95, "condensate return fraction of MP urea steam")
RET_LP = aval("RET_LP", 0.80, 0.60, 0.90, "condensate return fraction of LP user steam")
PC_REUSE = aval("PC_REUSE", 0.90, 0.60, 0.95, "fraction of process water (stream 23) reused as BFW after hydrolysis/desorption")
COND_FLASH = aval("COND_FLASH", 0.02, 0.01, 0.05, "flash steam at V-801 as fraction of returned condensate (not credited to the LP header, conservative)")
T_DA, T_COND, T_DM = 105.0, 90.0, 30.0                            # A deaerator, returned condensate, DM water temperatures, C
VENT_F = aval("VENT_F", 0.002, 0.001, 0.005, "deaerator vent as fraction of BFW")
LAM_LP = 2200.0                                                   # A effective LP steam heat release in deaerator, kJ/kg
CPW = 4.18                                                        # kJ/kg/K liquid water (screening)


def solve_steam():
    """fixed-point mass/heat balance of the steam-water system on the demand side (D); closes by construction, asserted below"""
    ds = 0.0
    for _ in range(200):
        lp_t = LP_FRAC * MP_U + ds                                 # LP header total = users + deaerator steam
        r2 = CP_S * (T_MP - T_LP) / LAM
        m_mp2 = lp_t / (1 + r2); sp2 = lp_t - m_mp2
        mp_t = MP_U + m_mp2
        r1 = CP_S * (T_HP - T_MP) / LAM
        m_hp1 = mp_t / (1 + r1); sp1 = mp_t - m_hp1
        hp_t = HP_RB + m_hp1
        bd = BD_F * hp_t
        bfw = hp_t + bd + sp1 + sp2
        c_mp, c_lp = RET_MP * MP_U, RET_LP * LP_FRAC * MP_U
        pc = g.M[23] * 3.6 * K; pc_re = PC_REUSE * pc
        fc = (1 - COND_FLASH) * (c_mp + c_lp) + pc_re
        vent = VENT_F * bfw
        X = bfw + vent
        a = CPW * (T_DA - T_DM) / LAM_LP; b = CPW * (T_DA - T_COND) * fc / LAM_LP
        dm = (X - fc - b) / (1 + a)
        ds_new = a * dm + b
        if abs(ds_new - ds) < 1e-10: ds = ds_new; break
        ds = ds_new
    d = dict(ds=ds, lp_t=lp_t, r1=r1, r2=r2, m_mp2=m_mp2, sp2=sp2, mp_t=mp_t, m_hp1=m_hp1, sp1=sp1, hp_t=hp_t, bd=bd, bfw=bfw,
             c_mp=c_mp, c_lp=c_lp, pc=pc, pc_re=pc_re, fc=fc, vent=vent, dm=dm, flash=FL_F * bd, bd_liq=bd - FL_F * bd)
    # closure checks
    assert abs(d["m_hp1"] + d["sp1"] - d["mp_t"]) < 1e-9 and abs(d["m_mp2"] + d["sp2"] - d["lp_t"]) < 1e-9
    assert abs(d["dm"] + d["fc"] + d["ds"] - d["bfw"] - d["vent"]) < 1e-6                   # deaerator mass
    assert abs(CPW * (T_DA - T_DM) * d["dm"] + CPW * (T_DA - T_COND) * d["fc"] - d["ds"] * LAM_LP) < 1e-6   # deaerator heat
    return d


SS = solve_steam()
DM_RAW_WASTE = aval("DM_RAW_WASTE", 0.05, 0.03, 0.10, "DM plant regeneration/rinse waste as fraction of raw-water feed")
DM_RAW = SS["dm"] / (1 - DM_RAW_WASTE); DM_EFF = DM_RAW - SS["dm"]

# ---- cooling water (duty from the Rev B model) ----
CW_UREA = g.UBA_CW_T_PER_T * U                                    # D t/h, S UBA 70 t/t urea (Snam 75)
CW_DT = aval("CW_DT", 10.0, 8.0, 12.0, "CW temperature rise across users, K (wet-bulb for Talcher not sourced)")
T_CWS = aval("T_CWS", 32.0, 30.0, 35.0, "CW supply temperature, C")
Q_UREA_MW = CW_UREA * 1000 / 3600 * CPW * CW_DT / 1000            # D MW (UBA t/t x cp x dT)
HEAT_REJ = aval("HEAT_REJ", 0.85, 0.80, 0.95, "fraction of compressor/ASU shaft power rejected to CW through inter/after-coolers")
P_ASU, P_K401, P_K601, P_OTH = g.ASU_MW * K, g.K401_MW * K, g.K601_MW * K, g.ELEC_OTHER_MW * K     # D MW (Rev B x K)
Q_MACH_MW = HEAT_REJ * (P_ASU + P_K401 + P_K601)                  # D
Q_CW_MW = Q_UREA_MW + Q_MACH_MW                                   # central case (A: excludes E-102/E-103/C-302 coolers, NH3 refrigeration condensers: gaps)
Q_CW_LO = Q_UREA_MW
Q_CW_HI = Q_CW_MW * 1.30
CW_Q = Q_CW_MW * 1000 / (CPW * CW_DT) * 3.6                       # t/h  D
CW_Q_LO, CW_Q_HI = Q_CW_LO * 1000 / (CPW * CW_DT) * 3.6, Q_CW_HI * 1000 / (CPW * CW_DT) * 3.6
LAM_EV = aval("LAM_EV", 2400.0, 2300.0, 2450.0, "latent heat of evaporation at cooling-tower water temperature, kJ/kg")
COC = aval("COC", 5.0, 4.0, 6.0, "cycles of concentration (raw water analysis is a gap)")
DRIFT_F = aval("DRIFT_F", 0.0002, 0.0001, 0.0005, "drift loss as fraction of circulation")
EVAP = Q_CW_MW * 1000 / LAM_EV * 3.6                              # t/h  D
DRIFT = DRIFT_F * CW_Q
CWBD = EVAP / (COC - 1) - DRIFT                                   # D
CWMK = EVAP + CWBD + DRIFT                                        # D
assert abs(CWMK - EVAP - CWBD - DRIFT) < 1e-9 and CWBD > 0
CW_HALF = CW_Q / 2                                                # A two supply headers
RHO_CW = 995.0

# ---- ETP / ZLD ----
PC_REJ = (1 - PC_REUSE) * SS["pc"]
ETP_IN = CWBD + DM_EFF + SS["bd_liq"] + PC_REJ
TDS_F = aval("TDS_F", 0.002, 0.001, 0.005, "dissolved solids in ETP inflow, mass fraction (raw water analysis is a gap)")
CAKE_SOL = aval("CAKE_SOL", 0.75, 0.60, 0.90, "solids fraction of the salt cake")
CAKE = TDS_F * ETP_IN / CAKE_SOL
ETP_REUSE = ETP_IN - CAKE
assert abs(ETP_IN - ETP_REUSE - CAKE) < 1e-9
CT_MK_NET = CWMK - ETP_REUSE
RAW = DM_RAW + CT_MK_NET                                          # raw water abstraction (excludes service/potable/fire/coal-area: gaps)

# ---- air, nitrogen ----
RHO_AIR_N = 28.96 / 22.414 / 1000                                 # t/Nm3 (D: M / 22.414 at 0 C, 1.013 bar)
IA_NM3 = aval("IA_NM3", 6000.0, 3000.0, 10000.0, "instrument air Nm3/h (control-valve count not available at this level)")
PA_NM3 = aval("PA_NM3", 3000.0, 1500.0, 6000.0, "plant (service) air Nm3/h")
N2_NM3 = aval("N2_NM3", 2000.0, 500.0, 5000.0, "continuous plant nitrogen Nm3/h (blanketing, seals, purges; start-up inerting is intermittent and a gap)")
P_AIR = 9.0                                                       # A bar abs discharge (about 8 bar g)
K_AIR, ETA_C = 1.4, 0.70                                          # ideal-gas k (S physics), isentropic efficiency (A)


def comp_kw(nm3_h, p1, p2, T1=35.0):
    m = nm3_h * RHO_AIR_N * 1000 / 3600                           # kg/s
    return m * 1.005 * (T1 + 273.15) * ((p2 / p1) ** ((K_AIR - 1) / K_AIR) - 1) / ETA_C   # D, cp air 1.005 kJ/kg/K


KW_AIR = comp_kw(IA_NM3 + PA_NM3, 1.013, P_AIR)
KW_N2 = comp_kw(N2_NM3, 1.0, 11.0, 25.0)
RHO_BFW = 955.0
KW_BFW = (SS["bfw"] * 1000 / 3600 / RHO_BFW) * 65e5 / 0.70 / 1000          # D kW: Q dP / eff (dP 65 bar A, eff 0.70 A)
KW_CWP = (CW_Q * 1000 / 3600 / RHO_CW) * 3.5e5 / 0.75 / 1000               # D kW: dP 3.5 bar (A), eff 0.75 (A)
ELEC_ID = P_ASU + P_K401 + P_K601 + P_OTH + (KW_BFW + KW_CWP + KW_AIR + KW_N2) / 1000

# ---- auxiliary boiler (coal-fired, A) ----
AUX_F = aval("AUX_F", 0.35, 0.25, 0.50, "start-up/standby steam as fraction of (HP gasifier+shift steam + MP urea steam)")
AUX = AUX_F * (HP_RB + MP_U)                                      # D t/h
DH_HP = aval("DH_HP", 2.76, 2.6, 2.9, "enthalpy rise BFW(105 C) to 50 bar 400 C steam, MJ/kg (steam-table check pending)")
ETA_B = aval("ETA_B", 0.85, 0.80, 0.90, "aux boiler efficiency on HHV")
EXC = aval("EXC", 0.20, 0.15, 0.30, "excess air, CFB")
CO = g.COAL
COAL_AUX = AUX * DH_HP / (ETA_B * g.HHV_COAL)                     # t/h  D (HHV S Dulong, gen_pid_urea.HHV_COAL)
O2_REQ = 32 / 12 * CO["carbon"] + 8 * CO["hydrogen"] + CO["sulfur"] - CO["oxygen"]   # D kg O2 / kg coal (as fired)
AIR_AUX = COAL_AUX * O2_REQ * (1 + EXC) / 0.2314                   # t/h D (O2 mass fraction of air 0.2314)
ASH_AUX = COAL_AUX * CO["ash"]
FLUE_AUX = COAL_AUX + AIR_AUX - ASH_AUX
assert abs(COAL_AUX + AIR_AUX - FLUE_AUX - ASH_AUX) < 1e-9


# ---- panel text-fit check (the data panel columns are 150/215/80 px at 10 pt): warn, do not hack the library ----
import pid_unit as _pu, pid_unit2 as _pu2
WARN = []
_orig_dp = _pu.data_panel


def _chk_dp(s, pkg, sh, tag, name, rows, notes):
    for r in rows:
        if len(str(r[0])) > 25 or len(str(r[1])) > 38 or len(str(r[2])) > 14: WARN.append((sh.no, r))
    if len(notes) > 8 or sum(len(n) for n in notes) > 1900: WARN.append((sh.no, "notes too long"))
    return _orig_dp(s, pkg, sh, tag, name, rows, notes)


_pu.data_panel = _chk_dp; _pu2.data_panel = _chk_dp

HAZ_SHEETS = {}   # sheets with toxic/flammable gas inventory that must have an ESD valve (none in area 80 except the coal boiler fuel train: MFT only)


# ============================ stream helpers =====================================================================
def S_(i, name, phase, flow, T, P, mw=None, rho=None):
    assert len(str(i)) <= 3, i
    return simple(str(i), name, phase, flow, T, P, mw=mw, rho=rho)


def steam(i, name, flow, T, P): return S_(i, name, "steam", flow, T, P, mw=18.015)
def water(i, name, flow, T, P, rho=990.0): return S_(i, name, "liq", flow, T, P, rho=rho)
def fixrelief(pkg, no, dest, set_bar=None):
    """template PSV uses the FIRST inlet design pressure and always says flare: patch the register row (drawing shows tag only)"""
    hit = [r for r in pkg.relief if r[0] == f"PSV-{no}01"]
    assert hit, no
    for r in hit:
        r[5] = dest
        if set_bar is not None: r[3] = fm(set_bar)


# ============================ local drawing helpers (draw around template gaps) ==================================
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


def wtable(s, x, y, colw, rows, size=9.0, ymax=775, head=True):
    """table with wrapped cells; asserts the table stays inside the drawing area"""
    lh = size + 2.6
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), max(int((colw[j] - 8) / (size * 0.52)), 4)) or [""] for j, c in enumerate(r)]
        rh = max(len(c) for c in cells) * lh + 5
        if i % 2 == 0 and not (head and i == 0): R(s, x, y, sum(colw), rh, "#f6f7fa", "none")
        if head and i == 0: R(s, x, y, sum(colw), rh, "#e8eaf0", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, ln in enumerate(c): lab(s, cx + 4, y + (k + 1) * lh, ln, size, 700 if (head and i == 0) else 400)
            cx += colw[j]
        y += rh
    assert y <= ymax, f"table overflow y={y}"
    return y


def local_sheet(pkg, no, title, tag, name):
    return head(pkg, AREA, no, title, tag, name)


def add_stream_diamond(sh, x, y, st): strm(sh, x, y, st.n)


# ============================ build ==============================================================================
def build(pkg):
    n0 = len(pkg.sheets); a = "A"
    T_ = lambda x: f"{x:,.1f}"
    d = SS
    # ---- streams ----
    s_hp_sup = steam("801", "HP steam supply (E-101,B-801)", d["hp_t"], T_HP, P_HP)
    s_hp_rb = steam("802", "HP steam to R-101/201/202", HP_RB, T_HP, P_HP)
    s_hp_ld = steam("803", "HP steam to PRDS-801", d["m_hp1"], T_HP, P_HP)
    s_sp1 = water("804", "spray BFW to PRDS-801", d["sp1"], 105.0, 65.0, 955.0)
    s_mp_t = steam("805", "MP steam from PRDS-801", d["mp_t"], T_MP, P_MP)
    s_mp_u = steam("806", "MP steam to C-601 stripper", MP_U, T_MP, P_MP)
    s_mp_ld = steam("807", "MP steam to PRDS-802", d["m_mp2"], T_MP, P_MP)
    s_sp2 = water("808", "spray BFW to PRDS-802", d["sp2"], 105.0, 65.0, 955.0)
    s_lp_t = steam("809", "LP steam from PRDS-802", d["lp_t"], T_LP, P_LP)
    s_lp_u = steam("810", "LP steam to users (C-302 etc)", LP_FRAC * MP_U, T_LP, P_LP)
    s_lp_da = steam("811", "LP steam to D-801", d["ds"], T_LP, P_LP)
    local_headers(pkg, s_hp_sup, s_hp_rb, s_hp_ld, s_sp1, s_mp_t, s_mp_u, s_mp_ld, s_sp2, s_lp_t, s_lp_u, s_lp_da)
    # ---- 802 / 803 PRDS ----
    sheet_package(pkg, AREA, 802, "Area 80  Utilities  -  PRDS-801 HP to MP pressure letdown with desuperheater",
                  dict(tag="PRDS-801", hazard="HP steam 400 C; noise", name="HP to MP letdown + desuperheater", spec="A1",
                       inlets=[(s_hp_ld, "HP"), (s_sp1, "BFW spray", "PL")], outlets=[(s_mp_t, "MP")],
                       utilities=[],
                       desc=["pressure-reducing valve PV-802, spray valve TV-802", f"spray ratio r = cp (T_in-T_out)/lambda = {d['r1']:.3f} (D, A consts)", f"{T_HP:g} C -> {T_MP:g} C outlet set point (A)"],
                       interlocks=[("TAHH", "MP outlet temperature high-high (closes letdown)", "0-450 C", f"HH {T_MP+60:.0f} C (A)"),
                                   ("TALL", "MP outlet temperature low (spray valve stuck open)", "0-450 C", f"L {T_MP-40:.0f} C (A)"),
                                   ("PAHH", "MP header pressure high-high", f"0-{round_up(P_MP*1.5,5):g} bar", f"HH {P_MP*1.1:.0f} bar (A)")],
                       relief="downstream MP header overpressure on PRV failure open",
                       type="PRV + desuperheater", op=f"{P_HP:g} -> {P_MP:g} bar", basis="D",
                       rows=[("Spray ratio r1", f"{d['r1']:.3f} kg/kg", "D"), ("Spray water", f"{d['sp1']:.1f} t/h", "D"), ("MP out = HP + spray", f"{d['mp_t']:.1f} t/h", "D asserted"),
                             ("Sizing case", "MP all via letdown", "A"), ("Valves", "PV-802, TV-802, bypass", "A")],
                       notes=["Mass closure: HP steam + spray = MP steam, asserted in code. Spray ratio uses two screening constants (cp 2.2 kJ/kg/K, 2,300 kJ/kg); replace by a steam-table enthalpy balance (gap).",
                              "Letdown is sized for the worst case where the MP header is fed only through the station; it must also pass the start-up case when B-801 supplies HP steam.",
                              "Downstream PSV protects the MP header (set at design pressure of MP); load = PRV failed-open flow, not sized."]))
    fixrelief(pkg, 802, "atmosphere via silencer, safe location (A)", design_conditions(P_MP, T_MP)[0])
    sheet_package(pkg, AREA, 803, "Area 80  Utilities  -  PRDS-802 MP to LP pressure letdown with desuperheater",
                  dict(tag="PRDS-802", hazard="MP steam 300 C; noise", name="MP to LP letdown + desuperheater", spec="A1",
                       inlets=[(s_mp_ld, "MP"), (s_sp2, "BFW spray", "PL")], outlets=[(s_lp_t, "LP")],
                       utilities=[],
                       desc=["pressure-reducing valve PV-803, spray valve TV-803", f"spray ratio r = {d['r2']:.3f} (D, A consts)", f"{T_MP:g} C -> {T_LP:g} C outlet set point (A)"],
                       interlocks=[("TAHH", "LP outlet temperature high-high", "0-300 C", f"HH {T_LP+40:.0f} C (A)"),
                                   ("PAHH", "LP header pressure high-high", f"0-{round_up(P_LP*2,5):g} bar", f"HH {P_LP*1.2:.1f} bar (A)"),
                                   ("PALL", "LP header pressure low-low", f"0-{round_up(P_LP*2,5):g} bar", f"LL {P_LP*0.6:.1f} bar (A)")],
                       relief="downstream LP header overpressure on PRV failure open",
                       type="PRV + desuperheater", op=f"{P_MP:g} -> {P_LP:g} bar", basis="D",
                       rows=[("Spray ratio r2", f"{d['r2']:.3f} kg/kg", "D"), ("Spray water", f"{d['sp2']:.1f} t/h", "D"), ("LP out", f"{d['lp_t']:.1f} t/h", "D asserted"),
                             ("LP = users + D-801", f"{LP_FRAC*MP_U:.1f} + {d['ds']:.1f} t/h", "D"), ("Flash steam from V-803", f"{d['flash']:.2f} t/h", "D not credited")],
                       notes=["LP header demand = LP users (A, 20 % of MP urea steam; C-302 reboiler duty is not computed in Rev B) + deaerator stripping steam (D). Blowdown flash steam from V-803 is not credited (conservative).",
                              "Because deaerator steam depends on BFW, which depends on the spray water, the balance is solved by fixed-point iteration and closed to 1e-10 (asserted).",
                              "LP header relief is atmospheric (silencer); no toxic inventory."]))
    fixrelief(pkg, 803, "atmosphere via silencer, safe location (A)", design_conditions(P_LP, T_LP)[0])
    # ---- 804 condensate tank ----
    s_cin = water("812", "Condensate returns (MP/LP)", d["c_mp"] + d["c_lp"], T_COND, 3.0, 965.0)
    s_cflash = steam("813", "Flash steam to LP header", COND_FLASH * (d["c_mp"] + d["c_lp"]), 105.0, 1.2)
    s_cout = water("814", "Condensate to D-801", d["c_mp"] + d["c_lp"] - s_cflash.flow, T_COND, 1.2, 965.0)
    sheet_vessel(pkg, AREA, 804, "Area 80  Utilities  -  V-801 condensate collection tank and transfer pumps",
                 dict(tag="V-801", name="Condensate collection tank", inlet=s_cin, gas=s_cflash, liq=s_cout, res_min=10.0, pumps="P-801", pump_dp_bar=4.0, spec="A1",
                      svc_in="PL", svc_gas="ST", svc_liq="PL", mat="A: CS", hazard="hot condensate; NH3/urea carry-over",
                      relief_case="blocked outlet; steam breakthrough", relief_dest="atmosphere via silencer (A)",
                      notes=[f"Inflow = {RET_MP:.2f} x MP urea steam + {RET_LP:.2f} x LP user steam (A, ranges 0.80-0.95 / 0.60-0.90). Flash steam 2 % of inflow (A) to LP header.",
                             "Process condensate from the urea evaporator (stream 23) is routed via the hydrolyser/desorber (not drawn, vendor) and joins at D-801 (sheet 805).",
                             "Condensate polishing (iron, ammonia) is not drawn: gap until the urea licensor gives quality limits.",
                             "Template draws the PSV line labelled 'to flare header' (template defect); register destination is atmosphere via silencer."]))
    fixrelief(pkg, 804, "atmosphere via silencer, safe location (A)")
    # ---- 805 deaerator + BFW pumps ----
    s_fc = water("815", "DM + condensate feed", d["dm"] + d["fc"], 70.0, 2.0, 975.0)
    s_vent = steam("816", "Deaerator vent", d["vent"], 105.0, 1.2)
    s_bfw = water("817", "BFW to HP boilers", d["bfw"], T_DA, 1.2, RHO_BFW)
    s_dm_in = water("818", "DM water makeup", d["dm"], T_DM, 4.0, 995.0)
    s_pc = water("819", "Treated process condensate", d["pc_re"], T_COND, 3.0, 965.0)
    s_dsteam = s_lp_da
    sh = sheet_vessel(pkg, AREA, 805, "Area 80  Utilities  -  D-801 deaerator with BFW storage and BFW pumps",
                 dict(tag="D-801", name="Deaerator + BFW storage", inlet=s_fc, gas=s_vent, liq=s_bfw, res_min=15.0, pumps="P-802", pump_dp_bar=65.0, spec="A1",
                      svc_in="PL", svc_gas="ST", svc_liq="BFW", mat="A: CS", hazard="hot water 105 C; steam",
                      relief_case="LP steam PRV failure; blocked vent", relief_dest="atmosphere via silencer (A)",
                      notes=[f"Feed = DM {d['dm']:.1f} + returned condensate {d['fc']-d['pc_re']:.1f} + treated process condensate {d['pc_re']:.1f} t/h (D). Stripping steam {d['ds']:.1f} t/h (stream 811) enters through a sparger drawn locally (template has one inlet).",
                             f"Mass: DM + condensate + steam = BFW + vent; heat: m_DM cp (105-30) + m_c cp (105-90) = m_steam x 2,200 kJ/kg (A). Both asserted. Vent {VENT_F*100:.1f} % of BFW (A 0.1-0.5 %).",
                             "Pumps P-802A/B: discharge 65 bar over suction = HP header 50 bar + 15 bar drum, control valve and line margin (A). Minimum-flow recycle is not drawn (template gap).",
                             "Size by 15 min hold-up (A) on BFW flow; deaerator vendor rating by spray/tray capacity is a gap."]))
    run(sh, pkg, sh, "805", AREA, s_dsteam, [(60, 425), (410, 425)], "LP header", "D-801 sparger", "A1", "ST", 70, label=(66, 399))
    fixrelief(pkg, 805, "atmosphere via silencer, safe location (A)")
    # ---- 806 BFW distribution ----
    s_bfw_hp = water("820", "BFW to E-101/102/103 drums", d["hp_t"] + d["bd"], T_DA, 70.0, RHO_BFW)
    s_bfw_sp = water("821", "BFW spray water (PRDS)", d["sp1"] + d["sp2"], T_DA, 70.0, RHO_BFW)
    s_bfw_in = water("822", "BFW from P-802A/B", d["bfw"], T_DA, 70.0, RHO_BFW)
    s_bfw_aux = water("823", "BFW to B-801 (standby)", 0.0 + 1e-3, T_DA, 70.0, RHO_BFW)
    s_bfw_in.flow = s_bfw_hp.flow + s_bfw_sp.flow + s_bfw_aux.flow          # close the header: in = out
    assert abs(s_bfw_in.flow - (d["bfw"] + 1e-3)) < 1e-6
    sheet_package(pkg, AREA, 806, "Area 80  Utilities  -  BFW distribution header, spray take-off, minimum-flow and chemical dosing",
                  dict(tag="BFW-801", hazard="hot BFW 105 C at 70 bar", name="BFW header and distribution", spec="A1",
                       inlets=[(s_bfw_in, "BFW", "PL")], outlets=[(s_bfw_hp, "to drums", "PL"), (s_bfw_sp, "to PRDS", "PL"), (s_bfw_aux, "to B-801", "PL")],
                       utilities=[("Hydrazine-free", 0.0, "dosing", "gap"), ("Phosphate", 0.0, "dosing", "gap")],
                       desc=["header with FV control valves per drum,", "spray take-off with check valves,", "pump minimum-flow line to D-801 (not sized)"],
                       interlocks=[("PALL", "BFW header pressure low-low (standby pump start)", "0-100 bar", "LL 60 bar (A)"),
                                   ("FAL", "BFW flow low to drums", "0-500 t/h", "L 70 % of design (A)"),
                                   ("TAH", "BFW temperature high", "0-150 C", "H 115 C (A)")],
                       type="piping header and valve manifold", op=f"{T_DA:g} C / 70 bar", basis="D",
                       rows=[("BFW total", f"{d['bfw']:.1f} t/h", "D"), ("Steam raised (drums)", f"{d['hp_t']:.1f} t/h", "D"), ("Blowdown", f"{d['bd']:.2f} t/h", "D 2 % (1-3)"),
                             ("Spray", f"{d['sp1']+d['sp2']:.1f} t/h", "D"), ("B-801 standby trickle", "0.001 t/h placeholder", "A"), ("Closure", "in = sum(out)", "D asserted")],
                       notes=["BFW = steam raised + blowdown + spray, with steam raised = HP header worst case; drum steam outputs by E-101/E-102/E-103 are not computed in Rev B (gap).",
                              "Chemical dosing is drawn as a utility arrow only; boiler chemistry limits are a gap (no fetched document).",
                              "BFW header at 70 bar is the pump discharge plus line margin (A)."]))
    # ---- 807 blowdown flash drum ----
    s_bd = water("824", "Boiler blowdown", d["bd"], 148.0, 4.5, 800.0)
    s_bd.phase = "twophase"; s_bd.mw = 18.015; s_bd.rho_in = None
    s_fl = steam("825", "Flash steam to LP header", d["flash"], 148.0, 4.5)
    s_bdl = water("826", "Blowdown liquid to cooler/ETP", d["bd_liq"], 148.0, 4.5, 920.0)
    assert abs(s_bd.flow - s_fl.flow - s_bdl.flow) < 1e-9
    sheet_vessel(pkg, AREA, 807, "Area 80  Utilities  -  V-803 HP blowdown flash drum",
                 dict(tag="V-803", name="HP blowdown flash drum", inlet=s_bd, gas=s_fl, liq=s_bdl, res_min=10.0, spec="A1", svc_in="PL", svc_gas="ST", svc_liq="PL",
                      mat="A: CS", hazard="flashing hot water (scald)", relief_case="blocked outlet; blowdown valve stuck open", relief_dest="atmosphere via silencer (A)",
                      notes=[f"Blowdown {BD_F*100:.0f} % of steam raised (A 1-3 %); {FL_F*100:.0f} % of it flashes to the LP header (A 15-35 %; a steam-table flash calculation is a gap). Liquid to a blowdown cooler (not drawn) then to ETP-801.",
                             "Drum pressure is 4.5 bar (LP header); flash steam is not credited in the LP header balance of sheet 803.",
                             "Tangential inlet and vent-to-atmosphere reserve are vendor details (gap)."]))
    fixrelief(pkg, 807, "atmosphere via silencer, safe location (A)")
    # ---- 808 aux boiler ----
    s_coal = S_("827", "Coal to B-801", "slurry", COAL_AUX, 25.0, 1.0, rho=800.0)
    s_air = S_("828", "Combustion air", "gas", AIR_AUX, 25.0, 1.1, mw=28.96)
    s_bfw_b = water("829", "BFW to B-801", AUX, T_DA, 70.0, RHO_BFW)
    s_stm_b = steam("830", "HP steam from B-801", AUX, T_HP, P_HP)
    s_flue = S_("831", "Flue gas to stack", "gas", FLUE_AUX, 140.0, 1.0, mw=29.0)
    s_ash = S_("832", "Ash to silo", "slurry", ASH_AUX, 120.0, 1.0, rho=700.0)
    sheet_package(pkg, AREA, 808, "Area 80  Utilities  -  B-801 auxiliary boiler (coal-fired CFB assumed), start-up and standby steam",
                  dict(tag="B-801", hazard="coal dust, hot surfaces, steam", name="Auxiliary boiler (coal, A)", spec="A1",
                       inlets=[(s_coal, "coal", "PS"), (s_air, "air", "PG"), (s_bfw_b, "BFW", "PL")], outlets=[(s_stm_b, "HP steam", "ST"), (s_flue, "flue gas", "PG"), (s_ash, "ash", "PS")],
                       utilities=[],
                       desc=["circulating-fluidised-bed boiler (A)", "fuel: coal from the plant coal stream basis", "light-up with oil (A); SO2 capture and ESP/bag filter by vendor"],
                       interlocks=[("LAHH", "drum level high-high (MFT)", "0-100 %", "HH 90 % (A)"),
                                   ("LALL", "drum level low-low (MFT)", "0-100 %", "LL 10 % (A)"),
                                   ("PAHH", "drum / steam pressure high-high (MFT)", f"0-{round_up(P_HP*1.5,10):g} bar", f"HH {P_HP*1.1:.0f} bar (A)"),
                                   ("XA", "furnace flame / bed temperature loss (MFT)", "0-1000 C", "per vendor (gap)")],
                       relief="drum / superheater overpressure (steam, to atmosphere)",
                       type="coal-fired auxiliary boiler", op=f"{AUX:.0f} t/h steam {P_HP:g} bar / {T_HP:g} C", basis="A",
                       rows=[("Firing", "coal CFB, LDO light-up", "A"), ("Duty (A fraction)", f"{AUX_F:.2f} x (HP+MP) = {AUX:.0f} t/h", "A 0.25-0.50"),
                             ("Enthalpy rise", f"{DH_HP:g} MJ/kg", "A 2.6-2.9"), ("Efficiency on HHV", f"{ETA_B:.2f}", "A 0.80-0.90"), ("Coal HHV", f"{g.HHV_COAL:.2f} MJ/kg", "S Dulong"),
                             ("Coal burn", f"{COAL_AUX:.1f} t/h", "D"), ("Excess air", f"{EXC*100:.0f} %", "A 15-30"), ("Ash", f"{ASH_AUX:.1f} t/h", "D ash 35 %")],
                       notes=["ASSUMPTION: coal-fired. Reason: coal is the site fuel and the Rev B balance has no natural-gas supply. A gas-fired package boiler would replace stream 827 by fuel gas and drop the ash line.",
                              "Air from stoichiometric O2 on the Rev B coal analysis (as fired) plus excess air (A); flue = coal + air - ash (asserted). Fly-ash/bed-ash split, limestone and SO2 are gaps.",
                              "Role: start-up steam for gasifier warm-up, ASU/ammonia loop heat-up and trip recovery; in normal running it floats on the HP header. Burner management/MFT logic follows a named standard: not read, gap.",
                              "The coal dust explosion hazard is handled on the coal-handling sheets (area 10); here the bunker is out of scope."]))
    fixrelief(pkg, 808, "atmosphere via silencer, safe location (A)", design_conditions(P_HP, T_HP)[0])
    # ---- 809 raw water tank ----
    s_riv = water("833", "Raw water from intake (gap)", RAW, 30.0, 3.0)
    s_raw = water("834", "Raw water to DM / CT", RAW, 30.0, 4.0)
    sheet_tank(pkg, AREA, 809, "Area 80  Utilities  -  T-801 raw water storage and pumps",
               dict(tag="T-801", name="Raw water storage", inflow=s_riv, outflow=s_raw, days=0.5, spec="A1", svc="PL", pumps="P-805", pump_dp=4.0, roof="cone",
                    hazard="none (water)", mat="A: CS / RCC",
                    notes=["Raw water source, abstraction permit and analysis are NOT in the Rev B basis (gap): no document was fetched. The intake is a placeholder.",
                           f"Flow = DM plant feed {DM_RAW:.1f} + cooling-tower makeup net of ETP reuse {CT_MK_NET:.1f} t/h (D). Fire, potable, service and coal-area water are not included (gap).",
                           "Storage 0.5 d (A, range 0.25-2 d); fire-water reserve is on area 90, sheet 912."]))
    # ---- 810 DM plant ----
    s_rw_dm = water("835", "Raw water to DM", DM_RAW, 30.0, 4.0)
    s_dm = water("836", "DM water to T-802", d["dm"], T_DM, 3.0, 995.0)
    s_regen = water("837", "Regeneration effluent", DM_EFF, 30.0, 1.0)
    sheet_package(pkg, AREA, 810, "Area 80  Utilities  -  DM-801 demineralisation plant (cation, anion, mixed bed; packaged)",
                  dict(tag="DM-801", hazard="acid / caustic regenerants", name="DM plant (packaged)", spec="A1",
                       inlets=[(s_rw_dm, "raw water", "PL")], outlets=[(s_dm, "DM water", "PL"), (s_regen, "regen. effluent", "PL")],
                       utilities=[],
                       desc=["trains: strong-acid cation -> degasser ->", "strong-base anion -> mixed bed polisher", "2 x 100 % trains, regeneration on conductivity/volume"],
                       interlocks=[("QAH", "DM water conductivity high (divert to waste)", "0-50 uS/cm", "H per BFW spec (gap)"),
                                   ("QAH", "silica breakthrough high", "0-100 ppb", "H per BFW spec (gap)"),
                                   ("LAL", "regenerant tank level low", "0-100 %", "L 20 % (A)")],
                       type="packaged DM plant", op="ambient, 4 bar", basis="A",
                       rows=[("DM output", f"{d['dm']:.1f} t/h", "D D-801 bal."), ("Regeneration waste", f"{DM_RAW_WASTE*100:.0f} % of raw", "A 3-10 %"), ("Raw feed", f"{DM_RAW:.1f} t/h", "D"),
                             ("Waste to ETP", f"{DM_EFF:.1f} t/h", "D"), ("Regenerants", "vendor data not available", "gap"), ("Water quality", "raw analysis not available", "gap")],
                       notes=["Packaged unit: only the mass balance is set here. Resin volumes, bed counts, regenerant consumption and BFW quality limits are vendor / licensor data (gap).",
                              "DM output includes the make-up for the gasifier and shift steam (Rev B streams 3, 6, 8), which is consumed with no condensate return.",
                              "Regeneration effluent is acid/alkali neutralised at ETP-801 (sheet 819)."]))
    # ---- 811 DM tank ----
    s_dm_t = water("838", "DM water to deaerator", d["dm"], T_DM, 3.0, 995.0)
    sheet_tank(pkg, AREA, 811, "Area 80  Utilities  -  T-802 DM water storage and transfer pumps",
               dict(tag="T-802", name="DM water storage", inflow=s_dm, outflow=s_dm_t, days=0.5, spec="A1", svc="PL", pumps="P-806", pump_dp=4.0, roof="cone",
                    hazard="none (high-purity water, N2 blanket)", mat="A: lined CS / SS",
                    notes=["0.5 d storage (A, 0.25-1 d) on the DM demand; N2 blanket from sheet 817 keeps CO2 and O2 out (A).",
                           "DM demand includes the one-pass steam to the gasifier and shift (Rev B 3+6+8) and BFW losses."]))
    # ---- 812 cooling tower ----
    s_hotA = water("839", "CW return header A", CW_HALF, T_CWS + CW_DT, 2.0, RHO_CW)
    s_hotB = water("840", "CW return header B", CW_HALF, T_CWS + CW_DT, 2.0, RHO_CW)
    s_mk = water("841", "CT makeup water", CWMK, 30.0, 3.0)
    s_cold = water("842", "Cold water to basin pumps", CW_Q - EVAP - DRIFT - CWBD + CWMK, T_CWS, 1.2, RHO_CW)
    s_cbd = water("843", "CT blowdown to ETP", CWBD, T_CWS, 2.0)
    s_evp = S_("844", "Evaporation + drift (vapour)", "gas", EVAP + DRIFT, 38.0, 1.0, mw=18.015)
    assert abs(s_hotA.flow + s_hotB.flow + s_mk.flow - s_cold.flow - s_cbd.flow - s_evp.flow) < 1e-6
    sheet_package(pkg, AREA, 812, "Area 80  Utilities  -  CT-801 cooling tower (induced draft, cells)",
                  dict(tag="CT-801", hazard="drift mist; rotating fans", name="Cooling tower", spec="A1",
                       inlets=[(s_hotA, "hot A", "CW"), (s_hotB, "hot B", "CW"), (s_mk, "makeup", "PL")],
                       outlets=[(s_cold, "cold water", "CW"), (s_cbd, "blowdown", "CW"), (s_evp, "evap + drift", "PG")],
                       utilities=[],
                       desc=[f"heat rejected {Q_CW_MW:.0f} MW (D; range {Q_CW_LO:.0f}-{Q_CW_HI:.0f})", f"dT {CW_DT:g} K (A 8-12), supply {T_CWS:g} C (A)", f"cycles {COC:g} (A 4-6); cells N+1 (A)"],
                       interlocks=[("LAL", "basin level low (makeup valve)", "0-100 %", "L 30 % (A)"),
                                   ("VAHH", "fan vibration high-high (trip)", "per vendor", "per vendor (gap)"),
                                   ("TAH", "cold water temperature high", "0-60 C", f"H {T_CWS+4:.0f} C (A)")],
                       type="induced-draft cooling tower", op=f"{CW_Q:,.0f} t/h {T_CWS+CW_DT:g}->{T_CWS:g} C", basis="D",
                       rows=[("Circulation", f"{CW_Q:,.0f} t/h", "D"), ("UBA urea train alone", f"{CW_UREA:,.0f} t/h ({Q_UREA_MW:.0f} MW)", "S UBA x U"), ("Machinery heat", f"{Q_MACH_MW:.0f} MW", f"D 0.85 x power"),
                             ("Evaporation", f"{EVAP:.0f} t/h", "D Q/lambda"), ("Drift", f"{DRIFT:.2f} t/h", "A 0.02 %"), ("Blowdown", f"{CWBD:.0f} t/h", "D E/(C-1)"), ("Makeup", f"{CWMK:.0f} t/h", "D asserted")],
                       notes=[f"CW duty = UBA urea-train cooling water (70 t/t x {U:.1f} t/h urea, dT 10 K) + {HEAT_REJ*100:.0f} % of ASU, K-401 and K-601 shaft power ({P_ASU:.0f}+{P_K401:.0f}+{P_K601:.0f} MW). Range: urea train alone {Q_CW_LO:.0f} MW to central +30 % {Q_CW_HI:.0f} MW (circulation {CW_Q_LO:,.0f}-{CW_Q_HI:,.0f} t/h).",
                              "Not included (gap): E-102, E-103, C-302 coolers, NH3 refrigeration condensers, turbine surface condensers; Rev B does not compute these duties.",
                              "Two supply headers are assumed so that each stays under the NPS 48 limit of the sizing table (A).",
                              "Fans, cell count and approach need a design wet-bulb temperature: not sourced (gap)."]))
    # ---- 813 CW pumps ----
    s_cA = water("845", "Basin outlet A", CW_HALF, T_CWS, 1.2, RHO_CW)
    s_cB = water("846", "Basin outlet B", CW_HALF, T_CWS, 1.2, RHO_CW)
    s_sA = water("847", "CW supply header A", CW_HALF, T_CWS, 4.7, RHO_CW)
    s_sB = water("848", "CW supply header B", CW_HALF, T_CWS, 4.7, RHO_CW)
    sheet_package(pkg, AREA, 813, "Area 80  Utilities  -  P-803 cooling-water circulating pumps (3 duty + 1 spare)",
                  dict(tag="P-803", hazard="rotating equipment", name="CW circulating pumps A-D", spec="A1",
                       inlets=[(s_cA, "basin A", "CW"), (s_cB, "basin B", "CW")], outlets=[(s_sA, "supply A", "CW"), (s_sB, "supply B", "CW")],
                       utilities=[("Motors", KW_CWP / 1000, "MW", "D")],
                       desc=[f"{CW_Q:,.0f} t/h total, dP 3.5 bar (A), eff 0.75 (A)", "3 x 33 % duty + 1 spare; motor-driven;", "one diesel/steam-driven standby is a gap (see ESD)"],
                       interlocks=[("PALL", "CW supply header pressure low-low (standby start)", "0-10 bar", "LL 3 bar (A)"),
                                   ("PAL", "CW supply pressure low", "0-10 bar", "L 3.5 bar (A)"),
                                   ("TAH", "CW return temperature high", "0-60 C", f"H {T_CWS+CW_DT+4:.0f} C (A)")],
                       type="vertical wet-pit pumps", op=f"{CW_Q:,.0f} t/h", basis="D",
                       rows=[("Total flow", f"{CW_Q:,.0f} t/h", "D"), ("Pump power", f"{KW_CWP/1000:.1f} MW", "D Q dP/eta"), ("Header split", "2 x 50 %", "A"), ("Pumps", "3 duty + 1 spare", "A")],
                       notes=["Loss of CW is a plant-wide trip cause: PALL starts the standby pump, a second PALL trips the machinery trains (cause and effect on area 90, sheet 916).",
                              "Differential pressure and efficiency are screening values (A); head from the real network is a gap."]))
    # ---- 814 chemical dosing ----
    dose = lambda ppm: ppm * 1e-6 * CWMK
    s_inh = S_("849", "Scale/corrosion inhibitor", "liq", dose(20.0), 30.0, 5.0, rho=1100.0)
    s_bio = S_("850", "Biocide", "liq", dose(5.0), 30.0, 5.0, rho=1100.0)
    s_acid = S_("851", "Dispersant", "liq", dose(10.0), 30.0, 5.0, rho=1050.0)
    s_dosed = S_("852", "Chemicals to CT basin", "liq", s_inh.flow + s_bio.flow + s_acid.flow, 30.0, 4.0, rho=1080.0)
    sheet_package(pkg, AREA, 814, "Area 80  Utilities  -  DOS-801 cooling-water chemical dosing",
                  dict(tag="DOS-801", hazard="oxidising biocide, acids", name="CW chemical dosing skid", spec="A1",
                       inlets=[(s_inh, "inhibitor", "PL"), (s_bio, "biocide", "PL"), (s_acid, "dispersant", "PL")], outlets=[(s_dosed, "to CT basin", "PL")],
                       utilities=[("Makeup flow", CWMK, "t/h", "D")],
                       desc=["3 day tanks with dosing pumps (2 x 100 %)", "dose paced on makeup flow (FIC)", "bund and drain to ETP; no acid dosing assumed (A)"],
                       interlocks=[("LAL", "chemical day-tank level low", "0-100 %", "L 20 % (A)"),
                                   ("QAH", "CW conductivity high (blowdown valve open)", "0-5000 uS/cm", "per cycles of concentration (A)"),
                                   ("AAH", "free halogen / biocide residual", "per site", "per site standard (gap)")],
                       type="chemical dosing skid", op="ambient", basis="A",
                       rows=[("Inhibitor dose", "20 ppm of makeup", "A 5-100"), ("Biocide dose", "5 ppm of makeup", "A 1-20"), ("Dispersant dose", "10 ppm of makeup", "A 2-50"),
                             ("Total", f"{s_dosed.flow*1000:.0f} kg/h", "D"), ("Product choice", "water-treatment vendor", "gap")],
                       notes=["Dose rates are placeholders (A) so the lines can be sized; real doses follow raw water analysis and product data, neither available (gap).",
                              "Chemical storage hazards (oxidising biocide, acids) need their own HAZOP node."]))
    # ---- 815 air compressors ----
    s_ia_air = S_("853", "Ambient air", "gas", (IA_NM3 + PA_NM3) * RHO_AIR_N, 35.0, 1.013, mw=28.96)
    s_ia = S_("854", "Instrument air (dry)", "gas", IA_NM3 * RHO_AIR_N, 40.0, P_AIR, mw=28.96)
    s_pa = S_("855", "Plant air", "gas", PA_NM3 * RHO_AIR_N, 40.0, P_AIR, mw=28.96)
    s_cond_a = S_("856", "Compressor condensate", "liq", 0.0005, 40.0, 1.0, rho=1000.0)
    sheet_package(pkg, AREA, 815, "Area 80  Utilities  -  K-801 instrument and plant air compressors, after-coolers and dryers",
                  dict(tag="K-801", hazard="compressed air, noise", name="Instrument + plant air package", spec="A1",
                       inlets=[(s_ia_air, "air", "PG")], outlets=[(s_ia, "instrument air", "PG"), (s_pa, "plant air", "PG"), (s_cond_a, "condensate", "PL")],
                       utilities=[("Motors", KW_AIR / 1000, "MW", "D")],
                       desc=[f"3 x 50 % oil-free screw (A) at {P_AIR:g} bar abs", "after-coolers, desiccant dryers 2 x 100 %", "dew point -40 C (A); filters; receivers V-804"],
                       interlocks=[("PALL", "instrument air header low-low (plant trip alarm)", "0-12 bar", "LL 5 bar abs (A)"),
                                   ("PAL", "instrument air header low (start standby)", "0-12 bar", "L 6 bar abs (A)"),
                                   ("TAH", "compressor discharge temperature high", "0-200 C", "H 120 C (A)"),
                                   ("MAH", "instrument air dew point high", "-80 to 0 C", "H -30 C (A)")],
                       relief="receiver / header overpressure",
                       type="packaged air compressors and dryers", op=f"{P_AIR:g} bar abs", basis="D",
                       rows=[("Instrument air", f"{IA_NM3:,.0f} Nm3/h", "A 3,000-10,000"), ("Plant air", f"{PA_NM3:,.0f} Nm3/h", "A 1,500-6,000"), ("Mass density", f"{RHO_AIR_N*1000:.3f} kg/Nm3", "D M/22.414"),
                             ("Isentropic power", f"{KW_AIR:.0f} kW", "D k 1.4, A"), ("Dew point", "-40 C", "A"), ("Fail-safe", "valves fail per sheet", "A")],
                       notes=["Demand is a placeholder: it needs the count of control valves and the analyser purges, which is only known after the unit sheets are collected. It is tagged A with a 3x range.",
                              "Instrument air loss drives the plant to its fail positions; the valve fail positions are on each unit sheet. No standalone IA dryer standard text was used.",
                              "Isentropic power: m cp T1 ((p2/p1)^((k-1)/k) - 1)/eta with k = 1.4 (ideal gas, physics), eta 0.70 (A), intercooling ignored (conservative)."]))
    fixrelief(pkg, 815, "atmosphere, safe location (A)", design_conditions(P_AIR, 40.0)[0])
    # ---- 816 air receiver ----
    s_wet = S_("857", "Dried air from dryers", "gas", (IA_NM3 + PA_NM3) * RHO_AIR_N, 40.0, P_AIR, mw=28.96)
    s_rec = S_("858", "Air to headers", "gas", s_wet.flow - 0.0005, 40.0, P_AIR - 0.3, mw=28.96)
    s_rc = S_("859", "Receiver drain", "liq", 0.0005, 40.0, 1.0, rho=1000.0)
    local_receiver(pkg, s_wet, s_rec, s_rc)
    # ---- 817 nitrogen ----
    n2_flow = N2_NM3 * 28.014 / 22.414 / 1000
    s_n2a = stream("860", "N2 slip from ASU-101 (S26)", "gas", flow=n2_flow, T=25.0, P=1.2, base=26)
    s_n2h = stream("861", "Plant N2 header", "gas", flow=n2_flow, T=40.0, P=11.0, base=26)
    sheet_package(pkg, AREA, 817, "Area 80  Utilities  -  N2-801 nitrogen distribution (ASU slip, compression, buffer, header)",
                  dict(tag="N2-801", hazard="asphyxiant gas", name="Plant nitrogen distribution", spec="A1",
                       inlets=[(s_n2a, "ASU N2", "PG")], outlets=[(s_n2h, "N2 header", "PG")],
                       utilities=[("Motor", KW_N2 / 1000, "MW", "D")],
                       desc=["slip of Rev B stream 26 (surplus N2, 365 t/h)", "2 x 100 % compressors to 11 bar abs (A)", "buffer receiver, pressure-controlled header"],
                       interlocks=[("PALL", "N2 header pressure low-low (inert users)", "0-15 bar", "LL 8 bar (A)"),
                                   ("AAL", "O2 in N2 header high", "0-5 %", "H 0.5 % (A)"),
                                   ("PAHH", "N2 header pressure high-high", "0-15 bar", "HH 13 bar (A)")],
                       relief="header overpressure (asphyxiant gas, vent to safe location)",
                       type="nitrogen distribution", op="11 bar abs", basis="D",
                       rows=[("Rev B surplus N2 (S26)", f"{g.M[26]*3.6*K:.0f} t/h", "D"), ("Continuous demand", f"{N2_NM3:,.0f} Nm3/h = {n2_flow:.2f} t/h", "A 500-5,000"), ("Compression", f"{KW_N2:.0f} kW", "D isentropic"),
                             ("Start-up inerting", "intermittent, not sized", "gap"), ("Hazard", "asphyxiant", "-")],
                       notes=["Plenty of N2 is available from ASU-101 stream 26 (surplus, vent / other use in Rev B), so the slip is a small fraction; liquid N2 backup storage is a gap.",
                              "Demand: seal gas, blanketing (T-802, flare purge), instrument purges; start-up inerting of gasifier and ammonia loop is intermittent and large (not sized).",
                              "Asphyxiation hazard: area oxygen-deficiency detection is on area 90, sheet 914."]))
    fixrelief(pkg, 817, "atmosphere via safe location (A)", design_conditions(11.0, 40.0)[0])
    # ---- 818 power single line ----
    local_power_sld(pkg)
    # ---- 819 ETP / ZLD ----
    s_e1 = water("862", "CT blowdown", CWBD, T_CWS, 2.0)
    s_e2 = water("863", "DM regeneration effluent", DM_EFF, 30.0, 1.0)
    s_e3 = water("864", "Boiler blowdown + S23 reject", d["bd_liq"] + PC_REJ, 50.0, 1.0)
    s_er = water("866", "Recovered water to CT makeup", ETP_REUSE, 35.0, 3.0)
    s_ek = S_("867", "Salt cake to secure landfill", "slurry", CAKE, 40.0, 1.0, rho=1300.0)
    assert abs(s_e1.flow + s_e2.flow + s_e3.flow - s_er.flow - s_ek.flow) < 1e-9
    sheet_package(pkg, AREA, 819, "Area 80  Utilities  -  ETP-801 effluent treatment and zero-liquid-discharge concept (packaged)",
                  dict(tag="ETP-801", hazard="acid/alkali, NH3 in effluent", name="ETP + ZLD (packaged concept)", spec="A1",
                       inlets=[(s_e1, "CT blowdown", "PL"), (s_e2, "DM effluent", "PL"), (s_e3, "blowdn + S23", "PL")],
                       outlets=[(s_er, "recovered", "PL"), (s_ek, "salt cake", "PS")],
                       utilities=[],
                       desc=["neutralise + equalise -> clarify/filter ->", "membrane (RO) -> brine concentrator ->", "crystalliser / dryer; condensate reused (A)"],
                       interlocks=[("QAH", "pH out of range at neutralisation (stop discharge)", "0-14 pH", "H/L per site (gap)"),
                                   ("LAHH", "equalisation tank level high-high", "0-100 %", "HH 90 % (A)"),
                                   ("QAH", "NH3-N in recovered water high (divert)", "per site", "per site standard (gap)")],
                       type="effluent treatment and ZLD package", op="ambient", basis="A",
                       rows=[("Inflow", f"{ETP_IN:.1f} t/h", "D"), ("TDS in inflow", f"{TDS_F*100:.1f} wt %", "A 0.1-0.5"), ("Salt cake", f"{CAKE:.2f} t/h at {CAKE_SOL*100:.0f} % solids", "A 60-90 %"),
                             ("Recovered water", f"{ETP_REUSE:.1f} t/h", "D"), ("Closure", "in = reuse + cake", "D asserted"), ("Sour water / coal runoff", "not in this node", "gap")],
                       notes=["Concept only: sources are the quantified area-80 streams. Sour-water stripper bottoms (area 300), coal-pile runoff, sanitary and oily water (sheet 906) are gaps.",
                              "UBA 2001 gives 0.46-0.65 m3 discharged process water per t urea (S, via gen_pid_urea) vs Rev B stream 23 of 0.30 t/t; 10 % of stream 23 is rejected here, 90 % reused as BFW (A 60-95 %).",
                              "Discharge limits, technology choice and brine chemistry need the site permit and raw water analysis (not available)."]))
    # ---- 820 utility balance ----
    local_balance(pkg)
    assert len(pkg.sheets) - n0 == NSHEETS, len(pkg.sheets) - n0
    return pkg


def local_headers(pkg, hp, hprb, hpld, sp1, mpt, mpu, mpld, sp2, lpt, lpu, lpda):
    """801: three steam headers drawn locally (the package template cannot show five outlets without label overlap)"""
    sh, lp = local_sheet(pkg, 801, "Area 80  Utilities  -  HP / MP / LP steam header system", "SH-801", "HP / MP / LP steam headers")
    s = sh; d = SS
    ys = {"HP": 190, "MP": 400, "LP": 580}
    names = {"HP": f"HP header {P_HP:g} bar / {T_HP:g} C (Rev B)", "MP": f"MP header {P_MP:g} bar / {T_MP:g} C (A)", "LP": f"LP header {P_LP:g} bar / {T_LP:g} C (A)"}
    for k, y in ys.items():
        PL(s, [(60, y), (960, y)], 5.0, INK); lab(s, 64, y - 9, names[k], 10.5, 700)
    def ln(st, frm, to, x, y, dx=14, dy=-6):
        no, n = reg_line(pkg, sh, AREA, st, frm, to, "A1", "ST" if st.phase == "steam" else "PL")
        strm(s, x, y, st.n); lab(s, x + dx, y + dy, no, 8.6, 700); lab(s, x + dx, y + dy + 10, f"{st.name} {st.flow:.1f} t/h", 8.3, 400, "start", GREY)
    def drop(x, y0, y1): pipe(s, [(x, y0), (x, y1)], 2.4)
    # sources
    node(s, 100, 100, 270, 46, ["E-101/102/103 steam raising", "duty not computed in Rev B (gap)"], "#fff4e0")
    node(s, 420, 100, 240, 46, ["B-801 auxiliary boiler", f"start-up / standby {AUX:.0f} t/h (A)"], "#fff4e0")
    drop(235, 146, 190); drop(540, 146, 190)
    ln(hp, "E-101, B-801", "HP header", 700, 165, 14, -6)
    # HP users
    node(s, 700, 250, 250, 46, ["R-101 / R-201 / R-202", "gasifier and shift steam (consumed)"], "#e8f5e9")
    drop(800, 190, 250); ln(hprb, "HP header", "R-101/201/202", 800, 222, 14, 0)
    # PRDS-801
    node(s, 210, 245, 190, 56, ["PRDS-801", "HP to MP letdown + desuperheater"], "#eef3fb")
    drop(305, 190, 245); ln(hpld, "HP header", "PRDS-801", 305, 217, 14, -6)
    drop(305, 301, 400); ln(mpt, "PRDS-801", "MP header", 305, 350, 14, -6)
    pipe(s, [(60, 280), (210, 280)], 2.0); ln(sp1, "BFW header", "PRDS-801", 100, 280, -46, 20)
    # MP users and PRDS-802
    node(s, 700, 450, 250, 46, ["C-601 HP stripper", "MP steam 0.92 t/t urea (S UBA)"], "#e8f5e9")
    drop(800, 400, 450); ln(mpu, "MP header", "C-601", 800, 425, 14, -6)
    node(s, 210, 450, 190, 56, ["PRDS-802", "MP to LP letdown + desuperheater"], "#eef3fb")
    drop(305, 400, 450); ln(mpld, "MP header", "PRDS-802", 305, 425, 14, -6)
    drop(305, 506, 580); ln(lpt, "PRDS-802", "LP header", 305, 543, 14, -6)
    pipe(s, [(60, 480), (210, 480)], 2.0); ln(sp2, "BFW header", "PRDS-802", 100, 480, -46, 20)
    # LP side
    node(s, 470, 500, 220, 40, ["V-803 flash steam", "to LP, not credited (0.9 t/h)"], "#f6f7fa"); pipe(s, [(580, 540), (580, 580)], 1.8, INK, False, "5 3")
    node(s, 520, 640, 200, 46, ["LP users: C-302 reboiler,", "tracing, heaters (A)"], "#e8f5e9"); drop(620, 580, 640); ln(lpu, "LP header", "LP users", 620, 612, 14, -6)
    node(s, 770, 640, 190, 46, ["D-801 deaerator", "stripping steam"], "#e8f5e9"); drop(865, 580, 640); ln(lpda, "LP header", "D-801", 865, 612, 14, -6)
    # relief and instruments
    for k, (no_, x) in {"HP": (1, 900), "MP": (2, 900), "LP": (3, 900)}.items():
        y = ys[k]; PL(s, [(x, y), (x, y - 28)], 1.6)
        pr, tt = {"HP": (P_HP, T_HP), "MP": (P_MP, T_MP), "LP": (P_LP, T_LP)}[k]
        psv_at(s, pkg, sh, x, y - 46, f"PSV-801{no_:02d}", f"SH-801 {k} header", "blocked in; PRV failed open", design_conditions(pr, tt)[0], "atmosphere via silencer, safe location (A)", "not sized: needs PRV failed-open flow")
    for k, ty, (fn, svc, rng, al) in [("HP", 150, ("PAHH", "HP header pressure high-high", f"0-{round_up(P_HP*1.5,10):g} bar", f"HH {P_HP*1.1:.0f} bar (A)")),
                                      ("HP", 215, ("PALL", "HP header pressure low-low (gasifier steam loss)", f"0-{round_up(P_HP*1.5,10):g} bar", f"LL {P_HP*0.8:.0f} bar (A)")),
                                      ("MP", 400, ("PAHH", "MP header pressure high-high", f"0-{round_up(P_MP*1.5,5):g} bar", f"HH {P_MP*1.1:.0f} bar (A)")),
                                      ("LP", 580, ("PALL", "LP header pressure low-low", f"0-{round_up(P_LP*2,5):g} bar", f"LL {P_LP*0.6:.1f} bar (A)"))]:
        y = ys[k]; x = 1030
        PL(s, [(960, y), (x - 15, ty)], 1.0, BLUE, "4 3")
        bub(s, pkg, sh, x, ty, fn, f"{801}{len([r for r in pkg.inst if r[-1]==801])+60}", "SH-801", svc, rng, al, panel=True)
    bub(s, pkg, sh, 1030, 460, "TAH", "80170", "SH-801", "HP header temperature high", "0-600 C", f"H {T_HP+30:.0f} C (A)")
    PL(s, [(960, 190), (990, 190), (990, 470), (1015, 460)], 1.0, BLUE, "4 3")
    lab(s, 40, 740, "Header flows are the demand-side worst case: MP and LP are taken through PRDS-801/802 (no turbine or process steam sources credited). Drip legs, traps and header isolation valves: A.", 9, 400, "start", GREY)
    eq(pkg, sh, "SH-801", "HP / MP / LP steam headers", "steam header system", f"HP {P_HP:g} / MP {P_MP:g} / LP {P_LP:g} bar", "per header PSV set", "A", "A: CS / Cr-Mo for HP", "D")
    rows = [("HP gasifier+shift", f"{HP_RB:.1f} t/h", "D Rev B x K"), ("MP urea (0.92 t/t)", f"{MP_U:.1f} t/h", "D S UBA p.19"), ("MP range", f"{MP_LO:.0f}-{MP_HI:.0f} t/h", "S UBA p.18,24"),
            ("LP users", f"{LP_FRAC*MP_U:.1f} t/h", "A 10-30 % MP"), ("D-801 steam", f"{d['ds']:.1f} t/h", "D"), ("HP header total", f"{d['hp_t']:.1f} t/h", "D worst case"), ("Closure", "HP-letdown = users", "D asserted")]
    return finish(pkg, sh, AREA, "SH-801", "HP / MP / LP steam headers", rows,
                  ["Header flows are the DEMAND-side worst case: all MP and LP steam is taken through the letdown stations. Steam generation by E-101/E-102/E-103 and E-601 is not computed in Rev B (needs a heat balance), so no steam source is credited.",
                   "HP 50 bar / 400 C are the Rev B stream conditions (A in Rev B); MP and LP pressures and temperatures are assumptions (A). LP 4.5 bar sits above the 4 bar carbamate-condenser steam side quoted by UBA via gen_pid_urea.",
                   "Header PSVs go to atmosphere via silencers (A); loads (PRV failed open) are not sized. Header instruments are registered; header low-low pressure on HP is a gasifier steam-loss alarm into ESD-3.",
                   "Condensate return and steam traps are on sheet 804."])


HOLD_MIN = aval("HOLD_MIN", 2.0, 1.0, 5.0, "air receiver hold-up time on compressor trip, minutes at design demand")
P_AIR_MIN = aval("P_AIR_MIN", 6.0, 5.0, 7.0, "lowest acceptable instrument-air pressure, bar abs")


def local_receiver(pkg, wet, rec, rc):
    """816: the vessel template sizes by LIQUID residence (air receiver would come out 0.0 m3), so the receiver is drawn locally with a gas hold-up volume (D)"""
    sh, lp = head(pkg, AREA, 816, "Area 80  Utilities  -  V-804 instrument and plant air receiver (hold-up on compressor trip)", "V-804", "Air receiver"); s = sh
    qn = (IA_NM3 + PA_NM3) / 3600.0                                  # Nm3/s
    V = qn * HOLD_MIN * 60 * 1.013 / (P_AIR - P_AIR_MIN)             # D m3: isothermal blow-down, V (p_hi - p_lo) = Qn t p_atm
    D = max(round_up((4 * V / (math.pi * 3.0)) ** (1 / 3), 0.1), 1.0); Ht = round_up(3.0 * D, 0.1)
    dP, dT = design_conditions(P_AIR - 1.013, 40.0)
    cx, top, w, h = 520, 220, 150, 300
    v = vvessel(s, cx, top, w, h)
    lab(s, cx - w / 2 - 12, top + h / 2, "V-804", 12, 700, "end"); lab(s, cx - w / 2 - 12, top + h / 2 + 14, "Air receiver", 9.5, 400, "end")
    lab(s, cx - w / 2 - 12, top + h / 2 + 27, f"{V:.0f} m3 ({D:.1f} m ID x {Ht:.1f} m) (D)", 9, 400, "end", GREY)
    run(s, pkg, sh, lp, AREA, wet, [(50, top + 70), (cx - w / 2, top + 70)], "K-801 dryers", "V-804", "A1", "IA", 1, label=(56, top + 44))
    run(s, pkg, sh, lp, AREA, rec, [(cx + 20, v["top"][1]), (cx + 20, 150), (1000, 150)], "V-804", "IA / PA headers", "A1", "IA", 2, label=(cx + 50, 124))
    run(s, pkg, sh, lp, AREA, rc, [(cx, v["bottom"][1]), (cx, 640), (800, 640)], "V-804", "drain trap to ETP", "A1", "PL", 3, label=(cx + 20, 600))
    psv_at(s, pkg, sh, cx - 40, top - 34, f"PSV-{lp}01", "V-804", "blocked outlet; compressor control failure", dP, "atmosphere, safe location (A)", "not sized: needs compressor flow")
    PL(s, [(cx - 40, top - 56), (cx - 40, 110), (200, 110)], 1.6, INK, "6 3"); lab(s, 204, 106, "PSV to atmosphere, safe location (A)", 8.5, 400, "start", GREY)
    bub(s, pkg, sh, cx + 150, top + 100, "PT", f"{lp}11", "V-804", "receiver pressure", f"0-{round_up(dP,5):g} bar", "-"); PL(s, [(cx + w / 2, top + 100), (cx + 135, top + 100)], 1.0, BLUE, "4 3")
    bub(s, pkg, sh, cx + 200, top + 100, "PAL", f"{lp}12", "V-804", "receiver pressure low (start standby)", f"0-{round_up(dP,5):g} bar", f"L {P_AIR_MIN+0.5:g} bar abs (A)", panel=True)
    bub(s, pkg, sh, cx + 250, top + 100, "PALL", f"{lp}13", "V-804", "receiver pressure low-low (plant alarm)", f"0-{round_up(dP,5):g} bar", f"LL {P_AIR_MIN-1:g} bar abs (A)", panel=True)
    bub(s, pkg, sh, cx + 150, top + 230, "LAH", f"{lp}21", "V-804", "drain pot level high", "0-100 %", "H 80 % (A)")
    blockv(s, pkg, sh, cx, 520 + 36, 90, f"HV-{lp}08", "-", 1, "gate", "drain block")
    eq(pkg, sh, "V-804", "Instrument and plant air receiver", "vertical vessel", f"{P_AIR:g} bar abs, 40 C", f"{dP:g} bar g / {dT:g} C (D)", f"{V:.0f} m3 ({D:.1f} x {Ht:.1f} m) (D)", "A: CS", "D")
    rows = [("Hold-up", f"{HOLD_MIN:g} min at design", "A 1-5 min"), ("Min pressure", f"{P_AIR_MIN:g} bar abs", "A 5-7"), ("Volume", f"{V:.0f} m3", "D isothermal"), ("Size", f"{D:.1f} m x {Ht:.1f} m", "D, L/D 3 A"),
            ("Design", f"{dP:g} bar g / {dT:g} C", "D"), ("Relief", f"PSV-{lp}01 set {dP:g} bar g", "A"), ("Hazard", "stored pressure", "-")]
    return finish(pkg, sh, AREA, "V-804", "Air receiver", rows,
                  ["Volume V = Qn t p_atm / (p_max - p_min): isothermal blow-down of the design demand (9,000 Nm3/h, A) for the hold-up time, between 9 bar abs and the minimum acceptable pressure (all A). The time to reach safe states after an air-compressor trip is a plant study (gap).",
                   "Drain through a level-controlled trap to the oily-water/ETP system (sheet 819 / area 90 sheet 906).",
                   "Drawn locally because the vessel template sizes by liquid residence only (an air receiver would be 0.0 m3)."])


def local_power_sld(pkg):
    sh, lp = local_sheet(pkg, 818, "Area 80  Utilities  -  SLD-801 power distribution, single-line block diagram", "SLD-801", "Power distribution (block)")
    s = sh
    lab(s, 30, 110, "Block diagram only: voltage levels, ratings, protection and earthing are electrical-design items and are not set here (no standard text used).", 9, 400, "start", GREY)
    grid = node(s, 40, 150, 150, 60, ["Grid / captive source", "supply route: gap"], "#fff4e0")
    dg = node(s, 40, 560, 150, 70, ["Emergency DG sets", "essential loads (A)"], "#fff4e0")
    hv = node(s, 260, 150, 150, 60, ["HV main switchboard", "incomers, bus section"])
    t1 = node(s, 470, 120, 150, 50, ["Transformer T1", "HV/MV (A)"]); t2 = node(s, 470, 190, 150, 50, ["Transformer T2", "HV/MV (A)"])
    mv = node(s, 680, 150, 170, 60, ["MV switchboard", "bus coupler, interlocked"])
    asu = node(s, 910, 112, 190, 52, ["ASU-101 compressors", f"{P_ASU:.0f} MW (D)"], "#e8f5e9")
    k4 = node(s, 910, 172, 190, 52, ["K-401 make-up / K-402", f"{P_K401:.0f} MW (D)"], "#e8f5e9")
    k6 = node(s, 910, 232, 190, 52, ["K-601 CO2 compressor", f"{P_K601:.0f} MW (D; drive A)"], "#e8f5e9")
    oth = node(s, 910, 292, 190, 52, ["Urea train + granulation", f"{P_OTH:.0f} MW (S UBA 43+23 kWh/t)"], "#e8f5e9")
    ut = node(s, 910, 352, 190, 52, ["Area 80 utilities", f"{(KW_BFW+KW_CWP+KW_AIR+KW_N2)/1000:.0f} MW (D)"], "#e8f5e9")
    lvt = node(s, 680, 320, 170, 56, ["MV/LV transformers", "motor control centres"])
    mcc = node(s, 680, 420, 170, 56, ["LV MCCs", "small motors, HVAC, lighting"])
    ess = node(s, 470, 560, 200, 70, ["Essential / ESD board", "fire pumps, ESD, F&G, flare ignition"], "#ffebee")
    ups = node(s, 730, 560, 190, 70, ["UPS + battery", "DCS, SIS, F&G, comms"], "#ffebee")
    link(s, grid, hv, "supply"); link(s, hv, t1); link(s, hv, t2); link(s, t1, mv); link(s, t2, mv)
    link(s, mv, asu); link(s, mv, k4); link(s, mv, k6); link(s, mv, oth); link(s, mv, ut)
    link(s, mv, lvt); link(s, lvt, mcc)
    link(s, dg, ess, "start on bus loss"); link(s, mcc, ess, "normal feed"); link(s, ess, ups)
    lab(s, 30, 700, f"Identified load {ELEC_ID:.0f} MW: ASU {P_ASU:.0f} + K-401 {P_K401:.0f} + K-601 {P_K601:.0f} + urea/granulation {P_OTH:.0f} + area 80 {(KW_BFW+KW_CWP+KW_AIR+KW_N2)/1000:.0f}; gasification island, coal handling, HVAC are gaps.", 9, 700, "start")
    lab(s, 30, 714, "If K-601 or other large drives are steam turbines, the electric load falls and the steam balance rises by the same energy (decision for the licensor).", 9, 400, "start", GREY)
    eq(pkg, sh, "SLD-801", "Power distribution (block)", "electrical single line (block)", f"identified {ELEC_ID:.0f} MW", "A", "-", "A: electrical design", "D")
    rows = [("Identified load", f"{ELEC_ID:.0f} MW", "D"), ("ASU-101", f"{P_ASU:.0f} MW", "S TDA x K"), ("K-401", f"{P_K401:.0f} MW", "S CoolProp xK"), ("K-601", f"{P_K601:.0f} MW", "S UBA x K"),
            ("Urea + granulation", f"{P_OTH:.0f} MW", "S UBA 66 kWh/t"), ("Area 80 pumps/compressors", f"{(KW_BFW+KW_CWP+KW_AIR+KW_N2)/1000:.0f} MW", "D"), ("Voltage levels", "not set", "gap"), ("Source", "grid/captive: gap", "gap")]
    finish(pkg, sh, AREA, "SLD-801", "Power distribution", rows,
           ["Essential / ESD board and UPS supply only the safety-critical loads; their list is derived from the ESD and fire-water sheets of area 90.",
            "Rev B gives machine powers (sourced as noted); 'Grid / captive source' is not part of the basis (gap): Talcher power route was not researched here.",
            "Motor starting, short-circuit level, protection co-ordination and standards (not read) are out of scope."])


def local_balance(pkg):
    sh, lp = local_sheet(pkg, 820, "Area 80  Utilities  -  plant utility balance (demand side, per t urea and plant total)", "UB-801", "Utility balance table")
    s = sh
    rows = [("Utility", "per t urea", "Plant total", "Basis tag", "Source / note"),
            ("Urea product", "1.00 t", f"{U:.1f} t/h", "D", "Rev B stream 22 x K (3,850 t/d)"),
            ("HP steam, gasifier + shift", f"{HP_RB/U:.3f} t", f"{HP_RB:.1f} t/h", "D", "Rev B streams 3+6+8 x K, consumed (no condensate)"),
            ("MP steam, urea train", f"{MP_U/U:.3f} t", f"{MP_U:.1f} t/h", "S/D", f"UBA 2001 p.19 0.92 t/t; range {MP_LO:.0f}-{MP_HI:.0f} t/h"),
            ("LP steam users + deaerator", f"{(LP_FRAC*MP_U+SS['ds'])/U:.3f} t", f"{LP_FRAC*MP_U+SS['ds']:.1f} t/h", "A/D", "LP users 20 % of MP (A); D-801 steam (D)"),
            ("HP header, worst case", f"{SS['hp_t']/U:.3f} t", f"{SS['hp_t']:.1f} t/h", "D", "all MP and LP through PRDS (no steam generation balance in Rev B)"),
            ("Auxiliary boiler B-801", f"{AUX/U:.3f} t", f"{AUX:.1f} t/h", "A", f"{AUX_F:.2f} x (HP+MP), range 0.25-0.50; coal {COAL_AUX:.1f} t/h (D)"),
            ("Boiler feedwater", f"{SS['bfw']/U:.3f} t", f"{SS['bfw']:.1f} t/h", "D", "steam raised + blowdown + spray"),
            ("DM water makeup", f"{SS['dm']/U:.3f} t", f"{SS['dm']:.1f} t/h", "D", "deaerator balance incl. 90 % reuse of stream 23"),
            ("Cooling water circulation", f"{CW_Q/U:.1f} t", f"{CW_Q:,.0f} t/h", "D", f"range {CW_Q_LO:,.0f}-{CW_Q_HI:,.0f}; UBA urea train {g.UBA_CW_T_PER_T:.0f} t/t (S)"),
            ("Cooling duty", f"{Q_CW_MW/U*1000:.0f} kWh", f"{Q_CW_MW:.0f} MW", "D", f"range {Q_CW_LO:.0f}-{Q_CW_HI:.0f} MW"),
            ("CT makeup", f"{CWMK/U:.2f} m3", f"{CWMK:.0f} t/h", "D", f"evaporation {EVAP:.0f}, blowdown {CWBD:.0f}, drift {DRIFT:.2f}"),
            ("Raw water abstraction", f"{RAW/U:.2f} m3", f"{RAW:.0f} t/h", "D", "DM feed + CT makeup net of ETP reuse; excludes fire/potable/service (gap)"),
            ("ETP inflow / reuse", f"{ETP_IN/U:.2f} m3", f"{ETP_IN:.0f} t/h", "D", f"recovered {ETP_REUSE:.0f} t/h, cake {CAKE:.2f} t/h"),
            ("Instrument + plant air", f"{(IA_NM3+PA_NM3)/U:.0f} Nm3", f"{IA_NM3+PA_NM3:,.0f} Nm3/h", "A", "3x range; control valve count not known"),
            ("Nitrogen (continuous)", f"{N2_NM3/U:.0f} Nm3", f"{N2_NM3:,.0f} Nm3/h", "A", "slip of Rev B stream 26"),
            ("Electric, identified", f"{ELEC_ID/U*1000:.0f} kWh", f"{ELEC_ID:.0f} MW", "D", "ASU, K-401, K-601, urea+granulation, area 80; others gap"),
            ("Process water to treatment", f"{SS['pc']/U:.2f} m3", f"{SS['pc']:.1f} t/h", "D", f"Rev B S23; UBA {g.UBA_PROCESS_WATER_M3[0]}-{g.UBA_PROCESS_WATER_M3[1]} m3/t (S) is higher")]
    wtable(s, 30, 100, [200, 90, 130, 80, 560], rows, 9.4, 775)
    eq(pkg, sh, "UB-801", "Utility balance", "table", "per t urea and total", "-", "-", "-", "D")
    finish(pkg, sh, AREA, "UB-801", "Utility balance", [("Urea rate", f"{U:.1f} t/h", "D"), ("Steam sources", "not balanced", "gap"), ("Cooling water", f"{CW_Q:,.0f} t/h", "D, range")],
           ["The table gathers the demands used on sheets 801-819 so that other areas can be checked against them. Every row repeats its tag and source.",
            "Not balanced (gap): steam generation by E-101/102/103 and E-601, turbine extraction, C-302 reboiler duty, E-103 cooler duty. These need a heat balance with a property model.",
            "UBA 2001 figures are those already read for Rev B (gen_pid_urea.py); no further document was fetched for area 80."])


def lint(pkg):
    names = [r[0] for r in pkg.equip]
    dup = {n for n in names if names.count(n) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    for r in pkg.relief: assert r[5], f"relief without destination {r}"
    ids = {k[0] for k in STREAMS}
    import re
    for sh in pkg.sheets:
        for m in re.finditer(r'<polygon points="[^"]*" fill="#fff" stroke="[^"]*" stroke-width="1.5"/>\s*<text[^>]*>([^<]*)</text>', "".join(sh.p)):
            assert m.group(1) in ids, f"stream diamond {m.group(1)} on sheet {sh.no} not in STREAMS"
    for no in HAZ_SHEETS: assert any(v[0].startswith("XV") and v[-1] == no for v in pkg.valves), f"sheet {no} has no ESD valve"
    return True


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID", "Rev B balance scaled K=%.4f; area 80 utilities" % K)
    pkg.total = NSHEETS
    build(pkg); lint(pkg)
    write_html(pkg.sheets, "/tmp/area80.html", "Coal-to-urea area 80", previews=True)
    for w in WARN: print("WARN", w)
    print(len(pkg.sheets), "sheets;", len(pkg.lines), "lines;", len(pkg.inst), "instruments;", len(pkg.equip), "equipment;", len(pkg.relief), "relief")
    print(f"U {U:.1f}  HP_RB {HP_RB:.1f}  MP {MP_U:.1f}  HP_T {SS['hp_t']:.1f}  BFW {SS['bfw']:.1f}  DM {SS['dm']:.1f}  DS {SS['ds']:.1f}  CW {CW_Q:,.0f} ({CW_Q_LO:,.0f}-{CW_Q_HI:,.0f})  Q {Q_CW_MW:.0f} MW  CWMK {CWMK:.0f}  RAW {RAW:.0f}  AUX {AUX:.1f} coal {COAL_AUX:.1f}  ELEC {ELEC_ID:.0f}")
    return pkg


if __name__ == "__main__":
    main()

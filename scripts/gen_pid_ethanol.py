#!/usr/bin/env python3
"""Generate the grain-based (1G) ethanol distillery P&ID set: P&ID, heat and material balance, four scenario overlays.
Basis: VertiStrat_DPR_Templates/Template_DPR_Ethanol_Grain_100KLPD.docx (100 KLPD, 330 d, process route, section 4). The HMB is computed in code
from capacity + stoichiometry + a short list of assumptions (A); closure is asserted. Screening aid, not certified design.

Usage (standard library only):
    python3 scripts/gen_pid_ethanol.py docs/pid/ETHANOL_PID_Set_RevB.html [--previews]
    chrome --headless=new --no-pdf-header-footer --print-to-pdf=docs/pid/ETHANOL_PID_Set_RevB.pdf file://$PWD/docs/pid/ETHANOL_PID_Set_RevB.html
Tags: S sourced, D derived (formula shown), A assumed by this drawing."""
import sys, os

import math

# ---- atomic masses (IUPAC standard atomic weights, rounded): C 12.011, H 1.008, O 15.999 (g/mol) -> D
MC, MH, MO = 12.011, 1.008, 15.999
M_H2O = 2 * MH + MO
M_ETOH = 2 * MC + 6 * MH + MO
M_CO2 = MC + 2 * MO
M_GLU = 6 * MC + 12 * MH + 6 * MO          # C6H12O6
M_ANH = 6 * MC + 10 * MH + 5 * MO          # C6H10O5 anhydroglucose unit of starch
COMPS = ["starch", "glucose", "ethanol", "water", "co2", "solids"]

# ---- S: capacity from the template (Template_DPR_Ethanol_Grain_100KLPD.docx, sections 1 and 9)
CAP_KLPD, DAYS = 100.0, 330
GRAIN_T_YR_TEMPLATE, DDGS_T_YR_TEMPLATE = 86800.0, 26000.0          # S: template section 9 (full capacity)
HOURS = DAYS * 24                                                    # D
PROD_M3_H = CAP_KLPD / 24.0                                          # D

# ---- A: assumptions (the single list printed on sheet 2)
A = dict(
    rho_prod=790.0,      # kg/m3 anhydrous product (A)
    x_prod=0.995,        # wt fraction ethanol in dehydrated product (A)
    x_hyd=0.94,          # wt fraction ethanol, rectifier overhead to molecular sieve (A)
    x_regen=0.70,        # wt fraction ethanol, sieve regeneration recycle to rectifier (A)
    x_s9=0.50,           # wt fraction ethanol, beer-column overhead vapour (A)
    loss=0.001,          # fraction of beer ethanol lost to stillage (A)
    starch=0.62,         # wt fraction starch in grain as received (A)
    moist=0.12,          # wt fraction moisture in grain as received (A)
    slurry=0.30,         # wt fraction grain (as received) in slurry (A)
    Y=0.93,              # Rev B: overall starch to ethanol + CO2 fraction (A; BioSTEAM-implied 0.930, ANL >= 0.916, range 0.88-0.95); balance stays as residual sugar/yeast in DDGS
    cap=0.60,            # fraction of stillage dry solids captured in decanter wet cake (A)
    cake=0.32,           # wt fraction solids in wet cake (A)
    syrup=0.35,          # wt fraction solids in syrup from evaporator (A)
    ddgs_moist=0.10,     # wt fraction moisture in DDGS (A)
    cp=4.0,              # kJ/kg/K aqueous streams (A)
    cp_et=2.4,           # kJ/kg/K ethanol liquid (A)
    lam_w=2257.0,        # kJ/kg latent heat of water at 100 C (A)
    lam_e=849.8,         # kJ/kg latent heat of ethanol at its NBP (D: CoolProp 8.0.0, frozen)
    lam_st=2100.0,       # kJ/kg latent heat of LP process steam (A)
    dh_ferm=85.0,        # kJ released per mol glucose fermented (A)
    RR_rect=3.5,         # Rev B rectifier reflux ratio (D: R/Rmin 1.29 from NRTL McCabe-Thiele, 39 ideal stages)
    econ=2.5,            # evaporator steam economy, kg evaporated per kg steam (A)
    n_eff=3,             # evaporator effects, equal evaporation per effect (A)
    eta_dry=0.65,        # dryer thermal efficiency (A)
)
REVA = dict(Y=0.90, lam_e=840.0, RR_rect=3.0)   # Rev A values, for the change table
T_ = dict(s1=30, s2=30, s3=60, s4=55, s5=85, s6=33, s7=33, s8=33, s9=95, s10=84, s11=40, s12=100, s13=104, s14=100, s16=60, s17=70, s18=55, s19=60, s20=95)
T_PRE = 80       # A: beer preheat to column
T_ST_OUT_CAP = 40


def mk(**k):
    d = {c: 0.0 for c in COMPS}; d.update(k); return d


def tot(d): return sum(d.values())


def solve(ov=None):
    r = {}; a = dict(A, **(ov or {}))
    P = PROD_M3_H * a["rho_prod"]                       # kg/h product (D)
    E_prod = a["x_prod"] * P
    # molecular sieve split: F = P + Rg ; x_hyd F = x_prod P + x_regen Rg  (D)
    Rg = P * (a["x_prod"] - a["x_hyd"]) / (a["x_hyd"] - a["x_regen"])
    F10 = P + Rg
    S11 = mk(ethanol=E_prod, water=P - E_prod)
    S12 = mk(ethanol=a["x_regen"] * Rg, water=(1 - a["x_regen"]) * Rg)
    S10 = mk(ethanol=a["x_hyd"] * F10, water=(1 - a["x_hyd"]) * F10)
    E9 = E_prod                                        # ethanol net through rectifier = product (recycle cancels)
    S9 = mk(ethanol=E9, water=E9 * (1 - a["x_s9"]) / a["x_s9"])
    # rectifier: S9 + S12 = S10 + S13 ; lees S13 carries the remaining water, no ethanol (A)
    S13 = mk(water=S9["water"] + S12["water"] - S10["water"])
    E8 = E9 / (1 - a["loss"])                          # ethanol in beer
    G_ferm = E8 / (2 * M_ETOH / M_GLU)                 # glucose fermented  (C6H12O6 -> 2 C2H5OH + 2 CO2)
    G_tot = G_ferm / a["Y"]
    CO2 = G_ferm * 2 * M_CO2 / M_GLU
    starch = G_tot * M_ANH / M_GLU
    w_hyd = G_tot - starch                             # water consumed by hydrolysis
    grain = starch / a["starch"]
    other = grain * (1 - a["starch"] - a["moist"])
    water_g = grain * a["moist"]
    S1 = mk(starch=starch, water=water_g, solids=other)
    S2 = dict(S1)
    S3 = mk(water=grain * (1 / a["slurry"] - 1))
    S4 = {c: S1[c] + S3[c] for c in COMPS}
    S5 = dict(S4)
    S6 = dict(S5); S6["starch"] = 0.0; S6["glucose"] = G_tot; S6["water"] = S5["water"] - w_hyd
    S7 = mk(co2=CO2)
    S8 = dict(S6); S8["glucose"] = G_tot - G_ferm; S8["ethanol"] = E8
    S14 = {c: S8[c] - S9[c] for c in COMPS}
    # decanter
    liq = S14["water"] + S14["ethanol"]; er = S14["ethanol"] / liq
    sol_names = ["glucose", "solids"]; DS = sum(S14[c] for c in sol_names)
    cake_solids = a["cap"] * DS; cake_tot = cake_solids / a["cake"]; cake_liq = cake_tot - cake_solids
    S15 = mk(glucose=a["cap"] * S14["glucose"], solids=a["cap"] * S14["solids"], water=cake_liq * (1 - er), ethanol=cake_liq * er)
    S16 = {c: S14[c] - S15[c] for c in COMPS}
    # evaporator: all ethanol and surplus water leave as condensate
    syr_solids = sum(S16[c] for c in sol_names); syr_tot = syr_solids / a["syrup"]
    S17 = mk(glucose=S16["glucose"], solids=S16["solids"], water=syr_tot - syr_solids)
    S18 = {c: S16[c] - S17[c] for c in COMPS}
    # dryer
    feed = {c: S15[c] + S17[c] for c in COMPS}; ds_all = feed["glucose"] + feed["solids"]
    ddgs_tot = ds_all / (1 - a["ddgs_moist"])
    S19 = mk(glucose=feed["glucose"], solids=feed["solids"], water=ddgs_tot - ds_all)
    S20 = {c: feed[c] - S19[c] for c in COMPS}
    S = {1: S1, 2: S2, 3: S3, 4: S4, 5: S5, 6: S6, 7: S7, 8: S8, 9: S9, 10: S10, 11: S11, 12: S12, 13: S13, 14: S14, 15: S15, 16: S16, 17: S17, 18: S18, 19: S19, 20: S20}
    r.update(S=S, P=P, E8=E8, G_tot=G_tot, G_ferm=G_ferm, CO2=CO2, starch=starch, grain=grain, w_hyd=w_hyd, Rg=Rg, DS=DS, feed=feed)
    # ---- closure
    inn = tot(S1) + tot(S3)
    out = tot(S7) + tot(S11) + tot(S13) + tot(S18) + tot(S19) + tot(S20)
    r["in"], r["out"] = inn, out; r["err"] = (out - inn) / inn * 100
    assert abs(r["err"]) < 0.1, r["err"]
    # unit-level closure
    def chk(name, i, o):
        e = (sum(map(tot, o)) - sum(map(tot, i))) / sum(map(tot, i)) * 100
        assert abs(e) < 0.1, (name, e); return e
    r["units"] = {"V-103 sacch.": chk("sacch", [S5], [S6]), "F-101 ferm.": chk("ferm", [S6], [S7, S8]), "C-101 beer col.": chk("c101", [S8], [S9, S14]),
                  "C-102 rectifier": chk("c102", [S9, S12], [S10, S13]), "MS-101 sieve": chk("ms", [S10], [S11, S12]),
                  "DC-101 decanter": chk("dc", [S14], [S15, S16]), "EV-101 evap.": chk("ev", [S16], [S17, S18]), "D-101 dryer": chk("dry", [S15, S17], [S19, S20])}
    # carbon check across hydrolysis + fermentation: C in starch (as C6H10O5) = C in glucose residual + ethanol + CO2   (D)
    nC = lambda mass, M, nc: mass / M * nc
    C_in = nC(starch, M_ANH, 6)
    C_out = nC(S8["glucose"], M_GLU, 6) + nC(S8["ethanol"], M_ETOH, 2) + nC(S7["co2"], M_CO2, 1)
    r["C_in"], r["C_out"] = C_in, C_out; r["C_err"] = (C_out - C_in) / C_in * 100; assert abs(r["C_err"]) < 0.1
    def elm(mass, M, nC, nH, nO): return (mass / M * nC * MC, mass / M * nH * MH, mass / M * nO * MO)
    e_in = [x + y for x, y in zip(elm(starch, M_ANH, 6, 10, 5), elm(w_hyd, M_H2O, 0, 2, 1))]
    e_out = [x + y + z for x, y, z in zip(elm(S8["glucose"], M_GLU, 6, 12, 6), elm(S8["ethanol"], M_ETOH, 2, 6, 1), elm(S7["co2"], M_CO2, 1, 0, 2))]
    r["elem"] = {k: (i, o, (o - i) / i * 100) for k, i, o in zip("CHO", e_in, e_out)}
    for k in "CHO": assert abs(r["elem"][k][2]) < 0.1, (k, r["elem"][k])
    r["L_h"] = P / a["rho_prod"] * 1000
    r["ddgs_split"] = dict(nonferm=S19["solids"] / r["L_h"], residual=S19["glucose"] / r["L_h"], moisture=S19["water"] / r["L_h"])
    # O and H over the fermenter (S6 glucose + water fixed): O atoms: glucose 6, ethanol 1, CO2 2 ; mol check ethanol = CO2
    assert abs(S8["ethanol"] / M_ETOH - S7["co2"] / M_CO2) < 1e-6 * S7["co2"]
    # ---- cross-checks against the template (informational)
    r["grain_t_yr"] = grain * HOURS / 1000; r["ddgs_t_yr"] = tot(S19) * HOURS / 1000
    r["prod_kl_yr"] = P / a["rho_prod"] * HOURS
    # ---- duties, kW (1 kW = 3600 kJ/h); negative = removed
    kW = lambda kj_h: kj_h / 3600.0
    D = {}
    D["H-101 slurry heater"] = kW(tot(S4) * a["cp"] * (T_["s5"] - T_["s4"]))
    D["H-102 mash cooler 1"] = -kW(tot(S5) * a["cp"] * (T_["s5"] - 60))
    D["H-103 mash cooler 2"] = -kW(tot(S5) * a["cp"] * (60 - T_["s6"]))
    D["F-101 fermentation cooling"] = -kW(r["G_ferm"] / M_GLU * 1000 * a["dh_ferm"])
    D["E-101 beer preheater (hot stillage)"] = kW(tot(S8) * a["cp"] * (T_PRE - T_["s8"]))
    # stillage outlet temperature from E-101 hot side (D)
    t_out = T_["s14"] - D["E-101 beer preheater (hot stillage)"] * 3600 / (tot(S14) * a["cp"])
    r["t_stillage_out"] = t_out; assert t_out > 30
    lam_mix = lambda x: x * a["lam_e"] + (1 - x) * a["lam_w"]
    D["E-102 beer column reboiler"] = kW(tot(S9) * lam_mix(a["x_s9"]) + tot(S8) * a["cp"] * (T_["s14"] - T_PRE))
    qc = a["RR_rect"] * tot(S10) * lam_mix(a["x_hyd"])
    D["E-103 rectifier condenser"] = -kW(qc)
    D["E-106 rectifier reboiler"] = kW(qc - tot(S13) * a["lam_w"])          # feed enters as saturated vapour; lees leaves as liquid
    D["E-104 product cooler"] = -kW(tot(S11) * (a["lam_e"] + a["cp_et"] * (T_["s10"] - T_["s11"])))
    ev_w = tot(S16) - tot(S17)
    D["EV-101 evaporator (steam)"] = kW(ev_w / a["econ"] * a["lam_st"])      # econ = kg evaporated per kg LP steam (A), so steam mass = ev_w/econ, at lam_st
    D["E-105 evap. last-effect condenser"] = -kW(ev_w * a["lam_w"] / a["n_eff"])   # last effect evaporates 1/n_eff of the total (A: equal split)
    D["D-101 dryer (steam/hot air)"] = kW(tot(S20) * a["lam_w"] / a["eta_dry"])
    steam_kW = sum(D[k] for k in ["H-101 slurry heater", "E-102 beer column reboiler", "E-106 rectifier reboiler", "EV-101 evaporator (steam)", "D-101 dryer (steam/hot air)"])
    r["steam_kW"] = steam_kW; r["steam_t_h"] = steam_kW * 3600 / a["lam_st"] / 1000
    r["duty"] = D
    r["steam_kg_per_L"] = steam_kW * 3600 / a["lam_st"] / (P / a["rho_prod"] * 1000)
    return r



# =====================================================================================================================
# drawing helpers
# =====================================================================================================================
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pidlib import *

class SheetB(Sheet):
    def svg(self):
        return super().svg().replace("|  Rev A<", "|  Rev B<").replace("Draft A. Screening", "Draft B. Screening")


STEAM = "#6a1b9a"; CW = "#0277bd"


def lab(s, x, y, t, size=10, w=400, anchor="start", fill=INK): T(s, x, y, t, size, w, anchor, fill)


def inst(s, x, y, a, b, panel=True, color=INK): bubble(s, x, y, a, b, panel, color)


def sig(s, pts): PL(s, pts, 1.2, BLUE, "5 4")


def esdl(s, pts): PL(s, pts, 1.7, RED, "6 4")


def line(s, pts, color=INK, sw=2.6, arr=None):
    PL(s, pts, sw, color)
    if arr:
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        arrow(s, xb, yb, arr, color, 8 if color == INK else 7)


def utility_in(s, x, y, d, text, color, ln=26, tx=None, ty=None, anchor="middle"):
    """utility stub arriving at (x,y); d = direction of travel (r l u d)"""
    dx, dy = {"r": (-ln, 0), "l": (ln, 0), "d": (0, -ln), "u": (0, ln)}[d]
    line(s, [(x + dx, y + dy), (x, y)], color, 1.8, d)
    lab(s, tx if tx is not None else x + dx, ty if ty is not None else y + dy - 5, text, 9.5, 700, anchor, color)


def ctl_valve(s, x, y, tag, color=INK, rot=0, tag_dx=0, tag_dy=0, anchor="middle", act=True):
    valve(s, x, y, rot, "gate", act=act, color=color)
    lab(s, x + tag_dx, y + tag_dy, tag, 9.5, 700, anchor, color)


def sieve_bed(s, cx, top, w, h):
    vvessel(s, cx, top, w, h, None, None)
    s.add(f'<rect x="{cx-w/2+3}" y="{top+h*0.12}" width="{w-6}" height="{h*0.76}" fill="url(#hatch)" opacity=".55"/>')


def gd(s, x, y, tag, color=RED):
    """gas detector: square with a G, tag beneath"""
    R(s, x - 9, y - 9, 18, 18, "#fff", color, 1.8)
    lab(s, x, y + 4, "G", 11, 700, "middle", color)
    if tag: lab(s, x, y + 21, tag, 9.5, 700, "middle", color)


def fd(s, x, y, tag, color=RED):
    s.add(f'<polygon points="{x},{y-11} {x+10},{y+8} {x-10},{y+8}" fill="#fff" stroke="{color}" stroke-width="1.8"/>')
    lab(s, x, y + 6, "F", 9.5, 700, "middle", color)
    if tag: lab(s, x, y + 20, tag, 9.5, 700, "middle", color)


def tagged(s, x, y, tag, color=RED, anchor="start"): lab(s, x, y, tag, 9.5, 700, anchor, color)


# =====================================================================================================================
# sheet 1 drawing: the conceptual P&ID (also redrawn, dimmed, under each scenario sheet)
# =====================================================================================================================
def pid(s):
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    PL(s, [(20, 336), (1120, 336)], 0.8, "#aab", "6 4"); PL(s, [(20, 582), (1120, 582)], 0.8, "#aab", "6 4")
    lab(s, 28, 100, "A  GRAIN HANDLING, MASHING, FERMENTATION", 10.5, 700, fill="#1a237e")
    lab(s, 28, 350, "B  DISTILLATION, DEHYDRATION, PRODUCT STORAGE", 10.5, 700, fill="#1a237e")
    lab(s, 28, 598, "C  STILLAGE PROCESSING, DDGS, UTILITIES", 10.5, 700, fill="#1a237e")
    # ---------------- band A ----------------
    R(s, 40, 112, 48, 58, "#fff", INK, 2.2); PL(s, [(40, 170), (58, 192), (70, 192), (88, 170)], 2.2)
    lab(s, 64, 136, "SL-101", 10.5, 700, "middle"); lab(s, 64, 149, "grain silo", 9.5, 400, "middle")
    line(s, [(64, 192), (64, 222)], arr="d"); strm(s, 64, 206, 1)
    s.add(f'<circle cx="64" cy="240" r="18" fill="#fff" stroke="{INK}" stroke-width="2"/>'); lab(s, 64, 244, "M", 10, 700, "middle")
    lab(s, 64, 274, "ML-101", 10.5, 700, "middle"); lab(s, 64, 287, "hammer mill", 9.5, 400, "middle")
    line(s, [(82, 240), (155, 240)], arr="r"); strm(s, 118, 240, 2)
    reactor(s, 185, 240, 60, 64)
    lab(s, 185, 306, "V-101 slurry tank", 10.5, 700, "middle")
    lab(s, 214, 117, "process water (PW)", 9.5, 700, "start", CW)
    line(s, [(205, 108), (205, 193)], CW, 2.2, "d"); strm(s, 205, 172, 3, CW)
    valve(s, 205, 138, 90, "gate", act=True, color=CW); lab(s, 193, 141, "FV-101", 9.5, 700, "end", CW)
    inst(s, 250, 150, "FFIC", "101"); sig(s, [(235, 150), (228, 143), (221, 138)])
    line(s, [(215, 262), (242, 262)], arr=None); strm(s, 228, 262, 4)
    pump(s, 255, 262, 13, "P-101")
    line(s, [(268, 249), (290, 249)], arr="r")
    hx(s, 325, 249, 70, 28)
    lab(s, 325, 281, "H-101 slurry heater", 10, 700, "middle") if False else None
    lab(s, 325, 278, "H-101", 10, 700, "middle"); lab(s, 325, 289, "slurry heater", 9.5, 400, "middle")
    line(s, [(325, 192), (325, 235)], STEAM, 1.8, "d"); lab(s, 325, 187, "LP steam", 9.5, 700, "middle", STEAM)
    valve(s, 325, 210, 90, "gate", act=True, color=STEAM); lab(s, 310, 214, "TV-101", 9.5, 700, "end", STEAM)
    line(s, [(360, 249), (380, 249)], arr="r")
    reactor(s, 410, 240, 60, 64)
    lab(s, 410, 306, "V-102 liquefaction", 10.5, 700, "middle")
    inst(s, 372, 168, "TIC", "101"); sig(s, [(372, 183), (372, 232), (380, 232)]); sig(s, [(357, 168), (340, 168), (340, 205)])
    line(s, [(440, 249), (470, 249)], arr="r"); strm(s, 455, 249, 5)
    hx(s, 500, 249, 60, 26); lab(s, 500, 278, "H-102 mash cooler", 9.5, 700, "middle"); lab(s, 500, 289, "(CW, A)", 9.5, 400, "middle")
    line(s, [(530, 249), (547, 249)], arr="r")
    reactor(s, 575, 240, 56, 64)
    lab(s, 575, 306, "V-103 saccharification", 10.5, 700, "middle")
    line(s, [(603, 249), (620, 249)], arr="r")
    hx(s, 650, 249, 60, 26); lab(s, 650, 278, "H-103 mash cooler", 9.5, 700, "middle"); lab(s, 650, 289, "(CW, A)", 9.5, 400, "middle")
    line(s, [(680, 249), (735, 249)], arr="r"); strm(s, 688, 249, 6)
    # fermenter, typical of n units
    R(s, 722, 150, 108, 168, "none", "#889", 1, "5 4")
    lab(s, 826, 313, "typical of n units (A)", 9.5, 400, "end", GREY)
    reactor(s, 775, 240, 70, 76, jacket=True)
    lab(s, 770, 308, "F-101A", 10.5, 700, "end")
    line(s, [(799, 201), (905, 201)], arr="r"); strm(s, 855, 201, 7)
    line(s, [(822, 201), (822, 188)], 1.8) if False else None
    # PVRV-201 on the CO2 line
    line(s, [(830, 201), (830, 192)], INK, 1.8); psv(s, 830, 176)
    line(s, [(848, 166), (880, 166), (880, 118), (930, 118)], INK, 1.8); lab(s, 836, 148, "PVRV-201", 9.5, 700, "start"); lab(s, 836, 138, "(R/A: A)", 9.5, 400, "start") if False else None
    vvessel(s, 930, 150, 50, 96, None, None, packing=True)
    lab(s, 962, 232, "SC-101", 10.5, 700, "start"); lab(s, 962, 244, "CO2 scrubber", 9.5, 400, "start")
    utility_in(s, 955, 172, "l", "scrub water", CW, 30, tx=988, ty=176, anchor="start")
    line(s, [(930, 136), (930, 100)], INK, 2.6, "u"); lab(s, 937, 108, "CO2 vent to safe location (A)", 9.5, 700, "start")
    line(s, [(930, 262), (930, 326)], INK, 2.6, "d")
    utility_in(s, 742, 200, "d", "", INK, 24); lab(s, 736, 180, "antifoam AF-201", 9.5, 700, "end")
    inst(s, 700, 205, "LSH", "201", False)
    # fermenter CW jacket loop
    line(s, [(866, 282), (848, 282)], CW, 1.8); line(s, [(836, 282), (815, 282)], CW, 1.8)
    valve(s, 842, 282, 0, "gate", act=True, color=CW); lab(s, 842, 308, "TV-201", 9.5, 700, "middle", CW); lab(s, 870, 286, "CW", 9.5, 700, "start", CW)
    inst(s, 852, 238, "TIC", "201"); sig(s, [(837, 243), (812, 243)]); sig(s, [(852, 253), (842, 271)])
    line(s, [(775, 291), (775, 326)], arr=None)
    line(s, [(930, 326), (110, 326)], arr=None); arrow(s, 600, 326, "l"); arrow(s, 300, 326, "l"); strm(s, 700, 326, 8)
        # ---------------- band B ----------------
    hvessel(s, 110, 424, 100, 52, None, None)
    lab(s, 110, 422, "V-104", 10.5, 700, "middle"); lab(s, 110, 435, "beer well", 9.5, 400, "middle")
    line(s, [(110, 326), (110, 398)], arr="d")
    inst(s, 58, 380, "LIC", "301"); sig(s, [(70, 391), (82, 402)])
    line(s, [(160, 424), (190, 424)], arr=None)
    pump(s, 205, 424, 13, "P-102")
    line(s, [(218, 411), (240, 411)], arr="r")
    hx(s, 275, 411, 70, 28)
    lab(s, 275, 441, "E-101 preheater", 9.5, 700, "middle"); lab(s, 275, 452, "(hot stillage S14, A)", 9.5, 400, "middle")
    line(s, [(310, 411), (367, 411)], arr="r")
    valve(s, 338, 411, 0, "gate", act=True); lab(s, 338, 432, "FV-301", 9.5, 700, "middle")
    inst(s, 322, 372, "FIC", "301"); sig(s, [(333, 384), (338, 395)]); sig(s, [(74, 372), (306, 372)])
    vvessel(s, 395, 382, 56, 140, None, None, trays=8)
    lab(s, 428, 508, "C-101", 10.5, 700, "start"); lab(s, 428, 520, "beer column", 9.5, 400, "start")
    # C-101 reboiler (left)
    line(s, [(395, 540), (395, 556), (330, 556)], arr=None)
    hx(s, 300, 556, 60, 26)
    lab(s, 234, 560, "E-102 reboiler", 9.5, 700, "end")
    line(s, [(270, 556), (240, 556), (240, 470), (367, 470)], arr="r")
    line(s, [(300, 508), (300, 543)], STEAM, 1.8, "d"); lab(s, 318, 482, "LP steam", 9.5, 700, "start", STEAM)
    valve(s, 300, 524, 90, "gate", act=True, color=STEAM); lab(s, 286, 520, "TV-302", 9.5, 700, "end", STEAM)
    inst(s, 340, 520, "TIC", "302"); sig(s, [(355, 520), (367, 520)]); sig(s, [(325, 520), (316, 524)])
    # overhead S9
    line(s, [(395, 366), (395, 352), (490, 352), (490, 440), (517, 440)], arr="r"); strm(s, 440, 352, 9)
    # PSV-301
    line(s, [(423, 408), (445, 408)], INK, 1.8); psv(s, 445, 392)
    line(s, [(463, 382), (482, 382)], INK, 1.8, "r"); lab(s, 428, 426, "PSV-301", 9.5, 700, "start"); lab(s, 428, 437, "to VH-101 (A)", 9.5, 400, "start")
    # rectifier
    vvessel(s, 545, 382, 56, 140, None, None, trays=10)
    lab(s, 528, 572, "C-102 rectifier", 10, 700, "end")
    line(s, [(545, 540), (545, 556), (600, 556)], arr=None)
    hx(s, 625, 556, 50, 26)
    lab(s, 668, 560, "E-106 reboiler", 9.5, 700, "start")
    line(s, [(650, 556), (662, 556), (662, 500), (573, 500)], arr="l")
    line(s, [(625, 512), (625, 543)], STEAM, 1.8, "d"); valve(s, 625, 528, 90, "gate", act=True, color=STEAM)
    lab(s, 640, 544, "TV-303", 9.5, 700, "start", STEAM); lab(s, 705, 538, "LP steam", 9.5, 700, "middle", STEAM)
    inst(s, 598, 528, "TIC", "303"); sig(s, [(598, 513), (590, 507), (573, 507)]) if False else None; sig(s, [(583, 528), (573, 528)]); sig(s, [(613, 528), (617, 528)]) if False else None
    line(s, [(545, 556), (545, 576)], arr=None); strm(s, 545, 567, 13)
    # overhead S10, condenser, reflux, PSV-302
    line(s, [(545, 366), (545, 358), (580, 358)], arr=None)
    hx(s, 610, 358, 60, 26)
    lab(s, 610, 338, "E-103 condenser", 9.5, 700, "middle")
    line(s, [(640, 358), (745, 358), (745, 376)], arr=None); strm(s, 678, 358, 10)
    line(s, [(592, 371), (592, 391), (573, 391)], arr="l"); lab(s, 586, 404, "reflux (FIC-303)", 9.5, 700, "start") if False else None
    lab(s, 597, 388, "reflux", 9.5, 700, "start")
    line(s, [(628, 371), (628, 384)], CW, 1.8, "d"); lab(s, 634, 385, "CW", 9.5, 700, "start", CW)
    line(s, [(573, 440), (606, 440)], INK, 1.8); psv(s, 606, 424)
    line(s, [(624, 414), (650, 414)], INK, 1.8, "r"); lab(s, 656, 416, "PSV-302", 9.5, 700, "start"); lab(s, 656, 427, "to VH-101 (A)", 9.5, 400, "start")
    # MS beds
    sieve_bed(s, 745, 390, 44, 100); sieve_bed(s, 815, 390, 44, 100)
    line(s, [(745, 358), (815, 358), (815, 376)], arr=None)
    valve(s, 745, 368, 90, "gate", act=False); valve(s, 815, 368, 90, "gate", act=False)
    lab(s, 745, 546, "MS-101A", 10, 700, "middle"); lab(s, 815, 546, "MS-101B", 10, 700, "middle")
    line(s, [(745, 502), (745, 518), (843, 518)], arr=None); line(s, [(815, 502), (815, 518)], arr=None)
    line(s, [(723, 470), (573, 470)], "#444", 2.2, "l"); strm(s, 640, 470, 12); lab(s, 640, 488, "regen A/B", 9.5, 400, "middle")
    # product cooler, tanks
    hx(s, 872, 518, 58, 26); lab(s, 872, 502, "E-104 cooler", 9.5, 700, "middle")
    strm(s, 834, 518, 11)
    lab(s, 872, 558, "CW", 9.5, 700, "middle", CW)
    line(s, [(901, 518), (932, 518)], arr="r")
    inst(s, 872, 478, "AT", "401", False)
    tank(s, 957, 548, 50, 66, None, None, "cone", 0.5)
    lab(s, 950, 424, "T-101 day tank", 10.5, 700, "end")
    line(s, [(957, 548), (957, 564), (978, 564)], arr=None)
    pump(s, 991, 564, 13, "P-103")
    line(s, [(1004, 551), (1030, 551)], arr="r")
    tank(s, 1070, 556, 80, 80, None, None, "cone", 0.7)
    lab(s, 1030, 458, "T-201A/B", 10.5, 700, "middle")
    inst(s, 1004, 504, "LIC", "401"); sig(s, [(1019, 504), (1030, 504)])
    line(s, [(1096, 556), (1096, 590)], arr="d"); lab(s, 1110, 603, "to loading (A)", 9.5, 700, "end")
    valve(s, 1096, 566, 90, "gate", act=True, color=RED); lab(s, 1090, 570, "XV-401", 9.5, 700, "end", RED)
    valve(s, 957, 556, 0, "gate", act=True, color=RED) if False else None
    line(s, [(1090, 470), (1090, 441)], INK, 1.8); s.add(f'<circle cx="1090" cy="434" r="7" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    line(s, [(1090, 427), (1090, 412)], INK, 1.8, "u"); lab(s, 1082, 431, "PVRV-401 + FA (A)", 9.5, 700, "end")
    # ESD panel, gas / flame detection, isolation valves (all A)
    R(s, 875, 344, 235, 40, "#fff3f3", RED, 1.4)
    lab(s, 880, 356, "ESD-1 (A): GD high-high / FD / manual ->", 9.5, 700, "start", RED)
    lab(s, 880, 367, "close XV-401/402/404, XV-301A/B; trip", 9.5, 400, "start", RED); lab(s, 880, 378, "P-102 / P-103 (fire: start FW-401, FC-401)", 9.5, 400, "start", RED)
    esdl(s, [(1110, 384), (1114, 384), (1114, 566), (1103, 566)])
    valve(s, 957, 557, 90, "gate", act=True, color=RED); lab(s, 946, 560, "XV-402", 9.5, 700, "end", RED)
    gd(s, 880, 590, "GD-402") if False else None
    # ---------------- band C ----------------
    hvessel(s, 130, 670, 110, 44, None, None)
    lab(s, 130, 668, "DC-101", 10.5, 700, "middle"); lab(s, 130, 681, "decanter", 9.5, 400, "middle")
    line(s, [(395, 540), (395, 574), (130, 574), (130, 646)], arr="d"); strm(s, 300, 574, 14)
    valve(s, 395, 556, 90, "gate", act=True) if False else None
    line(s, [(130, 699), (130, 760)], arr=None); strm(s, 130, 738, 15)
    line(s, [(130, 760), (500, 760), (500, 690), (540, 690)], arr="r"); lab(s, 420, 754, "wet cake S15 + syrup S17 to dryer", 9.5, 700, "start")
    
    line(s, [(185, 670), (215, 670)], arr=None)
    pump(s, 230, 670, 13, "P-104")
    line(s, [(243, 657), (320, 657)], arr="r"); strm(s, 283, 657, 16)
    vvessel(s, 350, 625, 60, 80, None, None)
    lab(s, 384, 692, "EV-101 evaporator", 10, 700, "start"); lab(s, 384, 704, "(3 effects, A)", 9.5, 400, "start")
    line(s, [(410, 640), (380, 640)], STEAM, 1.8, "l"); lab(s, 414, 644, "LP steam", 9.5, 700, "start", STEAM)
    line(s, [(350, 608), (350, 598), (410, 598)], arr=None)
    hx(s, 440, 598, 60, 22)
    lab(s, 440, 625, "E-105 condenser (CW)", 9.5, 700, "middle")
    line(s, [(470, 598), (508, 598)], arr="r"); strm(s, 490, 598, 18); lab(s, 514, 602, "S18 to ETP", 9.5, 700, "start")
    line(s, [(350, 722), (350, 760)], arr=None); strm(s, 350, 744, 17)
    # dryer
    hvessel(s, 650, 680, 170, 60, None, None)
    lab(s, 650, 678, "D-101 DDGS dryer", 11, 700, "middle"); lab(s, 650, 692, "(rotary, steam tube, A)", 9.5, 400, "middle")
    line(s, [(610, 626), (610, 650)], STEAM, 1.8, "d"); lab(s, 610, 620, "LP steam", 9.5, 700, "middle", STEAM)
    line(s, [(710, 650), (710, 626), (745, 626)], arr="r"); strm(s, 710, 640, 20)
    s.add(f'<polygon points="745,606 785,606 775,640 765,660 755,640" fill="#fff" stroke="{INK}" stroke-width="2"/>'); lab(s, 744, 600, "CY-101", 9.5, 700, "end")
    line(s, [(765, 606), (765, 592), (855, 592), (855, 606)], arr="d")
    R(s, 832, 606, 46, 42, "#fff", INK, 2); lab(s, 855, 625, "BF-101", 9.5, 700, "middle"); lab(s, 855, 637, "bag filter", 9.5, 400, "middle")
    line(s, [(878, 632), (915, 632)], arr="r"); lab(s, 920, 636, "S20 to stack (A)", 9.5, 700, "start")
    inst(s, 700, 612, "TIC", "501"); sig(s, [(700, 627), (700, 645)]) if False else None
    line(s, [(650, 710), (650, 742), (720, 742)], arr="r"); strm(s, 650, 728, 19)
    R(s, 720, 724, 56, 38, "#fff", INK, 2); lab(s, 748, 739, "SI-501", 10, 700, "middle"); lab(s, 748, 752, "DDGS silo", 9.5, 400, "middle")
    # utilities row
    gd(s, 1030, 640, "GD-401"); fd(s, 1075, 640, "FD-401"); gd(s, 905, 566, "GD-402")
    R(s, 800, 696, 90, 64, "#fff", INK, 1.6); lab(s, 845, 712, "B-101", 10.5, 700, "middle"); lab(s, 845, 725, "steam boiler", 9.5, 400, "middle"); lab(s, 845, 738, "(fuel TBD, A)", 9.5, 400, "middle")
    line(s, [(845, 696), (845, 672)], STEAM, 1.8, "u"); lab(s, 840, 691, "LP steam to all users", 9.5, 700, "end", STEAM)
    R(s, 910, 696, 90, 64, "#fff", INK, 1.6); lab(s, 955, 712, "CT-101", 10.5, 700, "middle"); lab(s, 955, 725, "cooling tower", 9.5, 400, "middle"); lab(s, 955, 738, "(CW header)", 9.5, 400, "middle")
    line(s, [(955, 696), (955, 672)], CW, 1.8, "u"); lab(s, 955, 664, "CW to users", 9.5, 700, "middle", CW)
    R(s, 1010, 696, 100, 64, "#fff", INK, 1.6); lab(s, 1060, 712, "ETP / ZLD", 10.5, 700, "middle"); lab(s, 1060, 725, "S13, S18, blowdown", 9.5, 400, "middle"); lab(s, 1060, 738, "(not detailed, A)", 9.5, 400, "middle")
    safety_devices(s)


# =====================================================================================================================
# generic sheet helpers
# =====================================================================================================================
def wtable(s, x, y, colw, rows, size=9.5, lh=11.5, pad=4, head=True, hfill="#e8eaf0"):
    """table with wrapped cells; returns y below. rows[0] is the header when head."""
    yy = y
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), width=max(4, int((colw[j] - 2 * pad) / (size * 0.54)))) or [""] for j, c in enumerate(r)]
        h = max(len(c) for c in cells) * lh + 2 * pad - 2
        if head and i == 0: R(s, x, yy, sum(colw), h, hfill, "none")
        elif i % 2 == 0: R(s, x, yy, sum(colw), h, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, t in enumerate(c): T(s, cx + pad, yy + pad + 8 + k * lh, t, size, 700 if (head and i == 0) or j == 0 else 400)
            cx += colw[j]
        yy += h
    R(s, x, y, sum(colw), yy - y, "none", "#9aa", 1)
    cx = x
    for w in colw[:-1]:
        cx += w; PL(s, [(cx, y), (cx, yy)], 0.5, "#ccd")
    return yy


def f0(v): return f"{v:,.0f}"


def pct(v, tot_):
    p = 100 * v / tot_ if tot_ else 0
    return "-" if v == 0 else ("<0.01" if p < 0.005 else (f"{p:.2f}" if p < 0.1 else f"{p:.1f}"))


def note_lines(s, x, y, lines, width, size=10, lh=13.5, bullet=True, fill=INK):
    for t in lines: y = WRAP(s, x, y, t, width, size, lh, fill, 400, bullet) + 2
    return y


def cloud(s, cx, cy, rx, ry, fill="#ef9a9a", op=0.45, stroke=RED):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" opacity="{op}" stroke="{stroke}" stroke-width="1.6" stroke-dasharray="7 4"/>')


def snum(s, x, y, n, color=RED):
    s.add(f'<circle cx="{x}" cy="{y}" r="11" fill="{color}"/>'); T(s, x, y + 4.5, str(n), 12, 700, "middle", "#fff")


def dim_pid(s):
    n = len(s.p); pid(s); body = s.p[n:]; del s.p[n:]
    s.add('<g opacity="0.26">' + "".join(body) + "</g>")


def legend_eth(s, x, y):
    items = [("process line", INK, None), ("LP steam (utility)", STEAM, None), ("cooling water", CW, None), ("ESD / trip output", RED, "6 4"), ("instrument signal", BLUE, "5 4")]
    for i, (t, c, d) in enumerate(items):
        PL(s, [(x, y + i * 14), (x + 30, y + i * 14)], 2 if c in (INK, STEAM, CW) else 1.4, c, d); T(s, x + 36, y + 4 + i * 14, t, 9.5)
    s.add(f'<rect x="{x+160}" y="{y-6}" width="30" height="10" fill="url(#hatch)"/>'); T(s, x + 196, y + 4, "adsorbent / packing", 9.5)
    strm(s, x + 175, y + 20, "n"); T(s, x + 196, y + 24, "stream no. = HMB column (sheet 2)", 9.5)
    T(s, x + 160, y + 42, "R = recommended by a source", 9.5); T(s, x + 160, y + 55, "A = assumed by this drawing", 9.5)
    T(s, x + 160, y + 68, "(R items: sheets 5 to 9; sizes of all", 9.5); T(s, x + 160, y + 80, "drawn devices are A unless sheet 6)", 9.5)
    gd(s, x + 8, y + 88, "gas"); fd(s, x + 52, y + 88, "flame")
    T(s, x + 160, y + 100, "Line no. L-nnn size-service-class: size, class A.", 9.5)


def hdr_sheet(no, title, sub):
    return SheetB(no, title, sub, code="VS-ETH", project="Grain ethanol (1G) distillery, 100 KLPD",
                 basis="DPR template 100 KLPD + stoichiometry, 11 Nov 2026")


TOTAL = 9


# =====================================================================================================================
# sheet 1: P&ID
# =====================================================================================================================
def line_numbers(s):
    for x, y, t, a in [(330, 320, "L-201 A-BEER-A", "start"), (453, 346, "L-301 A-EW-A", "start"), (690, 350, "L-302 A-EV-A", "start"),
                       (776, 530, "L-303", "start"), (60, 567, "L-401 A-STIL-A", "start"), (150, 754, "L-402 A-CAKE-A", "start")]:
        lab(s, x, y, t, 9.5, 400, a, GREY)


def sheet1(r):
    S = r["S"]
    s = hdr_sheet(1, "Conceptual P&ID: grain ethanol, milling to DDGS, 100 KLPD", f"1 of {TOTAL}: P&ID, base case, all numbered streams, Rev B devices")
    pid(s); line_numbers(s)
    # right panel
    panel_box(s)
    y = section(s, 1135, 84, 445, "Legend and conventions")
    legend_eth(s, 1150, y + 16)
    y = 84 + 22 + 16 + 136
    y = section(s, 1135, y, 445, "Process (template section 4, S)")
    y = WRAP(s, 1146, y + 16, "Milling, liquefaction, saccharification and fermentation of maize or rice, distillation and dehydration to fuel-grade ethanol, "
             "DDGS recovery, and a zero-liquid-discharge effluent system (Template_DPR_Ethanol_Grain_100KLPD.docx, section 4). Equipment groups follow the "
             "template cost table (section 7). Unit sizes, temperatures and pressures are not in the template: see sheet 2 for the A list.", 70, 10.5, 13.5)
    y = section(s, 1135, y + 6, 445, "Main control loops, relief and isolation (all A)")
    y = note_lines(s, 1146, y + 16, [
        "Flow: FFIC-101 water to grain ratio; FIC-301 beer feed, cascade from LIC-301 beer well level.",
        "Temperature: TIC-101 liquefaction (steam TV-101); TIC-201 fermenter jacket (CW TV-201); TIC-302 and TIC-303 column tray temperature to reboiler steam.",
        "Level: LIC-301 beer well; LIC-401 with independent LAHH-401 (T-201A/B) and LAHH-402 (T-101); LSH-201 foam alarm dosing antifoam, LSHH-201 closes XV-201.",
        "Quality: AT-401 water in product with off-spec diversion (diverter valve not drawn, open item).",
        "Relief (sheet 5): PSV-301/302/303 columns and sieve beds, PSV-401 evaporator, PSV-501 steam header, PVRV-201 fermenters, PVRV-402 and PVRV-401 + EVH-401 tanks, TSV-101..103, XP-101..503 dust vents. Vents go to VH-101 / ST-101 (height open, A).",
        "Gas / flame: GD-201 (CO2), GD-301/302/401/402 flammable gas, FD-401 flame; ESD-1 closes XV-401/402/404 and XV-301A/B, trips P-102 / P-103 (matrix, SIFs: sheet 7).",
        "Dryer: TIC-501, TAHH-501, SD-501, XV-501, RV-501, XP-501/502/503, DL-501 (sheet 4)."], 71, 10, 13)
    y = section(s, 1135, y + 6, 445, "Hazards that drive the safeguards (qualitative)")
    y = note_lines(s, 1146, y + 16, [
        "Ethanol, hydrous and anhydrous, is a flammable liquid handled hot in C-101, C-102, MS-101 and E-104, and stored in T-101 and T-201A/B (sheet 3 scenario 1, sheet 4 scenario 3).",
        f"Fermentation makes CO2: {f0(tot(S[7]))} kg/h at design rate (D); asphyxiation and foam / overpressure hazard (sheet 3 scenario 2).",
        "Dried DDGS and the dryer exhaust carry combustible dust (sheet 4 scenario 4)."], 71, 10, 13)
    y = section(s, 1135, y + 6, 445, "Open items for the licensor (not set here)")
    note_lines(s, 1146, y + 16, ["Vessel volumes, number of fermenters, column pressures and tray counts.", "Vent and relief destinations, relief sizing, area classification.",
                                 "Enzyme / yeast / chemical dosing, CIP, DDGS cooling and bagging, backset recycle, fuel for B-101.", "Line sizes, piping class, instrument types and set points."], 71, 10, 13)
    # bottom strip: equipment list
    D = r["duty"]
    kw = lambda k: f"{D[k]:+,.0f} kW"
    rows1 = [("Tag", "Service", "Basis from sheet 2 (D unless A)"),
             ("SL-101", "Grain silo and feed to mill", f"S1 {f0(tot(S[1]))} kg/h"),
             ("ML-101", "Hammer mill (dust extraction A)", "S1 to S2, same mass"),
             ("V-101 / P-101", "Slurry tank, slurry pump", f"S4 {f0(tot(S[4]))} kg/h"),
             ("H-101", "Slurry heater (LP steam)", kw("H-101 slurry heater")),
             ("V-102", "Liquefaction tank (85 C A)", "S5, enzyme dosing not drawn"),
             ("H-102 / H-103", "Mash coolers (CW)", f"{D['H-102 mash cooler 1']:+,.0f} / {D['H-103 mash cooler 2']:+,.0f} kW"),
             ("V-103", "Saccharification tank (60 C A)", f"hydrolysis water {f0(r['w_hyd'])} kg/h"),
             ("F-101A..n", "Fermenters, number set by licensor", f"{kw('F-101 fermentation cooling')} total (A heat of reaction)"),
             ("SC-101", "CO2 scrubber, liquor to beer well", f"S7 CO2 {f0(tot(S[7]))} kg/h"),
             ("V-104 / P-102", "Beer well, beer pump", f"S8 {f0(tot(S[8]))} kg/h"),
             ("E-101", "Beer preheater from hot stillage", kw("E-101 beer preheater (hot stillage)")),
             ("C-101 / E-102", "Beer column and reboiler", kw("E-102 beer column reboiler")),
             ("C-102 / E-103 / E-106", "Rectifier, condenser, reboiler", f"{D['E-103 rectifier condenser']:+,.0f} / {D['E-106 rectifier reboiler']:+,.0f} kW"),
             ("Relief devices", "PSV-301/302/303/401/501, PVRV-201/401/402, EVH-401, TSV-101..103, VT-101..103", "schedule sheet 5, sizing sheet 6")]
    rows2 = [("Tag", "Service", "Basis from sheet 2 (D unless A)"),
             ("MS-101A / B", "Molecular sieve beds, swing", f"S10 {f0(tot(S[10]))} kg/h; regen S12 {f0(tot(S[12]))} kg/h"),
             ("E-104", "Product cooler (CW)", kw("E-104 product cooler")),
             ("T-101 / P-103", "Day tank, transfer pump", f"S11 {f0(tot(S[11]))} kg/h; volume A open"),
             ("T-201A/B", "Fuel ethanol storage, PVRV-401 + FA, EVH-401, BD-401", "2 x 377 m3 (A), sheet 6"),
             ("DC-101 / P-104", "Decanter, thin stillage pump", f"S15 {f0(tot(S[15]))} / S16 {f0(tot(S[16]))} kg/h"),
             ("EV-101 / E-105", "Evaporator (3 effects A), condenser", f"{D['EV-101 evaporator (steam)']:+,.0f} / {D['E-105 evap. last-effect condenser']:+,.0f} kW"),
             ("D-101", "DDGS dryer (steam tube A)", f"{kw('D-101 dryer (steam/hot air)')}; S19 {f0(tot(S[19]))} kg/h"),
             ("CY-101 / BF-101", "Dryer cyclone, bag filter, stack", f"S20 {f0(tot(S[20]))} kg/h vapour"),
             ("SI-501", "DDGS silo", "volume A open"),
             ("B-101", "Steam boiler (fuel open)", f"LP steam {r['steam_t_h']:.1f} t/h (D, A constants)"),
             ("CT-101", "Cooling tower and CW header", "CW duty = sum of cooling lines on sheet 2"),
             ("ETP / ZLD", "Effluent treatment, zero liquid discharge", "S13, S18, blowdown; not sized"),
             ("Dust protection", "XP-101/102/501/502/503, RV-501, SD-501, DL-501, TAHH-501", "not sized (Kst gap)"),
             ("ESD, detection", "XV-201/301A/B/401/402/404/501; GD-201/301/302/401/402; FD-401; LAHH-401/402; LSHH-201; PAHH-301/302", "sheet 7"),
             ("Not drawn", "Enzyme and yeast dosing, CIP, DDGS cooler, spent-wash recycle", "open items for licensor")]
    y0 = 788
    section(s, 20, y0, 1100, "Equipment list (tags assigned by this drawing, sizes not set)")
    wtable(s, 20, y0 + 26, [96, 255, 189], rows1, 9.5, 11, 3)
    wtable(s, 580, y0 + 26, [100, 230, 210], rows2, 9.5, 11, 3)
    return s


# =====================================================================================================================
# sheet 2: HMB
# =====================================================================================================================
# =====================================================================================================================
# sheets 3 and 4: scenarios (overlays on the faded P&ID; safeguards keyed by badge, listed in the right panel)
# =====================================================================================================================
def badge(s, x, y, t):
    s.add(f'<circle cx="{x}" cy="{y}" r="9.5" fill="#fff" stroke="{RED}" stroke-width="1.6"/>'); T(s, x, y + 3.4, t, 9.5, 700, "middle", RED)


def ring(s, x, y, r=18): s.add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{RED}" stroke-width="2" stroke-dasharray="5 3"/>')


def box(s, x, y, w, h): R(s, x, y, w, h, "none", RED, 2, "6 4")


def esd_panel(s, causes):
    R(s, 875, 344, 235, 40, "#fff3f3", RED, 2)
    lab(s, 880, 356, causes, 9.5, 700, "start", RED)
    lab(s, 880, 367, "close XV-401/402/404, XV-301A/B; trip", 9.5, 400, "start", RED); lab(s, 880, 378, "P-102 / P-103 (fire: start FW-401, FC-401)", 9.5, 400, "start", RED)


def scen_table(s, rows, y0=788):
    section(s, 20, y0, 1100, "Scenario register (device sizes are A; R items and sources on sheets 5 to 9; HAZOP to confirm)", "#8e0000")
    wtable(s, 20, y0 + 26, [100, 165, 210, 395, 230], [("Scenario", "Initiating event", "Hazard", "Safeguards shown (keys 1a ...)", "Open data needs (not quantified)")] + rows, 9, 11, 3, hfill="#fde7e7")


def scen_panel(s, keys, notes):
    panel_box(s)
    y = section(s, 1135, 84, 445, "Symbols on this sheet", "#8e0000")
    star(s, 1160, y + 22, 13); T(s, 1182, y + 26, "release point or fire (qualitative)", 10)
    cloud(s, 1160, y + 46, 16, 8); T(s, 1182, y + 50, "gas extent sketch: not quantified", 10)
    badge(s, 1160, y + 68, "1a"); T(s, 1182, y + 71, "safeguard key, listed below (A)", 10)
    box(s, 1146, y + 81, 28, 12); T(s, 1182, y + 91, "red dashed = safeguard device that acts", 10)
    T(s, 1146, y + 108, "Faded = rest of the plant, as on sheet 1.", 10)
    y += 116
    for title, items in keys:
        y = section(s, 1135, y, 445, title, "#8e0000")
        y += 4
        for k, t in items:
            T(s, 1146, y + 11, k, 10, 700, fill=RED)
            y = WRAP(s, 1172, y + 11, t, 66, 10, 12.5) - 11 + 2
        y += 4
    y = section(s, 1135, y + 2, 445, "Notes", "#8e0000")
    note_lines(s, 1146, y + 16, notes, 71, 10, 13)


def sheet3(r):
    s = hdr_sheet(3, "Scenarios 1 and 2: ethanol release; fermenter CO2 and foam", f"3 of {TOTAL}: scenarios 1 and 2 on the P&ID")
    dim_pid(s)
    # ---- scenario 1
    cloud(s, 905, 548, 150, 56, "#ef9a9a", 0.30)
    star(s, 835, 536, 16); star(s, 991, 590, 16); snum(s, 812, 512, 1); snum(s, 1018, 602, 1)
    gd(s, 905, 566, ""); badge(s, 925, 574, "1a"); gd(s, 1030, 640, ""); badge(s, 1048, 648, "1a")
    esd_panel(s, "ESD-1 (A): GD high-high / FD / manual ->"); badge(s, 1100, 340, "1b")
    valve(s, 957, 557, 90, "gate", act=True, color=RED); badge(s, 940, 540, "1c")
    valve(s, 1096, 566, 90, "gate", act=True, color=RED); badge(s, 1078, 552, "1c")
    valve(s, 300, 497, 90, "gate", act=True, color=RED); badge(s, 280, 514, "1d")
    valve(s, 700, 512, 0, "gate", act=True, color=RED); badge(s, 722, 534, "1d")
    box(s, *BUND); badge(s, 936, 460, "1e")
    ring(s, 991, 564, 18); badge(s, 1010, 546, "1f")
    # ---- scenario 2
    star(s, 775, 200, 16); snum(s, 748, 146, 2)
    cloud(s, 775, 322, 140, 9, "#90a9d8", 0.55, BLUE)
    lab(s, 940, 302, "CO2 S7 (D): " + f"{r['CO2']:,.0f} kg/h total,", 9.5, 700, "start", BLUE); lab(s, 940, 314, "settles in pits and low spots", 9.5, 700, "start", BLUE)
    ring(s, 700, 205, 19); badge(s, 680, 190, "2a")
    valve(s, 716, 249, 0, "gate", act=True, color=RED); badge(s, 716, 269, "2b")
    ring(s, 742, 190, 9); badge(s, 757, 176, "2c")
    ring(s, 830, 178, 20); badge(s, 852, 160, "2d")
    ring(s, 852, 238, 18); ring(s, 842, 282, 14); badge(s, 876, 262, "2e")
    gd(s, 700, 296, ""); badge(s, 682, 306, "2f")
    box(s, 903, 134, 54, 130); badge(s, 966, 150, "2g")
    rows = [("1  Ethanol release, distillation / dehydration / day tank",
             "Flange, pump seal or sieve-bed hose failure; overfill or leak at E-104 outlet, T-101 or P-103",
             "Flammable liquid pool and vapour cloud, flash or pool fire; hot hydrous vapour at C-102 / MS-101 flashes on release",
             "1a GD-401 / GD-402; 1b ESD-1; 1c XV-402, XV-401 and XV-404 closed; 1d reboiler steam stopped (XV-301A/B); 1e bund and curbed pad with drain; 1f P-102 / P-103 tripped. Ignition source control and area classification not done",
             "Inventories of C-101, C-102, MS beds, T-101; hole sizes; ventilation and wind; detector layout; hot-work and electrical classification. Not quantified: needs release rate and ethanol properties (none in process_safety/data)"),
            ("2  Fermenter CO2, foam, overpressure",
             "Foaming raises level to the vent; blocked CO2 header or scrubber; loss of mash cooling; enzyme or feed overdose",
             f"Overpressure or vacuum of the fermenter; foam-over of mash; CO2 ({f0(tot(r['S'][7]))} kg/h total at design rate, D) collects in pits and enclosed spaces: asphyxiation",
             "2a LSH-201 foam alarm and LSHH-201 trip; 2b XV-201 closes mash feed; 2c AF-201 antifoam dosing; 2d PVRV-201 to scrubber; 2e TIC-201 / TV-201 jacket cooling; 2f GD-201 CO2 / O2 detector at low spots; 2g SC-101 scrubber and vent to safe location",
             "Fermenter count, volume, free board; vent sizing (not sized: needs CO2 rate per vessel and foam model); header design pressure; CO2 dispersion: not quantified, needs vent height and site layout")]
    scen_table(s, rows)
    scen_panel(s, [("Scenario 1 safeguards (A)", [("1a", "GD-401 / GD-402 flammable gas detectors at the sieve / cooler area and the day-tank pump; high-high gas to ESD-1."),
                                                   ("1b", "ESD-1 logic: also manual push-button and flame detection (sheet 4). Voting and SIL not set."),
                                                   ("1c", "XV-402 (T-101 outlet), XV-401 (T-201A/B outlet) and XV-404 (T-101 inlet) close; remote isolation of the largest inventories."),
                                                   ("1d", "XV-301A / XV-301B: LP steam to E-102 and E-106 reboilers stopped so the columns stop boiling."),
                                                   ("1e", "BD-401 bund with drain DV-401 to a contained sump (volume rule on sheet 8)."),
                                                   ("1f", "P-102 beer and P-103 product pumps tripped (P-103 ringed).")]),
                   ("Scenario 2 safeguards (A)", [("2a", "LSH-201 foam alarm and LSHH-201 trip on each fermenter."), ("2b", "XV-201 closes mash feed on high level."), ("2c", "AF-201 antifoam dosing."),
                                                  ("2d", "PVRV-201 pressure / vacuum relief to the CO2 line and scrubber."), ("2e", "TIC-201 / TV-201 jacket cooling."),
                                                  ("2f", "GD-201 CO2 / O2 detector at floor level; confined-space entry rules."), ("2g", "SC-101 scrubber, vent to a safe location (height open).")])],
              ["No consequence distance is given: no ethanol property data or released-mass input exists in this repo.",
               f"Scenario 2 number is stoichiometric only: S7 = {r['CO2']:,.0f} kg/h CO2 for the plant ({r['CO2']/M_CO2:,.1f} kmol/h, D); per fermenter needs the vessel count."])
    return s


def sheet4(r):
    s = hdr_sheet(4, "Scenarios 3 and 4: ethanol tank fire; DDGS dryer dust and fire", f"4 of {TOTAL}: scenarios 3 and 4 on the P&ID")
    dim_pid(s)
    # ---- scenario 3
    flame(s, 1062, 472, 0, 52, 44); star(s, 1062, 482, 14); snum(s, 1032, 440, 3)
    ring(s, 1090, 434, 11); badge(s, 1108, 424, "3a")
    ring(s, 1004, 504, 19); badge(s, 984, 490, "3b")
    fd(s, 1075, 640, ""); gd(s, 1030, 640, ""); badge(s, 1093, 648, "3c"); badge(s, 1012, 648, "3c")
    R(s, 1100, 492, 14, 10, "#fff", RED, 1.8); badge(s, 1090, 508, "3d")
    s.add(f'<path d="M1028,484 Q1062,462 1096,484" fill="none" stroke="{RED}" stroke-width="2.4" stroke-dasharray="3 3"/>'); badge(s, 1032, 462, "3e")
    box(s, *BUND); badge(s, 936, 460, "3f")
    valve(s, 1096, 566, 90, "gate", act=True, color=RED); badge(s, 1078, 552, "3g"); valve(s, 957, 557, 90, "gate", act=True, color=RED); badge(s, 940, 540, "3g")
    ring(s, 991, 564, 18)
    esd_panel(s, "ESD-1 (A): LAHH / FD / GD / manual ->"); badge(s, 1100, 340, "3h")
    esdl(s, [(1004, 485), (1004, 470), (990, 400), (990, 384)]) if False else None
    # ---- scenario 4
    star(s, 700, 690, 14); star(s, 855, 628, 14); snum(s, 778, 672, 4)
    ring(s, 700, 612, 19); badge(s, 680, 596, "4a")
    valve(s, 610, 638, 90, "gate", act=True, color=RED); badge(s, 590, 630, "4b")
    R(s, 724, 632, 20, 16, "#fff", RED, 2); lab(s, 734, 644, "SD", 9.5, 700, "middle", RED); badge(s, 752, 668, "4c") if False else None
    badge(s, 740, 660, "4c")
    box(s, 830, 604, 50, 46); box(s, 744, 600, 46, 62); badge(s, 810, 592, "4d")
    ring(s, 765, 667, 7); badge(s, 783, 654, "4e")
    for x in (610, 630, 650, 670): PL(s, [(x, 654), (x, 662)], 2.4, RED)
    badge(s, 590, 662, "4f")
    box(s, 716, 720, 64, 46); badge(s, 726, 716, "4g")
    rows = [("3  Ethanol storage tank fire (T-201A/B)",
             "Ignition of vapour at the vent, roof or shell seal; overfill; leak from shell or piping into the bund; lightning or hot work",
             "Tank-top, bund pool or flange fire of a polar flammable liquid; heat load on the neighbouring tank, T-101 and pumps",
             "3a PVRV-401 with flame arrestor; 3b LIC-401 with LAHH-401; 3c FD-401 and GD-401; 3d foam chamber FC-401 (foam type for a polar liquid to confirm); 3e FW-401 fire-water cooling ring and monitors; 3f bund, drain closed in service; 3g XV-401 / XV-402 and P-103 trip; 3h ESD-1",
             "Tank diameter, height, fill level, roof type; bund size; foam and water rates; fire-water capacity; spacing. Not quantified: radiation needs burning rate and flame model inputs for ethanol (none in this repo)"),
            ("4  DDGS dryer, dust and fire",
             "Hot spot or smouldering DDGS in the dryer, cyclone, bag filter or silo; plugging or overheated product; static or mechanical spark",
             "Dryer or filter fire; dust explosion in cyclone, bag filter or silo (organic feed dust, test data needed); ethanol vapour in the dryer exhaust",
             "4a TIC-501 with TAHH-501; 4b XV-501 trips steam and the feed screw; 4c spark / CO detection SD-501; 4d XP-501 / 502 / 503 vent panels; 4e RV-501 rotary-valve isolation; 4f DL-501 deluge; 4g silo temperature / CO monitoring; housekeeping and hot-work rules",
             "Dust tests of DDGS (Kst, Pmax, MIE, layer ignition temperature); vessel volumes and vent areas; dryer type and heat source; ethanol in dryer feed (S15 liquid carries ethanol, D). Not quantified: no dust explosion model used")]
    scen_table(s, rows)
    scen_panel(s, [("Scenario 3 safeguards (A)", [("3a", "PVRV-401 with flame arrestor on the tank roof; vent to a safe location."), ("3b", "LIC-401 level with LAHH-401 to ESD-1 (overfill)."),
                                                   ("3c", "FD-401 flame and GD-401 gas detection at the tank farm and pump."), ("3d", "Foam chamber FC-401 on the shell; foam suitable for a polar solvent to be confirmed."),
                                                   ("3e", "Fire-water cooling ring and monitors for the burning and the neighbouring tank."), ("3f", "BD-401 bund, drain valve DV-401 closed in service (volume rule on sheet 8)."),
                                                   ("3g", "XV-401 / XV-402 isolate, P-103 trips."), ("3h", "ESD-1 starts fire water and foam on FD / manual.")]),
                   ("Scenario 4 safeguards (A)", [("4a", "TIC-501 exhaust temperature with TAHH-501 trip."), ("4b", "XV-501 stops LP steam to the dryer; feed screw stops."),
                                                  ("4c", "Spark / CO detection SD-501 on the exhaust duct."), ("4d", "XP-501 / XP-502 / XP-503 vent panels on CY-101, BF-101, SI-501 (areas not sized)."),
                                                  ("4e", "RV-501 rotary valve isolation under the cyclone."), ("4f", "DL-501 deluge nozzles in the dryer drum."),
                                                  ("4g", "SI-501 temperature and CO monitoring.")])],
              ["Scenario 3: the flame is a sketch. There is no ethanol pool-fire input set in this repo, so no radiation distance is given.",
               "Scenario 4: dryer is a conceptual steam-tube rotary (A); a direct-fired heater would change the ignition picture. No dust test value is quoted."])
    return s



# =====================================================================================================================
# Rev B additions: safety devices on sheet 1, relief sizing, sensitivity, new sheet 2, safety design basis sheets 5 to 9
# =====================================================================================================================
BUND = (928, 452, 187, 134)


def xp(s, x, y, w=20, h=6):
    """explosion vent panel (dust): hatched rectangle, red outline"""
    s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#hatch)" stroke="{RED}" stroke-width="1.4"/>')


def tsv(s, x, y):
    """thermal relief valve: small triangle"""
    s.add(f'<polygon points="{x-5},{y+5} {x+5},{y+5} {x},{y-5}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    PL(s, [(x, y + 5), (x, y + 10)], 1.6)


def vent_up(s, x, y0, y1, tag, tx, ty, anchor="start"):
    line(s, [(x, y0), (x, y1)], INK, 1.8, "u"); lab(s, tx, ty, tag, 9.5, 700, anchor)


def safety_devices(s):
    """Rev B devices drawn on sheet 1 (and faded under the scenario sheets). All sizes A unless sheet 6 says otherwise."""
    # --- band A: dust, atmospheric vents, fermenter trips
    xp(s, 52, 104, 24, 6); lab(s, 82, 111, "XP-101", 9.5, 700, "start", RED)
    xp(s, 54, 259, 20, 5); lab(s, 64, 300, "XP-102 (A)", 9.5, 700, "middle", RED)
    for x, tag in ((125, "VT-101"), (430, "VT-102"), (592, "VT-103")):
        line(s, [(x, 203), (x, 188)], INK, 1.8, "u"); lab(s, x + 5, 187, tag, 9.5, 700, "start")
    valve(s, 716, 249, 0, "gate", act=True, color=RED); lab(s, 716, 274, "XV-201", 9.5, 700, "middle", RED)
    inst(s, 665, 205, "LSHH", "201", False)
    gd(s, 700, 296, "GD-201")
    # relief vent header / stack
    R(s, 1008, 214, 102, 52, "#fff", INK, 1.6)
    lab(s, 1059, 230, "VH-101 / ST-101", 10, 700, "middle"); lab(s, 1059, 243, "relief vent header,", 9.5, 400, "middle")
    lab(s, 1059, 255, "stack height open (A)", 9.5, 400, "middle")
    # --- band B: column pressure trips, PSV-303, XV-301A/B, TSVs, detectors
    inst(s, 350, 348, "PAHH", "301", False); inst(s, 548, 338, "PAHH", "302", False)
    line(s, [(300, 484), (300, 509)], STEAM, 1.8, "d")
    valve(s, 300, 497, 90, "gate", act=True, color=RED); lab(s, 288, 500, "XV-301A", 9.5, 700, "end", RED)
    line(s, [(735, 512), (640, 512)], STEAM, 1.8, "l")
    valve(s, 700, 512, 0, "gate", act=True, color=RED); lab(s, 700, 484, "XV-301B", 9.5, 700, "middle", RED)
    line(s, [(780, 358), (780, 352)], INK, 1.8); psv(s, 780, 336); line(s, [(798, 336), (808, 336)], INK, 1.8, "r")
    lab(s, 812, 334, "PSV-303", 9.5, 700, "start"); lab(s, 812, 345, "to VH-101", 9.5, 400, "start")
    tsv(s, 668, 380); lab(s, 678, 383, "TSV-101", 9.5, 700, "start")
    tsv(s, 255, 393); lab(s, 264, 391, "TSV-103", 9.5, 700, "start")
    tsv(s, 872, 541); lab(s, 881, 545, "TSV-102", 9.5, 700, "start")
    gd(s, 150, 470, "GD-301"); gd(s, 700, 440, "GD-302")
    # --- tank farm: day tank vent, ESD valve XV-404, LAHH, bund, foam, fire water, emergency vent
    vent_up_y = 457
    line(s, [(957, 473), (957, vent_up_y)], INK, 1.8); s.add(f'<circle cx="957" cy="450" r="7" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    line(s, [(957, 443), (957, 432)], INK, 1.8, "u"); lab(s, 949, 452, "PVRV-402 + FA", 9.5, 700, "end")
    valve(s, 915, 518, 0, "gate", act=True, color=RED); lab(s, 925, 536, "XV-404", 9.5, 700, "middle", RED)
    inst(s, 845, 448, "LAHH", "402", False); sig(s, [(860, 455), (900, 470), (932, 498)])
    inst(s, 1010, 533, "LAHH", "401", False)
    lab(s, 1082, 420, "EVH-401 emergency vent (A)", 9.5, 700, "end")
    R(s, *BUND, "none", AMBER, 1.6, "9 3 2 3")
    lab(s, 1112, 614, "BD-401 bund, DV-401 drain (A)", 9.5, 700, "end", AMBER)
    R(s, 1100, 492, 14, 10, "#fff", RED, 1.8); lab(s, 1108, 489, "FC-401", 9.5, 700, "end", RED)
    s.add(f'<path d="M1028,484 Q1062,462 1096,484" fill="none" stroke="{RED}" stroke-width="2.2" stroke-dasharray="3 3"/>'); lab(s, 1034, 489, "FW-401", 9.5, 700, "start", RED)
    # --- band C: evaporator PSV, dryer protection, steam header PSV
    line(s, [(325, 616), (325, 600)], INK, 1.8); psv(s, 325, 584); line(s, [(343, 584), (360, 584)], INK, 1.8, "r")
    lab(s, 364, 578, "PSV-401", 9.5, 700, "start"); lab(s, 364, 568, "to VH-101", 9.5, 400, "start")
    inst(s, 660, 610, "TAHH", "501", False)
    lab(s, 594, 642, "XV-501", 9.5, 700, "end", RED)
    R(s, 724, 632, 20, 16, "#fff", RED, 2); lab(s, 734, 644, "SD", 9.5, 700, "middle", RED); lab(s, 734, 660, "SD-501", 9.5, 700, "middle", RED)
    s.add(f'<circle cx="765" cy="667" r="7" fill="#fff" stroke="{RED}" stroke-width="1.8"/>'); lab(s, 776, 676, "RV-501", 9.5, 700, "start", RED)
    xp(s, 786, 610, 6, 14); lab(s, 796, 622, "XP-501", 9.5, 700, "start", RED)
    xp(s, 866, 600, 12, 6); lab(s, 882, 606, "XP-502", 9.5, 700, "start", RED)
    xp(s, 738, 716, 20, 6); lab(s, 762, 716, "XP-503", 9.5, 700, "start", RED)
    for x in (610, 630, 650, 670): PL(s, [(x, 654), (x, 662)], 2.4, RED)
    lab(s, 604, 667, "DL-501", 9.5, 700, "end", RED)
    line(s, [(875, 696), (875, 686)], STEAM, 1.8); psv(s, 875, 670); line(s, [(893, 670), (905, 670)], INK, 1.8, "r")
    lab(s, 909, 673, "PSV-501", 9.5, 700, "start"); lab(s, 909, 684, "to VH-101", 9.5, 400, "start")


# ---------------------------------------------------------------------------------------------------------------------
# frozen tool outputs (recorded, not recomputed by the standard-library generator)
# ---------------------------------------------------------------------------------------------------------------------
# rect_check.py: /private/tmp/claude-501/venv_val/bin/python -I /private/tmp/claude-501/val_ethanol/revb/rect_check.py
#   thermo 0.6.1 NRTL (ChemSep IPs) ethanol-water at 1 atm, CoolProp 8.0.0, scipy; McCabe-Thiele, xD = 94 wt %, feed vapour 50 wt % (S9).
FROZEN = dict(
    Rmin_tangent=2.7086, Rmin_q=2.4073, N_R30=66, N_R325=48, N_R35=39, N_R40=31,        # ideal stages, enriching section
    K_S9=1.2243, K_S10=1.1394, K_CO2=1.2848,                                              # ideal-gas cp0/(cp0-R) of the vapour mixes, CoolProp Cp0molar
    lam_e=849.83, T_nbp_e=351.57,                                                         # CoolProp 8.0.0: ethanol latent heat kJ/kg and NBP K at 1 atm
    # bst_corn_detail.py: /private/tmp/claude-501/venv_tools/bst/bin/python -I /private/tmp/claude-501/val_ethanol/revb/bst_corn_detail.py
    #   biosteam 2.54.0 / biorefineries 2.35.1 corn.Biorefinery (conventional dry grind), 19,012 L/h anhydrous ethanol, patch as in TOOLS_SURVEY 2a
    bst_corn=dict(moist=0.15, starch=0.612, fiber=0.1067, protein=0.0833, oil=0.034, ash=0.014),
    bst_ddgs_dry=0.5600, bst_ddgs_tkl=0.6218, bst_oil_kgL=0.0362, bst_yeast_kgL=0.0147, bst_grain_kgL=2.439,
    bst_ssf_yield=0.95, bst_thermal_MJL=8.78, bst_steam_kgL=2.78, bst_overall_Y=0.930,
)
REFS = dict(  # fetched and read in ETHANOL_VALIDATION.md / GAP_CLOSURE_BIO.md (URLs in ETHANOL_comparisons.csv)
    igl_grain=2.465, pr_grain=2.5526, anl_Lt=418.76, vv_ddgs=0.6087, pr_ddgs=0.700, anl_ddgs_tkl=0.786, anl_ddgs_dry=0.707, vv_co2=0.7633, pr_co2=0.74,
    igl_steam=6.6, pr_steam=5.04, vv_boiler=5.2174, anl_thermal=7.6891, igl_water=6.485, tmpl_grain=86800.0, tmpl_ddgs=26000.0,
)
# fermenter basis: BioSTEAM SSF defaults tau 60 h, V_wf 0.83 (tool, TOOLS_SURVEY 2a); turnaround, max size, mash density, peak factor are A
FERM = dict(tau=60.0, vwf=0.83, turn=4.0, vmax=700.0, rho=1050.0, peak=2.0)
TANKS = dict(T201_D=8.0, T201_H=7.5, T201_n=2, T101_D=4.5, T101_H=6.3, fill201=20.0, empty201=60.0, fill101=None, empty101=20.0)  # all A


def sizing(r):
    """Relief sizing with the repo's process_safety package (API 520-I gas, API 2000 5th ed. tank venting). Every input marked A is an assumption."""
    a = A; D = r["duty"]; S = r["S"]; out = {"ok": True, "rows": [], "geom": {}}
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if root not in sys.path: sys.path.insert(0, root)
        from process_safety import relief as RL, tank_venting as TV
    except Exception as e:                                           # pragma: no cover
        out["ok"] = False; out["err"] = repr(e); return out
    Mmix = lambda x: 1.0 / (x / M_ETOH + (1 - x) / M_H2O)
    lam_mix = lambda x: x * a["lam_e"] + (1 - x) * a["lam_w"]
    set_g = 150.0
    P1 = RL.relieving_pressure_kpa(set_g, "single_non_fire"); P2 = RL.ATM

    def vap(tag, case, W, T_K, M, k, setg, note):
        p1 = RL.relieving_pressure_kpa(setg, "single_non_fire")
        res = RL.gas_area(W, T_K, p1, P2, M, k)
        out["rows"].append((tag, case, f"W {W:,.0f} kg/h; T {T_K-273.15:.0f} C; M {M:.1f}; k {k:.3f}; set {setg/100:.2f} barg (A), 10 % accumulation; back pressure atm (A)",
                            f"{res.required_area_mm2:,.0f} mm2 effective ({res.regime})", note, res.required_area_mm2))
        return res
    W1 = D["E-102 beer column reboiler"] * 3600 / lam_mix(a["x_s9"])
    r301 = vap("PSV-301", "C-101 blocked overhead (S9 line closed), reboiler steam continues", W1, T_["s9"] + 273.15, Mmix(a["x_s9"]), FROZEN["K_S9"], set_g,
               "API 520-I eq. (module relief.gas_area). W = E-102 duty / mixture latent heat (all duty to vapour: conservative). Fire case not sized: needs diameter, height, holdup")
    W2 = (1 + a["RR_rect"]) * tot(S[10])
    r302 = vap("PSV-302", "C-102 loss of E-103 cooling or reflux (all top vapour unrefluxed)", W2, T_["s10"] + 273.15, Mmix(a["x_hyd"]), FROZEN["K_S10"], set_g,
               "W = (1 + R) x S10. Fire case and vacuum case not sized")
    W3 = tot(S[10])
    vap("PSV-303", "MS-101A/B blocked outlet on the vapour feed S10", W3, T_["s10"] + 273.15, Mmix(a["x_hyd"]), FROZEN["K_S10"], set_g,
        "W = S10. Regeneration vacuum and bed fire not sized: needs bed volume and adsorbent data")
    # fermenter
    Qm = tot(S[6]) / FERM["rho"]; Vg = Qm * (FERM["tau"] + FERM["turn"]) / FERM["vwf"]; N = math.ceil(Vg / FERM["vmax"])
    out["geom"].update(Qmash=Qm, Vgross=Vg, N=N, Veach=Vg / N)
    Wf = tot(S[7]) / N * FERM["peak"]
    vap("PVRV-201", f"F-101 blocked CO2 header, one fermenter at {FERM['peak']:.0f} x its average rate (A)", Wf, T_["s7"] + 273.15, M_CO2, FROZEN["K_CO2"], 20.0,
        f"N = {N} fermenters of {Vg/N:,.0f} m3 gross (D from tau 60 h, V_wf 0.83 BioSTEAM defaults; turnaround 4 h, max 700 m3, rho 1,050 kg/m3 are A). Foam-over and fire not sized: needs foam model")
    # tanks
    for tag, Dm, Hm, fill, empty in (("T-201A/B", TANKS["T201_D"], TANKS["T201_H"], TANKS["fill201"], TANKS["empty201"]),
                                     ("T-101", TANKS["T101_D"], TANKS["T101_H"], PROD_M3_H, TANKS["empty101"])):
        V = math.pi / 4 * Dm * Dm * Hm; Aw = TV.wetted_area_m2("vertical", Dm, Hm)
        nv = TV.normal_venting(V, fill, empty, True)
        fv = TV.fire_venting_Nm3h(Aw, 1.0, a["lam_e"], FROZEN["T_nbp_e"], M_ETOH)
        out["geom"][tag] = dict(V=V, Aw=Aw, out=nv["outbreathing_Nm3h"], inn=nv["inbreathing_Nm3h"], fire=fv)
        out["rows"].append((tag + " normal", "Normal out/in-breathing (fill, empty, thermal)",
                            f"V {V:,.0f} m3 (D {Dm} m x H {Hm} m, A); fill {fill:.1f} m3/h, empty {empty:.0f} m3/h (A); flash point below 37.8 C",
                            f"out {nv['outbreathing_Nm3h']:,.0f} / in {nv['inbreathing_Nm3h']:,.0f} Nm3/h air", "API 2000 5th ed. (1998) Table 2B, module tank_venting; 7th ed. changed the thermal method and is not implemented", None))
        out["rows"].append((tag + " fire", "External fire, bare shell, no credit (F = 1)",
                            f"wetted area {Aw:,.0f} m2 (shell, level at full height, 9.14 m cap); ethanol L {a['lam_e']:.0f} kJ/kg, T {FROZEN['T_nbp_e']} K, M {M_ETOH:.2f}",
                            f"{fv:,.0f} Nm3/h air equivalent", "API 2000 5th ed. Eq. 1B form. Total vent capacity (PVRV at full lift + EVH) must exceed this; frangible roof joint is the alternative (T-201A/B)", fv))
    Vl = max(out["geom"]["T-201A/B"]["V"], out["geom"]["T-101"]["V"]); Vt = out["geom"]["T-201A/B"]["V"] * TANKS["T201_n"] + out["geom"]["T-101"]["V"]
    out["geom"]["bund"] = dict(by_largest=1.10 * Vl, by_total=0.25 * Vt, V=max(1.10 * Vl, 0.25 * Vt), Vt=Vt)
    return out


def sens(overrides):
    """key metrics of the HMB for an override dict (calls solve)"""
    r = solve(overrides); S = r["S"]; L = r["L_h"]
    return dict(grain=r["grain"] / L, Lt=L / r["grain"] * 1000, ddgs=tot(S[19]) / L, dry=(S[19]["glucose"] + S[19]["solids"]) / L, co2=r["CO2"] / L,
                steam=r["steam_kg_per_L"], r=r)


# ---------------------------------------------------------------------------------------------------------------------
# sheet 2 (Rev B)
# ---------------------------------------------------------------------------------------------------------------------
def sheet2(r, rA):
    s = hdr_sheet(2, "Heat and material balance: grain ethanol, 100 KLPD", f"2 of {TOTAL}: HMB, duties, closure, benchmarks, Rev A to Rev B changes")
    S = r["S"]; labels = list(range(1, 21)); D = r["duty"]; DA = rA["duty"]; L = r["L_h"]
    names = ["grain", "milled", "water", "slurry", "mash", "sacch.", "CO2", "beer", "BC ovhd", "hydrous", "product", "regen", "lees", "stillage", "cake", "thin st.", "syrup", "cond.", "DDGS", "dry vap."]
    pz = {1: 1.01, 2: 1.01, 3: 2.0, 4: 1.01, 5: 1.5, 6: 1.5, 7: 1.05, 8: 1.5, 9: 1.3, 10: 1.2, 11: 1.1, 12: 1.2, 13: 1.4, 14: 1.4, 15: 1.01, 16: 1.5, 17: 1.1, 18: 1.0, 19: 1.01, 20: 1.01}
    ph = {1: "solid", 2: "solid", 3: "liquid", 4: "slurry", 5: "slurry", 6: "slurry", 7: "gas", 8: "slurry", 9: "vapour", 10: "vapour", 11: "liquid", 12: "vapour", 13: "liquid", 14: "slurry", 15: "wet solid", 16: "slurry", 17: "slurry", 18: "liquid", 19: "solid", 20: "vapour"}
    tk = {n: T_[f"s{n}"] for n in labels if f"s{n}" in T_}
    for n in (14, 15, 16): tk[n] = r["t_stillage_out"]
    tk[11] = 40
    rows = [("Description", names), ("Mass flow, kg/h", [f0(tot(S[n])) for n in labels]), ("Composition, wt %", None)]
    for c, nm in zip(COMPS, ["Starch", "Glucose (sugars)", "Ethanol", "Water", "CO2", "Other solids"]):
        rows.append((nm, [pct(S[n][c], tot(S[n])) for n in labels]))
    rows += [("Conditions (all A)", None), ("Temperature, C", [f"{tk[n]:.0f}" for n in labels]), ("Pressure, bar abs", [f"{pz[n]:.2f}".rstrip("0").rstrip(".") for n in labels]), ("Phase", [ph[n] for n in labels])]
    y = hmb_table(s, 20, 88, labels, rows, first_w=190, col_w=45, rh=18.5, size=10, title="Stream table, one column per stream number on sheet 1 (D from the balance; T, P, phase are A)", max_w=1100)
    yl = y + 8
    yl = section(s, 20, yl, 540, "Duties, kW (+ heat added, - removed); D from A constants")
    drows = [("Tag", "Service", "Rev B", "Rev A")]
    names_d = [("H-101", "H-101 slurry heater", "Slurry heater, steam"), ("H-102", "H-102 mash cooler 1", "Mash cooler 85 to 60 C, CW"), ("H-103", "H-103 mash cooler 2", "Mash cooler 60 to 33 C, CW"),
               ("F-101", "F-101 fermentation cooling", "Fermentation heat removal, CW (A)"), ("E-101", "E-101 beer preheater (hot stillage)", "Beer preheat to 80 C from stillage"),
               ("E-102", "E-102 beer column reboiler", "Beer column reboiler, steam"), ("E-103", "E-103 rectifier condenser", "Rectifier condenser, CW"),
               ("E-106", "E-106 rectifier reboiler", "Rectifier reboiler, steam"), ("E-104", "E-104 product cooler", "Product condense and cool, CW"),
               ("EV-101", "EV-101 evaporator (steam)", "Evaporator steam, 3 effects (economy 2.5 A)"), ("E-105", "E-105 evap. last-effect condenser", "Evaporator last-effect condenser, CW"),
               ("D-101", "D-101 dryer (steam/hot air)", "DDGS dryer heat input (eta 0.65 A)")]
    for tg, k, sv in names_d: drows.append((tg, sv, f"{D[k]:+,.0f}", f"{DA[k]:+,.0f}"))
    drows.append(("Steam", "Sum of H-101, E-102, E-106, EV-101, D-101", f"{r['steam_kW']:+,.0f}", f"{rA['steam_kW']:+,.0f}"))
    drows.append(("B-101", f"LP steam at 2,100 kJ/kg (A): {r['steam_t_h']:.1f} t/h, {r['steam_kg_per_L']:.2f} kg per L (Rev A {rA['steam_t_h']:.1f} t/h, {rA['steam_kg_per_L']:.2f})", "D", "D"))
    drows.append(("MS-101", "Sieve vaporiser, superheater, regeneration vacuum", "not calc.", "not calc."))
    yl = wtable(s, 20, yl, [60, 350, 65, 65], drows, 9.5, 11, 2)
    # ---- middle column: closure, DDGS decomposition, sensitivity, steam benchmark
    xb = 575
    yc = 88 + 22 + 18.5 * (len(rows) + 1) + 8
    yc = section(s, xb, yc, 545, "Closure checks (asserted in code, Rev B)")
    el = r["elem"]
    cl = [f"Overall mass: in {f0(r['in'])} kg/h (S1 + S3), out {f0(r['out'])} kg/h (S7 + S11 + S13 + S18 + S19 + S20), error {r['err']:.2f} %",
          f"Elements across hydrolysis + fermentation (starch + hydrolysis water in; residual glucose + ethanol + CO2 out): C {el['C'][0]:,.0f} / {el['C'][1]:,.0f} kg/h ({el['C'][2]:+.2f} %), "
          f"H {el['H'][0]:,.0f} / {el['H'][1]:,.0f} ({el['H'][2]:+.2f} %), O {el['O'][0]:,.0f} / {el['O'][1]:,.0f} ({el['O'][2]:+.2f} %); carbon in kmol {r['C_in']:,.1f} / {r['C_out']:,.1f}",
          f"Stoichiometry: ethanol {S[8]['ethanol']/M_ETOH:,.1f} kmol/h = CO2 {S[7]['co2']/M_CO2:,.1f} kmol/h (asserted); CO2 depends on ethanol only, so it does not change with Y",
          "Unit closure, error %: " + "; ".join(f"{k} {abs(v):.2f}" for k, v in r["units"].items())]
    yc = note_lines(s, xb + 8, yc + 16, cl, 100, 9.5, 12.5)
    # DDGS decomposition
    yc = section(s, xb, yc + 2, 545, "DDGS: where the mass comes from, kg dry per L product (D) against references")
    g = r["ddgs_split"]; gA = rA["ddgs_split"]; B = FROZEN
    dd = [("Item", "Rev A", "Rev B", "BioSTEAM corn", "Reference"),
          ("Non-fermentable grain solids (A7, A8)", f"{gA['nonferm']:.3f}", f"{g['nonferm']:.3f}", f"{B['bst_ddgs_dry']-B['bst_yeast_kgL']:.3f} (+oil {B['bst_oil_kgL']:.3f} sold)", "-"),
          ("Residual glucose / yeast in DDGS", f"{gA['residual']:.3f}", f"{g['residual']:.3f}", f"{B['bst_yeast_kgL']:.3f} yeast", "-"),
          ("DDGS dry", f"{gA['nonferm']+gA['residual']:.3f}", f"{g['nonferm']+g['residual']:.3f}", f"{B['bst_ddgs_dry']:.3f}", f"ANL {REFS['anl_ddgs_dry']:.3f} (0.56 to 0.97)"),
          ("DDGS at 10 % moisture, t/KL", f"{tot(rA['S'][19])/rA['L_h']:.3f}", f"{tot(S[19])/L:.3f}", f"{B['bst_ddgs_tkl']:.3f}", f"VV {REFS['vv_ddgs']:.3f}; PR {REFS['pr_ddgs']:.3f}; ANL {REFS['anl_ddgs_tkl']:.3f}")]
    yc = wtable(s, xb, yc, [185, 55, 55, 115, 135], dd, 9, 10.5, 2)
    yc = note_lines(s, xb + 8, yc + 16, [
        f"Reading (D): with grain at {r['grain']/L:.2f} kg/L and every non-starch solid going to DDGS, DDGS cannot fall below {g['nonferm']:.3f} kg dry/L ({g['nonferm']/0.9:.2f} t/KL) however high Y is. "
        "The references at 0.61 to 0.70 t/KL need non-starch solids removed (corn oil, fibre, protein feed, wet sales) or a different grain: not modelled, open item."], 100, 9.5, 12)
    # sensitivity
    yc = section(s, xb, yc + 2, 545, "Sensitivity (solve() re-run; A values varied one at a time from Rev B)")
    sv = [("Case", "grain kg/L", "L/t grain", "DDGS t/KL", "steam kg/L", "CO2 t/KL")]
    for nm, ov in (("Rev A (Y 0.90, R 3.0, L_e 840)", REVA), ("Rev B (Y 0.93, R 3.5)", {}), ("Rev B, Y 0.88", dict(Y=0.88)), ("Rev B, Y 0.95", dict(Y=0.95)),
                   ("Rev B, evaporator economy 3.0", dict(econ=3.0)), ("Rev B, starch 0.66 (A7)", dict(starch=0.66)), ("Rev B, dryer eta 0.80", dict(eta_dry=0.80))):
        m = sens(ov); sv.append((nm, f"{m['grain']:.3f}", f"{m['Lt']:.0f}", f"{m['ddgs']:.3f}", f"{m['steam']:.2f}", f"{m['co2']:.4f}"))
    yc = wtable(s, xb, yc, [195, 70, 70, 70, 70, 70], sv, 9, 10.5, 2)
    yc = section(s, xb, yc + 2, 545, "Steam and thermal energy against references (all grade A documents unless marked)")
    thermal = r["steam_kg_per_L"] * A["lam_st"] / 1000
    sh = lambda k: 100 * D[k] / r["steam_kW"]
    yc = note_lines(s, xb + 8, yc + 14, [
        f"Ours {r['steam_kg_per_L']:.2f} kg steam/L = {thermal:.1f} MJ/L (Rev A {rA['steam_kg_per_L']:.2f}). IGL Kashipur {REFS['igl_steam']:.1f}; PR Nashik {REFS['pr_steam']:.2f} (scope unclear); VV {REFS['vv_boiler']:.2f} is capacity incl. 6 MW power.",
        f"US dry mills (ANL 2007 Table 6): mean 1.73 kg/L, range 0.07 to 3.55, SD large; Dale and Tyner 2006: 36,000 Btu/gal = 4.8 kg/L (D). ANL fuel {REFS['anl_thermal']:.1f} MJ/L. BioSTEAM corn run: {B['bst_steam_kgL']:.2f} kg/L steam + NG = {B['bst_thermal_MJL']:.2f} MJ/L (NG at an assumed 50 MJ/kg).",
        f"Shares of steam (ours / Dale and Tyner): dryer {sh('D-101 dryer (steam/hot air)'):.0f} % / 27.5 %, beer + rectifier columns {sh('E-102 beer column reboiler')+sh('E-106 rectifier reboiler'):.0f} % / 32 %, evaporator {sh('EV-101 evaporator (steam)'):.0f} % / 26.4 %. "
        "US plants sell 36.7 % of DDGS wet (ANL Table 3); selling wet cake removes the dryer share. No heat integration beyond E-101 is modelled (A)."], 100, 9.5, 12)
    # ---- right panel: assumptions + changes box
    panel_box(s)
    y = section(s, 1135, 84, 445, "ASSUMED (A) and sourced bases, Rev B")
    a = A
    arows = [("ID", "Assumption", "Value"),
             ("A1", "Product density, anhydrous ethanol", f"{a['rho_prod']:.0f} kg/m3"), ("A2", "Ethanol in dehydrated product", f"{100*a['x_prod']:.1f} wt %"),
             ("A3", "Ethanol, rectifier overhead to sieve", f"{100*a['x_hyd']:.0f} wt %"), ("A4", "Ethanol, sieve regeneration recycle", f"{100*a['x_regen']:.0f} wt %"),
             ("A5", "Ethanol, beer column overhead", f"{100*a['x_s9']:.0f} wt %"), ("A6", "Beer ethanol lost to stillage", f"{100*a['loss']:.1f} %"),
             ("A7", "Starch in grain as received (no source)", f"{100*a['starch']:.0f} wt %"), ("A8", "Moisture in grain", f"{100*a['moist']:.0f} wt %"),
             ("A9", "Grain in slurry (as received)", f"{100*a['slurry']:.0f} wt %"), ("A10", "Starch to glucose conversion", "100 %"),
             ("A11", "Starch to ethanol + CO2, overall Y (range 0.88-0.95)", f"{100*a['Y']:.0f} %"), ("A12", "Decanter solids capture to cake", f"{100*a['cap']:.0f} %"),
             ("A13", "Solids in wet cake", f"{100*a['cake']:.0f} wt %"), ("A14", "Solids in syrup", f"{100*a['syrup']:.0f} wt %"),
             ("A15", "Moisture in DDGS", f"{100*a['ddgs_moist']:.0f} wt %"), ("A16", "Rectifier reflux ratio (D: R/Rmin 1.29)", f"{a['RR_rect']:.1f} kg/kg"),
             ("A17", "cp aqueous / ethanol liquid", f"{a['cp']:.1f} / {a['cp_et']:.1f} kJ/kg K"), ("A18", "Latent heat water (A) / ethanol (D, CoolProp)", f"{a['lam_w']:.0f} / {a['lam_e']:.1f} kJ/kg"),
             ("A19", "LP steam latent heat", f"{a['lam_st']:.0f} kJ/kg"), ("A20", "Heat released by fermentation (no source)", f"{a['dh_ferm']:.0f} kJ/mol glucose"),
             ("A21", "Evaporator effects; economy (range 2.5-3.0)", f"{a['n_eff']}; {a['econ']:.1f}"), ("A22", "Dryer thermal efficiency (no source)", f"{100*a['eta_dry']:.0f} %"),
             ("A23", "Stream T and P, beer preheat 80 C", "see table"), ("A24", "No backset recycle, no direct steam, lees ethanol-free", "-"),
             ("A25", "Enzymes, yeast, nutrients, antifoam neglected", "-")]
    y = wtable(s, 1140, y + 4, [34, 275, 130], arows, 9.5, 11, 2)
    y = section(s, 1135, y + 6, 445, "Rev A to Rev B changes")
    d_ = lambda a_, b_: f"{a_:,.0f}->{b_:,.0f}"
    yAg = rA["grain_t_yr"]; yBg = r["grain_t_yr"]
    chg = [("Item", "Rev A", "Rev B", "Source and effect"),
           ("A11 Y", "0.90", f"{a['Y']:.2f}", f"BioSTEAM corn: 0.930 (tool, D); ANL 2.81 gal/bu: >= 0.916; EIA 2.47-2.55 kg/L: 0.88-0.91. Grain {d_(yAg, yBg)} t/yr, DDGS {tot(rA['S'][19])/rA['L_h']:.3f}->{tot(S[19])/L:.3f} t/KL, steam {rA['steam_kg_per_L']:.2f}->{r['steam_kg_per_L']:.2f} kg/L. Closure 0.00 %"),
           ("A16 R", "3.0", f"{a['RR_rect']:.1f}", f"NRTL McCabe-Thiele (D): Rmin 2.71; 66 ideal stages at 3.0, 39 at 3.5. E-103 {DA['E-103 rectifier condenser']:+,.0f}->{D['E-103 rectifier condenser']:+,.0f}, E-106 {DA['E-106 rectifier reboiler']:+,.0f}->{D['E-106 rectifier reboiler']:+,.0f} kW"),
           ("A18 L_e", "840", f"{a['lam_e']:.1f}", "CoolProp 8.0.0 at NBP 351.57 K (D, frozen). Duties move by < 1 %"),
           ("Closure", "C only", "C, H, O", "H and O added over hydrolysis + fermentation (D); all within 0.01 %"),
           ("Economy 2.5", "2.5", "2.5", f"Not changed: Dale and Tyner default 3 passes is a model default (low-medium). Range shown: 3.0 gives {sens(dict(econ=3.0))['r']['duty']['EV-101 evaporator (steam)']:+,.0f} kW"),
           ("Fermenters", "not set", f"N = {SIZ['geom'].get('N', '?')}", "tau 60 h, V_wf 0.83 (BioSTEAM SSF defaults) + A turnaround; sizes PVRV-201 (sheet 6)"),
           ("Steam note", "none", "box above", "ANL, Dale and Tyner, IGL, PR, BioSTEAM; no value changed"),
           ("Sheets 5 to 9", "-", "added", "relief schedule and sizing, ESD matrix, SIFs, mitigation, HAZID, ISD; devices added on sheet 1")]
    yr = wtable(s, 1140, y + 2, [62, 38, 40, 300], chg, 9, 10.5, 2)
    # ---- bottom strip: S and D lists
    y0 = yl + 8
    y = section(s, 20, y0, 548, "Sourced values (S)")
    srows = [("Tag", "Item", "Source or formula"),
             ("S1", "Capacity 100 KLPD, 330 d, 33,000 KL/yr; route; grain 86,800 and DDGS 26,000 t/yr (cross-check only)", "VertiStrat_DPR_Templates/Template_DPR_Ethanol_Grain_100KLPD.docx, sections 1, 4, 7, 9"),
             ("S2", "Grain 2.465 / 2.553 kg/L; DDGS 0.609 / 0.700 t/KL; CO2 0.763 / 0.740 t/KL; steam 6.6 / 5.04 kg/L; water 6.49 L/L", "EIA documents: India Glycols PFR 200 KLD (Apr 2022 tables 06, 09); Pernod Ricard Nashik and Veer Vallabh Green exec. summaries (MPCB 2024-05, 2025-12); URLs in ETHANOL_comparisons.csv"),
             ("S3", "Yield 2.81 gal/bu denatured; DDGS 5.9 dry lb/gal (4.7-8.1); steam 14.47 lb/gal; 36.7 % DDGS sold wet", "M. Wu, Argonne for RFA, Analysis of the Efficiency of the U.S. Ethanol Industry 2007 (2008), Tables 3, 4, 6"),
             ("S4", "Default 3 evaporation passes; shares distillation 32 %, drying 27.5 %, evaporation 26.4 %; 36,000 Btu/gal (1998)", "Dale and Tyner, Purdue Staff Paper 06-04 (2006), Energy Balance section"),
             ("S5", "Corn 61.2 % starch, 15 % moisture; SSF yield 0.95 on glucose, rest to yeast; tau 60 h, V_wf 0.83; DDGS 0.560 kg dry/L; oil 0.036 kg/L", "BioSTEAM 2.54.0 / biorefineries 2.35.1 corn model run (TOOLS_SURVEY 2a, bst_corn_detail.py). Tool default, not a plant measurement"),
             ("S6", "Rmin 2.71, stages 66/48/39/31 at R 3.0/3.25/3.5/4.0; k of vapours; ethanol latent heat 849.8 kJ/kg", "rect_check.py: thermo 0.6.1 NRTL (ChemSep IPs), CoolProp 8.0.0, scipy; frozen above (FROZEN)")]
    drows2 = [("Tag", "Derived quantity", "Formula (molar masses from atomic masses C 12.011, H 1.008, O 15.999 g/mol)"),
              ("D1", f"Product P = {PROD_M3_H:.4f} m3/h x A1 = {r['P']:,.0f} kg/h", "100 KLPD / 24 h; ethanol net = A2 x P"),
              ("D2", f"Sieve split: regen = {r['Rg']:,.0f} kg/h", "Rg = P (x_prod - x_hyd) / (x_hyd - x_regen); F10 = P + Rg"),
              ("D3", f"Beer ethanol {r['E8']:,.0f} kg/h", "E8 = E_prod / (1 - A6); overhead water = ethanol x (1 - A5) / A5"),
              ("D4", f"Glucose fermented {r['G_ferm']:,.0f} kg/h; CO2 {r['CO2']:,.0f} kg/h", f"G = E8 / (2 M_EtOH / M_Glu), M_EtOH {M_ETOH:.2f}, M_Glu {M_GLU:.2f}, M_CO2 {M_CO2:.2f}; CO2 = G x 2 M_CO2 / M_Glu"),
              ("D5", f"Starch {r['starch']:,.0f} kg/h, grain {r['grain']:,.0f} kg/h", f"starch = G / A11 x M_AGU / M_Glu (M_AGU {M_ANH:.2f}); grain = starch / A7; water of hydrolysis = glucose - starch"),
              ("D6", "Decanter, evaporator, dryer", "cake = A12 x solids / A13; syrup solids / A14; DDGS = solids / (1 - A15); ethanol follows the liquid phase"),
              ("D7", "Duties", "m cp dT or m x latent heat; E-106 = condenser duty - lees x latent heat; EV-101 = evaporated water / economy x latent heat of steam")]
    wtable(s, 20, y + 2, [28, 270, 250], srows, 9, 10.5, 2)
    y = section(s, 1135, yr + 8, 445, "Derivations (D)")
    wtable(s, 1140, y + 2, [28, 150, 262], drows2, 9, 10.5, 2)
    return s


# ---------------------------------------------------------------------------------------------------------------------
# safety design basis sheets 5 to 9
# ---------------------------------------------------------------------------------------------------------------------
SRC = ("Sources: S1 HSE HSG176 (2015) tank storage; S2 HSE HSG238 control systems; S3 HSE COMAH plant layout; S4 EIGA Doc 15/21; S5 OSHA 29 CFR 1910.119; S10 CSB BP-Husky; S11 CSB Kuraray; "
       "S12 HSE/IChemE Hazards 33 (digesters); S19 LOPA/SIL snippets only. R = required or recommended by a named free source; A = assumed here; gap = standard not obtained "
       "(NFPA 30/68/11/15, API 520/521/2000/2350/650, IEC 61511, IEC 60079, OISD-STD-116/117/118/144, BIS, PESO, IBR boiler code).")


def sheet5(r):
    s = hdr_sheet(5, "Safety design basis 1: relief schedule", f"5 of {TOTAL}: relief schedule, every pressure item on sheet 1")
    rows = [("Item", "Service", "Design pressure basis (A)", "Relief case(s) considered", "Device (sheet 1)", "Discharge destination", "Sizing status"),
            ("SL-101", "Grain silo, dust", "atmospheric", "primary dust explosion; overfilling with dust cloud", "XP-101 vent panel", "outdoors via duct, safe area (A)", "not sized: needs Kst, Pmax of grain dust and silo volume (NFPA 68 paywalled: gap)"),
            ("ML-101", "Hammer mill and dust collector", "atmospheric", "dust explosion in mill or collector; tramp-metal spark", "XP-102 + isolation, magnet (A)", "safe area (A)", "not sized: same data needed"),
            ("V-101", "Slurry tank, 30 to 60 C", "atmospheric", "overfill; no pressure source", "VT-101 open vent", "atmosphere, overflow to drain (A)", "no relief device: open vent. Overflow line to drain to be confirmed"),
            ("V-102", "Liquefaction tank, 85 C", "atmospheric", "overfill; steam injection not used (H-101 indirect, A)", "VT-102 open vent", "atmosphere via hood (A)", "no relief device: open vent"),
            ("V-103", "Saccharification tank, 60 C", "atmospheric", "overfill", "VT-103 open vent", "atmosphere via hood (A)", "no relief device: open vent"),
            ("F-101A..n", "Fermenters, CO2 and foam", "design 0.35 barg and vacuum rating (A); set 0.2 barg (A)", "blocked CO2 header or scrubber; foam carry-over; vacuum on cooling or CIP; fire. Loss of cooling lowers CO2 rate: no overpressure case", "PVRV-201 (pressure / vacuum)", "SC-101 scrubber, then VH-101 / ST-101 (A)", "blocked header sized on sheet 6; foam, vacuum and fire not sized: need foam model, vessel geometry, vacuum rating"),
            ("SC-101", "CO2 scrubber, packed", "design 0.35 barg (A)", "blocked vent; foam carry-over from fermenters", "none of its own: protected by PVRV-201 on the common header (reason)", "-", "reason: no isolation valve between fermenter vent and scrubber (A); confirm in detail design"),
            ("V-104", "Beer well, 33 C", "atmospheric", "overfill; ethanol vapour in head space", "vent to SC-101 header (A)", "SC-101", "no relief device: vented"),
            ("H-101", "Slurry heater, LP steam", "tube side steam, shell slurry (A)", "tube rupture (steam into slurry); thermal expansion", "none drawn: slurry side open through V-101/V-102", "-", "open: decide design pressure of slurry side or add a PSV; needs steam pressure (A)"),
            ("H-102/H-103", "Mash coolers, CW", "CW side (A)", "blocked-in CW side heated by mash; tube rupture CW to mash (open side)", "none drawn: no isolation valves on CW side (A)", "-", "reason stated; confirm no block valves in detail design"),
            ("E-101", "Beer preheater, hot stillage", "beer side (A)", "blocked-in thermal expansion of beer or stillage", "TSV-103", "to V-104 or closed drain (A)", "not sized: needs blocked-in volume and heat input"),
            ("C-101", "Beer column, 1.3 bar abs, 95 to 104 C", "design 2.0 barg, set 1.5 barg (A)", "blocked overhead; steam control valve failure; loss of feed; fire; vacuum on steam trip", "PSV-301 + PAHH-301 / XV-301A (SIF-5)", "VH-101 / ST-101 (A)", "blocked overhead sized (sheet 6); fire and vacuum not sized: need diameter, height, holdup"),
            ("E-102", "Beer column reboiler, LP steam", "steam side (A)", "tube rupture: steam into column; thermal expansion", "covered by PSV-301 (reason)", "VH-101", "reason: LP steam pressure below column set pressure is required (A, to check)"),
            ("C-102", "Rectifier, 1.2 to 1.4 bar abs", "design 2.0 barg, set 1.5 barg (A)", "loss of E-103 cooling or reflux; blocked overhead; reboiler overheating; fire; vacuum", "PSV-302 + PAHH-302 / XV-301B (SIF-5)", "VH-101 / ST-101 (A)", "loss of condenser sized (sheet 6); fire, vacuum not sized: need dimensions, trays 39 ideal (D)"),
            ("E-103", "Rectifier condenser, CW", "CW side (A)", "blocked-in CW side; tube rupture CW to ethanol side", "TSV-101; tube rupture covered by PSV-302 (A)", "closed drain (A)", "not sized: needs blocked-in volume"),
            ("E-106", "Rectifier reboiler, LP steam", "steam side (A)", "tube rupture; thermal expansion", "covered by PSV-302 (reason)", "VH-101", "as E-102"),
            ("MS-101A/B", "Molecular sieve beds, swing, vapour S10", "design 2.0 barg, set 1.5 barg (A)", "blocked outlet; regeneration heating or vacuum; bed fire (adsorbent heat); valve mis-position between beds", "PSV-303", "VH-101 / ST-101 (A)", "blocked outlet sized (sheet 6); regeneration vacuum and bed fire not sized: need bed volume, adsorbent data"),
            ("E-104", "Product cooler, CW", "product side (A)", "thermal expansion with XV-404 closed", "TSV-102", "T-101 vapour space or closed drain (A)", "not sized: needs blocked-in volume"),
            ("T-101", "Day tank, anhydrous ethanol", "atmospheric, 0.07 barg (A)", "normal breathing; fire; overfill (SIF-2); vacuum on pump-out", "PVRV-402 + flame arrestor; emergency vent by weak roof seam (A)", "atmosphere at safe elevation (A)", "normal and fire vent flow sized (sheet 6); device capacities not selected (vendor)"),
            ("T-201A/B", "Fuel ethanol storage", "atmospheric, 0.07 barg (A)", "normal breathing; fire; overfill (SIF-1); vacuum on tanker loading", "PVRV-401 + flame arrestor + EVH-401 or frangible roof joint", "atmosphere at safe elevation (A)", "normal and fire vent flow sized (sheet 6); capacities not selected (vendor)"),
            ("DC-101", "Decanter, hot stillage", "atmospheric (A)", "hot stillage release; steam flash", "vapour hood to ETP vent (A), no device", "ETP vent (A)", "no relief device: atmospheric (reason)"),
            ("EV-101", "Evaporator, 3 effects, vacuum", "full vacuum rating (A); shell 1.5 barg (A)", "tube rupture steam to vacuum side; loss of vacuum; vapour blocked", "PSV-401", "VH-101 / ST-101 (A)", "not sized: needs effect volumes and steam pressure"),
            ("E-105", "Evaporator condenser, CW", "CW side (A)", "blocked-in CW side", "none drawn (no isolation valves, A)", "-", "reason stated"),
            ("D-101", "DDGS dryer, steam-tube rotary", "atmospheric (A)", "smouldering, dust explosion, steam tube rupture, overheating", "DL-501 deluge, XV-501, TAHH-501; explosion venting via XP-501/502", "outdoor safe area (A)", "not sized: needs Kst, Pmax, volume (NFPA 68 paywalled: gap)"),
            ("CY-101/BF-101", "Cyclone and bag filter, dust", "atmospheric (A)", "dust explosion; flame propagation to silo", "XP-501, XP-502, RV-501 isolation", "outdoor safe area (A)", "not sized: same"),
            ("SI-501", "DDGS silo", "atmospheric (A)", "smouldering; dust explosion", "XP-503; temperature / CO monitoring", "outdoor safe area (A)", "not sized: same"),
            ("B-101", "Steam boiler, fuel open", "boiler code design (gap)", "boiler overpressure, low water", "statutory boiler safety valves; PSV-501 on LP steam header", "safe location, VH-101 (A)", "gap: boiler code (IBR / ASME I) not obtained; header PSV not sized: needs boiler capacity and PRV"),
            ("CT-101", "Cooling tower", "atmospheric", "none credible", "none", "-", "no relief device (reason)")]
    cw = [95, 185, 185, 305, 230, 185, 375]
    y = wtable(s, 20, 90, cw, rows, 10, 12, 2)
    y = y + 8
    R(s, 20, y, 1100, 8, "none", "none")
    note_lines(s, 24, y + 8, ["Relief destination: 'to VH-101 / ST-101' is a single named closed header and stack (drawn on sheet 1); its height, flare or scrubber need and radiation / dispersion at grade are not quantified (open). "
                              "CSB Kuraray (S11) shows the discharge location is itself a design item.",
                              "Design and set pressures are A. Accumulation 10 % non-fire used for single valves (module relief). Devices marked 'covered by' are justified by the reason shown, not by a calculation.",
                              SRC], 220, 9.5, 12)
    return s


def sheet6(r, sz):
    s = hdr_sheet(6, "Safety design basis 2: relief sizing results and frozen tool outputs", f"6 of {TOTAL}: sizing with process_safety (API 520-I, API 2000 5th ed.)")
    if not sz["ok"]:
        T(s, 24, 120, "process_safety package not importable: " + sz.get("err", ""), 12, 700, fill=RED); return s
    rows = [("Device / case", "Scenario", "Inputs (A unless D)", "Result", "Method and caveat")]
    for tag, case, inp, res_, note, _ in sz["rows"]: rows.append((tag, case, inp, res_, note))
    cw = [90, 245, 440, 195, 590]
    y = wtable(s, 20, 90, cw, rows, 10.5, 13, 2)
    g = sz["geom"]
    y = section(s, 20, y + 10, 1100, "Derived geometry and bund volume (D from A inputs)")
    gr = [("Item", "Value", "Basis"),
          ("Fermenters", f"N = {g['N']}, gross {g['Veach']:,.0f} m3 each ({g['Vgross']:,.0f} m3 total)", f"mash {g['Qmash']:,.1f} m3/h x (60 + 4) h / 0.83 / max 700 m3 each"),
          ("T-201A/B", f"2 x {g['T-201A/B']['V']:,.0f} m3; wetted {g['T-201A/B']['Aw']:,.0f} m2", "7 d storage = 700 m3 (A); D 8.0 m x H 7.5 m (A)"),
          ("T-101", f"{g['T-101']['V']:,.0f} m3; wetted {g['T-101']['Aw']:,.0f} m2", "1 d of product (A); D 4.5 m x H 6.3 m (A)"),
          ("BD-401 bund", f"{g['bund']['V']:,.0f} m3 minimum", f"max(110 % of largest tank = {g['bund']['by_largest']:,.0f} m3, 25 % of total {g['bund']['Vt']:,.0f} m3 = {g['bund']['by_total']:,.0f} m3); S1 para 157 (R). Rain and fire-water allowance: gap")]
    y = wtable(s, 20, y, [160, 380, 560], gr, 10.5, 13, 2)
    y = section(s, 20, y + 10, 1100, "Frozen tool outputs used on this set (commands in the generator source, section FROZEN)")
    y = note_lines(s, 26, y + 14, [
        f"Rectifier (thermo 0.6.1 NRTL, CoolProp 8.0.0): Rmin {FROZEN['Rmin_tangent']} (tangent pinch; {FROZEN['Rmin_q']} q-line); ideal enriching stages {FROZEN['N_R30']} at R 3.0, {FROZEN['N_R325']} at 3.25, {FROZEN['N_R35']} at 3.5, {FROZEN['N_R40']} at 4.0. Rev B R = 3.5 (R/Rmin 1.29). Tray efficiency not set: A.",
        f"Vapour k (ideal gas, CoolProp Cp0molar): 50 wt % ethanol vapour {FROZEN['K_S9']}, 94 wt % {FROZEN['K_S10']}, CO2 {FROZEN['K_CO2']}. Ethanol latent heat {FROZEN['lam_e']} kJ/kg at {FROZEN['T_nbp_e']} K.",
        f"BioSTEAM 2.54.0 corn model: overall yield {FROZEN['bst_overall_Y']} of theoretical on starch (SSF {FROZEN['bst_ssf_yield']} on glucose, remainder to yeast), DDGS {FROZEN['bst_ddgs_dry']} kg dry/L, crude oil {FROZEN['bst_oil_kgL']} kg/L recovered separately, thermal {FROZEN['bst_thermal_MJL']} MJ/L. DWSIM was not available and no DWSIM result is claimed."], 200, 10.5, 13)
    note_lines(s, 26, y + 6, ["Not sized anywhere: fires on columns, beds, fermenters (need vessel dimensions); foam-over (needs foam model); tube-rupture flows; thermal-expansion valves (need blocked-in volume); dust explosion vents (need Kst, Pmax and NFPA 68 or EN 14491, not obtained); "
                              "vacuum cases; flare or stack radiation. The package states API 2000 5th ed. results need checking against the current edition; API 520/521 text was not read for this sheet (owner copy per ledger)."], 200, 10.5, 13)
    return s


def sheet7(r):
    s = hdr_sheet(7, "Safety design basis 3: ESD cause-and-effect matrix and SIF list", f"7 of {TOTAL}: ESD matrix, SIFs (SIL assumed, not verified)")
    fe = ["XV-401", "XV-402", "XV-404", "XV-301A", "XV-301B", "XV-201", "XV-501", "P-102", "P-103", "DL-501", "FW/FC-401"]
    cw = [300] + [56] * len(fe) + [330, 300]
    ce = [("Initiator (all on sheet 1)", *fe, "Voting (A)", "Source"),
          ("GD-401 / GD-402 / GD-301 / GD-302 flammable gas high-high", "C", "C", "C", "C", "C", "", "", "T", "T", "", "", "2oo4 on any two (A)", "R S4 S8 (principle); gap IEC 60079-29"),
          ("FD-401 flame, or manual ESD-1", "C", "C", "C", "C", "C", "", "", "T", "T", "", "S", "1oo2 FD / manual (A)", "R S5 (ESD procedures)"),
          ("LAHH-401 T-201A/B high-high level (SIF-1)", "", "C", "", "", "", "", "", "", "T", "", "", "1oo1 (A), independent of LIC-401", "R S1 para 137"),
          ("LAHH-402 T-101 high-high level (SIF-2)", "", "", "C", "", "", "", "", "", "", "", "", "1oo1 (A), independent", "R S1 para 137"),
          ("LSHH-201 fermenter foam / level (SIF-4)", "", "", "", "", "", "C", "", "", "", "", "", "1oo1 (A)", "A"),
          ("PAHH-301 C-101 top pressure (SIF-5)", "", "", "", "C", "", "", "", "", "", "", "", "1oo1 (A)", "A (S2 separation)"),
          ("PAHH-302 C-102 top pressure (SIF-5)", "", "", "", "", "C", "", "", "", "", "", "", "1oo1 (A)", "A (S2 separation)"),
          ("TAHH-501 / SD-501 dryer exhaust temperature or spark / CO (SIF-6)", "", "", "", "", "", "", "C", "", "", "S", "", "TAHH 1oo1; SD-501 start deluge on confirmed spark (A)", "A"),
          ("GD-201 CO2 high (fermenter hall, low level)", "", "", "", "", "", "", "", "", "", "", "", "alarm and ventilation only; no trip (A)", "A; gap: toxic limits not obtained"),
          ("Loss of instrument air or power", "C", "C", "C", "C", "C", "C", "C", "T", "T", "", "", "fail-safe positions", "R S1 para 128")]
    y = table(s, 20, 90, cw, ce, 24, 10.5, True, True)
    T(s, 24, y + 14, "C = close (fail-closed, spring-return), T = trip, S = start. Fail position: XV all fail closed (steam, product, mash); DL-501 and FW/FC-401 fail to no-action and start on a signal (A). Blank = no action.", 10)
    rows = [("SIF", "Function", "Initiator -> final element", "Hazard and demand source", "Independent protection layers credited (none quantified)", "SIL target (A)", "Free source"),
            ("SIF-1", "T-201A/B overfill", "LAHH-401 -> trip P-103, close XV-402", "Overfill of the product tank. Demand: operator error or LIC-401 failure; frequency not set (IOGP 434-01 owner copy, not re-read)", "LIC-401 alarm and operator response (A); PVRV-401 vent; bund BD-401", "SIL 1 (A)", "S1 para 137; S2"),
            ("SIF-2", "T-101 overfill", "LAHH-402 -> close XV-404", "Overfill of the day tank. Demand as SIF-1", "level alarm and operator response (A); PVRV-402; bund", "SIL 1 (A)", "S1 para 137"),
            ("SIF-3", "Flammable release", "gas / flame / manual -> ESD-1 (matrix)", "Pool and flash fire at the tank farm, sieve area or pumps. Demand: leaks from seals and flanges (IOGP 434-01 hole-size frequencies, S15)", "detection with alarm, bund, ignition-source control (area classification not done), fire water and foam (gap)", "SIL 2 (A)", "S5; S4 (detect); S10 (credit only what is independent)"),
            ("SIF-4", "Fermenter foam-over", "LSHH-201 -> close XV-201", "Foam to the vent, loss of CO2 scrubbing, overpressure. Demand: antifoam failure", "LSH-201 alarm, AF-201 dosing, PVRV-201", "SIL 1 (A)", "A"),
            ("SIF-5", "Column overpressure", "PAHH-301 / 302 -> close XV-301A / B", "Overpressure of C-101 or C-102, release of hot ethanol vapour. Demand: steam valve or cooling failure", "TIC-302 / 303 control, PSV-301 / 302 (credited only for the residual)", "SIL 1 (A)", "S2 para 32-34; S10"),
            ("SIF-6", "Dryer fire", "TAHH-501 / SD-501 -> close XV-501, stop feed, start DL-501", "Smouldering or dust fire in the dryer. Demand: hot spot in DDGS", "TIC-501 control, housekeeping, explosion vents (do not prevent fire)", "SIL 1 (A)", "A; dust data gap")]
    y = wtable(s, 20, y + 40, [60, 150, 280, 330, 340, 90, 215], rows, 10.5, 13, 2)
    note_lines(s, 24, y + 8, ["No SIL verification is claimed: IEC 61511 and a LOPA text were not obtained (S19 snippets only), so the targets are labelled A. HSG238 (S2) supports separating protection from control and deriving integrity from a risk analysis; "
                              "BP-Husky (S10) shows credited safeguards must be independent and tested. Proof-test intervals, architecture and PFDavg are not set."], 200, 10.5, 13)
    return s


def sheet8(r, sz):
    s = hdr_sheet(8, "Safety design basis 4: detection, mitigation and inherently safer design", f"8 of {TOTAL}: F&G, isolation, bund, distances, fire water, ventilation, ISD")
    g = sz["geom"] if sz.get("ok") else {}
    rho_rel = lambda M: M / 28.96
    bund = g.get("bund", {})
    rows = [("Topic", "Basis for this plant", "Status", "Source"),
            ("Gas detection (ethanol)", f"Ethanol vapour is {rho_rel(M_ETOH):.2f} times air density (D, M/28.96): detectors at low level at pump seals (P-102, P-103), sieve manifold, tank bund sump and column bases. Voting 2oo4 to ESD-1 (A). Tags GD-301, GD-302, GD-401, GD-402.", "A; detector type and alarm levels: gap (IEC 60079-29, OISD)", "S4 and S8 give the principle for gas detection (hydrogen / fertilizer guidance)"),
            ("Gas detection (CO2)", f"CO2 is {rho_rel(M_CO2):.2f} times air density (D): GD-201 at floor level in the fermenter hall and pits, alarm and ventilation, entry control. CO2 rate {tot(r['S'][7]):,.0f} kg/h (D).", "A; toxic and asphyxiant limits: gap, not obtained", "A"),
            ("Flame detection", "FD-401 line of sight over T-101, T-201A/B and the pump area. Ethanol flames are pale: detector type must suit alcohol (vendor).", "A", "S4: flames hard to see, leak detection to supplement (hydrogen)"),
            ("Isolation of large inventories", "XV-402 (T-101 outlet), XV-401 (T-201A/B outlet), XV-404 (product inlet to T-101), XV-301A/B (reboiler steam): remotely operated, fail closed, power-independent action.", "R (drawn)", "S1 para 128"),
            ("Bund / dyke", f"BD-401 around T-101 and T-201A/B: capacity not less than the larger of 110 % of the largest tank and 25 % of total tank capacity = {bund.get('V', 0):,.0f} m3 (D from A tank sizes); drain valve DV-401 closed in service; rainwater allowance and fire-water holding: gap.", "R rule, A volumes", "S1 para 157"),
            ("Safety distances", "T-201A/B are above 250 m3 (A): HSG176 Table 1 distance for that band is 15 m to boundary, buildings and fixed ignition sources (R). T-101 (100 m3) falls in an intermediate band: read Table 1. Tank-to-tank spacing, columns, dryer and boiler distances: gap (NFPA 30, OISD-STD-118, not obtained). Domino escalation and occupied buildings must be addressed in layout.", "R for one band, gap for the rest", "S1 Table 1; S3"),
            ("Fire water and foam", "FW-401 cooling ring and monitors, FC-401 foam chamber on T-201A/B. Foam must suit a polar (water-miscible) liquid: alcohol-resistant type (A). Application density, duration and fire-water capacity: not set; process_safety/fire_water.py takes these as inputs.", "A; gap: NFPA 11 / 15 / 30, OISD-STD-116 / 117 not obtained", "A"),
            ("Ventilation and inerting", "Fermenter hall natural or forced ventilation with low-level CO2 detection (A). Tank vapour spaces are not inerted (A); inerting of the sieve-bed regeneration loop is an option for the licensor. Dust areas: housekeeping and extraction at ML-101.", "A", "S12 (ventilation failures as incident cause, digesters)"),
            ("Area classification and ignition control", "Flammable liquid zones around pumps, tank vents (PVRV-401, PVRV-402), columns, sieve beds; dust zones at ML-101, D-101, CY-101, BF-101, SI-501. Not done here.", "gap: IEC 60079-10, API 505, OISD not obtained", "-"),
            ("Dryer and dust protection", "Explosion venting XP-501 / 502 / 503, isolation RV-501, spark / CO detection SD-501, deluge DL-501, housekeeping, no direct-fired heater (steam tube, A). Vent areas need Kst and Pmax of DDGS dust.", "A; vent sizing gap (NFPA 68)", "S5 (process safety information includes dust data)")]
    y = wtable(s, 20, 90, [150, 600, 200, 150], rows, 10.5, 13, 2)
    y = section(s, 20, y + 10, 1100, "Inherently safer design options for this process (qualitative; effect numbers are D from the HMB where shown)")
    rd = r["duty"]["D-101 dryer (steam/hot air)"]
    isd = [("No.", "Option", "Effect", "Source"),
           ("ISD-1", "Substitute: keep molecular-sieve dehydration (no benzene or cyclohexane entrainer, no toxic solvent inventory).", "Already in the process route; keep.", "S1 sheet 1 process route (template section 4)"),
           ("ISD-2", f"Reduce inventory: size T-101 for hours, not one day ({g.get('T-101', {}).get('V', 0):,.0f} m3 as drawn, A), or send product straight to T-201A/B.", "Removes one flammable inventory and one bund compartment.", "A"),
           ("ISD-3", "Moderate conditions: run the columns at the lowest pressure that the condenser allows; beer column under vacuum would allow lower-pressure steam and a smaller overpressure case.", "Lower relief loads; costs a vacuum system (not assessed).", "A"),
           ("ISD-4", f"Dryer: sell wet cake / syrup (DWGS) instead of DDGS, or dry only part. The dryer is {100*rd/r['steam_kW']:.0f} % of LP steam (D) and the only dust-explosion source after the mill; US plants sell 36.7 % of DDGS wet.", f"Removes up to {rd:,.0f} kW of the {r['steam_kW']:,.0f} kW steam (D) and the dryer, cyclone and silo dust hazard; market for wet cake is a business question.", "S3 ANL Table 3 (36.7 %)"),
           ("ISD-5", "Simplify CO2 handling: vent fermenter CO2 outdoors through the scrubber, keep fermenters in the open or in a ventilated shed with no pits.", "Removes the low-level asphyxiant accumulation case.", "A"),
           ("ISD-6", "Limit mill dust: enclosed mill with dust collector outside the building, explosion vent to a safe area.", "Removes the building as a confinement for a dust explosion.", "A")]
    wtable(s, 20, y, [50, 520, 380, 150], isd, 10.5, 13, 2)
    return s


def sheet9(r):
    s = hdr_sheet(9, "Safety design basis 5: hazard identification table (HAZOP-style nodes)", f"9 of {TOTAL}: nine nodes, qualitative; actions for the owner")
    rows = [("Node", "Deviation", "Cause", "Consequence (qualitative)", "Safeguards on sheet 1", "Action"),
            ("N1 Grain, silo, mill (SL-101, ML-101)", "dust cloud with ignition source", "tramp metal, bearing heat, static, poor housekeeping", "primary and secondary dust explosion; building damage", "XP-101, XP-102, magnet (A), dust extraction", "Get Kst, Pmax, MIE for the grain; dust hazard analysis; area classification (gap)"),
            ("N2 Slurry, liquefaction, saccharification (V-101..V-103, H-101)", "high temperature; tube rupture; overflow", "TIC-101 failure; steam tube leak; level control absent", "scalding, overflow of hot mash; steam into slurry", "TIC-101 / TV-101, VT-101..103 open vents", "Decide slurry-side design pressure vs H-101 steam pressure; overflow routing"),
            ("N3 Fermentation (F-101A..n, SC-101)", "more CO2 than vent capacity; foam; no vent flow; vacuum", "foam, blocked header or scrubber, antifoam failure, cooling or CIP vacuum", "overpressure or vacuum collapse; foam-over; CO2 in low spots: asphyxiation", "LSH-201, LSHH-201 -> XV-201, AF-201, PVRV-201, TIC-201, GD-201, scrubber and stack", "Foam model; per-vessel CO2 rate; stack height and CO2 dispersion; confined-space rules"),
            ("N4 Beer column (C-101, E-102)", "high pressure; high temperature; loss of feed", "steam valve fails open, blocked S9, feed pump trip", "overpressure, ethanol vapour release at VH-101, flooding", "TIC-302, PAHH-301 -> XV-301A, PSV-301, GD-301", "Fire-case sizing needs vessel data; decide destination of VH-101"),
            ("N5 Rectifier and sieve (C-102, MS-101A/B, E-103, E-106)", "loss of cooling or reflux; bed breakthrough; wrong valve sequence", "CW loss, reflux pump trip, bed valve fault, regeneration fault", "overpressure to VH-101; off-spec product; hot ethanol vapour leak", "TIC-303, PAHH-302 -> XV-301B, PSV-302, PSV-303, AT-401, GD-302", "Stage count and tray efficiency (39 ideal, D); bed valve interlocks; regeneration vacuum case"),
            ("N6 Product cooler and tanks (E-104, T-101, T-201A/B)", "high level; leak; fire", "LIC failure, transfer error, seal or flange leak, ignition", "overfill, bund pool fire, tank fire, escalation to neighbour", "LAHH-401/402, XV-401/402/404, BD-401, PVRV-401/402 + flame arrestors, EVH-401, FD/GD, FC-401, FW-401", "Confirm bund volume, spacing, fire-water and foam rates (standards not obtained)"),
            ("N7 Stillage, decanter, evaporator (DC-101, EV-101)", "tube leak; loss of vacuum; hot stillage release", "tube rupture, vacuum pump trip", "steam into vacuum side; scalding; ethanol in condensate", "PSV-401, vapour hood", "Size PSV-401; vacuum breaker; ethanol in S18 to ETP"),
            ("N8 DDGS dryer, cyclone, filter, silo (D-101, CY-101, BF-101, SI-501)", "high exhaust temperature; smouldering; dust cloud", "hot spot, plugged product, static or mechanical spark", "dryer or filter fire; dust explosion; silo fire", "TIC-501, TAHH-501, SD-501, XV-501, RV-501, XP-501/502/503, DL-501", "Dust tests (Kst, Pmax, layer ignition temperature); vent areas; silo CO monitoring"),
            ("N9 Utilities (B-101, CT-101, power, air)", "loss of steam, CW, power or instrument air", "boiler trip, pump or tower failure, grid loss", "loss of condenser cooling at C-102 (overpressure); fermenter overheating; all XV fail closed", "fail-safe valve positions, PSV-501, boiler safety valves (gap)", "Loss-of-utilities study; emergency power for ESD; boiler code")]
    y = wtable(s, 20, 90, [215, 190, 250, 270, 330, 305], rows, 10.5, 13, 3)
    note_lines(s, 24, y + 10, ["Deviations follow the guideword method listed in OSHA 29 CFR 1910.119 (S5: HAZOP is a named PHA method; facility siting and five-year update are required). No numeric consequences are given: none can be derived without release rates and ethanol consequence inputs, "
                               "and no ethanol property or scenario data exists in process_safety/data (CLAUDE.md rule: nothing invented).", SRC], 200, 10.5, 13)
    return s


# ---------------------------------------------------------------------------------------------------------------------
# results table (CSV) and main
# ---------------------------------------------------------------------------------------------------------------------
def results_rows(r, rA):
    S = r["S"]; SA = rA["S"]; L = r["L_h"]; LA = rA["L_h"]
    dev = lambda v, ref: 100 * (v - ref) / ref
    def row(metric, a_, b_, ref, ref_txt, status):
        da = dev(a_, ref) if ref else float("nan"); db = dev(b_, ref) if ref else float("nan")
        return [metric, f"{a_:.5g}", f"{b_:.5g}", ref_txt, f"{da:+.1f}" if ref else "", f"{db:+.1f}" if ref else "", status]
    DD = lambda x, xL: tot(x["S"][19]) / xL
    out = [["metric", "Rev A", "Rev B", "reference", "dev_before_pct", "dev_after_pct", "status"]]
    out.append(row("grain kg/L (IGL)", rA["grain"] / LA, r["grain"] / L, REFS["igl_grain"], f"{REFS['igl_grain']} kg/L India Glycols PFR", "agrees; moves from +0.7 to -2.6 %, inside 10 %; Y is A with range 0.88-0.95"))
    out.append(row("grain kg/L (PR)", rA["grain"] / LA, r["grain"] / L, REFS["pr_grain"], f"{REFS['pr_grain']} kg/L Pernod Ricard EIA", "slightly worse (-2.8 to -5.9 %), still inside 10 %; Indian refs favour Y 0.88-0.91, BioSTEAM/ANL favour 0.92-0.93"))
    out.append(row("ethanol L per t grain (ANL, denatured)", LA / rA["grain"] * 1000, L / r["grain"] * 1000, REFS["anl_Lt"], f"{REFS['anl_Lt']} L/t ANL 2007", "closed: -3.8 to -0.6 %"))
    out.append(row("DDGS t/KL at 10 % (VV)", DD(rA, LA), DD(r, L), REFS["vv_ddgs"], f"{REFS['vv_ddgs']} Veer Vallabh EIA", "reduced, not closed: floor 0.69 t/KL with all non-starch solids in DDGS (D); open item"))
    out.append(row("DDGS t/KL at 10 % (PR)", DD(rA, LA), DD(r, L), REFS["pr_ddgs"], f"{REFS['pr_ddgs']} Pernod Ricard EIA", "reduced, not closed"))
    out.append(row("DDGS t/KL at 10 % (ANL)", DD(rA, LA), DD(r, L), REFS["anl_ddgs_tkl"], f"{REFS['anl_ddgs_tkl']} ANL 5.9 dry lb/gal", "reduced to within 10 %: closed against ANL"))
    out.append(row("DDGS dry kg/L (ANL)", (SA[19]['glucose'] + SA[19]['solids']) / LA, (S[19]['glucose'] + S[19]['solids']) / L, REFS["anl_ddgs_dry"], f"{REFS['anl_ddgs_dry']} kg dry/L ANL", "reduced; inside ANL range 0.56-0.97"))
    out.append(row("CO2 t/KL (VV)", rA["CO2"] / LA, r["CO2"] / L, REFS["vv_co2"], f"{REFS['vv_co2']} Veer Vallabh", "unchanged: CO2 follows ethanol only (GAP_CLOSURE_BIO predicted a rise; the model shows none)"))
    out.append(row("CO2 t/KL (PR)", rA["CO2"] / LA, r["CO2"] / L, REFS["pr_co2"], f"{REFS['pr_co2']} Pernod Ricard", "unchanged, agrees"))
    out.append(row("LP steam kg/L (IGL)", rA["steam_kg_per_L"], r["steam_kg_per_L"], REFS["igl_steam"], f"{REFS['igl_steam']} India Glycols", "agrees; R 3.5 adds, Y 0.93 subtracts"))
    out.append(row("LP steam kg/L (PR)", rA["steam_kg_per_L"], r["steam_kg_per_L"], REFS["pr_steam"], f"{REFS['pr_steam']} Pernod Ricard (scope unclear)", "unchanged: no heat integration or scope data; benchmark box added"))
    out.append(row("boiler capacity kg/L (VV)", rA["steam_kg_per_L"], r["steam_kg_per_L"], REFS["vv_boiler"], f"{REFS['vv_boiler']} VV capacity incl. power", "unchanged: reference is installed capacity"))
    out.append(row("thermal MJ/L (ANL fuel)", rA["steam_kg_per_L"] * 2.1, r["steam_kg_per_L"] * 2.1, REFS["anl_thermal"], f"{REFS['anl_thermal']} MJ fuel/L ANL", "unchanged in kind: steam vs fuel, US plants sell DDGS wet; BioSTEAM 8.78 MJ/L shown"))
    out.append(row("slurry water L/L (IGL)", rA["S"][3] and tot(SA[3]) / LA, tot(S[3]) / L, REFS["igl_water"], f"{REFS['igl_water']} India Glycols", "worse, now outside 10 %: A9 slurry 30 % vs about 27.5 % implied by IGL; grain drop lowers water; A9 left unchanged (no source)"))
    out.append(row("grain t/yr (template)", rA["grain_t_yr"], r["grain_t_yr"], REFS["tmpl_grain"], "86,800 t/yr template", "template is the high figure; references support 81-84 kt/yr; Rev B is below that band at Y 0.93 (Y 0.90 gives 81.9)"))
    out.append(row("DDGS t/yr (template)", rA["ddgs_t_yr"], r["ddgs_t_yr"], REFS["tmpl_ddgs"], "26,000 t/yr template", "reduced, not closed"))
    for k, ref_txt in (("E-102 beer column reboiler", "3,453 kW CoolProp"), ("E-103 rectifier condenser", "3,162 kW CoolProp (RR 3 basis)"), ("E-106 rectifier reboiler", "1,119 kW (RR 3 basis)")):
        out.append([f"{k} kW", f"{rA['duty'][k]:.0f}", f"{r['duty'][k]:.0f}", ref_txt, "", "", "recomputed duty; R 3.5 raises condenser and reboiler (design decision, not a mismatch)"])
    out.append(["rectifier R/Rmin", f"{3.0/FROZEN['Rmin_tangent']:.2f}", f"{A['RR_rect']/FROZEN['Rmin_tangent']:.2f}", "Rmin 2.71 NRTL", "", "", "closed: 1.11 -> 1.29; 39 ideal stages (was 66)"])
    out.append(["S9 dew T C", "95", "95", "92.0 NRTL", "+3.3", "+3.3", "unchanged: 3 K superheat is A, explained"])
    out.append(["EV-101 duty kW", f"{rA['duty']['EV-101 evaporator (steam)']:.0f}", f"{r['duty']['EV-101 evaporator (steam)']:.0f}", "fixed in Rev A (lam_st)", "", "", "closed in Rev A; economy range 2.5-3.0 shown"])
    out.append(["lint: devices named but absent from sheet 1 (8)", "8", "0", "validation lint", "", "", "closed: XV-201, XV-301A/B, XV-501, GD-201, TAHH-501, LAHH-401 drawn; T-101 and MS-101A/B have devices"])
    return out


SIZ = {"geom": {}}


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/pid/ETHANOL_PID_Set_RevB.html"
    r = solve(); rA = solve(REVA)
    SIZ = sizing(r)
    sheets = [sheet1(r), sheet2(r, rA), sheet3(r), sheet4(r), sheet5(r), sheet6(r, SIZ), sheet7(r), sheet8(r, SIZ), sheet9(r)]
    for sh in sheets: frame(sh, TOTAL)
    write_html(sheets, out, "Grain ethanol 100 KLPD conceptual P&ID set, Rev B", previews="--previews" in sys.argv)
    if "--csv" in sys.argv:
        import csv
        with open(sys.argv[sys.argv.index("--csv") + 1], "w", newline="") as fh: csv.writer(fh).writerows(results_rows(r, rA))
    print(f"Closure: in {r['in']:,.0f} kg/h, out {r['out']:,.0f} kg/h, error {r['err']:.2f} %; carbon error {r['C_err']:.2f} %; "
          + "H/O " + ", ".join(f"{k} {v[2]:+.3f}%" for k, v in r["elem"].items() if k != "C"))
    if SIZ.get("ok"):
        for row_ in SIZ["rows"]: print(row_[0], "|", row_[3])

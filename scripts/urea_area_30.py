#!/usr/bin/env python3
"""Area 30 of the coal-to-urea unit-by-unit P&ID package: gasification (R-101), slag handling, syngas cooling, scrubbing, black-water and
grey-water treatment, sour-water stripping, relief / emergency depressurisation and nitrogen inerting.

Usage: python3 scripts/urea_area_30.py            (builds /tmp/area30.html and per-sheet previews /tmp/area30_s<n>.html, runs the lint)
       from urea_area_30 import build; build(pkg)  (called by the package driver)

NUMBER DISCIPLINE (tags as in pid_unit.py): S sourced, D derived (formula in this file), A assumed screening value (range stated in
docs/pid/urea_detail/AREA_30_NOTES.md).  The Rev B stream 4 (raw syngas, 1400 C) is cooled stage by stage in streams 301..309 from a
heat balance in balance() below; every unit asserts mass closure.  The ideal-gas enthalpy table and the water tables are frozen constants
produced by a CoolProp 8.0.0 run (python3.15 venv, 12 Nov 2026), tag S (tool run); they are not typed from memory.
Licensor-owned (not designed here): gasifier burner design and number, membrane-wall circuit, slag-tap and bath internals, quench geometry,
refractory/ash chemistry, start-up and shutdown sequences, relief loads.  Screening aid, not certified design."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *

AREA = "30"
# ---------------------------------------------------------------------------------------------------------------------
# 1. frozen property constants (tag S, CoolProp 8.0.0 run).  H_IG: ideal-gas H(T)-H(298.15 K), kJ/mol, on T_GRID_C.
# ---------------------------------------------------------------------------------------------------------------------
T_GRID_C = [25, 125, 225, 325, 425, 525, 625, 725, 825, 925, 1025, 1125, 1225, 1325, 1425]
H_IG = {
    'CO': [0.0, 2.922, 5.875, 8.884, 11.963, 15.116, 18.339, 21.626, 24.969, 28.362, 31.798, 35.27, 38.775, 42.307, 45.862],
    'CO2': [0.0, 3.928, 8.226, 12.823, 17.668, 22.718, 27.939, 33.304, 38.79, 44.377, 50.05, 55.796, 61.605, 67.467, 73.375],
    'H2': [0.0, 2.906, 5.828, 8.757, 11.695, 14.65, 17.627, 20.633, 23.672, 26.75, 29.869, 33.031, 36.238, 39.49, 42.785],
    'H2O': [0.0, 3.388, 6.859, 10.434, 14.122, 17.931, 21.863, 25.924, 30.112, 34.425, 38.859, 43.408, 48.063, 52.819, 57.667],
    'H2S': [0.0, 3.477, 7.11, 10.918, 14.907, 19.078, 23.426, 27.938, 32.601, 37.402, 42.325, 47.357, 52.486, 57.703, 62.996],
    'N2': [0.0, 2.917, 5.856, 8.838, 11.88, 14.988, 18.163, 21.402, 24.699, 28.047, 31.441, 34.874, 38.342, 41.841, 45.366],
}
HG25 = 2546.5   # kJ/kg, saturated vapour at 25 C: puts the ideal-gas H2O enthalpy on the steam-table scale (ideal-gas error vs real steam ~2-3 %, ignored, D)
PSAT_T_C = [100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280]
PSAT_BAR = [1.0142, 1.4338, 1.9867, 2.7028, 3.6154, 4.7616, 6.1823, 7.9219, 10.0281, 12.5524, 15.5493, 19.0767, 23.1959, 27.9709, 33.4693, 39.7617, 46.9226, 55.0299, 64.1658]
HF_KJKG = [419.2, 461.4, 503.8, 546.4, 589.2, 632.2, 675.5, 719.1, 763.1, 807.4, 852.3, 897.6, 943.6, 990.2, 1037.6, 1085.8, 1135.0, 1185.3, 1236.9]
HG_KJKG = [2675.6, 2691.1, 2705.9, 2720.1, 2733.4, 2745.9, 2757.4, 2767.9, 2777.2, 2785.3, 2792.0, 2797.3, 2800.9, 2802.9, 2803.0, 2800.9, 2796.6, 2789.7, 2779.9]
HL_COLD = [(30, 126.6), (40, 168.4), (50, 210.2), (60, 252.0), (70, 293.9), (80, 335.8), (90, 377.8)]   # compressed liquid at 10 bar, kJ/kg
SAT_P = {0.3: (69.1, 289.3, 2624.5), 1.5: (111.35, 467.1, 2693.1), 6.0: (158.83, 670.4, 2756.1), 100.0: (311.0, 1408.1, 2725.5)}   # bar: (Tsat C, hf, hg kJ/kg)
T_BFW = 200.0              # C, BFW from the area-70 HP feed-water heaters (A 150-230); enthalpy hl(T_BFW), pressure effect ignored (D)
HFG_LP4 = 2133.4           # kJ/kg latent heat at 4 bar (LP steam for the sour-water stripper reboiler)
RHO_W = {60: 983.4, 185: 883.9}   # kg/m3
RHO_STEAM_100, RHO_LIQ_100 = 55.5, 688.4   # kg/m3 saturated at 100 bar

def interp(xs, ys, x):
    if x <= xs[0]: return ys[0] + (ys[1] - ys[0]) / (xs[1] - xs[0]) * (x - xs[0])
    if x >= xs[-1]: return ys[-1] + (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) * (x - xs[-1])
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]: return ys[i] + (ys[i + 1] - ys[i]) * (x - xs[i]) / (xs[i + 1] - xs[i])

def psat(Tc): return math.exp(interp(PSAT_T_C, [math.log(p) for p in PSAT_BAR], Tc))      # bar, log-linear (D)
def t_dew(p_bar):                                                                         # inverse of psat (bisection)
    lo, hi = 100.0, 280.0
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if psat(mid) < p_bar: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi)
_HL_T = [t for t, _ in HL_COLD] + PSAT_T_C[1:]
_HL_H = [h for _, h in HL_COLD] + HF_KJKG[1:]
def hl(Tc): return interp(_HL_T, _HL_H, Tc)      # liquid water enthalpy kJ/kg (pressure effect ignored, D)
def hg_sat(Tc): return interp(PSAT_T_C, HG_KJKG, Tc)

def H_gas(sp, Tc):
    """kW: enthalpy of a gas dict {species: mol/s} at Tc relative to ideal gas at 25 C (H2O on the steam-table scale)"""
    h = 0.0
    for k, n in sp.items():
        e = interp(T_GRID_C, H_IG[k], Tc)
        if k == "H2O": e += HG25 * g.MW["H2O"] / 1000.0
        h += n * e
    return h

def gmass(sp): return sum(n * g.MW[k] for k, n in sp.items()) / 1000.0          # kg/s
def gadd(a, b, fb=1.0):
    o = dict(a)
    for k, n in b.items(): o[k] = o.get(k, 0.0) + fb * n
    return o

CP_SOLID = 1.1   # kJ/kg/K ash+char mean 1400->80 C (A, range 1.0-1.3); heat of fusion of slag ignored (A, would add 5-10 %)
def H_sol(m_kg_s, T1, T2): return m_kg_s * CP_SOLID * (T1 - T2)

# ---------------------------------------------------------------------------------------------------------------------
# 2. assumptions (tag A, ranges in the notes)
# ---------------------------------------------------------------------------------------------------------------------
P4, P301, P302, P303, P304, P309, P305 = 45.0, 44.5, 44.5, 43.0, 42.5, 42.0, 41.0   # bar: dp E-101 1.5, E-132 0.5, F-135 0.5, venturi+column 1.0
T_MIX = 900.0         # quench-zone outlet, below ash softening (A 800-950; licensor)
T_EV_PINCH = 30.0     # gas outlet of E-101 above steam saturation temperature (A 20-50)
P_DRUM = 100.0        # bar a steam drum (A 80-120)
T_ECON_OUT = 250.0    # BFW leaving the economiser, ~60 K subcooled below Tsat (A 230-280)
BLOWDOWN = 0.02       # fraction of BFW (A 0.01-0.03)
CIRC_RATIO = 8.0      # forced circulation, kg water / kg steam (A 5-15)
WALL_LOSS = 0.015     # membrane-wall heat as a fraction of coal thermal input (A 0.01-0.03)
FLY_FRAC = 0.30       # fraction of the ash/char (stream 5) leaving with the gas as fly slag (A 0.15-0.5)
FILTER_ETA = 0.97     # candle filter capture (A 0.95-0.995)
BW_SOLIDS = 0.03      # mass fraction solids in the black-water bleed (A 0.01-0.05)
T_WASH = 70.0         # grey water to the scrubber (A; follows the vacuum flash 69 C)
WASH_TOP_FRAC = 0.30  # share of the scrubber wash made with stripped sour water at the column top (A)
DT_COMP = 8.0         # K temperature rise in K-132 (A, screening)
RCP = {"slag_solids_in_slurry": 0.40, "cake_moisture": 0.25, "fines_to_overflow": 0.01}   # A: 0.3-0.6 ; 0.15-0.30 ; 0.5-3 %
T_BATH_HOT, T_BATH = 105.0, 80.0   # K-bath loop (A: 25 K rise); 80 C = Rev B stream 5 temperature (A2)
P_HP, P_LP, P_VAC = 6.0, 1.5, 0.3  # bar a flash drums (A)
CLAR_UNDER = 0.10     # clarifier underflow solids (A 0.05-0.15)
CAKE_SOLIDS = 0.55    # filter-press cake solids (A 0.45-0.65)
SOUR_OVHD_FRAC = 0.03 # SWS overhead (acid gas + vapour) as a fraction of feed (A 0.02-0.05)
SOUR_STEAM_RATIO = 0.15   # t LP steam per t feed (A 0.10-0.25)
EDV_VOL_M3, EDV_MIN = 400.0, 15.0   # gas inventory to the isolation valves; depressurisation time (A)

def balance():
    b = {}
    n4 = {k: v * K for k, v in g.S[4].items()}                 # mol/s of Rev B stream 4 x K
    dry4 = sum(v for k, v in n4.items() if k != "H2O")
    x = {k: v / dry4 for k, v in n4.items() if k != "H2O"}      # dry composition
    # ---- R-101 mass closure (Rev B streams 1,2,3 -> 4,5)
    m_in = (g.M[1] + g.M[2] + g.M[3]) * K; m_out = (gmass(n4) + g.M[5] * K)
    b["R101_resid"] = (m_out - m_in) / m_in
    assert abs(b["R101_resid"]) < 0.002, ("R-101 mass closure", b["R101_resid"])
    m5 = g.M[5] * K                                              # kg/s ash+char
    m312, m311 = FLY_FRAC * m5, (1 - FLY_FRAC) * m5
    # coal thermal input from the repo cold-gas efficiency (S) and CO+H2 HHV (S): D
    q_syn = (n4["CO"] * g.HHV_CO_KJ + n4["H2"] * g.HHV_H2_KJ)    # kW
    q_coal = q_syn / g.REPO_RUN["cge"]
    q_wall = WALL_LOSS * q_coal
    b.update(n4=n4, dry4=dry4, x=x, m5=m5, m311=m311, m312=m312, q_syn=q_syn, q_coal=q_coal, q_wall=q_wall)
    # ---- scrubber exit temperature (adiabatic saturation) with the quench-gas recycle, solved by bisection on T_out
    def point(T_out):
        y = psat(T_out) / P305; w = y / (1 - y)                  # mol H2O per mol dry gas at saturation (ideal, D)
        T301 = T_out + DT_COMP
        rec_unit = lambda T: gadd({k: v for k, v in x.items()}, {"H2O": w}) and H_gas(gadd(x, {"H2O": w}), T)   # kW per (mol/s dry)
        lhs = H_gas(n4, 1400.0) - H_gas(n4, T_MIX) + H_sol(m312, 1400.0, T_MIX)
        r = lhs / (rec_unit(T_MIX) - rec_unit(T301))             # mol/s dry recycle gas
        rec = gadd({k: r * v for k, v in x.items()}, {"H2O": r * w})
        n302 = gadd(n4, rec)
        # E-101 evaporator: gas to T_sat + pinch
        T303 = P_SAT_T + T_EV_PINCH
        q101 = H_gas(n302, T_MIX) - H_gas(n302, T303) + H_sol(m312, T_MIX, T303)
        h_ec = hl(T_ECON_OUT)
        # steam: q101 + q_wall = m_s (hg - h_ec) + m_bd (hf - h_ec), m_bd = BLOWDOWN m_bfw, m_bfw = m_s/(1-BLOWDOWN)
        hf_d, hg_d = SAT_P[100.0][1], SAT_P[100.0][2]
        m_bfw_per_ms = 1.0 / (1 - BLOWDOWN)
        den = (hg_d - h_ec) + BLOWDOWN * m_bfw_per_ms * (hf_d - h_ec)
        m_s = (q101 + q_wall) / den
        m_bfw = m_s * m_bfw_per_ms; m_bd = BLOWDOWN * m_bfw
        q_ec = m_bfw * (h_ec - hl(T_BFW))
        # E-132: gas from T303 down to T304 by q_ec (+ fly slag sensible), bisection
        lo, hi = 110.0, T303
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            dq = H_gas(n302, T303) - H_gas(n302, mid) + H_sol(m312, T303, mid)
            if dq > q_ec: lo = mid
            else: hi = mid
        T304 = 0.5 * (lo + hi)
        # F-135 (adiabatic, 5 K lost in the housing is ignored): T309 = T304
        T309 = T304
        # scrubber
        w_bw = (m311 * 0 + (1 - FILTER_ETA) * m312) / BW_SOLIDS - (1 - FILTER_ETA) * m312   # kg/s black-water water part
        n_dry_tot = dry4 + r
        n_w_out = w * n_dry_tot; n_w_in = n302["H2O"]
        dw = (n_w_out - n_w_in) * g.MW["H2O"] / 1000.0           # kg/s water evaporated into the gas (net; recycle is internal)
        n305 = {k: v * (1 if False else 1) for k, v in x.items()}
        n305 = gadd({k: n_dry_tot * v for k, v in x.items()}, {"H2O": n_w_out})
        m_wash = w_bw + dw
        h_in = H_gas(n302, T309) + m_wash * hl(T_WASH)
        h_out = H_gas(n305, T_out) + w_bw * hl(T_out)
        return dict(res=h_in - h_out, w=w, r=r, rec=rec, n302=n302, n305=n305, T301=T301, T303=T303, T304=T304, T309=T309, q101=q101, q_ec=q_ec,
                    m_s=m_s, m_bfw=m_bfw, m_bd=m_bd, dw=dw, w_bw=w_bw, m_wash=m_wash, T_out=T_out)
    global P_SAT_T
    P_SAT_T = SAT_P[100.0][0]
    lo, hi = 150.0, 235.0
    flo = point(lo)["res"]; fhi = point(hi)["res"]
    assert flo * fhi < 0, ("no sign change in scrubber balance", flo, fhi)
    for _ in range(80):
        mid = 0.5 * (lo + hi); fm_ = point(mid)["res"]
        if flo * fm_ <= 0: hi, fhi = mid, fm_
        else: lo, flo = mid, fm_
    b["sc"] = point(0.5 * (lo + hi))
    return b


# ---------------------------------------------------------------------------------------------------------------------
# 3. streams and unit balances (mass closure asserted)
# ---------------------------------------------------------------------------------------------------------------------
RHO_SOLID = 2500.0          # kg/m3 ash/char (A 2000-2800)
CYCLE_MIN = 30.0            # lock-hopper cycle (A 20-60)
SU_FRAC = 0.005             # start-up burner thermal duty as fraction of coal thermal input (A 0.003-0.01)
LHV_FUEL = 43000.0          # kJ/kg start-up liquid fuel (A, typical light distillate)
O2_PER_FUEL = 3.4 * 1.05    # kg O2 per kg fuel, near-stoichiometric hydrocarbon + 5 % (A)

def rho_w(T): return interp([60.0, 185.0], [983.4, 883.9], T)          # kg/m3 (two CoolProp points, linear, D)
def rho_gas(P_bar, T_C, mw): return P_bar * 1e5 * mw / 1000.0 / (R_GAS * (T_C + 273.15))
def rho_mix(mv, rv, ml, rl): return (mv + ml) / (mv / rv + ml / rl)
def chk(name, ins, outs, tol=1e-6):
    a, bb = sum(ins), sum(outs)
    assert abs(a - bb) <= tol * max(a, bb, 1e-9) + 1e-9, ("mass closure", name, a, bb)
    return (a - bb) / max(a, 1e-9)

def derive():
    b = balance(); s = b["sc"]; ST = {}; N = {}
    mw_of = lambda sp: gmass(sp) / sum(sp.values()) * 1000.0
    def gs(i, name, sp, T, P): return St(i, name, "gas", gmass(sp) * 3.6, round(T, 1), P, mw=mw_of(sp))
    def ls(i, name, flow, T, P, rho=None, phase="liq"): return St(i, name, phase, flow, round(T, 1), P, rho=rho if rho else rho_w(T))
    T_out = s["T_out"]
    # ---- gasifier feeds (Rev B 1, 2, 3) and raw gas 4
    ST[1] = stream(1, "coal, dense-phase", "slurry", P=50.0, rho=400.0)           # rho: A 300-450 kg/m3 dense-phase
    ST[2] = stream(2, "oxygen", "gas", P=50.0)
    ST[3] = stream(3, "HP steam to burners", "steam")
    ST[4] = stream(4, "raw syngas", "gas")
    m311, m312 = b["m311"] * 3.6, b["m312"] * 3.6
    chk("R-101 (Rev B 1+2+3 = 4+311+312, tolerance 0.2 %)", [ST[1].flow, ST[2].flow, ST[3].flow], [ST[4].flow, m311, m312], tol=0.002)
    # ---- gas train 301..309, 305..307
    n302, rec, n305, r = s["n302"], s["rec"], s["n305"], s["r"]
    y_in = n302["H2O"] / sum(n302.values()); dew = t_dew(y_in * P304)
    assert s["T304"] > dew + 15.0 and s["T303"] > dew + 15.0, ("dew-point margin", s["T304"], dew)
    N["dew302"] = dew
    ST[301] = gs(301, "quench recycle gas", rec, s["T301"], P301)
    ST[302] = gs(302, "mixed gas to E-101", n302, T_MIX, P302)
    chk("quench mix 4 + 301 = 302", [ST[4].flow, ST[301].flow], [ST[302].flow], tol=1e-9)
    ST[303] = gs(303, "gas from E-101", n302, s["T303"], P303)
    ST[304] = gs(304, "gas from E-132", n302, s["T304"], P304)
    m314 = (1 - FILTER_ETA) * m312; m313 = FILTER_ETA * m312
    chk("F-135 solids 312 = 313 + 314", [m312], [m313, m314])
    ST[309] = St(309, "gas + fines from F-135", "gas", ST[304].flow + m314, round(s["T309"], 1), P309, mw=mw_of(n302))
    ST[313] = St(313, "dry fly ash", "slurry", m313, round(s["T304"], 1), P304, rho=500.0)
    dw = s["dw"] * 3.6
    ST[305] = gs(305, "scrubbed syngas, total", n305, T_out, P305)
    chk("gas 305 = 302 + evaporated water", [ST[302].flow, dw], [ST[305].flow], tol=1e-9)
    ST[307] = gs(307, "recycle gas to K-132", rec, T_out, P305)
    n306 = {k: n305[k] - rec.get(k, 0.0) for k in n305}
    ST[306] = gs(306, "net syngas to shift (area 40)", n306, T_out, P305)
    chk("split 305 = 306 + 307", [ST[305].flow], [ST[306].flow, ST[307].flow], tol=1e-9)
    # ---- scrubber water
    m_wash = s["m_wash"] * 3.6; w_bw = s["w_bw"] * 3.6
    m330 = WASH_TOP_FRAC * m_wash; m331 = m_wash - m330
    ST[331] = ls(331, "wash water to venturi", m331, T_WASH, 46.0)
    ST[330] = ls(330, "stripped water to column top", m330, T_WASH, 46.0)
    m332 = w_bw + m314
    ST[332] = ls(332, "black water bleed", m332, T_out, P305, rho=rho_w(T_out) * 1.02)
    ST[308] = St(308, "venturi outlet, gas + water", "twophase", ST[309].flow + m331, round(T_out, 1), 0.5 * (P309 + P305),
                 rho=rho_mix(ST[305].flow, rho_gas(0.5 * (P309 + P305), T_out, mw_of(n305)), m331 + m314 - dw, rho_w(T_out)))
    chk("scrubber 309 + 331 + 330 = 305 + 332", [ST[309].flow, m331, m330], [ST[305].flow, m332], tol=1e-9)
    # ---- steam / BFW
    m_s, m_bfw, m_bd = s["m_s"] * 3.6, s["m_bfw"] * 3.6, s["m_bd"] * 3.6
    chk("BFW = steam + blowdown", [m_bfw], [m_s + m_bd], tol=1e-9)
    ST[361] = ls(361, "boiler feed water", m_bfw, T_BFW, 110.0)
    ST[360] = ls(360, "BFW from economiser", m_bfw, T_ECON_OUT, 108.0)
    ST[362] = St(362, "HP steam, saturated", "steam", m_s, SAT_P[100.0][0], P_DRUM, mw=18.015, rho=RHO_STEAM_100)
    ST[363] = ls(363, "boiler blowdown", m_bd, SAT_P[100.0][0], P_DRUM, rho=RHO_LIQ_100)
    m_c = CIRC_RATIO * m_s
    qw, q1 = b["q_wall"], s["q101"]
    m_w, m_e = m_c * qw / (qw + q1), m_c * q1 / (qw + q1)
    rho_tp = rho_mix(m_s, RHO_STEAM_100, m_c - m_s, RHO_LIQ_100)
    ST[367] = ls(367, "wall circulation water", m_w, 311.0, P_DRUM, rho=RHO_LIQ_100)
    ST[368] = St(368, "wall return, two-phase", "twophase", m_w, 311.0, P_DRUM - 2, rho=rho_tp)
    ST[369] = ls(369, "E-101 circulation water", m_e, 311.0, P_DRUM, rho=RHO_LIQ_100)
    ST[364] = St(364, "E-101 return, two-phase", "twophase", m_e, 311.0, P_DRUM - 2, rho=rho_tp)
    ST[365] = St(365, "riser return to drum", "twophase", m_c, 311.0, P_DRUM - 2, rho=rho_tp)
    ST[366] = ls(366, "downcomer water to P-134", m_c, 311.0, P_DRUM, rho=RHO_LIQ_100)
    chk("drum 365 + 360 = 362 + 363 + 366", [m_c, m_bfw], [m_s, m_bd, m_c])
    chk("circulation split 367 + 369 = 366", [m_w, m_e], [m_c])
    # ---- slag, bath, lock hopper, dewatering
    m323 = m311 / RCP["slag_solids_in_slurry"]; W0 = m323 - m311
    rho_sl = 1.0 / (RCP["slag_solids_in_slurry"] / RHO_SOLID + (1 - RCP["slag_solids_in_slurry"]) / rho_w(T_BATH))
    q_slag = H_sol(b["m311"], 1400.0, T_BATH); q_mk = W0 / 3.6 * (hl(T_BATH) - hl(T_WASH)); q_bath = q_slag + q_mk
    m321 = q_bath / (hl(T_BATH_HOT) - hl(T_BATH)) * 3.6
    ST[311] = St(311, "coarse slag to bath", "slurry", m311, 1400.0, P4, rho=RHO_SOLID)
    ST[312] = St(312, "fly slag in raw gas", "slurry", m312, 1400.0, P4, rho=RHO_SOLID)
    ST[328] = ls(328, "bath make-up water", W0, T_WASH, 50.0)
    ST[321] = ls(321, "bath water, hot", m321, T_BATH_HOT, P4)
    ST[322] = ls(322, "bath water, cooled", m321, T_BATH, P4)
    ST[323] = St(323, "slag slurry to V-102", "slurry", m323, T_BATH, P4, rho=rho_sl)
    chk("bath 311 + 328 = 323", [m311, W0], [m323])
    mw_dry = mw_of(b["x"])
    m325 = m323
    for _ in range(30):
        vol = m325 * 1000.0 / rho_sl                     # m3 = one hour of slurry (res_min = CYCLE_MIN, 50 % fill, sheet_vessel rule)
        v_free = vol / 2.0
        n_cycle = P4 * 1e5 * v_free / (R_GAS * (T_BATH + 273.15))
        m324 = n_cycle * mw_dry / 1000.0 / 1000.0 * (60.0 / CYCLE_MIN)    # t/h average
        m325 = m323 - m324
    ST[324] = St(324, "lock-hopper vent gas", "gas", m324, T_BATH, 1.5, mw=mw_dry)
    ST[325] = St(325, "slag slurry to dewatering", "slurry", m325, T_BATH, 1.5, rho=rho_sl)
    chk("V-102 323 = 324 + 325", [m323], [m324, m325], tol=1e-9)
    N["m_n2_lh"] = n_cycle * 28.014 / 1000.0 / 1000.0 * (60.0 / CYCLE_MIN)
    m326_s = m311 * (1 - RCP["fines_to_overflow"]); m326 = m326_s / (1 - RCP["cake_moisture"])
    ST[326] = St(326, "slag cake", "slurry", m326, T_BATH, 1.0, rho=1500.0)
    ST[327] = ls(327, "dewatering overflow", m325 - m326, T_BATH, 1.0, rho=rho_w(T_BATH) * 1.01)
    assert ST[327].flow > 0
    chk("DW-147 325 = 326 + 327", [m325], [m326, ST[327].flow], tol=1e-9)
    # ---- black-water flash cascade
    h0 = hl(T_out); x1 = (h0 - SAT_P[6.0][1]) / (SAT_P[6.0][2] - SAT_P[6.0][1]); v341 = x1 * w_bw
    W1 = w_bw - v341
    x2 = (SAT_P[6.0][1] - SAT_P[1.5][1]) / (SAT_P[1.5][2] - SAT_P[1.5][1]); v342 = x2 * W1; W2 = W1 - v342
    x3 = (SAT_P[1.5][1] - SAT_P[0.3][1]) / (SAT_P[0.3][2] - SAT_P[0.3][1]); v343 = x3 * W2; W3 = W2 - v343
    mwv = 18.015
    def tp(i, name, mv, Pb, Tb, ml):
        return St(i, name, "twophase", mv + ml, Tb, Pb, rho=rho_mix(mv, rho_gas(Pb, Tb, mwv), ml, rho_w(Tb)))
    ST[334] = tp(334, "black water after let-down, HP", v341, P_HP, SAT_P[6.0][0], W1 + m314)
    ST[341] = St(341, "HP flash steam", "gas", v341, SAT_P[6.0][0], P_HP, mw=mwv)
    ST[344] = ls(344, "black water, HP flashed", W1 + m314, SAT_P[6.0][0], P_HP)
    ST[335] = tp(335, "black water after let-down, LP", v342, P_LP, SAT_P[1.5][0], W2 + m314)
    ST[342] = St(342, "LP flash steam", "gas", v342, SAT_P[1.5][0], P_LP, mw=mwv)
    ST[345] = ls(345, "black water, LP flashed", W2 + m314, SAT_P[1.5][0], P_LP)
    ST[336] = tp(336, "black water after let-down, vacuum", v343, P_VAC, SAT_P[0.3][0], W3 + m314)
    ST[343] = St(343, "vacuum flash vapour", "gas", v343, SAT_P[0.3][0], P_VAC, mw=mwv)
    ST[346] = ls(346, "black water, vacuum flashed", W3 + m314, SAT_P[0.3][0], P_VAC)
    chk("HP flash", [ST[332].flow], [v341, W1 + m314]); chk("LP flash", [W1 + m314], [v342, W2 + m314]); chk("vacuum flash", [W2 + m314], [v343, W3 + m314])
    N["flash_fr"] = (x1, x2, x3)
    # ---- clarifier, press, tank
    S_c = m314 + RCP["fines_to_overflow"] * m311
    m348 = S_c / CLAR_UNDER; m349 = S_c / CAKE_SOLIDS; m350 = m348 - m349
    m347 = ST[346].flow + ST[327].flow - m349
    ST[348] = St(348, "clarifier underflow sludge", "slurry", m348, 65.0, 2.0, rho=1050.0)
    ST[349] = St(349, "filter cake", "slurry", m349, 65.0, 1.0, rho=1400.0)
    ST[350] = ls(350, "press filtrate", m350, 65.0, 2.0)
    ST[347] = ls(347, "clarified grey water", m347, 70.0, 1.5)
    chk("clarifier 346 + 327 + 350 = 347 + 348", [ST[346].flow, ST[327].flow, m350], [m347, m348])
    chk("press 348 = 349 + 350", [m348], [m349, m350])
    # dry-solids closure to Rev B stream 5
    cake_dry = S_c  # to press cake
    solids_out = m326_s + cake_dry + m313
    chk("solids: Rev B stream 5 = slag cake + press cake + fly ash (dry)", [g.M[5] * K * 3.6], [solids_out], tol=1e-9)
    m329 = m331 + W0
    ST[329] = ls(329, "grey water, HP discharge", m329, T_WASH, 50.0)
    need = m329 - m347
    # ---- sour-water stripper
    cond28 = stream(28, "process condensate", "liq", P=3.0, rho=992.0)
    v353 = v341 + v342 + v343
    ST[354] = St(354, "flash vapour to E-142", "gas", v353, 115.0, 1.4, mw=mwv)
    ST[353] = ls(353, "flash condensate", v353, 60.0, 1.3, rho=983.0)
    m391 = cond28.flow + v353; T391 = (cond28.flow * 40.0 + v353 * 60.0) / m391
    ST[391] = ls(391, "sour water to stripper", m391, T391, 3.0, rho=990.0)
    m392 = SOUR_OVHD_FRAC * m391
    ST[392] = St(392, "stripper overhead gas (NH3, H2S, CO2, steam)", "gas", m392, 90.0, 2.5, mw=20.0)
    ST[393] = ls(393, "stripped water", m391 - m392, 140.0, 3.5, rho=930.0)
    ST[394] = St(394, "LP steam to reboiler", "steam", SOUR_STEAM_RATIO * m391, 144.0, 4.0, mw=mwv)
    chk("C-146 391 = 392 + 393", [m391], [m392, ST[393].flow])
    avail = ST[393].flow - m330
    to_tank = min(avail, need); m351 = need - to_tank; m396 = avail - to_tank
    ST[395] = ls(395, "stripped water to grey-water tank", to_tank, 60.0, 1.5)
    ST[351] = ls(351, "process water make-up", m351, 30.0, 1.5)
    ST[396] = ls(396, "stripped water export", m396, 60.0, 3.0)
    chk("grey-water tank 347 + 395 + 351 = 329", [m347, to_tank, m351], [m329])
    chk("stripped water 393 = 330 + 395 + 396", [ST[393].flow], [m330, to_tank, m396])
    # ---- cooling water
    cw = lambda q_kw: q_kw / (hl(42.0) - hl(30.0)) * 3.6
    ST[371] = ls(371, "cooling water supply", cw(q_bath), 30.0, 5.0, rho=995.0)
    ST[372] = ls(372, "cooling water return", cw(q_bath), 42.0, 4.5, rho=991.0)
    q_e142 = (v341 * SAT_P[6.0][2] + v342 * SAT_P[1.5][2] + v343 * SAT_P[0.3][2] - v353 * hl(60.0)) / 3.6
    ST[373] = ls(373, "cooling water supply", cw(q_e142), 30.0, 5.0, rho=995.0)
    ST[374] = ls(374, "cooling water return", cw(q_e142), 42.0, 4.5, rho=991.0)
    # ---- start-up burner
    q_su = SU_FRAC * b["q_coal"]; m_fuel = q_su / LHV_FUEL * 3.6; m_o2su = O2_PER_FUEL * m_fuel
    ST[385] = ls(385, "start-up liquid fuel", m_fuel, 40.0, 56.0, rho=850.0)
    ST[387] = St(387, "start-up oxygen (branch of 2)", "gas", m_o2su, 40.0, 50.0, mw=31.998)
    ST[388] = St(388, "burner hot gas into R-101", "gas", m_fuel + m_o2su, 1400.0, P4, mw=28.0)
    chk("start-up burner", [m_fuel, m_o2su], [ST[388].flow], tol=1e-9)
    # ---- nitrogen
    n_r101, n_f135, n_other = 2.0, 1.2, 0.8                 # t/h (A)
    ST[381] = St(381, "N2 to burners and R-101 purge", "gas", n_r101, 25.0, 56.0, mw=28.014)
    ST[382] = St(382, "N2 back-pulse to F-135", "gas", n_f135, 25.0, 56.0, mw=28.014)
    ST[383] = St(383, "N2 to V-102 re-pressurisation", "gas", N["m_n2_lh"], 25.0, 56.0, mw=28.014)
    ST[384] = St(384, "N2 inerting, other users", "gas", n_other, 25.0, 56.0, mw=28.014)
    ST[380] = St(380, "N2 header from ASU-101", "gas", n_r101 + n_f135 + N["m_n2_lh"] + n_other, 25.0, 56.0, mw=28.014)
    chk("N2 header", [ST[380].flow], [ST[i].flow for i in (381, 382, 383, 384)])
    # ---- emergency depressurisation
    rho_inv = P4 * 1e5 * mw_of(n302) / 1000.0 / (R_GAS * 573.15)
    m_inv = EDV_VOL_M3 * rho_inv / 1000.0                  # t gas inventory (mean 300 C)
    m_edv = m_inv * (1 - 1.0 / P4) / (EDV_MIN / 60.0)      # t/h average to atmospheric pressure, D
    ST[398] = St(398, "EDV blowdown, gas train", "gas", m_edv, 300.0, 6.0, mw=mw_of(n302))
    ST[399] = St(399, "lock-hopper vent gas to flare", "gas", m324, 80.0, 2.0, mw=mw_dry)
    ST[397] = St(397, "to KO-101 / FL-101 (area 90)", "gas", m_edv + m324, 250.0, 3.0, mw=mw_of(n302))
    chk("EDV header", [m_edv, m324], [ST[397].flow])
    N.update(b=b, s=s, q_bath=q_bath, q_slag=q_slag, q_e142=q_e142, m_s=m_s, m_bfw=m_bfw, m_bd=m_bd, m_c=m_c, dw=dw, W0=W0, m_inv=m_inv, m_edv=m_edv,
             m_fuel=m_fuel, q_su=q_su, need=need, m351=m351, to_tank=to_tank, m396=m396, rho_sl=rho_sl, vol_lh=vol, m323=m323, m314=m314, m313=m313,
             S_c=S_c, w_bw=w_bw, m_wash=m_wash, cond28=cond28.flow, T391=T391)
    return ST, N

def power_wet_compressor(st_in, st_out, eta=0.75):
    """D: single-stage isentropic-type work W = m/M R T1 k/(k-1) ((p2/p1)^((k-1)/k) - 1)/eta, k from mean cp of the actual mixture (H table, 50 K)"""
    n = st_in.flow * 1000 / 3600 / st_in.mw * 1000       # mol/s
    s = balance()["sc"]; sp = {k: v / sum(s["rec"].values()) for k, v in s["rec"].items()}
    cp = (H_gas(sp, st_in.T + 50.0) - H_gas(sp, st_in.T)) / 50.0 * 1000.0     # J/mol/K per mol of mixture
    k = cp / (cp - R_GAS)
    T1 = st_in.T + 273.15
    w = n * R_GAS * T1 * k / (k - 1) * ((st_out.P / st_in.P) ** ((k - 1) / k) - 1) / eta
    return w / 1e6, k


# ---------------------------------------------------------------------------------------------------------------------
# 4. sheets
# ---------------------------------------------------------------------------------------------------------------------
PKG = None
def xrun(sh, no, st, pts, frm, to, idx, spec="A1", svc="PL", esd=False, label=None):
    return run(sh, PKG, sh, f"{AREA[0]}{no % 100:02d}", AREA, st, pts, frm, to, spec, svc, idx, esd=esd, label=label)

def sheet_r101(pkg, ST, N):
    no = 301; b, s = N["b"], N["s"]
    sh, lp = head(pkg, AREA, no, "Area 30  Gasification  -  R-101 entrained-flow slagging gasifier (membrane wall, quench zone, slag bath)", "R-101", "Entrained-flow slagging gasifier")
    cx, top, w, h = 560, 165, 170, 440
    v = vvessel(sh, cx, top, w, h); x0, x1 = cx - w / 2, cx + w / 2
    yb = v["bottom"][1]
    R(sh, x0 + 6, top + 12, w - 12, 118, "#fff8e1", "#bf8f00", 1.2, "4 3"); lab(sh, cx, top + 30, "quench zone", 9.5, 700, "middle", "#7a5c00"); lab(sh, cx, top + 43, "recycle gas 301 mixes to 900 C", 8.5, 400, "middle", GREY)
    R(sh, x0 + 6, top + 140, w - 12, 205, "none", GREEN, 1.8, "6 3"); lab(sh, cx, top + 160, "membrane wall", 9.5, 700, "middle", GREEN); lab(sh, cx, top + 173, "steam raising (367 in, 368 out)", 8.5, 400, "middle", GREY)
    lab(sh, cx, top + 186, "reaction zone", 9.5, 700, "middle", AMBER)
    R(sh, x0 + 6, top + 365, w - 12, 62, "#cfe6f7", "none", 1); lab(sh, cx, top + 392, "slag quench bath", 9.5, 700, "middle", BLUE); lab(sh, cx, top + 405, "water at 45 bar", 8.5, 400, "middle", GREY)
    flame(sh, x0 + 6, top + 205, 90, 62, 22); flame(sh, x1 - 6, top + 205, -90, 62, 22)
    lab(sh, cx, top + 245, "burners (licensor)", 8.5, 400, "middle", GREY)
    strm(sh, cx, top + 135, 4); lab(sh, cx - 16, top + 139, "raw gas 1400 C", 8.5, 400, "end", GREY)
    strm(sh, cx - 40, top + 330, 311); lab(sh, cx - 28, top + 334, "coarse slag", 8.5, 400, "start", GREY)
    strm(sh, cx + 30, top + 300, 312); lab(sh, cx + 42, top + 304, "fly slag", 8.5, 400, "start", GREY)
    # feeds from the left
    xrun(sh, no, ST[367], [(50, top + 55), (x0, top + 55)], "D-133 / P-134", "R-101 wall", 1, "CR", "BF", label=(56, top + 21))
    xrun(sh, no, ST[1], [(50, top + 150), (x0, top + 150)], "F-101", "R-101 burners", 2, "CR", "CL", esd=True, label=(56, top + 112))
    xrun(sh, no, ST[2], [(50, top + 205), (x0, top + 205)], "ASU-101", "R-101 burners", 3, "CR", "OX", esd=True, label=(56, top + 167))
    xrun(sh, no, ST[3], [(50, top + 260), (x0, top + 260)], "steam header", "R-101 burners", 4, "CR", "ST", esd=True, label=(56, top + 222))
    xrun(sh, no, ST[381], [(50, top + 315), (x0, top + 315)], "N2 header", "R-101 purge", 5, "A1", "N2", label=(56, top + 277))
    xrun(sh, no, ST[328], [(50, top + 395), (x0, top + 395)], "T-144 pumps", "bath", 6, "A1", "GW", label=(56, top + 357))
    # right side
    xrun(sh, no, ST[302], [(x1, top + 25), (1090, top + 25)], "R-101", "E-101", 7, "CR", "SG", esd=True, label=(x1 + 20, top - 10))
    xrun(sh, no, ST[301], [(1090, top + 85), (x1, top + 85)], "K-132", "R-101 quench", 8, "CR", "SG", label=(x1 + 20, top + 52))
    xrun(sh, no, ST[368], [(x1, top + 175), (1090, top + 175)], "R-101 wall", "D-133", 9, "CR", "BF", label=(x1 + 20, top + 141))
    xrun(sh, no, ST[321], [(x1, top + 392), (1090, top + 392)], "bath", "E-131", 10, "A1", "GW", label=(x1 + 20, top + 358))
    xrun(sh, no, ST[322], [(1090, top + 425), (x1, top + 425)], "E-131", "bath", 11, "A1", "GW", label=(x1 + 20, top + 433))
    xrun(sh, no, ST[323], [(cx, yb), (cx, yb + 55), (1090, yb + 55)], "R-101 bath", "V-102", 12, "A1", "SL", label=(cx + 70, yb + 21))
    # flare header: PSV and EDV
    PL(sh, [(60, 100), (1090, 100)], 2.0, INK, "6 3"); arrow(sh, 1090, 100, "r"); lab(sh, 64, 96, "flare header (EDV and PSV discharge) to KO-101 / FL-101 (area 90)", 8.5, 400, "start", GREY)
    px = x0 - 70
    PL(sh, [(x0, top + 30), (px, top + 30), (px, top + 18)], 2.0)
    psv_at(sh, pkg, sh, px, top - 2, "PSV-30101", "R-101 shell", "blocked outlet; E-101 tube rupture into gas; fire", design_conditions(P4, T_MIX)[0], "flare header via KO-101", "not sized: needs tube-rupture and blocked-in load")
    PL(sh, [(px, top - 34), (px, 100)], 1.6, INK, "6 3")
    lab(sh, px - 14, top + 12, "= PSV-101 (Rev B)", 8.5, 400, "end", GREY)
    blockv(sh, pkg, sh, cx + 30, 130, 90, "XV-30160", "-", 4, "ball", "emergency depressurisation (BDV-101 Rev B)", "FO", act=True)
    PL(sh, [(cx + 30, v["top"][1] + 6), (cx + 30, 100)], 2.0); lab(sh, cx + 64, 124, "XV-30160 EDV (Rev B BDV-101) FO", 8.5, 700, "start", RED)
    # instruments
    bub(sh, pkg, sh, 760, top + 215, "PIC", f"{lp}11", "R-101", "gasifier pressure (cascade to area 40 let-down)", "0-60 bar", "H 47 / L 42 bar")
    bub(sh, pkg, sh, 810, top + 215, "PAHH", f"{lp}12", "R-101", "pressure high-high (ESD-1)", "0-60 bar", "HH 49 bar (A)", panel=True)
    bub(sh, pkg, sh, 860, top + 215, "TAHH", f"{lp}13", "R-101", "membrane-wall / shell skin temperature high-high", "0-600 C", "HH per licensor (A)", panel=True)
    bub(sh, pkg, sh, 910, top + 215, "FAL", f"{lp}14", "R-101", "wall circulation flow low (trip)", "0-400 t/h", "LL 50 % (A)", panel=True)
    bub(sh, pkg, sh, 760, top + 270, "FFIC", f"{lp}21", "R-101", "O2 / coal ratio control", "0-1 kg/kg", "L 0.45 / H 0.65 (A)", panel=True)
    bub(sh, pkg, sh, 810, top + 270, "BSLL", f"{lp}22", "R-101", "burner flame loss (trip)", "on/off", "flame fail (A); sheet 302", panel=True)
    bub(sh, pkg, sh, 860, top + 270, "AAHH", f"{lp}23", "R-101", "CO / H2 gas detectors, hall (2oo3)", "0-100 % LEL", "HH 20 % LEL (A)", panel=True)
    bub(sh, pkg, sh, 910, top + 270, "AAHH", f"{lp}24", "R-101", "CO toxic detector, hall", "0-500 ppm", "H 30 / HH 100 ppm (A)", panel=True)
    bub(sh, pkg, sh, 760, top + 325, "LIC", f"{lp}31", "R-101 bath", "slag bath level", "0-100 %", "H 80 / L 20 % (A)")
    bub(sh, pkg, sh, 810, top + 325, "LALL", f"{lp}32", "R-101 bath", "bath level low-low (hot slag / gas blow-by to V-102)", "0-100 %", "LL 10 % (A)", panel=True)
    bub(sh, pkg, sh, 860, top + 325, "TI", f"{lp}33", "R-101 bath", "bath temperature", "0-150 C", "-")
    bub(sh, pkg, sh, 910, top + 325, "PDAH", f"{lp}34", "R-101 slag tap", "slag-tap differential pressure (plugging)", "0-5 bar", "H 3 bar (A)", panel=True)
    PL(sh, [(x1, top + 215), (745, top + 215)], 1.0, BLUE, "4 3"); PL(sh, [(x1, top + 270), (745, top + 270)], 1.0, BLUE, "4 3"); PL(sh, [(x1, top + 325), (745, top + 325)], 1.0, BLUE, "4 3")
    lab(sh, 700, yb + 88, "ESD-1 (Rev B): PSHH-101 / AT-102 / BE-101 close XV-30151..53 (coal, O2, steam) and open XV-30160", 8.5, 700, "start", RED)
    lab(sh, 700, yb + 100, "Licensor-owned: burners, wall circuit, slag tap, quench geometry, ash chemistry, light-up and trip sequences", 8.5, 400, "start", GREY)
    t_res = 3.0; vol = ST[4].q * t_res; D = (4 * vol / (math.pi * 3.0)) ** (1 / 3); Ht = D * 3.0
    Pd, Td = design_conditions(P4, T_MIX)
    eq(pkg, sh, "R-101", "Entrained-flow slagging gasifier, membrane wall", "pressure vessel", f"{P4:g} bar, 1400 C gas (S Rev B)", f"{Pd:g} bar g / shell T by licensor", f"{vol:.0f} m3 reaction vol., ~{D:.1f} m x {Ht:.0f} m (D,A)", "A: licensor", "D")
    eq(pkg, sh, "V-131", "Slag quench bath (lower section of R-101)", "bath", f"{P4:g} bar, {T_BATH:g} C", f"{Pd:g} bar g", "licensor", "A: licensor", "A")
    rows = [("Operating", f"{P4:g} bar / 1400 C", "S Rev B"), ("Design", f"{Pd:g} bar g, shell T lic.", "D"), ("Reaction vol.", f"{vol:.0f} m3 (3 s, A)", "D,A"), ("Size", f"~{D:.1f} m x {Ht:.0f} m", "D"),
            ("Coal thermal in", f"{b['q_coal']/1e3:,.0f} MW", "D (CGE S)"), ("Wall duty", f"{b['q_wall']/1e3:.1f} MW (1.5 %)", "D,A"), ("Fly slag", f"{ST[312].flow:.1f} t/h (30 %)", "A"),
            ("Relief", "PSV-30101 / XV-30160", "A"), ("Hazard", "CO, H2, H2S, hot slag, steam", "-")]
    finish(pkg, sh, AREA, "R-101", "Entrained-flow slagging gasifier", rows, [
        f"Mass closure: Rev B 1+2+3 = 4 + 311 + 312 within {abs(b['R101_resid'])*100:.2f} % (Rev B element balance residual). 311 + 312 = Rev B stream 5.",
        "Rev B tag map: XV-30152 = XV-101 (O2), XV-30151 = XV-102 (coal), XV-30153 = XV-103 (steam), XV-30160 = BDV-101, PSV-30101 = PSV-101.",
        "Quench recycle: stream 301 cools 4 from 1400 C to 900 C (heat balance in balance(), tag D; 900 C is an A below ash softening).",
        "Burner count, nozzle design, wall pressure drop and refractory-free wall are licensor data; not invented here."])
    return sh

def build(pkg):
    global PKG
    PKG = pkg; pkg.total = 0
    ST, N = derive()
    s = N["s"]; b = N["b"]; A = AREA
    sheet_r101(pkg, ST, N)
    # ---- 302 burner and start-up fuel
    sheet_package(pkg, A, 302, "Area 30  Gasification  -  BR-131 burner management and start-up fuel", dict(
        tag="BR-131", name="Burner management and start-up fuel skid", spec="CR",
        inlets=[(ST[385], "fuel", "PL"), (ST[387], "O2", "OX"), (ST[381], "N2", "N2")], outlets=[(ST[388], "hot gas", "SG")],
        desc=["start-up burner heats the membrane wall and bath", "to ignition conditions; pilot, main fuel", "double block and bleed on every fuel line", "licensor owns burner, light-up sequence"],
        utilities=[("instr. air", 500.0, "kg/h", "A"), ("cooling water", 2.0, "t/h", "A"), ("N2 purge", ST[381].flow, "t/h", "A"), ("power", 50.0, "kW", "A")],
        interlocks=[("BSLL", "burner flame loss (trip fuel and O2)", "on/off", "flame fail 3 s (A)"), ("PALL", "N2 purge pressure low (no light-up)", "0-80 bar", "LL 40 bar (A)"),
                    ("XSC", "double-block-and-bleed valves proved closed", "limit", "before purge (A)"), ("TAHH", "burner nozzle cooling water T high", "0-150 C", "HH 90 C (A)"),
                    ("AAHH", "CO / H2 detector, burner deck, 2oo3", "0-100 % LEL", "HH 20 % LEL (A)")],
        esd=True, relief="fuel line thermal expansion; blocked-in", type="burner skid",
        op=f"{ST[385].flow*1000:.0f} kg/h fuel, {N['q_su']/1e3:.1f} MW thermal (D,A)", hazard="flammable fuel, O2, CO/H2, flame",
        rows=[("Duty", f"{N['q_su']/1e3:.1f} MW", "D,A 0.5 %"), ("Fuel", f"{ST[385].flow:.2f} t/h", "D (LHV A)"), ("O2", f"{ST[387].flow:.2f} t/h", "D (stoich A)")],
        notes=["Start-up fuel is an A: light distillate or LPG, to be fixed by the licensor and site fuel availability. Duty is 0.5 % of coal thermal input (A, 0.3-1 %); LHV 43 MJ/kg (A).",
               "Burner flame loss, fuel/O2/N2 DBB logic and purge-before-light-up permissive are drawn as interlock bubbles; the sequence itself is licensor-owned.",
               "Mass closure: 385 + 387 = 388. Also required (not drawn, template shows at most 5 bubbles clear of the utility labels): PAL on fuel pressure (L 45 bar A), AAL O2 deficiency in the N2 area (L 19.5 %)."]))
    # ---- 303 K-132 quench gas recycle compressor
    pw, kk = power_wet_compressor(ST[307], ST[301])
    sheet_compressor(pkg, A, 303, "Area 30  Gasification  -  K-132 quench-gas recycle compressor", dict(
        tag="K-132", name="Quench-gas recycle compressor", suction=ST[307], discharge=ST[301], power_MW=pw, driver="motor", spec="SG", basis="D",
        hazard="wet sour syngas, condensate", mat="A: CS/low-alloy, sour",
        notes=[f"Power by isentropic single-stage formula with k = {kk:.2f} from the mixture cp (H table), eta 0.75 (A): D.",
               "Suction is saturated at the scrubber outlet temperature, so the KO drum returns condensate to the scrubber sump (not drawn: no stream defined); wet-gas compression is a vendor item.",
               "Recycle share: 301 = 307 = 250 t/h, set by the quench heat balance (4 at 1400 C to 900 C)."]))
    # ---- 304 E-131 bath cooler
    sheet_hx(pkg, A, 304, "Area 30  Slag handling  -  E-131 slag-bath water cooler", dict(
        tag="E-131", name="Slag-bath water cooler", hot_in=ST[321], hot_out=ST[322], cold_in=ST[371], cold_out=ST[372], duty_MW=N["q_bath"] / 1e3, kind="liq_liq", spec="A1", spec_c="A1", svc_c="CW",
        hazard="hot water + ash fines, erosion", mat="A: duplex, hard-faced",
        notes=[f"Duty = slag sensible heat 1400 to 80 C ({N['q_slag']/1e3:.1f} MW, cp 1.1 kJ/kg/K A, heat of fusion ignored) + heating of bath make-up 70 to 80 C.",
               "Bath water circulates in a closed loop at 45 bar through R-101; circulation pumps P-131A/B are not drawn (no pump template for a closed loop): gap.",
               "Bath hot/cold temperatures 105 / 80 C are A; 80 C matches Rev B stream 5."]))
    # ---- 305 V-102 lock hopper
    sheet_vessel(pkg, A, 305, "Area 30  Slag handling  -  V-102 slag lock hopper", dict(
        tag="V-102", name="Slag lock hopper", inlet=ST[323], gas=ST[324], liq=ST[325], res_min=CYCLE_MIN, spec="A1", svc_in="SL", svc_gas="SG", svc_liq="SL", pumps=None,
        mat="A: CS, abrasion lining", hazard="CO/H2 void gas, hot slag slurry",
        relief_case="gas blow-through from R-101 bath; blocked vent", relief_dest="flare header via KO-101",
        notes=[f"Cycle {CYCLE_MIN:g} min (A): fill, isolate, depressurise 45 to 1.5 bar, dump to V-102 dewatering, re-pressurise with N2 ({ST[383].flow:.1f} t/h average).",
               f"Vent gas 324 = void gas per cycle: P V_free/(R T) M, V_free = half the vessel (50 % fill rule), average {ST[324].flow:.1f} t/h; goes to the flare header (CO/H2), not atmosphere.",
               "Stream 5 (Rev B) is solids only: 311 + 312 = 5. Slurry solids 40 wt % (A 30-60)."]))
    # ---- 306 DW-147 dewatering
    sheet_package(pkg, A, 306, "Area 30  Slag handling  -  DW-147 slag dewatering bin and conveyor", dict(
        tag="DW-147", name="Slag dewatering bin and drag conveyor", spec="A1",
        inlets=[(ST[325], "slag slurry", "SL")], outlets=[(ST[326], "cake to truck", "SL"), (ST[327], "overflow", "GW")],
        desc=["dewatering bin with overflow weir", "submerged drag-chain conveyor", "cake to truck / stockpile, 25 wt % moisture", "overflow to CL-143 clarifier"],
        utilities=[("power", 100.0, "kW", "A"), ("flush water", 5.0, "t/h", "A"), ("vent", 100.0, "kg/h", "A")],
        interlocks=[("LAHH", "bin level high-high (stop slurry dump)", "0-100 %", "HH 90 % (A)"), ("JAH", "conveyor motor overload", "0-200 %", "H 110 % (A)"), ("ZSH", "bin outlet gate position", "open/closed", "not closed (A)"),
                    ("AAH", "CO detector, dewatering hall (residual gas)", "0-500 ppm", "H 30 ppm (A)")],
        type="dewatering bin + drag conveyor", op="80 C, 1 bar", hazard="hot slag, burns, residual CO",
        rows=[("Cake", f"{ST[326].flow:.0f} t/h wet", "D"), ("Moisture", "25 wt %", "A"), ("Fines to o/f", "1 %", "A")],
        notes=["Mass closure: 325 = 326 + 327. Dry solids of 326 + press cake + fly ash 313 = Rev B stream 5 (asserted in code).", "Solids handling hardware (bin, conveyor) is vendor-specific; sized by flow only (A)."]))
    # ---- 307 E-101 syngas cooler
    sheet_hx(pkg, A, 307, "Area 30  Syngas cooling  -  E-101 syngas cooler (HP steam raising)", dict(
        tag="E-101", name="Syngas cooler (evaporator)", hot_in=ST[302], hot_out=ST[303], cold_in=ST[369], cold_out=ST[364], duty_MW=s["q101"] / 1e3, kind="steam_gen", spec="CR", spec_c="CR", svc_c="BF",
        esd_hot=True, hazard="900 C syngas, HP tube rupture", mat="A: alloy by licensor",
        notes=[f"Gas leaves at Tsat(100 bar) + 30 K = {s['T303']:.0f} C (A pinch); below that the economiser E-132 takes over. Duty = H(302, 900 C) - H(302, {s['T303']:.0f} C) + fly slag sensible.",
               "Rev B A: E-101 'syngas cooler / quench' is split here into quench zone (R-101 sheet), evaporator (this sheet) and economiser (E-132).",
               "Tube rupture puts 100 bar water on the gas side: PSV-30101 on R-101 and the gas train; not sized."]))
    # ---- 308 E-132 economiser
    sheet_hx(pkg, A, 308, "Area 30  Syngas cooling  -  E-132 syngas economiser (BFW preheat)", dict(
        tag="E-132", name="Syngas economiser", hot_in=ST[303], hot_out=ST[304], cold_in=ST[361], cold_out=ST[360], duty_MW=s["q_ec"] / 1e3, kind="gas_liq", spec="CR", spec_c="CR", svc_c="BF",
        esd_hot=True, hazard="hot syngas, dew-point corrosion", mat="A: CS/low-alloy",
        notes=[f"BFW 200 to 250 C at 110 bar (A); gas outlet {s['T304']:.0f} C is a RESULT of the duty (D), and must stay above the dew point + 15 K (checked in code).",
               "BFW at 200 C assumes HP feed-water heaters in area 70 (A); at 105 C the economiser duty would cool the gas below its dew point.",
               "Hot-side bypass and temperature control keep F-135 above the dew point."]))
    # ---- 309 D-133 steam drum
    sh = sheet_vessel(pkg, A, 309, "Area 30  Syngas cooling  -  D-133 HP steam drum with forced-circulation pumps", dict(
        tag="D-133", name="HP steam drum", inlet=ST[365], gas=ST[362], liq=ST[366], res_min=0.5, pumps="P-134", pump_dp_bar=6.0, spec="CR", svc_in="BF", svc_gas="ST", svc_liq="BF",
        internals="demister", mat="A: low-alloy, to licensor/boiler code", hazard="HP steam 100 bar, carry-over",
        relief_case="blocked steam outlet; loss of BFW; fire", relief_dest="atmosphere via silencer (steam), safe location (A)",
        notes=[f"Steam {N['m_s']:.0f} t/h saturated at 100 bar (D); blowdown {N['m_bd']:.1f} t/h; BFW 360 = 362 + 363; closure 365 + 360 = 362 + 363 + 366 asserted.",
               f"Circulation ratio {CIRC_RATIO:g} kg water/kg steam (A 5-15): {N['m_c']:.0f} t/h through the membrane wall and E-101. Stream 3 (24 t/h to R-101) is a small part of the steam; surplus to area 70.",
               "Three-element level control (drum level, steam flow, BFW flow) and the BFW line (360) are drawn as added lines; level trips are the template's LALL / LAHH."]))
    # added lines on the drum sheet
    xrun(sh, 309, ST[360], [(40, 250), (410, 250)], "E-132", "D-133", 71, "CR", "BF", label=(46, 224))
    xrun(sh, 309, ST[363], [(410, 450), (60, 450)], "D-133", "blowdown flash (area 70)", 72, "CR", "BF", label=(66, 416))
    bub(sh, pkg, sh, 640, 300, "FFIC", "30941", "D-133", "three-element level control (cascade LIC-30921 / FT steam / FT BFW)", "0-100 %", "-")
    # ---- 310 F-135 fine-ash filter
    sheet_package(pkg, A, 310, "Area 30  Syngas cleaning  -  F-135 hot-gas fine-ash filter", dict(
        tag="F-135", name="Hot-gas fine-ash candle filter", spec="CR",
        inlets=[(ST[304], "gas + fly slag", "SG"), (ST[382], "N2 back-pulse", "N2")], outlets=[(ST[309], "cleaned gas", "SG"), (ST[313], "dry fly ash", "SL")],
        desc=["ceramic / metal candles, N2 back-pulse", "operated above gas dew point", "fly ash through lock hopper (licensor)", "to ash silo / bin (not drawn)"],
        utilities=[("N2 pulse", ST[382].flow, "t/h", "A"), ("heat tracing", 500.0, "kW", "A"), ("power", 50.0, "kW", "A")],
        interlocks=[("PDAH", "filter differential pressure high (fouling / broken candle)", "0-1 bar", "H 0.7 bar (A)"), ("TAL", "filter temperature low (dew-point margin)", "0-400 C", f"L {s['T304']-40:.0f} C (A)"),
                    ("AAH", "dust at outlet (broken candle)", "0-50 mg/m3", "H 10 mg/m3 (A)"), ("LAHH", "fly-ash hopper level high-high", "0-100 %", "HH 90 % (A)"),
                    ("AAHH", "CO / H2 detector at filter deck, 2oo3", "0-100 % LEL", "HH 20 % LEL (A)")],
        esd=True, relief="blocked outlet; scrubber overpressure", type="candle filter", op=f"{s['T304']:.0f} C, {P304:g} bar", hazard="CO/H2/H2S gas, ash dust, N2",
        rows=[("Capture", f"{FILTER_ETA*100:.0f} % of fly slag", "A"), ("Fly ash", f"{ST[313].flow:.1f} t/h dry", "D"), ("Fines left", f"{N['m314']:.2f} t/h", "D"), ("Dew margin", f"{s['T304']-t_dew(s['n302']['H2O']/sum(s['n302'].values())*P304):.0f} K", "D")],
        notes=["Fine-ash filter placed after the economiser (Shell-type route, A); fines passing the filter (314) go to the scrubber and become black water.", "Filter surface area is a vendor item (face velocity data not available): not sized."]))
    # ---- 311 VS-136 venturi
    sheet_package(pkg, A, 311, "Area 30  Syngas scrubbing  -  VS-136 venturi scrubber", dict(
        tag="VS-136", name="Venturi scrubber", spec="CR",
        inlets=[(ST[309], "gas + fines", "SG"), (ST[331], "wash water", "GW")], outlets=[(ST[308], "gas + water", "SG")],
        desc=["throat contact of gas with wash water", "removes fines passing F-135", f"L/G = {ST[331].flow*1000/3600/rho_gas(P309, s['T309'], 14.6)/ (ST[309].q if False else 1):.0f}" if False else "wash water 331 sprayed at throat", "outlet to C-137 column"],
        utilities=[("wash water", ST[331].flow, "t/h", "D")],
        interlocks=[("FAL", "wash water flow low (trip: gas to flare)", "0-60 t/h", "L 60 % (A)"), ("PDAH", "venturi differential pressure", "0-2 bar", "H 1.0 bar (A)"), ("TAHH", "outlet temperature high-high (water loss)", "0-300 C", f"HH {s['T_out']+40:.0f} C (A)"),
                    ("AAHH", "CO / H2 detector at scrubber deck", "0-100 % LEL", "HH 20 % LEL (A)")],
        esd=True, type="venturi", op=f"{s['T309']:.0f} -> {s['T_out']:.1f} C, {P309:g} bar", hazard="wet CO/H2/H2S gas, abrasion",
        rows=[("Gas in", f"{ST[309].flow:.0f} t/h", "D"), ("Wash water", f"{ST[331].flow:.1f} t/h", "D"), ("Evaporated", f"{N['dw']:.1f} t/h", "D"), ("Out T", f"{s['T_out']:.1f} C", "D")],
        notes=["Scrubber outlet temperature is solved from the adiabatic-saturation balance (gas enthalpy in = out + black water; saturation y = Psat/P), not typed.",
               f"It evaporates {N['dw']:.1f} t/h of wash water into the gas: stream 306 carries that extra steam, so area 40 can lower stream 6 (HP steam to R-201) by about this amount.",
               "Throat velocity and dp are vendor data; not sized. Mass closure over C-137: 309 + 331 + 330 = 305 + 332."]))
    # ---- 312 C-137 scrubber column
    sh = sheet_column(pkg, A, 312, "Area 30  Syngas scrubbing  -  C-137 syngas scrubber column", dict(
        tag="C-137", name="Syngas scrubber column", feed=ST[308], top=ST[305], bottom=ST[332], feed2=ST[330], packing=False, stages=8, spec="SG", esd=True,
        hazard="wet sour syngas 41 bar, black water", mat="A: CS, SS trays, sour",
        notes=[f"Top stream 305 ({ST[305].flow:.0f} t/h) splits to 306 net syngas to area 40 ({ST[306].flow:.0f} t/h) and 307 recycle to K-132 ({ST[307].flow:.0f} t/h).",
               f"Black-water bleed {ST[332].flow:.1f} t/h set by 3 wt % solids (A 1-5); chloride / ammonia build-up may require a larger bleed: licensor.",
               f"Wash water total {N['m_wash']:.1f} t/h: {ST[331].flow:.1f} t/h grey water to VS-136 and {ST[330].flow:.1f} t/h stripped water at the column top (30 %, A)."]))
    lab(sh, 560, 150, "305 splits: 306 net (area 40), 307 recycle (sheet 303)", 8.5, 700, "start", BLUE)
    # ---- 313..315 flash drums
    flash_n = ["P_HP", "P_LP", "P_VAC"]
    sheet_vessel(pkg, A, 313, "Area 30  Black-water treatment  -  V-139 HP flash drum", dict(
        tag="V-139", name="HP black-water flash drum", inlet=ST[334], gas=ST[341], liq=ST[344], res_min=5.0, spec="SS", svc_in="BW", svc_gas="SG", svc_liq="BW",
        mat="A: duplex or CS + SS lining", hazard="sour flash steam, hot black water",
        relief_case="blocked vapour outlet; letdown valve failure open", relief_dest="flare header via KO-101",
        notes=[f"Black water 332 ({ST[332].T:.1f} C, 41 bar) lets down to {P_HP:g} bar a; flash fraction {N['flash_fr'][0]*100:.1f} % of the water from the enthalpy balance (D).",
               "Dissolved gases in the flash steam are not quantified (no gas-solubility data in the HMB): gap. Flash steam goes to the condenser E-142.",
               "Let-down valve erosion is the dominant maintenance item: angle valve with hardened trim (A)."]))
    sheet_vessel(pkg, A, 314, "Area 30  Black-water treatment  -  V-140 LP flash drum", dict(
        tag="V-140", name="LP black-water flash drum", inlet=ST[335], gas=ST[342], liq=ST[345], res_min=5.0, spec="SS", svc_in="BW", svc_gas="SG", svc_liq="BW",
        mat="A: duplex or CS + SS lining", hazard="sour flash steam, hot black water",
        relief_case="blocked vapour outlet", relief_dest="flare header via KO-101",
        notes=[f"LP flash at {P_LP:g} bar a: {N['flash_fr'][1]*100:.1f} % of the remaining water flashes (D)."]))
    sheet_vessel(pkg, A, 315, "Area 30  Black-water treatment  -  V-141 vacuum flash drum", dict(
        tag="V-141", name="Vacuum black-water flash drum", inlet=ST[336], gas=ST[343], liq=ST[346], res_min=5.0, pumps="P-141", pump_dp_bar=3.0, spec="SS", svc_in="BW", svc_gas="SG", svc_liq="BW",
        mat="A: duplex or CS + SS lining", hazard="sour vapour, air in-leak (vacuum)",
        relief_case="vacuum breaker failure; blocked vapour outlet", relief_dest="flare header via KO-101 (A)",
        notes=[f"Vacuum {P_VAC:g} bar a (A) is held by a liquid-ring pump / ejector package (vendor, not drawn); its discharge joins E-142 at 1.4 bar.",
               "Air in-leakage into the sour vapour is an explosion path: PAH on vacuum drift, N2 break (see sheet 320). Cooled liquid goes to CL-143."]))
    # ---- 316 E-142 flash steam condenser
    sheet_hx(pkg, A, 316, "Area 30  Black-water treatment  -  E-142 flash-steam condenser", dict(
        tag="E-142", name="Flash-steam condenser", hot_in=ST[354], hot_out=ST[353], cold_in=ST[373], cold_out=ST[374], duty_MW=N["q_e142"] / 1e3, kind="cond", spec="SS", spec_c="A1", svc_c="CW", esd_hot=True,
        hazard="sour flash vapour, NH3/H2S vent", mat="A: SS or titanium tubes",
        notes=["Condenses 341 + 342 + 343 (HP, LP and vacuum flash vapours, 5.6 t/h) merged at 1.4 bar and 115 C (A); condensate 353 feeds the sour-water stripper.",
               "Non-condensables are not quantified (no solubility data): the vent line to the sour-gas header is not drawn: gap."]))
    # ---- 317 CL-143 clarifier
    sheet_package(pkg, A, 317, "Area 30  Grey-water system  -  CL-143 grey-water clarifier", dict(
        tag="CL-143", name="Grey-water clarifier", spec="A1",
        inlets=[(ST[346], "black water", "BW"), (ST[327], "slag overflow", "GW"), (ST[350], "press filtrate", "GW")], outlets=[(ST[347], "clarified water", "GW"), (ST[348], "sludge", "SL")],
        desc=["flocculant dosed in the feed well", "rake and underflow pumps", "covered, vented to sour-vent header", f"underflow {CLAR_UNDER*100:.0f} wt % solids (A)"],
        utilities=[("flocculant", 2.0, "kg/h", "A"), ("rake drive", 20.0, "kW", "A")],
        interlocks=[("JAHH", "rake torque high-high (raise rake, stop)", "0-100 %", "HH 90 % (A)"), ("LAH", "sludge blanket high", "0-100 %", "H 70 % (A)"), ("AAH", "H2S detector at clarifier cover", "0-100 ppm", "H 10 ppm (A)"), ("AAH", "overflow turbidity high", "0-100 NTU", "H 50 NTU (A)")],
        type="clarifier", op="65-70 C, atmospheric", hazard="H2S/NH3 release, hot water",
        rows=[("Feed", f"{ST[346].flow+ST[327].flow+ST[350].flow:.0f} t/h", "D"), ("Solids", f"{N['S_c']:.2f} t/h", "D"), ("Capture", "100 % (A)", "A")],
        notes=["Mass closure: 346 + 327 + 350 = 347 + 348. All solids are captured in the sludge (A; real overflow carries tens of mg/L).", "Rise rate and diameter need settling data for this ash: not obtained, not sized."]))
    # ---- 318 FP-145 filter press
    sheet_package(pkg, A, 318, "Area 30  Grey-water system  -  FP-145 sludge filter press", dict(
        tag="FP-145", name="Sludge filter press", spec="A1",
        inlets=[(ST[348], "sludge", "SL")], outlets=[(ST[349], "filter cake", "SL"), (ST[350], "filtrate", "GW")],
        desc=["plate-and-frame press, batch cycle", "feed pumps and air blow-down", f"cake {CAKE_SOLIDS*100:.0f} wt % solids (A)", "cake to hazardous-waste landfill (A)"],
        utilities=[("instr. air", 300.0, "kg/h", "A"), ("power", 80.0, "kW", "A"), ("wash water", 1.0, "t/h", "A")],
        interlocks=[("PAH", "press feed pressure high", "0-15 bar", "H 12 bar (A)"), ("ZAL", "plate closure not proved", "open/closed", "not closed (A)"), ("AAH", "H2S detector at press", "0-100 ppm", "H 10 ppm (A)")],
        type="filter press", op="65 C", hazard="H2S release, cake handling",
        rows=[("Cake", f"{ST[349].flow:.2f} t/h", "D"), ("Filtrate", f"{ST[350].flow:.1f} t/h", "D")],
        notes=["Mass closure: 348 = 349 + 350. Cycle time and plate area need cake filterability data: not obtained.", "Heavy-metal content of the cake (vanadium, nickel from petcoke) makes it hazardous waste: disposal route is a gap."]))
    # ---- 319 T-144 grey-water tank
    sheet_tank(pkg, A, 319, "Area 30  Grey-water system  -  T-144 grey-water tank and HP wash-water pumps", dict(
        tag="T-144", name="Grey-water tank", inflow=ST[347], outflow=ST[329], days=0.1, roof="cone", spec="A1", refrigerated=False, pumps="P-144", pump_dp=49.0, svc="GW",
        vent_dest="sour-vent header to flare (A)", hazard="H2S/NH3 sour vapour, hot water",
        notes=[f"Also receives 395 stripped water ({ST[395].flow:.1f} t/h) and make-up 351 ({ST[351].flow:.1f} t/h); closure 347 + 395 + 351 = 329 asserted.",
               f"Pumps lift 329 to {ST[329].P:g} bar for bath make-up 328 ({ST[328].flow:.0f} t/h) and wash water 331 ({ST[331].flow:.0f} t/h) / 330: multistage HP pumps.",
               "Tank height is fixed at 20 m by the template; a real grey-water tank would be wider and lower (cosmetic)."]))
    # ---- 320 C-146 sour-water stripper
    sheet_column(pkg, A, 320, "Area 30  Sour-water system  -  C-146 sour-water stripper", dict(
        tag="C-146", name="Sour-water stripper", feed=ST[391], top=ST[392], bottom=ST[393], reboiler=ST[394], packing=False, stages=15, spec="SS", esd=True,
        hazard="H2S, NH3, HCN, CO2 sour vapour", mat="A: CS, SS internals",
        notes=[f"Feed 391 = Rev B condensate 28 ({N['cond28']:.1f} t/h, from V-203, area 40) + flash condensate 353; overhead {SOUR_OVHD_FRAC*100:.0f} % of feed (A), reboiler steam {SOUR_STEAM_RATIO} t/t (A 0.10-0.25).",
               f"Template diameter uses the overhead flow only (0.5 m); the reboiler steam ({ST[394].flow:.1f} t/h) passes up the column: by the same 2 m/s rule D = {math.sqrt(4*ST[394].q/(math.pi*2.0)):.1f} m (D). Overhead acid gas goes to the sour-gas header (area 40, not drawn); dissolved H2S, NH3, CO2 not quantified (gap).",
               f"Stripped water 393: {ST[330].flow:.1f} t/h to C-137 top, {ST[395].flow:.1f} t/h to T-144, rest {ST[396].flow:.1f} t/h export (area 80)."]))
    # ---- 321 EDV and flare
    sh = sheet_package(pkg, A, 321, "Area 30  Relief  -  gasifier emergency depressurisation (EDV) and relief to flare", dict(
        tag="EDV-149", name="Gasifier emergency depressurisation and flare tie-in", spec="FL",
        inlets=[(ST[398], "EDV blowdown", "FL"), (ST[399], "V-102 vent", "FL")], outlets=[(ST[397], "to KO-101 / FL-101", "FL")],
        desc=["R-101 train blown down on ESD-1", "XV-30160 (BDV-101 Rev B) fails open", "restriction orifice limits flare load", "PSVs of area 30 discharge to the same header"],
        utilities=[("N2 purge", 500.0, "kg/h", "A"), ("seal gas", 100.0, "kg/h", "A")],
        interlocks=[("PSHH", "gasifier pressure high-high (ESD-1)", "0-60 bar", "HH 49 bar (A)"), ("XSO", "EDV open position", "open/closed", "alarm on open (A)"), ("AAHH", "CO / H2 detector 2oo3 (ESD-1 vote)", "0-100 % LEL", "HH 20 % LEL (A)"),
                    ("BSLL", "flame loss BE-101 (ESD-1 vote)", "on/off", "flame fail (A)"), ("HS", "manual ESD push-button HS-001", "on/off", "trip")],
        type="blowdown tie-in", op="6 bar, 300 C", hazard="hot CO/H2 release to flare",
        rows=[("EDV load", f"{ST[398].flow:.0f} t/h avg", "D,A"), ("Inventory", f"{N['m_inv']:.1f} t gas", "D,A"), ("Time", f"{EDV_MIN:g} min to 1 bar", "A"), ("Peak", "2 x average (A)", "A")],
        notes=[f"Inventory {EDV_VOL_M3:g} m3 (A 250-600) of gas at 45 bar, 300 C mean; average flow = inventory x (1 - 1/45) / {EDV_MIN:g} min; peak assumed 2 x average (A). The real peak is a flare-load case by the licensor.",
               "Relief schedule for area 30 (devices): PSV-30101 (R-101), PSV-30501 (V-102), PSV-30901 (D-133, atmosphere), PSV-31301..31501 (flash drums), PSV-32001 (C-146): see RELIEF_SCHEDULE.csv.",
               "Mass closure: 398 + 399 = 397. KO-101 and FL-101 are Rev B items (area 90). Flare-header temperature high (TAH, H 250 C A) is a further alarm not drawn."]))
    valve(sh, 300, 280, 0, "ball", act=True, color=RED); lab(sh, 300, 252, "XV-30160 (BDV-101) FO", 8.5, 700, "middle", RED)
    pkg.valves.append(["XV-30160 (BDV-101, symbol on sheet 301)", "ball", "emergency depressurisation", "R-101 train", 4, "FO (ESD)", 321])
    pkg.relief.append(["XV-30160 (BDV-101)", "R-101, E-101, E-132, F-135, VS-136, C-137 gas train", "ESD-1 emergency depressurisation", "n/a (opens on trip)", "A", "KO-101 / FL-101 (area 90)", "not sized: flow by inventory / time (D)", 321])
    # ---- 322 nitrogen
    sh = sheet_package(pkg, A, 322, "Area 30  Utilities  -  nitrogen purge and inerting header", dict(
        tag="N2-150", name="Nitrogen purge and inerting header", spec="N2",
        inlets=[(ST[380], "N2 from ASU-101", "N2")], outlets=[(ST[381], "burners, R-101", "N2"), (ST[382], "F-135 pulse", "N2"), (ST[383], "V-102 re-press.", "N2")],
        desc=["56 bar N2 from ASU-101 (Rev B stream 26 surplus)", "double block and bleed per user", "check valve at every connection to process", "purge-before-start and purge-after-trip"],
        utilities=[("other users", ST[384].flow, "t/h", "A"), ("N2 total", ST[380].flow, "t/h", "D")],
        interlocks=[("PALL", "N2 header pressure low-low (inhibit start; trip purge-dependent)", "0-80 bar", "LL 45 bar (A)"), ("PAL", "N2 header pressure low", "0-80 bar", "L 50 bar (A)"), ("AAL", "O2 deficiency, N2 header area", "0-25 %", "L 19.5 % (A)"),
                    ("XSC", "user DBB valves proved closed", "limit", "before process start (A)"), ("FI", "N2 flow to each user", "per user", "-")],
        esd=False, type="header and distribution", op="25 C, 56 bar",
        hazard="N2 asphyxiation, syngas back-flow",
        rows=[("R-101 purge", f"{ST[381].flow:.1f} t/h", "A"), ("F-135 pulse", f"{ST[382].flow:.1f} t/h", "A"), ("V-102", f"{ST[383].flow:.1f} t/h", "D"), ("Other", f"{ST[384].flow:.1f} t/h", "A")],
        notes=["Stream 384 (other users, flare purge tie-ins and instrument purges) is shown as a utility entry. Average flows; the V-102 repressurisation flow is the same gas volume as the vent 324 (D). Other users (A 0.5-1.5 t/h): flare purge tie-ins, instrument purges.",
               "Check valves and DBB on every user line are mandatory: syngas back-flow into the N2 header is a contamination and toxicity path.",
               "Pressure level 56 bar is an A (5 bar above gasifier feed pressure); the ASU stream 26 is at 1 bar in Rev B, so an N2 compressor is implied in area 10."]))
    ln = [r[0] for r in pkg.lines if r[-1] == 322 and str(r[4]) == "380"][0]
    blockv(sh, pkg, sh, 300, 280, 0, "XV-32250", ln, 4, "ball", "N2 header isolation on ESD", "FC (ESD)", act=True); lab(sh, 300, 252, "XV-32250 FC", 8.5, 700, "middle", RED)
    return pkg


# ---------------------------------------------------------------------------------------------------------------------
def lint(pkg):
    out = []
    tags = [r[0] for r in pkg.equip]
    dup = sorted({t for t in tags if tags.count(t) > 1})
    out.append(("duplicate equipment tags", dup)); assert not dup, dup
    nodest = [r for r in pkg.relief if not r[5]]; out.append(("relief rows without destination", len(nodest))); assert not nodest
    ids = {k[0] for k in STREAMS}
    import re
    used = set()
    for sh in pkg.sheets:
        svg = sh.svg()
        for m in re.finditer(r'<polygon points="([-\d.]+),([-\d.]+) [^"]*" fill="#fff"[^>]*/>\s*<text[^>]*>([^<]+)</text>', svg): used.add(m.group(3))
    missing = sorted(x for x in used if x.isdigit() and x not in ids); out.append(("diamond numbers not in STREAMS", missing)); assert not missing, missing
    no_esd = []
    toxic = {301, 302, 303, 305, 307, 308, 310, 311, 312, 313, 314, 315, 316, 320, 321, 322}
    for sh in pkg.sheets:
        if sh.no in toxic and not any(v[6] == sh.no and "ESD" in str(v[5]) for v in pkg.valves): no_esd.append(sh.no)
    out.append(("toxic/flammable-gas sheets without ESD valve", no_esd)); assert not no_esd, no_esd
    return out


def main():
    global PKG
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID", "Rev B balance scaled K=%.4f; capacity per ICRA/PIB (see docs/pid/analogues)" % K)
    build(pkg); pkg.total = len(pkg.sheets)
    write_html(pkg.sheets, "/tmp/area30.html", "Area 30 gasification, syngas cooling, scrubbing and water systems", previews=True)
    if "--registers" in sys.argv: pkg.write_registers(sys.argv[sys.argv.index("--registers") + 1])
    for k, v in lint(pkg): print("lint:", k, "->", v)
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices, {len(pkg.valves)} valves")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Coal-to-urea unit P&IDs, area 50: acid gas removal (physical-solvent concept), CO2 to K-601, Claus-type sulphur recovery with tail-gas
treatment, final purification by methanation (Rev B streams 9V, 10, 11, 12, 13, 29 and the H2 to the loop).

Usage: python3 scripts/urea_area_50.py        -> /tmp/area50.html (+ previews) and the lint
Depends on urea_area_40.py only for the water-vapour pressure (Antoine, A, checked there against the Rev B CoolProp value) and cp helper.

Number discipline: S sourced (document named, Rev B constants in gen_pid_urea.py), D derived (formula here), A assumed (range stated). The
physical-solvent loop is a GENERIC concept with screening coefficients (no vendor data): the Rev B module acid_gas_removal.py is a mass-balance
split / Kremser screening and carries no solvent properties, so solvent circulation, loadings and duties below are tag A throughout.
"""
import sys, os, math, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *
import urea_area_40 as a40
from urea_area_40 import psat_bar

MW50 = dict(g.MW); MW50.update({"SO2": 64.06, "S": 32.06})
CP50 = dict(a40.CP); CP50.update({"SO2": 45.0, "S": 30.0, "O2": 32.0})       # J/mol/K, A, +-15 %


def mass50(sp): return sum(n * MW50[k] for k, n in sp.items()) / 1000.0          # kg/s at Rev B scale
def cpm50(sp): n = sum(sp.values()); return sum(v * CP50[k] for k, v in sp.items()) / n
def tph50(sp): return mass50(sp) * 3.6 * K


_SEQ = [0]
def nid():
    _SEQ[0] += 1; return f"5{_SEQ[0]:02d}"


def mk(i, name, phase, sp, T, P, rho=None):
    mol = sum(sp.values())
    return St(i, name, phase, tph50(sp), T, P, mw=mass50(sp) / mol * 1000, rho=rho)


def liq(i, name, t_h, T, P, rho=1000.0): return St(i, name, "liq", t_h, T, P, rho=rho)


def close(a, b, tol=2e-4, what=""): assert abs(a - b) <= tol * max(abs(a), abs(b), 1e-9), f"closure {what}: {a} vs {b}"


# ====================== assumed screening constants (A, with ranges) ======================================================
RHO_SOLV = 1000.0      # kg/m3 generic physical solvent, A (950-1100)
CP_SOLV = 2.0          # kJ/kg/K, A (1.8-2.2)
K_CO2 = 3.0e-3         # kg CO2 per kg solvent per bar CO2 partial pressure at the absorber temperature, A (2e-3 - 5e-3); NOT vendor data
APPROACH = 0.60        # rich-solvent loading as fraction of equilibrium with feed gas, A (0.5-0.8)
H_DISS = 340.0         # kJ per kg CO2 dissolved (heat of absorption incl. condensation), A (250-400)
X_HP = 0.06            # share of dissolved CO2 released in the HP flash and recycled via K-301, A (0.03-0.10)
F_SLIP = 0.10          # share of flashed rich solvent sent to the hot H2S stripper C-302, A (0.05-0.30)
T_ABS_LEAN = 5.0       # lean solvent temperature to C-301, C, A (-10 to 10)
T_REG = 120.0          # C-302 bottom temperature, C, A (100-160)
EPS_RL = 0.90          # rich/lean exchanger effectiveness, A (0.8-0.95)
STRIP = 10.0           # kg stripping vapour per kg H2S in C-302, A (5-20)
LL_MAX = 100.0         # packed-column liquid load limit, m3/m2/h, A (50-150) -> column diameter / number of trains
D_MAX = 5.0            # maximum single-shell diameter, m, A (4-6)
DP_PUMP = 50.0         # bar, lean pump head to C-301 (45 bar + hold-up and line drop), A
P_HP, P_LP = 18.0, 2.0 # flash pressures, bar, A (HP 10-25); LP 2 bar = Rev B stream 10 pressure
COP_FRAC, T_EVAP, T_COND = 0.55, -5.0, 40.0   # refrigeration: fraction of Carnot COP (0.45-0.65), evaporation / condensing C, A
LEAK = 1.05            # 5 % extra chiller load for heat leak / unlisted, A
LAT_W, CP_WL = a40.LAT_W, a40.CP_WL

# ====================== AGR derived quantities ===========================================================================
S9, S10, S11, S12, S13, S28, S29 = g.S[9], g.S[10], g.S[11], g.S[12], g.S[13], g.S[28], g.S[29]
S9V = dict(S9); S9V["H2O"] = S9["H2O"] - S28["H2O"]                              # V-203 vapour (Rev B 9 less 28), D
close(mass50(S9V), mass50(S10) + mass50(S11) + mass50(S12), 2e-4, "9V = 10+11+12 (Rev B AGR split)")
M10, M11 = tph50(S10), tph50(S11)
N_CO2_FEED = S9V["CO2"] / sum(S9V.values()); PP_CO2 = N_CO2_FEED * 44.0                    # bar, D (feed 44 bar)
LOAD = APPROACH * K_CO2 * PP_CO2                                                       # kg CO2 / kg solvent, D
ABS_CO2 = M10 / (1.0 - X_HP)                                                          # t/h CO2 absorbed incl. the HP-flash recycle (D)
G5 = ABS_CO2 - M10                                                                     # t/h HP flash gas = CO2 recycle (A: pure CO2, co-absorbed H2/CO not quantified)
M_L = ABS_CO2 / LOAD                                                                   # t/h lean solvent circulation (D)
M_R = M_L + ABS_CO2 + M11                                                              # t/h rich solvent
M_H = M_R - G5; M_F = M_H - M10                                                        # after HP flash, after LP flash (flashed solvent keeps the H2S)
close(tph50(S9V) + G5 + M_L, tph50(S12) + M_R, 2e-4, "C-301 closure 9V + 5G + 5L = 12 + 5R")
M_Q = F_SLIP * M_F; M_B = M_F - M_Q; M_Z = M_Q - M11                                  # slipstream to C-302, bulk, regenerated slipstream
close(M_B + M_Z, M_L, 1e-9, "lean = bulk + regenerated slip")
Q_ABS = ABS_CO2 / 3.6 * H_DISS / 1000.0                                               # MW heat of absorption (D)
DT_RICH = Q_ABS * 1000 / (M_L / 3.6 * CP_SOLV)                                        # K temperature rise of the rich solvent (D)
T_RICH = T_ABS_LEAN + DT_RICH
Q_PUMP = (M_L * 1000 / 3600.0 / RHO_SOLV) * DP_PUMP * 1e5 / RULES["pump_eff"] / 1e6          # MW shaft, D (same rule as the vessel template)
Q_GASCOOL = sum(S9V.values()) * K * a40.cpm(S9V) * (40.0 - 10.0) / 1e6               # MW to cool the feed gas 40 -> 10 C (D, cp A)
Q_CH = (Q_PUMP + Q_GASCOOL) * LEAK                                                    # MW chiller duty (D)
Q_CH_REF = Q_CH
COP = COP_FRAC * (T_EVAP + 273.15) / (T_COND - T_EVAP); W_REF = Q_CH / COP           # MW compressor (D)
M_NH3 = Q_CH * 1000 / g.NH3_HFG_MINUS33C * 3.6                                        # t/h NH3 circulation, latent S at -33 C (CoolProp, Rev B) used as proxy (A)
ST_RB = M11 / 3.6                                                                      # kg/s H2S
Q_SENS_REG = M_Q / 3.6 * CP_SOLV * (1 - EPS_RL) * (T_REG - T_RICH) / 1000.0           # MW residual heating after rich/lean exchange
Q_STRIP = STRIP * ST_RB * LAT_W / 1000.0                                               # MW stripping vapour latent (A)
Q_REB = Q_SENS_REG + Q_STRIP
Q_E301 = EPS_RL * M_Q / 3.6 * CP_SOLV * (T_REG - T_RICH) / 1000.0
T_E301_COLD = T_RICH + EPS_RL * (T_REG - T_RICH); T_E301_HOT = T_REG - EPS_RL * (T_REG - T_RICH)
H2S_LEAN_PPM = (M11 / M_F) * (1 - F_SLIP) / F_SLIP * 1e6                                # kg H2S per kg bulk solvent in ppm mass, D (bulk lean H2S residual)
WATER_CO2 = S10["CO2"] * K * psat_bar(5.0) / (P_LP - psat_bar(5.0)) * 18.015 / 1000 * 3.6   # t/h water vapour with the LP-flash CO2 at 5 C if saturated (D)


def liq_D(Qm3h):
    """D: shell diameter and train count from the liquid-load limit LL_MAX and the shell limit D_MAX"""
    area = Qm3h / LL_MAX; n = max(1, math.ceil(area / (math.pi / 4 * D_MAX ** 2))); D = math.sqrt(4 * area / n / math.pi)
    return n, round(round_up(D, 0.1), 1)


N_ABS, D_ABS = liq_D(M_L * 1000 / RHO_SOLV)                           # m3/h = t/h * 1000 / rho
# ====================== methanation ======================================================================================
DH_CO, DH_CO2 = 206.0, 165.0     # kJ/mol methanation enthalpy magnitudes, A (+-5 %); textbook values, not from this repo
T_M_IN = 280.0                    # C bed inlet, A (250-300)
n12 = sum(S12.values())
MOX = S12["CO"] * DH_CO + S12["CO2"] * DH_CO2                                          # kW at Rev B scale
cp_m = cpm50(dict(S12, CH4=0.0)) if False else a40.cpm(dict(S12))
DT_AD = MOX * 1000 / (n12 * cp_m) if False else MOX * 1000 / (n12 * cp_m)              # K adiabatic rise if converted in one bed (D)
T_M_B1 = T_M_IN + DT_AD / 2; T_M_B2 = T_M_IN + DT_AD / 2                                # two beds, equal heat split (A), interbed cooler to T_M_IN
SPEC_METH = dict(S12); 
MO = {k: v for k, v in g.S[12].items()}
MO["H2"] = S12["H2"] - g.B.meth_h2; MO["CO"] = 0.0; MO["CO2"] = 0.0; MO["CH4"] = S12["CO"] + S12["CO2"]
MO["H2O"] = S12["H2O"] + S12["CO"] + 2 * S12["CO2"]
close(mass50(MO), mass50(S12), 2e-4, "R-301 closure")
S13c = g.S[13]
VAP_V302 = MO["H2O"] - S29["H2O"]
GAS_V302 = {k: v for k, v in MO.items() if k != "H2O"}; GAS_V302["H2O"] = VAP_V302
H2P = {"H2": MO["H2"]}
RES13 = {k: v for k, v in GAS_V302.items() if k != "H2"}
close(mass50(S12), mass50(S29) + mass50(GAS_V302), 2e-4, "V-302 closure")
close(mass50(GAS_V302), mass50(H2P) + mass50(S13c), 2e-4, "PU-301 closure vs Rev B stream 13")
Q_E304 = n12 * K * cp_m * (250.0 - 10.0) / 1e6                                         # MW feed (10 -> 250 C) preheat from effluent heat
T_E304_HOT_OUT = T_M_B2 - Q_E304 * 1e6 / (sum(MO.values()) * K * a40.cpm({k: v for k, v in MO.items() if v > 0}))
Q_E305 = sum(MO.values()) * K * a40.cpm({k: v for k, v in MO.items() if v > 0}) * (T_M_B1 - T_M_IN) / 1e6
Q_METHCOOL, W_METH = a40.cool_duty_MW(MO, T_E304_HOT_OUT, 40.0, 40.0) if T_E304_HOT_OUT > 40 else (0, 0)
# ====================== sulphur recovery (Claus, generic) ================================================================
ETA_F, ETA_1, ETA_2 = 0.65, 0.70, 0.60     # thermal-stage extent of reaction and per-converter conversion of remaining H2S/SO2, A (0.55-0.70; 0.60-0.80; 0.50-0.70)
ETA_ABS = 0.995                            # tail-gas amine absorber H2S capture, A (0.99-0.999)
X_CLAUS = 1 - (1 - ETA_F) * (1 - ETA_1) * (1 - ETA_2)
F11 = S11["H2S"]                                                                        # mol/s H2S (Rev B scale)
C_AG = S11.get("CO2", 0.0)                                                               # Rev C: CO2 co-stripped with the H2S (NETL Case 6 acid gas 34 mol % H2S); inert through the Claus train and tail-gas unit (A: no COS or CO formation, no CO2 capture in the TGT absorber)
F_TOT = F11 / (1 - ETA_ABS * (1 - X_CLAUS))                                            # D: with tail-gas H2S recycle to the furnace
R_H2S = F_TOT - F11                                                                    # recycled H2S, mol/s
O2_F = 0.5 * F_TOT                                                                      # O2 for 1/3 of the H2S to SO2 (D: H2S + 1.5 O2 -> SO2 + H2O)
AIR = {"O2": O2_F, "N2": O2_F * 0.79 / 0.21}
E_MAX = F_TOT / 3.0                                                                    # max Claus extent, mol SO2
EV = [ETA_F * E_MAX]; rem = E_MAX - EV[0]
EV.append(ETA_1 * rem); rem -= EV[1]; EV.append(ETA_2 * rem); rem -= EV[2]
S_REC = 3 * sum(EV)                                                                    # mol S atoms to liquid
assert abs(S_REC / F_TOT - X_CLAUS) < 1e-9
GAS_F = {"H2S": F_TOT * 2 / 3 - 2 * EV[0], "SO2": F_TOT / 3 - EV[0], "S": 3 * EV[0], "H2O": F_TOT / 3 + 2 * EV[0], "N2": AIR["N2"], "CO2": C_AG}
G_C1 = {k: v for k, v in GAS_F.items() if k != "S"}                                      # after sulphur condenser 1
G_R1 = dict(G_C1); G_R1["H2S"] -= 2 * EV[1]; G_R1["SO2"] -= EV[1]; G_R1["S"] = 3 * EV[1]; G_R1["H2O"] += 2 * EV[1]
G_C2 = {k: v for k, v in G_R1.items() if k != "S"}
G_R2 = dict(G_C2); G_R2["H2S"] -= 2 * EV[2]; G_R2["SO2"] -= EV[2]; G_R2["S"] = 3 * EV[2]; G_R2["H2O"] += 2 * EV[2]
G_C3 = {k: v for k, v in G_R2.items() if k != "S"}                                       # claus tail gas
TG_S = G_C3["H2S"] + G_C3["SO2"]
H2_HYD = 3 * G_C3["SO2"] * 1.2                                                          # mol/s H2, stoich x 1.2 excess (A 1.1-1.5)
G_HYD = {"H2S": G_C3["H2S"] + G_C3["SO2"], "H2O": G_C3["H2O"] + 2 * G_C3["SO2"], "N2": G_C3["N2"], "H2": H2_HYD - 3 * G_C3["SO2"], "CO2": G_C3.get("CO2", 0.0)}
close(mass50(G_C3) + mass50({"H2": H2_HYD}), mass50(G_HYD), 3e-4, "R-353 closure")
H2S_SLIP = (1 - ETA_ABS) * G_HYD["H2S"]
W_Q = G_HYD["H2O"] - G_HYD["N2"] * 0 - (G_HYD["N2"] + G_HYD["H2"] + G_HYD["CO2"]) * psat_bar(40.0) / (1.1 - psat_bar(40.0))     # mol/s condensed in the quench (D, saturated at 40 C, 1.1 bar)
W_Q = max(W_Q, 0.0)
TAIL_ABS = {"N2": G_HYD["N2"], "CO2": G_HYD["CO2"], "H2": G_HYD["H2"], "H2O": G_HYD["H2O"] - W_Q, "H2S": G_HYD["H2S"]}
R_SP = {"H2S": R_H2S}
close(R_H2S, ETA_ABS * G_HYD["H2S"], 1e-9, "recycled H2S")
O2_INC = 1.5 * H2S_SLIP + 0.5 * G_HYD["H2"] + 0.03 * (1.5 * H2S_SLIP + 0.5 * G_HYD["H2"])   # O2 incl 3 % excess (A 2-5 %), D
AIR_INC = {"O2": O2_INC, "N2": O2_INC * 0.79 / 0.21}
STACK = {"N2": G_HYD["N2"] + AIR_INC["N2"], "CO2": G_HYD["CO2"], "H2O": G_HYD["H2O"] - W_Q + G_HYD["H2"] + H2S_SLIP, "SO2": H2S_SLIP, "O2": O2_INC - 1.5 * H2S_SLIP - 0.5 * G_HYD["H2"]}
# element balances over the whole SRU + TGT (mass and S closure, asserted)
SIN = F11; SOUT = S_REC + STACK["SO2"]
close(SIN, SOUT, 1e-9, "sulphur atom balance (H2S in = liquid S + SO2 to stack)")
M_IN = mass50({"H2S": F11, "CO2": C_AG}) + mass50(AIR) + mass50({"H2": H2_HYD}) + mass50(AIR_INC)
M_OUT = mass50({"S": S_REC}) + mass50({"H2O": W_Q}) + mass50(STACK)
close(M_IN, M_OUT, 3e-4, "SRU + TGT overall mass closure")
RECOVERY = 1 - H2S_SLIP / F11
assert STACK["O2"] > 0
# temperatures / pressures (A)
T_F, T_WHB, T_C1, T_R1, T_C2, T_R2, T_C3, T_HYD = 1150.0, 300.0, 170.0, 230.0, 170.0, 210.0, 130.0, 280.0
DH_CLAUS = 100.0       # kJ/mol SO2 consumed, A (80-150): small because the reacting species are ~5-10 % of the gas
DH_HYD = 207.0         # kJ/mol SO2 hydrogenated, A (180-230)
LAT_S = 300.0          # kJ/kg latent heat of sulphur vapour condensation, A (280-320)
RES_CLAUS_S, RES_METH_S, RES_HYD_S, RES_GUARD = 4.0, 25.0, 4.0, 20.0     # catalyst-volume residence time rules, s, A


def build(pkg):
    area = "50"
    # ---------------- streams of the AGR ----------------
    s9v = St("9V", "shift gas to AGR", "gas", tph50(S9V), 40.0, 44.0, mw=mass50(S9V) / sum(S9V.values()) * 1000)
    mkc = lambda n, nm, f, T, P, rho=RHO_SOLV: liq(n, nm, f, T, P, rho)
    s12 = stream(12, "treated gas (stream 12)", "gas", T=10.0, P=40.0)         # Rev B 12; temperature A (10 C, cold from the chilled solvent)
    s10 = stream(10, "CO2 product (stream 10)", "gas", T=5.0, P=2.0)           # Rev B 10 at 2 bar; 5 C is the flash temperature (A), Rev B lists 40 C
    s11 = stream(11, "H2S acid gas (stream 11)", "gas", T=40.0, P=2.0)         # Rev B 11
    n = N_ABS
    s5l = mkc("501", "lean solvent", M_L, T_ABS_LEAN, 48.0)
    s5r = mkc("502", "rich solvent", M_R, round(T_RICH, 1), 44.0)
    s5g = St("503", "HP flash gas (CO2 recycle)", "gas", G5, round(T_RICH - 1, 1), P_HP, mw=44.01)
    s5h = mkc("504", "rich solvent after HP flash", M_H, round(T_RICH - 1, 1), P_HP)
    s5f = mkc("505", "flashed solvent (H2S retained)", M_F, T_ABS_LEAN, P_LP)
    s5q = mkc("506", "slip to H2S stripper", M_Q, T_ABS_LEAN, 3.0)
    s5qh = mkc("507", "slip after E-301", M_Q, round(T_E301_COLD, 1), 2.5)
    s5z = mkc("508", "hot regenerated slip", M_Z, T_REG, 2.5)
    s5zc = mkc("509", "regenerated slip after E-301", M_Z, round(T_E301_HOT, 1), 2.0)
    s5b = mkc("510", "bulk flashed solvent", M_B, T_ABS_LEAN, P_LP)
    s5m = mkc("511", "lean solvent, merged", M_L, round(T_ABS_LEAN + (T_E301_HOT - T_ABS_LEAN) * M_Z / M_L, 1), 2.0)
    s5p = mkc("512", "lean solvent from P-301", M_L, round(T_ABS_LEAN + 3, 1), 49.0)
    s5ch = mkc("513", "lean solvent to chiller outlet", M_L, T_ABS_LEAN, 48.0)
    close(s5b.flow + s5zc.flow, s5m.flow, 1e-9, "merge")
    # per-train views for C-301 (one of N identical trains, A)
    tr = lambda st, nm=None: St(st.n, (nm or st.name) + f" (1 of {n})", st.phase, st.flow / n, st.T, st.P, mw=st.mw, rho=st.rho_in)
    ratio = 1.0 / n
    # ---------------- 501 C-301 ----------------
    c1 = dict(tag="C-301", name=f"Acid-gas absorber, 1 of {n} trains", feed=tr(s9v), top=tr(s12), bottom=tr(s5r), feed2=tr(s5l), packing=True, stages=20, spec="A1", esd=True,
              mat="A: CS, sour service, low temp, licensor", hazard="H2S/CO toxic, H2 flammable, 44 bar",
              notes=[f"Generic physical-solvent concept (A): feed {s9v.flow:.0f} t/h gas, CO2 partial pressure {PP_CO2:.1f} bar (D), rich loading {LOAD*1000:.1f} g CO2 per kg solvent = {APPROACH:.2f} x {K_CO2*1000:.1f} g/kg/bar x pCO2 (A; no vendor data).",
                     f"Lean circulation {M_L:,.0f} t/h ({M_L/RHO_SOLV*1000:,.0f} m3/h at {RHO_SOLV:.0f} kg/m3 A); at {LL_MAX:.0f} m3/m2/h liquid load (A) this needs {n} shells of {D_ABS:.1f} m (D). The column template gives a vapour-velocity diameter only, patched here.",
                     f"Solvent leaves at {T_RICH:.1f} C: heat of absorption {Q_ABS:.1f} MW ({H_DISS:.0f} kJ/kg CO2, A) over {M_L/3.6*CP_SOLV:,.0f} kW/K (D).",
                     "Rev B treated-gas pressure is 40 bar against 44 bar feed: a 4 bar drop across absorber and lines is carried as Rev B boundary data. Co-absorbed H2/CO is not quantified (needs solubility data); the HP flash recycle is drawn as pure CO2.",
                     "The column template has no re-boiler on an absorber; none is drawn. The lean solvent top feed is the 5L stream (per train)."])
    sh = sheet_column(pkg, area, 501, f"Area 500  AGR  -  C-301 acid-gas absorber (1 of {n} trains)", c1)
    _patch_diam(pkg, sh, "C-301", tr(s9v), tr(s12), D_ABS, "liquid load")
    # ---------------- 502 V-303 HP flash drum ----------------
    sheet_vessel(pkg, area, 502, "Area 500  AGR  -  V-303 rich-solvent HP flash drum (flash-gas recycle)",
                 dict(tag="V-303", name="HP flash drum", inlet=St("502", f"rich solvent (all {n} trains)", "liq", M_R, s5r.T, P_HP + 2, rho=RHO_SOLV), gas=s5g, liq=s5h, res_min=3.0, spec="A1", svc_in="SL", svc_gas="SG", svc_liq="SL",
                      mat="A: CS, sour, low temp, licensor", hazard="CO2 (asphyxiant) + H2S, 18 bar", relief_dest="flare header",
                      notes=[f"Flashes {G5:.1f} t/h CO2 ({X_HP*100:.0f} % of the absorbed CO2, A 3-10 %) with the co-absorbed H2/CO to K-301 for recycle to C-301 feed (internal recycle: C-301 closure 9V + 5G + 5L = 12 + 5R asserted).",
                             "Drum sized by the vessel template (5 min liquid residence, A); inlet is let down through a level control valve upstream (not drawn), optionally through a power-recovery turbine (A, not sized)."]))
    # ---------------- 503 K-301 flash gas recycle compressor ----------------
    kw_k = G5 / 3.6 * 1000 / 44.01 * 8.314 * 288.0 * math.log(44.0 / P_HP) / 0.75 / 1e6 * 1.4 / 0.4          # rough polytropic-ish: ideal isothermal x gamma factor (A), MW
    kw_k = G5 / 3.6 / 44.01 * 8.314 * 288.0 * math.log(44.0 / P_HP) / 0.75 / 1000.0 * 1.3                  # MW: n R T ln(Pr) / eta, 1.3 factor for non-isothermal (A)
    sheet_compressor(pkg, area, 503, "Area 500  AGR  -  K-301 HP flash-gas recycle compressor",
                     dict(tag="K-301", name="Flash-gas recycle compressor", suction=s5g, discharge=St("563", "recycle gas to C-301 feed", "gas", G5, 90.0, 44.0, mw=44.01),
                          power_MW=kw_k, driver="motor", spec="A1", hazard="CO2 + H2S, H2 traces, 44 bar discharge",
                          notes=[f"Power {kw_k:.2f} MW = n R T ln(P2/P1) / 0.75 x 1.3 (A: isothermal reference, 1.3 non-isothermal factor, efficiency 0.75). A vendor curve replaces it.", "Recycle returns to the C-301 gas feed upstream of the absorber (not drawn)."]))
    # ---------------- 504 V-304 LP flash drum + pump P-302 ----------------
    sheet_vessel(pkg, area, 504, "Area 500  AGR  -  V-304 LP flash drum (CO2 product, stream 10) and P-302 transfer pumps",
                 dict(tag="V-304", name="LP flash drum (CO2 release)", inlet=St("504", "rich solvent to LP flash", "liq", M_H, s5h.T, 6.0, rho=RHO_SOLV), gas=s10, liq=s5f, res_min=5.0, pumps="P-302", pump_dp_bar=3.0, spec="A1", internals="demister",
                      svc_in="SL", svc_gas="SG", svc_liq="SL", mat="A: CS, low temp (to -30 C, A)", hazard="CO2 asphyxiant; H2S in liquid", relief_dest="atmosphere via vent stack (A) / flare",
                      notes=[f"Releases the whole CO2 product, stream 10 ({M10:.1f} t/h, Rev B), at {P_LP:.0f} bar; flash cooling absorbs {Q_ABS:.1f} MW so the solvent leaves near {T_ABS_LEAN:.0f} C (A).",
                             f"Flashed solvent {M_F:,.0f} t/h still carries all of the H2S ({M11:.1f} t/h, Rev B stream 11); the H2S slip stays in the liquid (H2S far more soluble than CO2: qualitative, needs data).",
                             f"Rev B stream 10 is pure CO2; saturated at 5 C and {P_LP:g} bar it would carry {WATER_CO2:.2f} t/h of water (D, Antoine A), dealt with in D-301. Rev B ignores it (0.2 % of the CO2)."]))
    # ---------------- 505 E-301 rich/lean exchanger ----------------
    sheet_hx(pkg, area, 505, "Area 500  AGR  -  E-301 slip-stream rich / lean solvent exchanger",
             dict(tag="E-301", name="Rich / lean solvent exchanger", hot_in=s5z, hot_out=s5zc, cold_in=s5q, cold_out=s5qh, duty_MW=Q_E301, kind="liq_liq", spec="A1", spec_c="A1", svc_c="SL",
                  esd_hot=True, hazard="H2S-bearing solvent, 120 C", mat="A: CS / 316 clad, licensor",
                  notes=[f"Effectiveness {EPS_RL:.2f} (A, 0.8-0.95): rich slip {T_RICH-DT_RICH:.0f}..{T_ABS_LEAN:.0f} C heated to {T_E301_COLD:.0f} C, lean slip cooled {T_REG:.0f} -> {T_E301_HOT:.0f} C; duty {Q_E301:.1f} MW (D).",
                         f"Only the H2S-loaded slip ({F_SLIP*100:.0f} % of the flash solvent, A 5-30 %) is heated: heating the whole {M_F:,.0f} t/h would need ~{M_F/3.6*CP_SOLV*(T_REG-T_RICH)/1000:,.0f} MW (D)."]))
    # ---------------- 506 C-302 regenerator ----------------
    lp = simple("514", "LP steam to C-302 reboiler", "steam", Q_REB * 1000 / a40.HFG_6BAR * 3.6, 159.0, 6.0, mw=18.015)
    c2 = dict(tag="C-302", name="H2S stripper / solvent regenerator", feed=s5qh, top=s11, bottom=s5z, packing=True, stages=15, reboiler=lp, spec="A1", esd=True,
              mat="A: 316 clad CS, sour, licensor", hazard="H2S toxic 2 bar; hot solvent",
              notes=[f"Strips the slip ({M_Q:,.0f} t/h) to give stream 11 (Rev B H2S, {M11:.2f} t/h) overhead and regenerated slip ({M_Z:,.0f} t/h) at {T_REG:.0f} C (A).",
                     f"Reboiler {Q_REB:.1f} MW = residual sensible {Q_SENS_REG:.1f} + stripping vapour {Q_STRIP:.1f} (strip ratio {STRIP:.0f} kg/kg H2S, A 5-20 x {LAT_W:.0f} kJ/kg A); LP steam 6 bar.",
                     f"Bulk lean solvent keeps {H2S_LEAN_PPM:,.0f} ppm (mass) of H2S because only {F_SLIP*100:.0f} % is regenerated (D): this limits H2S removal and may not reach the Rev B 99.9 %; a deeper strip (higher slip share) is the lever. Needs equilibrium data (gap).",
                     "Rev C: stream 11 is the acid gas with 34 mol % H2S and the balance taken as co-stripped CO2 (NETL Case 6 p.266, balance A); the CO2 passes through the Claus train as an inert (no COS or CO formation, A) so the sulphur unit sees about three times the gas volume of pure H2S. No enrichment stage is drawn (gap).",
                     "Overhead condenser, reflux drum and sour-water return are not in the column template and are not drawn (listed gap)."])
    sh = sheet_column(pkg, area, 506, "Area 500  AGR  -  C-302 H2S stripper / solvent regenerator with reboiler", c2)
    n2, d2 = liq_D(M_Q * 1000 / RHO_SOLV)
    _patch_diam(pkg, sh, "C-302", s5qh, s11, d2 if n2 == 1 else D_MAX, "liquid load")
    # ---------------- 507 V-305 lean surge + P-301 ----------------
    sheet_vessel(pkg, area, 507, "Area 500  AGR  -  V-305 lean-solvent surge drum and P-301 lean solvent pumps",
                 dict(tag="V-305", name="Lean solvent surge drum", inlet=s5m, liq=s5p, res_min=5.0, pumps="P-301", pump_dp_bar=DP_PUMP, spec="A1", svc_in="SL", svc_liq="SL", mat="A: CS, low temp",
                      hazard="solvent with H2S traces; HP pumps", relief_dest="closed drain / flare (A)",
                      notes=[f"P-301 (Rev B tag): {M_L:,.0f} t/h, dP {DP_PUMP:.0f} bar (A) -> {Q_PUMP:.1f} MW shaft (D); the vessel template draws 2 x 100 %, but at this size 3 x 50 % or a hydraulic turbine on the rich side are the usual alternatives (A, not drawn).",
                             f"Pump heat adds about {Q_PUMP*1000/(M_L/3.6*CP_SOLV):.1f} K to the solvent (D); it goes to the chiller E-302.", "Surge drum volume is the template residence-time rule (A), not a hold-up study."]))
    # ---------------- 508 E-302 chiller ----------------
    nh3v = simple("515", "NH3 refrigerant vapour from E-302", "gas", M_NH3, T_EVAP, 3.0, mw=17.031)
    nh3l = simple("516", "NH3 refrigerant liquid to E-302", "liq", M_NH3, T_EVAP, 3.5, rho=g.NH3_RHO_MINUS33C)
    sheet_hx(pkg, area, 508, "Area 500  AGR  -  E-302 lean-solvent chiller (NH3 evaporator)",
             dict(tag="E-302", name="Lean solvent chiller", hot_in=s5p, hot_out=s5ch, cold_in=nh3l, cold_out=nh3v, duty_MW=Q_CH, kind="boil", spec="A1", spec_c="A1", svc_c="NH3",
                  esd_hot=True, hazard="NH3 toxic refrigerant; cold solvent", mat="A: CS low temp, licensor", relief_dest="NH3 relief header / flare (A)",
                  notes=[f"Load {Q_CH:.1f} MW = ({Q_PUMP:.1f} pump heat + {Q_GASCOOL:.1f} feed-gas cooling 40 -> 10 C) x {LEAK:.2f} (A); the rest of the absorption heat is taken by flash cooling in V-304 (D).",
                         f"NH3 evaporating at {T_EVAP:.0f} C (A); circulation {M_NH3:.1f} t/h from the latent heat at -33 C ({g.NH3_HFG_MINUS33C:.0f} kJ/kg, CoolProp, Rev B) used as a proxy (A: lower at {T_EVAP:.0f} C, so true circulation is somewhat higher).",
                         "No cooling-water trim cooler is drawn: all solvent temperatures are below cooling-water supply (D); a start-up warm-solvent case needs one (A, not drawn). The chiller is a NH3 refrigerant evaporator (area T-/K-501 ammonia unit supplies refrigerant, A)."]))
    # ---------------- 509 RP-301 refrigeration package ----------------
    sheet_package(pkg, area, 509, "Area 500  AGR  -  RP-301 ammonia refrigeration package for the solvent chiller",
                  dict(tag="RP-301", name="NH3 refrigeration compressor, condenser and receiver", inlets=[(nh3v, "refrigerant vapour from E-302", "PG")], outlets=[(nh3l, "refrigerant liquid to E-302", "PL")], spec="A1", esd=True,
                       type="NH3 refrigeration package (A)", op=f"evap {T_EVAP:.0f} C, cond {T_COND:.0f} C", design="A", size=f"{W_REF:.1f} MW shaft (D)", relief="blocked discharge; fire",
                       desc=[f"COP = {COP_FRAC:.2f} x Carnot = {COP:.1f} (A)", f"compressor {W_REF:.1f} MW, condenser {Q_CH+W_REF:.1f} MW (D)"],
                       interlocks=[("PAHH", "suction pressure high-high (compressor trip)", "0-10 bar", "HH 6 bar (A)"), ("LAHH", "receiver level high-high", "0-100 %", "HH 90 % (A)"), ("AAHH", "NH3 gas detector, trip to ESD", "0-300 ppm", "H 25 / HH 50 ppm NH3 (A)")],
                       utilities=[("power", W_REF, "MW", "D"), ("cooling water", (Q_CH + W_REF) * 1000 / (CP_WL * 10) * 3.6, "t/h", "D, 10 K rise (A)")],
                       rows=[("Chiller load", f"{Q_CH:.1f} MW", "D"), ("Shaft power", f"{W_REF:.1f} MW", "D"), ("NH3 circulation", f"{M_NH3:.1f} t/h", "D")],
                       hazard="NH3 toxic and flammable", notes=["Refrigerant is anhydrous NH3 from the plant ammonia unit (A): refrigerant inventory and detection follow the ammonia-storage practice of the ammonia area.", "Mass closure: refrigerant vapour in = liquid out (internal circuit)."]))
    # ---------------- 510 D-301 CO2 dryer ----------------
    wet = St("517", "wet CO2 to dryer", "gas", M10 + WATER_CO2, 5.0, P_LP, mw=(M10 + WATER_CO2) / (M10 / 44.01 + WATER_CO2 / 18.015))
    dry = St("518", "dry CO2 to K-601", "gas", M10, 20.0, 1.8, mw=44.01)
    drw = liq("519", "water from dryer", WATER_CO2, 20.0, 1.8, 998.0)
    close(wet.flow, dry.flow + drw.flow, 1e-9, "D-301 closure")
    sheet_package(pkg, area, 510, "Area 500  AGR  -  D-301 CO2 dryer (twin-bed TSA) to K-601",
                  dict(tag="D-301", name="CO2 dryer, twin-bed temperature-swing", inlets=[(wet, "CO2 from V-304 (stream 10 + water)")], outlets=[(dry, "dry CO2 to K-601 suction (Rev B stream 10 content)"), (drw, "water to sour-water drain", "PL")], spec="A1", esd=True,
                       type="twin-bed TSA dryer (A)", op=f"5 C -> 20 C, {P_LP:g} bar", design="A", size="A", relief="blocked outlet",
                       desc=[f"water load {WATER_CO2*1000:.0f} kg/h (D, saturated at 5 C)", "regeneration: 5 % of CO2 heated, recycled (A)", "dew-point analyser on outlet"],
                       interlocks=[("AAH", "dryer outlet moisture high (dew point)", "-80 to 0 C", "H -40 C dew point (A)"), ("PDAH", "bed differential pressure high", "0-1 bar", "H 0.5 bar (A)"), ("AAHH", "CO2 asphyxiant gas detector, ESD", "0-5 vol %", "H 0.5 / HH 1.5 vol % (A)")],
                       utilities=[("regen heat", 0.05 * M10 * 1000 / 3600 * 0.85 * 150 / 1000, "MW", "A: 5 % slip, cp 0.85 kJ/kg/K, 150 K")], rows=[("Inlet", f"{wet.flow:.1f} t/h", "D"), ("Outlet", f"{dry.flow:.1f} t/h", "Rev B 10")],
                       hazard="CO2 asphyxiant; pressure release", notes=["Rev B stream 10 is dry CO2; the dryer protects K-601 and the urea unit from water and hydrate formation after a solvent carry-over (A).", "CO2 leaves at 20 C (reheat against plant water, A) so the K-601 suction sees dry gas above hydrate temperature; Rev B 10 lists 40 C.", "Delivery to K-601 is at about 1.8 bar after dryer drop (A); K-601 is in the urea area."]))
    # ---------------- methanation block ----------------
    s12g = mk("520", "treated gas after G-301 (stream 12)", "gas", S12, 10.0, 40.0)
    s12e = mk("521", "treated gas heated to E-304 outlet", "gas", S12, 250.0, 40.0)
    s12f = mk("522", "methanator bed-1 feed", "gas", S12, T_M_IN, 40.0)
    s12r = mk("523", "methanator bed-1 effluent", "gas", MO, round(T_M_B1, 0), 40.0)
    s12i = mk("524", "methanator bed-1 effluent after E-305", "gas", MO, T_M_IN, 40.0)
    s12o = mk("525", "methanator effluent (bed 2)", "gas", MO, round(T_M_B2, 0), 40.0)
    s12h = mk("526", "methanator effluent after E-304", "gas", MO, round(T_E304_HOT_OUT, 0), 40.0)
    sheet_reactor(pkg, area, 511, "Area 500  Purification  -  G-301 sulphur guard bed (protects the methanation catalyst)",
                  dict(tag="G-301", name="Sulphur guard bed (ZnO-type, A)", feed=s12, eff=s12g, vol_m3=s12.q * RES_GUARD, beds=1, spec="A1", mat="A: CS, licensor", hazard="H2, CO, residual H2S 40 bar",
                       notes=[f"Rev B leaves {S12['H2S']*K*1000:.1f} mmol/s H2S ({S12['H2S']*K*34.08/1000*3600:.2f} kg/h) in stream 12 (99.9 % removal); nickel methanation catalyst is poisoned by sulphur, so a sacrificial guard bed is drawn (A).",
                              f"Bed volume {s12.q*RES_GUARD:.0f} m3 = flow x {RES_GUARD:.0f} s (A, 10-40 s).", "In = out (adsorption of ppm H2S not in the balance). Spent absorbent is a hazardous waste stream (not quantified)."]))
    sheet_hx(pkg, area, 512, "Area 500  Purification  -  E-304 methanator feed / effluent exchanger",
             dict(tag="E-304", name="Methanator feed / effluent exchanger", hot_in=s12o, hot_out=s12h, cold_in=s12g, cold_out=s12e, duty_MW=Q_E304, kind="gas_gas", spec="A1", spec_c="A1", svc_c="PG", esd_hot=True,
                  hazard="H2 rich gas 40 bar, hot", mat="A: low-alloy, hot H2 service, licensor",
                  notes=[f"Duty {Q_E304:.1f} MW heats the treated gas from 10 to 250 C (D, cp A); bed-1 inlet {T_M_IN:.0f} C is trimmed by the start-up / trim heater (not drawn, A).", "Exit temperature of the hot side follows from the same duty (D)."]))
    q_em = a40.cpm({k: v for k, v in MO.items() if v > 0})
    bfw5 = simple("527", "BFW to E-305", "liq", 0.0, 105.0, 10.0, rho=955.0); stm5 = simple("528", "LP steam from E-305", "steam", 0.0, 159.0, 6.0, mw=18.015)
    m5 = Q_E305 * 1000 / (a40.HFG_6BAR + CP_WL * 54.0); bfw5.flow = stm5.flow = m5 * 3.6
    sheet_reactor(pkg, area, 513, "Area 500  Purification  -  R-301 methanator (2 beds, interbed cooling E-305)",
                  dict(tag="R-301", name="Methanation reactor", feed=s12f, eff=s12o, vol_m3=s12f.q * RES_METH_S, beds=2, spec="A1", mat="A: low-alloy / Cr-Mo, hot H2, licensor", hazard="H2 40 bar; runaway; CO/ CO2 breakthrough",
                       notes=[f"Rev B: CO and CO2 fully converted (3 H2 per CO, 4 H2 per CO2: {g.B.meth_h2*K:.0f} mol/s H2 consumed, Rev B). Oxides in stream 12 are {(S12['CO']+S12['CO2'])/n12*100:.1f} mol %.",
                              f"Heat of reaction {MOX*K/1000:.1f} MW (D; 206 / 165 kJ/mol CO / CO2 A). One adiabatic bed would rise {DT_AD:.0f} K ({T_M_IN:.0f} -> {T_M_IN+DT_AD:.0f} C, D): two beds with interbed cooler E-305 give {T_M_B1:.0f} C per bed.",
                              "FINDING: 4 mol % oxides is far above the usual methanator duty (a fraction of 1 mol %): either the CO2 removal in AGR is deepened or the methanator is replaced by a nitrogen wash / PSA, as the Rev B sheet 6 already suggests (ISD 3). Not changed here.",
                              f"Interbed steam raising E-305: {Q_E305:.1f} MW (D), LP steam {m5*3.6:.0f} t/h (A hfg). Catalyst volume {s12f.q*RES_METH_S:.0f} m3 = flow x {RES_METH_S:.0f} s (A).",
                              "The template TAHH trip is effluent + 60 C; set bed limits from the catalyst licensor (A)."]))
    sheet_hx(pkg, area, 514, "Area 500  Purification  -  E-305 methanator interbed steam generator",
             dict(tag="E-305", name="Methanator interbed cooler (LP steam)", hot_in=s12r, hot_out=s12i, cold_in=bfw5, cold_out=stm5, duty_MW=Q_E305, kind="steam_gen", spec="A1", spec_c="A1", svc_c="BW", esd_hot=True,
                  hazard="H2 rich gas 40 bar, hot", mat="A: low-alloy, hot H2", relief_dest="steam vent (A)", notes=[f"Cools bed-1 effluent {T_M_B1:.0f} -> {T_M_IN:.0f} C ({Q_E305:.1f} MW, D). Steam side relief is a boiler-package item."]))
    v302in = mk("529", "methanator effluent cooled", "twophase", MO, 40.0, 40.0); v302in.rho_in = None
    v302g = mk("530", "gas to PU-301", "gas", GAS_V302, 40.0, 39.5)
    v302c = St(29, "condensate (stream 29)", "liq", tph50(S29), 40.0, 40.0, rho=992.0)
    close(v302in.flow, v302g.flow + v302c.flow, 2e-4, "V-302 flow")
    v302in.mw = v302g.mw; v302in.rho_in = v302g.rho
    sheet_vessel(pkg, area, 515, "Area 500  Purification  -  V-302 methanator effluent knock-out drum and P-304 condensate pumps",
                 dict(tag="V-302", name="Methanator effluent KO drum", inlet=v302in, gas=v302g, liq=v302c, res_min=5.0, pumps="P-304", pump_dp_bar=6.0, spec="A1", internals="demister", svc_in="PG", svc_gas="PG", svc_liq="PC",
                      mat="A: CS, hot H2 below 200 C", hazard="H2 rich gas 40 bar",
                      notes=[f"Effluent from E-304 ({T_E304_HOT_OUT:.0f} C) is cooled to 40 C by a cooling-water cooler E-306 (duty {Q_METHCOOL:.1f} MW, D, includes {W_Q if False else (S29['H2O']*K*18.015/1000):.1f} kg/s water condensed; not given its own sheet).",
                             "Condensate is stream 29 (Rev B, A): water formed by methanation, to the sour-water stripper; gas goes to the final purification PU-301.", "V-302 mass closure 12 = 29 + gas (asserted)."]))
    sheet_package(pkg, area, 516, "Area 500  Purification  -  PU-301 final H2 purification (PSA / cryogenic wash concept)",
                  dict(tag="PU-301", name="Final hydrogen purification", inlets=[(v302g, "gas from V-302")], outlets=[(mk("531", "purified H2 to K-401", "gas", H2P, 40.0, 38.0), "H2 to loop make-up (K-401)"), (St(13, "purification residual (stream 13)", "gas", tph50(S13c), 40.0, 5.0, mw=mass50(S13c) / sum(S13c.values()) * 1000), "residual to fuel (Rev B 13)")],
                       spec="A1", esd=True, type="PSA or N2-wash concept (A)", op="40 bar, 40 C", design="A", size="A", relief="blocked outlet",
                       desc=["removes CH4, N2, vapour, H2S", "Rev B assumes 100 % H2 recovery (A)", "N2 wash option: ASU N2 (stream 14)"],
                       interlocks=[("AAH", "CO + CO2 in purified H2 (ammonia catalyst poison)", "0-20 ppm", "H 5 ppm / HH 10 ppm trip (A)"), ("PAHH", "feed pressure high-high", "0-50 bar", "HH 46 bar (A)"), ("AAHH", "H2 / H2S detector at unit, ESD", "0-100 %LEL", "H 20 / HH 40 %LEL (A)")],
                       rows=[("H2 to loop", f"{tph50(H2P):.1f} t/h", "D, Rev B"), ("Residual (13)", f"{tph50(S13c):.1f} t/h", "Rev B 13")],
                       hazard="H2 flammable, high pressure", notes=["Rev B has an implied H2 purifier: stream 13 is everything but H2, and 100 % of the H2 goes to K-401. A real PSA recovers about 85-90 % (A, not computed) and a nitrogen wash would deliver H2 + N2 with ppm-level oxides.", f"Decision: no separate N2 wash is drawn: the Rev B balance already supplies the loop N2 from ASU stream 14 at K-401 and does not need a wash; PU-301 is a concept box until the licensor fixes the process.", "Mass closure V-302 gas = H2 + stream 13 asserted in code (Rev B stage check)."]))
    # ---------------- sulphur recovery ----------------
    air = mk("532", "combustion air (blower)", "gas", AIR, 40.0, 1.7)
    rec = mk("533", "recycle H2S from TGT absorber", "gas", {"H2S": R_H2S}, 40.0, 1.8)
    s11b = stream(11, "H2S acid gas (stream 11)", "gas", T=40.0, P=2.0)
    furn_in = {"H2S": F_TOT}; furn_in_all = add_dict(furn_in, AIR)
    furn = mk("534", "furnace gas", "gas", add_dict(GAS_F, {}), T_F, 1.5)
    close(s11b.flow + rec.flow + air.flow, furn.flow, 3e-4, "F-351 closure")
    sheet_package(pkg, area, 517, "Area 500  Sulphur recovery  -  F-351 Claus reaction furnace (thermal stage)",
                  dict(tag="F-351", name="Claus reaction furnace and burner", inlets=[(s11b, "stream 11 acid gas (ESD)"), (air, "combustion air from blower"), (rec, "TGT recycle H2S")], outlets=[(furn, "furnace gas to E-351 WHB")], spec="A1", esd=True,
                       type="refractory furnace + BMS (A)", op=f"{T_F:.0f} C, 1.5 bar (A)", design="A", size="A", relief="explosion relief / PSV to safe location",
                       desc=[f"air {AIR['O2']*K:.0f} O2 + {AIR['N2']*K:.0f} N2 mol/s (1/3 H2S to SO2)", f"thermal extent {ETA_F:.2f} of Claus equilibrium max (A 0.55-0.70)", "acid gas 34 mol % H2S + CO2 (Rev C): flame-T limit, split flow (A, gap)"],
                       interlocks=[("BSL", "burner flame scanner (2oo3) low: trip", "flame", "no flame: close acid gas + air (A)"), ("FFIC", "air / acid-gas ratio control (trim by tail-gas H2S:SO2 analyser)", "ratio", "stoich 0.5 mol O2 per mol H2S (D)"), ("AAHH", "H2S gas detectors at burner platform: ESD", "0-100 ppm", "H 10 / HH 15 ppm (A)"),
                                   ("TAHH", "furnace temperature high-high (refractory)", "0-1500 C", "HH 1300 C (A)"), ("AIT", "tail-gas H2S:SO2 ratio analyser", "0-10", "ratio set 2.0 (D)")],
                       rows=[("H2S fed", f"{F_TOT*K:.1f} mol/s (incl. recycle {R_H2S*K:.1f})", "D"), ("Air", f"{air.flow:.1f} t/h", "D"), ("Sulphur recovery overall", f"{RECOVERY*100:.2f} %", "D (A: eta)")],
                       hazard="H2S/SO2 toxic, hot furnace",
                       notes=["Stoichiometry: H2S + 1.5 O2 -> SO2 + H2O for one third of the H2S; 2 H2S + SO2 -> 3 S + 2 H2O in the furnace and converters (D; thermodynamic equilibrium is not computed, extents are A).", "Rev C: the acid gas is 34 mol % H2S with CO2 inert, which moderates the flame; the flame temperature with the CO2 diluent is not recomputed and the split-flow or oxygen-enrichment choice is licensor work (gap). Furnace T 1,150 C is A.", f"Mass closure 11 + air + recycle = furnace gas asserted in code; sulphur atoms: {F11*K:.1f} mol/s in = {S_REC*K:.1f} liquid + {STACK['SO2']*K:.2f} to stack (asserted)."]))
    whb_o = mk("535", "furnace gas after WHB", "gas", GAS_F, T_WHB, 1.4)
    bfw6 = simple("536", "BFW to E-351", "liq", 0.0, 105.0, 12.0, rho=955.0); st6 = simple("537", "MP steam from E-351", "steam", 0.0, 188.0, 12.0, mw=18.015)
    q351 = sum(GAS_F.values()) * K * cpm50(GAS_F) * (T_F - T_WHB) / 1e6
    m6 = q351 * 1000 / (1980.0 + CP_WL * (188 - 105)); bfw6.flow = st6.flow = m6 * 3.6
    sheet_hx(pkg, area, 518, "Area 500  Sulphur recovery  -  E-351 waste-heat boiler (MP steam)",
             dict(tag="E-351", name="Claus waste-heat boiler", hot_in=furn, hot_out=whb_o, cold_in=bfw6, cold_out=st6, duty_MW=q351, kind="steam_gen", spec="A1", spec_c="A1", svc_c="BW", esd_hot=True,
                  hazard="H2S / SO2 hot gas; boiler tube leak", mat="A: CS / refractory-lined tube sheet, licensor", relief_dest="steam vent (A)",
                  notes=[f"{q351:.1f} MW = n cp dT ({T_F:.0f} -> {T_WHB:.0f} C, cp A {cpm50(GAS_F):.1f} J/mol/K). MP steam 12 bar, hfg 1,980 kJ/kg is A (+-5 %).", "Tube-sheet and ferrule design for 1,150 C inlet is a licensor item."]))
    c1o = mk("538", "gas after sulphur condenser 1", "gas", G_C1, T_C1, 1.3)
    s1 = St("539", "liquid sulphur from E-352", "liq", tph50({"S": 3 * EV[0]}), 150.0, 1.3, rho=1800.0)
    close(tph50(GAS_F), c1o.flow + s1.flow, 3e-4, "E-352 closure")
    bf7 = simple("540", "BFW to E-352", "liq", 0.0, 105.0, 5.0, rho=955.0); st7 = simple("541", "LP steam from E-352", "steam", 0.0, 144.0, 4.0, mw=18.015)
    q352 = sum(G_C1.values()) * K * cpm50(GAS_F) * (T_WHB - T_C1) / 1e6 + s1.flow / 3.6 * LAT_S / 1000
    m7 = q352 * 1000 / (2130.0 + CP_WL * 39.0); bf7.flow = st7.flow = m7 * 3.6
    sheet_hx(pkg, area, 519, "Area 500  Sulphur recovery  -  E-352 first sulphur condenser (LP steam)",
             dict(tag="E-352", name="Sulphur condenser 1", hot_in=whb_o, hot_out=c1o, cold_in=bf7, cold_out=st7, duty_MW=q352, kind="cond", spec="A1", spec_c="A1", svc_c="BW", esd_hot=True,
                  hazard="H2S, SO2, molten sulphur", mat="A: CS, steam traced / jacketed", relief_dest="steam vent (A)",
                  notes=[f"Condenses {s1.flow:.1f} t/h sulphur (D: 3 S per Claus extent) plus sensible heat to {T_C1:.0f} C; latent heat {LAT_S:.0f} kJ/kg is A (280-320). LP steam 4 bar hfg 2,130 kJ/kg is A.", "Liquid sulphur drains by seal leg to the pit T-351; all sulphur is assumed condensed (vapour carry-over 0, A: real units lose ~1 % as vapour/mist)."]))
    r1f = mk("542", "converter 1 feed (reheated)", "gas", G_C1, T_R1, 1.3)
    t_r1o = T_R1 + EV[1] * DH_CLAUS * 1000 / (sum(G_C1.values()) * cpm50(G_C1))
    r1o = mk("543", "converter 1 effluent", "gas", G_R1, round(t_r1o, 0), 1.2)
    close(r1f.flow, r1o.flow, 3e-4, "R-351 closure")
    sheet_reactor(pkg, area, 520, "Area 500  Sulphur recovery  -  R-351 Claus converter 1",
                  dict(tag="R-351", name="Claus catalytic converter 1", feed=r1f, eff=r1o, vol_m3=r1f.q * RES_CLAUS_S, beds=1, spec="A1", mat="A: CS, refractory, licensor", hazard="H2S/SO2 toxic; sulphur fire",
                       notes=[f"Extent {EV[1]*K:.1f} mol/s SO2 ({ETA_1*100:.0f} % of what is left, A 60-80), adiabatic rise {t_r1o-T_R1:.0f} K with {DH_CLAUS:.0f} kJ/kg-mol A (80-150).", "Reheat of the feed to 230 C (A) by hot gas bypass / fired reheater is not drawn.", f"Catalyst volume {r1f.q*RES_CLAUS_S:.0f} m3 = flow x {RES_CLAUS_S:.0f} s (A 2-6)."]))
    c2o = mk("544", "gas after sulphur condenser 2", "gas", G_C2, T_C2, 1.2)
    s2 = St("545", "liquid sulphur from E-353", "liq", tph50({"S": 3 * EV[1]}), 150.0, 1.2, rho=1800.0)
    close(r1o.flow, c2o.flow + s2.flow, 3e-4, "E-353 closure")
    bf8 = simple("546", "BFW to E-353", "liq", 0.0, 105.0, 5.0, rho=955.0); st8 = simple("547", "LP steam from E-353", "steam", 0.0, 144.0, 4.0, mw=18.015)
    q353 = sum(G_R1.values()) * K * cpm50(G_R1) * (t_r1o - T_C2) / 1e6 + s2.flow / 3.6 * LAT_S / 1000
    m8 = q353 * 1000 / (2130.0 + CP_WL * 39.0); bf8.flow = st8.flow = m8 * 3.6
    sheet_hx(pkg, area, 521, "Area 500  Sulphur recovery  -  E-353 second sulphur condenser",
             dict(tag="E-353", name="Sulphur condenser 2", hot_in=r1o, hot_out=c2o, cold_in=bf8, cold_out=st8, duty_MW=q353, kind="cond", spec="A1", spec_c="A1", svc_c="BW", esd_hot=True,
                  hazard="H2S, SO2, molten sulphur", mat="A: CS, steam traced", relief_dest="steam vent (A)", notes=[f"{s2.flow:.1f} t/h sulphur condensed; same method as E-352 (D, A)."]))
    r2f = mk("548", "converter 2 feed (reheated)", "gas", G_C2, T_R2, 1.2)
    t_r2o = T_R2 + EV[2] * DH_CLAUS * 1000 / (sum(G_C2.values()) * cpm50(G_C2))
    r2o = mk("549", "converter 2 effluent", "gas", G_R2, round(t_r2o, 0), 1.1)
    close(r2f.flow, r2o.flow, 3e-4, "R-352 closure")
    sheet_reactor(pkg, area, 522, "Area 500  Sulphur recovery  -  R-352 Claus converter 2",
                  dict(tag="R-352", name="Claus catalytic converter 2", feed=r2f, eff=r2o, vol_m3=r2f.q * RES_CLAUS_S, beds=1, spec="A1", mat="A: CS, refractory, licensor", hazard="H2S/SO2 toxic; sulphur fire",
                       notes=[f"Extent {EV[2]*K:.1f} mol/s SO2 ({ETA_2*100:.0f} % of what is left, A 50-70), rise {t_r2o-T_R2:.0f} K.", f"Overall Claus recovery {X_CLAUS*100:.1f} % (D from the three A extents; no equilibrium limit computed, so the value is optimistic if the equilibrium is the limit)."]))
    c3o = mk("550", "Claus tail gas", "gas", G_C3, T_C3, 1.1)
    s3 = St("551", "liquid sulphur from E-354", "liq", tph50({"S": 3 * EV[2]}), 130.0, 1.1, rho=1800.0)
    close(r2o.flow, c3o.flow + s3.flow, 3e-4, "E-354 closure")
    hw_i = simple("552", "hot-water loop to E-354", "liq", 0.0, 60.0, 4.0, rho=985.0); hw_o = simple("553", "hot-water loop from E-354", "liq", 0.0, 100.0, 3.5, rho=960.0)
    q354 = sum(G_R2.values()) * K * cpm50(G_R2) * (t_r2o - T_C3) / 1e6 + s3.flow / 3.6 * LAT_S / 1000
    hw_i.flow = hw_o.flow = q354 * 1000 / (CP_WL * 40.0) * 3.6
    sheet_hx(pkg, area, 523, "Area 500  Sulphur recovery  -  E-354 final sulphur condenser (hot-water cooled)",
             dict(tag="E-354", name="Sulphur condenser 3 (final)", hot_in=r2o, hot_out=c3o, cold_in=hw_i, cold_out=hw_o, duty_MW=q354, kind="cond", spec="A1", spec_c="A1", svc_c="BW", esd_hot=True,
                  hazard="H2S, SO2, molten sulphur", mat="A: CS, steam traced", relief_dest="atmosphere via safe vent (A)", notes=[f"{s3.flow:.1f} t/h sulphur; outlet {T_C3:.0f} C stays above the sulphur freezing region (A); cooled by a hot-water loop (A) so that the shell does not freeze sulphur."]))
    tot_s = St("554", "liquid sulphur to pit", "liq", s1.flow + s2.flow + s3.flow, 140.0, 1.2, rho=1800.0)
    close(tot_s.flow, tph50({"S": S_REC}), 1e-9, "sulphur total")
    sh = sheet_tank(pkg, area, 524, "Area 500  Sulphur recovery  -  T-351 liquid-sulphur pit and P-351 transfer pumps",
               dict(tag="T-351", name="Liquid sulphur pit", inflow=tot_s, outflow=St("555", "liquid sulphur to loading", "liq", tot_s.flow, 140.0, 3.0, rho=1800.0), days=2.0, roof="cone", spec="A1", svc="PL", pumps="P-351", pump_dp=3.0,
                    hazard="H2S degassing; sulphur fire; 140 C",
                    notes=[f"Receives {tot_s.flow:.1f} t/h ({tot_s.flow*24:.0f} t/d, D = Rev B stream 11 sulphur x recovery in the converters) of liquid sulphur at 140 C (A).", "Pit is steam-coiled and ventilated to the incinerator (sweep air; not drawn); H2S dissolved in the sulphur (degassing) is not quantified (A).", "Tank template draws a bund and PVRV; the pit vent here goes to the TGT incinerator, not atmosphere (A)."]))
    vol_pit = _patch_tank(pkg, sh, "T-351", St("555", "liquid sulphur to loading", "liq", tot_s.flow, 140.0, 3.0, rho=1800.0), 2.0)
    # ---------------- tail-gas treatment ----------------
    hyd_in_gas = c3o
    h2s = mk("556", "hydrogen for TGT hydrogenation", "gas", {"H2": H2_HYD}, 40.0, 1.5)    # from PU-301 H2 (A)
    hy_f = mk("557", "hydrogenation feed (reheated, with H2)", "gas", add_dict(G_C3, {"H2": H2_HYD}), T_HYD, 1.2)
    t_hy_o = T_HYD + G_C3["SO2"] * DH_HYD * 1000 / (sum(hy_f_mol(G_C3, H2_HYD).values()) * cpm50(hy_f_mol(G_C3, H2_HYD)))
    hy_o = mk("558", "hydrogenation effluent", "gas", G_HYD, round(t_hy_o, 0), 1.1)
    close(c3o.flow + h2s.flow, hy_o.flow, 3e-4, "R-353 flow")
    sheet_reactor(pkg, area, 525, "Area 500  Tail gas  -  R-353 tail-gas hydrogenation reactor",
                  dict(tag="R-353", name="Tail-gas hydrogenation reactor (Co-Mo, A)", feed=hy_f, eff=hy_o, vol_m3=hy_f.q * RES_HYD_S, beds=1, spec="A1", mat="A: CS / 304H, licensor", hazard="H2 + H2S/SO2; hot",
                       notes=[f"Reduces SO2 and S vapour to H2S with H2: SO2 + 3 H2 -> H2S + 2 H2O (D stoichiometry); H2 {H2_HYD*K*2.016/1000*3600:.2f} t/h = 1.2 x stoich (A 1.1-1.5), drawn from the purified H2 (stream H2P, PU-301; not in Rev B balance, <0.1 % of loop H2: asserted below 0.3 % in code).", f"Rise {t_hy_o-T_HYD:.0f} K with {DH_HYD:.0f} kJ/mol (A 180-230).", "Feed reheated to 280 C (A, 250-320) by in-line burner or steam heater, not drawn."]))
    assert H2_HYD / H2P["H2"] < 0.003, H2_HYD / H2P["H2"]
    sw = liq("559", "quench sour water", W_Q * K * 18.015 / 1000 * 3.6, 40.0, 1.1, 995.0)
    tg_r = mk("560", "recycle H2S to F-351 (stream 533)", "gas", R_SP, 40.0, 1.8)
    air_i = mk("561", "incinerator air", "gas", AIR_INC, 40.0, 1.1)
    stk = mk("562", "stack gas", "gas", STACK, 450.0, 1.05)
    close(hy_o.flow + air_i.flow, sw.flow + tg_r.flow + stk.flow, 3e-4, "TGT-351 closure")
    sheet_package(pkg, area, 526, "Area 500  Tail gas  -  TGT-351 quench, amine absorber and incinerator / stack",
                  dict(tag="TGT-351", name="Tail-gas quench, H2S absorber and incinerator", inlets=[(hy_o, "hydrogenation effluent"), (air_i, "incinerator air")], outlets=[(stk, "stack gas (SO2 to atmosphere)"), (tg_r, "recycle H2S to F-351"), (sw, "quench sour water", "PL")],
                       spec="A1", esd=True, type="quench + amine absorber + incinerator (A)", op="40 C quench, 450 C stack", design="A", size="A", relief="blocked outlet",
                       desc=[f"H2S capture {ETA_ABS*100:.1f} % (A 99-99.9)", f"slip {H2S_SLIP*K*34.08/1000*3600:.3f} t/h H2S -> SO2 at the stack", f"quench condensate {sw.flow:.1f} t/h to sour-water stripper"],
                       interlocks=[("AAH", "stack SO2 analyser high", "0-500 ppm", "limit per consent (A, not sourced)"), ("TAL", "incinerator temperature low (unburnt H2S)", "0-900 C", "L 600 C alarm (A)"), ("AAHH", "H2S detectors at absorber, ESD", "0-100 ppm", "H 10 / HH 15 ppm (A)"), ("BSL", "incinerator flame low: trip", "flame", "A")],
                       rows=[("S recovery overall", f"{RECOVERY*100:.2f} %", "D"), ("SO2 to stack", f"{STACK['SO2']*K*64.06/1000*3.6:.3f} t/h", "D"), ("Sulphur product", f"{tot_s.flow*24:.0f} t/d", "D")],
                       hazard="H2S/SO2 toxic; hot stack gas", notes=[f"Overall: {F11*K:.1f} mol/s H2S in = {S_REC*K:.1f} mol/s S to the pit + {STACK['SO2']*K:.2f} mol/s as SO2 to the stack (atoms asserted); total mass in = out asserted (SRU + TGT).", "The absorber is the same generic amine / physical-solvent concept (A); its internal flows are not sized here (package box).", "Stack height, dispersion and the SO2 emission limit are site / consent items and were not sourced (gap)."]))
    return pkg


def add_dict(a, b):
    out = dict(a)
    for k, v in b.items(): out[k] = out.get(k, 0.0) + v
    return out


def hy_f_mol(G, h2): return add_dict(G, {"H2": h2})


def _patch_diam(pkg, sh, tag, fd, tp, D_new, why):
    """draw-around for the column template (vapour-velocity diameter only): replace the printed diameter and the register row"""
    G = max(fd.q, tp.q); D_t = round_up(math.sqrt(4 * G / (math.pi * 2.0)), 0.1)
    for i, e in enumerate(sh.p):
        e2 = re.sub(r">%.1f m ID x" % D_t, ">%.1f m ID x" % D_new, e)
        e2 = e2.replace(">%.1f m<" % D_t, ">%.1f m<" % D_new).replace("D (2 m/s A)", "D (%s, A)" % why)
        sh.p[i] = e2
    for r in pkg.equip:
        if r[0] == tag: r[5] = re.sub(r"[\d.]+ m ID", "%.1f m ID" % D_new, r[5])


def _patch_tank(pkg, sh, tag, out, days):
    """Rev C: the shared tank template now includes the t -> kg factor, so no redraw is needed; only returns the working-plus-heel volume (D)"""
    return out.flow * 1000 * 24 * days / out.rho * 1.1


def lint(pkg):
    tags = [r[0] for r in pkg.equip]
    dup = {t for t in tags if tags.count(t) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    assert all(r[5] for r in pkg.relief), "relief row without destination"
    sid = {k[0] for k in STREAMS}
    bad = {r[4] for r in pkg.lines if str(r[4]) not in sid}
    assert not bad, f"stream numbers missing from STREAMS {bad}"
    for s in pkg.sheets:
        assert any(r[6] == s.no and "ESD" in str(r[5]) for r in pkg.valves), f"sheet {s.no} has no ESD valve"
    return len(pkg.equip), len(pkg.relief)


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), area 50: AGR, CO2, sulphur, methanation", "Rev B balance scaled K=%.4f" % K)
    build(pkg); pkg.total = len(pkg.sheets)
    lint(pkg)
    write_html(pkg.sheets, "/tmp/area50.html", "Coal-to-urea area 50", previews=True)
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices")
    print(f"AGR: pCO2 {PP_CO2:.1f} bar, loading {LOAD*1000:.1f} g/kg, circ {M_L:,.0f} t/h, N_abs {N_ABS} x D {D_ABS} m, Qabs {Q_ABS:.1f} MW, Trich {T_RICH:.1f}, pump {Q_PUMP:.1f} MW, chiller {Q_CH:.1f} MW, W_ref {W_REF:.1f} MW, NH3 {M_NH3:.1f} t/h, reb {Q_REB:.1f} MW, H2S lean {H2S_LEAN_PPM:.0f} ppm, E301 {Q_E301:.1f}")
    print(f"METH: oxides {(S12['CO']+S12['CO2'])/n12*100:.1f} %, dTad {DT_AD:.0f}, beds {T_M_B1:.0f}, Q {MOX*K/1000:.1f} MW, E304 {Q_E304:.1f}, E305 {Q_E305:.1f}, hot out {T_E304_HOT_OUT:.0f}, cool {Q_METHCOOL:.1f}")
    print(f"SRU: F_TOT {F_TOT*K:.1f} mol/s, X {X_CLAUS:.3f}, S {tph50({'S': S_REC}):.2f} t/h = {tph50({'S': S_REC})*24:.0f} t/d, recovery {RECOVERY:.4f}, SO2 stack {STACK['SO2']*K:.3f} mol/s, W_Q {W_Q*K*18.015/1000*3.6:.1f} t/h, air {tph50(AIR):.1f} t/h")


if __name__ == "__main__":
    main()

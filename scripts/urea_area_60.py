#!/usr/bin/env python3
"""Area 60: ammonia synthesis loop, ammonia refrigeration, ammonia storage (unit-by-unit P&ID sheets 601-619).

Usage: python3 scripts/urea_area_60.py   (builds /tmp/area60.html with previews and runs the lint)

Basis: Rev B balance (gen_pid_urea.py) scaled by K to 3,850 t/d urea (urea_basis.py). Rev B streams used: 14, 15, 16, 17, 27, 30 (area 60);
stream 18 is the T-501 / P-501 outlet. Stream 29 (V-302 condensate) belongs to area 40 and is not drawn here.
Number tags: S sourced, D derived (formula in comment), A assumed screening value. Property values marked 'CP8' were computed in this
session with CoolProp 8.0 (HEOS, pure ammonia / water / 3:1 H2:N2 mixture) and are typed here as constants (same practice as gen_pid_urea.py:
CoolProp is not a runtime dependency). No licensor or vendor data is used. Hand-off gaps are listed in docs/pid/urea_detail/AREA_60_NOTES.md.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *
import pid_unit2
import gen_pid_urea as g

AREA = "60"
# ---- constants (CP8 = CoolProp 8.0, computed 12 Nov 2026) ---------------------------------------------------
# saturated ammonia: T C -> (P bar, hL kJ/kg, hV kJ/kg, rhoL kg/m3)
NH3 = {-33.3: (1.014, 194.5, 1564.1, 681.6), -10: (2.906, 299.7, 1595.9, 652.0), 0: (4.292, 345.7, 1607.4, 638.6), 5: (5.156, 368.8, 1612.6, 632.0),
       10: (6.148, 392.2, 1617.4, None), 25: (10.027, 463.2, 1629.0, None), 40: (15.545, 536.1, 1635.8, 579.6)}
HFG = {t: v[2] - v[1] for t, v in NH3.items()}
DHS_AB = 136.06      # kJ/kg isentropic, sat. vapour 1.014 -> 2.906 bar (CP8)
DHS_B = 247.52       # kJ/kg isentropic, sat. vapour 2.906 -> 15.545 bar (CP8)
H_STEAM_50, H_BFW = 2794.2, 444.3    # kJ/kg: sat. steam 50 bar; BFW 105 C / 55 bar (CP8)
CP_GAS = 3.55        # kJ/kg/K mean cp of 3:1 H2:N2 at 200 bar, 3-450 C (CP8, 3.48-3.61); NH3 content ignored (A)
ETA_C = 0.75         # isentropic efficiency, same as the Rev B K-401 power basis (S gen_pid_urea.K401_KJ_PER_MOL)
GAMMA = 1.4          # A: H2/N2 diatomic, for stage discharge temperature only
CP_W = 4.18          # kJ/kg/K water (CP8 4.178 at 36 C)
T_SEP, T_PRE, T_OUT, T_WHB = 0.0, 300.0, 450.0, 330.0   # A: separator, converter nozzle inlet, converter outlet (S Rev B 450 C), WHB gas outlet
DP_LOOP = 8.0        # bar, A (5-15): loop pressure drop, circulator duty
GHSV = 20000.0       # Nm3/m3/h, A (10,000-25,000): catalyst volume only
DG_FRAC = 0.003      # A (0.001-0.01): dissolved H2/N2 in liquid NH3 flashed at letdown, mass fraction of liquid
U_HP_GAS = 300.0     # W/m2/K, A (200-500): gas-gas / gas-liquid at 200 bar; pid_unit2 U_SCREEN gas_gas=60 is a low-pressure value
pid_unit2.U_SCREEN["gas_gas_hp"] = U_HP_GAS; pid_unit2.U_SCREEN["gas_liq_hp"] = U_HP_GAS * 1.5
Z_B = [(3, 6.25e-4), (40, 5.9e-4), (100, 5.35e-4), (300, 3.9e-4), (450, 3.2e-4)]   # D: Z = 1 + b(T) P, fitted to CP8 H2:N2 3:1 at 200 bar (Z 1.125, 1.118, 1.107, 1.078, 1.064)


def Zhn(T, P):
    b = Z_B[-1][1]
    for (t0, b0), (t1, b1) in zip(Z_B, Z_B[1:]):
        if T <= t1: b = b0 + (b1 - b0) * max(0.0, (T - t0)) / (t1 - t0); break
    return 1.0 + b * P


def rho_gas(T, P, mw): return P * 1e5 * mw / 1000 / (R_GAS * (T + 273.15)) / Zhn(T, P)   # D, real-gas via Zhn (NH3 content neglected, A)
def mixmw(parts): return sum(m for m, _ in parts) / sum(m / w for m, w in parts)         # parts = [(t/h, mw)]
def two_rho(mg, rg, ml, rl): return (mg + ml) / (mg / rg + ml / rl)                       # D, homogeneous two-phase density


def sg(i, name, T, P, flow, mw, phase="gas", rho=None):
    """a gas stream with real-gas density"""
    st = simple(i, name, phase, flow, round(T, 1), P, mw=mw)
    st.rho_in = rho if rho else rho_gas(T, P, mw)
    return st


def detectors(sh, pkg, lp, x=1066, y=736, what="NH3"):
    """local add-on (templates have no gas detectors): two detectors with 2oo2 voting to ESD, registered as instruments"""
    lab(sh, x - 40, y - 26, f"{what} detectors", 8.5, 700, "start", RED)
    bub(sh, pkg, sh, x - 20, y, "AT", f"{lp}71", "area", f"{what} gas detector", "0-300 ppm", "H 25 ppm / HH 150 ppm (A)")
    bub(sh, pkg, sh, x + 20, y, "AAHH", f"{lp}72", "area", f"{what} detector HH -> ESD (2oo2)", "0-300 ppm", "HH 150 ppm (A)", panel=True)
    lab(sh, x - 40, y + 26, "limits A (HSE to confirm)", 7.5, 400, "start", GREY)


def add_note_eq(pkg, tag, design):
    for r in pkg.equip:
        if r[0] == tag: r[4] = design


def fix_text(sh, old, new):
    sh.p = [x.replace(old, new) for x in sh.p]


def lvalve(sh, pkg, x, y, tag, line, size, svc, fail="FC"):
    ctrlvalve(sh, x, y, 90); pkg.valves.append([tag, "control", svc, line, size, fail, sh.no])


def balance():
    """D: material and energy closure of the synthesis loop and refrigeration circuit from Rev B streams 14-17, 27, 30 (t/h unless stated)"""
    R = {}
    s15, s27, s17, s16, s30, s14 = (g.M[i] * 3.6 * K for i in (15, 27, 17, 16, 30, 14))
    mw_g = stream(15, "x", "gas").mw
    assert abs(s15 - (s17 + s16 + s30)) < 1e-6 * s15, "Rev B stream 15 = 17 + 16 + 30 (N and H balance)"
    R.update(s15=s15, s27=s27, s17=s17, s16=s16, s30=s30, s14=s14, mw_g=mw_g)
    R["eff"] = s15 + s27                              # converter inlet mass = effluent mass (D: reaction conserves mass)
    R["purge_tot"] = s16 + s30
    R["dg"] = DG_FRAC * s17                           # A: dissolved gas in the NH3 liquid
    R["liq401"] = s17 + R["dg"]
    R["gas401"] = R["eff"] - R["liq401"]
    R["purge_loop"] = R["gas401"] - s27
    assert abs(R["purge_loop"] + R["dg"] - R["purge_tot"]) < 1e-9 * R["eff"]
    R["mw_eff"] = mixmw([(R["eff"] - s17, mw_g), (s17, 17.031)])
    # circulator and mix temperature
    R["T_k402"] = 30.0 + 303.15 * ((200.0 / (200.0 - DP_LOOP)) ** ((GAMMA - 1) / GAMMA) - 1) / ETA_C
    R["T_mix"] = (s27 * R["T_k402"] + s15 * 40.0) / (s27 + s15)
    Q = g.Q_NH3 * K                                   # MW, R-401 reaction heat (S Rev B: n(NH3) x 52.34 kJ/mol)
    mk = R["eff"] / 3.6
    mq = (Q * 1e3 - mk * CP_GAS * (T_OUT - T_PRE)) / (CP_GAS * (T_PRE - R["T_mix"]))
    assert 0 < mq < mk
    R.update(Q_rx=Q, mq=mq * 3.6, mh=(mk - mq) * 3.6)
    R["Q403"] = (mk - mq) * CP_GAS * (T_PRE - R["T_mix"]) / 1e3
    R["T_ex"] = T_WHB - R["Q403"] * 1e3 / (mk * CP_GAS)
    R["Q_whb"] = mk * CP_GAS * (T_OUT - T_WHB) / 1e3
    R["m_steam"] = R["Q_whb"] * 1e3 / (H_STEAM_50 - H_BFW) * 3.6
    R["m_bfw"] = R["m_steam"]
    # condensation sequence: E-405 (40 C water), E-406 (cold interchanger to 10 C), E-401 chiller (to T_SEP)
    n_gas = (R["eff"] - s17) / mw_g; n_nh3 = s17 / 17.031     # kmol/h
    PT = sorted((t, v[0]) for t, v in NH3.items() if t in (-10, 0, 5, 10, 25, 40))
    def psat(T):
        for (t0, p0), (t1, p1) in zip(PT, PT[1:]):
            if T <= t1: return math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * (T - t0) / (t1 - t0))
        return PT[-1][1]
    def hfg(T): return HFG[40] + (HFG[0] - HFG[40]) * (40 - T) / 40.0     # D: linear between 0 and 40 C (CP8 ends; 25 C check 1166 vs 1176)
    def frac(T):   # D: fraction of the NH3 condensed at T and 200 bar, ideal-gas Raoult
        ps = psat(T); nv = n_gas * (ps / 200.0) / (1 - ps / 200.0); return min(1.0, max(0.0, 1 - nv / n_nh3))
    mg = (R["eff"] - s17) / 3.6; mn = s17 / 3.6; mcold = R["gas401"] / 3.6
    f1 = frac(40)
    R["T_cx_out"] = 30.0                                    # A: 10 K approach at the warm end of E-406
    R["Q406"] = mcold * CP_GAS * (R["T_cx_out"] - T_SEP) / 1e3
    lo, hi_ = T_SEP, 40.0
    for _ in range(60):   # bisection: hot-side outlet T of E-406 from the duty
        mid = 0.5 * (lo + hi_); q = (mg * CP_GAS * (40 - mid) + (frac(mid) - f1) * mn * hfg((40 + mid) / 2)) / 1e3
        if q > R["Q406"]: lo = mid
        else: hi_ = mid
    R["T_e406"] = 0.5 * (lo + hi_); f2 = frac(R["T_e406"])
    R.update(f1=f1, f2=f2)
    R["Q405"] = (mk * CP_GAS * (R["T_ex"] - 40) + f1 * mn * HFG[40]) / 1e3
    R["Q401"] = (mg * CP_GAS * (R["T_e406"] - T_SEP) + (1.0 - f2) * mn * hfg((R["T_e406"] + T_SEP) / 2)) / 1e3
    # refrigeration circuit (kg/s)
    y = (NH3[40][1] - NH3[-10][1]) / HFG[-10]
    mev = R["Q401"] * 1e3 / HFG[-10]
    Mc = mev / (1 - y); vflash = y * Mc
    hl = {t: NH3[t][1] for t in NH3}
    # tank boil-off (D): ingress per area (A 8 W/m2, range 5-12), shell + 1.1 x roof area
    days = 10.0; rho_l = NH3[-33.3][3]
    vol = R["liq401"] * 1000 * 24 * days / rho_l * 1.1; Dt = math.sqrt(4 * vol / (math.pi * 20.0))
    area = math.pi * Dt * 20.0 + 1.1 * math.pi * Dt ** 2 / 4
    q_pump = 0.3 * (s17 / 3.6 / rho_l) * 25e5 / 0.7 / 1e3          # kW heat from P-501 (30 % of shaft, A)
    B = (area * 8.0 / 1e3 + q_pump) / HFG[-33.3]                    # kg/s
    L40 = None
    # V-403 balance: 91 (0 C) + L40 -> (91 + B) liquid + Rv vapour; L40 = Rv + B
    mn_ = s17 / 3.6
    Rv = (mn_ * (hl[0] - hl[-33.3]) + B * (hl[40] - hl[-33.3])) / (NH3[-33.3][2] - hl[40])
    L40 = Rv + B
    mA = Rv + B
    mB = mev + vflash + mA
    R.update(y_flash=y, mev=mev * 3.6, Mc=Mc * 3.6, vflash=vflash * 3.6, B=B * 3.6, Rv=Rv * 3.6, L40=L40 * 3.6, mA=mA * 3.6, mB=mB * 3.6,
             W_A=mA * DHS_AB / ETA_C / 1e3, W_B=mB * DHS_B / ETA_C / 1e3, tank_vol=vol, tank_D=Dt, tank_area=area, days=days)
    R["Q503"] = mB * (HFG[-10] + NH3[-10][1] + DHS_B / ETA_C - NH3[40][1]) / 1e3 if False else mB * (NH3[-10][2] + DHS_B / ETA_C - NH3[40][1]) / 1e3
    R["m_cw405"] = R["Q405"] * 1e3 / (CP_W * 12.0) * 3.6; R["m_cw503"] = R["Q503"] * 1e3 / (CP_W * 12.0) * 3.6
    n_in = (g.B.inlet * K)    # mol/s H2+N2 into the converter (Rev B 'inlet')
    R["cat_m3"] = n_in * 3600 * 0.022414 / GHSV      # D: Nm3/h / GHSV
    R["K401"] = g.K401_MW * K       # MW, Rev B power x K (gen_pid_urea.K401_MW is at the Rev B 1.10 Mt/a rate)
    return R


def build(pkg):
    R = balance()
    A = "A"
    # ================= streams =================
    mw_g = R["mw_g"]; S = stream
    # make-up train
    s15 = stream(15, "make-up gas to K-401A", "gas", rho=rho_gas(40, 40, mw_g))
    s611 = stream("611", "K-401A discharge, cooled", "gas", T=40.0, P=89.4, flow=R["s15"], base=15); s611.rho_in = rho_gas(40, 89.4, mw_g)
    s15h = stream("612", "make-up gas to loop (K-401B out)", "gas", T=40.0, P=200.0, flow=R["s15"], base=15); s15h.rho_in = rho_gas(40, 200, mw_g)
    # circulator
    k402_in = sg("613", "loop gas to K-402", 30.0, 200 - DP_LOOP, R["s27"], mw_g)
    s27 = stream(27, "recycle gas from K-402", "gas", T=round(R["T_k402"], 1), P=200.0); s27.rho_in = rho_gas(R["T_k402"], 200, mw_g)
    # converter
    mw_eff = R["mw_eff"]
    cfeed_all = sg("614", "converter feed (main), E-403 out", T_PRE, 200.0, R["mh"], mw_g)
    cquench = sg("615", "converter cold quench", R["T_mix"], 200.0, R["mq"], mw_g)
    cmain_in = sg("616", "main feed to E-403 cold side", R["T_mix"], 200.0, R["mh"], mw_g)
    eff = sg("617", "converter effluent", T_OUT, 200.0, R["eff"], mw_eff)
    assert abs(cfeed_all.flow + cquench.flow - eff.flow) < 1e-9 * eff.flow, "R-401 mass closure"
    e_whb = sg("618", "effluent after WHB", T_WHB, 200.0, R["eff"], mw_eff)
    e_403 = sg("619", "effluent after E-403", R["T_ex"], 200.0, R["eff"], mw_eff)
    def tp(i, name, T, f):
        nl = f * R["s17"]; ng = R["eff"] - nl
        return simple(i, name, "twophase", R["eff"], round(T, 1), 200.0, rho=two_rho(ng, rho_gas(T, 200, mixmw([(ng - (R["s17"] - nl), mw_g), (R["s17"] - nl, 17.031)])), nl, NH3[40][3] if T > 20 else NH3[5][3]))
    e_405 = tp("620", "effluent after E-405 (28 % NH3 condensed)", 40.0, R["f1"])
    e_406 = tp("621", "effluent after E-406", R["T_e406"], R["f2"])
    e_401 = tp("622", "chilled effluent to V-401", T_SEP, 1.0)
    # V-401 products
    gas401 = sg("623", "separator gas to E-406", T_SEP, 200.0 - 2, R["gas401"], mw_g)
    liq401 = simple("624", "liquid NH3 to V-402", "liq", R["liq401"], T_SEP, 200.0, rho=NH3[0][3])
    purge_loop = sg("625", "loop purge to PGR-401", T_SEP, 198.0, R["purge_loop"], mw_g)
    # letdown
    fg = sg("626", "letdown flash gas to PGR-401", T_SEP, 25.0, R["dg"], mw_g)
    nh3_25 = simple("627", "NH3 to V-403 (25 bar)", "liq", R["s17"], T_SEP, 25.0, rho=NH3[0][3])
    # V-403 / refrigeration level 1
    l40 = simple("628", "recondensed NH3 to V-403", "liq", R["L40"], 40.0, 15.5, rho=NH3[40][3])
    v403_in = simple("629", "V-403 feed (flashing)", "twophase", R["s17"] + R["L40"], -33.3, 1.1,
                     rho=two_rho(R["Rv"], 0.8906, R["s17"] + R["L40"] - R["Rv"], NH3[-33.3][3]))
    v403_vap = simple("630", "level-1 refrigerant vapour", "gas", R["Rv"], -33.3, 1.05, mw=17.031, rho=0.8906)
    s17 = stream(17, "liquid NH3 to T-501 (incl. boil-off return)", "liq", T=-33.3, P=1.1, rho=NH3[-33.3][3], flow=R["s17"] + R["B"])
    bog = simple("631", "boil-off gas from T-501", "gas", R["B"], -33.3, 1.05, mw=17.031, rho=0.8906)
    lvl1 = simple("632", "level-1 vapour to K-501", "gas", R["mA"], -33.3, 1.05, mw=17.031, rho=0.8906)
    lvl2 = simple("633", "level-2 vapour from E-401", "gas", R["mev"], -10.0, 2.9, mw=17.031, rho=2.39)
    ecoflash = simple("634", "flash vapour from V-404", "gas", R["vflash"], -10.0, 2.9, mw=17.031, rho=2.39)
    kdisch = simple("635", "K-501 discharge", "gas", R["mB"], 144.6, 15.5, mw=17.031)
    kdisch.rho_in = 15.5e5 * 0.017031 / (R_GAS * (144.6 + 273.15)) * 1.0
    cond = simple("636", "refrigerant condensate", "liq", R["mB"], 40.0, 15.5, rho=NH3[40][3])
    liq_ev = simple("637", "refrigerant liquid to E-401", "liq", R["mev"], -10.0, 2.9, rho=NH3[-10][3])
    liq_v403 = simple("638", "refrigerant liquid to V-404", "liq", R["Mc"], 40.0, 15.5, rho=NH3[40][3])
    flash404 = simple("639", "V-404 feed (flashing)", "twophase", R["Mc"], -10.0, 2.9, rho=two_rho(R["vflash"], 2.39, R["Mc"] - R["vflash"], NH3[-10][3]))
    assert abs(R["mB"] - (R["mev"] + R["vflash"] + R["mA"])) < 1e-9 and abs(R["Mc"] + R["L40"] - R["mB"]) < 1e-6, (R["Mc"], R["L40"], R["mB"])
    # utilities
    def cw(i, name, T, flow): return simple(i, name, "liq", flow, T, 4.5, rho=995.0 if T < 35 else 990.0)
    cw405 = (cw("640", "cooling water to E-405", 30.0, R["m_cw405"]), cw("641", "cooling water return E-405", 42.0, R["m_cw405"]))
    cw503 = (cw("642", "cooling water to E-503", 30.0, R["m_cw503"]), cw("643", "cooling water return E-503", 42.0, R["m_cw503"]))
    bfw = simple("644", "BFW to E-404", "liq", R["m_bfw"], 105.0, 55.0, rho=955.0)
    hps = simple("645", "HP steam from E-404 (sat.)", "steam", R["m_steam"], 263.9, 50.0, mw=18.015)
    # ================= 601 K-401A =================
    t_hot = 313.15 * (1 + ((89.4 / 40.0) ** ((GAMMA - 1) / GAMMA) - 1) / ETA_C) - 273.15       # D hot discharge T, one stage
    w1 = R["K401"] / 2
    sheet_compressor(pkg, AREA, 601, "Area 60  Ammonia loop  -  K-401A make-up gas compressor, LP stage group (40 to 89 bar)",
        dict(tag="K-401A", name="Make-up gas compressor, LP casing", suction=s15, discharge=s611, power_MW=w1, driver="steam turbine", spec="A1",
             hazard="H2/N2 synthesis gas at 40-90 bar",
             notes=[f"K-401 is a two-casing train (A, B) at equal pressure ratio {math.sqrt(5):.3f}; interstage pressure 89.4 bar = sqrt(40 x 200) (D). Total shaft power {R['K401']:.1f} MW is the Rev B S value (CoolProp, eta 0.75); each casing carries half (D, equal ratio and flow).",
                    f"Hot discharge about {t_hot:.0f} C before the cooler (D, gamma 1.4 A, eta 0.75); the cooler 'K-401A-AC' on the sheet is the interstage cooler E-402 (template label 'aftercooler').",
                    "Stream 15 is the Rev B make-up (14 N2 + H2 + 30 recovered purge) at 40 bar; drier/CO2 guard bed (molecular sieve) is not drawn (gap: no CO2/H2O spec for the loop)."]))
    add_note_eq(pkg, "K-401A", f"{design_conditions(89.4, t_hot)[0]:g} bar g / {round_up(t_hot + 25, 5):g} C (D, hot discharge)")
    detectors(pkg.sheets[-1], pkg, "601", what="H2/NH3")
    # ================= 602 K-401B =================
    sheet_compressor(pkg, AREA, 602, "Area 60  Ammonia loop  -  K-401B make-up gas compressor, HP stage group (89 to 200 bar)",
        dict(tag="K-401B", name="Make-up gas compressor, HP casing", suction=s611, discharge=s15h, power_MW=w1, driver="steam turbine", spec="A1",
             hazard="H2/N2 at 200 bar",
             notes=["Discharge goes to the loop at the circulator K-402 outlet (200 bar, S Rev B stream 16/27 pressure); the make-up is mixed with the recycle before the feed/effluent exchanger E-403.",
                    "Both casings share one driver in this concept (A); a steam turbine is an assumption, a motor is equally possible (not in Rev B).",
                    "Oil-free / dry gas seal selection and the surge map are vendor items (gap)."]))
    add_note_eq(pkg, "K-401B", f"{design_conditions(200, t_hot)[0]:g} bar g / {round_up(t_hot + 25, 5):g} C (D, hot discharge)")
    detectors(pkg.sheets[-1], pkg, "602", what="H2/NH3")
    # ================= 603 K-402 =================
    p_circ = (R["s27"] / 3.6 / k402_in.rho) * DP_LOOP * 1e5 / ETA_C / 1e6     # MW, D: Q dP / eta
    sheet_package(pkg, AREA, 603, "Area 60  Ammonia loop  -  K-402 loop circulator",
        dict(tag="K-402", name="Loop circulator (single casing, motor)", inlets=[(k402_in, "loop gas", "PG")], outlets=[(s27, "recycle gas", "PG")],
             utilities=[("power", p_circ, "MW", "D"), ("seal gas", 0.0, "gap", "A"), ("lube oil", 0.0, "gap", "A")], esd=True, spec="A1",
             desc=["centrifugal, in-line with the loop", "dry gas seals (A)", f"dP {DP_LOOP:g} bar over the loop (A 5-15)"],
             interlocks=[("PDAL", "loop dP low", "0-20 bar", "L 4 bar (A)"), ("VAHH", "vibration HH trip", "per vendor", "gap"), ("TAH", "bearing temperature", "0-150 C", "H 90 C (A)"), ("FAL", "circulating flow low", "per vendor", "gap")],
             type="centrifugal circulator", op=f"{R['s27']:.0f} t/h, {200-DP_LOOP:g}->200 bar", design=f"{design_conditions(200, 60)[0]:g} bar g / {design_conditions(200, 60)[1]:g} C (D)", size=f"{p_circ:.2f} MW (D)",
             basis="D", relief="blocked discharge",
             rows=[("Flow", f"{R['s27']:.0f} t/h", "Rev B 27"), ("dP", f"{DP_LOOP:g} bar", "A"), ("Power", f"{p_circ:.2f} MW", "D Q dP/eta"), ("Rise", f"{R['T_k402']-30:.1f} K", "D")],
             hazard="H2/N2/NH3 at 200 bar",
             notes=[f"Power = volumetric flow x dP / eta (0.75 A) = {p_circ:.2f} MW. Gas is ideal-gas corrected by Z (D, fit to CoolProp).",
                    f"Suction {k402_in.T:g} C is the E-406 cold-side outlet; discharge rise {R['T_k402']-30:.1f} K (D) is the cooling load that E-403 carries.",
                    "Stream 27 is Rev B 'loop recycle gas' (40 C, 200 bar S); here T is the circulator discharge (A override), a Rev C change because Rev B has no refrigerated separator.",
                    "Template note: this unit has no aftercooler; the package sheet is used instead of sheet_compressor (whose block diagram includes one)."]))
    detectors(pkg.sheets[-1], pkg, "603", what="H2/NH3")
    # ================= 604 E-403 =================
    sheet_hx(pkg, AREA, 604, "Area 60  Ammonia loop  -  E-403 converter feed / effluent exchanger",
        dict(tag="E-403", name="Feed / effluent exchanger", hot_in=e_whb, hot_out=e_403, cold_in=cmain_in, cold_out=cfeed_all, duty_MW=R["Q403"], kind="gas_gas_hp", spec="A1", spec_c="A1",
             svc_c="PG", esd_hot=True, mat="A: Cr-Mo steel, nitriding/H2 service (to be set by licensor)", hazard="200 bar H2/N2/NH3 at up to 330 C",
             notes=[f"Duty = main feed mass x cp ({CP_GAS} kJ/kg/K, CP8) x ({T_PRE:g} - {R['T_mix']:.1f}) C = {R['Q403']:.0f} MW (D). T_ex is then set by the effluent heat balance: {R['T_ex']:.0f} C (D).",
                    f"U = {U_HP_GAS:g} W/m2/K is an assumption for 200 bar gas (A 200-500): the pid_unit2 gas_gas value (60) is a low-pressure number, so the area printed is not a vendor area.",
                    "Hot-end approach 30 K and converter inlet 300 C at the nozzle are assumptions (A). The extra heating to the bed-1 inlet is done inside R-401 (internal exchanger, not drawn).",
                    "Only the effluent side has an ESD valve on this sheet; the cold-side valves are the loop isolation of 614/616."]))
    detectors(pkg.sheets[-1], pkg, "604", what="H2/NH3")
    # ================= 605 R-401 =================
    sheet_reactor(pkg, AREA, 605, "Area 60  Ammonia loop  -  R-401 ammonia converter (3 beds)",
        dict(tag="R-401", name="Ammonia converter", feed=cfeed_all, eff=eff, vol_m3=R["cat_m3"], beds=3, spec="A1", quench=cquench,
             mat="A: Cr-Mo shell with internal liner / cartridge (to be set by licensor)", hazard="200 bar, up to 450 C",
             notes=[f"Effluent 450 C is the Rev B value (S repo ammonia_synthesis.py). Reaction heat {R['Q_rx']:.1f} MW = Rev B n(NH3) x 52.34 kJ/mol x K (S/D).",
                    f"Cold quench {R['mq']:.1f} t/h closes the boundary heat balance: m_q cp (450-{R['T_mix']:.0f}) + m_h cp (450-{T_PRE:g}) = Q (D, cp 3.55 CP8). Mass closure asserted.",
                    f"Catalyst volume {R['cat_m3']:.0f} m3 = inlet Nm3/h / GHSV {GHSV:g} 1/h (A 10,000-25,000); Nm3 from 22.414 L/mol (CODATA ideal).",
                    "Bed split (3), interbed quench-only layout and the 450 C bed outlet limit are assumptions (A); licensor mechanical design is a gap. TAHH/PAHH trips from the template."]))
    detectors(pkg.sheets[-1], pkg, "605", what="NH3/H2")
    # ================= 606 E-404 WHB =================
    sheet_hx(pkg, AREA, 606, "Area 60  Ammonia loop  -  E-404 waste-heat boiler (HP steam raising)",
        dict(tag="E-404", name="Converter waste-heat boiler", hot_in=eff, hot_out=e_whb, cold_in=bfw, cold_out=hps, duty_MW=R["Q_whb"], kind="steam_gen", spec="A1", spec_c="A1", svc_c="BFW",
             esd_hot=True, mat="A: Cr-Mo tube side, CS shell", hazard="200 bar tube side vs 50 bar steam",
             notes=[f"Duty {R['Q_whb']:.1f} MW = effluent mass x cp x (450 - {T_WHB:g}) C (D); steam {R['m_steam']:.0f} t/h = duty / (hv 50 bar - h BFW 105 C) = {H_STEAM_50-H_BFW:.0f} kJ/kg (CP8). Roughly {R['m_steam']/R['s17']:.2f} t steam per t NH3.",
                    "Steam at 50 bar is the Rev B HP header pressure (A, stream 3 conditions); the steam drum, blowdown and BFW control are not drawn (sheet shows the exchanger only).",
                    "Tube-rupture relief (200 bar to 50 bar side) needs the rupture case: relief sizing is a gap; PSV destination is the template default.",
                    "Gas outlet 330 C is an assumption (A 300-360): it fixes how much heat reaches E-403."]))
    detectors(pkg.sheets[-1], pkg, "606", what="NH3/H2")
    # ================= 607 E-405 =================
    sheet_hx(pkg, AREA, 607, "Area 60  Ammonia loop  -  E-405 loop water cooler (partial NH3 condensation)",
        dict(tag="E-405", name="Loop water cooler", hot_in=e_403, hot_out=e_405, cold_in=cw405[0], cold_out=cw405[1], duty_MW=R["Q405"], kind="gas_liq_hp", spec="A1", spec_c="A1", svc_c="CW", esd_hot=True,
             mat="A: CS (tube side NH3 gas); cooling-water side per site", hazard="NH3 leak into cooling water (tube rupture)",
             notes=[f"{R['f1']*100:.0f} % of the NH3 condenses at 40 C and 200 bar: ideal-gas Raoult, Psat(40 C) = 15.5 bar (CP8) (D, real-gas fugacity would condense more). Duty = sensible {CP_GAS} kJ/kg/K + latent {HFG[40]:.0f} kJ/kg (D).",
                    f"CW 30 -> 42 C (A), flow {R['m_cw405']:.0f} t/h = duty / (cp {CP_W} x 12 K) (D). Tube rupture: NH3 enters the CW return: add NH3 / conductivity analyser (gap, only noted).",
                    "Outlet 40 C is the water-cooled limit (A, 30 C CW + 10 K approach)."]))
    detectors(pkg.sheets[-1], pkg, "607", what="NH3")
    # ================= 608 E-406 =================
    sheet_hx(pkg, AREA, 608, "Area 60  Ammonia loop  -  E-406 cold interchanger (separator gas vs effluent)",
        dict(tag="E-406", name="Cold interchanger", hot_in=e_405, hot_out=e_406, cold_in=gas401, cold_out=k402_in, duty_MW=R["Q406"], kind="gas_gas_hp", spec="A1", spec_c="A1", svc_c="PG", esd_hot=True,
             mat="A: LT carbon steel (cold end below 0 C)", hazard="cold NH3 liquid-gas at 200 bar",
             notes=[f"Duty {R['Q406']:.1f} MW (D) cools the effluent 40 -> {R['T_e406']:.0f} C (D, hot outlet from the duty) and heats the {R['gas401']:.0f} t/h separator gas to {R['T_cx_out']:.0f} C (D); that is the K-402 suction temperature.",
                    f"NH3 condensed in this exchanger: {(R['f2']-R['f1'])*100:.0f} % of the loop NH3 (D, ideal Raoult at the outlet T, Psat from CP8 table). Two-phase tube-side flow; mixed-phase distribution is a gap.",
                    "Cold-side limited (A: 10 K warm-end approach, gas out 30 C): it recovers {R['Q406']:.1f} MW of cold that would otherwise load E-401 (D)."]))
    detectors(pkg.sheets[-1], pkg, "608", what="NH3")
    # ================= 609 E-401 =================
    sheet_hx(pkg, AREA, 609, "Area 60  Ammonia loop  -  E-401 loop chiller (refrigerant evaporating at -10 C)",
        dict(tag="E-401", name="Loop chiller (NH3 refrigerant)", hot_in=e_406, hot_out=e_401, cold_in=liq_ev, cold_out=lvl2, duty_MW=R["Q401"], kind="boil", spec="A1", spec_c="LT", svc_c="NH3", esd_hot=True,
             mat="A: LT carbon steel / killed steel (to -30 C or lower)", hazard="two ammonia inventories",
             notes=[f"Chiller duty {R['Q401']:.1f} MW = sensible gas cooling 10 -> 0 C + remaining NH3 latent at 5 C ({HFG[5]:.0f} kJ/kg CP8) (D). This is the refrigeration load that K-501B must serve.",
                    f"Refrigerant {R['mev']:.0f} t/h = duty / hfg(-10 C) {HFG[-10]:.0f} kJ/kg (CP8). Refrigerant evaporates at -10 C / 2.91 bar (A: 10 K approach to the 0 C separator).",
                    "Shell-side vapour leaves to V-404 (sheet 617); the chiller is a flooded kettle in reality; level control belongs to V-404 (not drawn here).",
                    "Residual NH3 in the separator gas (about 2 mol % at 0 C ideal) is not in Rev B stream 27 (pure H2:N2): gap carried to the notes file."]))
    detectors(pkg.sheets[-1], pkg, "609", what="NH3")
    # ================= 610 V-401 =================
    sh = sheet_vessel(pkg, AREA, 610, "Area 60  Ammonia loop  -  V-401 ammonia separator",
        dict(tag="V-401", name="Ammonia separator", inlet=e_401, gas=gas401, liq=liq401, res_min=3.0, spec="A1", svc_in="PG", svc_gas="PG", svc_liq="NH3", internals="demister",
             mat="A: LT carbon steel / low-alloy, 200 bar", hazard="200 bar NH3 liquid and H2/N2 gas",
             relief_case="blocked gas outlet; fire; LV stuck open", relief_dest="flare header",
             notes=[f"Liquid {R['liq401']:.1f} t/h = Rev B stream 17 ({R['s17']:.1f}) + dissolved gas {R['dg']:.2f} t/h (A {DG_FRAC*100:g} % mass; letdown flash gas, range 0.1-1 %). Gas {R['gas401']:.1f} t/h = recycle 27 + loop purge (D, mass closure asserted).",
                    "Template draws a level indicator and trips but no level control valve; a local LV-61021 is drawn below the vessel (template defect).",
                    "Separator at 0 C and 198 bar: liquid NH3 inventory behind the LV is the largest toxic release path; double LALL / LV fail-closed + HV/XV on the line are the ESD concept."]))
    lvalve(sh, pkg, 470, 503, "LV-61021", "624", 6, "level control", "FC")
    detectors(sh, pkg, "610", what="NH3")
    # ================= 611 V-402 =================
    sh = sheet_vessel(pkg, AREA, 611, "Area 60  Ammonia loop  -  V-402 letdown drum (200 to 25 bar)",
        dict(tag="V-402", name="Letdown drum", inlet=simple("646", "V-401 liquid after LV (flashing)", "twophase", R["liq401"], T_SEP, 25.0, rho=two_rho(R["dg"], rho_gas(T_SEP, 25, mw_g), R["s17"], NH3[0][3])),
             gas=fg, liq=nh3_25, res_min=3.0, spec="LT", svc_in="NH3", svc_gas="PG", svc_liq="NH3", internals="demister",
             mat="A: LT carbon steel", hazard="NH3 liquid at 25 bar",
             relief_case="blocked gas outlet; fire", relief_dest="flare header",
             notes=[f"Flash gas {R['dg']:.2f} t/h is only the dissolved H2/N2 (A). Real flash gas also carries NH3 vapour (Psat(0 C) 4.3 bar = 17 mol % at 25 bar, CP8); not in Rev B, goes with the purge to PGR-401 NH3 water wash (gap).",
                    "25 bar letdown level is an assumption (A 15-30 bar): no sourced value. Pure NH3 does not flash between 200 and 25 bar at 0 C (subcooled), only dissolved gas does.",
                    "LV between V-401 and this drum: erosion/flashing service; trim and fail-closed action are valve-vendor items (gap).",
                    "Liquid goes on to V-403 where the auto-refrigeration flash cools it to -33 C."]))
    lvalve(sh, pkg, 470, 503, "LV-61121", "627", 6, "level control", "FC")
    detectors(sh, pkg, "611", what="NH3")
    # ================= 612 PGR-401 =================
    pg_in = purge_loop
    pgr_rec = stream(30, "recovered H2/N2 to K-401A", "gas", rho=rho_gas(40, 40, mw_g))
    pgr_fuel = stream(16, "net purge / tail gas to fuel", "gas", P=5.0, rho=rho_gas(40, 5, mw_g))
    tot_in = pg_in.flow + fg.flow
    assert abs(tot_in - (pgr_rec.flow + pgr_fuel.flow)) < 1e-6 * tot_in, "PGR-401 mass closure (Rev B purge 16 + 30)"
    sheet_package(pkg, AREA, 612, "Area 60  Ammonia loop  -  PGR-401 purge-gas recovery",
        dict(tag="PGR-401", name="Purge-gas recovery unit (technology open)", inlets=[(pg_in, "loop purge (198 bar)", "PG"), (fg, "letdown flash gas (25 bar)", "PG")],
             outlets=[(pgr_rec, "recovered H2/N2 to K-401A", "PG"), (pgr_fuel, "tail gas to fuel header", "PG")], esd=True, spec="A1",
             utilities=[("water wash", 0.0, "gap", "A"), ("power", 0.0, "gap", "A")],
             desc=["NH3 water wash + membrane or cryogenic recovery", "technology not selected (A)", f"recovery {g.PURGE_RECOVERY*100:.0f} % of H2+N2 (A, Rev B)"],
             interlocks=[("PAHH", "inlet pressure HH", "0-250 bar", "HH 215 bar (A)"), ("AAH", "NH3 in recovered gas", "0-200 ppm", "H 20 ppm (A)"), ("TAL", "feed temperature low", "-20 to 60 C", "L -10 C (A)")],
             type="purge-gas recovery package", op="198 / 25 bar in, 40 bar recovered gas out", design=f"{design_conditions(198, 40)[0]:g} bar g (D)", size="gap (vendor)", basis="A", relief="blocked outlet",
             rows=[("Feed", f"{tot_in:.1f} t/h", "D 16+30"), ("Recovered", f"{pgr_rec.flow:.1f} t/h", "Rev B 30"), ("Tail gas", f"{pgr_fuel.flow:.1f} t/h", "Rev B 16"), ("Recovery", f"{g.PURGE_RECOVERY*100:.0f} %", "A (Rev B)")],
             hazard="H2-rich gas at 198 bar, NH3 in feed",
             notes=["Mass closure: feed (loop purge + letdown flash gas) = Rev B streams 30 + 16, asserted; split 90 % to 30 is the Rev B assumption (A 85-95 %), not a vendor figure.",
                    "Stream 16 pressure is overridden to 5 bar (A): Rev B lists 200 bar, which is the pressure at the purge take-off, not at the tail-gas outlet.",
                    "Power, wash-water rate and the technology choice (membrane vs cryogenic) are gaps; no vendor data used."]))
    detectors(pkg.sheets[-1], pkg, "612", what="H2/NH3")
    # ================= 613 V-403 =================
    sh = sheet_vessel(pkg, AREA, 613, "Area 60  Ammonia refrigeration  -  V-403 auto-refrigeration flash drum (to -33 C)",
        dict(tag="V-403", name="Auto-refrigeration flash drum", inlet=v403_in, gas=v403_vap, liq=s17, res_min=5.0, spec="LT", svc_in="NH3", svc_gas="NH3", svc_liq="NH3", internals="demister",
             mat="A: LT carbon steel (impact-tested), -40 C minimum design (A)", hazard="NH3 at -33 C",
             relief_case="blocked vapour outlet; fire", relief_dest="NH3 vent absorber C-501 / flare",
             notes=[f"Balance: 0 C liquid {R['s17']:.1f} t/h + recondensed liquid {R['L40']:.1f} t/h (40 C) -> liquid {R['s17']+R['B']:.1f} t/h at -33.3 C + vapour {R['Rv']:.1f} t/h. Energy closed on enthalpies from CoolProp (D, CP8).",
                    f"Vapour {R['Rv']:.1f} t/h = [m(hL0 - hL-33) + B(hL40 - hL-33)] / (hV-33 - hL40); B = boil-off {R['B']:.2f} t/h from T-501.",
                    "Liquid out is Rev B stream 17 plus the boil-off return B (+0.3 %): net product to urea stays Rev B (stream 18).",
                    "Template draws the LV on a pump line only; here the liquid flows to T-501 by pressure, LV shown local."]))
    lvalve(sh, pkg, 470, 503, "LV-61321", "17", 6, "level control", "FC")
    detectors(sh, pkg, "613", what="NH3")
    # ================= 614 K-501 =================
    sheet_package(pkg, AREA, 614, "Area 60  Ammonia refrigeration  -  K-501 refrigeration compressor (two-stage, BOG duty)",
        dict(tag="K-501", name="NH3 refrigeration compressor (LP + HP stage)", inlets=[(lvl1, "level 1 (-33 C): V-403 + BOG", "NH3"), (lvl2, "level 2 (-10 C): E-401", "NH3"), (ecoflash, "level 2: V-404 flash", "NH3")],
             outlets=[(kdisch, "discharge to E-503", "NH3")], esd=True, spec="LT",
             utilities=[("LP stage", R["W_A"], "MW", "D"), ("HP stage", R["W_B"], "MW", "D"), ("oil cooler", 0.0, "gap", "A")],
             desc=["LP stage 1.01 -> 2.91 bar", "HP stage 2.91 -> 15.5 bar", "also serves as BOG compressor", "standby BOG compressor K-502"],
             interlocks=[("LAHH", "suction KO level HH", "0-100 %", "HH 90 % (A)"), ("PAL", "suction pressure low", "0-5 bar", "L 0.7 bar (A)"), ("PAHH", "discharge pressure HH", "0-25 bar", "HH 19 bar (A)"), ("VAHH", "vibration HH", "per vendor", "gap"), ("TAH", "discharge T high", "0-200 C", "H 160 C (A)")],
             type="NH3 refrigeration compressor", op=f"1.0 -> 15.5 bar, {R['mB']:.0f} t/h", design="23 bar g / 175 C (A)", size=f"{R['W_A']+R['W_B']:.1f} MW (D)", basis="D", relief="blocked discharge",
             rows=[("LP stage", f"{R['mA']:.1f} t/h, {R['W_A']:.2f} MW", "D"), ("HP stage", f"{R['mB']:.1f} t/h, {R['W_B']:.2f} MW", "D"), ("Total shaft", f"{R['W_A']+R['W_B']:.1f} MW", "D"), ("eta", "0.75", "A")],
             hazard="NH3 vapour, toxic and corrosive to Cu alloys",
             notes=[f"Power = mass x isentropic dh / eta: LP {DHS_AB} kJ/kg (-33.3 to -10 C sat. vapour), HP {DHS_B} kJ/kg (-10 to 40 C), both CP8; eta 0.75 A. HP stage mass {R['mB']:.0f} t/h = chiller {R['mev']:.0f} + V-404 flash {R['vflash']:.0f} + LP {R['mA']:.0f} (asserted).",
                    f"Discharge 144.6 C is T(15.5 bar, h = hV(-10 C) + dh/eta) from CoolProp (D). HP-stage inlet superheat from the LP stage discharge is ignored (A, a few % low in power).",
                    "Compressor type (screw vs centrifugal), oil system and capacity control are open; a template compressor sheet is not used because it implies an aftercooler that this duty does not have."]))
    detectors(pkg.sheets[-1], pkg, "614", what="NH3")
    # ================= 615 E-503 =================
    cond_hot = simple("647", "K-501 discharge vapour", "gas", R["mB"], 144.6, 15.5, mw=17.031)
    cond_hot.rho_in = 15.5e5 * 0.017031 / (R_GAS * (144.6 + 273.15))
    sheet_hx(pkg, AREA, 615, "Area 60  Ammonia refrigeration  -  E-503 refrigerant condenser",
        dict(tag="E-503", name="Refrigerant condenser (CW)", hot_in=cond_hot, hot_out=cond, cold_in=cw503[0], cold_out=cw503[1], duty_MW=R["Q503"], kind="cond", spec="LT", spec_c="A1", svc_c="CW", esd_hot=True,
             mat="A: carbon steel (no copper alloys in NH3 service)", hazard="NH3 vapour 15 bar, tube leak to CW",
             notes=[f"Duty {R['Q503']:.1f} MW = mass x [hV(-10 C) + dh/eta - hL(40 C)] (D, CP8). Condensing at 40 C = 15.5 bar (CP8) assumes 30 C CW and 10 K approach (A).",
                    f"CW flow {R['m_cw503']:.0f} t/h = duty / (cp {CP_W} x 12 K) (D). Receiver and economiser flash are on sheet 617 (V-404).",
                    "Non-condensable purge (air ingress) from the condenser is not drawn: a purger is a standard item (gap)."]))
    detectors(pkg.sheets[-1], pkg, "615", what="NH3")
    # ================= 616 V-404 =================
    sh = sheet_vessel(pkg, AREA, 616, "Area 60  Ammonia refrigeration  -  V-404 refrigerant receiver / chiller flash drum",
        dict(tag="V-404", name="Refrigerant flash drum (-10 C)", inlet=flash404, gas=ecoflash, liq=liq_ev, res_min=5.0, spec="LT", svc_in="NH3", svc_gas="NH3", svc_liq="NH3", internals="demister",
             mat="A: LT carbon steel", hazard="NH3 at -10 C, 2.9 bar",
             relief_case="blocked vapour outlet; fire; chiller tube rupture", relief_dest="NH3 vent absorber C-501 / flare",
             notes=[f"Liquid from E-503 ({R['Mc']:.0f} t/h, 40 C) flashes 15.5 -> 2.91 bar: flash fraction {R['y_flash']*100:.1f} % = (hL40 - hL-10)/hfg(-10) (D, CP8) -> {R['vflash']:.1f} t/h to the HP stage.",
                    f"Remaining liquid {R['mev']:.0f} t/h feeds E-401 (stream 637). Receiver inventory sizing for pump-down is a gap.",
                    "Condenser receiver (40 C, 15.5 bar) is not drawn as a separate vessel (A, merged into E-503 hotwell).",
                    "The template shows a level control valve on pump lines only; local LV drawn."]))
    lvalve(sh, pkg, 470, 503, "LV-61621", "637", 6, "level control", "FC")
    detectors(sh, pkg, "616", what="NH3")
    # ================= 617 T-501 =================
    p501 = 25.0
    sheet_tank(pkg, AREA, 617, "Area 60  Ammonia storage  -  T-501 refrigerated NH3 tank (single containment, concept) with P-501 pumps",
        dict(tag="T-501", name="Refrigerated NH3 tank (-33 C)", inflow=s17, outflow=simple("648", "NH3 to P-501 (to urea)", "liq", R["s17"], -33.3, 1.1, rho=NH3[-33.3][3]), days=R["days"], roof="dome",
             spec="LT", svc="NH3", refrigerated=True, pumps="P-501", pump_dp=p501, vent_dest="BOG header to K-501 / K-502; relief to C-501 (A)",
             mat="A: 9 % Ni or killed LT carbon steel, double-wall concept (to be set by designer)", hazard="refrigerated liquid NH3",
             notes=[f"Capacity {R['days']:g} days (A 5-15) of Rev B NH3: {R['tank_vol']:,.0f} m3 gross, {R['tank_D']:.0f} m diameter x 20 m (D,A). Talcher storage volume not found: gap.",
                    f"Boil-off {R['B']:.2f} t/h = (heat ingress 8 W/m2 A x {R['tank_area']:,.0f} m2 + pump heat) / hfg(-33 C) {HFG[-33.3]:.0f} kJ/kg (D); returns via K-501 / V-403.",
                    f"P-501A/B lift NH3 {p501:g} bar to the urea battery limit (A 20-30), then the NH3 preheater (not drawn) and the HP NH3 pump P-601 (area 70). Stream 18 is the HP-pump outlet.",
                    "Water-spray / deluge protection and dyke volume rule: no fetched document, gap. Type-A is the user's concept name; classification and containment class not verified."]))
    sh = pkg.sheets[-1]
    vt = R["s17"] * 24 * R["days"] / NH3[-33.3][3] * 1.1; Dtw = math.sqrt(4 * vt / (math.pi * 20.0))   # what sheet_tank computed (t/h used as kg/h: template units defect)
    fix_text(sh, f"{vt:,.0f} m3 gross", f"{R['tank_vol']:,.0f} m3 gross"); fix_text(sh, f"{Dtw:.0f} m dia", f"{R['tank_D']:.0f} m dia")
    fix_text(sh, f">{vt:,.0f} m3<", f">{R['tank_vol']:,.0f} m3<"); fix_text(sh, f">{Dtw:.0f} m x 20 m<", f">{R['tank_D']:.0f} m x 20 m<")
    for r in pkg.equip:
        if r[0] == "T-501": r[5] = f"{R['tank_vol']:,.0f} m3 (D)"
    detectors(sh, pkg, "617", what="NH3")
    # ================= 618 K-502 =================
    bog_flow = R["B"] + R["Rv"]
    k502_in = simple("649", "BOG / flash vapour to K-502", "gas", bog_flow, -33.3, 1.05, mw=17.031, rho=0.8906)
    k502_out = simple("650", "K-502 discharge to E-503 / flare", "gas", bog_flow, 53.4, 2.9, mw=17.031, rho=2.9 * 1e5 * 0.017031 / (R_GAS * 326.6))
    sheet_package(pkg, AREA, 618, "Area 60  Ammonia storage  -  K-502 standby BOG compressor and flare route",
        dict(tag="K-502", name="Standby BOG compressor (screw, motor)", inlets=[(k502_in, "BOG + flash vapour", "NH3")], outlets=[(k502_out, "to E-503 inlet", "NH3")], esd=True, spec="LT",
             utilities=[("power", bog_flow / 3.6 * DHS_AB / ETA_C / 1e3, "MW", "D"), ("cooling", 0.0, "gap", "A")],
             desc=["covers K-501 outage", "100 % of BOG + V-403 flash", "alternative route: recondenser / C-501 / flare"],
             interlocks=[("PAL", "suction pressure low", "0-3 bar", "L 0.7 bar (A)"), ("PAHH", "discharge pressure HH", "0-8 bar", "HH 5 bar (A)"), ("LAHH", "KO level HH", "0-100 %", "HH 90 % (A)"), ("AAH", "NH3 in compressor house", "0-300 ppm", "H 25 ppm (A)")],
             type="screw compressor package", op=f"{bog_flow:.1f} t/h, 1.0 -> 2.9 bar", design="8 bar g / 100 C (A)", size=f"{bog_flow/3.6*DHS_AB/ETA_C/1e3:.2f} MW (D)", basis="D", relief="blocked discharge",
             rows=[("Flow", f"{bog_flow:.1f} t/h", "D B + V-403 vapour"), ("dh", f"{DHS_AB} kJ/kg", "CP8"), ("eta", "0.75", "A")],
             hazard="NH3 vapour, cold suction",
             notes=["Sized for the whole level-1 vapour (BOG + V-403 flash) so that one compressor can be out of service; the discharge joins K-501 HP-stage suction route to E-503 (A).",
                    "Last resort: tank vapour to the vent absorber C-501 (sheet 619) and then the flare KO-101 / FL-101 (Rev B EQUIP). An NH3 flare is not common practice; the destination is a licensor / HSE decision (gap).",
                    "Discharge T 53 C is the isentropic estimate at eta 0.75 (CP8 for 2.9 bar and h); no discharge cooler drawn."]))
    detectors(pkg.sheets[-1], pkg, "618", what="NH3")
    # ================= 619 C-501 =================
    vent_nh3 = R["Rv"] + R["B"]
    slip = 0.005
    c_in = simple("651", "NH3 vent / relief vapour", "gas", vent_nh3, -33.3, 1.1, mw=17.031, rho=0.8906)
    c_wat = simple("652", "wash water to C-501", "liq", 20.0 * vent_nh3, 25.0, 3.0, rho=997.0)
    c_top = simple("653", "scrubbed vent to flare / stack", "gas", slip * vent_nh3, 20.0, 1.05, mw=17.031, rho=0.7)
    c_bot = simple("654", "aqueous NH3 to treatment", "liq", vent_nh3 * (1 - slip) + c_wat.flow, 40.0, 2.0, rho=950.0)
    assert abs(c_in.flow + c_wat.flow - c_top.flow - c_bot.flow) < 1e-9 * c_wat.flow
    sheet_column(pkg, AREA, 619, "Area 60  Ammonia storage  -  C-501 NH3 vent absorber (water wash)",
        dict(tag="C-501", name="NH3 vent absorber", feed=c_in, top=c_top, bottom=c_bot, feed2=c_wat, packing=True, stages=8, spec="A1", esd=True,
             mat="A: carbon steel / FRP packing support", hazard="NH3 vapour release to atmosphere; absorption",
             notes=[f"Design vent {vent_nh3:.1f} t/h NH3 = the level-1 vapour (V-403 flash + BOG) that K-501 and K-502 would normally take (D); wash water 20 t/t NH3 (A 10-30) gives about 5 wt % NH3 in the bottoms.",
                    "Scrubbed-gas slip 0.5 % of the NH3 (A) is a placeholder; absorber efficiency needs NH3-water equilibrium data (gap). Bottoms go to the process-condensate desorber C-606 (area 70) or the effluent system.",
                    "Cited relief / vent-scrubbing guidance: none fetched (no document read); water-spray and deluge design are gaps.",
                    "Template reboiler/steam is not used (absorber only); the column PSV discharge goes to the flare header (A)."]))
    detectors(pkg.sheets[-1], pkg, "619", what="NH3")
    return pkg


def lint(pkg):
    tags = [r[0] for r in pkg.equip]; dup = {t for t in tags if tags.count(t) > 1}
    # K-401A-KO and similar are per-sheet unique by construction; report duplicates
    assert not dup, f"duplicate equipment tags: {sorted(dup)}"
    bad = [r[0] for r in pkg.relief if not r[5]]; assert not bad, bad
    ids = {k[0] for k in STREAMS}; used = {str(r[4]) for r in pkg.lines}
    assert used <= ids, used - ids
    for sh in pkg.sheets:
        assert any(v[6] == sh.no and v[0].startswith("XV") for v in pkg.valves), f"sheet {sh.no} has no ESD valve"
    return True


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), Area 60 ammonia loop, refrigeration, storage",
              "Rev B balance scaled K=%.4f; capacity per ICRA/PIB (see docs/pid/analogues)" % K)
    build(pkg); pkg.total = len(pkg.sheets); lint(pkg)
    write_html(pkg.sheets, "/tmp/area60.html", "Area 60", previews=True)
    if "--registers" in sys.argv: pkg.write_registers(sys.argv[sys.argv.index("--registers") + 1])
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices, lint OK")


if __name__ == "__main__":
    main()

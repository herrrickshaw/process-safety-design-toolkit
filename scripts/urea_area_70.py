#!/usr/bin/env python3
"""Area 70: urea synthesis, recovery, concentration, granulation (unit-by-unit P&ID sheets 701-722).

Usage: python3 scripts/urea_area_70.py   (builds /tmp/area70.html with previews and runs the lint)

Basis: Rev B balance (gen_pid_urea.py) scaled by K to 3,850 t/d urea (urea_basis.py). Rev B streams used: 18, 19, 21, 22, 23, 24 (area 70);
stream 20 (surplus CO2) and stream 28 (V-203 condensate, area 40) are not drawn here. Layout = CO2-stripping family (public licensor reference
is Stamicarbon; licensor NAMES only, no licensor data): R-601 -> C-601 CO2 stripper -> E-601 HP carbamate condenser -> R-601, with MP and LP
decomposers and carbamate recycle. Rev B lumps all unconverted NH3 + CO2 into stream 24; this file splits it (A: HP / MP / LP fractions) and
asserts closure at every node. Tags S sourced / D derived / A assumed. 'CP8' = value computed in this session with CoolProp 8.0 and typed as a
constant (as gen_pid_urea.py does). Gaps are listed in docs/pid/urea_detail/AREA_70_NOTES.md.
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *
import gen_pid_urea as g

AREA = "70"
# ---- constants -----------------------------------------------------------------------------------------------
H_FG_LP = 2133.4        # kJ/kg latent heat of steam at 4 bar (143.6 C) (CP8)
H_FG_100 = 2256.4       # kJ/kg latent heat of water at 100 C (CP8)
DHS_TURB = 1091.4       # kJ/kg isentropic drop 50 bar / 400 C to 0.1 bar (CP8); exhaust 45.8 C (CP8)
H_COND_TURB = 2186.3    # kJ/kg condensing duty per kg of exhaust at eta 0.75 (CP8, quality 0.914)
ETA_T = 0.75            # A: turbine isentropic efficiency
CP_W = 4.18
TOL = 5e-5          # relative: Rev B 18+19+24 differs from 21 by 1.3e-5 (its molar-mass table: urea 60.056 vs 2 x 17.031 + 44.01 - 18.015)
F_HP = 0.80             # A (0.70-0.90): fraction of the Rev B recycle (stream 24) that the HP stripper returns as gas to E-601
G_MP = 0.75             # A (0.6-0.9): share of the remaining recycle released in the MP decomposer; rest in the LP decomposer
V7_FRAC = 0.005         # A (0.2-1.0 %): inert / uncondensed vent from E-601 to the HP scrubber, fraction of stripper overhead
AIR_MOL = 0.005         # A (0.2-1.0 mol %): passivation air as mol fraction of the CO2 (rate is a licensor item: placeholder)
DH_CARB = 100.0         # kJ/mol CO2 condensed to carbamate, A (80-130): NOT sourced; replace with licensor / literature value
FRAC_COND = 0.90        # A: fraction of the CO2 in the gas that reacts / condenses in the carbamate condensers
P_MP, P_LP, P_VAC = 18.0, 4.0, 0.3     # bar abs, A (12-25, 2-6, 0.05-0.4)
X_MELT = 0.96           # A (0.95-0.997): urea mass fraction of the melt to the granulator
T_MELT = 138.0          # C, A (135-145)
Y_AIR = 0.05            # kg water per kg dry air in the granulator off-gas, A (0.03-0.08) -> air flow is a lower bound
DUST = 0.005            # A (0.2-1.0 %): urea dust carried out of G-601, fraction of product
SCRUB_CONC = 0.10       # A (5-20 wt %): urea in the dust-scrubber liquor
DES_FRAC = 0.005        # A (0.2-1.0 wt %): NH3 + CO2 in the process condensate to the desorber
STEAM_SHARES = dict(strip=0.60, mp=0.18, lp=0.12, hyd=0.10)     # A: split of the urea-train steam left after the evaporator (sum 1)
RHO = dict(carb=1000.0, soln=1150.0, melt=1230.0, eff=1050.0, dense_hp=300.0)    # A, kg/m3 (line and vessel sizing only)


def two_rho(mg, rg, ml, rl): return (mg + ml) / (mg / rg + ml / rl)


def detectors(sh, pkg, lp, x=1066, y=736, what="NH3"):
    lab(sh, x - 40, y - 26, f"{what} detectors", 8.5, 700, "start", RED)
    bub(sh, pkg, sh, x - 20, y, "AT", f"{lp}71", "area", f"{what} gas detector", "0-300 ppm", "H 25 ppm / HH 150 ppm (A)")
    bub(sh, pkg, sh, x + 20, y, "AAHH", f"{lp}72", "area", f"{what} detector HH -> ESD (2oo2)", "0-300 ppm", "HH 150 ppm (A)", panel=True)
    lab(sh, x - 40, y + 26, "limits A (HSE to confirm)", 7.5, 400, "start", GREY)


def lvalve(sh, pkg, x, y, tag, line, size, svc, fail="FC"):
    ctrlvalve(sh, x, y, 90); pkg.valves.append([tag, "control", svc, line, size, fail, sh.no])


def balance():
    R = {}
    s18, s19, s21, s22, s23, s24 = (g.M[i] * 3.6 * K for i in (18, 19, 21, 22, 23, 24))
    assert abs(s18 + s19 + s24 - s21) < TOL * s21 and abs(s22 + s23 + s24 - s21) < TOL * s21, "Rev B urea loop closure"
    assert abs(s18 + s19 - s22 - s23) < TOL * s21
    R.update(s18=s18, s19=s19, s21=s21, s22=s22, s23=s23, s24=s24)
    air = AIR_MOL * s19 / 44.01 * 28.96; R["air"] = air          # t/h; 28.96 kg/kmol dry air (physical constant)
    s19a = s19 + air; R["s19a"] = s19a
    O = s19a + F_HP * s24; G = (1 - F_HP) * s24
    V7 = V7_FRAC * O; assert V7 > air, "vent must carry the passivation air"
    R.update(O=O, G=G, V7=V7)
    R["gmp"], R["glp"] = G_MP * G, (1 - G_MP) * G
    R["c703"] = O + s18 - V7                           # E-601 condensate to R-601
    R["c704"] = G + V7 - air                           # HP scrubber bottoms to R-601
    R["feed_r"] = R["c703"] + R["c704"]
    assert abs(R["feed_r"] - s21) < TOL * s21, "R-601 feed = Rev B 21"
    R["B"] = s21 + s19a - O                            # stripper bottoms
    assert abs(R["B"] - (s22 + s23 + G)) < TOL * s21
    R["B_mp"] = R["B"] - R["gmp"]; R["SOL"] = s22 + s23; assert abs(R["B_mp"] - R["glp"] - R["SOL"]) < TOL * s21
    R["urea_wt"] = s22 / R["SOL"]
    # carbamate heat (A): CO2 mol/s in the gases
    co2_frac24 = g.S[24]["CO2"] * 44.01 / g.mass(g.S[24]) / 1000.0     # mass fraction of CO2 in Rev B stream 24
    n_co2_O = (s19 + F_HP * s24 * co2_frac24) * 1000 / 3600 / 44.01 * 1000    # mol/s
    R["Q601"] = FRAC_COND * n_co2_O * DH_CARB / 1e3                     # MW
    n_co2_G = G * co2_frac24 * 1000 / 3600 / 44.01 * 1000
    R["Q603"] = FRAC_COND * n_co2_G * G_MP * DH_CARB / 1e3 * 1.0        # MP condenser (gas share only)
    R["Q604"] = FRAC_COND * n_co2_G * (1 - G_MP) * DH_CARB / 1e3        # LP condenser
    R["m_lp601"] = R["Q601"] * 1e3 / H_FG_LP * 3.6                      # t/h LP steam raised in E-601
    R["co2_frac24"] = co2_frac24
    # evaporation / granulation
    dust = DUST * s22; R["dust"] = dust
    melt = (s22 + dust) / X_MELT; w_melt = melt - (s22 + dust)
    scrub_liq = dust / SCRUB_CONC; wash = scrub_liq - dust
    R.update(melt=melt, w_melt=w_melt, scrub_liq=scrub_liq, wash=wash)
    R["evap_feed"] = R["SOL"] + scrub_liq
    R["W_ev"] = s23 + wash - w_melt
    assert abs(R["evap_feed"] - melt - R["W_ev"]) < TOL * melt, "E-602 mass closure"
    R["Q602"] = R["W_ev"] * 1e3 / 3600 * H_FG_100 / 1e3                    # MW (D: latent only, sensible/BPE ignored A)
    R["m_st602"] = R["Q602"] * 1e3 / H_FG_LP * 3.6
    st_tot = g.STEAM_UREA_T_H * K; rest = st_tot - R["m_st602"]; assert rest > 0, (st_tot, R["m_st602"])
    assert abs(sum(STEAM_SHARES.values()) - 1) < 1e-12
    R["st"] = {k: v * rest for k, v in STEAM_SHARES.items()}; R["st"]["ev"] = R["m_st602"]; R["st_tot"] = st_tot
    R["air_gr"] = w_melt / Y_AIR
    R["offgas"] = R["air_gr"] + w_melt + dust
    # vacuum system and treatment
    R["motive"] = 1.5; R["vent_vac"] = 0.3                               # t/h, A (placeholders; vendor)
    R["cond_vac"] = R["W_ev"] + R["motive"] - R["vent_vac"]
    R["des_g"] = DES_FRAC * R["cond_vac"]
    R["clean"] = R["cond_vac"] - R["des_g"]
    R["clean_net"] = R["clean"] - wash
    # Rev B stream 23 = net clean condensate + granulator vapour + desorber NH3/CO2 (+ steam balance neglected)
    # turbine
    R["P601"] = g.K601_MW * K           # D: Rev B power x K (gen_pid_urea.K601_MW is at the Rev B 1.10 Mt/a rate)
    R["m_turb"] = R["P601"] * 1e3 / (ETA_T * DHS_TURB) * 3.6
    R["Q_turb_cond"] = R["m_turb"] / 3.6 * H_COND_TURB / 1e3
    R["m_cw_turb"] = R["Q_turb_cond"] * 1e3 / (CP_W * 12.0) * 3.6
    R["wA"] = 0.536 * R["P601"]; R["wB"] = 0.464 * R["P601"]
    return R


def build(pkg):
    R = balance(); S = stream
    # ================= streams =================
    co2_in = simple("700", "CO2 + passivation air to K-601A", "gas", R["s19a"], 40.0, 1.5, mw=44.01); co2_in.rho_in = 2.6
    k_mid = simple("702", "K-601A discharge, cooled", "gas", R["s19a"], 40.0, 15.0, mw=44.01); k_mid.rho_in = 27.1
    s19 = stream(19, "CO2 to C-601 (K-601B out)", "liq", flow=R["s19a"], rho=780.2)
    ds_i = lambda T, P, mw: None
    nh3_pre = stream(18, "NH3 to V-601 (preheated)", "liq", T=40.0, P=25.0, rho=580.7)
    s18 = stream(18, "NH3 to E-601 (P-601 out)", "liq", rho=594.0)
    s21 = stream(21, "urea reactor effluent", "liq", rho=RHO["eff"])
    s703 = simple("703", "carbamate from E-601", "liq", R["c703"], 170.0, 150.0, rho=RHO["carb"])
    s704 = simple("704", "HP scrubber bottoms", "liq", R["c704"], 150.0, 150.0, rho=RHO["carb"])
    s705 = simple("705", "R-601 feed (mixed)", "liq", R["feed_r"], 165.0, 150.0, rho=RHO["eff"])
    s706 = simple("706", "stripper overhead gas", "gas", R["O"], 170.0, 150.0, mw=30.0, rho=RHO["dense_hp"])
    s707 = simple("707", "stripped urea solution", "liq", R["B"], 185.0, 150.0, rho=RHO["soln"])
    steam25 = lambda i, n, f: simple(i, n, "steam", f, 224.0, 25.0, mw=18.015)
    st_strip = steam25("708", "steam to C-601 (25 bar sat.)", R["st"]["strip"])
    cond_strip = simple("709", "steam condensate from C-601", "liq", R["st"]["strip"], 224.0, 25.0, rho=840.0)
    e601_hot = simple("710", "E-601 inlet (overhead + NH3)", "twophase", R["O"] + R["s18"], 170.0, 150.0, rho=RHO["dense_hp"])
    e601_out = simple("711", "E-601 outlet to R-601", "liq", R["c703"], 170.0, 150.0, rho=RHO["carb"])
    bfw = simple("712", "BFW to E-601", "liq", R["m_lp601"], 105.0, 6.0, rho=955.0)
    lps = simple("713", "LP steam from E-601 (4 bar)", "steam", R["m_lp601"], 143.6, 4.0, mw=18.015)
    v7 = simple("714", "E-601 vent to HP scrubber", "gas", R["V7"], 170.0, 150.0, mw=28.0, rho=RHO["dense_hp"] * 0.5)
    v_out = simple("715", "scrubbed vent (air, inerts)", "gas", R["air"], 60.0, 18.0, mw=28.96)
    carbG = simple("716", "HP carbamate from P-602", "liq", R["G"], 100.0, 152.0, rho=RHO["carb"])
    mp_feed = simple("717", "urea solution to C-602 (after LV)", "twophase", R["B"], 170.0, P_MP, rho=two_rho(R["gmp"], 15.0, R["B"] - R["gmp"], RHO["soln"]))
    mp_gas = simple("718", "MP gas (NH3, CO2)", "gas", R["gmp"], 160.0, P_MP, mw=26.0); mp_gas.rho_in = P_MP * 1e5 * 0.026 / (R_GAS * 433.15)
    mp_liq = simple("719", "MP bottoms to C-604", "liq", R["B_mp"], 160.0, P_MP, rho=RHO["soln"])
    st_mp = simple("720", "steam to C-602 (12 bar sat.)", "steam", R["st"]["mp"], 188.0, 12.0, mw=18.015)
    mp_cond_in = simple("721", "E-603 inlet (MP gas + LP carbamate)", "twophase", R["G"], 150.0, P_MP, rho=two_rho(R["gmp"], 12.0, R["glp"], RHO["carb"]))
    mp_carb = simple("722", "MP carbamate solution", "liq", R["G"], 100.0, P_MP, rho=RHO["carb"])
    cw = lambda i, n, T, f: simple(i, n, "liq", f, T, 4.5, rho=995.0 if T < 35 else 990.0)
    m_cw603 = R["Q603"] * 1e3 / (CP_W * 12.0) * 3.6; m_cw604 = R["Q604"] * 1e3 / (CP_W * 12.0) * 3.6
    cw603 = (cw("723", "cooling water to E-603", 30.0, m_cw603), cw("724", "cooling water return E-603", 42.0, m_cw603))
    cw604 = (cw("725", "cooling water to E-604", 30.0, m_cw604), cw("726", "cooling water return E-604", 42.0, m_cw604))
    lp_feed = simple("727", "solution to C-604 (after LV)", "twophase", R["B_mp"], 150.0, P_LP, rho=two_rho(R["glp"], 3.5, R["SOL"], RHO["soln"]))
    lp_gas = simple("728", "LP gas (NH3, CO2, water vapour)", "gas", R["glp"], 130.0, P_LP, mw=26.0); lp_gas.rho_in = P_LP * 1e5 * 0.026 / (R_GAS * 403.15)
    lp_sol = simple("729", "LP bottoms: urea solution", "liq", R["SOL"], 130.0, P_LP, rho=RHO["soln"])
    st_lp = simple("730", "LP steam to C-604", "steam", R["st"]["lp"], 143.6, 4.0, mw=18.015)
    lp_carb = simple("731", "LP carbamate solution", "liq", R["glp"], 60.0, P_LP, rho=RHO["carb"])
    lp_carb_p = simple("732", "LP carbamate after P-603", "liq", R["glp"], 60.0, P_MP + 2, rho=RHO["carb"])
    mp_carb_in = simple("733", "carbamate to V-603 / P-602 suction", "liq", R["G"], 100.0, P_MP, rho=RHO["carb"])
    # evaporation
    ev_feed = simple("734", "solution to E-602", "liq", R["evap_feed"], 130.0, P_LP, rho=RHO["soln"])
    ev_out = simple("735", "E-602 outlet (melt + vapour)", "twophase", R["evap_feed"], 128.0, P_VAC, rho=two_rho(R["W_ev"], P_VAC * 1e5 * 0.018 / (R_GAS * 401.15), R["melt"], RHO["melt"]))
    st_ev = simple("736", "LP steam to E-602", "steam", R["st"]["ev"], 143.6, 4.0, mw=18.015)
    cond_ev = simple("737", "steam condensate from E-602", "liq", R["st"]["ev"], 143.6, 4.0, rho=920.0)
    vap = simple("738", "evaporator vapour to vacuum system", "gas", R["W_ev"], 70.0, P_VAC, mw=18.015); vap.rho_in = P_VAC * 1e5 * 0.018015 / (R_GAS * 343.15)
    melt_v = simple("739", "melt from V-605", "liq", R["melt"], T_MELT, P_VAC, rho=RHO["melt"])
    melt_p = simple("740", "melt to G-601 (P-604 out)", "liq", R["melt"], T_MELT, 6.0, rho=RHO["melt"])
    vac_cond = simple("741", "process condensate", "liq", R["cond_vac"], 50.0, 1.5, rho=988.0)
    motive = simple("742", "ejector motive steam", "steam", R["motive"], 143.6, 4.0, mw=18.015)
    vac_vent = simple("743", "vacuum non-condensables to scrubber", "gas", R["vent_vac"], 40.0, 1.05, mw=28.0)
    cw_vac = (cw("744", "cooling water to VAC-601", 30.0, 1500.0), cw("745", "cooling water return VAC-601", 42.0, 1500.0))
    # granulation
    air_g = simple("746", "fluidising air to G-601", "gas", R["air_gr"], 40.0, 1.1, mw=28.96)
    gran = stream(22, "urea granules to conveying", "slurry", flow=R["s22"], rho=750.0)
    off = simple("747", "G-601 off-gas (air, water, dust)", "gas", R["offgas"], 90.0, 1.0, mw=28.96)
    assert abs(R["melt"] - (R["s22"] + R["w_melt"] + R["dust"])) < TOL * R["melt"], "G-601 urea+water closure"
    wash = simple("748", "wash water to C-605", "liq", R["wash"], 40.0, 3.0, rho=992.0)
    top = simple("749", "scrubbed air to stack", "gas", R["air_gr"] + R["w_melt"], 45.0, 1.0, mw=28.9)
    bot = simple("750", "dust-scrubber liquor to E-602 feed", "liq", R["scrub_liq"], 45.0, 2.0, rho=1030.0)
    assert abs(off.flow + wash.flow - top.flow - bot.flow) < TOL * off.flow
    # treatment
    hyd_in = simple("751", "process condensate to R-602", "liq", R["cond_vac"], 60.0, 20.0, rho=988.0)
    hyd_out = simple("752", "hydrolysed condensate to C-606", "liq", R["cond_vac"], 190.0, 20.0, rho=880.0)
    st_hyd = steam25("753", "steam to R-602 / E-607", R["st"]["hyd"] * 0.6)
    des_in = simple("754", "condensate to C-606 (after E-607)", "liq", R["cond_vac"], 150.0, P_LP, rho=920.0)
    st_des = simple("755", "stripping steam to C-606", "steam", R["st"]["hyd"] * 0.4, 143.6, 4.0, mw=18.015)
    des_top = simple("756", "C-606 overhead (NH3, CO2, steam) to E-604", "gas", R["des_g"] + R["st"]["hyd"] * 0.4, 140.0, P_LP - 0.5, mw=20.0); des_top.rho_in = (P_LP - 0.5) * 1e5 * 0.020 / (R_GAS * 413.15)
    des_bot = simple("757", "clean process condensate", "liq", R["clean"], 145.0, P_LP, rho=920.0)
    # water balance check on Rev B stream 23 (D): net clean condensate + granulator water vapour + desorber NH3/CO2 = Rev B 23 (within steam-share bookkeeping)
    gap23 = R["clean_net"] + R["w_melt"] + R["des_g"] - (R["motive"] - R["vent_vac"]) - R["s23"]
    assert abs(gap23) < 1e-6 * R["s23"] + 1e-9, gap23
    # ================= 701 K-601A =================
    w_hot = 153.0
    sheet_compressor(pkg, AREA, 701, "Area 70  Urea synthesis  -  K-601A CO2 compressor, LP casing (1.5 to 15 bar)",
        dict(tag="K-601A", name="CO2 compressor, LP casing (2 stages)", suction=co2_in, discharge=k_mid, power_MW=R["wA"], driver="steam turbine", spec="SS",
             hazard="CO2 asphyxiant, wet CO2 corrosive",
             notes=[f"K-601 is a four-stage train in two casings. Total shaft power {R['P601']:.1f} MW is the Rev B S value (UBA 2001 p.24, 126 kWh/t CO2); the split 53.6 / 46.4 % between casings comes from a CoolProp isentropic calculation (eta 0.75, intercooled to 40 C) which itself gives 105 kWh/t (D, CP8, 17 % below UBA).",
                    f"Stream 700 = Rev B CO2 (19: {R['s19']:.1f} t/h) + passivation air {R['air']:.2f} t/h (A: {AIR_MOL*100:g} mol % of the CO2, placeholder: the rate is a licensor item). Suction 1.5 bar is the C-302 CO2 outlet 2 bar less 0.5 bar (A).",
                    f"Stage discharge about {w_hot:.0f} C before intercooling (CP8, eta 0.75). Intercooler is the template 'K-601A-AC'; condensate from the intercooler is acidic and needs a corrosion-resistant drain (gap).",
                    "Stream 20 (surplus CO2, Rev B) bypasses K-601: only stream 19 is compressed."]))
    detectors(pkg.sheets[-1], pkg, "701", what="CO2")
    # ================= 702 K-601B =================
    sheet_compressor(pkg, AREA, 702, "Area 70  Urea synthesis  -  K-601B CO2 compressor, HP casing (15 to 150 bar)",
        dict(tag="K-601B", name="CO2 compressor, HP casing (2 stages)", suction=k_mid, discharge=s19, power_MW=R["wB"], driver="steam turbine", spec="SS",
             hazard="CO2 at 150 bar, dense phase",
             notes=["Discharge 150 bar, 40 C is the Rev B stream 19 (S). At 40 C and 150 bar CO2 is a dense fluid (780 kg/m3, CP8): line sized as liquid at 2 m/s (A).",
                    "Passivation air rides with the CO2 into C-601 and leaves with the scrubbed vent (sheet 708). Oxygen consumption by the passivation layer is neglected in the mass balance (A).",
                    "Anti-surge is in the template; for a 150 bar dense-phase discharge the recycle cooler and check-valve arrangement are vendor items (gap). Interlock: no start without the CO2 passivation air available (not drawn)."]))
    detectors(pkg.sheets[-1], pkg, "702", what="CO2")
    # ================= 703 turbine =================
    steam_in = simple("751T", "HP steam to K-601 turbine", "steam", R["m_turb"], 400.0, 50.0, mw=18.015)
    t_cond = simple("752T", "turbine condensate", "liq", R["m_turb"], 45.8, 0.1, rho=990.0)
    cwt = (cw("753T", "cooling water to turbine condenser", 30.0, R["m_cw_turb"]), cw("754T", "cooling water return", 42.0, R["m_cw_turb"]))
    sheet_package(pkg, AREA, 703, "Area 70  Urea synthesis  -  K-601 steam turbine and surface condenser",
        dict(tag="TG-601", name="K-601 condensing steam turbine + condenser", inlets=[(steam_in, "HP steam 50 bar, 400 C", "ST"), (cwt[0], "cooling water", "CW")],
             outlets=[(t_cond, "condensate", "PL"), (cwt[1], "cooling water return", "CW")], esd=False, spec="A1",
             utilities=[("shaft", R["P601"], "MW", "S UBA"), ("exhaust", R["m_turb"], "t/h", "D"), ("cond duty", R["Q_turb_cond"], "MW", "D")],
             desc=["extraction / back-pressure option not drawn", "exhaust 0.1 bar (A), x = 0.914", f"steam rate {R['m_turb']/R['P601']:.2f} kg/kWh (D)"],
             interlocks=[("SAHH", "overspeed trip", "per vendor", "gap"), ("PAL", "condenser vacuum low", "0-1 bar", "L 0.15 bar abs (A)"), ("TAHH", "exhaust temperature HH", "0-150 C", "HH 90 C (A)"), ("VAHH", "vibration HH", "per vendor", "gap"), ("LAHH", "hotwell level HH", "0-100 %", "HH 90 % (A)")],
             type="steam turbine + surface condenser", op="50 bar / 400 C in, 0.1 bar exhaust", design="A (vendor)", size=f"{R['P601']:.1f} MW shaft", basis="S/D",
             relief="turbine casing / exhaust (rupture disc)",
             rows=[("Shaft", f"{R['P601']:.1f} MW", "S UBA p.24"), ("Steam", f"{R['m_turb']:.0f} t/h", "D"), ("dh isentropic", f"{DHS_TURB} kJ/kg", "CP8"), ("eta", f"{ETA_T}", "A"), ("Condenser", f"{R['Q_turb_cond']:.1f} MW", "D")],
             hazard="HP steam, overspeed",
             notes=[f"Steam = shaft / (eta x isentropic drop) = {R['m_turb']:.0f} t/h (D). The Rev B steam header (50 bar, 400 C) is the supply; condensing at 0.1 bar (45.8 C CP8) and eta 0.75 are assumptions (A).",
                    f"Condenser duty {R['Q_turb_cond']:.0f} MW = steam x 2186 kJ/kg (CP8); CW 30 -> 42 C (A) gives {R['m_cw_turb']:,.0f} t/h (D).",
                    f"A back-pressure or extraction turbine would feed the urea-train steam ({R['st_tot']:.0f} t/h, UBA 0.92 t/t) and change the plant steam balance; it is a design option, not in Rev B (A).",
                    "Turbine is not an NH3/CO2 inventory: no ESD valve is required for process isolation here; steam isolation is by the turbine trip valve (vendor)."]))
    # ================= 704 V-601 + P-601 =================
    sh = sheet_vessel(pkg, AREA, 704, "Area 70  Urea synthesis  -  V-601 NH3 suction vessel and P-601 HP ammonia pumps (25 to 150 bar)",
        dict(tag="V-601", name="NH3 feed vessel", inlet=nh3_pre, gas=None, liq=s18, res_min=5.0, pumps="P-601", pump_dp_bar=125.0, spec="LT", svc_in="NH3", svc_liq="NH3",
             mat="A: carbon steel (NH3 liquid 25 bar)", hazard="liquid NH3 at 25 bar, toxic", relief_case="blocked outlet; fire; thermal expansion", relief_dest="NH3 vent absorber C-501 (area 60)",
             notes=["NH3 arrives from T-501 / P-501 at -33 C and is warmed to 40 C in an NH3 preheater (E-607, not drawn) before this vessel; the preheater duty is about 25 kg/s x 4.6 kJ/kg/K x 73 K = 8.5 MW of low-grade heat (D, cp from CP8 at 0 C).",
                    f"P-601A/B raise 25 -> 150 bar (Rev B stream 18 S): dP 125 bar (D), shaft power per template at eta 0.70 (A). Centrifugal multistage or plunger: not decided (gap).",
                    "Template draws the level valve in the pump discharge line. For a 125 bar discharge the level / flow control is by pump speed or a recycle valve; the LV symbol on this sheet is a template artefact (defect).",
                    "Pump seals: NH3 leak containment (double mechanical seal, flush to closed drain) is not drawn."]))
    detectors(sh, pkg, "704", what="NH3")
    # ================= 705 R-601 =================
    sh = sheet_vessel(pkg, AREA, 705, "Area 70  Urea synthesis  -  R-601 urea reactor (180 C, 150 bar)",
        dict(tag="R-601", name="Urea reactor", inlet=s705, gas=None, liq=s21, res_min=30.0, spec="SS", svc_in="UR", svc_liq="UR",
             mat="A: stainless steel / zirconium lining (urea-carbamate corrosion); licensor", hazard="NH3, CO2, carbamate at 150 bar", relief_case="blocked outlet; thermal expansion; fire", relief_dest="HP scrubber C-603 / flare",
             notes=[f"Feed {R['feed_r']:.1f} t/h = E-601 carbamate {R['c703']:.1f} + HP scrubber bottoms {R['c704']:.1f}; effluent = Rev B stream 21 ({R['s21']:.1f} t/h) (D, closure asserted).",
                    "Residence time 30 min (A) sets the volume in the template (50 % fill rule); Rev B gives only the net per-pass conversion, not a kinetic volume. Operating temperature 180 C and pressure 150 bar are Rev B S values.",
                    "Drawn with the vessel template: sieve trays, lining and the effluent overflow nozzle are not shown. The reactor has no PIC of its own: pressure is set by the HP scrubber vent valve (sheet 708).",
                    "Template defect: drain / vent valves are drawn with a generic symbol; in carbamate service they are specified by the licensor. ESD: the NH3 feed (P-601) and CO2 (K-601B) are isolated at LAHH / PAHH."]))
    detectors(sh, pkg, "705", what="NH3/CO2")
    # ================= 706 C-601 =================
    sheet_column(pkg, AREA, 706, "Area 70  Urea synthesis  -  C-601 HP CO2 stripper (falling film)",
        dict(tag="C-601", name="HP CO2 stripper", feed=s19, top=s706, bottom=s707, feed2=s21, packing=False, stages=2, reboiler=st_strip, spec="SS", esd=True,
             mat="A: duplex / stainless tubes, lined channel (licensor)", hazard="NH3, CO2, carbamate, hot",
             notes=[f"CO2-stripping layout (Stamicarbon-type, licensor name only): reactor effluent flows down the tubes, fresh CO2 ({R['s19a']:.1f} t/h incl. air) strips NH3 and CO2 out as stream 706 = {R['O']:.1f} t/h.",
                    f"Overhead gas = CO2 + F_HP x stream 24, F_HP = {F_HP} (A 0.7-0.9, licensor item); bottoms {R['B']:.1f} t/h = urea 160.4 + water 48.1 + (1-F_HP) x 24 (closure asserted).",
                    f"Steam {R['st']['strip']:.0f} t/h at 25 bar sat. (A): share of the UBA total {R['st_tot']:.0f} t/h (S, 0.92 t/t urea) left after the evaporator; stripper wall temperature is limited by corrosion (gap).",
                    "Template shows a column with trays; the shell-and-tube falling-film geometry is not drawn. Tube-rupture steam-to-process leak and the CO2 passivation interlock are licensor items."]))
    detectors(pkg.sheets[-1], pkg, "706", what="NH3/CO2")
    # ================= 707 E-601 =================
    sheet_hx(pkg, AREA, 707, "Area 70  Urea synthesis  -  E-601 HP carbamate condenser (LP steam raising)",
        dict(tag="E-601", name="HP carbamate condenser", hot_in=e601_hot, hot_out=e601_out, cold_in=bfw, cold_out=lps, duty_MW=R["Q601"], kind="cond", spec="SS", spec_c="A1", svc_c="BFW", esd_hot=True,
             mat="A: stainless / duplex, Zr-lined (licensor)", hazard="NH3, CO2, carbamate at 150 bar",
             notes=[f"Duty {R['Q601']:.0f} MW = {FRAC_COND*100:.0f} % (A) of the CO2 in the gas x {DH_CARB:g} kJ/mol (A 80-130, NOT sourced: no document read). Treat as a placeholder; replace with the licensor value.",
                    f"LP steam raised {R['m_lp601']:.0f} t/h at 4 bar (D = duty / 2133 kJ/kg CP8). This exceeds the net UBA steam import ({R['st_tot']:.0f} t/h) because it is reused in C-604, E-602 and the hydrolyser; the plant steam balance is a gap.",
                    f"Hot inlet {R['O']+R['s18']:.0f} t/h = stripper overhead + fresh NH3 (stream 18); outlet {R['c703']:.0f} t/h after the {R['V7']:.2f} t/h vent to the HP scrubber (sheet 708).",
                    "Pool or falling-film type is open (licensor). Rev B stream 24 (170 C) is represented by streams 706 / 703 here."]))
    detectors(pkg.sheets[-1], pkg, "707", what="NH3/CO2")
    # ================= 708 C-603 =================
    sheet_column(pkg, AREA, 708, "Area 70  Urea synthesis  -  C-603 HP scrubber (carbamate wash of the E-601 vent)",
        dict(tag="C-603", name="HP scrubber", feed=v7, top=v_out, bottom=s704, feed2=carbG, packing=True, stages=4, spec="SS", esd=True,
             mat="A: stainless steel / duplex (licensor)", hazard="NH3, CO2, passivation air vent",
             notes=[f"Vent {R['V7']:.2f} t/h ({V7_FRAC*100:g} % of the overhead, A 0.2-1.0 %) is scrubbed with HP carbamate {R['G']:.1f} t/h; bottoms {R['c704']:.1f} t/h return to R-601 (closure asserted).",
                    f"Scrubbed vent leaves as the passivation air only ({R['air']:.2f} t/h, so air in = air out, D). Residual NH3/CO2 slip is not quantified (needs absorber data: gap) and the vent goes to the MP absorber / stack (A).",
                    "PIC on the vent controls the loop pressure (150 bar S): the template PIC / PV on the top line is this control. Its failure position and overpressure protection (PSV to flare) are drawn by the template.",
                    "Rev B has no separate scrubber; it is added here (Rev C item)."]))
    detectors(pkg.sheets[-1], pkg, "708", what="NH3/CO2")
    # ================= 709 C-602 =================
    sheet_column(pkg, AREA, 709, "Area 70  Urea recovery  -  C-602 MP decomposer (18 bar)",
        dict(tag="C-602", name="MP decomposer", feed=mp_feed, top=mp_gas, bottom=mp_liq, packing=False, stages=2, reboiler=st_mp, spec="SS", esd=True,
             mat="A: stainless / duplex (carbamate service)", hazard="NH3, CO2 at 18 bar",
             notes=[f"MP gas {R['gmp']:.1f} t/h = {G_MP*100:.0f} % (A 60-90) of the recycle that the stripper leaves in the solution; bottoms {R['B_mp']:.1f} t/h (closure asserted).",
                    f"Pressure {P_MP:g} bar and feed 170 C are assumptions (A): no sourced decomposer conditions. Steam {R['st']['mp']:.1f} t/h at 12 bar sat. (A share of the UBA total).",
                    "Rev B carries the recycle as anhydrous NH3 + CO2 (stream 24). Real carbamate carries water; the water recycle raises the reactor load and is a gap for Rev C.",
                    "LV on the stripper bottoms (150 -> 18 bar) is flashing / erosive service; not drawn here."]))
    detectors(pkg.sheets[-1], pkg, "709", what="NH3/CO2")
    # ================= 710 E-603 =================
    sheet_hx(pkg, AREA, 710, "Area 70  Urea recovery  -  E-603 MP carbamate condenser",
        dict(tag="E-603", name="MP carbamate condenser", hot_in=mp_cond_in, hot_out=mp_carb, cold_in=cw603[0], cold_out=cw603[1], duty_MW=R["Q603"], kind="cond", spec="SS", spec_c="A1", svc_c="CW", esd_hot=True,
             mat="A: stainless (carbamate)", hazard="NH3 / CO2 / carbamate, CW ingress",
             notes=[f"Duty {R['Q603']:.1f} MW = {FRAC_COND*100:.0f} % x CO2 in the MP gas x {DH_CARB:g} kJ/kmol-basis (A, NOT sourced). CW 30 -> 42 C (A): {m_cw603:,.0f} t/h (D).",
                    f"Hot side combines MP gas {R['gmp']:.1f} t/h with LP carbamate {R['glp']:.1f} t/h from P-603 (total {R['G']:.1f} t/h).",
                    "Carbamate crystallisation (solidification) when cooled too far is a real operating limit; the outlet 100 C and any trace heating are A placeholders (gap)."]))
    detectors(pkg.sheets[-1], pkg, "710", what="NH3/CO2")
    # ================= 711 V-603 + P-602 =================
    sh = sheet_vessel(pkg, AREA, 711, "Area 70  Urea recovery  -  V-603 MP carbamate vessel and P-602 HP carbamate pumps (18 to 150 bar)",
        dict(tag="V-603", name="MP carbamate vessel", inlet=mp_carb_in, gas=None, liq=carbG, res_min=10.0, pumps="P-602", pump_dp_bar=132.0, spec="SS", svc_in="UR", svc_liq="UR",
             mat="A: stainless steel (carbamate)", hazard="NH3 / CO2 carbamate solution", relief_case="blocked outlet; fire", relief_dest="MP absorber / flare",
             notes=[f"P-602A/B lift carbamate {R['G']:.1f} t/h from {P_MP:g} to 150 bar (dP 132 bar, D) and feed the HP scrubber C-603 (stream 716). Carbamate density 1000 kg/m3 is an assumption (A).",
                    "Plunger or multistage pumps in carbamate service: material and seal choice is a licensor item (gap). Dry-run trip on LALL from the template.",
                    "As on sheet 704, the template places the level valve on the pump discharge; for a 132 bar discharge that is a template artefact (defect)."]))
    detectors(sh, pkg, "711", what="NH3/CO2")
    # ================= 712 C-604 =================
    sheet_column(pkg, AREA, 712, "Area 70  Urea recovery  -  C-604 LP decomposer / rectifier (4 bar)",
        dict(tag="C-604", name="LP decomposer / rectifier", feed=lp_feed, top=lp_gas, bottom=lp_sol, packing=True, stages=6, reboiler=st_lp, spec="SS", esd=True,
             mat="A: stainless (carbamate)", hazard="NH3, CO2, hot urea solution",
             notes=[f"Bottoms {R['SOL']:.1f} t/h = urea {R['s22']:.1f} + water {R['s23']:.1f} t/h = {R['urea_wt']*100:.1f} wt % urea (D), i.e. Rev B streams 22 + 23; top gas {R['glp']:.1f} t/h (closure asserted).",
                    f"LP pressure {P_LP:g} bar is an assumption (A 2-6); steam {R['st']['lp']:.1f} t/h at 4 bar (A share of the UBA total).",
                    "Biuret formation and hydrolysis losses in the hot urea solution are not in Rev B (A: zero). Urea solution temperatures must be limited (gap: no biuret model)."]))
    detectors(pkg.sheets[-1], pkg, "712", what="NH3/CO2")
    # ================= 713 E-604 =================
    sheet_hx(pkg, AREA, 713, "Area 70  Urea recovery  -  E-604 LP carbamate condenser",
        dict(tag="E-604", name="LP carbamate condenser", hot_in=lp_gas, hot_out=lp_carb, cold_in=cw604[0], cold_out=cw604[1], duty_MW=R["Q604"], kind="cond", spec="SS", spec_c="A1", svc_c="CW", esd_hot=True,
             mat="A: stainless", hazard="NH3 / CO2, low pressure",
             notes=[f"Duty {R['Q604']:.1f} MW (A basis as E-603); CW {m_cw604:,.0f} t/h (D). Also receives the desorber overhead (stream 756, {R['des_g']:.2f} t/h NH3 + CO2 plus stripping steam) in practice; added to this duty is not included (A).",
                    "Low-pressure NH3 vapour inventory: ESD valve on the gas inlet; CW tube leak monitored by conductivity / NH3 (not drawn)."]))
    detectors(pkg.sheets[-1], pkg, "713", what="NH3")
    # ================= 714 V-604 + P-603 =================
    sh = sheet_vessel(pkg, AREA, 714, "Area 70  Urea recovery  -  V-604 LP carbamate vessel and P-603 LP carbamate pumps",
        dict(tag="V-604", name="LP carbamate vessel", inlet=lp_carb, gas=None, liq=lp_carb_p, res_min=10.0, pumps="P-603", pump_dp_bar=16.0, spec="SS", svc_in="UR", svc_liq="UR",
             mat="A: stainless steel", hazard="NH3 / CO2 carbamate solution", relief_case="blocked outlet; fire", relief_dest="LP absorber / flare",
             notes=[f"P-603A/B lift LP carbamate {R['glp']:.1f} t/h from {P_LP:g} to {P_MP+2:g} bar to the MP condenser E-603 (dP 16 bar, A).",
                    "Atmospheric vent of the vessel goes to the LP absorber / stack (not drawn: the absorber is not in Rev B, gap).",
                    "Template level valve on the pump discharge is a template artefact."]))
    detectors(sh, pkg, "714", what="NH3/CO2")
    # ================= 715 E-602 =================
    sheet_hx(pkg, AREA, 715, "Area 70  Urea concentration  -  E-602 vacuum evaporator heater",
        dict(tag="E-602", name="Evaporator heater (LP steam)", hot_in=st_ev, hot_out=cond_ev, cold_in=ev_feed, cold_out=ev_out, duty_MW=R["Q602"], kind="boil", spec="SS", spec_c="SS", svc_c="UR", esd_hot=False,
             mat="A: stainless steel", hazard="hot urea solution, vacuum", relief_dest="atmosphere (vacuum breaker) / safe location (A)",
             notes=[f"Evaporation {R['W_ev']:.1f} t/h = Rev B water {R['s23']:.1f} + scrubber wash {R['wash']:.1f} - water left in the melt {R['w_melt']:.2f} t/h (melt {X_MELT*100:g} wt % urea, A 95-99.7). Closure asserted.",
                    f"Duty {R['Q602']:.1f} MW = evaporation x 2256 kJ/kg (CP8); steam {R['st']['ev']:.0f} t/h at 4 bar (D). Single effect, no boiling-point rise: a 2-stage layout would cut steam (A).",
                    "Melt concentration for fluid-bed granulation is lower than for prilling; the 96 % value is an assumption, not sourced.",
                    "No ammonia ESD valve: NH3 content is low here (< 0.5 wt %, A); the steam side has an ESD for steam trip not drawn."]))
    sh = pkg.sheets[-1]
    detectors(sh, pkg, "715", what="NH3")
    # ================= 716 V-605 + P-604 =================
    sh = sheet_vessel(pkg, AREA, 716, "Area 70  Urea concentration  -  V-605 vacuum separator and P-604 melt pumps",
        dict(tag="V-605", name="Vacuum separator (melt)", inlet=ev_out, gas=vap, liq=melt_v, res_min=3.0, pumps="P-604", pump_dp_bar=6.0, spec="SS", svc_in="UR", svc_gas="PG", svc_liq="UR",
             internals="demister", mat="A: stainless steel (urea melt), steam-jacketed", hazard="hot urea melt, vacuum", relief_case="vacuum breaker; blocked vapour line", relief_dest="atmosphere (via safe location)",
             notes=[f"Melt {R['melt']:.1f} t/h at {T_MELT:g} C (A 135-145; the melt freezing point needs a sourced value: gap) goes to G-601 spray nozzles at 6 bar (A). Vapour {R['W_ev']:.1f} t/h to the vacuum system.",
                    f"Operating {P_VAC:g} bar abs (A 0.05-0.4). Template defect: design pressure is set as operating + 2 bar, which is meaningless for a vacuum vessel; design for full vacuum plus steam-trace temperature (not computed).",
                    "All lines in melt service are steam-traced / jacketed (not drawn); entrained urea in the vapour is captured in the condenser (VAC-601).",
                    "Template pump LV is the melt flow control to the granulator; a spray-pressure PIC would normally govern (gap)."]))
    detectors(sh, pkg, "716", what="NH3")
    # ================= 717 VAC-601 =================
    sheet_package(pkg, AREA, 717, "Area 70  Urea concentration  -  VAC-601 vacuum condenser and ejector system",
        dict(tag="VAC-601", name="Vacuum condenser + steam ejectors", inlets=[(vap, "evaporator vapour", "PG"), (motive, "ejector motive steam", "ST"), (cw_vac[0], "cooling water", "CW")],
             outlets=[(vac_cond, "process condensate to R-602", "PL"), (vac_vent, "non-condensables to scrubber", "PG"), (cw_vac[1], "cooling water return", "CW")], esd=False, spec="SS",
             utilities=[("motive steam", R["motive"], "t/h", "A"), ("duty", R["W_ev"] * 1e3 / 3600 * H_FG_100 / 1e3, "MW", "D")],
             desc=["surface condenser + 2-stage ejector (A)", f"vacuum {P_VAC:g} bar abs (A)", "vent to scrubber / stack"],
             interlocks=[("PAH", "vacuum lost (pressure high)", "0-1 bar", f"H {P_VAC*1.5:.2f} bar (A)"), ("LAHH", "hotwell level HH", "0-100 %", "HH 90 % (A)"), ("AAH", "NH3 in vent", "0-200 ppm", "H 25 ppm (A)")],
             type="vacuum condenser + ejectors", op=f"{P_VAC:g} bar abs", design="full vacuum / 3 bar g (A)", size="gap (vendor)", basis="A", relief="vacuum breaker", relief_set=3.0,
             rows=[("Vapour", f"{R['W_ev']:.1f} t/h", "D"), ("Motive steam", f"{R['motive']:.1f} t/h", "A"), ("Vent", f"{R['vent_vac']:.1f} t/h", "A"), ("Condensate", f"{R['cond_vac']:.1f} t/h", "D")],
             hazard="vacuum, NH3 in vent",
             notes=[f"Condensate {R['cond_vac']:.1f} t/h = vapour + motive steam - non-condensables (closure D). Motive steam {R['motive']:g} t/h and vent {R['vent_vac']:g} t/h are placeholders (A: vendor ejector data not available).",
                    f"CW flow {1500:,.0f} t/h on the sheet is a placeholder (A) for the condenser; duty {R['W_ev']*1e3/3600*H_FG_100/1e3:.1f} MW (D)."]))
    detectors(pkg.sheets[-1], pkg, "717", what="NH3")
    # ================= 718 G-601 =================
    sheet_package(pkg, AREA, 718, "Area 70  Urea granulation  -  G-601 fluid-bed granulator",
        dict(tag="G-601", name="Fluid-bed granulator (urea melt spray)", inlets=[(melt_p, "melt (spray nozzles)", "UR"), (air_g, "fluidising air", "PG")],
             outlets=[(gran, "granules to cooler / screens", "SO"), (off, "off-gas to C-605", "PG")], esd=True, spec="SS",
             utilities=[("air fan", 0.0, "gap", "A"), ("atomising air", 0.0, "gap", "A"), ("steam trace", 0.0, "gap", "A")],
             desc=["melt sprayed on seed granules", "granule growth, drying, cooling", "undersize / oversize recycle not in Rev B", "dust-explosion venting + isolation (A)"],
             interlocks=[("TAHH", "bed temperature HH", "0-200 C", "HH 150 C (A)"), ("PDAL", "bed dP low (defluidised)", "0-100 mbar", "L (vendor)"), ("AAH", "off-gas NH3", "0-200 ppm", "H 25 ppm (A)"), ("TAH", "off-gas T high (fire)", "0-200 C", "H 110 C (A)"), ("SAL", "air fan trip", "-", "trips melt feed (A)")],
             type="fluid-bed granulator", op=f"melt {R['melt']:.0f} t/h, air {R['air_gr']:.0f} t/h", design="vendor", size="gap (vendor)", basis="A", relief="explosion vent panels (dust)",
             rows=[("Melt", f"{R['melt']:.1f} t/h ({X_MELT*100:g} %)", "A"), ("Granules", f"{R['s22']:.1f} t/h", "Rev B 22"), ("Air", f"{R['air_gr']:.0f} t/h", "D lower bound"), ("Dust", f"{R['dust']:.2f} t/h", "A"), ("Water out", f"{R['w_melt']:.2f} t/h", "D")],
             hazard="dust explosion, hot melt, NH3 off-gas",
             notes=[f"Closure: melt {R['melt']:.1f} = granules {R['s22']:.1f} + water {R['w_melt']:.2f} + dust {R['dust']:.2f} t/h (asserted). Dust {DUST*100:g} % of product (A 0.2-1.0); recovered in C-605 and returned to E-602.",
                    f"Air {R['air_gr']:.0f} t/h = water to be removed / {Y_AIR} kg/kg (A 0.03-0.08): a LOWER bound; actual air is set by fluidisation velocity and cooling (vendor, gap).",
                    "Hazard: urea dust is combustible and can form explosive dust clouds; explosion venting, isolation and spark / hot-surface control are required. No standard (NFPA / ATEX) text was read, so no vent area or Kst is stated (gap).",
                    "Stream 22 is drawn as a solid on the line with a slurry rule (1.5 m/s) because the line rules lack a solids class: it is a conveyor, not a pipe (template defect). Rev B stream 22 is 60 C; granule cooler is not in Rev B."]))
    detectors(pkg.sheets[-1], pkg, "718", what="NH3")
    # ================= 719 C-605 =================
    sheet_column(pkg, AREA, 719, "Area 70  Urea granulation  -  C-605 dust scrubber (G-601 off-gas)",
        dict(tag="C-605", name="Dust scrubber", feed=off, top=top, bottom=bot, feed2=wash, packing=True, stages=3, spec="SS", esd=False,
             mat="A: stainless steel / FRP", hazard="urea dust, NH3 traces, wet solution",
             notes=[f"Off-gas {R['offgas']:.0f} t/h (air + water {R['w_melt']:.2f} + dust {R['dust']:.2f}) is washed with {R['wash']:.1f} t/h clean condensate to {SCRUB_CONC*100:g} wt % urea liquor (A 5-20 %): {R['scrub_liq']:.1f} t/h back to the E-602 feed. Closure asserted.",
                    "Saturation of the air by the wash water (evaporation) is not modelled (A): the top stream carries only the melt water. Dust capture efficiency and the NH3 emission limit are gaps (no emission standard fetched).",
                    "Wet scrubber after a dry granulator limits a dust cloud in the stack path; the scrubber is itself not an explosive-atmosphere unit while wet (A, to be confirmed in a DSEAR / ATEX review).",
                    "The template PSV (3 bar g design) and PIC are generic and not meaningful for a near-atmospheric scrubber: engine limit, listed in the notes file; the reboiler is not used."]))
    detectors(pkg.sheets[-1], pkg, "719", what="NH3")
    # ================= 720 R-602 =================
    sheet_package(pkg, AREA, 720, "Area 70  Process condensate treatment  -  R-602 urea hydrolyser",
        dict(tag="R-602", name="Urea hydrolyser (steam heated)", inlets=[(hyd_in, "process condensate", "PL"), (st_hyd, "steam (25 bar sat.)", "ST")],
             outlets=[(hyd_out, "hydrolysed condensate to C-606", "PL")], esd=True, spec="SS",
             utilities=[("steam", R["st"]["hyd"] * 0.6, "t/h", "A"), ("feed/effluent HX", 0.0, "gap", "A")],
             desc=["urea -> NH3 + CO2 at elevated T and P", "190 C, 20 bar (A, range 170-230 C)", "feed / effluent exchanger E-607 (not drawn)"],
             interlocks=[("PAHH", "pressure HH", "0-30 bar", "HH 25 bar (A)"), ("TAHH", "temperature HH", "0-250 C", "HH 215 C (A)"), ("LAHH", "level HH", "0-100 %", "HH 90 % (A)")],
             type="hydrolyser (vessel / reactor)", op="190 C / 20 bar (A)", design=f"{design_conditions(25, 224)[0]:g} bar g / {design_conditions(25, 224)[1]:g} C (D, 25 bar sat. steam side)", size="gap", basis="A", relief="blocked outlet",
             rows=[("Feed", f"{R['cond_vac']:.1f} t/h", "D"), ("Steam", f"{R['st']['hyd']*0.6:.1f} t/h", "A share"), ("T / P", "190 C / 20 bar", "A")],
             hazard="hot NH3 / CO2 / urea solution",
             notes=["Conditions are assumptions: hydrolysis needs a high-temperature, high-pressure step; no kinetic data or licensor figures were available (gap).",
                    "Rev B process water (stream 23) contains no urea; the urea load (about 0.1 wt %, A) is an assumption used only to justify the unit.",
                    "Treated water then goes to the desorber C-606 (sheet 721); steam 60 % of the treatment share (A)."]))
    detectors(pkg.sheets[-1], pkg, "720", what="NH3")
    # ================= 721 C-606 =================
    sheet_column(pkg, AREA, 721, "Area 70  Process condensate treatment  -  C-606 NH3 / CO2 desorber",
        dict(tag="C-606", name="Process condensate desorber", feed=des_in, top=des_top, bottom=des_bot, packing=False, stages=8, reboiler=st_des, spec="SS", esd=True,
             mat="A: stainless steel", hazard="NH3 / CO2 vapour, hot condensate",
             notes=[f"Feed {R['cond_vac']:.1f} t/h with {DES_FRAC*100:g} wt % NH3 + CO2 (A 0.2-1.0); stripping steam {R['st']['hyd']*0.4:.1f} t/h; overhead {des_top.flow:.1f} t/h returns to E-604; bottoms clean condensate {R['clean']:.1f} t/h.",
                    f"Net clean condensate to the battery limit = {R['clean']:.1f} - wash {R['wash']:.1f} = {R['clean_net']:.1f} t/h; with granulator water vapour {R['w_melt']:.2f} and desorber gas {R['des_g']:.2f} t/h this reproduces Rev B stream 23 ({R['s23']:.1f} t/h) after taking out the ejector steam net of the vent ({R['motive']-R['vent_vac']:.1f} t/h, A) (closure asserted).",
                    "Clean-condensate NH3 / urea specification is a gap (needs a discharge or boiler-feed standard). UBA (2001) gives 0.46-0.65 m3 discharged process water per t urea against 0.30 t/t in Rev B (S UBA p.19, 25): other waste waters are not in Rev B."]))
    detectors(pkg.sheets[-1], pkg, "721", what="NH3")
    # ================= 722 conveying =================
    conv_in = simple("758", "granules from G-601 cooler / screens", "slurry", R["s22"], 60.0, 1.0, rho=750.0)
    conv_out = simple("759", "granules to urea store", "slurry", R["s22"], 50.0, 1.0, rho=750.0)
    dust_air = simple("760", "dust extraction air to C-605", "gas", 20.0, 40.0, 1.0, mw=28.96)
    sheet_package(pkg, AREA, 722, "Area 70  Urea granulation  -  conveying to storage (belt conveyors, bucket elevator)",
        dict(tag="CV-601", name="Urea conveying system", inlets=[(conv_in, "granules (screened, cooled)", "SO")], outlets=[(conv_out, "to urea store", "SO"), (dust_air, "dust extraction air", "PG")], esd=False, spec="A1",
             utilities=[("power", 0.0, "gap", "A"), ("extraction fan", 0.0, "gap", "A")],
             desc=["belt conveyors + bucket elevator", "enclosed, dust extraction", "metal detector, belt scale (A)"],
             interlocks=[("SAHH", "belt misalignment / slip", "-", "trip drive (A)"), ("TAH", "bearing / belt hot spot", "0-150 C", "H 80 C (A)"), ("PDAH", "dust filter dP high", "0-30 mbar", "H (vendor)"), ("SAL", "conveyor stopped", "-", "stops upstream feed (A)")],
             type="solids conveying", op=f"{R['s22']:.1f} t/h granules", design="vendor", size="belt width gap", basis="A", relief="explosion venting on elevator / filter",
             rows=[("Rate", f"{R['s22']:.1f} t/h", "Rev B 22"), ("Bulk density", "750 kg/m3", "A"), ("Dust air", "20 t/h", "A")],
             hazard="dust explosion, moving machinery",
             notes=["Solid flows have no pipe class in the engine; lines are sized by the slurry rule (1.5 m/s) only so the register is populated. The rate is the Rev B stream 22; bulk density 750 kg/m3 is an assumption (A 700-800).",
                    "Bucket elevators, enclosed belts and dust filters are classic dust-explosion locations: explosion vents or suppression, isolation and ignition-source control apply. No standard was fetched, so no vent areas are given (gap).",
                    "Urea store (bulk shed, bagging, loading) is not drawn: out of the area scope."]))
    detectors(pkg.sheets[-1], pkg, "722", what="dust/NH3")
    return pkg


def lint(pkg):
    tags = [r[0] for r in pkg.equip]; dup = {t for t in tags if tags.count(t) > 1}
    assert not dup, f"duplicate equipment tags: {sorted(dup)}"
    bad = [r[0] for r in pkg.relief if not r[5]]; assert not bad, bad
    ids = {k[0] for k in STREAMS}; used = {str(r[4]) for r in pkg.lines}
    assert used <= ids, used - ids
    no_esd = [sh.no for sh in pkg.sheets if not any(v[6] == sh.no and v[0].startswith("XV") for v in pkg.valves)]
    # units without toxic / flammable gas inventory are allowed to have no XV: TG-601 (steam), VAC-601 (vacuum, trace), E-602 (steam / urea solution), C-605 (wet scrubber), CV-601 (solids)
    allowed = {703, 715, 717, 719, 722}
    assert set(no_esd) <= allowed, set(no_esd) - allowed
    return no_esd


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), Area 70 urea synthesis, recovery, concentration, granulation",
              "Rev B balance scaled K=%.4f; capacity per ICRA/PIB (see docs/pid/analogues)" % K)
    build(pkg); pkg.total = len(pkg.sheets); no_esd = lint(pkg)
    write_html(pkg.sheets, "/tmp/area70.html", "Area 70", previews=True)
    if "--registers" in sys.argv: pkg.write_registers(sys.argv[sys.argv.index("--registers") + 1])
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices, lint OK (no-XV sheets by design: {no_esd})")


if __name__ == "__main__":
    main()

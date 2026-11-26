#!/usr/bin/env python3
"""Generate the LNG liquefaction plant P&ID set, Rev B: P&ID, heat and material balance, four scenarios (2 sheets), safety design basis (3 sheets).

Rev B changes vs Rev A (details on sheet 2): NG cooling duties from a CoolProp enthalpy integral; 4-level propane cascade and 3-stage MR loop (Pe 3.5 bar)
with suction volumes and casings; propane:MR power split computed; specific power from the exergy minimum and a second-law efficiency; V-102 resized;
boil-off 0.05 %/day; gas-turbine fuel computed (stream 20); relief schedule, ESD matrix, SIF list, hazard table (sheets 5 to 7).
Thermodynamic constants (class TH) come from python3 thermo_lng.py final2 (CoolProp 8.0 HEOS; script kept in docs/pid/validation/LNG_thermo_revB.py).

Process basis: the default 2.0 mtpa case of the open-source design repo lng-design-opensource
(lng_design.liquefaction.size_liquefaction_train with LiquefactionBasis defaults and include_refrigerant_supply=True;
tank BOG from lng_design.tank_bog.compute_bog and lng_design.bog_compressor.size_bog_compressor).
Those functions need CoolProp, so this generator (standard library only) carries their printed outputs as the dict S below and
recomputes the balance from them. To regenerate S, run in the repo's .venv:
    from lng_design.liquefaction import LiquefactionBasis, size_liquefaction_train
    d = size_liquefaction_train(LiquefactionBasis(include_refrigerant_supply=True))
    g = size_tank_geometry(d.storage_tank.required_volume_m3)
    r = compute_bog(d.end_flash.liquid_composition_mole_frac, 1.1e5, g, fill_fraction=0.9)
    c = size_bog_compressor(r.bog_composition, r.design_bog_kg_s, 1.1e5 - 0.05e5, 5e5)
Tags: S = sourced (file / function named), D = derived (formula shown), A = assumed by this drawing, R = recommended or required by a source.

Usage:  python3 scripts/gen_pid_lng.py docs/pid/LNG_PID_Set_RevB.html [--previews]
Screening aid, not certified design."""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from pidlib import *
import pidlib as _pl


class Sheet(_pl.Sheet):
    def svg(self):
        return super().svg().replace('|  Rev A', '|  Rev B').replace('Draft A.', 'Draft B.')


import textwrap

# =====================================================================================================================
# 1. SOURCED VALUES (S): outputs of the repo functions, default 2.0 mtpa case
# =====================================================================================================================
REPO = "lng-design-opensource"
LQ = "liquefaction.size_liquefaction_train (defaults)"
S = dict(
    capacity_mtpa=2.0,                       # LiquefactionBasis.capacity_mtpa
    m_sweet=63.3761756280579,                # kg/s, LiquefactionDesign.feed_mass_flow_kg_s (= 2.0e9 kg/y / 31,557,600 s)
    feed_T_K=298.15, feed_P_Pa=50e5,         # LiquefactionBasis
    z=dict(CH4=0.85, C2H6=0.08, C3H8=0.04, N2=0.03),   # LiquefactionBasis.feed_composition (mole fractions)
    cond_m3_s=0.015, cond_rho=550.0,         # LiquefactionBasis (the repo calls it an illustrative allowance)
    ngl_kmol_h=dict(C2H6=320.0, C3H8=300.0, iC4=60.0, nC4=100.0, iC5=50.0, nC5=50.0, C6=40.0),  # refrigerant_supply default NGL feed
    co2_in=0.02, co2_out=0.0005, water_ppm_wt=700.0,
    trim_kW=2915.3040788906633, trim_dT=20.0, trim_cp=2.3, trim_fan_kW=49.84471899613493,
    precool_duty=12168.225720587116, precool_cp=2.4,
    lrc_duty=11027.454559282074, sub_duty=10843.663649960707, liq_cp=2.9,
    # C3 precool loop, precool.optimal_evap_temperature
    c3=dict(Te=230.14998852718796, Tc=313.15, Pe=97424.0612914412, Pc=1369420.3848039038, m=55.88478364326216, W=9330.260277438663,
            cop=1.3041678751460863, inlet_m3h=86361.34720249288, frame="E", frame_lo=55000, frame_hi=110000),
    # cascade_loops.three_loop_cascade: PMR (propane) and LRC (mixed refrigerant)
    pmr=dict(Te=233.14999999999998, Tc=313.15, Pe=111121.16425719768, Pc=1369420.3848039038, m=172.80030801383322, W=27389.537056773417,
             cop=1.3963726044657725, duty=38245.99919507848),
    lrc=dict(Te=173.15, Tc=236.15, Pe=9089.772732560374, Pc=5355608.420532413, m=37.610199823526315, W=27218.54463579641,
             Qc=38245.99919507848),
    lrc_blend=dict(N2=0.05, CH4=0.30, C2H6=0.35, C3H8=0.30),
    mr_charge_kmol=8000.0,
    c3_charge_kg=16765.43509297865,
    v102=dict(vol=47.33769908605736, dia_mm=2591, len_m=8.978058632305395),
    v101=dict(dia_mm=2591, ss_m=3.4444691086680614),
    t301=dict(dia_m=3.644108229697854, pack_m=3.311025909728188),
    v201=dict(n=2, dia_mm=3200, h_m=2.003082185110099, regen_kg_s=9.506426344208684, heater_kW=5455.857349525137, water_cycle_kg=1277.6637006616472),
    a101=dict(bays=2, L=12.2, W=4.9),
    mche=dict(area_m2=882.196364742567, tech="coil-wound (spiral-wound)", mita=5.0),
    # end_flash.flash_end_gas(feed composition, 113.15 K, 4.5 bar -> 1.1 bar)
    ef=dict(T_in_K=113.15, P_in=4.5e5, P_out=1.1e5, T=108.43122866767641, mliq=60.44213346003151, mvap=2.934042168026386,
            xliq=dict(CH4=0.859902316825239, C2H6=0.08350636792053026, C3H8=0.04175480130158936, N2=0.014836513952641435),
            yvap=dict(CH4=0.6242824015511591, C2H6=7.436640656604465e-05, C3H8=3.1684099410629054e-07, N2=0.37564291520128085)),
    end_C=-159.0,
    k401=dict(W=322.55323504447625, PR=4.545454545454546, n=1.5664164067183373, P_out=5e5),
    tank=dict(V=63826.892933793286, D=58.787448368689006, Hliq=23.514979347475602, gross=69255.5086251479, inv_kg=27296056.07903986,
              Q_kW=133.73035842070885, bog=0.3862015047132259, bor=0.12224407039097945, rho_l=475.1751151414022, rho_v=2.5932572375211795,
              bog_mw=20.540553102364917, bog_y=dict(CH4=0.6242824014781945, C2H6=7.43664065667658e-05, C3H8=3.1684099413665164e-07, N2=0.3756429152742447),
              fill=0.9),
    k501=dict(design=0.4248216551845485, W_each=66.53314243134231, installed=133.06628486268463, Td=245.87689512698353, stages=2,
              PR=2.1821789023599236, Ts=143.15, inlet_m3h=833.0005711239132),
    supply=dict(charge_kg=dict(C3H8=122594.92309297866, N2=11205.392, CH4=38502.72, C2H6=84193.31199999999),
                makeup_kg_y=dict(C3H8=12259.492309297866, N2=1120.5392, CH4=3850.272, C2H6=8419.331199999999),
                propane=dict(n=4, vol=229.09539498608868, cap_kg=370849.64235626045, dia_mm=4267, len_m=16.020689099459553, T_K=308.15, Pd=1687745.4753401543),
                ethane=dict(n=3, vol=230.79985990164417, cap_kg=254684.76879999996, dia_mm=4267, len_m=16.139882689076266, T_K=258.15, Pd=2957149.271348628),
                cols=(("deethanizer", 51.71, 70.90), ("depropanizer", 74.20, 67.79), ("debutanizer", 52.97, 37.82)), col_dia=0.457, feed_total_kmol_h=20.10),
    repo_total_kW=36871.35814827955,           # LiquefactionDesign.total_compression_power_kW (precool + LRC + flash gas)
    impound_m3=70209.58222717262,            # process_safety/lng.py impoundment_capacity_m3([63826.89]) = 1.10 x
)
# atomic masses (g/mol): C 12.011, H 1.008, N 14.007, O 15.999
AM = dict(C=12.011, H=1.008, N=14.007, O=15.999)
FORM = dict(CH4=dict(C=1, H=4), C2H6=dict(C=2, H=6), C3H8=dict(C=3, H=8), iC4=dict(C=4, H=10), nC4=dict(C=4, H=10),
            iC5=dict(C=5, H=12), nC5=dict(C=5, H=12), C6=dict(C=6, H=14), N2=dict(N=2), CO2=dict(C=1, O=2), H2O=dict(H=2, O=1))
MW = {k: sum(AM[e] * n for e, n in f.items()) for k, f in FORM.items()}
SPECIES = list(FORM)
GROUPS = [("Methane", ("CH4",)), ("Ethane", ("C2H6",)), ("Propane", ("C3H8",)), ("Butanes", ("iC4", "nC4")), ("C5+", ("iC5", "nC5", "C6")),
          ("Nitrogen", ("N2",)), ("CO2", ("CO2",)), ("Water", ("H2O",))]
R_GAS = 8.314462618        # J/mol/K (CODATA 2018 exact value)


# =====================================================================================================================
# 2. BALANCE (computed here, asserted)
# =====================================================================================================================
def comp_mass(frac_mole):
    """mass fractions from mole fractions"""
    tot = sum(frac_mole[k] * MW[k] for k in frac_mole)
    return {k: frac_mole[k] * MW[k] / tot for k in frac_mole}


def scale(d, kg_s):  # mass dict from mass fractions
    return {k: v * kg_s for k, v in d.items()}


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items(): out[k] = out.get(k, 0.0) + v
    return out


def sub(a, b):
    out = dict(a)
    for k, v in b.items(): out[k] = out.get(k, 0.0) - v
    return out


def tot(d): return sum(d.values())


import copy, json as _json
S_A = copy.deepcopy(S)          # Rev A repo outputs, kept for the Rev A to Rev B box
# ---- Rev B frozen CoolProp 8.0 (HEOS) data: command in sheet 2 note; script scripts/ is standard-library only, so these are constants ----
TH = _json.loads(r'''{"h_mr_hot_313": 652.7405050412401, "h_mr_hot_233": 209.9714699970092, "h_mr_cold_230": 575.826606516948, "NG_h": {"313.15": 806.9656472363521, "288.15": 745.1825746658268, "271.15": 701.6195870653722, "253.15": 652.4077698467574, "233.15": 581.4160923125359, "333.15": 855.710267608011, "173.15": 172.50915022472495, "114.15": -19.44084056456494, "298.15": 770.1047266621625}, "Q_levels": [61.78307257052529, 43.56298760045456, 49.21181721861478, 70.9916775342216], "propane": {"Te": [285.15, 268.15, 250.15, 230.15], "Pe": [6.734007066074474, 4.060370303960548, 2.1917606456561183, 0.9742411102150331], "Pc": 13.694203848039038, "hv": [587.7748502700422, 569.3038274975027, 548.628034975944, 524.8857395695405], "hl": [230.5742470456795, 187.58623462939343, 144.2866224935819, 98.3639818598466], "rho_v": [14.567590033102785, 8.910343369624254, 4.966059593856336, 2.329575939364852], "hc": 307.1479995984618, "rho_c": 467.4608653347891, "m_cond": 0.8790190409373756, "mev": [0.17296463671344497, 0.11412360450335966, 0.12170857522728137, 0.16644327341101572], "x": [0.2143718455724031, 0.11261732028981764, 0.10708676083902319, 0.10766775622497525], "stages": [{"level": 4, "P_in": 0.9742411102150331, "P_out": 2.1917606456561183, "m": 0.18652612249768652, "w": 8.83783989786953, "vol_m3_h": 288.2473284707597, "T_in": 230.14999999999975, "T_out": 265.12564051055995}, {"level": 3, "P_in": 2.1917606456561183, "P_out": 4.060370303960548, "m": 0.34520117320088084, "w": 13.402106032243166, "vol_m3_h": 260.2377774273957, "T_in": 258.2888265527524, "T_out": 286.219014508226}, {"level": 2, "P_in": 4.060370303960548, "P_out": 6.734007066074474, "m": 0.5176174701249017, "w": 17.183352671223897, "vol_m3_h": 222.04774464874512, "T_in": 280.2433252975154, "T_out": 304.1654540619013}, {"level": 1, "P_in": 6.734007066074474, "P_out": 13.694203848039038, "m": 0.8790190409373756, "w": 41.25909186727682, "vol_m3_h": 230.76358190415536, "T_in": 296.3640947198021, "T_out": 331.9667275229545}], "W": 80.68239046861342, "Qc": 306.2319453924296, "Q": [61.78307257052529, 43.56298760045456, 49.21181721861478, 70.9916775342216]}, "mr_blend": {"Nitrogen": 0.04, "Methane": 0.32, "Ethane": 0.61, "Propane": 0.03}, "mr_Pe": 3.5, "mr_Pc": 45.0, "mr_stages": [{"P_in": 3.5, "T_in": 230.15, "P_out": 8.19941498900034, "T_out": 285.2549346077985, "w": 87.15067372735182, "q_cool": 0.0, "v": 0.20244363555445266}, {"P_in": 8.19941498900034, "T_in": 285.2549346077985, "P_out": 19.20868747481241, "T_out": 346.72048863492364, "w": 106.05545951066703, "q_cool": 70.07389142040915, "v": 0.10616002275142881}, {"P_in": 19.20868747481241, "T_in": 313.15, "P_out": 44.99999999999999, "T_out": 378.3193767547614, "w": 111.16066548390745, "q_cool": 157.37900877722495, "v": 0.047794090456024466}], "w_ideal_kJ_kg": -464.7892107765409, "w_ideal_kWh_t": -129.1081141045947, "gamma_NG": 1.473739019476703, "Z_NG": 0.8869941886495386, "gamma_C3": 1.3486316106968925, "hfg_C3_14bar": 298.54537238606315, "T_C3_15bar": 317.1431416073476, "rho_C3_liq_40C": 467.4608653347891, "rho_vap_C3_15bar": 33.30593739039669, "MW_C3": 44.095620000000004, "Hfg_J_mol": {"CH4": -74534.0, "C2H6": -83780.0, "C3H8": -104390.0, "CO2": -393474.0, "H2O": -241822.0}, "LHV_MJ_kg": {"CH4": 50.02705229695194, "C2H6": 47.5102760226139, "C3H8": 46.336939020795064}}''')
NGH = {float(k): v for k, v in TH["NG_h"].items()}
LHV = {"CH4": 50.027, "C2H6": 47.510, "C3H8": 46.337}   # MJ/kg net, chemicals.reaction.Hfg (formation enthalpies) with CO2, H2O(g); propane agrees with the toolkit Annex value 46.013 within 0.7 %
RB = dict(eta_II=0.40, c3_share_ref=27.0 / 91.0, bor=0.05, eta_gt=0.33, latent_bog=346.3, v102_res_s=300.0, v102_fill=0.70, v102_LD=3.5,
          lo=S["c3"]["frame_lo"], hi=S["c3"]["frame_hi"])


def lhv_mass(d):  # MJ/kg of a species-mass dict
    t = sum(d.values())
    return sum(d.get(k, 0.0) * LHV.get(k, 0.0) for k in d) / t


def build_balance():
    B = {}
    m = S["m_sweet"]
    assert abs(S["capacity_mtpa"] * 1e9 / (365.25 * 24 * 3600) - m) / m < 1e-9
    wz = comp_mass(S["z"])
    sweet = scale(wz, m)
    n_sweet = sum(sweet[k] / MW[k] for k in sweet)
    n_co2 = S["co2_in"] / (1 - S["co2_in"]) * n_sweet
    co2 = {"CO2": n_co2 * MW["CO2"]}
    water = {"H2O": S["water_ppm_wt"] * 1e-6 * m}
    assert abs(water["H2O"] * 8 * 3600 - S["v201"]["water_cycle_kg"]) / S["v201"]["water_cycle_kg"] < 1e-4
    ngl_n = S["ngl_kmol_h"]
    ngl_w = {k: ngl_n[k] * MW[k] for k in ngl_n}
    cond = scale({k: v / sum(ngl_w.values()) for k, v in ngl_w.items()}, S["cond_m3_s"] * S["cond_rho"])
    ef, T, k4 = S["ef"], S["tank"], S["k401"]
    bog = RB["bor"] / 100.0 * T["inv_kg"] / 86400.0                      # D: boil-off from the sourced rate (0.05 %/day)
    tap = 0.0
    for it in range(500):
        mc = m - tap; sc = mc / m
        st13 = scale(comp_mass(ef["yvap"]), ef["mvap"] * sc); st14 = scale(comp_mass(ef["xliq"]), ef["mliq"] * sc)
        st16 = scale(comp_mass(T["bog_y"]), bog); st19 = sub(st14, st16)
        t_lng = tot(st19) * 3.6                                            # t/h
        W_ref = abs(TH["w_ideal_kWh_t"]) * t_lng / RB["eta_II"]                 # kW, C3 + MR shaft power (D)
        E_fuel = W_ref / RB["eta_gt"]                                      # kW LHV into gas turbines
        E_have = (tot(st13) * lhv_mass(st13) + tot(st16) * lhv_mass(st16)) * 1000.0
        tn = max(0.0, (E_fuel - E_have) / (lhv_mass(sweet) * 1000.0))
        if abs(tn - tap) < 1e-13: break
        tap = tn
    mc = m - tap; sc = mc / m
    st = {}
    st[1] = add(sweet, co2, water, cond); st[2] = cond; st[3] = add(sweet, co2, water); st[4] = co2; st[5] = add(sweet, water); st[6] = water
    cold = scale(wz, mc)
    st[7] = dict(sweet); st[8] = dict(sweet); st[20] = scale(wz, tap)
    for i in (9, 10, 11, 12): st[i] = dict(cold)
    assert abs(ef["mliq"] * sc + ef["mvap"] * sc - mc) / mc < 1e-9
    st[13] = st13; st[14] = st14
    B["species_err"] = {}
    for k in S["z"]:
        e = abs(st[13].get(k, 0) + st[14].get(k, 0) - cold[k]) / cold[k]
        assert e < 1e-3, (k, e); B["species_err"][k] = e
    st[15] = dict(st13); st[16] = st16; st[17] = dict(st16)
    st[18] = add(st[15], st[17], st[20]); st[19] = st19
    assert min(st[19].values()) > 0
    B["st"] = st; B["tap"] = tap; B["mc"] = mc; B["sc"] = sc; B["iter"] = it
    m_in = tot(st[1]); m_out = tot(st[2]) + tot(st[4]) + tot(st[6]) + tot(st[18]) + tot(st[19])
    B["m_in"], B["m_out"] = m_in * 3600, m_out * 3600
    B["err_pct"] = abs(m_in - m_out) / m_in * 100
    assert B["err_pct"] < 0.1
    def el(d):
        r = {e: 0.0 for e in AM}
        for k, v in d.items():
            for e, nn in FORM[k].items(): r[e] += v / MW[k] * nn * AM[e]
        return r
    ein = el(st[1]); eout = add(el(st[2]), el(st[4]), el(st[6]), el(st[18]), el(st[19]))
    B["el_err"] = {e: (abs(ein[e] - eout[e]) / ein[e] * 100 if ein[e] else 0.0) for e in AM}
    assert max(B["el_err"].values()) < 0.1
    B["T15"] = ef["T"] * k4["PR"] ** ((k4["n"] - 1) / k4["n"])
    B["lng_ship_mtpa"] = tot(st[19]) * 365.25 * 24 * 3600 / 1e9
    B["t_lng_h"] = t_lng
    # ---- NG-side duties: enthalpy integrals at 50 bar (CoolProp), not constant cp
    h = NGH
    D = {}
    D["A101"] = m * (h[333.15] - h[313.15]); D["pre"] = mc * (h[313.15] - h[233.15]); D["lrc"] = mc * (h[233.15] - h[173.15]); D["sub"] = mc * (h[173.15] - h[114.15])
    D["mche"] = D["lrc"] + D["sub"]; D["ng_total"] = D["pre"] + D["mche"]
    D["lrc_ref"] = S["m_sweet"] * (h[233.15] - h[173.15]); D["sub_ref"] = S["m_sweet"] * (h[173.15] - h[114.15])
    assert abs(D["lrc_ref"] - 25915.0) / 25915.0 < 0.003 and abs(D["sub_ref"] - 12165.0) / 12165.0 < 0.003   # matches the validator's independent CoolProp run
    B["D"] = D
    # ---- loops: propane 4-level cascade (frozen per kg NG) + MR 3 stages (frozen per kg MR)
    pc = TH["propane"]; Qsum = sum(TH["Q_levels"]); assert abs(Qsum - (h[313.15] - h[233.15])) < 1e-6
    u_w = pc["W"] / Qsum                                                  # kW shaft per kW evaporator, 4-level cascade
    mrs = TH["mr_stages"]; wmr = sum(x["w"] for x in mrs); Hpre = TH["h_mr_hot_313"] - TH["h_mr_hot_233"]
    W_tot = W_ref
    W_MR = (W_tot - u_w * D["pre"]) / (1 + u_w * Hpre / wmr)               # D: W_tot = W_C3 + W_MR, propane also pre-cools the MR
    m_MR = W_MR / wmr
    Q_MRpre = m_MR * Hpre
    Qe = D["pre"] + Q_MRpre; k = Qe / (mc * Qsum)
    W_C3 = u_w * Qe
    assert abs(W_C3 + W_MR - W_tot) < 1e-6 * W_tot, (W_C3, W_MR, W_tot, u_w, Hpre, wmr, D['pre'], tap, it)
    stg = []
    for x in pc["stages"]:
        stg.append(dict(level=x["level"], P_in=x["P_in"], P_out=x["P_out"], m=x["m"] * k * mc, W=x["w"] * k * mc, vol=x["vol_m3_h"] * k * mc))
    assert abs(sum(x["W"] for x in stg) - W_C3) < 1e-6 * W_C3
    for x in stg: x["casings"] = math.ceil(x["vol"] / RB["hi"])
    mrst = [dict(P_in=x["P_in"], P_out=x["P_out"], T_in=x["T_in"], W=x["w"] * m_MR, vol=x["v"] * m_MR * 3600, Qc=x["q_cool"] * m_MR) for x in mrs]
    for x in mrst: x["casings"] = math.ceil(x["vol"] / RB["hi"])
    Qcool = sum(x["Qc"] for x in mrst)
    Q_del = Qcool + Q_MRpre - W_MR
    assert abs(Q_del - m_MR * (TH["h_mr_cold_230"] - TH["h_mr_hot_233"])) < 1e-3 * Q_del   # MR loop energy balance vs the CoolProp enthalpy difference
    B.update(W_tot=W_tot, W_C3=W_C3, W_MR=W_MR, m_MR=m_MR, Q_MRpre=Q_MRpre, Qe=Qe, kscale=k, u_w=u_w, stg=stg, mrst=mrst, Qcool=Qcool, Q_del=Q_del,
             Q_A201=Qe + W_C3, m_cond=pc["m_cond"] * k * mc, c3_share=W_C3 / W_tot, mr_over_c3=W_MR / W_C3,
             W_K201=sum(x["W"] for x in stg if x["level"] in (4, 3)), W_K202=sum(x["W"] for x in stg if x["level"] in (2, 1)))
    B["del_ratio"] = Q_del / D["mche"]
    B["unalloc"] = Q_del - D["mche"]
    B["heat_in"] = D["pre"] + D["mche"] + W_C3 + W_MR + B["unalloc"]       # NG sensible 313 to 114 K + shaft + unallocated MR effect
    B["heat_out"] = B["Q_A201"] + Qcool
    B["heat_err"] = abs(B["heat_in"] - B["heat_out"]) / B["heat_out"] * 100
    assert B["heat_err"] < 0.1, B["heat_err"]
    # K-401, K-501, tank
    B["W_k401"] = k4["W"] * sc
    k5 = S["k501"]; des = 1.1 * bog; f5 = des / k5["design"]
    B["k501"] = dict(design=des, W_each=k5["W_each"] * f5, inlet_m3h=k5["inlet_m3h"] * f5)
    B["Q_in"] = bog * RB["latent_bog"]
    B["W_all"] = W_tot + B["W_k401"] + B["k501"]["W_each"]
    B["kWh_t"] = W_tot / (tot(st[19]) * 3.6); B["kWh_t_all"] = B["W_all"] / (tot(st[19]) * 3.6)
    B["fuel_kW"] = W_tot / RB["eta_gt"]; B["fuel_pct"] = tap / m * 100
    # V-102
    V = B["m_cond"] / TH["propane"]["rho_c"] * RB["v102_res_s"] / RB["v102_fill"]
    Dm = (4 * V / (math.pi * RB["v102_LD"])) ** (1 / 3)
    B["v102"] = dict(vol=V, dia_mm=Dm * 1000, len_m=Dm * RB["v102_LD"], res_old=S["v102"]["vol"] * RB["v102_fill"] * TH["propane"]["rho_c"] / (S["pmr"]["m"] + S["c3"]["m"]))
    B["v102_charge"] = V * RB["v102_fill"] * TH["propane"]["rho_c"]
    B["bog"] = bog; B["bog_t_d"] = bog * 86.4
    vap_vol = T["gross"] - T["V"] * T["fill"]; B["vap_vol"] = vap_vol
    B["dPdt_Pa_s"] = (bog / (T["bog_mw"] / 1000.0)) * R_GAS * ef["T"] / vap_vol
    B["lrc_charge_kg"] = S["mr_charge_kmol"] * sum(S["lrc_blend"][kk] * MW[kk] for kk in S["lrc_blend"])
    B["ref_charge_total_kg"] = sum(S["supply"]["charge_kg"].values())
    B["pmr_hold_kg"] = B["m_cond"] * RB["v102_res_s"]
    B["imp_check"] = 1.10 * T["V"]; assert abs(B["imp_check"] - S["impound_m3"]) < 1e-6
    B["Pc_C3"] = pc["Pc"] * 1e5
    return B


BAL = build_balance()
# Rev B values override the Rev A repo values wherever the scenario sheets read S (S_A keeps Rev A)
S["tank"] = dict(S["tank"], Q_kW=BAL["Q_in"], bog=BAL["bog"], bor=RB["bor"])
S["k501"] = dict(S["k501"], **BAL["k501"])
S["v102"] = dict(S["v102"], vol=BAL["v102"]["vol"], dia_mm=BAL["v102"]["dia_mm"], len_m=BAL["v102"]["len_m"])
S["c3_charge_kg"] = BAL["v102_charge"]
S["c3"] = dict(S["c3"], m=BAL["stg"][1]["m"], W=BAL["W_K201"], Pc=BAL["Pc_C3"])
S["pmr"] = dict(S["pmr"], m=BAL["stg"][3]["m"], W=BAL["W_K202"])
S["lrc"] = dict(S["lrc"], W=BAL["W_MR"], Pc=TH["mr_Pc"] * 1e5, Pe=TH["mr_Pe"] * 1e5)
STRM = {
    1: ("Raw feed gas + condensate", "G+L", 25.0, 50.0), 2: ("Condensate to NGL stabiliser", "L", 25.0, 50.0),
    3: ("Sour gas to T-301", "G", 25.0, 50.0), 4: ("CO2 acid gas (regen. overhead)", "G", None, None),
    5: ("Sweet wet gas to V-201", "G", 25.0, 50.0), 6: ("Water removed (regen.)", "L", None, None),
    7: ("Dry gas to A-101", "G", 60.0, 50.0), 8: ("Gas to E-201 and fuel tap", "G", 40.0, 50.0), 9: ("Gas to E-301 (precooled)", "G", -40.0, 50.0),
    10: ("Gas after warm section", "G*", -100.0, 50.0), 11: ("Subcooled LNG, MCHE outlet", "L", -159.0, 50.0),
    12: ("LNG to V-401 (after let-down)", "L", 113.15 - 273.15, 4.5), 13: ("Flash gas from V-401", "G", S["ef"]["T"] - 273.15, 1.1),
    14: ("LNG to TK-501", "L", S["ef"]["T"] - 273.15, 1.1), 15: ("Flash gas after K-401", "G", BAL["T15"] - 273.15, 5.0),
    16: ("BOG to K-501 (suction)", "G", S["k501"]["Ts"] - 273.15, 1.05),
    17: ("BOG after K-501", "G", S["k501"]["Td"] - 273.15, 5.0), 18: ("Fuel gas header (15 + 17 + 20)", "G", None, 5.0),
    19: ("LNG to loading (14 - 16)", "L", S["ef"]["T"] - 273.15, 1.1), 20: ("Fuel tap from stream 8 (to header)", "G", 40.0, 5.0),
}


def f0(x): return f"{x:,.0f}"
def f1(x): return f"{x:,.1f}"
def f2(x): return f"{x:,.2f}"


def wtable(s, x, y, colw, rows, size=10, lh=12.0, pad=4, head=True, charw=0.54, zebra=True, heads_fill="#e8eaf0"):
    """table with wrapped cells; returns y below"""
    yy = y
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), max(1, int((w - 2 * pad) / (charw * size)))) or [""] for c, w in zip(r, colw)]
        h = max(len(c) for c in cells) * lh + 2 * pad - 2
        if head and i == 0: R(s, x, yy, sum(colw), h, heads_fill, "none")
        elif zebra and i % 2 == 0: R(s, x, yy, sum(colw), h, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, t in enumerate(c):
                T(s, cx + pad, yy + pad + 9 + k * lh, t, size, 700 if (head and i == 0) else 400)
            cx += colw[j]
        yy += h
    R(s, x, y, sum(colw), yy - y, "none", "#9aa", 1)
    return yy


if __name__ == "__main__" and "--check" in sys.argv:  # prints the closure numbers only
    B = BAL
    print("closure kg/h", f0(B["m_in"]), f0(B["m_out"]), f"{B['err_pct']:.4f} %", B["el_err"], "heat", f"{B['heat_err']:.5f}")
    for kk in ("tap", "mc", "t_lng_h", "W_tot", "W_C3", "W_MR", "m_MR", "Qe", "kWh_t", "kWh_t_all", "fuel_kW", "fuel_pct", "c3_share", "mr_over_c3", "Q_del", "del_ratio", "Q_A201", "Qcool", "bog", "Q_in", "lng_ship_mtpa"): print(kk, B[kk])
    print(B["D"]); print(B["v102"]); print([ (x["level"], round(x["vol"]), x["casings"]) for x in B["stg"]], [(round(x["vol"]), x["casings"]) for x in B["mrst"]])
    sys.exit()

# =====================================================================================================================
# 3. DRAWING HELPERS
# =====================================================================================================================
FLARE_C = "#8d4b00"


def tg(s, x, y, t, size=10, anchor="start", weight=400, fill=INK): T(s, x, y, t, size, weight, anchor, fill)


def inlabel(s, cx, cy, t, size=10):
    w = len(t) * size * 0.58 + 4
    R(s, cx - w / 2, cy - size + 1, w, size + 3, "#fff", "none", 1, op=0.9)
    T(s, cx, cy, t, size, 700, "middle")


def conn(s, x, y, t, color=INK):
    s.add(f'<circle cx="{x}" cy="{y}" r="10" fill="#fff" stroke="{color}" stroke-width="1.5"/>')
    T(s, x, y + 3.5, t, 9.5, 700, "middle", color)


def compressor_l(s, cx, cy, r=15, label=None):
    """compressor drawn mirrored: inlet right, outlet left"""
    s.add(f'<g transform="translate({2*cx},0) scale(-1,1)">')
    compressor(s, cx, cy, r)
    s.add('</g>')
    if label: T(s, cx, cy + r + 13, label, 10, 700, "middle")
    return dict(inlet=(cx + r, cy), outlet=(cx - r, cy))


def sig(s, pts): PL(s, pts, 1.3, BLUE, "5 4", "ahb")
def esd(s, pts): PL(s, pts, 1.5, RED, "6 4", "ahr")
def rel(s, pts, arrow_=True):
    PL(s, pts, 2.2, FLARE_C, "9 3 2 3")


def off(s, dx, dy, fn, *a):
    s.add(f'<g transform="translate({dx},{dy})">')
    fn(s, *a)
    s.add('</g>')


def frame_area(s): R(s, 20, 84, 1100, 686, "none", "#889", 1)


def cloud(s, cx, cy, rx, ry, label=None, fill="#b3d4ff", stroke=BLUE, op=0.45):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="2" stroke-dasharray="8 5" opacity="{op}"/>')
    if label: T(s, cx, cy + 4, label, 11, 700, "middle", stroke)


def pool(s, cx, cy, rx, ry, fill="#9ecbff", label=None):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{BLUE}" stroke-width="1.6" opacity=".8"/>')
    if label: T(s, cx, cy + 4, label, 10, 700, "middle", BLUE)


# =====================================================================================================================
# 4. ZONES (sheet-1 coordinates; scenario sheets translate them)
# =====================================================================================================================


def psvc(s, nx, ny, d, tag, dest, tagpos=None):
    """compact PSV: nozzle (nx,ny), direction d (u/d/l/r) away from the vessel, outlet line to a flare/vent connector"""
    ux, uy = {"u": (0, -1), "d": (0, 1), "l": (-1, 0), "r": (1, 0)}[d]; px, py = -uy, ux
    P = lambda t, w=0: (round(nx + ux * t + px * w, 1), round(ny + uy * t + py * w, 1))
    PL(s, [P(0), P(4)], 2.0)
    pts = [P(4, -6), P(22, 6), P(22, -6), P(4, 6)]
    s.add(f'<polygon points="{" ".join(f"{a},{b}" for a, b in pts)}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    PL(s, [P(13, 0), P(13, 3), P(10, 5), P(16, 7), P(10, 9), P(13, 11)], 1.2)
    PL(s, [P(22), P(32)], 2.2, FLARE_C, "9 3 2 3")
    cx, cy = P(42)
    s.add(f'<circle cx="{cx}" cy="{cy}" r="10" fill="#fff" stroke="{FLARE_C}" stroke-width="1.5"/>')
    T(s, cx, cy + 3.5, dest, 9, 700, "middle", FLARE_C)
    if tagpos is None:
        tagpos = {"u": (nx + 9, ny - 30, "start"), "d": (nx + 9, ny + 32, "start"), "l": (nx - 4, ny - 10, "end"), "r": (nx + 4, ny - 10, "start")}[d]
    T(s, tagpos[0], tagpos[1], tag, 9.5, 700, tagpos[2])


def zone_pre(s):
    # feed and V-101
    tg(s, 24, 126, "FEED GAS", 9.5, "start", 700); tg(s, 24, 138, "L-101 (A)", 9.5)
    pipe(s, [(24, 170), (74, 170)]); strm(s, 30, 187, 1); valve(s, 52, 170, 0, "gate", act=True); tg(s, 44, 207, "XV-101", 9.5, "middle", 700)
    vvessel(s, 100, 120, 52, 100)
    inlabel(s, 100, 175, "V-101")
    psvc(s, 126, 118, "r", "PSV-101", "F1", (131, 108, "start")); bubble(s, 146, 215, "LSHH", "101", True, r=13); PL(s, [(126, 215), (133, 215)], 1.2, BLUE, "4 3")
    bubble(s, 150, 272, "AT", "101", True, r=13)
    pipe(s, [(126, 140), (162, 140), (162, 235), (189, 235)]); strm(s, 162, 190, 3)
    PL(s, [(74, 217), (60, 222)], 1.4); bubble(s, 45, 226, "LIC", "101", True)
    pipe(s, [(100, 234.6), (100, 296)]); valve(s, 100, 250, 90, "gate", act=True); strm(s, 100, 276, 2)
    sig(s, [(45, 241), (45, 250), (84, 250)])
    tg(s, 122, 254, "LV-101", 9.5, "start", 700)
    # T-301 amine absorber
    vvessel(s, 215, 115, 52, 140, packing=True)
    inlabel(s, 215, 190, "T-301")
    psvc(s, 241, 172, "r", "PSV-301", "F1", (246, 164, "start"))
    PL(s, [(215, 100.4), (215, 100)]); PL(s, [(215, 100), (395, 100)], 2.6); strm(s, 270, 100, 5)
    pipe(s, [(308, 130), (241, 130)]); tg(s, 246, 124, "lean amine in", 9.5)
    PL(s, [(308, 323), (308, 130)], 2.0, GREY)
    pipe(s, [(241, 245), (262, 245), (262, 300)], 2.0, GREY)
    R(s, 170, 300, 130, 46, "#fff", GREY, 1.3, "5 3")
    tg(s, 176, 316, "AGRU REGENERATION", 9.5, "start", 700); tg(s, 176, 329, "(stub, loop not sized, A)", 9.5)
    PL(s, [(300, 323), (308, 323)], 2.0, GREY)
    pipe(s, [(235, 346), (235, 384)]); strm(s, 235, 364, 4); tg(s, 250, 368, "acid gas CO2 out", 9.5)
    # V-201 A/B
    for cx, t in ((345, "V-201A"), (395, "V-201B")):
        vvessel(s, cx, 125, 44, 90)
        inlabel(s, cx, 175, t, 9.5)
        pipe(s, [(cx, 100), (cx, 112.7)]); PL(s, [(cx, 227.3), (cx, 250)])
    psvc(s, 352, 252, "d", "PSV-211A", "F1", (352, 334, "middle")); psvc(s, 400, 252, "d", "PSV-211B", "F1", (402, 346, "middle"))
    PL(s, [(345, 250), (440, 250)], 2.6); arrow(s, 440, 250, "r"); strm(s, 418, 250, 7)
    R(s, 430, 120, 112, 62, "#fff", GREY, 1.3, "5 3")
    tg(s, 436, 135, "REGEN. GAS CIRCUIT", 9.5, "start", 700); tg(s, 436, 148, "H-201 5,456 kW (S)", 9.5); tg(s, 436, 161, "9.5 kg/s (S), stub", 9.5); tg(s, 436, 174, "not in HMB (A)", 9.5)
    PL(s, [(430, 170), (417, 170)], 1.6, GREY, "5 3")
    # A-101
    hx(s, 480, 250, 80, 28, "A-101")
    tg(s, 480, 280, "air cooler", 9.5, "middle")
    pipe(s, [(520, 250), (565, 250)], arrow_=False); strm(s, 542, 250, 8)
    # fuel tap (stream 20) from stream 8 to the fuel header; water out (stream 6)
    pipe(s, [(558, 250), (558, 188)]); valve(s, 558, 234, 90, "gate", act=True); tg(s, 546, 222, "PCV-701", 9.5, "end", 700); strm(s, 558, 210, 20); conn(s, 558, 178, "FG")
    pipe(s, [(490, 182), (490, 218)]); strm(s, 490, 200, 6); tg(s, 478, 204, "water out (A)", 9.5, "end")


def zone_liq(s):
    """E-201, E-301 (MCHE), expansion, V-401, K-401, fuel gas header top, LNG line to y=340"""
    hx(s, 610, 250, 90, 28, "E-201"); psvc(s, 640, 237, "u", "PSV-202", "F1", (648, 205, "start"))
    pipe(s, [(655, 250), (715, 250), (715, 335), (758, 335)]); strm(s, 685, 250, 9)
    # MCHE
    vvessel(s, 790, 130, 64, 220)
    PL(s, [(760, 240), (820, 240)], 1.3, "#555", "6 4")
    tg(s, 790, 190, "SUBCOOL", 9.5, "middle", 700); tg(s, 790, 203, "section", 9.5, "middle")
    tg(s, 790, 292, "LRC", 9.5, "middle", 700); tg(s, 790, 305, "section", 9.5, "middle")
    inlabel(s, 790, 225, "E-301", 11)
    psvc(s, 822, 178, "r", "PSV-303", "F2", (826, 170, "start")); bubble(s, 722, 150, "AT", "401", True, r=14); tg(s, 722, 176, "gas det. (A)", 9.5, "middle")
    PL(s, [(758, 240), (732, 240)], 1.2); strm(s, 722, 240, 10)
    # NG out, expansion
    PL(s, [(822, 148), (860, 148)], 2.6); strm(s, 842, 148, 11)
    valve(s, 872, 148, 0, "gate", act=True); tg(s, 872, 114, "FCV-401", 9.5, "middle", 700); tg(s, 872, 103, "JT/expander (A)", 9.5, "middle")
    pipe(s, [(884, 148), (920, 148)]); strm(s, 902, 148, 12)
    # MR to shell in
    pipe(s, [(846, 222), (822, 222)]); conn(s, 856, 222, "M1")
    # V-401
    vvessel(s, 950, 125, 60, 100)
    inlabel(s, 950, 178, "V-401")
    pipe(s, [(980, 138), (1016, 138)]); strm(s, 997, 138, 13)
    compressor(s, 1030, 138, 14); tg(s, 1030, 162, "K-401", 10, "middle", 700)
    pipe(s, [(1044, 138), (1095, 138)], arrow_=False); strm(s, 1066, 138, 15)
    PL(s, [(920, 195), (906, 195)], 1.4); bubble(s, 891, 195, "LIC", "401", True)
    pipe(s, [(950, 241.8), (950, 340)]); valve(s, 950, 275, 90, "gate", act=True)
    sig(s, [(891, 210), (891, 275), (936, 275)])
    tg(s, 970, 272, "LV-401", 9.5, "start", 700); strm(s, 950, 315, 14)
    # SRC stub
    R(s, 832, 255, 88, 52, "#fff", GREY, 1.3, "5 3")
    tg(s, 838, 270, "SUBCOOL DUTY", 9.5, "start", 700); tg(s, 838, 283, "in MR loop K-301", 9.5); tg(s, 838, 296, "(Rev B, sheet 2)", 9.5)
    PL(s, [(832, 280), (822, 280)], 1.6, GREY, "5 3")
    # fuel gas header
    PL(s, [(1095, 138), (1095, 740)], 3.2); arrow(s, 1095, 740, "d")
    tg(s, 1090, 112, "FUEL GAS 5 bar(a) (A)", 9.5, "end", 700); strm(s, 1095, 260, 18); conn(s, 1066, 190, "FG"); PL(s, [(1076, 190), (1095, 190)], 2.2)
    tg(s, 1090, 760, "to GT drivers", 9.5, "end"); tg(s, 1090, 770, "(A, not sized)", 9.5, "end")
    # PSV on V-401 -> flare
    psvc(s, 980, 196, "r", "PSV-401", "F2", (985, 188, "start")); bubble(s, 1004, 230, "LSLL", "401", True, r=13); PL(s, [(980, 230), (991, 230)], 1.2, BLUE, "4 3")


def zone_refrig(s):
    # ---- C3 propane system
    pipe(s, [(632, 264), (632, 345), (494, 345)]); strm(s, 560, 345, 21)
    compressor_l(s, 480, 345, 15); tg(s, 480, 370, "K-201", 10, "middle", 700)
    pipe(s, [(620, 526), (620, 405), (494, 405)]); strm(s, 620, 465, 22)
    compressor_l(s, 480, 405, 15); tg(s, 480, 430, "K-202", 10, "middle", 700)
    PL(s, [(465, 345), (440, 345), (440, 470)], 2.6); PL(s, [(465, 405), (440, 405)], 2.6)
    pipe(s, [(440, 470), (406, 470)])
    hx(s, 360, 470, 90, 28, "A-201"); psvc(s, 378, 456, "u", "PSV-203", "F1", (386, 428, "start"))
    pipe(s, [(315, 470), (282, 470)])
    hvessel(s, 240, 470, 60, 34, "V-102")
    pipe(s, [(240, 487), (240, 520), (330, 520)]); valve(s, 240, 503, 90, "gate", act=True); tg(s, 228, 508, "XV-201", 9.5, "end", 700)
    conn(s, 344, 520, "L1"); tg(s, 336, 508, "C3 liquid to E-201, E-202", 9.5)
    # E-201 liquid in
    pipe(s, [(588, 264), (588, 308)]); valve(s, 588, 285, 90, "gate", act=True)
    conn(s, 588, 318, "L1")
    PL(s, [(566, 296), (574, 290)], 1.3, BLUE, "5 4"); bubble(s, 548, 300, "LIC", "201", True)
    sig(s, [(563, 297), (573, 288)])
    # PSV on V-102
    PL(s, [(255, 453), (255, 440)]); psv(s, 255, 424); PL(s, [(273, 424), (300, 424)], 2.2, FLARE_C, "9 3 2 3"); conn(s, 311, 424, "F1", FLARE_C)
    tg(s, 300, 410, "PSV-201", 9.5, "start", 700)
    # ---- E-202 and LRC loop
    hx(s, 600, 540, 90, 28, "E-202"); tg(s, 655, 632, "MR precooler (propane)", 9.5, "start"); psvc(s, 640, 555, "d", "PSV-304", "F1", (648, 590, "start"))
    pipe(s, [(572, 554), (572, 604)]); valve(s, 572, 578, 90, "gate", act=True); conn(s, 572, 614, "L1")
    compressor_l(s, 770, 540, 17); tg(s, 770, 570, "K-301A/B/C", 10, "middle", 700)
    pipe(s, [(790, 368), (790, 540), (787, 540)]); strm(s, 790, 450, 23)
    PL(s, [(753, 540), (735, 540)], 2.6); hx(s, 705, 540, 60, 22, "A-301"); PL(s, [(675, 540), (645, 540)], 2.6); arrow(s, 645, 540, "l"); psvc(s, 680, 529, "u", "PSV-305", "F1", (688, 502, "start"))
    pipe(s, [(555, 540), (526, 540)])
    hvessel(s, 480, 540, 70, 34, "V-301"); psvc(s, 442, 540, "l", "PSV-302", "F2", (440, 526, "end"))
    pipe(s, [(480, 557), (480, 612)]); valve(s, 480, 584, 90, "gate", act=True); tg(s, 468, 588, "FCV-301", 9.5, "end", 700)
    conn(s, 480, 622, "M1"); tg(s, 495, 642, "MR to E-301 shell", 9.5)
    tg(s, 775, 520, "MR", 9.5, "middle", 700)
    # BDV on K-301 discharge to flare
    PL(s, [(745, 540), (745, 490)], 1.6); valve(s, 745, 515, 90, "gate", act=True)
    PL(s, [(745, 490), (745, 482)], 2.2, FLARE_C, "9 3 2 3"); conn(s, 745, 471, "F1", FLARE_C); tg(s, 733, 474, "BDV-301", 9.5, "end", 700)
    # ESD / F&G (signal lines are drawn on the scenario sheets; here each device carries its destination)
    R(s, 290, 660, 150, 44, "#fff3e0", RED, 1.6)
    tg(s, 365, 677, "ESD-301", 11, "middle", 700, RED); tg(s, 365, 691, "train ESD + F&G (A)", 9.5, "middle", 400, RED)
    bubble(s, 545, 452, "AT", "301A", True); bubble(s, 410, 385, "AT", "201", True, r=14); bubble(s, 655, 508, "PT", "301", True, r=13); bubble(s, 558, 490, "BE", "301", True); bubble(s, 700, 600, "AT", "301B", True)
    tg(s, 527, 450, "gas det. (A)", 9.5, "end"); tg(s, 540, 490, "flame det. (A)", 9.5, "end"); tg(s, 718, 598, "gas det. (A)", 9.5, "start")
    tg(s, 545, 431, "to ESD-301", 9.5, "middle", 400, BLUE); tg(s, 558, 512, "to ESD-301", 9.5, "middle", 400, BLUE); tg(s, 718, 610, "to ESD-301", 9.5, "start", 400, BLUE)
    tg(s, 228, 519, "ESD", 9.5, "end", 700, RED)
    # deluge valves on the fire-water ring main
    PL(s, [(470, 722), (640, 722)], 3, BLUE); tg(s, 470, 740, "fire-water ring main (A)", 9.5, "start", 400, BLUE)
    for xx, tt in ((520, "DLG-301"), (600, "DLG-302")):
        PL(s, [(xx, 722), (xx, 700)], 2, BLUE); valve(s, xx, 690, 90, "gate", act=True, color=BLUE); tg(s, xx + 22, 694, tt, 9.5, "start", 700, BLUE)


def zone_refstore(s):
    tg(s, 30, 358, "REFRIG. STORAGE", 10, "start", 700)
    hvessel(s, 95, 430, 80, 30, "ST-701"); tg(s, 95, 468, "propane 4x229 m3 (S)", 9.5, "middle")
    psvc(s, 124, 415, "u", "PSV-701", "F1", (134, 392, "start"))
    pipe(s, [(144, 430), (170, 430), (170, 470), (199, 470)]); tg(s, 178, 466, "make-up", 9.5)
    valve(s, 160, 430, 0, "gate", act=True); tg(s, 172, 418, "XV-701", 9.5, "middle", 700)
    hvessel(s, 95, 545, 80, 30, "ST-702"); tg(s, 95, 583, "ethane 3x231 m3, -15 C (S)", 9.5, "middle")
    psvc(s, 124, 530, "u", "PSV-702", "F1", (134, 507, "start"))
    pipe(s, [(144, 545), (170, 545), (170, 593)]); conn(s, 170, 605, "E1")
    valve(s, 160, 545, 0, "gate", act=True); tg(s, 172, 533, "XV-702", 9.5, "middle", 700); tg(s, 186, 609, "ethane to MR make-up", 9.5)
    bubble(s, 40, 505, "AT", "701", True, r=13)
    R(s, 30, 296, 120, 48, "#fff", GREY, 1.3, "5 3")
    tg(s, 36, 311, "NGL-801 stabiliser", 9.5, "start", 700); tg(s, 36, 324, "deC2/deC3/deC4 (S)", 9.5); tg(s, 36, 337, "makes refrigerants", 9.5)


def zone_store(s, jetty_stub=True):
    # LNG line from V-401 (strm 14)
    pipe(s, [(950, 340), (950, 470)])
    tg(s, 958, 360, "L-114 (A)", 9.5, "start", 700)
    valve(s, 950, 395, 90, "gate", act=True); tg(s, 938, 412, "XV-503", 9.5, "end", 700)
    # tank
    tank(s, 950, 610, 190, 120, roof="dome", level=0.8)
    inlabel(s, 950, 540, "TK-501 LNG TANK", 11)
    # impoundment
    PL(s, [(832, 470), (832, 664), (1068, 664), (1068, 470)], 3, "#8d6e63", "12 5")
    tg(s, 840, 682, "IMPOUNDMENT 70,210 m3 (R)", 10, "start", 700, "#6d4c41")
    # in-tank pump column and loading line
    PL(s, [(865, 480), (865, 592)], 2.2); s.add(f'<circle cx="865" cy="598" r="9" fill="#fff" stroke="{INK}" stroke-width="1.8"/>')
    tg(s, 879, 602, "P-501A/B", 9.5, "start", 700)
    pipe(s, [(865, 480), (865, 395), (820, 395), (820, 700)], arrow_=False)
    valve(s, 865, 430, 90, "gate", act=True); tg(s, 860, 419, "XV-501", 9.5, "end", 700)
    valve(s, 820, 560, -90, "gate", act=True); tg(s, 812, 590, "XV-502", 9.5, "end", 700)
    if jetty_stub:
        pipe(s, [(820, 700), (820, 740), (700, 740)]); valve(s, 760, 740, 0, "gate", act=True); tg(s, 760, 766, "XV-504", 9.5, "middle", 700); tg(s, 696, 735, "L-501 LNG to jetty / loading", 9.5, "end", 700); tg(s, 696, 747, "arms (A, not sized)", 9.5, "end")
    strm(s, 820, 510, 19)
    # BOG
    PL(s, [(996, 474), (996, 370)], 2.6)
    pipe(s, [(996, 370), (1013, 370)], arrow_=False); pipe(s, [(996, 410), (1013, 410)], arrow_=False)
    compressor(s, 1028, 370, 15); compressor(s, 1028, 410, 15)
    tg(s, 1046, 386, "K-501A", 9.5, "start", 700); tg(s, 1046, 426, "K-501B", 9.5, "start", 700)
    PL(s, [(1043, 370), (1095, 370)], 2.6); PL(s, [(1043, 410), (1095, 410)], 2.6)
    valve(s, 1060, 370, 0, "check"); valve(s, 1060, 410, 0, "check")
    strm(s, 996, 445, 16); strm(s, 1082, 370, 17)
    # relief
    PL(s, [(1018, 484), (1018, 474)], 2.0); PL(s, [(1038, 489), (1038, 474)], 2.0)
    for xx, tt, ty in ((1018, "PSV-501A", 446), (1038, "PSV-501B", 432)):
        s.add(f'<polygon points="{xx-6},474 {xx+6},458 {xx+6},474 {xx-6},458" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
        PL(s, [(xx, 458), (xx, 452)], 2.2, FLARE_C, "9 3 2 3"); T(s, 1068, 443, "PSV-501A/B", 9.5, 700, "end") if xx == 1018 else None
    PL(s, [(1018, 452), (1075, 452), (1075, 745)], 2.2, FLARE_C, "9 3 2 3")
    bubble(s, 1010, 575, "TT", "501", True, r=13)
    # flare
    PL(s, [(1075, 745), (1010, 745)], 2.2, FLARE_C, "9 3 2 3")
    flare(s, 1010, 770, 55, "FL-601"); tg(s, 996, 765, "KOD (A)", 9.5, "end")
    # instruments
    PL(s, [(932, 480), (932, 461)], 1.4); bubble(s, 932, 448, "LT", "501", True, r=13)
    PL(s, [(905, 478), (905, 461)], 1.4); bubble(s, 905, 448, "PT", "501", True, r=13)
    # ESD, F&G
    R(s, 838, 310, 98, 36, "#fff3e0", RED, 1.6)
    tg(s, 887, 325, "ESD-501", 11, "middle", 700, RED); tg(s, 887, 339, "tank ESD + F&G (A)", 9.5, "middle", 400, RED)
    bubble(s, 880, 640, "TSL", "501", True, r=14); bubble(s, 1010, 640, "AT", "501", True, r=14)
    tg(s, 880, 662, "LNG det. (A)", 9.5, "middle"); tg(s, 1010, 662, "gas det. (A)", 9.5, "middle")




SRC_KEYS = [
    (1, "lng_design/liquefaction.py size_liquefaction_train, LiquefactionBasis defaults, include_refrigerant_supply=True (2.0 mtpa)"),
    (2, "lng_design/precool.py optimal_evap_temperature (called inside [1])"),
    (3, "lng_design/cascade_loops.py three_loop_cascade: PMR and LRC loops (inside [1])"),
    (4, "lng_design/end_flash.py flash_end_gas, 113.15 K, 4.5 to 1.1 bar(a) (inside [1])"),
    (5, "lng_design/tank_bog.py size_tank_geometry + compute_bog on the tank volume from [1], 1.1 bar(a), 90 % fill"),
    (6, "lng_design/bog_compressor.py size_bog_compressor, BOG from [5], 1.05 to 5 bar(a), 1 + 1 spare"),
    (7, "lng_design/refrigerant_supply.py size_refrigerant_supply (inside [1], default NGL feed)"),
    (8, "process_safety/lng.py impoundment_capacity_m3 (49 CFR 193.2181, text read per that file's docstring)"),
    (9, "process_safety/lng.py DISPERSION_RULE (49 CFR 193.2059)"),
    (10, "Atomic masses C 12.011, H 1.008, N 14.007, O 15.999 (conventional values) give every molar mass here"),
    (11, "CoolProp 8.0 HEOS run (class TH, sheet 2) and GAP_CLOSURE_THERMO.md"),
    (12, "Aoki, Kikkawa INIS QA9700008 (C3 27, MR 64 MW per train)"),
]


def sheet1():
    s = Sheet(1, "LNG liquefaction plant, 2.0 mtpa train: P&ID", "P&ID, whole plant", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case, 10 Nov 2026")
    frame(s, 4)
    frame_area(s)
    zone_pre(s); zone_liq(s); zone_refrig(s); zone_refstore(s); zone_store(s)
    tg(s, 365, 718, "Detector signals and ESD outputs are drawn on sheets 3 and 4.", 9.5, "middle", 400, GREY)
    # right panel: equipment list
    panel_box(s)
    y = section(s, 1135, 84, 445, "EQUIPMENT AND DEVICE LIST")
    rows = [("Tag", "Description", "Basis"),
            ("V-101", "Inlet separator 2,591 mm ID x 3.44 m S/S", "S[1]"),
            ("T-301", "Amine absorber 3.64 m ID, 3.31 m packing; amine loop not sized", "S[1] A"),
            ("V-201A/B", "Mol-sieve beds, 2 x 3.2 m ID x 2.0 m; regen 9.5 kg/s, H-201 5,456 kW", "S[1]"),
            ("A-101", "Trim air cooler, 2 bays 12.2 x 4.9 m, 2,915 kW", "S[1]"),
            ("E-201", "C3 precool evaporator, 12,168 kW", "S[1,2]"),
            ("K-201", "C3 precool compressor 9,330 kW, frame E, 86,361 m3/h", "S[2]"),
            ("K-202", "C3 PMR compressor 27,390 kW, 172.8 kg/s", "S[3]"),
            ("A-201", "Propane condenser 87,134 kW (air or water)", "D, A"),
            ("V-102", "Propane receiver 47.3 m3 (2,591 mm x 8.98 m)", "S[1]"),
            ("E-202", "LRC condenser / PMR evaporator, 38,246 kW", "S[3]"),
            ("K-301", "LRC mixed-refrigerant compressor 27,219 kW", "S[3]"),
            ("V-301", "MR accumulator, not sized", "A"),
            ("E-301", "MCHE, coil-wound; LRC section 882 m2, 11,027 kW; subcooling section 10,844 kW not sized", "S[1]"),
            ("FCV-401", "LNG let-down 50 to 4.5 bar(a); JT valve or expander not chosen", "A"),
            ("V-401", "End-flash drum 4.5 to 1.1 bar(a)", "S[4]"),
            ("K-401", "Flash-gas compressor 323 kW, 1.1 to 5 bar(a)", "S[1]"),
            ("TK-501", "LNG tank 63,827 m3 net, 58.8 m ID, 23.5 m liquid", "S[1,5]"),
            ("P-501A/B", "In-tank loading pumps (not sized)", "A"),
            ("K-501A/B", "BOG compressors, 2-stage reciprocating, 833 m3/h, 66.5 kW each, 1 + 1 spare", "S[6]"),
            ("IMP-501", "Impoundment 1.10 x 63,827 = 70,210 m3", "R[8], D"),
            ("PSV-501A/B", "Tank relief and vacuum protection, to FL-601", "A"),
            ("FL-601", "Flare with knock-out drum", "A"),
            ("ST-701", "Propane bullets 4 x 229 m3 (371 t capacity)", "S[7]"),
            ("ST-702", "Ethane bullets 3 x 231 m3 (255 t) at -15 C, 29.6 bar design pressure", "S[7], R"),
            ("NGL-801", "deC2 / deC3 / deC4, 0.457 m ID, feed 20.1 kmol/h", "S[7]"),
            ("ESD-301/501", "Train and tank ESD with fire and gas detection", "A")]
    y = wtable(s, 1135, y, (80, 285, 80), rows, 9.5, 11.6, 3)
    y = section(s, 1135, y + 10, 445, "SOURCE KEYS  S[n] (details and values on sheet 2)")
    y += 14
    for k_, v_ in SRC_KEYS:
        y = WRAP(s, 1141, y, f"[{k_}] {v_}", 80, 9.5, 11.6) + 2
    # bottom strip: stream key, legend, notes
    y = section(s, 20, 784, 1100, "STREAM KEY (numbers match the diamonds and the HMB on sheet 2; loops 21 to 23 are listed on sheet 2)")
    names = [(k, v[0]) for k, v in STRM.items()] + [(21, "Propane, K-201 circuit (suction)"), (22, "Propane, K-202 (PMR) circuit (suction)"), (23, "LRC mixed refrigerant (shell outlet)")]
    for c in range(3):
        sub_ = names[c * 8:(c + 1) * 8]
        wtable(s, 20 + c * 367, y, (30, 337), [("No.", "Stream")] + [(str(a), b) for a, b in sub_], 9.5, 11.6, 3)
    yl = 962
    section(s, 20, yl, 520, "LEGEND")
    R(s, 20, yl + 22, 520, 118, "#fff", "#889", 1)
    lx, ly = 34, yl + 42
    PL(s, [(lx, ly), (lx + 40, ly)], 2.6); tg(s, lx + 48, ly + 4, "process line", 9.5)
    PL(s, [(lx + 150, ly), (lx + 190, ly)], 2.2, FLARE_C, "9 3 2 3"); tg(s, lx + 198, ly + 4, "relief / vent to flare", 9.5)
    PL(s, [(lx + 330, ly), (lx + 370, ly)], 1.5, RED, "6 4"); tg(s, lx + 378, ly + 4, "ESD output", 9.5)
    ly += 22
    PL(s, [(lx, ly), (lx + 40, ly)], 1.3, BLUE, "5 4"); tg(s, lx + 48, ly + 4, "instrument signal", 9.5)
    PL(s, [(lx + 150, ly), (lx + 190, ly)], 2.0, GREY); tg(s, lx + 198, ly + 4, "amine / regen. stub", 9.5)
    s.add(f'<rect x="{lx+330}" y="{ly-8}" width="40" height="16" fill="#fff" stroke="{GREY}" stroke-dasharray="5 3"/>'); tg(s, lx + 378, ly + 4, "stub, not in HMB", 9.5)
    ly += 24
    conn(s, lx + 10, ly, "L1"); tg(s, lx + 28, ly + 4, "on-sheet continuation (same code = same line)", 9.5)
    strm(s, lx + 300, ly, 5); tg(s, lx + 318, ly + 4, "stream number (sheet 2)", 9.5)
    ly += 24
    tg(s, lx, ly + 4, "Tags: S sourced (file/function), D derived, A assumed by this drawing, R recommended or required by a source.", 9.5)
    tg(s, lx, ly + 18, "Line numbers L-nnn with size and service are 'A' (not defined by the repo). Tag letters follow ISA-5.1 style.", 9.5)
    section(s, 560, yl, 560, "NOTES")
    R(s, 560, yl + 22, 560, 118, "#fff", "#889", 1)
    yy = yl + 38
    for n in ("1. Process basis is the default case of the open-source repo lng-design-opensource: 2.0 mtpa gas to one train, C3 precool + LRC + subcooling, end flash, one LNG tank. The repo sizes loops independently; no real plant data exist.",
              "2. The subcooling loop (10,844 kW) and the amine and regeneration circuits are not sized by the repo and are shown as stubs. Line sizes, valve types and all instrument tags are assumed (A).",
              "3. Two propane circuits (K-201, K-202) share condenser A-201 and receiver V-102 here (A); the repo sizes them as separate calculations. See open items on sheet 2."):
        yy = WRAP(s, 566, yy, n, 104, 9.5, 11.6) + 3
    return s



def sheet1():
    s = Sheet(1, "LNG liquefaction plant, 2.0 mtpa train: P&ID", "P&ID, whole plant", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case, 10 Nov 2026")
    frame(s, 7)
    frame_area(s)
    zone_pre(s); zone_liq(s); zone_refrig(s); zone_refstore(s); zone_store(s)
    tg(s, 365, 718, "Detector signals and ESD outputs: sheets 3, 4 and 6.", 9.5, "middle", 400, GREY)
    # right panel: equipment list
    panel_box(s)
    y = section(s, 1135, 84, 445, "EQUIPMENT AND DEVICE LIST")
    rows = [("Tag", "Description", "Basis"),
            ("V-101", "Inlet separator 2,591 mm ID x 3.44 m S/S; PSV-101, LSHH-101, XV-101", "S[1] A"),
            ("T-301", "Amine absorber 3.64 m ID, 3.31 m packing; PSV-301; loop not sized", "S[1] A"),
            ("V-201A/B", "Mol-sieve beds 2 x 3.2 m ID x 2.0 m; PSV-211A/B; H-201 5,456 kW", "S[1]"),
            ("A-101", "Trim air cooler 2 bays, " + f0(BAL["D"]["A101"]) + " kW (enthalpy)", "S[1] D"),
            ("E-201", "Propane chillers, 4 levels, NG " + f0(BAL["D"]["pre"]) + " kW; PSV-202", "D"),
            ("E-202", "MR precooler (propane), " + f0(BAL["Q_MRpre"]) + " kW; PSV-304", "D"),
            ("K-201 / K-202", "Propane LP / HP casings " + f0(BAL["W_K201"]) + " / " + f0(BAL["W_K202"]) + " kW", "D"),
            ("A-201", "Propane condenser " + f0(BAL["Q_A201"]) + " kW; PSV-203", "D, A"),
            ("V-102", "Propane receiver " + f0(BAL["v102"]["vol"]) + " m3 (" + f0(BAL["v102"]["dia_mm"]) + " mm x " + f1(BAL["v102"]["len_m"]) + " m); PSV-201", "D"),
            ("K-301A/B/C", "MR compressor, 3 casings, " + f0(BAL["W_MR"]) + " kW, 3.5 to 45 bar(a)", "D, A"),
            ("A-301", "MR inter/after-coolers " + f0(BAL["Qcool"]) + " kW; PSV-305", "D"),
            ("V-301", "MR separator/accumulator, not sized; PSV-302", "A"),
            ("E-301", "MCHE coil-wound, NG " + f0(BAL["D"]["mche"]) + " kW; MR shell PSV-303", "S[1] D"),
            ("FCV-401", "LNG let-down 50 to 4.5 bar(a); JT valve or expander not chosen", "A"),
            ("V-401", "End-flash drum 4.5 to 1.1 bar(a); PSV-401, LSLL-401", "S[4] A"),
            ("K-401", "Flash-gas compressor " + f0(BAL["W_k401"]) + " kW, 1.1 to 5 bar(a)", "S[1]"),
            ("TK-501", "LNG tank 63,827 m3 net, 58.8 m ID; TT-501, PT-501, LT-501", "S[1,5]"),
            ("PSV-501A/B", "Tank relief + vacuum protection to FL-601", "A"),
            ("P-501A/B", "In-tank loading pumps (not sized)", "A"),
            ("K-501A/B", "BOG compressors 1 + 1, " + f0(BAL["k501"]["inlet_m3h"]) + " m3/h, " + f1(BAL["k501"]["W_each"]) + " kW", "S[6] D"),
            ("IMP-501", "Impoundment 1.10 x 63,827 = 70,210 m3", "R[8], D"),
            ("XV-101..504, 701/2", "ESD valves (fail closed); BDV-301 fail open", "A"),
            ("DLG-301/302", "Deluge valves, fire-water ring main", "A"),
            ("AT-xxx, BE-301, TSL-501", "Gas, flame and cold-spill detectors (sheet 6)", "A"),
            ("ST-701 / ST-702", "Propane 4 x 229 m3 (S[7]) / ethane 3 x 231 m3, -15 C, 29.6 bar; PSV-701/702", "S[7] R"),
            ("NGL-801", "deC2 / deC3 / deC4, 0.457 m ID, feed 20.1 kmol/h", "S[7]"),
            ("FL-601, F1, F2", "Flare + KOD, warm and cold relief headers", "A"),
            ("ESD-301/501", "Train and tank ESD with fire and gas detection", "A")]
    y = wtable(s, 1135, y, (80, 285, 80), rows, 9.5, 11.6, 3)
    y = section(s, 1135, y + 2, 445, "SOURCE KEYS  S[n] (details and values on sheet 2)")
    y += 14
    for k_, v_ in SRC_KEYS:
        y = WRAP(s, 1141, y, f"[{k_}] {v_}", 80, 9.5, 11.6) + 2
    # bottom strip: stream key, legend, notes
    y = section(s, 20, 784, 1100, "STREAM KEY (numbers match the diamonds and the HMB on sheet 2; loops 21 to 23 on sheet 2)")
    names = [(k, v[0]) for k, v in STRM.items()] + [(21, "Propane to K-201 LP casing (suction, level 4)"), (22, "Propane to K-202 HP casing (suction, level 2)"), (23, "MR to K-301A LP suction (3.5 bar a)")]
    for c in range(3):
        sub_ = names[c * 8:(c + 1) * 8]
        wtable(s, 20 + c * 367, y, (30, 337), [("No.", "Stream")] + [(str(a), b) for a, b in sub_], 9.5, 11.6, 3)
    yl = 962
    section(s, 20, yl, 520, "LEGEND")
    R(s, 20, yl + 22, 520, 118, "#fff", "#889", 1)
    lx, ly = 34, yl + 42
    PL(s, [(lx, ly), (lx + 40, ly)], 2.6); tg(s, lx + 48, ly + 4, "process line", 9.5)
    PL(s, [(lx + 150, ly), (lx + 190, ly)], 2.2, FLARE_C, "9 3 2 3"); tg(s, lx + 198, ly + 4, "relief / vent to flare", 9.5)
    PL(s, [(lx + 330, ly), (lx + 370, ly)], 1.5, RED, "6 4"); tg(s, lx + 378, ly + 4, "ESD output", 9.5)
    ly += 22
    PL(s, [(lx, ly), (lx + 40, ly)], 1.3, BLUE, "5 4"); tg(s, lx + 48, ly + 4, "instrument signal", 9.5)
    PL(s, [(lx + 150, ly), (lx + 190, ly)], 2.0, GREY); tg(s, lx + 198, ly + 4, "amine / regen. stub", 9.5)
    s.add(f'<rect x="{lx+330}" y="{ly-8}" width="40" height="16" fill="#fff" stroke="{GREY}" stroke-dasharray="5 3"/>'); tg(s, lx + 378, ly + 4, "stub, not in HMB", 9.5)
    ly += 24
    conn(s, lx + 10, ly, "L1"); tg(s, lx + 28, ly + 4, "on-sheet continuation (same code = same line)", 9.5)
    strm(s, lx + 300, ly, 5); tg(s, lx + 318, ly + 4, "stream number (sheet 2)", 9.5)
    ly += 24
    tg(s, lx, ly + 4, "Tags: S sourced (file/function), D derived, A assumed by this drawing, R recommended or required by a source.", 9.5)
    tg(s, lx, ly + 18, "Line numbers L-nnn with size and service are 'A' (not defined by the repo). Tag letters follow ISA-5.1 style.", 9.5)
    section(s, 560, yl, 560, "NOTES")
    R(s, 560, yl + 22, 560, 118, "#fff", "#889", 1)
    yy = yl + 38
    for n in ("1. Process basis: default case of the open-source repo lng-design-opensource (2.0 mtpa gas to the train), with the Rev B corrections on sheet 2: NG duties from CoolProp enthalpy, 4-level propane cascade, 3-stage MR loop, gas-turbine fuel tap (stream 20).",
              "2. Relief devices PSV-xxx go to F1 (warm) or F2 (cold) headers to FL-601; sizes and design pressures are in the relief schedule (sheet 5). ESD matrix and SIFs: sheet 6. Detection, impoundment, hazard nodes: sheet 7. All logic and set pressures are A.",
              "3. Line sizes, valve types and instrument tags are assumed (A). Suction knock-out drums, anti-surge and cold-box purge are not drawn (open items, sheet 2)."):
        yy = WRAP(s, 566, yy, n, 104, 9.5, 11.6) + 3
    return s




def pct(x, tot_):
    v = x / tot_ * 100
    if v == 0: return "-"
    if v < 0.01: return "<0.01"
    return f"{v:.2f}" if v < 1 else f"{v:.1f}"


def sheet2():
    s = Sheet(2, "Heat and material balance Rev B: streams, duties, closure, Rev A to Rev B changes", "HMB, duties, loops, changes", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case + CoolProp corrections, Rev B 11 Nov 2026")
    frame(s, 7)
    B = BAL; st = B["st"]; D = B["D"]; A_ = S_A
    ids = list(range(1, 21)); labels = [str(i) for i in ids]
    def tp(i):
        t_, p_ = STRM[i][2], STRM[i][3]
        return (f"{t_:.1f}" if t_ is not None else "-"), (f"{p_:.2f}" if p_ is not None else "-")
    ttag = {1: "S", 2: "A", 3: "A", 5: "A", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S", 12: "S", 13: "S", 14: "S", 15: "D", 16: "S", 17: "S", 19: "S", 20: "A"}
    ptag = {1: "S", 2: "A", 3: "A", 5: "A", 7: "A", 8: "A", 9: "A", 10: "A", 11: "A", 12: "S", 13: "S", 14: "S", 15: "A", 16: "A", 17: "A", 18: "A", 19: "S", 20: "A"}
    rows = [("Phase (G gas, L liquid, G* not checked)", [STRM[i][1] for i in ids]), ("Temperature (C)", [tp(i)[0] for i in ids]), ("Pressure (bar a)", [tp(i)[1] for i in ids]),
            ("T tag / P tag", [f"{ttag.get(i, '-')}/{ptag.get(i, '-')}" for i in ids]), ("Mass flow", None),
            ("Total (kg/h)", [f0(tot(st[i]) * 3600) for i in ids]), ("Total (kg/s)", [f"{tot(st[i]):.3f}" for i in ids]), ("Composition (mass %)", None)]
    for g, members in GROUPS: rows.append((g, [pct(sum(st[i].get(k, 0.0) for k in members), tot(st[i])) for i in ids]))
    y = hmb_table(s, 20, 84, labels, rows, first_w=232, col_w=62, rh=14.6, size=9.5, title=f"HEAT AND MATERIAL BALANCE Rev B (diamonds on sheet 1; basis {S['m_sweet']:.3f} kg/s dry sweet gas; stream 20 fuel tap {tot(st[20]):.3f} kg/s; cold-train gas {B['mc']:.3f} kg/s)")
    tg(s, 20, y + 11, "Stream 10 phase not computed here (EOS not in this generator; CoolProp enthalpies are used only for duties). Streams 4 and 6 leave the regeneration circuits. Streams 21 to 23 (loops) are in the table at right.", 9.5, "start", 400, GREY)
    y0 = y + 20
    yd = section(s, 20, y0, 780, "DUTY AND POWER LINES (kW)")
    tp_ = B["stg"]
    drows = [("Item", "Service", "kW", "Tag", "Source / formula"),
             ("A-101", "trim cooling 60 to 40 C, 50 bar", f0(D["A101"]), "D", f"m (h333.15 - h313.15), CoolProp; Rev A {f0(A_['trim_kW'])} (constant cp)"),
             ("E-201 NG", "NG 40 to -40 C, propane chillers", f0(D["pre"]), "D", "m_cold (h313.15 - h233.15)"),
             ("E-202 MR", "MR 40 to -40 C, propane chillers", f0(B["Q_MRpre"]), "D", "m_MR (h313 - h233 at 45 bar), CoolProp"),
             ("E-301 warm", "NG -40 to -100 C", f0(D["lrc"]), "D", f"m_cold (h233.15 - h173.15); at 63.376 kg/s = {f0(D['lrc_ref'])} (validator CoolProp 25,915)"),
             ("E-301 cold", "NG -100 to -159 C", f0(D["sub"]), "D", f"m_cold (h173.15 - h114.15); at 63.376 kg/s = {f0(D['sub_ref'])} (validator 12,165)"),
             ("K-201", "propane LP casing, levels 4 and 3", f0(B["W_K201"]), "D", "4-level cascade, CoolProp, eta 0.75 (repo value), scaled to the evaporator duty"),
             ("K-202", "propane HP casing, levels 2 and 1", f0(B["W_K202"]), "D", "same"),
             ("K-301A/B/C", "MR 3 casings, 3.5 to 45 bar(a)", f0(B["W_MR"]), "D", "W_tot - W_C3; m_MR = W_MR / 304.4 kJ/kg (CoolProp 3 stages)"),
             ("A-201", "propane condensing", f0(B["Q_A201"]), "D", "propane evaporator duty + W_C3"),
             ("A-301", "MR inter/after-coolers", f0(B["Qcool"]), "D", "m_MR sum(h_out - h(313 K)), CoolProp"),
             ("K-401", "flash gas 1.1 to 5 bar(a)", f0(B["W_k401"]), "S", f"repo {f0(S['k401']['W'])} kW x {B['sc']:.4f} (flash gas scales with cold-train gas)"),
             ("K-501", "BOG, one machine (shaft)", f0(B["k501"]["W_each"]), "S", "repo machine scaled with design BOG"),
             ("C3 + MR shaft", "refrigeration shaft power", f0(B["W_tot"]), "D", f"= {abs(TH['w_ideal_kWh_t']):.1f} kWh/t ideal x {B['t_lng_h']:.1f} t/h / eta_II {RB['eta_II']:.2f} (A)"),
             ("Specific power", f"{B['kWh_t']:.0f} kWh/t (refrigeration), {B['kWh_t_all']:.0f} with K-401, K-501", "-", "D", "per t LNG shipped; reference 300 to 350 kWh/t (Qatargas-derived 317 to 347)"),
             ("GT fuel", f"{B['fuel_kW']/1000:.1f} MW LHV = shaft / {RB['eta_gt']:.2f} (A)", f0(B["fuel_kW"]), "D", f"header energy from streams 15 + 17, remainder from tap stream 20 = {B['fuel_pct']:.1f} % of sweet gas")]
    yd = wtable(s, 20, yd, (100, 250, 60, 34, 336), drows, 9.5, 10.8, 2.5)
    xl = 815
    yl_ = section(s, xl, y0, 765, "COMPRESSOR STAGES, SUCTION VOLUME AND CASINGS (frame range 55,000 to 110,000 m3/h, S[2])")
    lrows = [("Loop / stage", "Suction bar(a)", "Discharge bar(a)", "Flow kg/s", "Power kW", "Suction m3/h", "Casings")]
    for x in tp_: lrows.append((f"C3 level {x['level']} stage", f"{x['P_in']:.2f}", f"{x['P_out']:.2f}", f1(x["m"]), f0(x["W"]), f0(x["vol"]), str(x["casings"])))
    for i, x in enumerate(B["mrst"]): lrows.append((f"MR stage {i+1} (K-301{'ABC'[i]})", f"{x['P_in']:.2f}", f"{x['P_out']:.2f}", f1(B["m_MR"]), f0(x["W"]), f0(x["vol"]), str(x["casings"])))
    yl_ = wtable(s, xl, yl_, (150, 90, 100, 90, 100, 130, 105), lrows, 9.5, 11.4, 3)
    mrb = TH["mr_blend"]
    yl_ = WRAP(s, xl + 6, yl_ + 14, f"MR blend (A, mol %): N2 {mrb['Nitrogen']*100:.0f}, CH4 {mrb['Methane']*100:.0f}, C2H6 {mrb['Ethane']*100:.0f}, C3H8 {mrb['Propane']*100:.0f}; Pe {TH['mr_Pe']} bar(a), Pc {TH['mr_Pc']} bar(a), 3 stages, intercooled to 313.15 K. Propane levels 285.15, 268.15, 250.15, 230.15 K (A), condensing 313.15 K, {B['Pc_C3']/1e5:.2f} bar(a). MR LP stage suction is at the top of one frame (double-flow LP casing, as at Qatargas, S: GAP_CLOSURE_THERMO): casings counted = suction volume / 110,000 rounded up.", 122, 9.5, 11.6)
    yl_ = WRAP(s, xl + 6, yl_ + 4, f"Residuals shown, not hidden: C3 share {B['c3_share']*100:.0f} % of shaft power (C3:MR = 1:{B['mr_over_c3']:.2f}) vs reference 1:2 to 3 (Qatargas 27:64 MW). MR loop at this flow can deliver {f0(B['Q_del'])} kW to the cold box vs {f0(D['mche'])} kW NG demand (ratio {B['del_ratio']:.2f}): the excess is the unmodelled real-cycle pinch penalty. A single-JT MR cycle test (CoolProp, 24 blends) gave a negative minimum approach: a split-flow C3MR cycle is needed to derive the flow from duty (open).", 122, 9.5, 11.6, fill=RED)
    yb = max(yd, yl_) + 10
    yy = section(s, 20, yb, 1100, "REV A TO REV B CHANGES")
    ch = [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
          ("NG duty 233 to 173 K", f"{f0(A_['lrc_duty'])} kW (cp 2.9)", f"{f0(D['lrc'])} kW ({f0(D['lrc_ref'])} at 63.376 kg/s)", "CoolProp HEOS h(T) at 50 bar (S, validator and this run agree)", "-57 % gap closed; the gas condenses in this span"),
          ("NG duty 173 to 114 K", f"{f0(A_['sub_duty'])} kW", f"{f0(D['sub'])} kW ({f0(D['sub_ref'])} at 63.376)", "same", "-11 % gap closed; total NG cooling 38.1 MW at 63.376 kg/s"),
          ("Subcooling loop", "stub, power omitted", "inside MR loop K-301A/B/C", "GAP_CLOSURE_THERMO (Qatargas: MR in 3 casings)", "removes the omitted 10.8 MW term from the ledger"),
          ("MR loop pressure ratio", f"{A_['lrc']['Pc']/A_['lrc']['Pe']:.0f} (0.09 bar suction, 1 machine)", f"{TH['mr_Pc']/TH['mr_Pe']:.1f} in 3 stages, 3.5 bar suction (A)", "CoolProp; Pe not sourced (range 3 to 5 bar, A)", "suction volume per stage within frame range; vacuum removed"),
          ("Propane arrangement", f"2 single-stage circuits, K-202 {f0(A_['pmr']['W'])} kW at 236,297 m3/h", f"4-level cascade, 2 casings, max stage {f0(max(x['vol'] for x in B['stg']))} m3/h", "CoolProp (S computed); frame range S[2]", "K-202 volume 2.1x over range closed"),
          ("C3:MR power", f"{A_['c3']['W']+A_['pmr']['W']:,.0f} : {A_['lrc']['W']:,.0f} kW (propane > MR)", f"{f0(B['W_C3'])} : {f0(B['W_MR'])} kW (1:{B['mr_over_c3']:.2f})", "ref 1:2 to 3; Qatargas 27:64 MW (Aoki, Kikkawa INIS QA9700008)", "reduced, not closed (residual shown)"),
          ("Specific power", "297 (421 with omitted loop) kWh/t", f"{B['kWh_t']:.0f} kWh/t, all loops", "ref 300 to 350 (Air Products C; Qatargas-derived 317 to 347)", "closed; eta_II 0.40 is A, chosen inside the sourced band"),
          ("V-102 receiver", "47.3 m3, 97 s on both circuits", f"{B['v102']['vol']:.0f} m3 = {B['v102']['dia_mm']:,.0f} mm x {B['v102']['len_m']:.1f} m, 300 s at 70 % fill", "repo 300 s basis; CoolProp rho 467.5", "residence gap closed; one vessel or two halves (A)"),
          ("TK-501 boil-off", "0.122 %/day, 133.7 kW", f"0.050 %/day, {B['Q_in']:.1f} kW", "GAP_CLOSURE_THERMO: design < 0.05, range 0.02 to 0.1 (high)", f"BOG {A_['tank']['bog']:.3f} to {B['bog']:.3f} kg/s; K-501 resized; range 0.03 to 0.05 %/day = {0.03/0.05*B['Q_in']:.1f} to {B['Q_in']:.1f} kW"),
          ("Driver fuel", "not computed", f"{B['fuel_kW']/1000:.1f} MW LHV; tap {tot(st[20]):.2f} kg/s", "GT efficiency 0.33 (A; 0.33 to 0.38); LHV via chemicals Hfg", f"LNG shipped {A_['m_sweet']*0+ (tot(st[19])*365.25*24*3600/1e9):.3f} mtpa (Rev A {1.895:.3f})")]
    yy = wtable(s, 20, yy, (120, 190, 250, 280, 260), ch, 9.5, 11.0, 2.5)
    cl = [f"Mass: in {f0(B['m_in'])} kg/h, out {f0(B['m_out'])} kg/h, error {B['err_pct']:.4f} %.",
          "Elements C, H, N, O error %: " + ", ".join(f"{e} {v:.4f}" for e, v in B["el_err"].items()) + ".",
          f"Heat: rejection A-201 + A-301 {f1(B['heat_out'])} kW = NG sensible cooling + W_C3 + W_MR + unallocated MR effect {f0(B['unalloc'])} kW = {f1(B['heat_in'])} kW, error {B['heat_err']:.4f} %.",
          f"Propane: Qe + W = Qc (1e-6). MR: Qcool + Q_MRpre - W = {f0(B['Q_del'])} kW = m_MR (h_cold - h_hot) (1e-3).",
          "NG duties reproduce the validator CoolProp values (25,915 and 12,165 kW at 63.376 kg/s) to 0.3 % (asserted)."]
    yc = section(s, 20, yy + 8, 540, "CLOSURE (asserted in code)")
    for ln in cl: yc = WRAP(s, 26, yc + 14, ln, 100, 9.5, 11.6) - 2
    ya = section(s, 570, yy + 8, 550, "ASSUMED (A) AND FROZEN TOOL RESULTS")
    for ln in ("Rev A A1 to A11 stand except A6 (one condenser A-201 and receiver V-102 serve the 4-level cascade) and A7 (replaced by fuel tap, stream 20).",
               "A12 eta_II 0.40, GT efficiency 0.33, MR blend and Pe/Pc, propane levels, 313.15 K ambient approach, flare back pressure: assumed.",
               "Frozen (class TH): venv_val python thermo_lng.py final2 (CoolProp 8.0 HEOS): h(T) 50 bar, 4-level propane, 3-stage MR, exergy 129.1 kWh/t; chemicals Hfg for LHV. No DWSIM result is claimed."):
        ya = WRAP(s, 576, ya + 14, ln, 104, 9.5, 11.6) - 2
    x2 = 1135; y2 = section(s, x2, 640, 445, "OPEN ITEMS (Rev B)", RED)
    for ln in ("1 C3:MR split 1:%.2f vs 1:2 to 3: needs a licensor split-flow cycle." % B["mr_over_c3"], "2 MR blend, Pe and eta_II are A: replace with licensor data.",
               "3 Suction knock-out drums per casing and anti-surge not drawn.", "4 Stream 10 phase and CO2 freeze-out at the cold end not computed.",
               "5 K-501 and tank volume kept at the repo 2 mtpa size although boil-off is lower.", "6 Rollover, ship-loading vapour and flare loads not sized.",
               "7 FCV-401 inlet is -159 C but end flash starts at -160 C (1 K, repo).", "8 Electric vs gas-turbine drive: GT assumed; with electric drive the tap falls to near zero (Freeport fuel use 1.8 %, S: FEIS)."):
        y2 = WRAP(s, x2 + 6, y2 + 14, ln, 84, 9.5, 11.6, fill=RED) - 2
    return s


def mark(s, x, y, n):
    s.add(f'<circle cx="{x}" cy="{y}" r="9" fill="#e8f5e9" stroke="{GREEN}" stroke-width="1.6"/>')
    T(s, x, y + 3.5, str(n), 9.5, 700, "middle", GREEN)


def xmark(s, x, y, r=11):
    PL(s, [(x - r, y - r), (x + r, y + r)], 3, RED); PL(s, [(x - r, y + r), (x + r, y - r)], 3, RED)


def scen_head(s, x, y, w, code, title, color=RED):
    R(s, x, y, w, 24, color, "none")
    T(s, x + 8, y + 17, f"{code}  {title}", 12, 700, fill="#fff")
    return y + 24


def kv_table(s, x, y, rows, w=445):
    return wtable(s, x, y, (w - 150, 105, 45), [("Quantity", "Value", "Tag")] + rows, 9.5, 11.4, 3)


def scen_table(s, y, rows):
    return wtable(s, 20, y, (68, 196, 232, 330, 274), [("Scenario", "Initiating event", "Hazard", "Safeguards shown", "Open data needs")] + rows, 9.5, 11.4, 3.5)


# -------- overlays on the storage zone (sheet-1 coordinates) --------
def overlay_store_signals(s):
    # detectors and instruments to ESD-501 (blue); ESD outputs to valves (red)
    sig(s, [(880, 626), (880, 618), (841, 618), (841, 360), (850, 360), (850, 347)])
    sig(s, [(1010, 626), (1010, 618), (880, 618)])
    sig(s, [(905, 435), (905, 348)]); sig(s, [(932, 435), (932, 348)])
    esd(s, [(872, 346), (872, 436), (881, 437)])
    esd(s, [(936, 333), (976, 333), (976, 395), (967, 395)])
    esd(s, [(838, 328), (804, 328), (804, 558), (806, 560)])
    # P-501 trip
    esd(s, [(856, 346), (856, 380), (846, 380), (846, 598), (856, 598)])


def grp(s, tx, ty, k, fn, *a):
    s.add(f'<g transform="translate({tx},{ty}) scale({k})">')
    fn(s, *a)
    s.add('</g>')


def draw_sheet3_scene(s):
    """sheet-1 coordinates; scaled by the caller"""
    zone_store(s, jetty_stub=False)
    overlay_store_signals(s)
    PL(s, [(1095, 340), (1095, 740)], 3.2); arrow(s, 1095, 740, "d"); tg(s, 1090, 330, "FUEL GAS 5 bar(a) (A)", 9.5, "end", 700)
    # jetty
    pipe(s, [(820, 700), (820, 740), (570, 740)]); valve(s, 760, 740, 0, "gate", act=True); tg(s, 760, 766, "XV-504 (A)", 9.5, "middle", 700)
    s.add(f'<path d="M430,712 L560,712 L545,748 L445,748 Z" fill="#fff" stroke="{INK}" stroke-width="2"/>'); T(s, 495, 735, "LNG CARRIER", 10, 700, "middle")
    tg(s, 810, 730, "L-501 (A)", 9.5, "end", 700); tg(s, 700, 758, "loading arm (A, not sized)", 9.5, "start")
    # ---- scenario A
    cloud(s, 665, 585, 165, 70, None)
    tg(s, 665, 575, "cold dense vapour cloud,", 10, "middle", 700, BLUE); tg(s, 665, 589, "then buoyant: not sized", 10, "middle", 700, BLUE)
    pool(s, 700, 692, 55, 14, fill="#9ecbff")
    flame(s, 685, 692, 0, 48, 34); flame(s, 722, 692, -10, 38, 26)
    tg(s, 630, 722, "LNG pool, pool fire if ignited", 9.5, "start", 700, RED)
    star(s, 820, 625, 17); T(s, 820, 629, "A1", 9.5, 700, "middle")
    star(s, 865, 466, 13); T(s, 865, 470, "A2", 9.5, 700, "middle")
    PL(s, [(806, 640), (745, 680)], 2, BLUE, "4 3", "ahb")
    PL(s, [(822, 640), (836, 662)], 3, "#8d6e63", "6 3")
    tg(s, 520, 650, "spill trench to impoundment (A)", 9.5, "start", 700, "#6d4c41"); PL(s, [(690, 647), (815, 650)], 1.3, "#8d6e63", "5 3", "ahb")
    tg(s, 440, 676, "RPT only if LNG reaches water (berth,", 9.5); tg(s, 440, 688, "drains): no drain to water (A)", 9.5)
    PL(s, [(430, 480), (520, 480)], 3, GREY, None, "ah"); tg(s, 430, 470, "wind: site data needed", 9.5, "start", 400, GREY)
    mark(s, 826, 322, 1); mark(s, 899, 408, 2); mark(s, 928, 395, 2); mark(s, 800, 530, 2); mark(s, 912, 650, 1); mark(s, 1060, 618, 3); mark(s, 836, 612, 4)
    # ---- scenario C
    xmark(s, 1028, 370, 10); xmark(s, 1028, 410, 10)
    tg(s, 1060, 346, "K-501A/B trip", 10, "end", 700, RED)
    PL(s, [(1043, 452), (1075, 452), (1075, 745)], 4, RED, "9 3 2 3")
    tg(s, 1070, 500, "PSV lifts", 9.5, "end", 700, RED)
    star(s, 1000, 520, 14); T(s, 1000, 524, "C", 9.5, 700, "middle")
    tg(s, 992, 505, "pressure rises", 9.5, "end", 700, RED)
    mark(s, 905, 426, 5); mark(s, 1012, 430, 6); mark(s, 1058, 462, 7); mark(s, 932, 426, 8)
    # rollover layers inside the tank
    s.add(f'<rect x="856" y="578" width="188" height="31" fill="#8fb8de" opacity=".75"/>')
    PL(s, [(856, 578), (1044, 578)], 1.3, BLUE, "6 4")
    tg(s, 872, 570, "upper layer: lighter", 9.5, "start"); tg(s, 934, 600, "lower layer: denser", 9.5, "start", 700)
    PL(s, [(1035, 604), (1035, 585), (1042, 562), (1035, 545)], 2.2, RED, None, "ahr")


def sheet3():
    s = Sheet(3, "Scenarios A and C: LNG loss of containment, BOG compressor failure and rollover", "Scenarios A and C, storage and loading", code="VS-LNG",
              project="LNG liquefaction plant (repo default 2.0 mtpa case)", basis="lng-design-opensource default case, 10 Nov 2026")
    frame(s, 7)
    frame_area(s)
    grp(s, -380, -305, 1.35, draw_sheet3_scene)
    # ---- right panel
    panel_box(s)
    y = scen_head(s, 1135, 84, 445, "A", "LNG release from TK-501 loading line or roof nozzle")
    yy = WRAP(s, 1141, y + 16, "Release at the transfer line L-501 (A1) or the pump-discharge roof nozzle (A2). LNG pools, boils off cold methane-rich vapour (dense, then buoyant), may ignite as a pool fire or flash fire, and chills carbon steel to brittle fracture. Rapid phase transition only if LNG reaches water. Shown with the impoundment, trench, ESD valves and detection.", 78, 10, 12.4)
    yy = kv_table(s, 1135, yy + 6, [
        ("TK-501 inventory at 90 % fill (t)", f0(S["tank"]["inv_kg"] / 1000), "S[5]"),
        ("LNG density, 108.43 K, 1.1 bar(a) (kg/m3)", f1(S["tank"]["rho_l"]), "S[5]"),
        ("LNG temperature in tank (C)", f"{S['ef']['T'] - 273.15:.1f}", "S[4]"),
        ("Net tank volume (m3)", f0(S["tank"]["V"]), "S[1]"),
        ("Impoundment 1.10 x net volume (m3)", f0(S["impound_m3"]), "R[8] D"),
        ("49 CFR 193.2059 case: average concentration", "2.5 vol %", "S[9]"),
        ("   receptor height / roughness", "0.5 m / 0.03 m", "S[9]"),
        ("   stability / wind / humidity", "F / 2.01 m/s / 50 %", "S[9]")])
    yy = WRAP(s, 1141, yy + 18, "Not quantified: pool size, burn rate, vapour and radiation distances. The toolkit's dispersion is neutral-gas screening and is not valid for cold LNG vapour; a dense-gas model (for example DEGADIS) and a pool-fire model (for example LNGFIRE3) are needed, with release rate, duration and site wind.", 78, 10, 12.4, RED)
    y = scen_head(s, 1135, yy + 10, 445, "C", "BOG compressor failure, tank overpressure and rollover")
    yy = WRAP(s, 1141, y + 16, "Both K-501A/B trip, or the fuel header cannot take BOG: boil-off accumulates in TK-501, pressure rises, PSV-501A/B lifts and cold vapour goes to FL-601. A rollover releases BOG far above the static rate.", 78, 10, 12.4)
    yy = kv_table(s, 1135, yy + 6, [
        ("Heat ingress (kW)", f1(S["tank"]["Q_kW"]), "S[5]"),
        ("Static BOG (kg/s)", f"{S['tank']['bog']:.3f}", "S[5]"),
        ("   = t/day; boil-off rate (% per day)", f"{BAL['bog_t_d']:.1f}; {S['tank']['bor']:.3f}", "D8 S[5]"),
        ("Design BOG with 10 % margin (kg/s)", f"{S['k501']['design']:.3f}", "S[6]"),
        ("BOG: CH4 / N2 (mol %)", f"{S['tank']['bog_y']['CH4']*100:.1f} / {S['tank']['bog_y']['N2']*100:.1f}", "S[5]"),
        ("K-501 inlet per machine (m3/h); shaft (kW)", f"{S['k501']['inlet_m3h']:.0f}; {S['k501']['W_each']:.1f}", "S[6]"),
        ("Vapour space (m3)", f0(BAL["vap_vol"]), "D8"),
        ("Pressure-rise bound, all BOG kept (Pa/s)", f"{BAL['dPdt_Pa_s']:.2f} (5.2 kPa/h)", "D9")])
    yy = WRAP(s, 1141, yy + 18, "D9: dP/dt = (m/M) R T / V, ideal gas, isothermal vapour, no vapour-liquid equilibrium: an upper bound. Not quantified: time to PSV set and PSV load (need design pressure, set pressure, relief rate), and rollover (needs layer data).", 78, 10, 12.4, RED)
    # ---- bottom strip: scenario table and safeguard key
    yb = section(s, 20, 784, 1100, "SCENARIO TABLE (green numbers on the drawing are the safeguards listed in the table)")
    rows = [("A  LNG release", "Rupture, flange or arm leak on loading line L-501 or the roof pump-discharge nozzle; frequency and hole size not available",
             "LNG pool and pool fire; cold dense vapour cloud, flash fire or explosion if congested; brittle fracture and cold burns; rapid phase transition if LNG reaches water",
             "1 TSL-501 / AT-501 / flame detection to ESD-501 (A); 2 XV-501, XV-502, XV-503, P-501 trip (A); 3 impoundment 70,210 m3 (R, 49 CFR 193.2181); 4 spill trench to impoundment, sump, no drain to water (A); cryogenic materials (A)",
             "Line size, pressure, loading rate, hole size, duration; site wind and ground; impoundment and tank-surge design; validated dense-gas and pool-fire models; water proximity"),
            ("C  BOG and rollover", "Trip of K-501A and K-501B, fuel header high pressure, or stratified LNG rolling over",
             "Tank overpressure, PSV lift and flare load; vacuum if pump-out without return; BOG surge in rollover; N2-rich BOG (37.6 mol %) disturbs fuel gas",
             "5 PT-501 PAH / PAHH and PIC split range to flare (A); 6 spare K-501B auto start (R: repo 1 + 1); 7 PSV-501A/B to FL-601 (A); 8 LT-501 and multipoint TT-501 for stratification (A); vacuum breaker (A)",
             "Tank design pressure and PSV set; relief capacity; flare capacity; cargo composition and density; stratification data")]
    scen_table(s, yb, rows)
    y = section(s, 1135, 700, 445, "TOOLKIT USE (documented numbers only)")
    for ln in ("Used: process_safety/lng.py impoundment_capacity_m3 (49 CFR 193.2181) and DISPERSION_RULE (49 CFR 193.2059, verified per its docstring).",
               "Not used: the toolkit's Gaussian dispersion (its docstring says it is not valid for cold LNG vapour) and the methane property table there (recalled values, +-3 %); LNG properties come from the repo's CoolProp calls.",
               "docs/ and scripts/build_lng_analogs.py hold LNG capital-cost analogs only, no consequence data."):
        y = WRAP(s, 1141, y + 16, ln, 78, 10, 12.4) - 2
    return s


def draw_sheet4_scene(s):
    zone_liq(s); zone_refrig(s); zone_refstore(s)
    pipe(s, [(500, 250), (565, 250)], arrow_=False); tg(s, 470, 232, "from A-101", 9.5, "start", 700)
    # ---- signals and ESD outputs (train)
    sig(s, [(545, 467), (545, 672), (441, 672)])
    sig(s, [(543, 490), (533, 490), (533, 682), (441, 682)])
    sig(s, [(700, 615), (700, 692), (441, 692)])
    esd(s, [(290, 672), (270, 672), (270, 505), (258, 505)])
    esd(s, [(365, 704), (365, 725), (770, 725), (770, 515), (756, 515)])
    # ---- scenario B
    cloud(s, 455, 430, 215, 105, None)
    tg(s, 245, 318, "flammable cloud: flash fire, VCE if congested (not sized)", 10, "start", 700, BLUE)
    star(s, 440, 388, 17); T(s, 440, 392, "B1", 9.5, 700, "middle")
    PL(s, [(424, 392), (385, 405)], 2, BLUE, "4 3", "ahb")
    star(s, 170, 545, 13); T(s, 170, 549, "B2", 9.5, 700, "middle")
    cloud(s, 110, 565, 120, 42, None, op=0.35)
    tg(s, 30, 627, "B2: ethane at -15 C, cold dense cloud (not sized)", 9.5, "start", 700, BLUE)
    # ---- scenario D
    flame(s, 760, 523, 0, 78, 56)
    R(s, 548, 500, 245, 98, "none", BLUE, 1.6, "7 4")
    R(s, 196, 452, 92, 50, "none", BLUE, 1.6, "7 4")
    s.add('<rect x="212" y="487" width="58" height="12" fill="url(#hatch)" opacity=".8"/>')
    tg(s, 30, 641, "PFP on V-102 supports (A), hatched", 9.5, "start", 700, AMBER)
    tg(s, 30, 655, "D: escalation targets V-102 (propane charge),", 9.5, "start", 700, RED); tg(s, 30, 668, "V-301, A-201, MCHE", 9.5, "start", 700, RED)
    # ---- markers
    mark(s, 610, 440, 1); mark(s, 345, 705, 2); mark(s, 676, 497, 3); mark(s, 290, 430, 4); mark(s, 200, 412, 5)
    mark(s, 540, 496, 6); mark(s, 204, 478, 7); mark(s, 790, 506, 6)


def sheet4():
    s = Sheet(4, "Scenarios B and D: refrigerant release and fire at the liquefaction train", "Scenarios B and D, refrigerant loops and train", code="VS-LNG",
              project="LNG liquefaction plant (repo default 2.0 mtpa case)", basis="lng-design-opensource default case, 10 Nov 2026")
    frame(s, 7)
    frame_area(s)
    draw_sheet4_scene(s)
    # callouts in the free top-left area
    R(s, 24, 92, 420, 84, "#fff", RED, 1.4)
    tg(s, 32, 108, "B  Refrigerant release (propane, ethane, mixed refrigerant)", 10.5, "start", 700, RED)
    for k_, ln in enumerate(("B1: K-201 / K-202 discharge header, propane 13.69 bar(a), 313 K (S[2], [3])",
                             "B2: ethane bullet outlet, -15 C, 29.6 bar design (S[7])",
                             "The repo uses ethane and propane; there is no ethylene loop.",
                             "Mixed refrigerant (LRC) lines: same hazard, see table.")):
        tg(s, 32, 124 + k_ * 14, ln, 9.5)
    R(s, 24, 186, 420, 70, "#fff", RED, 1.4)
    tg(s, 32, 202, "D  Fire at the liquefaction train (compressor and cold-end area)", 10.5, "start", 700, RED)
    for k_, ln in enumerate(("Ignited leak at K-301 / E-202 (A). Escalation targets: V-102 propane",
                             "charge (sheet 4 table), V-301, MCHE, A-201. Safeguards: flame and gas",
                             "detection, ESD-301, BDV-301 to flare, deluge, PFP (all A).")):
        tg(s, 32, 218 + k_ * 14, ln, 9.5)
    # right panel
    panel_box(s)
    y = scen_head(s, 1135, 84, 445, "B", "Refrigerant release (propane, ethane, mixed)")
    yy = WRAP(s, 1141, y + 16, "Loss of containment of flammable refrigerant at the C3 machinery (B1) or the ethane storage (B2): flashing liquid and vapour jet, flammable cloud, flash fire or vapour cloud explosion in the congested train, jet fire, and BLEVE of a vessel exposed to fire. Ethane at -15 C also causes cold burns.", 78, 10, 12.4)
    yy = kv_table(s, 1135, yy + 6, [
        ("Propane circulating K-201 / K-202 (kg/s)", f"{S['c3']['m']:.1f} / {S['pmr']['m']:.1f}", "S[2,3]"),
        ("Propane condensing pressure (bar a)", f"{S['c3']['Pc']/1e5:.2f}", "S[2]"),
        ("V-102 propane charge (t); PMR x 300 s (t)", f"{S['c3_charge_kg']/1000:.1f}; {BAL['pmr_hold_kg']/1000:.1f}", "S[1]; D"),
        ("MR charge: 8,000 kmol (Rev A repo, t)", f"{BAL['lrc_charge_kg']/1000:.0f}", "S[1] D"),
        ("MR discharge / suction (bar a)", f"{S['lrc']['Pc']/1e5:.1f} / {S['lrc']['Pe']/1e5:.4f}", "S[3]"),
        ("Refrigerant charge, all components (t)", f"{BAL['ref_charge_total_kg']/1000:.1f}", "S[7] D"),
        ("   propane / ethane / CH4 / N2 (t)", "122.6 / 84.2 / 38.5 / 11.2", "S[7]"),
        ("ST-701 propane, 4 bullets (t)", f"{S['supply']['propane']['cap_kg']/1000:.0f}", "S[7]"),
        ("ST-702 ethane, 3 bullets, -15 C (t)", f"{S['supply']['ethane']['cap_kg']/1000:.0f}", "S[7]")])
    yy = WRAP(s, 1141, yy + 18, "Rev A had the LRC suction at 0.0909 bar(a), below atmospheric (air-ingress route); Rev B MR suction is 3.5 bar(a) (A), which removes that route. Not quantified: release rate, cloud size, VCE overpressure, BLEVE (need line size, hole size, congestion, ignition probability, vessel fire exposure).", 78, 10, 12.4, RED)
    y = scen_head(s, 1135, yy + 10, 445, "D", "Fire at the liquefaction train")
    yy = WRAP(s, 1141, y + 16, "An ignited leak at K-301 or E-202 heats neighbouring equipment. The propane receiver V-102 and the bullets are the escalation targets; the cold end must be depressurised and isolated while fire water cools the exposed steel.", 78, 10, 12.4)
    yy = kv_table(s, 1135, yy + 6, [
        (f"V-102: {S['v102']['dia_mm']:,.0f} mm x {S['v102']['len_m']:.1f} m, {S['v102']['vol']:.0f} m3, propane (t)", f"{S['c3_charge_kg']/1000:.0f}", "D"),
        ("K-301 / K-202 shaft power (kW)", f"{S['lrc']['W']:,.0f} / {S['pmr']['W']:,.0f}", "S[3]"),
        ("A-201 condensing duty (kW)", f0(BAL["Q_A201"]), "D"),
        ("LRC charge in the loop (t)", f"{BAL['lrc_charge_kg']/1000:.0f}", "D")])
    yy = WRAP(s, 1141, yy + 18, "Not quantified: flame length, radiant flux, impingement time, fire-case relief and fire-water demand (need layout, wetted areas, PFP rating, structural data). No distances are given on this sheet.", 78, 10, 12.4, RED)
    y = section(s, 1135, 700, 445, "TOOLKIT USE")
    for ln in ("process_safety has jet-fire, BLEVE and relief modules; none was run here because the repo gives no line sizes, hole sizes or layout, and a number without them would be invented.",
               "Documented values only: the repo inventories on this sheet."):
        y = WRAP(s, 1141, y + 16, ln, 78, 10, 12.4) - 2
    yb = section(s, 20, 784, 1100, "SCENARIO TABLE (green numbers on the drawing are the safeguards listed in the table)")
    rows = [("B  Refrigerant release", "Seal, flange or line leak on the propane discharge header (B1) or the ethane bullet outlet (B2); MR line leak; frequency and hole size not available",
             "Flashing jet, flammable cloud, flash fire, vapour cloud explosion in congested train, jet fire, BLEVE under fire exposure; cold burns (ethane -15 C); air ingress at LRC suction",
             "1 gas AT-301A/B and flame BE-301 detection to ESD-301 (A); 2 ESD-301 closes XV-201 and trips K-201, K-202, K-301 (A); 3 BDV-301 blowdown to flare F1 (A); 4 PSV-201 on V-102 (A); 5 XV-701, XV-702 on bullet outlets (A)",
             "Line sizes and pressures, hole sizes, congestion and layout, wind, ignition probability, real MR composition and loop pressures, bullet fire exposure"),
            ("D  Train fire", "Ignited leak at K-301 or E-202; external pool fire",
             "Flame impingement and radiation on V-102 (propane charge, see table), V-301, A-201, MCHE and supports; escalation to BLEVE; loss of structure",
             "1 detection and 2 ESD-301 as B; 3 BDV-301 depressurises to flare; 6 deluge DLG-301 and DLG-302, fire-water ring main (A); 7 PFP on V-102 supports (A)",
             "Layout and spacing, wetted areas, fire-case relief sizing, fire-water demand, PFP rating, structural response, ignition frequency")]
    scen_table(s, yb, rows)
    return s




# =====================================================================================================================
# Rev B sheets
# =====================================================================================================================
from process_safety import relief as RL


def size_relief():
    wz = comp_mass(S["z"]); M_ng = 1.0 / sum(wz[k] / MW[k] for k in wz)
    out = {}
    P1 = RL.relieving_pressure_kpa(5500.0, "single_non_fire")
    r = RL.gas_area(S["m_sweet"] * 3600, 298.15, P1, 400.0, M_ng, TH["gamma_NG"], Z=TH["Z_NG"], set_g_kpa=5500.0)
    out["blocked"] = r
    v = BAL["v102"]; Dm = v["dia_mm"] / 1000
    A = RL.wetted_area_cylinder(Dm, v["len_m"], 0.7 * Dm, "horizontal", 0.0)
    W = RL.fire_relief_rate_kg_h(A, TH["hfg_C3_14bar"], 1.0, True)
    P1f = RL.relieving_pressure_kpa(1700.0, "fire")
    rf = RL.gas_area(W, TH["T_C3_15bar"], P1f, 400.0, TH["MW_C3"], TH["gamma_C3"], Z=1.0, set_g_kpa=1700.0)
    out["v102"] = (A, W, rf)
    P1t = RL.relieving_pressure_kpa(25.0, "single_non_fire")
    des = BAL["k501"]["design"] * 3600
    rt = RL.gas_area(des, S["k501"]["Ts"], P1t, 106.3, S["tank"]["bog_mw"], 1.3, Z=1.0, set_g_kpa=25.0)
    out["tank"] = (des, rt)
    return out


RELS = size_relief()


def fm(x): return f"{x:,.0f}"


def rel_status():
    r = RELS["blocked"]; A, W, rf = RELS["v102"]; des, rt = RELS["tank"]
    return {
        "blocked": f"sized, blocked outlet, gas {S['m_sweet']*3.6:.0f} t/h at 55 barg set: {fm(r.required_area_mm2)} mm2 = orifice {r.orifice} x{r.n_valves} (toolkit gas_area; k {TH['gamma_NG']:.2f}, Z {TH['Z_NG']:.2f} CoolProp); applies only if the feed source can exceed design pressure",
        "v102": f"sized, fire: wetted {A:.0f} m2, {W:,.0f} kg/h propane, {fm(rf.required_area_mm2)} mm2 = orifice {rf.orifice} x{rf.n_valves} (toolkit; latent heat at 15 bar, Z=1, set 17 barg A)",
        "tank": f"partly sized: compressor-trip case only, {des:,.0f} kg/h BOG, {rt.required_area_mm2:,.0f} mm2 = orifice {rt.orifice}; NOT governing: rollover, ship-loading displacement, vacuum and roof fire cases not sized (need cargo, API 620/EN 14620 basis)"}


def relief_sheet():
    s = Sheet(5, "Safety design basis 1 of 3: relief schedule", "Relief schedule, every pressure item on sheet 1", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case; Rev B 11 Nov 2026")
    frame(s, 7)
    st_ = rel_status()
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE (R required by a named free source, A assumed here, gap = standard not obtained). Design pressures are ASSUMED (A): the repo gives none.")
    NS = "not sized: needs "
    rows = [("Item", "Design pressure basis (A)", "Relief case(s)", "Device and tag", "Discharge", "Sizing status"),
            ("V-101 inlet separator", "55 barg, 10 % over 50 bar(a) (A)", "fire (gas-filled), blocked outlet, control-valve failure LV-101 open (gas blow-by to condensate line)", "PSV-101; LSHH-101 trip (SIF-4)", "F1 warm flare (A)", st_["blocked"] + "; fire case " + NS + "vessel wall data (API 521 gas-filled: gap)"),
            ("T-301 amine absorber", "55 barg (A)", "blocked gas outlet, fire, loss of amine (gas blow-by), tube/regen. circuits not drawn", "PSV-301", "F1 (A)", "same gas basis as V-101 (not repeated); " + NS + "amine loop design"),
            ("V-201A/B mol-sieve beds", "55 barg; regen. 5,456 kW heater (S)", "blocked outlet, fire, regeneration-gas valve failure, thermal expansion of trapped gas in isolated bed", "PSV-211A, PSV-211B", "F1 (A)", "gas basis as V-101; " + NS + "regen. circuit pressure and heater trip basis"),
            ("A-101 air cooler", "55 barg (A)", "blocked in, fire: gas only, no trapped liquid", "none (protected by PSV-211A/B upstream); reason R-gas", "-", "reason: gas-filled, same design pressure as neighbours (A)"),
            ("E-201 propane chillers (4 levels)", "tube side 55 barg NG; shell 17 barg propane (A)", "tube rupture (NG 50 bar into propane shell), blocked propane outlet, fire, thermal expansion", "PSV-202 (shell)", "F1 (A)", NS + "tube-rupture load: tube data and API 521 / 520 rules (gap); shell case not sized"),
            ("E-202 MR precooler", "MR side 50 bar(a) tube; propane shell 17 barg (A)", "tube rupture, blocked outlet, fire, thermal expansion", "PSV-304", "F1 (A)", NS + "tube data"),
            ("A-201 propane condenser", "17 barg (A)", "blocked outlet, fire, cooling-water or air loss: loop heat input " + f"{BAL['Q_A201']/1000:.0f} MW", "PSV-203", "F1 (A)", NS + "loss-of-cooling relief rate (heat input to relieve = A-201 duty is the upper bound) and condenser data"),
            ("V-102 propane receiver", "17 barg (A)", "external fire, blocked outlet XV-201 closed, loss of cooling, thermal expansion", "PSV-201", "F1 (A)", st_["v102"]),
            ("V-301 MR separator", "55 barg (A)", "fire, blocked outlet, loss of MR cooling, thermal expansion", "PSV-302", "F2 cold flare (A)", NS + "vessel size and MR composition"),
            ("A-301 MR coolers", "55 barg (A)", "blocked in, loss of cooling, tube leak", "PSV-305", "F1 (A)", NS + "cooler data"),
            ("E-301 MCHE, MR shell", "MR 50 bar(a) (A)", "tube (NG to shell) leak, blocked MR outlet, cold-end blocked-in liquid thermal expansion", "PSV-303", "F2 (A)", NS + "cold-box data (licensor); NG tube side is covered by the feed-side PSVs only while FCV-401 is open: gap, thermal relief on trapped cold LNG not drawn"),
            ("V-401 end-flash drum", "6 barg (A, over 4.5 bar(a) operating)", "blocked flash-gas outlet (K-401 trip), LV-401 failure open (gas to tank), FCV-401 failure open, fire", "PSV-401; LSLL-401 trip (SIF-5)", "F2 (A)", NS + "valve Cv data: FCV-401 full-open gas flow at 50 bar governs; not sized"),
            ("TK-501 LNG tank", "A: low-pressure tank, API 620 / EN 14620 class (gap)", "BOG compressor trip, rollover, ship-loading displacement, fill-valve failure, vacuum from pump-out, roof fire", "PSV-501A, PSV-501B (2 x 100 %, A) incl. vacuum breaker (A)", "FL-601 via KOD (A)", st_["tank"]),
            ("ST-701 propane bullets", "17 barg (A)", "fire, blocked outlet, thermal expansion between XV-701 and the vessel", "PSV-701 (per bullet)", "F1 (A)", NS + "bullet wetted area (3 more bullets same); fire sizing as V-102 would apply (not repeated)"),
            ("ST-702 ethane bullets", "29.6 bar design (S[7]), -15 C", "fire, blocked outlet, thermal expansion", "PSV-702 (per bullet)", "F1 (A)", NS + "latent heat of ethane at relieving pressure"),
            ("NGL-801 stabiliser (3 columns)", "stub in repo", "reflux failure, fire, blocked overhead", "to be defined (stub)", "F1 (A)", NS + "column design (not in the repo)"),
            ("H-201 regen. heater, amine regen.", "stub in repo", "tube leak, blocked outlet, fire", "to be defined (stub)", "F1 (A)", NS + "circuit not defined"),
            ("K-201 / K-202 / K-301A-C / K-401 / K-501A/B", "casing = discharge system rating", "blocked discharge, seal failure", "none on casings: discharge protected by PSV-203 / PSV-201 (propane), PSV-302 / PSV-305 (MR), PSV-401 (flash gas), PSV-501A/B (BOG); BDV-301", "F1 / F2", "reason R: compressor casings are protected through the downstream vessel PSV (OSHA PSM requires the design basis as process safety information, S5)"),
            ("Flare header F1, F2, KOD, FL-601", "A", "all relief cases at once, cold relief into a warm header (brittle fracture)", "-", "FL-601", NS + "simultaneous load, cold-flare material (cryogenic: F2 separate from F1 is A), back pressure: gap")]
    ytab = wtable(s, 20, y, (150, 190, 330, 235, 120, 535), rows, 11, 13.2, 3.5)
    yy = section(s, 20, ytab + 10, 780, "BASIS OF THE SIZED ROWS (toolkit process_safety/relief.py)")
    for ln in ("API 520 Part I gas equation re-derived in the toolkit (tests check it against the published SI constants); the standard text itself is paywalled and was not read: gap (confirm Kd, back-pressure and accumulation against your edition).",
               "Accumulation 10 % single, 21 % fire (toolkit ACCUMULATION, secondary-source values: verify). Fire heat input C F A^0.82 with C = 43,200 W (drainage and fire fighting, A) and F = 1.0 bare vessel.",
               "Flare back pressure taken as 400 kPa abs for sizing (A); relieving temperatures are operating temperatures (A). Not sized rows are open items for the licensor and vessel vendor."):
        yy = WRAP(s, 26, yy + 14, ln, 128, 11, 13.4) - 2
    y2 = section(s, 820, ytab + 10, 760, "DISCHARGE AND CRYOGENIC NOTES")
    for ln in ("Discharge location is a design item: CSB Kuraray (S11): horizontal discharge near workers was the cause of injury. All PSV outlets here go to closed headers F1/F2 (A); no atmospheric discharge is drawn.",
               "Cold relief (F2: LNG vapour, MR below -100 C) must not enter a carbon-steel warm header: separate cold header in austenitic or 9 % Ni material is assumed (A, qualitative); material class not selected.",
               "Vacuum: TK-501 and LRC-type suction systems below atmospheric need vacuum relief or low-pressure trips: breaker on TK-501 (A); MR suction is now 3.5 bar(a) so the Rev A vacuum is gone."):
        y2 = WRAP(s, 826, y2 + 14, ln, 126, 11, 13.4) - 2
    return s


def esd_sheet():
    s = Sheet(6, "Safety design basis 2 of 3: ESD cause-and-effect and SIF list", "ESD matrix and safety instrumented functions", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case; Rev B 11 Nov 2026")
    frame(s, 7)
    y = section(s, 20, 84, 1560, "ESD CAUSE-AND-EFFECT MATRIX (X = action; every tag is drawn on sheet 1; logic is assumed, A; fail position of all XV: close, BDV: open, DLG: open on signal)")
    fe = ["XV-101", "XV-201", "XV-501", "XV-502", "XV-503", "XV-504", "XV-701/2", "P-501", "K-201/202", "K-301", "K-401/501", "BDV-301", "DLG-301/2"]
    ini = [("AT-101 gas det. feed/AGRU (2oo3 A)", "XV-101 XV-201"), ("AT-201 gas det. compressor area", "XV-201 K-201/202 K-301 BDV-301 DLG-301/2"),
           ("AT-301A/B gas det. MR/C3 train", "XV-201 XV-701/2 K-201/202 K-301 BDV-301 DLG-301/2"), ("BE-301 flame det. train", "XV-201 XV-701/2 K-201/202 K-301 BDV-301 DLG-301/2"),
           ("AT-401 gas det. cold box", "XV-201 K-301 BDV-301"), ("AT-701 gas det. refrigerant storage", "XV-701/2"),
           ("AT-501 gas det. tank area", "XV-501 XV-502 XV-503 XV-504 P-501"), ("TSL-501 cold-spill detector", "XV-501 XV-502 XV-503 XV-504 P-501"),
           ("LSHH-101 V-101 high-high level", "XV-101"), ("LSLL-401 V-401 low-low level", "K-401/501"), ("PT-301 K-301 discharge PAHH", "K-301 BDV-301"),
           ("PT-501 PAHH tank pressure", "XV-501 XV-503 K-401/501"), ("PT-501 PALL tank vacuum", "P-501 K-401/501"), ("LT-501 LAHH tank level", "XV-503 XV-501"),
           ("Loss of instrument air / power", "XV-101 XV-201 XV-501 XV-502 XV-503 XV-504 XV-701/2 (fail closed) BDV-301 (fail open)"), ("ESD-301 / ESD-501 manual push button", "all above")]
    rows = [("Initiator",) + tuple(fe)]
    for name, acts in ini:
        if acts == "all above": rows.append((name,) + tuple("X" for _ in fe)); continue
        a = acts.replace("(fail closed)", "").replace("(fail open)", "")
        rows.append((name,) + tuple("X" if (f in a or (f == "K-401/501" and "K-401/501" in a) or (f == "BDV-301" and "BDV-301" in a)) else "" for f in fe))
    colw = (250,) + (96,) * len(fe)
    yt = wtable(s, 20, y, colw, rows, 11, 13.2, 3.5)
    yy = WRAP(s, 26, yt + 12, "Source basis: PSM operating procedures must cover emergency shutdown conditions and who acts (OSHA 1910.119, S5, R); isolating valves must close quickly and stay safe on power loss, ROSOV (HSE HSG176 para 128, S1, R). 49 CFR 193: control centre protected so it stays operational (S9, R). Voting, timing and fail positions are A. Detector counts and positions per hazard study: gap (NFPA 72 / ISA 84 not obtained).", 215, 11, 13.4)
    y = section(s, 20, yy + 6, 1560, "SAFETY INSTRUMENTED FUNCTIONS (SIL targets are ASSUMED (A): no SIL verification, no LOPA performed; IEC 61511 and LOPA texts not obtained: gap)")
    srows = [("SIF", "Function (initiator -> final element)", "Demand source", "Independent layers credited (A)", "SIL target (A)", "Free source / tag"),
             ("SIF-1", "PT-501 PAHH -> close XV-503 and XV-501, trip K-401 (stop adding vapour/liquid)", "BOG compressor trip or fuel-header back pressure", "PSV-501A/B; BPCS PIC alarm (A)", "SIL 1 (A)", "S2 separation, S5; A"),
             ("SIF-2", "LT-501 LAHH -> close XV-503 (tank fill)", "fill-control failure, ship/ train mismatch", "PSV-501A/B only for vapour; independent level transmitter (A)", "SIL 2 (A)", "S1 overfill/ROSOV, S2; A"),
             ("SIF-3", "PT-501 PALL -> stop P-501 and K-501 suction", "pump-out without vapour return, barometric fall", "vacuum breaker on PSV-501A/B (A)", "SIL 1 (A)", "A; gap (API 620 vacuum basis)"),
             ("SIF-4", "LSHH-101 -> close XV-101", "liquid carry-over to AGRU, MCHE freeze-out risk", "BPCS LIC-101 alarm (A)", "SIL 1 (A)", "S2 (BP-Husky S10: SIS credited yet failed, so verify)"),
             ("SIF-5", "LSLL-401 -> trip K-401/501 and close LV-401", "gas blow-by from V-401 to TK-501 (LIC-401 failure)", "PSV-501A/B, BPCS LIC-401 (A)", "SIL 1 (A)", "S2; A"),
             ("SIF-6", "PT-301 PAHH -> trip K-301, open BDV-301", "blocked MR discharge, surge", "PSV-302/305 (A)", "SIL 1 (A)", "S5, S11 (discharge location)"),
             ("SIF-7", "AT-301A/B, AT-201, BE-301 -> ESD-301: close XV-201, XV-701/2, trip K-201/202, K-301, open BDV-301, start DLG-301/2", "refrigerant release, ignited leak", "gas/flame detection is the layer; deluge and PFP (A)", "SIL 2 (A)", "S4 leak detection preferred to flame alone; S8; A"),
             ("SIF-8", "AT-501, TSL-501 -> ESD-501: close XV-501/502/503/504, trip P-501", "LNG release at transfer line or roof nozzle", "impoundment 110 % (R, S9), no drain to water (A)", "SIL 2 (A)", "S9 impoundment; S1 ROSOV"),
             ("SIF-9", "AT-401 -> close XV-201, trip K-301, open BDV-301", "cold-box (MCHE) leak of MR or LNG", "cold-box purge (A, not drawn)", "SIL 1 (A)", "A; gap (licensor)")]
    wtable(s, 20, y, (50, 470, 260, 330, 90, 360), srows, 11, 13.2, 3.5)
    return s


def haz_sheet():
    s = Sheet(7, "Safety design basis 3 of 3: detection, mitigation, hazard identification, inherent safety", "Detection, mitigation, HAZOP nodes, ISD", code="VS-LNG", project="LNG liquefaction plant (repo default 2.0 mtpa case)",
              basis="lng-design-opensource default case; Rev B 11 Nov 2026")
    frame(s, 7)
    y = section(s, 20, 84, 1560, "DETECTION AND MITIGATION (R required by a named free source, A assumed, gap = controlling standard not obtained)")
    imp = BAL["imp_check"]
    lines = [("Spill containment / impoundment", f"Impoundment volume {imp:,.0f} m3 = 1.10 x net tank volume {S['tank']['V']:,.0f} m3 (single tank, no surge allowance), basis 49 CFR 193.2181 as read in the toolkit docstring (S9, R). Trench and sump from loading line, transfer pumps and process area to the impoundment: layout and slope A. No drain to water or open sea (A). Remote impoundment sump, high-expansion foam: gap (NFPA 11/59A not obtained)."),
             ("Exclusion zones (Rev A had none)", "Basis stated, distances NOT calculated: 49 CFR 193.2057 requires thermal radiation exclusion zones from a design spill with the GTI LNGFIRE3 model (R); 193.2059 requires vapour dispersion to 2.5 % average concentration, receptor 0.5 m, roughness 0.03 m, stability F, wind 2.01 m/s, humidity 50 % using DEGADIS or an equivalent validated model (R). The toolkit's neutral-gas Gaussian dispersion is not valid for cold LNG vapour (its docstring) and is not used. NFPA 59A-2001 sections 2.2.3.2 to 2.2.3.4 (incorporated by the rule): gap. Needs: design spill rate and duration from line sizes, site wind and plot plan."),
             ("Cryogenic embrittlement and RPT", "LNG, cold MR (below -100 C) and ethane at -15 C: carbon steel is not acceptable in cold service; austenitic stainless steel, 9 % Ni steel or aluminium for cold lines, cold box and tank inner (A, qualitative); no drip trays or open drains where LNG could reach water, which is the rapid phase transition condition (A). Material standards (EN 14620, API 620 Annex Q, 49 CFR 193 materials): gap."),
             ("BOG, overpressure and vacuum", f"TK-501 vapour: BOG {BAL['bog']:.3f} kg/s at 0.05 %/day; K-501A/B 1 + 1 spare (S[6]); PSV-501A/B with vacuum breaker; PT-501 PAHH/PALL (SIF-1, SIF-3). Pressure-rise upper bound if all BOG is retained {BAL['dPdt_Pa_s']:.2f} Pa/s (D9). Ship-loading vapour return and rollover loads: not sized. MR suction vacuum of Rev A removed (3.5 bar(a))."),
             ("Fire protection", "Fire water: deluge DLG-301/302 on the train (A); PFP on V-102 and compressor structure supports (A). Fire-water demand not computed: toolkit fire_water.py provides density x area demand but areas and duration are not defined (needs layout). HSL fire-pressure-system guidance (S13, R) applies to V-102, V-301 and the bullets: PRV cycling in fire."),
             ("Isolation of large inventories", "ROSOV on large inventories (HSG176 para 128, S1, R): XV-501, 502, 503, 504 (tank and jetty), XV-201 (propane receiver outlet), XV-701/702 (bullets), XV-101 (feed). Largest isolatable inventories: TK-501 27,296 t (S), propane in V-102 about " + f"{BAL['v102_charge']/1000:.0f} t (D), MR charge about {BAL['lrc_charge_kg']/1000:.0f} t (D, Rev A repo charge)."),
             ("Gas and flame detection logic", "Gas detectors at release points: compressor hall (AT-201, AT-301A/B), cold box (AT-401), feed/AGRU (AT-101), storage (AT-701), tank area (AT-501) plus TSL-501 cold-spill detector; flame detector BE-301. Leak (gas) detection preferred for hard-to-see flames (EIGA, S4; R for hydrogen, A here); fertilizer guideline asks for detectors in hazard areas (S8, R). Counts, voting and alarm set points: gap."),
             ("Layout and safety distances", "Layout shall address domino escalation and occupied buildings (HSE COMAH plant layout, S3, R). Control centre sited or protected to stay operational (49 CFR 193, S9, R). Distances: A, not calculated; HSG176 Table 1 spacing is for small flammable liquid tanks and does not apply to LNG (S1).")]
    yy = wtable(s, 20, y, (230, 1330), [("Item", "Basis and status")] + lines, 11, 13.2, 3.5)
    y2 = section(s, 20, yy + 8, 1560, "HAZARD IDENTIFICATION (HAZOP-style nodes; qualitative: no numeric consequences, no risk ranking; PHA incl. facility siting is required by OSHA 1910.119, S5, R)")
    hz = [("Node", "Deviation", "Cause", "Consequence", "Safeguard", "Action"),
          ("N1 Feed, V-101, T-301", "More level / liquid carry-over", "slug from pipeline, LV-101 stuck", "liquids to AGRU and MCHE", "LIC-101, LSHH-101 SIF-4, XV-101", "confirm slug catcher need (A)"),
          ("N2 Mol sieve V-201A/B", "Less drying, more water", "regeneration failure, wet gas", "ice/hydrate in cold box, blocked MCHE", "regen. gas circuit stub; dew-point analyser not drawn", "add moisture analyser and trip (A)"),
          ("N3 Propane train K-201/202, A-201, V-102", "More pressure / loss of cooling", "condenser fouling, fan or water loss", "PSV-203/201 lift, flare load", "PSV-203, PSV-201, SIF-6 analogue, BDV-301", "size loss-of-cooling load (open)"),
          ("N4 MR loop K-301, A-301, V-301", "Less flow / surge, liquid at suction", "stage trip, cold return slug", "compressor damage, loss of refrigeration", "PT-301 SIF-6, BDV-301", "add suction drums per casing (not drawn: gap)"),
          ("N5 Cold box E-301", "Other than: CO2 or water in feed", "T-301 or V-201 upset", "freeze-out, blocked channels, thermal stress", "AT-401, SIF-9; CO2 solids data not quantified", "CO2 solubility limit (open)"),
          ("N6 V-401 end flash, FCV-401", "More gas to tank / reverse", "LV-401 fails open", "gas into TK-501, overpressure", "LSLL-401 SIF-5, PSV-401", "confirm LV-401 fail position (A)"),
          ("N7 TK-501 and BOG", "More pressure / less pressure", "K-501 trip, rollover, pump-out, ship loading", "PSV lift to flare, or vacuum", "PSV-501A/B, SIF-1, SIF-3, TT-501 profile", "rollover and ship-vapour loads (open)"),
          ("N8 Loading line L-501, XV-504", "More flow / loss of containment", "arm failure, drive-off, hose rupture", "LNG pool, vapour cloud, brittle fracture", "XV-501..504, TSL-501, impoundment, SIF-8", "ship-shore ESD link (gap)"),
          ("N9 Refrigerant storage ST-701/702", "More temperature / fire", "external fire, solar", "BLEVE-type vessel failure", "PSV-701/702, AT-701, XV-701/702", "mounding or fire protection (A)")]
    yh = wtable(s, 20, y2, (220, 200, 250, 280, 360, 250), hz, 11, 13.2, 3.5)
    y3 = section(s, 20, yh + 8, 1560, "INHERENTLY SAFER DESIGN NOTES")
    isd = ["Reduce inventory: mixed refrigerant held in the loop and 1 x 261 m3 propane receiver (V-102) are the largest flammable refrigerant inventories; two smaller receivers and a smaller MR charge (A, no source) would reduce a single-event release.",
           "Moderate conditions: MR suction at 3.5 bar(a) (A) removes the vacuum that Rev A had and so the air-ingress route into a flammable mixture inside the loop (qualitative).",
           "Substitute / avoid: no ethylene or heavier refrigerant is used in this layout (repo uses ethane and propane); ethane bullets at -15 C instead of ambient storage lower vapour pressure (S[7]).",
           "Simplify: one cold-box shell and one MR loop for the whole cold end (Rev B) replaces the separate unsized subcooling loop; fewer interconnections.",
           "Limit consequences: all relief to closed headers (CSB Kuraray, S11), impoundment at the tank, no drains to water (A), full-containment tank class would remove the dyke-surge case (A, standard not obtained: gap)."]
    for ln in isd: y3 = WRAP(s, 26, y3 + 14, ln, 240, 11, 13.4, bullet=True) - 2
    return s


def build_all():
    return [sheet1(), sheet2(), sheet3(), sheet4(), relief_sheet(), esd_sheet(), haz_sheet()]


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, "LNG P&ID set Rev B", previews="--previews" in sys.argv)
    print("ok", len(sheets))

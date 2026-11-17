#!/usr/bin/env python3
"""Generate the fruit and vegetable processing plant (10,000 t/yr) conceptual P&ID set: P&ID, heat and material balance,
four food-safety / utility scenarios.

Source: VertiStrat_DPR_Templates/Template_DPR_FoodProcessing_FruitVeg_10000tpa.docx (a TEMPLATE with illustrative figures).
Tags used on every number: S = sourced (file and section named), D = derived (formula shown), A = assumed by this drawing.
Atomic masses are not needed; physical property values (cp, latent heats, steam table values) are typed here as A inputs,
not as facts, and must be checked against a cited table before any use.

Usage (standard library only, Python 3.10+):
    python3 scripts/gen_pid_fruitveg.py docs/pid/FRUITVEG_PID_Set_RevB.html [--previews]
Screening aid, not certified design."""
import sys, os, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pidlib import *

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from process_safety import relief as RELIEF      # stdlib toolkit package: API 520 steam area, API 521 fire case (texts not read)
except Exception:
    RELIEF = None


class SheetB(Sheet):
    """pidlib frame() prints 'Rev A' / 'Draft A'; Rev B overrides both in the SVG string (pidlib is not edited)."""
    def svg(self):
        return super().svg().replace("|  Rev A", "|  Rev B").replace("Draft A.", "Draft B.")


Sheet = SheetB

SRC = "Template_DPR_FoodProcessing_FruitVeg_10000tpa.docx"
STM, CHW, REF, EFF, AIRC = "#b26a00", "#00838f", "#6a1b9a", "#6d4c41", "#546e7a"

# =====================================================================================================
# 1. HEAT AND MATERIAL BALANCE (computed here; sheets only print what this section returns)
# =====================================================================================================
NS = 8                                              # number of sheets in the Rev B set


# ---- ice cp: IAPWS R10-06(2009) Gibbs-energy equation for ice Ih, Eq. (6) cp = -T gTT, gTT from Table 4, coefficients of Table 2,
# evaluated at normal pressure p0 (only r20 of r2(p) survives). Document read: https://iapws.org/technical-guidance/release/Ice-2009.download
# Check value of Table 6 (cp = 2096.71391024 J/kg/K at 273.152519 K, 101325 Pa) is reproduced to 1e-9 (asserted below). Standard library only.
_Tt = 273.16
_t1, _r1 = complex(0.368017112855051e-1, 0.510878114959572e-1), complex(0.447050716285388e2, 0.656876847463481e2)
_t2, _r20 = complex(0.337315741065416, 0.335449415919309), complex(-0.725974574329220e2, -0.781008427112870e2)


def ice_cp_kj(T_K):
    tau = T_K / _Tt
    g_tt = sum(r * (1 / (t - tau) + 1 / (t + tau) - 2 / t) for r, t in ((_r1, _t1), (_r20, _t2))).real / _Tt
    return -T_K * g_tt / 1000.0                       # kJ/kg/K


assert abs(ice_cp_kj(273.152519) - 2.09671391024) < 1e-8


def ice_cp_mean(T_lo_C, T_hi_C, n=2000):
    return sum(ice_cp_kj(273.15 + T_lo_C + (T_hi_C - T_lo_C) * (i + .5) / n) for i in range(n)) / n


# ---- Rev A outputs, frozen from the Rev A generator (git history, run 2026-11-11) for the "Rev A to Rev B changes" box
REV_A = dict(q_b201=201.83, q_b401=48.24, q_pas_hf=18.46, q_pas_as=25.97, q_e402=34.58, q_frz=40.10, q_ref=50.12, steam_dir=381.04,
             steam_ind=74.99, steam_tot=456.03, q_boil_out=298.5, q_fuel=351.2, eff_m3h=10.446, cod_kgh=5.932, cod_mgl=567.9,
             dump_cod=251.6, pulp_tpy=6007.9, byp_tpy=1518.3, iqf_tpy=1829.3, T15=70.42, chw=135.96, fresh_m3t=5.112,
             cod_kgt=3.027, steam_t_frozen=0.1596, T34=40.0, prod_th=1.9593)

A = dict(
    h_per_day=20.0,                                   # A1 operating hours per day
    reject=0.03, soil=0.01,                           # A2 sort rejects (of consignment), adhering soil (of consignment)
    wash_kgkg=3.0, cip_kgkg=0.5,                      # A3 wash water and CIP / floor-wash water, kg per kg raw
    leach_wash=0.005, leach_blanch=0.01, leach_cool=0.003,   # A4 fruit mass leached to water
    split_pulp=0.75,                                  # A5 share of washed fruit to the pulp line (IQF share = 25 %: no source, tuned to template)
    by_pulp=0.14, by_iqf=0.22,                        # A6 peel/stone/pomace (pulp line, of blanched fruit); peel/trim (IQF, of fruit); crop input
    da_loss=0.015,                                    # A7 deaerator flash loss, of hot pulp
    hf_share=0.50,                                    # A8 hot-fill share of pasteurised pulp (rest aseptic)
    mu_kgkg=0.5, vent=0.10, hloss=0.15,               # A9 blancher make-up water kg/kg, steam lost as vapour, bath heat-loss allowance
    purge_kgkg=3.0,                                   # S Rev B: IQF cooler water, countercurrent drum cooler 2-4 L/kg (BREF sec 8.2.2.4); mid value. Rev A 0.3 (A12)
    cool_approach=5.0,                                # A Rev B: drum-cooler product exit = ambient + 5 K (water stage), CHW trims to 10 C
    frost=0.005,                                      # A12 frost/defrost loss
    peel_cod_kgt=36.5,                                # S Rev B: kg COD per t product, abrasion + knife peeling, half pears (BREF Table 8.3); caustic 66.3 (Table 8.4)
    peel_conc_mgl=5000.0,                             # S Rev B: peeling wastewater COD, mechanical peeling about 5,000 mg/L (steam 4,000) (BREF sec 8.2.1)
    peel_share_iqf=1.0, peel_share_pulp=0.0,          # A Rev B: PE-401 peels/cuts the whole IQF line; the pulp line is not peeled (crop open)
    Ta=28.0, Tb_pulp=90.0, Tb_iqf=85.0, T_pulper=80.0,     # A10 temperatures, deg C
    T_hf=95.0, T_as=105.0, T_hf_cool=35.0, T_as_cool=30.0, T_iqf_cool=10.0, T_frozen=-18.0,
    cp_dm=1.2,                                        # A Rev B: cp of fruit dry matter (sugar-class solids), range 1.2-1.5 kJ/kg/K
    cp_w=4.18,                                        # A11 water
    xw=0.85, x_frz=0.85, Tfp=-1.5,                    # A11 water fraction, frozen water fraction, freezing point
    Lf=333.4,                                         # S Rev B: latent heat of fusion at the triple point, 333.444 kJ/kg (IAPWS R10-06 Table 6, h of ice at Tt)
    hfg=2133.4, Tsat=143.6,                           # tool: CoolProp 8.0, water at 4.0 bar(a): Tsat 143.608 C, hfg 2133.398 kJ/kg (frozen)
    hfg_vac=2357.5,                                   # tool: CoolProp 8.0, water at 0.2 bar(a): hfg 2357.513 kJ/kg (frozen); Rev A 2300 (A)
    refr_over=0.25, boil_eff=0.85, T_feed=80.0,       # A12 refrigeration overhead, boiler efficiency, boiler feed T
    cod=1.1,                                          # A13 kg COD per kg fruit dry matter
    cop_lo=1.56, cop_hi=1.76,                         # tool: CoolProp 8.0 R717 (ammonia, a CONDITIONAL case) single stage, eta_is 0.7, saturated suction, saturated liquid at 35 C
    #                                                   (A), evaporating -40 C -> COP 1.56, -35 C -> 1.76 (recomputed in this session, matches validation 1.56-1.76)
    bref_kwh_lo=80.0, bref_kwh_hi=280.0,              # S: BREF sec 8.1 deep freezing, kWhe per t frozen vegetables (fans and auxiliaries included)
)
A["cp_ice"] = ice_cp_mean(A["T_frozen"], A["Tfp"])     # S: IAPWS R10-06 mean over -18 .. -1.5 C (2.025 kJ/kg/K); Rev A 1.9 (A)
A["cp_f"] = A["xw"] * A["cp_w"] + (1 - A["xw"]) * A["cp_dm"]     # D: 3.733; Rev A 3.6 (A)
S_RAW_T, S_TPD, S_PULP_T, S_BYP_T = 10000.0, 50.0, 6000.0, 1500.0     # S: docx 1, 4, 9


def balance(a=A):
    days = S_RAW_T / S_TPD                       # D: 10,000 t/yr / 50 t/d = 200 d
    hrs = days * a["h_per_day"]
    st = {}

    def fr(m): return (m * a["xw"], m * (1 - a["xw"]), 0.0)      # fruit composition (water, dry matter, soil)

    def add(n, name, comp, T, P, ph, io):
        w, d, so = comp
        st[n] = dict(n=n, name=name, w=w, d=d, so=so, m=w + d + so, T=T, P=P, ph=ph, io=io)

    def vec(*parts):
        return tuple(sum(p[i] for p in parts) for i in range(3))

    m1 = S_RAW_T * 1000.0 / hrs                  # kg/h
    soil = a["soil"] * m1
    add(1, "raw F&V", (fr(m1 - soil)[0], fr(m1 - soil)[1], soil), a["Ta"], 1.01, "solid", "in")
    add(2, "sort rejects", fr(a["reject"] * m1), a["Ta"], 1.01, "solid", "out")
    add(3, "wash water", (a["wash_kgkg"] * m1, 0, 0), a["Ta"], 3.0, "liquid", "in")
    pre = m1 - soil - st[2]["m"]
    leach_w = a["leach_wash"] * pre
    add(4, "washed fruit", fr(pre - leach_w), a["Ta"], 1.01, "solid", "int")
    add(5, "wash effluent", vec((st[3]["w"], 0, 0), (0, 0, soil), fr(leach_w)), a["Ta"], 1.01, "liquid", "int")
    m6 = a["split_pulp"] * st[4]["m"]
    add(6, "fruit to pulp", fr(m6), a["Ta"], 1.01, "solid", "int")
    # ---- pulp line blancher B-201 (direct steam)
    mu7 = a["mu_kgkg"] * m6
    h_eff = a["hfg"] + a["cp_w"] * (a["Tsat"] - a["Tb_pulp"])           # kJ/kg steam delivered into bath at Tb
    q_b201 = (m6 * a["cp_f"] + mu7 * a["cp_w"]) * (a["Tb_pulp"] - a["Ta"]) * (1 + a["hloss"]) / 3600.0   # kW
    m8 = q_b201 * 3600.0 / h_eff
    add(7, "B-201 MU wtr", (mu7, 0, 0), a["Ta"], 3.0, "liquid", "in")
    add(8, "B-201 steam", (m8, 0, 0), a["Tsat"], 4.0, "vapour", "in")
    add(9, "B-201 vent", (a["vent"] * m8, 0, 0), 100.0, 1.01, "vapour", "out")
    lb = a["leach_blanch"] * m6
    add(10, "B-201 ovfl", vec((mu7 + m8 - st[9]["m"], 0, 0), fr(lb)), a["Tb_pulp"], 1.01, "liquid", "int")
    add(11, "blanched F&V", fr(m6 - lb), a["Tb_pulp"], 1.01, "solid", "int")
    add(12, "peel/stone", fr(a["by_pulp"] * st[11]["m"]), a["T_pulper"], 1.01, "solid", "out")
    hot = tuple(st[11][k] - st[12][k] for k in ("w", "d", "so"))
    add(13, "hot pulp", hot, a["T_pulper"], 1.01, "slurry", "int")
    daw = a["da_loss"] * st[13]["m"]
    add(14, "DA cond.", (daw, 0, 0), 60.0, 0.2, "liquid", "int")
    T15 = a["T_pulper"] - a["da_loss"] * a["hfg_vac"] / a["cp_f"]        # D: flash cooling
    add(15, "DA pulp", (hot[0] - daw, hot[1], hot[2]), T15, 3.0, "slurry", "int")
    sc = lambda k, f: tuple(st[k][i] * f for i in ("w", "d", "so"))
    add(16, "HF pulp 95C", sc(15, a["hf_share"]), a["T_hf"], 3.0, "slurry", "int")
    add(17, "AS pulp 105C", sc(15, 1 - a["hf_share"]), a["T_as"], 3.0, "slurry", "int")
    add(18, "HF packs", sc(15, a["hf_share"]), a["T_hf_cool"], 1.01, "slurry", "out")
    add(19, "AS bags", sc(15, 1 - a["hf_share"]), a["T_as_cool"], 1.01, "slurry", "out")
    # ---- IQF line
    m20 = st[4]["m"] - m6
    add(20, "fruit to IQF", fr(m20), a["Ta"], 1.01, "solid", "int")
    add(21, "IQF peel/trim", fr(a["by_iqf"] * m20), a["Ta"], 1.01, "solid", "out")
    pieces = m20 - st[21]["m"]
    mu22 = a["mu_kgkg"] * pieces
    q_b401 = (pieces * a["cp_f"] + mu22 * a["cp_w"]) * (a["Tb_iqf"] - a["Ta"]) * (1 + a["hloss"]) / 3600.0
    h_eff2 = a["hfg"] + a["cp_w"] * (a["Tsat"] - a["Tb_iqf"])
    m23 = q_b401 * 3600.0 / h_eff2
    add(22, "B-401 MU wtr", (mu22, 0, 0), a["Ta"], 3.0, "liquid", "in")
    add(23, "B-401 steam", (m23, 0, 0), a["Tsat"], 4.0, "vapour", "in")
    add(24, "B-401 vent", (a["vent"] * m23, 0, 0), 100.0, 1.01, "vapour", "out")
    lb2 = a["leach_blanch"] * pieces
    add(25, "B-401 ovfl", vec((mu22 + m23 - st[24]["m"], 0, 0), fr(lb2)), a["Tb_iqf"], 1.01, "liquid", "int")
    add(26, "blanched pcs", fr(pieces - lb2), a["Tb_iqf"], 1.01, "solid", "int")
    m26 = st[26]["m"]
    lc = a["leach_cool"] * m26
    # Rev B: E-402 = countercurrent drum cooler (water, S 2-4 kg/kg) then chilled-water trim to the freezer inlet temperature
    Tx = a["Ta"] + a["cool_approach"]                                   # A: product exit of the water stage
    q_drum = m26 * a["cp_f"] * (a["Tb_iqf"] - Tx) / 3600.0               # kW, to the cooling water
    w27 = a["purge_kgkg"] * m26
    T28 = a["Ta"] + q_drum * 3600.0 / (w27 * a["cp_w"])                  # D: cooling-water outlet temperature
    assert Tx < T28 < a["Tb_iqf"], T28
    add(27, "E-402 wtr in", (w27, 0, 0), a["Ta"], 3.0, "liquid", "in")
    add(28, "E-402 wtr out", vec((w27, 0, 0), fr(lc)), T28, 1.01, "liquid", "int")
    add(29, "cooled pcs", fr(m26 - lc), a["T_iqf_cool"], 1.01, "solid", "int")
    fw = a["frost"] * st[29]["m"]
    add(30, "defrost drain", (fw, 0, 0), 5.0, 1.01, "liquid", "int")
    add(31, "IQF product", (st[29]["w"] - fw, st[29]["d"], 0), a["T_frozen"], 1.01, "solid", "out")
    add(32, "CIP/washdown", (a["cip_kgkg"] * m1, 0, 0), a["Ta"], 3.0, "liquid", "in")
    add(33, "CIP effluent", (st[32]["w"], 0, 0), a["Ta"], 1.01, "liquid", "int")
    # ---- Rev B: peel / cut water. The stream is defined by the BREF COD load per t product (S) and the BREF peeling-water COD
    # concentration (S); its dissolved/suspended dry matter is taken out of the dry peel/trim by-product (streams 21, 12), so the
    # product yield is unchanged and mass still closes. Water = COD / concentration.
    cod_pi = a["peel_share_iqf"] * a["peel_cod_kgt"] * st[31]["m"] / 1000.0           # kg COD/h, IQF line (PE-401)
    cod_pp = a["peel_share_pulp"] * a["peel_cod_kgt"] * (st[18]["m"] + st[19]["m"]) / 1000.0
    dm_pi, dm_pp = cod_pi / a["cod"], cod_pp / a["cod"]
    assert dm_pi <= 0.9 * st[21]["d"] and dm_pp <= 0.9 * st[12]["d"], ("peel dry matter exceeds the by-product", dm_pi, st[21]["d"], dm_pp, st[12]["d"])
    st[21]["d"] -= dm_pi; st[21]["m"] -= dm_pi
    st[12]["d"] -= dm_pp; st[12]["m"] -= dm_pp
    w35 = (cod_pi + cod_pp) * 1e6 / a["peel_conc_mgl"]
    add(35, "peel/cut wtr in", (w35, 0, 0), a["Ta"], 3.0, "liquid", "in")
    add(36, "peel/cut effl", (w35, dm_pi + dm_pp, 0), a["Ta"], 1.01, "liquid", "int")
    effk = (5, 10, 14, 25, 28, 30, 33, 36)
    eff = vec(*[(st[k]["w"], st[k]["d"], st[k]["so"]) for k in effk])
    T34 = sum(st[k]["m"] * st[k]["T"] for k in effk) / sum(st[k]["m"] for k in effk)    # D: mass-weighted (equal cp) mix, replaces A 40 C
    add(34, "to ETP", eff, T34, 1.01, "liquid", "out")
    # ---- mass closure
    ins = [k for k in st if st[k]["io"] == "in"]
    outs = [k for k in st if st[k]["io"] == "out" and k != 34] + [34]
    mi, mo = sum(st[k]["m"] for k in ins), sum(st[k]["m"] for k in outs)
    comp = {c: (sum(st[k][c] for k in ins), sum(st[k][c] for k in outs)) for c in ("w", "d", "so")}
    assert abs(mi - mo) / mi < 1e-3, (mi, mo)
    for c, (ci, co) in comp.items(): assert abs(ci - co) <= 1e-3 * max(ci, 1e-9), (c, ci, co)
    # internal node checks (each unit closes on its own)
    assert abs(st[4]["m"] - st[6]["m"] - st[20]["m"]) < 1e-6
    assert abs(st[11]["m"] - st[12]["m"] - st[13]["m"] - dm_pp) < 1e-6
    assert abs(st[15]["m"] - st[16]["m"] - st[17]["m"]) < 1e-6
    assert abs(st[20]["m"] - st[21]["m"] - pieces - dm_pi) < 1e-6
    # ---- duties, kW
    cpf, cpw = a["cp_f"], a["cp_w"]
    q_pas_hf = st[16]["m"] * cpf * (a["T_hf"] - T15) / 3600.0
    q_pas_as = st[17]["m"] * cpf * (a["T_as"] - T15) / 3600.0
    q_cool_hf = st[16]["m"] * cpf * (a["T_hf"] - a["T_hf_cool"]) / 3600.0
    q_cool_as = st[17]["m"] * cpf * (a["T_as"] - a["T_as_cool"]) / 3600.0
    q_e402 = m26 * cpf * (Tx - a["T_iqf_cool"]) / 3600.0                  # chilled-water trim after the water stage
    m29 = st[29]["m"]
    sens_hi = cpf * (a["T_iqf_cool"] - a["Tfp"])
    latent = a["xw"] * a["x_frz"] * a["Lf"]
    cp_frozen = a["xw"] * a["x_frz"] * a["cp_ice"] + a["xw"] * (1 - a["x_frz"]) * cpw + (1 - a["xw"]) * a["cp_dm"]   # D: frozen-product cp
    sens_lo = cp_frozen * (a["Tfp"] - a["T_frozen"])
    q_frz = m29 * (sens_hi + latent + sens_lo) / 3600.0
    q_ref = q_frz * (1 + a["refr_over"])
    iqf_th = st[31]["m"] / 1000.0
    kwe = (q_ref / a["cop_hi"], q_ref / a["cop_lo"])
    steam_ind = (q_pas_hf + q_pas_as) * 3600.0 / a["hfg"]
    steam_dir = m8 + m23
    steam_tot = steam_dir + steam_ind
    q_boil_out = (steam_dir * (a["hfg"] + cpw * (a["Tsat"] - a["T_feed"])) + steam_ind * a["hfg"]) / 3600.0
    q_fuel = q_boil_out / a["boil_eff"]
    dm_eff = eff[1]
    cod_kgh = dm_eff * a["cod"]
    cod_iqf_line = cod_pi + (st[25]["d"] + st[28]["d"]) * a["cod"]
    dump_cod = st[15]["m"] * (st[15]["d"] / st[15]["m"]) * a["cod"]       # one hour of pulp dumped (D, illustration)
    prod_th = (st[18]["m"] + st[19]["m"] + st[31]["m"]) / 1000.0
    fresh = sum(st[k]["m"] for k in (3, 7, 22, 27, 32, 35)) / 1000.0
    res = dict(st=st, days=days, hrs=hrs, mi=mi, mo=mo, comp=comp, T15=T15,
               q_b201=q_b201, q_b401=q_b401, q_pas_hf=q_pas_hf, q_pas_as=q_pas_as, q_cool_hf=q_cool_hf, q_cool_as=q_cool_as,
               q_e402=q_e402, q_drum=q_drum, Tx=Tx, T28=T28, q_frz=q_frz, q_ref=q_ref, steam_ind=steam_ind, steam_dir=steam_dir,
               steam_tot=steam_tot, q_boil_out=q_boil_out, q_fuel=q_fuel, chw=q_cool_hf + q_cool_as + q_e402,
               pulp_tpy=(st[18]["m"] + st[19]["m"]) * hrs / 1000.0, byp_tpy=(st[12]["m"] + st[21]["m"]) * hrs / 1000.0,
               iqf_tpy=st[31]["m"] * hrs / 1000.0, dm_eff=dm_eff, cod_kgh=cod_kgh, cod_mgl=cod_kgh / st[34]["m"] * 1e6,
               cod_peel=cod_pi + cod_pp, cod_leach=cod_kgh - cod_pi - cod_pp, cod_iqf_kgt=cod_iqf_line / iqf_th, cod_kgt=cod_kgh / prod_th,
               peel_mgl=(cod_pi + cod_pp) / w35 * 1e6 if w35 else 0.0, w35=w35, dm_pi=dm_pi, trim_dm=st[21]["d"] + dm_pi,
               dump_cod=dump_cod, h_eff=h_eff, cp_frozen=cp_frozen, iqf_th=iqf_th, prod_th=prod_th, fresh=fresh, fresh_m3t=fresh / prod_th,
               kwe_comp=kwe, kwh_t_comp=(kwe[0] / iqf_th, kwe[1] / iqf_th), kw_bref=(a["bref_kwh_lo"] * iqf_th, a["bref_kwh_hi"] * iqf_th),
               steam_t_frozen=m23 / st[31]["m"], steam_alt_b401=0.09 * st[31]["m"], T34=T34,
               steam_short=lambda f: a["T_hf"] - (1 - f) * (a["T_hf"] - T15))
    res["eff_m3h"] = st[34]["m"] / 1000.0
    return res


B = balance()
ST = B["st"]


def f0(x): return f"{x:,.0f}"
def f1(x): return f"{x:,.1f}"


# =====================================================================================================
# 2. drawing helpers
# =====================================================================================================
def ebox(s, x, y, w, h, tag, desc=None, fill="#fff", rx=5, sz=11):
    R(s, x, y, w, h, fill, INK, 2, None, rx)
    if desc is None: T(s, x + w / 2, y + h / 2 + 4, tag, sz, 700, "middle")
    else:
        T(s, x + w / 2, y + h / 2 - 2, tag, sz, 700, "middle"); T(s, x + w / 2, y + h / 2 + 10, desc, 9.5, 400, "middle")


def line(s, pts, col=INK, arrow_=False, dash=None, sw=2.4): pipe(s, pts, sw, col, arrow_, dash)


def dot(s, x, y, col=INK): s.add(f'<circle cx="{x}" cy="{y}" r="3.2" fill="{col}"/>')


def sig(s, pts): PL(s, pts, 1.3, BLUE, "5 4")


def esd(s, pts): PL(s, pts, 1.5, RED, "6 4", "ahr")


def vent_cap(s, x, y, col=INK):
    s.add(f'<path d="M{x-7},{y} Q{x},{y-9} {x+7},{y}" fill="none" stroke="{col}" stroke-width="2"/>')


def place(s, ox, oy, k=1.0): s.add(f'<g transform="translate({ox},{oy}) scale({k})">')
def endplace(s): s.add('</g>')


def hatch_box(s, x, y, w, h, color="#ffe0b2"): R(s, x, y, w, h, color, "none", op=.6)


def gapline(s, pts, gaps, col=EFF, arrow_=False, dash=None):
    """polyline broken at crossing points: pts is a list of (x,y); gaps = [(x,y)] on straight segments; gap half-length 7"""
    segs = []
    for (xa, ya), (xb, yb) in zip(pts[:-1], pts[1:]):
        cuts = sorted([g for g in gaps if (xa == xb == g[0] and min(ya, yb) < g[1] < max(ya, yb)) or (ya == yb == g[1] and min(xa, xb) < g[0] < max(xa, xb))],
                      key=lambda g: abs(g[0] - xa) + abs(g[1] - ya))
        cur = (xa, ya)
        for g in cuts:
            d = 7
            if xa == xb: e1 = (xa, g[1] - d if yb > ya else g[1] + d); e2 = (xa, g[1] + d if yb > ya else g[1] - d)
            else: e1 = (g[0] - d if xb > xa else g[0] + d, ya); e2 = (g[0] + d if xb > xa else g[0] - d, ya)
            segs.append([cur, e1]); cur = e2
        segs.append([cur, (xb, yb)])
    for i, sg in enumerate(segs): line(s, sg, col, arrow_ and i == len(segs) - 1, dash)


# =====================================================================================================
# 3. utility / hazard blocks (local coordinates; sheet 1 and the scenario sheets reuse them, hot=True adds scenario overlays)
# =====================================================================================================
def esd_box(s, x, y, w, tag, desc):
    ebox(s, x, y, w, 36, tag, desc, fill="#fff3e0", sz=10.5)


def block_refrig(s, evap=False, hot=False):
    """Refrigeration machinery room MR-701. Local origin top-left; room x 120..420, y 0..196. The refrigerant is NOT named in the
    source: shown as generic 'refrigerant (A)'. evap=True draws one combined evaporator box on the left (scenario sheet);
    on sheet 1 the F-401 and CS-401 lines are drawn by the caller. Wall penetrations: F-401 liquid (120,40), suction (120,80);
    CS-401 suction (312,0), liquid (376,0)."""
    R(s, 120, 0, 300, 196, "#faf7ff", REF, 1.8, "9 5")
    T(s, 128, 190, "MR-701 machinery room (A)", 10.5, 700, fill=REF)
    if evap:
        ebox(s, 0, 28, 96, 66, "F-401, CS-401", "evaporators", sz=10.5)
        line(s, [(120, 40), (96, 40)], REF); line(s, [(96, 80), (120, 80)], REF)
        T(s, 2, 112, "refrigerant (A):", 9.5, 700, fill=REF); T(s, 2, 124, "type not in source", 9.5, 400, fill=REF)
    else:
        line(s, [(312, 0), (312, 80)], REF); line(s, [(376, 0), (376, 40)], REF)
    line(s, [(120, 80), (160, 80)], REF)
    line(s, [(312, 80), (160, 80)], REF) if not evap else None
    line(s, [(160, 80), (160, 111)], REF)
    compressor(s, 160, 128, 17); T(s, 160, 160, "C-701", 10, 700, "middle"); T(s, 160, 172, "compressor (A)", 9, 400, "middle")
    line(s, [(177, 128), (230, 128)], REF, True)
    hx(s, 270, 128, 80, 28, None, None, REF); T(s, 270, 158, "E-701", 10, 700, "middle"); T(s, 270, 170, "condenser (A)", 9, 400, "middle")
    line(s, [(310, 128), (327, 128)], REF, True)
    hvessel(s, 365, 128, 56, 34); T(s, 365, 164, "V-701", 10, 700, "middle"); T(s, 365, 176, "receiver (A)", 9, 400, "middle")
    gaps = [(312, 40), (398, 40)] if not evap else [(398, 40)]
    gapline(s, [(403, 128), (412, 128), (412, 40), (120, 40)], gaps, REF)
    arrow(s, 150, 40, "l", REF)
    valve(s, 230, 40, 0, "gate", True, REF); T(s, 230, 58, "SV-701", 9, 700, "middle")
    PL(s, [(365, 111), (365, 100)], 1.6); psv(s, 365, 84, RED if hot else INK)
    PL(s, [(383, 84), (398, 84), (398, 0), (398, -14)], 2.4); vent_cap(s, 398, -14)
    T(s, 352, 72, "PSV-701", 9, 700, "end")
    bubble(s, 215, 92, "AT", "701", True); bubble(s, 190, 60, "AT", "702", True)
    bubble(s, 270, 94, "PSH", "701", True); PL(s, [(270, 109), (270, 114)], 1.2)
    if hot:
        s.add(f'<ellipse cx="260" cy="110" rx="150" ry="76" fill="#b39ddb" opacity=".22" stroke="{REF}" stroke-dasharray="4 4"/>')
        esd_box(s, 190, -78, 130, "ESD-701 (A)", "refrigeration safety logic")
        sig(s, [(215, 77), (215, 66), (255, 66), (255, -42)])
        esd(s, [(205, -42), (205, 4), (230, 4), (230, 16)])
        esd(s, [(190, -60), (140, -60), (140, 128), (143, 128)])
        esd(s, [(320, -60), (436, -60), (436, 232), (256, 232)])
        s.add(f'<circle cx="240" cy="232" r="13" fill="#fff" stroke="{INK}" stroke-width="2"/><path d="M231,223 L249,241 M249,223 L231,241" stroke="{INK}" stroke-width="1.6"/>')
        T(s, 258, 220, "EF-701 emergency extract (A)", 9.5, 700); T(s, 258, 246, "discharge to a safe outdoor location", 9)
        star(s, 327, 128, 17)
        T(s, 250, 72, "", 9)
    return dict()


def block_boiler(s, hot=False):
    """Steam boiler house BH-501, local 306 x 200. Boiler details are placeholders (A); 'boiler approval' is in the source (section 6)."""
    R(s, 0, 0, 306, 200, "#fffaf2", STM, 1.8, "9 5")
    T(s, 36, 14, "BH-501 (A)", 10.5, 700, fill=STM)
    vvessel(s, 84, 84, 56, 56)
    T(s, 2, 176, "BL-501", 10, 700); T(s, 2, 188, "boiler (R)", 9)
    line(s, [(0, 122), (56, 122)], STM, True); valve(s, 22, 122, 0, "ball", True, STM)
    T(s, 22, 140, "XV-501", 9, 700, "middle"); T(s, 22, 151, "fuel (A)", 9, 400, "middle")
    line(s, [(84, 68), (84, 56), (302, 56)], STM, True, sw=3.2)
    PL(s, [(104, 56), (104, 52)], 1.6); psv(s, 104, 36, RED if hot else INK); PL(s, [(122, 36), (140, 36), (140, 20)], 2.4); vent_cap(s, 140, 18)
    T(s, 124, 50, "PSV-501", 9, 700)
    valve(s, 190, 56, 0, "gate", True, STM); T(s, 172, 72, "XV-502", 9.5, 700); T(s, 172, 83, "steam ESDV (A)", 9)
    PL(s, [(240, 56), (240, 52)], 1.6); psv(s, 240, 36, RED if hot else INK); PL(s, [(258, 36), (276, 36), (276, 20)], 2.4); vent_cap(s, 276, 18)
    T(s, 258, 50, "PSV-502", 9, 700)
    T(s, 302, 96, "steam 4 bar(a) (A)", 9.5, 700, "end", STM); T(s, 302, 108, "to B-201, E-301, B-401", 9, 400, "end"); T(s, 302, 119, "(stubs, sheet 1)", 9, 400, "end")
    bubble(s, 134, 102, "LSLL", "501", True); PL(s, [(112, 102), (119, 102)], 1.2)
    bubble(s, 134, 136, "PT", "501", True); PL(s, [(112, 136), (119, 136)], 1.2)
    tank(s, 225, 195, 56, 30, "", None, "cone", .6, "#cfe6f7"); T(s, 225, 158, "FWT-501 feed tank (A)", 9, 700, "middle")
    line(s, [(197, 189), (84, 189), (84, 156)], "#2a6f97", True)
    line(s, [(302, 181), (258, 181)], "#2a6f97", False); arrow(s, 256, 181, "l", "#2a6f97"); T(s, 302, 170, "cond.", 9, 400, "end"); T(s, 302, 193, "return (A)", 9, 400, "end")
    if hot:
        s.add(f'<ellipse cx="218" cy="48" rx="30" ry="24" fill="none" stroke="{STM}" stroke-width="1.6" stroke-dasharray="3 3"/>')
        esd_box(s, 110, -78, 150, "BMS-501 / ESD (A)", "burner management + trips")
        sig(s, [(149, 102), (158, 102), (158, -42)]); sig(s, [(149, 136), (158, 136), (158, 102)])
        esd(s, [(190, -42), (190, 30)]); esd(s, [(110, -60), (14, -60), (14, 96)])
        star(s, 218, 46, 15)
    return dict()


def block_etp(s, hot=False):
    """Effluent treatment ETP-601 (conceptual; sizing needs COD/BOD and consent limits). Local origin top-left, 430 x 198."""
    R(s, 0, 0, 430, 198, "#fbf6f2", EFF, 1.8, "9 5")
    T(s, 110, 14, "ETP-601 (R)", 10.5, 700, fill=EFF)
    line(s, [(24, -10), (24, 60), (40, 60)], EFF, True)
    ebox(s, 40, 42, 52, 36, "S-601", "screen", sz=10.5)
    line(s, [(92, 60), (107, 60)], EFF, True)
    tank(s, 140, 112, 66, 48, "TK-601", "equalisation (A)", "dome", .55, "#d7ccc8")
    bubble(s, 140, 34, "LT", "601", True); PL(s, [(140, 49), (140, 63)], 1.3)
    line(s, [(173, 100), (189, 100)], EFF, False); pump(s, 200, 100, 11); T(s, 218, 118, "P-601", 9, 700)
    line(s, [(211, 89), (211, 60), (247, 60)], EFF, True)
    bubble(s, 232, 34, "AT", "601", True); PL(s, [(232, 49), (232, 60)], 1.3); T(s, 214, 20, "pH (A)", 9, 400, "end")
    reactor(s, 275, 84, 56, 56, "R-601", "aerobic (A)", False, "#fff", True)
    vvessel(s, 345, 52, 44, 60)
    T(s, 345, 26, "CL-601", 9.5, 700, "middle"); T(s, 345, 37, "clarifier (A)", 9, 400, "middle")
    line(s, [(303, 84), (323, 84)], EFF, True)
    line(s, [(367, 84), (426, 84)], EFF, True); T(s, 428, 98, "treated", 9, 400, "end"); T(s, 428, 109, "consent (A)", 9, 400, "end")
    line(s, [(345, 124), (345, 168), (290, 168)], EFF, True); ebox(s, 236, 156, 54, 24, "SB-601", None, sz=10); T(s, 263, 192, "sludge bed (A)", 9, 400, "middle")
    T(s, 8, 168, "Not sized: needs COD/BOD,", 9); T(s, 8, 180, "flow peaks, consent limits (S)", 9)
    if hot:
        s.add(f'<ellipse cx="60" cy="60" rx="52" ry="28" fill="#ffcc80" opacity=".4" stroke="{AMBER}" stroke-dasharray="3 3"/>')
        star(s, 24, 22, 14); T(s, 42, 26, "slug in", 10, 700, "start", RED)
    return dict()


def block_pasteur(s, hot=False):
    """Pasteuriser, hold tube, hot-fill and aseptic filling train (HACCP critical control point area). Local 508 x 222."""
    R(s, -6, -26, 508, 222, "#f6fbf6", GREEN, 1.8, "9 5")
    T(s, 2, -12, "HOT-FILL / ASEPTIC TRAIN: HACCP CCP AREA (R: HACCP, lab, traceability)", 10.5, 700, fill=GREEN)
    hx(s, 40, 70, 80, 28); T(s, 40, 98, "E-301", 10, 700, "middle"); T(s, 40, 110, "pasteuriser", 9, 400, "middle")
    R(s, 100, 62, 34, 16, "#fff", INK, 2, None, 8); T(s, 117, 102, "HT-301", 9.5, 700, "middle"); T(s, 117, 113, "hold tube", 9, 400, "middle")
    line(s, [(80, 70), (100, 70)]); line(s, [(134, 70), (250, 70)])
    PL(s, [(150, 70), (150, 43)], 1.3, BLUE, "5 4"); bubble(s, 150, 28, "TIC", "301", True)
    bubble(s, 200, 28, "TSL", "302", True); PL(s, [(200, 70), (200, 43)], 1.3, BLUE, "5 4")
    valve(s, 172, 70, 0, "gate", True, INK); T(s, 182, 94, "FDV-301", 9.5, 700); T(s, 182, 105, "divert (A)", 9)
    sig(s, [(215, 28), (222, 28), (222, 48), (172, 48), (172, 55)])
    PL(s, [(172, 81), (172, 150)], 2.4, INK, "6 4"); arrow(s, 172, 150, "d")
    ebox(s, 150, 150, 46, 30, "BT-301", "balance", sz=10)
    T(s, 204, 156, "divert: re-heat or", 9); T(s, 204, 168, "reject (A)", 9)
    dot(s, 250, 70)
    ebox(s, 262, 48, 56, 44, "FL-301", "HF filler"); line(s, [(250, 70), (262, 70)], INK, True)
    ebox(s, 336, 52, 66, 36, "TC-301", "cool tunnel"); line(s, [(318, 70), (336, 70)], INK, True)
    line(s, [(402, 70), (470, 70)], INK, True); T(s, 470, 62, "HF packs", 9.5, 400, "end")
    PL(s, [(250, 70), (250, 140), (276, 140)], 2.6)
    hx(s, 316, 140, 80, 28); T(s, 316, 168, "E-302", 10, 700, "middle"); T(s, 316, 180, "aseptic cooler", 9, 400, "middle")
    line(s, [(356, 140), (392, 140)], INK, True)
    ebox(s, 392, 118, 78, 44, "AF-301", "aseptic filler"); line(s, [(470, 140), (500, 140)], INK, True); T(s, 500, 132, "bags", 9.5, 400, "end")
    # steam with control valve TCV-301
    PL(s, [(40, -2), (40, 56)], 2.4, STM); arrow(s, 40, 56, "d", STM); valve(s, 40, 22, 90, "gate", True, STM)
    T(s, 62, 8, "STEAM (A)", 9, 700, fill=STM); T(s, 48, 46, "TCV-301", 9.5, 700)
    sig(s, [(135, 28), (62, 28)])
    PL(s, [(316, 100), (316, 126)], 2.4, CHW); arrow(s, 316, 126, "d", CHW); T(s, 322, 108, "CHW (A)", 9, 700, fill=CHW)
    PL(s, [(369, 20), (369, 52)], 2.4, CHW); arrow(s, 369, 52, "d", CHW); T(s, 375, 28, "CHW (A)", 9, 700, fill=CHW)
    if hot:
        star(s, 117, 70, 15); T(s, 8, 130, "product below critical T", 10.5, 700, fill=RED)
        T(s, 8, 142, "(hold or steam short)", 9.5, 400, fill=RED)
    return dict()


# =====================================================================================================
# 4. SHEET 1: P&ID
# =====================================================================================================
def sheet_pid():
    s = Sheet(1, "P&ID: fruit and vegetable processing plant, 10,000 t/yr raw input", "Process and utilities P&ID",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw",
              basis=SRC)
    frame(s, NS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    # ---------------- row A: receiving, washing, pulp line
    T(s, 60, 106, "PULP LINE", 11, 700, fill=GREY)
    line(s, [(30, 170), (90, 170)], INK, True); strm(s, 50, 170, 1)
    T(s, 28, 148, "raw F&V", 9.5); T(s, 28, 192, "10,000 t/yr (S)", 9, fill=GREY)
    ebox(s, 90, 140, 70, 60, "R-101", "receive/sort")
    line(s, [(125, 200), (125, 238)], INK, True); strm(s, 125, 216, 2)
    ebox(s, 98, 238, 54, 20, "WB-101", None, sz=10); T(s, 158, 252, "rejects", 9.5)
    line(s, [(160, 170), (200, 170)], INK, True)
    ebox(s, 200, 140, 80, 60, "W-102", "drum washer")
    line(s, [(240, 90), (240, 140)], INK, True); strm(s, 240, 100, 3); T(s, 226, 104, "wash water", 9.5, anchor="end")
    ctrlvalve(s, 240, 130, 90); bubble(s, 292, 110, "FIC", "102", True); sig(s, [(240, 112), (277, 112)]); sig(s, [(292, 125), (292, 130), (264, 130)])
    gapline(s, [(240, 200), (240, 262)], [], EFF, True); strm(s, 240, 230, 5, EFF)
    line(s, [(280, 170), (318, 170)], INK, True); strm(s, 299, 170, 4); dot(s, 318, 170)
    # pulp blancher
    line(s, [(318, 170), (372, 170)], INK, True); strm(s, 336, 170, 6)
    hvessel(s, 430, 170, 90, 44, "B-201", "pulp blancher")
    line(s, [(358, 112), (358, 168)], INK, True); strm(s, 358, 128, 7); T(s, 344, 132, "MU water", 9.5, anchor="end")
    line(s, [(400, 90), (400, 148)], STM, True); strm(s, 400, 100, 8, STM); T(s, 388, 104, "steam 4 bar(a) (A)", 9.5, anchor="end", fill=STM)
    ctrlvalve(s, 400, 128, 90, STM); bubble(s, 448, 108, "TIC", "201", True)
    sig(s, [(448, 148), (448, 123)]); sig(s, [(433, 108), (419, 108), (419, 119)])
    line(s, [(468, 148), (468, 118)], INK, False); vent_cap(s, 468, 116); strm(s, 486, 132, 9); T(s, 500, 136, "vent", 9.5)
    gapline(s, [(430, 192), (430, 262)], [], EFF, True); strm(s, 430, 230, 10, EFF)
    line(s, [(488, 170), (520, 170)], INK, True); strm(s, 504, 170, 11)
    ebox(s, 520, 146, 68, 48, "PU-201", "pulper")
    line(s, [(554, 194), (554, 238)], INK, True); strm(s, 554, 214, 12); ebox(s, 528, 238, 52, 20, "WB-201", None, sz=10)
    T(s, 522, 238, "peel/stone/", 9.5, anchor="end"); T(s, 522, 250, "pomace", 9.5, anchor="end")
    line(s, [(588, 170), (636, 170)], INK, True); strm(s, 620, 170, 13)
    vvessel(s, 660, 140, 48, 60)
    T(s, 692, 138, "DA-201", 10.5, 700); T(s, 692, 150, "deaerator", 9.5)
    line(s, [(660, 127), (660, 106), (650, 106)], INK, False); ebox(s, 606, 96, 44, 20, "VC-201", None, sz=9.5)
    gapline(s, [(606, 106), (594, 106), (594, 262)], [(594, 170)], EFF, True); strm(s, 594, 130, 14, EFF)
    line(s, [(660, 214), (660, 240), (677, 240)], INK, False); pump(s, 690, 240, 13); T(s, 722, 244, "P-201", 9.5, 700)
    line(s, [(703, 227), (703, 170), (725, 170)], INK, True); strm(s, 703, 198, 15)
    hx(s, 770, 170, 90, 28); T(s, 785, 205, "E-301", 10.5, 700, "middle"); T(s, 785, 217, "pasteuriser", 9.5, anchor="middle")
    line(s, [(770, 90), (770, 156)], STM, True); ctrlvalve(s, 770, 132, 90, STM); T(s, 778, 100, "STEAM (A)", 9.5, 700, fill=STM)
    R(s, 822, 162, 32, 16, "#fff", INK, 2, None, 8); T(s, 838, 192, "HT-301", 9.5, 700, "middle")
    line(s, [(815, 170), (822, 170)], INK); line(s, [(854, 170), (884, 170)], INK)
    sig(s, [(868, 170), (868, 140)]); bubble(s, 868, 125, "TIC", "301", True); sig(s, [(853, 125), (796, 125)])
    dot(s, 884, 170)
    valve(s, 906, 170, 0, "gate", True); T(s, 914, 196, "FDV-301", 9.5, 700)
    line(s, [(884, 170), (962, 170)], INK, True); strm(s, 936, 170, 16)
    sig(s, [(948, 170), (948, 140)]); bubble(s, 948, 125, "TSL", "302", True); sig(s, [(933, 125), (906, 125), (906, 146)])
    PL(s, [(906, 181), (906, 214)], 2.4, INK, "6 4"); arrow(s, 906, 214, "d"); T(s, 912, 226, "divert (A)", 9.5)
    ebox(s, 962, 146, 52, 48, "FL-301", "HF filler", sz=10.5)
    line(s, [(1014, 170), (1024, 170)], INK); ebox(s, 1024, 150, 62, 40, "TC-301", "cool tunnel", sz=10.5)
    line(s, [(1086, 170), (1114, 170)], INK, True); strm(s, 1100, 170, 18); T(s, 1114, 206, "HF packs", 9.5, anchor="end")
    PL(s, [(1055, 118), (1055, 150)], 2.4, CHW); arrow(s, 1055, 150, "d", CHW); T(s, 1061, 124, "CHW (A)", 9, 700, fill=CHW)
    # aseptic branch
    line(s, [(884, 170), (884, 300), (915, 300)], INK, True); strm(s, 884, 235, 17)
    hx(s, 955, 300, 80, 28); T(s, 955, 336, "E-302", 10.5, 700, "middle"); T(s, 955, 348, "aseptic cooler", 9.5, anchor="middle")
    PL(s, [(950, 266), (950, 286)], 2.4, CHW); arrow(s, 950, 286, "d", CHW); T(s, 944, 276, "CHW (A)", 9, 700, "end", CHW)
    line(s, [(995, 300), (1010, 300)], INK, True); ebox(s, 1010, 276, 76, 48, "AF-301", "aseptic fill", sz=10.5)
    line(s, [(1086, 300), (1114, 300)], INK, True); strm(s, 1100, 300, 19)
    T(s, 1114, 338, "AS bags (A)", 9.5, anchor="end")
    ebox(s, 975, 236, 135, 38, "LAB-801 (R)", "QC lab, batch release", fill="#e8f5e9", sz=10.5)
    # ---------------- row B: IQF line
    T(s, 60, 372, "IQF LINE", 11, 700, fill=GREY)
    line(s, [(318, 170), (318, 420), (350, 420)], INK, True); strm(s, 318, 335, 20)
    ebox(s, 80, 296, 104, 36, "CIP-901", "CIP / washdown (A)", sz=10.5)
    line(s, [(132, 372), (132, 332)], INK, True); strm(s, 132, 352, 32); T(s, 146, 356, "water (A)", 9.5)
    gapline(s, [(132, 296), (132, 262)], [], EFF, True); strm(s, 132, 280, 33, EFF); dot(s, 132, 262, EFF)
    ebox(s, 350, 390, 70, 60, "PE-401", "peel/trim/cut")
    line(s, [(385, 450), (385, 490)], INK, True); strm(s, 385, 468, 21); ebox(s, 359, 490, 52, 20, "WB-401", None, sz=10)
    line(s, [(420, 420), (462, 420)], INK, True)
    line(s, [(440, 356), (440, 418)], INK, True); strm(s, 440, 374, 22); T(s, 425, 378, "MU water", 9.5, anchor="end")
    hvessel(s, 520, 420, 90, 44, "B-401", "IQF blancher")
    line(s, [(490, 340), (490, 398)], STM, True); strm(s, 490, 350, 23, STM); T(s, 478, 354, "steam (A)", 9.5, anchor="end", fill=STM)
    ctrlvalve(s, 490, 376, 90, STM); bubble(s, 548, 360, "TIC", "401", True); sig(s, [(548, 398), (548, 375)]); sig(s, [(533, 362), (520, 362), (520, 367)])
    line(s, [(572, 398), (572, 368)], INK, False); vent_cap(s, 572, 366); strm(s, 588, 380, 24)
    gapline(s, [(520, 442), (520, 530)], [], EFF, True); strm(s, 520, 490, 25, EFF)
    line(s, [(578, 420), (615, 420)], INK, True); strm(s, 597, 420, 26)
    hx(s, 660, 420, 90, 28); T(s, 682, 454, "E-402 drum + CHW", 10.5, 700, "end")
    line(s, [(645, 352), (645, 406)], INK, True); strm(s, 645, 362, 27); T(s, 630, 366, "purge", 9.5, anchor="end")
    PL(s, [(682, 340), (682, 406)], 2.4, CHW); arrow(s, 682, 406, "d", CHW); T(s, 690, 352, "CHW (A)", 9, 700, fill=CHW)
    PL(s, [(692, 434), (692, 470)], 2.4, CHW); arrow(s, 692, 470, "d", CHW); T(s, 698, 466, "return", 9, 400, fill=CHW)
    gapline(s, [(650, 434), (650, 530)], [], EFF, True); strm(s, 650, 490, 28, EFF)
    line(s, [(705, 420), (745, 420)], INK, True); strm(s, 725, 420, 29)
    ebox(s, 745, 380, 130, 80, "F-401", "IQF tunnel freezer", fill="#ede7f6")
    PL(s, [(760, 452), (775, 440), (790, 452), (805, 440), (820, 452), (835, 440), (850, 452)], 1.5, REF)
    gapline(s, [(762, 460), (762, 530)], [], EFF, True); strm(s, 762, 496, 30, EFF)
    line(s, [(875, 420), (905, 420)], INK, True); strm(s, 890, 420, 31)
    ebox(s, 905, 395, 52, 50, "PK-401", "pack")
    line(s, [(957, 420), (1000, 420)], INK, True)
    ebox(s, 1000, 380, 108, 80, "CS-401", "cold store -18 C (A)", fill="#ede7f6")
    PL(s, [(1014, 452), (1029, 440), (1044, 452), (1059, 440), (1074, 452), (1089, 440)], 1.5, REF)
    bubble(s, 1054, 356, "TI", "401", False); PL(s, [(1054, 371), (1054, 380)], 1.2)
    # refrigerant lines F-401 / CS-401 down to machinery room
    line(s, [(770, 460), (770, 648), (820, 648)], REF); line(s, [(790, 460), (790, 608), (820, 608)], REF)
    line(s, [(1012, 460), (1012, 568)], REF); line(s, [(1076, 460), (1076, 568)], REF)
    # ---------------- effluent header
    gapline(s, [(762, 530), (44, 530), (44, 558)], [], EFF, True)
    gapline(s, [(594, 262), (44, 262), (44, 530)], [(318, 262)], EFF)
    T(s, 60, 524, "effluent header to ETP-601 (stream 34)", 9.5, 700, fill=EFF)
    strm(s, 44, 396, 34, EFF)
    # utilities blocks along the bottom
    place(s, 20, 568); block_etp(s); endplace(s)
    place(s, 456, 566); block_boiler(s); endplace(s)
    place(s, 700, 568); block_refrig(s); endplace(s)
    rev_b_devices(s)
    # block links: effluent into ETP (local inlet at 26,-10 => abs 46,562); refrigerant to the room walls
    # ---------------- legend and notes (right panel)
    panel_box(s)
    y = section(s, 1135, 84, 445, "LEGEND AND NOTES")
    yy = y + 18
    for col, lab, dash in ((INK, "process line (product / fruit)", None), (STM, "steam (boiler house BH-501)", None), (CHW, "chilled water (A)", None),
                           (REF, "refrigerant, type not in source (A)", None), (EFF, "effluent to ETP-601", None), (BLUE, "instrument signal", "5 4"), (RED, "ESD output", "6 4")):
        PL(s, [(1148, yy - 3), (1190, yy - 3)], 2.6 if dash is None else 1.5, col, dash); T(s, 1198, yy, lab, 10.5); yy += 17
    strm(s, 1160, yy + 8, "n"); T(s, 1182, yy + 12, "stream number: matches the HMB column on sheet 2", 10.5)
    yy += 28
    valve(s, 1160, yy + 6, 0, "gate"); T(s, 1182, yy + 10, "manual valve", 10.5); valve(s, 1300, yy + 6, 0, "gate", True); T(s, 1322, yy + 10, "control / ESD valve", 10.5)
    yy += 26
    psv(s, 1160, yy + 16); T(s, 1190, yy + 20, "pressure safety valve", 10.5); bubble(s, 1330, yy + 12, "TIC", "301", True); T(s, 1352, yy + 16, "controller", 10.5)
    yy += 44
    for n in NOTES1: yy = WRAP(s, 1145, yy, n, 74, 10, 12) + 4
    y = section(s, 1135, yy + 2, 445, "EQUIPMENT (descriptions A; R where the source names the function)")
    for i, (a_, b_) in enumerate(zip(EQUIP_C1, EQUIP_C2)):
        T(s, 1141, y + 14 + i * 11.8, a_, 9.5); T(s, 1362, y + 14 + i * 11.8, b_, 9.5)
    return s


# =====================================================================================================
# 5. SHEET 2: HMB
# =====================================================================================================
def stream_cols(keys):
    rows_name = [ST[k]["name"] for k in keys]
    def pct(k, c): return f"{100 * ST[k][c] / ST[k]['m']:.1f}"
    R_ = [("Stream name", rows_name), ("Mass flow (kg/h)", [f0(ST[k]["m"]) if ST[k]["m"] >= 100 else f1(ST[k]["m"]) for k in keys]),
          ("Annual (t/yr)", [f0(ST[k]["m"] * B["hrs"] / 1000) for k in keys]),
          ("Water (mass %)", [pct(k, "w") for k in keys]), ("Fruit dry matter (mass %)", [pct(k, "d") for k in keys]),
          ("Soil (mass %)", [pct(k, "so") for k in keys]),
          ("Temperature (C)", [f1(ST[k]["T"]) if abs(ST[k]["T"]) < 100 else f0(ST[k]["T"]) for k in keys]),
          ("Pressure (bar a)", [f"{ST[k]['P']:.2f}" if ST[k]["P"] < 1.5 else f"{ST[k]['P']:.1f}" for k in keys]),
          ("Phase", [ST[k]["ph"] for k in keys]), ("In / out of plant", [{"in": "IN", "out": "OUT", "int": "internal"}[ST[k]["io"]] for k in keys])]
    return R_


def case(**kw):
    """one balance run with changed assumptions (sensitivities, sheet 3); None if the peel dry matter exceeds the by-product"""
    a = dict(A); a.update(kw)
    try: return balance(a)
    except AssertionError: return None


def _chg_rows():
    q, r = B, REV_A
    return [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
            ("Peel/cut water and COD (new streams 35, 36)", f"COD {r['cod_kgt']:.1f} kg/t product (leach only)", f"COD {q['cod_kgt']:.1f} kg/t plant; {q['cod_iqf_kgt']:.1f} kg/t IQF line",
             "BREF Table 8.3: 36.5 kg/t; sec 8.2.1: 5,000 mg/L (read)",
             f"ETP load {r['cod_kgh']:.1f} to {q['cod_kgh']:.1f} kg COD/h; {r['cod_mgl']:.0f} to {q['cod_mgl']:.0f} mg/L; {r['eff_m3h']:.1f} to {q['eff_m3h']:.1f} m3/h. Mass closes; by-product {r['byp_tpy']:.0f} to {q['byp_tpy']:.0f} t/yr"),
            ("IQF cooler water (A12)", "0.3 kg/kg purge", f"{A['purge_kgkg']:.1f} kg/kg, drum cooler", "BREF sec 8.2.2.4: 2-4 L/kg (read), mid value",
             f"fresh water {r['fresh_m3t']:.2f} to {q['fresh_m3t']:.2f} m3/t product (BREF 5.0-8.5). E-402 chilled-water duty {r['q_e402']:.1f} to {q['q_e402']:.1f} kW; water stage takes {q['q_drum']:.1f} kW"),
            ("Ice cp and latent heat (A11)", "1.9 and 334 kJ/kg/K", f"{A['cp_ice']:.3f} (mean -18..-1.5 C); {A['Lf']:.1f}", "IAPWS R10-06(2009) Eq. 6, Tables 2, 4, 6 (read; check value reproduced)",
             f"freezing load {r['q_frz']:.1f} to {q['q_frz']:.1f} kW, refrigeration {r['q_ref']:.1f} to {q['q_ref']:.1f} kW. thermo value 1.26 not used"),
            ("Fruit cp, steam props (A11)", "3.60; 144.0 C, 2133; vac 2300", f"{A['cp_f']:.2f} (solids cp {A['cp_dm']} A); {A['Tsat']} C, {A['hfg']}; vac {A['hfg_vac']}", "composition (D); CoolProp 8.0 at 4.0, 0.2 bar (frozen)",
             f"B-201 {r['q_b201']:.1f} to {q['q_b201']:.1f} kW; E-301 {r['q_pas_hf']+r['q_pas_as']:.1f} to {q['q_pas_hf']+q['q_pas_as']:.1f} kW; steam {r['steam_tot']:.0f} to {q['steam_tot']:.0f} kg/h; boiler fuel {r['q_fuel']:.0f} to {q['q_fuel']:.0f} kW; deaerator out {r['T15']:.2f} to {q['T15']:.2f} C. Effluent T 40 (A) to {q['T34']:.1f} C (D)"),
            ("Blancher steam, belt + water cooler", "0.160 t/t frozen", f"{q['steam_t_frozen']:.3f} (kept); option 0.09", "BREF Tables 8.6, 8.7 (read)",
             f"0.09 needs cooling-water-to-preheat recovery (not drawn): B-401 steam {ST[23]['m']:.0f} to {q['steam_alt_b401']:.0f} kg/h (D). Not adopted"),
            ("Refrigeration electricity (new line)", "not given (62-70 kWhe/t implied)", f"{q['kwh_t_comp'][0]:.0f}-{q['kwh_t_comp'][1]:.0f} compressor; BREF 80-280 total", "BREF sec 8.1 (read); COP from CoolProp, ammonia as a conditional case",
             f"adds kWe: {q['kwe_comp'][0]:.0f}-{q['kwe_comp'][1]:.0f} compressor, {q['kw_bref'][0]:.0f}-{q['kw_bref'][1]:.0f} BREF total. Cold-store load still open"),
            ("Crop and pulp yield (A5, A6)", "83.9 % to line, crop open", "unchanged; crop is an input (sheet 3)", "BREF 8.2.1: peel loss 16-17 %; IFC Table 2: 60-200 kg/t (read)",
             f"template tuning kept: pulp {q['pulp_tpy']:.0f} t/yr vs S 6,000. Crop sensitivity on sheet 3"),
            ("IQF share (A5)", "25 % of fruit (A)", "25 % (A); range 10-50 % on sheet 3", "no source found", "unchanged here; sheet 3 shows q_ref, COD and water at 10 and 50 %"),
            ("Safety devices (new)", "PSV-501, 502, 701", "+ PSV-301, 401, 402, VB-201, AT-702, RH-701, ESD-701, BMS-501, EF-701", "SAFETY_FEATURES_CHECKLIST.md (S1, S5, S7, S11)", "none on the balance; relief, ESD, SIF, HAZOP on sheets 6 to 8")]


def sheet_hmb():
    s = Sheet(2, "HEAT AND MATERIAL BALANCE (Rev B): fruit and vegetable plant, 10,000 t/yr", "Heat and material balance",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="Computed in gen_pid_fruitveg.py; S / D / A tags")
    frame(s, NS)
    keysA, keysB = list(range(1, 19)), list(range(19, 37))
    y = hmb_table(s, 20, 84, keysA, stream_cols(keysA), 150, 77, 16, 9.5, "STREAMS 1 TO 18: receiving, washing, pulp line (kg/h at 4,000 operating h/yr)")
    y = hmb_table(s, 20, y + 8, keysB, stream_cols(keysB), 150, 77, 16, 9.5, "STREAMS 19 TO 36: IQF line, effluent (34 = to ETP), peel/cut water (35, 36)")
    q = B
    yt = y + 12
    y2 = section(s, 20, yt, 600, "DUTIES (D: computed from properties)")
    rows = [("Duty", "Equipment", "kW", "Basis"),
            ("Blancher, pulp line (direct steam)", "B-201", f1(q["q_b201"]), "(m cp + MU cp_w) dT x 1.15"),
            ("Blancher, IQF line (direct steam)", "B-401", f1(q["q_b401"]), "same, 85 C"),
            ("Pasteuriser, hot-fill share to 95 C", "E-301", f1(q["q_pas_hf"]), "m cp (95 - T15)"),
            ("Pasteuriser, aseptic share to 105 C", "E-301", f1(q["q_pas_as"]), "no regeneration (A)"),
            ("Cooling, hot-fill packs 95 to 35 C", "TC-301", f1(q["q_cool_hf"]), "chilled / cooling water"),
            ("Cooling, aseptic 105 to 30 C", "E-302", f1(q["q_cool_as"]), "no regeneration (A)"),
            ("IQF cooler, water stage 85 to 33 C", "E-402", f1(q["q_drum"]), f"to stream 27, out {q['T28']:.1f} C"),
            ("IQF cooler, chilled-water trim to 10 C", "E-402", f1(q["q_e402"]), "chilled water"),
            ("IQF freezing, product only", "F-401", f1(q["q_frz"]), "sensible + latent + sensible"),
            ("IQF refrigeration load (x 1.25)", "F-401 evap.", f1(q["q_ref"]), "fans, losses (A)"),
            ("Compressor electricity (D)", "C-701", f"{q['kwe_comp'][0]:.0f} to {q['kwe_comp'][1]:.0f}", "load / COP 1.76 to 1.56 (NH3, cond.)"),
            ("Freezing electricity, BREF total (S)", "F-401 + aux.", f"{q['kw_bref'][0]:.0f} to {q['kw_bref'][1]:.0f}", "80 to 280 kWhe/t (fans incl.)"),
            ("Steam, direct (B-201 + B-401), kg/h", "BH-501", f0(q["steam_dir"]), "Q / (hfg + cp dT)"),
            ("Steam, indirect (E-301), kg/h", "BH-501", f0(q["steam_ind"]), "Q / hfg; cond. returned"),
            ("Boiler heat to steam / fuel input", "BL-501", f"{q['q_boil_out']:.0f} / {q['q_fuel']:.0f}", "feed 80 C, 85 % (A)")]
    y2 = table(s, 20, y2, (240, 90, 80, 190), rows, 16, 9.5)
    T(s, 22, y2 + 11, "Cold-store load is not computed: needs layout, insulation, door traffic, stock level (no source found).", 9.5, fill=GREY)
    xc = 640
    y3 = section(s, xc, yt, 440, "CLOSURE (D, asserted in code)")
    R(s, xc, y3, 440, 112, "#fff", "#9aa", 1)
    mi, mo = q["mi"], q["mo"]
    T(s, xc + 10, y3 + 18, f"Closure: in {mi:,.0f} kg/h, out {mo:,.0f} kg/h, error {abs(mi-mo)/mi*100:.3f} %", 12, 700, fill=GREEN)
    cw, cd, cs = q["comp"]["w"], q["comp"]["d"], q["comp"]["so"]
    T(s, xc + 10, y3 + 36, f"Water: in {cw[0]:,.1f}, out {cw[1]:,.1f} kg/h", 10)
    T(s, xc + 10, y3 + 50, f"Dry matter: in {cd[0]:,.2f}, out {cd[1]:,.2f} kg/h.  Soil: in {cs[0]:,.2f}, out {cs[1]:,.2f} kg/h", 10)
    T(s, xc + 10, y3 + 66, "In: streams 1, 3, 7, 8, 22, 23, 27, 32, 35.  Out: 2, 9, 12, 18, 19, 21, 24, 31, 34.", 9.5)
    T(s, xc + 10, y3 + 80, "Stream 34 = 5 + 10 + 14 + 25 + 28 + 30 + 33 + 36.  Washer, pulper, deaerator,", 9.5)
    T(s, xc + 10, y3 + 93, "pasteuriser and IQF trim/peel splits also close (water, dry matter, soil asserted).", 9.5)
    y4 = section(s, xc, y3 + 120, 440, "CROSS-CHECK AGAINST THE SOURCE (S)")
    rows = [("Item", "S (template)", "Computed", "Diff"),
            ("Pulp and puree (t/yr)", f0(S_PULP_T), f0(q["pulp_tpy"]), f"{(q['pulp_tpy']/S_PULP_T-1)*100:+.1f} %"),
            ("Peel, stone, pomace (t/yr)", f0(S_BYP_T), f0(q["byp_tpy"]), f"{(q['byp_tpy']/S_BYP_T-1)*100:+.1f} %"),
            ("IQF frozen product (t/yr)", "not stated", f0(q["iqf_tpy"]), "A split")]
    y4 = table(s, xc, y4, (170, 95, 95, 80), rows, 16, 9.5)
    WRAP(s, xc + 2, y4 + 13, "By-product falls 3 % against Rev A because the peel-water COD is taken out of the dry trim (stream 21), not out of the product.", 82, 9.5, 12, GREY)
    xe = 1100
    y5 = section(s, xe, yt, 480, "ETP LOAD BASIS (D; sheet 4 scenario 4 uses it)")
    r = REV_A
    rows = [("Item", "Rev A", "Rev B"),
            ("Flow to ETP-601 (m3/h)", f1(r["eff_m3h"]), f1(q["eff_m3h"])),
            ("COD, fruit leach (kg/h)", f1(r["cod_kgh"]), f1(q["cod_leach"])),
            ("COD, peel/cut water at PE-401 (kg/h)", "0.0", f1(q["cod_peel"])),
            ("COD total (kg/h)", f1(r["cod_kgh"]), f1(q["cod_kgh"])),
            ("Mixed COD (mg/L)", f0(r["cod_mgl"]), f0(q["cod_mgl"])),
            ("Peel/cut stream alone (m3/h; mg/L)", "none", f"{q['w35']/1000:.2f}; {q['peel_mgl']:.0f}"),
            ("COD per t product, plant (kg/t)", f"{r['cod_kgt']:.1f}", f"{q['cod_kgt']:.1f}"),
            ("COD per t IQF product, peeled line (kg/t)", "n/a", f"{q['cod_iqf_kgt']:.1f}"),
            ("Removal to meet 250 mg/L (IFC Table 1)", f"{(1-250/r['cod_mgl'])*100:.0f} %", f"{(1-250/q['cod_mgl'])*100:.0f} %"),
            ("Effluent temperature (C)", "40 (A)", f"{q['T34']:.1f} (D)")]
    y5 = table(s, xe, y5, (290, 90, 100), rows, 16, 9.5)
    y5 = wtable(s, xe, y5 + 6, (480,), [(
        "Size the ETP from the 5,000 mg/L peel stream plus the dilute remainder and from peak days, not from the mixed average. BREF range for peeled fruit: 36.5 (Table 8.3) to 66.3 (caustic, Table 8.4) kg COD/t product. ETP not sized.",)], 9.5, 11.5, 4)
    ya = max(y2 + 22, y4 + 40, y5) + 8
    sec = section(s, 20, ya, 1100, "REV A TO REV B CHANGES (each row: item | Rev A | Rev B | source | effect on closure / duties)")
    yb = wtable(s, 20, sec, (150, 120, 150, 215, 465), _chg_rows(), 9.5, 11, 3)
    xr = 1135
    y6 = section(s, xr, ya, 445, "EFFLUENT SLUG ILLUSTRATION (D)")
    rows = [("Item", "Value"), ("One hour of pulp (stream 15) dumped: COD (kg)", f0(q["dump_cod"])), ("Multiple of a normal Rev B COD hour", f"{q['dump_cod']/q['cod_kgh']:.0f} x"),
            ("Multiple of a Rev A COD hour", f"{q['dump_cod']/REV_A['cod_kgh']:.0f} x")]
    y6 = table(s, xr, y6, (330, 115), rows, 16, 9.5)
    WRAP(s, xr + 2, y6 + 13, "CIP chemicals, spills, changeovers and seasonal peaks are still not in the model.", 82, 9.5, 12, GREY)
    if yb > 1112: print("WARNING sheet 2 changes box overflows to", yb)
    return s


def sheet_hmb_notes():
    s = Sheet(3, "HEAT AND MATERIAL BALANCE (Rev B): assumptions, sources, tool runs, sensitivities", "HMB notes and sensitivities",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="gen_pid_fruitveg.py; S / D / A tags; tool constants frozen")
    frame(s, NS)
    q = B
    y = section(s, 20, 84, 1100, "ASSUMED (A), to be confirmed by licensor or vendor; Rev B changes marked")
    A_lines = [
        "A1 20 h/d, so 200 d x 20 h = 4,000 h/yr; raw rate 2,500 kg/h.  A2 sort rejects 3 % and adhering soil 1 % of the consignment.  A3 wash water 3 kg/kg raw, CIP and floor wash 0.5 kg/kg raw.  A4 fruit leached: wash 0.5 %, blanch 1 %, cooler 0.3 %.  A5 75 % of washed fruit to the pulp line, 25 % to IQF (no source: tuned to the template; range 10-50 % on this sheet).",
        "A6 pulper by-product 14 % of blanched fruit, IQF peel and trim 22 % (crop input; IFC Table 2 gives 60-200 kg/t product by crop).  A7 deaerator flash loss 1.5 % of hot pulp.  A8 half of the pulp hot-filled, half aseptic.  A9 blancher make-up water 0.5 kg/kg fruit, 10 % of steam leaves as vapour, 15 % bath heat-loss allowance.",
        "A10 temperatures (C): ambient 28; B-201 90; B-401 85; pulper out 80; hot-fill 95; aseptic hold 105; cooled hot-fill 35; aseptic out 30; IQF cooled 10; frozen core -18; Rev B: drum-cooler product exit = ambient + 5 K (A).  A11 cp water 4.18; solids cp 1.2 (range 1.2-1.5) so fruit cp 3.73; water 85 % of fruit, 85 % of it frozen; freezing point -1.5 C.  A12 frost loss 0.5 %, refrigeration overhead 25 %, boiler efficiency 85 %, feed 80 C.",
        "A13 1.1 kg COD per kg fruit dry matter (sucrose 1.12, glucose 1.07, cellulose 1.18, citric acid 0.75 by stoichiometry; validation).  A14 refrigerant, boiler fuel, line sizes: not specified.  A15 (Rev B) peel/cut water applies to the whole IQF line (PE-401) and not to the pulp line; compressor COP from an ammonia cycle is a conditional proxy only.",
    ]
    yy = y + 14
    for t_ in A_lines: yy = WRAP(s, 26, yy, t_, 205, 9.5, 12) + 3
    y7 = section(s, 20, yy + 4, 1100, "SOURCED (S) AND DERIVED (D)")
    yy = y7 + 14
    yy = WRAP(s, 26, yy, f"S  {SRC}: raw input 10,000 t/yr, about 50 TPD in season, 6,000 t/yr pulp and puree (section 1); process steps (section 4); FSSAI, HACCP / ISO 22000, boiler approval, fire NOC, pollution-board consent (section 6); by-products 15,00,000 kg/yr, pulp 60,00,000 kg/yr (section 9); HACCP, in-house lab, batch traceability (section 12).", 205, 9.5, 12) + 3
    yy = WRAP(s, 26, yy, "S  EU JRC FDM BREF (JRC118627, Dec 2019): Table 8.3 (36.5 kg COD/t, abrasion + knife peeling), Table 8.4 (66.3, caustic), sec 8.2.1 (peeling wastewater about 4,000-5,000 mg/L), sec 8.2.2.4 (drum cooler 2-4 L/kg), Tables 8.6-8.7 (blancher steam 0.09 / 0.16 t/t), sec 8.1 (freezing 80-280 kWhe/t), Table 8.10 (water 5.0-8.5 m3/t frozen). IFC EHS Food and Beverage 2007 Tables 1, 2. IAPWS R10-06(2009) (ice cp, latent heat).", 205, 9.5, 12) + 3
    yy = WRAP(s, 26, yy, "D  operating days = 10,000 / 50 = 200.  Blancher Q = (m_fruit cp + m_MU cp_w)(Tb - Ta) x 1.15; steam = Q / (hfg + cp_w (Tsat - Tb)).  Deaerator T_out = T_in - loss x hfg_vac / cp.  Pasteuriser Q = m cp dT.  Drum cooler Q = m cp (85 - 33); water outlet = Ta + Q / (m_w cp_w).  Freezing Q = m [cp (Ti - Tfp) + x_w x_f L + cp_frozen (Tfp - Tout)], cp_frozen = x_w x_f cp_ice + x_w (1 - x_f) cp_w + (1 - x_w) cp_dm.  Peel water = COD / concentration; COD load = 36.5 kg/t x IQF product.  COD = dry matter x 1.1.", 205, 9.5, 12) + 4
    y8 = section(s, 20, yy + 2, 1100, "SENSITIVITIES (D: balance re-run with the changed input; base = Rev B)")
    def row(lab, r_):
        return (lab, f0(r_["pulp_tpy"]), f0(r_["iqf_tpy"]), f0(r_["byp_tpy"]), f1(r_["q_ref"]), f1(r_["cod_kgh"]), f0(r_["cod_mgl"]), f"{r_['fresh_m3t']:.2f}", f0(r_["steam_tot"]))
    rows = [("IQF share of washed fruit", "pulp t/yr", "IQF t/yr", "by-prod t/yr", "q_ref kW", "COD kg/h", "COD mg/L", "water m3/t", "steam kg/h")]
    for lab, sp in (("10 % IQF (split_pulp 0.90)", 0.90), ("25 % IQF (base, A)", 0.75), ("50 % IQF (split_pulp 0.50)", 0.50)):
        rows.append(row(lab, case(split_pulp=sp)))
    yy = table(s, 20, y8, (270, 100, 100, 110, 100, 100, 100, 110, 110), rows, 16, 9.5)
    # peel scope: arithmetic (D) because the dry matter for a larger load is not available from the trim alone
    prod_th, iqf_th = q["prod_th"], q["iqf_th"]
    dm_by = q["trim_dm"] + ST[12]["d"]
    def scope(lab, kgt, th):
        cod = q["cod_leach"] + kgt * th
        wpeel = kgt * th * 1e6 / A["peel_conc_mgl"] / 1000.0
        flow = q["eff_m3h"] - q["w35"] / 1000.0 + wpeel
        need = kgt * th / A["cod"]
        return (lab, f1(cod), f"{wpeel:.2f}", f1(flow), f0(cod / flow * 1000), f"{cod / prod_th:.1f}", f"{need:.1f} vs {dm_by:.1f}")
    rows = [("Peeling scope (kg COD/t product, BREF)", "COD kg/h", "peel m3/h", "flow m3/h", "COD mg/L", "kg COD/t plant", "peel dm vs by-prod dm kg/h"),
            scope("IQF line, 36.5 (Rev B base)", 36.5, iqf_th), scope("IQF line, caustic 66.3", 66.3, iqf_th),
            scope("whole plant peeled, 36.5", 36.5, prod_th), scope("whole plant peeled, 66.3", 66.3, prod_th)]
    yy = table(s, 20, yy + 8, (270, 100, 100, 110, 100, 130, 290), rows, 16, 9.5)
    T(s, 22, yy + 11, "Where peel dry matter exceeds the by-product dry matter, the load needs flesh loss as well: not modelled, so those rows are bounds (D).", 9.5, fill=GREY)
    rows = [("Crop by-product (IFC Table 2, kg/t product)", "fraction of raw", "pulp t/yr", "IQF t/yr", "by-prod t/yr", "product % of raw")]
    for lab, bp in (("strawberries 60", 60.0), ("apples 90", 90.0), ("peaches 180", 180.0), ("carrots 200", 200.0), ("template tuning (A6, base)", None)):
        if bp is None: r_ = q; fr_ = "0.14 / 0.22"
        else:
            f_ = bp / (1000.0 + bp); r_ = case(by_pulp=f_, by_iqf=f_, peel_share_iqf=0.0); fr_ = f"{f_:.3f}"
        rows.append((lab, fr_, f0(r_["pulp_tpy"]), f0(r_["iqf_tpy"]), f0(r_["byp_tpy"]), f"{(r_['pulp_tpy'] + r_['iqf_tpy']) / S_RAW_T * 100:.1f}"))
    yy = table(s, 20, yy + 20, (330, 140, 120, 120, 120, 150), rows, 16, 9.5)
    T(s, 22, yy + 11, "Crop rows use equal by-product fractions on both lines and no peel water (peel_share 0): yield bounds only. Mango extractor 77.9 % (search snippet, grade C) not used.", 9.5, fill=GREY)
    xr = 1135
    y9 = section(s, xr, 84, 445, "TOOL RUNS AND FROZEN CONSTANTS (provenance)")
    yy = y9 + 14
    for t_ in ("Ice cp: computed in the generator from the IAPWS R10-06(2009) Gibbs equation (Eq. 6, Tables 2 and 4, p = 101,325 Pa). Table 6 check value 2,096.71391 J/kg/K at 273.152519 K is reproduced to 1e-9 (assert). Mean over -18 to -1.5 C = 2.025 kJ/kg/K. Resolves the thermo 1.26 / Rev A 1.9 conflict: thermo is wrong for solid ice. Ice cp at 255.15 K is 1.965, at 271.65 K 2.086.",
               "Latent heat 333.4 kJ/kg: ice enthalpy at the triple point, -333,444 J/kg, IAPWS R10-06 Table 6; no correction from 0 to -1.5 C (A).",
               "Steam: /private/tmp/claude-501/venv_val/bin/python, CoolProp 8.0.0, PropsSI at 4.0 and 0.2 bar: Tsat 143.608 C, hfg 2,133.398 kJ/kg; hfg 2,357.513 kJ/kg at 0.2 bar (Tsat 60.06 C).",
               "Refrigeration COP: same interpreter, CoolProp R717 (ammonia, a conditional case only), single stage, eta_is 0.7, saturated suction, saturated liquid at 35 C (A): -35 C evaporating 1.76, -40 C 1.56. Not a statement that the plant uses ammonia.",
               "Not run: DWSIM (not installed); BioSTEAM has no fruit-and-vegetable model."):
        yy = WRAP(s, xr + 10, yy, t_, 80, 9.5, 12, bullet=True) + 5
    y10 = section(s, xr, yy + 4, 445, "STILL OPEN AGAINST THE REFERENCES")
    yy = y10 + 14
    for t_ in (f"Whole-plant COD {q['cod_kgt']:.1f} kg/t product stays below 36.5 because the pulp line is unpeeled (A15); the peeled IQF line is {q['cod_iqf_kgt']:.1f}.",
               "Blancher steam 0.163 t/t versus 0.09 (belt + water cooler): the difference is the heat recovery that is not drawn.",
               "Compressor electricity 63-72 kWhe/t versus BREF 80-280: BREF includes fans and auxiliaries.",
               "Pulp-line yield 83.9 % versus 77.9 % mango (grade C): crop open.",
               "IQF share, pasteuriser steam per t, hot-fill / aseptic split, cold-store load, boiler fuel: no source found."):
        yy = WRAP(s, xr + 10, yy, t_, 80, 9.5, 12, bullet=True) + 4
    return s


# =====================================================================================================
# 6. SHEETS 3 and 4: scenarios
# =====================================================================================================
def wtable(s, x, y, colw, rows, size=9.5, lh=11.5, pad=4):
    """table with wrapped cells; returns y below"""
    import textwrap
    yy = y
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(c, max(8, int((colw[j] - 8) / (size * 0.5)))) for j, c in enumerate(r)]
        h = max(len(c) for c in cells) * lh + 2 * pad
        if i == 0: R(s, x, yy, sum(colw), h, "#e8eaf0", "none")
        elif i % 2 == 0: R(s, x, yy, sum(colw), h, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, t_ in enumerate(c): T(s, cx + 4, yy + pad + 9 + k * lh, t_, size, 700 if (i == 0 or j == 0) else 400)
            cx += colw[j]
        yy += h
    R(s, x, y, sum(colw), yy - y, "none", "#9aa", 1)
    return yy


def scen_table(s, rows, y=784):
    y = section(s, 20, y, 1100, "SCENARIO TABLE (qualitative unless a number is shown; open data needs named)")
    hdr = ("Scenario", "Initiating event", "Hazard", "Safeguards shown (R / A)", "Open data needs")
    wtable(s, 20, y, (110, 190, 230, 330, 240), [hdr] + rows)


def note_box(s, x, y, w, title, lines, col=INK, size=10.5, bullet=True):
    """box with a bold title and wrapped lines; returns bottom y"""
    cw = int((w - 20) / (size * 0.52))
    yy = y + 26
    body = []
    for t_ in lines:
        n = len(textwrap.wrap(t_, cw))
        body.append(n)
    h = 30 + sum(body) * (size + 3.5) + 4 * len(lines)
    R(s, x, y, w, h, "#fff", col, 1.4)
    T(s, x + 8, y + 15, title, size, 700, fill=col)
    for t_ in lines: yy = WRAP(s, x + 8, yy, t_, cw, size, size + 3.5, col if col != INK else INK, 400, bullet) + 4
    return y + h


def q_(x): return f"{x:,.0f}"


def sheet_s12():
    s = Sheet(4, "SCENARIOS 1 AND 2: refrigerant release in the machinery room; boiler and steam release", "Scenarios 1 and 2",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="Qualitative; duties from sheet 2")
    frame(s, NS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    section(s, 20, 84, 540, "SCENARIO 1: refrigerant release, IQF / cold-store machinery room")
    place(s, 34, 250, 1.2); block_refrig(s, evap=True, hot=True); endplace(s)
    yb = note_box(s, 30, 570, 520, "Reading the drawing (S1)", [
        "Release at the receiver flange or a compressor seal; the cloud fills the room. The source does not name the refrigerant, so the cloud is generic.",
        "AT-701 and AT-702 detect, ESD-701 closes the liquid solenoid SV-701, stops C-701 and starts emergency extract EF-701 (all A).",
        f"Duty context (D): IQF refrigeration load about {q_(B['q_ref'])} kW ({q_(B['q_frz'])} kW product). Charge and compressor size come from the vendor."], RED, 10)
    section(s, 580, 84, 540, "SCENARIO 2: boiler or steam-header release")
    place(s, 598, 252, 1.65); block_boiler(s, hot=True); endplace(s)
    note_box(s, 590, 592, 520, "Reading the drawing (S2)", [
        "Header or flange break near XV-502: scald and flash steam; the steam supply to B-201, E-301 and B-401 is lost. Other initiators: low water or overpressure in BL-501.",
        f"Duty context (D): steam about {f0(B['steam_tot'])} kg/h ({f0(B['steam_dir'])} direct, {f0(B['steam_ind'])} indirect); boiler heat to steam {f0(B['q_boil_out'])} kW, fuel input {f0(B['q_fuel'])} kW at 85 % (A).",
        "BMS-501 trips fuel XV-501 and closes steam ESDV XV-502 on low water, high pressure or header low-pressure (A)."], STM, 10)
    panel_box(s)
    y = section(s, 1135, 84, 445, "WHY THESE TWO SCENARIOS")
    yy = y + 18
    for t_ in ("The source describes no large flammable inventory. Its process-safety exposure sits in the utilities: a refrigeration system for IQF freezing and the cold store, and a steam boiler.",
               "Refrigerant release: the machinery room concentrates charge, compressors and joints. The outcome depends on the refrigerant, which the source does not give: toxic (for example ammonia), asphyxiant (CO2, halocarbons) or flammable (hydrocarbons). The refrigerant choice is an open question for the licensor, with a hazard study to follow.",
               "Steam release: saturated steam at an assumed 4 bar(a) scalds at the break. Loss of steam also stops blanching and pasteurising, which is a food-safety event too (sheet 5).",
               "Statutory (S, section 6): boiler approval, factory licence and fire NOC are listed. Nothing in the source gives boiler capacity, fuel or inspection dates.",
               "All safeguards are A (assumed): detection, ESD closure, emergency extract, PSVs vented outside. No distance, release rate or frequency is given: those need vendor data."):
        yy = WRAP(s, 1145, yy, t_, 74, 10.5, 13.5, bullet=True) + 6
    y = section(s, 1135, yy + 6, 445, "OPEN DATA NEEDS, SCENARIOS 1 AND 2")
    yy = y + 18
    for t_ in ("Refrigerant type, charge, room volume, ventilation rate, detector set points and the refrigeration safety code to apply.",
               "Boiler capacity, fuel, header pressure and route, valve closing times, inspection and test records.",
               "Not quantified: needs the data above."):
        yy = WRAP(s, 1145, yy, t_, 74, 10.5, 13.5, bullet=True) + 4
    scen_table(s, [
        ("S1 Refrigerant release", "Leak from receiver V-701, compressor seals, flanges or a relief valve in MR-701", "Toxic, asphyxiant or flammable cloud in a closed room (depends on the refrigerant); cold burns; loss of IQF freezing and cold store",
         "AT-701 detector (A); ESD-701 closes SV-701 and stops C-701 (A); emergency extract EF-701 (A); PSV-701 vented outside (A); PSH-701 high-pressure cut-out (A)", "Refrigerant type and charge; room volume and ventilation rate; detector set points; refrigeration safety code to apply"),
        ("S2 Boiler / steam release", "Header or flange failure; low water; overpressure; loss of feedwater", "Scald and flash steam; boiler failure; loss of steam to blanchers and pasteuriser (a food-safety event too)",
         "LSLL-501 low-water trip (A); PT-501; PSV-501, PSV-502 vented to roof (A); XV-502 steam ESDV (A); XV-501 fuel shut-off (A); boiler approval (R, section 6)", "Boiler capacity, fuel, header pressure and route; inspection records")])
    return s


def sheet_s34():
    s = Sheet(5, "SCENARIOS 3 AND 4: hot-fill / aseptic product-temperature deviation; effluent high load", "Scenarios 3 and 4",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="Qualitative; computed lines from sheet 2")
    frame(s, NS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    section(s, 20, 84, 1100, "SCENARIO 3: hot-fill temperature deviation or loss of sterility (HACCP critical control point)")
    place(s, 44, 152, 1.45); block_pasteur(s, hot=True); endplace(s)
    note_box(s, 790, 112, 322, "Reading the drawing (S3)", [
        "The star marks product leaving the hold tube below the critical temperature.",
        f"E-301 duty (D): about {f1(B['q_pas_hf'])} kW to 95 C for hot-fill, {f1(B['q_pas_as'])} kW to 105 C for aseptic.",
        f"A 10 % shortfall in steam duty at constant flow lowers the 95 C outlet to about {B['steam_short'](0.10):.1f} C (linear, D).",
        "Critical limit, hold time and F-value are not in the source: not quantified. They come from the process authority's validated schedule."], GREEN, 10)
    section(s, 20, 446, 1100, "SCENARIO 4: effluent high load (slug of product or CIP liquor to the ETP)")
    place(s, 40, 500, 1.3); block_etp(s, hot=True); endplace(s)
    note_box(s, 612, 480, 500, "Reading the drawing (S4)", [
        "A slug of high-strength liquid enters the effluent header at the left (star). S-601 and equalisation TK-601 are the first defence; AT-601 (pH) and LT-601 (level) alarm.",
        f"Normal load (D from A): {f1(B['eff_m3h'])} m3/h, COD about {f1(B['cod_kgh'])} kg/h ({f0(B['cod_mgl'])} mg/L).",
        f"Illustration (D): one hour of deaerated pulp (stream 15) sent to drain carries about {f0(B['dump_cod'])} kg COD, {B['dump_cod']/B['cod_kgh']:.0f} times a normal hour.",
        "Real peaks (CIP, spills, changeovers, season start-up) are not modelled. Normal COD = fruit leach plus the IQF peel/cut stream (BREF Table 8.3); not a design peak."], EFF, 10)
    panel_box(s)
    y = section(s, 1135, 84, 445, "WHY A FOOD-SAFETY CCP IS DRAWN LIKE THIS")
    yy = y + 18
    for t_ in ("In a food plant the critical control point is a process-safety-like barrier: if product leaves E-301 and the hold tube below the validated temperature or time, the pack can carry live organisms. TIC-301 and TSL-302 with a flow-diversion valve FDV-301 divert under-processed product to BT-301 for re-heat or rejection (all A).",
               "The source lists HACCP / ISO 22000, an in-house lab and batch traceability as the mitigation (section 12, R). It gives no critical limit, hold time or validation: those are open data needs.",
               "Hot-fill depends on the fill temperature and the cooling tunnel TC-301; aseptic adds sterile cooling by E-302 and a sterile filler AF-301, where loss of sterility is the failure.",
               "Steam loss (sheet 4, S2) is also an S3 initiator: with no steam, E-301 cannot reach 95 or 105 C and FDV-301 must divert all flow."):
        yy = WRAP(s, 1145, yy, t_, 74, 10.5, 13.5, bullet=True) + 6
    y = section(s, 1135, yy + 6, 445, "SCENARIO 4 NUMBERS (D from A, sheet 2)")
    rows = [("Item", "Value"), ("Normal flow to ETP (m3/h)", f1(B["eff_m3h"])), ("Normal COD (kg/h)", f1(B["cod_kgh"])), ("Normal COD (mg/L)", f0(B["cod_mgl"])),
            ("One hour of pulp dumped: COD (kg)", f0(B["dump_cod"])), ("Ratio to a normal hour", f"{B['dump_cod']/B['cod_kgh']:.0f} x")]
    y = table(s, 1135, y, (275, 170), rows, 17, 10)
    y = section(s, 1135, y + 12, 445, "OPEN DATA NEEDS, SCENARIOS 3 AND 4")
    yy = y + 18
    for t_ in ("S3: critical limit, hold time, F-value, hold-tube design, CIP / SIP procedure, validation by the process authority.",
               "S4: COD / BOD and flow variation by crop, pollution-board consent limits, tank volumes, sludge route.",
               "Not quantified: needs the data above."):
        yy = WRAP(s, 1145, yy, t_, 74, 10.5, 13.5, bullet=True) + 4
    scen_table(s, [
        ("S3 Hot-fill / aseptic deviation", "Steam control or supply fault; hold tube fouled; excess flow; FDV-301 fails to divert; aseptic path contaminated", "Under-processed pulp reaches the pack: spoilage organisms or pathogens survive; recall and illness. A food-safety CCP, not a fire scenario",
         "TIC-301 / TSL-302 with FDV-301 divert (A); hold tube HT-301 (A); QC lab LAB-801 and batch traceability (R); HACCP plan (R); BT-301 re-heat or reject (A)", "Critical limit, hold time, F-value; hold-tube design; validation by the process authority; CIP / SIP procedure"),
        ("S4 Effluent high load", "Product or pulp dumped to drain; CIP discharge; season start-up; ETP screen blinds", "Biological upset, consent breach, odour; possible shutdown of washing and blanching",
         "S-601 screen (A); equalisation TK-601 with LT-601 and AT-601 pH (A); R-601 / CL-601 (A); ETP is in the source cost list (R); pollution-board consent (R, section 6)", "COD / BOD and flow variation; consent limits; tank volumes; sludge route")])
    return s


# =====================================================================================================
# 7. REV B: relief / safety devices on sheet 1, and the safety design basis sheets (6, 7, 8)
# =====================================================================================================
DP = dict(boiler=6.0, header=5.0, e301=4.0)      # A: design / set pressures, barg (operating steam 4 bar(a) = 3.0 barg; E-301 product 3 bar(a) = 2.0 barg)


def psv_at(s, x, y, mode="down", color=INK):
    """relief valve with its inlet at the top (mode 'down': spring hangs below, outlet to the right at (x+18, y))"""
    s.add(f'<g transform="translate({x},{y}) scale(1,-1) translate({-x},{-y})">')
    psv(s, x, y, color)
    s.add('</g>')


def psv501_indicative():
    """indicative PSV-501 steam area with the toolkit's API 520 Napier function (text not read): rated output = 1.25 x HMB steam (A)"""
    if RELIEF is None: return None
    W = 1.25 * B["steam_tot"]
    p1 = RELIEF.relieving_pressure_kpa(DP["boiler"] * 100.0, "single_non_fire")
    r = RELIEF.steam_area(W, p1)
    return W, p1, r.required_area_mm2, r.orifice


REL_KEY = [("Tag", "Protects", "Set (A)", "Discharge"),
           ("PSV-501", "BL-501 boiler", f"{DP['boiler']:.1f} barg", "roof, outdoor"),
           ("PSV-502", "steam header, E-301 / B-201 / B-401 steam side", f"{DP['header']:.1f} barg", "roof, outdoor"),
           ("PSV-301", "E-301 product side, HT-301", f"{DP['e301']:.1f} barg", "closed drain"),
           ("VB-201", "DA-201 / VC-201 (vacuum)", "full vacuum", "filtered air in"),
           ("PSV-401", "F-401 evaporator", "not set (refrigerant)", "RH-701"),
           ("PSV-402", "CS-401 evaporator", "not set (refrigerant)", "RH-701"),
           ("PSV-701", "V-701 receiver and loop", "not set (refrigerant)", "RH-701, vent cap"),
           ("vents 9, 24", "B-201, B-401 (open vent, no valve)", "atmospheric", "outdoor vent cap")]


def rev_b_devices(s):
    # ---- E-301 product-side relief (below the exchanger) and steam control valve tag
    PL(s, [(734, 184), (734, 190)], 2.4); psv_at(s, 734, 206)
    PL(s, [(752, 206), (752, 226)], 2.4); arrow(s, 752, 226, "d")
    T(s, 758, 234, "PSV-301 to drain (A)", 9, 700)
    T(s, 780, 151, "TCV-301", 9, 700)
    # ---- DA-201 vacuum breaker
    dot(s, 660, 116); PL(s, [(660, 116), (677, 116)], 2.2); valve(s, 688, 116, 180, "check", False, INK); PL(s, [(699, 116), (705, 116)], 2.2)
    T(s, 709, 120, "VB-201 (A)", 9, 700)
    # ---- IQF peel / cut water (streams 35, 36)
    line(s, [(368, 336), (368, 388)], INK, True); strm(s, 368, 358, 35); T(s, 380, 338, "peel water", 9.5)
    gapline(s, [(358, 450), (358, 470), (335, 470), (335, 530)], [], EFF, True); strm(s, 335, 500, 36, EFF); dot(s, 335, 530, EFF)
    # ---- refrigerant relief on F-401 / CS-401 into the relief header RH-701
    PL(s, [(850, 460), (850, 478)], 2.4, REF); psv_at(s, 850, 494, "down", REF); PL(s, [(832, 494), (832, 556)], 2.4, REF) if False else None
    PL(s, [(868, 494), (868, 556)], 2.4, REF)
    T(s, 838, 543, "PSV-401", 9, 700)
    PL(s, [(1040, 460), (1040, 478)], 2.4, REF); psv_at(s, 1040, 494, "down", REF); PL(s, [(1058, 494), (1058, 556)], 2.4, REF)
    T(s, 1006, 543, "PSV-402", 9, 700)
    gapline(s, [(868, 556), (1098, 556)], [(1012, 556), (1076, 556)], REF); dot(s, 868, 556, REF); dot(s, 1058, 556, REF); dot(s, 1098, 556, REF)
    T(s, 890, 552, "RH-701 header (A)", 9, 700, fill=REF)
    T(s, 892, 490, "refrigerant (A)", 9, 400, fill=REF); T(s, 892, 502, "liquid / suction", 9, 400, fill=REF)
    # ---- safety devices and logic band
    R(s, 20, 780, 1100, 330, "none", "#889", 1)
    section(s, 20, 780, 1100, "SAFETY DEVICES AND LOGIC (A unless marked; relief schedule and ESD matrix sheet 6, SIFs and HAZOP sheet 7, detection sheet 8)")
    table(s, 28, 812, (80, 230, 125, 105), REL_KEY, 16, 9.5)
    ind = psv501_indicative()
    T(s, 30, 975, "Indicative PSV-501: " + (f"{ind[2]:.0f} mm2, API 526 orifice {ind[3]} for an assumed rated output of {ind[0]:.0f} kg/h (A) at {DP['boiler']:.1f} barg set, 10 % accumulation" if ind else "not computed"), 9.5)
    WRAP(s, 30, 996, "No bulk flammable liquid is on this plant, so no bund is drawn. If fuel oil, caustic or acid are stored: bund at 110 % of the largest vessel or 25 % of total capacity (HSG176 para 157, S1, R for flammable liquids; applied to CIP chemicals by analogy, A). MR-701 and BH-501 sit apart from occupied areas; relief and extract discharge outdoors away from air intakes and people (S11 Kuraray, R).", 112, 9.5, 12)
    # EF-701, ESD-701, BMS-501
    PL(s, [(1010, 764), (1010, 799)], 2.4, REF, "5 3")
    s.add(f'<circle cx="1010" cy="812" r="13" fill="#fff" stroke="{INK}" stroke-width="2"/><path d="M1001,803 L1019,821 M1019,803 L1001,821" stroke="{INK}" stroke-width="1.6"/>')
    line(s, [(1023, 812), (1100, 812)], REF, True)
    T(s, 1100, 836, "to a safe outdoor location (A)", 9, 400, "end")
    T(s, 1010, 846, "EF-701 emergency extract (A)", 9.5, 700, "middle")
    ebox(s, 640, 822, 180, 40, "ESD-701 (A)", "refrigeration safety logic", fill="#fff3e0", sz=10.5)
    esd(s, [(820, 842), (940, 842), (940, 812), (996, 812)])
    TL(s, 640, 878, ["in: AT-701, AT-702 high-high (A), PSH-701, manual ESD (A)", "out: SV-701 close (room, above), C-701 stop, EF-701 start", "AT-701 / AT-702: two gas detectors in MR-701 (A; two detectors is the",
                      "ammonia-room practice reported by S7, conditional on refrigerant)"], 9.5, 11.5)
    ebox(s, 640, 946, 180, 40, "BMS-501 (A)", "burner management + trips", fill="#fff3e0", sz=10.5)
    TL(s, 640, 1002, ["in: LSLL-501 low-low water, PT-501 high pressure, flame (A)", "out: XV-501 fuel close, XV-502 steam ESDV close (boiler, above)", "fail position: closed on loss of signal or air (S1 para 128, R)"], 9.5, 11.5)
    return None


NOTES1 = [
    "Basis. Conceptual, screening, not for construction. Capacity, products, steps and approvals come from the DPR template (sections 1, 4, 6, 9, 12), a template with illustrative figures. Every other value is an assumption (A) or a cited source (S), see sheets 2 and 3.",
    "R = named in the source: HACCP / ISO 22000 and FSSAI, in-house lab and batch traceability (section 12), boiler approval and fire NOC (section 6), ETP and pollution-board consent (sections 6, 7). A = assumed by this drawing.",
    "Refrigerant. The source names none: generic 'refrigerant (A)'. Ammonia is treated as a labelled conditional case on sheets 6 to 8 (S6, S7 as reported); halocarbon, CO2 and hydrocarbon each give a different hazard. Open question for the licensor.",
    "Sterility / hot-fill. Product temperature after HT-301 is the HACCP critical control point: TIC-301 / TSL-302 with flow-diversion valve FDV-301 (A). Critical limits and hold time are not in the source.",
    "Steam. Direct steam heats B-201 and B-401 (streams 8, 23); E-301 and aseptic duty use indirect steam, condensate to FWT-501 (A). E-402 is a countercurrent drum cooler (water, stream 27) plus chilled-water trim. Peel/cut water (35, 36) at PE-401 (S, BREF).",
    "Relief (Rev B): PSV-301 on E-301, PSV-401 / 402 on F-401 / CS-401 into RH-701, VB-201 on DA-201, PSV-501 / 502 / 701 as before. Set pressures are A; see the key below the drawing. Open-vent vessels carry no valve in the vent.",
    "Not drawn: instrument air and cooling-water packages, chiller package, fire water, product pumps other than P-201, SIP supply to AF-301, cold-store defrost. Line sizes and numbers TBD (A).",
]
EQUIP_C1 = ["R-101 receiving, sorting belt", "W-102 drum washer", "B-201 pulp blancher, direct steam", "PU-201 pulper / finisher", "DA-201 vacuum deaerator (A)",
            "VC-201 vacuum condenser (A)", "VB-201 vacuum breaker (A)", "P-201 pulp pump", "E-301 pasteuriser, indirect steam", "TCV-301 steam control valve",
            "HT-301 hold tube (A)", "FDV-301 flow-diversion valve (A)", "FL-301 hot-fill filler", "TC-301 cooling tunnel", "E-302 aseptic cooler",
            "AF-301 aseptic filler", "LAB-801 QC lab (R)", "PSV-301 / 401 / 402 / 501 / 502 / 701 relief (A)"]
EQUIP_C2 = ["PE-401 peel / trim / cut", "B-401 IQF blancher, direct steam", "E-402 drum cooler + CHW trim", "F-401 IQF tunnel freezer", "PK-401 pack, CS-401 cold store",
            "C-701 / E-701 / V-701 refrigeration", "MR-701 machinery room, RH-701 header", "AT-701 / 702, PSH-701 detection", "ESD-701, BMS-501 logic; EF-701 fan",
            "BH-501 boiler house, BL-501 boiler (R)", "FWT-501 feed tank (A)", "S-601 screen, TK-601 equalisation, P-601 pump", "R-601 aerobic, CL-601 clarifier",
            "SB-601 sludge bed (A); ETP (R)", "CIP-901 CIP / washdown (A)", "WB-101 / 201 / 401 waste bins", "BT-301 balance tank (A; sheet 5 only)", ""]


# ---- sheet 6: relief schedule and ESD matrix
def sheet_safety_relief():
    s = Sheet(6, "SAFETY DESIGN BASIS (Rev B) 1 of 3: relief schedule and ESD cause-and-effect matrix", "Safety design basis, relief and ESD",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="SAFETY_FEATURES_CHECKLIST.md; marks R / A / gap")
    frame(s, NS)
    ind = psv501_indicative()
    ind_txt = (f"Indicative only: process_safety.relief.steam_area (API 520 Napier, text not read) for an assumed rated output of {ind[0]:.0f} kg/h (1.25 x HMB steam, A) at {DP['boiler']:.1f} barg set + 10 %: {ind[2]:.0f} mm2, orifice {ind[3]}. Boiler-code relief capacity: gap (HSE PM5 not reachable)." if ind else "not computed")
    y = section(s, 20, 84, 1100, "RELIEF SCHEDULE: every pressure item on sheet 1 (design pressures are A; R = named by a free source, gap = standard not obtained)")
    H_ = ("Item", "Design pressure basis (A)", "Relief cases", "Device (set)", "Discharge", "Sizing status", "Mark")
    rows = [H_,
            ("BL-501 boiler (R: approval, source sec. 6)", f"MAWP {DP['boiler']:.1f} barg; operating 3.0 barg (4 bar a)", "fire (external); blocked steam outlet (XV-502 closed); loss of feedwater / overheat; burner control failure",
             f"PSV-501 ({DP['boiler']:.1f} barg)", "roof, safe outdoor location", ind_txt, "A; gap: boiler code"),
            ("Steam header after XV-502", f"MAWP {DP['header']:.1f} barg (lowest steam-user rating)", "boiler pressure above user rating; trapped condensate expansion; steam control valve failed open (TCV-301, TIC-201, TIC-401)",
             f"PSV-502 ({DP['header']:.1f} barg)", "roof, safe outdoor location", "not sized: needs control-valve Cv at failure and the user pressure ratings", "A"),
            ("E-301 product side with HT-301", f"MAWP {DP['e301']:.1f} barg; operating 3 bar a (2.0 barg)", "blocked outlet at P-201 shut-off head; liquid thermal expansion; tube leak steam to product (steam 3.0 barg is below MAWP)",
             f"PSV-301 ({DP['e301']:.1f} barg)", "closed drain, scald hazard", "not sized: needs P-201 shut-off head and E-301 area / U", "A"),
            ("E-301 steam side; B-201, B-401 steam lines", f"MAWP {DP['header']:.1f} barg = header", "supply pressure above rating", "none: PSV-502 protects (no block valve between header and E-301)", "via PSV-502",
             "written reason; confirm there is no isolation valve between the header and each steam user", "A"),
            ("B-201, B-401 blanchers (open vent, direct steam)", "atmospheric; vent without valve (streams 9, 24)", "blocked vent; steam valve failed open", "open vent", "outdoor vent cap",
             "not sized: needs the failed-open steam flow; vent must pass it at negligible back-pressure", "A"),
            ("DA-201 deaerator, VC-201 vacuum condenser", "full vacuum and +0.5 barg", "full vacuum on loss of vent or condenser; cooling-water tube leak; positive pressure not credible (feeds are atmospheric or by P-201 downstream)",
             "VB-201 vacuum breaker", "filtered air in", "not sized: needs vessel volume and vacuum-source capacity (not drawn)", "A"),
            ("E-302, E-402, TC-301 (chilled-water side)", "CHW circuit MAWP 6.0 barg", "trapped CHW thermal expansion with hot product; tube leak product (2.0 barg) into CHW",
             "none here: CHW circuit relief / expansion vessel in the chiller package (not drawn)", "chiller package", "written reason; gap: confirm the package carries relief", "A; gap"),
            ("F-401 evaporator, CS-401 evaporator", "refrigerant dependent: not set", "trapped liquid expansion at isolation valves; hot-gas defrost; external fire",
             "PSV-401, PSV-402", "RH-701 to a safe outdoor location", "not sized: needs refrigerant, charge, defrost method. Ammonia (conditional): dual PRVs with a 3-way valve, relief to scrubber or flare (S6, S7 as reported); IIAR 2 gap", "A; gap"),
            ("V-701 receiver, C-701, E-701", "refrigerant dependent: not set", "external fire; blocked compressor discharge; loss of condenser cooling; non-condensables; liquid fill",
             "PSV-701 + PSH-701 cut-out (no isolation valve between, A)", "RH-701, vent cap outdoors", "not sized: refrigerant not named, receiver size not set. Fire case method exists (relief.fire_heat_input_W, API 521) but needs wetted area and latent heat", "A; gap"),
            ("FWT-501, TK-601, R-601, CL-601, S-601, PU-201, W-102", "atmospheric", "overfill; blocked vent; thermal vacuum on cooling (FWT-501 at 80 C)", "open vent / overflow", "drain",
             "written reason: no pressure source credible; vents must not be isolable", "A"),
            ("AF-301 aseptic filler, FL-301", "SIP steam / hot water not drawn", "SIP overpressure", "not drawn", "-", "gap: SIP supply not on this drawing", "gap")]
    y = wtable(s, 20, y, (140, 130, 235, 125, 105, 305, 60), rows, 9.5, 11.5, 3)
    y = section(s, 20, y + 10, 1100, "ESD CAUSE-AND-EFFECT MATRIX: every initiator and final element is drawn on sheet 1 (A: set points, voting and logic)")
    fin = ("SV-701", "C-701", "EF-701", "XV-501", "XV-502", "FDV-301", "TCV-301", "Alarm")
    M = [("Initiator",) + fin,
         ("AT-701 or AT-702 high (alarm level A)", "", "", "start", "", "", "", "", "X"),
         ("AT-701 or AT-702 high-high (A)", "close", "stop", "start", "", "", "", "", "X"),
         ("PSH-701 refrigerant high pressure", "", "stop", "", "", "", "", "", "X"),
         ("manual ESD, machinery room (A)", "close", "stop", "start", "", "", "", "", "X"),
         ("LSLL-501 boiler low-low water", "", "", "", "close", "close", "", "", "X"),
         ("PT-501 boiler high pressure", "", "", "", "close", "close", "", "", "X"),
         ("BMS-501 flame failure (A)", "", "", "", "close", "", "", "", "X"),
         ("TSL-302 product below critical T", "", "", "", "", "", "divert", "", "X"),
         ("steam supply loss at E-301 (A)", "", "", "", "", "", "divert", "close", "X"),
         ("fail position (loss of signal, air or power)", "closed", "stopped", "A: run", "closed", "closed", "divert", "closed", "-")]
    y = table(s, 20, y, (320,) + (97,) * 8, M, 15, 9.5)
    T(s, 22, y + 12, "Fail-safe isolation on loss of power: S1 para 128 (R). Voting, set points and test intervals are A; no SIL verification is claimed.", 9.5, fill=GREY)
    if y > 1112: print("WARNING sheet 6 overflow", y)
    xr = 1135
    y9 = section(s, xr, 84, 445, "MARKS AND SOURCES")
    yy = y9 + 14
    for t_ in ("R = required or recommended by a named free source. A = assumed here. gap = the controlling standard is paywalled or was not obtained (OISD, API 520/521/526, NFPA, IEC 61511, IIAR 2, EN 378, BIS, boiler code).",
               "S1 HSE HSG176 (2015): fail-safe remote isolation (para 128), bund 110 % / 25 % (para 157). S2 HSE HSG238: separate control and protection. S3 HSE COMAH plant-layout guidance. S5 OSHA 29 CFR 1910.119: relief design basis, ESD, PHA. S6 Fertilizers Europe ammonia tank guidance. S7 US EPA Region 7 ammonia refrigeration manual (describes IIAR 2). S10 CSB BP-Husky: SIS credited in PHA. S11 CSB Kuraray: relief discharge location. S19 SIL/LOPA snippets only (grade C).",
               "Ammonia is a conditional case only: the source names no refrigerant. Its conditional items are labelled on the rows above.",
               "Set pressures, boiler MAWP, circuit ratings and the Rev B sizing result are assumptions or indicative figures from the toolkit; none replaces a vendor or code calculation."):
        yy = WRAP(s, xr + 10, yy, t_, 80, 9.5, 12, bullet=True) + 5
    return s


# ---- sheet 7: SIF list and hazard identification
def sheet_safety_sif():
    s = Sheet(7, "SAFETY DESIGN BASIS (Rev B) 2 of 3: SIF list and hazard identification", "Safety design basis, SIF and HAZOP",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="SAFETY_FEATURES_CHECKLIST.md; qualitative, no invented numbers")
    frame(s, NS)
    y = section(s, 20, 84, 1100, "SAFETY INSTRUMENTED FUNCTIONS (SIL targets are ASSUMED (A); no SIL verification is claimed; IEC 61511 text not obtained)")
    rows = [("SIF", "Function and final elements", "Demand source (A)", "Protection layers credited (A)", "SIL target (A)", "Source / mark"),
            ("SIF-1", "AT-701 or AT-702 high-high: ESD-701 closes SV-701, stops C-701, starts EF-701", "refrigerant leak (seal, flange, relief lift)", "machinery-room ventilation; PSV-701; operator response", "1 (review if toxic refrigerant)", "S7 as reported (R, conditional); S2 separation; gap: IIAR 2"),
            ("SIF-2", "PSH-701 high pressure: stop C-701", "condenser cooling loss; blocked discharge", "PSV-701", "1", "A; S2"),
            ("SIF-3", "LSLL-501 low-low water: BMS-501 closes XV-501 and XV-502", "feedwater loss, FWT-501 empty", "basic level control (not credited if it shares the sensor); boiler design", "1", "A; boiler code gap (HSE PM5 404)"),
            ("SIF-4", "PT-501 high pressure: BMS-501 closes XV-501 and XV-502", "firing control failure; header closed", "PSV-501, PSV-502", "1", "A; S2"),
            ("SIF-5", "BMS-501 flame failure and purge: XV-501 closes", "burner fault", "burner design", "per burner standard", "gap: burner standard not obtained"),
            ("SIF-6", "TSL-302 under-temperature: FDV-301 diverts, stop filler", "TCV-301 fault, steam loss, hold-tube fouling, excess flow", "TIC-301 control (separate sensor); HACCP; LAB-801 release", "food-safety CCP: limit from process authority", "R: HACCP (source sec. 12); A for SIL"),
            ("SIF-7", "manual ESD pushbutton: SIF-1 outputs plus boiler trip", "operator or fire alarm", "none credited", "1", "A; S5 (emergency shutdown procedures)"),
            ("note", "Protection is separate from control (S2). BP-Husky (S10): a SIS and relief credited in the PHA did not prevent the release, so credit is tested, not assumed.", "", "", "", "S2, S10 (R)")]
    y = wtable(s, 20, y, (50, 270, 175, 255, 150, 200), rows, 9.5, 11.5, 3)
    y = section(s, 20, y + 10, 1100, "HAZARD IDENTIFICATION: 10 nodes, HAZOP style (qualitative; no numeric consequence is claimed). PSM requires a PHA incl. siting (S5, R)")
    rows = [("Node", "Deviation", "Cause", "Consequence", "Safeguard", "Action (A)"),
            ("N1 MR-701 loop", "more pressure", "condenser fouling or cooling loss; non-condensables; discharge blocked", "overpressure, release via PSV-701 (cloud depends on refrigerant)", "PSH-701; PSV-701 to RH-701", "name the refrigerant; size PSV for fire and blocked discharge"),
            ("N2 MR-701", "loss of containment", "seal, flange, hose or relief-valve failure", "toxic, asphyxiant or flammable atmosphere; cold burns", "AT-701, AT-702; SV-701; EF-701", "detector height by gas density; set points; ventilation rate"),
            ("N3 BL-501", "less water", "feedwater loss; FWT-501 empty", "tube overheating and failure", "LSLL-501 to BMS-501", "independent sensor; proof-test interval"),
            ("N4 BL-501, header", "more pressure", "firing control failure; header valves closed", "pressure above MAWP", "PT-501 trip; PSV-501, PSV-502", "size PSV for rated output; boiler code"),
            ("N5 steam header", "steam release", "flange or pipe failure; TCV failed open", "scald; loss of blanching and pasteurising", "XV-502 ESDV; PSV-502", "route and shield; isolation valve location"),
            ("N6 E-301, HT-301, FDV-301", "less temperature or time", "steam loss; TCV-301 stuck; hold tube fouled; excess flow", "under-processed product to the filler", "TIC-301, TSL-302 divert; BT-301; HACCP; LAB-801", "critical limit and hold time from process authority; divert-valve test"),
            ("N7 E-301", "tube leak or rupture", "corrosion; thermal fatigue", "steam into product or product into steam; contamination", "PSV-301; steam below product MAWP (A)", "set pressure differential; leak detection"),
            ("N8 DA-201, VC-201", "loss of vacuum or vacuum collapse", "vacuum source fails; vent blocked; condenser cooling lost", "air ingress; vessel collapse if vent blocked", "VB-201; design for full vacuum (A)", "confirm design basis and vacuum source"),
            ("N9 CIP-901", "wrong chemical or mixing", "acid and chlorine-based liquor mixed; wrong hose", "toxic gas; burns; product contamination", "segregated storage; dedicated connectors (A); PPE", "gap: no free source read; supplier data sheets"),
            ("N10 ETP-601", "high load", "pulp dump; peel-water surge; CIP slug", "biological upset; consent breach; odour", "S-601; TK-601; LT-601, AT-601", "size from the Rev B load, not 568 mg/L (sheet 2)")]
    y = wtable(s, 20, y, (115, 105, 230, 230, 215, 205), rows, 9.5, 11.5, 3)
    if y > 1112: print("WARNING sheet 7 overflow", y)
    xr = 1135
    y9 = section(s, xr, 84, 445, "HOW TO READ THIS SHEET")
    yy = y9 + 14
    for t_ in ("SIF targets are assumptions to be replaced by a hazard and risk study (LOPA or equivalent). The free sources read give separation of control and protection (S2) and the need to test credited layers (S10); the SIL method text is paywalled.",
               "Demand rates and failure data are not given: no frequency or SIL claim is made.",
               "Hazard nodes follow the checklist item 'HAZOP node list and PHA incl. facility siting' (S5). Consequences are qualitative; numbers need the refrigerant, charge and boiler data listed on sheets 3 to 5.",
               "Nodes N1 and N2 are refrigerant-dependent. If ammonia is chosen, treat as toxic: SIF-1 target and room ventilation are then reviewed (conditional, S6 and S7 as reported)."):
        yy = WRAP(s, xr + 10, yy, t_, 80, 9.5, 12, bullet=True) + 5
    return s


# ---- sheet 8: detection, mitigation, layout, inherently safer design
def sheet_safety_detect():
    s = Sheet(8, "SAFETY DESIGN BASIS (Rev B) 3 of 3: detection, mitigation, layout, inherently safer design", "Safety design basis, detection and ISD",
              code="VS-FV", project="Fruit and vegetable processing, 10,000 t/yr raw", basis="SAFETY_FEATURES_CHECKLIST.md; marks R / A / gap")
    frame(s, NS)
    y = section(s, 20, 84, 1100, "DETECTION AND MITIGATION")
    rows = [("Item", "Basis / logic", "Mark", "Source or gap"),
            ("Gas detection, MR-701", "two detectors (AT-701, AT-702) with alarm and high-high executive action (SIF-1). Height by gas density: ammonia vapour is lighter than air when warm, halocarbons and CO2 are heavier; so the refrigerant sets the placement.", "A; R conditional (ammonia)", "S7 as reported (dual detectors); IIAR 2 / EN 378 gap"),
            ("Machinery-room ventilation", "continuous ventilation plus emergency extract EF-701 started by detection; discharge to a safe outdoor location away from air intakes and people. Air-change rate: not set.", "A; R for discharge location", "S11 (discharge is a design item); rate: gap (IIAR 2, EN 378)"),
            ("Boiler house", "fuel is not in the source. If gas-fired: gas proving, leak test and detection per burner standard; flame failure trips XV-501 (SIF-5).", "A; gap", "burner standard and HSE PM5 (404) not obtained"),
            ("Isolation of inventories", "XV-501 (fuel), XV-502 (steam), SV-701 (refrigerant liquid): remotely operated, fail closed on loss of power. No large flammable inventory exists on this plant.", "R", "S1 para 128"),
            ("Refrigerant relief and venting", "PSV-401, 402, 701 into RH-701, vent outdoors. Ammonia (conditional): scrubber or flare for relief and vents; dual PRVs with 3-way valve.", "A; R conditional", "S6, S7 as reported; IIAR 2 gap"),
            ("Bund / impoundment", "no bulk flammable liquid: none drawn. Boiler fuel oil, caustic, acid: bund 110 % of the largest vessel or 25 % of total capacity. Rule is for flammable liquids; used for CIP chemicals by analogy.", "R (fuel); A (CIP)", "S1 HSG176 para 157"),
            ("Layout and distances", "MR-701 and BH-501 apart from occupied areas and exits; consider domino escalation and occupied buildings. Spacing table in S1 applies only to flammable-liquid tanks (1 m for up to 1 m3, to 15 m above 250 m3).", "R (principle); A (positions)", "S1 Table 1; S3"),
            ("Fire water and foam", "fire NOC is named in the source (section 6): its requirements set fire water; foam not needed for the process fluids drawn (A). No free source read for food-plant fire water.", "R (NOC); gap", "NOC requirements to obtain; NFPA 30 / OISD not obtained"),
            ("Hot-fill / aseptic sterility CCP", "calibrated temperature sensor and recorder after HT-301, flow diversion FDV-301, hold time from the validated schedule, batch hold until LAB-801 release. Detection of loss of sterility is by monitoring, not by a gas detector.", "R (HACCP, lab)", "source sec. 12; limits: gap (process authority)"),
            ("CIP chemical handling", "caustic and acid in separate bunded storage; dedicated connectors; no mixing of acid with chlorine-based liquor; eyewash and shower at the dosing point; dosing pump leak containment.", "A; gap", "no free source read; supplier safety data sheets"),
            ("Inerting", "not applicable: no flammable process atmosphere (fruit, water, steam). Machinery-room atmosphere is controlled by ventilation.", "A", "-")]
    y = wtable(s, 20, y, (180, 560, 150, 210), rows, 9.5, 11.5, 3)
    y = section(s, 20, y + 10, 1100, "INHERENTLY SAFER DESIGN OPTIONS (4 to 6, specific to this process)")
    rows = [("Option", "Idea", "Mark / source"),
            ("1 Substitute the refrigerant, or use an indirect loop", "choose a refrigerant with lower toxicity or flammability, or confine a small primary charge to MR-701 and send chilled brine or glycol to F-401 and CS-401: smaller inventory near people.", "A (no free source for the choice); S7 describes ammonia practice"),
            ("2 Reduce steam pressure and energy", "blanch and pasteurise at the lowest steam pressure that meets the duty (4 bar a drawn; BREF Table 8.6 tests at 7 bar); belt blancher with water cooler recovers heat (0.09 t/t against 0.16).", "S BREF Tables 8.6, 8.7 (read); A for pressure"),
            ("3 Moderate the boiler rating", "boiler MAWP only above what the header needs (6.0 against 5.0 barg here); smaller steam inventory in the header.", "A"),
            ("4 Separate the CCP from control", "give TSL-302 / FDV-301 their own sensor and valve, not shared with TIC-301 / TCV-301.", "R: S2 (separate protection and control)"),
            ("5 Reduce inventory at the receiver", "smallest receiver that supports pump-down; machinery room on an outside wall with its discharge away from intakes.", "A; S11 for discharge"),
            ("6 Reduce hazardous CIP chemicals", "lowest effective caustic and acid strength; avoid chlorine-based sanitiser with acid cleaners on the same skid.", "A")]
    y = wtable(s, 20, y, (230, 650, 220), rows, 9.5, 11.5, 3)
    if y > 1112: print("WARNING sheet 8 overflow", y)
    xr = 1135
    y9 = section(s, xr, 84, 445, "STANDARDS TO OBTAIN (gaps behind the rows)")
    yy = y9 + 14
    for t_ in ("IIAR 2 and EN 378 (refrigeration machinery rooms, detectors, ventilation, relief); IEC 61511 and a LOPA text (SIL method); API 520 / 521 / 526 and ASME VIII (relief sizing); boiler code and burner standard (PM5 returned 404); NFPA 30 / 58 and OISD standards (paywalled, INR 10,500 each plus GST) if fuel storage is added; PESO rules; FSSAI and process-authority limits for the CCP.",
               "Free sources read are S1 to S3, S5 to S7, S10, S11. Nothing paywalled is reproduced here.",
               "Rev B does not change the process-safety character of the set: no large flammable inventory; the hazards are refrigerant release, steam and boiler, and loss of sterility."):
        yy = WRAP(s, xr + 10, yy, t_, 80, 9.5, 12, bullet=True) + 5
    return s


def build_all():
    return [sheet_pid(), sheet_hmb(), sheet_hmb_notes(), sheet_s12(), sheet_s34(), sheet_safety_relief(), sheet_safety_sif(), sheet_safety_detect()]


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, "Fruit and vegetable plant P&ID set Rev B", previews="--previews" in sys.argv)
    print(f"ok {len(sheets)} sheets; closure in {B['mi']:,.1f} kg/h out {B['mo']:,.1f} kg/h error {abs(B['mi']-B['mo'])/B['mi']*100:.3f} %")

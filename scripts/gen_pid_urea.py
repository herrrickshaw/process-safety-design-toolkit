#!/usr/bin/env python3
"""Generate the coal-to-urea conceptual P&ID set, Rev B (VS-UREA): P&ID, heat and material balance (HMB), four scenario sheets and three
safety-design-basis sheets (relief schedule, ESD cause-and-effect + SIF list, detection / hazard identification / inherently safer design).

PROCESS BASIS: the repo /Users/umashankar/coal-to-urea-design-opensource (module coal_to_urea/, example examples/full_chain_worked_example.py).
That repo needs scipy and CoolProp, which this generator must not import (standard library only). So the generator re-implements the repo equations
(gasifier elemental balance + water-gas-shift equilibrium, two shift stages, acid-gas removal, ammonia loop algebra, urea conversion fit) with the
standard library, and asserts that with every Rev B change switched OFF it reproduces the repo's own recorded outputs (REPO_RUN, tag S).

REV B CHANGES to that repo basis (each is a flag in balance(); the Rev A numbers are recomputed here with the flags off, never typed):
  1 water-gas-shift K: thermodynamic fit instead of Moe 1962 (frozen constants from thermo/CoolProp, tests/crosscheck/urea_revb_constants.py)
  2 condensate knock-out V-203 after the shift (water vapour left at the 40 C saturation value, Psat from CoolProp)
  3 methanation R-301: residual CO and CO2 converted, H2 consumed 3 CO + 4 CO2, CH4 and water formed (D)
  4 purge-gas recovery PGR-401 (recovery fraction A) returning H2/N2 to K-401
  5 urea train with full carbamate recycle (stripping family): all unconverted NH3 and CO2 return to R-601 (S24 internal)
  6 plant rating: the coal feed is scaled so that urea = 1.10 Mt/a (the repo example at 145 kg/s coal and full recycle would make about 2.9 Mt/a)
  7 ASU power 275 kWh/t O2 (TDA / DOE-FE-0026142 range 250-300), utilities per t urea from UBA 2001, K-401 from a CoolProp run

Usage (standard library only):
    python3 scripts/gen_pid_urea.py docs/pid/UREA_PID_Set_RevB.html [--previews] [--results docs/pid/validation/UREA_REVB_RESULTS]
                                    [--dump-json file.json] [--verify-repo PATH]
Screening aid, not certified design."""
import sys, os, math, textwrap, re, json, csv
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.dirname(_HERE))          # worktree root, for process_safety (stdlib relief sizing)
from pidlib import *

# =====================================================================================================================
# 1. PROCESS BASIS AND BALANCE (computed in code)
# =====================================================================================================================
AWT = {"C": 12.011, "H": 1.008, "O": 15.999, "N": 14.007, "S": 32.06}
MW = {"H2O": 18.015, "O2": 31.998, "CO": 28.01, "CO2": 44.01, "H2": 2.016, "H2S": 34.08, "N2": 28.014, "NH3": 17.031,
      "UREA": 60.06, "CH4": 12.011 + 4 * 1.008, "Cs": 12.011, "Ha": 1.008, "Oa": 15.999, "Na": 14.007, "Sa": 32.06, "ASH": 1000.0}  # ASH: mol/s == kg/s
ELEM = {"H2O": {"H": 2, "O": 1}, "O2": {"O": 2}, "CO": {"C": 1, "O": 1}, "CO2": {"C": 1, "O": 2}, "H2": {"H": 2}, "H2S": {"H": 2, "S": 1},
        "N2": {"N": 2}, "NH3": {"N": 1, "H": 3}, "UREA": {"C": 1, "H": 4, "N": 2, "O": 1}, "CH4": {"C": 1, "H": 4}, "Cs": {"C": 1}, "Ha": {"H": 1},
        "Oa": {"O": 1}, "Na": {"N": 1}, "Sa": {"S": 1}, "ASH": {}}

COAL = dict(carbon=0.420, hydrogen=0.029, oxygen=0.052, nitrogen=0.008, sulfur=0.013, ash=0.350, moisture=0.128)   # gasifier.py TYPICAL_INDIAN_HIGH_ASH
COAL_REPO = 145.0; O2_RATIO = 0.55; STEAM_RATIO = 0.10; GASIFIER_K = 1673.15; C_CONV = 0.90
HT_K, HT_APPR, HT_STEAM = 623.15, 20.0, 0.30
LT_K, LT_APPR, LT_STEAM = 493.15, 10.0, 0.10
CO2_REMOVAL, H2S_REMOVAL = 0.97, 0.999
SPASS_CONV, PURGE_FRAC = 0.19, 0.02
TARGET_NC = 3.5
MTPA = 1.0e9 / (365.25 * 24 * 3600)   # kg/s per Mt/a, from the repo example
UREA_TARGET_MTPA = 1.10               # Rev B rating (the title of Rev A); see RATING box on sheet 2

# Values recorded by RUNNING the repo (examples/full_chain_worked_example.py chain, plus size_asu_for_o2_demand), 11 Nov 2026.  Tag S.
REPO_RUN = dict(syngas_mol_s=8584.471712010187, syngas_kg_s=182.5295371218393, unconv_c_kg_s=6.09, cge=0.6407146272117067,
                ht_flow=11159.813225613241, ht_conv=0.7968840521245049, lt_flow=12275.794548174566, lt_conv=0.8588404586144854,
                co2_cap_mol_s=4320.896612617275, h2s_cap_mol_s=58.737211478477846, treated_mol_s=7896.160724078813,
                nh3_mol_s=3469.325697879775, recycle_mol_s=28988.955147125955, purge_mol_s=591.6113295331827,
                co2_to_urea=991.2359136799357, urea_kg_s=34.76763932176029, unconv_nh3=2311.5621507016103,
                unconv_co2=412.3541400908533, asu_o2_air_kg_s=342.40808800550036, asu_o2_n2_kg_s=262.6580880055003,
                asu_o2_power_kW=210684.75529720605, urea_conv=0.584, conv_nc4375=0.68725)

# ---- Rev B frozen constants.  Provenance: /private/tmp/claude-501/venv_val/bin/python tests/crosscheck/urea_revb_constants.py  (run 11 Nov 2026;
#      CoolProp 8.0, thermo 0.6.1, chemicals 1.5.2, numpy).  Tag S (tool run); the script prints every number below.
WGS_FIT = (-16.23016869, 5566.907387, 1.629001945, -0.0002220309557)   # ln K = a + b/T + c ln T + d T, fit of thermo K(T) 450-2000 K, max error 0.67 % in K
K_THERMO = {1673.15: 0.30682, 643.15: 16.76587, 503.15: 128.60960}      # thermo K at the three stage temperatures (printed by the script)
DH_WGS_HT, DH_WGS_LT = 38.41, 39.76          # kJ/mol released at 643 K and 503 K, thermo Cp integrals (script); Rev A used 41.2 (298 K value)
DH_NH3_700K = 52.34                          # kJ/mol NH3, ideal gas at 700 K, thermo Cp integrals (validator recompute.py); Rev A used 46.1 (298 K)
PSAT_H2O_40C_KPA = 7.3849                    # CoolProp 8.0 water at 313.15 K
K401_KJ_PER_MOL = 7.4560                     # CoolProp HEOS mixture, 3:1 H2:N2, 313.15 K, 40 -> 200 bar, isentropic eta 0.75 (pure-component cross-check 7.430)
HHV_CO_KJ, HHV_H2_KJ = 282.95, 285.81        # kJ/mol, thermo Hf (CO2, CO, H2O gas) plus CoolProp latent heat of water at 298 K
NH3_HFG_MINUS33C = 1368.7; NH3_RHO_MINUS33C = 681.2   # kJ/kg and kg/m3, CoolProp, saturated liquid at 240.15 K
# ---- Rev B sourced utility figures (documents fetched and read)
ASU_KWH_PER_T_O2 = 275.0; ASU_RANGE = (250.0, 300.0)   # TDA Research final report DOE-FE-0026142 (30 Jul 2019), pdf p.12 "250-300 kWh per ton of O2"; single source
UBA_STEAM_T_PER_T = 0.92; UBA_STEAM_RANGE = (0.85, 1.30)   # UBA 2001 sec 2.5.2.3: 0.92 Stamicarbon (p.19), 0.85 Snam (p.24), median 1.3 all processes (p.18)
UBA_CW_T_PER_T = 70.0                                    # UBA 2001 p.20 (Stamicarbon); Snam 75 (p.24)
UBA_KWH_EXCL_CO2 = 43.0; UBA_KWH_GRAN = 23.0              # UBA p.20: 43 kWh/t urea without CO2 compressor, +23 granulation (Toyo)
UBA_CO2_COMP_KWH_PER_T_CO2 = 126.0                       # UBA p.24: Snam 115 kWh/t incl. CO2 compressor, 21-23 without; (115-22)/0.733 = 126 kWh/t CO2 (D)
UBA_PROCESS_WATER_M3 = (0.46, 0.65)                      # UBA p.19, p.25 (discharged process water per t urea)
# ---- Rev B assumptions (A)
PURGE_RECOVERY = 0.90                                    # A: H2/N2 recovered from the loop purge (range 0.85-0.95); not sourced
P_AGR_KPA, P_METH_KPA = 4500.0, 4000.0                   # A1/A3 pressures at the two knock-outs


def bisect(f, lo, hi, n=300):
    flo = f(lo); fhi = f(hi)
    assert flo * fhi <= 0, "no sign change"
    for _ in range(n):
        mid = 0.5 * (lo + hi); fm = f(mid)
        if flo * fm <= 0: hi, fhi = mid, fm
        else: lo, flo = mid, fm
    return 0.5 * (lo + hi)


def wgs_K_moe(T): return math.exp(4577.8 / T - 4.33)       # Moe 1962, as used in the repo gasifier.py and shift_reactor.py (Rev A)
def wgs_K_thermo(T):
    a, b, c, d = WGS_FIT
    return math.exp(a + b / T + c * math.log(T) + d * T)


def mass(sp):  # kg/s of a species dict (mol/s)
    return sum(n * MW[k] for k, n in sp.items()) / 1000.0


def elements(sp):  # mol/s of each element
    e = {}
    for k, n in sp.items():
        for el, c in ELEM[k].items(): e[el] = e.get(el, 0.0) + c * n
    return e


def gasify(coal_kg_s, Kfn):
    """gasifier.gasify_coal re-implemented (elemental balance + WGS equilibrium)"""
    c = COAL
    nC0 = coal_kg_s * c["carbon"] * 1000 / AWT["C"]; nH = coal_kg_s * c["hydrogen"] * 1000 / AWT["H"]
    nO = coal_kg_s * c["oxygen"] * 1000 / AWT["O"]; nN = coal_kg_s * c["nitrogen"] * 1000 / AWT["N"]
    nS = coal_kg_s * c["sulfur"] * 1000 / AWT["S"]; nWm = coal_kg_s * c["moisture"] * 1000 / MW["H2O"]
    o2_kg = coal_kg_s * O2_RATIO; nO2 = o2_kg * 1000 / MW["O2"]
    st_kg = coal_kg_s * STEAM_RATIO; nSt = st_kg * 1000 / MW["H2O"]
    nC = nC0 * C_CONV
    nHt = nH + 2 * (nWm + nSt); nOt = nO + (nWm + nSt) + 2 * nO2; nH2eq = nHt / 2
    K = Kfn(GASIFIER_K); A = 2 * nC + nH2eq - nOt
    res = lambda nCO: (nC - nCO) * (A - nCO) - K * nCO * (nH2eq - (A - nCO))
    nCO = bisect(res, max(1e-9, A - nH2eq), min(nC, A) - 1e-9)
    gas = {"CO": nCO, "CO2": nC - nCO, "H2": A - nCO, "H2O": nH2eq - (A - nCO), "H2S": nS, "N2": nN / 2}
    coal = {"Cs": nC0, "Ha": nH, "Oa": nO, "Na": nN, "Sa": nS, "H2O": nWm, "ASH": coal_kg_s * c["ash"]}
    slag = {"Cs": nC0 - nC, "ASH": coal_kg_s * c["ash"]}
    return coal, {"O2": nO2}, {"H2O": nSt}, gas, slag, K, o2_kg, st_kg


def shift(sp, steam_frac, T, appr, Kfn):
    """shift_reactor.shift_reactor re-implemented"""
    tot = sum(sp.values()); steam = steam_frac * tot
    nCO, nW, nCO2, nH2 = sp["CO"], sp["H2O"] + steam, sp["CO2"], sp["H2"]
    K = Kfn(T + appr)
    xi = bisect(lambda x: (nCO2 + x) * (nH2 + x) - K * (nCO - x) * (nW - x), 0.0, min(nCO, nW) - 1e-9)
    out = dict(sp); out.update({"CO": nCO - xi, "H2O": nW - xi, "CO2": nCO2 + xi, "H2": nH2 + xi})
    return {"H2O": steam}, out, xi / nCO


class Bal:
    """one converged balance (a namespace)"""
    pass


def balance(coal_kg_s, revb=True):
    """revb=False reproduces the repo example exactly (Rev A); revb=True applies the Rev B changes 1-5."""
    b = Bal(); b.revb = revb; b.coal_kg_s = coal_kg_s
    Kfn = wgs_K_thermo if revb else wgs_K_moe
    coal, o2s, sts, gas, slag, K, o2_kg, st_kg = gasify(coal_kg_s, Kfn)
    ht_st, ht, ht_conv = shift(gas, HT_STEAM, HT_K, HT_APPR, Kfn)
    lt_st, lt, lt_conv = shift(ht, LT_STEAM, LT_K, LT_APPR, Kfn)
    cond1 = {}; cond2 = {}
    if revb:   # V-203: cool to 40 C, knock out condensate; vapour left at saturation (ideal gas, Raoult-type: y = Psat/P, no solubility of CO2/H2S in the water: A)
        nd = sum(v for k, v in lt.items() if k != "H2O")
        n_w = min(nd * PSAT_H2O_40C_KPA / (P_AGR_KPA - PSAT_H2O_40C_KPA), lt["H2O"])
        cond1 = {"H2O": lt["H2O"] - n_w}; agr_in = dict(lt); agr_in["H2O"] = n_w
    else:
        agr_in = lt
    co2_cap = agr_in["CO2"] * CO2_REMOVAL; h2s_cap = agr_in["H2S"] * H2S_REMOVAL
    treated = dict(agr_in); treated["CO2"] -= co2_cap; treated["H2S"] -= h2s_cap
    b.meth_h2 = 3 * treated["CO"] + 4 * treated["CO2"]          # mol/s H2 a methanator consumes (D)
    if revb:   # R-301: CO + 3 H2 = CH4 + H2O ; CO2 + 4 H2 = CH4 + 2 H2O ; complete conversion (A: real units leave ppm CO/CO2)
        nCO, nCO2 = treated["CO"], treated["CO2"]
        mo = dict(treated); mo["H2"] = treated["H2"] - b.meth_h2; mo["CO"] = 0.0; mo["CO2"] = 0.0; mo["CH4"] = nCO + nCO2
        w_tot = treated["H2O"] + nCO + 2 * nCO2
        nd2 = sum(v for k, v in mo.items() if k != "H2O")
        w_v = nd2 * PSAT_H2O_40C_KPA / (P_METH_KPA - PSAT_H2O_40C_KPA)
        cond2 = {"H2O": w_tot - w_v}
        purif = {k: v for k, v in mo.items() if k not in ("H2", "CO", "CO2", "H2O") and v > 0}; purif["H2O"] = w_v
        h2 = mo["H2"]
    else:
        purif = {k: v for k, v in treated.items() if k != "H2"}; h2 = treated["H2"]
    n2_loop = h2 / 3.0
    air_mol = o2s["O2"] / 0.21; air = {"O2": 0.21 * air_mol, "N2": 0.79 * air_mol}
    n2_surplus = air["N2"] - n2_loop
    assert n2_surplus > 0
    # ammonia loop (ammonia_synthesis.ammonia_synthesis_loop) with optional purge-gas recovery r returned to the K-401 suction
    F_f = h2 + n2_loop; X, p = SPASS_CONV, PURGE_FRAC
    D = 1 - (1 - p) * (1 - X); r = PURGE_RECOVERY if revb else 0.0
    F = F_f / (1 - r * p * (1 - X) / D)                      # total gas into the loop = fresh + recovered
    inlet = F / D; Rr = (1 - p) * (1 - X) * inlet; nh3 = 0.5 * X * inlet; purge_tot = p * (1 - X) * inlet
    rec = r * purge_tot; purge = purge_tot - rec
    assert abs((F - rec) - F_f) < 1e-9 * F_f
    fh = 0.75
    # urea
    if revb:
        urea = nh3 / 2.0; assert urea <= co2_cap
        conv = min(max(0.171 + 0.118 * TARGET_NC, 0.05), 0.85)
        co2_tot = urea / conv; nh3_tot = TARGET_NC * co2_tot
        co2_u, co2_s = urea, co2_cap - urea
        rec_nh3, rec_co2 = nh3_tot - nh3, co2_tot - urea
    else:
        co2_u = min(nh3 / TARGET_NC, co2_cap); co2_s = co2_cap - co2_u
        conv = min(max(0.171 + 0.118 * (nh3 / co2_u), 0.05), 0.85); urea = conv * co2_u
        rec_nh3, rec_co2 = nh3 - 2 * urea, co2_u - urea
    S = {}
    S[1] = coal; S[2] = o2s; S[3] = sts; S[4] = gas; S[5] = slag; S[6] = ht_st; S[7] = ht; S[8] = lt_st; S[9] = lt
    S[10] = {"CO2": co2_cap}; S[11] = {"H2S": h2s_cap}; S[12] = treated
    S[13] = purif
    S[14] = {"N2": n2_loop}; S[15] = {"H2": fh * F, "N2": (1 - fh) * F}
    S[16] = {"H2": purge * fh, "N2": purge * (1 - fh)}
    S[17] = {"NH3": nh3}; S[18] = {"NH3": nh3}; S[19] = {"CO2": co2_u}; S[20] = {"CO2": co2_s}
    S[21] = {"UREA": urea, "H2O": urea, "NH3": rec_nh3, "CO2": rec_co2}
    S[22] = {"UREA": urea}; S[23] = {"H2O": urea}; S[24] = {"NH3": rec_nh3, "CO2": rec_co2}
    S[25] = air; S[26] = {"N2": n2_surplus}
    S[27] = {"H2": Rr * fh, "N2": Rr * (1 - fh)}
    S[28] = cond1; S[29] = cond2; S[30] = {"H2": rec * fh, "N2": rec * (1 - fh)}
    b.__dict__.update(S=S, K=K, ht_conv=ht_conv, lt_conv=lt_conv, o2_kg=o2_kg, st_kg=st_kg, F=F, F_f=F_f, Rr=Rr, inlet=inlet, nh3=nh3, purge=purge,
                      rec=rec, co2_cap=co2_cap, co2_u=co2_u, co2_s=co2_s, urea=urea, conv=conv, air_mol=air_mol, n2_loop=n2_loop, h2=h2,
                      h2s_cap=h2s_cap, n2_surplus=n2_surplus, treated_mol=sum(treated.values()), syn_mol=sum(gas.values()),
                      treated_h2o_frac=treated["H2O"] / sum(treated.values()), rec_nh3=rec_nh3, rec_co2=rec_co2)
    return b


def near(a, b, tol=1e-7, what=""):
    assert abs(a - b) <= tol * max(1.0, abs(b)), f"repo mismatch {what}: {a} vs {b}"


# ---- Rev A = the repo example, flags off: asserted against the recorded repo run
A = balance(COAL_REPO, revb=False); SA = A.S
MA = {k: mass(v) for k, v in SA.items()}; MA[1] = COAL_REPO
near(A.syn_mol, REPO_RUN["syngas_mol_s"], what="syngas mol/s"); near(MA[4], REPO_RUN["syngas_kg_s"], 1e-4, "syngas kg/s")
near(SA[5]["Cs"] * 12.011 / 1000, REPO_RUN["unconv_c_kg_s"], what="unconverted C")
near(sum(SA[7].values()), REPO_RUN["ht_flow"], what="HT flow"); near(A.ht_conv, REPO_RUN["ht_conv"], what="HT conv")
near(sum(SA[9].values()), REPO_RUN["lt_flow"], what="LT flow"); near(A.lt_conv, REPO_RUN["lt_conv"], what="LT conv")
near(A.co2_cap, REPO_RUN["co2_cap_mol_s"], what="CO2 captured"); near(A.h2s_cap, REPO_RUN["h2s_cap_mol_s"], what="H2S captured")
near(A.treated_mol, REPO_RUN["treated_mol_s"], what="treated gas"); near(A.nh3, REPO_RUN["nh3_mol_s"], what="NH3")
near(A.Rr, REPO_RUN["recycle_mol_s"], what="recycle"); near(A.purge, REPO_RUN["purge_mol_s"], what="purge")
near(A.co2_u, REPO_RUN["co2_to_urea"], what="CO2 to urea"); near(MA[22], REPO_RUN["urea_kg_s"], what="urea kg/s")
near(SA[24]["NH3"], REPO_RUN["unconv_nh3"], what="unconv NH3"); near(SA[24]["CO2"], REPO_RUN["unconv_co2"], what="unconv CO2")
near(MA[25], REPO_RUN["asu_o2_air_kg_s"], 1e-4, "ASU air kg/s"); near(A.conv, REPO_RUN["urea_conv"], what="urea conversion")
CGE_A = (SA[4]["CO"] * HHV_CO_KJ + SA[4]["H2"] * HHV_H2_KJ) / 1000.0 / (COAL_REPO * (33.87 * COAL["carbon"] + 144.3 * (COAL["hydrogen"] - COAL["oxygen"] / 8.0) + 9.4 * COAL["sulfur"]))
near(CGE_A, REPO_RUN["cge"], 2e-3, "cold gas efficiency from frozen HHVs")

# ---- Rev B: rating. All flows are homogeneous of degree 1 in the coal feed, so the coal feed that gives 1.10 Mt/a urea follows from one trial run.
_trial = balance(COAL_REPO, revb=True); _trial_urea = mass(_trial.S[22])
COAL_KG_S = COAL_REPO * UREA_TARGET_MTPA * MTPA / _trial_urea
B = balance(COAL_KG_S, revb=True); S = B.S
_chk = balance(2 * COAL_KG_S, revb=True); near(mass(_chk.S[22]), 2 * mass(S[22]), 1e-9, "linearity in coal feed")
M = {k: mass(v) for k, v in S.items()}; M[1] = COAL_KG_S
BOUND_IN = (1, 3, 6, 8, 25); BOUND_OUT = (5, 11, 13, 16, 20, 22, 23, 26, 28, 29)   # S24 and S30 are internal recycles in Rev B


def tot_el(ids, SS):
    e = {}
    for i in ids:
        for el, v in elements(SS[i]).items(): e[el] = e.get(el, 0.0) + v
    return e


M_IN = sum(M[i] for i in BOUND_IN); M_OUT = sum(M[i] for i in BOUND_OUT)
ERR_MASS = (M_OUT - M_IN) / M_IN * 100
E_IN, E_OUT = tot_el(BOUND_IN, S), tot_el(BOUND_OUT, S)
ELERR = {el: (E_OUT.get(el, 0) - E_IN[el]) / E_IN[el] * 100 for el in "CHONS"}
assert abs(ERR_MASS) < 0.1, ERR_MASS
for el in "CONS": assert abs(ELERR[el]) < 1e-6, (el, ELERR[el])
H_EXCESS = E_OUT["H"] - E_IN["H"]      # the repo gasifier gives H2S two H atoms its H balance never deducts: out - in = 2 x n(H2S) exactly
assert abs(H_EXCESS - 2 * S[4]["H2S"]) < 1e-6 * E_IN["H"], (H_EXCESS, 2 * S[4]["H2S"])
# Rev A closure for the change box (boundary S24 leaves)
_oA = (5, 11, 13, 16, 20, 22, 23, 24, 26)
ERR_MASS_A = (sum(MA[i] for i in _oA) - sum(MA[i] for i in BOUND_IN)) / sum(MA[i] for i in BOUND_IN) * 100

H2_MASS = B.h2 * MW["H2"] / 1000.0
STAGES = [("Gasifier  (1+2+3 = 4+5)", (1, 2, 3), (4, 5), 0.0), ("HT shift  (4+6 = 7)", (4, 6), (7,), 0.0), ("LT shift  (7+8 = 9)", (7, 8), (9,), 0.0),
          ("V-203 + AGR  (9 = 28+10+11+12)", (9,), (28, 10, 11, 12), 0.0),
          ("R-301 + V-302  (12 = 13+29 + H2 to loop)", (12,), (13, 29), H2_MASS),
          ("K-401 make-up  (14 + H2 + 30 = 15)", (14, 30), (15,), -H2_MASS),
          ("Loop  (15 = 17+16+30)", (15,), (17, 16, 30), 0.0), ("Urea reactor  (18+19+24 = 21)", (18, 19, 24), (21,), 0.0),
          ("Urea train  (21 = 22+23+24)", (21,), (22, 23, 24), 0.0), ("ASU  (25 = 2+14+26)", (25,), (2, 14, 26), 0.0)]
# (the two H2 terms put the fresh H2 mass, which is in S15 but not a numbered stream upstream, on the right side)


def stage_rows():
    rows = []
    for name, ins, outs, adj in STAGES:
        a = sum(M[i] for i in ins); b_ = sum(M[i] for i in outs) + (adj if adj > 0 else 0.0); a += (-adj if adj < 0 else 0.0)
        assert abs(b_ - a) / a * 100 < 0.1, (name, a, b_)
        rows.append((name, a * 3.6, b_ * 3.6, (b_ - a) / a * 100))
    return rows


STAGE_ROWS = stage_rows()
# loop element checks
nl = elements(S[17]); pl = elements(S[16]); ml = elements(S[15]); rl = elements(S[30])
for el in "NH": assert abs(nl[el] + pl[el] + rl[el] - ml[el]) < 1e-6 * ml[el]
assert abs(M[10] - M[19] - M[20]) < 1e-9 and abs(M[17] - M[18]) < 1e-9

# ---- derived quantities (Rev B and Rev A)
def hhv_coal_MJ_kg(): c = COAL; return 33.87 * c["carbon"] + 144.3 * (c["hydrogen"] - c["oxygen"] / 8.0) + 9.4 * c["sulfur"]
HHV_COAL = hhv_coal_MJ_kg(); Q_COAL = COAL_KG_S * HHV_COAL
Q_SYN = (S[4]["CO"] * HHV_CO_KJ + S[4]["H2"] * HHV_H2_KJ) / 1000.0; CGE_B = Q_SYN / Q_COAL
UREA_T_H = M[22] * 3.6; UREA_MTPA = M[22] / MTPA; UREA_TPD = M[22] * 86.4; NH3_TPD = M[17] * 86.4
Q_HT = B.ht_conv * S[4]["CO"] * DH_WGS_HT / 1000.0; Q_LT = B.lt_conv * S[7]["CO"] * DH_WGS_LT / 1000.0
Q_NH3 = B.nh3 * DH_NH3_700K / 1000.0
O2_T_H = M[2] * 3.6; ASU_MW = ASU_KWH_PER_T_O2 * O2_T_H / 1000.0
ASU_MW_LO, ASU_MW_HI = ASU_RANGE[0] * O2_T_H / 1000.0, ASU_RANGE[1] * O2_T_H / 1000.0
K401_MW = K401_KJ_PER_MOL * B.F / 1000.0
K601_MW = UBA_CO2_COMP_KWH_PER_T_CO2 * M[19] * 3.6 / 1000.0
ELEC_OTHER_MW = (UBA_KWH_EXCL_CO2 + UBA_KWH_GRAN) * UREA_T_H / 1000.0
STEAM_UREA_T_H = UBA_STEAM_T_PER_T * UREA_T_H; CW_T_H = UBA_CW_T_PER_T * UREA_T_H
CO_METH_H2 = B.meth_h2; CO_METH_PCT = CO_METH_H2 / (B.h2 + CO_METH_H2) * 100      # share of the H2 leaving the AGR (D)
NC_20 = TARGET_NC / 0.8; CONV_20 = min(max(0.171 + 0.118 * NC_20, 0.05), 0.85)
near(min(max(0.171 + 0.118 * 4.375, 0.05), 0.85), REPO_RUN["conv_nc4375"], what="fit at N/C 4.375")
UREA_20_PCT = (CONV_20 * 0.8 * B.co2_u / B.co2_u / B.conv - 1) * 100       # per-pass conversion sensitivity only (production is recycle-limited in Rev B)


def per_t(x_kg_s, urea_kg_s): return x_kg_s / urea_kg_s
def intensities(bal, MM, coal):
    u = MM[22]; n = MM[17]
    return dict(nh3_per_urea=MM[18] / u, co2_per_urea=MM[19] / u, coal_per_urea=coal / u, coal_per_nh3=coal / n,
                makeup_nm3_per_t_nh3=(bal.F - bal.rec) * 22.414e-3 * 3600 / (n * 3.6), steam_gasifier_per_urea=(MM[3] + MM[6] + MM[8]) / u,
                cond_per_urea=(MM[28] + MM[29]) / u, reaction_water_per_urea=MM[23] / u, co2_vent_per_urea=MM[20] / u,
                meth_pct=(bal.meth_h2 / (bal.h2 + bal.meth_h2) * 100) if bal.revb else 0.0, urea_mtpa=u / MTPA, nh3_tpd=n * 86.4, urea_tpd=u * 86.4,
                co_syn=bal.S[4]["CO"], h2_syn=bal.S[4]["H2"], treated_h2o_pct=bal.treated_h2o_frac * 100)
IA = intensities(A, MA, COAL_REPO); IB = intensities(B, M, COAL_KG_S)
# Option 1 (keep the repo example coal feed, recycle on) for the rating box
OPT1 = balance(COAL_REPO, revb=True); OPT1_UREA_MTPA = mass(OPT1.S[22]) / MTPA


def verify_repo(path):
    """optional: run the real repo functions and compare with this re-implementation (flags off)"""
    import types
    cp = types.ModuleType("CoolProp"); cpc = types.ModuleType("CoolProp.CoolProp"); cp.CoolProp = cpc
    sys.modules.setdefault("CoolProp", cp); sys.modules.setdefault("CoolProp.CoolProp", cpc)
    sys.path.insert(0, path)
    from coal_to_urea.gasifier import TYPICAL_INDIAN_HIGH_ASH, gasify_coal
    from coal_to_urea.shift_reactor import shift_reactor
    from coal_to_urea.acid_gas_removal import remove_acid_gases
    from coal_to_urea.ammonia_synthesis import ammonia_synthesis_loop
    from coal_to_urea.urea_synthesis import synthesize_urea
    g = gasify_coal(TYPICAL_INDIAN_HIGH_ASH, COAL_REPO, O2_RATIO, STEAM_RATIO, GASIFIER_K, C_CONV)
    ht = shift_reactor(g.syngas_composition_mole_frac, g.syngas_molar_flow_mol_s, g.syngas_molar_flow_mol_s * HT_STEAM, HT_K, HT_APPR)
    lt = shift_reactor(ht.outlet_composition_mole_frac, ht.outlet_molar_flow_mol_s, ht.outlet_molar_flow_mol_s * LT_STEAM, LT_K, LT_APPR)
    a = remove_acid_gases(lt.outlet_composition_mole_frac, lt.outlet_molar_flow_mol_s, CO2_REMOVAL, H2S_REMOVAL)
    h2 = a.treated_gas_composition_mole_frac["Hydrogen"] * a.treated_gas_molar_flow_mol_s
    n = ammonia_synthesis_loop(h2, h2 / 3, SPASS_CONV, PURGE_FRAC)
    u = synthesize_urea(n.nh3_product_mol_s, min(n.nh3_product_mol_s / TARGET_NC, a.captured_co2_molar_flow_mol_s))
    near(g.syngas_molar_flow_mol_s, A.syn_mol, 1e-9, "verify syngas"); near(a.captured_co2_molar_flow_mol_s, A.co2_cap, 1e-9, "verify CO2")
    near(n.nh3_product_mol_s, A.nh3, 1e-9, "verify NH3"); near(u.urea_produced_mass_flow_kg_s, MA[22], 1e-9, "verify urea")
    print("repo verification passed (Rev A flags off)")


def f1(x): return f"{x:,.1f}"
def f0(x): return f"{x:,.0f}"
def f2(x): return f"{x:,.2f}"
def f3(x): return f"{x:,.3f}"
def tph(i): return M[i] * 3.6


# =====================================================================================================================
# 2. DRAWING HELPERS AND PLANT
# =====================================================================================================================
DIAM = {}


def sd(s, x, y, n, dy=-22, dx=0):
    """stream diamond for the line point (x,y): placed dy above/below it (dy != 0) or dx beside it (dy == 0), joined by a short tick"""
    if dy == 0:
        sg = 1 if dx > 0 else -1
        PL(s, [(x, y), (x + dx - 11 * sg, y)], 0.9, "#777")
    else:
        PL(s, [(x, y), (x, y + dy + (11 if dy < 0 else -11))], 0.9, "#777")
    DIAM.setdefault(s.no, set()).add(n); strm(s, x + dx, y + dy, n)


def lab(s, x, y, t, size=9.5, w=400, anchor="start", fill=INK): T(s, x, y, t, size, w, anchor, fill)


def hop(s, x, y):
    """line-jump on a horizontal line at (x,y)"""
    s.add(f'<line x1="{x-7}" y1="{y}" x2="{x+7}" y2="{y}" stroke="#fff" stroke-width="5"/>')
    s.add(f'<path d="M{x-7},{y} A7,7 0 0 1 {x+7},{y}" fill="none" stroke="{INK}" stroke-width="2.6"/>')


def psv_dn(s, x, y, color=INK):
    """relief valve, inlet from above at (x, y-16), outlet to the right at (x+18, y)"""
    s.add(f'<g transform="translate(0,{2*y}) scale(1,-1)">'); psv(s, x, y, color); s.add('</g>')


def util(s, x, y, text, d="r", anchor="start"):
    """labelled utility stub: arrow pointing d (r,l,u,d) ending at (x,y)"""
    L = 22
    a = {"r": [(x - L, y), (x, y)], "l": [(x + L, y), (x, y)], "u": [(x, y + L), (x, y)], "d": [(x, y - L), (x, y)]}[d]
    PL(s, a, 1.4, GREEN); arrow(s, x, y, d, GREEN, 6)
    tx, ty = {"r": (a[0][0] - 3, y + 3), "l": (a[0][0] + 3, y + 3), "u": (x + 4, y + L + 9), "d": (x + 4, y - L - 3)}[d]
    T(s, tx, ty, text, 9, 400, "end" if d == "r" else "start", GREEN)


def xv(s, x, y, tag, rot=0, lx=0, ly=-14, anchor="middle", note=None):
    valve(s, x, y, rot, "gate", act=True, color=RED)
    T(s, x + lx, y + ly, tag, 10, 700, anchor, RED)
    if note: T(s, x + lx, y + ly + 11, note, 9, 400, anchor, RED)


def cv(s, x, y, tag, rot=0, lx=0, ly=-14, anchor="middle"):
    ctrlvalve(s, x, y, rot); T(s, x + lx, y + ly, tag, 10, 700, anchor)


def box(s, x, y, w, h, title, sub=None, fill="#eef3fb", stroke=INK):
    R(s, x, y, w, h, fill, stroke, 2)
    T(s, x + w / 2, y + 15, title, 11, 700, "middle")
    if sub:
        for i, t in enumerate(sub): T(s, x + w / 2, y + 28 + i * 11.5, t, 9, 400, "middle")


# ---------- coordinates of the plant drawing (shared by all sheets) ----------
LOWY = 523
XVP = {"XV-101": (215, 205, 0), "XV-102": (241, 150, 0), "XV-103": (180, 262, 90), "XV-501": (188, 726, 0),
       "XV-502": (300, 576, 90), "XV-602": (860, 650, 0), "XV-603": (790, 735, 90)}


def plant(s):
    """equipment, process lines, stream diamonds (all sheets). Instruments are added by pid_instruments()."""
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    # ---------------- band 1: ASU, gasification, shift (left to right)
    box(s, 30, 135, 80, 130, "ASU-101", ["cryogenic", "air separation", "O2 to R-101", "N2 to loop", "surplus N2 S26"])
    pipe(s, [(70, 265), (70, 300)]); sd(s, 70, 285, 26, 0, 28); lab(s, 64, 282, "N2 vent", 9.5, 400, "end")
    pipe(s, [(70, 90), (70, 135)]); sd(s, 70, 106, 25, 0, 28); lab(s, 62, 100, "air", 9.5, 400, "end")
    box(s, 150, 112, 72, 24, "F-101", None)
    pipe(s, [(186, 90), (186, 112)]); sd(s, 186, 100, 1, 0, 28); lab(s, 178, 104, "coal", 9.5, 400, "end")
    pipe(s, [(186, 136), (186, 150), (260, 150)])
    g = vvessel(s, 290, 128, 60, 120)
    lab(s, 290, 92, "entrained-flow, 1400 C", 9, 400, "middle"); lab(s, 290, 103, "R-101", 11, 700, "middle")
    pipe(s, [(110, 205), (260, 205)]); sd(s, 120, 205, 2, -22)
    pipe(s, [(180, 296), (180, 232), (260, 232)]); sd(s, 180, 282, 3, 0, -26); lab(s, 186, 306, "HP steam", 9.5)
    pipe(s, [(290, 265), (290, 274)], arrow_=False)
    R(s, 272, 274, 36, 18, "#eee", INK, 1.6); lab(s, 290, 287, "V-102", 9.5, 700, "middle")
    pipe(s, [(308, 283), (352, 283)]); sd(s, 330, 283, 5, -22); lab(s, 358, 287, "slag + char", 9.5)
    # syngas path
    pipe(s, [(320, 170), (365, 170)], arrow_=False); sd(s, 342, 170, 4, 22)
    hx(s, 400, 170, 70, 28); lab(s, 400, 202, "E-101", 10, 700, "middle")
    PL(s, [(385, 128), (385, 156)], 1.4, GREEN); arrow(s, 385, 156, "d", GREEN, 6); lab(s, 391, 126, "BFW", 9, 400, "start", GREEN)
    PL(s, [(417, 156), (417, 128)], 1.4, GREEN); arrow(s, 417, 128, "u", GREEN, 6); lab(s, 423, 126, "HP stm", 9, 400, "start", GREEN)
    pipe(s, [(435, 170), (508, 170)], arrow_=False)
    pipe(s, [(468, 117), (468, 170)]); sd(s, 468, 140, 6, 0, 24)
    vvessel(s, 535, 125, 54, 90); lab(s, 505, 226, "R-201", 10, 700, "end"); lab(s, 505, 237, "HT shift 350 C", 9, 400, "end")
    pipe(s, [(562, 170), (586, 170)], arrow_=False); sd(s, 574, 170, 7, -22)
    hx(s, 615, 170, 58, 28); lab(s, 615, 202, "E-102", 10, 700, "middle")
    pipe(s, [(644, 170), (673, 170)], arrow_=False)
    pipe(s, [(655, 117), (655, 170)]); sd(s, 655, 134, 8, 0, -24)
    vvessel(s, 700, 125, 54, 90); lab(s, 672, 226, "R-202", 10, 700, "end"); lab(s, 672, 237, "LT shift 220 C", 9, 400, "end")
    pipe(s, [(727, 170), (760, 170)], arrow_=False)
    hx(s, 790, 170, 60, 28); lab(s, 790, 138, "E-103", 10, 700, "middle"); util(s, 790, 198, "CW", "u")
    pipe(s, [(820, 170), (840, 170), (840, 350), (815, 350), (815, 362)]); sd(s, 840, 250, 9, 0, 26)
    vvessel(s, 815, 372, 36, 60); lab(s, 815, 392, "V-203", 9.5, 700, "middle"); lab(s, 815, 403, "KO", 9, 400, "middle")
    pipe(s, [(833, 400), (840, 400), (840, 452), (852, 452)])
    pipe(s, [(815, 442), (815, 480)]); sd(s, 815, 470, 28, 0, 26); lab(s, 815, 494, "condensate", 9, 400, "middle"); lab(s, 815, 504, "to stripper (A)", 9, 400, "middle")

    # ---------------- band 2: AGR, methanation, ammonia loop (right to left)
    vvessel(s, 880, 362, 56, 120, packing=True)
    lab(s, 880, 538, "C-301 absorber", 10.5, 700, "middle")
    vvessel(s, 990, 362, 56, 120)
    lab(s, 990, 538, "C-302", 10.5, 700, "middle"); lab(s, 990, 550, "regenerator", 10.5, 700, "middle")
    pipe(s, [(880, 346), (880, 336), (700, 336), (700, 366)]); hop(s, 840, 336); sd(s, 730, 336, 12, -22)
    # rich / lean solvent
    pipe(s, [(908, 470), (962, 470)])
    pipe(s, [(990, 498), (990, 512), (916, 512), (916, 380), (908, 380)])
    s.add(f'<line x1="916" y1="462" x2="916" y2="478" stroke="#fff" stroke-width="5"/><path d="M916,462 A7,7 0 0 0 916,478" fill="none" stroke="{INK}" stroke-width="2.6"/>')
    pump(s, 952, 512, 11, None); lab(s, 940, 528, "P-301", 9.5, 700, "middle")
    # acid gases
    pipe(s, [(990, 346), (990, 336), (1105, 336)]); sd(s, 1095, 336, 11, -22)
    lab(s, 1103, 354, "to sulphur", 9.5, 400, "end"); lab(s, 1103, 365, "recovery (A)", 9.5, 400, "end")
    pipe(s, [(1018, 390), (1040, 390), (1040, 650), (937, 650)]); sd(s, 1040, 520, 10, 0, -26)
    pipe(s, [(1040, 430), (1105, 430)]); sd(s, 1075, 430, 20, -22)
    lab(s, 1103, 452, "surplus CO2", 9.5, 400, "end"); lab(s, 1103, 463, "vent (A)", 9.5, 400, "end")
    # methanation and make-up
    vvessel(s, 700, 380, 50, 95)
    lab(s, 730, 476, "R-301", 10, 700); lab(s, 730, 487, "methanation", 9)
    pipe(s, [(725, 430), (775, 430)]); sd(s, 750, 430, 13, -22); lab(s, 735, 452, "residual", 9.5)
    pipe(s, [(700, 489), (700, LOWY), (691, LOWY)], arrow_=False)
    hvessel(s, 672, LOWY, 24, 22); lab(s, 672, 503, "V-302", 9.5, 700, "middle")
    pipe(s, [(653, LOWY), (617, LOWY)], arrow_=False)
    pipe(s, [(672, 540), (672, 562)]); sd(s, 672, 552, 29, 0, 24)
    pipe(s, [(60, 265), (60, 318), (650, 318), (650, LOWY)], arrow_=False); sd(s, 110, 318, 14, 22)
    lab(s, 70, 312, "N2 from ASU", 9.5, 400); sd(s, 633, LOWY, 15, -22)
    compressor(s, 600, LOWY, 17); lab(s, 600, 487, "K-401", 10, 700, "middle"); lab(s, 600, 498, "make-up", 9, 400, "middle")
    # loop
    vvessel(s, 480, 406, 60, 100)
    lab(s, 470, 580, "R-401 NH3 converter", 10, 700, "end"); lab(s, 470, 591, "450 C, 200 bar", 9, 400, "end")
    pipe(s, [(583, LOWY), (545, LOWY), (545, 365), (480, 365), (480, 389)])
    pipe(s, [(480, 523), (480, LOWY), (435, LOWY)], arrow_=False)
    hx(s, 400, LOWY, 70, 28); lab(s, 400, LOWY - 22, "E-401", 10, 700, "middle"); lab(s, 400, LOWY + 29, "cooler / chiller", 9, 400, "middle")
    pipe(s, [(365, LOWY), (342, LOWY)], arrow_=False)
    hvessel(s, 300, LOWY, 60, 40)
    lab(s, 250, 542, "V-401", 10, 700, "end"); lab(s, 250, 553, "NH3 separator", 9.5, 400, "end")
    pipe(s, [(300, 503), (300, 350), (480, 350), (480, 365)], arrow_=False)
    arrow(s, 300, 410, "u")
    compressor(s, 390, 350, 14); lab(s, 390, 328, "K-402", 10, 700, "middle")
    sd(s, 440, 350, 27, 22)
    pipe(s, [(300, 420), (205, 420)])
    box(s, 125, 395, 80, 50, "PGR-401", ["purge-gas", "recovery (A)"])
    pipe(s, [(125, 420), (95, 420)]); sd(s, 100, 420, 16, -22); lab(s, 28, 446, "net purge to fuel (A)", 9, 400, "start")
    pipe(s, [(165, 395), (165, 322)]); sd(s, 165, 358, 30, 0, 26); lab(s, 214, 355, "recovered H2/N2", 9, 400); lab(s, 214, 366, "to K-401 (S30)", 9, 400)

    # liquid NH3 to storage
    pipe(s, [(300, 556), (300, 600), (110, 600), (110, 636)])
    sd(s, 255, 600, 17, 22)
    # ---------------- band 3: NH3 storage and urea train
    tank(s, 110, 745, 120, 95, "T-501 NH3 storage", None, roof="dome", level=0.7)
    pipe(s, [(170, 726), (201, 726)], arrow_=False)
    pump(s, 215, 726, 14, "P-501")
    pipe(s, [(229, 712), (240, 712), (240, 752), (790, 752), (790, 714)]); sd(s, 330, 752, 18, -22)
    vvessel(s, 790, 600, 64, 96)
    lab(s, 830, 700, "R-601", 11, 700); lab(s, 830, 711, "urea reactor", 9); lab(s, 830, 722, "180 C, 150 bar", 9)
    compressor(s, 920, 650, 17); lab(s, 958, 612, "K-601", 10, 700, "middle"); lab(s, 958, 623, "CO2 compressor", 9.5, 400, "middle")
    pipe(s, [(903, 650), (822, 650)]); sd(s, 840, 650, 19, 22)
    vvessel(s, 680, 600, 56, 96)
    lab(s, 680, 733, "C-601 HP stripper", 10, 700, "middle"); lab(s, 640, 746, "MP steam 0.92 t/t urea (S)", 9, 400, "start", GREEN)
    pipe(s, [(758, 640), (708, 640)]); sd(s, 733, 640, 21, 22)
    pipe(s, [(680, 584), (680, 572), (654, 572)], arrow_=False)
    hx(s, 625, 572, 58, 24); lab(s, 662, 556, "E-601 condenser", 9.5, 700, "end")
    pipe(s, [(625, 584), (625, 752)]); sd(s, 625, 630, 24, 0, -24)
    lab(s, 590, 610, "carbamate recycle", 9.5, 400, "end"); lab(s, 590, 621, "to R-601 (A)", 9.5, 400, "end")

    pipe(s, [(652, 696), (615, 696)])
    hx(s, 580, 696, 70, 28); lab(s, 545, 664, "E-602 evaporator", 10, 700, "end")
    pipe(s, [(545, 696), (500, 696)]); sd(s, 522, 696, 22, -22)
    box(s, 430, 671, 70, 50, "G-601", ["granulation"])
    pipe(s, [(430, 696), (330, 696)]); lab(s, 330, 688, "urea to store (A)", 9.5, 400, "end")
    pipe(s, [(580, 710), (580, 736)]); sd(s, 580, 724, 23, 0, 26); lab(s, 574, 746, "process water", 9.5, 400, "end")
    # flare (band 1, right)
    flare(s, 1060, 294, 120, "")
    lab(s, 1068, 184, "FL-101", 10, 700, "start"); lab(s, 1068, 195, "flare (A)", 9.5, 400, "start")
    hvessel(s, 1040, 294, 20, 16); lab(s, 1068, 284, "KO-101", 9.5, 700, "start")
    hop(s, 625, 696)

# =====================================================================================================================
# 3. REV B DRAWING ADDITIONS: small relief valve, instruments, sheet-1 panel
# =====================================================================================================================
class SheetB(Sheet):
    """Sheet with the Rev B header (pidlib.frame prints Rev A; post-processed here, pidlib is not edited)"""
    def svg(self):
        return super().svg().replace("|  Rev A<", "|  Rev B<").replace("Draft A. Screening aid, not certified design", "Rev B draft. Screening aid, not certified design")


def psv_s(s, x, y, tag, inlet=None, outlet=None, lab_xy=None, anchor="start", flip=False):
    """small relief valve (scale 0.7). Upright: inlet at (x, y+11) below the body, outlet stub to the right. flip=True: inlet above (x, y-11)."""
    iy = y - 11 if flip else y + 11
    if inlet: PL(s, list(inlet) + [(x, iy)], 2.2)
    sc = "0.7,-0.7" if flip else "0.7"
    s.add(f'<g transform="translate({x},{y}) scale({sc})">'); psv(s, 0, 0); s.add('</g>')
    PL(s, [(x + 12.6, y)] + (list(outlet) if outlet else [(x + 20, y)]), 1.8, GREY, "5 3")
    if lab_xy: T(s, lab_xy[0], lab_xy[1], tag, 9.5, 700, anchor)


TRIPS = [("AT", "102"), ("AT", "103"), ("AT", "201"), ("BE", "101"), ("AT", "401"), ("AT", "501"), ("AT", "502"), ("AT", "601"),
         ("PSHH", "101"), ("TAHH", "201"), ("PSHH", "401"), ("PSHH", "601"), ("LSHH", "501"), ("LSLL", "401"), ("FALL", "602"), ("HS", "001")]


def pid_instruments(s):
    """control loops, relief devices, ESD valves, detectors (sheet 1)"""
    cv(s, 150, 205, "FV-102", 0, 27, -9); bubble(s, 150, 158, "FIC", "102", True); PL(s, [(150, 173), (150, 181)], 1.2, BLUE, "5 4")
    xv(s, 215, 205, "XV-101", 0, 0, -26)
    xv(s, 241, 150, "XV-102", 0, 0, -30)
    xv(s, 180, 262, "XV-103", 90, -14, 4, "end")
    bubble(s, 352, 126, "PIC", "101", True); PL(s, [(337, 126), (322, 126)], 1.2, BLUE, "5 4")
    # relief: PSV-101 keeps its drawn header FL-1
    PL(s, [(320, 215), (350, 215)], 2.6); psv_dn(s, 350, 232)
    PL(s, [(368, 232), (410, 232), (410, 294), (1060, 294)], 2.2, GREY, "7 4")
    lab(s, 416, 258, "PSV-101", 9.5, 700); lab(s, 655, 289, "flare header FL-1 (A)", 9.5, 400, "middle", GREY)
    bubble(s, 375, 262, "AT", "101", True)
    xv(s, 495, 294, "BDV-101", 0, 0, -30)
    psv_s(s, 238, 274, "PSV-102", [(272, 288), (238, 288)], lab_xy=(246, 250), anchor="end")
    # shift
    cv(s, 468, 150, "FV-201", 90, -14, 4, "end"); bubble(s, 468, 102, "FIC", "201", True); PL(s, [(468, 117), (468, 120)], 1.0, BLUE)
    psv_s(s, 550, 262, "PSV-201", [(550, 228), (550, 251)], [(575, 262), (575, 294)], (582, 258), flip=True)
    psv_s(s, 715, 262, "PSV-202", [(715, 228), (715, 251)], [(740, 262), (740, 294)], (746, 258), flip=True)
    # AGR, methanation
    bubble(s, 790, 312, "AT", "301", True); PL(s, [(790, 327), (790, 336)], 1.0, BLUE, "5 4")
    ctrlvalve(s, 938, 470, 90); lab(s, 938, 496, "LV-301", 9.5, 700, "middle")
    bubble(s, 938, 436, "LIC", "301", True); PL(s, [(938, 451), (938, 462)], 1.2, BLUE, "5 4")
    bubble(s, 665, 440, "TI", "301", False)
    psv_s(s, 940, 341, "PSV-301", [(908, 352), (940, 352)], [(953, 341), (965, 341), (965, 294)], (940, 316), "middle")
    psv_s(s, 1000, 317, "PSV-302", [(1000, 336)], [(1022, 317), (1022, 294)], (1028, 323))
    psv_s(s, 750, 361, "PSV-303", [(725, 392), (750, 392)], None, (764, 358))
    # loop
    ctrlvalve(s, 265, 420, 0); lab(s, 265, 446, "PV-401", 9.5, 700, "middle")
    bubble(s, 265, 386, "PIC", "401", True); PL(s, [(265, 401), (265, 412)], 1.2, BLUE, "5 4")
    ctrlvalve(s, 300, 600, 90); lab(s, 334, 604, "LV-401", 9.5, 700)
    bubble(s, 225, 600, "LIC", "401", True); PL(s, [(240, 600), (292, 600)], 1.2, BLUE, "5 4")
    bubble(s, 507, 440, "TI", "401", False)
    psv_s(s, 322, 462, "PSV-401", [(322, 507), (322, 473)], None, (348, 466))
    psv_s(s, 425, 400, "PSV-402", [(450, 415), (425, 415)], None, (425, 436), "middle")
    # NH3 storage
    xv(s, 188, 726, "XV-501", 0, 0, -28)
    bubble(s, 35, 672, "LIT", "501", True); PL(s, [(35, 687), (35, 695), (50, 695)], 1.2, BLUE, "5 4")
    psv_s(s, 192, 635, "PSV-501", [(170, 664), (192, 664)], None, (214, 639))
    psv_s(s, 75, 606, "PSV-502", [(75, 641)], None, (63, 610), "end")
    PL(s, [(150, 641), (150, 636)], 2.4); valve(s, 150, 628, 90, "check"); lab(s, 158, 616, "VB-501", 9.5, 700)
    # urea
    xv(s, 860, 650, "XV-602", 0, 0, -34)
    bubble(s, 960, 700, "UIC", "601", True); lab(s, 980, 698, "anti-surge / trip", 9.5); PL(s, [(955, 685), (935, 667)], 1.2, BLUE, "5 4")
    cv(s, 500, 752, "FV-601", 0, -12, -7, "end"); bubble(s, 528, 718, "FFIC", "601", True); PL(s, [(528, 733), (528, 740), (500, 740), (500, 737)], 1.2, BLUE, "5 4")
    xv(s, 790, 735, "XV-603", 90, 30, 4, "start")
    bubble(s, 822, 556, "PIC", "601", True); PL(s, [(822, 571), (822, 598)], 1.0, BLUE, "5 4")
    psv_s(s, 850, 574, "PSV-601", [(822, 603), (850, 603)], None, (864, 578))
    psv_s(s, 733, 612, "PSV-602", [(708, 626), (733, 626)], None, (733, 592), "middle")
    psv_s(s, 892, 628, "PSV-603", [(892, 650)], None, (892, 598), "middle")
    xv(s, 300, 576, "XV-502", 90, -14, 4, "end")
    # detector / trip points (locations in the panel table; grid keeps the plant drawing legible)
    lab(s, 888, 166, "detector / trip points (see panel)", 9, 400, "start", GREY)
    for i, (a, b_) in enumerate(TRIPS):
        bubble(s, 890 + 40 * (i % 4), 184 + 31 * (i // 4), a, b_, True)
    # ESD / F&G logic box
    R(s, 830, 94, 190, 56, "#fff3e0", RED, 1.8)
    lab(s, 925, 111, "ESD / F&G LOGIC (A)", 11, 700, "middle", RED)
    lab(s, 925, 125, "ESD-1..4 and manual HS-001: matrix on", 9, 400, "middle", RED)
    lab(s, 925, 137, "sheet 6; relief schedule on sheet 5", 9, 400, "middle", RED)


def legend(s, x, y):
    items = [("process line", INK, None, 2.6), ("ESD output (A)", RED, "6 4", 1.5), ("instrument signal", BLUE, "5 4", 1.3),
             ("utility stub", GREEN, None, 1.5), ("relief header / outlet (A)", GREY, "7 4", 2.2)]
    for i, (tx, c, d, w) in enumerate(items):
        PL(s, [(x, y + i * 14), (x + 30, y + i * 14)], w, c, d); T(s, x + 36, y + 4 + i * 14, tx, 9.5)
    valve(s, x + 215, y, 0, "gate", act=True, color=RED); T(s, x + 232, y + 4, "ESD valve XV (A)", 9.5)
    ctrlvalve(s, x + 215, y + 30); T(s, x + 232, y + 34, "control valve", 9.5)
    s.add(f'<g transform="translate({x+215},{y+62}) scale(0.7)">'); psv(s, 0, 0); s.add('</g>'); T(s, x + 232, y + 62, "relief valve PSV (A), set in sheet 5", 9.5)
    WRAP(s, x, y + 90, "S sourced (repo or fetched document), D derived, A assumed by this drawing, R recommended by a named free source.", 70, 9.5, 11.5)


def key_panel(s):
    panel_box(s)
    y = section(s, 1135, 84, 445, "PROCESS BASIS (Rev B; repo example plus the Rev B changes)")
    items = [
        f"Coal {COAL_KG_S:.1f} kg/s ({COAL_KG_S*3.6:,.0f} t/h), Indian high-ash preset. Rating set so that urea = {UREA_MTPA:.2f} Mt/a (sheet 2, rating box). Gasifier 1400 C, O2/coal 0.55, steam/coal 0.10, carbon conversion 90 %.",
        f"Two-stage shift, V-203 knock-out, AGR 97 % CO2 / 99.9 % H2S, R-301 methanation, loop 19 % per pass with 90 % purge recovery (A), urea at N/C 3.5 with full carbamate recycle.",
        f"Result: NH3 {M[17]*3.6:,.1f} t/h ({NH3_TPD:,.0f} t/d), urea {UREA_T_H:,.1f} t/h ({UREA_TPD:,.0f} t/d). CO2 surplus {M[20]*3.6:,.1f} t/h vented.",
        "The repo has no safety content: every relief, detector and trip on this sheet is A unless sheet 5-7 names a source (R)."]
    yy = y + 16
    for t in items: yy = WRAP(s, 1145, yy, t, 78, 10, 12, ) + 4
    y = section(s, 1135, yy + 2, 445, "KEY INSTRUMENTS AND TRIP POINTS (all A; ESD logic sheet 6)")
    rows = [("Tag", "Service / location"),
            ("FIC-102, XV-101/102/103", "O2 ratio; O2 / coal / steam trip to R-101"),
            ("PIC-101, PSHH-101", "gasifier pressure; high-high trip (ESD-1)"),
            ("AT-101, AT-102", "CO/H2 detectors, gasifier hall (2oo3 with BE-101)"),
            ("AT-103", "O2 enrichment, ASU / O2 line"), ("BE-101", "flame detector, R-101 burner and E-101"),
            ("AT-201, TAHH-201", "CO/H2 shift area; HT shift outlet T"), ("AT-301", "H2S / CO at AGR, C-301/302"),
            ("PIC-401, PSHH-401", "loop pressure; high-high trips K-401/402"),
            ("LIC-401, LSLL-401", "V-401 level; low-low stops gas blow-by"),
            ("AT-401", "NH3 detector at V-401 / loop (A)"), ("AT-501, AT-502", "NH3 detectors, T-501 outlet and bund"),
            ("LIT-501, LSHH-501", "tank level; high-high stops filling"), ("XV-501, XV-502", "T-501 outlet / V-401 liquid isolation"),
            ("FFIC-601, FALL-602", "N/C feed ratio; low CO2 flow trip"), ("PIC-601, PSHH-601", "R-601 pressure; high-high trip"),
            ("UIC-601, XV-602/603", "K-601 anti-surge; CO2 / NH3 isolation"), ("HS-001", "manual ESD push-button, control room")]
    yy = table(s, 1135, y + 2, (150, 295), rows, 15, 9.5)
    legend(s, 1150, yy + 20)
    return yy


EQUIP = [("Tag", "Service", "Basis"),
         ("ASU-101", "Cryogenic ASU, O2 to R-101, N2 to loop", "S repo; power S TDA"),
         ("F-101", "Coal mill and pressurisation lock hoppers", "A"),
         ("R-101", "Entrained-flow slagging gasifier, 1400 C", "S gasifier.py"),
         ("V-102", "Slag quench / lock hopper", "A"), ("E-101", "Syngas cooler / quench, steam raising", "A"),
         ("R-201", "HT water-gas shift, 350 C", "S shift_reactor.py"), ("E-102", "Shift interstage cooler", "A"),
         ("R-202", "LT water-gas shift, 220 C", "S shift_reactor.py"), ("E-103", "Gas cooler to V-203 / AGR", "A"),
         ("V-203", "Condensate knock-out after shift (Rev B)", "D Psat CoolProp; A"),
         ("C-301", "CO2 / H2S absorber", "S acid_gas_removal.py"), ("C-302", "Solvent regenerator, CO2 and H2S off", "A"),
         ("P-301", "Lean solvent pump", "A"), ("R-301", "Methanation CO / CO2 to CH4 (Rev B)", "D stoichiometry; A"),
         ("V-302", "Methanator effluent cooler + KO drum", "A"), ("PGR-401", "Purge-gas recovery unit, 90 % (A)", "A")]
EQUIP2 = [("Tag", "Service", "Basis"),
          ("K-401", "Make-up compressor 40 to 200 bar", "S call; power S CoolProp"), ("K-402", "Loop circulator", "A"),
          ("R-401", "NH3 converter, 450 C, 200 bar", "S ammonia_synthesis.py"), ("E-401", "Converter effluent cooler / chiller", "A"),
          ("V-401", "NH3 separator", "A"), ("T-501", "NH3 refrigerated storage (type A)", "A"), ("P-501", "NH3 feed pump", "A"),
          ("K-601", "CO2 compressor to urea pressure", "A; power S UBA"), ("R-601", "Urea reactor, 180 C, 150 bar", "S urea_synthesis.py"),
          ("C-601", "HP CO2 stripper (stripping family)", "A; UBA p.13"), ("E-601", "HP carbamate condenser, recycle to R-601", "A"),
          ("E-602", "Evaporation / concentration", "A"), ("G-601", "Granulation", "A"), ("KO-101", "Flare knock-out drum", "A"),
          ("FL-101", "Flare", "A")]


def sheet1():
    s = SheetB(1, "Coal-to-urea complex: P&ID (conceptual)", "Sheet 1: P&ID, whole process", code="VS-UREA",
               project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)", basis="repo example + Rev B HMB corrections, 11 Nov 2026")
    frame(s, 7)
    plant(s); pid_instruments(s)
    y = section(s, 20, 784, 1100, "EQUIPMENT LIST   (S sourced, D derived, A assumed by this drawing)   Line numbers and sizes TBD")
    table(s, 20, y, (58, 255, 237), EQUIP, 15.2, 9.5)
    table(s, 570, y, (58, 255, 237), EQUIP2, 15.2, 9.5)
    key_panel(s)
    return s


# =====================================================================================================================
# 4. SHEET 2: HEAT AND MATERIAL BALANCE, RATING, REV A TO REV B CHANGES
# =====================================================================================================================
TP = {1: (("25", "A"), ("1", "A")), 2: (("40", "A"), ("50", "A")), 3: (("400", "A"), ("50", "A")), 4: (("1400", "S"), ("45", "A")),
      5: (("80", "A"), ("1", "A")), 6: (("400", "A"), ("50", "A")), 7: (("350", "S"), ("45", "A")), 8: (("400", "A"), ("50", "A")),
      9: (("220", "S"), ("45", "A")), 10: (("40", "A"), ("2", "A")), 11: (("40", "A"), ("2", "A")), 12: (("40", "S"), ("40", "S")),
      13: (("40", "A"), ("40", "A")), 14: (("40", "A"), ("40", "A")), 15: (("40", "S"), ("40", "S")), 16: (("40", "A"), ("200", "S")),
      17: (("-33", "A"), ("1.1", "A")), 18: (("40", "A"), ("150", "S")), 19: (("40", "A"), ("150", "S")), 20: (("40", "A"), ("2", "A")),
      21: (("180", "S"), ("150", "S")), 22: (("60", "A"), ("1", "A")), 23: (("100", "A"), ("1", "A")), 24: (("170", "A"), ("150", "A")),
      25: (("25", "A"), ("1", "A")), 26: (("25", "A"), ("1", "A")), 27: (("40", "A"), ("200", "S")), 28: (("40", "A"), ("45", "A")),
      29: (("40", "A"), ("40", "A")), 30: (("40", "A"), ("40", "A"))}
PHASE = {1: "solid", 5: "solid", 17: "liq", 18: "liq", 21: "liq", 22: "solid", 23: "liq", 24: "liq", 28: "liq", 29: "liq"}
STREAM_KEY = {1: "Coal to F-101 / R-101", 2: "Oxygen ASU-101 to R-101", 3: "HP steam to R-101", 4: "Raw syngas R-101 to E-101",
              5: "Slag and unconverted char", 6: "HP steam to R-201", 7: "HT shift outlet", 8: "Steam to R-202", 9: "LT shift outlet",
              10: "CO2 captured (C-302)", 11: "H2S acid gas to sulphur", 12: "Treated gas to R-301", 13: "Purification residual (CH4, N2, H2S, vapour)",
              14: "N2 from ASU to K-401", 15: "Gas to K-401 (fresh + S30)", 16: "Net loop purge to fuel", 17: "Liquid NH3 to T-501",
              18: "NH3 feed to R-601 (P-501)", 19: "CO2 to R-601 (K-601)", 20: "Surplus CO2, vent / CCUS", 21: "Urea reactor effluent",
              22: "Urea product (G-601)", 23: "Process water (E-602)", 24: "Carbamate recycle E-601 to R-601", 25: "Air to ASU-101",
              26: "Surplus N2 (vent / other use)", 27: "Loop recycle gas", 28: "Condensate V-203 (to stripper, A)",
              29: "Condensate V-302 (A)", 30: "Recovered purge gas PGR-401 to K-401"}
COMP_ROWS = [("Organic coal+moisture / char C", ("Cs", "Ha", "Oa", "Na", "Sa", "H2O*")), ("Ash", ("ASH",)), ("O2", ("O2",)), ("N2", ("N2",)),
             ("H2", ("H2",)), ("CO", ("CO",)), ("CO2", ("CO2",)), ("CH4", ("CH4",)), ("H2O", ("H2O",)), ("H2S", ("H2S",)), ("NH3", ("NH3",)), ("Urea", ("UREA",))]


def rowmass(i, keys):
    m = 0.0
    for k in keys:
        kk = k.rstrip("*")
        if k.endswith("*") and i != 1: continue
        if kk == "H2O" and not k.endswith("*") and i == 1: continue
        m += S[i].get(kk, 0.0) * MW[kk] / 1000.0
    return m


def hmb_rows():
    ids = sorted(S)
    rows = [("Phase", [PHASE.get(i, "gas") for i in ids]), ("Temperature, C  (S/A)", [f"{TP[i][0][0]} {TP[i][0][1]}" for i in ids]),
            ("Pressure, bar  (S/A)", [f"{TP[i][1][0]} {TP[i][1][1]}" for i in ids]), ("Mass flow, t/h  (D)", [f1(tph(i)) for i in ids]),
            ("Mole flow, kmol/h  (D)", ["-" if i in (1, 5) else f1(sum(S[i].values()) * 3.6) for i in ids]), ("Composition, mass %  (D)", None)]
    for name, keys in COMP_ROWS:
        rows.append((name, ["-" if rowmass(i, keys) == 0 else f"{rowmass(i, keys)/M[i]*100:.1f}" for i in ids]))
    for i in ids:
        assert abs(sum(rowmass(i, k) for _, k in COMP_ROWS) / M[i] - 1) < 1e-9, i
    rows.append(("Total, mass %", ["100.0"] * len(ids)))
    return rows


def makeup_for_r(r):
    """fresh make-up Nm3 per t NH3 at purge recovery r (same loop algebra as balance())"""
    D = 1 - (1 - PURGE_FRAC) * (1 - SPASS_CONV)
    F = B.F_f / (1 - r * PURGE_FRAC * (1 - SPASS_CONV) / D); nh3 = 0.5 * SPASS_CONV * F / D
    return B.F_f * 22.414e-3 * 3600 / (nh3 * 17.031 / 1000 * 3.6)


def changes_rows():
    ia, ib = IA, IB
    return [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
            ("NH3 per t urea, t/t", f3(ia["nh3_per_urea"]), f3(ib["nh3_per_urea"]), "S Talcher 0.571 (TEIA); UBA; D stoich 0.567", "full recycle; S24 internal; mass error unchanged"),
            ("CO2 per t urea, t/t", f3(ia["co2_per_urea"]), f3(ib["co2_per_urea"]), "S Talcher 0.740 (TPFR Table E.1); D 0.733", "CO2 vent rises to " + f1(M[20] * 3.6) + " t/h"),
            ("Urea output, Mt/a at repo coal 145 kg/s", f2(ia["urea_mtpa"]), f2(OPT1_UREA_MTPA), "D balance, recycle on", f"NOT built: {OPT1_UREA_MTPA/1.27:.1f} x Talcher 1.27 Mt/a"),
            ("Rating: coal feed kg/s; urea Mt/a", f"{COAL_REPO:.1f}; {ia['urea_mtpa']:.2f}", f"{COAL_KG_S:.1f}; {ib['urea_mtpa']:.2f}", "D scaled to 1.10 Mt/a (A choice)", "all flows x " + f3(COAL_KG_S / COAL_REPO) + "; closure same"),
            ("Coal per t urea, t/t", f2(ia["coal_per_urea"]), f2(ib["coal_per_urea"]), "S Talcher 0.90 feed, 1.74 incl fuel coal", "gap +68 % vs 0.90 left: coal and pet coke, not closed"),
            ("WGS K at 1673 K", f3(wgs_K_moe(1673.15)), f3(wgs_K_thermo(1673.15)), "S thermo/CoolProp fit (script), K 0.3068", f"syngas CO {ia['co_syn']/A.syn_mol*100:.1f} to {ib['co_syn']/B.syn_mol*100:.1f} mol %"),
            ("WGS K at 643 K / 503 K", f"{wgs_K_moe(643.15):.1f} / {wgs_K_moe(503.15):.1f}", f"{wgs_K_thermo(643.15):.1f} / {wgs_K_thermo(503.15):.1f}", "S thermo K 16.77 / 128.6", f"conversion HT {A.ht_conv*100:.1f} to {B.ht_conv*100:.1f} %, LT {A.lt_conv*100:.1f} to {B.lt_conv*100:.1f} %"),
            ("H2O in gas to AGR, mol %", f1(ia["treated_h2o_pct"]), f1(ib["treated_h2o_pct"]), "D V-203 at 40 C, Psat CoolProp 7.385 kPa", f"S28 + S29 condensate {f1((M[28]+M[29])*3.6)} t/h out"),
            ("Methanation H2 use, % of H2", "0 (not deducted)", f1(ib["meth_pct"]), "D 3 CO + 4 CO2; complete conversion (A)", "H2 to loop and NH3 fall by this share"),
            ("Purge recovery; make-up Nm3/t NH3", f"0; {ia['makeup_nm3_per_t_nh3']:,.0f}", f"0.90 (A); {ib['makeup_nm3_per_t_nh3']:,.0f}", f"S Talcher 2651; A range 0.85-0.95 gives {makeup_for_r(0.85):,.0f}-{makeup_for_r(0.95):,.0f}", "r is assumed, not calibrated to Talcher"),
            ("ASU power, kWh/t O2", "733.8", f"{ASU_KWH_PER_T_O2:.0f} ({ASU_RANGE[0]:.0f}-{ASU_RANGE[1]:.0f})", "S TDA DOE-FE-0026142 p.12; single source", f"{REPO_RUN['asu_o2_power_kW']/1000:.1f} MW at 145 kg/s to {ASU_MW:.1f} MW here"),
            ("Reaction heats, kJ/mol", "41.2 shift; 46.1 NH3", f"{DH_WGS_HT} / {DH_WGS_LT} shift; {DH_NH3_700K} NH3", "S thermo Cp integrals (643/503/700 K)", f"R-201 {Q_HT:.0f} MW, R-202 {Q_LT:.0f} MW, R-401 {Q_NH3:.0f} MW"),
            ("K-401 power", "not computed", f"{K401_MW:.1f} MW", "S CoolProp HEOS 7.456 kJ/mol", "electric duty added; 40 to 200 bar, eta 0.75 (A)"),
            ("K-601 power", "not computed", f"{K601_MW:.1f} MW", "S UBA p.24: 126 kWh/t CO2 (D)", "multi-stage figure, not single isentropic"),
            ("Steam; cooling water; other power per t urea", "not computed", f"{UBA_STEAM_T_PER_T} t; {UBA_CW_T_PER_T:.0f} t; {UBA_KWH_EXCL_CO2+UBA_KWH_GRAN:.0f} kWh", "S UBA 2001 p.19-20 (Stamicarbon)", f"steam {STEAM_UREA_T_H:,.0f} t/h, CW {CW_T_H:,.0f} t/h (A: Snam 0.85 t)"),
            ("Mass closure error", f"{ERR_MASS_A:+.3f} %", f"{ERR_MASS:+.3f} %", "D asserted in code", "C, O, N, S exact; H +2 x H2S repo quirk (F1)"),
            ("Relief devices drawn", "4 PSV", "14 PSV + VB-501", "A; R-pointers sheets 5-7", "7 unprotected items now protected or reasoned")]


def sheet2():
    s = SheetB(2, "Coal-to-urea complex: heat and material balance", "Sheet 2: HMB, closure, rating, Rev A to Rev B", code="VS-UREA",
               project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)", basis="repo example + Rev B HMB corrections, 11 Nov 2026")
    frame(s, 7)
    ids = sorted(S)
    y = hmb_table(s, 20, 82, ids, hmb_rows(), first_w=185, col_w=45.3, rh=15.6, size=9,
                  title="HEAT AND MATERIAL BALANCE   steady state, Rev B, urea 1.10 Mt/a, full recycle   (stream numbers = diamonds on sheet 1)")
    y0 = y + 8
    yy = section(s, 20, y0, 540, "STREAM KEY")
    nrow = 15
    R(s, 20, yy, 540, nrow * 12.2 + 8, "#fff", "#889", 1)
    for n in ids:
        col, row = (n - 1) // nrow, (n - 1) % nrow
        lab(s, 26 + col * 268, yy + 12 + row * 12.2, f"S{n} {STREAM_KEY[n]}", 8.8)
    yk = yy + nrow * 12.2 + 14
    # closure (middle)
    cx = 575
    yc = section(s, cx, y0, 545, "CLOSURE (asserted in code)")
    R(s, cx, yc, 545, 104, "#fff", "#889", 1)
    lab(s, cx + 8, yc + 14, f"in {M_IN*3.6:,.1f} t/h, out {M_OUT*3.6:,.1f} t/h, error {ERR_MASS:+.3f} %   (in S1+3+6+8+25; out S5+11+13+16+20+22+23+26+28+29)", 9.5, 700, fill=GREEN)
    lab(s, cx + 8, yc + 28, "Elements, error out vs in:  C 0.0000 %,  O 0.0000 %,  N 0.0000 %,  S 0.0000 %", 9, 400)
    lab(s, cx + 8, yc + 41, f"H {ELERR['H']:+.2f} % = +2 x n(H2S) of the repo gasifier ({H_EXCESS:,.1f} mol/s H, repo finding F1, not changed).", 9, 400, fill=AMBER)
    lab(s, cx + 8, yc + 54, "S24 and S30 are internal recycles in Rev B (S24 left the boundary in Rev A).", 9, 400)
    lab(s, cx + 8, yc + 67, f"Rev A closure (repo, S24 out): {ERR_MASS_A:+.3f} %.  Linearity in coal feed asserted (2 x coal gives 2 x urea).", 9, 400)
    lab(s, cx + 8, yc + 80, f"Loop N and H out = make-up (asserted).  Units below each close within 0.1 %.", 9, 400, fill=GREY)
    lab(s, cx + 8, yc + 93, f"Cold-gas efficiency {CGE_B*100:.1f} % (Rev A {CGE_A*100:.1f} %), HHV of CO and H2 from thermo (frozen).", 9, 400, fill=GREY)
    rows = [("Unit balance", "in t/h", "out t/h", "err %")] + [(n, f1(a), f1(b_), f"{e:+.3f}") for n, a, b_, e in STAGE_ROWS]
    ys = table(s, cx, yc + 112, (300, 80, 80, 70), rows, 14, 9)
    # utilities per t urea
    yu = section(s, 20, yk - 4, 540, "STEAM, WATER, POWER PER t UREA (D from S1-S30; S = UBA 2001)")
    ut = [("Item", "per t urea", "per hour", "Source"),
          ("Gasifier + shift steam S3+S6+S8", f2(ib := IB["steam_gasifier_per_urea"]), f"{(M[3]+M[6]+M[8])*3.6:,.0f} t/h", "D"),
          ("Reaction water S23", f2(IB["reaction_water_per_urea"]), f"{M[23]*3.6:,.1f} t/h", "D; UBA 0.3 stoich"),
          ("Shift + methanator condensate S28+S29", f2(IB["cond_per_urea"]), f"{(M[28]+M[29])*3.6:,.0f} t/h", "D (A: no dissolved gas)"),
          ("Urea-train steam", f"{UBA_STEAM_T_PER_T} ({UBA_STEAM_RANGE[0]}-{UBA_STEAM_RANGE[1]})", f"{STEAM_UREA_T_H:,.0f} t/h", "S UBA p.19, 24, 18"),
          ("Cooling water", f"{UBA_CW_T_PER_T:.0f}", f"{CW_T_H:,.0f} t/h", "S UBA p.20"),
          ("Process water to treatment, m3", f"{UBA_PROCESS_WATER_M3[0]}-{UBA_PROCESS_WATER_M3[1]}", f"{UBA_PROCESS_WATER_M3[0]*UREA_T_H:,.0f}-{UBA_PROCESS_WATER_M3[1]*UREA_T_H:,.0f} m3/h", "S UBA p.19, 25"),
          ("Power excl. CO2 comp + granulation", f"{UBA_KWH_EXCL_CO2+UBA_KWH_GRAN:.0f} kWh", f"{ELEC_OTHER_MW:.1f} MW", "S UBA p.20")]
    table(s, 20, yu, (205, 85, 95, 155), ut, 14, 8.6)
    # right column: rating box, duties, assumptions
    rx = 1135
    yr = section(s, rx, y0, 445, "RATING: WHAT THE REPO TRAIN IS, AND THE CHOICE")
    txt = [f"Repo example, 145 kg/s coal, full recycle: NH3 {OPT1.nh3*17.031/1000*86.4:,.0f} t/d, urea {OPT1_UREA_MTPA:.2f} Mt/a (Rev A said 1.10 Mt/a only because the urea train was single pass: {ia_u:.2f} Mt/a)." if (ia_u := IA['urea_mtpa']) else "",
           f"Option 1 keep the NH3 train: {OPT1_UREA_MTPA:.2f} Mt/a, {OPT1_UREA_MTPA/1.27:.1f} x Talcher 1.27 Mt/a (3,850 t/d, TEIA). Option 2 (chosen) size to 1.10 Mt/a: coal {COAL_KG_S:.1f} kg/s ({COAL_KG_S*3.6:,.0f} t/h), NH3 {NH3_TPD:,.0f} t/d, one 1.10 Mt/a train, equipment sizes in the Talcher class.",
           "Reason: the title and owner basis are 1.10 Mt/a and all quantities scale linearly, so only the plant rating changes; ratios per tonne are unchanged by the choice."]
    yy = yr + 14
    for t in txt: yy = WRAP(s, rx + 6, yy, t, 78, 9.5, 11.5) + 4
    yd = section(s, rx, yy + 2, 445, "DUTIES AND POWER (Rev B rating)")
    drows = [("Item", "Value", "Tag / source"),
             ("Coal heat input, HHV", f"{Q_COAL:,.0f} MW", f"S Dulong {HHV_COAL:.2f} MJ/kg"),
             ("Syngas HHV (CO+H2)", f"{Q_SYN:,.0f} MW", f"D CGE {CGE_B*100:.1f} %"),
             ("R-201 shift heat", f"{Q_HT:,.0f} MW", f"D xi x {DH_WGS_HT} kJ/mol (S thermo)"),
             ("R-202 shift heat", f"{Q_LT:,.0f} MW", f"D xi x {DH_WGS_LT} kJ/mol (S thermo)"),
             ("R-401 synthesis heat", f"{Q_NH3:,.0f} MW", f"D x {DH_NH3_700K} kJ/mol (S, ideal gas)"),
             ("ASU-101 power", f"{ASU_MW:,.1f} MW", f"S 275 kWh/t O2; {ASU_MW_LO:.0f}-{ASU_MW_HI:.0f} MW"),
             ("K-401 power", f"{K401_MW:,.1f} MW", "S CoolProp, eta 0.75 (A)"),
             ("K-601 power", f"{K601_MW:,.1f} MW", "S UBA 126 kWh/t CO2"),
             ("Other urea power", f"{ELEC_OTHER_MW:,.1f} MW", "S UBA 43+23 kWh/t"),
             ("E-101/102/103/401/602, C-301/302", "not computed", "no property model here")]
    yy = table(s, rx, yd, (170, 85, 190), drows, 14.5, 9)
    ya = section(s, rx, yy + 6, 445, "ASSUMED (A), to be confirmed by licensor or vendor")
    arows = ["A1 Pressures 45 bar gasifier to AGR, steam and O2 50 bar; A2 coal 25 C, slag 80 C; A3 residual and N2 at 40 bar.",
             "A4 NH3 storage refrigerated atmospheric, -33 C, 1.1 bar (CoolProp Psat 1.029 bar).",
             "A5 Purge-gas recovery 90 % (range 0.85-0.95); methanation converts all CO and CO2; knock-outs ideal at 40 C, no gas in condensate.",
             "A6 Carbamate recycle complete (no NH3 loss; Talcher NH3 per t urea is 0.8 % above stoich, consistent with small losses).",
             "A7 All tags, lines, relief and safeguard items outside the repo core."]
    yy = ya + 13
    for t in arows: yy = WRAP(s, rx + 6, yy, t, 78, 9, 10.8) + 3
    # Rev A to Rev B box
    yb = section(s, 20, 786, 1100, "REV A TO REV B CHANGES   (item | Rev A | Rev B | source | effect on closure / duties; Rev A recomputed with the flags off)")
    mltable(s, 20, yb, (200, 125, 130, 300, 345), changes_rows(), 8.3, 9.6, 14, pad=3)
    return s


# =====================================================================================================================
# 4. SHEETS 3 AND 4: SCENARIOS (drawn on the dimmed P&ID)
# =====================================================================================================================
def mltable(s, x, y, colw, rows, size=9.5, lh=11.5, head_h=17, pad=8):
    """table with wrapped multi-line cells; returns bottom y"""
    tw = sum(colw)
    R(s, x, y, tw, head_h, "#e8eaf0", "none")
    cx = x
    for j, c in enumerate(rows[0]): T(s, cx + 4, y + 12, c, size, 700); cx += colw[j]
    yy = y + head_h
    for i, r in enumerate(rows[1:]):
        wrapped = [textwrap.wrap(c, width=max(8, int((colw[j] - 8) / (size * 0.52)))) for j, c in enumerate(r)]
        h = max(len(w) for w in wrapped) * lh + pad
        if i % 2 == 1: R(s, x, yy, tw, h, "#f6f7fa", "none")
        cx = x
        for j, w in enumerate(wrapped):
            for k, t in enumerate(w): T(s, cx + 4, yy + 12 + k * lh, t, size, 700 if j == 0 else 400)
            cx += colw[j]
        yy += h
        PL(s, [(x, yy), (x + tw, yy)], 0.6, "#bbb")
    R(s, x, y, tw, yy - y, "none", "#9aa", 1)
    return yy


def cloud(s, cx, cy, rx, ry, color="#8e24aa", op=0.14, dash="7 4"):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" fill-opacity="{op}" stroke="{color}" stroke-width="1.6" stroke-dasharray="{dash}"/>')


def esd_box(s, x, y, w, tag, line2):
    R(s, x, y, w, 36, "#fff3e0", RED, 1.8)
    lab(s, x + w / 2, y + 15, tag, 10.5, 700, "middle", RED); lab(s, x + w / 2, y + 28, line2, 9, 400, "middle", RED)


def red(s, pts): PL(s, pts, 1.5, RED, "6 4", "ahr")
def blu(s, pts): PL(s, pts, 1.2, BLUE, "5 4", "ahb")


def det(s, x, y, tag, note="(A)", tx=0, ty=24):
    bubble(s, x, y, "AT", tag, True)
    lab(s, x + tx, y + ty, note, 9, 400, "middle")


def psv101(s, label=True):
    PL(s, [(320, 215), (350, 215)], 2.6); psv_dn(s, 350, 232)
    PL(s, [(368, 232), (410, 232), (410, 294), (1060, 294)], 2.2, GREY, "7 4")
    if label: lab(s, 416, 258, "PSV-101 (A)", 9.5, 700)
    lab(s, 740, 289, "flare header FL-1 (A)", 9.5, 400, "middle", GREY)


def dim_plant(s):
    s.add('<g opacity="0.42">'); plant(s); s.add('</g>')


def card(s, x, y, w, title, lines, color):
    R(s, x, y, w, 20, color, "none"); lab(s, x + 8, y + 14, title, 11.5, 700, fill="#fff")
    yy = y + 36
    for t in lines: yy = WRAP(s, x + 8, yy, t, 78, 10, 12.5, bullet=True) + 3
    R(s, x, y, w, yy - y + 2, "none", "#889", 1)
    return yy + 8


def overlay_legend(s, x, y):
    star(s, x + 12, y, 11); lab(s, x + 30, y + 4, "release point", 9.5)
    cloud(s, x + 125, y, 22, 10, "#8e24aa"); lab(s, x + 152, y + 4, "cloud (no extent drawn)", 9.5)
    flame(s, x + 12, y + 32, 20, 22, 10); lab(s, x + 30, y + 28, "fire", 9.5)
    s.add(f'<rect x="{x+98}" y="{y+16}" width="32" height="14" fill="none" stroke="{AMBER}" stroke-width="2" stroke-dasharray="6 3"/>'); lab(s, x + 138, y + 28, "bund / dyke (A)", 9.5)
    PL(s, [(x, y + 52), (x + 28, y + 52)], 1.5, RED, "6 4", "ahr"); lab(s, x + 34, y + 56, "ESD output (A)", 9.5)
    PL(s, [(x + 130, y + 52), (x + 158, y + 52)], 1.2, BLUE, "5 4", "ahb"); lab(s, x + 164, y + 56, "detector signal (A)", 9.5)
    valve(s, x + 12, y + 78, 0, "gate", act=True, color=RED); lab(s, x + 30, y + 82, "ESD valve, closes on ESD logic (A)", 9.5)


def flows_table(s, y, items):
    """HMB flows at the release points (D, from sheet 2)"""
    lab(s, 1145, y + 6, "Flows at the release points (HMB, sheet 2)", 11, 700)
    rows = [("Scn", "Stream", "t/h", "kmol/h")] + [(sc, nm, f1(tph(i)), f1(sum(S[i].values()) * 3.6)) for i, sc, nm in items]
    return table(s, 1145, y + 12, (45, 235, 70, 75), rows, 15.5, 10) + 8


def esd_valve(s, name, note="ESD", lx=0, ly=-14, anchor="middle"):
    x, y, rot = XVP[name]
    xv(s, x, y, name, rot, lx, ly, anchor, note)


def sheet3():
    s = SheetB(3, "Coal-to-urea complex: scenarios A and B", "Sheet 3: NH3 release; syngas fire", code="VS-UREA",
              project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)",
              basis="Hazard identification only, qualitative")
    frame(s, 7)
    dim_plant(s)
    # ---------- scenario A: ammonia (storage and loop liquid line)
    cloud(s, 190, 690, 170, 70)
    s.add(f'<rect x="38" y="640" width="150" height="116" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="8 4"/>')
    tank(s, 110, 745, 120, 95, "T-501 NH3 storage", None, roof="dome", level=0.7)
    star(s, 160, 706, 16); lab(s, 128, 676, "A1", 12, 700, "middle", RED)
    star(s, 348, 575, 16); lab(s, 366, 598, "A2", 12, 700, fill=RED)
    esd_valve(s, "XV-501", "ESD-2", 0, -28)
    esd_valve(s, "XV-502", "ESD-2", -15, 2, "end")
    bubble(s, 212, 672, "AT", "501", True)
    bubble(s, 390, 640, "AT", "401", True)
    bubble(s, 80, 612, "LSHH", "501", True)
    esd_box(s, 262, 668, 140, "ESD-2 NH3 (A)", "T-501 / V-401 area")
    blu(s, [(227, 672), (262, 680)]); blu(s, [(390, 655), (390, 668)])
    red(s, [(262, 690), (188, 690), (188, 706)])
    red(s, [(330, 668), (330, 576), (312, 576)])
    lab(s, 262, 722, "P-501 trip on ESD-2 (A)", 9.5, 700, "start", RED)
    # ---------- scenario B: syngas
    cloud(s, 400, 200, 160, 90, "#e65100", 0.12)
    psv101(s, False)
    esd_valve(s, "XV-101", "ESD-1", 0, -38); esd_valve(s, "XV-102", "ESD-1", 0, -46); esd_valve(s, "XV-103", "ESD-1", -14, 2, "end")
    valve(s, 495, 294, 0, "gate", act=True, color=RED); lab(s, 495, 264, "BDV-101", 9.5, 700, "middle", RED)
    star(s, 448, 200, 15); lab(s, 474, 196, "B1", 12, 700, fill=RED)
    flame(s, 448, 204, 150, 40, 22)
    bubble(s, 322, 256, "AT", "102", True)
    bubble(s, 590, 236, "AT", "201", True)
    bubble(s, 440, 276, "BE", "101", True)
    esd_box(s, 830, 100, 200, "ESD-1 SYNGAS (A)", "closes XV-101,102,103; opens BDV-101")
    lab(s, 836, 150, "detectors AT-102, AT-201, BE-101 vote", 9, 400, "start", BLUE)
    lab(s, 836, 161, "into ESD-1 (A)", 9, 400, "start", BLUE)
    # side card
    panel_box(s)
    y = section(s, 1135, 84, 445, "SCENARIO CARDS")
    y = card(s, 1145, y + 6, 425, "A  Ammonia release (toxic)", [
        f"Liquid NH3 passing V-401 to T-501: {M[17]*3.6:,.0f} t/h (S, repo). Storage size and type are not in the repo.",
        "A1: tank outlet / P-501 suction. A2: V-401 liquid line, loop at 200 bar (S).",
        "Cloud and bund drawn without extent: no distance is computed."], "#6a1b9a")
    y = card(s, 1145, y + 6, 425, "B  Syngas release and fire (CO, H2, H2S)", [
        f"S4 composition (repo): CO {S[4]['CO']/B.syn_mol*100:.1f} mol %, H2 {S[4]['H2']/B.syn_mol*100:.1f} %, H2O {S[4]['H2O']/B.syn_mol*100:.1f} %, CO2 {S[4]['CO2']/B.syn_mol*100:.1f} %, H2S {S[4]['H2S']/B.syn_mol*100:.2f} %; flow {B.syn_mol*3.6:,.0f} kmol/h (S4).",
        "B1: flange or pipe failure between E-101 and R-201. Hot, toxic and flammable: jet fire, flash fire or confined explosion.",
        "ESD-1 stops O2, coal and steam to R-101 and opens BDV-101 to the flare."], "#c62828")
    y = flows_table(s, y, [(17, "A", "S17 liquid NH3 to T-501"), (16, "A", "S16 loop purge gas"), (4, "B", "S4 raw syngas, R-101 outlet"), (7, "B", "S7 HT shift outlet")])
    lab(s, 1145, y + 8, "Overlay key", 11, 700)
    overlay_legend(s, 1160, y + 28)
    WRAP(s, 1145, y + 140, "Safeguards are A unless marked R. R items (named free sources) are on sheets 5-7. Hazard text is qualitative; no number on this sheet is a consequence result.", 78, 10, 12.5, GREY)
    yt = section(s, 20, 784, 1100, "SCENARIO TABLE   (qualitative; open data needs are listed rather than assumed)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown (A; R on sheets 5-7)", "Open data needs"),
            ("A  Ammonia (toxic) release from storage or synthesis loop",
             "Seal, flange or nozzle failure at T-501 outlet / P-501 suction (A1), or leak on the V-401 liquid line (A2); overfill via LV-401 failure.",
             "Toxic NH3 cloud at ground level. Pressurised liquid flashes and chills, aerosol can travel as a dense cloud. Corrosive to eyes and skin. Narrow flammable range, so fire is secondary. Not quantified.",
             "AT-501 and AT-401 NH3 detectors; XV-501 remote isolation at the tank outlet; XV-502 on V-401 liquid; P-501 trip; LSHH-501 high-level cutoff; bund, sump and water spray; PSV-501 vent to scrubber (sheet 1).",
             "Not quantified: needs T-501 and loop inventory, storage type, pressure and temperature, hole size, release height, wind data, toxic end-point criteria, receptor distances."),
            ("B  Syngas (CO / H2 / H2S) release and fire",
             "Flange or gasket leak, or pipe failure, on raw syngas S4 / S7 between R-101 and the shift section (B1); gasifier trip leaving hot gas in line.",
             "Toxic CO and H2S. H2 and CO flammable: jet fire, flash fire, or explosion if confined. Hot lines (1400 C at the gasifier outlet, 350 C at HT shift) make ignition likely. Not quantified.",
             "AT-102, AT-201 CO/H2 detectors; BE-101 flame detector; XV-101 (O2), XV-102 (coal), XV-103 (steam) trip on ESD-1; BDV-101 blowdown to FL-1; PSV-101 to FL-1; fire protection on supports.",
             "Not quantified: needs R-101 operating pressure, inventory between isolation valves, hole sizes, congestion and confinement, ignition sources, H2S limits for the site.")]
    mltable(s, 20, yt, (120, 190, 280, 290, 220), rows, 9.5, 11.3)
    return s


def sheet4():
    s = SheetB(4, "Coal-to-urea complex: scenarios C and D", "Sheet 4: O2 / steam fire; urea failure", code="VS-UREA",
              project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)",
              basis="Hazard identification only; one repo-fit sensitivity (D)")
    frame(s, 7)
    dim_plant(s)
    # ---------- scenario C: oxygen / steam
    cloud(s, 215, 205, 98, 62, "#e65100", 0.12)
    cloud(s, 205, 255, 55, 22, "#1565c0", 0.16, "3 3")
    ctrlvalve(s, 150, 205); bubble(s, 150, 158, "FIC", "102", True); PL(s, [(150, 173), (150, 181)], 1.2, BLUE, "5 4")
    esd_valve(s, "XV-101", "ESD-3", 0, -38); esd_valve(s, "XV-102", "ESD-3", 0, -46); esd_valve(s, "XV-103", "ESD-3", -14, 2, "end")
    star(s, 182, 205, 13); lab(s, 176, 226, "C1", 12, 700, "middle", RED)
    flame(s, 182, 200, 20, 30, 16)
    star(s, 205, 232, 12); lab(s, 214, 252, "C2 steam leak", 10.5, 700, "start", RED)
    bubble(s, 240, 282, "BE", "101", True)
    esd_box(s, 830, 100, 200, "ESD-3 O2 / STEAM (A)", "closes XV-101,102,103")
    lab(s, 836, 150, "FIC-102 flow trip and BE-101 vote into ESD-3 (A)", 9, 400, "start", BLUE)
    # ---------- scenario D: urea
    cloud(s, 870, 650, 170, 90)
    star(s, 920, 650, 15); lab(s, 942, 646, "D1", 12, 700, fill=RED)
    star(s, 790, 636, 14); lab(s, 790, 618, "D2", 12, 700, "middle", RED)
    esd_valve(s, "XV-602", "ESD-4", 0, -38); x_, y_, r_ = XVP["XV-603"]; xv(s, x_, y_, "XV-603", r_, 30, 4, "start", "ESD-4")
    PL(s, [(790, 582), (790, 578), (762, 578)], 2.6); psv(s, 762, 562); PL(s, [(780, 562), (818, 562)], 2.2)
    lab(s, 822, 558, "PSV-601", 9.5, 700); lab(s, 822, 569, "to scrubber (A)", 9.5)
    bubble(s, 960, 712, "UIC", "601", True); lab(s, 980, 710, "anti-surge / trip (A)", 9.5)
    PL(s, [(955, 697), (935, 667)], 1.2, BLUE, "5 4")
    bubble(s, 733, 690, "AT", "601", True)
    bubble(s, 1000, 685, "FALL", "602", True); PL(s, [(1000, 670), (1000, 650)], 1.2, BLUE, "5 4")
    esd_box(s, 950, 730, 150, "ESD-4 UREA (A)", "K-601 trip / low CO2")
    blu(s, [(1000, 700), (1000, 730)])
    red(s, [(950, 742), (870, 742), (870, 662)]); red(s, [(950, 756), (806, 756), (806, 744)])
    lab(s, 940, 765, "", 9)
    panel_box(s)
    y = section(s, 1135, 84, 445, "SCENARIO CARDS")
    y = card(s, 1145, y + 6, 425, "C  Oxygen or HP steam fire / release", [
        f"O2 to R-101 {M[2]:.2f} kg/s (S: ratio 0.55 x coal); gasifier steam {M[3]:.1f} kg/s (S: 0.10 x coal). Supply pressures are A (50 bar).",
        "C1: fire on the O2 line at the gasifier inlet. C2: HP steam line leak at the R-101 steam nozzle.",
        "ESD-3 closes XV-101 and XV-103; XV-102 stops coal."], "#e65100")
    y = card(s, 1145, y + 6, 425, "D  Urea reactor / CO2 compressor failure", [
        "D1: K-601 trips or fails, CO2 stops while NH3 (S18) still arrives. D2: leak or overpressure at R-601 (180 C, 150 bar, S).",
        f"Repo fit (illustrative): CO2 loss of 20 % moves N/C {TARGET_NC:.1f} to {NC_20:.2f}, per-pass conversion {REPO_RUN['urea_conv']*100:.1f} to {CONV_20*100:.1f} %, urea {UREA_20_PCT:+.1f} % (D, production only).",
        "Surplus CO2 vent S20 stays available as a sink for CO2 if K-601 restarts."], "#00695c")
    y = flows_table(s, y, [(2, "C", "S2 oxygen to R-101"), (3, "C", "S3 HP steam to R-101"), (19, "D", "S19 CO2 to R-601"), (18, "D", "S18 NH3 to R-601")])
    lab(s, 1145, y + 8, "Overlay key", 11, 700)
    overlay_legend(s, 1160, y + 28)
    WRAP(s, 1145, y + 140, "Safeguards are A unless marked R. R items (named free sources) are on sheets 5-7. Hazard text is qualitative; the only number in the scenarios is the repo-fit sensitivity in D.", 78, 10, 12.5, GREY)
    yt = section(s, 20, 784, 1100, "SCENARIO TABLE   (qualitative; open data needs are listed rather than assumed)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown (A; R on sheets 5-7)", "Open data needs"),
            ("C  HP steam or oxygen fire in the gasifier area",
             "Ignition or failure on the O2 feed to R-101 (C1); rupture of the HP steam feed (C2); loss of O2:coal ratio control during a trip.",
             "Oxygen-enriched fire ignites organic material and metal quickly and can spread to the coal feed and syngas lines. A steam jet scalds, strips insulation and can damage nearby cables and instruments. Not quantified.",
             "XV-101 O2 isolation and XV-103 steam isolation on ESD-3; XV-102 coal stop; FIC-102 with flow trip; O2 line built and cleaned for oxygen service; BE-101 flame / heat detector; O2 and coal lines separated.",
             "Not quantified: needs O2 pressure and velocity limits, material and cleanliness requirements from the licensor and a named standard, steam pressure and temperature, line sizes, layout."),
            ("D  Urea reactor or CO2 compressor failure",
             "K-601 trip, surge or mechanical failure (D1) with NH3 feed continuing; leak, blockage or overpressure at R-601 / C-601 (D2).",
             "NH3-rich hot mixture at 150 bar is toxic and corrosive if released. Without CO2 the NH3 feed can raise pressure; solid carbamate can block lines if the loop cools. Output sensitivity from the repo fit is on the card; safety consequence not quantified.",
             "UIC-601 anti-surge and K-601 trip; FALL-602 low CO2 flow closes XV-603 on the NH3 feed and trips P-501; XV-602 CO2 isolation; PSV-601 to scrubber; AT-601 NH3 detector.",
             "Not quantified: needs R-601 / C-601 inventory, relief cases and rates, carbamate crystallisation margins from the licensor, K-601 data, scrubber capacity.")]
    mltable(s, 20, yt, (120, 190, 280, 290, 220), rows, 9.5, 11.3)
    return s


# =====================================================================================================================
# 5. SAFETY DESIGN BASIS (sheets 5-7)
# =====================================================================================================================
# Relief screening: process_safety.relief.gas_area (API 520-I derived equations; the toolkit says the standard text was not read), blocked-outlet case
# with the full inlet flow (no credit for control valves). M, k (ideal gas, thermo Cp) and Z (Peng-Robinson, thermo) are frozen from
# tests/crosscheck/urea_revb_constants.py relief_cases.json run (11 Nov 2026).  Design pressure = 1.10 x operating (A); set = design; back pressure 200 kPa abs (A).
RELIEF_KZ = {"PSV-101": (21.263, 1.2586, 1.0080), "PSV-201": (20.513, 1.2921, 1.0002), "PSV-202": (20.286, 1.3030, 0.9792),
             "PSV-301": (20.712, 1.3394, 0.9454), "PSV-303": (3.627, 1.3991, 1.0125), "PSV-401": (8.515, 1.4023, 1.0948), "PSV-402": (8.515, 1.3860, 1.0624)}
_agr = dict(S[9]); _agr["H2O"] = S[9]["H2O"] - S[28]["H2O"]
RELIEF_CASE = {"PSV-101": (S[4], 1673.15, 45, "S4"), "PSV-201": (S[7], 623.15, 45, "S7"), "PSV-202": (S[9], 493.15, 45, "S9"),
               "PSV-301": (_agr, 313.15, 45, "S9 less S28"), "PSV-303": (S[12], 313.15, 40, "S12"), "PSV-401": (S[15], 313.15, 200, "S15"),
               "PSV-402": (S[15], 723.15, 200, "S15")}


def relief_sizing():
    out = {}
    try:
        from process_safety.relief import gas_area, relieving_pressure_kpa
    except Exception as e:  # pragma: no cover
        return {t: f"not sized: process_safety not importable ({e})" for t in RELIEF_CASE}
    for tag, (sp, T, Pop, lab_) in RELIEF_CASE.items():
        M_, k, Z = RELIEF_KZ[tag]
        mw = mass(sp) * 1000.0 / sum(sp.values())
        assert abs(mw / M_ - 1) < 0.005, (tag, mw, M_)         # frozen M still matches the balance
        dg = math.ceil(1.10 * (Pop - 1.01325)); p1 = relieving_pressure_kpa(dg * 100.0, "single_non_fire")
        W = mass(sp) * 3600.0
        try:
            r = gas_area(W, T, p1, 200.0, M_, k, Z, set_g_kpa=dg * 100.0)
            out[tag] = dict(dg=dg, W=mass(sp), A=r.required_area_mm2, orifice=r.orifice, n=r.n_valves, regime=r.regime, Z=Z, k=k, stream=lab_, T=T)
        except Exception as e:
            out[tag] = f"toolkit refused: {str(e)[:60]}"
    return out


RS = relief_sizing()


def sized_text(tag):
    r = RS[tag]
    if isinstance(r, str): return r
    return (f"screening, blocked outlet, gas, full {r['stream']} flow {r['W']:.1f} kg/s at {r['T']:.0f} K: A_req {r['A']:,.0f} mm2 = "
            f"{r['n']} x API 526 '{r['orifice']}' (k {r['k']:.2f}, Z {r['Z']:.2f}, {r['regime']}); the full-flow case may instead be credited to a HIPS (A, sheet 6)")


T501_DAYS = 3.0   # A: storage days
T501_T = NH3_TPD * T501_DAYS; T501_M3 = T501_T * 1000.0 / NH3_RHO_MINUS33C
DP = lambda Pop: f"{math.ceil(1.10 * (Pop - 1.01325))} barg (1.10 x op, A)"
RELIEF_ROWS = [
    ("Item", "Service, operating (S/A)", "Design pressure basis (A)", "Relief case(s)", "Device (tag on sheet 1)", "Discharge", "Sizing status"),
    ("ASU-101", "cryogenic air separation, O2 / N2 / LOX", "vendor", "cold-box and LOX vaporiser overpressure, blocked outlets", "vendor PSVs and rupture discs (not drawn)", "safe location (A)", "not sized: vendor package; EIGA/CGA O2 standards: gap, not obtained"),
    ("F-101", "coal lock hoppers, pressurised by N2/CO2", "vendor", "blocked vent, gas blow-through from R-101 side", "PSV on each lock hopper (vendor, not drawn)", "FL-1 via KO (A)", "not sized: needs hopper volumes and pressurising rate"),
    ("R-101", "gasifier 1400 C, 45 bar", DP(45), "blocked outlet, loss of cooling, runaway O2", "PSV-101 (drawn, header FL-1)", "FL-1 flare header", sized_text("PSV-101")),
    ("V-102", "slag lock hopper, 80 C", "= R-101 side (A)", "gas blow-through from R-101, thermal", "PSV-102 (drawn)", "FL-1 (A)", "not sized: needs blow-through leak rate"),
    ("E-101", "syngas cooler, steam raising", "gas = R-101; steam side by licensor", "tube rupture, blocked steam outlet", "gas side by PSV-101 (no block valve); steam-drum PSV by licensor (not drawn)", "FL-1 / steam vent", "not sized: needs steam-drum data"),
    ("R-201", "HT shift 350 C, 45 bar", DP(45), "blocked outlet, loss of steam, CO breakthrough exotherm", "PSV-201 (drawn)", "FL-1", sized_text("PSV-201")),
    ("E-102", "shift interstage cooler", "= R-201", "tube rupture, thermal", "covered by PSV-201 (no block valve R-201 to R-202; confirm in HAZOP)", "FL-1", "reason stated; A"),
    ("R-202", "LT shift 220 C, 45 bar", DP(45), "blocked outlet, loss of cooling", "PSV-202 (drawn)", "FL-1", sized_text("PSV-202")),
    ("E-103", "gas cooler (CW)", "= R-202; CW side by utility", "CW tube rupture into gas side, thermal", "gas side by PSV-202; CW-side relief not drawn", "FL-1 / CW system", "not sized: needs CW design pressure"),
    ("V-203", "condensate knock-out 40 C, 45 bar", "= R-202", "blocked liquid outlet, gas blow-by", "covered by PSV-202 upstream and PSV-301 downstream (no block valves)", "FL-1", "reason stated; A"),
    ("C-301", "AGR absorber 40 C, 45 bar", DP(45), "blocked gas outlet, solvent loss, fire", "PSV-301 (drawn)", "FL-1 (sour gas)", sized_text("PSV-301")),
    ("C-302", "solvent regenerator, 2 bar acid gas", "A: low pressure", "blocked acid-gas outlet, loss of reflux, fire", "PSV-302 (drawn on off-gas line)", "FL-1 / sulphur recovery (A)", "not sized: needs regenerator duty and acid-gas load"),
    ("P-301", "lean solvent pump", "= C-301", "blocked discharge, thermal in isolated line", "thermal relief valve (not drawn)", "closed drain (A)", "not sized: needs solvent data"),
    ("R-301", "methanation 40 bar", DP(40), "blocked outlet, CO / CO2 breakthrough exotherm", "PSV-303 (drawn); runaway guarded by TAHH-201 SIF (sheet 6)", "FL-1", sized_text("PSV-303")),
    ("V-302", "methanator KO drum", "= R-301", "blocked liquid outlet", "covered by PSV-303 and PSV-401 (no block valves to K-401; confirm)", "FL-1", "reason stated; A"),
    ("K-401 / K-402", "make-up compressor 40 to 200 bar; circulator", DP(200), "blocked discharge, check-valve failure", "PSV-401 loop device covers (no block valve between); anti-recycle by vendor", "FL-1", "see PSV-401"),
    ("R-401", "NH3 converter 450 C, 200 bar", DP(200), "blocked outlet, loss of cooling, runaway", "PSV-402 (drawn)", "FL-1", sized_text("PSV-402")),
    ("E-401", "converter effluent cooler / NH3 chiller", "= loop; refrigerant side by refrigeration package", "refrigerant tube rupture, thermal, loss of cooling", "process side by PSV-401; refrigerant side not in repo (not drawn)", "FL-1 / scrubber", "not sized: refrigerant circuit not defined"),
    ("V-401", "NH3 separator, 200 bar loop", DP(200), "blocked outlet, fire, LV-401 failing open (gas blow-by to T-501)", "PSV-401 (drawn); LSLL-401 SIF guards blow-by", "FL-1", sized_text("PSV-401") + "; fire: not sized, needs V-401 dimensions"),
    ("T-501", f"refrigerated NH3, -33 C, 1.1 bar abs; {T501_DAYS:.0f} d = {T501_T:,.0f} t = {T501_M3:,.0f} m3 (D, A days)", "low-pressure tank code: gap (API 620 / 2000 / EN 14620 not obtained)", "fire, refrigeration loss (boil-off), filling, vacuum on pump-out, blow-by", "PSV-501, PSV-502 (dual, 3-way selector, per S7 R) and vacuum breaker VB-501 (drawn)", "NH3 scrubber then flare (S6 R)", "not sized: needs tank geometry and API 2000"),
    ("P-501", "NH3 feed pump", "= R-601 feed", "blocked discharge, thermal expansion of isolated liquid NH3", "thermal relief valve (not drawn)", "back to T-501 / scrubber", "not sized: needs line volumes"),
    ("K-601", "CO2 compressor to 150 bar", DP(150), "blocked discharge (XV-602 closed), surge", "PSV-603 (drawn upstream of XV-602); anti-surge UIC-601", "CO2 vent (safe location)", "not sized: dense-phase CO2, ideal-gas equations invalid (Z outside 0.8-1.1)"),
    ("R-601", "urea reactor 180 C, 150 bar", DP(150), "blocked outlet, loss of CO2 (NH3 continues), thermal, corrosion-driven leak", "PSV-601 (drawn)", "NH3 scrubber (A)", "not sized: two-phase NH3 / CO2 / carbamate, needs licensor data"),
    ("C-601 / E-601", "HP stripper, carbamate condenser (4 bar steam side per UBA)", "= R-601", "blocked vapour outlet, steam-side tube rupture", "PSV-602 (drawn) covers both (no block valve); steam-side relief by licensor", "NH3 scrubber (A)", "not sized: needs stripper data"),
    ("E-602 / G-601", "vacuum evaporator; granulator", "vacuum / atmospheric", "loss of vacuum, dust / NH3 vent", "no PSV: atmospheric or vacuum duty; vents to scrubber (A)", "scrubber", "reason stated; A"),
    ("KO-101 / FL-101", "flare knock-out and flare", "header back pressure A", "sum of coincident loads (fire, power failure) and BDV-101 blowdown", "KO-101, FL-101, BDV-101 (drawn)", "atmosphere", "not sized: needs governing-load summation (API 521 / 537 gap)")]
PRESSURE_ITEMS = ["ASU-101", "F-101", "R-101", "V-102", "E-101", "R-201", "E-102", "R-202", "E-103", "V-203", "C-301", "C-302", "P-301", "R-301", "V-302",
                  "K-401", "K-402", "R-401", "E-401", "V-401", "T-501", "P-501", "K-601", "R-601", "C-601", "E-601", "E-602", "G-601", "KO-101", "FL-101"]
PSV_TAGS = ["PSV-101", "PSV-102", "PSV-201", "PSV-202", "PSV-301", "PSV-302", "PSV-303", "PSV-401", "PSV-402", "PSV-501", "PSV-502", "PSV-601", "PSV-602", "PSV-603", "VB-501"]


def sheet5():
    s = SheetB(5, "Coal-to-urea complex: safety design basis, relief", "Sheet 5: relief schedule", code="VS-UREA",
               project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)", basis="OSHA PSM relief design basis R; sizing screening only")
    frame(s, 7)
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE   every pressure item on sheet 1: device or written reason   (R = required by a named free source, A = assumed here, gap = standard not obtained)")
    yb = mltable(s, 20, y, (78, 200, 138, 215, 300, 130, 499), RELIEF_ROWS, 9.3, 10.8, 15)
    notes = ["Basis: OSHA 29 CFR 1910.119 requires the relief system design basis in process safety information (R, S5). CSB Kuraray report: the discharge location is a design item (R, S11). Fire-case relief per API 521: standard not obtained (gap). Sizing uses process_safety.relief (API 520-I equations re-derived; the toolkit states the standard text was not read).",
             "Blocked-outlet cases take the whole inlet flow with no credit for control valves: the areas are large (single API 526 'R'/'T' orifices at 45 bar): the alternative is to avoid the case with the SIFs of sheet 6, and the flare must still take the load. Design pressure 1.10 x operating, set = design, back pressure 200 kPa abs, Kd 0.975 (all A). Z for 200 bar H2/N2 is 1.06-1.09, inside the 0.8-1.1 range of the equations.",
             "Items marked 'reason stated' have no block valve to a protected neighbour on this conceptual P&ID: that must be confirmed in the HAZOP (S5 PHA). Devices not drawn (vendor packages, steam drums, CW and refrigerant systems) are listed so that no pressure item is silent."]
    yy = yb + 8
    for t in notes: yy = WRAP(s, 22, yy, t, 245, 9, 11) + 3
    return s


# ---- ESD cause-and-effect and SIF list
FE = ["XV-101", "XV-102", "XV-103", "BDV-101", "XV-501", "XV-502", "XV-602", "XV-603", "P-501", "K-601", "K-401/402", "Alarm"]
_CE = [("HS-001 manual push-button (ESD-0)", FE),
      ("AT-101 / AT-102 / AT-201 CO-H2 high-high, 2oo3 (A) with BE-101 (ESD-1)", ["XV-101", "XV-102", "XV-103", "BDV-101", "Alarm"]),
      ("PSHH-101 gasifier high-high pressure (ESD-1)", ["XV-101", "XV-102", "XV-103", "BDV-101", "Alarm"]),
      ("AT-103 O2 high, FIC-102 deviation (ESD-3)", ["XV-101", "XV-102", "XV-103", "Alarm"]),
      ("TAHH-201 HT shift outlet high-high T", ["XV-101", "XV-102", "Alarm"]),
      ("AT-301 H2S / CO high-high, 2oo2 (A)", ["XV-101", "XV-102", "Alarm"]),
      ("AT-401 NH3 loop 2oo2 (A) (ESD-2)", ["XV-502", "K-401/402", "Alarm"]),
      ("PSHH-401 loop high-high pressure", ["K-401/402", "Alarm"]),
      ("LSLL-401 V-401 low-low level (gas blow-by)", ["XV-502", "Alarm"]),
      ("AT-501 / AT-502 NH3 tank 2oo2 (A) (ESD-2)", ["XV-501", "XV-502", "P-501", "Alarm"]),
      ("LSHH-501 T-501 high-high level", ["XV-502", "Alarm"]),
      ("AT-601 NH3 urea area 2oo2 (A) (ESD-4)", ["XV-602", "XV-603", "P-501", "K-601", "Alarm"]),
      ("PSHH-601 R-601 high-high pressure (ESD-4)", ["XV-602", "XV-603", "P-501", "K-601", "Alarm"]),
      ("FALL-602 low CO2 flow (ESD-4)", ["XV-603", "P-501", "Alarm"]),
      ("Loss of instrument air / power (fail-safe)", FE)]
CE = [(c, "".join("X" if f in els else " " for f in FE)) for c, els in _CE]
SIF = [("SIF", "Initiator", "Final elements", "Demand source", "IPLs credited (A)", "SIL target (A)", "Free source for the principle"),
       ("1", "PSHH-101 gasifier high-high pressure", "XV-101/102/103 close, BDV-101 opens", "PIC-101 / outlet blockage", "PIC-101 alarm, operator, PSV-101", "SIL 2 (A)", "separation of SIS from control, HSE HSG238 (R); IEC 61511: gap"),
       ("2", "AT-103 O2 / FIC-102 ratio deviation", "XV-101 (O2), XV-102, XV-103", "loss of O2:coal ratio control", "BPCS alarm, operator, O2-service build", "SIL 2 (A)", "HSG238 (R); IEC 61511: gap"),
       ("3", "AT-101/102/201 2oo3 + BE-101 (ESD-1)", "XV-101/102/103, BDV-101", "flange / gasket leak, syngas", "open-air structure, operator, detectors alarm", "SIL 1 (A)", "EIGA 15/21 leak detection (R); IFC EHS (R)"),
       ("4", "TAHH-201 shift outlet T", "XV-101, XV-102", "CO breakthrough / steam loss", "FIC-201 alarm, operator", "SIL 1 (A)", "HSG238 (R)"),
       ("5", "PSHH-401 loop pressure", "K-401 / K-402 trip", "PIC-401 purge failure", "PSV-401, operator", "SIL 2 (A)", "OSHA 1910.119 shutdown conditions (R)"),
       ("6", "LSLL-401 V-401 low-low level", "XV-502, LV-401 shut", "LV-401 fails open, 200 bar gas to T-501", "LIC-401 alarm; PSV-501/502 cannot take the flow (screening)", "SIL 2 (A)", "CSB BP-Husky: credited SIS failed (R, S10); IEC 61511: gap"),
       ("7", "LSHH-501 T-501 high-high level", "XV-502 close, LV-401 shut, P-501 off", "overfill by LIC fault", "LIT-501 alarm, operator", "SIL 1 (A)", "HSE HSG176 para 137, independent HH trip (R)"),
       ("8", "AT-401 / AT-501 / AT-502 NH3 2oo2 (ESD-2)", "XV-501, XV-502, P-501 stop", "seal / flange / nozzle leak", "bund, water spray (A), operator", "SIL 1 (A)", "EPA Region 7 (two detectors, R); IFC EHS (R)"),
       ("9", "PSHH-601 R-601 high-high pressure (ESD-4)", "XV-602, XV-603, P-501, K-601", "loss of CO2, blockage, carbamate", "PIC-601, PSV-601", "SIL 2 (A)", "HSG238 (R); IEC 61511: gap"),
       ("10", "FALL-602 low CO2 flow (ESD-4)", "XV-603 close, P-501 stop", "K-601 trip, FFIC-601 failure", "FFIC-601 alarm, UIC-601", "SIL 1 (A)", "HSG238 (R)")]


def sheet6():
    s = SheetB(6, "Coal-to-urea complex: safety design basis, ESD and SIF", "Sheet 6: ESD cause-and-effect, SIF list", code="VS-UREA",
               project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)", basis="assumed SIL targets; no SIL verification claimed")
    frame(s, 7)
    y = section(s, 20, 84, 1560, "ESD CAUSE-AND-EFFECT MATRIX   X = final element acts (A); every tag exists on sheet 1; valves fail closed, BDV-101 fails open (A)")
    lw, cw = 560, 76
    R(s, 20, y, lw + cw * len(FE), 20, "#e8eaf0", "none"); T(s, 24, y + 14, "Initiator (cause)", 9.5, 700)
    for j, f in enumerate(FE): T(s, 20 + lw + cw * j + cw / 2, y + 14, f, 9, 700, "middle")
    for i, (cause, marks) in enumerate(CE):
        yy = y + 20 + i * 17
        if i % 2: R(s, 20, yy, lw + cw * len(FE), 17, "#f6f7fa", "none")
        T(s, 24, yy + 12, cause, 9)
        for j in range(len(FE)):
            if j < len(marks) and marks[j] == "X": T(s, 20 + lw + cw * j + cw / 2, yy + 12, "X", 10, 700, "middle", RED)
    yb = y + 20 + len(CE) * 17
    R(s, 20, y, lw + cw * len(FE), yb - y, "none", "#9aa", 1)
    ys = section(s, 20, yb + 14, 1560, "SAFETY INSTRUMENTED FUNCTIONS   (SIL targets are ASSUMED (A); no LOPA, no PFDavg, no SIL verification claimed)")
    yy = mltable(s, 20, ys, (36, 285, 235, 220, 280, 85, 419), SIF, 9.3, 10.8, 15)
    WRAP(s, 22, yy + 12, "IEC 61511 / ISA 84 and CCPS LOPA texts were not obtained (gap): the SIL labels are placeholders to be replaced after a hazard and risk study. R basis available free: separation of protection from control and the need to derive integrity from the risk analysis (HSE HSG238); independent high-high level trips (HSG176 para 137); OSHA 29 CFR 1910.119 requires emergency shutdown procedures and mechanical integrity of ESD systems; CSB BP-Husky: a SIS credited in the PHA did not prevent the release.", 250, 9, 11, GREY)
    return s


HAZ = [("Node / deviation", "Cause", "Consequence (qualitative)", "Safeguards on sheets 1-6", "Action (A)"),
       ("N1 ASU to R-101 O2 line: high O2 flow or O2 leak", "FIC-102 failure, valve leak, contaminated line", "oxygen-enriched fire at the gasifier inlet; metal and organic materials ignite", "FIC-102, AT-103, BE-101, XV-101, SIF 2, O2-service cleanliness", "confirm O2 line material / velocity rules from licensor; EIGA standards: gap"),
       ("N2 R-101 gasifier / V-102: high pressure or temperature, loss of coal or steam", "outlet blockage, coal feed loss, slag-tap plugging", "relief to flare; hot toxic CO/H2 release; slag line blow-through", "PIC-101, PSHH-101, PSV-101, PSV-102, BDV-101, XV-102, SIF 1", "HAZOP the slag lock-hopper cycle; size BDV and flare load"),
       ("N3 E-101 / R-201 / R-202: high temperature, CO breakthrough, steam loss, tube leak", "gasifier upset, FIC-201 failure, cooler tube leak", "hot spot in catalyst; steam or water into gas; release of CO/H2", "TAHH-201, FIC-201, PSV-201/202, AT-201, SIF 4", "decide interstage quench vs cooler; confirm tube-rupture case"),
       ("N4 AGR C-301/C-302: gas carry-over, high level, H2S release, no flow", "foam, LIC-301 failure, pump P-301 trip", "H2S toxic cloud, sour gas to the regenerator or flare, solvent to methanator", "LIC-301, AT-301, PSV-301/302, to sulphur recovery", "define sulphur recovery and sour-flare handling"),
       ("N5 R-301 methanation: high temperature, CO / CO2 breakthrough", "AGR upset sends CO2 / CO forward", "exotherm in the catalyst bed, overpressure, loss of catalyst", "TI-301, TAHH-201 chain, PSV-303, SIF 4", "add a bed-temperature trip and CO analyser at AGR outlet; or replace by nitrogen wash (ISD 3)"),
       ("N6 NH3 loop K-401 / R-401 / V-401: high pressure, low V-401 level, hydrogen service", "PIC-401 failure, LV-401 fails open, compressor trip", "200 bar overpressure; gas blow-by into T-501 vents; H2 leak and fire; NH3 release", "PIC-401, PSHH-401, PSV-401/402, LSLL-401, XV-502, AT-401, SIF 5-6", "check metallurgy (hydrogen / nitriding): API 941 gap; size blow-by case"),
       ("N7 T-501 / P-501 NH3 storage: overfill, high pressure, vacuum, loss of refrigeration", "LIC failure, heat ingress, pump-out", "toxic NH3 vapour cloud; cold liquid spill; tank damage", "LIT-501, LSHH-501, XV-501, PSV-501/502, VB-501, AT-501/502, bund (sheet 7), SIF 7-8", "set tank type and containment; refrigeration reliability study"),
       ("N8 R-601 / C-601 / E-601 urea reactor and stripper: low CO2, high pressure, loss of passivation air, carbamate blockage", "K-601 trip, FFIC-601 failure, cooling loss", "NH3-rich hot liquid at 150 bar released; corrosion-driven leaks; solid carbamate; vent with O2 and inerts (UBA p.13, p.8)", "FALL-602, PSHH-601, PSV-601/602, XV-602/603, AT-601, SIF 9-10", "materials and passivation air from licensor; corrosion monitoring in the mechanical-integrity plan"),
       ("N9 K-601 CO2 compressor: surge, trip, high discharge pressure", "process upset, driver trip", "loss of CO2 to R-601, dense-phase CO2 release, asphyxiant in low areas", "UIC-601, PSV-603, XV-602, CO2 detection at low points (A)", "size PSV-603 with a dense-phase method; add CO2 detectors"),
       ("N10 flare / blowdown FL-101, KO-101, BDV-101: flare out, KO liquid, header overload", "simultaneous releases, pilot failure", "unburnt CO / H2S / NH3 release at the flare; liquid carry-over", "KO-101, BDV-101, PSV headers", "sum coincident loads; radiation and dispersion study (API 521: gap)")]
ISD = [("Option", "Idea", "Basis", "Label"),
       ("1 Reduce inventory", f"Size T-501 as a buffer: the urea plant takes all NH3 (S18 = S17). Each storage day holds {NH3_TPD:,.0f} t of NH3; {T501_DAYS:.0f} d = {T501_T:,.0f} t.", "D from the balance; principle (CCPS / Kletz not obtained)", "A"),
       ("2 Moderate conditions", "Store NH3 refrigerated at atmospheric pressure (-33 C, 1.1 bar) rather than pressurised: lower stored energy and release rate.", "Fertilizers Europe tank guidance describes the refrigerated types (S6)", "R (tank types), A (benefit)"),
       ("3 Substitute / simplify", f"Replace methanation by a cryogenic nitrogen wash: no catalytic exotherm and no {CO_METH_PCT:.1f} % H2 loss; surplus N2 S26 ({M[26]*3.6:,.0f} t/h) is available. Needs larger cold box.", "derived from this balance; not verified with a licensor", "A"),
       ("4 Simplify", "Feed R-601 directly from V-401 through P-501 with minimal buffer and keep NH3 / urea areas separate from the gasifier (layout, domino).", "HSE plant-layout guidance: domino effects, occupied buildings (S3)", "R (layout principle), A"),
       ("5 Moderate conditions", "CO2 stripping at synthesis pressure (as drawn) avoids separate medium / low-pressure carbamate recycle loops with their own NH3 inventories.", "UBA 2001 describes the stripping process (p.13); safety benefit is this drawing's claim", "R (process), A (benefit)")]
DETECT = [("Item", "Basis / logic", "Label"),
          ("NH3 gas detection", "AT-401 (V-401 / loop), AT-501 (T-501 outlet and P-501), AT-502 (tank bund low point), AT-601 (urea area). Cold refrigerated release forms a dense cloud: sensors low; enclosed areas also at roof level. 1oo2 alarm, 2oo2 trip (A). EPA Region 7 reports two detectors in an ammonia machinery room per IIAR 2.", "R (EPA S7, IFC S8), A (voting)"),
          ("CO / H2 / H2S detection", "AT-101, AT-102 (gasifier hall), AT-201 (shift), AT-301 (AGR). H2 lighter than air: high points under canopies; H2S heavier: low points. EIGA 15/21: leak detection should supplement or replace flame detection for hydrogen. BE-101 flame detector at the burner.", "R (EIGA S4, IFC S8), A (placement)"),
          ("Isolation of large inventories", "Remotely operated valves at vessel and tank outlets: XV-501 (T-501), XV-502 (V-401), XV-101/102/103 (R-101 feeds), XV-602/603 (R-601 feeds), BDV-101 (blowdown). Fail-safe on loss of power or air.", "R (HSE HSG176 para 128, S1)"),
          ("Containment / bund", f"T-501: containment type set by tank design (single / double / full, S6). Volume rule for flammable liquid bunds, used here by analogy: 110 % of the largest tank or 25 % of the total (HSG176 para 157). For {T501_DAYS:.0f} d storage: tank {T501_M3:,.0f} m3, bund basis {1.1*T501_M3:,.0f} m3. Refrigerated NH3 impoundment code: not obtained.", "R by analogy (S1), A; gap: API 620 / EN 14620"),
          ("Safety distances, layout", "Layout must address domino escalation and occupied buildings (HSE, S3). HSG176 Table 1 distances apply to flammable-liquid tanks, not to NH3. Distances for NH3 / CO / H2S / syngas must come from consequence modelling: not done here (no number given).", "R (S3), gap: OISD-STD-118 / 116, NFPA"),
          ("Fire water, spray, foam", "Water spray for NH3 vapour knock-down and cooling of exposed vessels (A). No flammable-liquid pool basis, so foam not shown. Fire-water demand not sized.", "A; gap: OISD-STD-116/117, NFPA 15/24"),
          ("Ventilation, inerting", f"Gasifier area open-air structure (A). Nitrogen from ASU for purging and start-up inerting: surplus N2 S26 {M[26]*3.6:,.0f} t/h (D). O2 line cleaning and materials from the licensor.", "A; gap: EIGA / CGA O2 standards"),
          ("Flare and blowdown", "KO-101 and FL-101 take PSV outlets (FL-1) and BDV-101; NH3 vents of PSV-501/502/601/602 go to a water scrubber first. Radiation and capacity not computed.", "R (S6: tank vents to flare or wet scrubber), gap: API 521 / 537")]


def sheet7():
    s = SheetB(7, "Coal-to-urea complex: safety design basis, hazards and mitigation", "Sheet 7: hazard identification, detection, mitigation, inherently safer", code="VS-UREA",
               project=f"Coal-to-urea complex, {UREA_MTPA:.2f} Mt/a urea (Rev B)", basis="qualitative; no consequence numbers invented")
    frame(s, 7)
    y = section(s, 20, 84, 1560, "HAZARD IDENTIFICATION   HAZOP-style nodes (qualitative; OSHA 1910.119 PHA incl. facility siting, R S5; no numeric consequences)")
    yb = mltable(s, 20, y, (270, 220, 330, 400, 340), HAZ, 9.3, 10.8, 15)
    y2 = section(s, 20, yb + 8, 1100, "DETECTION AND MITIGATION BASIS")
    yb2 = mltable(s, 20, y2, (150, 790, 160), DETECT, 9.3, 10.8, 15)
    y3 = section(s, 1135, yb + 8, 445, "INHERENTLY SAFER DESIGN NOTES")
    mltable(s, 1135, y3, (95, 210, 85, 55), ISD, 9.0, 10.4, 15)
    return s


# =====================================================================================================================
# 6. RESULTS FILES, LINT, MAIN
# =====================================================================================================================
def results_rows():
    """every metric the validator flagged (UREA_comparisons.csv): Rev A | Rev B | reference | deviation before / after | status"""
    T_ = _trial; ST = T_.S
    dev = lambda a, r: (a / r - 1) * 100
    rows = []
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool)
    def add(metric, a, b_, ref, src, status, unit=""):
        rows.append(dict(metric=metric, unit=unit, rev_a=a, rev_b=b_, reference=ref, source=src,
                         dev_a_pct=round(dev(a, ref), 1) if num(a) and num(ref) and ref else "",
                         dev_b_pct=round(dev(b_, ref), 1) if num(b_) and num(ref) and ref else "", status=status))
    UB = "UBA 2001 (urea BAT notes)"; TF = "Talcher PFR Table E.1 / EIA summary"
    add("WGS K at 1673 K (gasifier)", round(wgs_K_moe(1673.15), 4), round(wgs_K_thermo(1673.15), 4), 0.30682, "thermo 0.6.1 (script)", "closed (fit 0.2 % low; fit error 0.67 % max)")
    add("WGS K at 643 K (HT exit)", round(wgs_K_moe(643.15), 3), round(wgs_K_thermo(643.15), 3), 16.766, "thermo", "closed")
    add("WGS K at 503 K (LT exit)", round(wgs_K_moe(503.15), 2), round(wgs_K_thermo(503.15), 2), 128.61, "thermo", "closed")
    add("WGS reaction heat, kJ/mol (stage mean)", 41.2, round((DH_WGS_HT + DH_WGS_LT) / 2, 2), 39.14, "thermo Cp integrals at 570 K", "closed (stage values 38.41 / 39.76 used)", "kJ/mol")
    add("syngas flow at 145 kg/s coal", round(A.syn_mol, 1), round(T_.syn_mol, 1), 8584.7, "own elemental balance + thermo K", "unchanged (flow independent of K)", "mol/s")
    add("syngas CO at 145 kg/s", round(SA[4]["CO"], 1), round(ST[4]["CO"], 1), 3627.3, "as above", "closed", "mol/s")
    add("syngas H2 at 145 kg/s", round(SA[4]["H2"], 1), round(ST[4]["H2"], 1), 2129.7, "as above", "closed", "mol/s")
    add("HT shift CO conversion", round(A.ht_conv, 4), round(T_.ht_conv, 4), 0.7911, "thermo K", "closed")
    add("H2 after LT shift (S9)", round(SA[9]["H2"], 1), round(ST[9]["H2"], 1), 5656.6, "thermo K", "closed", "mol/s")
    add("NH3 synthesis heat, kJ/mol", 46.1, DH_NH3_700K, 52.34, "thermo Cp integrals 700 K (same calculation as the reference)", "closed (not independent)", "kJ/mol")
    add("NH3 Psat at -33 C (A4)", 1.1, 1.1, 1.029, "CoolProp", "unchanged: 6.9 % within tolerance, A kept", "bar")
    add("ASU specific work, kWh/t O2", 733.8, ASU_KWH_PER_T_O2, 275.0, "TDA DOE-FE-0026142 p.12, 250-300 (single source); validator's 175.6 used an assumed 0.30 second-law efficiency, not used", "closed against TDA mid value; flag: single source", "kWh/t O2")
    add("NH3 per t urea", round(IA["nh3_per_urea"], 4), round(IB["nh3_per_urea"], 4), 0.5714, TF, "closed (full recycle; stoich 0.5671)", "t/t")
    add("CO2 per t urea", round(IA["co2_per_urea"], 4), round(IB["co2_per_urea"], 4), 0.7403, TF, "closed (stoich 0.7328)", "t/t")
    add("make-up gas per t NH3", round(IA["makeup_nm3_per_t_nh3"]), round(IB["makeup_nm3_per_t_nh3"]), 2651, TF, f"closed by ASSUMED 90 % purge recovery (range {makeup_for_r(0.85):,.0f}-{makeup_for_r(0.95):,.0f}); not calibrated", "Nm3/t NH3")
    add("coal feed per t urea", round(IA["coal_per_urea"], 3), round(IB["coal_per_urea"], 3), 0.902, TF + " (coal + pet coke)", "reduced: coal quality, pet-coke blend, 90 % C conversion, methanation H2 loss; not closed (1.74 incl. fuel coal)", "t/t")
    add("coal feed per t NH3", round(IA["coal_per_nh3"], 3), round(IB["coal_per_nh3"], 3), 1.578, TF, "worse by 14 points: methanation takes 14.8 % of H2 (the repo basis ignored it); real plants avoid the loss (wash)", "t/t")
    add("coal LHV per t NH3 (feed only), GJ", 40.85, round(40.85 * IB["coal_per_nh3"] / IA["coal_per_nh3"], 2), 51.3, "EFMA Booklet 1 (relative factor, incl. fuel)", "reduced / same explanation", "GJ/t NH3")
    add("CO2 compression power, kWh/t CO2", 149, UBA_CO2_COMP_KWH_PER_T_CO2, 126, UB + " p.24 (D)", "closed (now uses the reference itself)", "kWh/t CO2")
    add("urea reactor CO2 conversion at N/C 3.5", 58.4, 58.4, 60.0, UB, "unchanged (repo fit, within the 60-70 % range edge)", "%")
    add("urea reactor conditions", "180 C 150 bar N/C 3.5", "180 C 150 bar N/C 3.5", "180-210 C, 140-250 atm, N/C 2.8-4", UB, "unchanged, agrees")
    add("steam per t urea, t/t", "not computed", UBA_STEAM_T_PER_T, "0.85-1.3", UB + " p.19, 24", "closed by adoption of the sourced figure (not independent)", "t/t")
    add("CO2 captured per t NH3", round(M[10] / M[17] if False else (A.co2_cap * 44.01) / (A.nh3 * 17.031), 2), round(M[10] / M[17], 2), "", "no reference found", "unchanged (no reference)", "t/t")
    add("K-401 make-up compression power", "not computed", round(K401_MW, 1), "7.43 kJ/mol equivalent (validator 55.95 MW at 145 kg/s)", "CoolProp (validator and this run)", "added; consistent", "MW")
    add("K-601 CO2 compression power", "not computed", round(K601_MW, 1), "", UB, "added", "MW")
    add("cold-gas efficiency", round(CGE_A * 100, 2), round(CGE_B * 100, 2), 66.64, "validator thermo recompute (grade C coal HHV)", "unchanged (within 5 %)", "%")
    add("pressure items without relief or reason (sheet 1)", 7, 0, 0, "validation lint", "closed: 14 PSV + VB-501 drawn, reasons for the rest (sheet 5)")
    return rows


def write_results(prefix):
    rows = results_rows()
    with open(prefix + ".csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
    md = [f"# UREA Rev B results (gen_pid_urea.py, 11 Nov 2026)", "",
          f"Rev B balance: coal {COAL_KG_S:.2f} kg/s, urea {UREA_T_H:.1f} t/h = {UREA_MTPA:.3f} Mt/a, NH3 {NH3_TPD:,.0f} t/d, mass closure error {ERR_MASS:+.3f} % (Rev A {ERR_MASS_A:+.3f} %), C, O, N, S exact, H = +2 x n(H2S) repo quirk. "
          "Rev A is recomputed from the same code with the Rev B changes switched off and is asserted against the recorded repo run. Numbers below are produced by the generator; the CSV has the same rows.", "",
          "## Rating decision", "",
          f"The repo single-pass train made 1.10 Mt/a at 145 kg/s coal. With full recycle the same NH3 train makes {OPT1_UREA_MTPA:.2f} Mt/a (2.4 x Talcher 1.27 Mt/a, TEIA). Choice: size to 1.10 Mt/a (coal {COAL_KG_S:.1f} kg/s). "
          "All flows are linear in the coal feed (asserted), so per-tonne ratios are the same for both options; only equipment sizes change. Owner may reverse the choice by changing UREA_TARGET_MTPA.", "",
          "## (a) Validator-flagged metrics", "", "| metric | Rev A | Rev B | reference | dev A % | dev B % | status |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['metric']} | {r['rev_a']} | {r['rev_b']} | {r['reference']} | {r['dev_a_pct']} | {r['dev_b_pct']} | {r['status']} |")
    md += ["", "## (b) Not closed, and why", "",
           f"- Coal per t urea {IB['coal_per_urea']:.2f} t/t against Talcher 0.90 t/t (coal + pet coke) is +68 %; per t NH3 {IB['coal_per_nh3']:.2f} against 1.58 (+69 %). Causes not separable here: Indian high-ash coal against a pet-coke blend, 90 % carbon conversion (repo), and the 14.8 % H2 lost to methanation. Talcher's own gasifier and wash design is not public.",
           "- Purge recovery 90 % is an assumption (A) that happens to land the make-up within 0.2 % of Talcher; the range 0.85-0.95 gives 2,653-2,656 against the loop-only value 2,857 without recovery. It is not evidence.",
           "- ASU power rests on one document (TDA / DOE-FE-0026142, 'ton' undefined); a second independent source was not found. The validator's 175.6 kWh/t O2 depends on an assumed second-law efficiency and was not adopted.",
           "- Gasifier K: the thermodynamic K is for the equilibrium CO + H2O = CO2 + H2; the DLR rig reaches this equilibrium near 1495 K (GAP_CLOSURE_THERMO), so 1673 K is an assumption of the repo, not verified.",
           "- Methanation complete conversion, knock-out ideality (no CO2 or H2S in the condensate), complete carbamate recycle and the 40 C separator temperature are assumptions (A).",
           "- Not computed: E-101/102/103/401/602 and C-301/302 duties, vessel sizes, flare load, steam balance (no property model in the stdlib toolkit).", "",
           "## (c) Safety items", "",
           f"Present now: relief schedule with {len(RELIEF_ROWS)-1} rows (14 PSV + VB-501 drawn, 7 sized by screening, others with a reason or 'not sized: needs ...'); ESD cause-and-effect matrix {len(CE)} initiators x {len(FE)} final elements, every XV, BDV, detector and trip tag drawn on sheet 1; SIF list {len(SIF)-1} functions with ASSUMED SIL; detection / mitigation basis (8 items); hazard identification 10 nodes; 5 inherently-safer notes; KO-101 and flare shown.",
           "Still gaps (standards not obtained): API 520/521/2000/620/537 (relief and flare sizing, tank venting), IEC 61511 and LOPA (SIL), OISD-STD-116/117/118/144, NFPA 15/24, IIAR 2, EN 14620, PESO SMPV(U), API 941, EIGA/CGA O2 standards, dense-phase CO2 relief method, NH3 dispersion and layout distances (no consequence model run), fire-water demand, scrubber and flare capacity.", "",
           "## (d) Verify with a licensor / vendor", "",
           "- Urea licensor: reactor and stripper design, carbamate recycle fraction, steam (0.92 t/t is Stamicarbon supplier data via UBA 2001), NH3 and CO2 losses, passivation air and vent handling, relief cases for R-601 and C-601 (two-phase).",
           "- Gasifier licensor: carbon conversion, K (equilibrium) approach, quench vs radiant cooler, slag lock-hopper cycle, relief and blowdown, O2-service rules.",
           "- ASU vendor: specific power (275 kWh/t O2 is a range 250-300 from one report), N2 export, cold-box relief.",
           "- Syngas purification: methanation vs nitrogen wash, purge-gas recovery rate, inert level in the loop (S13 is assumed to remove CH4).",
           "- Ammonia storage and refrigeration: tank type and size, containment, scrubber.", ""]
    with open(prefix + ".md", "w") as f: f.write("\n".join(md))


def _tags_of(sh):
    svg = sh.svg()
    txt = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
    tags = set()
    for t in txt:
        for m in re.findall(r"\b[A-Z]{1,5}-\d{3}[A-Z]?\b", t): tags.add(m)
    for a_, b_ in re.findall(r">([A-Z]{2,5})</text><text[^>]*>(\d{3}[A-Z]?)</text>", svg): tags.add(f"{a_}-{b_}")
    return tags


def lint(sheets):
    res = []
    s1 = sheets[0]; t1 = _tags_of(s1)
    dia = DIAM.get(1, set()); hm = set(S)
    res.append(f"stream diamonds on sheet 1: {len(dia)}, HMB columns: {len(hm)}, match: {dia == hm}")
    eq = [r[0] for r in EQUIP[1:] + EQUIP2[1:]]
    miss = [e for e in eq if e not in t1]
    res.append(f"equipment tags in lists {len(eq)}, missing from drawing: {miss}")
    pat = re.compile(r"\b(?:XV|BDV|AT|BE|LSHH|LSLL|FALL|PSHH|TAHH|HS|PSV|UIC|FIC|LIC|PIC|FFIC|LV|PV|FV|VB|TI|LIT)-\d{3}[A-Z]?\b")
    used = set()
    for sh in sheets[2:]:
        for t in _tags_of(sh):
            if pat.fullmatch(t): used.add(t)
    notin = sorted(t for t in used if t not in t1)
    res.append(f"instrument / valve tags used on sheets 3-7: {len(used)}, not on sheet 1: {notin}")
    sched = " ".join(" ".join(r) for r in RELIEF_ROWS)
    miss_psv = [p for p in PSV_TAGS if p not in t1]; unsched = [p for p in PSV_TAGS if p not in sched]
    res.append(f"relief devices {len(PSV_TAGS)}: missing on sheet 1 {miss_psv}; missing in schedule {unsched}")
    rows_items = " ".join(r[0] for r in RELIEF_ROWS[1:])
    res.append("pressure items without a schedule row: " + str([p for p in PRESSURE_ITEMS if not any(p.split("/")[0].strip() in r[0] or p in r[0] for r in RELIEF_ROWS[1:])]))
    dupes = [t for t in eq if eq.count(t) > 1]
    res.append(f"duplicate equipment tags: {dupes}")
    ok = dia == hm and not miss and not notin and not miss_psv and not unsched
    return ok, res


def build_all():
    return [sheet1(), sheet2(), sheet3(), sheet4(), sheet5(), sheet6(), sheet7()]


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if "--verify-repo" in sys.argv:
        vp = sys.argv[sys.argv.index("--verify-repo") + 1]; verify_repo(vp); args = [a for a in args if a != vp]
    resp = None
    if "--results" in sys.argv:
        resp = sys.argv[sys.argv.index("--results") + 1]; args = [a for a in args if a != resp]
    djs = None
    if "--dump-json" in sys.argv:
        djs = sys.argv[sys.argv.index("--dump-json") + 1]; args = [a for a in args if a != djs]
    out = args[0]
    sheets = build_all()
    write_html(sheets, out, "Coal-to-urea P&ID set Rev B", previews="--previews" in sys.argv)
    if resp: write_results(resp)
    if djs:
        json.dump(dict(coal=COAL_KG_S, streams={str(k): v for k, v in S.items()}, K=dict(g=B.K, ht=wgs_K_thermo(HT_K + HT_APPR), lt=wgs_K_thermo(LT_K + LT_APPR)),
                       ht_conv=B.ht_conv, lt_conv=B.lt_conv, nh3=B.nh3, urea=B.urea, F=B.F, rec=B.rec, purge=B.purge), open(djs, "w"))
    ok, res = lint(sheets)
    print("LINT", "PASS" if ok else "FAIL")
    for r in res: print("  " + r)
    print(f"ok {len(sheets)} sheets; closure: in {M_IN*3.6:,.1f} t/h, out {M_OUT*3.6:,.1f} t/h, error {ERR_MASS:+.3f} %; urea {UREA_T_H:.1f} t/h = {UREA_MTPA:.3f} Mt/a; coal {COAL_KG_S:.2f} kg/s")

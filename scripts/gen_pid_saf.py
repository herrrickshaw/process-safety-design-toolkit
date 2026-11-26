#!/usr/bin/env python3
"""Generate the SAF by HEFA (30,000 t/yr UCO feed, NREL jet-mode slate) conceptual P&ID set, Rev B: P&ID, heat and material balance,
balance basis and sensitivity, two scenario sheets, and a safety design basis (relief schedule, SIFs, cause-and-effect, detection, HAZOP nodes, inherent safety).

Rev B changes against Rev A (see the box on sheet 2): the DPR template's SAF 24,000 t/yr is NOT used (it is 80 wt % of the oil, above every open source). Feed 30,000 t/yr UCO is
kept (S, template); the product slate is the NREL TP-5100-87803 Table G-1 jet-mode slate (S): kerosene 46.1, diesel 30.4, naphtha 8.5, LPG 6.0, fuel gas 1.5 wt % of oil.
Stage-1 chemistry (pathway shares, fatty-acid mix) stays A. The reaction heat is DERIVED from heats of formation (frozen tool values, see HF_*), the recycle ratio follows
from it, the stage-2 exotherm is derived, and the V-201 vapour carry-over, fractionator feed phase and E-402/E-403 duties are frozen outputs of a thermo/CoolProp run
(command in tests/crosscheck/saf_revb_thermo.py). Nothing is taken from a licensor or vendor. Stage-2 and fractionator thermo are screening (Peng-Robinson, kij = 0).

Usage (standard library only; the thermo run needs the optional venv and is only a CHECK that refreshes the frozen constants):
    python3 scripts/gen_pid_saf.py docs/pid/SAF_PID_Set_RevB.html [--previews]
Screening aid, not certified design."""
import sys, os, math, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pidlib import *
from process_safety.plant_units import adiabatic_rise_K
from process_safety import relief as RLF


class SheetB(Sheet):
    """pidlib prints 'Rev A' in the frame; Rev B overrides it in the SVG string (pidlib is not edited)."""
    def svg(self): return super().svg().replace("  |  Rev A", "  |  Rev B").replace("Draft A. Screening aid", "Draft B. Screening aid")
NSHEETS = 8

# ====================================================================================================================
# 1. HEAT AND MATERIAL BALANCE (computed). Atomic masses (conventional standard atomic weights): C 12.011, H 1.008, O 15.999
# ====================================================================================================================
AM = {"C": 12.011, "H": 1.008, "O": 15.999}
def mw(c, h, o=0): return AM["C"] * c + AM["H"] * h + AM["O"] * o
M_H2, M_H2O, M_CO, M_CO2 = mw(0, 2), mw(0, 2, 1), mw(1, 0, 1), mw(1, 0, 2)
def mwp(n): return mw(n, 2 * n + 2)                       # n-paraffin CnH(2n+2)

# --- S: sourced -------------------------------------------------------------------------------------------------
FEED_T_YR = 30000.0                                      # S: DPR template sections 1 and 9 (UCO 3,00,00,000 kg/yr). The template SAF 24,000 t/yr is rejected, see change box.
SLATE_NREL = dict(kero=46.1, diesel=30.4, naph=8.5, lpg=6.0, fg=1.5)   # S: NREL/TP-5100-87803, SAF State-of-Industry Report HEFA pathway, Table G-1 (printed p.118), jet mode, wt % of oil
NREL_OTHER = dict(co_co2=4.0, aq=8.0, h2_in=4.5)         # S: same table: CO + CO2 4.0, aqueous 8.0, H2 in 4.5 wt % of oil
NREL_RD = dict(diesel=85.0, light=7.0, h2_in=4.0)        # S: same table, renewable-diesel mode (jet 0)
# Frozen tool values (S, tool): standard enthalpies of formation, ideal gas, 25 C, kJ/mol. Command and run: tests/crosscheck/saf_revb_thermo.py (chemicals 1.5.2 Hfg).
HF_H2O, HF_CO, HF_CO2, HF_PROP = -241.822, -110.525, -393.474, -104.39
HF_ALK_A, HF_ALK_B = -42.64, -20.69                      # linear fit Hf(CnH2n+2) = A + B n over C2..C4, C7, C11, C14..C18 (max residual 1.1 kJ/mol)
HF_TG = {"db": {"C16:0": -2053.09, "C18:0": -2176.93, "C18:1": -1825.27, "C18:2": -1473.61},   # triglyceride Hfg from the chemicals database (group-contribution estimates)
         "fa": {"C16:0": -2119.69, "C18:0": -2251.99, "C18:1": -1923.73, "C18:2": -1528.39}}   # via glycerol + 3 fatty acids - 3 H2O + 3 esterification (ethyl acetate analogue, -18.65 kJ/mol)
CP_L, CP_L_FEED, CP_L_COOL = 3.23, 2.83, 2.86            # S, tool: CoolProp n-dodecane liquid, mean cp kJ/kg/K: 250-340 C at 50 bar; 80-300 C at 50 bar; 45-350 C at 50 bar
LAM_N = 306.5                                            # S, tool: CoolProp n-heptane latent heat at 1.5 bar, kJ/kg (Rev A had 300, A)
# Frozen outputs of the PR-EOS flashes (thermo 0.6.1, kij = 0, screening) for the CURRENT balance; refreshed by tests/crosscheck/saf_revb_thermo.py
# Frozen thermo outputs (S, tool; thermo 0.6.1 Peng-Robinson, kij = 0, screening; run: tests/crosscheck/saf_revb_thermo.py, 2026-11-11). They depend on the balance below;
# fp_par9 (paraffin in stream 9, kg/h) is the fingerprint: if the A inputs change, the assert further down fails and the run must be repeated.
FROZEN = dict(PHI=0.0904,       # fraction of the paraffin in stream 9 that leaves V-201 as vapour at 340 C, 49.5 bar
              H_COND=786.2,     # kJ/kg: carried paraffin vapour 340 C (partial pressure 3.3 bar) to liquid 50 C, 47 bar
              E403_KW=462.5,    # E-403: C-401 feed 45 C liquid at 47 bar to feed_c at 1.5 bar (52.4 mol % vapour)
              E402_KW=160.3,    # E-402 from the column energy balance (Qcond + products - feed)
              E401_KW=87.2,     # E-401 overhead vapour at 113 C to liquid/vapour at 40 C
              VF_FEED=0.524, fp_par9=25218.3)

# --- A inputs (all listed on sheet 3 under "ASSUMED, to be confirmed by licensor or vendor") ---
DAYS_PER_YR = 330.0                                      # A: lead's instruction; NOT found in the template text
HOURS_PER_DAY = 24.0                                     # A: continuous running
FA = {"C16:0": (16, 32, 0.15, 0), "C18:0": (18, 36, 0.05, 0), "C18:1": (18, 34, 0.45, 1), "C18:2": (18, 32, 0.35, 2)}   # A: (C, H of acid, mole fraction, C=C bonds)
F_HDO, F_DCO2, F_DCO = 0.85, 0.08, 0.07                  # A: share of fatty-acid chains removed by hydrodeoxygenation / decarboxylation / decarbonylation
WASTE_FRAC = 0.015                                       # A: pretreatment waste as share of raw UCO
NCARB = dict(kero=11, diesel=16, naph=7, lpg2=4, fg=2)   # A: carbon number representing each cut as an n-paraffin (cracking LPG as butane, fuel gas as ethane); stage-1 propane is S/D
Q_FRAC = 0.5                                             # A: share of the recycle liquid used as quench
EXCESS = 3.0                                             # A: gas circulation = 3 x chemical H2 consumption (pure H2 loop)
CP_G, CP_V, LAM_W, CP_W = 14.3, 2.0, 2257.0, 4.19        # A: kJ/kg/K H2 gas, steam; kJ/kg water latent; kJ/kg/K water liquid
DT_R1 = 45.0                                             # A: target net bed rise R-201 (fits the 300-350 C deoxygenation window, NREL App. D.2 p.103); R_TOT now follows from it
GAMMA, ETA, RGAS = 1.41, 0.75, 8.314                     # A: H2 heat-capacity ratio, compressor isentropic efficiency; R = 8.314 J/mol/K
RR = 1.0                                                 # A: fractionator reflux ratio
TC = dict(uco=40, pre=80, in1=300, hot=340, cold=50, cold2=45, tank=45, T_H=275, in2=300, feed_c=210, top=112, saf=212, rd=303)   # C. T_H = E-201 outlet (A; TG fouling/polymerisation risk above about 250 C is not assessed). in2: inside the NREL 299-343 C window (S, p.103); feed_c A (PR flash: 52 mol % vapour, reboiler duty positive); top/saf/rd: D, PR/CoolProp dew and bubble points at 1.5 bar
P_BAR = dict(drum=3, pump=58, r1=50, v201=49.5, v202=47, kin=47, kout=53, r2=50, v301=47, col=1.5, tank=1.1)   # A: bar(a)


def balance(feed_t_yr=FEED_T_YR, slate=SLATE_NREL):
    """every flow in kg/h. Stage 1 (stoichiometry, A pathway shares) gives propane, water, CO/CO2 and hydrotreated paraffin; stage 2 splits the hydrotreated paraffin into the
    NREL slate. The hydrocarbon pool P (stage-1 propane + stage-2 products) is solved from carbon closure, hydrogen from the H balance (cross-checked by C-C scissions)."""
    nC = sum(v[0] * v[2] for v in FA.values()); sat = sum(v[3] * v[2] for v in FA.values()); Hacid = sum(v[1] * v[2] for v in FA.values())
    assert abs(sum(v[2] for v in FA.values()) - 1) < 1e-12 and abs(F_HDO + F_DCO2 + F_DCO - 1) < 1e-12
    Cch, Hch, Och = nC + 1, Hacid - 1 + 5 / 3, 2.0
    mwch = mw(Cch, Hch, Och); k = 1 / mwch
    nH2 = sat + 1 + 3 * F_HDO + F_DCO; nH2O = 2 * F_HDO + F_DCO
    Cht = nC - F_DCO2 - F_DCO; Hht = 2 * Cht + 2
    assert abs((Hch + 2 * nH2 - 2 * nH2O - 8 / 3) - Hht) < 1e-9, "stage-1 hydrogen balance does not close"
    hrs = DAYS_PER_YR * HOURS_PER_DAY
    raw = feed_t_yr * 1000 / hrs; F = raw * (1 - WASTE_FRAC); kF = F * k
    prop = k / 3 * mwp(3) * F
    Ctot = kF * (Cht + 1)                                  # kmol C in hydrocarbons (chains + propane)
    tot_s = sum(slate.values()); w = {x: v / tot_s for x, v in slate.items()}
    c_ = lambda n: n / mwp(n)                              # kmol C per kg n-paraffin
    P = (Ctot - prop * (c_(3) - c_(NCARB["lpg2"]))) / (sum(w[x] * c_(NCARB[x]) for x in ("kero", "diesel", "naph", "fg")) + w["lpg"] * c_(NCARB["lpg2"]))
    m = {x: w[x] * P for x in ("kero", "diesel", "naph", "fg")}
    lpg2 = w["lpg"] * P - prop
    assert lpg2 > 0, "slate LPG share is smaller than stage-1 propane"
    saf, rd, nap, fg = m["kero"], m["diesel"], m["naph"], m["fg"]
    h_prod = sum(mass / mwp(NCARB[x]) * (2 * NCARB[x] + 2) for x, mass in (("kero", saf), ("diesel", rd), ("naph", nap), ("fg", fg), ("lpg2", lpg2))) + prop / mwp(3) * 8
    h2_s1 = kF * nH2 * M_H2
    h2_tot = (h_prod + 2 * kF * nH2O - kF * Hch) / 2 * M_H2
    h2_s2 = h2_tot - h2_s1
    n_prod = sum(mass / mwp(NCARB[x]) for x, mass in (("kero", saf), ("diesel", rd), ("naph", nap), ("fg", fg), ("lpg2", lpg2)))
    assert abs((n_prod - kF) * M_H2 - h2_s2) < 1e-6 * h2_tot, "stage-2 H2 from scissions does not match the H balance"
    co2, co, h2o = kF * F_DCO2 * M_CO2, kF * F_DCO * M_CO, kF * nH2O * M_H2O
    mht = kF * mw(Cht, Hht)
    assert abs(mht + h2_s2 - (saf + nap + fg + lpg2 + rd)) < 1e-6 * mht, "stage-2 mass does not close"
    return dict(F=F, raw=raw, waste=raw - F, k=k, kF=kF, mwch=mwch, Cch=Cch, Hch=Hch, nC=nC, Cht=Cht, Hht=Hht, nH2=nH2, nH2O=nH2O, saf=saf, nap=nap, fg=fg, lpg2=lpg2, rd=rd,
                prop=prop, h2_tot=h2_tot, h2_s1=h2_s1, h2_s2=h2_s2, co2=co2, co=co, h2o=h2o, mht=mht, sat=sat, P=P, w=w)


B = balance()
F, S1, S2 = B["F"], B["h2_s1"], B["h2_s2"]
T_YR = DAYS_PER_YR * HOURS_PER_DAY / 1000                                       # t/yr per kg/h

# ---- stage-1 reaction heat from heats of formation (D from frozen S tool values), two triglyceride routes ----
def hf_alk(n): return HF_ALK_A + HF_ALK_B * n
def dH_stage1(route):
    """kJ per mol fatty chain (products - reactants, H2 = 0); gas-phase 25 C"""
    prod = HF_PROP / 3; react = 0.0
    for kk, (c_, h_, x, db) in FA.items():
        react += x * HF_TG[route][kk] / 3
        prod += x * (F_HDO * (hf_alk(c_) + 2 * HF_H2O) + F_DCO2 * (hf_alk(c_ - 1) + HF_CO2) + F_DCO * (hf_alk(c_ - 1) + HF_CO + HF_H2O))
    return prod - react
Q1_ROUTES = {r: -dH_stage1(r) / B["mwch"] * 1000 for r in HF_TG}                # kJ/kg UCO (MJ/kg x 1000)
Q1 = sum(Q1_ROUTES.values()) / len(Q1_ROUTES)                                    # kJ/kg clean UCO, mean of the two routes (+/- 8 % between them, treat as +/- 10 %)
Q1_KW = Q1 * F / 3600.0
GAS1 = EXCESS * S1 / F * CP_G                                                    # kJ/K per kg fresh feed carried by the circulating gas
R_TOT = (Q1 / DT_R1 - GAS1) / CP_L - 1                                           # D: liquid recycle (kg/kg fresh) that holds the net rise at DT_R1
assert R_TOT > 0
rin, rq = R_TOT * F * (1 - Q_FRAC), R_TOT * F * Q_FRAC
B["rin"], B["rq"] = rin, rq
PAR9 = B["mht"] + rin + rq                                                      # kg/h hydrotreated paraffin in the reactor effluent
CARRY = FROZEN["PHI"] * PAR9                                                    # kg/h paraffin vapour carried over by V-201 gas (frozen PR flash fraction), condensed in E-202/V-202, returned via P-203
assert CARRY < rq, "carry-over larger than the quench stream"
if FROZEN.get("fp_par9"): assert abs(PAR9 - FROZEN["fp_par9"]) < 2e-3 * PAR9, f"frozen thermo constants are stale (paraffin in stream 9 is {PAR9:.0f} kg/h): rerun tests/crosscheck/saf_revb_thermo.py"

# ---- stage-2 reaction heat: Hf(alkane) is linear in n, carbon is conserved, so dH = HF_ALK_A per C-C scission = per mol H2 consumed ----
Q2_KW = -HF_ALK_A * (S2 / M_H2) * 1000 / 3600.0
Q2_KJH = Q2_KW * 3600
ISOM_NOTE = "isomerisation heat neglected (A, small)"

# components (rows of the HMB), element formulas (C, H, O) per molecule
COMPS = ["UCO (TG)", "Waste", "H2", "H2O", "CO", "CO2", "Propane", "HT paraffin", "Fuel gas", "Crack LPG", "Naphtha cut", "SAF cut", "RD cut"]
FORM = {"UCO (TG)": (B["Cch"], B["Hch"], 2.0), "H2": (0, 2, 0), "H2O": (0, 2, 1), "CO": (1, 0, 1), "CO2": (1, 0, 2), "Propane": (3, 8, 0), "HT paraffin": (B["Cht"], B["Hht"], 0),
        "Fuel gas": (2, 6, 0), "Crack LPG": (4, 10, 0), "Naphtha cut": (7, 16, 0), "SAF cut": (11, 24, 0), "RD cut": (16, 34, 0)}
def elem_mass(comp, kg):
    if comp == "Waste": return (0, 0, 0)
    c, h, o = FORM[comp]; m_ = mw(c, h, o)
    return (kg * AM["C"] * c / m_, kg * AM["H"] * h / m_, kg * AM["O"] * o / m_)

# ---- stage-2 outlet temperature (D): adiabatic, liquid + circulating gas; compare with the NREL 299-343 C window ----
EXCESS2 = EXCESS
G2 = EXCESS2 * S2
T_OUT2 = TC["in2"] + Q2_KW * 3600 / (B["mht"] * CP_L + G2 * CP_G)
Q_QUENCH_REQ = max(0.0, (Q2_KW * 3600 - B["mht"] * CP_L * (343 - TC["in2"])) / (CP_G * (343 - 65)))   # kg/h cold H2 that would be needed to hold 343 C: 0 means none
T1K = TC["cold"] + 273.15
T2K = T1K * (P_BAR["kout"] / P_BAR["kin"]) ** ((GAMMA - 1) / GAMMA)
Tdis = (T1K + (T2K - T1K) / ETA) - 273.15
TC["out2"] = round(T_OUT2)

ST = {}   # stream number -> dict(comp -> kg/h)
ST[1] = {"UCO (TG)": F, "Waste": B["waste"]}
ST[2] = {"Waste": B["waste"]}
ST[3] = {"UCO (TG)": F}
ST[4] = {"HT paraffin": rin}
ST[5] = {"UCO (TG)": F, "HT paraffin": rin}
ST[6] = {"HT paraffin": rq}
ST[7] = {"H2": B["h2_tot"]}
ST[8] = {"H2": EXCESS * S1}
ST[9] = {"HT paraffin": PAR9, "H2": (EXCESS - 1) * S1, "H2O": B["h2o"], "CO": B["co"], "CO2": B["co2"], "Propane": B["prop"]}
ST[10] = {"HT paraffin": PAR9 - CARRY}
ST[11] = {"HT paraffin": B["mht"]}
ST[12] = {"H2": (EXCESS - 1) * S1, "H2O": B["h2o"], "CO": B["co"], "CO2": B["co2"], "Propane": B["prop"], "HT paraffin": CARRY}
ST[13] = {"H2": (EXCESS - 1) * S1, "CO": B["co"], "CO2": B["co2"], "Propane": B["prop"]}
ST[14] = {"H2O": B["h2o"]}
ST[15] = {"CO": B["co"], "CO2": B["co2"], "Propane": B["prop"]}
ST[16] = {"H2": (EXCESS - 1) * S1}
ST[17] = {"H2": G2}
LIGHT = {"Fuel gas": B["fg"], "Crack LPG": B["lpg2"]}
PRODS = {"Naphtha cut": B["nap"], "SAF cut": B["saf"], "RD cut": B["rd"]}
ST[18] = {"H2": G2 - S2, **LIGHT, **PRODS}
ST[19] = {"H2": G2 - S2}
ST[20] = {**LIGHT, **PRODS}
ST[21] = dict(LIGHT)
ST[22] = {"Naphtha cut": B["nap"]}
ST[23] = {"SAF cut": B["saf"]}
ST[24] = {"RD cut": B["rd"]}
ST[25] = {"HT paraffin": CARRY}
for n in ST: ST[n] = {c: v for c, v in ST[n].items() if v}
def tot(n): return sum(ST[n].values())
def tot_el(ns):
    e = [0.0, 0.0, 0.0]
    for n in ns:
        for c, v in ST[n].items():
            for i, x in enumerate(elem_mass(c, v)): e[i] += x
    return e

NODES = [("U-101", [1], [2, 3]), ("R-201", [5, 6, 8], [9]), ("V-201", [9], [10, 12]), ("P-202 split + P-203", [10, 25], [4, 6, 11]), ("V-202", [12], [13, 14, 25]), ("G-201", [13], [15, 16]),
         ("mix 3+4", [3, 4], [5]), ("K-201", [7, 16, 19], [8, 17]), ("R-301", [11, 17], [18]), ("V-301", [18], [19, 20]), ("C-401", [20], [21, 22, 23, 24])]
NODE_ERR = {}
for nm, i_, o_ in NODES:
    a_, b_ = sum(tot(n) for n in i_), sum(tot(n) for n in o_)
    NODE_ERR[nm] = abs(a_ - b_) / a_ * 100
    assert NODE_ERR[nm] < 0.1, f"node {nm} does not close: {a_} vs {b_}"
IN_EXT, OUT_EXT = [1, 7], [2, 14, 15, 21, 22, 23, 24]
M_IN, M_OUT = sum(tot(n) for n in IN_EXT), sum(tot(n) for n in OUT_EXT)
ERR_MASS = abs(M_IN - M_OUT) / M_IN * 100
assert ERR_MASS < 0.1, (M_IN, M_OUT)
E_IN, E_OUT = tot_el(IN_EXT), tot_el(OUT_EXT)
ERR_EL = [abs(a_ - b_) / a_ * 100 for a_, b_ in zip(E_IN, E_OUT)]
assert max(ERR_EL) < 0.1, ERR_EL
assert abs(tot(1) * T_YR - FEED_T_YR) < 1
SAF_TYR = tot(23) * T_YR
SLATE_YR = {"SAF": SAF_TYR, "RD": tot(24) * T_YR, "naphtha": tot(22) * T_YR, "LPG (propane + C4)": (B["prop"] + B["lpg2"]) * T_YR, "fuel gas": B["fg"] * T_YR}

# ---- duties (kW) ----
def kW(kg_h, cp, dT): return kg_h * cp * dT / 3600.0
K_MOL_H = (EXCESS * S1 + G2) / M_H2 * 1000
W_K201 = K_MOL_H * (GAMMA / (GAMMA - 1)) * RGAS * T1K * ((P_BAR["kout"] / P_BAR["kin"]) ** ((GAMMA - 1) / GAMMA) - 1) / ETA / 3600 / 1000
c_main = F * CP_L_FEED + EXCESS * S1 * CP_G; c_rec = rin * CP_L
T_REC = (TC["in1"] * (c_main + c_rec) - TC["T_H"] * c_main) / c_rec               # D: recycle temperature that makes the R-201 inlet mix 300 C with E-201 outlet at T_H (A)
T_MIXD = ((PAR9 - CARRY) * TC["hot"] + CARRY * TC["cold"]) / PAR9               # P-202 discharge header: hot V-201 liquid + cold V-202 condensate (stream 25) returned by P-203
assert T_REC <= T_MIXD + 1e-9, (T_REC, T_MIXD)
T_MIX = (F * CP_L_FEED * TC["pre"] + EXCESS * S1 * CP_G * Tdis) / (F * CP_L_FEED + EXCESS * S1 * CP_G)
DUTY = {}
DUTY["E-201"] = (c_main * (TC["T_H"] - T_MIX)) / 3600
DUTY["R-201 heat release"] = Q1_KW
DUTY["E-203"] = kW(rin + rq, CP_L, T_MIXD - T_REC)
DUTY["E-202"] = (kW((EXCESS - 1) * S1, CP_G, TC["hot"] - TC["cold"]) + B["h2o"] * (CP_V * (TC["hot"] - 100) + LAM_W + CP_W * (100 - TC["cold"])) / 3600
                 + kW(B["prop"] + B["co"] + B["co2"], CP_L_COOL, TC["hot"] - TC["cold"]) + CARRY * FROZEN["H_COND"] / 3600)
DUTY["E-301 (cooling)"] = kW(B["mht"], CP_L, T_MIXD - TC["in2"])
DUTY["R-301 heat release"] = Q2_KW
DUTY["E-302"] = kW(tot(18) - (G2 - S2), CP_L_COOL, TC["out2"] - TC["cold2"]) + kW(G2 - S2, CP_G, TC["out2"] - TC["cold2"])
DUTY["E-403"] = FROZEN["E403_KW"]
DUTY["E-401"] = FROZEN["E401_KW"]
DUTY["E-402"] = FROZEN["E402_KW"]
DUTY["E-404"] = kW(B["rd"], CP_L_COOL, TC["rd"] - TC["tank"])
DUTY["E-405"] = kW(B["saf"], CP_L_COOL, TC["saf"] - TC["tank"])
DUTY["K-201 shaft"] = W_K201
# ---- runaway cases (heat per kg fresh feed over fresh + diluent + circulating gas) with the DERIVED heat of reaction ----
CEFF_NORMAL = (1 + R_TOT) * CP_L + GAS1
DT_NORMAL = adiabatic_rise_K(Q1, CEFF_NORMAL)
DT_NO_QUENCH = adiabatic_rise_K(Q1, (1 + R_TOT * (1 - Q_FRAC)) * CP_L + GAS1)
DT_NO_DILUENT = adiabatic_rise_K(Q1, CP_L + GAS1)
DT_R2_ADIAB = T_OUT2 - TC["in2"]
DT_R1_AT_RA1 = Q1 / (CP_L * (1 + 1.0) + GAS1)                                    # sensitivity: recycle ratio 1:1 (NREL text), no extra quench
LOAD_E202 = tot(12)
LOAD_E401 = (1 + RR) * B["nap"] + B["fg"] + B["lpg2"]
H2_RATIO_SAF = B["h2_tot"] / (B["saf"] / 1000)
H2_PCT_OIL = B["h2_tot"] / F * 100

# ---- sensitivity cases (sheet 3): same model, other slate or feed ----
FEED_FOR_24K = FEED_T_YR * 24000.0 / SAF_TYR                                      # t/yr UCO that holds the DPR's 24,000 t/yr SAF with this model
B52 = balance(FEED_FOR_24K)
IEA_SAF = 0.15 * B["mht"] * T_YR                                                  # D: IEA Task 39 sec 5.1.4: about 15 % of hydrotreated product falls in the jet range with no extra cracking
# ---- relief sizing with the toolkit (process_safety/relief.py: API 520-I gas equation, derived; standard text not read; set pressures, k, Z, back pressure are A) ----
DESIGN_BARG = dict(loop=60.0, col=4.0)                    # A: HP loop design/set 60 barg (about 15 % over the 53 bara discharge); column 4 barg
BACKP_KPA = 350.0                                         # A: flare header back pressure, kPa abs
def size_gas(W, T_C, M, k, set_barg):
    p1 = RLF.relieving_pressure_kpa(set_barg * 100, "single_non_fire")
    return RLF.gas_area(W, T_C + 273.15, p1, BACKP_KPA, M, k, 1.0, set_g_kpa=set_barg * 100)
def mix_M(n_):
    kg = tot(n_); kmol = sum(v / (mw(*FORM[c]) if c != "H2" else M_H2) for c, v in ST[n_].items()); return kg / kmol
RELIEF_SIZED = {
    "PSV-203": size_gas(EXCESS * S1 + G2, Tdis, M_H2, GAMMA, DESIGN_BARG["loop"]),                        # K-201 blocked discharge: full circulation (zone: PSV-203 sits on the stage-2 gas header)
    "PSV-202": size_gas(LOAD_E202, TC["hot"], mix_M(12), 1.2, DESIGN_BARG["loop"]),                       # loss of E-202 cooling: stream 12
    "PSV-205": size_gas(LOAD_E401, TC["top"], (LOAD_E401 / (((1 + RR) * B["nap"]) / mwp(7) + B["fg"] / mwp(2) + B["lpg2"] / mwp(4))), 1.05, DESIGN_BARG["col"]),   # E-401 cooling lost
}

# ====================================================================================================================
# 2. DRAWING
# ====================================================================================================================
def f0(x): return f"{x:,.0f}"
def pct(x, tot_): return "-" if x <= 0 else f"{100 * x / tot_:.1f}"
def lab(s, x, y, t, size=9.5, anchor="start", fill=INK, w=400): T(s, x, y, t, size, w, anchor, fill)
def sig(s, pts, color=BLUE): PL(s, pts, 1.3, color, "5 4", None)
def pump_m(s, cx, cy, r=14, label=None):
    """pump mirrored: suction on the right, discharge up-left"""
    n0 = len(s.p); pump(s, cx, cy, r); seg = s.p[n0:]; del s.p[n0:]
    s.add(f'<g transform="translate({2*cx},0) scale(-1,1)">' + "".join(seg) + "</g>")
    if label: T(s, cx, cy + r + 13, label, 10, 700, "middle")
    return dict(inlet=(cx + r, cy), outlet=(cx - r, cy - r), cx=cx, cy=cy)
def jump(s, x, y, horiz=True):
    pass

K = {}          # key coordinates reused by the scenario sheets


def plant(s, detail=True):
    """draw the whole plant. detail=False hides most instrument bubbles (scenario sheets) but keeps tags, lines and stream diamonds."""
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    Y = 265                                  # main line of the top band
    # ---------------- UCO storage and pretreatment
    t1 = tank(s, 70, 330, 70, 90, "TK-101", "raw UCO (A)")
    p101 = pump(s, 126, 312, 12, None); lab(s, 126, 338, "P-101", 9.5, "middle", INK, 700)
    pipe(s, [(105, 312), (114, 312)], arrow_=False)
    u101 = vvessel(s, 190, 235, 50, 95, None, None)
    lab(s, 190, 215, "U-101", 11, "middle", INK, 700); lab(s, 190, 204, "pretreatment (A)", 9.5, "middle")
    pipe(s, [(p101["outlet"][0], p101["outlet"][1]), (138, 270), (165, 270)], arrow_=True)
    pipe(s, [(190, 344), (190, 372)])                                            # waste
    strm(s, 190, 360, 2); lab(s, 204, 364, "waste to disposal (A)", 9.5)
    strm(s, 138, 286, 1)
    v102 = hvessel(s, 290, 270, 58, 44, "V-102", "feed drum")
    pipe(s, [(215, 270), (v102["left"][0], 270)])
    strm(s, 237, 244, 3)
    p201 = pump(s, 340, 335, 14, None); lab(s, 340, 364, "P-201A/B", 10, "middle", INK, 700)
    pipe(s, [(290, v102["bottom"][1]), (290, 335), (326, 335)], arrow_=False)
    pipe(s, [(p201["outlet"][0], p201["outlet"][1]), (354, Y), (405, Y)])
    ctrlvalve(s, 372, Y); valve(s, 392, Y, 0, "ball", True, RED)
    lab(s, 400, 236, "XV-201", 9.5, "start", RED, 700)
    e201 = hx(s, 440, Y, 70, 28, "E-201", "feed heater")
    # H2 header joins the feed line before E-201
    pipe(s, [(375, 118), (375, Y)], arrow_=False)
    # ---------------- stage 1
    r201 = vvessel(s, 560, 185, 60, 150, None, None, packing=False)
    for yy in (205, 270):
        s.add(f'<rect x="533" y="{yy}" width="54" height="42" fill="url(#hatch)" opacity=".55" stroke="#b26a00" stroke-width="0.8"/>')
    T(s, 594, 182, "R-201", 11, 700, "start")
    lab(s, 560, 258, "bed 1", 8.5, "middle", AMBER); lab(s, 560, 323, "bed 2", 8.5, "middle", AMBER)
    pipe(s, [(475, Y), (500, Y), (500, 160), (560, 160), (560, r201["top"][1])])
    lab(s, 450, 160, "L103 feed + H2", 9, "end")
    strm(s, 520, 160, 5)
    # quench
    pipe(s, [(520, 408), (520, 247), (530, 247)], arrow_=True)
    ctrlvalve(s, 520, 300, -90)
    pipe(s, [(500, 408), (500, Y + 20)], arrow_=True)
    strm(s, 520, 330, 6); strm(s, 500, 360, 4)
    # effluent to hot separator
    pipe(s, [(560, r201["bottom"][1]), (560, 395 - 5 - 8), (650, 382), (650, 250), (673, 250)])
    strm(s, 588, 382, 9)
    v201 = vvessel(s, 700, 185, 54, 130, None, None)
    T(s, 732, 330, "V-201", 11, 700, "start"); T(s, 732, 342, "hot separator", 9.5, 400, "start"); strm(s, 700, 350, 10)
    # vapour: EDV riser and E-202
    pipe(s, [(700, v201["top"][1]), (700, 150), (765, 150)])
    strm(s, 735, 150, 12)
    e202 = hx(s, 800, 150, 70, 28, "E-202", "air cooler")
    pipe(s, [(835, 150), (855, 150), (855, 215), (871, 215)])
    v202 = hvessel(s, 935, 215, 100, 46, None, None)
    T(s, 935, 214, "V-202", 11, 700, "middle"); T(s, 935, 227, "cold sep/KO", 9.5, 400, "middle")
    
    # sour water
    pipe(s, [(935, 238), (935, 292)]); valve(s, 935, 268, 90, "gate"); strm(s, 960, 268, 14)
    lab(s, 942, 290, "sour water", 9.5, "start")
    # V-202 hydrocarbon condensate (stream 25): paraffin carried over by V-201 vapour, returned by P-203A/B to the P-202 discharge header
    pipe(s, [(905, 238), (905, 422)], arrow_=False); ctrlvalve(s, 905, 296, 90)
    strm(s, 905, 360, 25)
    p203 = pump_m(s, 891, 422, 14, None); lab(s, 891, 452, "P-203A/B", 10, "middle", INK, 700)
    pipe(s, [(877, 408), (754, 408)], arrow_=False); arrow(s, 790, 408, "l", INK, 9)
    # gas to G-201 and K-201
    pipe(s, [(935, 192), (935, 176), (968, 176)])
    strm(s, 950, 160, 13)
    R(s, 968, 160, 70, 55, "#f3f3f3", INK, 1.6); T(s, 1003, 184, "G-201", 11, 700, "middle"); T(s, 1003, 197, "gas treat (A)", 9, 400, "middle"); T(s, 1003, 208, "stub", 9, 400, "middle")
    pipe(s, [(1003, 160), (1003, 100)]); strm(s, 1003, 125, 15)
    lab(s, 1020, 132, "off-gas to", 9); lab(s, 1020, 143, "fuel gas/flare", 9)
    pipe(s, [(1003, 215), (1003, Y), (1043, Y)]); strm(s, 1003, 240, 16)
    k201 = compressor(s, 1060, Y, 17, None); lab(s, 1060, Y - 36, "K-201", 10, "middle", INK, 700); lab(s, 1060, Y - 25, "recycle comp.", 9, "middle")
    pipe(s, [(1077, Y), (1095, Y), (1095, 118), (375, 118)], arrow_=False)
    arrow(s, 377, 118, "l", INK, 9)
    strm(s, 1095, 200, 8)
    pipe(s, [(1095, Y), (1095, 470)], arrow_=False); PL(s, [(1095, 425), (1112, 425)], 2.6, GREY, "10 5")
    strm(s, 1095, 350, 17)
    valve(s, 450, 118, 0, "ball", True, RED); lab(s, 450, 108, "XV-202", 9.5, "middle", RED, 700)
    # H2 unit stub and make-up
    R(s, 965, 340, 110, 64, "#f3f3f3", INK, 1.6, "6 3")
    T(s, 1020, 360, "H2 UNIT", 11, 700, "middle"); T(s, 1020, 374, "stub (SMR or", 9, 400, "middle"); T(s, 1020, 386, "electrolyser, A)", 9, 400, "middle")
    pipe(s, [(1003, 340), (1003, Y)], arrow_=False); strm(s, 1003, 322, 7)
    arrow(s, 1003, Y + 8, "u", INK, 9)
    # ---------------- flare headers
    PL(s, [(560, 100), (1112, 100)], 4, GREY, "10 5"); lab(s, 570, 96, "FH-1 flare header (A)", 9.5, "start", GREY, 700)
    PL(s, [(1112, 100), (1112, 720)], 4, GREY, "10 5")
    lab(s, 1108, 455, "flare header", 9.5, "end", GREY)
    # PSV-201 on R-201
    pipe(s, [(590, 231), (615, 231)], arrow_=False); psv(s, 615, 215, INK); pipe(s, [(633, 215), (650, 215), (650, 100)], arrow_=False, color=GREY)
    lab(s, 640, 250, "PSV-201", 9.5, "end", INK, 700)
    # PSV-202 on V-202
    pipe(s, [(905, 200), (905, 176)], arrow_=False); psv(s, 905, 155, INK); pipe(s, [(923, 155), (935, 155)], arrow_=False, color=GREY)
    pipe(s, [(935, 155), (935, 100)], arrow_=False, color=GREY)
    lab(s, 898, 150, "PSV-202", 9.5, "end", INK, 700)
    # PSV-204 on V-201 (hot separator): fire, blocked liquid outlet; to FH-1
    pipe(s, [(727, 281), (760, 281)], arrow_=False); psv(s, 760, 265, INK); pipe(s, [(778, 265), (845, 265), (845, 100)], arrow_=False, color=GREY)
    lab(s, 790, 258, "PSV-204", 9.5, "start", INK, 700)
    # PSV-207 on V-102 (feed drum) to a safe location (A)
    pipe(s, [(290, 248), (290, 231)], arrow_=False); psv(s, 290, 215, INK); pipe(s, [(308, 215), (325, 215), (325, 192)], arrow_=True)
    lab(s, 278, 222, "PSV-207", 9.5, "end", INK, 700); lab(s, 325, 184, "to safe location (A)", 9.5, "middle")
    # EDV
    pipe(s, [(700, 150), (700, 100)], arrow_=False, color=GREY); valve(s, 700, 125, 0, "ball", True, RED); lab(s, 710, 128, "HV-201 EDV", 9.5, "start", RED, 700)
    # hot liquid pump and recycle / net split
    pipe(s, [(700, v201["bottom"][1]), (700, 380), (726, 380)], arrow_=False)
    p202 = pump(s, 740, 380, 14, None); lab(s, 764, 384, "P-202A/B", 10, "start", INK, 700)
    pipe(s, [(754, 366), (754, 408), (675, 408)], arrow_=False)
    arrow(s, 677, 408, "l", INK, 9)
    e203 = hx(s, 640, 408, 70, 28, "E-203", "recycle cooler")
    pipe(s, [(605, 408), (520, 408)], arrow_=False)
    # ---------------- stage 2
    pipe(s, [(754, 408), (754, 470)], arrow_=False)
    strm(s, 780, 424, 11)
    pipe(s, [(1095, 470), (865, 470)], arrow_=False)
    pipe(s, [(754, 470), (795, 470)], arrow_=False)
    e301 = hx(s, 830, 470, 70, 28, "E-301", "feed trim (A)")
    pipe(s, [(865, 470), (980, 470), (980, 484)])
    r301 = vvessel(s, 980, 500, 56, 110, None, None)
    for yy in (515, 560):
        s.add(f'<rect x="954" y="{yy}" width="52" height="30" fill="url(#hatch)" opacity=".55" stroke="#b26a00" stroke-width="0.8"/>')
    T(s, 1030, 570, "R-301", 11, 700, "start"); T(s, 1030, 583, "isomerisation /", 9.5, 400, "start"); T(s, 1030, 595, "cracking", 9.5, 400, "start")
    pipe(s, [(980, r301["bottom"][1]), (980, 626), (915, 626)])
    strm(s, 950, 626, 18)
    e302 = hx(s, 880, 626, 70, 28, "E-302", "effluent cooler")
    pipe(s, [(845, 626), (815, 626)])
    v301 = hvessel(s, 770, 626, 64, 44, "V-301", "separator")
    pipe(s, [(770, 604), (770, 585)], arrow_=False); arrow(s, 770, 585, "u", INK, 9)
    lab(s, 762, 580, "H2 to K-201 suction", 9.5, "end"); strm(s, 770, 565, 19)
    # PSV-203 on R-301
    pipe(s, [(1008, 530), (1040, 530)], arrow_=False); psv(s, 1040, 514, INK); pipe(s, [(1058, 514), (1112, 514)], arrow_=False, color=GREY)
    lab(s, 1060, 540, "PSV-203", 9.5, "start", INK, 700)
    # fractionator feed
    pipe(s, [(770, v301["bottom"][1]), (770, 690), (714, 690)], arrow_=False)
    strm(s, 742, 690, 20)
    p401 = pump_m(s, 700, 690, 14, None); lab(s, 700, 718, "P-401A/B", 10, "middle", INK, 700)
    pipe(s, [(686, 676), (686, 655), (670, 655)], arrow_=False)
    e403 = hx(s, 640, 655, 60, 26, "E-403", "feed heater")
    pipe(s, [(610, 655), (590, 655), (590, 570), (532, 570)])
    c401 = vvessel(s, 500, 440, 64, 200, None, None, trays=8)
    T(s, 500, 683, "C-401", 11, 700, "middle"); T(s, 500, 696, "fractionator", 9.5, 400, "middle")
    # overhead
    pipe(s, [(500, c401["top"][1]), (500, 405), (455, 405)], arrow_=False)
    e401 = hx(s, 420, 405, 70, 28, "E-401", "condenser")
    pipe(s, [(385, 405), (367, 405)], arrow_=False)
    v401 = hvessel(s, 325, 405, 60, 40, "V-401", "reflux drum")
    pipe(s, [(283, 405), (232, 405)]); strm(s, 258, 405, 21)
    lab(s, 232, 394, "light ends to fuel", 9.5, "end"); lab(s, 232, 424, "gas / flare (A)", 9.5, "end")
    pipe(s, [(325, 425), (325, 470), (336, 470)], arrow_=False)
    p402 = pump(s, 350, 470, 14, None); lab(s, 350, 498, "P-402A/B", 10, "middle", INK, 700)
    pipe(s, [(364, 456), (400, 456), (468, 456)])       # reflux
    lab(s, 440, 448, "reflux", 9.5, "middle")
    pipe(s, [(364, 456), (364, 470)], arrow_=False)
    pipe(s, [(364, 470), (90, 470), (90, 682)])          # naphtha
    strm(s, 250, 470, 22)
    # SAF side draw
    pipe(s, [(468, 510), (200, 510), (200, 682)]); strm(s, 300, 510, 23)
    hx(s, 400, 510, 56, 24, "E-405", "SAF cooler")
    # reboiler loop and RD
    pipe(s, [(500, c401["bottom"][1]), (500, 672), (430, 672), (430, 624)], arrow_=False)
    hx_ = hx(s, 430, 610, 56, 26, None, None); lab(s, 396, 606, "E-402", 10, "end", INK, 700); lab(s, 396, 618, "reboiler", 9, "end")
    pipe(s, [(430, 597), (430, 580), (468, 580)], arrow_=False)
    pipe(s, [(470, 672), (470, 690), (310, 690), (310, 682)]); strm(s, 334, 690, 24)
    valve(s, 450, 690, 0, "ball", True, RED); lab(s, 450, 722, "XV-401", 9.5, "middle", RED, 700)   # bottoms shutdown valve named in scenario S4 (added after lint: tag was on sheet 4 but not on sheet 1)
    hx(s, 390, 690, 56, 24, "E-404", "RD cooler")
    # PSV-205 on C-401
    pipe(s, [(532, 456), (560, 456)], arrow_=False); psv(s, 560, 440, INK); pipe(s, [(578, 440), (1112, 440)], arrow_=False, color=GREY)
    lab(s, 584, 457, "PSV-205", 9.5, "start", INK, 700)
    # tanks
    tank(s, 90, 745, 70, 56, "TK-403", "naphtha (A)", "cone", .5)
    tank(s, 200, 745, 70, 56, "TK-401", "SAF (A)", "cone", .5)
    tank(s, 310, 745, 70, 56, "TK-402", "RD (A)", "cone", .5)
    lab(s, 90, 770, "", 9)
    for cx_, nm_ in ((90, "403"), (200, "401"), (310, "402")):       # PVRV on the roof (left side), LAHH-4xx independent high-high level (right)
        PL(s, [(cx_ - 20, 684), (cx_ - 20, 670)], 2.0); s.add(f'<circle cx="{cx_-20}" cy="665" r="5" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
        lab(s, cx_ - 12, 656, "PVRV-" + nm_, 9, "end", INK, 700)
    PL(s, [(88, 236), (88, 224)], 2.0); s.add(f'<circle cx="88" cy="219" r="5" fill="#fff" stroke="{INK}" stroke-width="1.6"/>'); lab(s, 88, 209, "PVRV-101", 9, "middle", INK, 700)
    # rundown cooler E-404 (RD) is now drawn on the RD line
    # flare KOD and stack
    v501 = hvessel(s, 1040, 700, 80, 38, "V-501", "flare KOD")
    pipe(s, [(1112, 700), (1040 + 40 + 11, 700)], arrow_=False, color=GREY)
    pipe(s, [(1040 - 40 - 11, 700), (940, 700), (940, 745)], arrow_=False, color=GREY)
    flare(s, 940, 745, 60, ""); lab(s, 940, 764, "FL-501 flare", 10, "middle", INK, 700)
    # utilities stubs
    lab(s, 30, 108, "UTILITIES (stubs, A): hot oil, cooling water/air, N2, instrument air, power.", 9.5, "start", GREY)
    lab(s, 30, 122, "ESD-201 (A): closes XV-201, XV-202, XV-402; opens HV-201, HV-301;", 9.5, "start", RED, 700); lab(s, 30, 134, "trips K-201, P-201, heaters. ESD-401: XV-401, 402, 403; trips P-401/402.", 9.5, "start", RED, 700)
    K.update(dict(r201=r201, v201=v201, v202=v202, k201=(1060, Y), r301=r301, c401=c401, v401=v401, e202=(800, 150), e401=(420, 405), p202=(740, 380), psv201=(633, 215),
                  psv202=(923, 155), psv203=(1058, 514), psv205=(578, 440), hv201=(700, 125), xv201=(392, Y), xv202=(450, 118), reb=(430, 610), tkrd=(310, 745),
                  loop=(1095, 300), bottom=(500, 658)))
    if not detail: return
    # ---------------- instruments (sheet 1)
    # V-102 level
    bubble(s, 262, 330, "LIC", "102", True); sig(s, [(262, 315), (290, 292)])
    sig(s, [(247, 330), (232, 330), (232, 285)]); valve(s, 232, 270, 0, "gate", True)
    # FIC-201
    bubble(s, 372, Y - 40, "FIC", "201", True); sig(s, [(372, Y - 25), (372, Y - 15)])
    # TIC-201 hot oil
    bubble(s, 440, Y - 50, "TIC", "201", True); sig(s, [(440, Y - 35), (440, Y - 15)])
    # R-201 temperature
    bubble(s, 620, 300, "TAHH", "211", True); sig(s, [(605, 300), (590, 290)])
    bubble(s, 462, 335, "TIC", "212", True); sig(s, [(477, 332), (503, 303)])
    bubble(s, 470, 372, "FIC", "202", True); sig(s, [(485, 372), (498, 368)])
    bubble(s, 445, 180, "BE", "201", True, RED)
    # V-201 level
    bubble(s, 765, 235, "LIC", "201", True); sig(s, [(750, 235), (727, 235)])
    # V-202
    bubble(s, 868, 272, "LIC", "202", True); sig(s, [(883, 268), (895, 244)]); sig(s, [(883, 280), (897, 296)])
    bubble(s, 790, 305, "LALL", "201", True, RED); sig(s, [(775, 305), (727, 305)], RED)
    bubble(s, 835, 305, "LAHH", "202", True, RED); sig(s, [(842, 290), (862, 232)], RED)
    bubble(s, 868, 118, "PAHH", "202", True, RED); sig(s, [(865, 133), (857, 148)], RED)
    bubble(s, 870, 176, "PIC", "201", True); sig(s, [(870, 191), (885, 205)])
    # K-201 FAL and make-up valve
    bubble(s, 1060, 300, "FAL", "203", True); sig(s, [(1060, 285), (1060, Y + 17)])
    bubble(s, 935, 340, "AT", "201A", True, RED)
    ctrlvalve(s, 1003, 296, 90); lab(s, 990, 300, "PV-201", 9.5, "end")
    # R-301
    bubble(s, 1040, 480, "TAHH", "311", True); sig(s, [(1040, 495), (1008, 520)])
    # fire and gas (AT = H2 gas detector, BE = flame detector)
    bubble(s, 1070, 650, "AT", "301", True, RED)
    bubble(s, 615, 125, "AT", "201B", True, RED)
    bubble(s, 620, 520, "AT", "401", True, RED); bubble(s, 620, 475, "BE", "401", True, RED)
    bubble(s, 830, 665, "LALL", "301", True, RED); sig(s, [(818, 655), (800, 642)], RED)
    valve(s, 770, 668, 90, "ball", True, RED); lab(s, 775, 708, "XV-403", 9.5, "middle", RED, 700)
    for x, n_ in ((90, "403"), (200, "401"), (310, "402")): bubble(s, x - 50, 705, "LAHH", n_, True, RED)
    # HV-301: second emergency depressuring valve on the HP gas header (stage-2 branch), to FH-1
    valve(s, 1103, 425, 0, "ball", True, RED); lab(s, 1088, 423, "HV-301 EDV", 9.5, "end", RED, 700)
    # XV-402: hot-oil supply to E-402 / E-403 (stub)
    pipe(s, [(262, 610), (340, 610)], arrow_=True, color=GREY); valve(s, 300, 610, 0, "ball", True, RED); lab(s, 300, 585, "XV-402", 9.5, "middle", RED, 700); lab(s, 300, 640, "hot oil to E-402, E-403 (A)", 9.5, "middle", GREY)
    # bottom band instruments
    bubble(s, 846, 575, "LIC", "301", True); sig(s, [(836, 586), (800, 612)])
    bubble(s, 575, 500, "TIC", "401", True); sig(s, [(560, 500), (532, 490)])
    bubble(s, 280, 440, "LIC", "401", True); sig(s, [(295, 440), (318, 410)])
    # tanks
    for x, n_ in ((90, "403"), (200, "401"), (310, "402")):
        bubble(s, x + 30, 665, "LI", n_, True)
    

def stream_key(s, x, y, width=70):
    return [("1", "raw UCO"), ("2", "pretreat waste"), ("3", "clean UCO"), ("4", "recycle to inlet"), ("5", "R-201 liquid feed"), ("6", "quench liquid"), ("7", "H2 make-up"),
            ("8", "recycle H2 to R-201"), ("9", "R-201 effluent"), ("10", "V-201 liquid"), ("11", "net to stage 2"), ("12", "V-201 vapour"), ("13", "V-202 gas"), ("14", "sour water"),
            ("15", "off-gas"), ("16", "clean H2 return"), ("17", "H2 to R-301"), ("18", "R-301 effluent"), ("19", "H2 from V-301"), ("20", "V-301 liquid"), ("21", "light ends"),
            ("22", "naphtha"), ("23", "SAF"), ("24", "renewable diesel"), ("25", "V-202 HC liquid")]


def wtable(s, x, y, colw, rows, size=10, chars=None, lh=12.5, head=True, pad=5):
    """table with wrapped cells; returns the y below"""
    import textwrap as tw
    chars = chars or [int((w - 8) / (size * 0.53)) for w in colw]
    cells = [[tw.wrap(str(c), chars[j]) or [""] for j, c in enumerate(r)] for r in rows]
    yy = y
    for i, (r, cs) in enumerate(zip(rows, cells)):
        h = max(len(c) for c in cs) * lh + pad
        if head and i == 0: R(s, x, yy, sum(colw), h, "#e8eaf0", "none")
        elif i % 2 == 0: R(s, x, yy, sum(colw), h, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cs):
            for q, t_ in enumerate(c): T(s, cx + 4, yy + 11 + q * lh, t_, size, 700 if (head and i == 0) or j == 0 else 400)
            cx += colw[j]
        yy += h
    R(s, x, y, sum(colw), yy - y, "none", "#9aa", 1)
    return yy


def legend(s, x, y):
    items = [("process line", INK, None), ("ESD output", RED, "6 4"), ("instrument signal", BLUE, "5 4"), ("flare / relief header", GREY, "10 5")]
    for i, (t_, c, d) in enumerate(items):
        PL(s, [(x, y + i * 14), (x + 30, y + i * 14)], 2 if c == INK else 1.6, c, d)
        T(s, x + 36, y + 4 + i * 14, t_, 9.5)
    T(s, x + 180, y + 4, "R = required or named by a free source", 9.5); T(s, x + 180, y + 18, "S = sourced   D = derived   A = assumed", 9.5)
    T(s, x + 180, y + 32, "Diamond = stream number (HMB, sheet 2)", 9.5)


PROJ = "SAF by HEFA from UCO, 30,000 t/yr, jet-mode slate"
def newsheet(no, title, sub, basis):
    s = SheetB(no, title, sub, code="VS-SAF", project=PROJ, basis=basis); frame(s, NSHEETS); return s
def bul(s, x, yy, items, width=70, size=10.3, lh=13.2, gap=3):
    for t_ in items: yy = WRAP(s, x, yy, t_, width, size, lh, bullet=True) + gap
    return yy
def tags_ok(): return True

PSVD = {k: v for k, v in RELIEF_SIZED.items()}
def rs(k): v = PSVD[k]; return f"{v.required_area_mm2:,.0f} mm2, API 526 orifice {v.orifice}, {v.n_valves} valve ({v.regime} flow)"


def sheet_pid():
    s = newsheet(1, "P&ID Rev B: SAF by HEFA from UCO, 30,000 t/yr feed (about 100 TPD), jet-mode slate", "P&ID, whole process", "NREL slate (S); balance in code")
    plant(s, True)
    panel_box(s, 1135, 84, 445, 866)
    y = section(s, 1135, 84, 445, "PROCESS IN BRIEF"); yy = y + 16
    yy = bul(s, 1141, yy, ("S: DPR template steps: UCO pretreatment, hydrotreating with H2, isomerisation / cracking, fractionation into SAF, renewable diesel (RD) and naphtha; H2 supply unit (section 4). Feed 30,000 t/yr UCO (S).",
        f"Rev B slate (S, NREL TP-5100-87803 Table G-1, jet mode): SAF {SAF_TYR:,.0f} t/yr, RD {SLATE_YR['RD']:,.0f}, naphtha {SLATE_YR['naphtha']:,.0f}, LPG {SLATE_YR['LPG (propane + C4)']:,.0f}, fuel gas {SLATE_YR['fuel gas']:,.0f}. The DPR's 24,000 t/yr SAF is not credible at 30,000 t/yr feed (needs about {FEED_FOR_24K:,.0f} t/yr UCO).",
        f"D: stage 1 (R-201) releases {Q1_KW:,.0f} kW ({Q1/1000:.2f} MJ/kg), so liquid recycle is {R_TOT:.1f} kg/kg fresh feed (Rev A 1.5). V-201 vapour carries {FROZEN['PHI']*100:.0f} % of the paraffin; V-202 returns it (stream 25, P-203A/B). Stage 2 (R-301) rises {DT_R2_ADIAB:.0f} K (D).",
        f"A: one recycle-gas loop (K-201); H2 {B['h2_tot']*24/1000:.1f} t/d. Hot hydrocarbon plus hydrogen at 50 bar is the dominant hazard: sheets 4 to 8."), 70, 10.3, 13.2)
    y = section(s, 1135, yy + 4, 445, "SAFETY DEVICES ON THIS SHEET (details: sheets 6 to 8)"); yy = y + 16
    yy = bul(s, 1141, yy, ("Relief (A, all to FH-1 > V-501 > FL-501 unless stated): PSV-201 R-201, PSV-202 V-202, PSV-203 gas header / R-301, PSV-204 V-201, PSV-205 C-401, PSV-207 V-102 (safe location), PVRV on tanks. V-401, E-202, G-201, V-301 are in a protected zone (sheet 6).",
        "ESD-201: XV-201, XV-202, XV-402 close; EDV HV-201 and HV-301 open; K-201, P-201, heaters trip. ESD-401: XV-401, XV-402, XV-403, P-401/402 trip. Triggers: TAHH-211/311, FAL-203, PAHH-202, LAHH-202, LALL-201, LALL-301, AT/BE detectors.",
        "Hydrogen flames are hard to see: gas (AT) detection supplements flame detection (R, EIGA Doc 15/21). Detector type and voting are open items.",
        "R (DPR): cost lines 'Hydrogen unit and utilities' INR 120.00 cr and 'Effluent, safety & EMP' INR 25.00 cr; contents not described."), 70, 10.3, 13.2)
    y = section(s, 1135, yy + 4, 445, "LEGEND"); legend(s, 1141, y + 16)
    y = section(s, 1135, y + 70, 445, "LINE LIST (size, material, rating: A, to be set)")
    ll = [("Line", "From", "To", "Stream"), ("L101", "TK-101 / P-101", "U-101", "1"), ("L102", "U-101", "V-102, P-201", "3"), ("L103", "P-201 + H2 header", "E-201, R-201", "5, 8"),
          ("L104", "R-201", "V-201", "9"), ("L105", "P-202, P-203, E-203", "R-201 inlet, quench", "4, 6, 25"), ("L106", "P-202 + H2", "E-301, R-301", "11, 17"),
          ("L107", "V-201 vapour", "E-202, V-202, G-201", "12, 13"), ("L107B", "G-201, V-301, make-up", "K-201 suction", "16, 19, 7"), ("L108", "R-301, V-301", "E-403, C-401", "18, 20"),
          ("L109", "C-401, V-401", "TK-401/402/403", "21 to 24"), ("FH-1/2", "PSVs, HV-201, HV-301", "V-501, FL-501", "relief")]
    table(s, 1135, y + 3, (60, 145, 160, 80), ll, 17, 10, bold_first_col=True)
    y = section(s, 20, 784, 1100, "MAJOR EQUIPMENT (conceptual; sizes and ratings not set, A). Note column: relief / protection (sheet 6)")
    left = [("Tag", "Service", "Note"), ("TK-101", "Raw UCO storage", "PVRV-101"), ("U-101", "UCO pretreatment", "atmospheric vent (A)"), ("V-102", "Clean UCO feed drum", "PSV-207, LIC-102"),
            ("P-101, P-201A/B", "UCO transfer, feed pumps", "to loop pressure"), ("E-201", "Feed heater", "hot oil, TSV at detail design"), ("R-201", "Hydrotreater", "PSV-201, TAHH-211, 2 beds"),
            ("V-201", "Hot separator", "PSV-204, LALL-201, HV-201"), ("P-202A/B, P-203A/B", "Hot liquid pump, condensate return", "recycle + net; stream 25"), ("E-203", "Recycle trim cooler", "TSV at detail design"),
            ("E-202", "Effluent air cooler", "zone V-201/V-202"), ("V-202", "Cold separator, 3 phase", "PSV-202, PAHH/LAHH-202"), ("G-201", "Gas treat stub", "zone V-202")]
    right = [("Tag", "Service", "Note"), ("K-201", "Recycle gas compressor", "PSV-203 (header), FAL-203"), ("H2 unit", "Hydrogen supply", "DPR cost line, scope A"),
             ("E-301", "Stage 2 feed trim", "cooler 39 kW; start-up heater"), ("R-301", "Isomerisation / cracking", "PSV-203, TAHH-311, HV-301"), ("E-302, V-301", "Cooler, separator", "LALL-301, XV-403"),
             ("E-403, P-401A/B", "Column feed heater, pump", "hot oil XV-402"), ("C-401", "Fractionator", "PSV-205, side draw SAF"), ("E-401, V-401, P-402A/B", "Condenser, reflux drum, pumps", "zone C-401"),
             ("E-402", "Reboiler", "hot oil XV-402"), ("E-404, E-405", "RD cooler, SAF cooler", "rundown"), ("TK-401/402/403", "SAF / RD / naphtha", "PVRV, LAHH, bund (A)"), ("V-501, FL-501", "Flare KOD, flare", "no PSV: open to stack")]
    table(s, 20, y + 4, (130, 215, 215), left, 17, 10, bold_first_col=True)
    table(s, 580, y + 4, (150, 190, 200), right, 17, 10, bold_first_col=True)
    lab(s, 22, y + 4 + 17 * 13 + 14, "Lines: L101 raw UCO, L102 clean UCO, L103 feed + H2, L104 effluent, L105 recycle, L106 net liquid, L107 gas loop, L108 fractionator feed, L109 products. Stream 25 joins the P-202 discharge header.", 9.5, "start", GREY)
    return s


def sheet_hmb():
    s = newsheet(2, "HEAT AND MATERIAL BALANCE Rev B (computed): SAF by HEFA, 30,000 t/yr feed", "Heat and material balance", "NREL slate (S); balance computed in code; frozen PR flash outputs")
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    TTd = {1: TC["uco"], 2: TC["pre"], 3: TC["pre"], 4: round(T_REC), 5: TC["in1"], 6: round(T_REC), 7: 40, 8: round(Tdis), 9: round(TC["in1"] + DT_R1), 10: TC["hot"], 11: round(T_MIXD), 12: TC["hot"], 13: TC["cold"],
           14: TC["cold"], 15: TC["cold"], 16: TC["cold"], 17: round(Tdis), 18: TC["out2"], 19: TC["cold2"], 20: TC["cold2"], 21: 40, 22: 40, 23: TC["tank"], 24: TC["tank"], 25: TC["cold"]}
    PP = {1: 1.5, 2: 1.5, 3: P_BAR["drum"], 4: 52, 5: 52, 6: 52, 7: P_BAR["kin"], 8: P_BAR["kout"], 9: P_BAR["r1"], 10: P_BAR["v201"], 11: P_BAR["v201"], 12: P_BAR["v201"], 13: P_BAR["v202"], 14: P_BAR["v202"],
          15: 5, 16: P_BAR["kin"], 17: P_BAR["kout"], 18: P_BAR["r2"], 19: P_BAR["v301"], 20: P_BAR["v301"], 21: 1.3, 22: 1.3, 23: P_BAR["tank"], 24: P_BAR["tank"], 25: P_BAR["v202"]}
    PH = {1: "L", 2: "L", 3: "L", 4: "L", 5: "L+V", 6: "L", 7: "V", 8: "V", 9: "L+V", 10: "L", 11: "L", 12: "V", 13: "V", 14: "L", 15: "V", 16: "V", 17: "V", 18: "L+V", 19: "V", 20: "L", 21: "V", 22: "L", 23: "L", 24: "L", 25: "L"}
    def table_for(ns, y, title):
        rows = [("Total flow (kg/h)", [f0(tot(n)) for n in ns]), ("Temperature (C)", [str(TTd[n]) for n in ns]), ("Pressure (bar abs)", [f"{PP[n]:g}" for n in ns]), ("Phase", [PH[n] for n in ns]), ("Composition (mass %)", None)]
        for c in COMPS:
            if any(ST[n].get(c, 0) > 0 for n in ns): rows.append((c, [pct(ST[n].get(c, 0), tot(n)) for n in ns]))
        return hmb_table(s, 20, y, ns, rows, 150, 72, 15, 9.5, title, 1100)
    y = table_for(list(range(1, 14)), 88, "STREAMS 1 TO 13 (stage 1, separation, gas loop)  |  T, P: A; flows D; stream 12 includes the paraffin carry-over (PR flash, frozen)")
    y = table_for(list(range(14, 26)), y + 5, "STREAMS 14 TO 25 (gas loop, stage 2, fractionation, products, V-202 hydrocarbon liquid)")
    y += 5
    y = section(s, 20, y, 1100, f"DUTIES (kW). D: m cp dT with cp {CP_L} hot / {CP_L_FEED} feed / {CP_L_COOL} cool kJ/kg/K (CoolProp, S); E-401/402/403 and the E-202 condensing term from frozen PR flashes")
    d = DUTY
    items = [("E-201", d["E-201"]), ("R-201 heat", d["R-201 heat release"]), ("E-203", d["E-203"]), ("E-202", d["E-202"]), ("E-301 cool", d["E-301 (cooling)"]), ("R-301 heat", d["R-301 heat release"]),
             ("E-302", d["E-302"]), ("E-403", d["E-403"]), ("E-401", d["E-401"]), ("E-402", d["E-402"]), ("E-404", d["E-404"]), ("E-405", d["E-405"]), ("K-201", d["K-201 shaft"])]
    cw = 1100 / len(items)
    for i, (n_, v) in enumerate(items):
        R(s, 20 + i * cw, y, cw, 34, "#f6f7fa" if i % 2 == 0 else "#fff", "#cfd")
        T(s, 20 + i * cw + cw / 2, y + 13, n_, 9.5, 700, "middle"); T(s, 20 + i * cw + cw / 2, y + 28, f0(v), 10.5, 400, "middle")
    y += 38
    s.add(f'<rect x="20" y="{y}" width="1100" height="44" fill="#e8f5e9" stroke="{GREEN}" stroke-width="1.4"/>')
    T(s, 28, y + 16, f"Closure (mass): in {f0(M_IN)} kg/h (raw UCO + H2), out {f0(M_OUT)} kg/h, error {ERR_MASS:.3f} %.  Feed {tot(1)*T_YR:,.0f} t/yr; SAF {SAF_TYR:,.0f} t/yr (D from NREL slate).  Every node closes (worst {max(NODE_ERR.values()):.3f} %).", 11, 700, fill=GREEN)
    T(s, 28, y + 33, f"Element check (kg/h in, out, error): C {f0(E_IN[0])}, {f0(E_OUT[0])}, {ERR_EL[0]:.3f} %   H {f0(E_IN[1])}, {f0(E_OUT[1])}, {ERR_EL[1]:.3f} %   O {f0(E_IN[2])}, {f0(E_OUT[2])}, {ERR_EL[2]:.3f} %   |   stage-2 H2 from C-C scissions = H balance (asserted)", 10.5, 400, fill=GREEN)
    panel_box(s, 1135, 84, 445, 866)
    y = section(s, 1135, 84, 445, "HOW THE BALANCE IS BUILT (D)"); yy = y + 16
    yy = bul(s, 1141, yy, (f"Stage 1 (A chain mix C16:0 15, C18:0 5, C18:1 45, C18:2 35 mol %; HDO 85, DCO2 8, DCO 7 %): H2 {B['nH2']:.2f} and water {B['nH2O']:.2f} mol per chain; propane, water, CO2, CO and hydrotreated paraffin follow (asserted).",
        "Stage 2: the NREL kerosene, diesel, naphtha, LPG and fuel-gas shares (S) fix the hydrocarbon pool; its size follows from carbon closure, hydrogen from the H balance. Carbon numbers C11, C16, C7, C4, C2 are A.",
        f"Heat: Q = {Q1:,.0f} kJ/kg UCO from heats of formation (two triglyceride routes {Q1_ROUTES['fa']:,.0f} and {Q1_ROUTES['db']:,.0f}, S tool values, +/-10 %). Recycle R = (Q/dT - gas)/cp - 1 = {R_TOT:.2f} for a {DT_R1:.0f} K bed rise (A target in the 300-350 C window).",
        f"Stage 2: Q = {abs(HF_ALK_A):.1f} kJ per scission (= per mol H2) = {Q2_KW:.0f} kW; outlet {T_OUT2:.0f} C, inside NREL 299-343 C; isomerisation heat neglected (A).",
        f"V-201 (PR, kij 0, screening): {FROZEN['PHI']*100:.1f} % of the paraffin leaves as vapour; condensed in E-202 and returned from V-202 by P-203 (stream 25). Water/H2 solubility not reliable in this EOS.",
        f"C-401 feed at {TC['feed_c']} C, 1.5 bar is {FROZEN['VF_FEED']*100:.0f} mol % vapour; E-403 {d['E-403']:.0f} kW; reboiler from the column energy balance {d['E-402']:.0f} kW. At 250 C the feed is 100 % vapour and the reboiler duty would be negative (-118 kW).",
        f"H2 use {B['h2_tot']:.0f} kg/h = {B['h2_tot']*24/1000:.2f} t/d ({H2_PCT_OIL:.2f} wt % of clean oil; NREL 4.5): stage 1 {S1:.0f}, stage 2 {S2:.0f} kg/h. Per t SAF {H2_RATIO_SAF:.0f} kg."), 70, 10, 12.8, 3)
    y = section(s, 1135, yy + 2, 445, "STREAM KEY"); yy = y + 14
    for i, (n_, t_) in enumerate(stream_key(s, 0, 0)): T(s, 1141 + (i // 13) * 222, yy + (i % 13) * 13, f"{n_}  {t_}", 9.5)
    yy += 13 * 13 + 6
    y = section(s, 1135, yy, 445, "SOURCED (S)"); yy = y + 14
    bul(s, 1141, yy, ("DPR template: feed 30,000 t/yr UCO (sections 1, 9); steps (section 4); cost lines (section 7). NREL/TP-5100-87803 Table G-1 (p.118) slate; App. D.2 (p.103) 300-350 C deoxygenation and 299-343 C isomerisation windows. CoolProp cp, latent heat, bubble/dew points; chemicals Hf values (frozen, tests/crosscheck/saf_revb_thermo.py).",
        "Not sourced: operating days 330 (A), pathway shares (A), all T/P ladder values (A), gas circulation 3x (A)."), 70, 9.8, 12.5, 3)
    y = section(s, 20, 784, 1100, "Rev A TO Rev B CHANGES (item | Rev A | Rev B | source | effect on closure and duties)")
    ch = [("Item", "Rev A", "Rev B", "Source", "Effect on closure / duties"),
          ("SAF / slate", "SAF 24,000 t/yr (S template); RD+naph 891", f"SAF {SAF_TYR:,.0f}; RD {SLATE_YR['RD']:,.0f}; naph {SLATE_YR['naphtha']:,.0f}", "NREL Table G-1; IEA T39, IATA, Tao", "closure kept (0.000 %); 80 % to 45 % of oil"),
          ("Stage-1 reaction heat", "312 kW (0.30 MJ/kg)", f"{Q1_KW:,.0f} kW ({Q1/1000:.2f} MJ/kg)", "Hf, chemicals; 2 routes", "closes -70 %; sets recycle"),
          ("Recycle ratio / cp", "R 2.5 (1.5 net), cp 2.3", f"R {R_TOT:.1f}, cp {CP_L}", "D from Q; CoolProp", f"recycle flow x{R_TOT/1.5:.1f}; E-203 {d['E-203']:.0f} kW"),
          ("Runaway rises", "64 K / 113 K", f"{DT_NO_QUENCH:.0f} K / {DT_NO_DILUENT:.0f} K", "D (heat/cp incl. gas)", "no-quench / no-diluent"),
          ("V-201 split", "sharp, 0 % paraffin to vapour", f"{FROZEN['PHI']*100:.1f} % carried; stream 25, P-203", "PR flash (screening)", f"E-202 667 to {d['E-202']:.0f} kW"),
          ("C-401 feed, duties", "250 C liquid; E-403 420; E-402 clamped 0", f"{TC['feed_c']} C, 52 mol % vap; E-403 {d['E-403']:.0f}; E-402 {d['E-402']:.0f}", "PR flash, energy balance", "no clamp; E-401 4.7 to 87 kW"),
          ("R-301", "dT 10 K (A), in 350 C", f"dT {DT_R2_ADIAB:.0f} K (D), in {TC['in2']} C, out {TC['out2']} C", "Hf per scission; NREL window", f"R-301 heat {Q2_KW:.0f} kW; E-301 cooler {d['E-301 (cooling)']:.0f}"),
          ("Draw temperatures", "top 120, SAF 210, RD 320 C", "112, 212, 303 C", "CoolProp/PR bubble, dew", "RD 320 C was above its bubble point"),
          ("H2 total", "3.77 wt % oil", f"{H2_PCT_OIL:.2f} wt %", "NREL 4.5 (residual -16 %)", f"per t SAF 46 to {H2_RATIO_SAF:.0f} kg (OIES 55-60 net)")]
    wtable(s, 20, y + 3, (140, 200, 250, 215, 295), ch, 9.5, [27, 40, 50, 41, 58], 11.5, True, 4)
    return s


def sheet_basis():
    s = newsheet(3, "BALANCE BASIS Rev B: slate check against NREL, sensitivity, assumptions", "Balance basis and sensitivity", "NREL TP-5100-87803 Table G-1; IEA Task 39; IATA; Tao 2017")
    raw = B["raw"]
    def p(x): return f"{100*x/raw:.1f}"
    y = section(s, 20, 88, 1100, "A. Rev B vs NREL Table G-1, jet mode (wt % of raw oil; S = NREL value, D = this balance)"); 
    rows = [("Product", "NREL (S)", "Rev B (D)", "Deviation", "Comment"),
            ("Kerosene (SAF)", "46.1", p(B["saf"]), f"{(100*B['saf']/raw-46.1)/46.1*100:+.1f} %", "clean-oil basis (1.5 % waste, A) explains most of the gap"),
            ("Diesel (RD)", "30.4", p(B["rd"]), f"{(100*B['rd']/raw-30.4)/30.4*100:+.1f} %", "same"),
            ("Naphtha", "8.5", p(B["nap"]), f"{(100*B['nap']/raw-8.5)/8.5*100:+.1f} %", "same"),
            ("LPG (stage-1 propane + cracking C4)", "6.0", p(B["prop"] + B["lpg2"]), f"{(100*(B['prop']+B['lpg2'])/raw-6.0)/6.0*100:+.1f} %", "propane is stoichiometric (5.1 % of oil)"),
            ("Fuel gas", "1.5", p(B["fg"]), f"{(100*B['fg']/raw-1.5)/1.5*100:+.1f} %", "same"),
            ("CO + CO2", "4.0", p(B["co"] + B["co2"]), f"{(100*(B['co']+B['co2'])/raw-4.0)/4.0*100:+.0f} %", "unchanged: A pathway shares (HDO 85 %); NREL feed and shares differ. Not tuned to match"),
            ("Aqueous (reaction water)", "8.0", p(B["h2o"]), f"{(100*B['h2o']/raw-8.0)/8.0*100:+.0f} %", "same cause; open item for the licensor"),
            ("H2 in", "4.5", p(B["h2_tot"]), f"{(100*B['h2_tot']/raw-4.5)/4.5*100:+.0f} %", "stage-2 H2 only 0.45 wt %: n-paraffin cracking model; low-confidence residual")]
    y = wtable(s, 20, y + 3, (250, 90, 100, 90, 570), rows, 10.6, None, 13.6, True, 5)
    y = section(s, 20, y + 8, 1100, "B. Slate sensitivity (t/yr) and the 52,000 t/yr UCO alternative")
    S_ = SLATE_NREL
    rows = [("Case", "UCO", "SAF", "RD / diesel", "Naphtha", "LPG + fuel gas", "H2", "Basis"),
            ("Rev A (DPR template)", "30,000", "24,000", "4,500 (template) / 891 computed", "in RD", "189 kg/h propane", "3.77 % oil", "S template; not closable (80 % of oil)"),
            ("Rev B base: NREL jet mode", f"{FEED_T_YR:,.0f}", f"{SAF_TYR:,.0f}", f"{SLATE_YR['RD']:,.0f}", f"{SLATE_YR['naphtha']:,.0f}", f"{SLATE_YR['LPG (propane + C4)']+SLATE_YR['fuel gas']:,.0f}", f"{B['h2_tot']*T_YR:,.0f}", "D, this sheet set"),
            ("NREL jet mode, direct on raw oil", "30,000", f"{FEED_T_YR*S_['kero']/100:,.0f}", f"{FEED_T_YR*S_['diesel']/100:,.0f}", f"{FEED_T_YR*S_['naph']/100:,.0f}", f"{FEED_T_YR*(S_['lpg']+S_['fg'])/100:,.0f}", f"{FEED_T_YR*0.045:,.0f}", "S: Table G-1"),
            ("Diesel (RD) mode, no jet cut", "30,000", "0", f"{FEED_T_YR*NREL_RD['diesel']/100:,.0f}", "incl. in light 2,100", f"{FEED_T_YR*NREL_RD['light']/100:,.0f} (naph + LPG + FG)", f"{FEED_T_YR*NREL_RD['h2_in']/100:,.0f}", "S: Table G-1, RD mode"),
            ("Diesel mode + jet splitter (about 15 % jet)", "30,000", f"{IEA_SAF:,.0f} (15 % of HT paraffin)", "rest", "-", "-", "about 3.3 % oil", "D: IEA Task 39 5.1.4; YIELD_CHECK quotes 4,500 (15 % of oil, IATA)"),
            ("Tao 2017 hydrocracked bound", "30,000", "17,100 to 19,500", "-", "-", "-", "-", "D: 57-65 wt % of oil, upper design bound"),
            ("Hold 24,000 t/yr SAF (this model)", f"{FEED_FOR_24K:,.0f}", f"{B52['saf']*T_YR:,.0f}", f"{B52['rd']*T_YR:,.0f}", f"{B52['nap']*T_YR:,.0f}", f"{(B52['prop']+B52['lpg2']+B52['fg'])*T_YR:,.0f}", f"{B52['h2_tot']*T_YR:,.0f}", f"D; NREL ratio gives 52,060 t/yr; every unit scales x{FEED_FOR_24K/FEED_T_YR:.2f}")]
    y = wtable(s, 20, y + 3, (225, 70, 140, 130, 90, 135, 80, 230), rows, 10.6, None, 13.6, True, 5)
    y = section(s, 20, y + 8, 1100, "C. ASSUMED, to be confirmed by licensor or vendor (A)")
    A = [("330 d/yr, 24 h/d", "not in template"), ("FA mix 15/5/45/35 mol %", "C16:0 / C18:0 / C18:1 / C18:2"), ("HDO 85 / DCO2 8 / DCO 7 %", "pathway shares (drive CO/CO2, water)"), ("Waste 1.5 % of raw UCO", "moisture, gums, earth"),
         ("Carbon numbers kero 11, diesel 16, naph 7, LPG 4, FG 2", "n-paraffin pseudo-cuts"), ("Bed rise target 45 K", "inside 300-350 C window; sets recycle"), ("Quench share 50 % of recycle", ""), ("Gas circulation 3 x H2 use", "pure H2 loop"),
         ("E-201 outlet 275 C", "fouling not assessed"), ("T/P ladder: 300/340/50 C, 50 bar", "stage 2 in 300 C"), ("C-401 feed 210 C, RR 1.0, 1.5 bar", "feed phase from PR flash"), ("gamma 1.41, eta 0.75; H2 cp 14.3", ""),
         ("Design pressure 60 barg loop, 4 barg column", "relief basis, sheet 6"), ("Flare back pressure 350 kPa abs", "relief sizing"), ("PR EOS kij = 0", "screening, water/H2 unreliable"), ("Isomerisation heat neglected", "small")]
    rows = [("Item", "Basis", "Item", "Basis")]
    for i in range(0, len(A), 2): rows.append((A[i][0], A[i][1], A[i + 1][0], A[i + 1][1]))
    wtable(s, 20, y + 3, (330, 220, 330, 220), rows, 10.6, None, 13.6, True, 5)
    panel_box(s, 1135, 84, 445, 866)
    y = section(s, 1135, 84, 445, "REACTION HEAT, RECYCLE AND RUNAWAY (D)"); yy = y + 16
    yy = bul(s, 1141, yy, (f"Rev A derived the 'heat release' from an assumed 45 K rise, giving 0.30 MJ/kg. Rev B uses heats of formation (chemicals Hfg, gas, 25 C, frozen in the generator): {Q1_ROUTES['fa']:,.0f} kJ/kg by the fatty-acid route, {Q1_ROUTES['db']:,.0f} by the database triglyceride; mean {Q1:,.0f} (+/-10 %). Rev A validator range 1.02-1.11 MJ/kg: agrees.",
        f"Recycle: R = (Q/{DT_R1:.0f} - gas {GAS1:.2f})/{CP_L} - 1 = {R_TOT:.2f}. NREL text says liquid recycle up to 1:1 plus interbed H2 quench; at R = 1 the unquenched rise would be {DT_R1_AT_RA1:.0f} K. The two are not reconciled: licensor item.",
        f"Runaway (D, heat per kg over liquid + circulating gas): normal {DT_NORMAL:.0f} K; quench lost {DT_NO_QUENCH:.0f} K; recycle pump lost / no diluent {DT_NO_DILUENT:.0f} K. Rev A showed 64 and 113 K (understated 2.3-2.9 x then).",
        f"R-301: {Q2_KW:.0f} kW, {DT_R2_ADIAB:.0f} K rise, outlet {TC['out2']} C (window top 343). No cold-H2 quench needed in the base case ({Q_QUENCH_REQ:.0f} kg/h); loss of circulation gas would raise the rise to {Q2_KW*3600/(B['mht']*CP_L):.0f} K.",
        "Carry-over (PR): the sharp V-201 split of Rev A was wrong; hydrocarbon in the vapour needs a liquid outlet on V-202 (stream 25).",
        "Residuals not closed: stage-2 H2 (NREL 4.5 vs 3.76 wt % total), CO+CO2 and water (A pathway shares), licensor selectivity, real-fluid VLE of water and H2."), 70, 10.2, 13)
    legend(s, 1141, 860)
    return s


# ---------------- scenario sheets
SC = {
    "S1": ("S1 H2 release and fire, R-201 / K-201 recycle gas", "Flange or seal leak on the recycle gas loop (K-201 discharge, 53 bar, H2).",
           "Hydrogen jet release, ignition gives jet or flash fire; flame hard to see; escalation to R-201 and hot lines.",
           "AT-201A/B, AT-301 H2 detectors; BE-201 flame detector; ESD-201 trips K-201, closes XV-202 and XV-201, opens EDV HV-201 and HV-301 to FH-1 (all A).",
           "Hole size distribution; loop inventory; detector type for H2 flames; not quantified."),
    "S2": ("S2 High-pressure loss of containment, hot hydrocarbon and H2", "Weld or flange failure on the R-201 effluent line (L104, 50 bar, about 345 C).",
           "Hot paraffin plus H2 above its auto-ignition temperature: ignition on release, jet fire, then pool fire; thermal effects on R-201 and supports.",
           "ESD-201 and EDVs; TAHH-211; fire and gas detection; remote isolation XV-201/XV-202; passive fire protection and deluge (A, standard not obtained).",
           "Auto-ignition temperature of the cut (lab); valve closing times; line size; not quantified."),
    "S3": ("S3 R-201 temperature runaway / quench failure", "TIC-212 quench valve fails closed, or P-202 trips, or E-203 blocks.",
           f"Heat release {Q1_KW:,.0f} kW (D, Hf) spread over less liquid. D: bed rise {DT_NORMAL:.0f} K normal; {DT_NO_QUENCH:.0f} K without quench; {DT_NO_DILUENT:.0f} K with no diluent (Rev A: 64 / 113 K).",
           "TAHH-211 trips ESD-201; TIC-212 / FIC-202; PSV-201; EDV HV-201 depressures; XV-201 and XV-202 close (A).",
           "Maximum bed temperature (catalyst, metallurgy, hydrogen attack); licensor heat of reaction; temperature rise rate; runaway relief load: not quantified."),
    "S4": ("S4 Fractionator fire", f"Leak at C-401 bottoms / reboiler loop (about {TC['rd']} C RD) or reflux system ignites.",
           "Hot RD above 300 C; pool or spray fire at C-401, E-402 and P-401.",
           "BE-401 and AT-401; ESD-401 closes XV-401, XV-402, XV-403, trips pumps; deluge and bund (A); PSV-205 for fire case.",
           "Auto-ignition temperature; inventory; fire water demand; bund size; fire-case relief load; not quantified."),
    "S5": ("S5 Flare relief, loss of cooling", "Loss of E-202 fans or cooling water: V-201 vapour is not condensed (similarly E-401).",
           f"Pressure rises in V-202 and the loop until PSV-202 lifts to FH-1. D upper bound: stream 12 = {f0(LOAD_E202)} kg/h; overhead {f0(LOAD_E401)} kg/h (E-401).",
           "PAHH-202 and ESD-201 stop feed; PSV-202 / PSV-205 to FH-1 and KOD V-501; FL-501; K-201 trip (A).",
           "Relief load with hold-up credited; flare capacity, radiation, KOD size, back pressure; not quantified."),
}
def sc_table(s, y, keys):
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown", "Open data needs")] + [SC[k_] for k_ in keys]
    return wtable(s, 20, y, (150, 190, 255, 255, 250), rows, 9.6, [26, 36, 50, 50, 48], 12, True, 6)
def key_box(s, lines):
    R(s, 24, 128, 330, 13.2 * len(lines) + 8, "#fff", RED, 1.3); TL(s, 30, 141, lines, 9.5, 13.2, fill=RED)
def tag_star(s, x, y, n, r=15):
    star(s, x, y, r); T(s, x, y + 4, n, 11, 700, "middle", RED)


def sheet_sc1():
    s = newsheet(4, "SCENARIOS S1 to S3: hydrogen fire, high-pressure release, runaway", "Scenarios 1 to 3", "Qualitative, D runaway estimate (S3)")
    plant(s, False)
    tag_star(s, 1095, 235, "S1"); flame(s, 1088, 224, -35, 60, 30, .9)
    tag_star(s, 560, 375, "S2"); flame(s, 578, 371, 55, 70, 28, .9)
    tag_star(s, 560, 237, "S3", 17)
    key_box(s, ["S1  H2 jet fire at the K-201 discharge flange", "S2  hot paraffin + H2 release, R-201 effluent line", f"S3  R-201 runaway, quench lost (+{DT_NO_QUENCH:.0f} K / +{DT_NO_DILUENT:.0f} K, D)", "Safeguards (A): table below and sheets 6 to 8"])
    panel_box(s, 1135, 84, 445, 866)
    y = section(s, 1135, 84, 445, "S1: HYDROGEN RELEASE AND FIRE"); yy = y + 16
    yy = bul(s, 1141, yy, ("Hydrogen leaks easily, disperses upward and ignites at very low energy; its flame is nearly invisible, so leak (gas or acoustic) detection supplements flame detection (R, EIGA Doc 15/21). Property values are taken from the toolkit property set or a datasheet, not quoted here.",
        "Likely sources: flanges, seals and instrument connections on the 53 bar loop around K-201 and the reactors. The toolkit jet-flame module is built for paraffins, so no hydrogen flame length is given."))
    y = section(s, 1135, yy + 4, 445, "S2: HIGH-PRESSURE RELEASE, AUTO-IGNITION"); yy = y + 16
    yy = bul(s, 1141, yy, ("Reactor effluent is hot paraffin with excess H2 at 50 bar; above its auto-ignition temperature it can ignite without a spark. The value for this cut is a lab item.",
        "High-temperature hydrogen also drives hydrogen attack in steel: material selection is a design item (standard not obtained)."))
    y = section(s, 1135, yy + 4, 445, "S3: RUNAWAY / QUENCH FAILURE (D, Rev B)"); yy = y + 16
    yy = bul(s, 1141, yy, (f"Heat of reaction {Q1:,.0f} kJ/kg UCO from heats of formation (Rev A: 0.30 MJ/kg implied by the assumed 45 K rise). Recycle ratio {R_TOT:.1f} holds the net rise at {DT_R1:.0f} K.",
        f"Rise = heat / (cp x liquid + gas) via process_safety.plant_units.adiabatic_rise_K: quench lost {DT_NO_QUENCH:.0f} K; recycle lost {DT_NO_DILUENT:.0f} K. Whether this is acceptable depends on the maximum bed temperature (not in the source files).",
        "Emergency depressuring through HV-201 / HV-301 cools by expansion but does not stop the reaction: stopping feed (XV-201) and H2 (XV-202) is the first action."))
    legend_y = section(s, 1135, 720, 445, "LEGEND"); legend(s, 1141, legend_y + 16)
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (S1 to S3)"); sc_table(s, y + 3, ["S1", "S2", "S3"])
    return s


def sheet_sc2():
    s = newsheet(5, "SCENARIOS S4 and S5: fractionator fire, flare relief on loss of cooling", "Scenarios 4 and 5", "Qualitative, two D upper-bound relief loads (S5)")
    plant(s, False)
    tag_star(s, 456, 672, "S4", 13); flame(s, 500, 640, 8, 100, 52, .9); flame(s, 470, 650, -10, 70, 36, .6)
    tag_star(s, 842, 133, "S5", 13); tag_star(s, 454, 391, "S5", 12)
    PL(s, [(1112, 100), (1112, 700)], 5, RED, None, None, "none", .35); PL(s, [(940, 700), (940, 745)], 5, RED, None, None, "none", .35)
    key_box(s, ["S4  fire at C-401 bottoms / E-402 loop", f"S5  E-202 cooling lost: {f0(LOAD_E202)} kg/h to PSV-202 (D)", f"S5b E-401 cooling lost: {f0(LOAD_E401)} kg/h to PSV-205 (D)", "Red band: relief path FH-1 > V-501 > FL-501 (A)"])
    panel_box(s, 1135, 84, 445, 866)
    y = section(s, 1135, 84, 445, "S4: FRACTIONATOR FIRE"); yy = y + 16
    yy = bul(s, 1141, yy, (f"Bottoms and reboiler-loop RD is the hottest stage-2 liquid ({TC['rd']} C, its bubble point at 1.5 bar; Rev A used 320 C). A leak can burn as spray or pool fire under C-401 and the pumps.",
        "Safeguards drawn are A: the DPR names an 'Effluent, safety & EMP' line (INR 25.00 cr) and a fire NOC (section 6) but no design. Inventory, auto-ignition temperature, bund and fire-water basis are open."))
    y = section(s, 1135, yy + 4, 445, "S5: FLARE RELIEF, LOSS OF COOLING"); yy = y + 16
    yy = bul(s, 1141, yy, (f"E-202 loss (D): stream 12 = H2 {f0(ST[12]['H2'])} + steam {f0(ST[12]['H2O'])} + CO/CO2/propane {f0(ST[12]['CO']+ST[12]['CO2']+ST[12]['Propane'])} + paraffin {f0(ST[12]['HT paraffin'])} = {f0(LOAD_E202)} kg/h, upper bound (no hold-up credit).",
        f"E-401 loss (D): overhead = (1 + {RR:g}) x naphtha + light ends = {f0(LOAD_E401)} kg/h.",
        f"Screening sizes with process_safety.relief.gas_area (API 520-I gas equation, derived; set 60 / 4 barg, back pressure 350 kPa abs, k and Z are A): PSV-202 {rs('PSV-202')}; PSV-205 {rs('PSV-205')}. Flare radiation and KOD size are not quantified."))
    y = section(s, 1135, yy + 4, 445, "COMMON OPEN ITEMS"); yy = y + 16
    bul(s, 1141, yy, ("HAZOP / LOPA with licensor data (sheet 8 is a first-pass node list).", "Statutory route (DPR section 6): environmental clearance, PESO, factory and boiler licences, fire NOC. Applicability not assessed."))
    legend_y = section(s, 1135, 720, 445, "LEGEND"); legend(s, 1141, legend_y + 16)
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (S4 and S5)"); sc_table(s, y + 3, ["S4", "S5"])
    return s


def sheet_relief():
    s = newsheet(6, "SAFETY DESIGN BASIS (1): relief schedule and safety instrumented functions", "Safety design basis: relief, SIF", "SAFETY_FEATURES_CHECKLIST; EIGA 15/21, OSHA 1910.119, HSG176, HSG238")
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE: every pressure item on sheet 1 (design pressures A: loop 60 barg, column 4 barg)")
    rows = [("Item", "Design pressure basis (A)", "Relief case(s)", "Device", "Discharge", "Sizing status"),
        ("TK-101 UCO tank", "atmospheric", "fire, thermal expansion, pump in/out", "PVRV-101 + emergency vent (gap: not drawn)", "atmosphere, safe location", "not sized: needs tank size; API 2000 not obtained"),
        ("U-101 pretreatment", "atmospheric to low", "blocked outlet, heating", "open vent (A)", "safe location", "not sized: needs vessel data"),
        ("V-102 feed drum", "3 bara operating; 5 barg (A)", "blocked outlet, fire, thermal expansion", "PSV-207", "safe location (A)", "not sized: needs pump shut-off head, vessel size"),
        ("E-201 feed heater", "loop 60 barg; hot-oil side A", "blocked-in expansion (XV-201 shut), tube rupture", "TSV (tag at detail design, not drawn)", "closed drain / hot-oil expansion", "not sized: needs hot-oil design pressure"),
        ("R-201 hydrotreater", "60 barg (53 bara max + margin, A)", "fire, blocked outlet, runaway (S3), H2 overpressure", "PSV-201", "FH-1 > V-501 > FL-501", "not sized: runaway needs kinetics, fire needs vessel dimensions"),
        ("V-201 hot separator", "60 barg", "fire, blocked liquid outlet (LV-201), loss of cooling", "PSV-204 (new)", "FH-1", "not sized: needs vessel dimensions"),
        ("E-202 air cooler", "60 barg", "in zone V-201 / E-202 / V-202 (no block valves)", "covered by PSV-204 / PSV-202", "FH-1", "reason: no isolation between the vessels"),
        ("V-202 cold separator", "60 barg", "loss of E-202 cooling, blocked gas outlet, fire", "PSV-202", "FH-1", f"screening: load {f0(LOAD_E202)} kg/h, {rs('PSV-202')}"),
        ("G-201 gas-treat stub", "60 barg", "in zone of V-202", "covered by PSV-202", "FH-1", "reason: no block valve; stub scope open"),
        ("K-201 and HP gas header", "60 barg", "blocked discharge (full circulation)", "PSV-203 (header)", "FH-1", f"screening: {f0(EXCESS*S1+G2)} kg/h H2, {rs('PSV-203')}"),
        ("R-301 isomerisation", "60 barg", "fire, loss of circulation gas, blocked outlet", "PSV-203", "FH-1", "not sized: fire needs vessel dimensions; compressor case sized above"),
        ("E-301, E-302, V-301", "60 barg", "tube rupture, blocked-in expansion, gas blow-by to C-401", "in zone of PSV-203; TSV; LALL-301 + XV-403", "FH-1", "not sized: gas blow-by exceeds PSV-205, so a SIF is the protection (sheet 6 SIF-6)"),
        ("E-203 recycle trim cooler", "60 barg; cooling side A", "blocked-in expansion, tube rupture", "TSV (not drawn)", "closed drain", "not sized: needs cooling-side design pressure"),
        ("C-401 fractionator", "4 barg", "fire, loss of reflux / E-401 cooling, blocked vapour outlet", "PSV-205", "FH-1", f"screening: load {f0(LOAD_E401)} kg/h, {rs('PSV-205')}; fire not sized"),
        ("E-401, V-401", "4 barg", "zone with C-401 (open overhead line)", "covered by PSV-205", "FH-1", "reason: no block valve; V-401 fire case not sized"),
        ("E-402, E-403 (hot oil)", "4 barg process; hot-oil side A", "tube rupture, blocked-in expansion", "TSV (not drawn)", "closed drain", "not sized"),
        ("TK-401/402/403", "atmospheric", "fire, thermal expansion, filling", "PVRV-401/402/403 + emergency vent (gap)", "atmosphere", "not sized: API 2000 not obtained"),
        ("V-501 flare KOD", "near atmospheric", "none: open to the stack", "none", "FL-501", "reason: no isolation from the flare; liquid carry-over case open"),
        ("FL-501 flare", "n/a", "total relief load", "-", "-", "not quantified: radiation, capacity need loads")]
    y = wtable(s, 20, y + 3, (160, 200, 280, 290, 220, 410), rows, 11.2, None, 14.3, True, 5)
    y = WRAP(s, 22, y + 14, "Sizing uses process_safety.relief (API 520-I gas equation, derived) only where a load is known; set pressure, k, Z and back pressure are A. R: OSHA 1910.119 requires the relief design basis as process safety information; CSB Kuraray: discharge location is a design item. API 520/521/2000, OISD, PESO texts: gap, standard not obtained.", 200, 10.5, 13) + 4
    y = section(s, 20, y + 4, 1560, "SAFETY INSTRUMENTED FUNCTIONS (SIL targets ASSUMED, A: no SIL verification, no LOPA)")
    rows = [("SIF", "Initiator > final elements", "Demand source", "Independent layers credited (A)", "SIL (A)"),
        ("SIF-1", "TAHH-211 (multipoint) > XV-201, XV-202, XV-402 close; K-201, heaters trip; HV-201 opens", "quench or recycle loss, S3", "TIC-212 control, alarm and operator, PSV-201", "SIL 2"),
        ("SIF-2", "TAHH-311 > same ESD-201 set", "R-301 exotherm, gas loss", "alarm, PSV-203", "SIL 2"),
        ("SIF-3", "AT-201A/B, AT-301, AT-401 (gas), BE-201, BE-401 > ESD-201 / ESD-401", "H2 or HC release, S1, S2, S4", "detection only; ventilation (open air); fire protection", "SIL 1"),
        ("SIF-4", "FAL-203 low K-201 flow > heaters and XV-201 close", "compressor trip, loss of H2 sweep", "alarm, TIC-212", "SIL 1"),
        ("SIF-5", "PAHH-202, LAHH-202 > XV-201, XV-202 close", "loss of E-202 cooling, S5", "PIC-201, PSV-202", "SIL 1"),
        ("SIF-6", "LALL-201, LALL-301 > close level valve / XV-403; trip P-401", "gas blow-by 47 bar to 1.5 bar column", "LIC-201, LIC-301, PSV-205 (not enough alone)", "SIL 2"),
        ("SIF-7", "LAHH-401/402/403 > stop rundown (valves to add: gap)", "tank overfill", "LI-4xx gauging, operator", "SIL 1; R: HSG176 para 137 independent high-high")]
    y = wtable(s, 20, y + 3, (60, 600, 260, 480, 160), rows, 11.2, None, 14.3, True, 5)
    WRAP(s, 22, y + 14, "Separation of control and protection: R (HSE HSG238 paras 32-34). IEC 61511 and CCPS LOPA texts: gap, standard not obtained, so SIL levels are placeholders.", 200, 10.5, 13)
    return s


def sheet_esd():
    s = newsheet(7, "SAFETY DESIGN BASIS (2): cause-and-effect, detection and mitigation", "Safety design basis: ESD, F&G, mitigation", "EIGA 15/21; HSG176; HSE COMAH plant layout; OSHA 1910.119")
    y = section(s, 20, 84, 1560, "ESD CAUSE-AND-EFFECT (A). X = acts. Every tag below is drawn on sheet 1")
    cols = ["Initiator", "XV-201", "XV-202", "XV-402", "XV-401", "XV-403", "HV-201", "HV-301", "K-201", "P-201", "Heaters", "P-401/2"]
    M_ = [("TAHH-211", "XXX--XX-XX-"), ("TAHH-311", "XXX--XX-XX-"), ("FAL-203", "X--------XX-"), ("AT-201A/B, AT-301 (H2)", "XXX--XXXXX-"), ("BE-201", "XXX--XXXXX-"), ("AT-401, BE-401", "--XXX---X-XX"),
          ("PAHH-202", "XX---------X-"), ("LAHH-202", "XX---------X-"), ("LALL-201", "----------X--"), ("LALL-301", "----X-----X"), ("Manual ESD", "XXXXXXXXXXXX"), ("Loss of instrument air / power", "XXXXXXXXXXXX")]
    # patterns written as strings of 11 flags for the 11 element columns
    rows = [cols]
    ev = {"TAHH-211": "XXX XXX XXX- ".split(), }
    def row(name, on): return [name] + ["X" if c in on else "" for c in cols[1:]]
    rows += [row("TAHH-211 (R-201)", {"XV-201", "XV-202", "XV-402", "HV-201", "K-201", "P-201", "Heaters"}), row("TAHH-311 (R-301)", {"XV-201", "XV-202", "XV-402", "HV-201", "K-201", "P-201", "Heaters"}),
             row("FAL-203 (K-201 flow)", {"XV-201", "K-201", "Heaters"}), row("AT-201A/B, AT-301 (H2)", {"XV-201", "XV-202", "XV-402", "HV-201", "HV-301", "K-201", "P-201", "Heaters"}),
             row("BE-201 (flame)", {"XV-201", "XV-202", "XV-402", "HV-201", "HV-301", "K-201", "P-201", "Heaters"}), row("AT-401, BE-401 (C-401)", {"XV-401", "XV-402", "XV-403", "Heaters", "P-401/2"}),
             row("PAHH-202 / LAHH-202 (V-202)", {"XV-201", "XV-202", "Heaters"}), row("LALL-201 (V-201)", {"P-401/2"}), row("LALL-301 (V-301)", {"XV-403", "P-401/2"}),
             row("Manual ESD (control room)", set(cols[1:])), row("Loss of instrument air / power", {"XV-201", "XV-202", "XV-401", "XV-402", "XV-403", "HV-201", "HV-301"})]
    y = table(s, 20, y + 3, (230,) + (110,) * 11, rows, 22, 11, bold_first_col=True)
    T(s, 22, y + 14, "Fail positions (A): XV-201, 202, 401, 402, 403 fail closed; HV-201, HV-301 fail open (R: fail-safe ROSOV, HSG176 para 128). LALL-201 also closes LV-201. Tank LAHH: no rundown isolation valves on TK-401/403 lines yet (gap).", 10.5, 400, "start", GREY)
    y = section(s, 20, y + 26, 1560, "DETECTION, ISOLATION, CONTAINMENT, LAYOUT (R = free named source, A = assumed, gap = standard not obtained)")
    rows = [("Topic", "Basis in this set", "Source / status"),
        ("Gas / flame detection", "H2 leak detection (AT) at K-201, R-201/E-201, R-301; hydrocarbon AT and flame detectors BE at C-401; flames of H2 are hard to see so gas detection supplements flame detection. Voting 2oo3 and set points: A.", "R (EIGA Doc 15/21; IFC fertilizer EHS for gas detectors); set points gap"),
        ("Isolation of large inventories", "Remote shut-off valves close on ESD: XV-201 (feed), XV-202 (H2), XV-401 (RD bottoms), XV-403 (V-301 liquid), XV-402 (hot oil). Fail-safe action and closing time to be set by the hazard study. Large hydrocarbon inventories: C-401 sump, V-201, recycle loop.", "R (HSG176 para 128)"),
        ("Bund / impoundment", "Tank farm TK-401/402/403 (and TK-101): bund capacity at least 110 % of the largest tank or 25 % of total tank capacity (whichever the source applies); tank sizes not set, volume not computed.", "R (HSG176 para 157); sizes A"),
        ("Safety distances / layout", "H2 equipment: about 5 m to ignition sources and wall openings, 8 m to boundary or wooden structures (EIGA table 1). Small flammable tanks 1 m to 15 m by size (HSG176 Table 1). Layout must address domino effects and occupied buildings; Indian distances: OISD-STD-106/116/118/144/163 gap.", "R (EIGA, HSG176, HSE COMAH layout); OISD gap"),
        ("Fire water / foam / deluge", "Deluge on the reactor and C-401 areas and fire water ring main assumed (A). No free source with a design rate was read for this set; OISD fire-water standards: gap.", "A; gap"),
        ("Ventilation / inerting", "Open-air structure for the H2 areas (A); N2 purge and inerting of reactors before start-up and after ESD (A). Vent lines must avoid ignition and detonation risk (EIGA).", "R for vent lines; A for purge"),
        ("Hydrogen vent / flare", "All relief to FH-1 > KOD V-501 > FL-501; hydrogen-rich relief needs flame and radiation study; discharge away from workers (CSB Kuraray).", "R (CSB Kuraray); study open"),
        ("Hot oil and hot hydrocarbon", "Hot-oil system for E-201, E-402, E-403 (A): leak and fire case; passive fire protection on supports (A).", "A")]
    wtable(s, 20, y + 3, (190, 940, 430), rows, 11.2, None, 14.3, True, 5)
    return s


def sheet_hazop():
    s = newsheet(8, "SAFETY DESIGN BASIS (3): hazard identification nodes and inherently safer options", "Safety design basis: HAZOP nodes, ISD", "OSHA 1910.119 (PHA incl. siting); EIGA 15/21; CSB reports")
    y = section(s, 20, 84, 1560, "HAZARD IDENTIFICATION: HAZOP-style first pass, qualitative (R: PHA with siting, OSHA 1910.119)")
    rows = [("Node", "Deviation", "Cause", "Consequence", "Safeguard (sheets 1, 6, 7)", "Action"),
        ("N1 Feed: TK-101, U-101, V-102, P-201", "No / low flow", "pump trip, filter blocked", "loss of liquid heat sink; catalyst overheating if H2 continues", "FIC-201, FAL-203, SIF-4", "confirm minimum liquid flow with licensor"),
        ("N2 R-201 + quench + recycle", "High temperature", "quench valve fails closed, P-202 trip, E-203 blocked, feed rich in unsaturates", f"runaway: +{DT_NO_QUENCH:.0f} to +{DT_NO_DILUENT:.0f} K (D); catalyst damage, loss of containment", "TIC-212, TAHH-211 (SIF-1), PSV-201, HV-201", "get licensor heat of reaction and bed limits; reconcile recycle ratio with NREL 1:1"),
        ("N3 V-201 / E-202 / V-202", "Low-low level in V-201", "LV-201 fails open", "HP gas to stage 2 and fractionator feed", "LIC-201, LALL-201 (SIF-6)", "confirm interface and SIL"),
        ("N3 V-201 / E-202 / V-202", "Loss of cooling", "E-202 fan or utility failure", f"vapour {f0(LOAD_E202)} kg/h to PSV-202; H2 and steam to flare", "PAHH-202, LAHH-202 (SIF-5), PSV-202", "relief load with hold-up; flare capacity"),
        ("N4 Gas loop K-201", "Leak of H2", "flange, seal, instrument connection", "jet or flash fire, invisible flame", "AT-201A/B (SIF-3), ESD-201, HV-301, open structure", "detector layout study; minimise flanges"),
        ("N5 R-301 + E-301/302", "High temperature / loss of circulation", "gas trip, exotherm", f"rise up to {Q2_KW*3600/(B['mht']*CP_L):.0f} K without gas; metallurgy limit", "TAHH-311 (SIF-2), PSV-203", "confirm stage-2 exotherm with licensor"),
        ("N6 V-301 to C-401 let-down", "Gas blow-by (low level)", "LIC-301 fault, valve stuck open", "47 bar gas into a 4 barg column, beyond PSV-205", "LALL-301, XV-403 (SIF-6), PSV-205", "highest-priority SIF; SIL and proof test interval"),
        ("N7 C-401, E-402, E-403", "Fire at hot bottoms", f"leak at {TC['rd']} C RD or hot oil", "pool or spray fire, escalation to pumps and column", "AT-401, BE-401, ESD-401, XV-401, XV-402, deluge (A)", "inventory, fire-water basis, PFP"),
        ("N8 Tanks and flare", "Overfill / flare liquid carry-over", "no independent high-high, KOD sized small", "spill, burning rain", "LAHH-401/402/403 (SIF-7), bund, V-501", "tank isolation valves (gap), KOD sizing")]
    y = wtable(s, 20, y + 3, (170, 150, 215, 295, 340, 390), rows, 11.2, None, 14.3, True, 5)
    y = section(s, 20, y + 8, 1560, "INHERENTLY SAFER DESIGN OPTIONS (specific to this process; A unless a source is given)")
    rows = [("Option", "What it means here", "Source"),
        ("Reduce inventory", f"Keep V-201 and V-202 hold-up small and short; recycle {R_TOT:.1f} x fresh feed is a large hot circulating inventory (Rev B): ask the licensor for a lower-recycle design with interbed gas quench (NREL text: up to 1:1).", "A; NREL App. D.2"),
        ("Moderate conditions", "Lower loop pressure and hydrogen purity where the catalyst allows; keep bed rise at 45 K or less (300 to 345 C window); E-201 outlet 275 C reduced if fouling allows.", "A"),
        ("Simplify / reduce leak points", "Welded piping and fewer flanges on the 50 bar H2 loop; one common loop for both stages (as drawn); a single EDV manifold.", "A; EIGA Doc 15/21 on minimising leak sources (not verified clause by clause)"),
        ("Substitute", "H2 from an electrolyser or imported supply instead of on-site SMR removes a second hot reformer and CO inventory; decision belongs with the H2 unit scope.", "A"),
        ("Minimise hot hydrocarbon near ignition sources", "Place C-401 bottoms, E-402 and P-401 away from the H2 loop and from heaters; downwind and with drainage away from the reactor (layout study).", "R (HSE COMAH layout: domino effects); distances gap")]
    y = wtable(s, 20, y + 3, (200, 1010, 350), rows, 11.2, None, 14.3, True, 5)
    return s


def build_all():
    return [sheet_pid(), sheet_hmb(), sheet_basis(), sheet_sc1(), sheet_sc2(), sheet_relief(), sheet_esd(), sheet_hazop()]


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, "SAF by HEFA P&ID set Rev B", previews="--previews" in sys.argv)
    print("ok", len(sheets), f"closure in {M_IN:,.0f} out {M_OUT:,.0f} err {ERR_MASS:.3f} %  SAF {SAF_TYR:,.0f} t/yr")

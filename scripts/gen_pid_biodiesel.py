#!/usr/bin/env python3
"""Generate the biodiesel (B100) plant P&ID set: P&ID, heat and material balance, and process-safety scenarios. 20 KLPD, batch
transesterification of UCO / non-edible oil with methanol and alkali catalyst at about 40 C. Standard library only.

Sources (S) are these DPR files, held outside the repo (read 11 Nov 2026):
  [T]  VertiStrat_DPR_Templates/Template_DPR_Biodiesel_B100_20KLPD.docx   sections 1, 4, 6, 7, 9, 12
  [J2] Owner_20KLPD_Draft_DPR_v2.docx (private draft, not in repo)                        sections 1, 5 (process, mass balance), 7, 8, 11
  [B]  Biodiesel_18000KL_Sample_DPR_v2.docx (and v1)                      sections 5, 6 (process steps, tanks, EIA remarks)
  [J1] Owner_10000KL_Draft_DPR.docx (private draft, not in repo)                          section 5 (same process text, 0.88 t/KL, same ratios)
Everything else is D (derived in code, formula shown) or A (assumed by this drawing, listed on sheet 2).
Molar masses are derived from atomic masses C 12.011, H 1.008, O 15.999, Na 22.990 (IUPAC standard atomic weights, rounded).

Rev B (11 Nov 2026): closes the sourced gaps of docs/pid/validation/BIODIESEL_VALIDATION.md and GAP_CLOSURE_BIO.md (vacuum methanol recovery plus methanol
column, FFA limit, 20 % wash, species heat capacities, crude-glycerol basis) and adds the safety design basis (sheets 6 to 8).

Usage:  python3 scripts/gen_pid_biodiesel.py docs/pid/BIODIESEL_PID_Set_RevB.html [--previews]
Screening aid, not certified design."""
import sys, os, math, textwrap
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pidlib import *

TOTAL = 8
_SheetBase = Sheet


class Sheet(_SheetBase):
    """Rev B: pidlib's frame() prints Rev A, so the SVG text is post-processed here (pidlib is not edited)"""
    def svg(self):
        return super().svg().replace("|  Rev A", "|  Rev B").replace("Draft A. Screening", "Draft B. Screening")


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
try:
    from process_safety import relief as _relief          # stdlib toolkit package in this repo (fire-case and vapour sizing)
except Exception:                                          # pragma: no cover
    _relief = None

# =====================================================================================================  HMB (computed)
AM = dict(C=12.011, H=1.008, O=15.999, Na=22.990)
FORM = dict(TG=dict(C=57, H=104, O=6), FFA=dict(C=18, H=34, O=2), MeOH=dict(C=1, H=4, O=1), NaOH=dict(Na=1, O=1, H=1),
            FAME=dict(C=19, H=36, O=2), GLY=dict(C=3, H=8, O=3), SOAP=dict(C=18, H=33, O=2, Na=1), H2O=dict(H=2, O=1))
MW = {k: sum(AM[e] * n for e, n in f.items()) for k, f in FORM.items()}
SP = ["TG", "FFA", "MeOH", "NaOH", "FAME", "GLY", "SOAP", "H2O", "MIU"]
SPN = dict(TG="Triglyceride (oil)", FFA="Free fatty acid", MeOH="Methanol", NaOH="NaOH catalyst", FAME="FAME (biodiesel)",
           GLY="Glycerol", SOAP="Soap (Na oleate)", H2O="Water", MIU="Moisture/insol./unsap. (MIU)")

# --- S inputs (DPR files, unchanged from Rev A)
CAP_KLPD = 20.0            # S [T] s1 "6,000 KL/yr (20 KLPD)"; [J2] s1 "20 KLPD nameplate, about 6,000 KL a year at 300 days"
RHO_BD = 0.88              # S [J2] s5 table "6,000 KL x 0.88 t/KL"
YIELD = 0.96               # S [J2] s5 table "0.96 t biodiesel per t oil"; [B] s8 "Yield 0.96"
CAT_PCT = 0.01             # S [J2] s5 table "Catalyst ... 1% of biodiesel"
T_RX = 40.0                # S [T] s4 / [J2] s5 "at about 40 C"
T_BATCH_RX = 6.0           # S [J2] s5 "six hours per batch"
DPR = dict(biodiesel_t_yr=5280, oil_t_yr=5500, meoh_t_yr=581, cat_t_yr=53, gly_t_yr=528, days=300)   # S [J2] s5 table, s1

# --- S inputs added in Rev B (documents fetched and read; see docs/pid/validation/GAP_CLOSURE_BIO.md)
#   [S98]  Sheehan et al., NREL/SR-580-24089, May 1998, https://www.osti.gov/servlets/purl/1218369
#   [VG04] Van Gerpen et al., Biodiesel Analytical Methods, NREL/SR-510-36240, Jul 2004 (UNT copy), base-catalysis section
#   [AL14] Alam, MASc thesis, Univ. Regina 2014, single-flash methanol recovery cases (cited through GAP_CLOSURE_BIO.md)
FFA_LIMIT = 0.010          # S [VG04]: fats with FFA above about 1 % must be pretreated before base catalysis (soap + water otherwise)
WASH_FRAC = 0.20           # S [S98] p.148: countercurrent continuous wash, 20 % of ester mass (batch wash 30 to 40 %)
AQ_TO_ESTER = 0.05         # S [S98] p.148: after the wash, 5 % of the aqueous phase is lost to the ester phase (settler)
COL_XB = 0.005             # S [S98] 5.5.1.5: methanol column bottoms contain less than 0.5 % methanol
COL_XD = 0.0005            # S [S98] 5.5.1.5: distillate contains less than 0.05 % moisture
COL_REFLUX = 3.665         # S [S98] Fig. 66/68: reflux ratio 3.665 (basis not stated in the figure; taken as molar, near-pure methanol so mass ~ molar)

# --- D constants frozen from tool runs (provenance in comments; run again to refresh)
#   python3 -I docs/pid/validation/BIODIESEL_REVB_flash_check.py   (thermo 0.6.1 UNIFAC-Dortmund, CoolProp 8.0)
FLASH_P = 0.10             # bar(a), A design choice inside the sourced range (UNIFAC and [AL14]: about 90 % at 0.2, about 95 % at 0.1, 99 % at 0.02 bar)
FL = dict(E_M=0.9506, E_W=0.9469, G_M=0.9657, G_W=0.9665)   # D frozen: V-401 MeOH, V-401 H2O, V-402 MeOH, V-402 H2O vaporised fraction at 80 C, 0.10 bar(a), 1 equilibrium stage
FLASH_TBL = [(1.0, 19.0, 21.7, 34.5, 28.3), (0.5, 70.3, 70.6, 78.7, 77.1), (0.2, 89.7, 89.2, 92.8, 92.8), (0.1, 95.1, 94.7, 96.6, 96.6), (0.05, 97.6, 97.4, 98.3, 98.4), (0.02, 99.0, 99.0, 99.3, 99.4)]             # D frozen (P bar, E MeOH %, E H2O %, G MeOH %, G H2O %); filled by the check script output
#   python3 -I props.py   (CoolProp 8.0; thermo 0.6.1 Chemical.Cpl)
CPS = dict(TG=2.04, FFA=2.16, MeOH=2.60, NaOH=1.50, FAME=2.28, GLY=2.55, SOAP=2.00, H2O=4.18, MIU=2.00)   # kJ/kg/K; TG triolein 35 C, FFA oleic 60 C, FAME methyl oleate 60 C,
#   GLY glycerol 60 C (thermo); MeOH and H2O CoolProp 30 to 40 C (2.57 to 2.63; 4.18); NaOH, SOAP, MIU are A
LAM_M80 = 1069.2           # D CoolProp: methanol latent heat at 80 C, kJ/kg (flash duty)
LAM_W80 = 2314.3           # D CoolProp: water, liquid 80 C to vapour 80 C at 0.10 bar, kJ/kg
LAM_M65 = 1101.0           # D CoolProp: methanol latent heat at 64.5 C (column), kJ/kg
LAM_M60 = 1109.6           # D CoolProp: methanol latent heat at 60 C (dryer)
LAM_W60 = 2357.7           # D CoolProp: water latent heat at 60 C (dryer, 0.2 bar)
DH_M_COND = 1316.3         # D CoolProp: methanol vapour 80 C, 0.10 bar to liquid 5 C, kJ/kg
DH_W_COND = 2628.3         # D CoolProp: water vapour 80 C, 0.10 bar to liquid 5 C, kJ/kg
TSAT_M_01 = 15.2           # D CoolProp: methanol saturation temperature at 0.10 bar(a), C (a cooling-water condenser cannot condense at this pressure)
TSAT_M_1ATM = 64.5         # D CoolProp 64.48 C; [S98] Fig. 68 column top 64.49 C

# --- A inputs (listed on sheet 3)
A = dict(
    N_BATCH=4,        # A batches per day: 2 reactors x 2 batches per 12 h cycle (6 h reaction S + 6 h charge/heat/settle/discharge)
    FFA=FFA_LIMIT, H2O=0.005,   # FFA at the sourced limit (Rev A: 2.0 wt%); water A; triglyceride fraction is SOLVED (D) so that product = nameplate
    X_TG=0.98,        # A triglyceride conversion (98 % reported, 99 % overall two-stage: [S98] 5.5.1.2)
    R_MEOH=6.0,       # A methanol : triglyceride mole ratio (stoichiometric 3; 6:1 most common [VG04])
    CAT_SOL=0.10,     # A catalyst dissolved at 10 wt% NaOH in methanol in M-301
    SPLIT_MEOH=0.70,  # A fraction of unreacted methanol reporting to the glycerol phase in V-302
    SPLIT_H2O=0.90,   # A fraction of water reporting to the glycerol phase in V-302
    VENT=0.01,        # A fraction of methanol vapour lost with the vacuum-pump exhaust (Rev A: 0.2 % with the condenser vent); range 0.2 to 2 %
    W_DRY=0.0005,     # A water in dry biodiesel (mass fraction); IS 15607 limit not read
    T_AMB=30.0, T_FLASH=80.0, T_WASH=60.0, T_TANK=40.0, T_COND=5.0, T_COLF=5.0, T_COLB=99.0,   # A temperatures, C (T_COLB: water-rich bottoms at 1 atm)
)


def batch_model(wtg):
    """one batch, kg. Returns dict stream-number -> dict(species -> kg), plus misc."""
    N = A["N_BATCH"]
    B = CAP_KLPD * RHO_BD * 1000.0 / N          # D product per batch = nameplate x density / batches per day
    F1 = B / YIELD                              # D oil received per batch (S yield)
    st = {}
    TG0, FFA0, W0 = F1 * wtg, F1 * A["FFA"], F1 * A["H2O"]
    MIU = F1 - TG0 - FFA0 - W0                  # D remainder: filtered out as cake
    if MIU < 0: return None
    st[1] = dict(TG=TG0, FFA=FFA0, H2O=W0, MIU=MIU)
    st[2] = dict(MIU=MIU)
    st[3] = dict(TG=TG0, FFA=FFA0, H2O=W0)
    nTG, nFFA = TG0 / MW["TG"], FFA0 / MW["FFA"]
    nconv = A["X_TG"] * nTG
    NaOH = CAT_PCT * B                          # S 1 % of biodiesel
    if NaOH / MW["NaOH"] < nFFA: return None
    meoh_tot = A["R_MEOH"] * nTG * MW["MeOH"]
    m7 = NaOH * (1 / A["CAT_SOL"] - 1)
    st[8] = dict(NaOH=NaOH)
    FAME, GLY = 3 * nconv * MW["FAME"], nconv * MW["GLY"]
    cons = 3 * nconv * MW["MeOH"]
    w5 = 0.0                                    # water carried in the recovered methanol (stream 5): fixed-point loop
    for _ in range(200):
        f6 = (meoh_tot - m7) / meoh_tot
        st[6] = dict(MeOH=meoh_tot - m7, H2O=w5 * f6)
        st[7] = dict(MeOH=m7, H2O=w5 * (1 - f6))
        st[9] = dict(NaOH=NaOH, MeOH=m7, H2O=st[7]["H2O"])
        # reactor R-301:  TG + 3 MeOH -> 3 FAME + GLY ;  FFA + NaOH -> soap + H2O
        st[10] = dict(FAME=FAME, GLY=GLY, TG=(nTG - nconv) * MW["TG"], MeOH=meoh_tot - cons, NaOH=NaOH - nFFA * MW["NaOH"],
                      SOAP=nFFA * MW["SOAP"], H2O=W0 + nFFA * MW["H2O"] + w5)
        s = st[10]
        st[11] = dict(FAME=s["FAME"], TG=s["TG"], MeOH=(1 - A["SPLIT_MEOH"]) * s["MeOH"], H2O=(1 - A["SPLIT_H2O"]) * s["H2O"])
        st[12] = dict(GLY=s["GLY"], SOAP=s["SOAP"], NaOH=s["NaOH"], MeOH=A["SPLIT_MEOH"] * s["MeOH"], H2O=A["SPLIT_H2O"] * s["H2O"])
        st[13] = dict(MeOH=FL["E_M"] * st[11]["MeOH"], H2O=FL["E_W"] * st[11]["H2O"])      # V-401 vacuum flash vapour
        st[14] = dict(MeOH=FL["G_M"] * st[12]["MeOH"], H2O=FL["G_W"] * st[12]["H2O"])      # V-402 vacuum flash vapour
        st[16] = dict(FAME=st[11]["FAME"], TG=st[11]["TG"], MeOH=st[11]["MeOH"] - st[13]["MeOH"], H2O=st[11]["H2O"] - st[13]["H2O"])
        st[17] = dict(GLY=st[12]["GLY"], SOAP=st[12]["SOAP"], NaOH=st[12]["NaOH"], MeOH=st[12]["MeOH"] - st[14]["MeOH"], H2O=st[12]["H2O"] - st[14]["H2O"])
        vapM, vapW = st[13]["MeOH"] + st[14]["MeOH"], st[13]["H2O"] + st[14]["H2O"]
        st[15] = dict(MeOH=A["VENT"] * vapM)                                               # VP-401 exhaust
        st[23] = dict(MeOH=vapM - st[15]["MeOH"], H2O=vapW)                                # condensate to C-401
        FM, FW = st[23]["MeOH"], st[23]["H2O"]
        det = (1 - COL_XD) * (1 - COL_XB) - COL_XB * COL_XD
        Dm = (FM * (1 - COL_XB) - COL_XB * FW) / det                                       # distillate mass: D(1-xd) + Bt xb = FM ; D xd + Bt (1-xb) = FW
        Bt = ((1 - COL_XD) * FW - COL_XD * FM) / det
        st[5] = dict(MeOH=Dm * (1 - COL_XD), H2O=Dm * COL_XD)
        st[24] = dict(MeOH=Bt * COL_XB, H2O=Bt * (1 - COL_XB))
        if abs(st[5]["H2O"] - w5) < 1e-13: break
        w5 = st[5]["H2O"]
    st[4] = dict(MeOH=meoh_tot - st[5]["MeOH"])          # V-201: 4 + 5 = 6 + 7 (methanol)
    st[18] = dict(H2O=WASH_FRAC * sum(st[16].values()))
    aqW, aqM = st[18]["H2O"] + st[16]["H2O"], st[16]["MeOH"]
    org = st[16]["FAME"] + st[16]["TG"]
    st[19] = dict(H2O=(1 - AQ_TO_ESTER) * aqW, MeOH=(1 - AQ_TO_ESTER) * aqM)
    st[20] = dict(FAME=st[16]["FAME"], TG=st[16]["TG"], H2O=AQ_TO_ESTER * aqW, MeOH=AQ_TO_ESTER * aqM)
    wd = A["W_DRY"] / (1 - A["W_DRY"]) * org
    st[22] = dict(FAME=st[16]["FAME"], TG=st[16]["TG"], H2O=wd)
    st[21] = dict(H2O=st[20]["H2O"] - wd, MeOH=st[20]["MeOH"])
    for k, d in st.items():
        for sp, v in d.items():
            if v < -1e-9: return None
    return st, dict(B=B, F1=F1, MIU=MIU, nTG=nTG, nFFA=nFFA, nconv=nconv, meoh_tot=meoh_tot, cons=cons, NaOH=NaOH)


def solve():
    lo, hi = 0.80, 0.99
    def prod(w):
        r = batch_model(w)
        return sum(r[0][22].values()) - r[1]["B"] if r else -1e9
    for _ in range(200):
        mid = (lo + hi) / 2
        if prod(mid) > 0: hi = mid
        else: lo = mid
    wtg = (lo + hi) / 2
    st, m = batch_model(wtg)
    m["wtg"] = wtg
    return st, m


ST, M = solve()
tot = lambda d: sum(d.values())
HR = 24.0 / A["N_BATCH"]            # hours per batch period (24 h average basis)
H = lambda x: x / HR                # kg/batch -> kg/h

# --- closure
IN_IDS, OUT_IDS = [1, 4, 8, 18], [2, 15, 17, 19, 21, 22, 24]
m_in, m_out = sum(tot(ST[i]) for i in IN_IDS), sum(tot(ST[i]) for i in OUT_IDS)
ERR = (m_out - m_in) / m_in * 100.0
assert abs(ERR) < 0.1, ERR
# unit closures
UNITS = {
    "E/F-101 filter": ([1], [2, 3]), "V-201 methanol dosing": ([4, 5], [6, 7]), "M-301 catalyst mix": ([7, 8], [9]),
    "R-301 reactor": ([3, 6, 9], [10]), "V-302 settler": ([10], [11, 12]), "V-401 ester vacuum flash": ([11], [13, 16]),
    "V-402 glycerol vacuum flash": ([12], [14, 17]), "E-401/V-403/VP-401": ([13, 14], [15, 23]), "C-401 methanol column": ([23], [5, 24]),
    "C-501 wash + settle": ([16, 18], [19, 20]), "V-601 dryer": ([20], [21, 22]),
}
UNIT_ERR = {}
for k, (i, o) in UNITS.items():
    a, b = sum(tot(ST[x]) for x in i), sum(tot(ST[x]) for x in o)
    UNIT_ERR[k] = (a, b); assert abs(a - b) / a < 1e-9, (k, a, b)


def elem(ids):
    e = dict(C=0.0, H=0.0, O=0.0, Na=0.0)
    for i in ids:
        for sp, kg in ST[i].items():
            if sp == "MIU": continue
            for el, n in FORM[sp].items(): e[el] += kg / MW[sp] * n          # kmol of element
    return e
E_IN, E_OUT = elem(IN_IDS), elem(OUT_IDS)
for el in E_IN: assert abs(E_IN[el] - E_OUT[el]) / E_IN[el] < 1e-9, el          # stoichiometric (element) closure
# reaction identity: TG + 3 MeOH -> 3 FAME + GLY in mass
assert abs(MW["TG"] + 3 * MW["MeOH"] - 3 * MW["FAME"] - MW["GLY"]) < 1e-6
# S cross-checks (D): per day
DAY = {i: tot(ST[i]) * A["N_BATCH"] for i in ST}
assert abs(DAY[22] - CAP_KLPD * RHO_BD * 1000) < 1e-6 * DAY[22]

# --- duties (kJ per batch)
T_MIX = (tot(ST[4]) * A["T_AMB"] + tot(ST[5]) * A["T_TANK"]) / (tot(ST[4]) + tot(ST[5]))     # D mixing temperature of V-201 outlet


def dT(d, t_lo, t_hi):
    """sensible heat magnitude, kJ: sum m cp (t_hi - t_lo) with species heat capacities CPS"""
    return sum(kg * CPS[sp] * (t_hi - t_lo) for sp, kg in d.items())


D_COL = tot(ST[5]); B_COL = tot(ST[24])
Q_COND_SAT = D_COL * (1 + COL_REFLUX) * LAM_M65                                   # D total condensation at 64.5 C (reflux + distillate)
Q = {}
Q["E-101 oil heater 30 to 40 C (TO)"] = dT(ST[3], A["T_AMB"], T_RX)
Q["R-301 jacket, charge to 40 C (TO)"] = dT(ST[6], T_MIX, T_RX) + dT(ST[9], T_MIX, T_RX)
Q["V-401 coil: heat to 80 C + vacuum flash (TO)"] = dT(ST[11], T_RX, A["T_FLASH"]) + ST[13]["MeOH"] * LAM_M80 + ST[13]["H2O"] * LAM_W80
Q["V-402 coil: heat to 80 C + vacuum flash (TO)"] = dT(ST[12], T_RX, A["T_FLASH"]) + ST[14]["MeOH"] * LAM_M80 + ST[14]["H2O"] * LAM_W80
Q["E-403 C-401 reboiler (TO)"] = Q_COND_SAT + D_COL * CPS["MeOH"] * (TSAT_M_1ATM - A["T_COLF"]) + B_COL * CPS["H2O"] * (A["T_COLB"] - A["T_COLF"])
Q["V-601 dryer: evaporate water + MeOH (TO)"] = ST[21]["H2O"] * LAM_W60 + ST[21]["MeOH"] * LAM_M60
Q["E-401 vacuum condenser, vapour 80 C to liquid 5 C (CH)"] = (ST[13]["MeOH"] + ST[14]["MeOH"]) * DH_M_COND + (ST[13]["H2O"] + ST[14]["H2O"]) * DH_W_COND
Q["E-402 column condenser + distillate to 40 C (CW)"] = Q_COND_SAT + D_COL * CPS["MeOH"] * (TSAT_M_1ATM - A["T_TANK"])
Q["E-501 ester cooler 80 to 60 C (CW)"] = dT(ST[16], A["T_WASH"], A["T_FLASH"])
Q["VP-601 dryer vapour condenser (CW)"] = ST[21]["H2O"] * LAM_W60 + ST[21]["MeOH"] * LAM_M60
Q["E-602 product cooler 60 to 40 C (CW)"] = dT(ST[22], A["T_TANK"], A["T_WASH"])
kW = lambda kj: kj / (HR * 3600.0)
Q_TO = sum(v for k, v in Q.items() if "(TO)" in k); Q_CW = sum(v for k, v in Q.items() if "(CW)" in k); Q_CH = sum(v for k, v in Q.items() if "(CH)" in k)
# Rev A values, frozen from the Rev A generator run (MJ per batch) for the change box
REV_A = {"V-401 coil": 522.9, "V-402 coil": 446.7, "E-401 cond": 580.8, "E-501": 176.1, "E-602": 176.0, "V-601": 25.4, "TO total": 1097.6, "CW total": 958.2,
         "wash kg/d": 880.0, "crude gly kg/d": 2415.0, "fresh MeOH kg/d": 1877.0, "soap % of 17": 16.4, "stream 21 kg/b": 11.0}

# stream header data: (id, name, from, to, phase, T, P)
SD = {
    1: ("UCO as received", "UC-101", "T-101", "L", 30, 1.0), 2: ("Filter cake (MIU)", "F-101", "drum", "S", 30, 1.0),
    3: ("Oil to reactor", "E-101", "R-301", "L", 40, 3.0), 4: ("Fresh methanol", "T-201", "V-201", "L", 30, 3.0),
    5: ("Recovered methanol (dry)", "C-401", "V-201", "L", 40, 3.0), 6: ("Methanol dose", "V-201", "R-301", "L", round(T_MIX), 3.0),
    7: ("Methanol to M-301", "V-201", "M-301", "L", round(T_MIX), 3.0), 8: ("NaOH catalyst", "H-301", "M-301", "S", 30, 1.0),
    9: ("Catalyst solution", "M-301", "R-301", "L", round(T_MIX), 3.0), 10: ("Reactor effluent", "R-301", "V-302", "L", 40, 3.0),
    11: ("Ester phase", "V-302", "V-401", "L", 40, 1.1), 12: ("Glycerol phase", "V-302", "V-402", "L", 40, 1.1),
    13: ("MeOH/H2O vapour", "V-401", "E-401", "V", 80, FLASH_P), 14: ("MeOH/H2O vapour", "V-402", "E-401", "V", 80, FLASH_P),
    15: ("Vacuum pump exhaust", "VP-401", "vent", "V", 5, 1.0), 16: ("Stripped ester", "V-401", "C-501", "L", 80, 3.0),
    17: ("Crude glycerol", "V-402", "T-801", "L", 80, 1.1), 18: ("Wash water", "PW", "C-501", "L", 30, 3.0),
    19: ("Wash water out", "C-501", "ETP", "L", 60, 1.1), 20: ("Wet biodiesel", "C-501", "V-601", "L", 60, 1.1),
    21: ("Dryer vapour", "V-601", "VP-601", "V", 60, 0.2), 22: ("Dry biodiesel B100", "V-601", "T-701", "L", 40, 1.1),
    23: ("Wet MeOH condensate", "V-403", "C-401", "L", 5, 1.5), 24: ("Column bottoms (water)", "C-401", "ETP", "L", round(A["T_COLB"]), 1.1),
}


def fmt(x, d=0):
    return f"{x:,.{d}f}"


# =====================================================================================================  drawing helpers
TO_C = "#c26a00"          # thermal oil
P = {}                    # key ports for overlays


def open_dim(s, on):
    if on: s.add('<g opacity=".30">')


def close_dim(s, on):
    if on: s.add('</g>')


def tagl(s, x, y, tag, sub=None, anchor="start", size=10.5):
    T(s, x, y, tag, size, 700, anchor)
    if sub: T(s, x, y + 11.5, sub, 9, 400, anchor, GREY)


def rot_pump(s, cx, cy, mode, r=13, label=None, lx=None, ly=None):
    """mode 'h': suction left, discharge up-right ; 'v': suction top, discharge bottom-right ; 'l': suction right, discharge bottom-left"""
    rot = {"h": 0, "v": 90, "l": 180}[mode]
    if rot: s.add(f'<g transform="rotate({rot} {cx} {cy})">')
    pump(s, cx, cy, r, None)
    if rot: s.add('</g>')
    if label: T(s, lx if lx is not None else cx, ly if ly is not None else cy + r + 14, label, 10, 700, "middle" if lx is None else "start")
    return dict(h=dict(i=(cx - r, cy), o=(cx + r, cy - r)), v=dict(i=(cx, cy - r), o=(cx + r, cy + r)), l=dict(i=(cx + r, cy), o=(cx - r, cy + r)))[mode]


def vhx(s, cx, cy, ln=54, w=24, color=INK):
    s.add(f'<g transform="rotate(90 {cx} {cy})">')
    hx(s, cx, cy, ln, w, None, None, color)
    s.add('</g>')
    return dict(top=(cx, cy - ln / 2), bot=(cx, cy + ln / 2))


def hop(s, x, y, half=6):
    """horizontal line hops over a vertical one at (x, y): call after both are drawn"""
    s.add(f'<rect x="{x-half-1}" y="{y-3}" width="{2*half+2}" height="6" fill="#fff"/>')
    PL(s, [(x, y - 3.2), (x, y + 3.2)], 2.6)
    s.add(f'<path d="M{x-half},{y} A{half},{half} 0 0 1 {x+half},{y}" fill="none" stroke="{INK}" stroke-width="2.6"/>')


def sig(s, pts, dash="5 4"):
    PL(s, pts, 1.2, BLUE, dash, "ahb")


def to_pipe(s, pts, arrow_=True):
    PL(s, pts, 2.4, TO_C)
    if arrow_ and len(pts) >= 2:
        (xa, ya), (xb, yb) = pts[-2], pts[-1]
        if abs(xb - xa) >= abs(yb - ya): arrow(s, xb, yb, "r" if xb > xa else "l", TO_C, 8)
        else: arrow(s, xb, yb, "d" if yb > ya else "u", TO_C, 8)


def vent_sym(s, x, y, h=16):
    """open vent stub with flame-arrester diamond"""
    PL(s, [(x, y), (x, y - h)], 2.4)
    s.add(f'<polygon points="{x},{y-h*0.75-5} {x+5},{y-h*0.75} {x},{y-h*0.75+5} {x-5},{y-h*0.75}" fill="#fff" stroke="{INK}" stroke-width="1.3"/>')
    s.add(f'<path d="M{x-6},{y-h-1} Q{x},{y-h-9} {x+6},{y-h-1}" fill="none" stroke="{INK}" stroke-width="1.8"/>')


# =====================================================================================================  P&ID zones
CWC = "#1e88e5"


def cw_stub(s, x, y, kind):
    """cooling water stub below an exchanger at (x, y): 'in' = supply, 'out' = return"""
    if kind == "in":
        PL(s, [(x, y + 16), (x, y)], 1.8, CWC); arrow(s, x, y, "u", CWC, 7); T(s, x, y + 27, "CWS", 8.5, 700, "middle", CWC)
    else:
        PL(s, [(x, y), (x, y + 16)], 1.8, CWC); arrow(s, x, y + 16, "d", CWC, 7); T(s, x, y + 27, "CWR", 8.5, 700, "middle", CWC)


def zone_A(s, dim=False):
    """A  UCO receipt and pre-treatment"""
    open_dim(s, dim)
    T(s, 30, 95, "A  UCO RECEIPT AND PRE-TREATMENT", 10, 700, fill=GREY)
    R(s, 36, 118, 50, 34, "#fff", INK, 1.6); T(s, 61, 133, "UC-101", 10, 700, "middle"); T(s, 61, 145, "tanker", 9, 400, "middle")
    pipe(s, [(86, 135), (95, 135), (95, 176)])
    strm(s, 95, 156, 1)
    tank(s, 95, 255, 80, 70, None, None, "cone", 0.55)
    T(s, 95, 238, "T-101", 11, 700, "middle")
    tagl(s, 30, 277, "T-101 UCO receipt tank", "atmospheric, size TBD (A)")
    vent_sym(s, 115, 181, 12); T(s, 123, 172, "PVRV-101", 8.5, 700)
    bubble(s, 36, 222, "LT", "101", True); PL(s, [(51, 222), (55, 222)], 1.2)
    PL(s, [(135, 241), (162, 241)], 2.6)
    pp = rot_pump(s, 175, 241, "h", 13, "P-101", 175, 270)
    pipe(s, [pp["o"], (pp["o"][0], 128), (214, 128)])
    R(s, 214, 113, 28, 30, "#fff", INK, 2); PL(s, [(221, 113), (221, 143)], 1, "#777"); PL(s, [(235, 113), (235, 143)], 1, "#777")
    T(s, 228, 106, "F-101", 10, 700, "middle")
    PL(s, [(242, 128), (258, 128)], 2.6)
    pipe(s, [(228, 143), (228, 190)]); strm(s, 228, 162, 2); T(s, 220, 182, "cake", 9, 400, "end")
    bubble(s, 258, 162, "PDI", "101", False); PL(s, [(258, 128), (258, 147)], 1.0, BLUE, "3 3")
    hx(s, 285, 128, 54, 24, None, None)
    T(s, 285, 110, "E-101", 10, 700, "middle")
    to_pipe(s, [(285, 140), (285, 200)], False); valve(s, 285, 178, 90, "gate", act=True, color=TO_C)
    T(s, 302, 196, "TCV-102", 9.5, 700); T(s, 302, 207, "TOS/TOR", 9, 400, fill=TO_C)
    bubble(s, 325, 160, "TIC", "102", True)
    PL(s, [(318, 128), (318, 145)], 1.0, BLUE, "3 3"); sig(s, [(325, 175), (325, 181), (302, 181)])
    PL(s, [(312, 128), (345, 128)], 2.6); strm(s, 329, 128, 3)
    close_dim(s, dim)


def zone_B(s, dim=False):
    """B  methanol storage, dosing and catalyst"""
    open_dim(s, dim)
    T(s, 30, 392, "B  METHANOL, CATALYST", 10, 700, fill=GREY)
    R(s, 30, 398, 300, 225, "none", AMBER, 1.4, "7 4"); T(s, 36, 619, "bund / sump (A)", 9, 400, fill=AMBER)
    tank(s, 80, 598, 90, 100, None, None, "cone", 0.6, "#e3f2fd")
    T(s, 80, 566, "T-201", 11, 700, "middle"); T(s, 80, 579, "methanol", 9, 400, "middle")
    PL(s, [(52, 493), (52, 458)], 2.4); valve(s, 52, 478, 90, "ball", act=True, color=RED); T(s, 74, 470, "XV-203", 9, 700)
    T(s, 58, 452, "tanker fill (A)", 9, 400)
    vent_sym(s, 108, 492, 18); T(s, 117, 478, "PVRV-201", 9.5, 700); T(s, 117, 489, "+ flame arr. (A)", 9, 400)
    bubble(s, 143, 520, "LT", "201", True); PL(s, [(125, 520), (128, 520)], 1.2)
    bubble(s, 143, 553, "LSHH", "201", True); PL(s, [(125, 553), (128, 553)], 1.2)
    PL(s, [(125, 578), (153, 578)], 2.6); valve(s, 136, 578, 180, "ball", act=True, color=RED); T(s, 131, 612, "XV-201", 9.5, 700, "middle")
    pp = rot_pump(s, 166, 578, "h", 12, None); T(s, 182, 606, "P-201", 10, 700, "middle")
    pipe(s, [pp["o"], (178, 520), (203, 520)]); strm(s, 178, 545, 4)
    vvessel(s, 231, 420, 56, 110, None, None, 0)
    T(s, 231, 468, "V-201", 11, 700, "middle"); T(s, 231, 481, "dosing tank", 9, 400, "middle")
    bubble(s, 296, 436, "WT", "201", True); PL(s, [(259, 436), (281, 436)], 1.2)
    vent_sym(s, 231, 405, 12); T(s, 264, 388, "PVRV-202", 8.5, 700); T(s, 264, 398, "N2 blanket (A)", 8.5, 400)
    pipe(s, [(356, 483), (259, 483)]); strm(s, 300, 483, 5); hop(s, 345, 483); T(s, 340, 497, "5 from C-401 (L-402)", 8.5, 400, "end")
    PL(s, [(231, 546), (231, 551)], 2.6)
    p2 = rot_pump(s, 231, 563, "v", 12, None); T(s, 248, 562, "P-202", 10, 700)
    PL(s, [p2["o"], (243, 575), (345, 575)], 2.6); strm(s, 300, 575, 6)
    PL(s, [(345, 739), (345, 140)], 2.6); arrow(s, 345, 140, "u")
    valve(s, 345, 520, 90, "ball", act=True, color=RED); T(s, 334, 513, "XV-202", 9.5, 700, "end")
    bubble(s, 60, 425, "AT", "201A", True); bubble(s, 100, 425, "BE", "201", True); bubble(s, 312, 538, "AT", "201B", True)
    R(s, 30, 628, 330, 134, "none", AMBER, 1.2, "7 4"); T(s, 36, 641, "catalyst area (A)", 9, 400, fill=AMBER)
    pipe(s, [(258, 575), (258, 640), (272, 640)]); strm(s, 258, 600, 7)
    s.add(f'<polygon points="203,652 247,652 237,672 213,672" fill="#fff" stroke="{INK}" stroke-width="2"/>')
    T(s, 225, 666, "H-301", 9.5, 700, "middle")
    pipe(s, [(225, 632), (225, 652)]); T(s, 219, 645, "NaOH/KOH bags", 9, 700, "end")
    PL(s, [(225, 672), (225, 680), (272, 680)], 2.4); arrow(s, 272, 680, "r"); strm(s, 247, 680, 8)
    reactor(s, 300, 665, 56, 62, None, None, False, "#fff", False)
    T(s, 300, 669, "M-301", 10.5, 700, "middle")
    PL(s, [(262, 698), (300, 698)], 2); PL(s, [(300, 686), (300, 706)], 3)
    s.add(f'<circle cx="254" cy="698" r="8" fill="#fff" stroke="{INK}" stroke-width="1.6"/><text x="254" y="701.2" font-size="9" font-weight="700" text-anchor="middle">M</text>')
    bubble(s, 300, 603, "LSH", "311", True); PL(s, [(300, 618), (300, 618)], 1.2)
    PL(s, [(300, 712), (300, 715)], 2.4)
    p3 = rot_pump(s, 300, 727, "v", 12, None); T(s, 282, 752, "P-301", 10, 700, "end")
    PL(s, [p3["o"], (312, 739), (345, 739)], 2.6); strm(s, 330, 739, 9)
    tagl(s, 36, 700, "M-301 catalyst mix tank", "NaOH 10 wt% in MeOH; PVRV-301 (A)"); vent_sym(s, 284, 626, 9)
    tagl(s, 36, 740, "ES-301 shower / eyewash (A)")
    close_dim(s, dim)


def zone_C(s, dim=False):
    """C  reaction and glycerol separation"""
    open_dim(s, dim)
    T(s, 372, 94, "C  REACTION, GLYCEROL SEPARATION", 10, 700, fill=GREY)
    PL(s, [(345, 128), (521, 128)], 2.6)
    for cx, t in ((410, "A"), (545, "B")):
        reactor(s, cx, 250, 76, 120, None, None, True)
        R(s, cx - 27, 244, 54, 30, "#fff", "none"); T(s, cx, 257, "R-301" + t, 10.5, 700, "middle"); T(s, cx, 269, "8 m3 (A)", 8.5, 400, "middle")
        PL(s, [(cx - 24, 128), (cx - 24, 174)], 2.6); valve(s, cx - 24, 150, 270, "ball", act=True, color=RED)
        T(s, cx - 24, 117, "XV-301" + t, 9.5, 700, "middle")
        PL(s, [(cx + 28, 324), (cx + 28, 340)], 2.6)
        psv(s, cx + 26, 150); PL(s, [(cx + 26, 173), (cx + 26, 166)], 2.2)
        PL(s, [(cx + 44, 150), (cx + 58, 150), (cx + 58, 100)], 2.4)
        if t == "B": T(s, cx + 62, 141, "PSV-301B", 9, 700)
        else: T(s, 463, 123, "PSV-301A", 9, 700, "end")
    PL(s, [(468, 100), (640, 100)], 2.4); hvessel(s, 662, 100, 32, 18); T(s, 662, 126, "KO-301", 8.5, 700, "middle")
    PL(s, [(690, 100), (740, 100), (740, 88)], 2.4)
    hop(s, 468, 128)
    s.add(f'<polygon points="740,99 745,94 740,89 735,94" fill="#fff" stroke="{INK}" stroke-width="1.3"/>')
    T(s, 750, 92, "FA-301 + stack, safe loc.", 8.5, 400)
    PL(s, [(372, 214), (362, 214)], 1.8, GREEN); arrow(s, 372, 214, "r", GREEN, 7); T(s, 360, 217, "N2", 9, 700, "end", GREEN)
    PL(s, [(606, 214), (587, 214)], 1.8, GREEN); arrow(s, 587, 214, "l", GREEN, 7); T(s, 609, 217, "N2", 9, 700, "start", GREEN)
    for y, a, b in ((186, "TIC", "301"), (216, "TSHH", "301"), (246, "LT", "301"), (276, "PT", "301")):
        PL(s, [(448, y), (462, y)], 1.2); bubble(s, 477, y, a, b, True)
    to_pipe(s, [(454, 321), (500, 321)], False); valve(s, 477, 321, 0, "gate", act=True, color=TO_C)
    T(s, 477, 336, "TCV-301A/B", 8.5, 700, "middle")
    bubble(s, 606, 250, "AT", "301", True); bubble(s, 606, 284, "BE", "301", True)
    PL(s, [(438, 340), (607, 340)], 2.6); PL(s, [(573, 324), (573, 340)], 2.6)
    p = rot_pump(s, 620, 340, "h", 13, None); T(s, 607, 358, "P-302", 10, 700, "end")
    pipe(s, [p["o"], (633, 215), (652, 215)]); strm(s, 633, 290, 10)
    hvessel(s, 730, 215, 120, 60, None, None)
    T(s, 730, 212, "V-302 settler", 11, 700, "middle"); T(s, 730, 225, "glycerol separation", 9, 400, "middle")
    bubble(s, 705, 150, "LT", "302", True); PL(s, [(705, 165), (705, 188)], 1.2)
    vent_sym(s, 688, 186, 12); T(s, 684, 176, "PVRV-302", 8.5, 700, "end")
    PL(s, [(775, 185), (775, 165), (815, 165), (815, 450), (835, 450)], 2.6); arrow(s, 835, 450, "r"); strm(s, 815, 215, 11)
    PL(s, [(730, 245), (730, 268), (680, 268), (680, 450), (705, 450)], 2.6); arrow(s, 705, 450, "r"); strm(s, 680, 340, 12)
    close_dim(s, dim)


def gl_stub(s, x, y, kind):
    """chilled glycol stub below an exchanger at (x, y)"""
    c = "#6a1b9a"
    if kind == "in":
        PL(s, [(x, y + 16), (x, y)], 1.8, c); arrow(s, x, y, "u", c, 7); T(s, x, y + 27, "GLS", 8.5, 700, "middle", c)
    else:
        PL(s, [(x, y), (x, y + 16)], 1.8, c); arrow(s, x, y + 16, "d", c, 7); T(s, x, y + 27, "GLR", 8.5, 700, "middle", c)


def zone_D(s, dim=False):
    """D  methanol recovery (Rev B): vacuum flashes V-401/V-402 at 0.10 bar(a), glycol-cooled vacuum condenser E-401, receiver V-403,
    vacuum pump VP-401, methanol column package C-401 (E-402, V-404, P-405, E-403), glycerol pump P-404"""
    open_dim(s, dim)
    T(s, 752, 514, "D METHANOL", 10, 700, fill=GREY); T(s, 752, 526, "RECOVERY", 10, 700, fill=GREY)
    for cx, t, sub in ((860, "V-401", "ester flash"), (730, "V-402", "gly. flash")):
        vvessel(s, cx, 410, 50, 80, None, None, 0)
        T(s, cx, 447, t, 10.5, 700, "middle"); T(s, cx, 459, sub, 8.5, 400, "middle"); T(s, cx, 470, "0.10 bar(a)", 8, 400, "middle")
        to_pipe(s, [(cx + 25, 474), (cx + 56, 474)], False); valve(s, cx + 40, 474, 0, "gate", act=True, color=TO_C)
    T(s, 892, 497, "TCV-402", 9, 700); T(s, 762, 497, "TCV-401", 9, 700)
    PL(s, [(860, 396), (860, 364), (530, 364)], 2.6); PL(s, [(730, 396), (730, 364)], 2.6); arrow(s, 532, 364, "l")
    strm(s, 860, 380, 13); strm(s, 730, 380, 14)
    hop(s, 815, 364); hop(s, 680, 364)
    # common relief on the vapour header (PSV-401/402), to KO-301
    PL(s, [(770, 364), (770, 368)], 2.6); psv(s, 770, 352); PL(s, [(788, 352), (798, 352), (798, 326)], 2.4); arrow(s, 798, 326, "u")
    T(s, 758, 334, "PSV-401/402", 8, 700, "end")
    hx(s, 500, 364, 60, 26, None, None)
    gl_stub(s, 516, 377, "in"); gl_stub(s, 484, 377, "out")
    T(s, 545, 396, "E-401", 10, 700); T(s, 545, 407, "vac. condenser", 9, 400); T(s, 545, 418, "chilled glycol 5 C (A)", 8.5, 400)
    PL(s, [(470, 364), (420, 364), (420, 404)], 2.6); arrow(s, 420, 404, "d")
    hvessel(s, 420, 424, 64, 40, None, None)
    T(s, 420, 424, "V-403", 10.5, 700, "middle"); T(s, 420, 437, "0.10 bar(a)", 8, 400, "middle")
    PL(s, [(400, 404), (400, 396), (379, 396)], 2.6); compressor(s, 368, 396, 11, None)
    T(s, 368, 378, "VP-401", 9, 700, "middle")
    pipe(s, [(368, 407), (368, 450)]); strm(s, 368, 427, 15)
    bubble(s, 488, 438, "LT", "403", True); PL(s, [(452, 430), (473, 436)], 1.2)
    PL(s, [(420, 444), (420, 470), (393, 470)], 2.6)
    p4 = rot_pump(s, 380, 470, "l", 13, None); T(s, 412, 482, "P-403", 10, 700)
    # feed to the methanol column
    PL(s, [p4["o"], (367, 615), (578, 615)], 2.6); arrow(s, 578, 615, "r"); strm(s, 367, 540, 23)
    # C-401 package
    R(s, 410, 486, 274, 190, "none", GREY, 1.2, "7 4")
    T(s, 416, 670, "C-401 PACKAGE (A)", 8.5, 700, fill=GREY)
    vvessel(s, 600, 527, 44, 100, None, None, 6)
    T(s, 572, 636, "C-401", 10.5, 700, "end"); T(s, 572, 647, "methanol col.", 8, 400, "end")
    PL(s, [(600, 515), (600, 500), (545, 500)], 2.6)
    hx(s, 517, 500, 56, 22, None, None); T(s, 517, 484, "E-402", 9.5, 700, "middle")
    cw_stub(s, 531, 511, "in"); cw_stub(s, 503, 511, "out")
    PL(s, [(489, 500), (466, 500), (466, 511)], 2.6)
    vvessel(s, 466, 518, 26, 34, None, None, 0); T(s, 451, 531, "V-404", 9, 700, "end")
    bubble(s, 430, 556, "LT", "404", True, r=13); PL(s, [(443, 556), (453, 556)], 1.2)
    PL(s, [(466, 559), (466, 571)], 2.6)
    pp = rot_pump(s, 466, 582, "v", 11, None); T(s, 450, 600, "P-405", 9, 700, "end")
    PL(s, [pp["o"], (560, 593), (560, 545), (578, 545)], 2.6); arrow(s, 578, 545, "r"); T(s, 520, 589, "reflux", 8, 400, "middle")
    PL(s, [(500, 593), (500, 640), (396, 640)], 2.6); arrow(s, 396, 640, "l"); strm(s, 440, 640, 5)
    hop(s, 500, 615)
    T(s, 394, 629, "5 to V-201", 8.5, 400, "end"); T(s, 394, 652, "(L-402)", 8.5, 400, "end")
    bubble(s, 538, 556, "PT", "404", True, r=13); PL(s, [(551, 556), (578, 556)], 1.2)
    vhx(s, 660, 590, 44, 22)
    PL(s, [(660, 568), (660, 557), (622, 557)], 2.6)
    PL(s, [(622, 618), (660, 618), (660, 612)], 2.6)
    PL(s, [(671, 590), (678, 590), (678, 572)], 2.4, TO_C); to_pipe(s, [(678, 572), (730, 572)])
    valve(s, 696, 572, 0, "gate", act=True, color=TO_C); valve(s, 714, 572, 0, "ball", act=True, color=RED)
    T(s, 696, 589, "TCV-404", 8, 700, "middle"); T(s, 716, 599, "XV-401", 8, 700, "middle")
    bubble(s, 655, 648, "TIC", "404", True, r=14); PL(s, [(655, 634), (655, 618)], 1.0, BLUE, "3 3")
    PL(s, [(622, 535), (640, 535)], 2.6); psv(s, 640, 519); PL(s, [(658, 519), (676, 519), (676, 496)], 2.4); arrow(s, 676, 496, "u")
    T(s, 680, 514, "PSV-403", 8, 700)
    PL(s, [(600, 639), (600, 690)], 2.6); arrow(s, 600, 690, "d"); strm(s, 600, 664, 24); T(s, 594, 686, "water to ETP", 8.5, 400, "end")
    bubble(s, 600, 452, "BE", "401", True)
    # existing instruments
    bubble(s, 785, 425, "TIC", "403", True); PL(s, [(755, 425), (770, 425)], 1.2)
    bubble(s, 915, 425, "TIC", "402", True); PL(s, [(885, 425), (900, 425)], 1.2)
    bubble(s, 650, 396, "PT", "401", True); PL(s, [(650, 364), (650, 381)], 1.2)
    bubble(s, 640, 455, "AT", "401", True)
    # glycerol pump
    PL(s, [(730, 504), (730, 513)], 2.6); p5 = rot_pump(s, 730, 524, "v", 11, None); T(s, 716, 530, "P-404", 9.5, 700, "end")
    PL(s, [p5["o"], (741, 604)], 2.6); arrow(s, 741, 604, "d"); strm(s, 741, 568, 17)
    close_dim(s, dim)


def zone_E(s, dim=False):
    """E  wash, drying, product"""
    open_dim(s, dim)
    PL(s, [(860, 490), (860, 534)], 2.6); strm(s, 860, 515, 16)
    p = rot_pump(s, 860, 546, "v", 12, None); T(s, 842, 572, "P-402", 10, 700, "end")
    PL(s, [p["o"], (872, 565)], 2.6)
    vhx(s, 872, 590, 50, 22)
    T(s, 852, 596, "E-501 cooler, CW", 9.5, 700, "end")
    PL(s, [(872, 615), (872, 639)], 2.6); arrow(s, 872, 639, "d")
    PL(s, [(790, 627), (872, 627)], 2.2, CWC); arrow(s, 866, 627, "r", CWC, 7)
    valve(s, 838, 627, 0, "gate", act=True); T(s, 836, 610, "FCV-501", 9.5, 700, "middle")
    T(s, 790, 616, "PW", 9, 700, "start", CWC); strm(s, 810, 627, 18)
    vvessel(s, 872, 655, 56, 70, None, None, 0)
    T(s, 872, 692, "C-501", 10.5, 700, "middle"); T(s, 872, 704, "wash col.", 9, 400, "middle"); vent_sym(s, 893, 645, 9); T(s, 900, 639, "PVRV-501", 8, 700)
    bubble(s, 822, 722, "LIC", "501", True); PL(s, [(837, 722), (846, 722)], 1.2)
    PL(s, [(872, 741), (872, 756), (800, 756)], 2.4); arrow(s, 800, 756, "l"); strm(s, 838, 756, 19)
    bubble(s, 908, 742, "AT", "501", True); PL(s, [(893, 742), (872, 742)], 1.0, BLUE, "3 3")
    T(s, 796, 753, "wash water", 9, 400, "end"); T(s, 796, 764, "to ETP", 9, 400, "end")
    pipe(s, [(900, 690), (942, 690)]); strm(s, 921, 690, 20)
    vvessel(s, 970, 655, 56, 70, None, None, 0)
    T(s, 970, 692, "V-601", 10.5, 700, "middle"); T(s, 970, 704, "vac. dryer", 9, 400, "middle")
    PL(s, [(998, 664), (1020, 664), (1020, 666)], 2.6); psv(s, 1020, 650); PL(s, [(1038, 650), (1046, 650)], 2.4); T(s, 1002, 676, "PSV-601", 8, 700)
    to_pipe(s, [(998, 722), (1026, 722)], False); valve(s, 1012, 722, 0, "gate", act=True, color=TO_C)
    T(s, 1012, 742, "TCV-601", 9, 700, "middle"); T(s, 1012, 752, "TOS/TOR", 8.5, 400, "middle", TO_C)
    PL(s, [(970, 639), (970, 618), (952, 618), (952, 604)], 2.4)
    R(s, 912, 564, 80, 40, "#fff", INK, 1.8)
    T(s, 952, 581, "VP-601", 10.5, 700, "middle"); T(s, 952, 594, "condenser + pump", 8.5, 400, "middle")
    pipe(s, [(952, 564), (952, 520)]); strm(s, 952, 542, 21); T(s, 944, 524, "condensate", 9, 400, "end"); T(s, 944, 535, "to ETP", 9, 400, "end")
    PL(s, [(998, 690), (1036, 690)], 2.6)
    pr = rot_pump(s, 1048, 690, "h", 12, None); T(s, 1048, 716, "P-601", 10, 700, "middle")
    PL(s, [pr["o"], (1060, 642)], 2.6)
    vhx(s, 1060, 620, 44, 20)
    T(s, 1046, 614, "E-602", 10, 700, "end"); T(s, 1046, 625, "cooler, CW", 9, 400, "end")
    PL(s, [(1060, 598), (1060, 565)], 2.6); strm(s, 1060, 583, 22)
    PL(s, [(1060, 565), (1030, 565), (1030, 541)], 2.6); PL(s, [(1060, 565), (1090, 565), (1090, 541)], 2.6)
    pipe(s, [(1030, 565), (1004, 565)]); T(s, 1000, 557, "dispatch", 9, 400, "end")
    for cx, tg in ((1030, "T-701A"), (1090, "T-701B")):
        tank(s, cx, 540, 44, 80, None, None, "cone", 0.5, "#fff3c4")
        T(s, cx, 505, tg, 9.5, 700, "middle"); vent_sym(s, cx + 13, 456, 9)
    bubble(s, 986, 488, "LT", "701", True); PL(s, [(1001, 488), (1008, 488)], 1.2)
    T(s, 1060, 430, "PVRV-701A/B", 8.5, 700, "middle")
    close_dim(s, dim)


def zone_G(s, dim=False):
    open_dim(s, dim)
    tank(s, 730, 700, 90, 84, None, None, "cone", 0.5, "#e8f5e9")
    T(s, 730, 668, "T-801", 11, 700, "middle"); T(s, 730, 681, "crude glycerol", 9, 400, "middle"); vent_sym(s, 752, 611, 9); T(s, 764, 601, "PVRV-801", 8, 700)
    PL(s, [(775, 683), (800, 683)], 2.6); arrow(s, 800, 683, "r"); T(s, 778, 676, "to tanker", 9, 400)
    bubble(s, 664, 665, "LT", "801", True); PL(s, [(679, 665), (685, 665)], 1.2)
    close_dim(s, dim)


def zone_F(s, dim=False):
    """F  thermopack utility stub"""
    open_dim(s, dim)
    T(s, 905, 95, "F  THERMOPACK (utility stub)", 10, 700, fill=GREY)
    R(s, 1030, 140, 80, 110, "#fff4e0", TO_C, 2.4)
    pts = [(1042, 160)]
    for i in range(6): pts.append((1098 if i % 2 == 0 else 1042, 160 + (i + 1) * 12))
    PL(s, pts, 1.8, TO_C)
    s.add(f'<path d="M1070,250 Q1062,262 1070,271 Q1078,262 1070,250 Z" fill="url(#flame)" stroke="{RED}" stroke-width="1"/>')
    PL(s, [(1070, 140), (1070, 126)], 3); T(s, 1078, 128, "stack", 9, 400)
    R(s, 1046, 224, 48, 16, "#fff4e0", "none"); T(s, 1070, 236, "H-901", 11, 700, "middle")
    PL(s, [(1070, 312), (1070, 272)], 2.2, RED); arrow(s, 1070, 316, "u", RED, 7); valve(s, 1070, 292, 90, "ball", act=True, color=RED)
    T(s, 1056, 290, "XV-901", 9.5, 700, "end"); T(s, 1056, 301, "fuel shut-off", 9, 400, "end"); T(s, 1070, 322, "fuel (type TBD) / air", 9, 400, "middle")
    PL(s, [(1030, 160), (900, 160)], 2.4, TO_C); arrow(s, 900, 160, "l", TO_C, 8)
    T(s, 905, 153, "TOS to users", 9, 400, fill=TO_C)
    PL(s, [(900, 232), (962, 232)], 2.4, TO_C); arrow(s, 962, 232, "r", TO_C, 8); T(s, 902, 224, "TOR return", 9, 400, fill=TO_C)
    pp = rot_pump(s, 975, 232, "h", 12, None); T(s, 975, 258, "P-901A/B", 10, 700, "middle")
    PL(s, [pp["o"], (1000, 220), (1000, 236), (1030, 236)], 2.4, TO_C); arrow(s, 1030, 236, "r", TO_C, 8)
    vvessel(s, 1000, 108, 36, 30, None, None, 0); T(s, 1000, 125, "V-901", 9, 700, "middle")
    PL(s, [(1000, 152), (1000, 160)], 2.2, TO_C)
    bubble(s, 940, 200, "TSHH", "901", True); PL(s, [(940, 160), (940, 185)], 1.0, BLUE, "3 3")
    bubble(s, 925, 285, "FSLL", "901", True); PL(s, [(925, 232), (925, 270)], 1.0, BLUE, "3 3")
    close_dim(s, dim)


def zone_S(s, dim=False):
    """ESD logic, nitrogen stub"""
    open_dim(s, dim)
    R(s, 400, 708, 240, 56, "#fff3e0", RED, 1.8)
    T(s, 520, 728, "ESD-101  ESD + FIRE & GAS LOGIC (A)", 10, 700, "middle", RED)
    T(s, 520, 744, "red valves = ESD, fail-closed; matrix on sheet 7", 9, 400, "middle", RED)
    R(s, 654, 712, 90, 52, "#e8f5e9", GREEN, 1.4)
    for i, (t, w) in enumerate((("N2 SUPPLY (A)", 700), ("PCV + PAL-951", 400), ("to T-201, V-201,", 400), ("M-301, R-301A/B", 400))):
        T(s, 699, 723 + i * 10.5, t, 8, w, "middle", GREEN)
    close_dim(s, dim)


def pid(s, dim=()):
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    zone_A(s, "A" in dim); zone_B(s, "B" in dim); zone_C(s, "C" in dim); zone_D(s, "D" in dim)
    zone_E(s, "E" in dim); zone_G(s, "G" in dim); zone_F(s, "F" in dim); zone_S(s, "S" in dim)


# =====================================================================================================  table helper
def wtable(s, x, y, colw, rows, size=9.5, lh=11.5, pad=3, head=True, fills=None):
    """table with wrapped cells; returns y below"""
    cpc = size * 0.53
    ncol = [max(4, int((w - 8) / cpc)) for w in colw]
    tw = sum(colw)
    yy = y
    for i, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), ncol[j]) or [""] for j, c in enumerate(r)]
        rh = max(len(c) for c in cells) * lh + 2 * pad
        if head and i == 0: R(s, x, yy, tw, rh, "#e8eaf0", "none")
        elif i % 2 == 0: R(s, x, yy, tw, rh, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cells):
            for k, t in enumerate(c):
                T(s, cx + 4, yy + pad + lh * (k + 1) - 2.5, t, size, 700 if (head and i == 0) else 400)
            cx += colw[j]
        yy += rh
    R(s, x, y, tw, yy - y, "none", "#9aa", 1)
    return yy


# =====================================================================================================  sheet 1: P&ID
LEG_Y = 84


def legend(s, x, y, w):
    y = section(s, x, y, w, "LEGEND")
    R(s, x, y, w, 138, "#fff", "#889", 1)
    c1, c2 = x + 10, x + 228
    yy = y + 16
    PL(s, [(c1, yy), (c1 + 34, yy)]); T(s, c1 + 40, yy + 4, "process line", 9.5)
    PL(s, [(c2, yy), (c2 + 34, yy)], 2.4, TO_C); T(s, c2 + 40, yy + 4, "thermal oil TOS / TOR", 9.5)
    yy += 19
    PL(s, [(c1, yy), (c1 + 34, yy)], 2.2, CWC); T(s, c1 + 40, yy + 4, "cooling water / glycol / PW", 9.5)
    PL(s, [(c2, yy), (c2 + 34, yy)], 1.8, GREEN); T(s, c2 + 40, yy + 4, "nitrogen (N2)", 9.5)
    yy += 19
    PL(s, [(c1, yy), (c1 + 34, yy)], 1.2, BLUE, "5 4"); T(s, c1 + 40, yy + 4, "instrument signal", 9.5)
    valve(s, c2 + 17, yy, 0, "ball", act=True, color=RED); T(s, c2 + 40, yy + 4, "ESD valve, fail-closed (A)", 9.5)
    yy += 24
    psv(s, c1 + 10, yy + 6); T(s, c1 + 40, yy + 4, "PSV to vent header", 9.5)
    valve(s, c2 + 17, yy, 0, "gate", act=True, color=TO_C); T(s, c2 + 40, yy + 4, "control valve (thermal oil)", 9.5)
    yy += 26
    bubble(s, c1 + 14, yy, "LT", "101", True, r=13); T(s, c1 + 40, yy + 4, "instrument, logic-mounted", 9.5)
    strm(s, c2 + 17, yy, 7); T(s, c2 + 40, yy + 4, "stream no. = HMB column", 9.5)
    yy += 22
    R(s, c1, yy - 5, 34, 10, "none", AMBER, 1.2, "5 3"); T(s, c1 + 40, yy + 4, "bund / area (A)", 9.5)
    vent_sym(s, c2 + 17, yy + 6, 10); T(s, c2 + 40, yy + 4, "vent + flame arrester", 9.5)
    return y + 138


EQUIP = [("Tag", "Description", "Basis"),
         ("UC-101", "UCO tanker unloading connection", "A"),
         ("T-101, PVRV-101", "UCO receipt tank, breather valve", "S3, A"),
         ("P-101", "UCO transfer pump", "S3 (pumps)"),
         ("F-101", "UCO filter, cake = MIU (stream 2)", "S2 (filtration)"),
         ("E-101", "UCO heater 30 to 40 C, thermal oil", "S2 (pre-heat)"),
         ("T-201, PVRV-201", "Methanol tank, PESO licence, breather + FA", "S1, R, A"),
         ("P-201/202", "Methanol transfer / dosing pumps", "A"),
         ("V-201, PVRV-202", "Methanol dosing tank, N2 blanket", "A"),
         ("H-301", "NaOH/KOH bag-tipping hopper", "A"),
         ("M-301, PVRV-301", "Catalyst mix tank, agitated, vent", "A"),
         ("P-301", "Catalyst solution pump", "A"),
         ("R-301A/B", "Batch reactors, jacketed, 8 m3", "S3 (form A)"),
         ("PSV-301A/B", "Reactor relief to KO-301", "A"),
         ("KO-301, FA-301", "Vent catch pot, flame arrester, stack", "A"),
         ("P-302", "Reactor discharge pump", "A"),
         ("V-302, PVRV-302", "Settler, glycerol separation, vent", "S3, A"),
         ("V-401, V-402", "Vacuum flashes 0.10 bar(a), 80 C, TO coil", "Rev B, D"),
         ("PSV-401/402", "V-401/402 header relief to KO-301", "A"),
         ("E-401", "Vacuum condenser, chilled glycol 5 C", "Rev B, D"),
         ("RU-401", "Glycol chiller package (vendor, off sheet)", "A"),
         ("V-403, P-403", "Wet methanol receiver (0.10 bar) / pump", "A"),
         ("VP-401", "Vacuum pump package, V-403 vent", "A"),
         ("C-401 package", "Methanol column, reflux 3.665", "S98, Rev B"),
         ("E-402, V-404", "Column condenser (CW), reflux drum", "A"),
         ("E-403, P-405", "Column reboiler (TO), reflux pump", "A"),
         ("PSV-403", "C-401 relief to KO-301", "A"),
         ("P-402", "Stripped ester pump", "A"),
         ("P-404", "Crude glycerol pump (V-402 to T-801)", "Rev B, A"),
         ("E-501", "Ester cooler 80 to 60 C, CW", "A"),
         ("C-501, PVRV-501", "Water wash column, 20 % wash", "S98, A"),
         ("V-601, PSV-601", "Vacuum dryer, relief", "A"),
         ("VP-601, P-601", "Vacuum package, product pump", "A"),
         ("E-602", "Product cooler 60 to 40 C, CW", "A"),
         ("T-701A/B", "B100 product tanks, IS 15607 test", "S2, S3"),
         ("PVRV-701A/B", "Breather valves on T-701A/B", "A"),
         ("T-801, PVRV-801", "Crude glycerol tank, vent", "S3, A"),
         ("H-901", "Thermopack, thermal oil heater", "S1 (utilities)"),
         ("P-901A/B, V-901", "TO circulation pumps, expansion tank", "A"),
         ("XV-201/202/203", "T-201 outlet / dose / fill ESD valves", "A"),
         ("XV-301A/B, XV-901", "Reactor inlet / fuel ESD valves", "A"),
         ("XV-401", "C-401 reboiler TO ESD valve", "A"),
         ("TCV-xxx", "TO control valves 102, 301, 401 to 404, 601", "A"),
         ("AT / BE", "Gas / flame detectors 201, 301, 401", "A"),
         ("ESD-101, ES-301", "ESD + F&G logic; shower / eyewash", "A")]
LINES = [("Line", "From > to", "Service", "Stream", "Size"),
         ("L-101", "UC-101 > T-101", "UCO", "1", "TBD (A)"),
         ("L-102", "T-101 > P-101 > F-101 > E-101 > charge header", "UCO, filtered", "3 (2)", "TBD (A)"),
         ("L-201", "T-201 > P-201 > V-201", "methanol", "4", "TBD (A)"),
         ("L-202", "V-201 > P-202 > riser > charge header", "methanol dose", "6, 7", "TBD (A)"),
         ("L-203", "H-301 > M-301 > P-301 > riser", "NaOH, cat. solution", "8, 9", "TBD (A)"),
         ("L-301", "charge header > R-301A/B (batch sequence)", "oil, MeOH, cat.", "3, 6, 9", "TBD (A)"),
         ("L-302", "R-301A/B > P-302 > V-302", "reactor effluent", "10", "TBD (A)"),
         ("L-303/304", "V-302 > V-401 (ester) / V-402 (glycerol)", "ester / glycerol phase", "11, 12", "TBD (A)"),
         ("L-401", "V-401/402 > E-401 > V-403 (0.10 bar(a))", "MeOH/H2O vapour", "13, 14", "TBD (A)"),
         ("L-402", "V-403 > P-403 > C-401 > V-201", "wet / dry methanol", "23, 5", "TBD (A)"),
         ("L-403", "V-403 > VP-401 > vent; C-401 > ETP", "exhaust; bottoms", "15, 24", "TBD (A)"),
         ("L-501", "V-401 > P-402 > E-501 > C-501", "stripped ester", "16", "TBD (A)"),
         ("L-502", "PW > C-501 > ETP", "wash water in / out", "18, 19", "TBD (A)"),
         ("L-503", "C-501 > V-601 > P-601 > E-602 > T-701A/B", "wet / dry biodiesel", "20, 22", "TBD (A)"),
         ("L-504", "V-601 > VP-601 > ETP", "dryer vapour / condensate", "21", "TBD (A)"),
         ("L-601", "V-402 > P-404 > T-801 > tanker", "crude glycerol", "17", "TBD (A)"),
         ("L-701", "PSV-301A/B, 401/402, 403 > KO-301 > FA-301 > stack", "relief vent", "-", "TBD (A)"),
         ("L-901", "H-901 > users > H-901 (TOS / TOR)", "thermal oil", "-", "TBD (A)")]

CE = [("Initiator (voting TBD, A)", "XV-201", "XV-202", "XV-203", "XV-301A/B", "TCV-301", "XV-901", "XV-401"),
      ("AT-201A/B gas HH", "close", "close", "close", "-", "-", "-", "-"),
      ("BE-201 / BE-301 flame", "close", "close", "close", "close", "close", "close", "close"),
      ("AT-301 gas HH", "-", "close", "-", "close", "close", "close", "-"),
      ("TSHH-301 / PAHH-301", "-", "close", "-", "close", "close", "close", "-"),
      ("TSHH-901 / FSLL-901", "-", "-", "-", "-", "-", "close", "-"),
      ("LSHH-201 tank level", "-", "-", "close", "-", "-", "-", "-"),
      ("AT-401 gas / BE-401, PAHH-404", "-", "-", "-", "-", "-", "-", "close")]


def sheet_pid():
    s = Sheet(1, "BIODIESEL (B100) 20 KLPD: P&ID, batch transesterification, vacuum methanol recovery, thermopack",
              "P&ID, whole process", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="DPR files S1 to S3, sourced Rev B values, HMB on sheet 2")
    frame(s, TOTAL)
    pid(s)
    panel_box(s)
    y = legend(s, 1135, 84, 445)
    y = section(s, 1135, y + 8, 445, "EQUIPMENT AND DEVICE LIST (basis: S = DPR file, R, A)")
    table(s, 1135, y, (112, 238, 95), EQUIP, 12.1, 8.4)
    y = section(s, 20, 784, 560, "LINE LIST (sizes TBD, A)")
    y = wtable(s, 20, y, (58, 232, 120, 62, 88), LINES, 9, 10.4, 1.4)
    y2 = section(s, 600, 784, 520, "CAUSE AND EFFECT, short form (full matrix, SIFs, instrument index: sheet 7)")
    y2 = wtable(s, 600, y2, (150, 52, 52, 52, 62, 58, 52, 42), CE, 8.2, 10.2, 1.8)
    yk = 84 + 866 - 118
    WRAP(s, 1141, yk + 2, "Basis key. S1 Template_DPR_Biodiesel_B100_20KLPD.docx; S2 Owner_20KLPD_Draft_DPR_v2.docx (private draft, not in repo); S3 Biodiesel_18000KL_Sample_DPR_v2.docx (process-safety-design-toolkit repo). S98 Sheehan et al. NREL/SR-580-24089 (1998). R = DPR risk line 'PESO-compliant tanks, fire-fighting, hazard study'. A = assumed by this drawing: every ESD valve, detector, relief device, N2 blanket and bund is A.", 78, 8.6, 10.2)
    notes = [
        "Rev B: V-401/V-402 run at 0.10 bar(a) (Rev A 1.0 bar did not close); the vapour carries water, so a methanol column C-401 dries it. Chilled glycol is needed because methanol saturates at 15.2 C at 0.10 bar (CW cannot condense it). Wash C-501 (20 %) is chosen, not the DPR no-wash scheme (sheet 3).",
        "FFA 1 wt% is a feed acceptance limit; oil above 1 % needs acid esterification (not drawn). Reactor 8 m3 (6.1 m3 working volume); R-301B carries the same instruments, valves and PSV as R-301A. Tank, vessel and line sizes TBD.",
    ]
    for n in notes: y2 = WRAP(s, 600, y2 + 8, n, 118, 8.6, 10.2)
    return s


glyp_pct = ST[17]["GLY"] / tot(ST[22]) * 100
Vw = (ST[3]["TG"] + ST[3]["FFA"] + ST[3]["H2O"]) / 920.0 + (ST[6]["MeOH"] + ST[9]["MeOH"]) / 790.0   # D m3 of oil + methanol charge (A densities)

# =====================================================================================================  sheet 2: HMB
PATH = "process-safety-design-toolkit/"
SHORT = {1: "UCO", 2: "cake", 3: "oil", 4: "MeOH new", 5: "MeOH dry", 6: "MeOH dose", 7: "MeOH cat", 8: "NaOH", 9: "cat soln", 10: "effluent",
         11: "ester ph", 12: "gly ph", 13: "vap 80C", 14: "vap 80C", 15: "VP exh.", 16: "str. ester", 17: "crude gly", 18: "wash H2O",
         19: "wash out", 20: "wet BD", 21: "dry vap", 22: "B100", 23: "MeOH wet", 24: "col btms"}


def pct(v):
    if v <= 0: return "-"
    if v < 0.05: return "<0.1"
    if v >= 99.95: return "100"
    return f"{v:.1f}"


def sheet_hmb():
    s = Sheet(2, "HEAT AND MATERIAL BALANCE (Rev B): biodiesel 20 KLPD, per batch and per hour",
              "HMB, streams 1 to 24", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="DPR files S1 to S3; Rev B sourced values; assumptions on sheet 3")
    frame(s, TOTAL)
    ids = sorted(ST)
    rows = [("Stream name", [SHORT[i] for i in ids]),
            ("From (equipment tag)", [SD[i][1] for i in ids]),
            ("To (equipment tag)", [SD[i][2] for i in ids]),
            ("Phase (L liquid, V vapour, S solid)", [SD[i][3] for i in ids]),
            ("Temperature, C (A)", [str(SD[i][4]) for i in ids]),
            ("Pressure, bar(a) (A)", [f"{SD[i][5]:.2f}" if SD[i][5] < 0.5 else f"{SD[i][5]:.1f}" for i in ids]),
            ("FLOW (D)", None),
            ("Mass flow, kg/batch", [fmt(tot(ST[i]), 1) for i in ids]),
            (f"Mass flow, kg/h (24 h avg, batch / {HR:.0f} h)", [fmt(H(tot(ST[i])), 1) for i in ids]),
            ("COMPOSITION, mass % (D)", None)]
    for sp in SP:
        rows.append((SPN[sp], [pct(100 * ST[i].get(sp, 0) / tot(ST[i])) for i in ids]))
    rows.append(("Sum, %", ["100.0"] * len(ids)))
    y = hmb_table(s, 20, 84, ids, rows, first_w=205, col_w=55, rh=15.6, size=9, title="STREAM TABLE: numbers match the diamonds on sheet 1 (one batch = one period of 6 h; 4 batches per day)")
    yL = section(s, 20, y + 10, 600, "CLOSURE (computed in code, asserted)")
    yy = yL + 17
    T(s, 28, yy, f"Closure: in {fmt(H(m_in), 2)} kg/h, out {fmt(H(m_out), 2)} kg/h, error {abs(ERR):.2f} %   ({fmt(m_in, 1)} kg/batch in, {fmt(m_out, 1)} kg/batch out)", 11, 700, fill=GREEN)
    yy += 15
    T(s, 28, yy, "Boundary: in = streams 1, 4, 8, 18; out = streams 2, 15, 17, 19, 21, 22, 24. Others internal (methanol loop 23, 5 closes at V-201).", 8.6, 400, fill=GREY)
    yy += 14
    T(s, 28, yy, "Element check, kmol/batch in / out:  " + "   ".join(f"{e} {E_IN[e]:,.3f} / {E_OUT[e]:,.3f}" for e in ("C", "H", "O", "Na")), 9.5, 400)
    yy += 14
    T(s, 28, yy, f"Reaction identity (D): TG + 3 MeOH = 3 FAME + GLY :  {MW['TG']:.2f} + {3*MW['MeOH']:.2f} = {3*MW['FAME']:.2f} + {MW['GLY']:.2f} kg/kmol (difference {MW['TG']+3*MW['MeOH']-3*MW['FAME']-MW['GLY']:.0e})", 9, 400)
    yy += 8
    urows = [("Unit balance (in = out, kg/batch)", "kg", "Unit balance", "kg")]
    keys = list(UNIT_ERR)
    half = (len(keys) + 1) // 2
    for k in range(half):
        a = keys[k]; b = keys[k + half] if k + half < len(keys) else None
        urows.append((a, fmt(UNIT_ERR[a][0], 1), b or "", fmt(UNIT_ERR[b][0], 1) if b else ""))
    yy = table(s, 20, yy, (190, 90, 190, 90), urows, 14.2, 9)
    yy += 6
    T(s, 22, yy + 10, "Molar masses (D), kg/kmol: " + ", ".join(f"{k} {MW[k]:.2f}" for k in ("TG", "FFA", "MeOH", "NaOH", "FAME", "GLY", "SOAP", "H2O")), 8, 400, fill=GREY)
    yD = section(s, 20, yy + 18, 600, "DUTIES (D; species heat capacities and latent heats frozen from tool runs, sheet 3)")
    drows = [("Service", "MJ/batch", "kW avg")]
    for k, v in Q.items(): drows.append((k, fmt(v / 1000, 1), fmt(kW(v), 1)))
    drows.append(("Total thermal oil (TO) duty at users", fmt(Q_TO / 1000, 1), fmt(kW(Q_TO), 1)))
    drows.append(("Total cooling water (CW) duty", fmt(Q_CW / 1000, 1), fmt(kW(Q_CW), 1)))
    drows.append(("Total chilled glycol (CH) duty (new utility)", fmt(Q_CH / 1000, 1), fmt(kW(Q_CH), 1)))
    yD = table(s, 20, yD, (390, 105, 105), drows, 13.6, 8.8)
    T(s, 22, yD + 11, "Not computed: reaction heat, heat loss, thermopack fuel and efficiency, column stage count (open data).", 8.2, fill=GREY)
    # Rev A to Rev B changes
    fa = lambda x: fmt(x, 0)
    rb = lambda k: Q[[q for q in Q if q.startswith(k)][0]] / 1000
    ch = [("Item", "Rev A", "Rev B", "Source", "Effect on closure and duties"),
          ("V-401 ester methanol recovery", "99.5 % at 80 C, 1.0 bar(a) (A11); recompute 14.5 %", f"{FL['E_M']*100:.1f} % MeOH, {FL['E_W']*100:.0f} % of water, at 80 C, {FLASH_P:.2f} bar(a)", "D: UNIFAC-Dortmund flash (frozen); [AL14] about 90 % at 0.2 atm, GAP_CLOSURE_BIO", f"Closure kept (0.00 %); residual MeOH to wash (19) and dryer (21). V-401 duty {REV_A['V-401 coil']:.0f} to {rb('V-401'):.0f} MJ/batch"),
          ("V-402 glycerol-phase recovery", "99.5 % at 1.0 bar (needs 0.011 bar)", f"{FL['G_M']*100:.1f} % MeOH, {FL['G_W']*100:.0f} % of water at 0.10 bar(a)", "D: same run (salts and soap ignored)", f"V-402 duty {REV_A['V-402 coil']:.0f} to {rb('V-402'):.0f}; crude glycerol 2,415 to {fa(DAY[17])} kg/d"),
          ("Condensing at 0.10 bar", "CW condenser 80 to 40 C", f"Chilled glycol 5 C; methanol Tsat {TSAT_M_01} C at 0.10 bar", "D: CoolProp 8.0", f"E-401 {REV_A['E-401 cond']:.0f} to {rb('E-401'):.0f} MJ on a new CH utility; VP-401 + RU-401 added"),
          ("Methanol loop", "Condensate straight to V-201 (stream 5)", "V-403 > C-401 column > V-201; new streams 23, 24", f"S: [S98] 5.5.1.5 reflux {COL_REFLUX}, bottoms <0.5 % MeOH, distillate <0.05 % water", f"Reboiler {rb('E-403'):.0f} MJ (TO), E-402 {rb('E-402'):.0f} MJ (CW); fresh MeOH {fa(REV_A['fresh MeOH kg/d'])} to {fa(DAY[4])} kg/d"),
          ("FFA in oil, single-stage NaOH", "2.0 wt% (A1)", "1.0 wt% feed limit; above it acid esterification pretreatment (not drawn)", "S: [VG04] FFA above about 1 % must be pretreated", f"Soap in stream 17 {REV_A['soap % of 17']:.1f} to {100*ST[17]['SOAP']/tot(ST[17]):.1f} %; NaOH use unchanged"),
          ("Wash water", "5 % of ester (A13)", f"{WASH_FRAC*100:.0f} % of ester, 5 % of aqueous phase carried to dryer", "S: [S98] p.148", f"Effluent 19: {fa(REV_A['wash kg/d'])} to {fa(DAY[19])} kg/d; dryer {REV_A['V-601']:.0f} to {rb('V-601'):.0f} MJ/batch"),
          ("Heat capacity of ester", "2.0 kJ/kg/K for all organics (A18)", "FAME 2.28, oil 2.04, glycerol 2.55 (species)", "D: thermo 0.6.1 Cpl, CoolProp", f"E-501 {REV_A['E-501']:.0f} to {rb('E-501'):.0f}; E-602 {REV_A['E-602']:.0f} to {rb('E-602'):.0f} MJ/batch"),
          ("Latent heats", "MeOH 1,100, water 2,300 (A19)", "MeOH 1,069 (80 C), 1,101 (64.5 C); water 2,314 / 2,358", "D: CoolProp 8.0", "Duties above use these"),
          ("Vent loss", "0.2 % of methanol vapour (A12)", f"{A['VENT']*100:.0f} % at VP-401 exhaust (A, range 0.2 to 2 %)", "A: depends on leak rate, 5 C outlet", f"Stream 15 {fmt(tot(ST[15]),1)} kg/batch"),
          ("Crude glycerol basis", "13.7 % of B100, note missing", f"{DAY[17]/DAY[22]*100:.1f} % of B100 crude; pure glycerol {glyp_pct:.1f} % (DPR 10 % is this basis)", "S: [S98] Table 13 0.15 kg/kg crude", "Basis stated; no closure effect"),
          ("Totals TO / CW", f"{REV_A['TO total']:.0f} / {REV_A['CW total']:.0f} MJ/batch", f"{Q_TO/1000:.0f} / {Q_CW/1000:.0f} MJ/batch; CH {Q_CH/1000:.0f}", "D", "Thermopack and cooling loads rise; new chilled-glycol load")]
    yR = section(s, 640, y + 10, 940, "REV A TO REV B CHANGES (item | Rev A | Rev B | source | effect on closure / duties)")
    wtable(s, 640, yR, (125, 155, 235, 215, 210), ch, 8.2, 9.8, 1.8)
    return s


def sheet_basis():
    s = Sheet(3, "HMB BASIS (Rev B): assumptions, sourced values, methanol-recovery and column basis",
              "HMB basis, assumptions A1 to A27", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="DPR files S1 to S3; S98, VG04, AL14; frozen tool runs")
    frame(s, TOTAL)
    y2 = section(s, 20, 84, 600, "ASSUMED, to be confirmed by licensor or vendor (A)")
    arows = [("ID", "Assumption", "Value"),
             ("A1", "Oil as received FFA (as oleic acid); S limit 1 % [VG04] (Rev A 2.0 %)", "1.0 wt%"),
             ("A2", "Oil as received: water", "0.5 wt%"),
             ("A3", "Triglyceride = triolein, FAME = methyl oleate (UCO profile not in DPR)", "model"),
             ("A4", "Triglyceride conversion in R-301 (98 % reported, [S98])", "98 %"),
             ("A5", "Methanol : triglyceride mole ratio (6:1 most common, [VG04])", "6 : 1"),
             ("A6", "Catalyst NaOH, 10 wt% in methanol in M-301 (KOH / methoxide not stated)", "10 wt%"),
             ("A7", "Batches per day: 2 reactors x 2 batches per 12 h cycle", "4"),
             ("A8", "Unreacted methanol to glycerol phase in V-302", "70 %"),
             ("A9", "Water to glycerol phase in V-302", "90 %"),
             ("A10", "Glycerol, soap, NaOH wholly to glycerol phase; FAME, TG to ester phase", "100 %"),
             ("A11", f"V-401/402 pressure, design choice (UNIFAC 90 % at 0.2, 95 % at 0.1, 99 % at 0.02 bar)", f"{FLASH_P:.2f} bar(a)"),
             ("A12", "Methanol lost with VP-401 exhaust (range 0.2 to 2 %)", f"{A['VENT']*100:.0f} %"),
             ("A13", "Wash 20 % and 5 % carry-over are S [S98]; wash temperature 60 C is A", "S / A"),
             ("A14", "Water in dry biodiesel (IS 15607 limit not read)", "0.05 %"),
             ("A15", "MIU wholly removed as cake in F-101", "100 %"),
             ("A16", "Temperatures: ambient / flash / wash and dry / tanks (reactor 40 is S)", "30/80/60/40 C"),
             ("A17", "Pressures: tanks 1.0 to 1.1, pumped lines 3.0, C-401 feed 1.5, dryer 0.2", "bar(a)"),
             ("A18", "Heat capacities NaOH 1.5, soap 2.0, MIU 2.0 (others D, frozen)", "kJ/kg/K"),
             ("A19", "Reflux ratio basis (3.665 S) taken molar; column stage count not computed", "gap"),
             ("A20", "Reaction heat, heat loss and heat integration neglected", "0"),
             ("A21", "Density for volumes: oil 0.92, methanol 0.79 t/m3; reactor fill 80 %", "-"),
             ("A22", f"Reactor size, rounded up from working volume {Vw:.1f} m3 / 0.8", "8 m3 each"),
             ("A23", "Glycol / chilled supply 5 C at E-401; condenser outlet 5 C", "5 C"),
             ("A24", "Column feed 5 C, bottoms 99 C (water-rich, 1 atm), distillate cooled to 40 C", "C"),
             ("A25", "Salts, soap and NaOH do not alter V-402 volatilities (UNIFAC on MeOH/H2O/glycerol only)", "caveat"),
             ("A26", "Recovered methanol meets reactor water limit at 0.05 % (S98 spec)", "0.05 %"),
             ("A27", "Fresh methanol is dry", "0 % water")]
    y2 = wtable(s, 20, y2, (36, 470, 94), arows, 8.6, 10.2, 1.4)
    y2 = section(s, 20, y2 + 8, 600, "OBSERVATIONS AND OPEN ITEMS")
    obs = [f"DPR crude glycerol 10 % of B100 is a pure-glycerol basis (here {glyp_pct:.1f} %); crude incl. soap, NaOH, residual water and methanol is {DAY[17]/DAY[22]*100:.1f} % (D); [S98] Table 13 gives 0.15 kg/kg.",
           f"Fresh methanol {fmt(DAY[4])} kg/d is {(DAY[4]/(DPR['meoh_t_yr']*1000/DPR['days'])-1)*100:+.1f} % against the DPR 11 % line.",
           "Conversion 98 % leaves 2 % triglyceride in B100: ester content against IS 15607 is not checked (limits not read).",
           "Crude glycerol leaves V-402 at 80 C into an atmospheric tank; no cooler is drawn (open).",
           "Wash (S98) conflicts with the DPR no-wash scheme and creates ETP load; with no wash the soap/Na/glycerol control of B100 would need a stated alternative (not read).",
           "N2 blanket, vent and relief flows are not in this balance (intermittent; vendor)."]
    y2 += 10
    for o in obs: y2 = WRAP(s, 26, y2, o, 118, 8.8, 10.4, bullet=True) + 3
    x3 = 640
    y3 = section(s, x3, 84, 480, "SOURCED (S): DPR files and published documents")
    srows = [("Item", "Value", "Source"),
             ("Capacity, operating days", "20 KLPD = 6,000 KL/yr, 300 d", "S1 s1; S2 s1"),
             ("Biodiesel density, yield, catalyst", "0.88 t/KL; 0.96 t/t; 1 % of B100", "S2 s5 table"),
             ("Reaction temperature, time", "about 40 C, 6 h/batch", "S2 s5; S1 s4"),
             ("Process steps, equipment", "filter, pre-heat, reactor, settling, methanol recovery, IS 15607, thermopack", "S2 s5; S3 s5, s6"),
             ("Risk line", "PESO tanks, fire-fighting", "S1 s12; S2 s11"),
             ("FFA limit, single-stage alkali", "above about 1 %: pretreat", "VG04 base catalysis"),
             ("Wash water; aqueous carry-over", "20 % of ester (batch 30-40 %); 5 % of aqueous", "S98 p.148"),
             ("Methanol column spec, reflux", "bottoms <0.5 % MeOH; distillate <0.05 % water; 3.665", "S98 5.5.1.5, Fig 66/68"),
             ("Column top temperature", "64.49 C (CoolProp 64.48)", "S98 Fig 68"),
             ("Crude glycerol", "0.15 kg/kg biodiesel", "S98 Tables 13, 14"),
             ("Flash recovery vs pressure", "about 90 % at 0.2 atm (simulated)", "AL14 via GAP_CLOSURE_BIO")]
    y3 = wtable(s, x3, y3, (150, 205, 125), srows, 8.4, 10, 1.4)
    y3 = WRAP(s, x3 + 2, y3 + 10, "S1 = VertiStrat_DPR_Templates/Template_DPR_Biodiesel_B100_20KLPD.docx; S2 = Owner_20KLPD_Draft_DPR_v2.docx (private draft, not in repo); S3 = Biodiesel_18000KL_Sample_DPR_v2.docx; S98 = Sheehan et al., NREL/SR-580-24089 (osti.gov/servlets/purl/1218369); VG04 = Van Gerpen et al., NREL/SR-510-36240; AL14 = Alam, MASc Univ. Regina 2014 (through GAP_CLOSURE_BIO.md).", 84, 8.2, 9.6)
    y3 = section(s, x3, y3 + 4, 480, "CROSS-CHECK against the DPR, per day (D)")
    D = DAY
    xrows = [("Item", "This HMB", "DPR (S2 s5)"),
             ("Oil received, kg/d", fmt(D[1]), fmt(DPR["oil_t_yr"] * 1000 / DPR["days"]) + " (check)"),
             ("Fresh methanol, kg/d", fmt(D[4]), fmt(DPR["meoh_t_yr"] * 1000 / DPR["days"]) + f" ({(D[4]/(DPR['meoh_t_yr']*1000/DPR['days'])-1)*100:+.1f} %)"),
             ("NaOH, kg/d", fmt(D[8]), fmt(DPR["cat_t_yr"] * 1000 / DPR["days"])),
             ("Glycerol (pure), kg/d", fmt(ST[17]["GLY"] * A["N_BATCH"]), f"{fmt(DPR['gly_t_yr']*1000/DPR['days'])} crude"),
             ("Crude glycerol, kg/d", fmt(D[17]), f"{D[17]/D[22]*100:.1f} % of B100 vs 10 %"),
             ("Wash water, kg/d", fmt(D[18]), "0 (no wash)")]
    y3 = wtable(s, x3, y3, (150, 130, 200), xrows, 8.6, 10, 1.4)
    y3 = wtable(s, x3, y3 + 6, (480,), [("DERIVED (D)",),
        (f"B = 20,000 L/d x 0.88 = {fmt(CAP_KLPD*RHO_BD*1000)} kg/d; per batch {fmt(M['B'],1)} kg. Oil = B / 0.96 = {fmt(M['F1'],1)} kg. TG fraction solved so stream 22 = B: {M['wtg']*100:.2f} wt%.",),
        (f"Methanol charge = 6 n_TG M = {fmt(M['meoh_tot'],1)} kg; consumed = 3 X n_TG M = {fmt(M['cons'],1)} kg. V-201: stream 4 = (6 + 7) - 5. Column: D(1-xd) + B xb = F_MeOH, D xd + B(1-xb) = F_water.",),
        ("Duty = sum m cp dT + m lambda; reboiler = D(1+R) lambda(64.5 C) + D cp (64.5-5) + B cp (99-5); T(V-201 out) = mass-weighted mix of 4 and 5.",)], 8.6, 10, 1.4, head=True)
    x4 = 1135
    y4 = section(s, x4, 84, 445, "METHANOL RECOVERY BASIS (D, frozen tool run)")
    frows = [("P, bar(a) at 80 C", "V-401 MeOH %", "V-401 H2O %", "V-402 MeOH %", "V-402 H2O %")]
    for r in FLASH_TBL: frows.append((f"{r[0]:g}", f"{r[1]:.1f}", f"{r[2]:.1f}", f"{r[3]:.1f}", f"{r[4]:.1f}"))
    y4 = wtable(s, x4, y4, (105, 85, 85, 85, 85), frows, 8.6, 10.2, 1.6)
    notes = ["One equilibrium stage, isothermal flash, UNIFAC-Dortmund activity coefficients (thermo 0.6.1), CoolProp vapour pressures, on the Rev B phase compositions. Script: docs/pid/validation/BIODIESEL_REVB_flash_check.py. Methanol-only ester phase (Rev A feed) gives 14.5 % at 1 bar, 69.9 % at 0.5, 89.6 % at 0.2, 95.0 % at 0.1, 99.0 % at 0.02 bar (GAP_CLOSURE_BIO).",
             "Water flashes with the methanol (Psat water 0.47 bar at 80 C), so the vapour is wet: C-401 dries it to the S98 distillate spec. Glycerol-phase water recovery is partial because glycerol is hygroscopic.",
             f"Condensation: methanol saturates at {TSAT_M_01} C at 0.10 bar(a); cooling water (about 30 C or above) cannot condense it, hence chilled glycol at 5 C. Methanol Psat at 5 C is 0.055 bar, so about half of the exhaust gas is methanol: VP-401 exhaust must not go to atmosphere (scrubber / back to vent header, A).",
             "Caveats: no measured methanol / methyl-oleate data were used; soap, NaOH and salts are ignored in V-402; real flash would need a thin-film or stripped design for 99 %; confirm with a licensor.",
             "FFA: 1 wt% is the acceptance limit [VG04]; above it add acid esterification (acid systems need about 20:1 methanol, same text). Not drawn.",
             "Wash: 20 % countercurrent (S98). The DPR no-wash scheme is not adopted because the stripped ester still carries residual methanol, soap and sodium; a no-wash alternative needs its own B100 quality basis (IS 15607 not read)."]
    y4 += 8
    for n in notes: y4 = WRAP(s, x4 + 6, y4, n, 88, 8.6, 10.2, bullet=True) + 3
    return s


# =====================================================================================================  sheets 3 and 4: scenarios
def mark(s, n, x, y, color=GREEN):
    s.add(f'<circle cx="{x}" cy="{y}" r="8.5" fill="#fff" stroke="{color}" stroke-width="1.8"/>')
    T(s, x, y + 3.4, n, 9.5, 700, "middle", color)


def xmark(s, x, y, r=9, color=RED):
    PL(s, [(x - r, y - r), (x + r, y + r)], 3.2, color); PL(s, [(x - r, y + r), (x + r, y - r)], 3.2, color)


def cloud(s, cx, cy, rx, ry, color="#42a5f5"):
    s.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{color}" opacity=".20" stroke="{BLUE}" stroke-width="1.6" stroke-dasharray="3 4"/>')


def callout(s, x, y, w, title, lines, color=RED, size=9.5, lh=11.5):
    tl = textwrap.wrap(title, int((w - 12) / 6.0))
    body = [textwrap.wrap(l, int((w - 12) / (size * 0.52))) for l in lines]
    h = 8 + 13 * len(tl) + lh * sum(len(b) for b in body) + 6
    R(s, x, y, w, h, "#fff", color, 1.5)
    for i, t in enumerate(tl): T(s, x + 6, y + 14 + 13 * i, t, 10.5, 700, fill=color)
    yy = y + 14 + 13 * (len(tl) - 1) + lh + 2
    for b_ in body:
        for t in b_:
            T(s, x + 6, yy, t, size, 400, fill=color); yy += lh
    return y + h


def scen_panel(s, blocks, inv_rows, note, basis=()):
    panel_box(s)
    y = 84
    for title, items in blocks:
        y = section(s, 1135, y, 445, title)
        yy = y + 14
        for t in items: yy = WRAP(s, 1141, yy, t, 82, 9.5, 11.6, bullet=True) + 3
        y = yy + 4
    y = section(s, 1135, y + 2, 445, "INVENTORIES FROM THE HMB (D, sheet 2)")
    y = wtable(s, 1135, y, (255, 190), inv_rows, 9.5, 11, 1.8, head=False)
    y = section(s, 1135, y + 6, 445, "CONSEQUENCE NUMBERS: NOT RUN")
    y = WRAP(s, 1141, y + 14, note, 82, 9.5, 11.6)
    if basis:
        y = section(s, 1135, y + 8, 445, "SOURCE LINES USED (S)")
        yy = y + 14
        for t in basis: yy = WRAP(s, 1141, yy, t, 82, 9.5, 11.6, bullet=True) + 3


BASIS = ["Methanol and biodiesel storage needs a PESO licence; risk line 'Methanol storage hazard: PESO-compliant tanks, fire-fighting, hazard study' (S1 s6, s12; S2 s6, s11).",
         "Batch transesterification at about 40 C, six hours per batch, thermopack in utilities (S2 s5, s7; S1 s7).",
         "Scheme with no water wash and no process effluent (S2 s5; S3 s5): C-501 and the wash-water scenario are A.",
         "Everything else on these sheets (detectors, ESD, vents, N2, relief) is A: the DPR files list none of it."]
SC_HEAD = ("Scenario", "Initiating event", "Hazard", "Safeguards shown (numbers / letters on drawing)", "Open data needs")
SC_W = (118, 190, 228, 308, 256)

INV = [("Methanol charge per batch, streams 6 + 7 (MeOH)", f"{fmt(M['meoh_tot'],1)} kg; {M['meoh_tot']/790:.2f} m3 at 790 kg/m3 (A)"),
       ("Methanol consumed by reaction per batch", f"{fmt(M['cons'],1)} kg"),
       ("Recovered methanol, stream 5, per batch", f"{fmt(tot(ST[5]),1)} kg"),
       ("Unreacted methanol in reactor effluent (10)", f"{fmt(ST[10]['MeOH'],1)} kg per batch"),
       ("Fresh methanol per day (stream 4 x 4)", f"{fmt(DAY[4])} kg (DPR line: 1,937)"),
       ("NaOH per batch / per day (stream 8)", f"{fmt(tot(ST[8]),1)} kg / {fmt(DAY[8])} kg"),
       ("Wash water out per batch (stream 19)", f"{fmt(tot(ST[19]),1)} kg incl. {ST[19]['MeOH']:.1f} kg methanol"),
       ("Thermal oil duty at users (24 h average)", f"{kW(Q_TO):.1f} kW (A cp, latent)")]

NOTE_Q = ("The toolkit has stdlib models that could size a release or a pool fire (process_safety.release.liquid_release_kg_s, pool_spread, pool_fire, relief), "
          "but each needs inputs this project does not have: hole size and head, bund area, tank volume and count, layout distances, wind, vessel MAWP and "
          "relief set pressure, thermal oil type and inventory. No distance, rate or frequency is quoted. Each scenario row below says what it needs.")


def sheet_sc1():
    s = Sheet(4, "SCENARIOS 1 AND 2: methanol release in storage / dosing, and fire in the methanol area or reactor area",
              "Scenarios S1 (release), S2 (fire)", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="P&ID sheet 1, HMB sheet 2; qualitative")
    frame(s, TOTAL)
    pid(s, dim=("A", "D", "E", "G"))
    # S1 overlay (blue): release, cloud, pool
    cloud(s, 185, 510, 150, 98)
    s.add(f'<ellipse cx="125" cy="606" rx="92" ry="9" fill="{CWC}" opacity=".40"/>')
    star(s, 190, 520, 11)
    T(s, 40, 346, "S1", 14, 700, fill=BLUE)
    callout(s, 62, 302, 268, "S1  METHANOL RELEASE (storage / dosing)", ["Leak at P-201 / P-202 / V-201 flange, seal or hose, or T-201 overfill. Liquid pool in the bund, vapour cloud over the area. Flammable and toxic."], BLUE)
    for n, x, y in ((1, 322, 415), (2, 79, 410), (3, 150, 596), (4, 133, 537), (5, 214, 396), (6, 27, 744), (7, 392, 722)): mark(s, str(n), x, y)
    # S2 overlay (red): pool fire, radiation, reactor area fire
    for fx, ln in ((62, 34), (96, 40), (150, 32)): flame(s, fx, 606, 0, ln, 22, 0.85)
    for ax in (190, 236): PL(s, [(ax, 600), (ax, 584)], 1.8, RED, None, "ahr")
    T(s, 38, 603, "S2", 11, 700, fill=RED)
    for fx in (440, 470): flame(s, fx, 337, 0, 30, 20, 0.85)
    T(s, 418, 322, "S2", 11, 700, fill=RED)
    callout(s, 528, 545, 152, "S2  FIRE, methanol or reactor area", ["Ignition of S1 pool or vapour, hot work, static, hot thermal oil leak. Radiant heat on T-201, V-201, R-301."], RED)
    for n, x, y in (("a", 124, 414), ("b", 625, 276), ("c", 84, 486), ("d", 392, 745), ("e", 322, 440), ("f", 433, 135)): mark(s, n, x, y)
    # panel
    blocks = [
        ("WHAT IS DRAWN", [
            "Blue star, cloud and pool: S1, release of methanol (toxic and flammable) in the bunded storage and dosing area.",
            "Red flames and arrows: S2, pool fire in the bund and fire at the reactor area; thermopack H-901 stands as a possible ignition source, its separation distance is an open item.",
            "Dimmed: units not involved. Green marks are safeguards."]),
        ("S1 SAFEGUARDS (numbers)", [
            "1 Bund and sump around T-201, P-201, V-201 (A).",
            "2 Gas detectors AT-201A/B to ESD-101 (A).",
            "3 XV-201 tank outlet ESD valve, and P-201 / P-202 trip (A).",
            "4 LSHH-201 high-high level, stops tanker fill via XV-203 (A).",
            "5 N2 blanket and PVRV-201 with flame arrester on T-201 and V-201 (A).",
            "6 ES-301 emergency shower and eyewash (A), for skin and eye contact.",
            "7 Fire-fighting (R: DPR risk line); ESD-101 logic (A)."]),
        ("S2 SAFEGUARDS (letters)", [
            "a Flame detector BE-201; b flame detector BE-301 (A), to ESD-101.",
            "c Water spray / foam on T-201 (R: DPR 'fire-fighting'); foam type for a water-miscible fuel is an open item.",
            "d ESD-101 closes XV-201, XV-202, XV-301A/B and trips XV-901 (A).",
            "e Bund limits pool area (A). f PSV-301A/B relieve reactor pressure under fire (A, not sized)."]),
    ]
    scen_panel(s, blocks, INV, NOTE_Q, BASIS)
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (qualitative; no distance, rate or frequency is quoted)")
    rows = [SC_HEAD,
            ("S1 Methanol release, storage and dosing area (T-201, P-201, V-201, P-202)",
             "Leak or seal failure on P-201 / P-202, flange or hose failure, tanker hose failure during fill, overfill of T-201 or V-201.",
             "Flammable liquid pool in the bund and flammable vapour cloud (flash fire if ignited; explosion in a congested area not assessed). Toxic by inhalation, ingestion and skin (general knowledge, check the SDS). Methanol burns with a faint flame (general, confirm).",
             "1 bund and sump (A); 2 gas detectors AT-201A/B to ESD-101 (A); 3 XV-201 and pump trip (A); 4 LSHH-201 stops fill (A); 5 N2 blanket + PVRV-201 + flame arrester (A); 6 shower / eyewash (A); 7 fire-fighting (R) and ESD-101 (A).",
             "Tank size and count, bund area and volume, hole size and head, ignition sources, wind, boundary and building distances, detector set points. PESO licensing class and distances are not in the source files. Not quantified: needs these."),
            ("S2 Fire in the methanol tank farm or reactor area",
             "Ignition of an S1 release, hot work, static discharge during transfer, thermal oil leak on a hot surface, electrical fault at the reactor area.",
             "Pool fire in the bund with radiant heat on T-201, V-201 and the reactors; reactor contents (about 951 kg methanol per batch, D) heat and vent via PSV-301A/B. Escalation to the thermopack or to tankers is an open item.",
             "a, b flame detectors (A); c spray / foam on T-201 (R); d ESD closes XV-201, XV-202, XV-301A/B and trips XV-901 (A); e bund (A); f PSV-301A/B (A).",
             "Layout and spacing (none in source files), fire-water source and rate, foam type and rate, reactor design pressure, PSV set and fire-case load, radiant heat targets. Not quantified: needs bund area, burning rate inputs and layout.")]
    wtable(s, 20, y, SC_W, rows, 9, 11, 2.2)
    return s


def sheet_sc2():
    s = Sheet(5, "SCENARIOS 3 TO 5: overpressure and thermopack, catalyst and wash water, loss of N2 / vent",
              "Scenarios S3, S4, S5", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="P&ID sheet 1, HMB sheet 2; qualitative")
    frame(s, TOTAL)
    pid(s, dim=("A", "G"))
    # S3
    star(s, 477, 321, 13)
    PL(s, [(468, 128), (468, 104)], 5, GREEN, None, None, "none", .6); arrow(s, 468, 102, "u", GREEN, 11)
    star(s, 1030, 160, 12); flame(s, 1030, 150, 0, 26, 18, 0.9)
    T(s, 432, 308, "S3", 11, 700, fill=RED); T(s, 1012, 180, "S3", 11, 700, fill=RED)
    callout(s, 935, 335, 177, "S3  OVERPRESSURE / THERMOPACK", ["TCV-301, TIC-301 or H-901 control fails: reactor heats above 40 C, methanol vapour, PSV-301 lifts. Thermal oil leak at TOS line."], RED)
    for n, x, y in (("1", 497, 218), ("2", 497, 278), ("3", 484, 104), ("4", 958, 192), ("5", 1090, 298), ("6", 498, 188)): mark(s, n, x, y)
    # S4
    star(s, 225, 652, 12)
    PL(s, [(872, 741), (872, 756), (800, 756)], 5, RED, None, None, "none", .55)
    callout(s, 36, 300, 292, "S4  CATALYST AND WASH WATER", ["Bag-tipping dust or spill at H-301, caustic splash at M-301; alkaline methanol and soap carry-over in wash water (stream 19) to the ETP."], AMBER)
    T(s, 240, 640, "S4", 11, 700, fill=AMBER); T(s, 884, 756, "S4", 11, 700, fill=AMBER)
    for n, x, y in (("1", 256, 656), ("2", 27, 756), ("3", 320, 596), ("4", 822, 612), ("5", 924, 730), ("6", 800, 712)): mark(s, n, x, y, AMBER)
    # S5
    for x, y in ((362, 214), (606, 214), (231, 395), (108, 475), (400, 392), (740, 94)): xmark(s, x, y, 7)
    callout(s, 45, 98, 200, "S5  LOSS OF N2 / VENT BLOCKED", ["N2 supply fails or a vent path blocks (X marks): air ingress into methanol vessels, or over / under-pressure."], RED)
    for n, x, y in (("i", 648, 722), ("ii", 125, 470), ("iii", 392, 735), ("iv", 484, 126)): mark(s, n, x, y, "#6a1b9a")
    blocks = [
        ("WHAT IS DRAWN", [
            "S3: star at the reactor jacket thermal oil valve and at the thermopack outlet; green arrow = PSV-301 lifting to the vent.",
            "S4: amber star at the catalyst hopper H-301; red thick line = wash water out (stream 19) to the ETP.",
            "S5: red X on every nitrogen or vent path (R-301A/B N2, V-201 vent, PVRV-201, VP-401 exhaust, FA-301)."]),
        ("S3 SAFEGUARDS (numbers)", [
            "1 TSHH-301 reactor high-high temperature closes TCV-301A/B and trips XV-901 (A).",
            "2 PT-301 PAHH closes XV-301A/B and TCV-301A/B (A).",
            "3 PSV-301A/B to the vent header, KO-301 catch pot and flame arrester FA-301, stack to a safe location (A; set pressure and design pressure open; sizing on sheet 6).",
            "4 TSHH-901 and FSLL-901 trip the burner (A). 5 XV-901 fuel shut-off (A). 6 TIC-301 normal control of TCV-301A/B (A)."]),
        ("S4 SAFEGUARDS (numbers, amber)", [
            "1 H-301 enclosed tipping station with dust extraction (A). 2 ES-301 shower and eyewash (A). 3 LSH-311 high level on M-301 (A).",
            "4 FCV-501 sets wash ratio (A). 5 AT-501 pH / conductivity on stream 19 to divert off-spec water (A). 6 LIC-501 holds the wash level (A)."]),
        ("S5 SAFEGUARDS (roman, purple)", [
            "i PAL-951 low N2 pressure alarm (A). ii PVRV-201 and flame arrester keep a breathing path (A). iii ESD-101 stops transfer pumps on low N2 (A). iv FA-301 vent line kept clear: inspect (A)."]),
    ]
    scen_panel(s, blocks, INV[:1] + INV[3:4] + INV[5:], NOTE_Q, BASIS)
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (qualitative; no distance, rate or frequency is quoted)")
    rows = [SC_HEAD,
            ("S3 Reactor overpressure or thermopack failure",
             "TCV-301 sticks open, TIC-301 or TT fails low, H-901 control or burner fails high, vent or PSV path blocked, thermal oil pump P-901 stops with burner on, thermal oil leak.",
             "Reactor heats above 40 C with about 951 kg methanol per batch (D): vapour pressure rise, release via PSV-301 to the vent. Thermal oil leak on a hot surface: fire. Overheated oil in the heater coil.",
             "1 TSHH-301; 2 PAHH-301; 3 PSV-301A/B + FA-301; 4 TSHH-901 / FSLL-901 burner trip; 5 XV-901; 6 TIC-301 (all A).",
             "Reactor design pressure and temperature, PSV set and relief case (not sized), thermal oil type, flash point, inventory and operating temperature, jacket limits, vent size and discharge location. Not quantified."),
            ("S4 NaOH / KOH catalyst handling and wash water",
             "Bag-tipping spill or dust at H-301, splash while dissolving in methanol at M-301, M-301 overflow, wash-water carry-over of alkaline methanol and soap, line failure at C-501 outlet.",
             "Corrosive burns to skin and eyes (general knowledge, check the SDS). Dissolving in methanol releases heat (general). Wash water is about 880 kg/batch (20 % of ester, S98) with methanol traces (D, sheet 2). The DPR says no process effluent: the wash is chosen in Rev B (sheet 3).",
             "1 enclosed hopper and dust extraction; 2 ES-301; 3 LSH-311; 4 FCV-501; 5 AT-501 divert; 6 LIC-501 (all A).",
             "Catalyst grade and form (NaOH, KOH or methoxide), pack size, ETP capacity, discharge standard (none in the source files), SDS data. Confirm with the technology supplier whether a wash is used. Not quantified."),
            ("S5 Loss of nitrogen or vent blocked",
             "N2 supply or regulator fails, N2 header pressure falls while pumping out; vent line, PVRV-201 or flame arrester FA-301 blocked; vacuum is lost or air leaks into V-401/V-402/V-403/V-601 (VP-401 trips).",
             "Air ingress into vessels holding methanol vapour gives a flammable atmosphere inside the vessel. Blocked vent: overpressure of reactors, vacuum collapse or overpressure of atmospheric tanks T-201, V-403.",
             "i PAL-951 alarm; ii PVRV-201 + flame arrester path; iii ESD-101 stops transfer pumps on low N2; iv FA-301 vent kept clear (all A).",
             "N2 source, receiver and consumption, vent and breather sizing, tank design pressure and vacuum, flammable limits of methanol (not entered), inspection interval of flame arresters. Not quantified.")]
    wtable(s, 20, y, SC_W, rows, 9, 11, 2.2)
    return s


# =====================================================================================================  sheets 6 to 8: safety design basis
K_MEOH = 1.32        # D CoolProp 8.0: methanol vapour cp/cv at 359 K, 2.2 bar(a), frozen
T_REL_K = 359.0      # D CoolProp 8.0: methanol saturation temperature at 222 kPa(a) (relieving pressure of a 1.0 barg set, fire accumulation), frozen
LAM_REL = 1056.2     # D CoolProp 8.0: methanol latent heat at 222 kPa(a), kJ/kg, frozen
SET_G = 100.0        # A kPa(g) set pressure used for the screening cases (the DPR gives no design pressure)
Q_REB = Q["E-403 C-401 reboiler (TO)"]


def relief_numbers():
    """screening sizes from the repo toolkit (process_safety.relief); every input is A, so the numbers are examples of the method, not a design"""
    out = {}
    if _relief is None: return out
    V = 8.0; Dv = (4 * V / (math.pi * 1.5)) ** (1 / 3); Lv = 1.5 * Dv           # A: 8 m3 vertical vessel, H/D 1.5, 80 % fill
    Aw = _relief.wetted_area_cylinder(Dv, Lv, 0.8 * Lv, "vertical")
    W1 = _relief.fire_relief_rate_kg_h(Aw, LAM_REL)
    r1 = _relief.gas_area(W1, T_REL_K, _relief.relieving_pressure_kpa(SET_G, "fire"), _relief.ATM, MW["MeOH"], K_MEOH, set_g_kpa=SET_G)
    out["R"] = (Dv, Lv, Aw, W1, r1.required_area_mm2, r1.orifice, r1.n_valves)
    W2 = kW(Q_REB) * 3600.0 / LAM_REL                                           # kg/h: loss of cooling, reboiler duty (24 h average) all to vapour
    r2 = _relief.gas_area(W2, T_REL_K, _relief.relieving_pressure_kpa(SET_G, "single_non_fire"), _relief.ATM, MW["MeOH"], K_MEOH, set_g_kpa=SET_G)
    out["C"] = (kW(Q_REB), W2, r2.required_area_mm2, r2.orifice, r2.n_valves)
    return out


RN = relief_numbers()
_zones = {}
try:
    from process_safety import atex as _atex
    _zones = {g_: _atex.zone("gas", g_) for g_ in ("continuous", "primary", "secondary")}
except Exception:                                                              # pragma: no cover
    pass
SZ_R = (f"screening size (toolkit, inputs A: 8 m3, H/D 1.5, 80 % fill, set {SET_G/100:.1f} barg): fire wetted area {RN['R'][2]:.1f} m2, vapour {RN['R'][3]:,.0f} kg/h, "
        f"required area {RN['R'][4]:,.0f} mm2, orifice {RN['R'][5]} x {RN['R'][6]}; runaway and jacket-leak cases not sized") if RN else "not sized: toolkit unavailable"
SZ_C = (f"screening size (toolkit, inputs A): loss of cooling, reboiler {RN['C'][0]:.0f} kW average all to vapour = {RN['C'][1]:,.0f} kg/h, required area {RN['C'][2]:,.0f} mm2, "
        f"orifice {RN['C'][3]} x {RN['C'][4]}; fire and tube-rupture cases not sized") if RN else "not sized"

RELIEF = [("Item", "Design pressure basis (A)", "Relief case(s)", "Device (sheet 1)", "Discharge", "Sizing status"),
          ("T-101 UCO tank", "atmospheric; tank code not read", "pump in/out breathing, thermal, fire (UCO flash point not read)", "PVRV-101 breather; weak roof seam", "atmosphere, safe location", "not sized: needs tank volume and fill/empty rates"),
          ("F-101 filter", "rated at or above P-101 shut-off (A)", "blocked outlet at pump shut-off", "none: rating >= shut-off head (reason)", "-", "needs P-101 curve"),
          ("E-101 heater", "TO side A", "thermal expansion of blocked-in oil, tube leak", "TSV on trapped section (vendor, not drawn)", "TO expansion line", "not sized: needs TO inventory"),
          ("T-201 methanol tank", "atmospheric / low pressure; N2 blanketed", "normal breathing, thermal, fire engulfment, overfill", "PVRV-201 + flame arrester; emergency vent or weak seam", "atmosphere via flame arrester, safe location", "not sized: needs T-201 volume and geometry (toolkit tank_venting, API 2000 5th ed., ready)"),
          ("V-201 dosing tank", "atmospheric, N2 blanketed", "N2 regulator failure, overfill, pump-out vacuum, fire", "PVRV-202", "safe location (vent header A)", "not sized"),
          ("M-301 catalyst mix", "atmospheric", "NaOH-in-methanol dissolution exotherm, N2 failure, fire", "PVRV-301", "vent header (A)", "not sized: heat of solution not in sources"),
          ("R-301A/B reactors", "A: design 1.5 barg (DPR silent); lines 3.0 bar(a)", "fire; blocked outlet (P-302 shut-off); TCV-301 / TIC-301 failure; N2 over-pressure; jacket TO leak; runaway (no data)", "PSV-301A/B", "KO-301, FA-301, stack to safe location", SZ_R),
          ("V-302 settler", "atmospheric to 1.1 bar(a)", "overfill, blocked outlet, fire", "PVRV-302", "vent header (A)", "not sized"),
          ("V-401, V-402 flashes", "full vacuum (FV) rated, plus A 1.0 barg", "loss of vacuum or air in-leak with TO still on; blocked vapour line; E-401 glycol loss; TO coil leak; fire", "PSV-401/402 (common header)", "KO-301, FA-301, stack", "not sized: needs vessel volumes and TO coil temperature"),
          ("E-401 vacuum condenser", "vapour side FV; glycol side A", "tube rupture (glycol into vacuum side), thermal expansion, glycol loss", "TSV on glycol side (vendor, not drawn)", "glycol loop", "tube-rupture rule (API 521) not obtained: gap"),
          ("V-403 receiver", "FV; methanol Psat 40 C = 0.36 bar(a) (CoolProp), so not self-pressurising", "air in-leak, N2 back-flow, cooling loss", "none: FV rating + check valve in VP-401 line (reason)", "-", "reason stated; confirm with vacuum vendor"),
          ("C-401 column", "A: 1.5 barg + FV", "loss of cooling (E-402), reflux failure, blocked outlet, TO control failure at E-403, fire, tube rupture", "PSV-403", "KO-301, FA-301, stack", SZ_C),
          ("E-402, E-403", "CW side / TO side A", "thermal expansion, tube leak (TO into methanol)", "TSV (vendor, not drawn)", "closed", "not sized"),
          ("C-501 wash", "atmospheric", "overfill, blocked outlet (P-402 shut-off), fire", "PVRV-501 (vent)", "atmosphere, safe location", "not sized"),
          ("V-601 dryer", "FV rated", "loss of vacuum with heat on; blocked vapour line to VP-601", "PSV-601", "safe location", "not sized"),
          ("VP-401, VP-601 pumps", "vendor", "discharge blocked, seal-fluid loss", "vendor package relief", "scrubber or safe location (A)", "vendor"),
          ("E-501, E-602 coolers", "CW side A", "thermal expansion of blocked-in water", "TSV (not drawn)", "closed drain", "not sized"),
          ("T-701A/B product", "atmospheric", "breathing, thermal, fire (B100 flash point not read)", "PVRV-701A/B", "atmosphere", "not sized: needs volumes"),
          ("T-801 glycerol", "atmospheric", "breathing; residual methanol in headspace", "PVRV-801", "atmosphere, safe location", "not sized"),
          ("H-901, V-901 thermopack", "TO circuit, vendor", "loss of flow, over-temperature, coil leak, TO expansion", "V-901 vent and coil protection (vendor package, not drawn)", "safe location", "vendor package; TO type and temperature not in sources"),
          ("N2 header", "regulator outlet A", "PCV failure open", "PSV on header (A, not drawn)", "safe location", "not sized")]
BUND_ROWS = [
    ("Bund / dyke (R)", f"Rule read in HSG176 (checklist, para 157): capacity 110 % of the largest vessel, or 25 % of total tank capacity; take the greater (A reading, confirm in the text). T-201 volume is TBD. Illustration only (A): 7 days of fresh methanol {fmt(DAY[4])} kg/d = {DAY[4]*7/790:.1f} m3 at 790 kg/m3, bund at least {1.1*DAY[4]*7/790:.1f} m3. V-201 holds one batch charge {fmt(M['meoh_tot'],0)} kg = {M['meoh_tot']/790:.2f} m3 (D)."),
    ("PESO / licence", "gap: Petroleum Rules 2002 and SMPV(U) Rules 2016 (peso.gov.in did not connect, only snippets). Licence class, storage quantity limits and distances not stated here."),
    ("Safety distances (R)", "HSG176 Table 1: 1 m (tank up to 1 m3) to 15 m (over 250 m3) from boundaries, buildings and ignition sources; HSE layout guidance: address domino escalation and occupied buildings. T-201 distance depends on its volume (TBD). H-901 (burner, ignition source) to methanol area and glycerol/biodiesel tanks: distance not set (gap)."),
    ("Fire water / foam (R, rates gap)", "DPR risk line: hydrants and spray / foam. Rates, hydrant layout and foam concentrate: gap (OISD standards and NFPA 30 / 15 are paywalled). Methanol is water-miscible, so confirm an alcohol-resistant foam (general knowledge, check)."),
]
DET_ROWS = [
    ("Gas detection (R)", "AT-201A/B at T-201 / P-201 / V-201 / tanker manifold; AT-301 at the reactor area; AT-401 at the vacuum / column package. Place at likely leak points (seals, flanges, manifolds, sample points); methanol vapour is about 1.1 x air (32.04 / 28.96) so no strong low or high bias: mount around 1 m (A). Set points and voting TBD (A). Source: gas detectors in hazard areas, IFC EHS nitrogenous fertilizer guideline (checklist S8)."),
    ("Flame detection", "BE-201, BE-301, BE-401. Methanol flame is hard to see (general knowledge, check SDS): use UV/IR type (A)."),
    ("Isolation of inventory (R)", "XV-201 (T-201 outlet), XV-203 (tanker fill), XV-202 (dose line), XV-301A/B (reactors), XV-401 (C-401 reboiler heat), XV-901 (burner fuel); fail-closed, remote push-button in the control room (A). HSG176 para 128: remote shut-off valves on large inventories, fail safe."),
    ("Ventilation / inerting", "Open-air process structure (A). N2 blanket on T-201, V-201, M-301, R-301A/B; vacuum vessels are never opened to air except through a PCV N2 break. N2 asphyxiation at vents and in vessels: confined-space rule (general)."),
    ("Methanol inventory", f"Upper bound outside T-201 (D): R-301A + R-301B charges 2 x {fmt(M['meoh_tot'],0)} kg, V-201 batch charge {fmt(M['meoh_tot'],0)} kg, V-302 about {fmt(ST[10]['MeOH'],0)} kg, plus C-401 / V-403 hold-up (not sized): about {fmt(3*M['meoh_tot']+ST[10]['MeOH'],0)} kg. Flammable and toxic (inhalation, ingestion, skin; general, check SDS). Threshold check against the MAH rules: gap."),
    ("Vacuum system", f"Air in-leak plus methanol vapour gives a flammable mixture inside V-403, VP-401 and its exhaust: methanol Psat at 5 C is 0.055 bar, i.e. 5.5 vol % at 1 bar exhaust (CoolProp), flammable limits not entered (gap). Vessels FV-rated; check valve against suck-back; exhaust to scrubber or safe location, not into the process area; N2 purge on VP-401 (A)."),
    ("Thermopack", "Fuel type and BMS per vendor; free boiler / thermal-fluid heater guidance not found (HSE PM5 404): gap. TO leak on hot surface near methanol is a fire route (S3). TO type, flash point and film temperature not in sources."),
    ("Caustic (NaOH)", f"{fmt(DAY[8]/4,1)} kg NaOH per batch (D). Enclosed bag-tipping hopper H-301 with dust extraction, ES-301 shower and eyewash, M-301 high level LSH-311; dissolution in methanol releases heat (general, not quantified). Corrosive to skin and eyes (check SDS)."),
]
ZONE_ROWS = [("Hazardous-area basis", "Zone from release grade and ventilation (toolkit atex.zone, medium dilution, good availability): continuous grade zone %s, primary %s, secondary %s. Apply: inside T-201, V-201 and C-401 headspace zone 0; vent outlets (PVRV-201/202, FA-301 stack) and open sample points zone 1; pump seals, flanges, valves zone 2. Extents are not computed. Gas group and temperature class of methanol, EPL and equipment category: not entered (IEC 60079-10-1 and the SDS are not in the sources, gap). H-901 and non-Ex equipment kept outside classified areas: distance gap." % (_zones.get("continuous"), _zones.get("primary"), _zones.get("secondary")))]


def sheet_relief():
    s = Sheet(6, "SAFETY DESIGN BASIS (1 of 3): relief schedule, bund and distances, detection, isolation, hazardous area",
              "Safety design basis: relief and mitigation", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="Checklist SAFETY_FEATURES_CHECKLIST.md; R = named free source, A = assumed, gap = standard not obtained")
    frame(s, TOTAL)
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE (A: no design pressure or set point exists in the DPR files; every device is drawn on sheet 1 with its tag; coverage: every vessel, tank, column, reactor and exchanger on sheet 1 has a row)")
    y = wtable(s, 20, y, (118, 205, 330, 235, 190, 482), RELIEF, 8.2, 9.8, 1.6)
    yb = section(s, 20, y + 8, 760, "BUND, DISTANCES, FIRE WATER (R, A, gap)")
    wtable(s, 20, yb, (130, 630), [("Topic", "Basis")] + BUND_ROWS, 8.2, 9.8, 1.6)
    yd = section(s, 800, y + 8, 780, "DETECTION, ISOLATION, INERTING AND HAZARD-SPECIFIC BASIS (R, A, gap)")
    y2 = wtable(s, 800, yd, (130, 650), [("Topic", "Basis")] + DET_ROWS + ZONE_ROWS, 8.2, 9.8, 1.6)
    return s


ESD_COLS = ("XV-201", "XV-202", "XV-203", "XV-301A/B", "TCV-301A/B", "XV-901", "XV-401", "TCV-401/402/404", "P-201/202", "P-301", "P-403/405", "VP-401")
X_ = "X"
ESD = [("AT-201A/B gas HH (methanol area)", "XV-201 XV-202 XV-203 P-201/202"),
       ("BE-201 flame (methanol area)", "XV-201 XV-202 XV-203 XV-301A/B TCV-301A/B XV-901 XV-401 TCV-401/402/404 P-201/202 P-301 P-403/405 VP-401"),
       ("AT-301 gas HH (reactor area)", "XV-202 XV-301A/B TCV-301A/B XV-901 P-301"),
       ("BE-301 flame (reactor area)", "XV-201 XV-202 XV-203 XV-301A/B TCV-301A/B XV-901 XV-401 TCV-401/402/404 P-201/202 P-301 P-403/405 VP-401"),
       ("TSHH-301 reactor temperature HH", "XV-202 TCV-301A/B XV-901"),
       ("PAHH-301 (PT-301) reactor pressure HH", "XV-202 XV-301A/B TCV-301A/B XV-901"),
       ("TSHH-901 / FSLL-901 thermopack", "XV-901"),
       ("LSHH-201 T-201 level HH", "XV-203 P-201/202"),
       ("LSH-311 M-301 level high", "P-301"),
       ("AT-401 gas HH / BE-401 flame (vacuum, column)", "XV-401 TCV-401/402/404 P-403/405 VP-401"),
       ("PAHH-404 (PT-404) column pressure HH", "XV-401 TCV-401/402/404"),
       ("PAH-401 (PT-401) loss of vacuum", "TCV-401/402/404"),
       ("PAL-951 low N2 pressure", "P-201/202 P-403/405")]
SIF = [("SIF", "Function", "Initiator > final element", "Demand source (sheets 4, 5)", "IPLs credited (A)", "SIL target (A)", "Free source"),
       ("SIF-1", "T-201 overfill", "LSHH-201 > XV-203, P-201", "S1 tanker over-delivery", "LT-201 alarm and operator, bund, PVRV-201", "SIL 1", "HSG176 para 137 (R)"),
       ("SIF-2", "Reactor high temperature", "TSHH-301 > TCV-301A/B, XV-901", "S3 TCV-301 / TIC-301 failure", "TIC-301 loop, operator, PSV-301A/B", "SIL 1", "HSG238 (R)"),
       ("SIF-3", "Reactor high pressure", "PAHH-301 > XV-301A/B, TCV-301A/B, XV-901", "S3 blocked vent, overheating", "PSV-301A/B, KO-301", "SIL 1", "HSG238 (R)"),
       ("SIF-4", "Thermopack trip", "TSHH-901, FSLL-901 > XV-901", "S3 loss of TO flow / over-temperature", "vendor BMS, TIC", "SIL 2", "gap: boiler guidance not found"),
       ("SIF-5", "Methanol gas detected", "AT-201A/B > XV-201/202/203, pumps", "S1 release", "bund, operator, ES-301", "SIL 1", "IFC EHS (R)"),
       ("SIF-6", "Flame detected", "BE-201/301/401 > all XV, pumps, VP-401", "S2 fire", "fire fighting, spray / foam, PSV", "SIL 1", "HSG176 para 128 (R)"),
       ("SIF-7", "Column over-pressure", "PAHH-404 > XV-401, TCV-404", "loss of E-402 cooling", "PSV-403, CW flow alarm", "SIL 1", "HSG238 (R)"),
       ("SIF-8", "Loss of vacuum", "PAH-401 > TCV-401/402", "VP-401 trip, air in-leak, glycol loss", "PSV-401/402, PT-401 alarm", "SIL 1", "HSG238 (R)"),
       ("SIF-9", "M-301 overfill", "LSH-311 > P-301", "S4 mix tank overflow", "operator, WT-201 batch charge", "SIL 1", "HSG176 para 137 (R)")]
INSTR = [("LT-101", "T-101 level, alarm"), ("PDI-101", "F-101 differential pressure"), ("TIC-102", "oil outlet T, > TCV-102"), ("LT-201", "T-201 level"),
         ("LSHH-201", "T-201 level HH (SIF-1)"), ("AT-201A/B", "gas detectors, methanol area"), ("BE-201", "flame detector, methanol area"), ("WT-201", "V-201 batch weighing"),
         ("LSH-311", "M-301 level high (SIF-9)"), ("TIC-301", "reactor T, > TCV-301A/B"), ("TSHH-301", "reactor T HH (SIF-2)"), ("LT-301", "reactor level"),
         ("PT-301", "reactor P; PAHH-301 (SIF-3)"), ("AT-301", "gas detector, reactor area"), ("BE-301", "flame detector, reactor area"), ("LT-302", "V-302 interface level"),
         ("PT-401", "vapour header vacuum; PAH-401 (SIF-8)"), ("AT-401", "gas detector, vacuum / column"), ("BE-401", "flame detector, column"), ("TIC-402", "V-401 T, > TCV-402"),
         ("TIC-403", "V-402 T, > TCV-401"), ("LT-403", "V-403 level"), ("LT-404", "V-404 level"), ("PT-404", "column P; PAHH-404 (SIF-7)"),
         ("TIC-404", "column T, > TCV-404"), ("LIC-501", "C-501 level"), ("AT-501", "pH / conductivity, stream 19"), ("FCV-501", "wash water flow valve"),
         ("LT-701", "T-701 level"), ("LT-801", "T-801 level"), ("TSHH-901", "thermopack T HH (SIF-4)"), ("FSLL-901", "TO flow low-low (SIF-4)"),
         ("PAL-951", "low N2 pressure alarm")]
HAZ = [("Node", "Deviation", "Cause", "Consequence (qualitative)", "Safeguards", "Action"),
       ("1 T-201, P-201, tanker fill", "more level", "tanker over-delivery, LT-201 fails", "overflow to bund; flammable pool and vapour, toxic", "LSHH-201 > XV-203 (SIF-1), bund, PVRV-201", "confirm bund volume; independent HH sensor"),
       ("2 V-201, M-301, H-301", "more heat / no N2", "NaOH dissolution in methanol; N2 supply lost", "warm methanol, vapour at vent, dust", "LSH-311, ES-301, PAL-951, enclosed hopper", "get heat of solution; N2 source sizing"),
       ("3 R-301A/B reaction", "more temperature, pressure", "TCV-301 stuck, TIC fails, vent blocked", "methanol vapour to PSV, KO-301; release if PSV discharge fails", "TSHH-301, PAHH-301, PSV-301A/B, KO-301, FA-301", "set design pressure; size PSV (sheet 6); vent stack height"),
       ("4 V-302 settler", "other composition", "poor phase split, high soap", "soap / glycerol to V-401: fouling, off-spec ester", "LT-302, sampling", "FFA limit 1 % at receipt"),
       ("5 V-401/402, E-401, V-403, VP-401", "less vacuum / air in-leak", "VP-401 trips, leak, glycol loss", "methanol vapour pressure rise; flammable air-methanol mixture in vacuum train", "PT-401 > TCV-401/402 (SIF-8), PSV-401/402, check valve, N2 purge", "vacuum vendor; exhaust to scrubber; flammable-limit check"),
       ("6 E-401 glycol loop", "no cooling", "RU-401 failure", "uncondensed methanol to VP-401 exhaust: release", "VP-401 trip, AT-401", "outlet temperature alarm; RU-401 spare"),
       ("7 C-401 column", "loss of cooling or reflux", "CW failure at E-402, P-405 trip", "over-pressure; methanol to PSV-403", "PSV-403, PAHH-404 > XV-401 (SIF-7)", "stage count and sizing; fire case"),
       ("8 C-501, V-601, ETP", "more methanol in effluent", "poor V-401/402 recovery", "flammable / toxic wash water to ETP", "AT-501, LIC-501", "ETP basis (none in sources)"),
       ("9 H-901 thermopack, TO", "no flow, over-temperature", "P-901 trips, burner high", "coil overheating, TO leak and fire near methanol", "FSLL-901, TSHH-901 > XV-901 (SIF-4)", "TO type; separation distance")]
ISD = [("Option", "What changes", "Basis"),
       ("Reduce methanol inventory", "size V-201 to one batch charge and T-201 to a tanker lot, no bulk store (T-201 volume TBD)", "A (HSG176 distances scale with tank size, R)"),
       ("Moderate conditions", "reactor at 40 C is below methanol boiling point 64.5 C (S98 Fig 68, CoolProp): atmospheric vessels. Hot water instead of thermal oil for every user up to 80 C; only E-403 (99 C bottoms) needs a hotter medium", "S: 40 C (DPR); A: heating medium"),
       ("Soften the vacuum", "run V-401/402 at 0.2 bar(a): about 90 % recovery, methanol Tsat 28 C, simpler chilling; residual goes to the wash and C-401", "D: sheet 3 table; A"),
       ("Short residence time", "thin-film or wiped-film flash instead of heated batch pots reduces hold-up (vendor claims over 99 % in 1 to 3 stages, grade C)", "C: Alam Table 1.4 via GAP_CLOSURE_BIO"),
       ("Avoid acid pretreatment", "buy oil to a 1 % FFA specification instead of adding acid esterification (no sulfuric acid, no 20:1 methanol)", "S: VG04; A"),
       ("Substitute catalyst form", "methoxide solution delivered by supplier removes bag tipping and dissolution heat, but adds a delivered flammable inventory", "A: trade-off, not in sources")]


def sheet_esd():
    s = Sheet(7, "SAFETY DESIGN BASIS (2 of 3): ESD cause-and-effect matrix, SIF list, instrument index",
              "Safety design basis: ESD, SIF, instruments", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="SIL targets are A: no SIL verification claimed; IEC 61511 and LOPA texts not obtained (gap)")
    frame(s, TOTAL)
    y = section(s, 20, 84, 860, "ESD CAUSE-AND-EFFECT MATRIX (X = acts; all final elements on sheet 1; voting TBD, A)")
    rows = [("Initiator",) + tuple(ESD_COLS)]
    for ini, fe in ESD:
        acts = fe.split()
        rows.append((ini,) + tuple(X_ if c in acts else "-" for c in ESD_COLS))
    rows.append(("Fail position",) + ("closed",) * 5 + ("closed",) * 2 + ("closed",) + ("stop",) * 4)
    y = wtable(s, 20, y, (232,) + (52,) * 12, rows, 8, 10, 1.8)
    WRAP(s, 22, y + 12, "XV-201/202/203/301A/B/401/901 are ball valves with spring-return actuators (A); TCV-301A/B, 401, 402, 404 close the thermal-oil supply; pumps are stopped by the ESD-101 logic. ESD-101 is separate from the basic control loops (HSG238, R).", 150, 8.6, 10.2)
    y2 = section(s, 900, 84, 680, "INSTRUMENT INDEX (every tag drawn on sheet 1)")
    ir = [("Tag", "Service", "Tag", "Service")]
    half = (len(INSTR) + 1) // 2
    for k in range(half):
        a = INSTR[k]; b = INSTR[k + half] if k + half < len(INSTR) else ("", "")
        ir.append(a + b)
    wtable(s, 900, y2, (78, 262, 78, 262), ir, 8, 10, 1.6)
    ys = section(s, 20, y + 52, 1560, "SAFETY INSTRUMENTED FUNCTIONS (SIL targets A; independent of the basic control loops; demand frequencies not quantified)")
    wtable(s, 20, ys, (50, 150, 300, 260, 360, 90, 350), SIF, 8.4, 10.2, 1.8)
    return s


def sheet_haz():
    s = Sheet(8, "SAFETY DESIGN BASIS (3 of 3): hazard identification nodes and inherently safer design options",
              "Safety design basis: HAZOP nodes, ISD", code="VS-BD", project="Biodiesel (B100) plant, 20 KLPD, batch transesterification",
              basis="OSHA 29 CFR 1910.119 (R): PHA with facility siting; consequences qualitative, no numbers")
    frame(s, TOTAL)
    y = section(s, 20, 84, 1560, "HAZARD IDENTIFICATION (HAZOP-style nodes; qualitative; the full study with facility siting is still to be done, R: OSHA PSM)")
    y = wtable(s, 20, y, (190, 140, 230, 300, 380, 320), HAZ, 8.6, 10.4, 2.2)
    y = section(s, 20, y + 12, 1120, "INHERENTLY SAFER DESIGN OPTIONS")
    wtable(s, 20, y, (180, 640, 300), ISD, 8.6, 10.4, 2.2)
    return s


# =====================================================================================================  main
def build_all():
    return [sheet_pid(), sheet_hmb(), sheet_basis(), sheet_sc1(), sheet_sc2(), sheet_relief(), sheet_esd(), sheet_haz()]


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, "Biodiesel B100 20 KLPD P&ID set, Rev B", previews="--previews" in sys.argv)
    print("ok", len(sheets))
    print(f"Closure: in {H(m_in):,.2f} kg/h, out {H(m_out):,.2f} kg/h, error {abs(ERR):.2f} %")

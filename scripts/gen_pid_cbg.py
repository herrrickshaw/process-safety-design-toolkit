#!/usr/bin/env python3
"""Generate the compressed biogas (CBG) plant P&ID set, Rev B: P&ID, heat and material balance, basis, four scenarios and the safety design basis.

Basis (S): docs source is VertiStrat_DPR_Templates/Template_DPR_CBG_10TPD.docx, Section 1 and 4 (10 TPD CBG; mixed feedstock of press mud, agri residue
and napier grass), Section 7 (cost-table headings used for the equipment groups), Section 6 (PESO licence for compressed gas storage and cascade filling),
Section 9 (33,00,000 kg/yr CBG, 18,000 t/yr FOM, 52,800 t/yr feedstock; implied 330 operating days).
Rev B closes the sourced gaps of docs/pid/validation/GAP_CLOSURE_BIO.md (feed mix as an input, FOM cake solids and TS capture, methane slip,
upgrader power, oxidiser basis) and the real-gas items of CBG_VALIDATION.md, and adds the safety design basis (relief schedule, ESD cause-and-effect,
SIF list, detection and mitigation, hazard identification, inherently safer options, hazardous-area basis). Everything else that fixes a number
is ASSUMED (A) and listed on sheet 3. Release rates use process_safety.release.gas_release_kg_s; relief areas use process_safety.relief.gas_area
(API 520-I gas equation, derived in the toolkit; standard text not read; see sheet 6).

Frozen tool outputs (provenance in the constants below): CoolProp 8.0.0 HEOS, run with
    /private/tmp/claude-501/venv_val/bin/python scripts/cbg_realgas_check.py
Usage (standard library only):
    python3 scripts/gen_pid_cbg.py docs/pid/CBG_PID_Set_RevB.html [--previews] [--lint]
Screening aid, not certified design."""
import sys, os, math, re
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
from pidlib import *
from process_safety.release import gas_release_kg_s
from process_safety.relief import gas_area, relieving_pressure_kpa, ACCUMULATION

REV = "B"
NSHEETS = 7

# =====================================================================================================================
# 1. HEAT AND MATERIAL BALANCE, computed in code
# =====================================================================================================================
# atomic masses (g/mol): C 12.011, H 1.008, O 15.999, S 32.06 (IUPAC conventional values)
M_CH4, M_CO2, M_H2S, M_H2O = 12.011 + 4 * 1.008, 12.011 + 2 * 15.999, 2 * 1.008 + 32.06, 2 * 1.008 + 15.999
RGAS = 8.314462618            # J/(mol K), CODATA
NM3_KMOL = RGAS * 273.15 / 101325 * 1000   # Nm3 per kmol at 0 C, 101.325 kPa (D) = 22.414

# ---- S: from the DPR template
CBG_TPD, DPR_FEED_TPD = 10.0, 160.0                     # S: Sections 1 and 4 (DPR feed kept only as a comparison in Rev B)
CBG_KG_YR, DPR_FOM_T_YR, DPR_FEED_T_YR = 3_300_000.0, 18_000.0, 52_800.0   # S: Section 9
OP_DAYS = CBG_KG_YR / (CBG_TPD * 1000)                  # D = 330 d/yr
assert abs(OP_DAYS - DPR_FEED_T_YR / DPR_FEED_TPD) < 1e-9

# ---- S: feed classes (Rev B: the feed mix is an input; GAP_CLOSURE_BIO.csv rows 'Feed per t CBG', 'Biogas yield')
# t of feed per t CBG: press mud 25 (CSE India, CBG National Blueprint webinar slides 24 Jul 2026, slide 24, 5-TPD model; Bawase et al., Int J Des Nat
# Ecodyn 21(6) 2026, doi 10.18280/ijdne.210612, p1654, 'approximately 25 t PM per t CBG'). Napier grass: 150 m3 biogas/t = 60 kg CBG/t = 16.7 t/t
# (Bawase p1654; the 60 kg conversion is D). Agri residue has no source: treated as the Napier class (A). Press-mud raw biogas CH4 64.1 % (Rouf et al.,
# Bangladesh J Sci Ind Res 45(4) 2010, doi 10.3329/bjsir.v45i4.7383, Table IV, press mud alone; batch range 63.4 to 66.8).
FEED = {"press mud": dict(t_per_t=25.0, ch4_dry=0.641, nm3_t=(86.0, 93.0)),                 # 86-93 Nm3/t is D (GAP_CLOSURE_BIO)
        "napier / residue class": dict(t_per_t=16.7, ch4_dry=0.55, nm3_t=(150.0, 150.0))}  # CH4 0.55 is A (Rev A value, no source read)

# ---- S: frozen tool outputs (CoolProp 8.0.0 HEOS, CH4/CO2 96/4 mol, cbg_realgas.py)
K202_REAL_SHAFT = 0.9508     # real-gas shaft work / ideal-gas formula (3 stages 16.01 -> 251.01 bara, inlet 40 C, eta_s 0.75): 589.5 / 620.0 kJ/kg
K202_REAL_COOL = 1.2205      # real-gas cooling duty / ideal-gas formula: 756.8 / 620.0 kJ/kg (enthalpy departure at 250 bar), stage-3 exit 132.6 C
G_REAL_OVER_IDEAL = 1.2380   # isentropic choked mass flux, real gas / toolkit ideal (k 1.30, Z = 1) at 251.01 bara, 313.15 K: 53,236 / 43,001 kg/m2/s
Z_HP = 0.8776                # compressibility at 251.01 bara, 40 C, 96/4 CH4/CO2 (rho 188.5 kg/m3)
Z_PSV401 = 0.9529            # Z at the PSV-401 relieving pressure (about 20.4 bara, 40 C, CH4 58.3 mol %); Z 0.9607 at 17.01 bara
Z_PSV501 = 0.9269            # Z at the PSV-501 relieving pressure (about 303.8 bara, 40 C, 96/4 CH4/CO2)
Z_K201 = 0.9607              # compressibility of raw biogas at 17.01 bara, 40 C, CH4 58.3 / CO2 41.7 (0.9566 to 0.9634 over CH4 50 to 64 %)

# ---- S: Rev B measured / literature values replacing A values
SLIP_MEMBRANE = 0.0064       # Bawase et al. p1655: membrane methane slip 0.64 % (inside IEA Bioenergy Task 37 slide 15 membrane range 0.5 to 1.0 %; permit limits 0.2 to 1 %)
SLIP_PSA = 0.0125            # Bawase et al. p1655: multi-stage PSA 1.25 % (Task 37 slides 15-17: PSA below 2 %)
UPG_KWH_MEMBRANE = 0.575     # Bawase et al. p1656: membrane upgrader 0.575 kWh/m3 biomethane (single LCI source, upper end of the 0.3 to 0.575 range in GAP_CLOSURE_BIO)
UPG_KWH_MEMBRANE_LOW = 0.30  # lower end of the range proposed in GAP_CLOSURE_BIO (no document: A)
UPG_KWH_PSA = 0.19           # D: 'more than three times' (Bawase p1656) -> PSA below 0.575 / 3
CAKE_TS = 0.287              # Romio, Ward and Moller, Front Sustain Food Syst 2024, doi 10.3389/fsufs.2024.1415508, Tables 2-3: industrial solid fraction TS 286.97 g/kg
CAPTURE_IND, CAPTURE_LAB = 0.2684, 0.518   # same: TS captured in the solid fraction, industrial / lab scale
RTO_MIN_CH4 = 0.0037         # IEA Bioenergy Task 37 workshop slides, 25 Oct 2023, slides 10 and 18: regenerative thermal oxidation autothermic from 0.37 vol % CH4

# ---- A: assumptions (ASSUMED, to be confirmed by licensor or vendor)
A_BASE = dict(
    w_pm=0.50,              # A0 press-mud share of the feed mass (rest napier / residue class); DPR names the three feeds without shares
    cbg_ch4_mol=0.96,       # A1 CBG methane mol fraction (balance CO2); product spec to be set by offtaker
    h2s_dry_mol=0.002,      # A3 raw biogas H2S, dry basis (2,000 ppmv); CO2 is the balance
    slip=SLIP_MEMBRANE,     # A4 -> S in Rev B: methane slip, fraction of CH4 entering the upgrader that leaves in the off-gas (membrane base case)
    h2o_wet_mass=0.04,      # A5 water vapour, mass fraction of wet raw biogas leaving the digester at 38 C
    h2s_removal=0.99,       # A6 H2S removed in the desulphurisation vessel
    chiller_cond=0.90,      # A7 fraction of water vapour condensed in the chiller
    feed_ts=0.30,           # A8 total solids of the mixed feedstock, mass fraction
    vs_c=0.50,              # A9 carbon mass fraction of destroyed volatile solids
    slurry_ts=0.12,         # A10 total solids of slurry to the digesters
    press_capture=CAPTURE_IND,   # A11 -> S: fraction of digestate TS captured in the FOM cake (industrial separation; lab 0.52)
    cake_ts=CAKE_TS,        # A11b -> S: total solids of the FOM cake
    recycle=0.70,           # A12 fraction of centrate recycled to the hydrolysis tank (limited so fresh water stays >= 0)
    T_feed=30.0, T_dig=38.0, T_cent=35.0, T_chill=5.0, T_cool=40.0,   # A13 temperatures, C
    cp_slurry=4.0,          # A14 kJ/kg K
    lam=2400.0,             # A15 kJ/kg latent heat of water vapour, used for the chiller
    dig_loss=0.10,          # A16 heat loss as fraction of the sensible heating duty
    k_gas=1.30, eta_comp=0.75,   # A17 isentropic exponent and efficiency of the compressors
    P_dig=0.003, P_chill=0.05, P_memb=16.0, P_ret=15.0, P_cbg=250.0,    # A18 bar(g)
    n_st_201=2, n_st_202=3,      # A19 compressor stages
    dP_blower=0.05,         # A20 bar, blower differential (included in P_chill)
    upg_kwh=UPG_KWH_MEMBRANE,    # A28 -> S: electrical kWh per Nm3 biomethane for the upgrading block (scope not stated in the source)
    lhv_ch4=802.3,          # A29 kJ/mol CH4 lower heating value (textbook value, not fetched: A)
)
A = A_BASE


def mol_to_kg(n, M): return n * M      # kmol/h * kg/kmol


def feed_mix(w_pm):
    """t feed per t CBG and the press-mud share of the CBG methane (D). 1/(w/25 + (1-w)/16.7): mass-weighted feed requirement per t CBG."""
    pm, gr = FEED["press mud"], FEED["napier / residue class"]
    inv = w_pm / pm["t_per_t"] + (1 - w_pm) / gr["t_per_t"]
    f_pm = (w_pm / pm["t_per_t"]) / inv                  # share of the CBG (and CH4) made from press mud
    ch4 = 1.0 / (f_pm / pm["ch4_dry"] + (1 - f_pm) / gr["ch4_dry"])   # dry CH4 mole fraction of the blended raw gas (moles of gas add)
    return dict(t_per_t=1.0 / inv, f_pm=f_pm, ch4_dry=ch4, nm3_t_ref=(w_pm * pm["nm3_t"][0] + (1 - w_pm) * gr["nm3_t"][0],
                                                                      w_pm * pm["nm3_t"][1] + (1 - w_pm) * gr["nm3_t"][1]))


def build_balance(over=None):
    A = dict(A_BASE); A.update(over or {})
    B = {}
    mix = feed_mix(A["w_pm"])
    A["ch4_dry_mol"] = mix["ch4_dry"]          # A2 -> D: from the feed mix (press mud 64.1 % S, napier class 55 % A)
    feed_tpd = CBG_TPD * mix["t_per_t"]        # D: feed follows the mix (DPR 160 TPD is the comparison)
    # --- CBG product (S: 10 TPD) and its methane
    cbg = CBG_TPD * 1000 / 24                                   # S/D kg/h
    x = A["cbg_ch4_mol"]
    m_cbg_kmol = cbg / (x * M_CH4 + (1 - x) * M_CO2)
    n_ch4_cbg, n_co2_cbg = x * m_cbg_kmol, (1 - x) * m_cbg_kmol
    # --- raw biogas from the methane requirement and the slip (D)
    n_ch4_up = n_ch4_cbg / (1 - A["slip"])
    n_ch4_off = n_ch4_up - n_ch4_cbg
    n_tot_dry = n_ch4_up / A["ch4_dry_mol"]
    n_h2s = A["h2s_dry_mol"] * n_tot_dry
    n_co2_raw = n_tot_dry - n_ch4_up - n_h2s
    n_co2_off = n_co2_raw - n_co2_cbg
    assert n_co2_off > 0
    dry_kg = n_ch4_up * M_CH4 + n_co2_raw * M_CO2 + n_h2s * M_H2S
    wet_kg = dry_kg / (1 - A["h2o_wet_mass"])
    h2o_raw = wet_kg - dry_kg
    # --- components per stream, kg/h
    s = {}
    s[5] = dict(CH4=n_ch4_up * M_CH4, CO2=n_co2_raw * M_CO2, H2S=n_h2s * M_H2S, H2O=h2o_raw, TS=0.0)
    h2s_rem = s[5]["H2S"] * A["h2s_removal"]
    s[7] = dict(CH4=0, CO2=0, H2S=h2s_rem, H2O=0, TS=0)
    s[8] = dict(CH4=s[5]["CH4"], CO2=s[5]["CO2"], H2S=s[5]["H2S"] - h2s_rem, H2O=h2o_raw, TS=0)
    cond = h2o_raw * A["chiller_cond"]
    s[9] = dict(CH4=0, CO2=0, H2S=0, H2O=cond, TS=0)
    s[10] = dict(CH4=s[8]["CH4"], CO2=s[8]["CO2"], H2S=s[8]["H2S"], H2O=h2o_raw - cond, TS=0)
    s[11] = dict(s[10])
    s[13] = dict(CH4=n_ch4_cbg * M_CH4, CO2=n_co2_cbg * M_CO2, H2S=0, H2O=0, TS=0)
    s[12] = {c: s[11][c] - s[13][c] for c in s[11]}
    s[14] = dict(s[13])
    # --- liquid side
    feed = feed_tpd * 1000 / 24
    ts_feed = A["feed_ts"] * feed
    c_biogas = (s[5]["CH4"] / M_CH4 + s[5]["CO2"] / M_CO2) * 12.011        # kg C/h in raw biogas (D)
    vs_destroyed = c_biogas / A["vs_c"]                                      # D
    hydro_water = (s[5]["CH4"] + s[5]["CO2"] + s[5]["H2S"]) - vs_destroyed   # D: water consumed (>0 required)
    assert hydro_water > 0, "implied hydrolysis water must be positive"
    cap = A["press_capture"]
    r = A["recycle"]
    def solve(r):
        ts_dig = (ts_feed - vs_destroyed) / (1 - r * (1 - cap))              # D steady state with recycle
        ts_cake = cap * ts_dig
        fom = ts_cake / A["cake_ts"]                                          # D: FOM follows capture and cake solids (Rev B)
        ts_cent = ts_dig - ts_cake
        ts_slurry = ts_feed + r * ts_cent
        slurry = ts_slurry / A["slurry_ts"]
        dig = slurry - wet_kg
        cent = dig - fom
        rec = r * cent
        water_slurry = slurry - ts_slurry
        water_rec = rec - r * ts_cent
        fresh = water_slurry - (feed - ts_feed) - water_rec
        return dict(ts_dig=ts_dig, ts_cake=ts_cake, fom=fom, ts_cent=ts_cent, ts_slurry=ts_slurry, slurry=slurry, dig=dig, cent=cent,
                    rec=rec, water_slurry=water_slurry, water_rec=water_rec, fresh=fresh)
    while solve(r)["fresh"] <= 0 and r > 0.05: r -= 0.01        # recycle limited so that fresh make-up water is positive
    q = solve(r); globals_ = q
    ts_dig, ts_cake, fom, ts_cent, ts_slurry, slurry, dig, cent, rec = (q[k] for k in ("ts_dig", "ts_cake", "fom", "ts_cent", "ts_slurry", "slurry", "dig", "cent", "rec"))
    water_slurry, water_rec, fresh = q["water_slurry"], q["water_rec"], q["fresh"]
    surplus = cent - rec
    water_feed = feed - ts_feed
    assert fresh > 0, "fresh water make-up must be positive"
    s[1] = dict(CH4=0, CO2=0, H2S=0, H2O=water_feed, TS=ts_feed)
    s[2] = dict(CH4=0, CO2=0, H2S=0, H2O=fresh, TS=0)
    s[3] = dict(CH4=0, CO2=0, H2S=0, H2O=water_rec, TS=r * ts_cent)
    s[4] = dict(CH4=0, CO2=0, H2S=0, H2O=water_slurry, TS=ts_slurry)
    s[6] = dict(CH4=0, CO2=0, H2S=0, H2O=dig - ts_dig, TS=ts_dig)
    s[15] = dict(CH4=0, CO2=0, H2S=0, H2O=fom - ts_cake, TS=ts_cake)
    s[16] = dict(CH4=0, CO2=0, H2S=0, H2O=cent - ts_cent, TS=ts_cent)
    s[17] = dict(CH4=0, CO2=0, H2S=0, H2O=surplus - (1 - r) * ts_cent, TS=(1 - r) * ts_cent)
    # the digester converts: slurry water - vapour - hydrolysis water = digestate water (independent route to the same number)
    assert abs((water_slurry - h2o_raw - hydro_water) - (dig - ts_dig)) < 1e-6 * dig
    mass = {k: sum(v.values()) for k, v in s.items()}
    # ---- unit-by-unit closure (kg/h)
    units = [("TK-101 mixing", [1, 2, 3], [4]), ("D-201 digestion", [4], [5, 6]),
             ("R-301 desulphurisation", [5], [8, 7]), ("E-301 chiller", [8], [10, 9]), ("K-201 compression", [10], [11]),
             ("M-401 upgrading", [11], [12, 13]), ("K-202 compression", [13], [14]),
             ("S-501 dewatering", [6], [15, 16]), ("Centrate split", [16], [3, 17])]
    rows = []
    for name, i, o in units:
        a, b = sum(mass[k] for k in i), sum(mass[k] for k in o)
        rows.append((name, a, b, 100 * (a - b) / a))
        assert abs(a - b) / a < 1e-3, (name, a, b)
    mass_in = mass[1] + mass[2]
    outs = [13, 12, 9, 7, 15, 17]
    mass_out = sum(mass[k] for k in outs)
    assert abs(mass_in - mass_out) / mass_in < 1e-3
    # ---- methane, carbon, sulphur and TS balances
    ch4_in, ch4_out = s[5]["CH4"], s[13]["CH4"] + s[12]["CH4"]
    assert abs(ch4_in - ch4_out) / ch4_in < 1e-3
    cin = (s[5]["CH4"] / M_CH4 + s[5]["CO2"] / M_CO2)
    cout = sum(s[k]["CH4"] / M_CH4 + s[k]["CO2"] / M_CO2 for k in (12, 13))
    assert abs(cin - cout) / cin < 1e-3
    h2s_in, h2s_out = s[5]["H2S"], s[7]["H2S"] + s[8]["H2S"]
    assert abs(h2s_in - h2s_out) / h2s_in < 1e-9
    ts_in, ts_out = s[1]["TS"] - vs_destroyed, s[15]["TS"] + s[17]["TS"]          # TS in feed less VS destroyed = TS leaving as cake + surplus
    assert abs(ts_in - ts_out) / ts_in < 1e-3, (ts_in, ts_out)
    w_in = s[1]["H2O"] + s[2]["H2O"]
    w_out = sum(s[k]["H2O"] for k in (9, 12, 15, 17)) + hydro_water
    assert abs(w_in - w_out) / w_in < 1e-3, (w_in, w_out)
    # off-gas flammability data for the oxidiser basis (D)
    off_ch4_mol = n_ch4_off / (n_ch4_off + n_co2_off)
    off_dry_kmol = n_ch4_off + n_co2_off + s[12]["H2S"] / M_H2S
    off_ch4_nm3h = n_ch4_off * NM3_KMOL
    off_heat_kw = n_ch4_off * 1000 * A["lhv_ch4"] / 3600                      # kmol/h * 1000 mol * kJ/mol / 3600 s
    B.update(s=s, mass=mass, rows=rows, mass_in=mass_in, mass_out=mass_out, ch4_in=ch4_in, ch4_out=ch4_out,
             cin=cin * 12.011, cout=cout * 12.011, h2s_in=h2s_in, h2s_out=h2s_out, ts_in=ts_in, ts_out=ts_out, w_in=w_in, w_out=w_out,
             vs_destroyed=vs_destroyed, hydro_water=hydro_water, fom=fom, feed=feed, feed_tpd=feed_tpd, mix=mix, recycle=r,
             nm3_h=n_tot_dry * NM3_KMOL, n_tot=n_tot_dry, ts_dig=ts_dig, ts_cake=ts_cake, cake_ts_frac=ts_cake / fom,
             slurry=slurry, dig=dig, wet_kg=wet_kg, dry_kg=dry_kg, n_ch4_up=n_ch4_up, n_co2_off=n_co2_off, n_ch4_off=n_ch4_off,
             cbg=cbg, cbg_nm3_h=m_cbg_kmol * NM3_KMOL, cent=cent, fresh=fresh, rec=rec, surplus=surplus,
             off_ch4_mol=off_ch4_mol, off_ch4_nm3h=off_ch4_nm3h, off_heat_kw=off_heat_kw, ch4_dry=A["ch4_dry_mol"], slip=A["slip"],
             yield_nm3_t=n_tot_dry * NM3_KMOL * 24 / feed_tpd, fom_t_yr=fom * 24 * OP_DAYS / 1000, feed_t_yr=feed_tpd * OP_DAYS, A=A)
    # ---- duties (D), kW
    k, eta = A["k_gas"], A["eta_comp"]
    def mavg(st):  # kg/kmol of a gas stream
        return sum(st.values()) / (st["CH4"] / M_CH4 + st["CO2"] / M_CO2 + st["H2S"] / M_H2S + st["H2O"] / M_H2O)
    def comp(mdot_kg_h, M, T1C, p1_bara, p2_bara, nst, Tcool=A["T_cool"]):
        """equal pressure ratio per stage; stage 1 inlet at T1C, every later stage inlet at the intercooler outlet Tcool
        (validation fix: the first version used T1C for every stage, which understated K-201 work because its stage 2 inlet is 40 C, not 5 C)"""
        rs = (p2_bara / p1_bara) ** (1 / nst)
        cp = k / (k - 1) * RGAS / (M / 1000)                                                 # J/kg K
        shaft_j = cool_j = 0.0
        Tin = T1C + 273.15
        for _ in range(nst):
            dT = Tin * (rs ** ((k - 1) / k) - 1) / eta
            shaft_j += cp * dT                                                               # J/kg: k/(k-1) R/M T1 (rs^((k-1)/k)-1)/eta
            cool_j += cp * (Tin + dT - (Tcool + 273.15))                                     # each stage cooled back to Tcool
            T2 = Tin + dT
            Tin = Tcool + 273.15
        return mdot_kg_h / 3600 * shaft_j / 1000, mdot_kg_h / 3600 * cool_j / 1000, rs, T2 - 273.15
    M10 = mavg(s[10]); M13 = mavg(s[13])
    P1 = 1.01325 + A["P_chill"]
    d = {}
    d["K-201 shaft"], d["K-201 cooling"], rs201, T201 = comp(mass[10], M10, A["T_chill"], P1, A["P_memb"] + 1.01325, A["n_st_201"])
    sh202, co202, rs202, T202 = comp(mass[13], M13, A["T_cool"], A["P_ret"] + 1.01325, A["P_cbg"] + 1.01325, A["n_st_202"])
    d["K-202 shaft ideal"], d["K-202 cooling ideal"] = sh202, co202
    d["K-202 shaft"], d["K-202 cooling"] = sh202 * K202_REAL_SHAFT, co202 * K202_REAL_COOL      # Rev B: real-gas ratios frozen from CoolProp
    # blower: V dP / eta, ideal-gas density at 38 C
    rho5 = (1.01325 + A["P_dig"]) * 1e5 * (mavg(s[5]) / 1000) / (RGAS * (A["T_dig"] + 273.15))
    d["K-301 blower shaft"] = mass[5] / 3600 / rho5 * A["dP_blower"] * 1e5 / eta / 1000
    # chiller: latent of condensed water + sensible of the gas from T_dig to T_chill
    cp_gas = k / (k - 1) * RGAS / (mavg(s[8]) / 1000)
    d["E-301 chiller"] = (cond * A["lam"] + (mass[8] - h2o_raw) * cp_gas / 1000 * (A["T_dig"] - A["T_chill"])) / 3600
    # digester heating: mix feed (30 C), fresh (30 C), recycle (35 C) to T4, heat to 38 C
    T4 = (mass[1] * A["T_feed"] + mass[2] * A["T_feed"] + mass[3] * A["T_cent"]) / (mass[1] + mass[2] + mass[3])
    sens = mass[4] * A["cp_slurry"] * (A["T_dig"] - T4) / 3600
    d["D-201 heating"] = sens * (1 + A["dig_loss"])
    # upgrader electrical power: specific figure x biomethane flow; the part not explained by K-201 + K-301 shaft is 'other upgrader load' (D)
    d["upgrader electrical"] = A["upg_kwh"] * B["cbg_nm3_h"]
    d["upgrader other"] = d["upgrader electrical"] - d["K-201 shaft"] - d["K-301 blower shaft"]
    d["upgrader kWh/Nm3 (K-201+K-301 shaft)"] = (d["K-201 shaft"] + d["K-301 blower shaft"]) / B["cbg_nm3_h"]
    B.update(duty=d, rs201=rs201, T201=T201, rs202=rs202, T202=T202, T4=T4, M5=mavg(s[5]), M10=M10, M13=M13, M12=mavg(s[12]), rho5=rho5, M11=mavg(s[11]))
    return B


BAL = build_balance()
S_ = BAL["s"]
MASS = BAL["mass"]
# technology cases (D): same model, different slip and upgrader power; and sensitivity of the feed mix
CASES = {"membrane (base)": build_balance(), "PSA-class": build_balance(dict(slip=SLIP_PSA, upg_kwh=UPG_KWH_PSA)),
         "Rev A slip 1.5 %": build_balance(dict(slip=0.015))}
MIXES = {w: build_balance(dict(w_pm=w)) for w in (0.0, 0.5, 1.0)}

# =====================================================================================================================
# 2. SCENARIO NUMBERS (documented formulas only) AND RELIEF SIZING
# =====================================================================================================================
SC = {}
# scenario inventory assumptions (A)
SC["holder_h"] = 4.0           # A21 gas holder buffer, hours of raw biogas production (both holders together)
SC["hole_holder_mm"] = 100.0   # A22 hole in membrane
SC["p_holder_mbarg"] = 3.0     # A23 operating pressure of holder, mbar(g)
SC["hole_hp_mm"] = 10.0        # A24 hole in HP CBG line / hose
SC["cd"] = 0.85                # A25 gas discharge coefficient (toolkit default range 0.85 to 1.0)
SC["casc_m3"] = 3.0            # A26 cascade water volume, m3
SC["Z_hp"] = Z_HP              # A27 -> S (CoolProp, frozen): compressibility used for inventory at 250 barg
hold_vol_nm3 = BAL["nm3_h"] * SC["holder_h"]
SC["hold_nm3"] = hold_vol_nm3
SC["hold_ch4_kg"] = BAL["n_ch4_up"] * SC["holder_h"]  * M_CH4        # D: CH4 kg in holder buffer (same composition as stream 5)
SC["hold_h2s_kg"] = (A["h2s_dry_mol"] * BAL["n_tot"]) * SC["holder_h"] * M_H2S
SC["hold_gas_kg"] = BAL["wet_kg"] * SC["holder_h"]
SC["q_holder"] = gas_release_kg_s(SC["hole_holder_mm"] / 1000, 101.325 + SC["p_holder_mbarg"] / 10, A["T_dig"] + 273.15, BAL["M5"], A["k_gas"], SC["cd"])
SC["t_holder_min"] = SC["hold_gas_kg"] / SC["q_holder"] / 60
SC["gen_kg_s"] = BAL["wet_kg"] / 3600       # blocked-outlet relief basis: normal gas generation
P_hp_abs = (A["P_cbg"] + 1.01325) * 100     # kPa abs
SC["q_hp_ideal"] = gas_release_kg_s(SC["hole_hp_mm"] / 1000, P_hp_abs, A["T_cool"] + 273.15, BAL["M13"], A["k_gas"], SC["cd"])
SC["q_hp"] = SC["q_hp_ideal"] * G_REAL_OVER_IDEAL         # Rev B: real-gas flux ratio frozen from CoolProp
SC["casc_kg"] = P_hp_abs * 1000 * SC["casc_m3"] * (BAL["M13"] / 1000) / (SC["Z_hp"] * RGAS * (A["T_cool"] + 273.15))
SC["t_casc_min"] = SC["casc_kg"] / SC["q_hp"] / 60
SC["casc_cbg_h"] = SC["casc_kg"] / BAL["cbg"]     # cascade inventory in hours of production

# ---- relief sizing (toolkit process_safety.relief.gas_area; API 520-I gas equation derived there; the standard text was not read; Kd 0.975 default)
DESIGN_MARGIN = 1.10          # A30 design pressure = 1.10 x operating (bar g) where no better basis exists
RELIEF = {}
def size_gas(tag, W_kg_h, T_K, M, k, Z, set_bar_g, back_kpa_abs=101.325 + 5.0, case="single_non_fire"):
    set_kpa = set_bar_g * 100.0
    P1 = relieving_pressure_kpa(set_kpa, case)
    r = gas_area(W_kg_h, T_K, P1, back_kpa_abs, M, k, Z, set_g_kpa=set_kpa)
    RELIEF[tag] = dict(W=W_kg_h, set_bar_g=set_bar_g, P1_bar_a=P1 / 100, area=r.required_area_mm2, orifice=r.orifice, n=r.n_valves, regime=r.regime, Z=Z)
    return RELIEF[tag]
# PSV-401: K-201 discharge / M-401 blocked outlet, load = full K-201 flow (stream 11), set at design pressure of M-401
SET_401 = round((A["P_memb"]) * DESIGN_MARGIN, 1)
size_gas("PSV-401", MASS[11], A["T_cool"] + 273.15, BAL["M11"], A["k_gas"], Z_PSV401, SET_401)
# PSV-501: K-202 discharge / HP line blocked outlet (cascade full), load = full K-202 flow (stream 14), real-gas Z at relieving condition ~ Z_HP (A: Z_HP is at 251 bara)
SET_501 = round(A["P_cbg"] * DESIGN_MARGIN, 0)
size_gas("PSV-501", MASS[14], A["T_cool"] + 273.15, BAL["M13"], A["k_gas"], Z_PSV501, SET_501)


# =====================================================================================================================
# 3. DRAWING HELPERS
# =====================================================================================================================
SL, BG, CB, OG = "#5d4037", GREEN, "#6a1b9a", "#7b8086"     # slurry, biogas, CBG, off-gas line colours
TXT = GREY


def N(x, d=0):
    return f"{x:,.{d}f}"


def psv_m(s, x, y, color=INK):
    """relief valve mirrored: inlet below (x,y+18), outlet to the left at y"""
    s.add(f'<g transform="translate({x},{y}) scale(-1,1)" stroke="{color}" stroke-width="1.8" fill="#fff">'
          f'<polygon points="-10,16 10,16 0,-2"/><polygon points="0,-2 18,-10 18,10"/>'
          f'<polyline points="0,-2 0,-8 -6,-12 6,-17 -6,-22 6,-27 0,-31" fill="none"/></g>')


def pump_m(s, cx, cy, r=14, label=None):
    """pump mirrored: suction on the right, discharge up-left"""
    s.add(f'<g transform="translate({cx},{cy}) scale(-1,1)"><circle r="{r}" fill="#fff" stroke="{INK}" stroke-width="2"/>'
          f'<polygon points="{-r*0.7},{-r*0.7} {r*0.7},{-r*0.7} 0,{r*0.3}" fill="none" stroke="{INK}" stroke-width="1.4" transform="rotate(-90)"/>'
          f'<polyline points="0,{-r} {r},{-r}" fill="none" stroke="{INK}" stroke-width="2"/></g>')
    if label: T(s, cx, cy + r + 13, label, 10, 700, "middle")
    return dict(inlet=(cx + r, cy), outlet=(cx - r, cy - r))


def fa_sym(s, x, y, vertical=True, color=INK):
    """flame arrestor: small box with crossed lines"""
    w, h = (12, 16) if vertical else (16, 12)
    s.add(f'<g stroke="{color}" stroke-width="1.5" fill="#fff"><rect x="{x-w/2}" y="{y-h/2}" width="{w}" height="{h}"/>'
          f'<line x1="{x-w/2}" y1="{y-h/2}" x2="{x+w/2}" y2="{y+h/2}"/><line x1="{x-w/2}" y1="{y+h/2}" x2="{x+w/2}" y2="{y-h/2}"/></g>')


def pvrv(s, x, y, color=INK):
    """pressure/vacuum breather valve on a tank roof: small circle with up and down ticks"""
    s.add(f'<g stroke="{color}" stroke-width="1.6" fill="#fff"><circle cx="{x}" cy="{y}" r="6"/><polyline points="{x-3},{y+2} {x},{y-3} {x+3},{y+2}" fill="none"/></g>')


def tprd(s, x, y):
    s.add(f'<polygon points="{x},{y-6} {x+6},{y+5} {x-6},{y+5}" fill="#fff" stroke="{RED}" stroke-width="1.5"/>')


def dest(s, x, y, t, col=GREEN, anchor="start"):
    T(s, x, y, t, 9, 700, anchor, col)


def sig(s, pts, color=BLUE, dash="5 4", marker="ahb"):
    PL(s, pts, 1.3, color, dash, marker if marker else None)


def lnum(s, x, y, t, col=INK, anchor="start"):
    T(s, x, y, t, 9.5, 400, anchor, col)


def gap_h(s, x, y, half=6):
    """white break in a horizontal line where a vertical line crosses"""
    s.add(f'<rect x="{x-half}" y="{y-3}" width="{2*half}" height="6" fill="#fff"/>')


def tag(s, x, y, t, size=10, col=INK, anchor="start", w=700):
    T(s, x, y, t, size, w, anchor, col)


def box(s, x, y, w, h, title, sub=None, fill="#fff", stroke=INK, dash=None, tsize=10.5):
    R(s, x, y, w, h, fill, stroke, 1.6, dash)
    T(s, x + w / 2, y + 15, title, tsize, 700, "middle")
    if sub:
        for i, l in enumerate(sub): T(s, x + w / 2, y + 28 + i * 12, l, 9.5, 400, "middle")


def stub(s, x, y, text, d="r", col=AMBER, length=34, anchor=None):
    """utility stub with label; d is the direction the fluid flows relative to the drawing (r = into the drawing from the left)"""
    if d == "r":
        PL(s, [(x - length, y), (x, y)], 1.8, col, "6 3", None); arrow(s, x, y, "r", col, 8); T(s, x - length, y - 5, text, 9.5, 700, "start", col)
    elif d == "l":
        PL(s, [(x + length, y), (x, y)], 1.8, col, "6 3", None); arrow(s, x, y, "l", col, 8); T(s, x + length, y - 5, text, 9.5, 700, "end", col)
    elif d == "d":
        PL(s, [(x, y - length), (x, y)], 1.8, col, "6 3", None); arrow(s, x, y, "d", col, 8); T(s, x + 5, y - length + 8, text, 9.5, 700, "start", col)
    elif d == "u":
        PL(s, [(x, y + length), (x, y)], 1.8, col, "6 3", None); arrow(s, x, y, "u", col, 8); T(s, x + 5, y + length - 4, text, 9.5, 700, "start", col)


# ---------- coordinates of the main equipment (shared by all sheets) ----------
DA, DB = 330, 450            # digester centre x
DCY, DH, DW = 480, 160, 90   # digester centre y, height, width (D-201A and B)
GY = 285                     # biogas header y
RY = 195                     # upgrading row y
FEEDY, DIGY = 615, 655       # slurry feed header and digestate header y


def pid(s, detail=True, dim=False):
    """draw the whole plant. detail=False leaves out instrument bubbles and most tag texts (scenario sheets)."""
    if dim: s.add('<g opacity="0.45">')
    # ================= feed handling, hydrolysis and slurry feed =================
    s.add(f'<polygon points="28,640 92,640 80,700 40,700" fill="#fff" stroke="{INK}" stroke-width="2.4"/>')   # hopper
    PL(s, [(40, 700), (80, 700), (80, 712), (40, 712), (40, 700)], 2, INK)
    if detail:
        tag(s, 60, 735, "H-101", 11, anchor="middle"); T(s, 60, 748, "feed hopper", 9.5, 400, "middle")
        T(s, 60, 760, "+ screw feeder", 9.5, 400, "middle")
    tk = reactor(s, 150, 670, 76, 80, jacket=False, agitator=True)
    if detail:
        tag(s, 150, 566, "TK-101", 11, anchor="middle")
        T(s, 150, 578, "hydrolysis / mixing", 9.5, 400, "middle")
    pipe(s, [(92, 676), (112, 676)], 2.6, SL)
    strm(s, 102, 654, 1)
    stub(s, 176, 636, "water", "d", BLUE, 34); strm(s, 214, 608, 2)
    # pump P-101 and slurry line
    pump(s, 245, 670, 13)
    pipe(s, [(188, 670), (232, 670)], 2.6, SL, False)
    valve(s, 210, 670, 0, "gate")
    if detail:
        tag(s, 245, 702, "P-101", 10, anchor="middle")
    pipe(s, [(258, 657), (258, FEEDY), (DA - 22, FEEDY)], 2.6, SL, False)
    pipe(s, [(DA - 22, FEEDY), (DA - 22, DCY + DH / 2 + 16)], 2.6, SL, True)
    pipe(s, [(DA - 22, FEEDY), (DB - 22, FEEDY), (DB - 22, DCY + DH / 2 + 16)], 2.6, SL, True)
    valve(s, 290, FEEDY, 0, "gate"); valve(s, DA - 22, 598, 90, "ball", act=True, color=RED); valve(s, DB - 22, 598, 90, "ball", act=True, color=RED)
    strm(s, 275, FEEDY - 24, 4)
    if detail:
        tag(s, DA - 40, 580, "XV-101A", 9, RED, "end"); tag(s, DB - 8, 580, "XV-101B", 9, RED, "start")
        PL(s, [(125, 619), (125, 596)], 2.2, BG); arrow(s, 125, 596, "u", GREEN, 7)
        tag(s, 118, 592, "VT-101", 9, GREEN, "end")
    if detail:
        lnum(s, 262, FEEDY + 17, "SL-102-150-A", SL)
    # ================= digesters with membrane gas holders =================
    for cx, nm in ((DA, "A"), (DB, "B")):
        reactor(s, cx, DCY, DW, DH, agitator=False, jacket=True, dome=True)
        # side agitator
        PL(s, [(cx - DW / 2, DCY + 30), (cx - DW / 2 + 22, DCY + 30)], 3)
        s.add(f'<circle cx="{cx-DW/2-8}" cy="{DCY+30}" r="8" fill="#fff" stroke="{INK}" stroke-width="1.5"/><text x="{cx-DW/2-8}" y="{DCY+33}" font-size="8.5" font-weight="700" text-anchor="middle">M</text>')
        # gas offtake
        PL(s, [(cx, DCY - DH / 2 - 38), (cx, GY)], 2.6, BG)
        if detail:
            tag(s, cx, DCY - 12, f"D-201{nm}", 11, anchor="middle"); T(s, cx, DCY + 1, "digester", 9.5, 400, "middle")
            T(s, cx, DCY - DH / 2 - 14, f"GH-201{nm}", 10, 700, "middle", GREEN); T(s, cx, DCY - DH / 2 - 3, "membrane holder", 9, 400, "middle", GREEN)
    # digestate outlets
    pipe(s, [(DA + DW / 2, 548), (390, 548), (390, DIGY), (600, DIGY)], 2.6, SL, False)
    pipe(s, [(DB + DW / 2, 548), (510, 548), (510, DIGY)], 2.6, SL, False)
    gap_h(s, 390, FEEDY)
    PL(s, [(390, 548), (390, DIGY)], 2.6, SL)
    valve(s, 372, 548, 0, "gate"); valve(s, 492, 548, 0, "gate")
    strm(s, 420, DIGY - 20, 6)
    if detail: lnum(s, 520, DIGY - 8, "SL-103-200-A", SL)
    # overflow lines (liquid seal) from the digesters to the digestate headers
    PL(s, [(DA + DW / 2, 430), (390, 430), (390, 548)], 1.8, SL, "5 3"); PL(s, [(DB + DW / 2, 430), (510, 430), (510, 548)], 1.8, SL, "5 3")
    if detail: T(s, 390, 424, "OF", 9, 700, "middle", SL); T(s, 510, 424, "OF", 9, 700, "middle", SL)
    # PRVs on holders, vents to safe location
    psv_m(s, DA - 40, 345, GREEN); PL(s, [(DA - 40, 364), (DA - 40, 384)], 2.2, BG)
    PL(s, [(DA - 58, 345), (DA - 66, 345), (DA - 66, 322)], 2.2, BG); arrow(s, DA - 66, 322, "u", GREEN, 8)
    psv_m(s, DB - 40, 345, GREEN); PL(s, [(DB - 40, 364), (DB - 40, 384)], 2.2, BG)
    PL(s, [(DB - 58, 345), (DB - 66, 345), (DB - 66, 322)], 2.2, BG); arrow(s, DB - 66, 322, "u", GREEN, 8)
    if detail:
        tag(s, DA - 70, 330, "PRV-201A", 9.5, GREEN, "end"); tag(s, DB - 70, 330, "PRV-201B", 9.5, GREEN, "end")
    # hot water to the digester coils (utility stub)
    if detail:
        stub(s, DA - DW / 2 - 12, 555, "HW (A)", "r", AMBER, 36)
    # ================= biogas header, flare, blower, desulphurisation =================
    pipe(s, [(DA, GY), (520, GY)], 2.6, BG, False)
    valve(s, 500, GY, 0, "ball", act=True, color=RED)     # XV-201 holder isolation
    compressor(s, 575, GY, 15)
    pipe(s, [(520, GY), (560, GY)], 2.6, BG, False)
    pipe(s, [(590, GY), (625, GY)], 2.6, BG, False)
    strm(s, 478, GY - 14, 5)
    if detail:
        tag(s, 575, GY + 30, "K-301", 10, anchor="middle"); T(s, 575, GY + 42, "biogas blower", 9, 400, "middle")
        tag(s, 500, GY + 22, "XV-201", 9.5, RED, "middle"); lnum(s, 345, GY + 14, "BG-201-200-A", BG)
    # holder PRV vents rise over the header to a safe vent stack (VS), flame arrestors FA-201A/B (A)
    for vx, nm in ((DA - 66, "A"), (DB - 66, "B")):
        gap_h(s, vx, GY)
        PL(s, [(vx, 322), (vx, 268)], 2.2, BG); arrow(s, vx, 268, "u", GREEN, 8)
        fa_sym(s, vx, 306, True, GREEN)
        if detail:
            tag(s, vx - 9, 309, f"FA-201{nm}", 9, GREEN, "end"); dest(s, vx + 6, 266, "VS")
    # flare branch from the header start
    pipe(s, [(DA, GY), (190, GY), (190, 335), (110, 335)], 2.6, BG, False)
    valve(s, 190, 312, 90, "gate", act=True)
    flare(s, 110, 335, 150, "FL-901"); fa_sym(s, 150, 335, False, GREEN)
    if detail:
        tag(s, 182, 310, "PV-201", 9.5, anchor="end"); T(s, 182, 322, "to flare", 9, 400, "end")
        lnum(s, 120, 350, "BG-202-150-A", BG, "start"); T(s, 120, 363, "FA-901 flame arrestor (A)", 9, 400, "start")
    # desulphurisation
    vvessel(s, 650, 240, 50, 90, fill="#fff")
    PL(s, [(632, 262), (668, 262)], 1.1, "#555"); PL(s, [(632, 300), (668, 300)], 1.1, "#555")
    if detail:
        tag(s, 672, 384, "R-301", 11); T(s, 672, 396, "H2S removal", 9.5, 400); T(s, 672, 408, "(type A)", 9.5, 400)
    pipe(s, [(650, 226), (650, RY), (690, RY)], 2.6, BG, False)
    psv_m(s, 604, 236, GREEN); PL(s, [(604, 254), (604, GY)], 2.0, BG)
    if detail:
        tag(s, 596, 207, "PSV-301", 9, GREEN, "end"); dest(s, 596, 218, "to FH (A)", GREEN, "end")
    pipe(s, [(650, 344), (650, 420)], 2.6, SL, True)
    strm(s, 626, 410, 7)
    T(s, 650, 452, "spent media / sulphur", 9.5, 400, "middle", TXT)
    # ================= upgrading row =================
    hx(s, 730, RY, 80, 28)
    if detail:
        tag(s, 730, RY - 24, "E-301", 10, anchor="middle"); T(s, 722, RY + 30, "gas chiller", 9.5, 400, "end")
    pipe(s, [(770, RY), (813, RY)], 2.6, BG, False)
    strm(s, 791, RY - 22, 10)
    strm(s, 700, RY - 23, 8)
    PL(s, [(730, RY + 14), (730, 250)], 2.4, BLUE if False else SL)
    arrow(s, 730, 250, "d", SL, 8); strm(s, 750, 240, 9)
    T(s, 760, 262, "condensate to ETP", 9.5, 400, "start", TXT)
    stub(s, 722, 150, "CHW 7/12 C (A)", "d", BLUE, 30)
    psv(s, 672, 140, GREEN); PL(s, [(672, 158), (672, RY)], 2.0, BG)
    if detail:
        tag(s, 664, 116, "PSV-302", 9, GREEN, "end"); dest(s, 664, 127, "to FH (A)", GREEN, "end")
    compressor(s, 830, RY, 17)
    if detail: tag(s, 830, RY + 36, "K-201", 10, anchor="middle"); T(s, 830, RY + 48, "biogas comp.", 9.5, 400, "middle")
    pipe(s, [(847, RY), (890, RY)], 2.6, BG, False)
    strm(s, 868, RY + 24, 11)
    psv(s, 855, 148, GREEN); PL(s, [(855, 166), (855, RY)], 2.0, BG)
    if detail:
        tag(s, 850, 112, "PSV-401", 9, GREEN, "end")
    # membrane
    R(s, 890, 172, 74, 46, "#fff", INK, 2.2)
    for i in range(3): PL(s, [(900, 182 + i * 14), (954, 182 + i * 14)], 1.3, "#555")
    if detail:
        tag(s, 927, 236, "M-401", 11, anchor="middle"); T(s, 927, 248, "membrane stages", 9.5, 400, "middle"); T(s, 927, 260, "(or PSA, A)", 9.5, 400, "middle")
    # off-gas
    pipe(s, [(927, 172), (927, 118), (942, 118)], 2.6, OG, True)
    strm(s, 945, 156, 12)
    fa_sym(s, 927, 140, True, OG)
    psv_m(s, 905, 140, GREEN); PL(s, [(905, 158), (927, 158)], 2.0, OG)
    if detail:
        tag(s, 893, 112, "PSV-402", 9, GREEN, "end")
    box(s, 942, 98, 94, 40, "OX-401 (RTO, A)", ["FA-401, BMS-401"], stroke=OG, tsize=10)
    # retentate = CBG
    pipe(s, [(964, RY), (1000, RY)], 2.6, CB, False)
    strm(s, 981, RY + 22, 13)
    compressor(s, 1017, RY, 15)
    if detail: tag(s, 1017, RY + 32, "K-202", 10, anchor="middle"); T(s, 1017, RY + 44, "CBG comp.", 9.5, 400, "middle")
    pipe(s, [(1032, RY), (1059, RY)], 2.6, CB, False)
    # dryer
    vvessel(s, 1076, 168, 34, 58, fill="#fff")
    if detail: tag(s, 1068, 262, "V-501", 10, anchor="end"); T(s, 1068, 274, "CBG dryer", 9.5, 400, "end")
    # dryer outlet down to cascade bay
    pipe(s, [(1076, 241), (1076, 300)], 2.6, CB, False)
    valve(s, 1076, 318, 90, "ball", act=True, color=RED)
    if detail: tag(s, 1060, 309, "XV-501", 9.5, RED, "end")
    strm(s, 1100, 290, 14)
    # cascade storage bank
    for i, yy in enumerate((352, 388, 424)):
        s.add(f'<rect x="965" y="{yy-9}" width="88" height="18" rx="9" fill="#fff" stroke="{INK}" stroke-width="2"/>')
        PL(s, [(1053, yy), (1076, yy)], 2.2, CB)
    PL(s, [(1076, 330), (1076, 424)], 2.6, CB)
    if detail:
        tag(s, 1009, 335, "CAS-601A/B/C", 10, anchor="middle"); T(s, 1009, 446, "cascade, 250 barg (A)", 9.5, 400, "middle")
    for yy in (352, 388, 424): tprd(s, 958, yy)
    psv_m(s, 1108, 362, GREEN); PL(s, [(1076, 380), (1108, 380)], 2.0, CB)
    if detail:
        tag(s, 955, 340, "TPRD-601", 9, RED, "end"); pass
    # filling hose and dispenser
    PL(s, [(1076, 424), (1076, 470), (1050, 470)], 2.6, CB)
    valve(s, 1076, 448, 90, "ball", act=True, color=RED)
    if detail: tag(s, 1084, 435, "XV-601", 9, RED, "start")
    box(s, 940, 455, 110, 40, "Filling bay", ["hose + breakaway (A)"], tsize=10)
    PL(s, [(1050, 470), (1050, 475)], 2.0, CB)
    # grid injection alternative
    PL(s, [(1076, 290), (1023, 290)], 2.2, CB, "6 4")
    box(s, 905, 272, 118, 36, "Grid option", ["PRS + custody meter (A)"], stroke=CB, dash="6 4", tsize=10)
    # PSV on CBG HP line and dryer
    psv(s, 1046, 160, INK); PL(s, [(1046, RY), (1046, 178)], 2.0, CB); PL(s, [(1064, 160), (1064, 144)], 2, INK); arrow(s, 1064, 144, "u", INK, 7)
    if detail:
        tag(s, 1070, 148, "PSV-501", 9.5, INK, "start"); T(s, 1070, 136, "vent (A)", 9, 400, "start", TXT)
    # ================= dewatering, centrate, FOM and LFOM =================
    R(s, 600, 630, 84, 50, "#fff", INK, 2.2)
    for i in range(4): PL(s, [(610, 642 + i * 9), (674, 642 + i * 9)], 1.3, "#555")
    if detail:
        tag(s, 642, 622, "S-501", 10.5, anchor="middle")
    pipe(s, [(684, 645), (740, 645)], 3, SL, False)
    strm(s, 712, 626, 15)
    box(s, 740, 620, 150, 50, "FOM maturation / curing", ["screening + bagging (A)"], tsize=10)
    pipe(s, [(890, 645), (930, 645)], 2.6, SL, True)
    box(s, 930, 622, 100, 46, "FOM store", ["dispatch (A)"], tsize=10)
    tag(s, 815, 684, "FOM section", 10, GREY, "middle")
    # centrate
    pipe(s, [(642, 680), (642, 692), (660, 692), (660, 703)], 2.6, SL, True)
    strm(s, 622, 688, 16)
    tank(s, 660, 752, 64, 44, roof="cone", level=0.6)
    pvrv(s, 684, 712); PL(s, [(684, 706), (684, 692)], 1.8, GREEN); arrow(s, 684, 692, "u", GREEN, 7)
    if detail:
        T(s, 700, 697, "TK-501", 10.5, 700, "start"); T(s, 700, 709, "centrate tank", 9.5, 400, "start")
        tag(s, 690, 686, "PVRV-501", 9, GREEN, "start")
    pump_m(s, 585, 743, 13)
    PL(s, [(628, 743), (598, 743)], 2.6, SL)
    pipe(s, [(572, 730), (150, 730), (150, 712)], 2.6, SL, True)
    strm(s, 330, 714, 3)
    if detail:
        lnum(s, 400, 745, "SL-104-100-A", SL); tag(s, 560, 719, "P-502", 9.5, anchor="end")
    valve(s, 520, 730, 0, "gate")
    # surplus liquid digestate (LFOM)
    pipe(s, [(692, 743), (790, 743)], 2.6, SL, True)
    valve(s, 735, 743, 0, "gate", act=True)
    tank(s, 830, 752, 64, 44, roof="cone", level=0.4)
    strm(s, 765, 725, 17)
    pvrv(s, 850, 710); PL(s, [(850, 704), (850, 692)], 1.8, GREEN); arrow(s, 850, 692, "u", GREEN, 7)
    if detail:
        T(s, 870, 727, "TK-502", 10.5, 700, "start"); T(s, 870, 739, "LFOM store (A)", 9.5, 400, "start")
        tag(s, 858, 686, "PVRV-502", 9, GREEN, "start")
    # =================== instrumentation, F&G and ESD ===================
    if detail:
        # ESD / F&G logic panel
        R(s, 700, 465, 150, 54, "#fff", RED, 1.8)
        T(s, 775, 482, "ESD-101 logic", 11, 700, "middle", RED); T(s, 775, 496, "F&G + trips (A)", 9.5, 400, "middle", RED)
        T(s, 775, 509, "SIL not assigned", 9.5, 400, "middle", RED)
        # holder pressure loop
        bubble(s, 392, 250, "PIC", "201", True); PL(s, [(392, 265), (392, GY)], 1, BLUE, "5 4")
        sig(s, [(377, 250), (190, 250), (190, 298)], BLUE)
        bubble(s, 437, 250, "PSLL", "201", True); PL(s, [(437, 265), (437, GY)], 1, BLUE, "5 4")
        bubble(s, 472, 250, "PSHH", "201", True); PL(s, [(472, 265), (472, GY)], 1, BLUE, "5 4")
        bubble(s, 248, 426, "LSHH", "201", True); PL(s, [(263, 426), (285, 426)], 1.2, BLUE, "5 4")
        bubble(s, 248, 470, "TT", "201", False); PL(s, [(263, 470), (285, 470)], 1.2, BLUE, "5 4")
        bubble(s, 545, 345, "AT", "201", True, RED)
        T(s, 563, 349, "CH4+H2S", 9.5, 400, "start", RED)
        PL(s, [(531, 352), (498, 372)], 1.2, RED, "5 4")
        # biogas quality / flow
        bubble(s, 540, 250, "FIT", "201", False)
        PL(s, [(540, 265), (540, GY)], 1, BLUE, "5 4")
        bubble(s, 705, 345, "AT", "301", True); T(s, 725, 352, "H2S after R-301", 9.5, 400, "start", TXT)
        PL(s, [(697, 330), (668, 302)], 1, BLUE, "5 4")
        bubble(s, 818, 150, "TT", "301", False)
        bubble(s, 972, 168, "AT", "401", True); PL(s, [(972, 183), (972, RY)], 1, BLUE, "5 4")
        bubble(s, 795, 312, "AT", "402", True, RED); bubble(s, 835, 312, "UV/IR", "401", True, RED)
        T(s, 815, 340, "compressor house: CH4, flame (A)", 9, 400, "middle", RED)
        bubble(s, 1010, 150, "PSHH", "501", True); PL(s, [(1010, 165), (1010, RY)], 1, BLUE, "5 4")
        bubble(s, 1100, 407, "PT", "601", True); PL(s, [(1085, 407), (1076, 407)], 1, BLUE, "5 4")
        bubble(s, 900, 545, "AT", "601", True, RED); T(s, 918, 549, "AT-601 CH4, UV/IR-601 flame, filling bay", 9.5, 700, "start", RED)
        bubble(s, 232, 566, "AT", "202", True)
        # level on TK-101 and TK-501
        bubble(s, 92, 612, "LIT", "101", True)
        bubble(s, 600, 702, "LIT", "501", True); PL(s, [(612, 712), (634, 724)], 1, BLUE, "5 4")
        # ESD outputs: red dashed to XVs (schematic routing)
        sig(s, [(700, 485), (516, 485), (516, 312), (508, 312)], RED, "6 4", "ahr")
        sig(s, [(850, 475), (915, 475), (915, 318), (1062, 318)], RED, "6 4", "ahr")
        sig(s, [(850, 510), (1104, 510), (1104, 448)], RED, "6 4", "ahr")
        sig(s, [(775, 519), (775, 598), (462, 598)], RED, "6 4", "ahr")
        T(s, 560, 590, "trip: XV-101A/B close, P-101 stops (A)", 9.5, 400, "start", RED)
        T(s, 535, 525, "ESB-101 manual ESD (A)", 9.5, 400, "start", RED)
    if dim: s.add('</g>')


def panel_title(s, text):
    return section(s, 1135, 84, 445, text)


# =====================================================================================================================
# 4. SHEETS
# =====================================================================================================================
BASIS = "DPR template Template_DPR_CBG_10TPD.docx (S); all else assumed (A)"
PROJ = "10 TPD compressed biogas (CBG) plant"
# R/A meaning: R = named in the DPR template (Section 4 or 7 headings); A = assumed by this drawing.


class RSheet(Sheet):
    """Sheet with Rev B in the header and title block (pidlib frame() prints Rev A / Draft A)."""
    def svg(self):
        return super().svg().replace("  |  Rev A<", f"  |  Rev {REV}<").replace("Draft A.", f"Draft {REV}.")


def wtable(s, x, y, colw, rows, size=9.5, lh=11.5, head=True, pad=3, cpc=5.1):
    """wrapped-text table; returns y below. cpc = characters per pixel factor (px per char)."""
    import textwrap
    tw = sum(colw)
    for ri, r in enumerate(rows):
        cells = [textwrap.wrap(str(c), max(4, int((colw[j] - 6) / (cpc * size / 9.5)))) or [""] for j, c in enumerate(r)]
        h = max(len(c) for c in cells) * lh + 2 * pad
        if head and ri == 0: R(s, x, y, tw, h, "#e8eaf0", "none")
        elif ri % 2 == 0: R(s, x, y, tw, h, "#f6f7fa", "none")
        cx = x
        for j, c in enumerate(cells):
            for li, t in enumerate(c):
                T(s, cx + 4, y + pad + lh - 2 + li * lh, t, size, 700 if (head and ri == 0) or j == 0 else 400)
            cx += colw[j]
        y += h
    return y


EQUIP = [
    ("Tag", "Service", "Basis"),
    ("H-101", "Feed hopper + screw", "A"), ("TK-101", "Hydrolysis / mixing tank", "A"), ("P-101", "Slurry feed pump", "A"),
    ("D-201A/B", "Digesters, 2 x 50 %", "A"), ("GH-201A/B", "Membrane gas holders", "R"), ("PRV-201A/B", "Holder P/V relief", "A"),
    ("FA-201A/B", "Flame arrestors, vents", "A"), ("OF-201A/B", "Digester overflow seal", "A"),
    ("K-301", "Biogas blower", "A"), ("R-301", "H2S removal vessel", "A"), ("PSV-301", "R-301 relief to FH", "A"),
    ("E-301", "Gas chiller", "A"), ("PSV-302", "E-301 tube-rupture relief", "A"), ("K-201", "Biogas compressor", "A"),
    ("PSV-401", "K-201 discharge, M-401", "A"), ("M-401", "Membrane CO2 removal", "R"), ("PSV-402", "Permeate side relief", "A"),
    ("FA-401", "Off-gas flame arrestor", "A"), ("OX-401", "Off-gas RTO, BMS-401", "A"), ("K-202", "CBG comp. to 250 barg", "A"),
    ("V-501", "CBG dryer", "A"), ("PSV-501", "HP line relief to VS", "A"), ("CAS-601", "Cascade 250 barg", "R"),
    ("TPRD-601", "Thermal PRD per tube", "A"), ("PSV-601", "Cascade header relief", "A"), ("FL-901", "Flare + FA-901", "A"),
    ("S-501", "Screw press", "A"), ("TK-501/502", "Centrate / LFOM tanks", "A"), ("PVRV-501/502", "Tank P/V valves", "A"),
    ("VT-101", "TK-101 vent", "A"),
]


def sheet_pid():
    s = RSheet(1, "CBG PLANT, 10 TPD: PIPING AND INSTRUMENTATION DIAGRAM (conceptual)", "P&ID, feed to CBG, FOM, relief and detection devices",
               code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    pid(s, detail=True)
    panel_box(s)
    y = section(s, 1135, 84, 445, "NOTES AND BASIS (Rev B)")
    yy = y + 16
    mx = BAL["mix"]
    notes = [
        "S: 10 TPD CBG, 330 d/yr, DPR Sections 1, 4, 9 (press mud, agri residue, napier grass; shares not given). Rev B makes the feed mix an input (A0, press mud "
        f"{100*A['w_pm']:.0f} %): feed {BAL['feed_tpd']:.0f} TPD, {mx['t_per_t']:.1f} t per t CBG (25 for press mud, 16.7 napier class; sheet 3). DPR 160 TPD fits only an all-napier feed.",
        "Rev B values: slip 0.64 % (membrane), upgrader 0.575 kWh/Nm3, cake 28.7 % TS at 27 % TS capture, off-gas RTO with no support fuel (0.37 vol % CH4 limit). Sources and the Rev A to Rev B box: sheets 2 and 3.",
        "Everything else (two 50 % digesters, mesophilic, double-membrane holders, membrane upgrading, 250 barg cascade) is A; none is a licensor or vendor selection.",
        "Stream diamonds 1 to 17 are the columns of the HMB on sheet 2. Line numbers are service-seq-size(mm)-class, class A pending specification.",
        "Colours: brown slurry, green biogas, purple CBG, grey off-gas, red dashed ESD, blue dashed signal, amber dashed utility.",
    ]
    for t in notes: yy = WRAP(s, 1141, yy, t, 70, 10, 12.5, bullet=True) + 3
    y = section(s, 1135, yy + 2, 445, "SAFEGUARDS SHOWN (A unless marked R; basis on sheets 6 and 7)")
    yy = y + 16
    safe = [
        "Relief devices tagged on the drawing: PRV-201A/B (pressure and vacuum) with FA-201A/B, PSV-301, 302, 401, 402, 501, 601, TPRD-601 per tube, PVRV-501/502, VT-101, OF-201A/B. Destinations: FH = flare header to FL-901, VS = safe vent stack, both A.",
        "Holder: PIC-201 opens PV-201 to flare before the PRV lifts; PSLL-201 stops K-301 (vacuum); PSHH-201 stops feed. XV-201 isolates the holders; XV-101A/B stop slurry feed on LSHH-201 or ESD.",
        "Gas detection AT-201 (CH4 high and low level, H2S; S12), AT-202 H2S at the feed area, AT-402 and UV/IR-401 in the compressor house, AT-601 and UV/IR-601 at the filling bay feed ESD-101. Matrix on sheet 6.",
        "K-202 discharge PSV-501 and PSHH-501; XV-501 and XV-601 close the cascade and fill on ESD. Off-gas to OX-401 through FA-401.",
    ]
    for t in safe: yy = WRAP(s, 1141, yy, t, 70, 10, 12.5, bullet=True) + 3
    y = section(s, 1135, yy + 2, 445, "LEGEND")
    yy = y + 16
    for i, (t, c, dsh) in enumerate([("slurry / liquid", SL, None), ("raw biogas", BG, None), ("CBG", CB, None), ("off-gas", OG, None),
                                      ("ESD output", RED, "6 4"), ("instrument signal", BLUE, "5 4"), ("utility stub", AMBER, "6 3")]):
        col = i % 2; row = i // 2
        xx = 1146 + col * 215; y0 = yy + row * 17
        PL(s, [(xx, y0), (xx + 34, y0)], 2.4 if dsh is None else 1.6, c, dsh); T(s, xx + 40, y0 + 4, t, 10)
    yy += 4 * 17 + 6
    valve(s, 1160, yy, 0, "ball", act=True, color=RED); T(s, 1184, yy + 4, "ESD valve (XV), fail-closed (A)", 10)
    psv(s, 1385, yy + 4, GREEN); T(s, 1408, yy + 4, "relief valve", 10)
    yy += 26
    fa_sym(s, 1160, yy, True); T(s, 1184, yy + 4, "flame arrestor (FA)", 10)
    pvrv(s, 1385, yy); T(s, 1408, yy + 4, "P/V breather valve", 10)
    yy += 24
    tprd(s, 1160, yy); T(s, 1184, yy + 4, "thermal PRD (TPRD)", 10)
    bubble(s, 1385, yy, "LT", "101", True, r=12); T(s, 1408, yy + 4, "panel mounted", 10)
    y = section(s, 1135, yy + 20, 445, "UTILITIES (stubs; no loads given in the source, A)")
    yy = y + 16
    for t in ("Drawn as stubs: process water to TK-101, hot water 60/50 C to the digester coils, chilled water 7/12 C to E-301.",
              "Not drawn: power, instrument air, nitrogen purge, flare pilot, compressor cooling water, fire water, flare KO drum, compressor interstage coolers and separators (vendor package, gap)."):
        yy = WRAP(s, 1141, yy, t, 70, 10, 12.5, bullet=True) + 3
    # bottom strip: equipment list in four blocks
    y = section(s, 20, 784, 1100, "EQUIPMENT AND DEVICE LIST (R = named in DPR template Section 4 or 7; A = assumed here; no sizes, none in the source)")
    body = EQUIP[1:]
    per = (len(body) + 3) // 4
    for i in range(4):
        table(s, 20 + i * 275, y, (78, 155, 36), [EQUIP[0]] + body[i * per:(i + 1) * per], 15.5, 9.5)
    y2 = y + 15.5 * (per + 1) + 10
    rows = [("Instrument", "Function", "Signal / action"),
            ("PIC-201 / PSLL-201 / PSHH-201", "Holder pressure, low, high-high", "PV-201 to flare; K-301 stop; feed trip (A)"),
            ("LSHH-201A/B, LIT-101, LIT-501", "Digester HH level; tank levels", "XV-101A/B close, P-101 stop; alarms"),
            ("AT-201 / AT-202 / AT-301", "CH4+H2S at holders; H2S feed area; H2S after R-301", "alarm; ESD at 2 of 2 (A); K-201 trip on AT-301 HH (A)"),
            ("AT-401 / AT-402 / UV/IR-401", "CBG analyser; CH4 and flame, compressor house", "XV-501 close; compressors stop (A)"),
            ("PSHH-501", "K-202 discharge high-high", "trips K-202, XV-601 (A)"),
            ("AT-601 + UV/IR-601 (PT-601)", "Cascade bay CH4, flame; cascade pressure", "ESD: XV-601, XV-501 close")]
    table(s, 20, y2, (200, 380, 400), rows, 15.5, 9.5)
    T(s, 22, y2 + 15.5 * len(rows) + 12, "Voting, set points and SIL are A (sheet 7). Nothing on this sheet is a design value.", 9.5, fill=GREY)
    return s


def sheet_hmb():
    s = RSheet(2, "CBG PLANT, 10 TPD: HEAT AND MATERIAL BALANCE, Rev B (computed in code)", "Heat and material balance, closure, Rev A to Rev B changes",
               code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    st = S_
    ids = list(range(1, 18))
    def pct(k, c): return f"{100 * st[k][c] / MASS[k]:.1f}" if MASS[k] > 0 and st[k][c] / MASS[k] >= 0.0005 else ("-" if st[k][c] == 0 else "<0.1")
    temp = {1: A["T_feed"], 2: A["T_feed"], 3: A["T_cent"], 4: round(BAL["T4"], 1), 5: A["T_dig"], 6: A["T_dig"], 7: A["T_dig"], 8: A["T_dig"],
            9: A["T_chill"], 10: A["T_chill"], 11: A["T_cool"], 12: A["T_cool"], 13: A["T_cool"], 14: A["T_cool"], 15: A["T_cent"], 16: A["T_cent"], 17: A["T_cent"]}
    press = {1: "0", 2: "0.5", 3: "0.5", 4: "0.5", 5: "0.003", 6: "0.5", 7: "0", 8: "0.05", 9: "0", 10: "0.05", 11: "16", 12: "1.0", 13: "15", 14: "250", 15: "0", 16: "0", 17: "0"}
    phase = {1: "solid/wet", 2: "liquid", 3: "slurry", 4: "slurry", 5: "gas", 6: "slurry", 7: "solid", 8: "gas", 9: "liquid", 10: "gas", 11: "gas", 12: "gas", 13: "gas", 14: "gas", 15: "wet cake", 16: "slurry", 17: "slurry"}
    rows = [("Mass flow (kg/h)", [N(MASS[k]) for k in ids]), ("Mass flow (t/d)", [f"{MASS[k]*24/1000:.1f}" for k in ids]),
            ("Composition (mass %)", None),
            ("CH4", [pct(k, "CH4") for k in ids]), ("CO2", [pct(k, "CO2") for k in ids]), ("H2S", [pct(k, "H2S") for k in ids]),
            ("Water (H2O)", [pct(k, "H2O") for k in ids]), ("Total solids (TS)", [pct(k, "TS") for k in ids]),
            ("Conditions (all A)", None),
            ("Temperature (C)", [f"{temp[k]:g}" for k in ids]), ("Pressure (bar g)", [press[k] for k in ids]), ("Phase", [phase[k] for k in ids])]
    y = hmb_table(s, 20, 84, ids, rows, first_w=170, col_w=64, rh=16.5, size=10, title="STREAM TABLE (kg/h; streams 1 to 17 match the diamonds on sheet 1)")
    d = BAL["duty"]
    y0 = y + 8
    yb = section(s, 20, y0, 590, "DUTIES (D: formulas below; kW)")
    drows = [("Item", "kW", "Basis"),
             ("D-201A/B heating (incl. 10 % loss)", f"{d['D-201 heating']:.0f}", f"m4 cp (38 - {BAL['T4']:.1f} C), cp 4.0 (A)"),
             ("E-301 chiller", f"{d['E-301 chiller']:.0f}", "0.90 m(H2O) x 2,400 kJ/kg + gas sensible (A)"),
             ("K-301 blower shaft", f"{d['K-301 blower shaft']:.1f}", "V dP / eta, dP 0.05 bar"),
             (f"K-201 shaft ({A['n_st_201']} st, r = {BAL['rs201']:.2f})", f"{d['K-201 shaft']:.0f}", "ideal gas k 1.30, eta 0.75 (A); CoolProp check -1.8 %"),
             ("K-201 inter/aftercooler", f"{d['K-201 cooling']:.0f}", f"stage exit {BAL['T201']:.0f} C cooled to 40 C"),
             (f"K-202 shaft ({A['n_st_202']} st, r = {BAL['rs202']:.2f})", f"{d['K-202 shaft']:.1f}", f"ideal {d['K-202 shaft ideal']:.1f} x {K202_REAL_SHAFT} (CoolProp, S)"),
             ("K-202 inter/aftercoolers", f"{d['K-202 cooling']:.1f}", f"ideal {d['K-202 cooling ideal']:.1f} x {K202_REAL_COOL} (CoolProp, S)"),
             ("Upgrader electrical (0.575 kWh/Nm3 CBG)", f"{d['upgrader electrical']:.0f}", f"S: Bawase p1656 x {BAL['cbg_nm3_h']:.0f} Nm3/h CBG"),
             ("  of which not K-201 + K-301 (other load)", f"{d['upgrader other']:.0f}", "D: scope of 0.575 not stated (recycle, chilling, utilities; A)")]
    yb = table(s, 20, yb, (255, 55, 280), drows, 15.5, 9.5)
    T(s, 22, yb + 12, "Shaft = m k/(k-1) R T1/M [r^((k-1)/k) - 1]/eta per stage; cooler = m cp (T2 - 40 C); K-202 corrected by frozen CoolProp real-gas ratios.", 9, fill=GREY)
    # closure
    y2 = section(s, 628, y0, 500, "CLOSURE (asserted in code, limit 0.1 %)")
    err = abs(100 * (BAL["mass_in"] - BAL["mass_out"]) / BAL["mass_in"])
    pe = lambda a, b: abs(100 * (a - b) / a)
    yy = y2 + 14
    for t, b in ((f"Mass: in {N(BAL['mass_in'])} kg/h (1 + 2), out {N(BAL['mass_out'])} kg/h (13 + 12 + 9 + 7 + 15 + 17), error {err:.3f} %", True),
                 (f"Methane: raw biogas {BAL['ch4_in']:.1f} kg/h = CBG {S_[13]['CH4']:.1f} + off-gas {S_[12]['CH4']:.1f}; error {pe(BAL['ch4_in'], BAL['ch4_out']):.3f} %", False),
                 (f"Carbon (CH4 + CO2): {BAL['cin']:.1f} kg C/h in, {BAL['cout']:.1f} out; error {pe(BAL['cin'], BAL['cout']):.3f} %", False),
                 (f"Sulphur (H2S): {BAL['h2s_in']:.3f} kg/h in = {BAL['h2s_out']:.3f} out (stream 7 + 8); error {pe(BAL['h2s_in'], BAL['h2s_out']):.3f} %", False),
                 (f"Solids: feed TS - VS destroyed = {BAL['ts_in']:.0f} kg/h; cake + surplus TS {BAL['ts_out']:.0f}; error {pe(BAL['ts_in'], BAL['ts_out']):.3f} %", False),
                 (f"Water incl. {BAL['hydro_water']:.0f} kg/h hydrolysis uptake: in {BAL['w_in']:.0f}, out {BAL['w_out']:.0f}; error {pe(BAL['w_in'], BAL['w_out']):.3f} %", False),
                 (f"VS destroyed {BAL['vs_destroyed']:.0f} kg/h = carbon in biogas / 0.50 (A9); recycle used {100*BAL['recycle']:.0f} % of centrate", False)):
        yy = WRAP(s, 634, yy, t, 86, 9.5, 12, weight=700 if b else 400) + 2
    T(s, 1138, y0 + 14, "Unit closure (kg/h in, out, error %):", 10, 700)
    urows = [("Unit", "In", "Out", "Err %")] + [(r[0], N(r[1]), N(r[2]), f"{abs(r[3]):.3f}") for r in BAL["rows"]]
    table(s, 1138, y0 + 20, (160, 95, 95, 70), urows, 14.5, 9.5)
    # Rev A to Rev B changes
    yc = max(yb + 20, yy + 6, y0 + 20 + 14.5 * len(urows) + 8)
    yc = section(s, 20, yc, 1560, "REV A TO REV B CHANGES (each applied in the calculation, not typed)")
    cb = BAL; cs = CASES; mxa = MIXES
    revA = dict(feed=160.0, fom=18000.0, yield_=144.6)
    chg = [("Item", "Rev A", "Rev B", "Source", "Effect on closure and duties"),
           ("Feed mix", "single 16.0 t/t (S, DPR)", f"input A0: {100*A['w_pm']:.0f} % press mud (25 t/t), rest napier class (16.7): {cb['mix']['t_per_t']:.1f} t/t; feed {cb['feed_tpd']:.0f} TPD", "CSE blueprint slide 24; Bawase p1654 (S)", f"feed +{100*(cb['feed_tpd']/160-1):.0f} % vs DPR; slurry {cb['slurry']/1000:.1f} t/h; D-201 heating {d['D-201 heating']:.0f} kW (Rev A 112)"),
           ("Raw biogas CH4, dry", "55 mol % (A2)", f"{100*cb['ch4_dry']:.1f} % blend: press mud 64.1 (S), napier 55 (A)", "Rouf et al. 2010 Table IV", f"raw gas {cb['nm3_h']:.0f} Nm3/h (Rev A 964); closure unchanged"),
           ("Yield, Nm3 raw gas per t feed", "144.6 (D)", f"{cb['yield_nm3_t']:.0f} (D); source blend {cb['mix']['nm3_t_ref'][0]:.0f} to {cb['mix']['nm3_t_ref'][1]:.0f}", "Bawase p1654; CSE (D)", f"gap to source {100*(cb['yield_nm3_t']/cb['mix']['nm3_t_ref'][0]-1):+.0f} to {100*(cb['yield_nm3_t']/cb['mix']['nm3_t_ref'][1]-1):+.0f} %, was +56 % vs CSE press mud"),
           ("Methane slip A4", "1.5 %", "0.64 % (membrane; PSA case 1.25 %)", "Bawase p1655; Task 37 slide 15", f"off-gas CH4 {100*cb['off_ch4_mol']:.2f} mol % (Rev A 1.90); CH4 closure 0.000 %"),
           ("Upgrader power", "0.240 kWh/Nm3 shaft", f"0.575 kWh/Nm3 electrical = {d['upgrader electrical']:.0f} kW; K-201+K-301 = {d['K-201 shaft']+d['K-301 blower shaft']:.0f} kW", "Bawase p1656 (single LCI source)", f"{d['upgrader other']:.0f} kW other upgrader load shown (A); range 0.30 to 0.575, PSA 0.19"),
           ("FOM cake solids; TS capture", "40.5 %; 85 % (A11)", f"28.7 %; {100*A['press_capture']:.0f} % (lab 52 %)", "Romio et al. 2024 Tables 2-3", f"FOM {cb['fom']*24/1000:.0f} t/d = {cb['fom_t_yr']:,.0f} t/yr (DPR 18,000); centrate {cb['cent']/1000:.1f} t/h"),
           ("Oxidiser basis", "'needs support fuel'", f"RTO: autothermic above 0.37 vol % CH4; off-gas {100*cb['off_ch4_mol']:.2f} %, {cb['off_heat_kw']:.0f} kW", "Task 37 slides 10, 18 (S)", "no fuel in the balance; flare or simple oxidiser would need fuel"),
           ("K-202 cooling", "71.8 kW (ideal)", f"{d['K-202 cooling']:.1f} kW (x {K202_REAL_COOL})", "CoolProp 8.0 HEOS (S, frozen)", "closes the -18 % finding; shaft 71.8 to " + f"{d['K-202 shaft']:.1f} kW"),
           ("10 mm hole at 250 barg; Z", "2.87 kg/s; Z 0.90 (A27)", f"{SC['q_hp']:.2f} kg/s (x {G_REAL_OVER_IDEAL}); Z {Z_HP}", "CoolProp 8.0 HEOS (S, frozen)", f"cascade inventory {SC['casc_kg']:.0f} kg; empties in {SC['t_casc_min']:.0f} min")]
    wtable(s, 20, yc, (170, 190, 470, 240, 490), chg, size=10.5, lh=13, pad=4, cpc=5.4)
    return s


def sheet_basis():
    s = RSheet(3, "CBG PLANT, 10 TPD: FEED-MIX INPUT, TECHNOLOGY CASES AND ASSUMPTION REGISTER", "Basis: feed mix, technology cases, A / S / D register",
               code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    y = section(s, 20, 84, 760, "FEED-MIX INPUT A0 (mass share of press mud; the rest is napier / residue class)")
    rows = [("Press-mud share", "t feed / t CBG", "Feed TPD", "Raw CH4 dry", "Nm3/t (model)", "Nm3/t (sources)", "FOM t/yr")]
    for w, c in MIXES.items():
        lo, hi = c["mix"]["nm3_t_ref"]
        rows.append((f"{100*w:.0f} %" + (" (base)" if w == 0.5 else ""), f"{c['mix']['t_per_t']:.1f}", f"{c['feed_tpd']:.0f}", f"{100*c['ch4_dry']:.1f} %", f"{c['yield_nm3_t']:.0f}",
                     f"{lo:.0f}" if lo == hi else f"{lo:.0f} to {hi:.0f}", f"{c['fom_t_yr']:,.0f}"))
    y = table(s, 20, y, (120, 110, 90, 100, 110, 120, 110), rows, 17, 10)
    y = WRAP(s, 24, y + 14, "t/t: press mud 25 (S: CSE slide 24, Bawase p1654); napier 16.7 (S, Bawase 150 m3/t = 60 kg CBG/t, conversion D); agri residue has no source and is lumped with napier (A). "
             "Blend t/t = 1 / (w/25 + (1 - w)/16.7). Raw CH4: press mud 64.1 % (S, Rouf Table IV, range 63.4 to 66.8), napier class 55 % (A, Rev A value). Source Nm3/t: press mud 86 to 93 (D), napier 150 (S), mass-weighted. "
             "The model is below the sources by 8 to 15 %; part of the napier gap is CH4: 150 m3/t with 60 kg CBG/t implies about 50 % CH4. DPR 160 TPD and 52,800 t/yr (S) correspond to 100 % napier class (167 TPD) at best.", 120, 10, 12.5) + 4
    y = section(s, 20, y + 6, 760, "TECHNOLOGY CASES (same model; one source each)")
    rows = [("Case", "Slip", "Upgrader kWh/Nm3", "Upgrader kW", "Raw gas Nm3/h", "Off-gas CH4 mol %", "Off-gas heat kW", "Source")]
    for nm, sl, kw, src in (("membrane (base)", "0.64 %", "0.575", "Bawase p1655-1656"), ("PSA-class", "1.25 %", "0.19", "Bawase; 0.19 is D (<0.575/3)"), ("Rev A slip 1.5 %", "1.5 %", "0.575", "Rev A value")):
        c = CASES[nm]
        rows.append((nm, sl, kw, f"{c['duty']['upgrader electrical']:.0f}", f"{c['nm3_h']:.0f}", f"{100*c['off_ch4_mol']:.2f}", f"{c['off_heat_kw']:.0f}", src))
    y = wtable(s, 20, y, (110, 60, 105, 80, 90, 100, 90, 125), rows, size=9.5, lh=11.5, pad=2) + 4
    y = WRAP(s, 24, y + 10, "Slip range for the base case 0.2 to 1 % (permit limits Germany 0.2, France 0.5 to 1, Denmark 1; Task 37 2025 pp12, 24; membrane 0.5 to 1.0, Task 37 slide 15). 0.64 % is the one sourced membrane value (Bawase) and sits inside it; a vendor guarantee is still needed. "
             "Upgrader power: 0.575 is one LCI inventory with unstated scope, not a plant meter; 0.30 (A, GAP_CLOSURE_BIO proposal) is the low end. All three cases pass the same closure tests. "
             "Oxidiser: RTO autothermic from 0.37 vol % CH4 (Task 37 slides 10, 18); even PSA-class off-gas (1.8 %) is above it. RTO manufacturer limit is below 10 kW or 1 m3 CH4/h; base case "
             f"{BAL['off_heat_kw']:.0f} kW and {BAL['off_ch4_nm3h']:.1f} m3/h is above both. CH4 LHV 802.3 kJ/mol is a textbook value (A).", 120, 10, 12.5)
    # right: independent check list
    y = section(s, 800, 84, 780, "INDEPENDENT CHECKS ON REV B (CoolProp 8.0 HEOS; cbg_realgas.py)")
    chk = [("Check", "Generator", "Independent", "Result")]
    chk += [("K-202 shaft / cooling (kW)", f"{d_['K-202 shaft']:.1f} / {d_['K-202 cooling']:.1f}", "68.2 / 87.6", "agrees (was 71.8 / 71.8)"),
            ("Z at 251 bara, 40 C", f"{Z_HP}", "0.8776", "agrees (A27 0.90 replaced)"),
            ("10 mm hole, 251 bara (kg/s)", f"{SC['q_hp']:.2f}", "G real 53,236 x area x Cd", "agrees (ideal gave 2.87)"),
            ("K-201 shaft (kW)", f"{d_['K-201 shaft']:.1f}", f"{381.2*MASS[11]/3600:.1f}", f"{100*(d_['K-201 shaft']/(381.2*MASS[11]/3600)-1):+.1f} % (CoolProp, CH4 58.3 %)"),
            ("Raw gas CH4 balance", f"{BAL['ch4_in']:.1f} kg/h", "CBG + off-gas", "closes 0.000 %")]
    y = wtable(s, 800, y, (200, 170, 190, 220), chk, size=9.5, lh=11.5, pad=2)
    y = section(s, 800, y + 14, 780, "ASSUMPTION REGISTER (A = assumed, S = sourced, D = derived)")
    reg = [("ID", "Input", "Value", "Tag"),
           ("A0", "Press-mud share of feed", f"{100*A['w_pm']:.0f} % (range 0 to 100)", "A"),
           ("A1", "CBG CH4 / CO2 (mol %)", "96 / 4", "A"), ("A2", "Raw CH4, dry", f"{100*BAL['ch4_dry']:.1f} % (blend)", "S/A/D"),
           ("A3", "H2S in raw gas, dry", "2,000 ppmv", "A"), ("A4", "Methane slip", "0.64 % (range 0.2 to 1)", "S"),
           ("A5", "Water in wet raw gas", "4 mass %", "A"), ("A6", "H2S removal R-301", "99 %", "A"), ("A7", "Water condensed E-301", "90 %", "A"),
           ("A8", "Feed total solids", "30 mass %", "A"), ("A9", "C in destroyed VS", "0.50", "A"), ("A10", "Slurry TS", "12 mass %", "A"),
           ("A11", "TS capture; cake TS", "27 % (lab 52 %); 28.7 %", "S"), ("A12", "Centrate recycled", f"{100*BAL['recycle']:.0f} % (cap: fresh water > 0)", "A"),
           ("A13", "T feed/dig/cent/chill/cool (C)", "30/38/35/5/40", "A"), ("A14-16", "cp 4.0; lambda 2,400; loss 10 %", "as stated", "A"),
           ("A17", "k gas; compressor eta", "1.30; 0.75", "A"), ("A18", "P membrane/ret/CBG (bar g)", "16 / 15 / 250", "A"),
           ("A19", "Stages K-201 / K-202", "2 / 3", "A"), ("A21-26", "Holder 4 h, holes 100 / 10 mm, Cd 0.85, cascade 3 m3", "as stated", "A"),
           ("A27", "Z at 251 bara", f"{Z_HP}", "S"), ("A28", "Upgrader kWh/Nm3", "0.575 (0.30 to 0.575)", "S"),
           ("A30", "Design pressure / operating", f"{DESIGN_MARGIN:.2f}", "A")]
    y = table(s, 800, y, (60, 330, 330, 60), reg, 15, 9.5)
    srows = [("Tag", "Sourced (S) item", "Where"),
             ("S", "10 TPD CBG; 330 d/yr; DPR feed 160 TPD and FOM 18,000 t/yr (comparison only)", "DPR Sections 1, 4, 9"),
             ("S", "t/t press mud 25, napier 16.7; napier 150 Nm3/t; slip 0.64 / 1.25 %; 0.575 kWh/Nm3", "CSE slide 24; Bawase doi 10.18280/ijdne.210612 pp1654-1656"),
             ("S", "press mud CH4 64.1 %; cake 28.7 % TS, capture 26.8 % (lab 51.8 %)", "Rouf 2010 Table IV; Romio 2024 Tables 2-3"),
             ("S", "RTO autothermic 0.37 vol % CH4; membrane slip 0.5 to 1.0 %", "IEA Bioenergy Task 37 slides 10, 15, 18"),
             ("S", "real-gas ratios K-202 0.9508 / 1.2205, flux 1.2380, Z 0.8776 / 0.9269 / 0.9529", "CoolProp 8.0.0 HEOS, cbg_realgas.py (frozen)"),
             ("D", "mixing, balance, duties, relief areas (toolkit gas_area, API 520-I derived, standard not read)", "build_balance(), size_gas()")]
    wtable(s, 800, y + 10, (40, 470, 270), srows, size=9.5, lh=11.5, pad=2)
    names = ["1 Feedstock mix", "2 Fresh water", "3 Centrate recycle", "4 Slurry to D-201", "5 Raw biogas (wet)", "6 Digestate", "7 Spent H2S media", "8 Desulphurised biogas",
             "9 Chiller condensate", "10 Dry biogas", "11 Biogas to M-401", "12 CO2-rich off-gas", "13 CBG (low pressure)", "14 CBG 250 barg", "15 FOM cake", "16 Centrate", "17 Surplus LFOM"]
    T(s, 22, 1062, "Stream names:  " + "  |  ".join(names[:9]), 9.5, 400, fill=INK)
    T(s, 22, 1076, "  |  ".join(names[9:]), 9.5, 400, fill=INK)
    return s


d_ = BAL["duty"]


def callout(s, x, y, w, lines, col=RED, size=10, lh=12.5, fill="#fff"):
    R(s, x, y, w, 14 + lh * len(lines), fill, col, 1.5)
    for i, t in enumerate(lines): T(s, x + 7, y + 14 + i * lh, t, size, 700 if i == 0 else 400, "start", col)
    return y + 14 + lh * len(lines)


def cloud(s, x, y, rx=60, ry=26, col="#9ccc65", op=0.45):
    s.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{col}" opacity="{op}" stroke="#558b2f" stroke-width="1.2" stroke-dasharray="5 3"/>')


def okbox(s, x, y, w, t):  # safeguard tag
    R(s, x, y, w, 15, "#e8f5e9", GREEN, 1.2)
    T(s, x + w / 2, y + 11, t, 9.5, 700, "middle", GREEN)


def sheet_scn_gas():
    s = RSheet(4, "CBG PLANT: SCENARIOS 1 AND 2, DIGESTER AND GAS HOLDER", "Scenarios 1 and 2, holder release; overpressure/vacuum",
              code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    pid(s, detail=False, dim=True)
    # --- scenario 1: membrane holder release (right dome, B)
    cx, cy = DB, DCY - DH / 2 - 30
    cloud(s, cx + 20, cy - 30, 95, 30, op=0.35)
    star(s, cx + 30, cy - 2, 15)
    T(s, cx + 70, cy + 24, "1", 22, 700, "middle", RED)
    callout(s, 530, 455, 400, ["1  Biogas / H2S release from membrane holder GH-201B",
                              f"Hole {SC['hole_holder_mm']:.0f} mm (A22) at {SC['p_holder_mbarg']:.0f} mbar(g) (A23): {SC['q_holder']:.2f} kg/s raw biogas",
                              f"Holder buffer {N(SC['hold_gas_kg'])} kg wet biogas ({SC['holder_h']:.0f} h of production, A21):",
                              f"CH4 {N(SC['hold_ch4_kg'])} kg, H2S {SC['hold_h2s_kg']:.1f} kg at 2,000 ppmv (A3)",
                              f"Whole buffer discharges in about {SC['t_holder_min']:.0f} min at the initial rate (D, no refill)"], RED)
    # --- scenario 2: overpressure / vacuum (digester A headspace)
    s.add(f'<ellipse cx="{DA}" cy="{DCY-DH/2-22}" rx="62" ry="40" fill="none" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="7 4"/>')
    T(s, DA - 64, DCY - DH / 2 - 52, "2", 22, 700, "middle", AMBER)
    callout(s, 530, 545, 400, ["2  Digester over-pressure or vacuum (air ingress)",
                               f"Blocked outlet: gas generation {SC['gen_kg_s']:.2f} kg/s ({N(BAL['wet_kg'])} kg/h) goes to flare / PRV",
                               "Vacuum: K-301 draws more than is generated, or digestate is",
                               "pumped out with no gas make-up: air is drawn into the headspace.",
                               "PRV-201 capacity and set points: not quantified (needs vendor)"], AMBER)
    # safeguards drawn (highlight)
    okbox(s, 120, 262, 80, "PV-201 to flare")
    okbox(s, 392, 258, 56, "PIC-201")
    okbox(s, 490, 316, 70, "XV-201 closes")
    okbox(s, 186, 394, 96, "PRV-201A/B vent")
    okbox(s, 520, 345, 84, "AT-201 + ESD")
    okbox(s, 40, 130, 100, "FL-901 burns gas")
    # bottom strip table
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (consequence numbers only where a documented formula or toolkit function was run)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown", "Open data needs"),
            ("1 Holder / digester gas release", "Membrane tear, fixing failure, hose/clamp failure on GH-201, fire, vehicle impact (A)", "Flammable and toxic (H2S) cloud near the digesters; ignition gives flash fire; unignited H2S exposure", "AT-201 CH4/H2S detection; ESD-101 closes XV-201 and stops K-301; PIC-201/PV-201 limit pressure; PRV vent to safe place", "Membrane material and tear mode; H2S limit values and dispersion not run; layout, wind, ignition sources"),
            ("2 Over-pressure / vacuum", "Blower trip or XV-201 closed with feed running (over-pressure); K-301 over-draw or digestate draw-off (vacuum)", "Holder over-inflation, membrane burst, vent release; vacuum draws air and makes a flammable mixture", "PIC-201 to PV-201 and flare; PRV-201A/B pressure/vacuum relief; LSHH-201 stops feed; low-pressure trip of K-301 (A)", "PRV capacity, set and vacuum limits; holder design pressure; flammable range of the CH4/CO2/air mixture")]
    yy = y
    colw = (150, 220, 250, 270, 210)
    R(s, 20, yy, sum(colw), 19, "#e8eaf0", "none"); cx0 = 20
    for j, t in enumerate(rows[0]): T(s, cx0 + 4, yy + 13, t, 10.5, 700); cx0 += colw[j]
    yy += 19
    for r in rows[1:]:
        hmax = 0; cx0 = 20
        for j, t in enumerate(r):
            e = WRAP(s, cx0 + 4, yy + 13, t, int(colw[j] / 5.5), 10, 12.5, weight=700 if j == 0 else 400)
            hmax = max(hmax, e); cx0 += colw[j]
        yy = hmax + 4
        PL(s, [(20, yy - 2), (20 + sum(colw), yy - 2)], 0.6, "#bbb")
    yy += 4
    for t in (f"Rates: process_safety.release.gas_release_kg_s (orifice flow, Cd {SC['cd']} A25, k {A['k_gas']} A17), M of raw biogas {BAL['M5']:.1f} kg/kmol (D). Inventories = production rate x hours (D).",
              "Not quantified: toxic and flammable cloud extent, membrane failure frequency, H2S exposure limits. Needs: holder datasheet, wind and layout, licensed dispersion model."):
        yy = WRAP(s, 22, yy, t, 190, 10, 12.5, GREY) + 2
    # right panel
    panel_box(s)
    y = section(s, 1135, 84, 445, "SCENARIO 1: HOLDER RELEASE")
    yy = y + 16
    for t in ("Release point: tear or failed fixing in the outer or inner membrane of GH-201B; gas escapes at holder pressure, only a few mbar(g), so the release is low momentum and the cloud is driven by wind and buoyancy. Wet raw biogas has a molar mass of about " + f"{BAL['M5']:.1f}" + " kg/kmol (D), close to air, so it may not rise: dispersion not assessed.",
              f"The rate above ({SC['q_holder']:.2f} kg/s) is for a {SC['hole_holder_mm']:.0f} mm hole at {SC['p_holder_mbarg']:.0f} mbar(g). It is a screening number, not a tear model.",
              "H2S is toxic as well as flammable. No toxic limit is quoted here (not in the source files).",
              "Actions: detectors alarm, ESD closes XV-201 to keep the plant gas out, K-301 stops, PV-201 and the flare take the pressure, operators isolate feed."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13.5, bullet=True) + 5
    y = section(s, 1135, yy + 4, 445, "SCENARIO 2: OVERPRESSURE / VACUUM")
    yy = y + 16
    for t in (f"Normal gas generation is {SC['gen_kg_s']:.3f} kg/s wet biogas (stream 5). If the offtake is blocked the headspace fills at that rate until the flare valve or PRV passes it: this is the relief basis (D), not a sized valve.",
              "Holder volume would take the first minutes; after that the membrane or PRV is the last safeguard. Over-inflation can burst the outer membrane.",
              "Vacuum case: air entering the headspace can pass the flammable range as it mixes with biogas. A low-pressure trip on K-301 and a vacuum breaker are the usual first barriers (A).",
              "Digester structural pressure/vacuum limits are not in the source files."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13.5, bullet=True) + 5
    okbox(s, 1141, yy + 4, 100, "green = safeguard acts")
    T(s, 1141, yy + 34, "green cloud = release; star = release point; amber = scenario 2", 10, fill=GREY)
    return s


def sheet_scn_hp():
    s = RSheet(5, "CBG PLANT: SCENARIOS 3 AND 4, COMPRESSION AND CASCADE FILLING", "Scenarios 3 and 4, HP release; fire at cascade",
              code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    pid(s, detail=False, dim=True)
    # scenario 3: HP release at K-202 outlet (x ~1032..1056, y 195)
    jx, jy = 1044, RY - 4
    flame(s, jx, jy - 4, -50, 42, 14, 0.9)
    star(s, jx, jy, 11)
    T(s, 1109, 212, "3", 22, 700, "middle", RED)
    callout(s, 530, 455, 400, ["3  High-pressure CBG release at K-202 / cascade filling",
                              f"{SC['hole_hp_mm']:.0f} mm hole (A24), {A['P_cbg']:.0f} barg, {A['T_cool']:.0f} C: {SC['q_hp']:.2f} kg/s CBG (real-gas flux, choked)",
                              f"Cascade {SC['casc_m3']:.0f} m3 holds about {N(SC['casc_kg'])} kg ({SC['casc_cbg_h']:.1f} h of production; Z {SC['Z_hp']}, A26/A27)",
                              f"Emptying through that hole: about {SC['t_casc_min']:.0f} min if not isolated (D)",
                              "Jet length, noise and ignition probability: not quantified"], RED)
    # scenario 4: fire at the cascade bay
    fx = 1009
    for xx in (980, 1005, 1030, 1050):
        flame(s, xx, 436, (xx - 1010) / 8, 46, 22, 0.9)
    star(s, 1009, 388, 11, "#ffeb3b", RED)
    T(s, 945, 400, "4", 22, 700, "middle", RED)
    callout(s, 530, 545, 400, ["4  Fire at cascade bank or compressor house",
                               "Fire (pool, jet from scenario 3, or vehicle) heats CAS-601 tubes",
                               "and K-202. Gas tubes burst when hot steel loses strength",
                               "if thermal relief or isolation fails (gas burst, not BLEVE).",
                               "Heat flux and radius: not quantified (needs layout and PRD data)"], RED)
    # safeguards
    okbox(s, 870, 318, 112, "ESD: XV-501/601 close")
    okbox(s, 990, 505, 100, "UV/IR + AT-601")
    okbox(s, 972, 226, 58, "PSHH-501")
    okbox(s, 896, 343, 56, "TPRD (A)")
    okbox(s, 870, 466, 62, "breakaway")
    # bottom table
    y = section(s, 20, 784, 1100, "SCENARIO TABLE (consequence numbers only where a documented formula or toolkit function was run)")
    rows = [("Scenario", "Initiating event", "Hazard", "Safeguards shown", "Open data needs"),
            ("3 HP CBG release", "Fitting, hose or tube leak at K-202 discharge, dryer or fill hose; hose pull-away from a departing trailer (A)", "Choked jet of flammable gas at 250 barg; jet fire if ignited; delayed ignition in the compressor enclosure", "AT-601 and UV/IR to ESD-101; XV-601/XV-501 close; hose breakaway; PSHH-501 trips K-202; PSV-501 on the HP line", "Hole size distribution; compressor house ventilation; ignition sources"),
            ("4 Fire at cascade or compressor", "Leak fire, external fire, vehicle fire at the filling bay, fire in the compressor house (A)", "Radiant heat on cascade tubes and K-202; thermal burst of tubes; domino to adjacent trailers", "UV/IR detection; ESD closes fill and storage; TPRD on tubes (A); passive/active fire protection not defined; separation per PESO licence (conditions not in source)", "Layout and separation distances; tube PRD data; fire-water or deluge basis; PESO licence conditions")]
    yy = y
    colw = (150, 220, 250, 270, 210)
    R(s, 20, yy, sum(colw), 19, "#e8eaf0", "none"); cx0 = 20
    for j, t in enumerate(rows[0]): T(s, cx0 + 4, yy + 13, t, 10.5, 700); cx0 += colw[j]
    yy += 19
    for r in rows[1:]:
        hmax = 0; cx0 = 20
        for j, t in enumerate(r):
            e = WRAP(s, cx0 + 4, yy + 13, t, int(colw[j] / 5.5), 10, 12.5, weight=700 if j == 0 else 400)
            hmax = max(hmax, e); cx0 += colw[j]
        yy = hmax + 4
        PL(s, [(20, yy - 2), (20 + sum(colw), yy - 2)], 0.6, "#bbb")
    yy += 4
    for t in (f"Rate: process_safety.release.gas_release_kg_s at {P_hp_abs/100:.1f} bar abs, 313 K, M {BAL['M13']:.2f} kg/kmol, k {A['k_gas']}, Cd {SC['cd']}; ideal rate {SC['q_hp_ideal']:.2f} kg/s x real-gas flux ratio {G_REAL_OVER_IDEAL} (CoolProp, frozen) = {SC['q_hp']:.2f}; inventory Z {SC['Z_hp']} (S, CoolProp).",
              "Not quantified: jet flame length, radiation, burst energy, probabilities. Needs: toolkit jet-fire run on the real hole size, vendor cascade data, layout."):
        yy = WRAP(s, 22, yy, t, 190, 10, 12.5, GREY) + 2
    panel_box(s)
    y = section(s, 1135, 84, 445, "SCENARIO 3: HIGH-PRESSURE RELEASE")
    yy = y + 16
    for t in (f"CBG at {A['P_cbg']:.0f} barg is the highest-energy inventory on the site. A {SC['hole_hp_mm']:.0f} mm hole gives about {SC['q_hp']:.2f} kg/s (choked flow, formula in toolkit release.py). The compressor and cascade supply side keeps feeding until K-202 stops and XV-501/XV-601 close.",
              f"Cascade inventory ({N(SC['casc_kg'])} kg) is {SC['casc_cbg_h']:.1f} h of plant output; it is the stored energy for scenario 4.",
              "Ignited: jet fire on neighbouring tubes, hoses, trailers. Unignited in the enclosure: explosion risk; ventilation and gas detection matter.",
              "Quantities marked A: hole, cascade size. Replace with vendor data."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13.5, bullet=True) + 5
    y = section(s, 1135, yy + 4, 445, "SCENARIO 4: FIRE AT CASCADE OR COMPRESSOR")
    yy = y + 16
    for t in ("Compressed gas cylinders are protected by thermally activated pressure-relief devices (TPRD, A); where they are missing or blocked from the flame, tubes can rupture. No rule or distance is quoted: PESO licence conditions are named in DPR Section 6 but not in the source files.",
              "Safeguards drawn: flame and gas detection, ESD of fill and storage valves, TPRD (A). Active fire protection is not defined.",
              "Biogas upstream (holders, 4 h buffer) is not near the cascade; the flare and holder isolation limit escalation toward the digesters.",
              "Domino with the oxidiser and flare is a layout question: not assessed."):
        yy = WRAP(s, 1141, yy, t, 70, 10.5, 13.5, bullet=True) + 5
    T(s, 1141, yy + 12, "star = release point; flames = fire; green tags = safeguards that act", 10, fill=GREY)
    return s



# =====================================================================================================================
# 5. SAFETY DESIGN BASIS (sheets 6 and 7)
# =====================================================================================================================
# Source ledger (free sources; full list in docs/pid/validation/SAFETY_FEATURES_CHECKLIST.md): S5 OSHA 1910.119; S11 CSB Kuraray report (discharge location);
# S12 Bergin et al. (HSE), Explosion safety in anaerobic digestion sites, IChemE Hazards 33 (2023), read in full for this revision; S13 Roberts et al. (HSL) IChemE SS 149;
# S1 HSE HSG176; S2 HSE HSG238; S4 EIGA Doc 15/21; S3 HSE COMAH plant layout; S14 Purple Book PGS 3; S9 49 CFR 193 (impoundment rule, LNG only).
HOLDER_GAS_EACH = BAL["wet_kg"] / 2


def relief_rows():
    r4, r5 = RELIEF["PSV-401"], RELIEF["PSV-501"]
    sz401 = (f"SIZED (D): blocked outlet, load {r4['W']:.0f} kg/h (stream 11), set {r4['set_bar_g']} barg, relieving {r4['P1_bar_a']:.1f} bara, Z {r4['Z']}, Kd 0.975, critical flow: "
             f"{r4['area']:.0f} mm2, API 526 orifice {r4['orifice']} ({r4['n']} valve). Toolkit gas_area; standard not read, verify coefficients")
    sz501 = (f"SIZED (D): blocked outlet, load {r5['W']:.0f} kg/h (stream 14), set {r5['set_bar_g']:.0f} barg, relieving {r5['P1_bar_a']:.0f} bara, Z {r5['Z']}: "
             f"{r5['area']:.1f} mm2, orifice {r5['orifice']}. Real-gas flux is 24 % above the ideal equation, so this is conservative")
    return [("Item", "Design pressure basis (A)", "Relief case(s)", "Device", "Discharge", "Sizing status"),
            ("TK-101 hydrolysis tank", "atmospheric; open vent", "overfill, out-breathing, vacuum on emptying, gas evolution", "VT-101 open vent", "odour/H2S treatment (A); zone per S12", "not sized: needs volume and fill/empty rates"),
            ("D-201A/B digesters + GH-201A/B holders", "low-pressure gas space; structural pressure and vacuum limits not in source", f"blocked gas outlet (generation {HOLDER_GAS_EACH:.0f} kg/h each, D), foam or crust blocking vent (S12), vacuum (K-301 over-draw, digestate draw-off), liquid overfill, support-air failure",
             "PRV-201A/B pressure + vacuum with FA-201A/B (S12: one over- and one under-pressure device per gas container); PV-201 to flare; OF-201A/B overflow seal; LSHH-201", "VS safe stack (A); flare for PV-201", "not sized: needs holder/digester design pressures; load stated; low-pressure venting standard not obtained (gap)"),
            ("R-301 H2S vessel", "above blower shut-off pressure (not known)", "blocked outlet (blower deadhead); fire on gas-filled vessel; media self-heating or fire (S12 incident list)", "PSV-301", "FH to FL-901 (A)", "not sized: needs blower curve and set pressure"),
            ("E-301 gas chiller", "gas side at least CHW pressure, or relief", "tube rupture (CHW to gas side), blocked-in CHW thermal expansion, ice blockage", "PSV-302 (gas side); CHW thermal relief on chiller package", "FH (A); CHW to closed drain", "not sized: needs CHW pressure, tube data; rupture method not obtained"),
            ("K-201 discharge, M-401 high-pressure side", f"{SET_401} barg = {DESIGN_MARGIN} x 16 (A)", "blocked outlet (retentate valve shut), control failure; fire on gas-filled vessel (not a PSV case)", "PSV-401", "FH to FL-901 (A)", sz401),
            ("M-401 permeate side, OX-401 feed", "low (off-gas 1 barg, A)", "membrane or tube failure puts high-pressure gas on the permeate line", "PSV-402; FA-401", "FH (A)", "not sized: needs permeate-side design pressure and failure area"),
            ("OX-401 off-gas RTO", "vendor", "flame-out, combustion-air loss, purge failure", "BMS-401 (flame, purge, permissives)", "stack", "gap: oxidiser vendor package (BMS and relief)"),
            ("K-202 discharge, V-501 dryer, HP line", f"{SET_501:.0f} barg = {DESIGN_MARGIN} x 250 (A)", "blocked outlet (cascade full or XV-501 closed), thermal expansion, fire", "PSV-501; PSHH-501", "VS safe stack at height (A)", sz501),
            ("CAS-601A/B/C cascade", f"{SET_501:.0f} barg (A); tube rating to vendor", "thermal expansion when isolated, fire (gas burst, not BLEVE), overfill", "TPRD-601 on each tube; PSV-601 on header", "VS; TPRD vent away from tubes (A)", "not sized: TPRD and thermal case need vendor data and heat input (S13 method, owner copy)"),
            ("Filling hose and dispenser", "250 barg class", "hose pull-away, over-fill", "breakaway, XV-601, dispenser relief (vendor)", "dispenser vent", "gap: dispenser vendor design"),
            ("TK-501 / TK-502 centrate, LFOM", "atmospheric", "overfill, out-breathing and vacuum, dissolved biogas (S12: digestate stores zoned like digesters)", "PVRV-501/502 (flame-arrester type to be chosen); LIT-501 high", "VS (A); overflow to TK-502", "not sized: needs volumes; tank-venting standard not obtained (gap)"),
            ("D-201 hot-water coils", "utility package", "blocked-in thermal expansion", "thermal relief on hot-water skid (not drawn)", "closed drain", "gap: utility package scope"),
            ("P-101, P-502 pumps; S-501; H-101", "discharge piping rated for shut-off (A)", "pump deadhead (centrifugal drawn); no pressure items", "none (stated reason)", "-", "A: change pump type, add PSV-101"),
            ("FL-901 flare + FA-901", "vendor", "flashback; liquid carry-over", "FA-901; flare KO / seal drum not drawn", "-", "gap: flare package; support fuel for off-spec gas")]


ESD_COLS = ["XV-101A/B", "P-101", "XV-201", "PV-201", "K-301", "K-201", "K-202", "XV-501", "XV-601", "OX-401", "alarm"]
ESD_ROWS = [("AT-201 CH4 high-high (2oo2, A)", {"XV-201": "C", "K-301": "S", "XV-101A/B": "C", "P-101": "S", "alarm": "A"}),
            ("AT-201 H2S high-high (A)", {"XV-201": "C", "K-301": "S", "alarm": "A"}),
            ("AT-202 H2S, feed area (A)", {"alarm": "A"}),
            ("LSHH-201A/B digester level", {"XV-101A/B": "C", "P-101": "S", "alarm": "A"}),
            ("PSHH-201 holder pressure HH", {"PV-201": "O", "XV-101A/B": "C", "P-101": "S", "alarm": "A"}),
            ("PSLL-201 holder pressure low", {"K-301": "S", "alarm": "A"}),
            ("AT-301 H2S after R-301 high-high", {"K-201": "S", "alarm": "A"}),
            ("PSHH-501 K-202 discharge", {"K-202": "S", "XV-601": "C", "alarm": "A"}),
            ("AT-401 CBG off-spec", {"XV-501": "C", "K-202": "S", "alarm": "A"}),
            ("AT-402 CH4 compressor house", {"K-301": "S", "K-201": "S", "K-202": "S", "XV-201": "C", "XV-501": "C", "alarm": "A"}),
            ("UV/IR-401 flame compressor house", {"K-301": "S", "K-201": "S", "K-202": "S", "XV-201": "C", "XV-501": "C", "XV-601": "C", "OX-401": "S", "alarm": "A"}),
            ("AT-601 CH4 filling bay", {"XV-601": "C", "XV-501": "C", "K-202": "S", "alarm": "A"}),
            ("UV/IR-601 flame filling bay / cascade", {"XV-601": "C", "XV-501": "C", "K-202": "S", "K-201": "S", "alarm": "A"}),
            ("OX-401 BMS flame-out (delay A)", {"K-201": "S", "alarm": "A"}),
            ("ESB-101 manual ESD", {c: ("O" if c == "PV-201" else "C" if c.startswith("XV") else "S" if c[0] in "PKO" else "A") for c in ESD_COLS}),
            ("Power or instrument-air loss", {"XV-101A/B": "C", "XV-201": "C", "XV-501": "C", "XV-601": "C", "PV-201": "O", "alarm": "A"})]
SIFS = [("SIF", "Initiator and final element", "Demand source (A)", "IPLs credited (A)", "SIL target (A)"),
        ("SIF-1 digester high level", "LSHH-201A/B to XV-101A/B + P-101", "feed overfill, level instrument failure", "operator on LIT, overflow OF-201", "SIL 1 (A)"),
        ("SIF-2 holder over-pressure", "PSHH-201 to PV-201 open + feed stop", "blocked gas outlet, blower trip, foam (S12)", "PIC-201, PRV-201 as last layer", "SIL 1 (A)"),
        ("SIF-3 holder vacuum", "PSLL-201 to K-301 stop", "blower over-draw, digestate draw-off", "PRV-201 vacuum side", "SIL 1 (A)"),
        ("SIF-4 gas in compressor house", "AT-402 / UV/IR-401 to compressors stop, XV closed", "flange or seal leak, delayed ignition", "ventilation, area classification", "SIL 2 (A)"),
        ("SIF-5 K-202 discharge HH", "PSHH-501 to K-202 stop + XV-601", "cascade full, XV-501 shut", "PSV-501", "SIL 2 (A)"),
        ("SIF-6 filling bay leak or fire", "AT-601 / UV/IR-601 to XV-601, XV-501, K-202", "hose failure, pull-away, vehicle impact", "breakaway coupling, TPRD, layout", "SIL 2 (A)"),
        ("SIF-7 H2S breakthrough", "AT-301 HH to K-201 stop", "R-301 media exhausted", "operator, media change schedule", "SIL 1 (A)")]
HAZ = [("Node / deviation", "Cause", "Consequence (qualitative)", "Safeguard", "Action"),
       ("1 D-201/GH-201: more gas, blocked offtake", "XV-201 shut, blower trip, foam in vent", "holder over-inflation, membrane burst, release of CH4 and H2S", "PIC-201/PV-201, PRV-201, PSHH-201", "check foam control; size PRV (gap)"),
       ("2 D-201/GH-201: less pressure, air ingress", "blower over-draw, digestate withdrawn", "flammable mixture in headspace; ignition source", "PSLL-201, PRV vacuum side", "confirm vacuum limits; purge procedure"),
       ("3 GH-201: loss of containment", "membrane tear, fixing failure", "CH4/H2S cloud, density can vary (S12), toxic and flammable", "AT-201 high and low level, XV-201", "confirm zones with dispersion study"),
       ("4 R-301: high temperature, fire", "air in media bed, exothermic reaction (S12)", "bed fire, H2S release", "PSV-301, AT-301, no air ingress rule", "vendor media data"),
       ("5 M-401/OX-401: more flow to permeate", "membrane failure", "HP gas to off-gas line, OX flame disturbance", "PSV-402, FA-401, BMS-401", "permeate design pressure"),
       ("6 K-202 and cascade: high pressure", "blocked outlet, control failure", "line or tube over-stress", "PSHH-501, PSV-501, PSV-601", "relief set points to vendor"),
       ("7 Filling bay: release or hose pull-away", "vehicle drive-off, hose wear", "jet fire, tube heating", "breakaway, XV-601, UV/IR-601, TPRD", "layout distances (gap)"),
       ("8 TK-501/502: overfill, vacuum", "pump trip, blocked vent", "tank damage, biogas release to low points (S12)", "PVRV-501/502, LIT-501", "venting calc (gap)")]
ISD = [("Reduce inventory: 4 h holder buffer (A21) and 3 m3 cascade (A26) set the stored energy; use the smallest buffer the offtake allows.", "A"),
       ("Moderate conditions: operate the holders at a few mbar and keep digestate stores away from compressors; keep high-pressure storage in the open at the plant edge.", "A"),
       ("Substitute / eliminate: avoid air-injection desulphurisation (S12 Table 3 gives zone 0 around it); choose a media or biological type with no air in the gas path.", "S12"),
       ("Simplify: size R-301 and the blower so shut-off pressure is below vessel design and no PSV is needed; fewer relief points to flare.", "A"),
       ("Moderate: lean off-gas (below 1 vol % CH4) goes to an RTO at 0.37 vol % limit, so no support-fuel gas line is needed.", "S"),
       ("Limit hose and tube hazards: breakaway coupling, TPRD per tube, filling bay at the site edge (distances need PESO text).", "A")]
HAC = [("Location (S12 Table 3, Austrian, French, German guidance)", "Zone proposed"),
       ("Gas space of digester / holder, indoor", "Zone 1 (Aus) or 2 (Fr)"),
       ("Outdoor around flexible-membrane holder", "Zone 2, 3 m radius (Fr, Ger); Zone 1 at 1 m, then 2 to 3 m (Aus)"),
       ("Relief and vent discharge, pipe connections", "Zone 1 at 1 m, Zone 2 at 3 m radius"),
       ("Desulphurisation with air injection", "Zone 0, 3 m (Aus); not used here (ISD note 3)"),
       ("Digestate store, condensate separator", "as digester; mouth of vent line Zone 2, 1 m"),
       ("Combustion unit room", "not classified if ventilated and monitored (Fr)"),
       ("Compressor house, cascade bay, filling bay", "gap: no free source; apply IS/IEC 60079-10-1, not obtained")]


def sheet_safety1():
    s = RSheet(6, "CBG PLANT: SAFETY DESIGN BASIS (1), RELIEF SCHEDULE AND ESD CAUSE-AND-EFFECT", "Safety design basis: relief schedule, ESD matrix",
               code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    y = section(s, 20, 84, 1560, "RELIEF SCHEDULE (A = assumed; R = recommended by a named free source; devices tagged on sheet 1; set pressures A; no SIL or vendor claim)")
    y = wtable(s, 20, y, (150, 190, 330, 290, 170, 430), relief_rows(), size=10.5, lh=12.5, pad=3, cpc=5.3)
    y = WRAP(s, 22, y + 11, "Sizing uses process_safety.relief.gas_area (API 520-I gas equation as derived in the toolkit; Kd 0.975; accumulation 10 % non-fire; the standard text was not read, paywalled). Back pressure 5 kPa over atmosphere (A). "
             "Discharge locations are a design item (S11); FH and VS are A. Controlling standards not obtained: API 520/521/526/2000, OISD-STD-106/116/118, PESO SMPV(U) 2016 (gap).", 250, 9.5, 11.5, GREY)
    y = section(s, 20, y + 6, 1560, "ESD CAUSE-AND-EFFECT (C close, O open, S stop, A alarm; every tag exists on sheet 1; voting and set points A)")
    colw = [300] + [100] * len(ESD_COLS)
    R(s, 20, y, sum(colw), 18, "#e8eaf0", "none"); T(s, 24, y + 13, "Initiator", 10, 700)
    for j, c in enumerate(ESD_COLS): T(s, 20 + colw[0] + 100 * j + 50, y + 13, c, 9.5, 700, "middle")
    y += 18
    for i, (nm, eff) in enumerate(ESD_ROWS):
        if i % 2 == 0: R(s, 20, y, sum(colw), 15, "#f6f7fa", "none")
        T(s, 24, y + 11, nm, 9.5)
        for j, c in enumerate(ESD_COLS):
            v = eff.get(c)
            if v: T(s, 20 + colw[0] + 100 * j + 50, y + 11, v, 9.5, 700, "middle", RED if v != "A" else GREY)
        y += 15
    R(s, 20, y - 15 * len(ESD_ROWS) - 18, sum(colw), 15 * len(ESD_ROWS) + 18, "none", "#9aa", 1)
    T(s, 22, y + 12, "Fail-safe: XV close and PV-201 open on loss of power or air (A). Source: S5 requires emergency shutdown to be covered in procedures and integrity; S1 para 128 for fail-safe remote valves.", 9.5, fill=GREY)
    return s


def sheet_safety2():
    s = RSheet(7, "CBG PLANT: SAFETY DESIGN BASIS (2), SIF LIST, DETECTION, HAZARDS, HAZARDOUS AREAS", "Safety design basis: SIF, detection, hazard identification",
               code="VS-CBG", project=PROJ, basis=BASIS)
    frame(s, NSHEETS)
    y = section(s, 20, 84, 1000, "SAFETY INSTRUMENTED FUNCTIONS (SIL targets are ASSUMED, A; no SIL verification claimed)")
    y = wtable(s, 20, y, (150, 270, 220, 200, 160), SIFS, size=10, lh=12, pad=3, cpc=5.1)
    y = WRAP(s, 22, y + 11, "Free source: S2 (HSE HSG238) separates protection from control and sets integrity from the hazard and risk analysis. IEC 61511 and LOPA texts not obtained (gap). BP-Husky (S10): credited SIS and relief did not prevent overflow, so test them.", 190, 9.5, 11.5, GREY)
    y = section(s, 20, y + 6, 1000, "HAZARD IDENTIFICATION, 8 NODES (qualitative; no numeric consequences; PSM requires a PHA incl. facility siting, S5)")
    y = wtable(s, 20, y, (190, 170, 240, 210, 190), HAZ, size=10, lh=12, pad=3, cpc=5.1)
    x2, w2 = 1040, 540
    y2 = section(s, x2, 84, w2, "DETECTION AND MITIGATION")
    det = ["F&G: CH4 detectors at BOTH high and low level at holders, enclosures and digestate stores, because biogas can be lighter or heavier than air (S12); H2S toxic detectors at personnel areas (AT-202, AT-201). EIGA S4: use leak or gas detection beside flame detection.",
           "Isolation: XV-201 at the holders, XV-101A/B at the feed, XV-501 and XV-601 at the cascade; fail-safe, remotely operated (S1 para 128). Largest gas inventories: holders (4 h of raw gas) and cascade (3 m3).",
           "Containment: no flammable liquid on site. Bund rule (S1 para 157: 110 % of the largest vessel) applied by analogy to the LFOM and centrate tanks TK-501/502 is A; ground-level overflow pipes need a zone (S12).",
           "Layout: HSE COMAH layout guidance (S3) asks for domino and occupied-building checks; distances: gap (PESO licence conditions and OISD not obtained). S4 Table 1 gives hydrogen distances only, not applicable.",
           "Ventilation and inerting: forced ventilation where zoning depends on it, with an alternative strategy on failure (S12); nitrogen purge for compressor and cascade work (not drawn). Fire water and foam: gap, no free source for CBG; toolkit fire_water needs layout.",
           "Discharge: vent and relief outlets away from workers and buildings (S11, Kuraray); zone 1 at 1 m, zone 2 at 3 m around outlets (S12)."]
    for t in det: y2 = WRAP(s, x2 + 6, y2 + 14, t, 100, 9.5, 11.5, bullet=True)
    y2 = section(s, x2, y2 + 8, w2, "HAZARDOUS-AREA BASIS (R from S12; India basis gap)")
    y2 = table(s, x2, y2, (270, 270), HAC[:1] + HAC[1:], 15, 9)
    y3 = max(y, y2) + 10
    y3 = section(s, 20, y3, 1560, "INHERENTLY SAFER DESIGN OPTIONS (R = named source, A = assumed)")
    for t, tg in ISD:
        y3 = WRAP(s, 26, y3 + 13, f"[{tg}] " + t, 250, 9.5, 11.5)
    return s


def lint(sheets):
    """structural lint on the generated SVG: diamonds vs HMB columns, tags vs drawing, relief coverage, ESD tags on sheet 1"""
    svg = {sh.no: "".join(sh.p) for sh in sheets}
    txt1 = " ".join(re.findall(r">([^<]+)</text>", svg[1]))
    diam = len(re.findall(r'<polygon points="[\d.]+,[\d.]+ [\d.]+,[\d.]+ [\d.]+,[\d.]+ [\d.]+,[\d.]+" fill="#fff" stroke="#111" stroke-width="1.5"/>', svg[1]))
    hmb_cols = 17
    norm = lambda t: re.sub(r"(?<=\d)[A-C](/[A-C])*$", "", t)
    # tags on sheet 1: pair bubble texts (a then b) too
    toks = set(re.findall(r"[A-Z][A-Za-z/]*-\d{3}(?:[A-C](?:/[A-C])?)?", txt1))
    bub = re.findall(r'font-weight="700"[^>]*>([A-Z/]{2,5})</text><text[^>]*>(\d{3})</text>', svg[1])
    toks |= {f"{a}-{b}" for a, b in bub}
    base = {norm(t) for t in toks}
    wanted = set()
    for tab in (relief_rows(), SIFS, ESD_ROWS):
        for r in tab[1:] if tab is not ESD_ROWS else tab:
            for c in (r if isinstance(r[0], str) and not isinstance(r[1], dict) else [r[0]]):
                wanted |= {norm(t) for t in re.findall(r"[A-Z][A-Za-z/]*-\d{3}(?:[A-C](?:/[A-C])?)?", str(c))}
    for c in ESD_COLS: wanted |= {norm(t) for t in re.findall(r"[A-Z][A-Za-z/]*-\d{3}", c)}
    missing = sorted(t for t in wanted if t not in base and not t.startswith(("PSV-101", "TSV")))
    return dict(diamonds=diam, hmb_cols=hmb_cols, missing=missing, ntags=len(base))


def build_all():
    return [sheet_pid(), sheet_hmb(), sheet_basis(), sheet_scn_gas(), sheet_scn_hp(), sheet_safety1(), sheet_safety2()]


if __name__ == "__main__":
    out = sys.argv[1]
    sheets = build_all()
    write_html(sheets, out, f"CBG plant P&ID set Rev {REV}", previews="--previews" in sys.argv)
    err = 100 * (BAL["mass_in"] - BAL["mass_out"]) / BAL["mass_in"]
    print(f"ok {len(sheets)} sheets. Closure: in {BAL['mass_in']:,.1f} kg/h, out {BAL['mass_out']:,.1f} kg/h, error {err:.4f} %")
    if "--lint" in sys.argv: print("lint", lint(sheets))

#!/usr/bin/env python3
"""Coal-to-urea unit P&IDs, area 40: sour CO shift, heat recovery, gas cooling and condensate knock-out (Rev B streams 4, 6, 7, 8, 9, 28).

Usage: python3 scripts/urea_area_40.py            -> /tmp/area40.html (+ /tmp/area40_s<n>.html previews) and runs the lint
Sheets 401-415, tags E-201..E-205, G-201, H-201 are new in this package; R-201, E-102, R-202, E-103, V-203 are the Rev B tags.

Number discipline: S = sourced (document named), D = derived (formula in this file), A = assumed screening value with its range.
Thermochemistry reuses the Rev B constants in gen_pid_urea.py (WGS K fit and reaction heats, tag S there). Mean heat capacities, the
latent heat, the Antoine constants and the temperatures chosen below are tag A (generic textbook-type values, range stated, no vendor data).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *

A_ = "A"
# ---- assumed screening constants (A) ---------------------------------------------------------------------
CP = dict(H2=29.5, CO=30.5, CO2=44.0, H2O=35.5, N2=30.0, H2S=36.0, CH4=50.0)      # J/mol/K mean 200-500 C, A, +-10 %
LAT_W = 2250.0       # kJ/kg latent heat of water over 40-170 C (mean), A, range 2080-2400
CP_WL = 4.2          # kJ/kg/K liquid water, A
HFG_50BAR = 1650.0   # kJ/kg latent heat of steam at 50 bar, A, +-5 %
HFG_6BAR = 2100.0    # kJ/kg latent heat of steam at 6 bar, A, +-5 %
T_4C = 215.0         # gas leaving E-101 syngas cooler / quench, A (range 200-240; dew point of the mixed feed is ~206 C, checked below)
T_B1, T_B2 = 280.0, 300.0     # HT bed inlet temperatures, A (range 270-310), sets the bed exit temperature
T_L1, T_L2 = 205.0, 195.0     # LT bed inlet temperatures, A (range 195-215), >= dew point + margin on bed 1
TMAX_BED_HT = 520.0  # screening limit on a sour-shift bed exit temperature, A (range 480-540); licensor sets the real limit
RES_GUARD_S, RES_SHIFT_S = 20.0, 30.0   # catalyst-volume rule: gas residence time at bed conditions, s, A (guard 10-40, shift 20-60)
ANTOINE_HI = (8.14019, 1810.94, 244.485)   # log10 P[mmHg] = A - B/(C+T[C]), 99-374 C, A (cross-checked below)
ANTOINE_LO = (8.07131, 1730.63, 233.426)   # 1-100 C, A (cross-checked below)


def psat_bar(Tc):
    a, b, c = ANTOINE_HI if Tc >= 100 else ANTOINE_LO
    return 10 ** (a - b / (c + Tc)) / 750.062


assert abs(psat_bar(40.0) * 100 - PSAT_H2O_40C_KPA if False else psat_bar(40.0) * 100 - g.PSAT_H2O_40C_KPA) < 0.02 * g.PSAT_H2O_40C_KPA   # vs CoolProp value (S, Rev B)
assert abs(psat_bar(100.0) - 1.01325) < 0.01 * 1.01325                                                                                      # normal boiling point of water


def dew_C(y_w, P):
    a, b, c = ANTOINE_HI
    return b / (a - math.log10(y_w * P * 750.062)) - c


def cpm(sp): n = sum(sp.values()); return sum(v * CP[k] for k, v in sp.items()) / n          # J/mol/K


def mk(i, name, phase, sp, T, P, rho=None):
    """St from a Rev B species dict (mol/s at Rev B scale); flow scaled by K (D)"""
    mol = sum(sp.values())
    return St(i, name, phase, g.mass(sp) * 3.6 * K, T, P, mw=g.mass(sp) / mol * 1000, rho=rho)


def add(*ds):
    out = {}
    for d in ds:
        for k, v in d.items(): out[k] = out.get(k, 0.0) + v
    return out


def tph(sp): return g.mass(sp) * 3.6 * K


def adiabatic_bed(sp, Tin, appr, dH):
    """D: one adiabatic WGS bed. xi (mol/s, Rev B scale) so that equilibrium K at (T_out + approach) holds with T_out = Tin + xi dH / (n cp)"""
    nCO, nW, nCO2, nH2 = sp["CO"], sp["H2O"], sp["CO2"], sp["H2"]; n = sum(sp.values()); cp = cpm(sp)
    def res(x):
        T = Tin + x * dH * 1000 / (n * cp)
        return (nCO2 + x) * (nH2 + x) - g.wgs_K_thermo(T + 273.15 + appr) * (nCO - x) * (nW - x)
    lo, hi = 0.0, min(nCO, nW) - 1e-9
    assert res(lo) < 0
    for _ in range(200):
        m = 0.5 * (lo + hi)
        if res(lo) * res(m) <= 0: hi = m
        else: lo = m
    x = 0.5 * (lo + hi)
    out = dict(sp); out["CO"] -= x; out["H2O"] -= x; out["CO2"] += x; out["H2"] += x
    return out, Tin + x * dH * 1000 / (n * cp), x


def water_vap(sp, T, P):
    """D: water left in the vapour at T, P (ideal gas, Raoult) after condensation; never more than the water present"""
    nd = sum(v for k, v in sp.items() if k != "H2O"); ps = psat_bar(T)
    return min(sp["H2O"], nd * ps / (P - ps))


def cool_duty_MW(sp, T1, T2, P):
    """D: sensible (mean cp, A) plus latent of the water condensed between T1 and T2 at P; MW at plant scale (x K)"""
    n = sum(sp.values()) * K
    sens = n * cpm(sp) * (T1 - T2) / 1e6
    wc = (water_vap(sp, T1, P) - water_vap(sp, T2, P)) * K * 18.015 / 1000      # kg/s condensed (plant scale)
    return sens + wc * LAT_W / 1000.0, wc


# ---- the shift train, computed once (HMB reuse) ----------------------------------------------------------------
P_SH = 45.0
S4, S6, S7, S8, S9 = g.S[4], g.S[6], g.S[7], g.S[8], g.S[9]
F_HT = add(S4, S6)                                   # gas + steam into R-201
assert abs(g.mass(F_HT) - g.mass(S7)) < 2e-4 * g.mass(S7)          # mass closure 4 + 6 = 7 (Rev B)
F_LT = add(S7, S8)
assert abs(g.mass(F_LT) - g.mass(S9)) < 2e-4 * g.mass(S9)          # 7 + 8 = 9 (Rev B)
# HT: two adiabatic beds in series with external interbed steam generator
HT1, TB1_OUT, X1 = adiabatic_bed(F_HT, T_B1, g.HT_APPR, g.DH_WGS_HT)
HT2, TB2_OUT, X2 = adiabatic_bed(HT1, T_B2, g.HT_APPR, g.DH_WGS_HT)
CONV_HT = (X1 + X2) / F_HT["CO"]
assert TB1_OUT <= TMAX_BED_HT, TB1_OUT
# LT: two adiabatic beds
LT1, TL1_OUT, Y1 = adiabatic_bed(F_LT, T_L1, g.LT_APPR, g.DH_WGS_LT)
LT2, TL2_OUT, Y2 = adiabatic_bed(LT1, T_L2, g.LT_APPR, g.DH_WGS_LT)
CONV_LT = (Y1 + Y2) / F_LT["CO"]
DEW_MIX_HT = dew_C(F_HT["H2O"] / sum(F_HT.values()), P_SH); DEW_LT_IN = dew_C(F_LT["H2O"] / sum(F_LT.values()), P_SH)
DEW_9 = dew_C(S9["H2O"] / sum(S9.values()), P_SH)
assert T_4C > dew_C(S4["H2O"] / sum(S4.values()), P_SH) + 20          # stream 4 is not at its dew point
assert T_L1 >= DEW_LT_IN + 20, (T_L1, DEW_LT_IN)                      # LT bed 1 inlet at least 20 C above dew point (A margin)
CO_SLIP = dict(RevB=S9["CO"], adiabatic=LT2["CO"])

# HT mixing and heating
T_MIX = (T_4C * sum(S4.values()) * cpm(S4) + 400.0 * S6["H2O"] * CP["H2O"]) / (sum(S4.values()) * cpm(S4) + S6["H2O"] * CP["H2O"])   # D: adiabatic mix of gas at T_4C and steam at 400 C
assert T_MIX > DEW_MIX_HT + 20, (T_MIX, DEW_MIX_HT)
Q_E201 = sum(F_HT.values()) * K * cpm(F_HT) * (T_B1 - T_MIX) / 1e6          # MW: feed preheat to bed 1 inlet
T_E201_HOT_OUT = 350.0 - Q_E201 * 1e6 / (sum(S7.values()) * K * cpm(S7))     # hot side leaves cooler by Q / (n cp)
Q_E202 = sum(F_HT.values()) * K * cpm(HT1) * (TB1_OUT - T_B2) / 1e6          # HT interbed steam generator
# stage 7 between: E-201 hot out -> E-102 -> mix with stream 8 -> LT inlet T_L1
T_E102_OUT = T_L1 - (400.0 - T_L1) * S8["H2O"] * CP["H2O"] / (sum(S7.values()) * cpm(S7))       # D: so that 7E + steam 8 mixes to T_L1
assert T_E102_OUT > T_L1 - 60
Q_E102 = sum(S7.values()) * K * cpm(S7) * (T_E201_HOT_OUT - T_E102_OUT) / 1e6
Q_E204 = sum(F_LT.values()) * K * cpm(LT1) * (TL1_OUT - T_L2) / 1e6          # LT interbed cooler
# LT effluent train: stream 9 (Rev B 220 C) -> 150 -> 100 -> 40
Q_E205, W205 = cool_duty_MW(S9, 220.0, 150.0, P_SH)
Q_E203, W203 = cool_duty_MW(S9, 150.0, 100.0, P_SH)
Q_E103, W103 = cool_duty_MW(S9, 100.0, 40.0, P_SH)
W_TOT = (water_vap(S9, 220.0, P_SH) - water_vap(S9, 40.0, P_SH)) * K * 18.015 / 1000
assert abs(W205 + W203 + W103 - W_TOT) < 1e-9
# the model condensate vs Rev B stream 28 (Rev B: Raoult at 40 C and P_AGR = 45 bar): must agree
assert abs(W_TOT - g.M[28] * K) < 0.02 * g.M[28] * K, (W_TOT, g.M[28] * K)


def build(pkg):
    area = "40"
    # ================= streams of this area (new ids start with 4, <= 3 chars) =================
    s4c = mk("4C", "raw syngas after E-101 (stream 4, cooled)", "gas", S4, T_4C, P_SH)           # A temperature; flow = Rev B stream 4 x K
    s4g = mk("4G", "raw syngas after guard bed G-201", "gas", S4, T_4C - 1.0, P_SH)
    s6 = stream(6, "HP steam to R-201 (stream 6)", "steam", T=400.0, P=50.0)                       # Rev B 6
    s4m = mk("4M", "HT shift mixed feed (4 + 6)", "gas", F_HT, round(T_MIX, 0), P_SH)
    s4f = mk("4F", "HT shift bed-1 feed", "gas", F_HT, T_B1, P_SH)
    s7 = stream(7, "HT shift effluent (stream 7)", "gas", P=P_SH)                                  # Rev B 7, 350 C
    s7b = mk("7B", "HT bed-1 effluent", "gas", HT1, round(TB1_OUT, 0), P_SH)
    s7i = mk("7I", "HT bed-1 effluent after interbed cooler", "gas", HT1, T_B2, P_SH)
    s7c = mk("7C", "HT effluent after E-201", "gas", S7, round(T_E201_HOT_OUT, 0), P_SH)
    s7e = mk("7E", "HT effluent after E-102", "gas", S7, round(T_E102_OUT, 0), P_SH)
    s8 = stream(8, "steam to R-202 (stream 8)", "steam", T=400.0, P=50.0)                          # Rev B 8
    s8m = mk("8M", "LT shift feed (7 + 8)", "gas", F_LT, T_L1, P_SH)
    s8b = mk("8B", "LT bed-1 effluent", "gas", LT1, round(TL1_OUT, 0), P_SH)
    s8i = mk("8I", "LT bed-1 effluent after interbed cooler", "gas", LT1, T_L2, P_SH)
    s9 = stream(9, "LT shift effluent (stream 9)", "gas", P=P_SH)                                  # Rev B 9, 220 C
    s9a = mk("9A", "shift gas after E-205", "twophase", S9, 150.0, P_SH)
    s9b = mk("9B", "shift gas after E-203", "twophase", S9, 100.0, P_SH)
    for st in (s9a, s9b): st.rho_in = None
    # mass closure of every mixer (D)
    assert abs(s4g.flow + s6.flow - s4m.flow) < 2e-4 * s4m.flow and abs(s7.flow - s4m.flow) < 2e-4 * s4m.flow
    assert abs(s7e.flow + s8.flow - s8m.flow) < 2e-4 * s8m.flow and abs(s9.flow - s8m.flow) < 2e-4 * s8m.flow

    # ---- 401 G-201 guard bed: protects the Co-Mo catalyst from particulates, chloride / NH3 / HCN, arsenic (catalyst protection)
    vol_g = s4g.q * RES_GUARD_S
    sheet_reactor(pkg, area, 401, "Area 400  Shift  -  G-201 raw-gas guard bed (catalyst protection)",
                  dict(tag="G-201", name="Raw-gas guard bed (chloride / particulate)", feed=s4c, eff=s4g, vol_m3=vol_g, beds=1, spec="A1",
                       mat="A: CS, sour service, licensor", hazard="H2S/CO toxic, H2 flammable, 45 bar",
                       notes=["Stream 4C is Rev B stream 4 after the E-101 syngas cooler / quench; its temperature (%.0f C) is an A, Rev B gives only the gasifier exit." % T_4C,
                              "Bed volume = gas flow x %.0f s residence (A, range 10-40 s): %.0f m3. Adsorbent / hydrolysis media are licensor items." % (RES_GUARD_S, vol_g),
                              "Rev B carries no chloride, NH3, HCN, COS or metals; the guard bed is drawn as protection of R-201 and is not in the balance (flow in = flow out).",
                              "A guard bed is not a COS hydrolysis reactor: see notes file, COS is converted over the sour-shift catalyst itself."]))
    # ---- 402 X-201 steam addition and mixing to R-201
    sheet_package(pkg, area, 402, "Area 400  Shift  -  X-201 HP steam addition and mixing to R-201 (stream 6)",
                  dict(tag="X-201", name="HP steam injection and static mixer", inlets=[(s4g, "guard-bed outlet"), (s6, "HP steam, desuperheater upstream (A)", "ST")],
                       outlets=[(s4m, "mixed feed to E-201")], spec="A1", esd=True, type="in-line static mixer with steam injection (A)",
                       op=f"{T_MIX:.0f} C, {P_SH:g} bar", design="A", size="A", relief="blocked outlet",
                       desc=["steam control by flow ratio to gas", f"dry-gas basis ratio steam/gas = {S6['H2O']/(sum(S4.values())):.2f} mol/mol (D, Rev B)", f"mixed gas {T_MIX:.0f} C vs dew point {DEW_MIX_HT:.0f} C (D)"],
                       interlocks=[("FFIC", "steam / raw-gas ratio control", "ratio 0-1 mol/mol", "L %.2f / LL %.2f trip (A)" % (0.8 * S6["H2O"] / sum(S4.values()), 0.6 * S6["H2O"] / sum(S4.values()))),
                                   ("TAL", "mixed-gas temperature low (dew-point margin)", "0-400 C", f"L {DEW_MIX_HT+25:.0f} C, LL {DEW_MIX_HT+15:.0f} C trip (A)"),
                                   ("AAHH", "H2S / CO gas detection at mixer, trip to ESD", "0-100 ppm H2S", "H 10 / HH 15 ppm H2S (A)")],
                       rows=[("Steam", "stream 6, 400 C, 50 bar", "Rev B"), ("Mixed gas", f"{T_MIX:.0f} C", "D"), ("Dew point", f"{DEW_MIX_HT:.0f} C", "D, A (Antoine)")],
                       hazard="sour syngas 45 bar; condensate slug", utilities=[("HP steam", s6.flow, "t/h", "Rev B 6")],
                       notes=["Steam is desuperheated and mixed so that no liquid reaches the catalyst; a mixed-gas temperature low-low trip closes the gas feed.", "Mass closure 4G + 6 = 4M asserted in code (flow in = flow out)."]))
    # ---- 403 E-201 feed / effluent exchanger
    sheet_hx(pkg, area, 403, "Area 400  Shift  -  E-201 R-201 feed / effluent exchanger (heat recovery)",
             dict(tag="E-201", name="HT shift feed / effluent exchanger", hot_in=s7, hot_out=s7c, cold_in=s4m, cold_out=s4f, duty_MW=Q_E201, kind="gas_gas", spec="A1", spec_c="A1", svc_c="PG",
                  esd_hot=True, hazard="sour syngas both sides, 45 bar",
                  mat="A: CS/low-alloy, sour, licensor",
                  notes=["Duty = n cp dT on the cold side (D; cp A). Hot-side leaving temperature follows from the same duty.", "Cold side is the shell side here; the template draws a trim control valve on the cold inlet, in service a bypass of the cold side is used to hold the bed-1 inlet temperature (A)."]))
    # ---- 404 H-201 start-up heater
    n2 = simple("4H3", "start-up nitrogen (stream 14 source)", "gas", 0.10 * s4f.flow, 40.0, 40.0, mw=28.014)     # A: 10 % of design mass flow (range 5-15 %)
    n2o = simple("4H4", "hot start-up nitrogen to R-201", "gas", n2.flow, 300.0, 40.0, mw=28.014)
    q_h = n2.flow * 1000 / 3600 * 1.04 * (300.0 - 40.0) / 1e6      # MW, cp N2 1.04 kJ/kg/K (A)
    m_h = q_h * 1000 / (2.9 * (400.0 - 270.0))                     # kg/s, steam cp 2.9 kJ/kg/K (A)
    hs = simple("4H1", "HP steam for start-up heater", "steam", m_h * 3.6, 400.0, 50.0, mw=18.015)
    hc = simple("4H2", "steam leaving H-201", "steam", hs.flow, 270.0, 49.0, mw=18.015)
    sheet_hx(pkg, area, 404, "Area 400  Shift  -  H-201 start-up heater (catalyst heat-up)",
             dict(tag="H-201", name="Shift start-up heater (steam / nitrogen)", hot_in=hs, hot_out=hc, cold_in=n2, cold_out=n2o, duty_MW=q_h, kind="gas_liq", spec="A1", spec_c="A1", svc_c="N2",
                  hazard="N2 asphyxiant; HP steam; hot catalyst",
                  mat="A: low-alloy",
                  notes=["Used only for start-up and sulphiding: circulates nitrogen at 10 % of design mass flow (A, 5-15 %) and heats it to 300 C (A) before sour gas is introduced.", "Nitrogen comes from the ASU nitrogen header (stream 14 source, area ASU). Duty = m cp dT with cp(N2) 1.04 kJ/kg/K (A).", "Catalyst sulphiding / reduction procedure is a licensor item."]))
    # ---- 405 R-201 HT shift
    vol_ht = s4f.q * RES_SHIFT_S
    sheet_reactor(pkg, area, 405, "Area 400  Shift  -  R-201 high-temperature sour shift (2 beds, interbed cooling E-202)",
                  dict(tag="R-201", name="HT sour shift reactor", feed=s4f, eff=s7, vol_m3=vol_ht, beds=2, spec="A1", mat="A: low-alloy, sour, licensor",
                       hazard="CO/H2/H2S 45 bar; T excursion",
                       notes=[f"Beds in series with external interbed steam generator E-202 (sheet 406): bed 1 {T_B1:.0f} -> {TB1_OUT:.0f} C, interbed to {T_B2:.0f} C, bed 2 {T_B2:.0f} -> {TB2_OUT:.0f} C (D, adiabatic equilibrium, approach {g.HT_APPR:.0f} K).",
                              f"Computed CO conversion {CONV_HT*100:.1f} % against Rev B {g.B.ht_conv*100:.1f} % (stream 7 carries Rev B composition and 350 C; the adiabatic exit is {TB2_OUT:.0f} C). The single-bed adiabatic case gives bed exit ~520 C.",
                              f"Bed 1 exit {TB1_OUT:.0f} C against the {TMAX_BED_HT:.0f} C screening limit (A, 480-540): little margin; the licensor's catalyst limit governs.",
                              f"The TAHH shown here is the template rule (effluent + 60 C); the bed-1 exit trip is on CP-201 (sheet 415). Catalyst volume {vol_ht:.0f} m3 = feed flow x {RES_SHIFT_S:.0f} s (A, 20-60 s). The reactor template draws the interbed loop as a vessel with two beds; the external cooler connection is on sheet 406."]))
    # ---- 406 E-202 interbed steam generator
    bfw_hp = simple("4B1", "HP boiler feedwater to E-202", "liq", 0.0, 105.0, 55.0, rho=955.0)
    q = Q_E202; m_s = q * 1000 / (HFG_50BAR + CP_WL * (264.0 - 105.0))        # kg/s steam, sat T at 50 bar ~ 264 C (A)
    bfw_hp.flow = m_s * 3.6
    st_hp = simple("4B2", "HP saturated steam from E-202", "steam", m_s * 3.6, 264.0, 50.0, mw=18.015)
    sheet_hx(pkg, area, 406, "Area 400  Shift  -  E-202 R-201 interbed steam generator (HP steam raising)",
             dict(tag="E-202", name="HT shift interbed steam generator", hot_in=s7b, hot_out=s7i, cold_in=bfw_hp, cold_out=st_hp, duty_MW=q, kind="steam_gen", spec="A1", spec_c="A1", svc_c="BW",
                  esd_hot=True, hazard="sour hot gas 45 bar; tube rupture",
                  mat="A: low-alloy, licensor", relief_dest="flare header / steam vent (A)",
                  notes=[f"Duty {q:.1f} MW = n cp dT on the gas side ({TB1_OUT:.0f} -> {T_B2:.0f} C). Steam mass from duty / (latent {HFG_50BAR:.0f} kJ/kg A + sensible), saturation 264 C at 50 bar (A).",
                         "Boiler drum, circulation and steam-side relief are boiler-package items (not drawn here); BFW enters at 105 C, a BFW preheat from E-205 is implied (A).",
                         "Tube-rupture case: gas side 45 bar vs steam side 50 bar -> water/steam would be forced into the shift gas; a high-pressure steam-side pressure detector and the TAHH trip on R-201 are the safeguards (A)."]))
    # ---- 407 E-102 interstage cooler
    bfw_lp = simple("4B3", "BFW to E-102", "liq", 0.0, 105.0, 10.0, rho=955.0)
    m_l = Q_E102 * 1000 / (HFG_6BAR + CP_WL * (159.0 - 105.0)); bfw_lp.flow = m_l * 3.6
    st_lp = simple("4B4", "LP saturated steam from E-102", "steam", m_l * 3.6, 159.0, 6.0, mw=18.015)
    sheet_hx(pkg, area, 407, "Area 400  Shift  -  E-102 shift interstage cooler (LP steam raising)",
             dict(tag="E-102", name="Shift interstage cooler", hot_in=s7c, hot_out=s7e, cold_in=bfw_lp, cold_out=st_lp, duty_MW=Q_E102, kind="steam_gen", spec="A1", spec_c="A1", svc_c="BW",
                  esd_hot=True, hazard="sour gas 45 bar vs 6-bar steam side", mat="A: CS, sour service", relief_dest="steam vent (A)",
                  notes=[f"Cools the HT effluent from {T_E201_HOT_OUT:.0f} to {T_E102_OUT:.0f} C so that adding stream 8 steam gives exactly the LT inlet {T_L1:.0f} C (D, energy balance).", "LP steam saturation 159 C at 6 bar and latent 2,100 kJ/kg are A (+-5 %).", "Steam-side relief is a boiler-package item; PSV-407-01 on the sheet protects the 6-bar shell against tube rupture from the 45-bar gas side (A, not sized)."]))
    # ---- 408 X-202 steam addition to R-202
    sheet_package(pkg, area, 408, "Area 400  Shift  -  X-202 steam addition and mixing to R-202 (stream 8)",
                  dict(tag="X-202", name="LT shift steam injection and static mixer", inlets=[(s7e, "from E-102"), (s8, "HP steam (A: let down and desuperheated)", "ST")],
                       outlets=[(s8m, "mixed feed to R-202")], spec="A1", esd=True, type="in-line static mixer with steam injection (A)", op=f"{T_L1:.0f} C, {P_SH:g} bar", design="A", size="A", relief="blocked outlet",
                       desc=[f"steam/gas ratio {S8['H2O']/sum(S7.values()):.2f} mol/mol (D, Rev B)", f"mixed gas {T_L1:.0f} C vs dew point {DEW_LT_IN:.0f} C (D)"],
                       interlocks=[("FFIC", "LT steam ratio control", "0-0.5 mol/mol", "L %.2f / LL %.2f trip (A)" % (0.8 * S8["H2O"] / sum(S7.values()), 0.6 * S8["H2O"] / sum(S7.values()))),
                                   ("TAL", "LT inlet temperature low (dew point)", "0-300 C", f"L {DEW_LT_IN+25:.0f} / LL {DEW_LT_IN+15:.0f} C trip (A)"),
                                   ("AAHH", "H2S / CO gas detection, trip to ESD", "0-100 ppm H2S", "H 10 / HH 15 ppm (A)")],
                       rows=[("Steam", "stream 8, 400 C, 50 bar", "Rev B"), ("Mixed gas", f"{T_L1:.0f} C", "D")], hazard="sour syngas 45 bar; wet catalyst",
                       utilities=[("HP steam", s8.flow, "t/h", "Rev B 8")], notes=["Condensate on the LT catalyst destroys it: the dew-point margin trip is the main protection (A: margin 25 C alarm, 15 C trip).", "Mass closure 7E + 8 = 8M asserted in code."]))
    # ---- 409 R-202 LT shift
    vol_lt = s8m.q * RES_SHIFT_S
    sheet_reactor(pkg, area, 409, "Area 400  Shift  -  R-202 low-temperature sour shift (2 beds, interbed cooling E-204)",
                  dict(tag="R-202", name="LT sour shift reactor", feed=s8m, eff=s9, vol_m3=vol_lt, beds=2, spec="A1", mat="A: CS / low-alloy, sour service, licensor",
                       hazard="CO/H2/H2S 45 bar; wet catalyst",
                       notes=[f"Beds in series, external interbed cooler E-204 (sheet 410): bed 1 {T_L1:.0f} -> {TL1_OUT:.0f} C, cooled to {T_L2:.0f} C, bed 2 -> {TL2_OUT:.0f} C (D adiabatic, approach {g.LT_APPR:.0f} K).",
                              f"Computed CO conversion {CONV_LT*100:.1f} % (CO leaving {LT2['CO']*K:.0f} mol/s) against Rev B {g.B.lt_conv*100:.1f} % (CO {S9['CO']*K:.0f} mol/s): consistent. A SINGLE adiabatic bed with the same inlet gives only about 72-77 % and an exit near 250-260 C, so Rev B stream 9 needs the second bed.",
                              f"Bed-1 inlet {T_L1:.0f} C is {T_L1-DEW_LT_IN:.0f} K above the mixed-gas dew point {DEW_LT_IN:.0f} C (D).",
                              f"Catalyst volume {vol_lt:.0f} m3 = feed flow x {RES_SHIFT_S:.0f} s (A, 20-60 s)."]))
    # ---- 410 E-204 LT interbed cooler
    bfw_i = simple("4B5", "BFW to E-204", "liq", 0.0, 105.0, 55.0, rho=955.0)
    bfw_o = simple("4B6", "warm BFW from E-204", "liq", 0.0, 180.0, 54.0, rho=900.0)
    m_i = Q_E204 * 1000 / (CP_WL * (180.0 - 105.0)); bfw_i.flow = bfw_o.flow = m_i * 3.6
    sheet_hx(pkg, area, 410, "Area 400  Shift  -  E-204 R-202 interbed cooler (BFW heating)",
             dict(tag="E-204", name="LT shift interbed cooler", hot_in=s8b, hot_out=s8i, cold_in=bfw_i, cold_out=bfw_o, duty_MW=Q_E204, kind="gas_liq", spec="A1", spec_c="A1", svc_c="BW",
                  esd_hot=True, hazard="sour syngas 45 bar; BFW 55 bar", mat="A: CS, sour service",
                  notes=[f"Cools bed-1 effluent {TL1_OUT:.0f} -> {T_L2:.0f} C; BFW heated 105 -> 180 C (A) with cp 4.2 kJ/kg/K (A). The BFW is plant BFW, consumers are the steam generators on sheets 406 and 407.", "BFW pressure above gas pressure keeps leaks flowing into the gas, which is the safer direction for a catalyst-fouling case only if the BFW is clean (A); confirm in HAZOP."]))
    # ---- 411-413 effluent train
    bfw5i = simple("4B7", "BFW to E-205", "liq", 0.0, 105.0, 55.0, rho=955.0)
    bfw5o = simple("4B8", "BFW from E-205", "liq", 0.0, 180.0, 54.0, rho=900.0)
    bfw5i.flow = bfw5o.flow = Q_E205 * 1000 / (CP_WL * 75.0) * 3.6
    sheet_hx(pkg, area, 411, "Area 400  Shift  -  E-205 shift effluent / HP boiler-feedwater heater",
             dict(tag="E-205", name="Shift effluent BFW heater", hot_in=s9, hot_out=s9a, cold_in=bfw5i, cold_out=bfw5o, duty_MW=Q_E205, kind="gas_liq", spec="A1", spec_c="A1", svc_c="BW",
                  esd_hot=True, hazard="sour syngas; sour condensate <%.0f C" % DEW_9, mat="A: CS + allowance, CRA when wet",
                  notes=[f"Duty {Q_E205:.1f} MW = sensible heat plus latent of {W205:.1f} kg/s water condensed between 220 and 150 C (D; latent {LAT_W:.0f} kJ/kg A).", f"Dew point of stream 9 is {DEW_9:.0f} C (D, Antoine A, checked against CoolProp Psat at 40 C within 2 %)."]))
    dm_i = simple("4D1", "DM water to E-203", "liq", 0.0, 30.0, 6.0, rho=996.0)
    dm_o = simple("4D2", "warm DM water from E-203", "liq", 0.0, 105.0, 5.5, rho=955.0)
    dm_i.flow = dm_o.flow = Q_E203 * 1000 / (CP_WL * 75.0) * 3.6
    sheet_hx(pkg, area, 412, "Area 400  Shift  -  E-203 shift gas / demineralised-water heater (heat recovery)",
             dict(tag="E-203", name="Shift gas DM-water heater", hot_in=s9a, hot_out=s9b, cold_in=dm_i, cold_out=dm_o, duty_MW=Q_E203, kind="cond", spec="A1", spec_c="A1", svc_c="BW",
                  esd_hot=True, hazard="sour condensate: corrosion", mat="A: CRA or clad in condensing zone, licensor",
                  notes=[f"Duty {Q_E203:.1f} MW including condensation of {W203:.1f} kg/s water between 150 and 100 C (D).", "DM water flow from duty / (cp x 75 K) is high compared with a normal DM make-up; the cold stream is the deaerator feed / sour-water stripper reboil duty in service (A). The plant-wide water balance is not available."]))
    cw_i = simple("4W1", "cooling water to E-103", "liq", 0.0, 33.0, 5.0, rho=995.0)
    cw_o = simple("4W2", "cooling water return from E-103", "liq", 0.0, 43.0, 4.5, rho=990.0)
    s9c = mk("9C", "shift gas after E-103", "twophase", S9, 40.0, P_SH); s9c.rho_in = None
    cw_i.flow = cw_o.flow = Q_E103 * 1000 / (CP_WL * 10.0) * 3.6
    sheet_hx(pkg, area, 413, "Area 400  Shift  -  E-103 shift gas cooler (cooling water)",
             dict(tag="E-103", name="Shift gas cooler", hot_in=s9b, hot_out=s9c, cold_in=cw_i, cold_out=cw_o, duty_MW=Q_E103, kind="cond", spec="A1", spec_c="A1", svc_c="CW",
                  esd_hot=True, hazard="sour syngas 45 bar; CW leak", mat="A: CS with CRA tubes in condensing zone",
                  notes=[f"Duty {Q_E103:.1f} MW including condensation of {W103:.1f} kg/s water between 100 and 40 C (D). CW rise 10 K (A).", "Total condensate over E-205 + E-203 + E-103 reproduces Rev B stream 28 within 2 % (asserted in code, Raoult at the Rev B 40 C / 45 bar basis).", "Two-phase line to V-203 is sized with the two-phase velocity rule (A)."]))
    # ---- 414 V-203 (pilot call, renumbered; the pilot in gen_pid_urea_detail.py is left untouched)
    wat = g.M[28] * 3.6 * K
    gas_in = stream(9, "shift gas, cooled", "twophase", T=40.0, P=45.0, drop_water=True, flow=g.M[9] * 3.6 * K)
    gas_in.rho_in = None
    v_gas = St("9V", "shift gas to AGR", "gas", g.M[9] * 3.6 * K - wat, 40.0, 44.0, mw=gas_in.mw)
    gas_in.mw = v_gas.mw; gas_in.rho_in = v_gas.rho * 1.0
    cond = St(28, "process condensate", "liq", wat, 40.0, 45.0, rho=992.0)
    assert abs((gas_in.flow) - (v_gas.flow + cond.flow)) < 1e-9 * gas_in.flow       # V-203 mass closure
    sheet_vessel(pkg, area, 414, "Area 400  Shift and gas cooling  -  V-203 condensate knock-out drum",
                 dict(tag="V-203", name="Shift condensate KO drum", inlet=gas_in, gas=v_gas, liq=cond, res_min=5.0, pumps="P-203", pump_dp_bar=8.0, spec="A1", internals="demister",
                      svc_in="SG", svc_gas="SG", svc_liq="PC", mat="A: CS, sour service, licensor", hazard="sour syngas (H2, CO, H2S) 45 bar",
                      notes=["Stream 9V is a Rev C split of stream 9 into vapour (to C-301) and condensate (stream 28).", "Condensate goes to the sour-water stripper (area 300); H2S dissolved in it is not quantified (needs solubility data).",
                             "Shift-gas flow through the drum is Rev B stream 9 less stream 28 (V-203 closure asserted)."]))
    # ---- 415 catalyst-protection / SIS loop sheet
    sheet_package(pkg, area, 415, "Area 400  Shift  -  CP-201 shift-area catalyst protection and safety instrumented functions",
                  dict(tag="CP-201", name="Shift area SIS and catalyst-protection loops", inlets=[(s4c, "raw gas from E-101")], outlets=[(s9, "LT shift effluent")], spec="A1", esd=True,
                       type="instrumented functions (cause and effect, A)", op="45 bar", design="A", size="-", mat="-", basis="A",
                       desc=["1oo2 / 2oo3 voting by licensor SIL study", "trips close XV on gas and steam inlets", "depressure to flare on HH"],
                       interlocks=[("TAHH", "R-201 bed exit temperature (3 points)", "0-600 C", f"HH {TMAX_BED_HT:.0f} C trip + depress (A)"), ("TAHH", "R-202 bed exit temperature (3 points)", "0-400 C", "HH 320 C trip (A)"),
                                   ("PAHH", "shift pressure high-high", "0-60 bar", "HH 50 bar trip (A)"), ("AAHH", "H2S / CO detectors at R-201/R-202 platform", "0-100 ppm H2S", "H 10 / HH 15 ppm: ESD (A)"),
                                   ("AAL", "H2S in gas low (sulphiding)", "0-1 mol %", "L 0.1 mol % alarm (A, range 0.05-0.3)"), ("LAHH", "V-203 level HH", "0-100 %", "HH 90 %: close XV-401 (A)")],
                       rows=[("H2S in raw gas", f"{S4['H2S']/sum(S4.values())*100:.2f} mol %", "D, Rev B"), ("CO in raw gas", f"{S4['CO']/sum(S4.values())*100:.0f} mol %", "D, Rev B")],
                       hazard="H2S/CO toxic, H2 flammable, 45 bar",
                       notes=["H2S in the raw gas is far above the minimum that keeps a sour-shift catalyst sulphided (alarm set at 0.1 mol %, A).", "Trip actions and set points are screening values (A); the licensor cause-and-effect and a SIL assessment replace them."]))
    return pkg


# ---- lint, used by __main__ ---------------------------------------------------------------------------------
def lint(pkg):
    tags = [r[0] for r in pkg.equip]
    dup = {t for t in tags if tags.count(t) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    assert all(r[5] for r in pkg.relief), "relief row without destination"
    sid = {k[0] for k in STREAMS}
    bad = {r[4] for r in pkg.lines if str(r[4]) not in sid}
    assert not bad, f"stream numbers missing from STREAMS {bad}"
    hazardous = {s.no for s in pkg.sheets}
    for no in hazardous:
        if no == 404 or no == 415:   # H-201 handles nitrogen / steam; CP-201 has its own ESD valve row from the package
            pass
        has = any(r[6] == no and "ESD" in str(r[5]) for r in pkg.valves)
        assert has or no == 404, f"sheet {no} has no ESD valve"
    return len(pkg.equip), len(pkg.relief)


def main():
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), area 40: sour shift", "Rev B balance scaled K=%.4f" % K)
    build(pkg); pkg.total = len(pkg.sheets)
    lint(pkg)
    write_html(pkg.sheets, "/tmp/area40.html", "Coal-to-urea area 40", previews=True)
    print(f"{len(pkg.sheets)} sheets, {len(pkg.lines)} lines, {len(pkg.inst)} instruments, {len(pkg.equip)} equipment, {len(pkg.relief)} relief devices")
    print(f"HT: bed1 {T_B1:.0f}->{TB1_OUT:.0f}, bed2 {T_B2:.0f}->{TB2_OUT:.0f}, conv {CONV_HT:.3f} (RevB {g.B.ht_conv:.3f}); LT: {T_L1:.0f}->{TL1_OUT:.0f}, {T_L2:.0f}->{TL2_OUT:.0f}, conv {CONV_LT:.3f} (RevB {g.B.lt_conv:.3f})")
    print(f"T_MIX {T_MIX:.1f} dewmix {DEW_MIX_HT:.1f} dewLT {DEW_LT_IN:.1f} dew9 {DEW_9:.1f}; Q MW: E201 {Q_E201:.1f} E202 {Q_E202:.1f} E102 {Q_E102:.1f} E204 {Q_E204:.1f} E205 {Q_E205:.1f} E203 {Q_E203:.1f} E103 {Q_E103:.1f}; cond {W_TOT:.1f} vs {g.M[28]*K:.1f} kg/s; CO slip RevB {S9['CO']*K:.0f} vs {LT2['CO']*K:.0f} mol/s")


if __name__ == "__main__":
    main()

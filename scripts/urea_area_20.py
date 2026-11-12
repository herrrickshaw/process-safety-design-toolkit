#!/usr/bin/env python3
"""Area 20: air separation unit ASU-101 broken into unit sheets 201-216, coal-to-urea package.

Usage: python3 scripts/urea_area_20.py     (builds /tmp/area20.html + per-sheet previews, runs the lint)

Mass basis: Rev B stream 25 (air), 2 (O2), 14 (N2 to the ammonia loop), 26 (surplus N2), scaled to 3,850 t/d urea (urea_basis, K).
Rev B closure: 25 = 2 + 14 + 26 (O2 and N2 only; argon, CO2 and water of air are not in Rev B).  Here stream 26 is split:
the N2 import of area 10 (lock hoppers, dense-phase conveying; urea_area_10) is taken from it, the remainder is the vent.
ASU electric power: Rev B 275 kWh/t O2 (gen_pid_urea, TDA / DOE-FE-0026142 p.12, range 250-300, single source). The train powers computed
here are a bottom-up check (D from stated stage counts and efficiencies, A) and are compared with it in the notes.
O2-service statements cite EIGA Doc 13/20 "Oxygen pipeline and piping systems" (fetched and read: sections 4.2, 4.4, 6.1); no number is taken from it.
Property values typed here (latent heats, liquid densities, saturation temperatures) are textbook values tagged A; no property package is available (stdlib only).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *
import urea_area_10 as a10

AREA = "20"
MWO2, MWN2 = g.MW["O2"], g.MW["N2"]
PAR = dict(
    p_air_in=(0.98, "0.97-0.99", "air after intake filter, bar abs"), p_mac=(6.0, "5-8", "main air compressor discharge, bar abs"),
    eta_air=(0.80, "0.75-0.85", "MAC isentropic efficiency per stage"), eta_gas=(0.75, "0.70-0.80", "O2 and N2 compressor isentropic efficiency (K-401 uses 0.75 A in gen_pid_urea)"),
    k_diatomic=(1.4, "D", "ideal diatomic gas heat-capacity ratio (kinetic theory: 7/5)"), r_stage_max=(3.5, "3-4", "maximum pressure ratio per stage"),
    cp_air=(1.005, "1.00-1.01", "air specific heat kJ/kg/K"), cp_n2=(1.04, "1.03-1.05", "N2 specific heat kJ/kg/K"), cp_w=(4.18, "4.1-4.2", "water kJ/kg/K"),
    t_dcc_out=(15.0, "10-20", "air out of direct-contact cooler, C"), w_in=(8.0, "5-12", "chilled water in, C"), w_out=(25.0, "20-30", "water out of DCC, C"),
    regen_frac=(0.10, "0.05-0.20", "regeneration N2 as fraction of air flow"), t_regen=(180.0, "150-250", "regeneration gas temperature, C"),
    x_b=(0.36, "0.30-0.40", "HP column sump O2 mole fraction (crude oxygen)"),
    p_hp=(5.5, "5-6", "HP column pressure, bar abs"), p_lp=(1.4, "1.3-1.6", "LP column pressure at the sump, bar abs"),
    p_o2_lp=(1.3, "1.2-1.4", "O2 gas from cold box, bar abs"), p_n2_hp=(5.2, "4.8-5.4", "HP N2 from cold box, bar abs"), p_n2_lp=(1.1, "1.05-1.2", "waste N2, bar abs"),
    lox_h=(4.0, "1-8", "LOX backup, h at full O2 flow"), lin_h=(2.0, "1-4", "LIN backup, h at ammonia-loop N2 flow"), refill_lox_h=(48.0, "24-72", "LOX refill time, h"), refill_lin_h=(24.0, "12-48", "LIN refill time, h"),
    rho_lox=(1140.0, "1100-1150", "LOX density kg/m3 (textbook)"), rho_lin=(807.0, "790-810", "LIN density kg/m3 (textbook)"), rho_rich=(900.0, "800-1000", "crude oxygen liquid density kg/m3"),
    L_o2=(213.0, "200-220", "O2 latent heat kJ/kg (textbook)"), L_n2=(199.0, "190-205", "N2 latent heat kJ/kg (textbook)"), cp_o2=(0.92, "0.91-0.93", "O2 kJ/kg/K"),
    t_hw_in=(80.0, "60-90", "vaporiser hot water in, C"), t_hw_out=(50.0, "40-60", "vaporiser hot water out, C"),
)
P_ = {k: v[0] for k, v in PAR.items()}
closed = a10.closed


def stage_power_MW(m_t_h, mw, T1_C, ratio, eta, k=None):
    """D: multistage compression with ideal intercooling to T1: W = N k/(k-1) m Rs T1 (r_s^((k-1)/k) - 1) / eta; N = ceil(ln r / ln r_max)"""
    k = k or P_["k_diatomic"]; N = max(1, math.ceil(math.log(ratio) / math.log(P_["r_stage_max"])))
    rs = ratio ** (1.0 / N); Rs = R_GAS / (mw / 1000.0)
    w = N * k / (k - 1) * (m_t_h * 1000 / 3600) * Rs * (T1_C + 273.15) * (rs ** ((k - 1) / k) - 1) / eta
    return w / 1e6, N


# ---- balance ------------------------------------------------------------------------------------------------------------
s25 = stream(25, "air to ASU-101", "gas", T=25.0, P=1.0)
AIR = s25.flow; MW_AIR = s25.mw
s2 = stream(2, "oxygen ASU-101 to R-101", "gas", T=40.0, P=50.0)
s14 = stream(14, "N2 from ASU to K-401", "gas", T=40.0, P=40.0)
O2, N2_LOOP = s2.flow, s14.flow
N2_G = a10.N2_HP_TOTAL                      # t/h HP N2 to area 10 users (D, urea_area_10)
N2_ALL = AIR - O2                           # t/h, all N2 in air (Rev B: O2 and N2 only)
VENT = N2_ALL - N2_LOOP - N2_G              # t/h waste N2, Rev B stream 26 less the area-10 import
S26_REVB = g.M[26] * 3.6 * K
assert abs(N2_ALL - N2_LOOP - S26_REVB) < 1e-6, "Rev B closure 25 = 2 + 14 + 26"
N2_PROD = N2_LOOP + N2_G                     # HP N2 product from the cold box
# HP / LP column split (D from x_b, A)
w_b = P_["x_b"] * MWO2 / (P_["x_b"] * MWO2 + (1 - P_["x_b"]) * MWN2)        # mass fraction O2 in crude liquid
BOT = O2 / w_b; N2_BOT = BOT - O2; N2_TOP = N2_ALL - N2_BOT                  # t/h
REFLUX = VENT - N2_BOT                                                         # t/h LIN reflux to LP column (D from closure)
assert abs((N2_TOP - REFLUX) - N2_PROD) < 1e-6, "HP column top = reflux + HP N2 product"
assert REFLUX > 0 and N2_PROD > 0
# air-side chain
Q_DCC = AIR / 3.6 * P_["cp_air"] * (40.0 - P_["t_dcc_out"]) / 1000.0           # MW
W_DCC = Q_DCC * 1000.0 / (P_["cp_w"] * (P_["w_out"] - P_["w_in"])) * 3.6        # t/h chilled water
REGEN = P_["regen_frac"] * AIR
Q_REGEN = REGEN / 3.6 * P_["cp_n2"] * (P_["t_regen"] - 25.0) / 1000.0
P_MAC_W, N_MAC = stage_power_MW(AIR, MW_AIR, 25.0, P_["p_mac"] / P_["p_air_in"], P_["eta_air"])
P_O2_W, N_O2 = stage_power_MW(O2, MWO2, 20.0, 50.0 / P_["p_o2_lp"], P_["eta_gas"])
P_N2L_W, N_N2L = stage_power_MW(N2_LOOP, MWN2, 20.0, 40.0 / P_["p_n2_hp"], P_["eta_gas"])
P_N2G_W, N_N2G = stage_power_MW(N2_G, MWN2, 20.0, 58.0 / P_["p_n2_hp"], P_["eta_gas"])
P_SUM = P_MAC_W + P_O2_W + P_N2L_W + P_N2G_W
ASU_REVB_MW = g.ASU_KWH_PER_T_O2 * O2 / 1000.0
V_LOX = O2 * 1000 * P_["lox_h"] / P_["rho_lox"] * 1.1; V_LIN = N2_LOOP * 1000 * P_["lin_h"] / P_["rho_lin"] * 1.1   # t/h x 1000 / (kg/m3)
Q_LOX_V = O2 / 3.6 * (P_["L_o2"] + P_["cp_o2"] * (20.0 + 181.0)) / 1000.0       # MW
Q_LIN_V = N2_LOOP / 3.6 * (P_["L_n2"] + P_["cp_n2"] * (20.0 + 190.0)) / 1000.0
NOTE_AREA20 = dict(AIR=AIR, O2=O2, N2_LOOP=N2_LOOP, N2_G=N2_G, VENT=VENT, S26_REVB=S26_REVB, REFLUX=REFLUX, BOT=BOT, N2_TOP=N2_TOP, Q_DCC=Q_DCC, W_DCC=W_DCC, REGEN=REGEN, Q_REGEN=Q_REGEN,
                   P_MAC=P_MAC_W, P_O2=P_O2_W, P_N2L=P_N2L_W, P_N2G=P_N2G_W, P_SUM=P_SUM, ASU_REVB_MW=ASU_REVB_MW, kWh_t_O2=P_SUM * 1000 / O2, V_LOX=V_LOX, V_LIN=V_LIN, Q_LOX_V=Q_LOX_V, Q_LIN_V=Q_LIN_V)


def gas(i, name, f, T, P, mw): return simple(i, name, "gas", f, T, P, mw=mw)
def liq(i, name, f, T, P, rho): return simple(i, name, "liq", f, T, P, rho=rho)
SAFE = "safe location, atmosphere via silencer (A)"
O2_NOTE = "O2 service (EIGA Doc 13/20 sec 4.2, read): fire needs oxidiser + fuel + ignition; ignition sources include particle impact, adiabatic compression, promoted ignition by organics, friction, arcing. Cleaning to an oxygen-service standard (sec 6.1) and burn-resistant materials where those mechanisms are active; no numeric limit is taken here."


def retime(sh, days_param, hours):
    """sheet_tank computes volume = flow[t/h] x 24 x days / rho x 1.1 with no x1000 (template defect, volumes 1000x too small): the caller passes days x 1000
    so the volume and diameter are right, and the printed 'days' text is rewritten here to the real hours"""
    old = sh.svg
    sh.svg = lambda: old().replace(f"({days_param:g} d, D,A)", f"({hours:g} h, D,A)").replace(f"{days_param:g} days of", f"{hours:g} h of")


def svg_sub(sh, pairs):
    old = sh.svg
    def f():
        s = old()
        for a, b in pairs: s = s.replace(a, b)
        return s
    sh.svg = f


def duct_fix(pkg, sh):
    """lines whose gas size exceeds the largest NPS (48 in) at more than twice the velocity rule are ducts (area = q / rule, D); rewrite the printed line number, NPS and velocity"""
    rows = [r for r in pkg.lines if r[-1] == sh.no and r[9] >= NPS[-1] and float(r[10]) > 2 * RULES["v_gas"]]
    allduct = all(r in rows for r in pkg.lines if r[-1] == sh.no and r[9] >= NPS[-1])
    pairs = []
    for r in rows:
        pairs += [(r[0], r[0].replace('48"', "DUCT", 1)), (f">{r[10]}<", f">{RULES['v_gas']:g}<")]
    if allduct and rows: pairs.append((">48<", ">duct<"))
    svg_sub(sh, pairs)
    return len(rows)


def fix_tank(sh, tag, name, vol, hours, impound):
    return   # Rev C0: the shared tank template now places its labels and bund correctly, nothing to overpaint
    """sheet_tank draws the bund box over the left-hand tank labels (template defect): overpaint and redraw them, and move the box"""
    D = math.sqrt(4 * vol / (math.pi * 20.0))
    R(sh, 146, 326, 150, 140, "#fff", "none", 0); R(sh, 30, 344, 324, 50, "#fff", "none", 0)
    lab(sh, 346, 360, tag, 12, 700, "end"); lab(sh, 346, 374, name, 9.5, 400, "end"); lab(sh, 346, 387, f"{vol:,.0f} m3 gross ({hours:g} h, D,A)  {D:.0f} m dia", 9, 400, "end", GREY)
    R(sh, 150, 430, 190, 74, "none", "#c62828", 1.6, "6 3"); lab(sh, 245, 448, impound, 9.5, 700, "middle", RED); lab(sh, 245, 462, "impounding volume rule: not obtained", 8.5, 400, "middle", GREY)


def fix_label(sh, x, y, w, text):
    """overpaint a template label that is wrong for non-flammable service and write the right one"""
    R(sh, x, y - 10, w, 14, "#fff", "none", 0); lab(sh, x + 4, y, text, 8.5, 400, "start", GREY)


def build(pkg):
    A = "A"; r0 = len(pkg.relief)
    # ---- 201 air intake filter --------------------------------------------------------------------------------------------
    s201 = gas("201", "filtered air to MAC", AIR, 25.0, P_["p_air_in"], MW_AIR); closed("201", [s25.flow], [s201.flow])
    sheet_package(pkg, AREA, 201, "Area 20  Air separation  -  FA-2001 air intake filter house and silencer",
        dict(tag="FA-2001", name="Air intake filter house with silencer", inlets=[(s25, "air", "PG")], outlets=[(s201, "air", "PG")], spec="A1", type="self-cleaning pulse filter house",
             desc=["weather hood, inlet screen, 2-stage filtration", "pulse cleaning with instrument air", "suction silencer", "intake location away from hydrocarbon, NH3 and CO2 sources (A)"],
             utilities=[("pulse air", 0.0, "vendor", A)],
             interlocks=[("PDAH", "filter dP high", "0-20 mbar", "H 10 mbar (A)"), ("AAH", "hydrocarbon in intake air (cold-box safety)", "0-100 % LEL", "alarm; trip ASU on high (A)"), ("TI", "intake air temperature", "-10 to 60 C", "-")],
             op=f"{AIR:,.0f} t/h air, 25 C", size="vendor", hazard="contaminated intake air", basis="A",
             rows=[("Air (stream 25)", f"{AIR:,.1f} t/h", "S Rev B x K"), ("Pressure drop", f"{1.0-P_['p_air_in']:.2f} bar", "A 0.01-0.03"), ("Composition", "O2/N2 only in Rev B", "gap")],
             notes=["Air composition in Rev B is O2 + N2 only; water vapour, CO2 and argon are not in the balance (gap). Their removal is shown qualitatively on sheets 203-204.", "Hydrocarbon analyser on the intake is a safety layer for the cold box (accumulation in liquid O2 is a recognised hazard class; no figure taken here)."]))
    duct_fix(pkg, pkg.sheets[-1])
    # ---- 202 MAC
    s202 = gas("202", "compressed air to DCC", AIR, 40.0, P_["p_mac"], MW_AIR); closed("202", [s201.flow], [s202.flow])
    sheet_compressor(pkg, AREA, 202, "Area 20  Air separation  -  K-2001 main air compressor train",
        dict(tag="K-2001", name="Main air compressor", suction=s201, discharge=s202, power_MW=P_MAC_W, driver="motor", spec="A1", basis="D",
             notes=[f"D: power = N k/(k-1) m Rs T1 (r_s^((k-1)/k) - 1)/eta with N = {N_MAC} stages (max ratio {P_['r_stage_max']} A), k = 1.4 (ideal diatomic), eta {P_['eta_air']} (A 0.75-0.85), ideal intercooling to 25 C: {P_MAC_W:.1f} MW.",
                    f"Bottom-up train power: MAC {P_MAC_W:.1f} + O2 {P_O2_W:.1f} + loop N2 {P_N2L_W:.1f} + gasifier N2 {P_N2G_W:.1f} = {P_SUM:.1f} MW = {P_SUM*1000/O2:.0f} kWh/t O2, against Rev B ASU-101 {ASU_REVB_MW:.1f} MW (275 kWh/t O2, TDA range 250-300, single source). The Rev B figure appears to exclude O2 compression to 50 bar and N2 compression (or to rest on a different configuration); needs reconciling in Rev C.",
                    "Air is compressed to 6 bar abs (A 5-8); discharge T on the template is the aftercooled 40 C. Interstage coolers, condensate drains and inlet guide vanes are vendor items; one aftercooler is drawn."],
             hazard="hot air; surge", mat="A: CS"))
    duct_fix(pkg, pkg.sheets[-1])
    # ---- 203 DCC
    s203 = gas("203", "cooled air to adsorbers", AIR, P_["t_dcc_out"], P_["p_mac"] - 0.3, MW_AIR)
    sw_in = liq("204", "chilled water to DCC", W_DCC, P_["w_in"], 4.0, 999.0); sw_out = liq("205", "water from DCC", W_DCC, P_["w_out"], 1.5, 997.0)
    closed("203", [s202.flow, sw_in.flow], [s203.flow, sw_out.flow])
    sheet_column(pkg, AREA, 203, "Area 20  Air separation  -  C-2001 direct-contact air cooler (packed)",
        dict(tag="C-2001", name="Direct-contact air cooler", feed=s202, top=s203, bottom=sw_out, feed2=sw_in, packing=True, stages=10, spec="A1", hazard="water carry-over",
             notes=[f"D: duty {Q_DCC:.1f} MW = air x cp x (40 - {P_['t_dcc_out']:g} C); chilled water {W_DCC:,.0f} t/h for {P_['w_in']:g}->{P_['w_out']:g} C (A). Condensed water vapour is not in Rev B: gap.",
                    "Chilled water comes from a chiller or evaporative cooler (utilities, not sized). Column diameter comes from the template 2 m/s vapour rule (A), not a packed-tower flooding calculation."]))
    fix_label(pkg.sheets[-1], 60, 103, 190, "PSV to atmosphere, safe location (A)")
    # ---- 204 adsorbers
    s206 = gas("206", "purified air to cold box", AIR, 18.0, P_["p_mac"] - 0.5, MW_AIR)
    s207 = gas("207", "hot regeneration N2", REGEN, P_["t_regen"], P_["p_n2_lp"] + 0.1, MWN2); s208 = gas("208", "regeneration waste N2", REGEN, 60.0, P_["p_n2_lp"], MWN2)
    closed("204a", [s203.flow], [s206.flow]); closed("204b", [s207.flow], [s208.flow])
    sheet_package(pkg, AREA, 204, "Area 20  Air separation  -  AD-2001 A/B molecular-sieve adsorbers (packaged)",
        dict(tag="AD-2001", name="Molecular-sieve adsorbers A/B", inlets=[(s203, "air", "PG"), (s207, "regen N2", "PG")], outlets=[(s206, "air", "PG"), (s208, "regen N2", "PG")], spec="A1",
             type="2 x 100 % switching adsorbers (packaged)", esd=False,
             desc=["one on adsorption, one on regeneration", "removes water, CO2 and some hydrocarbons (vendor)", "switching valves, interlocked", f"regeneration heater {Q_REGEN:.1f} MW (D)"],
             utilities=[("regen heater", Q_REGEN, "MW (D)", "D"), ("switch air", 0.0, "vendor", A)],
             interlocks=[("AAHH", "CO2 / moisture breakthrough in purified air (trip)", "0-10 ppm", "per vendor (gap)"), ("TAH", "regeneration gas temperature high", "0-300 C", f"H {P_['t_regen']+20:.0f} C (A)"), ("PDAH", "bed dP high", "0-0.5 bar", "H 0.3 bar (A)"), ("ZAH", "switching valve position", "-", "interlock (A)")],
             op=f"{AIR:,.0f} t/h air; {REGEN:,.1f} t/h regen N2", size="vendor (bed volume from cycle time: gap)", hazard="breakthrough; hot regen gas", relief="blocked outlet / fire (adsorber)",
             rows=[("Air (203 -> 206)", f"{AIR:,.0f} t/h", "D"), ("Regen N2", f"{REGEN:,.1f} t/h", f"D {P_['regen_frac']*100:.0f} % of air A"), ("Regen heater", f"{Q_REGEN:.1f} MW", "D"), ("Regen T", f"{P_['t_regen']:g} C", "A 150-250"), ("Adsorbate", "not in Rev B", "gap")],
             notes=["Regeneration N2 is taken from the cold-box waste N2 (stream 213) and returns to the vent, so it adds no flow outside Rev B stream 26 (asserted: in = out; the desorbed water and CO2 are not in Rev B).", "Cycle time, bed volume, pressure-swing options and the regeneration schedule are vendor items (gap)."]))
    pkg.relief[-1][5] = SAFE
    # ---- 205 cold box
    s209 = gas("209", "oxygen gas from cold box", O2, 20.0, P_["p_o2_lp"], MWO2)
    s210 = gas("210", "HP N2 product from cold box", N2_PROD, 20.0, P_["p_n2_hp"], MWN2)
    s213 = gas("213", "waste N2 from cold box", VENT, 20.0, P_["p_n2_lp"], MWN2)
    closed("205", [s206.flow], [s209.flow, s210.flow, s213.flow])
    sheet_package(pkg, AREA, 205, "Area 20  Air separation  -  CB-2001 cold box with main heat exchanger (packaged)",
        dict(tag="CB-2001", name="Cold box with main heat exchanger", inlets=[(s206, "air", "PG")], outlets=[(s209, "O2", "PG"), (s210, "N2", "PG"), (s213, "waste N2", "PG")], spec="A1",
             type="cold box (packaged, vendor)", esd=True,
             desc=["brazed-aluminium main heat exchanger (vendor)", "HP and LP columns on sheets 206-207", "perlite insulation, N2-purged casing", "refrigeration: expander or liquid make: vendor"],
             utilities=[("casing N2", 0.0, "vendor", A), ("refrig.", 0.0, "gap", A)],
             interlocks=[("AAH", "O2 purity (product)", "0-100 vol %", "per user spec (gap)"), ("AAH", "hydrocarbon in main-condenser liquid O2", "0-100 ppm", "alarm; drain (A)"), ("PAHH", "cold box casing pressure high", "0-0.1 bar", "relief: rupture disc (A)"), ("TAL", "warm-end product temperature low", "-20 to 40 C", "L 5 C (A)")],
             op=f"{AIR:,.0f} t/h air in", size="vendor", hazard="LOX, hydrocarbons, cryogenic", relief="cold-box casing overpressure (leak of cryogenic liquid)", mat="A: Al / SS (vendor)",
             rows=[("Air in (206)", f"{AIR:,.1f} t/h", "S Rev B"), ("O2 (209 -> stream 2)", f"{O2:,.1f} t/h", "S Rev B x K"), ("HP N2 (210)", f"{N2_PROD:,.1f} t/h", "D"), ("Waste N2 (213)", f"{VENT:,.1f} t/h", "D"), ("Closure", "in = out (asserted)", "D"), ("Refrigeration", "not in Rev B", "gap")],
             notes=[f"Rev B closure 25 = 2 + 14 + 26. Stream 26 ({S26_REVB:,.1f} t/h) is split here into the N2 import of area 10 ({N2_G:,.1f} t/h, stream 233/215) and the vent {VENT:,.1f} t/h (213, then 26 on sheet 216); the sum is unchanged.",
                    "Rev B recovers all the air O2 as product and all N2 as pure N2; real recovery, argon and impure fractions are outside Rev B (gap). Heat-leak and refrigeration (turbine, liquid make) are not in Rev B (no source numbers invented).", O2_NOTE]))
    pkg.relief[-1][5] = "safe location, atmosphere (casing rupture disc, A)"
    duct_fix(pkg, pkg.sheets[-1])
    # ---- 206 HP column
    s219 = simple("219", "air feed to HP column (part liquid)", "twophase", AIR, -176.0, P_["p_hp"], mw=MW_AIR)
    s220 = gas("220", "HP column top N2", N2_TOP, -178.0, P_["p_hp"] - 0.1, MWN2)
    s221 = liq("221", "crude oxygen liquid (HP sump)", BOT, -175.0, P_["p_hp"], P_["rho_rich"])
    closed("206", [s219.flow], [s220.flow, s221.flow])
    sheet_column(pkg, AREA, 206, "Area 20  Air separation  -  C-2002 high-pressure column",
        dict(tag="C-2002", name="HP column (in cold box)", feed=s219, top=s220, bottom=s221, packing=False, stages=40, spec="A1", hazard="cryogenic liquid; O2 enrichment",
             notes=[f"D: crude liquid at {P_['x_b']*100:.0f} mol % O2 (A 30-40 %) holds all the air O2 ({O2:,.1f} t/h) and {N2_BOT:,.1f} t/h N2; the top is {N2_TOP:,.1f} t/h pure N2 (Rev B has only O2 and N2). Top N2 = LP reflux {REFLUX:,.1f} + HP product {N2_PROD:,.1f} t/h (asserted).",
                    "Temperatures and pressures (-176 / -178 / -175 C, 5.5 bar) are screening values (A, +/-5 K), no VLE run; the template sizes the diameter at 2 m/s vapour velocity and uses a steam reboiler slot that is not used: the main condenser-reboiler (HP top condenses against LP sump) is inside the cold box and is not drawn by this template (defect)."]))
    fix_label(pkg.sheets[-1], 60, 103, 190, "PSV to atmosphere, safe location (A)")
    # ---- 207 LP column
    s222 = liq("222", "crude oxygen after expansion", BOT, -190.0, P_["p_lp"] + 0.1, P_["rho_rich"])
    s223 = liq("223", "LIN reflux from HP top", REFLUX, -194.0, P_["p_lp"] + 0.1, P_["rho_lin"])
    s224 = gas("224", "LP column top waste N2", VENT, -193.0, P_["p_lp"] - 0.1, MWN2)
    s225 = liq("225", "liquid oxygen (LP sump)", O2, -181.0, P_["p_lp"], P_["rho_lox"])
    closed("207", [s222.flow, s223.flow], [s224.flow, s225.flow])
    sheet_column(pkg, AREA, 207, "Area 20  Air separation  -  C-2003 low-pressure column",
        dict(tag="C-2003", name="LP column (in cold box)", feed=s222, top=s224, bottom=s225, feed2=s223, packing=True, stages=60, spec="A1", hazard="LOX sump; cryogenic liquid",
             notes=[f"D from closure: reflux {REFLUX:,.1f} t/h = waste N2 {VENT:,.1f} - N2 in crude {N2_BOT:,.1f}. Sump liquid = all product O2 ({O2:,.1f} t/h) which is boiled in the main condenser and warmed in the main heat exchanger to stream 209.",
                    "Hydrocarbon build-up in the LOX sump is the classical ASU hazard: continuous liquid purge and analyser are in the vendor package (not drawn); structured packing is assumed (A). Temperatures are screening values (A)."]))
    fix_label(pkg.sheets[-1], 60, 103, 190, "PSV to atmosphere, safe location (A)")
    # ---- 208 LOX tank (+ pumps)
    sfill = liq("226", "LOX fill (intermittent)", O2 * P_["lox_h"] / P_["refill_lox_h"], -181.0, 1.5, P_["rho_lox"])
    slox = liq("227", "LOX to pumps / vaporiser", O2, -183.0, 1.2, P_["rho_lox"])
    sheet_tank(pkg, AREA, 208, "Area 20  Air separation  -  T-2001 liquid oxygen backup storage and LOX pumps",
        dict(tag="T-2001", name="LOX storage tank (vacuum-insulated)", inflow=sfill, outflow=slox, days=P_["lox_h"] / 24.0, roof="dome", spec="A1", refrigerated=True, pumps="P-2001", pump_dp=48.5, mat="A: SS inner, CS outer",
             vent_dest="safe location, atmosphere via vent stack, no flame arrestor on O2 (A)",
             notes=[f"D: backup {P_['lox_h']:g} h at full O2 flow (A 1-8 h) = {V_LOX:,.0f} m3 gross; refill {P_['refill_lox_h']:g} h from the LP sump (A), fill is an intermittent stream outside the steady Rev B balance.",
                    "Template defects fixed locally in the registers: TI range (cryogenic) and vent destination (no flame arrestor in O2). LOX tank spacing, bund/impounding volume and combustible-material exclusion distances need a standard that was not fetched (gap).", O2_NOTE],
             hazard="cryogenic LOX; O2 enrichment"))
    retime(pkg.sheets[-1], P_["lox_h"] / 24.0, P_["lox_h"])
    svg_sub(pkg.sheets[-1], [("-50 to 60 C", "-200 to 40 C")]); fix_tank(pkg.sheets[-1], "T-2001", "LOX storage tank", V_LOX, P_["lox_h"], "impounding (A)")
    # ---- 209 LOX vaporiser
    s228 = liq("228", "LOX pumped to vaporiser", O2, -178.0, 50.0, P_["rho_lox"]); s229 = gas("229", "O2 gas to header (standby)", O2, 20.0, 49.0, MWO2)
    hw = Q_LOX_V * 1000 / (P_["cp_w"] * (P_["t_hw_in"] - P_["t_hw_out"])) * 3.6
    h1 = liq("230", "hot water to LOX vaporiser", hw, P_["t_hw_in"], 4.0, 972.0); h2 = liq("231", "hot water return", hw, P_["t_hw_out"], 3.0, 988.0)
    sheet_hx(pkg, AREA, 209, "Area 20  Air separation  -  E-2005 LOX vaporiser (standby O2 supply)",
        dict(tag="E-2005", name="LOX vaporiser", hot_in=h1, hot_out=h2, cold_in=s228, cold_out=s229, duty_MW=Q_LOX_V, kind="gas_liq", spec="A1", spec_c="A1", svc_c="PL",
             relief_dest=SAFE, hazard="LOX release; O2-rich vent", mat="A: SS (O2 service, cleaned)",
             notes=[f"D: duty = O2 x (L {P_['L_o2']:g} kJ/kg + cp {P_['cp_o2']} x 201 K) = {Q_LOX_V:.1f} MW (textbook L and cp typed here: A). Hot water {hw:,.0f} t/h for {P_['t_hw_in']:g}->{P_['t_hw_out']:g} C (A).",
                    "Standby only: runs when K-2002 or the cold box trips, to hold O2 to R-101 for a controlled shutdown (A). The template labels the water side 'tube' and the cryogenic side 'shell' by its fixed layout; real arrangement is vendor.", O2_NOTE]))
    # ---- 210 LIN tank
    sfin = liq("239", "LIN fill (intermittent)", N2_LOOP * P_["lin_h"] / P_["refill_lin_h"], -194.0, 1.5, P_["rho_lin"])
    slin = liq("234", "LIN to pumps / vaporiser", N2_LOOP, -194.0, 1.2, P_["rho_lin"])
    sheet_tank(pkg, AREA, 210, "Area 20  Air separation  -  T-2002 liquid nitrogen backup storage and LIN pumps",
        dict(tag="T-2002", name="LIN storage tank (vacuum-insulated)", inflow=sfin, outflow=slin, days=P_["lin_h"] / 24.0, roof="dome", spec="A1", refrigerated=True, pumps="P-2002", pump_dp=38.5, mat="A: SS inner, CS outer",
             vent_dest="safe location, atmosphere via vent stack (asphyxiant: not near occupied areas) (A)",
             notes=[f"D: backup {P_['lin_h']:g} h at the ammonia-loop N2 flow ({N2_LOOP:,.1f} t/h) = {V_LIN:,.0f} m3 gross (A 1-4 h); refill {P_['refill_lin_h']:g} h (A). Also the source for purging and start-up inerting of areas 10 and 40 (not sized).",
                    "N2 asphyxiation: vents and relief outlets discharge to a safe location and oxygen-deficiency detection is required around the tank and vaporiser (A)."],
             hazard="cryogenic LIN; asphyxiation"))
    retime(pkg.sheets[-1], P_["lin_h"] / 24.0, P_["lin_h"])
    svg_sub(pkg.sheets[-1], [("-50 to 60 C", "-200 to 40 C")]); fix_tank(pkg.sheets[-1], "T-2002", "LIN storage tank", V_LIN, P_["lin_h"], "impounding (A)")
    # ---- 211 LIN vaporiser
    s235 = liq("235", "LIN pumped to vaporiser", N2_LOOP, -190.0, 40.0, P_["rho_lin"]); s236 = gas("236", "N2 gas to header (standby)", N2_LOOP, 20.0, 39.0, MWN2)
    hn = Q_LIN_V * 1000 / (P_["cp_w"] * (P_["t_hw_in"] - P_["t_hw_out"])) * 3.6
    h3 = liq("237", "hot water to LIN vaporiser", hn, P_["t_hw_in"], 4.0, 972.0); h4 = liq("238", "hot water return", hn, P_["t_hw_out"], 3.0, 988.0)
    sheet_hx(pkg, AREA, 211, "Area 20  Air separation  -  E-2006 LIN vaporiser (standby N2 to the loop)",
        dict(tag="E-2006", name="LIN vaporiser", hot_in=h3, hot_out=h4, cold_in=s235, cold_out=s236, duty_MW=Q_LIN_V, kind="gas_liq", spec="A1", spec_c="A1", svc_c="PL",
             relief_dest=SAFE, hazard="cryogenic LIN; asphyxiant release", mat="A: SS",
             notes=[f"D: duty = N2 x (L {P_['L_n2']:g} kJ/kg + cp {P_['cp_n2']} x 210 K) = {Q_LIN_V:.1f} MW (textbook values typed: A); at 40 bar N2 is above its critical pressure, so the latent-heat term is a screening stand-in for the pseudo-boiling enthalpy rise.",
                    "Standby only: holds N2 to K-401 (stream 14) when the cold box or K-2003 is out."]))
    # ---- 212 O2 compressor
    s_c2 = gas("209", "oxygen gas from cold box", O2, 20.0, P_["p_o2_lp"], MWO2)
    sheet_compressor(pkg, AREA, 212, "Area 20  Air separation  -  K-2002 oxygen compressor (O2 service)",
        dict(tag="K-2002", name="Oxygen compressor", suction=s_c2, discharge=s2, power_MW=P_O2_W, driver="motor", spec="O2", basis="D",
             notes=[f"D: {N_O2} stages, eta {P_['eta_gas']} (A), intercooled to 20 C: {P_O2_W:.1f} MW. O2 is 100 % pure in Rev B (stream 2).", O2_NOTE,
                    "Compressor-specific rules (EIGA Doc 10 reciprocating and Doc 27 centrifugal are cited in Doc 13/20 sec 6; not read): casing, seals, lubrication, intercooler and aftercooler materials and the anti-surge arrangement are vendor items for O2. No numbers taken.",
                    "Template defects handled here: the relief destination is set to a safe-location vent (never flare for O2); the suction KO drum is the template default and a cold GOX stream may not need one (vendor)."],
             hazard="O2 compressor fire", mat="A: O2-cleaned, burn-resistant where required (EIGA 13/20 4.4)"))
    pkg.relief[-1][5] = "safe location, atmosphere via silencer; never to flare (O2)"
    # ---- 213 N2 compressor (loop)
    s232n = gas("232", "N2 to K-2003 suction", N2_LOOP, 20.0, P_["p_n2_hp"], MWN2)
    sheet_compressor(pkg, AREA, 213, "Area 20  Air separation  -  K-2003 nitrogen compressor (to ammonia loop, stream 14)",
        dict(tag="K-2003", name="Nitrogen compressor (loop N2)", suction=s232n, discharge=s14, power_MW=P_N2L_W, driver="motor", spec="A1", basis="D",
             notes=[f"D: {N_N2L} stages from {P_['p_n2_hp']:g} to 40 bar, eta {P_['eta_gas']} (A), intercooled: {P_N2L_W:.1f} MW. Stream 14 (Rev B) is the discharge: {N2_LOOP:,.1f} t/h, 40 C, 40 bar; K-401 then takes it to 200 bar (area 40).",
                    "N2 is drawn from the HP column top, avoiding a 1 bar suction; surplus N2 stays at LP. Anti-surge and KO drum are template defaults."], hazard="high-pressure N2 (asphyxiant)", mat="A: CS"))
    pkg.relief[-1][5] = SAFE
    # ---- 214 N2 compressor (gasifier users)
    s233 = gas("233", "HP N2 to K-2004 suction", N2_G, 20.0, P_["p_n2_hp"], MWN2)
    s215 = gas("215", "HP N2 to area 10 users", N2_G, 40.0, 58.0, MWN2)
    closed("210", [s232n.flow, s233.flow], [s210.flow])
    sheet_compressor(pkg, AREA, 214, "Area 20  Air separation  -  K-2004 HP nitrogen compressor (to coal feeding)",
        dict(tag="K-2004", name="Nitrogen compressor (coal feeding N2)", suction=s233, discharge=s215, power_MW=P_N2G_W, driver="motor", spec="A1", basis="D",
             notes=[f"Demand from area 10 (urea_area_10): lock hopper net N2 {a10.N2_LH:,.1f} + dense-phase conveying {a10.N2_CONV:,.1f} = {N2_G:,.1f} t/h at 58 bar (feed vessel 55 bar + 3 bar header drop, A). D: {N_N2G} stages, eta {P_['eta_gas']} (A): {P_N2G_W:.1f} MW.",
                    "Single compressor drawn; spare and N2 buffer volume for a trip of the compressor (HSG103 para 29 asks for a reliable inert supply with reserve) are not sized (gap). The LIN vaporiser can back this duty only at its own flow."],
             hazard="HP N2; loss of inert supply", mat="A: CS"))
    pkg.relief[-1][5] = SAFE
    # ---- 215 O2 header
    s2a = gas("2", "oxygen to R-101", O2, 40.0, 50.0, MWO2); s2b = gas("2", "oxygen to R-101 (standby path)", O2, 40.0, 50.0, MWO2)
    sheet_package(pkg, AREA, 215, "Area 20  Air separation  -  HD-2001 oxygen header to R-101 users",
        dict(tag="HD-2001", name="O2 header with filter, vent and ESD", inlets=[(s2, "O2 from K-2002", "PG"), (s229, "standby from E-2005", "PG")], outlets=[(s2a, "O2 to R-101 (FIC-102)", "PG")], spec="O2",
             type="oxygen header and battery-limit valves", esd=True, relief="blocked outlet (header)",
             desc=["particle filter (burn-resistant, cleaned)", "PIC pressure control to R-101", "silencer vent (safe location)", "N2 purge connection, inerting before maintenance", "AT-103 O2 analyser (Rev B sheet 1)"],
             utilities=[("N2 purge", 0.0, "intermittent", A)],
             interlocks=[("PAL", "O2 header pressure low (alarm, standby start)", "0-70 bar", f"L 45 bar (A)"), ("PAHH", "O2 header pressure high-high", "0-70 bar", "HH 55 bar (A)"), ("AAL", "O2 purity low (to R-101 trip)", "0-100 vol %", "per licensor (gap)"), ("TAHH", "O2 temperature high", "0-100 C", "HH 60 C (A)")],
             op=f"{O2:,.1f} t/h O2 at 50 bar", size="vendor / O2 line spec", hazard="O2 header fire", basis="A",
             rows=[("O2 (stream 2)", f"{O2:,.1f} t/h", "S Rev B x K"), ("Standby", f"E-2005, {O2:,.1f} t/h", "A (not additive)"), ("Line velocity", "generic rule only", "gap"), ("Material", "O2-cleaned", "A")],
             notes=[O2_NOTE, "The line-list velocity is the generic 25 m/s gas rule of pid_unit.RULES and is NOT an oxygen design velocity: EIGA Doc 13/20 sec 4.4 requires the velocity to stay under the impingement curve (Figure 2) for the metal and pressure (and sec 4.4.3, Figure 3 for non-impingement sites). The curve values were not extracted; line sizes on O2 sheets must be redone from them (gap).",
                    "Inlets are alternative sources (K-2002 or E-2005), not additive; the Rev B sheet 1 has FIC-102, XV-101 and AT-103 at the R-101 end. Header volume as buffer against compressor trip is not sized."]))
    pkg.relief[-1][5] = "safe location, atmosphere via silencer; never to flare (O2)"
    # ---- 216 N2 and vent header
    s14b = gas("14", "N2 to K-401 (loop)", N2_LOOP, 40.0, 40.0, MWN2); s215b = gas("215", "HP N2 to area 10 users", N2_G, 40.0, 58.0, MWN2)
    s26 = gas("26", "surplus N2 to vent, after area 10 import", VENT, 25.0, P_["p_n2_lp"], MWN2)
    closed("216", [s14.flow, s215.flow, s213.flow], [s14b.flow, s215b.flow, s26.flow])
    sheet_package(pkg, AREA, 216, "Area 20  Air separation  -  HD-2002 nitrogen headers and waste-N2 vent",
        dict(tag="HD-2002", name="N2 headers to users and waste-N2 vent stack", inlets=[(s14, "N2 from K-2003", "PG"), (s215, "HP N2 from K-2004", "PG"), (s213, "waste N2", "PG")],
             outlets=[(s14b, "N2 to K-401 (area 40)", "PG"), (s215b, "N2 to area 10 (116, 118)", "PG"), (s26, "N2 to vent stack", "PG")], spec="A1",
             type="N2 headers, battery-limit valves and vent stack", esd=True,
             desc=["isolation at each battery limit", "regeneration N2 returns here (stream 208)", "silencer on vent stack", "oxygen-deficiency detectors at vents"],
             utilities=[("backup N2", 0.0, "E-2006", A)],
             interlocks=[("PAL", "N2 header 40 bar pressure low (start LIN backup)", "0-60 bar", "L 36 bar (A)"), ("PAL", "N2 header 58 bar pressure low (area 10 alarm)", "0-80 bar", "L 53 bar (A)"), ("AAL", "O2 deficiency at vent stack area", "0-21 vol %", "alarm (A)"), ("FI", "vent flow", "0-400 t/h", "-")],
             op=f"{N2_LOOP:,.0f} + {N2_G:,.0f} t/h to users; {VENT:,.0f} t/h vent", size="vendor", hazard="N2 asphyxiant at vents", basis="A", relief="blocked outlet (N2 header)",
             rows=[("N2 to K-401 (14)", f"{N2_LOOP:,.1f} t/h", "S Rev B x K"), ("N2 to area 10 (215)", f"{N2_G:,.1f} t/h", "D area 10"), ("Vent (26)", f"{VENT:,.1f} t/h", "D"), ("Rev B stream 26", f"{S26_REVB:,.1f} t/h", "S"), ("Closure", "in = out (asserted)", "D")],
             notes=[f"Stream 26 here is Rev B surplus N2 ({S26_REVB:,.1f} t/h) minus the area-10 import ({N2_G:,.1f} t/h) = {VENT:,.1f} t/h (D); Rev B sheet 1 should be revised to show the import (Rev C item).", "HSG103 para 28: inert gas can accumulate in a workroom and cause asphyxiation in extreme cases; applied here to vents and low spots (general advice, HSE HSG103 fetched)."]))
    pkg.relief[-1][5] = SAFE
    duct_fix(pkg, pkg.sheets[-1])
    for sh in pkg.sheets:
        if sh.no in (201, 204, 205, 215, 216): svg_sub(sh, [(">0.0 ", ">")])
    # patch destinations: air / N2 / O2 services never go to flare
    for r in pkg.relief[r0:]:
        if r[5] in ("flare header", "flare / safe location (A)"): r[5] = SAFE
    return pkg


def lint(pkg):
    tags = [r[0] for r in pkg.equip]; dup = {t for t in tags if tags.count(t) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    assert all(r[5] for r in pkg.relief), "relief row without destination"
    assert all("flare" not in r[5].lower() or "never" in r[5].lower() for r in pkg.relief), "cryogenic/air service relief to flare"
    esd = {r[-1] for r in pkg.valves if "ESD" in str(r[5])}
    need = [sh.no for sh in pkg.sheets if sh.no in (205, 212, 213, 214, 215, 216) and sh.no not in esd]
    assert not need, f"no ESD valve on {need}"
    print("lint ok:", len(pkg.sheets), "sheets;", len(pkg.equip), "equipment rows;", len(pkg.relief), "relief rows;", len(pkg.lines), "lines")


if __name__ == "__main__":
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID", "Rev B balance scaled K=%.4f" % K)
    build(pkg); pkg.total = len(pkg.sheets)
    write_html(pkg.sheets, "/tmp/area20.html", "Area 20 air separation", previews=True)
    lint(pkg)
    for k, v in NOTE_AREA20.items(): print(f"{k:12s} {v:,.3f}")

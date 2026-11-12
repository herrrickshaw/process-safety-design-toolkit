#!/usr/bin/env python3
"""Area 10: coal and petcoke handling and preparation (unit-by-unit P&ID sheets 101-113), coal-to-urea package.

Usage: python3 scripts/urea_area_10.py     (builds /tmp/area10.html + per-sheet previews, runs the lint)

Mass basis: Rev B stream 1 (coal + petcoke blend to F-101, scaled to 3,850 t/d urea by K, urea_basis). Ash and moisture from gen_pid_urea.COAL.
Petcoke share of the blend: A 25 % (VENDOR_REFERENCE.md, Air Products / NETL materials "blended with pet-coke up to 25 %"; the Talcher PFR, quoted in
UREA_VALIDATION.md, gives 38.5 / (106.2 + 38.5) = 26.6 %).  Every other parameter is a screening assumption (A) listed in PAR with its range.
Safety statements cite only documents fetched and read for this area: HSE HSG103 (2nd ed. 2003) and EIGA Doc 13/20 (see AREA_10_NOTES.md).
"""
import sys, os, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from urea_basis import *
from pid_unit import *
from pid_unit2 import *

AREA = "10"
# ---- screening parameters (all tag A unless noted): name -> (value, range, meaning) -------------------------------------
PAR = dict(
    pet_frac=(0.25, "0.20-0.30", "petcoke mass share of the blend (VENDOR_REFERENCE: up to 25 %; PFR 26.6 %)"),
    rho_coal=(800.0, "700-900", "coal bulk density kg/m3"), rho_pet=(750.0, "650-850", "petcoke bulk density kg/m3"),
    pc_moist=(0.02, "0.01-0.05", "pulverised-coal moisture at mill outlet, mass fraction"),
    pc_rho_bulk=(500.0, "400-600", "pulverised coal bulk density kg/m3"),
    t_pc_out=(80.0, "70-95", "mill outlet gas / PC temperature C"), t_gas_in=(250.0, "200-300", "hot inert gas to mill, C"),
    cp_solid=(1.2, "1.0-1.4", "dry coal specific heat kJ/kg/K"), cp_gas=(1.05, "1.0-1.1", "inert gas specific heat kJ/kg/K"),
    cp_w=(4.18, "4.1-4.2", "liquid water specific heat kJ/kg/K"), hfg=(2260.0, "2250-2270", "latent heat of water kJ/kg (textbook value typed here; replace by a property run)"),
    mill_loss=(0.05, "0.03-0.10", "mill and duct heat loss, fraction of duty"),
    store_days_coal=(15.0, "7-30", "coal stockyard live storage, days"), store_days_pet=(10.0, "5-20", "petcoke storage, days"),
    belt_factor=(1.5, "1.2-2.0", "conveyor rating over average flow"),
    bunker_min=(30.0, "15-60", "mill feed bunker residence, min"), bin_min=(45.0, "30-90", "PC storage bin residence, min"),
    fill=(0.85, "0.75-0.90", "bin working fill fraction"), lh_fill=(0.8, "0.7-0.9", "lock hopper fill fraction"),
    n_lh=(4, "3-6", "lock hoppers in staggered duty"), lh_cycle_min=(30.0, "15-60", "lock hopper cycle time, min"),
    p_fv=(55.0, "50-60", "feed vessel / lock hopper top pressure, bar abs (gasifier 45 bar + burner and line drop)"),
    t_fv=(60.0, "40-80", "feed vessel gas temperature C"), eq_recovery=(0.6, "0.4-0.7", "gas recovered by pressure equalisation between lock hoppers"),
    rho_dense=(350.0, "250-450", "dense-phase mixture density kg/m3 (must stay below bulk density)"), rho_part=(1500.0, "1300-1800", "PC particle density kg/m3"),
    v_dense=(6.0, "3-8", "dense-phase line velocity m/s"), n_burner=(4, "2-6", "burner feed lines (licensor sets the count)"),
    inert_changes=(2.0, "1-4", "inerting purge changes per hour of ullage"), inert_extra=(1.1, "1.0-1.3", "allowance for filter and ducts on bin ullage"),
    purge_seal=(0.05, "0.02-0.10", "instrument and seal purge N2, t/h"), o2_limit=(8.0, "from dust tests", "placeholder O2 alarm limit vol % until explosibility tests set it (HSG103 para 25)"),
)
P_ = {k: v[0] for k, v in PAR.items()}
R_MOL = R_GAS


def closed(name, ins, outs, tol=1e-6):
    a, b = sum(ins), sum(outs)
    assert abs(a - b) <= tol * max(a, b, 1.0), f"mass closure {name}: in {a:.4f} out {b:.4f}"


def rho_gas(Pbar, TC, mw): return Pbar * 1e5 * mw / 1000.0 / (R_MOL * (TC + 273.15))


# ---- the area balance (D from Rev B stream 1 and the parameters above) ---------------------------------------------------
BLEND = g.M[1] * 3.6 * K                                  # t/h, Rev B stream 1 scaled
MOIST, ASH = g.COAL["moisture"], g.COAL["ash"]
PET = P_["pet_frac"] * BLEND; COAL = BLEND - PET           # D
DRY = BLEND * (1 - MOIST)                                  # D dry solids (ash + organic)
PC = DRY / (1 - P_["pc_moist"])                            # D pulverised coal at mill outlet
EVAP = BLEND - PC                                          # D water evaporated in the mill
Q_EVAP = EVAP / 3.6 * (P_["hfg"] + P_["cp_w"] * (P_["t_pc_out"] - 25.0)) / 1000.0     # MW
Q_SOL = PC / 3.6 * P_["cp_solid"] * (P_["t_pc_out"] - 25.0) / 1000.0                     # MW
Q_MILL = (Q_EVAP + Q_SOL) * (1 + P_["mill_loss"])                                         # MW
G_HOT = Q_MILL * 1000.0 / (P_["cp_gas"] * (P_["t_gas_in"] - P_["t_pc_out"])) * 3.6      # t/h hot inert gas, D (once-through, no recycle credit)
G_OUT = G_HOT + EVAP                                       # t/h mill gas out (gas + evaporated water)
# lock hoppers
RHO_N2_FV = rho_gas(P_["p_fv"], P_["t_fv"], 28.013)
BATCH_H = P_["n_lh"] * 60.0 / P_["lh_cycle_min"]           # batches per hour, all hoppers
BATCH_T = PC / BATCH_H                                      # t per batch
V_LH = BATCH_T * 1000.0 / (P_["pc_rho_bulk"] * P_["lh_fill"])   # m3 per hopper
N2_LH = V_LH * RHO_N2_FV * (1 - P_["eq_recovery"]) * BATCH_H / 1000.0   # t/h net HP N2 (= vent to filter)
# dense phase
PHI = (P_["rho_dense"] - RHO_N2_FV) / (P_["rho_part"] - RHO_N2_FV)      # solids volume fraction
LOAD = PHI * P_["rho_part"] / ((1 - PHI) * RHO_N2_FV)                   # kg solid per kg gas
N2_CONV = PC / LOAD                                         # t/h conveying N2
FV_MIX = PC + N2_CONV
# PC bin and inerting
V_BIN = PC * P_["bin_min"] / 60.0 * 1000.0 / (P_["pc_rho_bulk"] * P_["fill"])   # m3
ULLAGE = V_BIN * (1 - P_["fill"])
RHO_N2_LP = rho_gas(1.1, 40.0, 28.013)
N2_INERT_BIN = P_["inert_extra"] * ULLAGE * P_["inert_changes"] * RHO_N2_LP / 1000.0   # t/h
N2_INERT = N2_INERT_BIN + P_["purge_seal"]
N2_HP_TOTAL = N2_LH + N2_CONV                               # demand on area 20 (K-2004)
NOTE_AREA10 = dict(BLEND=BLEND, COAL=COAL, PET=PET, PC=PC, EVAP=EVAP, Q_MILL=Q_MILL, G_HOT=G_HOT, N2_LH=N2_LH, N2_CONV=N2_CONV, N2_INERT=N2_INERT, LOAD=LOAD, V_LH=V_LH, V_BIN=V_BIN)


def solid(i, name, flow, rho, T=25.0, P=1.0, v=None):
    """new solids stream; chute/duct screening size uses the slurry rule (1.5 m/s) unless v given (A)"""
    st = simple(i, name, "slurry", flow, T, P, rho=rho)
    if v: st.vel_rule = (lambda v=v: v)
    return st


# ---- local solids-handling sheet (sheet_package draws a gate valve on every line, which is wrong for belts and chutes) -----
def sheet_solids(pkg, area, no, title, u):
    """u: tag,name, inlets/outlets [(St, dev_tag, dev_name, esd)], utilities [(name,q,unit,basis)], interlocks [(fn,svc,range,alarm)],
       desc[], vents [(suffix, protects, destination)], psv (bool, pressure vessel), notes, hazard, rows, extra(callable sh,lp)"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    bx, by, bw, bh = 400, 200, 280, 330
    R(s, bx, by, bw, bh, "#eef3fb", INK, 2.4)
    lab(s, bx + bw / 2, by + 22, u["tag"], 14, 700, "middle"); lab(s, bx + bw / 2, by + 40, u["name"], 10, 400, "middle")
    for i, t in enumerate(u.get("desc", [])): lab(s, bx + bw / 2, by + 62 + i * 12.5, t, 8.8, 400, "middle", GREY)
    idx = 0
    def ports(items, side):
        nonlocal idx
        n = len(items)
        step = min(78, (bh - 130) / max(n - 1, 1)) if n > 1 else 0
        y0 = by + 110 if n > 1 else by + 150
        for k, (st, dev, devname, esd) in enumerate(items):
            idx += 1; yy = round(y0 + k * step)
            if side == "in":
                x1, x2 = 50, bx; dx, ex, lx, hx_ = 190, 285, 56, 310
            else:
                x1, x2 = bx + bw, 1090; dx, ex, lx, hx_ = bx + bw + 40, bx + bw + 280, bx + bw + 14, bx + bw + 200
            noln, n_ = reg2(pkg, sh, area, st, u["tag"] if side == "out" else "upstream", "downstream" if side == "out" else u["tag"], u["spec"], st_svc(st))
            pipe(s, [(x1, yy), (x2, yy)])
            R(s, dx - 17, yy - 9, 34, 18, "#fff", INK, 1.6); lab(s, dx, yy + 3.5, dev, 8.5, 700, "middle")
            tg = f"{dev}-{lp}{idx:02d}"; lab(s, dx, yy + 20, tg, 8, 400, "middle", GREY)
            pkg.valves.append([tg, devname, "solids isolation / feeding", noln, n_, "-", sh.no])
            if esd:
                blockv(s, pkg, sh, ex, yy, 0, f"XV-{lp}{idx+50:02d}", noln, n_, "ball", "ESD isolation", act=True)
                pkg.valves[-1][5] = "FC (ESD)"; lab(s, ex, yy - 24, f"XV-{lp}{idx+50:02d}", 8.5, 700, "middle", RED)
            strm(s, (x1 + 30) if side == "in" else (x2 - 30), yy, st.n)
            lab(s, lx, yy - 36, noln, 9, 700); lab(s, lx, yy - 25.5, f"{st.name}", 8.5, 400, "start", GREY)
            lab(s, lx, yy - 15, f"{fm(st.flow)} t/h  {st.T:g} C  {st.P:g} bar", 8.5, 400, "start", GREY)
    ports(u["inlets"], "in"); ports(u["outlets"], "out")
    for i, (nm, q, unit, basis) in enumerate(u.get("utilities", [])):
        xx = bx + 40 + i * 70
        PL(s, [(xx, by + bh + 60), (xx, by + bh)], 1.6, GREEN); arrow(s, xx, by + bh, "u", GREEN, 6)
        lab(s, xx, by + bh + 74, nm, 9, 700, "middle", GREEN); lab(s, xx, by + bh + 86, (f"{q:,.1f} {unit}" if q > 0 else unit), 8.5, 400, "middle", GREY)
    for i, il in enumerate(u.get("interlocks", [])):
        bub(s, pkg, sh, 60 + i * 52, 650, il[0], f"{lp}{60+i}", u["tag"], il[1], il[2], il[3], panel=True)
    for i, (suf, prot, dest) in enumerate(u.get("vents", [])):
        vx = bx + 30 + i * 85; tg = f"EV-{lp}{suf}"
        R(s, vx, by - 14, 50, 12, "#fff", RED, 1.8); lab(s, vx + 25, by - 18, tg, 8.5, 700, "middle", RED)
        pkg.relief.append([tg, prot, "dust explosion (HSG103 para 60-63)", "per vendor", "A", dest, "not sized: needs volume, Kst/Pmax from 20-L test, vessel strength, opening pressure", sh.no])
    if u.get("psv"):
        psv_at(s, pkg, sh, bx + bw - 30, by - 12 if not u.get("vents") else by - 60, f"PSV-{lp}01", u["tag"], "blocked outlet; gas supply failure", design_conditions(u.get("p_op", u["inlets"][0][0].P), 60)[0],
               u["psv"], "not sized: needs relief load (gas supply capacity)")
    if u.get("extra"): u["extra"](sh, lp)
    eq(pkg, sh, u["tag"], u["name"], u.get("type", "solids handling unit"), u.get("op", "see stream table"), u.get("design", "A: vendor"), u.get("size", "A"), u.get("mat", "A: vendor"), u.get("basis", "A"))
    for e in u.get("eqs", []): eq(pkg, sh, *e)
    hz = u.get("hazard", "see HAZOP"); notes = list(u.get("notes", []))
    if len(hz) > 34: notes.insert(0, "Hazard: " + hz + "."); hz = hz[:31] + "..."
    rows = [("Type", u.get("type", "solids handling")[:34], "A")] + list(u.get("rows", [])) + [("Hazard", hz, "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, notes)


def reg2(pkg, sh, area, st, frm, to, spec, svc):
    """reg_line, but a gas stream whose size exceeds the largest NPS in the series is registered as a duct (area from q / v rule, D)"""
    no, n = reg_line(pkg, sh, area, st, frm, to, spec, svc)
    v = st.velocity(n)
    if n >= NPS[-1] and v > 1.2 * st.vel_rule():
        ar = st.q / st.vel_rule(); no2 = no.replace(f'{n:g}"', "DUCT", 1)
        pkg.lines[-1][0], pkg.lines[-1][9], pkg.lines[-1][10] = no2, f"{ar:.1f} m2", fm(st.vel_rule(), 1)
        return no2, n
    return no, n


def st_svc(st): return "GS" if st.phase == "gas" else "SO"


def build(pkg):
    A = "A"
    n2lp = lambda i, nm, f: simple(i, nm, "gas", f, 40.0, 1.1, mw=28.013)
    # ---- 101 coal receipt ------------------------------------------------------------------------------------------------
    s101 = solid("101", "coal from wagons (as received)", COAL, P_["rho_coal"])
    s102 = solid("102", "coal on receiving belt", COAL, P_["rho_coal"])
    closed("101", [s101.flow], [s102.flow])
    sheet_solids(pkg, AREA, 101, "Area 10  Coal and petcoke handling  -  coal receipt: wagon tippler, hopper, apron feeder",
        dict(tag="TP-1001", name="Wagon tippler, receiving hopper and apron feeder", inlets=[(s101, "TS", "tippler chute gate", False)],
             outlets=[(s102, "AF", "apron feeder", False)], spec="A1", type="rotary wagon tippler + hopper + feeder",
             desc=["tippler dust enclosure with extraction", "hopper with grizzly (oversize)", "apron feeder to receiving belt"],
             utilities=[("dust extract.", 0.0, "vendor", A), ("water spray", 0.0, "vendor", A)],
             interlocks=[("LAH", "hopper level high (stops tippler)", "0-100 %", "H 80 % (A)"), ("SAL", "apron feeder zero-speed", "0-100 %", "alarm; stops tippler (A)"), ("ZAH", "tippler end of travel", "-", "interlock (A)")],
             op=f"{s101.flow:,.1f} t/h average coal; wagon sets: not sized", size="vendor", hazard="coal dust cloud and fire at the tippler; moving plant",
             rows=[("Throughput", f"{COAL:,.1f} t/h average", "D"), ("Coal share", f"{(1-P_['pet_frac'])*100:.0f} % of blend", "A"), ("Rated flow", f"{COAL*P_['belt_factor']:,.0f} t/h", "A x1.5")],
             notes=["Stream 101 is 75 % of Rev B stream 1 (petcoke share 25 % is A, range 20-30 %). Rev B moisture 12.8 % and ash 35 % apply to the blend.", "Wagon sets, unloading rate and railway siding are not sized (receipt logistics are not in Rev B).",
                    "NPS column for solids lines is a chute duct screening size from the 1.5 m/s slurry rule (A); chutes and belts are sized by the vendor."]))
    # ---- 102 receiving belt
    s103 = solid("103", "coal at crusher house", COAL, P_["rho_coal"]); closed("102", [s102.flow], [s103.flow])
    sheet_solids(pkg, AREA, 102, "Area 10  Coal and petcoke handling  -  receiving belt conveyor with tramp-metal removal and sampling",
        dict(tag="BC-1001", name="Receiving belt conveyor", inlets=[(s102, "CH", "chute", False)], outlets=[(s103, "CH", "chute", False)], spec="A1", type="belt conveyor (enclosed)",
             desc=["magnetic separator, metal detector", "belt weigher, in-line sampler", "pull-cord and belt-sway trips"],
             utilities=[("drive", 0.0, "vendor", A)],
             interlocks=[("SSH", "belt over-speed / slip", "0-100 %", "alarm and stop (A)"), ("WAH", "belt weigher high load", "0-150 %", "H 110 % (A)"), ("TAH", "idler bearing / belt-rub temperature", "0-150 C", "alarm (A)"), ("ZAH", "belt-sway / pull-cord", "-", "trip (A)")],
             op=f"{s102.flow:,.1f} t/h average", size=f"rated {COAL*P_['belt_factor']:,.0f} t/h (D: 1.5 x average, A)", hazard="coal dust; fire in belt gallery from friction or idler failure",
             rows=[("Average flow", f"{COAL:,.1f} t/h", "D"), ("Rating", f"{COAL*P_['belt_factor']:,.0f} t/h", "A x1.5"), ("Tramp metal", "magnet + detector", "A")],
             notes=["HSG103 para 82: dust-handling transfer systems should shut down on a fire or explosion trip (belt trips drawn as A interlocks).", "Belt width, speed and gallery layout are vendor items; not sized."]))
    # ---- 103 crusher
    s104 = solid("104", "crushed coal to stacker", COAL, P_["rho_coal"]); closed("103", [s103.flow], [s104.flow])
    sheet_solids(pkg, AREA, 103, "Area 10  Coal and petcoke handling  -  crusher house: screen and crusher",
        dict(tag="CR-1001", name="Coal screen and crusher", inlets=[(s103, "CH", "chute", False)], outlets=[(s104, "CH", "chute", False)], spec="A1", type="screen + roll/hammer crusher",
             desc=["vibrating screen, oversize to crusher", "crusher feeder with bypass of fines", "dust extraction and bag filter"],
             utilities=[("dust extract.", 0.0, "vendor", A)],
             interlocks=[("JAH", "crusher motor current high (jam)", "0-150 %", "H 110 %, trip 130 % (A)"), ("VAH", "crusher vibration", "per vendor", "per vendor (gap)"), ("TAH", "crusher bearing temperature", "0-150 C", "H 90 C (A)"), ("LAH", "outlet chute blocked", "-", "trip feeder (A)")],
             op=f"{s103.flow:,.1f} t/h", size="vendor; top size set by mill feed spec (gap)", hazard="coal dust; tramp-metal damage; ignition by sparks",
             vents=[("01", "dust collector at crusher house", "to safe place in open air via duct (A)")],
             rows=[("Flow", f"{COAL:,.1f} t/h", "D"), ("Product size", "mill feed spec: gap", "gap"), ("Dust extraction", "bag filter, vent panel", "A")],
             notes=["Crushing is applied to coal only; petcoke is received crushed (A, verify with the supplier specification).", "Explosion vent panel on the dust collector: area is not sized because Kst and Pmax of the coal/petcoke dust are not available (HSG103 para 61 lists the inputs)."]))
    # ---- 104 stockyard
    s105 = solid("105", "coal reclaimed to blending", COAL, P_["rho_coal"]); closed("104", [s104.flow], [s105.flow])
    vol_y = COAL * 24 * P_["store_days_coal"] * 1000.0 / P_["rho_coal"]   # t x 1000 / (kg/m3) = m3
    sheet_solids(pkg, AREA, 104, "Area 10  Coal and petcoke handling  -  coal stockyard: stacker and bucket-wheel reclaimer",
        dict(tag="SY-1001", name="Coal stockyard, stacker and reclaimer", inlets=[(s104, "CH", "chute", False)], outlets=[(s105, "CH", "chute", False)], spec="A1", type="open stockyard + stacker/reclaimer",
             desc=[f"live storage {P_['store_days_coal']:g} d (A) = {COAL*24*P_['store_days_coal']/1000:,.1f} kt", f"volume {vol_y:,.0f} m3 (D, bulk {P_['rho_coal']:g} kg/m3 A)", "water sprinklers, compaction, temperature probes"],
             utilities=[("sprinklers", 0.0, "vendor", A)],
             interlocks=[("TAH", "stockpile core temperature", "0-150 C", "alarm (A)"), ("SAL", "reclaimer drive trip", "-", "trip (A)"), ("AAH", "CO in stacker/reclaimer cabin", "0-100 ppm", "A")],
             op=f"{s104.flow:,.1f} t/h in = {s105.flow:,.1f} t/h out (steady state)", size=f"{COAL*24*P_['store_days_coal']/1000:,.1f} kt live (D)", hazard="spontaneous heating of coal piles; coal dust; fire",
             rows=[("Live storage", f"{P_['store_days_coal']:g} d  ({P_['store_days_coal']*COAL*24/1000:,.0f} kt)", "A range 7-30"), ("Stockpile volume", f"{vol_y:,.0f} m3", "D"), ("Closure", "stack = reclaim", "D")],
             notes=["Steady-state mass closure stack = reclaim; stock build and draw are not modelled.", "HSG103 para 50 recommends periodic temperature checks in the interior of large stored piles of self-heating materials; the TAH probe follows that general advice (self-heating tendency of this coal is not known: gap).",
                    "Fire fighting: HSG103 para 92 says water should not be used on fires in coal dust (violent reaction / flammable gases); stockpile sprinklers are for dust suppression and cooling only, to be confirmed with the fire-safety study."]))
    # ---- 105 petcoke storage
    s106 = solid("106", "petcoke from trucks / wagons", PET, P_["rho_pet"]); s107 = solid("107", "petcoke reclaimed to blending", PET, P_["rho_pet"]); closed("105", [s106.flow], [s107.flow])
    sheet_solids(pkg, AREA, 105, "Area 10  Coal and petcoke handling  -  petcoke receipt, covered store and reclaim",
        dict(tag="PS-1001", name="Petcoke covered store and reclaim feeder", inlets=[(s106, "TS", "unloading hopper gate", False)], outlets=[(s107, "WF", "weigh feeder", False)], spec="A1", type="covered store + hopper + weigh feeder",
             desc=[f"storage {P_['store_days_pet']:g} d (A) = {PET*24*P_['store_days_pet']/1000:,.1f} kt", "enclosed, dust extraction", "reclaim by loader to hopper (A)"],
             utilities=[("dust extract.", 0.0, "vendor", A)],
             interlocks=[("LAH", "reclaim hopper level high", "0-100 %", "H 80 % (A)"), ("WIC", "weigh feeder ratio to coal", "0-100 %", "ratio PET : COAL 25 : 75 (A)"), ("AAH", "CO in store", "0-100 ppm", "A")],
             op=f"{s106.flow:,.1f} t/h average", size=f"{PET*24*P_['store_days_pet']/1000:,.1f} kt (D)", hazard="petcoke dust; fines blown off; fire in covered store",
             vents=[("01", "petcoke hopper dust collector", "to safe place in open air via duct (A)")],
             rows=[("Petcoke flow", f"{PET:,.1f} t/h", "D = 25 % x stream 1"), ("Storage", f"{P_['store_days_pet']:g} d", "A range 5-20"), ("Dust", "enclosed + extraction", "A")],
             notes=["Petcoke is blended at 25 % of stream 1 by mass (A); petcoke moisture, ash and volatile content differ from the Indian coal and are NOT modelled (Rev B uses one composition for the blend): gap.",
                    "Petcoke source, sulphur and vanadium content are outside Rev B; storage covered to limit fines loss (A)."]))
    # ---- 106 blending and mill feed bunker
    s1 = stream(1, "coal-petcoke blend to F-101", "slurry", rho=(P_["rho_coal"] * (1 - P_["pet_frac"]) + P_["rho_pet"] * P_["pet_frac"]))
    closed("106", [s105.flow, s107.flow], [s1.flow])
    vbun = BLEND * P_["bunker_min"] / 60.0 * 1000.0 / (s1.rho_in * P_["fill"])
    sheet_solids(pkg, AREA, 106, "Area 10  Coal and petcoke handling  -  blending: weigh feeders and mill feed bunker",
        dict(tag="BN-1001", name="Mill feed bunker with weigh feeders", inlets=[(s105, "WF", "weigh feeder (coal)", False), (s107, "WF", "weigh feeder (petcoke)", False)],
             outlets=[(s1, "WF", "gravimetric feeder to mill", True)], spec="A1", type="bunker (silo) + weigh feeders",
             desc=[f"{P_['bunker_min']:g} min residence (A) = {vbun:,.0f} m3 (D)", "ratio control petcoke : coal", "outlet feeder with ESD gate to F-101"],
             utilities=[("N2 inerting", 0.0, "sheet 113", A)],
             interlocks=[("LAHH", "bunker level high-high (stops belts)", "0-100 %", "HH 95 % (A)"), ("LALL", "bunker level low-low (mill trip)", "0-100 %", "LL 10 % (A)"), ("TAH", "bunker wall temperature (hot spot)", "0-150 C", "alarm (A)"), ("AAH", "CO in bunker", "0-100 ppm", "alarm (A)"), ("WIC", "blend ratio", "0-100 %", "A")],
             op=f"{s1.flow:,.1f} t/h blend = Rev B stream 1", size=f"{vbun:,.0f} m3 (D)", hazard="coal dust cloud on filling; smouldering; CO accumulation (HSG103 para 51)",
             vents=[("01", "bunker top", "to safe place in open air via duct (A)")],
             rows=[("Blend (stream 1)", f"{BLEND:,.1f} t/h", "S Rev B x K"), ("Coal / petcoke", f"{COAL:,.1f} / {PET:,.1f} t/h", "D"), ("Moisture / ash", f"{MOIST*100:.1f} % / {ASH*100:.1f} %", "S COAL"), ("Bunker", f"{vbun:,.0f} m3", "D")],
             notes=["Stream 1 is the Rev B coal feed to F-101, here the sum of 105 and 107 (asserted in code). Composition is the Rev B COAL preset for the whole blend.", "HSG103 para 51: dust smouldering in restricted air can give off CO that explodes when fresh air enters; CO probes in the bunker follow that."]))
    # ---- 107 mill F-101
    s110 = simple("110", "hot inert gas to F-101", "gas", G_HOT, P_["t_gas_in"], 1.1, mw=28.0)
    s108 = simple("108", "mill discharge: PC in gas", "twophase", PC + G_OUT, P_["t_pc_out"], 1.05, rho=rho_gas(1.05, P_["t_pc_out"], 27.0) * 1.0)
    closed("107", [s1.flow, s110.flow], [s108.flow])
    sheet_solids(pkg, AREA, 107, "Area 10  Coal preparation  -  F-101 coal mill: drying and grinding to pulverised coal",
        dict(tag="F-101", name="Coal mill (drying and grinding)", inlets=[(s1, "RV", "rotary feeder / airlock", True), (s110, "DM", "damper", False)],
             outlets=[(s108, "DM", "damper", True)], spec="A1", type="roller (or ball) mill with classifier, inert drying gas",
             desc=[f"dries {MOIST*100:.1f} % to {P_['pc_moist']*100:.0f} % moisture (A)", f"duty {Q_MILL:.1f} MW (D); water out {EVAP:.1f} t/h (D)", "rotating classifier, rejects hopper (pyrites)", "number of mills: vendor (gap)"],
             utilities=[("hot gas duty", Q_MILL, "MW (D)", "D"), ("seal N2", 0.0, "vendor", A)],
             interlocks=[("TAHH", "mill outlet temperature high-high (trip)", f"0-150 C", f"H {P_['t_pc_out']+10:.0f} / HH {P_['t_pc_out']+20:.0f} C (A)"), ("AAHH", "O2 in mill gas high-high (trip, N2 snuff)", "0-21 vol %", f"H {P_['o2_limit']:g} % placeholder (A)"), ("AAH", "CO in mill outlet gas", "0-1000 ppm", "alarm (A)"), ("PDAH", "mill dP high", "per vendor", "per vendor (gap)"), ("JAH", "mill motor current", "0-150 %", "H 110 % (A)")],
             op=f"{s1.flow:,.1f} t/h in; {PC:,.1f} t/h PC out", size="vendor", hazard="coal dust explosion inside mill; smouldering in mill; CO; hot-gas O2 control",
             vents=[("01", "mill body", "to safe place in open air via duct (A)")],
             rows=[("Feed (stream 1)", f"{BLEND:,.1f} t/h", "S"), ("PC out (108 solids)", f"{PC:,.1f} t/h", "D"), ("Water evaporated", f"{EVAP:,.1f} t/h", "D"), ("Hot gas (110)", f"{G_HOT:,.0f} t/h at {P_['t_gas_in']:g} C", "D"), ("Mill duty", f"{Q_MILL:.1f} MW", "D"), ("Outlet T", f"{P_['t_pc_out']:g} C", "A 70-95")],
             notes=[f"D: duty = (evap x (hfg + cp_w dT) + PC cp dT) x 1.05; hot gas = duty / (cp (T_in - T_out)); hfg {P_['hfg']:g} kJ/kg is a textbook value typed here (A), replace by a property run. Hot gas comes from a hot-gas generator (not in Rev B, not sized).",
                    f"Rev B takes stream 1 into R-101 at 12.8 % moisture. Here the mill dries to {P_['pc_moist']*100:.0f} % (A), so the PC to the burners ({PC:,.1f} t/h) is lower than stream 1 by {EVAP:,.1f} t/h of water. REV C ITEM: gasifier water balance should use the dried PC.",
                    "HSG103 para 25-29: the safe O2 limit under inerting is set by tests and a safety margin; the O2 trip value shown is a placeholder (A) until explosibility tests exist. Mill type, number of mills and grinding energy are vendor items (gap)."]))
    # ---- 108 bag filter and fan
    s109 = solid("109", "pulverised coal to PC bin", PC, P_["pc_rho_bulk"], T=P_["t_pc_out"])
    s111 = simple("111", "clean mill gas to stack", "gas", G_OUT, 70.0, 1.0, mw=26.0)
    closed("108", [s108.flow], [s109.flow, s111.flow])
    sheet_solids(pkg, AREA, 108, "Area 10  Coal preparation  -  BF-101 pulse-jet bag filter and ID fan",
        dict(tag="BF-101", name="PC bag filter with rotary valves and ID fan", inlets=[(s108, "DM", "inlet damper", True)], outlets=[(s109, "RV", "rotary valve", True), (s111, "FN", "ID fan", False)], spec="A1", type="pulse-jet bag filter (inert, pressure-shock resistant)",
             desc=["pulse-jet cleaning with N2", "hoppers with rotary valves (explosion barrier)", "ID fan to stack, dust emission not sized", "antistatic media, earthed (A)"],
             utilities=[("pulse N2", 0.0, "sheet 113", A), ("hopper heat", 0.0, "vendor", A)],
             interlocks=[("PDAH", "filter dP high (blinding)", "0-30 mbar", "H 15 mbar (A)"), ("TAHH", "filter inlet temperature", "0-150 C", f"HH {P_['t_pc_out']+20:.0f} C (A)"), ("AAH", "CO in clean gas (smouldering)", "0-1000 ppm", "alarm (A)"), ("AAHH", "O2 in filter inlet gas", "0-21 vol %", f"H {P_['o2_limit']:g} % placeholder (A)"), ("LAH", "hopper level high", "-", "H (A)")],
             op=f"{s108.flow:,.0f} t/h in", size="vendor", hazard="dust explosion in filter housing; smouldering deposits; CO; pressure-shock",
             vents=[("01", "filter housing", "to safe place in open air via duct or flameless device (A)"), ("02", "hopper", "to safe place in open air (A)")],
             rows=[("Gas in (108)", f"{PC+G_OUT:,.0f} t/h", "D"), ("PC out (109)", f"{PC:,.1f} t/h", "D"), ("Clean gas (111)", f"{G_OUT:,.0f} t/h", "D"), ("Dust to stack", "not sized", "gap")],
             notes=["HSG103 para 81: rotary valves, a material choke or explosion isolation valves are listed as ways to stop an explosion spreading between interconnected units; rotary valves are drawn on the hopper outlets and an isolation valve is on the inlet.", "HSG103 para 63: vents must discharge to a safe place in the open air through a duct (or use flameless venting); a fireball must be expected.",
                    "Stack height, emission limit and fan duty are not sized (no emission figures fetched)."]))
    # ---- 109 PC bin
    s112 = solid("112", "PC to lock hoppers", PC, P_["pc_rho_bulk"], T=P_["t_pc_out"])
    s113 = n2lp("113", "inerting N2 to PC bin", N2_INERT_BIN)
    s114 = n2lp("114", "bin vent gas to BF-101", N2_INERT_BIN)
    closed("109", [s109.flow, s113.flow], [s112.flow, s114.flow])
    sheet_solids(pkg, AREA, 109, "Area 10  Coal preparation  -  V-1001 pulverised coal storage bin",
        dict(tag="V-1001", name="Pulverised coal storage bin (inerted)", inlets=[(s109, "RV", "rotary valve", True), (s113, "XN", "N2 block valve", False)],
             outlets=[(s112, "SG", "slide gate (fluidised outlet)", True), (s114, "XN", "vent valve", False)], spec="A1", type="inerted silo with fluidised cone",
             desc=[f"{P_['bin_min']:g} min residence (A) = {V_BIN:,.0f} m3 (D)", f"fill {P_['fill']*100:.0f} %, ullage {ULLAGE:,.0f} m3", "aeration cone, load cells", "O2 and CO probes in head space"],
             utilities=[("aeration N2", 0.0, "sheet 113", A), ("N2 purge", N2_INERT_BIN, "t/h (D)", "D")],
             interlocks=[("LAHH", "bin level high-high (stops mill)", "0-100 %", "HH 95 % (A)"), ("LALL", "bin level low-low (alarm)", "0-100 %", "LL 15 % (A)"), ("TAH", "bin wall / PC temperature", "0-150 C", f"H {P_['t_pc_out']+20:.0f} C (A)"), ("AAH", "CO in bin head space", "0-1000 ppm", "alarm; N2 flood (A)"), ("AAHH", "O2 in bin head space", "0-21 vol %", f"H {P_['o2_limit']:g} % placeholder (A)")],
             op=f"{PC:,.1f} t/h through", size=f"{V_BIN:,.0f} m3 (D)", hazard="dust explosion; smouldering PC and CO build-up; N2 asphyxiation (HSG103 para 28)",
             vents=[("01", "bin roof", "to safe place in open air via duct (A)"), ("02", "bin roof", "to safe place in open air via duct (A)")],
             rows=[("Residence", f"{P_['bin_min']:g} min  A range 30-90", "A"), ("Volume", f"{V_BIN:,.0f} m3", "D"), ("Inerting N2", f"{N2_INERT_BIN*1000:,.0f} kg/h", "D: 2 changes/h A"), ("O2 limit", f"{P_['o2_limit']:g} % placeholder", "A, tests required")],
             notes=["D: inerting N2 = 1.1 x ullage x 2 changes/h x N2 density at 1.1 bar, 40 C; HSG103 ref 1 gives purge calculations (not read).", "HSG103 para 29: the inert gas supply must be reliable with a reserve sufficient to shut the plant down safely; a LP N2 buffer on sheet 113 is drawn for that.",
                    "HSG103 para 93: an inert atmosphere can be used on deep-seated fires, but removing heat from a large silo may take days or weeks."]))
    # ---- 110 lock hoppers
    s115 = solid("115", "PC to pressurised feed vessel", PC, P_["pc_rho_bulk"], T=P_["t_fv"], P=P_["p_fv"])
    s116 = simple("116", "HP N2 for lock hopper pressurisation (net)", "gas", N2_LH, P_["t_fv"], P_["p_fv"] + 3.0, mw=28.013)
    s117 = simple("117", "lock hopper vent gas to BF-101", "gas", N2_LH, 60.0, 1.1, mw=28.013)
    closed("110", [s112.flow, s116.flow], [s115.flow, s117.flow])
    def ex110(sh, lp):
        lab(sh, 40, 700, f"{P_['n_lh']:g} hoppers in staggered duty (A), each cycle {P_['lh_cycle_min']:g} min: fill, purge, pressurise, discharge, depressurise.", 8.8, 400, "start", GREY)
        lab(sh, 40, 713, f"Pressure equalisation recovers {P_['eq_recovery']*100:.0f} % of the gas to the next hopper (A); net N2 from the HP header = vent to filter.", 8.8, 400, "start", GREY)
    sheet_solids(pkg, AREA, 110, "Area 10  Coal feeding  -  LH-1001 A-D pressurisation lock hoppers",
        dict(tag="LH-1001", name="PC lock hoppers A-D (pressurisation)", inlets=[(s112, "SG", "inlet slide gate (double)", True), (s116, "XN", "N2 pressurisation valve", True)],
             outlets=[(s115, "BV", "discharge ball/isolation valve", True), (s117, "XN", "depressurisation valve", False)], spec="A1", type="pressure vessels (4 off, staggered)",
             desc=[f"{P_['n_lh']:g} x {V_LH:,.0f} m3 (D), batch {BATCH_T:,.1f} t", f"cycle {P_['lh_cycle_min']:g} min, {BATCH_H:g} batches/h (A)", f"design {design_conditions(P_['p_fv'], 60)[0]:g} bar g (D)", "vent through filter to BF-101", "N2 only, never air or O2"],
             utilities=[("HP N2", N2_LH, "t/h net (D)", "D")],
             interlocks=[("PAHH", "lock hopper pressure high-high", f"0-{round_up(design_conditions(P_['p_fv'],60)[0],10):g} bar", f"HH {P_['p_fv']*1.1:.0f} bar (A)"), ("PDAL", "differential to feed vessel (permissive to open)", "0-5 bar", "permissive (A)"), ("LAHH", "hopper level high-high", "0-100 %", "HH 95 % (A)"), ("ZSC", "double-gate closed proof", "-", "interlock (A)"), ("AAH", "O2 after purge", "0-21 vol %", f"H {P_['o2_limit']:g} % placeholder (A)")],
             op=f"{PC:,.1f} t/h PC; N2 {N2_LH:,.1f} t/h net", size=f"{P_['n_lh']:g} x {V_LH:,.0f} m3 (D)", hazard="high-pressure N2 (asphyxiant) and PC; blow-back from gasifier through feed vessel; dust explosion in vent train",
             psv="vent via BF-101 inlet (A)", extra=ex110, p_op=P_["p_fv"],
             rows=[("Hoppers", f"{P_['n_lh']:g} x {V_LH:,.0f} m3", "D"), ("Batch", f"{BATCH_T:,.1f} t", "D"), ("Gas inventory", f"{V_LH*RHO_N2_FV:,.0f} kg per fill", "D ideal gas"), ("Net N2", f"{N2_LH:,.1f} t/h", "D"), ("Recovery", f"{P_['eq_recovery']*100:.0f} %", "A 40-70"), ("Pressure", f"{P_['p_fv']:g} bar abs", "A")],
             notes=[f"D: V = batch / (bulk density x fill); gas per fill = V x N2 density at {P_['p_fv']:g} bar, {P_['t_fv']:g} C; net N2 = gas x (1 - recovery) x batches/h. Interstitial gas carried with PC into the feed vessel is neglected (gap).",
                    "Lock hopper cycle logic, valve types (wear in coal service) and vent filtering are licensor items; the sequence is drawn only as permissives (A).", "Gasifier pressure 45 bar is Rev B; +10 bar margin to feed vessel is A (burner and line drop)."]))
    # ---- 111 feed vessel
    nb = int(P_["n_burner"]); line_flow = FV_MIX / nb
    s118 = simple("118", "HP N2 conveying and aeration gas", "gas", N2_CONV, P_["t_fv"], P_["p_fv"] + 3.0, mw=28.013)
    outs = []
    for k in range(nb):
        st = simple(str(119 + k), f"dense-phase PC + N2 to burner B{k+1}", "twophase", line_flow, P_["t_fv"], P_["p_fv"] - 3.0, rho=P_["rho_dense"]); st.vel_rule = (lambda v=P_["v_dense"]: v)
        outs.append((st, "XN", "burner isolation (fast)", True))
    closed("111", [s115.flow, s118.flow], [o[0].flow for o in outs])
    sheet_solids(pkg, AREA, 111, "Area 10  Coal feeding  -  FV-1001 pressurised feed vessel and dense-phase transport headers",
        dict(tag="FV-1001", name="Pressurised feed vessel with fluidising cone", inlets=[(s115, "BV", "inlet isolation valve", True), (s118, "XN", "N2 supply valve", True)],
             outlets=outs, spec="A1", type="pressure vessel + dense-phase transport",
             desc=[f"{P_['n_burner']:g} burner lines (A; licensor sets the count)", f"mixture density {P_['rho_dense']:g} kg/m3 (A), loading {LOAD:.1f} kg/kg (D)", f"line velocity {P_['v_dense']:g} m/s (A)", "load cells, level radar, aeration pads"],
             utilities=[("HP N2", N2_CONV, "t/h (D)", "D")],
             interlocks=[("LAL", "feed vessel level low (burner trip)", "0-100 %", "L 20 %, LL 10 % trip (A)"), ("PAHH", "feed vessel pressure high-high", f"0-{round_up(design_conditions(P_['p_fv'],60)[0],10):g} bar", f"HH {P_['p_fv']*1.1:.0f} bar (A)"), ("PDAL", "feed vessel to gasifier dP low (flow-back)", "0-10 bar", "L 2 bar, trip (A)"), ("WIC", "PC mass flow to burners", "0-100 %", "per burner (A)")],
             op=f"{PC:,.1f} t/h PC + {N2_CONV:,.1f} t/h N2", size="vendor; volume from storage buffer (gap)", hazard="gasifier back-flow into PC system (oxygen, hot syngas); N2 asphyxiant; dust explosion",
             psv="vent via BF-101 inlet (A)", p_op=P_["p_fv"],
             rows=[("PC in (115)", f"{PC:,.1f} t/h", "D"), ("N2 conveying (118)", f"{N2_CONV:,.1f} t/h", "D"), ("Loading", f"{LOAD:.1f} kg/kg", "D"), ("Per line", f"{line_flow:,.1f} t/h mixture", "D"), ("Pressure", f"{P_['p_fv']:g} bar abs", "A"), ("Particle density", f"{P_['rho_part']:g} kg/m3", "A")],
             notes=[f"D: solids volume fraction = (rho_mix - rho_N2)/(rho_p - rho_N2) with rho_mix {P_['rho_dense']:g} kg/m3 (must stay below the bulk density {P_['pc_rho_bulk']:g}); loading = phi rho_p / ((1-phi) rho_N2); N2 = PC / loading.",
                    "Conveying with N2 (not air, not CO2) is a screening choice (A); CO2 from the AGR would remove the N2 import but adds to the CO2 balance of the urea plant: licensor decision (gap).", "The N2 import is supplied by K-2004 in area 20 (sheet 214); Rev B stream 26 surplus N2 covers it."]))
    # ---- 112 burner feed line (single line, x nb)
    b1 = outs[0][0]
    bpc = simple("123", "PC + N2 to burner B1 (gasifier R-101)", "twophase", line_flow, P_["t_fv"], P_["p_fv"] - 6.0, rho=P_["rho_dense"]); bpc.vel_rule = (lambda v=P_["v_dense"]: v)
    b_n2 = simple("124", "N2 purge to burner line B1", "gas", 0.05, 40.0, P_["p_fv"] + 3.0, mw=28.013)
    b_out = simple("125", "purge gas into burner (during trip)", "gas", 0.05, 40.0, P_["p_fv"] - 6.0, mw=28.013)
    # a purge flows only on trip and start-up; it is an intermittent stream outside the steady-state balance
    sheet_solids(pkg, AREA, 112, "Area 10  Coal feeding  -  burner feed line B1 (typical for B1-B4): flow measurement, fast isolation, N2 purge",
        dict(tag="BL-1001", name="Burner feed line (typical, x%d)" % nb, inlets=[(b1, "XN", "isolation (fast)", True), (b_n2, "XN", "N2 purge valve", False)],
             outlets=[(bpc, "NR", "non-return / flow-back valve", True), (b_out, "XN", "burner purge", False)], spec="A1", type="dense-phase transport line, erosion resistant",
             desc=["mass-flow measurement and control valve", "flow-back protection (non-return + fast valve)", "N2 purge after each trip", "bend and line erosion allowance"],
             utilities=[("purge N2", 0.05, "t/h intermittent (A)", A)],
             interlocks=[("FIC", "PC flow to burner (loop with ratio to O2)", "0-100 %", "H 110 / L 90 % (A)"), ("PDAL", "line dP low (blockage / flow-back)", "0-10 bar", "L (A), trip"), ("BAL", "flame scanner (burner trip from R-101)", "-", "from R-101 BE-101"), ("ZSC", "isolation valve closed proof", "-", "interlock (A)")],
             op=f"{line_flow:,.1f} t/h mixture", size=f"NPS {b1.nps():g} in (D: 6 m/s A)", hazard="flow-back of syngas / oxygen into PC line; erosion; plugged line",
             rows=[("Line flow", f"{line_flow:,.1f} t/h", "D"), ("Lines", f"{nb} (A)", "A"), ("Velocity", f"{P_['v_dense']:g} m/s", "A 3-8"), ("Purge", "0.05 t/h on trip", "A")],
             notes=["The O2 line to the same burner (stream 2, FIC-102, XV-101) is on sheet 1 and area 20 sheet 215: the PC and O2 trips must be one ESD (SIF 2 of the Rev B HAZOP).", "Streams 124/125 are intermittent purges outside the steady-state balance (flow A); the check on this sheet is: flow 123 = flow of line 119 (asserted)."]))
    assert abs(bpc.flow - b1.flow) < 1e-9
    # ---- 113 dust and explosion protection loop
    s123 = n2lp("126", "LP N2 inerting header from area 20", N2_INERT)
    s124 = n2lp("127", "instrument and seal purge N2", P_["purge_seal"])
    closed("113", [s123.flow], [s113.flow, s124.flow])
    def ex113(sh, lp):
        R(sh, 20, 700, 1100, 36, "none", "#889", 1)
        lab(sh, 30, 714, "Protection layers drawn on sheets 101-112 (HSG103 headings): inerting (para 25-29), ignition-source control (para 30 on), explosion relief vents (para 60-63),", 8.8, 400, "start", GREY)
        lab(sh, 30, 727, "isolation between units (para 80-82: rotary valves, chokes, trips from vent-panel switches), housekeeping, CO monitoring (para 51), fire response without water on coal dust (para 92).", 8.8, 400, "start", GREY)
    sheet_solids(pkg, AREA, 113, "Area 10  Coal preparation  -  dust and explosion protection: N2 inerting, O2 and CO monitoring",
        dict(tag="IN-1001", name="N2 inerting header and O2/CO analysers", inlets=[(s123, "XN", "header ESD valve", True)],
             outlets=[(s113, "XN", "bin inerting valve", False), (s124, "XN", "purge manifold", False)], spec="A1", type="inert-gas distribution + analysers",
             desc=["buffer receiver for N2 reserve", "O2 analysers (2oo3) on mill, filter, bin", "CO analysers on bin, bunker, filter", "vent-panel switches trip conveyors, feeders, mill"],
             utilities=[("LP N2", N2_INERT, "t/h (D)", "D")],
             interlocks=[("AAHH", "O2 high-high on mill gas (2oo3)", "0-21 vol %", f"H {P_['o2_limit']:g} % placeholder; trip mill (A)"), ("AAH", "CO high on bin / filter / bunker", "0-1000 ppm", "alarm; N2 flood (A)"), ("PAL", "N2 header pressure low", "0-10 bar", "L 3 bar (A)"), ("XS", "vent-panel burst switch trips conveyors", "-", "trip chain (A)"), ("FAL", "inerting flow low", "per vendor", "L (A)")],
             op=f"{N2_INERT:,.2f} t/h N2 (D)", size="buffer receiver: gap", hazard="dust explosions in mill, filter, bin, bunker; CO; N2 asphyxiation; loss of inert supply",
             extra=ex113,
             rows=[("N2 for bin", f"{N2_INERT_BIN*1000:,.0f} kg/h", "D"), ("Purge N2", f"{P_['purge_seal']*1000:,.0f} kg/h", "A"), ("Total (126)", f"{N2_INERT*1000:,.0f} kg/h", "D"), ("O2 limit", "from dust tests", "gap"), ("Vent area", "not sized", "gap")],
             notes=["Sources read for this sheet: HSE HSG103 (2nd ed., 2003) paras 25-29, 50-51, 60-63, 80-82, 90-93. Kst, Pmax, minimum ignition energy and limiting O2 of the actual blend are not available: vent areas, the O2 limit and the CO alarm are placeholders (A).",
                    "Equipment in zoned areas needs the correct category (HSG103 para 33 ff: zone 20 inside the equipment, 21/22 outside); zoning drawing is outside this package.",
                    "N2 asphyxiation hazard from inerted vessels and vents (HSG103 para 28): oxygen-deficiency alarms at manholes and vents (A)."]))
    return pkg


def lint(pkg):
    tags = [r[0] for r in pkg.equip]; dup = {t for t in tags if tags.count(t) > 1}
    assert not dup, f"duplicate equipment tags {dup}"
    assert all(r[5] for r in pkg.relief), "relief row without destination"
    sids = {k[0] for k in STREAMS}
    import re
    for sh in pkg.sheets:
        for m in re.finditer(r'<text[^>]*>(\d+|\w+)</text>', sh.svg()):
            pass
    esd_sheets = {r[-1] for r in pkg.valves if "ESD" in str(r[5])}
    need = [sh.no for sh in pkg.sheets if sh.no >= 107 and sh.no not in esd_sheets]   # sheets with pressurised gas / hot-gas / dust-explosion inventory
    assert not need, "sheet without ESD valve: " + str(need)
    print("lint ok:", len(pkg.sheets), "sheets;", len(pkg.equip), "equipment rows;", len(pkg.relief), "relief rows;", len(pkg.lines), "lines")


if __name__ == "__main__":
    pkg = Pkg("VS-CU", "Coal-to-urea complex, 3,850 t/d urea (Talcher-class), unit-by-unit P&ID", "Rev B balance scaled K=%.4f" % K)
    build(pkg); pkg.total = len(pkg.sheets)
    write_html(pkg.sheets, "/tmp/area10.html", "Area 10 coal handling and preparation", previews=True)
    lint(pkg)
    for k, v in NOTE_AREA10.items(): print(f"{k:8s} {v:,.3f}")

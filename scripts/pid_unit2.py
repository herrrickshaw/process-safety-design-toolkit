"""pid_unit2.py - further unit-sheet templates (heat exchanger, fixed-bed reactor, column, compressor train, storage tank,
packaged/solids unit) for the unit-by-unit P&ID engine. Same number discipline and registers as pid_unit.py (tags S/D/A).
"""
import math
from pid_unit import *

U_SCREEN = dict(gas_gas=60.0, gas_liq=120.0, liq_liq=500.0, cond=800.0, boil=1500.0, steam_gen=600.0)   # W/m2/K, A: screening overall coefficients


def run(s, pkg, sh, lp, area, st, pts, frm, to, spec, svc, idx, esd=False, label=None, diamond=True, vtag="HV", notes=None, valves=True):
    """draw one process line along pts, register it, add isolation (and optional ESD) valve, stream diamond, label"""
    no, n = reg_line(pkg, sh, area, st, frm, to, spec, svc)
    pipe(s, pts)
    (xa, ya), (xb, yb) = pts[0], pts[1]
    hor = abs(xb - xa) >= abs(yb - ya)
    seg = math.hypot(xb - xa, yb - ya)
    def at(f): return (xa + (xb - xa) * f, ya + (yb - ya) * f)
    vx, vy = at(0.38)
    if valves: blockv(s, pkg, sh, vx, vy, 0 if hor else 90, f"{vtag}-{lp}{idx:02d}", no, n, "gate", "isolation")
    if esd and valves:
        ex, ey = at(0.66)
        blockv(s, pkg, sh, ex, ey, 0 if hor else 90, f"XV-{lp}{idx+50:02d}", no, n, "ball", "ESD isolation", act=True)
        pkg.valves[-1][5] = "FC (ESD)"
        lab(s, ex, ey + 17, f"XV-{lp}{idx+50:02d}", 8.5, 700, "middle", RED)
    if diamond:
        dx, dy = at(0.12 if seg > 120 else 0.5)
        strm(s, dx, dy, st.n)
    lx, ly = (label if label else ((xa + 6, ya - 26) if hor else (xa + 14, ya + 12)))
    lab(s, lx, ly, no, 9, 700); lab(s, lx, ly + 10.5, f"{st.name}  {fm(st.flow)} t/h  {st.T:g} C  {st.P:g} bar", 8.5, 400, "start", GREY)
    return no, n


def head(pkg, area, no, title, tag, name):
    sh = USheet(pkg, no, title, f"{tag} {name}", None)
    lp = f"{area[0]}{no % 100:02d}"
    R(sh, 20, 84, 1100, 686, "none", "#889", 1)
    return sh, lp


def finish(pkg, sh, area, tag, name, rows, notes, relief_tag=None):
    data_panel(sh, pkg, sh, tag, name, rows, notes + ["Alarm/trip levels, margins and velocity limits are screening rules (A) in pid_unit.RULES; trip logic needs licensor cause-and-effect."])
    li = [r for r in pkg.lines if r[-1] == sh.no]
    bottom_tables(sh, sh, [[r[0], r[4], pg(r[6]), pg(r[7]), r[8], r[9], r[10]] for r in li[-11:]], [[r[0], r[3], r[4], r[5]] for r in pkg.inst if r[-1] == sh.no][-11:])
    frame(sh, pkg.total); pkg.add_sheet(sh); return sh


def eq(pkg, sh, tag, name, typ, op, des, size, mat, basis="D"):
    pkg.equip.append([tag, name, typ, op, des, size, mat, basis, sh.no])


def pump_pair(s, pkg, sh, lp, area, st, x, y, ptag, frm, dp_bar, x_out, spec, idx=40, ctrl=None):
    """duty/spare pair with suction/discharge isolation and check valves; discharge header runs right to x_out"""
    no, n = reg_line(pkg, sh, area, st, frm, "downstream", spec, "PL")
    PL(s, [(x - 60, y), (x - 60 + 40, y)], 2.6)
    for k, (nm, px) in enumerate((("A", x + 20), ("B", x + 150))):
        PL(s, [(x - 20 + (0 if k == 0 else 0), y), (px - 14, y)], 2.6)
        pump(s, px, y, 14, f"{ptag}{nm}"); lab(s, px, y + 38, "duty" if nm == "A" else "spare", 8.5, 400, "middle", GREY)
        blockv(s, pkg, sh, px - 42, y, 0, f"HV-{lp}{idx+k*10}", no, n, "gate", f"{ptag}{nm} suction")
        PL(s, [(px + 14, y - 14), (px + 14, y - 48), (x_out, y - 48)], 2.6)
        blockv(s, pkg, sh, px + 14, y - 32, 90, f"NRV-{lp}{idx+1+k*10}", no, n, "check", f"{ptag}{nm} discharge check")
        blockv(s, pkg, sh, px + 54, y - 48, 0, f"HV-{lp}{idx+2+k*10}", no, n, "gate", f"{ptag}{nm} discharge isolation")
    kw = st.q * dp_bar * 1e5 / RULES["pump_eff"] / 1000
    eq(pkg, sh, f"{ptag}A/B", f"{st.name} pump (duty/spare)", "centrifugal", f"{fm(st.flow)} t/h, dP {dp_bar:g} bar (A)", "-", f"{fm(kw)} kW shaft (D)", "A", "A")
    return no, n


# ---- heat exchanger -----------------------------------------------------------------------------------------
def sheet_hx(pkg, area, no, title, u):
    """u: tag,name, hot_in,hot_out,cold_in,cold_out (St), duty_MW (D from HMB), kind in gas_gas|gas_liq|liq_liq|cond|boil|steam_gen,
       spec, utility(bool: cold side is a utility), tctrl(bool), notes, hazard, mat"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    hi, ho, ci, co = u["hot_in"], u["hot_out"], u["cold_in"], u["cold_out"]
    Q = u["duty_MW"] * 1e6
    d1, d2 = hi.T - co.T, ho.T - ci.T
    lmtd = (d1 - d2) / math.log(d1 / d2) if abs(d1 - d2) > 1e-6 and d1 > 0 and d2 > 0 else max(d1, 1.0)
    Uc = U_SCREEN[u.get("kind", "gas_liq")]; A_m2 = Q / (Uc * lmtd)      # D: A = Q / (U LMTD), U screening (A)
    Pd = max(design_conditions(hi.P, hi.T)[0], design_conditions(ci.P, ci.T)[0]); Td = design_conditions(hi.P, hi.T)[1]
    cx, cy = 560, 330
    hxp = hx(s, cx, cy, 300, 70)
    lab(s, cx, cy - 46, u["tag"], 13, 700, "middle"); lab(s, cx, cy + 56, f"{u['name']}   area {A_m2:,.0f} m2 (D)   duty {u['duty_MW']:.1f} MW (D)", 9.5, 400, "middle", GREY)
    lab(s, cx, cy + 69, f"LMTD {lmtd:.0f} K (D)   U {Uc:g} W/m2/K (A)", 9, 400, "middle", GREY)
    # tube side = hot, shell side = cold (A)
    run(s, pkg, sh, lp, area, hi, [(60, cy), (hxp["left"][0], cy)], "upstream", u["tag"] + " tube", u["spec"], u.get("svc_h", "PG"), 1, esd=u.get("esd_hot", False), label=(66, cy - 40))
    run(s, pkg, sh, lp, area, ho, [(hxp["right"][0], cy), (1080, cy)], u["tag"] + " tube", "downstream", u["spec"], u.get("svc_h", "PG"), 2, label=(870, cy - 40))
    run(s, pkg, sh, lp, area, ci, [(cx - 110, 150), (cx - 110, cy - 35)], "supply", u["tag"] + " shell", u.get("spec_c", "A1"), u.get("svc_c", "CW"), 3, label=(cx - 100, 140))
    run(s, pkg, sh, lp, area, co, [(cx + 110, cy - 35), (cx + 110, 150)], u["tag"] + " shell", "return", u.get("spec_c", "A1"), u.get("svc_c", "CW"), 4, label=(cx + 120, 190))
    # temperature control on the hot outlet through a cold-side control valve
    ctrlvalve(s, cx - 110, 198, 90); pkg.valves.append([f"TV-{lp}11", "control", "outlet temperature", "cold feed", ci.nps(), "FO" if u.get("kind") != "boil" else "FC", sh.no])
    bub(s, pkg, sh, cx + 40, 230 + 90, "TIC", f"{lp}11", u["tag"], "hot outlet temperature", f"0-{round_up(hi.T*1.2,50):g} C", f"H {ho.T+15:.0f} / L {max(ho.T-25,0):.0f} C")
    PL(s, [(ho.T and 1080 - 60, cy + 1), (1020, 420), (cx + 40, 420), (cx + 40, 365)], 1.0, BLUE, "4 3")
    PL(s, [(cx + 40, 345), (cx - 110, 345), (cx - 110, 211)], 1.0, BLUE, "4 3")
    bub(s, pkg, sh, 900, cy + 40, "TI", f"{lp}12", u["tag"], "hot outlet temperature indication", f"0-{round_up(hi.T*1.2,50):g} C", "-")
    bub(s, pkg, sh, 180, cy + 40, "PDI", f"{lp}13", u["tag"], "tube-side differential pressure (fouling)", "0-2 bar", "H 1.0 bar", panel=False)
    # thermal-relief / tube rupture protection on the low-pressure side
    plow = min(hi.P, ci.P)
    psv_at(s, pkg, sh, cx + 250, cy - 70, f"PSV-{lp}01", u["tag"] + " shell", "tube rupture; blocked-in thermal expansion", design_conditions(ci.P, ci.T)[0], u.get("relief_dest", "flare / safe location (A)"), "not sized: needs tube-rupture flow and fluid properties")
    PL(s, [(cx + 250, cy - 92), (cx + 250, 110), (420, 110)], 1.6, INK, "6 3"); lab(s, 424, 106, "PSV discharge (A)", 8.5, 400, "start", GREY)
    # drains and vents
    for k, xx in enumerate((cx - 130, cx + 130)):
        PL(s, [(xx, cy + 35), (xx, cy + 70 + 12)], 2.0); blockv(s, pkg, sh, xx, cy + 55, 90, f"HV-{lp}2{k}", "-", 0.75, "gate", "drain" if k == 0 else "vent")
        lab(s, xx, cy + 98, "drain" if k == 0 else "vent", 8.5, 400, "middle", GREY)
    eq(pkg, sh, u["tag"], u["name"], "shell-and-tube exchanger", f"hot {hi.T:g}->{ho.T:g} C @ {hi.P:g} bar; cold {ci.T:g}->{co.T:g} C", f"{Pd:g} bar g / {Td:g} C (D)", f"{A_m2:,.0f} m2 (D)", u.get("mat", "A: to be set by licensor"))
    rows = [("Duty", f"{u['duty_MW']:.1f} MW", "D"), ("LMTD", f"{lmtd:.0f} K", "D"), ("U", f"{Uc:g} W/m2/K", "A"), ("Area", f"{A_m2:,.0f} m2", "D"),
            ("Design", f"{Pd:g} bar g / {Td:g} C", "D"), ("Tube side", hi.name, "HMB"), ("Shell side", ci.name, "HMB"), ("Relief", f"PSV-{lp}01", "A"), ("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))


# ---- fixed-bed reactor --------------------------------------------------------------------------------------
def sheet_reactor(pkg, area, no, title, u):
    """u: tag,name, feed,eff (St), beds, bed_dT (K, D), vol_m3 (D from space velocity), spec, quench(St|None), notes, hazard, mat"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    fi, ef = u["feed"], u["eff"]
    P, T = ef.P, max(fi.T, ef.T)
    dP, dT = design_conditions(P, T)
    n = u.get("beds", 1); vol = u["vol_m3"]
    D = (4 * vol / (math.pi * 3.0)) ** (1 / 3); D = max(round_up(D, 0.1), 1.0); Ht = round_up(D * 3.0 + 2.0, 0.1)
    cx, top, w, h = 520, 190, 130, 340
    v = vvessel(s, cx, top, w, h)
    bh = (h - 70) / n
    for b in range(n):
        y0 = top + 40 + b * bh
        s.add(f'<rect x="{cx-w/2+4}" y="{y0}" width="{w-8}" height="{bh*0.6}" fill="url(#hatch)" opacity=".55" stroke="{AMBER}"/>')
        lab(s, cx, y0 + bh * 0.33, f"bed {b+1}", 9, 700, "middle", AMBER)
        bub(s, pkg, sh, cx + w / 2 + 40, y0 + bh * 0.3, "TI", f"{lp}3{b+1}", u["tag"], f"bed {b+1} outlet temperature (3 points)", f"0-{round_up(T*1.3,50):g} C", "-")
        PL(s, [(cx + w / 2, y0 + bh * 0.3), (cx + w / 2 + 25, y0 + bh * 0.3)], 1.0, BLUE, "4 3")
    lab(s, cx - w / 2 - 12, top + h / 2, u["tag"], 12, 700, "end"); lab(s, cx - w / 2 - 12, top + h / 2 + 14, u["name"], 9.5, 400, "end")
    lab(s, cx - w / 2 - 12, top + h / 2 + 27, f"{D:.1f} m ID x {Ht:.1f} m T/T, {n} bed(s) (D,A)", 9, 400, "end", GREY)
    run(s, pkg, sh, lp, area, fi, [(50, top + 70), (cx - w / 2, top + 70)], "upstream", u["tag"], u["spec"], "PG", 1, esd=True, label=(56, top + 44))
    run(s, pkg, sh, lp, area, ef, [(cx, v["bottom"][1]), (cx, 640), (1000, 640)], u["tag"], "downstream", u["spec"], "PG", 2, label=(cx + 20, 660))
    if u.get("quench"):
        run(s, pkg, sh, lp, area, u["quench"], [(50, top + 190), (cx - w / 2, top + 190)], "supply", u["tag"] + " interbed", u["spec"], "PG", 3, label=(56, top + 164))
        ctrlvalve(s, 240, top + 190); pkg.valves.append([f"TV-{lp}11", "control", "interbed quench", "quench", 4, "FC", sh.no])
    # high-temperature trip and pressure
    bub(s, pkg, sh, cx - 120, 130, "TAHH", f"{lp}41", u["tag"], "bed temperature high-high (trip)", f"0-{round_up(T*1.3,50):g} C", f"HH {u.get('tahh', ef.T + 60):.0f} C (A)", panel=True)
    bub(s, pkg, sh, cx - 60, 130, "PAHH", f"{lp}42", u["tag"], "pressure high-high (trip)", f"0-{round_up(dP,10):g} bar", f"HH {min(P*1.05, 0.95*dP):.1f} bar (A, below design)", panel=True)
    bub(s, pkg, sh, cx + 140, 150, "PDI", f"{lp}43", u["tag"], "bed differential pressure", "0-5 bar", "H 3 bar")
    psv_at(s, pkg, sh, cx + 30, top - 34, f"PSV-{lp}01", u["tag"], "blocked outlet; runaway; fire", dP, u.get("relief_dest", "flare header"), "not sized: needs runaway/fire load")
    PL(s, [(cx + 30, top - 56), (cx + 30, 110), (900, 110)], 1.6, INK, "6 3"); lab(s, 700, 106, f"PSV to {u.get('relief_dest', 'flare header')} (A)", 8.5, 400, "start", GREY)
    # emergency depressurisation
    blockv(s, pkg, sh, cx + 100, 150, 0, f"XV-{lp}60", "-", 2, "ball", "emergency depressurisation", "FO", act=True)
    PL(s, [(cx + 40, top - 4), (cx + 40, 150), (cx + 80, 150)], 2.0); PL(s, [(cx + 120, 150), (900, 150)], 2.0); lab(s, 905, 154, "EDV to flare (A)", 8.5, 400, "start", GREY)
    eq(pkg, sh, u["tag"], u["name"], "fixed-bed reactor", f"{fi.T:g}->{ef.T:g} C @ {P:g} bar", f"{dP:g} bar g / {dT:g} C (D)", f"{D:.1f} m ID x {Ht:.1f} m; {vol:.0f} m3 cat. (D)", u.get("mat", "A: to be set by licensor"))
    rows = [("Operating", f"{fi.T:g}->{ef.T:g} C / {P:g} bar", "HMB"), ("Design", f"{dP:g} bar g / {dT:g} C", "D"), ("Catalyst vol.", f"{vol:.0f} m3", "D"), ("Beds", str(n), "A"),
            ("Size", f"{D:.1f} m x {Ht:.1f} m", "D,A"), ("Relief", f"PSV-{lp}01", "A"), ("Trips", "TAHH, PAHH -> ESD", "A"), ("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))


# ---- compressor train ---------------------------------------------------------------------------------------
def sheet_compressor(pkg, area, no, title, u):
    """u: tag,name, suction(St), discharge(St), power_MW (D), driver ('motor'|'steam turbine'), spec, notes, hazard, mat"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    si, di = u["suction"], u["discharge"]
    dP, dT = design_conditions(di.P, di.T)
    y = 330
    # suction KO drum
    ko = vvessel(s, 250, 230, 70, 140)
    lab(s, 250, 410, f"{u['tag']}-KO", 10, 700, "middle"); lab(s, 250, 423, "suction KO drum (A)", 8.5, 400, "middle", GREY)
    run(s, pkg, sh, lp, area, si, [(50, y), (215, y)], "upstream", f"{u['tag']}-KO", u["spec"], "PG", 1, esd=True, label=(56, y - 40))
    PL(s, [(250, ko["top"][1]), (250, 170), (440, 170), (440, y)], 2.6)
    PL(s, [(250, ko["bottom"][1]), (250, 470)], 2.0); blockv(s, pkg, sh, 250, 450, 90, f"HV-{lp}05", "-", 1, "gate", "KO drain"); lab(s, 262, 470, "drain", 8.5, 400, "start", GREY)
    bub(s, pkg, sh, 320, 330, "LAHH", f"{lp}22", f"{u['tag']}-KO", "KO drum level high-high (compressor trip)", "0-100 %", "HH 90 % (A)", panel=True)
    PL(s, [(285, 330), (305, 330)], 1.0, BLUE, "4 3")
    cp = compressor(s, 520, y, 38)
    lab(s, 520, y + 62, u["tag"], 12, 700, "middle"); lab(s, 520, y + 75, f"{u['name']}  {u['power_MW']:.1f} MW shaft (D)", 9.5, 400, "middle")
    PL(s, [(440, y), (cp["inlet"][0], y)], 2.6)
    R(s, 600, y - 22, 70, 44, "#eef3fb", INK, 1.8); lab(s, 635, y + 4, u.get("driver", "motor"), 9.5, 700, "middle"); PL(s, [(558, y), (600, y)], 3.0)
    # discharge: check valve, aftercooler, to downstream
    PL(s, [(520, y - 38), (520, 240), (760, 240)], 2.6)
    blockv(s, pkg, sh, 640, 240, 0, f"NRV-{lp}41", "-", di.nps(), "check", "discharge check")
    if u.get("aftercooler", True):
        ac = hx(s, 820, 240, 100, 32); lab(s, 820, 205, f"{u['tag']}-AC", 10, 700, "middle"); lab(s, 820, 275, "aftercooler (A)", 8.5, 400, "middle", GREY)
        PL(s, [(760, 240), (770, 240)], 2.6)
    else:
        PL(s, [(760, 240), (870, 240)], 2.6)
    run(s, pkg, sh, lp, area, di, [(870, 240), (1090, 240)], f"{u['tag']}-AC", "downstream", u["spec"], "PG", 2, esd=True, label=(880, 196))
    # anti-surge recycle
    PL(s, [(700, 240), (700, 150), (440, 150), (440, y)], 1.8, INK, "6 3")
    ctrlvalve(s, 560, 150); pkg.valves.append([f"FV-{lp}51", "control", "anti-surge recycle", "recycle", si.nps(), "FO", sh.no])
    bub(s, pkg, sh, 560, 112, "FIC", f"{lp}51", u["tag"], "anti-surge (flow vs surge line)", "per vendor", "surge margin per vendor (gap)", panel=True)
    bub(s, pkg, sh, 480, 420, "PAHH", f"{lp}42", u["tag"], "discharge pressure high-high (trip)", f"0-{round_up(dP,10):g} bar", f"HH {min(di.P*1.05, 0.95*dP):.1f} bar (A, below design)", panel=True)
    bub(s, pkg, sh, 580, 420, "VAHH", f"{lp}43", u["tag"], "vibration high-high (trip)", "per vendor", "per vendor (gap)", panel=True)
    bub(s, pkg, sh, 680, 420, "TAH", f"{lp}44", u["tag"], "discharge temperature high", f"0-{round_up(di.T*1.3,50):g} C", f"H {di.T+20:.0f} C (A)")
    psv_at(s, pkg, sh, 700, 200, f"PSV-{lp}01", u["tag"] + " discharge", "blocked discharge", dP, u.get("relief_dest", "flare header"), "not sized: needs relief load")
    kw = u["power_MW"]
    eq(pkg, sh, u["tag"], u["name"], "centrifugal compressor" if not u.get("recip") else "reciprocating compressor", f"{si.P:g} -> {di.P:g} bar", f"{dP:g} bar g / {dT:g} C (D)", f"{kw:.1f} MW shaft (D)", u.get("mat", "A"), u.get("basis", "D"))
    eq(pkg, sh, f"{u['tag']}-KO", "suction KO drum", "vertical vessel", f"{si.P:g} bar", f"{design_conditions(si.P, si.T)[0]:g} bar g (D)", "A", "A")
    rows = [("Suction", f"{si.P:g} bar / {si.T:g} C", "HMB"), ("Discharge", f"{di.P:g} bar / {di.T:g} C", "HMB"), ("Pressure ratio", f"{di.P/si.P:.1f}", "D"), ("Shaft power", f"{kw:.1f} MW", u.get("basis", "D")),
            ("Driver", u.get("driver", "motor"), "A"), ("Anti-surge", "FIC-%s51 recycle" % lp, "R"), ("Trips", "LAHH, PAHH, VAHH", "A"), ("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))


# ---- column (absorber / stripper / distillation) ----------------------------------------------------------
def sheet_column(pkg, area, no, title, u):
    """u: tag,name, feed (St), top (St), bottom (St), packing (bool), stages, reboiler (St steam|None), condenser (bool), spec, notes, hazard, mat,
       feed2 (St|None) second feed at the top (e.g. lean solvent)"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    fd, tp, bt = u["feed"], u["top"], u["bottom"]
    P, T = fd.P, max(fd.T, bt.T)
    dP, dT = design_conditions(P, T)
    Gv = max([x.q for x in (fd, tp, bt) if x.phase in ("gas", "steam", "twophase")] or [0.0])
    Ll = max([x.q for x in (fd, bt, u.get("feed2")) if x is not None and x.phase in ("liq", "slurry")] or [0.0])
    D = max(round_up(math.sqrt(4 * Gv / (math.pi * RULES["v_col_gas"])), 0.1) if Gv else 0.0,
            round_up(math.sqrt(4 * Ll / (math.pi * RULES["v_col_liq"])), 0.1) if Ll else 0.0, 0.6)   # D: larger of the vapour (2 m/s) and liquid (0.01 m/s) superficial-velocity diameters (A)
    Ht = round_up(u.get("stages", 20) * (0.6 if not u.get("packing") else 0.4) + 6, 0.5)
    cx, top, w, h = 470, 180, 100, 400
    v = vvessel(s, cx, top, w, h, trays=0 if u.get("packing") else min(u.get("stages", 20) // 3, 10), packing=bool(u.get("packing")))
    lab(s, cx - w / 2 - 12, top + 40, u["tag"], 12, 700, "end"); lab(s, cx - w / 2 - 12, top + 54, u["name"], 9.5, 400, "end")
    lab(s, cx - w / 2 - 12, top + 67, f"{D:.1f} m ID x {Ht:.0f} m T/T (D,A)", 9, 400, "end", GREY)
    run(s, pkg, sh, lp, area, fd, [(50, top + h - 90), (cx - w / 2, top + h - 90)], "upstream", u["tag"], u["spec"], "PG", 1, esd=u.get("esd", False), label=(56, top + h - 134))
    if u.get("feed2"):
        run(s, pkg, sh, lp, area, u["feed2"], [(50, top + 50), (cx - w / 2, top + 50)], "upstream", u["tag"] + " top feed", u["spec"], "PL", 3, label=(56, top + 6))
    run(s, pkg, sh, lp, area, tp, [(cx, v["top"][1]), (cx, 125), (900, 125)], u["tag"], "downstream", u["spec"], "PG", 2, label=(cx + 24, 100))
    run(s, pkg, sh, lp, area, bt, [(cx, v["bottom"][1]), (cx, 690), (1000, 690)], u["tag"], "downstream", u["spec"], "PL", 4, label=(cx + 24, 672))
    if u.get("reboiler"):
        rb = u["reboiler"]; hx(s, cx + 190, top + h - 20, 90, 30); lab(s, cx + 190, top + h - 44, f"{u['tag']}-RB", 10, 700, "middle")
        PL(s, [(cx + w / 2, top + h - 20), (cx + 145, top + h - 20)], 2.0); PL(s, [(cx + 235, top + h - 20), (cx + 270, top + h - 20), (cx + 270, top + h - 80), (cx + w / 2, top + h - 80)], 2.0)
        run(s, pkg, sh, lp, area, rb, [(cx + 190, top + h + 70), (cx + 190, top + h - 5)], "supply", f"{u['tag']}-RB", "A1", "ST", 5, label=(cx + 200, top + h + 60))
    bub(s, pkg, sh, cx + 90, top + 120, "PIC", f"{lp}11", u["tag"], "column top pressure", f"0-{round_up(dP,5):g} bar", f"H {P*1.05:.0f} / L {P*0.9:.0f} bar")
    bub(s, pkg, sh, cx + 90, top + h - 120, "LIC", f"{lp}21", u["tag"], "sump level", "0-100 %", "H 80 / L 20 % ; LL 10 % trip", panel=True)
    bub(s, pkg, sh, cx + 150, top + h - 120, "LAHH", f"{lp}22", u["tag"], "sump level high-high (flooding)", "0-100 %", "HH 90 % (A)", panel=True)
    bub(s, pkg, sh, cx + 90, top + 205, "PDI", f"{lp}13", u["tag"], "column differential pressure (flooding)", "0-1 bar", "H 0.7 bar (A)")
    bub(s, pkg, sh, cx + 150, top + 205, "TI", f"{lp}14", u["tag"], "profile temperatures", f"0-{round_up(T*1.3,50):g} C", "-")
    ctrlvalve(s, cx + 40, 125); pkg.valves.append([f"PV-{lp}11", "control", "top pressure", tp.name, tp.nps(), "FO", sh.no])
    psv_at(s, pkg, sh, cx - 30, top - 36, f"PSV-{lp}01", u["tag"], "blocked outlet; fire; reboiler/utility failure", dP, u.get("relief_dest", "flare header"), "not sized: needs relief load")
    PL(s, [(cx - 30, top - 58), (cx - 30, 108), (60, 108)], 1.6, INK, "6 3"); lab(s, 64, 103, f"PSV to {u.get('relief_dest', 'flare header')} (A)", 8.5, 400, "start", GREY)
    eq(pkg, sh, u["tag"], u["name"], "packed column" if u.get("packing") else "trayed column", f"{P:g} bar, {fd.T:g}->{bt.T:g} C", f"{dP:g} bar g / {dT:g} C (D)", f"{D:.1f} m ID x {Ht:.0f} m (D,A)", u.get("mat", "A: to be set by licensor"))
    rows = [("Operating", f"{P:g} bar / {fd.T:g}->{bt.T:g} C", "HMB"), ("Design", f"{dP:g} bar g / {dT:g} C", "D"), ("Diameter", f"{D:.1f} m", "D (vapour / liquid load, A)"), ("Height", f"{Ht:.0f} m", "A"),
            ("Internals", "packing" if u.get("packing") else f"{u.get('stages',20)} trays (A)", "A"), ("Relief", f"PSV-{lp}01", "A"), ("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))


# ---- storage tank -------------------------------------------------------------------------------------------
def sheet_tank(pkg, area, no, title, u):
    """u: tag,name, inflow (St), outflow (St), days (storage), roof, spec, refrigerated (bool), notes, hazard, mat"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    inf, out = u["inflow"], u["outflow"]
    rho = out.rho; vol = out.flow * 1000 * 24 * u["days"] / rho * 1.1      # D: working volume = flow (t/h x 1000 kg/t) x 24 h x days / density, + 10 % heel/ullage (A)
    h_m = u.get("h_m", 20.0); D = math.sqrt(4 * vol / (math.pi * h_m))
    cx, base, w, h = 470, 470, 220, 220
    t = tank(s, cx, base, w, h, roof=u.get("roof", "cone"), level=0.7)
    lab(s, cx - w / 2 - 14, base - h / 2, u["tag"], 12, 700, "end"); lab(s, cx - w / 2 - 14, base - h / 2 + 14, u["name"], 9.5, 400, "end")
    lab(s, cx - w / 2 - 14, base - h / 2 + 27, f"{vol:,.0f} m3 gross ({u['days']:g} d, D,A)  {D:.0f} m dia", 9, 400, "end", GREY)
    run(s, pkg, sh, lp, area, inf, [(60, 175), (cx - 40, 175), (cx - 40, t["top"][1] + 6)], "upstream", u["tag"], u["spec"], u.get("svc", "PL"), 1, esd=True, label=(66, 134))
    run(s, pkg, sh, lp, area, out, [(cx + 60, base), (cx + 60, 560)], u["tag"], "downstream", u["spec"], u.get("svc", "PL"), 2, label=(cx + 72, 520))
    pump_pair(s, pkg, sh, lp, area, out, cx + 20, 600, u.get("pumps", "P-" + u["tag"][2:]), u["tag"], u.get("pump_dp", 5.0), 1000, u["spec"], 40)
    # vent / pressure-vacuum protection
    psv_at(s, pkg, sh, cx + 40, t["top"][1] - 8, f"PVRV-{lp}01", u["tag"], "inbreathing/outbreathing; fire", 0.02 if not u.get("refrigerated") else 0.1, u.get("vent_dest", "atmosphere via flame arrestor (A)"), "not sized: needs pump-in/out rates and fire case")
    PL(s, [(cx + 40, t["top"][1] - 30), (cx + 40, 125), (900, 125)], 1.6, INK, "6 3"); lab(s, 700, 121, "vent / BOG header (A)", 8.5, 400, "start", GREY)
    bub(s, pkg, sh, cx + 150, base - 70, "LT", f"{lp}21", u["tag"], "level (radar)", "0-100 %", "-"); PL(s, [(cx + 110, base - 70), (cx + 135, base - 70)], 1.0, BLUE, "4 3")
    bub(s, pkg, sh, cx + 190, base - 70, "LAHH", f"{lp}22", u["tag"], "level high-high (stops inflow)", "0-100 %", "HH 95 % (A)", panel=True)
    bub(s, pkg, sh, cx + 150, base - 140, "LALL", f"{lp}23", u["tag"], "level low-low (stops pumps)", "0-100 %", "LL 5 % (A)", panel=True)
    bub(s, pkg, sh, cx + 190, base - 140, "TI", f"{lp}14", u["tag"], "bulk temperature", f"{out.T-40:.0f} to {out.T+40:.0f} C", "-")
    R(s, cx - w / 2 - 36, base - 40, w + 72, 52, "none", "#c62828", 1.6, "6 3"); lab(s, cx - w / 2 - 32, base + 26, "bund / dyke (A); volume rule: not obtained", 8.5, 700, "start", RED)
    eq(pkg, sh, u["tag"], u["name"], "storage tank" + (" (refrigerated)" if u.get("refrigerated") else ""), f"{out.T:g} C, near-atmospheric", "A", f"{vol:,.0f} m3 (D)", u.get("mat", "A"))
    rows = [("Storage", f"{u['days']:g} days of {out.name}", "A"), ("Gross volume", f"{vol:,.0f} m3", "D"), ("Diameter", f"{D:.0f} m x {h_m:g} m", "D,A"), ("Roof", u.get("roof", "cone"), "A"),
            ("Pumps", u.get("pumps", "-") + "A/B", "A"), ("Bund", "volume rule: gap", "gap"), ("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))


# ---- packaged / solids unit (mill, cold box, prilling tower, ...) -------------------------------------------
def sheet_package(pkg, area, no, title, u):
    """u: tag,name, inlets [(St, label)], outlets [(St, label)], utilities [(name, qty, unit, basis)], interlocks [str], notes, hazard, desc"""
    sh, lp = head(pkg, area, no, title, u["tag"], u["name"]); s = sh
    bx, by, bw, bh = 400, 220, 280, 300
    R(s, bx, by, bw, bh, "#eef3fb", INK, 2.4)
    lab(s, bx + bw / 2, by + 24, u["tag"], 14, 700, "middle"); lab(s, bx + bw / 2, by + 42, u["name"], 10, 400, "middle")
    for i, t in enumerate(u.get("desc", [])): lab(s, bx + bw / 2, by + 70 + i * 13, t, 9, 400, "middle", GREY)
    ins, outs = u["inlets"], u["outlets"]
    for i, (st, lb, *ph) in enumerate(ins):
        yy = by + 60 + i * round(min(80, (bh - 100) / max(len(ins), 1)))
        run(s, pkg, sh, lp, area, st, [(50, yy), (bx, yy)], "upstream", u["tag"], u["spec"], ph[0] if ph else "PG", i + 1, esd=(i == 0 and u.get("esd", False)), label=(56, yy - 34), valves=not u.get("solids", False))
    for i, (st, lb, *ph) in enumerate(outs):
        yy = by + 60 + i * round(min(80, (bh - 100) / max(len(outs), 1)))
        run(s, pkg, sh, lp, area, st, [(bx + bw, yy), (1090, yy)], u["tag"], "downstream", u["spec"], ph[0] if ph else "PG", 10 + i, label=(bx + bw + 20, yy - 34), valves=not u.get("solids", False))
    for i, (nm, q, unit, basis) in enumerate(u.get("utilities", [])):
        xx = bx + 40 + i * 70
        PL(s, [(xx, by + bh + 60), (xx, by + bh)], 1.6, GREEN); arrow(s, xx, by + bh, "u", GREEN, 6)
        lab(s, xx, by + bh + 74, nm, 9, 700, "middle", GREEN); lab(s, xx, by + bh + 86, (f"{q:,.1f} {unit}" if abs(q) >= 0.05 else f"A ({unit})"), 8.5, 400, "middle", GREY)
    for i, il in enumerate(u.get("interlocks", [])):
        bub(s, pkg, sh, 150 + i * 60, 600, il[0], f"{lp}{60+i}", u["tag"], il[1], il[2], il[3], panel=True)
    if u.get("relief"):
        psv_at(s, pkg, sh, bx + bw - 40, by - 20, f"PSV-{lp}01", u["tag"], u["relief"], u.get("relief_set", max(design_conditions(x[0].P, x[0].T)[0] for x in list(ins) + list(outs))), u.get("relief_dest", "flare / safe location (A)"), "not sized: needs relief load")
    eq(pkg, sh, u["tag"], u["name"], u.get("type", "packaged unit"), u.get("op", "see HMB"), u.get("design", "A"), u.get("size", "A"), u.get("mat", "A: vendor"), u.get("basis", "A"))
    rows = [("Type", u.get("type", "packaged unit"), "A")] + [(a, b, c) for a, b, c in u.get("rows", [])] + [("Hazard", u.get("hazard", "see HAZOP"), "-")]
    return finish(pkg, sh, area, u["tag"], u["name"], rows, u.get("notes", []))

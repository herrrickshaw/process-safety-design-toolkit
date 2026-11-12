"""pid_unit.py - unit-by-unit P&ID sheet engine (standard library only, builds on pidlib.py).

One sheet = one equipment unit with its ancillaries. Templates draw the unit, size lines and vessels from the
heat-and-material balance, and register every line, instrument, relief device and equipment item so that the
line list, instrument index and equipment list are generated from the SAME data as the drawings.

Number discipline (same as the rest of the toolkit): every value carries a tag.
  S sourced (document named), D derived (formula named here), A assumed screening rule (to be confirmed by licensor).
No licensed-standard text and no vendor data are used. Velocity limits, residence times, design margins and the
ISA-5.1 tag letters are screening conventions, listed in RULES below so they are reviewed in one place.
"""
import math, csv, os, textwrap
from pidlib import *

# ---- screening rules (all tag A) -------------------------------------------------------------------------
RULES = dict(
    v_gas=20.0, v_gas_hp=25.0, v_liq=2.0, v_slurry=1.5, v_twophase=12.0, v_steam=35.0, v_suction=1.0,   # m/s
    v_sep_gas=0.5, v_col_liq=0.01, v_col_gas=2.0, res_flash_min=5.0, res_surge_min=5.0, ld_ratio=3.0,                                                   # min, -
    dp_margin_bar=2.0, dp_margin_frac=0.10, dt_margin_C=25.0,                                              # design margins
    pump_eff=0.70, alarm_H=0.80, alarm_HH=0.90, alarm_L=0.20, alarm_LL=0.10,                               # fractions of range
)
NPS = [0.5, 0.75, 1, 1.5, 2, 3, 4, 6, 8, 10, 12, 14, 16, 18, 20, 24, 30, 36, 42, 48,
       54, 60, 72, 84, 96, 120]   # nominal pipe sizes, inches (public series to 48 in); above 48 in the entries are fabricated ducts, nominal bore (A)
R_GAS = 8.314462618   # J/mol/K (CODATA)


def nps_for(q_m3_s, v):
    d_in = math.sqrt(4 * q_m3_s / (math.pi * v)) / 0.0254
    for n in NPS:
        if n >= d_in: return n
    return NPS[-1]


def round_up(x, step): return math.ceil(x / step) * step


def pg(x):
    """compact number text for tables (no float noise)"""
    try: return f"{float(x):g}"
    except (TypeError, ValueError): return x


def fm(x, d=1): return f"{x:,.{d}f}"


class Pkg:
    """collects the registers while sheets are drawn"""
    def __init__(self, code, project, basis, rev="P0"):
        self.code, self.project, self.basis, self.rev = code, project, basis, rev
        self.sheets, self.lines, self.inst, self.equip, self.relief, self.valves = [], [], [], [], [], []
        self.seq = {}; self.total = 0

    def next_line(self, area, size, svc, spec):
        self.seq[area] = self.seq.get(area, 0) + 1
        return f'{size:g}"-{svc}-{area}{self.seq[area]:02d}-{spec}'

    def add_sheet(self, sh): self.sheets.append(sh)

    def write_registers(self, outdir):
        os.makedirs(outdir, exist_ok=True)
        def w(name, head, rows):
            with open(os.path.join(outdir, name), "w", newline="") as f:
                c = csv.writer(f); c.writerow(head); c.writerows(rows)
        w("LINE_LIST.csv", ["line_no", "service", "from", "to", "stream", "phase", "T_C", "P_bar", "flow_t_h", "NPS_in", "velocity_m_s", "spec", "tag_size", "sheet"], self.lines)
        w("INSTRUMENT_INDEX.csv", ["tag", "service", "equipment", "function", "range", "alarm_trip", "set_tag", "sheet"], self.inst)
        w("EQUIPMENT_LIST.csv", ["tag", "name", "type", "operating", "design", "size", "material", "basis_tag", "sheet"], self.equip)
        w("RELIEF_SCHEDULE.csv", ["tag", "protects", "case", "set_bar_g", "set_tag", "destination", "sizing_status", "sheet"], self.relief)
        w("STREAM_TABLE.csv", ["stream", "name", "phase", "flow_t_h", "T_C", "P_bar", "mw_or_rho"], [[k[0], k[1], v.phase, fm(v.flow), v.T, v.P, (fm(v.mw,2) if v.mw else v.rho_in)] for k, v in sorted(STREAMS.items(), key=lambda kv: kv[0][0])])
        w("VALVE_LIST.csv", ["tag", "type", "service", "line_no", "size_in", "fail_position", "sheet"], self.valves)


class USheet(Sheet):
    """Sheet that prints the package revision instead of the library default"""
    def __init__(self, pkg, no, title, sub, total_ref):
        super().__init__(no, title, sub, code=pkg.code, project=pkg.project, basis=pkg.basis)
        self.pkg, self.total_ref = pkg, total_ref

    def svg(self):
        t = super().svg()
        n = len(self.title)
        if n * 21 * 0.56 > 1040:   # long title: reduce the font so it stops before the right-hand banner text
            fs = max(13.0, 1040 / (n * 0.56)); t = t.replace('font-size="21"', f'font-size="{fs:.1f}"', 1)
        return (t.replace("Rev A", f"Rev {self.pkg.rev}").replace("Draft A. Screening aid", f"Draft {self.pkg.rev}. Screening aid")
                 .replace(f"-00{self.no}", f"-{self.no:03d}").replace(f"Sheet {self.no} of 0", f"Sheet {sorted(x.no for x in self.pkg.sheets).index(self.no)+1} of {len(self.pkg.sheets)}"))


# ---- stream helper ----------------------------------------------------------------------------------------
STREAMS = {}   # registry of every stream used, for the stream table in the package


class St:
    """a stream with the data the sizing rules need. phase in gas|liq|slurry|steam|twophase"""
    def __init__(self, n, name, phase, flow_t_h, T, P, mw=None, rho=None, tags=("D", "A", "A")):
        self.n, self.name, self.phase, self.flow, self.T, self.P, self.mw, self.rho_in, self.tags = n, name, phase, flow_t_h, T, P, mw, rho, tags
        STREAMS[(str(n), name)] = self

    @property
    def rho(self):   # kg/m3; gas ideal (D: rho = P M / R T, P in bar abs), liquid as given (A)
        if self.rho_in: return self.rho_in
        return self.P * 1e5 * self.mw / 1000 / (R_GAS * (self.T + 273.15))

    @property
    def q(self): return self.flow * 1000 / 3600 / self.rho     # m3/s

    def vel_rule(self):
        return {"gas": RULES["v_gas_hp"] if self.P > 30 else RULES["v_gas"], "liq": RULES["v_liq"], "slurry": RULES["v_slurry"],
                "twophase": RULES["v_twophase"], "steam": RULES["v_steam"]}[self.phase]

    def nps(self): return nps_for(self.q, self.vel_rule())

    def velocity(self, nps): return self.q / (math.pi * (nps * 0.0254) ** 2 / 4)


# ---- drawing helpers --------------------------------------------------------------------------------------
def lab(s, x, y, t, size=9.5, w=400, anchor="start", fill=INK): T(s, x, y, t, size, w, anchor, fill)


def reg_line(pkg, sh, area, st, frm, to, spec, svc):
    n = st.nps(); no = pkg.next_line(area, n, svc, spec)
    pkg.lines.append([no, st.name, frm, to, st.n, st.phase, st.T, st.P, fm(st.flow), n, fm(st.velocity(n), 1), spec, "A", sh.no])
    return no, n


def blockv(s, pkg, sh, x, y, rot, tag, line_no, size, kind="gate", svc="block", fail="-", act=False):
    valve(s, x, y, rot, kind, act=act)
    pkg.valves.append([tag, kind, svc, line_no, size, fail, sh.no])


def bub(s, pkg, sh, x, y, fn, loop, equip, svc, rng, alarm, setag="A", panel=False):
    bubble(s, x, y, fn, loop, panel=panel)
    pkg.inst.append([f"{fn}-{loop}", svc, equip, fn, rng, alarm, setag, sh.no])


def psv_at(s, pkg, sh, x, y, tag, protects, case, set_bar, dest, status, label_dx=-10):
    psv(s, x, y); lab(s, x + label_dx, y - 4, tag, 9.5, 700, "end")
    pkg.relief.append([tag, protects, case, fm(set_bar), "A", dest, status, sh.no])


def stream_tag(s, x, y, st, dy=-22): strm(s, x, y, st.n)


def line_label(s, x, y, no, st, anchor="start"):
    lab(s, x, y, no, 9, 700, anchor); lab(s, x, y + 10.5, f"{st.name}  {fm(st.flow)} t/h  {st.T:g} C  {st.P:g} bar", 8.5, 400, anchor, GREY)


def design_conditions(P, T):
    """D: design pressure = op + max(2 bar, 10 %); design temperature = op + 25 C (rules A)"""
    if P < 1.0:   # vacuum service (P in bar abs): rated for full vacuum plus 3.5 bar g internal (A, screening convention, to be set by the designer)
        return 3.5, round_up(T + RULES["dt_margin_C"], 5)
    dp = max(RULES["dp_margin_bar"], RULES["dp_margin_frac"] * P)
    return round_up(P + dp, 0.5), round_up(T + RULES["dt_margin_C"], 5)


def data_panel(s, pkg, sh, tag, name, rows, notes):
    panel_box(s)
    y = section(s, 1135, 84, 445, f"{tag}  {name}")
    wrapped = [("Item", "Value", "Basis")]
    for a, b, c in rows:       # values longer than the column are wrapped onto continuation rows instead of overflowing the panel
        parts = textwrap.wrap(str(b), 34) or [""]; cparts = textwrap.wrap(str(c), 15) or [""]
        for k in range(max(len(parts), len(cparts))):
            wrapped.append((a if k == 0 else "", parts[k] if k < len(parts) else "", cparts[k] if k < len(cparts) else ""))
    y = table(s, 1135, y + 2, [120, 220, 105], wrapped, rh=18, size=10)
    y = section(s, 1135, y + 10, 445, "Notes")
    for n in notes: y = WRAP(s, 1143, y + 16, n, 72, 10, 12.5, bullet=True) - 2
    return y


def bottom_tables(s, sh, line_rows, inst_rows):
    y = 790
    section(s, 20, y, 560, "Line list (this sheet)")
    table(s, 20, y + 24, [118, 78, 60, 52, 58, 58, 86], [("Line no.", "Stream", "T C", "P bar", "t/h", "NPS", "v m/s (D)")] + line_rows[:11], rh=16.5, size=8.8)
    section(s, 600, y, 520, "Instruments (this sheet)")
    table(s, 600, y + 24, [92, 128, 168, 132], [("Tag", "Function", "Range (A)", "Alarm / trip (A)")] + inst_rows[:11], rh=16.5, size=8.8)


# ---- template 1: vertical vessel (separator / KO / flash / surge drum) with optional pump pair --------------
def sheet_vessel(pkg, area, no, title, u):
    """u: tag, name, inlet(St), gas(St|None), liq(St|None), res_min, pumps(tag|None), pump_dp_bar, spec, svc dict,
       internals ('cyclone'|'demister'|None), notes[], hazard text, drain(bool), P/T come from inlet"""
    sh = USheet(pkg, no, title, f"{u['tag']} {u['name']}", None)
    s = sh; lp = f"{area[0]}{no % 100:02d}"
    inl, gas, liq = u["inlet"], u.get("gas"), u.get("liq")
    P, T = inl.P, inl.T
    dP, dT = design_conditions(P, T)
    # D: vessel volume from liquid residence time on the liquid flow; diameter from L/D
    vol = (liq.q * 60 * u.get("res_min", RULES["res_flash_min"])) / 0.5 if liq else 3.0   # 50 % working fill
    D = (4 * vol / (math.pi * RULES["ld_ratio"])) ** (1 / 3); D = max(round_up(D, 0.1), 0.8)
    if gas: D = max(D, round_up(math.sqrt(4 * gas.q / (math.pi * RULES["v_sep_gas"])), 0.1))   # D: also big enough for the vapour (superficial velocity rule, A)
    Ht = round_up(D * RULES["ld_ratio"], 0.1)
    R(s, 20, 84, 1100, 686, "none", "#889", 1)
    cx, top, w, h = 470, 215, 120, 270
    v = vvessel(s, cx, top, w, h)
    lab(s, cx - w / 2 - 12, top + h / 2, u["tag"], 12, 700, "end"); lab(s, cx - w / 2 - 12, top + h / 2 + 14, u["name"], 9.5, 400, "end")
    lab(s, cx - w / 2 - 12, top + h / 2 + 27, f"{D:.1f} m ID x {Ht:.1f} m T/T (D, A)", 9, 400, "end", GREY)
    if u.get("internals") == "demister":
        s.add(f'<rect x="{cx-w/2+4}" y="{top+22}" width="{w-8}" height="16" fill="url(#hatch)" opacity=".6"/>'); lab(s, cx + w / 2 + 6, top + 33, "demister (A)", 8.5, 400, "start", GREY)
    # inlet nozzle N1 left
    n_in, nps_in = reg_line(pkg, sh, area, inl, "upstream", u["tag"], u["spec"], u.get("svc_in", "PG"))
    yin = top + 90
    pipe(s, [(40, yin), (cx - w / 2, yin)])
    blockv(s, pkg, sh, 140, yin, 0, f"HV-{lp}01", n_in, nps_in, "gate", "inlet isolation")
    if u.get("esd", True):
        blockv(s, pkg, sh, 230, yin, 0, f"XV-{lp}02", n_in, nps_in, "ball", "ESD inlet isolation", "FC", act=True)
        pkg.valves[-1][5] = "FC (ESD)"
        s.add(f'<line x1="230" y1="{yin-9}" x2="230" y2="{yin-28}" stroke="{RED}" stroke-width="1.4" stroke-dasharray="4 3"/>')
        lab(s, 236, yin - 24, f"XV-{lp}02", 9, 700, "start", RED)
    strm(s, 80, yin, inl.n); line_label(s, 52, yin - 26, n_in, inl)
    lab(s, 38, yin + 22, "from upstream unit (see key sheet)", 8.5, 400, "start", GREY)
    # gas outlet N2 top
    if gas:
        n_g, nps_g = reg_line(pkg, sh, area, gas, u["tag"], "downstream", u["spec"], u.get("svc_gas", "PG"))
        ytop = 140
        pipe(s, [(cx + 10, v["top"][1]), (cx + 10, ytop), (900, ytop)])
        blockv(s, pkg, sh, 600, ytop, 0, f"HV-{lp}03", n_g, nps_g, "gate", "gas outlet isolation")
        ctrlvalve(s, 740, ytop); pkg.valves.append([f"PV-{lp}11", "control", "pressure control", n_g, nps_g, "FO", no])
        bub(s, pkg, sh, 740, ytop + 44, "PIC", f"{lp}11", u["tag"], "operating pressure", f"0-{round_up(dP, 5):g} bar", f"H {P*1.05:.0f}/ L {P*0.9:.0f} bar")
        PL(s, [(740, ytop + 29), (740, ytop + 10)], 1.0, BLUE, "4 3")
        strm(s, 860, ytop, gas.n); line_label(s, 780, ytop + 22, n_g, gas)
        lab(s, 905, ytop + 4, "to downstream unit", 8.5, 400, "start", GREY)
    # liquid outlet N3 bottom
    ybot = top + h + 30
    if liq:
        n_l, nps_l = reg_line(pkg, sh, area, liq, u["tag"], u.get("pumps") or "downstream", u["spec"], u.get("svc_liq", "PL"))
        pipe(s, [(cx, v["bottom"][1]), (cx, 590)], arrow_=False)
        strm(s, cx, 575, liq.n); blockv(s, pkg, sh, cx, 526, 90, f"HV-{lp}05", n_l, nps_l, "gate", "liquid outlet isolation")
        lab(s, cx + 12, 548, n_l, 9, 700); lab(s, cx + 12, 559, f"{liq.name}  {fm(liq.flow)} t/h  {liq.T:g} C", 8.5, 400, "start", GREY)
        # level control: LT with 3 alarms + LIC
        lx = cx + w / 2 + 70
        PL(s, [(cx + w / 2, top + h - 30), (lx, top + h - 30)], 1.0, BLUE, "4 3"); PL(s, [(cx + w / 2, top + 150), (lx, top + 150)], 1.0, BLUE, "4 3")
        bub(s, pkg, sh, lx + 15, top + h - 30, "LT", f"{lp}21", u["tag"], "liquid level", "0-100 %", "-")
        bub(s, pkg, sh, lx + 15, top + 150, "LAHH", f"{lp}22", u["tag"], "level high-high (trip)", "0-100 %", f"HH {RULES['alarm_HH']*100:.0f} %", panel=True)
        bub(s, pkg, sh, lx + 55, top + h - 30, "LIC", f"{lp}21", u["tag"], "level control", "0-100 %", f"H {RULES['alarm_H']*100:.0f} / L {RULES['alarm_L']*100:.0f} % ; LL {RULES['alarm_LL']*100:.0f} % trip", panel=True)
        pkg.inst[-1][3] = "LIC"; pkg.inst.append([f"LALL-{lp}23", "level low-low (pump trip)", u["tag"], "LALL", "0-100 %", f"LL {RULES['alarm_LL']*100:.0f} %", "A", no])
        if u.get("pumps"):
            pt = u["pumps"]; py = 640
            PL(s, [(cx, 590), (cx, py), (cx + 70, py)], 2.6); arrow(s, cx + 70, py, "r")
            for k, (nm, px) in enumerate((("A", cx + 120), ("B", cx + 270))):
                PL(s, [(cx + 70 + (0 if k == 0 else 0), py), (px - 14, py)], 2.6)
                pp = pump(s, px, py, 14, f"{pt}{nm}")
                lab(s, px, py + 38, ("duty" if nm == "A" else "spare"), 8.5, 400, "middle", GREY)
                blockv(s, pkg, sh, px - 50, py, 0, f"HV-{lp}3{k}", n_l, nps_l, "gate", f"{pt}{nm} suction");
                PL(s, [(px + 14, py - 14), (px + 14, py - 50), (cx + 400, py - 50)], 2.6)
                blockv(s, pkg, sh, px + 14, py - 34, 90, f"NRV-{lp}4{k}", n_l, nps_l, "check", f"{pt}{nm} discharge check")
                blockv(s, pkg, sh, px + 64, py - 50, 0, f"HV-{lp}5{k}", n_l, nps_l, "gate", f"{pt}{nm} discharge isolation")
            ctrlvalve(s, cx + 360, py - 50); pkg.valves.append([f"LV-{lp}21", "control", "level control", n_l, nps_l, "FC", no])
            pipe(s, [(cx + 400, py - 50), (1000, py - 50)])
            lab(s, 1005, py - 46, "to downstream unit", 8.5, 400, "start", GREY)
            dp = u.get("pump_dp_bar", 6.0); kw = liq.q * dp * 1e5 / RULES["pump_eff"] / 1000
            pkg.equip.append([f"{pt}A/B", f"{u['name']} pump (duty/spare)", "centrifugal", f"{fm(liq.flow)} t/h, dP {dp:g} bar (A)", "-", f"{fm(kw)} kW shaft (D: Q dP / eff 0.70 A)", "A", "A", no])
    # relief valve on gas space
    psv_at(s, pkg, sh, cx - 30, top - 34, f"PSV-{lp}01", u["tag"], u.get("relief_case", "blocked outlet; fire"), dP, u.get("relief_dest", "flare header"), "not sized: needs relief load (fire wetted area, vapour generation)")
    PL(s, [(cx - 30, top - 52), (cx - 30, 112), (60, 112)], 1.6, INK, "6 3"); lab(s, 64, 107, f"PSV to {u.get('relief_dest', 'flare header')} (A)", 8.5, 400, "start", GREY)
    # drains, vent, N2 purge
    yd = top + h + 30
    PL(s, [(cx - 50, yd), (cx - 50, yd + 26)], 2.0)
    blockv(s, pkg, sh, cx - 50, yd + 8, 90, f"HV-{lp}08", "-", 1.5, "gate", "drain 1 (double block)"); blockv(s, pkg, sh, cx - 50, yd + 20, 90, f"HV-{lp}09", "-", 1.5, "gate", "drain 2")
    lab(s, cx - 58, yd + 40, "closed drain", 8.5, 400, "end", GREY)
    PL(s, [(cx + 36, top - 14), (cx + 36, top - 44)], 2.0); blockv(s, pkg, sh, cx + 36, top - 30, 90, f"HV-{lp}10", "-", 0.75, "gate", "vent"); lab(s, cx + 46, top - 28, "vent / N2 purge", 8.5, 400, "start", GREY)
    # equipment register
    pkg.equip.append([u["tag"], u["name"], "vertical vessel", f"{P:g} bar, {T:g} C (S/A per HMB)", f"{dP:g} bar g / {dT:g} C (D)", f"{D:.1f} m ID x {Ht:.1f} m T/T (D)", u.get("mat", "A: to be set by licensor"), "D", no])
    rows = [("Service", u["name"], "-"), ("Operating", f"{P:g} bar / {T:g} C", "HMB"), ("Design", f"{dP:g} bar g / {dT:g} C", "D"),
            ("Volume", f"{vol:.1f} m3 (50 % fill)", "D"), ("Size", f"{D:.1f} m ID x {Ht:.1f} m", "D,A"), ("Residence", f"{u.get('res_min', RULES['res_flash_min']):g} min liquid", "A"),
            ("Material", u.get("mat", "to be set"), "A"), ("Relief", f"PSV-{lp}01 set {dP:g} bar g", "A"), ("Hazard", u.get("hazard", "see HAZOP sheet"), "-")]
    data_panel(s, pkg, sh, u["tag"], u["name"], rows, u.get("notes", []) + ["Instrument alarm and trip levels are screening fractions of range (A); trip logic needs the licensor cause-and-effect.", "Lines are sized by the screening velocity limits in pid_unit.RULES (A)."])
    li = [r for r in pkg.lines if r[-1] == sh.no][-6:]
    bottom_tables(s, sh, [[r[0], r[4], pg(r[6]), pg(r[7]), r[8], r[9], r[10]] for r in li], [[r[0], r[3], r[4], r[5]] for r in pkg.inst if r[-1] == sh.no][-11:])
    frame(s, pkg.total)
    pkg.add_sheet(sh)
    return sh

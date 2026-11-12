"""urea_safety.py - fold the sourced safety findings (docs/pid/urea_detail/sources/SAFETY_SOURCES.md) into the coal-to-urea package.

apply(pkg) runs after every area module has built its sheets and does five things:
  1. relief schedule: fire-case screening rate for ammonia-wetted vessels (29 CFR 1910.111 note to Table H-36), dust-explosion vent inputs (coal envelope),
     and the 'standard not obtained' wording for the cases that stay open;
  2. detector alarm set points: low alarm at the 8-h workplace exposure limit and high alarm at the 15-min limit (UK HSE EH40/2005 Table 1) for NH3, H2S and CO,
     in the instrument register and in the printed instrument tables;
  3. a 'Safety sources applied' box on each affected unit sheet (storage, mill circuit, O2 service, sulphur pit, carbamate/urea, gasifier, acid gas);
  4. a safety-basis section (area 95): relief design-basis register (OSHA 1910.119 PSI requirement), detector basis, dust and inerting basis, oxygen-service
     check against the EIGA curves, incident lessons mapped to sheets, and the open-gap register;
  5. nothing is invented: every number below is from a document named in SAFETY_SOURCES.md (grade in brackets) or is derived from the package; paywalled standards
     (API 520/521/2000, NFPA, IEC 61511, IIAR, ISO) stay 'gap: standard not obtained'.
Oxygen line sizing (EIGA Doc 13/20 impingement curve) is applied in pid_unit.St.vel_rule, so O2 lines are sized by it when the area modules build.
"""
import math, re, html, collections, textwrap
from pid_unit import *
from pid_unit2 import *

NH3_FIRE = "29 CFR 1910.111 (b)(9) Table H-36 note: A > 2,500 sq ft -> 22.11 A^0.82 SCFM air at 120 % of set pressure [A]"
FT2 = 10.7639          # sq ft per m2 (exact conversion)


def _size_dims(size):
    """'5.8 m ID x 17.4 m T/T (D)' -> (D, L) in m, or None"""
    m = re.search(r"([\d.]+) m ID x ([\d.]+) m", size or "")
    return (float(m.group(1)), float(m.group(2))) if m else None


def _vessel_area_m2(D, L):
    return math.pi * D * L + 2 * 1.084 * D * D        # D: shell + two 2:1 ellipsoidal heads (head area ~1.084 D2)


def _sheet(pkg, no): return next(s for s in pkg.sheets if s.no == no)


def _replace_text(sh, old, new):
    o, n = html.escape(old, quote=False), html.escape(new, quote=False)
    for i, e in enumerate(sh.p):
        if f">{o}</text>" in e: sh.p[i] = e.replace(f">{o}</text>", f">{n}</text>")


# ---- 1. relief schedule ------------------------------------------------------------------------------------
def relief(pkg):
    eqd = {r[0]: r for r in pkg.equip}
    n_fire = n_dust = 0
    out = []
    for r in pkg.relief:
        tag, prot, case, sheet = r[0], r[1], r[2], r[7]
        if re.search(r"dust explosion", case, re.I):
            r[6] = ("inputs (A, coal envelope): St1, Kst <= 220 bar m/s, Pmax <= 10 bar (Huescar Medina 2015, 1 m3 tests, grade B); petcoke and urea dust not measured; "
                    "vent-area equation (EN 14491 / NFPA 68) not obtained: not sized"); n_dust += 1
        elif re.search(r"fire", case, re.I) and (re.search(r"NH3|ammonia", prot + " " + case, re.I) or any(
                re.search(r"NH3|ammonia", e[1], re.I) and e[0] in prot.split() + [prot] for e in pkg.equip)):
            eq = next((e for e in pkg.equip if e[0] in prot.split() + [prot] and re.search(r"NH3|ammonia", e[1], re.I)), None) or \
                next((e for e in pkg.equip if e[-1] == sheet and re.search(r"NH3|ammonia", e[1], re.I)), None)
            D_L = _size_dims(eq[5]) if eq else None
            area = None
            if D_L: area = _vessel_area_m2(*D_L)
            elif eq and eq[0] == "T-501":
                V = float(re.search(r"([\d,]+) m3", eq[5]).group(1).replace(",", "")); Dt = math.sqrt(4 * V / (math.pi * 20.0)); area = math.pi * Dt * 20.0 + math.pi * Dt * Dt / 4
            if area:
                a_ft2 = area * FT2
                if a_ft2 > 2500: r[6] = f"screening (D): area {area:,.0f} m2 = {a_ft2:,.0f} sq ft -> {22.11 * a_ft2 ** 0.82:,.0f} SCFM air at 120 % set [{NH3_FIRE}]; pressure-vessel rule, extrapolation if atmospheric tank (A)"; n_fire += 1
                else: r[6] = f"area {a_ft2:,.0f} sq ft is below 2,500: Table H-36 values not extracted (gap); formula valid only above 2,500 sq ft"
        elif re.search(r"tube rupture|API|fire", case, re.I) and r[6].startswith("not sized"):
            r[6] = r[6] + "; gap: standard not obtained (API 520/521)"
    return n_fire, n_dust


# ---- 2. detector alarm set points ---------------------------------------------------------------------------
ALARM_RULES = [   # (service regex, old alarm regex, register text, drawing text); EH40/2005 Table 1 values (grade A)
    (r"NH3", r"25 ppm", "L 25 ppm (EH40 8-h WEL, D) / H 35 ppm (15-min STEL, D) / HH 150 ppm ESD (A; IDLH not read)", "L25/H35/HH150 ppm (D,A)"),
    (r"H2S", r"10 ppm|H 10", "L 5 ppm (EH40 8-h WEL, D) / H 10 ppm (15-min STEL, D) / HH 15 ppm ESD (A)", "L5/H10/HH15 ppm (D,A)"),
    (r"\bCO\b", r"30|100 ppm", "L 20 ppm (EH40 8-h WEL, D) / HH 100 ppm (15-min STEL, D)", "L20/HH100 ppm (D)"),
]


def alarms(pkg):
    n = 0
    for r in pkg.inst:
        if r[3] not in ("AT", "AAH", "AAHH"): continue
        svc, alarm = r[1], r[5]
        if "ppm" not in alarm: continue
        # an NH3/H2S/CO ppm alarm; do not touch CO2 (not read) or %LEL rows
        for sre, are, full, short in ALARM_RULES:
            if re.search(sre, svc) and not re.search(r"CO2", svc if sre == r"\bCO\b" else "") and re.search(are, alarm):
                old = alarm; r[5] = full; r[6] = "D (EH40/2005 T1) + A"
                _replace_text(_sheet(pkg, int(r[7])), old, short); n += 1; break
    return n


# ---- 3. per-sheet notes ---------------------------------------------------------------------------------------
NOTES = {
    "T-501": ["Containment: Fertilizers Europe survey of 22 refrigerated NH3 tanks: nearly all have secondary containment, >80 % full-height wall; take bund = 100 % of tank contents with impervious floor (A, rule not obtained).",
              "Rollover of aqueous/anhydrous layers can exceed PSV capacity and lift the shell: add rollover case; weak roof-to-shell weld preferred on new tanks (B).",
              "Commissioning purge: O2 below 4 %, then below 0.5 % before NH3 (B). Detector proof test every 6 months, bund visual check yearly (B).",
              "Fire-case relief: see the relief register (area 95); 1910.111 rule is for pressure vessels, extrapolation here (A)."],
    "MILL": ["Inerting basis: steam, CO2 or N2 must bring O2 to 15 vol % or less to stop a pulveriser fire (Babcock & Wilcox PSB 16, grade B); the A placeholder trip of 8 % O2 is below that and is kept.",
             "Dust data sheet required before vent sizing: volume, Kst, Pmax (20 L or larger apparatus), strength, opening pressure (HSE HSG103, grade A). Screening: coal St1, Kst <= 220, Pmax <= 10 bar (A).",
             "CO alarm levels and NFPA 69/85/8503 limits not obtained: gap. Finest mill cut governs Kst."],
    "O2": ["EIGA Doc 13/20 (grade A): impingement V <= 30 m/s at 0.3-1.5 MPa abs, P x V <= 45 MPa m/s at 1.5-10 MPa, 4.5 m/s at 10-20 MPa; 2x for non-impingement (to 200 C). O2 lines here are sized by the impingement curve.",
           "304/316 exemption pressures 1.38 MPa (3.18 mm) and 2.58 MPa (6.35 mm); Monel 400/copper/brass 20.68 MPa: use alloy at impingement points above exemption. Filter particles 150 micron or smaller.",
           "Cleaning: dry oil-free gas = dew point -40 C or lower and oil 0.5 mg/m3 or less; white-light grey-metal finish and UVA check; numeric residue limit (EIGA Doc 33) not fetched."],
    "S": ["Pyrophoric iron sulphide forms in closed steel dead-space chambers (low O2, moisture, H2S): no closed gauge chambers, stainless gauge pockets, vents kept open, periodic tank gas analysis (Association for the Study of Failure, 1991, grade B)."],
    "UREA": ["Carbamate leak (ARIA 29603): start-up after a long outage, mis-seated carbon-steel flange at the condenser bypass valve, about 5 t NH3 equivalent released. Any carbamate leak = shutdown; positive material check on bypass-valve flanges; carbamate containment to retention (B).",
             "H2 in the CO2 feed is a hazard here (HIAD urea explosion: passivation O2 + H2 in CO2 gave a flammable mix in the HP scrubber, oil traces the probable ignition): H2 analysis on CO2, O2 dosing limit, oil-free scrubber, design-to-contain (B)."],
    "GAS": ["Eastman Kingsport 2020 (CSB, grade A): loss of quench water and a stuck-open check valve let hot syngas backflow and burn at about 1,000 psi; the PHA wrongly assumed low level would trip the gasifier: loss of quench water is an explicit trip with independent flow measurement, check valves in the MI list.",
            "HIAD 214: burner flange leak with substituted stud-bolt material and an unassessed repair: verify flange bolt material in the burner MI (B)."],
    "ACID": ["Deer Park 2024 (IChemE, B): contractors opened a flange on a live acid-gas line: positive line marking, double isolation and H2S detection at acid-gas flanges; permit to work."],
    "DUSTU": ["Urea dust: Fertilizers Europe says no dust-explosion hazard (one private communication, grade C, no Kst); urea decomposes above 133 C releasing NH3. Dust protection is NOT removed on this basis; test or check GESTIS-DUST-EX (manual lookup needed)."],
}


def sheet_notes(pkg):
    by_tag = {e[0]: int(e[-1]) for e in pkg.equip}
    targets = []   # (sheet no, key)
    for t in ("T-501",): targets.append((by_tag[t], t))
    for t in ("F-101", "BF-101", "V-1001", "LH-1001", "IN-1001", "BN-1001"):
        if t in by_tag: targets.append((by_tag[t], "MILL"))
    for t in ("K-2002", "HD-2001"):
        if t in by_tag: targets.append((by_tag[t], "O2"))
    targets += [(301, "O2"), (302, "O2"), (209, "O2")]
    targets.append((by_tag["T-351"], "S"))
    for t in ("R-601", "E-601", "C-603", "C-601", "K-601A", "K-601B"):
        if t in by_tag: targets.append((by_tag[t], "UREA"))
    for t in ("R-101", "BR-131"):
        if t in by_tag: targets.append((by_tag[t], "GAS"))
    for t in ("C-302", "F-351", "D-301"):
        if t in by_tag: targets.append((by_tag[t], "ACID"))
    for t in ("G-601", "C-605", "BAG-901"):
        if t in by_tag: targets.append((by_tag[t], "DUSTU"))
    seen = {}
    for no, key in targets: seen.setdefault(no, [])
    for no, key in targets:
        if key not in seen[no]: seen[no].append(key)
    for no, keys in seen.items():
        sh = _sheet(pkg, no); y = 700
        section(sh, 1135, y - 4, 445, "Safety sources applied (Rev C1)")
        y += 36
        for k in keys:
            for line in NOTES[k]:
                if y > 936: break
                y = WRAP(sh, 1143, y, line, 72, 9, 11, bullet=True) + 2
    return len(seen)


# ---- 4. safety-basis sheets (area 95) ---------------------------------------------------------------------
def _doc_sheet(pkg, no, title, sub):
    sh = USheet(pkg, no, title, sub, None); sh.docs = True
    R(sh, 20, 84, 1560, 1010, "none", "#889", 1)
    return sh


def wtable(s, x, y, colw, rows, size=9, lh=11.5, pad=6, head=True):
    """table whose cells wrap to their column width (chars ~ px / (0.52 x size)); row height follows the tallest cell"""
    wrapped = [[textwrap.wrap(str(c), max(4, int((w - 8) / (size * 0.52)))) or [""] for c, w in zip(r, colw)] for r in rows]
    tw = sum(colw); yy = y
    for i, cells in enumerate(wrapped):
        h = max(len(c) for c in cells) * lh + pad
        if head and i == 0: R(s, x, yy, tw, h, "#e8eaf0", "none")
        elif i % 2 == 0: R(s, x, yy, tw, h, "#f6f7fa", "none")
        cx = x
        for c, w in zip(cells, colw):
            for k, line in enumerate(c): T(s, cx + 4, yy + 3 + size + k * lh, line, size, 700 if (head and i == 0) else 400)
            cx += w
        yy += h
    R(s, x, y, tw, yy - y, "none", "#9aa", 1)
    return yy


def _trunc(t, n): t = str(t); return t if len(t) <= n else t[:n - 1] + "..."


def sheets_relief(pkg):
    rows = sorted(pkg.relief, key=lambda r: (int(r[7]), r[0]))
    per = 38; n = math.ceil(len(rows) / per); out = []
    for k in range(n):
        sh = _doc_sheet(pkg, 951 + k, f"Safety basis  -  Relief design-basis register ({k+1} of {n})", "relief devices, cases and sizing status")
        y = section(sh, 20, 90, 1560, "29 CFR 1910.119(d)(3)(i)(D): process safety information must include relief system design and design basis (grade A). Loads are NOT sized; status says what is missing.")
        colw = [92, 44, 215, 250, 70, 270, 619]
        hdr = [("Tag", "Sht", "Protects", "Case", "Set bar g", "Destination", "Sizing status")]
        body = [(_trunc(r[0], 17), r[7], _trunc(r[1], 44), _trunc(r[2], 52), _trunc(r[3], 12), _trunc(r[5], 56), _trunc(r[6], 128)) for r in rows[k * per:(k + 1) * per]]
        table(sh, 20, y + 2, colw, hdr + body, rh=20.5, size=8.6)
        frame(sh, pkg.total); pkg.add_sheet(sh); out.append(sh)
    return n


def sheet_detectors(pkg):
    sh = _doc_sheet(pkg, 955, "Safety basis  -  Toxic gas detector alarm basis", "exposure limits applied to the detector instruments")
    y = section(sh, 20, 90, 1560, "Exposure limits (UK HSE EH40/2005 Table 1, grade A) and how the alarms are set")
    rows = [("Gas", "8-h WEL (low alarm)", "15-min STEL (high alarm)", "OSHA PEL cross-check (grade A)", "IDLH", "Rule applied in this package", "Detectors updated"),
            ("Ammonia", "25 ppm", "35 ppm", "50 ppm (NIOSH REL 25 TWA / 35 STEL)", "gap: cdc.gov blocked", "L at 8-h WEL (D), H at STEL (D), HH ESD stays 150 ppm (A)", ""),
            ("Hydrogen sulphide", "5 ppm", "10 ppm", "Z-2 not read", "gap", "L 5 (D), H 10 (D), HH ESD 15 ppm (A)", ""),
            ("Carbon monoxide", "20 ppm", "100 ppm", "50 ppm (NIOSH ceiling 200)", "gap", "L 20 (D), HH at STEL 100 (D)", ""),
            ("Carbon dioxide", "not read", "not read", "not read", "gap", "keep A values (0.5 / 1.5 vol %)", "0")]
    cnt = collections.Counter()
    for r in pkg.inst:
        if r[3] in ("AT", "AAH", "AAHH") and str(r[6]).startswith("D (EH40"):
            g = "Ammonia" if "25 ppm (EH40" in r[5] else "Hydrogen sulphide" if "H2S" in r[1] or "L 5 ppm" in r[5] else "Carbon monoxide"; cnt[g] += 1
    rows = [list(x) for x in rows]
    for x in rows[1:4]: x[6] = str(cnt[x[0]])
    y = wtable(sh, 20, y + 2, [150, 150, 170, 290, 160, 440, 200], rows, size=9.5, lh=12.5)
    y = section(sh, 20, y + 16, 1560, "What stays assumed or open")
    for t in ["HH (ESD) set points are assumed (A): IDLH and the 'Z-2' H2S ceiling/peak were not read (cdc.gov returned 403 and was not bypassed); detectors keep their 2oo2 or 2oo3 voting as drawn.",
              "CO2 detector set points are not from EH40 (the agent read NH3, H2S and CO only); they stay A. Hydrocarbon, O2-purity, dust and turbidity analysers are 'per vendor/site (gap)'.",
              "CO and O2 alarm levels in the coal circuit: NFPA 85/8503 not obtained (gap). HSG103 only says set the oxygen control level with a safety margin.",
              "Detector placement logic, response time and coverage need a gas-dispersion study and the project F&G philosophy (gap)."]:
        y = WRAP(sh, 30, y + 16, t, 200, 10.5, 14, bullet=True)
    frame(sh, pkg.total); pkg.add_sheet(sh)


def sheet_dust(pkg):
    sh = _doc_sheet(pkg, 956, "Safety basis  -  Dust explosion and inerting basis", "inputs for vent and inerting design; vent areas are not sized")
    y = section(sh, 20, 90, 1560, "Dust data read (screening inputs, tag A until the real dusts are tested)")
    rows = [("Dust", "Kst bar m/s", "Pmax bar", "Other", "Source (grade)", "Use in package"),
            ("Coal, literature range", "30-220", "5-10", "MEC 60-120 g/m3; all St1", "Huescar Medina et al., Fuel 151 (2015), Table 1, 1 m3 tests (B)", "envelope for area 10: St1, Kst <= 220, Pmax <= 10 bar (A)"),
            ("Kellingley / Colombian coal", "80 / 129", "8.2 / 8.5", "1 m3 apparatus", "same, Table 1 (B)", "cross-check"),
            ("Brown coal / Spanish / German lignite", "151 / 107 / 105", "10.0 / 8.8 / 8.7", "20 L sphere under-reads Pmax", "same (B)", "use 1 m3 values, not 20 L Pmax"),
            ("Coal dust (vendor page)", "85", "6.4", "St1, sample not stated", "explosiontesting.co.uk (C)", "cross-check only"),
            ("Petroleum coke", "no free value", "no free value", "-", "none found (gap)", "assumed = coal envelope; flag for test"),
            ("Urea", "not measured", "-", "'no dust-explosion hazard' (one private communication); decomposes > 133 C giving NH3", "Fertilizers Europe 2015 sect. 6.3 (C)", "dust protection NOT removed from granulation/bagging; unresolved")]
    y = wtable(sh, 20, y + 2, [250, 120, 110, 300, 400, 380], rows, size=9)
    y = section(sh, 20, y + 14, 1560, "Method points (HSE HSG103, grade A) and inerting")
    for t in ["Vent design needs vessel volume, Kst and Pmax from a 20 L or larger apparatus, vessel strength and panel opening pressure; St classes: St1 0-200, St2 200-300, St3 300-600 bar m/s; Table 1 values are not for direct design (paras 61-62, Appendix A).",
              "Inerting: the limiting oxygen concentration must be found experimentally with a safety margin and a reliable inert-gas supply (paras 25-29). Pulveriser fire: bring O2 to 15 vol % or less with steam, CO2 or N2; water only after inerting; do not open a mill with burning contents (Babcock & Wilcox PSB 16, B). The A placeholder trip of 8 % O2 is kept: it is stricter.",
              "Vent-area equations (EN 14491 / NFPA 68) and NFPA 69/85/8503 were not obtained: gap: standard not obtained. GESTIS-DUST-EX needs a manual browser lookup for coal, lignite, petroleum coke and urea (site reachable, scripted search failed).",
              "Package effect: the dust-explosion relief rows (EV-xxxxx) carry these inputs in the register and stay 'not sized'; area 10 needs the dust data sheet before any vent area is claimed."]:
        y = WRAP(sh, 30, y + 16, t, 205, 10.5, 14, bullet=True)
    n = sum(1 for r in pkg.relief if re.search("dust explosion", r[2], re.I))
    T(sh, 30, y + 26, f"Dust-explosion vent devices in the package: {n}", 11, 700)
    frame(sh, pkg.total); pkg.add_sheet(sh)


def sheet_oxygen(pkg):
    sh = _doc_sheet(pkg, 957, "Safety basis  -  Oxygen service: velocity check against the EIGA curves", "all oxygen gas lines in the package")
    y = section(sh, 20, 90, 1560, "EIGA Doc 13/20 (free, grade A): limits apply to the minimum flow area in normal operation (not relief); impingement curve to 200 C")
    o2 = [r for r in pkg.lines if re.search(r"\boxygen\b|\bO2\b", r[1], re.I) and not re.search(r"crude|LOX|liquid|CO2|N2|air", r[1], re.I) and r[5] == "gas"]
    rows = [("Line", "Service", "P bar abs", "T C", "v m/s (D)", "limit impingement", "limit non-impingement", "verdict", "Sheet")]
    bad = 0
    for r in o2:
        P = float(r[7]); v = float(r[10]); li = eiga_limit(P); ln = eiga_limit(P, False)
        ok = v <= li + 1e-9; bad += (not ok)
        rows.append((r[0], _trunc(r[1], 34), f"{P:g}", f"{float(r[6]):g}", f"{v:.1f}", f"{li:.1f}", f"{ln:.1f}", "within impingement limit" if ok else "EXCEEDS impingement limit", r[-1]))
    y = table(sh, 20, y + 2, [160, 300, 90, 70, 100, 150, 170, 290, 80], rows[:34], rh=21, size=9.2)
    y = section(sh, 20, y + 14, 1560, "Rules and exemptions read from the document")
    for t in ["Curves: impingement V = 30 m/s for 0.3-1.5 MPa abs; P x V = 45 MPa m/s for 1.5-10 MPa; V = 4.5 m/s for 10-20 MPa. Non-impingement: 60 m/s; P x V = 80; 8 m/s. Example: 4 MPa abs, carbon steel, impingement: 11.3 m/s.",
              "Exemption pressures (impingement points): 304/316 3.18 mm wall 1.38 MPa, 6.35 mm 2.58 MPa; Monel 400, copper, brass 20.68 MPa; Inconel 625 6.90 MPa. Filtration of particles 150 micron or smaller is a mitigation.",
              f"Package effect: O2 lines are sized by the impingement curve (pid_unit.St.vel_rule); {len(o2)} gas lines checked, {bad} exceed the limit after sizing. Cleaning: dry oil-free dew point -40 C or lower, oil 0.5 mg/m3 or less; UVA check; numeric residue limit (EIGA Doc 33) not fetched."]:
        y = WRAP(sh, 30, y + 16, t, 205, 10.5, 14, bullet=True)
    frame(sh, pkg.total); pkg.add_sheet(sh)
    return len(o2), bad


def sheet_incidents(pkg):
    sh = _doc_sheet(pkg, 958, "Safety basis  -  Incident lessons mapped to the sheets", "design changes or flags taken from public incident reports")
    y = section(sh, 20, 90, 1560, "Each lesson is applied as a note, a flag or a trip requirement on the sheets named; none changes a sized value")
    rows = [("Incident (source, grade)", "What happened", "Design response", "Sheets", "Status"),
            ("Eastman Kingsport gasifier fire, 29 Nov 2020 (CSB, A)", "corroded support cracked, water to the gasifier lost, stuck-open check valve, hot syngas backflow, fire at ~1,000 psi; PHA assumed low level would trip", "loss of quench water = explicit gasifier trip with independent flow measurement; check-valve testing in MI list", "301, 302, 321", "flagged in notes; trip logic to be confirmed by licensor"),
            ("Ammonia plant explosion, HIAD 214 (B)", "burner flange leak, substituted stud-bolt material, unassessed repair", "verify flange bolt material in the burner MI", "301, 302", "flagged"),
            ("Carbamate leak, ARIA 29603 (B)", "start-up after 5-week outage, mis-seated carbon-steel flange at condenser bypass, ~5 t NH3 equivalent, leak watched 10 h", "any carbamate leak = shutdown; positive material check on bypass flanges; containment to retention", "705-708", "flagged"),
            ("Urea scrubber explosion, HIAD (B)", "passivation O2 + H2 in CO2 feed gave flammable mix in HP scrubber after NH3/CO2 absorbed; oil traces probable ignition", "H2 analysis on CO2 (coal CO2 carries H2), O2 dosing limit, oil-free scrubber, design to contain", "701, 702, 705, 708", "flagged; H2 level in CO2 not computed (gap)"),
            ("Molten-sulphur tank fire, 1991 (shippai, B)", "pyrophoric iron sulphide in a closed gauge chamber ignited on opening", "no closed dead-space chambers, stainless gauge pockets, vents open, gas analysis", "524", "flagged"),
            ("Deer Park acid-gas flange, 2024 (IChemE, B)", "wrong flange opened on a live pressurised acid-gas line, 2 fatalities", "positive line marking, double isolation, H2S detection at flanges", "506, 517, 510", "flagged"),
            ("Refrigerated NH3 tanks survey (Fertilizers Europe, B)", "rollover can exceed PSV capacity; most tanks have secondary containment", "bund = 100 % contents (A), rollover case, weak roof weld, O2 purge limits, detector proof test", "617", "flagged; bund volume rule not obtained"),
            ("Pulveriser fires (B&W PSB 16, B)", "inerting must bring O2 to 15 vol % or less; do not open a burning mill", "mill-circuit O2 trip basis; kept stricter 8 % placeholder", "106-113", "flagged"),
            ("West Fertilizer (CSB, C)", "ammonium nitrate: not part of this plant", "none", "-", "not used")]
    wtable(sh, 20, y + 2, [290, 400, 410, 130, 330], rows, size=9)
    frame(sh, pkg.total); pkg.add_sheet(sh)


def sheet_gaps(pkg):
    sh = _doc_sheet(pkg, 959, "Safety basis  -  Open gaps (standards and data not obtained)", "what still blocks sized relief, detection and fire protection")
    y = section(sh, 20, 90, 1560, "Controlling standards are paywalled; free substitutes were used where they exist; the rest is 'gap: standard not obtained'")
    rows = [("Gap", "Needed", "Free substitute used", "Status"),
            ("Fire relief, process vessels (hydrocarbon, syngas, hot)", "API 520/521 wetted-area method, vapour load", "29 CFR 1910.111 for NH3-wetted vessels only", "open"),
            ("Tube rupture relief", "API 521 guidance, fluid properties, tube data", "none found (HSE CRR 136/1998 URL returned 404)", "open"),
            ("Blocked-outlet relief", "per-case loads", "1910.111: full rated capacity for NH3 pumps and compressors; hydrostatic relief between liquid-NH3 valves", "partly"),
            ("Common relief header / flare loads", "simultaneous load basis", "HSE COMAH relief page (principles, grade B)", "partly"),
            ("Dust vent areas", "EN 14491 / NFPA 68, measured Kst/Pmax", "HSG103 method, coal literature envelope", "partly"),
            ("Petcoke and urea dust data", "GESTIS-DUST-EX or tests", "none (manual lookup needed)", "open"),
            ("CO and O2 alarm levels, coal circuit", "NFPA 69/85/8503", "B&W 15 vol % O2 (B)", "partly"),
            ("IDLH and H2S ceiling values", "NIOSH pocket guide (cdc.gov blocked), OSHA Z-2", "EH40/2005 limits (A)", "partly"),
            ("Fire water, foam, detector placement", "OISD-STD-116/117 official PDF, NFPA", "snippet only: 4 hydrants/foam outlets plus 1 monitor (C)", "open"),
            ("NH3 water spray, vent scrubbing, bund volume rule", "IIAR, NFPA", "none", "open"),
            ("Claus furnace / waste-heat boiler explosions", "primary article", "snippet only (C)", "open"),
            ("Oxygen cleaning residue limit", "EIGA Doc 33", "Doc 13/20 dew point and oil limits (A)", "partly")]
    wtable(sh, 20, y + 2, [420, 420, 560, 160], rows, size=9.5, lh=12.5)
    frame(sh, pkg.total); pkg.add_sheet(sh)


def apply(pkg):
    nf, nd = relief(pkg)
    na = alarms(pkg)
    nn = sheet_notes(pkg)
    n_rel = sheets_relief(pkg)
    sheet_detectors(pkg); sheet_dust(pkg)
    no2, bad = sheet_oxygen(pkg)
    sheet_incidents(pkg); sheet_gaps(pkg)
    return dict(nh3_fire=nf, dust_rows=nd, alarms=na, noted_sheets=nn, relief_sheets=n_rel, o2_lines=no2, o2_over=bad)

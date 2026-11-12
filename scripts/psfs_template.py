#!/usr/bin/env python3
"""psfs_template.py - blank Process Safeguarding Flow Scheme (PSFS) template sheet, drawn with the same routine as the real sheets (urea_psfs.draw_unit_box).

One A3 sheet: a worked-example unit box with placeholder rows in the four required sections (A final safeguards, B capacity-determining components and
control-valve fail action, C mitigating systems, D interfaces), the editing rules from the public description of the PSFS, a review checklist that
mirrors the psfs_lint.py rules, and the sign-off block. Output: docs/pid/urea_detail/PSFS_TEMPLATE.html (print to PDF with headless Chrome).
Usage: python3 scripts/psfs_template.py [out.html]
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pid_unit import *
import urea_psfs as P, psfs_model as M


def example_unit():
    u = M.Unit(0)
    u.equip = [dict(tag="V-xxx", name="Equipment name", type="vessel / exchanger / compressor", sheet="000")]
    u.A_relief = [dict(tag="PSV-xxx01", set_bar_g="__", destination="flare header / atmosphere via silencer / closed drain", sizing_status="not sized: needs relief load", protects="V-xxx")]
    u.A_trips = [dict(tag="PAHH-xxx42", function="PAHH", alarm_trip="HH __ bar (below design and below the PSV set)", service="pressure high-high trip")]
    u.B_control = [dict(tag="PV-xxx11", fail_position="FO", service="pressure control, opens to flare (state spring action, stay-put, minimum stop)")]
    u.C_esd = [dict(tag="XV-xxx51", type="ball", fail_position="FC (ESD)", service="feed isolation on trip")]
    return u


RULES = [
    "A  Show every final safeguard of the unit: relief valves, rupture disks, thermal expansion valves (those on pumps and in cooling-water service may be omitted), and every",
    "    instrumented protective function against loss of containment. Each relief device carries set pressure, capacity and discharge destination. Never summarise as '+ n more'.",
    "B  Show every trip, control, bypass valve or restriction that, if inadvertently open, could pass more than 25 % of the relief device capacity, and the relief device capacity itself.",
    "    For each control valve shown, state spring action (FO / FC), stay-put device and minimum stop if fitted.",
    "C  Show the mitigating systems: ESD valves with spring action (FC / FO) and remotely operated valves installed for emergencies.",
    "D  Show the interfaces that matter to safeguarding: flare and relief headers, vents, drains, utilities supplied to or from other units.",
    "Edit the drawing at its source: change the register or the area module, rebuild, then run scripts/psfs_lint.py (--fix redraws the sheets from the registers).",
]
CHECK = [
    ("P01-P03  every relief device, ESD valve and trip of the unit is drawn in its box", "P05-P06  no tag drawn that is not in the registers; no tag drawn twice"),
    ("P04  every relief device has a recognised discharge destination", "P07, P09  every control valve has a fail action; every ESD valve is FC or FO"),
    ("P08  no truncation ('+ n more', '...')", "P10, P30  relief set and high-high trip not above the equipment design pressure"),
    ("P11-P13  every unit sheet has a box; text inside boxes; sheet has title and legend", "P20-P22  open gaps: capacity not sized, set by vendor, >25 % screen not performed"),
]


def build(out):
    pkg = Pkg("VS-CU", "Process Safeguarding Flow Scheme template", "Template: placeholders only, no design content", rev="T0")
    sh = P.new_sheet(pkg, 970, "Safeguarding  -  PSFS TEMPLATE (blank, with editing rules and review checklist)", "template"); sh.psfs_template = True
    u = example_unit(); h = P.draw_unit_box(sh, P.X0, P.TOP, u, title="V-xxx  Equipment name (tag and name of the unit's main item)", subtitle="sheet nnn  |  equipment type  (one box per unit sheet)")
    b = M.Unit(0); b.equip = [dict(tag="________", name="________________", type="________", sheet="___")]
    b.A_relief = [dict(tag="PSV-________", set_bar_g="___", destination="flare / vent / drain (choose)", sizing_status="not sized", protects="")] * 2
    b.A_trips = [dict(tag="________", function="___", alarm_trip="HH ___ bar", service="________")] * 2
    b.B_control = [dict(tag="PV-________", fail_position="__", service="________")]
    b.C_esd = [dict(tag="XV-________", type="____", fail_position="__ (ESD)", service="________")]
    P.draw_unit_box(sh, P.X0, P.TOP + h + 30, b, title="BLANK FORM  tag ________  name ________________", subtitle="sheet ___  |  copy this box once per unit sheet")
    x0 = P.X0 + P.COLW + 30
    section(sh, x0, P.TOP, 1560 - P.COLW - 30 + 20 - 30 + 10, "How to edit a PSFS (public description of the Safeguarding Memorandum, section 8)")
    for i, ln in enumerate(RULES): T(sh, x0 + 6, P.TOP + 42 + i * 17, ln, 9.2, 700 if ln[:1] in "ABCD" else 400)
    y2 = P.TOP + 42 + len(RULES) * 17 + 20
    section(sh, x0, y2, 1560 - P.COLW - 30 + 20 - 30 + 10, "Review checklist (each line is a rule of scripts/psfs_lint.py)")
    for i, (l, r) in enumerate(CHECK): T(sh, x0 + 6, y2 + 42 + i * 17, l, 9.2); T(sh, x0 + 6 + 560, y2 + 42 + i * 17, r, 9.2)
    y3 = y2 + 42 + len(CHECK) * 17 + 20
    section(sh, x0, y3, 1560 - P.COLW - 30 + 20 - 30 + 10, "Sign-off")
    for i, (a, b) in enumerate((("Prepared (process engineer)", "name / date"), ("Instrumented functions (control engineer)", "name / date"), ("Reviewed (safety / HAZOP leader)", "name / date"), ("Revision", "__  reason: ______________________"))):
        T(sh, x0 + 6, y3 + 42 + i * 22, a, 9.5, 700); T(sh, x0 + 330, y3 + 42 + i * 22, b + "  ______________________", 9.5, 400, fill=GREY)
    P.legend(sh); frame(sh, 1); pkg.add_sheet(sh); pkg.total = 1
    write_html(pkg.sheets, out, "PSFS template", previews=False)
    return pkg, sh


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "docs/pid/urea_detail/PSFS_TEMPLATE.html"
    pkg, sh = build(out); print("wrote", out)

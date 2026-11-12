"""psfs_model.py - the content model of a Process Safeguarding Flow Scheme (PSFS), built from the package registers.

Required PSFS content (public description, enggcyclopedia.com 'Safeguarding Memorandum', section 8; ISO 15926-4 definition at posccaesar.org):
  A  final safeguards          relief valves, rupture disks, thermal expansion valves (pump and cooling-water ones may be omitted),
                               instrumented protective functions against loss of containment
  B  capacity-determining      trip / control / bypass valves and restrictions that, opened inadvertently, give relief flow above 25 % of the
                               relief device capacity; the relief device capacity; for each control valve its spring action
  C  mitigating systems        ESD valves with spring action, remotely operated valves installed for emergencies
  D  interfaces                relevant interfaces with other units and systems incl. utilities, flare and relief systems
The defining standard's symbols and layout are proprietary and are NOT used. Nothing here is added to the design: every row comes from the registers.
"""
import re, csv, os, collections

COLS = dict(
    relief=["tag", "protects", "case", "set_bar_g", "set_tag", "destination", "sizing_status", "sheet"],
    valves=["tag", "type", "service", "line_no", "size_in", "fail_position", "sheet"],
    inst=["tag", "service", "equipment", "function", "range", "alarm_trip", "set_tag", "sheet"],
    equip=["tag", "name", "type", "operating", "design", "size", "material", "basis_tag", "sheet"])

TRIP_FUNCS = {"LAHH", "LALL", "TAHH", "PAHH", "PALL", "TALL", "VAHH", "PDAHH", "FALL", "BSLL", "XA", "PAH"}
DETECTOR_FUNCS = {"AT", "AAH", "AAHH"}
DEST_WORDS = (("flare", "flare"), ("atmosphere", "atmosphere"), ("safe", "safe place"), ("drain", "closed drain"), ("slop", "slop"), ("retention", "retention"),
              ("scrubber", "scrubber"), ("absorber", "scrubber"), ("vent", "vent"), ("BOG", "BOG header"), ("KO", "KO drum"), ("open air", "atmosphere"), ("silencer", "atmosphere"))
TAG = re.compile(r"\b[A-Z]{1,5}-\d{4,6}[A-Z]?\b")


def _row(kind, r):
    if isinstance(r, dict): return {k: ("" if r.get(k) is None else str(r.get(k))) for k in COLS[kind]}
    return {k: ("" if v is None else str(v)) for k, v in zip(COLS[kind], r)}


class Regs:
    """the four registers the PSFS is built from, as lists of dicts keyed by the CSV column names"""
    def __init__(self, relief, valves, inst, equip):
        self.relief, self.valves, self.inst, self.equip = relief, valves, inst, equip

    @classmethod
    def from_pkg(cls, pkg):
        return cls(*[[_row(k, r) for r in getattr(pkg, k)] for k in ("relief", "valves", "inst", "equip")])

    @classmethod
    def from_csv(cls, d):
        files = dict(relief="RELIEF_SCHEDULE.csv", valves="VALVE_LIST.csv", inst="INSTRUMENT_INDEX.csv", equip="EQUIPMENT_LIST.csv")
        return cls(*[[_row(k, r) for r in csv.DictReader(open(os.path.join(d, files[k])))] for k in ("relief", "valves", "inst", "equip")])


def dest_class(d):
    """normalised discharge destination, or '' when the text names none of the recognised destinations"""
    for k, v in DEST_WORDS:
        if k.lower() in str(d).lower(): return v
    return ""


def is_trip(i):
    return i["function"] in TRIP_FUNCS or (re.search(r"trip", i["alarm_trip"], re.I) and i["function"] not in DETECTOR_FUNCS)


def first_number(s):
    m = re.search(r"-?\d+(?:\.\d+)?", str(s)); return float(m.group()) if m else None


def design_bar_g(equip_row):
    """design pressure in bar g where the equipment register states one as 'N bar g' (else None)"""
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*bar\s*g", equip_row["design"]); return float(m.group(1)) if m else None


class Unit:
    """one unit sheet of the package and its safeguards"""
    def __init__(self, sheet):
        self.sheet = sheet
        self.equip, self.A_relief, self.A_trips, self.B_control, self.C_esd, self.det = [], [], [], [], [], []

    @property
    def interfaces(self):   # D: discharge destinations of the unit's relief devices
        out = collections.OrderedDict()
        for r in self.A_relief: out.setdefault(dest_class(r["destination"]) or "UNKNOWN", []).append(r["tag"])
        return out

    @property
    def tags(self):
        return ({r["tag"] for r in self.A_relief} | {i["tag"] for i in self.A_trips} | {v["tag"] for v in self.B_control} | {v["tag"] for v in self.C_esd})


def build(regs, first_safety_sheet=950):
    """unit sheet number -> Unit. Sheets at or above first_safety_sheet (the safety / PSFS documentation sheets) are not units."""
    U = collections.OrderedDict()
    for e in sorted(regs.equip, key=lambda r: int(r["sheet"])):
        if int(e["sheet"]) >= first_safety_sheet: continue
        U.setdefault(int(e["sheet"]), Unit(int(e["sheet"]))).equip.append(e)
    for r in regs.relief:
        if int(r["sheet"]) in U: U[int(r["sheet"])].A_relief.append(r)
    for i in regs.inst:
        n = int(i["sheet"])
        if n not in U: continue
        if is_trip(i): U[n].A_trips.append(i)
        elif i["function"] in DETECTOR_FUNCS: U[n].det.append(i)
    for v in regs.valves:
        n = int(v["sheet"])
        if n not in U: continue
        if "ESD" in v["fail_position"] or re.search(r"\bESD\b|emergency", v["type"] + " " + v["service"], re.I): U[n].C_esd.append(v)
    # rule B: control valves on a sheet that has a relief device (their fail action sets the relief case); collected last so A_relief is complete
    for n, u in U.items():
        u.B_control = [v for v in regs.valves if int(v["sheet"]) == n and v["type"] == "control" and u.A_relief and v not in u.C_esd]
    return U

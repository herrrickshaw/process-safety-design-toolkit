"""Plant model ingestion: PFS/PFD and HMB stream tables, P&ID registers, and Proteus (DEXPI) XML, into one dictionary.

Accepted inputs (each as an inline list of dicts or a CSV path; numbers are parsed, blanks become None):
    units           tag, type, design_P_kpag, design_T_C, mdmt_C, volume_m3, D_m, L_m, orientation, level_pct, latent_heat_kJ_kg, ...
    streams         id, from, to, phase, T_C, P_kpag, mass_kg_h, mw, k, Z, rho_kg_m3, components (JSON text or dict), H_kW   (PFS / HMB)
    lines           line_no, from, to, nps, id_mm, length_m, design_P_kpag, fluid                          (P&ID line list)
    relief_devices  tag, unit, type, set_kpag, orifice | area_mm2, outlet_to, inlet_line                   (PSV / BDV / rupture disk register)
    instruments     tag, type, unit, loop, function, group, voting
    valves          tag, type, unit, line, fail
    exchangers      tag, hp_unit, lp_unit, tube_id_mm, hp_design_kpag, lp_design_kpag, phase, ...
Proteus XML (the ProteusXML / DEXPI exchange format, schema 4.2): equipment with design pressure and temperature elements, nozzles, piping
network segments and connections, piping components (valves, relief devices) and process instrumentation functions are read. Element names
were taken from the published Proteus 4.2 XSD; the parser is a small stdlib reader tested on a synthetic file with that structure, NOT
validated against real vendor exports, and pressure units in the file do not say gauge or absolute (gauge is assumed and noted).
Not used: pyDEXPI (AGPL-3.0; incompatible with copying into this MIT project).
"""
from __future__ import annotations

import csv
import json
import os
import xml.etree.ElementTree as ET

from . import relief

# ASME B36.10 schedule 40 inside diameters (mm), as commonly tabulated: verify against your pipe class before use.
SCH40_ID_MM = {2: 52.5, 3: 77.9, 4: 102.3, 6: 154.1, 8: 202.7, 10: 254.5, 12: 303.2}
_PRESSURE_TO_KPA = {"kpa": 1.0, "bar": 100.0, "mpa": 1000.0, "psi": 6.894757, "psig": 6.894757, "kpag": 1.0, "barg": 100.0, "pa": 0.001}
SECTIONS = ("units", "streams", "lines", "relief_devices", "instruments", "valves", "exchangers")


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    if s == "":
        return None
    try:
        return float(s) if any(c in s for c in ".eE") else int(s)
    except ValueError:
        return s


def read_csv(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = []
        for r in csv.DictReader(fh):
            d = {k.strip(): _num(v) for k, v in r.items() if k}
            if isinstance(d.get("components"), str):
                try:
                    d["components"] = json.loads(d["components"])
                except ValueError:
                    d["components"] = {}
            rows.append(d)
        return rows


def _section(v, base):
    if isinstance(v, str):
        return read_csv(v if os.path.isabs(v) or not base else os.path.join(base, v))
    return [dict(x) for x in (v or [])]


def load(spec: dict, base_dir: str | None = None) -> dict:
    m = {k: _section(spec.get(k), base_dir) for k in SECTIONS}
    m["name"] = spec.get("name", "plant")
    m["notes"] = []
    if spec.get("proteus_xml"):
        p = spec["proteus_xml"]
        px = from_proteus_xml(p if os.path.isabs(p) or not base_dir else os.path.join(base_dir, p))
        known = {u["tag"] for u in m["units"]}
        for u in px["units"]:
            if u["tag"] not in known:
                m["units"].append(u)
        for k in ("lines", "relief_devices", "instruments", "valves"):
            m[k] += px[k]
        m["notes"] += px["notes"]
    for ln in m["lines"]:
        if not ln.get("id_mm") and ln.get("nps") in SCH40_ID_MM:
            ln["id_mm"] = SCH40_ID_MM[ln["nps"]]
            ln["id_note"] = "ID from the schedule 40 table (assumed schedule)"
    for d in m["relief_devices"]:
        if not d.get("area_mm2") and d.get("orifice") in relief.API526_ORIFICES_MM2:
            d["area_mm2"] = relief.API526_ORIFICES_MM2[d["orifice"]]
    return m


def validate(m: dict) -> list[str]:
    errs = []
    tags = [u["tag"] for u in m["units"]]
    if len(tags) != len(set(tags)):
        errs.append("duplicate unit tag")
    t = set(tags)
    for s in m["streams"]:
        for e in ("from", "to"):
            if s.get(e) not in (None, "", "feed", "product", "battery_limit") and s.get(e) not in t:
                errs.append(f"stream {s.get('id')}: {e} '{s.get(e)}' is not a unit")
    for coll in ("relief_devices", "instruments", "valves"):
        for d in m[coll]:
            if d.get("unit") and d["unit"] not in t:
                errs.append(f"{coll} {d.get('tag')}: unit '{d['unit']}' not in units")
    return errs


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _val(el, name):
    for c in el:
        if _local(c.tag) == name:
            v, u = c.get("Value"), (c.get("Units") or "").strip().lower()
            if v is None:
                return None, u
            return float(v), u
    return None, ""


def _kpa(v, u):
    if v is None:
        return None
    return v * _PRESSURE_TO_KPA.get(u, 1.0)


def from_proteus_xml(src: str) -> dict:
    root = ET.fromstring(src) if src.lstrip().startswith("<") else ET.parse(src).getroot()
    out = {"units": [], "lines": [], "relief_devices": [], "instruments": [], "valves": [],
           "notes": ["Proteus XML: pressure units carry no gauge/absolute flag; values treated as gauge; tags and classes as written in the file"]}
    ids = {}
    for el in root.iter():
        if el.get("ID") and el.get("TagName"):
            ids[el.get("ID")] = el.get("TagName")
    for el in root.iter():
        n = _local(el.tag)
        tag, cls = el.get("TagName"), el.get("ComponentClass") or ""
        if n == "Equipment" and tag:
            p, pu = _val(el, "MaximumDesignPressure")
            t, tu = _val(el, "MaximumDesignTemperature")
            tmin, _ = _val(el, "MinimumDesignTemperature")
            u = {"tag": tag, "type": cls or "equipment", "source": "proteus"}
            if p is not None:
                u["design_P_kpag"] = _kpa(p, pu)
            if t is not None:
                u["design_T_C"] = t - 273.15 if tu in ("k", "kelvin") else t
            if tmin is not None:
                u["mdmt_C"] = tmin - 273.15 if tu in ("k", "kelvin") else tmin
            out["units"].append(u)
        elif n == "PipingNetworkSegment" and (tag or el.get("ID")):
            ln = {"line_no": tag or el.get("ID"), "source": "proteus"}
            nd, _ = _val(el, "NominalDiameter")
            idd, _ = _val(el, "InsideDiameter")
            dp, du = _val(el, "MaximumDesignPressure")
            if nd:
                ln["nps_mm"] = nd
            if idd:
                ln["id_mm"] = idd
            if dp is not None:
                ln["design_P_kpag"] = _kpa(dp, du)
            conns = [c for c in el if _local(c.tag) == "Connection"]
            for c in conns:
                for k, dst in (("FromID", "from"), ("ToID", "to")):
                    v = c.get(k)
                    if v:
                        ln[dst] = ids.get(v, v).split("->")[0]
            out["lines"].append(ln)
        elif n == "PipingComponent" and tag:
            cl = cls.lower()
            rec = {"tag": tag, "class": cls, "source": "proteus"}
            if "relief" in cl or "safety" in cl:
                out["relief_devices"].append(dict(rec, type="PSV"))
            elif "check" in cl:
                out["valves"].append(dict(rec, type="check"))
            elif "valve" in cl:
                out["valves"].append(dict(rec, type="valve"))
        elif n == "ProcessInstrumentationFunction" and tag:
            out["instruments"].append({"tag": tag, "type": tag.split("-")[0].upper(), "class": cls, "source": "proteus"})
    return out

"""Step 6 - risk mitigation: apply candidate safeguards to a copy of the study, re-run, and rank by risk reduction and ALARP CBA.

A measure is {"name", "capex", "opex_per_yr", "changes": [...]}. Supported changes (all keys optional except "target"):
  {"target": "section",   "id": "S1" | "*", "set": {...}, "multiply": {...}}     e.g. smaller isolatable inventory (ESD/SDV),
                                                                                     bund area, release height
  {"target": "frequency", "section": "S1" | "*", "hole": "rupture" | "*", "factor": 0.1}   e.g. an added IPL (PFD), inspection
  {"target": "ignition",  "set": {"factor": 0.5}}                                  ignition control / hazardous-area upgrade
  {"target": "population" | "receptors", "name": "Control room", "set"/"multiply": {...}}   relocation, occupancy, blast-rated building
  {"target": "conventions", "set": {"thermal_s": 10}}                             e.g. escape routes / shelter (justify!)
  {"target": "indoor_vulnerability", "set": {"vce": 0.05}}
"""
from __future__ import annotations

import copy


def _apply_dict(d: dict, ch: dict):
    for k, v in ch.get("set", {}).items():
        d[k] = v
    for k, v in ch.get("multiply", {}).items():
        d[k] = d[k] * v


def apply(study: dict, measure: dict) -> dict:
    s = copy.deepcopy(study)
    for ch in measure["changes"]:
        t = ch["target"]
        if t == "section":
            hit = [sec for sec in s["sections"] if ch.get("id", "*") in ("*", sec["id"])]
            if not hit:
                raise KeyError(f"measure {measure['name']!r}: no section {ch.get('id')!r}")
            for sec in hit:
                _apply_dict(sec, ch)
        elif t == "frequency":
            for sec in s["sections"]:
                if ch.get("section", "*") in ("*", sec["id"]):
                    ff = sec.setdefault("frequency_factors", {})
                    h = ch.get("hole", "*")
                    ff[h] = ff.get(h, 1.0) * ch["factor"]
            for x in s.get("extra_scenarios", []):
                if ch.get("section", "*") in ("*", x["section"]) and ch.get("hole", "*") in ("*", x.get("hole", "user")):
                    x["ipl_pfds"] = x.get("ipl_pfds", []) + [ch["factor"]]
        elif t == "ignition":
            _apply_dict(s.setdefault("ignition", {}), ch)
        elif t in ("population", "receptors"):
            hit = [p for p in s.get(t, []) if p["name"] == ch["name"]]
            if not hit:
                raise KeyError(f"measure {measure['name']!r}: no {t} entry {ch['name']!r}")
            for p in hit:
                _apply_dict(p, ch)
        elif t in ("conventions", "indoor_vulnerability"):
            _apply_dict(s.setdefault(t, {}), ch)
        else:
            raise ValueError(f"unknown change target {t!r}")
    return s

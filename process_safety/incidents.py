"""Incident register built from US Chemical Safety Board investigation pages (`data/incidents.json`).

Each record carries the facts the CSB page states (date, place, final report date, deaths where stated, an example recommendation)
and the toolkit's own mapping to modules and to the design review steps of `docs/DESIGN_AWARENESS.md`. It is a reading list for
designers, not a statistical dataset: 17 selected investigations, US only, chosen because they map to toolkit modules.
"""
from __future__ import annotations

import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "data", "incidents.json")
_CACHE: dict | None = None


def _data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def incidents() -> list[dict]:
    return list(_data()["incidents"])


def search(text=None, module=None, step=None, sector=None, year=None) -> list[dict]:
    out = []
    for i in incidents():
        if module and module not in i["modules"]:
            continue
        if step and step not in i["design_steps"]:
            continue
        if sector and sector.lower() not in i["sector"].lower():
            continue
        if year and not i["date"].startswith(str(year)):
            continue
        if text and text.lower() not in " ".join([i["name"], i["lesson"], i["recommendation"], i["sector"], i["location"]]).lower():
            continue
        out.append(i)
    return sorted(out, key=lambda i: i["date"])


def markdown() -> str:
    d = _data()
    inc = sorted(d["incidents"], key=lambda i: i["date"])
    lines = ["# Incident register (CSB investigations)", "",
             f"Generated from `process_safety/data/incidents.json` (compiled {d['compiled']}). {len(inc)} investigations selected because they map to toolkit modules; US only.",
             d["note"] + ". Regenerate: `python -m process_safety incidents --markdown > docs/INCIDENTS.md`.", "",
             "Deaths and injuries are shown only where the CSB page text stated them (blank = not stated in the text read). Recommendations are paraphrased from the first recommendation shown on the page; read the report for the full set.", "",
             "| Date | Incident | Place | Deaths | Injured | Example recommendation | Design lesson | Modules | Steps | Source |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i in inc:
        lines.append(f"| {i['date']} | {i['name']} | {i['location']} | {'' if i['deaths'] is None else i['deaths']} | {'' if i['injured'] is None else i['injured']} | {i['recommendation']} | {i['lesson']}{' (' + i['note'] + ')' if i['note'] else ''} | {', '.join(i['modules'])} | {', '.join(map(str, i['design_steps']))} | [CSB]({i['source']}) |")
    return "\n".join(lines) + "\n"

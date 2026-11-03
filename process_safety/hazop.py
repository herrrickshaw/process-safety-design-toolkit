"""HAZOP worksheet generator: node x parameter x guideword deviations with generic cause/consequence/safeguard prompts -> CSV (opens in Excel).

Method basis: guideword approach of IEC 61882 / CCPS (No/More/Less/As well as/Part of/Reverse/Other than). The prompts are generic
checklists from common practice, not text of any standard; they speed up the workshop but do NOT replace a facilitated team review
with P&IDs, cause-and-effect, and site experience.
"""
from __future__ import annotations

import csv

GUIDEWORDS = ["No", "More", "Less", "As well as", "Part of", "Reverse", "Other than"]

DEVIATIONS = {
    "Flow": ["No", "More", "Less", "Reverse", "As well as", "Other than"],
    "Pressure": ["More", "Less"],
    "Temperature": ["More", "Less"],
    "Level": ["No", "More", "Less"],
    "Composition": ["As well as", "Part of", "Other than"],
    "Phase": ["Other than"],
    "Reaction": ["More", "Less", "No", "Other than"],
    "Utilities": ["No", "Less"],
    "Operation/Maintenance": ["Other than", "Part of"],
}

CAUSES = {
    ("Flow", "No"): ["Line blocked / valve closed (manual or failed)", "Pump or compressor trip", "Control valve fails closed", "Source empty / loss of suction", "Line rupture upstream"],
    ("Flow", "More"): ["Control valve fails open", "Bypass opened", "Pump runs out on curve", "Downstream pressure loss", "Wrong set point"],
    ("Flow", "Less"): ["Partial blockage / fouling", "Pump wear or low speed", "Valve partly closed", "Strainer plugged"],
    ("Flow", "Reverse"): ["Check valve failure", "Pressure in downstream higher than upstream", "Pump trip with high downstream pressure"],
    ("Flow", "As well as"): ["Leaking exchanger tube (cross-contamination)", "Air ingress", "Slugs / carry-over"],
    ("Flow", "Other than"): ["Wrong material delivered", "Misrouting by wrong valve line-up"],
    ("Pressure", "More"): ["Blocked outlet", "Gas breakthrough", "Thermal expansion of blocked-in liquid", "External fire", "Reaction runaway", "Tube rupture", "Surge / water hammer"],
    ("Pressure", "Less"): ["Vacuum from cooling/condensation or pump-out", "Vent blocked", "Leak or loss of containment", "Compressor suction starved"],
    ("Temperature", "More"): ["Loss of cooling/reflux", "Fouled exchanger", "Fire", "Heater control failure", "Exothermic reaction"],
    ("Temperature", "Less"): ["Loss of heating", "Cold feed", "Joule-Thomson cooling on depressuring", "Ambient low (freezing, hydrates, wax)"],
    ("Level", "No"): ["Outflow exceeds inflow", "Level control failure", "Gas blow-by into downstream"],
    ("Level", "More"): ["Inflow exceeds outflow", "Outlet blocked", "Level instrument failure", "Carry-over / overfill"],
    ("Level", "Less"): ["Outlet valve fails open", "Leak", "Inflow reduced"],
    ("Composition", "As well as"): ["Contamination (water, air, catalyst, oil)", "Back-flow", "Utility ingress"],
    ("Composition", "Part of"): ["Incomplete reaction/separation", "Wrong ratio / metering failure"],
    ("Composition", "Other than"): ["Wrong charge", "Unplanned side reaction"],
    ("Phase", "Other than"): ["Flashing across control valve", "Condensation in gas line", "Solids / hydrate formation"],
    ("Reaction", "More"): ["Cooling failure", "Catalyst/initiator overdose", "Accumulation of reactant then sudden onset", "Agitator failure"],
    ("Reaction", "Less"): ["Low temperature (accumulation)", "Catalyst deficiency", "Poor mixing"],
    ("Reaction", "No"): ["No initiation", "Inhibitor present"],
    ("Reaction", "Other than"): ["Side or decomposition reaction", "Wrong raw material"],
    ("Utilities", "No"): ["Power / instrument air / steam / cooling-water failure", "Nitrogen supply lost"],
    ("Utilities", "Less"): ["Reduced utility header pressure", "Fouling"],
    ("Operation/Maintenance", "Other than"): ["Wrong sequence", "Isolation not proven", "Permit not followed", "Human error"],
    ("Operation/Maintenance", "Part of"): ["Step omitted", "Incomplete purge / drain"],
}

COLUMNS = ["Node", "Design intent", "Parameter", "Guideword", "Deviation", "Causes (prompts)", "Consequences", "Safeguards", "S", "L", "Risk",
           "Recommendations", "Action by", "Status"]


def generate(node: str, design_intent: str = "", parameters: list[str] | None = None) -> list[dict]:
    rows = []
    for param in parameters or list(DEVIATIONS):
        for gw in DEVIATIONS[param]:
            rows.append({"Node": node, "Design intent": design_intent, "Parameter": param, "Guideword": gw,
                         "Deviation": f"{gw} {param.lower()}", "Causes (prompts)": "; ".join(CAUSES.get((param, gw), [])),
                         "Consequences": "", "Safeguards": "", "S": "", "L": "", "Risk": "", "Recommendations": "", "Action by": "", "Status": "open"})
    return rows


def to_csv(rows: list[dict], path: str) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:  # BOM so Excel reads UTF-8
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    return len(rows)

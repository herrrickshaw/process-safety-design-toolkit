"""Step 1 - hazard identification: HAZID checklist register, HAZOP worksheets per section (reuses hazop.py), and the
loss-of-containment (LOC) scenario register that feeds the QRA.

The HAZID guide-categories are a generic checklist in the style of ISO 17776 / common HAZID practice (external, natural,
process, utilities, human, security, simultaneous operations); they prompt a facilitated team review and do not replace it.
HAZOP deviations that can end in loss of containment are tagged so the team can trace each LOC scenario back to its causes;
any cause that is not covered by the generic parts-count frequency (e.g. overpressure with a failed PSV) should be added as an
`extra_scenarios` entry with a fault tree or LOPA frequency.
"""
from __future__ import annotations

import csv

from .. import hazop

HAZID_CHECKLIST = {
    "Natural / environmental": ["Seismic", "Flooding / storm surge", "Lightning", "Extreme heat / cold", "Cyclone / high wind", "Subsidence"],
    "External / third party": ["Vehicle impact", "Dropped objects / lifting", "Neighbouring facility (domino)", "Aircraft", "Pipeline third-party damage"],
    "Process / loss of containment": ["Overpressure", "Underpressure / vacuum", "Overfill", "Brittle fracture / low temperature", "Corrosion / erosion",
                                       "Vibration / fatigue", "Runaway reaction", "Thermal expansion of trapped liquid"],
    "Ignition / fire / explosion": ["Hot surfaces", "Electrical (area classification)", "Static", "Hot work", "Vehicles in hazardous areas"],
    "Toxic / asphyxiant": ["H2S / toxic gas", "Nitrogen / CO2 asphyxiation", "Confined-space entry"],
    "Utilities": ["Power failure", "Instrument air failure", "Cooling water failure", "Fire water availability"],
    "Human / organisational": ["Operator error", "Maintenance isolation", "Permit to work", "Shift handover", "Competence"],
    "Security": ["Sabotage / unauthorised access", "Cyber attack on control systems"],
    "Simultaneous operations": ["Construction alongside operation", "Loading during maintenance"],
}

LOC_DEVIATIONS = {("Pressure", "More"), ("Pressure", "Less"), ("Temperature", "More"), ("Temperature", "Less"), ("Level", "More"),
                  ("Flow", "Reverse"), ("Reaction", "More"), ("Operation/Maintenance", "Other than"), ("Operation/Maintenance", "Part of")}

HAZID_COLUMNS = ["Section", "Category", "Hazard", "Applicable (Y/N)", "Threat / cause", "Consequence", "Existing safeguards", "Action", "Owner"]


def hazid_register(sections: list[dict]) -> list[dict]:
    return [{"Section": s["id"] + " " + s.get("name", ""), "Category": cat, "Hazard": h, "Applicable (Y/N)": "", "Threat / cause": "",
             "Consequence": "", "Existing safeguards": "", "Action": "", "Owner": ""}
            for s in sections for cat, hz in HAZID_CHECKLIST.items() for h in hz]


def hazop_rows(sections: list[dict]) -> list[dict]:
    rows = []
    for s in sections:
        for r in hazop.generate(f"{s['id']} {s.get('name', '')}", s.get("design_intent", "")):
            r["Consequences"] = "Potential loss of containment -> see QRA LOC register" if (r["Parameter"], r["Guideword"]) in LOC_DEVIATIONS else ""
            rows.append(r)
    return rows


def write_csv(rows: list[dict], path: str, columns: list[str] | None = None) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=columns or list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return len(rows)

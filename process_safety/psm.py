"""Process safety management (PSM): OSHA 29 CFR 1910.119 elements, applicability test, due-date tracking, AIGA 99 / CCPS RBPS crosswalk,
and a maturity-scored gap assessment.

VERIFIED against the primary text (osha.gov/laws-regs/regulations/standardnumber/1910/1910.119 and ...AppA, fetched 2026-11-03):
the 14 elements (c)-(p); PHA update/revalidation at least every 5 years; operating procedures certified annually; refresher training at
least every 3 years; incident investigation started within 48 h, reports retained 5 years; compliance audit at least every 3 years with
the two latest reports retained; mechanical-integrity inspection frequency per manufacturers' recommendations and good engineering
practice; threshold quantities in data/osha_psm_appendix_a.json and the 10,000 lb flammable rule with its two exemptions.
NOT regulatory advice: OSHA is US law; in India the equivalent duties sit across MSIHC 1989, Chemical Accidents Rules 1996,
Petroleum Rules 2002, Factories Act etc. (see docs/PSM_FRAMEWORKS.md). The crosswalk and gap scoring are the author's aids.
"""
from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from importlib import resources

LB_PER_KG = 2.2046226218

# id: (paragraph, title, verified requirement/cadence note)
OSHA_ELEMENTS = {
    "c": ("1910.119(c)", "Employee participation", "written plan of action; consult employees and their representatives on PHA and other elements; give access to PHA and PSM information"),
    "d": ("1910.119(d)", "Process safety information", "compile hazards of chemicals, process technology and equipment information before conducting the PHA"),
    "e": ("1910.119(e)", "Process hazard analysis", "team-based PHA; update and revalidate at least every 5 years; keep PHAs and resolutions for the life of the process"),
    "f": ("1910.119(f)", "Operating procedures", "written procedures for each phase; review as often as necessary; certify annually that they are current and accurate"),
    "g": ("1910.119(g)", "Training", "initial training; refresher training at least every 3 years; document training"),
    "h": ("1910.119(h)", "Contractors", "evaluate contractor safety performance when selecting; inform of hazards; periodically evaluate contract employers"),
    "i": ("1910.119(i)", "Pre-startup safety review", "for new and significantly modified facilities, confirm construction, procedures, PHA recommendations and training before introducing hazardous chemicals"),
    "j": ("1910.119(j)", "Mechanical integrity", "written procedures, training, inspection and testing at frequencies per manufacturers' recommendations and good engineering practice, deficiency correction, quality assurance"),
    "k": ("1910.119(k)", "Hot work permit", "permit for hot work on or near a covered process"),
    "l": ("1910.119(l)", "Management of change", "written procedures for changes (except replacement in kind) to chemicals, technology, equipment, procedures, facilities; address consequences before the change"),
    "m": ("1910.119(m)", "Incident investigation", "start within 48 hours; team with process expertise; written report; resolve findings; retain reports 5 years"),
    "n": ("1910.119(n)", "Emergency planning and response", "emergency action plan per 1910.38 including procedures for small releases"),
    "o": ("1910.119(o)", "Compliance audits", "certify compliance evaluation at least every 3 years; report; respond to findings; retain the two most recent reports"),
    "p": ("1910.119(p)", "Trade secrets", "provide access to information needed for PSM compliance without regard to trade secret status, under confidentiality agreements"),
}

# AIGA 99 (Asia Industrial Gases Association) 21 elements - titles verified from the document's contents page
AIGA99_ELEMENTS = {
    1: "Leadership commitment and responsibility", 2: "Compliance with legislation and industry standards",
    3: "Employee selection, training, and competency", 4: "Workforce involvement", 5: "Communication with stakeholders",
    6: "Hazard identification and risk assessment", 7: "Documentation, records, and knowledge management",
    8: "Process and operational status monitoring and handover", 9: "Operating procedures", 10: "Management of operational interfaces",
    11: "Standards and practices", 12: "Management of change", 13: "Operational readiness and process startup",
    14: "Emergency and crisis management", 15: "Inspection and maintenance", 16: "Management of safety critical devices",
    17: "Work control, permit to work, and task risk management", 18: "Contractors and suppliers - selection and management",
    19: "Incident investigation", 20: "Audit, management review, and intervention", 21: "Measures and metrics",
}

# CCPS Risk Based Process Safety: 20 elements in four pillars (from published literature)
RBPS_ELEMENTS = {
    "Commit to process safety": ["Process safety culture", "Compliance with standards", "Process safety competency", "Workforce involvement", "Stakeholder outreach"],
    "Understand hazards and risk": ["Process knowledge management", "Hazard identification and risk analysis"],
    "Manage risk": ["Operating procedures", "Safe work practices", "Asset integrity and reliability", "Contractor management",
                    "Training and performance assurance", "Management of change", "Operational readiness", "Conduct of operations", "Emergency management"],
    "Learn from experience": ["Incident investigation", "Measurement and metrics", "Auditing", "Management review and continuous improvement"],
}

# AUTHOR'S approximate crosswalk OSHA element -> AIGA 99 element numbers (not published by either body; check before relying on it)
CROSSWALK_OSHA_TO_AIGA = {"c": [4], "d": [7, 11], "e": [6], "f": [9], "g": [3], "h": [18], "i": [13], "j": [15, 16], "k": [17], "l": [12],
                          "m": [19], "n": [14], "o": [20], "p": [5, 7]}

CADENCE_YEARS = {"pha_revalidation": 5, "operating_procedure_certification": 1, "refresher_training": 3, "compliance_audit": 3}


def _data() -> dict:
    return json.loads(resources.files("process_safety").joinpath("data/osha_psm_appendix_a.json").read_text())


def appendix_a() -> list[dict]:
    return _data()["chemicals"]


def lookup_chemical(name_or_cas: str) -> dict | None:
    q = name_or_cas.strip().lower()
    for r in appendix_a():
        if r["cas"] == name_or_cas.strip() or r["chemical"].lower() == q:
            return r
    for r in appendix_a():
        if q in r["chemical"].lower():
            return r
    return None


def covered_chemical(name_or_cas: str, quantity_kg: float) -> dict:
    """Appendix A test: covered when the quantity in a process (interconnected vessels, one location) is >= the threshold quantity."""
    r = lookup_chemical(name_or_cas)
    if r is None:
        return {"found": False, "note": "not in Appendix A parsed list; check the official page"}
    tq_kg = r["tq_lb"] / LB_PER_KG
    return {"found": True, "chemical": r["chemical"], "cas": r["cas"], "threshold_lb": r["tq_lb"], "threshold_kg": tq_kg,
            "quantity_kg": quantity_kg, "covered": quantity_kg >= tq_kg}


def covered_flammable(quantity_kg: float, category1_gas_or_liquid_below_37_8C: bool = True, workplace_fuel_only: bool = False,
                      atmospheric_tank_below_boiling_point: bool = False) -> dict:
    """1910.119(a)(1)(ii): >= 10,000 lb (4535.9 kg) of a Category 1 flammable gas or a liquid with flash point < 37.8 C at one location,
    except (A) hydrocarbon fuels used solely for workplace consumption (not part of a process with a covered chemical) and
    (B) such liquids in atmospheric tanks or transferred while kept below their normal boiling point without chilling/refrigeration."""
    thr = 10000 / LB_PER_KG
    exempt = workplace_fuel_only or atmospheric_tank_below_boiling_point
    return {"threshold_kg": thr, "quantity_kg": quantity_kg, "exempt": exempt,
            "covered": category1_gas_or_liquid_below_37_8C and quantity_kg >= thr and not exempt}


def _add_years(d: date, years: int) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:  # 29 Feb
        return d.replace(year=d.year + years, day=28)


def due_dates(last_done: dict[str, date], today: date | None = None, warn_days: int = 90) -> dict:
    """Next due date for each recurring OSHA cadence from the last completion date; status overdue / due-soon / ok."""
    today = today or date.today()
    out = {}
    for key, yrs in CADENCE_YEARS.items():
        if key not in last_done:
            continue
        nxt = _add_years(last_done[key], yrs)
        days = (nxt - today).days
        out[key] = {"last": last_done[key].isoformat(), "next_due": nxt.isoformat(), "days_remaining": days,
                    "status": "overdue" if days < 0 else "due-soon" if days <= warn_days else "ok"}
    return out


def incident_investigation_deadline(incident_time) -> "datetime":
    """Investigation must be initiated no later than 48 hours after the incident (datetime in, datetime out)."""
    return incident_time + timedelta(hours=48)


def gap_assessment(scores: dict[str, int], weights: dict[str, float] | None = None, framework: str = "osha") -> dict:
    """Self-assessment: score each element 0 (none) .. 4 (embedded and audited). Returns weighted percentage and the weakest elements.
    A planning aid for prioritising work, not a compliance finding."""
    names = {k: v[1] for k, v in OSHA_ELEMENTS.items()} if framework == "osha" else {str(k): v for k, v in AIGA99_ELEMENTS.items()}
    missing = [k for k in names if k not in scores]
    w = {k: (weights or {}).get(k, 1.0) for k in scores}
    total = sum(w[k] * scores[k] for k in scores)
    pct = 100 * total / (4 * sum(w.values()))
    ranked = sorted(scores, key=lambda k: scores[k])
    return {"percent": pct, "unscored": missing, "weakest": [(k, names.get(k, k), scores[k]) for k in ranked[:3]]}

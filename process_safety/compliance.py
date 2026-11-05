"""Tiered compliance with design requirements, and derogations.

A requirement in a design practice or standard carries a tier, taken from its modal verb:

    MUST    "shall", "must", "is required to", and every "shall not" prohibition. Comply, or hold an approved derogation.
    SHOULD  "should", "is recommended". Comply, or explain: a documented justification, accepted by the discipline lead.
    CAN     "may", "can", "is permitted". Optional: record whether it was adopted. No derogation is ever needed.

A derogation is a formal, recorded, approved departure from a MUST clause for a stated scope and period. What a valid one needs:

    justification, a risk assessment reference, at least one compensating measure, an expiry date, a consequence assessment, and the
    sign-offs the approval matrix requires.

A SHOULD departure needs a justification and the (lighter) sign-offs the matrix gives it; an expiry is optional. A clause marked
`statutory` (a law or licence condition, not a company or industry practice) cannot be derogated internally: the only route is an
exemption from the regulator, recorded here as `regulator_ref`.

Approval matrix. Who must sign depends on the tier and on the consequence if the departure goes wrong. Technical authority levels run
TA3 (lowest: site / discipline) < TA2 (project / regional discipline) < TA1 (highest: corporate / principal). The consequence class
(low, medium, high, severe) is the highest of the safety severity and the six PESTLE ratings (0-5) given for the failure scenario;
`APPROVAL_MATRIX` gives the sign-offs for each tier and class. With no consequence assessment the matrix uses `severe`. The level names,
the 0-5 scale, the class thresholds and the matrix cells are defaults written to be edited: they are not any company's rules.

PESTLE maps the consequence across Political, Economic, Social, Technological, Legal and Environmental factors, each rated 0-5 with a
note. A factor rated `ACTION_AT` (3) or more needs a management action, and a MUST derogation must address all six factors. This module checks that a register is complete and consistent; it does not judge whether a
justification is technically adequate, and a passing register is not an approval.
"""
from __future__ import annotations

import csv
import datetime as dt
import json

TIERS = ("MUST", "SHOULD", "CAN")
STATUSES = ("complied", "derogated", "not-applicable", "open", "adopted", "not-adopted")
VALID_STATUS = {
    "MUST": ("complied", "derogated", "not-applicable", "open"),
    "SHOULD": ("complied", "derogated", "not-applicable", "open"),
    "CAN": ("adopted", "not-adopted", "not-applicable", "open"),
}
# Technical authority levels, lowest to highest. An approval at a higher level can stand in for a lower required level.
APPROVER_LEVELS = ("TA3", "TA2", "TA1")
PESTLE_FACTORS = ("political", "economic", "social", "technological", "legal", "environmental")
CLASS_THRESHOLDS = ((2, "low"), (3, "medium"), (4, "high"), (5, "severe"))     # highest rating up to and including N -> class
ACTION_AT = 3                                                                  # a PESTLE factor at or above this needs a management action
# Sign-offs required (each by a different person; a higher level may sign for a lower requirement), by tier and consequence class.
APPROVAL_MATRIX = {
    "MUST": {"low": ("TA2",), "medium": ("TA2",), "high": ("TA1",), "severe": ("TA1", "TA2")},
    "SHOULD": {"low": ("TA3",), "medium": ("TA3",), "high": ("TA2",), "severe": ("TA1",)},
}
_MODALITY_TIER = {"mandatory": "MUST", "prohibition": "MUST", "recommended": "SHOULD", "permissive": "CAN"}


def tier_from_modality(modality: str) -> str:
    """Map the requirements extractor's modality (mandatory / prohibition / recommended / permissive) to MUST / SHOULD / CAN."""
    try:
        return _MODALITY_TIER[modality]
    except KeyError:
        raise ValueError(f"unknown modality {modality!r}") from None


def _date(s, what):
    try:
        return dt.date.fromisoformat(str(s))
    except ValueError:
        raise ValueError(f"{what}: {s!r} is not an ISO date (YYYY-MM-DD)") from None


def _level(name):
    return APPROVER_LEVELS.index(name) if name in APPROVER_LEVELS else -1


def consequence_class(consequence: dict | None) -> tuple[str, list[str]]:
    """(class, drivers): the class from the highest of safety severity and the PESTLE ratings; drivers are the factors at that rating.
    No assessment, or no rating at all, gives ('severe', [])."""
    c = consequence or {}
    ratings = {}
    if c.get("safety_severity") is not None:
        ratings["safety"] = c["safety_severity"]
    for f, v in (c.get("pestle") or {}).items():
        if f not in PESTLE_FACTORS:
            raise ValueError(f"unknown PESTLE factor {f!r}; use {PESTLE_FACTORS}")
        if v.get("rating") is not None:
            ratings[f] = v["rating"]
    for k, r in ratings.items():
        if not isinstance(r, (int, float)) or not 0 <= r <= 5:
            raise ValueError(f"consequence rating for {k} must be 0-5, got {r!r}")
    if not ratings:
        return "severe", []
    top = max(ratings.values())
    cls = next(name for limit, name in CLASS_THRESHOLDS if top <= limit)
    return cls, sorted(k for k, r in ratings.items() if r == top)


def required_signoffs(tier: str, cls: str) -> tuple[str, ...]:
    return APPROVAL_MATRIX[tier][cls]


def _signoffs_met(required, approvals):
    """Match each required level to a distinct approval at that level or above (highest requirements first). Returns the unmet levels."""
    pool = sorted((a.get("level") for a in approvals if _level(a.get("level")) >= 0), key=_level, reverse=True)
    unmet = []
    for need in sorted(required, key=_level, reverse=True):
        for i, have in enumerate(pool):
            if _level(have) >= _level(need):
                pool.pop(i)
                break
        else:
            unmet.append(need)
    return unmet


def check_derogation(clause: dict, as_of: dt.date) -> list[dict]:
    """Problems with one clause's derogation record (empty list: the record is complete and in force)."""
    tier, d = clause["tier"], clause.get("derogation") or {}
    cid = clause["id"]
    issues = []

    def bad(code, msg):
        issues.append({"clause": cid, "tier": tier, "code": code, "message": msg})

    if clause.get("statutory") and tier == "MUST":
        if not clause.get("regulator_ref"):
            bad("statutory-no-exemption", "a statutory requirement cannot be derogated internally: record the regulator's exemption in regulator_ref")
        return issues
    if not d.get("justification"):
        bad("no-justification", "a departure needs a written justification")
    cons = d.get("consequence")
    if tier == "MUST":
        if not d.get("risk_assessment_ref"):
            bad("no-risk-assessment", "a MUST derogation needs a risk assessment reference")
        if not d.get("compensating_measures"):
            bad("no-compensating-measures", "a MUST derogation needs at least one compensating measure")
        if not d.get("expiry"):
            bad("no-expiry", "a MUST derogation needs an expiry (or review) date")
        if not cons:
            bad("no-consequence-assessment", "a MUST derogation needs a consequence assessment (scenario, safety severity, PESTLE); the matrix assumes 'severe' until it is given")
        else:
            missing = [f for f in PESTLE_FACTORS if f not in (cons.get("pestle") or {})]
            if missing:
                bad("pestle-incomplete", f"a MUST derogation must address all six PESTLE factors; missing: {', '.join(missing)}")
            if not cons.get("scenario"):
                bad("no-scenario", "describe the consequence scenario (what happens if the departure goes wrong)")
    if cons:
        for f, v in (cons.get("pestle") or {}).items():
            if f in PESTLE_FACTORS and (v.get("rating") or 0) >= ACTION_AT and not (cons.get("management_actions") or {}).get(f):
                bad("pestle-no-action", f"{f} is rated {v['rating']} (>= {ACTION_AT}) with no management action")
    cls, _ = consequence_class(cons)
    required = required_signoffs(tier, cls)
    unmet = _signoffs_met(required, d.get("approvals") or [])
    if not d.get("approvals"):
        bad("not-approved", f"no approval recorded; {tier} / {cls} consequence needs {' + '.join(required)}")
    elif unmet:
        bad("approval-insufficient", f"{tier} / {cls} consequence needs {' + '.join(required)}; unmet: {', '.join(unmet)}")
    for a in d.get("approvals") or []:
        if _level(a.get("level")) < 0:
            bad("unknown-approver-level", f"approver level {a.get('level')!r} is not one of {list(APPROVER_LEVELS)}")
    if d.get("expiry"):
        try:
            if _date(d["expiry"], f"{cid} expiry") < as_of:
                bad("expired", f"derogation expired on {d['expiry']}")
        except ValueError as e:
            bad("bad-date", str(e))
    return issues


def review(clause: dict) -> dict:
    """The consequence class, required and present sign-offs and the PESTLE map for one derogated clause."""
    d = clause.get("derogation") or {}
    cons = d.get("consequence") or {}
    cls, drivers = consequence_class(d.get("consequence"))
    req = required_signoffs(clause["tier"], cls)
    pm = cons.get("pestle") or {}
    acts = cons.get("management_actions") or {}
    return {"clause": clause["id"], "tier": clause["tier"], "consequence_class": cls, "driven_by": drivers,
            "required_signoffs": list(req), "present_signoffs": [a.get("level") for a in d.get("approvals") or []],
            "unmet": _signoffs_met(req, d.get("approvals") or []),
            "scenario": cons.get("scenario", ""),
            "pestle": {f: {"rating": pm[f].get("rating"), "note": pm[f].get("note", ""), "management_action": acts.get(f, "")} for f in PESTLE_FACTORS if f in pm}}


def matrix_markdown() -> str:
    """The approval matrix as a Markdown table."""
    cls = [n for _, n in CLASS_THRESHOLDS]
    rows = ["| Tier | " + " | ".join(cls) + " |", "|---|" + "---|" * len(cls)]
    for t, m in APPROVAL_MATRIX.items():
        rows.append(f"| {t} | " + " | ".join(" + ".join(m[c]) for c in cls) + " |")
    return "\n".join(rows) + "\n"


def evaluate(register: dict, as_of: dt.date | None = None) -> dict:
    """Check a register {"clauses": [...]} and summarise compliance by tier. Raises ValueError on a malformed register."""
    as_of = as_of or _date(register.get("as_of", dt.date.today().isoformat()), "as_of")
    clauses = register.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        raise ValueError("register needs a non-empty 'clauses' list")
    seen, issues = set(), []
    table = {t: {s: 0 for s in VALID_STATUS[t]} for t in TIERS}
    for c in clauses:
        for k in ("id", "tier", "status"):
            if k not in c:
                raise ValueError(f"clause {c.get('id', '?')}: missing '{k}'")
        if c["id"] in seen:
            raise ValueError(f"duplicate clause id {c['id']!r}")
        seen.add(c["id"])
        if c["tier"] not in TIERS:
            raise ValueError(f"clause {c['id']}: tier must be one of {TIERS}")
        if c["status"] not in VALID_STATUS[c["tier"]]:
            raise ValueError(f"clause {c['id']}: status {c['status']!r} is not valid for {c['tier']} (use {VALID_STATUS[c['tier']]})")
        table[c["tier"]][c["status"]] += 1
        if c["status"] == "derogated":
            if c["tier"] == "CAN":
                raise ValueError(f"clause {c['id']}: a CAN clause is optional and cannot be derogated")
            issues += check_derogation(c, as_of)
        elif c["status"] == "not-applicable" and c["tier"] != "CAN" and not c.get("na_reason"):
            issues.append({"clause": c["id"], "tier": c["tier"], "code": "na-no-reason", "message": "not-applicable needs a stated reason (na_reason)"})
        elif c["status"] == "open":
            issues.append({"clause": c["id"], "tier": c["tier"], "code": "open", "message": "no compliance position recorded yet"})
    bad_ids = {i["clause"] for i in issues}
    blocking_ids = {i["clause"] for i in issues if i["tier"] == "MUST"}
    must = table["MUST"]
    must_total = sum(must.values()) - must["not-applicable"]
    must_ok = must["complied"] + sum(1 for c in clauses if c["tier"] == "MUST" and c["status"] == "derogated" and c["id"] not in bad_ids)
    should = table["SHOULD"]
    should_total = sum(should.values()) - should["not-applicable"]
    return {
        "as_of": as_of.isoformat(),
        "by_tier": table,
        "must_compliance": {"satisfied": must_ok, "applicable": must_total, "pct": round(100 * must_ok / must_total, 1) if must_total else None},
        "should_complied_pct": round(100 * should["complied"] / should_total, 1) if should_total else None,
        "derogations": {t: table[t]["derogated"] for t in ("MUST", "SHOULD")},
        "derogation_reviews": [review(c) for c in clauses if c["status"] == "derogated" and not (c.get("statutory") and c["tier"] == "MUST")],
        "issues": issues,
        "ready_for_gate": not blocking_ids,
        "gate_note": "ready_for_gate is false while any MUST clause is open or has an incomplete, expired or improperly approved derogation",
    }


def init_register(extract_csv: str, as_of: str | None = None) -> dict:
    """Build a starting register (every clause 'open') from a CSV written by `process_safety requirements`."""
    clauses = []
    with open(extract_csv, newline="", encoding="utf-8") as fh:
        for n, r in enumerate(csv.DictReader(fh), 1):
            cid = f"{r.get('file', '')}:{r.get('clause') or n}".strip(":")
            if any(c["id"] == cid for c in clauses):
                cid = f"{cid}#{n}"
            clauses.append({"id": cid, "source": r.get("file", ""), "tier": tier_from_modality(r["modality"]), "text": r.get("statement", ""),
                            "status": "open"})
    return {"as_of": as_of or dt.date.today().isoformat(), "clauses": clauses}


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)

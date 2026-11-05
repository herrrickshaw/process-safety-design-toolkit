"""Tiered compliance with design requirements, and derogations.

A requirement in a design practice or standard carries a tier, taken from its modal verb:

    MUST    "shall", "must", "is required to", and every "shall not" prohibition. Comply, or hold an approved derogation.
    SHOULD  "should", "is recommended". Comply, or explain: a documented justification, accepted by the discipline lead.
    CAN     "may", "can", "is permitted". Optional: record whether it was adopted. No derogation is ever needed.

A derogation is a formal, recorded, approved departure from a MUST clause for a stated scope and period. What a valid one needs:

    justification, a risk assessment reference, at least one compensating measure, an approver of enough seniority, an expiry date.

A SHOULD departure needs only a justification and a discipline-level approver (an expiry is optional). A clause marked
`statutory` (a law or licence condition, not a company or industry practice) cannot be derogated internally: the only route is an
exemption from the regulator, recorded here as `regulator_ref`.

The seniority ladder and which level approves which tier are defaults (`APPROVER_LEVELS`, `REQUIRED_APPROVER`), written to be edited:
they are not any company's rules. This module checks that a register is complete and consistent; it does not judge whether a
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
# Ladder from lowest to highest authority; a derogation must be approved at or above the level its tier requires.
APPROVER_LEVELS = ("discipline-lead", "project-manager", "technical-authority")
REQUIRED_APPROVER = {"MUST": "technical-authority", "SHOULD": "discipline-lead"}
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
    if tier == "MUST":
        if not d.get("risk_assessment_ref"):
            bad("no-risk-assessment", "a MUST derogation needs a risk assessment reference")
        if not d.get("compensating_measures"):
            bad("no-compensating-measures", "a MUST derogation needs at least one compensating measure")
        if not d.get("expiry"):
            bad("no-expiry", "a MUST derogation needs an expiry (or review) date")
    need = REQUIRED_APPROVER[tier]
    got = d.get("approved_by_level")
    if not got:
        bad("not-approved", f"no approval recorded; {tier} needs {need} or higher")
    elif _level(got) < 0:
        bad("unknown-approver-level", f"approver level {got!r} is not one of {list(APPROVER_LEVELS)}")
    elif _level(got) < _level(need):
        bad("approver-too-junior", f"{got} cannot approve a {tier} departure; needs {need} or higher")
    if d.get("expiry"):
        try:
            if _date(d["expiry"], f"{cid} expiry") < as_of:
                bad("expired", f"derogation expired on {d['expiry']}")
        except ValueError as e:
            bad("bad-date", str(e))
    return issues


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

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

EU compliance. A derogation is an internal, company-level instrument: it cannot waive a legal requirement. A clause with
`legal_basis` {"regime": "EU", "instrument", "article", "relation"} is treated as follows. relation "is" (the clause is the legal
text): it cannot be derogated internally, only exempted by the member-state competent authority. relation "implements" (a company
clause that exists to meet the law): it may be derogated only with an `eu_equivalence` statement showing the alternative still
meets the legal duty, and its consequence class is at least `EU_CLASS_FLOOR`. For a Seveso III establishment (register field
"seveso": "lower" or "upper"), a derogation that could have significant consequences for major-accident hazards is a modification
under Article 11 of Directive 2012/18/EU: the operator reviews and, where necessary, updates the notification, the major-accident
prevention policy (MAPP), the safety management system and (upper tier) the safety report, and informs the competent authority in
advance. Only Seveso III was read for this module (EUR-Lex text, 2026-11-06); other EU instruments are recognised by name but their
articles are not encoded. EU law is transposed nationally: check your member state's law and your competent authority.

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
EU_CLASS_FLOOR = "high"          # a derogation of a clause that implements an EU legal duty is never rated below this
SEVESO_TIERS = (None, "lower", "upper")
SEVESO_DOCUMENTS = {"lower": ("notification", "MAPP", "safety management system"),
                    "upper": ("notification", "MAPP", "safety management system", "safety report")}
# What Directive 2012/18/EU (Seveso III) says on the points used here; paraphrased from the EUR-Lex text.
SEVESO_ARTICLES = {
    "5": "General obligations: take all necessary measures to prevent major accidents and limit their consequences; prove this to the competent authority at any time",
    "7(4)": "Notification: inform the competent authority in advance of a modification of an establishment or installation that could have significant consequences for major-accident hazards",
    "8": "Major-accident prevention policy (MAPP) and safety management system",
    "10": "Safety report (upper tier): must show adequate safety and reliability in design, construction, operation and maintenance (10(1)(c)); reviewed at least every five years and after changes (10(5))",
    "11": "Modification: review and, where necessary, update notification, MAPP, SMS and safety report, and inform the competent authority of the details in advance of the modification",
    "19": "Prohibition of use where prevention and mitigation measures are seriously deficient, or required information was not submitted",
}
_RANK = [n for _, n in CLASS_THRESHOLDS]

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


def _eu_relation(clause):
    lb = clause.get("legal_basis") or {}
    if lb.get("regime") != "EU":
        return None
    if lb.get("relation") not in ("is", "implements"):
        raise ValueError(f"clause {clause['id']}: legal_basis.relation must be 'is' or 'implements'")
    return lb["relation"]


def effective_class(clause: dict) -> tuple[str, list[str]]:
    """Consequence class after the EU floor (a clause implementing an EU duty is rated at least EU_CLASS_FLOOR)."""
    cls, drivers = consequence_class((clause.get("derogation") or {}).get("consequence"))
    if _eu_relation(clause) == "implements" and _RANK.index(cls) < _RANK.index(EU_CLASS_FLOOR):
        return EU_CLASS_FLOOR, drivers + ["EU floor"]
    return cls, drivers


def significant_for_seveso(clause: dict) -> bool:
    """A derogation is screened for Seveso Article 11 when it is a MUST departure, or any departure rated high or severe."""
    cls, _ = effective_class(clause)
    return clause["tier"] == "MUST" or _RANK.index(cls) >= _RANK.index("high")


def check_derogation(clause: dict, as_of: dt.date, seveso: str | None = None) -> list[dict]:
    """Problems with one clause's derogation record (empty list: the record is complete and in force)."""
    tier, d = clause["tier"], clause.get("derogation") or {}
    cid = clause["id"]
    issues = []

    def bad(code, msg):
        issues.append({"clause": cid, "tier": tier, "code": code, "message": msg})

    rel = _eu_relation(clause)
    if (clause.get("statutory") or rel == "is") and tier == "MUST":
        if not clause.get("regulator_ref"):
            who = "the member-state competent authority" if rel == "is" else "the regulator"
            bad("statutory-no-exemption", f"a statutory requirement cannot be derogated internally: record {who}'s exemption in regulator_ref")
        return issues
    if rel == "implements" and not d.get("eu_equivalence"):
        bad("eu-equivalence-not-shown", "this clause implements an EU legal duty: state in eu_equivalence how the alternative still meets it")
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
    cls, _ = effective_class(clause)
    required = required_signoffs(tier, cls)
    if seveso and significant_for_seveso(clause):
        sa = d.get("seveso_assessment")
        if not sa or "significant" not in sa or not sa.get("rationale"):
            bad("seveso-not-assessed", "Seveso Art. 11: assess (seveso_assessment: significant true/false with a rationale) whether this departure could have significant consequences for major-accident hazards")
        elif sa["significant"]:
            if not sa.get("authority_informed"):
                bad("seveso-authority-not-informed", "Seveso Art. 11 / 7(4): the competent authority must be informed of the details in advance of the modification (authority_informed date)")
            missing = [x for x in SEVESO_DOCUMENTS[seveso] if x not in (sa.get("documents_updated") or [])]
            if missing:
                bad("seveso-documents-not-updated", f"Seveso Art. 11: review and update before the modification: {', '.join(missing)}")
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
    cls, drivers = effective_class(clause)
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


def eu_summary(register: dict) -> dict | None:
    """EU view of the register, or None when it has no Seveso tier and no clause with an EU legal basis."""
    sev = register.get("seveso")
    if sev not in SEVESO_TIERS:
        raise ValueError(f"register 'seveso' must be one of {SEVESO_TIERS}")
    eu = [c for c in register["clauses"] if _eu_relation(c)]
    if not sev and not eu:
        return None
    der = [c for c in register["clauses"] if c["status"] == "derogated"]
    screened = [c for c in der if sev and significant_for_seveso(c) and not (c.get("statutory") or _eu_relation(c) == "is")]
    sig = [c["id"] for c in screened if ((c.get("derogation") or {}).get("seveso_assessment") or {}).get("significant")]
    return {
        "seveso_tier": sev,
        "non_derogable_eu_clauses": sorted(c["id"] for c in eu if _eu_relation(c) == "is" and c["tier"] == "MUST"),
        "eu_implementing_derogations": sorted(c["id"] for c in der if _eu_relation(c) == "implements"),
        "derogations_screened_for_art11": sorted(c["id"] for c in screened),
        "art11_significant": sorted(sig),
        "art11_unassessed": sorted(c["id"] for c in screened if "significant" not in ((c.get("derogation") or {}).get("seveso_assessment") or {})),
        "documents_to_update_if_significant": list(SEVESO_DOCUMENTS[sev]) if sev else [],
        "notes": ["Derogations are internal: they never waive an EU or national legal requirement.",
                  "Under Seveso Art. 5(2) the operator must be able to prove to the competent authority, at any time, that all necessary measures were taken: keep this register current and producible.",
                  "Art. 10(1)(c) (upper tier): the safety report must show adequate safety and reliability in design; list derogations and their compensating measures there.",
                  "Only Seveso III articles are encoded; check ATEX, PED, IED and your member state's transposition separately."],
    }


def evaluate(register: dict, as_of: dt.date | None = None) -> dict:
    """Check a register {"clauses": [...]} and summarise compliance by tier. Raises ValueError on a malformed register."""
    as_of = as_of or _date(register.get("as_of", dt.date.today().isoformat()), "as_of")
    clauses = register.get("clauses")
    if not isinstance(clauses, list) or not clauses:
        raise ValueError("register needs a non-empty 'clauses' list")
    if register.get("seveso") not in SEVESO_TIERS:
        raise ValueError(f"register 'seveso' must be one of {SEVESO_TIERS}")
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
            issues += check_derogation(c, as_of, register.get("seveso"))
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
        "eu_compliance": eu_summary(register),
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

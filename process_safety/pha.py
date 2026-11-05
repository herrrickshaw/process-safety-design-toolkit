"""PHA study management beyond the HAZOP worksheet: CHAZOP, What-if / SWIFT and PSSR worksheets, SIMOPS matrices and schedule
clash checks, HAZOP recommendation (action) tracking, and HAZOP revalidation (due dates, triggers, carry-forward diff).

Worksheet prompts are generic checklists from common practice (CCPS guidelines, IEC 61882 style guidewords, SWIFT as described
in the open literature); they prompt a facilitated team and do not replace it. The 5-year PHA revalidation cadence is OSHA
1910.119(e)(6) (already used in psm.py); other regimes may differ.
"""
from __future__ import annotations

import csv
import datetime as dt
import itertools
import math

CHAZOP = {
    "Field signal / sensor": ["No signal (open circuit, power loss)", "Frozen / stuck reading", "Drift high / low", "Wrong range or calibration",
                              "Noisy / intermittent signal", "Sensor shares tapping or transmitter with SIS (common cause)"],
    "Controller / logic": ["Wrong mode (manual / auto / cascade)", "Wrong set point or tuning", "Logic or configuration error after change",
                           "Controller failure / watchdog", "Loss of communications to field I/O", "Time / sequence fault in batch logic"],
    "Final element": ["Valve fails open / closed / stays put", "Actuator air or power loss", "Positioner failure", "Slow stroke", "Valve passing"],
    "Operator interface": ["Alarm flood / missing alarm", "Wrong display or tag", "HMI frozen", "Operator overrides / bypasses left in place"],
    "Power and infrastructure": ["UPS / DC failure", "Network switch failure", "Cabinet cooling failure", "Lightning / surge"],
    "Security": ["Unauthorised logic change", "Remote access misuse", "Malware on engineering station"],
}

WHAT_IF = {
    "Equipment failure": ["What if the pump trips?", "What if the control valve fails open?", "What if the exchanger tube leaks?",
                          "What if the relief valve lifts / fails to lift?"],
    "Utilities": ["What if power is lost?", "What if instrument air fails?", "What if cooling water stops?", "What if nitrogen is lost?"],
    "Human factors": ["What if the wrong valve is opened?", "What if a step is skipped?", "What if the batch is double-charged?",
                      "What if the line is not drained before opening?"],
    "External": ["What if there is a fire nearby?", "What if a vehicle hits the pipe rack?", "What if it floods?", "What if there is an earthquake?"],
    "Materials": ["What if the feed is contaminated / wrong?", "What if water gets in?", "What if the inhibitor is missing?"],
}

SWIFT_GUIDEWORDS = ["Wrong (material, action, place, time)", "Incorrect quantity / rate", "Without (missing step, utility, check)", "Failure of",
                    "Error / mistake", "Timing (too early, too late)", "Sequence (wrong order)", "Simultaneous / interference", "Maintenance / testing",
                    "External influence", "Change (from design / MOC)"]

PSSR = ["Construction meets design and P&IDs (as-built)", "Safety, operating, maintenance and emergency procedures in place and adequate",
        "PHA performed and recommendations resolved before start-up (new facility) / MOC met (modification)", "Training of each employee completed",
        "Relief devices installed, set and documented", "SIS / interlocks tested and bypasses removed", "Fire & gas detection commissioned",
        "Fire protection systems available", "Hazardous-area equipment certified and inspected", "Line-up, blinds and spades checked",
        "Pressure / leak tests completed", "Housekeeping and access / escape routes clear", "Emergency response and communication ready"]

SIMOPS_LEVELS = {"P": "permitted", "C": "conditional (controls required)", "X": "prohibited"}


def worksheet(kind: str, node: str, extra: dict | None = None) -> list[dict]:
    src = {"chazop": CHAZOP, "whatif": WHAT_IF}.get(kind)
    rows = []
    if kind == "swift":
        for g in SWIFT_GUIDEWORDS:
            rows.append({"Node / activity": node, "Guideword": g, "What-if question": "", "Hazard / consequence": "", "Safeguards": "",
                         "Risk": "", "Recommendation": "", "Owner": "", "Status": "open"})
        return rows
    if kind == "pssr":
        return [{"Item": node, "Check": c, "Verified (Y/N/NA)": "", "Evidence": "", "Punch item": "", "By": ""} for c in PSSR]
    if src is None:
        raise ValueError("kind must be chazop | whatif | swift | pssr")
    for cat, items in {**src, **(extra or {})}.items():
        for it in items:
            rows.append({"Node / activity": node, "Category": cat, "Prompt": it, "Causes": "", "Consequences": "", "Safeguards": "",
                         "S": "", "L": "", "Risk": "", "Recommendation": "", "Owner": "", "Status": "open"})
    return rows


def simops_matrix(activities: list[str], rules: dict[str, str], default: str = "C") -> list[list[str]]:
    """rules keyed 'A|B' (order-insensitive) -> 'P' | 'C' | 'X'. Returns a square matrix (header row/col included)."""
    def r(a, b):
        return rules.get(f"{a}|{b}", rules.get(f"{b}|{a}", "-" if a == b else default))
    return [[""] + activities] + [[a] + [r(a, b) for b in activities] for a in activities]


def simops_clashes(schedule: list[dict], rules: dict[str, str], default: str = "C") -> list[dict]:
    """schedule = [{"activity", "start" (ISO), "end", "x", "y", "radius_m"?}] -> overlapping pairs that are X (or C) and spatially close."""
    out = []
    for a, b in itertools.combinations(schedule, 2):
        lvl = rules.get(f"{a['activity']}|{b['activity']}", rules.get(f"{b['activity']}|{a['activity']}", default))
        if lvl == "P":
            continue
        s1, e1, s2, e2 = (dt.datetime.fromisoformat(v) for v in (a["start"], a["end"], b["start"], b["end"]))
        if max(s1, s2) >= min(e1, e2):
            continue
        d = math.hypot(a.get("x", 0) - b.get("x", 0), a.get("y", 0) - b.get("y", 0))
        if d > a.get("radius_m", 1e9) + b.get("radius_m", 0) and "radius_m" in a:
            continue
        out.append({"activity_1": a["activity"], "activity_2": b["activity"], "level": SIMOPS_LEVELS.get(lvl, lvl),
                    "overlap_from": max(s1, s2).isoformat(), "overlap_to": min(e1, e2).isoformat(), "distance_m": round(d, 1)})
    return out


def action_status(actions: list[dict], today: dt.date | None = None) -> dict:
    """actions = [{"id", "study", "node", "risk" (e.g. 'high'), "owner", "due" (ISO date), "status": open|closed|deferred, "closed" (ISO)?}]"""
    today = today or dt.date.today()
    rows, by_owner = [], {}
    for a in actions:
        due = dt.date.fromisoformat(a["due"]) if a.get("due") else None
        closed = a.get("status", "open") == "closed"
        overdue = (not closed) and due is not None and due < today
        age = (today - due).days if overdue else 0
        bucket = "" if not overdue else "<30 d" if age < 30 else "30-90 d" if age <= 90 else ">90 d"
        rows.append({**a, "overdue": overdue, "days_overdue": age, "ageing": bucket})
        o = by_owner.setdefault(a.get("owner", "unassigned"), {"open": 0, "overdue": 0, "closed": 0})
        o["closed" if closed else "open"] += 1
        o["overdue"] += overdue
    n = len(actions) or 1
    closed_n = sum(1 for a in actions if a.get("status") == "closed")
    high_open = [r["id"] for r in rows if r.get("risk", "").lower() in ("high", "very high", "extreme") and r.get("status") != "closed"]
    return {"rows": rows, "closure_pct": 100 * closed_n / n, "overdue": sum(r["overdue"] for r in rows), "by_owner": by_owner,
            "high_risk_open": high_open}


def revalidation(last_pha: str, mocs_since: int = 0, incidents_since: int = 0, years: int = 5, today: dt.date | None = None,
                 moc_trigger: int = 10) -> dict:
    """Due date (last + years, OSHA 1910.119(e)(6) uses 5) and early-revalidation triggers (counts are company thresholds)."""
    today = today or dt.date.today()
    last = dt.date.fromisoformat(last_pha)
    try:
        due = last.replace(year=last.year + years)
    except ValueError:  # 29 Feb
        due = last.replace(year=last.year + years, day=28)
    triggers = []
    if mocs_since >= moc_trigger:
        triggers.append(f"{mocs_since} MOCs since last PHA (>= {moc_trigger})")
    if incidents_since:
        triggers.append(f"{incidents_since} process-safety incident(s) since last PHA")
    return {"due": due.isoformat(), "days_left": (due - today).days, "overdue": due < today, "early_revalidation_triggers": triggers,
            "approach": "redo" if (due < today and triggers) else "revalidate (review changes, incidents, recommendations)"}


def carry_forward(old_rows: list[dict], new_nodes: dict[str, str]) -> dict:
    """Compare the previous worksheet's nodes and design intents with the current list {node: design intent}."""
    old = {}
    for r in old_rows:
        old.setdefault(r["Node"], r.get("Design intent", ""))
    added = sorted(set(new_nodes) - set(old))
    removed = sorted(set(old) - set(new_nodes))
    changed = sorted(n for n in set(old) & set(new_nodes) if (old[n] or "").strip() != (new_nodes[n] or "").strip())
    same = sorted(n for n in set(old) & set(new_nodes) if n not in changed)
    return {"added": added, "removed": removed, "intent_changed": changed, "unchanged": same,
            "open_items_carried": [r for r in old_rows if r.get("Status", "open") != "closed" and r["Node"] in new_nodes]}


def write_csv(rows: list[dict] | list[list], path: str) -> int:
    with open(path, "w", newline="", encoding="utf-8-sig") as fh:
        if rows and isinstance(rows[0], list):
            csv.writer(fh).writerows(rows)
        elif rows:
            keys = list(dict.fromkeys(k for r in rows for k in r))
            w = csv.DictWriter(fh, fieldnames=keys)
            w.writeheader()
            w.writerows(rows)
    return len(rows)

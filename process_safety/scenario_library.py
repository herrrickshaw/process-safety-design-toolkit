"""Qualitative scenario library (`data/scenario_library.json`): per scenario family the hazards, initiating events, credible outcomes,
barriers, HAZID prompts, the toolkit modules that quantify it, and what is still missing, each tied to the sources behind it.

Honesty rules, enforced by tests: `grade` says how the content was obtained (read = source text read; search-summary = a search-engine
summary only; generic = standard hazard vocabulary with no specific source; none = no source read, fields left blank rather than guessed).
`status` says what the toolkit can do (partial = some quantitative modules exist with stated limits; planned = none yet; blocked = the
governing source is paywalled or unavailable, so only input-driven checks are possible). Prompts are prompts, not requirements, and nothing
here is a substitute for the standard or for a study team.
"""
from __future__ import annotations

import json
import os

_PATH = os.path.join(os.path.dirname(__file__), "data", "scenario_library.json")
_CACHE: dict | None = None
STATUSES = ("partial", "planned", "blocked")
GRADES = ("read", "search-summary", "generic", "none")


def _data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def entries() -> list[dict]:
    return list(_data()["entries"])


def get(scenario_id: str) -> dict:
    for e in entries():
        if e["id"] == scenario_id:
            return e
    raise KeyError(f"unknown scenario id: {scenario_id}")


def search(text: str | None = None, family: str | None = None, status: str | None = None, module: str | None = None) -> list[dict]:
    out = []
    for e in entries():
        if family and e["family"] != family:
            continue
        if status and e["status"] != status:
            continue
        if module and module not in e["modules"]:
            continue
        if text:
            hay = " ".join([e["id"], e["title"], e["family"], *e["hazards"], *e["initiating_events"], *e["outcomes"], *e["barriers"],
                            *e["hazid_prompts"], *e["gaps"]]).lower()
            if text.lower() not in hay:
                continue
        out.append(e)
    return out


def worksheet(scenario_id: str) -> list[dict]:
    """HAZID worksheet rows for one scenario: guideword-free prompts with blank cause, consequence, safeguard and action columns."""
    e = get(scenario_id)
    rows = []
    for i, p in enumerate(e["hazid_prompts"], 1):
        rows.append({"scenario": e["id"], "item": i, "prompt": p, "cause": "", "consequence": "", "existing_safeguards": "", "action": "", "owner": ""})
    for h in e["hazards"]:
        rows.append({"scenario": e["id"], "item": f"hazard: {h}", "prompt": f"Is '{h}' present in this design?", "cause": "", "consequence": "",
                     "existing_safeguards": "", "action": "", "owner": ""})
    return rows


def coverage_gaps() -> list[tuple[str, str, str]]:
    """(scenario id, status, gap) for every recorded gap, planned and blocked scenarios first."""
    order = {"blocked": 0, "planned": 1, "partial": 2}
    rows = [(e["id"], e["status"], g) for e in entries() for g in e["gaps"]]
    return sorted(rows, key=lambda r: (order[r[1]], r[0]))


def markdown() -> str:
    d = _data()
    es = d["entries"]
    lines = ["# Scenario library (qualitative toolkit)", "",
             f"Generated from `process_safety/data/scenario_library.json` (compiled {d['compiled']}). {len(es)} scenario families.",
             "Regenerate: `python -c \"from process_safety import scenario_library as s; print(s.markdown())\" > docs/SCENARIO_LIBRARY.md`.", "",
             d["note"], "",
             "| Scenario | Family | Status | Grade | Quantified by | Main gaps |", "|---|---|---|---|---|---|"]
    for e in es:
        lines.append(f"| `{e['id']}` {e['title']} | {e['family']} | {e['status']} | {e['grade']} | {', '.join(e['modules']) or '-'} | {'; '.join(e['gaps']) or '-'} |")
    lines.append("")
    for e in es:
        lines += [f"## {e['title']} (`{e['id']}`)", "", f"Status **{e['status']}**, grade **{e['grade']}**.", ""]
        for label, key in (("Hazards", "hazards"), ("Initiating events", "initiating_events"), ("Credible outcomes", "outcomes"),
                           ("Barriers named in the sources", "barriers"), ("HAZID prompts", "hazid_prompts"), ("Gaps", "gaps")):
            if e[key]:
                lines.append(f"**{label}**")
                lines += [f"* {x}" for x in e[key]]
                lines.append("")
        if e["sources"]:
            lines.append("**Sources** (read: " + ", ".join(sorted({s['read'] for s in e['sources']})) + ")")
            lines += [f"* [{s['title']}]({s['url']}) ({s['read']})" for s in e["sources"]]
            lines.append("")
    return "\n".join(lines)

"""Worldwide process safety incident casebook for teaching and safety discussions (`data/incident_casebook.json`).

A selection of historical cases, not a statistical dataset: how many cases a country has says nothing about how safe it is.
It complements the US-only CSB register in `incidents.py`, which maps investigations to design review steps; a case in both
carries `csb_id`. Every case names the sources that were read, each graded A (official investigation, inquiry, regulator, court or
government), B (professional body, peer reviewed, or an official summary such as an HSE case-study page or a French ARIA
accident sheet) or C (encyclopedia, news or other secondary). Each learning is marked
`source` (a source draws it) or `compiler` (this toolkit's interpretation). Discussion questions and topic prompts are the
compiler's.
"""
from __future__ import annotations

import json
import os

from . import country_coverage

_PATH = os.path.join(os.path.dirname(__file__), "data", "incident_casebook.json")
_CACHE: dict | None = None

# places outside the 193 UN members and two observers
EXTRA_PLACES = {"TWN": "Taiwan"}

GRADES = {"A": "official", "B": "professional, peer reviewed or an official summary page", "C": "secondary"}

CAUSE_STATUS = {"official-investigation": "official investigation", "secondary-account": "secondary account",
                "disputed": "disputed", "not-established": "not established"}

# topic: (label, opening prompt for a discussion, toolkit modules worth opening in class)
TOPICS = {
    "hazard-identification": ("Hazard identification", "Which study should have found this scenario, and what would it have needed to be told?", ("hazop", "pha")),
    "facility-siting": ("Facility siting and occupied buildings", "Who was where, and did they need to be there?", ("explosion", "qra")),
    "land-use-planning": ("Land-use planning and neighbours", "How did the distance to the public come to be what it was, and who can change it?", ("qra", "mah")),
    "management-of-change": ("Management of change", "What changed, who judged it safe, and what did they not look at?", ("psm",)),
    "mechanical-integrity": ("Mechanical integrity and corrosion", "How was the equipment expected to fail, and what inspection would have seen it?", ("vessel_mech", "psm")),
    "pipeline-integrity": ("Pipeline integrity", "How would the operator have known the line was weak or leaking, and how fast?", ("pipeline",)),
    "isolation-and-permit": ("Isolation, permits and handover", "What did the next person believe about the state of the equipment, and why?", ("psm",)),
    "contractor-management": ("Contractors and interfaces", "Which risk fell between two organisations?", ("psm",)),
    "startup-shutdown": ("Start-up, shutdown and abnormal operation", "What was different from normal running, and which safeguards assumed normal running?", ("depressuring", "overfill")),
    "overfill-and-level": ("Overfill and level control", "What stops the filling if the indication is wrong?", ("overfill", "tank_venting")),
    "relief-and-disposal": ("Relief, venting and disposal", "Where does the material go when containment is relieved, and is that place safe?", ("relief", "flare_system")),
    "reactive-hazards": ("Reactive and runaway hazards", "What can this material do on its own if it gets warmer, older or mixed?", ("reaction_hazard", "thermal_runaway")),
    "combustible-dust": ("Combustible dust", "Where could dust collect, and what would the second explosion feed on?", ("dust_explosion", "atex")),
    "toxic-release": ("Toxic releases", "How far could it travel, and what would people downwind do?", ("dispersion", "consequence")),
    "vapour-cloud-explosion": ("Vapour cloud explosions", "What let the cloud grow, and what made it explode rather than burn?", ("explosion", "dispersion")),
    "bleve-and-fire": ("Fires and BLEVE", "What was heating what, and how long did people have?", ("fireball", "pool_fire", "fire_water")),
    "ignition-control": ("Ignition control", "If we assume the release ignites, what would we design differently?", ("electrical", "flammability")),
    "storage-and-segregation": ("Storage, quantities and segregation", "Why was that much of it in that place, next to that?", ("mah",)),
    "hazardous-transport": ("Hazardous materials in transport", "Which controls stop applying once the material leaves the site?", ("consequence",)),
    "well-control": ("Well control and offshore barriers", "Which barriers were counted on, and how was each one shown to work?", ("bowtie",)),
    "alarms-and-human-factors": ("Alarms, displays and human factors", "What could the operator actually see and do in the time available?", ("sil",)),
    "safety-culture": ("Leadership and safety culture", "What warning was already available, and why did it not move anyone?", ("psm",)),
    "emergency-response": ("Emergency response and evacuation", "What did responders and neighbours know about what they were facing?", ("egress", "fire_water")),
    "natural-hazards-and-utilities": ("Natural hazards and loss of utilities", "What happens to the safeguards when power, water or access is lost?", ("reliability",)),
}

EVENT_TYPES = ("fire", "explosion", "toxic release", "BLEVE", "vapour cloud explosion", "dust explosion", "runaway reaction",
               "blowout", "pipeline rupture", "structural failure")

DISCUSSION_METHOD = (
    "Give the group the place, the plant and the day, not the outcome. Ask what could go wrong.",
    "Walk through what happened. Separate what an inquiry established from what is disputed or unknown.",
    "Ask which barriers existed on paper, which existed on the day, and who knew the difference.",
    "Use the two case questions, then the topic prompt.",
    "End on your own site: name one thing to check this month, who will check it and how you will know.",
)


def _data() -> dict:
    global _CACHE
    if _CACHE is None:
        with open(_PATH, encoding="utf-8") as fh:
            _CACHE = json.load(fh)
    return _CACHE


def cases() -> list[dict]:
    return sorted(_data()["cases"], key=lambda c: (c["date"], c["id"]))


def country_names() -> dict[str, str]:
    return {**{s["iso3"]: s["name"] for s in country_coverage.states()}, **EXTRA_PLACES}


def resolve_country(key: str) -> str | None:
    k = key.strip().lower()
    for code, name in EXTRA_PLACES.items():
        if k in (code.lower(), name.lower()):
            return code
    s = country_coverage.find(key)
    return s["iso3"] if s else None


def search(text=None, country=None, topic=None, sector=None, event=None, year=None) -> list[dict]:
    code = None
    if country:
        code = resolve_country(country)
        if code is None:
            return []
    out = []
    for c in cases():
        if code and c["iso3"] != code:
            continue
        if topic and topic not in c["topics"]:
            continue
        if sector and sector.lower() not in c["sector"].lower():
            continue
        if event and event.lower() not in [e.lower() for e in c["event_types"]]:
            continue
        if year and not c["date"].startswith(str(year)):
            continue
        if text:
            hay = [c["name"], c["place"], c["substance"], c["what_happened"], *c["causes"], *(x["text"] for x in c["learnings"])]
            if text.lower() not in " ".join(hay).lower():
                continue
        out.append(c)
    return out


def deaths_text(c: dict) -> str:
    d = "not stated" if c["deaths"] is None else str(c["deaths"])
    return d + (" (see note)" if c["deaths_note"] else "")


def best_grade(c: dict) -> str:
    return min(s["grade"] for s in c["sources"])


def sheet(c: dict) -> list[str]:
    """One case as Markdown lines."""
    names = country_names()
    lines = [f"### {c['name']}", "",
             f"`{c['id']}` · {c['date']} · {c['place']}, {names[c['iso3']]} · {c['sector']} · {', '.join(c['event_types'])}"
             + (f" · {c['substance']}" if c["substance"] else ""),
             "", f"**Deaths:** {deaths_text(c)}." + (f" {c['deaths_note']}" if c["deaths_note"] else ""),
             "", f"**What happened.** {c['what_happened']}", "",
             f"**Causes** ({CAUSE_STATUS[c['cause_status']]}):", ""]
    lines += [f"- {x}" for x in c["causes"]]
    lines += ["", "**Key learnings:**", ""]
    lines += [f"- {x['text']} *[{x['basis']}]*" for x in c["learnings"]]
    lines += ["", "**Discuss:**", ""]
    lines += [f"{n}. {q}" for n, q in enumerate(c["questions"], 1)]
    if c["regulatory_aftermath"]:
        lines += ["", f"**Aftermath.** {c['regulatory_aftermath']}"]
    if c.get("support_note"):
        lines += ["", f"**How far the sources go.** {c['support_note']}"]
    lines += ["", "**Topics:** " + ", ".join(TOPICS[t][0] for t in c["topics"])
              + (f". Also in the [CSB register](INCIDENTS.md) as `{c['csb_id']}`." if c.get("csb_id") else "."), "", "**Sources read:**", ""]
    lines += [f"- [{s['grade']}] [{s['title'].replace('[', '(').replace(']', ')')}]({s['url']}), {s['publisher']}" for s in c["sources"]]
    return lines + [""]


def markdown() -> str:
    d, cs, names = _data(), cases(), country_names()
    grades = {g: sum(1 for c in cs if best_grade(c) == g) for g in GRADES}
    lines = ["# Process safety incident casebook", "",
             "Generated from `process_safety/data/incident_casebook.json`. Regenerate with "
             "`python -m process_safety casebook --markdown > docs/INCIDENT_CASEBOOK.md`. Search with "
             "`python -m process_safety casebook --country India` or `--topic facility-siting`.", "",
             "## Read this first", "",
             f"- {len(cs)} historical cases from {len({c['iso3'] for c in cs})} countries and territories, compiled {d['compiled']} for teaching and safety "
             "discussions. It is a **selection**, not a complete record: a country's count says nothing about how safe it is, "
             "and a missing incident is not a minor one.",
             "- Best source read per case: " + ", ".join(f"{g} ({GRADES[g]}) {n}" for g, n in grades.items()) + ". "
             "Grade C accounts need checking against an inquiry report before they are relied on. The grade is that of the best "
             "source, which may support only part of an account: read *How far the sources go* on the case sheet.",
             "- " + d["audit"],
             "- Learnings marked *[source]* are drawn by a source that was read; *[compiler]* are this toolkit's interpretation. "
             "Discussion questions and topic prompts are the compiler's.",
             "- Death tolls are often disputed or revised. `not stated` means the pages read did not give a figure.",
             "- Cases involve real people. Teach the decisions and conditions, not blame.",
             "", "## How to run a case discussion", ""]
    lines += [f"{n}. {x}" for n, x in enumerate(DISCUSSION_METHOD, 1)]
    lines += ["", "## Roster", "", "| Date | Case | Country | Sector | Deaths | Best source |", "|---|---|---|---|---|---|"]
    lines += [f"| {c['date']} | {c['name']} (`{c['id']}`) | {names[c['iso3']]} | {c['sector']} | {deaths_text(c)} | {best_grade(c)} |" for c in cs]
    lines += ["", "## By country", "", "| Country or territory | Cases |", "|---|---|"]
    for code in sorted({c["iso3"] for c in cs}, key=lambda k: names[k]):
        lines.append(f"| {names[code]} | " + ", ".join(f"`{c['id']}`" for c in cs if c["iso3"] == code) + " |")
    lines += ["", "## Key safety discussions", ""]
    for key, (label, prompt, modules) in TOPICS.items():
        hits = [c for c in cs if key in c["topics"]]
        if not hits:
            continue
        lines += [f"### {label}", "", f"**Open with:** {prompt}", "",
                  "**Cases:** " + ", ".join(f"`{c['id']}`" for c in hits), "",
                  "**Toolkit modules:** " + ", ".join(f"`{m}`" for m in modules), ""]
    lines += ["## Case sheets", ""]
    for c in cs:
        lines += sheet(c)
    return "\n".join(lines).rstrip() + "\n"

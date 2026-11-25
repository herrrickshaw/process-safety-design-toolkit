"""Country-by-country safety regime table for industrial assets (`data/country_safety.json`) over the 193 UN members and the two
observer states (`data/un_states.json`).

Each state has seven slots (SLOTS). A slot is 'found' (a name and a link), 'not-found' or 'not-searched'. 'not-found' means this compilation's
searches did not turn one up; it does NOT mean the country has no such law. Entries come from web-search result listings: the
pages were not read (except one Wikipedia table used for some standards bodies), so names, currency and applicability are unconfirmed. EU and EEA membership adds the EU instruments as a
separate regional layer; the national transposition is what applies on site.
"""
from __future__ import annotations

import json
from importlib import resources

from . import standards_library

SLOTS = {
    "standards_body": "National standards body",
    "osh_law": "Occupational safety and health law",
    "major_hazard": "Major hazard / process safety",
    "pressure_equipment": "Boilers and pressure equipment",
    "fire": "Fire safety law or code",
    "electrical": "Electrical safety or wiring code",
    "hazardous_substances": "Petroleum, gas, pipelines, explosives, dangerous goods",
}

EU = ("AUT BEL BGR HRV CYP CZE DNK EST FIN FRA DEU GRC HUN IRL ITA LVA LTU LUX MLT NLD POL PRT ROU SVK SVN ESP SWE").split()
EEA_EFTA = ["ISL", "LIE", "NOR"]
EU_INSTRUMENTS = {
    "osh_law": ["Directive 89/391/EEC"],
    "major_hazard": ["Directive 2012/18/EU"],
    "pressure_equipment": ["Directive 2014/68/EU"],
    "hazardous_substances": ["Directive 2014/34/EU", "Directive 1999/92/EC"],
}

_CACHE: dict[str, dict] = {}


def _load(name: str) -> dict:
    if name not in _CACHE:
        _CACHE[name] = json.loads(resources.files("process_safety").joinpath("data", name).read_text(encoding="utf-8"))
    return _CACHE[name]


def states() -> list[dict]:
    return list(_load("un_states.json")["states"])


def table() -> dict[str, dict]:
    return _load("country_safety.json")["countries"]


def regional(iso3: str) -> dict[str, list[dict]]:
    """EU instruments, from the standards library, for EU members and the three EEA-EFTA states (confirm EEA incorporation)."""
    if iso3 not in EU and iso3 not in EEA_EFTA:
        return {}
    idx = standards_library.by_designation()
    return {slot: [idx[d] for d in ds] for slot, ds in EU_INSTRUMENTS.items()}


def find(key: str) -> dict | None:
    """By ISO3, ISO2 or (part of) the name; None if there is no match or the name matches more than one state."""
    k = key.strip().lower()
    all_states = states()
    for s in all_states:
        if k in (s["iso3"].lower(), s["iso2"].lower(), s["name"].lower()):
            return s
    hits = [s for s in all_states if k and k in s["name"].lower()]
    return hits[0] if len(hits) == 1 else None


def counts() -> dict:
    t = table()
    per_slot = {slot: sum(1 for c in t.values() if c[slot]["status"] == "found") for slot in SLOTS}
    pending = {slot: sum(1 for c in t.values() if c[slot]["status"] == "not-searched") for slot in SLOTS}
    untouched = sum(1 for c in t.values() if all(v["status"] == "not-searched" for k, v in c.items() if k != "standards_body"))
    return {"states": len(t), "slots": len(t) * len(SLOTS), "found": sum(per_slot.values()), "per_slot": per_slot,
            "not_searched": sum(pending.values()), "pending_per_slot": pending, "states_laws_untouched": untouched,
            "not_found": len(t) * len(SLOTS) - sum(per_slot.values()) - sum(pending.values())}


def _cell(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def markdown() -> str:
    d = _load("country_safety.json")
    t, c = table(), counts()
    slots = [v for t_ in t.values() for v in t_.values() if v["status"] == "found"]
    official = sum(1 for v in slots if v["source"] == "official")
    checks: dict[str, int] = {}
    for v in slots:
        k = v.get("check", "unchecked")
        checks[k] = checks.get(k, 0) + 1
    lines = ["# Safety regimes for industrial assets, country by country", "",
             "Generated from `process_safety/data/country_safety.json`. Regenerate with "
             "`python -m process_safety countries --markdown > docs/COUNTRY_SAFETY_COVERAGE.md`. One country: "
             "`python -m process_safety countries NAME_OR_ISO_CODE`.", "",
             "## Read this first", "",
             "* **This is a starting index, not a legal register.** It records one standards body and up to six main laws or codes per "
             "state. It does not list every safety standard in any country.",
             f"* **This table is incomplete.** {c['not_searched']} of {c['slots']} slots have not been searched yet, and for "
             f"{c['states_laws_untouched']} of {c['states']} states none of the six law areas has been searched.",
             "* **The pages were not read.** Entries come from web-search result listings, except standards bodies marked as coming "
             f"from one Wikipedia table (compiled {d['compiled']}). Names, years, whether a law is still in force and whether it applies to your asset are unconfirmed.",
             "* **`not found` is not `none exists`.** It means the searches did not turn one up. **`not searched yet`** means nobody "
             "has looked.",
             "* **Federal and devolved countries** often regulate at state or provincial level.",
             "* **Check** is one automated request: " + ", ".join(f"{k} {v}" for k, v in sorted(checks.items()))
             + ". `robots` = the site's rules disallow this kind of agent, so it was not requested; `blocked` = refused automated "
             "clients; `error` = no answer. A page that loads has not been shown to be the right one.",
             "", "## Spot check", "", d["audit"], "", "## Coverage", "",
             f"{c['states']} states, {c['slots']} slots, {c['found']} found ({100 * c['found'] // c['slots']} %). "
             f"{c['not_found']} searched without a result, {c['not_searched']} not searched yet. Of the found entries, {official} are marked official sources and {len(slots) - official} secondary "
             "(the researcher's classification).", "", "| Area | States with an entry | Not searched yet |", "|---|---|---|"]
    lines += [f"| {label} | {c['per_slot'][slot]} of {c['states']} | {c['pending_per_slot'][slot]} |" for slot, label in SLOTS.items()]
    lines += ["", "## EU and EEA layer", "",
              "For the 27 EU members, and for Iceland, Liechtenstein and Norway (confirm incorporation into the EEA Agreement), the EU "
              "instruments also matter: " + ", ".join(
                  f"[{x}]({standards_library.by_designation()[x]['url']})" for xs in EU_INSTRUMENTS.values() for x in xs)
              + ". National transposition is what applies.", ""]
    by_region: dict[str, list[dict]] = {}
    for s in states():
        by_region.setdefault(s["region"], []).append(s)
    for region in sorted(by_region):
        lines += [f"## {region}", ""]
        for s in sorted(by_region[region], key=lambda x: x["name"]):
            lines += [f"### {s['name']} ({s['iso3']})", "", "| Area | Entry | Source | Check | Note |", "|---|---|---|---|---|"]
            for slot, label in SLOTS.items():
                v = t[s["iso3"]][slot]
                if v["status"] == "found":
                    entry = f"[{_cell(v['name']).replace('[', '(').replace(']', ')')}]({v['url']})"
                    lines.append(f"| {label} | {entry} | {v['source']} | {v.get('check', 'unchecked')} | {_cell(v.get('note', ''))} |")
                else:
                    word = "not searched yet" if v["status"] == "not-searched" else "not found"
                    lines.append(f"| {label} | {word} | | | {_cell(v.get('note', ''))} |")
            lines.append("")
    return "\n".join(lines)

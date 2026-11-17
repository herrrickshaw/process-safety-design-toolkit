"""Catalogue of common process-safety study recommendation types: what usually triggers each, the usual response, which cost scope in
`design_workflow` it maps to, a keyword classifier for free-text recommendations, and the incidents in `docs/INCIDENTS.md` whose CSB
recommendations fall in the category.

"Common" here has a limited basis, stated plainly: no published frequency benchmark of PHA/HAZOP recommendation types was found
(practitioner papers describe categories and good practice but give no counts). The catalogue is built from (1) the recommendation
types the toolkit's own models can trigger (relief, overfill, interface, tube rupture, MDMT, detection, voting), (2) the 17 CSB
recommendations in the incident register, mapped by hand from the text seen, and (3) practitioner categories. Use `tally()` on YOUR
register to get your own frequencies.
"""
from __future__ import annotations

import re

# id: (title, category, usual trigger, usual response, workflow scope, keywords)
CATALOG: dict[str, dict] = {
    "PSV-ADD": dict(title="Add a pressure relief device", category="relief", scope="device",
                    trigger="closed-in equipment that can be overpressured by a credible scenario has no relief device",
                    response="install a PSV (or rupture disk) sized for the governing case and route its discharge to a safe place",
                    keywords=["add psv", "install psv", "install relief", "add relief", "relief valve", "pressure relief", "safety valve", "no relief", "psv", "prv", "rupture disk", "bursting disc", "tube rupture relief"]),
    "PSV-UPSIZE": dict(title="Resize the relief device", category="relief", scope="device",
                       trigger="required relieving area exceeds the installed orifice for the governing case (fire, blocked outlet, control valve failure)",
                       response="replace with the next API 526 orifice or add a valve; re-check inlet and outlet piping",
                       keywords=["resize", "upsize", "larger psv", "larger relief", "orifice", "relief capacity", "psv capacity", "psv sizing", "relief sizing", "inadequate relief", "insufficient relief"]),
    "RELIEF-PIPING": dict(title="Fix relief inlet/outlet piping losses or back pressure", category="relief", scope="device",
                          trigger="inlet loss above the 3% rule at rated capacity, or built-up back pressure above the valve's limit",
                          response="enlarge or shorten the inlet line, relocate the valve, use a balanced or pilot-operated valve, enlarge the outlet header",
                          keywords=["inlet line", "inlet loss", "pressure drop", "back pressure", "backpressure", "3%", "outlet header", "relief line"]),
    "FLARE-LOAD": dict(title="Check flare/vent header capacity or route relief to a safe location", category="relief", scope="reroute",
                       trigger="coincident relief loads exceed header or flare capacity, or a flammable/toxic vent discharges to atmosphere",
                       response="re-rate the header, reroute or add a header, add a knock-out drum, or move the discharge to the flare",
                       keywords=["flare", "header", "vent to safe", "discharge to atmosphere", "atmospheric vent", "knock-out", "ko drum", "reroute", "re-route"]),
    "BDV": dict(title="Add or resize blowdown / emergency depressuring", category="relief", scope="device",
                trigger="a vapour-filled vessel in a fire ruptures before the PSV protects it, or inventory must be reduced quickly",
                response="add a remotely operated blowdown valve sized for the target depressuring time; check MDMT and flare load",
                keywords=["blowdown", "depressur", "bdv", "emergency depressuring", "fire case vapour"]),
    "HLL-SIF": dict(title="Independent high-level protection (alarm and trip)", category="instrumented", scope="sensors",
                    trigger="time to overfill is short compared with operator response plus valve closure, or overfill leads to a major release",
                    response="independent level sensor and logic with trip to stop the inflow, sized by LOPA/SIL, proof-tested",
                    keywords=["high level", "high-high", "overfill", "lahh", "lshh", "level alarm", "independent level", "level trip"]),
    "SIF-UPGRADE": dict(title="Upgrade a safety instrumented function (voting, SIL, proof test)", category="instrumented", scope="sensors",
                        trigger="LOPA shows a risk reduction gap, or a trip uses a single sensor with an unacceptable PFD or spurious trip rate",
                        response="redundant sensors with voting (for example 2oo3), shorter proof-test interval, SIL verification",
                        keywords=["sil", "sif", "voting", "2oo3", "1oo2", "proof test", "safety instrumented", "interlock", "trip"]),
    "ALARM": dict(title="Add or rationalise an alarm", category="instrumented", scope="pcn",
                  trigger="a deviation has no alarm, or alarm flooding hides the critical one",
                  response="add the alarm with a defined response, rationalise priorities and set points",
                  keywords=["alarm", "annunciat", "operator display"]),
    "DETECT": dict(title="Add gas, fire or flame detection", category="mitigation", scope="sensors",
                   trigger="flammable or toxic inventory with no detection, or detector coverage gaps",
                   response="add detectors with voting and executive actions (alarm, shutdown, isolation) mapped to coverage targets",
                   keywords=["gas detector", "flame detector", "fire detector", "detection", "f&g", "fire and gas", "h2s detector"]),
    "ISOLATION": dict(title="Remote / emergency isolation of inventory", category="mitigation", scope="device",
                      trigger="a large flammable or toxic inventory can only be isolated manually after a release",
                      response="remotely operated shutdown valves with fire-safe design, position indication and a defined closure time",
                      keywords=["remote isolation", "remotely operated", "esd", "shutdown valve", "sdv", "emergency isolation", "block valve", "isolation valve"]),
    "INTERFACE-DP": dict(title="Protect the high/low pressure interface", category="relief", scope="device",
                         trigger="upstream operating pressure exceeds downstream design pressure (control valve failure, reverse flow, tube rupture)",
                         response="raise the downstream design pressure, add relief sized for the blow-by, or add check valves / trips against reverse flow",
                         keywords=["design pressure", "hp/lp", "high pressure", "low pressure", "downstream", "interface", "tube rupture", "check valve", "backflow", "reverse flow", "blow-by", "blowby"]),
    "MATERIAL": dict(title="Materials, MDMT, damage mechanisms and inspection", category="integrity", scope="mechanical",
                     trigger="depressuring or process cooling takes metal below its MDMT, or a damage mechanism (HTHA, sulfidation, corrosion) applies",
                     response="upgrade materials, limit depressuring rate, add inspection or monitoring, revise operating limits",
                     keywords=["mdmt", "brittle", "low temperature", "corrosion", "material", "htha", "hydrogen attack", "sulfidation", "sulphidation", "metallurgy", "inspection programme"]),
    "FIRE-PROT": dict(title="Passive or active fire protection", category="mitigation", scope="mechanical",
                      trigger="fire exposure can fail supports or vessels before relief or blowdown works",
                      response="passive fireproofing of supports and vessels, fire water or deluge, drainage",
                      keywords=["fireproof", "pfp", "fire water", "deluge", "fire protection", "fire insulation", "water spray"]),
    "LAYOUT": dict(title="Siting, layout, blast and occupied buildings", category="mitigation", scope="civil",
                   trigger="occupied buildings or ignition sources lie within the effect distances of a credible event",
                   response="relocate, blast-harden, add distance or barriers, limit occupancy",
                   keywords=["blast", "siting", "occupied building", "relocate", "separation distance", "layout", "control room location"]),
    "HAC": dict(title="Hazardous area classification and electrical equipment", category="electrical", scope="electrical",
                trigger="equipment or cabling in a classified zone is not suitably rated or an ignition source is unmanaged",
                response="reclassify, replace with correctly rated equipment, improve earthing and static control",
                keywords=["hazardous area", "ex rated", "ex-rated", "classification", "ignition source", "earthing", "bonding", "static", "atex"]),
    "PROCEDURE": dict(title="Procedure, training, management of change, pre-startup review", category="administrative", scope="none",
                      trigger="a hazard depends on correct human action, a change was made without review, or transient modes are not analysed",
                      response="written procedure with checks, training and competence, MOC and PSSR, start-up and shutdown hazard analysis",
                      keywords=["procedure", "training", "moc", "management of change", "pssr", "pre-startup", "competence", "permit", "awareness", "marking", "labelling"]),
    "INSPECT-TEST": dict(title="Inspection, testing and maintenance regime", category="integrity", scope="opex",
                         trigger="a safeguard has no defined test interval or evidence of testing",
                         response="define and record proof-test and inspection intervals and acceptance criteria",
                         keywords=["test frequency", "testing", "calibrat", "maintenance", "inspect", "mechanical integrity"]),
    "DEADLEG": dict(title="Dead legs, low points and draining", category="integrity", scope="reroute",
                    trigger="stagnant sections allow polymerisation, corrosion, water accumulation or freezing",
                    response="remove or flush dead legs, add drains, change the line route or isolate spare equipment properly",
                    keywords=["dead leg", "deadleg", "low point", "drain", "popcorn", "stagnant", "spare pump"]),
    "DUST": dict(title="Combustible dust controls", category="mitigation", scope="mechanical",
                 trigger="dust accumulation or dispersion with an ignition source",
                 response="dust hazard analysis, housekeeping, explosion vents or suppression, ignition control",
                 keywords=["dust", "explosion vent", "housekeeping", "dust collector"]),
    "CYBER-PCN": dict(title="Process control network and OT cybersecurity", category="instrumented", scope="pcn",
                      trigger="safety or control functions run on a network without segregation, access control or monitoring",
                      response="segment the network, add firewalls and access control, monitoring and patching, change control for configuration",
                      keywords=["cyber", "network", "firewall", "pcn", "dcs", "plc", "ot security", "remote access"]),
    "INHERENT": dict(title="Inherently safer alternative", category="inherent", scope="none",
                     trigger="a hazardous method or inventory can be removed or reduced instead of protected",
                     response="eliminate, substitute, minimise or simplify (for example air blow instead of natural gas blow)",
                     keywords=["inherently safer", "eliminate", "substitut", "reduce inventory", "minimi", "alternative method"]),
}

# CSB recommendations seen on the investigation pages (docs/INCIDENTS.md), mapped by hand from the text captured. Partly captured or
# unrelated texts are not mapped.
CSB_EVIDENCE = {
    "kleen-energy-2010": ["INHERENT"], "tesoro-anacortes-2010": ["MATERIAL"], "chevron-richmond-2012": ["MATERIAL"],
    "imperial-sugar-2008": ["DUST"], "didion-2017": ["DUST", "PROCEDURE"], "capeco-2009": ["HLL-SIF"],
    "tpc-2019": ["DEADLEG"], "williams-olefins-2013": ["PSV-UPSIZE", "BDV"], "pemex-2024": ["PROCEDURE"], "west-fertilizer-2013": ["PROCEDURE"],
}

SCOPE_NOTE = {"device": "design_workflow device scope (PSV, inlet line, blowdown valve)", "reroute": "design_workflow pipeline rerouting scope",
              "sensors": "design_workflow additional sensors scope", "pcn": "design_workflow PCN modification scope",
              "civil": "recommendation_cost lines (civil)", "electrical": "recommendation_cost lines (electrical)",
              "mechanical": "recommendation_cost lines (mechanical)", "opex": "opex book (test and inspection cost)", "none": "no capital scope (procedure / design choice)"}


def _has(t: str, kw: str) -> bool:
    """Keyword test: short keywords (4 characters or fewer, such as sil, psv, moc) must stand alone as words, so 'sil' does not match 'silver'."""
    if len(kw) <= 4:
        return re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", t) is not None
    return kw in t


def classify(text: str) -> list[str]:
    """Catalogue ids whose keywords appear in the text, best match first (number of keyword hits, then catalogue order)."""
    t = " " + re.sub(r"\s+", " ", (text or "").lower()) + " "
    hits = []
    for i, (cid, c) in enumerate(CATALOG.items()):
        n = sum(1 for k in c["keywords"] if _has(t, k))
        if n:
            hits.append((-n, i, cid))
    return [cid for _, _, cid in sorted(hits)]


def tally(texts: list[str]) -> dict:
    """Count recommendations by catalogue id (a text can count in more than one) and list those that match nothing."""
    counts = {cid: 0 for cid in CATALOG}
    unmatched = []
    for t in texts:
        ids = classify(t)
        if not ids:
            unmatched.append(t)
        for cid in ids[:2]:                 # at most the two best matches, so a long sentence does not count everywhere
            counts[cid] += 1
    return {"counts": {k: v for k, v in sorted(counts.items(), key=lambda kv: -kv[1]) if v}, "unmatched": unmatched, "n": len(texts)}


def csb_tally() -> dict:
    counts: dict[str, int] = {}
    for ids in CSB_EVIDENCE.values():
        for i in ids:
            counts[i] = counts.get(i, 0) + 1
    return {"counts": dict(sorted(counts.items(), key=lambda kv: -kv[1])), "incidents_mapped": len(CSB_EVIDENCE), "incidents_in_register": 17}


def markdown() -> str:
    lines = ["# Common recommendation types", "",
             "Generated from `process_safety/recommendation_catalog.py`. Regenerate: `python -m process_safety catalog --markdown > docs/RECOMMENDATIONS_CATALOG.md`.", "",
             "**Basis of 'common'.** No published frequency benchmark of HAZOP/PHA recommendation types was found. This list comes from the recommendation types the toolkit's models can trigger, the 17 CSB recommendations in `docs/INCIDENTS.md` (mapped by hand, column CSB) and practitioner categories. For real frequencies, run `python -m process_safety tool plant` on your own register.", "",
             "| Id | Recommendation | Category | Usual trigger | Usual response | Cost scope | CSB |", "|---|---|---|---|---|---|---|"]
    csb = {}
    for inc, ids in CSB_EVIDENCE.items():
        for i in ids:
            csb.setdefault(i, []).append(inc)
    for cid, c in CATALOG.items():
        lines.append(f"| {cid} | {c['title']} | {c['category']} | {c['trigger']} | {c['response']} | {SCOPE_NOTE[c['scope']]} | {len(csb.get(cid, []))} |")
    lines += ["", "CSB column: number of the 17 investigations whose recommendation maps to the type (n is small; it shows coverage, not frequency).", ""]
    return "\n".join(lines)

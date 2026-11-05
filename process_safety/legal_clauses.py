"""Legal clauses that bear on derogations and design change, by jurisdiction.

A company derogation (see `compliance`) cannot waive a law. What the law does say about the same situation falls into four topics:

    general-duty   a standing duty to take the necessary measures, and to be able to prove it
    change         management of change / modification of a covered installation or process
    notify         informing the regulator or updating the safety documents before a change
    exemption      the only route by which a legal duty can be set aside (a variance, exemption or prohibition notice)

Each entry says what the provision requires (paraphrased, never quoted at length), what it means for a derogation, where it is, and how it
was checked: grade A = the legal text was read for the toolkit on the date shown; grade B = read only in a regulator's guidance or a
secondary source, so the wording and numbering must be checked against the legislation. Jurisdictions not listed here have not been read:
`docs/REGULATORY_LANDSCAPE.md` lists the regimes of other countries (Singapore, Australia, India, Canada, Korea, Gulf and others) with
their own read/not-read grades. This is a finding aid, not legal advice.
"""
from __future__ import annotations

TOPICS = ("general-duty", "change", "notify", "exemption")
CHECKED = "2026-11-06"

CLAUSES = [
    {"id": "EU-SEVESO-5", "region": "EU", "instrument": "Directive 2012/18/EU (Seveso III)", "provision": "Art. 5", "topic": "general-duty", "grade": "A",
     "requires": "The operator must take all necessary measures to prevent major accidents and limit their consequences, and must be able to prove this to the competent authority at any time.",
     "for_derogations": "A derogation is part of the evidence, not a way out of the duty: keep the register, risk assessments and compensating measures producible on request.",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018"},
    {"id": "EU-SEVESO-7-4", "region": "EU", "instrument": "Directive 2012/18/EU (Seveso III)", "provision": "Art. 7(4)", "topic": "notify", "grade": "A",
     "requires": "The operator informs the competent authority in advance of a significant change in the substances or processes, or a modification of an establishment or installation that could have significant consequences for major-accident hazards.",
     "for_derogations": "A derogation that changes a major-accident scenario can trigger advance notice.",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018"},
    {"id": "EU-SEVESO-10", "region": "EU", "instrument": "Directive 2012/18/EU (Seveso III)", "provision": "Art. 10(1)(c), 10(5)", "topic": "notify", "grade": "A",
     "requires": "An upper-tier safety report must show adequate safety and reliability in design, construction, operation and maintenance; it is reviewed at least every five years and after changes or new knowledge.",
     "for_derogations": "Accepted derogations and their compensating measures belong in the safety report.",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018"},
    {"id": "EU-SEVESO-11", "region": "EU", "instrument": "Directive 2012/18/EU (Seveso III)", "provision": "Art. 11", "topic": "change", "grade": "A",
     "requires": "For a modification that could have significant consequences for major-accident hazards, the operator reviews and where necessary updates the notification, MAPP, safety management system and safety report, and informs the competent authority of the details in advance.",
     "for_derogations": "Screen each MUST derogation (and any rated high or severe) as a possible Art. 11 modification.",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018"},
    {"id": "EU-SEVESO-19", "region": "EU", "instrument": "Directive 2012/18/EU (Seveso III)", "provision": "Art. 19", "topic": "exemption", "grade": "A",
     "requires": "Member states prohibit use where prevention and mitigation measures are seriously deficient, and may prohibit it where required information was not submitted in time.",
     "for_derogations": "The enforcement end of the same regime: an unassessed or unreported derogation is the kind of gap that supports a finding. No operator-level exemption exists in this article.",
     "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018"},
    {"id": "US-OSHA-119-l", "region": "US", "instrument": "29 CFR 1910.119 (OSHA process safety management)", "provision": "(l) Management of change", "topic": "change", "grade": "A",
     "requires": "Written procedures to manage changes (except replacements in kind) to process chemicals, technology, equipment and procedures, and facility changes affecting a covered process. Before any change: technical basis, impact on safety and health, changes to operating procedures, time needed, and authorization requirements. Affected employees are informed and trained before start-up; process safety information and procedures are updated.",
     "for_derogations": "Departing from a design requirement on a covered process is a change: run it through the MOC procedure, including authorization, before it is implemented. The tiered sign-off in `compliance` can serve as the authorization record.",
     "url": "https://www.ecfr.gov/current/title-29/section-1910.119"},
    {"id": "US-EPA-68-75", "region": "US", "instrument": "40 CFR Part 68 (EPA Risk Management Program)", "provision": "§ 68.75 Management of change", "topic": "change", "grade": "A",
     "requires": "Same structure as OSHA's: written change procedures, with technical basis, impact on safety and health, operating procedure changes, time period and authorization addressed before any change; training before start-up; updated process safety information.",
     "for_derogations": "As for OSHA: a derogation on a covered process is a change needing MOC authorization.",
     "url": "https://www.ecfr.gov/current/title-40/section-68.75"},
    {"id": "US-OSHA-1905", "region": "US", "instrument": "29 CFR Part 1905 (rules of practice for OSHA variances)", "provision": "§ 1905.1 and Part 1905 generally", "topic": "exemption", "grade": "A",
     "requires": "The procedure for granting variances from OSHA standards under sections 6(b)(6)(A) and 6(d) of the OSH Act. Only the Department of Labor can grant a variance; the scope paragraph and definitions were read, not the full procedure.",
     "for_derogations": "An internal derogation is not a variance. A departure from an OSHA standard needs an OSHA variance; a departure from a company practice that merely exceeds OSHA is the company's own to derogate.",
     "url": "https://www.ecfr.gov/current/title-29/part-1905"},
    {"id": "UK-COMAH-5", "region": "UK (Great Britain)", "instrument": "Control of Major Accident Hazards Regulations 2015", "provision": "Reg. 5 (general duty)", "topic": "general-duty", "grade": "B",
     "requires": "Take all measures necessary to prevent major accidents and limit their consequences to people and the environment (HSE guidance; implements Seveso III, outside the EU since Brexit).",
     "for_derogations": "Same position as Seveso Art. 5. The regulation numbers for safety-report review and modification were not confirmed: check legislation.gov.uk.",
     "url": "https://www.hse.gov.uk/comah/comah15.htm"},
]
for _c in CLAUSES:
    _c["checked"] = CHECKED


def search(text: str | None = None, region: str | None = None, topic: str | None = None) -> list[dict]:
    out = []
    for c in CLAUSES:
        if region and region.lower() not in c["region"].lower():
            continue
        if topic and c["topic"] != topic:
            continue
        if text and text.lower() not in " ".join(str(v) for v in c.values()).lower():
            continue
        out.append(c)
    return out


def markdown() -> str:
    lines = ["# Legal clauses that bear on derogations and design change", "",
             f"Generated from `process_safety/legal_clauses.py` (checked {CHECKED}); a test keeps this file in sync. Regenerate: `python -m process_safety legal-clauses --markdown > docs/LEGAL_CLAUSES.md`. "
             "Search: `python -m process_safety legal-clauses [TEXT] [--region R] [--topic T]`.", "",
             "A company derogation cannot waive a law. The clauses below are what the law says about the same ground: a standing duty (**general-duty**), **change** control, "
             "**notify**ing the regulator or updating safety documents, and the only route that sets a legal duty aside (**exemption**).",
             "Grade **A**: the legal text was read for the toolkit. Grade **B**: seen only in regulator guidance or a secondary source; confirm against the legislation. "
             "Paraphrased; not legal advice.", "",
             f"{len(CLAUSES)} clauses from {len({c['region'] for c in CLAUSES})} regimes. **Not yet read** (see `docs/REGULATORY_LANDSCAPE.md` for what is known): Australia (WHS major hazard facilities), Singapore, "
             "India, Canada, South Korea, China, Japan, Brazil, Norway, the Gulf states and others.", ""]
    for t in TOPICS:
        rows = [c for c in CLAUSES if c["topic"] == t]
        if not rows:
            continue
        lines += [f"## {t}", "", "| Region | Provision | Requires | For a derogation | Grade |", "|---|---|---|---|---|"]
        for c in rows:
            lines.append(f"| {c['region']} | [{c['instrument']}, {c['provision']}]({c['url']}) | {c['requires']} | {c['for_derogations']} | {c['grade']} |")
        lines.append("")
    return "\n".join(lines)

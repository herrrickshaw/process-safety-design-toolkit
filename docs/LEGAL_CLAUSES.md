# Legal clauses that bear on derogations and design change

Generated from `process_safety/legal_clauses.py` (checked 2026-11-06); a test keeps this file in sync. Regenerate: `python -m process_safety legal-clauses --markdown > docs/LEGAL_CLAUSES.md`. Search: `python -m process_safety legal-clauses [TEXT] [--region R] [--topic T]`.

A company derogation cannot waive a law. The clauses below are what the law says about the same ground: a standing duty (**general-duty**), **change** control, **notify**ing the regulator or updating safety documents, and the only route that sets a legal duty aside (**exemption**).
Grade **A**: the legal text was read for the toolkit. Grade **B**: seen only in regulator guidance or a secondary source; confirm against the legislation. Paraphrased; not legal advice.

9 clauses from 3 regimes. **Not yet read** (see `docs/REGULATORY_LANDSCAPE.md` for what is known): Australia (WHS major hazard facilities), Singapore, India, Canada, South Korea, China, Japan, Brazil, Norway, the Gulf states and others.

## general-duty

| Region | Provision | Requires | For a derogation | Grade |
|---|---|---|---|---|
| EU | [Directive 2012/18/EU (Seveso III), Art. 5](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | The operator must take all necessary measures to prevent major accidents and limit their consequences, and must be able to prove this to the competent authority at any time. | A derogation is part of the evidence, not a way out of the duty: keep the register, risk assessments and compensating measures producible on request. | A |
| UK (Great Britain) | [Control of Major Accident Hazards Regulations 2015, Reg. 5 (general duty)](https://www.hse.gov.uk/comah/comah15.htm) | Take all measures necessary to prevent major accidents and limit their consequences to people and the environment (HSE guidance; implements Seveso III, outside the EU since Brexit). | Same position as Seveso Art. 5. The regulation numbers for safety-report review and modification were not confirmed: check legislation.gov.uk. | B |

## change

| Region | Provision | Requires | For a derogation | Grade |
|---|---|---|---|---|
| EU | [Directive 2012/18/EU (Seveso III), Art. 11](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | For a modification that could have significant consequences for major-accident hazards, the operator reviews and where necessary updates the notification, MAPP, safety management system and safety report, and informs the competent authority of the details in advance. | Screen each MUST derogation (and any rated high or severe) as a possible Art. 11 modification. | A |
| US | [29 CFR 1910.119 (OSHA process safety management), (l) Management of change](https://www.ecfr.gov/current/title-29/section-1910.119) | Written procedures to manage changes (except replacements in kind) to process chemicals, technology, equipment and procedures, and facility changes affecting a covered process. Before any change: technical basis, impact on safety and health, changes to operating procedures, time needed, and authorization requirements. Affected employees are informed and trained before start-up; process safety information and procedures are updated. | Departing from a design requirement on a covered process is a change: run it through the MOC procedure, including authorization, before it is implemented. The tiered sign-off in `compliance` can serve as the authorization record. | A |
| US | [40 CFR Part 68 (EPA Risk Management Program), § 68.75 Management of change](https://www.ecfr.gov/current/title-40/section-68.75) | Same structure as OSHA's: written change procedures, with technical basis, impact on safety and health, operating procedure changes, time period and authorization addressed before any change; training before start-up; updated process safety information. | As for OSHA: a derogation on a covered process is a change needing MOC authorization. | A |

## notify

| Region | Provision | Requires | For a derogation | Grade |
|---|---|---|---|---|
| EU | [Directive 2012/18/EU (Seveso III), Art. 7(4)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | The operator informs the competent authority in advance of a significant change in the substances or processes, or a modification of an establishment or installation that could have significant consequences for major-accident hazards. | A derogation that changes a major-accident scenario can trigger advance notice. | A |
| EU | [Directive 2012/18/EU (Seveso III), Art. 10(1)(c), 10(5)](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | An upper-tier safety report must show adequate safety and reliability in design, construction, operation and maintenance; it is reviewed at least every five years and after changes or new knowledge. | Accepted derogations and their compensating measures belong in the safety report. | A |

## exemption

| Region | Provision | Requires | For a derogation | Grade |
|---|---|---|---|---|
| EU | [Directive 2012/18/EU (Seveso III), Art. 19](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32012L0018) | Member states prohibit use where prevention and mitigation measures are seriously deficient, and may prohibit it where required information was not submitted in time. | The enforcement end of the same regime: an unassessed or unreported derogation is the kind of gap that supports a finding. No operator-level exemption exists in this article. | A |
| US | [29 CFR Part 1905 (rules of practice for OSHA variances), § 1905.1 and Part 1905 generally](https://www.ecfr.gov/current/title-29/part-1905) | The procedure for granting variances from OSHA standards under sections 6(b)(6)(A) and 6(d) of the OSH Act. Only the Department of Labor can grant a variance; the scope paragraph and definitions were read, not the full procedure. | An internal derogation is not a variance. A departure from an OSHA standard needs an OSHA variance; a departure from a company practice that merely exceeds OSHA is the company's own to derogate. | A |

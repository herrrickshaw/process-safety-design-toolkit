# Compliance tiers and derogations

Design practices and standards do not all bind equally. The toolkit tracks a project's position against each requirement by **tier**, and treats a departure from a binding requirement as a formal, approved **derogation**.

| Tier | Source wording | Position allowed | What a departure needs |
|---|---|---|---|
| **MUST** | "shall", "must", "is required to", and every "shall not" | complied, derogated, not-applicable (with a reason), open | a **derogation**: justification, risk assessment reference, at least one compensating measure, an expiry or review date, a consequence assessment (scenario, safety severity, PESTLE), and the sign-offs the approval matrix requires |
| **SHOULD** | "should", "is recommended" | complied, derogated, not-applicable, open | **comply or explain**: a written justification, a consequence rating, and the (lighter) sign-offs the matrix gives it; an expiry is optional |
| **CAN** | "may", "can", "is permitted" | adopted, not-adopted, not-applicable, open | nothing: the clause is optional, so it cannot be derogated; record whether it was adopted |

A clause marked `"statutory": true` (a law or licence condition, not a company or industry practice) **cannot be derogated internally**. The only route is an exemption from the regulator, recorded as `regulator_ref`.

## Approval matrix: TA1, TA2, TA3
Who must sign a derogation depends on the tier and on the **consequence class** if the departure goes wrong. Technical authority levels run **TA3** (lowest: site / discipline) < **TA2** (project / regional discipline) < **TA1** (highest: corporate / principal). A higher level can sign in place of a lower required one, but each required sign-off needs a different person.

| Tier | low | medium | high | severe |
|---|---|---|---|---|
| MUST | TA2 | TA2 | TA1 | TA1 + TA2 |
| SHOULD | TA3 | TA3 | TA2 | TA1 |

`python3 -m process_safety compliance --matrix` prints this table from the code. The consequence class is the **highest** of the safety severity and the six PESTLE ratings (each 0-5): up to 2 is low, 3 medium, 4 high, 5 severe. With no consequence assessment the matrix uses **severe** (and, for a MUST clause, an issue is raised), so skipping the assessment never lowers the approval needed.

## PESTLE: mapping the management consequence
For each derogation the consequence scenario is mapped across **P**olitical, **E**conomic, **S**ocial, **T**echnological, **L**egal and **E**nvironmental factors. Each gets a 0-5 rating and a note; a factor rated 3 or more needs a **management action** (for example a spare pump and insurance cover for an economic impact, or agreeing a permit condition with the regulator for a legal one). A MUST derogation must address all six factors (a rating of 0 with a note counts); a SHOULD derogation may give only those that apply.

| Factor | Typical question for the failure scenario |
|---|---|
| Political | Does it attract government, community-leader or host-state attention, or affect licence to operate? |
| Economic | Lost production, repair and clean-up cost, insurance, contractual penalties? |
| Social | People harmed or affected on and off site, workforce confidence, public concern? |
| Technological | Does it depend on a single technology, detector or system; could it spread to other equipment or controls? |
| Legal | Breach of a permit, licence or regulation; enforcement notice; liability? |
| Environmental | Release to air, water or ground; duration and recovery? |

The output's `derogation_reviews` lists, for each derogated clause, the consequence class, the factors that set it (`driven_by`), the sign-offs required, present and unmet, the scenario and the full PESTLE map with its management actions.

## Follow-up: how derogations affect EC (EU) compliance
**A derogation is an internal instrument. It cannot waive a legal requirement.** European Commission law reaches a site through directives that member states transpose into national law, and the only party that can exempt a legal duty is the member-state competent authority. What this means for a register:

| Situation | Rule in the toolkit |
|---|---|
| The clause **is** the EU legal text (`legal_basis.relation: "is"`) | Cannot be derogated internally. Record the competent authority's exemption in `regulator_ref`, or the clause stays an issue (`statutory-no-exemption`). |
| The clause **implements** an EU duty (company practice that exists to meet the law, `relation: "implements"`) | May be derogated only with an `eu_equivalence` statement showing the alternative still meets the legal duty. Its consequence class is **at least `high`**, so the matrix asks for more senior sign-off. |
| The site is a **Seveso III establishment** (`"seveso": "lower"` or `"upper"` on the register) | Every MUST derogation, and any derogation rated high or severe, is screened as a possible **modification** (Article 11). |

**Seveso III, Directive 2012/18/EU** (text read from EUR-Lex, 2026-11-06; wording below paraphrased):
* **Article 5**: the operator must take all necessary measures to prevent major accidents and limit their consequences, and must be able to **prove this to the competent authority at any time**. The derogation register, with its risk assessments and compensating measures, is part of that proof, so keep it current and producible.
* **Article 11**: for a modification of an installation, establishment, storage facility or process that could have significant consequences for major-accident hazards, the operator reviews and where necessary updates the **notification, the MAPP, the safety management system and the safety report**, and **informs the competent authority of the details in advance**. A derogation that changes a credible major-accident scenario (for example the vent-release case) is exactly that kind of change. Article 7(4) also requires advance notice of such modifications.
* **Article 10**: an upper-tier safety report must show adequate safety and reliability in design (10(1)(c)) and be reviewed at least every five years and after changes (10(5)). Accepted derogations and their compensating measures belong in it.
* **Article 19**: a member state may prohibit use where prevention and mitigation measures are seriously deficient, or required information was not submitted. An unassessed or unreported derogation is the sort of gap that feeds that finding.

For each screened derogation the register records `seveso_assessment`: `significant` (true/false), a `rationale`, and, if significant, the date `authority_informed` and the list of `documents_updated` (notification, MAPP, safety management system, plus the safety report for upper tier). Issues raised: `seveso-not-assessed`, `seveso-authority-not-informed`, `seveso-documents-not-updated`, `eu-equivalence-not-shown`.

The output's `eu_compliance` block lists the non-derogable EU clauses, the derogations that implement EU duties, those screened for Article 11, those found significant, those not yet assessed, and the documents to update.

Other jurisdictions: `python3 -m process_safety legal-clauses` (docs/LEGAL_CLAUSES.md) lists the provisions read so far for the EU, the US (OSHA PSM and EPA RMP management of change, OSHA variances), the UK, Australia (Commonwealth WHS major hazard facilities), Singapore, India (Factories Act, MSIHC Rules), Canada (federal) and South Korea. The cost side, how a derogation moves the insurance premium and retained loss, is in `docs/INSURANCE_IMPACT.md`.

**What is and is not covered.** Only Seveso III was read for this feature, and only the articles above are encoded. ATEX (equipment and workplace), the Pressure Equipment Directive, the Industrial Emissions Directive and national transposition (for example COMAH in Great Britain, which is outside the EU) are not encoded: use `legal_basis` to mark such clauses, but check the legal text yourself. A "not significant" finding is the operator's judgement and may be challenged by the competent authority. Seveso issues on a SHOULD departure do not block `ready_for_gate`; they remain in the issue list. This is not legal advice.

## Use
```bash
# check a register (the shipped example has deliberate faults: an expired derogation, a junior approver, a statutory clause)
python3 -m process_safety compliance process_safety/examples/compliance.json

# start a register from a requirements extract: every clause begins "open", tier set from its modal verb
python3 -m process_safety compliance --init requirements_out/my_requirements.csv --out requirements_out/register.json
```
The register is JSON: `{"as_of": "YYYY-MM-DD", "clauses": [{"id", "tier", "status", "text", "derogation": {"justification", "risk_assessment_ref", "compensating_measures", "expiry", "consequence": {"scenario", "safety_severity", "pestle": {factor: {"rating", "note"}}, "management_actions": {factor: text}}, "approvals": [{"level": "TA1", "name"}]}, "statutory", "regulator_ref", "na_reason", "legal_basis": {"regime": "EU", "instrument", "article", "relation": "is|implements"}}], "seveso": "lower|upper"}`. The shipped example shows each field. `--as-of` overrides the date used for expiry checks.

The output gives counts by tier and status, MUST compliance (complied plus validly derogated, over applicable clauses), the share of SHOULD clauses complied with, the derogations in force, a list of issues, and `ready_for_gate`. That flag is false while any MUST clause is open or has an incomplete, expired or improperly approved derogation. Open or departed SHOULD clauses are reported but do not block it.

Issue codes: `open`, `no-justification`, `no-risk-assessment`, `no-compensating-measures`, `no-expiry`, `no-consequence-assessment`, `no-scenario`, `pestle-incomplete`, `pestle-no-action`, `not-approved`, `approval-insufficient`, `unknown-approver-level`, `expired`, `bad-date`, `na-no-reason`, `statutory-no-exemption`, `eu-equivalence-not-shown`, `seveso-not-assessed`, `seveso-authority-not-informed`, `seveso-documents-not-updated`.

## Limits
* **The levels, the 0-5 scale, the class thresholds and the matrix cells are defaults, not any company's rules.** TA1 as the highest level and TA3 as the lowest is an assumption about common usage; edit `APPROVER_LEVELS`, `CLASS_THRESHOLDS` and `APPROVAL_MATRIX` in `process_safety/compliance.py` to match your own procedure. The ratings are the assessor's judgement; the tool does not derive them.
* **It checks completeness and consistency, not adequacy.** It cannot judge whether a justification is technically sound or the compensating measures are enough. A passing register is not an approval.
* **The requirements extractor does not detect CAN.** It finds "shall", "should" and prohibitions only (permissive "may" and "can" are too common in ordinary prose), so CAN clauses are added by hand.
* A register built with `--init` contains extracted statement text. Like the extract it came from, keep it outside version control: the command refuses an output path inside a repository unless git ignores it.

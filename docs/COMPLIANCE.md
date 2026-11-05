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

## Use
```bash
# check a register (the shipped example has deliberate faults: an expired derogation, a junior approver, a statutory clause)
python3 -m process_safety compliance process_safety/examples/compliance.json

# start a register from a requirements extract: every clause begins "open", tier set from its modal verb
python3 -m process_safety compliance --init requirements_out/my_requirements.csv --out requirements_out/register.json
```
The register is JSON: `{"as_of": "YYYY-MM-DD", "clauses": [{"id", "tier", "status", "text", "derogation": {"justification", "risk_assessment_ref", "compensating_measures", "expiry", "consequence": {"scenario", "safety_severity", "pestle": {factor: {"rating", "note"}}, "management_actions": {factor: text}}, "approvals": [{"level": "TA1", "name"}]}, "statutory", "regulator_ref", "na_reason"}]}`. The shipped example shows each field. `--as-of` overrides the date used for expiry checks.

The output gives counts by tier and status, MUST compliance (complied plus validly derogated, over applicable clauses), the share of SHOULD clauses complied with, the derogations in force, a list of issues, and `ready_for_gate`. That flag is false while any MUST clause is open or has an incomplete, expired or improperly approved derogation. Open or departed SHOULD clauses are reported but do not block it.

Issue codes: `open`, `no-justification`, `no-risk-assessment`, `no-compensating-measures`, `no-expiry`, `no-consequence-assessment`, `no-scenario`, `pestle-incomplete`, `pestle-no-action`, `not-approved`, `approval-insufficient`, `unknown-approver-level`, `expired`, `bad-date`, `na-no-reason`, `statutory-no-exemption`.

## Limits
* **The levels, the 0-5 scale, the class thresholds and the matrix cells are defaults, not any company's rules.** TA1 as the highest level and TA3 as the lowest is an assumption about common usage; edit `APPROVER_LEVELS`, `CLASS_THRESHOLDS` and `APPROVAL_MATRIX` in `process_safety/compliance.py` to match your own procedure. The ratings are the assessor's judgement; the tool does not derive them.
* **It checks completeness and consistency, not adequacy.** It cannot judge whether a justification is technically sound or the compensating measures are enough. A passing register is not an approval.
* **The requirements extractor does not detect CAN.** It finds "shall", "should" and prohibitions only (permissive "may" and "can" are too common in ordinary prose), so CAN clauses are added by hand.
* A register built with `--init` contains extracted statement text. Like the extract it came from, keep it outside version control: the command refuses an output path inside a repository unless git ignores it.

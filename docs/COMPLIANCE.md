# Compliance tiers and derogations

Design practices and standards do not all bind equally. The toolkit tracks a project's position against each requirement by **tier**, and treats a departure from a binding requirement as a formal, approved **derogation**.

| Tier | Source wording | Position allowed | What a departure needs |
|---|---|---|---|
| **MUST** | "shall", "must", "is required to", and every "shall not" | complied, derogated, not-applicable (with a reason), open | a **derogation**: justification, risk assessment reference, at least one compensating measure, an expiry or review date, approval at technical-authority level |
| **SHOULD** | "should", "is recommended" | complied, derogated, not-applicable, open | **comply or explain**: a written justification and discipline-lead approval; an expiry is optional |
| **CAN** | "may", "can", "is permitted" | adopted, not-adopted, not-applicable, open | nothing: the clause is optional, so it cannot be derogated; record whether it was adopted |

A clause marked `"statutory": true` (a law or licence condition, not a company or industry practice) **cannot be derogated internally**. The only route is an exemption from the regulator, recorded as `regulator_ref`.

## Use
```bash
# check a register (the shipped example has deliberate faults: an expired derogation, a junior approver, a statutory clause)
python3 -m process_safety compliance process_safety/examples/compliance.json

# start a register from a requirements extract: every clause begins "open", tier set from its modal verb
python3 -m process_safety compliance --init requirements_out/my_requirements.csv --out requirements_out/register.json
```
The register is JSON: `{"as_of": "YYYY-MM-DD", "clauses": [{"id", "tier", "status", "text", "derogation": {...}, "statutory", "regulator_ref", "na_reason"}]}`. `--as-of` overrides the date used for expiry checks.

The output gives counts by tier and status, MUST compliance (complied plus validly derogated, over applicable clauses), the share of SHOULD clauses complied with, the derogations in force, a list of issues, and `ready_for_gate`. That flag is false while any MUST clause is open or has an incomplete, expired or improperly approved derogation. Open or departed SHOULD clauses are reported but do not block it.

Issue codes: `open`, `no-justification`, `no-risk-assessment`, `no-compensating-measures`, `no-expiry`, `not-approved`, `approver-too-junior`, `unknown-approver-level`, `expired`, `bad-date`, `na-no-reason`, `statutory-no-exemption`.

## Limits
* **The approver ladder is a default** (`discipline-lead` < `project-manager` < `technical-authority`; MUST needs the top, SHOULD the bottom). It is not any company's rule: edit `APPROVER_LEVELS` and `REQUIRED_APPROVER` in `process_safety/compliance.py` to match your own procedure.
* **It checks completeness and consistency, not adequacy.** It cannot judge whether a justification is technically sound or the compensating measures are enough. A passing register is not an approval.
* **The requirements extractor does not detect CAN.** It finds "shall", "should" and prohibitions only (permissive "may" and "can" are too common in ordinary prose), so CAN clauses are added by hand.
* A register built with `--init` contains extracted statement text. Like the extract it came from, keep it outside version control: the command refuses an output path inside a repository unless git ignores it.

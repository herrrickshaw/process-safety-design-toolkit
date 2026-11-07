# Cost of implementing safety study recommendations

`process_safety/recommendation_cost.py` (tool `recs`) estimates what it costs to carry out the recommendations that come out of HAZOP, LOPA, QRA, PSSR and hazardous-area reviews: **piping changes, civil work, electrical changes, instrumentation and other construction modifications**. It gives a range rather than a point, splits online work from work that needs a shutdown, merges the shutdown work into the turnaround schedule and cost risk model, and tests each recommendation against the ALARP cost-benefit rule.

Run: `python -m process_safety tool example recs`, then `python -m process_safety tool recs recs.json --out out/`.

## What goes in (every number is yours)
| Input | Meaning |
|---|---|
| `rate_book` | unit rates you supply (for example installed piping per metre, concrete per m3, cable per metre, Ex junction boxes each); the toolkit ships none |
| `recommendations[].lines[]` | discipline (`piping`, `civil`, `electrical`, `instrumentation`, `mechanical`, `other`), quantity (a number or min/mode/max), and a `rate_key` or an inline rate |
| `indirects` | percentages of direct cost: engineering, procurement, construction management, owner's cost, commissioning, escalation. None is defaulted |
| `rate_factor` | one shared multiplier on all rates (market conditions); without it lines are independent and the spread is too narrow |
| `requires_shutdown`, `work_duration_days` | work that can only be done with the unit down, and how long it takes |
| `pll_before`, `pll_after`, `opex_pct_of_capex`, `life_years` | risk reduction (potential loss of life per year) and running cost, for the cost-benefit test |
| `alarp` | VPF, disproportion factor, lifetime, discount rate (policy inputs, no defaults for VPF) |
| `shutdown_model`, `insert_after`, `insert_before` | optional: a `shutdown_risk` model into which the shutdown-dependent items are inserted as activities |

## Outputs
Per recommendation: direct cost by discipline at the mode, total with indirects, capex P10/P50/P80/P90, contingency as P80 minus the all-modes base, and the ALARP cost-benefit (benefit, cost, ratio, ICAF, decision). Portfolio: total, P-values, shutdown versus online split, discipline split, ranking by cost per fatality averted. With a shutdown model: the change in schedule, direct cost, lost operating days, opportunity cost and total cost.

## Worked example (illustrative inputs; six hypothetical recommendations; 5000 runs)
| ID | Recommendation | Source | Work | Base (mode) | P50 | P80 | Cost/benefit | Decision on CBA alone |
|---|---|---|---|---|---|---|---|---|
| R1 | Independent high-level shutdown on feed drum (SIF) | LOPA scenario 4, overfill | online | 40 | 48 | 55 | 0.75 | IMPLEMENT |
| R2 | Replace undersized relief header section and add tie-in | HAZOP node 3, action 7 | shutdown | 161 | 180 | 204 | 3.53 | NOT REASONABLY PRACTICABLE |
| R3 | Remote-operated isolation valves on inventory line | QRA mitigation M2 | shutdown | 106 | 125 | 139 | 2.53 | IMPLEMENT |
| R4 | Blast-resistant wall for control-room side | QRA occupied-building study | online | 102 | 114 | 129 | 0.76 | IMPLEMENT |
| R5 | Replace non-Ex junction boxes in reclassified zone | hazardous area review | shutdown | 63 | 72 | 83 | 3.75 | NOT REASONABLY PRACTICABLE |
| R6 | UPS for ESD valve actuators and F&G | PSSR finding | online | 66 | 72 | 81 | 4.86 | NOT REASONABLY PRACTICABLE |

* Portfolio: base 538, P50 616, P80 656; contingency (P80 minus base) 119 (22% of base). Of the base, 329 is shutdown work and 208 can be done online. Direct cost by discipline: piping 153, civil 47, electrical 132, instrumentation 17, mechanical 43.
* Merged into the example shutdown model (inserted after inspection, before box-up): P50 duration moves by +0.06 days and P80 by +0.10 days, because the modifications run in parallel with the longer repair and bundle work and sit inside its float; direct cost rises by about 381 at P50. Change the insertion point to a critical activity and the same work extends the shutdown (a test shows a 6-day plan becoming 7), which then brings the lost operating days and opportunity cost into the picture.
* The decision column is the cost-benefit test alone at a disproportion factor of 3 with made-up risk numbers. It is not a recommendation about any real measure.

## How to read it
* Contingency here is the gap between the P-value and the all-modes base, driven by your ranges, not a flat percentage.
* ALARP: a measure is expected unless its cost is grossly disproportionate to its benefit. CBA is one input: legal requirements, relevant good practice and measures that remove an intolerable risk are expected regardless.
* Add management of change, engineering review and the pre-startup safety review as lines or schedule activities; the tool reminds you.
* Online work still needs permits and safe isolation. Put hot-work and SIMOPS delays in the shutdown risk register.

## Limits
No resource-loaded schedule, productivity or congestion factors, no hazardous-area permit delays, no soil or access data for civil work, no tax or financing. Quantities are takeoffs you must make; rates come from your contractors or estimating database. The Monte Carlo is checked by closed-form tests (mean of a product of independent three-point variables, indirects arithmetic, the existing ALARP function, the effect of a shared rate factor, and the merge into the shutdown model) in `tests/test_recommendation_cost.py`.

See also `docs/SHUTDOWN_RISK.md`, `docs/QRA.md` (mitigation cost-benefit) and `docs/DESIGN_AWARENESS.md`.

# Shutdown schedule and cost risk (turnaround QSRA / QCRA)

`process_safety/shutdown_risk.py` runs a Monte Carlo analysis of a shutdown (turnaround) plan: a network of activities with
three-point durations and costs, discrete risk events, an optional common-cause factor, and the **opportunity cost of the operating days the
plant is not producing**. It answers the questions a shutdown steering committee asks: how long is it likely to take, what will it cost,
how much contingency is defensible, which activities and risks drive the answer, and what each day is worth.

Naming: the toolkit's `qra` package is the *safety* quantitative risk assessment (consequence, frequency, individual and societal risk).
This module is the *project* risk analysis (schedule and cost) and is called `shutdown_risk` to keep the two apart.

Run it: `python -m process_safety tool example shutdown` copies a worked input; `python -m process_safety tool shutdown shutdown.json --out out/`.

## What goes in (every number is yours)
| Input | Meaning |
|---|---|
| `activities[]` | `id`, `name`, `predecessors` (finish-to-start), `duration_days` {min, mode, max}, optional `cost_fixed` {min, mode, max}, `cost_per_day`, `safety_critical` |
| `risks[]` | `probability`, `affects` (activities delayed), `delay_days` and `extra_cost` ranges |
| `common_factor` | one sampled multiplier on all durations (weather, labour productivity): the simplest positive correlation |
| `duration_cost_per_day`, `overrun_cost_per_day`, `target_days`, `budget` | standby/hire cost for every shutdown day; extra cost per day beyond the target; targets for the probability of success |
| `opportunity` | `margin_per_day` (contribution margin per operating day), `ramp_down_days`, `ramp_up_days` (equivalent full-rate days lost), `recoverable_fraction` (production that can be made up later), `operating_days_per_year` |
| `total_budget` | optional budget for direct plus opportunity cost |
| `distribution` | `triangular` (default) or `pert` |

The toolkit ships **no rates, margins or benchmarks**. The example file is labelled illustrative; replace every figure with your own estimates, quotes and turnaround history.

## What comes out
Base case (all modes, no risks); mean and P10/P50/P80/P90 of duration, direct cost, lost operating days, opportunity cost and total cost;
contingency as P80 minus base; probability of meeting the target duration, the budget and both; on-stream factor for the year; the **value of one day**
(opportunity plus standby cost, and the extra beyond the target); S-curve (CSV and SVG); criticality index per activity; rank-correlation tornado for duration and for cost;
and convergence checks (the tool runs a small sample first, plans the number of runs, then runs the full set).

## Worked example (illustrative inputs, 12 activities, 5 risks, seeds fixed)
Run on 2026-11-06 with the shipped `examples/shutdown.json`; 5753 runs.

| Quantity | Base (all modes, no risk) | P50 | P80 | P90 |
|---|---|---|---|---|
| Shutdown duration, days | 25.0 | 31.5 | 35.6 | 37.7 |
| Direct cost | 384 | 527 | 640 | 700 |
| Lost operating days (incl. ramps) | | 33.4 | 37.4 | 39.5 |
| Opportunity cost | | 2,702 | 3,031 | 3,202 |
| Total cost (direct + opportunity) | 2,531 | 3,228 | 3,668 | 3,899 |

* The 28-day target is met in 20% of runs although the base case says 25 days: the all-modes plan hides the skew from long tails and risk events.
* Opportunity cost is 84% of the median total cost. A day is worth 87 before the target and 101 beyond it (cost units per day), so an acceleration that costs less than that per day saved is worth considering, except on safety-critical work.
* On-stream factor for the year: 92.4% planned, 90.5% at P50, 89.3% at P80.
* Contingency (total cost, P80 minus base): 1,137; duration P80 minus base: 10.6 days.
* Duration drivers (Spearman): activity A6 +0.80, risk R1 +0.59, activity A3 +0.38, activity A4 +0.36. Cost drivers: activity A6 +0.81, risk R1 +0.62, activity A3 +0.37, activity A4 +0.35.
* Most critical activities: A1 100%, A10 100%, A11 100%, A12 100%, A3 100%, A4 94%.
* The notes the tool prints include the safety-critical warning (isolation and the pre-startup safety review sit on the critical path in every run).

## The process-safety lens
* Mark isolation, gas-free certification, SIS proof tests and the pre-startup safety review `safety_critical`. The tool reports how often they are critical and warns that schedule pressure lands on them. Contingency must not be bought by shortening them (see `docs/DESIGN_AWARENESS.md`, steps 5, 8 and 12).
* Put SIMOPS clashes, permit delays and hot-work restrictions in the risk register (the example does), and link the risk to the activities it delays.
* A shutdown is when inspection findings (damage mechanisms) appear: the example's largest risk is extra repair scope found on opening.

## Limits
Calendar days only; no resource limits, calendars or lags; independence between activities unless a `common_factor` is given (the tool says so); risk events are independent; no unknown-unknowns allowance;
margin is a single number per day. The percentiles are as good as the ranges and probabilities supplied, which usually come from expert judgement: record who gave them and why.
The Monte Carlo itself is checked by closed-form tests (series means, the product of CDFs for parallel paths, risk-event expectations, opportunity-cost expectations) in `tests/test_shutdown_risk.py`.

## Further reading (found via a pasted summary; pages not read)
[IQRM on QCRA](https://iqrm.net/blog/qcra-explained-quantitative-cost-risk-analysis-2026), [SOMA Project Controls](https://www.somaprojectcontrols.com/resources/guides/monte-carlo-is-not-magic/). See `docs/LITERATURE.md`.

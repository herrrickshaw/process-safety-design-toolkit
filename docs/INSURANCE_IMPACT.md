# Insurance impact of safety studies and derogations: an actuarial view

Safety studies change what an insurer is asked to cover in four ways. The `insurance` command puts numbers on three of them from your own inputs.

| Effect of the studies | Actuarial meaning | In the model |
|---|---|---|
| Recommendations implemented | lower scenario frequency or loss, so lower expected loss | change `freq_per_yr`, `pd_loss`, `bi_days` |
| A derogation of a safeguard | higher frequency (the barrier's PFD rises) or larger loss (for example less separation) | `pfd` and `loss_factor` per case |
| Compensating measures | recover part of the difference | the third case |
| Better-documented risk (a QRA, closed-out HAZOP actions) | narrower uncertainty on the frequencies, so a smaller loading for "we do not know" | `error_factor` per case; not a risk change |

## Method (exposure rating)
A project has no claims history, so the price rests on scenarios, not experience. The module uses a compound Poisson model for events that reach the insurer's layer:
* Scenario loss `L` = physical damage + business interruption days x value per day.
* Layer loss = `min(max(L - deductible, 0), limit)`; layer expected loss `EL` = sum of frequency x layer loss; variance = sum of frequency x layer loss squared.
* Frequencies are best-estimate medians with a lognormal **error factor** `EF = P95/P50`. The mean exceeds the median by `m = exp(sigma^2/2)`, `sigma = ln(EF)/1.645`: `EF = 3` adds about 25%, `EF = 5` about 61%, `EF = 10` about 2.7 times. This is why evidence alone, with no physical change, can lower a modelled premium.
* **Technical premium** = (`EL` x `m` + `k` x SD) / (1 - expense ratio): the standard-deviation principle, with `k` the risk-load multiple you choose.
* **Retained loss** (the deductible and anything above the limit, times `m`) is reported separately; it is the owner's own cost and rises with a derogation even if the premium is capped.
* The present value of the premium and retained-loss difference between the derogated and compensated cases, over `years` at `discount_rate`, is set against `measure_cost`.
* `credibility(n, k)` and `blended_premium` give the Buhlmann weight `Z = n/(n+k)` for blending a site's own claims experience with the exposure premium. A new project has `n = 0`, so `Z = 0` and the exposure premium stands alone.

## Use
```bash
python3 -m process_safety insurance process_safety/examples/insurance.json
```
The input is JSON: `programme` (`deductible`, `limit`), `pricing` (`expense_ratio`, `risk_load_k`, `discount_rate`, `years`), `cases` (the first is the baseline), `error_factor` per case, `scenarios` (frequency, `pd_loss`, `bi_days`, `pfd` and `loss_factor` per case), `value_per_day`, `measure_cost`, `pml_return_period`.

## Example (invented inputs, to show the shape of the answer)
Three scenarios, a 10 M deductible, a 500 M limit, a derogated trip whose PFD rises from 0.01 to 0.1, and compensating gas detection that brings it to 0.03:

| Case | Layer expected loss | Technical premium | Change | Retained loss |
|---|---|---|---|---|
| baseline | 0.17 M | 3.13 M | - | 0.04 M |
| derogated | 0.92 M | 6.64 M | +112% | 0.13 M |
| derogated with compensation | 0.33 M | 4.21 M | +34% | 0.06 M |

With a 2.5 M compensating package, the 10-year present value of the saving is about 16.8 M, a net 14.3 M. The numbers are invented: only the method is the point. The large swing comes from a tenfold PFD change on scenarios that dominate the layer, and from the model treating the layer as thinly loaded (premium is mostly the standard-deviation term).

## How the studies link to cover and price beyond the model
These points are general and unverified against any insurer's practice; confirm with your broker.
* Insurers typically ask for hazard study and risk-engineering information on large projects. Open actions, expired derogations and unresolved MUST items are the items a reviewer is likely to raise; `compliance` lists them.
* **Whether a departure from a legal or policy requirement affects cover depends on the policy wording** (conditions, warranties, exclusions). The toolkit cannot read your policy. A statutory breach (see `legal-clauses`) is a legal exposure as well as an insurance one.
* A derogation changes the moral picture as well as the numbers: a documented, approved, time-limited departure with compensating measures reads very differently from an undocumented one.
* Study-driven redesign can delay start-up. Whether delay in start-up cover responds depends on the policy; a delay caused by a design change, as opposed to insured damage, is normally not an insured event.

## Limits
* No rates, loadings, loss data or market view ship with the toolkit; every number is an input. A result is not a quotation, and capacity, grades and negotiation also set price.
* Scenario sets are never complete: omitted scenarios understate the premium. Frequencies from a QRA carry large uncertainty, which `error_factor` only summarises.
* One year, independent events, a single layer; no reinstatement premiums, aggregate deductibles, co-insurance, or correlation between scenarios.

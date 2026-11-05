# Cost estimation: approaches and what the toolkit now covers

Three kinds of cost question come up around a process-safety programme, and the toolkit now has an estimator for each:

| Question | Module / tool | Method | Docs |
|---|---|---|---|
| What would the plant cost (concept stage)? | `lng_cost`, `tool lngcost` | analogs scaled by size, escalation, location and site type, ranged by Monte Carlo | this page |
| What does it cost to implement the study recommendations? | `recommendation_cost`, `tool recs` | quantity x rate lines by discipline, indirects, Monte Carlo, ALARP | `docs/RECOMMENDATION_COSTS.md` |
| What does a shutdown cost in money and lost operating days? | `shutdown_risk`, `tool shutdown` | CPM network Monte Carlo with opportunity cost | `docs/SHUTDOWN_RISK.md` |

They connect: the plant capex gives a sanity check on safety spend (`safety_spend_ratio`), and the plant's throughput and unit margin give the margin per operating day that `shutdown_risk` needs (`daily_margin`).

## Approaches, from rough to detailed (AACE class names as in ORIMIZ's documentation; the AACE practice itself was not read)
1. **Analog / capacity factoring (Class 5, FEL 1).** Scale the cost of similar past projects. Used here for a whole plant. Accuracy is wide (the ORIMIZ defaults use -30% / +50%; AACE quotes wider extremes).
2. **Parametric or equipment-factored (Class 4).** Cost from major equipment and installation factors. Not built in the toolkit; the recommendation estimator is the unit-rate form of the lower classes.
3. **Unit-cost, quantity-based (Class 3 and below).** Takeoffs times rates, as in `recommendation_cost`. Needs a rate book you hold.
Ranging is by Monte Carlo on the inputs rather than a flat percentage.

## Reviewing the reference notebook (`LNG_orimiz_testing.ipynb`)
* The notebook cloned the ORIMIZ repository, found no `main.py` or `simulate.py` (the package is `fel1_lng_cost` with a Streamlit app), and fell through to its own **fallback formula**. The printed numbers are that formula's arithmetic, not the repository's estimate.
* The fallback assumes USD 650 million per MTPA at the US Gulf Coast, a location factor of 1.45 and 25% contingency, giving USD 5,891 million (USD 1,178 million per MTPA) for 5 MTPA in Western Australia. None of the three numbers is sourced in the notebook.
* The ORIMIZ public analog table contradicts the baseline. Published plant-only costs, in each project's own cost-year dollars (not escalated), range as follows.

Australian projects (OIES plant-only splits of integrated projects):

| Project | Cost year | USD million per MTPA | Scope | Grade |
|---|---|---|---|---|
| Gorgon LNG (3 trains) | 2013 | 2,109 | integrated upstream | B |
| Wheatstone LNG (2 trains) | 2014 | 1,989 | integrated upstream | B |
| Ichthys LNG (2 trains) | 2015 | 1,929 | integrated upstream | B |
| Queensland Curtis LNG (2 trains) | 2012 | 1,412 | integrated upstream | B |
| Australia Pacific LNG (2 trains) | 2014 | 1,300 | integrated upstream | B |
| Gladstone LNG (2 trains) | 2013 | 1,295 | integrated upstream | B |

US projects:

| Project | Cost year | Site | USD million per MTPA |
|---|---|---|---|
| Corpus Christi Trains 1-2 | 2015 | greenfield | 1,044 |
| Port Arthur LNG Phase 1 (2 trains) | 2023 | greenfield | 1,000 |
| Louisiana LNG Phase 1 (3 trains) | 2025 | greenfield | 994 |
| Rio Grande LNG Phase 1 (3 trains) | 2023 | greenfield | 847 |
| Sabine Pass Train 5 | 2015 | brownfield | 844 |
| Elba Liquefaction (10 modular units) | 2016 | brownfield | 840 |
| Freeport LNG Trains 1-3 | 2014 | brownfield | 800 |
| Cameron LNG Trains 1-3 | 2014 | brownfield | 733 |
| Cove Point LNG | 2014 | brownfield | 717 |
| Corpus Christi Train 3 | 2018 | brownfield | 667 |
| Golden Pass LNG (3 trains) | 2019 | brownfield | 625 |
| Sabine Pass Trains 1-4 | 2012 | brownfield | 550 |

So even before escalation to 2026, every Australian figure is above the notebook's USD 1,178 million per MTPA, and recent US greenfield figures (2023-25) sit at 850 to 1,000. The USD 650 baseline matches only older US brownfield trains. The 25% contingency is flat, and the levelised cost formula divides by a capital charge of 10% that the notebook also does not source.
* ORIMIZ's own code was **not run** here (the sandbox denied executing third-party code); its README, factor file and data were read as text. Its numbers for this case are therefore not quoted.

## The toolkit's estimator (`lng_cost`)
Steps: escalate each analog to the target year, correct location, bring site type to greenfield and back, scale train size with exponent 0.7 (0.6 to 0.8 in the range), take the median and range by Monte Carlo (analog choice, exponent, target location factor, escalation rate, definition growth 0 to 15%). It lists every analog with all its factors, every exclusion with its reason, and warns if the range is narrower than Class 5 typically is or fewer than five analogs remain.

**Inputs you must supply:** a cost index or an escalation rate, and location factors for the target and for each analog's location code. The toolkit ships neither, because they are the largest judgments (ORIMIZ takes them from its Open Plant Cost Index, which is a separate MIT-licensed package). Site-type factors (brownfield 1.50, partly brownfield 1.15; partial brownfield 1.25 as the ORIMIZ authors' judgment), the 0.7 exponent and the 0 to 15% definition growth ship as editable defaults, each with its stated source.

**Worked example (the placeholders are mine, not data):** a 5 MTPA single train in Western Australia, 2026 dollars, escalation 2/3/5% a year, target location factor 1.45 (range 1.30 to 1.70), placeholder factors for the analogs' locations. 24 analogs kept, 2 excluded for train size.

| | Total, USD million | Per MTPA |
|---|---|---|
| P10 | 8,810 | 1,762 |
| P50 | 11,119 | 2,224 |
| P80 | 13,601 | 2,720 |
| P90 | 15,316 | 3,063 |

The notebook's USD 5,891 million sits below the P10 (percentile 0 of the distribution), at 59% of the central median. That comparison depends on the placeholder factors, so treat it as a demonstration of the method; the analog table above is the data-only evidence.

Linking to the other estimators with the example inputs: a 5 MTPA plant at USD 2.0 per MMBtu margin and 52 MMBtu per tonne earns about 1.49 USD million per operating day (350 operating days a year), which is the `margin_per_day` for the shutdown model; and USD 65 million of safety modifications is 0.6% of the median plant capex.

## Limits
Published figures mix scopes (plant only, plant plus pipeline, integrated upstream splits), bases (FID budgets, outturns, EPC-only) and contingency treatment, and most are announced at FID; final costs are often higher. The OIES-derived factors reflect 2014-18 conditions. Gas richness, CO2 handling, multi-train effects, tanks and marine items are not adjusted individually here (ORIMIZ's tool does, with a register of site items). Use it to screen and to size study contingency, not to decide an investment.

## Attribution
Analog data: ORIMIZ-Consulting/open-fel1-lng-cost, `data/public_analogs.csv` (Haider, S. Z., 2026), MIT licence, copyright 2026 Syed Zia Haider; the licence notice is carried in `data/lng_analogs.json`. Most onshore figures originate in Songhurst, B. (2018), *LNG Plant Cost Reduction 2014-18*, OIES Paper NG137 (not read in full here). The method here is a simplified re-implementation of the approach described in their README and factor file, not a copy of their code.

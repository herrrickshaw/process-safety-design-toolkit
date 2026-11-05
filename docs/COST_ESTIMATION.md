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

## Other reliable sources and tools (searched 2026-11-06; reliability noted)
| Source | What it gives | How reliable / how used |
|---|---|---|
| [Honeywell UniSim Design R460 brochure](https://process.honeywell.com/content/dam/process/en/documents/document-lists/hon-ia-hps-bro-unisim-design-r460-vcma.pdf) and [FAQ](https://hcenews.honeywell.com/rs/093-RAU-212/images/UNISIM_External_FAQ.pdf) | The vendor states UniSim Design has built-in equipment sizing and rating and "seamless integration" with Cost Engineering's **Cleopatra Enterprise** for costing; the FAQ lists Cleopatra Plus for cost estimating and Capex optimisation as a use. | Read in Honeywell's own documents (I confirmed the Cleopatra wording in both). Vendor marketing, an older release, and no public description of the data flow or the cost method, so use it as a pointer to a commercial route, not as a method. A [co-hosted webinar page](https://cleopatraenterprise.com/webinar-learn-how-to-easily-design-and-evaluate-the-cost-of-your-projects) exists; its content was not read. |
| NETL, [Cost estimation methodology (QGESS)](https://netl.doe.gov/projects/files/QGESSCostEstMethodforNETLAssessmentsofPowerPlantPerformance_022621.pdf) and [Capital cost scaling, Rev. 4](https://www.osti.gov/servlets/purl/1573493) | A public government methodology: bare erected cost through total overnight cost, AACE class targeting (NETL studies aim for Class 4, quoted as -15% / +30%), scaling by size, date and location. | Government source, free, the best open reference for an equipment-factored (Class 4) workflow. Power-plant context. Search summaries only; the PDFs were not read. |
| AACE International RP 18R-97 ([library](https://library.aacei.org/pgd01/pgd01.shtml)) | The classification system for process-industry estimates (five classes, accuracy ranges at an 80% interval). | Copyrighted and not read. The ranges quoted here come from the ORIMIZ factor file (Class 5 low -20% to -50%, high +30% to +100%; Class 4 -15% to -30% and +20% to +50%; Class 3 -10% to -20% and +10% to +30%) and NETL; check the practice itself before citing. |
| [BioSTEAM TEA](https://biosteam.readthedocs.io/en/latest/tutorial/Techno-economic_analysis.html), [QSDsan TEA](https://qsdsan.readthedocs.io/en/latest/tutorials/7_TEA.html), OpenPyTEA (TU Delft) | Open-source Python techno-economic analysis: installed cost from a Lang factor or per-unit bare-module factors, cash flows, uncertainty. QSDsan exposes a CEPCI input. | Open and documented. Licences and default factor values were not checked: look in their source before reusing anything. The most direct models for an equipment-factored extension of `recommendation_cost`. |
| [OIES NG137](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2018/10/LNG-Plant-Cost-Reduction-2014%E2%80%9318-NG137.pdf) | Liquefaction plant costs in dollars per tonne per annum, the origin of most ORIMIZ analog figures and factors. | The most useful free LNG benchmark. Only its contents list was seen here; the figures in `lng_analogs.json` are as ORIMIZ transcribed them. |
| [Oil & Gas Journal LNG benchmarking article](https://ogj.com/drilling-production/production-operations/article/17239949/benchmarking-study-compares-lng-plant-costs) | An older trade comparison of LNG plant costs. | Dated, not read; background only. |
| DWSIM Capital Cost Estimator | A third-party add-on for the open-source DWSIM simulator that estimates capital and operating costs from a flowsheet. | Listed on a paid marketplace as a demo and a paid package; I did not verify its method. |
| CEPCI (Chemical Engineering Plant Cost Index) | The usual cost index. | Proprietary: values come from the magazine, so the toolkit cannot ship them. The ORIMIZ authors' Open Plant Cost Index is a free alternative that was not read here. |

Gaps: no free source was found that publishes equipment cost correlations (Turton CAPCOST or Sinnott are tied to textbooks), and no EIA, IEA or GIIGNL LNG capex benchmark turned up in the searches. Say so before relying on any figure from the weaker rows.

What this suggests for the toolkit: simulators such as UniSim and DWSIM already produce equipment lists with sizes, so the natural next step is an **equipment-factored mode** (purchase cost from your own vendor or database figures, installation by Lang or bare-module factors you supply, with the same Monte Carlo ranging and shutdown merge). I have not built it; the NETL methodology and BioSTEAM's factor structure are the references to follow.

## Commercial tools and guides named by the user (added 2026-11-06)
| Name | What it is | Status here |
|---|---|---|
| [GAO Cost Estimating and Assessment Guide, GAO-20-195G](https://www.gao.gov/products/gao-20-195g) | Free US government guide: a 12-step estimating process resting on accuracy, comprehensiveness, credibility and documentation, with cost and schedule risk analysis | gao.gov blocks automated requests; confirmed from search summaries; not read. The best free methodology reference alongside NETL's |
| PMI PMBOK Guide ([pmi.org](https://www.pmi.org/standards/pmbok)) | Commercial project management standard | not read; the site blocks automated requests |
| [Cleopatra Enterprise](https://cleopatraenterprise.com) (Cost Engineering Consultancy) | Cost estimating and project cost management software; linked from UniSim Design per Honeywell's documents | vendor documents only |
| [Nomitech CostOS](https://www.nomitech.com) | Commercial cost estimating software | vendor site only; not evaluated |
| [Oracle Primavera Cloud](https://www.oracle.com/construction-engineering/primavera-cloud/) | Commercial scheduling and controls | not evaluated. A turnaround schedule kept there could feed `shutdown_risk` as activities with durations and predecessors; that import is not built |

Trademarks and copyright, as notified by their owners: PMI(R) and PMBOK(R) (c) Project Management Institute, Inc.; GAO(R) (c) U.S. Government Accountability Office; Cleopatra Enterprise(R) (c) Cost Engineering Consultancy; CostOS(R) (c) Nomitech Ltd.; Oracle(R) and Primavera Cloud (c) Oracle Corporation. All rights reserved by their owners. This toolkit has no affiliation with them, reproduces none of their content, and mentions the names only to say what they are and where they fit.

## Limits
Published figures mix scopes (plant only, plant plus pipeline, integrated upstream splits), bases (FID budgets, outturns, EPC-only) and contingency treatment, and most are announced at FID; final costs are often higher. The OIES-derived factors reflect 2014-18 conditions. Gas richness, CO2 handling, multi-train effects, tanks and marine items are not adjusted individually here (ORIMIZ's tool does, with a register of site items). Use it to screen and to size study contingency, not to decide an investment.

## Attribution
Analog data: ORIMIZ-Consulting/open-fel1-lng-cost, `data/public_analogs.csv` (Haider, S. Z., 2026), MIT licence, copyright 2026 Syed Zia Haider; the licence notice is carried in `data/lng_analogs.json`. Most onshore figures originate in Songhurst, B. (2018), *LNG Plant Cost Reduction 2014-18*, OIES Paper NG137 (not read in full here). The method here is a simplified re-implementation of the approach described in their README and factor file, not a copy of their code.

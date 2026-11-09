# Project pipeline, WBS, scheduling and reporting

Spec and usage for four JSON-driven tools that wrap the study work the toolkit already does (HAZOP and PHA management, shutdown risk, QRA). They are for planning and tracking a consultancy's or an owner's study portfolio. They are **not** a replacement for a scheduling or CRM product, and they hold no rates, durations or win probabilities of their own: every number is an input.

```bash
python3 -m process_safety tool example tenders        # also wbs | schedule | portfolio
python3 -m process_safety tool tenders tenders.json --out out/
python3 -m process_safety tool wbs wbs.json --out out/
python3 -m process_safety tool schedule schedule.json --out out/
python3 -m process_safety tool portfolio portfolio.json --out out/   # one report over all of the above plus PHA actions
```

## What "monitoring" means here
The register (`tender_register.py`) holds tenders and upcoming projects that someone or something has put in it: typed by hand, exported from a portal, or produced by a scheduled agent. The toolkit does **not** scrape tender portals (stdlib only, offline, and portal terms differ). Two functions help the intake: `triage` matches keyword rules against pasted or exported item text and proposes register entries, and `check` rejects malformed entries. What the module then does is date and value arithmetic: which deadlines fall in the next N days, which have been missed, which projects start soon, the weighted pipeline value, bid scores and win rate.

## Modules
| Module | Tool name | Takes | Gives |
|---|---|---|---|
| `wbs.py` | `wbs` | numbered nodes (`1`, `1.1`, `1.1.2`) with leaf estimates; or a generic template (`hazop`, `qra`, `pha_revalidation`) instantiated per node | rolled-up effort, cost and percent complete per node, WBS dictionary CSV, a schedule input built from the leaves |
| `schedule.py` | `schedule` | activities with working-day durations, links FS/SS/FF with lag, a working calendar with holidays, start-no-earlier dates, optional deadline, owners, effort, percent complete and a status date | dates, total float, critical path, deadline slack, planned percent at the status date, weekly load per owner against capacity, Gantt SVG and CSV; `from_shutdown` converts a `shutdown` model so one network drives both the plan and the P50/P80 risk run |
| `tender_register.py` | `tenders` | entries (client, service, stage, dates, value, scores) plus stage probabilities, bid weights and thresholds | deadlines due and missed, upcoming project starts, weighted pipeline by stage and award month, bid scores and recommendation, win rate, triage of raw items |
| `portfolio.py` | `portfolio` | the register, projects (a schedule or a WBS, budget, actual cost, status date), capacity, and the `pha` action and revalidation inputs | one report: headline counts, deadlines, starts, pipeline, earned-value status per project, capacity overloads across projects, tenders won but not yet planned, HAZOP action ageing and revalidation due; JSON, CSV and a self-contained HTML page |

## Refusals
* A cyclic network, an unknown predecessor, a duplicate id or WBS code, a parent code that does not exist, a negative duration, a link type other than FS, SS or FF, a calendar with no working day, a date that is not ISO, dates out of order within a tender, a stage not in the stage list, a probability outside 0 to 1.
* No weighted pipeline without stage probabilities: they are inputs, and the report says "not computed" if they are missing. No bid recommendation without weights and thresholds.
* Earned value needs a budget; the cost index needs an actual cost; neither is guessed.

## Constants and sources
None are typed in. Critical path method, total float, and the earned-value definitions (planned value, earned value, SV = EV - PV, CV = EV - AC, SPI = EV / PV, CPI = EV / AC, EAC = BAC / CPI) are definitions, not recalled data; the EAC form assumes current cost performance continues, and the report says so. The WBS templates are generic activity lists, not the procedure of any standard: IEC 61882 and company procedures were not read. Durations, effort and costs in the templates are left empty on purpose.

## Identities the tests rely on
* WBS: a parent's effort and cost equal the sum of its children; the root total equals the sum of leaves; a parent's percent complete lies between its children's.
* Schedule: with a seven-day calendar, finish-to-start links and no lags, the project duration equals `shutdown_risk` base-case duration for the same network; the critical path's durations sum to the project duration; total float is never negative without a deadline; adding a holiday never brings the finish earlier; a positive lag never brings it earlier; shifting the start by a whole number of weeks shifts every date by the same number of days; weekly load per owner sums to that owner's effort.
* Register: the by-stage pipeline value sums to the total; scaling all bid weights leaves the score unchanged; raising a criterion score never lowers the bid score; win rate equals won over won plus lost.
* Earned value: EV and PV lie between 0 and the budget; EV = PV when reported percent equals planned percent.

## Limits
Calendar days are whole working days on one calendar per schedule; no resource levelling (overload is reported, not resolved); no cost loading of activities beyond the project budget weighting by effort; no multi-project dependencies; weekly capacity is scaled by the working days in the week but personal leave is not modelled. The register is only as current as its last update.

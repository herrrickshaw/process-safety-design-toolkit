# Domain-driven design for the toolkit, and other architecture choices for scale

**Status: a design proposal, not implemented.** Nothing in `process_safety/` has moved. This page says what a domain-driven layout would look like for the code that exists today, what each other scaling option would buy, and which trigger should make you adopt it. The current layout is in `docs/ARCHITECTURE.md`.

**Basis.** The module list and import graph of `process_safety/` on branch `feature/project-pipeline-planning` (read with Python `ast`, not by running the code), `docs/DESIGN_LIFECYCLE_PLAN.md` for the study lifecycle, `docs/FEATURE_GAP_ANALYSIS.md` for the protected-by-licence split, and the toolkit rules in `CONTRIBUTING.md` (standard library only, every number sourced). Architecture pattern names are the common ones (Evans, domain-driven design; Cockburn, hexagonal architecture); no pattern text is quoted. No performance figure is claimed: nothing was benchmarked.

## 1. What the code looks like now

* About 90 modules sit flat in `process_safety/`, one per calculation family, plus `qra/` (a six-step sub-package), `cli/` (command registry) and `tools.py` (JSON-driven study tools).
* Measured from imports: `constants` is imported by 13 modules, `relief` by 8, `ranges` by 6, `qra` by 5. `tools.py` imports 18 modules and is the one place that knows every study. `portfolio` imports `pha`, `schedule`, `tender_register` and `wbs`.
* Calculation modules are pure functions and the CLI does not leak into them. That is already the hard part of a clean architecture.

What strains as the toolkit grows from calculators to a delivery platform (tenders, projects, studies, actions):

| Strain | Evidence in the repo |
|---|---|
| No named boundaries: a commercial tender, a HAZOP action and a jet-fire view factor share one flat namespace | 90 sibling modules, no sub-packages except `qra/` and `cli/` |
| One orchestration module knows everything | `tools.py` imports 18 modules and is the integration point |
| State is loose JSON files with no identity or history | `positions`-style files, `examples/*.json`; no study ID, no revision trail |
| The language drifts: "scenario", "case", "event" and "release" are used in different senses | `scenarios.py`, `scenario_ingest.py`, `qra/`, `release.py` |
| Licensed or protected features (see the gap analysis) have no place to live without entering the open core | `docs/FEATURE_GAP_ANALYSIS.md` ledger |

## 2. Ubiquitous language (terms to fix first)

DDD starts with words. These need one meaning each, written into `docs/GLOSSARY.md` (generated from `glossary.py`, so edit the source):

| Term | Proposed single meaning |
|---|---|
| Scenario | A defined loss of containment or process upset with initiating cause, inventory and conditions (input to consequence and frequency) |
| Case | One simulator or HMB operating state (normal, minimum, maximum, upset); never used for a hazard |
| Study | A dated, owned piece of work that produces findings (HAZID, HAZOP, LOPA, QRA, SIL verification, PSSR) |
| Finding | One result in a study (a deviation with cause and consequence, a risk contributor) |
| Recommendation | A proposed change that closes a finding |
| Action | A tracked task with owner and due date that implements a recommendation |
| Safeguard / barrier | An independent layer that prevents or mitigates; carries a credited PFD or effectiveness and its evidence |
| Source grade | A or B (primary text read) or C (secondary), as used in `standards.py` and the research docs |

## 3. Subdomains and bounded contexts

Core domain = where the value and the risk are. Supporting = needed, not differentiating. Generic = replaceable.

| Context | Kind | Today's modules | Owns |
|---|---|---|---|
| **Consequence physics** | Core | `release`, `jet_flame`, `pool_fire`, `fireball`, `vapour_fire`, `dispersion`, `dense_gas`, `explosion`, `expansion`, `viewfactor`, `structural_fire`, `flare`, `depressuring`, `tank_venting`, `overfill`, `twophase`, `thermal_runaway` | Pure physical models. No study, no project, no standards text. |
| **Risk assessment** | Core | `qra/`, `bowtie`, `sil`, `sil_lifecycle`, `ram`, `reliability`, `egress`, `fg_mapping`, `atex`, `mah` | Frequencies, individual and societal risk, ALARP, SIF verification, barrier credit |
| **Process hazard analysis** | Core | `hazop`, `pha`, `pid_review`, `recommendation_catalog` | HAZOP and revalidation records, deviations, recommendations, action tracking |
| **Plant and design basis** | Supporting | `plant_model`, `plant_units`, `hmb`, `scenario_ingest`, `fluiddata`, `props`, `hydraulics`, `separator`, `relief`, `relief_piping`, `vessel_mech`, `design_workflow` | The plant as streams, units, lines and relief devices; ingest of PFS, HMB, P&ID |
| **Compliance and standards** | Supporting | `standards`, `legal_clauses`, `compliance`, `psm`, `rmp`, `incidents`, `literature`, `requirements_extract` | Clause register with source grade, regime screening, incident evidence |
| **Project delivery** | Supporting | `wbs`, `schedule`, `shutdown_risk`, `portfolio` | Work breakdown, critical path, earned value, shutdown schedule and cost risk |
| **Commercial pipeline** | Supporting | `tender_register` | Tenders, deadlines, bid score, win rate |
| **Cost estimation** | Supporting | `recommendation_cost`, `lng_cost`, `insurance_impact` | Capex and opex ranges, ALARP cost-benefit |
| **Shared kernel** | Generic | `units`, `constants`, `ranges`, `glossary`, `templating` | Quantities with units, physical constants, input ranges. Changed only by agreement of every context. |
| **Interfaces** | Generic | `cli/`, `tools.py` runner, SVG and HTML writers | Parsing, rendering, files |

### Context map (how the contexts relate)

```
  Standards (Conformist)               Plant & design basis  --(Customer/Supplier)-->  Consequence physics
      |  grade + clause                     |  streams, inventories                          |  effect distances
      v                                     v                                                v
  Process hazard analysis  <--(Published language: Finding, Recommendation)-->  Risk assessment
      |  actions, revalidation dates                                                         |  risk, ALARP
      v                                                                                      v
  Project delivery  <-----------------------  Cost estimation  <-------------------------- (recommendation cost)
      ^
      |  tender won -> project created   (Domain event, not a shared table)
  Commercial pipeline

  Shared kernel: units, constants, ranges        Anti-corruption layers: Proteus XML, simulator streams, Excel
```

Relationship choices and why:

* **Standards is Conformist.** The toolkit cannot change a standard, so it takes the standard's model and records the grade; it never invents a value (`CONTRIBUTING.md` rule).
* **Plant ingest is an anti-corruption layer.** Proteus XML, simulator exports and client spreadsheets are translated once at the edge into `Stream`, `Unit` and `Line` objects. No other context sees a vendor field name.
* **Findings and recommendations are a published language.** HAZOP, QRA and LOPA each raise recommendations in the same small schema, so project delivery and cost estimation consume one shape.
* **Commercial pipeline to project delivery goes by event.** `TenderWon` creates a project skeleton; the two contexts do not share a table or import each other.

## 4. Inside a context: building blocks

| Block | Meaning here | Example |
|---|---|---|
| Value object | Immutable, equal by value, validates itself | `Quantity(value, unit)`, `Pressure`, `Frequency`, `SourceRef(title, edition, clause, grade)`, `DateWindow` |
| Entity | Has identity over time | `Action`, `Recommendation`, `Tender`, `Task` |
| Aggregate root | One consistency boundary; outside code goes through it | `HazopStudy` (nodes, deviations, actions), `Project` (WBS tree and schedule), `TenderRegister`, `SifLoop` (components, proof-test interval, PFD) |
| Domain service | Logic that belongs to no entity | `CriticalPathPlanner`, `RiskIntegrator`, `AlarpAssessor` |
| Repository | Port for load and save of an aggregate | `StudyRepository`, `TenderRepository` |
| Domain event | Something that happened that another context cares about | `RecommendationRaised`, `ActionClosed`, `RevalidationDue`, `ScenarioChanged`, `TenderWon`, `DeadlineMissed` |

Invariants to enforce in the aggregate, not in the CLI (each already exists as a check somewhere; DDD gives it one home):

* An `Action` has an owner and a due date, and a closed action has closure evidence.
* A safeguard credited in a study carries a PFD, its source and its independence statement; a credit with no source is rejected.
* A `SourceRef` of grade A or B must name the clause actually read; promoting a grade requires the primary text (existing rule in `CLAUDE.md`).
* A WBS node's roll-up equals the sum of its leaves; a schedule has no dependency cycle (both are checked today in `wbs.check` and `schedule.check`).
* A study has exactly one status at a time (draft, issued, revalidation due), so revalidation dates come from one place instead of three.

## 5. Layering that fits "standard library only"

DDD usually arrives with a framework. Here it cannot, so the layers are plain packages and `typing.Protocol` ports.

```
process_safety/
  kernel/            units, constants, ranges, glossary          (imported by all; imports nothing)
  physics/           consequence models, pure                    (imports kernel only)
  risk/              qra, bowtie, sil, ram                       (imports kernel, physics)
  hazard_analysis/   hazop, pha, recommendations                 (imports kernel, risk via Finding schema)
  plant/             streams, units, ingest ACL                  (imports kernel)
  compliance/        standards, clauses, regimes                 (imports kernel)
  delivery/          wbs, schedule, portfolio, shutdown          (imports kernel; reads others via ports)
  pipeline/          tenders                                     (imports kernel)
  costing/           recommendation and LNG cost                 (imports kernel)
  app/               use cases = today's `tools.py` branches, one function each
  adapters/          cli, json_files, sqlite, proteus_xml, svg_html, excel
```

Dependency rule: domain packages never import `app/` or `adapters/`; `app/` wires use cases to adapters. A stdlib test (an `ast` walk like the one used to write this page) fails the build when a forbidden import appears, so the rule is checked, not hoped for. That test belongs in `tests/test_architecture.py`.

The command registry in `cli/registry.py` already is a primary adapter. The change is that `tools.py` stops being a 18-import switch and becomes `app/` use cases that each import one or two contexts.

## 6. Migration without a rewrite (strangler)

The golden-output file (`tests/golden/cli_golden.json`) and the scenario tests are the safety net: any step that changes a number fails the build, so each step can be small.

| Step | Change | Size (ideal days) | Gate |
|---|---|---|---|
| M0 | Add `tests/test_architecture.py` that records today's import graph as the baseline and fails on new cross-context imports | 1 | passes on current code |
| M1 | Write the language table above into `glossary.py`; no code moves | 1 | glossary doc regenerated |
| M2 | Introduce `Quantity` and `SourceRef` in `kernel/`; use first in the new project-planning code only | 2 | identity tests, no golden change |
| M3 | Move planning modules (`wbs`, `schedule`, `tender_register`, `portfolio`) into `delivery/` and `pipeline/` with import shims at the old paths | 2 | golden unchanged |
| M4 | Define `Finding` and `Recommendation` schemas; make `pha`, `bowtie`, `sil_lifecycle` emit them | 4 | new schema tests |
| M5 | Replace `tools.py` branches by `app/` use cases, one per tool | 3 | `tool <name>` output byte-identical |
| M6 | `StudyRepository` port with JSON adapter, then SQLite adapter | 3 | round-trip tests |

About 16 ideal days in total, which is an estimate, not a measurement. The sprint plan's calibration rule applies (`docs/SPRINT_PLAN.md`). Rejected: a big-bang move of all 90 modules (breaks every import and every reader's habit for no new capability), and renaming CLI commands (breaks scripts and the golden file).

## 7. Other architecture choices for scale

"Scale" means four different things here. Pick by the one that hurts.

| Scale axis | What grows | First symptom to watch |
|---|---|---|
| Compute | Monte Carlo runs in `qra`, `ram`, `shutdown_risk`, field grids in `fg_mapping` | A study takes minutes and blocks an interactive session |
| Data | Studies, scenarios and tenders per client and per year | JSON files too many to search, no history |
| Team | More contributors and more standards | Merge conflicts in `tools.py` and `standards.py`; import tangles |
| Use | Several engineers using it at once, a web front end | Two people edit one register and overwrite each other |

| Option | What it is | Helps which axis | Cost and risk | Fit with the stdlib-only rule | Verdict |
|---|---|---|---|---|---|
| **A. Modular monolith** (sections 3 to 6) | One deployable, enforced internal boundaries | Team | Low; discipline needed | Full | **Do now.** It is the precondition for every other row. |
| **B. Hexagonal (ports and adapters)** | Domain at the centre, I/O at the edge | Team, Use | Low; some indirection | Full (`Protocol`) | **Do with A.** Already half there with the CLI registry. |
| **C. Pipes and filters / dataflow** | Each study is a pipeline of pure steps (ingest, balance, scenarios, consequence, risk, report) with typed hand-offs | Compute, Team | Low to medium; needs stable step schemas | Full | **Adopt for the design workflow.** `design_workflow` is already a chain; make the steps first-class so they can be cached and re-run from a failed step. |
| **D. Plugin architecture** | Core discovers extra modules by entry point or directory | Team, Licence | Medium; versioned plugin API to maintain | Full (`importlib`) | **Adopt for protected features.** Licensed or client-specific content lives in a private package that registers commands; the open core never contains it. Matches the "protected by licence" class in the gap analysis. |
| **E. Event log (append-only study history)** | Store changes to a study as events; state is a replay | Data, Use | Medium; schema evolution of old events | Full (JSON lines or `sqlite3`) | **Adopt for actions and findings only.** A safety record wants who-changed-what and when. Not for the physics, which has no history to keep. Rejected: full event sourcing of everything. |
| **F. CQRS read models** | Separate write model from read-optimised views | Data, Use | Medium; two models to keep consistent | Full | **Adopt for the portfolio report** only: it already reads from several contexts and is rebuilt on demand. Do not split the write side of the calculators. |
| **G. Parallel compute with `multiprocessing`** | Run Monte Carlo batches across cores | Compute | Low; seeds must be handled so results stay reproducible | Full (`concurrent.futures`) | **Do first for compute.** Identity checks already exist (`ram` has an analytic check), so a parallel run can be proved equal to the serial one in distribution. |
| **H. Work queue and workers** | Studies submitted as jobs, run by worker processes | Compute, Use | Medium to high; a broker or database queue | Partial: stdlib `sqlite3` as a queue works for one host; a real broker is an outside dependency | **Defer.** Adopt when two or more people run long studies at once. Start with an `sqlite3` job table behind the repository port. |
| **I. Storage ladder** | JSON files, then `sqlite3`, then Postgres | Data, Use | Low per step behind the repository port | Files and `sqlite3` are stdlib; Postgres needs a driver (outside the core) | **Climb on triggers:** SQLite when searching or concurrent edits matter; Postgres when more than one host or a web service appears. The repo already has a DuckDB and Postgres pattern in the parent project; not needed here yet. |
| **J. Service-based or microservices** | Each context a separate service | Team, Use | High; network, versioning, deploy, observability | Breaks the single-tool promise | **Reject for now.** The contexts share one shared kernel and are developed by one small team; a network boundary adds failure modes the calculators do not have. Revisit only if one context (for example costing with a licensed price book) needs separate access control or release rhythm. |
| **K. Workflow engine** | A durable engine for long human-in-the-loop processes | Use | High; external service | No | **Reject for now.** The review and sign-off steps are human and slow; tracked actions and dates (E) cover the need. |
| **L. Serverless functions** | Each calculation behind an HTTP function | Use | Medium; cold start and packaging per function | Packaging, not language, is the problem | **Reject for the core.** Calculators are fast and local; a thin web adapter over `app/` (B) gives the same reach without splitting the code. |

## 8. Recommended path and triggers

1. **Now (sprint-sized):** M0 to M3, option A and B. It costs about 6 ideal days and changes no output.
2. **Next:** M4 and M5, plus option C for the design workflow and option G for Monte Carlo. This is where DDD starts to pay: one `Finding` shape and one use-case layer.
3. **On a trigger, not before:**

| Trigger | Move |
|---|---|
| First licensed or client-specific module is needed | Option D (plugins) |
| Two people need to edit one register, or you need history for audit | Option E plus SQLite (I) |
| A web front end is requested | A thin HTTP adapter over `app/`, and option F for the portfolio view |
| Long studies block interactive use | Option H with an `sqlite3` job table |
| One context needs separate access control or release cycle | Re-examine option J for that context only |

## 9. Risks and limits of this proposal

* The context boundaries above are a first cut from module names and imports. Two will be argued: whether `relief` belongs to plant design or to consequence physics, and whether `incidents` belongs to compliance or to hazard analysis. Settle them in the first review, not in code.
* DDD adds indirection. For a calculator library it is justified only where the model has state and rules (studies, actions, projects, tenders). Keep `physics/` as plain functions; do not wrap every formula in an object.
* Effort figures are estimates and are not measured against this repository's history, which spans one week.
* This page recommends; the owner decides. Nothing here changes safety results, and the limits statement in the CLI outputs stays as it is.

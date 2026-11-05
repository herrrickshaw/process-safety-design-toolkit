# Changelog (decisions, including rejected alternatives)

## 0.11.0 - 2026-11-06: use cases, two-phase relief, solid-flame view factor
* New: `docs/USE_CASES.md` (eight scenarios across refinery, LPG, terminals, functional safety, regulation, electrical, data centre and occupational safety, generated from `scripts/use_case_cmds.py` by `scripts/gen_use_cases.py`; the test suite runs every command and checks the doc is current).
* New: `twophase` (omega method) and CLI `twophase`. The choked flux is found by maximising the energy-balance flux over pressure ratio, not from a recalled chart; tests check the result against the published critical-ratio equation (five omegas) and two exact limits (omega near 0 is incompressible flow, omega = 1 is isothermal choking at exp(-1/2)).
* New: `viewfactor` and CLI `flame-flux`: midpoint integration of the view factor to flat rectangular flame faces; tests match the Howell rectangle result to 2e-4 and the far-field inverse-square limit.
* Coverage map: two entries added; the README "not implemented" list now says two-phase relief sizing is covered and runaway-reaction (DIERS) relief is not. Two ranges (`omega_parameter`, `emissive_power_kW_m2`) and five glossary terms added; `docs/RANGES.md` and `docs/GLOSSARY.md` regenerated.
* Found while writing the use cases: the point-source `pool-fire` distances and the SEP-based solid-flame fluxes disagree by about four times in the far field (25% radiant fraction against about 6% implied by the Mudan-Croce SEP). Documented in the use case, not papered over; no model was changed.
* Docs: `docs/DESIGN_AWARENESS.md` (review steps, design choices, incident instances) and section 5 there on external material read 2026-11-06: the PHMSA LNG proposed rule (proposed, not final, so `lng` still follows the current 49 CFR 193 text), a Sigma-HSE early-design article, and the CCPS Beacon page which was blocked and not read.
* Docs: `docs/REGULATORY_LANDSCAPE.md` (country, governing body and company views; gaps for Gulf, Canada, Japan and Indian operators left empty rather than guessed).
* Used existing toolkits as oracles and data sources (CoolProp, fluids; dev-time only, the package stays dependency-free): 62 new cross-checks (186 in all, all within tolerance) covering `twophase` against a direct CoolProp isentropic HEM integration, Lee-Kesler/Rackett for seven hydrocarbons, real-gas choked release, `fluids` separator, drag, friction, valve-unit and tank-geometry functions. `scripts/gen_validation.py` now regenerates `docs/VALIDATION.md`.
* New data: `data/fluid_screening.json` (18 fluids x 14 pressures, CoolProp 8.0.0), `fluiddata` module, `twophase --fluid`, `fluid-data` command. Findings: the two-point omega reproduces the HEM flux within 2.2% on all 252 rows, the single-point saturated omega degrades near the critical point (CLI now warns above half Pc), and the ideal-gas isentrope used for MDMT screening is 5-9% colder than the real-gas one (conservative; documented). Use case `flashing-lpg` now uses real fluid data instead of illustrative omegas.
* Docs: SPE/JPT (ADNOC 15-element PSM framework and its 50-event root-cause review; BP Oregon, Ohio 2022 OSHA findings), AFPM and the EPA RMP revision proposal of Feb 2026 added to `DESIGN_AWARENESS.md` and `REGULATORY_LANDSCAPE.md`; PSM News read but not used.
* Literature: `literature.py`, `data/literature.json` (49 sources, each with kind, region, access, topics, toolkit modules, whether content was read, and an HTTP status check), CLI `literature`, generated `docs/LITERATURE.md`, `scripts/build_literature.py` and `scripts/check_literature_urls.py`. Findings from the URL check: journals, CCPS, the Energy Institute, ILO and OECD pages block automated clients (HTTP 403), PESO and NOPSEMA timed out, and the direct HSE R2P2 URL is dead (replaced by the HSE risk pages). Listed, not read; nothing is claimed about their content.
* Data: `data/incidents.json` and `docs/INCIDENTS.md`: 17 CSB investigations (2003-2024) read from csb.gov, with date, place, report date, deaths and injuries only where the page text stated them, an example recommendation, and the toolkit's mapping to modules and design review steps. `incidents.py`, CLI `incidents`, `scripts/build_incidents.py`. The CSB site is a dynamic page; detail URLs came from its sitemap. Two page inconsistencies are noted in the data (PEMEX release year, ITC status).
* New: `shutdown_risk` (QSRA + QCRA by Monte Carlo on a CPM network) and `tool shutdown`, with the opportunity cost of lost operating days (margin per day, ramp-down/up in equivalent days, recoverable fraction, on-stream factor, value of one day), safety-critical activity flags, S-curve SVG/CSV, criticality and rank-correlation tornado, sample-first run planning. 16 tests including closed-form checks (series means, product of CDFs for parallel paths, risk-event and opportunity-cost expectations). The shipped example is illustrative and labelled so; no rates or margins are defaulted. Named `shutdown_risk` because `qra` here means safety risk assessment.
* New: `recommendation_cost` and `tool recs`: cost estimate for implementing safety study recommendations by discipline (piping, civil, electrical, instrumentation, mechanical), with quantity and rate uncertainty, user-supplied indirects and a shared rate factor, Monte Carlo contingency (P-value minus base), shutdown-dependent items merged into the `shutdown_risk` model (schedule, direct cost, lost operating days and opportunity cost effect) and ALARP cost-benefit via the existing `qra.alarp`. No unit rates are shipped; the example is illustrative. 10 tests including a check that a modification on the critical path extends a 6-day plan to 7.
* New: `lng_cost` and `tool lngcost`: conceptual LNG liquefaction capex by the analog method (26 public analogs from the MIT-licensed ORIMIZ table, attribution in `data/lng_analogs.json`), with size/escalation/location/site-type adjustment, exclusion reasons, Monte Carlo range and Class 5 sanity warnings; `daily_margin` (feeds the shutdown opportunity cost) and `safety_spend_ratio`. Cost index and location factors are required inputs, not shipped. `docs/COST_ESTIMATION.md` reviews the reference notebook: it fell through to an unsourced fallback formula (USD 650M per MTPA, factor 1.45, 25% flat) that sits below every published Australian plant-only analog. ORIMIZ's own code was not executed (the sandbox refused third-party code); its README, factors and data were read as text.
* Rejected: depending on CoolProp at runtime (it would end the stdlib-only promise; the table ships as JSON); using `iapws` (GPL v3) anywhere in the source tree; widening the MDMT tolerance silently (it is labelled a known difference).
* Rejected: coding the TNO multi-energy blast curves and OISD layout distances (the curves and the standard were not read, so the numbers would be recalled); a default omega or Kd (both depend on the fluid and the valve); defaulting Kd to 0.85 for two-phase service.

## 0.10.0 - 2026-11-05: streamlined CLI, input ranges, glossary, CI/CD, validation
* New: `ranges.py` (55 quantities with hard and soft ranges), `glossary.py` (about 115 terms), CLI commands `ranges` and `glossary`, `--no-range-check`, generated `docs/RANGES.md` and `docs/GLOSSARY.md`, `@validated` on `relief.gas_area`, `sil.pfd_avg`, `sil.lopa`, `electrical.idmt_time_s` and `fireball.fireball`.
* Refactor (no change to any output): the 437-line `__main__.py` with a 34-branch `if/elif` is now a command registry (`cli/`), one class per command, with range checks applied by the framework. `constants.py` replaces `R`, `G` and atmospheric pressure defined in 9 modules. A golden test pins 40 CLI outputs from before the refactor; all match.
* Fixed (found by the lint step): `fg_mapping.py` reused a quote character inside an f-string, a syntax error on Python 3.10 and 3.11 although the package declares `>=3.10`; `psm.py` annotated with `datetime` without importing it. Removed the unused imports.
* CI/CD: GitHub Actions matrix on Python 3.10 to 3.13, lint (real errors only), optional cross-check job, tag-driven release workflow that checks tag against `pyproject.toml`, Dependabot for actions.
* Validation: `tests/crosscheck/validate.py` runs 124 checks against fluids, thermo, CoolProp and closed-form literature formulas; all within tolerance. `docs/VALIDATION.md` lists them and the known differences (liquid relief area consistently 4.7% below `fluids`, cause not resolved).
* Rejected: a heavyweight linter ruleset (style rules would touch hundreds of lines of working numerical code for no safety gain); one class per physical model (the modules are already single-purpose); making soft ranges errors (they are judgement, and a deliberate extreme case must still run).
* Rejected: hard-failing on unknown range names at call time rather than import time; typos now fail when the module is imported.

## 0.9.0 - 2026-11-05: iFluids service map and data-centre helpers
* New: `datacentre` (PUE, cooling-water balance, evaporative water, UPS battery and diesel sizing, N/N+1/2N availability, generic HAZID
  prompts), CLI `datacentre`, docs/DATACENTRE.md, docs/IFLUIDS_SERVICES.md (brochure services mapped to modules, with gaps), eight new
  entries in the coverage map (three implemented, five marked not implemented). 7 new tests.
* Built from the iFluids Engineering brochure service list, because data centres reuse the same disciplines: hydraulics, power
  system studies, fire and risk. No iFluids data-centre project is claimed.
* Rejected: Uptime tier availability percentages, ASHRAE envelopes and NFPA 2001/75 design values as defaults (documents not read;
  remembered numbers could be wrong). Diesel specific fuel consumption has no default, since it is vendor data. A common-cause factor was
  left out rather than invented, so availability is optimistic and says so.
* Checked: the evaporative water formula reproduces a hand calculation (1.46 L evaporated, 2.19 L at 3 cycles); cooling-water flow
  satisfies the energy balance in both directions.

## 0.8.0 - 2026-11-05: consultancy study tools (bow-tie, OBRA, emergency zones, SIL lifecycle, F&G, PHA, thermal/ATEX, RAM)
* New: `bowtie`, `qra.buildings`, `qra.emergency`, `sil_lifecycle`, `fg_mapping`, `pha`, `thermal_runaway`, `atex`, `ram`, `tools` runner,
  CLI `tool` and `qra buildings|emergency`; worked examples in `process_safety/examples/`; docs/STUDIES.md. 166 tests (24 new).
* QRA footprints gained `Effect.field()` (flux, overpressure, engulfment, cloud, concentration) so buildings and emergency zones reuse
  the same events instead of re-modelling.
* Found while building: the TNT field gives 4000 kPa inside a vapour cloud. Added a flagged 800 kPa cap (`vce_overpressure_cap_kpa`)
  for building and zone use. H2S ERPG-1 on a 22 s release gave a 20 km zone (steady-plume artefact), so the example uses ERPG-3/2 only and
  the limitation is documented. Point gas detectors first used line-of-sight blocking, which is wrong for gas that diffuses around
  obstacles: it is now opt-in for point detectors (still on for flame detectors). Mixed-key CSV exports (closed actions, toxic distances) fixed.
* Verified before coding: Stoessel classes (both TUV SUD EPSC lecture examples reproduced as tests), Purple Book discrete building
  vulnerability (DNV note), IEC 61511 Table 6 (COR1 copy), Route 1H tables, KSt classes, MoEF TGM damage criteria.
* Rejected: API 752/753 building damage levels and pressure-impulse curves (paywalled: custom curves are inputs); IEC 60079-10-1 ventilation
  table beyond two cases and zone extents; dust-vent sizing; a default risk-graph calibration; Keller TD24-from-DSC-onset correlation (not verified).

## 0.7.0 - 2026-11-05: quantitative risk assessment workflow (`qra` package)
* New `process_safety/qra/`: hazid, frequency, eta, effects, risk, alarp, mitigation, validate, progress, study, report; CLI `qra`;
  docs/QRA.md; worked example `qra/examples/lpg_terminal.json`. 142 tests (28 new, identity/conservation based).
* Generic LOC frequencies ship only for rows seen in public documents (PHMSA LNG failure-rate table 2015, HSE PCAG 6K, HSE generic
  vessel value), each with its source. Pumps, compressors, valves and flanges have no verified public row, so the study must supply
  them: rejected shipping remembered OGP 434-1 / Purple Book numbers.
* Cox-Lees-Ang ignition/explosion probabilities verified against the EU JRC RAPID-N tabulation. The immediate/delayed split is not in
  Cox and is a required study input (no default) rather than a hidden assumption.
* Wind-sector handling: first version sent each plume down the sector centreline only. The map showed spokes and the village receptor
  was missed by geometry (IR 2.6e-9/yr). Spreading each sector over adaptive sub-directions (step <= 1/3 of the plume's angular width)
  moved it to ~1e-4/yr, converged within ~6% when the resolution is doubled. Sample runs now report this convergence check automatically.
* Pool area bug found in the first sample run: a small leak inside a bund was given the whole bund area. Fixed: continuous releases
  use the burn-off area capped by the bund.
* Consistency identities checked on every run: event-tree branches sum to 1, PLL from F-N events equals population-weighted LSIR,
  max LSIR <= total LOC frequency, monotone F-N, footprints vs grid extent.
* Rejected: India-wide default criteria (none exists; OISD-STD-118 / PNGRB / MSIHC bases not read - use `custom`); dense-gas model
  (no verifiable open formulation within scope - use the override hook with Phast/RISKCURVES footprints); a default VPF (policy input).

## 0.6.0 - 2026-11-03: electrical and mechanical safety
* New: `electrical`, `noise`, `mechanical_safety`, docs/ELECTRICAL_MECHANICAL.md. 114 tests.
* The arc-flash calculator enforces OSHA's applicability limits (open-air three-phase up to 15 kV) and refuses enclosed equipment and higher voltages
  instead of returning a number. Rejected: reproducing IEEE 1584 empirical equations (could not be verified; gives wrong answers if mis-recalled),
  NFPA 70E PPE category tables (paywalled).
* ISO 13855 is implemented in its pre-2024 form with an explicit edition warning, because the 2024 edition changed the formula.
* Rejected: full ISO 13849-1 architecture assessment (category, MTTFd, DC), earthing grid design, protection coordination studies, load flow:
  these need models and data beyond the formula level.

## 0.5.0 - 2026-11-03: LNG, LPG, refinery, petrochemical and chemicals coverage
* New: `props` (Lee-Kesler/Rackett), `lng`, `lpg`, `rmp`, `flare_system`, `plant_units`; docs/SECTORS_AND_LESSONS.md. 102 tests.
* Chose property correlations over a property database or CoolProp: dependency-free and testable against well-known values.
* Corrected a mistake in my own wording while building `rmp`: neutral-gas Gaussian screening is NOT a lower bound for dense gases. At the
  RMP worst-case conditions it can over- or under-predict badly (chlorine distances come out tens of km) so it is labelled an order-of-magnitude
  flag; the TNT-equivalent 1 psi flammable distance is the more robust output. The lookup bug (a substring match returned the wrong
  substance) was fixed by preferring CAS/exact/prefix matches.
* Rejected: coding LNGFIRE3/DEGADIS-style siting, NFPA 59A spacing tables, OISD-STD-194/150/144 requirements (paywalled, not read);
  rapid-phase-transition energetics; HF alkylation and FCC afterburn models (no verifiable open source found).

## 0.4.0 - 2026-11-03: PSM management system, MAH classification, pipeline design
* New modules `psm`, `mah`, `pipeline` built from primary public texts that were actually fetched and read (OSHA 1910.119 and Appendix A,
  Seveso III Annex I, 49 CFR 192). Data tables are parsed from those texts, with unparsed rows omitted instead of guessed.
* Rejected/blocked: EPA equipment-leak emission factors (EPA site blocks automated access; the OISD-224 fugitive-VOC use case therefore stays
  unimplemented rather than coded from remembered factors); AXA XL fire-water demand guide (blocked); eCFR (redirect to a block page: used the
  Cornell LII copy instead); synergenog and MDPI (blocked, not retried); Purdue deck (empty retrieval).
* Rejected: reproducing OISD/NFPA spacing and fire-water rate tables (paywalled or not retrievable).

## 0.3.0 - 2026-11-03: more process-safety design cases
* Added pool fire, flammability/inerting/static, structural fire and PFP screening, depressuring with minimum-temperature check,
  overfill alarm placement and PSV inlet/outlet piping checks (88 tests).
* Depressuring is offered as isothermal/adiabatic bounds, not a single answer: heat input and liquid flashing decide the real curve.
* Rejected: dust-explosion vent sizing (NFPA 68 / VDI 3673 coefficients could not be verified), jet-fire flame length correlations,
  acoustic-induced vibration sound-power constants, gas control-valve Cv constants. All stay unimplemented rather than guessed.

## 0.2.0 - 2026-11-03: wider industry coverage
* Added hydraulics, fire-water, vessel mechanical, release, dispersion, explosion, consequence probits, reliability (fault/event trees),
  HAZOP worksheet generation, emissions and reaction-hazard screening. Every module is stdlib-only and tested against identities
  (equation residuals, mass conservation, analytic limits) rather than against remembered example numbers.
* Rejected: hard-coding OISD/NFPA application rates, damage-overpressure tables, gas control-valve Cv constants and Stoessel criticality
  classes: they could not be verified from open text, so they stay inputs or are marked not implemented.
* Rejected: building a QRA engine. Frequency data, ignition and population modelling and dense-gas physics need validated software;
  this package supplies screening inputs and cross-checks only.

## 0.1.0 - 2026-11-03
* Stdlib-only, no numpy/CoolProp: keeps it runnable anywhere and every number traceable. Rejected: depending on `fluids`/`thermo`
  (good libraries; recommended instead as an independent cross-check, see docs/TOOLKIT_SURVEY.md).
* Gas/liquid PSV equations derived from isentropic orifice flow rather than pasted constants; tests assert they reproduce the API
  SI constants, which catches unit slips.
* API 2000: implemented the **5th edition (1998)** because it is the only text that could be read (public). The 7th edition changed the
  thermal method and is NOT implemented; fire-case equations and tables are unchanged in structure but check your edition.
  Found while testing: printed Table 3B rows at 110 m2 (+4%) and 19 m2 (+1.1%) deviate from the standard's own Eq 1B; Eq 1B must use
  latent heat in J/kg even though the text says kJ/kg.
* Vapour-filled fire: **rejected** coding the API 521 empirical F' formula (constants and SI/US units could not be verified; an
  error undersizes a safety device). Built a transient wall/gas model instead, which also compares depressuring and PSV.
* Excluded licensed material on purpose: this repository contains no licensed standards, vendor datasheets or company documents (e.g. Shell DEPs), and must stay that way.
* Exposed physical models as inputs where the standards give judgement values (K factors, fire flux, film coefficient).

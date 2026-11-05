# Changelog (decisions, including rejected alternatives)

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

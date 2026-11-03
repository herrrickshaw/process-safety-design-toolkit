# Changelog (decisions, including rejected alternatives)

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

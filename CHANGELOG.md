# Changelog (decisions, including rejected alternatives)

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

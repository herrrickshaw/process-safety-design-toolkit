# Building an open jet-fire model, and being honest about what it does not prove

*Draft for review. Demo and repository links are at the bottom.*

A jet fire from a pressurised release is one of the hazards process-safety engineers screen most often, and the usual tools for it (Phast, FRED, EFFECTS) are commercial. I wanted to know how much of that workflow can be built from open material, and where the open material runs out. This post is what I found, what I built, and what I could not prove.

## Start with the survey, not the code

I began by looking for open-source literature and software across the whole chain: a release (flashing or not), a fire or dispersion model, and the response of the metal it hits.

What exists in the open:

- **Method documentation.** DNV publishes the theory and validation documents for the jet-fire model in Phast, including the Chamberlain, Cook and Johnson correlations. The Sandia LNG fire-model protocol and the HSE research reports on jet-fire models and vessel impingement are free.
- **Software.** FDS (mostly Fortran), FireFOAM, HyRAM+ for hydrogen (GPL-3.0), the EPA's DEGADIS (Fortran) for dense gas, ALOHA for screening, and a small MATLAB toolbox, fireSIM, that implements pool-fire, fireball and Shell-Chamberlain jet-fire formulas.
- **Data.** NIST-JANAF thermochemistry, NIST cryogenic material fits, the Sandia hydrogen compatibility reference, the NIMS creep sheets.

What I did not find: an open implementation of flashing-release source terms feeding a jet-fire model, an open validated case of a jet flame heating steel in FDS or FireFOAM, a plain carbon-steel entry in NIST's cryogenic database, or a free copy of the Eurocode steel-at-fire-temperature table. Those gaps are the real finding.

## One module, built from the source

The toolkit I added to is a standard-library-only Python package with a strict rule: every number needs a source that was actually read, and tests check identities rather than remembered examples. That rule shaped the work.

I downloaded the DNV theory document and read the vapour-phase equations in full. The new module, `jet_flame`, takes the post-expansion mass flow, density and velocity, plus the molecular weight, heat of combustion, wind and release angle. It returns the effective source diameter, the still-air flame length (by solving Kalghatgi's correlation numerically), the flame length in wind, the angle of the flame axis, the lift-off distance, the frustum widths, the fraction of heat radiated and the surface emissive power.

The tests are identities, not looked-up answers:

- the frustum geometry closes (the hole-to-tip distance equals the flame length);
- the radiated power balances (surface emissive power times area equals the radiated fraction times heat release, when the cap is not applied);
- in the high-velocity limit the flame length tends to the momentum-dominated constant of the correlation;
- the angle correlation is continuous where its two branches meet.

That last one mattered. The text extracted from the PDF was ambiguous for two equations. For the angle correlation I picked the reading that is continuous at the branch point, because only that one passes the test. I flagged both readings in the changelog for confirmation against Chamberlain's original paper, which I have not read.

## What the plausibility check did and did not show

DNV tabulates the inputs of seven Chamberlain field trials. I ran them through the module with an approximate natural-gas heat of combustion. Frustum lengths came out between 17 and 54 metres, inside the span DNV plots for the measurements except for one trial. Surface emissive power for the larger trials fell in the measured range, but for the three smaller, higher-velocity trials it came out above it.

That is a plausibility check, not a validation. DNV gives the measured values only as plots, so I could not compute a per-test error, and I did not put any of those numbers into the tests. The honest status of the module is: implemented from a source that was read, tested for internal consistency, roughly in range, not validated.

## Limits worth stating plainly

Pure vapour only. Wind in the plane of the release. No ground impingement. No two-phase or liquid release, no hydrogen or other low-luminosity flames, and no Johnson correlations, which DNV recommends for near-horizontal releases. The density and velocity must come from a separate discharge model. It is a screening aid.

## The demo

I also built a small browser calculator that runs the same equations and draws the flame to scale, with three reference cases that it checks against the Python results. It runs entirely in the browser. **Demo: https://jet-flame-screening.lovable.app** (its self-check panel shows all three reference cases passing).

## What I would do next

1. Digitise the measured flame lengths and emissive powers from the validation plots, or find Chamberlain's tables, and add a real cross-check with an error band.
2. Add a flashing-release source term so the density and velocity come from the same toolchain.
3. Replace the recalled steel-strength values with the Eurocode table once someone with access reads it.

**Repository:** https://github.com/herrrickshaw/process-safety-design-toolkit (branch `feature/jet-flame-chamberlain`).

*This is an engineering screening aid. It is not a safety case, and it should not be used for design without independent verification.*

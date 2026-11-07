"""Regenerate docs/VALIDATION.md from the cross-check results (needs fluids, thermo, CoolProp).

    python tests/crosscheck/validate.py --json /tmp/xc.json && python scripts/gen_validation.py /tmp/xc.json
"""
import datetime
import json
import os
import sys

HEAD = """# Validation

Run on {date} against independent libraries and closed-form literature formulas. **{ok} of {n} checks are within their stated tolerance.** Reproduce with `pip install fluids thermo CoolProp scipy` then `python tests/crosscheck/validate.py` (CI job `crosscheck`); regenerate this page with `scripts/gen_validation.py`.

## What this does and does not show

* It shows the toolkit's equations and constants agree with independent implementations to the stated tolerance. The tolerance is set per check (0.1% for closed-form identities, 5% for property correlations against an equation of state, 12% where the reference is itself a range).
* It does **not** show that a result is right for a plant. Inputs, scenario selection and the standard edition a project cites are outside the check.
* References: `fluids` (API 520 gas, steam and liquid sizing, Darcy friction, separators, drag, tank geometry, valve units), `thermo` and `CoolProp` (vapour pressure, density, latent heat, real-gas isentropes, and a direct homogeneous-equilibrium integration for two-phase flow), and closed-form formulas typed from the open literature (API 521 fire heat input, Kinney-Graham, Roberts fireball, Burgess/Thomas/Mudan-Croce, IEC 60255, IEEE 80, OSHA 1910.95, Briggs dispersion coefficients, Eisenberg probit, IEC 61508-6, 49 CFR 192/193). Paywalled standards were not read; where a check uses one it is the formula as published in the open literature or in `fluids`.

## Differences to know about

* **Liquid relief area** is about 4.7% lower than `fluids.API520_A_l` for the two cases checked (within the 5% tolerance, but consistently one-sided). The cause was not resolved here (overpressure-correction or discharge-coefficient handling are the likely places). Treat the toolkit's liquid area as a screening value and confirm against the vendor's sizing.
* **Steam relief area** uses the Napier form with the older constant; `fluids` implements the 10th-edition form. They agree within the 5% tolerance for the cases checked; use the edition your project cites.
* **API 2000 fire heat input** has a boundary at exactly 0.07 barg design pressure for wetted areas of 260 m2 and above, where the published table switches formula; the toolkit follows the table as read and the cross-check avoids the boundary.
* **TNT energy** is compared with the literature range 4.184 to 4.69 MJ/kg, not a single value.
* **Two-phase omega method.** With the two-point omega (isentropic, at 90% of the inlet pressure) the choked flux is within 0.7% of a direct CoolProp integration for propane, n-butane and ammonia, and within 2.2% across all 252 rows of the bundled table (18 fluids, up to 90% of the critical pressure). The single-point saturated omega is within 4% of the direct integration below 0.3 of the critical pressure and 7% below 0.5, then degrades toward the critical point (about 13% at 0.7 Pc, up to 38% at 0.9 Pc): use the two-point basis (the default) there.
* **Depressuring minimum temperature.** The ideal-gas isentrope with the inlet-state k is 5 to 9% (10 to 20 K) colder than the real-gas isentrope for methane and nitrogen from 50 to 10 bar. The toolkit value is the lower, so it is conservative for MDMT screening; it is not the metal temperature. The check tolerance is set to 10% for that reason.
* **Lee-Kesler and Rackett** correlations (`props`) agree with the CoolProp reference EOS within 4% (observed worst case 2.1%) for the seven hydrocarbons at Tr 0.6 to 0.8; they are not for polar fluids or near the critical point.

## All checks

| # | Check | Toolkit | Reference | Difference % | Tolerance % | Reference source |
|---|---|---|---|---|---|---|
"""


def main(path):
    r = json.load(open(path))
    ok = sum(1 for x in r if x["ok"])
    out = HEAD.format(date=datetime.date.today().isoformat(), ok=ok, n=len(r))
    for i, x in enumerate(r, 1):
        u = f" {x['unit']}" if x.get("unit") else " "
        out += f"| {i} | {x['name']} | {x['ours']:.6g}{u} | {x['ref']:.6g} | {x['rel_diff_pct']:.3f} | {x['tol_pct']:.3g} | {x['ref_src']} |\n"
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "VALIDATION.md"), "w", encoding="utf-8") as fh:
        fh.write(out)
    print("wrote docs/VALIDATION.md", len(r), "checks")


if __name__ == "__main__":
    main(sys.argv[1])

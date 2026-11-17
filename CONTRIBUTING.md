# Contributing

* Keep the toolkit dependency-free (stdlib only, Python 3.10+). Optional libraries belong only in `tests/crosscheck/`.
* Every number needs a source. If a standard is paywalled and was not read, make the value an input or mark the topic not implemented in `standards.py`; do not type a remembered value.
* Test with identities (energy balance, conservation, monotonic behaviour, analytic limits), not remembered example numbers.
* Log decisions, including rejected alternatives, in `CHANGELOG.md`.
* Every new numeric CLI argument needs a unit: give it a `ranges` entry (its unit is read from there) or a `units = {...}` entry on the command; `scripts/verify_deliverables.py all-args-dimensioned` fails otherwise. Unit rules are in `docs/UNITS.md`.
* Every new command or calculation needs a scenario in `tests/scenarios/scenarios.json` with an independent oracle or a metamorphic relation (not a remembered number).

## Checks to run before a PR

```bash
python -m unittest discover tests          # all tests, CLI golden outputs, generated-docs sync
ruff check --select E9,F63,F7,F82,F401,F811,F841 --target-version py310 process_safety tests
python tests/crosscheck/validate.py        # optional: pip install fluids thermo CoolProp scipy
python scripts/gen_fluid_table.py          # regenerate data/fluid_screening.json (needs CoolProp)
python scripts/gen_validation.py xc.json   # after validate.py --json xc.json
octave-cli --eval "addpath('matlab'); ps_run_tests"   # the MATLAB/Octave ports (needs Octave); tests/test_matlab.py compares them with Python
python scripts/run_scenarios.py --check    # the design-scenario suite (SI and US runs, oracles, metamorphic checks)
python scripts/run_scenarios.py --write    # regenerate docs/SCENARIO_REPORT.md; --update re-captures snapshots after a deliberate change
python scripts/gen_input_templates.py --write   # regenerate docs/INPUT_TEMPLATES.md and templates/ after adding or changing an argument
```

Regenerate the generated docs after editing `ranges.py` or `glossary.py`:

```bash
python -m process_safety ranges --markdown > docs/RANGES.md
python -m process_safety glossary --markdown > docs/GLOSSARY.md
```

If a CLI output changes on purpose, update `tests/golden/cli_golden.json` in the same PR and say why in the changelog.

## Releasing

Bump `version` in `pyproject.toml`, add the `CHANGELOG.md` entry, merge, then tag `vX.Y.Z`. The release workflow checks the tag against the version, runs the tests, builds, and creates the GitHub release.

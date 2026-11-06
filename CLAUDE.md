# CLAUDE.md

Guidance for AI coding agents working on this repo. Contributor rules are in `CONTRIBUTING.md`; this file adds the working loop.

## Hard rules (from CONTRIBUTING.md, repeated because they are the ones agents break)

- Standard library only, Python 3.10+. Optional libraries belong only in `tests/crosscheck/`.
- Every number needs a source. If a standard is paywalled and was not read, make the value an input or mark the topic not implemented in `standards.py`. Never type a remembered value.
- Test with identities (energy balance, conservation, monotonic behaviour, analytic limits), not remembered example numbers.
- Log decisions, including rejected alternatives, in `CHANGELOG.md`.
- Never commit text extracted from licensed standards or company design practices (Shell DEPs and similar).

## Working loop

1. **Spec first for anything non-trivial.** Write what the function takes, returns, and refuses, with the source of each constant, before code. (`spec-driven` habit; see `docs/DESIGN_LIFECYCLE_PLAN.md`.)
2. **Read the source, then cite it.** Use the `source-driven-development` skill: fetch the clause or paper, record title, edition and clause in the docstring. A search snippet is not a source.
3. **Test first.** Use `test-driven-development`: write the identity test, watch it fail, then implement.
4. **Root cause before fix.** On a failing test or wrong number, use `debugging-and-error-recovery`: reproduce, find the cause, fix only that, add a regression test. Do not touch unrelated modules while debugging.
5. **Doubt the result.** For any calculation that feeds a safety decision, use `doubt-driven-development`: check units, limits and a second route (hand calc or `tests/crosscheck/`) before calling it done.
6. **Review before PR.** Use `code-review-and-quality`; for ranges and standards also check that `ranges.py` limits are enforced and `RANGES.md` is regenerated.
7. **Record it.** `documentation-and-adrs`: decisions go in `CHANGELOG.md`; regenerate docs listed in `CONTRIBUTING.md`.

## Checks before any PR

```bash
python -m unittest discover tests
ruff check --select E9,F63,F7,F82,F401,F811,F841 --target-version py310 process_safety tests
```

Say what was run and the result. If a check was not run, say so.

## Domain cautions

- Outputs are engineering screening aids, not certified design. Keep the limits statement in new CLI outputs.
- Changing a CLI output on purpose means updating `tests/golden/cli_golden.json` in the same change, with the reason in the changelog.
- Compliance and legal clause entries carry a source grade (A or B); do not promote a grade without reading the primary text.

## Credits

Skills in `.claude/skills/` come from Addy Osmani's `agent-skills` (MIT); the working loop borrows ideas from Garry Tan's `gstack`. See `THIRD_PARTY_NOTICES.md`.

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

## Fetching data from open sources

Learned while building the leak chain (`docs/SOURCE_TERM_SOURCES.md` is the worked example).

1. **Fetch the document, not a summary.** Download the PDF with `curl` (browser User-Agent, about one request per second per host) into its own new directory, extract text with `pdftotext -layout`, and read the passage. A search snippet or a fetch-tool summary is grade C: the summariser can be wrong, so take every number and equation from the extracted text. Where extraction garbles an equation, render the page (`pdftoppm`) and read the image.
2. **Prefer the publisher's own copy.** Known open locations: TNO Yellow Book at `publications.tno.nl/publication/34634119/QIKv78/TNO-2005-yellow.pdf`; the Dutch Publicatiereeks Gevaarlijke Stoffen at `content.publicatiereeksgevaarlijkestoffen.nl/documents/PGS2/...` (Yellow), `PGS3/...` (Purple), `PGS4/...` (Red) and `publicatiereeksgevaarlijkestoffen.nl/documents/81474/...` (PGS 1, the Green Book, in Dutch). Do not cite unofficial uploads (Scribd and similar): they cannot be verified and often return errors.
3. **Stop at a wall.** A CAPTCHA, robot check, WAF challenge, login, registration or "enter your name and company" form means stop on that host. Do not use stealth or fingerprint-spoofing browsers, identity or proxy rotation, or challenge solvers, and do not submit anyone's details to a form. Report the item as unavailable and ask the owner to share the document. Paywalled books (CCPS, API, ISO, Wiley) are never scraped.
4. **No unvetted crawlers.** Do not install or run third-party scraper binaries or build them from an unknown account. If the owner wants one used, they run it themselves, with robots.txt respected and stealth off, on named open URLs, and share the output files; read those as documents.
5. **Check, then grade.** Reproduce the source's own worked example as a test where it has one; check each equation against a second source (the Purple Book heat probit was confirmed against the Norwegian DSB guideline and the Dutch Green Book). Report misprints found rather than silently fixing them, and say which form reproduces the book's numbers.
6. **Record every source** in the ledger with title, edition, section or page, route, and grade (A = the standard's text was read; B = a public document quoting it; C = web page or summary). Say what is still missing and what would close it. Never commit extracted text from licensed standards: extract values and equations, cite the clause.

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

<!-- BACKLOG.MD GUIDELINES START -->
<!-- backlog.md-instructions-version: 1.55.3 -->
<CRITICAL_INSTRUCTION>

## Backlog.md Workflow

This project uses Backlog.md for task and project management.

**At the beginning of each conversation in this project, run `backlog instructions overview` before answering or taking action. Re-read it only if you have not read it yet in the current conversation.**

Use the overview to decide whether to search, read, create, or update Backlog tasks.

Before task lifecycle actions, read the matching detailed guide:
- `backlog instructions task-creation` before creating or splitting tasks
- `backlog instructions task-execution` before planning, changing status or assignee, adding a plan or implementation notes, or implementing task work
- `backlog instructions task-finalization` before checking acceptance criteria, writing final summaries, or moving tasks to terminal statuses

Use `backlog <command> --help` before running unfamiliar commands. Help shows options, fields, and examples.

Do not edit Backlog task, draft, document, decision, or milestone markdown files directly. Use the `backlog` CLI so metadata, relationships, and history stay consistent.

</CRITICAL_INSTRUCTION>
<!-- BACKLOG.MD GUIDELINES END -->

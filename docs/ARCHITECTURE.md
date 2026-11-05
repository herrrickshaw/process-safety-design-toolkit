# Architecture

The toolkit is dependency-free Python (stdlib only, 3.10+). Each module is one calculation family; the command line is a thin layer over them.

```
process_safety/
  constants.py        shared physical constants (R, g, atmosphere): one definition each
  ranges.py           input ranges: hard (impossible, rejected) and soft (atypical, warns)
  glossary.py         terms and abbreviations, single data table
  relief.py, sil.py, ...   calculation modules (pure functions, no I/O)
  qra/                six-step risk-study workflow
  tools.py            JSON-driven study tools (bowtie, SIF, F&G, thermal, ATEX, RAM, PHA)
  cli/
    registry.py       Command registry, output helper, range enforcement
    *_cmds.py         one module per domain; one class per command
  __main__.py         builds the parser from the registry and dispatches
```

## How SOLID shows up

| Principle | Where |
|---|---|
| Single responsibility | Calculation modules compute; `cli/` parses and prints; `ranges.py` validates; `glossary.py` holds definitions. `__main__.py` only wires. |
| Open/Closed | A new command is a new class with `@command("name")`; no dispatcher is edited. (Before 0.10.0 this was a 34-branch `if/elif` in one function.) |
| Liskov | Every command class provides `add_arguments(parser)` and `run(args, parser)`; the framework treats them alike. |
| Interface segregation | A command declares only its arguments and an optional `ranges` map; nothing else is required. |
| Dependency inversion | The CLI depends on the registry interface, not on each command; calculation modules do not import the CLI. |

## Patterns used

* **Registry / command pattern** for the CLI (`cli/registry.py`).
* **Single data source**: `ranges.RANGES` and `glossary.CATEGORIES` generate `docs/RANGES.md` and `docs/GLOSSARY.md` and the `ranges` and `glossary` commands; tests fail if the docs drift.
* **Decorator** `@validated(...)` checks a function's arguments against `RANGES` (hard ranges only) so library users get the same protection as CLI users.
* **Golden-output tests** (`tests/golden/cli_golden.json`) pin the exact output of 40 CLI cases, so a refactor cannot change a number unnoticed.

## Range policy

* **Hard range**: physically or mathematically impossible (negative absolute temperature, Cp/Cv of 1.0 or less, a fraction above 1). CLI exits 2 with the reason; library functions raise `ranges.RangeError`.
* **Soft range**: possible but atypical (Cp/Cv above 1.67, a wind speed above 25 m/s). The CLI prints a warning to stderr and still runs. `--no-range-check` skips both for a deliberate out-of-range study.
* Soft ranges are engineering judgement, not a standard's limits. They are there to catch unit slips (kPa for kPag, mm for m), not to certify a value.

## Adding a command

1. Add a class in the right `cli/*_cmds.py` with `@command("name", "help text")`, `add_arguments`, `run`, and a `ranges = {dest: range_name}` map.
2. Add any new quantity to `ranges.py`; regenerate `docs/RANGES.md`.
3. Add a test, and a golden case if the output is stable.

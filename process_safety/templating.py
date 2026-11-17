"""Input templates: describe every argument of a CLI command (unit in SI and US, accepted range, default, help), write a fill-in
JSON template, and turn a filled template back into the command line. The command classes are the single source: nothing here is
typed per command, so a new command or argument shows up in its template with no edit.
"""
from __future__ import annotations

import argparse
import csv
import io
import json

from . import ranges, units
from .cli.registry import REGISTRY, arg_unit


def _parser(cmd) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(add_help=False)
    cmd.add_arguments(p)
    return p


def _bounds(rng, cli_unit: str, system: str):
    def conv(x):
        return None if x is None else round(units.from_cli(x, cli_unit, system), 6)
    return conv(rng.hard_min), conv(rng.hard_max), conv(rng.soft_min), conv(rng.soft_max)


def describe(name: str, system: str = "si") -> list[dict]:
    """One dict per argument of command `name`, in declaration order, with units for `system`."""
    cmd = REGISTRY[name]
    rows = []
    for a in _parser(cmd)._actions:
        if a.dest == "help":
            continue
        flag = isinstance(a, argparse._StoreTrueAction)
        typ = "flag" if flag else getattr(a.type, "__name__", "str") if a.type else "str"
        cli_u = arg_unit(cmd, a.dest)
        rname = cmd.ranges.get(a.dest)
        row = {"command": name, "name": a.dest, "flag": a.option_strings[-1] if a.option_strings else "(positional)",
               "positional": not a.option_strings, "required": bool(a.required) if a.option_strings else a.nargs not in ("?", "*"),   # positional: by nargs only (Python 3.10/3.11 flag nargs="*" as required)
               "type": typ, "list": a.nargs in ("+", "*"), "default": a.default if a.default not in (None, []) and not flag else None,   # older Pythons give [] for an empty nargs="*"
               "choices": list(a.choices) if a.choices else None, "help": a.help or "",
               "unit_working": cli_u, "unit": units.display_unit(cli_u, system) if cli_u else None,
               "unit_si": cli_u, "unit_us": units.us_unit(cli_u) if cli_u else None, "range": rname,
               "hard_min": None, "hard_max": None, "soft_min": None, "soft_max": None}
        if rname and cli_u:
            row["hard_min"], row["hard_max"], row["soft_min"], row["soft_max"] = _bounds(ranges.RANGES[rname], cli_u, system)
        if row["default"] is not None and cli_u and typ in ("float", "int"):
            d = row["default"]
            row["default"] = [round(units.from_cli(x, cli_u, system), 9) for x in d] if isinstance(d, (list, tuple)) else round(units.from_cli(d, cli_u, system), 9)
        rows.append(row)
    return rows


def template(name: str, system: str = "si") -> dict:
    """The fill-in file: `inputs` holds null for each required value and the default for the rest; `_guide` explains each one."""
    rows = describe(name, system)
    inputs, guide = {}, {}
    for r in rows:
        inputs[r["name"]] = r["default"] if not r["required"] else None
        g = {"flag": r["flag"], "required": r["required"], "type": r["type"] + (" list" if r["list"] else ""), "unit": r["unit"],
             "help": r["help"]}
        if r["choices"]:
            g["choices"] = r["choices"]
        if r["range"]:
            g["range"] = {k: r[k] for k in ("hard_min", "hard_max", "soft_min", "soft_max") if r[k] is not None}
        guide[r["name"]] = g
    note = ("Fill in `inputs` using the unit in each _guide entry. Help text may quote SI units; the `unit` field is the one that applies. "
            "psig and psia are different: gauge arguments (set_g, back_g ...) are psig, absolute ones psia. Temperatures are readings, not differences.")
    return {"command": name, "units": system, "_note": note, "inputs": inputs, "_guide": guide}


def to_argv(filled: dict) -> list[str]:
    """`--units <sys> <command> <args...>` from a filled template. Null values for optional arguments are left out."""
    name = filled["command"]
    if name not in REGISTRY:
        raise ValueError(f"unknown command {name!r}")
    system = filled.get("units", "si")
    rows = {r["name"]: r for r in describe(name, system)}
    inputs = filled.get("inputs", {})
    unknown = sorted(set(inputs) - set(rows))
    if unknown:
        raise ValueError(f"{name}: unknown input(s) {', '.join(unknown)}; allowed: {', '.join(rows)}")
    missing = [n for n, r in rows.items() if r["required"] and inputs.get(n) is None]
    if missing:
        raise ValueError(f"{name}: required input(s) not filled in: {', '.join(missing)}")
    pos, opts = [], []
    for n, r in rows.items():
        v = inputs.get(n)
        if v is None or v is False:
            continue
        vals = v if isinstance(v, list) else [v]
        if r["type"] == "flag":
            opts.append(r["flag"])
        elif r["positional"]:
            pos += [str(x) for x in vals]
        else:
            opts += [r["flag"], *[str(x) for x in vals]]
    return ["--units", system, name, *opts, *pos]


def csv_all(system_pair=("si", "us")) -> str:
    out = io.StringIO()
    w = csv.writer(out, lineterminator="\n")
    w.writerow(["command", "parameter", "flag", "required", "type", "default", "unit_si", "unit_us", "hard_min_si", "hard_max_si",
                "soft_min_si", "soft_max_si", "hard_min_us", "hard_max_us", "soft_min_us", "soft_max_us", "choices", "help"])
    for name in REGISTRY:
        si, us = describe(name, "si"), describe(name, "us")
        for a, b in zip(si, us):
            w.writerow([name, a["name"], a["flag"], "yes" if a["required"] else "", a["type"] + (" list" if a["list"] else ""),
                        "" if a["default"] is None else a["default"], a["unit_si"] or "", a["unit_us"] or "",
                        *["" if a[k] is None else a[k] for k in ("hard_min", "hard_max", "soft_min", "soft_max")],
                        *["" if b[k] is None else b[k] for k in ("hard_min", "hard_max", "soft_min", "soft_max")],
                        " ".join(map(str, a["choices"] or [])), a["help"]])
    return out.getvalue()


def markdown_all() -> str:
    lines = ["# Input templates", "",
             "Generated by `python scripts/gen_input_templates.py --write` from the command definitions; do not edit by hand.", "",
             "Fill one in with `python -m process_safety template <command> --units si|us > in.json`, edit `inputs`, then run",
             "`python -m process_safety run in.json`. The same table as a spreadsheet: `templates/inputs_all.csv`; one ready file per",
             "command and unit system: `templates/inputs/<command>.<si|us>.json`. Unit rules and the metric/US differences: `docs/UNITS.md`.", ""]
    for name, cmd in REGISTRY.items():
        lines += [f"## `{name}`", "", cmd.help or "", "",
                  "| Parameter | Flag | Req | SI unit | US unit | Hard range (SI) | Soft range (SI) | Default | Meaning |", "|---|---|---|---|---|---|---|---|---|"]
        for r in describe(name, "si"):
            def span(lo, hi):
                return "" if lo is None and hi is None else f"{'-inf' if lo is None else lo} .. {'inf' if hi is None else hi}"
            hard, soft = span(r["hard_min"], r["hard_max"]), span(r["soft_min"], r["soft_max"])
            lines.append(f"| `{r['name']}` | `{r['flag']}` | {'yes' if r['required'] else ''} | {r['unit_si'] or ''} | {r['unit_us'] or ''} | "
                         f"{hard} | {soft} | {'' if r['default'] is None else r['default']} | {r['help'].replace('|', '/')} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def dump(obj) -> str:
    return json.dumps(obj, indent=2, default=float) + "\n"

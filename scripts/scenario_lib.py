"""Scenario engine: run documented design scenarios against the toolkit and judge the outcomes.

A scenario (tests/scenarios/scenarios.json) is a command line (kind "cli"), a short sequence of steps in a scratch folder
(kind "steps", for the JSON tools and file-writing commands), or a Python call (kind "python"). Each carries up to five kinds of
check, and every check has a verdict, so a scenario "passes" only if all of them do:

  expect      physical or logical bounds on the result (positive, below a ceiling, a flag, a category)
  oracle      an independent recomputation written as a formula from first principles or from a unit definition, not from the
              toolkit's own code ("1500 lb x 0.45359237 kg/lb")
  meta        a metamorphic relation: change one input and test the way the answer must move (double the flow, the area doubles;
              raise the set pressure, the area falls). These need no remembered answer.
  si_us       the same case typed in US-customary units through `--units us` must give the SI result (CLI scenarios)
  regression  a snapshot of the current values (rtol 1e-6) so a later change is noticed; this one is NOT independent evidence

Scenarios never rely on a remembered example number: a number a standard published is used only where the toolkit already cites it,
and then through an oracle formula that shows where it comes from.
"""
from __future__ import annotations

import ast
import argparse
import dataclasses
import importlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
SCENARIO_FILE = os.path.join(ROOT, "tests", "scenarios", "scenarios.json")

from process_safety import templating, units  # noqa: E402
from process_safety.cli import REGISTRY  # noqa: E402
from process_safety.cli.registry import arg_unit  # noqa: E402

RTOL = 1e-9          # SI vs US run
RTOL_SNAP = 1e-6


# ---- loading ------------------------------------------------------------------------------------------------------------------
def load(path: str = SCENARIO_FILE) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


# ---- path access and formulas --------------------------------------------------------------------------------------------------
_TOKEN = re.compile(r'\["[^"]+"\]|[^.\[\]]+|\[\d+\]')


def get_path(obj, path: str):
    if path in ("", "$value"):
        return obj
    cur = obj
    for tok in _TOKEN.findall(path):
        if tok.startswith('["'):
            cur = cur[tok[2:-2]]
        elif tok.startswith("["):
            cur = cur[int(tok[1:-1])]
        else:
            cur = cur[tok]
    return cur


_FUNCS = {"sqrt": math.sqrt, "log": math.log, "log10": math.log10, "exp": math.exp, "max": max, "min": min, "ceil": math.ceil,
          "pi": math.pi, "abs": abs, "sin": math.sin, "cos": math.cos, "tan": math.tan, "radians": math.radians}
_OK = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant, ast.Name, ast.Call, ast.Load, ast.Add, ast.Sub, ast.Mult, ast.Div,
       ast.Pow, ast.USub, ast.UAdd, ast.Mod, ast.FloorDiv)


def eval_formula(expr: str, result) -> float:
    """Evaluate arithmetic with $path references into `result`. Only numbers, + - * / **, and the small function table are allowed."""
    names: dict[str, float] = {}

    def sub(m):
        key = f"v{len(names)}"
        names[key] = get_path(result, m.group(1))
        return key
    src = re.sub(r"\$([A-Za-z0-9_.\[\]]+)", sub, expr)
    tree = ast.parse(src, mode="eval")
    for node in ast.walk(tree):
        if not isinstance(node, _OK):
            raise ValueError(f"formula element not allowed: {type(node).__name__} in {expr!r}")
        if isinstance(node, ast.Name) and node.id not in names and node.id not in _FUNCS:
            raise ValueError(f"unknown name {node.id!r} in {expr!r}")
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name) and node.func.id in _FUNCS):
            raise ValueError(f"call not allowed in {expr!r}")
    return float(eval(compile(tree, "<formula>", "eval"), {"__builtins__": {}}, {**_FUNCS, **names}))


def close(a, b, rtol=RTOL, atol=1e-12) -> bool:
    return math.isclose(a, b, rel_tol=rtol, abs_tol=atol)


# ---- running -------------------------------------------------------------------------------------------------------------------
def run_cli(args: list[str], cwd: str | None = None):
    r = subprocess.run([sys.executable, "-m", "process_safety", *args], capture_output=True, text=True, cwd=cwd or ROOT,
                       env={**os.environ, "PYTHONPATH": ROOT})
    return r.returncode, r.stdout, r.stderr


def parse(out: str):
    try:
        return json.loads(out)
    except ValueError:
        return {"$stdout": out}


def run_python(call: str, kwargs: dict):
    mod, fn = call.rsplit(".", 1)
    f = getattr(importlib.import_module("process_safety." + mod), fn)
    r = f(**kwargs) if callable(f) else f
    if dataclasses.is_dataclass(r):
        r = dataclasses.asdict(r)
    if isinstance(r, tuple):
        r = list(r)
    return r if isinstance(r, dict) else {"value": r}


def execute(sc: dict, vary=None):
    """Run a scenario, optionally with inputs varied (one {"flag"|"kwarg", "factor"} or a list of them) -> (ok, result_or_error)."""
    varies = [] if vary is None else vary if isinstance(vary, list) else [vary]
    kind = sc.get("kind", "cli" if "args" in sc else "steps" if "steps" in sc else "python")
    if kind == "python":
        kw = dict(sc["kwargs"])
        for v in varies:
            kw[v["kwarg"]] = kw[v["kwarg"]] * v["factor"]
        try:
            return True, run_python(sc["call"], kw)
        except Exception as e:  # a scenario that raises is a failed scenario, reported with the reason
            return False, f"{type(e).__name__}: {e}"
    if kind == "cli":
        args = list(sc["args"])
        for v in varies:
            i = args.index(v["flag"]) + 1
            new = float(args[i]) * v["factor"]
            args[i] = str(int(new)) if re.fullmatch(r"-?\d+", args[i]) and new.is_integer() else repr(new)
        rc, out, err = run_cli(args)
        if rc != 0:
            return False, f"exit {rc}: {err.strip()[-300:]}"
        return True, parse(out)
    with tempfile.TemporaryDirectory() as tmp:
        last = None
        for step in sc["steps"]:
            if isinstance(step, dict):
                with open(os.path.join(tmp, step["write"]), "w", encoding="utf-8") as fh:
                    if "json" in step:
                        json.dump(step["json"], fh)
                    else:
                        fh.write(step["text"])
                continue
            rc, out, err = run_cli([x.replace("@ROOT@", ROOT) for x in step], cwd=tmp)
            if rc != 0:
                return False, f"exit {rc} in {' '.join(step)}: {err.strip()[-300:]}"
            last = parse(out)
        files = {}
        for name in sc.get("files", []):
            p = os.path.join(tmp, name)
            if os.path.exists(p):
                with open(p, encoding="utf-8-sig") as fh:
                    files[name] = fh.read()
            else:
                files[name] = None
        if isinstance(last, dict):
            last = {**last, "$files": files}
        else:
            last = {"$value": last, "$files": files}
        return True, last


# ---- checks --------------------------------------------------------------------------------------------------------------------
def check_expect(e: dict, res) -> tuple[bool, str]:
    op, path, want = e["op"], e["path"], e.get("value")
    try:
        got = get_path(res, path)
    except (KeyError, IndexError, TypeError):
        return (op == "absent"), f"{path} missing"
    ok = {
        "exists": lambda: True, "absent": lambda: False,
        "gt": lambda: got > want, "ge": lambda: got >= want, "lt": lambda: got < want, "le": lambda: got <= want,
        "eq": lambda: got == want, "ne": lambda: got != want, "in": lambda: got in want,
        "between": lambda: want <= got <= e["hi"], "true": lambda: bool(got) is True, "false": lambda: bool(got) is False,
        "len_ge": lambda: len(got) >= want, "contains": lambda: want in got,
        "no_prefix": lambda: not any(str(x).startswith(want) for x in got),
        "le_path": lambda: got <= get_path(res, want), "ge_path": lambda: got >= get_path(res, want),
        "close": lambda: close(got, want, e.get("rtol", 1e-6)),
        "sum_close": lambda: close(sum(x[e["key"]] for x in got), want, e.get("rtol", 1e-9)),
        "not_none": lambda: got is not None, "is_none": lambda: got is None,
    }[op]()
    return bool(ok), f"{path} = {got!r}"


def check_oracle(o: dict, res) -> tuple[bool, str]:
    want = eval_formula(o["formula"], res)
    got = get_path(res, o["path"])
    return close(got, want, o.get("rtol", 1e-6), o.get("atol", 1e-12)), f"{o['path']} = {got:.10g} vs formula {want:.10g}"


def check_meta(sc: dict, mt: dict, base) -> tuple[bool, str]:
    ok, var = execute(sc, mt["vary"])
    if not ok:
        return False, f"varied run failed: {var}"
    a, b = get_path(base, mt["path"]), get_path(var, mt["path"])
    rel = mt["relation"]
    if rel == "ratio":
        r = b / a
        return close(r, mt["value"], mt.get("rtol", 1e-6)), f"{mt['path']} x{r:.8g} (want x{mt['value']})"
    verdict = {"increasing": b > a, "decreasing": b < a, "unchanged": close(a, b, 1e-9)}[rel]
    return verdict, f"{mt['path']} {a:.8g} -> {b:.8g} ({rel})"


def _walk_close(si, us, path="", rtol=RTOL):
    """Every key in the SI result must be in the US result with the same value (extra US keys are checked separately)."""
    if isinstance(si, dict):
        if not isinstance(us, dict):
            return [f"{path}: structure differs"]
        bad = []
        for k, v in si.items():
            if k not in us:
                bad.append(f"{path}.{k} missing in US run")
            else:
                bad += _walk_close(v, us[k], f"{path}.{k}", rtol)
        return bad
    if isinstance(si, list):
        if not isinstance(us, list) or len(si) != len(us):
            return [f"{path}: list differs"]
        return [m for a, b in zip(si, us) for m in _walk_close(a, b, path + "[]", rtol)]
    if isinstance(si, bool) or isinstance(si, str) or si is None:
        return [] if si == us else [f"{path}: {si!r} != {us!r}"]
    if isinstance(si, (int, float)):
        return [] if isinstance(us, (int, float)) and close(si, us, rtol, 1e-9) else [f"{path}: {si!r} != {us!r}"]
    return []


def _extra_keys(si, us, path=""):
    """Each recognised-unit key in the SI result must have its US sibling equal to the conversion of the SI value."""
    bad = []
    if isinstance(si, dict) and isinstance(us, dict):
        for k, v in si.items():
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                c = units._convert_key(k, v)
                if c:
                    if c[0] not in us:
                        bad.append(f"{path}.{c[0]} not added")
                    elif not close(us[c[0]], c[1], 1e-9, 1e-12):
                        bad.append(f"{path}.{c[0]} = {us[c[0]]} but SI value converts to {c[1]}")
            else:
                bad += _extra_keys(v, us.get(k), f"{path}.{k}")
    elif isinstance(si, list) and isinstance(us, list):
        for a, b in zip(si, us):
            bad += _extra_keys(a, b, path + "[]")
    return bad


def us_argv(args: list[str]) -> list[str]:
    """The same CLI case written in US units: parse the SI line, convert every dimensioned number, rebuild through the template path."""
    name = args[0]
    cmd = REGISTRY[name]
    p = argparse.ArgumentParser(add_help=False)
    cmd.add_arguments(p)
    ns = vars(p.parse_args(args[1:]))
    inputs = {}
    for dest, v in ns.items():
        u = arg_unit(cmd, dest)
        if v is not None and u and not isinstance(v, bool):
            v = [units.from_cli(x, u, "us") for x in v] if isinstance(v, (list, tuple)) else units.from_cli(v, u, "us")
        inputs[dest] = v
    return templating.to_argv({"command": name, "units": "us", "inputs": inputs})


def check_si_us(sc: dict, base) -> tuple[bool, str, float]:
    rc, out, err = run_cli(us_argv(sc["args"]))
    if rc != 0:
        return False, f"US run exit {rc}: {err.strip()[-300:]}", math.nan
    us = parse(out)
    bad = _walk_close(base, us) + _extra_keys(base, us)
    return not bad, "; ".join(bad[:3]) or "US run equals SI run", 0.0 if not bad else math.nan


def snapshot(res) -> dict:
    out = {}
    if isinstance(res, dict):
        for k, v in res.items():
            if k.startswith("$") or re.search(r"runtime|elapsed|timestamp|wall_time|file$|path$", k, re.I):
                continue          # values that change from run to run (timings, temp paths) are not evidence of a change
            if isinstance(v, bool) or isinstance(v, (int, float, str)) and (not isinstance(v, str) or len(v) < 60):
                out[k] = v
    return dict(list(out.items())[:12])


def check_snapshot(snap: dict, res) -> tuple[bool, str]:
    bad = []
    for k, want in snap.items():
        got = res.get(k) if isinstance(res, dict) else None
        if isinstance(want, (int, float)) and not isinstance(want, bool):
            if not isinstance(got, (int, float)) or not close(got, want, RTOL_SNAP, 1e-12):
                bad.append(f"{k}: {got!r} != {want!r}")
        elif got != want:
            bad.append(f"{k}: {got!r} != {want!r}")
    return not bad, "; ".join(bad[:3]) or f"{len(snap)} values unchanged"


def evaluate(sc: dict) -> dict:
    """Run every check of one scenario -> {"id", "checks": [{"kind","name","ok","detail"}], "ok": bool}."""
    checks = []

    def add(kind, name, ok, detail):
        checks.append({"kind": kind, "name": name, "ok": bool(ok), "detail": detail})

    ok, base = execute(sc)
    if not ok:
        add("run", "scenario runs", False, base)
        return {"id": sc["id"], "checks": checks, "ok": False}
    add("run", "scenario runs", True, "exit 0")
    for e in sc.get("expect", []):
        try:
            v, d = check_expect(e, base)
        except Exception as ex:
            v, d = False, f"{type(ex).__name__}: {ex}"
        add("expect", f"{e['path']} {e['op']} {e.get('value', '')}".strip(), v, d)
    for o in sc.get("oracle", []):
        try:
            v, d = check_oracle(o, base)
        except Exception as ex:
            v, d = False, f"{type(ex).__name__}: {ex}"
        add("oracle", f"{o['path']} = {o['formula']}", v, d)
    for mt in sc.get("meta", []):
        try:
            v, d = check_meta(sc, mt, base)
        except Exception as ex:
            v, d = False, f"{type(ex).__name__}: {ex}"
        vv = mt["vary"] if isinstance(mt["vary"], list) else [mt["vary"]]
        what = " & ".join(f"{x.get('flag') or x.get('kwarg')} x{x['factor']}" for x in vv)
        add("meta", f"{what} -> {mt['path']} {mt['relation']}", v, d)
    if sc.get("si_us", True) and "args" in sc:
        v, d, _ = check_si_us(sc, base)
        add("si_us", "US-unit run equals SI run", v, d)
    if "regression" in sc:
        v, d = check_snapshot(sc["regression"], base)
        add("regression", "snapshot unchanged", v, d)
    return {"id": sc["id"], "checks": checks, "ok": all(c["ok"] for c in checks)}


def run_all(data: dict | None = None):
    data = data or load()
    return [evaluate(sc) for sc in data["scenarios"]]


def update_snapshots(path: str = SCENARIO_FILE) -> int:
    data = load(path)
    n = 0
    for sc in data["scenarios"]:
        ok, res = execute(sc)
        if ok:
            sc["regression"] = snapshot(res)
            n += 1
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")
    return n

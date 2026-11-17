"""Independent checks for the units / templates / scenarios work. Each prints `PASS <name>` only after every assertion holds.

    python scripts/verify_deliverables.py <check> [<check> ...]      (run with no argument to list the checks)

The expected values below are written out from the legal definitions (inch, pound, gallon, foot-pound-force, Btu) rather than read
back from process_safety.units, so a wrong factor in the code cannot also be wrong here.
"""
import ast
import copy
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, HERE)


def ok(name):
    print(f"PASS {name}")


def need(cond, msg):
    if not cond:
        print("FAIL " + msg)
        sys.exit(1)


def rel(a, b, tol=1e-12):
    return math.isclose(a, b, rel_tol=tol, abs_tol=1e-300)


def units_exact():
    from process_safety import units as U
    # published definitions: 1 in = 0.0254 m, 1 lb = 0.45359237 kg, 1 lbf = 4.4482216152605 N, 1 US gal = 3.785411784 L,
    # 1 Btu_IT = 1055.05585262 J, g = 9.80665 m/s2
    in_m, lb_kg, lbf_n = 0.0254, 0.45359237, 4.4482216152605
    need(rel(U.convert(1, "ft", "m"), 0.3048), "ft")
    need(rel(U.convert(1, "in", "mm"), 25.4), "in")
    need(rel(U.convert(1, "ft2", "m2"), 0.3048 ** 2), "ft2")
    need(rel(U.convert(1, "in2", "mm2"), 25.4 ** 2), "in2")
    need(rel(U.convert(1, "lb", "kg"), lb_kg), "lb")
    need(rel(U.convert(1, "psi", "Pa"), lbf_n / in_m ** 2, 1e-12), f"psi {U.convert(1, 'psi', 'Pa')}")
    need(rel(U.convert(1, "psig", "kPag"), lbf_n / in_m ** 2 / 1000, 1e-12), "psig")
    need(rel(U.convert(1, "gal", "m3"), 3.785411784e-3), "gal")
    need(rel(U.convert(1, "gpm", "m3/h"), 3.785411784e-3 * 60), "gpm")
    need(rel(U.convert(1, "Btu/lb", "kJ/kg"), 1.05505585262 / lb_kg, 1e-12), "Btu/lb")
    need(rel(U.convert(1, "Btu/h/ft2", "kW/m2"), 1.05505585262 / 3600 / 0.3048 ** 2, 1e-12), "Btu/h/ft2")
    need(rel(U.convert(1, "lb/ft3", "kg/m3"), lb_kg / 0.3048 ** 3), "lb/ft3")
    need(rel(U.convert(1, "lb/lbmol", "kg/kmol"), 1.0), "lb/lbmol equals kg/kmol")
    need(rel(U.convert(1, "fc", "lux"), 1 / 0.3048 ** 2), "fc")
    need(rel(U.convert(32, "degF", "degC"), 0.0, 1e-12) or abs(U.convert(32, "degF", "degC")) < 1e-12, "32 F is 0 C")
    need(abs(U.convert(212, "degF", "K") - 373.15) < 1e-9, "212 F is 373.15 K")
    need(abs(U.convert(-40, "degF", "degC") + 40) < 1e-9, "-40 is the same in both scales")
    need(rel(U.convert(10, "dF", "dK"), 10 * 5 / 9), "temperature difference has no offset")
    need(abs(U.convert(0, "K", "degF") + 459.67) < 1e-9, "absolute zero is -459.67 F")
    # every unit round-trips, every US counterpart exists and has the same dimension
    for sym, u in U.UNITS.items():
        for v in (0.0, 1.0, 123.456, -40.0):
            back = U.convert(U.convert(v, sym, [s for s, w in U.UNITS.items() if w.dimension == u.dimension][0]),
                             [s for s, w in U.UNITS.items() if w.dimension == u.dimension][0], sym)
            need(abs(back - v) <= 1e-9 * max(1.0, abs(v)), f"round trip {sym} {v} -> {back}")
    for si, us in U.US_FOR.items():
        need(si in U.UNITS and us in U.UNITS, f"unit table lacks {si} or {us}")
        need(U.UNITS[si].dimension == U.UNITS[us].dimension, f"{si} and {us} differ in dimension")
    ok("units-exact")


def gauge_absolute():
    from process_safety import units as U
    for a, b in (("psig", "psia"), ("kPag", "kPa abs"), ("barg", "bara"), ("psia", "psig")):
        try:
            U.convert(1, a, b)
        except U.UnitError:
            continue
        need(False, f"{a}->{b} should be refused")
    need(abs(U.gauge_to_abs(0, "psig", "psia") - 101.325e3 / (0.45359237 * 9.80665 / 0.0254 ** 2)) < 1e-9, "0 psig is one atmosphere in psia")
    need(abs(U.gauge_to_abs(0, "kPag", "kPa abs") - 101.325) < 1e-12, "0 kPag is 101.325 kPa abs")
    need(abs(U.abs_to_gauge(U.gauge_to_abs(150, "psig", "psia"), "psia", "psig") - 150) < 1e-9, "gauge/abs round trip")
    r = subprocess.run([sys.executable, "-m", "process_safety", "convert", "150", "psig", "psia"], capture_output=True, text=True, cwd=ROOT)
    need(r.returncode == 2 and "gauge" in r.stderr, "CLI refuses gauge->absolute without the flag")
    r = subprocess.run([sys.executable, "-m", "process_safety", "convert", "0", "psig", "psia", "--across-atmosphere"], capture_output=True, text=True, cwd=ROOT)
    need(r.returncode == 0 and abs(json.loads(r.stdout)["result"] - 14.6959487755) < 1e-6, "CLI converts with the flag")
    # a US set pressure of 217.557 psig is 1500 kPag, not 1500 kPa absolute
    r = subprocess.run([sys.executable, "-m", "process_safety", "--units", "us", "relief-gas", "--W", "26455.5", "--T", "260.33", "--set-g", "217.557",
                        "--case", "fire", "--M", "44", "--k", "1.13", "--Z", "0.9"], capture_output=True, text=True, cwd=ROOT)
    need(r.returncode == 0 and abs(json.loads(r.stdout)["required_area_mm2"] - 733.27) < 0.5, "US relief-gas matches the SI case")
    ok("gauge-absolute")


def _float_args():
    import argparse as ap
    from process_safety.cli import REGISTRY
    for n, c in REGISTRY.items():
        p = ap.ArgumentParser(add_help=False)
        c.add_arguments(p)
        for a in p._actions:
            if a.dest != "help" and a.type is float:
                yield n, c, a


def all_args_dimensioned():
    from process_safety import units as U
    from process_safety.cli.registry import arg_unit
    n_args = 0
    bad = []
    for n, c, a in _float_args():
        n_args += 1
        u = arg_unit(c, a.dest)
        if u is None:
            bad.append(f"{n}.{a.dest} has no unit")
            continue
        try:
            U.us_unit(u)
        except U.UnitError as e:
            bad.append(f"{n}.{a.dest}: {e}")
    need(n_args >= 150, f"expected at least 150 float arguments, found {n_args}")
    need(not bad, "; ".join(bad[:5]))
    ok("all-args-dimensioned")


def si_us_equivalence():
    import scenario_lib as L
    data = L.load()
    n = 0
    for sc in data["scenarios"]:
        if sc.get("si_us", True) and "args" in sc:
            v, d, _ = L.check_si_us(sc, L.execute(sc)[1])
            need(v, f"{sc['id']}: {d}")
            n += 1
    need(n >= 35, f"only {n} CLI scenarios were run in both unit systems")
    print(f"{n} scenarios run in SI and in US units, worst relative difference below 1e-9 (limit {L.RTOL})")
    ok("si-us-equivalence")


def templates_run():
    from process_safety import templating
    from process_safety.cli import REGISTRY
    import argparse as ap
    for name, cmd in REGISTRY.items():
        p = ap.ArgumentParser(add_help=False)
        cmd.add_arguments(p)
        dests = [a.dest for a in p._actions if a.dest != "help"]
        for system in ("si", "us"):
            t = templating.template(name, system)
            need(list(t["inputs"]) == dests, f"{name} {system}: template lacks arguments {set(dests) ^ set(t['inputs'])}")
            need(t["units"] == system and set(t["_guide"]) == set(dests), f"{name} {system}: guide incomplete")
            for g in t["_guide"].values():
                need("unit" in g and "help" in g, f"{name}: guide entry without unit/help")
    # a filled US template gives the same output as the direct SI command
    import tempfile
    si = subprocess.run([sys.executable, "-m", "process_safety", "relief-gas", "--W", "12000", "--T", "400", "--set-g", "1500", "--case", "fire",
                         "--M", "44", "--k", "1.13", "--Z", "0.9"], capture_output=True, text=True, cwd=ROOT)
    t = templating.template("relief-gas", "us")
    t["inputs"].update(W=12000 / 0.45359237, T=(400 * 9 / 5) - 459.67, set_g=1500 / 6.894757293168361, case="fire", M=44, k=1.13, Z=0.9)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "in.json")
        json.dump(t, open(path, "w"))
        us = subprocess.run([sys.executable, "-m", "process_safety", "run", path], capture_output=True, text=True, cwd=ROOT)
    need(us.returncode == 0, us.stderr[-200:])
    a, b = json.loads(si.stdout), json.loads(us.stdout)
    need(rel(a["required_area_mm2"], b["required_area_mm2"], 1e-9) and a["orifice"] == b["orifice"], "template run differs from direct CLI")
    # an unfilled template is refused and names the missing inputs
    t2 = templating.template("relief-gas", "si")
    try:
        templating.to_argv(t2)
    except ValueError as e:
        need("not filled in" in str(e), str(e))
    else:
        need(False, "unfilled template must be refused")
    ok("templates-run")


def templates_sync():
    r = subprocess.run([sys.executable, os.path.join(HERE, "gen_input_templates.py")], capture_output=True, text=True, cwd=ROOT)
    need(r.returncode == 0, r.stdout + r.stderr)
    from process_safety.cli import REGISTRY
    for name in REGISTRY:
        for s in ("si", "us"):
            need(os.path.exists(os.path.join(ROOT, "templates", "inputs", f"{name}.{s}.json")), f"missing template {name}.{s}")
    doc = open(os.path.join(ROOT, "docs", "INPUT_TEMPLATES.md"), encoding="utf-8").read()
    need(all(f"## `{n}`" in doc for n in REGISTRY), "INPUT_TEMPLATES.md lacks a command")
    ok("templates-sync")


def units_doc():
    from process_safety import units as U
    text = open(os.path.join(ROOT, "docs", "UNITS.md"), encoding="utf-8").read()
    missing = [u for u in set(U.US_FOR.values()) if u not in text]
    need(not missing, f"UNITS.md does not mention: {missing}")
    for phrase in ("--units us", "Gauge is not absolute", "--across-atmosphere", "temperature difference", "lb is mass", "US gallons", "Standard volumes",
                   "Tonnes", "template", "convert", "psig", "gauge_to_abs"):
        need(phrase.lower() in text.lower(), f"UNITS.md lacks '{phrase}'")
    traps = re.findall(r"^\d+\. \*\*", text, re.M)
    need(len(traps) >= 8, f"only {len(traps)} named traps")
    ok("units-doc")


def metamorphic_count():
    import scenario_lib as L
    data = L.load()
    n_sc = sum(1 for s in data["scenarios"] if s.get("meta"))
    need(n_sc >= 25, f"only {n_sc} scenarios have metamorphic checks")
    res = L.run_all(data)
    metas = [c for r in res for c in r["checks"] if c["kind"] == "meta"]
    need(len(metas) >= 100 and all(c["ok"] for c in metas), f"{len(metas)} metamorphic checks, {sum(not c['ok'] for c in metas)} failing")
    rels = {m["relation"] for s in data["scenarios"] for m in s.get("meta", [])}
    need({"ratio", "increasing", "decreasing", "unchanged"} <= rels, f"relation kinds used: {rels}")
    print(f"{n_sc} scenarios, {len(metas)} metamorphic checks evaluated, all pass")
    ok("metamorphic-count")


def scenario_coverage():
    import scenario_lib as L
    from process_safety.cli import REGISTRY
    data = L.load()
    used, tools = set(), set()
    for s in data["scenarios"]:
        if "args" in s:
            used.add(s["args"][0])
        for st in s.get("steps", []):
            if isinstance(st, list):
                used.add(st[0])
                if st[0] == "tool" and st[1] != "example":
                    tools.add(st[1])
    missing = sorted(set(REGISTRY) - used)
    need(not missing, f"commands without a scenario: {missing}")
    want_tools = {"bowtie", "sif", "fg", "thermal", "atex", "ram", "shutdown", "recs", "lngcost", "workflow", "plant", "pha"}
    need(want_tools <= tools, f"tools without a scenario: {sorted(want_tools - tools)}")
    need(len(data["scenarios"]) >= 60, "fewer than 60 scenarios")
    ids = [s["id"] for s in data["scenarios"]]
    need(len(ids) == len(set(ids)), "duplicate scenario ids")
    need(all(s.get("expect") or s.get("oracle") for s in data["scenarios"]), "a scenario has neither expect nor oracle checks")
    need(all("regression" in s for s in data["scenarios"]), "a scenario lacks its regression snapshot (run_scenarios.py --update)")
    print(f"{len(REGISTRY)} commands, {len(want_tools)} JSON tools, {len(ids)} scenarios")
    ok("scenario-coverage")


def negative_control():
    import scenario_lib as L
    data = L.load()
    sc = next(s for s in data["scenarios"] if s["id"] == "REL-01")
    need(L.evaluate(sc)["ok"], "REL-01 should pass as written")
    bad = copy.deepcopy(sc)
    bad["expect"] = [{"path": "required_area_mm2", "op": "lt", "value": 0}]
    r = L.evaluate(bad)
    need(not r["ok"] and any(c["kind"] == "expect" and not c["ok"] for c in r["checks"]), "a wrong bound must fail")
    bad = copy.deepcopy(sc)
    bad["oracle"] = [{"path": "required_area_mm2", "formula": "12000*2", "rtol": 1e-6}]
    r = L.evaluate(bad)
    need(any(c["kind"] == "oracle" and not c["ok"] for c in r["checks"]), "a wrong oracle must fail")
    bad = copy.deepcopy(sc)
    bad["meta"] = [{"vary": {"flag": "--W", "factor": 2}, "path": "required_area_mm2", "relation": "ratio", "value": 3, "rtol": 1e-6}]
    r = L.evaluate(bad)
    need(any(c["kind"] == "meta" and not c["ok"] for c in r["checks"]), "a wrong metamorphic ratio must fail")
    bad = copy.deepcopy(sc)
    bad["regression"] = {"required_area_mm2": 1.0}
    r = L.evaluate(bad)
    need(any(c["kind"] == "regression" and not c["ok"] for c in r["checks"]), "a drifted snapshot must fail")
    bad = copy.deepcopy(sc)
    bad["args"] = ["relief-gas", "--W", "-5", "--T", "400", "--set-g", "1500", "--M", "44", "--k", "1.13"]
    need(not L.evaluate(bad)["ok"], "a rejected input must fail the scenario")
    # the SI/US comparison itself notices a difference, and the formula evaluator refuses code
    need(L._walk_close({"a": 1.0, "b": [1, 2]}, {"a": 1.0, "b": [1, 3]}), "US comparison must flag a differing value")
    need(not L._walk_close({"a": 1.0}, {"a": 1.0 + 1e-12}), "US comparison must allow rounding noise")
    try:
        L.eval_formula("__import__('os').system('echo x')", {})
    except ValueError:
        pass
    else:
        need(False, "formula evaluator must refuse calls")
    ok("negative-control")


def coverage_map():
    import scenario_lib as L
    from process_safety import standards
    data = L.load()
    topics = set(standards.TOPICS)
    mapped = {t for s in data["scenarios"] for t in s["topics"]}
    gaps = set(data["gaps"])
    need(mapped <= topics, f"scenario topics not in the coverage map: {mapped - topics}")
    need(gaps <= topics, f"gap topics not in the coverage map: {gaps - topics}")
    need(not (mapped & gaps), f"topics both mapped and listed as gaps: {mapped & gaps}")
    need(mapped | gaps == topics, f"topics with neither a scenario nor a stated gap: {sorted(topics - mapped - gaps)}")
    not_impl = {t for t, (_, _, st) in standards.TOPICS.items() if st.startswith("not implemented")}
    need(gaps == not_impl, f"gaps {sorted(gaps ^ not_impl)} differ from the topics whose status says not implemented")
    need(all(len(w) >= 40 for w in data["gaps"].values()), "a gap lacks a stated reason")
    print(f"{len(topics)} topics: {len(mapped)} with scenarios, {len(gaps)} stated gaps")
    ok("coverage-map")


def report_sync():
    import scenario_lib as L
    import run_scenarios as R
    data = L.load()
    results = L.run_all(data)
    text = R.report(data, results)
    path = os.path.join(ROOT, "docs", "SCENARIO_REPORT.md")
    need(os.path.exists(path) and open(path, encoding="utf-8").read() == text, "docs/SCENARIO_REPORT.md is stale: python scripts/run_scenarios.py --write")
    for col in ("| Id |", "| Topic |", "| expect |", "| oracle |", "| meta |", "| si_us |", "| regression |", "| Verdict |"):
        need(col in text, f"report lacks column {col}")
    need(all(f"| {s['id']} |" in text for s in data["scenarios"]), "report lacks a scenario")
    need("### Gaps" in text and f"{len(results)} of {len(results)} scenarios pass" in text, "report summary wrong")
    ok("report-sync")


def full_suite():
    r = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], capture_output=True, text=True, cwd=ROOT)
    m = re.search(r"Ran (\d+) tests", r.stderr)
    need(r.returncode == 0 and m, r.stderr[-800:])
    need(int(m.group(1)) >= 342 + 5, f"only {m.group(1)} tests")
    print(f"{m.group(1)} tests OK")
    ok("full-suite")


def _ruff():
    import shutil
    import tempfile
    exe = shutil.which("ruff")
    if exe:
        return [exe]
    venv = os.path.join(tempfile.gettempdir(), "ps_ruff_venv")
    py = os.path.join(venv, "bin", "python")
    if not os.path.exists(py):
        subprocess.run([sys.executable, "-m", "venv", venv], check=True, capture_output=True)
        subprocess.run([py, "-m", "pip", "install", "-q", "ruff"], check=True, capture_output=True)
    return [py, "-m", "ruff"]


def lint_stdlib():
    r = subprocess.run(_ruff() + ["check", "--select", "E9,F63,F7,F82,F401,F811,F841", "--target-version", "py310", "process_safety", "tests", "scripts"],
                       capture_output=True, text=True, cwd=ROOT)
    need(r.returncode == 0, r.stdout[-1500:] + r.stderr[-300:])
    std = set(sys.stdlib_module_names)

    def third_party(src):
        out = set()
        for node in ast.walk(ast.parse(src)):
            if isinstance(node, ast.Import):
                out |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                out.add(node.module.split(".")[0])
        return {m for m in out if m not in std and m != "process_safety"}
    new = set()
    for dp, _, fs in os.walk(os.path.join(ROOT, "process_safety")):
        for f in fs:
            if f.endswith(".py"):
                path = os.path.join(dp, f)
                new |= third_party(open(path, encoding="utf-8").read())
    old = set()
    ls = subprocess.run(["git", "ls-tree", "-r", "--name-only", "HEAD", "process_safety"], capture_output=True, text=True, cwd=ROOT).stdout.split()
    for path in ls:
        if path.endswith(".py"):
            old |= third_party(subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, text=True, cwd=ROOT).stdout)
    need(new <= old, f"new third-party imports: {sorted(new - old)}")
    ok("lint-stdlib")


def docs_updated():
    ch = open(os.path.join(ROOT, "CHANGELOG.md"), encoding="utf-8").read()
    head = ch[:6000]
    for phrase in ("--units us", "template", "convert", "egress", "illumination", "scenario", "rejected"):
        need(phrase.lower() in head.lower(), f"CHANGELOG top lacks '{phrase}'")
    rd = open(os.path.join(ROOT, "README.md"), encoding="utf-8").read()
    for phrase in ("--units", "UNITS.md", "SCENARIO_REPORT.md", "INPUT_TEMPLATES.md", "egress", "illumination"):
        need(phrase in rd, f"README lacks '{phrase}'")
    ct = open(os.path.join(ROOT, "CONTRIBUTING.md"), encoding="utf-8").read()
    for phrase in ("run_scenarios.py", "gen_input_templates.py", "UNITS.md"):
        need(phrase in ct, f"CONTRIBUTING lacks '{phrase}'")
    ok("docs-updated")


CHECKS = {k.replace("_", "-"): v for k, v in globals().items() if callable(v) and k in (
    "units_exact", "gauge_absolute", "all_args_dimensioned", "si_us_equivalence", "templates_run", "templates_sync", "units_doc",
    "metamorphic_count", "scenario_coverage", "negative_control", "coverage_map", "report_sync", "full_suite", "lint_stdlib", "docs_updated")}

if __name__ == "__main__":
    names = sys.argv[1:]
    if not names:
        print("checks: " + ", ".join(CHECKS))
        sys.exit(0)
    for n in names:
        need(n in CHECKS, f"unknown check {n}")
        CHECKS[n]()

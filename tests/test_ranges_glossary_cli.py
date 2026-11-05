import io
import json
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout

from process_safety import glossary, ranges
from process_safety.__main__ import main
from process_safety.cli.registry import REGISTRY

ROOT = os.path.dirname(os.path.dirname(__file__))


def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            rc = main(list(args))
        except SystemExit as e:
            rc = e.code
    return rc, out.getvalue(), err.getvalue()


class Ranges(unittest.TestCase):
    def test_hard_violation_raises(self):
        for name, v in (("temperature_K", -5), ("heat_capacity_ratio", 1.0), ("beta_factor", 1.2), ("pfd", 0), ("exposure_hours", 25)):
            with self.assertRaises(ranges.RangeError, msg=name):
                ranges.check(name, v)

    def test_boundaries(self):
        self.assertEqual(ranges.check("fraction_0_1", 0), [])          # closed
        self.assertEqual(ranges.check("fraction_0_1", 1), [])
        with self.assertRaises(ranges.RangeError):
            ranges.check("pressure_abs_kPa", 0)                         # open at 0
        self.assertEqual(ranges.check("pfd", 1), [])                    # (0, 1]

    def test_soft_warning_only(self):
        w = ranges.check("heat_capacity_ratio", 2.5)
        self.assertEqual(len(w), 1)
        self.assertIn("typical range", w[0])
        self.assertEqual(ranges.check("heat_capacity_ratio", 1.3), [])

    def test_not_a_number(self):
        with self.assertRaises(ranges.RangeError):
            ranges.check("temperature_K", "abc")

    def test_every_soft_range_inside_hard_range(self):
        for r in ranges.RANGES.values():
            for v in (r.soft_min, r.soft_max):
                if v is not None and v not in (float("inf"), float("-inf")):
                    self.assertFalse(r.violates_hard(v), f"{r.name}: soft bound {v} is outside the hard range")

    def test_decorator(self):
        @ranges.validated(T="temperature_K")
        def f(T):
            return T
        self.assertEqual(f(300), 300)
        with self.assertRaises(ranges.RangeError):
            f(-1)
        with self.assertRaises(KeyError):
            ranges.validated(x="no_such_range")

    def test_library_functions_enforce_hard_ranges(self):
        from process_safety import relief, sil
        with self.assertRaises(ranges.RangeError):
            relief.gas_area(1000, -10, 1200, 101.3, 30, 1.3)
        with self.assertRaises(ranges.RangeError):
            sil.pfd_avg("1oo2", 1e-6, 8760, beta=1.5)

    def test_every_cli_range_name_exists(self):
        for c in REGISTRY.values():
            for dest, rname in c.ranges.items():
                ranges.get(rname)

    def test_docs_in_sync(self):
        with open(os.path.join(ROOT, "docs", "RANGES.md"), encoding="utf-8") as fh:
            self.assertIn(ranges.markdown_table(), fh.read(), "docs/RANGES.md is stale: python -m process_safety ranges --markdown")


class Glossary(unittest.TestCase):
    def test_search(self):
        self.assertEqual(glossary.search("bleve")[0]["term"], "BLEVE")
        self.assertTrue(glossary.search("safety integrity"))
        self.assertEqual(glossary.search("zzzz-not-a-term"), [])

    def test_entries_complete_and_unique(self):
        es = glossary.entries()
        self.assertGreaterEqual(len(es), 100)
        terms = [e["term"] for e in es]
        self.assertEqual(len(terms), len(set(terms)))
        for e in es:
            self.assertTrue(e["definition"].strip() and e["applies_to"].strip(), e["term"])

    def test_docs_in_sync(self):
        with open(os.path.join(ROOT, "docs", "GLOSSARY.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), glossary.markdown(), "docs/GLOSSARY.md is stale: python -m process_safety glossary --markdown")


class Cli(unittest.TestCase):
    GOOD = ["relief-gas", "--W", "5000", "--T", "300", "--set-g", "1000", "--M", "30", "--k", "1.3"]

    def test_hard_range_exits_2(self):
        args = list(self.GOOD)
        args[args.index("--T") + 1] = "-5"
        rc, out, err = run(*args)
        self.assertEqual(rc, 2)
        self.assertIn("possible range", err)
        self.assertEqual(out, "")

    def test_soft_range_warns_but_runs(self):
        args = list(self.GOOD)
        args[args.index("--k") + 1] = "2.5"
        rc, out, err = run(*args)
        self.assertEqual(rc, 0)
        self.assertIn("warning:", err)
        self.assertIn("required_area_mm2", out)

    def test_clean_input_is_silent(self):
        rc, out, err = run(*self.GOOD)
        self.assertEqual((rc, err), (0, ""))

    def test_no_range_check_flag_skips_warning(self):
        args = list(self.GOOD)
        args[args.index("--k") + 1] = "2.5"
        rc, out, err = run("--no-range-check", *args)
        self.assertEqual((rc, err), (0, ""))

    def test_registry_covers_all_original_commands(self):
        original = ("relief-gas relief-steam relief-liquid relief-fire tank-normal tank-fire vapour-fire plume blowdown hazop-csv pool-fire depressure "
                    "steel-fire psm-check psm-due seveso pipeline rmp-check rmp-worst lng lpg h2o2 arc-flash idmt noise safeguard earthing datacentre "
                    "flare lopa pfd fireball qra tool coverage").split()
        self.assertEqual([c for c in original if c not in REGISTRY], [])

    def test_glossary_and_ranges_commands(self):
        rc, out, _ = run("glossary", "LOPA")
        self.assertEqual(rc, 0)
        self.assertIn("Layer of protection analysis", out)
        self.assertEqual(run("glossary", "zzzz-nothing")[0], 1)
        rc, out, _ = run("ranges", "beta_factor")
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(out)["name"], "beta_factor")
        self.assertEqual(run("ranges", "nonsense")[0], 2)

    def test_golden_outputs_unchanged_by_refactor(self):
        with open(os.path.join(ROOT, "tests", "golden", "cli_golden.json"), encoding="utf-8") as fh:
            golden = json.load(fh)
        for case in golden:
            r = subprocess.run([sys.executable, "-m", "process_safety", *case["args"]], capture_output=True, text=True, cwd=ROOT)
            self.assertEqual((r.returncode, r.stdout), (case["rc"], case["stdout"]), f"changed: {case['args']}")


if __name__ == "__main__":
    unittest.main()

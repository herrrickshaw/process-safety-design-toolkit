"""Run the CLI inside the test process.

The golden test starts `python -m process_safety` as a subprocess, so coverage cannot see the command code it runs. These tests call
`main()` directly: every golden case must give the same exit code and the same output. The shipped input templates are blank forms, so running
one unfilled must either succeed or be refused with exit 2 and a message, never end in a traceback.
"""
import contextlib
import glob
import io
import json
import os
import unittest

from process_safety import units
from process_safety.__main__ import main

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def call(argv):
    out, err = io.StringIO(), io.StringIO()
    cwd = os.getcwd()
    os.chdir(ROOT)
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                rc = main(list(argv))
            except SystemExit as e:
                rc = e.code if isinstance(e.code, int) else 1
    finally:
        os.chdir(cwd)
        units.set_system("si")
    return rc, out.getvalue(), err.getvalue()


def approx_equal(test, a, b, where):
    if isinstance(a, float) or isinstance(b, float):
        test.assertAlmostEqual(a, b, delta=1e-9 * max(1.0, abs(a), abs(b)), msg=where)
    elif isinstance(a, dict):
        test.assertEqual(sorted(a), sorted(b), where)
        for k in a:
            approx_equal(test, a[k], b[k], f"{where}.{k}")
    elif isinstance(a, list):
        test.assertEqual(len(a), len(b), where)
        for i, (x, y) in enumerate(zip(a, b)):
            approx_equal(test, x, y, f"{where}[{i}]")
    else:
        test.assertEqual(a, b, where)


class GoldenInProcess(unittest.TestCase):
    def test_golden_cases_match_in_process(self):
        with open(os.path.join(ROOT, "tests", "golden", "cli_golden.json"), encoding="utf-8") as fh:
            cases = json.load(fh)
        for case in cases:
            name = " ".join(case["args"])
            with self.subTest(name):
                rc, out, _ = call(case["args"])
                self.assertEqual(rc, case["rc"], name)
                try:
                    want = json.loads(case["stdout"])
                except ValueError:
                    self.assertEqual(out.strip(), case["stdout"].strip(), name)
                else:
                    approx_equal(self, json.loads(out), want, name)


class BlankTemplates(unittest.TestCase):
    def test_every_blank_template_runs_or_is_refused_cleanly(self):
        paths = sorted(glob.glob(os.path.join(ROOT, "templates", "inputs", "*.json")))
        self.assertTrue(paths)
        for path in paths:
            with self.subTest(os.path.basename(path)):
                rc, out, err = call(["run", path])        # an unhandled exception fails the subtest
                self.assertIn(rc, (0, 2), f"{os.path.basename(path)}: {err[-300:]}")
                self.assertTrue((out if rc == 0 else err).strip(), os.path.basename(path))


class TankFireMissingInputs(unittest.TestCase):
    def test_no_area_and_no_shape_is_refused_with_a_message(self):
        for argv in (["tank-fire"], ["tank-fire", "--shape", "sphere"], ["tank-fire", "--D", "5"]):
            with self.subTest(argv):
                rc, _, err = call(argv)
                self.assertEqual(rc, 2)
                self.assertIn("--wetted-area", err)

    def test_either_route_still_works(self):
        for argv in (["tank-fire", "--wetted-area", "50"], ["tank-fire", "--shape", "sphere", "--D", "5"]):
            with self.subTest(argv):
                self.assertEqual(call(argv)[0], 0)


if __name__ == "__main__":
    unittest.main()

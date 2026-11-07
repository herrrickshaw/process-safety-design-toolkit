import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import scenario_lib as L  # noqa: E402
import run_scenarios as R  # noqa: E402


class Scenarios(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = L.load()
        cls.results = L.run_all(cls.data)

    def test_every_scenario_passes(self):
        for r in self.results:
            bad = [f"[{c['kind']}] {c['name']}: {c['detail']}" for c in r["checks"] if not c["ok"]]
            self.assertFalse(bad, f"{r['id']}: " + "; ".join(bad))

    def test_report_in_sync(self):
        with open(R.REPORT, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), R.report(self.data, self.results), "docs/SCENARIO_REPORT.md is stale: python scripts/run_scenarios.py --write")

    def test_wrong_expectations_fail(self):
        sc = next(s for s in self.data["scenarios"] if s["id"] == "REL-01")
        import copy
        bad = copy.deepcopy(sc)
        bad["oracle"] = [{"path": "required_area_mm2", "formula": "1", "rtol": 1e-6}]
        self.assertFalse(L.evaluate(bad)["ok"])

    def test_formula_evaluator_refuses_code(self):
        with self.assertRaises(ValueError):
            L.eval_formula("__import__('os').getcwd()", {})
        self.assertAlmostEqual(L.eval_formula("$a*2+sqrt(9)", {"a": 4}), 11.0)


if __name__ == "__main__":
    unittest.main()

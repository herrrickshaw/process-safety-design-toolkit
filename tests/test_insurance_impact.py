import json
import math
import os
import subprocess
import sys
import unittest

from process_safety import insurance_impact as ii

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "process_safety", "examples", "insurance.json")


def simple(**kw):
    d = {"programme": {"deductible": 10e6, "limit": 1000e6}, "pricing": {"expense_ratio": 0.2, "risk_load_k": 0.5},
         "scenarios": [{"name": "s", "freq_per_yr": 0.01, "pd_loss": 100e6}]}
    d.update(kw)
    return d


class Maths(unittest.TestCase):
    def test_hand_calculation(self):
        # layer loss 90M, EL = 0.9M, Var = 0.01 x 90^2 = 81 M^2 -> SD 9M; premium = (0.9 + 0.5 x 9) / 0.8 = 6.75M
        r = ii.evaluate(simple())["cases"][0]
        self.assertAlmostEqual(r["layer_expected_loss"], 0.9e6, delta=1)
        self.assertAlmostEqual(r["layer_sd"], 9e6, delta=1)
        self.assertAlmostEqual(r["technical_premium"], 6.75e6, delta=1)
        self.assertAlmostEqual(r["retained_expected_loss"], 0.1e6, delta=1)           # 0.01 x 10M deductible

    def test_limit_caps_the_layer_and_the_excess_is_retained(self):
        r = ii.evaluate(simple(programme={"deductible": 10e6, "limit": 50e6}))["cases"][0]
        self.assertAlmostEqual(r["layer_expected_loss"], 0.5e6, delta=1)
        self.assertAlmostEqual(r["retained_expected_loss"], 0.5e6, delta=1)            # 10M below + 40M above the limit, x 0.01

    def test_uncertainty_factor(self):
        self.assertEqual(ii.lognormal_mean_factor(1), 1.0)
        sigma = math.log(3) / 1.645
        self.assertAlmostEqual(ii.lognormal_mean_factor(3), math.exp(sigma ** 2 / 2), places=12)
        self.assertGreater(ii.lognormal_mean_factor(10), ii.lognormal_mean_factor(3))
        with self.assertRaises(ValueError):
            ii.lognormal_mean_factor(0.5)

    def test_narrower_error_factor_lowers_premium(self):
        r = ii.evaluate(simple(cases=["a", "b"], error_factor={"a": 10, "b": 3}))["cases"]
        self.assertLess(r[1]["technical_premium"], r[0]["technical_premium"])
        self.assertLess(r[1]["premium_change_pct"], 0)

    def test_pfd_scales_frequency(self):
        inp = simple(cases=["base", "der"], scenarios=[{"name": "s", "freq_per_yr": 0.01, "pd_loss": 100e6, "pfd": {"base": 0.01, "der": 0.1}}])
        r = ii.evaluate(inp)["cases"]
        self.assertAlmostEqual(r[1]["scenario_frequencies"]["s"], 0.1)
        self.assertAlmostEqual(r[1]["layer_expected_loss"], 10 * r[0]["layer_expected_loss"], delta=1)

    def test_loss_factor_and_business_interruption(self):
        inp = simple(value_per_day=1e6, cases=["base", "der"],
                     scenarios=[{"name": "s", "freq_per_yr": 0.01, "pd_loss": 50e6, "bi_days": 50, "loss_factor": {"der": 1.2}}])
        r = ii.evaluate(inp)["cases"]
        self.assertAlmostEqual(r[0]["ground_up_expected_loss"], 0.01 * 100e6, delta=1)
        self.assertAlmostEqual(r[1]["ground_up_expected_loss"], 0.01 * 120e6, delta=1)

    def test_pv_comparison_and_net_value(self):
        with open(EX, encoding="utf-8") as fh:
            r = ii.evaluate(json.load(fh))
        cm = r["compensating_measures"]
        self.assertAlmostEqual(cm["annuity_factor"], sum(1.08 ** -t for t in range(1, 11)))
        self.assertAlmostEqual(cm["net_value"], cm["pv_total_saving"] - 2.5e6, delta=1)
        prem = [c["technical_premium"] for c in r["cases"]]
        self.assertTrue(prem[0] < prem[2] < prem[1])           # derogation costs more; compensation recovers part of it

    def test_credibility(self):
        self.assertEqual(ii.credibility(0), 0.0)
        self.assertAlmostEqual(ii.credibility(10, 10), 0.5)
        self.assertAlmostEqual(ii.blended_premium(2.0, 4.0, 10, 10), 3.0)
        with self.assertRaises(ValueError):
            ii.credibility(-1)

    def test_bad_inputs(self):
        for bad in ({}, simple(scenarios=[]), simple(pricing={"expense_ratio": 0.95, "risk_load_k": 0}),
                    simple(programme={"deductible": 0, "limit": 0}),
                    simple(scenarios=[{"name": "s", "freq_per_yr": -1, "pd_loss": 1}]),
                    simple(scenarios=[{"name": "s"}])):
            with self.assertRaises(ValueError):
                ii.evaluate(bad)


class Cli(unittest.TestCase):
    def test_runs_example(self):
        r = subprocess.run([sys.executable, "-m", "process_safety", "insurance", EX], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(len(json.loads(r.stdout)["cases"]), 3)


class LegalClauses(unittest.TestCase):
    def test_entries_complete_and_search(self):
        from process_safety import legal_clauses as lc
        for c in lc.CLAUSES:
            self.assertIn(c["topic"], lc.TOPICS)
            self.assertIn(c["grade"], ("A", "B"))
            self.assertTrue(c["url"].startswith("https://") and c["requires"] and c["for_derogations"])
        self.assertEqual(len({c["id"] for c in lc.CLAUSES}), len(lc.CLAUSES))
        self.assertTrue(lc.search(region="EU", topic="change"))
        self.assertEqual(lc.search("zzzz"), [])

    def test_doc_in_sync(self):
        from process_safety import legal_clauses as lc
        with open(os.path.join(ROOT, "docs", "LEGAL_CLAUSES.md"), encoding="utf-8") as fh:
            self.assertEqual(fh.read(), lc.markdown() + "\n" if not lc.markdown().endswith("\n") else lc.markdown(),
                             "docs/LEGAL_CLAUSES.md is stale: python -m process_safety legal-clauses --markdown > docs/LEGAL_CLAUSES.md")


if __name__ == "__main__":
    unittest.main()

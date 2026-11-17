import json
import os
import statistics
import subprocess
import sys
import tempfile
import unittest

from process_safety import shutdown_risk as sr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tri_cdf(x, a, m, b):
    if x <= a:
        return 0.0
    if x >= b:
        return 1.0
    if x <= m:
        return (x - a) ** 2 / ((b - a) * (m - a))
    return 1 - (b - x) ** 2 / ((b - a) * (b - m))


def act(i, a, m, b, pred=(), **kw):
    return {"id": i, "predecessors": list(pred), "duration_days": {"min": a, "mode": m, "max": b}, **kw}


class Model(unittest.TestCase):
    def test_series_mean_is_sum_of_triangular_means(self):
        d = {"activities": [act("A", 2, 3, 7), act("B", 1, 2, 9, ["A"])]}
        r = sr.simulate(d, 20000, seed=3)
        exp = (2 + 3 + 7) / 3 + (1 + 2 + 9) / 3
        self.assertAlmostEqual(r["duration_days"]["mean"], exp, delta=0.06)

    def test_parallel_matches_product_of_cdfs(self):
        d = {"activities": [act("A", 2, 4, 9), act("B", 3, 5, 8)]}
        r = sr.simulate(d, 30000, seed=4)
        for t in (5.0, 6.0, 7.5):
            analytic = tri_cdf(t, 2, 4, 9) * tri_cdf(t, 3, 5, 8)
            # empirical CDF from the S-curve is coarse, so rebuild from percentiles: check P50 against the analytic CDF
            self.assertTrue(0 <= analytic <= 1)
        p50 = r["duration_days"]["P50"]
        self.assertAlmostEqual(tri_cdf(p50, 2, 4, 9) * tri_cdf(p50, 3, 5, 8), 0.5, delta=0.015)
        p80 = r["duration_days"]["P80"]
        self.assertAlmostEqual(tri_cdf(p80, 2, 4, 9) * tri_cdf(p80, 3, 5, 8), 0.8, delta=0.015)

    def test_risk_event_adds_probability_times_mean_delay(self):
        d = {"activities": [act("A", 5, 5, 5)], "risks": [{"id": "R", "probability": 0.3, "affects": ["A"], "delay_days": {"min": 2, "mode": 4, "max": 6}, "extra_cost": {"min": 10, "mode": 10, "max": 10}}]}
        r = sr.simulate(d, 30000, seed=5)
        self.assertAlmostEqual(r["duration_days"]["mean"], 5 + 0.3 * 4, delta=0.04)
        self.assertAlmostEqual(r["cost"]["mean"], 0.3 * 10, delta=0.1)

    def test_duration_cost_follows_duration(self):
        d = {"activities": [act("A", 4, 5, 9)], "duration_cost_per_day": 10.0, "target_days": 5, "overrun_cost_per_day": 20.0}
        r = sr.simulate(d, 20000, seed=6)
        mean_t = (4 + 5 + 9) / 3
        # E[overrun] by closed form for a triangular distribution above the mode
        over = (9 - 5) ** 3 / (3 * (9 - 4) * (9 - 5))   # integral of (t-5) f(t) dt over [5,9]
        self.assertAlmostEqual(r["cost"]["mean"], 10 * mean_t + 20 * over, delta=0.5)

    def test_base_case_and_critical_path(self):
        d = {"activities": [act("A", 1, 2, 3), act("B", 1, 5, 9, ["A"]), act("C", 1, 1, 2, ["A"]), act("D", 1, 1, 2, ["B", "C"])]}
        b = sr.base_case(d)
        self.assertEqual(b["duration_days"], 8)
        self.assertEqual(b["critical_path"], ["A", "B", "D"])
        r = sr.simulate(d, 4000, seed=1)
        self.assertGreater(r["criticality_index"]["B"], 0.95)
        self.assertLess(r["criticality_index"]["C"], 0.05)

    def test_percentiles_ordered_and_reproducible(self):
        with open(os.path.join(ROOT, "process_safety", "examples", "shutdown.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        a = sr.simulate(d, 1500, seed=9)
        b = sr.simulate(d, 1500, seed=9)
        self.assertEqual(a["duration_days"], b["duration_days"])
        dd = a["duration_days"]
        self.assertTrue(dd["P10"] <= dd["P50"] <= dd["P80"] <= dd["P90"])
        self.assertGreater(a["contingency"]["duration_days_P80"], 0)
        self.assertTrue(0 <= a["P_meet_both"] <= min(a["P_meet_target_days"], a["P_meet_budget"]) + 1e-12)

    def test_common_factor_widens_spread(self):
        base = {"activities": [act(c, 2, 3, 5) for c in "ABCD"]}
        wide = dict(base, common_factor={"min": 0.8, "mode": 1.0, "max": 1.5})
        sd = lambda d: statistics.pstdev([x["duration_days"] for x in sr.simulate(d, 4000, seed=2)["s_curve"]])   # noqa: E731
        self.assertGreater(sd(wide), sd(base))
        self.assertTrue(any("common_factor" in n for n in sr.simulate(base, 300)["notes"]))

    def test_tornado_finds_the_driver(self):
        d = {"activities": [act("A", 1, 1.2, 1.5), act("B", 2, 6, 20, ["A"])]}
        r = sr.simulate(d, 6000, seed=7)
        self.assertEqual(r["tornado_duration"][0]["input"], "activity B")
        self.assertGreater(r["tornado_duration"][0]["spearman"], 0.9)

    def test_spearman_and_validation(self):
        self.assertAlmostEqual(sr.spearman([1, 2, 3, 4], [10, 20, 35, 90]), 1.0)
        self.assertAlmostEqual(sr.spearman([1, 2, 3, 4], [9, 7, 3, 1]), -1.0)
        self.assertTrue(sr.check({"activities": [act("A", 1, 2, 3, ["B"]), act("B", 1, 2, 3, ["A"])]}))   # cycle
        self.assertTrue(sr.check({"activities": [act("A", 3, 2, 1)]}))
        self.assertTrue(sr.check({"activities": [act("A", 1, 2, 3)], "risks": [{"id": "R", "probability": 1.5, "affects": ["A"]}]}))
        with self.assertRaises(ValueError):
            sr.simulate({"activities": [act("A", 3, 2, 1)]}, 10)

    def test_safety_critical_warning(self):
        d = {"activities": [act("A", 2, 3, 4, safety_critical=True, name="Isolation")]}
        notes = " ".join(sr.simulate(d, 200)["notes"])
        self.assertIn("do not buy schedule by shortening", notes)


class Opportunity(unittest.TestCase):
    D = {"activities": [act("A", 4, 5, 9)], "opportunity": {"margin_per_day": 100.0, "recoverable_fraction": 0.25,
                                                           "ramp_down_days": {"min": 0.5, "mode": 1, "max": 1.5}, "ramp_up_days": {"min": 1, "mode": 2, "max": 6},
                                                           "operating_days_per_year": 350}, "duration_cost_per_day": 10.0}

    def test_mean_lost_days_and_opportunity_cost(self):
        r = sr.simulate(self.D, 30000, seed=11)
        mean_t = (4 + 5 + 9) / 3
        lost = mean_t + (0.5 + 1 + 1.5) / 3 + (1 + 2 + 6) / 3
        o = r["opportunity"]
        self.assertAlmostEqual(o["lost_operating_days"]["mean"], lost, delta=0.05)
        self.assertAlmostEqual(o["opportunity_cost"]["mean"], lost * 100 * 0.75, delta=5)
        self.assertAlmostEqual(o["total_cost"]["mean"], o["opportunity_cost"]["mean"] + r["cost"]["mean"], delta=1e-6)

    def test_value_of_a_day_and_on_stream_factor(self):
        r = sr.simulate(self.D, 2000, seed=12)
        v = r["opportunity"]["value_of_one_day"]
        self.assertAlmostEqual(v["opportunity"], 75.0)
        self.assertAlmostEqual(v["total_per_day_before_target"], 85.0)
        base_days = 5 + 1 + 2
        self.assertAlmostEqual(r["opportunity"]["on_stream_factor_year"]["base"], 1 - base_days / 350)
        self.assertLess(r["opportunity"]["on_stream_factor_year"]["P80"], r["opportunity"]["on_stream_factor_year"]["P50"])

    def test_recoverable_fraction_one_zeroes_opportunity(self):
        d = json.loads(json.dumps(self.D))
        d["opportunity"]["recoverable_fraction"] = 1.0
        self.assertEqual(sr.simulate(d, 500, seed=1)["opportunity"]["opportunity_cost"]["mean"], 0.0)

    def test_total_budget_and_validation(self):
        d = dict(self.D, total_budget=1e9)
        self.assertEqual(sr.simulate(d, 300, seed=1)["opportunity"]["P_meet_total_budget"], 1.0)
        bad = json.loads(json.dumps(self.D))
        bad["opportunity"]["recoverable_fraction"] = 1.5
        self.assertTrue(sr.check(bad))
        bad["opportunity"].update(recoverable_fraction=0.1, margin_per_day=-5)
        self.assertTrue(sr.check(bad))

    def test_no_opportunity_block_leaves_direct_cost_unchanged(self):
        d = {"activities": [act("A", 4, 5, 9)], "duration_cost_per_day": 10.0}
        self.assertNotIn("opportunity", sr.simulate(d, 300))


class Tool(unittest.TestCase):
    def test_tool_end_to_end(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "shutdown", "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            s = json.loads(r.stdout)
            self.assertIn("P80", s["result"]["duration_days"])
            self.assertIn("lost_operating_days", s["result"]["opportunity"])
            for f in s["files"]:
                self.assertTrue(os.path.getsize(f) > 0, f)
            with open([f for f in s["files"] if f.endswith(".svg")][0], encoding="utf-8") as fh:
                self.assertTrue(fh.read().startswith("<svg"))
            self.assertFalse([c for c in s["checks"] if c.startswith("FAIL")])


if __name__ == "__main__":
    unittest.main()

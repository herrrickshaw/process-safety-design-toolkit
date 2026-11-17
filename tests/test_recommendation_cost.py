import json
import os
import statistics
import subprocess
import sys
import tempfile
import unittest

from process_safety import recommendation_cost as rc
from process_safety import shutdown_risk as sr
from process_safety.qra import alarp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def one(lines, **kw):
    return dict({"recommendations": [{"id": "R", "lines": lines}]}, **kw)


class Estimate(unittest.TestCase):
    def test_deterministic_line_and_indirects(self):
        d = one([{"discipline": "piping", "description": "pipe", "qty": 100, "rate": 2.0}],
                indirects={"engineering_pct": 10, "procurement_pct": 5, "escalation_pct": 10})
        e = rc.estimate(d, 200)
        self.assertAlmostEqual(e["indirect_factor"], 1.15 * 1.10)
        r = e["recommendations"][0]
        self.assertAlmostEqual(r["total_mode"], 200 * 1.15 * 1.10)
        self.assertAlmostEqual(r["capex"]["P50"], r["total_mode"])
        self.assertAlmostEqual(r["contingency_P80"], 0.0)

    def test_sampled_mean_is_product_of_means(self):
        q = {"min": 80, "mode": 100, "max": 160}
        rt = {"min": 1.0, "mode": 1.2, "max": 2.0}
        d = one([{"discipline": "civil", "description": "x", "qty": q, "rate": rt}], distribution="triangular")
        e = rc.estimate(d, 40000, seed=3)
        expect = (80 + 100 + 160) / 3 * (1.0 + 1.2 + 2.0) / 3
        self.assertAlmostEqual(e["recommendations"][0]["capex"]["mean"], expect, delta=0.01 * expect)
        d["distribution"] = "pert"
        e = rc.estimate(d, 40000, seed=3)
        expect = (80 + 400 + 160) / 6 * (1.0 + 4.8 + 2.0) / 6
        self.assertAlmostEqual(e["recommendations"][0]["capex"]["mean"], expect, delta=0.01 * expect)

    def test_discipline_split_and_rate_book(self):
        d = {"rate_book": {"c": {"unit": "m3", "rate": 3.0}},
             "recommendations": [{"id": "R", "lines": [{"discipline": "civil", "description": "a", "qty": 10, "rate_key": "c"},
                                                      {"discipline": "electrical", "description": "b", "qty": 4, "rate": 5.0}]}]}
        e = rc.estimate(d, 100)
        r = e["recommendations"][0]
        self.assertEqual(r["direct_by_discipline_mode"], {"civil": 30.0, "electrical": 20.0})
        self.assertAlmostEqual(sum(r["direct_by_discipline_mode"].values()), r["direct_mode"])
        self.assertEqual(e["portfolio"]["direct_by_discipline_mode"], {"civil": 30.0, "electrical": 20.0})

    def test_shared_rate_factor_widens_portfolio_spread(self):
        lines = [{"discipline": "piping", "description": str(i), "qty": 10, "rate": {"min": 0.9, "mode": 1.0, "max": 1.2}} for i in range(8)]
        no = rc.estimate(one(lines), 6000, seed=2)["portfolio"]["capex"]
        yes = rc.estimate(one(lines, rate_factor={"min": 0.9, "mode": 1.0, "max": 1.4}), 6000, seed=2)["portfolio"]["capex"]
        self.assertGreater(yes["P90"] - yes["P10"], no["P90"] - no["P10"])

    def test_cba_matches_alarp_module(self):
        d = one([{"discipline": "piping", "description": "p", "qty": 100, "rate": 10.0}], alarp={"vpf": 5000, "disproportion_factor": 3, "lifetime_yr": 20, "discount_rate": 0.03})
        d["recommendations"][0].update(pll_before=0.001, pll_after=0.0004, opex_pct_of_capex=2.0)
        r = rc.estimate(d, 100)["recommendations"][0]
        ref = alarp.cost_benefit(0.0006, 1000.0, 20.0, 5000, 20, 3, 0.03)
        self.assertAlmostEqual(r["cba"]["cost_benefit_ratio"], ref["cost_benefit_ratio"])
        self.assertEqual(r["cba"]["decision"], ref["decision"])

    def test_validation(self):
        bad = one([{"discipline": "plumbing", "description": "x", "qty": 1, "rate": 1}])
        self.assertTrue(rc.check(bad))
        self.assertTrue(rc.check(one([{"discipline": "civil", "description": "x", "qty": 1, "rate_key": "missing"}])))
        d = one([{"discipline": "civil", "description": "x", "qty": 1, "rate": 1}])
        d["recommendations"][0].update(pll_before=0.001, pll_after=0.002)
        self.assertTrue(rc.check(d))
        d["recommendations"][0].update(pll_after=0.0, requires_shutdown=True)
        self.assertTrue(rc.check(d))   # shutdown without duration
        with self.assertRaises(ValueError):
            rc.estimate(bad)

    def test_notes_flag_missing_indirects_and_rate_factor(self):
        n = " ".join(rc.estimate(one([{"discipline": "civil", "description": "x", "qty": 1, "rate": 1}]), 50)["notes"])
        self.assertIn("direct cost only", n)
        self.assertIn("rate_factor", n)


class Merge(unittest.TestCase):
    SD = {"activities": [{"id": "A", "duration_days": {"min": 2, "mode": 2, "max": 2}},
                         {"id": "B", "predecessors": ["A"], "duration_days": {"min": 3, "mode": 3, "max": 3}},
                         {"id": "C", "predecessors": ["B"], "duration_days": {"min": 1, "mode": 1, "max": 1}}]}

    def est(self):
        d = {"recommendations": [{"id": "M1", "title": "mod", "requires_shutdown": True, "work_duration_days": {"min": 4, "mode": 4, "max": 4},
                                  "lines": [{"discipline": "piping", "description": "p", "qty": 10, "rate": 5.0}]},
                                 {"id": "M2", "title": "online", "lines": [{"discipline": "civil", "description": "c", "qty": 1, "rate": 9.0}]}]}
        return rc.estimate(d, 200)

    def test_merge_adds_only_shutdown_items_and_rewires(self):
        m = rc.merge_into_shutdown(self.SD, self.est(), ["A"], ["C"])
        ids = [a["id"] for a in m["activities"]]
        self.assertIn("MOD-M1", ids)
        self.assertNotIn("MOD-M2", ids)
        c = next(a for a in m["activities"] if a["id"] == "C")
        self.assertIn("MOD-M1", c["predecessors"])
        self.assertEqual(sr.check(m), [])
        self.assertEqual(len(self.SD["activities"]), 3)   # original untouched

    def test_modification_on_critical_path_extends_duration_and_cost(self):
        m = rc.merge_into_shutdown(self.SD, self.est(), ["A"], ["C"])
        base = sr.base_case(self.SD)
        merged = sr.base_case(m)
        self.assertEqual(base["duration_days"], 6)
        self.assertEqual(merged["duration_days"], 7)      # A(2) -> MOD(4) -> C(1) = 7 beats A -> B(3) -> C
        r = sr.simulate(m, 300, seed=1)
        self.assertAlmostEqual(r["cost"]["mean"], 50.0, delta=1.0)   # the modification's capex (10 x 5, no indirects)


class Tool(unittest.TestCase):
    def test_tool_end_to_end(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "recs", "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            s = json.loads(r.stdout)
            self.assertIn("shutdown_effect", s)
            self.assertGreater(s["shutdown_effect"]["delta_direct_cost"]["P50"], 0)
            for f in s["files"]:
                self.assertTrue(os.path.getsize(f) > 0, f)
            pc = s["estimate"]["portfolio"]
            self.assertLess(pc["capex"]["P10"], pc["capex"]["P80"])
            self.assertAlmostEqual(pc["shutdown_work_total_mode"] + pc["online_work_total_mode"], pc["total_mode"])
            self.assertTrue(statistics.fmean([r["total_mode"] for r in s["recommendations"]]) > 0)


if __name__ == "__main__":
    unittest.main()

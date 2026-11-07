import json
import os
import subprocess
import sys
import tempfile
import unittest

from process_safety import lng_cost as lc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A1 = {"id": "t1", "project": "Test 1", "country": "X", "location_code": "AAA", "site_type": "brownfield", "trains": 1, "capacity_mtpa": 4.0, "train_size_mtpa": 4.0,
      "fid_year": 2016, "cost_year": 2016, "plant_only_musd": 4000.0, "headline_musd": 4000.0, "scope": "plant_only", "cost_basis": "budget",
      "split_source": "", "contingency_status": "budget", "grade": "A", "source_url": "https://example.com"}


class SyntheticAnalog(unittest.TestCase):
    def setUp(self):
        self._saved = lc._CACHE
        lc._CACHE = {"analogs": [dict(A1)], "compiled": "t", "source": "t", "license": "t", "note": "t"}

    def tearDown(self):
        lc._CACHE = self._saved

    CFG = {"capacity_mtpa": 8.0, "trains": 1, "site_type": "greenfield", "target_year": 2021, "location_code": "BBB",
           "escalation_pct_per_year": 4.0, "location_factors": {"AAA": 1.0, "BBB": 1.5}, "size_band": (0.5, 3.0)}

    def test_every_factor_by_hand(self):
        a = lc.adjust(self.CFG)["kept"][0]
        unit0 = 4000.0 / 4.0
        self.assertAlmostEqual(a["unit_musd_per_mtpa_published"], unit0)
        self.assertAlmostEqual(a["escalation"], 1.04 ** 5)
        self.assertAlmostEqual(a["location"], 1.5)
        self.assertAlmostEqual(a["site_type"], 1.50)             # brownfield analog to greenfield target
        self.assertAlmostEqual(a["size_scaling"], 2.0 ** -0.3)   # target train twice the analog, n = 0.7
        self.assertAlmostEqual(a["unit_musd_per_mtpa_adjusted"], unit0 * 1.04 ** 5 * 1.5 * 1.5 * 2.0 ** -0.3)
        self.assertAlmostEqual(a["total_musd"], a["unit_musd_per_mtpa_adjusted"] * 8.0)

    def test_cost_index_replaces_rate(self):
        cfg = {k: v for k, v in self.CFG.items() if k != "escalation_pct_per_year"} | {"cost_index": {"2016": 100, "2021": 130}}
        self.assertAlmostEqual(lc.adjust(cfg)["kept"][0]["escalation"], 1.3)
        with self.assertRaises(ValueError):
            lc.adjust({**cfg, "cost_index": {"2016": 100}})

    def test_collapsed_ranges_give_the_deterministic_value(self):
        cfg = dict(self.CFG, escalation_pct_per_year=4.0, exponent_range=(0.7, 0.7), definition_growth={"min": 0, "mode": 0, "max": 0})
        r = lc.estimate(cfg, 300)
        for p in ("P10", "P50", "P90"):
            self.assertAlmostEqual(r["total_musd"][p], r["central"]["median_total_musd"], delta=1e-6 * r["central"]["median_total_musd"])

    def test_size_exponent_changes_result_in_the_right_direction(self):
        lo = lc.adjust(dict(self.CFG, exponent=0.6))["median_unit"]
        hi = lc.adjust(dict(self.CFG, exponent=0.8))["median_unit"]
        self.assertLess(lo, hi)     # larger target train than the analog: higher exponent means less saving

    def test_exclusions_carry_reasons(self):
        other = dict(A1, id="t2", location_code="CCC", train_size_mtpa=40.0, capacity_mtpa=40.0)
        lc._CACHE = {"analogs": [dict(A1), other], "compiled": "t", "source": "t", "license": "t", "note": "t"}
        r = lc.adjust(dict(self.CFG, location_factors={"AAA": 1.0, "BBB": 1.5, "CCC": 1.0}))
        self.assertEqual([k["id"] for k in r["kept"]], ["t1"])
        self.assertEqual(r["excluded"][0]["id"], "t2")
        self.assertIn("train size", r["excluded"][0]["reason"])
        r2 = lc.adjust(dict(self.CFG))        # no factor for CCC -> reason names the missing location
        self.assertEqual(r2["excluded"][0]["reason"], "no location factor for CCC")

    def test_no_analogs_left_is_an_error(self):
        with self.assertRaises(ValueError) as cm:
            lc.adjust(dict(self.CFG, capacity_mtpa=40.0))      # target train 40 vs analog 4 = 10x, outside the band
        self.assertIn("no analogs left", str(cm.exception))

    def test_missing_inputs_are_errors(self):
        self.assertTrue(lc.check({"capacity_mtpa": 5, "trains": 1, "site_type": "greenfield", "target_year": 2026, "location_code": "X"}))
        bad = dict(self.CFG)
        del bad["escalation_pct_per_year"]
        self.assertTrue(any("no cost index" in e for e in lc.check(bad)))
        self.assertTrue(any("location_factors" in e for e in lc.check({**self.CFG, "location_factors": {"AAA": 1.0}})))


class Data(unittest.TestCase):
    def test_bundled_analogs(self):
        a = lc.analogs()
        self.assertGreaterEqual(len(a), 20)
        for r in a:
            self.assertGreater(r["plant_only_musd"], 0)
            self.assertTrue(r["source_url"].startswith("http"))
            self.assertIn(r["grade"], ("A", "B", "C"))
            self.assertGreater(r["train_size_mtpa"], 0)
        self.assertIn("MIT", lc.data()["license"])

    def test_published_unit_costs_known_rows(self):
        by = {r["id"]: r for r in lc.analogs()}
        self.assertAlmostEqual(by["ichthys"]["plant_only_musd"] / by["ichthys"]["capacity_mtpa"], 16200 / 8.4)
        au = [r["plant_only_musd"] / r["capacity_mtpa"] for r in lc.analogs() if r["country"] == "Australia"]
        self.assertTrue(all(u > 1000 for u in au))     # every published Australian plant-only unit cost exceeds 1,000 $M/MTPA

    def test_helpers(self):
        self.assertAlmostEqual(lc.daily_margin(5.0, 2.0, 52, 350), 5e6 / 350 * 52 * 2.0 / 1e6)
        self.assertAlmostEqual(lc.safety_spend_ratio(65, 11000), 65 / 11000)
        with self.assertRaises(ValueError):
            lc.daily_margin(5.0, 2.0, 0, 350)


class Tool(unittest.TestCase):
    def test_tool_end_to_end(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "lngcost", "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            s = json.loads(r.stdout)
            t = s["result"]["total_musd"]
            self.assertTrue(t["P10"] < t["P50"] < t["P80"] < t["P90"])
            self.assertIn("compare", s["result"])
            self.assertTrue(os.path.getsize(s["files"][0]) > 0)
            bad = subprocess.run([sys.executable, "-m", "process_safety", "tool", "lngcost", os.path.join(ROOT, "tests", "golden", "cli_golden.json"), "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()

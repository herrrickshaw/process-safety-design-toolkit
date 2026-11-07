"""Optional: needs `pip install openpytea`. Checks scripts/openpytea_bridge.py against an independent re-derivation of the Turton
correlation and the CEPCI escalation, and that a bridged rate book runs through `tool recs`."""
import importlib.util
import json
import math
import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts"))


@unittest.skipUnless(importlib.util.find_spec("openpytea"), "needs: pip install openpytea")
class Bridge(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import openpytea_bridge as B
        cls.B = B

    def item(self, size, unit="m3", **kw):
        d = {"key": "k", "name": "V", "category": "Pressure vessels", "type": "Horizontal", "process_type": "Fluids", "size": size, "size_unit": unit}
        d.update(kw)
        return d

    def test_turton_quadratic_and_cepci_rederived(self):
        # Turton et al. (2018) Table A.1 horizontal vessel, K1..K3 read from the correlation row, cost year 2001, CEPCI 394.3 -> 800 (2024)
        r = self.B.cost_item(self.item(12.5), 2024)
        x = math.log10(12.5)
        cp_2001 = 10 ** (3.5565 + 0.3776 * x + 0.0905 * x * x)
        self.assertAlmostEqual(r["purchased_usd"], cp_2001 * 800 / 394.3, delta=r["purchased_usd"] * 2e-4)

    def test_unit_conversion_to_native(self):
        self.assertAlmostEqual(self.B.to_native(1.0, "m3", "volume, ft^3"), 1 / 0.3048 ** 3, places=9)
        self.assertAlmostEqual(self.B.to_native(100.0, "kW", "shaft power, kW"), 100.0)
        self.assertAlmostEqual(self.B.to_native(1.0, "kW", "driver power, hp"), 1000 / (550 * 0.3048 * 0.45359237 * 9.80665), places=9)
        with self.assertRaises(ValueError):
            self.B.to_native(1.0, "m3", "flow capacity, gpm x sqrt[head, ft]")

    def test_same_size_in_us_units_gives_same_cost(self):
        a = self.B.cost_item(self.item(12.5, "m3"), 2024)["purchased_usd"]
        b = self.B.cost_item(self.item(12.5 / 0.3048 ** 3, "ft3"), 2024)["purchased_usd"]
        self.assertAlmostEqual(a, b, delta=a * 1e-9)

    def test_economies_of_scale_and_units(self):
        one = self.B.cost_item(self.item(10), 2024)["purchased_usd"]
        two = self.B.cost_item(self.item(20), 2024)["purchased_usd"]
        self.assertTrue(one < two < 2 * one)
        n2 = self.B.cost_item(self.item(10, num_units=2), 2024)["purchased_usd"]
        self.assertAlmostEqual(n2, 2 * one, delta=one * 1e-9)

    def test_out_of_range_is_flagged(self):
        self.assertTrue(self.B.cost_item(self.item(10), 2024)["in_range"])
        self.assertFalse(self.B.cost_item(self.item(5000), 2024)["in_range"])

    def test_spread_is_required_and_checked(self):
        spec = {"target_year": 2024, "currency": "kUSD", "currency_per_usd": 0.001, "items": [self.item(10)]}
        with self.assertRaises(ValueError):
            self.B.build(spec)
        spec["spread"] = {"min": 1.2, "max": 1.5}
        with self.assertRaises(ValueError):
            self.B.build(spec)

    def test_rate_book_runs_through_tool_recs(self):
        with open(os.path.join(ROOT, "templates", "openpytea_equipment.example.json"), encoding="utf-8") as fh:
            spec = json.load(fh)
        res = self.B.build(spec)
        with open(os.path.join(ROOT, "process_safety", "examples", "recs.json"), encoding="utf-8") as fh:
            study = json.load(fh)
        study["rate_book"].update(res["rate_book"])
        study["recommendations"][0]["lines"].append({"discipline": "mechanical", "description": "new KO drum", "rate_key": "eq_flare_ko_drum",
                                                     "qty": {"min": 1, "mode": 1, "max": 1}})
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "study.json")
            with open(path, "w") as fh:
                json.dump(study, fh)
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "recs", path, "--quiet"], capture_output=True, text=True, cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stderr[-500:])
        self.assertNotIn("FAIL", json.dumps(json.loads(r.stdout)["checks"]))


if __name__ == "__main__":
    unittest.main()

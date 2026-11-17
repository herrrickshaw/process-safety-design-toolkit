import json
import math
import os
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from process_safety import templating, units  # noqa: E402


def cli(*args):
    r = subprocess.run([sys.executable, "-m", "process_safety", *args], capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout, r.stderr


class Factors(unittest.TestCase):
    def test_definitions(self):
        self.assertAlmostEqual(units.convert(1, "ft", "m"), 0.3048, places=15)
        self.assertAlmostEqual(units.convert(1, "lb", "kg"), 0.45359237, places=15)
        # lbf = lb x standard gravity; psi = lbf/in2
        self.assertTrue(math.isclose(units.convert(1, "psi", "Pa"), 0.45359237 * 9.80665 / 0.0254 ** 2, rel_tol=1e-14))
        self.assertTrue(math.isclose(units.convert(1, "gal", "m3"), 231 * 0.0254 ** 3, rel_tol=1e-14))

    def test_temperature_reading_versus_difference(self):
        self.assertAlmostEqual(units.convert(212, "degF", "degC"), 100.0, places=9)
        self.assertAlmostEqual(units.convert(-40, "degF", "degC"), -40.0, places=9)
        self.assertAlmostEqual(units.convert(100, "dF", "dK"), 100 * 5 / 9, places=12)
        self.assertNotAlmostEqual(units.convert(100, "dF", "dK"), units.convert(100, "degF", "K"), places=3)

    def test_gauge_and_absolute_are_not_interchangeable(self):
        with self.assertRaises(units.UnitError):
            units.convert(10, "psig", "psia")
        self.assertAlmostEqual(units.gauge_to_abs(0, "kPag", "kPa abs"), 101.325, places=12)
        self.assertAlmostEqual(units.abs_to_gauge(units.gauge_to_abs(7, "psig", "psia"), "psia", "psig"), 7, places=9)

    def test_dimension_mismatch_and_unknown_unit(self):
        with self.assertRaises(units.UnitError):
            units.convert(1, "m", "kg")
        with self.assertRaises(units.UnitError):
            units.convert(1, "furlong", "m")

    def test_lb_per_lbmol_equals_kg_per_kmol(self):
        self.assertEqual(units.convert(44, "lb/lbmol", "kg/kmol"), 44)

    def test_parse_quantity(self):
        self.assertAlmostEqual(units.parse_quantity("150 psig", "kPag"), 1034.2135939752, places=6)
        self.assertEqual(units.parse_quantity("42", "kPag"), 42.0)

    def test_every_us_target_exists_with_matching_dimension(self):
        for si, us in units.US_FOR.items():
            self.assertEqual(units.UNITS[si].dimension, units.UNITS[us].dimension, (si, us))


class OutputKeys(unittest.TestCase):
    def test_us_siblings_added_and_si_kept(self):
        out = units.add_us_keys({"required_area_mm2": 645.16, "regime": "critical", "detail": {"G_kg_m2_s": 4.88242764}})
        self.assertAlmostEqual(out["required_area_in2"], 1.0, places=9)
        self.assertEqual(out["required_area_mm2"], 645.16)
        self.assertAlmostEqual(out["detail"]["G_lb_ft2_s"], 1.0, places=6)
        self.assertEqual(out["regime"], "critical")


class CommandLine(unittest.TestCase):
    def test_us_case_equals_si_case(self):
        rc, si, _ = cli("relief-gas", "--W", "12000", "--T", "400", "--set-g", "1500", "--case", "fire", "--M", "44", "--k", "1.13", "--Z", "0.9")
        w = 12000 / 0.45359237
        t = 400 * 9 / 5 - 459.67
        p = 1500 / (0.45359237 * 9.80665 / 0.0254 ** 2 / 1000)
        rc2, us, _ = cli("--units", "us", "relief-gas", "--W", repr(w), "--T", repr(t), "--set-g", repr(p), "--case", "fire", "--M", "44", "--k", "1.13", "--Z", "0.9")
        self.assertEqual((rc, rc2), (0, 0))
        a, b = json.loads(si), json.loads(us)
        self.assertTrue(math.isclose(a["required_area_mm2"], b["required_area_mm2"], rel_tol=1e-9))
        self.assertAlmostEqual(b["required_area_in2"], a["required_area_mm2"] / 645.16, places=9)

    def test_range_check_runs_after_conversion(self):
        # 900 degF is above the soft maximum? no: -500 degF is below absolute zero and must be rejected as a hard violation
        rc, _, err = cli("--units", "us", "relief-gas", "--W", "1000", "--T", "-500", "--set-g", "100", "--M", "30", "--k", "1.2")
        self.assertEqual(rc, 2)
        self.assertIn("temperature", err.lower())

    def test_temperature_rise_is_a_difference(self):
        rc, si, _ = cli("datacentre", "--it-kw", "1000", "--facility-kw", "1300", "--delta-t", "5.5555555555555")
        rc2, us, _ = cli("--units", "us", "datacentre", "--it-kw", "1000", "--facility-kw", "1300", "--delta-t", "10")
        self.assertEqual((rc, rc2), (0, 0))
        self.assertTrue(math.isclose(json.loads(si)["cooling_water_m3_h"], json.loads(us)["cooling_water_m3_h"], rel_tol=1e-9))

    def test_convert_command(self):
        rc, out, _ = cli("convert", "150", "psig", "kPag")
        self.assertEqual(rc, 0)
        self.assertAlmostEqual(json.loads(out)["result"], 1034.213593975254, places=6)
        self.assertEqual(cli("convert", "1", "psig", "psia")[0], 2)
        self.assertEqual(cli("convert", "0", "psig", "psia", "--across-atmosphere")[0], 0)


class Templates(unittest.TestCase):
    def test_template_roundtrip(self):
        t = templating.template("relief-gas", "us")
        self.assertEqual(t["units"], "us")
        self.assertEqual(t["_guide"]["set_g"]["unit"], "psig")
        self.assertEqual(t["_guide"]["W"]["unit"], "lb/h")
        self.assertIsNone(t["inputs"]["W"])
        with self.assertRaises(ValueError):
            templating.to_argv(t)
        t["inputs"].update(W=1000, T=200, set_g=100, M=30, k=1.2)
        argv = templating.to_argv(t)
        self.assertEqual(argv[:3], ["--units", "us", "relief-gas"])
        self.assertIn("--set-g", argv)

    def test_unknown_input_refused(self):
        t = templating.template("relief-gas", "si")
        t["inputs"]["bogus"] = 1
        with self.assertRaises(ValueError):
            templating.to_argv(t)

    def test_us_ranges_are_converted(self):
        rows = {r["name"]: r for r in templating.describe("relief-gas", "us")}
        # hard minimum temperature is absolute zero: -459.67 degF
        self.assertAlmostEqual(rows["T"]["hard_min"], -459.67, places=2)


class NewCommands(unittest.TestCase):
    def test_egress_identity(self):
        rc, out, _ = cli("egress", "--distance", "60", "--speed", "1.2", "--people", "200", "--width", "2", "--specific-flow", "1.3", "--detect-s", "30", "--premove-s", "60")
        self.assertEqual(rc, 0)
        r = json.loads(out)
        self.assertAlmostEqual(r["rset_s"], 30 + 60 + max(60 / 1.2, 200 / (1.3 * 2)), places=9)
        self.assertEqual(r["governing"], "flow through the exit")

    def test_egress_rejects_nonsense(self):
        self.assertEqual(cli("egress", "--distance", "-5", "--speed", "1.2", "--people", "10", "--width", "1", "--specific-flow", "1", "--detect-s", "0", "--premove-s", "0")[0], 2)

    def test_illumination_identity(self):
        rc, out, _ = cli("illumination", "--area", "100", "--flux", "3000", "--uf", "0.6", "--mf", "0.8", "--target", "300")
        r = json.loads(out)
        self.assertAlmostEqual(r["n_exact"], 300 * 100 / (3000 * 0.6 * 0.8), places=9)
        self.assertGreaterEqual(r["achieved_lux"], 300)
        self.assertEqual(cli("illumination", "--area", "100", "--flux", "3000", "--uf", "0.6", "--mf", "0.8")[0], 2)


if __name__ == "__main__":
    unittest.main()

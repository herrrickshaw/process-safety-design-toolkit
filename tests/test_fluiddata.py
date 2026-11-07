import json
import os
import subprocess
import sys
import unittest

from process_safety import fluiddata, twophase

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class FluidData(unittest.TestCase):
    def test_table_shape(self):
        self.assertGreaterEqual(len(fluiddata.names()), 15)
        for n in fluiddata.names():
            rows = fluiddata._fluid(n)["rows"]
            self.assertGreaterEqual(len(rows), 4)
            ps = [r["P_kPa"] for r in rows]
            self.assertEqual(ps, sorted(ps))
            self.assertTrue(all(r["rho_liq_kg_m3"] > 0 and r["omega_two_point"] > 0 for r in rows), n)

    def test_grid_point_and_interpolation(self):
        rows = fluiddata._fluid("propane")["rows"]
        r = rows[5]
        got = fluiddata.at_pressure("propane", r["P_kPa"])
        self.assertAlmostEqual(got["omega_two_point"], r["omega_two_point"], places=9)
        mid = (rows[5]["P_kPa"] * rows[6]["P_kPa"]) ** 0.5
        m = fluiddata.at_pressure("propane", mid)
        lo, hi = sorted((rows[5]["omega_two_point"], rows[6]["omega_two_point"]))
        self.assertTrue(lo <= m["omega_two_point"] <= hi)

    def test_omega_falls_with_pressure(self):
        rows = fluiddata._fluid("propane")["rows"]
        w = [r["omega_two_point"] for r in rows]
        self.assertEqual(w, sorted(w, reverse=True))

    def test_out_of_range_and_unknown(self):
        with self.assertRaises(ValueError):
            fluiddata.at_pressure("propane", 1.0)
        with self.assertRaises(ValueError):
            fluiddata.at_pressure("unobtainium", 1000.0)

    def test_omega_method_reproduces_bundled_hem_flux(self):
        """The shipped HEM fluxes come from direct CoolProp integration; the omega method (two-point) must match them within 3%."""
        worst = 0.0
        for n in fluiddata.names():
            for r in fluiddata._fluid(n)["rows"]:
                g = twophase.mass_flux(r["P_kPa"], r["rho_liq_kg_m3"], r["omega_two_point"])["G_kg_m2_s"]
                worst = max(worst, abs(g / r["G_hem_kg_m2_s"] - 1))
        self.assertLess(worst, 0.03)

    def test_data_file_provenance(self):
        with open(os.path.join(ROOT, "process_safety", "data", "fluid_screening.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        self.assertIn("CoolProp", d["source"])


class Cli(unittest.TestCase):
    def run_cli(self, *a):
        return subprocess.run([sys.executable, "-m", "process_safety", *a], capture_output=True, text=True)

    def test_twophase_with_fluid(self):
        r = self.run_cli("twophase", "--fluid", "propane", "--P0", "1900", "--W", "8", "--Kd", "0.85")
        self.assertEqual(r.returncode, 0, r.stderr)
        out = json.loads(r.stdout)
        self.assertAlmostEqual(out["G_kg_m2_s"] / out["G_hem_reference_kg_m2_s"], 1.0, delta=0.03)

    def test_saturated_basis_warns_near_critical(self):
        r = self.run_cli("twophase", "--fluid", "propane", "--P0", "3500", "--omega-basis", "saturated")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("warning", json.loads(r.stdout))

    def test_fluid_data_cli(self):
        self.assertEqual(self.run_cli("fluid-data").returncode, 0)
        self.assertIn("saturated_liquid", self.run_cli("fluid-data", "ammonia", "--P", "1500").stdout)
        self.assertEqual(self.run_cli("fluid-data", "propane", "--P", "1").returncode, 2)


if __name__ == "__main__":
    unittest.main()

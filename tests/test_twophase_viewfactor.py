import math
import subprocess
import sys
import unittest

from process_safety import ranges, twophase, viewfactor


class TwoPhase(unittest.TestCase):
    def test_critical_ratio_satisfies_published_equation(self):
        for w in (0.5, 1, 3, 10, 100):
            e = twophase.critical_pressure_ratio(w)
            res = e ** 2 + (w * w - 2 * w) * (1 - e) ** 2 + 2 * w * w * math.log(e) + 2 * w * w * (1 - e)
            self.assertAlmostEqual(res, 0.0, places=5, msg=f"omega={w}")

    def test_omega_one_is_isothermal_choking(self):
        self.assertAlmostEqual(twophase.critical_pressure_ratio(1.0), math.exp(-0.5), places=6)
        g = twophase.mass_flux(1000, 2.0, 1.0)["G_kg_m2_s"]
        self.assertAlmostEqual(g, math.exp(-0.5) * math.sqrt(1000e3 * 2.0), delta=1e-3 * g)   # G = e^-1/2 sqrt(P0/v0)

    def test_small_omega_is_incompressible_liquid(self):
        m = twophase.mass_flux(1000, 500.0, 1e-6, P_back_kPa=500)
        self.assertEqual(m["regime"], "subcritical")
        self.assertAlmostEqual(m["G_kg_m2_s"], math.sqrt(2 * 500.0 * 500e3), delta=1e-3 * m["G_kg_m2_s"])

    def test_back_pressure_regimes(self):
        choked = twophase.mass_flux(1000, 600.0, 10.0, P_back_kPa=100)
        self.assertEqual(choked["regime"], "choked")
        sub = twophase.mass_flux(1000, 600.0, 10.0, P_back_kPa=950)
        self.assertEqual(sub["regime"], "subcritical")
        self.assertLess(sub["G_kg_m2_s"], choked["G_kg_m2_s"])

    def test_omega_helpers_and_area(self):
        self.assertAlmostEqual(twophase.omega_two_point(0.002, 0.0024), 9 * 0.2)
        self.assertAlmostEqual(twophase.relief_area_mm2(10.0, 5000.0, 0.8), 2500.0)
        with self.assertRaises(ValueError):
            twophase.relief_area_mm2(10.0, 5000.0, 1.5)

    def test_hard_range_on_pressure(self):
        with self.assertRaises(ranges.RangeError):
            twophase.mass_flux(-5, 600.0, 3.0)


class ViewFactor(unittest.TestCase):
    def test_matches_howell_rectangle_corner(self):
        d, a, b = 5.0, 3.0 / 5.0, 4.0 / 5.0
        exact = (a / math.sqrt(1 + a * a) * math.atan(b / math.sqrt(1 + a * a)) + b / math.sqrt(1 + b * b) * math.atan(a / math.sqrt(1 + b * b))) / (2 * math.pi)
        face = viewfactor.vertical_flame_face(3.0, 4.0, d, lateral_offset_m=1.5)
        self.assertAlmostEqual(viewfactor.view_factor((-d, 0, 0), (1, 0, 0), face, n=250), exact, delta=2e-4)

    def test_far_field_inverse_square(self):
        small = viewfactor.vertical_flame_face(1.0, 1.0, 100.0, 0.0, -0.5)
        f = viewfactor.view_factor((-100.0, 0, 0), (1, 0, 0), small, n=40)
        self.assertAlmostEqual(f, 1.0 / (math.pi * 100.0 ** 2), delta=1e-3 * f)

    def test_facing_away_is_zero_and_flux_scales(self):
        face = viewfactor.vertical_flame_face(10, 10, 8)
        self.assertEqual(viewfactor.view_factor((-8, 0, 0), (-1, 0, 0), face, n=40), 0.0)
        r1 = viewfactor.flux_from_faces((-8, 0, 0), (1, 0, 0), [face], 50.0, 1.0, 60)
        r2 = viewfactor.flux_from_faces((-8, 0, 0), (1, 0, 0), [face], 50.0, 0.5, 60)
        self.assertAlmostEqual(r2["incident_kW_m2"], r1["incident_kW_m2"] / 2)

    def test_two_faces_sum(self):
        f1 = viewfactor.vertical_flame_face(4, 6, 10, lateral_offset_m=-2)
        f2 = viewfactor.vertical_flame_face(4, 6, 10, lateral_offset_m=2)
        whole = viewfactor.vertical_flame_face(8, 6, 10)
        both = viewfactor.flux_from_faces((-10, 0, 0), (1, 0, 0), [f1, f2], 40.0, 1.0, 80)["view_factor"]
        one = viewfactor.view_factor((-10, 0, 0), (1, 0, 0), whole, n=160)
        self.assertAlmostEqual(both, one, delta=2e-4)


class Cli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "process_safety", *args], capture_output=True, text=True)

    def test_twophase_needs_kd_for_area(self):
        r = self.run_cli("twophase", "--P0", "1100", "--rho0", "600", "--omega", "8", "--W", "5")
        self.assertEqual(r.returncode, 2)
        ok = self.run_cli("twophase", "--P0", "1100", "--rho0", "600", "--omega", "8", "--W", "5", "--Kd", "0.85")
        self.assertEqual(ok.returncode, 0)
        self.assertIn("required_area_mm2", ok.stdout)

    def test_flame_flux_cli(self):
        r = self.run_cli("flame-flux", "--width", "20", "--height", "31", "--distance", "15", "--sep", "30.9", "--tau", "0.8", "--n", "60")
        self.assertEqual(r.returncode, 0)
        self.assertIn("incident_kW_m2", r.stdout)


if __name__ == "__main__":
    unittest.main()

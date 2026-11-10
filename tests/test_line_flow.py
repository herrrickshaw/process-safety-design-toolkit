"""Line-friction (HEM) discharge: identities and monotonic behaviour. Experiments are in tests/crosscheck/validate_line.py (reported, not asserted)."""
import math
import unittest

from process_safety import line_flow as lf
from process_safety import yb_annex as y


class LineFlow(unittest.TestCase):
    def test_single_phase_limit_matches_darcy_weisbach(self):
        # ambient set above the vapour pressure so the liquid never flashes: dP = (1 + k_entry + f L/D) 0.5 rho v^2 exactly
        T, P0, Pa, L, D = 270.0, 25e5, 20e5, 40.0, 0.05
        r = lf.line_discharge("propane", T, P0, Pa, [(L, D)], k_entry=0.5)
        rho = y.liquid_density_kg_m3("propane", T)
        v = r["W_kg_s"] / (rho * math.pi / 4 * D * D)
        f = lf.colebrook_f(rho * v * D / y.liquid_viscosity_Pa_s("propane", T), 1.5e-6 / D)
        self.assertAlmostEqual((P0 - Pa) / (0.5 * rho * v * v), 1.0 + 0.5 + f * L / D, delta=0.01 * (1.5 + f * L / D))

    def test_longer_line_passes_less_and_fittings_reduce_flow(self):
        base = lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(20.0, 0.1)])["W_kg_s"]
        longer = lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(80.0, 0.1)])["W_kg_s"]
        valved = lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(20.0, 0.1)], k_fittings=10.0)["W_kg_s"]
        self.assertLess(longer, base)
        self.assertLess(valved, base)

    def test_higher_vessel_pressure_passes_more(self):
        a = lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(30.0, 0.08)])["W_kg_s"]
        b = lf.line_discharge("propane", 278.65, 12.0e5, 1.013e5, [(30.0, 0.08)])["W_kg_s"]
        self.assertGreater(b, a)

    def test_flashing_release_is_choked(self):
        self.assertEqual(lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(30.0, 0.08)])["regime"], "choked at exit")

    def test_colebrook_limits(self):
        self.assertAlmostEqual(lf.colebrook_f(1000.0, 0.0), 0.064, places=9)
        self.assertAlmostEqual(lf.colebrook_f(1e5, 0.0), 0.0180, delta=0.0005)  # smooth-pipe value from the Blasius/Colebrook tables
        self.assertGreater(lf.colebrook_f(1e6, 0.01), lf.colebrook_f(1e6, 0.0))

    def test_refusals(self):
        with self.assertRaises(ValueError):
            lf.line_discharge("propane", 278.65, 0.5e5, 1.013e5, [(10.0, 0.05)])
        with self.assertRaises(ValueError):
            lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [])
        with self.assertRaises(ValueError):
            lf.line_discharge("propane", 278.65, 7.5e5, 1.013e5, [(10.0, -0.05)])
        with self.assertRaises(ValueError):
            lf.colebrook_f(0.0, 0.0)


if __name__ == "__main__":
    unittest.main()

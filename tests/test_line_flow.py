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

    def test_low_driving_pressure_does_not_crash_and_is_ordered(self):
        # the entrance loss alone can exceed the available head at trial flows; the solver must treat that as infeasible, not raise
        low = lf.line_discharge("n-butane", 287.0, 2.6e5, 1.013e5, [(1.85, 0.04)])["W_kg_s"]
        high = lf.line_discharge("n-butane", 287.0, 6.0e5, 1.013e5, [(1.85, 0.04)])["W_kg_s"]
        self.assertGreater(low, 0.0)
        self.assertGreater(high, low)

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



class LineInStudy(unittest.TestCase):
    def _data(self, **extra):
        import json, os
        from process_safety import tools
        with open(os.path.join(os.path.dirname(tools.__file__), "examples", "lgrelease.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        d.update(extra)
        return d

    def test_long_thin_line_reduces_release_and_flame(self):
        from process_safety import lg_release
        base = lg_release.run(self._data())
        out = lg_release.run(self._data(line={"segments": [[60.0, 0.025]], "k_fittings": 5.0}))
        self.assertLess(out["release"]["W_used_kg_s"], base["release"]["W_used_kg_s"])
        self.assertLess(out["jet"]["flame"]["L_B_m"], base["jet"]["flame"]["L_B_m"])

    def test_generous_line_leaves_the_hole_in_control(self):
        from process_safety import lg_release
        base = lg_release.run(self._data())
        out = lg_release.run(self._data(line={"segments": [[2.0, 0.15]]}))
        self.assertEqual(out["release"]["W_used_kg_s"], base["release"]["W_used_kg_s"])

    def test_bad_line_refused(self):
        from process_safety import lg_release
        with self.assertRaises(ValueError):
            lg_release.run(self._data(line={"segments": []}))


if __name__ == "__main__":
    unittest.main()


class DelayedEquilibrium(unittest.TestCase):
    """Relaxation-length option: identities only (the closure is an input, not validated)."""
    SEG = [(67.0, 0.152), (13.0, 0.052)]
    CASE = ("propane", 278.65, 7.53e5)

    def w(self, **kw):
        return lf.line_discharge(*self.CASE, 101325.0, self.SEG, **kw)["W_kg_s"]

    def test_short_relaxation_length_recovers_hem_and_flow_rises_with_length(self):
        hem, w1, w10 = self.w(), self.w(relaxation_length_m=1.0), self.w(relaxation_length_m=10.0)
        self.assertLess(abs(w1 / hem - 1.0), 0.03)  # L_r -> 0 limit is HEM
        self.assertTrue(hem < w1 < w10)  # later flashing -> denser mixture -> more flow

    def test_rejects_non_positive_length(self):
        for bad in (0.0, -1.0):
            with self.assertRaises(ValueError):
                self.w(relaxation_length_m=bad)

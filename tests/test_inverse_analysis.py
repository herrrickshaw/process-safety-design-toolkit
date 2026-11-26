"""Identities of the inverse analysis (tests/crosscheck/inverse_analysis.py): the solver must return a parameter that reproduces its own target."""
import importlib.util
import os
import unittest

spec = importlib.util.spec_from_file_location("inverse_analysis", os.path.join(os.path.dirname(__file__), "crosscheck", "inverse_analysis.py"))
ia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ia)


class InverseIdentities(unittest.TestCase):
    def test_bisect_finds_a_root(self):
        self.assertAlmostEqual(ia.bisect(lambda x: x * x - 2.0, 0.0, 2.0), 2.0 ** 0.5, places=9)

    def test_mass_multiplier_reproduces_the_target_length(self):
        t = ia.TESTS[0]
        target = 31.1
        fm = ia.bisect(lambda f: ia.flame(t, m=t[2] * f)["L_B_m"] - target, 0.02, 1.0)
        self.assertAlmostEqual(ia.flame(t, m=t[2] * fm)["L_B_m"], target, delta=0.01)

    def test_flame_is_longer_with_more_mass(self):
        t = ia.TESTS[1]
        self.assertLess(ia.flame(t, m=t[2] * 0.5)["L_B_m"], ia.flame(t)["L_B_m"])

    def test_droplet_c_ds_scales_linearly_with_the_target_diameter(self):
        rows = {r[0]: r for r in ia.droplet_rows()}
        a, b = rows["STEP 5 bar"], rows["STEP 11 bar"]
        self.assertAlmostEqual(a[3] / 15.0, a[2] / a[1], places=9)
        self.assertAlmostEqual(b[3] / 15.0, b[2] / b[1], places=9)

    def test_dnv_implied_exit_pressure_follows_the_momentum_balance(self):
        for nm, uo, uf, Pe in ia.dnv_state_rows():
            self.assertGreater(uf, uo)
            self.assertGreater(Pe, 1.0)


if __name__ == "__main__":
    unittest.main()

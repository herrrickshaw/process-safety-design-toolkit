import math
import unittest

from process_safety import atex, dust_explosion as de, enclosure_ventilation as ev

R_KMOL = 8314.462618


class Ventilation(unittest.TestCase):
    def test_mass_to_volume_is_the_ideal_gas_law(self):
        v = ev.gas_volume_rate_m3_s(0.01, 2.016, 293.15, 101.325)
        n = 0.01 / 2.016                                   # kmol/s
        self.assertAlmostEqual(101325.0 * v, n * R_KMOL * 293.15, delta=1e-6 * n * R_KMOL * 293.15)

    def test_required_flow_holds_the_target_fraction(self):
        for k in (1.0, 2.0, 5.0):
            q = ev.required_ventilation_m3_s(0.002, 0.04, 0.25, mixing_factor=k)
            self.assertAlmostEqual(ev.steady_fraction_of_lfl(0.002, q, 0.04, mixing_factor=k), 0.25, places=12)

    def test_poorer_mixing_needs_more_air(self):
        a = ev.required_ventilation_m3_s(0.002, 0.04, 0.25, mixing_factor=1.0)
        b = ev.required_ventilation_m3_s(0.002, 0.04, 0.25, mixing_factor=3.0)
        self.assertAlmostEqual(b, 3.0 * a, delta=1e-12 * b)

    def test_lower_target_or_higher_generation_needs_more_air(self):
        base = ev.required_ventilation_m3_s(0.002, 0.04, 0.25)
        self.assertGreater(ev.required_ventilation_m3_s(0.002, 0.04, 0.10), base)
        self.assertGreater(ev.required_ventilation_m3_s(0.004, 0.04, 0.25), base)

    def test_dilute_limit_is_generation_over_concentration(self):
        g, c = 1e-6, 0.01
        q = ev.required_ventilation_m3_s(g, 0.5, c / 0.5)   # lfl 0.5 and fraction 0.02, so the target concentration is c
        self.assertAlmostEqual(q, g / c, delta=0.02 * g / c)

    def test_time_to_fraction_sealed_limit_and_monotonic(self):
        v, g = 50.0, 0.001
        t_sealed = ev.time_to_fraction_of_lfl_s(v, g, 0.0, 0.04, 0.25)
        self.assertAlmostEqual(t_sealed, -v / g * math.log(1 - 0.25 * 0.04), places=9)
        self.assertAlmostEqual(t_sealed, v * 0.25 * 0.04 / g, delta=0.01 * t_sealed)   # about V C / g for a small fraction
        t_vent = ev.time_to_fraction_of_lfl_s(v, g, 0.05, 0.04, 0.25)
        self.assertGreater(t_vent, t_sealed)

    def test_never_reached_when_ventilation_holds_below_target(self):
        q = ev.required_ventilation_m3_s(0.001, 0.04, 0.25)
        self.assertEqual(ev.time_to_fraction_of_lfl_s(50.0, 0.001, 2 * q, 0.04, 0.25), math.inf)

    def test_refusals(self):
        for args in ((0.0, 0.04, 0.25), (0.001, 0.0, 0.25), (0.001, 0.04, 0.0), (0.001, 0.04, 1.0), (0.001, 1.5, 0.25)):
            with self.assertRaises(ValueError, msg=str(args)):
                ev.required_ventilation_m3_s(*args)
        with self.assertRaises(ValueError):
            ev.required_ventilation_m3_s(0.001, 0.04, 0.25, mixing_factor=0.5)


class DustCubicLaw(unittest.TestCase):
    def test_round_trip(self):
        self.assertAlmostEqual(de.dpdt_max_bar_s(de.kst_bar_m_s(350.0, 0.02), 0.02), 350.0, places=9)

    def test_cubic_law_definition(self):
        self.assertAlmostEqual(de.kst_bar_m_s(100.0, 1.0), 100.0, places=12)
        self.assertAlmostEqual(de.kst_bar_m_s(100.0, 8.0), 200.0, places=12)            # V^(1/3) = 2

    def test_scale_up_by_volume(self):
        self.assertAlmostEqual(de.scale_dpdt_bar_s(400.0, 0.02, 20.0), 400.0 * (0.02 / 20.0) ** (1 / 3), places=9)
        self.assertLess(de.scale_dpdt_bar_s(400.0, 0.02, 20.0), 400.0)                  # a larger vessel has a lower maximum rate of rise

    def test_class_comes_from_atex(self):
        self.assertEqual(de.explosion_class(250.0), atex.kst_class(250.0))

    def test_refusals(self):
        for bad in (dict(dpdt_max_bar_s=-1, volume_m3=1), dict(dpdt_max_bar_s=10, volume_m3=0)):
            with self.assertRaises(ValueError):
                de.kst_bar_m_s(**bad)


if __name__ == "__main__":
    unittest.main()

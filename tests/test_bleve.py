"""BLEVE fireball (Yellow Book CPR 14E 6.5.7) and Purple Book framework: the book's worked example is the oracle."""
import math
import unittest

from process_safety import bleve


class YellowBookExample(unittest.TestCase):
    """Yellow Book section 6.6.5: 45 m3 propane road tanker, 85 % full, receptor 200 m from the point under the fireball."""
    m = 0.85 * 45.0 * 517.0

    def test_mass(self):
        self.assertAlmostEqual(bleve.released_mass_kg(45.0, 0.85, 517.0), 19776.0, delta=1.0)      # book prints 19775

    def test_dimensions(self):
        m = 19775.0
        self.assertAlmostEqual(bleve.radius_m(m), 80.68, delta=0.02)
        self.assertAlmostEqual(bleve.duration_s(m), 11.15, delta=0.01)
        self.assertAlmostEqual(bleve.centre_height_m(m), 161.37, delta=0.05)

    def test_flux_chain(self):
        m = 19775.0
        fl = bleve.flux_W_m2(m, 16e5, 46.013e6, 0.426134e6, 2582.0, 200.0, tau=0.7335, dT_K=1717.0)
        self.assertAlmostEqual(fl["X_m"], 256.98, delta=0.05)
        self.assertAlmostEqual(fl["F_view"], 0.09856, delta=2e-5)
        self.assertAlmostEqual(fl["F_s"], 0.314, delta=0.001)
        self.assertAlmostEqual(fl["dH_J_kg"], 41.153e6, delta=2e3)
        self.assertAlmostEqual(fl["SEP_W_m2"], 28.02e4, delta=0.03e4)
        # the book prints 20.361e3, but its own factors give 28.02e4 x 0.09856 x 0.7335 = 20.257e3 (an arithmetic slip of 0.5 % in the book); the chain here gives the latter
        self.assertAlmostEqual(fl["q_W_m2"], 28.02e4 * 0.09856 * 0.7335, delta=0.01e3)

    def test_transmissivity_629_matches_book_value(self):
        self.assertAlmostEqual(bleve.transmissivity(21.04e4), 0.67, delta=0.005)


class Identities(unittest.TestCase):
    def test_heat_balance(self):
        """SEP x surface area x duration = radiated heat F_s dH m."""
        m, Psv = 5000.0, 12e5
        fl = bleve.flux_W_m2(m, Psv, 46.013e6, 0.426e6, 2500.0, 100.0)
        area = 4 * math.pi * fl["r_fb_m"] ** 2
        self.assertAlmostEqual(fl["SEP_W_m2"] * area * fl["duration_s"], fl["F_s"] * fl["dH_J_kg"] * m, delta=1e-6 * fl["F_s"] * fl["dH_J_kg"] * m)

    def test_flux_falls_with_distance_and_distance_inverts(self):
        m, Psv = 5000.0, 12e5
        q = [bleve.flux_W_m2(m, Psv, 46.013e6, 0.426e6, 2500.0, x)["q_W_m2"] for x in (50.0, 100.0, 200.0, 400.0)]
        self.assertTrue(all(a > b for a, b in zip(q, q[1:])))
        d = bleve.distance_to_flux_m(m, Psv, 46.013e6, 0.426e6, 2500.0, 35e3)
        self.assertAlmostEqual(bleve.flux_W_m2(m, Psv, 46.013e6, 0.426e6, 2500.0, d)["q_W_m2"], 35e3, delta=1.0)

    def test_scaling(self):
        self.assertAlmostEqual(bleve.radius_m(8000.0) / bleve.radius_m(1000.0), 8.0 ** 0.325, places=9)
        self.assertGreater(bleve.duration_s(2000.0), bleve.duration_s(1000.0))

    def test_inside_fireball_refused(self):
        with self.assertRaises(ValueError):
            bleve.view_factor(50.0, 0.0, 10.0)

    def test_net_heat_must_be_positive(self):
        with self.assertRaises(ValueError):
            bleve.flux_W_m2(1000.0, 1e6, 1e6, 0.4e6, 2500.0, 50.0)


class PurpleBook(unittest.TestCase):
    def test_direct_ignition_bands(self):
        self.assertEqual(bleve.direct_ignition_probability(500.0), 0.2)
        self.assertEqual(bleve.direct_ignition_probability(5000.0), 0.5)
        self.assertEqual(bleve.direct_ignition_probability(50000.0), 0.7)
        self.assertEqual(bleve.direct_ignition_probability(500.0, "low"), 0.02)

    def test_cloud_fraction_is_continuous(self):
        self.assertAlmostEqual(bleve.cloud_mass_fraction(0.1 - 1e-12), bleve.cloud_mass_fraction(0.1), places=6)
        self.assertAlmostEqual(bleve.cloud_mass_fraction(0.36 - 1e-12), 1.0, places=6)
        self.assertEqual(bleve.cloud_mass_fraction(0.5), 1.0)

    def test_failure_pressure(self):
        self.assertAlmostEqual(bleve.failure_pressure_Pa(15e5, 0.0), 1.21 * 15e5)

    def test_outcome_frequencies_sum(self):
        o = bleve.catastrophic_failure_outcomes(40000.0)
        tot = o["f_BLEVE_fireball_per_y"] + o["f_cloud_and_pool_direct_ignition_per_y"] + o["f_no_direct_ignition_per_y"]
        self.assertAlmostEqual(tot, o["f_instantaneous_per_y"], delta=1e-18)
        self.assertAlmostEqual(o["f_BLEVE_fireball_per_y"], 5e-7 * 0.7 * 0.7)
        self.assertAlmostEqual(bleve.catastrophic_failure_outcomes(40000.0, True)["f_instantaneous_per_y"], 5.5e-6)


if __name__ == "__main__":
    unittest.main()

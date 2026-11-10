"""Vapour cloud explosion screening (Purple Book 4.8): the book's own consistency statement and scaling identities."""
import math
import unittest

from process_safety import vce

HC_PROPANE = 46.013e6


class PurpleBook(unittest.TestCase):
    def test_default_fraction_reproduces_the_older_formulas(self):
        """The book states that f_obstr = 0.08 reproduces R = 0.03 (0.1 E)^(1/3) and 0.06 (0.1 E)^(1/3)."""
        for m in (500.0, 5000.0, 50000.0):
            new = vce.blast_radii_m(m, HC_PROPANE)
            old = vce.old_formula_radii_m(m, HC_PROPANE)
            self.assertAlmostEqual(new["R_0.3bar_m"] / old["R_0.3bar_m"], 1.0, delta=0.01)
            self.assertAlmostEqual(new["R_0.1bar_m"] / old["R_0.1bar_m"], 1.0, delta=0.01)

    def test_radii_ratio_and_scaling(self):
        r = vce.blast_radii_m(10000.0, HC_PROPANE)
        self.assertAlmostEqual(r["R_0.1bar_m"] / r["R_0.3bar_m"], 2.0, places=12)
        r8 = vce.blast_radii_m(80000.0, HC_PROPANE)
        self.assertAlmostEqual(r8["R_0.3bar_m"] / r["R_0.3bar_m"], 2.0, places=9)

    def test_obstruction_fraction_scaling(self):
        a = vce.blast_radii_m(10000.0, HC_PROPANE, 0.08)["R_0.3bar_m"]
        b = vce.blast_radii_m(10000.0, HC_PROPANE, 0.64)["R_0.3bar_m"]
        self.assertAlmostEqual(b / a, 2.0, places=9)

    def test_event_split_sums(self):
        f = vce.event_frequencies(1e-6)
        self.assertAlmostEqual(f["flash_fire_per_y"] + f["explosion_per_y"], 1e-6, places=20)
        self.assertAlmostEqual(f["explosion_per_y"], 0.4e-6, places=20)

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            vce.blast_radii_m(100.0, HC_PROPANE, 0.0)
        with self.assertRaises(ValueError):
            vce.event_frequencies(1.0, 1.5)


class JetMass(unittest.TestCase):
    def test_lfl_mass_fraction(self):
        w = vce.lfl_mass_fraction(0.021, 44.096)
        self.assertAlmostEqual(w, 0.021 * 44.096 / (0.021 * 44.096 + 0.979 * 28.96), places=12)
        self.assertAlmostEqual(w, 0.0316, delta=0.0002)

    def test_jet_mass_scaling(self):
        """Doubling the flow at fixed d*, u0 doubles the mass; the mass scales as 1/u0 and with the square of the LFL dilution at fixed d*."""
        base = vce.jet_flammable_mass_kg(2.0, 0.1, 100.0, 0.03)
        self.assertAlmostEqual(vce.jet_flammable_mass_kg(4.0, 0.1, 100.0, 0.03) / base, 2.0, places=9)
        self.assertAlmostEqual(vce.jet_flammable_mass_kg(2.0, 0.1, 200.0, 0.03) / base, 0.5, places=9)
        self.assertAlmostEqual(vce.jet_flammable_mass_kg(2.0, 0.1, 100.0, 0.015) / base, 4.0, places=9)

    def test_jet_mass_matches_hand_integral(self):
        """Hand integral: fuel per metre m(z)/u0 = 0.32 m0 z/(d* u0); integral 0..z_L = 0.16 m0 z_L^2/(d* u0)."""
        m0, ds, u0, w = 2.34, 0.126, 153.0, 0.0316
        zL = (1 / w) / 0.32 * ds
        self.assertAlmostEqual(vce.jet_flammable_mass_kg(m0, ds, u0, w), 0.16 * m0 * zL ** 2 / (ds * u0), places=9)


if __name__ == "__main__":
    unittest.main()

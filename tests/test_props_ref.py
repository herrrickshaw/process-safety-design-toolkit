"""Reference (NIST-tabulated) saturation properties: identities and cross-source consistency with the Yellow Book Annex."""
import unittest

from process_safety import props_ref as p
from process_safety import yb_annex as y


class PropsRef(unittest.TestCase):
    def test_round_trip_saturation(self):
        for fl in ("propane", "n-butane"):
            for T in (180.0, 233.3, 287.7, 331.1):
                self.assertAlmostEqual(p.saturation_temperature_K(fl, p.vapour_pressure_Pa(fl, T)), T, places=3)

    def test_monotonic_and_signs(self):
        for fl in ("propane", "n-butane"):
            Ts = [200.0 + 10 * k for k in range(14)]
            self.assertTrue(all(p.vapour_pressure_Pa(fl, a) < p.vapour_pressure_Pa(fl, b) for a, b in zip(Ts, Ts[1:])))
            self.assertTrue(all(p.liquid_density_kg_m3(fl, a) > p.liquid_density_kg_m3(fl, b) for a, b in zip(Ts, Ts[1:])))
            self.assertTrue(all(p.heat_of_vaporisation_J_kg(fl, a) > p.heat_of_vaporisation_J_kg(fl, b) for a, b in zip(Ts, Ts[1:])))
            self.assertTrue(all(p.vapour_density_kg_m3(fl, a) < p.vapour_density_kg_m3(fl, b) for a, b in zip(Ts, Ts[1:])))

    def test_real_gas_limits(self):
        # Z of the saturated vapour tends to 1 at low pressure and falls as the critical point is approached
        for fl, Tlo, Thi in (("propane", 180.0, 340.0), ("n-butane", 200.0, 360.0)):
            self.assertAlmostEqual(p.compressibility_saturated_vapour(fl, Tlo), 1.0, delta=0.01)
            self.assertLess(p.compressibility_saturated_vapour(fl, Thi), 0.8)

    def test_boiling_points_agree_with_annex(self):
        for fl in ("propane", "n-butane"):
            self.assertAlmostEqual(p.normal_boiling_point_K(fl), y.normal_boiling_point_K(fl), delta=0.3)

    def test_propane_agrees_with_annex_within_3_percent(self):
        for T in (240.0, 275.0, 300.0):
            self.assertAlmostEqual(p.vapour_pressure_Pa("propane", T) / y.vapour_pressure_Pa("propane", T), 1.0, delta=0.03)
            self.assertAlmostEqual(p.liquid_density_kg_m3("propane", T) / y.liquid_density_kg_m3("propane", T), 1.0, delta=0.03)

    def test_out_of_range_refused(self):
        with self.assertRaises(ValueError):
            p.vapour_pressure_Pa("propane", 400.0)
        with self.assertRaises(ValueError):
            p.liquid_density_kg_m3("methane", 250.0)


if __name__ == "__main__":
    unittest.main()

"""Fire-case relief against the HSL propane vessel trials as tabulated by Roberts, Buckland, Shirvill, Lowesmith and Salater,
"Design and protection of pressure systems to withstand severe fires", IChemE Symposium Series 149 (2003), Table 3 (owner-supplied PDF xvii-paper-22).

Oracle: 2 tonne tank, 85 % fill, wetted area 15.3 m2, set 17.2 barg: heat input 404 kW (adequate drainage) and 664 kW (inadequate), API required effective
areas 296 and 486 mm2. The paper's 5 tonne pool-fire row (25.7 m2, 577 and 948 kW) does not follow Q = C A^0.82 for 25.7 m2 (the formula gives 619 and 1016 kW;
577 kW implies A = 23.4 m2), so it is not used as an oracle. The required areas match the API 520 critical-flow formula with Z = 1 and k = 1.13 at 335 K to within
about 5 %; with the real saturated-vapour Z (about 0.67) the area is about 22 % smaller, a sensitivity the relief workbook records.
"""
import unittest

from process_safety import relief

ACCUM_FIRE = 0.21


class HslFireCase(unittest.TestCase):
    def test_api521_heat_input_matches_the_trial_table(self):
        self.assertAlmostEqual(relief.fire_heat_input_W(15.3, 1.0, True) / 1000.0, 404.0, delta=404.0 * 0.01)
        self.assertAlmostEqual(relief.fire_heat_input_W(15.3, 1.0, False) / 1000.0, 664.0, delta=664.0 * 0.01)

    def test_pool_fire_row_is_inconsistent_with_the_formula(self):
        # documents why the 5 tonne row is not an oracle: the printed 577 kW would need a smaller wetted area than the printed 25.7 m2
        self.assertGreater(relief.fire_heat_input_W(25.7, 1.0, True) / 1000.0, 600.0)

    def test_required_area_matches_published_within_7_percent_for_ideal_vapour(self):
        P1 = relief.relieving_pressure_kpa(17.2 * 100.0, "fire")
        for W_kg_s, expected in ((1.51, 296.0), (2.48, 486.0)):
            A = relief.gas_area(W_kg_s * 3600.0, 335.0, P1, 101.325, 44.096, 1.13, 1.0).required_area_mm2
            self.assertAlmostEqual(A / expected, 1.0, delta=0.07, msg=W_kg_s)

    def test_real_gas_z_reduces_the_area_by_the_square_root_of_z(self):
        P1 = relief.relieving_pressure_kpa(17.2 * 100.0, "fire")
        a1 = relief.gas_area(5436.0, 335.0, P1, 101.325, 44.096, 1.13, 1.0).required_area_mm2
        a2 = relief.gas_area(5436.0, 335.0, P1, 101.325, 44.096, 1.13, 0.673).required_area_mm2
        self.assertAlmostEqual(a2 / a1, 0.673 ** 0.5, places=6)



class RealGasFlux(unittest.TestCase):
    """API 520-I (supplied copy) 5.6.1, 5.6.3.2.2 and Annex B.3.5: Z = 1.0 when no valid calculated Z exists; ideal-gas equation valid for Z about 0.8 to 1.1."""
    P1, T, M, K = 2187.365, 334.75, 44.096, 1.115

    def test_effective_z_of_an_ideal_gas_flux_is_one(self):
        G1, _ = relief.gas_mass_flux(self.P1, 101.325, self.T, self.M, self.K, 1.0)
        self.assertAlmostEqual(relief.effective_Z(G1, self.P1, self.T, self.M, self.K), 1.0, places=9)

    def test_area_from_flux_reproduces_the_gas_equation_at_the_effective_z(self):
        G_real = 6225.1   # CoolProp isentropic integration for saturated propane at this relieving state (tests/crosscheck/check_real_gas_flux.py)
        z = relief.effective_Z(G_real, self.P1, self.T, self.M, self.K)
        a_eq = relief.gas_area(28863.0, self.T, self.P1, 101.325, self.M, self.K, z).required_area_mm2
        a_flux = relief.gas_area_from_flux(28863.0, G_real)
        self.assertAlmostEqual(a_eq / a_flux, 1.0, places=6)

    def test_z_one_is_conservative_against_the_real_gas_flux_for_saturated_propane(self):
        z = relief.effective_Z(6225.1, self.P1, self.T, self.M, self.K)
        self.assertTrue(0.75 < z < 0.82)          # about 0.78: Z = 1 over-sizes by about 13 %, the calculated Z of 0.673 under-sizes by about 7 %
        a1 = relief.gas_area(28863.0, self.T, self.P1, 101.325, self.M, self.K, 1.0).required_area_mm2
        a_real = relief.gas_area_from_flux(28863.0, 6225.1)
        self.assertGreater(a1, a_real)
        a_calc = relief.gas_area(28863.0, self.T, self.P1, 101.325, self.M, self.K, 0.673).required_area_mm2
        self.assertLess(a_calc, a_real)

    def test_refusals(self):
        with self.assertRaises(ValueError):
            relief.gas_area_from_flux(0.0, 5000.0)


if __name__ == "__main__":
    unittest.main()

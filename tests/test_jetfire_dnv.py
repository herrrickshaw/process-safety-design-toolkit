"""JFSH-Cook liquid / two-phase source diameter (DNV Jet Fire Theory eq 58): DNV's own validation outputs (Validation document, Table 13) are the oracle.

Inputs are DNV's post-expansion state for each test (mass flow, velocity, expanded radius from Table 12/13), ambient from Table 9.
DNV predicted flame lengths: B3026 38.9 m, B3029 50.0 m, SA8051 33.2 m. The measured lengths (31.1, 30.7, 18.3 m) are NOT the oracle here:
DNV states its model is conservative for these tests; this checks that the toolkit implements the same model, not that the model is right.
"""
import math
import unittest

from process_safety import jet_flame as jf

R = 8.314462618
HC = {"propane": 46.013e6, "n-butane": 45.86e6}
MW = {"propane": 44.096, "n-butane": 58.1}
# name, fluid, m, v, r, wind, angle wind-release, T_ambient, T_sat(1 atm) used by DNV, DNV flame length
CASES = [("B3026", "propane", 16.1, 152.74, 0.059, 3.7, 16.0, 286.85, 230.51, 38.9),
         ("B3029", "propane", 18.0, 146.47, 0.062, 2.0, 9.0, 281.15, 230.51, 50.0),
         ("SA8051", "n-butane", 6.86, 46.22, 0.040, 0.5, 73.0, 281.85, 272.14, 33.2)]


def _run(fluid, m, v, r, wind, ang, Ta, Tsat, with_vap):
    rho_j = m / (math.pi * r * r * v)
    rho_a = 1.0e5 * 0.02896 / (R * Ta)
    rho_vap = 1.0e5 * MW[fluid] / 1000.0 / (R * Tsat)
    return jf.chamberlain(m, rho_j, rho_a, MW[fluid], HC[fluid], wind, ang, v_j_m_s=v, fs_model="cook", rho_vap_kg_m3=rho_vap if with_vap else None)


class DnvTwoPhase(unittest.TestCase):
    def test_flame_length_matches_dnv_validation_within_5_percent(self):
        for nm, fl, m, v, r, wind, ang, Ta, Tsat, ld in CASES:
            L = _run(fl, m, v, r, wind, ang, Ta, Tsat, True)["L_B_m"]
            self.assertAlmostEqual(L / ld, 1.0, delta=0.05, msg=nm)

    def test_pure_vapour_diameter_is_longer_for_two_phase_jets(self):
        for nm, fl, m, v, r, wind, ang, Ta, Tsat, ld in CASES:
            a = _run(fl, m, v, r, wind, ang, Ta, Tsat, True)["L_B_m"]
            b = _run(fl, m, v, r, wind, ang, Ta, Tsat, False)["L_B_m"]
            self.assertGreater(b, 1.2 * a, msg=nm)

    def test_source_diameter_relation(self):
        out = _run("propane", 16.1, 152.74, 0.059, 3.7, 16.0, 286.85, 230.51, True)
        rho_j = 16.1 / (math.pi * 0.059 ** 2 * 152.74)
        rho_vap = 1.0e5 * 44.096 / 1000.0 / (R * 230.51)
        self.assertAlmostEqual(out["Ds_m"], 2 * 0.059 * math.sqrt(rho_j / rho_vap), places=9)

    def test_default_unchanged_when_option_absent(self):
        out = jf.chamberlain(2.0, 5.0, 1.2, 44.1, 4.6e7, 5.0, 90.0, v_j_m_s=100.0)
        self.assertAlmostEqual(out["Ds_m"], 2 * math.sqrt(2.0 / (5.0 * math.pi * 100.0)) * math.sqrt(5.0 / 1.2), places=9)

    def test_angle_against_wind_allowed_and_shortens(self):
        base = jf.chamberlain(2.0, 5.0, 1.2, 44.1, 4.6e7, 5.0, 0.0, v_j_m_s=100.0)["L_B_m"]
        back = jf.chamberlain(2.0, 5.0, 1.2, 44.1, 4.6e7, 5.0, 180.0, v_j_m_s=100.0)["L_B_m"]
        self.assertLess(back, base)

    def test_bad_density_refused(self):
        with self.assertRaises(ValueError):
            jf.chamberlain(2.0, 5.0, 1.2, 44.1, 4.6e7, 5.0, 90.0, v_j_m_s=100.0, rho_vap_kg_m3=0.0)


if __name__ == "__main__":
    unittest.main()

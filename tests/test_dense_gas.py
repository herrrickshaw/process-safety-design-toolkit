import unittest

from process_safety import dense_gas as dg

G = 9.80665
RHO_A = 1.204
# EPA TSCREEN workbook (EPA-454/B-94-023 text, section 5.4) chlorine gas leak, 2 m/s wind at 10 m
CL = dict(Qm_kg_s=1.10, rho2_kg_m3=3.059, T2_K=282.5, Ta_K=293.15, rho_a_kg_m3=RHO_A, Ur_m_s=2.0)


class Criteria(unittest.TestCase):
    def test_reduced_gravity_definition(self):
        self.assertAlmostEqual(dg.reduced_gravity(3.059, RHO_A), G * (3.059 - RHO_A) / RHO_A, places=12)
        self.assertEqual(dg.reduced_gravity(RHO_A, RHO_A), 0.0)

    def test_source_dimension_matches_volume_flux_relation(self):
        d = dg.source_dimension_m(1.10, 3.059, 2.0)
        self.assertAlmostEqual(d * d * 2.0 / 2.0, 1.10 / 3.059, places=12)          # D^2 Ur / 2 = Qm / rho2
        self.assertAlmostEqual(d, 0.600, delta=0.001)                                 # worked example in the source

    def test_plume_criterion_is_a_richardson_number(self):
        c = dg.plume_is_dense(1.10, 3.059, RHO_A, 2.0)
        D = dg.source_dimension_m(1.10, 3.059, 2.0)
        self.assertAlmostEqual(c["richardson"], G * (3.059 - RHO_A) / RHO_A * (1.10 / 3.059) / (D * 2.0 ** 3), places=12)
        self.assertAlmostEqual(c["ratio"], 0.959, delta=0.002)                        # worked example in the source
        self.assertTrue(c["dense"])

    def test_light_gas_is_never_dense(self):
        self.assertFalse(dg.plume_is_dense(1.0, 0.7, RHO_A, 3.0)["dense"])
        self.assertFalse(dg.puff_is_dense(100.0, 0.7, RHO_A, 3.0)["dense"])

    def test_high_wind_turns_dense_behaviour_off(self):
        self.assertTrue(dg.plume_is_dense(1.1, 3.059, RHO_A, 2.0)["dense"])
        self.assertFalse(dg.plume_is_dense(1.1, 3.059, RHO_A, 60.0)["dense"])

    def test_puff_criterion_value(self):
        c = dg.puff_is_dense(1380.0, 1.876, RHO_A, 2.0)
        self.assertAlmostEqual(c["alpha_i"], 3.52, delta=0.02)                       # worked example in the source
        self.assertTrue(c["dense"])


class Corrections(unittest.TestCase):
    def test_cold_gas_cases(self):
        a, b = dg.cold_gas_cases(3.059, 282.5, 293.15)
        self.assertEqual(a, (3.059, 282.5))
        self.assertAlmostEqual(b[0], 3.059 * 282.5 / 293.15, places=12)             # rho * T2 / Ta
        self.assertEqual(b[1], 293.15)

    def test_averaging_time_factor(self):
        self.assertEqual(dg.concentration_for_10min(1.0, 10.0), 1.0)
        self.assertAlmostEqual(dg.concentration_for_10min(1.0, 15.0), 1.020, delta=0.0006)   # worked example in the source
        self.assertTrue(dg.concentration_for_10min(1.0, 1.0) < 1.0)                 # shorter averaging time reads higher, so the 10-minute equivalent is lower

    def test_nonisothermal_mole_fraction(self):
        self.assertAlmostEqual(dg.nonisothermal_mole_fraction(0.1, 293.15, 293.15), 0.1, places=12)
        self.assertAlmostEqual(dg.nonisothermal_mole_fraction(1e-6, 293.15, 282.5), 1e-6 / (1e-6 + 293.15 / 282.5 * (1 - 1e-6)), places=15)
        self.assertAlmostEqual(dg.nonisothermal_mole_fraction(1e-6, 293.15, 282.5), 1e-6, delta=4e-8)   # the source rounds this to 1 ppm
        self.assertLess(dg.nonisothermal_mole_fraction(0.1, 293.15, 200.0), 0.1)     # a colder source needs a smaller equivalent mole fraction

    def test_release_regime_thresholds(self):
        self.assertEqual(dg.release_regime(2.0, 10000.0, 1000.0), "continuous")      # Ur Td / x = 20
        self.assertEqual(dg.release_regime(2.0, 1000.0, 1000.0), "both")             # 2
        self.assertEqual(dg.release_regime(2.0, 100.0, 1000.0), "instantaneous")     # 0.2


class Distances(unittest.TestCase):
    def test_plume_far_field_matches_the_worked_example(self):
        # corrections off: the source example rounds Cm to 1 ppm, so isolate the fitted equation itself
        r = dg.continuous_distance_m(**CL, Cm_mole_fraction=1e-6, t_av_min=10.0, apply_nonisothermal=False)
        by = {c["case"]: c for c in r["cases"]}
        self.assertAlmostEqual(by["no_heat_transfer"]["x_m"], 8710.0, delta=0.003 * 8710.0)
        self.assertAlmostEqual(by["full_heat_transfer"]["x_m"], 8950.0, delta=0.003 * 8950.0)
        self.assertEqual(r["x_m"], max(c["x_m"] for c in r["cases"]))                # report the larger distance

    def test_nonisothermal_correction_is_conservative(self):
        # the correction acts on the case whose source stays cold; the full-heat-transfer case has T2 = Ta so it is unchanged
        kw = dict(**CL, Cm_mole_fraction=1e-6, t_av_min=10.0)
        with_c = {c["case"]: c["x_m"] for c in dg.continuous_distance_m(**kw)["cases"]}
        without = {c["case"]: c["x_m"] for c in dg.continuous_distance_m(**kw, apply_nonisothermal=False)["cases"]}
        self.assertGreater(with_c["no_heat_transfer"], without["no_heat_transfer"])
        self.assertAlmostEqual(with_c["full_heat_transfer"], without["full_heat_transfer"], delta=1e-9)

    def test_distance_grows_as_the_target_concentration_falls(self):
        xs = [dg.continuous_distance_m(**CL, Cm_mole_fraction=c)["x_m"] for c in (1e-3, 1e-4, 1e-5, 1e-6)]
        self.assertEqual(xs, sorted(xs))

    def test_plume_distance_scaling_with_release_rate(self):
        # beta ~ alpha^-1/2 and alpha ~ q^(1/5): x = beta sqrt(q/U) so x ~ q^(1/2 - 1/10) = q^0.4 at fixed other inputs
        a = dg.continuous_distance_m(**{**CL, "Qm_kg_s": 1.0}, Cm_mole_fraction=1e-5, heat_transfer="none")["x_m"]
        b = dg.continuous_distance_m(**{**CL, "Qm_kg_s": 4.0}, Cm_mole_fraction=1e-5, heat_transfer="none")["x_m"]
        self.assertAlmostEqual(b / a, 4.0 ** 0.4, delta=1e-9)

    def test_plume_refuses_outside_the_recovered_fit(self):
        with self.assertRaises(ValueError):
            dg.continuous_distance_m(**CL, Cm_mole_fraction=0.05)                    # LFL-type concentration: fit not available
        with self.assertRaises(ValueError):
            dg.continuous_distance_m(**{**CL, "Qm_kg_s": 1e-4}, Cm_mole_fraction=1e-6)   # alpha_c < 1

    def test_passive_release_is_refused_with_advice(self):
        with self.assertRaises(ValueError) as cm:
            dg.continuous_distance_m(**{**CL, "rho2_kg_m3": 0.7, "T2_K": 293.15}, Cm_mole_fraction=1e-6)
        self.assertIn("passive", str(cm.exception))

    def test_puff_far_field_close_to_the_worked_example(self):
        r = dg.instantaneous_distance_m(Q_kg=1380.0, rho2_kg_m3=1.876, T2_K=239.05, Ta_K=293.15, rho_a_kg_m3=RHO_A, Ur_m_s=2.0,
                                        Cm_mole_fraction=1e-6, Co=0.188, heat_transfer="none", apply_nonisothermal=False)
        self.assertAlmostEqual(r["x_m"], 6480.0, delta=0.03 * 6480.0)               # residual about 2.4 percent, see module docstring

    def test_puff_distance_scaling_with_mass(self):
        kw = dict(rho2_kg_m3=1.876, T2_K=293.15, Ta_K=293.15, rho_a_kg_m3=RHO_A, Ur_m_s=2.0, Cm_mole_fraction=1e-5, heat_transfer="none")
        a = dg.instantaneous_distance_m(Q_kg=500.0, **kw)["x_m"]
        b = dg.instantaneous_distance_m(Q_kg=4000.0, **kw)["x_m"]
        # alpha_i ~ Q^(1/6), beta ~ alpha^-1/2, x = beta Q^(1/3): x ~ Q^(1/3 - 1/12) = Q^0.25 (alpha_i between 1 and 10)
        self.assertAlmostEqual(b / a, 8.0 ** 0.25, delta=1e-9)

    def test_puff_alpha_is_capped_at_ten(self):
        kw = dict(rho2_kg_m3=3.0, T2_K=293.15, Ta_K=293.15, rho_a_kg_m3=RHO_A, Ur_m_s=1.0, Cm_mole_fraction=1e-5, heat_transfer="none")
        r = dg.instantaneous_distance_m(Q_kg=5e7, **kw)
        self.assertGreater(r["alpha_i"], 10.0)
        self.assertEqual(r["alpha_used"], 10.0)

    def test_notes_state_the_limits(self):
        notes = " ".join(dg.continuous_distance_m(**CL, Cm_mole_fraction=1e-6)["notes"]).lower()
        for word in ("jet", "aerosol", "obstacle", "screening"):
            self.assertIn(word, notes)


if __name__ == "__main__":
    unittest.main()

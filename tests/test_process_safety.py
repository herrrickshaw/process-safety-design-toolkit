import math, unittest
from process_safety import fireball, flare, relief, sil, standards


def lam_avg(f, ti, n=20000):
    return sum(f(ti * (i + .5) / n) for i in range(n)) / n


class Relief(unittest.TestCase):
    def test_gas_critical_matches_api_si_constant(self):
        W, T, P1, M, k, Z = 20000, 400, 1200, 44.0, 1.15, 0.95
        r = relief.gas_area(W, T, P1, 101.325, M, k, Z)
        C = 520 * math.sqrt(k * (2 / (k + 1)) ** ((k + 1) / (k - 1)))
        api = 13160 * W / (C * 0.975 * P1) * math.sqrt(T * Z / M)
        self.assertEqual(r.regime, "critical")
        self.assertAlmostEqual(r.required_area_mm2 / api, 1, delta=0.005)

    def test_gas_subcritical_matches_api_17_9(self):
        W, T, P1, P2, M, k, Z = 20000, 400, 1200, 800, 44.0, 1.15, 0.95
        r = relief.gas_area(W, T, P1, P2, M, k, Z)
        x = P2 / P1
        F2 = math.sqrt(k / (k - 1) * x ** (2 / k) * (1 - x ** ((k - 1) / k)) / (1 - x))
        api = 17.9 * W / (F2 * 0.975) * math.sqrt(T * Z / (M * P1 * (P1 - P2)))
        self.assertEqual(r.regime, "subcritical")
        self.assertAlmostEqual(r.required_area_mm2 / api, 1, delta=0.005)

    def test_liquid_matches_api_11_78(self):
        r = relief.liquid_area(60.0, 850, 1500, 101.325, mu_cP=0.5)
        Qlpm = 60e3 / 60
        api = 11.78 * Qlpm / (0.65 * r.detail["Kv"]) * math.sqrt(0.85 / (1500 - 101.325))
        self.assertAlmostEqual(r.required_area_mm2 / api, 1, delta=0.005)
        self.assertLessEqual(r.detail["Kv"], 1.0)

    def test_viscous_liquid_needs_more_area(self):
        a = relief.liquid_area(5.0, 900, 1500, 101.325, mu_cP=1).required_area_mm2
        b = relief.liquid_area(5.0, 900, 1500, 101.325, mu_cP=500).required_area_mm2
        self.assertGreater(b, a)

    def test_steam_si_constant_equals_us_unit_conversion(self):
        W_kg, P_kpa = 10000, 2000
        A_us = (W_kg / 0.45359237) / (51.5 * P_kpa / 6.894757 * 0.975) * 645.16
        self.assertAlmostEqual(relief.steam_area(W_kg, P_kpa).required_area_mm2 / A_us, 1, delta=0.005)

    def test_napier_continuous_at_boundary(self):
        lo = relief.steam_area(1e4, 10339).detail["Kn"]; hi = relief.steam_area(1e4, 10340).detail["Kn"]
        self.assertAlmostEqual(lo, hi, delta=0.01)

    def test_orifice_selection_and_multiple(self):
        self.assertEqual(relief.select_orifice(60)[0], "D")
        self.assertEqual(relief.select_orifice(100)[0], "E")
        self.assertEqual(relief.select_orifice(1000)[0], "K")
        self.assertEqual(relief.select_orifice(40000), ("T", 3))

    def test_fire_heat_input(self):
        self.assertAlmostEqual(relief.fire_heat_input_W(100) / 1e6, 43200 * 100 ** 0.82 / 1e6)
        self.assertGreater(relief.fire_heat_input_W(50, adequate_drainage_and_firefighting=False), relief.fire_heat_input_W(50))

    def test_wetted_area_limits(self):
        full = relief.wetted_area_cylinder(2.0, 6.0, 2.0)
        half = relief.wetted_area_cylinder(2.0, 6.0, 1.0)
        self.assertGreater(full, half)
        self.assertAlmostEqual(relief.wetted_area_cylinder(2.0, 20.0, 15.0, "vertical"), math.pi * 2 * 7.6 + 1.084 * 4)
        self.assertEqual(relief.wetted_area_cylinder(2, 6, 0), 0.0)

    def test_back_pressure_warning(self):
        r = relief.gas_area(5000, 350, 1100, 700, 30, 1.3, set_g_kpa=1000)
        self.assertTrue(any("back pressure" in n for n in r.notes))

    def test_governing(self):
        a = relief.gas_area(1000, 300, 1000, 101.3, 20, 1.3); b = relief.gas_area(9000, 300, 1000, 101.3, 20, 1.3)
        self.assertIs(relief.governing_case({"blocked": a, "fire": b})[1], b)


class Flare(unittest.TestCase):
    def test_radiant_fraction_values(self):
        self.assertAlmostEqual(flare.radiant_fraction(16), 0.192, places=3)
        self.assertAlmostEqual(flare.radiant_fraction(44), 0.318, places=3)
        self.assertEqual(flare.radiant_fraction(200), 0.40)

    def test_distance_radiation_roundtrip(self):
        Q = 5e7
        d = flare.safe_distance_m(Q, 4.73, 0.2)
        self.assertAlmostEqual(flare.radiation_kW_m2(Q, d, 0.2), 4.73, places=6)

    def test_inverse_square(self):
        self.assertAlmostEqual(flare.radiation_kW_m2(1e7, 10, .2) / flare.radiation_kW_m2(1e7, 20, .2), 4)

    def test_point_source_warning(self):
        c = flare.radiation_checks(1e6, 0.2, flame_length_m=50)
        self.assertTrue(c["warnings"])

    def test_tip_diameter_scales(self):
        d1 = flare.tip_diameter_m(10, 20, 300, 1.3, 0.5); d2 = flare.tip_diameter_m(40, 20, 300, 1.3, 0.5)
        self.assertAlmostEqual(d2 / d1, 2, places=6)


class SIL(unittest.TestCase):
    def test_pfd_1oo1(self):
        self.assertAlmostEqual(sil.pfd_avg("1oo1", 2e-6, 8760), 2e-6 * 8760 / 2)

    def test_redundant_matches_numerical_average(self):
        lam, ti = 1e-6, 8760
        p = lambda t: 1 - math.exp(-lam * t)
        self.assertAlmostEqual(sil.pfd_avg("1oo2", lam, ti) / lam_avg(lambda t: p(t) ** 2, ti), 1, delta=0.01)
        self.assertAlmostEqual(sil.pfd_avg("2oo3", lam, ti) / lam_avg(lambda t: 3 * p(t) ** 2 - 2 * p(t) ** 3, ti), 1, delta=0.02)  # simplified form is slightly conservative
        self.assertAlmostEqual(sil.pfd_avg("2oo2", lam, ti) / lam_avg(lambda t: 1 - (1 - p(t)) ** 2, ti), 1, delta=0.01)

    def test_beta_dominates_redundant(self):
        self.assertGreater(sil.pfd_avg("1oo2", 1e-6, 8760, beta=0.1), 5 * sil.pfd_avg("1oo2", 1e-6, 8760))

    def test_bands(self):
        self.assertEqual(sil.sil_for_pfd(5e-2), "SIL 1"); self.assertEqual(sil.sil_for_pfd(5e-3), "SIL 2")
        self.assertEqual(sil.sil_for_pfd(5e-4), "SIL 3"); self.assertEqual(sil.sil_for_pfd(0.5), "below SIL 1")

    def test_lopa(self):
        r = sil.lopa(0.1, [0.1, 0.01], 1e-5)
        self.assertAlmostEqual(r.mitigated_per_yr, 1e-4); self.assertAlmostEqual(r.required_pfd, 0.1)
        self.assertEqual(r.sil_needed, "below SIL 1")
        r2 = sil.lopa(0.1, [0.1], 1e-6)
        self.assertAlmostEqual(r2.required_pfd, 1e-4); self.assertEqual(r2.sil_needed, "SIL 3")
        self.assertTrue(sil.lopa(1e-3, [0.1], 1e-3).meets_target_without_sif)

    def test_proof_test_interval_inverse(self):
        ti = sil.max_proof_test_interval_h("1oo1", 1e-6, 1e-2)
        self.assertAlmostEqual(sil.pfd_avg("1oo1", 1e-6, ti), 1e-2, places=6)

    def test_sif_sum(self):
        self.assertEqual(sil.sif_pfd({"s": 1e-3, "l": 1e-4, "fe": 5e-3})[1], "SIL 2")


class Fireball(unittest.TestCase):
    def test_scaling_and_energy(self):
        fb = fireball.fireball(10_000, 46)
        self.assertAlmostEqual(fb["diameter_m"], 5.8 * 10_000 ** (1 / 3))
        # radiated energy = SEP * surface * duration = fraction * m * Hc
        E = fb["surface_emissive_power_kW_m2"] * 1e3 * math.pi * fb["diameter_m"] ** 2 * fb["duration_s"]
        self.assertAlmostEqual(E / (0.3 * 10_000 * 46e6), 1, places=9)

    def test_flux_decays_with_distance(self):
        fb = fireball.fireball(10_000, 46)
        self.assertGreater(fireball.incident_kW_m2(fb, 150), fireball.incident_kW_m2(fb, 400))
        d = fireball.distance_to_flux_m(fb, 12.5)
        self.assertAlmostEqual(fireball.incident_kW_m2(fb, d), 12.5, places=3)

    def test_large_mass_duration_branch(self):
        self.assertAlmostEqual(fireball.fireball(1e5, 46)["duration_s"], 2.6 * 1e5 ** (1 / 6))


class Standards(unittest.TestCase):
    def test_oisd_lookup(self):
        self.assertEqual(standards.oisd_lookup("OISD-STD-106")["title"], "Pressure Relief & Disposal System")
        self.assertEqual(standards.oisd()["count"], 105)


if __name__ == "__main__":
    unittest.main()


class TankVenting(unittest.TestCase):
    def setUp(self):
        from process_safety import tank_venting as tv
        self.tv = tv

    def test_table_2b_anchors_and_interpolation(self):
        t = self.tv.thermal_venting(1000, False)
        self.assertEqual((t["inbreathing_Nm3h"], t["outbreathing_Nm3h"]), (169, 101))
        self.assertEqual(self.tv.thermal_venting(1000, True)["outbreathing_Nm3h"], 169)
        self.assertAlmostEqual(self.tv.thermal_venting(1250, False)["inbreathing_Nm3h"], (169 + 253) / 2)
        with self.assertRaises(ValueError):
            self.tv.thermal_venting(30001, False)

    def test_normal_is_sum_of_liquid_and_thermal(self):
        n = self.tv.normal_venting(1000, 100, 150, volatile=False)
        self.assertAlmostEqual(n["outbreathing_Nm3h"], 1.01 * 100 + 101)
        self.assertAlmostEqual(n["inbreathing_Nm3h"], 0.94 * 150 + 169)
        v = self.tv.normal_venting(1000, 100, 150, volatile=True)
        self.assertAlmostEqual(v["outbreathing_Nm3h"], 2.02 * 100 + 169)

    def test_eq_1b_reproduces_table_3b(self):
        for A, tab in self.tv._T3B:
            eq = self.tv.fire_venting_Nm3h(A, design_barg=0.5)
            # printed-table quirks: 110 m2 (15,461) is ~4% above Eq 1B; 19 m2 (5,780) follows the linear tier 63,150 A, ~1.1% above
            tol = {110: 0.05, 19: 0.015}.get(A, 0.01)
            self.assertAlmostEqual(eq / tab, 1, delta=tol, msg=f"A={A}")

    def test_constant_208_2_and_19910(self):
        A = 500.0
        self.assertAlmostEqual(self.tv.fire_venting_Nm3h(A, design_barg=0.5) / A ** 0.82, 208.2, delta=0.1)
        self.assertAlmostEqual(self.tv.fire_venting_Nm3h(300, design_barg=0.05) / 19910, 1, delta=0.005)
        self.assertEqual(self.tv.fire_venting_simplified(300, design_barg=0.05), 19910)

    def test_heat_input_continuity_between_tiers(self):
        for A in (18.6, 93, 260):
            lo = self.tv.fire_heat_input_W(A * (1 - 1e-6), 0.5); hi = self.tv.fire_heat_input_W(A * (1 + 1e-6), 0.5)
            self.assertAlmostEqual(lo / hi, 1, delta=0.005)

    def test_F_scales_and_pressure_limit(self):
        self.assertAlmostEqual(self.tv.fire_venting_Nm3h(50, 0.3) / self.tv.fire_venting_Nm3h(50), 0.3)
        with self.assertRaises(ValueError):
            self.tv.fire_heat_input_W(50, 2.0)

    def test_wetted_area(self):
        self.assertAlmostEqual(self.tv.wetted_area_m2("sphere", 10), math.pi * 10 * 9.14)
        self.assertAlmostEqual(self.tv.wetted_area_m2("sphere", 30), 0.55 * math.pi * 900)
        self.assertAlmostEqual(self.tv.wetted_area_m2("vertical", 20, 15), math.pi * 20 * 9.14)
        self.assertAlmostEqual(self.tv.wetted_area_m2("vertical", 20, 5), math.pi * 20 * 5)
        h = self.tv.wetted_area_m2("horizontal", 3, 12)
        self.assertGreaterEqual(h, 0.75 * (math.pi * 3 * 12 + math.pi * 9 / 2))

    def test_shortfall(self):
        self.assertEqual(self.tv.emergency_vent_shortfall_Nm3h(10000, 4000), 6000)
        self.assertEqual(self.tv.emergency_vent_shortfall_Nm3h(3000, 4000), 0)


class VapourFire(unittest.TestCase):
    def setUp(self):
        from process_safety import vapour_fire as vf
        self.vf = vf
        self.base = dict(volume_m3=15.0, exposed_area_m2=36.0, diameter_m=2.0, wall_mm=20.0, M=20.0, k=1.3, P0_kpag=1000.0)

    def V(self, **kw):
        return self.vf.Vessel(**{**self.base, **kw})

    def test_ky_anchors(self):
        self.assertEqual(self.vf.ky(293.15), 1.0)
        self.assertAlmostEqual(self.vf.ky(600 + 273.15), 0.47)
        self.assertAlmostEqual(self.vf.ky(550 + 273.15), (0.78 + 0.47) / 2)
        self.assertEqual(self.vf.ky(1300 + 273.15), 0.0)

    def test_no_fire_nothing_happens(self):
        r = self.vf.simulate(self.V(), 0.0, t_end_s=600)
        self.assertTrue(r.protected); self.assertAlmostEqual(r.peak_pressure_kpag, 1000.0, places=6)
        self.assertEqual(r.mass_discharged_kg, 0.0)

    def test_radiative_equilibrium_wall_temperature(self):
        r = self.vf.simulate(self.V(wall_mm=10, P0_kpag=0.0, strength_MPa=1e6), 100.0, h_in=0.0, t_end_s=4000)
        eq = (100e3 / (0.8 * self.vf.SIGMA) + 323.15 ** 4) ** 0.25
        self.assertAlmostEqual(r.peak_wall_K / eq, 1, delta=0.01)

    def test_psv_limits_pressure_and_discharges(self):
        strong = dict(strength_MPa=1e6)
        no = self.vf.simulate(self.V(**strong), 100.0, t_end_s=900)
        yes = self.vf.simulate(self.V(**strong), 100.0, psv_area_mm2=300, psv_set_kpag=1500, t_end_s=900)
        self.assertGreater(no.peak_pressure_kpag, yes.peak_pressure_kpag)
        self.assertGreater(yes.mass_discharged_kg, 0); self.assertIsNotNone(yes.t_relief_onset_s)
        self.assertLess(yes.peak_pressure_kpag, 1500 * 1.15)

    def test_thin_wall_fails_earlier(self):
        thin = self.vf.simulate(self.V(wall_mm=10), 100.0, t_end_s=3000)
        thick = self.vf.simulate(self.V(wall_mm=40), 100.0, t_end_s=3000)
        self.assertIsNotNone(thin.t_rupture_s)
        self.assertTrue(thick.t_rupture_s is None or thick.t_rupture_s > thin.t_rupture_s)

    def test_blowdown_lowers_pressure(self):
        a = self.vf.simulate(self.V(strength_MPa=1e6), 100.0, t_end_s=600)
        b = self.vf.simulate(self.V(strength_MPa=1e6), 100.0, bdv_area_mm2=600, bdv_open_s=60, t_end_s=600)
        self.assertLess(b.final_pressure_kpag, 0.5 * a.final_pressure_kpag)

    def test_rupture_before_relief_note(self):
        r = self.vf.simulate(self.V(wall_mm=8, P0_kpag=1400.0), 150.0, psv_area_mm2=300, psv_set_kpag=2500, t_end_s=3000)
        if r.t_rupture_s is not None and r.t_relief_onset_s is None:
            self.assertTrue(any("BEFORE" in n for n in r.notes))


class Scenarios(unittest.TestCase):
    def test_thermal_expansion(self):
        from process_safety import scenarios as sc
        self.assertAlmostEqual(sc.thermal_expansion_relief_m3h(1000, 1e-3, 800, 2000), 6.25e-7 * 3600)

    def test_10_13_rule(self):
        from process_safety import scenarios as sc
        self.assertTrue(sc.tube_rupture_exempt(1300, 1000)); self.assertFalse(sc.tube_rupture_exempt(1300, 900))

    def test_tube_rupture_flows(self):
        from process_safety import scenarios as sc
        liq = sc.tube_rupture_flow_kg_s(0.019, 3000, 500, "liquid", rho=800)
        self.assertAlmostEqual(liq, 0.62 * 2 * math.pi * 0.019 ** 2 / 4 * math.sqrt(2 * 800 * 2500e3))
        gas = sc.tube_rupture_flow_kg_s(0.019, 3000, 101.325, "gas", T_K=350, M=20, k=1.3)
        G, _ = relief.gas_mass_flux(3000, 101.325, 350, 20, 1.3)
        self.assertAlmostEqual(gas, 0.62 * 2 * math.pi * 0.019 ** 2 / 4 * G)

    def test_header_mach_roundtrip(self):
        from process_safety import scenarios as sc
        D = sc.flare_header_diameter_m(30, 150, 320, 28, 1.3, 0.5)
        rho = 150e3 * 0.028 / (8.314462618 * 320); c = math.sqrt(1.3 * 8.314462618 * 320 / 0.028)
        self.assertAlmostEqual(rho * 0.5 * c * math.pi * D * D / 4, 30, places=6)

    def test_catalogue(self):
        from process_safety import scenarios as sc
        self.assertIn("External fire (vapour-filled)", sc.SCENARIOS)


class Separator(unittest.TestCase):
    def test_droplet_velocity_limits(self):
        from process_safety import separator as sp
        stokes = 1000 * 9.80665 * (20e-6) ** 2 / (18 * 1.8e-5)
        self.assertAlmostEqual(sp.droplet_terminal_velocity(20, 1000, 1.2, 1.8e-5) / stokes, 1, delta=0.03)
        self.assertTrue(0.9 < sp.droplet_terminal_velocity(300, 1000, 1.2, 1.8e-5) < 1.7)

    def test_souders_brown(self):
        from process_safety import separator as sp
        self.assertAlmostEqual(sp.souders_brown_velocity(800, 20, 0.0762), 0.0762 * math.sqrt(780 / 20))

    def test_vertical(self):
        from process_safety import separator as sp
        r = sp.vertical_separator(0.8, 0.004, 800, 20)
        self.assertLessEqual(r["actual_gas_velocity_m_s"], r["design_gas_velocity_m_s"] + 1e-9)
        self.assertAlmostEqual(r["liquid_height_m"], 300 * 0.004 / (math.pi * r["diameter_m"] ** 2 / 4))

    def test_horizontal(self):
        from process_safety import separator as sp
        r = sp.horizontal_separator(1.5, 0.006, 800, 20)
        self.assertLessEqual(r["gas_velocity_m_s"], r["design_gas_velocity_m_s"])
        self.assertTrue(2.5 <= r["L_over_D"] <= 5.01)

    def test_knockout(self):
        from process_safety import separator as sp
        k = sp.knockout_drum_vertical(3.0, 700, 5.0, 1.0e-5)
        self.assertLessEqual(3.0 / (math.pi * k["diameter_m"] ** 2 / 4), k["settling_velocity_m_s"] + 1e-9)

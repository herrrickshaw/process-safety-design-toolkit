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


class Hydraulics(unittest.TestCase):
    def setUp(self):
        from process_safety import hydraulics as hy, fire_water as fw, vessel_mech as vm
        self.hy, self.fw, self.vm = hy, fw, vm

    def test_friction_factor_limits(self):
        self.assertAlmostEqual(self.hy.friction_factor(1000, 0.1), 0.064)
        f = self.hy.friction_factor(1e5, 0.1, 0.0)  # smooth pipe Re=1e5: Blasius-ish 0.018
        self.assertTrue(0.0175 < f < 0.0185)
        D, eps = 0.1, 4.6e-5; Re = 3e5; f = self.hy.friction_factor(Re, D, eps)
        lhs = 1 / math.sqrt(f); rhs = -2 * math.log10(eps / (3.7 * D) + 2.51 / (Re * math.sqrt(f)))
        self.assertAlmostEqual(lhs, rhs, places=8)

    def test_incompressible_dp_components(self):
        r = self.hy.incompressible_dp_kpa(0.01, 0.1, 100, 1000, 1e-3, K_total=3, dz=5)
        self.assertAlmostEqual(r["dp_static_kPa"], 1000 * 9.80665 * 5 / 1e3)
        self.assertAlmostEqual(r["dp_total_kPa"], r["dp_friction_kPa"] + r["dp_fittings_kPa"] + r["dp_static_kPa"])
        self.assertAlmostEqual(r["dp_fittings_kPa"], 3 * 1000 * r["velocity_m_s"] ** 2 / 2 / 1e3)

    def test_isothermal_gas_equation_residual_and_limit(self):
        r = self.hy.isothermal_gas_outlet_kpa(2.0, 0.2, 500, 1000, 300, 20, 1.1e-5)
        Rs = 8.314462618 / 0.020; Gm = 2.0 / (math.pi * 0.04 / 4)
        P1, P2 = 1e6, r["P2_kPa"] * 1e3
        res = P1 ** 2 - P2 ** 2 - Gm ** 2 * Rs * 300 * (r["f"] * 500 / 0.2 + 2 * math.log(P1 / P2))
        self.assertAlmostEqual(res / P1 ** 2, 0, places=9)
        short = self.hy.isothermal_gas_outlet_kpa(0.2, 0.3, 10, 1000, 300, 20, 1.1e-5)
        self.assertLess(short["dp_kPa"], 5)
        with self.assertRaises(ValueError):
            self.hy.isothermal_gas_outlet_kpa(50, 0.1, 5000, 500, 300, 20, 1.1e-5)

    def test_erosional_conversion(self):
        self.assertAlmostEqual(self.hy.erosional_velocity_m_s(1000), 122 / math.sqrt(1000) * 1.0, delta=0.05 * 122 / math.sqrt(1000) + 0.01)
        self.assertAlmostEqual(self.hy.erosional_velocity_m_s(800) / self.hy.erosional_velocity_m_s(200), 0.5)

    def test_control_valve(self):
        self.assertAlmostEqual(self.hy.kv_liquid(100, 1000, 1.0), 100.0)
        self.assertAlmostEqual(self.hy.kv_liquid(100, 800, 4.0), 100 * math.sqrt(0.8 / 4))
        dp = self.hy.liquid_choked_dp_bar(10, 1, 50, FL=0.9)
        self.assertAlmostEqual(dp, 0.81 * (10 - (0.96 - 0.28 * math.sqrt(1 / 50)) * 1))

    def test_pump(self):
        self.assertAlmostEqual(self.hy.npsha_m(101.325, 3.17, 1000, 2.0, 0.5), (101.325 - 3.17) * 1e3 / (1000 * 9.80665) + 1.5)
        self.assertAlmostEqual(self.hy.pump_hydraulic_kW(36, 50, 1000), 1000 * 9.80665 * 0.01 * 50 / 1e3)
        a = self.hy.pump_affinity(100, 50, 20, 1450, 2900)
        self.assertEqual((a["Q"], a["H"], a["P"]), (200, 200, 160))

    def test_water_hammer(self):
        a = self.hy.wave_speed_m_s(2.2e9, 1000, 0.5, 0.01, 2.0e11)
        self.assertTrue(900 < a < 1300)
        self.assertAlmostEqual(self.hy.wave_speed_m_s(2.2e9, 1000, 0.5, 1e6, 2e11), math.sqrt(2.2e9 / 1000), places=2)
        s = self.hy.surge_screen(1000, a, 0.5 * 2 * 1000 / a, 1000, 2.0)
        self.assertTrue(s["rapid_closure"]); self.assertAlmostEqual(s["estimated_kPa"], 1000 * a * 2.0 / 1e3)
        slow = self.hy.surge_screen(1000, a, 4 * 2 * 1000 / a, 1000, 2.0)
        self.assertAlmostEqual(slow["estimated_kPa"], slow["joukowsky_kPa"] / 4)

    def test_hazen_williams_vs_darcy(self):
        hw = self.fw.hazen_williams_bar_per_m(1000, 100, 140) * 1e5  # Pa/m
        d = self.hy.incompressible_dp_kpa(1000 / 60000, 0.1, 1, 1000, 1.0e-3, eps=1.5e-6)["dp_friction_kPa"] * 1e3
        self.assertAlmostEqual(hw / d, 1, delta=0.25)
        self.assertAlmostEqual(self.fw.hazen_williams_bar_per_m(2000, 100, 120) / self.fw.hazen_williams_bar_per_m(1000, 100, 120), 2 ** 1.85)

    def test_fire_water_demand(self):
        self.assertAlmostEqual(self.fw.nozzle_flow_lpm(25, 3.5), 0.97 * math.pi * 0.025 ** 2 / 4 * math.sqrt(2 * 3.5e5 / 1000) * 60000)
        d = self.fw.demand_summary({"tank": 3000, "pump": 1200}, ["tank", "pump"], 4, 500)
        self.assertEqual(d["design_flow_lpm"], 4700); self.assertAlmostEqual(d["storage_m3"], 4700 * 0.06 * 4)

    def test_vessel_mechanical(self):
        t = self.vm.cylinder_thickness_mm(1500, 1000, 138, 0.85, 3)
        self.assertAlmostEqual(t["t_circumferential_mm"], 1.5 * 1000 / (138 * 0.85 - 0.9))
        self.assertGreater(t["t_circumferential_mm"], t["t_longitudinal_mm"])
        mawp = self.vm.cylinder_mawp_kpag(t["t_required_mm"], 1000, 138, 0.85)
        self.assertAlmostEqual(mawp, 1500, delta=1)
        h = self.vm.ellipsoidal_head_thickness_mm(1500, 2000, 138, 0.85)
        self.assertAlmostEqual(h, 1.5 * 2000 / (2 * 138 * 0.85 - 0.3))
        self.assertAlmostEqual(self.vm.hydrotest_kpag(1500), 1950)
        self.assertAlmostEqual(self.vm.liquid_inventory_m3(2, 10, 0.5), math.pi * 1 * 10 / 2)
        with self.assertRaises(ValueError):
            self.vm.cylinder_thickness_mm(60000, 1000, 138, 1.0)


class Consequence(unittest.TestCase):
    def setUp(self):
        from process_safety import release, dispersion, explosion, consequence
        self.rl, self.dp, self.ex, self.cq = release, dispersion, explosion, consequence

    def test_release_basic(self):
        self.assertAlmostEqual(self.rl.liquid_release_kg_s(0.025, 800, 2e5, 2.0), 0.62 * math.pi * 0.025 ** 2 / 4 * math.sqrt(2 * 800 * (2e5 + 800 * 9.80665 * 2)))
        G, _ = relief.gas_mass_flux(1000, 101.325, 300, 20, 1.3)
        self.assertAlmostEqual(self.rl.gas_release_kg_s(0.01, 1000, 300, 20, 1.3), 0.85 * math.pi * 0.01 ** 2 / 4 * G)
        self.assertAlmostEqual(self.rl.tank_drain_time_s(10, 0.05, 5), 10 / (0.62 * math.pi * 0.05 ** 2 / 4) * math.sqrt(2 * 5 / 9.80665))

    def test_blowdown_matches_analytic_while_choked(self):
        V, P0, T0, M, k, d = 20.0, 2000.0, 300.0, 20.0, 1.3, 0.05
        r = self.rl.blowdown_adiabatic(V, P0, T0, M, k, d, t_end_s=5.0, dt=0.01)
        # compare mass released over first 5 s with the closed form pressure ratio (mass ratio = (P/P0)^(1/k))
        pr = self.rl.blowdown_adiabatic_analytic_P_ratio(5.0, V, P0, T0, M, k, d)
        self.assertAlmostEqual(r["released_kg"] / r["initial_mass_kg"], 1 - pr ** (1 / k), delta=0.002)
        full = self.rl.blowdown_adiabatic(V, P0, T0, M, k, d, t_end_s=3000)
        self.assertLess(full["released_kg"], full["initial_mass_kg"]); self.assertGreater(full["released_kg"], 0.9 * full["initial_mass_kg"] * (1 - 101.325 / P0))

    def test_sigmas_and_mass_conservation(self):
        sy, sz = self.dp.sigmas(500, "D")
        self.assertAlmostEqual(sz, 0.06 * 500 * (1 + 0.0015 * 500) ** -0.5)
        Q, u, H, x = 10.0, 3.0, 25.0, 800.0
        sy, sz = self.dp.sigmas(x, "D")
        n = 4000; ymax = 8 * sy; dy = 2 * ymax / n
        iy = sum(self.dp.concentration_g_m3(Q, u, H, x, -ymax + i * dy, 0.0) for i in range(n + 1)) * dy
        self.assertAlmostEqual(iy, Q / u * 2 * math.exp(-H * H / (2 * sz * sz)) / (math.sqrt(2 * math.pi) * sz), delta=1e-3 * iy)
        nz = 4000; zmax = 10 * sz + H; dz = zmax / nz
        iz = sum(self.dp.concentration_g_m3(Q, u, H, x, 0.0, i * dz) for i in range(nz + 1)) * dz  # centreline y=0
        flux = iz * math.sqrt(2 * math.pi) * sy * u  # integrate lateral analytically
        self.assertAlmostEqual(flux, Q, delta=2e-3 * Q)

    def test_plume_rise_and_max(self):
        F = self.dp.buoyancy_flux(15, 2, 450, 293)
        self.assertGreater(F, 0)
        self.assertGreater(self.dp.plume_rise_m(F, 3), self.dp.plume_rise_m(F, 6))
        self.assertGreater(self.dp.plume_rise_m(F, 3, "D"), 0); self.assertGreater(self.dp.plume_rise_m(F, 3, "F"), 0)
        low = self.dp.max_ground_concentration(10, 3, 10)[0]; high = self.dp.max_ground_concentration(10, 3, 60)[0]
        self.assertGreater(low, high)
        c, x = self.dp.max_ground_concentration(10, 3, 30)
        self.assertAlmostEqual(self.dp.distance_to_threshold_m(10, 3, 30, c * 0.999999) is not None, True)
        self.assertIsNone(self.dp.distance_to_threshold_m(10, 3, 30, c * 2))

    def test_ppm_roundtrip(self):
        self.assertAlmostEqual(self.dp.mg_m3_to_ppm(self.dp.ppm_to_mg_m3(100, 34.08), 34.08), 100)
        self.assertAlmostEqual(self.dp.ppm_to_mg_m3(1, 24.45 * 1.0, 298.15), 24.45 * 101.325 / (8.314462618 * 298.15), places=6)

    def test_explosion(self):
        self.assertAlmostEqual(self.ex.tnt_equivalent_kg(1000, 46, 0.05, 4.5), 0.05 * 1000 * 46 / 4.5)
        W = 1000.0
        p10 = self.ex.kinney_graham_kpa(W, 10 * W ** (1 / 3)); p4 = self.ex.kinney_graham_kpa(W, 4 * W ** (1 / 3))
        self.assertTrue(8 < p10 < 12); self.assertTrue(40 < p4 < 50); self.assertGreater(p4, p10)
        R = self.ex.distance_for_overpressure_m(W, 21)
        self.assertAlmostEqual(self.ex.kinney_graham_kpa(W, R), 21, places=4)
        E = self.ex.brode_burst_energy_J(2000, 101.325, 10, 1.4)
        self.assertAlmostEqual(E, (2000 - 101.325) * 1e3 * 10 / 0.4)
        self.assertAlmostEqual(self.ex.burst_tnt_equivalent_kg(E, 4.5, True), 2 * E / 4.5e6)

    def test_probits(self):
        self.assertAlmostEqual(self.cq.fraction_from_probit(5.0), 0.5)
        self.assertAlmostEqual(self.cq.fraction_from_probit(self.cq.probit_from_fraction(0.1)), 0.1, places=9)
        t = self.cq.time_to_fraction_thermal_s(12.5, 0.5)
        self.assertAlmostEqual(self.cq.fraction_from_probit(self.cq.probit_thermal(12.5, t)), 0.5, places=6)
        self.assertLess(self.cq.time_to_fraction_thermal_s(37.5), self.cq.time_to_fraction_thermal_s(12.5))
        c = self.cq.concentration_for_fraction_ppm("chlorine", 30, 0.5)
        self.assertAlmostEqual(self.cq.fraction_from_probit(self.cq.probit_toxic_named("chlorine", c, 30)), 0.5, places=6)
        self.assertTrue(100 < c < 2000)


class Reliability(unittest.TestCase):
    def setUp(self):
        from process_safety import reliability as rb, hazop, emissions, reaction_hazard
        self.rb, self.hz, self.em, self.rx = rb, hazop, emissions, reaction_hazard

    def test_availability_and_koon(self):
        self.assertAlmostEqual(self.rb.availability(900, 100), 0.9)
        self.assertAlmostEqual(self.rb.parallel_availability([0.9, 0.9]), 0.99)
        self.assertAlmostEqual(self.rb.series_availability([0.9, 0.9]), 0.81)
        p = 0.1
        self.assertAlmostEqual(self.rb.koon_failure_probability(1, 2, p), p ** 2)
        self.assertAlmostEqual(self.rb.koon_failure_probability(2, 3, p), 3 * p ** 2 * (1 - p) + p ** 3)
        self.assertAlmostEqual(self.rb.koon_failure_probability(2, 2, p), 1 - (1 - p) ** 2)

    def test_fault_tree_exact_with_repeated_event(self):
        ft = self.rb.FaultTree().event("A", .1).event("B", .2).event("C", .3)
        ft.gate("AB", "AND", ["A", "B"]).gate("AC", "AND", ["A", "C"]).gate("TOP", "OR", ["AB", "AC"])
        self.assertAlmostEqual(ft.probability("TOP"), .1 * (.2 + .3 - .2 * .3))
        self.assertEqual(ft.minimal_cut_sets("TOP"), [frozenset({"A", "B"}), frozenset({"A", "C"})])
        b = ft.birnbaum("TOP")
        self.assertAlmostEqual(b["A"], .2 + .3 - .06)
        self.assertGreater(b["A"], b["B"])

    def test_vote_gate_matches_binomial(self):
        ft = self.rb.FaultTree()
        for n in "XYZ":
            ft.event(n, .1)
        ft.gate("TOP", "VOTE", ["X", "Y", "Z"], k=2)
        self.assertAlmostEqual(ft.probability("TOP"), self.rb.koon_failure_probability(2, 3, .1))
        self.assertEqual(len(ft.minimal_cut_sets("TOP")), 3)

    def test_event_tree_conserves_frequency(self):
        out = self.rb.event_tree(0.1, [("PSV", .99), ("Operator", .9), ("SIS", .99)])
        self.assertEqual(len(out), 8); self.assertAlmostEqual(sum(o["frequency_per_yr"] for o in out), 0.1)
        self.assertAlmostEqual(next(o for o in out if all(v == "fails" for v in o["path"].values()))["frequency_per_yr"], .1 * .01 * .1 * .01)

    def test_fmea_and_matrix(self):
        self.assertEqual(self.rb.rpn(8, 5, 4), 160)
        self.assertEqual(self.rb.risk_rank(5, 5), (25, "extreme")); self.assertEqual(self.rb.risk_rank(1, 2)[1], "low")

    def test_hazop_generation_and_csv(self):
        import csv, os, tempfile
        rows = self.hz.generate("Node 1", "Feed naphtha to surge drum", ["Flow", "Pressure"])
        self.assertEqual(len(rows), 6 + 2)
        self.assertIn("Control valve fails closed", rows[0]["Causes (prompts)"])
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "h.csv"); self.assertEqual(self.hz.to_csv(rows, p), 8)
            with open(p, encoding="utf-8-sig") as fh:
                back = list(csv.DictReader(fh))
            self.assertEqual(back[0]["Deviation"], "No flow"); self.assertEqual(list(back[0].keys()), self.hz.COLUMNS)
        for (param, gw) in self.hz.CAUSES:
            self.assertIn(gw, self.hz.DEVIATIONS[param])

    def test_emissions(self):
        self.assertAlmostEqual(self.em.molar_mass("CH4"), 16.043, places=3)
        self.assertAlmostEqual(self.em.co2_per_kg_fuel("CH4"), 44.009 / 16.043, places=4)
        self.assertAlmostEqual(self.em.co2_per_kg_fuel("C3H8"), 3 * 44.009 / 44.097, places=3)
        r = self.em.flare_emissions(1000, 0.75, 0.98)
        self.assertAlmostEqual(r["co2_kg"], 1000 * .98 * .75 * 44.009 / 12.011)
        self.assertAlmostEqual(r["co2e_kg"], r["co2_kg"] + 20 * 28)
        self.assertAlmostEqual(self.em.sox_from_sulfur_kg(1000, 0.01), 10 * (32.06 + 2 * 15.999) / 32.06)

    def test_reaction_hazard(self):
        dT = self.rx.adiabatic_temperature_rise_K(-100, 2.0, 1000, 2.0)  # 100 kJ/mol, 2 mol/L
        self.assertAlmostEqual(dT, 100 * 2.0 * 1000 / (1000 * 2.0))
        self.assertAlmostEqual(self.rx.mtsr_C(80, dT, 0.3), 80 + 30)
        s = self.rx.screen(80, dT, 1.0, 100, 150, 120)
        self.assertTrue(any("boiling" in f for f in s["flags"])); self.assertTrue(any("TD24" in f for f in s["flags"]))
        self.assertTrue(any("MTT" in f for f in s["flags"]))  # MTSR 180 C > MTT 150 C
        ok = self.rx.screen(80, dT, 0.1, 200, 150, 120)  # MTSR 90 C: below everything
        self.assertEqual(len(ok["flags"]), 1); self.assertIn("below", ok["flags"][0])
        self.assertFalse(any("MTT" in f for f in self.rx.screen(80, dT, 1.0, 100, 200, 120)["flags"]))


class MoreCases(unittest.TestCase):
    def setUp(self):
        from process_safety import pool_fire, flammability, structural_fire
        self.pf, self.fl, self.sf = pool_fire, flammability, structural_fire

    def test_pool_fire_basics(self):
        m = self.pf.burning_rate_kg_m2_s(44_000, 350, 2.2, 400, 298.15)
        self.assertAlmostEqual(m, 0.001 * 44000 / (350 + 2.2 * 101.85))
        self.assertAlmostEqual(self.pf.burning_rate_kg_m2_s(50_000, 510, 3.5, 111.7), 0.001 * 50000 / 510)  # cryogenic: no sensible term
        D = 20.0
        H = self.pf.flame_height_m(D, 0.08)
        self.assertAlmostEqual(H / D, 42 * (0.08 / (1.2 * math.sqrt(9.80665 * D))) ** 0.61)
        self.assertTrue(1.0 < H / D < 4.0)
        self.assertTrue(20 < self.pf.mudan_croce_sep_kW_m2(50) < 60); self.assertGreater(self.pf.mudan_croce_sep_kW_m2(5), self.pf.mudan_croce_sep_kW_m2(50))

    def test_pool_fire_radiation(self):
        pf = self.pf.pool_fire(300, 44_000, 350, 2.2, 400)
        self.assertAlmostEqual(pf["Q_kW"], pf["mass_burn_rate_kg_s"] * 44_000)
        far = pf["flame_height_m"] * 5
        self.assertAlmostEqual(self.pf.incident_kW_m2(pf, far) / self.pf.incident_kW_m2(pf, 2 * far), 4, delta=0.9)
        d = self.pf.distance_to_flux_m(pf, 4.73)
        self.assertAlmostEqual(self.pf.incident_kW_m2(pf, d), 4.73, places=5)

    def test_flammability(self):
        self.assertAlmostEqual(self.fl.le_chatelier([0.5, 0.5], [5.0, 2.0]), 1 / (0.5 / 5 + 0.5 / 2))
        self.assertAlmostEqual(self.fl.le_chatelier([1, 1], [5.0, 5.0]), 5.0)
        self.assertAlmostEqual(self.fl.oxygen_stoich_z("CH4"), 2.0); self.assertAlmostEqual(self.fl.oxygen_stoich_z("C3H8"), 5.0)
        self.assertAlmostEqual(self.fl.oxygen_stoich_z("C2H6O"), 3.0)
        self.assertAlmostEqual(self.fl.loc_vol_pct(2.1, "C3H8"), 10.5)

    def test_purge(self):
        c = self.fl.sweep_through_conc(21, 0, 100, 0.5, 50)
        self.assertAlmostEqual(c, 21 * math.exp(-1))
        t = self.fl.sweep_through_time_h(21, 5, 0, 100, 50)
        self.assertAlmostEqual(self.fl.sweep_through_conc(21, 0, 100, t, 50), 5)
        n = self.fl.pressure_purge_cycles(21, 2, 700, 100)
        self.assertEqual(n, 2)
        self.assertLessEqual(21 * (100 / 700) ** n, 2); self.assertGreater(21 * (100 / 700) ** (n - 1), 2)

    def test_static_and_zones(self):
        self.assertAlmostEqual(self.fl.relaxation_time_s(1e-11, 2.0), 8.854e-12 * 2 / 1e-11, places=4)
        self.assertTrue(self.fl.pipe_charging_check(2.0, 0.1)["ok"]); self.assertFalse(self.fl.pipe_charging_check(7.0, 0.2)["ok"])
        self.assertEqual([self.fl.zone_from_release_hours(h) for h in (2000, 100, 1)], ["Zone 0", "Zone 1", "Zone 2"])

    def test_fire_curves(self):
        self.assertAlmostEqual(self.sf.iso834_C(0), 20); self.assertAlmostEqual(self.sf.iso834_C(30), 20 + 345 * math.log10(241))
        self.assertAlmostEqual(self.sf.hydrocarbon_C(0), 20, places=6)
        self.assertTrue(1050 < self.sf.hydrocarbon_C(60) < 1100)
        self.assertGreater(self.sf.hydrocarbon_C(5), self.sf.iso834_C(5))

    def test_steel_temperature(self):
        thin = self.sf.steel_temperature_history(250, t_end_min=30)
        thick = self.sf.steel_temperature_history(60, t_end_min=30)
        t_thin, t_thick = self.sf.time_to_critical_min(thin), self.sf.time_to_critical_min(thick)
        self.assertIsNotNone(t_thin); self.assertTrue(t_thick is None or t_thick > t_thin)
        prot = dict(thickness_m=0.02, **{"lambda": 0.1}, cp=1000.0, rho=300.0, Ap_over_V=150)
        p = self.sf.steel_temperature_history(150, protection=prot, t_end_min=120)
        u = self.sf.steel_temperature_history(150, t_end_min=120)
        self.assertGreater(self.sf.time_to_critical_min(p) or 999, (self.sf.time_to_critical_min(u) or 0) + 5)
        thicker = self.sf.steel_temperature_history(150, protection={**prot, "thickness_m": 0.04}, t_end_min=120)
        self.assertGreaterEqual(self.sf.time_to_critical_min(thicker) or 999, self.sf.time_to_critical_min(p) or 999)
        # steel never exceeds the gas temperature
        for t, T in u:
            self.assertLessEqual(T, self.sf.hydrocarbon_C(t) + 1e-6)


class Depressuring(unittest.TestCase):
    def setUp(self):
        from process_safety import depressuring as dep, overfill as of, relief_piping as rp
        self.dep, self.of, self.rp = dep, of, rp

    def test_numeric_matches_closed_form_while_choked(self):
        args = (30.0, 5000.0, 1000.0, 300.0, 20.0, 1.3, 800.0)
        pc = self.dep.choke_pressure_kpa(1.3); self.assertLess(pc, 1000)
        for mode in ("isothermal", "adiabatic"):
            n = self.dep.depressuring_time_s(*args, mode=mode, dt=0.01)
            c = self.dep.closed_form_time_s(*args, mode=mode)
            self.assertAlmostEqual(n / c, 1, delta=0.01, msg=mode)
        self.assertLess(self.dep.depressuring_time_s(*args, mode="adiabatic"), self.dep.depressuring_time_s(*args, mode="isothermal"))

    def test_required_area_roundtrip_and_temperature(self):
        A = self.dep.required_area_mm2(30, 5000, 1000, 300, 20, 1.3, 600)
        t = self.dep.depressuring_time_s(30, 5000, 1000, 300, 20, 1.3, A, mode="isothermal", dt=0.2)
        self.assertAlmostEqual(t / 600, 1, delta=0.02)
        self.assertAlmostEqual(self.dep.min_gas_temperature_K(300, 5000, 1000, 1.3), 300 * 0.2 ** (0.3 / 1.3))
        self.assertLess(self.dep.min_gas_temperature_K(300, 5000, 1000, 1.3), 300)

    def test_overfill(self):
        self.assertAlmostEqual(self.of.time_to_overfill_s(10, 360), 100)
        self.assertAlmostEqual(self.of.alarm_margin_m3(360, 600, 60, 1.5), 0.1 * 660 * 1.5)
        a = self.of.tank_area_m2(10)
        self.assertAlmostEqual(self.of.alarm_height_m(14.0, a, 360, 600, 60), 14.0 - 0.1 * 660 / a)

    def test_relief_piping(self):
        self.assertTrue(self.rp.inlet_loss_check(20, 1000)["ok"]); self.assertFalse(self.rp.inlet_loss_check(40, 1000)["ok"])
        self.assertAlmostEqual(self.rp.reaction_force_N(5, 200, 101.325, 0.05), 1000.0)
        self.assertAlmostEqual(self.rp.reaction_force_N(5, 200, 201.325, 0.05), 1000 + 100e3 * 0.05)
        s = self.rp.exit_state_from_mach(5, 0.25, 110, 320, 20, 1.3)
        self.assertAlmostEqual(s["density_kg_m3"] * s["velocity_m_s"] * s["area_m2"], 5.0)


class PSMandMAH(unittest.TestCase):
    def setUp(self):
        from process_safety import psm, mah, pipeline
        self.psm, self.mah, self.pl = psm, mah, pipeline

    def test_elements_and_data(self):
        self.assertEqual(list(self.psm.OSHA_ELEMENTS), list("cdefghijklmnop")); self.assertEqual(len(self.psm.OSHA_ELEMENTS), 14)
        self.assertEqual(len(self.psm.AIGA99_ELEMENTS), 21); self.assertEqual(sum(len(v) for v in self.psm.RBPS_ELEMENTS.values()), 20)
        self.assertEqual(set(self.psm.CROSSWALK_OSHA_TO_AIGA), set(self.psm.OSHA_ELEMENTS))
        for v in self.psm.CROSSWALK_OSHA_TO_AIGA.values():
            for n in v: self.assertIn(n, self.psm.AIGA99_ELEMENTS)
        tq = {r["chemical"]: r["tq_lb"] for r in self.psm.appendix_a()}
        for name, v in {"Chlorine": 1500, "Ammonia, Anhydrous": 10000, "Hydrogen Fluoride": 1000, "Hydrogen Sulfide": 1500, "Ethylene Oxide": 5000,
                        "Phosgene (also called Carbonyl Chloride)": 100, "Sulfur Dioxide (liquid)": 1000}.items():
            self.assertEqual(tq[name], v, name)
        self.assertGreaterEqual(len(tq), 130)

    def test_applicability(self):
        r = self.psm.covered_chemical("7782-50-5", 700); self.assertTrue(r["covered"]); self.assertAlmostEqual(r["threshold_kg"], 1500 / 2.2046226218)
        self.assertFalse(self.psm.covered_chemical("chlorine", 600)["covered"])
        self.assertFalse(self.psm.covered_chemical("nonexistium", 1)["found"])
        f = self.psm.covered_flammable(5000); self.assertTrue(f["covered"]); self.assertAlmostEqual(f["threshold_kg"], 4535.9, places=1)
        self.assertFalse(self.psm.covered_flammable(5000, workplace_fuel_only=True)["covered"])
        self.assertFalse(self.psm.covered_flammable(5000, atmospheric_tank_below_boiling_point=True)["covered"])
        self.assertFalse(self.psm.covered_flammable(4000)["covered"])

    def test_due_dates(self):
        from datetime import date, datetime
        d = self.psm.due_dates({"pha_revalidation": date(2020, 2, 29), "compliance_audit": date(2023, 6, 1), "refresher_training": date(2025, 10, 1),
                                "operating_procedure_certification": date(2025, 11, 1)}, today=date(2026, 11, 3))
        self.assertEqual(d["pha_revalidation"]["next_due"], "2025-02-28"); self.assertEqual(d["pha_revalidation"]["status"], "overdue")
        self.assertEqual(d["compliance_audit"]["next_due"], "2026-06-01"); self.assertEqual(d["compliance_audit"]["status"], "overdue")
        self.assertEqual(d["refresher_training"]["status"], "ok"); self.assertEqual(d["operating_procedure_certification"]["next_due"], "2026-11-01")
        self.assertEqual(self.psm.incident_investigation_deadline(datetime(2026, 1, 1, 10)), datetime(2026, 1, 3, 10))

    def test_gap_assessment(self):
        s = {k: 4 for k in self.psm.OSHA_ELEMENTS}; s["l"] = 1; s["o"] = 0
        g = self.psm.gap_assessment(s)
        self.assertAlmostEqual(g["percent"], 100 * (12 * 4 + 1) / 56); self.assertEqual(g["weakest"][0][0], "o"); self.assertEqual(g["unscored"], [])
        self.assertEqual(self.psm.gap_assessment({"e": 2})["unscored"][0], "c")

    def test_seveso(self):
        p1 = self.mah.part1()
        self.assertEqual((p1["P5c"]["lower_t"], p1["P5c"]["upper_t"]), (5000, 50000)); self.assertEqual((p1["H1"]["lower_t"], p1["H1"]["upper_t"]), (5, 20))
        cl = self.mah.find_substance("Chlorine"); self.assertEqual((cl["lower_t"], cl["upper_t"]), (10, 25))
        self.assertEqual(self.mah.classify([{"substance": "Chlorine", "tonnes": 10, "group": "H"}])["tier"], "lower-tier")
        self.assertEqual(self.mah.classify([{"substance": "Chlorine", "tonnes": 25, "group": "H"}])["tier"], "upper-tier")
        self.assertEqual(self.mah.classify([{"substance": "Chlorine", "tonnes": 9, "group": "H"}])["tier"], "below Seveso scope")
        c = self.mah.classify([{"substance": "Chlorine", "tonnes": 6, "group": "H"}, {"substance": "Hydrogen sulphide", "tonnes": 3, "group": "H"}])
        self.assertEqual(c["tier"], "lower-tier"); self.assertAlmostEqual(c["sums"]["H"]["lower"], 0.6 + 0.6)
        sep = self.mah.classify([{"substance": "Chlorine", "tonnes": 6, "group": "H"}, {"category": "P2", "tonnes": 6}])  # 0.6 H + 0.6 P: groups not added
        self.assertEqual(sep["tier"], "below Seveso scope")
        lpg = self.mah.classify([{"substance": "Liquefied flammable gases", "tonnes": 60, "group": "P"}]); self.assertEqual(lpg["tier"], "lower-tier")
        with self.assertRaises(KeyError): self.mah.classify([{"substance": "Unobtainium", "tonnes": 1, "group": "H"}])

    def test_pipeline(self):
        self.assertEqual(self.pl.DESIGN_FACTOR, {1: 0.72, 2: 0.60, 3: 0.50, 4: 0.40})
        self.assertAlmostEqual(self.pl.temperature_derating(135.0), (1.0 + 0.967) / 2); self.assertEqual(self.pl.temperature_derating(100), 1.0)
        self.assertAlmostEqual(self.pl.temperature_derating(232.0), 0.867)
        with self.assertRaises(ValueError): self.pl.temperature_derating(300)
        P = self.pl.design_pressure_kpa(448, 12.7, 610, 1, 1.0, 20)  # X65, 24 in, 0.5 in
        self.assertAlmostEqual(P, 2 * 448 * 12.7 / 610 * 0.72 * 1000)
        self.assertAlmostEqual(self.pl.required_wall_mm(P, 448, 610, 1, 1.0, 20), 12.7)
        self.assertLess(self.pl.design_pressure_kpa(448, 12.7, 610, 3), P)
        self.assertAlmostEqual(self.pl.design_pressure_kpa(448, 12.7, 610, 1, 0.6, 20), P * 0.6)
        r = self.pl.potential_impact_radius_m(1000 / 0.1450377377, 36 * 25.4)  # 1000 psi, 36 in
        self.assertAlmostEqual(r / 0.3048, 0.69 * math.sqrt(1000 * 36 ** 2), places=3); self.assertAlmostEqual(r / 0.3048, 785.5, delta=0.5)
        self.assertTrue(self.pl.hca_by_pir(250, 20)); self.assertFalse(self.pl.hca_by_pir(250, 19)); self.assertFalse(self.pl.hca_by_pir(150, 50))
        self.assertFalse(self.pl.hca_by_pir(250, 50, class_location=3))


class Sectors(unittest.TestCase):
    def setUp(self):
        from process_safety import props, lng, lpg, rmp, flare_system, plant_units
        self.pr, self.lng, self.lpg, self.rmp, self.fs, self.pu = props, lng, lpg, rmp, flare_system, plant_units

    def test_property_correlations_against_known_values(self):
        self.assertAlmostEqual(self.pr.vapour_pressure_bar("propane", 300) / 9.98, 1, delta=0.03)
        self.assertAlmostEqual(self.pr.vapour_pressure_bar("propane", 323.15) / 17.1, 1, delta=0.04)
        for c, (Tc, Pc, w, M, Tb) in self.pr.COMPONENTS.items():
            self.assertAlmostEqual(self.pr.vapour_pressure_bar(c, Tb) / 1.01325, 1, delta=0.04, msg=c)
            self.assertAlmostEqual(self.pr.saturation_temperature_K(c, 1.01325), Tb, delta=2.5, msg=c)
        self.assertAlmostEqual(self.pr.liquid_density_kg_m3("methane", 111.66) / 422, 1, delta=0.02)
        self.assertAlmostEqual(self.pr.liquid_density_kg_m3("propane", 288.15) / 507, 1, delta=0.02)
        self.assertAlmostEqual(self.pr.liquid_density_kg_m3("n-butane", 288.15) / 584, 1, delta=0.02)
        self.assertGreater(self.pr.liquid_density_kg_m3("propane", 270), self.pr.liquid_density_kg_m3("propane", 320))
        self.assertGreater(self.pr.vapour_pressure_bar("n-butane", 320), self.pr.vapour_pressure_bar("n-butane", 300))

    def test_lng_impoundment_per_cfr_193_2181(self):
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([160000]), 176000)
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([160000], surge_accounted=True), 160000)
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([100000, 100000]), 200000)
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([160000, 50000]), 210000)
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([160000, 20000]), 180000)
        self.assertAlmostEqual(self.lng.impoundment_capacity_m3([160000, 10000]), 176000)
        self.assertEqual(self.lng.DISPERSION_RULE["average_concentration_vol_pct"], 2.5)
        self.assertEqual((self.lng.DISPERSION_RULE["stability"], self.lng.DISPERSION_RULE["wind_speed_m_s"]), ("F", 2.01))

    def test_lng_boiloff_regas_liquefaction(self):
        self.assertAlmostEqual(self.lng.boil_off_rate_kg_s(51), 0.1)
        pct = self.lng.boil_off_pct_per_day(100, 160000)
        self.assertAlmostEqual(pct, 100 / 510 * 86400 / (160000 * 422) * 100)
        self.assertTrue(0.02 < pct < 0.5)
        d = self.lng.regas_duty_kW(100, 111.66, 283.15)
        self.assertAlmostEqual(d, 100 * (510 + 2.2 * (283.15 - 111.66)))
        self.assertAlmostEqual(self.lng.seawater_flow_m3_s(d, 5.0), d / (3.99 * 5) / 1025)
        self.assertAlmostEqual(self.lng.scv_fuel_gas_kg_s(d, 0.98, 50), d / (0.98 * 50000))
        w = self.lng.ideal_liquefaction_work_kJ_kg(300)
        # numeric check of the exergy integral: sum of (T0/T - 1) dQ over the cooling path
        T0, Tb, n = 300.0, 111.66, 200000
        num = sum((T0 / (Tb + (T0 - Tb) * (i + .5) / n) - 1) * 2.2 * (T0 - Tb) / n for i in range(n)) + 510 * (T0 / Tb - 1)
        self.assertAlmostEqual(w / num, 1, delta=1e-4)
        self.assertAlmostEqual(self.lng.kWh_per_tonne(3600.0), 1000.0)

    def test_lpg(self):
        f = self.lpg.max_fill_fraction("propane", 288.15, 323.15)
        self.assertTrue(0.8 < f < 0.95)
        self.assertLess(self.lpg.max_fill_fraction("propane", 288.15, 333.15), f)
        self.assertAlmostEqual(self.lpg.vapour_pressure_kPag("propane", 323.15), 17.1e2 - 101.325, delta=0.05 * 1700)
        self.assertAlmostEqual(self.lpg.liquid_mass_kg("propane", 100, 288.15, 0.85), 100 * 0.85 * self.pr.liquid_density_kg_m3("propane", 288.15))
        self.assertAlmostEqual(self.lpg.refrigerated_boil_off_kg_s(42.5), 0.1)
        self.assertAlmostEqual(self.lpg.design_pressure_for_max_temperature_kPag("n-butane", 323.15, 1.1), 1.1 * self.lpg.vapour_pressure_kPag("n-butane", 323.15))

    def test_rmp_data_and_rules(self):
        d = self.rmp._data()
        self.assertEqual((len(d["toxics"]), len(d["flammables"])), (77, 63))
        self.assertTrue(all(r["toxic_endpoint_mg_L"] is not None for r in d["toxics"]))
        c = self.rmp.find("Chlorine"); self.assertEqual((c["tq_lb"], c["toxic_endpoint_mg_L"]), (2500, 0.0087))
        self.assertEqual(self.rmp.find("7664-41-7")["tq_lb"], 10000)
        self.assertEqual((self.rmp.find("propane")["name"], self.rmp.find("propane")["tq_lb"], self.rmp.find("propane")["kind"]), ("Propane", 10000, "flammable"))
        self.assertTrue(self.rmp.threshold_check("chlorine", 1200)["covered"]); self.assertFalse(self.rmp.threshold_check("chlorine", 1000)["covered"])
        self.assertFalse(self.rmp.threshold_check("chlorine", 5000, weight_fraction=0.005)["covered"])
        self.assertAlmostEqual(self.rmp.ENDPOINT_OVERPRESSURE_KPA, 6.894757)
        self.assertEqual((self.rmp.WORST_CASE_WIND_M_S, self.rmp.WORST_CASE_STABILITY, self.rmp.RELEASE_DURATION_S, self.rmp.EXPLOSION_YIELD), (1.5, "F", 600.0, 0.10))
        self.assertAlmostEqual(self.rmp.pool_area_m2(2.0), 200.0)

    def test_rmp_worst_cases(self):
        a = self.rmp.worst_case_toxic_gas("Chlorine", 20); b = self.rmp.worst_case_toxic_gas("Chlorine", 80)
        self.assertAlmostEqual(a["release_rate_kg_s"], 20 / 600); self.assertGreater(b["screening_distance_m_neutral_gas"], a["screening_distance_m_neutral_gas"])
        self.assertIn("dense", a["warning"])
        with self.assertRaises(KeyError): self.rmp.worst_case_toxic_gas("propane", 100)
        v = self.rmp.worst_case_flammable_vce(20000, 46.3)
        self.assertAlmostEqual(v["tnt_equivalent_kg"], 0.1 * 20000 * 46.3 / 4.5)
        from process_safety import explosion
        self.assertAlmostEqual(explosion.kinney_graham_kpa(v["tnt_equivalent_kg"], v["distance_to_1psi_m"]), 6.894757, places=3)

    def test_flare_system(self):
        events = {"power failure": [{"name": "a", "kg_s": 30, "mw": 20, "T_K": 350}, {"name": "b", "kg_s": 20, "mw": 40, "T_K": 400}],
                  "cooling water": [{"name": "c", "kg_s": 60, "mw": 30, "T_K": 320}], "fire": [{"name": "d", "kg_s": 10, "mw": 30, "T_K": 300}]}
        name, load, loads = self.fs.governing_event(events)
        self.assertEqual(name, "cooling water"); self.assertAlmostEqual(loads["power failure"]["kg_s"], 50)
        self.assertAlmostEqual(loads["power failure"]["mw"], 50 / (30 / 20 + 20 / 40)); self.assertAlmostEqual(loads["power failure"]["T_K"], (30 * 350 + 20 * 400) / 50)
        D = self.fs.header_for_event(load, 200, 1.3, 0.5)
        from process_safety import scenarios
        self.assertAlmostEqual(D, scenarios.flare_header_diameter_m(60, 200, 320, 30, 1.3, 0.5))

    def test_plant_units(self):
        self.assertAlmostEqual(self.pu.furnace_purge_time_s(100, 5), 100.0 * 5 / 5)
        h = self.pu.h2o2_decomposition(1000)
        self.assertAlmostEqual(h["o2_per_kg_h2o2"], 0.5 * 31.998 / 34.0147, places=4)
        self.assertAlmostEqual(h["heat_kW"], 1000e3 / 34.0147 * 98.2 / 3600, delta=0.5)
        self.assertAlmostEqual(h["max_steam_kg_h"], h["heat_kW"] * 3600 / 2257.0)
        self.assertAlmostEqual(self.pu.adiabatic_rise_K(200, 2.5), 80.0)
        q = self.pu.hydrogenation_heat_kJ_kg_feed(100, 800, 125)
        self.assertAlmostEqual(q, 100 * 1000 / 22.414 * 125 / 800)


class CLI(unittest.TestCase):
    """The CLI builds its whole parser on every call, so one bad help string breaks every command; exercise representative commands."""

    def run_cli(self, *argv):
        import contextlib, io
        from process_safety.__main__ import main
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(list(argv))
        return rc, buf.getvalue()

    def test_commands_run_and_emit(self):
        import json
        cases = [("coverage",), ("psm-check", "--chemical", "chlorine", "--kg", "700"), ("rmp-check", "chlorine", "--kg", "1200"),
                 ("rmp-worst", "propane", "--kg", "20000", "--hc", "46.3"), ("lng", "--tanks", "160000", "--heat-kw", "100", "--regas-kg-s", "100"),
                 ("lpg", "propane"), ("h2o2", "--kg-h", "1000"), ("pool-fire", "--area", "300", "--hc", "44000", "--hv", "350", "--cp", "2.2", "--tb", "400"),
                 ("depressure", "--volume", "30", "--p0", "5000", "--pt", "1000", "--T0", "300", "--M", "20", "--k", "1.3", "--area", "800"),
                 ("seveso", "Chlorine:H=6", "Hydrogen sulphide:H=3"), ("pipeline", "--smys", "448", "--wall", "12.7", "--od", "610"),
                 ("arc-flash", "--kv", "0.48", "--ka", "20", "--t", "0.2", "--dist-mm", "455"), ("idmt", "--i", "2000", "--pickup", "200", "--tms", "0.3"),
                 ("noise", "95:2", "90:4"), ("safeguard", "--stop-s", "0.2", "--d-mm", "30"), ("earthing", "--rho-s", "3000", "--t", "0.5", "--rho", "75", "--hs", "0.2")]
        for argv in cases:
            rc, out = self.run_cli(*argv)
            self.assertEqual(rc, 0, argv); self.assertTrue(out.strip(), argv)
            if argv[0] != "coverage":
                json.loads(out)

    def test_help_for_every_command(self):
        import contextlib, io
        from process_safety.__main__ import main
        for cmd in ("relief-gas", "tank-fire", "vapour-fire", "rmp-worst", "lng", "psm-due", "hazop-csv"):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf), self.assertRaises(SystemExit) as cm:
                main([cmd, "--help"])
            self.assertEqual(cm.exception.code, 0, cmd)


class ElectricalMechanical(unittest.TestCase):
    def setUp(self):
        from process_safety import electrical as el, mechanical_safety as ms, noise
        self.el, self.ms, self.nz = el, ms, noise

    def test_fault_cable_power(self):
        self.assertAlmostEqual(self.el.fault_current_kA(11, 0.5), 11 / (math.sqrt(3) * 0.5))
        self.assertAlmostEqual(self.el.transformer_fault_kA(1, 0.415, 5), 1 / (math.sqrt(3) * 0.415 * 0.05))
        self.assertAlmostEqual(self.el.transformer_fault_kA(1, 0.415, 5, 100), 1 / (math.sqrt(3) * 0.415 * 0.06))
        self.assertAlmostEqual(self.el.full_load_current_A(55, 415, 0.85, 0.93), 55000 / (math.sqrt(3) * 415 * 0.85 * 0.93))
        self.assertAlmostEqual(self.el.voltage_drop_pct(100, 0.2, 0.3, 0.08, 1.0, 415), math.sqrt(3) * 100 * 0.2 * 0.3 / 415 * 100)
        self.assertGreater(self.el.voltage_drop_pct(100, 0.2, 0.3, 0.08, 0.8, 415, 1), self.el.voltage_drop_pct(100, 0.2, 0.3, 0.08, 0.8, 415, 3) * 0.99)
        self.assertAlmostEqual(self.el.min_csa_mm2(10, 1.0, "copper", "XLPE"), 10000 / 143)
        self.assertGreater(self.el.min_csa_mm2(10, 1, "aluminium", "PVC"), self.el.min_csa_mm2(10, 1, "copper", "XLPE"))
        self.assertAlmostEqual(self.el.pf_correction_kvar(100, 0.8, 0.95), 100 * (0.75 - math.tan(math.acos(0.95))))
        self.assertAlmostEqual(self.el.motor_start_dip_pct(5, 50), 100 * 5 / 55)

    def test_idmt_and_grading(self):
        self.assertAlmostEqual(self.el.idmt_time_s(10, 1, 1.0, "standard_inverse"), 0.14 / (10 ** 0.02 - 1))
        self.assertAlmostEqual(self.el.idmt_time_s(10, 1, 1.0, "standard_inverse"), 2.97, places=2)
        self.assertAlmostEqual(self.el.idmt_time_s(10, 1, 1.0, "very_inverse"), 1.5)
        self.assertAlmostEqual(self.el.idmt_time_s(10, 1, 1.0, "extremely_inverse"), 80 / 99)
        self.assertEqual(self.el.idmt_time_s(1.0, 1, 1.0), float("inf"))
        self.assertAlmostEqual(self.el.idmt_time_s(10, 1, 0.5), 0.5 * self.el.idmt_time_s(10, 1, 1.0))
        self.assertTrue(self.el.grading_check(0.8, 0.4)["ok"]); self.assertFalse(self.el.grading_check(0.6, 0.4)["ok"])

    def test_earthing(self):
        self.assertAlmostEqual(self.el.surface_layer_factor(75, 4000, 0.2), 0.82, places=2)
        self.assertEqual(self.el.surface_layer_factor(100, 100, 0.1), 1.0)
        t = self.el.tolerable_touch_V(3000, 0.5, 0.8, 50)
        self.assertAlmostEqual(t, (1000 + 1.5 * 0.8 * 3000) * 0.116 / math.sqrt(0.5))
        self.assertGreater(self.el.tolerable_step_V(3000, 0.5, 0.8), t)
        self.assertGreater(self.el.tolerable_touch_V(3000, 0.5, 0.8, 70), t)
        self.assertLess(self.el.tolerable_touch_V(3000, 1.0), self.el.tolerable_touch_V(3000, 0.25))
        R = self.el.rod_resistance_ohm(100, 3, 0.0079)
        self.assertAlmostEqual(R, 100 / (2 * math.pi * 3) * (math.log(4 * 3 / 0.0079) - 1)); self.assertLess(self.el.rod_resistance_ohm(100, 6, 0.0079), R)
        self.assertAlmostEqual(self.el.ground_potential_rise_V(5000, 0.5), 2500)

    def test_lightning(self):
        self.assertEqual(self.el.ROLLING_SPHERE_RADIUS_M, {1: 20.0, 2: 30.0, 3: 45.0, 4: 60.0})
        self.assertAlmostEqual(self.el.protected_radius_at_ground_m(10, 20), math.sqrt(10 * 30)); self.assertEqual(self.el.protected_radius_at_ground_m(25, 20), 20)
        self.assertAlmostEqual(self.el.protected_radius_at_height_m(10, 5, 20), math.sqrt(300) - math.sqrt(175)); self.assertEqual(self.el.protected_radius_at_height_m(10, 10, 20), 0.0)
        self.assertGreater(self.el.protected_radius_at_ground_m(10, 45), self.el.protected_radius_at_ground_m(10, 20))
        A = self.el.collection_area_m2(50, 30, 10); self.assertAlmostEqual(A, 1500 + 2 * 30 * 80 + math.pi * 900)
        self.assertAlmostEqual(self.el.strikes_per_year(self.el.ground_flash_density_from_thunderdays(40), A), 4 * A * 1e-6)

    def test_ex_selection(self):
        self.assertEqual(self.el.allowed_t_classes(280), ["T3", "T4", "T5", "T6"]); self.assertEqual(self.el.allowed_t_classes(90), ["T6"])
        self.assertEqual(self.el.allowed_t_classes(540), list(self.el.T_CLASS_MAX_C)); self.assertEqual(self.el.allowed_t_classes(80), [])
        self.assertEqual(self.el.allowed_t_classes(210, margin_C=20), ["T4", "T5", "T6"])
        self.assertEqual([self.el.gas_group_from_mesg(x) for x in (0.28, 0.5, 0.65, 0.9, 1.1)], ["IIC", "IIC", "IIB", "IIA", "IIA"])
        self.assertEqual([self.el.min_epl_for_zone(z) for z in (0, 1, 2)], ["Ga", "Gb", "Gc"])

    def test_arc_flash_lee(self):
        E = self.el.lee_incident_energy_J_cm2(0.48, 20, 0.2, 455)
        self.assertAlmostEqual(E, 2.142e6 * 0.48 * 20 * 0.2 / 455 ** 2)
        self.assertAlmostEqual(self.el.lee_incident_energy_J_cm2(0.48, 20, 0.2, 910) * 4, E)
        D = self.el.lee_boundary_mm(0.48, 20, 0.2)
        self.assertAlmostEqual(self.el.lee_incident_energy_J_cm2(0.48, 20, 0.2, D), 5.02)
        self.assertAlmostEqual(5.02 * self.el.CAL_PER_J, 1.2, places=2)
        a = self.el.lee_applicable(480, 3, enclosed=False); self.assertTrue(a["ok"]) ; self.assertFalse(a["conditional"])
        self.assertTrue(self.el.lee_applicable(11000, 3, False)["conditional"])
        self.assertFalse(self.el.lee_applicable(480, 3, enclosed=True)["ok"]); self.assertFalse(self.el.lee_applicable(20000, 3, False)["ok"])
        self.assertTrue(self.el.lee_applicable(480, 1, True)["ok"])

    def test_noise_osha(self):
        for L, T in ((90, 8), (95, 4), (100, 2), (105, 1), (110, 0.5), (115, 0.25)):
            self.assertAlmostEqual(self.nz.osha_permissible_hours(L), T)
        for L, T in ((92, 6), (97, 3), (102, 1.5)):
            self.assertAlmostEqual(self.nz.osha_permissible_hours(L) / T, 1, delta=0.02)
        self.assertAlmostEqual(self.nz.dose_pct([(95, 2), (90, 4)]), 100.0)
        self.assertAlmostEqual(self.nz.twa_dBA(100), 90.0); self.assertAlmostEqual(self.nz.twa_dBA(50), 85.0, places=1)
        self.assertAlmostEqual(self.nz.niosh_permissible_hours(88), 4.0); self.assertAlmostEqual(self.nz.niosh_permissible_hours(100), 0.25)
        self.assertAlmostEqual(self.nz.sum_levels_dB([90, 90]), 93.0103, places=3)
        self.assertAlmostEqual(self.nz.point_source_level_dB(100, 1, 20), 100 - 20 * math.log10(20))
        r85 = self.nz.distance_for_level_m(100, 1, 85)
        self.assertAlmostEqual(self.nz.point_source_level_dB(100, 1, r85), 85.0)

    def test_machinery_safety(self):
        self.assertEqual((self.ms.required_pl("S2", "F2", "P2"), self.ms.required_pl("S2", "F1", "P1"), self.ms.required_pl("S1", "F1", "P1")), ("e", "c", "a"))
        self.assertEqual(len(self.ms._RISK_GRAPH), 8)
        self.assertEqual([self.ms.pl_from_pfhd(x) for x in (5e-8, 5e-7, 2e-6, 5e-6, 5e-5, 1e-9)], ["e", "d", "c", "b", "a", None])
        self.assertTrue(self.ms.pl_meets("d", "c")); self.assertFalse(self.ms.pl_meets("c", "d"))
        self.assertAlmostEqual(self.ms.safeguard_distance_mm(0.2, 30), 500.0)   # K=2000 gives 528 > 500; K=1600 gives 448 < 500 -> 500
        self.assertAlmostEqual(self.ms.safeguard_distance_mm(1.0, 14), 1600.0)
        self.assertAlmostEqual(self.ms.safeguard_distance_mm(0.1, 14), 200.0)
        self.assertAlmostEqual(self.ms.safeguard_distance_mm(0.1, 10), 200.0)  # C floors at 0

    def test_lifting_and_impacts(self):
        self.assertAlmostEqual(self.ms.sling_leg_tension_N(1000, 2, 60), 1000 * 9.80665 / (2 * 0.5))
        self.assertAlmostEqual(self.ms.sling_leg_tension_N(1000, 2, 0), 1000 * 9.80665 / 2)
        self.assertAlmostEqual(self.ms.drop_velocity_m_s(50), math.sqrt(2 * 9.80665 * 50))
        vd = self.ms.drop_velocity_m_s(50, 5, 1.0, 0.01); self.assertTrue(0 < vd < self.ms.drop_velocity_m_s(50))
        vt = self.ms.terminal_velocity_m_s(5, 1.0, 0.01); self.assertAlmostEqual(self.ms.drop_velocity_m_s(1e5, 5, 1.0, 0.01), vt, delta=0.01 * vt)
        self.assertAlmostEqual(self.ms.impact_energy_kJ(10, 20), 2.0); self.assertAlmostEqual(self.ms.ship_collision_energy_kJ(5000, 2.0), 14000.0)

    def test_piping_mechanics(self):
        s = self.ms.pipe_section(168.3, 7.11)
        self.assertAlmostEqual(s["I_m4"], math.pi / 64 * (0.1683 ** 4 - (0.1683 - 0.01422) ** 4)); self.assertAlmostEqual(s["Z_m3"], s["I_m4"] / 0.08415)
        dry = self.ms.max_pipe_span_m(168.3, 7.11); wet = self.ms.max_pipe_span_m(168.3, 7.11, fluid_density=1000)
        self.assertLess(wet["max_span_m"], dry["max_span_m"]); self.assertGreater(wet["w_N_m"], dry["w_N_m"])
        self.assertEqual(dry["max_span_m"], min(dry["L_deflection_m"], dry["L_stress_m"]))
        self.assertAlmostEqual(self.ms.thermal_growth_mm(100, 100), 120.0)
        self.assertAlmostEqual(self.ms.guided_cantilever_leg_m(200, 100, 150, 200), math.sqrt(3 * 200e9 * 0.2 * 0.1 / 150e6))
        self.assertAlmostEqual(self.ms.bolt_torque_Nm(20, 100e3), 400.0)

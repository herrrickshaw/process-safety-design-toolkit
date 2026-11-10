"""Identity tests for flash_release, droplet, pool_spread, jet_radiation and the lgrelease tool.

Identities (continuity, momentum, energy, exact first integral, evaporation law, limits) rather than remembered example numbers. The one
regression block pins the propane worked example to the values computed in the design review (CoolProp-derived inputs)."""
import json
import math
import os
import shutil
import tempfile
import unittest

from process_safety import droplet, flash_release, jet_flame, jet_radiation, pool_spread, tools
from process_safety.constants import G as g_acc

PROPANE = dict(P0_kPa=1200.0, rho0_kg_m3=476.9645, omega=6.410917, area_m2=math.pi * 0.025 ** 2 / 4, Cd=0.62, T0_K=307.5809, Tb_K=231.036,
               cp_mean_J_kgK=2493.63, h_fg_Tb_J_kg=425592.0, rho_L_Tb_kg_m3=580.883, rho_V_Tb_kg_m3=2.41611)


class FlashRelease(unittest.TestCase):
    def setUp(self):
        self.r = flash_release.saturated_liquid_release(**PROPANE)

    def test_continuity(self):
        r = self.r
        self.assertAlmostEqual(r["A_f_m2"] * r["rho_f_kg_m3"] * r["u_f_m_s"], r["W_kg_s"], delta=1e-12 * r["W_kg_s"])

    def test_choke_density_velocity_equal_flux(self):
        r = self.r
        self.assertAlmostEqual(r["rho_choke_kg_m3"] * r["u_choke_m_s"], r["G_kg_m2_s"], delta=1e-9 * r["G_kg_m2_s"])

    def test_momentum_balance(self):
        r = self.r
        self.assertAlmostEqual(r["G_kg_m2_s"] * (r["u_f_m_s"] - r["u_choke_m_s"]), (r["P_choke_kPa"] - 101.325) * 1000.0, delta=1e-6)

    def test_energy_balance_exact(self):
        r = self.r
        self.assertAlmostEqual(r["x_isenthalpic"] - r["x_vapour"], r["KE_share_of_h_fg"], places=12)

    def test_flux_scales_with_area_and_cd(self):
        a = dict(PROPANE, area_m2=PROPANE["area_m2"] * 2)
        b = dict(PROPANE, Cd=0.31)
        self.assertAlmostEqual(flash_release.saturated_liquid_release(**a)["W_kg_s"] / self.r["W_kg_s"], 2.0, places=12)
        self.assertAlmostEqual(flash_release.saturated_liquid_release(**b)["W_kg_s"] / self.r["W_kg_s"], 0.5, places=12)

    def test_flux_below_bernoulli(self):
        bern = math.sqrt(2 * PROPANE["rho0_kg_m3"] * (PROPANE["P0_kPa"] - 101.325) * 1000)
        self.assertLess(self.r["G_kg_m2_s"], bern / 3)       # two-phase choking removes most of the liquid-only flux

    def test_subcritical_has_no_expansion_velocity_gain(self):
        r = flash_release.saturated_liquid_release(P0_kPa=108.0, rho0_kg_m3=570.0, omega=6.4, area_m2=1e-4, Cd=0.6, T0_K=232.0, Tb_K=231.036,
                                                   cp_mean_J_kgK=2300.0, h_fg_Tb_J_kg=425592.0, rho_L_Tb_kg_m3=580.883, rho_V_Tb_kg_m3=2.4)
        self.assertEqual(r["regime"], "subcritical")
        self.assertAlmostEqual(r["u_f_m_s"], r["u_choke_m_s"], places=9)

    def test_refusals(self):
        for bad in (dict(T0_K=231.0), dict(Cd=1.5), dict(area_m2=-1.0), dict(P0_kPa=100.0)):
            with self.assertRaises(ValueError):
                flash_release.saturated_liquid_release(**dict(PROPANE, **bad))

    def test_iso_limits(self):
        self.assertEqual(flash_release.iso4126_10_check(307.58, 369.89, 1200, 4251, 6.4), [])
        self.assertEqual(len(flash_release.iso4126_10_check(340, 369.89, 3000, 4251, 150)), 3)

    def test_regression_propane_example(self):
        r = self.r
        self.assertAlmostEqual(r["W_kg_s"], 2.3368, delta=2e-3)
        self.assertAlmostEqual(r["u_f_m_s"], 153.70, delta=0.1)
        self.assertAlmostEqual(r["x_vapour"], 0.4207, delta=2e-3)


class Droplet(unittest.TestCase):
    def test_weber_identity_and_scaling(self):
        d = droplet.weber_max_diameter_m(0.0157, 150.0, 1.18, 12.5)
        self.assertAlmostEqual(1.18 * 150.0 ** 2 * d / 0.0157, 12.5, places=9)
        self.assertAlmostEqual(droplet.weber_max_diameter_m(0.0157, 300.0, 1.18, 12.5) / d, 0.25, places=12)
        self.assertAlmostEqual(droplet.weber_max_diameter_m(0.0314, 150.0, 1.18, 12.5) / d, 2.0, places=12)

    def test_evaporation_law_d_squared_linear(self):
        t1 = droplet.evaporation_time_s(2e-4, 580.0, 4.2e5, 0.026, 67.0)
        t2 = droplet.evaporation_time_s(1e-4, 580.0, 4.2e5, 0.026, 67.0)
        self.assertAlmostEqual(t1 / t2, 4.0, places=12)

    def test_evaporation_time_matches_numerical_integration(self):
        rho, hfg, k, dT, Nu, d0 = 580.0, 4.2e5, 0.026, 67.0, 2.0, 2e-4
        d, t, dt = d0, 0.0, 1e-5
        while d > 1e-7:
            d -= 2 * Nu * k * dT / (rho * hfg * d) * dt        # d (dd/dt) = -2 Nu k dT / (rho h_fg)
            t += dt
        self.assertAlmostEqual(t, droplet.evaporation_time_s(d0, rho, hfg, k, dT, Nu), delta=2e-3 * t)

    def test_stokes_terminal_velocity_closed_form(self):
        d, rl, rg, mu = 2e-5, 580.0, 1.18, 1.85e-5
        v = droplet.terminal_velocity_m_s(d, rl, rg, mu)
        self.assertAlmostEqual(v, (rl - rg) * g_acc * d * d / (18 * mu), delta=1e-6 * v)

    def test_schiller_naumann_reduces_to_stokes_when_c1_small(self):
        d, rl, rg, mu = 2e-5, 580.0, 1.18, 1.85e-5
        v0 = droplet.terminal_velocity_m_s(d, rl, rg, mu)
        v1 = droplet.terminal_velocity_m_s(d, rl, rg, mu, droplet.schiller_naumann(1e-12, 0.687))
        self.assertAlmostEqual(v1, v0, delta=1e-6 * v0)

    def test_critical_diameter_balances_times(self):
        args = (580.0, 1.18, 1.85e-5, 4.2e5, 0.026, 67.0)
        dc = droplet.critical_diameter_m(2.0, *args)
        self.assertAlmostEqual(droplet.evaporation_time_s(dc, 580.0, 4.2e5, 0.026, 67.0), 2.0 / droplet.terminal_velocity_m_s(dc, 580.0, 1.18, 1.85e-5), delta=1e-6)
        self.assertGreater(droplet.critical_diameter_m(4.0, *args), dc)       # a higher release gives more time: larger droplets evaporate

    def test_partial_expansion_energy_is_continuous_between_cases(self):
        Pst, Pa, v = 1.2e6, 1.0e5, 2.0e-3
        up = droplet.partial_expansion_energy_J_kg(Pst, Pa, v, Pst * (1 - 1e-12), 0.0)
        two = droplet.partial_expansion_energy_J_kg(Pst, Pa, v, Pst, 0.0)
        self.assertAlmostEqual(up, two, delta=1e-6)
        low = droplet.partial_expansion_energy_J_kg(Pst, Pa, v, Pa * (1 + 1e-12), 0.0)
        sub = droplet.partial_expansion_energy_J_kg(Pst, Pa, v, Pa, 0.0)
        self.assertAlmostEqual(low, sub, delta=1e-6)

    def test_flashing_smd_decreases_with_energy_and_refuses_bad_input(self):
        self.assertGreater(droplet.flashing_smd_m(1e3), droplet.flashing_smd_m(1e4))
        for bad in (0.0, -1.0, 1e6):
            with self.assertRaises(ValueError):
                droplet.flashing_smd_m(bad)

    def test_rainout_correlations_continuity_and_limits(self):
        self.assertAlmostEqual(droplet.rainout_kletz(0.5), 0.0, places=12)
        self.assertEqual(droplet.rainout_kletz(0.0, subcooled=True), 1.0)
        self.assertAlmostEqual(droplet.rainout_lautkaski(1.0 / 3.0 - 1e-12), 0.0, places=9)
        self.assertEqual(droplet.rainout_lautkaski(0.4), 0.0)
        self.assertAlmostEqual(droplet.rainout_lautkaski(0.0), 0.6, places=12)
        self.assertAlmostEqual(droplet.rainout_kletz(0.4485), 1 - 2 * 0.4485, places=12)

    def test_validity_warnings(self):
        self.assertEqual(droplet.validity_warnings(5.0, 500.0, 1.22, True), [])
        self.assertEqual(len(droplet.validity_warnings(25.0, 1200.0, 2.0, False)), 4)


class PoolSpread(unittest.TestCase):
    def test_first_integral_without_friction_feed_or_burning(self):
        rl, ra, r0, h0 = 580.0, 1.18, 0.3, 0.02
        V = math.pi * r0 ** 2 * h0
        s = pool_spread.spread(0.0, rl, ra, 0.0, r0, h0, 0.0, t_end_s=2.0, dt_s=1e-4, stop_at_equilibrium=False)
        gp = pool_spread.reduced_gravity(rl, ra)
        k = 4 * gp * V / math.pi
        r, u = s["final"]["radius_m"], s["final"]["front_speed_m_s"]
        self.assertAlmostEqual(u * u, k * (1 / r0 ** 2 - 1 / r ** 2), delta=1e-6 * u * u)
        self.assertGreater(r, r0)

    def test_volume_balance_without_burning(self):
        s = pool_spread.spread(1.5, 580.0, 1.18, 0.0, 0.2, 0.01, 1e-3, t_end_s=3.0, dt_s=1e-3, stop_at_equilibrium=False)
        V0 = math.pi * 0.2 ** 2 * 0.01
        self.assertAlmostEqual(s["final"]["volume_m3"], V0 + 1.5 * s["final"]["t_s"] / 580.0, delta=1e-9)

    def test_volume_is_stationary_at_the_burn_off_radius(self):
        m, mflux = 2.0, 0.1
        r_eq = math.sqrt(pool_spread.equilibrium_area_m2(m, mflux) / math.pi)
        h0 = 0.01
        s = pool_spread.spread(m, 580.0, 1.18, mflux, r_eq, h0, 0.0, t_end_s=1e-3, dt_s=1e-5, stop_at_equilibrium=False)
        V0 = math.pi * r_eq ** 2 * h0
        self.assertAlmostEqual(s["final"]["volume_m3"] / V0, 1.0, delta=1e-7)

    def test_equilibrium_area_balance(self):
        A = pool_spread.equilibrium_area_m2(2.0, 0.1)
        self.assertAlmostEqual(0.1 * A, 2.0, places=12)
        self.assertGreater(pool_spread.equilibrium_area_m2(4.0, 0.1), A)

    def test_friction_slows_the_front(self):
        a = pool_spread.spread(0.0, 580.0, 1.18, 0.0, 0.3, 0.02, 0.0, t_end_s=1.0, dt_s=1e-3, stop_at_equilibrium=False)["final"]["radius_m"]
        b = pool_spread.spread(0.0, 580.0, 1.18, 0.0, 0.3, 0.02, 0.05, t_end_s=1.0, dt_s=1e-3, stop_at_equilibrium=False)["final"]["radius_m"]
        self.assertLess(b, a)

    def test_reaches_burn_off_radius(self):
        s = pool_spread.spread(2.0, 580.0, 1.18, 0.1, 0.05, 0.01, 1e-3)
        self.assertIsNotNone(s["t_to_equilibrium_s"])
        self.assertAlmostEqual(s["final"]["radius_m"], s["r_equilibrium_m"], delta=0.05)

    def test_refusals(self):
        with self.assertRaises(ValueError):
            pool_spread.spread(1.0, 1.0, 2.0, 0.1, 0.1, 0.01, 0.0)     # liquid lighter than air
        with self.assertRaises(ValueError):
            pool_spread.equilibrium_area_m2(1.0, 0.0)


def _flame():
    return jet_flame.chamberlain(2.3368, 5.70987, 1.18432, 44.0956, 46.33e6, 5.0, 90.0, v_j_m_s=153.7)


class JetRadiation(unittest.TestCase):
    def test_far_field_tends_to_point_source(self):
        f = _flame()
        r = 3000.0
        q = jet_radiation.flux_kW_m2(f, 2.0, r, 0.0, 2.0)
        self.assertAlmostEqual(q, f["radiated_power_kW"] / (4 * math.pi * r * r), delta=0.02 * q)

    def test_converges_with_source_count(self):
        f = _flame()
        a = jet_radiation.flux_kW_m2(f, 2.0, 30.0, 0.0, 1.5, 1.0, 60)
        b = jet_radiation.flux_kW_m2(f, 2.0, 30.0, 0.0, 1.5, 1.0, 480)
        self.assertAlmostEqual(a, b, delta=2e-3 * b)

    def test_crosswind_symmetry_and_tau_linear(self):
        f = _flame()
        self.assertAlmostEqual(jet_radiation.flux_kW_m2(f, 2.0, 15.0, 8.0), jet_radiation.flux_kW_m2(f, 2.0, 15.0, -8.0), places=12)
        self.assertAlmostEqual(jet_radiation.flux_kW_m2(f, 2.0, 15.0, 8.0, tau=0.5) / jet_radiation.flux_kW_m2(f, 2.0, 15.0, 8.0), 0.5, places=12)

    def test_flux_falls_downwind_of_the_flame(self):
        f = _flame()
        vals = [jet_radiation.flux_kW_m2(f, 2.0, x, 0.0) for x in (30, 40, 60, 100, 200)]
        self.assertEqual(vals, sorted(vals, reverse=True))

    def test_reach_returns_the_threshold_flux(self):
        f = _flame()
        for d in ("downwind", "upwind", "crosswind"):
            s = jet_radiation.reach_m(f, 2.0, 12.5, d)
            x, y = (s, 0.0) if d == "downwind" else (-s, 0.0) if d == "upwind" else (0.0, s)
            self.assertAlmostEqual(jet_radiation.flux_kW_m2(f, 2.0, x, y), 12.5, delta=1e-6)

    def test_higher_threshold_reaches_less_far(self):
        f = _flame()
        self.assertLess(jet_radiation.reach_m(f, 2.0, 37.5, "downwind"), jet_radiation.reach_m(f, 2.0, 4.7, "downwind"))

    def test_refusals(self):
        f = _flame()
        with self.assertRaises(ValueError):
            jet_radiation.flux_kW_m2(f, 2.0, 10.0, 0.0, tau=1.5)
        with self.assertRaises(ValueError):
            jet_radiation.reach_m(f, 2.0, 12.5, "sideways")


class YbAnnex(unittest.TestCase):
    """The Annex prints its own values at 288.15 K; reproducing them checks the coefficient transcription."""
    PRINTED = {"propane": dict(rho=509.2712, vp=7.307659e5, hv=348160.99, cpl=2582.192, mu=1.030978e-4, sigma=8.154658e-3),
               "n-butane": dict(rho=584.4904, vp=1.821095e5, hv=362140.53, cpl=2457.016, mu=1.649110e-4, sigma=1.397065e-2)}

    def test_values_printed_in_the_annex_at_288_15_K(self):
        from process_safety import yb_annex as A
        for f, v in self.PRINTED.items():
            got = dict(rho=A.liquid_density_kg_m3(f, 288.15), vp=A.vapour_pressure_Pa(f, 288.15), hv=A.heat_of_vaporisation_J_kg(f, 288.15),
                       cpl=A.liquid_heat_capacity_J_kgK(f, 288.15), mu=A.liquid_viscosity_Pa_s(f, 288.15), sigma=A.surface_tension_N_m(f, 288.15))
            for k in v:
                self.assertAlmostEqual(got[k] / v[k], 1.0, delta=3e-4, msg=f"{f} {k}")

    def test_vapour_pressure_equals_ambient_at_the_boiling_point(self):
        from process_safety import yb_annex as A
        for f in ("propane", "n-butane"):
            self.assertAlmostEqual(A.vapour_pressure_Pa(f, A.normal_boiling_point_K(f)) / 101325.0, 1.0, delta=0.06)       # the Annex correlations are not exact at the boiling point (propane 0.5 %, butane 4 %)

    def test_saturation_temperature_inverts_vapour_pressure(self):
        from process_safety import yb_annex as A
        T = A.saturation_temperature_K("propane", 1.2e6)
        self.assertAlmostEqual(A.vapour_pressure_Pa("propane", T), 1.2e6, delta=1.0)

    def test_enthalpy_change_is_additive_and_antisymmetric(self):
        from process_safety import yb_annex as A
        a, b, c = 231.0, 260.0, 300.0
        self.assertAlmostEqual(A.liquid_enthalpy_change_J_kg("propane", a, c), A.liquid_enthalpy_change_J_kg("propane", a, b) + A.liquid_enthalpy_change_J_kg("propane", b, c), places=6)
        self.assertAlmostEqual(A.liquid_enthalpy_change_J_kg("propane", a, b), -A.liquid_enthalpy_change_J_kg("propane", b, a), places=9)

    def test_out_of_range_is_refused(self):
        from process_safety import yb_annex as A
        with self.assertRaises(ValueError):
            A.liquid_density_kg_m3("propane", 500.0)
        with self.assertRaises(ValueError):
            A.liquid_density_kg_m3("water", 300.0)


class YbSprayWorkedExample(unittest.TestCase):
    """The Yellow Book's own worked butane example (section 2.6.3.5, Table 2.6) is the oracle."""
    def setUp(self):
        from process_safety import yb_annex as A, yb_spray as S
        self.A, self.S = A, S
        self.jet = S.jet_after_flash(41.34, 0.00363, 174549, 101325, 0.0, 584.49, 4.233, 428806 - 473622, 362140, 376740, 600.72, 2.5964)
        self.dd = S.droplet_diameter_m(self.jet["b_f_m"], self.jet["u_f_m_s"], 0.000197, 600.72, 0.0159, 1.225, 288.15, 272.7)

    def test_step1_jet_state_matches_table(self):
        j = self.jet
        self.assertAlmostEqual(j["u_f_m_s"], 25.91, delta=0.01)
        self.assertAlmostEqual(j["Phi_f"], 0.15732, delta=2e-5)
        self.assertAlmostEqual(j["A_f_m2"], 0.099, delta=1e-3)
        self.assertAlmostEqual(j["b_f_m"], 0.177, delta=1e-3)

    def test_step2_droplet_diameter_matches_table(self):
        self.assertEqual(self.dd["branch"], "b")
        self.assertAlmostEqual(self.dd["d_d_m"] * 1000.0, 0.29, delta=0.005)
        self.assertAlmostEqual(self.dd["We_f"] / 9012339.0, 1.0, delta=2e-3)

    def test_step2_branch_a_for_small_weber_number(self):
        r = self.S.droplet_diameter_m(0.002, 5.0, 1e-6, 600.0, 0.02, 1.2, 280.0, 272.7)
        self.assertEqual(r["branch"], "a")
        self.assertAlmostEqual(r["d_d_m"], 3.78 * 0.002 * math.sqrt(1.0 + 3.0 * (2 * 0.002 * 25 * 600 / 0.02) / (2 * 0.002 * 5 / 1e-6)), places=12)
        hot = self.S.droplet_diameter_m(0.002, 5.0, 1e-6, 600.0, 0.02, 1.2, 320.0, 272.7)       # T_e above 1.11 T_B: the other branch
        self.assertEqual(hot["branch"], "b")
        self.assertAlmostEqual(hot["d_d_m"], 15.0 * 0.02 / (25.0 * 1.2), places=12)

    def test_step3_free_fall_droplet_temperature_and_no_rainout(self):
        A, S = self.A, self.S
        d = self.dd["d_d_m"]
        ud = S.free_fall_velocity_m_s(d, 600.72, 1.71e-5, 1.225, 9.8)
        Re = ud * d / 1.71e-5
        self.assertAlmostEqual(ud, 1.313, delta=0.005)
        self.assertAlmostEqual(Re, 22.25, delta=0.05)
        D = 1.71e-5 / 0.7
        kBf = lambda T: S.k_B_m2_s(0.0581, D, 101325, 600.72, 288.15, A.vapour_pressure_Pa("n-butane", T))
        Td, kB = S.droplet_temperature_K(288.15, Re, 0.7, 0.87, A.air_conductivity_W_mK(), lambda T: A.heat_of_vaporisation_J_kg("n-butane", T), 600.72, kBf, T_low_K=200.0)
        self.assertAlmostEqual(Td, 215.09, delta=0.5)           # air conductivity is not given in the book; ours is derived from its Prandtl number
        self.assertAlmostEqual(kB / 2.87e-8, 1.0, delta=0.03)
        r = S.rainout(jet=self.jet, d_d_m=d, q_kg_s=41.34, h_s_m=1.0, kB=kB, Sc=0.7, rho_L_f=600.72, rho_a=1.225, nu_a=1.71e-5, g=9.8)
        self.assertEqual(r["rainout_kg_s"], 0.0)                 # the book's "nett mass released to the air" equals the full 41.34 kg/s
        self.assertAlmostEqual(r["q_nett_air_kg_s"], 41.34, places=9)
        self.assertAlmostEqual(r["d_M_m"] * 1000.0, 0.47, delta=0.02)   # the book prints "47 mm": a misprint for 0.47 mm

    def test_energy_balance_closes_for_a_two_phase_exit(self):
        """Total enthalpy plus kinetic energy is conserved: H_V,e - (1-Phi_e) L_e + u_e^2/2 = H_V,f - (1-Phi_f) L_f + u_f^2/2."""
        S = self.S
        He, Hf, Le, Lf, Phi_e = 470000.0, 430000.0, 362000.0, 376000.0, 0.1
        j = S.jet_after_flash(30.0, 0.004, 400000.0, 101325.0, Phi_e, 584.0, 7.0, Hf - He, Le, Lf, 600.0, 2.6)
        lhs = He - (1 - Phi_e) * Le + 0.5 * j["u_e_m_s"] ** 2
        rhs = Hf - (1 - j["Phi_f"]) * Lf + 0.5 * j["u_f_m_s"] ** 2
        self.assertAlmostEqual(lhs, rhs, places=6)
        self.assertAlmostEqual(j["rho_e_kg_m3"], 1.0 / (0.9 / 584.0 + 0.1 / 7.0), places=9)

    def test_rainout_mass_is_the_liquid_fraction_times_diameter_ratio_cubed(self):
        S = self.S
        jet = {"Phi_f": 0.2}
        rho_a, nu_a, kB, h, rho_L, g = 1.225, 1.71e-5, 2.8e-8, 1.0, 600.0, 9.81
        d0 = 1.15 * (72 * rho_a * nu_a * kB * h / (rho_L * g)) ** 0.25
        r = S.rainout(jet=jet, d_d_m=d0, q_kg_s=10.0, h_s_m=h, kB=kB, Sc=1e-12, rho_L_f=rho_L, rho_a=rho_a, nu_a=nu_a, g=g)   # Sc -> 0 removes the convection term
        self.assertGreater(r["d_ground_m"], 0.0)
        self.assertLess(r["d_ground_m"], d0)
        self.assertAlmostEqual(r["rainout_kg_s"], 0.8 * 10.0 * (r["d_ground_m"] / d0) ** 3, places=12)
        self.assertAlmostEqual(r["rainout_kg_s"] + r["q_nett_air_kg_s"], 10.0, places=12)

    def test_flash_energy_balance_is_the_liquid_side_balance(self):
        A = self.A
        # for a saturated-liquid exit, (2.140) equals (h_L,e - h_L,f - KE)/L_f when dH_V = L_f - L_e - (h_L,e - h_L,f)
        Te, Tf = 288.15, 272.7
        Le, Lf = A.heat_of_vaporisation_J_kg("n-butane", Te), A.heat_of_vaporisation_J_kg("n-butane", Tf)
        dh = A.liquid_enthalpy_change_J_kg("n-butane", Tf, Te)
        dHv = Lf - Le - dh
        j = self.S.jet_after_flash(41.34, 0.00363, 174549, 101325, 0.0, 584.49, 4.233, dHv, Le, Lf, 600.72, 2.5964)
        ke = 0.5 * (j["u_f_m_s"] ** 2 - j["u_e_m_s"] ** 2)
        self.assertAlmostEqual(j["Phi_f"], (dh - ke) / Lf, places=9)


class YbMath(unittest.TestCase):
    def test_zeroth_order_max_rainout_diameter_from_the_integration(self):
        """With Stokes fall and no convection, d(d)/dt = -kB/d: the largest droplet that just evaporates on reaching the ground has
        d0^4 = 72 rho_a nu_a kB h / (rho_L g). Integrating (2.149)-(2.150) with the convection term removed must agree (Sc -> 0 removes it)."""
        from process_safety import yb_spray as S
        rho_a, nu_a, kB, h, rho_L, g = 1.225, 1.71e-5, 2.8e-8, 1.0, 600.0, 9.81
        d0 = (72 * rho_a * nu_a * kB * h / (rho_L * g)) ** 0.25
        below = S.fall_and_evaporate(d0 * 0.98, h, kB, 1e-12, rho_L, rho_a, nu_a, g)
        above = S.fall_and_evaporate(d0 * 1.02, h, kB, 1e-12, rho_L, rho_a, nu_a, g)
        self.assertEqual(below["d_ground_m"], 0.0)
        self.assertGreater(above["d_ground_m"], 0.0)

    def test_burning_flux_limits_and_equilibrium_balance(self):
        from process_safety import yb_poolfire as P
        self.assertAlmostEqual(P.burning_flux_kg_m2_s(50.0, 0.099, 1.4), 0.099, places=9)
        D = P.equilibrium_diameter_m(2.0, 0.099, 1.4)
        self.assertAlmostEqual(P.burning_flux_kg_m2_s(D, 0.099, 1.4) * math.pi * D * D / 4.0, 2.0, delta=1e-9)
        self.assertGreater(P.equilibrium_diameter_m(4.0, 0.099, 1.4), D)

    def test_flame_length_against_the_formula_and_wind_exponent(self):
        from process_safety import yb_poolfire as P
        D, m, rho = 3.0, 0.1, 1.2
        L0 = D * 55.0 * (m / (rho * math.sqrt(g_acc * D))) ** 0.67
        self.assertAlmostEqual(P.flame_length_m(D, m, rho, 0.0)["L_m"], L0, places=12)
        uc = (g_acc * m * D / rho) ** (1.0 / 3.0)
        w = P.flame_length_m(D, m, rho, 3.0 * uc)
        self.assertAlmostEqual(w["L_m"] / L0, 3.0 ** -0.21, places=12)
        self.assertEqual(P.flame_length_m(D, m, rho, 0.9 * uc)["L_m"], L0)           # below u_c the scaled wind speed is one

    def test_flame_length_grows_with_diameter_and_u_star_floor(self):
        from process_safety import yb_poolfire as P
        a = P.flame_length_m(3.0, 0.1, 1.2, 0.0)
        b = P.flame_length_m(6.0, 0.1, 1.2, 0.0)
        self.assertGreater(b["L_m"], a["L_m"])
        self.assertEqual(a["u_star"], 1.0)
        self.assertLess(P.flame_length_m(3.0, 0.1, 1.2, 8.0)["L_m"], a["L_m"])      # wind shortens the flame (u*^-0.21)

    def test_tilt_satisfies_its_defining_relation(self):
        from process_safety import yb_poolfire as P
        D, u, nu = 4.0, 5.0, 1.5e-5
        th = math.radians(P.flame_tilt_deg(D, u, nu))
        c = 0.666 * (u * u / (g_acc * D)) ** 0.333 * (u * D / nu) ** 0.117
        self.assertAlmostEqual(math.tan(th) / math.cos(th), c, places=9)
        self.assertEqual(P.flame_tilt_deg(D, 0.0, nu), 0.0)


class Vulnerability(unittest.TestCase):
    TABLE_5_1 = {0.01: 2.67, 0.1: 3.72, 0.2: 4.16, 0.5: 5.00, 0.7: 5.52, 0.9: 6.28, 0.99: 7.33}

    def test_probit_to_probability_matches_the_purple_book_table(self):
        from process_safety import vulnerability as V
        for P, Pr in self.TABLE_5_1.items():
            self.assertAlmostEqual(V.probability_from_probit(Pr), P, delta=0.003)

    def test_symmetry_and_monotonicity(self):
        from process_safety import vulnerability as V
        for z in (0.5, 1.0, 2.0):
            self.assertAlmostEqual(V.probability_from_probit(5 + z) + V.probability_from_probit(5 - z), 1.0, places=12)
        self.assertLess(V.death_probability(10.0), V.death_probability(20.0))
        self.assertLess(V.death_probability(10.0, 5.0), V.death_probability(10.0, 20.0))

    def test_norwegian_dsb_table_of_50_percent_fatality_fluxes(self):
        """DSB guideline (2021) Table 4.1, from the same TNO probit: the listed duration and flux pairs each give Pr = 5 (probability 0.5)."""
        from process_safety import vulnerability as V
        for t, q in ((610, 1.5), (415, 2.0), (242, 3.0), (165, 4.0), (122, 5.0), (49, 10.0), (28, 15.0)):
            self.assertAlmostEqual(V.heat_probit(q * 1000.0, t, cap_s=None), 5.0, delta=0.08, msg=f"{t} s at {q} kW/m2")
            self.assertAlmostEqual(V.death_probability(q, t, cap_s=None), 0.5, delta=0.04)

    def test_green_book_table_4_1_dose_values_for_the_eisenberg_form(self):
        """Dutch Green Book (PGS 1 Deel 1A, 2003) Table 4-1 B: the 1, 50 and 99 % lethality fluxes for pulse durations of 1.43, 10.1 and 45.2 s lie near probit 2.67, 5.00, 7.33 on eq. 4.1: the 50 % rows to 0.2, the 1 % and 99 % rows only to 0.45 (the equation fits the median; the tabulated tails imply a slope of about 2.5)."""
        from process_safety import vulnerability as V
        rows = [(1, 1.43, 146e3, 2.67), (1, 10.1, 33.1e3, 2.67), (1, 45.2, 10.2e3, 2.67), (50, 1.43, 263.6e3, 5.0), (50, 10.1, 57.95e3, 5.0), (50, 45.2, 18.5e3, 5.0),
                (99, 1.43, 586e3, 7.33), (99, 10.1, 128e3, 7.33), (99, 45.2, 39.8e3, 7.33)]
        for pct, t, q, pr in rows:
            self.assertAlmostEqual(V.heat_probit(q, t, cap_s=None, variant="eisenberg"), pr, delta=0.2 if pct == 50 else 0.45, msg=f"{pct} % at {t} s")

    def test_hydrocarbon_form_sits_above_eisenberg_by_the_ir_dose_factor(self):
        """Eq. 4.5 - eq. 4.1 = 2.10 in probit, i.e. the dose for the same lethality is lower by exp(2.10/2.56) = 2.27, close to the factor 2.23 the book cites for infrared against ultraviolet radiation."""
        from process_safety import vulnerability as V
        d = V.heat_probit(30000.0, 10.0) - V.heat_probit(30000.0, 10.0, variant="eisenberg")
        self.assertAlmostEqual(d, 2.10, places=9)
        self.assertAlmostEqual(math.exp(d / 2.56), 2.23, delta=0.06)
        self.assertGreater(V.death_probability(15.0, 20.0), V.death_probability(15.0, 20.0, variant="eisenberg"))
        with self.assertRaises(ValueError):
            V.heat_probit(30000.0, 10.0, variant="other")

    def test_thermal_dose_flux_round_trip_and_dutch_versus_uk_fifty_percent(self):
        from process_safety import vulnerability as V
        for dose, t in ((1000.0, 20.0), (2000.0, 20.0), (290.0, 10.0)):
            self.assertAlmostEqual(V.flux_for_thermal_dose_kW_m2(dose, t) ** (4.0 / 3.0) * t, dose, places=9)
        q50 = V.flux_for_probability_kW_m2(0.5)                       # Dutch hydrocarbon probit, 20 s
        self.assertAlmostEqual(q50 ** (4.0 / 3.0) * 20.0, 1040.0, delta=15.0)     # about half the UK offshore 2000 dose
        self.assertLess(q50, V.flux_for_thermal_dose_kW_m2(V.THERMAL_DOSE_CRITERIA["fatality_50pct_offshore"], 20.0))

    def test_dsb_form_is_the_same_probit(self):
        from process_safety import vulnerability as V
        for q, t in ((5.0, 30.0), (15.0, 12.0), (35.0, 5.0)):
            self.assertAlmostEqual(V.heat_probit(q * 1000.0, t, cap_s=None), -12.8 + 2.56 * math.log(t * q ** (4.0 / 3.0)), delta=0.01)

    def test_probit_literal_value(self):
        from process_safety import vulnerability as V
        self.assertAlmostEqual(V.heat_probit(20000.0, 20.0), -36.38 + 2.56 * math.log(20000.0 ** (4.0 / 3.0) * 20.0), places=12)

    def test_probit_time_and_flux_scaling(self):
        from process_safety import vulnerability as V
        self.assertAlmostEqual(V.heat_probit(1e4, 10.0) - V.heat_probit(1e4, 5.0), 2.56 * math.log(2.0), places=12)
        self.assertAlmostEqual(V.heat_probit(2e4, 10.0) - V.heat_probit(1e4, 10.0), 2.56 * (4.0 / 3.0) * math.log(2.0), places=12)
        self.assertEqual(V.heat_probit(1e4, 60.0), V.heat_probit(1e4, 20.0))          # exposure time capped at 20 s

    def test_inverse_round_trip(self):
        from process_safety import vulnerability as V
        for P in (0.01, 0.5, 0.9):
            self.assertAlmostEqual(V.death_probability(V.flux_for_probability_kW_m2(P)), P, places=9)

    def test_clothing_and_building_threshold(self):
        from process_safety import vulnerability as V
        self.assertEqual(V.outdoor_fatality_fraction(35.0), 1.0)
        self.assertAlmostEqual(V.outdoor_fatality_fraction(20.0), 0.14 * V.death_probability(20.0), places=12)

    def test_table_4_5_bands(self):
        from process_safety import vulnerability as V
        self.assertEqual(V.direct_ignition_probability(5, "gas_average_high"), 0.2)
        self.assertEqual(V.direct_ignition_probability(50, "gas_average_high"), 0.5)
        self.assertEqual(V.direct_ignition_probability(500, "gas_average_high"), 0.7)
        self.assertEqual(V.direct_ignition_probability(5, "k1_liquid"), 0.065)
        self.assertEqual(V.direct_ignition_probability(9.99, "gas_low"), 0.02)
        self.assertEqual(V.direct_ignition_probability(10.0, "gas_low"), 0.04)
        self.assertEqual(V.direct_ignition_probability(100.0, "gas_low"), 0.04)
        self.assertEqual(V.direct_ignition_probability(100.5, "gas_low"), 0.09)
        with self.assertRaises(ValueError):
            V.direct_ignition_probability(5, "plasma")


class LeungOmegaPrimaryText(unittest.TestCase):
    """Leung, 'Easily Size Relief Devices and Piping for Two-Phase Flow', Chemical Engineering Progress 92(12), Dec 1996 (page images read from the owner's Drive copy):
    eq. 28a v/v0 = w (P0/P - 1) + 1; eq. 29a (saturated liquid) w = (cp T0 P0 / v0)(v_fg0/h_fg0)^2; eq. 31 nozzle flux; eq. 32 the transcendental equation for the
    critical ratio; eq. 33 G_c / sqrt(P0 rho0) = eta_c / sqrt(w); eq. 35 and 37 the limits w = 1 (eta_c = 0.606) and w = 0 (Bernoulli)."""
    OMEGAS = (0.5, 1.0, 2.0, 6.41, 20.0, 100.0)

    def test_critical_ratio_satisfies_equation_32(self):
        from process_safety import twophase
        for w in self.OMEGAS:
            e = twophase.critical_pressure_ratio(w)
            resid = e ** 2 + (w * w - 2 * w) * (1 - e) ** 2 + 2 * w * w * math.log(e) + 2 * w * w * (1 - e)
            self.assertAlmostEqual(resid / (2.0 * w * w), 0.0, delta=1e-8, msg=f"omega {w}")      # residual scaled by the size of the omega^2 terms

    def test_choked_flux_equals_equation_33(self):
        from process_safety import twophase
        P0, rho0 = 1.2e6 / 1000.0, 477.0                    # kPa, kg/m3
        for w in self.OMEGAS:
            m = twophase.mass_flux(P0, rho0, w)
            self.assertAlmostEqual(m["G_kg_m2_s"], m["eta_critical"] * math.sqrt(P0 * 1000.0 * rho0 / w), delta=1e-6 * m["G_kg_m2_s"], msg=f"omega {w}")

    def test_equation_35_limit_omega_one(self):
        from process_safety import twophase
        self.assertAlmostEqual(twophase.critical_pressure_ratio(1.0), 0.606, delta=1e-3)          # Leung's 0.606 is the k = 1.001 value
        self.assertAlmostEqual(twophase.critical_pressure_ratio(1.0), math.exp(-0.5), places=7)  # the exact omega = 1 limit

    def test_equation_37_limit_small_omega_is_bernoulli(self):
        from process_safety import twophase
        P0, rho0 = 1000.0, 600.0
        m = twophase.mass_flux(P0, rho0, 1e-6, P_back_kPa=500.0)
        self.assertAlmostEqual(m["G_kg_m2_s"], math.sqrt(2.0 * rho0 * (P0 - 500.0) * 1000.0), delta=2e-3 * m["G_kg_m2_s"])

    def test_equation_29a_matches_the_toolkit_saturated_omega(self):
        from process_safety import twophase
        cp, T, P, vl, vg, hfg = 2835.0, 307.58, 1.2e6, 1 / 477.0, 1 / 26.24, 318119.0
        v_lg = vg - vl
        self.assertAlmostEqual(twophase.omega_saturated_liquid(cp, T, P, vl, v_lg, hfg), (cp * T * P / vl) * (v_lg / hfg) ** 2, places=9)

    def test_equation_28a_is_the_two_point_omega(self):
        from process_safety import twophase
        v0, v9 = 2.0e-3, 2.18e-3
        w = twophase.omega_two_point(v0, v9)
        self.assertAlmostEqual(v9 / v0, w * (1.0 / 0.9 - 1.0) + 1.0, places=12)


class IgnitionUkooa(unittest.TestCase):
    def test_all_thirty_curves_load_and_are_non_decreasing_after_sorting(self):
        from process_safety import ignition_ukooa as U
        self.assertEqual(sorted(U.CASES), list(range(1, 31)))
        for c in U.CASES:
            pts = U.points(c)
            self.assertTrue(all(b[1] >= a[1] - 1e-12 for a, b in zip(pts, pts[1:])), U.CASES[c][0])
            self.assertEqual(pts[-1][0], 100000.0)

    def test_interpolation_equation_at_nodes_and_midpoint(self):
        from process_safety import ignition_ukooa as U
        pts = U.points(8)
        for q, p in pts:
            self.assertAlmostEqual(U.ignition_probability(q, 8), p, places=12)
        (q0, p0), (q1, p1) = pts[3], pts[4]                # 1 kg/s and 100 kg/s
        self.assertAlmostEqual(U.ignition_probability(math.sqrt(q0 * q1), 8), math.sqrt(p0 * p1), places=12)   # geometric mean in log-log space

    def test_constant_beyond_the_end_points(self):
        from process_safety import ignition_ukooa as U
        self.assertEqual(U.ignition_probability(1e-6, 5), U.points(5)[0][1])
        self.assertEqual(U.ignition_probability(1e7, 5), U.points(5)[-1][1])

    def test_table_1_maximum_probabilities_equal_the_last_point(self):
        """Table 1 of the same paper lists each curve's maximum probability; it equals the last point of the Table 2 transcription."""
        from process_safety import ignition_ukooa as U
        table_1_max = {1: 0.07, 2: 0.007, 3: 1.0, 4: 1.0, 5: 0.6, 6: 0.1, 7: 0.013, 8: 0.65, 9: 0.13, 10: 0.05, 11: 0.7, 12: 0.12, 13: 0.015, 14: 1.0, 15: 1.0,
                       16: 0.5, 17: 0.0175, 18: 0.01, 19: 0.025, 20: 0.04, 21: 0.05, 22: 0.04, 23: 0.025, 24: 0.15, 25: 0.15, 26: 0.028, 27: 0.1, 28: 0.3, 29: 0.08, 30: 0.0024}
        for c, mx in table_1_max.items():
            self.assertAlmostEqual(U.points(c)[-1][1], mx, places=9, msg=U.CASES[c][0])

    def test_gas_liquid_combination(self):
        from process_safety import ignition_ukooa as U
        self.assertAlmostEqual(U.combine_gas_and_liquid(0.1, 0.2), 1 - 0.9 * 0.8, places=12)
        self.assertAlmostEqual(U.combine_gas_and_liquid(0.0, 0.3), 0.3, places=12)
        with self.assertRaises(ValueError):
            U.combine_gas_and_liquid(1.2, 0.1)

    def test_cox_curves_in_the_paper_match_the_toolkit_cox_values_in_their_bands(self):
        """The paper's curve 28 (Cox, Lees and Ang gas) holds 0.30 above 100 kg/s; the toolkit's Cox table has 0.30 above 50 kg/s."""
        from process_safety import ignition_ukooa as U
        from process_safety.qra import frequency as F
        self.assertEqual(U.ignition_probability(200.0, 28), F.cox_ignition(200.0, "gas"))


class StepValidation(unittest.TestCase):
    """EEC STEP propane flashing-jet measurements as summarised in HSE CRR 403/2002 (read through an archived copy): saturated propane released from 2 and 5 mm
    orifices at 5, 11 and 17 bar; measured Sauter mean diameters at 60 mm downstream were 39 to 49 micrometres (5 bar), 30 to 31 (11 bar) and below 30 (17 bar);
    no droplet above 80 micrometres at 5 bar; the report concludes very little rain-out is expected at 11 bar. Pressures are taken as absolute here (the summary does
    not say; a 1 bar shift changes the prediction by well under the margins below)."""
    def _d(self, bar, basis):
        path = os.path.join(os.path.dirname(tools.__file__), "examples", "lgrelease.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        data.update(P0_kPa=bar * 100.0, hole_d_m=0.005, discharge_basis=basis)
        from process_safety import lg_release
        return lg_release.run(data)["droplet"]

    def test_liquid_orifice_basis_is_within_a_factor_of_two_of_the_measured_mean_sizes(self):
        for bar, lo, hi in ((5, 39.0, 49.0), (11, 30.0, 31.0)):
            d = self._d(bar, "yellow_book_liquid")["d_d_m"] * 1e6
            self.assertGreater(d, lo / 2.0, f"{bar} bar")
            self.assertLess(d, hi * 2.0, f"{bar} bar")

    def test_no_rainout_predicted_where_the_measurements_show_little(self):
        for basis in ("omega", "yellow_book_liquid"):
            self.assertEqual(self._d(11, basis)["rainout_kg_s"], 0.0)

    def test_predicted_droplets_decrease_with_pressure_as_measured(self):
        for basis in ("omega", "yellow_book_liquid"):
            d = [self._d(b, basis)["d_d_m"] for b in (5, 11, 17)]
            self.assertTrue(d[0] > d[1] > d[2])


class LgReleaseTool(unittest.TestCase):
    def _run(self, name):
        path = os.path.join(os.path.dirname(tools.__file__), "examples", "lgrelease.json")
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        if name == "B":
            data.update(mode="refrigerated", overpressure_kPa_g=10.0, head_m=5.0)
            data.pop("P0_kPa")
        if name == "C":
            data["discharge_basis"] = "yellow_book_liquid"
        out = tempfile.mkdtemp()
        try:
            return tools.run_tool("lgrelease", data, out, progress=False)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_saturated_omega_example_passes_its_checks(self):
        s = self._run("A")
        self.assertFalse([c for c in s["checks"] if c.startswith("FAIL")])
        self.assertAlmostEqual(s["release"]["W_kg_s"], 2.34, delta=0.02)
        self.assertEqual(s["droplet"]["rainout_kg_s"], 0.0)
        self.assertIsNotNone(s["jet"])
        self.assertEqual(s["pool"], [])

    def test_both_discharge_bases_are_reported_and_yellow_book_is_larger(self):
        s = self._run("A")
        self.assertGreater(s["discharge"]["yellow_book_liquid"]["W_kg_s"], 3.0 * s["discharge"]["omega"]["W_kg_s"])

    def test_yellow_book_basis_gives_larger_flame(self):
        a, c = self._run("A"), self._run("C")
        self.assertFalse([x for x in c["checks"] if x.startswith("FAIL")])
        self.assertGreater(c["jet"]["flame"]["L_B_m"], a["jet"]["flame"]["L_B_m"])
        self.assertGreater(c["jet"]["reach_m"]["P_death_1pct"]["downwind"], a["jet"]["reach_m"]["P_death_1pct"]["downwind"])

    def test_refrigerated_has_pool_and_no_jet(self):
        s = self._run("B")
        self.assertFalse([c for c in s["checks"] if c.startswith("FAIL")])
        self.assertIsNone(s["jet"])
        self.assertGreater(s["droplet"]["rainout_fraction_of_release"], 0.5)
        p = s["pool"][0]
        self.assertAlmostEqual(p["feed_kg_s"], s["droplet"]["rainout_kg_s"], places=9)
        self.assertTrue(p["from_yellow_book_method"])

    def test_three_ignition_models_are_reported(self):
        ig = self._run("A")["ignition"]
        self.assertEqual(ig["purple_book_direct_ignition"], 0.2)
        self.assertEqual(ig["cox_lees_ang_total_ignition"], 0.07)
        self.assertEqual(len(ig["ukooa_total_ignition"]), 3)
        self.assertTrue(all(0 < v < 0.05 for v in ig["ukooa_total_ignition"].values()))

    def test_missing_inputs_are_refused(self):
        s = tools.run_tool("lgrelease", {"fluid": "propane"}, tempfile.mkdtemp(), progress=False)
        self.assertTrue(any(c.startswith("FAIL") for c in s["checks"]))


if __name__ == "__main__":
    unittest.main()

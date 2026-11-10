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


class LgReleaseTool(unittest.TestCase):
    def _run(self, name):
        path = os.path.join(os.path.dirname(tools.__file__), "examples", "lgrelease.json")
        data = json.load(open(path))
        if name == "B":
            data.update(mode="refrigerated", overpressure_kPa_g=10.0, head_m=5.0)
            data.pop("P0_kPa"); data["properties"] = {}
        out = tempfile.mkdtemp()
        try:
            return tools.run_tool("lgrelease", data, out, progress=False)
        finally:
            shutil.rmtree(out, ignore_errors=True)

    def test_saturated_example_passes_its_checks(self):
        s = self._run("A")
        self.assertFalse([c for c in s["checks"] if c.startswith("FAIL")])
        self.assertAlmostEqual(s["release"]["W_kg_s"], 2.3368, delta=2e-3)
        self.assertEqual(s["droplet"]["lautkaski"], 0.0)
        self.assertIsNotNone(s["jet"])

    def test_refrigerated_has_pool_and_no_jet(self):
        s = self._run("B")
        self.assertFalse([c for c in s["checks"] if c.startswith("FAIL")])
        self.assertIsNone(s["jet"])
        self.assertEqual(s["droplet"]["kletz"], 1.0)
        self.assertTrue(s["pool"])
        big = max(s["pool"], key=lambda p: p["rainout_fraction"])
        self.assertAlmostEqual(big["feed_kg_s"], big["rainout_fraction"] * s["release"]["W_kg_s"], places=9)

    def test_missing_inputs_are_refused(self):
        s = tools.run_tool("lgrelease", {"fluid": "propane"}, tempfile.mkdtemp(), progress=False)
        self.assertTrue(any(c.startswith("FAIL") for c in s["checks"]))


if __name__ == "__main__":
    unittest.main()

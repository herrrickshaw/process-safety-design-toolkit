"""Refusals of bad input, and behaviour of branches in the release, fire and explosion chain that no other test runs.

No remembered result values: each test checks a refusal, an identity or a monotonic relation. The numbers used as inputs are arbitrary
test inputs, not property data.
"""
import copy
import json
import os
import unittest

from process_safety import (bleve, droplet, flash_release, ignition_ukooa, jet_radiation, lg_release, line_flow, pool_spread,
                            props_ref, release_frequency, vce, vulnerability, yb_annex, yb_poolfire, yb_spray)

EXAMPLE = os.path.join(os.path.dirname(lg_release.__file__), "examples", "lgrelease.json")


def example():
    with open(EXAMPLE, encoding="utf-8") as fh:
        return json.load(fh)


class Refusals(unittest.TestCase):
    def refuses(self, cases):
        for pattern, func, args in cases:
            with self.subTest(func=func.__name__, pattern=pattern, args=args):
                with self.assertRaisesRegex(ValueError, pattern):
                    func(*args)

    def test_droplet(self):
        self.refuses([
            ("pressures and specific volume", droplet.partial_expansion_energy_J_kg, (1e5, 2e5, 1e-3, 1e5, -1e3)),
            ("constants must be positive", droplet.schiller_naumann, (0.0, 1.0)),
            ("sigma must be positive", droplet.weber_max_diameter_m, (0.0, 50.0, 1.2, 12.5)),
            ("d must be positive", droplet.evaporation_time_s, (0.0, 500.0, 4e5, 0.026, 40.0)),
            ("d must be positive", droplet.terminal_velocity_m_s, (0.0, 500.0, 1.2, 1.8e-5)),
            ("denser than the gas", droplet.terminal_velocity_m_s, (1e-4, 1.0, 1.2, 1.8e-5)),
            ("did not bracket", droplet.terminal_velocity_m_s, (1e-2, 1e4, 1.0, 1e-5, lambda Re: 1e-12)),
            ("fall height", droplet.critical_diameter_m, (0.0, 500.0, 1.2, 1.8e-5, 4e5, 0.026, 40.0)),
            ("no crossover", droplet.critical_diameter_m, (1e12, 500.0, 1.2, 1.8e-5, 4e5, 0.026, 40.0)),
            ("cp and latent heat", droplet.isenthalpic_flash_fraction, (0.0, 300.0, 230.0, 4e5)),
        ])

    def test_fireball_and_explosion(self):
        self.refuses([
            ("filling degree", bleve.released_mass_kg, (10.0, 1.5, 500.0)),
            ("vapour pressure", bleve.radiated_fraction, (0.0,)),
            (r"tau must be in", bleve.transmissivity, (None, 1.2)),
            ("pw_x or a constant", bleve.transmissivity, ()),
            ("reactivity", bleve.direct_ignition_probability, (500.0, "medium")),
            ("mass must be positive", bleve.direct_ignition_probability, (0.0,)),
            ("flash fraction", bleve.cloud_mass_fraction, (1.1,)),
            ("heat of combustion", vce.combustion_energy_J, (-1.0, 4.6e7)),
            ("LFL must be", vce.lfl_mass_fraction, (1.0, 44.0)),
            ("all inputs", vce.jet_flammable_mass_kg, (0.0, 0.1, 100.0, 0.03)),
        ])

    def test_pool_and_spray(self):
        self.refuses([
            ("r0 must be positive", pool_spread.spread, (1.0, 500.0, 1.2, 0.1, 0.0, 0.1, 1.0)),
            ("must not be negative", pool_spread.spread, (-1.0, 500.0, 1.2, 0.1, 0.5, 0.1, 1.0)),
            ("k_beta must be positive", yb_poolfire.burning_flux_kg_m2_s, (0.0, 0.1, 1.4)),
            ("feed must be positive", yb_poolfire.equilibrium_diameter_m, (0.0, 0.1, 1.4)),
            ("q must be positive", yb_spray.jet_after_flash, (0.0, 1e-4, 1e6, 1e5, 0.0, 500.0, 20.0, 0.0, 3e5, 4e5, 580.0, 2.4)),
            ("Phi_e must be", yb_spray.jet_after_flash, (1.0, 1e-4, 1e6, 1e5, 1.0, 500.0, 20.0, 0.0, 3e5, 4e5, 580.0, 2.4)),
            ("after flashing", yb_spray.jet_after_flash, (1.0, 1e-4, 1e6, 1e5, 0.0, 500.0, 20.0, 1e7, 3e5, 4e5, 580.0, 2.4)),
            ("not bracketed", yb_spray.droplet_temperature_K, (290.0, 1.0, 0.7, 0.7, 0.025, lambda T: 4e5, 500.0, lambda T: 0.0, 300.0)),
        ])

    def test_radiation_and_harm(self):
        flame = {"alpha_deg": 0.0, "B_m": 0.0, "R_L_m": 10.0, "radiated_power_kW": 1e4}
        self.refuses([
            ("n must be at least 1", jet_radiation.source_points, (flame, 1.0, 0)),
            ("coincides", jet_radiation.flux_kW_m2, (flame, 0.0, 0.0, 0.0, 5.0, 1.0, 1)),
            ("threshold must be positive", jet_radiation.reach_m, (flame, 1.0, 0.0, "downwind")),
            ("still above the threshold", jet_radiation.reach_m, (flame, 1.0, 1e-9, "downwind", 1.5, 1.0, 60, 20.0)),
            ("Q and t", vulnerability.heat_probit, (0.0, 20.0)),
            ("P must be between", vulnerability.flux_for_probability_kW_m2, (1.0,)),
            ("rate must be positive", vulnerability.direct_ignition_probability, (0.0, "gas_low")),
            ("dose and time", vulnerability.flux_for_thermal_dose_kW_m2, (0.0, 20.0)),
        ])

    def test_ignition_and_frequency(self):
        self.refuses([
            ("case must be 1 to 30", ignition_ukooa.points, (31,)),
            ("rate must be positive", ignition_ukooa.ignition_probability, (0.0, 1)),
        ])

    def test_frequency_sheet_without_the_period(self):
        sheet, period = next((n, p) for n, v in release_frequency.POWER.items() for p in release_frequency.PERIODS if p not in v)
        with self.assertRaisesRegex(ValueError, "only for the periods"):
            release_frequency.exceedance(sheet, 100.0, 10.0, period)

    def test_property_ranges(self):
        lo_p = props_ref._TABLE["propane"][0][1]
        self.refuses([
            ("outside the tabulated vapour-pressure range", props_ref.saturation_temperature_K, ("propane", lo_p / 2.0)),
            ("outside the vapour-pressure range", yb_annex.saturation_temperature_K, ("propane", 1.0)),
        ])
        extra = next(iter(props_ref._MUV))
        with self.assertRaisesRegex(ValueError, "outside the tabulated range"):
            props_ref.vapour_viscosity_Pa_s(extra, props_ref._MUV[extra][-1][0] + 1.0)

    def test_flash_fraction_outside_range(self):
        with self.assertRaisesRegex(ValueError, r"flash fraction .* is outside"):
            # almost no superheat: the jet's kinetic energy exceeds it
            flash_release.saturated_liquid_release(1000.0, 500.0, 5.0, 1e-4, 0.62, 231.001, 231.0, 2500.0, 4.2e5, 580.0, 2.4)

    def test_line_flow(self):
        T0 = 290.0
        P0 = props_ref.vapour_pressure_Pa("propane", T0)
        with self.assertRaisesRegex(ValueError, "props must be"):
            line_flow.line_discharge("propane", T0, P0, 101325.0, [(1.0, 0.05)], props="other")
        with self.assertRaisesRegex(ValueError, "even a trickle"):
            line_flow.line_discharge("propane", T0, 101325.1, 101325.0, [(1e9, 1e-5)])


class Fireball(unittest.TestCase):
    ARGS = (1000.0, 1e6, 4.6e7, 4e5, 2500.0)      # mass kg, vapour pressure Pa, dHc, dHv, cp

    def test_a_constant_transmissivity_is_returned_unchanged(self):
        self.assertEqual(bleve.transmissivity(constant=0.8), 0.8)

    def test_stated_range_of_the_transmissivity_formula(self):
        self.assertTrue(bleve.transmissivity_in_range(5e4))
        self.assertFalse(bleve.transmissivity_in_range(5e3))
        self.assertFalse(bleve.transmissivity_in_range(5e5))

    def test_no_distance_when_the_target_flux_is_never_reached(self):
        peak = bleve.flux_W_m2(*self.ARGS, 0.0)["q_W_m2"]
        self.assertIsNone(bleve.distance_to_flux_m(*self.ARGS, 1.01 * peak))
        x = bleve.distance_to_flux_m(*self.ARGS, 0.5 * peak)
        self.assertAlmostEqual(bleve.flux_W_m2(*self.ARGS, x)["q_W_m2"], 0.5 * peak, delta=1e-6 * peak)


class DropletScreen(unittest.TestCase):
    BASE = dict(sigma_N_m=0.007, u_f_m_s=60.0, rho_air=1.2, mu_air=1.8e-5, k_air=0.026, We_crit=12.5, rho_L=500.0, h_fg_J_kg=4e5,
                dT_K=40.0, fall_height_m=1.22, superheated=False, x_isenthalpic=0.2)

    def screen(self, **changes):
        return droplet.screen(**{**self.BASE, **changes})

    def test_subcooled_uses_the_weber_size_and_kletz_gives_full_rainout(self):
        out = self.screen()
        self.assertIsNone(out["d_flashing_smd_m"])
        self.assertEqual(out["d_used_m"], out["d_weber_max_m"])
        self.assertAlmostEqual(out["d_over_d_critical"], out["d_used_m"] / out["d_critical_m"])
        self.assertEqual(out["kletz"], 1.0)
        self.assertNotIn("validity_warnings", out)

    def test_superheated_with_expansion_energy_uses_the_flashing_size(self):
        out = self.screen(superheated=True, Ep_J_kg=2e4)
        self.assertEqual(out["d_used_m"], droplet.flashing_smd_m(2e4))
        self.assertEqual(out["kletz"], droplet.rainout_kletz(0.2, False))

    def test_verdict_follows_the_size_ratio(self):
        d_crit = self.screen()["d_critical_m"]
        verdicts = []
        for ratio in (0.1, 1.0, 10.0):
            # We_crit scales the Weber diameter linearly, so it sets the ratio directly
            We = ratio * d_crit * self.BASE["u_f_m_s"] ** 2 * self.BASE["rho_air"] / self.BASE["sigma_N_m"]
            out = self.screen(We_crit=We)
            self.assertAlmostEqual(out["d_over_d_critical"], ratio)
            verdicts.append(out["verdict"])
        self.assertIn("expected small", verdicts[0])
        self.assertIn("uncertain", verdicts[1])
        self.assertIn("significant rainout", verdicts[2])

    def test_validity_warnings_appear_when_the_orifice_and_pressure_are_given(self):
        out = self.screen(orifice_mm=25.0, P_kPa=500.0)
        self.assertEqual(len(out["validity_warnings"]), 1)
        self.assertIn("orifice", out["validity_warnings"][0])


class ReleaseInput(unittest.TestCase):
    def errors(self, change):
        data = example()
        change(data)
        return "\n".join(lg_release.check(data))

    def test_worked_example_is_accepted(self):
        self.assertEqual(lg_release.check(example()), [])

    def test_each_bad_field_is_named(self):
        def drop(key):
            return lambda d: d.pop(key, None)

        def put(path, value):
            def change(d):
                *head, last = path
                for k in head:
                    d = d.setdefault(k, {})
                d[last] = value
            return change

        def saturated_without_pressure(d):
            d["mode"] = "saturated"
            d.pop("P0_kPa", None)

        def refrigerated_without_head(d):
            d["mode"] = "refrigerated"
            d.pop("head_m", None)

        def line_in_refrigerated(d):
            d.update(mode="refrigerated", line={"segments": [[1.0, 0.05]]})

        for expected, change in [
            ("fluid must be one of", put(["fluid"], "water")),
            ("ammonia: this chain", put(["fluid"], "ammonia")),
            ("missing section 'pool'", drop("pool")),
            ("needs P0_kPa", saturated_without_pressure),
            ("needs overpressure_kPa_g and head_m", refrigerated_without_head),
            ("discharge_basis must be", put(["discharge_basis"], "other")),
            ("line.segments must be", put(["line"], {"segments": []})),
            ("line is only implemented", line_in_refrigerated),
            ("frequency.D_mm and frequency.count", put(["frequency"], {"sheet": min(release_frequency.equipment_types()), "D_mm": 0})),
            ("frequency.period must be", put(["frequency"], {"sheet": min(release_frequency.equipment_types()), "D_mm": 100, "period": "x"})),
            ("fire.probit must be", put(["fire", "probit"], "other")),
            ("only a vertical release", put(["fire", "release_angle_deg"], 0)),
        ]:
            with self.subTest(expected=expected):
                self.assertIn(expected, self.errors(change))

    def test_extra_fluid_needs_the_reference_basis_and_a_heat_of_combustion(self):
        data = example()
        data.update(fluid="isobutane", property_basis="yb_annex")
        data["fire"].pop("Hc_J_kg", None)
        text = "\n".join(lg_release.check(data))
        self.assertIn("only property_basis 'reference'", text)
        self.assertIn("supply fire.Hc_J_kg", text)

    def test_extra_fluid_without_burning_constants_warns_instead_of_computing_a_pool_fire(self):
        data = copy.deepcopy(example())
        data.update(fluid="isobutane", property_basis="reference")
        data["fire"]["Hc_J_kg"] = 4.5e7
        data["pool"]["extra_rainout_fractions"] = [0.1]
        data.pop("frequency", None)
        out = lg_release.run(data)
        self.assertEqual(out["pool"], [])
        self.assertTrue(any("pool fire not computed" in w for w in out["warnings"]))


if __name__ == "__main__":
    unittest.main()

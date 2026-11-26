"""Droplet screen, input guards of the liquefied-gas release chain and BLEVE guards."""
import copy
import json
import math
import os
import unittest

from process_safety import bleve, droplet, lg_release

EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "process_safety", "examples", "lgrelease.json")


def _example():
    with open(EXAMPLE, encoding="utf-8") as fh:
        return json.load(fh)


# Illustrative round numbers, not property data: the tests below are identities between the function's own outputs.
SCREEN = dict(sigma_N_m=0.015, u_f_m_s=60.0, rho_air=1.2, mu_air=1.8e-5, k_air=0.025, We_crit=12.5, rho_L=580.0, h_fg_J_kg=4.2e5,
              dT_K=50.0, fall_height_m=1.22, superheated=False, x_isenthalpic=0.2)


class DropletScreen(unittest.TestCase):
    def test_critical_diameter_balances_evaporation_and_fall(self):
        r = droplet.screen(**SCREEN)
        d = r["d_critical_m"]
        t_evap = droplet.evaporation_time_s(d, SCREEN["rho_L"], SCREEN["h_fg_J_kg"], SCREEN["k_air"], SCREEN["dT_K"])
        t_fall = SCREEN["fall_height_m"] / droplet.terminal_velocity_m_s(d, SCREEN["rho_L"], SCREEN["rho_air"], SCREEN["mu_air"])
        self.assertAlmostEqual(t_evap / t_fall, 1.0, places=6)
        self.assertAlmostEqual(r["d_over_d_critical"], r["d_used_m"] / d)

    def test_subcooled_uses_mechanical_size_and_superheated_uses_flashing_size(self):
        cold = droplet.screen(**SCREEN, Ep_J_kg=2.0e4)
        self.assertIsNone(cold["d_flashing_smd_m"])
        self.assertEqual(cold["d_used_m"], cold["d_weber_max_m"])
        self.assertEqual(cold["kletz"], 1.0)
        hot = droplet.screen(**{**SCREEN, "superheated": True}, Ep_J_kg=2.0e4)
        self.assertEqual(hot["d_used_m"], droplet.flashing_smd_m(2.0e4))
        self.assertEqual(hot["kletz"], droplet.rainout_kletz(SCREEN["x_isenthalpic"], False))
        no_ep = droplet.screen(**{**SCREEN, "superheated": True})
        self.assertEqual(no_ep["d_used_m"], no_ep["d_weber_max_m"])

    def test_verdict_follows_the_diameter_ratio(self):
        seen = {}
        for u in (5.0, 10.0, 20.0, 30.0, 45.0, 60.0, 90.0, 150.0, 300.0):
            r = droplet.screen(**{**SCREEN, "u_f_m_s": u})
            ratio = r["d_over_d_critical"]
            band = "small" if ratio < 0.5 else "uncertain" if ratio < 2.0 else "significant"
            self.assertIn(band, r["verdict"])
            seen[band] = True
        self.assertEqual(set(seen), {"small", "uncertain", "significant"})

    def test_validity_warnings_only_with_orifice_and_pressure(self):
        self.assertNotIn("validity_warnings", droplet.screen(**SCREEN))
        self.assertEqual(droplet.screen(**SCREEN, orifice_mm=6.35, P_kPa=500.0)["validity_warnings"], [])
        bad = droplet.screen(**{**SCREEN, "fall_height_m": 5.0}, orifice_mm=25.0, P_kPa=2000.0, horizontal=False)
        self.assertEqual(len(bad["validity_warnings"]), 4)

    def test_expansion_energy_cases(self):
        ep = droplet.partial_expansion_energy_J_kg
        # continuous where the two-phase and superheated-liquid cases meet; subcooled is pure pressure work
        self.assertAlmostEqual(ep(8e5, 1e5, 2e-3, 8e5, -900.0), ep(8e5, 1e5, 2e-3, 8e5 * (1 - 1e-12), -900.0), places=5)
        self.assertAlmostEqual(ep(8e5, 1e5, 2e-3, 0.5e5, -900.0), 7e5 * 2e-3)

    def test_refusals(self):
        for call in (lambda: droplet.weber_max_diameter_m(0.0, 1.0, 1.2, 12.5),
                     lambda: droplet.partial_expansion_energy_J_kg(1e5, 2e5, 1e-3, 1e5, 0.0),
                     lambda: droplet.schiller_naumann(0.0, 1.0),
                     lambda: droplet.evaporation_time_s(1e-4, 580.0, 4e5, 0.025, 0.0),
                     lambda: droplet.terminal_velocity_m_s(-1e-4, 580.0, 1.2, 1.8e-5),
                     lambda: droplet.terminal_velocity_m_s(1e-4, 1.0, 1.2, 1.8e-5),
                     lambda: droplet.terminal_velocity_m_s(1e-4, 580.0, 1.2, 1.8e-5, drag=lambda Re: 0.0),
                     lambda: droplet.critical_diameter_m(0.0, 580.0, 1.2, 1.8e-5, 4e5, 0.025, 50.0),
                     lambda: droplet.critical_diameter_m(1e12, 580.0, 1.2, 1.8e-5, 4e5, 0.025, 50.0),
                     lambda: droplet.isenthalpic_flash_fraction(0.0, 288.0, 231.0, 4e5)):
            with self.assertRaises(ValueError):
                call()


class BleveGuards(unittest.TestCase):
    def test_refusals(self):
        for call in (lambda: bleve.released_mass_kg(10.0, 1.5, 500.0),
                     lambda: bleve.radiated_fraction(0.0),
                     lambda: bleve.transmissivity(constant=1.2),
                     lambda: bleve.transmissivity(),
                     lambda: bleve.direct_ignition_probability(100.0, "medium"),
                     lambda: bleve.direct_ignition_probability(0.0),
                     lambda: bleve.cloud_mass_fraction(1.1)):
            with self.assertRaises(ValueError):
                call()

    def test_constant_transmissivity_and_unreachable_flux(self):
        self.assertEqual(bleve.transmissivity(constant=0.8), 0.8)
        self.assertIsNone(bleve.distance_to_flux_m(1000.0, 1.4e6, 4.6e7, 3.7e5, 2500.0, 1e12))


class ReleaseInputGuards(unittest.TestCase):
    def _errors(self, **changes):
        data = copy.deepcopy(_example())
        for key, value in changes.items():
            if isinstance(value, dict) and isinstance(data.get(key), dict):
                data[key].update(value)
            else:
                data[key] = value
        return "\n".join(lg_release.check(data))

    def test_shipped_example_is_accepted(self):
        self.assertEqual(lg_release.check(_example()), [])

    def test_each_bad_input_is_named(self):
        cases = [
            ({"fluid": "water"}, "fluid must be one of"),
            ({"fluid": "isobutane", "property_basis": "yb_annex"}, "only property_basis 'reference'"),
            ({"mode": "refrigerated"}, "needs overpressure_kPa_g and head_m"),
            ({"discharge_basis": "hem"}, "discharge_basis must be"),
            ({"line": {"segments": [[10.0, 0.0]]}}, "line.segments must be"),
            ({"mode": "refrigerated", "line": {"segments": [[10.0, 0.05]]}}, "line is only implemented"),
            ({"frequency": {"sheet": "none", "D_mm": 0}}, "frequency.D_mm and frequency.count must be positive"),
            ({"frequency": {"sheet": "none", "D_mm": 100, "period": "1900"}}, "frequency.period must be one of"),
            ({"fire": {"probit": "other"}}, "fire.probit must be"),
            ({"fire": {"release_angle_deg": 0}}, "only a vertical release"),
        ]
        for changes, message in cases:
            with self.subTest(message=message):
                self.assertIn(message, self._errors(**changes))
        data = _example()
        del data["P0_kPa"]
        self.assertIn("needs P0_kPa", "\n".join(lg_release.check(data)))

    def test_no_reach_when_the_flux_is_never_met(self):
        face = {"diameter_m": 3.0, "flame_height_m": 5.0, "sep_mudan_croce_kW_m2": 60.0, "tau": 1.0}
        self.assertEqual(lg_release._solid_flame_reach(face, 1e6), 0.0)
        near, far = lg_release._solid_flame_reach(face, 20.0), lg_release._solid_flame_reach(face, 5.0)
        self.assertTrue(math.isfinite(far) and far > near > 0)


if __name__ == "__main__":
    unittest.main()

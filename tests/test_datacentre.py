"""Tests for the data-centre helpers: energy balance, published-physics identities, availability monotonicity."""
import unittest

from process_safety import datacentre as dc, reliability


class DataCentre(unittest.TestCase):
    def test_pue(self):
        self.assertAlmostEqual(dc.pue(13000, 10000), 1.3)
        with self.assertRaises(ValueError):
            dc.pue(9000, 10000)

    def test_cooling_flow_energy_balance(self):
        q = dc.cooling_water_flow_m3_h(1000, 8)                      # 1 MW at dT 8 K
        kg_s = q * 1000 / 3600
        self.assertAlmostEqual(kg_s * 4.18 * 8, 1000, places=6)
        self.assertAlmostEqual(dc.cooling_water_flow_m3_h(2000, 8), 2 * q)
        self.assertAlmostEqual(dc.cooling_water_flow_m3_h(1000, 16), q / 2)

    def test_evaporative_water_matches_hand_calc(self):
        # 1.16 kWh heat per kWh IT, 85% evaporated, 2.43 MJ/kg: 1.46 L evaporated; 3 cycles -> 2.19 L; 6 cycles -> 1.75 L
        self.assertAlmostEqual(dc.evaporative_water_l_per_kwh_it(1.16, 3), 2.19, delta=0.01)
        self.assertAlmostEqual(dc.evaporative_water_l_per_kwh_it(1.16, 6), 1.75, delta=0.01)
        self.assertGreater(dc.evaporative_water_l_per_kwh_it(1.16, 2), dc.evaporative_water_l_per_kwh_it(1.16, 6))

    def test_battery_and_diesel(self):
        self.assertAlmostEqual(dc.battery_energy_kwh(1000, 15, 1.0, 1.0), 250.0)
        self.assertAlmostEqual(dc.battery_energy_kwh(1000, 15, 0.95, 0.8, 1.25), 250 / (0.95 * 0.8) * 1.25)
        # 1 MW for 12 h at 210 g/kWh = 2520 kg; at 840 kg/m3 = 3.0 m3
        self.assertAlmostEqual(dc.diesel_storage_m3(1000, 12, 210), 3.0)
        self.assertAlmostEqual(dc.diesel_storage_m3(1000, 12, 210, reserve_fraction=0.1), 3.3)
        with self.assertRaises(ValueError):
            dc.diesel_storage_m3(1000, 12, 0)
        with self.assertRaises(ValueError):
            dc.battery_energy_kwh(1000, 15, 1.2, 0.8)

    def test_availability_logic(self):
        a = 0.99
        self.assertAlmostEqual(dc.k_of_n_availability(3, 3, a), a ** 3)                      # N: all needed -> series
        self.assertGreater(dc.k_of_n_availability(3, 4, a), dc.k_of_n_availability(3, 3, a))  # N+1 beats N
        self.assertGreater(dc.k_of_n_availability(3, 5, a), dc.k_of_n_availability(3, 4, a))
        self.assertAlmostEqual(dc.k_of_n_availability(1, 2, a), 1 - (1 - a) ** 2)
        self.assertAlmostEqual(dc.k_of_n_availability(2, 3, a), 3 * a ** 2 * (1 - a) + a ** 3)
        one_path = [0.999, 0.99]
        self.assertAlmostEqual(dc.dual_path_availability([one_path, one_path]), 1 - (1 - 0.999 * 0.99) ** 2)
        self.assertGreater(dc.dual_path_availability([one_path, one_path]), dc.dual_path_availability([one_path]))
        self.assertAlmostEqual(dc.downtime_h_per_year(0.999), 8.76)

    def test_hazid_prompts_complete(self):
        for p in dc.HAZID_PROMPTS:
            self.assertEqual(set(p), {"area", "hazard", "toolkit", "note"})
            self.assertTrue(all(p.values()))
        self.assertGreaterEqual(len(dc.HAZID_PROMPTS), 8)

    def test_summary_uses_only_supplied_inputs(self):
        s = dc.summary(10000, facility_kw=13000, delta_t_k=8, autonomy_min=10, gen_hours=48, sfc_g_kwh=210)
        self.assertAlmostEqual(s["pue"], 1.3)
        self.assertAlmostEqual(s["diesel_m3"], 13000 * 48 * 210 / 1000 / 840)
        self.assertEqual(set(dc.summary(5000)), {"it_kw"})
        self.assertIs(dc.reliability, reliability)


if __name__ == "__main__":
    unittest.main()

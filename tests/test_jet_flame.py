import math
import unittest

from process_safety import jet_flame

G = 9.80665
BASE = dict(m_kg_s=2.0, rho_j_kg_m3=1.2, v_j_m_s=300.0, rho_amb_kg_m3=1.2, MW=44.1, Hc_J_kg=46.0e6,
            wind_m_s=0.0, release_angle_deg=90.0)


def flame(**kw):
    d = dict(BASE)
    d.update(kw)
    return jet_flame.chamberlain(**d)


class JetFlame(unittest.TestCase):
    def test_velocity_and_radius_are_consistent(self):
        f = flame()
        self.assertAlmostEqual(f["m_kg_s"], f["rho_j_kg_m3"] * math.pi * f["r_j_m"] ** 2 * f["v_j_m_s"], delta=1e-9)

    def test_radius_input_gives_same_flame_as_velocity_input(self):
        a = flame()
        b = jet_flame.chamberlain(m_kg_s=2.0, rho_j_kg_m3=1.2, r_j_m=a["r_j_m"], rho_amb_kg_m3=1.2, MW=44.1, Hc_J_kg=46.0e6,
                                  wind_m_s=0.0, release_angle_deg=90.0)
        self.assertAlmostEqual(a["L_B_m"], b["L_B_m"], delta=1e-9 * a["L_B_m"])

    def test_source_diameter_definition(self):
        f = flame(rho_j_kg_m3=0.6)
        self.assertAlmostEqual(f["Ds_m"], 2 * f["r_j_m"] * math.sqrt(0.6 / 1.2), delta=1e-12)

    def test_still_air_length_satisfies_kalghatgi_correlation(self):
        f = flame()
        n_ri = (G / (f["Ds_m"] ** 2 * f["v_j_m_s"] ** 2)) ** (1 / 3)
        lhs = (f["Ds_m"] * f["beta"] / (f["L_B0_m"] * f["W_st"])) ** (2 / 3)
        self.assertAlmostEqual(lhs, 0.2 + 0.024 * n_ri * f["L_B0_m"], places=9)

    def test_momentum_limit(self):
        # Richardson number -> 0 (very high velocity): L_B0 W_st / (beta Ds) -> 0.2**-1.5
        f = flame(v_j_m_s=1.0e10, rho_j_kg_m3=1.2, m_kg_s=1.2 * math.pi * 0.05 ** 2 * 1.0e10)
        ratio = f["L_B0_m"] * f["W_st"] / (f["beta"] * f["Ds_m"])
        self.assertAlmostEqual(ratio, 0.2 ** -1.5, delta=2e-3 * ratio)

    def test_length_grows_with_flow_at_fixed_velocity(self):
        lengths = [flame(m_kg_s=m)["L_B_m"] for m in (0.5, 1, 2, 5, 20)]
        self.assertEqual(lengths, sorted(lengths))

    def test_wind_shortens_flame(self):
        lengths = [flame(wind_m_s=u)["L_B_m"] for u in (0, 2, 5, 10)]
        self.assertEqual(lengths, sorted(lengths, reverse=True))

    def test_alpha_is_continuous_at_r_005(self):
        v = 100.0
        lo = flame(v_j_m_s=v, wind_m_s=0.05 * v - 1e-9, m_kg_s=1.2 * math.pi * 0.02 ** 2 * v)["alpha_deg"]
        hi = flame(v_j_m_s=v, wind_m_s=0.05 * v + 1e-9, m_kg_s=1.2 * math.pi * 0.02 ** 2 * v)["alpha_deg"]
        self.assertAlmostEqual(lo, hi, delta=0.02 * lo)

    def test_still_air_vertical_flame_is_straight(self):
        f = flame()
        self.assertAlmostEqual(f["alpha_deg"], 8000 * 0.0 / 1.0, places=9)

    def test_frustum_closes_the_triangle(self):
        for u in (0.0, 3.0, 12.0):
            for th in (90.0, 45.0, 0.0):
                f = flame(wind_m_s=u, release_angle_deg=th)
                a = math.radians(f["alpha_deg"])
                tip = (f["B_m"] + f["R_L_m"] * math.cos(a)) ** 2 + (f["R_L_m"] * math.sin(a)) ** 2
                self.assertAlmostEqual(tip, f["L_B_m"] ** 2, delta=1e-9 * f["L_B_m"] ** 2)

    def test_radiated_power_balance_when_not_capped(self):
        f = flame(sep_max_kW_m2=1e9)
        self.assertFalse(f["sep_capped"])
        self.assertAlmostEqual(f["SEP_kW_m2"] * f["area_m2"], f["radiated_power_kW"], delta=1e-9 * f["radiated_power_kW"])
        self.assertAlmostEqual(f["radiated_power_kW"], f["F_s"] * 2.0 * 46.0e6 / 1000, delta=1e-9 * f["radiated_power_kW"])

    def test_sep_cap_is_applied_and_flagged(self):
        f = flame(sep_max_kW_m2=1.0)
        self.assertTrue(f["sep_capped"])
        self.assertEqual(f["SEP_kW_m2"], 1.0)

    def test_frustum_area_matches_cylinder_limit(self):
        # W1 = W2 = w: area = 2 (pi/4 w^2) + pi w L  (cylinder with end discs)
        a = jet_flame.frustum_area_m2(2.0, 2.0, 10.0)
        self.assertAlmostEqual(a, 2 * math.pi / 4 * 4 + math.pi * 2.0 * 10.0, places=9)

    def test_cook_fs_scales_with_molecular_weight(self):
        # (33): unchanged below MW 21, sqrt(MW/21) from 21 to 60, 1.69 above 60
        ratio = lambda mw: flame(MW=mw, fs_model="cook")["F_s"] / flame(MW=mw)["F_s"]
        self.assertAlmostEqual(ratio(16.0), 1.0, places=12)
        self.assertAlmostEqual(ratio(44.1), math.sqrt(44.1 / 21.0), places=12)
        self.assertAlmostEqual(ratio(72.0), 1.69, places=12)

    def test_refusals(self):
        for bad in (dict(m_kg_s=0), dict(rho_j_kg_m3=-1), dict(wind_m_s=-1), dict(MW=0), dict(Hc_J_kg=0),
                    dict(release_angle_deg=120), dict(fs_model="x")):
            with self.assertRaises(ValueError, msg=str(bad)):
                flame(**bad)
        with self.assertRaises(ValueError):
            jet_flame.chamberlain(m_kg_s=1, rho_j_kg_m3=1, rho_amb_kg_m3=1.2, MW=16, Hc_J_kg=5e7, wind_m_s=0, release_angle_deg=90)
        with self.assertRaises(ValueError):
            flame(r_j_m=0.1)

    def test_notes_warn_for_near_horizontal_release(self):
        self.assertTrue(any("Johnson" in n for n in flame(release_angle_deg=0.0)["notes"]))
        self.assertFalse(any("Johnson" in n for n in flame(release_angle_deg=90.0)["notes"]))


if __name__ == "__main__":
    unittest.main()

import math
import unittest

from process_safety import expansion, jet_flame

R_KMOL = 8314.462618   # J/(kmol K)
GAS = dict(P_st_kPa=2000.0, T_st_K=300.0, Mw=16.0, gamma=1.3, area_m2=math.pi * 0.025 ** 2 / 4, Cd=0.85)
LIQ = dict(P0_kPa=900.0, T0_K=300.0, rho_L_kg_m3=500.0, cp_L_J_kgK=2500.0, Tb_K=231.0, h_fg_J_kg=426e3, Mw=44.1,
           area_m2=math.pi * 0.025 ** 2 / 4, Cd=0.62)


def cp_of(g):
    return g["gamma"] * (R_KMOL / g["Mw"]) / (g["gamma"] - 1.0)


class GasExpansion(unittest.TestCase):
    def test_vena_contracta_is_sonic(self):
        r = expansion.atex_gas(**GAS)
        self.assertAlmostEqual(r["u_vc_m_s"], math.sqrt(GAS["gamma"] * R_KMOL / GAS["Mw"] * r["T_vc_K"]), delta=1e-9 * r["u_vc_m_s"])

    def test_flow_matches_choked_orifice_formula(self):
        r = expansion.atex_gas(**GAS)
        g, mw = GAS["gamma"], GAS["Mw"]
        G = GAS["Cd"] * GAS["area_m2"] * GAS["P_st_kPa"] * 1000 * math.sqrt(g * mw / (R_KMOL * GAS["T_st_K"]) * (2 / (g + 1)) ** ((g + 1) / (g - 1)))
        self.assertAlmostEqual(r["G_kg_s"], G, delta=1e-9 * G)

    def test_conservation_of_mass_momentum_energy(self):
        r = expansion.atex_gas(**GAS)
        a_vc = GAS["Cd"] * GAS["area_m2"]
        self.assertAlmostEqual(r["rho_f_kg_m3"] * r["A_f_m2"] * r["u_f_m_s"], r["G_kg_s"], delta=1e-9 * r["G_kg_s"])
        lhs = r["rho_f_kg_m3"] * r["A_f_m2"] * r["u_f_m_s"] ** 2
        rhs = r["rho_vc_kg_m3"] * a_vc * r["u_vc_m_s"] ** 2 + (r["P_vc_kPa"] - 101.325) * 1000 * a_vc
        self.assertAlmostEqual(lhs, rhs, delta=1e-9 * rhs)
        cp = cp_of(GAS)
        self.assertAlmostEqual(cp * r["T_f_K"] + r["u_f_m_s"] ** 2 / 2, cp * r["T_vc_K"] + r["u_vc_m_s"] ** 2 / 2, delta=1e-6)

    def test_ideal_gas_density_at_final_state(self):
        r = expansion.atex_gas(**GAS)
        self.assertAlmostEqual(r["rho_f_kg_m3"], 101325.0 * GAS["Mw"] / (R_KMOL * r["T_f_K"]), delta=1e-6 * r["rho_f_kg_m3"])

    def test_no_expansion_when_vena_contracta_is_at_ambient(self):
        g = dict(GAS)
        crit = (2 / (g["gamma"] + 1)) ** (g["gamma"] / (g["gamma"] - 1))
        g["P_st_kPa"] = 101.325 / crit
        r = expansion.atex_gas(**g)
        self.assertAlmostEqual(r["u_f_m_s"], r["u_vc_m_s"], delta=1e-9 * r["u_vc_m_s"])
        self.assertAlmostEqual(r["T_f_K"], r["T_vc_K"], delta=1e-9)
        self.assertAlmostEqual(r["A_f_m2"], g["Cd"] * g["area_m2"], delta=1e-9 * g["area_m2"])

    def test_higher_pressure_gives_faster_and_colder_jet(self):
        out = [expansion.atex_gas(**{**GAS, "P_st_kPa": p}) for p in (300, 1000, 3000, 8000)]
        self.assertEqual([o["u_f_m_s"] for o in out], sorted(o["u_f_m_s"] for o in out))
        self.assertEqual([o["T_f_K"] for o in out], sorted((o["T_f_K"] for o in out), reverse=True))

    def test_velocity_cap_is_applied_through_the_energy_equation(self):
        r = expansion.atex_gas(**{**GAS, "P_st_kPa": 8000.0}, u_cap_m_s=500.0)
        self.assertEqual(r["u_f_m_s"], 500.0)
        self.assertTrue(r["capped"])
        cp = cp_of(GAS)
        self.assertAlmostEqual(cp * r["T_f_K"] + 500.0 ** 2 / 2, cp * r["T_vc_K"] + r["u_vc_m_s"] ** 2 / 2, delta=1e-6)
        self.assertAlmostEqual(r["rho_f_kg_m3"] * r["A_f_m2"] * 500.0, r["G_kg_s"], delta=1e-9 * r["G_kg_s"])

    def test_refusals(self):
        for bad in (dict(P_st_kPa=100.0), dict(T_st_K=0.0), dict(gamma=1.0), dict(Cd=1.5), dict(Mw=-1), dict(area_m2=0)):
            with self.assertRaises(ValueError, msg=str(bad)):
                expansion.atex_gas(**{**GAS, **bad})
        with self.assertRaises(ValueError):
            expansion.atex_gas(**GAS, u_cap_m_s=-5)

    def test_chain_into_jet_flame(self):
        lengths = []
        for p in (500.0, 2000.0, 8000.0):
            r = expansion.atex_gas(**{**GAS, "P_st_kPa": p})
            f = jet_flame.chamberlain(rho_amb_kg_m3=1.2, MW=GAS["Mw"], Hc_J_kg=50e6, wind_m_s=0.0, release_angle_deg=90.0,
                                      **expansion.jet_flame_inputs(r))
            lengths.append(f["L_B_m"])
        self.assertEqual(lengths, sorted(lengths))
        self.assertGreater(lengths[0], 0)


class FlashingLiquid(unittest.TestCase):
    def test_flash_fraction_energy_identity(self):
        x = expansion.adiabatic_flash_fraction(2500.0, 300.0, 231.0, 426e3)
        self.assertAlmostEqual(x * 426e3, 2500.0 * (300.0 - 231.0), delta=1e-9)

    def test_flash_fraction_limits_and_monotonic(self):
        self.assertEqual(expansion.adiabatic_flash_fraction(2500.0, 231.0, 231.0, 426e3), 0.0)
        self.assertEqual(expansion.adiabatic_flash_fraction(2500.0, 200.0, 231.0, 426e3), 0.0)
        xs = [expansion.adiabatic_flash_fraction(2500.0, t, 231.0, 426e3) for t in (240, 270, 300, 330)]
        self.assertEqual(xs, sorted(xs))
        with self.assertRaises(ValueError):
            expansion.adiabatic_flash_fraction(2500.0, 1000.0, 231.0, 426e3)

    def test_mixture_state_and_conservation(self):
        r = expansion.atex_flashing_liquid(**LIQ)
        rho_v = 101325.0 * LIQ["Mw"] / (R_KMOL * LIQ["Tb_K"])
        self.assertAlmostEqual(1 / r["rho_f_kg_m3"], r["x_vapour"] / rho_v + (1 - r["x_vapour"]) / LIQ["rho_L_kg_m3"], delta=1e-12)
        self.assertTrue(rho_v < r["rho_f_kg_m3"] < LIQ["rho_L_kg_m3"])
        self.assertAlmostEqual(r["rho_f_kg_m3"] * r["A_f_m2"] * r["u_f_m_s"], r["G_kg_s"], delta=1e-9 * r["G_kg_s"])

    def test_discharge_is_bernoulli_liquid_at_ambient_vena_contracta(self):
        r = expansion.atex_flashing_liquid(**LIQ)
        u = math.sqrt(2 * (LIQ["P0_kPa"] - 101.325) * 1000 / LIQ["rho_L_kg_m3"])
        self.assertAlmostEqual(r["u_vc_m_s"], u, delta=1e-9 * u)
        self.assertAlmostEqual(r["G_kg_s"], LIQ["Cd"] * LIQ["area_m2"] * LIQ["rho_L_kg_m3"] * u, delta=1e-9 * r["G_kg_s"])
        self.assertAlmostEqual(r["u_f_m_s"], r["u_vc_m_s"], delta=1e-12)     # no pressure thrust: vena contracta already at ambient

    def test_hotter_liquid_flashes_more_and_expands_more(self):
        a = expansion.atex_flashing_liquid(**{**LIQ, "T0_K": 280.0})
        b = expansion.atex_flashing_liquid(**{**LIQ, "T0_K": 320.0})
        self.assertGreater(b["x_vapour"], a["x_vapour"])
        self.assertGreater(b["A_f_m2"] / b["G_kg_s"] * b["u_f_m_s"], a["A_f_m2"] / a["G_kg_s"] * a["u_f_m_s"])

    def test_rainout_is_an_input_not_a_prediction(self):
        r = expansion.atex_flashing_liquid(**LIQ, rainout_fraction=0.25)
        self.assertAlmostEqual(r["airborne_kg_s"], 0.75 * r["G_kg_s"], delta=1e-12)
        self.assertEqual(expansion.atex_flashing_liquid(**LIQ)["airborne_kg_s"], expansion.atex_flashing_liquid(**LIQ)["G_kg_s"])
        with self.assertRaises(ValueError):
            expansion.atex_flashing_liquid(**LIQ, rainout_fraction=1.0)

    def test_refusals(self):
        for bad in (dict(P0_kPa=100.0), dict(T0_K=-1), dict(Tb_K=0), dict(rho_L_kg_m3=0), dict(Cd=0)):
            with self.assertRaises(ValueError, msg=str(bad)):
                expansion.atex_flashing_liquid(**{**LIQ, **bad})

    def test_notes_say_jet_flame_is_vapour_only(self):
        self.assertTrue(any("two-phase" in n.lower() for n in expansion.atex_flashing_liquid(**LIQ)["notes"]))


if __name__ == "__main__":
    unittest.main()

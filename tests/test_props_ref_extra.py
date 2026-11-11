"""Further fluids in props_ref (isobutane, propylene, ammonia, ethane): thermodynamic identities, not remembered values."""
import copy
import json
import os
import unittest

from process_safety import line_flow, lg_release, props_ref

FLUIDS = ("isobutane", "propylene", "ammonia", "ethane")
EXAMPLE = os.path.join(os.path.dirname(__file__), "..", "process_safety", "examples", "lgrelease.json")


class Tables(unittest.TestCase):
    def test_clausius_clapeyron_closes_within_3_percent(self):
        """h_fg = T (v_g - v_l) dP/dT must hold between tabulated rows (checks column order and units of every fluid)."""
        for fl in FLUIDS:
            rows = props_ref._TABLE[fl]
            mid = len(rows) // 2
            (T1, P1), (T2, P2) = rows[mid - 1][:2], rows[mid + 1][:2]
            T = rows[mid][0]
            dPdT = (P2 - P1) / (T2 - T1)
            vg, vl = 1.0 / props_ref.vapour_density_kg_m3(fl, T), 1.0 / props_ref.liquid_density_kg_m3(fl, T)
            rhs = T * (vg - vl) * dPdT
            self.assertLess(abs(rhs / props_ref.heat_of_vaporisation_J_kg(fl, T) - 1.0), 0.03, fl)

    def test_monotone_and_physical(self):
        for fl in FLUIDS:
            rows = props_ref._TABLE[fl]
            for a, b in zip(rows, rows[1:]):
                self.assertGreater(b[1], a[1])   # vapour pressure rises
                self.assertLess(b[2], a[2])      # liquid density falls
                self.assertGreater(b[3], a[3])   # vapour density rises
            Z = props_ref.compressibility_saturated_vapour(fl, rows[len(rows) // 2][0])
            self.assertTrue(0.4 < Z < 1.0, (fl, Z))

    def test_no_remembered_heat_of_combustion(self):
        for fl in FLUIDS:
            with self.assertRaises(ValueError):
                props_ref.net_heat_of_combustion_J_kg(fl)
        self.assertGreater(props_ref.net_heat_of_combustion_J_kg("propane"), 0)   # Annex value still served

    def test_existing_fluids_unchanged(self):
        self.assertAlmostEqual(props_ref.molar_mass_kg_mol("propane"), 0.044096, places=6)
        self.assertGreater(props_ref.vapour_viscosity_Pa_s("n-butane", 288.15), 0)


class Chain(unittest.TestCase):
    def test_line_flow_rises_with_pressure(self):
        seg = [(30.0, 0.1)]
        for fl, T in (("isobutane", 288.15), ("ammonia", 288.15), ("propylene", 288.15)):
            Pv = props_ref.vapour_pressure_Pa(fl, T)
            w1 = line_flow.line_discharge(fl, T, Pv * 1.2, 101325.0, seg)["W_kg_s"]
            w2 = line_flow.line_discharge(fl, T, Pv * 2.0, 101325.0, seg)["W_kg_s"]
            self.assertGreater(w2, w1, fl)

    def test_lg_release_needs_Hc_and_refuses_ammonia(self):
        base = json.load(open(EXAMPLE))
        d = copy.deepcopy(base)
        d["fluid"], d["P0_kPa"] = "isobutane", 600.0
        self.assertTrue(any("Hc_J_kg" in e for e in lg_release.check(d)))
        d["fire"]["Hc_J_kg"] = 4.0e7   # test input only, not a data value
        self.assertEqual(lg_release.check(d), [])
        d["fluid"] = "ammonia"
        self.assertTrue(any("ammonia" in e for e in lg_release.check(d)))

    def test_lg_release_runs_for_isobutane_with_explicit_gaps_reported(self):
        d = json.load(open(EXAMPLE))
        d["fluid"], d["P0_kPa"] = "isobutane", 600.0
        d["fire"]["Hc_J_kg"] = 4.0e7
        r = lg_release.run(d)
        self.assertGreater(r["release"]["W_kg_s"], 0)
        self.assertEqual(r["pool"], [])
        self.assertTrue(any("pool fire not computed" in w for w in r["warnings"]) or r["droplet"]["rainout_kg_s"] <= 1e-9)
        self.assertIsNone(r["ignition"]["purple_book_direct_ignition"])


if __name__ == "__main__":
    unittest.main()

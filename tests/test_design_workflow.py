import copy
import json
import os
import subprocess
import sys
import tempfile
import unittest

from process_safety import design_workflow as dw
from process_safety import relief, sil
from process_safety.qra import alarp

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(ROOT, "process_safety", "examples", "workflow.json"), encoding="utf-8") as fh:
    EX = json.load(fh)


def ex():
    d = copy.deepcopy(EX)
    d.pop("shutdown_model", None)
    return d


class Screening(unittest.TestCase):
    def test_liquid_wetted_matches_the_relief_modules(self):
        d = ex()
        u = d["units"][0]
        v, f = u["vessel"], u["fluid"]
        A = relief.wetted_area_cylinder(v["D_m"], v["L_m"], v["level_m"], v["orientation"], v["elevation_m"])
        W = relief.fire_relief_rate_kg_h(A, v["latent_heat_kJ_kg"], v["F"], True)
        r = relief.gas_area(W, f["relieving_T_K"], relief.relieving_pressure_kpa(u["set_kpag"], "fire"), u["back_pressure_kpag"] + relief.ATM, f["M"], f["k"], f["Z"], set_g_kpa=u["set_kpag"])
        s = dw.screen_unit(u)
        self.assertAlmostEqual(s["simulate"]["required_area_mm2"], r.required_area_mm2)
        self.assertEqual(s["simulate"]["required_orifice"], r.orifice)
        self.assertFalse(s["resize"]["psv_ok"])                       # installed 506 mm2 < required
        self.assertEqual(s["resize"]["psv_new"]["orifice"], r.orifice)

    def test_adequate_psv_is_left_alone(self):
        u = copy.deepcopy(ex()["units"][0])
        u["existing"]["psv_area_mm2"] = 5000.0
        s = dw.screen_unit(u)
        self.assertTrue(s["resize"]["psv_ok"])
        self.assertNotIn("psv_new", s["resize"])

    def test_inlet_line_is_upsized_when_the_3_percent_rule_fails(self):
        u = copy.deepcopy(ex()["units"][0])
        u["existing"].update(inlet_id_m=0.03, inlet_length_m=15.0)
        s = dw.screen_unit(u)
        self.assertFalse(s["resize"]["inlet_existing"]["ok"])
        new = s["resize"]["inlet_new"]
        self.assertTrue(new["check"]["ok"])
        self.assertGreater(new["id_m"], 0.03)

    def test_rerouting_lengthens_the_inlet_and_increases_the_loss(self):
        s = dw.screen_unit(ex()["units"][0])
        self.assertGreater(s["resize"]["inlet_after_reroute"]["existing_size"]["inlet_loss_fraction"], s["resize"]["inlet_existing"]["inlet_loss_fraction"])

    def test_vapour_filled_gets_a_blowdown_valve_and_is_protected(self):
        s = dw.screen_unit(ex()["units"][1])
        self.assertFalse(s["simulate"]["protected_as_installed"])
        bd = s["resize"]["bdv_new"]
        self.assertTrue(bd["protected_after"])
        self.assertTrue(bd["governed_by_minimum_practical_size"])
        self.assertAlmostEqual(bd["equivalent_diameter_mm"], 50.0)

    def test_sif_benefit_matches_sil_module(self):
        sf = ex()["units"][1]["sif"]
        b = dw.sif_benefit(sf)
        self.assertAlmostEqual(b["pfd_before"], sil.pfd_avg("1oo1", 2e-6, 8760.0, 0.05))
        self.assertAlmostEqual(b["pfd_after"], sil.pfd_avg("2oo3", 2e-6, 8760.0, 0.05))
        self.assertAlmostEqual(b["pll_before"], 0.1 * b["pfd_before"] * 2)
        self.assertGreater(b["rrf_gain"], 1.0)


class Chain(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = ex()
        cls.r = dw.run(cls.d, 1500)

    def test_check_reports_problems(self):
        bad = copy.deepcopy(self.d)
        bad["units"][0]["install"]["reroute"]["new_rate_key"] = "nope"
        del bad["opex_book"]
        e = dw.check(bad)
        self.assertTrue(any("nope" in x for x in e))
        self.assertTrue(any("opex_book" in x for x in e))
        bad2 = copy.deepcopy(self.d)
        bad2["units"][0]["mode"] = "gas"
        self.assertTrue(dw.check(bad2))
        with self.assertRaises(ValueError):
            dw.run(bad)

    def test_bill_of_quantities_has_every_scope(self):
        boq = {b["id"]: b["lines"] for b in self.r["stage3_bill_of_quantities"]}
        self.assertEqual(set(boq), {"V-101:device", "V-101:reroute", "V-201:device", "V-201:sensors", "V-201:pcn"})
        rr = {ln["description"]: ln for ln in boq["V-101:reroute"]}
        self.assertEqual(rr["new routed line"]["qty"]["mode"], 55)
        self.assertEqual(rr["demolish and remove old line"]["qty"]["mode"], 40)
        self.assertEqual(rr["90 degree elbows"]["qty"]["mode"], 6)
        sn = {ln["description"]: ln for ln in boq["V-201:sensors"]}
        self.assertEqual(sn["cable for pressure transmitter"]["qty"]["mode"], 440)     # 2 sensors x 220 m
        self.assertEqual(sn["cable for flammable gas detector"]["qty"]["mode"], 450)   # 3 x 150 m

    def test_capex_arithmetic(self):
        est = self.r["stage4_capex"]
        self.assertAlmostEqual(est["portfolio"]["total_mode"], sum(x["total_mode"] for x in est["recommendations"]))
        by = {x["id"]: x for x in est["recommendations"]}
        rr = by["V-101:reroute"]
        book = self.d["rate_book"]
        direct = 40 * book["demo_pipe"]["rate"]["mode"] + 55 * book["pipe_6in"]["rate"]["mode"] + 6 * book["elbow"]["rate"]["mode"] + 8 * book["pipe_support"]["rate"]["mode"] \
            + 3 * book["tie_in"]["rate"]["mode"] + 6 * book["concrete"]["rate"]["mode"]
        self.assertAlmostEqual(rr["direct_mode"], direct)
        self.assertAlmostEqual(rr["total_mode"], direct * est["indirect_factor"])
        self.assertTrue(by["V-201:sensors"]["requires_shutdown"] is False)
        self.assertTrue(by["V-201:pcn"]["requires_shutdown"])

    def test_opex_parts_by_hand(self):
        o = {u["tag"]: u for u in self.r["stage5_opex"]["units"]}["V-201"]
        ob = self.d["opex_book"]
        cap = {x["id"]: x["capex"]["P50"] for x in self.r["stage4_capex"]["recommendations"]}
        self.assertAlmostEqual(o["parts"]["bdv_proof_test"], ob["bdv_test_cost"] / ob["bdv_test_interval_years"])
        self.assertAlmostEqual(o["parts"]["sensor_calibration_and_proof_test"], 5 * ob["sensor_test_cost"] / ob["sensor_test_interval_years"])
        self.assertAlmostEqual(o["parts"]["pcn_support_and_licences"], ob["pcn_support_pct_of_pcn_capex"] / 100 * cap["V-201:pcn"])
        self.assertAlmostEqual(o["parts"]["maintenance_of_new_equipment"], ob["maintenance_pct_of_capex"] / 100 * (cap["V-201:device"] + cap["V-201:sensors"] + cap["V-201:pcn"]))
        pv = alarp.present_value_factor(25, 0.035)
        self.assertAlmostEqual(o["lifecycle_opex_pv"], o["annual_opex"] * pv)

    def test_lifecycle_and_alarp_package(self):
        lc = self.r["lifecycle"]
        self.assertGreater(lc["lifecycle_cost_P50_pv"], lc["capex_P50"])
        a = {x["tag"]: x for x in self.r["stage6_alarp_per_unit_package"]}
        v2 = a["V-201"]
        ref = alarp.cost_benefit(v2["pll_before"] - v2["pll_after"], v2["package_capex_P50"], v2["annual_opex"], 9000, 25, 3, 0.035)
        self.assertAlmostEqual(v2["cost_benefit_ratio"], ref["cost_benefit_ratio"])
        self.assertIsNotNone(v2["sif"])           # benefit was derived from the voting change
        self.assertIsNone(a["V-101"]["sif"])      # benefit was the supplied risk reduction

    def test_nothing_to_change(self):
        d = ex()
        d["units"] = [copy.deepcopy(d["units"][0])]
        d["units"][0]["existing"]["psv_area_mm2"] = 830.0      # J orifice, enough for the fire case, inlet line still passes the 3% rule
        d["units"][0]["install"] = {}
        r = dw.run(d, 200)
        self.assertIn("no design changes", r["note"])


class Tool(unittest.TestCase):
    def test_tool_end_to_end(self):
        with tempfile.TemporaryDirectory() as out:
            r = subprocess.run([sys.executable, "-m", "process_safety", "tool", "workflow", "--out", out, "--quiet"], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)
            s = json.loads(r.stdout)
            self.assertIn("shutdown_effect", s)
            self.assertGreater(s["shutdown_effect"]["delta_direct_cost"]["P50"], 0)
            self.assertEqual(len(s["files"]), 3)
            for f in s["files"]:
                self.assertTrue(os.path.getsize(f) > 0, f)
            self.assertGreater(s["lifecycle"]["lifecycle_cost_P50_pv"], s["lifecycle"]["capex_P50"])


if __name__ == "__main__":
    unittest.main()

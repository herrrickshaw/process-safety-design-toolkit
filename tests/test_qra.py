"""QRA workflow tests: identities and conservation laws, not remembered example numbers."""
import copy
import io
import json
import math
import os
import tempfile
import unittest

from process_safety.qra import alarp, effects, eta, frequency, hazid, mitigation, progress, report, risk, study, validate

EX = os.path.join(os.path.dirname(__file__), "..", "process_safety", "qra", "examples", "lpg_terminal.json")


def small_study():
    s = study.load(EX)
    s["grid"] = {"x_min": -400, "x_max": 400, "y_min": -400, "y_max": 400, "step": 25}
    s["conventions"]["sector_subdivisions"] = 4
    return s


class Disc(effects.Effect):
    """p = 1 inside radius R centred xc downwind (directional if xc != 0)."""

    def __init__(self, R, xc=0.0):
        self.R, self.xc, self.kind = R, xc, "test"
        self.directional = xc != 0
        self.reach = xc + R
        self.half_width = R
        self.x_back = max(0.0, R - xc)

    def p(self, dx, dy):
        return 1.0 if math.hypot(dx - self.xc, dy) <= self.R else 0.0


def run_one(effect, f=1e-3, rose=None, weather_dep=False, step=2.0, ext=200):
    sc = [{"id": "A", "x": 0.0, "y": 0.0, "frequency_per_yr": f,
           "branches": [{"outcome": "test", "prob": 1.0, "build": lambda w: effect, "weather_dependent": weather_dep}]}]
    g = risk.Grid(-ext, ext, -ext, ext, step)
    wx = [{"name": "D5", "stability": "D", "u": 5, "p": 1.0}]
    rec = [{"name": "down", "x": 0.0, "y": 60.0}, {"name": "up", "x": 0.0, "y": -60.0}]
    pop = [{"name": "P1", "x": 30.0, "y": 0.0, "people": 10, "indoor_fraction": 0.5}, {"name": "P2", "x": 0.0, "y": 60.0, "people": 4}]
    return risk.integrate(sc, wx, rose or [1 / 8] * 8, g, rec, pop, {"test": 0.2}, lambda s, o, w: o["build"](w), progress=False, sub=6)


class Frequency(unittest.TestCase):
    def test_cox_bands_match_rapidn_table(self):
        self.assertEqual([frequency.cox_ignition(r, "gas") for r in (0.5, 10, 80)], [0.01, 0.07, 0.30])
        self.assertEqual([frequency.cox_ignition(r, "liquid") for r in (0.5, 10, 80)], [0.01, 0.03, 0.08])
        self.assertEqual([frequency.cox_explosion_given_ignition(r) for r in (0.5, 10, 80)], [0.04, 0.12, 0.30])

    def test_parts_count_per_metre_and_per_item(self):
        ds = frequency.load_dataset()
        sec = {"id": "X", "equipment": [{"type": "piping_300_499mm", "length_m": 100, "diameter_mm": 300}, {"type": "pressure_vessel", "count": 3}]}
        loc = {x["id"]: x for x in frequency.loc_scenarios(sec, ds)}
        self.assertAlmostEqual(loc["X-piping_300_499mm-rupture"]["frequency_per_yr"], 7e-8 * 100)
        self.assertAlmostEqual(loc["X-piping_300_499mm-D/3"]["hole_mm"], 100)
        self.assertAlmostEqual(loc["X-piping_300_499mm-0.1D_max50"]["hole_mm"], 30)
        self.assertAlmostEqual(loc["X-pressure_vessel-10mm"]["frequency_per_yr"], 3e-4)
        self.assertTrue(loc["X-pressure_vessel-rupture"]["instantaneous"])

    def test_every_dataset_row_has_a_known_source(self):
        ds = frequency.load_dataset()
        for name, eq in ds["equipment"].items():
            for r in eq["rows"]:
                self.assertIn(r["source"], ds["sources"], name)

    def test_fault_tree_frequency(self):
        spec = {"initiator_per_yr": 0.1, "basic": {"a": 0.1, "b": 0.01, "c": 0.001},
                "gates": {"g": ["OR", ["b", "c"]], "top": ["AND", ["a", "g"]]}, "top": "top"}
        f, d = frequency.fault_tree_frequency(spec)
        self.assertAlmostEqual(f, 0.1 * 0.1 * (1 - 0.99 * 0.999), places=15)
        self.assertEqual(d["cut_sets"], [["a", "b"], ["a", "c"]])
        x = frequency.extra_scenario({"id": "e", "section": "S", "hole_mm": 10, "fault_tree": spec, "ipl_pfds": [0.01, 0.1]})
        self.assertAlmostEqual(x["frequency_per_yr"], f * 1e-3)


class EventTree(unittest.TestCase):
    def test_branches_sum_to_one_for_every_example_loc(self):
        s = small_study()
        for sc in study.build_scenarios(s, frequency.load_dataset()):
            self.assertAlmostEqual(sum(b["prob"] for b in sc["branches"]), 1.0, places=12, msg=sc["id"])
            self.assertTrue(all(0 <= b["prob"] <= 1 for b in sc["branches"]))

    def test_vce_capped_by_delayed_ignition(self):
        st = {"airborne_fraction": 1.0, "phase": "gas", "instantaneous": False, "rate_for_ignition_kg_s": 100}
        m = {"LFL_vol": 0.05, "Hc_MJ_kg": 50}
        br = {b["outcome"]: b["prob"] for b in eta.branches(st, {}, m, study.DEFAULT_CONVENTIONS, {"immediate_fraction": 0.9})}
        self.assertAlmostEqual(br["vce"], 0.3 * 0.1)          # capped at P(delayed) = 0.3 x 0.1
        self.assertNotIn("flash_fire", br)                     # zero-probability branch dropped
        self.assertAlmostEqual(sum(br.values()), 1.0)


class SourceAndEffects(unittest.TestCase):
    def test_flash_fraction_is_cp_dT_over_hv(self):
        m = study.load(EX)["materials"]["propane"]
        st = effects.source_term({"P_kpag": 750, "T_K": 303, "inventory_kg": 1e4}, m, 25, False, study.DEFAULT_CONVENTIONS)
        self.assertAlmostEqual(st["flash_fraction"], 2.52 * (303 - 231.1) / 426)
        self.assertAlmostEqual(st["airborne_fraction"], min(1, 2 * st["flash_fraction"]))
        self.assertAlmostEqual(st["airborne_rate_kg_s"] + st["rainout_rate_kg_s"], st["rate_kg_s"])

    def test_jet_flame_length_equals_tceq_api_form(self):
        # TCEQ: flame height above tip 4.56e-3 q^0.478 (q cal/s) for a 45 deg flame -> length = height / sin 45
        Q = 5e8
        tceq_len = 4.56e-3 * (Q / 4.1868) ** 0.478 / math.sin(math.pi / 4)
        self.assertAlmostEqual(0.00326 * Q ** 0.478 / tceq_len, 1, delta=0.005)

    def test_lung_probit_threshold(self):
        # 1 % lethality where -77.1 + 6.91 ln P = 2.674 -> P ~ 101.8 kPa
        self.assertAlmostEqual(effects.lung_p(math.exp((2.6737 + 77.1) / 6.91) / 1e3), 0.01, delta=1e-3)

    def test_radial_effect_monotone(self):
        e = effects.Radial(lambda r: 1 / (1 + (r / 50) ** 4), "x")
        vals = [e.p(r, 0) for r in range(0, int(e.reach) + 20, 5)]
        self.assertTrue(all(a >= b for a, b in zip(vals, vals[1:])))
        self.assertEqual(e.p(e.reach + 1, 0), 0.0)

    def test_small_leak_in_bund_makes_small_pool(self):
        m = study.load(EX)["materials"]["diesel"]
        st = effects.source_term({"P_kpag": 0, "T_K": 303, "inventory_kg": 1e6, "liquid_head_m": 8}, m, 10, False, study.DEFAULT_CONVENTIONS)
        self.assertLess(effects.pool_area(st, {"bund_area_m2": 2500}, m), 50)


class Integration(unittest.TestCase):
    def test_radial_area_identity_and_centre_value(self):
        f, R = 1e-3, 50.0
        res = run_one(Disc(R), f=f)
        g = res["grid"]
        area_sum = sum(v for row in g.ir for v in row) * g.step ** 2
        self.assertAlmostEqual(area_sum / (f * math.pi * R * R), 1, delta=0.02)
        self.assertAlmostEqual(risk.max_ir(g)[0], f)

    def test_directional_area_identity(self):
        f, R, xc = 1e-3, 30.0, 80.0
        res = run_one(Disc(R, xc), f=f, weather_dep=True)
        g = res["grid"]
        area_sum = sum(v for row in g.ir for v in row) * g.step ** 2
        self.assertAlmostEqual(area_sum / (f * math.pi * R * R), 1, delta=0.03)

    def test_wind_from_south_hits_north_only(self):
        rose = [0.0] * 8
        rose[4] = 1.0  # wind FROM the south -> blows north
        res = run_one(Disc(30.0, 60.0), rose=rose, weather_dep=True)
        self.assertGreater(res["receptor_lsir"]["down"], 0)
        self.assertEqual(res["receptor_lsir"]["up"], 0)

    def test_pll_identity_and_vulnerability(self):
        res = run_one(Disc(50.0), f=1e-3)
        # P1 at 30 m: 10 people x (0.5 outdoor + 0.5 x 0.2 indoor) = 6 fatalities; P2 at 60 m outside the disc
        self.assertAlmostEqual(res["pll"], 1e-3 * 6)
        self.assertAlmostEqual(res["pll"], res["pll_check"])
        self.assertEqual(risk.fn_curve(res["fn_events"])[0], (1.0, 1e-3))

    def test_adaptive_subdivisions(self):
        thin = effects.Footprint(750, 25, 1.0, "flash_fire")
        self.assertGreaterEqual(risk.subdivisions(thin, 45, 12), 30)
        self.assertEqual(risk.subdivisions(Disc(50), 45, 12), 12)


class Criteria(unittest.TestCase):
    def test_r2p2_bands(self):
        c = alarp.get_criteria("uk_hse_r2p2")
        self.assertEqual(alarp.classify_ir(2e-3, "worker", c), "INTOLERABLE")
        self.assertEqual(alarp.classify_ir(2e-4, "worker", c), "TOLERABLE IF ALARP")
        self.assertEqual(alarp.classify_ir(2e-4, "public", c), "INTOLERABLE")
        self.assertEqual(alarp.classify_ir(5e-7, "public", c), "BROADLY ACCEPTABLE")
        self.assertAlmostEqual(alarp.fn_line(50, c["fn"]["intolerable"]), 2e-4)  # passes through the R2P2 anchor

    def test_fn_regions(self):
        c = alarp.get_criteria("uk_hse_r2p2")
        self.assertEqual(alarp.classify_fn([(1, 1e-3), (10, 1e-5)], c)["region"], "TOLERABLE IF ALARP")
        self.assertEqual(alarp.classify_fn([(1, 1e-7)], c)["region"], "BROADLY ACCEPTABLE")
        self.assertEqual(alarp.classify_fn([(100, 1e-3)], c)["region"], "INTOLERABLE")
        nl = alarp.get_criteria("nl_bevi")
        self.assertAlmostEqual(alarp.fn_line(10, nl["fn"]["intolerable"]), 1e-5)

    def test_cost_benefit(self):
        r = alarp.cost_benefit(1e-3, 1e6, 1e4, 1e8, 25, 3)
        self.assertAlmostEqual(r["benefit"], 1e-3 * 1e8 * 25)
        self.assertAlmostEqual(r["cost_benefit_ratio"], (1e6 + 25e4) / 2.5e6)
        self.assertTrue(r["decision"].startswith("IMPLEMENT"))
        self.assertAlmostEqual(alarp.present_value_factor(10, 0.1), (1 - 1.1 ** -10) / 0.1)


class Validation(unittest.TestCase):
    def test_example_is_clean(self):
        self.assertFalse(validate.inputs(study.load(EX), frequency.load_dataset()).errors)

    def test_catches_bad_inputs(self):
        s = study.load(EX)
        s["weather"][0]["p"] = 0.5
        s["materials"]["propane"]["LFL_vol"] = 2.1
        s["sections"][0]["T_K"] = 30
        s["wind_rose"] = s["wind_rose"][:7]
        del s["ignition"]["immediate_fraction"]
        errs = " | ".join(validate.inputs(s, frequency.load_dataset()).errors)
        for frag in ("weather probabilities", "LFL_vol", "T_K", "wind rose", "immediate_fraction"):
            self.assertIn(frag, errs)
        with self.assertRaises(ValueError):
            study.run(s, progress=False)

    def test_piping_band_check(self):
        s = study.load(EX)
        s["sections"][2]["equipment"][0]["diameter_mm"] = 600
        self.assertTrue(any("outside piping_300_499mm" in e for e in validate.inputs(s, frequency.load_dataset()).errors))


class EndToEnd(unittest.TestCase):
    def test_sample_then_full_and_outputs(self):
        s = small_study()
        smp = study.run(s, sample=3, progress=False, mitigate=False)
        self.assertEqual(len(smp["scenarios"]), 3)
        self.assertIn("projected_full_base_s", smp["projection"])
        self.assertIn("angular_convergence_max_change", smp["projection"])
        full = study.run(s, progress=False)
        self.assertFalse(full["validation_results"]["errors"])
        self.assertAlmostEqual(full["results"]["pll"], full["results"]["pll_check"], delta=1e-9 * full["results"]["pll"])
        with tempfile.TemporaryDirectory() as d:
            files = report.write_all(full, s, d, xlsx=False)
            self.assertTrue(os.path.getsize(files["report"]) > 10_000)
            with open(files["summary"]) as fh:
                self.assertEqual(json.load(fh)["scenarios_run"], 18)

    def test_mitigation_frequency_factor_scales_pll_exactly(self):
        s = small_study()
        s["mitigation"] = [{"name": "all x0.1", "changes": [{"target": "frequency", "section": "*", "hole": "*", "factor": 0.1}]}]
        out = study.run(s, progress=False)
        m = out["mitigation"][0]
        self.assertAlmostEqual(m["pll_after"] / m["pll_before"], 0.1, places=9)

    def test_mitigation_does_not_mutate_study(self):
        s = small_study()
        before = json.dumps(s, sort_keys=True)
        mitigation.apply(s, s["mitigation"][1])
        self.assertEqual(before, json.dumps(s, sort_keys=True))

    def test_hazid_and_hazop_rows(self):
        s = study.load(EX)
        self.assertEqual(len(hazid.hazid_register(s["sections"])), 4 * sum(len(v) for v in hazid.HAZID_CHECKLIST.values()))
        rows = hazid.hazop_rows(s["sections"])
        self.assertTrue(any("loss of containment" in r["Consequences"] for r in rows))

    def test_override_replaces_model(self):
        s = small_study()
        s["overrides"] = {"S2-Loading hose-rupture": {"jet_fire+pool_fire": {"type": "radial", "table": [[0, 1.0], [40, 1.0], [41, 0.0]]}}}
        out = study.run(s, progress=False, mitigate=False)
        e = out["results"]["effects"][("S2-Loading hose-rupture", "jet_fire+pool_fire", None)]
        self.assertEqual(e.p(30, 0), 1.0)
        self.assertEqual(e.p(45, 0), 0.0)


class ProgressBar(unittest.TestCase):
    def test_eta_and_lines(self):
        buf = io.StringIO()
        p = progress.Progress(100, "x", stream=buf)
        for _ in range(100):
            p.update()
        p.done()
        lines = buf.getvalue().strip().splitlines()
        self.assertTrue(lines[-1].endswith("done"))
        self.assertIn("ETA", lines[0])
        self.assertLessEqual(len(lines), 13)


if __name__ == "__main__":
    unittest.main()

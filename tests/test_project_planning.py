"""Identity tests for wbs, schedule, tender_register and portfolio (docs/PROJECT_PIPELINE.md). No remembered example numbers."""
import datetime as dt
import json
import os
import unittest

from process_safety import pha, portfolio, schedule, shutdown_risk, tender_register as tr, wbs

D = dt.date
HERE = os.path.dirname(os.path.abspath(__file__))
EX = os.path.join(os.path.dirname(HERE), "process_safety", "examples")


def load(name):
    with open(os.path.join(EX, name + ".json"), encoding="utf-8") as fh:
        return json.load(fh)


def net(calendar=None, start="2026-01-05", **kw):
    d = {"start": start, "activities": [
        {"id": "A", "duration_days": 3},
        {"id": "B", "duration_days": 4, "predecessors": ["A"]},
        {"id": "C", "duration_days": 2, "predecessors": ["A"]},
        {"id": "D", "duration_days": 1, "predecessors": ["B", "C"]}]}
    if calendar:
        d["calendar"] = calendar
    d.update(kw)
    return d


class Schedule(unittest.TestCase):
    def test_seven_day_calendar_matches_shutdown_base_case(self):
        sd = load("shutdown")
        for a in sd["activities"]:
            a["duration_days"] = {"min": a["duration_days"]["mode"], "mode": a["duration_days"]["mode"], "max": a["duration_days"]["mode"]}
        want = shutdown_risk.base_case(sd)
        p = schedule.plan(schedule.from_shutdown(sd, "2026-03-02"))
        self.assertAlmostEqual(p["duration_days"], want["duration_days"], places=9)
        self.assertEqual(p["critical_path"], want["critical_path"])

    def test_critical_path_sums_to_duration_and_float_nonnegative(self):
        p = schedule.plan(net())
        dur = {r["id"]: r["duration_days"] for r in p["activities"]}
        self.assertAlmostEqual(sum(dur[i] for i in p["critical_path"]), p["duration_days"], places=9)
        self.assertEqual(p["critical_path"], ["A", "B", "D"])
        self.assertTrue(all(r["total_float_days"] >= -1e-9 for r in p["activities"]))
        self.assertAlmostEqual(next(r for r in p["activities"] if r["id"] == "C")["total_float_days"], 2.0)

    def test_dates_skip_weekends(self):
        p = schedule.plan(net())          # starts Monday 2026-01-05, 3 + 4 + 1 working days
        rows = {r["id"]: r for r in p["activities"]}
        self.assertEqual(rows["A"]["start"], "2026-01-05")
        self.assertEqual(rows["A"]["finish"], "2026-01-07")
        self.assertEqual(rows["B"]["start"], "2026-01-08")
        self.assertEqual(rows["B"]["finish"], "2026-01-13")   # Thu, Fri, then Mon, Tue
        self.assertEqual(p["finish"], "2026-01-14")

    def test_holiday_never_brings_finish_earlier(self):
        base = schedule.plan(net())
        held = schedule.plan(net(calendar={"workdays": [0, 1, 2, 3, 4], "holidays": ["2026-01-08"]}))
        self.assertGreaterEqual(held["finish"], base["finish"])
        self.assertGreater(held["finish"], base["finish"])

    def test_lag_monotone(self):
        a = schedule.plan(net())["duration_days"]
        d = net()
        d["activities"][1]["predecessors"] = [{"id": "A", "type": "FS", "lag": 2}]
        self.assertGreaterEqual(schedule.plan(d)["duration_days"], a)
        self.assertAlmostEqual(schedule.plan(d)["duration_days"], a + 2)

    def test_lag_on_a_noncritical_link_uses_up_float_exactly(self):
        d = net()
        free = next(r for r in schedule.plan(d)["activities"] if r["id"] == "C")["total_float_days"]
        d["activities"][3]["predecessors"] = ["B", {"id": "C", "type": "FS", "lag": 1}]
        p = schedule.plan(d)
        c = next(r for r in p["activities"] if r["id"] == "C")
        self.assertAlmostEqual(c["total_float_days"], free - 1)
        self.assertAlmostEqual(p["duration_days"], 8.0)          # the lagged path is still shorter than A-B-D

    def test_start_shift_by_whole_weeks_shifts_all_dates(self):
        p0, p1 = schedule.plan(net()), schedule.plan(net(start="2026-01-19"))
        for r0, r1 in zip(p0["activities"], p1["activities"]):
            self.assertEqual(D.fromisoformat(r1["start"]) - D.fromisoformat(r0["start"]), dt.timedelta(days=14))
            self.assertEqual(D.fromisoformat(r1["finish"]) - D.fromisoformat(r0["finish"]), dt.timedelta(days=14))

    def test_ss_and_ff_links(self):
        d = {"start": "2026-01-05", "calendar": {"workdays": [0, 1, 2, 3, 4, 5, 6]}, "activities": [
            {"id": "A", "duration_days": 10},
            {"id": "B", "duration_days": 4, "predecessors": [{"id": "A", "type": "SS", "lag": 3}]},
            {"id": "C", "duration_days": 4, "predecessors": [{"id": "A", "type": "FF", "lag": 2}]}]}
        rows = {r["id"]: r for r in schedule.plan(d)["activities"]}
        self.assertAlmostEqual(rows["B"]["es"], 3.0)
        self.assertAlmostEqual(rows["C"]["ef"], 12.0)       # EF_C >= EF_A + 2
        self.assertAlmostEqual(rows["C"]["es"], 8.0)

    def test_deadline_gives_negative_slack_and_flags(self):
        p = schedule.plan(net(finish_by="2026-01-09"))
        self.assertLess(p["deadline"]["slack_working_days"], 0)
        self.assertTrue(p["deadline"]["late"])
        q = schedule.plan(net(finish_by="2026-03-02"))
        self.assertGreater(q["deadline"]["slack_working_days"], 0)
        self.assertFalse(q["deadline"]["late"])

    def test_start_no_earlier(self):
        d = net()
        d["activities"][0]["start_no_earlier"] = "2026-01-12"
        self.assertEqual(schedule.plan(d)["activities"][0]["start"], "2026-01-12")

    def test_weekly_load_conserves_effort_and_flags_overload(self):
        d = net(capacity_days_per_week={"ann": 2.0})
        for a in d["activities"]:
            a["owner"] = "ann"
            a["effort_days"] = a["duration_days"] * 1.0
        p = schedule.plan(d)
        self.assertAlmostEqual(sum(r["demand_days"] for r in p["load"] if r["owner"] == "ann"), 10.0, places=9)
        self.assertTrue(p["overloads"])
        d["capacity_days_per_week"] = {"ann": 50.0}
        self.assertFalse(schedule.plan(d)["overloads"])

    def test_checks_refuse_bad_input(self):
        bad = net()
        bad["activities"][0]["predecessors"] = ["D"]
        self.assertTrue(any("cycle" in e for e in schedule.check(bad)))
        bad = net()
        bad["activities"][1]["predecessors"] = ["ZZ"]
        self.assertTrue(any("unknown predecessor" in e for e in schedule.check(bad)))
        bad = net()
        bad["activities"].append({"id": "A", "duration_days": 1})
        self.assertTrue(any("duplicate" in e for e in schedule.check(bad)))
        bad = net()
        bad["activities"][0]["duration_days"] = -1
        self.assertTrue(schedule.check(bad))
        bad = net(calendar={"workdays": []})
        self.assertTrue(schedule.check(bad))
        bad = net()
        bad["activities"][1]["predecessors"] = [{"id": "A", "type": "XX"}]
        self.assertTrue(schedule.check(bad))
        bad = net(start="05/01/2026")
        self.assertTrue(schedule.check(bad))

    def test_progress_planned_percent(self):
        d = net(status_date="2026-01-07")
        d["activities"][0]["percent_complete"] = 100
        p = schedule.plan(d)
        a = next(r for r in p["activities"] if r["id"] == "A")
        self.assertAlmostEqual(a["planned_percent"], 100.0)
        b = next(r for r in p["activities"] if r["id"] == "B")
        self.assertAlmostEqual(b["planned_percent"], 0.0)

    def test_gantt_svg(self):
        import tempfile
        p = schedule.plan(net())
        with tempfile.TemporaryDirectory() as t:
            path = os.path.join(t, "g.svg")
            schedule.gantt_svg(p, path)
            with open(path, encoding="utf-8") as fh:
                self.assertIn("<svg", fh.read())


def wbs_data():
    return {"wbs": [
        {"code": "1", "name": "Study"},
        {"code": "1.1", "name": "Prepare", "duration_days": 2, "effort_days": 4, "cost": 100, "percent_complete": 100},
        {"code": "1.2", "name": "Workshop", "duration_days": 5, "effort_days": 20, "cost": 400, "percent_complete": 50, "predecessors": ["1.1"]},
        {"code": "2", "name": "Report"},
        {"code": "2.1", "name": "Draft", "duration_days": 3, "effort_days": 6, "cost": 300, "percent_complete": 0, "predecessors": ["1.2"]}]}


class Wbs(unittest.TestCase):
    def test_rollup_conserves(self):
        r = {n["code"]: n for n in wbs.roll_up(wbs_data())}
        self.assertAlmostEqual(r["1"]["effort_days"], r["1.1"]["effort_days"] + r["1.2"]["effort_days"])
        self.assertAlmostEqual(r["1"]["cost"], 500)
        leaves = [n for n in r.values() if n["leaf"]]
        self.assertAlmostEqual(sum(n["effort_days"] for n in leaves), r["1"]["effort_days"] + r["2"]["effort_days"])
        self.assertTrue(r["1.2"]["percent_complete"] <= r["1"]["percent_complete"] <= r["1.1"]["percent_complete"])
        self.assertAlmostEqual(r["1"]["percent_complete"], (100 * 4 + 50 * 20) / 24)

    def test_check_refuses(self):
        d = wbs_data()
        d["wbs"].append({"code": "3.1", "name": "orphan", "duration_days": 1})
        self.assertTrue(any("parent" in e for e in wbs.check(d)))
        d = wbs_data()
        d["wbs"].append({"code": "1.1", "name": "dup", "duration_days": 1})
        self.assertTrue(any("duplicate" in e for e in wbs.check(d)))
        d = wbs_data()
        d["wbs"][1]["duration_days"] = -1
        self.assertTrue(wbs.check(d))
        d = wbs_data()
        d["wbs"][2]["predecessors"] = ["9.9"]
        self.assertTrue(any("unknown predecessor" in e for e in wbs.check(d)))
        d = wbs_data()
        d["wbs"][0]["code"] = "one"
        self.assertTrue(wbs.check(d))

    def test_to_schedule_runs_and_summary_dates(self):
        p = schedule.plan(wbs.to_schedule(wbs_data(), "2026-01-05"))
        self.assertEqual(p["critical_path"], ["1.1", "1.2", "2.1"])
        self.assertAlmostEqual(p["duration_days"], 10)
        s = wbs.summary_dates(wbs_data(), p)
        self.assertEqual(s["1"]["start"], "2026-01-05")
        self.assertEqual(s["2"]["finish"], p["finish"])

    def test_template_structure_only(self):
        t = wbs.template("hazop", nodes=["Node 1 Feed", "Node 2 Reactor"])
        d = {"wbs": t}
        self.assertEqual(wbs.check(d, require_estimates=False), [])
        leaves = [n for n in t if not any(m["code"].startswith(n["code"] + ".") for m in t)]
        self.assertTrue(all(n.get("duration_days") is None and n.get("effort_days") is None for n in leaves))
        self.assertTrue(any("Node 2 Reactor" in n["name"] for n in t))
        self.assertTrue(wbs.check(d))                     # estimates still missing: refused for scheduling
        with self.assertRaises(ValueError):
            wbs.template("nope")


def reg():
    return {"today": "2026-11-09",
            "stage_probability": {"identified": 0.1, "qualifying": 0.2, "bid": 0.4, "submitted": 0.5},
            "tenders": [
                {"id": "T1", "client": "X", "title": "HAZOP of unit A", "service": "HAZOP", "stage": "bid", "value": 100,
                 "published": "2026-10-20", "submission_deadline": "2026-11-12", "award_expected": "2026-12-15", "start_expected": "2027-01-10"},
                {"id": "T2", "client": "Y", "title": "QRA", "service": "QRA", "stage": "submitted", "value": 300,
                 "submission_deadline": "2026-11-01", "award_expected": "2026-11-05"},
                {"id": "T3", "client": "Z", "title": "HAZOP revalidation", "service": "HAZOP", "stage": "won", "value": 50,
                 "start_expected": "2026-11-20"},
                {"id": "T4", "client": "Z", "title": "Old", "service": "HAZOP", "stage": "lost", "value": 40},
                {"id": "T5", "client": "W", "title": "Identified", "service": "SIL", "stage": "identified", "value": 20,
                 "submission_deadline": "2026-11-02"}]}


class Tenders(unittest.TestCase):
    def test_deadlines_and_missed(self):
        r = reg()
        out = tr.deadlines(r["tenders"], D(2026, 11, 9), 14)
        ids = [(x["id"], x["event"]) for x in out["upcoming"]]
        self.assertIn(("T1", "submission_deadline"), ids)
        self.assertIn(("T3", "start_expected"), ids)
        self.assertEqual(sorted(x["id"] for x in out["missed"]), ["T5"])          # deadline passed, never reached bid
        self.assertEqual([x["id"] for x in out["chase"]], ["T2"])                 # submitted, award date passed
        self.assertEqual([x["days_left"] for x in out["upcoming"]], sorted(x["days_left"] for x in out["upcoming"]))

    def test_upcoming_projects(self):
        u = tr.upcoming_projects(reg()["tenders"], D(2026, 11, 9), 30)
        self.assertEqual([x["id"] for x in u], ["T3"])
        u = tr.upcoming_projects(reg()["tenders"], D(2026, 11, 9), 90, include_open=True)
        self.assertEqual({x["id"]: x["confirmed"] for x in u}, {"T3": True, "T1": False})

    def test_pipeline_sums(self):
        r = reg()
        p = tr.weighted_pipeline(r["tenders"], r["stage_probability"])
        self.assertAlmostEqual(sum(v["weighted"] for v in p["by_stage"].values()), p["weighted_total"])
        self.assertAlmostEqual(p["weighted_total"], 100 * 0.4 + 300 * 0.5 + 20 * 0.1)
        self.assertAlmostEqual(p["booked"], 50)
        self.assertAlmostEqual(sum(p["by_award_month"].values()), p["weighted_total"] - 20 * 0.1)  # T5 has no award date
        self.assertEqual(p["unscheduled_weighted"], 20 * 0.1)
        r["tenders"][0]["probability"] = 1.0
        self.assertAlmostEqual(tr.weighted_pipeline(r["tenders"], r["stage_probability"])["weighted_total"], 100 + 150 + 2)
        self.assertIsNone(tr.weighted_pipeline(r["tenders"], {})["weighted_total"])

    def test_bid_score(self):
        cfg = {"weights": {"fit": 3, "margin": 2, "capacity": 1}, "scale_max": 5, "bid_threshold": 0.7, "review_threshold": 0.5}
        e = {"scores": {"fit": 5, "margin": 4, "capacity": 3}}
        s = tr.bid_score(e, cfg)
        self.assertAlmostEqual(s["score"], (3 * 5 + 2 * 4 + 1 * 3) / (5 * 6))
        self.assertEqual(s["recommendation"], "bid")
        cfg2 = dict(cfg, weights={k: 10 * v for k, v in cfg["weights"].items()})
        self.assertAlmostEqual(tr.bid_score(e, cfg2)["score"], s["score"])
        e2 = {"scores": {"fit": 5, "margin": 5, "capacity": 3}}
        self.assertGreaterEqual(tr.bid_score(e2, cfg)["score"], s["score"])
        self.assertEqual(tr.bid_score({"scores": {"fit": 0, "margin": 1, "capacity": 0}}, cfg)["recommendation"], "no bid")
        self.assertEqual(tr.bid_score({"scores": {"fit": 5}}, cfg)["recommendation"], "incomplete")
        with self.assertRaises(ValueError):
            tr.bid_score(e, {"weights": cfg["weights"], "scale_max": 5})

    def test_win_rate(self):
        w = tr.win_rate(reg()["tenders"])
        self.assertAlmostEqual(w["overall"]["rate"], 1 / 2)
        self.assertEqual(w["by_service"]["HAZOP"]["won"], 1)
        self.assertIsNone(tr.win_rate([{"id": "x", "stage": "bid"}])["overall"]["rate"])

    def test_check_refuses(self):
        r = reg()
        r["tenders"][0]["stage"] = "dreaming"
        self.assertTrue(any("stage" in e for e in tr.check(r)))
        r = reg()
        r["tenders"][0]["award_expected"] = "2026-10-01"       # before submission deadline
        self.assertTrue(any("order" in e for e in tr.check(r)))
        r = reg()
        r["tenders"][0]["probability"] = 1.5
        self.assertTrue(tr.check(r))
        r = reg()
        r["tenders"][1]["id"] = "T1"
        self.assertTrue(any("duplicate" in e for e in tr.check(r)))
        r = reg()
        r["tenders"][0]["submission_deadline"] = "12/11/2026"
        self.assertTrue(tr.check(r))
        self.assertEqual(tr.check(reg()), [])

    def test_triage(self):
        rules = {"services": {"HAZOP": ["hazop", "hazard and operability"], "QRA": ["quantitative risk"]}, "include": ["process safety"],
                 "exclude": ["catering"]}
        items = [{"title": "Tender for HAZOP study of LPG terminal", "text": "", "source": "feed"},
                 {"title": "Catering services", "text": "includes a hazop of the kitchen", "source": "feed"},
                 {"title": "Road works", "text": "asphalt", "source": "feed"},
                 {"title": "Process safety audit", "text": "Quantitative risk assessment required", "source": "feed"}]
        out = tr.triage(items, rules)
        self.assertEqual([c["title"] for c in out], ["Tender for HAZOP study of LPG terminal", "Process safety audit"])
        self.assertEqual(out[1]["services"], ["QRA"])
        self.assertEqual(tr.triage([{"title": "hazopper", "text": ""}], rules), [])      # whole words only


def project(done=50):
    return {"id": "P1", "name": "HAZOP unit A", "tender_id": "T3", "budget": 1000, "actual_cost": 600, "status_date": "2026-01-09",
            "start": "2026-01-05", "calendar": {"workdays": [0, 1, 2, 3, 4]},
            "activities": [{"id": "A", "duration_days": 4, "owner": "ann", "effort_days": 4, "percent_complete": done},
                           {"id": "B", "duration_days": 4, "owner": "ann", "effort_days": 4, "predecessors": ["A"], "percent_complete": 0}]}


class Portfolio(unittest.TestCase):
    def data(self):
        return {"today": "2026-01-09", "tenders": reg()["tenders"], "stage_probability": reg()["stage_probability"],
                "capacity_days_per_week": {"ann": 5}, "projects": [project()],
                "pha": {"actions": [{"id": "1", "study": "S", "node": "n", "risk": "high", "owner": "ann", "due": "2025-12-01", "status": "open"}],
                        "revalidations": [{"unit": "U1", "last_pha": "2021-01-01", "mocs_since": 0, "incidents_since": 0}]}}

    def test_earned_value_identities(self):
        p = portfolio.run(self.data())["projects"][0]
        ev = p["earned_value"]
        self.assertTrue(0 <= ev["PV"] <= 1000 and 0 <= ev["EV"] <= 1000)
        self.assertAlmostEqual(ev["EV"], 250.0)                  # (4 x 50% + 4 x 0%) / 8 of the budget
        self.assertAlmostEqual(ev["PV"], 625.0)                  # planned by Fri 9 Jan: A done, B (starts that Friday) a quarter done
        self.assertAlmostEqual(ev["SV"], ev["EV"] - ev["PV"])
        self.assertAlmostEqual(ev["SPI"], ev["EV"] / ev["PV"])
        self.assertAlmostEqual(ev["CPI"], 250 / 600)
        self.assertAlmostEqual(ev["EAC"], 1000 / (250 / 600))
        d = self.data()
        d["projects"][0]["activities"][0]["percent_complete"] = 100
        d["projects"][0]["activities"][1]["percent_complete"] = 25
        ev2 = portfolio.run(d)["projects"][0]["earned_value"]
        self.assertAlmostEqual(ev2["EV"], ev2["PV"])
        self.assertAlmostEqual(ev2["SPI"], 1.0)

    def test_missing_budget_or_cost_not_guessed(self):
        d = self.data()
        del d["projects"][0]["budget"]
        self.assertIsNone(portfolio.run(d)["projects"][0]["earned_value"])
        d = self.data()
        del d["projects"][0]["actual_cost"]
        ev = portfolio.run(d)["projects"][0]["earned_value"]
        self.assertIsNone(ev["CPI"])
        self.assertIsNone(ev["EAC"])

    def test_report_sections(self):
        r = portfolio.run(self.data())
        for k in ("headline", "deadlines", "upcoming_projects", "pipeline", "projects", "overloads", "needs_plan", "pha", "notes", "checks"):
            self.assertIn(k, r)
        self.assertEqual(r["needs_plan"], [])                    # T3 is covered by project P1
        self.assertEqual(r["pha"]["actions"]["overdue"], 1)
        self.assertEqual(r["pha"]["revalidations"][0]["unit"], "U1")
        self.assertTrue(r["pha"]["revalidations"][0]["overdue"])
        d = self.data()
        d["projects"] = []
        self.assertEqual([x["id"] for x in portfolio.run(d)["needs_plan"]], ["T3"])

    def test_capacity_across_projects(self):
        d = self.data()
        d["projects"].append(dict(project(), id="P2", tender_id=None))
        r = portfolio.run(d)
        self.assertTrue(r["overloads"])                          # two projects of ann in the same weeks against 5 d/week
        self.assertAlmostEqual(sum(x["demand_days"] for x in r["load"] if x["owner"] == "ann"), 16.0)

    def test_pha_actions_match_pha_module(self):
        d = self.data()
        want = pha.action_status(d["pha"]["actions"], D(2026, 1, 9))
        self.assertEqual(portfolio.run(d)["pha"]["actions"]["overdue"], want["overdue"])

    def test_html_written(self):
        import tempfile
        d = self.data()
        d["today"] = "2026-11-09"
        r = portfolio.run(d)
        with tempfile.TemporaryDirectory() as t:
            path = os.path.join(t, "r.html")
            portfolio.write_html(r, path)
            with open(path, encoding="utf-8") as fh:
                txt = fh.read()
            self.assertIn("<html", txt)
            self.assertIn("P1", txt)
            self.assertIn("T1", txt)

    def test_refuses_bad_inputs(self):
        d = self.data()
        d["tenders"][0]["stage"] = "x"
        r = portfolio.run(d)
        self.assertTrue(any(c.startswith("FAIL") for c in r["checks"]))


class Examples(unittest.TestCase):
    def test_examples_pass_their_checks(self):
        from process_safety import tools
        import tempfile
        for name in ("wbs", "schedule", "tenders", "portfolio"):
            with tempfile.TemporaryDirectory() as t:
                s = tools.run_tool(name, load(name), t, progress=False)
                self.assertFalse(any(str(c).startswith("FAIL") for c in s["checks"]), (name, s["checks"]))
                self.assertTrue(s.get("files"), name)


if __name__ == "__main__":
    unittest.main()

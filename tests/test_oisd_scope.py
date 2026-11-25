import re
import unittest

from process_safety import standards


class OisdScope(unittest.TestCase):
    def setUp(self):
        self.d = standards.oisd_refinery_scope()
        self.official = standards.oisd()["standards"]

    def test_table_has_sixty_numbered_rows(self):
        es = self.d["entries"]
        self.assertEqual(len(es), self.d["letter_statistics"]["applicable_to_refineries_and_gpp"])
        self.assertEqual([e["n"] for e in es], list(range(1, 61)))
        self.assertEqual(len({e["letter_id"] for e in es}), 60)

    def test_ids_are_well_formed_and_scopes_present(self):
        for e in self.d["entries"]:
            self.assertRegex(e["letter_id"], r"^OISD-(STD|RP|GDN)-\d+$")
            self.assertGreater(len(e["letter_title_and_scope"]), 40, e["letter_id"])

    def test_id_status_agrees_with_the_official_list(self):
        for e in self.d["entries"]:
            num = re.search(r"(\d+)$", e["letter_id"]).group(1)
            same_num = [k for k in self.official if k.endswith("-" + num)]
            if e["letter_id"] in self.official:
                self.assertEqual((e["id_status"], e["official_id"]), ("exact", e["letter_id"]))
            elif same_num:
                self.assertEqual((e["id_status"], e["official_id"]), ("prefix_changed", same_num[0]))
            else:
                self.assertEqual((e["id_status"], e["official_id"]), ("absent_from_2026_list", None))
            if e["official_id"]:
                self.assertEqual(e["official_title"], self.official[e["official_id"]]["title"])

    def test_mandatory_list_matches_the_letter(self):
        self.assertEqual(len(standards.oisd_mandatory()), self.d["letter_statistics"]["mandatory_by_statute"])
        for must in ("OISD-STD-105", "OISD-STD-116", "OISD-STD-118", "OISD-STD-150", "OISD-GDN-178"):
            self.assertIn(must, standards.oisd_mandatory())

    def test_lookup_by_either_number(self):
        a, b = standards.oisd_scope("OISD-GDN-178"), standards.oisd_scope("OISD-STD-178")
        self.assertIs(a["n"], b["n"])
        self.assertEqual(a["id_status"], "prefix_changed")
        self.assertIsNone(standards.oisd_scope("OISD-STD-999"))

    def test_known_scope_statements(self):
        self.assertIn("1 kg/cm2g", standards.oisd_scope("OISD-STD-106")["letter_title_and_scope"].lower())
        self.assertIn("not cover", standards.oisd_scope("OISD-STD-113")["letter_title_and_scope"].lower())


if __name__ == "__main__":
    unittest.main()

import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
from gen_use_cases import run  # noqa: E402
from use_case_cmds import CASES, TEXT  # noqa: E402


class UseCases(unittest.TestCase):
    def test_every_command_runs_and_is_in_the_doc(self):
        with open(os.path.join(ROOT, "docs", "USE_CASES.md"), encoding="utf-8") as fh:
            doc = fh.read()
        self.assertEqual(set(CASES), set(TEXT))
        for cid, steps in CASES.items():
            for label, args, _ in steps:
                rc, _ = run(args)
                self.assertEqual(rc, 0, f"{cid}: {args}")
                self.assertIn(label, doc, "docs/USE_CASES.md is stale: python scripts/gen_use_cases.py --write")


if __name__ == "__main__":
    unittest.main()


class DesignAwareness(unittest.TestCase):
    def test_commands_named_in_doc_exist(self):
        import re
        from process_safety.cli import REGISTRY
        with open(os.path.join(ROOT, "docs", "DESIGN_AWARENESS.md"), encoding="utf-8") as fh:
            names = set(re.findall(r"cmd:([a-z0-9-]+)", fh.read()))
        self.assertTrue(names)
        self.assertEqual(names - set(REGISTRY), set())

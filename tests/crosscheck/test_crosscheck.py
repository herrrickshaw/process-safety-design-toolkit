"""Optional cross-check suite: skipped unless fluids, thermo and CoolProp are installed (see tests/crosscheck/validate.py)."""
import importlib.util
import os
import subprocess
import sys
import unittest

NEEDED = ("fluids", "thermo", "CoolProp")


@unittest.skipUnless(all(importlib.util.find_spec(m) for m in NEEDED), "needs: pip install fluids thermo CoolProp")
class CrossCheck(unittest.TestCase):
    def test_all_checks_within_tolerance(self):
        r = subprocess.run([sys.executable, os.path.join(os.path.dirname(__file__), "validate.py")], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout[-2000:] + r.stderr[-2000:])
        self.assertIn("outside: 0", r.stdout)


if __name__ == "__main__":
    unittest.main()

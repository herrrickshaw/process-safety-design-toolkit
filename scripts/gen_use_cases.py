"""Run the commands in use_case_cmds.CASES and write docs/USE_CASES.md (python scripts/gen_use_cases.py --write)."""
import json
import os
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from use_case_cmds import CASES, TEXT  # noqa: E402

ROOT = os.path.dirname(HERE)


def rnd(o):
    if isinstance(o, float):
        return float(f"{o:.4g}")
    if isinstance(o, list):
        return [rnd(x) for x in o]
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    return o


def run(args):
    r = subprocess.run([sys.executable, "-m", "process_safety", *args], capture_output=True, text=True, cwd=ROOT)
    return r.returncode, r.stdout


def shown(out, keys):
    try:
        j = json.loads(out)
    except ValueError:
        return out.strip()
    if keys:
        j = {k: j[k] for k in keys if k in j}
    return json.dumps(rnd(j), indent=2)


def build() -> str:
    lines = ["# Use cases", "",
             "Worked scenarios, each run with real commands. Every command below is executed by the test suite (exit status 0), and the",
             "numbers are copied from a run of `python scripts/gen_use_cases.py --write` (4 significant figures, selected fields shown).",
             "These are screening results: read the limit in each takeaway, and see `docs/VALIDATION.md` for what was cross-checked.", ""]
    for cid, steps in CASES.items():
        title, sector, situation, takeaway = TEXT[cid]
        lines += [f"## {title}", "", f"*Sector: {sector}.*", "", situation, ""]
        for label, args, keys in steps:
            rc, out = run(args)
            if rc != 0:
                raise SystemExit(f"command failed ({cid}): {args}")
            lines += [f"**{label}**", "", "```bash", "python3 -m process_safety " + " ".join(shlex.quote(a) for a in args), "```", "",
                      "```json", shown(out, keys), "```", ""]
        lines += [f"**Takeaway.** {takeaway}", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    text = build()
    if "--write" in sys.argv:
        with open(os.path.join(ROOT, "docs", "USE_CASES.md"), "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote docs/USE_CASES.md", len(text.splitlines()), "lines")
    else:
        print(text)

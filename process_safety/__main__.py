"""CLI: python -m process_safety <command> ... (run with -h for the list; commands live in process_safety/cli/)."""
from __future__ import annotations

import argparse
import sys

from . import cli  # noqa: F401  (importing the package registers every command)
from .cli.registry import REGISTRY, check_ranges


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="process_safety", description=__doc__)
    p.add_argument("--no-range-check", action="store_true", help="skip input range checks (not recommended)")
    sub = p.add_subparsers(dest="cmd", required=True)
    for c in REGISTRY.values():
        c.add_arguments(sub.add_parser(c.name, help=c.help))
    return p


def main(argv=None):
    p = build_parser()
    a = p.parse_args(argv)
    cmd = REGISTRY[a.cmd]
    if not a.no_range_check:
        for w in check_ranges(cmd, a, p):
            print("warning: " + w, file=sys.stderr)
    return cmd.run(a, p) or 0


if __name__ == "__main__":
    sys.exit(main())

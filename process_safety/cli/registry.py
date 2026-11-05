"""Command registry: each CLI command is one class registered by name (Open/Closed: add a command, edit no dispatcher).

A command class provides:
    add_arguments(parser)   declare its arguments (single responsibility: parsing only)
    run(args, parser) -> int | None   do the work and print through `emit`
Optional class attribute `ranges = {dest: range_name}` links numeric arguments to entries in `process_safety.ranges`;
the framework then rejects impossible values (exit 2) and warns on atypical ones (stderr), unless --no-range-check is given.
"""
from __future__ import annotations

import dataclasses
import json
from typing import Callable

from .. import ranges


def emit(obj) -> None:
    """Single output path: indented JSON; dataclasses are converted."""
    print(json.dumps(dataclasses.asdict(obj) if dataclasses.is_dataclass(obj) else obj, indent=2, default=float))


@dataclasses.dataclass(frozen=True)
class Command:
    name: str
    help: str | None
    add_arguments: Callable
    run: Callable
    ranges: dict


REGISTRY: dict[str, Command] = {}


def command(name: str, help: str | None = None):
    """Class decorator registering a command class under `name`."""
    def deco(cls):
        if name in REGISTRY:
            raise ValueError(f"duplicate command {name!r}")
        REGISTRY[name] = Command(name, help, cls.add_arguments, cls.run, dict(getattr(cls, "ranges", {})))
        return cls
    return deco


def check_ranges(cmd: Command, args, parser) -> list[str]:
    """Hard violations end the run via parser.error (exit 2); soft ones are returned as warnings."""
    warnings: list[str] = []
    for dest, rname in cmd.ranges.items():
        value = getattr(args, dest, None)
        if value is None:
            continue
        values = value if isinstance(value, (list, tuple)) else [value]
        for v in values:
            try:
                warnings += ranges.check(rname, v, f"--{dest.replace('_', '-')}")
            except ranges.RangeError as e:
                parser.error(str(e))
    return warnings

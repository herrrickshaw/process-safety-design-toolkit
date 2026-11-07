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

from .. import ranges, units


def emit(obj) -> None:
    """Single output path: indented JSON; dataclasses are converted."""
    data = dataclasses.asdict(obj) if dataclasses.is_dataclass(obj) else obj
    if units.active_system() == "us":
        data = units.add_us_keys(json.loads(json.dumps(data, default=float)))
    print(json.dumps(data, indent=2, default=float))


@dataclasses.dataclass(frozen=True)
class Command:
    name: str
    help: str | None
    add_arguments: Callable
    run: Callable
    ranges: dict
    units: dict = dataclasses.field(default_factory=dict)   # dest -> working unit, for arguments without a range entry


REGISTRY: dict[str, Command] = {}


def command(name: str, help: str | None = None):
    """Class decorator registering a command class under `name`."""
    def deco(cls):
        if name in REGISTRY:
            raise ValueError(f"duplicate command {name!r}")
        REGISTRY[name] = Command(name, help, cls.add_arguments, cls.run, dict(getattr(cls, "ranges", {})), dict(getattr(cls, "units", {})))
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


def arg_unit(cmd: Command, dest: str) -> str | None:
    """The unit a numeric argument is given in: from its range entry, else the command's `units` table, else None."""
    if dest in cmd.units:
        return cmd.units[dest]
    if dest in cmd.ranges:
        return ranges.RANGES[cmd.ranges[dest]].unit
    return None


def convert_args(cmd: Command, args, system: str) -> None:
    """Convert every dimensioned numeric argument typed in `system` to the command's working unit, in place."""
    if system == "si":
        return
    for dest in vars(args):
        u = arg_unit(cmd, dest)
        v = getattr(args, dest)
        if u is None or v is None or isinstance(v, bool):
            continue
        if isinstance(v, (list, tuple)):
            setattr(args, dest, type(v)(units.to_cli(x, u, system) for x in v))
        elif isinstance(v, (int, float)):
            setattr(args, dest, units.to_cli(v, u, system))

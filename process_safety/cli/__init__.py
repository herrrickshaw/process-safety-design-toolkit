"""Command-line layer: registry + one module per domain. Importing the modules registers their commands."""
from . import electrical_cmds, fire_cmds, regulatory_cmds, relief_cmds, reliability_cmds, risk_cmds, utility_cmds  # noqa: F401
from .registry import REGISTRY, emit  # noqa: F401

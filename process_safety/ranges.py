"""Accepted-value ranges for the quantities the toolkit takes as inputs.

Two tiers, so a screening tool neither lets nonsense through nor blocks an unusual-but-real case:

* **hard** range: physically or mathematically impossible outside it (a negative absolute temperature, a heat-capacity ratio of 1
  or less, a fraction above 1). A hard violation raises `RangeError` (a `ValueError`) and the CLI exits with status 2.
* **soft** range: the typical engineering range. A value outside it is allowed but returns a warning ("check the value"); the CLI
  prints it to stderr and carries on.

The ranges are data (`RANGES`), not code: add or tighten one in a single place, and `python -m process_safety ranges` and
`docs/RANGES.md` follow. They are screening guards, not design limits: a standard or a vendor datasheet always governs.
"""
from __future__ import annotations

import functools
import inspect
import math
from dataclasses import dataclass


class RangeError(ValueError):
    """An input is outside the physically or mathematically possible (hard) range."""


@dataclass(frozen=True)
class Range:
    name: str
    unit: str
    description: str
    hard_min: float | None = None
    hard_max: float | None = None
    min_exclusive: bool = False      # hard_min itself is not allowed
    max_exclusive: bool = False
    soft_min: float | None = None
    soft_max: float | None = None
    note: str = ""

    def hard_text(self) -> str:
        lo = "-inf" if self.hard_min is None else f"{self.hard_min:g}"
        hi = "inf" if self.hard_max is None else f"{self.hard_max:g}"
        left = "(" if self.min_exclusive or self.hard_min is None else "["
        right = ")" if self.max_exclusive or self.hard_max is None else "]"
        return f"{left}{lo}, {hi}{right}"

    def soft_text(self) -> str:
        if self.soft_min is None and self.soft_max is None:
            return "-"
        lo = "-inf" if self.soft_min is None else f"{self.soft_min:g}"
        hi = "inf" if self.soft_max is None else f"{self.soft_max:g}"
        left = "(" if self.soft_min is None else "["
        right = ")" if self.soft_max is None else "]"
        return f"{left}{lo}, {hi}{right}"

    def unit_text(self) -> str:
        return "" if self.unit == "-" else f" {self.unit}"

    def violates_hard(self, v: float) -> bool:
        if math.isnan(v):
            return True
        if self.hard_min is not None and (v < self.hard_min or (self.min_exclusive and v == self.hard_min)):
            return True
        return self.hard_max is not None and (v > self.hard_max or (self.max_exclusive and v == self.hard_max))

    def outside_soft(self, v: float) -> bool:
        return (self.soft_min is not None and v < self.soft_min) or (self.soft_max is not None and v > self.soft_max)


def _r(name, unit, description, **kw):
    return name, Range(name, unit, description, **kw)


_POS = dict(hard_min=0.0, min_exclusive=True)
_NONNEG = dict(hard_min=0.0)

RANGES: dict[str, Range] = dict([
    # thermodynamic state
    _r("temperature_K", "K", "absolute temperature", **_POS, soft_min=50, soft_max=3000),
    _r("temperature_C", "degC", "temperature", hard_min=-273.15, min_exclusive=True, soft_min=-200, soft_max=800),
    _r("pressure_abs_kPa", "kPa abs", "absolute pressure", **_POS, soft_min=1, soft_max=100_000),
    _r("set_pressure_kPag", "kPag", "relief or design set pressure (gauge)", **_POS, soft_min=7, soft_max=40_000,
       note="API 2000 tanks start near 7 kPag; API 526 valves go to about 40 MPa"),
    _r("back_pressure_kPag", "kPag", "total back pressure (gauge)", **_NONNEG, soft_max=5_000),
    _r("design_pressure_barg", "barg", "design pressure (gauge)", **_NONNEG, soft_max=1.034, note="API 2000 covers up to 1.034 barg"),
    _r("molar_mass_kg_kmol", "kg/kmol", "molar mass", **_POS, soft_min=2, soft_max=500),
    _r("heat_capacity_ratio", "-", "Cp/Cv (isentropic exponent)", hard_min=1.0, min_exclusive=True, soft_max=1.67,
       note="1.67 is monatomic; most process gases are 1.1 to 1.4"),
    _r("compressibility", "-", "gas compressibility factor Z", **_POS, soft_min=0.2, soft_max=1.5),
    _r("density_kg_m3", "kg/m3", "density", **_POS, soft_min=0.05, soft_max=2500),
    _r("viscosity_cP", "cP", "dynamic viscosity", **_POS, soft_min=0.005, soft_max=10_000),
    _r("latent_heat_kJ_kg", "kJ/kg", "latent heat of vaporisation", **_POS, soft_min=50, soft_max=2500),
    _r("heat_of_combustion_kJ_kg", "kJ/kg", "heat of combustion", **_POS, soft_min=1_000, soft_max=150_000),
    _r("heat_of_combustion_MJ_kg", "MJ/kg", "heat of combustion", **_POS, soft_min=1, soft_max=150),
    _r("specific_heat_kJ_kgK", "kJ/kg/K", "specific heat", **_POS, soft_min=0.5, soft_max=10),
    # sizes and flows
    _r("length_m", "m", "length or diameter", **_POS, soft_max=2_000),
    _r("nonneg_length_m", "m", "length that may be zero (elevation, release height, liquid level)", **_NONNEG, soft_max=200),
    _r("area_m2", "m2", "area", **_POS, soft_min=0.1, soft_max=100_000),
    _r("area_mm2", "mm2", "orifice or vent area", **_NONNEG, soft_max=1_000_000),
    _r("volume_m3", "m3", "volume or capacity", **_POS, soft_min=0.001, soft_max=500_000),
    _r("flow_m3_h", "m3/h", "volumetric flow", **_NONNEG, soft_max=100_000),
    _r("mass_flow_kg_h", "kg/h", "mass flow", **_POS, soft_max=5_000_000),
    _r("mass_flow_kg_s", "kg/s", "mass flow", **_POS, soft_max=10_000),
    _r("release_rate_g_s", "g/s", "release rate", **_POS, soft_max=10_000_000),
    _r("mass_kg", "kg", "mass", **_POS, soft_max=10_000_000_000),
    _r("wall_mm", "mm", "wall thickness", **_POS, soft_min=1, soft_max=100),
    _r("wind_speed_m_s", "m/s", "wind speed at release height", **_POS, soft_min=0.5, soft_max=25),
    _r("concentration_ppm", "ppm", "concentration", **_POS, soft_min=0.01, soft_max=1_000_000),
    _r("time_s", "s", "time or duration", **_POS, soft_max=86_400),
    _r("time_nonneg_s", "s", "time that may be zero", **_NONNEG, soft_max=86_400),
    _r("time_min", "min", "time", **_POS, soft_max=1_440),
    # dimensionless
    _r("fraction_0_1", "-", "fraction or efficiency", hard_min=0.0, hard_max=1.0),
    _r("coefficient_0_1", "-", "coefficient in (0, 1] (discharge, back-pressure, combination, superheat)", **_POS, hard_max=1.0, soft_min=0.5),
    _r("environment_factor", "-", "fire environment factor F", **_POS, hard_max=1.0, soft_min=0.03),
    _r("pfd", "-", "probability of failure on demand", **_POS, hard_max=1.0),
    _r("beta_factor", "-", "common-cause beta factor", hard_min=0.0, hard_max=1.0, soft_max=0.2),
    _r("frequency_per_yr", "1/yr", "event frequency", **_POS, soft_min=1e-9, soft_max=100),
    _r("failure_rate_per_h", "1/h", "dangerous undetected failure rate", **_POS, soft_min=1e-10, soft_max=1e-4),
    _r("proof_test_years", "yr", "proof-test interval", **_POS, soft_min=0.01, soft_max=20),
    _r("multiplier_positive", "-", "positive multiplier", **_POS),
    # electrical and mechanical
    _r("voltage_kV", "kV", "line-to-line voltage", **_POS, soft_min=0.1, soft_max=800),
    _r("current_kA", "kA", "fault current", **_POS, soft_min=0.5, soft_max=106),
    _r("current_A", "A", "current", **_POS, soft_max=200_000),
    _r("distance_mm", "mm", "working distance or detection capability", **_POS, soft_min=6, soft_max=3_000),
    _r("relay_tms", "-", "time multiplier setting", **_POS, soft_min=0.025, soft_max=1.5),
    _r("resistivity_ohm_m", "ohm m", "resistivity", **_POS, soft_min=1, soft_max=10_000),
    _r("sound_level_dBA", "dBA", "sound level", hard_min=0.0, soft_min=40, soft_max=140),
    _r("exposure_hours", "h", "exposure time", **_POS, hard_max=24.0),
    _r("smys_MPa", "MPa", "specified minimum yield strength", **_POS, soft_min=100, soft_max=900),
    _r("section_factor_1_m", "1/m", "steel section factor Am/V", **_POS, soft_min=10, soft_max=500),
    _r("diameter_mm", "mm", "pipe outside diameter", **_POS, soft_min=10, soft_max=2000),
    _r("heat_flux_kW_m2", "kW/m2", "absorbed heat flux", **_POS, soft_min=10, soft_max=400),
    _r("power_kW", "kW", "power", **_POS, soft_max=10_000_000),
    _r("temperature_rise_K", "K", "temperature rise", **_POS, soft_min=1, soft_max=50),
    _r("omega_parameter", "-", "omega compressibility parameter of a two-phase / flashing fluid", **_POS, soft_min=0.1, soft_max=500),
    _r("emissive_power_kW_m2", "kW/m2", "flame surface emissive power (SEP)", **_POS, soft_min=20, soft_max=400),
    _r("fuel_consumption_g_kWh", "g/kWh", "specific fuel consumption (vendor data)", **_POS, soft_min=150, soft_max=350),
])


def get(name: str) -> Range:
    try:
        return RANGES[name]
    except KeyError:
        raise KeyError(f"unknown range {name!r}; see `python -m process_safety ranges`") from None


def check(name: str, value, label: str | None = None) -> list[str]:
    """Check one value against RANGES[name]. Raise RangeError outside the hard range; return warnings outside the soft range."""
    rng = get(name)
    label = label or name
    try:
        v = float(value)
    except (TypeError, ValueError):
        raise RangeError(f"{label}: {value!r} is not a number") from None
    if rng.violates_hard(v):
        raise RangeError(f"{label}={v:g}{rng.unit_text()} is outside the possible range {rng.hard_text()} for {rng.description}")
    if rng.outside_soft(v):
        extra = f" ({rng.note})" if rng.note else ""
        return [f"{label}={v:g}{rng.unit_text()} is outside the typical range {rng.soft_text()} for {rng.description}{extra}: check the value"]
    return []


def check_many(name: str, values, label: str | None = None) -> list[str]:
    return [w for v in values for w in check(name, v, label)]


def validated(**param_ranges: str):
    """Decorator: check named arguments of a function against RANGES before it runs (hard ranges only; raises RangeError).

        @validated(T_K="temperature_K", k="heat_capacity_ratio")
        def f(T_K, k): ...
    """
    for rname in param_ranges.values():
        get(rname)  # fail at import time on a typo

    def deco(fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            bound = sig.bind_partial(*args, **kwargs)
            for pname, rname in param_ranges.items():
                if pname in bound.arguments and bound.arguments[pname] is not None:
                    check(rname, bound.arguments[pname], pname)
            return fn(*args, **kwargs)

        return wrapper

    return deco


def markdown_table() -> str:
    rows = ["| Range name | Unit | Quantity | Hard range (rejected outside) | Soft range (warns outside) | Note |", "|---|---|---|---|---|---|"]
    for r in RANGES.values():
        rows.append(f"| `{r.name}` | {r.unit} | {r.description} | {r.hard_text()} | {r.soft_text()} | {r.note} |")
    return "\n".join(rows)

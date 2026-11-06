"""SI and US-customary units: exact conversions, a per-argument dimension table, and the rules that stop the classic mix-ups.

Every factor here is a legal definition or is derived from one, nothing is a remembered engineering value:

    inch = 0.0254 m, foot = 12 in, pound-mass = 0.45359237 kg, standard gravity = 9.80665 m/s2 (so lbf = lb x g),
    psi = lbf / in2, US gallon = 231 in3, International Table Btu = 1055.05585262 J, hour = 3600 s, degF = 5/9 K.

How the CLI uses it (`--units us`): a value typed in the US unit of its dimension is converted to the unit the command works in
(kPag, mm, m3/h ...) before the range check and the calculation. Outputs gain a sibling key in US units
(`required_area_mm2` -> `required_area_in2`). The calculation itself is always SI, so a US run is the SI run in other numbers.

Rules that are easy to get wrong, enforced or documented in docs/UNITS.md:

* Gauge and absolute pressure are different dimensions. psig converts to kPag, psia to kPa abs, by a pure factor. Changing
  between gauge and absolute adds or subtracts the standard atmosphere 101.325 kPa and is only done by `gauge_to_abs` /
  `abs_to_gauge`, never implicitly.
* Temperatures are absolute readings (degF -> K by offset). A temperature *difference* (delta-T) converts by the factor only
  (`temperature_difference`), and is a separate dimension here so it cannot be passed through the offset by mistake.
* Mass versus force: lb is mass, lbf is force. psi is force per area; lb/ft3 is mass density.
* Volumes at standard conditions (scf, Nm3, Sm3) are NOT converted: their reference temperature differs between sources, so a
  conversion would hide a choice. Give the mass flow instead.
* lb/lbmol equals kg/kmol numerically (factor 1), a unit pair worth knowing, not an error.
"""
from __future__ import annotations

from dataclasses import dataclass

from .constants import ATM_KPA, G

# ---- exact definitions -----------------------------------------------------------------------------------------------------
INCH_M = 0.0254
FOOT_M = 12 * INCH_M
LB_KG = 0.45359237
LBF_N = LB_KG * G
PSI_PA = LBF_N / INCH_M ** 2
GAL_US_M3 = 231 * INCH_M ** 3
BTU_J = 1055.05585262
HOUR_S = 3600.0
RANKINE_K = 5.0 / 9.0
F_ZERO_K = 459.67 * RANKINE_K            # 0 degF in kelvin


@dataclass(frozen=True)
class Unit:
    symbol: str
    dimension: str
    to_base: float                        # base = value * to_base + offset
    offset: float = 0.0


# base units: length m, area m2, volume m3, mass kg, pressure Pa (gauge or abs by dimension), temperature K, ...
_UNITS = [
    # length
    Unit("m", "length", 1.0), Unit("mm", "length", 1e-3), Unit("ft", "length", FOOT_M), Unit("in", "length", INCH_M),
    # area
    Unit("m2", "area", 1.0), Unit("mm2", "area", 1e-6), Unit("ft2", "area", FOOT_M ** 2), Unit("in2", "area", INCH_M ** 2),
    # volume
    Unit("m3", "volume", 1.0), Unit("ft3", "volume", FOOT_M ** 3), Unit("gal", "volume", GAL_US_M3),
    # mass
    Unit("kg", "mass", 1.0), Unit("lb", "mass", LB_KG),
    # pressure, absolute
    Unit("kPa abs", "pressure_abs", 1e3), Unit("psia", "pressure_abs", PSI_PA), Unit("bara", "pressure_abs", 1e5),
    # pressure, gauge
    Unit("kPag", "pressure_gauge", 1e3), Unit("barg", "pressure_gauge", 1e5), Unit("psig", "pressure_gauge", PSI_PA),
    # pressure with no gauge/absolute meaning: a stress, a differential, a load per area
    Unit("Pa", "pressure_plain", 1.0), Unit("kPa", "pressure_plain", 1e3), Unit("bar", "pressure_plain", 1e5),
    Unit("MPa", "pressure_plain", 1e6), Unit("psi", "pressure_plain", PSI_PA), Unit("ksi", "pressure_plain", 1e3 * PSI_PA),
    # temperature (absolute reading)
    Unit("K", "temperature", 1.0), Unit("degC", "temperature", 1.0, 273.15), Unit("degF", "temperature", RANKINE_K, F_ZERO_K),
    Unit("degR", "temperature", RANKINE_K),
    # temperature difference
    Unit("dK", "temperature_difference", 1.0), Unit("dF", "temperature_difference", RANKINE_K),
    # mass flow
    Unit("kg/s", "mass_flow", 1.0), Unit("kg/h", "mass_flow", 1 / HOUR_S), Unit("g/s", "mass_flow", 1e-3),
    Unit("lb/s", "mass_flow", LB_KG), Unit("lb/h", "mass_flow", LB_KG / HOUR_S),
    # volumetric flow
    Unit("m3/h", "volume_flow", 1 / HOUR_S), Unit("gpm", "volume_flow", GAL_US_M3 / 60.0), Unit("ft3/min", "volume_flow", FOOT_M ** 3 / 60.0),
    # density
    Unit("kg/m3", "density", 1.0), Unit("lb/ft3", "density", LB_KG / FOOT_M ** 3),
    # specific volume
    Unit("m3/kg", "specific_volume", 1.0), Unit("ft3/lb", "specific_volume", FOOT_M ** 3 / LB_KG),
    # dynamic viscosity (cP is in common use in both systems)
    Unit("cP", "viscosity", 1e-3),
    # energy per mass
    Unit("kJ/kg", "energy_per_mass", 1e3), Unit("MJ/kg", "energy_per_mass", 1e6), Unit("Btu/lb", "energy_per_mass", BTU_J / LB_KG),
    # specific heat
    Unit("kJ/kg/K", "specific_heat", 1e3), Unit("Btu/lb/degF", "specific_heat", BTU_J / LB_KG / RANKINE_K),
    # velocity
    Unit("m/s", "velocity", 1.0), Unit("ft/s", "velocity", FOOT_M),
    # heat flux
    Unit("kW/m2", "heat_flux", 1e3), Unit("Btu/h/ft2", "heat_flux", BTU_J / HOUR_S / FOOT_M ** 2),
    # heat-transfer coefficient
    Unit("W/m2K", "htc", 1.0), Unit("Btu/h/ft2/degF", "htc", BTU_J / HOUR_S / FOOT_M ** 2 / RANKINE_K),
    # molar mass (numerically equal)
    Unit("kg/kmol", "molar_mass", 1.0), Unit("lb/lbmol", "molar_mass", 1.0),
    # per length
    Unit("1/m", "per_length", 1.0), Unit("1/ft", "per_length", 1 / FOOT_M),
    # power, used as heat duty: kW is kept in both systems for electrical and data-centre work; Btu/h is offered for heat duty
    Unit("kW", "power", 1e3), Unit("W", "power", 1.0), Unit("Btu/h", "power", BTU_J / HOUR_S),
    # illuminance and luminous flux (SI lm and lux; US foot-candle = lm/ft2)
    Unit("lux", "illuminance", 1.0), Unit("fc", "illuminance", 1.0 / FOOT_M ** 2),
]

#: units that mean the same in both systems; they have no US counterpart and pass through unchanged
_NEUTRAL = {"-", "s", "min", "h", "yr", "1/yr", "1/h", "kV", "kA", "A", "ohm m", "dBA", "ppm", "g/kWh", "lm", "MW", "t", "tonne",
            "kg/m2/s", "kg/m2/h", "percent", "fraction", "ohm", "persons/m/s"}

UNITS: dict[str, Unit] = {u.symbol: u for u in _UNITS}

#: the US-customary counterpart of each unit a command works in (None = the quantity is the same in both systems)
US_FOR: dict[str, str] = {
    "m": "ft", "mm": "in", "m2": "ft2", "mm2": "in2", "m3": "ft3", "kg": "lb",
    "kPa abs": "psia", "kPag": "psig", "barg": "psig", "MPa": "ksi",
    "K": "degF", "degC": "degF", "dK": "dF",
    "kg/s": "lb/s", "kg/h": "lb/h", "g/s": "lb/h", "m3/h": "gpm",
    "kg/m3": "lb/ft3", "m3/kg": "ft3/lb", "cP": "cP",
    "kJ/kg": "Btu/lb", "MJ/kg": "Btu/lb", "kJ/kg/K": "Btu/lb/degF",
    "m/s": "ft/s", "kW/m2": "Btu/h/ft2", "W/m2K": "Btu/h/ft2/degF",
    "kg/kmol": "lb/lbmol", "1/m": "1/ft", "lux": "fc",
}
UNITS["cP"] = Unit("cP", "viscosity", 1e-3)

SYSTEMS = ("si", "us")


class UnitError(ValueError):
    """An unknown unit, or a conversion between different dimensions."""


def unit(symbol: str) -> Unit:
    try:
        return UNITS[symbol]
    except KeyError:
        raise UnitError(f"unknown unit {symbol!r}; known: {', '.join(sorted(UNITS))}") from None


def convert(value: float, src: str, dst: str) -> float:
    """Convert between two units of the SAME dimension. Gauge <-> absolute is refused (use gauge_to_abs / abs_to_gauge)."""
    if src in _NEUTRAL and dst == src:
        return value
    a, b = unit(src), unit(dst)
    if a.dimension != b.dimension:
        hint = ""
        if {a.dimension, b.dimension} == {"pressure_abs", "pressure_gauge"}:
            hint = " (gauge and absolute pressure differ by the atmosphere: use gauge_to_abs / abs_to_gauge)"
        raise UnitError(f"cannot convert {src} ({a.dimension}) to {dst} ({b.dimension}){hint}")
    return ((value * a.to_base + a.offset) - b.offset) / b.to_base


def gauge_to_abs(p_gauge: float, gauge_unit: str, abs_unit: str) -> float:
    """Gauge reading -> absolute pressure, adding the standard atmosphere (101.325 kPa). Units must be gauge and absolute."""
    if unit(gauge_unit).dimension != "pressure_gauge" or unit(abs_unit).dimension != "pressure_abs":
        raise UnitError("gauge_to_abs needs a gauge unit and an absolute unit")
    pa = p_gauge * unit(gauge_unit).to_base + ATM_KPA * 1e3
    return pa / unit(abs_unit).to_base


def abs_to_gauge(p_abs: float, abs_unit: str, gauge_unit: str) -> float:
    if unit(gauge_unit).dimension != "pressure_gauge" or unit(abs_unit).dimension != "pressure_abs":
        raise UnitError("abs_to_gauge needs an absolute unit and a gauge unit")
    pa = p_abs * unit(abs_unit).to_base - ATM_KPA * 1e3
    return pa / unit(gauge_unit).to_base


def parse_quantity(text: str, to: str) -> float:
    """'150 psig' -> value in `to` (kPag). A bare number is taken as already being in `to`."""
    parts = text.strip().split(None, 1)
    if len(parts) == 1:
        return float(parts[0])
    return convert(float(parts[0]), parts[1].strip(), to)


def is_neutral(symbol: str) -> bool:
    return symbol in _NEUTRAL


def us_unit(cli_unit: str) -> str:
    """The US unit that goes with a command's working unit (same symbol for neutral units)."""
    if cli_unit in _NEUTRAL:
        return cli_unit
    if cli_unit in US_FOR:
        return US_FOR[cli_unit]
    if cli_unit in UNITS:
        return cli_unit                  # no distinct US counterpart defined (kW, W, ...)
    raise UnitError(f"no unit information for {cli_unit!r}")


def to_cli(value: float, cli_unit: str, system: str) -> float:
    """Value typed in `system` for an argument whose working unit is `cli_unit` -> the working unit."""
    if system == "si" or cli_unit in _NEUTRAL:
        return value
    u = us_unit(cli_unit)
    return value if u == cli_unit else convert(value, u, cli_unit)


def from_cli(value: float, cli_unit: str, system: str) -> float:
    if system == "si" or cli_unit in _NEUTRAL:
        return value
    u = us_unit(cli_unit)
    return value if u == cli_unit else convert(value, cli_unit, u)


def display_unit(cli_unit: str, system: str) -> str:
    return cli_unit if system == "si" else us_unit(cli_unit)


# ---- output keys: a trailing unit token on a result key gets a US sibling -----------------------------------------------------
# longest suffix first. P_kPa style keys are taken as ABSOLUTE (the repo uses kPag for gauge); degC keys are not present in results.
_KEY_UNITS = [
    ("_kg_m2_s", "kg/m2/s", "lb/ft2/s", 1 / (LB_KG / FOOT_M ** 2), "_lb_ft2_s"),
    ("_kW_m2", "kW/m2", "Btu/h/ft2", None, "_Btu_h_ft2"),
    ("_kg_m3", "kg/m3", "lb/ft3", None, "_lb_ft3"),
    ("_kJ_kg", "kJ/kg", "Btu/lb", None, "_Btu_lb"),
    ("_m3_h", "m3/h", "gpm", None, "_gpm"),
    ("_kg_s", "kg/s", "lb/s", None, "_lb_s"),
    ("_kg_h", "kg/h", "lb/h", None, "_lb_h"),
    ("_mm2", "mm2", "in2", None, "_in2"),
    ("_kPag", "kPag", "psig", None, "_psig"),
    ("_kpag", "kPag", "psig", None, "_psig"),
    ("_kPa", "kPa abs", "psia", None, "_psia"),
    ("_m2", "m2", "ft2", None, "_ft2"),
    ("_m3", "m3", "ft3", None, "_ft3"),
    ("_mm", "mm", "in", None, "_in"),
    ("_kg", "kg", "lb", None, "_lb"),
    ("_K", "K", "degF", None, "_F"),
    ("_m", "m", "ft", None, "_ft"),
]


def _convert_key(key: str, value: float):
    for suffix, si, us, _, new in _KEY_UNITS:
        if key.endswith(suffix):
            if suffix == "_kg_m2_s":
                return key[: -len(suffix)] + new, value / (LB_KG / FOOT_M ** 2)
            return key[: -len(suffix)] + new, convert(value, si, us)
    return None


def add_us_keys(obj):
    """Return `obj` with a US-unit sibling for every numeric result whose key ends in a recognised unit token."""
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            out[k] = add_us_keys(v)
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                c = _convert_key(k, v)
                if c and c[0] not in obj:
                    out[c[0]] = c[1]
        return out
    if isinstance(obj, list):
        return [add_us_keys(v) for v in obj]
    return obj


# ---- active system for the CLI -----------------------------------------------------------------------------------------------
_active = {"system": "si"}


def set_system(system: str) -> None:
    if system not in SYSTEMS:
        raise UnitError(f"units must be one of {SYSTEMS}")
    _active["system"] = system


def active_system() -> str:
    return _active["system"]

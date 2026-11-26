"""Leak (loss of containment) frequencies for process equipment by hole size, from IOGP Report 434-01 "Risk Assessment Data Directory: Process Release Frequencies"
(September 2019, version 1.1 of May 2021), datasheets (1) to (20) of section 2.2, read from the owner-supplied PDF.

Data are the UK HSE Hydrocarbon Release Database as analysed by the report: topsides of offshore installations, said to be applicable to onshore facilities handling hydrocarbons,
with the report's advice to check the overall frequency against the installation's own record (section 1.3). Two periods are given: 2006-2015 (the recommended set) and 1992-2015.

Frequency of a release exceeding hole diameter d (mm), per equipment-year (per metre-year for pipes):  F(d) = C d^m + B for 1 mm < d <= D, and 0 for d > D, where D is the
equipment size (mm). For pipes, flanged joints, manual and actuated valves the parameters C, m, B depend on D by linear interpolation between the three equipment diameters tabulated
(values above 508 mm use the 508 mm column); for the other equipment the report gives one power law F(d) = a d^b (plus a constant for a few).
Hole classes [lo, hi): 1-3, 3-10, 10-50, 50-150 and above 150 mm; the frequency of a class is F(lo) - F(hi), with F(hi) = 0 when hi exceeds D, so the full-bore hole (d = D) falls in
the class whose lower limit is not above D. The report recommends the geometric mean of a class as the representative hole size (22.4 mm for 10-50 mm), limited to the equipment size
for the top class (section 2.1.2).

Verification: the report's own tabulations (every class, six equipment sizes, both periods, sheets 1 to 7) are reproduced by these equations within the 2-figure rounding the report uses,
except two cells noted in the tests. Not included: sheet 6 for 1992-2015 (the report prints the instrument-connection equation under the vessel heading; its table disagrees with it),
flexible piping (sheet 17: its 1992-2015 table disagrees with its equation), xmas trees, turbines, pipeline ESDVs and SSIV assemblies (sheets 21 to 24). Leak frequencies only: the report
excludes releases at zero pressure, gives no catastrophic vessel failure (section 2.2, sheet 6), and for LNG facilities and inter-unit pipework see its sections 2.3 and 3.3.
Screening aid, not certified design.
"""
from __future__ import annotations

import math

HOLE_CLASSES = ((1.0, 3.0), (3.0, 10.0), (10.0, 50.0), (50.0, 150.0), (150.0, None))
PERIODS = ("2006-2015", "1992-2015")

# sized equipment: (equipment diameters, C, m, B) at the tabulated diameters (mm)
SIZED = {
    1: {"name": "Steel process pipes", "unit": "per metre year",
        "2006-2015": ((0, 170, 508), (2.99e-5, 1.39e-5, 1.87e-5), (-0.798, -0.872, -0.482), (0.0, 0.0, 6.69e-8)),
        "1992-2015": ((0, 170, 508), (7.65e-5, 2.09e-5, 1.68e-5), (-0.798, -0.872, -0.482), (0.0, 0.0, 7.12e-8))},
    2: {"name": "Flanged joints", "unit": "per flanged joint year",
        "2006-2015": ((0, 174, 508), (5.37e-6, 1.31e-5, 3.10e-5), (-0.775, -0.790, -1.071), (-1.40e-7, 4.00e-7, 2.05e-6)),
        "1992-2015": ((0, 174, 508), (1.64e-5, 4.00e-5, 9.48e-5), (-0.775, -0.790, -1.071), (-4.27e-7, 1.22e-6, 6.26e-6))},
    3: {"name": "Manual valves", "unit": "per valve year",
        "2006-2015": ((0, 165, 508), (3.01e-5, 3.06e-5, 9.38e-5), (-0.557, -0.765, -0.524), (0.0, 0.0, 4.41e-7)),
        "1992-2015": ((0, 165, 508), (4.90e-5, 4.99e-5, 1.53e-4), (-0.557, -0.765, -0.524), (0.0, 0.0, 7.18e-7))},
    4: {"name": "Actuated valves", "unit": "per valve year",
        "2006-2015": ((0, 172, 508), (2.79e-4, 1.23e-4, 1.37e-4), (-0.957, -0.718, -0.912), (-9.89e-8, 2.90e-7, 0.0)),
        "1992-2015": ((0, 172, 508), (4.67e-4, 2.06e-4, 2.29e-4), (-0.957, -0.718, -0.912), (-1.66e-7, 4.87e-7, 0.0))},
}

# size-independent power laws F(d) = a d^b + c
POWER = {
    5: {"name": 'Instrument connections', "unit": 'per connection year',
        '2006-2015': (0.000199, -0.87, 0.0),
        '1992-2015': (0.000341, -0.87, 0.0),
    },
    6: {"name": 'Process (pressure) vessels', "unit": 'per vessel year',
        '2006-2015': (0.00065, -0.66, 0.0),
    },
    7: {"name": 'Pumps: centrifugal', "unit": 'per pump year',
        '2006-2015': (0.0035, -1.35, 0.0),
        '1992-2015': (0.00768, -1.35, 0.0),
    },
    8: {"name": 'Pumps: reciprocating', "unit": 'per pump year',
        '1992-2015': (0.00222, -0.41, 0.0),
    },
    9: {"name": 'Compressors: centrifugal', "unit": 'per compressor year',
        '2006-2015': (0.0058, -0.8, 0.0),
        '1992-2015': (0.00627, -0.8, 0.0),
    },
    10: {"name": 'Compressors: reciprocating', "unit": 'per compressor year',
        '2006-2015': (0.0119, -0.78, 0.0),
        '1992-2015': (0.0273, -0.78, 0.0),
    },
    11: {"name": 'Heat exchangers: shell and tube, shell side HC', "unit": 'per exchanger year',
        '2006-2015': (0.00164, -0.72, 0.0),
        '1992-2015': (0.00227, -0.72, 0.0),
    },
    12: {"name": 'Heat exchangers: shell and tube, tube side HC', "unit": 'per exchanger year',
        '2006-2015': (0.000883, -0.53, 0.0),
        '1992-2015': (0.00109, -0.53, 0.0),
    },
    13: {"name": 'Heat exchangers: plate', "unit": 'per exchanger year',
        '2006-2015': (0.00842, -0.99, 0.0),
        '1992-2015': (0.0102, -0.99, 0.0),
    },
    14: {"name": 'Heat exchangers: air-cooled', "unit": 'per exchanger year',
        '1992-2015': (0.00134, -0.993, 0.0),
    },
    15: {"name": 'Filters', "unit": 'per filter year',
        '2006-2015': (0.00186, -0.988, 0.0),
        '1992-2015': (0.00353, -0.988, 0.0),
    },
    16: {"name": 'Pig traps', "unit": 'per pig trap year',
        '2006-2015': (0.0028, -0.648, 0.0),
        '1992-2015': (0.00363, -0.648, 0.0),
    },
    18: {"name": 'Process (pressure) vessels, other', "unit": 'per vessel year',
        '2006-2015': (0.00409, -0.51, 0.0),
        '1992-2015': (0.00438, -0.51, 0.0),
    },
    19: {"name": 'Degassers', "unit": 'per degasser year',
        '1992-2015': (0.00214, -0.474, 0.0),
    },
    20: {"name": 'Expanders', "unit": 'per expander year',
        '1992-2015': (0.00388, -0.8, 0.0),
    },
}


def equipment_types() -> dict[int, str]:
    out = {n: v["name"] for n, v in SIZED.items()}
    out.update({n: v["name"] for n, v in POWER.items()})
    return dict(sorted(out.items()))


def _interp(D, anchors, values):
    if D >= anchors[-1]:
        return values[-1]
    for i in range(len(anchors) - 1):
        if anchors[i] <= D <= anchors[i + 1]:
            return values[i] + (values[i + 1] - values[i]) * (D - anchors[i]) / (anchors[i + 1] - anchors[i])
    raise ValueError("equipment size out of range")


def _check(sheet: int, period: str):
    if period not in PERIODS:
        raise ValueError(f"period must be one of {PERIODS}")
    if sheet in SIZED:
        if period not in SIZED[sheet]:
            raise ValueError(f"no {period} data for sheet {sheet}")
        return "sized", SIZED[sheet]
    if sheet in POWER:
        if period not in POWER[sheet]:
            raise ValueError(f"the report gives sheet {sheet} ({POWER[sheet]['name']}) only for the periods {[p for p in PERIODS if p in POWER[sheet]]}")
        return "power", POWER[sheet]
    raise ValueError(f"sheet {sheet} is not implemented; available: {sorted(equipment_types())}")


def exceedance(sheet: int, D_mm: float, hole_mm: float, period: str = "2006-2015") -> float:
    """F(d): frequency per equipment year of a release with hole diameter above `hole_mm`; zero above the equipment size D."""
    if not (D_mm > 0 and hole_mm > 0):
        raise ValueError("equipment size and hole diameter must be positive")
    kind, d = _check(sheet, period)
    if hole_mm > D_mm:
        return 0.0
    if kind == "sized":
        anchors, C, m, B = d[period]
        return _interp(D_mm, anchors, C) * hole_mm ** _interp(D_mm, anchors, m) + _interp(D_mm, anchors, B)
    a, b, c = d[period]
    return a * hole_mm ** b + c


def class_frequencies(sheet: int, D_mm: float, period: str = "2006-2015") -> list[float]:
    """Frequencies per equipment year for the five hole classes (1-3, 3-10, 10-50, 50-150, >150 mm); a class whose lower limit exceeds D is zero."""
    out = []
    for lo, hi in HOLE_CLASSES:
        if lo > D_mm:
            out.append(0.0)
            continue
        f_lo = exceedance(sheet, D_mm, max(lo, 1.0 + 1e-9), period)
        f_hi = 0.0 if hi is None else exceedance(sheet, D_mm, hi, period)
        out.append(f_lo - f_hi)
    return out


def total_frequency(sheet: int, D_mm: float, period: str = "2006-2015") -> float:
    """Total leak frequency above 1 mm per equipment year: the sum of the class frequencies, which equals F(1 mm)."""
    return sum(class_frequencies(sheet, D_mm, period))


def hole_class(hole_mm: float) -> int:
    """Index (0 to 4) of the hole class containing a hole of this diameter."""
    if hole_mm < 1.0:
        raise ValueError("the report covers holes of 1 mm and above")
    for i, (lo, hi) in enumerate(HOLE_CLASSES):
        if hi is None or hole_mm < hi:
            return i
    raise ValueError("unreachable")


def representative_hole_mm(class_index: int, D_mm: float) -> float:
    """Geometric mean of the class limits (the report's recommendation); the top class takes the equipment size D."""
    lo, hi = HOLE_CLASSES[class_index]
    if hi is None:
        return D_mm
    return min(math.sqrt(lo * hi), D_mm)


def leak_frequency(sheet: int, D_mm: float, count: float = 1.0, period: str = "2006-2015") -> list[dict]:
    """Per-class leak frequencies for `count` equipment items (or metres of pipe), with the representative hole size of each class."""
    if not count > 0:
        raise ValueError("count must be positive")
    freqs = class_frequencies(sheet, D_mm, period)
    return [{"hole_range_mm": (lo, hi), "representative_hole_mm": representative_hole_mm(i, D_mm), "frequency_per_year": f * count}
            for i, ((lo, hi), f) in enumerate(zip(HOLE_CLASSES, freqs)) if f > 0]

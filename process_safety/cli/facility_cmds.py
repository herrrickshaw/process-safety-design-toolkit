"""Facility design checks: escape time and illumination."""
from __future__ import annotations

from .. import egress, illumination
from .registry import command, emit


@command("egress", "escape time check: RSET (detection + pre-movement + travel or exit flow) against an ASET you supply")
class Egress:
    ranges = {"distance": "length_m", "speed": "walking_speed_m_s", "width": "length_m", "specific_flow": "specific_flow",
              "detect_s": "time_nonneg_s", "premove_s": "time_nonneg_s", "aset_s": "time_s"}

    @staticmethod
    def add_arguments(e):
        e.add_argument("--distance", type=float, required=True, help="travel distance to a place of safety, m")
        e.add_argument("--speed", type=float, required=True, help="walking speed, m/s (from the study basis, no default)")
        e.add_argument("--people", type=int, required=True)
        e.add_argument("--width", type=float, required=True, help="effective width of the narrowest exit, m")
        e.add_argument("--specific-flow", type=float, required=True, help="persons per metre of width per second (no default)")
        e.add_argument("--detect-s", type=float, required=True, help="time to detect and raise the alarm, s")
        e.add_argument("--premove-s", type=float, required=True, help="recognition and response time before moving, s")
        e.add_argument("--aset-s", type=float, help="available safe egress time from the fire or toxic study, s (adds the margin)")

    @staticmethod
    def run(a, p):
        try:
            r = egress.rset_s(a.distance, a.speed, a.people, a.width, a.specific_flow, a.detect_s, a.premove_s)
            if a.aset_s is not None:
                r.update(egress.margin(r["rset_s"], a.aset_s))
        except ValueError as e:
            p.error(str(e))
        emit(r)


@command("illumination", "lumen-method average illuminance: luminaires needed for a target, or the lux of a given count")
class Illumination:
    ranges = {"area": "area_m2", "flux": "luminous_flux_lm", "uf": "coefficient_0_1", "mf": "coefficient_0_1", "target": "illuminance_lux"}

    @staticmethod
    def add_arguments(i):
        i.add_argument("--area", type=float, required=True, help="floor area, m2")
        i.add_argument("--flux", type=float, required=True, help="lumens per luminaire (datasheet)")
        i.add_argument("--uf", type=float, required=True, help="utilisation factor from the photometric table")
        i.add_argument("--mf", type=float, required=True, help="maintenance factor")
        i.add_argument("--target", type=float, help="target illuminance, lux: give the luminaires needed")
        i.add_argument("--count", type=int, help="existing luminaire count: give the lux achieved")

    @staticmethod
    def run(a, p):
        if (a.target is None) == (a.count is None):
            p.error("give exactly one of --target or --count")
        try:
            if a.target is not None:
                emit(illumination.luminaires_needed(a.target, a.flux, a.uf, a.mf, a.area))
            else:
                emit({"achieved_lux": illumination.average_lux(a.count, a.flux, a.uf, a.mf, a.area)})
        except ValueError as e:
            p.error(str(e))

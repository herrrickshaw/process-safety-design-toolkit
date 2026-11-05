"""Fire, explosion and dispersion commands."""
from __future__ import annotations

from .. import dispersion, fireball, pool_fire, structural_fire, vapour_fire, viewfactor
from .registry import command, emit


@command("vapour-fire", "transient vapour-filled vessel fire: PSV vs rupture vs blowdown")
class VapourFire:
    ranges = {"volume": "volume_m3", "area": "area_m2", "D": "length_m", "wall_mm": "wall_mm", "M": "molar_mass_kg_kmol",
              "k": "heat_capacity_ratio", "q": "heat_flux_kW_m2", "psv_area": "area_mm2", "bdv_area": "area_mm2",
              "bdv_open_s": "time_nonneg_s", "t_end": "time_s", "psv_set_g": "set_pressure_kPag"}

    @staticmethod
    def add_arguments(vf):
        for n in ("volume", "area", "D", "wall-mm", "M", "k", "p0-g"):
            vf.add_argument("--" + n, type=float, required=True)
        vf.add_argument("--q", type=float, default=100.0, help="absorbed flux kW/m2 (pool ~100, jet ~250: verify)")
        vf.add_argument("--psv-area", type=float, default=0.0, help="mm2"); vf.add_argument("--psv-set-g", type=float)
        vf.add_argument("--bdv-area", type=float, default=0.0, help="mm2"); vf.add_argument("--bdv-open-s", type=float, default=900.0)
        vf.add_argument("--strength", type=float, default=260.0, help="MPa (min yield; conservative)")
        vf.add_argument("--h-in", type=float, default=20.0); vf.add_argument("--t-end", type=float, default=3600.0)

    @staticmethod
    def run(a, p):
        v = vapour_fire.Vessel(a.volume, a.area, a.D, a.wall_mm, a.M, a.k, a.p0_g, strength_MPa=a.strength)
        emit(vapour_fire.simulate(v, a.q, a.psv_area, a.psv_set_g, bdv_area_mm2=a.bdv_area, bdv_open_s=a.bdv_open_s,
                                  h_in=a.h_in, t_end_s=a.t_end))


@command("plume", "Gaussian plume screening (neutral gas): max ground conc and distance to a threshold")
class Plume:
    ranges = {"Q": "release_rate_g_s", "u": "wind_speed_m_s", "H": "nonneg_length_m", "threshold_ppm": "concentration_ppm", "M": "molar_mass_kg_kmol"}

    @staticmethod
    def add_arguments(pl):
        pl.add_argument("--Q", type=float, required=True, help="release g/s"); pl.add_argument("--u", type=float, default=3.0)
        pl.add_argument("--H", type=float, default=0.0, help="effective release height m"); pl.add_argument("--stability", default="D")
        pl.add_argument("--threshold-ppm", type=float); pl.add_argument("--M", type=float, help="molar mass for ppm conversion")

    @staticmethod
    def run(a, p):
        c, x = dispersion.max_ground_concentration(a.Q, a.u, a.H, a.stability)
        out = {"max_ground_conc_g_m3": c, "at_distance_m": x}
        if a.M:
            out["max_ground_conc_ppm"] = dispersion.mg_m3_to_ppm(c * 1000, a.M)
        if a.threshold_ppm and a.M:
            out["farthest_distance_above_threshold_m"] = dispersion.distance_to_threshold_m(
                a.Q, a.u, a.H, dispersion.ppm_to_mg_m3(a.threshold_ppm, a.M) / 1000, a.stability)
        out["warning"] = "neutral-buoyancy screening only; dense gases need a dense-gas model"
        emit(out)


@command("pool-fire", "pool fire burn rate, flame height, distances to radiation levels")
class PoolFire:
    ranges = {"area": "area_m2", "hc": "heat_of_combustion_kJ_kg", "hv": "latent_heat_kJ_kg", "cp": "specific_heat_kJ_kgK",
              "tb": "temperature_K", "fraction": "fraction_0_1"}

    @staticmethod
    def add_arguments(pf):
        for n in ("area", "hc", "hv", "cp", "tb"):
            pf.add_argument("--" + n, type=float, required=True)
        pf.add_argument("--fraction", type=float, default=0.25)

    @staticmethod
    def run(a, p):
        r = pool_fire.pool_fire(a.area, a.hc, a.hv, a.cp, a.tb, radiant_fraction=a.fraction)
        r["distance_m"] = {str(q): round(pool_fire.distance_to_flux_m(r, q), 1) for q in (37.5, 12.5, 4.73, 1.58)}
        r["note"] = "point-source: unreliable inside ~2 pool diameters; no wind tilt"
        emit(r)


@command("steel-fire", "steel temperature vs time in a hydrocarbon fire; time to critical temperature")
class SteelFire:
    ranges = {"am_v": "section_factor_1_m", "crit": "temperature_C", "minutes": "time_min"}

    @staticmethod
    def add_arguments(sf):
        sf.add_argument("--am-v", type=float, required=True, help="section factor Am/V 1/m"); sf.add_argument("--crit", type=float, default=550.0)
        sf.add_argument("--minutes", type=float, default=120.0)
        sf.add_argument("--iso", action="store_true", help="use ISO 834 instead of the hydrocarbon curve")

    @staticmethod
    def run(a, p):
        h = structural_fire.steel_temperature_history(a.am_v, structural_fire.iso834_C if a.iso else structural_fire.hydrocarbon_C,
                                                      t_end_min=a.minutes)
        emit({"time_to_critical_min": structural_fire.time_to_critical_min(h, a.crit), "critical_C": a.crit,
              "steel_C_at": {str(t): round(T) for t, T in h if t in (5, 10, 15, 30, 60, 120)}})


@command("fireball")
class Fireball:
    ranges = {"mass": "mass_kg", "hc": "heat_of_combustion_MJ_kg", "fraction": "fraction_0_1"}

    @staticmethod
    def add_arguments(fb):
        fb.add_argument("--mass", type=float, required=True, help="kg")
        fb.add_argument("--hc", type=float, required=True, help="MJ/kg")
        fb.add_argument("--fraction", type=float, default=0.3)

    @staticmethod
    def run(a, p):
        b = fireball.fireball(a.mass, a.hc, a.fraction)
        emit({**b, "distance_to_kW_m2": {str(k): fireball.distance_to_flux_m(b, k) for k in (37.5, 12.5, 4.0)}})


@command("flame-flux", "solid-flame view-factor radiation to a target facing a vertical rectangular flame (near-field)")
class FlameFlux:
    ranges = {"width": "length_m", "height": "length_m", "distance": "length_m", "base": "nonneg_length_m",
              "sep": "emissive_power_kW_m2", "tau": "coefficient_0_1"}

    @staticmethod
    def add_arguments(ff):
        ff.add_argument("--width", type=float, required=True, help="flame face width m"); ff.add_argument("--height", type=float, required=True, help="flame face height m")
        ff.add_argument("--distance", type=float, required=True, help="target to flame plane, m")
        ff.add_argument("--offset", type=float, default=0.0, help="lateral offset of the flame centre from the target, m")
        ff.add_argument("--base", type=float, default=0.0, help="flame base height above the target, m")
        ff.add_argument("--sep", type=float, required=True, help="surface emissive power kW/m2 (e.g. from pool-fire)")
        ff.add_argument("--tau", type=float, default=1.0); ff.add_argument("--n", type=int, default=200, help="integration cells per side")

    @staticmethod
    def run(a, p):
        face = viewfactor.vertical_flame_face(a.width, a.height, a.distance, a.offset, a.base)
        r = viewfactor.flux_from_faces((-a.distance, 0.0, 0.0), (1.0, 0.0, 0.0), [face], a.sep, a.tau, a.n)
        r["note"] = "flat vertical face, target facing it, no tilt or blockage; compare with pool-fire point-source distances"
        emit(r)

"""Electrical, mechanical and exposure commands."""
from __future__ import annotations

from .. import datacentre, electrical, mechanical_safety, noise
from .registry import command, emit


@command("arc-flash", "Lee-method incident energy and boundary (open-air 3-phase; OSHA applicability limits enforced)")
class ArcFlash:
    ranges = {"kv": "voltage_kV", "ka": "current_kA", "t": "time_s", "dist_mm": "distance_mm"}

    @staticmethod
    def add_arguments(af):
        af.add_argument("--kv", type=float, required=True); af.add_argument("--ka", type=float, required=True); af.add_argument("--t", type=float, required=True)
        af.add_argument("--dist-mm", type=float, required=True); af.add_argument("--phases", type=int, default=3); af.add_argument("--enclosed", action="store_true")

    @staticmethod
    def run(a, p):
        ok = electrical.lee_applicable(a.kv * 1000, a.phases, a.enclosed)
        out = {"applicability": ok}
        if ok["ok"]:
            E = electrical.lee_incident_energy_J_cm2(a.kv, a.ka, a.t, a.dist_mm)
            out.update({"incident_energy_J_cm2": E, "incident_energy_cal_cm2": E * electrical.CAL_PER_J,
                        "boundary_mm_second_degree_burn": electrical.lee_boundary_mm(a.kv, a.ka, a.t), "note": "screening; arc-flash study per IEEE 1584 for enclosed equipment"})
        emit(out)


@command("idmt", "IEC 60255 inverse-time overcurrent relay operating time")
class Idmt:
    ranges = {"i": "current_A", "pickup": "current_A", "tms": "relay_tms"}

    @staticmethod
    def add_arguments(im):
        im.add_argument("--i", type=float, required=True, help="fault current A"); im.add_argument("--pickup", type=float, required=True); im.add_argument("--tms", type=float, required=True)
        im.add_argument("--curve", default="standard_inverse", choices=list(electrical.IDMT))

    @staticmethod
    def run(a, p):
        emit({"operating_time_s": electrical.idmt_time_s(a.i, a.pickup, a.tms, a.curve), "multiple_of_pickup": a.i / a.pickup})


@command("noise", "OSHA noise dose and TWA; items LEVEL_dBA:HOURS")
class Noise:
    @staticmethod
    def add_arguments(nz):
        nz.add_argument("items", nargs="+")

    @staticmethod
    def run(a, p):
        from .. import ranges
        ex = [(float(x.split(":")[0]), float(x.split(":")[1])) for x in a.items]
        for lvl, hrs in ex:
            for w in ranges.check("sound_level_dBA", lvl, "level") + ranges.check("exposure_hours", hrs, "hours"):
                import sys
                print("warning: " + w, file=sys.stderr)
        d = noise.dose_pct(ex)
        emit({"dose_pct": d, "twa_dBA": noise.twa_dBA(d), "exceeds_pel": d > 100, "above_action_level": d >= 50, "basis": "OSHA 1910.95 Table G-16 / App. A"})


@command("safeguard", "ISO 13855 (pre-2024 form) minimum distance for an electro-sensitive protective device")
class Safeguard:
    ranges = {"stop_s": "time_s", "d_mm": "distance_mm"}

    @staticmethod
    def add_arguments(sg):
        sg.add_argument("--stop-s", type=float, required=True, help="total stopping time incl. response, s"); sg.add_argument("--d-mm", type=float, required=True, help="detection capability mm")

    @staticmethod
    def run(a, p):
        emit({"min_distance_mm": mechanical_safety.safeguard_distance_mm(a.stop_s, a.d_mm), "note": "pre-2024 ISO 13855 form; confirm the edition your project cites"})


@command("earthing", "IEEE 80 tolerable touch and step voltages (50 and 70 kg)")
class Earthing:
    ranges = {"rho_s": "resistivity_ohm_m", "t": "time_s", "rho": "resistivity_ohm_m", "hs": "length_m"}

    @staticmethod
    def add_arguments(er):
        er.add_argument("--rho-s", type=float, required=True, help="surface layer resistivity ohm-m"); er.add_argument("--t", type=float, required=True, help="fault duration s")
        er.add_argument("--rho", type=float, help="underlying soil resistivity (with --hs for the Cs derating)"); er.add_argument("--hs", type=float, help="surface layer thickness m")

    @staticmethod
    def run(a, p):
        Cs = electrical.surface_layer_factor(a.rho, a.rho_s, a.hs) if a.rho and a.hs else 1.0
        emit({"Cs": Cs, "touch_V_50kg": electrical.tolerable_touch_V(a.rho_s, a.t, Cs, 50), "step_V_50kg": electrical.tolerable_step_V(a.rho_s, a.t, Cs, 50),
              "touch_V_70kg": electrical.tolerable_touch_V(a.rho_s, a.t, Cs, 70), "step_V_70kg": electrical.tolerable_step_V(a.rho_s, a.t, Cs, 70)})


@command("datacentre", "data-centre screening: PUE, cooling-water flow, UPS battery energy, diesel storage (supply only the inputs you have)")
class Datacentre:
    ranges = {"it_kw": "power_kW", "facility_kw": "power_kW", "delta_t": "temperature_rise_K", "heat_kw": "power_kW",
              "battery_eff": "coefficient_0_1", "battery_dod": "coefficient_0_1", "gen_load_kw": "power_kW", "sfc": "fuel_consumption_g_kWh"}

    @staticmethod
    def add_arguments(dcp):
        dcp.add_argument("--it-kw", type=float, required=True); dcp.add_argument("--facility-kw", type=float); dcp.add_argument("--delta-t", type=float, help="cooling water dT, K")
        dcp.add_argument("--heat-kw", type=float, help="heat to remove (default: IT load)"); dcp.add_argument("--autonomy-min", type=float)
        dcp.add_argument("--battery-eff", type=float, default=0.95); dcp.add_argument("--battery-dod", type=float, default=0.8)
        dcp.add_argument("--gen-hours", type=float); dcp.add_argument("--gen-load-kw", type=float); dcp.add_argument("--sfc", type=float, help="specific fuel consumption, g/kWh (vendor data)")

    @staticmethod
    def run(a, p):
        if a.gen_hours is not None and not a.sfc:
            p.error("--gen-hours needs --sfc (vendor data, no default)")
        emit(datacentre.summary(a.it_kw, a.facility_kw, a.delta_t, a.heat_kw, a.autonomy_min, a.battery_eff, a.battery_dod, a.gen_load_kw, a.gen_hours, a.sfc))

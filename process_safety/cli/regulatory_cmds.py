"""Regulatory screening: PSM, Seveso, RMP, pipeline, LNG, LPG."""
from __future__ import annotations

import datetime as _dt

from .. import lng, lpg, mah, pipeline, plant_units, props, psm, rmp
from .registry import command, emit


@command("psm-check", "OSHA PSM applicability: Appendix A chemical or the 10,000 lb flammables rule")
class PsmCheck:
    ranges = {"kg": "mass_kg"}

    @staticmethod
    def add_arguments(pc):
        pc.add_argument("--chemical", help="name or CAS"); pc.add_argument("--kg", type=float, required=True)
        pc.add_argument("--flammable", action="store_true"); pc.add_argument("--workplace-fuel", action="store_true"); pc.add_argument("--atmospheric-below-bp", action="store_true")

    @staticmethod
    def run(a, p):
        if a.flammable:
            emit(psm.covered_flammable(a.kg, workplace_fuel_only=a.workplace_fuel, atmospheric_tank_below_boiling_point=a.atmospheric_below_bp))
        else:
            emit(psm.covered_chemical(a.chemical, a.kg))


@command("psm-due", "next due dates (ISO dates) for PHA revalidation, procedure certification, refresher training, compliance audit")
class PsmDue:
    @staticmethod
    def add_arguments(pd):
        for n in ("pha", "procedures", "training", "audit"):
            pd.add_argument("--" + n, help="last done YYYY-MM-DD")
        pd.add_argument("--today")

    @staticmethod
    def run(a, p):
        last = {k: _dt.date.fromisoformat(v) for k, v in (("pha_revalidation", a.pha), ("operating_procedure_certification", a.procedures),
                                                          ("refresher_training", a.training), ("compliance_audit", a.audit)) if v}
        emit(psm.due_dates(last, _dt.date.fromisoformat(a.today) if a.today else None))


@command("seveso", "Seveso III sum-rule tier; items as KEY=tonnes, KEY=P2 (category) or Name:H=tonnes (substance:group)")
class Seveso:
    @staticmethod
    def add_arguments(sv):
        sv.add_argument("items", nargs="+")

    @staticmethod
    def run(a, p):
        inv = []
        for it in a.items:
            key, val = it.split("=", 1)
            if ":" in key:
                name, grp = key.split(":"); inv.append({"substance": name, "group": grp, "tonnes": float(val)})
            else:
                inv.append({"category": key, "tonnes": float(val)})
        r = mah.classify(inv)
        emit({"tier": r["tier"], "sums": {g: {"lower": round(v["lower"], 3), "upper": round(v["upper"], 3)} for g, v in r["sums"].items() if v["items"]},
              "note": "Seveso III Annex I, 2012 text; MSIHC 1989 schedules not reproduced"})


@command("pipeline", "49 CFR 192 design pressure and potential impact radius (natural gas)")
class Pipeline:
    units = {"joint": "-"}
    ranges = {"smys": "smys_MPa", "wall": "wall_mm", "od": "diameter_mm", "temp": "temperature_C"}

    @staticmethod
    def add_arguments(pp):
        for n in ("smys", "wall", "od"):
            pp.add_argument("--" + n, type=float, required=True, help={"smys": "MPa", "wall": "mm", "od": "mm"}[n])
        pp.add_argument("--class-location", type=int, default=1); pp.add_argument("--joint", type=float, default=1.0)
        pp.add_argument("--temp", type=float, default=20.0); pp.add_argument("--buildings", type=int, default=0)

    @staticmethod
    def run(a, p):
        P = pipeline.design_pressure_kpa(a.smys, a.wall, a.od, a.class_location, a.joint, a.temp)
        r = pipeline.potential_impact_radius_m(P, a.od)
        emit({"design_pressure_kPag": P, "design_pressure_bar": P / 100, "potential_impact_radius_m_natural_gas_at_that_pressure": r,
              "hca_criterion_iii": pipeline.hca_by_pir(r, a.buildings, a.class_location), "note": "49 CFR 192 basis (US), natural gas only"})


@command("rmp-check", "EPA RMP (40 CFR 68) threshold check for a regulated toxic/flammable substance")
class RmpCheck:
    ranges = {"kg": "mass_kg", "weight_fraction": "coefficient_0_1"}

    @staticmethod
    def add_arguments(rc):
        rc.add_argument("substance"); rc.add_argument("--kg", type=float, required=True); rc.add_argument("--weight-fraction", type=float, default=1.0)

    @staticmethod
    def run(a, p):
        emit(rmp.threshold_check(a.substance, a.kg, a.weight_fraction))


@command("rmp-worst", "RMP worst-case criteria: toxic gas (10 min, 1.5 m/s, F) or flammable VCE (10%% yield, 1 psi)")
class RmpWorst:
    ranges = {"kg": "mass_kg", "hc": "heat_of_combustion_MJ_kg"}

    @staticmethod
    def add_arguments(rw):
        rw.add_argument("substance"); rw.add_argument("--kg", type=float, required=True)
        rw.add_argument("--hc", type=float, help="heat of combustion MJ/kg (flammables)")

    @staticmethod
    def run(a, p):
        f = rmp.find(a.substance)
        if f is None:
            raise SystemExit(f"{a.substance!r} not in the parsed RMP tables")
        emit(rmp.worst_case_toxic_gas(a.substance, a.kg) if f["kind"] == "toxic" else rmp.worst_case_flammable_vce(a.kg, a.hc))


@command("lng", "LNG: impoundment (49 CFR 193.2181), boil-off, regas duty")
class Lng:
    ranges = {"tanks": "volume_m3", "heat_kw": "power_kW", "regas_kg_s": "mass_flow_kg_s", "sw_dT": "temperature_rise_K"}

    @staticmethod
    def add_arguments(lg):
        lg.add_argument("--tanks", type=float, nargs="+", required=True, help="tank capacities m3"); lg.add_argument("--surge", action="store_true")
        lg.add_argument("--heat-kw", type=float, help="heat ingress kW (boil-off)"); lg.add_argument("--regas-kg-s", type=float)
        lg.add_argument("--sw-dT", type=float, default=5.0)

    @staticmethod
    def run(a, p):
        out = {"impoundment_m3": lng.impoundment_capacity_m3(a.tanks, a.surge), "basis": "49 CFR 193.2181"}
        if a.heat_kw:
            out["boil_off_kg_s"] = lng.boil_off_rate_kg_s(a.heat_kw)
            out["boil_off_pct_per_day_largest_tank"] = lng.boil_off_pct_per_day(a.heat_kw, max(a.tanks))
        if a.regas_kg_s:
            d = lng.regas_duty_kW(a.regas_kg_s, 111.66, 283.15)
            out.update({"regas_duty_MW": d / 1000, "seawater_m3_s_open_rack": lng.seawater_flow_m3_s(d, a.sw_dT)})
        emit(out)


@command("lpg", "LPG/hydrocarbon: vapour pressure, density, max fill fraction")
class Lpg:
    ranges = {"fill_C": "temperature_C", "max_C": "temperature_C"}

    @staticmethod
    def add_arguments(lp):
        lp.add_argument("component"); lp.add_argument("--fill-C", type=float, default=15.0); lp.add_argument("--max-C", type=float, default=50.0)

    @staticmethod
    def run(a, p):
        Tf, Tm = a.fill_C + 273.15, a.max_C + 273.15
        emit({"vapour_pressure_kPag_at_max": lpg.vapour_pressure_kPag(a.component, Tm), "liquid_density_kg_m3_at_fill": props.liquid_density_kg_m3(a.component, Tf),
              "max_fill_fraction_thermodynamic_ceiling": lpg.max_fill_fraction(a.component, Tf, Tm), "note": "codes (API 2510, OISD-STD-144/150, IS 2825) set the practical limit"})


@command("h2o2", "hydrogen peroxide decomposition: O2, heat and max steam per hour")
class H2o2:
    ranges = {"kg_h": "mass_flow_kg_h"}

    @staticmethod
    def add_arguments(hp):
        hp.add_argument("--kg-h", type=float, required=True, help="pure H2O2 decomposing, kg/h")

    @staticmethod
    def run(a, p):
        emit(plant_units.h2o2_decomposition(a.kg_h))

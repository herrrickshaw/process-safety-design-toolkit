"""ATEX / hazardous-area support: dust explosion class from KSt, zone from release grade, EPL and ATEX equipment category per
zone, FIBC type screening, and an explosion protection document (EPD) register.

Verified: KSt classes St0 = 0, St1 0-200, St2 200-300, St3 > 300 bar.m/s (several test-lab and OSHA NEP-derived sources).
Standard mappings (well established; check your edition): zone 0/1/2 -> EPL Ga/Gb/Gc and ATEX category 1G/2G/3G; zone 20/21/22 ->
Da/Db/Dc and 1D/2D/3D. Dust grade -> zone (IEC 60079-10-2): continuous 20, primary 21, secondary 22.
Gas grade -> zone depends on ventilation degree and availability (IEC 60079-10-1 Annex D). Only two cases are coded:
medium dilution with good availability (continuous 0, primary 1, secondary 2) and high dilution ("NE", negligible extent);
every other combination returns None - assess it with the standard. Zone EXTENT (distance) is not computed.
FIBC screening (summary of IEC 61340-4-4 practice, not the text): no flammable atmosphere and MIE > 1000 mJ -> A; flammable
vapour/gas present -> C (groundable) or D; dust MIE <= 3 mJ -> C or D; else B. VERIFY with the standard and the supplier.
Dust explosion venting / suppression design is NOT implemented (NFPA 68 / EN 14491 coefficients not verified).
"""
from __future__ import annotations

ZONE_EPL = {0: "Ga", 1: "Gb", 2: "Gc", 20: "Da", 21: "Db", 22: "Dc"}
ZONE_CATEGORY = {0: "1G", 1: "2G", 2: "3G", 20: "1D", 21: "2D", 22: "3D"}
DUST_GRADE_ZONE = {"continuous": 20, "primary": 21, "secondary": 22}
GAS_GRADE_ZONE_MEDIUM_GOOD = {"continuous": 0, "primary": 1, "secondary": 2}


def kst_class(kst_bar_m_s: float) -> str:
    if kst_bar_m_s <= 0:
        return "St0"
    return "St1" if kst_bar_m_s <= 200 else "St2" if kst_bar_m_s <= 300 else "St3"


def zone(substance: str, grade: str, dilution: str = "medium", availability: str = "good"):
    grade = grade.lower()
    if substance == "dust":
        return DUST_GRADE_ZONE[grade]
    if dilution == "high":
        return f"{GAS_GRADE_ZONE_MEDIUM_GOOD[grade]} NE"
    if dilution == "medium" and availability == "good":
        return GAS_GRADE_ZONE_MEDIUM_GOOD[grade]
    return None


def fibc_type(flammable_gas_present: bool, dust_mie_mJ: float | None) -> str:
    if flammable_gas_present:
        return "C (earthed) or D"
    if dust_mie_mJ is not None and dust_mie_mJ <= 3:
        return "C (earthed) or D"
    if dust_mie_mJ is None or dust_mie_mJ > 1000:
        return "A, B, C or D (A only with no flammable atmosphere)"
    return "B, C or D"


def epd_register(areas: list[dict]) -> list[dict]:
    """areas = [{"area", "substance": "gas"|"dust", "material", "grade", "dilution", "availability", "kst", "mie_mJ", "autoignition_C",
                 "gas_group", "ignition_sources": [...]}] -> EPD rows with zone, EPL, category, dust class and open actions."""
    from .electrical import allowed_t_classes
    rows = []
    for a in areas:
        z = a.get("zone") if a.get("zone") is not None else zone(a["substance"], a["grade"], a.get("dilution", "medium"), a.get("availability", "good"))
        zi = int(str(z).split()[0]) if z is not None else None
        rows.append({"area": a["area"], "material": a.get("material", ""), "substance": a["substance"], "release_grade": a.get("grade", ""),
                     "zone": "ASSESS (IEC 60079-10-1 Annex D)" if z is None else z,
                     "EPL": ZONE_EPL.get(zi, "") if zi is not None else "", "ATEX_category": ZONE_CATEGORY.get(zi, "") if zi is not None else "",
                     "dust_class": kst_class(a["kst"]) if a.get("kst") is not None else "",
                     "T_class_allowed": ", ".join(allowed_t_classes(a["autoignition_C"])) if a.get("autoignition_C") and a["substance"] == "gas" else "",
                     "gas_group": a.get("gas_group", ""), "FIBC": fibc_type(a["substance"] == "gas", a.get("mie_mJ")) if a.get("bulk_bags") else "",
                     "ignition_sources_to_control": "; ".join(a.get("ignition_sources", [])), "status": "draft"})
    return rows

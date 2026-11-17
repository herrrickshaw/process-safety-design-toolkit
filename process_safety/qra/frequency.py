"""Step 2 - frequency analysis: parts-count LOC frequencies from a generic dataset, fault-tree initiators, IPL credits, and
Cox-Lees-Ang ignition / explosion probabilities.

Generic data (data/generic_frequencies.json) holds only rows whose values were seen in a public document, each with its source.
Missing equipment (pumps, compressors, flanges, valves) must be given per item ("rows" or "frequency_per_yr") from OGP 434-1, HSE
FRED, the Purple Book or site data. Fault trees reuse reliability.FaultTree: frequency = initiator x P(top).

Cox, Lees & Ang (1990) "Classification of Hazardous Locations" (IChemE), as tabulated by the EU JRC RAPID-N database:
    ignition       gas: <1 kg/s 0.01, 1-50 kg/s 0.07, >50 kg/s 0.30;  liquid: 0.01, 0.03, 0.08
    explosion|ign  0.04, 0.12, 0.30 (gas bands)
They are total (immediate + delayed) probabilities for an onshore process plant. The split between immediate and delayed
ignition is NOT in Cox: it is the study input ignition.immediate_fraction.
"""
from __future__ import annotations

import json
import math
import os

from ..reliability import FaultTree

_DATA = os.path.join(os.path.dirname(__file__), "data", "generic_frequencies.json")

COX_IGNITION = {"gas": (0.01, 0.07, 0.30), "liquid": (0.01, 0.03, 0.08)}
COX_EXPLOSION_GIVEN_IGNITION = (0.04, 0.12, 0.30)


def _band(rate_kg_s: float) -> int:
    return 0 if rate_kg_s < 1 else 1 if rate_kg_s <= 50 else 2


def cox_ignition(rate_kg_s: float, phase: str) -> float:
    """phase 'gas' (also used for flashing liquids whose airborne fraction dominates) or 'liquid'."""
    return COX_IGNITION["gas" if phase == "gas" else "liquid"][_band(rate_kg_s)]


def cox_explosion_given_ignition(rate_kg_s: float) -> float:
    return COX_EXPLOSION_GIVEN_IGNITION[_band(rate_kg_s)]


def load_dataset(extra: dict | str | None = None) -> dict:
    with open(_DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    if extra:
        if isinstance(extra, str):
            with open(extra, encoding="utf-8") as fh:
                extra = json.load(fh)
        data["equipment"].update(extra.get("equipment", {}))
        data["sources"].update(extra.get("sources", {}))
    return data


def hole_diameter_mm(hole: str, item: dict, section: dict) -> float:
    """Map a hole key to a diameter. Item-level 'hole_mm' overrides win (needed for D/3 on vessels and tanks)."""
    ov = item.get("hole_mm", {})
    if hole in ov:
        return float(ov[hole])
    D = item.get("diameter_mm") or section.get("connection_diameter_mm")
    if hole.endswith("mm") and hole[:-2].replace(".", "").isdigit():
        return float(hole[:-2])
    if D is None and hole == "rupture" and item.get("instantaneous_rupture", True):
        return 0.0  # catastrophic vessel/tank rupture: instantaneous, hole size not used
    if D is None:
        raise ValueError(f"hole '{hole}' on {item['type']} needs diameter_mm (item) or connection_diameter_mm (section) or hole_mm")
    if hole == "rupture":
        return float(D)
    if hole == "D/3":
        return D / 3
    if hole == "0.1D_max50":
        return min(0.1 * D, 50.0)
    raise ValueError(f"unknown hole key {hole!r}")


def item_rows(item: dict, dataset: dict) -> tuple[list[dict], str]:
    """Rows for an equipment item: its own 'rows' (study-supplied) or the dataset's, and the multiplier unit."""
    if "rows" in item:
        return item["rows"], item.get("unit", "per_item_yr")
    if "frequency_per_yr" in item:
        return [{"hole": item.get("hole", "rupture"), "freq": item["frequency_per_yr"], "source": item.get("source", "study input")}], "per_item_yr"
    eq = dataset["equipment"].get(item["type"])
    if eq is None:
        raise KeyError(f"equipment type {item['type']!r} has no generic data: give 'rows' or 'frequency_per_yr' for it")
    return eq["rows"], eq["unit"]


def loc_scenarios(section: dict, dataset: dict) -> list[dict]:
    """Parts count: one LOC scenario per (equipment item, hole), frequency = row freq x count (or x length for piping).
    Holes larger than the item's diameter are capped at full bore. Vessel/tank 'rupture' rows are instantaneous releases."""
    out = []
    ff = section.get("frequency_factors", {})
    for k, item in enumerate(section["equipment"]):
        rows, unit = item_rows(item, dataset)
        mult = item.get("length_m", 0) if unit == "per_m_yr" else item.get("count", 1)
        for row in rows:
            d = hole_diameter_mm(row["hole"], item, section)
            if item.get("diameter_mm"):
                d = min(d, item["diameter_mm"])
            inst = row["hole"] == "rupture" and unit == "per_item_yr" and item.get("instantaneous_rupture", True)
            factor = ff.get(row["hole"], 1.0) * ff.get("*", 1.0)
            out.append({"id": f"{section['id']}-{item.get('tag', item['type'])}-{row['hole']}", "section": section["id"],
                        "equipment": item.get("tag", item["type"]), "hole": row["hole"], "hole_mm": d, "instantaneous": inst,
                        "frequency_per_yr": row["freq"] * mult * factor, "base_frequency_per_yr": row["freq"] * mult,
                        "source": row.get("source", "study input"), "basis": f"{row['freq']:.2e} {unit} x {mult}" + (f" x factor {factor:g}" if factor != 1 else "")})
    return out


def fault_tree_frequency(spec: dict) -> tuple[float, dict]:
    """spec = {"initiator_per_yr": f, "basic": {name: p}, "gates": {name: [kind, [inputs], k]}, "top": name}.
    Returns (frequency, details incl. minimal cut sets and Birnbaum importance)."""
    ft = FaultTree()
    for n, p in spec["basic"].items():
        ft.event(n, p)
    for n, g in spec["gates"].items():
        ft.gate(n, g[0], g[1], g[2] if len(g) > 2 else None)
    P = ft.probability(spec["top"])
    return spec.get("initiator_per_yr", 1.0) * P, {"P_top": P, "cut_sets": [sorted(c) for c in ft.minimal_cut_sets(spec["top"])],
                                                   "birnbaum": ft.birnbaum(spec["top"])}


def extra_scenario(spec: dict) -> dict:
    """User-defined scenario (e.g. from HAZOP/LOPA): explicit frequency_per_yr, or a fault_tree; optional ipl_pfds."""
    detail = {}
    if "fault_tree" in spec:
        f, detail = fault_tree_frequency(spec["fault_tree"])
    else:
        f = spec["frequency_per_yr"]
    pfd = math.prod(spec.get("ipl_pfds", []))
    return {"id": spec["id"], "section": spec["section"], "equipment": spec.get("equipment", "user scenario"), "hole": spec.get("hole", "user"),
            "hole_mm": spec["hole_mm"], "instantaneous": spec.get("instantaneous", False), "frequency_per_yr": f * pfd,
            "base_frequency_per_yr": f, "source": spec.get("source", "study input"),
            "basis": ("fault tree" if detail else "explicit") + (f" x IPL PFD {pfd:.1e}" if pfd != 1 else ""), "fault_tree": detail}

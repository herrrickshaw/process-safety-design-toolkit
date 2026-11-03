"""Major-accident-hazard (MAH) establishment classification by the EU Seveso III sum rule (Directive 2012/18/EU, Annex I).

Data: data/seveso_iii_annex_i.json parsed from the official 2012 text (EU Publications Office, CELEX 32012L0018): 21 Part 1 hazard
categories and the Part 2 named substances whose two thresholds parsed cleanly (rows with qualified/unparsed thresholds were
omitted, not guessed). The Annex has since been amended: check the consolidated EUR-Lex text. India's MSIHC Rules 1989 have their own
schedules (not reproduced here; the schedule text was not retrieved). A substance in Part 2 uses the Part 2 quantity rather than its
Part 1 category quantity. The sum rule is applied separately to health (H), physical (P) and environmental (E) groups.
"""
from __future__ import annotations

import json
from importlib import resources


def _data() -> dict:
    return json.loads(resources.files("process_safety").joinpath("data/seveso_iii_annex_i.json").read_text())


def part1() -> dict:
    return _data()["part1"]


def part2() -> list[dict]:
    return _data()["part2"]


def find_substance(name: str) -> dict | None:
    q = name.lower()
    hits = [r for r in part2() if q in r["substance"].lower()]
    return hits[0] if hits else None


def group_of_category(code: str) -> str:
    return code[0]  # H, P or E (O-categories form their own 'other' group and are not summed with them)


def classify(inventory: list[dict]) -> dict:
    """inventory items: {'category': 'P2', 'tonnes': 12} or {'substance': 'Chlorine', 'tonnes': 4, 'group': 'H'}.
    Named substances require an explicit group because the group follows the substance's hazard classification for the case at hand."""
    sums = {g: {"lower": 0.0, "upper": 0.0, "items": []} for g in ("H", "P", "E", "O")}
    for it in inventory:
        if "category" in it:
            c = part1()[it["category"]]
            g, lo, up = group_of_category(it["category"]), c["lower_t"], c["upper_t"]
            label = it["category"]
        else:
            s = find_substance(it["substance"])
            if s is None:
                raise KeyError(f"{it['substance']!r} not in the parsed Part 2 list: use its Part 1 category or add it")
            g, lo, up, label = it["group"], s["lower_t"], s["upper_t"], s["substance"]
        q = it["tonnes"]
        sums[g]["lower"] += q / lo
        sums[g]["upper"] += q / up
        sums[g]["items"].append((label, q, q / lo, q / up))
    tier = "upper-tier" if any(v["upper"] >= 1 for v in sums.values()) else "lower-tier" if any(v["lower"] >= 1 for v in sums.values()) else "below Seveso scope"
    return {"tier": tier, "sums": sums}

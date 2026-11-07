"""Build process_safety/data/lng_analogs.json from the public analog table of ORIMIZ-Consulting/open-fel1-lng-cost (MIT licence).

    python scripts/build_lng_analogs.py /path/to/open-fel1-lng-cost/data/public_analogs.csv [commit]

Keeps onshore liquefaction rows that carry a plant-only figure (the published plant-only amount, or the headline figure where the scope
is plant only). Every row keeps its source URL, scope, cost basis and data quality grade from the original table.
"""
import csv
import json
import os
import sys

src = sys.argv[1]
commit = sys.argv[2] if len(sys.argv) > 2 else "unknown"
out = []
for r in csv.DictReader(open(src, encoding="utf-8")):
    if r["facility_type"] != "onshore_liquefaction":
        continue
    plant = r["plant_only_amount_million"] or (r["cost_amount_million"] if r["scope"] == "plant_only" else "")
    if not plant or r["currency"] != "USD":
        continue
    cap = float(r["capacity_mtpa"])
    trains = int(r["trains"])
    ts = float(r["train_size_mtpa"]) if r["train_size_mtpa"] else cap / trains
    out.append({"id": r["id"], "project": r["project"], "country": r["country"], "location_code": r["location_code"], "site_type": r["site_type"],
                "trains": trains, "capacity_mtpa": cap, "train_size_mtpa": round(ts, 3), "fid_year": int(r["fid_year"]), "cost_year": int(r["cost_year"]),
                "plant_only_musd": float(plant), "headline_musd": float(r["cost_amount_million"]), "scope": r["scope"], "cost_basis": r["cost_basis"],
                "split_source": r["split_source"], "contingency_status": r["contingency_status"], "grade": r["data_quality"], "source_url": r["source_url"]})
doc = {"compiled": "2026-11-06",
       "source": "ORIMIZ-Consulting/open-fel1-lng-cost, data/public_analogs.csv (Haider, S. Z., 2026), commit " + commit,
       "license": "MIT License, Copyright (c) 2026 Syed Zia Haider. Permission notice: https://github.com/ORIMIZ-Consulting/open-fel1-lng-cost/blob/main/LICENSE",
       "note": "Published project costs in the dollars of each row's cost_year, NOT escalated. Most onshore plant-only splits come from OIES NG137 (Songhurst, 2018). Scope and contingency differ between rows: read each source.",
       "analogs": out}
dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "lng_analogs.json")
json.dump(doc, open(dst, "w"), indent=1)
print(len(out), "analogs")

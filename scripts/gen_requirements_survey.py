"""Write docs/PUBLIC_REQUIREMENTS_SURVEY.md (counts only) from one or more private extraction CSVs made by `process_safety requirements`.

    python scripts/gen_requirements_survey.py out1.csv [out2.csv ...]

Only counts and document titles are written; statement text never leaves the CSVs. Titles come from TITLES (matched on file-name text); a file with no
entry is listed under its file name.
"""
import collections
import csv
import os
import re
import sys

TITLES = {
    "StorageTankDesignandConstructionGuidelines": "Storage tank design and construction guidelines",
    "SIGTTO-SGMF": "SIGTTO/SGMF LNG standards and guidelines (2015): almost no extractable text",
    "EHS+Guidelines+for+Ports": "IFC EHS Guidelines for Ports, Harbors and Terminals (2017)",
    "Code-of-Practice-LNG-facilities": "Code of practice for LNG facilities (regulator publication)",
    "cng-lng-regulations": "CNG/LNG regulations (US regulatory text, as filed in the library)",
    "Petroleum Rules 2002": "Petroleum Rules 2002 (India), as held",
    "PetroleumRegulations031719": "Petroleum regulations (document dated 2019-03-17 in its file name)",
    "corrosionresistantalloys": "Corrosion-resistant alloys in oil and gas: selection guidelines",
    "UpdateddraftT4S-LPG": "Updated draft T4S-LPG (technical standards document named in the file, 2018)",
    "Revised+LNG+Facilities": "Revised LNG facilities draft EHS guideline (December 2016)",
    "BIMCO-IBIA": "BIMCO-IBIA bunkering guide (2018)",
    "lng_regulatory_roadmap": "LNG regulatory roadmap",
    "Liquefied Petroleum Gas (Regulation": "Liquefied Petroleum Gas (Regulation of Supply and Distribution) Order, 2000 (India)",
    "oil_and_gas_separation_design_manual": "Oil and gas separation design manual (Sivalls)",
    "lpg-fueled-vessels": "Guidelines for LPG-fuelled vessels (IRS)",
    "HydrogenLeakageRegulations": "Hydrogen leakage regulations: CGEP commentary (2022)",
    "petrochemical-organic-chemical-sector-flare": "Petrochemical/organic chemical sector flare gas rules (minimal text)",
    "PNGRB_T4S_CGD": "PNGRB technical standards and specifications for city gas distribution networks (PDF from pngrb.gov.in; little extractable text)",
    "PNGRB_RO_T4S_2025": "PNGRB T4S for dispensing automotive fuels (retail outlets), 2025 consolidated amendment",
    "AER_Directive060": "Alberta Energy Regulator Directive 060: upstream flaring, incinerating and venting",
    "DOE_STD_1189_2016": "DOE-STD-1189-2016: Integration of Safety into the Design Process",
    "eCFR_29CFR1910.106": "29 CFR 1910.106 Flammable liquids (eCFR, 2026-11-03)",
    "eCFR_29CFR1910.110": "29 CFR 1910.110 Storage and handling of liquefied petroleum gases (eCFR, 2026-11-03)",
}


def title(f):
    for k, v in TITLES.items():
        if k.lower() in f.lower():
            return v
    return re.sub(r"^([0-9a-f]{20,}_)+", "", f)


def main(paths):
    rows = []
    for p in paths:
        rows += list(csv.DictReader(open(p, encoding="utf-8")))
    by = collections.defaultdict(collections.Counter)
    mod, typ, files = collections.Counter(), collections.Counter(), collections.Counter()
    classified = 0
    for r in rows:
        t = title(r["file"])
        files[t] += 1
        mod[r["modality"]] += 1
        if r["recommendation_types"]:
            classified += 1
            for k in r["recommendation_types"].split(";")[:2]:
                typ[k] += 1
                by[t][k] += 1
    n = len(rows)
    fr = "\n".join(f"| {t} | {c} | {', '.join(f'{k} {v}' for k, v in by[t].most_common(3)) or '-'} |" for t, c in files.most_common())
    tr = "\n".join(f"| {k} | {c} |" for k, c in typ.most_common())
    doc = f"""# What public design and safety documents require: a counts-only survey

Run on 2026-11-06 with `python -m process_safety requirements` on {len(files)} public documents: regulations, codes of practice, EHS guidelines, class-society and industry guidance, a design manual, a US safety-in-design standard and two sections of the US federal regulations. **Only counts are published here.** The statements stay in private files: they are other organisations' text, and nothing in this repository reproduces it.

## Totals
{n:,} normative statements: {mod['mandatory']:,} mandatory ("shall", "must", "is required to"), {mod['recommended']:,} recommended ("should") and {mod['prohibition']:,} prohibitions. {classified:,} ({100 * classified / n:.0f}%) matched one or more of the catalogue's recommendation types; {n - classified:,} ({100 * (n - classified) / n:.0f}%) matched none, because the catalogue covers relief, protective instrumentation, isolation, detection, integrity and similar safety topics, not every requirement in a regulation (licensing, marking, administrative duties). A hand check of 14 matches in an earlier run found about two thirds sensible, so treat the type counts as indicative.

## Recommendation types the documents mention (best two matches per statement)
| Type | Statements |
|---|---|
{tr}

What this says, and does not say: these are requirements in public documents, not the recommendations a HAZOP raises, so the ranking differs from a PHA register's. Procedures and training, inspection and testing, materials and relief devices lead here. A plausible reason, not tested, is that regulations state duties, while relief sizing, high-level protection and detection are detailed in design standards (API, NFPA, IEC) that are mostly paywalled and absent from this collection. There is still no published frequency benchmark for HAZOP recommendation types.

## By document
| Document | Statements | Top types |
|---|---|---|
{fr}

Documents that yielded almost nothing are scanned, image-based or table-based PDFs where `pdftotext` finds little text: an extraction limit, not a finding.

## Method and limits
Sentences with shall/must/should/shall-not/is-required-to; keyword classification against `docs/RECOMMENDATIONS_CATALOG.md`; no table or figure reading; titles are taken from file names or the source page and may not match official titles. See `docs/REQUIREMENTS_EXTRACT.md` for the tool and its limits. Sources of the second batch: pngrb.gov.in, static.aer.ca, wbdg.org (DOE-STD-1189-2016) and the eCFR API.
"""
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "PUBLIC_REQUIREMENTS_SURVEY.md")
    open(out, "w", encoding="utf-8").write(doc)
    print(n, "statements,", len(files), "documents")


if __name__ == "__main__":
    main(sys.argv[1:])

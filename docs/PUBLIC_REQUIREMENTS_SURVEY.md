# What public design and safety documents require: a counts-only survey

Run on 2026-11-06 with `python -m process_safety requirements` on 23 public documents: regulations, codes of practice, EHS guidelines, class-society and industry guidance, a design manual, a US safety-in-design standard and two sections of the US federal regulations. **Only counts are published here.** The statements stay in private files: they are other organisations' text, and nothing in this repository reproduces it.

## Totals
8,519 normative statements: 6,870 mandatory ("shall", "must", "is required to"), 1,095 recommended ("should") and 554 prohibitions. 1,700 (20%) matched one or more of the catalogue's recommendation types; 6,819 (80%) matched none, because the catalogue covers relief, protective instrumentation, isolation, detection, integrity and similar safety topics, not every requirement in a regulation (licensing, marking, administrative duties). A hand check of 14 matches in an earlier run found about two thirds sensible, so treat the type counts as indicative.

## Recommendation types the documents mention (best two matches per statement)
| Type | Statements |
|---|---|
| PROCEDURE | 330 |
| INSPECT-TEST | 292 |
| MATERIAL | 230 |
| PSV-ADD | 152 |
| HAC | 126 |
| FIRE-PROT | 95 |
| INTERFACE-DP | 91 |
| DEADLEG | 86 |
| INHERENT | 79 |
| ISOLATION | 79 |
| FLARE-LOAD | 64 |
| DETECT | 50 |
| LAYOUT | 46 |
| ALARM | 39 |
| SIF-UPGRADE | 34 |
| HLL-SIF | 31 |
| BDV | 15 |
| CYBER-PCN | 12 |
| PSV-UPSIZE | 6 |
| RELIEF-PIPING | 6 |
| DUST | 3 |

What this says, and does not say: these are requirements in public documents, not the recommendations a HAZOP raises, so the ranking differs from a PHA register's. Procedures and training, inspection and testing, materials and relief devices lead here. A plausible reason, not tested, is that regulations state duties, while relief sizing, high-level protection and detection are detailed in design standards (API, NFPA, IEC) that are mostly paywalled and absent from this collection. There is still no published frequency benchmark for HAZOP recommendation types.

## By document
| Document | Statements | Top types |
|---|---|---|
| Updated draft T4S-LPG (technical standards document named in the file, 2018) | 1694 | INSPECT-TEST 78, PROCEDURE 66, FIRE-PROT 64 |
| PNGRB T4S for dispensing automotive fuels (retail outlets), 2025 consolidated amendment | 1621 | PROCEDURE 83, INSPECT-TEST 52, HAC 37 |
| CNG/LNG regulations (US regulatory text, as filed in the library) | 1392 | PROCEDURE 42, PSV-ADD 39, MATERIAL 38 |
| Petroleum regulations (document dated 2019-03-17 in its file name) | 807 | INSPECT-TEST 56, PROCEDURE 24, MATERIAL 21 |
| 29 CFR 1910.110 Storage and handling of liquefied petroleum gases (eCFR, 2026-11-03) | 593 | PSV-ADD 53, PROCEDURE 28, INTERFACE-DP 22 |
| 29 CFR 1910.106 Flammable liquids (eCFR, 2026-11-03) | 540 | MATERIAL 37, PROCEDURE 20, DEADLEG 20 |
| Alberta Energy Regulator Directive 060: upstream flaring, incinerating and venting | 487 | FLARE-LOAD 44, PROCEDURE 25, INSPECT-TEST 10 |
| Code of practice for LNG facilities (regulator publication) | 380 | PROCEDURE 19, LAYOUT 13, MATERIAL 11 |
| DOE-STD-1189-2016: Integration of Safety into the Design Process | 212 | INTERFACE-DP 7, MATERIAL 6, INHERENT 5 |
| Storage tank design and construction guidelines | 135 | DEADLEG 12, MATERIAL 5, INHERENT 4 |
| Revised LNG facilities draft EHS guideline (December 2016) | 121 | PROCEDURE 6, DEADLEG 5, MATERIAL 4 |
| IFC EHS Guidelines for Ports, Harbors and Terminals (2017) | 115 | MATERIAL 10, INHERENT 4, LAYOUT 3 |
| Guidelines for LPG-fuelled vessels (IRS) | 98 | HAC 9, INHERENT 5, DETECT 2 |
| Petroleum Rules 2002 (India), as held | 90 | INSPECT-TEST 4, MATERIAL 3, PROCEDURE 2 |
| LNG regulatory roadmap | 55 | PROCEDURE 10, INHERENT 1 |
| Liquefied Petroleum Gas (Regulation of Supply and Distribution) Order, 2000 (India) | 46 | - |
| PNGRB technical standards and specifications for city gas distribution networks (PDF from pngrb.gov.in; little extractable text) | 43 | INSPECT-TEST 15, CYBER-PCN 2 |
| BIMCO-IBIA bunkering guide (2018) | 41 | PROCEDURE 1, INSPECT-TEST 1 |
| Oil and gas separation design manual (Sivalls) | 23 | INTERFACE-DP 2, RELIEF-PIPING 1 |
| Corrosion-resistant alloys in oil and gas: selection guidelines | 13 | MATERIAL 1 |
| Hydrogen leakage regulations: CGEP commentary (2022) | 5 | DETECT 2 |
| Petrochemical/organic chemical sector flare gas rules (minimal text) | 5 | - |
| SIGTTO/SGMF LNG standards and guidelines (2015): almost no extractable text | 3 | - |

Documents that yielded almost nothing are scanned, image-based or table-based PDFs where `pdftotext` finds little text: an extraction limit, not a finding.

## Method and limits
Sentences with shall/must/should/shall-not/is-required-to; keyword classification against `docs/RECOMMENDATIONS_CATALOG.md`; no table or figure reading; titles are taken from file names or the source page and may not match official titles. See `docs/REQUIREMENTS_EXTRACT.md` for the tool and its limits. Sources of the second batch: pngrb.gov.in, static.aer.ca, wbdg.org (DOE-STD-1189-2016) and the eCFR API.

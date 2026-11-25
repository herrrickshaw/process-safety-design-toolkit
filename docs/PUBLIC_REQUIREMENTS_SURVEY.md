# What public design and safety documents require: a counts-only survey

Run on 2026-11-06 with `python -m process_safety requirements` on 27 public documents: regulations, codes of practice, EHS guidelines, class-society and industry guidance, a design manual, a US safety-in-design standard and two sections of the US federal regulations. **Only counts are published here.** The statements stay in private files: they are other organisations' text, and nothing in this repository reproduces it.

## Totals
11,130 normative statements: 8,552 mandatory ("shall", "must", "is required to"), 1,864 recommended ("should") and 714 prohibitions. 2,131 (19%) matched one or more of the catalogue's recommendation types; 8,999 (81%) matched none, because the catalogue covers relief, protective instrumentation, isolation, detection, integrity and similar safety topics, not every requirement in a regulation (licensing, marking, administrative duties). A hand check of 14 matches in an earlier run found about two thirds sensible, so treat the type counts as indicative.

## Recommendation types the documents mention (best two matches per statement)
| Type | Statements |
|---|---|
| PROCEDURE | 434 |
| INSPECT-TEST | 363 |
| MATERIAL | 294 |
| PSV-ADD | 196 |
| HAC | 144 |
| INHERENT | 110 |
| FIRE-PROT | 108 |
| INTERFACE-DP | 107 |
| DEADLEG | 106 |
| ISOLATION | 96 |
| FLARE-LOAD | 71 |
| LAYOUT | 64 |
| DETECT | 61 |
| ALARM | 52 |
| SIF-UPGRADE | 44 |
| HLL-SIF | 38 |
| BDV | 24 |
| CYBER-PCN | 14 |
| PSV-UPSIZE | 8 |
| RELIEF-PIPING | 6 |
| DUST | 3 |

What this says, and does not say: these are requirements in public documents, not the recommendations a HAZOP raises, so the ranking differs from a PHA register's. Procedures and training, inspection and testing, materials and relief devices lead here. A plausible reason, not tested, is that regulations state duties, while relief sizing, high-level protection and detection are detailed in design standards (API, NFPA, IEC) that are mostly paywalled and absent from this collection. There is still no published frequency benchmark for HAZOP recommendation types.

## By document
| Document | Statements | Top types |
|---|---|---|
| CNG/LNG regulations (US regulatory text, as filed in the library) | 2784 | PROCEDURE 84, PSV-ADD 78, MATERIAL 76 |
| Updated draft T4S-LPG (technical standards document named in the file, 2018) | 1694 | INSPECT-TEST 78, PROCEDURE 66, FIRE-PROT 64 |
| PNGRB T4S for dispensing automotive fuels (retail outlets), 2025 consolidated amendment | 1621 | PROCEDURE 83, INSPECT-TEST 52, HAC 37 |
| Petroleum regulations (document dated 2019-03-17 in its file name) | 807 | INSPECT-TEST 56, PROCEDURE 24, MATERIAL 21 |
| Code of practice for LNG facilities (regulator publication) | 760 | PROCEDURE 38, LAYOUT 26, MATERIAL 22 |
| 29 CFR 1910.110 Storage and handling of liquefied petroleum gases (eCFR, 2026-11-03) | 593 | PSV-ADD 53, PROCEDURE 28, INTERFACE-DP 22 |
| 29 CFR 1910.106 Flammable liquids (eCFR, 2026-11-03) | 540 | MATERIAL 37, PROCEDURE 20, DEADLEG 20 |
| Alberta Energy Regulator Directive 060: upstream flaring, incinerating and venting | 487 | FLARE-LOAD 44, PROCEDURE 25, INSPECT-TEST 10 |
| HSE HSG253: The safe isolation of plant and equipment (UK) | 323 | PROCEDURE 29, INSPECT-TEST 5, INHERENT 3 |
| HSE HSG176: The storage of flammable liquids in tanks (UK) | 287 | INSPECT-TEST 14, MATERIAL 8, PROCEDURE 7 |
| Revised LNG facilities draft EHS guideline (December 2016) | 242 | PROCEDURE 12, DEADLEG 10, MATERIAL 8 |
| DOE-STD-1189-2016: Integration of Safety into the Design Process | 212 | INTERFACE-DP 7, MATERIAL 6, INHERENT 5 |
| Storage tank design and construction guidelines | 135 | DEADLEG 12, MATERIAL 5, INHERENT 4 |
| IFC EHS Guidelines for Ports, Harbors and Terminals (2017) | 115 | MATERIAL 10, INHERENT 4, LAYOUT 3 |
| Guidelines for LPG-fuelled vessels (IRS) | 98 | HAC 9, INHERENT 5, DETECT 2 |
| Petroleum Rules 2002 (India), as held | 90 | INSPECT-TEST 4, MATERIAL 3, PROCEDURE 2 |
| HSE HSG254: Developing process safety indicators (UK) | 58 | DETECT 1, PROCEDURE 1, INSPECT-TEST 1 |
| LNG regulatory roadmap | 55 | PROCEDURE 10, INHERENT 1 |
| LNGF-DesignConsiderations.pdf | 50 | HAC 3, INTERFACE-DP 2, INSPECT-TEST 2 |
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

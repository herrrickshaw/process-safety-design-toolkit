# What public design and safety documents require: a counts-only survey

Run on 2026-11-06 with `python -m process_safety requirements` on 17 public documents from the author's reference library (regulations, codes of practice, EHS guidelines, class-society and industry guidance, one design manual). **Only counts are published here.** The statements themselves stay in a private file: they are other organisations' text, and nothing in this repository reproduces it.

## Totals
5,023 normative statements: 3,943 mandatory ("shall", "must", "is required to"), 793 recommended ("should") and 287 prohibitions. 963 (19%) matched one or more of the catalogue's recommendation types; 4,060 (81%) matched none, because the catalogue covers relief, protective instrumentation, isolation, detection, integrity and similar safety topics, not every requirement in a regulation (licensing, marking, administrative duties). A hand check of 14 matches in an earlier run found about two thirds sensible, so treat the type counts as indicative.

## Recommendation types the documents mention (best two matches per statement)
| Type | Statements |
|---|---|
| INSPECT-TEST | 192 |
| PROCEDURE | 174 |
| MATERIAL | 139 |
| FIRE-PROT | 76 |
| PSV-ADD | 69 |
| HAC | 60 |
| INHERENT | 45 |
| DEADLEG | 44 |
| ISOLATION | 43 |
| DETECT | 37 |
| INTERFACE-DP | 35 |
| ALARM | 29 |
| LAYOUT | 29 |
| HLL-SIF | 24 |
| SIF-UPGRADE | 21 |
| FLARE-LOAD | 18 |
| BDV | 11 |
| CYBER-PCN | 9 |
| PSV-UPSIZE | 3 |
| RELIEF-PIPING | 3 |
| DUST | 1 |

What this says, and does not say: these are requirements in public documents, not the recommendations a HAZOP raises, so the ranking differs from a PHA register's. Inspection and testing, procedures and training, materials and fire protection lead here. A plausible reason, not tested, is that regulations state them as duties, while relief sizing, high-level protection and detection are detailed in design standards (API, NFPA, IEC) that are mostly paywalled and absent from this library. There is still no published frequency benchmark for HAZOP recommendation types.

## By document
| Document | Statements | Top types |
|---|---|---|
| Updated draft T4S-LPG (technical standards document named in the file, 2018) | 1694 | INSPECT-TEST 78, PROCEDURE 66, FIRE-PROT 64 |
| CNG/LNG regulations (US regulatory text, as filed in the library) | 1392 | PROCEDURE 42, PSV-ADD 39, MATERIAL 38 |
| Petroleum regulations (document dated 2019-03-17 in its file name) | 807 | INSPECT-TEST 56, PROCEDURE 24, MATERIAL 21 |
| Code of practice for LNG facilities (regulator publication) | 380 | PROCEDURE 19, LAYOUT 13, MATERIAL 11 |
| Storage tank design and construction guidelines | 135 | DEADLEG 12, MATERIAL 5, INHERENT 4 |
| Revised LNG facilities draft EHS guideline (December 2016) | 121 | PROCEDURE 6, DEADLEG 5, MATERIAL 4 |
| IFC EHS Guidelines for Ports, Harbors and Terminals (2017) | 115 | MATERIAL 10, INHERENT 4, LAYOUT 3 |
| Guidelines for LPG-fuelled vessels (IRS) | 98 | HAC 9, INHERENT 5, DETECT 2 |
| Petroleum Rules 2002 (India), as held | 90 | INSPECT-TEST 4, MATERIAL 3, PROCEDURE 2 |
| LNG regulatory roadmap | 55 | PROCEDURE 10, INHERENT 1 |
| Liquefied Petroleum Gas (Regulation of Supply and Distribution) Order, 2000 (India) | 46 | - |
| BIMCO-IBIA bunkering guide (2018) | 41 | PROCEDURE 1, INSPECT-TEST 1 |
| Oil and gas separation design manual (Sivalls) | 23 | INTERFACE-DP 2, RELIEF-PIPING 1 |
| Corrosion-resistant alloys in oil and gas: selection guidelines | 13 | MATERIAL 1 |
| Hydrogen leakage regulations: CGEP commentary (2022) | 5 | DETECT 2 |
| Petrochemical/organic chemical sector flare gas rules (text extracted is minimal) | 5 | - |
| SIGTTO/SGMF LNG standards and guidelines (2015) - almost no extractable text | 3 | - |

Two documents yielded almost nothing (a scanned or image-based PDF gives `pdftotext` no text); that is an extraction limit, not a finding.

## Method and limits
Sentences with shall/must/should/shall-not/is-required-to; keyword classification against `docs/RECOMMENDATIONS_CATALOG.md`; no table or figure reading; each statement counted once per document; duplicated documents in the library were de-duplicated by file name; document titles above are taken from file names, which may not match the official titles. See `docs/REQUIREMENTS_EXTRACT.md` for the tool and its limits.

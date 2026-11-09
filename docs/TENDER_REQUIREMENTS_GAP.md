# Middle East tender requirements against iFluids' record and the toolkit: comparison and gaps

Written 2026-11-09 on branch `feature/project-pipeline-planning`. It replaces the earlier India and Singapore version (still in git history, commit `c623f65`): all of iFluids' external clients are in the Middle East, so the requirements, the iFluids evidence and the gaps below are Gulf-specific. Gap classes follow `docs/FEATURE_GAP_ANALYSIS.md` (build now, needs information, protected or out of scope). Nothing here was built or run.

**The evidence is weaker than the earlier version.** The Gulf operators' own requirements (ADNOC, Saudi Aramco, QatarEnergy, KOC, PDO and OQ) sit in standards and tender packages that are not public. No operator standard and no full tender document was read. Requirements are inferred from a tender listing, contractor-published award notices, a plan, secondary summaries and job postings, and each source is graded:

* **B**: a listing or contractor-published description of a real tender or award.
* **C**: a secondary summary, a plan seen only through a search summary, or a job posting. Indicative only.

There is no grade A (a primary document read in full).

## Sources
| Id | Source | Grade | What it gave | Limits |
|---|---|---|---|---|
| QE | QatarEnergy Refinery Mesaieed, international competitive bid LT24107800, "HAZOP revalidation and other safety studies", via a [TenderDetail listing](https://www.tenderdetail.com/Global-Tenders/TenderNotice/87894343/3DD34C2B-E3A1-4435-B5FC-C72857C4A137); closed 25 Nov 2024 | B | Scope in two parts; 120-day offer validity; 150-day bond; mandatory vendor registration and SAP vendor code; document purchase window | Issuer and country fields hidden on the page (Qatar inferred from Mesaieed); qualification criteria, evaluation, duration and currencies not shown; documents gated |
| SA | [Apave, Saudi petrochemical HAZOP award, Oct 2024](https://middle-east.apave.com/en/News/Apave-secures-major-process-safety-study-for-leading-petrochemical-company-in-Saudi-Arabia) (contractor press release) | B | Scope list, SABIC standards for inherently safer design, 18 to 24 months with concurrent units | No deliverables, software or client name |
| BG | Velosi, [Borouge 1 and 2 retrospective HAZOP and SIL](https://velosiaims.com/tr/velosi-news/contractaward2), Abu Dhabi (contractor press release) | B | HAZOP, SIL classification and verification, SRS; "latest ADNOC and international standards" | Award date unclear |
| DG | Velosi, [Dalma Gas Development HAZOP and SIL](https://velosiaims.com/tr/velosi-news/hazop-sil-studies-for-dalma-gas-development-project), Abu Dhabi, Jan 2022 | B | HAZOP and SIL of a gas turbine generator and export compressor; BS IEC 61882 | Client not named in the text |
| KP | KIPIC Annual Plan 2024 to 2025 (Kuwait): a six-month lump-sum tender for a HAZOP of refinery process units, April 2024 | C | A planned HAZOP tender | Seen only in a search summary; the PDF would not open (certificate error), so the document was not read |
| LC | Local-content regimes: ADNOC and the Unified ICV programme; Saudi Aramco IKTVA ([Aramco supplier page](https://aramco.com/en/what-we-do/suppliers/become-a-supplier), law-firm summaries) | C | ICV certificate and IKTVA reports scored in bids | Consultants disagree on whether an ICV certificate is mandatory or only scored; no official ADNOC page read; IKTVA summaries date from 2017 to 2018 |
| AD | ADNOC contractor HSE Management Standard (named in ADNOC's 2023 sustainability report, via a search summary) | C | Minimum HSE prequalification and selection criteria exist | Standard not read |
| JP | Gulf job postings (QatarEnergy LNG, ADNOC Onshore, Ras Laffan roles) | C | Studies operators expect: QRA, HAZOP and SIL baseline and revalidation, HAZID, What-if, LOPA, FERA, EERA, dropped objects; certified functional safety credentials | Employer wishes, not tender rules |
| AR | Saudi Aramco HAZOP guideline AER-5437 (2009 copy) and SAEP-343 risk-based inspection (copy, 2015 and 2019 issues) | C | HAZOP as one hazard-identification step; RBI per API RP 580 | Secondary copies; current SAEPs may differ |
| RC | Royal Commission Environmental Regulations (RCER-2015) for Jubail, Yanbu and Ras Al Khair | C | A best-available-technology assessment for new and modified facilities | An environmental assessment, not a QRA; no RCER risk-assessment text found |

Not used: a KOC technical specification (its visible page names neither KOC nor any HAZOP rule, so a search summary's "KOC-L-017, third-party team leader" claim stays unconfirmed); all Indian and Singapore sources; an OMRAN (Oman) invitation, which is general consultancy. Nothing was found that sets HAZOP or QRA requirements for Oman.

## Requirements found
| # | Requirement | Seen in |
|---|---|---|
| R1 | Vendor registration with the operator and purchase of the tender document inside the issue window | QE |
| R2 | Bid bond, with bond and offer validity (120 and 150 days in QE) | QE |
| R3 | Local-content scoring: ICV certificate (ADNOC and Unified programme), IKTVA reports (Aramco) | LC |
| R4 | Contractor HSE prequalification | AD |
| R5 | HAZOP revalidation and baseline HAZOP of operating units | QE, KP, SA |
| R6 | SIL studies for new safety instrumented functions; retrospective SIL classification and verification with an SRS | QE, BG, DG |
| R7 | Method and standards: BS IEC 61882, operator and client standards (ADNOC, SABIC) | DG, BG, SA |
| R8 | LOPA, flare system analysis, management-of-change and incident review, fire and dust explosion, human factors, external events, utilities | SA |
| R9 | Emergency escape, evacuation and rescue assessment (EERA) and pre-incident plans for major accident scenarios | QE |
| R10 | PSV design review for staggered set points | QE |
| R11 | Credentialed, independent HAZOP leader | JP |
| R12 | Front-end QRA, including land-use planning | JP |
| R13 | Multi-unit programme delivery: 18 to 24 months with concurrent units | SA |
| R14 | Fire and explosion risk analysis (FERA) and dropped-object studies | JP |
| R15 | Risk-based inspection per SAEP-343 and API RP 580 | AR |
| R16 | Environmental best-available-technology assessment | RC |

## iFluids' stated Middle East record
Everything below is a company statement, not verified. India client names in the brochure data are set aside because iFluids' external clients are in the Middle East.

* **Gulf clients (brochure data in the landscape deck):** QAFCO, Qatar Energy, ORPIC, OQ and Aramco's Jubail refinery. No project detail.
* **Presence (iFluids presentation):** offices or associates in Oman, Qatar, Kuwait and the UAE, besides Chennai and Mumbai.
* **Named projects (iFluids presentation, no clients or dates):** flare radiation analysis of Rumaitha/Shanayel facilities; fire and explosion risk assessment study; detailed engineering for fire detection and protection; lightning protection assessment for 43 buildings; arc flash and illumination for offshore rigs; crude tanks and SBM feasibility; OLGA model; as-built drafting to PDO standards.
* **Services (iFluids profile):** HAZOP and HAZID, QRA, SIL assessment, LOPA, ALARP demonstration, ERDMP, risk-based inspection, pipeline asset integrity, environmental risk assessment and emission study.
* **Tools:** PHAST and PHAST Risk, PHA-Pro, exSILentia, Bow-Tie, Isograph, FlareNet, PIPENET, OLGA, HYSYS, Primavera.
* **Certification:** ISO 9001:2008 in one deck, none in the other profile, 2015 on a third-party contact page: check the current certificate.

## Comparison
Evidence: **stated** = iFluids says it offers this; **partly** = related work or a service without a project; **not stated** = nothing found. Toolkit: **covered** = a module does it; **partial** = screening or one part; **missing** = nothing in the repository.

| # | iFluids stated evidence | Evidence | Toolkit support | Toolkit |
|---|---|---|---|---|
| R1 | Not stated | not stated | `tender_register` tracks deadlines; no field for the purchase window or registration status | partial |
| R2 | Not stated | not stated | no bond or validity tracking | missing |
| R3 | Offices in four Gulf countries; certificates not stated | partly | none | missing |
| R4 | Not stated | not stated | none | missing |
| R5 | HAZOP, HAZID, PHA-Pro; Gulf clients named without projects | stated | `hazop`, `pha` (revalidation, carry-forward, actions), `pid_review`, `wbs` template | partial |
| R6 | SIL assignment, verification, validation; exSILentia | stated | `sil`, `sil_lifecycle` (PFD, HFT and SFF, SRS skeleton); no systematic capability or proof-test coverage | partial |
| R7 | PDO standards named for drafting; IEC 61882 use not stated | partly | `hazop` uses IEC 61882 guidewords only; operator standards unread | partial |
| R8 | LOPA and flare radiation analysis stated; dust explosion and human factors not | partly | `sil.lopa`, `flare`, `flare_system`, `dust_explosion`, `atex`; no human factors | partial |
| R9 | Egress design, evacuation modelling, ERDMP; EERA by name not stated | partly | `egress` (RSET against ASET), `qra.emergency` | partial |
| R10 | Not stated | not stated | `relief` has accumulation for multiple valves; no set-point review | partial |
| R11 | Independent HAZOP service; leader credentials not stated | partly | none: people and independence | missing |
| R12 | QRA with PHAST Risk | stated | `qra` (contours, F-N, ALARP, buildings, override hook); no Gulf criteria set | partial |
| R13 | 900+ process safety projects claimed; Primavera | partly | `wbs`, `schedule`, `portfolio`, `pha` action tracking | covered |
| R14 | Fire and explosion risk assessment study (named) | partly | `qra.effects`, `explosion`, `structural_fire`, `mechanical_safety` (dropped objects) | partial |
| R15 | Risk-based inspection listed | stated | none | missing |
| R16 | Environmental risk assessment and emission study listed | partly | `emissions` | partial |

Counts. iFluids evidence: 4 stated, 8 partly, 4 not stated. Toolkit: 1 covered, 10 partial, 5 missing.

## Gaps to fill
### Gaps iFluids has to close itself (evidence and capability)
| # | Gap | What to assemble or decide |
|---|---|---|
| E1 | Gulf reference register | Per client, facility and year: units or P&IDs, study types (HAZOP, SIL, EERA, FERA), completion letters. Named projects lack client and date |
| E2 | Vendor registrations | QatarEnergy needs registration and a SAP vendor code before the tender document can be bought; check ADNOC, Aramco, OQ, PDO and KOC status |
| E3 | Local-content certificates | ICV (UAE and Oman) and IKTVA (Saudi) status and scores: not stated |
| E4 | HSE prequalification pack and ISO certificate | ADNOC-type contractor HSE standard; resolve the ISO 9001 edition conflict |
| E5 | PSV design review capability | Not stated: decide whether to offer it, partner or decline |
| E6 | HAZOP leader credentials and independence | Names, certifications (for example certified functional safety professional) and an independence statement |
| E7 | Bid bond and guarantee facility | QE-type bonds with 150-day validity |

### Toolkit: build now
| # | Gap | Extends | Why it can be built now |
|---|---|---|---|
| M1 | Gulf bid mechanics: purchase window, registration status, bond amount and validity, offer validity, ICV or IKTVA status, with date checks | `tender_register` | Fields and date arithmetic; every value is an input |
| M2 | Eligibility checker against the reference register | `tender_register` | Criteria are inputs |
| M3 | WBS templates for HAZOP revalidation, SIL for new SIFs, EERA and FERA | `wbs` | Structure only, no numbers |
| M4 | P&ID register to HAZOP nodes to WBS | `plant_model`, `pha`, `wbs` | Existing ingestion |
| M5 | Bid compliance matrix: requirement, evidence, module, status | `tender_register` | Structure only |

### Toolkit: needs additional information
| # | Gap | What is missing |
|---|---|---|
| N1 | Operator standards (ADNOC, Aramco SAEP and SAES, QatarEnergy, SABIC, KOC, PDO) | Not public; obtained through registration, tender packages or contracts |
| N2 | Local-content scoring rules | Official ADNOC and Unified ICV, Aramco IKTVA, Oman and Qatar pages (only secondary summaries read) |
| N3 | PSV staggered set-point review | API 520 and 521 text (paywalled); the toolkit's accumulation figures are secondary-source values marked "verify" |
| N4 | Risk-based inspection | API RP 580 and 581, SAEP-343 text |
| N5 | EERA and pre-incident plan methods | Operator procedures and the governing standard, unread |
| N6 | Gulf QRA criteria and land-use rules | Not found; the toolkit has only UK R2P2 and Dutch Bevi sets |
| N7 | RCER best-available-technology procedure | RCER Volume II, published by the Royal Commission, not read |
| N8 | Dust explosion and human factors methods | NFPA and guidance text, unread |

### Protected or out of scope
Vendor registrations and bonds; ICV and IKTVA certification by approved auditors; operator-internal standards (confidential); signed or certified studies; the commercial tools iFluids delivers in (PHAST, PHA-Pro, exSILentia), which the toolkit cross-checks and does not replace.

## Data needed to close the gaps
| From | Data | Closes |
|---|---|---|
| iFluids project records | Gulf reference register; registration status and codes; ICV and IKTVA certificates; HSE pack; current ISO certificate; credentials of HAZOP leaders; HAZOP hours per node | E1 to E7, M2, M4 |
| Operators (via registration or tender packages) | ADNOC contractor HSE standard and process safety standards; Aramco SAEP and SAES; QatarEnergy tender documents; SABIC and PDO specifications | N1, N3, N5, N6 |
| Official public pages | ADNOC and Unified ICV, Aramco IKTVA, Oman and Qatar local-content rules; RCER Volume II | N2, N7 |
| Paywalled standards | API 520, 521, 580, 581; IEC 61882; NFPA dust-explosion text | N3, N4, N8 |

## Suggested order
1. Build the Gulf reference register from iFluids records (E1): it drives the eligibility checker and every bid response.
2. M1, M2 and M5: bid mechanics, eligibility and compliance matrix.
3. M3 and M4: study templates and the P&ID-to-WBS path.
4. Obtain the operator documents (N1) as registrations allow; do not code anything from them until read.

## Not checked
Whether the pattern holds for operators not covered (PDO, OQ, KNPC, Bapco); the actual qualification criteria of the QatarEnergy tender; whether ICV certificates are mandatory for consultancy bids; any HAZOP or QRA requirement in Oman; the KIPIC plan text; iFluids' current registrations and certificates.

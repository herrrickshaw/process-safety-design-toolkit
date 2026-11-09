# Tender requirements against the toolkit: comparison and gaps to fill

Written 2026-11-09 on branch `feature/project-pipeline-planning`. It compares what a small set of **published tender documents and regulator guidance** ask for with what this repository offers today, and sorts the gaps with the same classes as `docs/FEATURE_GAP_ANALYSIS.md` (build now, needs information, protected or out of scope). Nothing here was built or run. "Offering" means the repository's modules, not a consultancy's staff, credentials or software licences.

## Sources read (and what was not)
Five sources. They are a thin sample: three Indian tender records, one expression of interest, one regulator's guidance. Treat the requirement list as a starting checklist, not a market survey.

| Id | Source | What it is | Route | Limits |
|---|---|---|---|---|
| NRL | Numaligarh Refinery pre-bid minutes, ref PUR-TS-1004878, 17 Jan 2023 ([PDF](https://www.nrl.co.in/UPLOAD/Tender/NRL117202325015PM_Pre_Bid_MoM_2968033.pdf)) | Periodic HAZOP of all process units and utilities, GeM bid GEM/2023/B/2968033 | PDF text extracted locally | One page of minutes. The tender document itself, the second qualification criterion (B) and the scope text were **not** read |
| IOCL | Indian Oil Marketing Division, Kandla LPG import terminal, GeM/2025/B/6914271, via a [tender aggregator listing](https://tenderdekho.com/tender-detail/td-3j5ibruWee) | HAZOP and QRA, ERDMP manual update, safety report; consultancy only | Aggregator page summarised by a fetch tool | Not the bid document. Turnover figure shown without a unit, EMD, timeline and payment terms not shown. The listing names Parbind Petsafety as L1 and iFluids Engineering as L2; iFluids also appears among the attendees in the NRL minutes |
| OIL | Oil India pre-bid replies, tender CGI3675P24, 26 Jun 2023 ([PDF](https://www.oil-india.com/files/oldtender/national/PREBID_CGI3675P24.pdf)) | Residual life assessment, fit-for-purpose/service and QRA of two cross-country pipelines | PDF text extracted locally | Four pages of bidder queries. The table of ten threat categories and the deliverable units are images and were not read. These are bidders' proposals; OIL's replies mostly say "as per tender document" |
| BMC | Brunei Methanol Company EOI WR 6012297, Health Risk Assessment consultancy, 2023 ([page](https://www.brunei-methanol.com/eoi-hraconsultancy)) | Expression of interest | Page summarised by a fetch tool | Summary only |
| SG | Singapore Major Hazards Department QRA information guide (Rev 0, Dec 2025) and NEA QRA Criteria Guidelines Rev 2, 11 Jul 2024 ([guide](https://www.nea.gov.sg/docs/default-source/our-services/building-planning/qra-info-guide-and-assessment-checklist.pdf)) | Regulator guidance on what a QRA submission must meet; **not a tender** | PDF text extracted locally | The QRA Technical Guidance and Submission Format it points to were not read |

Not used: a UK listing titled "M0070 QRA Service" (it turned out to be project risk management, not process safety); a JTC requirements link (404); a Contracts Finder attachment (403, not bypassed). Full GeM documents were not available to me.

## Requirements found
| # | Requirement | Seen in |
|---|---|---|
| R1 | Pre-qualification by past experience measured in a quantity under one contract: 300 P&IDs of HAZOP under a single work order; 156 km of pipeline assessment in one contract within 7 years; 7 years of HAZOP/QRA and ERDMP experience | NRL, OIL, IOCL |
| R2 | Financial and statutory proof: turnover threshold, solvency or financial statements, GST and PAN, earnest-money deposit with exemption for micro and small enterprises | IOCL, NRL |
| R3 | Bid mechanics: two-packet bid, bid validity (120 days), pre-bid query round, value-wise evaluation, technical bid with a methodology statement | IOCL, NRL, OIL |
| R4 | Regulator-registered consultant for the QRA | SG |
| R5 | Study carried out at the client's site only | NRL |
| R6 | Periodic HAZOP of every process unit and utility | NRL |
| R7 | HAZOP and QRA together with an ERDMP manual update and a safety report | IOCL |
| R8 | Pipeline residual life, fit-for-purpose and QRA with a probabilistic risk engine, in-line-inspection data, Monte Carlo per defect, ten threat categories, results per chainage and for years 1 to 5 | OIL (as proposed by bidders) |
| R9 | QRA that meets published criteria: individual risk of fatality and injury, cumulative escalation, occupied buildings; contours confined within the boundary or to industrial land and not reaching sensitive receptors; cluster boundaries | SG |
| R10 | Structured ALARP demonstration, including why further reduction is grossly disproportionate; top risk contributors carried into ALARP prioritisation | SG |
| R11 | Three QRA types: fixed installation, pipeline, bulk road transport | SG |
| R12 | Follow-on deliverables: emergency response plan, process hazard analysis, fire safety plan, pollution impact study | SG |
| R13 | Prescribed submission format with electronic files, completeness check, at most two comment rounds, about 4 to 6 months to clear | SG |
| R14 | Early-stage QRA allowed on coarse data (maximum inventory, expected conditions, key equipment, anticipated layout), updated as design firms up | SG |
| R15 | Health risk assessment of manned buildings: physical, chemical, biological, ergonomic and psychosocial hazards, with measurements, risk ranking and an action plan | BMC |
| R16 | Team CVs, a project timeline with milestones, a methodology and standards statement | BMC, IOCL |

SG gives numbers for R9 that the toolkit can check against, read from the 2024 criteria guideline: fixed installations, individual risk of fatality 5e-5 per year confined within the boundary and 5e-6 confined to industrial land, with 3e-7 also listed; injury 3e-7; cumulative escalation 1e-4 confined within the boundary; on-site occupied buildings 1e-3 not to be exceeded. Pipelines and bulk transport have lower values in the same document.

## Comparison with the offering
Status: **yes** = a module covers it; **partial** = screening or one part; **no** = nothing in the repository.

| # | Toolkit offering today | Status | Gap |
|---|---|---|---|
| R1 | `tender_register` tracks tenders, but nothing tests a requirement such as "300 P&IDs under one work order" against a reference list | no | eligibility check against a references register |
| R2 | none (company records) | no | out of scope |
| R3 | `tender_register` (deadlines, missed bids, bid score), `wbs` and `schedule` for the timeline | partial | no bid-validity or compliance-matrix tracking |
| R4 | none | no | credential, not software |
| R5 | none | n/a | commercial term |
| R6 | `hazop.generate`, `pha` (worksheets, actions, revalidation, carry-forward), `pid_review`, `plant` ingestion of P&ID registers, `wbs` HAZOP template | partial | nothing turns an ingested P&ID register into a node list and a WBS with effort per P&ID |
| R7 | `qra` (screening), `qra.emergency` (zones, MCLS, ERDMP-style level), `pha` | partial | no ERDMP manual or safety report skeleton; the PNGRB and OISD clause text was not read |
| R8 | `pipeline` (design pressure, wall thickness, impact radius) only | no | no residual-life, fitness-for-service, inspection-data or probabilistic pipeline engine |
| R9 | `qra.risk` (LSIR contours, IRPA, F-N, PLL), `qra.alarp` (R2P2 and Bevi sets plus custom), `qra.buildings` | partial | no Singapore criteria set; no boundary or land-use confinement check; no injury contours; cumulative escalation is qualitative only (`hazid` lists domino as a prompt) |
| R10 | `qra.alarp`, `qra.mitigation` (VPF, disproportion factor, ICAF cost-benefit) | yes | no structured ALARP demonstration document |
| R11 | fixed installation only | partial | no pipeline or road-transport QRA |
| R12 | `pha`, `structural_fire`, `fire_water`, `emissions`, `qra.emergency` | partial | scattered calculations, no deliverable assembly |
| R13 | `qra.report` writes HTML, Excel and CSV | partial | no regulator submission format (the NEA Submission Format was not read) |
| R14 | `qra run --sample`, screening-level by design, limits stated in `docs/QRA.md` | yes | none beyond stated screening limits |
| R15 | `noise` (OSHA exposure only) | no | no health risk assessment |
| R16 | `docs/QRA.md`, `docs/VALIDATION.md`, `SOURCES.md` give citable method and limits; `wbs`, `schedule` give timeline | partial | no proposal or methodology-statement generator |

## Gaps to fill, by class
### Build now (a source in hand or no external constant needed)
| Gap | Where | Why it can be built |
|---|---|---|
| G1 Singapore criteria set and contour-confinement check: IR (fatality) contours against the site boundary and land-use polygons, with the thresholds above as a sourced criteria set beside R2P2 and Bevi | `qra.alarp`, `qra.risk` | thresholds read from the NEA guideline; geometry is stdlib. Tests: a contour inside the boundary passes, scaling frequencies by a factor moves the contour outward monotonically |
| G2 Eligibility checker: tender criteria (minimum quantity in one contract, years, value) against a references register, with the evidence listed | `tender_register` | every criterion is an input; pass or fail arithmetic |
| G3 P&ID register to HAZOP node list to WBS, so effort can be tracked per P&ID | `plant_model`, `pha`, `wbs` | existing ingestion; effort values stay inputs |
| G4 Compliance matrix: requirement, evidence, module, status, for the bid response | `tender_register` or `compliance` | structure only |
| G5 ALARP demonstration skeleton filled from `mitigation` results | `qra.report` | structure follows what SG says a demonstration must contain |

### Needs additional information
| Gap | What is missing |
|---|---|
| G6 Pipeline QRA and residual-life or fitness-for-service (R8, R11) | the governing methods (API 579, ASME B31G and similar) are paywalled and were not read; a probabilistic engine with inspection data needs defect-growth and failure-prediction models with sourced parameters |
| G7 Injury contours and cumulative escalation (R9) | the injury harm criteria and escalation method sit in the NEA QRA Technical Guidance, which was not read |
| G8 Road-transport QRA (R11) | route and accident frequency data |
| G9 ERDMP manual and safety report structure (R7) | the PNGRB and OISD clause text was not read; `docs/DATA_REGISTER.md` records the official purchase route for OISD editions |
| G10 Regulator submission format (R13) | the NEA Submission Format document |
| G11 Health risk assessment (R15) | exposure limit tables and measurement methods to be read from primary sources |
| G12 HAZOP effort per P&ID for pricing (R6) | the company's own productivity data; the toolkit holds no rates |

### Protected or out of scope
| Item | Why |
|---|---|
| Regulator registration (R4), turnover, GST and PAN (R2), on-site delivery (R5), team CVs (R16) | credentials, company records and commercial terms, not software |
| A named proprietary risk engine (R8, Muhlbauer-type or an equivalent) | vendor models; the override hook can accept a result, not reproduce the engine |
| Certified or signed studies | the toolkit's limits statement stands: screening aids, not certified design |

## Suggested order
1. G1, then G2 and G4: small, sourced, and they make the next bid checkable.
2. G3 and G5 next; they reuse the existing ingestion and `mitigation` work.
3. Obtain the NEA Technical Guidance and Submission Format (G7, G10) and the OISD or PNGRB text (G9) before any code for those items.
4. G6 only after the pipeline-assessment standards have been read; do not type remembered values.

## Not checked
Whether the pattern across these five sources holds for other operators; the PQC criterion (B) at NRL; the OIL scope table; whether a client would accept a screening-level QRA for R9 without a validated consequence tool.

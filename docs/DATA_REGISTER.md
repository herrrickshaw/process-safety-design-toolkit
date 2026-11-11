# Data register: sources, gaps and data still required

Started 2026-11-07. Hand-written (not generated); `SOURCES.md` is the line-by-line ledger of constants, this page is the map above it:
what data the toolkit stands on, what is missing, and what to obtain next. Update it when a source is read, a gap closes or a new gap is found.

**Read levels used here:** *text* = document text read for the toolkit; *summary* = a search-engine summary or a presentation deck only;
*pointer* = the source exists and was located but no values were taken; *blocked* = the source exists but could not be fetched or is paywalled.

## A. Data sources in use

| Source | What it gives | Access | Read | Used by |
|---|---|---|---|---|
| DNV "Theory - Jet Fire" (JFSH, Dec 2023) and its validation document | Chamberlain jet-flame equations; field-trial inputs; accuracy claims | free PDFs (no-reproduction notice) | text | `jet_flame` |
| Witlox and Fernandez, ATEX atmospheric expansion, IChemE Hazards 26 (2016) | Mass, momentum and energy balances for orifice release expansion; velocity cap; validation ranges | free PDF | text | `expansion` |
| US EPA TSCREEN workbook (EPA-454/B-94-023), section 5.4 | Britter-McQuaid criteria and far-field fits; worked examples | free PDF | text | `dense_gas` |
| OISD letter OISD/ENGG/GEN/22 to PNGRB (30 Apr 2020), Annexure A | OISD's table of 60 refinery and gas-processing standards with scope; the ten statutory ones | free PDF on pngrb.gov.in | text | `standards.oisd_refinery_scope` |
| OISD official standards list, oisd.gov.in (fetched 2026-09-21) | 105 standard numbers, titles, editions | free web page | titles only | `standards.oisd` |
| **OISD-STD-118 Rev 3 (June 2025) "Suraksha Samwad" presentation** (user-supplied, 15 pages) | Scope, 1000 KL threshold, QRA and board approval for non-compliance, definitions added, layout philosophy, flare sterile radius, dyke capacities, titles of Tables 1-12 | supplied by the user | text (slides) | not yet coded; see section C |
| **OISD-GDN-192 "Safety Practices During Construction", 2nd edition April 2016** (user-supplied; the PDF is titled "GCC-FINAL and GDN 192", 68 pages of scanned images, read by OCR) | Construction-phase safety: general duties of execution agencies and owners, work-place practices, excavation, scaffolding, structural work, road work, cutting and welding, confined spaces, proof and pressure testing, work at heights, lifting equipment. Marked "for restricted circulation only" and not to be reproduced | supplied by the user (controlled copy) | text by OCR (accuracy not checked page by page) | candidate source for a construction-safety scenario; Annexure I lists about 31 BIS safety codes for civil works (IS 818 onward), a pointer list for Indian codes; no text reproduced here |
| NIST cryogenic material properties, 304 stainless page | Fits for conductivity, specific heat, modulus, expansion, 4-300 K | free web page | text | not yet in code |
| NIST-JANAF, NIST/TRC Web Thermo Tables, Sandia hydrogen compatibility reference, NIMS creep sheets | Thermochemistry; pure-component data; hydrogen embrittlement; creep rupture | free (WTT Lite) / free / free / free | pointer | none yet |
| CoolProp, `fluids`, `thermo` (dev-time only) | Fluid properties used as oracles; `data/fluid_screening.json` | open licence | tool | `fluiddata`, cross-checks |
| API 2000 5th edition (1998), 49 CFR 192/193, 40 CFR 68, OSHA 1910.119/.95, Seveso III Annex I | Tank venting, pipeline, LNG, RMP, PSM, noise, thresholds | free (public posting or law text) | text | `tank_venting`, `pipeline`, `lng`, `rmp`, `psm`, `noise`, `mah` |
| HSE R2P2, PHMSA LNG failure-rate table, Cox-Lees-Ang, Purdue/Crowl probits, MoEF EIA manual | QRA criteria, generic frequencies, ignition and probit constants | free documents, several via excerpts | summary or text (see `SOURCES.md`) | `qra` |

## B. Gaps in data

**Governing standards not read (paywalled or unavailable).** API 520, 521, 526 and 2000 7th edition; IEC 61508 and 61511 beyond the Table 6 sample;
EN 1993-1-2; NFPA 59A, 68, 69, 855; IEC 60079-10-1 and EI 15; DIERS method papers; the TNO Yellow and Purple Books; OISD-STD-106, 113, 116, 118 (tables) and 244.
Effect: every constant from these is recalled or an input, and `structural_fire`, `vapour_fire` and `relief` carry "verify" flags.

**Quantitative data missing.**
* Generic failure frequencies for pumps, compressors, valves and flanges (no verified public row).
* Open flammable-limit, heat-of-combustion and autoignition data (NIST WTT Lite covers about 150 compounds only; DIPPR and Yaws are not open).
* Carbon-steel low-temperature properties (NIST has nickel steels, which are unreliable, and austenitics only).
* Steel strength and thermal properties at fire temperatures (EN 1993-1-2 Table 3.1 and annex).
* Measured values for the Chamberlain jet-fire trials (DNV gives plots, not tables) and any jet-fire-on-steel validation case.
* Droplet-size and rainout correlation (CCPS modified correlation reported best by the DNV JIP, not read); EPA aerosol correction (equation unreadable).
* Britter-McQuaid correlation curves (two figures) and the HSE report itself (open copy returned HTTP 403): flammable-limit distances are not covered.
* Blast curves for the multi-energy method; BLEVE blast and fragment correlations.
* Dense-phase CO2 and impurity equation of state for hazard work (CoolProp has CO2; not wired in) and decompression-fracture data.
* Battery vent-gas composition and rate (UL 9540A test data are project-specific).
* Incident and frequency data for biogas and CBG plants, SAF and HEFA units, ammonia bunkering and hydrogen stations (none found beyond summaries).

**Validation gaps.** `jet_flame` and `expansion` are plausibility-checked only; the puff fit in `dense_gas` is 2.4 percent off its own example; two Chamberlain
equation readings (angle correlation, base-width exponent) await the original; no module has been checked against a commercial consequence tool.

**Provenance gaps.** Most scenario-library entries rest on search-engine summaries; 14 of the 60 OISD numbers in OISD's 2020 table are absent from the 2026 official list (reason not determined).

## C. Additional data required

Ordered by what each unlocks. "From" is where I would look first; paywalled items need a controlled copy you hold.

| # | Data | From | Unlocks | Status |
|---|---|---|---|---|
| 1 | OISD-STD-118 Rev 3 Tables 1-12 (the distance values) | **buy from OISD** (Rs 10,000 + GST per standard, August 2026 editions, register at oisd.gov.in); the supplied deck lists the tables but not the values | layout-distance checker with real tables | **needed**; official purchase route found 2026-11-07 |
| 2 | OISD-STD-113, 116, 106, 244 (current editions) | OISD purchase; **draft STD-113 (hazardous-area classification) is free for public comment until 14 Nov 2026**, also drafts of STD-246 (CBG), STD-134 and STD-235 | classification extents, CBG plant safety, fire-water, relief and disposal checks | drafts downloaded 2026-11-07 (scratch folder, not in the repo); structure read, values not yet extracted |
| 3 | Generic frequencies for pumps, compressors, valves, flanges | OGP 434 series, HSE FRED, Purple Book (CPR 18E), or site data | complete parts-count QRA | needed |
| 4 | EN 1993-1-2 Table 3.1 and thermal annex | national standards body | replace recalled steel properties in `structural_fire` and `vapour_fire` | needed |
| 5 | NFPA 68, 69 and 855 (or EN 14491 and EN 14994) | NFPA / CEN | dust and battery-enclosure vent sizing, purge limit fraction | needed |
| 6 | IEC 60079-10-1 and EI 15 | IEC / Energy Institute | hazardous-area extents | needed |
| 7 | HSE CRR 17/1988 (Britter-McQuaid workbook) full report | download manually in a browser (automated fetch was blocked) | flammable-limit distances and the plume band alpha_c < 1 | needed |
| 8 | TNO Yellow Book multi-energy curves | TNO Coloured Books | multi-energy explosions | needed |
| 9 | Chamberlain 1987 tables, or digitised DNV Figures 1-4 | Chamberlain (Shell) paper; DNV validation plots | real error band for `jet_flame` | needed |
| 10 | CCPS modified droplet-size correlation and DNV droplet theory | DNV droplet size theory PDF (located, text not read) | rainout prediction instead of an input | located |
| 11 | Fauske and Leung runaway vent-sizing papers; DIERS manual | AIChE / DIERS | two-phase runaway relief | not searched |
| 12 | CoolProp CO2 real-fluid properties wired into a decompression check | CoolProp (already a dev-time dependency) | CO2 pipeline screening | available, not built |
| 13 | NIST carbon-steel low-temperature data or ASME MDMT curves | NIST; ASME VIII UCS-66 | cryogenic spill and MDMT checks | needed |
| 14 | UL 9540A test reports for the actual battery product | vendor | battery vent-gas source term | project-specific |
| 15 | Site data: wind rose and stability, occupancy and population, ignition-source density, equipment inventory, P&IDs | the site | any QRA beyond generic screening | project-specific |
| 16 | OISD-GDN-192 numeric requirements (for example test-pressure factors, scaffold loads, excavation limits) | the supplied copy, after checking the OCR against the page images | construction-phase checkers with inputs taken from a read source | OCR done, values not yet extracted or verified |

## D. What the supplied OISD-STD-118 deck contributes

It is a training presentation of Rev 3 (June 2025), not the standard, so treat its numbers as pointers to check against the standard. Stated in it:
the standard applies from 1000 KL aggregate storage upward (below that, inter-distances follow risk assessment); installations that do not meet it need a detailed QRA
and board approval submitted to OISD; flare sterile radius 90 m, reducible to as little as 60 m by an API 521 thermal radiation study; dyke enclosure capacity
120,000 m3 (floating roof) and 60,000 m3 (fixed roof); oily-water sewer pits at least 30 m from fired equipment (15 m if covered and vented); no trenches or pits within
15 m of furnace walls; 12 inter-distance tables, 24 facility types, 29 notes to Table 1. None of these is coded as a default. They would become inputs to a
layout checker once Tables 1-12 are in hand.

## E. Further sources found 2026-11-07 (searched, not downloaded unless stated)

**OISD, official routes (oisd.gov.in).** Corrects the earlier note that no official route existed.
* [Purchase of Standards](https://oisd.gov.in/purchase-of-standard): latest editions (August 2026) for industry and individuals, Rs 10,000 + GST (Rs 10,500) per standard or Rs 2,00,000 + GST (Rs 2,10,000) for the full set; register on the site, pay online; access through the "OISD Standard Access" customer login.
* [Standards for Public Comments](https://oisd.gov.in/oisd-standards-for-public-comments): free drafts: STD-246 Compressed Biogas plants (comments by 9 Nov 2026), STD-134 Inspection of Heat Exchangers (9 Nov), STD-113 Classification of Areas for Electrical Installations (14 Nov), STD-235 Aviation Fuelling Stations (3 Dec). PDFs are 1.4 to 2.3 MB.
* [Suraksha Samwad](https://oisd.gov.in/suraksha-samwad): 36 free presentations (layouts STD-118, revised STD-116 June 2025, incident case studies, incident-reporting changes, DMP changes).
* [Errata and Updation](https://oisd.gov.in/errata-and-updation): errata for STD-114, 117, 142, 164, GDN-166, 200, RP-158. Also Safety Alerts, Case Studies and Working Group Report pages (not read).
* [Standards in statutory regulations](https://oisd.gov.in/list-of-oisd-standards-in-various-statutory-regulations) (page dated 2 Sep 2026, read): Petroleum Rules 2002: STD-105, 116, 117, 118, 141, 156; Gas Cylinder Rules 2016: STD-144, 169; Static and Mobile Pressure Vessels (Unfired) Rules 2016: STD-150; Oil Mines Regulations 2017: 16 standards (RP-108, STD-114, 116, 117, 118, 128, 129, 141, RP-149, RP-174, GDN-178, 182, STD-187, 189, 191, GDN-226). This agrees with OISD's 2020 letter (its ten refinery-relevant statutory standards are a subset).

**PNGRB regulations (free, official, pngrb.gov.in).** [Notified T4S regulations](https://www.pngrb.gov.in/eng-web/regulation-t4s.html): 104 PDFs including Petroleum Refineries and Gas Processing Plants (original 3 Apr 2023; amendments 23 Jul 2025 and 16 Jan 2026; consolidated 18 Feb 2026), LNG, LPG, Petroleum Installations (amended 17 Aug 2026), retail outlets, CGD, natural gas and petroleum pipelines, IMS and ERDMP. These reference OISD and API standards by clause; text not yet read.

**Other free or partly free sources (from searches; availability not tested).**
* [API IBR Reading Room](https://www.api.org/products-and-services/standards/ibr-reading-room): free read-only view of about 200 standards incorporated into US regulation; no download or print; whether 520 or 521 are included was not confirmed.
* [NFPA free access](https://www.nfpa.org/codes-and-standards/resources/free-access) (free account, read-only): NFPA 59A, 68, 69 and 855 availability not confirmed.
* [IOGP Report 434-01 process release frequencies](https://www.iogp.org/bookstore/product/risk-assessment-data-directory-process-release-frequencies/): listed as free (name and email); the 434 series also has ignition probabilities (434-06, access unclear), storage incident frequencies and vulnerability of humans.
* [Standards Norway NORSOK](https://standard.no/en/sectors/petroleum/norsok-standards/): free overview list; full texts paid (HSE-related ones free to unions and safety representatives).
* [Public.Resource.Org BIS standards](https://law.resource.org/pub/in/bis.gov.in.20230601.pdf) and BIS (reported to make Indian Standards free for non-commercial use since 2022, to verify): relevant to the BIS codes listed in OISD-GDN-192 Annexure I.
* PESO: [Petroleum Rules, SMPV(U) and Gas Cylinder Rules pages](https://www.peso.gov.in/en) and circulars.
* Not worth using: Scribd and pdfcoffee uploads of OISD documents (unofficial, edition unknown, often "restricted circulation"), netlify.app "free download" pages (spam).
* Not found: DNV recommended practices download terms; free copies of EN 1993-1-2; NFPA 59A/68/69/855 free-access confirmation.

**Downloaded 2026-11-07 (free public-comment drafts, "for restricted circulation only" on the cover, not for reproduction; kept outside the repo).**
OISD-STD-246 CBG plants (81 pages: design requirements, fire protection, operation and maintenance, emergency plan, annexures on digester system, safety studies, upgrading technology and audit checklists); OISD-STD-134 heat exchanger inspection (76 pages); OISD-STD-113 hazardous-area classification, revised edition (66 pages; clause 6 "Extent of Hazardous Area" is the part the toolkit lacks); OISD-STD-235 aviation fuelling stations (133 pages). All have text layers. They are drafts, so any value taken from them must be re-checked against the final edition.

## F. Sources from Kaggle, GitHub and other open repositories (searched 2026-11-07)

Provenance caution: a saved preference says to favour official exchange or regulator sources over redistributed dataset dumps; Kaggle is listed here only because it was asked for. No Kaggle dataset could be confirmed (the search tool does not index Kaggle well), so everything below is from official or institutional hosts.

| Need | Source | Access and licence | Note |
|---|---|---|---|
| Process-safety incident records | [eMARS (EU JRC)](https://emars.jrc.ec.europa.eu/) and the [JRC list of open chemical-accident databases](https://minerva.jrc.ec.europa.eu/en/shorturl/minerva/chemical_accident_databases) | free; query results download as Excel; site names withheld | strongest open option; ARIA (France) hosted via the JRC |
| Major-accident reference set | [Zenodo record 20010231](https://zenodo.org/record/20010231) (15 catastrophic incidents 1984-2022, JSON) | open (licence not read) | small; mirrored on Hugging Face |
| Industrial incident sample | a Kaggle set of 425 incidents from 12 plants in South America cited by a 2024 study | not located | find on Kaggle directly; provenance unknown |
| Pipeline incidents | PHMSA incident data via [data.gov listing](https://catalog.data.gov/dataset/pipeline-incident-flagged-files) and the PHMSA data pages; [unified PHMSA and DOE OE-417 set](https://ieee-dataport.org/documents/phmsa-oe-417-unified-incident-dataset-v10) (12,935 records, CC BY 4.0); [offshore pipeline incidents, OSTI](https://www.osti.gov/biblio/2280823) (900+ incidents 1986-2021) | free | feeds `qra` frequencies; US-only |
| Fault detection and process upsets | Tennessee Eastman data: [DTU extended reference data](https://data.dtu.dk/articles/dataset/Tennessee_Eastman_Reference_Data_for_Fault-Detection_and_Decision_Support_Systems/13385936) (28 faults, 6 modes, 500 runs each); GitHub [multi-mode TE datasets](https://www.github.com/Lichen0102/Multi-mode-Fault-Diagnosis-Datasets-with-TE-process) and [new_tep_datasets](https://github.com/anasouzac/new_tep_datasets); [IEEE DataPort TEP](https://ieee-dataport.org/documents/tennessee-eastman-process-dataset) | free | simulation benchmarks, not plant incidents |
| Hydrogen jet-flame validation | [BAM jet-flame data, TU Berlin DepositOnce](https://depositonce.tu-berlin.de/items/67478559-f808-4d03-bc23-955980e2d781) (hydrogen and methane, CSV per series) | open | candidate to validate `jet_flame` against measured data |
| Liquid-hydrogen dispersion and rainout | [PRESLHY HSE rainout tests, KIT RADAR](https://radar.kit.edu/radar/en/dataset/nWczysTWjmuzgFKm) (DOI 10.35097/1481) | CC BY-SA 4.0 | useful for rainout validation of `expansion` |
| LNG dispersion and spill data | none found on Zenodo, figshare or Mendeley; Burro, Coyote and Maplin Sands remain in published reports | n/a | Hansen et al. (2010) is the lead |
| GitHub process-safety code | no process-safety repositories turned up for HAZOP, LOPA or QRA beyond those already in `docs/SIMULATION_TOOLS.md` (HyRAM+, PFTA, GasDispersion.jl, DEGADISx, pyBNBowTie, BayesianSafety); [Kenexis Open PHA](https://www.kenexis.com/software/openpha/) is free to use but not open source | mixed | a direct GitHub topic search was not possible with this search tool |
| US incident data (RMP accident history, OSHA severe injury, CSB) | not found in this search | public downloads exist from general knowledge, not verified | needs a follow-up check |

## G. Extraction plan and status (2026-11-07)

Rule used: statements, tables and figure labels from these documents go to the gitignored `standards_private/` folder on this machine, not into the repository. The repository records structure, counts and what each document can unlock.

| Step | What | Status |
|---|---|---|
| 1 | Extract every "shall", "should" and prohibition sentence from the four OISD drafts (STD-246, 134, 113, 235) and OISD-GDN-192 with `python -m process_safety requirements` | **done**: 2,941 statements in `standards_private/oisd_drafts_and_gdn192.csv` (STD-246 510, STD-134 465, STD-113 181, STD-235 1,025, GDN-192 760); 1,776 mandatory, 134 prohibitions; 2,274 not matched to a recommendation type |
| 2 | Pull the statements that carry a number and a unit | **done**: 165 in `standards_private/oisd_numeric_requirements.csv` (STD-246 38, STD-134 17, STD-113 9, STD-235 73, GDN-192 28). Sentence extraction misses values held in tables and figures, so this is a floor, not the full set |
| 3 | STD-113 extent-of-hazardous-area values, which sit in Figures 1 to 17 (heavier and lighter than air; tanks, spheres, bullets, compressor shelters) | **partly done**: pages 32 to 47 rendered and OCR'd to `standards_private/private_oisd113_figure_dimensions.txt`. The OCR is noisy (for example "45m" for what is probably 4.5 m, and one garbled value), so none of it is trustworthy until checked against the page images |
| 4 | Verify the figure dimensions by eye against the page images, or against the final STD-113 edition after the comment period (closes 14 Nov 2026) | not done; needs a person or the purchased edition |
| 5 | Map the extracted statements to toolkit modules: STD-113 to `atex` and `flammability` (zone extents), STD-246 to the `biogas-cbg` scenario entry and CBG checklists, GDN-192 to a construction-safety scenario entry, STD-235 to a fuelling-station entry | not done |
| 6 | Build input-driven checkers (extent look-ups, CBG plant audit checklist, construction permits checklist) whose limits come from a verified copy you supply | not done; blocked on step 4 |
| 7 | Buy or register for the final editions (STD-118 Tables 1 to 12, STD-113, STD-116, STD-246) at oisd.gov.in | your decision |

Caveats: the four drafts are drafts; GDN-192 text is OCR; the sentence extractor classifies by keywords and quotes sentences that only describe a requirement.


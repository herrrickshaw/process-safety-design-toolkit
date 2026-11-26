
```markdown
# DATA_SOURCES

This toolkit ships screening calculators and small reference tables. It is not a safety case. Paywalled standards were not read
(see SOURCES.md for the constant-by-constant ledger and confidence). Dates are fetch dates unless stated.

## Reference tables in process_safety/data/

### un_states.json, country_safety.json
- State list: https://www.un.org/en/about-us/member-states and https://unstats.un.org/unsd/methodology/m49/overview/ (fetched 2026-11-25).
- Standards bodies not found by search: acronym and ISO status from https://en.wikipedia.org/wiki/Countries_in_the_International_Organization_for_Standardization (read 2026-11-25, CC BY-SA; facts only).
- Laws: web-search result listings gathered on 2026-11-25; pages not opened. Method: `scripts/build_country_safety.py`, `scripts/check_country_coverage.py`.

### standards_library.json, design_recommendations.json
- Content: index of document designations, titles, publishers, links and link-check results; and a reading map by design activity. Facts only; no standard text is reproduced.
- Sources: publisher, regulator and rights-holder pages. ASTM titles were read from store.astm.org pages on the `checked` date; titles marked `title_source: compiler` were typed and not compared with the publisher. ASTM and other designations and marks belong to their owners; their listing is not an endorsement.
- Digital Refining article rows (`title_source: search-listing`) come from web-search results; the site's robots.txt disallows Claude agents, so its pages were not requested.
- Method: `scripts/build_standards_library.py`, then `scripts/check_standards_library.py` (and `--pdf`).

### oisd_standards.json
- Publisher: Oil Industry Safety Directorate (OISD), MoPNG. URL: https://www.oisd.gov.in/oisd-standards (fetched 2026-09-21, re-checked 2026-11-03; the URL redirected to a "resource not found" page on 2026-11-08 - recheck)
- Content: 105 standard numbers, titles, editions (facts only; standard text is not reproduced).
- Licence: Government of India publication, no open licence stated.
- Method: HTML fetched with curl and parsed.

### oisd_refinery_scope.json
- Publisher: OISD. Document: letter OISD/ENGG/GEN/22 to PNGRB, 30 Apr 2020, Annexure A, https://www.pngrb.gov.in/pdf/public-notice/RGP19052020/OISD.pdf
- Content: 60 standards the letter lists as applicable to refineries/gas processing, 10 flagged statutory; titles matched to the official list (14 not found in the 2026 list).
- Licence: Government of India document. Scope cell text is shortened to a pointer in future revisions.

### osha_psm_appendix_a.json, epa_rmp_substances.json
- Publisher: US OSHA (29 CFR 1910.119 App. A, https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119AppA) and US EPA (40 CFR 68.130 Tables 1 and 3 and App. A, Cornell LII eCFR copy), fetched 2026-11-03.
- Content: 134 and 77+63 substances with threshold quantities (lb) and toxic endpoints (mg/L). US federal regulation, public domain.
- Caveat: OSHA list completeness to confirm; mixture rules simplified.

### seveso_iii_annex_i.json
- Publisher: European Union, Directive 2012/18/EU Annex I (CELEX 32012L0018), EU Publications Office, fetched 2026-11-03. Reuse: Decision 2011/833/EU, attribution "(c) European Union, https://eur-lex.europa.eu".
- Content: Part 1 (21 categories) and Part 2 (38 of 48 named substances). Rows with unparsed thresholds omitted; Annex amendments after 2012 not applied.

### fluid_screening.json
- Generated with CoolProp 8.0.0 (MIT; Helmholtz-energy equations of state) on 2026-11-06; saturated-liquid properties and HEM mass-flux for 18 fluids. Screening data only.

### incidents.json
- Publisher: US Chemical Safety and Hazard Investigation Board investigation pages (https://www.csb.gov/), read 2026-11-06. Facts as stated by CSB; lessons and design-step mapping are the toolkit's own. Deaths unknown for 6 entries.

### incident_casebook.json
- Historical incident cases for teaching, compiled 2026-11-26 from pages and documents fetched and read by research agents (official reports, professional and journal sources, and secondary pages; some through archive copies or third-party mirrors). Each case lists its sources with a grade. At compile time a script required an exact quote from the saved text for each date, cause and stated death toll; the quotes and page texts are not committed. All prose is the toolkit's own.

### legal_clauses.json
- 46 provisions (India, Australia, Singapore, Canada, South Korea and others) paraphrased from the cited statutes/regulations; each entry has the instrument, provision, grade (A = text read, B = secondary) and URL. Not legal text; check the current consolidated version.

### modelling_map.json, modelling_studies.json
- Map: bibliographic records harvested on 2026-11-26 by `scripts/harvest_modelling_literature.py` from the OpenAlex, Crossref, DOAJ, HAL, DataCite and OSTI APIs without keys (OpenAlex stopped when the free daily allowance ran out). Title, authors, year, venue, identifiers and links come from those catalogues; tool and study tags are rule matches on title and abstract (`process_safety/modelling_tags.py`). Abstracts are not committed. Records were not read and links were not checked.
- Study sheets: paraphrases of openly fetched works read by AI research agents. `scripts/build_modelling_literature.py` required an exact quote from the saved text for each tool, step, choice, validation, sensitivity and limitation entry, before audit corrections. Quotes and source texts are not committed. Audit status is in the document.

### lng_analogs.json
- Source: ORIMIZ-Consulting/open-fel1-lng-cost, data/public_analogs.csv (Haider 2026), commit 4ed065a, MIT licence (full notice in THIRD_PARTY_NOTICES.md). Underlying figures come from company announcements and OIES NG137 (Songhurst 2018).

### literature.json, scenario_library.json
- Pointer lists and qualitative scenario text built from search-engine summaries and public pages; `read` and `grade` fields state how much was actually read. Not a substitute for the source documents.

## Constants in code
Equations and coefficients in process_safety/*.py are derived from first principles, textbooks or open literature and marked in SOURCES.md
(high / medium / low-medium). API Std 2000 5th ed. (1998) tables 2B, 3B, 4B are reproduced in tank_venting.py for screening, from the publicly
posted copy (https://law.resource.org/pub/us/cfr/ibr/002/api.2000.1998.pdf); (c) American Petroleum Institute; the current edition differs.

## Not included, by policy
Licensed standards text (API, NFPA, IEC, ISO, EN, ASME), vendor datasheets, client documents, and any OISD document marked for restricted
circulation. Notes derived from such documents stay in a private folder (standards_private/, ignored by git).

## Third-party code
.claude/skills and .claude/references: addyosmani/agent-skills (MIT, fetched 2026-11-06) - see THIRD_PARTY_NOTICES.md.
```

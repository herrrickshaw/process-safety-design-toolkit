# Process safety management frameworks: what each is, and how this toolkit uses it

Compiled 2026-11-03 from public documents (fetched and read, except where noted). Summaries are the author's; see the sources for the text.

| Framework | What it is | Structure | Use here |
|---|---|---|---|
| [OSHA 29 CFR 1910.119](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) (US law) | Regulation for highly hazardous chemicals | 14 elements, paragraphs (c)-(p), plus Appendix A threshold list | `psm.OSHA_ELEMENTS`, cadences, applicability, `data/osha_psm_appendix_a.json` |
| [AIGA 99/20](https://asiaiga.org/uploaded_docs/en_AIGA_99_20_Process_Safety_Mangement.pdf) | Industry guideline (industrial gases), four groups: leadership, risk identification, risk management, review and improvement | 21 elements | `psm.AIGA99_ELEMENTS`, crosswalk, gap scoring |
| CCPS Risk Based Process Safety | Industry framework (book; paywalled) | 20 elements in 4 pillars | `psm.RBPS_ELEMENTS` (titles from published literature) |
| [CSChE PSM Standard, 1st ed.](https://www.cheminst.ca/wp-content/uploads/2019/04/PSM20Standard20first20edition-1.pdf) | Canadian voluntary standard from the MIACC guide | each element has "required elements" and "recommended guidelines" | reference for how to separate mandatory from recommended practice |
| [DOE-HDBK-1101-96](https://www.energy.gov/documents/doe-hdbk-1101-96) | US DOE handbook on PSM for highly hazardous chemicals | element-by-element guidance, audit forms (exhibits incl. a sample PSM audit report) | audit/checklist design reference |
| [India: process safety regulations overview](https://www.sigma-hse.co.in/news/process-safety-regulations-in-india) | Consultancy article: India has no single PSM regulation | MSIHC Rules 1989; Chemical Accidents (EPPR) Rules 1996; Petroleum Rules 2002; Explosives Rules 2008; Gas Cylinders Rules 2016; SMPV(U) Rules 2016; Ammonium Nitrate Rules 2012; Factories Act and state rules; Environment (Protection) Act | scope map; the Indian rules themselves are not implemented |
| EU Seveso III (Directive 2012/18/EU) | Major-accident hazards law | Annex I qualifying quantities, sum rule, lower/upper tier | `mah.classify`, `data/seveso_iii_annex_i.json` |
| US pipeline safety (49 CFR 192) | Gas pipeline design and integrity | design formula, design factors, class locations, HCA | `pipeline.*` |

**Not read:** the Purdue "Global Process Safety Regulations" slide deck (retrieval returned no text) and the synergenog "14 elements" page (the site blocks automated access; not retried). No content from them was used.

**What the PSM module does and does not do.** It encodes the cadences and thresholds that are unambiguous in the OSHA text, tracks due dates, and
scores a self-assessment against the 14 (or 21) elements. It cannot assess the quality of a PHA, a procedure, or a management system:
that is audit work (see the DOE handbook's audit guidance and your own regulator's requirements).

# Literature and tool survey: sources and methods that could close the large deviations

Run 2026-11-10 (web and GitHub searches; access checked with HTTP requests, nothing downloaded). **None of the listed documents has been read yet** unless the manifest says `read`: what each offers below comes from search results, repository descriptions and publisher abstract pages, so treat it as a lead, not a finding. Machine-readable list: `docs/literature_manifest.csv` (36 rows); fetch script: `scripts/fetch_open_sources.py` (dry run by default; writes outside the repository). Access words: *free* = openly downloadable, *bot block* = the publisher refused an automated request, open the link in a browser (not bypassed), *paid* = purchase.

## 1. What each large deviation needs, and where to look

| Deviation (docs/INVERSE_ANALYSIS.md) | Candidate fix | Sources and tools | Expected direction |
|---|---|---|---|
| Flame length +25 to +85 % against visible length; SEP 19 to 27 % low | A jet-fire model with buoyant lift-off and a better flame-shape and area; a documented visible-length definition | HSE RR1229 (revised fireball and jet fire models, 2023), RR1188 (model performance), RR1196 (radiation review); Hankinson and Lowesmith 2012; Palacios and Casal thesis; Carsley occurrence contours | Shorter horizontal reach and smaller area, which raises SEP |
| SEP model 9 to 11 % above DNV Phast | DNV intermediate values (area, Fs, W2) | DNV (request); HSE RR1196 for Fs treatment | One constant factor of about 0.905 |
| Small gas-fed jets: Fs 3 to 4.5 times high | A regime switch for small, gas-fed flames | Gomez-Mares 2010 (read); Palacios and Casal thesis; TU Berlin propane dataset | Fs about 0.07 instead of 0.2 to 0.3 below large-flame sizes |
| Line-fed rate: AA 3029 -14 %, JIVE 8051 +517 % | Delayed-equilibrium or omega pipe model in place of HEM; measured near-orifice pressure | DEM papers (CNS, De Lorenzo benchmark, Polimi); Leung omega method (OSTI); Hebrard and Lacome 2008 (INERIS LPG data) | DEM flashes later than HEM, so more flow: the right direction for the propane tests |
| Droplet size at STEP | Phase III tri-linear correlation and the INERIS tests | Kay, Bowen, Witlox 2010; Witlox papers (read); Coldrick 2016; INERIS AMS papers | Pressure dependence of the flashing regime |
| Fire-case relief, vessel failure under jet fire | Jet-fire heat-flux categories, depressurisation targets, vessel heat-up | Scandpower guideline v2; Energy Institute severe-fire guideline (paid); HSE OTO 2000 051; Andreasen 2018; Moodie 1987 | Larger design heat flux than API 521 pool fire |
| BLEVE fireball choice | Static versus dynamic fireball | HSE RR1185; Roberts, Gosse, Hawksworth 2000 (xv-paper-09) | Peak SEP earlier than the static model |

## 2. Sources by topic (verified access)

### Jet fire models and radiation
| Source | Access | Check | Priority |
|---|---|---|---|
| [HSE RR1229, Revised fireball and jet fire models for pipelines](https://www.hse.gov.uk/research/assets/docs/rr1229.pdf) | free | 200 PDF, 2.0 MB | 1 |
| [HSE RR1196, Radiation calculations for fireball and jet fire models: literature review](https://www.hse.gov.uk/research/assets/docs/rr1196.pdf) | free | 200 PDF, 0.7 MB | 1 |
| [HSE RR1188, Jet fire modelling for pipelines Part 2, model performance](https://hse.gov.uk/research/rrhtm/rr1188.htm) and [RR1187 Part 1 literature review](https://hse.gov.uk/research/rrhtm/rr1187.htm) | free | 200 | 1 and 2 |
| [Hankinson and Lowesmith 2012, methods of determining the radiative characteristics of jet fires](https://repository.lboro.ac.uk/articles/A_consideration_of_methods_of_determining_the_radiative_characteristics_of_jet_fires/9243536/files/16827371.pdf) (Loughborough repository) | free | 202 bot challenge: open in a browser | 1 |
| [Carsley, flame occurrence from video (IChemE SS 139)](https://www.icheme.org/media/25322/major-hazards-onshore-and-offshore-ii-icheme-symposium-series-139-1995-14-carsley.pdf) | free | 200 PDF, 6.7 MB | 2 |
| [Palacios and Casal, Study of jet fires geometry and radiative features (UPC thesis)](https://upcommons.upc.edu/entities/publication/13117a01-4c71-4665-a9ac-dd31dc6861e0) | free | 418 bot check: open in a browser | 2 |
| [TU Berlin DepositOnce: Versuchsdaten Freistrahlflammen (propane CSV series)](https://depositonce.tu-berlin.de/items/67478559-f808-4d03-bc23-955980e2d781) | free dataset (confirm licence) | 200 | 2 |
| [RIVM 620550005](https://www.rivm.nl/bibliotheek/rapporten/620550005.pdf), [DNV JFSH validation](https://myworkspace.dnv.com/download/public/phast/technical_documentation/07_fire_models/JFSH%20Jet%20Fire%20Model%20Validation.pdf), [Johnson et al. IChemE XII-09](https://www.icheme.org/media/12116/xii-paper-09.pdf) | free | in hand, read | 0 |

Not available openly: Barker (Shell 1993, 1994) and Cracknell (Shell 1996) are confidential Shell reports; Cook et al. (1990) and Chamberlain (1987) are paid articles.

### Flashing releases, discharge and droplets
| Source | Access | Check | Priority |
|---|---|---|---|
| [Hebrard and Lacome 2008, evaluation of two-phase flow models for accidental release (INERIS, HAL)](https://hal-ineris.archives-ouvertes.fr/ineris-00973315) | free | 200 bot challenge: open in a browser | 1 |
| [Delayed equilibrium model and validation experiments for two-phase choked flows (CNS)](https://proceedings.cns-snc.ca/index.php/pcns/article/download/4576/4575/4611) | free | 200 PDF, 1.6 MB | 1 |
| [DEM extension to organic fluids (Politecnico di Milano, open access)](https://re.public.polimi.it/retrieve/c312af2f-dfad-4271-83eb-909b0bd1a200/J13%20-%20IJMF2024_DEM.pdf) | free | 403 bot block: browser | 2 |
| [De Lorenzo et al., DEM benchmark against 450 points (IJMF 2017)](https://researchportal.ip-paris.fr/en/publications/benchmark-of-delayed-equilibrium-model-dem-and-classic-two-phase-/) | landing page, full text to check | 200 | 2 |
| [Leung, The omega method for discharge rate evolution (OSTI)](https://www.osti.gov/biblio/255386) | free | 200 | 2 |
| [Witlox, Harper, Oke, Hazards XXI paper 88](https://www.icheme.org/media/9584/xxi-paper-088.pdf) | free | 200 PDF | 1 (owner copy) |
| [INERIS large-scale flashing releases, 64 propane and 30 butane tests (AMS 147092)](https://ams.confex.com/ams/pdfpapers/147092.pdf) and [AMS 160460](https://ams.confex.com/ams/pdfpapers/160460.pdf) | free | 200 PDF | 2 and 3 |
| [Coldrick 2016, small-scale flashing propane jets (Chem Eng Trans 48)](https://www.aidic.it/cet/16/48/013.pdf) | free | 999 bot block: browser | 2 |
| Kay, Bowen, Witlox 2010 (J Loss Prev Process Ind 23:849) | paid | search by title; DOI not confirmed | 1 |

### Vessels, relief and fire protection
| Source | Access | Check | Priority |
|---|---|---|---|
| [Scandpower, Guidelines for protection of pressurised systems exposed to fire v2 (2004)](https://www.iomosaic.com/diersweb/docs/Scandpower%20Fire%20Guidelines%20Version%202.pdf) | third-party mirror, authorisation unconfirmed | 200 PDF, 0.75 MB | 1 (obtain from Scandpower or Lloyd's Register if possible) |
| Energy Institute, Guidelines for the design and protection of pressure systems to withstand severe fires (2003) | paid | not checked | 1 |
| HSE OTO 2000 051, response of pressurised process vessels to fire attack | free from HSE; official URL not confirmed (the guessed one returned 404) | not found | 1 |
| [Moodie et al., 5 tonne LPG tank engulfment (IChemE SS 102)](https://www.icheme.org/media/25216/hazards-from-pressure-icheme-symposium-series-102-1987-17-moodie.pdf) | free | 200 PDF, 12 MB | 2 |
| [Roberts et al., xvi-paper-15 deluge](https://www.icheme.org/media/10160/xvi-paper-15.pdf), [xv-paper-09 fireballs](https://www.icheme.org/media/10224/xv-paper-09.pdf) | free | 200 PDF | owner copies |
| [Andreasen et al., relief valve sizing for gas-filled vessels in fire (Safety 4(1) 11, MDPI)](https://mdpi.com/2313-576X/4/1/11) | free, open access | 403 bot block: browser | 2 |
| [HSE RR1185, fireball models and data: literature review](https://www.hse.gov.uk/research/rrhtm/rr1185.htm) | free | 200 | 2 |

## 3. Software and data tools for the repository

The toolkit stays standard-library only; external tools are optional cross-checks in `tests/crosscheck` or independent references.

| Tool | Licence (GitHub) | Role | Use under the repo rules |
|---|---|---|---|
| [NeqSim](https://github.com/equinor/neqsim) (Equinor, Java; [documentation](https://equinor.github.io/neqsim/safety/dispersion_and_consequence)) and [neqsim-python](https://github.com/equinor/neqsim-python) | Apache-2.0 | Equation of state with phase equilibrium; its safety package lists JetFireModel (API 521 6.4.4, Chamberlain), PoolFireModel (API 521 6.4.3), BLEVECalculator (Yellow Book) and vessel depressurisation with Scandpower jet and pool fire presets | Second route for jet fire, pool fire, BLEVE and the real-gas flux; optional cross-check script |
| [CoolProp](https://github.com/CoolProp/CoolProp), [fluids](https://github.com/CalebBell/fluids), [thermo](https://github.com/CalebBell/thermo) | MIT | Properties, API 520 relief, fittings, friction | Already used |
| [teqp](https://github.com/usnistgov/teqp) (NIST) and [thermopack](https://github.com/thermotools/thermopack) (SINTEF) | NIST and "other" (read the licence before use) | Equations of state for the Annex B flux integration and the DEM | Candidates; check licence terms |
| [HyRAM+](https://github.com/sandialabs/hyram) (Sandia) | GPL-3.0 | Open consequence models, hydrogen focus, jet-fire and radiation implementations | **External cross-check only; GPL, so no code may be copied** |
| pypws (PyPI) | client for DNV Phast Web Services | Gives access to DNV's DISC, UDM and jet-fire models if a DNV licence exists | Needs a DNV account; would settle the 0.905 factor directly |
| [slabx](https://github.com/lyullee/slabx), [degadisx](https://github.com/lyullee/degadisx) | NOASSERTION, zero stars | Unvetted Python reimplementations of SLAB and DEGADIS | Do not rely on them; use the original EPA/Havens codes for dispersion |
| EFFECTS (GexCon), Kenexis Consequence Modeling, Phast | commercial | Validated consequence tools | Paid; see `Resources` in the calculation workbook |

## 4. Ranked list of fixes to try next (all unproven)

1. **Delayed-equilibrium option in `line_flow`** (sources: DEM-CNS, De Lorenzo benchmark, Hebrard and Lacome). Tests: AA 3026, 3029, JIVE 8051. It is the only candidate that moves the propane rates the right way (HEM under-predicts them by 9 to 14 %).
2. **HSE RR1229 and RR1188**: compare their revised jet-fire geometry with `jet_flame`; if open equations exist, implement lift-off and area; judged against the DNV Table 13 and RIVM outputs.
3. **Small-flame regime switch for the radiant fraction** from Gomez-Mares 2010 and the TU Berlin propane data.
4. **Phase III droplet correlation** (Kay et al.) plus INERIS and Coldrick data; keep the Weber branch for sub-cooled releases.
5. **NeqSim cross-check script** for API 521 jet and pool heat input, BLEVE and the Annex B flux (optional, in `tests/crosscheck`).
6. **Scandpower and Energy Institute heat-flux categories** to replace the API 521 pool-fire heat input where a jet fire is the design case.

## 5. Caveats

* Snippet-based: no document in section 2 marked unread has been opened; some titles (CET 48 paper 012, CET 26 paper 011) are unconfirmed and carry priority 3.
* The Scandpower copy is a third-party mirror; obtain it from the owner organisation before relying on it. Scribd copies of HSE OTO 2000 051 and other reports exist and are not used.
* Open-access status was judged from HTTP responses and publisher pages, not from licence text; a CC licence is not assumed.
* Prices and licence terms of paid items were not researched.

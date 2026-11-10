# Sources for the liquefied-gas leak chain (discharge, droplets, rain-out, jet and pool fire)

Updated 2026-11-10 after the owner supplied the TNO Yellow Book (`TNO-2005-yellow.pdf`, `PGS2-1997-v0.1-physical-effects.pdf`) and the CCPS CPQRA PDF, and after both publishers' official copies were downloaded and found identical to them (same checksums).

**Grades.** A = the standard or book text itself was read. B = a public document that quotes the standard was read. C = a web page or search summary.

## What is now backed by the primary text (grade A)

| Item | Where in the source | Used in |
|---|---|---|
| Jet state after flashing: exit density (2.138), jet velocity (2.139), vapour fraction after flashing (2.140), jet area and radius (2.141) | Yellow Book CPR 14E (2005), ch. 2, section 2.5.3.7 step 1 | `yb_spray.jet_after_flash` |
| Droplet diameter: Reynolds and Weber numbers (2.142), two correlations (2.143a, b), **C_ds = 15 recommended (literature 10 to 20)** | same, step 2 | `yb_spray.droplet_diameter_m` |
| Free-fall velocity (2.145), evaporation coefficient k_B (2.146), droplet temperature (2.147), maximum rain-out droplet (2.148), droplet integration (2.149, 2.150), net mass to air (2.151) | same, step 3 | `yb_spray` |
| Worked butane example with every intermediate value (Table 2.6, section 2.6.3.5) | ch. 2, section 2.6.3.5 | the oracle in `tests/test_source_term.py` (jet state, vapour fraction, droplet diameter, Reynolds number, free-fall speed, droplet temperature within 0.3 K, k_B within 2 %, and zero rain-out all reproduced) |
| Property correlations and constants for **propane and n-butane** (liquid density, vapour pressure, heat of vaporisation, liquid heat capacity, liquid viscosity, surface tension, net heat of combustion 46.013 MJ/kg for propane, boiling points) and for air | Yellow Book Annex "Physical properties of chemicals", annex-47, annex-17, annex-13 | `yb_annex`; the tests reproduce the values the Annex prints at 288.15 K to 3e-4 |
| Pool burning rate m'' = m_inf (1 - exp(-k beta D)) (6.66) and Table 6.5 (LPG m_inf 0.099 kg/m2 s, k beta 1.4; butane 0.078, 2.7); Burgess form with c8 = 0.001 (6.67) | ch. 6, section 6.5.4.2 | `yb_poolfire` |
| Pool flame length L/D = 55 (m''/(rho_a (gD)^0.5))^0.67 (u*)^-0.21 (6.12), characteristic wind (6.14), tilt (6.68 to 6.70) | ch. 6, section 6.5.4.3 steps 3 to 6 | `yb_poolfire` |
| Pool surface emissive power SEP = c3 exp(-c5 D) + c4 (1 - exp(-c5 D)), c3 = 140, c4 = 20 kW/m2, c5 = 0.12 1/m (6.19) | ch. 6, section 6.3.4.6 | `lg_release` (and the toolkit's existing `pool_fire` uses the same constants: **confirmed**) |
| Heat-radiation probit Pr = -36.38 + 2.56 ln(Q^(4/3) t), exposure limited to 20 s, building and clothing ignition at 35 kW/m2, clothing factor 0.14 | Dutch Purple Book (PGS 3, CPR 18E, 1999), eq. 5.4 and notes, section 5.2.3 | `vulnerability` |
| **Primary derivation of the heat probit**: Eisenberg form Pr = -38.48 + 2.56 ln(t q^(4/3)) (4.1) with its Table 4-1 doses; hydrocarbon-fire lethality form Pr = -36.38 + 2.56 ln(t q^(4/3)) (4.5), after Stoll et al.; pain and injury thresholds (Table 3-6: 1.5 kW/m2 pain threshold, 4.7 kW/m2 mean time to pain 14.5 s, 8 kW/m2 lethal within minutes, 700 kJ/m2 for 50 % lethality) | Dutch Green Book, PGS 1 Deel 1A "Effecten van brand op personen" (CPR 16 Deel 1A, December 2003), ch. 3 and 4; Dutch language, downloaded from the PGS publisher | `vulnerability` (variant 'hydrocarbon' default, 'eisenberg' optional); Table 4-1 is the test oracle. Eq. 4.1 reproduces the 50 % doses to 0.2 probit but the book's own 1 % and 99 % doses sit 0.35 to 0.44 probit away from it (the table implies a slope near 2.5), so the tails of the probit are approximate |
| Probit against probability (Table 5.1) | Purple Book ch. 5 | test oracle for `probability_from_probit` |
| Direct ignition probabilities by release rate and reactivity class (Table 4.5); propane and butane are class "average" (Table 4.7) | Purple Book ch. 4, section 4.7.1 | `vulnerability.direct_ignition_probability` |
| Release frequencies per vessel, pipe and pump (Tables 3.3, 3.7 and others) | Purple Book ch. 3 | not yet used by a module (recorded here for the frequency step) |

## Still from public secondary documents (grade B)

| Item | Source | Notes |
|---|---|---|
| Omega-method equations and ISO 4126-10 limits (T/Tc < 0.9, P/Pc < 0.5, omega 0 to 100 at P/Po = 0.9) | Melhem, ioMosaic white paper 2023 (the PDF you sent), eq. 37 to 41 and Table 1 | The Yellow Book does not present the omega method; it cites Leung and DIERS papers. The CCPS Relief and Effluent Handling guideline, which the problem statement names for it, was not supplied. |
| Jet-fire Chamberlain frustum model, SEP cap | DNV, "Theory - Jet Fire" (read earlier, grade B) | the Yellow Book has its own jet-flame models in ch. 6 (sections 6.3.2 and 6.5.3); not yet implemented here |
| Pool spreading law d2r/dt2 = 4 g' h / r - C_T (dr/dt)^2 / h | Basha et al., Chemical Engineering Transactions 31 (2013), quoting Webber et al. (2010) | C_T of order 1e-3 is an input; the Yellow Book ch. 3 spreading model was not used |
| Simple rainout correlations (Kletz, Lautkaski) and their validity range | DNV Phast droplet-size report | now only a comparison beside the Yellow Book method |

## Corrections made after reading the primary text

* The DNV report attributes a critical Weber number of 12.5 to the Yellow Book. The Yellow Book itself writes d = C_ds sigma / (u_f^2 rho_a) with **C_ds = 15** recommended. The tool uses 15.
* The DNV report's Kletz and Lautkaski correlations are not the Yellow Book method. The Yellow Book integrates the droplet evaporation while it falls (2.149, 2.150) and gives a rain-out mass directly.
* Misprints in the Yellow Book found while reproducing its worked example: (2.140) prints (1 + Phi_e) where (1 - Phi_e) reproduces the table; (2.146) prints ln(1 - P_s/P_a), negative, while the example's k_B is positive (the module uses minus that logarithm); the example's "d_M = 47 mm" is 0.47 mm (the zeroth-order result 0.29 mm times the convection factor 1.63) and its quoted Re_d of 3671 does not follow from either. These are recorded in the `yb_spray` docstring. The example also uses the number 1.97e-4, labelled dynamic viscosity, as a kinematic viscosity in Re_f; the choice between (2.143a) and (2.143b) is unaffected.
* Heat of combustion: the Annex net value for propane is 46.013 MJ/kg (the earlier 46.33 was my derivation from a NIST higher value and water's latent heat; replaced).
* LPG pool burning rate: Yellow Book Table 6.5 gives 0.099 kg/m2 s for large pools; Mizner (1982) measured 0.13 for a 20 m propane-propene pool; the Burgess form gives about 0.11 for propane. The tool uses Table 6.5 with the diameter correction.
* **The two discharge bases differ by a factor of four for propane at 12 bar.** The Yellow Book (2.5.3.4) treats a hole in the liquid space as liquid outflow, Bernoulli with the full pressure difference, and flashes the liquid after the exit; the omega method treats the same hole as flashing, choked flow. For the 25 mm hole: 9.87 kg/s against 2.34 kg/s. The tool computes both and lets you choose which drives the fire calculation.

## Files added later (2026-11-10, second batch) and what they gave

| File | What it is | Result |
|---|---|---|
| `chef_manual_v2.0.pdf` | CCPS Chemical Hazard Engineering Fundamentals manual v2.0 (2019), screening methods | **Flash fraction F_V = (T - T_B) C_s / H_V (eq. 27)**, identical to the toolkit's `adiabatic_flash_fraction`. States a critical Weber number "typically 10 to 20" (supports the Yellow Book's 10 to 20 range for C_ds) and that "there is not a completely acceptable method for predicting aerosol evaporation": a common practice is aerosol evaporation of 1 to 4 times the flash fraction. So the Yellow Book integration used by the tool is not the CCPS screening practice; the CCPS shortcut is far more conservative or less, depending on the multiple. Toxic probit only; no ignition table or heat-radiation probit. |
| `prj11100262033_final_report_rev_2021-2.pdf` | Norwegian DSB guideline for QRA of facilities handling hazardous substances (Vysus/DNV, Nov 2021) | Quotes the **same TNO heat probit** as the Purple Book (Pr = -12.8 + 2.56 ln(t q^(4/3)), q in kW/m2, which equals -36.38 + 2.56 ln(Q^(4/3) t) with Q in W/m2) and tabulates 50 % fatality fluxes by duration (610 s at 1.5 kW/m2 down to 28 s at 15 kW/m2), used as an independent test oracle. Recommends assuming no clothing protection. Describes the ignition models in use (RIVM, OGP/UKOOA, MISOF, HyRAM) and says the OGP model sets immediate ignition at 0.001 for all releases; the curves themselves are not tabulated there. |
| `te_994_prn.pdf` | IAEA-TECDOC-994 (1998), integrated risk assessment in large industrial areas | Table IV.2: effects of heat radiation (35, 23, 12.6, 4.7, 2.1, 1.2 kW/m2) on equipment and people, qualitative. An Eisenberg-type probit (different from the TNO probit; gives lower fatality for the same dose). The tool now reports reach to these levels beside the probit levels. |
| `preview-9780470935187_A23942645.pdf` | CCPS Guidelines for Pressure Relief and Effluent Handling Systems (1998), 57-page preview | Front matter, contents and chapter 1 only. The contents page shows "Stagnation Pressure and Critical Pressure Ratio" (page 103) in chapter 2, which is not in the preview. **No omega-method text.** |
| `pdfcoffee.com_guidelines-for-pressure-relief-...pdf` | one page of API 521 (page 220) | mentions that the DIERS Project Manual and the CCPS guideline give guidance on whether two-phase relief occurs; no equations. |
| `Introduction to Process Safety.pdf`, `risk_based_process_safety_overview.pdf`, `francis-stoessel-thermal-safety...pdf` | CCPS introductory and management texts; reaction thermal safety | no ignition, thermal-radiation or two-phase discharge content for this chain (checked by search for the relevant terms). |
| `PGS2-1997-v0.1-physical-effects.pdf` (two copies), `TNO-2005-yellow.pdf`, `PGS3-1999-...pdf`, `Guidelinesforchemicalquantitativeriskassessment.pdf` | already used | the PGS2 and PGS3 files are byte-identical to the publisher copies already read; the CPQRA file is the same 79-page extract (front matter and chapter 1). |

## Third batch: open search for the pending items (2026-11-10)

| Item | Found | Result |
|---|---|---|
| HSE CRR 403/2002 (Witlox and Bowen, review of flashing liquid jets) | The hse.gov.uk path is gone (404); the Internet Archive holds the official PDF (`web.archive.org/web/2016id_/http://www.hse.gov.uk/research/crr_pdf/2002/crr02403.pdf`, 78 pages). Read. | Critical Weber number 10 to 20 is what "all atmospheric dispersion codes" use, but the report **does not endorse it as a correlator of mean droplet size** (it bounds the maximum stable droplet; it is independent of orifice size). DeVaull and King confirmed (eta_R = eta*(1 - (x/0.145)^1.8), eta* = 1 - 2.33 (T_a - T_as)/T_a); Kletz "performs not so well". **EEC STEP propane data**: saturated propane, 2, 5, 8 mm orifices, 5, 11, 17 bar; no droplet above 80 micrometres even closest to the nozzle; SMD 39 to 49 micrometres at 5 bar (60 mm downstream), 30 to 31 at 11 bar, below 30 at 17 bar; "very little if any rainout" expected at 11 bar. Used as the validation set below. |
| UKOOA / Energy Institute ignition look-up curves | IChemE Symposium Series 158 (Hazards XXIII) paper "Practical application of the UKOOA ignition model", open on icheme.org, reproduces all 30 curves (Table 2) and the interpolation equation | New `ignition_ukooa`: log-log interpolation, 30 curves, gas-and-liquid combination rule; tests check Table 1 maxima and the interpolation identities. For the propane example (2.34 kg/s): UKOOA 0.006 to 0.011 total, Cox 0.07 total, Purple Book 0.2 **direct** only; the tool reports all three. The Energy Institute report itself and IOGP 434-06 were not obtained (unofficial copies exist; not used). |
| UK HSE thermal dose criteria (HSL/2004/04) | (superseded: the HSE report was supplied and read; see the fifth batch.) Earlier: The HSE PDF is not retrievable; an ioMosaic paper "Risk-Based Approach - Damage Criteria" (open) tabulates the criteria and quotes HSE | `vulnerability.THERMAL_DOSE_CRITERIA`: 290 escape impeded, 1000 for 1 % fatality, 1800 (public, fireball) and 2000 (offshore) for 50 % [(kW/m2)^(4/3) s]. **The UK 50 % dose is about twice the Dutch hydrocarbon probit's** (1040 at 20 s: 19.5 against 31.6 kW/m2). Reach to these levels is reported beside the probit levels. |
| Leung omega method, CCPS relief guideline | (superseded by the fourth batch: Leung's 1996 article is on the owner's Drive and was read.) Earlier: only citations: Leung, Chem. Eng. Progress 92(12), 28-50 (1996); IoMosaic DIERS bibliography; a vendor sheet reproducing API 520 Annex C section headings (equations are images, not extractable) | still no primary text for omega; the API 520 scenario list confirms saturated liquid propane entering a PRV and flashing is the omega method's case 1 (methods C.2.1 or C.2.2). |
| Other candidates found, not used | Energy Institute and IOGP ignition reports (Scribd, kupdf, docshare copies); ResearchGate pages (login); HSE CRR 403 copies on Scribd | unofficial or behind a login; not used |

### Validation against measurements (EEC STEP propane flashing jets, as reported in HSE CRR 403/2002)

Predicted initial droplet diameter by the tool (Yellow Book 2.143b) against the measured Sauter mean diameter at 60 mm downstream. Pressures taken as absolute; the 5 mm orifice (droplet size in the model does not depend on orifice size once the jet state is fixed by the pressure).

| Storage pressure | Measured SMD | Liquid-orifice basis | Omega basis | CCPS flashing correlation as printed by DNV (not used by the tool) |
|---|---|---|---|---|
| 5 bar | 39 to 49 micrometres | 56 | 19 | 221 |
| 11 bar | 30 to 31 | 20 | 8.7 | 166 |
| 17 bar | below 30 | 12 | 5.7 | 138 |

The Yellow Book formula on the liquid-orifice jet state is within a factor of two of the measured means; on the omega state it under-predicts by two to three times; the CCPS flashing correlation as implemented over-predicts about five times, so it is only a comparison in the tool. Rain-out is zero at 11 bar on both bases, as measured. The measurements are mean sizes after some evaporation, not the initial size, so this is a consistency check, not a calibration; it is encoded in `tests/test_source_term.py` (class `StepValidation`).

## Fourth batch: the owner's Google Drive (2026-11-10)

Searched with the Drive connector (read-only). The Drive holds copies of most files already read, plus the following that were new:

| File on Drive | What it is | Result |
|---|---|---|
| `Easily Size Relief Devices and Piping for Two Phase Flow - JC Leung.pdf` (scanned, a document-delivery copy marked for private study) | Leung, Chemical Engineering Progress 92(12), 28-50, December 1996: the omega-method article | **Primary text for the omega method.** Read from page images (the text layer drops the equations): eq. 28a v/v0 = w (P0/P - 1) + 1; eq. 29a flashing w = x0 v_g0/v0 + (cp T0 P0/v0)(v_fg0/h_fg0)^2; eq. 31 nozzle mass flux; eq. 32 transcendental equation for the critical ratio; eq. 33 G_c = eta_c sqrt(P0 rho0 / w); eq. 35, 36, 37 the limits w = 1 (eta_c = 0.606 for k = 1.001) and w = 0 (Bernoulli). The toolkit's `twophase` equations match these; the tests now check eq. 32 residuals, eq. 33, the limits and eq. 29a (class `LeungOmegaPrimaryText`). The API-style fit of eta_c (two transcriptions disagreeing) is not in this article; the toolkit keeps the exact root. |
| `1999p6.pdf` (Tran and Reynolds, Kaiser Engineers, "Sizing of relief valves for two-phase flow in the Bayer process") | review of API, HEM and slip models | States that DIERS found experimentally observed discharge rates up to **three times** the homogeneous-equilibrium prediction, especially at low pressure, and that HEM is conservative for relief sizing. Supports reporting the omega (HEM-type) result and the liquid-orifice result as a bracket, with the omega result the lower for a discharge release. |
| `two_phase_flow_bibliography.pdf`, `xix-paper-35.pdf`, `DeterminationofTwoPhaseFlowRegimes...pdf`, `IJCHE_Volume 16...pdf`, `Conceptual-design-of-pressure-relief-systems...pdf`, `enghandbook3.pdf` (Crosby) | relief background | not needed for the leak chain; no new constants taken |
| `PGS4-1997-v0.1-probabilities.pdf` | Red Book | on Drive; not used for this chain |
| `Guidelinesforchemicalquantitativeriskassessment.pdf`, `preview-9780470935187...pdf` (and a duplicate) | the same 79-page CPQRA extract and 57-page relief-guideline preview already checked | no new content |

Dropbox: a search for the CCPS relief and CPQRA topics returned only LNG and process-safety guides (`Code-of-Practice-LNG-facilities.pdf`, DEKRA process safety guide); no CCPS chapters. IOGP 434-06, the Energy Institute ignition report, HSE HSL/2004/04, API 520 and the CCPS CPQRA chapters 2 and 5.2.2 are **not** on the Drive.

## Fifth batch: documents the owner supplied after the source list (2026-11-10)

| File | What it is | Result |
|---|---|---|
| `434-01.pdf` | IOGP Report 434-01 v1.1 (May 2021), *Process release frequencies* (62 pages) | **Read.** Leak frequency by hole class (1-3, 3-10, 10-50, 50-150, >150 mm) for 24 equipment types from the UK HSE hydrocarbon release database, two periods. New `release_frequency` module: steel pipes, flanged joints, manual and actuated valves with size-interpolated parameters; power laws for instrument connections, vessels, pumps, compressors, heat exchangers, filters, pig traps and others. The report's own tabulations (sheets 1 to 7, every class and size, both periods) are the test oracle: reproduced within 6 % (one cell 8 %). Found in the report: the vessel sheet for 1992-2015 prints the instrument-connection equation (not implemented), and flexible piping and pipeline ESDV tables disagree with their equations (not implemented). Pipe frequency is per metre year; recommended period 2006-2015. |
| `434-06.pdf` | IOGP Report 434-06 v1.1 (May 2021), *Ignition probabilities* (48 pages) | **Read; this is the primary source for the UKOOA / Energy Institute curves.** All 30 curves in `ignition_ukooa` (first transcribed from a conference paper) were parsed from its Table 3-1 and agree exactly. Guidance now recorded: immediate ignition probability is 0.001 whatever the release size; the curves give total ignition; a sustained jet fire should be assumed whatever the time of ignition; use the gas/LPG curves for a liquid well above its normal boiling point (large plant above 1200 m2 or 35 000 m2 site: curve 8; small plant: curve 5); not valid for LNG or refrigerated condensed gases. Table 2-4 gives the ignition timing distribution. Section 5.3 describes the CCPS ignition model (three levels, modification factors) **without equations**, so the CCPS equations are still missing. |
| `hsl04-04.pdf` | HSE HSL/2004/04, *Human vulnerability to thermal radiation offshore* (O'Sullivan and Jagger, 33 pages) | **Read; primary source for the UK thermal doses.** Table 2: escape impeded 290; 1-5 % fatality offshore 1000; 50 % fatality with radiation to the front or back only (fireball) 1000; 50 % fatality offshore 2000 (LD50, recommended); 100 % 3500 (guiding figure) [(kW/m2)^(4/3) s]. It states that the Eisenberg (1975) and Lees (1994) probits are more optimistic than Tsao and Perry (1979), whose lethality probit is the -36.38 form used as the default here. **A correction:** the earlier note (from a vendor paper) listed a 1800 dose for 50 % fatality of members of the public and for a fireball; the report gives 1000 for a fireball and no public value, so `THERMAL_DOSE_CRITERIA` now carries the report's values only. |
| `tses_article1390b7a.pdf` | Dlabka et al., review of thermal radiation effects on humans, Transactions of the VSB Ostrava 6(2), 2011 | Table 4 lists the lethality probits with constants for q in W/m2 and in kW/m2: Tsao and Perry -36.38 / -12.8 / 2.56; Lees -29.02 / -10.69 / 1.99; Eisenberg -14.9 for kW/m2 (as the IAEA document prints). `vulnerability` now offers the Lees form; the tests check the W/m2 and kW/m2 constants against each other. |
| `xxiii-paper-62.pdf` | Lisbona et al. (HSL), comparative study of flash-fire risk models, IChemE Hazards XXIII | Flash fire only; not used for this chain. |

## Sixth batch: two documents the owner supplied (2026-11-10)

- **RIVM report 620550005/2012**, Kooi and Uijt de Haag, "A comparison of jet fire models for horizontal two-phase and liquid releases" (grade A for the tabulated values, read from the supplied PDF). It compares the Dutch SAFETI-NL model (JFSH-Cook, the family `jet_flame` follows), the Shell Barker (LPG) and Cracknell (generic) models against five experiments. Two are propane LPG (Project AA tests 3026 and 3029, 97 % propane, 52 mm orifice); the others are crude oil (BFETS-2) and butane (JIVE 8051).
  - Table 5 values: test 3026, 16.1 kg/s, expanded velocity 153 m/s (JFSH): measured flame length 31.1 m, JFSH-Cook 38.3, Barker 37.7, Cracknell 34.3; measured surface emissive power 331 kW/m2, JFSH 253; fraction radiated 0.35 JFSH, 0.27 Barker, 0.30 Cracknell. Test 3029, 18.0 kg/s, 146 m/s: measured 30.7 m, JFSH 49.4, Barker 39.4, Cracknell 34.9; measured SEP 294, JFSH 197.
  - Conclusions (section 3.5): Cracknell is the best generic model for flame size and shape; Barker may be better for volatile liquids such as propane; JFSH-Cook better for non-volatile releases; the fraction radiated is uncertain and JFSH-Cook is the most conservative. JFSH-Cook ignores buoyancy.
- **Check of `jet_flame.chamberlain` against Project AA** (not in the toolkit's tests, finding only): run horizontal (angle 0), wind 3.7 and 2.0 m/s, jet velocity from the report, jet density from the toolkit flash, the model gives flame lengths of 55 m (test 3026) and 69 m (test 3029) against measured 31.1 and 30.7 m and JFSH-Cook 38.3 and 49.4. It therefore overpredicts length by about 1.8 to 2.2 times for horizontal two-phase LPG jets. The toolkit's angle factor (1 - 0.00607 (theta - 90)) raises a horizontal flame by 55 %; with the vertical factor the length is 35.6 m. The two-phase Cook modification and buoyancy are not implemented (the model is the pure-vapour Chamberlain form). Surface emissive power comes out at 96 (Chamberlain fraction 0.24) or 139 kW/m2 (Cook fraction 0.35) against measured 331. The worked example in this ledger is a vertical jet, where this bias is not demonstrated, but jet lengths for horizontal or two-phase releases should not be taken from this model without a check.
- **PHMSA-2011-0075-0003, DNV Phast UDM 6.6 validation submission** (DNV to PHMSA, 25 October 2010; grade B, qualitative). It lists what the droplet, rain-out and pool sub-models were validated against (initial droplet size in the droplet JIP, rain-out against CCPS experiments and Phase IV JIP water and xylene, EEC elevated two-phase propane jet for dispersion, PVAP pool spreading for propane and butane) but prints no droplet or rain-out numbers in the parts read, so it adds no new validation data. Useful as a pointer to the DNV droplet papers (Witlox and Bowen 2002; Witlox et al. 2010), which are the sources to obtain next.


### Validation against Project AA propane jets (RIVM 620550005/2012 Table 5; toolkit chain run 2026-11-10)

Conditions: 97 % propane, 52 mm orifice, vessel 7.53 bar(a) at 5.5 C (test 3026) and 7.34 bar(a) at 3.2 C (test 3029), 67 m line, horizontal release, wind 3.7 and 2.0 m/s. The liquid is subcooled by about 2 bar, so the omega (saturated) route does not apply; the Yellow Book liquid route is used. Jet state is computed at the measured release rate.

| Quantity | Test 3026 measured | Barker / Cracknell / JFSH-Cook | Toolkit | Test 3029 measured | Toolkit |
|---|---|---|---|---|---|
| Release rate, kg/s | 16.1 | - | 34 to 55 (orifice, Cd 0.62 to 1) | 18.0 | 34 to 55 |
| Expanded jet velocity, m/s | not reported | 79 / 76 / 153 | 75 | not reported | 74 |
| Flame length, m | 31.1 | 37.7 / 34.3 / 38.3 | 59.6 horizontal factor, 38.5 vertical factor | 30.7 | 73.6, 47.6 |
| Surface emissive power, kW/m2 | 331 | 231 / 178 / 253 | 112 horizontal, 265 vertical | 294 | 97, 232 |
| Droplet diameter, micron | not reported | - | 34 | not reported | 34 |

Reading: (1) the expansion step agrees with the Barker and Cracknell velocities (75 against 69 to 79), not with the DNV JFSH value of 153 m/s. (2) The release rate is over-predicted 2 to 3.5 times because the toolkit has no 67 m line: the real flow is limited by line friction and flashing in the pipe (the orifice would see a pressure below the vapour pressure), and a saturated-liquid-in-a-vessel model cannot reproduce it. Feed the measured rate to the jet steps, as done above. (3) Flame length is over-predicted 1.9 to 2.4 times with the horizontal-release factor; the factor is 1.55 and is the whole discrepancy for test 3026 (38.5 m with the vertical factor, 24 % high). The sign of the horizontal angle correction in DNV eq (4) should be checked against the JFSH document. (4) Emissive power follows the length error: low by 3 times (horizontal factor), low by 20 % (vertical factor). (5) Droplet size of 34 micron is of the same order as the STEP propane measurements (30 to 49 micron) at different conditions.
Not validated: the omega discharge (no experiment here with a short hole and saturated liquid), rain-out and pool fire (no data reported), probit and frequency (not measurable). The vertical-release flame in the leak study therefore has an unquantified bias; the horizontal tests show the model can be 24 % to 2.4 times long depending on the angle factor.

## Still open

| Item | Status |
|---|---|
| CCPS Guidelines for Chemical Process Quantitative Risk Analysis, 2nd ed. | The supplied PDF (twice) has 79 pages: the front matter, contents and chapter 1 (introduction). It contains no ignition-probability tables, no thermal vulnerability criteria, no consequence models. Its only relevant statement is an illustration of an effect-zone criterion at 5 kW/m2 (page of the definitions in chapter 1). Please share chapter 2 (consequence models), section 5.2.2 (ignition sources and data) and the thermal-effects tables, or the whole book. |
| CCPS Guidelines for Pressure Relief and Effluent Handling Systems (Leung omega method) | only the front matter and chapter 1 were supplied (57-page preview); chapters 2 and 3 hold the method. API 520 Part I Annex C is quoted by Melhem and by a calculator page; one transcription of the critical-ratio fit gives 0.806 and the other 0.8127 against the exact root 0.8126; the toolkit uses the exact root. |
| Yellow Book jet-flame models (ch. 6.5.3) and pool spreading (ch. 3) | read only in outline; not implemented. |
| Thermal threshold values 37.5, 12.5, 4.7 kW/m2 (the HSE report and the Green Book now give the dose-based criteria) | no primary source found for those round numbers (the Green Book gives its own thresholds, Table 3-6, and the probit); replaced in the tool by the Purple Book probit levels (1 % and 50 % death for a 20 s exposure: 9.8 and 19.5 kW/m2) and the 35 kW/m2 ignition level; extra levels can still be added as inputs. |
| Energy Institute ignition report (2006, now 2nd ed. 2019) | purchase; IOGP 434-06 reproduces the curves and the guidance (fifth batch) The Purple Book Table 4.5 replaces the Cox values in the tool output; the Cox values remain in `qra.frequency` as a secondary alternative. |

## Results on the worked example (propane, 25 mm, 12 bar(a), saturated liquid, 5 m/s wind), rerun through `tool lgrelease`

| | Omega basis | Yellow Book liquid-orifice basis |
|---|---|---|
| Release rate | 2.34 kg/s | 9.87 kg/s |
| Jet velocity after flashing / vapour fraction | 153.5 m/s / 0.414 | 101.7 m/s / 0.434 |
| Droplet diameter (2.143b) | 8 micrometres | 18 micrometres |
| Rain-out (Yellow Book integration) | 0 | 0 |
| Flame length / SEP | 14.2 m / 189 kW/m2 | 27.8 m / 204 kW/m2 |
| Downwind reach, 1 % death / 50 % death / 35 kW/m2 | 15.4 / 9.9 / 5.8 m | 35.0 / 23.9 / 15.8 m |
| Direct ignition probability (Purple Book Table 4.5, under 10 kg/s, average-reactive gas) | 0.2 | 0.2 |

Refrigerated propane tank (5 m head, 10 kPa(g), 25 mm hole): 2.04 kg/s at 11.5 m/s, droplets 1.4 mm, **rain-out 96 % by the Yellow Book integration**, pool 5.0 m across, flame 10.9 m (tilted 57 degrees at 5 m/s), 90 MW, SEP 86 kW/m2; solid-flame reach from the pool centre 11.6 m (1 % death), 7.2 m (50 %), 4.3 m (35 kW/m2).

Both discharge bases give no rain-out for the hot saturated release, so a pool fire there is a hypothesis (ground impingement) and is evaluated only when `pool.extra_rainout_fractions` is given.

## Source register with links

**Read in full or by section (primary or publisher copies)**

| Source | Link |
|---|---|
| TNO Yellow Book CPR 14E, 2005 second print | https://publications.tno.nl/publication/34634119/QIKv78/TNO-2005-yellow.pdf (same text: https://content.publicatiereeksgevaarlijkestoffen.nl/documents/PGS2/PGS2-1997-v0.1-physical-effects.pdf) |
| Purple Book PGS 3 (CPR 18E) | https://content.publicatiereeksgevaarlijkestoffen.nl/documents/PGS3/PGS3-1999-v0.1-quantitative-risk-assessment.pdf |
| Green Book PGS 1 Deel 1A, effects of fire on people (Dutch, 2003) | https://publicatiereeksgevaarlijkestoffen.nl/documents/81474/1664357365-pgs1-2005-v0-1-deel-1a.pdf |
| HSE CRR 403/2002, flashing liquid jets and two-phase dispersion (archived official PDF) | https://web.archive.org/web/2016id_/http://www.hse.gov.uk/research/crr_pdf/2002/crr02403.pdf |
| Leung, Chem. Eng. Progress 92(12), 1996 (owner's Drive copy, scanned) | https://drive.google.com/file/d/1GRp1fnnpMKwRk0pPIz0Pr5xFl3Efgf-a/view |
| CCPS CHEF manual v2.0 (owner's Drive copy) | https://drive.google.com/file/d/1MgkjQ-NEi0oInTB9UU3CMb5pldsX9zxI/view |
| Norwegian DSB QRA guideline, Vysus/DNV 2021 (owner's Drive copy) | https://drive.google.com/file/d/1178r0oFnB3oYbJLcw0XmkgkJG2nvBDYR/view |
| Melhem, ioMosaic white paper on the omega method, 2023 (owner's Drive copy) | https://drive.google.com/file/d/1HTy-qydBDQ9UXZIp9n88dIdocbif42A-/view |
| Tran and Reynolds, relief valves for two-phase flow (owner's Drive copy) | https://drive.google.com/file/d/1mWD7kWECQVCm4y_Tf4uyAnSE__vI6a4k/view |
| DNV Phast droplet size theory and validation | https://myworkspace.dnv.com/download/public/phast/technical_documentation/05_dispersion/udm/thermodynamics/Droplet%20size%20Model%20Theory_Validation.pdf |
| IChemE Hazards XXIII, practical application of the UKOOA ignition model | https://www.icheme.org/media/9183/paper47-hazards-23.pdf |
| ioMosaic, risk-based approach to damage criteria | https://iomosaic.com/docs/default-source/papers/risk-based-approach-damage-criteria.pdf |
| Mizner, IChemE Symposium Series 71 (1982), LPG pool fires | https://www.icheme.org/media/25178/the-assessment-of-major-hazards-icheme-symposium-series-71-1982-12-mizner.pdf |
| Basha et al., Chemical Engineering Transactions 31 (2013), pool spreading | https://www.aidic.it/cet/13/31/008.pdf |
| NIST Chemistry WebBook, propane | https://webbook.nist.gov/cgi/cbook.cgi?ID=C74986&Units=SI&Mask=1 |
| IAEA-TECDOC-994 (file `te_994_prn.pdf` supplied by the owner) | no link recorded |

**Not obtained**

| Item | Where it is | Why not |
|---|---|---|
| CCPS Pressure Relief and Effluent Handling, chapters 2 and 3 | Wiley / AIChE; the Drive copy is a 57-page preview https://drive.google.com/file/d/1UyQ3QkP-ItF9lNgl9mr2-zOt7s42dJAO/view | paywalled; preview has front matter and chapter 1 only |
| CCPS CPQRA 2nd ed., chapter 2 and section 5.2.2 | Wiley / AIChE; the Drive copy is a 79-page extract https://drive.google.com/file/d/17PNHRRFvvUFM9utipYJC5PkvNNplgug5/view | paywalled; extract has front matter and chapter 1 only |
| IOGP 434-06 ignition probabilities | https://www.iogp.org/bookstore/product/risk-assessment-data-directory-ignition-probabilities/ | free download behind a registration form; not filled in |
| Energy Institute ignition probability review (2006) | Energy Institute | purchase; curves obtained from the IChemE paper above |
| HSE HSL/2004/04, human vulnerability to thermal radiation offshore | summary https://www.fabig.com/external-publications/hse-hsl200404/ | PDF not retrievable (archive copy refused automated requests) |
| API 520 Part I (omega annex), ISO 4126-10 | API, ISO | paywalled; limits quoted through the Melhem white paper |

Unofficial copies on Scribd, kupdf, docshare and similar were found for several of the above and are not used.

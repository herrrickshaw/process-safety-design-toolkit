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

## Still open

| Item | Status |
|---|---|
| CCPS Guidelines for Chemical Process Quantitative Risk Analysis, 2nd ed. | The supplied PDF (twice) has 79 pages: the front matter, contents and chapter 1 (introduction). It contains no ignition-probability tables, no thermal vulnerability criteria, no consequence models. Its only relevant statement is an illustration of an effect-zone criterion at 5 kW/m2 (page of the definitions in chapter 1). Please share chapter 2 (consequence models), section 5.2.2 (ignition sources and data) and the thermal-effects tables, or the whole book. |
| CCPS Guidelines for Pressure Relief and Effluent Handling Systems (Leung omega method) | only the front matter and chapter 1 were supplied (57-page preview); chapters 2 and 3 hold the method. API 520 Part I Annex C is quoted by Melhem and by a calculator page; one transcription of the critical-ratio fit gives 0.806 and the other 0.8127 against the exact root 0.8126; the toolkit uses the exact root. |
| Yellow Book jet-flame models (ch. 6.5.3) and pool spreading (ch. 3) | read only in outline; not implemented. |
| Thermal threshold values 37.5, 12.5, 4.7 kW/m2 | no primary source found; replaced in the tool by the Purple Book probit levels (1 % and 50 % death for a 20 s exposure: 9.8 and 19.5 kW/m2) and the 35 kW/m2 ignition level; extra levels can still be added as inputs. |
| IOGP 434-06 ignition curves | behind a registration form; not submitted. The Purple Book Table 4.5 replaces the Cox values in the tool output; the Cox values remain in `qra.frequency` as a secondary alternative. |

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

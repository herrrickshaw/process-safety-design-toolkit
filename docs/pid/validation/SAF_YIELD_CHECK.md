# SAF yield check: DPR slate against ICAO / CORSIA and open HEFA data (2026-11-11)

Question: is SAF 24,000 t/yr from 30,000 t/yr used cooking oil (UCO), i.e. 80 wt % of the oil, credible for a HEFA plant?
Answer: no. Every source read puts SAF at 15 to about 65 wt % of the oil depending on mode; 80 % is above all of them.

## What each source says (value read in the fetched text unless marked)

| Source | Value | Mode | Grade | Where |
|---|---|---|---|---|
| IEA Bioenergy Task 39, SAF report (2024), sec 5.1.4 | about 15 % of hydrotreated fats and oils falls in the jet range with no extra cracking; a larger jet fraction needs more hydrocracking, which makes more gas and lowers liquid yield; refiners "indicate intent to shift up to 70 % and some up to 100 %"; new isomerisation catalysts are said to avoid yield loss, but the report's footnote 7 says that is company claims | diesel mode / jet-shifted | A | `task39.ieabioenergy.com/.../IEA-Bioenergy-Task-39-SAF-report.pdf`, pp 26-27 |
| NREL maximum-jet balance, Table G-1 (read by the assumption-literature agent, not re-read here) | kerosene 46.1, diesel 30.4, naphtha 8.5, LPG 6.0, fuel gas 1.5 wt %; H2 4.0 (RD) to 4.5 (jet) wt % of feed | max jet | A (agent) | `ASSUMPTION_LITERATURE.md` row, printed p.118 |
| Tao et al., Biotechnol Biofuels 10:261 (2017), Table 2, yellow grease | jet 194.7, gasoline-range 93.7, propane 1.6, diesel 0.8 gal per dry ton of oil | max jet (hydrocracking) | A | PMC5679388 |
| ISCC CORSIA 205 v2.0 (mirror of ICAO default values) | gives only life-cycle emissions per MJ (UCO HEFA 13.9 gCO2e/MJ in the HEFA table, layout-extracted: check against the 8th edition); no process yields appear anywhere in the document | n/a | A | `ISCC_CORSIA_205_Life_Cycle_Emissions_2.0.pdf` |
| ICAO conversion-process pages, "rules of thumb" | not read: icao.int is behind a Cloudflare challenge; not bypassed | n/a | not read | see memory note on the ISCC mirror |

Tao conversion to mass (derived, two assumptions): jet 194.7 gal = 737 L; at 0.775 to 0.80 kg/L that is 571 to 590 kg. Per US short ton (907 kg) of oil that is 63 to 65 wt %; per metric ton 57 to 59 wt %. The paper does not define "dry ton" in the text read, and the oil in its model is hydrocracked for maximum jet, so treat this as an upper design bound, not a plant average. Gasoline-range plus jet plus diesel plus propane is about 90 % of the oil mass on the same basis.

## Owner-supplied documents (added 2026-11-11)

| Document | Yield content | Grade | Where |
|---|---|---|---|
| IATA, SAF Handbook (May 2024) | "HEFA can deliver a SAF fraction between 15-50 %", Fischer-Tropsch 25-40 %, alcohol-to-jet 70-90 % of the refinery's total output. Figure 7 (adapted from ICCT, "The cost of supporting alternative jet fuels in the European Union"), read from the plotted bars (approximate, share of product output): HEFA default SAF about 15 %, renewable diesel about 77 %, light ends about 8 %; HEFA maximum-SAF mode SAF about 55 %, renewable diesel about 26 %, light ends about 19 %. "Adjusting product slates often comes at the expense of overall yields." | A (text and figure read) | p.16, sec 2.2.4 |
| RSB ICAO CORSIA standard, RSB-STD-12-001 v1.6 (June 2025) | no process yields; default life-cycle values only. Confirms UCO via HEFA: core LCA 13.9 gCO2e/MJ, ILUC none, total 13.9 (so the ISCC-mirror value above is also in the June 2025 table) | A | HEFA default-value table |
| ICAO Document 05, Sustainability Criteria (June 2025) | sustainability criteria only; no yields or conversion data | A | whole file grepped |
| ICAO ACT-SAF, "PPT05_A Introduction to SAF" | CORSIA eligibility and life-cycle accounting slides; no yields | A | whole file grepped |

IATA's range (15-50 % text, about 55 % in the figure for maximum-SAF mode) agrees with IEA Task 39 (about 15 % default) and NREL (46.1 % max jet) and is a fourth independent source against the DPR's 80 %. The figure's basis (mass, energy or volume of product) is not stated on the page; treat the percentages as shares of fuel output, not of oil mass.

## Verdict for the DPR slate

- Our DPR value: SAF 24,000 / 30,000 = 80 wt % of UCO. Above the Tao upper bound (57-65 %), above NREL (46.1 %), above the claimed catalyst ceiling (70 % of the liquid, which is itself about 0.85 x 30,000 = 17,850 t/yr), and above the stoichiometric liquid ceiling the SAF validator computed (83-85 % of the oil as total liquid fuel, before naphtha and propane).
- Credible SAF from 30,000 t/yr UCO: about 4,500 t/yr (15 %, diesel mode with a splitter), 13,800 t/yr (46.1 %, NREL max jet), up to about 17,500-19,500 t/yr (Tao-type hydrocracked design, unproven commercially). The SAF validator's 13,500-17,500 t/yr range sits inside this.
- To reach 24,000 t/yr SAF: 52,000 t/yr UCO at 46.1 %, 37,000-42,000 t/yr at 57-65 %.
- CORSIA / ICAO does not constrain yield; it constrains emissions per MJ (UCO HEFA is a low-intensity eligible pathway). Eligibility is not evidence for the DPR's mass yield.

## What to change in the SAF set (needs the owner's choice, see lead summary)

1. Keep feed 30,000 t/yr (template S) and set SAF to 46.1 wt % (about 13,800 t/yr), diesel 30.4, naphtha 8.5, LPG 6.0, fuel gas 1.5 (NREL Table G-1 as the slate), H2 4.5 wt % of feed; OR raise feed to about 52,000 t/yr to hold SAF at 24,000 t/yr (capacity change: every unit size scales 1.7x).
2. Flag the template's revenue lines (SAF 24,000 t/yr at INR 165/kg) as overstated by about 42 % at 30,000 t/yr feed.
3. Re-run the stage-1 reaction heat and quench rise after the slate change (SAF validator: runaway rises understated 2.3-2.9x).

Fetched files: `<scratch>/val_saf_yield/` (iscc205.pdf, task39.pdf, pmc5679388.html).

# Capacity analogues: grain ethanol, biodiesel (UCO), HEFA SAF (2026-11-12)

Purpose: real operating, permitted or announced plants to ground the design capacity of our three conceptual sets. Screening aid, not certified design. Every value below was read in a fetched document unless the grade is C (search snippet or unreadable page). Row-level data, URLs and pages are in `ETHANOL_BIODIESEL_SAF_ANALOGUES.csv` (same folder). Fetched files are under `/private/tmp/claude-501/cap_1` to `cap_5`.

Grades: A = the document was fetched and the passage read (including company press releases and trade pages: the document itself, not necessarily independent of the company); C = search snippet or a page whose body could not be read.
Verification: verified = a regulator/government document or two independent sources agree; single-source = one origin only (company or proponent), even if several outlets repeat it.

Our current Rev B basis (from the generators): ethanol 100 KLPD, 330 d, grain 86,800 t/yr, DDGS 26,000 t/yr; biodiesel 20 KLPD (6,000 kL/yr, 300 d, 17.6 t/d); SAF feed 30,000 t/yr UCO, SAF 46.1 wt % (about 13,800 t/yr) per `SAF_YIELD_CHECK.md`.

Walls met (not bypassed): sec.gov (Aemetis 10-K) returned "undeclared automated tool"; marketscreener.com (Jagatjit 200 KLPD board approval) returned Access Denied; Argus page empty; Biodiesel Magazine bodies truncated.

## 1. Grain / molasses / cane ethanol (India, KLPD)

| Plant, operator, place | Capacity | Key figures read | Status | Source, page | Grade / verification |
|---|---|---|---|---|---|
| Shiur SK, Kalamnuri, Maharashtra | 30 KLPD molasses (also cane juice) | molasses 111 TPD (C) / 103 TPD (B-heavy); steam max 10.65 TPH from 15 TPH boiler; power 0.89 MW; water 221 m3/d | proposed, summary 2021-04 | MPCB public-hearing summary, pp 1-5, 8 | A / single-source |
| Pernod Ricard, Dindori, Nashik | 60 existing, 250 proposed | boiler 18 TPH existing, 60 TPH proposed (6.5 MW TG); steam 17.1 then 52.5 TPH; DDGS 175 total; rice + maize + malt; scope includes potable spirit | 60 operating; expansion proposed 2024-05 | MPCB summary, pp 3-5 | A / single-source |
| Grain distillery, Nayagarh, Odisha (M/s Sanjeev Kumar Gupta) | 100 KLD | 30 TPH AFBC boiler, 3 MW co-gen, water 400 m3/d, DDGS 48 TPD, CO2 65 TPD, ZLD | EC granted 2024-10-03 | MoEFCC EC letter, pp 2, 9-10 | A / verified (government) |
| SLB Ethanol DPR | 200 KLPD (218 total spirits) | broken rice 444.4 t/d at 450 L/t (2.22 kg grain/L); steam 34.52 TPH (derived 4.14 kg/L); boiler 45 TPH; TG 5 MW; coal 6.88 TPH; DDGS 88.9 t/d (0.44 t/KL); CO2 165 TPD | proposed, DPR Dec-2021 | EC-portal DPR, pp 4, 10 | A / single-source |
| India Glycols Kashipur Unit II | 200 KLD (72,000 KL/yr) | 55 TPH boiler, 7 MW co-gen; site history 120 to 205 to 425 KLPD (EC 24-06-2004) | proposed, PFR 2022 | EC-portal PFR, pp 1-3 | A / single-source |
| Sufalam Industries, Deori, Gondia | 300 existing + 200 = 500 KLD | boiler 58 TPH, 5 MW captive, DDGS 233 TPD, CO2 395 TPD | 300 operating; expansion proposed 2026-02 | MPCB summary, pp 3-4 | A / single-source |
| Godavari Biorefineries, Sameerwadi | +200 KLPD grain (beside 600 KLPD cane) | Rs 130 crore investment | commissioned (SEBI Reg 30 relayed) | iamrenew web page | A / single-source |
| India Glycols, Gorakhpur | +200 KLPD, 310 combined | unit trap: 310 is combined | commissioned, reported 2025-04 | iamrenew, chinimandi | A / single-source |

Sizing context: the MoEFCC expert-committee agendas fetched (Aug and Sep 2022, `environmentclearance.nic.in/writereaddata/Form-1A/Agenda/...`) list dozens of grain proposals; the sizes read in the extracted text run from 60 up to 400 KLD, with 100 to 200 KLPD the commonest.

New benchmarks for our Rev B 100 KLPD: grain 2.22 kg/L (SLB DPR, 450 L/t) against our 2.40 kg/L and IGL 2.465 already in the set; steam 4.14 kg/L derived from the SLB DPR against IGL 6.6 and PR 5.04 already cited; DDGS 0.44 t/KL (SLB) and 0.48 t/KL (Nayagarh EC table, 14,850 t/yr / 100 KL / 330 d, derived) against our 0.74 dry kg/L. The DDGS gap is worth a look (basis of the DPR figures unknown: dry, with or without solubles). Do not treat the Shiur 8.5 kg/L derived steam as a benchmark.

Not read: Jagatjit 200 KLPD (Hamira, board approval 2022-07-22), DCM Shriram Ajbapur 200 to 320 KLPD, EID Parry 120 KLPD: search snippets only (C), excluded from the table.

### Recommended ethanol capacities
- Small 60 KLPD: Pernod Ricard Nashik operating base (60) and several 60 KLPD grain proposals on the 2022 agendas. Versus Rev B: 0.6x.
- Base 100 KLPD: the Nayagarh EC (granted, same class, same 100 KLD plus 3 MW pairing). Keep Rev B unchanged: 1.0x.
- Large 200 KLPD: SLB DPR, IGL Unit II, Godavari commissioned, IGL Gorakhpur increment. 2.0x Rev B; every unit scales about 2x. Beyond this (250 to 500 KLD) exists but only as single-source expansions on multi-unit sites.

## 2. Biodiesel from used cooking oil / waste oils

| Plant, operator, place | Capacity | Notes | Status | Source | Grade / verification |
|---|---|---|---|---|---|
| M11 Industries, Padubidri, Karnataka | 450 TPD (about 511 KLPD at 0.88) | UCO and waste oils; Rs 350 crore | operating Aug-2024 | Biofuels Digest, iamrenew | A / single-source (company PR) |
| Universal Biofuels (Aemetis), Kakinada | 60 Mgy done Sep-2023; 80 Mgy in process then (about 918 KLPD at 330 d, derived) | page also states 100 Mgy goal; SEC filing blocked | operating | biobased-diesel.com (company PR) | A / single-source |
| BioD Technology, Dubai | 30,000 t/yr (about 91 t/d, 103 KLPD) | UCO, tallow, POME, trap grease | commissioned (2021) | biobased-diesel.com | A / single-source |
| Agri Energy, Bootle UK | 16 million L/yr (about 48 KLPD) | page body truncated | opened 2012 | Biodiesel Magazine | C |
| Green Fuels / Aris, Mumbai-Pune | 20 t/d (planned) | closest to our 17.6 t/d, not built | planned | Argus snippet | C |
| BioD Energy, Bawal | 100 t/d planned | status unknown | announced 2018 | newspaper snippet | C |

Finding: no operating plant near 20 KLPD was found with a readable document. Our Rev B 20 KLPD sits below every readable analogue (BioD Dubai about 5x, M11 about 25x, Kakinada about 46x). None of the biodiesel rows reached "verified".

### Recommended biodiesel capacities (all rest on single-source entries)
- Small 20 KLPD: keep Rev B (1.0x). Only analogue is the planned 20 t/d Green Fuels unit (C).
- Base 100 KLPD (about 88 t/d): BioD Dubai 30,000 t/yr. 5x Rev B.
- Large about 500 KLPD (450 TPD): M11 Padubidri. 25x Rev B; batch transesterification vessel sizing would change to continuous.

## 3. HEFA SAF / renewable diesel from waste fats and oils

| Plant, operator, place | Capacity | SAF share as stated | Status | Source, page | Grade / verification |
|---|---|---|---|---|---|
| Saffaire Sakai, Cosmo/JGC/REVO, Osaka | about 30,000 kL/yr neat SAF (23,250-24,000 t at 0.775-0.80 kg/L) | 100 % product is SAF; feed tonnage not stated | complete 2024-12-25; supply Apr-2025 | Cosmo/JV release 2025-03-07, p 3; 2022 release | A / single-source origin |
| Montana Renewables, Great Falls | 16,140 bpd now; 16,400 bpd proposed | proposed SAF + renewable kerosene : RD about 80:20 | operating; revised project applied 2026-06-25, draft | Montana DEQ draft EA; OGJ (15,000 b/sd design, Apr-2023) | A / verified, scope resized from 18,000 bpd plan (snippet) |
| Rodeo, Phillips 66 | 800 Mgy (50,000 bpd) | not stated | operating 2024 | BIC Magazine 2024-04-02 | A / single-source |
| Neste Rotterdam | 2,700 kt/yr total; SAF capability 1,200 kt | 44 % (1,200 / 2,700, derived) | FID 2022-06-27; start-up unconfirmed | Neste stock exchange release | A / single-source |
| IndianOil Panipat | 35,000 t/yr SAF from UCO | all | announced 2025-08, unconfirmed | Biofuels Digest | A / single-source |
| BPCL Mumbai | 4,000 tpd kerosene hydrotreater co-processing 5 % UCO (about 200 t/d) | n/a (co-processing) | technology award 2026-10-14 | Hydrocarbon Engineering | A / single-source |
| Neste Singapore (2,600 kt, up to 1,000 SAF) and Diamond Green Diesel Port Arthur (470 Mgy, about half convertible) | | | | | C, snippets only |

Unit traps: Cosmo gives SAF volume, not feed. Neste "SAF capability" is not a committed slate. Montana is a combined SAF + RD barrel figure. Panipat is probably a co-processing unit (not stated).

### What our feed gives at the sourced yields (from `SAF_YIELD_CHECK.md`: IATA default 15 %, NREL max jet 46.1 %, Tao hydrocracked 57-65 % per ton, SAF share of oil)
| Feed, t/yr UCO | SAF at 15 % | SAF at 46.1 % | SAF at 57-65 % |
|---|---|---|---|
| 30,000 (Rev B) | 4,500 | 13,830 | 17,100-19,500 |
| 50,000 | 7,500 | 23,050 | 28,500-32,500 |
| 100,000 | 15,000 | 46,100 | 57,000-65,000 |

Cosmo's 23,250-24,000 t/yr SAF therefore implies about 50,400-52,100 t/yr feed at NREL 46.1 %, or about 35,800-42,100 t/yr at Tao-type yields (feed not disclosed; this is an inference, not a Cosmo statement). It equals the DPR's 24,000 t/yr SAF target.

### Recommended SAF capacities
- Small 30,000 t/yr feed (Rev B, 1.0x), SAF about 13,800 t/yr at 46.1 %. No verified plant at this feed size; it is below Sakai.
- Base 50,000 t/yr feed (1.67x Rev B), SAF about 23,000 t/yr at 46.1 %: matches the one readable small SAF analogue (Cosmo Sakai) and the DPR's SAF target.
- Large 100,000 t/yr feed (3.3x), SAF about 46,000 t/yr at 46.1 %. This is an interpolation: no verified analogue exists between Sakai and Montana (16,140 bpd) or Rodeo (50,000 bpd), both far bigger. IndianOil Panipat's 35,000 t/yr SAF (single-source) is the only Indian figure near it.

## Not found
- Any readable document for an operating UCO biodiesel plant below 100 t/d.
- A feed tonnage or hydrogen/utility figures for Sakai, Panipat or Rodeo.
- Hydrogen, steam and power per tonne for any HEFA plant (permits read give only bpd).
- Independent second sources for the biodiesel and SAF announcements: sec.gov and marketscreener walls were not bypassed.
- Jagatjit, DCM Shriram, EID Parry filings (snippets only).

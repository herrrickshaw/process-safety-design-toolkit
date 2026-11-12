# Capacity analogues: CBG, fruit and vegetable processing, coal-to-urea

Purpose: ground design capacities in real or permitted plants. Screening aid, not certified design.
Date of search: 12 Nov 2026. Full machine-readable list: `CBG_FRUITVEG_UREA_ANALOGUES.csv` (same folder; includes `announced_by`, `verification_source`, `verification_status`).

Grades: A = document or page was fetched and the passage read. C = search snippet only, or the host blocked the fetch.
Verification: "verified" = at least two independent public sources agree; "single-source" = one source only. A trade outlet repeating the same company release is not counted as independent.
Local copies of every fetched document are in `/private/tmp/claude-501/cap_cfu/` (scratch, may be wiped).

## Our current Rev B basis (from the generators)

| Process | Rev B capacity | Source in script |
|---|---|---|
| CBG | 10 t/d CBG, 330 d/yr (3.3 kt/yr CBG), DPR feed 160 t/d, 52,800 t/yr | `gen_pid_cbg.py` lines 4-6, 38-41 |
| Fruit and veg | 10,000 t/yr raw, about 50 t/d in season, 200 d/yr, 6,000 t/yr pulp | `gen_pid_fruitveg.py` lines 101-105 |
| Coal-to-urea | 1.10 Mt/yr urea (feed coal scaled to this) | `gen_pid_urea.py` line 22 and `UREA_TARGET_MTPA` |

## 1. Compressed biogas (CBG)

| Plant | Operator, place | Capacity | Feed / key figures | Status | Source (page) | Grade | Verification |
|---|---|---|---|---|---|---|---|
| Lehragaga | Verbio India, Sangrur, Punjab | 33 t/d CBG design | 300 t/d paddy straw (9.1 t/t, derived), 8 x 10,000 m3 digesters, 600-650 t/d FOM, about Rs 220 cr | commissioned Oct 2022; about 6 t/d at start-up | PIB 19 Oct 2022 (PRID 1868887) | A | verified (PIB + Tribune quoting company MD); sustained 33 t/d not shown |
| Satna | Gruner Renewable Energy, Madhya Pradesh | 23.5 t/d single-day record, 120 % of design (design about 19.6 derived) | paddy straw, agri residue | operating, Jun 2026 | Energetica India 24 Jun 2026 | A | single-source (same company release elsewhere) |
| Balrampur, Lakhimpur Kheri (2 plants) | EverEnviro, Uttar Pradesh | 10 t/d each | press mud | commissioned Apr 2024 | iamrenew.com 4 Apr 2024 | A | single-source |
| Moradabad | Samridh Bioenergy, UP | 12 t/d | 270 t/d organic waste (22.5 t/t derived), 30,000 m3/d biogas | broke ground Apr 2025 | Construction World 17 Apr 2025 | A | single-source |
| Batala | MEPL BioEnergy, Punjab | 100 t/d press mud in, 5.6 t/d "biogas" out (17.9 t/t if CBG, derived) | Rs 35 cr | inaugurated Dec 2024 | Energetica India 17 Dec 2024 | A | single-source, unit ambiguous |
| SATAT fleet | MoPNG | 132 plants, 920 t/d, mean 7.0 t/d (derived) | | Jan 2026 | Energetica India 6 Jan 2026 | A | single-source |
| CSE model | Centre for Science and Environment | 5 t/d model; press mud 25 t/t CBG, dung 50, MSW 25, straw 10; capex Rs 25-30 cr press mud | also real case plants 3.2, 5 t/d | webinar 24 Jul 2026 | CSE national blueprint, pdf pp 6, 8, 10 | A | single-source, a model |
| EU fleet | EBA Statistical Report 2025 | mean 483 m3/h biomethane, 1,620 plants (2024) | | Dec 2025 | Renewable Energy Magazine 10 Dec 2025 | A | verified (two outlets of one EBA release) |
| South Dakota dairy RNG | EnviTec Biogas USA, SJI | 778 Nm3/h (483 scfm) | about 1,100 m3/d manure, 9,500 cows | commissioned 2025 | Bioenergy International 31 Mar 2025 | A | single-source |
| Gorakhpur | Indian Oil | 20 t/d | | Mar 2024 | Natural Gas World (header only) | C | single-source |
| Navsari (announced) | Gruner Renewable Energy, Gujarat | 44 t/d BIOGAS, not CBG | press mud, paddy, cane trash, MSW; Rs 220 cr | announced Jun 2024, no commissioning found | The Machine Maker 17 Jun 2024 | A | single-source, unit trap, excluded |

Unit and scale traps found:
- Navsari "44 t/d" is biogas; CBG is roughly half or less. Do not compare with 33 t/d CBG.
- Satna 23.5 t/d is one record day, not nameplate.
- Sangrur 33 t/d is design; PIB says it ran at about 6 t/d at inauguration.
- Gruner says many CBG plants run at 40-50 % of installed capacity; nameplate overstates real output.
- Feed per t CBG varies 10 (straw) to 50 (dung); press mud 25 (CSE) or 17.9 (Batala, derived).

Recommended CBG capacities (only from entries with two sources or from operating plants):

| Size | Capacity | Reason | Versus Rev B (10 t/d) |
|---|---|---|---|
| Small | 5 t/d CBG | CSE benchmark model; fleet mean is 7 t/d; below this the upgrader dominates cost. Provisional: model, single-source | 0.5x |
| Base | 10 t/d CBG | EverEnviro runs two 10 t/d press-mud plants; Samridh builds 12 t/d. Keep Rev B | 1.0x, unchanged |
| Large | 33 t/d CBG | Largest verified design (Sangrur, PIB + company MD). Needs 300 t/d straw or about 800 t/d press mud at 25 t/t | 3.3x |

Rev B feed (160 t/d for 10 t/d CBG, 16 t/t) is lighter than the CSE press-mud figure (25 t/t, i.e. 250 t/d). Check which feedstock mix the 160 t/d represents before scaling.

## 2. Fruit and vegetable processing

No entry reached "verified" and no Indian EC/EIA or consent document with a tonnes-per-year figure was found; most hits are company statements. Treat the recommendation as provisional.

| Plant | Operator, place | Capacity | Notes | Status | Source | Grade | Verification |
|---|---|---|---|---|---|---|---|
| Jalgaon IQF/BQF | Jain Irrigation, Maharashtra | 60,000 t/yr fruit; 40 t/d IQF + 16 t/d BQF | mango, banana, pomegranate, papaya etc. | launched Jun 2015 | Business World 23 Jun 2015 | A | single-source |
| Jain group | Jain Irrigation (Alfa Laval feature) | 200,000 t/yr F&V handled FY2006-07, 100,000 fruit; target above 300,000 | group, four plants, not one nameplate | old | Alfa Laval story | A | single-source |
| Mwandege | Bakhresa Food Products, Tanzania | 45,000 to 100,000 t/yr fruit (announced) | Tsh 20 bn (US$8.27M) | completion not verified | Food Business Africa | A | single-source |
| Molina | Patagoniafresh (CFT line), Chile | 1,200 t/d tomato + 600 t/d fruit | fruit line 25 t/h | built from 2014 | CFT page | A | single-source, vendor |
| Egypt tomato | Paste & Juice | 1,000 to 2,000 t/d tomato (announced) | new line Apr-May 2024 | completion not verified | tomatonews.com | A | single-source |
| Almonte | SVZ, Spain | 12,500 to 20,000 t/yr | puree | c. 2018 | fruit-processing.com snippet | C | single-source |
| Prosser | Tree Top, USA | 650 t/d apple/pear, 125 t/d soft fruit | Cloudflare wall, stopped | n/a | snackandbakery.com snippet | C | single-source |
| Parala FPU | Himachal Pradesh ESIA, India | 10 t/h apple concentrate, RTS 2,000 L/h, pectin 40 t/d | host unreachable from this machine | ESIA Sep 2021 | HP govt PDF, snippet | C | single-source |

Traps: tonnes of raw intake versus product (Jain 60,000 t/yr fruit versus 56 t/d product); t/d at a season peak versus t/yr (Rev B uses 200 d); announced doublings (Bakhresa, P&J) not shown to be completed. A Chittoor MBA thesis (Krishikosh) says the selected mango/tomato plants process 450 t/d mango and 250 t/d tomato in season, but it does not say if that is one plant or the sample, so it is not used.

Recommended (provisional, because no entry is verified):

| Size | Capacity | Reason | Versus Rev B (10,000 t/yr) |
|---|---|---|---|
| Small | 10,000 t/yr raw (about 50 t/d, 200 d) | No operating analogue this small found; keeps Rev B as the FPO or cluster-scale case | 1.0x |
| Base | 30,000 t/yr raw (about 150 t/d, 200 d) | Between SVZ 20,000 t/yr (snippet) and Jain IQF 60,000 t/yr | 3x |
| Large | 100,000 t/yr raw (about 500 t/d, 200 d) | Bakhresa announced target; Patagoniafresh fruit line 600 t/d; Jain group above 100,000 t/yr fruit | 10x |

Rev B at 10,000 t/yr sits at the low end of what real companies list; nothing found supports it as an industrial nameplate.

## 3. Coal-to-urea

| Plant | Operator, place | Capacity | Key figures | Status | Source (page) | Grade | Verification |
|---|---|---|---|---|---|---|---|
| Talcher | Talcher Fertilizers (RCF, CIL, GAIL, FCIL), Odisha | 3,850 t/d urea, 2,200 t/d NH3 (one train each); 1.27 Mt/yr at 330 d | coal feed 106.2 t/h, fuel coal 134.0 t/h, pet coke 38.5 t/h; syngas 243,000 Nm3/h; CO2 60,480 Nm3/h; water 1,437 m3/h; 2 x 35 MW; raw coal 3.5-4.5 Mt/yr | 65.66 % complete Feb 2025; cost Rs 13,277 cr to about 19,000 cr | Pre-Feasibility Report, pdf pp 18, 24, 29, 43 | A | verified (PFR, PIB CCEA 20 Apr 2021, ICRA 21 Apr 2026) |
| Plant IV | China XLX, Xinxiang, Henan | +800,000 t/yr urea, +450,000 t/yr NH3 | coal-slurry gasification; group 1.25 Mt/yr before | Sep 2013 | Process Worldwide | A | single-source |
| Plant V | China XLX, Xinjiang | 520,000 t/yr urea | group above 2.6 Mt/yr | started Aug 2015 | Process Worldwide | A | single-source |
| Yiding | Yili Group, Ordos | 1.04 Mt/yr urea, 0.6 Mt/yr NH3 | CCG gasifier, RMB 750 m, target Sep 2022 | completion not verified | CHOREN 1 Apr 2021 | A | single-source |
| Hami | CNCEC-built, Xinjiang | 1.0 Mt/yr urea, 0.6 Mt/yr NH3 at full output | start-up trials, full capacity projected | Nov 2025 | Blooming Global 24 Nov 2025 | A | single-source |
| Tuke | China Coal Ordos | 1.75 Mt/yr urea, 1.0 Mt/yr NH3 | 13 BGL gasifiers | operating | ppPLUS database | C | single-source, excluded |

Traps: Talcher capacity is stable across three sources but cost rose 43 % and the date slipped from 2022-24 to unknown; Chinese Mt figures can be group totals or increments (XLX IV); "full capacity" at Hami is a projection. Talcher ratio NH3/urea 0.571 (derived).

Recommended (Talcher is the only verified entry; the others are single-source):

| Size | Capacity | Reason | Versus Rev B (1.10 Mt/yr) |
|---|---|---|---|
| Small | 0.52 Mt/yr urea (about 1,575 t/d at 330 d, derived) | China XLX Plant V; single ammonia and urea line scale. Single-source | 0.47x |
| Base | 1.27 Mt/yr urea (3,850 t/d, 2,200 t/d NH3) | Talcher, the only verified coal-gasification urea project, and the Indian reference | 1.15x (Rev B is 13 % lower; Rev B coal feed scales with it) |
| Large | 1.75 Mt/yr urea | Tuke is the largest found but grade C; use 1.0 Mt/yr (Hami, Yiding) as a verified-quality fallback, i.e. no step up from Rev B | 1.6x |

## Not found

- No Indian CBG, fruit pulp or puree plant EC/EIA with a stated capacity was fetched (PARIVESH search returned none; most CBG plants fall under state consent only).
- No stock-exchange filing or investor presentation with an announced CBG, fruit-processing or urea nameplate was fetched. The Talcher capacity came from the EC pre-feasibility report and PIB.
- No verbio.de press release (404), no Tree Top, SVZ or Himachal ESIA text (wall or host error).
- No fruit and vegetable utility data (steam, water per t) and no CBG power or steam per t were located.
- Coal-to-urea feed per t urea for the Chinese plants was not found; only Talcher gives hourly feed (about 106 t/h gasifier coal for 160 t/h urea, derived 0.66 t coal per t urea, fuel coal excluded).

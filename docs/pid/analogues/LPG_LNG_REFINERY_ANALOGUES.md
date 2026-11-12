# Capacity analogues: LPG, small/mid LNG, crude refinery

Prepared 12 Nov 2026. Companion CSV: `LPG_LNG_REFINERY_ANALOGUES.csv` (same rows, with page, grade, announced_by, verification columns).
Grade A = document fetched with curl and read as extracted text (or HTML text) in this session. Grade C = search snippet only. No remembered values.
"Verified" = two independent public sources agree. "Single-source primary" = one regulator or proponent filing read in full, no independent second source found. Pages are PDF page indices of the extracted file.

## Our current Rev B basis (read from the scripts)
- LPG: five assumed vessels V1-V5, 1.4 x 3.5 m up to 4.0 x 19.0 m; reference V3 is a 105 m3 bullet (about 45 t at 85 % fill). No bottling or throughput basis. (`gen_pid_lpg.py`)
- LNG: 2.0 mtpa, one train, one 63,827 m3 LNG tank. (`gen_pid_lng.py`)
- Refinery: 15 Mt/yr crude unit (about 286,000 bpd). (`gen_pid_refinery.py`)

## 1. LPG storage / bottling / terminal (6 grade A, 3 grade C)
| Plant (operator, place) | Nameplate | Equipment | Source, page | Status |
|---|---|---|---|---|
| Puducherry (IOCL) | 22 TMTPA, 115 MT/day filling | 3x100 + 2x300 MT mounded = 900 MT, 1 carousel | IOCL draft EIA, pp.26, 29 | proposed; one passage says 600 MT total, tables say 900 |
| Chakan (IOCL) | 60.87 TMTPA | 600 -> 1,800 MT (2x600 MT mounded added), 24-point carousel | MPCB exec summary 2019-07, Table E.1 | proposed |
| Una (IOCL) | 60 TMTPA, about 250 MT/day | 3x300 + 2x600 MT = 2,100 MT | PFR Jan 2017, pp.4, 9 | proposed |
| Rasayani (BPCL) | 270 TMTPA Ph I, 540 Ph II | 3x1,450 MT per phase (4,350 MT; 8,700 MT total), 2x48-station carousels per phase | MPCB exec summary Oct 2018, p.3 | proposed |
| Uran terminal (BPCL) | 54,700 MT storage | 2x8,000 + 2x12,000 MT refrigerated, 8 Horton spheres x 1,350 MT, mounded 3x900 + 2x600 MT | MPCB exec summary Oct 2017, Table 1 | proposed expansion |
| Chhara terminal (Vopak/SP Ports) | 5.0 MMTA LPG throughput | refrigerated propane/butane tanks 50,000 m3 each as read, 200,000 m3 total; 6x450 MT mounded | CRZ Form-2 summary 2019, p.2 | proposed |
| Matia (BPCL) C | 30 TMTPA, 300 MT | 10-point carousel, 600 cyl/h | psuconnect, 19 Aug 2026 | commissioned; single news source |
| Hathua (BPCL) C | 180 vs 120 TMTPA | 2x24 carousel | BPCL announcement vs Lok Sabha snippet | CONFLICTING |
| Naharlagun (IOCL) C | 87 MT, 3,000 cyl/day | 3 bullets | press snippet | single source |

Traps: TMTPA is thousand tonnes per year. Chakan gives 24-point and 12-point carousel in different places. Rasayani lists 2x48 and 4x48 in different sections, and Phase I vs II doubles everything. Chhara mixes m3 and MT. No LPG entry has an independent second source (the filings are primary), so LPG recommendations are single-source primary, not "verified".

### Recommended LPG design capacities
| | Bulk storage | Bottling | Basis | vs Rev B |
|---|---|---|---|---|
| Small | 300 MT (3x100 MT) | 22 TMTPA | Puducherry existing and post-augmentation scale | similar order to the sum of Rev B vessels, but Rev B has no bottling basis |
| Base | 900 MT (e.g. 3x300 MT) | 60 TMTPA | Una existing 900 MT / 60 TMTPA; Chakan 60.87 TMTPA | about 3x the combined Rev B vessels; V3 (about 45 t) is about 5 % of base |
| Large | 4,350 MT (3x1,450 MT mounded) | 270 TMTPA | Rasayani Phase I | well over 10x Rev B |

Rev B vessels (largest about 100 t) are below every real bottling plant read; they fit a sub-100 MT site (Naharlagun 87 MT, grade C, not used).

## 2. Small/mid-scale LNG liquefaction (4 grade A, 1 grade C)
| Plant | Nameplate | Equipment | Source | Status / verification |
|---|---|---|---|---|
| Vijaipur SSLNG (GAIL) | 36 t/day (2x18) | 2 skids, 2 tanks 56 kL, 400-800 kW/skid | GAIL slide p.3 (pngrb.gov.in); indianinfrastructure.com 26 Mar 2024 | commissioned Mar 2024; verified |
| Jacksonville (Eagle LNG) | 1.0 MTPA = 3 x 0.33 (550,000 gal/d per train) | 1 tank 45,000 m3 net | FERC FEIS Apr 2019, ES, p.19 | authorised; build status not verified |
| Elba Island (Kinder Morgan) | 2.5 MTPA, authorised 2.9 | 10 modular units, 5 tanks | FERC order CP23-375, p.3 | operating since 2020; capacity verified |
| CCL Midscale Trains 8 and 9 (Cheniere) | 3 MTPA = 2 x 1.5 (5 with debottlenecking) | 3 existing tanks shared | Cheniere release Sep 2025; OGJ 24 Jun 2025 | FID Jun 2025; verified |
| CCL Stage 3 (Cheniere) C | about 10 MTPA = 7 x about 1.49 | | trade snippet | per-train reference only |

Traps: per-train vs total; gallons/day vs tonnes; 3 vs 5 MTPA after debottlenecking at CCL 8-9; Elba 2.5 baseload vs 2.9 authorised. Tank per tonne: Jacksonville 45,000 m3 for 1.0 MTPA; Rev B 63,827 m3 for 2.0 MTPA is less storage per tonne.

### Recommended LNG design capacities
| | Capacity | Basis | vs Rev B 2.0 mtpa |
|---|---|---|---|
| Small | 36 t/day (about 0.013 MTPA) | Vijaipur, verified | about 1/150 |
| Base | 1.0 MTPA as 3 trains x 0.33, one 45,000 m3 tank | Eagle (capacity read from FEIS; trade press agrees, grade C) | half |
| Large | 3.0 MTPA as 2 trains x 1.5 | CCL 8-9, verified | 1.5x; the largest single train read is 1.5, below Rev B's single 2.0 mtpa train |

## 3. Crude refinery, India (11 grade A, 0 grade C)
Nameplate source for all: PPAC "Installed Refinery Capacity" table at 1.04.2026 (fetched), cross-checked with the MoPNG refining-capacity page (fetched, undated).
| Refinery | MMTPA | Notes |
|---|---|---|
| Digboi (IOCL) | 0.65 | verified |
| Bongaigaon (IOCL) | 2.7 (PPAC) vs 2.35 (MoPNG) | CONFLICTING; PPAC is newer |
| Numaligarh (NRL) | 3.0, expanding to 9.0 | new 6 MMTPA unit plus 1,635 km crude line; target Mar 2027; cost 22,594 -> 28,026 -> 37,720 crore (under approval) per NRL PDF p.1; delayed |
| Bina (BORL/BPCL) | 7.8 | verified |
| Mathura (IOCL) | 8.0 | verified |
| HPCL Rajasthan (Barmer) | 9.0 | PPAC 9,000 kt; EIL (PMC) page; utilities package 7 tanks + 3 spheres; schedule 49 -> 75 months; verified, delayed |
| Paradip (IOCL) | 15.0 | nameplate; Rev B notes reported throughput 10.6 vs 12.2 |
| Panipat (IOCL) | 15.0 | planned 25 not verified |
| CPCL Cauvery Basin | 9.0 planned | PPAC lists 0; excluded |

PPAC (2026) and MoPNG (older) also differ for HPCL Mumbai (9.5 vs 7.5) and Visakh (15.0 vs 8.3); these look like later expansions, not errors.

### Recommended refinery design capacities
| | Capacity | Basis | vs Rev B 15 Mt/yr |
|---|---|---|---|
| Small | 3.0 MMTPA | Numaligarh existing, verified | 1/5 |
| Base | 9.0 MMTPA | HRRL, verified (Bina 7.8, Mathura 8.0 bracket it) | 0.6x |
| Large | 15.0 MMTPA | Paradip, Panipat, verified | equal; only Jamnagar (33.0, 35.2) and Nayara (20.0) are larger |

## Not found
- An independent second source for any LPG filing; Hathua tonnage and resolution of 180 vs 120 (Sansad PDF host failed to connect, snippet only).
- Eagle LNG status after the FEIS; Elba per-train rating (only the 10-unit total).
- Any Indian small-scale LNG environmental clearance; any announced Indian midscale liquefaction project.
- Refinery tank/sphere counts for most sites (only the HRRL utilities package).
- Numaligarh cost: NRL cites 37,720 crore here and 33,901 in another document; unresolved.

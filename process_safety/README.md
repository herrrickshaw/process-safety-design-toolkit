# process_safety: standards-based safety design calculators

Dependency-free Python (stdlib only). Built from the safety topics in the iFluids Engineering brochure (HAZOP/QRA/SIL, relief and
flare, fire and gas, SIMOPS...), the standards you listed (OISD, PESO, MSIHC 1989, OSHA PSM, CCPS, IEC 61511) and the API relief
and flare standards. `python3 -m process_safety coverage` prints the topic -> standard -> code map.

**Not a safety case.** The standards are paywalled and were not read. Formulas are derived from first principles and unit-tested
against the API constants (13160, 17.9, 11.78, 190.5), with the remaining coefficients flagged below. A competent engineer must
verify every input and every flagged value against the current edition before any design use.

## Modules

| Module | Implements | Basis | Confidence |
|---|---|---|---|
| `relief.py` | Gas/vapour (critical + subcritical), steam (Napier), liquid (Kv iteration) PSV area; API 526 orifice pick; accumulation 10/16/21 %; fire heat input `43 200·F·A^0.82` W; wetted area of cylinders; governing-case selection | API 520-I, 521, 526 | equations cross-checked in tests; Kd, Kv curve, Napier Kn, fire constants, orifice table are from memory of the standards, verify |
| `flare.py` | Point-source radiation, safe distances for 1.58/4.73/6.31/9.46 kW/m², Hajek-Ludwig radiant fraction, tip diameter by Mach | API 521 | point source is unreliable inside ~2 flame lengths (warned); allowable levels from secondary sources |
| `sil.py` | LOPA (frequency x IPL PFDs vs tolerable), required SIL, PFDavg 1oo1/1oo2/2oo2/2oo3 with beta, SIF sum, max proof-test interval | CCPS LOPA, IEC 61511/61508-6 | 1oo2/2oo3 validated vs numerical averaging (simplified form is ~1 % conservative); **no HFT/SFF architectural check** |
| `fireball.py` | BLEVE fireball size, duration, emissive power, flux vs distance, thermal dose | CCPS/Roberts | coefficients (5.8 m^1/3, 0.45 m^1/3) from secondary sources, check Roberts 1982 (open PDF below) |
| `tank_venting.py` | API 2000 normal venting (Table 2B interpolation + liquid movement), fire-exposure venting (Eq 1B, 2B, Table 3B, Table 4B F-factors), wetted area, emergency-vent shortfall | API 2000 **5th ed. 1998, text read** (public); 7th ed. thermal method NOT implemented | Eq 1B reproduces every Table 3B row within 1% except two printed-table quirks (110 m2: +4%, 19 m2: +1.1%, both the standard's own values); L must be J/kg in Eq 1B though the text says kJ/kg |
| `standards.py` | Coverage map + OISD list (105 standards, titles/editions fetched from oisd.gov.in on 2026-09-21 by the refinery repo) | OISD | list verified; contents not read |

## CLI examples

```bash
python3 -m process_safety relief-fire --D 2.5 --L 8 --level 1.5 --latent 330     # wetted area, heat input, relief rate
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1000 --case fire --M 44 --k 1.13 --Z 0.9
python3 -m process_safety lopa --ie 0.1 --ipl 0.1 0.01 --target 1e-6              # -> required PFD, SIL
python3 -m process_safety pfd --arch 1oo2 --lambda-du 2e-6 --ti-years 1 --beta 0.05
python3 -m process_safety tank-normal --volume 5000 --fill 400 --empty 500 --volatile
python3 -m process_safety tank-fire --shape vertical --D 20 --L 15 --F bare --normal-capacity 1500
python3 -m process_safety flare --mass 20 --lhv 46 --mw 30 --flame-length 40
python3 -m unittest discover tests
```

## How these are designed in different scenarios (open literature found)

| Topic | Scenario logic | Open-access source found |
|---|---|---|
| PSV scenarios | Blocked outlet, external fire, control-valve failure, thermal expansion, tube rupture, runaway reaction, utility failure: size each, the largest governs | No open peer-reviewed review found; only vendor/tutorial pages. Two-phase/runaway: DIERS (AIChE) |
| Flare radiation | Point-source `K = τ F Q / 4πD²`; F ≈ 0.2 methane, 0.33 propane, 0.4 heavier | [Honeywell/Callidus flare fundamentals deck](https://uop.honeywell.com/content/dam/uop/en-us/documents/equipment-aftermarket/callidus-technologies/training/Day%203%20Oct%207%202020%20Flare%20Fundimentals.pdf); [Utah: empirical flare methods vs CFD](https://collections.lib.utah.edu/ark:/87278/s6324z24) |
| LOPA / SIL | IE frequency x IPL PFDs -> required PFD -> SIL band; pitfalls and uncertainty in target PFD | [King, IChemE Hazards XXI](https://www.icheme.org/media/9671/xxi-paper-043.pdf); [Beedle, Hazards 30 worked example](https://www.icheme.org/media/25678/hazards-30-paper-08-beedle.pdf); [TUV risktec LOPA vs risk graphs](https://risktec.tuv.com/wp-content/uploads/2018/10/on-the-use-of-lopa-and-risk-graphs-for-sil-determination-as-published-mkopsc-2014.pdf); [arXiv SIL allocation](https://arxiv.org/pdf/2506.02309) |
| BLEVE / fireball | Size and duration scale with mass^(1/3); radiate a fraction of combustion energy | [Roberts 1982, IChemE Symp. 71](https://www.icheme.org/media/25180/the-assessment-of-major-hazards-icheme-symposium-series-71-1982-14-roberts.pdf); [DNV Phast fireball theory/validation](https://myworkspace.dnv.com/download/public/phast/technical_documentation/07_fire_models/Fireball%20Model%20Theory_Review_Validation.pdf); [InTechOpen chapter](https://www.intechopen.com/chapters/72656) |
| Regulatory map | OISD (e.g. STD-106 relief and disposal, 116 fire protection, 118 layouts), PESO, MSIHC 1989, OSHA PSM, CCPS RBPS | [OISD](https://oisd.gov.in/), [OSHA PSM](https://www.osha.gov/process-safety-management/standards) |

## Gaps (not implemented)

QRA (pool/jet fire, explosion, toxic dispersion: use DNV Phast/Safeti as iFluids does), fire-water hydraulics (OISD-STD-116 values
not read), layout separation (OISD-STD-118), hazardous-area classification, F&G mapping, vapour-filled fire case, SIL HFT/SFF constraints, HAZOP worksheets. Natural next modules: vapour-filled fire case (API 521), vent/PV-valve flow-curve selection, then API 2000 7th-ed. thermal method once the text is obtained.

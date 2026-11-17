# Units: SI and US customary

The toolkit calculates in SI. Every command takes SI numbers by default; add `--units us` before the command name and type the same
case in US-customary units. The calculation is identical, only the numbers you type and the extra output keys change.

```bash
# SI
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1500 --case fire --M 44 --k 1.13 --Z 0.9
# the same case in US units: 26455.5 lb/h, 260.33 degF, 217.557 psig
python3 -m process_safety --units us relief-gas --W 26455.5 --T 260.33 --set-g 217.557 --case fire --M 44 --k 1.13 --Z 0.9
```

With `--units us` every numeric result whose key ends in a unit token also gets a US sibling next to it
(`required_area_mm2` is joined by `required_area_in2`, `G_kg_m2_s` by `G_lb_ft2_s`, `P_kPa` by `P_psia`). The SI keys are always kept.

## Fill-in templates

```bash
python3 -m process_safety template --list                     # commands that have a template
python3 -m process_safety --units us template relief-gas > in.json   # a US-unit template (or: template relief-gas --system us)
# edit "inputs" in in.json (null means required), then
python3 -m process_safety run in.json
python3 -m process_safety template --all > inputs_all.csv     # every parameter, SI and US units and ranges, as a table
```

`docs/INPUT_TEMPLATES.md` lists every command's parameters; `templates/inputs/<command>.<si|us>.json` has a ready file for each, and
`templates/inputs_all.csv` opens in a spreadsheet. The file's `units` field decides how the numbers are read, so a US file run on
another machine cannot silently be read as SI. Each `_guide` entry names the unit, the accepted hard and soft range in that unit,
the default and the meaning of the argument.

## Quantities and their US counterparts

| Quantity | SI unit the command works in | US unit used with `--units us` | Exact relation |
|---|---|---|---|
| length | m | ft | 1 ft = 0.3048 m |
| small length, thickness | mm | in | 1 in = 25.4 mm |
| area | m2, mm2 | ft2, in2 | from the lengths |
| volume | m3 | ft3 | from the length |
| liquid volumetric flow | m3/h | gpm (US gallon per minute) | 1 gal = 231 in3 = 3.785411784 L |
| mass | kg | lb | 1 lb = 0.45359237 kg |
| mass flow | kg/s, kg/h, g/s | lb/s, lb/h, lb/h | from mass and time |
| density | kg/m3 | lb/ft3 | from mass and length |
| specific volume | m3/kg | ft3/lb | |
| pressure, gauge | kPag, barg | psig | 1 psi = 1 lbf/in2 = 6.894757... kPa |
| pressure, absolute | kPa abs | psia | |
| stress, yield strength | MPa | ksi | 1 ksi = 1000 psi |
| temperature (a reading) | K, degC | degF | degF = (K x 9/5) - 459.67 |
| temperature rise (a difference) | K (shown as dK) | dF | 1 dF = 5/9 dK, no offset |
| energy per mass | kJ/kg, MJ/kg | Btu/lb | International Table Btu = 1055.05585262 J |
| specific heat | kJ/kg/K | Btu/lb/degF | 1 Btu/lb/degF = 4.1868 kJ/kg/K |
| velocity | m/s | ft/s | |
| heat flux, radiation | kW/m2 | Btu/h/ft2 | 1 kW/m2 is about 317 Btu/h/ft2 |
| heat-transfer coefficient | W/m2K | Btu/h/ft2/degF | |
| molar mass | kg/kmol | lb/lbmol | numerically equal, factor 1 |
| per length (section factor, extinction) | 1/m | 1/ft | |
| illuminance | lux | fc (foot-candle = lumen per ft2) | 1 fc = 10.7639 lux |
| viscosity | cP | cP | same unit in both systems |
| electrical (kV, kA, A, ohm m), dBA, ppm, time, frequency, tonnes, dates | unchanged | unchanged | same in both systems |

Every factor comes from a definition (inch, pound, gallon, standard gravity, International Table Btu), not from a remembered value.
`python3 -m process_safety convert --table` prints all of them.

## What `convert` is for

The JSON tools (`tool bowtie`, `qra`, `compliance` ...), `insurance` and the Python API take SI inside their files and are not
rescaled by `--units`. Convert the numbers when you write the file:

```bash
python3 -m process_safety convert 150 psig kPag             # 1034.2 kPag
python3 -m process_safety convert 0 psig psia --across-atmosphere   # 14.696 psia, gauge to absolute on purpose
python3 -m process_safety convert 212 degF degC             # 100
python3 -m process_safety convert 10 dF dK                  # 5.556, a difference
```

## The differences that cause mistakes

1. **Gauge is not absolute.** psig and kPag are gauge; psia and kPa abs are absolute. They differ by the atmosphere (101.325 kPa =
   14.696 psi). Converting psig to psia is refused unless you pass `--across-atmosphere` (or call `gauge_to_abs`). The toolkit
   names the basis in every flag: `--set-g` and `--back-g` are gauge, `--p0` for blowdown is absolute. Check the `unit` in the
   template before you type a pressure.
2. **A temperature reading is not a temperature difference.** 100 degF is 310.9 K, but a rise of 100 dF is 55.6 dK. Arguments such as
   the cooling-water `--delta-t` and the seawater `--sw-dT` are differences and convert by the factor only.
3. **lb is mass, lbf is force.** psi is pounds-force per square inch; lb/ft3 is pounds-mass per cubic foot. `lb/lbmol` equals
   `kg/kmol`; that is a coincidence of the definitions, not a missing conversion.
4. **US gallons, not imperial.** gpm here is the US gallon (3.785 L); the imperial gallon is 4.546 L. Barrels (42 US gal) are not offered.
5. **Standard volumes are not converted.** scf, Nm3 and Sm3 are tied to reference temperatures that differ between standards
   (0, 15, 15.6, 20 C). The toolkit does not convert them, because a conversion would hide the choice; give a mass flow instead.
   (Where a command uses Nm3/h by its own definition, the reference state is stated in its help.)
6. **Tonnes are metric tonnes.** The Seveso quantities are metric tonnes; short tons (2000 lb) and long tons are not accepted.
7. **mm and in.** Wall thickness is `--wall-mm` in SI and inches in US; the `blowdown --hole-d` is in metres (not millimetres) and in feet.
8. **Radiation.** kW/m2 and Btu/h/ft2 differ by a factor of about 317; an OSHA or API flux limit quoted in one unit must be converted before it is
   compared with a result in the other.
9. **Data in the Python API and JSON files are SI.** `--units us` does not touch them.
10. **Help text quotes SI.** The `--help` text says "kg/h", "K", "kPag"; the template's `unit` field is what applies under `--units us`.

## Where US customary is the native system of a source

Some sources are written in US units and the toolkit keeps their basis visible instead of silently re-deriving it:

- 49 CFR 192.903 potential impact radius `r = 0.69 sqrt(p d^2)` ft with p in psi and d in inches (`pipeline`, returned in metres).
- OSHA 1910.119 Appendix A thresholds in pounds (`psm-check`, shown in lb and kg), EPA 40 CFR 68 thresholds in pounds (`rmp-check`),
  and the 1 psi overpressure endpoint (`rmp-worst`).
- The erosional-velocity constant C = 100 of API RP 14E is a US-unit constant (ft/s with density in lb/ft3). `hydraulics.erosional_velocity_m_s`
  converts it; scenario HYD-03 checks it from the definitions of the foot and the pound.
- API 520 and API 2000 formulas appear in both unit systems in the standards; the toolkit codes the SI form and the scenario suite
  checks that a US-unit input gives the same answer (docs/SCENARIO_REPORT.md, `si_us` column).

## How it is tested

`python scripts/run_scenarios.py --check` runs 150+ design scenarios. Every command-line scenario whose command takes dimensioned numbers is
run twice, once in SI and once in US units through `--units us`, and the two answers must agree to a relative 1e-9; each US sibling key
must equal the conversion of its SI value. `tests/test_units.py` checks the factors against the definitions and the gauge/absolute
and difference-versus-reading rules. See `docs/SCENARIO_REPORT.md`.

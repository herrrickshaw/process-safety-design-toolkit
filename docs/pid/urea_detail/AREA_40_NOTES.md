> **Rev C2 note:** the balance was rebased on sourced values after this file was written (see REBASE_REVC.md). Flow and duty numbers quoted below are from the earlier Rev B balance and are superseded by the registers and the sheets; assumptions and open items still apply.

# Area 40: sour CO shift, heat recovery, gas cooling, condensate knock-out

Generator: `scripts/urea_area_40.py` (`build(pkg)`, run it directly for /tmp/area40.html and the lint). 15 sheets, numbers 401-415, area digit 4, tags such as LIC-41421.
Basis: Rev B balance scaled by K = 3850 / Rev B urea t/d = 1.2784 (D). Rev B streams used: 4, 6, 7, 8, 9, 28 (V-203 closure). Tag S / D / A as in `pid_unit.py`.

## Sheets
| No. | Tag | Unit |
|---|---|---|
| 401 | G-201 | raw-gas guard bed (catalyst protection) |
| 402 | X-201 | HP steam addition and mixing to R-201 (stream 6) |
| 403 | E-201 | R-201 feed / effluent exchanger |
| 404 | H-201 | start-up heater (steam heating nitrogen circulation) |
| 405 | R-201 | HT sour shift, 2 beds |
| 406 | E-202 | R-201 interbed steam generator (HP) |
| 407 | E-102 | interstage cooler HT to LT (LP steam) |
| 408 | X-202 | steam addition to R-202 (stream 8) |
| 409 | R-202 | LT sour shift, 2 beds |
| 410 | E-204 | R-202 interbed cooler (BFW heating) |
| 411 | E-205 | shift effluent / HP BFW heater |
| 412 | E-203 | shift gas / DM-water heater (condensing) |
| 413 | E-103 | shift gas cooler (cooling water) |
| 414 | V-203 | condensate KO drum + P-203A/B (pilot call, renumbered) |
| 415 | CP-201 | shift-area SIS and catalyst-protection loops (package sheet) |

New streams (ids of at most 3 chars): 4C, 4G, 4M, 4F, 7B, 7I, 7C, 7E, 8M, 8B, 8I, 9A, 9B, 9C, 9V (gas side, species from Rev B, flows = Rev B x K, mass closure asserted); utilities 4H1-4H4, 4B1-4B8, 4D1-4D2, 4W1-4W2 (flows from the duty of the exchanger they serve).

## How the train was built (all in code)
* Each shift stage is two adiabatic beds in series with an external interbed cooler. Bed temperature rise comes from the Rev B WGS equilibrium constant (`wgs_K_thermo`, S) and Rev B reaction heats (S), with the Rev B approach temperatures (20 K HT, 10 K LT). Mean heat capacities are A (+-10 %).
* HT: bed 1 280 to 505 C, interbed to 300 C, bed 2 to 362 C, CO conversion 77.6 % (Rev B 79.1 %, stream 7 is 350 C). LT: bed 1 205 to 258 C, interbed to 195 C, bed 2 to 205 C, conversion 90.0 % (Rev B 86.8 %). CO slip to V-203 about 35 mol/s against 47 mol/s in Rev B (scaled).
* A SINGLE adiabatic bed cannot deliver the Rev B conversions: the HT heat of reaction (about 50 MW scaled) gives a temperature rise of more than 250 K, so the Rev B 350 C is an equilibrium temperature, not an adiabatic outlet. Rev B streams 7 and 9 are kept as given; the bed temperatures are on the notes of sheets 405 and 409. Bed-1 exit 505 C is within 15 K of the 520 C screening limit (A, 480-540): this is the highest-risk number in the area.
* Dew points (D, Antoine A, checked in code against the Rev B CoolProp Psat at 40 C within 2 %): HT mixed gas 206 C, LT mixed feed 178 C, stream 9 166 C. Mixed-gas temperatures are asserted at least 20 K above dew point.
* Duties (MW, D): E-201 3.4, E-202 37.2, E-102 26.8, E-204 12.8, E-205 28.4, E-203 28.6, E-103 16.5. Total condensate over E-205, E-203, E-103 equals Rev B stream 28 within 2 % (asserted).
* Mass closure asserted: 4G + 6 = 4M = 7; 7E + 8 = 8M = 9; V-203 9 = 9V + 28.

## Decision: no COS hydrolysis reactor
Not drawn. Rev B carries sulphur only as H2S (no COS in stream 4), the sour-shift catalyst hydrolyses COS in R-201 / R-202 itself, and every gas path passes the shift. A separate hydrolysis reactor would be needed only if part of the raw gas bypassed the shift, which the Rev B flowsheet does not do. If a licensor shows COS in stream 4, add a COS hydrolysis bed after G-201 (A).

## A assumptions (range)
Raw gas after E-101 215 C (200-240); bed inlets HT 280 / 300 C (270-310), LT 205 / 195 C (195-215); bed catalyst volume = gas flow x 30 s (20-60), guard 20 s (10-40); mean cp 29.5-44 J/mol/K (+-10 %); latent heat of water 2,250 kJ/kg (2,080-2,400); steam latent 1,650 (50 bar) and 2,100 (6 bar) kJ/kg (+-5 %); BFW 105 C, cooling water rise 10 K; start-up nitrogen 10 % of design mass flow (5-15 %); alarm and trip values on the CP-201 sheet; materials left to the licensor.

## Gaps and template defects
* Not sized: relief loads (PSV rows say "not sized"), boiler drums and steam-side relief, bed reheat control, catalyst loading and sulphiding procedure. Pressure drop across the train is not in Rev B (all shift streams 45 bar).
* E-205 / E-203 duties imply BFW 160 t/h and DM water about 330 t/h: plant-wide water and steam balance is not available.
* Template: `sheet_reactor` trip TAHH = effluent + 60 C (410 C on R-201 against a 505 C bed-1 exit; the real trip is on CP-201), `sheet_reactor` draws one inlet and outlet so the interbed loop is described in notes; `sheet_hx` and `sheet_package` labels overlap (duty label with drain/vent valves on exchanger sheets; XV tag with line label on package sheets), data-panel text longer than about 46 characters runs out of the panel (hazard and type rows were shortened).
* No separate sheet for a start-up N2 header, nor for the sour-water stripper (area 300).

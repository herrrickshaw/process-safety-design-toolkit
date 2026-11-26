# Model assumptions against the facts in the sources

Second look at the seven errors left above 10 %, using the primary documents again and four additional ones. Each item states what the toolkit assumed, what the sources say, and a corrected verdict. **Several verdicts differ from the earlier summary**; those are marked CORRECTED.

Sources read in full or in the cited section: RIVM 620550005/2012 ([RIVM](https://www.rivm.nl/bibliotheek/rapporten/620550005.pdf)); DNV JFSH Jet Fire Model Validation, Dec 2023 ([DNV](https://mysoftware.dnv.com/download/public/phast/technical_documentation/07_fire_models/JFSH%20Jet%20Fire%20Model%20Validation.pdf)); Witlox et al., two-phase jet droplet size, Phase III JIP ([AMS paper](https://ams.confex.com/ams/pdfpapers/163608.pdf)); Johnson, Brightwell, Carsley, IChemE Symposium Series 134, paper XII-09 ([IChemE](https://www.icheme.org/media/12116/xii-paper-09.pdf)); Cracknell et al., IChemE Symposium Series 139 ([IChemE](https://www.icheme.org/media/25321/major-hazards-onshore-and-offshore-ii-icheme-symposium-series-139-1995-13-cracknell.pdf)). Search snippets only (not read in full): the HEM pipe-flow literature items in section 8.

## 1. Project AA 3029 release rate: model -14 %

| | |
|---|---|
| Our assumption | HEM line model, 67 m x 152 mm then 13 m x 52 mm, roughness 1.5 micron, entrance K 0.5, no fittings, vessel state from RIVM Table 4. |
| Facts | Geometry and roughness agree in both RIVM and DNV. DNV states that **its own discharge model agrees with measured flow for every Bennett test except 3026 and 3029**, and for those two it runs the line-rupture model with the upstream pressure varied until the measured rate is matched. A pressure sensor 150 mm upstream of the orifice read 4.6 barg for 3029; there was no reading for 3026. Our model gives 4.2 barg at the choked exit for 3029 (-9 %) and 4.6 barg for 3026. |
| Sensitivity (this review) | Entrance K 0.5 to 0 changes the rate by under 1 %. Roughness 1.5 to 15 micron lowers it by about 10 % (14.7 to 13.2 and 15.5 to 13.8 kg/s). DNV also tested both roughness values. |
| Direction of bias | HEM normally **over**-predicts flashing flow at high quality; the delayed-equilibrium literature reports it roughly 50 % high for one organic fluid, against 10 % with a delayed model (snippet). Ours is low, so the cause is more likely the rig description (unknown valves, bends, vessel nozzle) or the flow measurement than the flashing physics. |
| Verdict | **Not a model error that can be separated from rig data.** -8 % and -14 % bracket the measured value, the independently measured exit-side pressure agrees within 9 %, and DNV could not predict these two tests either. Status: open, data-limited. |

## 2. JIVE 8051 release rate: model +516 %

| | |
|---|---|
| Our assumption | Vessel at the "driving pressure" 19.85 bar(a) and 1.9 C (RIVM Table 4) feeds the line and a 40 mm discharge. |
| Facts | DNV records no pressure or temperature reading near the orifice for the 79 m line in its text, but its input table lists a pressure upstream of the orifice of **about 1.6 barg** for 8051 and a vessel temperature of **13.9 C** (RIVM says 1.9 C; the two sources disagree). DNV again tunes the upstream pressure to hit 6.86 kg/s. A plain 40 mm orifice at 19.85 bar(a) passes 37.7 kg/s; at the 2.6 bar(a) near-orifice pressure the same orifice passes about 10 kg/s (+50 % on 6.86). |
| Sensitivity | Using 13.9 C instead of 1.9 C changes the model rate by under 3 % (42.3 to 41.2 kg/s). |
| Verdict | **CORRECTED.** The error is not "something unknown in the rig"; it is that **the vessel driving pressure is not the pressure at the discharge**: about 17 bar was lost between vessel and orifice (valves or a throttled line). The implied K of 73 is that loss, expressed as a coefficient. The toolkit has no way to know it, so a line-fed prediction needs the measured near-orifice pressure as input. Open: the JIVE report (Sekulin and Acton) was not obtained. |

## 3. Droplet size: 27 to 71 % off the EEC STEP data

| | |
|---|---|
| Our assumption | Weber-limited breakup, C_ds 15 (Yellow Book 2.143b), at the discharge state. |
| Facts | STEP droplets were measured 60 mm downstream. The Phase III JIP scaled experiments measured 250 mm (flashing) and 500 mm (subcooled) downstream, on water, cyclohexane, butane, propane and gasoline. The Phase III correlation is **tri-linear in superheat**: mechanical breakup, a transition to flashing, and a fully flashing branch. It replaced the CCPS/Weber form used in Phast and, per the authors, agrees better with the STEP and large-scale butane data. |
| Verdict | **CORRECTED.** My earlier statement "no better sourced correlation exists" was wrong: one exists (Kay, Bowen and Witlox 2009 give the equations), I do not have it. The Weber form we use is the mechanical-breakup branch and is the wrong regime for a flashing propane jet at 5 to 17 bar; the 27 to 71 % error is therefore expected, not random. Measurement distance also differs between data sets, so a model value at the nozzle cannot be compared to an SMD at 60 mm without evaporation and breakup downstream. Status: open, equations needed. |

## 4. Flame length: +25 %, +64 %, +85 %

| | |
|---|---|
| Our assumption | Measured length = flame length L_B along the centreline. |
| Facts | RIVM: the reported AA lengths are the **time-averaged horizontal length of the visible flame**, "a little larger than" the 20 % occurrence contour, and the radiant flame is usually bigger than the visible one because soot hides the tail. For 3029 the value 30.7 m comes from a Shell internal document; the report quoted 25.9 m, judged erroneous. For JIVE 8051 the report gives no length: 18.3 m is read off a figure (20 % occurrence at 6 m height; the 50 % contour is about 16.6 m). DNV says the 8051 value is an estimate and notes the report mentions a 40 degree angle against 73 to 75 degrees used. The models are "cautiously realistic" by design (conservative length, accurate radiated heat). RIVM rates JFSH-Cook "poor" for 3029 and 8051, Barker "good" and "reasonable", Cracknell "reasonable" for both; JFSH-Cook has no lift-off, while JIVE 8051 shows pronounced buoyancy. |
| Verdict | **CORRECTED.** Not only "model bias". The three data points differ in definition and quality (visible horizontal length vs centreline length; one value from an unpublished document; one read off a graph). Real, separate model gap: no buoyant lift-off in the Cook form, which shortens the horizontal reach for butane. Status: partly definition/measurement, partly the model's missing buoyancy; Cracknell and Barker equations still needed. |

## 5. Surface emissive power: 19 to 27 % low

| | |
|---|---|
| Our assumption | The measured values (331, 294 kW/m2) are comparable mean flame values. |
| Facts | Confirmed: RIVM Table 5 note 5 says the AA values are the **mean flame SEP averaged over 10 to 15 s**, so they are comparable. (The BFETS values are maxima and the JIVE values are spot values; RIVM excludes them from comparison, and so should we.) RIVM and DNV both attribute the low mean SEP to **over-predicted flame surface area at a correctly predicted radiated heat**. |
| Check (this review) | If radiated heat is right, SEP scales as 1/area. For 3029 the model length is +61 % over the measured 30.7 m (DNV 49.4 m) and the SEP ratio is 197/294 = 0.67, i.e. area about 1.5 times; for 3026 length +23 %, SEP ratio 253/331 = 0.76. The two errors are **one error seen twice**, not two independent ones. |
| Verdict | **CORRECTED.** SEP and flame length are linked through area; fixing the length would fix the SEP. JFSH-Cook also cuts SEP at 350 kW/m2 (Chamberlain, private communication), which is binding for the JIVE cases. Shell's own model gives the flame ends and sides different SEP through a grey-gas path-length term (XII-09), which the Cook form lacks. |

## 6. Jet velocity against Barker

Facts: no velocity was measured ("not reported", RIVM Tables 5 to 7). The tools disagree with each other on the same butane test: SAFETI-NL JFSH-Cook 9.3 m/s, Barker 15, Cracknell 28, Phast 46. **Verdict: unmeasurable; a comparison between model states, not an error.** Reclassified, no action.

## 7. INERIS vertical flames, "passes" and the no-wind case

Facts: jet velocity (40 m/s) and wind (3 m/s) were **assumed** because the sources do not publish them. The four passes (-7 % to +3 %) therefore depend on assumptions; the no-wind +57 % shows how much. **Verdict: CORRECTED.** Treat the INERIS rows as conditional passes, not validation.

## 8. Other checks on the line model

* HEM is reported to work well for long pipes and to over-predict where the quality is high or the pipe short (snippets: [Politecnico di Milano](https://re.public.polimi.it/bitstream/11311/1072768/4/11311-1072768%20Dossena.pdf), [AIDIC](https://www.aidic.it/cet/12/26/011.pdf)). The AA lines are 80 m long, which is the favourable case.
* Bug found during this review: a low-pressure trial flow could make the solver call a property correlation with a negative pressure; fixed in `line_flow.py` (entrance loss larger than the head now counts as infeasible) with a regression test.

## 9. Revised scorecard

Of the 19 comparisons above 10 % in the validation sheet:

| Class | Count | Items |
|---|---|---|
| Wrong regime in the model | 4 | droplet size (Weber branch used for a flashing jet) |
| Input or rig data missing | 5 | AA 3029 and 3026 flux, JIVE rate (vessel pressure is not the discharge pressure), AA flux |
| Definition or measurement mismatch | 6 | three flame lengths, three more with the DNV-model rows |
| One cause, counted twice | 2 | SEP (area over-prediction) |
| Not a measurement | 2 | Barker velocities |

Counts are approximate groupings of rows, not independent errors.

## 10. What would close each item

1. Kay, Bowen and Witlox (2009), the Phase III SMD equations, to replace the Weber branch for flashing jets.
2. Sekulin and Acton JIVE report, and the Bennett et al. 1991 overview (Davenport, Bennett, Cowley, Rowson), for pressures, valves and flame definitions.
3. The Barker and Cracknell papers, for lift-off and area, which would fix both length and SEP.
4. Pressure and temperature histories near the orifice for 3026, which was never recorded.

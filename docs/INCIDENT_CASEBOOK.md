# Process safety incident casebook

Generated from `process_safety/data/incident_casebook.json`. Regenerate with `python -m process_safety casebook --markdown > docs/INCIDENT_CASEBOOK.md`. Search with `python -m process_safety casebook --country India` or `--topic facility-siting`.

## Read this first

- 78 historical cases from 38 countries and territories, compiled 2026-11-26 for teaching and safety discussions. It is a **selection**, not a complete record: a country's count says nothing about how safe it is, and a missing incident is not a minor one.
- Best source read per case: A (official) 25, B (professional, peer reviewed or an official summary page) 36, C (secondary) 17. Grade C accounts need checking against an inquiry report before they are relied on. The grade is that of the best source, which may support only part of an account: read *How far the sources go* on the case sheet.
- Checked once: after the research, agents that had not written the records compared all 78 cases with the saved source texts (no new searches) and raised 122 findings, of which 22 were plain errors. 101 were applied; 21 were rejected: source-grade upgrades against the grading rule above, and a suggestion to cite a copy that was not obtained within the source-fetching rules. The corrected text was not audited again, long reports were read in the relevant parts only, and the audit cannot catch an error in a source.
- Learnings marked *[source]* are drawn by a source that was read; *[compiler]* are this toolkit's interpretation. Discussion questions and topic prompts are the compiler's.
- Death tolls are often disputed or revised. `not stated` means the pages read did not give a figure.
- Cases involve real people. Teach the decisions and conditions, not blame.

## How to run a case discussion

1. Give the group the place, the plant and the day, not the outcome. Ask what could go wrong.
2. Walk through what happened. Separate what an inquiry established from what is disputed or unknown.
3. Ask which barriers existed on paper, which existed on the day, and who knew the difference.
4. Use the two case questions, then the topic prompt.
5. End on your own site: name one thing to check this month, who will check it and how you will know.

## Roster

| Date | Case | Country | Sector | Deaths | Best source |
|---|---|---|---|---|---|
| 1917-12-06 | Halifax Explosion (`halifax-1917`) | Canada | ports and warehousing | 1946 (see note) | B |
| 1921-09-21 | Oppau fertiliser silo explosion (`oppau-1921`) | Germany | explosives and fertiliser | 507 (see note) | B |
| 1944-10-20 | East Ohio Gas LNG tank failure and fire (`cleveland-lng-1944`) | United States of America | LPG/LNG | 130 (see note) | A |
| 1947-04-16 | Texas City ammonium nitrate ship explosions (`texas-city-1947`) | United States of America | ports and warehousing | not stated (see note) | B |
| 1966-01-04 | Feyzin refinery propane sphere BLEVE (`feyzin-1966`) | France | LPG/LNG | 18 (see note) | B |
| 1974-06-01 | Flixborough (Nypro UK) vapour cloud explosion (`flixborough-1974`) | United Kingdom of Great Britain and Northern Ireland | chemicals | 28 | B |
| 1975-11-07 | DSM Beek naphtha cracker explosion (`beek-1975`) | Netherlands (Kingdom of the) | chemicals | 14 | B |
| 1976-07-10 | Seveso (ICMESA) dioxin release (`seveso-1976`) | Italy | chemicals | 0 (see note) | B |
| 1978-07-11 | Los Alfaques campsite propylene tanker disaster (`los-alfaques-1978`) | Spain | transport | 215 (see note) | C |
| 1984-02-24 | Vila Soco (Cubatao) gasoline pipeline fire (`cubatao-1984`) | Brazil | pipeline | 93 (see note) | C |
| 1984-05-23 | Abbeystead valve house methane explosion (`abbeystead-1984`) | United Kingdom of Great Britain and Northern Ireland | pipeline | 16 | B |
| 1984-11-19 | San Juan Ixhuatepec LPG terminal disaster (`ixhuatepec-1984`) | Mexico | LPG/LNG | 542 (see note) | B |
| 1984-12-03 | Bhopal methyl isocyanate release (`bhopal-1984`) | India | chemicals | 3787 (see note) | B |
| 1986-11-01 | Sandoz Schweizerhalle warehouse fire and Rhine pollution (`schweizerhalle-1986`) | Switzerland | ports and warehousing | not stated (see note) | B |
| 1987-03-22 | BP Grangemouth hydrocracker explosion (`grangemouth-1987`) | United Kingdom of Great Britain and Northern Ireland | refining | 1 (see note) | B |
| 1988-05-05 | Shell Norco refinery catalytic cracker explosion (`norco-1988`) | United States of America | refining | 7 (see note) | C |
| 1988-07-06 | Piper Alpha offshore platform disaster (`piper-alpha-1988`) | United Kingdom of Great Britain and Northern Ireland | oil and gas upstream | 167 (see note) | A |
| 1989-06-04 | Ufa (Asha) NGL pipeline and passenger train disaster (`ufa-1989`) | Russian Federation | pipeline | 575 (see note) | C |
| 1989-10-23 | Phillips 66 Houston Chemical Complex explosion (`pasadena-1989`) | United States of America | chemicals | 23 | B |
| 1991-05-07 | Bright Sparklers fireworks factory explosion (`bright-sparklers-1991`) | Malaysia | explosives and fertiliser | 22 (see note) | C |
| 1992-04-22 | Guadalajara sewer explosions (`guadalajara-1992`) | Mexico | pipeline | 210 (see note) | A |
| 1992-09-21 | Hickson & Welch jet fire (`castleford-1992`) | United Kingdom of Great Britain and Northern Ireland | chemicals | 5 | B |
| 1994-07-24 | Texaco refinery (Pembroke Cracking Company) explosion (`milford-haven-1994`) | United Kingdom of Great Britain and Northern Ireland | refining | 0 (see note) | B |
| 1994-11-02 | Dronka (Durunka) fuel depot fire and flood (`dronka-fuel-depot-1994`) | Egypt | storage and terminals | 469 (see note) | B |
| 1995-12-16 | AECI Somerset West sulphur stockpile fire (`somerset-west-sulphur-1995`) | South Africa | chemicals | not stated (see note) | A |
| 1997-09-14 | HPCL Visakhapatnam refinery LPG explosion and fire (`hpcl-vizag-1997`) | India | refining | 56 (see note) | B |
| 1998-09-25 | Esso Longford gas plant explosion (`longford-1998`) | Australia | oil and gas upstream | 2 | A |
| 1998-10-17 | Jesse (Idjerhe) petroleum pipeline fire (`jesse-pipeline-1998`) | Nigeria | pipeline | not stated (see note) | C |
| 2000-05-13 | Enschede fireworks warehouse explosions (`enschede-2000`) | Netherlands (Kingdom of the) | explosives and fertiliser | 22 (see note) | B |
| 2000-06-25 | Mina Al-Ahmadi refinery explosion (`mina-al-ahmadi-2000`) | Kuwait | refining | 5 (see note) | C |
| 2001-03-15 | P-36 production platform explosions and sinking (`p36-2001`) | Brazil | oil and gas upstream | 11 | B |
| 2001-09-21 | AZF fertiliser plant ammonium nitrate explosion (`toulouse-2001`) | France | explosives and fertiliser | 31 (see note) | B |
| 2003-09-26 | Idemitsu Hokkaido refinery tank fires after the Tokachi-oki earthquake (`idemitsu-tomakomai-2003`) | Japan | storage and terminals | not stated (see note) | B |
| 2004-01-19 | Skikda LNG plant explosion (`skikda-lng-2004`) | Algeria | LPG/LNG | 27 | A |
| 2004-02-18 | Neyshabur freight train explosion (`neyshabur-rail-2004`) | Iran (Islamic Republic of) | transport | not stated (see note) | B |
| 2004-07-30 | Ghislenghien high-pressure gas pipeline rupture (`ghislenghien-2004`) | Belgium | pipeline | 24 (see note) | B |
| 2004-09-01 | Sasol Secunda ethylene plant explosion (`sasol-secunda-2004`) | South Africa | chemicals | 10 (see note) | C |
| 2005-03-23 | BP Texas City refinery explosion (`texas-city-2005`) | United States of America | refining | 15 | A |
| 2005-07-27 | Mumbai (Bombay) High North platform fire (`bombay-high-north-2005`) | India | oil and gas upstream | 22 (see note) | B |
| 2005-11-13 | Jilin petrochemical explosions and Songhua River pollution (`jilin-2005`) | China | chemicals | 8 (see note) | B |
| 2005-12-11 | Buncefield oil depot overfill, explosion and fire (`buncefield-2005`) | United Kingdom of Great Britain and Northern Ireland | storage and terminals | 0 (see note) | A |
| 2007-11-18 | Haradh-Uthmaniyah gas pipeline fire (`haradh-pipeline-2007`) | Saudi Arabia | pipeline | 40 (see note) | C |
| 2007-12-19 | T2 Laboratories runaway reaction (`t2-2007`) | United States of America | chemicals | 4 | A |
| 2008-02-07 | Imperial Sugar dust explosions (`imperial-sugar-2008`) | United States of America | food and agriculture | 14 | A |
| 2008-04-05 | Icepak coolstore explosion and fire, Tamahere (`tamahere-coolstore-2008`) | New Zealand | food and agriculture | 1 | A |
| 2008-06-03 | Varanus Island gas pipeline rupture and fire (`varanus-island-2008`) | Australia | pipeline | 0 (see note) | A |
| 2008-08-10 | Sunrise Propane explosions (`toronto-sunrise-2008`) | Canada | LPG/LNG | 2 (see note) | A |
| 2009-06-29 | Viareggio LPG freight train derailment (`viareggio-2009`) | Italy | transport | 32 (see note) | A |
| 2009-08-21 | Montara wellhead platform blowout (`montara-2009`) | Australia | oil and gas upstream | 0 (see note) | A |
| 2009-10-29 | Indian Oil Jaipur POL terminal vapour cloud explosion (`ioc-jaipur-2009`) | India | storage and terminals | 11 (see note) | A |
| 2010-04-20 | Macondo blowout, Deepwater Horizon (`deepwater-horizon-2010`) | United States of America | oil and gas upstream | 11 | A |
| 2011-03-11 | Cosmo Oil Chiba refinery LPG sphere fire and BLEVEs (`cosmo-chiba-2011`) | Japan | refining | 0 (see note) | B |
| 2012-04-22 | Mitsui Chemicals Iwakuni-Ohtake resorcinol plant explosion (`mitsui-iwakuni-2012`) | Japan | chemicals | 1 (see note) | B |
| 2012-05-05 | Bangkok Synthetics explosion and fire, Map Ta Phut (`map-ta-phut-bst-2012`) | Thailand | chemicals | 12 (see note) | C |
| 2012-08-25 | Amuay refinery vapour cloud explosion (`amuay-2012`) | Venezuela (Bolivarian Republic of) | refining | 42 (see note) | C |
| 2012-09-18 | Reynosa Pemex gas facility fire (`reynosa-2012`) | Mexico | oil and gas upstream | 29 (see note) | C |
| 2012-09-27 | Gumi hydrogen fluoride release (`gumi-hf-2012`) | Republic of Korea | chemicals | 5 | B |
| 2012-09-29 | Nippon Shokubai Himeji acrylic acid tank explosion (`himeji-2012`) | Japan | chemicals | 1 (see note) | B |
| 2013-04-17 | West Fertilizer fire and explosion (`west-fertilizer-2013`) | United States of America | explosives and fertiliser | 15 (see note) | A |
| 2013-07-06 | Lac-Megantic runaway oil train (`lac-megantic-2013`) | Canada | transport | 47 | A |
| 2013-11-22 | Sinopec Donghuang crude oil pipeline leak and explosions (`qingdao-pipeline-2013`) | China | pipeline | 62 (see note) | B |
| 2014-06-27 | GAIL Tatipaka-Kondapalli gas pipeline explosion (`gail-andhra-2014`) | India | pipeline | 22 (see note) | C |
| 2014-07-31 | Kaohsiung underground propylene pipeline explosions (`kaohsiung-2014`) | Taiwan | pipeline | 32 | B |
| 2014-08-02 | Kunshan Zhongrong aluminium dust explosion (`kunshan-2014`) | China | metals and manufacturing | 146 (see note) | C |
| 2015-06-03 | Accra flood and GOIL filling station fire (`accra-goil-2015`) | Ghana | storage and terminals | 150 (see note) | A |
| 2015-08-12 | Tianjin port Ruihai warehouse explosions (`tianjin-2015`) | China | ports and warehousing | 165 (see note) | B |
| 2016-10-17 | BASF Ludwigshafen North Harbour pipeline fire and explosion (`ludwigshafen-2016`) | Germany | pipeline | 5 (see note) | C |
| 2017-06-25 | Ahmedpur East road tanker petrol fire (`ahmedpur-east-2017`) | Pakistan | transport | 214 (see note) | C |
| 2017-10-24 | Mongstad refinery cracker naphtha leak (`mongstad-2017`) | Norway | refining | not stated (see note) | A |
| 2019-01-18 | Tlahuelilpan pipeline explosion (`tlahuelilpan-2019`) | Mexico | pipeline | 137 (see note) | A |
| 2019-03-21 | Xiangshui Tianjiayi Chemical explosion (`xiangshui-2019`) | China | chemicals | 78 | B |
| 2019-08-10 | Morogoro fuel tanker fire and explosion (`morogoro-tanker-2019`) | United Republic of Tanzania | transport | 97 (see note) | B |
| 2020-05-07 | LG Polymers styrene vapour release (`lg-polymers-2020`) | India | chemicals | 12 (see note) | A |
| 2020-05-27 | Baghjan-5 well blowout and fire (`baghjan-2020`) | India | oil and gas upstream | 2 (see note) | A |
| 2020-08-04 | Beirut port ammonium nitrate explosion (`beirut-port-2020`) | Lebanon | ports and warehousing | 218 (see note) | B |
| 2021-03-07 | Bata explosions at Nkuantoma military barracks (`bata-barracks-2021`) | Equatorial Guinea | explosives and fertiliser | 107 (see note) | A |
| 2022-06-04 | BM Container Depot fire and explosions, Sitakunda (`sitakunda-2022`) | Bangladesh | ports and warehousing | 51 (see note) | C |
| 2023-03-03 | Pertamina Plumpang fuel terminal fire (`plumpang-2023`) | Indonesia | storage and terminals | 33 (see note) | B |

## By country

| Country or territory | Cases |
|---|---|
| Algeria | `skikda-lng-2004` |
| Australia | `longford-1998`, `varanus-island-2008`, `montara-2009` |
| Bangladesh | `sitakunda-2022` |
| Belgium | `ghislenghien-2004` |
| Brazil | `cubatao-1984`, `p36-2001` |
| Canada | `halifax-1917`, `toronto-sunrise-2008`, `lac-megantic-2013` |
| China | `jilin-2005`, `qingdao-pipeline-2013`, `kunshan-2014`, `tianjin-2015`, `xiangshui-2019` |
| Egypt | `dronka-fuel-depot-1994` |
| Equatorial Guinea | `bata-barracks-2021` |
| France | `feyzin-1966`, `toulouse-2001` |
| Germany | `oppau-1921`, `ludwigshafen-2016` |
| Ghana | `accra-goil-2015` |
| India | `bhopal-1984`, `hpcl-vizag-1997`, `bombay-high-north-2005`, `ioc-jaipur-2009`, `gail-andhra-2014`, `lg-polymers-2020`, `baghjan-2020` |
| Indonesia | `plumpang-2023` |
| Iran (Islamic Republic of) | `neyshabur-rail-2004` |
| Italy | `seveso-1976`, `viareggio-2009` |
| Japan | `idemitsu-tomakomai-2003`, `cosmo-chiba-2011`, `mitsui-iwakuni-2012`, `himeji-2012` |
| Kuwait | `mina-al-ahmadi-2000` |
| Lebanon | `beirut-port-2020` |
| Malaysia | `bright-sparklers-1991` |
| Mexico | `ixhuatepec-1984`, `guadalajara-1992`, `reynosa-2012`, `tlahuelilpan-2019` |
| Netherlands (Kingdom of the) | `beek-1975`, `enschede-2000` |
| New Zealand | `tamahere-coolstore-2008` |
| Nigeria | `jesse-pipeline-1998` |
| Norway | `mongstad-2017` |
| Pakistan | `ahmedpur-east-2017` |
| Republic of Korea | `gumi-hf-2012` |
| Russian Federation | `ufa-1989` |
| Saudi Arabia | `haradh-pipeline-2007` |
| South Africa | `somerset-west-sulphur-1995`, `sasol-secunda-2004` |
| Spain | `los-alfaques-1978` |
| Switzerland | `schweizerhalle-1986` |
| Taiwan | `kaohsiung-2014` |
| Thailand | `map-ta-phut-bst-2012` |
| United Kingdom of Great Britain and Northern Ireland | `flixborough-1974`, `abbeystead-1984`, `grangemouth-1987`, `piper-alpha-1988`, `castleford-1992`, `milford-haven-1994`, `buncefield-2005` |
| United Republic of Tanzania | `morogoro-tanker-2019` |
| United States of America | `cleveland-lng-1944`, `texas-city-1947`, `norco-1988`, `pasadena-1989`, `texas-city-2005`, `t2-2007`, `imperial-sugar-2008`, `deepwater-horizon-2010`, `west-fertilizer-2013` |
| Venezuela (Bolivarian Republic of) | `amuay-2012` |

## Key safety discussions

### Hazard identification

**Open with:** Which study should have found this scenario, and what would it have needed to be told?

**Cases:** `oppau-1921`, `abbeystead-1984`, `longford-1998`, `enschede-2000`, `p36-2001`, `toulouse-2001`, `bombay-high-north-2005`, `t2-2007`, `tamahere-coolstore-2008`, `ioc-jaipur-2009`, `xiangshui-2019`, `sitakunda-2022`

**Toolkit modules:** `hazop`, `pha`

### Facility siting and occupied buildings

**Open with:** Who was where, and did they need to be there?

**Cases:** `cleveland-lng-1944`, `flixborough-1974`, `ixhuatepec-1984`, `norco-1988`, `pasadena-1989`, `castleford-1992`, `dronka-fuel-depot-1994`, `hpcl-vizag-1997`, `skikda-lng-2004`, `texas-city-2005`, `bombay-high-north-2005`, `varanus-island-2008`, `toronto-sunrise-2008`, `ioc-jaipur-2009`, `kunshan-2014`, `bata-barracks-2021`, `plumpang-2023`

**Toolkit modules:** `explosion`, `qra`

### Land-use planning and neighbours

**Open with:** How did the distance to the public come to be what it was, and who can change it?

**Cases:** `halifax-1917`, `cleveland-lng-1944`, `los-alfaques-1978`, `cubatao-1984`, `ixhuatepec-1984`, `bhopal-1984`, `ufa-1989`, `bright-sparklers-1991`, `guadalajara-1992`, `dronka-fuel-depot-1994`, `somerset-west-sulphur-1995`, `enschede-2000`, `toulouse-2001`, `ghislenghien-2004`, `jilin-2005`, `buncefield-2005`, `west-fertilizer-2013`, `qingdao-pipeline-2013`, `accra-goil-2015`, `tianjin-2015`, `beirut-port-2020`, `bata-barracks-2021`, `plumpang-2023`

**Toolkit modules:** `qra`, `mah`

### Management of change

**Open with:** What changed, who judged it safe, and what did they not look at?

**Cases:** `oppau-1921`, `flixborough-1974`, `abbeystead-1984`, `bhopal-1984`, `grangemouth-1987`, `castleford-1992`, `milford-haven-1994`, `longford-1998`, `imperial-sugar-2008`, `tamahere-coolstore-2008`, `montara-2009`, `himeji-2012`, `lac-megantic-2013`, `gail-andhra-2014`, `mongstad-2017`, `lg-polymers-2020`

**Toolkit modules:** `psm`

### Mechanical integrity and corrosion

**Open with:** How was the equipment expected to fail, and what inspection would have seen it?

**Cases:** `cleveland-lng-1944`, `beek-1975`, `norco-1988`, `milford-haven-1994`, `longford-1998`, `mina-al-ahmadi-2000`, `idemitsu-tomakomai-2003`, `skikda-lng-2004`, `varanus-island-2008`, `viareggio-2009`, `cosmo-chiba-2011`, `amuay-2012`, `reynosa-2012`, `gail-andhra-2014`, `mongstad-2017`

**Toolkit modules:** `vessel_mech`, `psm`

### Pipeline integrity

**Open with:** How would the operator have known the line was weak or leaking, and how fast?

**Cases:** `cubatao-1984`, `piper-alpha-1988`, `ufa-1989`, `guadalajara-1992`, `jesse-pipeline-1998`, `mina-al-ahmadi-2000`, `ghislenghien-2004`, `haradh-pipeline-2007`, `varanus-island-2008`, `qingdao-pipeline-2013`, `gail-andhra-2014`, `kaohsiung-2014`, `ludwigshafen-2016`, `tlahuelilpan-2019`

**Toolkit modules:** `pipeline`

### Isolation, permits and handover

**Open with:** What did the next person believe about the state of the equipment, and why?

**Cases:** `feyzin-1966`, `ixhuatepec-1984`, `piper-alpha-1988`, `pasadena-1989`, `castleford-1992`, `hpcl-vizag-1997`, `mina-al-ahmadi-2000`, `p36-2001`, `sasol-secunda-2004`, `haradh-pipeline-2007`, `ioc-jaipur-2009`, `cosmo-chiba-2011`, `map-ta-phut-bst-2012`, `reynosa-2012`, `gumi-hf-2012`, `ludwigshafen-2016`, `mongstad-2017`

**Toolkit modules:** `psm`

### Contractors and interfaces

**Open with:** Which risk fell between two organisations?

**Cases:** `pasadena-1989`, `ghislenghien-2004`, `sasol-secunda-2004`, `haradh-pipeline-2007`, `viareggio-2009`, `montara-2009`, `deepwater-horizon-2010`, `reynosa-2012`, `ludwigshafen-2016`, `ahmedpur-east-2017`, `baghjan-2020`

**Toolkit modules:** `psm`

### Start-up, shutdown and abnormal operation

**Open with:** What was different from normal running, and which safeguards assumed normal running?

**Cases:** `beek-1975`, `grangemouth-1987`, `texas-city-2005`, `mitsui-iwakuni-2012`, `map-ta-phut-bst-2012`, `lg-polymers-2020`

**Toolkit modules:** `depressuring`, `overfill`

### Overfill and level control

**Open with:** What stops the filling if the indication is wrong?

**Cases:** `texas-city-2005`, `buncefield-2005`

**Toolkit modules:** `overfill`, `tank_venting`

### Relief, venting and disposal

**Open with:** Where does the material go when containment is relieved, and is that place safe?

**Cases:** `seveso-1976`, `grangemouth-1987`, `milford-haven-1994`, `texas-city-2005`, `t2-2007`

**Toolkit modules:** `relief`, `flare_system`

### Reactive and runaway hazards

**Open with:** What can this material do on its own if it gets warmer, older or mixed?

**Cases:** `oppau-1921`, `texas-city-1947`, `seveso-1976`, `bhopal-1984`, `bright-sparklers-1991`, `castleford-1992`, `toulouse-2001`, `neyshabur-rail-2004`, `t2-2007`, `mitsui-iwakuni-2012`, `himeji-2012`, `west-fertilizer-2013`, `tianjin-2015`, `xiangshui-2019`, `lg-polymers-2020`, `sitakunda-2022`

**Toolkit modules:** `reaction_hazard`, `thermal_runaway`

### Combustible dust

**Open with:** Where could dust collect, and what would the second explosion feed on?

**Cases:** `imperial-sugar-2008`, `kunshan-2014`

**Toolkit modules:** `dust_explosion`, `atex`

### Toxic releases

**Open with:** How far could it travel, and what would people downwind do?

**Cases:** `seveso-1976`, `bhopal-1984`, `schweizerhalle-1986`, `somerset-west-sulphur-1995`, `jilin-2005`, `gumi-hf-2012`, `lg-polymers-2020`

**Toolkit modules:** `dispersion`, `consequence`

### Vapour cloud explosions

**Open with:** What let the cloud grow, and what made it explode rather than burn?

**Cases:** `flixborough-1974`, `beek-1975`, `norco-1988`, `ufa-1989`, `pasadena-1989`, `hpcl-vizag-1997`, `skikda-lng-2004`, `sasol-secunda-2004`, `buncefield-2005`, `viareggio-2009`, `ioc-jaipur-2009`, `amuay-2012`, `kaohsiung-2014`

**Toolkit modules:** `explosion`, `dispersion`

### Fires and BLEVE

**Open with:** What was heating what, and how long did people have?

**Cases:** `feyzin-1966`, `los-alfaques-1978`, `ixhuatepec-1984`, `idemitsu-tomakomai-2003`, `toronto-sunrise-2008`, `cosmo-chiba-2011`, `tlahuelilpan-2019`, `plumpang-2023`

**Toolkit modules:** `fireball`, `pool_fire`, `fire_water`

### Ignition control

**Open with:** If we assume the release ignites, what would we design differently?

**Cases:** `abbeystead-1984`, `schweizerhalle-1986`, `jesse-pipeline-1998`, `idemitsu-tomakomai-2003`, `skikda-lng-2004`, `haradh-pipeline-2007`, `imperial-sugar-2008`, `tamahere-coolstore-2008`, `map-ta-phut-bst-2012`, `qingdao-pipeline-2013`, `kaohsiung-2014`, `kunshan-2014`, `accra-goil-2015`, `ahmedpur-east-2017`, `morogoro-tanker-2019`

**Toolkit modules:** `electrical`, `flammability`

### Storage, quantities and segregation

**Open with:** Why was that much of it in that place, next to that?

**Cases:** `oppau-1921`, `cleveland-lng-1944`, `texas-city-1947`, `feyzin-1966`, `schweizerhalle-1986`, `bright-sparklers-1991`, `dronka-fuel-depot-1994`, `somerset-west-sulphur-1995`, `enschede-2000`, `toulouse-2001`, `neyshabur-rail-2004`, `west-fertilizer-2013`, `accra-goil-2015`, `tianjin-2015`, `xiangshui-2019`, `beirut-port-2020`, `bata-barracks-2021`, `sitakunda-2022`

**Toolkit modules:** `mah`

### Hazardous materials in transport

**Open with:** Which controls stop applying once the material leaves the site?

**Cases:** `halifax-1917`, `texas-city-1947`, `los-alfaques-1978`, `neyshabur-rail-2004`, `toronto-sunrise-2008`, `viareggio-2009`, `gumi-hf-2012`, `lac-megantic-2013`, `ahmedpur-east-2017`, `morogoro-tanker-2019`

**Toolkit modules:** `consequence`

### Well control and offshore barriers

**Open with:** Which barriers were counted on, and how was each one shown to work?

**Cases:** `montara-2009`, `deepwater-horizon-2010`, `baghjan-2020`

**Toolkit modules:** `bowtie`

### Alarms, displays and human factors

**Open with:** What could the operator actually see and do in the time available?

**Cases:** `cubatao-1984`, `abbeystead-1984`, `grangemouth-1987`, `ufa-1989`, `milford-haven-1994`, `longford-1998`, `p36-2001`, `bombay-high-north-2005`, `jilin-2005`, `buncefield-2005`, `deepwater-horizon-2010`, `mitsui-iwakuni-2012`, `himeji-2012`, `lac-megantic-2013`, `kaohsiung-2014`, `mongstad-2017`

**Toolkit modules:** `sil`

### Leadership and safety culture

**Open with:** What warning was already available, and why did it not move anyone?

**Cases:** `flixborough-1974`, `piper-alpha-1988`, `bright-sparklers-1991`, `sasol-secunda-2004`, `varanus-island-2008`, `montara-2009`, `deepwater-horizon-2010`, `mitsui-iwakuni-2012`, `amuay-2012`, `lac-megantic-2013`, `kunshan-2014`, `xiangshui-2019`, `baghjan-2020`, `beirut-port-2020`

**Toolkit modules:** `psm`

### Emergency response and evacuation

**Open with:** What did responders and neighbours know about what they were facing?

**Cases:** `halifax-1917`, `texas-city-1947`, `feyzin-1966`, `beek-1975`, `seveso-1976`, `cubatao-1984`, `schweizerhalle-1986`, `piper-alpha-1988`, `guadalajara-1992`, `hpcl-vizag-1997`, `jesse-pipeline-1998`, `enschede-2000`, `mina-al-ahmadi-2000`, `p36-2001`, `neyshabur-rail-2004`, `ghislenghien-2004`, `bombay-high-north-2005`, `jilin-2005`, `imperial-sugar-2008`, `tamahere-coolstore-2008`, `toronto-sunrise-2008`, `map-ta-phut-bst-2012`, `amuay-2012`, `gumi-hf-2012`, `himeji-2012`, `west-fertilizer-2013`, `qingdao-pipeline-2013`, `tianjin-2015`, `ludwigshafen-2016`, `ahmedpur-east-2017`, `tlahuelilpan-2019`, `morogoro-tanker-2019`, `baghjan-2020`, `beirut-port-2020`, `bata-barracks-2021`, `sitakunda-2022`, `plumpang-2023`

**Toolkit modules:** `egress`, `fire_water`

### Natural hazards and loss of utilities

**Open with:** What happens to the safeguards when power, water or access is lost?

**Cases:** `dronka-fuel-depot-1994`, `somerset-west-sulphur-1995`, `idemitsu-tomakomai-2003`, `cosmo-chiba-2011`, `accra-goil-2015`

**Toolkit modules:** `reliability`

## Case sheets

### Halifax Explosion

`halifax-1917` · 1917-12-06 · Halifax harbour (the Narrows), Nova Scotia, Canada · ports and warehousing · fire, explosion · picric acid, TNT, gun cotton and benzol cargo

**Deaths:** 1946 (see note). Counts differ: Canadian Encyclopedia says nearly 2,000 died, gives 1,631 dead or missing in 1918 morgue records and a revised figure of 1,946 by 2004 (used here). Maritime Museum of the Atlantic says more than 1,700. A Northern Mariner article says two thousand, and quotes a 1962 newspaper figure of at least 1,600. No official final figure was read.

**What happened.** The inbound French munitions ship Mont-Blanc and the outbound Norwegian Imo collided in the harbour Narrows. Fire broke out aboard Mont-Blanc, which drifted to the Halifax shore and exploded about 20 minutes later, devastating the Richmond district.

**Causes** (disputed):

- Collision after conflicting manoeuvres and signals in the Narrows; sparks started a fire
- Sources differ on what first ignited: benzol on deck (journal article) or dry picric acid below deck (encyclopedia)
- Fault: the 1918 inquiry blamed Mont-Blanc; a split Supreme Court of Canada decision and then the Privy Council (1920) found both ships at fault
- The journal author describes confused wartime control of harbour traffic and earlier warnings that officials did not act on, and argues that blame was focused on the pilot, which drew attention away from federal failings

**Key learnings:**

- Movements of explosive cargo through populated harbours need positive traffic control and clear right-of-way. *[compiler]*
- People who know a cargo is explosive need a fast way to warn the shore; spectators gathered to watch the fire. *[compiler]*
- The first official finding of fault may be overturned; read the appeals as well as the inquiry. *[compiler]*

**Discuss:**

1. What separation, routing and timing rules would you set for a munitions or ammonium nitrate ship passing a city?
2. How would you tell harbourside residents in minutes that a burning ship may explode?

**Topics:** Hazardous materials in transport, Emergency response and evacuation, Land-use planning and neighbours.

**Sources read:**

- [B] [The Persecution of Pilot Mackey (The Northern Mariner XX No. 2, 2010)](https://tnm.journals.yorku.ca/index.php/default/article/download/317/299), The Northern Mariner / Le marin du nord
- [C] [Halifax Explosion](https://thecanadianencyclopedia.ca/en/article/halifax-explosion), The Canadian Encyclopedia
- [C] [Halifax Explosion](https://maritimemuseum.novascotia.ca/what-see-do/halifax-explosion), Maritime Museum of the Atlantic

### Oppau fertiliser silo explosion

`oppau-1921` · 1921-09-21 · Oppau, Ludwigshafen, Germany · explosives and fertiliser · explosion · ammonium sulfate nitrate

**Deaths:** 507 (see note). A BASF author's review gives 507 killed and 1,917 injured and notes that figures differ by source. BASF's history page says over 500 dead and about 2,000 hurt.

**What happened.** Blasting, used routinely to loosen caked fertiliser in a silo holding about 4,500 t of ammonium sulfate nitrate, set off a detonation. About 20,000 earlier blasting operations had passed without notable incident. The works and surrounding town were devastated.

**Causes** (not established):

- Reichstag committee: causes could not be reliably determined (as quoted by BASF)
- Later review: a new spray-drying process changed physical properties and made the salt easier to detonate
- Later review: a fine fraction richer in ammonium nitrate probably built up unnoticed and was initiated by loosening charges; definite proof is not possible

**Key learnings:**

- Assess a process change before it is made, including its effect on the hazard properties of the material, and update the safety concept. *[source]*
- Where the hazard potential is extreme, no single deviation should be able to release it. *[source]*
- A long incident-free record under old conditions is not evidence of safety after the product or process changes. *[compiler]*

**Discuss:**

1. Which material properties would your change procedure require to be re-tested after a change of drying method?
2. What routine practice on your site is justified mainly by the number of times it has not gone wrong?

**Topics:** Management of change, Reactive and runaway hazards, Storage, quantities and segregation, Hazard identification.

**Sources read:**

- [B] [Oppau 1921: Old Facts Revisited (Hörcher, Chemical Engineering Transactions 48, 2016)](https://www.aidic.it/CET/16/48/125.pdf), AIDIC
- [C] [100th anniversary of the Oppau explosion](https://www.basf.com/global/en/who-we-are/history/Oppau1921.html), BASF

### East Ohio Gas LNG tank failure and fire

`cleveland-lng-1944` · 1944-10-20 · Cleveland, Ohio, United States of America · LPG/LNG · fire, explosion, structural failure · liquefied natural gas

**Deaths:** 130 (see note). Encyclopedia of Cleveland History says the toll reached 130. No official count was read.

**What happened.** A liquefied natural gas storage tank (No. 4) failed and its contents ignited. About 20 minutes later a sphere also failed. Liquid and vapour flowed along streets into sewers, where vapour exploded, and fire swept homes and businesses near the plant.

**Causes** (not established):

- Bureau of Mines (as summarised in an NFPA staff presentation): a definitive cause could not be determined
- Contributing factors listed: wooden support of the inner tank, steel prone to brittle failure, and a flaw in tank or welding
- Spilled LNG entered sewers and vapour mixed with air
- No evidence found of operating error or sabotage

**Key learnings:**

- Separate LNG facilities widely from inhabited areas and take great care to keep spills out of storm sewers. *[source]*
- Provide dikes, and establish low-temperature properties of metals before using them for cryogenic storage. *[source]*
- A crack at first cool-down should prompt a documented re-examination of whether the material and design are suitable, in addition to repair and changes to cool-down practice. *[compiler]*

**Discuss:**

1. How do you size and locate impoundment so a total tank failure cannot reach drains or neighbours?
2. What material tests and acceptance evidence would you demand for a cryogenic containment steel today?

**How far the sources go.** The official source read (GAO) supports only the Bureau of Mines recommendations. Cause findings come from an NFPA staff presentation summarising the Bureau report, which was not read; the death toll is from an encyclopedia.

**Topics:** Facility siting and occupied buildings, Mechanical integrity and corrosion, Land-use planning and neighbours, Storage, quantities and segregation.

**Sources read:**

- [B] [LNG in the U.S.: pre-1940 and early experience (presentation by T. Lemoff, NFPA, citing the Bureau of Mines report)](https://share.ansi.org/shared%20documents/Standards%20Activities/International%20Standardization/Regional/Staff/LMM/SCCP%20Materials/SCCPWorkshop_Lemoff1_20100215.pdf), NFPA staff presentation, hosted by ANSI
- [A] [Liquefied Natural Gas (report highlights, 1978)](https://www.gao.gov/products/105075), U.S. Government Accountability Office
- [C] [East Ohio Gas Co. Explosion and Fire](https://case.edu/ech/articles/e/east-ohio-gas-co-explosion-and-fire), Encyclopedia of Cleveland History, Case Western Reserve University

### Texas City ammonium nitrate ship explosions

`texas-city-1947` · 1947-04-16 · Texas City, Texas, United States of America · ports and warehousing · fire, explosion · ammonium nitrate

**Deaths:** not stated (see note). The report as of 29 April 1947 records 433 bodies recovered and about 135 missing. It is an interim count, so no single integer is given.

**What happened.** Fire was found in bagged fertiliser-grade ammonium nitrate in a hold of the Grandcamp at the dock. Someone ordered no water, to protect the cargo, though hose lines were later in use. The ship exploded about an hour after discovery; a second ammonium nitrate ship, High Flyer, exploded the next night. Docks and a nearby chemical plant were destroyed.

**Causes** (not established):

- The report says the fire's time of origin and cause will probably never be known
- It judges that plentiful water early on would probably have extinguished it; steam use was reported but unconfirmed
- Hazards of ammonium nitrate were little known to handlers; bags carried no hazard warning
- Ammonium nitrate packed in combustible bags let the fire spread very rapidly once established

**Key learnings:**

- Label containers clearly as hazardous and instruct everyone who handles the material. *[source]*
- Fight ammonium nitrate fires with large quantities of water and respiratory protection; do not rely on steam. *[source]*
- Ports should tell the fire chief in advance about hazardous cargo and hold a worst-case disaster plan. *[source]*
- Prohibit smoking and open lights, and segregate ammonium nitrate from combustibles. *[source]*

**Discuss:**

1. Who in a modern port must know where ammonium nitrate is, and how quickly can they find out?
2. How would you write a stop-or-fight decision for a fire involving an oxidiser cargo near a city?

**How far the sources go.** The main account is a transcription hosted by a firefighters' union local; its official status was not confirmed.

**Topics:** Storage, quantities and segregation, Reactive and runaway hazards, Emergency response and evacuation, Hazardous materials in transport.

**Sources read:**

- [B] [Texas City, Texas, Disaster, April 16, 17, 1947 (transcription of the report)](https://local1259iaff.org/report.htm), Fire Prevention and Engineering Bureau of Texas and National Board of Fire Underwriters; transcription hosted by IAFF Local 1259

### Feyzin refinery propane sphere BLEVE

`feyzin-1966` · 1966-01-04 · Feyzin, France · LPG/LNG · fire, BLEVE · propane

**Deaths:** 18 (see note). HSE and IChemE LPB 251 both give 18 dead; injured is 81 (HSE) or 84 (LPB 251).

**What happened.** While water was being drained from the bottom of a propane sphere, a blockage cleared and propane escaped through valves that could no longer be closed. The cloud ignited, probably at a car about 160 m away. Fire engulfed the sphere, which ruptured while crews cooled neighbouring vessels, and further vessel failures followed.

**Causes** (secondary account):

- Drain valves opened in an order contrary to a recently issued procedure; a probable ice or hydrate plug then cleared and the valves froze open
- Poorly designed manual drain with difficult valve access and discharge directly beneath the valves
- Escaping liquid accumulated under the sphere instead of draining away
- Fire-fighting approach left the engulfed sphere without cooling

**Key learnings:**

- Avoid direct draining of LPG vessels; use a closed system or an isolatable de-watering pot, with a remotely operated isolation valve on the drain. *[source]*
- Protect spheres with deluge water, fire-resistant insulation or mounding and protected legs, and slope the ground so spills run away from the vessels. *[source]*
- Train responders for fire-engulfed vessels: cool the affected tank and nearby installations while keeping people and vehicles as far away as possible. Time to BLEVE is hard to judge, and the bulletin notes that the cautious philosophy is to evacuate and shelter rather than try to extinguish. *[source]*

**Discuss:**

1. Which of your drain or sample points could release pressurised liquid that one operator cannot stop, and how would you redesign it?
2. What information would an incident commander need to decide between cooling a vessel and withdrawing?

**Aftermath.** HSE states that design measures such as insulation or permanent water sprays on spheres and leg reinforcement were taken into codes of practice after the incident.

**Topics:** Fires and BLEVE, Isolation, permits and handover, Emergency response and evacuation, Storage, quantities and segregation.

**Sources read:**

- [B] [Refinery fire at Feyzin, 4th January 1966](https://www.hse.gov.uk/comah/sragtech/casefeyzin66.htm), HSE (COMAH case study page)
- [B] [Loss Prevention Bulletin 251, Anniversaries (October 2016)](https://minerva.jrc.ec.europa.eu/en/shorturl/minerva/lpb251anniversaries_special_issuepdf), IChemE (copy served by EC JRC Minerva)

### Flixborough (Nypro UK) vapour cloud explosion

`flixborough-1974` · 1974-06-01 · Flixborough, North Lincolnshire, United Kingdom of Great Britain and Northern Ireland · chemicals · vapour cloud explosion, fire · cyclohexane

**Deaths:** 28.

**What happened.** A reactor with a leaking crack was removed and a temporary bypass fitted between its neighbours so production could continue. On a Saturday afternoon the 20-inch bypass ruptured, releasing a large quantity of cyclohexane that formed a cloud and exploded. Eighteen of the dead were in the control room.

**Causes** (disputed):

- Failure of the temporary bypass, installed without drawings, adequate calculations or pressure testing (HSE; IChemE paper on the Court of Inquiry)
- Plant modification made without a full assessment of consequences
- HSE allows that a fire on an adjacent 8-inch line might have brought about the bypass failure; an IChemE paper reports that the Inquiry considered this alternative highly improbable and dismissed it

**Key learnings:**

- Design, build, test and maintain modifications to the same standard as the original plant. *[source]*
- Position and design control rooms and other occupied buildings for the possibility of a sudden major event. *[source]*
- A temporary repair needed to keep production going deserves at least as much independent engineering review as a permanent one. *[compiler]*

**Discuss:**

1. Who on your site has the competence and authority to reject a temporary piping modification?
2. Which occupied buildings would you move or strengthen if a large flammable release occurred today?

**Topics:** Management of change, Facility siting and occupied buildings, Vapour cloud explosions, Leadership and safety culture.

**Sources read:**

- [B] [Flixborough (Nypro UK) explosion, 1st June 1974](https://www.hse.gov.uk/comah/sragtech/caseflixboroug74.htm), HSE (COMAH case study page)
- [B] [Flixborough: lessons which are still relevant today (R. Turney, Loss Prevention Bulletin 237)](https://www.icheme.org/media/2229/lpb237_p21.pdf), IChemE

### DSM Beek naphtha cracker explosion

`beek-1975` · 1975-11-07 · Beek, Netherlands (Kingdom of the) · chemicals · vapour cloud explosion, fire · C2-rich light hydrocarbons

**Deaths:** 14.

**What happened.** During start-up of a naphtha cracker, vapour escaped from the depropaniser section and ignited, causing a large vapour cloud explosion and numerous fires. HSE records 14 dead and 107 injured, three of them off site. The alarm was not sounded before the explosion.

**Causes** (secondary account):

- Evidence suggested low-temperature embrittlement at the depropaniser feed drum; instrument records were destroyed
- A de-ethaniser upset sent much colder, C2-rich liquid to a drum that normally ran warm
- Initial fracture thought to be on a small pipe to the relief valve; it occurred at a weld which, with ageing, may fail at a higher temperature than the drum material limit

**Key learnings:**

- Set minimum design temperature from upset and start-up cases, including flashing, and apply it to welds and small-bore connections as well as shells. *[compiler]*
- Raising the alarm should not depend on a verbal instruction left for others to act on; anyone who learns of a release should sound it directly. *[compiler]*

**Discuss:**

1. Which upstream upsets could chill equipment on your unit below its minimum design metal temperature?
2. How would you test that any person who sees a release can raise the site alarm without delay?

**Topics:** Mechanical integrity and corrosion, Start-up, shutdown and abnormal operation, Vapour cloud explosions, Emergency response and evacuation.

**Sources read:**

- [B] [Explosion and fire at DSM, Beek, 7th November 1975](https://www.hse.gov.uk/comah/sragtech/casebeek75.htm), HSE (COMAH case study page)

### Seveso (ICMESA) dioxin release

`seveso-1976` · 1976-07-10 · Meda / Seveso, near Milan, Italy · chemicals · runaway reaction, toxic release · 2,3,7,8-TCDD (dioxin) from trichlorophenol production

**Deaths:** 0 (see note). HSE states no human deaths were attributed to TCDD. Many people fell ill and thousands of animals died or were slaughtered.

**What happened.** A trichlorophenol batch was shut down at the end of a shift with most solvent still in the reactor, leaving it without stirring or cooling. Hours later the bursting disc ruptured and vented a cloud containing dioxin over neighbouring municipalities. Warnings to authorities and the public were badly delayed.

**Causes** (secondary account):

- Batch interrupted contrary to operating procedures and left unstirred and uncooled
- Studies showed weaker exotherms, besides the known main one, that could lead to runaway; LPB 251 says the way the reaction started in the unstirred reactor was not understood at the time
- No vessel to catch or destroy vented material, although the disc maker had recommended a second receiver
- Bursting disc set pressure and purpose are reported differently: HSE gives 3.5 bar, to guard the compressed-air transfer, and says a lower setting would have vented at a less hazardous temperature; LPB 251 gives 3.8 bar, intended to protect the initial reaction stage

**Key learnings:**

- Understand reaction thermodynamics, including side reactions and decompositions under plausible procedural deviations. *[source]*
- Route batch reactor relief to containment wherever possible. *[source]*
- Prepare and exercise emergency plans with external responders, and give authorities timely, usable hazard information. *[source]*

**Discuss:**

1. What happens on your batch reactor if the step is abandoned halfway at the end of a shift?
2. What relief discharge destination would you accept for a reaction that can form a highly toxic by-product?

**Aftermath.** IChemE LPB 251 says many of the lessons became requirements of the EU Seveso Directives.

**Topics:** Reactive and runaway hazards, Relief, venting and disposal, Toxic releases, Emergency response and evacuation.

**Sources read:**

- [B] [Icmesa chemical company, Seveso, 10th July 1976](https://www.hse.gov.uk/comah/sragtech/caseseveso76.htm), HSE (COMAH case study page)
- [B] [Loss Prevention Bulletin 251, Anniversaries (October 2016)](https://minerva.jrc.ec.europa.eu/en/shorturl/minerva/lpb251anniversaries_special_issuepdf), IChemE (copy served by EC JRC Minerva)

### Los Alfaques campsite propylene tanker disaster

`los-alfaques-1978` · 1978-07-11 · Alcanar / Sant Carles de la Rapita, Tarragona, Spain · transport · explosion, fire · propylene

**Deaths:** 215 (see note). HISTORY (grade C) gives 215 dead. ScienceDaily, summarising research on Spanish chemical accidents (grade C), gives 217. No official figure was read.

**What happened.** A road tanker carrying liquefied propylene came to grief beside a crowded holiday campsite on the Spanish Mediterranean coast and exploded in a very large fireball. More than 200 people died and many survivors had severe burns. According to HISTORY, the truck hit a wall, and some witnesses reported a fire before the crash.

**Causes** (not established):

- HISTORY: the truck crashed into a concrete wall for unknown reasons
- HISTORY: some witnesses reported a fire on the truck before the crash
- The sources read do not establish why the tank failed

**Key learnings:**

- ScienceDaily quotes a researcher saying the accident was a turning point for the safety of road transport of chemicals. *[source]*
- Routing of pressurised flammable cargoes should consider dense temporary populations such as campsites, not only permanent housing. *[compiler]*

**Discuss:**

1. Which temporary or seasonal populations lie along your dangerous-goods routes?
2. What tanker design and filling controls would you require before accepting a liquefied-gas load?

**Topics:** Hazardous materials in transport, Fires and BLEVE, Land-use planning and neighbours.

**Sources read:**

- [C] [Gas fire incinerates crowded campsite, killing hundreds](https://www.history.com/this-day-in-history/july-11/gas-fire-incinerates-crowded-campsite), HISTORY
- [C] [Study reviews Spain's most serious chemical accidents](https://www.sciencedaily.com/releases/2014/05/140520093438.htm), ScienceDaily (from Plataforma SINC)

### Vila Soco (Cubatao) gasoline pipeline fire

`cubatao-1984` · 1984-02-24 · Vila Soco, Cubatao, Sao Paulo, Brazil · pipeline · pipeline rupture, fire · gasoline

**Deaths:** 93 (see note). Strongly disputed. The official figure is 93. A truth commission of the Cubatao bar association believes the toll may exceed 500; the news report says the state prosecutor's office worked with scenarios of 508, 631 and more than 700, which include estimated missing children (86 bodies documented). The fire ran from the night of 24 into 25 February.

**What happened.** Gasoline leaked from a Petrobras pipeline running through mangrove beside a settlement built largely on stilts. The fuel spread under the homes and ignited around the night of 24 to 25 February, and fire swept the settlement.

**Causes** (disputed):

- News account: later investigations pointed to a communication failure between refinery and terminal, with a receiving valve shut during a transfer, probably overpressuring the line
- Poor maintenance of old pipelines also not ruled out; a commission member alleges operating error and lack of maintenance
- Ignition source unknown

**Key learnings:**

- Make both ends of a transfer confirm the valve line-up before pumping starts. *[compiler]*
- Keep pipeline rights-of-way clear of housing and reassess the line's risk when settlement encroaches. *[compiler]*
- Treat a public report of a fuel leak as an emergency requiring pumps to stop. *[compiler]*

**Discuss:**

1. What interlock or positive confirmation would stop a transfer into a closed terminal valve?
2. When informal housing already sits on a pipeline route, what can the operator do in the short and long term?

**Topics:** Pipeline integrity, Land-use planning and neighbours, Alarms, displays and human factors, Emergency response and evacuation.

**Sources read:**

- [C] [Tragedia da Vila Soco, em Cubatao, completa 40 anos](https://www.gazetasp.com.br/brasil/tragedia-da-vila-soco-em-cubatao-completa-40-anos/), Gazeta de S. Paulo
- [C] [Comissao quer levar caso do incendio da Vila Soco a Corte Interamericana](https://agenciabrasil.ebc.com.br/geral/noticia/2014-07/comissao-quer-levar-caso-do-incendio-da-vila-soco-corte-interamericana), Agencia Brasil

### Abbeystead valve house methane explosion

`abbeystead-1984` · 1984-05-23 · Abbeystead, Lancashire, United Kingdom of Great Britain and Northern Ireland · pipeline · explosion · methane

**Deaths:** 16.

**What happened.** Visitors were gathered in a valve house at the outfall of a water transfer scheme. Shortly after pumping began, methane that had collected during 17 days without pumping was displaced into the building and exploded. Sixteen people died and nobody in the valve house escaped injury. No ignition source was positively identified.

**Causes** (secondary account):

- Ignition of a methane-air mixture accumulated in the valve house
- Gas displaced from a void at the end of the tunnel after 17 days without pumping
- Methane hazard, including gas dissolved in inflowing water, not recognised in design or operation
- Operation departed from the designers' manual; procedures changed without proper consultation

**Key learnings:**

- HSE states that a discharge system open to atmosphere would have prevented the explosion. *[source]*
- Consult properly on the effect of operating-procedure changes and make sure operators understand special design features. *[source]*
- Screen utility and water assets for flammable gas hazards, not only plants that handle hydrocarbons on purpose. *[compiler]*

**Discuss:**

1. Where in a nominally non-hazardous system could gas collect during a long idle period?
2. How should designers communicate an operating step that is safety critical for a reason operators cannot see?

**Topics:** Hazard identification, Management of change, Ignition control, Alarms, displays and human factors.

**Sources read:**

- [B] [The Abbeystead explosion, 23rd May 1984](https://www.hse.gov.uk/comah/sragtech/caseabbeystead84.htm), HSE (COMAH case study page)

### San Juan Ixhuatepec LPG terminal disaster

`ixhuatepec-1984` · 1984-11-19 · San Juan Ixhuatepec, Mexico City area, Mexico · LPG/LNG · fire, BLEVE, vapour cloud explosion · LPG

**Deaths:** 542 (see note). IChemE summary gives 542 as the official toll and says unofficial estimates were higher (shanty town population unknown). The HSE case study says about 500.

**What happened.** An LPG transfer line ruptured at a state-owned storage terminal during filling. The escaping cloud drifted to a flare and ignited. About 15 minutes after the release began, the first of a series of BLEVEs occurred over roughly an hour and a half, destroying the terminal and hitting nearby housing.

**Causes** (secondary account):

- Loss of containment from an 8-inch LPG line; IChemE says overpressure or overfilling, exact cause unknown because evidence was destroyed
- No gas detection; emergency isolation operated late
- Close vessel spacing and bund walls that let LPG pool around vessels
- Firewater system disabled by the initial blast
- Housing had grown close to the terminal fence

**Key learnings:**

- Provide remotely operated emergency isolation valves on bulk LPG vessels, closing slowly enough to avoid pressure surge. *[source]*
- Enforce land-use rules that keep minimum separation between major hazard sites and homes. *[source]*
- Study escalation when setting layout, spacing and fire protection. *[source]*

**Discuss:**

1. How would you grade and drain the ground under pressurised LPG vessels so that a leak cannot feed fire under them?
2. What should operators do on an unexplained pressure drop in a filling line before the source is found?

**How far the sources go.** Based on summaries; an original investigation report was not read.

**Topics:** Fires and BLEVE, Facility siting and occupied buildings, Land-use planning and neighbours, Isolation, permits and handover.

**Sources read:**

- [B] [PEMEX LPG Terminal, Mexico City, Mexico. 19th November 1984](https://www.hse.gov.uk/comah/sragtech/casepemex84.htm), UK Health and Safety Executive
- [B] [Lessons Learned Database incident summary: Multiple LPG Storage Tank Ruptures](https://www.icheme.org/media/14831/san-juan-ixhuatepec-mexico-city-incident-summary-19-nov-84.pdf), IChemE

### Bhopal methyl isocyanate release

`bhopal-1984` · 1984-12-03 · Bhopal, Madhya Pradesh, India · chemicals · toxic release, runaway reaction · methyl isocyanate

**Deaths:** 3787 (see note). ARIA gives 3,787 (2,259 immediate) as official Madhya Pradesh figures, and 5,000-25,000 across other sources; it says the true number will never be known. A PTI report in Deccan Herald quotes a state official that compensation was paid for 5,295 deaths; an NGO there claims over 25,000.

**What happened.** During the night of 2-3 December, water entered a methyl isocyanate storage tank. A runaway reaction lifted the relief system. The scrubber was overwhelmed and the flare was out of service, so a dense toxic cloud drifted into settlements beside the plant. The public siren sounded after most of the release had occurred.

**Causes** (disputed):

- About 500 L of water entered a tank holding 42 t of MIC; how it got in (washing error, connection error or sabotage) is contested
- Refrigeration and nitrogen pressurisation of the tank were out of service
- Scrubber ineffective and undersized; flare dismantled for maintenance
- Defective instruments, disconnected high-temperature alarms and modifications made without risk analysis
- Cost cutting, reduced maintenance and poor emergency preparedness

**Key learnings:**

- Safety barriers, technical and organisational, have to be kept working, particularly when a site is under financial pressure. *[source]*
- Modifications, including taking barriers out of service, need risk analysis and compensating measures. *[source]*
- Reduce hazardous inventory at source, control development around the site and tell neighbours how to protect themselves. *[source]*

**Discuss:**

1. Which of the unavailable barriers would you have treated as a condition for continuing to store MIC, and who should have had authority to enforce that?
2. How would an inherently safer design review treat the storage of a highly toxic reaction intermediate?

**Topics:** Toxic releases, Reactive and runaway hazards, Management of change, Land-use planning and neighbours.

**Sources read:**

- [B] [ARIA No. 7022: Release of toxic gases in a pesticide plant, Bhopal](https://www.aria.developpement-durable.gouv.fr/wp-content/files_mf/FD7022Bhopal_Inde_08122014_GB_PA.pdf), French Ministry for Sustainable Development, BARPI
- [C] [Bhopal gas tragedy: no accurate data on deaths 30 years on, alleges NGO](https://www.deccanherald.com/amp/story/archives%2Fbhopal-gas-tragedy-no-accurate-2228541), Deccan Herald (PTI)

### Sandoz Schweizerhalle warehouse fire and Rhine pollution

`schweizerhalle-1986` · 1986-11-01 · Schweizerhalle, near Basel, Switzerland · ports and warehousing · fire, toxic release · agrochemicals including organophosphorus insecticides and mercury fungicides

**Deaths:** not stated (see note). The sources read give no fatality figure.

**What happened.** A fire shortly after midnight destroyed a Sandoz chemical warehouse. Foam attack was overwhelmed and very large volumes of water were applied. Site drainage could not hold it, and most contaminated run-off entered the Rhine, killing aquatic life far downstream. The international Rhine alarm was delayed by nearly a day.

**Causes** (secondary account):

- Zurich City Police Science Department investigation: probably operator error with a blowtorch while shrink-wrapping sacks of Prussian blue (as reported by LPB 251)
- Smouldering could go unseen for hours before rapid open fire
- Site drainage could not cope with firefighting water

**Key learnings:**

- Provide tertiary containment for firewater sized on realistic worst-case application rates. *[source]*
- Segregate hazardous substances into suitably sized compartments and make sure workers and fire services understand the bulk storage fire risk. *[source]*
- Plan fire strategy in advance by scenario, comparing options including controlled burn-down. *[source]*

**Discuss:**

1. For your largest warehouse, where would the firewater go after the first hour?
2. Under what pre-agreed conditions would you let a warehouse burn rather than extinguish it?

**Aftermath.** Eawag states the disaster led directly to Switzerland's Major Accidents Ordinance; LPB 251 says the EU Seveso Directive was amended in 1988 to strengthen storage requirements.

**Topics:** Storage, quantities and segregation, Emergency response and evacuation, Ignition control, Toxic releases.

**Sources read:**

- [B] [Loss Prevention Bulletin 251, Anniversaries (October 2016)](https://minerva.jrc.ec.europa.eu/en/shorturl/minerva/lpb251anniversaries_special_issuepdf), IChemE (copy served by EC JRC Minerva)
- [B] [Rhine running red, fish dead: 30th anniversary of the Sandoz blaze](https://www.eawag.ch/en/info/portal/news/news-detail/der-rhein-rot-die-fische-tot-30-jahre-nach-dem-sandoz-brand), Eawag
- [C] [Chemical disaster still burns in Swiss memory](https://www.swissinfo.ch/eng/sci-tech/schweizerhalle-fire_chemical-disaster-still-burns-in-swiss-memory/42559954), SWI swissinfo.ch

### BP Grangemouth hydrocracker explosion

`grangemouth-1987` · 1987-03-22 · Grangemouth, Scotland, United Kingdom of Great Britain and Northern Ireland · refining · explosion, fire · hydrogen and hydrocarbons

**Deaths:** 1 (see note). IChemE's incident summary gives one fatality (a contract crane driver) and no other injuries. The HSE case page read does not state a toll.

**What happened.** While a hydrocracker was held on standby during recommissioning, high-pressure gas broke through from the high-pressure separator into the low-pressure separator when liquid level was lost. The low-pressure vessel, whose relief was sized only for fire, ruptured violently. Fragments travelled over 1 km and fire followed.

**Causes** (official investigation):

- Gas breakthrough from the high-pressure to the low-pressure separator
- Low-low level trip disconnected or taken out of service years earlier, without management of change
- Low-pressure separator relief not sized for gas breakthrough
- Operators distrusted the main level reading and relied on a backup chart recorder, whose offset led them to believe the HP separator level was normal

**Key learnings:**

- Disconnect trips only after documented risk assessment and management of change confirm that alternative controls are adequate. *[source]*
- Review every high-pressure to low-pressure interface for adequate overpressure protection. *[source]*
- Relief sizing should state which scenarios were considered and rejected, so that a lost safeguard visibly reopens the case. *[compiler]*

**Discuss:**

1. For one HP/LP interface you know, what is the relief load on gas blow-by if the level trip fails?
2. How would your plant detect that a trip had been defeated for years?

**Topics:** Relief, venting and disposal, Management of change, Alarms, displays and human factors, Start-up, shutdown and abnormal operation.

**Sources read:**

- [B] [The hydrocracker explosion and fire at BP Oil, Grangemouth Refinery, 22nd March 1987](https://www.hse.gov.uk/comah/sragtech/casebpgrang87b.htm), HSE (COMAH case study page)
- [B] [Individual incident summary: low pressure separator catastrophic failure](https://www.icheme.org/media/15173/grangemouth-incident-summary-22-mar-87.pdf), IChemE Lessons Learned Database

### Shell Norco refinery catalytic cracker explosion

`norco-1988` · 1988-05-05 · Norco, Louisiana, United States of America · refining · vapour cloud explosion, fire · light hydrocarbons

**Deaths:** 7 (see note). Chemical Processing podcast says seven Shell workers were killed; a TapRooT blog says six employees. No official figure was read.

**What happened.** In the early hours a large release in the catalytic cracking unit ignited and exploded, killing workers, damaging homes in the surrounding community and leading to evacuation. The blast was reported to have been felt far beyond the refinery.

**Causes** (not established):

- Trade-press account: believed catastrophic failure of a corroded vapour line off a depropanizer overhead
- TapRooT blog: no definite cause was found
- No official investigation report was read

**Key learnings:**

- The podcast guest stresses corrosion management that understands process chemistry and targets inspection where damage is likely, such as elbows and welds. *[source]*
- The podcast guest stresses checking whether people still occupy old buildings near process units. *[source]*

**Discuss:**

1. How would you choose inspection locations on an overhead vapour line, and what local changes in process chemistry would move them?
2. Which occupied buildings at your site were never designed for blast, and who still works in them at night?

**Topics:** Mechanical integrity and corrosion, Vapour cloud explosions, Facility siting and occupied buildings.

**Sources read:**

- [C] [Podcast: Lessons Learned From 1988 Shell Plant Explosion](https://www.chemicalprocessing.com/safety-security/article/33004331/podcast-lessons-learned-from-1988-shell-plant-explosion), Chemical Processing
- [C] [Remembering An Accident: Norco, Louisiana Oil Refinery Explosion](https://taproot.com/remembering-an-accident-norco-louisiana-oil-refinery-explosion/), TapRooT blog

### Piper Alpha offshore platform disaster

`piper-alpha-1988` · 1988-07-06 · Piper Alpha platform, North Sea, United Kingdom of Great Britain and Northern Ireland · oil and gas upstream · explosion, fire, pipeline rupture · gas condensate, crude oil and natural gas

**Deaths:** 167 (see note). Cullen: 165 of the 226 persons on board plus two crew of a rescue craft, 167 in all.

**What happened.** A condensate leak in the gas compression module ignited. Oil fires followed and the control room and main power were lost. Fire then ruptured gas pipeline risers connected to other platforms, massively intensifying it. Smoke and flame prevented evacuation from the accommodation by helicopter or lifeboat.

**Causes** (official investigation):

- Night shift tried to restart a condensate pump unaware that its relief valve had been removed; the blank flange fitted was not leak-tight
- Failures of shift handover communication and the permit to work system
- Riser failures massively fed the fire. The fire-water system was disabled by damage or power loss; the diesel fire pumps had also been left on manual, so even if undamaged they would not have started without manual action
- Superficial management attitude to major hazard risk and weak emergency training

**Key learnings:**

- Require a formal safety assessment of major hazards, presented to the regulator as a safety case. *[source]*
- Provide a temporary safe refuge with defined endurance, with escape routes and embarkation assessed. *[source]*
- Prevent equipment still under maintenance from being returned to service, through an effective permit system and shift handover. *[source]*

**Discuss:**

1. How would a night-shift operator on your plant learn that a relief valve on a standby pump had been removed?
2. What hazards can reach your facility through pipelines connected to sites you do not control?

**Aftermath.** A key Cullen recommendation was put into effect in 1992 through the UK Offshore Installations (Safety Case) Regulations. The industry account says industry accepted all 106 recommendations.

**Topics:** Isolation, permits and handover, Leadership and safety culture, Emergency response and evacuation, Pipeline integrity.

**Sources read:**

- [A] [The Public Inquiry into the Piper Alpha Disaster, Volume 1 (Lord Cullen), chapters 1-2](https://www.hse.gov.uk/offshore/assets/docs/piper-alpha-public-inquiry-volume1.pdf), HM Government; copy published by HSE
- [B] [Piper Alpha: Lessons Learnt, 2008](https://jesip.org.uk/uploads/media/incident_reports_and_inquiries/Piper%20Alpha%20Explosion.pdf), Oil industry body document hosted by JESIP

### Ufa (Asha) NGL pipeline and passenger train disaster

`ufa-1989` · 1989-06-04 · Near Asha, Bashkir ASSR (then USSR), Russian Federation · pipeline · pipeline rupture, vapour cloud explosion, fire · natural gas liquids (reported as propane and butane)

**Deaths:** 575 (see note). Both sources read give 575; no official investigation report was read. They differ on prosecutions: Moscow Times says nine officials were charged; RailTarget says nine were charged and seven served sentences.

**What happened.** A liquids pipeline leaked about a kilometre from the Trans-Siberian railway and a flammable cloud collected along the track in the night. When two passenger trains passed through the area, the cloud exploded, destroying carriages. Operators had reportedly seen pressure fall and restored it without checking for a leak.

**Causes** (secondary account):

- Leak from a pipeline near the railway; RailTarget reports a 1.7 m crack of unexplained origin
- Pressure drop answered by restoring pressure instead of searching for a leak
- Gas accumulated near the track in the prevailing weather; reported smell not acted on
- Ignition disputed: Moscow Times says wheel sparks; RailTarget says the exact source is uncertain

**Key learnings:**

- An unexplained pressure drop on a hazardous liquid pipeline should trigger leak confirmation or shutdown before throughput is restored. *[compiler]*
- Where pipelines run near transport corridors, there needs to be a direct way to stop traffic when a leak is suspected or reported. *[compiler]*

**Discuss:**

1. What evidence should a controller require before restoring pressure after an unexplained drop?
2. How would a public report of gas smell reach both your pipeline control room and the railway?

**Topics:** Pipeline integrity, Vapour cloud explosions, Land-use planning and neighbours, Alarms, displays and human factors.

**Sources read:**

- [C] [On this day: Ufa train disaster](https://www.themoscowtimes.com/2019/06/04/on-this-day-ufa-train-disaster-a65865), The Moscow Times
- [C] [The Hidden Horror of the Trans-Siberian Railway: Russia's Deadliest Train Disaster](https://www.railtarget.eu/technologies-and-infrastructure/trans-siberian-railway-train-disaster-ufa-9901.html), RailTarget

### Phillips 66 Houston Chemical Complex explosion

`pasadena-1989` · 1989-10-23 · Pasadena, Texas, United States of America · chemicals · vapour cloud explosion, fire, explosion · flammable polyethylene reactor inventory

**Deaths:** 23.

**What happened.** Contractors were clearing a blocked settling leg on a polyethylene loop reactor. The isolating ball valve above the open leg was open, and nearly the whole reactor inventory escaped within seconds. The vapour cloud ignited and exploded, followed by further explosions and fires.

**Causes** (secondary account):

- Single ball valve opened because its actuator air hoses were connected, and cross-connected
- Practice relied on one valve instead of double block or blind flange required by company and industry practice
- Permit-to-work not enforced
- No fixed gas detection; control room and other occupied areas too close
- Firewater came from the process water system, which was badly damaged; the fire pumps' power cables were attacked by fire, and of three standby diesel pumps one was under maintenance and another ran out of fuel

**Key learnings:**

- Study worst-case scenarios and escalation when setting layout, spacing and emergency plans. *[source]*
- Do not remove safeguards on live plant for any reason other than maintenance and testing. *[source]*
- An actuator whose hoses can be swapped defeats the intended fail position; design connections so they cannot be reversed. *[compiler]*

**Discuss:**

1. What isolation standard would you require before breaking containment on a reactor inventory, and how would you verify it in the field?
2. How would you design firewater so one explosion cannot disable it?

**How far the sources go.** Based on summaries; the original investigation report was not read.

**Topics:** Isolation, permits and handover, Contractors and interfaces, Facility siting and occupied buildings, Vapour cloud explosions.

**Sources read:**

- [B] [Phillips 66, Pasadena, USA. 23rd October 1989](https://www.hse.gov.uk/comah/sragtech/casepasadena89.htm), UK Health and Safety Executive
- [B] [Lessons Learned Database incident summary: Reactor Inventory Release Via Settling Leg](https://www.icheme.org/media/14709/pasadena-incident-summary-23-oct-89.pdf), IChemE

### Bright Sparklers fireworks factory explosion

`bright-sparklers-1991` · 1991-05-07 · Sungai Buloh, Selangor, Malaysia · explosives and fertiliser · fire, explosion · pyrotechnic compositions

**Deaths:** 22 (see note). A 1993 DAP statement quoting the Royal Commission gives 22 dead and 103 injured; a 2020 New Straits Times feature gives 26 dead and 103 injured. The commission report itself was not read.

**What happened.** A factory chemist was testing a new product at a fireworks factory next to a village. Chemicals from the experiment spilled and started a fire that reached stored large firecrackers, causing a series of explosions that damaged nearby homes.

**Causes** (secondary account):

- Spill during product testing started a fire that spread to stored fireworks
- Royal Commission (as quoted): the company broke many laws in a dangerous operation
- Royal Commission, as quoted in a DAP statement: certain government departments did not properly perform statutory duties on the factory's siting, construction, maintenance and operation

**Key learnings:**

- The Royal Commission, as quoted, linked the long-undetected illegal operation to certain government departments not properly performing their statutory duties. *[source]*
- Where several agencies regulate one site, their enforcement should be coordinated. *[compiler]*
- Experimental work with energetic materials must be separated from stored product, and explosive sites need separation from housing. *[compiler]*

**Discuss:**

1. How would you set separation distances between testing, storage and housing at a pyrotechnics site?
2. When several agencies each regulate part of a site, how do gaps get found?

**Aftermath.** The New Straits Times reports that the fire service's hazardous materials unit was established after the disaster.

**Topics:** Storage, quantities and segregation, Land-use planning and neighbours, Reactive and runaway hazards, Leadership and safety culture.

**Sources read:**

- [C] [NST175: The Bright Sparklers tragedy](https://nst.com.my/amp/news/nation/2020/08/613814/nst175-bright-sparklers-tragedy), New Straits Times
- [C] [DAP statement on the Royal Commission of Inquiry findings (18 April 1993, archived)](https://bibliotheca.limkitsiang.com/?p=6929), Lim Kit Siang archive

### Guadalajara sewer explosions

`guadalajara-1992` · 1992-04-22 · Reforma District, Guadalajara, Jalisco, Mexico · pipeline · explosion · gasoline / hydrocarbons in sewers

**Deaths:** 210 (see note). Disputed. A 2022 journal article, citing earlier researchers, gives official figures of 210 dead and 2 missing, with unofficial estimates of 252 to 700 dead. Expansion (news) gives 206. Petitioners to the Inter-American Commission listed 224 fatalities which they said were based on official figures.

**What happened.** A series of explosions in the underground sewer system tore up kilometres of streets in a densely populated district. Residents had reported strong gasoline smells from drains in the preceding days; officials and Pemex staff checked, but the area was not evacuated.

**Causes** (disputed):

- Fuel in the sewers; petitioners and many others attributed it to a leak from a Pemex polyduct
- The federal prosecutor's version: several factors, including the Salamanca-Guadalajara polyduct rupture, urban train works and an improperly mounted water pipe on the polyduct
- Defence experts held that the polyduct leak came after the explosions
- Criminal case against accused officials, including Pemex employees, dismissed without convictions; Expansion reports that the federal prosecutor's investigation cleared Pemex, which was never criminally charged

**Key learnings:**

- Fuel smells in drains were reported for days without an evacuation decision, and state and municipal authorities later blamed each other for no order being given; evacuation authority should be settled in advance. *[compiler]*
- Give one named role the authority and a gas-reading trigger to evacuate when flammable vapour is found in a public drain. *[compiler]*
- Check crossings and contacts between pipelines and other buried services during design and third-party construction. *[compiler]*

**Discuss:**

1. Who in your area can order an evacuation on high flammable-vapour readings in a sewer, and at what reading?
2. How would you detect a slow product-pipeline leak that migrates into municipal drains?

**How far the sources go.** The official source is an Inter-American Commission admissibility report that records the parties' positions; it is not a causal investigation. The toll is from a journal article.

**Topics:** Pipeline integrity, Emergency response and evacuation, Land-use planning and neighbours.

**Sources read:**

- [A] [Report No. 17/03, Petition 11.823, Maria Estela Acosta Hernandez et al. (Explosions in the Reforma District of Guadalajara), inadmissibility](https://cidh.oas.org/annualrep/2003eng/Mexico.11823.htm), Inter-American Commission on Human Rights
- [B] [El derecho a la verdad, justicia y reparacion: afectados de las explosiones del 22 de abril (Carta Economica Regional 130, 2022)](https://scielo.org.mx/pdf/cer/v35n130/0187-7674-cer-35-130-59.pdf), Universidad de Guadalajara journal, via SciELO
- [C] [Las dudas por las explosiones de Guadalajara siguen 20 anos despues](https://expansion.mx/nacional/2012/04/22/las-dudas-por-las-explosiones-de-guadalajara-continuan-20-anos-despues), Expansion

### Hickson & Welch jet fire

`castleford-1992` · 1992-09-21 · Castleford, West Yorkshire, United Kingdom of Great Britain and Northern Ireland · chemicals · runaway reaction, fire · nitrotoluene distillation residues

**Deaths:** 5.

**What happened.** A still base was opened for cleaning for the first time in about 30 years. The residue was warmed with steam and raked out by hand. It decomposed and ignited, sending a jet fire through the manway into a nearby control building and on to the office block. Five people died.

**Causes** (official investigation):

- Residue and vessel atmosphere not analysed; sludge wrongly assumed thermally stable
- Temperature probe sat above the sludge and a faulty steam regulator supplied hotter steam than intended
- No permit for the raking task and inlet not isolated; metal rake used
- Occupied buildings close to the plant; weak management of organisational change

**Key learnings:**

- Assess organisational change carefully, including workload and training. *[source]*
- Consider siting and structure of control rooms and occupied buildings near process plant, with doors opening outwards. *[source]*
- Practise muster and roll-call procedures routinely. *[source]*
- First-time cleaning of long-accumulated residue should be treated as a new process needing sampling and reactivity review. *[compiler]*

**Discuss:**

1. What would your permit system require before heating an unknown residue?
2. Does your temperature instrument measure the material that can run away, at all inventory levels?

**Topics:** Reactive and runaway hazards, Isolation, permits and handover, Facility siting and occupied buildings, Management of change.

**Sources read:**

- [B] [The fire at Hickson & Welch Limited, Castleford, 21st September 1992](https://www.hse.gov.uk/comah/sragtech/casehickwel92.htm), HSE (COMAH case study page)
- [B] [Individual incident summary: nitration plant residue exothermic runaway](https://www.icheme.org/media/14092/castleford-incident-summary-21-sep-92.pdf), IChemE Lessons Learned Database

### Texaco refinery (Pembroke Cracking Company) explosion

`milford-haven-1994` · 1994-07-24 · Milford Haven, Wales, United Kingdom of Great Britain and Northern Ireland · refining · explosion, fire · flammable hydrocarbons

**Deaths:** 0 (see note). IChemE summary: no fatalities, 26 injured.

**What happened.** An electrical storm and a lightning-started crude unit fire upset the refinery. About five hours later, liquid pumped into a vessel whose outlet was shut overflowed through the relief system to the flare. The FCC flare knock-out drum outlet line failed, releasing about 20 t of hydrocarbons that exploded.

**Causes** (official investigation):

- Level control valve shut while the control system showed it open
- Rupture of a corroded flare knock-out drum outlet elbow under liquid carry-over
- Earlier modification had reduced the drum's liquid pump-out capability without adequate assessment
- Alarm flood and poor control displays; unit kept running when it should have been shut down

**Key learnings:**

- Prioritise safety-critical alarms, document responses and limit total alarm numbers to what an operator can handle. *[source]*
- Give control displays process overviews, including mass and heat balance information. *[source]*
- Subject all modifications, including emergency ones, to formal hazard analysis. *[source]*
- Provide flare knock-out drums with critical high-level alarms and enough liquid removal capacity to prevent carry-over. *[source]*

**Discuss:**

1. How would your operators detect a mass-balance error when a valve position indication is false?
2. What conditions should force shutdown of a unit during a site-wide upset?

**Topics:** Alarms, displays and human factors, Relief, venting and disposal, Mechanical integrity and corrosion, Management of change.

**Sources read:**

- [B] [The explosion and fires at the Texaco Refinery, Milford Haven, 24th July 1994](https://www.hse.gov.uk/comah/sragtech/casetexaco94.htm), HSE (COMAH case study page)
- [B] [Individual incident summary: flare knockout drum outlet line rupture](https://www.icheme.org/media/14216/milford-haven-incident-summary-24-jul-94.pdf), IChemE Lessons Learned Database

### Dronka (Durunka) fuel depot fire and flood

`dronka-fuel-depot-1994` · 1994-11-02 · Dronka, Asyut Governorate, Egypt · storage and terminals · fire · stored fuel (reported as diesel and aircraft fuel)

**Deaths:** 469 (see note). WMO panel accepts 469. A New York Times report two days after the event (in Roanoke Times) said officials gave at least 400, with about 200 more thought buried.

**What happened.** During severe storms and flooding, fuel from a military reserve depot beside the village caught fire, and burning fuel was carried through the flooded streets.

**Causes** (disputed):

- WMO panel describes a lightning-caused oil tank fire
- A contemporary news report instead says heavy rain and wind apparently overturned fuel tank cars
- Burning fuel carried by floodwater into the village; depot reported less than 100 yards from the nearest home

**Key learnings:**

- Bulk fuel storage uphill of or beside housing needs siting review for flood paths, not only fire radiation distances. *[compiler]*
- Lightning protection, containment and flood resilience must be assessed together because one storm can defeat several barriers. *[compiler]*

**Discuss:**

1. How would you model where burning fuel goes if a tank farm's bunds are overtopped by floodwater?
2. What land-use and siting controls would keep a strategic fuel reserve and housing adequately separated, whichever came first?

**How far the sources go.** Only the abstract of the professional paper was read.

**Topics:** Natural hazards and loss of utilities, Land-use planning and neighbours, Facility siting and occupied buildings, Storage, quantities and segregation.

**Sources read:**

- [B] [WMO assessment of weather and climate mortality extremes: lightning, tropical cyclones, tornadoes, and hail (repository abstract page only)](https://repository.up.ac.za/handle/2263/61387), University of Pretoria repository (paper by a WMO panel)
- [C] [Egypt in shock, rage (New York Times report, 4 November 1994)](https://scholar.lib.vt.edu/VA-news/ROA-Times/issues/1994/rt9411/941104/11040109.htm), Roanoke Times archive (Virginia Tech)
- [C] [1994 Dronka floods and lightning strike](https://en.wikipedia.org/wiki/1994_Dronka_floods_and_lightning_strike), Wikipedia

### AECI Somerset West sulphur stockpile fire

`somerset-west-sulphur-1995` · 1995-12-16 · AECI site, Somerset West; smoke over Macassar, South Africa · chemicals · fire, toxic release · sulphur (sulphur dioxide)

**Deaths:** not stated (see note). Neither source read states a death toll, so none is recorded.

**What happened.** A fire ignited a long-standing sulphur stockpile at a chemical site, consuming about 7,250 tons. A sulphur dioxide cloud drifted over Macassar, many residents were evacuated overnight, and some developed persistent respiratory illness.

**Causes** (official investigation):

- Grass fires broke out near the stockpile on 13-15 December; a further fire on 16 December ignited it
- Judicial commission (as recorded by the High Court) held AECI negligent in failing to prevent the fire

**Key learnings:**

- A solid stock that looks inert can be a major toxic release source if it burns; include it in major hazard assessment. *[compiler]*
- Vegetation fires near stockpiles need firebreaks, watch arrangements and escalation after repeated nearby fires. *[compiler]*
- Off-site consequence planning must follow changes in neighbouring population. *[compiler]*

**Discuss:**

1. How would you estimate the sulphur dioxide source term and downwind effect of a burning sulphur stockpile?
2. What should three days of grass fires near a bulk combustible store have triggered?

**How far the sources go.** The official source is a 2012 court judgment that records the commission's finding; the commission report was not read.

**Topics:** Toxic releases, Storage, quantities and segregation, Natural hazards and loss of utilities, Land-use planning and neighbours.

**Sources read:**

- [A] [AECI Limited and Others v Dreyer, case A559/2011, judgment 13 August 2012](https://semantis.ai/resources/9441.pdf), Western Cape High Court (copy at semantis.ai)
- [B] [Factors Associated with Persistent Lower Respiratory Symptoms or Asthma among Residents Exposed to a Sulphur Stockpile Fire Incident (2019)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6388145), International Journal of Environmental Research and Public Health

### HPCL Visakhapatnam refinery LPG explosion and fire

`hpcl-vizag-1997` · 1997-09-14 · Visakhapatnam, Andhra Pradesh, India · refining · vapour cloud explosion, fire · LPG

**Deaths:** 56 (see note). The abstract of 'Analysis of an LPG explosion and fire' says 56 were declared dead but the number could have been up to three times higher. The abstract of a second Process Safety Progress paper, on the 'worst industrial accident of the 1990s', says over 60. Business Standard's first-day report said at least 22; Oil & Gas Journal said 56.

**What happened.** LPG leaked while a cargo from a pressurised ship was being received. The vapour cloud spread through the tank farm, administration area, utilities and at least one process unit before igniting. Explosion and fire destroyed storage vessels, administrative buildings, process units and an adjacent liquid terminal.

**Causes** (secondary account):

- Leak during receipt of LPG from a ship
- Wide spread of the vapour cloud before ignition; the specific release scenario could not be confirmed by witnesses because those doing the transfer died

**Key learnings:**

- Transfer operations need remote detection and isolation that do not depend on the people at the leak surviving. *[compiler]*
- Occupied buildings should be sited and designed assuming a drifting LPG cloud from import and storage areas. *[compiler]*

**Discuss:**

1. What instrumentation and records would let investigators reconstruct a release if no operator survived?
2. Where would you place occupied buildings relative to an LPG import line and sphere farm, and on what scenario?

**How far the sources go.** Both journal papers were read as abstracts only.

**Topics:** Facility siting and occupied buildings, Vapour cloud explosions, Emergency response and evacuation, Isolation, permits and handover.

**Sources read:**

- [B] [Analysis of an LPG explosion and fire (abstract only read)](https://doi.org/10.1002/prs.680220307), Process Safety Progress
- [B] [The world's worst industrial accident of the 1990s (abstract only read)](https://doi.org/10.1002/prs.680180304), Process Safety Progress
- [C] [Hindustan refinery to restart in 2 months](https://ogj.com/home/article/17242564/hindustan-refinery-to-restart-in-2-months), Oil & Gas Journal
- [C] [22 killed in HPCL refinery blast](https://www.business-standard.com/article/specials/22-killed-in-hpcl-refinery-blast-197091501015_1.html), Business Standard

### Esso Longford gas plant explosion

`longford-1998` · 1998-09-25 · Longford, Victoria, Australia · oil and gas upstream · explosion, fire · hydrocarbon gas, condensate and oil (lean oil absorption plant)

**Deaths:** 2.

**What happened.** Loss of lean oil flow let a reboiler heat exchanger in Gas Plant 1 chill far below its normal temperature. When warm oil was reintroduced the cold vessel suffered brittle fracture. Released hydrocarbons ignited; two employees died and Victoria's gas supply was cut.

**Causes** (official investigation):

- Lean oil pumps tripped and were not restarted for hours while cold fluids kept flowing through exchanger GP905
- Reintroducing warm lean oil into the embrittled exchanger caused brittle fracture
- Operators and supervisors did not know the hazard: inadequate training and no current procedures
- Planned HAZOP of Gas Plant 1 never took place

**Key learnings:**

- A planned retrospective HAZOP, had it been done, would have exposed the loss-of-lean-oil cold hazard and led to procedures and training. *[source]*
- An unreported earlier cold temperature incident was a lost chance to warn staff. *[source]*
- If the lean oil process is ever reinstated, protect equipment against low temperature with suitable steels or adequate warnings and shutdowns, and apply rigorous risk assessment. Separately, even without reinstatement, the Commission said emergency shutdown systems needed review to make sure the gas plants can be isolated from each other and from the CSP. *[source]*
- The Commission found that moving plant engineers off site was a permanent change that should have been risk assessed first and was not. It said the change may have contributed, but a direct causal link could not be established. *[source]*

**Discuss:**

1. Which deviations on a plant you know could take a vessel below its minimum design metal temperature, and how would an operator recognise it?
2. How would you assess the safety effect of moving plant engineering support off site?

**Aftermath.** The Royal Commission recommended that externally imposed, monitored obligations be placed on Esso through approval of a safety case or safety report.

**Topics:** Hazard identification, Management of change, Alarms, displays and human factors, Mechanical integrity and corrosion.

**Sources read:**

- [A] [The Esso Longford Gas Plant Accident: Report of the Longford Royal Commission, June 1999 (scanned; text by local OCR)](https://www.parliament.vic.gov.au/papers/govpub/VPARL1998-99No61.pdf), Government Printer, State of Victoria

### Jesse (Idjerhe) petroleum pipeline fire

`jesse-pipeline-1998` · 1998-10-17 · Atiegwo near Jesse, Delta State, Nigeria · pipeline · fire · petrol

**Deaths:** not stated (see note). No official toll read. An AFP timeline on Al Jazeera gives 1,082 and dates the event 18 October; Nnimmo Bassey's article dates it 17 October and says over a thousand; its footnote cites a title giving 1,098.

**What happened.** Petrol escaped from a 16-inch NNPC products pipeline; accounts quoted in the source say it spread over farmland and into a river, drawing local people to it. It ignited, killing many, and burned for about five days.

**Causes** (disputed):

- State company and military government alleged sabotage; the article says this was never substantiated
- A retired army chief alleged a siphoning operation and deliberate ignition (unverified allegation)
- Root cause described as still not established 22 years later

**Key learnings:**

- The author calls for replacing life-expired lines, regular integrity testing and transparent, immediate incident reporting and response. *[source]*
- A pipeline operator needs leak detection, fast shutdown and community warning in local languages whatever caused the breach. *[compiler]*
- Public blame before any investigation is no substitute for establishing the cause, and the author suggests that fear of prosecution led some families to take injured relatives out of hospital early, which may have added to the deaths. *[compiler]*

**Discuss:**

1. How quickly should a products pipeline operator detect and isolate a breach in a populated rural area, and how would you prove that capability?
2. What makes an incident investigation credible when the operator and government have an interest in the finding?

**Topics:** Pipeline integrity, Emergency response and evacuation, Ignition control.

**Sources read:**

- [C] [Jesse Pipeline Fire Tragedy: 22 Years of Silence (18 October 2020)](https://www.nnimmobassey.africa/posts/jesse-pipeline-fire-tragedy-22-years-of-silence), Nnimmo Bassey (advocacy author)
- [C] [Timeline of Nigeria pipeline disasters (AFP, 12 May 2006)](https://www.aljazeera.com/news/2006/5/12/timeline-of-nigeria-pipeline-disasters), Al Jazeera

### Enschede fireworks warehouse explosions

`enschede-2000` · 2000-05-13 · Roombeek district, Enschede, Netherlands (Kingdom of the) · explosives and fertiliser · fire, explosion · fireworks

**Deaths:** 22 (see note). The ARIA sheet gives 22 deaths, including 4 rescuers (fire-fighters in its narrative), and also mentions 3 disappearances without explaining them further. Other published counts were seen only in search results and were not read.

**What happened.** A fire broke out in a workshop at a fireworks warehouse in a residential district while nobody was reported on site. It spread to storage containers and boxes, which exploded in sequence, ending in a very large blast. The surrounding neighbourhood was devastated and firefighters were among the dead.

**Causes** (not established):

- Initial cause of the workshop fire never determined
- Stored quantities and hazard divisions did not match the authorisation, with most stock in a more severe hazard division than the one authorised
- No separation between containers, unauthorised containers and inadequate fire protection
- Weak inspection, enforcement and inter-agency communication (Oosting Commission, as summarised by ARIA)

**Key learnings:**

- The Oosting Commission, as summarised by ARIA, found that no lessons had been drawn from the 1991 Culemborg accident, including on classification accuracy. *[source]*
- Limited official inspection does not excuse an operator from regulatory duties. *[source]*
- Verify the declared explosive hazard division of imported goods before relying on it for layout, quantity limits or firefighting plans. *[compiler]*

**Discuss:**

1. How would responders on arrival know that the real hazard class was higher than licensed?
2. What separation and siting basis would you set for pyrotechnic storage near housing?

**Aftermath.** ARIA reports that work on a new Dutch regulatory framework for fireworks began in June 2000, and that single safety distances of 800 m for professional fireworks storage and 30 m for consumer fireworks were applied.

**Topics:** Storage, quantities and segregation, Land-use planning and neighbours, Emergency response and evacuation, Hazard identification.

**Sources read:**

- [B] [Explosion of a fireworks warehouse, May 13, 2000 (ARIA No. 17730)](https://www.aria.developpement-durable.gouv.fr/wp-content/files_mf/A17730_ips17730_003.pdf), French Ministry of Sustainable Development, BARPI

### Mina Al-Ahmadi refinery explosion

`mina-al-ahmadi-2000` · 2000-06-25 · Mina Al-Ahmadi refinery, Kuwait · refining · explosion, fire · natural gas condensate

**Deaths:** 5 (see note). The insurer summary and the 28 June 2000 Oil & Gas Journal report give 5 dead; the latter notes that earlier reports had said 4.

**What happened.** Staff were trying to isolate a leaking pipe that carried condensate to the refinery's gas plant from an NGL plant outside it when an explosion occurred. The ensuing fire burned for about nine hours; it wrecked two reformers and damaged three crude distillation units.

**Causes** (secondary account):

- Leak on a condensate line
- Initial investigation pointed to lack of inspection and maintenance of the line, which the refinery did not own
- Unclear ownership is thought to have delayed isolating the line

**Key learnings:**

- Every line crossing a battery limit needs an agreed owner for inspection, maintenance and emergency isolation. *[compiler]*
- People sent to isolate a live leak are exposed to ignition; remotely operable isolation at interfaces reduces that exposure. *[compiler]*

**Discuss:**

1. List the pipelines on a site you know that belong to another party. Who inspects them and who may shut them in?
2. Under what conditions should personnel withdraw instead of attempting manual isolation of a leak?

**Topics:** Mechanical integrity and corrosion, Pipeline integrity, Isolation, permits and handover, Emergency response and evacuation.

**Sources read:**

- [C] [The 100 Largest Losses 1972-2011, 22nd edition](https://www.joiff.com/members/sharedlearning/topics/archive2012/documents/100LargestLosses2012.pdf), Marsh (copy hosted by JOIFF)
- [C] [Update: Kuwaiti refinery repair may take 6 months (28 June 2000)](https://www.ogj.com/refining-processing/article/17253085/update-kuwaiti-refinery-repair-may-take-6-months), Oil & Gas Journal

### P-36 production platform explosions and sinking

`p36-2001` · 2001-03-15 · Roncador field, Campos Basin, Brazil · oil and gas upstream · explosion, structural failure · oil, gas and oily water

**Deaths:** 11.

**What happened.** An isolated-in-name drain tank inside a support column was pressurised by back-flow while the other drain tank was being emptied. It ruptured, broke a seawater pipe and released hydrocarbons. A second explosion killed emergency team members; the column flooded and the platform sank on 20 March.

**Causes** (secondary account):

- Operators lined up drain-tank water to the production header, against the operating manual
- Starboard tank intake not positively isolated while its vent was blinded and pump removed; the atmospheric tank pressurised and burst
- Tanks and seawater piping placed inside a stability-critical column
- Open watertight manholes, dampers that failed to close and fail-set sea valve aided flooding
- Alarm flood: 1,723 alarms in 17 minutes

**Key learnings:**

- Do not put process-connected tanks inside columns or pontoons where damage threatens stability. *[source]*
- Isolation procedures, permits and toolbox talks must cover every connection, including the inlet. *[source]*
- Run and update hazard studies, especially when converting a drilling unit to production. *[source]*
- Emergency teams need portable gas detectors, clear command instructions and drilled procedures. *[source]*

**Discuss:**

1. Draw the isolation you would require before removing the pump from an atmospheric drain tank. What protects it from back-flow?
2. How should a conversion project re-check area classification and common-cause failures?

**Aftermath.** The JRC note says the Brazilian regulator implemented reforms in how it managed offshore operations after the accident.

**How far the sources go.** Based on summaries; the original investigation report was not read.

**Topics:** Isolation, permits and handover, Hazard identification, Alarms, displays and human factors, Emergency response and evacuation.

**Sources read:**

- [B] [Learning Opportunity Notification LON-004: P-36 (summarises the ANP/DPC investigation report)](https://lmalloyds.com/wp-content/uploads/2025/06/LON-004-P36-Rev1-2.pdf), JRC Learning Opportunity Notification, hosted on lmalloyds.com
- [C] [Commission blames gas accumulation for P-36 platform blast](https://www.offshore-mag.com/home/article/16774270/commission-blames-gas-accumulation-for-p-36-platform-blast), Offshore magazine

### AZF fertiliser plant ammonium nitrate explosion

`toulouse-2001` · 2001-09-21 · Toulouse, France · explosives and fertiliser · explosion · off-specification ammonium nitrate

**Deaths:** 31 (see note). The ARIA sheet counts 31 people who died in the explosion or in the following days (our total): 21 on the AZF premises, 1 at the neighbouring SNPE works and 9 elsewhere.

**What happened.** Off-specification and rejected ammonium nitrate stored in a shed detonated on a weekday morning at a fertiliser works near the city. The blast killed people on and off site, injured thousands and caused severe damage far beyond the fence. Material had been added to the shed shortly before.

**Causes** (disputed):

- Many hypotheses examined; ARIA records no consensus among the parties
- Court-appointed experts (2006) attributed it to sodium dichloroisocyanurate (named dichlorocyanurate in the sheet) meeting ammonium nitrate shortly before the blast

**Key learnings:**

- Do not exclude severe scenarios from hazard studies and emergency plans only because experience suggests they are very unlikely. *[source]*
- Reduce hazard potential at source, and control urban development around existing hazardous sites. *[source]*
- Waste and off-specification streams need the same compatibility controls as product, or tighter ones. *[compiler]*

**Discuss:**

1. What incompatible materials could reach your off-spec or waste store, and by what route?
2. Which scenario has your hazard study screened out on historical grounds, and what if that judgement is wrong?

**Aftermath.** The ARIA sheet says the response included preparation of the French law of 30 July 2003 on major hazards. Legal status as of that sheet (updated July 2013; later proceedings not read): acquittal at first instance, conviction on appeal in 2012, and a further appeal then lodged.

**Topics:** Storage, quantities and segregation, Reactive and runaway hazards, Land-use planning and neighbours, Hazard identification.

**Sources read:**

- [B] [Explosion in the AZF fertilizer plant (ARIA No. 21329, updated July 2013)](https://www.aria.developpement-durable.gouv.fr/wp-content/files_mf/A21329_ips21329_008.pdf), French Ministry of Sustainable Development, BARPI

### Idemitsu Hokkaido refinery tank fires after the Tokachi-oki earthquake

`idemitsu-tomakomai-2003` · 2003-09-26 · Tomakomai, Hokkaido, Japan · storage and terminals · fire, structural failure · naphtha (full-surface fire); the product in the ring-fire tank is not stated in the sources read

**Deaths:** not stated (see note). The sources read do not state a death toll for the refinery fires.

**What happened.** Long-period ground motion caused large sloshing in floating-roof tanks. A ring fire broke out on one tank, and several floating roofs sank. About two days later the exposed naphtha in a tank with a sunken roof ignited despite foam application and burned as a full-surface fire for 44 hours.

**Causes** (secondary account):

- Large sloshing from 4-8 s ground motion in a deep sedimentary basin, above the code assumption
- Ring fire: sparks from roof collision with gauge pole and guide supports
- Naphtha fire: roof sank; inferred static sparks from isolated foam on the exposed liquid

**Key learnings:**

- Seismic design for tanks should use site- and period-specific long-period spectra and check sloshing, including higher modes. *[source]*
- Preventing floating roofs from sinking is important to prevent fire; check roof and pontoon strength. *[source]*
- Lower operating levels reduce the likelihood of fire and spill. *[source]*

**Discuss:**

1. How would you set maximum fill height for a floating-roof tank in a long-period seismic zone?
2. What are the ignition risks of foaming an exposed light-hydrocarbon surface, and how would you manage them?

**Aftermath.** Japan revised the Fire Service Law provisions on sloshing and floating-roof strength, in force from April 2005.

**How far the sources go.** The Hatayama paper was read as an abstract only.

**Topics:** Natural hazards and loss of utilities, Mechanical integrity and corrosion, Ignition control, Fires and BLEVE.

**Sources read:**

- [B] [Tank damage in the 2003 Tokachi-oki earthquake and revision of long-period design spectra (Zama, Hatayama et al.)](https://iitk.ac.in/nicee/wcee/article/14_S10-005.PDF), 14th World Conference on Earthquake Engineering
- [B] [Lessons from the 2003 Tokachi-oki earthquake for prediction of long-period motions and sloshing damage (abstract only read)](https://link.springer.com/article/10.1007/s10950-007-9066-y), Journal of Seismology
- [B] [Sloshing Damage to Oil Storage Tanks due to Long-Period Strong Ground Motions during the 2011 Tohoku, Japan Earthquake (K. Hatayama; includes comparison with 2003 and later countermeasures)](https://iisee.kenken.go.jp/symposium/10thIWSMRR/13.pdf), National Research Institute of Fire and Disaster, presentation hosted by BRI

### Skikda LNG plant explosion

`skikda-lng-2004` · 2004-01-19 · Skikda, Algeria · LPG/LNG · explosion, vapour cloud explosion, fire · LNG and mixed refrigerant hydrocarbons

**Deaths:** 27.

**What happened.** A steam boiler serving the Unit 40 refrigeration compressor exploded after drawing flammable vapour into its air intake. The breached firebox ignited vapour outside, and a much larger vapour cloud explosion destroyed three liquefaction trains and administration, maintenance and security buildings.

**Causes** (secondary account):

- Hydrocarbon leak into a semi-confined space between the control room, boiler and liquefaction section
- Both summaries indicate, as a preliminary or believed cause, that the boiler's combustion air intake drew in the flammable mixture
- Leak source: a cold box leak is judged probable by one summary; Sonatrach's preliminary view was that it might never be determined
- Cited root causes: poor layout and inadequate cold box inspection and maintenance

**Key learnings:**

- Study escalation to set plant layout and equipment spacing. *[source]*
- Enforce minimum separation between high-hazard plant and homes through land-use planning. *[source]*
- Fired equipment and air intakes near hydrocarbon inventory are ignition sources that need gas detection and a defined trip response. *[compiler]*

**Discuss:**

1. Which combustion air or ventilation intakes on your site could ingest a flammable cloud, and what happens automatically if they do?
2. How would you decide where to put the control room and occupied buildings relative to liquefaction trains?

**How far the sources go.** Only the executive summary of the US team report was read; it relays the operator's preliminary hypothesis.

**Topics:** Facility siting and occupied buildings, Vapour cloud explosions, Ignition control, Mechanical integrity and corrosion.

**Sources read:**

- [A] [SAND2004-6258, Appendix E: Report of the U.S. Government Team Site Inspection of the Sonatrach Skikda LNG Plant, 12-16 March 2004 (executive summary)](https://www.nrc.gov/docs/ML0933/ML093350855.pdf), Sandia National Laboratories / US DOE (NRC document copy)
- [B] [Skikda Incident Summary: LNG Production Plant Partially Destroyed](https://toolbox.energyinst.org/__data/assets/pdf_file/0014/14126/2004-01-19-Skikda-Incident-Summary.pdf), IChemE Safety & Loss Prevention SIG / Energy Institute Toolbox

### Neyshabur freight train explosion

`neyshabur-rail-2004` · 2004-02-18 · Khayyam station near Neyshabur, Iran (Islamic Republic of) · transport · fire, explosion · mixed cargo: sulphur, fertiliser (reported as including ammonium nitrate), petrol/oil, cotton

**Deaths:** not stated (see note). Figures differ and no official final toll was read. A 2018 journal article says more than 300; BBC (25 February 2004) cites local agencies at about 289 and describes the toll as nearly 300.

**What happened.** Fifty-one freight wagons rolled away from one station, derailed near Khayyam station and caught fire. Hours later, while firefighters, officials and onlookers were at the scene, the cargo exploded, damaging nearby villages.

**Causes** (secondary account):

- Runaway wagons; the transport minister attributed it probably to failings by railway personnel, with other possibilities still being examined
- Journal account: an ammonium nitrate wagon next to the fire decomposed after hours and the other wagons exploded
- Wagons lacked hazard placards, so firefighters did not know the contents

**Key learnings:**

- Hazardous cargo must be classified and placarded so responders know what is burning. *[source]*
- Keep the public and non-essential people out until the scene is confirmed safe. *[source]*
- Wagon securing and train marshalling are process safety controls when oxidisers and fuels travel together. *[compiler]*

**Discuss:**

1. What information must a first responder have within minutes of a mixed-cargo derailment, and how would you guarantee it?
2. How would you design defences against stationary wagons starting to roll and running away?

**Topics:** Hazardous materials in transport, Emergency response and evacuation, Storage, quantities and segregation, Reactive and runaway hazards.

**Sources read:**

- [B] [Pattern and nature of Neyshabur train explosion blast injuries (World J Emerg Surg 13:3, 2018)](https://link.springer.com/article/10.1186/s13017-018-0164-7), BMC / Springer Nature
- [C] ['Error' caused Iran train blast (25 February 2004)](http://news.bbc.co.uk/2/hi/middle_east/3487290.stm), BBC News

### Ghislenghien high-pressure gas pipeline rupture

`ghislenghien-2004` · 2004-07-30 · Ghislenghien, Ath, Belgium · pipeline · pipeline rupture, fire, explosion · natural gas

**Deaths:** 24 (see note). The ARIA sheet gives 24 dead and 132 injured. A UKOPA briefing gives 23 dead and about 140 seriously injured.

**What happened.** A leak on a buried 1 m gas transmission pipeline in an industrial zone drew firefighters, police and utility staff. The leak worsened and, about an hour after the first call, the line failed and the gas formed a fireball followed by a very tall flare. Responders and workers nearby were killed.

**Causes** (official investigation):

- Scrape marks left reduced wall at the failure location
- Tournai prosecutor, on an expert report, confirmed external damage during earlier earthworks
- UKOPA notes recent third-party road and car park construction over the line, with some details unsubstantiated by the operator

**Key learnings:**

- Safety studies should cover rupture scenarios, valve management strategy, land use around the route and third-party works controls. *[source]*
- For a large leak, set a wide cordon and isolate by line valves rather than working close to the leak. *[source]*
- Control third-party activity near pipelines and make sure damage gets reported. *[source]*

**Discuss:**

1. How far back should responders stand for a leak on a large high-pressure gas line, and who decides to isolate?
2. How would you find out that a contractor had gouged your pipeline weeks earlier?

**How far the sources go.** The French accident-database sheet was read from a copy on a third-party site, with a pipeline industry source.

**Topics:** Pipeline integrity, Emergency response and evacuation, Contractors and interfaces, Land-use planning and neighbours.

**Sources read:**

- [B] [Rupture et inflammation d'un gazoduc, 30 juillet 2004 (ARIA No. 27681, French)](https://lafibre.info/images/international/200909_aria_belgique_rupture_et_inflammation_gazoduc_le_30_juillet_2004.pdf), French environment ministry, BARPI; copy hosted by lafibre.info
- [B] [Fluxys pipeline incident 30th July 2004 (UKOPA/04/0093)](https://ukopa.co.uk/wp-content/uploads/2025/07/UKOPA-04-0093.pdf), UKOPA

### Sasol Secunda ethylene plant explosion

`sasol-secunda-2004` · 2004-09-01 · Sasol Polymers ethylene plant, Secunda, South Africa · chemicals · explosion, fire · flammable gas (ethylene plant)

**Deaths:** 10 (see note). Sasol's later filings give 10. A same-day news report gave 6.

**What happened.** An explosion and fire occurred at the Sasol Polymers ethylene plant while it was undergoing planned maintenance with several contractors present. Employees and contractors were killed and many injured.

**Causes** (not established):

- Company's same-day preliminary indication: a gas leak formed a cloud that ignited
- No investigation findings were read

**Key learnings:**

- Maintenance periods put many people next to live inventory; limit occupancy and verify positive isolation before breaking containment. *[compiler]*
- The company said the event showed that an improving safety record must not breed complacency. *[source]*

**Discuss:**

1. How would you control the number and location of contractors during a partial plant turnaround?
2. Why can an improving injury rate coexist with a high major-accident risk, and what indicators would show the difference?

**Aftermath.** Sasol reported appointing DuPont Safety Resources in November 2004 to review its South African safety systems and practices.

**Topics:** Contractors and interfaces, Isolation, permits and handover, Leadership and safety culture, Vapour cloud explosions.

**Sources read:**

- [C] [Annual Report on Form 20-F, year ended 30 June 2006](https://www.sec.gov/Archives/edgar/data/314590/000095012306013418/sasol_20f.pdf), Sasol (SEC filing, company document)
- [C] [Annual review, 30 June 2005](http://sasol.com/sites/default/files/2024-08/Annual%20review%2C%2030%20June%202005.pdf), Sasol (company document)
- [C] [Six dead, more than 100 injured in Sasol explosion (1 September 2004)](https://mg.co.za/news/south-africa/2004-09-01-six-dead-more-than-100-injured-in-sasol-explosion), Mail & Guardian

### BP Texas City refinery explosion

`texas-city-2005` · 2005-03-23 · Texas City, Texas, United States of America · refining · vapour cloud explosion, fire · flammable liquid hydrocarbons (raffinate)

**Deaths:** 15.

**What happened.** During restart of an isomerisation unit, a splitter tower was filled for over three hours with no liquid withdrawn. Relief valves discharged liquid to a blowdown drum with an open vent stack, which overflowed. The vapour cloud ignited, killing contractors in and around nearby trailers.

**Causes** (official investigation):

- Tower overfilled; misleading level indication, a failed redundant alarm and poor display; no automatic high-level protection
- Undersized atmospheric blowdown drum and stack instead of a flare
- Occupied temporary trailers sited close to the stack
- Fatigue, staffing, training, handover and procedure failures in startup
- Senior management weak on major-hazard safety culture; budget cuts

**Key learnings:**

- Site occupied trailers away from hazardous process areas. *[source]*
- Evaluate vessel overfilling in relief design and replace atmospheric blowdown with safer disposal such as flares. *[source]*
- Give distillation towers effective level instruments and automatic controls, and displays showing material balance. *[source]*
- Use leading and lagging process safety indicators, and address fatigue. *[source]*

**Discuss:**

1. Which independent layers would you require against tower overfill during startup?
2. Who should be allowed near a unit during startup, and how is that enforced?

**Topics:** Facility siting and occupied buildings, Relief, venting and disposal, Overfill and level control, Start-up, shutdown and abnormal operation. Also in the [CSB register](INCIDENTS.md) as `texas-city-2005`.

**Sources read:**

- [A] [BP America (Texas City) Refinery Explosion, investigation page](https://www.csb.gov/bp-america-texas-city-refinery-explosion/), U.S. Chemical Safety Board
- [A] [Investigation Report: Refinery Explosion and Fire, BP Texas City, Report 2005-04-I-TX (March 2007)](https://www.csb.gov/file.aspx?DocumentId=5596), U.S. Chemical Safety Board

### Mumbai (Bombay) High North platform fire

`bombay-high-north-2005` · 2005-07-27 · Mumbai High field, Arabian Sea, India · oil and gas upstream · fire, structural failure, pipeline rupture · natural gas and oil

**Deaths:** 22 (see note). 22 dead consists of 11 confirmed fatalities and 11 missing.

**What happened.** A multi-purpose support vessel with an injured crew member approached in monsoon swell, with thruster problems and under manual control. After the basket transfer, a swell pushed its helideck into the platform, severing at least one gas riser. The fire destroyed the platform within about two hours; the vessel also burned and later sank.

**Causes** (secondary account):

- Vessel struck gas export risers located outside the jacket
- Vulnerable riser layout, with guards unsuited to a vessel of that size
- No fire protection on risers; large riser inventories kept feeding the fire
- Medical transfer made in bad weather with thruster/DP problems and limited alternatives

**Key learnings:**

- Locate risers away from loading faces or protect them, and treat them as safety-critical with their own risk assessment. *[source]*
- Consider subsea isolation valves and riser fire protection where inventories are large. *[source]*
- Set marine operating procedures for bad weather and plan other medical evacuation routes. *[source]*

**Discuss:**

1. Who should be able to refuse a vessel approach during a medical emergency, and what information do they need?
2. When does riser inventory justify a subsea isolation valve?

**Aftermath.** The Lloyd's-hosted notification states that India afterwards set up a regulator for offshore oil and gas production.

**Topics:** Hazard identification, Emergency response and evacuation, Alarms, displays and human factors, Facility siting and occupied buildings.

**Sources read:**

- [B] [Learning Opportunity Notification LON-002: Mumbai High North](https://lmalloyds.com/wp-content/uploads/2025/06/LON-002-Mumbai-High-North-1.pdf), JRC Learning Opportunity Notification, hosted by Lloyd's Market Association
- [C] [The Samudra Suraksha at Bombay High North](https://shipsandoil.co.uk/the-sumadra-suraksha-at-bombay-high-norths), Ships & Oil

### Jilin petrochemical explosions and Songhua River pollution

`jilin-2005` · 2005-11-13 · Jilin City, Jilin, China · chemicals · explosion, fire · benzene, aniline, nitrobenzene

**Deaths:** 8 (see note). Xinhua's November 2006 account (via UPI and Dialogue Earth) gives 8 dead and 60 injured. A 2006 journal note citing early UNEP information gives 5 confirmed dead and nearly 70 injured.

**What happened.** An explosion in a nitrobenzene unit at the Jilin Petrochemical plant killed eight people and released about 100 tonnes of benzene compounds into the Songhua River. Downstream, Harbin shut off its water supply for several days. Public notification of the pollution was delayed, and the plume reached towards Russia.

**Causes** (secondary account):

- Operating rules not followed: the State Council finding as reported by Xinhua/UPI
- Mishandling of a steam valve (Dialogue Earth report of the findings)
- Early accounts attributed the blast to a blockage in a processing tower

**Key learnings:**

- Emergency plans for chemical plants should cover contaminated firewater and spills reaching rivers, with prompt notification downstream. *[compiler]*
- The UNEP mission and the later journal note supported continued monitoring of the river, including sediments and water use after the spring thaw. *[source]*

**Discuss:**

1. What containment would stop firewater and spilled aromatics from a unit fire reaching a river?
2. Who must be told, and how fast, when an on-site accident threatens a public water supply?

**Aftermath.** Xinhua accounts report that the State Council disciplined company executives and local environmental officials in November 2006.

**How far the sources go.** The professional sources predate the final findings; the toll and cause come from news reports of Xinhua.

**Topics:** Emergency response and evacuation, Alarms, displays and human factors, Toxic releases, Land-use planning and neighbours.

**Sources read:**

- [B] [The Songhua River Spill, China, December 2005: Field Mission Report](https://archive.eecentre.org/eecentre.org/wp-content/uploads/2019/06/China-december-2005-UNEP-Mission-Report.pdf), UNEP
- [B] [Dilemmas downstream from the Songhua River spill](https://link.springer.com/content/pdf/10.1007/BF03161020.pdf), Journal of Medical Toxicology
- [C] [Plant blast case brings citations](https://www.upi.com/Top_News/2006/11/24/Plant-blast-case-brings-citations/11391164389858/), UPI
- [C] [China punishes officials a year after toxic spill](https://dialogue.earth/en/uncategorized/580-china-punishes-officials-a-year-after-toxic-spill/), Dialogue Earth

### Buncefield oil depot overfill, explosion and fire

`buncefield-2005` · 2005-12-11 · Hemel Hempstead, Hertfordshire, United Kingdom of Great Britain and Northern Ireland · storage and terminals · vapour cloud explosion, fire · unleaded petrol

**Deaths:** 0 (see note). MIIB: 43 injured, none seriously, and no fatalities.

**What happened.** A petrol tank being filled by pipeline overflowed overnight after its level gauge stopped changing and automatic shutdown did not occur. Fuel cascading down the tank formed a large vapour cloud that spread off site. Explosions followed around 06:00, then a fire engulfing more than 20 large tanks.

**Causes** (official investigation):

- Tank 912 level reading stayed static from about 03:00 while filling continued
- The independent high-level protection that should have closed valves did not operate
- Overflowing petrol cascading from the tank top created a rich vapour cloud

**Key learnings:**

- Fit a high-integrity automatic overfill prevention system physically and electrically independent of the tank gauging system. *[source]*
- Set the integrity of overfill protection by systematic safety integrity level assessment following BS EN 61511 principles, with periodic testing. *[source]*
- A level that stays flat while a tank is receiving should itself raise an alarm. *[compiler]*

**Discuss:**

1. How would you prove that your independent high-level switch will work on the day it is needed?
2. Who can see, and who can stop, a transfer controlled from another organisation's control room?

**Aftermath.** In November 2008 the Government and Competent Authority published a response setting out progress by regulators and industry against the Board's design, operation and emergency recommendations.

**Topics:** Overfill and level control, Vapour cloud explosions, Alarms, displays and human factors, Land-use planning and neighbours.

**Sources read:**

- [A] [The Buncefield Incident 11 December 2005: final report of the Major Incident Investigation Board, Volume 2](https://www.icheme.org/media/13923/buncefield-miib-final-report-volume-2a.pdf), MIIB (copy hosted by IChemE)
- [A] [The Buncefield Investigation: the Government and Competent Authority's response (Cm 7491)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/238688/7491.pdf), UK Government

### Haradh-Uthmaniyah gas pipeline fire

`haradh-pipeline-2007` · 2007-11-18 · Haradh-Uthmaniyah gas pipeline, about 30 km from Hawiyah gas plant, Saudi Arabia · pipeline · explosion, fire · natural gas

**Deaths:** 40 (see note). Toll rose from 28 (19 November report) to 40 (Aramco statement reported 21 November).

**What happened.** Fire broke out shortly after midnight on a gas pipeline where maintenance work for new tie-ins was under way. Most of the dead worked for the contractor doing the work.

**Causes** (not established):

- Occurred during maintenance work for new tie-ins
- An unnamed industry source said workers were welding a plate on the pipeline
- Aramco set up a technical committee; its findings were not read

**Key learnings:**

- Tie-ins and hot work on or beside live gas lines need verified isolation or an engineered hot-tap procedure, with minimum people in the hazard area. *[compiler]*
- Contractor crews should be inside the same permit, gas testing and emergency escape arrangements as the operator. *[compiler]*

**Discuss:**

1. What evidence should be required before welding starts on a pipeline that is part of a live gas network?
2. How would you determine the number of people allowed near a live tie-in?

**Topics:** Isolation, permits and handover, Pipeline integrity, Contractors and interfaces, Ignition control.

**Sources read:**

- [C] [Explosion in Aramco Gas Pipeline Kills 28 (19 November 2007)](https://www.arabnews.com/node/305849), Arab News
- [C] [Final Toll in Pipeline Blast Put at 40 Dead, 9 Injured (21 November 2007)](https://www.arabnews.com/node/305890), Arab News

### T2 Laboratories runaway reaction

`t2-2007` · 2007-12-19 · Jacksonville, Florida, United States of America · chemicals · runaway reaction, explosion, fire · methylcyclopentadienyl manganese tricarbonyl (MCMT) batch

**Deaths:** 4.

**What happened.** During the first reaction step of an MCMT batch, the operator reported a cooling problem. Minutes later the reactor burst and its contents ignited. Employees were killed, people at neighbouring businesses were injured, and debris travelled up to a mile.

**Causes** (official investigation):

- Root cause: the company did not recognise the runaway hazard of the process
- Cooling system open to single-point failure (likely loss of cooling started the runaway)
- Reactor relief system could not relieve a runaway

**Key learnings:**

- CSB recommended adding reactive hazard awareness to undergraduate chemical engineering curricula. *[source]*
- Characterise heat of reaction and secondary decomposition before scale-up, and size cooling and relief from those data. *[compiler]*
- A long production record does not show that a process is safe. T2 was on its 175th batch, and CSB records unexpected exotherms in three of the first ten; investigate such excursions instead of relying on later successful batches. *[compiler]*

**Discuss:**

1. What calorimetry would you require before approving this kind of batch step at full scale?
2. With loss of cooling, how much time is there, and what independent action would use it?

**Topics:** Reactive and runaway hazards, Relief, venting and disposal, Hazard identification. Also in the [CSB register](INCIDENTS.md) as `t2-2007`.

**Sources read:**

- [A] [T2 Laboratories Inc. Reactive Chemical Explosion, investigation page](https://www.csb.gov/t2-laboratories-inc-reactive-chemical-explosion/), U.S. Chemical Safety Board
- [A] [Investigation Report: T2 Laboratories, Inc. Runaway Reaction (September 2009; text read is marked Board Voting Copy)](https://www.csb.gov/assets/1/20/T2_Final_Copy_9_17_09.pdf), U.S. Chemical Safety Board

### Imperial Sugar dust explosions

`imperial-sugar-2008` · 2008-02-07 · Port Wentworth, Georgia, United States of America · food and agriculture · dust explosion, fire · sugar and cornstarch dust

**Deaths:** 14.

**What happened.** A first sugar dust explosion occurred in a recently enclosed belt conveyor under storage silos. It lofted dust built up on floors and high surfaces, causing secondary explosions through the packing buildings and nearby areas. Blast damage blocked exit routes and fires destroyed buildings.

**Causes** (official investigation):

- Conveying equipment not designed or maintained to limit dust release
- Poor housekeeping let large dust deposits build up
- Newly enclosed conveyor allowed explosible concentration; overheated bearing was the most likely ignition source
- Inadequate emergency notification and no evacuation drills

**Key learnings:**

- Run a company-wide housekeeping programme to prevent hazardous dust build-up. *[source]*
- Design and operate to the combustible dust and electrical classification standards, and train workers and contractors. *[source]*
- Install an emergency alarm system and run evacuation drills. *[source]*
- Enclosing equipment changes the hazard and should go through management of change. *[compiler]*

**Discuss:**

1. What management-of-change questions should adding covers to a conveyor trigger?
2. How would you set and measure a dust accumulation limit that housekeeping can be audited against?

**Aftermath.** CSB's report notes that after the incident OSHA announced it intended to start rulemaking on a combustible dust standard.

**Topics:** Combustible dust, Management of change, Ignition control, Emergency response and evacuation. Also in the [CSB register](INCIDENTS.md) as `imperial-sugar-2008`.

**Sources read:**

- [A] [Imperial Sugar Company Dust Explosion and Fire, investigation page](https://www.csb.gov/imperial-sugar-company-dust-explosion-and-fire/), U.S. Chemical Safety Board
- [A] [Investigation Report on the Imperial Sugar Company dust explosion and fire (September 2009)](https://www.csb.gov/assets/1/20/Imperial_Sugar_Report_Final_updated.pdf), U.S. Chemical Safety Board

### Icepak coolstore explosion and fire, Tamahere

`tamahere-coolstore-2008` · 2008-04-05 · Tamahere, near Hamilton, New Zealand · food and agriculture · explosion, fire · propane-based refrigerant

**Deaths:** 1.

**What happened.** Firefighters attending a smoke detector alarm entered a coolstore plant room where they saw what appeared to be smoke, vapour or leaking refrigerant, apparently with no smell and no evident flammable-gas warning signs. A violent explosion followed, killing one firefighter, seriously injuring seven others and starting a large fire.

**Causes** (official investigation):

- Almost certainly a leak of flammable propane-based refrigerant ignited in the plant room, probably by electrical equipment
- Fire Service did not know of the flammable refrigerant; no apparent warning signage or odorant
- Plant room electrical equipment apparently not designed to be flame proof
- Report notes systemic regulatory and information-sharing defects

**Key learnings:**

- Require odorant in large flammable gas installations and bring stationary refrigeration systems under hazardous substance controls. *[source]*
- Share hazardous substance information between agencies and use pre-incident planning to identify high-risk buildings, including outside urban districts. *[source]*
- Introducing a flammable refrigerant, even one marketed as a substitute for a non-flammable one, needs hazardous area, ventilation, detection and electrical review. *[compiler]*

**Discuss:**

1. What should a management-of-change review cover when a site that has used non-flammable refrigerants introduces a hydrocarbon blend?
2. What information and instruments should responders have before entering a plant room on an automatic alarm?

**Topics:** Management of change, Emergency response and evacuation, Ignition control, Hazard identification.

**Sources read:**

- [A] [Inquiry into the Explosion and Fire at Icepak Coolstores, Tamahere, on 5 April 2008 (September 2008)](https://new-courses.justice.eku.edu/FSE/FSE120/Docs/TamahereNewZealand2008.pdf), New Zealand Fire Service Commission (copy hosted by Eastern Kentucky University)

### Varanus Island gas pipeline rupture and fire

`varanus-island-2008` · 2008-06-03 · Varanus Island, Western Australia, Australia · pipeline · pipeline rupture, explosion, fire · natural gas

**Deaths:** 0 (see note). The Senate committee report states there were no injuries or fatalities.

**What happened.** A high-pressure 12-inch sales gas line weakened by external corrosion ruptured on the beach. Neighbouring lines then failed and fires damaged the gas plant. Western Australia lost about 30 per cent of its gas supply for roughly two months.

**Causes** (official investigation):

- External corrosion at the beach crossing
- Ineffective anti-corrosion coating and cathodic protection there
- Ineffective inspection and monitoring by the operator
- Later inquiry: risk was foreseeable from the operator's own documents; regulatory arrangements were confused

**Key learnings:**

- Collate consultant, audit and safety case information; the inquiry found warnings were available to the operator but the risk was not addressed. *[source]*
- Regulatory competence and clear jurisdiction are essential to a safety case regime. *[source]*
- Parallel pipelines laid close together allow one rupture to escalate; spacing and isolation need explicit review. *[compiler]*

**Discuss:**

1. How would you inspect a short wet-dry shore crossing that is hard to survey or pig?
2. What should a regulator do when an operator cannot produce integrity data for a critical pipeline?

**Topics:** Pipeline integrity, Mechanical integrity and corrosion, Leadership and safety culture, Facility siting and occupied buildings.

**Sources read:**

- [A] [Offshore Petroleum Safety Regulation: Varanus Island Incident Investigation (Bills and Agostini), June 2009](https://www.parliament.wa.gov.au/publications/tabledpapers.nsf/displaypaper/3814556ca4a64e2517855edb48257a0900104edb/$file/varanus+inquiry.pdf), Government of Western Australia (tabled paper)
- [A] [Minister releases full report into Varanus Island gas pipeline explosion (10 October 2008)](https://www.wa.gov.au/government/media-statements/Barnett%20Liberal%20National%20Government/Minister-releases-full-report-into-Varanus-Island-gas-pipeline-explosion-20081010), Government of Western Australia
- [A] [Matters relating to the gas explosion at Varanus Island, Western Australia (December 2008)](https://www.aph.gov.au/~/media/wopapub/senate/committee/economics_ctte/completed_inquiries/2008_10/wa_gas_08/report/report_pdf.ashx), Senate Standing Committee on Economics

### Sunrise Propane explosions

`toronto-sunrise-2008` · 2008-08-10 · 54 Murray Road, Toronto, Ontario, Canada · LPG/LNG · explosion, fire · propane

**Deaths:** 2 (see note). The Fire Marshal release says two people died; it identifies a Sunrise employee found at the scene and a Toronto Fire district chief who died of a heart attack at the scene.

**What happened.** A series of explosions occurred at a propane facility in a Toronto neighbourhood. Thousands of people were temporarily evacuated. The Ontario Fire Marshal traced the start to a propane leak during a transfer directly between two cargo trucks.

**Causes** (official investigation):

- Propane leak from a hose failure during a tank-to-tank (truck to truck) transfer
- Ignition source not determined

**Key learnings:**

- Treat transfer hoses and direct truck-to-truck transfers as loss-of-containment points that need a defined design basis, inspection and procedure. *[compiler]*
- Siting of LPG facilities near homes should be judged on credible transfer-leak scenarios. *[compiler]*

**Discuss:**

1. What engineering and audit controls would you apply to a direct transfer between two cargo trucks?
2. What would you require for siting a propane filling facility near housing?

**Aftermath.** The Fire Marshal said its recommendations would go to a Propane Advisory Team of government, agency, propane industry and fire service members, formed to identify regulatory issues and resolve industry and fire department challenges arising from fire service requirements in O. Reg. 440/08.

**How far the sources go.** The official source is the Fire Marshal's news release, not the full report.

**Topics:** Fires and BLEVE, Facility siting and occupied buildings, Hazardous materials in transport, Emergency response and evacuation.

**Sources read:**

- [A] [Office of the Fire Marshal concludes investigation at Sunrise Propane (4 August 2010)](https://www.newswire.ca/news-releases/office-of-the-fire-marshal-concludes-investigation-at-sunrise-propane-544884292.html), Ontario Office of the Fire Marshal, via CNW/Newswire

### Viareggio LPG freight train derailment

`viareggio-2009` · 2009-06-29 · Viareggio, Tuscany, Italy · transport · explosion, fire · LPG

**Deaths:** 32 (see note). 32 fatalities from a 2014 peer-reviewed paper, which says the total includes two heart attack deaths and deaths up to six months later; the investigation body's annual report extract read does not state the toll.

**What happened.** A freight train of 14 LPG tank cars passed through Viareggio station at night when an axle on the first wagon failed. Cars derailed and the overturned lead car was punctured, releasing over 45 t of LPG. The dense cloud spread into neighbouring streets and ignited, with explosions, flash fire and pool fires.

**Causes** (official investigation):

- Italian rail investigation body: fatigue failure of a wagon axle due to lack of proper maintenance
- Its annual report points to weak control and traceability of outsourced wagon maintenance
- 2014 paper: the tank was holed by a trackside object, with a stake or a switch assembly offered as hypotheses

**Key learnings:**

- Make basic maintenance rules for dangerous-goods wagons mandatory and keep safety-critical components traceable; certification alone was judged ineffective. *[source]*
- Consider removing or replacing trackside items that can cut or tear a derailed tank, starting at the most exposed urban sites. *[source]*
- A client's safety assurance cannot stop at checking that a maintenance contractor holds a certificate. *[compiler]*

**Discuss:**

1. What evidence beyond certification would you require from a firm maintaining safety-critical transport equipment?
2. Which fixed objects along a hazardous cargo route could puncture a derailed or overturned tank?

**Topics:** Hazardous materials in transport, Mechanical integrity and corrosion, Contractors and interfaces, Vapour cloud explosions.

**Sources read:**

- [A] [Annual Report 2013, Italian Railway Investigation Body (NIB IT)](https://www.era.europa.eu/sites/default/files/reports/RELAZIONE%20ANNUALE%202013-EN.pdf), Direzione Generale per le Investigazioni Ferroviarie (published by ERA)
- [B] [New Insights into the Viareggio Railway Accident (Manca, Chemical Engineering Transactions 36, 2014)](https://www.aidic.it/cet/14/36/003.pdf), AIDIC

### Montara wellhead platform blowout

`montara-2009` · 2009-08-21 · Montara Wellhead Platform, Timor Sea, Australia · oil and gas upstream · blowout · crude oil and gas

**Deaths:** 0 (see note). The report states that the 69 personnel were safely evacuated.

**What happened.** A suspended well on the Montara wellhead platform kicked and flowed uncontrolled during return-to-well operations. All personnel were evacuated. Oil and gas flowed into the Timor Sea for more than ten weeks.

**Causes** (official investigation):

- Primary barrier, the cemented 9-5/8 inch casing shoe, failed; the cement job was compromised and not pressure tested
- A second pressure-containing cap was never installed and the one fitted was later removed and not reinstated
- No barrier complied with the company's own well construction standards at suspension
- Systemic weaknesses in company competence, communication and records; weak regulatory oversight

**Key learnings:**

- Keep at least two tested and verified barriers in place whenever reasonably practicable, including batch operations. *[source]*
- Do not rely on a single barrier against blowout. The only exception should be a true emergency with the regulator's prior written approval, given only after a proper risk assessment, in exceptional circumstances and with risk reduced as low as reasonably practicable. *[source]*
- Anomalies in a barrier installation must trigger testing and remediation; a plan on paper does not prove a barrier exists. *[compiler]*

**Discuss:**

1. What test results would you require before counting a cement shoe as a well barrier?
2. How should day/night, rig/shore and contractor handovers record the status of safety-critical barriers?

**Topics:** Well control and offshore barriers, Management of change, Contractors and interfaces, Leadership and safety culture.

**Sources read:**

- [A] [Report of the Montara Commission of Inquiry, June 2010](https://www.industry.gov.au/sites/default/files/2018-11/montara-commission-of-inquiry-report-june-2010.pdf), Commonwealth of Australia

### Indian Oil Jaipur POL terminal vapour cloud explosion

`ioc-jaipur-2009` · 2009-10-29 · Sanganer, Jaipur, Rajasthan, India · storage and terminals · vapour cloud explosion, fire · motor spirit (petrol)

**Deaths:** 11 (see note). The inquiry report gives 11 (six from IOC, five outsiders).

**What happened.** While petrol was being lined up for transfer, a large leak came from a Hammer Blind valve. The operating crew were overcome or absent, and the leak ran uncontrolled for about 75 minutes. The vapour cloud then exploded and the fire spread to all tanks, burning for about 11 days and destroying the terminal.

**Causes** (official investigation):

- Normal valve operating sequence not followed during line-up
- Hammer Blind valve design left a large opening during changeover
- No site-specific written procedure and no usable remote shut-off
- Poor understanding of the hazard; emergency shutdown backup and control-room cover lacking

**Key learnings:**

- Provide remote isolation and design changes that make operator error less likely. *[source]*
- Site large installations using quantitative risk assessment and consider buffer-zone land-use controls. *[source]*
- Have site-specific written procedures and keep redundant safety systems in working order. *[source]*
- A long uncontrolled loss of containment must be treated as a credible event in hazard identification. *[source]*

**Discuss:**

1. How would you design the tank outlet line-up so that no single sequence error can open the tank to atmosphere?
2. What detection and response should work if the only operators present are incapacitated in the first minute?

**Aftermath.** A 2011 Lok Sabha answer states the ministry accepted the committee's recommendations and told oil marketing companies to implement them.

**How far the sources go.** The report was read from a copy on the FABIG site that is headed 'Confidential'; a 2010 Lok Sabha answer states the report was put in the public domain.

**Topics:** Vapour cloud explosions, Isolation, permits and handover, Hazard identification, Facility siting and occupied buildings.

**Sources read:**

- [A] [IOC Fire Accident Investigation Report (Independent Inquiry Committee chaired by M.B. Lal); copy hosted by FABIG](https://www.fabig.com/media/hu5d2dmi/ioc-fire-accident-investigation-report.pdf), Ministry of Petroleum and Natural Gas committee
- [A] [Lok Sabha Starred Question 113, 04.03.2010 (states the report was put in the public domain)](https://eparlib.nic.in/bitstream/123456789/577546/1/82388.pdf), Lok Sabha
- [A] [Lok Sabha Unstarred Question 641, 24.11.2011](https://eparlib.nic.in/bitstream/123456789/610852/1/112925.pdf), Lok Sabha

### Macondo blowout, Deepwater Horizon

`deepwater-horizon-2010` · 2010-04-20 · Macondo well, Gulf of Mexico off Louisiana, United States of America · oil and gas upstream · blowout, explosion, fire · oil and gas

**Deaths:** 11.

**What happened.** During temporary well abandonment, a failed bottom cement barrier was wrongly judged sealed after a pressure test. Mud was removed and hydrocarbons flowed undetected for almost an hour. Gas reached the rig and ignited. The blowout preventer did not seal the well; the rig sank.

**Causes** (official investigation):

- Cement barrier not effectively installed; negative pressure test misread
- Influx not detected in time
- Blowout preventer had latent faults (miswiring) and buckled drillpipe stopped the blind shear ram sealing
- Operator and contractor had vague safety roles; process safety got less attention than personal safety

**Key learnings:**

- Treat people as safety barriers and design and manage them with their limits in mind. *[source]*
- Close the gap between work as planned and work as done in safety-critical well operations. *[source]*
- Test and verify safety-critical elements, including redundant emergency systems, for latent failure. *[source]*
- Measure process safety indicators with the same effort as personal injury statistics. *[source]*

**Discuss:**

1. What acceptance criteria and independent check would you set for a negative pressure test?
2. How can a redundant emergency system be proof-tested so that one dead channel cannot hide?

**Topics:** Well control and offshore barriers, Leadership and safety culture, Alarms, displays and human factors, Contractors and interfaces.

**Sources read:**

- [A] [Macondo Blowout and Explosion, investigation page](https://www.csb.gov/macondo-blowout-and-explosion/), U.S. Chemical Safety Board
- [A] [Macondo Investigation Report, Executive Summary (April 2016)](https://www.csb.gov/file.aspx?DocumentId=5997), U.S. Chemical Safety Board

### Cosmo Oil Chiba refinery LPG sphere fire and BLEVEs

`cosmo-chiba-2011` · 2011-03-11 · Ichihara, Chiba, Japan · refining · fire, BLEVE, vapour cloud explosion · LPG

**Deaths:** 0 (see note). The IChemE summary lists 0 fatalities and 6 injuries.

**What happened.** The Tohoku earthquake damaged the leg braces of an LPG sphere that was full of water for inspection. In an aftershock it collapsed and broke adjacent LPG pipes. A locked-open emergency block valve kept feeding the fire, and successive BLEVEs destroyed the LPG tank farm and affected neighbouring plants.

**Causes** (secondary account):

- Water-filled sphere carried much more weight than the LPG design case; braces and legs failed
- Water left in for 12 days instead of the usual 2-3
- Emergency block valve locked open, against regulations
- Pipe damage on collapse, tight spacing and delayed firefighting escalated the event

**Key learnings:**

- Strengthen sphere legs and braces in seismic areas, including for water-filled conditions. *[source]*
- Include natural-hazard triggers in emergency planning and drill with degraded access and communications. *[source]*
- Provide piping flexibility near spheres so a collapse is less likely to break lines. *[source]*
- A defeated emergency isolation valve needs formal approval, time limits and compensating measures. *[compiler]*

**Discuss:**

1. Which temporary conditions, such as hydrotest water, should be design load cases combined with earthquake?
2. How would your bypass register have treated the locked-open valve?

**Topics:** Natural hazards and loss of utilities, Fires and BLEVE, Isolation, permits and handover, Mechanical integrity and corrosion.

**Sources read:**

- [B] [eNatech accident record: Cosmo Oil refinery, Tohoku earthquake](https://enatech.jrc.ec.europa.eu/view/natech/14), European Commission Joint Research Centre
- [B] [Individual incident summary: multiple LPG storage tanks rupture after earthquake](https://www.icheme.org/media/17219/chiba-incident-summary-11-mar-11.pdf), IChemE Lessons Learned Database

### Mitsui Chemicals Iwakuni-Ohtake resorcinol plant explosion

`mitsui-iwakuni-2012` · 2012-04-22 · Waki-cho, Yamaguchi, Japan · chemicals · runaway reaction, explosion, fire · organic hydroperoxide

**Deaths:** 1 (see note). The committee report gives 1 dead and 25 injured.

**What happened.** A steam failure led to emergency shutdown of a batch oxidation reactor. About an hour later an operator released the interlock to speed cooling, which also stopped the nitrogen that kept the liquid mixed. Peroxide in the uncooled upper section decomposed, and the reactor burst, spreading fire to adjacent equipment.

**Causes** (secondary account):

- Interlock released, stopping nitrogen and agitation
- No cooling coil in the upper liquid and thermometer for the interlock only in the lower part
- No criteria in the manual for releasing the interlock; release was easy and its side effect undocumented
- No alarm for loss of agitation gas; the main control screen did not show nitrogen flow and made the temperature distribution hard to read once agitation stopped
- Underlying: weak risk assessment, loss of skills and disregard of rules

**Key learnings:**

- Make the reactor inherently safer after emergency shutdown with both hardware and procedural measures: cool it promptly, keep it agitated, and define clear stable conditions under which the interlock may safely be released. *[source]*
- Address underlying causes: risk assessment, passing on skills, rule compliance and ownership of hazards. *[source]*
- A safe state after trip should be defined in measurable terms, and resetting a trip must not silently remove a protective function. *[compiler]*

**Discuss:**

1. How would you redesign the interlock so that changing cooling mode cannot stop mixing?
2. Where should temperature sensors be if agitation can fail?

**How far the sources go.** The investigation read is by an external committee appointed by the company, not a public authority.

**Topics:** Reactive and runaway hazards, Alarms, displays and human factors, Start-up, shutdown and abnormal operation, Leadership and safety culture.

**Sources read:**

- [B] [Resorcinol Plant Accident Investigation Committee Report, 23 January 2013](https://jp.mitsuichemicals.com/en/release/2013/pdf/130123_02e.pdf), Mitsui Chemicals (committee of academics and external specialists)

### Bangkok Synthetics explosion and fire, Map Ta Phut

`map-ta-phut-bst-2012` · 2012-05-05 · Map Ta Phut Industrial Estate, Rayong, Thailand · chemicals · explosion, fire · toluene (reported)

**Deaths:** 12 (see note). Deputy Public Health Minister's figure of 12 dead and 129 injured; other reports give injuries up to about 140. Police at one point could confirm only 10.

**What happened.** An explosion and fire hit a Bangkok Synthetics synthetic rubber plant. A company officer said the factory had been closed for repairs beforehand, and the provincial governor said the blasts occurred while workers were cleaning a chemical tank. Smoke spread widely and more than a thousand nearby residents were evacuated.

**Causes** (not established):

- Early reports only: blast during tank cleaning or while toluene was being put into a tank
- A company officer suggested toluene might have ignited after excessive heat; no final investigation was read

**Key learnings:**

- Tank cleaning and other shutdown work around flammable materials needs the same hazard study, ignition control and permits as normal operation, whatever the eventual cause here. *[compiler]*
- Community warning arrangements around petrochemical estates should be tested. *[compiler]*

**Discuss:**

1. What would your permit for cleaning a tank that has held, or may receive, flammable liquid require?
2. What non-flammable or lower-hazard cleaning options would you evaluate first?

**Topics:** Start-up, shutdown and abnormal operation, Isolation, permits and handover, Ignition control, Emergency response and evacuation.

**Sources read:**

- [C] [Map Ta Phut toll: 12 dead, 129 injured](https://www.bangkokpost.com/thailand/politics/292091/map-ta-phut-toll-12-killed129-wounded), Bangkok Post
- [C] [Blasts, fire at Thai petrochemical plant kill 12](https://www.claimsjournal.com/news/international/2012/05/07/206320.htm), Associated Press via Claims Journal
- [C] [12 killed, 140 injured in Thailand factory explosion](https://www.joiff.com/members/sharedlearning/topics/archive2012/ThailandFactoryExplosion.html), JOIFF shared learning (news compilation)

### Amuay refinery vapour cloud explosion

`amuay-2012` · 2012-08-25 · Amuay refinery, Paraguana, Falcon, Venezuela (Bolivarian Republic of) · refining · vapour cloud explosion, fire · olefins

**Deaths:** 42 (see note). COENER report gives 42 dead and 5 missing as the official figures and cites unofficial estimates of more than 95 dead. No official final report was read directly.

**What happened.** A cloud of flammable gas in the Block 23 storage area of the refinery ignited at about 01:10, causing a vapour cloud explosion followed by tank fires. Plant installations and nearby shops, schools and homes were destroyed.

**Causes** (disputed):

- State investigation (as reported in news): deliberate sabotage, with intentionally loosened bolts on a gas pump
- Non-official COENER report: most probably mechanical seal failure on one or more P-200 olefin pumps
- COENER: gas present for hours without alarm activation or evacuation
- COENER (non-official): weak maintenance and safety culture. A news report says an opposition investigation blamed poor maintenance and underinvestment; the files read do not show whether that was a separate study

**Key learnings:**

- COENER recommends keeping alarm systems operable, completing preventive maintenance and empowering operating staff. *[source]*
- COENER recommends respecting safety zones around refineries and independent audits of sites near communities. *[source]*
- When official and independent accounts conflict, teach both and ask what physical evidence would separate them. *[compiler]*

**Discuss:**

1. What evidence would distinguish seal failure from tampering on a pump flange or gland?
2. With a confirmed uncontrolled light-hydrocarbon leak, what triggers alarm and off-site evacuation?

**How far the sources go.** The report read is not the official one and is hosted by a political party; the state's findings were known only through news.

**Topics:** Vapour cloud explosions, Mechanical integrity and corrosion, Emergency response and evacuation, Leadership and safety culture.

**Sources read:**

- [C] [Informe de Investigacion sobre la explosion e incendio ocurrido en la Refineria de Amuay (non-official; copy hosted by the opposition party Vente Venezuela)](https://www.ventevenezuela.org/wp-inter/uploads/2013/08/Informe-de-Investigacion-Amuay-Versi%C3%B3n-Final-14-08-2013-Re.pdf), Comite de Manufactura, COENER, 2013
- [C] [Venezuela probe says sabotage caused Amuay disaster](https://www.foxbusiness.com/markets/venezuela-probe-says-sabotage-caused-amuay-disaster), Fox Business
- [C] [What was behind Venezuela's deadly oil refinery explosion?](https://www.csmonitor.com/World/Americas/2013/0916/What-was-behind-Venezuela-s-deadly-oil-refinery-explosion), Christian Science Monitor

### Reynosa Pemex gas facility fire

`reynosa-2012` · 2012-09-18 · Near Reynosa, Tamaulipas, Mexico · oil and gas upstream · explosion, fire · natural gas

**Deaths:** 29 (see note). News figures changed over the first days: 26 dead with 7 missing on the day (Pemex, via Insurance Journal); 29 the next day, attributed to Pemex (Fox News); 30 two days later (AP, via Deseret News). No final official figure was read. Most of the dead were contract workers.

**What happened.** An explosion and fire hit a Pemex gas reception, metering and distribution facility near the US border, next to a gas processing plant. Many of those killed were contractors working at the site. Pemex shut in the pipeline and said it found no sign of sabotage.

**Causes** (not established):

- Pemex officials said an accidental leak appeared to have caused the fire
- AP reported executives saying a valve apparently failed during routine testing
- No official investigation report was read

**Key learnings:**

- Limit the number of people near live piping during testing to those the task needs. *[compiler]*
- Early company statements are not a root cause; look for the final investigation before drawing technical lessons. *[compiler]*

**Discuss:**

1. What permit and exclusion-zone rules would you apply to routine valve testing at a gas gathering hub?
2. How should a contractor-heavy site account for everyone within minutes of an explosion?

**Topics:** Contractors and interfaces, Isolation, permits and handover, Mechanical integrity and corrosion.

**Sources read:**

- [C] [Explosion, Fire at Mexico Pemex Gas Facility Kills 26](https://www.insurancejournal.com/news/international/2012/09/19/263451.htm), Insurance Journal
- [C] [Toll rises to 29 dead, 46 injured in Mexico pipeline fire](https://www.foxnews.com/world/toll-rises-to-29-dead-46-injured-in-mexico-pipeline-fire.print), Fox News
- [C] [Mexico blast a blow to Pemex's improving safety](https://www.deseret.com/2012/9/20/20436944/mexico-blast-a-blow-to-pemex-s-improving-safety/), Deseret News (AP)

### Gumi hydrogen fluoride release

`gumi-hf-2012` · 2012-09-27 · Gumi National Industrial Complex, North Gyeongsang, Republic of Korea · chemicals · toxic release · anhydrous hydrogen fluoride

**Deaths:** 5.

**What happened.** While anhydrous hydrogen fluoride was being moved from a tank lorry to dilution equipment, a valve was opened by mistake and several tonnes escaped. Five workers died, thousands of people later sought medical attention, and responders were among those exposed.

**Causes** (secondary account):

- Worker error opened a valve during transfer for dilution
- The tank lorry was pressurised for the transfer and release continued until the pressurising pump was switched off after about 30 minutes. The modelling paper says full closure of the lorry valve took about 8 hours, but judges that little escaped after the pump stopped.

**Key learnings:**

- Toxic transfer connections need remote emergency isolation and design that prevents unintended valve opening. *[compiler]*
- Responders need chemical-specific protective equipment and guidance for HF before an event; a study of responders linked symptoms to proximity, duration and lack of respiratory protection. *[compiler]*

**Discuss:**

1. What layers of protection should exist on a tanker unloading connection for anhydrous HF?
2. How should responder rotation and respiratory protection be planned when breathing apparatus air lasts under an hour?

**Aftermath.** A 2025 Processes paper says Korea subsequently enacted a new chemical safety management law with off-site consequence analysis and risk management plan elements.

**Topics:** Toxic releases, Hazardous materials in transport, Emergency response and evacuation, Isolation, permits and handover.

**Sources read:**

- [B] [Acute Symptoms in Firefighters who Participated in Collection Work after the Community Hydrogen Fluoride Spill Accident](https://pmc.ncbi.nlm.nih.gov/articles/PMC3923340), Annals of Occupational and Environmental Medicine
- [B] [Comparison of damage-range prediction models using the Gumi accident (in Korean)](https://koreascience.kr/article/JAKO201713059664140.pdf), Korean Chemical Engineering Research 55(1)
- [B] [Systematic Cause Analysis of an Explosion Accident During the Packaging of Dangerous Goods (mentions Gumi in its introduction)](https://mdpi-res.com/d_attachment/processes/processes-13-00687/article_deploy/processes-13-00687.pdf), Processes (MDPI)

### Nippon Shokubai Himeji acrylic acid tank explosion

`himeji-2012` · 2012-09-29 · Himeji, Hyogo, Japan · chemicals · runaway reaction, BLEVE, fire · acrylic acid

**Deaths:** 1 (see note). One municipal firefighter died; ARIA counts 37 casualties in total including this death.

**What happened.** An intermediate tank was filled during a column test without its upper recirculation running. Uncooled upper layers dimerised and then polymerised. White vapour revealed the runaway; water spray on the insulated tank did not help. The tank burst while firefighters were nearby, and the contents ignited.

**Causes** (secondary account):

- Upper recirculation not started, leaving liquid above the cooling coil stagnant and uncooled
- No temperature instrumentation on the tank
- Outdated manual and poor training for an infrequent operating mode
- Weak oversight of modifications (a cooling loop designed for 25 m3 was not upgraded) and of maintenance (removal of the steam-trace temperature control was not logged)
- Earlier polymerisation incident not shared; late call to the fire service

**Key learnings:**

- Review risk and barriers for even minor changes and update operating documents to match. *[source]*
- Train for infrequent operating phases. *[source]*
- Continuously monitor parameters critical to runaway for each reactive material. *[source]*

**Discuss:**

1. Which hazard study prompt would have caught that cooling capacity only covered part of the tank volume?
2. When should firefighters withdraw from a vessel with a suspected runaway, and who tells them?

**Aftermath.** ARIA reports that authorities kept the damaged unit from restarting until the technical investigation was completed.

**Topics:** Reactive and runaway hazards, Management of change, Alarms, displays and human factors, Emergency response and evacuation.

**Sources read:**

- [B] [ARIA No. 42817: Explosion and fire on an acrylic acid tank at a chemical plant (based on the investigation commission report)](https://www.aria.developpement-durable.gouv.fr/wp-content/files_mf/FD_42817_Himeji_GB.pdf), French Ministry for Sustainable Development, BARPI

### West Fertilizer fire and explosion

`west-fertilizer-2013` · 2013-04-17 · West, Texas, United States of America · explosives and fertiliser · fire, explosion · fertiliser-grade ammonium nitrate

**Deaths:** 15 (see note). CSB final report: 12 emergency responders and 3 members of the public (15). The CSB web page summary says twelve volunteer firefighters and two members of the public, while its video description says 15 fatalities.

**What happened.** A fire at a fertiliser storage and retail site led, about 20 minutes after the first emergency calls, to detonation of ammonium nitrate. Responders and residents were killed, many were injured, and homes, schools and a nursing home nearby were badly damaged.

**Causes** (official investigation):

- CSB: combustible building and bin materials and combustibles stored nearby fed the fire and likely led to detonation
- CSB: no fire detection or sprinklers; no pre-incident planning or FGAN response training
- CSB: the town had grown up close to the site
- Fire origin: CSB (January 2016) reported no final determination; in May 2016 ATF ruled the fire intentionally set (read via news report)

**Key learnings:**

- Keep combustibles away from ammonium nitrate and use noncombustible buildings and bins, and also provide fire detection and automatic sprinklers. CSB addressed recommendations on these points to code and regulatory bodies. *[source]*
- Fire services need pre-incident planning and specific ammonium nitrate hazard training. *[source]*
- CSB found shortcomings in regulation, land-use planning and insurer oversight. Its recommendations addressed regulatory coverage and insurer guidance, among other things; none of its numbered recommendations was a land-use planning measure. *[source]*

**Discuss:**

1. When should a fire service withdraw rather than fight a fire near ammonium nitrate, and what information would it need in advance?
2. How should planners treat a rural store that housing and schools have since surrounded?

**Aftermath.** CSB's report says the President issued Executive Order 13650 on chemical facility safety and security in response.

**Topics:** Storage, quantities and segregation, Reactive and runaway hazards, Land-use planning and neighbours, Emergency response and evacuation. Also in the [CSB register](INCIDENTS.md) as `west-fertilizer-2013`.

**Sources read:**

- [A] [West Fertilizer Explosion and Fire, investigation page](https://www.csb.gov/west-fertilizer-explosion-and-fire-/), U.S. Chemical Safety Board
- [A] [Investigation Report: West Fertilizer Company Fire and Explosion (January 2016)](https://www.csb.gov/file.aspx?DocumentId=5983), U.S. Chemical Safety Board
- [C] [ATF: 2013 Fire at Texas Fertilizer Plant Intentionally Set](https://www.insurancejournal.com/news/southcentral/2016/05/11/408160.htm), Insurance Journal

### Lac-Megantic runaway oil train

`lac-megantic-2013` · 2013-07-06 · Lac-Megantic, Quebec, Canada · transport · fire, explosion · petroleum crude oil

**Deaths:** 47.

**What happened.** A parked, unattended 72-tank-car crude train on a grade lost locomotive air-brake pressure after its engine was shut down following a fire. With too few hand brakes, it rolled about seven miles and derailed in the town centre in the early hours (it was parked on the evening of 5 July). Fire and explosions followed.

**Causes** (official investigation):

- Too few hand brakes; the effectiveness test was done with locomotive air brakes still applied
- Shutting down the locomotives let air leak away from the independent brakes
- A poor earlier engine repair led to the locomotive fire
- Weak company safety culture, training and supervision; weak regulatory follow-up and SMS audit
- Tank cars met the requirements then in force but were of an older standard; almost every derailed car was breached, and enhanced safety features could have reduced the damage. Separately, the crude was more volatile than shipping documents described, which the TSB treats as a risk

**Key learnings:**

- Railways need additional physical defences against runaway trains. *[source]*
- The regulator should check that safety management systems work, not only that they exist. *[source]*
- Flammable-liquid tank cars need tougher protection standards, and routes for dangerous goods should be risk-planned. *[source]*

**Discuss:**

1. Design a securement test that cannot be passed with the air brakes still holding the train. What independent barrier would you add?
2. How should information about changes in equipment state, such as a locomotive being shut down, reach someone competent to judge the brake effect?

**Aftermath.** TSB reports that Transport Canada issued an emergency directive barring single-person crews on dangerous-goods trains and that parts of the Canadian Rail Operating Rules were rewritten.

**Topics:** Hazardous materials in transport, Leadership and safety culture, Alarms, displays and human factors, Management of change.

**Sources read:**

- [A] [Lac-Megantic runaway train and derailment investigation summary (R13D0054)](https://www.tsb.gc.ca/eng/rapports-reports/rail/2013/r13d0054/r13d0054-r-es.html), Transportation Safety Board of Canada

### Sinopec Donghuang crude oil pipeline leak and explosions

`qingdao-pipeline-2013` · 2013-11-22 · Huangdao District, Qingdao, Shandong, China · pipeline · pipeline rupture, vapour cloud explosion, fire · crude oil

**Deaths:** 62 (see note). Both papers read give 62 dead and 136 injured; one passage in the Petroleum Science paper breaks down 61 deaths.

**What happened.** A corroded buried crude pipeline ruptured where it crossed a covered culvert. Oil entered the confined drainage space and vapour built up for hours during repair work. About eight hours after the leak, excavation with equipment that was not explosion-proof ignited the mixture, with explosions in a built-up area.

**Causes** (secondary account):

- Corrosion in a saline, tidal culvert environment; coating overhaul unfinished and inspections missed the damage
- Oil collected and vaporised in a confined conduit
- Slow reporting and poor emergency assessment
- Sparks from a non-explosion-proof hydraulic hammer without effective gas testing

**Key learnings:**

- Assess the consequences of oil entering confined spaces, collect and ventilate quickly, and monitor for flammable gas during repair. *[source]*
- Report leaks immediately and set isolation areas based on fire and explosion risk. *[source]*
- Account for urban growth around old pipelines and keep separation from buildings. *[source]*

**Discuss:**

1. What survey would identify every place where your pipeline's leak could enter a drain or culvert?
2. What conditions must be met before excavation starts at a hydrocarbon leak?

**Topics:** Pipeline integrity, Emergency response and evacuation, Ignition control, Land-use planning and neighbours.

**Sources read:**

- [B] [Modeling and analysis of a catastrophic oil spill and vapor cloud explosion in a confined space upon oil pipeline leaking](https://www.cup.edu.cn/petroleumscience/docs/2019-11/c6c0ac5aa2c749098a227691551a416e.pdf), Petroleum Science
- [B] [Application of an Improved Model for Accident Analysis: A Case Study](https://pmc.ncbi.nlm.nih.gov/articles/PMC6695596), International Journal of Environmental Research and Public Health

### GAIL Tatipaka-Kondapalli gas pipeline explosion

`gail-andhra-2014` · 2014-06-27 · Tatipaka-Kondapalli pipeline, Andhra Pradesh, India · pipeline · pipeline rupture, vapour cloud explosion, fire · natural gas and condensate

**Deaths:** 22 (see note). PTI's September 2014 account of the inquiry gives 22.

**What happened.** Condensate and gas leaking from a corroded pipeline, probably since the previous night, formed a vapour cloud. It ignited early in the morning, possibly from a stove being lit at a tea vendor's. The fire engulfed nearby dwellings and tea stalls.

**Causes** (secondary account):

- Line designed for dry gas carried wet gas with water and condensate, causing internal corrosion
- Committed gas dehydration units were not installed
- Inquiry committee: GAIL's systems or approach to repeated repairs of the high-pressure lines appeared inadequate and was a factor; it found individual culpability hard to establish

**Key learnings:**

- Dehydrate gas before it enters the pipeline. *[source]*
- Inspect lines thoroughly, provide leak detection and patrol the route. *[source]*
- A change in the fluid carried compared with the design basis should go through management of change, and repeated leaks should trigger an integrity reassessment. *[compiler]*

**Discuss:**

1. What evidence would show that a pipeline's actual service had drifted from its design basis?
2. After how many repairs should a line be de-rated or taken out of service, and who decides?

**Topics:** Pipeline integrity, Mechanical integrity and corrosion, Management of change.

**Sources read:**

- [C] [OilMin probe blames lapses by GAIL for pipeline blast in AP](https://www.business-standard.com/article/pti-stories/oilmin-probe-blames-lapses-by-gail-for-pipeline-blast-in-ap-114090900901_1.html), Business Standard (PTI)

### Kaohsiung underground propylene pipeline explosions

`kaohsiung-2014` · 2014-07-31 · Kaohsiung, Taiwan · pipeline · pipeline rupture, vapour cloud explosion, fire · propylene

**Deaths:** 32.

**What happened.** A buried propylene line leaked into a storm drain trench. Operators saw abnormal pressure and flow, ran a static pressure test and restarted pumping. Gas spread more than 4.5 km while responders could not identify it, then ignited about three hours after the leak, blowing up roads under crowded streets.

**Causes** (secondary account):

- Pipe exposed to humid air inside a drain trench corroded from 6 mm to under 1 mm
- The abnormal flow and pressure led to a stop and a static test, but pumping was restarted and a remaining flow discrepancy was left for later; neither company told the fire bureau or other authorities
- At least 90,000 kg estimated released into a connected trench network
- Probable ignition by a fire truck above a cable junction box (authors' analysis)

**Key learnings:**

- Include leaks into underground trenches in pipeline risk assessment and keep accurate pipeline and drain plans for responders. *[source]*
- Control ignition sources strictly; dispersal to below the flammable limit is the only safe outcome of such a leak. *[source]*
- Do not restart a line after an unexplained pressure or flow anomaly until the discrepancy is resolved by a test capable of finding the leak. *[compiler]*

**Discuss:**

1. Why could a static test at vapour pressure fail to reveal a leak in a liquefied gas line, and what test would you require?
2. How should an incident commander set the exclusion zone when gas may be travelling in drains?

**Topics:** Pipeline integrity, Vapour cloud explosions, Alarms, displays and human factors, Ignition control.

**Sources read:**

- [B] [Kaohsiung Vapour Explosion: a detailed analysis of the tragedy in the harbour city](https://www.aidic.it/cet/16/48/121.pdf), Chemical Engineering Transactions 48 (AIDIC)

### Kunshan Zhongrong aluminium dust explosion

`kunshan-2014` · 2014-08-02 · Kunshan, Jiangsu, China · metals and manufacturing · dust explosion · aluminium dust

**Deaths:** 146 (see note). 75 died immediately; the toll later rose to 146 (AP, December 2014). Early reports give 75.

**What happened.** A dust explosion hit a factory that polished aluminium vehicle wheels. Many injured workers later died in hospital.

**Causes** (secondary account):

- Preliminary finding: a flame in a dust-filled room
- Inadequate ventilation and dust removal and a substandard electrical system
- Rules on dust cleanup, explosion-protected equipment, building spacing and line density ignored
- Earlier dust warnings ignored and no safety training; weak local enforcement

**Key learnings:**

- Enforce dust cleanup, explosion-protected equipment, building spacing, production-line density rules and safety training. *[compiler]*
- Dust hazard analysis should cover metal-finishing shops, which may not be seen as process plants. *[compiler]*

**Discuss:**

1. How would you set housekeeping and dust-collector limits for an aluminium polishing shop?
2. How should production-line layout and the number of people exposed be treated as design variables that limit consequences?

**Aftermath.** The State Council dismissed the city's two top officials and others were put under judicial review (AP, December 2014).

**Topics:** Combustible dust, Ignition control, Leadership and safety culture, Facility siting and occupied buildings.

**Sources read:**

- [C] [China fires officials over deadly auto parts factory blast](https://www.claimsjournal.com/news/international/2014/12/31/259639.htm), Associated Press via Claims Journal
- [C] [Safety violations at China auto factory led to dust blast](https://www.swissinfo.ch/eng/safety-violations-at-china-auto-factory-led-to-dust-blast-xinhua/40536080), Reuters via SWI swissinfo.ch

### Accra flood and GOIL filling station fire

`accra-goil-2015` · 2015-06-03 · Kwame Nkrumah Circle, Accra, Ghana · storage and terminals · fire · fuel floating on floodwater

**Deaths:** 150 (see note). A World Bank aide memoire on its 10-19 June 2015 mission attributes 150 deaths to the filling station fire, without giving an as-of date for that figure. Daily Graphic gives 159 for the flood and fire together.

**What happened.** During severe flooding, people sheltered at a filling station. Fuel mixed with the floodwater and ignited, burning people at and around the station.

**Causes** (secondary account):

- Flooding displaced fuel from the station; the government committee, as reported, cited leaking fuel tanks
- Fuel floating on the water
- Committee, as reported: a discarded lit cigarette ignited it

**Key learnings:**

- The government committee recommended drain dredging and training, certification and licensing of filling station attendants, among other measures. *[source]*
- Underground fuel storage design and siting must consider flooding: water ingress, tank displacement, vents and fill points below flood level. *[compiler]*
- Fuel on floodwater carries ignition hazard far beyond the station's classified zones. *[compiler]*

**Discuss:**

1. What flood scenarios should a filling station hazard study include, and what should staff do when water reaches the forecourt?
2. Should some flood-prone urban sites be closed to fuel retail, and by what criteria?

**Aftermath.** A year later Daily Graphic reported that some filling stations had been demolished but that many committee recommendations had not been carried out.

**How far the sources go.** The World Bank document supports the toll and only briefly mentions a leak linked to the flood; the government committee's cause is known only through a newspaper.

**Topics:** Natural hazards and loss of utilities, Land-use planning and neighbours, Ignition control, Storage, quantities and segregation.

**Sources read:**

- [A] [Technical Scoping Mission, Ghana Floods, 10-19 June 2015: Aide Memoire (scanned; text by local OCR)](https://repository.parliament.gh/server/api/core/bitstreams/5bd7102e-8e58-4c6f-84b1-9c94c6f5883c/content), World Bank (Parliament of Ghana repository)
- [C] [A year after the June 3 twin disaster (1 June 2016)](https://www.graphic.com.gh/features/features/a-year-after-the-june-3-twin-disaster.html), Daily Graphic

### Tianjin port Ruihai warehouse explosions

`tianjin-2015` · 2015-08-12 · Binhai New Area, Tianjin, China · ports and warehousing · fire, explosion · nitrocellulose, ammonium nitrate

**Deaths:** 165 (see note). State Council investigators: 165 dead (including 99 firefighters and 11 police), plus 8 missing. The IChemE bulletin gives 173 including 104 firefighters.

**What happened.** A fire started in a container yard at a hazardous goods warehouse. Firefighters did not know what was stored. The fire spread to ammonium nitrate and two large explosions followed, the second much larger, devastating the surrounding area and dispersing other chemicals including sodium cyanide.

**Causes** (secondary account):

- Nitrocellulose dried out after loss of wetting agent, self-heated in hot weather and ignited
- Fire spread to illegally stored ammonium nitrate
- Containers stacked too close and quantities beyond permits; residences too near
- Responders not told of the contents; company violations and failed official oversight

**Key learnings:**

- Keep self-reactive materials wetted and away from heat, and segregate them from oxidisers. *[source]*
- Emergency responders need reliable knowledge of stored materials and planning for hazardous chemical fires. *[source]*
- Coordinate regulation so that siting and permit limits are enforced. *[source]*

**Discuss:**

1. What inventory information should be available to the fire service within minutes, even at night?
2. How would you set separation and quantity limits in a mixed dangerous-goods yard?

**Aftermath.** The IChemE bulletin article reports that a national inspection of hazardous material storage sites followed.

**How far the sources go.** The professional source is a student prize paper; the official toll and cause were read in a news agency report, not the investigation report.

**Topics:** Storage, quantities and segregation, Reactive and runaway hazards, Emergency response and evacuation, Land-use planning and neighbours.

**Sources read:**

- [B] [Failures, repeated: the Tianjin explosion (student SIESO Medal paper), Loss Prevention Bulletin 286](https://www.icheme.org/media/18714/lpb286_pg17.pdf), IChemE
- [C] [China probe says stored chemical caused Tianjin blasts](https://www.philstar.com/world/2016/02/05/1550331/china-probe-says-stored-chemical-caused-tianjin-blasts), Associated Press via Philstar

### BASF Ludwigshafen North Harbour pipeline fire and explosion

`ludwigshafen-2016` · 2016-10-17 · North Harbour, Ludwigshafen, Germany · pipeline · fire, explosion, pipeline rupture · butylene mixture (raffinate), ethylene and other pipeline products

**Deaths:** 5 (see note). BASF's 2 December 2016 update gives four dead. Pipeline Technology Journal, reporting the court judgment, gives 5 dead (4 firefighters) and 44 injured.

**What happened.** During preventive replacement work on an emptied pipeline in a pipe trench, a cut was made into a neighbouring line that was not part of the job and held flammable raffinate. A fire started, and during early firefighting an explosion occurred, probably at an ethylene line, spreading fire along the trench.

**Causes** (secondary account):

- Prosecutor and police statement (translated by BASF): a line outside the work scope had been cut, apparently with a cutting disc
- BASF preliminary view: leaking butylene mixture ignited by angle grinder sparks
- Pipeline Technology Journal: a subcontractor accidentally cut the wrong pipe and was sentenced to one year on parole (it describes the work as welding); it also reports that BASF was mentioned as co-responsible during the trial but would not be prosecuted

**Key learnings:**

- Mark the exact pipe and cut location physically in the field and verify it jointly before any hot cutting in congested racks or trenches. *[compiler]*
- Emergency crews approaching a pipe-trench fire need to consider escalation from adjacent pressurised lines. *[compiler]*

**Discuss:**

1. How would you make it practically impossible to cut the wrong line in a crowded pipe trench?
2. What approach distance and information would your fire crew use at a pipe corridor fire?

**Topics:** Isolation, permits and handover, Contractors and interfaces, Pipeline integrity, Emergency response and evacuation.

**Sources read:**

- [C] [Update: Fire at the North Harbor in Ludwigshafen (last update 27 October 2016)](https://www.basf.com/global/en/media/news-releases/2016/10/p-16-359), BASF
- [C] [Update: Fire at the North Harbor in Ludwigshafen (last update 2 December 2016)](https://www.basf.com/global/en/media/news-releases/2016/12/p-16-391), BASF
- [C] [Court rules over subcontractor who caused gas explosion at BASF site](https://pipeline-journal.net/news/court-rules-over-subcontractor-who-caused-gas-explosion-basf-site), Pipeline Technology Journal

### Ahmedpur East road tanker petrol fire

`ahmedpur-east-2017` · 2017-06-25 · Ahmedpur East (Ahmedpur Sharqia), Bahawalpur, Punjab, Pakistan · transport · fire, explosion · petrol

**Deaths:** 214 (see note). 214 is the toll in the Dawn page read (July 2017), attributed to medical sources; it was still changing and a final official toll was not read.

**What happened.** A fuel tanker overturned on a highway. A large crowd gathered to collect the spilled petrol despite attempts by the driver and motorway police to clear the area. After about ten minutes the fuel ignited, engulfing the crowd.

**Causes** (secondary account):

- Regulator committee: tanker did not meet technical and legal standards for its load and carried a fake fitness certificate
- Licensee remained responsible for outsourced haulage
- Regulator report as quoted by Dawn: ignition attributed to low public awareness and to absent or late cordoning by local government and motorway police
- Rollover cause not officially established: the article says the tanker overturned during a sharp turn, and also reports an unconfirmed account from police sources about driver fatigue. The ignition source had not been officially established

**Key learnings:**

- Hold marketers to a timed plan to bring contracted tankers up to safety rules. *[source]*
- Run public hazard awareness campaigns and review local patrol and quick-response plans. *[source]*

**Discuss:**

1. How should a fuel company assure the condition and certification of contracted vehicles?
2. What can the first two people at an overturned tanker realistically do about a gathering crowd?

**Aftermath.** The regulator OGRA fined Shell Pakistan Rs10 million and ordered compensation to victims.

**How far the sources go.** Only a newspaper account of the regulator's report was read.

**Topics:** Hazardous materials in transport, Contractors and interfaces, Emergency response and evacuation, Ignition control.

**Sources read:**

- [C] [Bahawalpur tragedy: Shell ordered to pay Rs10m penalty, Rs240m in compensation to victims' families](https://www.dawn.com/news/1343802/bahawalpur-tragedy-ogra-imposes-more-than-rs250m-penalty-on-shell), Dawn

### Mongstad refinery cracker naphtha leak

`mongstad-2017` · 2017-10-24 · Mongstad, Norway · refining · toxic release · cracker naphtha

**Deaths:** not stated (see note). No deaths are reported; the report records no ignition and no symptoms in the operator who found the leak, but states no casualty count. This was a leak without fire.

**What happened.** An operator following up a report of an unusual smell found a naphtha leak from a small pump minimum-flow line in the cracker, caused by internal corrosion. The section was isolated and the plant evacuated. The leak did not ignite, but the investigators said ignition could have produced a substantial fire.

**Causes** (official investigation):

- Internal corrosion of a pump protection line
- Changes in operating conditions, including salt handling by water washing and chemicals, not assessed for plant integrity
- Inspection programme not revised after higher corrosion rates were found
- Likely mechanism: ammonium chloride corrosion from inadequate chloride control, possibly linked to water washing or chemicals, with poorly controlled low flow causing deposits and condensation. Separately, the report found a weakness in information transfer: the night shift's smell observation was passed on only verbally (it did not cause the corrosion)

**Key learnings:**

- Review changes in operating conditions across disciplines for their effect on integrity and inspection. *[source]*
- Revise risk-based inspection when measured corrosion exceeds assumed rates. *[source]*
- Record safety-relevant observations at shift handover and assess exposure hazards, not only flammability, when clearing contaminated material. *[source]*

**Discuss:**

1. Which gradual changes in feed or washing practice on a unit would trigger your management-of-change process?
2. How should findings on one part of a corrosion loop change inspection of the rest?

**Aftermath.** The Petroleum Safety Authority Norway identified four regulatory nonconformities and one improvement point.

**Topics:** Mechanical integrity and corrosion, Management of change, Alarms, displays and human factors, Isolation, permits and handover.

**Sources read:**

- [A] [Investigation report: Mongstad refinery, naphtha leak in cracker, 24 October 2017](https://www.havtil.no/contentassets/74b1e297d48b4f97a8987dd6f8c7682b/2017_1147_investigation-report-mongstad-naphta_102417.pdf), Petroleum Safety Authority Norway (now Havtil)

### Tlahuelilpan pipeline explosion

`tlahuelilpan-2019` · 2019-01-18 · San Primitivo, Tlahuelilpan, Hidalgo, Mexico · pipeline · pipeline rupture, fire, explosion · gasoline

**Deaths:** 137 (see note). CENAPRED gives 137 deaths in total. A news report of 1 March 2019, citing the Hidalgo state government, gave 134.

**What happened.** An illegal tap ruptured a 14-inch gasoline line on the Tuxpan-Tula section. Soldiers found the leak in the afternoon; a large crowd gathered to collect fuel and did not leave when asked. Hours later the fuel exploded and burned.

**Causes** (not established):

- Illegal tap ruptured the pipeline
- Large crowd gathered at the spill to collect gasoline
- Military personnel were heavily outnumbered and could not clear the area
- Ignition source not stated in the sources read

**Key learnings:**

- The CNDH made proposals to the authorities with prevention and non-repetition in view. Among them, Pemex should undergo an environmental impact assessment, including a risk study, for hydrocarbon transport even though not obliged to; the release also calls for affected people not to be stigmatised or criminalised and to have access to care. *[source]*
- A leaking liquid-fuel line in a populated or farmed area needs a pre-agreed plan covering shutdown of flow and crowd control. *[compiler]*
- Third-party interference belongs in pipeline hazard studies as a credible release cause with people present. *[compiler]*

**Discuss:**

1. On detecting a tap, what decides whether to stop pumping, and how fast can the line be isolated and the spill limited?
2. What can an operator do in advance when the public is likely to approach a release rather than flee it?

**How far the sources go.** The official sources are a socioeconomic impact study and a human rights commission press release; neither states the ignition source.

**Topics:** Pipeline integrity, Emergency response and evacuation, Fires and BLEVE.

**Sources read:**

- [A] [Impacto socioeconomico: explosion e incendio de gasolina en un ducto, Tlahuelilpan, Hidalgo, 18 de enero de 2019](https://www.cenapred.gob.mx/es/Publicaciones/archivos/407-IMPACTO_TLAHUELILPAN.pdf), CENAPRED (Mexican government)
- [A] [Comunicado DGDDH/018/2026](https://www.cndh.org.mx/sites/default/files/documentos/2026-02/COM_2026_018.pdf), Comision Nacional de los Derechos Humanos
- [C] [Death toll from Mexico pipeline fire rises to 134](https://www.news24.com/world/news/death-toll-from-mexico-pipeline-fire-rises-to-134-20190301), News24

### Xiangshui Tianjiayi Chemical explosion

`xiangshui-2019` · 2019-03-21 · Xiangshui, Yancheng, Jiangsu, China · chemicals · fire, explosion, runaway reaction · nitration waste

**Deaths:** 78.

**What happened.** Nitrated waste that had been stored illegally for long periods at a chemical plant in an industrial park self-heated and ignited, leading to a massive explosion with heavy casualties both injured and dead, and large economic loss.

**Causes** (secondary account):

- Long-term illegal storage of nitrated hazardous waste
- Heat accumulation took the waste past its autoignition temperature
- Deficient safety management and safety awareness
- Inadequate government supervision

**Key learnings:**

- Reactive wastes need the same thermal stability assessment, inventory limits and temperature monitoring as raw materials and products. *[compiler]*
- Inspections should reconcile waste generated against waste lawfully disposed of. *[compiler]*

**Discuss:**

1. How would you find undeclared or accumulating reactive waste on a site?
2. What data are needed to set a maximum pile size and residence time for a self-heating waste?

**How far the sources go.** The journal source was read as an abstract only; it gives the heat-accumulation mechanism and indirect causes. Prolonged illegal storage and spontaneous ignition come from a Xinhua report of the State Council investigation group's findings; the official report was not read.

**Topics:** Reactive and runaway hazards, Storage, quantities and segregation, Leadership and safety culture, Hazard identification.

**Sources read:**

- [B] [A summary of the investigation report on the Tianjiayi explosion incident (abstract only read)](https://doi.org/10.1002/prs.12132), Process Safety Progress
- [C] [Cause of deadly chemical plant blast in east China revealed](https://www.xinhuanet.com/english/2019-11/15/c_138558301.htm), Xinhua

### Morogoro fuel tanker fire and explosion

`morogoro-tanker-2019` · 2019-08-10 · Morogoro, United Republic of Tanzania · transport · fire, explosion · petrol

**Deaths:** 97 (see note). Toll rose as injured people died. Xinhua quoted a national hospital spokesperson giving 97 as of 19 August 2019 (not necessarily final); a 2022 burns-journal review says at least 89.

**What happened.** A fuel tanker overturned after an accident. People gathered to collect the leaking petrol, and the fuel ignited, causing a deadly fire and explosion.

**Causes** (secondary account):

- Tanker overturned and leaked
- Crowd collecting spilled fuel around the wreck
- Review attributes ignition to removal of the damaged truck's battery

**Key learnings:**

- Prevent the initial crash and, above all, deter people from collecting spilled fuel, which is linked to poverty. *[source]*
- A leaking tanker needs rapid cordoning and ignition control; responder arrival time and crowd control belong in transport risk assessment. *[compiler]*

**Discuss:**

1. How can a fuel distributor reduce harm in the first minutes after a rollover, before any emergency service arrives?
2. Which design, routing or social measures would you prioritise where spilled fuel has economic value to bystanders?

**Topics:** Hazardous materials in transport, Emergency response and evacuation, Ignition control.

**Sources read:**

- [B] [Catastrophes liees a une explosion de camion-citerne entre 2000 et 2020 (Ann Burns Fire Disasters 35(1), 2022)](https://pmc.ncbi.nlm.nih.gov/articles/PMC9020852), Euro-Mediterranean Council for Burns and Fire Disasters (PMC)
- [C] [Death toll climbs to 97 in Tanzania's fuel tanker explosion (20 August 2019)](http://www.xinhuanet.com/english/2019-08/20/c_138321510.htm), Xinhua

### LG Polymers styrene vapour release

`lg-polymers-2020` · 2020-05-07 · R.R. Venkatapuram, Visakhapatnam, Andhra Pradesh, India · chemicals · toxic release, runaway reaction · styrene

**Deaths:** 12 (see note). The High Power Committee gives 12 deaths in the immediate subsequent period and 585 hospitalised.

**What happened.** As the plant prepared to restart after a COVID-19 lockdown, styrene in a large storage tank polymerised and heated. In the early hours, vapour streamed from the tank vents into neighbouring settlements.

**Causes** (official investigation):

- Piping change inside the tank disrupted circulation, causing thermal stratification
- Refrigeration run only in daytime; single bottom temperature sensor missed hot upper layers
- Inhibitor monitored essentially only from bottom samples (top sampling very irregular); no inhibitor stock at the time and no dissolved oxygen monitoring
- Rising polymer content treated as a quality issue, not a safety warning
- No lockdown or restart procedure and no process safety management system

**Key learnings:**

- Treat idle or shutdown storage of reactive monomers as a separate operating mode with its own procedure and pre-startup safety review. *[source]*
- Measure temperature and inhibitor where hot spots can form, not at one convenient point. *[source]*
- In-tank piping changes need review of their effect on mixing and heat removal. *[compiler]*
- Quality data that indicate reaction progress should have safety alarm limits and an escalation route. *[compiler]*

**Discuss:**

1. Which measurements would give the earliest warning of runaway polymerisation in a 2,000-tonne tank, and what actions should each trigger?
2. How would your site decide what must keep running during an unplanned long shutdown?

**How far the sources go.** The committee report was read from a mirror on a non-government site.

**Topics:** Reactive and runaway hazards, Management of change, Start-up, shutdown and abnormal operation, Toxic releases.

**Sources read:**

- [A] [Report of the High Power Committee on the Styrene Vapour Release Accident at LG Polymers (copy hosted by Safteng)](https://safteng.net/wp-content/uploads/2020/07/HPCR_on_Styrene_vapour_release_accident_at_LG_Polymers.pdf), Government of Andhra Pradesh High Power Committee

### Baghjan-5 well blowout and fire

`baghjan-2020` · 2020-05-27 · Baghjan, Tinsukia, Assam, India · oil and gas upstream · blowout, fire · natural gas and condensate

**Deaths:** 2 (see note). The 2 are the Oil India firefighters reported killed in the June 2020 well fire (Deccan Herald). The expert committee volume read dates the explosion and fire to 9 June 2020; the news report of a ministry order dates the fire to 8 June. Later or other deaths were not checked.

**What happened.** During workover of a gas well, the blowout preventer was removed while a cement plug meant as the second barrier was untested. The well became live and blew out. It later caught fire, with damage to surrounding villages, wetland and wildlife.

**Causes** (official investigation):

- Cement plug placed far above the perforated zone and neither tagged nor pressure tested
- BOP removed after 15 h of waiting on cement although the plan required 48 h
- Hydrostatic head fell and the well became active; with the blowout preventer removed and no tested secondary barrier, it flowed and blew out
- Deficient planning, execution discipline and supervision by contractor and operator (committee's stated probable reasons, preliminary)

**Key learnings:**

- Do not nipple down the BOP without a confirmed, tested secondary barrier; do not rely on fluid hydrostatic head alone. *[source]*
- Place the secondary barrier as close to the hydrocarbon zone as practicable. *[source]*
- Critical well operations need proper planning, adherence to procedure and on-site supervision. *[source]*

**Discuss:**

1. What hold points and sign-offs would stop BOP removal before barrier verification?
2. How should a client and a drilling contractor divide supervision of a critical workover step?

**How far the sources go.** Only the interim (first volume) committee report was read, which calls its causes probable. The death count, from a news report, covers the two firefighters; later deaths were not checked.

**Topics:** Well control and offshore barriers, Contractors and interfaces, Leadership and safety culture, Emergency response and evacuation.

**Sources read:**

- [A] [Progress Report (Volume I), Committee of Experts headed by Justice B.P. Katakey, 31 October 2020](https://www.greentribunal.gov.in/sites/default/files/news_updates/Progress%20Report%20Volume%20I%20in%20OA%2043%20of%202020%20(EZ)%20%20and%20OA%2044%20of%202020%20(EZ)%20.pdf), Committee constituted by the National Green Tribunal
- [C] [Oil ministry sets up high level panel to inquire into Assam oil well disaster](https://www.deccanherald.com/india/oil-ministry-sets-up-high-level-panel-to-inquire-into-assam-oil-well-disaster-848640.html), Deccan Herald

### Beirut port ammonium nitrate explosion

`beirut-port-2020` · 2020-08-04 · Port of Beirut, Hangar/Warehouse 12, Lebanon · ports and warehousing · fire, explosion · ammonium nitrate

**Deaths:** 218 (see note). No official figure was read. Human Rights Watch gives 218; the IChemE Loss Prevention Bulletin article gives 207.

**What happened.** A fire broke out in a port warehouse and several minutes later led to explosions, ending in a massive detonation of ammonium nitrate that had been held there for years after being taken off a detained ship. The port and much of the city were badly damaged.

**Causes** (disputed):

- Technical-grade ammonium nitrate kept for years in an unsuitable port warehouse in a single stack
- Fireworks and other combustibles stored in the same warehouse
- Repeated written warnings did not lead to removal of the cargo
- What started the fire is unresolved; welding is one debated theory

**Key learnings:**

- Ports should be developed and prepared to manage hazardous cargo that they are obliged to store but that is not part of their normal planned operations. *[source]*
- An oxidiser stock should be divided and segregated from fireworks, tyres and other fuels or ignition hazards. *[source]*
- A warning letter is not a control. Escalation routes need an authority that can act when the holder of the material cannot. *[compiler]*

**Discuss:**

1. Who in your organisation can force the removal of a hazardous inventory that is held under a legal dispute, and how long may that take?
2. How would you set separation, stack size and siting limits for an oxidiser store next to a populated area?

**Topics:** Storage, quantities and segregation, Land-use planning and neighbours, Emergency response and evacuation, Leadership and safety culture.

**Sources read:**

- [B] [Port of Beirut: lessons from the ammonium nitrate explosion that devastated the peninsula (Loss Prevention Bulletin 284, April 2022)](https://www.icheme.org/media/18192/lpb284_pg02.pdf), IChemE
- [C] ['They Killed Us from the Inside': An Investigation into the August 4 Beirut Blast](https://www.hrw.org/report/2021/08/03/they-killed-us-inside/investigation-august-4-beirut-blast), Human Rights Watch

### Bata explosions at Nkuantoma military barracks

`bata-barracks-2021` · 2021-03-07 · Bata, Equatorial Guinea · explosives and fertiliser · fire, explosion · technical ammonium nitrate (explosives) and military ammunition

**Deaths:** 107 (see note). 107 is the official-records figure quoted in the UN assessment.

**What happened.** A series of explosions hit the Nkuantoma gendarmerie and military barracks in a populated area. The UN assessment found the first and strongest blast was in a container area holding technical ammonium nitrate, which then set off the military arsenal and scattered unexploded ordnance across the city.

**Causes** (not established):

- First and strongest explosion in containers holding technical ammonium nitrate, which propagated to the ammunition depot
- Local residents reported a fire may have started it; the assessment does not establish the initiating cause

**Key learnings:**

- Explosive materials and ammunition stores need separation distances so that one event cannot start the next. *[compiler]*
- Explosives storage next to housing turns a depot accident into a city disaster; siting must be reviewed as settlements grow. *[compiler]*
- Emergency plans for explosives sites must cover scattered unexploded ordnance and public access to debris. *[compiler]*

**Discuss:**

1. What separation and quantity limits would you require between two explosive stores, and how would you verify them over time?
2. How should a regulator oversee hazardous storage held by military or other bodies outside normal industrial permitting?

**How far the sources go.** The source is a UN assessment mission report read from a mirror. The copy read carries a 'BORRADOR' (draft) watermark, and no final version was read.

**Topics:** Storage, quantities and segregation, Land-use planning and neighbours, Facility siting and occupied buildings, Emergency response and evacuation.

**Sources read:**

- [A] [2021 Bata Explosions, Equatorial Guinea: Multi-Cluster/Sector Initial Rapid Assessment (MIRA), 30 March 2021, copy watermarked as a draft (OCHA lists the assessment; copy read is the file hosted by the EE Centre)](https://archive.eecentre.org/eecentre.org/wp-content/uploads/2022/02/MIRA_Equatorial-Guinea_30march2021_eng.pdf), UN OCHA / UNDAC

### BM Container Depot fire and explosions, Sitakunda

`sitakunda-2022` · 2022-06-04 · Sitakunda, Chattogram, Bangladesh · ports and warehousing · fire, explosion · hydrogen peroxide

**Deaths:** 51 (see note). The Business Standard gives 51; Prothom Alo's report on the port authority inquiry gives 49; bdnews24 says around 50. Firefighters were among the dead.

**What happened.** A fire at a private container depot holding hydrogen peroxide consignments among export cargo was followed by explosions while firefighters, who did not know of the chemical, applied water. The fire took days to put out and caused many deaths and injuries among workers, responders and others.

**Causes** (disputed):

- Divisional Commissioner's committee attributes the fire/explosions to hydrogen peroxide and depot mismanagement
- Port authority inquiry cites poor segregation, no hydrants and untrained staff and recommends probing possible sabotage
- Other agencies said the depot lacked permission and other materials may have contributed
- Peroxide containers delayed on site; packaging reported not to meet international standards

**Key learnings:**

- Segregate dangerous goods from other cargo, allow handling only at capable depots and require hydrants and coordination with fire stations. *[source]*
- Review the law and coordination between the many approving agencies for dangerous goods storage. *[source]*
- Depots need an on-site dangerous goods register that responders can read before choosing a firefighting method. *[compiler]*

**Discuss:**

1. What controls should apply when dangerous goods dwell far longer than planned at a logistics site?
2. How should a depot signal oxidiser hazards to arriving firefighters?

**Topics:** Storage, quantities and segregation, Emergency response and evacuation, Reactive and runaway hazards, Hazard identification.

**Sources read:**

- [C] [Sitakunda fire: probes find depot owners liable](https://www.tbsnews.net/node/455690), The Business Standard
- [C] [Investigation committee says chemicals caused BM Depot fire](https://bdnews24.com/bangladesh/investigation-committee-says-chemicals-caused-bm-depot-fire), bdnews24
- [C] [Explosion due to weakness in hazardous material management](https://en.prothomalo.com/bangladesh/explosion-due-to-weakness-in-management-of-hazardous-materials), Prothom Alo

### Pertamina Plumpang fuel terminal fire

`plumpang-2023` · 2023-03-03 · Plumpang, North Jakarta, Indonesia · storage and terminals · fire · fuel (specific product not established in the sources read)

**Deaths:** 33 (see note). Jakarta health agency figure as of 24 March 2023 (Jakarta Post). Early reports gave lower and changing counts (e.g. 17, 20, 23).

**What happened.** A fire started in the evening at the fuel terminal and spread into dense housing that lay very close to the boundary. Residents were killed and evacuation reports range from several hundred to thousands.

**Causes** (not established):

- No final investigation was read
- Early statements: the police chief suggested a possible technical problem while a tank was being filled; Pertamina's chief said an inlet pipe burned and the tanks did not
- Consequences linked to housing encroaching on the buffer area (a newspaper analysis puts the closest homes 28 m from the depot)

**Key learnings:**

- Establish and keep a buffer zone; a geography journal study recommends one extending 100 m from the depot's present outer wall (its abstract words this as a 50-100 m range). *[source]*
- A Parliament research brief calls for prevention to international standards, working detection and firefighting, and regular drills. *[source]*
- A buffer distance should come from consequence analysis and be protected by enforceable land-use control. *[compiler]*

**Discuss:**

1. Is it better to move an existing terminal, move its neighbours or reduce its hazard, and how would you compare them?
2. How would you check whether a fixed 100 m buffer is adequate for this terminal's credible scenarios?

**How far the sources go.** The professional source is a study of buffer zones. The toll and account rest on secondary sources; no final investigation report was read.

**Topics:** Land-use planning and neighbours, Facility siting and occupied buildings, Emergency response and evacuation, Fires and BLEVE.

**Sources read:**

- [C] [Pertamina fuel depot fire death toll rises to 33](https://www.thejakartapost.com/indonesia/2023/03/24/pertamina-fuel-depot-fire-death-toll-rises-to-33), The Jakarta Post
- [C] [17 killed in Plumpang fuel terminal fire](https://www.kompas.id/baca/english/2023/03/04/17-killed-in-plumpang-fuel-terminal-fire), Kompas.id
- [C] [Dirut Pertamina on the source of the Plumpang fire (in Indonesian)](https://www.kompas.tv/bisnis/387976/dirut-pertamina-ungkap-sumber-api-yang-sebabkan-kebakaran-depo-plumpang-bukan-dari-tangki-bbm), Kompas TV
- [C] [Research brief on Pertamina refinery/depot incidents (in Indonesian)](https://repositori.dpr.go.id/id/eprint/683/1/Brief%20Insiden%20Kilang%20Pertamina.%20FINAL.pdf), DPR RI repository
- [B] [Buffer zone study around Plumpang fuel depot](https://jurnal.ugm.ac.id/ijg/article/download/85036/pdf), Indonesian Journal of Geography

| Range name | Unit | Quantity | Hard range (rejected outside) | Soft range (warns outside) | Note |
|---|---|---|---|---|---|
| `temperature_K` | K | absolute temperature | (0, inf) | [50, 3000] |  |
| `temperature_C` | degC | temperature | (-273.15, inf) | [-200, 800] |  |
| `pressure_abs_kPa` | kPa abs | absolute pressure | (0, inf) | [1, 100000] |  |
| `set_pressure_kPag` | kPag | relief or design set pressure (gauge) | (0, inf) | [7, 40000] | API 2000 tanks start near 7 kPag; API 526 valves go to about 40 MPa |
| `back_pressure_kPag` | kPag | total back pressure (gauge) | [0, inf) | (-inf, 5000] |  |
| `design_pressure_barg` | barg | design pressure (gauge) | [0, inf) | (-inf, 1.034] | API 2000 covers up to 1.034 barg |
| `molar_mass_kg_kmol` | kg/kmol | molar mass | (0, inf) | [2, 500] |  |
| `heat_capacity_ratio` | - | Cp/Cv (isentropic exponent) | (1, inf) | (-inf, 1.67] | 1.67 is monatomic; most process gases are 1.1 to 1.4 |
| `compressibility` | - | gas compressibility factor Z | (0, inf) | [0.2, 1.5] |  |
| `density_kg_m3` | kg/m3 | density | (0, inf) | [0.05, 2500] |  |
| `viscosity_cP` | cP | dynamic viscosity | (0, inf) | [0.005, 10000] |  |
| `latent_heat_kJ_kg` | kJ/kg | latent heat of vaporisation | (0, inf) | [50, 2500] |  |
| `heat_of_combustion_kJ_kg` | kJ/kg | heat of combustion | (0, inf) | [1000, 150000] |  |
| `heat_of_combustion_MJ_kg` | MJ/kg | heat of combustion | (0, inf) | [1, 150] |  |
| `specific_heat_kJ_kgK` | kJ/kg/K | specific heat | (0, inf) | [0.5, 10] |  |
| `length_m` | m | length or diameter | (0, inf) | (-inf, 2000] |  |
| `nonneg_length_m` | m | length that may be zero (elevation, release height, liquid level) | [0, inf) | (-inf, 200] |  |
| `area_m2` | m2 | area | (0, inf) | [0.1, 100000] |  |
| `area_mm2` | mm2 | orifice or vent area | [0, inf) | (-inf, 1e+06] |  |
| `volume_m3` | m3 | volume or capacity | (0, inf) | [0.001, 500000] |  |
| `flow_m3_h` | m3/h | volumetric flow | [0, inf) | (-inf, 100000] |  |
| `mass_flow_kg_h` | kg/h | mass flow | (0, inf) | (-inf, 5e+06] |  |
| `mass_flow_kg_s` | kg/s | mass flow | (0, inf) | (-inf, 10000] |  |
| `release_rate_g_s` | g/s | release rate | (0, inf) | (-inf, 1e+07] |  |
| `mass_kg` | kg | mass | (0, inf) | (-inf, 1e+10] |  |
| `wall_mm` | mm | wall thickness | (0, inf) | [1, 100] |  |
| `wind_speed_m_s` | m/s | wind speed at release height | (0, inf) | [0.5, 25] |  |
| `concentration_ppm` | ppm | concentration | (0, inf) | [0.01, 1e+06] |  |
| `time_s` | s | time or duration | (0, inf) | (-inf, 86400] |  |
| `time_nonneg_s` | s | time that may be zero | [0, inf) | (-inf, 86400] |  |
| `time_min` | min | time | (0, inf) | (-inf, 1440] |  |
| `fraction_0_1` | - | fraction or efficiency | [0, 1] | - |  |
| `coefficient_0_1` | - | coefficient in (0, 1] (discharge, back-pressure, combination, superheat) | (0, 1] | [0.5, inf) |  |
| `environment_factor` | - | fire environment factor F | (0, 1] | [0.03, inf) |  |
| `pfd` | - | probability of failure on demand | (0, 1] | - |  |
| `beta_factor` | - | common-cause beta factor | [0, 1] | (-inf, 0.2] |  |
| `frequency_per_yr` | 1/yr | event frequency | (0, inf) | [1e-09, 100] |  |
| `failure_rate_per_h` | 1/h | dangerous undetected failure rate | (0, inf) | [1e-10, 0.0001] |  |
| `proof_test_years` | yr | proof-test interval | (0, inf) | [0.01, 20] |  |
| `multiplier_positive` | - | positive multiplier | (0, inf) | - |  |
| `voltage_kV` | kV | line-to-line voltage | (0, inf) | [0.1, 800] |  |
| `current_kA` | kA | fault current | (0, inf) | [0.5, 106] |  |
| `current_A` | A | current | (0, inf) | (-inf, 200000] |  |
| `distance_mm` | mm | working distance or detection capability | (0, inf) | [6, 3000] |  |
| `relay_tms` | - | time multiplier setting | (0, inf) | [0.025, 1.5] |  |
| `resistivity_ohm_m` | ohm m | resistivity | (0, inf) | [1, 10000] |  |
| `sound_level_dBA` | dBA | sound level | [0, inf) | [40, 140] |  |
| `exposure_hours` | h | exposure time | (0, 24] | - |  |
| `smys_MPa` | MPa | specified minimum yield strength | (0, inf) | [100, 900] |  |
| `section_factor_1_m` | 1/m | steel section factor Am/V | (0, inf) | [10, 500] |  |
| `diameter_mm` | mm | pipe outside diameter | (0, inf) | [10, 2000] |  |
| `heat_flux_kW_m2` | kW/m2 | absorbed heat flux | (0, inf) | [10, 400] |  |
| `power_kW` | kW | power | (0, inf) | (-inf, 1e+07] |  |
| `temperature_rise_K` | K | temperature rise | (0, inf) | [1, 50] |  |
| `omega_parameter` | - | omega compressibility parameter of a two-phase / flashing fluid | (0, inf) | [0.1, 500] |  |
| `emissive_power_kW_m2` | kW/m2 | flame surface emissive power (SEP) | (0, inf) | [20, 400] |  |
| `fuel_consumption_g_kWh` | g/kWh | specific fuel consumption (vendor data) | (0, inf) | [150, 350] |  |
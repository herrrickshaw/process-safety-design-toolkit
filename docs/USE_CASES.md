# Use cases

Worked scenarios, each run with real commands. Every command below is executed by the test suite (exit status 0), and the
numbers are copied from a run of `python scripts/gen_use_cases.py --write` (4 significant figures, selected fields shown).
These are screening results: read the limit in each takeaway, and see `docs/VALIDATION.md` for what was cross-checked.

## Refinery or gas plant: fire on a gas-filled drum

*Sector: oil and gas, refining.*

A 15 m3 drum holds gas at 1000 kPag with a PSV set at 1500 kPag. You need a PSV for the fire case and want to know if the valve alone keeps the vessel intact.

**Size the PSV for a fire on a gas-filled drum**

```bash
python3 -m process_safety relief-gas --W 12000 --T 400 --set-g 1500 --case fire --M 44 --k 1.13 --Z 0.9
```

```json
{
  "required_area_mm2": 733.3,
  "orifice": "J",
  "regime": "critical"
}
```

**Does that PSV protect a 20 mm wall vessel in a pool fire?**

```bash
python3 -m process_safety vapour-fire --volume 15 --area 36 --D 2 --wall-mm 20 --M 20 --k 1.3 --p0-g 1000 --psv-area 830 --psv-set-g 1500
```

```json
{
  "t_relief_onset_s": 319.0,
  "t_rupture_s": 700.0,
  "peak_pressure_kpag": 1503.0,
  "protected": false
}
```

**Add a blowdown valve opening at 60 s**

```bash
python3 -m process_safety vapour-fire --volume 15 --area 36 --D 2 --wall-mm 20 --M 20 --k 1.3 --p0-g 1000 --psv-area 830 --psv-set-g 1500 --bdv-area 800 --bdv-open-s 60
```

```json
{
  "t_rupture_s": null,
  "protected": true
}
```

**Takeaway.** The fire-case valve at 1500 kPag set pressure is a J orifice (733 mm2 required, 830 mm2 installed), yet the vessel still ruptures at 700 s because the wall weakens while the valve holds pressure at about 1503 kPag. Opening a blowdown valve at 60 s avoids rupture in the hour simulated. The lesson is the one API 521 draws: sizing the valve is not the same as protecting the vessel. Flux, film coefficient and strength curve are assumptions listed in `vapour_fire.py`.

## LPG or light-hydrocarbon bullet: flashing relief

*Sector: LPG, petrochemicals, terminals.*

A propane bullet relieves a liquid that flashes as pressure falls. Gas-only or liquid-only sizing would be wrong; the omega method sizes the two-phase case.

**Vapour pressure and fill limit of a propane bullet**

```bash
python3 -m process_safety lpg propane --fill-C 15 --max-C 50
```

```json
{
  "vapour_pressure_kPag_at_max": 1616.0,
  "max_fill_fraction_thermodynamic_ceiling": 0.8842
}
```

**Two-phase relief area at omega 2 (mostly liquid-like)**

```bash
python3 -m process_safety twophase --P0 1900 --rho0 450 --omega 2 --W 8 --Kd 0.85
```

```json
{
  "G_kg_m2_s": 14320.0,
  "eta_critical": 0.6925,
  "required_area_mm2": 657.3
}
```

**Same case at omega 6**

```bash
python3 -m process_safety twophase --P0 1900 --rho0 450 --omega 6 --W 8 --Kd 0.85
```

```json
{
  "G_kg_m2_s": 9631.0,
  "eta_critical": 0.8068,
  "required_area_mm2": 977.3
}
```

**Same case at omega 20 (strongly flashing)**

```bash
python3 -m process_safety twophase --P0 1900 --rho0 450 --omega 20 --W 8 --Kd 0.85
```

```json
{
  "G_kg_m2_s": 5844.0,
  "eta_critical": 0.8938,
  "required_area_mm2": 1611.0
}
```

**Takeaway.** For the same 8 kg/s relief rate and the same Kd of 0.85, the required area is 657 mm2 at omega 2, 977 mm2 at omega 6 and 1611 mm2 at omega 20: more flashing needs more area, a factor 2.5 across this range. Omega is an input here (the illustrative values 2, 6 and 20 are not propane properties): take it from your property package, and treat the area as a screening value until it is checked against API 520 Annex C and the valve vendor.

## Terminal siting: how far is far enough from a pool fire

*Sector: tank farms, LNG and LPG terminals.*

A 20 m diameter bunded pool fire is credible. You want radiation at a boundary or a neighbouring unit, close in and far out.

**Burn rate, SEP and distances for a 20 m diameter pool**

```bash
python3 -m process_safety pool-fire --area 314 --hc 44000 --hv 350 --cp 2.2 --tb 400
```

```json
{
  "diameter_m": 19.99,
  "flame_height_m": 31.35,
  "heat_release_MW": 1059.0,
  "sep_mudan_croce_kW_m2": 30.89,
  "distance_m": {
    "37.5": 17.8,
    "12.5": 37.9,
    "4.73": 64.9,
    "1.58": 114.4
  }
}
```

**Near-field flux at 15 m from the flame face (solid flame)**

```bash
python3 -m process_safety flame-flux --width 20 --height 31 --distance 15 --sep 30.9 --tau 0.8
```

```json
{
  "view_factor": 0.2653,
  "incident_kW_m2": 6.559
}
```

**Same at 40 m**

```bash
python3 -m process_safety flame-flux --width 20 --height 31 --distance 40 --sep 30.9 --tau 0.8
```

```json
{
  "view_factor": 0.08781,
  "incident_kW_m2": 2.171
}
```

**LNG tank impoundment and boil-off for the same site**

```bash
python3 -m process_safety lng --tanks 160000 --heat-kw 100 --regas-kg-s 100
```

```json
{
  "impoundment_m3": 176000.0,
  "basis": "49 CFR 193.2181",
  "boil_off_kg_s": 0.1961,
  "boil_off_pct_per_day_largest_tank": 0.02509,
  "regas_duty_MW": 88.73,
  "seawater_m3_s_open_rack": 4.339
}
```

**Takeaway.** The solid-flame view factor falls from 0.265 at 15 m to 0.088 at 40 m, giving 6.6 and 2.2 kW/m2. The point-source model in `pool-fire` gives a very different answer (12.5 kW/m2 at 37.9 m from the pool centre) because it radiates 25% of the heat release, while the Mudan-Croce SEP of 30.9 kW/m2 implies about 6% (SEP x flame side area is about 61 MW of 1059 MW). The two models disagree by a factor of about four in the far field. Neither is validated against a test here: run both, report both, and use the conservative one for siting until an engineer chooses.

## Functional safety: from LOPA to a proof-test interval

*Sector: all process industries.*

A scenario with initiating frequency 0.1/yr and two protection layers must reach 1e-6/yr.

**How much risk reduction does the scenario need (LOPA)?**

```bash
python3 -m process_safety lopa --ie 0.1 --ipl 0.1 0.01 --target 1e-6
```

```json
{
  "required_rrf": 100.0,
  "sil_needed": "SIL 1"
}
```

**Can a 1oo2 pair deliver it with a yearly proof test?**

```bash
python3 -m process_safety pfd --arch 1oo2 --lambda-du 2e-6 --ti-years 1 --beta 0.05
```

```json
{
  "pfd_avg": 0.0005303,
  "rrf": 1886.0,
  "achieves": "SIL 3"
}
```

**What if the proof test slips to every 3 years?**

```bash
python3 -m process_safety pfd --arch 1oo2 --lambda-du 2e-6 --ti-years 3 --beta 0.05
```

```json
{
  "pfd_avg": 0.002145,
  "rrf": 466.2,
  "achieves": "SIL 2"
}
```

**Takeaway.** LOPA asks for a risk reduction factor of 100 (SIL 1). A 1oo2 pair with a dangerous undetected rate of 2e-6/h and a 5% common-cause factor reaches PFDavg 5.3e-4 with a yearly proof test (SIL 3 band) and 2.1e-3 with a three-yearly one (SIL 2 band). Stretching the test interval cost one SIL band. Architectural constraints (HFT/SFF) are in `sil_lifecycle`, not in this command.

## Regulatory screen for a new chlorine installation

*Sector: chemicals, water treatment, pharma.*

Before design you want to know which regimes a chlorine and hydrogen sulphide inventory falls under.

**Seveso tier for a chlorine and H2S inventory**

```bash
python3 -m process_safety seveso Chlorine:H=6 'Hydrogen sulphide:H=3'
```

```json
{
  "tier": "lower-tier",
  "sums": {
    "H": {
      "lower": 1.2,
      "upper": 0.39
    }
  },
  "note": "Seveso III Annex I, 2012 text; MSIHC 1989 schedules not reproduced"
}
```

**OSHA PSM applicability for 700 kg chlorine**

```bash
python3 -m process_safety psm-check --chemical chlorine --kg 700
```

```json
{
  "found": true,
  "chemical": "Chlorine",
  "cas": "7782-50-5",
  "threshold_lb": 1500,
  "threshold_kg": 680.4,
  "quantity_kg": 700.0,
  "covered": true
}
```

**EPA RMP threshold for 1,200 kg chlorine**

```bash
python3 -m process_safety rmp-check chlorine --kg 1200
```

```json
{
  "found": true,
  "name": "Chlorine",
  "kind": "toxic",
  "threshold_lb": 2500,
  "threshold_kg": 1134.0,
  "quantity_counted_kg": 1200.0,
  "covered": true
}
```

**Next due dates for PSM obligations**

```bash
python3 -m process_safety psm-due --pha 2021-03-15 --audit 2023-06-01 --today 2026-11-03
```

```json
{
  "pha_revalidation": {
    "last": "2021-03-15",
    "next_due": "2026-03-15",
    "days_remaining": -233,
    "status": "overdue"
  },
  "compliance_audit": {
    "last": "2023-06-01",
    "next_due": "2026-06-01",
    "days_remaining": -155,
    "status": "overdue"
  }
}
```

**Takeaway.** Seveso III lower tier; OSHA PSM covered (700 kg against a 680.4 kg threshold); EPA RMP covered (1200 kg against 1134 kg); and the sample PHA and audit dates are already overdue on 2026-11-03. These are applicability screens from the rule text; Indian MSIHC schedules are not reproduced, so an Indian site needs them checked separately.

## Electrical: arc flash, relay time, earthing

*Sector: power, utilities, process plant.*

A 480 V board with 20 kA available needs a first-pass incident energy, a relay time and tolerable earthing voltages.

**Arc flash at a 480 V, 20 kA board**

```bash
python3 -m process_safety arc-flash --kv 0.48 --ka 20 --t 0.2 --dist-mm 455
```

```json
{
  "applicability": {
    "ok": true,
    "conditional": false,
    "why": "open-air three-phase"
  },
  "incident_energy_J_cm2": 19.87,
  "incident_energy_cal_cm2": 4.748,
  "boundary_mm_second_degree_burn": 905.1,
  "note": "screening; arc-flash study per IEEE 1584 for enclosed equipment"
}
```

**Relay operating time at 10 times pickup**

```bash
python3 -m process_safety idmt --i 2000 --pickup 200 --tms 0.3
```

```json
{
  "operating_time_s": 0.8912,
  "multiple_of_pickup": 10.0
}
```

**Tolerable touch and step voltage on a crushed-rock surface**

```bash
python3 -m process_safety earthing --rho-s 3000 --t 0.5 --rho 75 --hs 0.2
```

```json
{
  "Cs": 0.8209,
  "touch_V_50kg": 770.1,
  "step_V_50kg": 2588.0,
  "touch_V_70kg": 1042.0,
  "step_V_70kg": 3503.0
}
```

**Takeaway.** Open-air Lee method gives 4.75 cal/cm2 at 455 mm and a 905 mm boundary; the applicability check passes only for open-air three-phase, so enclosed gear needs IEEE 1584 (not implemented). The relay curve gives 0.89 s at ten times pickup. Tolerable touch voltage for a 50 kg person is 770 V on the 3000 ohm m surface layer.

## Data centre: supporting-system sizing

*Sector: data centres, GCC infrastructure.*

A 10 MW IT hall with 13 MW facility load needs first-pass cooling water, battery and diesel numbers.

**Cooling water, UPS battery and diesel for a 10 MW IT load**

```bash
python3 -m process_safety datacentre --it-kw 10000 --facility-kw 13000 --delta-t 8 --autonomy-min 10 --gen-hours 48 --sfc 210
```

```json
{
  "it_kw": 10000.0,
  "pue": 1.3,
  "cooling_water_m3_h": 1077.0,
  "battery_nameplate_kwh": 2193.0,
  "diesel_m3": 156.0
}
```

**Takeaway.** PUE 1.3, cooling water 1077 m3/h at 8 K rise, 2193 kWh nameplate battery for 10 minutes, 156 m3 diesel for 48 hours at the supplied fuel consumption (a vendor value, never defaulted). No tier or ASHRAE value is coded; see `docs/DATACENTRE.md`.

## Occupational: noise and machine guarding

*Sector: any workplace.*

A worker spends a shift at mixed noise levels, and a light curtain must stop a machine safely.

**Daily noise dose for a mixed shift**

```bash
python3 -m process_safety noise 95:2 90:4 100:0.5
```

```json
{
  "dose_pct": 125.0,
  "twa_dBA": 91.61,
  "exceeds_pel": true,
  "above_action_level": true,
  "basis": "OSHA 1910.95 Table G-16 / App. A"
}
```

**Minimum distance for a light curtain with a 0.2 s stop time**

```bash
python3 -m process_safety safeguard --stop-s 0.2 --d-mm 30
```

```json
{
  "min_distance_mm": 500,
  "note": "pre-2024 ISO 13855 form; confirm the edition your project cites"
}
```

**Takeaway.** Dose 125% and TWA 91.6 dBA exceed the OSHA permissible level; the minimum light-curtain distance for a 0.2 s stop time is 500 mm (pre-2024 ISO 13855 form, so confirm the edition).

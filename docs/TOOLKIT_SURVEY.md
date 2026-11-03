# Other toolkits found (2026-11-03)

Found by web search; NOT evaluated or run unless stated. Use them as independent cross-checks.

| Tool | What it covers | Notes |
|---|---|---|
| [`fluids` (Caleb Bell)](https://fluids.readthedocs.io/fluids.safety_valve.html) | `safety_valve`: API 520 gas/vapour, steam, subcritical liquid sizing, API 526 rounding; `separator`: Souders-Brown K (Watkins, York demister) | best cross-check for `relief` and `separator`; search found no API 521 fire-case function. Suggested test: `pip install fluids`, compare areas |
| [`fluids.separator`](https://fluids.readthedocs.io/fluids.separator.html) | vapour-liquid separator K-factors | see above |
| [DeepSafety (PyPI)](https://pypi.org/project/deepsafety/1.0.0/) | claims relief selection/sizing (liquid, gas, two-phase, external fire, thermal expansion), source models, HAZOP/FMEA/What-If | claims unverified; licence/repo not confirmed |
| [jendakolda/API_Calc](https://github.com/jendakolda/API_Calc) | PSV sizing per API RP 520 | scope unverified |
| [Open PHA (Kenexis)](https://kenexis.com/wp-content/uploads/2020/02/Open-PHA-brochure.pdf) | HAZOP/LOPA worksheets | free + premium tiers; not an open calculation library |
| [GitHub topic: vessel-sizing](https://www.github.com/topics/vessel-sizing) | assorted vessel/line sizing repos | unvetted |
| [Engineers Edge API separator Excel](https://www.engineersedge.com/excel_calculators/Fluids_Engineering/api_separator_sizing_15535.htm) | spreadsheet separator sizing | unvetted |
| DNV Phast/Safeti, DNV Maros, PHA-Pro (commercial) | QRA, RAM, HAZOP worksheets | the tools shown in the consultancy brochure; consequence modelling is out of scope here |

No open-source flare-radiation (API 521 point source) repository was found by search.

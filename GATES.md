# Gates: units, input templates, official scenarios and coverage completion

OWNS: process_safety/units.py, process_safety/egress.py, process_safety/illumination.py, process_safety/cli/**, process_safety/__main__.py, scripts/**, tests/**, docs/**, templates/**, CHANGELOG.md, README.md

Scope: SI and US-customary input handling with a template and a run command, a documented scenario suite run in both unit systems with an official report, and every coverage topic either exercised by a scenario or listed as an explicit gap.

- [x] G1: unit factors equal the exact legal definitions (inch, pound, gallon, psi, BTU, foot) and temperature conversions round-trip
  CHECK: python3 scripts/verify_deliverables.py units-exact
  EXPECT: PASS units-exact
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=2b3e90757a75bbee7460f6629ee9a135eab2c7af459f7fcc5a8d4aaa3f96aa12; output-bytes=17

- [x] G2: gauge and absolute pressure are never mixed (psig converts to kPag, psia to kPa abs, and the conversion between them uses 101.325 kPa)
  CHECK: python3 scripts/verify_deliverables.py gauge-absolute
  EXPECT: PASS gauge-absolute
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=f78d06e35d7a8078f8a02078455acdc3e1efc04a5215705e6bde9a26d686d13f; output-bytes=20

- [x] G3: every float argument of every CLI command has a declared dimension (or is declared dimensionless), none is silently skipped
  CHECK: python3 scripts/verify_deliverables.py all-args-dimensioned
  EXPECT: PASS all-args-dimensioned
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=cfd81bf328b8b03525b6ea313b17476a99544451f4ead2558484ab14b32e55a7; output-bytes=26

- [x] G4: running a command with --units us on US-converted inputs gives the same result as SI inputs, for every scenario in the suite (max relative difference reported)
  CHECK: python3 scripts/verify_deliverables.py si-us-equivalence
  EXPECT: PASS si-us-equivalence
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=918bb31e43e94335192320bfb1205fa1b370cd77fb291f72c2525230d775c701; output-bytes=114

- [x] G5: the template command lists every argument of every command in both unit systems, and the run command executes a filled template to the same output as the direct CLI
  CHECK: python3 scripts/verify_deliverables.py templates-run
  EXPECT: PASS templates-run
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=a8a4e22284564bb1e5dc9b7e827757a309084c6fbdb9a592566e53d44a61366d; output-bytes=19

- [x] G6: generated input-template docs and CSV are in sync with the code
  CHECK: python3 scripts/verify_deliverables.py templates-sync
  EXPECT: PASS templates-sync
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=93694cd200cc68f753e0b55445874f299611e1e6aed97e80ee39baa51fda7fce; output-bytes=20

- [x] G7: docs/UNITS.md covers every quantity in the unit table, the gauge/absolute rule, and the named metric-versus-US traps
  CHECK: python3 scripts/verify_deliverables.py units-doc
  EXPECT: PASS units-doc
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=d9662d8152c4507f0b9299d942e14a6b09b60c7a66850e7ce648288a1fb49c07; output-bytes=15

- [x] G8: the scenario suite has at least one scenario for every CLI command and for every JSON tool, with at least 60 scenarios, and every scenario passes
  CHECK: python3 scripts/run_scenarios.py --check && python3 scripts/verify_deliverables.py scenario-coverage
  EXPECT: /SCENARIOS PASS[\s\S]*PASS scenario-coverage/
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=dce39bbba55fbf5ebfff3e4412ae3c6e9d6b2131adf683bea88987a29c098e42; output-bytes=88

- [x] G9: the suite contains metamorphic checks (scaling, monotonic, conservation) on at least 25 scenarios, and these are evaluated, not skipped
  CHECK: python3 scripts/verify_deliverables.py metamorphic-count
  EXPECT: PASS metamorphic-count
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=cab61b60287ccfdc32477fa433638bfe52b84020c845bb0df868aad43b2816ea; output-bytes=80

- [x] G10: negative control, a deliberately wrong expectation makes the runner fail (so a pass means something)
  CHECK: python3 scripts/verify_deliverables.py negative-control
  EXPECT: PASS negative-control
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=071123dd3b42a05e44f9669da05def19ab6a80fb383e9579985c0410f65e2e1a; output-bytes=22

- [x] G11: every coverage topic maps to scenario ids or to a named gap with a reason, and the gap list equals the topics whose coverage status says not implemented
  CHECK: python3 scripts/verify_deliverables.py coverage-map
  EXPECT: PASS coverage-map
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=9e15dfb2139483be933566e8132ad1226f9237b436163464b64408edf5ae2a8f; output-bytes=62

- [x] G12: the official scenario report is generated, in sync, and lists scenario id, topic, checks, SI/US difference and verdict
  CHECK: python3 scripts/verify_deliverables.py report-sync
  EXPECT: PASS report-sync
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=15b43b68aa7d3445595688b7ee671cb5bb40bd28ebc72894f875abe6d2d1092d; output-bytes=17

- [x] G13: full test suite passes with at least 342 tests plus the new ones
  CHECK: python3 scripts/verify_deliverables.py full-suite
  EXPECT: PASS full-suite
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=bddb4c6ba27d63bc1ab0471e4742b1d833344b1ef8ff0285379b5f0f02ce299b; output-bytes=29

- [x] G14: lint clean (ruff selection from CI) and no new import outside the standard library in process_safety
  CHECK: python3 scripts/verify_deliverables.py lint-stdlib
  EXPECT: PASS lint-stdlib
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=2ccf202c6e6734521b1d56ddc7e559ccaab533707187d590bf72d326a41f3a7a; output-bytes=17

- [x] G15: CHANGELOG records the decisions including rejected alternatives, and README and CONTRIBUTING mention the new commands
  CHECK: python3 scripts/verify_deliverables.py docs-updated
  EXPECT: PASS docs-updated
  EVIDENCE: exit=0; shell=/bin/sh; cwd=/Users/umashankar/repos/process-safety-design-toolkit; path=3ee9235cc917/24 entries; EXPECT=matched; output-sha256=4b642dc5561e0ee18feb44bd90152b09272445433e2e269278c76511405bc037; output-bytes=18

- [ ] G16: reviewer reads docs/UNITS.md and the report once and confirms no remembered standard value was typed into code, only definitions and inputs
  EVIDENCE: pending

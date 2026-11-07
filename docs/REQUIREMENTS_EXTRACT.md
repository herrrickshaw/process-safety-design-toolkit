# Extracting "shall" requirements from design practices and standards (locally)

Company design and engineering practices, client specifications and bought standards state what a project **shall** and **should** do. A gap analysis of the design against them is a normal project deliverable, and the requirements that matter most for safety are the ones that overlap the recommendations safety studies raise (relief, isolation, detection, independence of trips, and so on). `python -m process_safety requirements` pulls those statements out of documents you hold, classifies them against the toolkit's recommendation catalogue, and compares them with your PHA register.

## What it deliberately does not do
* **No proprietary text ships with the toolkit, and none should be committed.** Company practices and bought standards are the owner's intellectual property. The command writes statements only to the CSV you name, and **refuses a path inside a git repository unless git ignores it** (`requirements_out/`, `private_*` and `*.private.csv` are ignored by default). The screen shows counts, not statement text, unless you ask with `--show N`.
* It is not a requirements management tool: it finds sentences with modal verbs, so it misses requirements written in tables or without "shall", and it includes sentences that merely quote a requirement. Treat the output as a worklist to review.

## Use
```bash
python3 -m process_safety requirements "my_practice.docx" "my_spec.txt" --out requirements_out/my_requirements.csv --register my_phA_register.csv
```
Readers: `.txt`, `.md`, `.csv`, `.docx` (standard library) and `.pdf` through `pdftotext` when it is installed (otherwise convert first).

Output columns: file, clause, modality (mandatory / recommended / prohibition), the catalogue type(s) it matches, the cost scope that type maps to, and the statement. Console summary: statements per modality, per file and per recommendation type, and, with `--register`, the requirement types your register never mentions.

## A test on public documents
Run on four public LNG documents (a regulator's code of practice, an international lender's EHS guideline draft, a design-considerations paper and a US fuel-transfer regulation): 1,943 normative statements (1,627 mandatory, 174 recommended, 142 prohibitions); 1,622 of them (83%) matched no catalogue type, because the catalogue covers relief, protective instrumentation, isolation, detection and similar safety topics, not every requirement in a regulation (marking, training frequencies, cylinder manufacture). A hand check of 14 matched statements found about two thirds sensible; the rest were false matches, and two causes were fixed (short keywords such as "sil" matched inside other words, and "capacity" and "insulation" were too generic). Expect to review the output.

## Finding documents: index a Zotero library
If your reference library is in Zotero, `scripts/zotero_index.py` builds a CSV of every attachment (title, file name, type, collections, tags) from a copy of `zotero.sqlite`, and can resolve files that were later moved by matching names in the folders you give it:
```bash
python3 scripts/zotero_index.py ~/path/Zotero/zotero.sqlite /Users/Shared/private_dep_work/out/zotero_index.csv --storage ~/path/Zotero/storage --also-search ~/path/folder1 ~/path/folder2
```
In one 32,000-attachment library it located 99% of the files this way. The index holds titles and file names that may be personal: keep it outside any repository.

## Where this fits in a project
| Project document | What it holds | Toolkit link |
|---|---|---|
| Process flow scheme and HMB | the process and its cases | `tool plant` (streams, units) |
| Process engineering flow scheme | devices, instruments, isolation | `tool plant` (registers, Proteus XML) |
| Process safeguarding memorandum | the safeguards relied on for each hazard and why | the rationale table of `tool plant`, `docs/PLANT_INGEST.md` |
| Process control narrative | how control and shutdown functions operate | `tool workflow` (sensors, PCN scope) |
| Standards gap analysis | where the design departs from the practice | `requirements`, `standards` (coverage map), OISD list |
| HAZOP / LOPA register | deviations, safeguards, recommendations | `tool plant` (register analysis) |

## Public documents of the same kind (free to read)
* [DOE-STD-1189-2016, Integration of Safety into the Design Process](https://www.standards.doe.gov/standards-documents/1100/1189-astd-2016): requirements and guidance for integrating safety into project design, with a safety design strategy; written for nuclear facilities, but the staged approach transfers. A public document, so it is safe to run the extractor on and to publish the result.
* [IOGP JIP33 specifications](https://www.iogp.org/bookstore/product-category/jip33/instruments/): free equipment and materials specifications with "shall" requirements (for example for pressure relief valves and control valves).
* OSHA 29 CFR 1910.119 and 49 CFR 192/193 (public regulations): the toolkit already encodes their mandatory elements in `psm`, `pipeline` and `lng`.
See `docs/LITERATURE.md`. These were not read for this page.

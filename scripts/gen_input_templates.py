"""Write the input-template files from the command definitions (python scripts/gen_input_templates.py --write).

    docs/INPUT_TEMPLATES.md          every command, every argument, SI and US units, ranges, defaults
    templates/inputs_all.csv         the same as one spreadsheet-ready table
    templates/inputs/<cmd>.<si|us>.json   a fill-in file per command and unit system (run with `process_safety run`)

Without --write it only checks that the files on disk match what the code would write (exit 1 if stale).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from process_safety import templating  # noqa: E402
from process_safety.cli import REGISTRY  # noqa: E402


def expected() -> dict[str, str]:
    files = {"docs/INPUT_TEMPLATES.md": templating.markdown_all(), "templates/inputs_all.csv": templating.csv_all()}
    for name in REGISTRY:
        for system in ("si", "us"):
            files[f"templates/inputs/{name}.{system}.json"] = templating.dump(templating.template(name, system))
    return files


def main(argv):
    files = expected()
    stale = []
    for rel, text in files.items():
        path = os.path.join(ROOT, rel)
        if "--write" in argv:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        elif not os.path.exists(path) or open(path, encoding="utf-8").read() != text:
            stale.append(rel)
    extra = []
    d = os.path.join(ROOT, "templates", "inputs")
    if os.path.isdir(d):
        extra = [f for f in os.listdir(d) if f"templates/inputs/{f}" not in files]
    if "--write" in argv:
        for f in extra:
            os.remove(os.path.join(d, f))
        print(f"wrote {len(files)} files")
        return 0
    if stale or extra:
        print("stale or extra: " + ", ".join(stale + extra[:5]) + "  (run: python scripts/gen_input_templates.py --write)")
        return 1
    print("input templates in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

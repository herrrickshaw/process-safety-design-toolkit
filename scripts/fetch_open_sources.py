"""Download the open-access PDFs listed in docs/literature_manifest.csv into a folder OUTSIDE the repository (licensed or third-party text must not be committed).

Dry run by default (prints what would be fetched). Pass --confirm to download. Polite: one request per second, browser User-Agent, no retries against a
bot challenge (a 403, 418, 202, 999 or an HTML reply is logged and skipped, never bypassed). Only rows whose access starts with 'free', whose URL ends in .pdf
and whose recorded check was a 200 PDF are fetched. A log with SHA-256 of every file is written next to the files.
Usage: python3 scripts/fetch_open_sources.py --out ~/sources            (dry run)
       python3 scripts/fetch_open_sources.py --out ~/sources --confirm
Standard library only."""
import argparse
import csv
import hashlib
import os
import time
import urllib.request

MANIFEST = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "docs", "literature_manifest.csv")
UA = "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def selectable(row: dict) -> bool:
    return (row["access"].lower().startswith("free") and row["url"].lower().split("?")[0].endswith(".pdf")
            and row["http_check_2026-11-10"].startswith("200 PDF") and row["read_status"].lower() != "read")


def load(path: str = MANIFEST) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--confirm", action="store_true")
    a = ap.parse_args()
    rows = [r for r in load() if selectable(r)]
    print("%d open PDFs selected (%s)" % (len(rows), "downloading" if a.confirm else "dry run"))
    if a.confirm:
        os.makedirs(a.out, exist_ok=True)
    log = []
    for r in rows:
        print("  %-18s %s" % (r["id"], r["url"]))
        if not a.confirm:
            continue
        req = urllib.request.Request(r["url"], headers={"User-Agent": UA})
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = resp.read()
                if not data.startswith(b"%PDF"):
                    log.append((r["id"], "skipped: not a PDF (bot challenge?)", "", len(data)))
                    continue
        except Exception as e:  # logged and skipped; never bypassed
            log.append((r["id"], "failed: %s" % e, "", 0))
            continue
        path = os.path.join(a.out, r["id"] + ".pdf")
        with open(path, "wb") as fh:
            fh.write(data)
        log.append((r["id"], "ok", hashlib.sha256(data).hexdigest(), len(data)))
        time.sleep(1.0)
    if a.confirm:
        with open(os.path.join(a.out, "fetch_log.csv"), "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh); w.writerow(["id", "result", "sha256", "bytes"]); w.writerows(log)


if __name__ == "__main__":
    main()

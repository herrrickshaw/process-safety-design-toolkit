"""Checks on the country table.

  shape   exactly the 193 UN members and 2 observers
  slots   every state has every slot dispositioned as found or not-found (fails while anything is not-searched)
  structure  every slot has a well-formed status, not-searched allowed
  floors  research floors, fixed before the research was run
  links   every found link has a check result and none is 'missing'
  fetch   request the unchecked links (robots.txt honoured, one at a time per host) and record the result
  prune   turn links that came back 'missing' into not-found, saying so in the note
Standard library plus the curl command (fetch only).
"""
import concurrent.futures
import json
import os
import sys
from urllib.parse import urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from process_safety import country_coverage as cc  # noqa: E402

DATA = os.path.join(os.path.dirname(HERE), "process_safety", "data", "country_safety.json")
FLOORS = {"osh_law": 170, "standards_body": 150, "total": 820}


def found(data):
    return [(iso, slot, v) for iso, row in data["countries"].items() for slot, v in row.items() if v["status"] == "found"]


def fail(msg: str) -> None:
    print("FAIL", msg)
    raise SystemExit(1)


def main() -> None:
    cmd = sys.argv[1]
    with open(DATA, encoding="utf-8") as fh:
        data = json.load(fh)
    table, states = data["countries"], cc.states()
    if cmd == "shape":
        codes = [s["iso3"] for s in states]
        n_obs = sum(1 for s in states if s["status"] == "observer")
        if len(set(codes)) != len(codes) or len(codes) != 195 or n_obs != 2 or set(codes) != set(table):
            fail(f"shape: states={len(codes)} observers={n_obs} table={len(table)}")
        print(f"PASS shape states={len(table)}")
    elif cmd in ("slots", "structure"):
        bad, pending = [], 0
        for iso, row in table.items():
            if set(row) != set(cc.SLOTS):
                bad.append((iso, "slot names"))
                continue
            for slot, v in row.items():
                if v["status"] == "found":
                    if not (v.get("name") and v.get("url", "").startswith("http") and v.get("source") in ("official", "secondary")):
                        bad.append((iso, slot))
                elif v["status"] == "not-searched":
                    pending += 1
                elif v["status"] != "not-found":
                    bad.append((iso, slot))
        if bad:
            fail(f"slots blank={len(bad)} {bad[:10]}")
        if cmd == "structure":  # repository invariant: every slot carries a known status
            print(f"PASS structure not-searched={pending}")
            return
        if pending:
            fail(f"slots not-searched={pending} (never researched, so not dispositioned)")
        print("PASS slots blank=0")
    elif cmd == "floors":
        per = {s: sum(1 for r in table.values() if r[s]["status"] == "found") for s in cc.SLOTS}
        got = {"osh_law": per["osh_law"], "standards_body": per["standards_body"], "total": sum(per.values())}
        print(got, per)
        short = {k: (got[k], v) for k, v in FLOORS.items() if got[k] < v}
        if short:
            fail(f"floors short (got, needed): {short}")
        print("PASS floors")
    elif cmd == "links":
        rows = found(data)
        unchecked = [r for r in rows if "check" not in r[2]]
        missing = [r for r in rows if r[2].get("check") == "missing"]
        if unchecked or missing or not rows:
            fail(f"links found={len(rows)} unchecked={len(unchecked)} missing={len(missing)}")
        print(f"PASS links unchecked=0 missing=0 of {len(rows)}")
    elif cmd == "fetch":
        import check_standards_library as chk
        todo = [r for r in found(data) if "check" not in r[2]]
        by_host: dict[str, list[str]] = {}
        for u in dict.fromkeys(r[2]["url"] for r in todo):
            by_host.setdefault(urlsplit(u).netloc, []).append(u)
        results: dict = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=12) as ex:
            for res in ex.map(chk.run_host, by_host.values()):
                results.update(res)
        for _, _, v in todo:
            v["check"] = results[v["url"]]["check"]
        save(data)
    elif cmd == "prune":
        n = 0
        for iso, slot, v in found(data):
            if v.get("check") == "missing":
                table[iso][slot] = {"status": "not-found", "note": "A search result gave a link that returned 'not found'; entry removed."}
                n += 1
        save(data)
        print("pruned", n)
    else:
        fail(f"unknown command {cmd}")
    if cmd in ("fetch", "prune"):
        tally: dict[str, int] = {}
        for _, _, v in found(data):
            tally[v.get("check", "unchecked")] = tally.get(v.get("check", "unchecked"), 0) + 1
        print(tally)


def save(data: dict) -> None:
    with open(DATA, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


if __name__ == "__main__":
    main()

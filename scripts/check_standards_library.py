"""Check every distinct URL in data/standards_library.json (one request per URL, one at a time per host) and record the result.

robots.txt is read first for each host; its disallow rules and crawl delay are honoured.

check values:
  ok        reachable, and the page is not an error page
  pdf       reachable and the response is a PDF
  missing   404/410, or a "200" page whose <title> says it was not found
  blocked   401/403/418/429/202/999 or a bot challenge: the site refuses automated clients; open it in a browser (not bypassed)
  error     timeout, TLS, DNS or server error
  robots    the host's robots.txt disallows Claude agents for this URL: not requested
For ASTM pages the official page title replaces the (empty) title and title_source becomes 'publisher-page'.

Usage: python3 scripts/check_standards_library.py [--only-unchecked] [--host store.astm.org] [--pdf]
Standard library plus the curl command.
"""
import argparse
import concurrent.futures
import datetime
import html
import json
import os
import re
import subprocess
import tempfile
import time
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "standards_library.json")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"


AGENTS = ("Claude-User", "ClaudeBot", "anthropic-ai")  # this checker is run by or for a Claude agent: honour rules aimed at them
_ROBOTS: dict[str, RobotFileParser | None] = {}


def robots(url: str) -> RobotFileParser | None:
    host = urlsplit(url).netloc
    if host not in _ROBOTS:
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "15", "-w", "\n%{http_code}", f"https://{host}/robots.txt"],
                           capture_output=True, text=True, errors="replace")
        body, _, code = r.stdout.rpartition("\n")
        rp = None
        if code == "200" and "<html" not in body[:500].lower():
            rp = RobotFileParser()
            rp.parse(body.splitlines())
        _ROBOTS[host] = rp
    return _ROBOTS[host]


def allowed(url: str) -> bool:
    rp = robots(url)
    return rp is None or all(rp.can_fetch(a, url) for a in AGENTS)


def delay(url: str) -> None:
    rp = robots(url)
    asked = (rp.crawl_delay("ClaudeBot") or rp.crawl_delay("*")) if rp else None
    time.sleep(max(1.0, float(asked or 1)))


def fetch(url: str) -> dict:
    with tempfile.NamedTemporaryFile() as tmp:
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "30", "--max-filesize", "30000000", "-o", tmp.name,
                            "-w", "%{http_code}\t%{content_type}\t%{url_effective}", url], capture_output=True, text=True)
        parts = (r.stdout.split("\t") + ["", "", ""])[:3]
        code = int(parts[0] or 0)
        with open(tmp.name, "rb") as fh:
            body = fh.read(600_000)
    ctype, final = parts[1].lower(), parts[2]
    m = re.search(rb"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    title = " ".join(html.unescape(m.group(1).decode("utf-8", "replace")).split()) if m else ""
    low = title.lower()
    if code in (401, 403, 418, 429, 202, 999) or "just a moment" in low or "attention required" in low:
        check = "blocked"
    elif code in (404, 410) or low.startswith("404") or "page not found" in low:
        check = "missing"
    elif 200 <= code < 300:
        check = "pdf" if body.startswith(b"%PDF") or "pdf" in ctype else "ok"
    else:
        check = "error"
    return {"http_status": code, "check": check, "final_url": final, "page_title": title}


def check_pdf(url: str) -> str:
    """Ask for the first bytes only; 'pdf' only if the file really starts with the PDF magic number."""
    if not allowed(url):
        return "robots"
    with tempfile.NamedTemporaryFile() as tmp:
        r = subprocess.run(["curl", "-sL", "-A", UA, "--max-time", "40", "-r", "0-1023", "--max-filesize", "80000000", "-o", tmp.name,
                            "-w", "%{http_code}", url], capture_output=True, text=True)
        code = int(r.stdout.strip() or 0)
        with open(tmp.name, "rb") as fh:
            head = fh.read(8)
    if head.startswith(b"%PDF"):
        return "pdf"
    return "blocked" if code in (401, 403, 418, 429, 202, 999) else "missing" if code in (404, 410) else "not-pdf" if code else "error"


def run_host(urls: list[str]) -> dict:
    out = {}
    blocked_in_a_row = 0
    for u in urls:
        if not allowed(u):
            out[u] = {"http_status": 0, "check": "robots", "final_url": "", "page_title": ""}
            continue
        if blocked_in_a_row >= 3:  # the host refuses automated clients: stop asking it
            out[u] = {"http_status": 0, "check": "blocked", "final_url": "", "page_title": ""}
            continue
        out[u] = fetch(u)
        blocked_in_a_row = blocked_in_a_row + 1 if out[u]["check"] == "blocked" else 0
        print(out[u]["http_status"], out[u]["check"], u, flush=True)
        delay(u)
    return out


def astm_title(page_title: str, designation: str) -> str:
    code = designation.split()[-1]
    m = re.match(rf"^{code}(?![0-9])\S*\s+(.*)$", page_title, re.I)
    if not m:
        return ""
    return re.split(r"\s*\|\s*", m.group(1))[0].strip()


def save(data: dict) -> None:
    with open(P, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=1, ensure_ascii=False)
        fh.write("\n")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only-unchecked", action="store_true")
    ap.add_argument("--host")
    ap.add_argument("--pdf", action="store_true", help="check only the pdf_url fields")
    a = ap.parse_args()
    with open(P, encoding="utf-8") as fh:
        data = json.load(fh)
    if a.pdf:
        for e in data["entries"]:
            if e.get("pdf_url"):
                e["pdf_check"] = check_pdf(e["pdf_url"])
                print(e["pdf_check"], e["pdf_url"], flush=True)
                delay(e["pdf_url"])
        save(data)
        return
    todo = [e for e in data["entries"]
            if (not a.only_unchecked or "check" not in e) and (not a.host or urlsplit(e["url"]).netloc == a.host)]
    by_host: dict[str, list[str]] = {}
    for u in dict.fromkeys(e["url"] for e in todo):
        by_host.setdefault(urlsplit(u).netloc, []).append(u)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:  # one thread per host at a time
        for res in ex.map(run_host, by_host.values()):
            results.update(res)
    today = datetime.date.today().isoformat()
    for e in todo:
        r = results[e["url"]]
        e.update(http_status=r["http_status"], check=r["check"], checked=today)
        if r["final_url"] and r["final_url"].rstrip("/") != e["url"].rstrip("/"):
            e["final_url"] = r["final_url"]
        else:
            e.pop("final_url", None)
        if e["body"] == "ASTM" and r["check"] == "ok":
            t = astm_title(r["page_title"], e["designation"])
            if t:
                e["title"], e["title_source"] = t, "publisher-page"
    # drop any earlier result for a link that robots.txt disallows
    for e in data["entries"]:
        if e.get("check") not in (None, "robots") and not allowed(e["url"]):
            e.update(check="robots", http_status=0)
            e.pop("final_url", None)
    save(data)
    tally: dict[str, int] = {}
    for e in data["entries"]:
        tally[e.get("check", "unchecked")] = tally.get(e.get("check", "unchecked"), 0) + 1
    print(tally)


if __name__ == "__main__":
    main()

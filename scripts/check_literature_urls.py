"""Check every URL in data/literature.json (HTTP status, browser User-Agent, polite 1 req/s) and record it in the file."""
import datetime
import json
import os
import subprocess
import time

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "process_safety", "data", "literature.json")
d = json.load(open(P))
today = datetime.date.today().isoformat()
for e in d["entries"]:
    r = subprocess.run(["curl", "-sL", "-A", "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/120 Safari/537.36", "-o", "/dev/null",
                        "-w", "%{http_code}", "--max-time", "25", e["url"]], capture_output=True, text=True)
    code = r.stdout.strip() or "000"
    e["http_status"] = int(code)
    e["checked"] = today
    print(code, e["id"])
    time.sleep(1)
json.dump(d, open(P, "w"), indent=1)

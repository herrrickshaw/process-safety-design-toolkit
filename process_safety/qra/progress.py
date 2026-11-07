"""Progress bar with elapsed time and ETA (stderr), stdlib only. Throttled so it costs nothing in tight loops."""
from __future__ import annotations

import sys
import time


def _fmt(s: float) -> str:
    if s != s or s == float("inf"):
        return "--"
    s = int(round(s))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h{m:02d}m{sec:02d}s" if h else f"{m}m{sec:02d}s" if m else f"{sec}s"


class Progress:
    """p = Progress(total, "IR grid"); p.update(n); p.done(). ETA = elapsed/done x remaining (linear throughput)."""

    def __init__(self, total: int, label: str = "", stream=None, min_interval_s: float = 0.5, enabled: bool = True):
        self.total = max(int(total), 1)
        self.label = label
        self.stream = stream or sys.stderr
        self.min_interval = min_interval_s
        self.enabled = enabled
        self.n = 0
        self.t0 = time.perf_counter()
        self._last = 0.0
        self._tty = hasattr(self.stream, "isatty") and self.stream.isatty()
        self._last_decile = -1

    @property
    def elapsed(self) -> float:
        return time.perf_counter() - self.t0

    def eta(self) -> float:
        return float("inf") if self.n == 0 else self.elapsed / self.n * (self.total - self.n)

    def line(self) -> str:
        f = self.n / self.total
        bar = "#" * int(30 * f) + "." * (30 - int(30 * f))
        return f"{self.label:<22} [{bar}] {100 * f:5.1f}% {self.n}/{self.total}  elapsed {_fmt(self.elapsed)}  ETA {_fmt(self.eta())}"

    def update(self, k: int = 1) -> None:
        self.n = min(self.n + k, self.total)
        if not self.enabled:
            return
        now = time.perf_counter()
        if self._tty:
            if now - self._last >= self.min_interval or self.n == self.total:
                self.stream.write("\r" + self.line())
                self.stream.flush()
                self._last = now
        else:  # logs / notebooks: one line per 10 %
            dec = int(10 * self.n / self.total)
            if dec != self._last_decile:
                self._last_decile = dec
                self.stream.write(self.line() + "\n")
                self.stream.flush()

    def done(self) -> float:
        self.n = self.total
        if self.enabled:
            self.stream.write(("\r" if self._tty else "") + self.line() + "  done\n")
            self.stream.flush()
        return self.elapsed

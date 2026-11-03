"""Reliability and risk-analysis arithmetic: availability, k-out-of-n, fault trees (exact + minimal cut sets + Birnbaum importance),
event trees, FMEA RPN, and a configurable risk matrix.

Independence of basic events is assumed (no common cause unless you model it as its own basic event). Tolerable-risk matrices are
company-specific: the default 5x5 bands here are a placeholder; replace with your client's matrix.
"""
from __future__ import annotations

import itertools
import math
from dataclasses import dataclass, field


def failure_probability(lambda_per_h: float, t_h: float) -> float:
    return 1 - math.exp(-lambda_per_h * t_h)


def availability(mtbf_h: float, mttr_h: float) -> float:
    return mtbf_h / (mtbf_h + mttr_h)


def parallel_availability(avails: list[float]) -> float:
    return 1 - math.prod(1 - a for a in avails)


def series_availability(avails: list[float]) -> float:
    return math.prod(avails)


def koon_failure_probability(k_required: int, n: int, p_fail: float) -> float:
    """Probability that fewer than k of n identical independent components work (system with k-out-of-n success logic fails)."""
    return sum(math.comb(n, j) * p_fail ** j * (1 - p_fail) ** (n - j) for j in range(n - k_required + 1, n + 1))


@dataclass
class FaultTree:
    basic: dict[str, float] = field(default_factory=dict)
    gates: dict[str, tuple] = field(default_factory=dict)  # name -> (type, [inputs], k)

    def event(self, name: str, p: float) -> "FaultTree":
        self.basic[name] = p
        return self

    def gate(self, name: str, kind: str, inputs: list[str], k: int | None = None) -> "FaultTree":
        """kind: AND | OR | VOTE (k of n inputs must occur)."""
        self.gates[name] = (kind.upper(), list(inputs), k)
        return self

    def _eval(self, node: str, state: dict[str, bool]) -> bool:
        if node in self.basic:
            return state[node]
        kind, ins, k = self.gates[node]
        vals = [self._eval(i, state) for i in ins]
        return all(vals) if kind == "AND" else any(vals) if kind == "OR" else sum(vals) >= k

    def _used(self, node: str, acc: set) -> set:
        if node in self.basic:
            acc.add(node)
        else:
            for i in self.gates[node][1]:
                self._used(i, acc)
        return acc

    def probability(self, top: str, override: dict[str, float] | None = None) -> float:
        """Exact top-event probability by Shannon enumeration over the basic events actually used (<= 20), so repeated events are handled."""
        probs = {**self.basic, **(override or {})}
        names = sorted(self._used(top, set()))
        if len(names) > 20:
            raise ValueError("more than 20 basic events: use minimal cut sets with the rare-event approximation")
        total = 0.0
        for bits in itertools.product([False, True], repeat=len(names)):
            state = dict(zip(names, bits))
            if self._eval(top, state):
                total += math.prod(probs[n] if b else 1 - probs[n] for n, b in state.items())
        return total

    def minimal_cut_sets(self, top: str) -> list[frozenset]:
        """MOCUS: expand gates to sets of basic events, then drop supersets."""
        def expand(node):
            if node in self.basic:
                return [frozenset([node])]
            kind, ins, k = self.gates[node]
            subs = [expand(i) for i in ins]
            if kind == "OR":
                return [c for s in subs for c in s]
            if kind == "AND":
                return [frozenset().union(*combo) for combo in itertools.product(*subs)]
            out = []
            for pick in itertools.combinations(range(len(subs)), k):
                out += [frozenset().union(*combo) for combo in itertools.product(*[subs[i] for i in pick])]
            return out
        sets = list(set(expand(top)))
        return sorted([s for s in sets if not any(o < s for o in sets)], key=lambda s: (len(s), sorted(s)))

    def birnbaum(self, top: str) -> dict[str, float]:
        """Birnbaum importance: P(top | event certain) - P(top | event impossible)."""
        return {n: self.probability(top, {n: 1.0}) - self.probability(top, {n: 0.0}) for n in sorted(self._used(top, set()))}


def event_tree(initiating_freq_per_yr: float, barriers: list[tuple[str, float]]) -> list[dict]:
    """barriers = [(name, probability the barrier WORKS)]. Returns every outcome path with its frequency; frequencies sum to the IE frequency."""
    out = []
    for bits in itertools.product([True, False], repeat=len(barriers)):
        p = math.prod(pw if b else 1 - pw for b, (_, pw) in zip(bits, barriers))
        out.append({"path": {n: ("works" if b else "fails") for b, (n, _) in zip(bits, barriers)}, "frequency_per_yr": initiating_freq_per_yr * p})
    return out


def rpn(severity: int, occurrence: int, detection: int) -> int:
    """FMEA Risk Priority Number (each 1-10)."""
    return severity * occurrence * detection


DEFAULT_BANDS = [(4, "low"), (9, "medium"), (16, "high"), (25, "extreme")]  # placeholder: replace with the client matrix


def risk_rank(severity: int, likelihood: int, bands=DEFAULT_BANDS) -> tuple[int, str]:
    """5x5 matrix score = severity x likelihood mapped to a band (upper bounds)."""
    score = severity * likelihood
    for ub, name in bands:
        if score <= ub:
            return score, name
    return score, bands[-1][1]

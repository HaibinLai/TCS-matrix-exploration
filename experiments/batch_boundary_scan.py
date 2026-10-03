#!/usr/bin/env python3
"""Batch approximate scan for z/x=1 hierarchy overhead.

This is a discovery/negative-search tool.  It samples arbitrary divisible
triples P1>P2>P3, evaluates the lower envelopes in a vectorized grid of
t=y/x values, and sends the top candidates to the exact boundary checker.
It does not prove a universal upper bound.
"""
from itertools import product
from random import Random

import numpy as np

try:
    from scan_boundary_hierarchies import divisors, exact_boundary, grids, line, nested
except ModuleNotFoundError:
    from .scan_boundary_hierarchies import divisors, exact_boundary, grids, line, nested


def approximate_fast(ps, steps=401):
    choices = [list(grids(p)) for p in ps]
    chains = [c for c in product(*choices) if nested(c)]
    if len(chains) > 5000:
        return None
    independent = [
        np.asarray([[float(a), float(b)] for g in gs for a, b in [line(g)]])
        for gs in choices
    ]
    nested_lines = np.asarray(
        [[sum(float(line(g)[j]) for g in chain) for j in range(2)] for chain in chains]
    )
    t = np.linspace(0.0, 1.0, steps)
    independent_value = sum(np.min(lines[:, 0, None] + lines[:, 1, None] * t, axis=0) for lines in independent)
    nested_value = np.min(nested_lines[:, 0, None] + nested_lines[:, 1, None] * t, axis=0)
    ratio = nested_value / independent_value
    index = int(np.argmax(ratio))
    return float(ratio[index]), float(t[index]), len(chains), tuple(map(len, choices))


def sample_triples(seed=20261002, samples=500, max_p1=1500):
    rng = Random(seed)
    divisor_table = [[] for _ in range(max_p1 + 1)]
    for divisor in range(1, max_p1 + 1):
        for multiple in range(divisor, max_p1 + 1, divisor):
            divisor_table[multiple].append(divisor)
    out = set()
    while len(out) < samples:
        p1 = rng.randint(12, max_p1)
        proper = [d for d in divisor_table[p1] if 2 <= d < p1]
        if not proper:
            continue
        p2 = rng.choice(proper)
        proper2 = [d for d in divisor_table[p2] if 2 <= d < p2]
        if not proper2:
            continue
        p3 = rng.choice(proper2)
        out.add((p1, p2, p3))
    return sorted(out)


if __name__ == "__main__":
    candidates = sample_triples()
    approximate = []
    for ps in candidates:
        result = approximate_fast(ps)
        if result is not None:
            approximate.append((result[0], ps, result[1:]))
    approximate.sort(reverse=True)
    print("sampled", len(candidates), "evaluated", len(approximate), "hierarchies")
    for row in approximate[:20]:
        print("approx", row)
    print("exact top candidates")
    for _, ps, _ in approximate[:15]:
        exact = exact_boundary(ps)
        if exact is not None:
            print("exact", ps, exact[:2], float(exact[0]), "meta", exact[2:])

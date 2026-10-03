#!/usr/bin/env python3
"""Scan the three-level family (2*p*q, p*q, p) at y/x=1/p.

Unlike the square-free prime-family scripts, p may be composite.  The exact
partial-chain envelope uses Fraction arithmetic and the 1-D hull pruner.
"""
from fractions import Fraction
import argparse

from scan_multilevel_boundary_dp import compatible, grids, line, value
from scan_multilevel_boundary_hull import prune


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def value_at(p, q):
    choices = [list(grids(x)) for x in (2 * p * q, p * q, p)]
    t = Fraction(1, p)
    independent = sum(min(value(line(g), t) for g in gs) for gs in choices)
    partial = {g: [line(g)] for g in choices[0]}
    for level in (1, 2):
        new = {}
        for outer in choices[level]:
            lo = line(outer)
            candidates = []
            for inner in choices[level - 1]:
                if compatible(inner, outer):
                    candidates.extend((a + lo[0], b + lo[1])
                                      for a, b in partial[inner])
            new[outer] = prune(candidates)
        partial = new
    nested = min(value(l, t) for lines in partial.values() for l in lines)
    return nested / independent


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-max", type=int, default=100)
    ap.add_argument("--q-max", type=int, default=1000)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    rows = []
    qs = [q for q in range(3, args.q_max + 1) if is_prime(q)]
    for p in range(3, args.p_max + 1):
        for q in qs:
            if q <= p:
                continue
            ratio = value_at(p, q)
            rows.append((ratio, p, q))
    rows.sort(reverse=True)
    print(f"checked={len(rows)} p<= {args.p_max} prime q<= {args.q_max}")
    for ratio, p, q in rows[:args.top]:
        print(f"p={p} q={q} ratio={ratio} ({float(ratio):.9f})")

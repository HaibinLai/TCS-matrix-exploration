#!/usr/bin/env python3
"""Exact-grid diagnostic for radial monotonicity in the prime-p family.

Write normalized aspect ratios as (x,z,y)=(1,s,s*t), 0<=s,t<=1.  The
boundary theorem proves the maximum at s=1; this script checks the stronger
conjecture that N/I is nondecreasing in s for each fixed t.  It is empirical,
not a proof.
"""
from fractions import Fraction
from itertools import product
import argparse

try:
    from exact_2d_pruned import grids, line, nested, value
except ModuleNotFoundError:
    from .exact_2d_pruned import grids, line, nested, value


def ratio(choices, chains, s, t):
    z = s
    y = s * t
    denominator = sum(
        (min(value(line(g), z, y) for g in gs) for gs in choices),
        Fraction(0),
    )
    numerator = min(
        sum((value(line(g), z, y) for g in chain), Fraction(0))
        for chain in chains
    )
    return numerator / denominator


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n**0.5) + 1))


def check(p, q, steps):
    choices = [list(grids(P)) for P in (2 * p * q, p * q, p)]
    chains = [chain for chain in product(*choices) if nested(chain)]
    grid = [Fraction(i, steps) for i in range(steps + 1)]
    minimum_increment = None
    witness = None
    for t in grid:
        previous = ratio(choices, chains, grid[0], t)
        for s in grid[1:]:
            current = ratio(choices, chains, s, t)
            increment = current - previous
            if minimum_increment is None or increment < minimum_increment:
                minimum_increment, witness = increment, (s, t)
            if increment < 0:
                return False, minimum_increment, witness
            previous = current
    return True, minimum_increment, witness


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", nargs="*", type=int, default=[3, 5, 7, 11, 13, 17])
    parser.add_argument("--q", nargs="*", type=int, default=[29, 31, 53, 71, 101])
    parser.add_argument("--steps", type=int, default=40)
    args = parser.parse_args()
    checked = 0
    for p in args.p:
        for q in args.q:
            if p >= q or not is_prime(p) or not is_prime(q):
                continue
            ok, increment, witness = check(p, q, args.steps)
            print(f"p={p:2d} q={q:3d} monotone={ok} min_increment={increment} witness={witness}")
            if not ok:
                raise AssertionError((p, q, increment, witness))
            checked += 1
    print(f"checked={checked} radial-monotonicity cases")

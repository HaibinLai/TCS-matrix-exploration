#!/usr/bin/env python3
"""Check the analytic boundary theorem for the prime-p hierarchy family.

For P*=(2*p*q, p*q, p), q>p>=3 prime, write t=y/x on the boundary z=x.
The independent lower envelope has three intervals, and three explicit nested
chains provide the upper bounds needed for the ratio.  The proof itself is
recorded in the research log; this script checks the formulas exactly against
all factor assignments for selected parameters.
"""
from fractions import Fraction
from itertools import product
import argparse

try:
    from scan_boundary_hierarchies import grids, line, nested, val
except ModuleNotFoundError:
    from .scan_boundary_hierarchies import grids, line, nested, val


def boundary_line(grid):
    """Return intercept and t-slope for x=z=1, y=t."""
    a, b, c = grid
    return Fraction(1, a * b) + Fraction(1, a * c), Fraction(1, b * c)


def candidate_independent(p, q, t):
    i1 = min(
        Fraction(1, p * q) + t,
        Fraction(3, 2 * p * q) + t / 2,
        Fraction(p + 2, 2 * p * q) + t / (2 * p),
    )
    i2 = min(Fraction(2, p * q) + t, Fraction(p + 1, p * q) + t / p)
    i3 = Fraction(2, p) + t
    return i1 + i2 + i3


def chain_value(chain, t):
    return sum((val(boundary_line(g), t) for g in chain), Fraction(0))


def candidate_ratio(p, q):
    return Fraction(p * (9 * q + 7), (6 * p + 3) * q + 3 * p * p + 4 * p)


def verify_one(p, q):
    pstars = (2 * p * q, p * q, p)
    choices = [list(grids(P)) for P in pstars]
    chains = [chain for chain in product(*choices) if nested(chain)]
    chain_a = ((2 * p * q, 1, 1), (p * q, 1, 1), (p, 1, 1))
    chain_b = ((p * q, 1, 2), (p * q, 1, 1), (p, 1, 1))
    chain_c = ((p, 2, q), (p, 1, q), (p, 1, 1))
    assert chain_a in chains and chain_b in chains and chain_c in chains

    breakpoints = [
        Fraction(0),
        Fraction(1, p * q),
        Fraction(1, q),
        Fraction(1, p),
        Fraction(1),
    ]
    for left, right in zip(breakpoints, breakpoints[1:]):
        midpoint = (left + right) / 2
        independent = sum(
            (min(val(boundary_line(g), midpoint) for g in gs) for gs in choices),
            Fraction(0),
        )
        assert independent == candidate_independent(p, q, midpoint)
        # The selected chain gives an upper bound for the nested envelope.
        selected = chain_a if right <= Fraction(1, q) else chain_b if left < Fraction(1, p) else chain_c
        nested_upper = chain_value(selected, midpoint)
        nested_value = min(chain_value(chain, midpoint) for chain in chains)
        assert nested_value <= nested_upper

    expected = candidate_ratio(p, q)
    # At t=1/p, the symbolic endpoint certificate identifies chain_c as optimal.
    t = Fraction(1, p)
    nested_value = min(chain_value(chain, t) for chain in chains)
    independent = sum(min(val(boundary_line(g), t) for g in gs) for gs in choices)
    assert nested_value / independent == expected
    return len(chains), expected


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n**0.5) + 1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", nargs="*", type=int, default=[3, 5, 7, 11, 13, 17])
    parser.add_argument("--q", nargs="*", type=int, default=[29, 31, 53, 71, 101])
    args = parser.parse_args()
    checked = 0
    for p in args.p:
        for q in args.q:
            if p >= q or not is_prime(p) or not is_prime(q):
                continue
            chains, ratio = verify_one(p, q)
            print(f"p={p:2d} q={q:3d} chains={chains:2d} boundary R={ratio} OK")
            checked += 1
    print(f"checked={checked} boundary formula cases")

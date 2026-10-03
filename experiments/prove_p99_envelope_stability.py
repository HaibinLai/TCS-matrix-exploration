#!/usr/bin/env python3
"""Parametric domination certificate for the prime-p, q-prime family.

For q>p prime, every grid line has coefficients affine in u=1/q.  The
active lines found at q0 dominate every grid/nested line on the whole domain
for u in [0,1/q0].  Since a line difference is affine in (z,y) and affine in
u after fixing a domain corner, it is enough to check u=0,1/q0 at the three
vertices (0,0),(1,0),(1,1).

This proves a fixed finite active-line cover for all prime q>=q0.  It does
not by itself prove which overlay vertex maximizes N/I; that is the remaining
parametric-ratio step.
"""
from fractions import Fraction as F
import argparse

from exact_multilevel_2d import build_envelopes, line


VERTICES = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1))]


def add_poly(x, y):
    return x[0] + y[0], x[1] + y[1]


def inv_product(x, y):
    exponent = x[1] + y[1]
    if exponent > 1:
        raise AssertionError((x, y))
    return (F(1, x[0] * y[0]), F(0)) if exponent == 0 else (F(0), F(1, x[0] * y[0]))


def symbolic_grid(g, q0):
    """Replace the unique q0 factor by a symbolic q factor."""
    return tuple((d // q0, 1) if d % q0 == 0 else (d, 0) for d in g)


def symbolic_line(g, q0):
    a, b, c = symbolic_grid(g, q0)
    return (inv_product(a, b), inv_product(a, c), inv_product(b, c))


def symbolic_sum(grids, q0):
    out = [(F(0), F(0))] * 3
    for g in grids:
        current = symbolic_line(g, q0)
        out = [add_poly(x, y) for x, y in zip(out, current)]
    return tuple(out)


def evaluate(polyline, u, z, y):
    return sum(
        (((constant + slope * u) * coordinate)
         for (constant, slope), coordinate in zip(polyline, (F(1), F(z), F(y)))),
        F(0),
    )


def dominates(candidate, dominator, q0):
    """Check candidate >= dominator at all endpoint/corner combinations."""
    for u in (F(0), F(1, q0)):
        for z, y in VERTICES:
            if evaluate(candidate, u, z, y) < evaluate(dominator, u, z, y):
                return False
    return True


def compatible(inner, outer):
    return all(i % o == 0 for i, o in zip(inner, outer))


def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def certify(p=99, q0=997):
    if p < 3:
        raise ValueError("p must be at least 3")
    if q0 <= p or not is_prime(q0):
        raise ValueError("q0 must be a prime larger than p")
    pstars = (2 * p * q0, p * q0, p)
    choices, independent, nested, partial_stats = build_envelopes(pstars)

    all_independent = []
    active_independent = []
    for level, grids in enumerate(choices):
        all_lines = [symbolic_sum((g,), q0) for g in grids]
        active_lines = []
        for active in independent[level]:
            matches = [symbolic_sum((g,), q0) for g in grids if line(g) == active]
            if not matches or len(set(matches)) != 1:
                raise AssertionError((level, active, len(matches), len(set(matches))))
            active_lines.append(matches[0])
        all_independent.append(all_lines)
        active_independent.append(active_lines)

    chains = []
    for inner in choices[0]:
        for middle in choices[1]:
            if not compatible(inner, middle):
                continue
            for outer in choices[2]:
                if compatible(middle, outer):
                    chains.append((inner, middle, outer))
    all_nested = list({symbolic_sum(chain, q0) for chain in chains})
    active_nested = []
    for active in nested:
        matches = [symbolic_sum(chain, q0) for chain in chains
                   if tuple(sum(line(g)[i] for g in chain) for i in range(3)) == active]
        if not matches or len(set(matches)) != 1:
            raise AssertionError((active, len(matches), len(set(matches))))
        active_nested.append(matches[0])

    results = []
    for level in range(3):
        uncovered = [
            candidate for candidate in all_independent[level]
            if not any(dominates(candidate, active, q0) for active in active_independent[level])
        ]
        results.append((f"independent[{level}]", len(all_independent[level]),
                       len(active_independent[level]), len(uncovered)))
        if uncovered:
            raise AssertionError(results[-1])
    uncovered = [
        candidate for candidate in all_nested
        if not any(dominates(candidate, active, q0) for active in active_nested)
    ]
    results.append(("nested", len(all_nested), len(active_nested), len(uncovered)))
    if uncovered:
        raise AssertionError(results[-1])
    print("p", p, "q0", q0, "partial stats", tuple(partial_stats))
    for result in results:
        print("%s total=%d active=%d uncovered=%d" % result)
    print("certificate=True for every prime q>=q0 at the envelope-cover level")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", type=int, default=99)
    parser.add_argument("--q0", type=int, default=997)
    args = parser.parse_args()
    certify(args.p, args.q0)

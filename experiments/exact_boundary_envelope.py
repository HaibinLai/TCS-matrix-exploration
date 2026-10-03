#!/usr/bin/env python3
"""Exact one-dimensional envelope on the aspect-ratio boundary z/x=1.

For fixed P*=(132,66,6), every grid proxy is a+b*t with t=y/x in [0,1].
The script enumerates all breakpoints of the independent and nested lower
envelopes using exact rational arithmetic, then maximizes their ratio on each
interval. This proves only the z/x=1 boundary result, not the full 2-D domain.
"""
from fractions import Fraction
from itertools import product


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def nested(chain):
    return all(
        all(inner[d] % outer[d] == 0 for d in range(3))
        for inner, outer in zip(chain, chain[1:])
    )


def line(grid):
    # z/x=1; t=y/x. H = a + b*t.
    p1, p2, p3 = grid
    return Fraction(1, p1*p2) + Fraction(1, p1*p3), Fraction(1, p2*p3)


def intersect(l1, l2):
    a1, b1 = l1
    a2, b2 = l2
    if b1 == b2:
        return None
    return (a2 - a1) / (b1 - b2)


def value(line_pair, t):
    a, b = line_pair
    return a + b*t


def lower_line(lines, t):
    vals = [(value(line_pair, t), line_pair) for line_pair in lines]
    return min(vals)


def envelope_breakpoints(lines):
    points = {Fraction(0), Fraction(1)}
    for i, l1 in enumerate(lines):
        for l2 in lines[i+1:]:
            t = intersect(l1, l2)
            if t is not None and Fraction(0) < t < Fraction(1):
                points.add(t)
    return sorted(points)


if __name__ == "__main__":
    pstars = (132, 66, 6)
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]
    independent_lines = []
    for gs in choices:
        # A line for each level; the sum of lower envelopes is handled by
        # carrying all per-level breakpoints.
        independent_lines.append([line(g) for g in gs])
    nested_lines = []
    for chain in chains:
        a = sum((line(g)[0] for g in chain), Fraction(0))
        b = sum((line(g)[1] for g in chain), Fraction(0))
        nested_lines.append((a, b))

    points = {Fraction(0), Fraction(1)}
    for lines in independent_lines:
        points.update(envelope_breakpoints(lines))
    points.update(envelope_breakpoints(nested_lines))
    points = sorted(points)

    best = (Fraction(0), None)
    active_changes = []
    for lo, hi in zip(points, points[1:]):
        mid = (lo + hi) / 2
        inds = [lower_line(lines, mid)[1] for lines in independent_lines]
        nval, nline = lower_line(nested_lines, mid)
        ilines = inds
        ia = sum((l[0] for l in ilines), Fraction(0))
        ib = sum((l[1] for l in ilines), Fraction(0))
        na, nb = nline
        # Ratio of two positive affine functions is monotone on the interval.
        candidates = [lo, hi]
        for t in candidates:
            I = ia + ib*t
            N = na + nb*t
            ratio = N / I
            if ratio > best[0]:
                best = (ratio, (t, ilines, nline))
        active_changes.append((lo, hi, ilines, nline))

    print("P*", pstars, "nested chains", len(chains))
    print("breakpoints", len(points), "intervals", len(points)-1)
    print("max ratio", best[0], float(best[0]))
    print("at", best[1][0], "independent lines", best[1][1], "nested line", best[1][2])
    print("contains 5/33:", Fraction(5,33) in points)
    for lo, hi, inds, nline in active_changes:
        if lo <= Fraction(5,33) <= hi:
            print("interval around 5/33", lo, hi, inds, nline)

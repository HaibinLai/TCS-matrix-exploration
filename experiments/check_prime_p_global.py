#!/usr/bin/env python3
"""Exact two-dimensional checks for the prime-p hierarchy family.

This is an empirical verifier, not a symbolic proof.  It reuses the exact
rational arrangement enumeration from ``exact_2d_pruned.py`` and checks that
the observed global maximizer agrees with the candidate

    R_p(q) = p*(9*q+7) / ((6*p+3)*q + 3*p*p + 4*p)

at (z,y)=(1,1/p), for selected distinct primes p<q.
"""
from fractions import Fraction
from itertools import product
import argparse

try:
    from exact_2d_pruned import add, grids, inter, inside, line, lower_active, value, nested
except ModuleNotFoundError:
    from .exact_2d_pruned import add, grids, inter, inside, line, lower_active, value, nested


DOMAIN = [
    (Fraction(0), Fraction(0), Fraction(-1)),
    (Fraction(0), Fraction(-1), Fraction(1)),
    (Fraction(-1), Fraction(1), Fraction(0)),
]
CORNERS = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(1), Fraction(1))]


def equality(left, right):
    return tuple(a - b for a, b in zip(left, right))


def edge_points(edge):
    a, b, c = edge
    out = []
    if b:
        out.append((-a / b, Fraction(0)))
    if c:
        out.append((Fraction(1), -(a + b) / c))
    if b + c:
        z = -a / (b + c)
        out.append((z, z))
    return out


def exact_global(pstars):
    choices = [list(grids(p)) for p in pstars]
    chains = [chain for chain in product(*choices) if nested(chain)]
    independent_lines = [list({line(g) for g in gs}) for gs in choices]
    nested_lines = list({add(line(c[0]), line(c[1]), line(c[2])) for c in chains})

    active_independent = [
        [candidate for candidate in lines if lower_active(candidate, lines)]
        for lines in independent_lines
    ]
    active_nested = [candidate for candidate in nested_lines if lower_active(candidate, nested_lines)]

    equalities = []
    for lines in active_independent:
        equalities.extend(equality(a, b) for i, a in enumerate(lines) for b in lines[i + 1 :])
    equalities.extend(equality(a, b) for i, a in enumerate(active_nested) for b in active_nested[i + 1 :])

    points = set(CORNERS)
    for edge in equalities:
        points.update(point for point in edge_points(edge) if inside(*point))
    for i, first in enumerate(equalities):
        for second in equalities[i + 1 :]:
            point = inter(first, second)
            if point is not None and inside(*point):
                points.add(point)

    best = (Fraction(0), None)
    for z, y in points:
        denominator = sum((min(value(candidate, z, y) for candidate in lines) for lines in independent_lines), Fraction(0))
        numerator = min(value(candidate, z, y) for candidate in nested_lines)
        ratio = numerator / denominator
        if ratio > best[0]:
            best = (ratio, (z, y, denominator, numerator))
    return best, len(chains), tuple(map(len, active_independent)), len(active_nested), len(points)


def candidate_ratio(p, q):
    return Fraction(p * (9 * q + 7), (6 * p + 3) * q + 3 * p * p + 4 * p)


def is_prime(n):
    if n < 2:
        return False
    d = 2
    while d * d <= n:
        if n % d == 0:
            return False
        d += 1
    return True


def run(ps, qs):
    checked = 0
    for p in ps:
        for q in qs:
            if p >= q or not is_prime(p) or not is_prime(q):
                continue
            pstars = (2 * p * q, p * q, p)
            (observed, location), chains, active_i, active_n, vertices = exact_global(pstars)
            expected = candidate_ratio(p, q)
            expected_location = (Fraction(1), Fraction(1, p))
            ok = observed == expected and location[:2] == expected_location
            print(
                f"p={p:2d} q={q:3d} ratio={observed} "
                f"location={location[:2]} active={active_i}/{active_n} "
                f"vertices={vertices} {'OK' if ok else 'FAIL'}"
            )
            if not ok:
                raise AssertionError((p, q, observed, expected, location, expected_location))
            checked += 1
    print(f"checked={checked} exact global-max cases")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", nargs="*", type=int, default=[3, 5, 7, 11, 13, 17])
    parser.add_argument("--q", nargs="*", type=int, default=[29, 31, 53, 71, 101])
    args = parser.parse_args()
    run(args.p, args.q)

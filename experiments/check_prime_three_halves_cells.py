#!/usr/bin/env python3
"""Polyhedral-cell certificate for the 3/2 upper bound.

Use coordinates (s,u)=(z/x,y/x), so 0<=u<=s<=1 and every grid cost is
affine in (s,u).  Rearrangement lets the independent lower envelope use only
grids with a>=b>=c in the strict ordered region.  The script overlays the
independent cells with the lower-envelope cells of all legal nested chains,
then checks H_chain <= (3/2) * I at every resulting cell vertex.  This is a
finite exact certificate for each supplied (p,q), not yet a symbolic proof
for all primes.
"""
from fractions import Fraction
from itertools import product
import argparse

try:
    from exact_2d_pruned import grids, nested
except ModuleNotFoundError:
    from .exact_2d_pruned import grids, nested


DOMAIN = [
    (Fraction(0), Fraction(-1), Fraction(0)),
    (Fraction(0), Fraction(0), Fraction(-1)),
    (Fraction(0), Fraction(-1), Fraction(1)),
    (Fraction(-1), Fraction(1), Fraction(0)),
]


def line(grid):
    a, b, c = grid
    p = a * b * c
    return (Fraction(c, p), Fraction(b, p), Fraction(a, p))


def value(line_, s, u):
    return line_[0] + line_[1] * s + line_[2] * u


def difference(left, right):
    return tuple(a - b for a, b in zip(left, right))


def intersection(first, second):
    a, b, c = first
    d, e, f = second
    determinant = b * f - c * e
    if determinant == 0:
        return None
    return ((c * d - a * f) / determinant, (a * e - b * d) / determinant)


def inside(point):
    s, u = point
    return 0 <= u <= s <= 1


def satisfies(constraints, point):
    s, u = point
    return all(a + b * s + c * u <= 0 for a, b, c in constraints)


def vertices(constraints):
    result = set()
    for index, first in enumerate(constraints):
        for second in constraints[index + 1 :]:
            point = intersection(first, second)
            if point is not None and inside(point) and satisfies(constraints, point):
                result.add(point)
    return result


def sorted_grids(p, q):
    products = (2 * p * q, p * q, p)
    return [[g for g in grids(P) if g[0] >= g[1] >= g[2]] for P in products]


def certify(p, q):
    independent = sorted_grids(p, q)
    independent_lines = [[line(g) for g in level] for level in independent]
    regions = []
    for level in independent_lines:
        active = []
        for candidate in level:
            constraints = list(DOMAIN) + [difference(candidate, other) for other in level]
            points = vertices(constraints)
            if points:
                active.append((candidate, constraints))
        regions.append(active)

    all_grids = [list(grids(P)) for P in (2 * p * q, p * q, p)]
    chains = [chain for chain in product(*all_grids) if nested(chain)]
    chain_lines = [(chain, tuple(sum(line(g)[j] for g in chain) for j in range(3))) for chain in chains]

    cells = 0
    nested_regions = 0
    for first, second, third in product(*regions):
        independent_constraints = list(DOMAIN) + first[1] + second[1] + third[1]
        if not vertices(independent_constraints):
            continue
        cells += 1
        independent_line = tuple(first[0][j] + second[0][j] + third[0][j] for j in range(3))
        for chain, chain_line in chain_lines:
            constraints = independent_constraints + [
                difference(chain_line, other_line)
                for _, other_line in chain_lines
            ]
            points = vertices(constraints)
            if not points:
                continue
            nested_regions += 1
            certificate = tuple(chain_line[j] - Fraction(3, 2) * independent_line[j] for j in range(3))
            if any(value(certificate, *point) > 0 for point in points):
                return False, tuple(map(len, regions)), cells, nested_regions, (first[0], second[0], third[0], chain)
    return True, tuple(map(len, regions)), cells, nested_regions, None


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
            ok, counts, cells, nested_regions, failure = certify(p, q)
            print(f"p={p:2d} q={q:3d} cells={cells} nested_regions={nested_regions} active={counts} certificate={ok}")
            if not ok:
                raise AssertionError((p, q, failure))
            checked += 1
    print(f"checked={checked} exact 3/2 cell certificates")

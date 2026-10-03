#!/usr/bin/env python3
"""Exact U_8/I checks for the p=2r, q=4r+3 subfamily.

U_8 is the minimum of eight valid compatible nested-chain sums.  Since N is
the minimum over all compatible chains, N <= U_8.  The script checks the
resulting upper bound exactly over the arrangement of the 10/5/2 sorted
independent lines and the eight chain lines.  It is a finite certificate for
the listed cases, not yet a symbolic proof for every r.
"""
from fractions import Fraction as F
from itertools import combinations
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from exact_multilevel_2d import grids, line, subtract, intersect, inside, satisfies, DOMAIN, value

CASES = [(5, 23), (7, 29), (11, 47), (13, 53), (17, 71), (19, 79)]


def vertices(lines):
    equalities = [subtract(a, b) for i, a in enumerate(lines) for b in lines[i + 1:]]
    points = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1))]
    for e in equalities:
        a, b, c = e
        if b:
            p = (-a / b, F(0))
            if inside(p):
                points.append(p)
        if c:
            p = (F(1), -(a + b) / c)
            if inside(p):
                points.append(p)
        if b + c:
            z = -a / (b + c)
            p = (z, z)
            if inside(p):
                points.append(p)
    for e1, e2 in combinations(equalities, 2):
        p = intersect(e1, e2)
        if inside(p):
            points.append(p)
    return list(set(points))


def chains(r, q):
    # First four chains from the original prime-family proof.
    base = [
        (F(1, r*q) + F(1, 2*r), F(5, 2*r), F(3, 4*q) + F(1, 2)),
        (F(1, r) + F(3, 2*r*q), F(5, 4*r), F(1, q) + F(1, 2)),
        (F(1, r*q) + F(1, 2*r), F(5, 4*r), F(1) + F(3, 2*q)),
        (F(1, 2*r) + F(3, 4*r*q), F(5, 2*r), F(1, q) + F(1, 2)),
    ]
    # Four additional chains needed by the composite divisor profile.
    extra = [
        (F(3, 4*r*q) + F(1, 2*r), F(3, 4*r*q) + F(1, 2*r), F(3)),
        (F(1, r*q) + F(1, 2*r), F(3, 4*r*q) + F(1, 2*r), F(5, 2)),
        (F(3, 2*r*q) + F(1, r), F(1, r*q) + F(1, 2*r), F(5, 4)),
        (F(1, r*q) + F(1, 2*r), F(3, 2*r*q) + F(1, r), F(5, 4)),
    ]
    return base + extra


def run(r, q):
    levels = []
    for P in (4*r*q, 2*r*q, 2*r):
        # Rearrangement inequality: with 1 >= z >= y, sort each factor triple
        # descending before forming its line; this preserves the lower envelope.
        sorted_grids = {tuple(sorted(g, reverse=True)) for g in grids(P)}
        levels.append([line(g) for g in sorted_grids])
    chain_lines = chains(r, q)
    all_lines = [l for ls in levels for l in ls] + chain_lines
    R = F(5*q*r*(8*q + 13),
          28*q*q*r + 15*q*q + 6*q*r*r + 52*q*r + 9*r*r)
    best = (F(0), None)
    for z, y in vertices(all_lines):
        I = sum(min(value(l, z, y) for l in ls) for ls in levels)
        U = min(value(l, z, y) for l in chain_lines)
        ratio = U / I
        if ratio > best[0]:
            best = (ratio, (z, y, I, U))
    assert best[0] == R, (r, q, best, R)
    return best, tuple(map(len, levels)), len(all_lines)


if __name__ == '__main__':
    for r, q in CASES:
        best, counts, line_count = run(r, q)
        print(f'r={r} q={q} levels={counts} lines={line_count} '
              f'max={best[0]} at ({best[1][0]},{best[1][1]})')
    print('eight-chain exact upper-bound certificate=True')

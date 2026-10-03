#!/usr/bin/env python3
"""Exact local-envelope checks for the candidate p=2r, q=4r+3 family.

This deliberately checks only the proposed point and active lines; it is not a global proof.
"""
from fractions import Fraction as F
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import build_envelopes, value


CASES = [(5, 23), (7, 29), (11, 47), (13, 53), (17, 71)]


def run(r, q):
    p = 2 * r
    z, y = F(2 * q + 3, 5 * q), F(1, r)
    _, independent, nested, stats = build_envelopes((2 * p * q, p * q, p))
    mins = []
    for lines in independent:
        vals = [value(line, z, y) for line in lines]
        mins.append(min(vals))
    nvals = [value(line, z, y) for line in nested]
    n = min(nvals)
    ratio = n / sum(mins)
    predicted = F(5 * q * r * (8 * q + 13),
                  28 * q * q * r + 15 * q * q + 6 * q * r * r + 52 * q * r + 9 * r * r)
    # The proposed active independent grids are (q,r,4), (q,r,2), (r,2,1).
    expected = [
        (F(1, r * q) + z * F(1, 4 * q) + y * F(1, 4 * r)),
        (F(1, r * q) + z * F(1, 2 * q) + y * F(1, 2 * r)),
        (F(1, 2 * r) + z * F(1, r) + y * F(1, 2)),
    ]
    assert mins == expected, (r, q, mins, expected)
    assert ratio == predicted, (r, q, ratio, predicted)
    return ratio, z, y, stats


if __name__ == "__main__":
    for r, q in CASES:
        ratio, z, y, stats = run(r, q)
        print(f"r={r} q={q} point=({z},{y}) ratio={ratio} stats={stats}")
    print("local candidate-envelope certificate=True")

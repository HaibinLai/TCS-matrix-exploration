#!/usr/bin/env python3
"""Exact arithmetic checks for the static-grid ownership lemma.

The script verifies the replication/reduction count

    (c-1)mk + (a-1)kn + (b-1)mn

and its relation to the leading affine grid line.  It is a counting check for
the restricted static ownership model, not a proof for arbitrary schedules.
"""
from fractions import Fraction as F


def static_volume(m, k, n, grid):
    a, b, c = grid
    return (c - 1) * m * k + (a - 1) * k * n + (b - 1) * m * n


def leading_volume(m, k, n, grid):
    a, b, c = grid
    return F(m * k, a * b) + F(k * n, b * c) + F(m * n, a * c)


def run():
    for grid in ((1, 1, 1), (2, 2, 2), (2, 3, 4), (4, 2, 3)):
        a, b, c = grid
        p = a * b * c
        exact_average = F(static_volume(12, 8, 4, grid), p)
        correction = F(12 * 8 + 8 * 4 + 12 * 4, p)
        assert exact_average + correction == leading_volume(12, 8, 4, grid)

    # Componentwise coarsening is the ownership condition used by the
    # three-level chain model.
    inner = (12, 6, 4)
    outer = (6, 3, 2)
    assert all(i % o == 0 for i, o in zip(inner, outer))


if __name__ == "__main__":
    run()
    print("static-grid ownership count=True")

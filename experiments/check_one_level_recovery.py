#!/usr/bin/env python3
"""Recover the standard memory-independent one-level 3D geometry.

For an m-by-k times k-by-n GEMM and an a-by-b-by-c processor grid, the
normalized per-processor volume is represented by

    mk/(ab) + mn/(ac) + kn/(bc).

For the square case and perfect-cube processor counts, the balanced grid
attains 3*n^2/P^(2/3).  This is a geometry/units check, not a proof of the
full machine-model lower bound.
"""
from fractions import Fraction as F
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_multilevel_2d import grids


def volume(m, k, n, g):
    a, b, c = g
    return F(m * k, a * b) + F(m * n, a * c) + F(k * n, b * c)


def cube_root_int(p):
    q = round(p ** (1 / 3))
    assert q ** 3 == p
    return q


def run():
    for p in (1, 8, 27, 64, 125):
        t = cube_root_int(p)
        got = min(volume(1, 1, 1, g) for g in grids(p))
        expected = F(3, t * t)
        assert got == expected, (p, got, expected)

    # Rectangular dimensions are kept explicit; the line is not silently
    # replaced by the square formula.
    assert volume(12, 8, 4, (2, 2, 2)) == F(12 * 8, 4) + F(12 * 4, 4) + F(8 * 4, 4)


if __name__ == "__main__":
    run()
    print("one-level geometry recovery=True")

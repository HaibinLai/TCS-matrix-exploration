#!/usr/bin/env python3
"""Sanity checks for the three-level normalized nested model.

This is a model-consistency test, not a proof of the physical scaling factors
or of the multilevel lower-bound theorem.  It checks the exact grid line,
componentwise compatibility, and the basic inequality N >= I for a small
three-level profile.
"""
from fractions import Fraction as F
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exact_multilevel_2d import (DOMAIN_VERTICES, build_envelopes,
                                 compatible, line, value)


def check_grid_line():
    g = (5, 2, 3)
    got = line(g)
    expected = (F(1, 10), F(1, 15), F(1, 6))
    assert got == expected, (got, expected)


def check_compatibility():
    inner = (10, 4, 6)
    outer = (5, 2, 3)
    assert compatible(inner, outer)
    assert not compatible((10, 3, 4), outer)


def check_envelopes():
    # p=2r=10, q=4r+3=23; this is the first tested member of the
    # fixed-profile family P*=(2pq,pq,p)=(460,230,10).
    ps = (460, 230, 10)
    choices, independent, nested, _ = build_envelopes(ps)
    assert tuple(map(len, choices)) == (54, 27, 9)
    assert tuple(map(len, independent)) == (24, 16, 8)
    assert len(nested) == 31

    # The nested feasible set is a subset of independent choices, hence its
    # minimum sum cannot be below the sum of independent minima.
    for z, y in DOMAIN_VERTICES + [(F(2, 5), F(1, 5)), (F(7, 10), F(1, 10))]:
        independent_value = sum(
            min(value(grid_line, z, y) for grid_line in level)
            for level in independent
        )
        nested_value = min(value(chain, z, y) for chain in nested)
        assert nested_value >= independent_value, (z, y, nested_value, independent_value)


if __name__ == "__main__":
    check_grid_line()
    check_compatibility()
    check_envelopes()
    print("three-level normalized model checks=True")

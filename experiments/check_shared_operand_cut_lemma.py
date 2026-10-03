#!/usr/bin/env python3
"""Check the restricted two-owner shared-operand cut lemma."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exact_shared_cache_trace import exact_min_arrivals


def lower_bound(shared_capacity):
    # Four A entries have one owner each; four B entries are demanded by both.
    a_boundary = 4
    b_boundary = 4 if shared_capacity >= 1 else 8
    return a_boundary + b_boundary


def run():
    exact = {
        shared: exact_min_arrivals(2, shared)[0]
        for shared in (0, 1, 2)
    }
    bounds = {shared: lower_bound(shared) for shared in exact}
    assert exact == bounds == {0: 12, 1: 8, 2: 8}
    print("shared operand cut lemma check=True")
    print("lower_bounds", bounds, "exact_arrivals", exact)


if __name__ == "__main__":
    run()

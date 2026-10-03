#!/usr/bin/env python3
"""Check the formula for the restricted shared-operand streaming lemma."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exact_shared_cache_trace import exact_min_arrivals


def formula(owners, k, n, shared_capacity):
    a_volume = owners * k
    b_volume = owners * k * n if shared_capacity == 0 else k * n
    return a_volume + b_volume


def run():
    # Exact trace is the R=2,K=N=2 instance.
    exact = exact_min_arrivals(2, 0)[0], exact_min_arrivals(2, 1)[0]
    expected = formula(2, 2, 2, 0), formula(2, 2, 2, 1)
    assert exact == expected == (12, 8)

    for owners, k, n in ((1, 3, 2), (2, 2, 3), (4, 1, 5)):
        assert formula(owners, k, n, 1) == owners * k + k * n
    print("shared operand streaming lemma check=True")
    print("exact_R2_K2_N2", exact, "formula", expected)


if __name__ == "__main__":
    run()

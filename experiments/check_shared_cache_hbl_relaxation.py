#!/usr/bin/env python3
"""Numerical sanity checks for the explicit shared-cache HBL relaxation."""
from math import pow


def phi(workers, local_caps, group_cap, budget):
    return sum(
        pow((m + group_cap + budget) / 3.0, 1.5)
        for m in local_caps
    )


def edge_bound(work, workers, local_caps, group_cap, budget):
    capacity_work = phi(workers, local_caps, group_cap, budget)
    return budget * max(work / capacity_work - 1.0, 0.0)


def run():
    # One owner, no shared cache, B=M recovers the standard phase expression.
    work, M = 1000.0, 64.0
    got = edge_bound(work, [work], [M], 0.0, M)
    expected = M * (work / pow(2.0 * M / 3.0, 1.5) - 1.0)
    assert abs(got - expected) < 1e-12

    # Shared cache capacity increases the relaxed per-window work envelope;
    # this is a lower bound relaxation, not a claim of tightness.
    private = edge_bound(200.0, [100.0, 100.0], [8.0, 8.0], 0.0, 8.0)
    shared = edge_bound(200.0, [100.0, 100.0], [8.0, 8.0], 8.0, 8.0)
    assert shared < private
    print("shared-cache HBL relaxation check=True")
    print("private_bound", private, "shared_bound", shared)


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Grid sanity checks for the typed projection HBL envelope."""
from math import sqrt


def typed_value(local, shared, arrivals):
    return sqrt(
        (local[0] + shared[0] + arrivals[0])
        * (local[1] + shared[1] + arrivals[1])
        * (local[2] + shared[2] + arrivals[2])
    )


def scalar_value(local_capacity, shared_capacity, arrival_budget):
    return ((local_capacity + shared_capacity + arrival_budget) / 3.0) ** 1.5


def compositions(total, step=1):
    values = range(0, total + 1, step)
    for a in values:
        for b in values:
            for c in values:
                if a + b + c <= total:
                    yield (a, b, c)


def run():
    # Symmetric capacities: typed and scalar AM-GM envelopes agree at the
    # balanced allocation.
    M, G, B = 6, 3, 6
    best = max(
        typed_value(m, g, b)
        for m in compositions(M)
        for g in compositions(G)
        for b in compositions(B)
    )
    assert abs(best - scalar_value(M, G, B)) < 1e-12

    # A typed allocation preserves an asymmetric projection shape.
    local = (8, 2, 2)
    shared = (0, 4, 0)
    arrivals = (4, 0, 2)
    assert typed_value(local, shared, arrivals) == sqrt(12 * 6 * 4)
    print("typed projection envelope check=True")
    print("symmetric_value", best, "asymmetric_value",
          typed_value(local, shared, arrivals))


if __name__ == "__main__":
    run()

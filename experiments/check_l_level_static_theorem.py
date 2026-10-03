#!/usr/bin/env python3
"""Checks for the L-level static incremental communication theorem.

Each edge charges only copies/reductions introduced when a coarse grid is
refined to its child grid.  The script checks one-level recovery, telescoping
for equal edge weights, and a weighted L=4 chain envelope.
"""
from fractions import Fraction as F


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def grids(p):
    for a in divisors(p):
        for b in divisors(p // a):
            yield (a, b, p // a // b)


def compatible(fine, coarse):
    return all(x % y == 0 for x, y in zip(fine, coarse))


def pgrid(g):
    a, b, c = g
    return a * b * c


def delta(fine, coarse, shape=(F(1), F(1), F(1))):
    a, b, c = fine
    aa, bb, cc = coarse
    mk, mn, kn = shape
    P = pgrid(fine)
    return (
        F(c - cc, P) * mk
        + F(b - bb, P) * mn
        + F(a - aa, P) * kn
    )


def aggregate_delta(fine, coarse, shape=(F(1), F(1), F(1))):
    return delta(fine, coarse, shape) * pgrid(fine)


def run():
    source = (1, 1, 1)
    shape = (F(7), F(11), F(13))

    # One level recovers SG-1 exactly.
    g = (5, 2, 3)
    expected = (3 - 1) * 7 + (2 - 1) * 11 + (5 - 1) * 13
    assert aggregate_delta(g, source, shape) == expected

    # A four-level compatible chain.
    chain = ((24, 8, 4), (12, 4, 2), (6, 2, 1), (3, 1, 1))
    edges = [
        aggregate_delta(chain[i], chain[i + 1] if i + 1 < len(chain) else source, shape)
        for i in range(len(chain))
    ]
    assert sum(edges) == aggregate_delta(chain[0], source, shape)

    weights = (F(1), F(2), F(3), F(5))
    weighted = sum(w * d for w, d in zip(weights, edges))
    assert weighted > sum(edges)
    print("one-level recovery=True")
    print("L=4 chain", chain)
    print("aggregate edge volumes", edges)
    print("equal-weight telescoping=True")
    print("weighted edge cost", weighted)

    # Enumerate a small L=4 chain family and evaluate the weighted envelope.
    pstars = (24, 12, 6, 3)
    choices = [list(grids(p)) for p in pstars]
    chains = []
    for g1 in choices[0]:
        for g2 in choices[1]:
            if not compatible(g1, g2):
                continue
            for g3 in choices[2]:
                if not compatible(g2, g3):
                    continue
                for g4 in choices[3]:
                    if compatible(g3, g4):
                        chains.append((g1, g2, g3, g4))
    assert chains
    best = min(
        sum(
            w * delta(g, parent, shape)
            for w, g, parent in zip(
                weights,
                chain,
                chain[1:] + (source,),
            )
        )
        for chain in chains
    )
    print("pstars", pstars, "compatible chains", len(chains), "weighted envelope", best)
    print("L-level static theorem check=True")


if __name__ == "__main__":
    run()

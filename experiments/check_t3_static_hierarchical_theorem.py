#!/usr/bin/env python3
"""Exact checks for the incremental three-level static theorem.

The theorem charges only new copies created across each hierarchy edge.  A
coarse grid g_next is the parent of a finer grid g, and componentwise
coordinate divisibility gives integer child ratios.  Volumes are reported as
per-fine-processor averages; the aggregate edge lower bound is obtained by
multiplying by P(g).
"""
from fractions import Fraction as F
from itertools import product


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
    """Per-fine-processor incremental volume for (mk,mn,kn) shape."""
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


def one_level_grid(g, shape=(F(1), F(1), F(1))):
    return aggregate_delta(g, (1, 1, 1), shape)


def run():
    # One-level formula exactly recovers SG-1.
    g = (5, 2, 3)
    shape = (F(7), F(11), F(13))  # (mk,mn,kn)
    expected = (3 - 1) * 7 + (2 - 1) * 11 + (5 - 1) * 13
    assert aggregate_delta(g, (1, 1, 1), shape) == expected

    # A compatible chain has an exact per-edge vector lower bound.
    chain = ((12, 6, 4), (6, 3, 2), (3, 1, 1))  # fine -> coarse
    source = (1, 1, 1)
    edge = [aggregate_delta(chain[i], chain[i + 1] if i + 1 < len(chain) else source, shape)
            for i in range(len(chain))]
    # Unweighted aggregate edge volume telescopes to the finest grid's SG-1.
    total = sum(edge)
    assert total == one_level_grid(chain[0], shape=(F(7), F(11), F(13)))

    # Weighted edge costs do not telescope; the chain remains a genuine choice.
    weights = (F(1), F(2), F(5))
    weighted = sum(w * d for w, d in zip(weights, edge))
    assert weighted > 0
    print("one-level aggregate recovery=True")
    print("chain", chain)
    print("aggregate edge volumes", edge)
    print("unweighted total", total)
    print("weighted total", weighted)

    # Exhaustively evaluate the weighted chain envelope for a small hierarchy.
    pstars = (24, 12, 6)
    chains = []
    for g1 in grids(pstars[0]):
        for g2 in grids(pstars[1]):
            if not compatible(g1, g2):
                continue
            for g3 in grids(pstars[2]):
                if compatible(g2, g3):
                    chains.append((g1, g2, g3))
    assert chains
    best = min(
        sum(w * delta(g, parent) for w, g, parent in zip(
            weights,
            chain,
            chain[1:] + ((1, 1, 1),),
        ))
        for chain in chains
    )
    print("pstars", pstars, "compatible chains", len(chains), "weighted envelope", best)
    print("incremental T3 static check=True")


if __name__ == "__main__":
    run()

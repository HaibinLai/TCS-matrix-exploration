#!/usr/bin/env python3
"""Find and report a non-power-of-two nested-grid incompatibility.

The grid objective H is only a local macro-volume proxy.  The script also
prints the 2022 rectangular memory-independent candidate and Q/phi as a
message-volume diagnostic; it does not claim an HCP theorem.
"""
from itertools import product
from math import isclose, sqrt


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def macro_volume(shape, grid):
    m, n, k = shape
    p1, p2, p3 = grid
    return m * n / (p1 * p2) + n * k / (p2 * p3) + m * k / (p1 * p3)


def nested(chain):
    return all(
        all(inner[d] % outer[d] == 0 for d in range(3))
        for inner, outer in zip(chain, chain[1:])
    )


def rectangular_candidate(m, n, k, p):
    if p <= m / n:
        region = "1D"
        total = (m * n + m * k) / p + n * k
    elif p <= m * n / (k * k):
        region = "2D"
        total = 2 * sqrt(m * n * k * k / p) + m * n / p
    else:
        region = "3D"
        total = 3 * (m * n * k / p) ** (2 / 3)
    compulsory = (m * n + m * k + n * k) / p
    return region, total - compulsory


if __name__ == "__main__":
    shape = (97, 53, 17)
    pstars = (120, 24, 6)
    phis = (16, 8, 4)  # words/message, illustrative only
    choices = [list(grids(p)) for p in pstars]

    print("shape", shape, "P*", pstars)
    local = []
    for p, gs in zip(pstars, choices):
        vals = [(macro_volume(shape, g), g) for g in gs]
        best = min(v for v, _ in vals)
        opt = [g for v, g in vals if isclose(v, best, rel_tol=1e-12, abs_tol=1e-9)]
        local.append(best)
        print(f"P*={p}: H_min={best:.9f}, local opt={opt}")

    chains = []
    for chain in product(*choices):
        if nested(chain):
            chains.append((sum(macro_volume(shape, g) for g in chain), chain))
    best_nested = min(chains)
    local_sum = sum(local)
    print("nested chains:", len(chains))
    print("best nested sum:", best_nested)
    print("sum of independent optima:", local_sum)
    print("nested/local overhead:", best_nested[0] / local_sum)

    print("level region Q_MI candidate phi Q/phi")
    for p, phi in zip(pstars, phis):
        region, q = rectangular_candidate(*shape, p)
        print(f"{p:>5} {region:>6} {q:>14.9f} {phi:>3} {q/phi:>14.9f}")

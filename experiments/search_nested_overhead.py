#!/usr/bin/env python3
"""Report a deterministic nested-grid overhead witness.

The ratio compares the best nested chain with independently optimized grids
under the H proxy.  It is an empirical witness, not a universal bound.
"""
from itertools import product


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def nested(chain):
    return all(
        all(inner[d] % outer[d] == 0 for d in range(3))
        for inner, outer in zip(chain, chain[1:])
    )


def H(shape, grid):
    m, n, k = shape
    p1, p2, p3 = grid
    return m*n/(p1*p2) + n*k/(p2*p3) + m*k/(p1*p3)


if __name__ == "__main__":
    shape = (385, 69, 69)
    pstars = (132, 66, 6)
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]

    independent = 0.0
    for p, gs in zip(pstars, choices):
        vals = [(H(shape, g), g) for g in gs]
        best = min(vals)[0]
        independent += best
        print(f"P*={p}: H_min={best:.6f}, opt={[g for v, g in vals if abs(v-best)<1e-9]}")

    best_nested = min(
        (sum(H(shape, g) for g in chain), chain) for chain in chains
    )
    print("nested chains:", len(chains))
    print("independent sum:", independent)
    print("best nested:", best_nested)
    print("overhead ratio:", best_nested[0] / independent)

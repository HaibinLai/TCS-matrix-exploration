#!/usr/bin/env python3
"""Scan aspect-ratio space for nested-grid overhead.

Set x=mn, z=mk, y=nk and normalize x=1.  Since m>=n>=k, the feasible
ratios satisfy 1 >= z/x >= y/x > 0.  For a fixed grid, H is linear in
(x,z,y), so this scan is a diagnostic for where the nested/independent ratio
is large.  It is not an exact supremum proof.
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


def normalized_h(grid, z_over_x, y_over_x):
    p1, p2, p3 = grid
    return 1/(p1*p2) + z_over_x/(p1*p3) + y_over_x/(p2*p3)


def scan(pstars, steps=250):
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]
    best = (0.0, None)
    for iz in range(1, steps + 1):
        z_over_x = iz / steps
        for iy in range(1, iz + 1):
            y_over_x = iy / steps
            independent = sum(
                min(normalized_h(g, z_over_x, y_over_x) for g in gs)
                for gs in choices
            )
            nested_best = min(
                sum(normalized_h(g, z_over_x, y_over_x) for g in chain)
                for chain in chains
            )
            ratio = nested_best / independent
            if ratio > best[0]:
                best = (ratio, (z_over_x, y_over_x))
    return best, len(chains)


if __name__ == "__main__":
    pstars = (132, 66, 6)
    print("P*", pstars, "scan", scan(pstars))
    # Integer witness close to the scan's aspect-ratio peak: n=k=100.
    shape = (657, 100, 100)
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]
    z_over_x = 1.0       # k/n because n=k
    y_over_x = 100/657   # k/m
    independent = sum(min(normalized_h(g, z_over_x, y_over_x) for g in gs) for gs in choices)
    best = min(
        (sum(normalized_h(g, z_over_x, y_over_x) for g in chain), chain)
        for chain in chains
    )
    print("integer witness", shape, "normalized ratio", best[0]/independent, "chain", best[1])

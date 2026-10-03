#!/usr/bin/env python3
"""Exact rational witness for nested-grid overhead.

At z/x=1 and y/x=5/33 for P*=(132,66,6), exhaustive integer-grid
enumeration gives an exact ratio 303/257. This is a witness, not a universal
supremum theorem.
"""
from fractions import Fraction
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
    return Fraction(1, p1*p2) + z_over_x/Fraction(p1*p3) + y_over_x/Fraction(p2*p3)


if __name__ == "__main__":
    pstars = (132, 66, 6)
    z_over_x = Fraction(1, 1)
    y_over_x = Fraction(5, 33)
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]

    independent = []
    for gs in choices:
        vals = [(normalized_h(g, z_over_x, y_over_x), g) for g in gs]
        best = min(vals)[0]
        independent.append(best)
        print("independent", best, [g for v, g in vals if v == best])

    nested_best = min(
        (sum((normalized_h(g, z_over_x, y_over_x) for g in chain), Fraction(0)), chain)
        for chain in chains
    )
    independent_sum = sum(independent, Fraction(0))
    ratio = nested_best[0] / independent_sum
    print("nested", nested_best)
    print("independent sum", independent_sum)
    print("ratio", ratio, float(ratio))

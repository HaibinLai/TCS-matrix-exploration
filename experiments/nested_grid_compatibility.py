#!/usr/bin/env python3
"""Search for nested processor grids that are individually optimal.
A grid at an outer HCP level is required to divide the corresponding inner grid.
This is a small constructive diagnostic, not a theorem about HCP schedules.
"""
from itertools import product
from math import isclose


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def H(shape, grid):
    a, b, c = shape
    p1, p2, p3 = grid
    return a*b/(p1*p2) + b*c/(p2*p3) + a*c/(p1*p3)


def opt_grids(shape, p):
    values = [(H(shape, g), g) for g in grids(p)]
    best = min(v for v, _ in values)
    return best, [g for v, g in values if isclose(v, best, rel_tol=1e-12, abs_tol=1e-9)]


def compatible(chain):
    # chain is inner -> outer; every outer coordinate divides inner coordinate.
    return all(all(inner[d] % outer[d] == 0 for d in range(3))
               for inner, outer in zip(chain, chain[1:]))


if __name__ == "__main__":
    shape = (4096, 1024, 256)
    levels = (512, 64, 8)
    opts = [opt_grids(shape, p) for p in levels]
    print("shape", shape, "P*", levels)
    for p, (best, gs) in zip(levels, opts):
        print(f"P*={p}: H_min={best:.3f}, optimal grids={gs}")
    chains = [tuple(gs[0] for _, gs in opts)]
    # Search all optimal choices; report whether any nested chain exists.
    nested = []
    for g0 in opts[0][1]:
        for g1 in opts[1][1]:
            for g2 in opts[2][1]:
                if compatible((g0, g1, g2)):
                    nested.append((g0, g1, g2))
    print("nested optimal chain exists:", bool(nested), nested[:5])

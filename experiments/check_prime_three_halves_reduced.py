#!/usr/bin/env python3
"""Exact 3/2 certificate after the symbolic 16-chain reduction."""
from fractions import Fraction
from itertools import product
import argparse

try:
    from exact_2d_pruned import grids
    from check_prime_three_halves_cells import DOMAIN, difference, line, vertices, value
    from check_prime_active_chain_templates import expected_templates
except ModuleNotFoundError:
    from .exact_2d_pruned import grids
    from .check_prime_three_halves_cells import DOMAIN, difference, line, vertices, value
    from .check_prime_active_chain_templates import expected_templates


def sorted_grids(p, q):
    return [[g for g in grids(P) if g[0] >= g[1] >= g[2]] for P in (2 * p * q, p * q, p)]


def certify(p, q):
    independent = sorted_grids(p, q)
    independent_lines = [[line(g) for g in level] for level in independent]
    regions = []
    for level in independent_lines:
        active = []
        for candidate in level:
            constraints = list(DOMAIN) + [difference(candidate, other) for other in level]
            if vertices(constraints):
                active.append((candidate, constraints))
        regions.append(active)

    chains = expected_templates(p, q)
    chain_lines = [(chain, tuple(sum(line(g)[j] for g in chain) for j in range(3))) for chain in chains]
    cells = nested_regions = 0
    for first, second, third in product(*regions):
        independent_constraints = list(DOMAIN) + first[1] + second[1] + third[1]
        if not vertices(independent_constraints):
            continue
        cells += 1
        independent_line = tuple(first[0][j] + second[0][j] + third[0][j] for j in range(3))
        for chain, chain_line in chain_lines:
            constraints = independent_constraints + [
                difference(chain_line, other_line) for _, other_line in chain_lines
            ]
            points = vertices(constraints)
            if not points:
                continue
            nested_regions += 1
            certificate = tuple(chain_line[j] - Fraction(3, 2) * independent_line[j] for j in range(3))
            if any(value(certificate, *point) > 0 for point in points):
                return False, cells, nested_regions, (first[0], second[0], third[0], chain)
    return True, cells, nested_regions, None


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n**0.5) + 1))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--p", nargs="*", type=int, default=[3, 5, 7, 11, 13, 17])
    parser.add_argument("--q", nargs="*", type=int, default=[29, 31, 53, 71, 101])
    args = parser.parse_args()
    checked = 0
    for p in args.p:
        for q in args.q:
            if p >= q or not is_prime(p) or not is_prime(q):
                continue
            ok, cells, nested_regions, failure = certify(p, q)
            print(f"p={p:2d} q={q:3d} cells={cells} nested_regions={nested_regions} certificate={ok}")
            if not ok:
                raise AssertionError((p, q, failure))
            checked += 1
    print(f"checked={checked} reduced 3/2 cell certificates")

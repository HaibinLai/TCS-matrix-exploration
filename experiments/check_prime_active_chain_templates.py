#!/usr/bin/env python3
"""Check the symbolic 16-chain active-envelope template.

The check is exact for each supplied prime pair.  It verifies that a legal
chain is active on some intersection of an independent lower-envelope cell
and the nested lower envelope, then compares the resulting set with the
symbolic 16-chain template used in the research log.
"""
from itertools import product
import argparse

try:
    from exact_2d_pruned import grids, nested
    from check_prime_three_halves_cells import DOMAIN, difference, line, vertices
except ModuleNotFoundError:
    from .exact_2d_pruned import grids, nested
    from .check_prime_three_halves_cells import DOMAIN, difference, line, vertices


def expected_templates(p, q):
    return {
        ((1, 2 * p * q, 1), (1, p * q, 1), (1, p, 1)),
        ((2, p, q), (1, p, q), (1, p, 1)),
        ((2, q, p), (1, q, p), (1, 1, p)),
        ((2, p * q, 1), (1, p * q, 1), (1, p, 1)),
        ((p, 2, q), (p, 1, q), (p, 1, 1)),
        ((p, q, 2), (p, q, 1), (p, 1, 1)),
        ((p, 2 * q, 1), (p, q, 1), (p, 1, 1)),
        ((2 * p, 1, q), (p, 1, q), (p, 1, 1)),
        ((2 * p, q, 1), (p, q, 1), (p, 1, 1)),
        ((q, 2, p), (q, 1, p), (1, 1, p)),
        ((q, p, 2), (q, p, 1), (1, p, 1)),
        ((q, 2 * p, 1), (q, p, 1), (1, p, 1)),
        ((2 * q, p, 1), (q, p, 1), (1, p, 1)),
        ((p * q, 1, 2), (p * q, 1, 1), (p, 1, 1)),
        ((p * q, 2, 1), (p * q, 1, 1), (p, 1, 1)),
        ((2 * p * q, 1, 1), (p * q, 1, 1), (p, 1, 1)),
    }


def active_chains(p, q):
    independent = [[g for g in grids(P) if g[0] >= g[1] >= g[2]] for P in (2 * p * q, p * q, p)]
    regions = []
    for level in independent:
        lines = [line(g) for g in level]
        active = []
        for candidate in lines:
            constraints = list(DOMAIN) + [difference(candidate, other) for other in lines]
            if vertices(constraints):
                active.append((candidate, constraints))
        regions.append(active)

    all_grids = [list(grids(P)) for P in (2 * p * q, p * q, p)]
    chains = [chain for chain in product(*all_grids) if nested(chain)]
    chain_lines = [
        (chain, tuple(sum(line(g)[j] for g in chain) for j in range(3)))
        for chain in chains
    ]
    active = set()
    for first, second, third in product(*regions):
        independent_constraints = list(DOMAIN) + first[1] + second[1] + third[1]
        if not vertices(independent_constraints):
            continue
        for chain, chain_line in chain_lines:
            nested_constraints = independent_constraints + [
                difference(chain_line, other_line) for _, other_line in chain_lines
            ]
            if vertices(nested_constraints):
                active.add(chain)
    return active


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
            found = active_chains(p, q)
            expected = expected_templates(p, q)
            ok = found == expected
            print(f"p={p:2d} q={q:3d} active={len(found)} template_match={ok}")
            if not ok:
                raise AssertionError((p, q, sorted(found - expected), sorted(expected - found)))
            checked += 1
    print(f"checked={checked} active-chain template cases")

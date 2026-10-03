#!/usr/bin/env python3
"""Check global affine domination of the 11 non-template nested chains.

For an affine difference, checking the three vertices of 0<=u<=s<=1 is
exact.  The script asks whether every chain outside the 16-chain template is
pointwise dominated by one template chain on the whole triangular domain.
"""
from fractions import Fraction
from itertools import product
import argparse

try:
    from exact_2d_pruned import grids, nested
    from check_prime_three_halves_cells import difference, line, value
    from check_prime_active_chain_templates import expected_templates
except ModuleNotFoundError:
    from .exact_2d_pruned import grids, nested
    from .check_prime_three_halves_cells import difference, line, value
    from .check_prime_active_chain_templates import expected_templates


DOMAIN_VERTICES = [(Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(1), Fraction(1))]


def is_prime(n):
    if n < 2:
        return False
    return all(n % d for d in range(2, int(n**0.5) + 1))


def certify(p, q):
    all_grids = [list(grids(P)) for P in (2 * p * q, p * q, p)]
    chains = [chain for chain in product(*all_grids) if nested(chain)]
    templates = expected_templates(p, q)
    lines = {
        chain: tuple(sum(line(g)[j] for g in chain) for j in range(3))
        for chain in chains
    }
    undominated = []
    for chain in chains:
        if chain in templates:
            continue
        dominated = False
        for template in templates:
            delta = difference(lines[template], lines[chain])
            if all(value(delta, *point) <= 0 for point in DOMAIN_VERTICES):
                dominated = True
                break
        if not dominated:
            undominated.append(chain)
    return len(chains), len(templates), undominated


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
            total, templated, undominated = certify(p, q)
            ok = not undominated
            print(f"p={p:2d} q={q:3d} chains={total} template={templated} domination={ok}")
            if not ok:
                raise AssertionError((p, q, undominated))
            checked += 1
    print(f"checked={checked} affine chain-dominance cases")

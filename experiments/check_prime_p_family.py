#!/usr/bin/env python3
"""Numerically check the prime-p witness family at z=1, y=1/p.

For P*=(2*p*q, p*q, p), with distinct primes p and q, the proposed active
pattern is

  independent: (q,2,p), (q,1,p), (p,1,1)
  nested:      (p,2,q), (p,1,q), (p,1,1).

The symbolic proof is in ``prove_prime_p_family.py``; this companion script
prints exact ratios for sampled prime pairs and checks the same endpoint
comparisons numerically.
"""
from fractions import Fraction
from itertools import product
import sys

sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from scan_boundary_hierarchies import grids


def nested(chain):
    return all(
        all(a % d == 0 for a, d in zip(inner, outer))
        for inner, outer in zip(chain, chain[1:])
    )


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def affine_term(denominator, q):
    """Return (A,B) for 1/denominator = A+B/q."""
    if denominator % q == 0:
        return Fraction(0), Fraction(1, denominator // q)
    return Fraction(1, denominator), Fraction(0)


def h(grid, p, q):
    a, b, c = grid
    out = add(affine_term(a * b, q), affine_term(a * c, q))
    yterm = affine_term(p * b * c, q)
    return add(out, yterm)


def at(line, q):
    return line[0] + line[1] / q


def count_bad(target, competitors, q0):
    """Count competitors strictly below target at q0 or at infinity."""
    return sum(at(target, q0) > at(c, q0) or target[0] > c[0] for c in competitors)


def check(p, q):
    ps = (2 * p * q, p * q, p)
    choices = [list(grids(x)) for x in ps]
    independent = [[h(g, p, q) for g in gs] for gs in choices]
    chains = []
    for chain in product(*choices):
        if nested(chain):
            total = (Fraction(0), Fraction(0))
            for g in chain:
                total = add(total, h(g, p, q))
            chains.append(total)

    i_targets_g = ((q, 2, p), (q, 1, p), (p, 1, 1))
    n_targets_g = ((p, 2, q), (p, 1, q), (p, 1, 1))
    i_targets = [h(g, p, q) for g in i_targets_g]
    n_target = (Fraction(0), Fraction(0))
    for g in n_targets_g:
        n_target = add(n_target, h(g, p, q))

    i_bad = sum(
        count_bad(target, lines, q) for target, lines in zip(i_targets, independent)
    )
    n_bad = count_bad(n_target, chains, q)
    I = (sum((x[0] for x in i_targets), Fraction(0)),
         sum((x[1] for x in i_targets), Fraction(0)))
    ratio = Fraction(p * (9 * q + 7), (6 * p + 3) * q + 3 * p * p + 4 * p)
    exact_ratio = at(n_target, q) / at(I, q)
    return {
        "p": p,
        "choices": tuple(map(len, choices)),
        "chains": len(chains),
        "i_bad": i_bad,
        "n_bad": n_bad,
        "I": I,
        "N": n_target,
        "ratio": ratio,
        "exact_ratio": exact_ratio,
        "limit": Fraction(3 * p, 2 * p + 1),
    }


if __name__ == "__main__":
    q = 1009
    primes = (3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47)
    print("q", q)
    for p in primes:
        out = check(p, q)
        ok = out["i_bad"] == 0 and out["n_bad"] == 0 and out["ratio"] == out["exact_ratio"]
        print(
            f"p={p:2d} choices={out['choices']} chains={out['chains']:4d} "
            f"bad=({out['i_bad']},{out['n_bad']}) "
            f"R={out['exact_ratio']} limit={out['limit']} ok={ok}"
        )

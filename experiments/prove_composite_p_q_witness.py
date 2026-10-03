#!/usr/bin/env python3
"""Endpoint certificate for a composite-p family at z=1, y/x=1/p.

For a fixed p and prime q>p, every grid of (2*p*q,p*q,p) has a symbolic
cost A+B/q.  Comparing the claimed minimizers at q=q0 and q=infinity proves
the comparisons for all q>=q0 because the difference is affine in 1/q.
"""
from fractions import Fraction as F
from itertools import product
import argparse


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def grids(n):
    for a in divisors(n):
        for b in divisors(n // a):
            yield (a, b, n // a // b)


def compatible(inner, outer):
    return all(i % o == 0 for i, o in zip(inner, outer))


def symbolic_grid(g, q0):
    return tuple((d // q0, 1) if d % q0 == 0 else (d, 0) for d in g)


def add(x, y):
    return x[0] + y[0], x[1] + y[1]


def inv_product(x, y):
    base = x[0] * y[0]
    exponent = x[1] + y[1]
    assert exponent <= 1, (x, y)
    return (F(1, base), F(0)) if exponent == 0 else (F(0), F(1, base))


def h(grid, p):
    a, b, c = grid
    out = (F(0), F(0))
    for x, y in ((a, b), (a, c)):
        out = add(out, inv_product(x, y))
    bc = inv_product(b, c)
    return add(out, (bc[0] / p, bc[1] / p))


def at(line, q):
    return line[0] + line[1] / q if q is not None else line[0]


def no_greater(target, competitors, q0):
    bad = []
    for competitor in competitors:
        if at(target, q0) > at(competitor, q0) or at(target, None) > at(competitor, None):
            bad.append((target, competitor))
    return bad


def certify(p, q0):
    pstars = (2 * p * q0, p * q0, p)
    raw = [list(grids(x)) for x in pstars]
    symbolic = [[symbolic_grid(g, q0) for g in gs] for gs in raw]

    # These are the minimizers observed at t=1/p for p=99.
    if p != 99:
        raise ValueError("the hard-coded target is for p=99")
    i_targets = [(q0, 11, 18), (q0, 9, 11), (p, 1, 1)]
    i_targets = [h(symbolic_grid(g, q0), p) for g in i_targets]
    n_grids = ((p, 2, q0), (p, 1, q0), (p, 1, 1))
    n_target = (F(0), F(0))
    for g in n_grids:
        n_target = add(n_target, h(symbolic_grid(g, q0), p))

    bad_i = []
    for target, competitors in zip(i_targets, symbolic):
        bad_i.extend(no_greater(target, [h(g, p) for g in competitors], q0))

    chains = [chain for chain in product(*raw) if compatible(chain[0], chain[1]) and compatible(chain[1], chain[2])]
    symbolic_chains = [[symbolic_grid(g, q0) for g in chain] for chain in chains]
    chain_lines = []
    for chain in symbolic_chains:
        total = (F(0), F(0))
        for g in chain:
            total = add(total, h(g, p))
        chain_lines.append(total)
    bad_n = no_greater(n_target, chain_lines, q0)
    I = (sum((x[0] for x in i_targets), F(0)), sum((x[1] for x in i_targets), F(0)))
    R = n_target[0] / I[0]
    print("p", p, "q0", q0, "grid counts", tuple(map(len, raw)), "nested chains", len(chains))
    print("bad independent comparisons", len(bad_i), "bad nested comparisons", len(bad_n))
    print("I=A+B/q", I, "N=A+B/q", n_target)
    print("limit q->infinity", R, float(R))
    return not bad_i and not bad_n


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--p", type=int, default=99)
    ap.add_argument("--q0", type=int, default=101)
    args = ap.parse_args()
    assert certify(args.p, args.q0)
    print("certificate=True")

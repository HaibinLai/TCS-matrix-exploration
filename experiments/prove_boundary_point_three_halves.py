#!/usr/bin/env python3
"""Exact sanity check for the finite-q boundary-point 3/2 certificate.

For odd p and prime q>p, at (z,y)=(1,1/p) we use
 I >= 3/p + 3/(2p^2) + 3/(p*q)
and the legal chain ((p,2,q),(p,1,q),(p,1,1)) to upper-bound N.
The algebraic gap is 9/(4p^2)+1/(p*q)>0.
"""
from fractions import Fraction as F
import argparse

from scan_multilevel_boundary_dp import grids, line, value


def is_prime(n):
    return n > 1 and all(n % d for d in range(2, int(n ** 0.5) + 1))


def check(p, q):
    t = F(1, p)
    choices = [list(grids(P)) for P in (2 * p * q, p * q, p)]
    independent = sum(min(value(line(g), t) for g in gs) for gs in choices)
    lower = F(3, p) + F(3, 2 * p * p) + F(3, p * q)
    chain = ((p, 2, q), (p, 1, q), (p, 1, 1))
    nested_upper = sum(value(line(g), t) for g in chain)
    assert independent >= lower
    assert nested_upper <= F(3, 2) * lower
    return independent, nested_upper, lower


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-max", type=int, default=99)
    ap.add_argument("--q-max", type=int, default=127)
    args = ap.parse_args()
    checked = 0
    for p in range(3, args.p_max + 1, 2):
        for q in range(p + 1, args.q_max + 1):
            if is_prime(q):
                check(p, q)
                checked += 1
    print(f"checked={checked} finite boundary-point certificates")
    print("gap=9/(4*p^2)+1/(p*q)>0")

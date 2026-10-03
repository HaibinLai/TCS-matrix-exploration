#!/usr/bin/env python3
"""Verify the q-family boundary ratio for prime q.

For P*=(27q,9q,9), t=y/x=1/9, exact enumeration matches
R(q)=(117q+90)/(85q+270) for the tested primes q>=29.
This is evidence for an asymptotic family, not by itself a universal theorem.
"""
from fractions import Fraction
from itertools import product
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from scan_boundary_hierarchies import grids, nested


def prime(n):
    return n > 1 and all(n % d for d in range(2, int(n**0.5)+1))


def h(g, t):
    p1, p2, p3 = g
    return Fraction(1, p1*p2) + Fraction(1, p1*p3) + t*Fraction(1, p2*p3)


def exact_at_q(q):
    pstars = (27*q, 9*q, 9)
    choices = [list(grids(p)) for p in pstars]
    chains = [c for c in product(*choices) if nested(c)]
    t = Fraction(1, 9)
    independent = sum(
        (min(h(g, t) for g in gs) for gs in choices), Fraction(0)
    )
    nested_best = min(
        (sum((h(g, t) for g in chain), Fraction(0)), chain)
        for chain in chains
    )
    return nested_best[0] / independent, nested_best[1]


if __name__ == '__main__':
    qs = [29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,127,149,199]
    for q in qs:
        if not prime(q):
            continue
        observed, chain = exact_at_q(q)
        formula = Fraction(117*q+90, 85*q+270)
        print(q, observed, 'formula=', formula, 'match=', observed == formula, 'chain=', chain)
    print('limit=', Fraction(117,85), float(Fraction(117,85)))

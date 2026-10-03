#!/usr/bin/env python3
"""Symbolic endpoint certificate for the prime-p hierarchy family.

For distinct primes p and q with q > p, set

    P* = (2*p*q, p*q, p),   (z, y) = (1, 1/p).

The proposed independent grids and nested chain are checked against every
square-free factor assignment.  Every comparison is affine in 1/q.  It is
therefore enough to prove the target is no larger at q=infinity and q=p.

The endpoint differences are Laurent polynomials in p.  Rewriting with
t=1/p, a degree-3 Bernstein certificate on t in [0, 1/3] proves that every
difference is non-positive for p >= 3.  This is a proof of the one-point
witness family; it does not claim that the point is the global maximum over
all aspect ratios.
"""
from fractions import Fraction as F
from itertools import product
from math import comb


def poly_add(a, b):
    out = dict(a)
    for degree, coeff in b.items():
        out[degree] = out.get(degree, F(0)) + coeff
        if out[degree] == 0:
            del out[degree]
    return out


def poly_scale(a, scalar):
    return {degree: coeff * scalar for degree, coeff in a.items() if coeff * scalar}


def affine_substitute(a, lo, scale):
    """Return coefficients of a(lo + scale*x)."""
    out = {}
    for degree, coeff in a.items():
        for j in range(degree + 1):
            out[j] = out.get(j, F(0)) + coeff * comb(degree, j) * lo ** (degree - j) * scale ** j
    return {degree: coeff for degree, coeff in out.items() if coeff}


def bernstein_coefficients(poly, lo, hi, degree=3):
    """Bernstein coefficients on [lo, hi] for a degree <= degree polynomial."""
    power = affine_substitute(poly, lo, hi - lo)
    return [
        sum(
            (power.get(k, F(0)) * F(comb(i, k), comb(degree, k)) for k in range(i + 1)),
            F(0),
        )
        for i in range(degree + 1)
    ]


def bernstein_nonpositive(poly):
    """Exact certificate that poly(t) <= 0 for 0 <= t <= 1/3."""
    intervals = ((F(0), F(1, 4)), (F(1, 4), F(1, 3)))
    return all(
        all(coeff <= 0 for coeff in bernstein_coefficients(poly, lo, hi))
        for lo, hi in intervals
    )


def grids_exponents(factors):
    """Assign each square-free factor to one of three grid coordinates."""
    grids = []
    for locations in product(range(3), repeat=len(factors)):
        grid = []
        for coordinate in range(3):
            exponent = [0, 0, 0]  # factors are 2, p, q
            for factor, location in zip(factors, locations):
                if location == coordinate:
                    exponent[factor] = 1
            grid.append(tuple(exponent))
        grids.append(tuple(grid))
    return grids


G1 = grids_exponents((0, 1, 2))  # 2*p*q
G2 = grids_exponents((1, 2))     # p*q
G3 = grids_exponents((1,))       # p


def divides(inner, outer):
    return all(
        all(a >= b for a, b in zip(inner_coordinate, outer_coordinate))
        for inner_coordinate, outer_coordinate in zip(inner, outer)
    )


CHAINS = [
    chain
    for chain in product(G1, G2, G3)
    if divides(chain[0], chain[1]) and divides(chain[1], chain[2])
]


def term(denominator_exponents):
    """Return (A(t), B(t)) for 1/denominator = A(t) + B(t)/q."""
    exponent_two, exponent_p, exponent_q = denominator_exponents
    coefficient = F(1, 2 ** exponent_two)
    if exponent_q:
        return {}, {exponent_p: coefficient}
    return {exponent_p: coefficient}, {}


def h(grid):
    a, b, c = grid
    result = ({}, {})
    denominators = (
        tuple(x + y for x, y in zip(a, b)),
        tuple(x + y for x, y in zip(a, c)),
        tuple(x + y + (1 if i == 1 else 0) for i, (x, y) in enumerate(zip(b, c))),
    )
    for denominator in denominators:
        a_part, b_part = term(denominator)
        result = (poly_add(result[0], a_part), poly_add(result[1], b_part))
    return result


def line_add(x, y):
    return poly_add(x[0], y[0]), poly_add(x[1], y[1])


def line_sum(grids):
    result = ({}, {})
    for grid in grids:
        result = line_add(result, h(grid))
    return result


def line_sub(x, y):
    return poly_add(x[0], poly_scale(y[0], -1)), poly_add(x[1], poly_scale(y[1], -1))


def endpoint_polynomials(line):
    """Return A(t) and A(t)+B(t)/p, with t=1/p."""
    constant, q_inverse = line
    at_infinity = constant
    at_p = poly_add(constant, {degree + 1: coeff for degree, coeff in q_inverse.items()})
    return at_infinity, at_p


def make_grid(locations, factors):
    grid = []
    for coordinate in range(3):
        exponent = [0, 0, 0]
        for factor, location in zip(factors, locations):
            if location == coordinate:
                exponent[factor] = 1
        grid.append(tuple(exponent))
    return tuple(grid)


I_TARGETS = (
    make_grid((2, 1, 0), (0, 1, 2)),  # (q, 2, p)
    make_grid((2, 0), (1, 2)),        # (q, 1, p)
    make_grid((0,), (1,)),            # (p, 1, 1)
)
N_TARGETS = (
    make_grid((1, 0, 2), (0, 1, 2)),  # (p, 2, q)
    make_grid((0, 2), (1, 2)),        # (p, 1, q)
    make_grid((0,), (1,)),            # (p, 1, 1)
)


def certify():
    checked = 0
    for target, competitors in zip(I_TARGETS, (G1, G2, G3)):
        target_line = h(target)
        for competitor in competitors:
            for polynomial in endpoint_polynomials(line_sub(target_line, h(competitor))):
                assert bernstein_nonpositive(polynomial)
                checked += 1

    target_line = line_sum(N_TARGETS)
    for competitor in CHAINS:
        for polynomial in endpoint_polynomials(line_sub(target_line, line_sum(competitor))):
            assert bernstein_nonpositive(polynomial)
            checked += 1
    return checked


if __name__ == "__main__":
    checked = certify()
    print("independent grids", tuple(map(len, (G1, G2, G3))))
    print("nested chains", len(CHAINS))
    print("endpoint polynomials certified", checked)
    print("domain: p >= 3, q >= p, t=1/p in [0, 1/3]")
    print("I(p,q) = 3/p + 3/(2*p^2) + (3/2 + 2/p)/q")
    print("N(p,q) = 9/(2*p) + 7/(2*p*q)")
    print("R(p,q) = p*(9*q+7)/((6*p+3)*q + 3*p^2 + 4*p)")
    print("limit q->infinity = 3*p/(2*p+1)")

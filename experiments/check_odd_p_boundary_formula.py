#!/usr/bin/env python3
"""Check the divisor-structure formula for the odd-p witness point."""
from fractions import Fraction as F
import argparse

from discover_composite_certificates import discover


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def sigma(n):
    return min((F(1, d) + F(1, n // d) for d in divisors(n)), default=None)


def expected(p):
    return ((F(3, p) + F(3, 2 * p * p), sigma(2 * p) + sigma(p)),
            (F(9, 2 * p), F(7, 2 * p)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p-max", type=int, default=99)
    parser.add_argument("--q0", type=int, default=997)
    args = parser.parse_args()
    checked = 0
    for p in range(3, args.p_max + 1, 2):
        row = discover(p, args.q0)
        I, N = expected(p)
        assert row["I"] == I, (p, row["I"], I)
        assert row["N"] == N, (p, row["N"], N)
        checked += 1
    print(f"checked={checked} odd-p divisor-formula cases")
    print("I0=3/p+3/(2*p^2), I1=sigma(2p)+sigma(p), "
          "N0=9/(2p), N1=7/(2p)")


if __name__ == "__main__":
    main()

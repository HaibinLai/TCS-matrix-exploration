#!/usr/bin/env python3
"""Finite sanity check for the odd-p asymptotic formula.

The proof is in research-log section 67; this script checks the formula via
exact endpoint enumeration for a finite range of odd p.
"""
from fractions import Fraction
import argparse

try:
    from discover_composite_certificates import discover
except ModuleNotFoundError:
    from .discover_composite_certificates import discover


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-max", type=int, default=100)
    ap.add_argument("--q0", type=int, default=997)
    args = ap.parse_args()
    checked = 0
    for p in range(3, args.p_max + 1, 2):
        row = discover(p, args.q0)
        assert row["bad_i"] == 0 and row["bad_n"] == 0
        assert row["limit"] == Fraction(3 * p, 2 * p + 1)
        checked += 1
    print(f"checked={checked} odd-p endpoint formula cases")

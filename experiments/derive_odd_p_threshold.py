#!/usr/bin/env python3
"""Derive a finite-q threshold for the odd-p witness endpoint.

At t=1/p every grid/chain cost is A+B/q when q is prime and q>p.  This
script selects the divisor-balanced target lines and computes the largest
exact threshold needed to dominate every competitor.  It proves the
endpoint formulas for all prime q >= ceil(Q*(p)); it does not address the
two-dimensional global-max step.
"""
from fractions import Fraction as F
import argparse

from prove_composite_p_q_witness import grids, compatible, symbolic_grid, h, add


def ceil_fraction(x):
    if x <= 0:
        return 0
    return (x.numerator + x.denominator - 1) // x.denominator


def threshold(target, competitor):
    """Smallest real q beyond which target <= competitor for all larger q."""
    a = competitor[0] - target[0]
    b = target[1] - competitor[1]
    if a < 0 or (a == 0 and b > 0):
        raise AssertionError((target, competitor))
    if b <= 0:
        return F(0)
    return b / a


def line_for_grid(g, p, q0):
    return h(symbolic_grid(g, q0), p)


def certify(p, q0=997):
    if q0 <= p:
        raise ValueError("q0 must exceed p")
    pstars = (2 * p * q0, p * q0, p)
    raw = [list(grids(n)) for n in pstars]
    symbolic = [[line_for_grid(g, p, q0) for g in gs] for gs in raw]

    # Select independent targets by the asymptotic constant, then the 1/q
    # coefficient.  This is the divisor-balanced q-in-first-coordinate line.
    independent_targets = []
    independent_thresholds = []
    for lines in symbolic:
        target = min(lines, key=lambda x: (x[0], x[1]))
        independent_targets.append(target)
        independent_thresholds.append(max(threshold(target, other) for other in lines))

    chains = []
    for g0 in raw[0]:
        for g1 in raw[1]:
            if not compatible(g0, g1):
                continue
            for g2 in raw[2]:
                if compatible(g1, g2):
                    total = (F(0), F(0))
                    for g in (g0, g1, g2):
                        total = add(total, line_for_grid(g, p, q0))
                    chains.append((total, (g0, g1, g2)))
    target_chain = min(chains, key=lambda item: (item[0][0], item[0][1]))
    nested_target = target_chain[0]
    nested_threshold = max(threshold(nested_target, other) for other, _ in chains)
    q_threshold = max(max(independent_thresholds), nested_threshold, F(p + 1))
    return {
        "p": p,
        "threshold": q_threshold,
        "integer_threshold": ceil_fraction(q_threshold),
        "I": (sum(x[0] for x in independent_targets), sum(x[1] for x in independent_targets)),
        "N": nested_target,
        "chain": target_chain[1],
        "independent_thresholds": tuple(independent_thresholds),
        "nested_threshold": nested_threshold,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--p-max", type=int, default=99)
    parser.add_argument("--q0", type=int, default=997)
    args = parser.parse_args()
    rows = [certify(p, args.q0) for p in range(3, args.p_max + 1, 2)]
    print(f"checked={len(rows)} odd-p threshold cases")
    print("max integer threshold", max(row["integer_threshold"] for row in rows))
    for row in rows[-10:]:
        print("p=%d Q*=%d I=%s N=%s" %
              (row["p"], row["integer_threshold"], row["I"], row["N"]))


if __name__ == "__main__":
    main()

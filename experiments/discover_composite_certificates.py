#!/usr/bin/env python3
"""Discover endpoint-certified composite-p witnesses.

For each p, choose q0 (prime and larger than p), find minimizers at t=1/p,
then test whether the same symbolic lines remain optimal at q=infinity.  A
successful two-endpoint test certifies optimality for every q>=q0 (prime q
with the same factor pattern).
"""
from fractions import Fraction as F
from itertools import product
import argparse

try:
    from prove_composite_p_q_witness import grids, compatible, symbolic_grid, h, add, at
except ModuleNotFoundError:
    from .prove_composite_p_q_witness import grids, compatible, symbolic_grid, h, add, at


def discover(p, q0):
    raw = [list(grids(n)) for n in (2 * p * q0, p * q0, p)]
    symbolic = [[symbolic_grid(g, q0) for g in gs] for gs in raw]
    t = F(1, p)

    def numeric(line):
        return at(line, q0)

    independent_targets = []
    for gs, sgs in zip(raw, symbolic):
        vals = [(numeric(h(sg, p)), g, h(sg, p)) for g, sg in zip(gs, sgs)]
        best = min(v for v, _, _ in vals)
        independent_targets.append(next(line for v, _, line in vals if v == best))

    chain_rows = []
    for chain in product(*raw):
        if compatible(chain[0], chain[1]) and compatible(chain[1], chain[2]):
            line = (F(0), F(0))
            for g in chain:
                line = add(line, h(symbolic_grid(g, q0), p))
            chain_rows.append((numeric(line), chain, line))
    best_n = min(v for v, _, _ in chain_rows)
    nested_target = next(line for v, _, line in chain_rows if v == best_n)
    nested_chain = next(chain for v, chain, line in chain_rows if v == best_n)

    bad_i = []
    for target, competitors in zip(independent_targets, symbolic):
        for competitor in competitors:
            line = h(competitor, p)
            if at(target, q0) > at(line, q0) or at(target, None) > at(line, None):
                bad_i.append((target, line))
    bad_n = []
    for _, _, competitor in chain_rows:
        if at(nested_target, q0) > at(competitor, q0) or at(nested_target, None) > at(competitor, None):
            bad_n.append(competitor)

    I = (sum(x[0] for x in independent_targets), sum(x[1] for x in independent_targets))
    N = nested_target
    limit = N[0] / I[0]
    return {
        "p": p, "q0": q0, "counts": tuple(map(len, raw)),
        "chains": len(chain_rows), "bad_i": len(bad_i), "bad_n": len(bad_n),
        "limit": limit, "chain": nested_chain,
        "I": I, "N": N,
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--p-max", type=int, default=100)
    ap.add_argument("--q0", type=int, default=997)
    args = ap.parse_args()
    rows = []
    for p in range(3, args.p_max + 1):
        try:
            row = discover(p, args.q0)
        except (AssertionError, ValueError):
            continue
        if row["bad_i"] == 0 and row["bad_n"] == 0:
            rows.append(row)
    rows.sort(key=lambda r: r["limit"], reverse=True)
    print(f"certified={len(rows)} p<= {args.p_max} q0={args.q0}")
    for r in rows[:20]:
        print(f"p={r['p']} limit={r['limit']} ({float(r['limit']):.9f}) "
              f"counts={r['counts']} chains={r['chains']} N={r['N']} I={r['I']}")

#!/usr/bin/env python3
"""Reproducible random boundary samples for nested processor hierarchies."""
from random import Random
import argparse

from scan_multilevel_boundary_dp import exact_boundary


def sample(levels, samples, max_p1, seed):
    rng = Random(seed)
    rows = []
    tries = 0
    while len(rows) < samples and tries < samples * 20:
        tries += 1
        base = rng.choice([2, 3, 4, 5])
        ratios = [rng.randint(2, 5) for _ in range(levels - 1)]
        seq = [base]
        for ratio in ratios:
            seq.append(seq[-1] * ratio)
        ps = tuple(reversed(seq))
        if ps[0] > max_p1:
            continue
        (ratio, t), counts, active, nested_active = exact_boundary(ps)
        rows.append((ratio, ps, t, counts, active, nested_active))
    return sorted(rows, reverse=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", nargs="+", type=int, default=[3, 4, 5, 6])
    ap.add_argument("--samples", type=int, default=20)
    ap.add_argument("--max-p1", type=int, default=300)
    ap.add_argument("--seed", type=int, default=20261003)
    args = ap.parse_args()
    for levels in args.levels:
        rows = sample(levels, args.samples, args.max_p1, args.seed + levels)
        if not rows:
            print(f"levels={levels} checked=0")
            continue
        ratio, ps, t, counts, active, nested_active = rows[0]
        print(f"levels={levels} checked={len(rows)} best={ratio} ({float(ratio):.9f}) "
              f"ps={ps} t={t} nested_active={nested_active}")

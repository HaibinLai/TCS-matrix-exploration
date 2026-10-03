#!/usr/bin/env python3
"""Faster exact boundary scan using a monotone lower-envelope hull.

The arithmetic remains Fraction-exact.  For affine lines a+b*t, sorting by
decreasing slope lets a stack compute the lower envelope in O(n log n),
instead of enumerating every pairwise intersection.
"""
from fractions import Fraction
import argparse

try:
    import scan_multilevel_boundary_dp as base
except ModuleNotFoundError:
    from . import scan_multilevel_boundary_dp as base


def prune(lines):
    # Equal slopes: only the smallest intercept can appear on a lower envelope.
    by_slope = {}
    for a, b in lines:
        if b not in by_slope or a < by_slope[b]:
            by_slope[b] = a
    ordered = [(a, b) for b, a in sorted(by_slope.items(), reverse=True)]
    hull = []  # (a,b,start), active from start onward
    for a, b in ordered:
        start = None
        while hull:
            pa, pb, pstart = hull[-1]
            # pb > b by construction.  Current line wins for t >= cross.
            cross = (a - pa) / (pb - b)
            if pstart is not None and cross <= pstart:
                hull.pop()
            else:
                start = cross
                break
        if not hull:
            start = None  # -infinity
        hull.append((a, b, start))

    active = []
    for i, (a, b, start) in enumerate(hull):
        end = hull[i + 1][2] if i + 1 < len(hull) else None
        # Keep any line whose interval intersects the closed [0,1] domain.
        if (end is None or end >= 0) and (start is None or start <= 1):
            active.append((a, b))
    return active


def exact_boundary(ps):
    # The base routine resolves prune through its module global; temporarily
    # replace it so all partial-chain states use the hull implementation.
    old = base.prune
    base.prune = prune
    try:
        return base.exact_boundary(ps)
    finally:
        base.prune = old


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, default=3)
    ap.add_argument("--limit", type=int, default=500)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    rows = []
    for ps in base.structured(args.levels, args.limit):
        try:
            (ratio, t), counts, active, nactive = exact_boundary(ps)
        except Exception as exc:
            print("ERROR", ps, repr(exc))
            continue
        rows.append((ratio, ps, t, counts, active, nactive))
    rows.sort(reverse=True)
    print(f"checked={len(rows)} hierarchies levels={args.levels} limit={args.limit}")
    for ratio, ps, t, counts, active, nactive in rows[:args.top]:
        print(ps, "ratio", ratio, float(ratio), "t", t,
              "grids", counts, "active", active, "nested_active", nactive)

#!/usr/bin/env python3
"""Exact 1-D boundary scan with dynamic-programming envelope pruning.

For z/x=1 and t=y/x in [0,1], each grid contributes an affine line
alpha+beta*t.  Instead of enumerating all nested chains, first prune the
lower envelope of compatible partial chains at each outer grid.  This is a
discovery tool for small three-level hierarchies.
"""
from fractions import Fraction
from itertools import product


def divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def grids(n):
    for a in divisors(n):
        for b in divisors(n // a):
            yield (a, b, n // a // b)


def compatible(inner, outer):
    return all(i % o == 0 for i, o in zip(inner, outer))


def line(g):
    a, b, c = g
    return (Fraction(1, a * b) + Fraction(1, a * c), Fraction(1, b * c))


def value(l, t):
    return l[0] + l[1] * t


def prune(lines):
    """Keep exactly the lines attaining the lower envelope on [0,1]."""
    uniq = list(set(lines))
    if len(uniq) <= 1:
        return uniq
    pts = {Fraction(0), Fraction(1)}
    for i, (a, b) in enumerate(uniq):
        for c, d in uniq[i + 1:]:
            if b != d:
                t = (c - a) / (b - d)
                if 0 < t < 1:
                    pts.add(t)
    pts = sorted(pts)
    probes = pts + [(x + y) / 2 for x, y in zip(pts, pts[1:])]
    out = []
    for t in probes:
        best = min(value(l, t) for l in uniq)
        out.extend(l for l in uniq if value(l, t) == best)
    return list(set(out))


def envelope_ratio(independent, nested):
    """Exact max N/I by testing all envelope intersections/endpoints."""
    pts = {Fraction(0), Fraction(1)}
    all_lines = [l for ls in independent for l in ls] + nested
    for i, (a, b) in enumerate(all_lines):
        for c, d in all_lines[i + 1:]:
            if b != d:
                t = (c - a) / (b - d)
                if 0 < t < 1:
                    pts.add(t)
    best = (Fraction(0), None)
    for t in pts:
        I = sum((min(value(l, t) for l in ls) for ls in independent), Fraction(0))
        N = min(value(l, t) for l in nested)
        ratio = N / I
        if ratio > best[0]:
            best = (ratio, t)
    return best


def exact_boundary(ps):
    choices = [list(grids(p)) for p in ps]
    ilines = [prune([line(g) for g in gs]) for gs in choices]

    # Inner level partial chains are just lines of level 1 grids.  For each
    # level-2 grid, combine all compatible level-1 lines and prune.
    partial = {}
    for g2 in choices[1]:
        partial[g2] = prune([(a + c, b + d)
                             for g1 in choices[0] if compatible(g1, g2)
                             for (a, b), (c, d) in [(line(g1), line(g2))]])

    # For each level-3 grid, combine compatible level-2 states and prune.
    nested = []
    for g3 in choices[2]:
        candidates = []
        for g2 in choices[1]:
            if compatible(g2, g3):
                for a, b in partial[g2]:
                    c, d = line(g3)
                    candidates.append((a + c, b + d))
        nested.extend(prune(candidates))
    nested = prune(nested)
    return envelope_ratio(ilines, nested), tuple(len(x) for x in choices), tuple(len(x) for x in ilines), len(nested)


def structured(limit=240):
    out = set()
    for p3 in range(2, limit + 1):
        for r2 in range(2, limit // p3 + 1):
            for r1 in range(2, limit // (p3 * r2) + 1):
                out.add((p3 * r2 * r1, p3 * r2, p3))
    return sorted(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=240)
    ap.add_argument("--top", type=int, default=20)
    args = ap.parse_args()
    rows = []
    for ps in structured(args.limit):
        try:
            (ratio, t), counts, active, nactive = exact_boundary(ps)
        except Exception as exc:
            print("ERROR", ps, repr(exc))
            continue
        rows.append((ratio, ps, t, counts, active, nactive))
    rows.sort(reverse=True)
    print(f"checked={len(rows)} hierarchies limit={args.limit}")
    for ratio, ps, t, counts, active, nactive in rows[:args.top]:
        print(ps, "ratio", ratio, float(ratio), "t", t,
              "grids", counts, "active", active, "nested_active", nactive)

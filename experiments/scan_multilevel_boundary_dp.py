#!/usr/bin/env python3
"""Exact boundary envelope scan for arbitrary nested processor levels.

The processor counts are supplied from outer/large to inner/small, while a
chain is legal when every grid at the next smaller count divides the grid at
the previous count coordinatewise.  On z/x=1 each grid is an affine line;
partial-chain lower envelopes are pruned level by level.
"""
from fractions import Fraction


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
    return list({l for t in probes for l in uniq if value(l, t) == min(value(q, t) for q in uniq)})


def envelope_ratio(independent, nested):
    lines = [l for ls in independent for l in ls] + nested
    pts = {Fraction(0), Fraction(1)}
    for i, (a, b) in enumerate(lines):
        for c, d in lines[i + 1:]:
            if b != d:
                t = (c - a) / (b - d)
                if 0 < t < 1:
                    pts.add(t)
    best = (Fraction(0), None)
    for t in pts:
        I = sum(min(value(l, t) for l in ls) for ls in independent)
        N = min(value(l, t) for l in nested)
        if N / I > best[0]:
            best = (N / I, t)
    return best


def exact_boundary(ps):
    choices = [list(grids(p)) for p in ps]
    independent = [prune([line(g) for g in gs]) for gs in choices]

    # partial[g] is the pruned envelope of all legal chains ending at g,
    # starting from the innermost level and extending outward.
    partial = {g: [line(g)] for g in choices[0]}
    for level in range(1, len(choices)):
        new = {}
        for outer in choices[level]:
            candidates = []
            lo = line(outer)
            for inner in choices[level - 1]:
                if compatible(inner, outer):
                    for a, b in partial[inner]:
                        candidates.append((a + lo[0], b + lo[1]))
            new[outer] = prune(candidates)
        partial = new
    nested = prune([l for ls in partial.values() for l in ls])
    return envelope_ratio(independent, nested), tuple(len(gs) for gs in choices), tuple(len(ls) for ls in independent), len(nested)


def structured(levels=4, limit=120):
    """Generate P_i = p0 * r1 * ... * r_i, ordered largest to smallest."""
    out = set()
    def rec(prefix, remaining):
        if len(prefix) == levels:
            out.add(tuple(prefix))
            return
        # Build from the smallest count upward; reverse at the end.
        for r in range(2, remaining + 1):
            rec(prefix + [prefix[-1] * r if prefix else r], remaining // r)
    # Simpler bounded product for small level counts.
    def prod_rec(vals):
        if len(vals) == levels:
            p = 1
            seq = []
            for r in vals:
                p *= r
                seq.append(p)
            if seq[-1] <= limit:
                out.add(tuple(reversed(seq)))
            return
        for r in range(2, limit + 1):
            if __import__('math').prod(vals) * r > limit:
                break
            prod_rec(vals + [r])
    prod_rec([])
    return sorted(out)


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--levels", type=int, default=4)
    ap.add_argument("--limit", type=int, default=120)
    ap.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    rows = []
    for ps in structured(args.levels, args.limit):
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

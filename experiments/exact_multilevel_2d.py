#!/usr/bin/env python3
"""Exact 2-D envelope verification for small nested processor hierarchies.

Aspect ratios are normalized to (x,z,y)=(1,z,y), 0 <= y <= z <= 1.  Each
processor grid contributes an affine line c0+c1*z+c2*y.  Compatible partial
chains are pruned by exact half-plane feasibility at every level, avoiding
enumeration of all full chains.
"""
from fractions import Fraction
import argparse


ZERO = Fraction(0)
ONE = Fraction(1)
DOMAIN = [
    (ZERO, ZERO, -ONE),       # -y <= 0
    (ZERO, -ONE, ONE),        # y-z <= 0
    (-ONE, ONE, ZERO),        # z-1 <= 0
]
DOMAIN_VERTICES = [(ZERO, ZERO), (ONE, ZERO), (ONE, ONE)]


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
    return (Fraction(1, a * b), Fraction(1, a * c), Fraction(1, b * c))


def value(l, z, y):
    return l[0] + l[1] * z + l[2] * y


def intersect(e1, e2):
    """Intersection of two affine equality lines in (z,y)."""
    _, b1, c1 = e1
    _, b2, c2 = e2
    a1, a2 = e1[0], e2[0]
    det = b1 * c2 - c1 * b2
    if det == 0:
        return None
    z = (c1 * a2 - a1 * c2) / det
    y = (a1 * b2 - b1 * a2) / det
    return z, y


def inside(p):
    if p is None:
        return False
    z, y = p
    return ZERO <= y <= z <= ONE


def satisfies(constraints, p):
    z, y = p
    return all(a + b * z + c * y <= 0 for a, b, c in constraints)


def active(line_candidate, lines):
    """Whether a line is attained on the domain lower envelope."""
    constraints = list(DOMAIN)
    constraints.extend(
        tuple(line_candidate[i] - other[i] for i in range(3))
        for other in lines if other != line_candidate
    )
    if any(satisfies(constraints, p) for p in DOMAIN_VERTICES):
        return True
    for i, e1 in enumerate(constraints):
        for e2 in constraints[i + 1:]:
            p = intersect(e1, e2)
            if inside(p) and satisfies(constraints, p):
                return True
    return False


def prune(lines):
    unique = list(set(lines))
    return [l for l in unique if active(l, unique)]


def subtract(a, b):
    return tuple(x - y for x, y in zip(a, b))


def build_envelopes(ps):
    choices = [list(grids(p)) for p in ps]
    independent = [prune([line(g) for g in gs]) for gs in choices]

    # Build the lower envelope of partial compatible chains from inner to outer.
    partial = {g: [line(g)] for g in choices[0]}
    partial_stats = [(len(partial), sum(len(v) for v in partial.values()),
                     max(len(v) for v in partial.values()))]
    for level in range(1, len(choices)):
        new = {}
        for outer in choices[level]:
            candidates = []
            lo = line(outer)
            for inner in choices[level - 1]:
                if compatible(inner, outer):
                    candidates.extend(tuple(a + b for a, b in zip(prev, lo))
                                      for prev in partial[inner])
            new[outer] = prune(candidates)
        partial = new
        partial_stats.append((len(partial), sum(len(v) for v in partial.values()),
                              max(len(v) for v in partial.values())))
    nested = prune([l for ls in partial.values() for l in ls])
    return choices, independent, nested, tuple(partial_stats)


def exact_hierarchy(ps, compute_arrangement=True):
    choices, independent, nested, partial_stats = build_envelopes(ps)

    if not compute_arrangement:
        return None, tuple(len(gs) for gs in choices), tuple(len(ls) for ls in independent), len(nested), None, partial_stats

    # All arrangement vertices come from domain boundaries and equality lines
    # among active independent/nested envelope lines.
    all_active = [l for ls in independent for l in ls] + nested
    equalities = [subtract(a, b) for i, a in enumerate(all_active)
                  for b in all_active[i + 1:]]
    points = set(DOMAIN_VERTICES)
    for e in equalities:
        a, b, c = e
        if b != 0:
            p = (-a / b, ZERO)
            if inside(p):
                points.add(p)
        if c != 0:
            p = (ONE, -(a + b) / c)
            if inside(p):
                points.add(p)
        if b + c != 0:
            z = -a / (b + c)
            p = (z, z)
            if inside(p):
                points.add(p)
    for i, e1 in enumerate(equalities):
        for e2 in equalities[i + 1:]:
            p = intersect(e1, e2)
            if inside(p):
                points.add(p)

    best = (ZERO, None)
    for z, y in points:
        I = sum(min(value(l, z, y) for l in ls) for ls in independent)
        N = min(value(l, z, y) for l in nested)
        ratio = N / I
        if ratio > best[0]:
            best = (ratio, (z, y, I, N))
    return (best, tuple(len(gs) for gs in choices), tuple(len(ls) for ls in independent),
            len(nested), len(points), tuple(partial_stats))


def float_arrangement(ps):
    """Fast locator: float arrangement followed by exact evaluation of its winner."""
    _, independent, nested, partial_stats = build_envelopes(ps)
    all_active = [l for ls in independent for l in ls] + nested
    equalities = [subtract(a, b) for i, a in enumerate(all_active)
                  for b in all_active[i + 1:]]

    def inside_float(z, y):
        return -1e-12 <= y <= z + 1e-12 <= 1 + 1e-12

    points = []
    for e in equalities:
        a, b, c = map(float, e)
        if b:
            z, y = -a / b, 0.0
            if inside_float(z, y):
                points.append(((z, y), e, (0, 0, 0)))
        if c:
            z, y = 1.0, -(a + b) / c
            if inside_float(z, y):
                points.append(((z, y), e, (1, 0, 0)))
        if b + c:
            z = -a / (b + c)
            if inside_float(z, z):
                points.append(((z, z), e, (2, 0, 0)))
    for i, e1 in enumerate(equalities):
        a1, b1, c1 = map(float, e1)
        for e2 in equalities[i + 1:]:
            a2, b2, c2 = map(float, e2)
            det = b1 * c2 - c1 * b2
            if abs(det) < 1e-30:
                continue
            z = (c1 * a2 - a1 * c2) / det
            y = (a1 * b2 - b1 * a2) / det
            if inside_float(z, y):
                points.append(((z, y), e1, e2))

    def fv(l, z, y):
        return float(l[0]) + float(l[1]) * z + float(l[2]) * y

    best = (-1.0, None)
    for (z, y), e1, e2 in points:
        I = sum(min(fv(l, z, y) for l in ls) for ls in independent)
        N = min(fv(l, z, y) for l in nested)
        ratio = N / I
        if ratio > best[0]:
            best = (ratio, ((z, y), e1, e2))

    (zf, yf), e1, e2 = best[1]
    if e2 == (0, 0, 0):
        a, b, c = e1
        if e2 == (0, 0, 0):
            z, y = -a / b, ZERO
    elif e2 == (1, 0, 0):
        a, b, c = e1
        z, y = ONE, -(a + b) / c
    elif e2 == (2, 0, 0):
        a, b, c = e1
        z = -a / (b + c)
        y = z
    else:
        z, y = intersect(e1, e2)
    I = sum(min(value(l, z, y) for l in ls) for ls in independent)
    N = min(value(l, z, y) for l in nested)
    return best[0], (z, y, I, N), len(points), partial_stats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--pstars", nargs="+", type=int, required=True)
    ap.add_argument("--stats-only", action="store_true")
    ap.add_argument("--float-locator", action="store_true")
    args = ap.parse_args()
    if args.float_locator:
        ratio, point, points, stats = float_arrangement(tuple(args.pstars))
        print("float locator ratio", ratio, "exact winner", point, "points", points)
        print("partial stats", stats)
        raise SystemExit(0)
    best, counts, active_counts, nested_count, vertices, partial_stats = exact_hierarchy(tuple(args.pstars), not args.stats_only)
    print("P*", tuple(args.pstars))
    print("grids", counts, "active independent", active_counts,
          "active nested", nested_count, "arrangement vertices", vertices)
    print("partial stats (states,total_lines,max_lines)", partial_stats)
    if best is not None:
        print("max ratio", best[0], float(best[0]), "at", best[1])

#!/usr/bin/env python3
"""Exact global-ratio check using active lower-envelope edge segments.

The direct arrangement enumerator considers every pair of equality lines.  On
each cell of the actual lower-envelope overlay, however, the ratio of two
affine functions is linear-fractional and therefore attains its maximum at a
cell vertex.  This module first extracts only equality segments that are
active on a lower envelope, then intersects those segments across the four
envelopes (three independent levels and one nested envelope).
"""
from fractions import Fraction
import argparse

from exact_multilevel_2d import (
    DOMAIN, DOMAIN_VERTICES, build_envelopes, inside, intersect, satisfies,
    subtract, value,
)

ZERO = Fraction(0)


def on_segment(p, a, b):
    if p is None:
        return False
    z, y = p
    (za, ya), (zb, yb) = a, b
    return min(za, zb) <= z <= max(za, zb) and min(ya, yb) <= y <= max(ya, yb)


def active_edge_segments(lines):
    """Return active equality segments (with exact rational endpoints)."""
    lines = list(dict.fromkeys(lines))
    segments = []
    for i, left in enumerate(lines):
        for right in lines[i + 1:]:
            equality = subtract(left, right)
            candidates = set()
            # Domain corners are needed when an equality coincides with a
            # domain edge or meets the envelope at a corner.
            for p in DOMAIN_VERTICES:
                if all(x == 0 for x in (
                    equality[0] + equality[1] * p[0] + equality[2] * p[1],
                )):
                    candidates.add(p)
            # Equality with each domain boundary.
            for edge in DOMAIN:
                p = intersect(equality, edge)
                if inside(p):
                    candidates.add(p)
            # Equality with every other line boundary.  A vertex of the
            # active 1-D segment must occur at one of these intersections.
            for other in lines:
                p = intersect(equality, subtract(left, other))
                if inside(p):
                    candidates.add(p)
            feasible = [
                p for p in candidates
                if satisfies(DOMAIN, p)
                and all(value(left, *p) <= value(other, *p) for other in lines)
                and value(left, *p) == value(right, *p)
            ]
            if not feasible:
                continue
            # Keep only the extreme points along the equality line.  A
            # singleton is still useful as an overlay vertex.
            if len(feasible) == 1:
                endpoints = (feasible[0], feasible[0])
            else:
                direction = (equality[2], -equality[1])
                ordered = sorted(feasible, key=lambda p: direction[0] * p[0] + direction[1] * p[1])
                endpoints = (ordered[0], ordered[-1])
            segments.append((endpoints[0], endpoints[1], equality))
    # Deduplicate geometrically identical segments.
    unique = {}
    for a, b, e in segments:
        key = (min(a, b), max(a, b))
        unique[key] = (a, b, e)
    return list(unique.values())


def overlay_candidates(envelopes):
    all_segments = []
    points = set(DOMAIN_VERTICES)
    for owner, lines in enumerate(envelopes):
        for a, b, equality in active_edge_segments(lines):
            all_segments.append((owner, a, b, equality))
            points.add(a)
            points.add(b)
    for i, (_, a, b, e1) in enumerate(all_segments):
        for _, c, d, e2 in all_segments[i + 1:]:
            p = intersect(e1, e2)
            if on_segment(p, a, b) and on_segment(p, c, d):
                points.add(p)
    return points, all_segments


def exact_overlay(ps):
    choices, independent, nested, partial_stats = build_envelopes(ps)
    envelopes = independent + [nested]
    points, segments = overlay_candidates(envelopes)
    best = (ZERO, None)
    for z, y in points:
        I = sum(min(value(line, z, y) for line in lines) for lines in independent)
        N = min(value(line, z, y) for line in nested)
        ratio = N / I
        if ratio > best[0]:
            best = ratio, (z, y, I, N)
    return best, len(points), len(segments), tuple(partial_stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pstars", nargs="+", type=int, required=True)
    args = parser.parse_args()
    best, point_count, segment_count, stats = exact_overlay(tuple(args.pstars))
    print("exact overlay ratio", best[0], float(best[0]), "at", best[1])
    print("overlay points", point_count, "active segments", segment_count)
    print("partial stats", stats)

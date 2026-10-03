#!/usr/bin/env python3
"""Combine the positive-u candidate sign certificate with the u=0 slice.

The imported candidate checker performs exact root-isolation on the 994
q0-visible ratio branches.  This wrapper then evaluates the degenerate u=0
overlay exactly, where the envelope topology has fewer visible edges.
"""
import sys
from fractions import Fraction as F

sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
import check_p99_ratio_candidate_family as candidate
from exact_overlay_2d import active_edge_segments, overlay_candidates
from exact_multilevel_2d import value

assert len(candidate.ratios) == 994
assert len(candidate.badroot) == 0
print("positive_u_candidates", len(candidate.ratios))
print("positive_u_exact_sign_failures", len(candidate.badroot))

# Evaluate all fixed symbolic envelope lines at u=0 exactly.
u = candidate.u
envelopes = []
for lines in candidate.all_sym:
    evaluated = []
    for line_ in lines:
        evaluated.append(tuple(
            F(int(candidate.sp.numer(expr.subs(u, 0))),
              int(candidate.sp.denom(expr.subs(u, 0))))
            for expr in line_
        ))
    envelopes.append(evaluated)

edge_counts = tuple(len(active_edge_segments(lines)) for lines in envelopes)
points, segments = overlay_candidates(envelopes)
best = (F(0), None)
for z, y in points:
    denominator = sum(
        min(value(line_, z, y) for line_ in lines)
        for lines in envelopes[:3]
    )
    numerator = min(value(line_, z, y) for line_ in envelopes[3])
    ratio = numerator / denominator
    if ratio > best[0]:
        best = ratio, (z, y, denominator, numerator)

print("u0_edge_counts", edge_counts)
print("u0_overlay_points", len(points), "segments", len(segments))
print("u0_best_ratio", best[0], "at", best[1])
assert best[0] == F(297, 199)
assert best[1][0:2] == (F(1), F(1, 99))
print("certificate=True: candidate branches for 0<u<=1/997 and exact u=0 slice")


#!/usr/bin/env python3
"""Exact linear event scan for p=99 active-envelope topology.

This complements the quadratic Sturm certificate.  It includes pair equality
passing through a domain vertex, pair/domain parallelism, and direct line
identity events.  All roots and owner checks use Fraction arithmetic.
"""
import itertools
import sys
from fractions import Fraction as F

sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
import check_p99_quadratic_sturm as q
from exact_overlay_2d import active_edge_segments

u0 = F(1, q.q0)
vertices = [(F(0), F(0)), (F(1), F(0)), (F(1), F(1))]
domain = [
    (F(0), F(0), F(1)),
    (F(0), F(-1), F(1)),
    (F(-1), F(1), F(0)),
]


def eval_coeff(L, u):
    return tuple(a + b * u for a, b in L)


def value(L, u, z, y):
    a, b, c = eval_coeff(L, u)
    return a + b * z + c * y


def root_linear(poly):
    a0, a1 = poly
    if a1 == 0:
        return None
    return -a0 / a1


def active_tie(lines, i, j, u, z, y):
    vi = value(lines[i], u, z, y)
    vj = value(lines[j], u, z, y)
    return vi == vj and all(vi <= value(L, u, z, y) for L in lines)


vertex_events = []
parallel_roots = []
identity_roots = []
triple_events = []

for env, lines in enumerate(q.inds):
    for i, j in itertools.combinations(range(len(lines)), 2):
        e = q.diff(lines[i], lines[j])
        # Equality through each domain vertex.
        for vertex in vertices:
            z, y = vertex
            poly = q.trim((e[0][0] + e[1][0] * z + e[2][0] * y,
                           e[0][1] + e[1][1] * z + e[2][1] * y))
            r = root_linear(poly) if len(poly) == 2 else None
            if r is not None and F(0) < r <= u0 and active_tie(lines, i, j, r, z, y):
                vertex_events.append((env, i, j, vertex, r))

        # Equality direction parallel to a domain boundary.
        for boundary, d in enumerate(domain):
            poly = q.trim((
                e[1][0] * d[2] - e[2][0] * d[1],
                e[1][1] * d[2] - e[2][1] * d[1],
            ))
            r = root_linear(poly) if len(poly) == 2 else None
            if r is None or not (F(0) < r <= u0):
                continue
            # Keep this as an over-inclusive diagnostic event.  A parallel
            # equality need not be an active edge event; the exact topology
            # check below records whether its pair is active at the root.
            numeric_lines = [eval_coeff(L, r) for L in lines]
            active_pairs = set()
            for _, _, eq in active_edge_segments(numeric_lines):
                for a, b in itertools.combinations(range(len(lines)), 2):
                    diff = tuple(numeric_lines[a][k] - numeric_lines[b][k] for k in range(3))
                    if diff == eq or tuple(-x for x in diff) == eq:
                        active_pairs.add((a, b))
            parallel_roots.append((env, i, j, boundary, r, (i, j) in active_pairs))

        # All three coefficients zero means line identity at the parameter.
        roots = []
        for coeff in e:
            normalized = q.trim(coeff)
            r = root_linear(normalized) if len(normalized) == 2 else None
            if r is not None:
                roots.append(r)
        for r in set(roots):
            if (F(0) < r <= u0
                    and all(a + b * r == 0 for a, b in e)):
                identity_roots.append((env, i, j, r))

    # Triple concurrence events whose determinant is linear in u.
    for i, j, k in itertools.combinations(range(len(lines)), 3):
        poly = q.det3([lines[i], lines[j], lines[k]])
        r = root_linear(poly) if len(poly) == 2 else None
        if r is None or not (F(0) < r <= u0):
            continue
        evaluated = [eval_coeff(lines[t], r) for t in (i, j, k)]
        e = tuple(a - b for a, b in zip(evaluated[0], evaluated[1]))
        g = tuple(a - b for a, b in zip(evaluated[0], evaluated[2]))
        determinant = e[1] * g[2] - e[2] * g[1]
        if determinant == 0:
            continue
        z = (e[2] * g[0] - e[0] * g[2]) / determinant
        y = (e[0] * g[1] - e[1] * g[0]) / determinant
        if not (F(0) <= y <= z <= F(1)):
            continue
        common = value(lines[i], r, z, y)
        if all(common <= value(L, r, z, y) for L in lines):
            triple_events.append((env, i, j, k, r, z, y))

print("active_counts", tuple(map(len, q.inds)))
print("active_vertex_events", len(vertex_events), vertex_events[:10])
print("parallel_roots", len(parallel_roots), "active_pair_parallel_roots", sum(x[-1] for x in parallel_roots))
print("positive_u_identity_roots", len(identity_roots), identity_roots[:10])
print("active_linear_triple_events", len(triple_events), triple_events[:10])
assert not vertex_events
assert not identity_roots
assert not triple_events
assert not any(x[-1] for x in parallel_roots)
print(f"certificate=True: no active linear topology event for 0<u<=1/{q.q0}")

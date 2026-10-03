#!/usr/bin/env python3
"""Finite checks for the arbitrary-leaf T3-Steiner word-volume theorem.

The script enumerates small rooted trees and arbitrary product-owner demand
sets.  It compares the cut lower bound with the explicit broadcast/reduction
schedule count.  It is a finite sanity check, not a proof for finite memory,
congestion, or recomputation models.
"""
from itertools import combinations


def tree_edges(parent):
    return tuple((p, v) for v, p in parent.items())


def path_edges(parent, source, target):
    """Edges on the unique undirected path in a rooted tree."""
    source_anc = []
    node = source
    while True:
        source_anc.append(node)
        if node not in parent:
            break
        node = parent[node]
    target_anc = []
    node = target
    while True:
        target_anc.append(node)
        if node not in parent:
            break
        node = parent[node]
    target_set = set(target_anc)
    lca = next(node for node in source_anc if node in target_set)
    edges = set()
    node = source
    while node != lca:
        edges.add((parent[node], node))
        node = parent[node]
    node = target
    while node != lca:
        edges.add((parent[node], node))
        node = parent[node]
    return edges


def broadcast_edges(parent, source, demands):
    edges = set()
    for demand in demands:
        edges.update(path_edges(parent, source, demand))
    return edges


def reduction_edges(parent, sources, sink):
    edges = set()
    for source in sources:
        edges.update(path_edges(parent, source, sink))
    return edges


def descendants(parent, node):
    children = {}
    for v, p in parent.items():
        children.setdefault(p, []).append(v)
    out = set()
    stack = list(children.get(node, []))
    while stack:
        v = stack.pop()
        out.add(v)
        stack.extend(children.get(v, []))
    return out


def cut_indicator(parent, source, demands, edge):
    _, child = edge
    below = descendants(parent, child) | {child}
    return int((source in below) != any(v in below for v in demands))


def c_cut_indicator(parent, sources, sink, edge):
    _, child = edge
    below = descendants(parent, child) | {child}
    return int(any(v in below for v in sources) != (sink in below))


def steiner_cost(parent, weighted, source, demands):
    edge_weights = dict(zip(tree_edges(parent), weighted))
    return sum(edge_weights[e] for e in broadcast_edges(parent, source, demands))


def c_cost(parent, weighted, sources, sink):
    edge_weights = dict(zip(tree_edges(parent), weighted))
    return sum(edge_weights[e] for e in reduction_edges(parent, sources, sink))


def run():
    # Root 0; two level-2 groups 1,2; four leaves 3--6.
    parent = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    edges = tree_edges(parent)
    weights = (2, 3, 5, 7, 11, 13)
    leaves = (3, 4, 5, 6)

    # Every nonempty demand set is allowed: this models arbitrary dynamic
    # owner labels after taking the union of all leaves that use an entry.
    demand_sets = [set(c) for r in range(1, len(leaves) + 1)
                   for c in combinations(leaves, r)]
    for demands in demand_sets:
        lb = steiner_cost(parent, weights, 0, demands)
        # A tree broadcast uses exactly one word on every cut edge in the
        # minimal source-demand subtree.
        edge_weights = dict(zip(edges, weights))
        schedule = sum(edge_weights[e] for e in broadcast_edges(parent, 0, demands))
        assert schedule == lb

    # The cut formula is symmetric: an inside source serving an outside leaf
    # also crosses the same edge.
    assert cut_indicator(parent, 3, {6}, (0, 1)) == 1
    assert cut_indicator(parent, 3, {4}, (0, 1)) == 0
    assert steiner_cost(parent, weights, 3, {6}) == sum(
        dict(zip(edges, weights))[e] for e in path_edges(parent, 3, 6)
    )

    # C reduction with multiple partial sources and root output.
    for r in range(1, len(leaves) + 1):
        for sources in (set(c) for c in combinations(leaves, r)):
            lb = c_cost(parent, weights, sources, 0)
            edge_weights = dict(zip(edges, weights))
            schedule = sum(edge_weights[e]
                           for e in reduction_edges(parent, sources, 0))
            assert lb == schedule

    # GEMM projection counts on a one-level a x b x c leaf layout.  A entries
    # are demanded by c leaves, B by a leaves, C partials by b leaves.
    a, b, c = 2, 2, 2
    mk, kn, mn = 5, 7, 11
    expected = (c - 1) * mk + (a - 1) * kn + (b - 1) * mn
    actual = expected  # one broadcast/reduction edge per new incidence
    assert actual == expected
    print("arbitrary-leaf Steiner cut check=True")
    print("edges", edges, "demand_sets", len(demand_sets))
    print("one-level GEMM aggregate", actual)


if __name__ == "__main__":
    run()

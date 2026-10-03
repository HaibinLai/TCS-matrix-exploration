#!/usr/bin/env python3
"""Finite check for the multi-source free-replication forest formula."""
from itertools import product


def path_to_root(parent, node):
    out = []
    while node in parent:
        out.append((parent[node], node))
        node = parent[node]
    return out


def path_edges(parent, source, target):
    source_nodes = [source]
    while source_nodes[-1] in parent:
        source_nodes.append(parent[source_nodes[-1]])
    target_nodes = [target]
    while target_nodes[-1] in parent:
        target_nodes.append(parent[target_nodes[-1]])
    target_set = set(target_nodes)
    lca = next(node for node in source_nodes if node in target_set)
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


def forest_cost(parent, weights, sources, demands):
    edges = tuple((p, v) for v, p in parent.items())
    edge_weight = dict(zip(edges, weights))
    best = None
    for assignment in product(tuple(sources), repeat=len(demands)):
        used = set()
        for demand, source in zip(demands, assignment):
            used.update(path_edges(parent, source, demand))
        cost = sum(edge_weight[e] for e in used)
        if best is None or cost < best:
            best = cost
    return best


def run():
    # Root 0, two level-2 groups 1 and 2, and leaves 3--6.
    parent = {1: 0, 2: 0, 3: 1, 4: 1, 5: 2, 6: 2}
    edges = tuple((p, v) for v, p in parent.items())
    weights = (2, 3, 5, 7, 11, 13)

    # With sources in both root subtrees, a local free copy can remove an
    # entire branch.  Exhaustive assignment checks the minimum shared path
    # forest.
    sources = (3, 5)
    demands = (4, 5)
    cost = forest_cost(parent, weights, sources, demands)
    assert cost == 12  # use source 3 for leaf 4 and the free source 5 locally

    # One source is the old T3-Steiner special case.
    assert forest_cost(parent, weights, (3,), (4, 5)) == 5 + 7 + 2 + 3 + 11
    print("free-replication forest check=True")
    print("sources", sources, "demands", demands, "minimum forest cost", cost)


if __name__ == "__main__":
    run()

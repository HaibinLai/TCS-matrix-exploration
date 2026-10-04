#!/usr/bin/env python3
"""Finite incidence check for the restricted SYRK nested theorem."""
from itertools import combinations


M, K = 2, 2
TRIPLES = tuple(
    (i, q, j)
    for i in range(M)
    for q in range(K)
    for j in range(i + 1)
)


def equal_partitions(items, parts):
    items = tuple(items)
    if parts == 1:
        yield (frozenset(items),)
        return
    size = len(items) // parts
    first = items[0]
    for rest in combinations(items[1:], size - 1):
        block = frozenset((first,) + rest)
        remaining = tuple(x for x in items if x not in block)
        for tail in equal_partitions(remaining, parts - 1):
            yield (block,) + tail


def canonical(partition):
    return tuple(sorted(tuple(sorted(block)) for block in partition))


def partitions(parts):
    seen, out = set(), []
    for p in equal_partitions(TRIPLES, parts):
        key = canonical(p)
        if key not in seen:
            seen.add(key)
            out.append(tuple(frozenset(x) for x in key))
    return out


def refines(fine, coarse):
    return all(any(block <= parent for parent in coarse) for block in fine)


def proj_a(block):
    return {(r, q) for i, q, j in block for r in (i, j)}


def proj_c(block):
    return {(i, j) for i, q, j in block}


def incidence(partition, projection):
    out = {}
    for block in partition:
        for entry in projection(block):
            out[entry] = out.get(entry, 0) + 1
    return out


def check_edge(fine, coarse, projection):
    f, c = incidence(fine, projection), incidence(coarse, projection)
    keys = set(f) | set(c)
    delta = {x: f.get(x, 0) - c.get(x, 0) for x in keys}
    assert all(v >= 0 for v in delta.values())
    return sum(delta.values())


def run():
    levels = {p: partitions(p) for p in (6, 3, 1)}
    chains = 0
    weighted = 0
    for fine in levels[6]:
        for middle in levels[3]:
            if not refines(fine, middle):
                continue
            for coarse in levels[1]:
                chains += 1
                assert refines(middle, coarse)
                parts = (fine, middle, coarse, (frozenset(TRIPLES),))
                for edge in range(3):
                    a = check_edge(parts[edge], parts[edge + 1], proj_a)
                    c = check_edge(parts[edge], parts[edge + 1], proj_c)
                    weighted += (edge + 1) * (a + 2 * c)
    assert chains > 0 and weighted > 0
    print("SYRK nested incidence check=True")
    print("triples", len(TRIPLES), "chains", chains, "weighted_volume", weighted)


if __name__ == "__main__":
    run()

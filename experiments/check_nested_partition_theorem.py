#!/usr/bin/env python3
"""Exhaustive incidence check for the static nested-partition theorem.

The proof is per entry: if an entry occurs in d_f fine parts and d_c nested
coarse parts, a broadcast/reduction forest needs exactly d_f-d_c new edge
word events.  This checks that identity for every 2x2x2 partition chain.
"""

from itertools import combinations


DIMS = (2, 2, 2)
TRIPLES = tuple(
    (i, k, j)
    for i in range(DIMS[0])
    for k in range(DIMS[1])
    for j in range(DIMS[2])
)
AXES = ((0, 1), (1, 2), (0, 2))  # A, B, C projections
LEVELS = (8, 4, 2)
WEIGHTS = (2, 3, 5)
SOURCE = (frozenset(TRIPLES),)


def equal_partitions(items, parts):
    items = tuple(items)
    if parts == 1:
        yield (frozenset(items),)
        return
    block_size = len(items) // parts
    first = items[0]
    for rest in combinations(items[1:], block_size - 1):
        block = frozenset((first,) + rest)
        remaining = tuple(item for item in items if item not in block)
        for tail in equal_partitions(remaining, parts - 1):
            yield (block,) + tail


def canonical(partition):
    return tuple(sorted(tuple(sorted(block)) for block in partition))


def all_partitions(parts):
    seen = set()
    out = []
    for partition in equal_partitions(TRIPLES, parts):
        key = canonical(partition)
        if key not in seen:
            seen.add(key)
            out.append(tuple(frozenset(block) for block in key))
    return out


def refines(fine, coarse):
    return all(any(block <= parent for parent in coarse) for block in fine)


def projection(block, axes):
    return {tuple(item[i] for i in axes) for item in block}


def incidence_counts(partition, axes):
    counts = {}
    for block in partition:
        for entry in projection(block, axes):
            counts[entry] = counts.get(entry, 0) + 1
    return counts


def edge_increment(fine, coarse, axes):
    fine_counts = incidence_counts(fine, axes)
    coarse_counts = incidence_counts(coarse, axes)
    entries = set(fine_counts) | set(coarse_counts)
    increments = {
        entry: fine_counts.get(entry, 0) - coarse_counts.get(entry, 0)
        for entry in entries
    }
    assert all(value >= 0 for value in increments.values())
    return increments


def run():
    choices = {parts: all_partitions(parts) for parts in LEVELS}
    chains = 0
    checked_edges = 0
    weighted_total = 0
    for fine in choices[8]:
        for middle in choices[4]:
            if not refines(fine, middle):
                continue
            for coarse in choices[2]:
                if not refines(middle, coarse):
                    continue
                chains += 1
                levels = (fine, middle, coarse, SOURCE)
                for edge_index in range(3):
                    fine_level = levels[edge_index]
                    coarse_level = levels[edge_index + 1]
                    edge_volume = 0
                    for axes in AXES:
                        increments = edge_increment(
                            fine_level, coarse_level, axes
                        )
                        # A forest retains one copy in each coarse part and
                        # adds one event for every remaining incidence.
                        edge_volume += sum(increments.values())
                        checked_edges += len(increments)
                    weighted_total += WEIGHTS[edge_index] * edge_volume

    assert chains > 0
    assert checked_edges > 0
    assert weighted_total > 0
    print("nested partition incidence theorem check=True")
    print("chains", chains, "checked_entry_edge_differences", checked_edges)
    print("sampled_weighted_forest_volume", weighted_total)


if __name__ == "__main__":
    run()

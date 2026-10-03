#!/usr/bin/env python3
"""Small counterexample to rectangularization under weighted edge costs.

On the 2x2x2 product set, compare arbitrary nested partitions with rectangular
processor-grid chains for P=(8,4,2).  With edge weights (1,2,1), a diagonal
coarse partition beats every rectangular chain.
"""
from itertools import combinations

DIMS = (2, 2, 2)
TRIPLES = tuple((i, k, j) for i in range(2) for k in range(2) for j in range(2))
PROJECTIONS = ((0, 1), (1, 2), (0, 2))
WEIGHTS = (1, 2, 1)  # fine, middle, coarse edges
LEVELS = (8, 4, 2)
SOURCE = (frozenset(TRIPLES),)


def projection(block, axes):
    return {tuple(t[i] for i in axes) for t in block}


def projection_sum(partition):
    return sum(
        len(projection(block, axes))
        for block in partition
        for axes in PROJECTIONS
    )


def equal_partitions(items, p):
    items = tuple(items)
    if p == 1:
        yield (frozenset(items),)
        return
    block_size = len(items) // p
    first = items[0]
    for rest in combinations(items[1:], block_size - 1):
        block = frozenset((first,) + rest)
        remaining = tuple(item for item in items if item not in block)
        for tail in equal_partitions(remaining, p - 1):
            yield (block,) + tail


def canonical(partition):
    return tuple(sorted(tuple(sorted(block)) for block in partition))


def all_partitions(p):
    out, seen = [], set()
    for partition in equal_partitions(TRIPLES, p):
        key = canonical(partition)
        if key not in seen:
            seen.add(key)
            out.append(tuple(frozenset(block) for block in key))
    return out


def refines(fine, coarse):
    return all(any(block <= parent for parent in coarse) for block in fine)


def grid_partition(grid):
    a, b, c = grid
    blocks = {}
    for i, k, j in TRIPLES:
        key = (i // (2 // a), k // (2 // b), j // (2 // c))
        blocks.setdefault(key, set()).add((i, k, j))
    return tuple(frozenset(block) for block in blocks.values())


def grids(p):
    return [
        (a, b, c)
        for a in (1, 2)
        for b in (1, 2)
        for c in (1, 2)
        if a * b * c == p
    ]


def weighted_value(chain):
    partitions = chain + (SOURCE,)
    return sum(
        weight * (projection_sum(partitions[i]) - projection_sum(partitions[i + 1]))
        for i, weight in enumerate(WEIGHTS)
    )


def run():
    choices = [all_partitions(p) for p in LEVELS]
    arbitrary_best = None
    arbitrary_witness = None
    chains = 0
    for fine in choices[0]:
        for middle in choices[1]:
            if not refines(fine, middle):
                continue
            for coarse in choices[2]:
                if not refines(middle, coarse):
                    continue
                chains += 1
                value = weighted_value((fine, middle, coarse))
                if arbitrary_best is None or value < arbitrary_best:
                    arbitrary_best = value
                    arbitrary_witness = (fine, middle, coarse)

    rectangular_best = None
    rectangular_witness = None
    for gf in grids(LEVELS[0]):
        fine = grid_partition(gf)
        for gm in grids(LEVELS[1]):
            middle = grid_partition(gm)
            if not refines(fine, middle):
                continue
            for gc in grids(LEVELS[2]):
                coarse = grid_partition(gc)
                if not refines(middle, coarse):
                    continue
                value = weighted_value((fine, middle, coarse))
                if rectangular_best is None or value < rectangular_best:
                    rectangular_best = value
                    rectangular_witness = (gf, gm, gc)

    assert arbitrary_best == 12
    assert rectangular_best == 16
    print(
        f"levels={LEVELS} weights={WEIGHTS} arbitrary_chains={chains} "
        f"arbitrary_min={arbitrary_best} rectangular_min={rectangular_best}"
    )
    print("rectangular witness", rectangular_witness)
    print("weighted rectangularization counterexample=True")


if __name__ == "__main__":
    run()

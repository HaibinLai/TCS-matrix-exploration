#!/usr/bin/env python3
"""Exhaustive 2x2x3 nested-partition check.

For the product set [2]x[2]x[3], enumerate all two-level chains with 2 and
4 equal owner groups.  Compare arbitrary nested partitions against compatible
rectangular grids.  This is a finite falsification test, not a theorem.
"""
from itertools import combinations

DIMS = (2, 2, 3)
TRIPLES = tuple(
    (i, k, j)
    for i in range(DIMS[0])
    for k in range(DIMS[1])
    for j in range(DIMS[2])
)
PROJECTIONS = ((0, 1), (1, 2), (0, 2))
INITIAL = sum(DIMS[i] * DIMS[j] for i, j in PROJECTIONS)


def projection(block, axes):
    return {tuple(t[i] for i in axes) for t in block}


def boundary(partition):
    return sum(
        len(projection(block, axes))
        for block in partition
        for axes in PROJECTIONS
    ) - INITIAL


def equal_two_partition(items):
    items = tuple(items)
    first = items[0]
    for rest in combinations(items[1:], len(items) // 2 - 1):
        left = frozenset((first,) + rest)
        right = frozenset(item for item in items if item not in left)
        yield left, right


def split_six(block):
    items = tuple(block)
    first = items[0]
    for rest in combinations(items[1:], 2):
        left = frozenset((first,) + rest)
        right = frozenset(item for item in items if item not in left)
        yield left, right


def grid_partition(grid):
    a, b, c = grid
    blocks = {}
    for i, k, j in TRIPLES:
        key = (i // (DIMS[0] // a), k // (DIMS[1] // b), j // (DIMS[2] // c))
        blocks.setdefault(key, set()).add((i, k, j))
    return tuple(frozenset(block) for block in blocks.values())


def grids(p):
    out = []
    for a in range(1, DIMS[0] + 1):
        for b in range(1, DIMS[1] + 1):
            for c in range(1, DIMS[2] + 1):
                if a * b * c == p:
                    out.append((a, b, c, grid_partition((a, b, c))))
    return out


def refines(fine, coarse):
    return all(any(block <= parent for parent in coarse) for block in fine)


def run():
    best = None
    chains = 0
    for coarse in equal_two_partition(TRIPLES):
        for left in split_six(coarse[0]):
            for right in split_six(coarse[1]):
                fine = left + right
                chains += 1
                value = boundary(coarse) + boundary(fine)
                best = value if best is None else min(best, value)

    rectangular = None
    witnesses = 0
    for _, _, _, coarse in grids(2):
        for _, _, _, fine in grids(4):
            if not refines(fine, coarse):
                continue
            value = boundary(coarse) + boundary(fine)
            if rectangular is None or value < rectangular:
                rectangular, witnesses = value, 1
            elif value == rectangular:
                witnesses += 1

    print(
        f"dims={DIMS} levels=(2,4) arbitrary_min={best} "
        f"rectangular_min={rectangular} nested_chains={chains} "
        f"rectangular_witnesses={witnesses}"
    )
    assert best == rectangular == 18
    print("2x2x3 nested partition boundary check=True")


if __name__ == "__main__":
    run()

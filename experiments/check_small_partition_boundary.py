#!/usr/bin/env python3
"""Tiny exhaustive check for the partition/HBL route.

For a 2-by-2-by-2 classical GEMM product set, enumerate balanced partitions
into P=2 and P=4 owner groups.  Compare the minimum projection boundary with
rectangular processor-grid partitions.  This is evidence for a
rectangularization conjecture only; it is not a general proof.
"""
from itertools import combinations

DIMS = (2, 2, 2)
TRIPLES = tuple((i, k, j) for i in range(2) for k in range(2) for j in range(2))
PROJECTIONS = ((0, 1), (1, 2), (0, 2))
INITIAL = sum(2 * 2 for _ in PROJECTIONS)


def projection(block, axes):
    return {tuple(t[i] for i in axes) for t in block}


def boundary(partition):
    return sum(
        len(projection(block, axes))
        for block in partition
        for axes in PROJECTIONS
    ) - INITIAL


def equal_partitions(items, block_size):
    items = tuple(items)
    if not items:
        yield []
        return
    first = items[0]
    for rest in combinations(items[1:], block_size - 1):
        block = (first,) + rest
        remaining = tuple(item for item in items if item not in block)
        for tail in equal_partitions(remaining, block_size):
            yield [set(block)] + tail


def rectangular_partition(grid):
    a, b, c = grid
    blocks = {}
    for i, k, j in TRIPLES:
        key = (i // (2 // a), k // (2 // b), j // (2 // c))
        blocks.setdefault(key, set()).add((i, k, j))
    return list(blocks.values())


def run():
    for p in (2, 4):
        parts = list(equal_partitions(TRIPLES, len(TRIPLES) // p))
        best = min(boundary(partition) for partition in parts)
        rectangular = []
        for a in range(1, 3):
            for b in range(1, 3):
                for c in range(1, 3):
                    if a * b * c == p:
                        rectangular.append(boundary(rectangular_partition((a, b, c))))
        assert best == min(rectangular), (p, best, rectangular)
        print(f"P={p} partitions={len(parts)} min_boundary={best} rectangular_min={min(rectangular)}")


if __name__ == "__main__":
    run()
    print("small partition boundary check=True")

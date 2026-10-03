#!/usr/bin/env python3
"""Exhaustive nested-partition boundary checks on the 2x2x2 product set.

We enumerate equal-sized partitions at three ownership levels and compare the
minimum sum of projection boundaries over all nested chains with the minimum
restricted to compatible rectangular processor-grid partitions.

This is a falsification test for the rectangularization conjecture only; it is
not a proof for general dimensions or arbitrary dynamic schedules.
"""
from itertools import combinations
from math import prod

TRIPLES = tuple((i, k, j) for i in range(2) for k in range(2) for j in range(2))
PROJECTIONS = ((0, 1), (1, 2), (0, 2))
INITIAL = 12


def projection(block, axes):
    return {tuple(t[i] for i in axes) for t in block}


def boundary(partition):
    return sum(
        len(projection(block, axes))
        for block in partition
        for axes in PROJECTIONS
    ) - INITIAL


def canonical(partition):
    return tuple(sorted((tuple(sorted(block)) for block in partition)))


def equal_partitions(items, p):
    items = tuple(items)
    if p == 1:
        yield (frozenset(items),)
        return
    if len(items) % p:
        return
    block_size = len(items) // p
    first = items[0]
    for rest in combinations(items[1:], block_size - 1):
        block = frozenset((first,) + rest)
        remaining = tuple(item for item in items if item not in block)
        for tail in equal_partitions(remaining, p - 1):
            part = (block,) + tail
            yield tuple(sorted(part, key=lambda x: tuple(sorted(x))))


def all_partitions(p):
    seen = set()
    out = []
    for part in equal_partitions(TRIPLES, p):
        key = canonical(part)
        if key not in seen:
            seen.add(key)
            out.append(part)
    return out


def refines(fine, coarse):
    return all(any(block <= parent for parent in coarse) for block in fine)


def grid_partition(grid):
    a, b, c = grid
    assert a * b * c in (1, 2, 4, 8)
    blocks = {}
    for i, k, j in TRIPLES:
        key = (i // (2 // a), k // (2 // b), j // (2 // c))
        blocks.setdefault(key, set()).add((i, k, j))
    return tuple(frozenset(block) for block in blocks.values())


def factor_grids(p):
    return [
        (a, b, c)
        for a in (1, 2)
        for b in (1, 2)
        for c in (1, 2)
        if a * b * c == p
    ]


def best_nested(ps):
    levels = [all_partitions(p) for p in ps]
    best = None
    count = 0
    for coarse in levels[0]:
        for middle in levels[1]:
            if not refines(middle, coarse):
                continue
            for fine in levels[2]:
                if not refines(fine, middle):
                    continue
                count += 1
                value = boundary(coarse) + boundary(middle) + boundary(fine)
                if best is None or value < best:
                    best = value
    return best, count


def best_nested_grids(ps):
    grids = [factor_grids(p) for p in ps]
    best = None
    witnesses = []
    for gc in grids[0]:
        pc = grid_partition(gc)
        for gm in grids[1]:
            pm = grid_partition(gm)
            if not refines(pm, pc):
                continue
            for gf in grids[2]:
                pf = grid_partition(gf)
                if not refines(pf, pm):
                    continue
                value = boundary(pc) + boundary(pm) + boundary(pf)
                if best is None or value < best:
                    best = value
                    witnesses = [(gc, gm, gf)]
                elif value == best:
                    witnesses.append((gc, gm, gf))
    return best, witnesses


def run():
    for ps in ((1, 2, 4), (2, 4, 8)):
        arbitrary, chains = best_nested(ps)
        rectangular, witnesses = best_nested_grids(ps)
        print(
            f"levels={ps} arbitrary_min={arbitrary} rectangular_min={rectangular} "
            f"nested_chains={chains} rectangular_witnesses={len(witnesses)}"
        )
        assert arbitrary == rectangular
    print("nested partition boundary check=True")


if __name__ == "__main__":
    run()

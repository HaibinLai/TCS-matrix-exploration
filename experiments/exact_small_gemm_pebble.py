#!/usr/bin/env python3
"""Exact tiny-GEMM read/partial-load pebble search.

Model: one owner computes every product of a 2x2x2 GEMM exactly once.  The
fast memory holds at most M entries.  Loading an A, B, or already-initialized C
entry costs one word; evictions are free.  The first zero initialization of a
C accumulator is free and occupies one fast-memory slot.  Final output stores
are omitted deliberately, so this is a read/partial-load model rather than a
full GEMM I/O theorem.

The shortest path is exact for this finite state model.  It is used only to
test whether the cut and phase lower bounds already determine the optimum.
"""
from heapq import heappop, heappush


def popcount(value):
    """Python 3.9-compatible integer population count."""
    return bin(value).count("1")


def make_products():
    # IDs are A entries, then B entries, then C entries.
    a = {(i, k): i * 2 + k for i in range(2) for k in range(2)}
    b0 = len(a)
    b = {(k, j): b0 + k * 2 + j for k in range(2) for j in range(2)}
    c0 = b0 + len(b)
    c = {(i, j): c0 + i * 2 + j for i in range(2) for j in range(2)}
    return [(a[i, k], b[k, j], c[i, j])
            for i in range(2) for k in range(2) for j in range(2)]


def exact_min_loads(capacity):
    products = make_products()
    data_count = 12
    goal = (1 << len(products)) - 1
    # State = (completed product mask, resident data mask).
    start = (0, 0)
    distance = {start: 0}
    parent = {}
    queue = [(0, *start)]

    while queue:
        cost, completed, resident = heappop(queue)
        state = (completed, resident)
        if cost != distance[state]:
            continue
        if completed == goal:
            return cost, parent, state, products

        # Zero-cost product transitions.  A C accumulator can be created for
        # free on its first product; an initialized but evicted C must reload.
        initialized_c = 0
        for p, (_, _, c_id) in enumerate(products):
            if completed >> p & 1:
                initialized_c |= 1 << c_id
        for p, (a_id, b_id, c_id) in enumerate(products):
            if completed >> p & 1:
                continue
            if not ((resident >> a_id) & 1 and (resident >> b_id) & 1):
                continue
            if not ((resident >> c_id) & 1) and ((initialized_c >> c_id) & 1):
                continue
            if (resident >> c_id) & 1:
                resident_options = (resident,)
            elif popcount(resident) < capacity:
                resident_options = (resident | (1 << c_id),)
            else:
                resident_options = tuple(
                    (resident & ~(1 << evicted)) | (1 << c_id)
                    for evicted in range(data_count)
                    if (resident >> evicted) & 1
                )
            for next_resident in resident_options:
                next_state = (completed | (1 << p), next_resident)
                if cost < distance.get(next_state, 10**9):
                    distance[next_state] = cost
                    heappush(queue, (cost, *next_state))
                    parent[next_state] = (state, ("compute", p))

        # One word load, with an optional free eviction if memory is full.
        for data_id in range(data_count):
            if (resident >> data_id) & 1:
                continue
            if popcount(resident) < capacity:
                resident_options = (resident | (1 << data_id),)
            else:
                resident_options = tuple(
                    (resident & ~(1 << evicted)) | (1 << data_id)
                    for evicted in range(data_count)
                    if (resident >> evicted) & 1
                )
            for next_resident in resident_options:
                next_state = (completed, next_resident)
                next_cost = cost + 1
                if next_cost < distance.get(next_state, 10**9):
                    distance[next_state] = next_cost
                    heappush(queue, (next_cost, *next_state))
                    parent[next_state] = (state, ("load", data_id))

    return None, parent, None, products


def run():
    results = {}
    for capacity in (3, 4, 5, 6):
        optimum, _, _, _ = exact_min_loads(capacity)
        results[capacity] = optimum
    assert results == {3: 12, 4: 10, 5: 9, 6: 8}

    # For M=3, the one-copy A/B cut term is 8 words.  The standard continuous
    # phase term is 3 * (8 / (2*3/3)^(3/2) - 1) = 3*(8/(2sqrt(2))-1).
    # Hence max(cut, phase) = 8, strictly below the exact trace optimum 12.
    print("exact tiny GEMM pebble check=True")
    print("minimum read/partial-load words", results)
    print("M=3 cut=8 max(cut,phase)=8 exact=12")


if __name__ == "__main__":
    run()

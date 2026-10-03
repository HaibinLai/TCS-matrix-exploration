#!/usr/bin/env python3
"""Exact two-owner operand trace with a shared child cache.

Toy model:
* A 2x2x2 GEMM is split by the i index between two owners.
* Each owner has an M-entry local cache containing A/B entries.
* The child group has a G-entry shared cache containing B entries.
* Parent-to-group shared arrivals and parent-to-owner direct arrivals cost one.
* Shared-to-local promotion, eviction, and product computation cost zero.
* C values are computed and written for free; this isolates operand traffic.

The result is an exact diagnostic for shared-cache reuse, not a full GEMM I/O
theorem. It is useful because the state space stays finite and transparent.
"""

from heapq import heappop, heappush


def bit(value):
    return 1 << value


def popcount(value):
    return bin(value).count("1")


def product_operands():
    a = {(i, k): i * 2 + k for i in range(2) for k in range(2)}
    b0 = len(a)
    b = {(k, j): b0 + k * 2 + j for k in range(2) for j in range(2)}
    products = []
    owners = []
    for i in range(2):
        for k in range(2):
            for j in range(2):
                products.append((a[i, k], b[k, j]))
                owners.append(i)
    return products, owners


def insert_options(mask, item, capacity, universe=8):
    item_bit = bit(item)
    if mask & item_bit:
        return (mask,)
    if popcount(mask) < capacity:
        return (mask | item_bit,)
    return tuple(
        (mask & ~bit(evicted)) | item_bit
        for evicted in range(universe)
        if mask & bit(evicted)
    )


def exact_min_arrivals(local_capacity, shared_capacity):
    product_list, owner_of = product_operands()
    goal = (1 << len(product_list)) - 1
    # done, local owner 0, local owner 1, shared B entries
    start = (0, 0, 0, 0)
    distance = {start: 0}
    parent = {}
    queue = [(0, start)]

    while queue:
        cost, state = heappop(queue)
        if distance[state] != cost:
            continue
        done, local0, local1, shared = state
        if done == goal:
            return cost, parent, state, product_list, owner_of

        locals_ = (local0, local1)

        # Free promotion from the child shared cache to either local cache.
        for owner in (0, 1):
            for item in range(4, 8):
                if not (shared & bit(item)) or locals_[owner] & bit(item):
                    continue
                for promoted in insert_options(
                    locals_[owner], item, local_capacity
                ):
                    next_locals = list(locals_)
                    next_locals[owner] = promoted
                    next_state = (
                        done, next_locals[0], next_locals[1], shared
                    )
                    if cost < distance.get(next_state, 10**9):
                        distance[next_state] = cost
                        heappush(queue, (cost, next_state))
                        parent[next_state] = (state, ("promote", owner, item))

        # Free operand-only product computations.
        for index, (a_id, b_id) in enumerate(product_list):
            if done & bit(index):
                continue
            owner = owner_of[index]
            local = locals_[owner]
            if not (local & bit(a_id) and local & bit(b_id)):
                continue
            next_state = (done | bit(index), local0, local1, shared)
            if cost < distance.get(next_state, 10**9):
                distance[next_state] = cost
                heappush(queue, (cost, next_state))
                parent[next_state] = (state, ("compute", owner, index))

        # Direct parent-to-owner arrivals.  A owner needs A entries 0/1;
        # owner 1 needs A entries 2/3; both need all B entries.
        for owner in (0, 1):
            relevant = (
                ({0, 1} if owner == 0 else {2, 3})
                | set(range(4, 8))
            )
            for item in sorted(relevant):
                if locals_[owner] & bit(item):
                    continue
                for next_local in insert_options(
                    locals_[owner], item, local_capacity
                ):
                    next_locals = list(locals_)
                    next_locals[owner] = next_local
                    next_state = (
                        done, next_locals[0], next_locals[1], shared
                    )
                    next_cost = cost + 1
                    if next_cost < distance.get(next_state, 10**9):
                        distance[next_state] = next_cost
                        heappush(queue, (next_cost, next_state))
                        parent[next_state] = (state, ("direct", owner, item))

        # One shared arrival for a B entry.
        if shared_capacity:
            for item in range(4, 8):
                if shared & bit(item):
                    continue
                for next_shared in insert_options(
                    shared, item, shared_capacity
                ):
                    next_state = (done, local0, local1, next_shared)
                    next_cost = cost + 1
                    if next_cost < distance.get(next_state, 10**9):
                        distance[next_state] = next_cost
                        heappush(queue, (next_cost, next_state))
                        parent[next_state] = (state, ("shared", item))

    return None, parent, None, product_list, owner_of


def reconstruct(parent, state):
    actions = []
    while state in parent:
        state, action = parent[state]
        actions.append(action)
    actions.reverse()
    return actions


def run():
    results = {}
    for shared_capacity in (0, 1, 2):
        result = exact_min_arrivals(2, shared_capacity)
        assert result[0] is not None
        results[shared_capacity] = result[0]
    assert results[0] >= results[1] >= results[2]
    print("exact shared-cache operand trace check=True")
    print("local_capacity", 2, "arrivals_by_shared_capacity", results)


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Exact restricted full-trace search for a shared-B 2x2x2 GEMM.

Restriction deliberately used for the first finite-capacity breakthrough:
* rows are fixed to two owners (owner i computes all products for row i);
* M is the owner-local capacity and G=1 shared cache receives each of the four
  B entries exactly once, in an arbitrary permutation;
* shared arrivals are available to both owners and cost one each; direct B
  loads are disallowed in this restricted model;
* C is a local accumulator. The first accumulator is free, an initialized C
  evicted from local memory costs one store, a root-current C reload costs one,
  and each final C value must be current at the root (one final store if not).

For a fixed B-arrival permutation, owners are independent once the four shared
arrivals are fixed. The exact one-owner 0/1 shortest path below enumerates all
local resident states. The result is a finite certificate, not an unrestricted
finite-capacity theorem.
"""
from collections import deque
from itertools import permutations

# One owner: A_0,A_1 are ids 0,1; B_{00},B_{01},B_{10},B_{11} are ids 2..5;
# C_0,C_1 are ids 6,7.
PRODUCTS = ((0, 2, 6), (0, 3, 7), (1, 4, 6), (1, 5, 7))
B_IDS = tuple(range(2, 6))
A_IDS = (0, 1)
C_IDS = (6, 7)


def bit(x):
    return 1 << x


def popcount(x):
    return bin(x).count("1")


def insert_options(mask, item, capacity, root_current):
    """Yield (new local mask, cost, new root-current mask, evicted id)."""
    item_bit = bit(item)
    if mask & item_bit:
        yield mask, 0, root_current, None
        return
    if popcount(mask) < capacity:
        yield mask | item_bit, 0, root_current, None
        return
    for evicted in range(8):
        if not (mask & bit(evicted)):
            continue
        cost = 0
        new_root = root_current
        if evicted in C_IDS:
            # An initialized C is always saved before eviction. The caller
            # only invokes this on initialized accumulators or first-C slots.
            cost = 1
            new_root |= bit(evicted - 6)
        yield ((mask ^ bit(evicted)) | item_bit), cost, new_root, evicted


def exact_owner_cost(order, capacity):
    """Exact local cost excluding the four shared-B arrival words."""
    start = (0, 0, 0, 0)  # event index, completed mask, local mask, root-current C
    distance = {start: 0}
    queue = deque([start])
    best = 10**9

    while queue:
        state = queue.popleft()
        cost = distance[state]
        if cost >= best:
            continue
        event, done, local, root_current = state
        if done == 0b1111:
            # Any C not current at root needs one final write. Keep searching:
            # the first done state minimizes internal cost, not necessarily the
            # internal cost plus the terminal write count.
            best = min(best, cost + 2 - popcount(root_current))
            continue

        initialized = 0
        for product, (_, _, c_id) in enumerate(PRODUCTS):
            if done & bit(product):
                initialized |= bit(c_id - 6)

        # Zero-cost product computations. A first C accumulator is inserted
        # for free; initialized-but-absent C must use the reload transition.
        for product, (a_id, b_id, c_id) in enumerate(PRODUCTS):
            if done & bit(product) or not (local & bit(a_id)):
                continue
            if not (local & bit(b_id)):
                continue
            c_bit = bit(c_id)
            if local & c_bit:
                next_state = (
                    event,
                    done | bit(product),
                    local,
                    root_current & ~bit(c_id - 6),
                )
                if cost < distance.get(next_state, 10**9):
                    distance[next_state] = cost
                    queue.appendleft(next_state)
            elif not (initialized & bit(c_id - 6)):
                for next_local, evict_cost, next_root, _ in insert_options(
                    local, c_id, capacity, root_current
                ):
                    next_state = (
                        event,
                        done | bit(product),
                        next_local,
                        next_root & ~bit(c_id - 6),
                    )
                    next_cost = cost + evict_cost
                    if next_cost < distance.get(next_state, 10**9):
                        distance[next_state] = next_cost
                        queue.appendleft(next_state)

        # Direct A arrivals cost one. (Direct B arrivals are prohibited by the
        # restricted theorem; all B data come through the current event.)
        for a_id in A_IDS:
            if local & bit(a_id):
                continue
            for next_local, evict_cost, next_root, _ in insert_options(
                local, a_id, capacity, root_current
            ):
                next_state = (event, done, next_local, next_root)
                next_cost = cost + 1 + evict_cost
                if next_cost < distance.get(next_state, 10**9):
                    distance[next_state] = next_cost
                    queue.append(next_state)

        # Reload an initialized C from the root when its saved value is current.
        for c_id in C_IDS:
            c_bit = bit(c_id)
            c_index = c_id - 6
            if local & c_bit or not (initialized & bit(c_index)):
                continue
            if not (root_current & bit(c_index)):
                continue
            for next_local, evict_cost, next_root, _ in insert_options(
                local, c_id, capacity, root_current
            ):
                next_state = (event, done, next_local, next_root)
                next_cost = cost + 1 + evict_cost
                if next_cost < distance.get(next_state, 10**9):
                    distance[next_state] = next_cost
                    queue.append(next_state)

        # Promote only the B entry of the current shared event. Promotion is
        # free; evicting an initialized C stores it first.
        if event < len(order):
            b_id = 2 + order[event]
            if not (local & bit(b_id)):
                for next_local, evict_cost, next_root, _ in insert_options(
                    local, b_id, capacity, root_current
                ):
                    next_state = (event, done, next_local, next_root)
                    next_cost = cost + evict_cost
                    if next_cost < distance.get(next_state, 10**9):
                        distance[next_state] = next_cost
                        queue.appendleft(next_state)

            # Move to the next parent->group arrival. Previously promoted B
            # entries may remain local and remain usable.
            next_state = (event + 1, done, local, root_current)
            if cost < distance.get(next_state, 10**9):
                distance[next_state] = cost
                queue.appendleft(next_state)

    assert best < 10**9
    return best


def run():
    owner_costs = {}
    for capacity in (3, 4):
        values = [
            (order, exact_owner_cost(order, capacity))
            for order in permutations(range(4))
        ]
        costs = {value for _, value in values}
        owner_costs[capacity] = costs
        # With the correct four B_{k,j} entries, M=3 has good and bad
        # one-arrival permutations (5 or 6); M=4 is permutation-independent.
        assert costs == ({5, 6} if capacity == 3 else {4})
        assert min(value for _, value in values) == (5 if capacity == 3 else 4)
        print("M", capacity, "owner costs", sorted(costs),
              "minimum", min(value for _, value in values))

    # Four shared B arrivals plus two independent row owners.
    assert min(owner_costs[3]) * 2 + 4 == 14
    assert min(owner_costs[4]) * 2 + 4 == 12
    print("restricted shared-C full-trace check=True")
    print("M=3,G=1,one-arrival-per-B minimum total=14")
    print("M=4,G=1,one-arrival-per-B total=12")


if __name__ == "__main__":
    run()

#!/usr/bin/env python3
"""Inspect phases of the exact 2x2x2 pebble optimum.

The phase split puts at most M load events in each phase.  It records the
actual A/B/C projection sizes and checks whether Loomis--Whitney is attained.
The result is evidence about the trace model, not a general GEMM theorem.
"""

import sys
from math import sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from exact_small_gemm_pebble import exact_min_loads


def shortest_actions(capacity):
    cost, parent, state, products = exact_min_loads(capacity)
    actions = []
    while state != (0, 0):
        previous, action = parent[state]
        actions.append(action)
        state = previous
    actions.reverse()
    return cost, products, actions


def split_phases(actions, capacity):
    phases = []
    current = []
    loads = 0
    for action in actions:
        if action[0] == "load" and loads == capacity and current:
            phases.append(current)
            current = []
            loads = 0
        current.append(action)
        if action[0] == "load":
            loads += 1
    if current:
        phases.append(current)
    return phases


def run():
    capacity = 3
    cost, products, actions = shortest_actions(capacity)
    phases = split_phases(actions, capacity)
    summaries = []
    for phase in phases:
        product_set = [products[index]
                       for kind, index in phase if kind == "compute"]
        projections = tuple(len({product[axis] for product in product_set})
                            for axis in range(3))
        work = len(product_set)
        hbl = sqrt(projections[0] * projections[1] * projections[2])
        summaries.append((sum(kind == "load" for kind, _ in phase),
                          work, projections, hbl))

    assert cost == 12
    assert len(phases) == 4
    assert sum(summary[1] for summary in summaries) == 8
    assert any(summary[1] < summary[3] for summary in summaries)
    print("exact trace phase check=True")
    print("capacity", capacity, "loads", cost, "phase_summaries", summaries)


if __name__ == "__main__":
    run()

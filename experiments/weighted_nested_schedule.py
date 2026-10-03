#!/usr/bin/env python3
"""Diagnostic search for volume-vs-message-sensitive nested grid schedules.

H(g) is the usual per-process 3D collective-volume proxy.  H/phi is only a
message-aggregation proxy; this script is not a communication lower-bound
proof and ignores collective tree/logarithmic factors.
"""
from itertools import product
from math import isclose


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def H(shape, grid):
    m, n, k = shape
    p1, p2, p3 = grid
    return m*n/(p1*p2) + n*k/(p2*p3) + m*k/(p1*p3)


def nested(chain):
    return all(
        all(inner[d] % outer[d] == 0 for d in range(3))
        for inner, outer in zip(chain, chain[1:])
    )


def all_nested_chains(shape, pstars):
    choices = [list(grids(p)) for p in pstars]
    return [chain for chain in product(*choices) if nested(chain)]


def objective(chain, shape, weights, phis, message_weight):
    score = 0.0
    for g, w, phi, mw in zip(chain, weights, phis, message_weight):
        h = H(shape, g)
        score += w * h + mw * h / phi
    return score


if __name__ == "__main__":
    shape = (97, 53, 17)
    pstars = (120, 24, 6)
    chains = all_nested_chains(shape, pstars)
    print("shape", shape, "P*", pstars, "nested chains", len(chains))

    volume_best = min(chains, key=lambda c: objective(c, shape, (1,1,1), (1,1,1), (0,0,0)))
    print("volume-best:", volume_best)
    print("volume objective:", objective(volume_best, shape, (1,1,1), (1,1,1), (0,0,0)))

    scenarios = [
        ("outer-latency", (1, 1, 1), (16, 8, 4), (0, 0, 20)),
        ("all-message", (1, 1, 1), (16, 8, 4), (1, 1, 1)),
        ("middle-message-bottleneck", (0, 0, 0), (1, 2, 1), (1, 1, 1)),
        ("inner-bandwidth", (4, 2, 1), (16, 8, 4), (0, 0, 0)),
        ("outer-bandwidth", (1, 1, 4), (16, 8, 4), (0, 0, 0)),
    ]
    for name, weights, phis, mw in scenarios:
        best = min(chains, key=lambda c: objective(c, shape, weights, phis, mw))
        score = objective(best, shape, weights, phis, mw)
        print(name, "best=", best, "score=", round(score, 6),
              "same-as-volume=", best == volume_best)

#!/usr/bin/env python3
"""Small arithmetic certificate for the formal three-level main theorem."""


def projection_sums_rect(m, k, n, a, b, c):
    # A, B, C incidences for an a x b x c block owner grid.
    return c * m * k, a * k * n, b * m * n


def increments(levels, m, k, n):
    # levels are fine-to-coarse (a,b,c), with root appended.
    chain = list(levels) + [(1, 1, 1)]
    out = []
    for (a, b, c), (an, bn, cn) in zip(chain, chain[1:]):
        xa, xb, xc = projection_sums_rect(m, k, n, a, b, c)
        xan, xbn, xcn = projection_sums_rect(m, k, n, an, bn, cn)
        out.append((xa - xan, xb - xbn, xc - xcn))
    return out


def run():
    # A three-edge compatible chain for a 2 x 2 x 2 GEMM.
    chain = [(4, 2, 2), (2, 1, 1), (1, 1, 1)]
    got = increments(chain, 2, 2, 2)
    assert got == [(4, 8, 4), (0, 4, 0), (0, 0, 0)]

    # One-level recovery: a=2,b=2,c=2 gives 4+4+4 aggregate words.
    assert increments([(2, 2, 2)], 2, 2, 2) == [(4, 4, 4)]

    # Rectangular specialization: A/B/C terms remain mk, kn, mn weighted by
    # the corresponding replication factors, so the theorem does not assume n=n.
    m, k, n = 4, 3, 5
    one = increments([(2, 3, 2)], m, k, n)[0]
    assert one == ((2 - 1) * m * k, (2 - 1) * k * n, (3 - 1) * m * n)

    # A nonnegative weighted edge objective is just a linear form in increments.
    weights = (2, 3, 5)
    assert sum(w * x for w, x in zip(weights, one)) == 2 * 12 + 3 * 15 + 5 * 40
    print("three-level nested main theorem arithmetic check=True")
    print("chain increments", got, "one-level rectangular", one)


if __name__ == "__main__":
    run()

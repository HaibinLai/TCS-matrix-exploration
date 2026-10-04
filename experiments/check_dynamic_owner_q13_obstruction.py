#!/usr/bin/env python3
"""Check the combinatorial obstruction behind dynamic-owner Q=13.

Products (i,k,j) are the vertices of a 2x2x2 cube. A-entries are the four
edges changing j (fixed i,k); C-entries are the four edges changing k (fixed
i,j). With a one-slot shared B cache, changing owner across a B edge can be
served by the one baseline B arrival, so only A/C bichromatic edges consume an
extra word in the source/partial accounting.

Every fixed-i (k,j) layer is a 4-cycle. Its A/C boundary has even cardinality;
a nonconstant layer has at least two bichromatic edges. Therefore at most one
A/C split edge forces the owner assignment to be constant on each row layer,
i.e. fixed-row or single-owner. This is a finite check of the parity step; the
analytic lower-bound theorem is recorded in docs/dynamic-owner-q14-theorem.md.
"""
from itertools import product

VERTICES = tuple(product((0, 1), repeat=3))  # (i,k,j)
A_EDGES = tuple(((i, k, 0), (i, k, 1)) for i in (0, 1) for k in (0, 1))
C_EDGES = tuple(((i, 0, j), (i, 1, j)) for i in (0, 1) for j in (0, 1))
AC_EDGES = A_EDGES + C_EDGES


def cut(labels, edges):
    return sum(labels[u] != labels[v] for u, v in edges)


def is_row_dependent(labels):
    return all(labels[i, k, j] == labels[i, 0, 0]
               for i, k, j in VERTICES)


def run():
    low = []
    by_cut = {}
    for bits in product((0, 1), repeat=8):
        labels = dict(zip(VERTICES, bits))
        ac = cut(labels, AC_EDGES)
        by_cut[ac] = by_cut.get(ac, 0) + 1
        if ac <= 1:
            low.append(labels)
            assert is_row_dependent(labels)
    # The only zero-AC-cut assignments are the four row-constant patterns.
    assert len(low) == 4
    assert by_cut[0] == 4
    assert min(ac for ac in by_cut if ac > 0) == 2
    print("dynamic-owner Q13 obstruction check=True")
    print("assignment_count", 2 ** 8)
    print("ac_cut_histogram", dict(sorted(by_cut.items())))
    print("assignments_with_ac_cut_le_1", len(low), "all_row_dependent=True")


if __name__ == "__main__":
    run()

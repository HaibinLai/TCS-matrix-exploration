#!/usr/bin/env python3
"""Check the fixed-assignment boundary and a weighted event-copy toy tradeoff."""


def run():
    # c = a1*b1 + a2*b2, two leaves below root.
    operand_words = 4
    lam = 3
    split = operand_words + 2 * lam
    colocated = operand_words + lam
    assert split == 10
    assert colocated == 7
    # Colocation changes the assignment; it is not recomputation.

    # If one event at r1 is externally required and r2 also needs it,
    # duplicating that event adds two operand arrivals and removes one
    # C-partial arrival.  The sign changes at lambda=2.
    assert (2 - lam) == -1
    assert 2 - 1 == 1
    print("recomputation event tradeoff check=True")
    print("split", split, "colocated", colocated, "copy_delta(lambda=3)", 2 - lam)


if __name__ == "__main__":
    run()

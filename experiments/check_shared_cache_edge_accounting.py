#!/usr/bin/env python3
"""Check edge-level accounting for a shared child cache."""


def run():
    operand = "a_0"

    # Two owners need the same entry. A shared child cache receives one word
    # across the parent-child edge and serves both local phases.
    shared_edge_arrivals = [operand]
    local_missing = [{operand}, {operand}]
    assert len(shared_edge_arrivals) == 1
    assert all(operand in missing for missing in local_missing)

    # With owner-private caches the two deliveries are distinct edge events.
    private_edge_arrivals = [operand, operand]
    assert len(private_edge_arrivals) == 2

    print("shared-cache edge accounting check=True")
    print("shared_edge_words", len(shared_edge_arrivals),
          "private_edge_words", len(private_edge_arrivals))


if __name__ == "__main__":
    run()

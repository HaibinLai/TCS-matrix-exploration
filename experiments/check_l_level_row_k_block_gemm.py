#!/usr/bin/env python3
"""Check the fresh-arrival L-level row-k-block formula."""


def edge_volume(m, k, n, row_groups, reduction_groups):
    return m * k + row_groups * k * n + reduction_groups * m * n


def weighted_volume(m, k, n, row_groups, reduction_groups, costs):
    a, b, c = costs
    return a * m * k + b * row_groups * k * n + c * reduction_groups * m * n


def run():
    levels = ((1, 1), (2, 1), (4, 2), (8, 4))
    m, k, n = 8, 6, 5
    values = [
        edge_volume(m, k, n, rows, reds)
        for rows, reds in levels[1:]
    ]
    assert values == [
        48 + 2 * 6 * 5 + 1 * 8 * 5,
        48 + 4 * 6 * 5 + 2 * 8 * 5,
        48 + 8 * 6 * 5 + 4 * 8 * 5,
    ]
    assert weighted_volume(8, 6, 5, 4, 2, (2, 3, 7)) == (
        2 * 48 + 3 * 4 * 6 * 5 + 7 * 2 * 8 * 5
    )
    print("fresh-arrival L-level row-k theorem check=True")
    print("edge_volumes", values)


if __name__ == "__main__":
    run()

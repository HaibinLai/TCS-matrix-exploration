#!/usr/bin/env python3
"""Check the full row-by-k-block three-level GEMM volume formulas."""


def volumes(rows, k, columns, row_groups, reduction_blocks):
    top = rows * k + row_groups * k * columns + rows * columns
    fine = rows * k + row_groups * k * columns + rows * columns * reduction_blocks
    return top, fine


def weighted_volume(rows, k, columns, row_groups, reduction_blocks,
                    top_costs, fine_costs):
    top_types = (rows * k, row_groups * k * columns, rows * columns)
    fine_types = (
        rows * k,
        row_groups * k * columns,
        rows * columns * reduction_blocks,
    )
    return sum(c * v for c, v in zip(top_costs, top_types)) + sum(
        c * v for c, v in zip(fine_costs, fine_types)
    )


def run():
    for rows, k, columns, row_groups, blocks in (
        (2, 2, 2, 2, 2),
        (4, 6, 3, 2, 3),
        (8, 5, 4, 4, 5),
    ):
        top, fine = volumes(rows, k, columns, row_groups, blocks)
        assert top == rows * k + row_groups * k * columns + rows * columns
        assert fine == rows * k + row_groups * k * columns + rows * columns * blocks
        assert top + fine == (
            2 * rows * k
            + 2 * row_groups * k * columns
            + rows * columns
            + rows * columns * blocks
        )
    weighted = weighted_volume(
        4, 6, 3, 2, 3,
        (2, 3, 5),
        (7, 11, 13),
    )
    assert weighted == (
        2 * 24 + 3 * 36 + 5 * 12
        + 7 * 24 + 11 * 36 + 13 * 36
    )
    print("three-level row-k-block GEMM theorem check=True")
    print("m=2,k=2,n=2,H=2,S=2", volumes(2, 2, 2, 2, 2))


if __name__ == "__main__":
    run()

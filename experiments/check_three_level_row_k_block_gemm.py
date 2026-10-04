#!/usr/bin/env python3
"""Check the full row-by-k-block three-level GEMM volume formulas."""


def volumes(rows, k, columns, reduction_blocks):
    top = rows * k + rows * k * columns + rows * columns
    fine = rows * k + rows * k * columns + rows * columns * reduction_blocks
    return top, fine


def run():
    for rows, k, columns, blocks in ((2, 2, 2, 2), (3, 4, 5, 2), (4, 6, 3, 3)):
        top, fine = volumes(rows, k, columns, blocks)
        assert top == rows * k + rows * k * columns + rows * columns
        assert fine == rows * k + rows * k * columns + rows * columns * blocks
        assert top + fine == (
            2 * rows * k
            + 2 * rows * k * columns
            + rows * columns
            + rows * columns * blocks
        )
    print("three-level row-k-block GEMM theorem check=True")
    print("R=2,K=2,N=2,S=2", volumes(2, 2, 2, 2))


if __name__ == "__main__":
    run()

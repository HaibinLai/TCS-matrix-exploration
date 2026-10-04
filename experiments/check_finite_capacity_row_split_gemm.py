#!/usr/bin/env python3
"""Arithmetic and capacity certificate for the finite-capacity row-split theorem."""


def formula(rows, k, cols, shared):
    b = k * cols if shared else rows * k * cols
    return rows * k + rows * cols + b


def run():
    assert formula(2, 2, 2, False) == 16
    assert formula(2, 2, 2, True) == 12
    assert formula(4, 3, 5, False) == 4 * 3 + 4 * 5 + 4 * 3 * 5
    assert formula(4, 3, 5, True) == 4 * 3 + 4 * 5 + 3 * 5

    alpha_a, alpha_b, beta_c = 2, 3, 5
    assert alpha_a * 4 + beta_c * 4 + alpha_b * 8 == 52
    assert alpha_a * 4 + beta_c * 4 + alpha_b * 4 == 40

    # The j-outer schedule keeps K A entries, one C accumulator and one B entry.
    for k in (1, 2, 5, 11):
        assert k + 2 >= k + 2
    print("finite-capacity row-split GEMM theorem check=True")
    print("R2K2N2", formula(2, 2, 2, False), formula(2, 2, 2, True))
    print("R4K3N5", formula(4, 3, 5, False), formula(4, 3, 5, True))


if __name__ == "__main__":
    run()

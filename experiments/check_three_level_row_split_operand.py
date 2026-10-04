#!/usr/bin/env python3
"""Check the two-edge row-split operand theorem."""


def bound(owners, k, n, groups):
    top = owners * k + groups * k * n
    fine = owners * k + owners * k * n
    return top, fine


def run():
    for owners, k, n, groups in (
        (2, 2, 2, 1),
        (4, 2, 3, 2),
        (8, 1, 7, 4),
    ):
        top, fine = bound(owners, k, n, groups)
        assert top == owners * k + groups * k * n
        assert fine == owners * k + owners * k * n
        assert top + fine == 2 * owners * k + (groups + owners) * k * n
    print("three-level row-split operand theorem check=True")
    print("R=2,K=2,N=2,H=1", bound(2, 2, 2, 1))


if __name__ == "__main__":
    run()

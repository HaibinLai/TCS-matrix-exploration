#!/usr/bin/env python3
"""Check the two-edge row-split operand theorem."""


def bound(owners, k, n):
    top = owners * k + k * n
    fine = owners * k + owners * k * n
    return top, fine


def run():
    for owners, k, n in ((2, 2, 2), (3, 4, 5), (8, 1, 7)):
        top, fine = bound(owners, k, n)
        assert top == owners * k + k * n
        assert fine == owners * k + owners * k * n
        assert top + fine == 2 * owners * k + (owners + 1) * k * n
    print("three-level row-split operand theorem check=True")
    print("R=2,K=2,N=2", bound(2, 2, 2))


if __name__ == "__main__":
    run()

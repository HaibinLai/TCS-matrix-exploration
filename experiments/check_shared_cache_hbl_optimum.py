#!/usr/bin/env python3
"""Check the homogeneous-owner phase-budget optimization lemma."""
from math import sqrt


def h_value(B, A, D):
    return B * max(D / (A + B) ** 1.5 - 1.0, 0.0)


def root_budget(A, D):
    if D <= A ** 1.5:
        return None
    right = min(2.0 * A, D ** (2.0 / 3.0) - A)

    def derivative(B):
        return D * (A - B / 2.0) / (A + B) ** 2.5 - 1.0

    left = 0.0
    for _ in range(100):
        mid = (left + right) / 2.0
        if derivative(mid) > 0:
            left = mid
        else:
            right = mid
    return (left + right) / 2.0


def run():
    A = 16.0
    D = 3.0 * sqrt(3.0) * 200.0 / 2.0
    budget = root_budget(A, D)
    assert budget is not None
    assert 0.0 < budget < min(2.0 * A, D ** (2.0 / 3.0) - A)
    assert h_value(budget, A, D) >= h_value(0.0, A, D)
    assert h_value(budget, A, D) >= h_value(2.0 * A, A, D)

    assert root_budget(16.0, 16.0 ** 1.5) is None
    print("shared-cache HBL optimum check=True")
    print("A", A, "D", D, "B_star", budget,
          "H_star", h_value(budget, A, D))


if __name__ == "__main__":
    run()

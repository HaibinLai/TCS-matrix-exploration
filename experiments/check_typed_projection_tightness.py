#!/usr/bin/env python3
"""Check the equality certificate for a typed rectangular HBL phase."""

from math import isqrt, prod, sqrt


def rectangular_dimensions(x_a, x_b, x_c):
    """Return (i, k, j) when x=(ik,kj,ij) has an integer solution."""
    nums = (
        x_a * x_c / x_b,
        x_a * x_b / x_c,
        x_b * x_c / x_a,
    )
    dims = tuple(isqrt(round(v)) for v in nums)
    if any(d * d != round(v) for d, v in zip(dims, nums)):
        return None
    i, k, j = dims
    if (i * k, k * j, i * j) != (x_a, x_b, x_c):
        return None
    return dims


def run():
    x = (6, 12, 8)
    dims = rectangular_dimensions(*x)
    assert dims == (2, 3, 4)
    work = prod(dims)
    assert work == sqrt(prod(x))

    # A projection triple can satisfy HBL without being one rectangular tile.
    assert rectangular_dimensions(5, 6, 7) is None
    print("typed rectangular tightness check=True")
    print("projection_sizes", x, "dimensions", dims, "work", work)


if __name__ == "__main__":
    run()

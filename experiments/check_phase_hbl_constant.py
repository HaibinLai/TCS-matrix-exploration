#!/usr/bin/env python3
"""Exact integer check of the phase HBL/AM-GM constant.

For a phase with x+y+z <= 2M, verify
    xyz <= (2M/3)^3
for small integer M.  This checks the constant used in
``docs/phase-hbl-multilevel-interface.md``; it is not a GEMM execution test.
"""


def run():
    for M in range(1, 41):
        best = 0
        witness = None
        for x in range(2 * M + 1):
            for y in range(2 * M - x + 1):
                for z in range(2 * M - x - y + 1):
                    value = x * y * z
                    if value > best:
                        best, witness = value, (x, y, z)
        # Compare without floating point: 27 xyz <= (2M)^3.
        assert 27 * best <= (2 * M) ** 3
        if best > 0:
            assert witness is not None
    print("phase HBL integer constant check=True")


if __name__ == "__main__":
    run()

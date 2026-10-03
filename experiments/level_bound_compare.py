#!/usr/bin/env python3
"""Compare the 2022 rectangular memory-independent candidate across HCP levels.
This is a regime/continuity sanity check, not a proof of a multilevel theorem.
"""
from math import sqrt


def d_piecewise(m, n, k, p):
    assert m >= n >= k and p >= 1
    if p <= m / n:
        region = "1D"
        d = (m * n + m * k) / p + n * k
    elif p <= m * n / (k * k):
        region = "2D"
        d = 2 * sqrt(m * n * k * k / p) + m * n / p
    else:
        region = "3D"
        d = 3 * (m * n * k / p) ** (2 / 3)
    compulsory = (m * n + m * k + n * k) / p
    return region, d, d - compulsory


def report(m, n, k, pstars, M_levels):
    print(f"shape=({m},{n},{k}), m/n={m/n:g}, mn/k^2={m*n/(k*k):g}")
    print("level P* M region D communication Q_MD max-leading")
    for i, (p, M) in enumerate(zip(pstars, M_levels), 1):
        region, D, Qmi = d_piecewise(m, n, k, p)
        qmd = 2 * m * n * k / (p * sqrt(M))
        print(f"{i:>5} {p:>3} {M:>8} {region:>6} {D:>12.3f} {Qmi:>14.3f} {qmd:>12.3f} {max(Qmi,qmd):>12.3f}")


if __name__ == "__main__":
    # P* decreases as we move outward in this HCP example.
    report(4096, 1024, 256, [512, 64, 8], [32768, 262144, 2097152])
    print("\nBoundary continuity checks")
    m, n, k = 4096, 1024, 256
    compulsory = lambda p: (m * n + m * k + n * k) / p
    p = m / n
    d1 = (m * n + m * k) / p + n * k
    d2 = 2 * sqrt(m * n * k * k / p) + m * n / p
    print(f"P={p:g}: D_1D={d1:.6f}, D_2D={d2:.6f}, Q={d1-compulsory(p):.6f}")
    p = m * n / (k * k)
    d2 = 2 * sqrt(m * n * k * k / p) + m * n / p
    d3 = 3 * (m * n * k / p) ** (2 / 3)
    print(f"P={p:g}: D_2D={d2:.6f}, D_3D={d3:.6f}, Q={d2-compulsory(p):.6f}")

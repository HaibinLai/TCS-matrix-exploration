#!/usr/bin/env python3
"""Exact global-overlay scan for odd composite p in (2*p*q,p*q,p)."""
import argparse
import sys

from exact_overlay_2d import exact_overlay


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--q", type=int, default=997)
    parser.add_argument("--p", nargs="+", type=int,
                        default=list(range(3, 100, 2)))
    args = parser.parse_args()
    for p in args.p:
        best, points, segments, stats = exact_overlay((2 * p * args.q, p * args.q, p))
        z, y, _, _ = best[1]
        print(f"p={p:3d} q={args.q} ratio={best} point=({z},{y}) "
              f"overlay_points={points} active_segments={segments}")


if __name__ == "__main__":
    main()

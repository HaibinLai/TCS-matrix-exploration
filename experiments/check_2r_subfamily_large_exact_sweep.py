#!/opt/miniconda3/bin/python
"""Larger exact U_8/I samples for the p=2r, q=4r+3 profile.

The sweep is intentionally separate from the six-case smoke test so that the
short validation remains quick.  It checks the exact ratio and witness through
the same 25-line arrangement routine.
"""
from check_2r_subfamily_eight_chain_bound import run

CASES = [
    (31, 127), (37, 151), (41, 167), (47, 191), (59, 239), (67, 271),
    (89, 359), (107, 431), (109, 439), (149, 599), (151, 607),
    (157, 631), (179, 719), (181, 727),
]


if __name__ == '__main__':
    for r, q in CASES:
        best, _, _ = run(r, q)
        print(f'r={r} q={q} ratio={best[0]} point=({best[1][0]},{best[1][1]})')
    print('large exact sweep certificate=True')

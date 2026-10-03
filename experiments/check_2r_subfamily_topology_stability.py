#!/opt/miniconda3/bin/python
"""Finite topology audit for the p=2r, q=4r+3 fixed profile.

The symbolic ratio certificate in ``probe_2r_subfamily_symbolic_cells.py`` is
lifted from the 33 cells at r=21.  This script records the owner/chain
signatures of all feasible full-dimensional cells and checks that the same
signature is obtained at several larger parameters.  It is deliberately an
audit, not a proof that no unseen cell can appear for every real r>=21.
"""
from prove_2r_subfamily_eight_chain_cells import run_profile


def signature(r):
    q = 4 * r + 3
    levels, _, cells = run_profile(r, q, proving_only=False)
    ids = [{line: i for i, line in enumerate(level)} for level in levels]
    sig = tuple(sorted(
        (tuple(ids[level][owners[level]] for level in range(3)), chain)
        for owners, chain, _ in cells
    ))
    return sig


def run(samples=(21, 23, 50, 100)):
    base = signature(samples[0])
    records = []
    for r in samples:
        sig = signature(r)
        records.append((r, len(sig), sig == base))
    assert all(n == 33 and same for _, n, same in records), records
    return records


if __name__ == '__main__':
    print('samples=', run())
    print('topology signature stable at sampled r>=21 values; no-new-cell proof remains open')

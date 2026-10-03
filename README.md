# TCS Matrix Exploration

This repository contains the reproducible notes and exact-enumeration scripts from an ongoing study of I/O and communication complexity for matrix multiplication.

The current computational focus is the three-level aspect-ratio model implemented in `experiments/exact_multilevel_2d.py`. A hierarchy is represented by processor counts $P^*=(P_1,P_2,P_3)$, normalized shape parameters $1\ge z\ge y\ge0$, affine communication lines for processor grids, and compatible nested chains.

The main open thread is the fixed divisor profile

\[
P^*=(2pq,pq,p),\qquad p=2r,\qquad q=4r+3,
\]

with $r$ and $q$ odd primes. The current evidence supports the candidate maximizer

\[
(z,y)=\left(\frac{2q+3}{5q},\frac1r\right)
\]

and the closed-form ratio recorded in the research note. This is not yet stated as a general theorem: the remaining proof task is a parameterized no-new-cell argument for the 25-line arrangement.

## Contents

- `docs/` — research notes, literature update, chronological exploration log, formal three-level model specification, one-level phase/HBL recovery, static-grid ownership lemma, nested-partition HBL route, and proof obligations.
- `docs/reports/` — agent reports and proof-gap notes.
- `experiments/` — exact enumeration, symbolic certificates, scans, and counterexample searches.
- `context/` — the current research handoff and explicit proof-status boundaries.
- `artifacts/` — small text outputs retained as provenance.

The generated Python bytecode and temporary caches are intentionally excluded.

## Reproducing the current certificates

Use a Python environment containing SymPy for the symbolic scripts. The bundled environment used during the exploration is `/opt/miniconda3/bin/python`.

```bash
/opt/miniconda3/bin/python experiments/prove_2r_subfamily_independent_cover.py
/opt/miniconda3/bin/python experiments/prove_sorted_factor_rearrangement.py
/opt/miniconda3/bin/python experiments/probe_2r_subfamily_symbolic_cells.py
python3 experiments/check_2r_subfamily_eight_chain_bound.py
/opt/miniconda3/bin/python experiments/check_2r_subfamily_topology_stability.py
/opt/miniconda3/bin/python experiments/prove_2r_subfamily_empty_cell_certificates.py
/opt/miniconda3/bin/python experiments/check_one_level_recovery.py
/opt/miniconda3/bin/python experiments/check_three_level_model.py
/opt/miniconda3/bin/python experiments/check_static_grid_ownership.py
/opt/miniconda3/bin/python experiments/check_small_partition_boundary.py
```

The last script classifies the 800 owner/chain combinations at $r=21,q=87$: 33 full-dimensional cells, 658 empty combinations, and 109 point-degenerate combinations. Every empty combination has a three-constraint Farkas certificate whose signs remain valid for $r\ge21$ under the current coefficientwise test. The point-degenerate combinations are deliberately kept separate; they are part of the remaining topology audit.

The one-level and three-level checks validate geometry and envelope consistency only; they do not claim the physical HBL lower-bound theorem. `docs/t3-proof-obligations.md` separates the projection, ownership-chain, and edge-additivity lemmas needed for that theorem. `docs/one-level-phase-hbl-lemma.md` records the recovered $n^3/(P\sqrt M)$ phase term and its remaining grid-ownership gap.

The large exact sweep is available as `experiments/check_2r_subfamily_large_exact_sweep.py`. It was run on a 160-core CPU host for 14 additional prime pairs and agreed with the candidate formula in every case.

## Status boundary

The repository records verified finite computations and symbolic branch certificates. It does not claim that the complete general lower-bound theorem has been finished. In particular, the next proof step is to handle the 109 point-degenerate combinations and then combine that result with the stable 33-cell ratio certificate.

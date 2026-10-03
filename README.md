# TCS Matrix Exploration

This repository contains the reproducible notes and exact-enumeration scripts from an ongoing study of I/O and communication complexity for matrix multiplication.

The current computational focus is the three-level aspect-ratio model implemented in `experiments/exact_multilevel_2d.py`. A hierarchy is represented by processor counts $P^*=(P_1,P_2,P_3)$, normalized shape parameters $1\ge z\ge y\ge0$, affine communication lines for processor grids, and compatible nested chains.

The divisor-profile arrangement remains a reproducible geometry case study, but it is no longer treated as the main theorem target. The current theory files state a tight three-level static vector bound, its arbitrary owner-partition boundary lemma, and an $L$-level/asymmetric-cost extension. The main open problem is now the time-expanded lifting lemma needed to cover dynamic ownership, finite-capacity phases, and recomputation.

## Contents

- `docs/` — research notes, literature update, formal three-level model, static incremental theorem, general nested-partition theorem, hierarchical Steiner envelope, weighted rectangularization counterexample, arbitrary partition-boundary lemma, $L$-level/asymmetric-cost extension, phase/HBL multilevel interface, one-level recovery, nested-partition route, and proof obligations.
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
/opt/miniconda3/bin/python experiments/check_t3_static_hierarchical_theorem.py
/opt/miniconda3/bin/python experiments/check_l_level_static_theorem.py
/opt/miniconda3/bin/python experiments/check_small_partition_boundary.py
```

The last script classifies the 800 owner/chain combinations at $r=21,q=87$: 33 full-dimensional cells, 658 empty combinations, and 109 point-degenerate combinations. Every empty combination has a three-constraint Farkas certificate whose signs remain valid for $r\ge21$ under the current coefficientwise test. The point-degenerate combinations are deliberately kept separate; they are part of the remaining topology audit.

The one-level and normalized-envelope checks validate geometry only. `docs/t3-static-hierarchical-theorem.md` gives the proved static three-level vector theorem and matching tree schedule; `docs/nested-partition-static-theorem.md` extends it to arbitrary nested partitions and records a weighted non-rectangular counterexample; `docs/t3-partition-boundary-lemma.md` gives the arbitrary one-edge projection bound and a dynamic total-volume corollary. `docs/one-level-phase-hbl-lemma.md` records the separate recovered $n^3/(P\sqrt M)$ phase term and its remaining joint-capacity gap.

The large exact sweep is available as `experiments/check_2r_subfamily_large_exact_sweep.py`. It was run on a 160-core CPU host for 14 additional prime pairs and agreed with the candidate formula in every case.

## Status boundary

The repository records a complete tight theorem only for the explicitly stated static owner-consistent model. The arbitrary dynamic multilevel theorem is not finished: the remaining central question is whether a time-expanded owner schedule admits a compatible per-edge chain, or whether a small counterexample invalidates that strengthening. The 109 point-degenerate arrangement cases are secondary geometry evidence, not the proof target.

# Current research context

This file is the handoff context for the matrix-multiplication I/O-complexity exploration.

## Current theorem status (2026-10-04)

The project has moved beyond the original 109-cell arrangement enumeration. The
proved static results now include:

- a three-level nested-partition vector theorem and its arbitrary nested-partition
  generalization;
- a fixed-tree, arbitrary-leaf-demand Steiner/cut theorem with a matching
  memory-independent broadcast/reduction schedule;
- a full three-level rectangular row--\(k\)-block GEMM theorem, including
  asymmetric edge weights;
- a fresh-arrival \(L\)-level rectangular theorem. If \(H_\ell\) is the number of
  row groups and \(S_\ell\) the number of reduction groups below edge \(\ell\),
  then
  \[
  V_\ell\ge mk+H_\ell kn+S_\ell mn,
  \]
  with equality in the explicitly defined fresh-arrival schedule model.

The finite-capacity arbitrary-schedule theorem is still open. Its legal target is
the joint phase/cut trace envelope in `docs/finite-capacity-phase-cut-envelope.md`;
ownership and HBL terms cannot be added as independent scalars because their first
loads overlap. Free initial replication has a tight multi-source Steiner-forest
bound. Recomputation is only solved for a fixed event assignment; optimizing event
multiplicity together with resident traces and edge costs remains open.

The latest clarification is in `docs/recomputation-event-tradeoff.md`: for ordinary
classical GEMM, moving a product to a different owner is owner reassignment, not a
recomputation gain. A genuine recomputation theorem needs an externally constrained
event that is retained while a second event is created elsewhere. The next useful
experiment is a small integer search over event assignments and finite-capacity
traces, beginning with \(2\times2\times2\) products.

## Research question

Study tight I/O/communication lower bounds for matrix multiplication across sequential, two-level, multilevel, and parallel models. The literature notes cover Hong–Kung, classical GEMM, Strassen-like algorithms, distributed-memory lower bounds, symmetric kernels, and recent asymmetric-memory work. The current computational branch studies exact multilevel arrangements rather than claiming a new general parallel-GEMM lower bound.

## Active mathematical branch

For

\[
P^*=(2pq,pq,p),\qquad p=2r,\qquad q=4r+3,
\]

with the fixed divisor profile induced by distinct odd prime factors $r,q$, the sorted independent envelopes have 10, 5, and 2 lines. Eight compatible nested chains give the current upper envelope $U_8$. The candidate point and ratio are

\[
(z,y)=\left(\frac{2q+3}{5q},\frac1r\right),
\qquad
R=\frac{5qr(8q+13)}{28q^2r+15q^2+6qr^2+52qr+9r^2}.
\]

The independent-envelope cover is symbolic for $r\ge5$ within this fixed profile. The 33-cell branch at $r=21$ has a symbolic feasibility and ratio certificate for $r\ge21$. Exact $U_8/I$ checks cover 20 prime parameter pairs in the notes.

## Latest certificate

`experiments/prove_2r_subfamily_empty_cell_certificates.py` applies a two-dimensional Helly/Farkas search to all 800 owner/chain combinations at $r=21,q=87$:

```text
full empty point stable failed 33 658 109 658 0
failed []
```

Interpretation:

- 33 combinations are full-dimensional cells.
- 658 combinations are empty, and each has a three-constraint certificate whose determinant signs and contradiction remain coefficientwise valid after substituting $r=21+a$.
- 109 combinations are point-degenerate at $r=21$. They are not silently counted as empty; they remain the main topology-completeness task because a degenerate cell could, in principle, become full-dimensional after a parameter change.

The finite topology audit also found 33 cells with the same owner/chain signature at $r=21,23,50,100$, and at every integer $21\le r\le40$. This is evidence, not a substitute for the remaining symbolic treatment of the 109 degenerate cases.

## Reproducibility boundary

All claims in the notes distinguish:

1. exact finite arrangement results;
2. coefficientwise symbolic certificates for a named branch or cover;
3. empirical topology sweeps; and
4. the still-open no-new-cell completion argument.

Do not upgrade (2) or (3) into a general theorem without proving the point-degenerate cases and checking the full parameter domain.

## Conversation handoff

The original discussion asked for a Markdown research note, a current literature update on parallel tight lower bounds, and a concrete exploration of gaps. The notes in `docs/` preserve that discussion’s direction and the later computational refinements. The arrangement-cell branch is now secondary; the next concrete action is to solve the finite-capacity event-aware trace envelope and test whether it admits a closed form or a restricted tight schedule.

The consolidated theorem entry point is `docs/three-level-nested-main-theorem.md`;
its arithmetic certificate is `experiments/check_three_level_nested_main_theorem.py`.
A restricted symmetry-aware incidence extension is now recorded for SYRK and SYMM in
`docs/syrk-nested-incidence-extension.md`; finite-memory symmetric phase coupling
remains open.

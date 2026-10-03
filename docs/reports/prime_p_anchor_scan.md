# Prime-p anchor scan

The corrected symbolic pipeline was scanned beyond the initial $p=3,5,7$ cases. For each
prime $p$ in

\[
3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,
\]

we selected a prime anchor $q_0$ and checked:

1. symbolic dominance of every independent grid and every compatible nested chain;
2. quadratic Sturm roots with exact owner/domain filtering;
3. linear boundary, parallelism, identity, and triple events;
4. the finite q0-visible ratio candidate family against
   \[
   R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
   \]

## Anchor policy and result

For $p\le31$ we used $q_0=67$. For $p\ge37$ in the scan we used the smallest tested prime
strictly larger than $2p$:

| p | q0 | envelope cover | active topology | ratio sign |
|---:|---:|:---:|:---:|:---:|
| 3,5,7,11,13,17,19,23,29,31 | 67 | pass | pass | pass |
| 37 | 79 | pass | pass | pass |
| 41 | 83 | pass | pass | pass |
| 43 | 89 | pass | pass | pass |
| 47 | 97 | pass | pass | pass |
| 53 | 107 | pass | pass | pass |
| 59,61 | 127 | pass | pass | pass |
| 67 | 137 | pass | pass | pass |
| 71,73 | 149 | pass | pass | pass |
| 79 | 163 | pass | pass | pass |
| 83 | 167 | pass | pass | pass |
| 89 | 179 | pass | pass | pass |
| 97 | 197 | pass | pass | pass |
| 101 | 211 | pass | pass | pass |

For every row, the symbolic envelope-cover output is `uncovered=0`, the corrected event scans
have no active event on $0<u\le1/q_0$, and the ratio candidate has zero exact sign failures.

## Interpretation

This is evidence for a prime-p pattern with a threshold near $q_0>2p$, but it is not yet a
general theorem. The scan uses the three-level coordinate-divisibility model and a finite
arrangement certificate; the continuity lemma connecting no active events to the complete overlay
vertex set still needs to be written. The composite case $p=99$ behaves differently: $q_0=199$
has a stable topology but 204 ratio-branch sign failures, while $q_0=997$ passes. This separates
topology stabilization from the stronger global-ratio threshold.

## Direct exact-global cross-check

A separate full exact-overlay scan (`check_prime_p_global.py`) checked 141 instances for
$p=23,29,37,47,59,71,83,97$ over multiple prime q values. Every instance had the global
maximum at $(z,y)=(1,1/p)$ and matched
\[
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
\]
This is an empirical cross-check of the fixed-anchor certificates, not a theorem for arbitrary
prime p and q.

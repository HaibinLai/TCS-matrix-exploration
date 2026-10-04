# Dynamic-owner (2\times2\times2), (M=3): bounded-search report

## Question

Can dynamic reassignment of the eight products between two owners reduce the
fixed-row-owner value (Q=14) to (Q=13)? This report records the exact-search
attempt and its current boundary. It does **not** claim that (Q=13) is
impossible.

## Searched model

- (A,B,C\in\mathbb F^{2\times2}), two symmetric owners, local capacity
  (M=3).
- Each product ((i,k,j)) is computed exactly once and may be assigned to
  either owner.
- There is one root copy of every (A/B) entry. Direct root-to-owner (A/B)
  arrivals cost one word.
- A one-slot shared (B) cache ((G=1)) may receive a root arrival at cost one;
  promotion to either owner is free. This is the most favorable shared-(B)
  variant used in the search.
- The first (C_{ij}) accumulator is free. A dirty (C) must be stored at the
  root before eviction or migration (cost one); a root-current (C) reload costs
  one. Final (C) values must be current at the root.
- No recomputation and no free initial replication. Owner labels are
  canonicalized by swapping the two local resident masks.

A state is

\[
(D,L_0,L_1,G,R),
\]

where (D) is the completed-product mask, (L_o) is owner (o)'s resident
12-entry mask, (G) is the shared-(B) mask, and (R) records the four
root-current (C) values. Zero-cost transitions are product computation,
shared-to-local promotion, and (A/B) eviction; all root arrivals,
(C)-stores, (C)-reloads, and final writes are charged.

## Result and limitation

`experiments/exact_dynamic_owner_gemm_q13.py` performs a bounded 0/1 shortest-path
search, with an admissible missing-source/final-(C) heuristic in its A* variant.
The initial exact 0/1 search reached roughly 500,000 expanded states and about
2.4 million discovered states before being stopped for memory use (about
1.2 GB); it had not produced a terminal trace of cost at most 13. The A* variant
was also stopped before a terminal result. Therefore the search found neither a
(Q=13) witness nor a proof that (Q=13) is impossible.

The non-result is expected: dynamic owner choice creates many zero-cost cache
interleavings, while repeated shared-(B) arrivals and (C)-store/reload
migration preserve many resident states. Infeasibility of this incomplete run
cannot be used as a lower-bound proof.

## A promising analytic pruning route

A (Q\le13) trace has only one word above the baseline of four distinct (A)
arrivals, four distinct (B) arrivals, and four final (C) writes. This yields a
small case split for a future proof:

1. If no (A/B) source is replicated, every product's (A_{ik}) and (B_{kj})
   must meet at the same owner. The connected incidence graph forces all input
   labels, and hence all products, onto one owner.
2. If products are split between owners while every (C_{ij})'s two terms stay
   together, the change in owner labels across rows/columns forces input
   replication. A candidate (Q=13) proof would need to show that any
   nonconstant output-owner pattern requires at least two replicated (A/B)
   entries, not merely one.
3. If a (C_{ij})'s two terms are assigned to different owners, at least one
   extra (C)-movement is consumed by partial migration. The remaining budget
   then allows no input replication, returning to case 1.
4. The remaining single-owner case needs a separate small lemma: a one-owner
   (2\times2\times2) GEMM with (M=3) requires at least two words beyond the
   (A/B)-source plus final-(C) baseline. The existing exact toy search is
   evidence for this but uses a different final-write convention, so it has not
   been promoted to a theorem here.

Thus the next useful target is a finite classification of product-owner label
patterns under one extra source/partial event, followed by a clean single-owner
(M=3) lemma. This is substantially smaller than enumerating arbitrary dynamic
traces.

## Subsequent analytic resolution

The bounded search itself was inconclusive, but the search question is now resolved
for this model by the cube-boundary theorem in
`docs/dynamic-owner-q14-theorem.md`: a (Q\le13) trace has at most one extra
word, which forces each fixed-(i) ((k,j)) layer to have a constant owner.
The resulting constant-owner and row-owner cases both need two extra words, so
(Q^*=14). The large-state search remains useful only as a diagnostic and is not
used as the proof.

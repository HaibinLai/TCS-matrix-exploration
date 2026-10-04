# Dynamic-owner (2\times2\times2) lower bound at (M=3)

This note closes the (Q=13) question in a specific but useful finite-capacity
model. It combines a cube-coloring argument with the two (M=3) lemmas in the
finite-trace notes.

## Model and baseline

Let (A,B,C\in\mathbb F^{2\times2}). There are two owners, each with local
capacity (M=3). Every product ((i,k,j)) is computed exactly once, and its
owner may be chosen dynamically. The root has one copy of each (A/B) entry;
there is a one-slot shared (B) cache. A single root-to-shared arrival of
(B_{kj}) can be promoted for free to either owner. There is no free initial
replication and no recomputation.

A first (C_{ij}) accumulator is free. Partial (C) movement, root reloads,
and final (C) write-backs are charged one word per crossing. Direct owner-to-owner
transfers, if used, are also charged. The baseline source/final accounting is

\[
Q_{\rm base}=4\;A\text{-source words}+4\;B\text{-source words}
              +4\;C\text{-final words}=12.
\]

The shared (B) cache is deliberately favorable: splitting two products that
share a (B_{kj}) does not by itself cost above the one baseline (B)-arrival.

## Cube boundary lemma

Represent the eight products as vertices (v=(i,k,j)\in\{0,1\}^3), and color a
vertex by its owner. The four (A_{ik}) entries are the edges that change (j);
the four (C_{ij}) entries are the edges that change (k). If the endpoints of
an (A)-edge have different owners, one (A) source copy must cross to both
owners (or be transferred), costing at least one extra word beyond its baseline
arrival. The analogous statement holds for a (C)-edge: two owners computing
the
two terms require at least one extra partial/root movement beyond the final
write. Let (b_{AC}) be the number of bichromatic (A/C) edges.

For fixed (i), the four vertices ((i,k,j)) form a cycle in the ((k,j)
plane. A two-coloring of a cycle has an even number of bichromatic edges; if the
layer is nonconstant, it has at least two. Consequently

\[
b_{AC}\le1\quad\Longrightarrow\quad
f(i,k,j)=r_i\quad\text{for some }r_0,r_1\in\{0,1\}.
\tag{CUBE}
\]

The finite checker `experiments/check_dynamic_owner_q13_obstruction.py` enumerates
all (2^8) owner assignments and confirms that the only assignments with
(b_{AC}\le1) are the four row-constant patterns. The proof is the cycle parity
argument, so the enumeration is only a sanity check.

## The (Q=13) contradiction

Suppose (Q\le13). Relative to (Q_{\rm base}=12), at most one extra word is
available. Every bichromatic (A/C) edge consumes at least one such extra word,
so (b_{AC}\le1). By (CUBE), the owner assignment is constant on each row:

- If (r_0=r_1), all eight products are computed by one owner. The one-owner
  (M=3) lemma gives (Q\ge14): consider the first two products. They share
  at most one of their three data entries. The other two entries of the first
  product each have a later second use, but at the second product the three
  entries of that product already occupy all three slots. Both first-product
  entries must therefore be reloaded or moved later, yielding at least two words
  beyond the (12)-word baseline.
- If (r_0\ne r_1), this is the fixed row-owner model. The row-owner lemma gives
  (a_i+c_i\ge5) for each owner: with only two (A)-arrivals and two final
  (C)-writes, the first two products would require at least four local slots.
  Since the shared (B) source still needs four distinct arrivals,
  (Q\ge5+5+4=14).

Both cases contradict (Q\le13). The row-split schedule with (G=1) and
(M=3) attains (Q=14), so

\[
\boxed{Q^*_{\rm dynamic\ owner}(2\times2\times2,M=3,G=1)=14}
\]

under the stated one-copy/no-recomputation/root-(C) model.

## Boundary of the theorem

The argument relies on one baseline (B)-arrival being able to serve both owners,
which is why only (A/C) cube edges are charged. It does not cover free initial
replication, recomputation, a different C-reduction network, or capacities and
costs that allow an uncharged owner-to-owner copy. Those changes require a new
edge-cost model.

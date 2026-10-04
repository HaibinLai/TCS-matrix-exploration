# Restricted finite-capacity shared-B/C trace and row-owner lower bound

This note records an exact finite-state result for a deliberately restricted
\(2\times2\times2\) GEMM trace, followed by an analytic bound for the wider
fixed-row-owner model. The finite-state certificate itself is not a claim about the
general E-TRACE optimum.

## Model

Let \(A,B,C\in\mathbb F^{2\times2}\). Owner \(i\) computes the four products
\((i,k,j)\) for its row \(i\). Each owner has local capacity \(M\). A child-group
shared cache has \(G=1\) and stores only \(B\) entries.

The parent sends each of the four \(B_{kj}\) entries exactly once, in an arbitrary
permutation. Each shared arrival costs one word and can be promoted to either owner
for free. Direct \(B\) loads are prohibited in this restricted model.

An \(A\) arrival to its owner costs one word. The first \(C_{ij}\) accumulator is
created for free. If an initialized accumulator is evicted, its current partial is
stored at the root at cost one; a later root-to-owner reload costs one. Each final
\(C\) value must be current at the root. Products are computed once. Arithmetic,
\(A/B\) eviction, and shared-to-local promotion are free.

## Exact restricted theorem

Let \(Q_M^{(1\text{-}B)}\) be the minimum total edge volume in this model. Then

$$
Q_3^{(1\text{-}B)}=14,
\qquad
Q_4^{(1\text{-}B)}=12.
\tag{RST}
$$

For the correct four entries \(B_{00},B_{01},B_{10},B_{11}\), the exact local cost
depends on the arrival permutation when \(M=3\): it is \(5\) for eight permutations
and \(6\) for the other sixteen. For \(M=4\), every permutation has local
cost \(4\). Therefore the minimum over permutations is

$$
\min q_3^{\rm row}=5,
\qquad
\min q_4^{\rm row}=4,
$$

where local cost includes \(A\) arrivals, \(C\) reloads/stores, and final write-back,
but excludes the four shared-arrival words. Hence the restricted-model minima are

$$
\min Q_3^{(1\text{-}B)}=4+2\cdot5=14,
\qquad
\min Q_4^{(1\text{-}B)}=4+2\cdot4=12.
$$

The memory-independent source/copy plus final-write baseline is \(4+4+4=12\): four \(A\) words, four shared-\(B\) words, and four final \(C\) words. Hence \(M=3\) has an exact restricted-capacity penalty of two words, while \(M=4\) attains the baseline.

## Why it matters

The result includes C partial lifetime and final write-back. Shared-B reuse reduces
the B lineage to four arrivals, but three local slots cannot avoid all accumulator
stores/reloads for the optimal one-use B order. The extra two words are invisible
to the memory-independent copy count and arise from the local resident trace; an
unfavorable arrival order can cost one more local word.

The finite-state certificate is restricted to one arrival per \(B\) entry. The
row-split argument below removes that arrival restriction from the lower bound,
while retaining fixed row ownership, one-copy input, and no recomputation.

## Exact certificate

`experiments/check_restricted_shared_c_full_trace.py` performs a 0/1 shortest-path
enumeration of all 24 shared-B arrival permutations. A state records the current
arrival index, completed products, local resident set, and which C values are current
at the root. It allows arbitrary local action order, C reloads, C stores on eviction,
and final write-back.

The checker reports:

```text
M 3 owner costs [5, 6] minimum 5
M 4 owner costs [4] minimum 4
restricted shared-C full-trace check=True
M=3,G=1,one-arrival-per-B minimum total=14
M=4,G=1,one-arrival-per-B total=12
```

Because the shortest-path graph contains every legal trace in this restricted model
and every transition has its stated word cost, the result is exact and tight for
that trace class.

## A stronger row-split lower bound

The exact certificate suggests a short analytic argument that removes the
one-arrival-per-\(B\) restriction from the **lower bound**. Keep the one-copy
input and no-recomputation assumptions, but allow arbitrary shared or direct
\(B\)-delivery. For owner \(i\), let \(a_i\) count all arrivals of its two
\(A\)-entries and let \(c_i\) count all movements of its two \(C\)-accumulators
(stores, reloads, and final write-backs). Then

\[
a_i+c_i\ge 5\qquad(M=3).
\tag{ROW-AC}
\]

Indeed \(a_i\ge2\) and \(c_i\ge2\). If equality \(a_i+c_i=4\) held, each
\(A_{ik}\) would be loaded exactly once and remain resident until its second
use, while each \(C_{ij}\) would remain resident from its first product through
its second product and cross the edge only at its final write. Consider the first
two products in the owner's order. If they use the same \(k\) and different \(j\), the two \(C\)-entries and one \(A\)-entry must remain resident; if they use different \(k\) and the same \(j\), the two \(A\)-entries and one \(C\)-entry must remain resident; if both coordinates differ, all four are active. In every
case the current \(B\)-entry adds another resident word, requiring at least four
local slots. This contradicts \(M=3\). Thus one extra \(A\)-arrival or \(C\)-movement
is unavoidable, proving (ROW-AC).

At least one source-to-child/owner transfer is required for each of the four
distinct \(B\)-entries, so \(Q_B\ge4\). Consequently every fixed-row-owner,
one-copy, no-recomputation \(2\times2\times2\) execution with \(M=3\) satisfies

\[
Q\ge (a_0+c_0)+(a_1+c_1)+Q_B
  \ge 5+5+4=14.
\tag{ROW-LB}
\]

The \(G=1\), one-arrival-per-\(B\) witness certified above attains 14, so this
is an exact unrestricted result **within the fixed row-owner model**, even
though the matching schedule happens to lie in the restricted class. It still
does not cover dynamic owner reassignment, free initial replication,
recomputation, or a shared \(C\)-partial/reduction path.

# Restricted finite-capacity shared-B/C trace

This note records an exact finite-state result for a deliberately restricted
(2\times2\times2) GEMM trace. It is a certificate for a useful submodel, not a
claim about the unrestricted E-TRACE optimum.

## Model

Let (A,B,C\in\mathbb F^{2\times2}). Owner (i) computes the four products
((i,k,j)) for its row (i). Each owner has local capacity (M). A child-group
shared cache has (G=1) and stores only B entries.

The parent sends each of the four (B_{kj}) entries exactly once, in an arbitrary
permutation. Each shared arrival costs one word and can be promoted to either owner
for free. Direct B loads are prohibited in this restricted model.

An A arrival to its owner costs one word. The first (C_{ij}) accumulator is
created for free. If an initialized accumulator is evicted, its current partial is
stored at the root at cost one; a later root-to-owner reload costs one. Each final
C value must be current at the root. Products are computed once. Arithmetic,
A/B eviction, and shared-to-local promotion are free.

## Exact restricted theorem

Let (Q_M^{(1\text{-}B)}) be the minimum total edge volume in this model. Then

$$
Q_3^{(1\text{-}B)}=14,
\qquad
Q_4^{(1\text{-}B)}=12.
\tag{RST}
$$

For every permutation of the four shared-B arrivals, the exact local cost of one
row owner is

$$
q_3^{\rm row}=5,
\qquad
q_4^{\rm row}=4,
$$

where local cost includes A arrivals, C reloads/stores, and final write-back, but
excludes the four shared-arrival words. Thus

$$
Q_M^{(1\text{-}B)}=4+2q_M^{\rm row}.
$$

The memory-independent source/copy plus final-write baseline is
(4+4+4=12): four A words, four shared-B words, and four final C words. Hence
(M=3) has an exact restricted-capacity penalty of two words, while (M=4)
attains the baseline.

## Why it matters

The result includes C partial lifetime and final write-back. Shared-B reuse reduces
the B lineage to four arrivals, but three local slots cannot avoid all accumulator
stores/reloads for every possible one-use B order. The extra two words are invisible
to the memory-independent copy count and arise from the local resident trace.

The result becomes an unrestricted lower bound only after proving that repeated
shared-B arrivals or direct B loads cannot reduce the total below 14. That step is
still open.

## Exact certificate

`experiments/check_restricted_shared_c_full_trace.py` performs a 0/1 shortest-path
enumeration of all 24 shared-B arrival permutations. A state records the current
arrival index, completed products, local resident set, and which C values are current
at the root. It allows arbitrary local action order, C reloads, C stores on eviction,
and final write-back.

The checker reports:

```text
M 3 owner costs [5]
M 4 owner costs [4]
restricted shared-C full-trace check=True
M=3,G=1,one-arrival-per-B total=14
M=4,G=1,one-arrival-per-B total=12
```

Because the shortest-path graph contains every legal trace in this restricted model
and every transition has its stated word cost, the result is exact and tight for
that trace class.

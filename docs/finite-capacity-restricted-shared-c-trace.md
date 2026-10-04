# A restricted finite-capacity breakthrough: shared-B, row-split (2\times2\times2)

## Model

Consider (C=AB) with (A,B,C\in\mathbb F^{2\times2}). Owner (i) computes
exactly the four products ((i,k,j)) for its row (i). Each owner has local
capacity (M). A child-group shared cache has capacity (G=1) and is used only
for (B)-entries. The parent sends each of the four (B_{kj}) entries exactly
once, in an arbitrary permutation; each such shared arrival costs one word and
can be promoted for free by either owner. Direct (B)-loads are prohibited in
this restricted model.

An (A)-arrival to its owner costs one word. The first (C_{ij}) accumulator
is created for free. If an initialized accumulator is evicted, the current
partial is stored at the root at cost one; a later root-to-owner reload costs
one. At the end each of the four final (C)-values must be current at the root.
Products are computed once and arithmetic is free. Evictions of (A) or (B)
and shared-to-local promotions are free.

This is a deliberately narrow trace class. It isolates the interaction between
one-use shared-(B) arrivals, three-word local capacity, and (C)-accumulator
lifetime. It does not claim the unrestricted optimum, where a (B)-entry may
arrive repeatedly or be loaded directly.

## Exact restricted theorem

Let (Q_{M}^{(1\text{-}B)}) be the minimum total edge volume in this model. Then

\[
Q_{3}^{(1\text{-}B)}=14,
\qquad
Q_{4}^{(1\text{-}B)}=12.
\tag{RST}
\]

More explicitly, for **every** permutation of the four shared (B)-arrivals,
the exact minimum local cost of one row owner is

\[
q_3^{\rm row}=5,
\qquad q_4^{\rm row}=4,
\]

where local cost includes (A)-arrivals, (C)-reloads/stores, and final
write-back but excludes the four shared-arrival words. Therefore

\[
Q_M^{(1\text{-}B)}=4+2q_M^{\rm row}.
\]

The static one-copy plus final-write baseline is (4\) (A)-words (+4)
shared (B)-words (+4) final (C)-words (=12). Thus (M=3) has an exact
restricted-capacity penalty of two words:

\[
Q_3^{(1\text{-}B)}-12=2.
\]

At (M=4), the baseline is attained.

## Why the result is useful

The result gives a concrete overlap obstruction with (C)-partials included.
A shared (B) arrival can be reused by both owners, but with only three local
slots an owner cannot keep the two (A)-values and both (C)-lifetimes while
streaming all four one-use (B)-events. The extra two words are not visible in
the memory-independent source/copy count; they arise from the local accumulator
trace. This is precisely the finite-capacity coupling that a scalar sum of a
Steiner cut term and a phase/HBL term cannot represent.

The statement is intentionally a restricted theorem. It becomes a genuine
unrestricted lower bound only after proving that repeated shared arrivals or
direct (B)-loads cannot reduce the total below 14, which is still open.

## Exact certificate

`experiments/check_restricted_shared_c_full_trace.py` performs a 0/1 shortest-path
enumeration of every local resident state for all (4!=24) arrival permutations.
A state records the current arrival index, completed products, local resident
set, and which (C)-values are current at the root. It allows arbitrary local
action order, (C)-reloads, (C)-stores on eviction, and final write-back.

The checker reports

```text
M 3 owner costs [5]
M 4 owner costs [4]
restricted shared-C full-trace check=True
M=3,G=1,one-arrival-per-B total=14
M=4,G=1,one-arrival-per-B total=12
```

Because the shortest-path graph contains every legal trace in the stated
restricted model and every transition has its exact word cost, the finite result
is both a lower-bound certificate and a matching-schedule certificate for that
trace class. It is not evidence for the unrestricted (E\)-TRACE optimum.

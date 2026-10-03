# Nested-partition HBL theorem: a less restrictive route

The static-grid ownership lemma assumes rectangular block ownership from the start. A more general route is to optimize over arbitrary nested partitions of the classical GEMM product set, and only later prove that rectangular grids are optimal.

## Product set and projections

Let

\[
T=[m]\times[k]\times[n]
\]

be the set of scalar products. For a subset $S\subseteq T$, define its input/output projections

\[
\pi_A(S)\subseteq[m]\times[k],\quad
\pi_B(S)\subseteq[k]\times[n],\quad
\pi_C(S)\subseteq[m]\times[n].
\]

Loomis–Whitney gives

\[
|S|\le
\sqrt{|\pi_A(S)|\cdot|\pi_B(S)|\cdot|\pi_C(S)|}.
\]

For a balanced partition $\Pi=\{S_1,\ldots,S_P\}$, define the projection boundary

\[
\partial(\Pi)=
\sum_{r=1}^{P}
\bigl(|\pi_A(S_r)|+|\pi_B(S_r)|+|\pi_C(S_r)|\bigr)
-(mk+kn+mn).
\]

The subtraction removes one initially owned copy of each matrix entry. If initial replication is allowed, its copies must be added to the initial term instead of being free.

## Partition lower-bound statement

For a one-time classical GEMM schedule whose product ownership at a communication edge induces partition $\Pi_\ell$, the edge volume satisfies

\[
V_\ell\ge \partial(\Pi_\ell)-\text{initial copies}_\ell.
\]

The reason is direct: every entry in a projection must be available to the owner group that computes a product using it; every partial output in a $C$-projection must either cross the edge or be the final owner. The HBL inequality limits how many products a part can cover for a given projection budget.

## Nested hierarchy

Let $\Pi_1,\Pi_2,\Pi_3$ be partitions induced at the three charged edges. If ownership is nested, every part at a finer edge lies inside a part at the next coarser edge. Write

\[
\Pi_3\preceq\Pi_2\preceq\Pi_1.
\]

The resulting arbitrary-partition lower-bound envelope is

\[
B_{\mathrm{part}}(m,k,n)=
\min_{\Pi_3\preceq\Pi_2\preceq\Pi_1}
\sum_{\ell=1}^{3}
\partial(\Pi_\ell),
\]

up to initial-copy and output boundary terms.

This is a weaker but more general target than the current grid envelope: rectangular block partitions are only a subset of all partitions, so

\[
B_{\mathrm{part}}
\le
B_{\mathrm{grid}}.
\]

The missing **rectangularization theorem** would show that, under balanced classical GEMM and the chosen cost model, an optimizer of $B_{\mathrm{part}}$ can be replaced by nested rectangular blocks without increasing the boundary. Only then can the current 25-line $N(z,y)$ be promoted from a grid-restricted bound to an arbitrary-schedule bound.

## Current evidence

`work/check_small_partition_boundary.py` exhaustively enumerates balanced partitions of the $2\times2\times2$ product set:

```text
P=2 partitions=35 min_boundary=4 rectangular_min=4
P=4 partitions=105 min_boundary=8 rectangular_min=8
small partition boundary check=True
```

This supports rectangularization in the smallest cases but proves nothing for general dimensions or three nested partitions.

## Why this route matters

It separates two logically different claims:

1. **Partition/HBL theorem:** arbitrary schedules pay a projection boundary;
2. **Rectangularization theorem:** rectangular nested grids attain the minimum boundary.

The first claim is closer to a general communication lower bound. The second is the exact bridge to the current factor/divisor arrangement. If rectangularization fails, the correct theorem should use $B_{\mathrm{part}}$, and the grid experiments become upper-bound constructions or special cases rather than universal lower bounds.

# Finite-arrangement continuity lemma

This memo records the proof bridge needed by the fixed-anchor certificates.

## Setting

Let $D=\{(z,y):0\le y\le z\le1\}$, and let each envelope family be a finite set of
affine lines

\[
\ell_i(u,z,y)=a_i(u)+b_i(u)z+c_i(u)y,
\]

where every coefficient is affine in $u=1/q$. For independent families $E_1,E_2,E_3$ and a
nested family $E_N$, write

\[
I(u,z,y)=\sum_{r=1}^3\min_{\ell\in E_r}\ell(u,z,y),
\qquad
N(u,z,y)=\min_{\ell\in E_N}\ell(u,z,y).
\]

Assume $I>0$ on the region under consideration.

## Lemma (active-envelope continuity)

Let $J=(u_-,u_+)$ be an interval on which the following events do not occur for any envelope:

1. an equality line of two candidate lines passes through a vertex of $D$;
2. an equality line becomes parallel to a boundary of $D$ while carrying an active envelope edge;
3. three candidate equality lines become concurrent at a point of $D$ while all three attain the
   envelope minimum;
4. two candidate lines become identical on an active envelope segment.

Then the active lower-envelope edge complex of every envelope is combinatorially constant on $J$.
Consequently, the overlay of the four active envelope complexes has a fixed finite set of vertex
branches. Each branch has coordinates that are rational functions of $u$ on $J$.

### Proof sketch

An active envelope edge is a connected component of a pairwise equality line after clipping by $D$
and by the inequalities against all other candidate lines. Its endpoints can change only when an
endpoint reaches a vertex of $D$, when the equality direction becomes parallel to a boundary, when
another equality cuts the edge at a triple concurrence, or when two lines become identical. These
are exactly events 1--4. In their absence, endpoint order and all active-owner inequalities are
locally constant. Since $J$ is connected and the arrangement is finite, the active edge complex is
constant throughout $J$. Intersections of pairs of affine equality lines then give rational
coordinate functions for every overlay vertex branch.

## Ratio reduction

On any fixed overlay cell, the four envelope owners are fixed, so $N$ and $I$ are affine in
$(z,y)$. The ratio $N/I$ is linear-fractional. Along every line segment in a polygon, a
linear-fractional function with positive denominator is monotone or constant, so its maximum is
attained at a segment endpoint. Repeating over the cell gives

\[
\max_{(z,y)\in D}\frac{N}{I}
\quad\text{at an overlay vertex or a vertex of }D.
\]

Therefore, if every fixed vertex branch $v(u)$ satisfies

\[
R_*(u)I(u,v(u))-N(u,v(u))\ge0,
\]

then $N/I\le R_*$ everywhere on the whole interval $J$.

## Endpoint handling

The point $u=0$ may contain duplicate lines and a different combinatorial complex. It must be
checked by a separate exact overlay, followed by a comparison with the limiting value of $R_*$.
This is why the p=99 certificate has two parts: the positive interval $(0,1/997]$ and the exact
degenerate slice $u=0$.

## What remains for a publishable theorem

The corrected event checker now evaluates domain and owner signs at isolated algebraic roots using
polynomial gcd/Sturm sign tests rather than a floating midpoint. A formal theorem still needs to
state the candidate line families for the chosen prime-$p$ template and connect the finite
certificate to all prime-$q$ grids in prose. The lemma above is the combinatorial bridge; it is not
itself a claim that the arbitrary-$p$ or multilevel theorem is done.

# Radial monotonicity certificate for the prime hierarchy family

Consider the three-level family
\[
(P_1^*,P_2^*,P_3^*)=(2pq,pq,p),\qquad q>2p,\qquad p\ge3,
\]
with normalized coordinates
\[
(x,z,y)=(1,s,st),\qquad 0\le s,t\le1.
\]
For a grid line \(\ell=(a,b,c)\), its cost is
\[
H_\ell(1,s,st)=a+s(b+ct).
\]
On a cell where the numerator envelope uses \(n\) and the three independent envelopes use
\(i_1,i_2,i_3\), write
\[
N=n_0+s(n_1+n_2t),\qquad
I=i_0+s(i_1+i_2t).
\]
Then the sign of the radial derivative is the sign of the affine polynomial
\[
D(t)=(n_1+n_2t)i_0-n_0(i_1+i_2t).
\]
Thus it is enough to check the endpoints of the cell's projected \(t\)-interval.

## Eight-cell template for q>2p

The exact half-plane feasibility checker finds eight full-dimensional active combinations in the tested
prime cases. The rows below list the nested chain, the three independent grids, and the projected
interval or subinterval for \(t\). Permutations of factor labels are written with \(p,q\).

| row | nested chain | independent grids | t-range | derivative numerator \(D(t)\) |
|---:|---|---|---|---|
| 0 | \((p,q,2),(p,q,1),(p,1,1)\) | \((q,p,2),(q,p,1),(p,1,1)\) | \([1/p,1]\) | \(\frac{3(p-q)(q+2)(t-1)}{2p^2q^2}\) |
| 1 | \((2pq,1,1),(pq,1,1),(p,1,1)\) | same three grids | subinterval of \([0,1/(pq)]\) | \(0\) |
| 2 | \((pq,2,1),(pq,1,1),(p,1,1)\) | row 0 independent grids | subinterval of \([1/q,1/p]\) | \(D_2(t)\) |
| 3 | row 2 nested chain | \((pq,2,1),(pq,1,1),(p,1,1)\) | subinterval of \([1/(pq),1/q]\) | \(0\) |
| 4 | row 2 nested chain | \((2q,p,1),(q,p,1),(p,1,1)\) | subinterval of \([1/q,1/p]\) | \(\frac{(3p-4)(2q+3)(qt-1)}{4p^2q^2}\) |
| 5 | \((2p,q,1),(p,q,1),(p,1,1)\) | row 0 independent grids | subinterval of \([1/p,1]\) | \(D_5(t)\) |
| 6 | row 5 nested chain | \((q,2p,1),(q,p,1),(p,1,1)\) | subinterval of \([\min(1/p,p/q),1]\) | \(\frac{(4p-3q)(2q+3)(t-1)}{4p^2q^2}\) |
| 7 | row 5 nested chain | \((2q,p,1),(q,p,1),(p,1,1)\) | subinterval of \([\min(1/p,p/q),\max(1/p,p/q)]\) | \(\frac{(p-q)(2q+3)(4t-3)}{4p^2q^2}\) |

The two remaining derivative polynomials are
\[
D_2(t)=\frac{6pq^2t+14pqt-6pq-9p-6q^2t-9qt+10q+16}{4p^2q^2},
\]
\[
D_5(t)=\frac{10pqt-6pq+16pt-9p-6q^2t+6q^2-9qt+14q}{4p^2q^2}.
\]
They are affine in \(t\), and share the endpoint expression
\[
D_2(1/p)=D_5(1/p)=-\frac{A(p,q)}{4p^3q^2},
\]
where
\[
A(p,q)=6p^2q+9p^2-6pq^2-24pq-16p+6q^2+9q.
\]
Writing \(q=2p+r\),
\[
A=-12p^3-18p^2r-15p^2-6(p-1)r^2+2p+9r<0
\]
for \(p\ge3,r>0\). Also
\[
D_2(1/q)=\frac{5p+4q+7}{4p^2q^2}>0,
\qquad
D_5(1)=\frac{4pq+7p+5q}{4p^2q^2}>0.
\]
Therefore rows 2 and 5 are nonnegative on their stated intervals. Rows 0, 4, 6, and 7 are nonnegative from
\(q>2p\), \(p\ge3\), \(t\le1\), and
\(t\le\max(1/p,p/q)\le1/2<3/4\) for row 7.

**Conditional conclusion.** Once the eight-cell active template is established for all prime \(q>2p\),
these formulas prove that \(N(1,s,st)/I(1,s,st)\) is nondecreasing in \(s\). Combined with the exact
boundary theorem, this would prove the full two-dimensional sharp formula
\[
\max_{0\le y\le z\le1}\frac{N(z,y)}{I(z,y)}
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
\]
The remaining logical step is the parameterized proof that no other full-dimensional active combination
appears for arbitrary prime \(q>2p\); the current arrangement checker verifies this exactly for the cases below.

## Exact checks

`work/check_prime_radial_cells.py` uses exact rational half-plane feasibility, ignores degenerate boundary-only
combinations, and checks the derivative on each feasible cell's exact projected \(t\)-range. Results:

```text
p=3  q=29  active=(16,8,3)/16  feasible_cells=8  bad=0
p=5  q=29  active=(16,8,3)/16  feasible_cells=8  bad=0
p=23 q=67  active=(16,8,3)/16  feasible_cells=8  bad=0
p=37 q=79  active=(16,8,3)/16  feasible_cells=8  bad=0
p=97 q=197 active=(16,8,3)/16  feasible_cells=8  bad=0
```

A separate exact rational grid scan at step \(1/80\) checked 52 additional \((p,q)\) cases and found no
negative radial increment. The grid scan is diagnostic; the eight-cell check is the stronger finite-cell
certificate.

The purely symbolic derivative algebra is reproducible with:

```bash
python work/prove_prime_radial_derivatives.py
```

It prints the eight factored derivatives and verifies the shared endpoint polynomial identity,
ending with `symbolic derivative certificate=True under p>=3, q>2p`.

## Four-chain reduction

A stronger simplification is available for the upper-bound direction. Let \(U\) be the minimum of only
four legal chain costs, corresponding to rows 1, 2, 5, and 0 of the table. Since \(N\le U\), an exact
certificate for \(U/I\le R_p(q)\), together with equality at \((1,1/p)\), proves the desired result for
\(N/I\) without classifying all 16 nested active lines.

`work/check_prime_four_chain_bound.py` enumerates the exact arrangement of the 16/8/3 independent
active lines and these four chain lines, checks the global maximum, verifies all full-dimensional radial
cells, and checks equality with the true nested envelope at the witness. It completed 19 cases with
`cells=8`, `radial_bad=0`, and `witness_equality=True`:

```text
(p,q) = (3,29),(3,67),(3,79),(3,197),(3,211),
        (5,29),(5,67),(5,79),(5,197),(5,211),
        (23,67),(23,79),(23,197),(23,211),
        (37,79),(37,197),(37,211),
        (97,197),(97,211).
```

This turns the remaining universal step into a smaller statement: prove the eight-cell active template
for the four-chain upper envelope \(U/I\) whenever \(q>2p\). The finite certificates already show
that this upper envelope has the same sharp value as the full nested envelope in the tested cases.

## Independent-envelope cover is now symbolic

`work/prove_prime_independent_cover.py` fixes the 16/8/3 candidate grids and proves that every
omitted divisor grid is dominated on the full triangle by one of them. Since line differences are affine
in \((z,y)\), it suffices to check the three triangle vertices. The script then substitutes
\(p=3+a\), \(q=2p+r\) and verifies coefficientwise nonnegativity for \(a,r\ge0\).

It reports 12 omitted grids and ends with:

```text
symbolic independent-cover certificate=True omitted=12
```

Thus the independent envelopes do not require a numerical active-line assumption for \(p\ge3,q>2p\).
The remaining parameterized step is only the eight-cell arrangement of these fixed candidate lines with
the four-chain upper envelope.

## Closure of the conditional gap

The earlier conditional wording can now be removed. The fixed candidate lines reduce the independent
envelopes exactly to \(m_0=\min(A,B,C,D,E)\), \(m_1=\min(F,G)\), with the p-level line \(H\).
The four-chain upper envelope reduces to the three t-regimes in
`prime_family_full_theorem.md`. Its possible minima pair only in the seven derivative cases listed
there; all seven signs are proved under \(p\ge3,q>2p\). Thus the eight-cell arrangement need not be
proved separately. Together with the boundary theorem and the witness equality, this gives a complete
restricted-family theorem.

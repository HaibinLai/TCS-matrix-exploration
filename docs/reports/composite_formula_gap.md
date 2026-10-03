# Composite-p stress test and counterexamples

The sharp formula proved for prime \(p\),
\[
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},
\]
does not extend to composite \(p\). Extra divisor grids change both independent and nested
lower envelopes.

## First full-dimensional counterexample

For \(p=6,q=13\), so \((P_1^*,P_2^*,P_3^*)=(156,78,6)\), the complete exact arrangement gives
\[
\max N/I=\frac{135}{113}=1.1946902654867257
\]
at
\[
(z,y)=\left(1,\frac{29}{195}\right).
\]
The prime-family formula would predict
\[
R_6(13)=\frac{248}{213}=1.164319248826291,
\]
so it is strictly false for this composite parameter. At the maximizing point,
\[
I=\frac{113}{180},\qquad N=\frac34.
\]
One minimizing independent configuration is
\[
(26,2,3),\quad(13,2,3),\quad(6,1,1),
\]
and one minimizing nested chain is
\[
(39,2,2)\to(39,1,2)\to(3,1,2).
\]
The exact checker reports 54/27/9 total grids, active independent counts 24/16/8, 32 active nested
lines, and 224434 arrangement vertices.

## Larger exact counterexample at the old witness point

For \(p=49,q=101\), the complete exact arrangement gives
\[
\max N/I=\frac{11221}{8039}=1.3958203756686156
\]
at \((z,y)=(1,1/49)\). The prime-family expression is
\[
\frac{11221}{9349}=1.2002353193\quad\text{(strictly smaller)}.
\]
The exact checker reports 54/18/6 total grids, active independent counts 25/10/5, 25 active nested
lines, and 152740 arrangement vertices. At the maximizer, an independent minimizer uses
\((202,7,7)\) at the outer level and \((101,7,7)\) at the middle level; the square factor
\(49=7^2\) is split across grid dimensions.

## Boundary scan

`work/scan_composite_formula_gap.py` checks composite \(p\le50\) and prime \(q\le500\) with
\(q>2p\). It finds 1247 exact boundary counterexamples. The largest discrepancies in this range
include:

```text
p=49 q=101  boundary=11221/8039  prime-formula=11221/9349
p=45 q=97   boundary=2200/1571    prime-formula=75/62
p=35 q=71   boundary=595/433       prime-formula=665/557
p=25 q=53   boundary=3025/2228     prime-formula=3025/2521
```

This shows that the prime assumption is structural: it is not a proof convenience. A general theorem
must be indexed by the divisor profile of \(p\), or use a different invariant than the scalar parameter
\(p\). The exact scan output is saved in
`work/agent_reports/composite_formula_gap_scan.txt`.

## Interior composite counterexamples

Composite factorization can move the global maximizer into the interior of the normalized triangle:

```text
p=10, q=23: max=4531/3666 at (z,y)=(49/115,1/5)
p=14, q=29: max=248675/196974 at (z,y)=(61/145,1/7)
```

These are full exact 2-D arrangement results, not boundary scans. For p=10, the boundary maximum is
`4925/4001`, so the interior point is strictly larger. For p=14, the boundary maximum is
`8575/6957`, also strictly smaller. The points suggest a factor-profile family with p=2r, but the
formula changes as q crosses further divisor-dependent thresholds; no general composite theorem is
claimed.

## Additional exact cases from retreat

Two larger complete exact arrangements were run on the retreat CPU:

```text
p=22, q=47: max=1005565/775602 = 1.2964961410620395
             at (z,y)=(97/235,1/11)
p=26, q=53: max=1505465/1155702 = 1.302641165283092
             at (z,y)=(109/265,1/13)
```

Both runs have 54/27/9 candidate grids, 24/16/8 active independent lines, and 31 active nested
lines. The arrangement sizes are 289015 and 291599 vertices, respectively. These examples are
consistent with a possible `p=2r` factor-profile subfamily whose maximizer lies on `y=1/r`, but
the `z` coordinate and value still depend on the divisor profile. This is evidence for a
classification problem, not a claimed composite theorem.

## A candidate subfamily formula (conjectural)

The four exact cases with (p=2r) and (q=4r+3), for (r=5,7,11,13), share the same active
line pattern. Their maximizer is

\[
 (z,y)=\left(\frac{2q+3}{5q},\frac1r\right),
\]

and the exact values fit

\[
 \frac{N}{I}
 =
 \frac{5qr(8q+13)}{28q^2r+15q^2+6qr^2+52qr+9r^2}.
\]

This identity is obtained by evaluating the displayed active lines, not by a general proof. In
particular, it is only a candidate (p=2r, q=4r+3) subfamily: the cases (p=6,q=13) and
other divisor profiles do not follow it. A useful next proof target is to characterize exactly
which factor conditions make these active lines dominate, then prove the corresponding local
arrangement cell is globally maximal.

`work/prove_2r_subfamily_chain_forms.py` gives the exact chain algebra: after (q=4r+3), all
four chain forms equal

\[
N_0=\frac{32r+37}{4r(4r+3)}=\frac{8q+13}{4rq}
\]

at (z_0=(8r+9)/(5(4r+3))=(2q+3)/(5q), y_0=1/r). The six pairwise chain differences are
also recorded symbolically. Thus the candidate numerator and witness equality are now algebraically
closed; only the global (U/I) upper bound remains.

The same script verifies the coordinatewise divisibility ratios for all four chains, so
`compatible four-chain certificate=True` and (N\le U) are valid for the whole fixed divisor
profile.

## Exact completion for p=18, q=37

The long-running exact arrangement on the retreat CPU completed:

```text
p=18, q=37: max=13905/10826 = 1.2844079068908183
             at (z,y)=(1,77/1665)
```

The run has 108/54/18 candidate grids, 38/25/11 active independent lines, 52 active nested
lines, and 2071814 arrangement vertices. The prime-family expression is only `120/101`.
Unlike the four `p=2r, q=4r+3` cases above, this `r=9` divisor profile returns to the boundary
`z=1` and has `y != 1/r`. This is a useful negative control against overgeneralizing the
candidate subfamily.

The common four-chain pattern in the four positive cases is (writing the innermost grid first)

```text
(r,2q,2) -> (r,2q,1) -> (r,2,1)
(2r,q,2) -> (r,q,2)   -> (r,1,2)
(2r,q,2) -> (2r,q,1)  -> (2r,1,1)
(2r,2q,1) -> (r,2q,1) -> (r,2,1)
```

The independent minimizers at the candidate point use the grids `(q,r,4)`, `(q,r,2)`, and
`(r,2,1)`. These identities explain why the pattern is plausible when the odd factor is prime
and why the (p=18=2\cdot3^2) negative control has a different envelope. They are still a
conjectural dominance certificate until all competing divisor grids are symbolically excluded.

The new `work/check_2r_prime_subfamily.py` checks the proposed point and all lower-envelope lines
exactly for (r=5,7,11,13,17) (with (q=4r+3)). It reports the same independent/nested
candidate pattern and the closed-form ratio in all five cases, including the new local case

```text
r=17, q=71: point=(29/71,1/17), ratio=701267/532722
```

This remains a local-envelope certificate; the full global arrangement for (r=17) is running
separately on retreat and is recorded below.

## Global exact confirmation for p=34, q=71

The retreat run completed the full arrangement for (p=34=2\cdot17, q=71=4\cdot17+3):

```text
p=34, q=71: max=701267/532722 = 1.3163845307683932
             at (z,y)=(29/71,1/17)
```

There are 54/27/9 candidate grids, 24/16/8 active independent lines, 31 active nested lines,
and 296028 arrangement vertices. This exactly matches the candidate subfamily formula; the
prime-family expression is only `21964/18301`. The subfamily now has five global exact cases,
but this remains evidence rather than a general theorem.

## Symbolic independent-envelope reduction for the candidate subfamily

`work/prove_2r_subfamily_independent_cover.py` enumerates the fixed divisor profile for
\(p=2r, q=4r+3\), recovers the 24/16/8 active lines, and proves every omitted line is dominated
on the triangle by an active line after substituting \(q=4r+3\). Positivity is certified as a
polynomial in \(r-5\), so the result holds for all real \(r\ge5\) with this divisor profile:

```text
level 4rq: grids=54, active=24, omitted=30
level 2rq: grids=27, active=16, omitted=11
level 2r : grids=9,  active=8,  omitted=1
symbolic independent-cover certificate=True for r>=5, q=4r+3
```

This closes the independent-envelope part of the proposed subfamily. The remaining proof task is
the nested eight-chain upper bound and its two-dimensional ratio monotonicity.

For reference, the four chain sums have the following affine forms in ((z,y)):

\[
\begin{aligned}
C_1&=\left(\frac1{rq}+\frac1{2r}\right)+\frac{5}{2r}z
       +\left(\frac{3}{4q}+\frac12\right)y,\\
C_2&=\left(\frac1r+\frac{3}{2rq}\right)+\frac{5}{4r}z
       +\left(\frac1q+\frac12\right)y,\\
C_3&=\left(\frac1{rq}+\frac1{2r}\right)+\frac{5}{4r}z
       +\left(1+\frac{3}{2q}\right)y,\\
C_4&=\left(\frac1{2r}+\frac{3}{4rq}\right)+\frac{5}{2r}z
       +\left(\frac1q+\frac12\right)y.
\end{aligned}
\]

The nested cost satisfies (N\le U:=\min(C_1,C_2,C_3,C_4)), with equality at the proposed
maximizer. A complete subfamily proof now reduces to showing (U/I) is bounded by the candidate
value over the finite arrangement formed by these four lines and the 24/16/8 independent lines.

For the composite profile, the four extra chain sums used in (U_8) are

\[
\begin{aligned}
C_5&=\left(\frac{3}{4rq}+\frac1{2r}\right)+\left(\frac{3}{4rq}+\frac1{2r}\right)z+3y,\\
C_6&=\left(\frac1{rq}+\frac1{2r}\right)+\left(\frac{3}{4rq}+\frac1{2r}\right)z+\frac52y,\\
C_7&=\left(\frac{3}{2rq}+\frac1r\right)+\left(\frac1{rq}+\frac1{2r}\right)z+\frac54y,\\
C_8&=\left(\frac1{rq}+\frac1{2r}\right)+\left(\frac{3}{2rq}+\frac1r\right)z+\frac54y.
\end{aligned}
\]

The eight-chain certificate uses (U_8=\min(C_1,\ldots,C_8)), not just the first four.

## Global exact confirmation for p=38, q=79

The retreat run added a sixth global case:

```text
p=38, q=79: max=4840725/3666242 = 1.3203506478841276
             at (z,y)=(161/395,1/19)
```

The run has 54/27/9 candidate grids, 24/16/8 active independent lines, 31 active nested lines,
and 296851 arrangement vertices. The result exactly matches the candidate subfamily formula;
the prime-family expression is only `27284/22733`.

## Eight-chain upper-envelope certificate

The original four-chain upper bound is too loose away from the witness for this composite profile.
Adding four compatible chains gives (U_8), with

\[
N\le U_8:=\min_{1\le i\le8} C_i.
\]

`work/check_2r_subfamily_eight_chain_bound.py` enumerates the arrangement of the 10/5/2 sorted
independent lines and these eight chains exactly. It obtains the candidate ratio and point for all
six tested cases (r=5,7,11,13,17,19), with output

```text
eight-chain exact upper-bound certificate=True
```

This reduces the remaining symbolic problem to the 25-line arrangement for the fixed prime divisor
profile.

The reduction from 54/27/9 ordered grids to 10/5/2 sorted factor triples is justified by
`work/prove_sorted_factor_rearrangement.py`: for (1\ge z\ge y\ge0), assigning the largest factor
to the (y)-coefficient, the middle factor to (z), and the smallest to the constant term is
coefficientwise optimal. All six permutations are checked symbolically.

`work/prove_2r_subfamily_eight_chain_cells.py` makes the cell structure explicit. The ratio
certificate has 36, 35, 34, 34, 34 full-dimensional proving cells for
(r=5,7,11,17,19), respectively; every cell has a chain owner whose affine inequality proves the
candidate bound at all of its exact vertices. The changing cell count records the remaining
parameter thresholds instead of silently assuming one arrangement topology.

`work/probe_2r_subfamily_symbolic_cells.py` now lifts the 33-cell branch at \(r=21\) to rational
functions of \(r\). It checks 121 cell vertices, proves feasibility and ratio signs by coefficientwise
positivity after \(r=21+a\), and samples the topology at \(r=21,23,50,100\):

```text
r0=21 cells=33 vertices_checked=121 bad=0
sampled stable topology=[(21,33),(23,33),(50,33),(100,33)]
symbolic r>=21 cell certificate=True for the 33-cell branch
```

The remaining finite branches are \(r=5,7,11,13,17,19\), plus the small topology transitions; the
large-r branch is symbolically certified modulo proving that no unseen cell appears after the
sampled topology checks.

## Topology stability audit and larger exact sweep

The fixed-profile cell enumerator was extended with
`work/check_2r_subfamily_topology_stability.py`. It compares cells by their three independent
owner indices and chain owner, so the comparison does not depend on the rational coordinates of a
particular vertex. At (r=21,23,50,100), `run_profile(..., proving_only=False)` finds exactly 33
full-dimensional feasible cells, with identical signatures:

```text
samples=[(21,33,True),(23,33,True),(50,33,True),(100,33,True)]
```

This is stronger than checking only the 33 cells that already pass the ratio inequality: it counts
all feasible owner/chain cells at each sampled parameter. It is still a finite topology audit, not
the missing symbolic proof that no new cell can appear for every real (r\ge21).

The exact (U_8/I) arrangement was also run on the retreat CPU for fourteen additional prime
pairs with (q=4r+3), namely
((31,127),(37,151),(41,167),(47,191),(59,239),(67,271),(89,359),
(107,431),(109,439),(149,599),(151,607),(157,631),(179,719),(181,727)).
Every run returned the predicted point
(z=(2q+3)/(5q),y=1/r) and the closed-form ratio, extending the exact finite global sample
count from six to twenty cases. These runs test the fixed divisor profile and do not replace a
parameterized no-new-cell argument.

As an additional stress test, the retreat CPU enumerated all fixed-profile cells for every integer
21 <= r <= 40 (with q=4r+3); every parameter had 33 cells and the owner/chain signature matched
the r=21 signature (`BAD []`). This widens the empirical stability interval but leaves the same
real-parameter no-new-cell gap.

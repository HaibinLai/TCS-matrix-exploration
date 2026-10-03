# Odd-p endpoint formulas: lemma, threshold certificate, and minimal failure

日期：2026-10-03

## Setup

At the witness aspect point

\[
(z,y)=(1,1/p),
\]

the per-grid proxy is

\[
h_p(a,b,c)=\frac1{ab}+\frac1{ac}+\frac1{pbc},
\qquad abc=P.
\]

For the three processor levels

\[
P_1=2pq,\qquad P_2=pq,\qquad P_3=p,
\]

where (p) is odd and (q>p) is prime, every factorization at (P_1) or (P_2) contains (q) in exactly one coordinate. Therefore each grid cost is affine in (u=1/q).

## Exact affine decomposition

Let (P_k=kpq) with (k\in\{1,2\}).

If the (q)-factor is in (a), write (a=qr), (rbc=kp). Then

\[
h_p(qr,b,c)=\frac{r}{kp^2}
 +\frac{b+c}{kp}\,u.
\tag{1}
\]

If (q) is in (b), write (b=qr), (arc=kp). Then

\[
h_p(a,qr,c)=\frac{r}{kp}
 +\left(\frac1{ar}+\frac1{prc}\right)u,
\tag{2}
\]

and the (q)-in-(c) case is symmetric.

Thus all independent grid lines and all compatible-chain lines have the form (A+Bu). This is the key finite-comparison lemma: once one candidate has the smallest (A), and among tied (A) the smallest (B), it is optimal for all sufficiently small (u) (equivalently, all sufficiently large (q)).

## Independent target formulas

For (P_3=p),

\[
h_p(a,b,c)=\frac{b+c+a/p}{p}\ge\frac3p,
\]

because (b+c\ge2) and (a/p>0), with equality at ((a,b,c)=(p,1,1)). Hence

\[
I_3=\frac3p.
\]

For (P_k=kpq), the asymptotic minimum in (1) is obtained with (r=1). The remaining factors satisfy (bc=kp), and

\[
\min_{bc=kp}\frac{b+c}{kp}
 =\min_{d\mid kp}\left(\frac1d+\frac1{kp/d}\right)
 =:\sigma(kp).
\]

Therefore the target line is

\[
I_k(u)=\frac1{kp^2}+\sigma(kp)u,
\qquad k=1,2.
\tag{3}
\]

Summing (3) and (I_3) gives

\[
I_p(q)=\frac3p+\frac3{2p^2}
      +\frac{\sigma(p)+\sigma(2p)}q.
\tag{4}
\]

Equation (4) is an eventual formula: it is exact once (q\) is above the finite crossing threshold defined below. It is not valid for every (q>p).

## Nested target and a provable asymptotic lower bound

Use the compatible chain

\[
(p,2,q),\qquad (p,1,q),\qquad (p,1,1),
\]

with the levels ordered (2pq,pq,p). Its cost is

\[
N_p(q)=\frac9{2p}+\frac7{2pq}.
\tag{5}
\]

The constant term in (5) can be shown to be optimal among all compatible chains:

1. The (p)-level cost is at least (3/p), with equality only at ((p,1,1)).
2. Compatibility with this bottom grid forces the first coordinate of the (pq)-grid to be divisible by (p). In (1), this means (r\ge p) if (q) is in (a), giving constant at least (1/p); if (q) is in (b) or (c), (2) already gives constant (r/(p)\ge1/p).
3. The same argument for (2pq) gives constant at least (1/(2p)).

Consequently every compatible chain has constant term at least

\[
\frac3p+\frac1p+\frac1{2p}=\frac9{2p},
\]

and the displayed chain attains it. Among chains with this constant, direct use of (1)--(2) gives a coefficient at least (7/(2p)), also attained by the displayed chain. This proves (5) after the finite-(q) crossing threshold.

## Explicit finite threshold

For a finite set of affine lines (L_g(u)=A_g+B_g u), define the crossing threshold of a target line (L_*(u)) by

\[
Q(L_*)=
\max_{g:\,A_g>A_*}
\frac{B_*-B_g}{A_g-A_*},
\]

with negative numerators clipped to zero. Ties with (A_g=A_*) are settled by (B_*\le B_g). Applying this to the three independent grid sets and to all compatible chains gives an exact finite certificate

\[
Q^*(p)=\max\{p+1,Q_{2pq}(p),Q_{pq}(p),Q_{\rm nested}(p)\}.
\]

For every prime (q\ge Q^*(p)), equations (4) and (5) hold exactly. The script

```text
python work/derive_odd_p_threshold.py --p-max 99 --q0 997
```

performs these comparisons with exact rational arithmetic. It checked 49 odd (p\le99); the largest integer threshold was (Q^*=891), attained at (p=99). Representative thresholds are:

```text
p=3   Q*=4
p=9   Q*=27
p=15  Q*=45
p=25  Q*=125
p=27  Q*=81
p=45  Q*=225
p=81  Q*=729
p=99  Q*=891
```

The threshold certificate proves the endpoint formulas, but it does not prove that ((z,y)=(1,1/p)) is the global maximizer over the full two-dimensional aspect domain.

## Minimal failure of the unrestricted claim

The smallest tested failure of “(4) holds for every prime (q>p)” is

\[
(p,q)=(9,11).
\]

At this point:

- (2pq=198) independent optimum: ((22,3,3)), cost (38/891);
- (pq=99) independent optimum: ((11,3,3)), cost (65/891);
- (p=9) optimum: ((9,1,1)), cost (1/3).

Thus the actual independent sum is

\[
I_{\rm actual}=\frac{400}{891}.
\]

The divisor target in (3) would use the (2pq) grid ((11,3,6)), giving (46/891), so it is beaten by ((22,3,3)) at this small (q). The nested optimum remains

\[
((9,2,11),(9,1,11),(9,1,1)),
\qquad N=\frac{53}{99}.
\]

Hence

\[
R_{\rm actual}=\frac{477}{400},
\]

whereas substituting (4)--(5) would incorrectly give (159/136). A second failure occurs at the middle level for ((p,q)=(27,29)), so even the middle target need not be optimal immediately above (p).

## Consequence for the research direction

The useful theorem-sized statement is therefore:

> For every odd (p), the endpoint independent and nested costs are affine in (1/q). The divisor formulas (4)--(5) hold for all prime (q\ge Q^*(p)), where (Q^*(p)) is an explicitly computable finite crossing threshold. The unrestricted claim for every prime (q>p) is false; the minimal failure is ((p,q)=(9,11)).

The remaining hard step is to bound (Q^*(p)) in closed form and then prove the same candidate endpoint is globally optimal in the full ((z,y))-triangle.

For the previously studied (p=99) case, the certificate gives

\[
I_{99}(q)=\frac{199}{6534}+\frac{23}{66q},
\qquad
N_{99}(q)=\frac1{22}+\frac7{198q},
\]

valid for every prime (q\ge891); in particular it applies to (q=997).

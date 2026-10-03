# Global-max exploration for the prime hierarchy family

**Scope.** This report checks the proposed three-level family
\[
P^*=(2pq,pq,p),\qquad 0\le y\le z\le 1,
\]
with independent lower envelope \(I(z,y)\), legal nested-chain envelope \(N(z,y)\), and candidate maximum at \((z,y)=(1,1/p)\). It is an agent report only; it does not modify the main research log.

## Exact global checks

The existing exact arrangement checker (`work/check_prime_p_global.py`) was run with rational arithmetic. For every case below the observed global maximum equals
\[
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
\]
and the maximizer is exactly `(z,y)=(1,1/p)`.

### p=3

Exact cases checked for all primes
\[
q=5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97.
\]
The checker reported `active=(16,8,3)/16` and 3970--4502 exact candidate vertices depending on q. Representative ratios include
\[
R_3(5)=13/12,\qquad R_3(29)=67/54,\qquad R_3(97)=220/173.
\]

### p=5

Exact cases checked for
\[
q=7,11,13,17,19,23,29,31,37,41,43,47,53.
\]
Again every case has maximizer `(1,1/5)` and active envelope counts `(16,8,3)/16`. Representative ratios are
\[
R_5(7)=175/163,\qquad R_5(29)=335/263,\qquad R_5(53)=605/461.
\]

These are finite exact certificates, not a universal theorem.

## Fixed-topology checks at q=29

`work/check_prime_active_chain_templates.py` gives, with exact rational inequalities:

```
p=3, q=29: active nested chains=16, template_match=True
p=5, q=29: active nested chains=16, template_match=True
```

The 16 chains are the symbolic template in `work/check_prime_active_chain_templates.py`. The independent active-line counts are 5, 2, and 1; the product of these envelopes has 10 nonempty cells. The reduced exact `3/2` certificate (`work/check_prime_three_halves_reduced.py`) reports, for both p=3 and p=5 at q=29, `cells=10`, `nested_regions=84`, `certificate=True`. This proves only the coarse bound \(N/I\le3/2\), not that the sharper candidate \(R_p(q)\) is globally maximal.

## Boundary formula

The exact boundary script (`work/check_prime_p_boundary_theorem.py`) verifies for selected prime pairs that, on \(z=1\) with \(t=y/z\),
\[
I_p(t)=\min\left\{\frac1{pq}+t,\frac3{2pq}+\frac t2,\frac{p+2}{2pq}+\frac t{2p}\right\}
+\min\left\{\frac2{pq}+t,\frac{p+1}{pq}+\frac tp\right\}
+\frac2p+t,
\]
and the endpoint \(t=1/p\) gives \(R_p(q)\). This is an exact witness/boundary result; it does not control interior \(z<1\).

## Attempted parameterized proof and explicit gap

For p=3, the independent envelope has a stable-looking 5/2/1 active-line pattern for q>=7 (q=5 has an exceptional geometric vertex, but is already covered by the exact global check). The normalized active cells are 10 and their vertices involve only
\[
(0,0),\ (1/3,1/3),\ (1,1),\ (1/3,1/q),\ (1,1/q),\ (1,1/(3q)),\ (1,0).
\]
At q=29 the nested active set is the same 16-chain template. I attempted to use one affine nested-chain line to certify
\[
N(z,y)\le R_3(q)I(z,y)
\]
cell by cell. Several cells admit a single-chain certificate; two cells (the regions containing the \((1/3,1/3)\) and \((0,0)\) transitions) require subdividing by nested-envelope equalities. Thus an independent-envelope-only certificate is insufficient. The missing step is a symbolic overlay proof that these nested subdivisions have no topology changes for all q>=29 and that every resulting vertex satisfies the sharp ratio inequality.

A successful parameterized proof would therefore need:

1. a q>=29 event-sweep/Sturm certificate for the 16 nested lines and the 10 independent cells;
2. exact sign checks for \(N-R_3(q)I\) on every resulting symbolic overlay vertex;
3. a separate exact check for the exceptional q=5 topology.

No universal p=3 proof has been claimed here. The numerical/exact evidence strongly supports the conjecture, but the gap is specifically the interior overlay topology and sharp-ratio sign certificate.

## Reproducibility

Commands used:

```bash
python work/check_prime_p_global.py --p 3 --q 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 61 67 71 73 79 83 89 97
python work/check_prime_p_global.py --p 5 --q 7 11 13 17 19 23 29 31 37 41 43 47 53
python work/check_prime_active_chain_templates.py --p 3 --q 29
python work/check_prime_active_chain_templates.py --p 5 --q 29
python work/check_prime_three_halves_reduced.py --p 3 --q 29
python work/check_prime_three_halves_reduced.py --p 5 --q 29
```

## Superseding update

The earlier “explicit gap” section is superseded for the regime \(q>2p\). The four-chain upper
bound plus the reduced independent envelopes now yields a parameterized full two-dimensional proof;
see `work/agent_reports/prime_family_full_theorem.md` and
`work/prove_prime_full_2d_upper_bound.py`. The exceptional near-threshold cases \(p<q\le2p\),
including p=3,q=5, remain covered only by exact finite checks.

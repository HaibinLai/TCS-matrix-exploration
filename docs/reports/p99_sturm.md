# p=99 quadratic topology events: exact Sturm check

## Scope

This report upgrades the quadratic part of the topology-event diagnostic. It
checks triple-concurrence determinant polynomials for the fixed p=99 active
line sets (56, 24, 10, 51 lines for the three independent envelopes and the
nested envelope). Pair/domain-boundary event polynomials are already linear in
u and are handled by the existing Fraction scan.

The interval is (0<u\le u_0=1/997), where (u=1/q).

## Exact certificate

Run:

```text
PYTHONPATH=work python work/check_p99_quadratic_sturm.py
```

Output:

```text
active_counts (56, 24, 10, 51)
quadratic_unique 1405 source_triples 11219
sturm_roots_open_interval 0 count_hist {0: 1405} endpoint_polys 146
...
certificate=True: no quadratic triple-concurrence roots in (0,1/997]; endpoint-only polynomials are handled by the separate degenerate endpoint analysis
```

The script constructs all coefficients with exact `Fraction` arithmetic,
converts each normalized quadratic determinant to a SymPy rational `Poly`,
and calls its Sturm root counter on the closed interval. Roots at the two
endpoints are removed explicitly. Every one of the 1405 quadratic polynomials
has zero roots in the open interval; the 146 endpoint-only polynomials vanish
only at (u=0), and no polynomial vanishes at (u_0). These endpoint degeneracies
are handled by the separate exact overlay at (u=0), rather than interpreted as
interior topology events.

Thus there is no quadratic triple-concurrence event for any (0<u\le1/997).
The (u=0) degeneracy is consistent with the separate endpoint treatment
already required by the lower-envelope scan (the number of visible edges
changes at exactly (u=0)).

## Ratio-level endpoint check

The wrapper `work/check_p99_ratio_all_u.py` combines the existing exact
candidate-family sign check with an exact overlay at (u=0):

```text
PYTHONPATH=work python work/check_p99_ratio_all_u.py
```

The relevant output is:

```text
positive_u_candidates 994
positive_u_exact_sign_failures 0
u0_edge_counts (4, 4, 12, 28)
u0_overlay_points 12 segments 48
u0_best_ratio 297/199 at (1, 1/99, 199/6534, 1/22)
certificate=True: candidate branches for 0<u<=1/997 and exact u=0 slice
```

For (0<u\le1/997), the imported checker has 994 q0-visible symbolic
candidate branches and exact Sturm sign checks for

\[
R_*(u)I(u)-N(u)\ge0,
\qquad R_*(u)=\frac{297+231u}{199+2277u},
\]

with zero failures. The topology-event work shows that the only possible
quadratic events are absent in the open interval; the remaining linear-event
scan has no active event after exact Fraction owner-gap checks. Under that
fixed positive-u topology, these 994 branches cover every overlay vertex.

At (u=0), the topology is genuinely degenerate, so it is checked directly:
the exact overlay has 12 points and 48 active segments, and its maximum is

\[
\frac{297}{199}
\quad\text{at}\quad(z,y)=\left(1,\frac1{99}\right).
\]

The remaining formal boundary is presentation-level integration: the implication
“no active event implies the 994 q0-visible branches cover all (u>0)” should be
written as an explicit combinatorial-continuity lemma. No numerical root check
is needed for the quadratic events anymore.

## Linear-event certificate (now split out)

That remaining checker is now available as
`work/check_p99_linear_events.py`:

```text
PYTHONPATH=work python work/check_p99_linear_events.py
```

It checks, with exact `Fraction` roots and owner comparisons:

* pair equalities crossing the three domain vertices;
* pair/domain parallelism (0 positive roots in the corrected affine cover);
* positive-(u) pair identity;
* linear triple-concurrence events.

The output is:

```text
active_counts (56, 24, 10, 51)
active_vertex_events 0 []
parallel_roots 0 active_pair_parallel_roots 0
positive_u_identity_roots 0 []
active_linear_triple_events 0 []
certificate=True: no active linear topology event for 0<u<=1/997
```

Together with the quadratic Sturm result, this gives a complete exact
exclusion of active topology events on (0<u\le1/997). The only remaining
combinatorial change is the already isolated duplicate-line degeneration at
(u=0), which is handled by the direct endpoint overlay above.

## What this proves and what remains

This is an exact exclusion of all quadratic roots in the open positive-u
interval. Combined with the standalone exact linear-event scan, it removes the
main possible source of active-edge topology changes for (q\ge997). The only
remaining work is to state the combinatorial-continuity implication in the
theorem proof and combine it with the already passing ratio wrapper and the
separate u=0 overlay argument.

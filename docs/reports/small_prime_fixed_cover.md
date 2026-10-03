# Small-prime fixed-cover extension

After correcting the symbolic replacement for a factor containing the anchor prime
($1/(dq)$ must become $u/d$, never an integer floor), the same exact pipeline was run for
$p=3,5,7$ with anchor $q_0=67$.

## Envelope-cover certificate

For each $p$, `prove_p99_envelope_stability.py --p p --q0 67` reports

```text
independent[0] total=27 active=16 uncovered=0
independent[1] total=9 active=8 uncovered=0
independent[2] total=3 active=3 uncovered=0
nested total=27 active=16 uncovered=0
```

This checks all grids and all coordinatewise-compatible nested chains at the symbolic
envelope-cover level for prime $q\ge67$.

## Topology and ratio certificates

For $p=3,5,7$, with `PRIME_P=p Q0=67`, the corrected quadratic Sturm and linear event scans
report no active event on $0<u\le1/67$. The ratio candidate checks report respectively

```text
p=3: 54 stable candidate branches, 0 exact sign failures
p=5: 37 stable candidate branches, 0 exact sign failures
p=7: 31 stable candidate branches, 0 exact sign failures
```

The candidate boundary ratio is

\[
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},
\]

at $(z,y)=(1,1/p)$.

Independent direct exact-global checks also found the predicted maximizer for 43 prime values
$7\le q\le199$ when $p=5$, and 42 prime values $11\le q\le199$ when $p=7$. For $p=3$,
all 60 primes below 300 were checked with the exact overlay routine.

## Status and limitation

This is a reproducible computational certificate for three small-prime families, not yet a
published theorem: the remaining formal step is to state the finite-arrangement continuity lemma
and connect the symbolic cover to every prime-$q$ grid template in prose. It also does not prove
the result for arbitrary $p$; the corrected scan already shows that $p=23,29,31,\ldots$ may need
larger anchors than 67 because their quadratic determinant families can have roots in the initial
interval.

Scripts:

- `work/prove_p99_envelope_stability.py`
- `work/prove_p3_envelope_stability.py`
- `work/check_p99_quadratic_sturm.py`
- `work/check_p99_linear_events.py`
- `work/p3probe/check_p3_ratio_candidate_family.py`
- `work/check_prime_p_global.py`

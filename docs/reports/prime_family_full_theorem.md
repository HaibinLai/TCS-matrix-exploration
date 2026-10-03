# Prime-family three-level sharp theorem

## Statement

Let \(p,q\) be distinct primes with \(p\ge3\) and \(q>2p\). Consider the three-level
processor hierarchy
\[
(P_1^*,P_2^*,P_3^*)=(2pq,pq,p),
\]
with independent lower envelope \(I(z,y)\), nested-chain lower envelope \(N(z,y)\), and
\(0\le y\le z\le1\). Then
\[
\boxed{
\max_{0\le y\le z\le1}\frac{N(z,y)}{I(z,y)}
=R_p(q)
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
}
\]
and the maximum is attained at \((z,y)=(1,1/p)\).

This is a theorem for the restricted divisibility/communication model above. It is not a theorem
for arbitrary multilevel GEMM schedules or arbitrary processor hierarchies.

## Reduction to two normalized variables

Write
\[
(z,y)=(s,st),\qquad 0\le s,t\le1.
\]
For a grid \(g=(a,b,c)\) at product \(P\),
\[
H_g(1,s,st)=\frac{c+s(b+at)}{P}.
\]
Define the scaled level expressions
\[
\begin{aligned}
A&=1+s+2pqst,&B&=1+2s+pqst,\\
C&=1+ps+2qst,&D&=2+ps+qst,\\
E&=1+2ps+qst,\\
F&=1+s+pqst,&G&=1+ps+qst,\\
H&=1+s+pst.
\end{aligned}
\]
The independent cost is
\[
I(s,t)=\frac{m_0(s,t)+2m_1(s,t)+2qH(s,t)}{2pq},
\]
where
\[
m_0=\min(A,B,C,D,E),\qquad m_1=\min(F,G).
\]
The symbolic independent-cover proof is in
`work/prove_prime_independent_cover.py` and the reduction to these five/two/one lines is in
`work/prove_prime_reduced_envelopes.py`.

The comparisons
\[
\begin{aligned}
A-B&=s(pq t-1),&B-C&=s(p-2)(qt-1),\\
C-D&=qst-1,&C-E&=s(qt-p),\\
D-E&=1-ps,&F-G&=s(p-1)(qt-1)
\end{aligned}
\]
therefore give
\[
m_0=
\begin{cases}
A,&t\le1/(pq),\\
B,&1/(pq)\le t\le1/q,\\
\min(C,D,E),&t\ge1/q,
\end{cases}
\qquad
m_1=
\begin{cases}
F,&t\le1/q,\\
G,&t\ge1/q.
\end{cases}
\]
For the first two cases, the omitted comparisons follow from \(p\ge3\), \(q>2p\), and
\(0\le s,t\le1\); for \(t\ge1/q\), \(A,B\) are dominated by \(C\).

## Four-chain upper envelope

Use the following four legal nested chains:
\[
\begin{aligned}
\mathcal A&=((2pq,1,1),(pq,1,1),(p,1,1)),\\
\mathcal B&=((pq,2,1),(pq,1,1),(p,1,1)),\\
\mathcal C&=((2p,q,1),(p,q,1),(p,1,1)),\\
\mathcal D&=((p,q,2),(p,q,1),(p,1,1)).
\end{aligned}
\]
Let \(U\) be the minimum of their costs. Since every chain is legal,
\[
N\le U.
\]
Set
\[
K=1+qs+2pst,\qquad L=2+qs+pst,\qquad J=1+qs+pst.
\]
Then
\[
U(s,t)=\frac{2qH+\min(A+2F,\ B+2F,\ K+2J,\ L+2J)}{2pq}.
\]
The relevant comparison identities are
\[
\begin{aligned}
(A+2F)-(K+2J)&=s(q-1)(4pt-3),\\
(B+2F)-(K+2J)&=s(3q-4)(pt-1),\\
(B+2F)-(L+2J)&=-1+s(3pqt-3pt-3q+4),\\
(K+2J)-(L+2J)&=pst-1.
\end{aligned}
\]
They imply the exact chain envelope
\[
U=
\begin{cases}
(A+2F+2qH)/(2pq),&t\le1/(pq),\\
(B+2F+2qH)/(2pq),&1/(pq)\le t\le1/p,\\
\bigl(2qH+\min(K+2J,L+2J)\bigr)/(2pq),&t\ge1/p.
\end{cases}
\]
For example, on \(t\le1/q\), \(A,B\) dominate both \(K,L\); on
\(1/q\le t\le1/p\), \(B\) dominates both; on \(t\ge1/p\), \(A,B\) are no smaller than
\(K\), leaving the \(K/L\) comparison.

## Radial monotonicity

On every region where the displayed minima are fixed, the sign of
\(\partial_s(U/I)\) is the sign of an affine polynomial in \(t\). The nontrivial cases are:

| region | derivative numerator |
|---|---|
| \(U=\mathcal B, m_0=C\) | \((3p-4)(2q+3)(qt-1)\) |
| \(U=\mathcal B, m_0=D\) | \(D_{BD}(t)\) |
| \(U=\mathcal B, m_0=E\) | \((p-1)(2q+3)(3qt-4)\) |
| \(U=\mathcal C, m_0=C\) | \((p-q)(2q+3)(4t-3)\) |
| \(U=\mathcal C, m_0=D\) | \(D_{CD}(t)\) |
| \(U=\mathcal C, m_0=E\) | \((4p-3q)(2q+3)(t-1)\) |
| \(U=\mathcal D, m_0=D\) | \(6(p-q)(q+2)(t-1)\) |

Here
\[
\begin{aligned}
D_{BD}(t)&=6pq^2t+14pqt-6pq-9p-6q^2t-9qt+10q+16,\\
D_{CD}(t)&=10pqt-6pq+16pt-9p-6q^2t+6q^2-9qt+14q.
\end{aligned}
\]
The first, third, fourth, sixth and seventh rows are immediately nonnegative on their feasible
regions: respectively \(qt\ge1\), \(qt\ge p\), \(t\le p/q<1/2\), \(q>2p\), and
\(t\le1\).

The two affine polynomials are checked at their interval endpoints:
\[
D_{BD}(1/q)=5p+4q+7>0,
\qquad
D_{BD}(1/p)=-\frac{\Psi(p,q)}p,
\]
\[
D_{CD}(1/p)=-\frac{\Psi(p,q)}p,
\qquad
D_{CD}(1)=4pq+7p+5q>0,
\]
where
\[
\Psi=6p^2q+9p^2-6pq^2-24pq-16p+6q^2+9q.
\]
Writing \(q=2p+r\) with \(r>0\),
\[
-\Psi=12p^3-2p+15p^2+9r(2p^2-1)+6(p-1)r^2>0
\]
for \(p\ge3\). Hence
\[
\partial_s(U/I)\ge0
\qquad(0\le s,t\le1).
\]
The exact symbolic identities are verified by
`work/prove_prime_full_2d_upper_bound.py`.

## Boundary and equality

The already established boundary calculation at \(s=1\) gives
\[
\max_{0\le t\le1}\frac{N(1,t)}{I(1,t)}
=R_p(q)
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},
\]
with the maximum at \(t=1/p\). The same four-chain upper bound is valid on the boundary, so
\(U(1,t)/I(1,t)\le R_p(q)\). Since \(U/I\) is nondecreasing in \(s\),
\[
\frac{N(s,st)}{I(s,st)}\le\frac{U(s,t)}{I(s,t)}
\le\frac{U(1,t)}{I(1,t)}\le R_p(q).
\]
At \((s,t)=(1,1/p)\), the boundary endpoint certificate shows that one of the four chains is an
actual nested minimizer, so \(U=N\) there and equality holds.

This closes the restricted three-level theorem. The broader research problem—arbitrary multilevel
hierarchies, replication/recomputation, asymmetric costs, and per-level communication vectors—remains
open and is separate from this prime-family certificate.

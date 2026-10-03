#!/usr/bin/env python3
"""Symbolic derivative certificate for the eight q>2p radial cell templates.

The active-cell classification is a separate statement.  Given that template,
this script derives the affine-in-t radial derivative numerators and verifies
the endpoint signs used in the proof.
"""
import sympy as sp
p, q, t, r = sp.symbols('p q t r', positive=True)

def line(g):
    a,b,c = g
    return [sp.Rational(1,1)/(a*b), sp.Rational(1,1)/(a*c), sp.Rational(1,1)/(b*c)]
def total(gs):
    return [sp.factor(sum(line(g)[i] for g in gs)) for i in range(3)]
def D(n, indep):
    I=total(indep); N=total(n)
    return sp.factor((N[1]+N[2]*t)*I[0] - N[0]*(I[1]+I[2]*t))

def G(*x):
    names={1:sp.Integer(1),2:sp.Integer(2),'p':p,'q':q,'2p':2*p,'2q':2*q,'pq':p*q,'2pq':2*p*q}
    return tuple(names[v] for v in x)

# Keep the full templates explicit to make the certificate auditable.
templates=[
 ((G('p','q',2),G('p','q',1),G('p',1,1)), [G('q','p',2),G('q','p',1),G('p',1,1)]),
 ((G('2pq',1,1),G('pq',1,1),G('p',1,1)), [G('2pq',1,1),G('pq',1,1),G('p',1,1)]),
 ((G('pq',2,1),G('pq',1,1),G('p',1,1)), [G('q','p',2),G('q','p',1),G('p',1,1)]),
 ((G('pq',2,1),G('pq',1,1),G('p',1,1)), [G('pq',2,1),G('pq',1,1),G('p',1,1)]),
 ((G('pq',2,1),G('pq',1,1),G('p',1,1)), [G('2q','p',1),G('q','p',1),G('p',1,1)]),
 ((G('2p','q',1),G('p','q',1),G('p',1,1)), [G('q','p',2),G('q','p',1),G('p',1,1)]),
 ((G('2p','q',1),G('p','q',1),G('p',1,1)), [G('q','2p',1),G('q','p',1),G('p',1,1)]),
 ((G('2p','q',1),G('p','q',1),G('p',1,1)), [G('2q','p',1),G('q','p',1),G('p',1,1)]),
]
Ds=[D(n,I) for n,I in templates]
for i,d in enumerate(Ds): print(f'D{i} = {d}')
assert Ds[1] == 0 and Ds[3] == 0
assert sp.factor(Ds[0] - 3*(p-q)*(q+2)*(t-1)/(2*p**2*q**2)) == 0
assert sp.factor(Ds[4] - (3*p-4)*(2*q+3)*(q*t-1)/(4*p**2*q**2)) == 0
assert sp.factor(Ds[6] - (4*p-3*q)*(2*q+3)*(t-1)/(4*p**2*q**2)) == 0
assert sp.factor(Ds[7] - (p-q)*(2*q+3)*(4*t-3)/(4*p**2*q**2)) == 0
A=6*p**2*q+9*p**2-6*p*q**2-24*p*q-16*p+6*q**2+9*q
assert sp.factor(Ds[2].subs(t,1/p) + A/(4*p**3*q**2)) == 0
assert sp.factor(Ds[5].subs(t,1/p) + A/(4*p**3*q**2)) == 0
assert sp.factor(Ds[2].subs(t,1/q) - (5*p+4*q+7)/(4*p**2*q**2)) == 0
assert sp.factor(Ds[5].subs(t,1) - (4*p*q+7*p+5*q)/(4*p**2*q**2)) == 0
A_sub=sp.factor(A.subs(q,2*p+r))
print('A(q=2p+r) =', A_sub)
# -A is visibly a sum of positive terms after grouping for p>=3,r>0:
print('-A grouped = 12*p^3-2*p + 15*p^2 + 9*r*(2*p^2-1) + 6*(p-1)*r^2')
assert sp.expand(-A_sub - (12*p**3-2*p+15*p**2+9*r*(2*p**2-1)+6*(p-1)*r**2)) == 0
print('symbolic derivative certificate=True under p>=3, q>2p')

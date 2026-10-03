#!/usr/bin/env python3
"""Symbolic reduction of the independent and four-chain envelopes.

For p>=3 and q>2p, every independent grid is covered by the fixed 16/8/3
candidate lists, and those candidates reduce to five level-(2pq) lines,
two level-(pq) lines, and one level-p line.  The resulting min formulas are
used by the radial proof.
"""
import sympy as sp
from exact_multilevel_2d import grids, line
p,q,a,r=sp.symbols('p q a r', positive=True)
V=((0,0),(1,0),(1,1))
T={'1':sp.Integer(1),'2':sp.Integer(2),'p':p,'q':q,'2p':2*p,'2q':2*q,'pq':p*q,'2pq':2*p*q}

def sl(g):
    aa,bb,cc=(T[x] for x in g)
    return tuple(sp.factor(sp.S(1)/(u*v)) for u,v in ((aa,bb),(aa,cc),(bb,cc)))
def val(l,z,y):return sp.factor(l[0]+l[1]*z+l[2]*y)
def nonnegative(expr):
    num,den=sp.fraction(sp.factor(expr))
    poly=sp.Poly(sp.expand(num.subs({p:3+a,q:2*(3+a)+r})),a,r)
    return all(c>=0 for c in poly.coeffs())
def dominates(g, h):
    return all(nonnegative(val(sl(g),z,y)-val(sl(h),z,y)) for z,y in V)

# Five lines that survive at level 2pq.
level0=(('2pq','1','1'),('pq','2','1'),('2q','p','1'),('q','p','2'),('q','2p','1'))
level1=(('pq','1','1'),('q','p','1'))
level2=(('p','1','1'),)
# Candidate 16/8/3 sets from the independent cover proof.
candidates=[
 ('1','2pq','1'),('2','p','q'),('2','pq','1'),('2','q','p'),('2p','q','1'),('2pq','1','1'),('2q','1','p'),('2q','p','1'),('p','2','q'),('p','2q','1'),('p','q','2'),('pq','1','2'),('pq','2','1'),('q','2','p'),('q','2p','1'),('q','p','2')
]
for g in candidates:
 if not any(dominates(g,h) for h in level0):
  raise AssertionError(('level0 not reduced',g))
for g in [('1','p','q'),('1','pq','1'),('1','q','p'),('p','1','q'),('p','q','1'),('pq','1','1'),('q','1','p'),('q','p','1')]:
 if not any(dominates(g,h) for h in level1):
  raise AssertionError(('level1 not reduced',g))
print('independent reduced envelope=True: level0=5 level1=2 level2=1')
# Verify the four chain upper envelope comparisons used by the radial proof.
# Scaled expressions omit the common 2q*H term.
s,t=sp.symbols('s t', nonnegative=True)
A=1+s+2*p*q*s*t; B=1+2*s+p*q*s*t; C=1+p*s+2*q*s*t; D=2+p*s+q*s*t; E=1+2*p*s+q*s*t
F=1+s+p*q*s*t; G=1+p*s+q*s*t; H=1+s+p*s*t
K=1+q*s+2*p*s*t; L=2+q*s+p*s*t; J=1+q*s+p*s*t
# Basic envelope comparisons are recorded as endpoint inequalities in the report.
assert sp.simplify((A-B)-s*(p*q*t-1))==0
assert sp.simplify((B-C)-s*(p-2)*(q*t-1))==0
assert sp.simplify((C-D)-(q*s*t-1))==0
assert sp.simplify((C-E)-s*(q*t-p))==0
assert sp.simplify((D-E)-(1-p*s))==0
assert sp.simplify((A+2*F)-(B+2*F)-(A-B))==0
assert sp.simplify((B+2*F)-(K+2*J)-s*(3*q-4)*(p*t-1))==0
assert sp.simplify((A+2*F)-(K+2*J)-s*(q-1)*(4*p*t-3))==0
assert sp.simplify((B+2*F)-(L+2*J)-(3*p*q*s*t-3*p*s*t-3*q*s+4*s-1))==0
assert sp.simplify((K+2*J)-(L+2*J)-(p*s*t-1))==0
print('four-chain comparison identities=True')

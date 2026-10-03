#!/usr/bin/env python3
"""Symbolic proof certificate for the full two-dimensional prime-p upper bound.

The independent-cover script reduces I to five/two/one min formulas.  This
script verifies the chain comparisons and all radial derivative identities for
the four-chain upper envelope U>=N.  Under p>=3 and q>2p, the listed min
regions and endpoint signs imply d(U/I)/ds>=0; the boundary theorem then gives
max U/I=R_p(q).  Equality with N is supplied by the boundary witness.
"""
import sympy as sp
p,q,s,t,r=sp.symbols('p q s t r', positive=True)
A=1+s+2*p*q*s*t; B=1+2*s+p*q*s*t; C=1+p*s+2*q*s*t; D=2+p*s+q*s*t; E=1+2*p*s+q*s*t
F=1+s+p*q*s*t; G=1+p*s+q*s*t; H=1+s+p*s*t
K=1+q*s+2*p*s*t; L=2+q*s+p*s*t; J=1+q*s+p*s*t

def eq(lhs,rhs): assert sp.simplify(lhs-rhs)==0
# Independent envelope comparisons.
eq(A-B,s*(p*q*t-1))
eq(B-C,s*(p-2)*(q*t-1))
eq(C-D,q*s*t-1)
eq(C-E,s*(q*t-p))
eq(D-E,1-p*s)
eq(F-G,s*(p-1)*(q*t-1))
# Chain envelope comparisons.
eq((A+2*F)-(B+2*F),A-B)
eq((B+2*F)-(K+2*J),s*(3*q-4)*(p*t-1))
eq((A+2*F)-(K+2*J),s*(q-1)*(4*p*t-3))
eq((B+2*F)-(L+2*J),-1+s*(3*p*q*t-3*p*t-3*q+4))
eq((A+2*F)-(L+2*J),-1+s*(4*p*q*t-3*p*t-3*q+3))
eq((K+2*J)-(L+2*J),p*s*t-1)
# Radial derivative numerators for all nontrivial combinations.
def deriv(U,m):
    N=U+2*q*H; I=m+2*G+2*q*H
    return sp.factor(sp.diff(N,s)*I-N*sp.diff(I,s))
D_BC=deriv(B+2*F,C); D_BD=deriv(B+2*F,D); D_BE=deriv(B+2*F,E)
D_CC=deriv(K+2*J,C); D_CD=deriv(K+2*J,D); D_CE=deriv(K+2*J,E); D_DD=deriv(L+2*J,D)
expected={
'D_BC':(3*p-4)*(2*q+3)*(q*t-1),
'D_BD':6*p*q**2*t+14*p*q*t-6*p*q-9*p-6*q**2*t-9*q*t+10*q+16,
'D_BE':(p-1)*(2*q+3)*(3*q*t-4),
'D_CC':(p-q)*(2*q+3)*(4*t-3),
'D_CD':10*p*q*t-6*p*q+16*p*t-9*p-6*q**2*t+6*q**2-9*q*t+14*q,
'D_CE':(4*p-3*q)*(2*q+3)*(t-1),
'D_DD':6*(p-q)*(q+2)*(t-1),
}
for name,got in [('D_BC',D_BC),('D_BD',D_BD),('D_BE',D_BE),('D_CC',D_CC),('D_CD',D_CD),('D_CE',D_CE),('D_DD',D_DD)]: eq(got,expected[name])
Aend=6*p**2*q+9*p**2-6*p*q**2-24*p*q-16*p+6*q**2+9*q
assert sp.simplify(D_BD.subs(t,1/q)-(5*p+4*q+7))==0
assert sp.simplify(D_BD.subs(t,1/p)+Aend/p)==0
assert sp.simplify(D_CD.subs(t,1/p)+Aend/p)==0
assert sp.simplify(D_CD.subs(t,1)-(4*p*q+7*p+5*q))==0
A_sub=sp.expand(Aend.subs(q,2*p+r))
assert sp.expand(-A_sub-(12*p**3-2*p+15*p**2+9*r*(2*p**2-1)+6*(p-1)*r**2))==0
print('independent formulas: m0=min(A,B,C,D,E), m1=min(F,G), H fixed')
print('chain formula: U=(2qH+min(A+2F,B+2F,K+2J,L+2J))/(2pq)')
print('radial derivative identities=True (7 nontrivial cases)')
print('endpoint polynomial -A is positive for p>=3, q>2p')
print('full two-dimensional upper-bound algebra certificate=True')

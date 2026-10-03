#!/opt/miniconda3/bin/python
"""Algebraic identities for the four-chain upper bound in p=2r,q=4r+3."""
import sympy as sp

r, z, y = sp.symbols('r z y', positive=True)
q = 4*r + 3
C1 = (1/(r*q)+1/(2*r)) + sp.Rational(5,2)/r*z + (sp.Rational(3,4)/q+sp.Rational(1,2))*y
C2 = (1/r+sp.Rational(3,2)/(r*q)) + sp.Rational(5,4)/r*z + (1/q+sp.Rational(1,2))*y
C3 = (1/(r*q)+1/(2*r)) + sp.Rational(5,4)/r*z + (1+sp.Rational(3,2)/q)*y
C4 = (1/(2*r)+sp.Rational(3,4)/(r*q)) + sp.Rational(5,2)/r*z + (1/q+sp.Rational(1,2))*y
z0 = (2*q+3)/(5*q)
y0 = 1/r
N0 = (8*q+13)/(4*r*q)

# Four compatible chains used for the upper envelope.  Each tuple is inner -> outer.
chains = [
    (((r,2*q,2), (r,2*q,1), (r,2,1)), ((1,1,2), (1,q,1))),
    (((2*r,q,2), (r,q,2), (r,1,2)), ((2,1,1), (1,q,1))),
    (((2*r,q,2), (2*r,q,1), (2*r,1,1)), ((1,1,2), (1,q,1))),
    (((2*r,2*q,1), (r,2*q,1), (r,2,1)), ((2,1,1), (1,q,1))),
]
for chain, ratios in chains:
    for inner, outer in zip(chain, chain[1:]):
        expected = ratios[0] if inner == chain[0] else ratios[1]
        assert all(sp.simplify(i - e*o) == 0 for i, e, o in zip(inner, expected, outer))

assert all(sp.factor(C.subs({z:z0, y:y0})-N0) == 0 for C in (C1,C2,C3,C4))
diffs = [sp.factor(C1-C2), sp.factor(C1-C3), sp.factor(C1-C4),
         sp.factor(C2-C3), sp.factor(C2-C4), sp.factor(C3-C4)]
assert all(d != 0 for d in diffs)
print('candidate point=', sp.factor(z0), 1/r)
print('common chain value=', sp.factor(N0))
print('chain difference identities=', len(diffs))
print('compatible four-chain certificate=True')
print('four-chain equality certificate=True')

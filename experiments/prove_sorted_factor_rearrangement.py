#!/opt/miniconda3/bin/python
"""Certificate for reducing each independent envelope to sorted factor triples."""
import itertools
import sympy as sp

# A>=B>=C>=0 and 1>=z>=y>=0 are parameterized by nonnegative increments.
c, u, v, t, w, h = sp.symbols('c u v t w h', nonnegative=True)
A, B, C = c + v + u, c + v, c
y, z, one = t, t + w, t + w + h
weights = {0: one, 1: z, 2: y}
factors = (A, B, C)
canonical = C*one + B*z + A*y
checked = 0
for perm in itertools.permutations(factors):
    # perm=(a,b,c) means c + b*z + a*y.
    expr = sp.expand(perm[2]*one + perm[1]*z + perm[0]*y - canonical)
    poly = sp.Poly(expr, c, u, v, t, w, h)
    assert all(coef >= 0 for coef in poly.coeffs()), (perm, expr)
    checked += 1
print('permutations checked=', checked)
print('sorted-factor rearrangement certificate=True')

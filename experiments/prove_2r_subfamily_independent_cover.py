#!/opt/miniconda3/bin/python
"""Symbolic independent-envelope cover for p=2r, q=4r+3.

The odd factors r and q are treated as distinct primes only through the divisor
profile {1,2,4,r,2r,4r,q,2q,4q,rq,2rq,4rq}; the proof below checks the
resulting finite grid family for every real r>=5 after substituting q=4r+3.
It proves only the independent lower-envelope reduction, not the full ratio theorem.
"""
import sympy as sp
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import grids, line, active

r = sp.symbols('r', real=True)
q = 4*r + 3
TOK = {
    1: '1', 2: '2', 4: '4', 17: 'r', 34: '2r', 68: '4r',
    71: 'q', 142: '2q', 284: '4q', 1207: 'rq', 2414: '2rq', 4828: '4rq',
}
VAL = {
    '1': sp.Integer(1), '2': sp.Integer(2), '4': sp.Integer(4),
    'r': r, '2r': 2*r, '4r': 4*r,
    'q': q, '2q': 2*q, '4q': 4*q,
    'rq': r*q, '2rq': 2*r*q, '4rq': 4*r*q,
}
VERTICES=((0,0),(1,0),(1,1))

def token_grid(g):
    return tuple(TOK[x] for x in g)

def sym_line(g):
    a,b,c=(VAL[x] for x in g)
    return (1/(a*b), 1/(a*c), 1/(b*c))

def val(l,z,y): return l[0]+l[1]*z+l[2]*y

def nonnegative(expr):
    num, den = sp.fraction(sp.factor(expr))
    assert sp.ask(sp.Q.positive(den.subs(r,5))) is not False
    poly = sp.Poly(sp.expand(num.subs(r, sp.Symbol('a')+5)), sp.Symbol('a'))
    return all(c >= 0 for c in poly.all_coeffs())

def cover_level(P):
    gs=list(grids(P))
    lines=[line(g) for g in gs]
    active_lines=[l for l in set(lines) if active(l, lines)]
    active_tokens={token_grid(next(g for g in gs if line(g)==l)) for l in active_lines}
    checked=0
    for g in gs:
        gt=token_grid(g)
        if gt in active_tokens:
            continue
        gl=sym_line(gt)
        dominators=[]
        for ct in sorted(active_tokens):
            cl=sym_line(ct)
            if all(nonnegative(val(gl,i,j)-val(cl,i,j)) for i,j in VERTICES):
                dominators.append(ct)
        if not dominators:
            raise AssertionError(('no symbolic dominator',P,gt))
        checked += 1
    return len(gs), len(active_tokens), checked

if __name__ == '__main__':
    # Numeric sample r=17 is only used to recover the fixed divisor-profile token names.
    for P in (4828,2414,34):
        print('level',P,'grids/active/omitted=',cover_level(P))
    print('symbolic independent-cover certificate=True for r>=5, q=4r+3')

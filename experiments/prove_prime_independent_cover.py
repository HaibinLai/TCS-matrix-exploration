#!/usr/bin/env python3
"""Symbolic cover certificate for independent lower envelopes.

For P*=(2pq,pq,p), the fixed 16/8/3 candidate grids from the q>2p
arrangement cover every divisor grid: every omitted line is dominated on the
whole triangle by one candidate line.  Dominance of affine lines is checked at
(0,0),(1,0),(1,1); symbolic positivity is certified after p=3+a,
q=2p+r (a,r>=0).
"""
from fractions import Fraction
import sympy as sp
from exact_multilevel_2d import grids, line

p,q,a,r=sp.symbols('p q a r', positive=True)
VERTICES=((0,0),(1,0),(1,1))
TOKENS={'1':sp.Integer(1),'2':sp.Integer(2),'p':p,'q':q,'2p':2*p,'2q':2*q,
        'pq':p*q,'2pq':2*p*q}
NUMTOK={1:1,2:2,23:'p',67:'q',46:'2p',134:'2q',1541:'pq',3082:'2pq'}
# Candidate sets read from the exact q>2p arrangement template.
CANDIDATES=[
 [('1','2pq','1'),('2','p','q'),('2','pq','1'),('2','q','p'),
  ('2p','q','1'),('2pq','1','1'),('2q','1','p'),('2q','p','1'),
  ('p','2','q'),('p','2q','1'),('p','q','2'),('pq','1','2'),
  ('pq','2','1'),('q','2','p'),('q','2p','1'),('q','p','2')],
 [('1','p','q'),('1','pq','1'),('1','q','p'),('p','1','q'),
  ('p','q','1'),('pq','1','1'),('q','1','p'),('q','p','1')],
 [('1','1','p'),('1','p','1'),('p','1','1')],
]

def sym_grid(g): return tuple(TOKENS[x] for x in g)
def sym_line(g):
    aa,bb,cc=sym_grid(g)
    return (1/(aa*bb),1/(aa*cc),1/(bb*cc))
def val(l,z,y): return l[0]+l[1]*z+l[2]*y
def num_grid(g,pv=23,qv=67):
    out=[]
    for x in g:
        if x=='1': out.append(1)
        elif x=='2': out.append(2)
        elif x=='p': out.append(pv)
        elif x=='q': out.append(qv)
        elif x=='2p': out.append(2*pv)
        elif x=='2q': out.append(2*qv)
        elif x=='pq': out.append(pv*qv)
        elif x=='2pq': out.append(2*pv*qv)
    return tuple(out)
def token_grid(g,pv=23,qv=67):
    rev={1:'1',2:'2',pv:'p',qv:'q',2*pv:'2p',2*qv:'2q',pv*qv:'pq',2*pv*qv:'2pq'}
    return tuple(rev[x] for x in g)
def positive_under_regime(expr):
    num,den=sp.fraction(sp.factor(expr))
    # All denominators here are positive on p>=3,q>2p.
    sub=sp.Poly(sp.expand(num.subs({p:3+a,q:2*(3+a)+r})),a,r)
    coeffs=sub.coeffs()
    return not coeffs or all(c>=0 for c in coeffs)

checked=0
for level,P in enumerate((2*23*67,23*67,23)):
    all_tokens=[token_grid(g) for g in grids(P)]
    cand=CANDIDATES[level]
    cand_num=[num_grid(g) for g in cand]
    for gt in all_tokens:
        if gt in cand: continue
        gnum=num_grid(gt)
        gl=line(gnum)
        dominators=[]
        for ct,cn in zip(cand,cand_num):
            cl=line(cn)
            if all(Fraction(gl[0]-cl[0])+Fraction(gl[1]-cl[1])*z+Fraction(gl[2]-cl[2])*y >= 0 for z,y in VERTICES):
                dominators.append(ct)
        if not dominators:
            raise AssertionError(('no dominator',level,gt))
        dom=dominators[0]
        diff=[sp.factor(x-y) for x,y in zip(sym_line(gt),sym_line(dom))]
        if not all(positive_under_regime(diff[0]+diff[1]*z+diff[2]*y)
                   for z,y in VERTICES):
            raise AssertionError(('symbolic failure',level,gt,dom,diff))
        print(f'level={level} omitted={gt} dominated_by={dom}')
        checked += 1
print(f'symbolic independent-cover certificate=True omitted={checked}')

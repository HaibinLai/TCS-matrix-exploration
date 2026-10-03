#!/usr/bin/env python3
"""Symbolic endpoint certificate for the q-family at z=1,y=1/9.

For prime q>3, every divisor of 27q, 9q, or 9 has a fixed base*q^e
pattern. At the selected aspect ratio, each grid proxy is A+B/q.  If the
claimed target line is no larger than every competitor at q=29 and at
q=infinity (1/q=0), linearity proves the comparison for every q>=29.
"""
from fractions import Fraction
from itertools import product
import sys
sys.path.insert(0, str(__file__).rsplit('/',1)[0])
from scan_boundary_hierarchies import grids

def nested_sym(c):
    return all(
        all(ei >= eo and bi % bo == 0 for (bi,ei),(bo,eo) in zip(inner,outer))
        for inner,outer in zip(c,c[1:])
    )


def symbolic_grid(g, q0=29):
    # q0 is prime, so detect whether a coordinate contains q.
    out=[]
    for d in g:
        if d % q0 == 0:
            out.append((d//q0, 1))
        else:
            out.append((d, 0))
    return tuple(out)


def add_sym(x,y): return (x[0]+y[0],x[1]+y[1])
def inv_term(factors):
    base=1; exp=0
    for b,e in factors: base*=b; exp+=e
    # coefficient for 1/base*q^exp; all terms here have exp 0 or 1.
    return (Fraction(0), Fraction(1,base)) if exp==1 else (Fraction(1,base),Fraction(0))

def h_sym(g):
    p1,p2,p3=g
    # z=1, y=1/9
    x=(0,0)
    for term in (inv_term((p1,p2)),inv_term((p1,p3))): x=add_sym(x,term)
    y=inv_term((p2,p3)); x=add_sym(x,(y[0]/9,y[1]/9))
    return x

def at(sym,q): return sym[0]+sym[1]/q

def no_greater(target, competitors):
    # target <= competitor at q=29 and q=infinity.
    bad=[]
    for c in competitors:
        if at(target,29)>at(c,29) or target[0]>c[0]: bad.append((target,c))
    return bad

if __name__=='__main__':
    q0=29; pstars=(27*q0,9*q0,9)
    choices_raw=[list(grids(p)) for p in pstars]
    choices=[[symbolic_grid(g,q0) for g in gs] for gs in choices_raw]
    chains=[c for c in product(*choices) if nested_sym(c)]
    target_i=[((q0,3,9)),((q0,3,3)),((9,1,1))]
    target_i=[symbolic_grid(g,q0) for g in target_i]
    target_i=[h_sym(g) for g in target_i]
    target_chain=[symbolic_grid(g,q0) for g in ((9,3,q0),(9,1,q0),(9,1,1))]
    target_n=(sum((h_sym(g)[0] for g in target_chain),Fraction(0)),sum((h_sym(g)[1] for g in target_chain),Fraction(0)))
    bad_i=[]
    for target,gs in zip(target_i,choices): bad_i.extend(no_greater(target,[h_sym(g) for g in gs]))
    nlines=[]
    for c in chains:
        s=(Fraction(0),Fraction(0))
        for g in c:s=add_sym(s,h_sym(g))
        nlines.append(s)
    bad_n=no_greater(target_n,nlines)
    print('q divisor pattern: choices',list(map(len,choices)),'nested chains',len(chains))
    print('independent targets',target_i,'bad endpoint comparisons',len(bad_i))
    print('nested target',target_n,'bad endpoint comparisons',len(bad_n))
    print('I', (sum((x[0] for x in target_i),Fraction(0)),sum((x[1] for x in target_i),Fraction(0))))
    print('N',target_n)

#!/usr/bin/env python3
"""Endpoint certificate for P*=(30q,15q,15), t=y/x=1/15.

For prime q>5, divisor patterns are fixed. The target independent lines and
nested chain are checked against every competitor at q=101 and q=infinity;
linearity in 1/q then covers q>=101 primes.
"""
from fractions import Fraction
from itertools import product
import sys
sys.path.insert(0, str(__file__).rsplit('/',1)[0])
from scan_boundary_hierarchies import grids

def nested_sym(c):
    return all(all(ei>=eo and bi%bo==0 for (bi,ei),(bo,eo) in zip(i,o)) for i,o in zip(c,c[1:]))
def sym_grid(g,q0):
    return tuple((d//q0,1) if d%q0==0 else (d,0) for d in g)
def add(x,y):return (x[0]+y[0],x[1]+y[1])
def term(fs):
    base=1;exp=0
    for b,e in fs:base*=b;exp+=e
    return (Fraction(0),Fraction(1,base)) if exp==1 else (Fraction(1,base),Fraction(0))
def h(g):
    p1,p2,p3=g; r=add(term((p1,p2)),term((p1,p3))); y=term((p2,p3)); return add(r,(y[0]/15,y[1]/15))
def at(l,q):return l[0]+l[1]/q
def no_greater(target, competitors):return sum(at(target,101)>at(c,101) or target[0]>c[0] for c in competitors)
if __name__=='__main__':
    q0=101; ps=(30*q0,15*q0,15)
    raw=[list(grids(p)) for p in ps]; choices=[[sym_grid(g,q0) for g in gs] for gs in raw]
    chains=[c for c in product(*choices) if nested_sym(c)]
    targets=[sym_grid(g,q0) for g in ((q0,5,6),(q0,3,5),(15,1,1))]
    ti=[h(g) for g in targets]
    tc=[sym_grid(g,q0) for g in ((15,2,q0),(15,1,q0),(15,1,1))]
    tn=(sum((h(g)[0] for g in tc),Fraction(0)),sum((h(g)[1] for g in tc),Fraction(0)))
    ilbad=sum(no_greater(t,[h(g) for g in gs]) for t,gs in zip(ti,choices))
    nlines=[]
    for c in chains:
        s=(Fraction(0),Fraction(0))
        for g in c:s=add(s,h(g))
        nlines.append(s)
    print('choices',list(map(len,choices)),'chains',len(chains))
    print('independent',ti,'bad endpoint comparisons',ilbad)
    print('nested',tn,'bad endpoint comparisons',no_greater(tn,nlines))
    print('I', (sum((x[0] for x in ti),Fraction(0)),sum((x[1] for x in ti),Fraction(0))))
    print('N',tn)
    # ratio formula: (45q+35)/(31q+135)
    print('limit',Fraction(45,31),float(Fraction(45,31)))

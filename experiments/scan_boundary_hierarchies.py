#!/usr/bin/env python3
"""Scan exact z=1 boundary overhead across processor hierarchies.

This is a discovery tool. Each hierarchy uses exact rational breakpoint
enumeration on t=y/x in [0,1]; it does not assert a universal bound.
"""
from fractions import Fraction
from itertools import product
from random import Random


def divisors(p): return [d for d in range(1,p+1) if p%d==0]
def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p//p1): yield (p1,p2,p//p1//p2)
def nested(c): return all(all(a%d==0 for a,d in zip(i,o)) for i,o in zip(c,c[1:]))
def line(g):
    a,b,c=g
    return (Fraction(1,a*b)+Fraction(1,a*c), Fraction(1,b*c))
def val(l,t): return l[0]+l[1]*t
def inter(l1,l2):
    a,b=l1; c,d=l2
    if b==d:return None
    return (c-a)/(b-d)
def lower(lines,t):return min(val(l,t) for l in lines)

def exact_boundary(ps):
    choices=[list(grids(p)) for p in ps]
    chains=[c for c in product(*choices) if nested(c)]
    if len(chains)>3000:return None
    ils=[[line(g) for g in gs] for gs in choices]
    nls=[]
    for c in chains:
        ls=[line(g) for g in c]
        nls.append((sum((l[0] for l in ls),Fraction(0)),sum((l[1] for l in ls),Fraction(0))))
    points={Fraction(0),Fraction(1)}
    for ls in ils+[nls]:
        for i,l in enumerate(ls):
            for q in ls[i+1:]:
                t=inter(l,q)
                if t is not None and 0<t<1:points.add(t)
    best=(Fraction(0),None)
    for t in sorted(points):
        I=sum((lower(ls,t) for ls in ils),Fraction(0)); N=lower(nls,t)
        r=N/I
        if r>best[0]:best=(r,t)
    return best[0],best[1],len(chains),[len(x) for x in choices],len(points)

def approximate_boundary(ps, steps=200):
    choices=[list(grids(p)) for p in ps]
    chains=[c for c in product(*choices) if nested(c)]
    if len(chains)>3000:return None
    lines=[[tuple(float(x) for x in line(g)) for g in gs] for gs in choices]
    nlines=[tuple(sum(float(line(g)[j]) for g in c) for j in range(2)) for c in chains]
    best=0.0
    for i in range(steps+1):
        t=i/steps
        I=sum(min(a+b*t for a,b in ls) for ls in lines)
        N=min(a+b*t for a,b in nlines)
        best=max(best,N/I)
    return best,len(chains),[len(x) for x in choices]

if __name__=='__main__':
    rng=Random(23)
    candidates=[]
    # Structured factorizations with P1/P2/P3 integer ratios.
    for p3 in range(2,16):
        for r2 in range(2,14):
            for r1 in range(2,14):
                ps=(p3*r2*r1,p3*r2,p3)
                if ps[0]<=420:candidates.append(ps)
    rng.shuffle(candidates)
    approx=[]
    for ps in candidates[:500]:
        out=approximate_boundary(ps)
        if out is not None: approx.append((out[0],ps,out[1:]))
    approx.sort(reverse=True)
    print('approximately evaluated',len(approx),'hierarchies')
    exact=[]
    for _,ps,_ in approx[:15]:
        out=exact_boundary(ps)
        if out is not None: exact.append((out[0],ps,out[1:]))
    exact.sort(reverse=True)
    for r,ps,meta in exact:
        print(ps,'ratio',r,float(r),'t/meta',meta)

#!/usr/bin/env python3
"""Exact four-chain upper-bound certificate for the prime hierarchy family.

For P*=(2pq,pq,p), four legal nested chains give an upper envelope U>=N:
A=(2pq,1,1)->(pq,1,1)->(p,1,1)
B=(pq,2,1)->(pq,1,1)->(p,1,1)
C=(2p,q,1)->(p,q,1)->(p,1,1)
D=(p,q,2)->(p,q,1)->(p,1,1).

The script checks exactly that max U/I equals R_p(q), and checks the radial
sign on every full-dimensional active cell of U/I.  It is a certificate for
N/I because N<=U; equality at (z,y)=(1,1/p) is checked separately.
"""
from fractions import Fraction as F
from itertools import product
import argparse
from exact_multilevel_2d import build_envelopes, line, value, subtract, intersect, inside, satisfies, DOMAIN, DOMAIN_VERTICES

def polygon(constraints):
    pts=[p for p in DOMAIN_VERTICES if satisfies(constraints,p)]
    for i,c1 in enumerate(constraints):
        for c2 in constraints[i+1:]:
            p=intersect(c1,c2)
            if inside(p) and satisfies(constraints,p): pts.append(p)
    return list(set(pts))

def full_dimensional(points):
    if len(points)<3: return False
    x0,y0=points[0]
    return any((x-x0)*(y2-y0)!=(y-y0)*(x2-x0)
               for x,y in points[1:] for x2,y2 in points[1:] if (x,y)!=(x2,y2))

def chain_lines(p,q):
    chains=[
      ((2*p*q,1,1),(p*q,1,1),(p,1,1)),
      ((p*q,2,1),(p*q,1,1),(p,1,1)),
      ((2*p,q,1),(p,q,1),(p,1,1)),
      ((p,q,2),(p,q,1),(p,1,1)),
    ]
    return [tuple(sum(line(g)[i] for g in c) for i in range(3)) for c in chains]

def check(p,q):
    _,ind,nested,_=build_envelopes((2*p*q,p*q,p))
    upper=chain_lines(p,q)
    # Exact overlay vertices for independent envelopes plus U.
    all_lines=[l for ls in ind for l in ls]+upper
    eq=[subtract(a,b) for i,a in enumerate(all_lines) for b in all_lines[i+1:]]
    points=set(DOMAIN_VERTICES)
    for e in eq:
        a,b,c=e
        if b:
            z=-a/b
            if inside((z,F(0))): points.add((z,F(0)))
        if c:
            y=-(a+b)/c
            if inside((F(1),y)): points.add((F(1),y))
        if b+c:
            z=-a/(b+c)
            if inside((z,z)): points.add((z,z))
    for i,e1 in enumerate(eq):
        for e2 in eq[i+1:]:
            pnt=intersect(e1,e2)
            if inside(pnt): points.add(pnt)
    best=(F(0),None)
    for z,y in points:
        I=sum(min(value(l,z,y) for l in ls) for ls in ind)
        U=min(value(l,z,y) for l in upper)
        if U/I>best[0]: best=(U/I,(z,y))
    target=F(p*(9*q+7),(6*p+3)*q+3*p*p+4*p)
    # Active-cell radial derivative check for U/I.
    cells=bad=0
    for u in upper:
      constraints_u=list(DOMAIN)+[tuple(u[i]-v[i] for i in range(3)) for v in upper if v!=u]
      for a,b,c in product(*ind):
        constraints=list(constraints_u)
        for chosen,ls in ((a,ind[0]),(b,ind[1]),(c,ind[2])):
            constraints.extend(tuple(chosen[i]-other[i] for i in range(3)) for other in ls if other!=chosen)
        pts=polygon(constraints)
        if not pts or not full_dimensional(pts): continue
        cells+=1
        i0=a[0]+b[0]+c[0]; ib=a[1]+b[1]+c[1]; ic=a[2]+b[2]+c[2]
        d0=u[1]*i0-u[0]*ib; d1=u[2]*i0-u[0]*ic
        ts=[y/z for z,y in pts if z>0]
        if ts and min(d0+d1*t for t in (min(ts),max(ts)))<0: bad+=1
    # At the claimed maximizer, U must equal the true nested envelope N.
    z,y=F(1),F(1,p)
    I=sum(min(value(l,z,y) for l in ls) for ls in ind)
    N=min(value(l,z,y) for l in nested)
    equality=(N/I==target and min(value(l,z,y) for l in upper)==N)
    print(f'p={p} q={q} Umax={best[0]} at={best[1]} target={target} '
          f'cells={cells} radial_bad={bad} witness_equality={equality}')
    if best[0]!=target or best[1]!=(F(1),F(1,p)) or bad or not equality:
        raise AssertionError((p,q,best,target,cells,bad,equality))

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--p',nargs='+',type=int,required=True); ap.add_argument('--q',nargs='+',type=int,required=True); args=ap.parse_args()
    cases=0
    for p,q in product(args.p,args.q):
        if q<=2*p: continue
        check(p,q); cases+=1
    print(f'checked={cases} four-chain upper-bound certificates')

#!/usr/bin/env python3
"""Exact active-cell radial derivative check for P*=(2pq,pq,p).

For a feasible combination of one line from each independent envelope and one
nested line, N/I as a function of s at fixed t has affine-over-affine derivative
D(t).  This script uses exact half-plane feasibility in (z,y) and checks D at
all t in [0,1], a deliberately stronger condition than the feasible cell's
actual t projection.
"""
from fractions import Fraction as F
from itertools import product
import argparse
from exact_multilevel_2d import build_envelopes, DOMAIN, DOMAIN_VERTICES, intersect, inside, satisfies

def polygon(lines):
    cs=list(DOMAIN)
    for chosen, all_lines in lines:
        cs.extend(tuple(chosen[i]-other[i] for i in range(3)) for other in all_lines if other != chosen)
    points=[]
    points.extend(p for p in DOMAIN_VERTICES if satisfies(cs,p))
    for i,c1 in enumerate(cs):
        for c2 in cs[i+1:]:
            p=intersect(c1,c2)
            if inside(p) and satisfies(cs,p): points.append(p)
    return list(set(points))

def full_dimensional(points):
    if len(points) < 3:
        return False
    base = points[0]
    return any((x-base[0])*(y2-base[1]) != (y-base[1])*(x2-base[0])
               for x,y in points[1:] for x2,y2 in points[1:]
               if (x,y) != (x2,y2))

def main(p,q):
    _,ind,nested,_=build_envelopes((2*p*q,p*q,p))
    feasible_count=bad=0
    bad_examples=[]
    for n in nested:
      for a,b,c in product(*ind):
        points=polygon([(a,ind[0]),(b,ind[1]),(c,ind[2]),(n,nested)])
        if not points or not full_dimensional(points): continue
        feasible_count += 1
        i0=a[0]+b[0]+c[0]
        ib=a[1]+b[1]+c[1]
        ic=a[2]+b[2]+c[2]
        d0=n[1]*i0-n[0]*ib
        d1=n[2]*i0-n[0]*ic
        # t=y/z is a linear-fractional function on each convex cell, so its
        # extrema occur at polygon vertices (ignore the z=0 corner).
        ts=[y/z for z,y in points if z > 0]
        if not ts:
            continue
        d_at = [d0+d1*t for t in (min(ts),max(ts))]
        if min(d_at) < 0:
            bad += 1
            if len(bad_examples)<3: bad_examples.append((n,a,b,c,d0,d0+d1))
    print(f'p={p} q={q} active={tuple(map(len,ind))}/{len(nested)} feasible_cells={feasible_count} bad={bad}')
    for x in bad_examples: print('BAD',x)
    if bad: raise SystemExit(1)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--p',type=int,required=True);ap.add_argument('--q',type=int,required=True);args=ap.parse_args();main(args.p,args.q)

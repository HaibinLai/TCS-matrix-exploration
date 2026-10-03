#!/usr/bin/env python3
"""Exact 2-D envelope search after exact lower-envelope pruning.

For each candidate affine line, feasibility of its lower-envelope region is
checked by enumerating vertices of the bounded half-plane intersection. The
remaining arrangement is then enumerated exactly. This computes a full
2-D result for one fixed hierarchy, assuming the vertex characterization;
it is still not a theorem for all hierarchies.
"""
from fractions import Fraction
from itertools import product
import argparse


def divisors(p):
    return [d for d in range(1, p + 1) if p % d == 0]


def grids(p):
    for p1 in divisors(p):
        for p2 in divisors(p // p1):
            yield (p1, p2, p // p1 // p2)


def nested(chain):
    return all(all(inner[d] % outer[d] == 0 for d in range(3)) for inner, outer in zip(chain, chain[1:]))


def line(grid):
    p1, p2, p3 = grid
    return (Fraction(1,p1*p2), Fraction(1,p1*p3), Fraction(1,p2*p3))


def add(*ls):
    return tuple(sum((l[i] for l in ls), Fraction(0)) for i in range(3))


def value(l,z,y):
    return l[0]+l[1]*z+l[2]*y


def inter(e1,e2):
    a1,b1,c1=e1; a2,b2,c2=e2
    det=b1*c2-c1*b2
    if det==0:return None
    return ((c1*a2-a1*c2)/det,(a1*b2-b1*a2)/det)


def inside(z,y):return Fraction(0)<=y<=z<=Fraction(1)

# A + B z + C y <= 0; domain is y>=0, z-y>=0, z<=1.
DOMAIN=[(Fraction(0),Fraction(0),Fraction(-1)),
        (Fraction(0),Fraction(-1),Fraction(1)),
        (Fraction(-1),Fraction(1),Fraction(0))]
CORNERS=[(Fraction(0),Fraction(0)),(Fraction(1),Fraction(0)),(Fraction(1),Fraction(1))]


def satisfies(constraints,p):
    z,y=p
    return all(a+b*z+c*y<=0 for a,b,c in constraints)


def lower_active(candidate, lines):
    # Region candidate <= every other line, plus domain.
    constraints=list(DOMAIN)
    for other in lines:
        if other != candidate:
            constraints.append(tuple(candidate[i]-other[i] for i in range(3)))
    if any(satisfies(constraints,p) for p in CORNERS): return True
    for i,e1 in enumerate(constraints):
        for e2 in constraints[i+1:]:
            p=inter(e1,e2)
            if p is not None and inside(*p) and satisfies(constraints,p):
                return True
    return False


def equality(l1,l2):return tuple(a-b for a,b in zip(l1,l2))


def edge_points(e):
    a,b,c=e; out=[]
    if b: out.append((-a/b,Fraction(0)))
    if c: out.append((Fraction(1),-(a+b)/c))
    if b+c: 
        z=-a/(b+c); out.append((z,z))
    return out


def lower(lines,z,y):return min(value(l,z,y) for l in lines)


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pstars', nargs=3, type=int, default=(132,66,6))
    args = parser.parse_args()
    pstars=tuple(args.pstars)
    choices=[list(grids(p)) for p in pstars]
    chains=[c for c in product(*choices) if nested(c)]
    ilines=[]; active_counts=[]
    for gs in choices:
        ls=list({line(g) for g in gs})
        active=[l for l in ls if lower_active(l,ls)]
        ilines.append(active); active_counts.append(len(active))
    nall=list({add(line(c[0]),line(c[1]),line(c[2])) for c in chains})
    nactive=[l for l in nall if lower_active(l,nall)]
    eq=[]
    for ls in ilines:
        eq += [equality(a,b) for i,a in enumerate(ls) for b in ls[i+1:]]
    eq += [equality(a,b) for i,a in enumerate(nactive) for b in nactive[i+1:]]
    pts=set(CORNERS)
    for e in eq:
        pts.update(p for p in edge_points(e) if inside(*p))
    for i,e1 in enumerate(eq):
        for e2 in eq[i+1:]:
            p=inter(e1,e2)
            if p is not None and inside(*p):pts.add(p)
    all_i=[list({line(g) for g in gs}) for gs in choices]
    best=(Fraction(0),None)
    for z,y in pts:
        I=sum((lower(ls,z,y) for ls in all_i),Fraction(0))
        N=lower(nall,z,y)
        r=N/I
        if r>best[0]:best=(r,(z,y,I,N))
    print('P*',pstars,'chains',len(chains))
    print('active independent',active_counts,'active nested',len(nactive))
    print('equality lines',len(eq),'vertices',len(pts))
    print('max ratio',best[0],float(best[0]),'at',best[1])

#!/usr/bin/env python3
"""Exact Sturm exclusion of p=99 quadratic topology-event roots."""
import sys,itertools,math,os
from fractions import Fraction as F
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import build_envelopes,line
p=int(os.environ.get('PRIME_P','99'));q0=int(os.environ.get('Q0','997'))
ps=(2*p*q0,p*q0,p)
choices,ind,nested,stats=build_envelopes(ps)
def invpair(x,y):
    exponent=x[1]+y[1]
    if exponent==0:return (F(1,x[0]*y[0]),F(0))
    if exponent==1:return (F(0),F(1,x[0]*y[0]))
    raise AssertionError((x,y))
def sl(g):
 a,b,c=tuple((d//q0,1) if d%q0==0 else (d,0) for d in g)
 return (invpair(a,b),invpair(a,c),invpair(b,c))
def add(ls):return tuple((sum(x[i][0] for x in ls),sum(x[i][1] for x in ls)) for i in range(3))
inds=[]
for k,gs in enumerate(choices):
 mp={}
 for g in gs: mp.setdefault(line(g),[]).append(sl(g))
 inds.append([mp[x][0] for x in ind[k]])
chains=[]
for a in choices[0]:
 for b in choices[1]:
  if any(x%y for x,y in zip(a,b)):continue
  for c in choices[2]:
   if all(x%y==0 for x,y in zip(b,c)):chains.append((a,b,c))
mp={}
for chain in chains:
 key=tuple(sum(line(g)[i] for g in chain) for i in range(3));mp.setdefault(key,[]).append(add([sl(g) for g in chain]))
inds.append([mp[x][0] for x in nested])
# poly tuples low first
def trim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a or [F(0)])
def addp(a,b):
 return trim(tuple((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))))
def subp(a,b):
 return trim(tuple((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))))
def mulp(a,b):
 o=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):o[i+j]+=x*y
 return trim(o)
def det3(rows):
 a,b,c=rows
 def pr(x,y,z):return mulp(mulp(x,y),z)
 return subp(addp(addp(pr(a[0],b[1],c[2]),pr(a[1],b[2],c[0])),pr(a[2],b[0],c[1])),addp(addp(pr(a[2],b[1],c[0]),pr(a[0],b[2],c[1])),pr(a[1],b[0],c[2])))
def diff(x,y):return tuple((a[0]-b[0],a[1]-b[1]) for a,b in zip(x,y))
def norm(a):
 a=trim(a)
 for x in a:
  if x:return tuple(v/x for v in a)
 return a

def peval(a,r):return sum(float(x)*r**i for i,x in enumerate(a))

def expr(a,u): return sum(float(x)*u**i for i,x in enumerate(a))
# Collect every quadratic triple determinant.
quads={}
for env,ls in enumerate(inds):
    for i,j,k in itertools.combinations(range(len(ls)),3):
        poly=norm(det3([ls[i],ls[j],ls[k]]))
        if len(poly)==3:
            quads.setdefault(poly,[]).append((env,i,j,k))

import sympy as sp
u=sp.symbols("u")
u0=sp.Rational(1,q0)
root_total=0
endpoint_zero=0
count_hist={}
endpoint_records=[]

def coeff_at(L,r):
    return tuple(x[0]+x[1]*r for x in L)
def eval_line(L,r,z,y):
    a,b,c=coeff_at(L,r)
    return a+b*z+c*y

def inspect_source(poly, source):
    env,i,j,k=source; ls=inds[env]
    r=F(0)
    Li,Lj,Lk=[coeff_at(ls[t],r) for t in (i,j,k)]
    E=tuple(a-b for a,b in zip(Li,Lj)); G=tuple(a-b for a,b in zip(Li,Lk))
    det=E[1]*G[2]-E[2]*G[1]
    record={"source":source,"det_direction_at_0":det}
    if det:
        z=(E[2]*G[0]-E[0]*G[2])/det
        y=(E[0]*G[1]-E[1]*G[0])/det
        record["point_at_0"]=(z,y)
        record["inside_at_0"]=bool(F(0)<=y<=z<=1)
        v=eval_line(ls[i],r,z,y)
        gaps=[eval_line(L,r,z,y)-v for L in ls]
        record["min_owner_gap_at_0"]=min(gaps)
    else:
        record["point_at_0"]="parallel_or_coincident"
    return record

for poly in quads:
    expr=sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(poly))
    P=sp.Poly(expr,u,domain=sp.QQ)
    # Strip endpoint factors, then count roots in the open interval by the
    # sign-variation difference of the exact Sturm chain.
    at0=(P.eval(0)==0)
    atu0=(P.eval(u0)==0)
    stripped=sp.Poly(expr,u,domain=sp.QQ)
    if at0:
        stripped=sp.Poly(sp.cancel(stripped.as_expr()/u),u,domain=sp.QQ)
    if atu0:
        stripped=sp.Poly(sp.cancel(stripped.as_expr()/(u-u0)),u,domain=sp.QQ)
    chain=sp.sturm(stripped.as_expr(),u)
    def variations(x):
        signs=[]
        for h in chain:
            value=sp.factor(h.subs(u,x))
            if value==0: continue
            signs.append(1 if value>0 else -1)
        return sum(a!=b for a,b in zip(signs,signs[1:]))
    strict=variations(sp.Rational(0))-variations(u0)
    root_total += strict
    count_hist[strict]=count_hist.get(strict,0)+1
    if at0 or atu0:
        endpoint_zero += int(at0 or atu0)
        endpoint_records.append((poly,at0,atu0,[inspect_source(poly,s) for s in quads[poly]]))
print("active_counts",tuple(map(len,inds)))
print("quadratic_unique",len(quads),"source_triples",sum(map(len,quads.values())))
print("sturm_distinct_roots_closed_interval",sum(sp.Poly(sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(poly)),u,domain=sp.QQ).count_roots(sp.Rational(0),u0) for poly in quads))
print("sturm_roots_open_interval",root_total,"count_hist",count_hist,"endpoint_polys",len(endpoint_records))
for poly,at0,atu0,recs in endpoint_records:
    print("ENDPOINT_POLY",poly,"at0",at0,"atu0",atu0,"sources",len(recs))
    for rec in recs: print("  ",rec)
# A determinant root is only a topology event if its triple intersection is
# inside the aspect-ratio domain and is attained by the active envelope.  The
# root count above is therefore an over-inclusive diagnostic; owner-filter
# every isolated root before asserting absence of active events.
def as_expr(pair):
    return sp.Rational(pair[0].numerator,pair[0].denominator) + sp.Rational(pair[1].numerator,pair[1].denominator)*u

def sign_at_root(expr, root_poly, left, right):
    poly=sp.Poly(sp.factor(expr),u,domain=sp.QQ)
    if poly.is_zero:return 0
    if sp.gcd(poly,root_poly).degree()>0:return 0
    if poly.count_roots(left,right)>0:return None
    v=poly.eval((left+right)/2)
    return 1 if v>0 else -1 if v<0 else 0

def quotient_sign(num, den, root_poly, left, right):
    sn=sign_at_root(num,root_poly,left,right); sd=sign_at_root(den,root_poly,left,right)
    if sn is None or sd is None or sd==0:return None
    return 0 if sn==0 else sn*sd

def owner_at_root(ls, root_poly, left, right, triple):
    i,j,k=triple
    E=[sp.factor(as_expr(ls[i][t])-as_expr(ls[j][t])) for t in range(3)]
    G=[sp.factor(as_expr(ls[i][t])-as_expr(ls[k][t])) for t in range(3)]
    det=sp.factor(E[1]*G[2]-E[2]*G[1])
    znum=sp.factor(E[2]*G[0]-E[0]*G[2]); ynum=sp.factor(E[0]*G[1]-E[1]*G[0])
    sdet=sign_at_root(det,root_poly,left,right)
    if sdet in (None,0):return False,'singular',None
    tests=[quotient_sign(ynum,det,root_poly,left,right),
           quotient_sign(sp.factor(znum-ynum),det,root_poly,left,right),
           quotient_sign(sp.factor(det-znum),det,root_poly,left,right)]
    if any(x is None for x in tests):return False,'unknown-domain',tests
    if any(x<0 for x in tests):return False,'outside-domain',tests
    gaps=[]
    for t in range(len(ls)):
        da=sp.factor(as_expr(ls[t][0])-as_expr(ls[i][0]))
        db=sp.factor(as_expr(ls[t][1])-as_expr(ls[i][1]))
        dc=sp.factor(as_expr(ls[t][2])-as_expr(ls[i][2]))
        gap=sp.factor(da*det+db*znum+dc*ynum)
        gaps.append(quotient_sign(gap,det,root_poly,left,right))
    if any(x is None for x in gaps):return False,'unknown-owner',gaps
    return all(x>=0 for x in gaps),'active' if all(x>=0 for x in gaps) else 'above-envelope',gaps

active_roots=[]
for poly,sources in quads.items():
    expr=sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(poly))
    P=sp.Poly(expr,u,domain=sp.QQ)
    for rr in sp.polys.polytools.intervals(P,eps=sp.Rational(1,10**20)):
        (a,b),mult=rr
        if b<=0 or a>=u0:continue
        for src in sources:
            ok,kind,data=owner_at_root(inds[src[0]],P,a,b,src[1:])
            active_roots.append((poly,src,ok,kind,data))
print('interior_root_source_owner_checks',len(active_roots))
for rec in active_roots:print('ROOT_OWNER',rec)
assert all(not rec[2] for rec in active_roots)
assert all(not atu0 for _,_,atu0,_ in endpoint_records)
print(f"certificate=True: no active quadratic topology event in (0,1/{q0}]; endpoint-only roots are handled separately")

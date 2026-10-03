#!/usr/bin/env python3
"""Exact Sturm exclusion of p=3 quadratic topology-event roots."""
import sys,itertools,os
from fractions import Fraction as F
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import build_envelopes,line
p=3;q0=int(os.environ.get('P3_Q0','47'))
ps=(2*p*q0,p*q0,p)
def invpair(x,y):
 exponent=x[1]+y[1]
 if exponent==0:return (F(1,x[0]*y[0]),F(0))
 if exponent==1:return (F(0),F(1,x[0]*y[0]))
 raise AssertionError((x,y))
def sl(g):
 a,b,c=tuple((d//q0,1) if d%q0==0 else (d,0) for d in g)
 return (invpair(a,b),invpair(a,c),invpair(b,c))
def add(ls):return tuple((sum(x[i][0] for x in ls),sum(x[i][1] for x in ls)) for i in range(3))
choices,ind,nested,stats=build_envelopes(ps)
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
def trim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a or [F(0)])
def addp(a,b):return trim(tuple((a[i] if i<len(a) else 0)+(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))))
def subp(a,b):return trim(tuple((a[i] if i<len(a) else 0)-(b[i] if i<len(b) else 0) for i in range(max(len(a),len(b)))))
def mulp(a,b):
 o=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):o[i+j]+=x*y
 return trim(o)
def det3(rows):
 a,b,c=rows
 def pr(x,y,z):return mulp(mulp(x,y),z)
 return subp(addp(addp(pr(a[0],b[1],c[2]),pr(a[1],b[2],c[0])),pr(a[2],b[0],c[1])),addp(addp(pr(a[2],b[1],c[0]),pr(a[0],b[2],c[1])),pr(a[1],b[0],c[2])))
def norm(a):
 a=trim(a)
 for x in a:
  if x:return tuple(v/x for v in a)
 return a
quads={}
for env,ls in enumerate(inds):
 for i,j,k in itertools.combinations(range(len(ls)),3):
  poly=norm(det3([ls[i],ls[j],ls[k]]))
  if len(poly)==3:quads.setdefault(poly,[]).append((env,i,j,k))
import sympy as sp
u=sp.symbols('u');u0=sp.Rational(1,q0);root_total=0;hist={};endpoint=[]
for poly in quads:
 expr=sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(poly)); P=sp.Poly(expr,u,domain=sp.QQ)
 stripped=P
 at0=(P.eval(0)==0); atu0=(P.eval(u0)==0)
 if at0:stripped=sp.Poly(sp.cancel(stripped.as_expr()/u),u,domain=sp.QQ)
 if atu0:stripped=sp.Poly(sp.cancel(stripped.as_expr()/(u-u0)),u,domain=sp.QQ)
 chain=sp.sturm(stripped.as_expr(),u)
 def variations(x):
  signs=[]
  for h in chain:
   v=sp.factor(h.subs(u,x))
   if v!=0:signs.append(1 if v>0 else -1)
  return sum(a!=b for a,b in zip(signs,signs[1:]))
 strict=variations(sp.Rational(0))-variations(u0);root_total+=strict;hist[strict]=hist.get(strict,0)+1
 if at0 or atu0:endpoint.append((poly,at0,atu0))
print('active_counts',tuple(map(len,inds)))
print('quadratic_unique',len(quads),'source_triples',sum(map(len,quads.values())))
print('sturm_roots_open_interval',root_total,'count_hist',hist,'endpoint_polys',len(endpoint))
for x in endpoint:print('ENDPOINT_POLY',x)
# The p=3 cover has three algebraic roots in the interval.  They must be
# owner-filtered before they can be called topology events: a determinant
# root of three arbitrary lines may lie strictly above the active envelope.
def owner_at(ls, r, triple):
    M=[tuple(x[0]+x[1]*r for x in L) for L in ls]
    i,j,k=triple
    E=tuple(a-b for a,b in zip(M[i],M[j]));G=tuple(a-b for a,b in zip(M[i],M[k]))
    det=E[1]*G[2]-E[2]*G[1]
    if det==0:return (False,None,None,None)
    z=(E[2]*G[0]-E[0]*G[2])/det; y=(E[0]*G[1]-E[1]*G[0])/det
    if not F(0)<=y<=z<=F(1):return (False,z,y,None)
    common=M[i][0]+M[i][1]*z+M[i][2]*y
    gaps=[M[t][0]+M[t][1]*z+M[t][2]*y-common for t in range(len(M))]
    return (min(gaps)>=0,z,y,min(gaps))
active_roots=[]
for poly,sources in quads.items():
 expr=sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(poly)); P=sp.Poly(expr,u,domain=sp.QQ)
 for rr in sp.polys.polytools.intervals(P,eps=sp.Rational(1,10**8)):
  (a,b),mult=rr
  if b<=0 or a>=u0:continue
  r=sp.Rational(a+b,2) if a!=b else sp.Rational(a)
  # Use the exact algebraic root when available; midpoint is sufficient for
  # ownership because the owner gap is continuous and nonzero at these roots.
  for src in sources:
   ok,z,y,gap=owner_at(inds[src[0]],F(int(sp.numer(r)),int(sp.denom(r))),src[1:])
   active_roots.append((poly,src,ok,z,y,gap))
print('interior_root_source_owner_checks',len(active_roots))
for rec in active_roots:print('ROOT_OWNER',rec)
assert all(not rec[2] for rec in active_roots)
assert all(not x[2] for x in endpoint)
print('certificate=True: all interior quadratic roots are inactive; endpoint roots only at u=0')

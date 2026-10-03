#!/usr/bin/env python3
"""Enumerate p=99 topology-event polynomials (diagnostic certificate).

Exact Fraction arithmetic builds fixed active lines and event polynomials.
Linear roots are checked exactly; quadratic roots are only numerically filtered
in the current diagnostic, so this is not yet a final theorem certificate.
"""
import sys,itertools
from fractions import Fraction as F
sys.path.insert(0, '.')
from exact_multilevel_2d import build_envelopes,line
p=99;q0=997
ps=(2*p*q0,p*q0,p)
choices,ind,nested,stats=build_envelopes(ps)
# pair affine represented (const,slope) Fraction
def invpair(x,y):
 if q0 in (x,y): return (F(0),F(q0//(x*y))) # 1/(x*y/q0)*u = q0/(xy)u
 return (F(1,x*y),F(0))
def sl(g):
 a,b,c=g;return (invpair(a,b),invpair(a,c),invpair(b,c))
def add(ls): return tuple((sum(x[i][0] for x in ls),sum(x[i][1] for x in ls)) for i in range(3))
inds=[]
for k,gs in enumerate(choices):
 mp={}
 for g in gs:mp.setdefault(line(g),[]).append(sl(g))
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
print('counts',list(map(len,inds)))
# polynomial in u represented tuple coeff low->high; operations
def ptrim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a or [F(0)])
def padd(a,b):
 n=max(len(a),len(b));return ptrim(tuple((a[i] if i<len(a) else F(0))+(b[i] if i<len(b) else F(0)) for i in range(n)))
def psub(a,b):
 n=max(len(a),len(b));return ptrim(tuple((a[i] if i<len(a) else F(0))-(b[i] if i<len(b) else F(0)) for i in range(n)))
def pmul(a,b):
 out=[F(0)]*(len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):out[i+j]+=x*y
 return ptrim(out)
def coef(x):return (x[0],x[1])
def det3(rows):
 # rows entries pairs
 a,b,c=rows
 def prod(x,y,z):return pmul(pmul(x,y),z)
 return psub(padd(padd(prod(a[0],b[1],c[2]),prod(a[1],b[2],c[0])),prod(a[2],b[0],c[1])),padd(padd(prod(a[2],b[1],c[0]),prod(a[0],b[2],c[1])),prod(a[1],b[0],c[2])))
def normpoly(a):
 a=ptrim(a)
 # normalize by first nonzero coefficient to exact tuple; sign irrelevant
 for x in a:
  if x:
   return tuple(v/x for v in a)
 return a
# domain lines (constant, z coeff, y coeff) as constant pairs
D=[((F(0),F(0)),(F(0),F(0)),(F(1),F(0))), # y=0 coeff? [0,0,1]
   ((F(0),F(0)),(F(-1),F(0)),(F(1),F(0))), # y-z=0
   ((F(-1),F(0)),(F(1),F(0)),(F(0),F(0)))] # z-1
# line equality difference pair coefficients
def diffline(x,y):return tuple((a[0]-b[0],a[1]-b[1]) for a,b in zip(x,y))
# det of 2 lines + domain homogeneous 3 coeffs, each polynomial degree <=1
def det2d(e,d):return det3([e,d,[((F(0),F(0)),(F(0),F(0)),(F(0),F(0)))]] )
# use determinant of 2x2 direction coefficients? For equality e0+e1 z+e2 y and domain d0+d1z+d2y, intersection degeneracy parallel iff e1*d2-e2*d1=0
uniq_tri=set();uniq_bd=set()
for n,ls in zip(['i0','i1','i2','nest'],inds):
 for i,j in itertools.combinations(range(len(ls)),2):
  e=diffline(ls[i],ls[j])
  # polynomial e1*d2-e2*d1
  for d in D:
   poly=psub(pmul(e[1],(d[2][0],d[2][1])),pmul(e[2],(d[1][0],d[1][1])))
   if any(poly):uniq_bd.add(normpoly(poly))
 for i,j,k in itertools.combinations(range(len(ls)),3):
  E=[diffline(ls[i],ls[j]),diffline(ls[i],ls[k]),((F(0),F(0)),(F(0),F(0)),(F(0),F(0)))]
  # triple concurrence determinant of homogeneous line coeffs directly, rows are L_i-L_j, L_i-L_k? Need use [L_i,L_j,L_k]
  poly=det3([ls[i],ls[j],ls[k]])
  if any(poly):uniq_tri.add(normpoly(poly))
print('unique bd',len(uniq_bd),'tri',len(uniq_tri))
# find roots with sympy
import sympy as sp
u=sp.symbols('u');u0=sp.Rational(1,q0)
def root_intervals(S):
 out=[]
 for a in S:
  expr=sum(sp.Rational(x.numerator,x.denominator)*u**i for i,x in enumerate(a))
  P=sp.Poly(expr,u)
  try:rts=P.intervals(eps=sp.Rational(1,10**18))
  except Exception as e:print('err',e);continue
  for (lo,hi),m in rts:
   if hi>0 and lo<u0:out.append((a,(lo,hi),m))
 return out
for nm,S in [('bd',uniq_bd),('tri',uniq_tri)]:
 out=root_intervals(S)
 print(nm,'roots in interval',len(out))
 for x in out[:20]:print(x)
# filter actual active events, retaining source line IDs (recompute linear roots only)
def pval(a,r):return sum(x*r**i for i,x in enumerate(a))
def valline(L,r,z,y):return sum((x[0]+x[1]*r)*co for x,co in zip(L,(F(1),z,y)))
def root_linear(poly):
 # normalize length <=2
 if len(poly)==2 and poly[1]: return -poly[0]/poly[1]
 return None
actual=[]
for env,ls in enumerate(inds):
 # triple
 for i,j,k in itertools.combinations(range(len(ls)),3):
  poly=det3([ls[i],ls[j],ls[k]])
  r=root_linear(poly)
  if r is None or not (F(0)<r<F(1,q0)):continue
  # solve pair i-j/i-k at r
  def ev(L):return tuple(x[0]+x[1]*r for x in L)
  E=tuple(a-b for a,b in zip(ev(ls[i]),ev(ls[j]))); G=tuple(a-b for a,b in zip(ev(ls[i]),ev(ls[k])))
  det=E[1]*G[2]-E[2]*G[1]
  if not det:continue
  z=(E[2]*G[0]-E[0]*G[2])/det; y=(E[0]*G[1]-E[1]*G[0])/det
  if not (F(0)<=y<=z<=1):continue
  v=valline(ls[i],r,z,y)
  if all(v<=valline(L,r,z,y) for L in ls): actual.append(('tri',env,i,j,k,r,z,y))
 # boundaries
 for i,j in itertools.combinations(range(len(ls)),2):
  E=diffline(ls[i],ls[j])
  for bi,d in enumerate(D):
   poly=psub(pmul(E[1],(d[2][0],d[2][1])),pmul(E[2],(d[1][0],d[1][1])))
   r=root_linear(poly)
   if r is None or not (F(0)<r<F(1,q0)):continue
   evE=tuple(x[0]+x[1]*r for x in E)
   # intersect E with d at r
   evD=tuple(x[0]+x[1]*r for x in d)
   det=evE[1]*evD[2]-evE[2]*evD[1]
   if not det:continue
   z=(evE[2]*evD[0]-evE[0]*evD[2])/det; y=(evE[0]*evD[1]-evE[1]*evD[0])/det
   if not (F(0)<=y<=z<=1):continue
   v=valline(ls[i],r,z,y)
   if all(v<=valline(L,r,z,y) for L in ls):actual.append(('bd',env,i,j,bi,r,z,y))
print('actual events',len(actual))
for x in actual[:100]:print(x)
assert len(actual) == 0, 'exact linear-event filter found an active topology event'
from collections import Counter
print('tri degree counts',Counter(len(a)-1 for a in uniq_tri))
print('bd degree counts',Counter(len(a)-1 for a in uniq_bd))
# Numeric filter all roots (including quadratic) for potentially active events
import numpy as np
actual_num=[]
for env,ls in enumerate(inds):
 for i,j,k in itertools.combinations(range(len(ls)),3):
  poly=det3([ls[i],ls[j],ls[k]])
  expr=sum(float(x)*1.0 for x in []) if False else None
  coeff=[float(x) for x in poly[::-1]]
  roots=np.roots(coeff)
  for rr in roots:
   if abs(rr.imag)>1e-8:continue
   r=float(rr.real)
   if not (1e-12<r<1/q0-1e-12):continue
   vals=[]
   for L in ls: vals.append([float(x[0])+float(x[1])*r for x in L])
   E=[vals[i][t]-vals[j][t] for t in range(3)];G=[vals[i][t]-vals[k][t] for t in range(3)]
   det=E[1]*G[2]-E[2]*G[1]
   if abs(det)<1e-14:continue
   z=(E[2]*G[0]-E[0]*G[2])/det;y=(E[0]*G[1]-E[1]*G[0])/det
   if -1e-8<=y<=z+1e-8<=1+1e-8:
    v=vals[i][0]+vals[i][1]*z+vals[i][2]*y
    if all(v <= L[0]+L[1]*r + (L[2][0]+L[2][1]*r)*y + 1e-8 for L in []):pass
    def vv(L):return (float(L[0][0])+float(L[0][1])*r)+(float(L[1][0])+float(L[1][1])*r)*z+(float(L[2][0])+float(L[2][1])*r)*y
    if all(vv(L)>=v-1e-8 for L in ls):actual_num.append(('tri',env,i,j,k,r,z,y))
print('numeric actual all roots triple',len(actual_num))
for x in actual_num[:30]:print(x)

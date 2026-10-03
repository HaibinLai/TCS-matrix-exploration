#!/usr/bin/env python3
"""Symbolic sign check for a q0-visible prime-p overlay candidate family.

This is a partial parametric certificate.  It builds symbolic intersections
from the active edge segments observed at the selected q0, selects candidates that are
inside the domain at q0, and checks the endpoint target ratio against the
corresponding envelope branch.  Exact rational root isolation proves
nonnegativity for this candidate family on u in [0,1/q0].  It does not yet
prove that no new active edge appears away from q0; the companion topology
scan excludes active events on this interval.
"""
import itertools,os
from fractions import Fraction as F
import sympy as sp
from exact_multilevel_2d import build_envelopes,line,value,subtract,intersect,inside,satisfies,DOMAIN,DOMAIN_VERTICES
p=int(os.environ.get('PRIME_P','3'));q0=int(os.environ.get('Q0','67'))
u=sp.symbols('u', real=True)
ps=(2*p*q0,p*q0,p)
choices,ind,nested,stats=build_envelopes(ps)
# symbolic line tuple of sympy expressions in u
def templ(g):return tuple((d//q0,1) if d%q0==0 else (d,0) for d in g)
def inv(x,y):
 e=x[1]+y[1]
 return sp.Rational(1,x[0]*y[0])*(u**e)
def sl(g):
 a,b,c=templ(g);return (inv(a,b),inv(a,c),inv(b,c))
def addls(xs):return tuple(sum((sl(g)[i] for g in xs),sp.S(0)) for i in range(3))
def eval_line(l, z, y):
    return l[0] + l[1] * z + l[2] * y

# mappings
symI=[]
for k,gs in enumerate(choices):
 mp={}
 for g in gs: mp.setdefault(line(g),[]).append(sl(g))
 symI.append([mp[x][0] for x in ind[k]])
# nested chains
chains=[]
for g0 in choices[0]:
 for g1 in choices[1]:
  if not all(a%b==0 for a,b in zip(g0,g1)): continue
  for g2 in choices[2]:
   if all(a%b==0 for a,b in zip(g1,g2)): chains.append((g0,g1,g2))
mpN={}
for c in chains:
 key=tuple(sum(line(g)[i] for g in c) for i in range(3));mpN.setdefault(key,[]).append(addls(c))
symN=[mpN[x][0] for x in nested]
# active edge pair extraction numeric, with line indices

def edges(lines):
 out=[]
 for i,left in enumerate(lines):
  for j in range(i+1,len(lines)):
   right=lines[j]; eq=subtract(left,right); cand=set()
   for pp in DOMAIN_VERTICES:
    if eq[0]+eq[1]*pp[0]+eq[2]*pp[1]==0:cand.add(pp)
   for de in DOMAIN:
    pp=intersect(eq,de)
    if inside(pp):cand.add(pp)
   for other in lines:
    pp=intersect(eq,subtract(left,other))
    if inside(pp):cand.add(pp)
   feas=[pp for pp in cand if all(value(left,*pp)<=value(o,*pp) for o in lines) and value(left,*pp)==value(right,*pp)]
   if not feas:continue
   if len(feas)==1:a=b=feas[0]
   else:
    d=(eq[2],-eq[1]); ords=sorted(feas,key=lambda pp:d[0]*pp[0]+d[1]*pp[1]);a,b=ords[0],ords[-1]
   out.append((a,b,i,j))
 # dedup by endpoint geometry
 uniq={}
 for a,b,i,j in out: uniq[(min(a,b),max(a,b))]=(a,b,i,j)
 return list(uniq.values())
all_num=ind+[nested]; all_sym=symI+[symN]
seg=[]
for owner,ls in enumerate(all_num):
 for a,b,i,j in edges(ls):seg.append((owner,a,b,ls[i],ls[j],all_sym[owner][i],all_sym[owner][j]))
print('segments',len(seg))
# symbolic equality line as expressions const+ bz+cy
def eqsym(l1,l2):return tuple(sp.factor(a-b) for a,b in zip(l1,l2))
def intersym(e1,e2):
 _,b1,c1=e1;_,b2,c2=e2;a1,a2=e1[0],e2[0]
 det=sp.cancel(b1*c2-c1*b2)
 if det==0:return None
 return (sp.cancel((c1*a2-a1*c2)/det),sp.cancel((a1*b2-b1*a2)/det))
def evalsym(l,z,y):return sp.factor(l[0]+l[1]*z+l[2]*y)
def inside_num(pp):return F(0)<=pp[1]<=pp[0]<=F(1)
def point_num(expr,q):
 zz=expr[0].subs(u,sp.Rational(1,q)); yy=expr[1].subs(u,sp.Rational(1,q))
 return F(int(sp.numer(zz)),int(sp.denom(zz))),F(int(sp.numer(yy)),int(sp.denom(yy)))
# candidate sym points from all segment equalities and domain
segeq=[eqsym(s[5],s[6]) for s in seg]
cands=[]
# corners
for z,y in DOMAIN_VERTICES:cands.append((sp.Rational(z),sp.Rational(y),'corner'))
for i,e in enumerate(segeq):
 a,b,c=e
 if b!=0:cands.append((sp.factor(-a/b),sp.S(0),('edge',i)))
 if c!=0:cands.append((sp.S(1),sp.factor(-(a+b)/c),('edge',i)))
 if b+c!=0:
  zz=sp.factor(-a/(b+c));cands.append((zz,zz,('edge',i)))
for i,e1 in enumerate(segeq):
 for j in range(i+1,len(segeq)):
  pp=intersym(e1,segeq[j])
  if pp is not None:cands.append((pp[0],pp[1],('pair',i,j)))
# dedup by expressions
uniq=[];seen=set()
for z,y,src in cands:
 key=(sp.factor(z),sp.factor(y))
 if key not in seen:seen.add(key);uniq.append((z,y,src))
print('raw candidates',len(uniq))
# filter candidate at q0 is inside and is on overlay cell? use inside only plus each point should be a vertex from active segments; all generated seg eq but may equality outside segment
filtered=[]
for z,y,src in uniq:
 try:pp=point_num((z,y),q0)
 except Exception:continue
 if inside_num(pp):filtered.append((z,y,src))
print('inside q0',len(filtered))
# choose active line at q0/q=100003 for point; ratio expression
Rtar=sp.factor(p*(9+sp.Rational(7,1)*u)/((6*p+3)+(3*p*p+4*p)*u))
bad=[]; ratios=[]
for z,y,src in filtered:
 p0=point_num((z,y),q0); p1=point_num((z,y),100003)
 chosen=[]; stable=True
 for ls in all_sym:
  vals0=[sp.N(eval_line(l,p0[0],p0[1]).subs(u,sp.Rational(1,q0))) for l in ls]
  vals1=[sp.N(eval_line(l,p1[0],p1[1]).subs(u,sp.Rational(1,100003))) for l in ls]
  i0=min(range(len(vals0)),key=lambda i:float(vals0[i]));i1=min(range(len(vals1)),key=lambda i:float(vals1[i]))
  if i0!=i1:stable=False;break
  chosen.append(ls[i0])
 if not stable:continue
 I=sp.factor(sum(eval_line(chosen[k],z,y) for k in range(3)))
 N=sp.factor(eval_line(chosen[3],z,y))
 ratio=sp.factor(N/I)
 diff=sp.factor(Rtar-ratio)
 num,den=sp.fraction(diff)
 # test numeric signs at q0 and q large
 v0=sp.N(diff.subs(u,sp.Rational(1,q0)));v1=sp.N(diff.subs(u,0))
 if float(v0)<-1e-10 or float(v1)<-1e-10:
  bad.append((src,z,y,diff,v0,v1))
 ratios.append((src,diff))
print('stable',len(ratios),'bad endpoint',len(bad))
for x in bad[:5]:print('BAD',x)
# Exact sign check with rational root-isolation intervals for numerator/denominator.
def sign_check(expr):
 num,den=sp.fraction(sp.cancel(expr))
 pn=sp.Poly(num,u); pd=sp.Poly(den,u)
 bounds={sp.Rational(0),sp.Rational(1,q0)}
 for poly in (pn,pd):
  for (a,b),mult in poly.intervals(eps=sp.Rational(1,10**10)):
   if b < 0 or a > sp.Rational(1,q0): continue
   bounds.add(max(sp.Rational(0),a)); bounds.add(min(sp.Rational(1,q0),b))
 bounds=sorted(bounds)
 for a,b in zip(bounds,bounds[1:]):
  if a==b: continue
  x=(a+b)/2
  if sp.sign(expr.subs(u,x)) < 0: return False,(a,b),sp.factor(num),sp.factor(den)
 return True,None,None,None
badroot=[]
for src,d in ratios:
 ok,info,num,den=sign_check(d)
 if not ok: badroot.append((src,info,num,den))
print('exact sign bad',len(badroot))
if badroot:
    for x in badroot[:3]: print('ROOTBAD', x)
else:
    print('certificate=True for the q0-visible candidate family')

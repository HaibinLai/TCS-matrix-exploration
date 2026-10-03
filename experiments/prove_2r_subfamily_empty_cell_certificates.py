from itertools import product, combinations
from fractions import Fraction as F
import sympy as sp, sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from prove_2r_subfamily_eight_chain_cells import profile_levels, chains, vertices, full_dimensional
from exact_multilevel_2d import DOMAIN,subtract
r=sp.symbols('r'); q=4*r+3; D=4*r*q
# symbolic fixed profile lines
levels_g=[((q,r,4),(q,2*r,2),(q,4*r,1),(2*q,r,2),(2*q,2*r,1),(4*q,r,1),(r*q,2,2),(r*q,4,1),(2*r*q,2,1),(4*r*q,1,1)),((q,r,2),(q,2*r,1),(2*q,r,1),(r*q,2,1),(2*r*q,1,1)),((r,2,1),(2*r,1,1))]
def gridline(g):
 a,b,c=g; return tuple(sp.cancel(D/x) for x in (a*b,a*c,b*c))
Slevels=[[gridline(g) for g in gs] for gs in levels_g]
Schains=[tuple(sp.cancel(D*x) for x in l) for l in [
(1/(r*q)+1/(2*r),sp.Rational(5,2)/r,sp.Rational(3,4)/q+sp.Rational(1,2)),(1/r+sp.Rational(3,2)/(r*q),sp.Rational(5,4)/r,1/q+sp.Rational(1,2)),(1/(r*q)+1/(2*r),sp.Rational(5,4)/r,1+sp.Rational(3,2)/q),(1/(2*r)+sp.Rational(3,4)/(r*q),sp.Rational(5,2)/r,1/q+sp.Rational(1,2)),(sp.Rational(3,4)/(r*q)+1/(2*r),sp.Rational(3,4)/(r*q)+1/(2*r),3),(1/(r*q)+1/(2*r),sp.Rational(3,4)/(r*q)+1/(2*r),sp.Rational(5,2)),(sp.Rational(3,2)/(r*q)+1/r,1/(r*q)+1/(2*r),sp.Rational(5,4)),(1/(r*q)+1/(2*r),sp.Rational(3,2)/(r*q)+1/r,sp.Rational(5,4))]]
Slevels=[[tuple(sp.expand(x) for x in l) for l in ls] for ls in Slevels]; Schains=[[tuple(sp.expand(x) for x in l) for l in Schains]][0]

def det2(n1,n2):return n1[0]*n2[1]-n1[1]*n2[0]
def coeff_sign(expr):
 p=sp.Poly(sp.expand(expr),r)
 if p.is_zero:return 0
 a=sp.symbols('a'); ps=sp.Poly(sp.expand(p.as_expr().subs(r,21+a)),a); cc=ps.all_coeffs()
 if all(x>=0 for x in cc):return 1
 if all(x<=0 for x in cc):return -1
 # exact root fallback
 try:
  if p.count_roots(21,sp.oo)==0:
   val=p.eval(21)
   return 1 if val>0 else -1 if val<0 else 0
 except: pass
 return None

def numeric_constraints(owners,ci,r0=21):
 lv=profile_levels(r0,4*r0+3); cs=chains(r0,4*r0+3)
 cons=list(DOMAIN); labels=['D0','D1','D2']
 for k,o in enumerate(owners):
  for j,other in enumerate(lv[k]):
   if other!=o: cons.append(subtract(o,other));labels.append(f'L{k}_{j}')
 for j,other in enumerate(cs):
  if j!=ci: cons.append(subtract(cs[ci],other));labels.append(f'C{j}')
 return cons,labels

def symbolic_constraints(owners,ci):
 cons=[tuple(sp.Integer(x) for x in g) for g in DOMAIN]; labels=['D0','D1','D2']
 for k,o in enumerate(owners):
  for j,other in enumerate(Slevels[k]):
   if other!=Slevels[k][o]: cons.append(tuple(sp.expand(x-y) for x,y in zip(Slevels[k][o],other)));labels.append(f'L{k}_{j}')
 for j,other in enumerate(Schains):
  if j!=ci: cons.append(tuple(sp.expand(x-y) for x,y in zip(Schains[ci],other)));labels.append(f'C{j}')
 return cons,labels

def stable_triple(scons,idx):
 # Return stable symbolic Farkas certificate for a triple or None.
 for inds in [idx]:
  es=[scons[i] for i in inds]; ns=[(e[1],e[2]) for e in es]
  lam=[det2(ns[1],ns[2]),det2(ns[2],ns[0]),det2(ns[0],ns[1])]
  # orient using r=21 numeric signs
  vals=[sp.N(x.subs(r,21)) for x in lam]
  if all(v<=0 for v in vals): lam=[-x for x in lam]; vals=[-v for v in vals]
  if not all(v>=-1e-12 for v in vals) or all(v<1e-12 for v in vals): continue
  signs=[coeff_sign(x) for x in lam]
  if any(s not in (1,0) for s in signs): continue
  const=sp.expand(sum(lam[t]*es[t][0] for t in range(3)))
  sc=coeff_sign(const)
  if sc==1 and any(x!=0 for x in lam): return (inds,lam,const)
 return None

def find_cert(cons,scons):
 # numeric Farkas triple search; then stable symbolic check
 for idx in combinations(range(len(cons)),3):
  es=[cons[i] for i in idx]; ns=[(e[1],e[2]) for e in es]
  lam=[det2(ns[1],ns[2]),det2(ns[2],ns[0]),det2(ns[0],ns[1])]
  if all(x<=0 for x in lam):lam=[-x for x in lam]
  if not all(x>=0 for x in lam) or all(x==0 for x in lam):continue
  if sum(lam[t]*es[t][0] for t in range(3))<=0:continue
  stable=stable_triple(scons,idx)
  if stable:return stable
 return None

r0=21; levels=profile_levels(r0,87); cs=chains(r0,87)
allc=fullc=empty=point=stable=0; failed=[]
for owners in product(*levels):
 for ci in range(8):
  ncons, nlabs=numeric_constraints(owners,ci); vs=vertices(ncons)
  if full_dimensional(vs):fullc+=1;continue
  if vs:point+=1;continue
  empty+=1
  scons,slabs=symbolic_constraints(tuple(levels[k].index(owners[k]) for k in range(3)),ci)
  cert=find_cert(ncons,scons)
  if cert:stable+=1
  elif len(failed)<10: failed.append((tuple(levels[k].index(owners[k]) for k in range(3)),ci))
print('full empty point stable failed',fullc,empty,point,stable,len(failed))
print('failed',failed)

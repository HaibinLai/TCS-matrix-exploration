#!/usr/bin/env python3
"""Exact active linear topology-event scan for p=3, q0=29."""
import itertools,sys
from fractions import Fraction as F
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
import check_p3_quadratic_sturm as q
from exact_overlay_2d import active_edge_segments
u0=F(1,q.q0)
vertices=[(F(0),F(0)),(F(1),F(0)),(F(1),F(1))]
domain=[(F(0),F(0),F(1)),(F(0),F(-1),F(1)),(F(-1),F(1),F(0))]
def trim(a):
 a=list(a)
 while a and not a[-1]:a.pop()
 return tuple(a or [F(0)])
def diff(a,b):return tuple((x[0]-y[0],x[1]-y[1]) for x,y in zip(a,b))
def evalc(L,u):return tuple(a+b*u for a,b in L)
def value(L,u,z,y):
 a,b,c=evalc(L,u);return a+b*z+c*y
def root(poly):return None if len(poly)!=2 or poly[1]==0 else -poly[0]/poly[1]
def active_tie(lines,i,j,u,z,y):
 v=value(lines[i],u,z,y)
 return v==value(lines[j],u,z,y) and all(v<=value(L,u,z,y) for L in lines)
vertex=[];parallel=[];identity=[];triple=[]
for env,lines in enumerate(q.inds):
 for i,j in itertools.combinations(range(len(lines)),2):
  e=diff(lines[i],lines[j])
  for z,y in vertices:
   r=root(trim((e[0][0]+e[1][0]*z+e[2][0]*y,e[0][1]+e[1][1]*z+e[2][1]*y)))
   if r is not None and F(0)<r<=u0 and active_tie(lines,i,j,r,z,y):vertex.append((env,i,j,(z,y),r))
  for bi,d in enumerate(domain):
   r=root(trim((e[1][0]*d[2]-e[2][0]*d[1],e[1][1]*d[2]-e[2][1]*d[1])))
   if r is None or not F(0)<r<=u0:continue
   nums=[evalc(L,r) for L in lines];pairs=set()
   for _,_,eq in active_edge_segments(nums):
    for a,b in itertools.combinations(range(len(lines)),2):
     dd=tuple(nums[a][k]-nums[b][k] for k in range(3))
     if dd==eq or tuple(-x for x in dd)==eq:pairs.add((a,b))
   parallel.append((env,i,j,bi,r,(i,j) in pairs))
  roots=[]
  for c in e:
   rr=root(trim(c))
   if rr is not None:roots.append(rr)
  for r in set(roots):
   if F(0)<r<=u0 and all(a+b*r==0 for a,b in e):identity.append((env,i,j,r))
 for i,j,k in itertools.combinations(range(len(lines)),3):
  # determinants are at most linear for affine coefficient vectors
  a,b,c=lines[i],lines[j],lines[k]
  def det_at(u):
   M=[evalc(x,u) for x in (a,b,c)]
   return (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
    -M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
    +M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0]))
  v0=det_at(F(0));v1=det_at(F(1));r=None
  if v1!=v0:r=-v0/(v1-v0)
  if r is None or not F(0)<r<=u0:continue
  M=[evalc(x,r) for x in (a,b,c)];e=tuple(x-y for x,y in zip(M[0],M[1]));g=tuple(x-y for x,y in zip(M[0],M[2]));det=e[1]*g[2]-e[2]*g[1]
  if det==0:continue
  z=(e[2]*g[0]-e[0]*g[2])/det;y=(e[0]*g[1]-e[1]*g[0])/det
  if not F(0)<=y<=z<=F(1):continue
  common=value(lines[i],r,z,y)
  if all(common<=value(L,r,z,y) for L in lines):triple.append((env,i,j,k,r,z,y))
print('active_counts',tuple(map(len,q.inds)))
print('active_vertex_events',len(vertex),vertex)
print('parallel_roots',len(parallel),'active_pair_parallel_roots',sum(x[-1] for x in parallel))
print('positive_u_identity_roots',len(identity),identity)
print('active_linear_triple_events',len(triple),triple)
assert not vertex and not identity and not triple and not any(x[-1] for x in parallel)
print(f'certificate=True: no active linear topology event for 0<u<=1/{q.q0}')

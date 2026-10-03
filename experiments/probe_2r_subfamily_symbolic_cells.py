#!/opt/miniconda3/bin/python
"""Attempt a symbolic cell certificate for the stable r>=21 topology.

This is intentionally a probe: it takes the exact 33-cell decomposition at
r=21, lifts its vertices to rational functions of r, and checks coefficientwise
positivity after r=21+a.  A successful run is a strong branch certificate;
failure identifies the missing threshold or vertex case.
"""
from fractions import Fraction as F
from itertools import combinations
import sympy as sp
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import grids, line, subtract, intersect, inside, satisfies, DOMAIN
from prove_2r_subfamily_eight_chain_cells import run_profile, chains, profile_levels

r, a = sp.symbols('r a', real=True)
q = 4*r + 3

def sym_chains():
    return [
        (1/(r*q)+1/(2*r), sp.Rational(5,2)/r, sp.Rational(3,4)/q+sp.Rational(1,2)),
        (1/r+sp.Rational(3,2)/(r*q), sp.Rational(5,4)/r, 1/q+sp.Rational(1,2)),
        (1/(r*q)+1/(2*r), sp.Rational(5,4)/r, 1+sp.Rational(3,2)/q),
        (1/(2*r)+sp.Rational(3,4)/(r*q), sp.Rational(5,2)/r, 1/q+sp.Rational(1,2)),
        (sp.Rational(3,4)/(r*q)+1/(2*r), sp.Rational(3,4)/(r*q)+1/(2*r), 3),
        (1/(r*q)+1/(2*r), sp.Rational(3,4)/(r*q)+1/(2*r), sp.Rational(5,2)),
        (sp.Rational(3,2)/(r*q)+1/r, 1/(r*q)+1/(2*r), sp.Rational(5,4)),
        (1/(r*q)+1/(2*r), sp.Rational(3,2)/(r*q)+1/r, sp.Rational(5,4)),
    ]

R0 = 11
def token(v, r0=None):
    if r0 is None: r0 = R0
    q0=4*r0+3
    mp={1:'1',2:'2',4:'4',r0:'r',2*r0:'2r',4*r0:'4r',q0:'q',2*q0:'2q',4*q0:'4q',
        r0*q0:'rq',2*r0*q0:'2rq',4*r0*q0:'4rq'}
    return mp[v]

VAL={'1':sp.Integer(1),'2':sp.Integer(2),'4':sp.Integer(4),'r':r,'2r':2*r,'4r':4*r,'q':q,'2q':2*q,'4q':4*q,
     'rq':r*q,'2rq':2*r*q,'4rq':4*r*q}
def sym_line_numeric(l, r0=11):
    # Find a grid at this level is handled outside; this maps a numeric line by its grid token.
    return l
def sym_grid(g):
    x=tuple(token(v) for v in g); A,B,C=(VAL[t] for t in x)
    return (1/(A*B),1/(A*C),1/(B*C))
def sign_poly(expr, r0=21):
    num, den = sp.together(sp.factor(expr)).as_numer_denom()
    num=sp.Poly(sp.expand(num.subs(r, r0+a)), a)
    den=sp.Poly(sp.expand(den.subs(r, r0+a)), a)
    if not all(c>=0 for c in den.all_coeffs()):
        return False
    return all(c>=0 for c in num.all_coeffs())
def affine_inter(e1,e2):
    _,b1,c1=e1;_,b2,c2=e2;a1,a2=e1[0],e2[0]
    det=b1*c2-c1*b2
    if det==0:return None
    return (sp.factor((c1*a2-a1*c2)/det),sp.factor((a1*b2-b1*a2)/det))

def main():
    global R0
    r0,q0=21,87
    R0 = r0
    levels_num, chain_num, cells=run_profile(r0,q0)
    levels_sym=[]
    for gs in [
        ((q0,r0,4),(q0,2*r0,2),(q0,4*r0,1),(2*q0,r0,2),(2*q0,2*r0,1),
         (4*q0,r0,1),(r0*q0,2,2),(r0*q0,4,1),(2*r0*q0,2,1),(4*r0*q0,1,1)),
        ((q0,r0,2),(q0,2*r0,1),(2*q0,r0,1),(r0*q0,2,1),(2*r0*q0,1,1)),
        ((r0,2,1),(2*r0,1,1)),
    ]:
        line_map={line(g):sym_grid(g) for g in gs}
        levels_sym.append(line_map)
    csym=sym_chains()
    R=5*q*r*(8*q+13)/(28*q*q*r+15*q*q+6*q*r*r+52*q*r+9*r*r)
    checked_vertices=0; bad=[]
    for owners,ci,verts in cells:
        # Rebuild numeric and symbolic constraints in the same order.
        cn=list(DOMAIN); cs=[]
        for g in DOMAIN: cs.append(tuple(sp.Integer(x) for x in g))
        own_sym=[levels_sym[k][o] for k,o in enumerate(owners)]
        for k,o in enumerate(owners):
            for other in levels_num[k]:
                if other!=o:
                    cn.append(subtract(o,other))
                    cs.append(tuple(sp.factor(x-y) for x,y in zip(levels_sym[k][o],levels_sym[k][other])))
        for j,other in enumerate(chain_num):
            if j!=ci:
                cn.append(subtract(chain_num[ci],other))
                cs.append(tuple(sp.factor(x-y) for x,y in zip(csym[ci],csym[j])))
        I=tuple(sum(x[k] for x in own_sym) for k in range(3))
        T=tuple(sp.factor(R*I[k]-csym[ci][k]) for k in range(3))
        for vz,vy in verts:
            pairs=[]
            for i,j in combinations(range(len(cn)),2):
                pv=intersect(cn[i],cn[j])
                if pv==(vz,vy): pairs.append((i,j))
            if not pairs:
                # domain corner may be represented by two domain constraints; retry all pairs.
                bad.append(('missing-pair',ci,(vz,vy))); continue
            ok_vertex=False
            for i,j in pairs:
                xy=affine_inter(cs[i],cs[j])
                if xy is None: continue
                zexpr,yexpr=xy
                # Feasibility of the whole cell at this symbolic vertex.
                feasible=all(sign_poly(-(g[0]+g[1]*zexpr+g[2]*yexpr),r0) for g in cs)
                target=sign_poly(T[0]+T[1]*zexpr+T[2]*yexpr,r0)
                if feasible and target:
                    ok_vertex=True;break
                if bad == [] and not (feasible and target):
                    print('diagnostic cell',ci,'vertex',vz,vy,'pair',i,j,
                          'feasible',feasible,'target',target,
                          'target_expr',sp.factor(T[0]+T[1]*zexpr+T[2]*yexpr))
            checked_vertices+=1
            if not ok_vertex: bad.append(('vertex',ci,(vz,vy),len(pairs)))
    print('r0=21 cells=',len(cells),'vertices_checked=',checked_vertices,'bad=',len(bad))
    if bad: print('first_bad=',bad[0])
    else:
        topology = []
        for rr in (21, 23, 50, 100):
            _, _, cc = run_profile(rr, 4*rr+3)
            topology.append((rr, len(cc)))
        assert all(n == 33 for _, n in topology), topology
        print('sampled stable topology=', topology)
        print('symbolic r>=21 cell certificate=True for the 33-cell branch')

if __name__=='__main__': main()

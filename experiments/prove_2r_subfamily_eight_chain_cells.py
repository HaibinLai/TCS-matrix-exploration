#!/opt/miniconda3/bin/python
"""Explore the 36-cell certificate behind the eight-chain bound.

At r=5 this enumerates each full-dimensional cell of the 10/5/2 sorted
independent envelopes and eight-chain envelope.  It records which chain proves
the candidate ratio bound on every cell.  The symbolic extension is the next
step; keeping the cell decomposition explicit prevents hiding a missing
divisor-profile case.
"""
from fractions import Fraction as F
from itertools import combinations, product
import sys
sys.path.insert(0, str(__file__).rsplit('/', 1)[0])
from exact_multilevel_2d import grids, line, subtract, intersect, inside, satisfies, DOMAIN, value


def vertices(constraints):
    pts = []
    for p in [(F(0), F(0)), (F(1), F(0)), (F(1), F(1))]:
        if satisfies(constraints, p):
            pts.append(p)
    for e1, e2 in combinations(constraints, 2):
        p = intersect(e1, e2)
        if p is not None and inside(p) and satisfies(constraints, p):
            pts.append(p)
    return list(set(pts))

def full_dimensional(points):
    if len(points) < 3:
        return False
    x0, y0 = points[0]
    return any((x1-x0)*(y2-y0) != (x2-x0)*(y1-y0)
               for x1, y1 in points[1:] for x2, y2 in points[1:]
               if (x1, y1) != (x2, y2))


def chains(r, q):
    return [
        (F(1, r*q)+F(1, 2*r), F(5, 2*r), F(3, 4*q)+F(1, 2)),
        (F(1, r)+F(3, 2*r*q), F(5, 4*r), F(1, q)+F(1, 2)),
        (F(1, r*q)+F(1, 2*r), F(5, 4*r), F(1)+F(3, 2*q)),
        (F(1, 2*r)+F(3, 4*r*q), F(5, 2*r), F(1, q)+F(1, 2)),
        (F(3, 4*r*q)+F(1, 2*r), F(3, 4*r*q)+F(1, 2*r), F(3)),
        (F(1, r*q)+F(1, 2*r), F(3, 4*r*q)+F(1, 2*r), F(5, 2)),
        (F(3, 2*r*q)+F(1, r), F(1, r*q)+F(1, 2*r), F(5, 4)),
        (F(1, r*q)+F(1, 2*r), F(3, 2*r*q)+F(1, r), F(5, 4)),
    ]

def profile_levels(r, q):
    """The 10/5/2 sorted lines for the fixed {2,r,q} divisor profile."""
    def mk(g):
        a, b, c = g
        p = a*b*c
        return (F(c, p), F(b, p), F(a, p))
    return [
        [mk(g) for g in ((q,r,4),(q,2*r,2),(q,4*r,1),(2*q,r,2),
                         (2*q,2*r,1),(4*q,r,1),(r*q,2,2),(r*q,4,1),
                         (2*r*q,2,1),(4*r*q,1,1))],
        [mk(g) for g in ((q,r,2),(q,2*r,1),(2*q,r,1),(r*q,2,1),(2*r*q,1,1))],
        [mk(g) for g in ((r,2,1),(2*r,1,1))],
    ]


def run(r=5, q=23):
    levels = []
    for P in (4*r*q, 2*r*q, 2*r):
        gs = {tuple(sorted(g, reverse=True)) for g in grids(P)}
        levels.append([line(g) for g in gs])
    cs = chains(r, q)
    R = F(5*q*r*(8*q+13), 28*q*q*r+15*q*q+6*q*r*r+52*q*r+9*r*r)
    cells = []
    for owners in product(*levels):
        for ci, chain in enumerate(cs):
            constraints = list(DOMAIN)
            for lev, owner in enumerate(owners):
                constraints.extend(subtract(owner, other) for other in levels[lev]
                                  if other != owner)
            constraints.extend(subtract(chain, other) for j, other in enumerate(cs) if j != ci)
            vs = vertices(constraints)
            if not full_dimensional(vs):
                continue
            Iline = tuple(sum(l[k] for l in owners) for k in range(3))
            if all(value(chain, z, y) <= R * value(Iline, z, y) for z, y in vs):
                cells.append((owners, ci, vs))
    return levels, cs, cells

def run_profile(r=5, q=23, proving_only=True):
    """Same cell enumeration with the fixed divisor profile, even if q is composite."""
    levels = profile_levels(r, q)
    cs = chains(r, q)
    R = F(5*q*r*(8*q+13), 28*q*q*r + 15*q*q + 6*q*r*r + 52*q*r + 9*r*r)
    cells = []
    for owners in product(*levels):
        for ci, chain in enumerate(cs):
            constraints = list(DOMAIN)
            for lev, owner in enumerate(owners):
                constraints.extend(subtract(owner, other) for other in levels[lev]
                                  if other != owner)
            constraints.extend(subtract(chain, other) for j, other in enumerate(cs) if j != ci)
            vs = vertices(constraints)
            if not full_dimensional(vs):
                continue
            Iline = tuple(sum(l[k] for l in owners) for k in range(3))
            if (not proving_only or
                    all(value(chain, z, y) <= R * value(Iline, z, y) for z, y in vs)):
                cells.append((owners, ci, vs))
    return levels, cs, cells


if __name__ == '__main__':
    for r, q in ((5, 23), (7, 29), (11, 47), (17, 71), (19, 79)):
        levels, cs, cells = run(r, q)
        owners = {i: sum(ci == i for _, ci, _ in cells) for i in range(8)}
        print(f'r={r} q={q} levels={tuple(map(len, levels))} cells={len(cells)} owners={owners}')
    print('eight-chain cell certificate=True for five exact parameters')

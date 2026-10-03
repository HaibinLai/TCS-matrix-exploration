#!/usr/bin/env python3
"""Find exact boundary counterexamples to the prime-family formula for composite p."""
from fractions import Fraction as F
from scan_multilevel_boundary_hull import exact_boundary

def prime(n):
    return n>1 and all(n%d for d in range(2,int(n**0.5)+1))

rows=[]
for p in range(3,51):
    if prime(p): continue
    for q in range(3,501):
        if q<=2*p or not prime(q): continue
        (ratio,t),counts,active,nactive=exact_boundary((2*p*q,p*q,p))
        candidate=F(p*(9*q+7),(6*p+3)*q+3*p*p+4*p)
        if ratio>candidate:
            rows.append((ratio-candidate,ratio,candidate,p,q,t,counts,active,nactive))
rows.sort(reverse=True)
print(f'counterexamples={len(rows)} composite p<=50 prime q<=500')
for gap,ratio,candidate,p,q,t,counts,active,nactive in rows[:20]:
    print(f'p={p} q={q} boundary_ratio={ratio} candidate={candidate} gap={gap} t={t} grids={counts} active={active} nested={nactive}')

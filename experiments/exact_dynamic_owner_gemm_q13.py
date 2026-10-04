#!/usr/bin/env python3
"""Bounded exact search for dynamic-owner 2x2x2 GEMM, M=3.

Model: two symmetric owners (local capacity 3), one root copy of A/B, optional
one-slot shared B cache (G=1), no recomputation. Any unfinished product can be
assigned to either owner. A/B root arrivals and shared-B arrivals cost one;
shared-to-local promotion/eviction of A/B cost zero. C first initialization is
free. A dirty C must be stored at root before eviction or explicit migration
(cost one); root-to-owner C reload costs one. Final C values must be current at
root. We canonicalize owner labels, cap the search at a target communication
budget, and use 0/1 BFS. This is an exact decision search for the stated finite
model; it is not the general dynamic-owner theorem.
"""
from collections import deque
import heapq

A = {(i, k): i * 2 + k for i in range(2) for k in range(2)}
B = {(k, j): 4 + k * 2 + j for k in range(2) for j in range(2)}
C = {(i, j): 8 + i * 2 + j for i in range(2) for j in range(2)}
PRODUCTS = []
for i in range(2):
    for k in range(2):
        for j in range(2):
            PRODUCTS.append((A[i, k], B[k, j], C[i, j]))

A_IDS = tuple(range(4))
B_IDS = tuple(range(4, 8))
C_IDS = tuple(range(8, 12))
ALL_IDS = tuple(range(12))

def bit(x):
    return 1 << x

def pc(x):
    return bin(x).count("1")

def canon(local0, local1):
    return (local0, local1) if local0 <= local1 else (local1, local0)

def init_c(done):
    out = 0
    for p, (_, _, c) in enumerate(PRODUCTS):
        if done & bit(p): out |= bit(c - 8)
    return out

def local_c_mask(local):
    return sum(bit(c - 8) for c in C_IDS if local & bit(c))

def c_local_any(local0, local1, c):
    return (local0 | local1) & bit(c)

def insert_options(mask, item, M, root_current):
    b = bit(item)
    if mask & b:
        yield mask, 0, root_current, None
        return
    if pc(mask) < M:
        yield mask | b, 0, root_current, None
        return
    for ev in ALL_IDS:
        if not (mask & bit(ev)):
            continue
        cost = 0
        root = root_current
        if ev in C_IDS:
            idx = ev - 8
            if not (root & bit(idx)):
                cost = 1
                root |= bit(idx)
        yield ((mask ^ bit(ev)) | b), cost, root, ev

def heuristic(state):
    """Admissible source/terminal movement bound for A* pruning."""
    done,l0,l1,shared,root=state
    locals_union=l0|l1
    h=0
    # Every missing A used by a remaining product needs at least one root arrival.
    needed_a=0; needed_b=0; needed_c=0
    for p,(a,b,c) in enumerate(PRODUCTS):
        if not(done&bit(p)):
            needed_a|=bit(a); needed_b|=bit(b); needed_c|=bit(c-8)
    h += pc(needed_a & ~locals_union)
    # A B entry may be available in either local cache or shared cache.
    local_b=((l0|l1)&sum(bit(x) for x in B_IDS))
    shared_b=shared
    h += pc(needed_b & ~(local_b|shared_b))
    # Each final C not current at root needs at least one movement. An initialized
    # C absent from local but current at root also needs one reload to do more work.
    for ci in range(4):
        c=8+ci; cb=bit(c); pending=needed_c&bit(ci)
        if not(root&bit(ci)):
            h += 1
        elif pending and not((l0|l1)&cb):
            h += 1
    return h

def exact_q13(target=13, G=1, progress_every=500000):
    # state=(done,local0,local1,shared_B_mask,root_current_C_mask)
    start=(0,0,0,0,0)
    d={start:0}; parent={}; q=[(heuristic(start),0,start)]; expanded=0
    while q:
        _,queued_cost,state=heapq.heappop(q)
        cost=d[state]
        if queued_cost != cost:
            continue
        expanded+=1
        if expanded % progress_every == 0:
            print('expanded',expanded,'states',len(d),'cost',cost,flush=True)
        if cost > target:
            continue
        done,l0,l1,shared,root=state
        if done == (1<<len(PRODUCTS))-1:
            # Final stores; current root entries need no transfer.
            final = cost + (4-pc(root))
            if final <= target:
                return final, state, d, parent, expanded
            continue
        locals_=(l0,l1); initialized=init_c(done)
        # Product computations, zero cost. C must be local; first use can
        # allocate it for free, initialized C requires explicit reload.
        for p,(a,b,c) in enumerate(PRODUCTS):
            if done & bit(p): continue
            for owner in (0,1):
                local=locals_[owner]
                if not (local & bit(a) and local & bit(b)): continue
                cb=bit(c); ci=c-8
                if local & cb:
                    nl=local; nr=root & ~bit(ci)
                    ns_done=done|bit(p)
                    nxt0,nxt1=canon(nl if owner==0 else l0, nl if owner==1 else l1)
                    ns=(ns_done,nxt0,nxt1,shared,nr)
                    if cost < d.get(ns,10**9):
                        d[ns]=cost; parent[ns]=(state,('compute',p,owner)); heapq.heappush(q,(cost+heuristic(ns),cost,ns))
                elif not (initialized & bit(ci)) and not c_local_any(l0,l1,c):
                    for nl,ec,nr,ev in insert_options(local,c,3,root):
                        a0,a1=(nl,l1) if owner==0 else (l0,nl)
                        a0,a1=canon(a0,a1)
                        ns=(done|bit(p),a0,a1,shared,nr&~bit(ci))
                        nc=cost+ec
                        if nc < d.get(ns,10**9) and nc<=target:
                            d[ns]=nc;parent[ns]=(state,('compute-first',p,owner,ev,ec));
                            heapq.heappush(q,(nc+heuristic(ns),nc,ns))
        # Direct A/B root arrivals to either owner.
        for owner in (0,1):
            local=locals_[owner]
            for item in A_IDS+B_IDS:
                if local & bit(item): continue
                for nl,ec,nr,ev in insert_options(local,item,3,root):
                    a0,a1=(nl,l1) if owner==0 else (l0,nl);a0,a1=canon(a0,a1)
                    ns=(done,a0,a1,shared,nr);nc=cost+1+ec
                    if nc<d.get(ns,10**9) and nc<=target:
                        d[ns]=nc;parent[ns]=(state,('direct',owner,item,ev,ec));heapq.heappush(q,(nc+heuristic(ns),nc,ns))
        # Shared B arrivals and free promotions.
        if G:
            for item in B_IDS:
                if shared & bit(item): continue
                # G=1; replacing old shared B is free.
                ns=(done,l0,l1,bit(item),root);nc=cost+1
                if nc<d.get(ns,10**9) and nc<=target:
                    d[ns]=nc;parent[ns]=(state,('shared-B',item));heapq.heappush(q,(nc+heuristic(ns),nc,ns))
            for owner in (0,1):
                local=locals_[owner]
                for item in B_IDS:
                    if not(shared&bit(item)) or local&bit(item): continue
                    for nl,ec,nr,ev in insert_options(local,item,3,root):
                        a0,a1=(nl,l1) if owner==0 else (l0,nl);a0,a1=canon(a0,a1)
                        ns=(done,a0,a1,shared,nr);nc=cost+ec
                        if nc<d.get(ns,10**9):
                            d[ns]=nc;parent[ns]=(state,('promote-B',owner,item,ev,ec));
                            heapq.heappush(q,(nc+heuristic(ns),nc,ns))
        # Explicit stores of dirty local C enable migration; local copy remains.
        for owner in (0,1):
            local=locals_[owner]
            for c in C_IDS:
                ci=c-8
                if local&bit(c) and not(root&bit(ci)):
                    ns=(done,l0,l1,shared,root|bit(ci));nc=cost+1
                    if nc<d.get(ns,10**9) and nc<=target:
                        d[ns]=nc;parent[ns]=(state,('store-C',owner,c));heapq.heappush(q,(nc+heuristic(ns),nc,ns))
        # C reload from root; disallow duplicate local C copies.
        for owner in (0,1):
            local=locals_[owner]
            for c in C_IDS:
                ci=c-8; cb=bit(c)
                if local&cb or c_local_any(l0,l1,c) or not(initialized&bit(ci)) or not(root&bit(ci)):
                    continue
                for nl,ec,nr,ev in insert_options(local,c,3,root):
                    a0,a1=(nl,l1) if owner==0 else (l0,nl);a0,a1=canon(a0,a1)
                    ns=(done,a0,a1,shared,nr);nc=cost+1+ec
                    if nc<d.get(ns,10**9) and nc<=target:
                        d[ns]=nc;parent[ns]=(state,('reload-C',owner,c,ev,ec));heapq.heappush(q,(nc+heuristic(ns),nc,ns))
    return None,None,d,parent,expanded

def reconstruct(parent,state):
    out=[]
    while state in parent:
        state,action=parent[state];out.append(action)
    return list(reversed(out))

def run():
    result=exact_q13()
    print('dynamic-owner Q<=13 result',result[0], 'expanded',result[-1], 'states',len(result[2]))
    if result[0] is not None:
        print('witness length',len(reconstruct(result[3],result[1])))

if __name__=='__main__': run()

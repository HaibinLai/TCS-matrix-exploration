from itertools import product

def divisors(n):
    return [d for d in range(1,n+1) if n%d==0]

def grids(P):
    for p1 in divisors(P):
        for p2 in divisors(P//p1):
            yield p1,p2,P//p1//p2

def macro(n1,n2,n3,P,g):
    p1,p2,p3=g
    a,b,c=n1/p1,n2/p2,n3/p3
    return a,b,c,a*b+b*c+a*c

for dims,P in [((4096,4096,4096),64),((1024,256,64),64),((4096,256,16),16)]:
    rows=[]
    for g in grids(P):
        a,b,c,H=macro(*dims,P,g)
        rows.append((H,g,(a,b,c)))
    rows.sort()
    print('\n',dims,'P=',P,'min H=',rows[0])
    for M in [rows[0][0]*2, rows[0][0]*0.75, rows[0][0]*0.25]:
        feasible=[r for r in rows if r[0]<=M]
        print('M2=',M,'feasible=',bool(feasible),'best=',feasible[0] if feasible else None)

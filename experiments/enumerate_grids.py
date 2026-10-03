from math import prod

def divisors(n):
    return [d for d in range(1,n+1) if n%d==0]

def grids(P):
    for p1 in divisors(P):
        for p2 in divisors(P//p1):
            p3=P//p1//p2
            yield p1,p2,p3

def terms(a,b,c,P,g):
    p1,p2,p3=g
    SA=a*b/(p1*p2)
    SB=b*c/(p2*p3)
    SD=a*c/(p1*p3)
    return SA,SB,SD,SA+SB+SD,max(SA,SB,SD)

for dims in [(1024,1024,1024),(1024,256,64),(4096,1024,256)]:
    a,b,c=dims; P=64
    rows=[]
    for g in grids(P):
        t=terms(a,b,c,P,g)
        rows.append((t[3],t[4],g,t[:3]))
    print('\nDims',dims,'P',P)
    print('min sum:',sorted(rows)[:5])
    print('min max:',sorted(rows,key=lambda x:(x[1],x[0]))[:5])

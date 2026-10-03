import math


def q_mi(N, P):
    return 3 * N**2 / P**(2/3) - 3 * N**2 / P


def q_md(N, P, M):
    return 2 * N**3 / (P * math.sqrt(M))

print('P,N,M, Q_MI, Q_MD, dominant')
N = 4096
for P in [1, 8, 64, 512, 4096, 32768]:
    M_cross = 4/9 * N**2 / P**(2/3)
    for factor in [0.25, 1.0, 4.0]:
        M = factor * M_cross
        mi = q_mi(N, P)
        md = q_md(N, P, M)
        print(f'{P:5d} {N:5d} {M:12.2f} {mi:12.2f} {md:12.2f} {"MD" if md > mi else "MI"}')

print('\n3D memory terms for square N x N GEMM')
for P in [8, 64, 512, 4096]:
    p = P ** (1/3)
    # balanced grid: A, B, D each N^2 / P^(2/3)
    term = N**2 / P**(2/3)
    print(f'P={P:5d}, p~{p:7.3f}, A=B=D={term:12.2f}, sum={3*term:12.2f}')

import math

N = 4096
P_levels = [8, 8, 8]       # cores/node, nodes/drawer, drawers
M1 = 32 * 1024             # words per core

Pstar = []
prod = 1
for p in reversed(P_levels):
    prod *= p
    Pstar.append(prod)
Pstar.reverse()

M = []
prod = M1
for i in range(len(P_levels)):
    M.append(prod)
    if i + 1 < len(P_levels):
        prod *= P_levels[i]

print('level P_i^* M_i Q_MD Q_MI dominant')
for i, (ps, mi) in enumerate(zip(Pstar, M), 1):
    qmd = 2*N**3/(ps*math.sqrt(mi))
    qmi = 3*N**2/(ps**(2/3))
    print(i, ps, mi, f'{qmd:.1f}', f'{qmi:.1f}', 'MD' if qmd > qmi else 'MI')

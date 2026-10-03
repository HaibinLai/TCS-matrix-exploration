"""Corrected restricted panel model.

If the slow tier can retain the full partial C tile, panelization does not
require a reduction after every k-panel. It repeats A/B panel movement but
reduces C once at the end.
"""
for a in [256, 1024, 4096]:
    print('a=', a)
    for frac in [3.0, 2.0, 1.5, 1.25]:
        M2 = frac*a*a
        # Largest k-panel that fits with a persistent a x a partial C.
        t = min(a, max(0.0, (M2-a*a)/(2*a)))
        if t == 0:
            print(f' M2/a^2={frac:5.3f} no complete partial-C tile')
            continue
        # A/B gather over all panels plus one final C reduction.
        q_network = 2*a*a + a*a
        # Leading local fast-tier traffic over all panels.
        M1 = a*a/4
        q_local = 2*a**3/(M1**0.5)
        print(f' M2/a^2={frac:5.3f} t/a={t/a:7.4f} '
              f'Qnetwork/a^2={q_network/a**2:5.1f} '
              f'Qlocal/(a^3/sqrt(M1))={q_local/(a**3/(M1**0.5)):5.1f}')

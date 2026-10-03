#!/usr/bin/env python3
"""Symbolic corner proof for reducing 27 nested chains to 16 templates.

Forms are represented in the basis (1, r, t, v), where r=1/p, t=1/q,
v=r*t.  For each of the 11 non-template chains, the script computes the
three vertex differences against the listed template dominator and verifies
the elementary bounds valid for 0<t<r<=1/3.
"""
from fractions import Fraction


def add(*forms):
    result = {}
    for form in forms:
        for key, value in form.items():
            result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def neg(form):
    return {key: -value for key, value in form.items()}


def sub(left, right):
    return add(left, neg(right))


def factor(name):
    table = {
        1: (1, 0, 0),
        2: (2, 0, 0),
        "p": (1, 1, 0),
        "q": (1, 0, 1),
        "2p": (2, 1, 0),
        "2q": (2, 0, 1),
        "pq": (1, 1, 1),
        "2pq": (2, 1, 1),
    }
    return table[name]


def reciprocal_product(*names):
    coefficient = Fraction(1)
    p_power = q_power = 0
    for name in names:
        current, p_exp, q_exp = factor(name)
        coefficient *= current
        p_power += p_exp
        q_power += q_exp
    return {(p_power, q_power): Fraction(1, coefficient)}


def line(grid):
    a, b, c = grid
    return reciprocal_product(a, b), reciprocal_product(a, c), reciprocal_product(b, c)


def chain_line(chain):
    return tuple(add(*(line(grid)[index] for grid in chain)) for index in range(3))


def corner_forms(form):
    constant = form.get((0, 0), Fraction(0))
    r = form.get((1, 0), Fraction(0))
    t = form.get((0, 1), Fraction(0))
    v = form.get((1, 1), Fraction(0))
    return (form, add({(0, 0): constant}, {(1, 0): r}), add({(0, 0): constant}, {(1, 0): r}, {(0, 1): t}, {(1, 1): v}))


def form_string(form):
    names = {(0, 0): "1", (1, 0): "r", (0, 1): "t", (1, 1): "v"}
    terms = []
    for key, coefficient in sorted(form.items()):
        sign = "+" if coefficient > 0 else "-"
        terms.append(f"{sign}{abs(coefficient)}*{names[key]}")
    return " ".join(terms).lstrip("+") or "0"


def upper_bound(form):
    """Return a rigorous simple upper bound under 0<t<r<=1/3, v=rt."""
    c0 = form.get((0, 0), Fraction(0))
    cr = form.get((1, 0), Fraction(0))
    ct = form.get((0, 1), Fraction(0))
    cv = form.get((1, 1), Fraction(0))

    # Use v<=r or v<=t when a negative coefficient can absorb a positive v.
    if cr < 0 < cv and cr + cv <= 0:
        cr, cv = cr + cv, Fraction(0)
    if ct < 0 < cv and ct + cv <= 0:
        ct, cv = ct + cv, Fraction(0)

    # Positive terms use r,t<=1/3 and v=r*t<=1/9; negative terms are dropped.
    bound = c0
    if cr > 0:
        bound += cr / 3
    if ct > 0:
        bound += ct / 3
    if cv > 0:
        bound += cv / 9
    return bound


def rows():
    # (non-template chain, template dominator), written symbolically.
    return [
        (((1, 1, "2pq"), (1, 1, "pq"), (1, 1, "p")), ((1, "2pq", 1), (1, "pq", 1), (1, "p", 1))),
        (((1, 2, "pq"), (1, 1, "pq"), (1, 1, "p")), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        (((1, "p", "2q"), (1, "p", "q"), (1, "p", 1)), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        (((1, "2p", "q"), (1, "p", "q"), (1, "p", 1)), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        (((1, "q", "2p"), (1, "q", "p"), (1, 1, "p")), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        (((1, "2q", "p"), (1, "q", "p"), (1, 1, "p")), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        (((1, "pq", 2), (1, "pq", 1), (1, "p", 1)), ((2, "pq", 1), (1, "pq", 1), (1, "p", 1))),
        (((2, 1, "pq"), (1, 1, "pq"), (1, 1, "p")), ((2, "p", "q"), (1, "p", "q"), (1, "p", 1))),
        ((("p", 1, "2q"), ("p", 1, "q"), ("p", 1, 1)), (("p", 2, "q"), ("p", 1, "q"), ("p", 1, 1))),
        ((("q", 1, "2p"), ("q", 1, "p"), (1, 1, "p")), (("p", 2, "q"), ("p", 1, "q"), ("p", 1, 1))),
        ((("2q", 1, "p"), ("q", 1, "p"), (1, 1, "p")), (("p", 2, "q"), ("p", 1, "q"), ("p", 1, 1))),
    ]


if __name__ == "__main__":
    checked = 0
    for non_template, dominator in rows():
        difference = tuple(
            sub(chain_line(dominator)[index], chain_line(non_template)[index])
            for index in range(3)
        )
        corners = (
            difference[0],
            add(difference[0], difference[1]),
            add(difference[0], difference[1], difference[2]),
        )
        bounds = tuple(upper_bound(corner) for corner in corners)
        print(" ".join(form_string(corner) for corner in corners), "bounds", bounds)
        if any(bound > 0 for bound in bounds):
            raise AssertionError((non_template, dominator, corners, bounds))
        checked += 1
    print(f"checked={checked} symbolic dominance rows")

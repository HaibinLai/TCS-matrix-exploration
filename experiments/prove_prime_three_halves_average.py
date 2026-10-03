#!/usr/bin/env python3
"""Symbolic 3/2 upper-bound certificate for the odd-prime hierarchy family.

The average of three legal nested chains is used as an upper bound on the
nested minimum.  The script checks that this average is at most 3/2 times
every sorted independent candidate combination, in both q>=2p and q<2p
factor-order regimes.  Since the difference is affine on 0<=u<=s<=1,
three-corner checks are exact.
"""
from fractions import Fraction


def add(*forms):
    result = {}
    for form in forms:
        for key, value in form.items():
            result[key] = result.get(key, Fraction(0)) + value
    return {key: value for key, value in result.items() if value}


def scale(coefficient, form):
    return {key: coefficient * value for key, value in form.items()}


def subtract(left, right):
    return add(left, scale(Fraction(-1), right))


def factor(name):
    return {
        1: (1, 0, 0),
        2: (2, 0, 0),
        "p": (1, 1, 0),
        "q": (1, 0, 1),
        "2p": (2, 1, 0),
        "2q": (2, 0, 1),
        "pq": (1, 1, 1),
        "2pq": (2, 1, 1),
    }[name]


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


def form_string(form):
    names = {(0, 0): "1", (1, 0): "r", (0, 1): "t", (1, 1): "v"}
    terms = []
    for key, coefficient in sorted(form.items()):
        sign = "+" if coefficient > 0 else "-"
        terms.append(f"{sign}{abs(coefficient)}*{names[key]}")
    return " ".join(terms).lstrip("+") or "0"


def upper_bound(form):
    """Simple bound using 0<t<r<=1/3 and v=r*t."""
    constant = form.get((0, 0), Fraction(0))
    r = form.get((1, 0), Fraction(0))
    t = form.get((0, 1), Fraction(0))
    v = form.get((1, 1), Fraction(0))

    # Absorb a positive v into a negative r or t using v<=r and v<=t.
    if r < 0 < v and r + v <= 0:
        r, v = r + v, Fraction(0)
    if t < 0 < v and t + v <= 0:
        t, v = t + v, Fraction(0)

    bound = constant
    if r > 0:
        bound += r / 3
    if t > 0:
        bound += t / 3
    if v > 0:
        bound += v / 9
    return bound


def candidate_levels(regime):
    first = [
        ("A", ("q", "p", 2)),
        ("B_" + regime, (("q", "2p", 1) if regime == ">=" else ("2p", "q", 1))),
        ("C", ("2q", "p", 1)),
        ("D", ("pq", 2, 1)),
        ("E", ("2pq", 1, 1)),
    ]
    second = [("F", ("q", "p", 1)), ("G", ("pq", 1, 1))]
    return first, second


if __name__ == "__main__":
    chains = [
        (("p", 2, "q"), ("p", 1, "q"), ("p", 1, 1)),
        (("p", "q", 2), ("p", "q", 1), ("p", 1, 1)),
        (("pq", 1, 2), ("pq", 1, 1), ("p", 1, 1)),
    ]
    average = tuple(scale(Fraction(1, 3), add(*(chain_line(chain)[index] for chain in chains))) for index in range(3))
    h = line(("p", 1, 1))
    checked = 0
    for regime in (">=", "<"):
        first, second = candidate_levels(regime)
        for first_name, first_grid in first:
            for second_name, second_grid in second:
                independent = tuple(
                    add(line(first_grid)[index], line(second_grid)[index], h[index])
                    for index in range(3)
                )
                delta = tuple(
                    subtract(average[index], scale(Fraction(3, 2), independent[index]))
                    for index in range(3)
                )
                corners = (
                    delta[0],
                    add(delta[0], delta[1]),
                    add(delta[0], delta[1], delta[2]),
                )
                bounds = tuple(upper_bound(corner) for corner in corners)
                print(regime, first_name, second_name, " | ", " ; ".join(form_string(corner) for corner in corners), "bounds", bounds)
                if any(bound > 0 for bound in bounds):
                    raise AssertionError((regime, first_name, second_name, corners, bounds))
                checked += 1
    print(f"checked={checked} symbolic average certificates")

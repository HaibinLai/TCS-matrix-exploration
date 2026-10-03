#!/usr/bin/env python3
"""Scan the fixed p=99 active-line cover for edge-template changes in u=1/q."""
from fractions import Fraction as F
from exact_multilevel_2d import build_envelopes, line, subtract
from exact_overlay_2d import active_edge_segments

P = 99
Q0 = 997


def inv_symbolic_grid(g):
    return tuple((F(d // Q0), 1) if d % Q0 == 0 else (F(d), 0) for d in g)


def inv_product(x, y):
    if x[1] + y[1] == 0:
        return (F(1, x[0] * y[0]), F(0))
    return (F(0), F(1, x[0] * y[0]))


def symbolic_line(g):
    a, b, c = inv_symbolic_grid(g)
    return (inv_product(a, b), inv_product(a, c), inv_product(b, c))


def add_lines(lines):
    out = [(F(0), F(0))] * 3
    for line_ in lines:
        out = [(a[0] + b[0], a[1] + b[1]) for a, b in zip(out, line_)]
    return tuple(out)


def evaluate_line(line_, u):
    return tuple(a + b * u for a, b in line_)


def compatible(inner, outer):
    return all(i % o == 0 for i, o in zip(inner, outer))


def normalize(equality):
    first = next(x for x in equality if x)
    return tuple(x / first for x in equality)


def build_cover():
    pstars = (2 * P * Q0, P * Q0, P)
    choices, independent, nested, stats = build_envelopes(pstars)
    covers = []
    for level, grids in enumerate(choices):
        mapping = {}
        for g in grids:
            mapping.setdefault(line(g), []).append(symbolic_line(g))
        covers.append([mapping[x][0] for x in independent[level]])

    chains = []
    for inner in choices[0]:
        for middle in choices[1]:
            if not compatible(inner, middle):
                continue
            for outer in choices[2]:
                if compatible(middle, outer):
                    chains.append((inner, middle, outer))
    mapping = {}
    for chain in chains:
        key = tuple(sum(line(g)[i] for g in chain) for i in range(3))
        mapping.setdefault(key, []).append(add_lines([symbolic_line(g) for g in chain]))
    covers.append([mapping[x][0] for x in nested])
    return covers, stats


def edge_keys(lines, u):
    numeric = [evaluate_line(line_, u) for line_ in lines]
    keys = set()
    for _, _, equality in active_edge_segments(numeric):
        found = None
        for i in range(len(numeric)):
            for j in range(i + 1, len(numeric)):
                pair = subtract(numeric[i], numeric[j])
                if pair == equality or tuple(-x for x in pair) == equality:
                    found = (i, j)
                    break
            if found is not None:
                break
        if found is None:
            raise AssertionError("edge pair not found")
        keys.add(found)
    return frozenset(keys)


def main():
    covers, stats = build_cover()
    u_values = [F(0), F(1, 997), F(1, 1009), F(1, 10007), F(1, 100003), F(1, 10**6)]
    reference = None
    for u in u_values:
        current = tuple(edge_keys(lines, u) for lines in covers)
        if u == F(1, 997):
            reference = current
        changed = [] if reference is None else [i for i, (a, b) in enumerate(zip(reference, current)) if a != b]
        print("u=", u, "edge counts=", tuple(map(len, current)), "changed levels=", changed)
        if changed:
            raise AssertionError((u, changed))
    print("template_stable=True", "partial_stats=", tuple(stats))


if __name__ == "__main__":
    main()

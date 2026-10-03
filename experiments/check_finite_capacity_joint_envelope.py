#!/usr/bin/env python3
"""Check the event accounting used by the finite-capacity joint envelope.

The numerical example is deliberately an abstract phase trace.  It checks the
logic of the overlap warning: the first loads are included in both the cut
boundary and the standard phase bound, so adding the two scalar lower bounds can
exceed the traffic of the same trace.  It is not a GEMM schedule certificate.
"""
from fractions import Fraction as F


def continuous_phase_bound(work, capacity, phase_work):
    return F(capacity) * (F(work, phase_work) - 1)


def run():
    capacity = 6
    phase_work = 8
    work = 27
    first_loads = 6
    trace_loads = 18

    phase_lb = continuous_phase_bound(work, capacity, phase_work)
    assert phase_lb == F(57, 4)
    assert max(F(first_loads), phase_lb) < trace_loads
    assert F(first_loads) + phase_lb > trace_loads

    # Infinite-capacity limit: only the cut term remains in this interface.
    assert continuous_phase_bound(27, 1000, 10_000) < 0
    print("joint phase/cut overlap check=True")
    print("first_loads", first_loads,
          "phase_lb", phase_lb,
          "trace_loads", trace_loads,
          "naive_sum", F(first_loads) + phase_lb)


if __name__ == "__main__":
    run()

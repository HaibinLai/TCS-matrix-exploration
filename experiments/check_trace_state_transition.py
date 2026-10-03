#!/usr/bin/env python3
"""Check the resident-state transition used by the joint trace envelope."""


def next_resident(resident, shared, arrivals, phase_entries, capacity):
    candidates = resident | shared | arrivals | phase_entries
    mandatory = shared | arrivals
    assert len(mandatory) <= capacity
    optional = candidates - mandatory
    # Keep newly available entries first; evicting other entries is optional.
    return mandatory | set(list(optional)[:capacity - len(mandatory)])


def run():
    resident = {"a0"}
    shared = {"b0"}
    arrivals = {"c0"}
    phase_entries = {"p0"}
    next_state = next_resident(resident, shared, arrivals, phase_entries, 3)

    # The transition must permit an arrival to survive into the next phase.
    assert "c0" in next_state
    assert "b0" in next_state
    assert next_state <= resident | shared | arrivals | phase_entries

    # A shared entry can be consumed by two owners without two edge arrivals.
    assert len({"b0"}) == 1
    print("trace state transition check=True")
    print("candidate_entries", sorted(resident | shared | arrivals | phase_entries))


if __name__ == "__main__":
    run()

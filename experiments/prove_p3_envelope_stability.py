#!/usr/bin/env python3
"""Run the exact symbolic envelope-cover certificate for p=3, q0=67."""
from prove_p99_envelope_stability import certify

if __name__ == "__main__":
    certify(3, 67)

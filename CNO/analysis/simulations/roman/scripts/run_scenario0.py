"""Run and print the initial Roman spatial-kernel verification card."""

from __future__ import annotations

import json

from cno_sim.scenarios import run_initial_verification


if __name__ == "__main__":
    print(json.dumps(run_initial_verification(), indent=2, sort_keys=True))

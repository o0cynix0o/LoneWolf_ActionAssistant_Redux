#!/usr/bin/env python3
"""Aggregate Book 5 onboarding validation."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable

COMMANDS = [
    [PYTHON, "testing/lwbook5_setup_smoke.py"],
    [PYTHON, "testing/lwbook5_section_flow_audit.py", "--check"],
    [PYTHON, "testing/lwbook5_automation_language_audit.py", "--check"],
    [PYTHON, "testing/lwbook5_playable_pipeline_smoke.py"],
    [PYTHON, "testing/playtest_book4.py"],
]


def main() -> int:
    for command in COMMANDS:
        print(f"Running: {' '.join(command)}")
        completed = subprocess.run(command, cwd=ROOT)
        if completed.returncode:
            return completed.returncode
    print("Book 5 aggregate validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

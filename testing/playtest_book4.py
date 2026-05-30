#!/usr/bin/env python3
"""Aggregate validation for the Book 4 onboarding helper build."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable


COMMANDS = [
    [
        PYTHON,
        "-m",
        "py_compile",
        "app_server.py",
        "lonewolf_redux.py",
        "launch_lonewolf_redux.py",
        "ws_server.py",
        "testing/lwbook4_setup_smoke.py",
        "testing/lwbook4_section_flow_audit.py",
        "testing/lwbook4_automation_language_audit.py",
        "testing/lwbook4_playable_pipeline_smoke.py",
        "testing/browser_choices_static_smoke.py",
        "testing/browser_landing_static_smoke.py",
        "testing/browser_settings_static_smoke.py",
    ],
    [PYTHON, "testing/lwbook4_setup_smoke.py"],
    [PYTHON, "testing/lwbook4_section_flow_audit.py", "--check"],
    [PYTHON, "testing/lwbook4_automation_language_audit.py", "--check"],
    [PYTHON, "testing/lwbook4_playable_pipeline_smoke.py"],
    [PYTHON, "testing/lwbook3_setup_smoke.py"],
    [PYTHON, "testing/lwbook3_playable_pipeline_smoke.py"],
    [PYTHON, "testing/lwbook2_setup_smoke.py"],
    [PYTHON, "testing/lwbook2_playable_pipeline_smoke.py"],
    [PYTHON, "testing/browser_choices_static_smoke.py"],
    [PYTHON, "testing/browser_landing_static_smoke.py"],
    [PYTHON, "testing/browser_settings_static_smoke.py"],
]


def main() -> int:
    for index, command in enumerate(COMMANDS, 1):
        print(f"[{index}/{len(COMMANDS)}] {' '.join(command)}")
        subprocess.run(command, cwd=ROOT, check=True)
    print("Book 4 aggregate playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

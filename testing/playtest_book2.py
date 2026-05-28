#!/usr/bin/env python3
"""Run the current Book 2 acceptance checks."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


CHECKS: list[list[str]] = [
    [
        sys.executable,
        "-m",
        "py_compile",
        "app_server.py",
        "lonewolf_redux.py",
        "launch_lonewolf_redux.py",
        "ws_server.py",
        "testing/lwbook2_setup_smoke.py",
        "testing/lwbook2_section_flow_audit.py",
        "testing/lwbook2_automation_language_audit.py",
        "testing/lwbook2_playable_pipeline_smoke.py",
        "testing/lwbook1_achievement_smoke.py",
        "testing/browser_choices_static_smoke.py",
    ],
    [sys.executable, "testing/lwbook2_setup_smoke.py"],
    [sys.executable, "testing/lwbook2_section_flow_audit.py", "--check"],
    [sys.executable, "testing/lwbook2_automation_language_audit.py", "--write"],
    [sys.executable, "testing/lwbook2_playable_pipeline_smoke.py"],
    [sys.executable, "testing/lwbook1_achievement_smoke.py"],
    [sys.executable, "testing/browser_choices_static_smoke.py"],
]


def format_command(command: list[str]) -> str:
    return " ".join(command)


def main() -> int:
    failures: list[tuple[list[str], int]] = []
    for index, command in enumerate(CHECKS, start=1):
        print(f"[{index}/{len(CHECKS)}] {format_command(command)}", flush=True)
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode:
            failures.append((command, result.returncode))
            break

    if failures:
        command, code = failures[0]
        print(f"Book 2 playtest failed with exit code {code}: {format_command(command)}", file=sys.stderr)
        return code or 1

    print("Book 2 aggregate playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

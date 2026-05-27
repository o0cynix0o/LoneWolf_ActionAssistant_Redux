#!/usr/bin/env python3
"""Run the Book 1 acceptance playtest ladder."""

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
    ],
    [sys.executable, "testing/lwbook1_section_flow_audit.py", "--check"],
    [sys.executable, "testing/lwbook1_simple_automation_smoke.py"],
    [sys.executable, "testing/lwbook1_healing_loss_smoke.py"],
    [sys.executable, "testing/lwbook1_player_choice_aftermath_smoke.py"],
    [sys.executable, "testing/lwbook1_random_recovery_smoke.py"],
    [sys.executable, "testing/lwbook1_section21_staged_smoke.py"],
    [sys.executable, "testing/lwbook1_route_random_smoke.py"],
    [sys.executable, "testing/lwbook1_combat_smoke.py"],
    [sys.executable, "testing/lwbook1_combat_edge_playtest.py"],
    [sys.executable, "testing/lwbook1_automation_language_smoke.py"],
    [sys.executable, "testing/lwbook1_branch_playtest.py"],
    [sys.executable, "testing/lwbook1_route_gauntlet_playtest.py"],
    [sys.executable, "testing/lwbook1_end_to_end_playtest.py"],
    [sys.executable, "testing/lwbook1_achievement_smoke.py"],
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
        print(f"Book 1 playtest failed with exit code {code}: {format_command(command)}", file=sys.stderr)
        return code or 1

    print("Book 1 aggregate playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

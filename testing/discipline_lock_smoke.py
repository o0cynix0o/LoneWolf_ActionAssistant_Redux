#!/usr/bin/env python3
"""Ensure Kai Disciplines are read-only during live play."""

from __future__ import annotations

import contextlib
import io
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app_server  # noqa: E402
import lonewolf_redux  # noqa: E402


ASSISTANT_HTML = ROOT / "assistant.html"


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def quiet(callable_obj, *args, **kwargs) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        callable_obj(*args, **kwargs)
    return buffer.getvalue().strip()


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    assistant = lonewolf_redux.LoneWolfReduxAssistant(
        save_dir=ROOT / "testing" / "tmp" / "discipline-lock-saves",
        data_dir=ROOT / "data",
    )
    assistant.state = lonewolf_redux.create_book1_character_state(
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"],
        combat_skill_roll=4,
        endurance_roll=4,
        gold_roll=4,
        starting_find_roll=4,
        weaponskill_roll=4,
    )
    return assistant


def test_browser_controls_removed() -> None:
    source = ASSISTANT_HTML.read_text(encoding="utf-8")
    assert_true("data-power" not in source, "Disciplines panel must not expose data-power buttons.")
    assert_true("action: 'power'" not in source, "Browser must not send live power mutation actions.")
    assert_true("${has ? 'Known' : 'Available'}</small></div>" in source, "Disciplines should render read-only status rows.")


def test_cli_power_command_read_only() -> None:
    assistant = fresh_assistant()
    before = list(assistant.character["KaiDisciplines"])

    add_output = quiet(assistant.power_command, ["discipline", "add", "Healing"])
    remove_output = quiet(assistant.power_command, ["discipline", "remove", "Camouflage"])

    assert_true(assistant.character["KaiDisciplines"] == before, "power_command must not mutate Disciplines.")
    assert_true("only be changed" in add_output, "add command should explain the lock.")
    assert_true("only be changed" in remove_output, "remove command should explain the lock.")


def test_api_power_action_read_only() -> None:
    app_server.ASSISTANT = fresh_assistant()
    before = list(app_server.ASSISTANT.character["KaiDisciplines"])
    output = app_server.handle_action({"action": "power", "mode": "add", "name": "Healing"})

    assert_true(app_server.ASSISTANT.character["KaiDisciplines"] == before, "power API must not mutate Disciplines.")
    assert_true("only be changed" in output, "power API should explain the lock.")


def main() -> int:
    test_browser_controls_removed()
    test_cli_power_command_read_only()
    test_api_power_action_read_only()
    print("Discipline lock smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

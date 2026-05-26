#!/usr/bin/env python3
"""Smoke-test Book 1 section 21 staged marsh roll helper."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "section21-staged-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "section21-staged-last-save.txt"
DEFAULT_DISCIPLINES = ["Healing", "Camouflage", "Sixth Sense", "Tracking", "Weaponskill"]


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Section 21 Staged Smoke",
        kai_disciplines=DEFAULT_DISCIPLINES,
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=3,
        starting_find_roll=4,
        weaponskill_roll=6,
    )
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


def assert_false(value, label: str) -> None:
    if value:
        raise AssertionError(f"{label}: expected falsey value, got {value!r}")


def set_section_21(assistant: lonewolf_redux.LoneWolfReduxAssistant) -> None:
    quiet(assistant.set_section, 21)
    assert_equal(assistant.state["CurrentSection"], 21, "section 21 position")


def smoke_first_roll_success() -> None:
    assistant = fresh_assistant()
    set_section_21(assistant)

    result = assistant.roll_current_section(5)
    assert_equal(result["Staged"], True, "first roll is staged")
    assert_equal(result["Stage"], "first", "first roll stage id")
    assert_equal(result["Route"], 189, "first roll success route")
    assert_equal(result["Complete"], True, "first roll completes staged helper")
    assert_false(assistant.death_active(), "first roll success is not death")

    payload = assistant.current_section_flow_payload()["StagedRoll"]
    assert_equal(payload["Complete"], True, "first roll payload complete")
    assert_equal(len(payload["History"]), 1, "first roll history length")

    repeat = assistant.roll_current_section(0)
    assert_equal(repeat["Route"], 189, "completed staged roll keeps route")
    assert_equal(repeat["AlreadyComplete"], True, "repeat staged roll is not rerolled")
    assert_equal(
        repeat["ActionMessages"],
        ["Staged roll already complete for this section visit."],
        "repeat staged roll message",
    )


def smoke_second_roll_recovery() -> None:
    assistant = fresh_assistant()
    set_section_21(assistant)

    result = assistant.roll_current_section(4)
    assert_equal(result["Route"], None, "first low roll has no route")
    assert_equal(result["NextStage"], "second", "first low roll advances to second stage")
    assert_equal(result["Complete"], False, "first low roll remains incomplete")

    payload = assistant.current_section_flow_payload()["StagedRoll"]
    assert_equal(payload["Stage"], "second", "payload advances to second stage")

    result = assistant.roll_current_section(8)
    assert_equal(result["Stage"], "second", "second roll stage id")
    assert_equal(result["Route"], 189, "second roll recovery route")
    assert_equal(result["Complete"], True, "second roll completes staged helper")

    payload = assistant.current_section_flow_payload()["StagedRoll"]
    assert_equal(len(payload["History"]), 2, "second roll history length")
    assert_false(assistant.death_active(), "second roll recovery is not death")


def smoke_final_roll_success() -> None:
    assistant = fresh_assistant()
    set_section_21(assistant)

    assistant.roll_current_section(4)
    assistant.roll_current_section(7)
    payload = assistant.current_section_flow_payload()["StagedRoll"]
    assert_equal(payload["Stage"], "final", "payload advances to final stage")

    result = assistant.roll_current_section(9)
    assert_equal(result["Stage"], "final", "final roll stage id")
    assert_equal(result["Route"], 312, "final roll escape route")
    assert_equal(result["Complete"], True, "final escape completes staged helper")
    assert_false(assistant.death_active(), "final roll success is not death")


def smoke_final_roll_death() -> None:
    assistant = fresh_assistant()
    set_section_21(assistant)

    assistant.roll_current_section(4)
    assistant.roll_current_section(7)
    result = assistant.roll_current_section(8)

    assert_equal(result["Stage"], "final", "death roll final stage")
    assert_equal(result["Route"], None, "death roll has no route")
    assert_equal(result["Ending"], "death", "death roll ending")
    assert_equal(result["Complete"], True, "death roll completes staged helper")
    assert_true(result["ActionsApplied"], "death ending action applied")
    assert_true(assistant.death_active(), "death state active")
    assert_equal(assistant.automation.get("Ending", {}).get("Type"), "death", "ending marker")
    assert_equal(assistant.character["EnduranceCurrent"], 0, "death sets END to zero")

    recovery = assistant.death_recovery_payload()
    assert_equal(recovery["CanRewind"], True, "section 21 death can rewind")
    assert_equal(recovery["RewindTarget"]["Section"], 1, "section 21 death rewind target")


def main() -> int:
    smoke_first_roll_success()
    smoke_second_roll_recovery()
    smoke_final_roll_success()
    smoke_final_roll_death()
    print("Book 1 section 21 staged roll smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

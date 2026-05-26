#!/usr/bin/env python3
"""Smoke-test Book 1 random side effects and recovery item behavior."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "random-recovery-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "random-recovery-last-save.txt"
DEFAULT_DISCIPLINES = ["Camouflage", "Sixth Sense", "Tracking", "Mindshield", "Weaponskill"]


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Random Recovery Smoke",
        kai_disciplines=disciplines or DEFAULT_DISCIPLINES,
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


def smoke_random_endurance_side_effects() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 36)
    start_endurance = int(assistant.character["EnduranceCurrent"])
    result = assistant.roll_current_section(4)
    assert_equal(result["Route"], 140, "section 36 fall route")
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance - 2, "section 36 fall END loss")
    assert_true(result["ActionMessages"], "section 36 action message")

    result = assistant.roll_current_section(4)
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance - 2, "section 36 does not double-apply")
    assert_equal(
        result["ActionMessages"],
        ["Roll outcome effects already applied for this visit."],
        "section 36 repeat roll message",
    )

    assistant = fresh_assistant()
    quiet(assistant.set_section, 158)
    after_entry = int(assistant.character["EnduranceCurrent"])
    result = assistant.roll_current_section(8)
    assert_equal(result["Route"], 106, "section 158 route")
    assert_equal(assistant.character["EnduranceCurrent"], after_entry - 4, "section 158 second bolt END loss")


def smoke_random_backpack_side_effects() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Laumspur"]
    quiet(assistant.set_section, 188)
    result = assistant.roll_current_section(0)
    assert_equal(result["Route"], 303, "section 188 low roll route")
    assert_equal(assistant.inventory["HasBackpack"], False, "section 188 loses Backpack")
    assert_equal(assistant.inventory["BackpackItems"], [], "section 188 clears Backpack Items")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Laumspur"]
    quiet(assistant.set_section, 188)
    start_endurance = int(assistant.character["EnduranceCurrent"])
    result = assistant.roll_current_section(9)
    assert_equal(result["Route"], 303, "section 188 high roll route")
    assert_equal(assistant.inventory["HasBackpack"], True, "section 188 high roll keeps Backpack")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal", "Laumspur"], "section 188 high roll keeps items")
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance - 3, "section 188 high roll END loss")


def smoke_laumspur_recovery() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Laumspur")
    assistant.character["EnduranceCurrent"] = int(assistant.character["EnduranceMax"]) - 5
    quiet(assistant.use_item, "backpack", "Laumspur")
    assert_equal(
        assistant.character["EnduranceCurrent"],
        int(assistant.character["EnduranceMax"]) - 2,
        "Laumspur restores 3 END",
    )
    if "Laumspur" in assistant.inventory["BackpackItems"]:
        raise AssertionError("Laumspur was not consumed")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Laumspur"]
    assistant.character["EnduranceCurrent"] = int(assistant.character["EnduranceMax"]) - 5
    quiet(assistant.set_section, 130)
    assert_equal(assistant.inventory["BackpackItems"], [], "Laumspur fulfilled required Meal")
    assert_equal(
        assistant.character["EnduranceCurrent"],
        int(assistant.character["EnduranceMax"]) - 2,
        "Laumspur Meal restored 3 END",
    )


def main() -> int:
    smoke_random_endurance_side_effects()
    smoke_random_backpack_side_effects()
    smoke_laumspur_recovery()
    print("Book 1 random/recovery smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke-test confirmed Book 1 simple section effects."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "simple-automation-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "simple-automation-last-save.txt"


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Automation Smoke",
        kai_disciplines=disciplines
        or ["Camouflage", "Sixth Sense", "Tracking", "Healing", "Weaponskill"],
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


def assert_in(member, container, label: str) -> None:
    if member not in container:
        raise AssertionError(f"{label}: {member!r} not found in {container!r}")


def smoke_endurance_and_meal() -> None:
    assistant = fresh_assistant()
    start_end = int(assistant.character["EnduranceCurrent"])
    quiet(assistant.set_section, 119)
    assert_equal(assistant.character["EnduranceCurrent"], start_end - 2, "section 119 END loss")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 130)
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), 0, "section 130 consumed Meal")
    assert_equal(assistant.character["EnduranceCurrent"], assistant.character["EnduranceMax"], "section 130 no END loss with Meal")

    assistant = fresh_assistant(disciplines=["Hunting", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    assistant.inventory["BackpackItems"] = []
    start_end = int(assistant.character["EnduranceCurrent"])
    quiet(assistant.set_section, 130)
    assert_equal(assistant.character["EnduranceCurrent"], start_end, "Hunting skips required Meal loss")

    assistant = fresh_assistant(disciplines=["Hunting", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    assistant.inventory["BackpackItems"] = ["Meal"]
    start_end = int(assistant.character["EnduranceCurrent"])
    quiet(assistant.set_section, 235)
    messages = assistant.automation["Journal"][-1]["Messages"]
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "Hunting preserves carried Meal")
    assert_equal(assistant.character["EnduranceCurrent"], start_end, "Hunting prevents required Meal END loss")
    assert_in(
        "Hunting: no Meal needed; Meals unchanged at 1",
        messages,
        "Hunting exemption receipt includes unchanged Meal count",
    )

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] -= 8
    quiet(assistant.set_section, 212)
    assert_equal(assistant.character["EnduranceCurrent"], assistant.character["EnduranceMax"], "section 212 restores END")


def smoke_gold_loot_and_items() -> None:
    assistant = fresh_assistant()
    start_gold = int(assistant.inventory["GoldCrowns"])
    quiet(assistant.set_section, 33)
    assert_equal(assistant.inventory["GoldCrowns"], start_gold + 3, "section 33 Gold Crowns")

    assistant = fresh_assistant()
    start_end = int(assistant.character["EnduranceCurrent"])
    quiet(assistant.set_section, 76)
    assert_equal(assistant.character["EnduranceCurrent"], start_end - 2, "section 76 END loss")
    assert_in("Vordak Gem", assistant.inventory["BackpackItems"], "section 76 Vordak Gem")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 20)
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["Weapons"] = []
    assistant.inventory["HasBackpack"] = False
    assistant.automation_flags["backpackAvailable"] = False
    assistant.automation_flags["backpackItemsAvailable"] = False
    quiet(assistant.apply_flow_loot, "20-supplies")
    assert_equal(assistant.inventory["HasBackpack"], True, "section 20 restores Backpack")
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), 2, "section 20 Meals")
    assert_in("Dagger", assistant.inventory["Weapons"], "section 20 Dagger")


def smoke_gear_loss_and_completion() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 162)
    assert_equal(assistant.inventory["Weapons"], [], "section 162 discards Weapons")
    assert_equal(assistant.inventory["BackpackItems"], [], "section 162 discards Backpack Items")
    assert_equal(assistant.inventory["HasBackpack"], False, "section 162 discards Backpack")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Vordak Gem")
    start_end = int(assistant.character["EnduranceCurrent"])
    start_cs = int(assistant.character["CombatSkillCurrent"])
    quiet(assistant.set_section, 236)
    assert_equal(assistant.character["EnduranceCurrent"], start_end - 6, "section 236 END loss")
    assert_equal(assistant.character["CombatSkillCurrent"], start_cs - 1, "section 236 CS loss")
    if "Vordak Gem" in assistant.inventory["BackpackItems"]:
        raise AssertionError("section 236 did not remove Vordak Gem")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 350)
    assert_in(1, assistant.character["CompletedBooks"], "section 350 completed Book 1")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "section 350 ending")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 53)
    assert_equal(assistant.death_active(), True, "section 53 death active")
    assert_equal(assistant.automation["Ending"]["Type"], "death", "section 53 ending")


def main() -> int:
    smoke_endurance_and_meal()
    smoke_gold_loot_and_items()
    smoke_gear_loss_and_completion()
    print("Book 1 simple automation smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

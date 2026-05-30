#!/usr/bin/env python3
"""Smoke-test Book 5 playable helper data."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book5-playable-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book5-playable-last-save.txt"
BOOK5_CHOICES = ["shield", "two-special-rations", "potion-of-laumspur", "sword"]


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book5_character_state(
        name="Book Five Pipeline",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=BOOK5_CHOICES,
    )
    assistant.character["KaiDisciplines"] = [
        "Camouflage",
        "Hunting",
        "Sixth Sense",
        "Tracking",
        "Healing",
        "Weaponskill",
        "Mindshield",
        "Mindblast",
        "Animal Kinship",
    ]
    assistant.character["CompletedBooks"] = [1, 2, 3, 4]
    assistant.inventory["SpecialItems"] = lonewolf_redux.add_unique_item(
        assistant.inventory["SpecialItems"], "Sommerswerd"
    )
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def loss_choice_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, choice_id: str) -> dict:
    for choice in assistant.current_section_flow_payload()["LossChoices"]:
        if choice["Id"] == choice_id:
            return choice
    raise AssertionError(f"loss choice {choice_id!r} not found")


def test_book5_confiscation_restore_and_safekeeping() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Sword", "Dagger"]
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["SpecialItems"] = ["Sommerswerd", "Crystal Star Pendant"]
    assistant.inventory["GoldCrowns"] = 33
    assistant.inventory["Nobles"] = 33
    assistant.automation["Stored"]["safekeepingSpecialItems"] = ["Silver Helm"]

    quiet(assistant.set_section, 10)
    assert_equal(assistant.inventory["Weapons"], [], "weapons confiscated")
    assert_equal(assistant.inventory["BackpackItems"], [], "backpack confiscated")
    assert_equal(assistant.inventory["SpecialItems"], [], "special items confiscated")
    assert_equal(assistant.inventory["GoldCrowns"], 0, "gold confiscated")
    assert_true("Silver Helm" in assistant.automation["Stored"]["safekeepingSpecialItems"], "safekeeping survives confiscation")

    quiet(assistant.set_section, 69)
    assert_equal(assistant.automation["Stored"]["confiscatedEquipment"]["GoldCrowns"], 33, "section 69 does not overwrite stored gold")

    quiet(assistant.set_section, 14)
    assert_true("Sword" in assistant.inventory["Weapons"], "weapon restored")
    assert_true("Rope" in assistant.inventory["BackpackItems"], "backpack restored")
    assert_true("Crystal Star Pendant" in assistant.inventory["SpecialItems"], "special item restored")
    assert_equal(assistant.inventory["GoldCrowns"], 33, "gold restored")


def test_book5_meals_blood_poisoning_and_loss_choices() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope", "Prism"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 137)
    assert_equal(assistant.inventory["BackpackItems"], ["Rope", "Prism"], "city meal consumes Backpack Meal")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "Meal prevents END loss")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Potion of Laumspur (+4 END)"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 63)
    assert_true(assistant.automation_flags["book5BloodPoisoningActive"], "blood poisoning starts")
    quiet(assistant.set_section, 102)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "blood poisoning charges next section")
    quiet(assistant.use_item, "backpack", "Potion of Laumspur")
    assert_equal(assistant.character["EnduranceCurrent"], 22, "Laumspur restores END")
    assert_equal(assistant.automation_flags["book5BloodPoisoningActive"], False, "Laumspur cures blood poisoning")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["Weapons"] = ["Sword"]
    quiet(assistant.set_section, 19)
    choice = loss_choice_by_id(assistant, "guard-payment-1")
    assert_true(all(item["Item"] != "Meal" for item in choice["Candidates"]), "guard payment excludes Meals")
    quiet(assistant.apply_section_loss, "guard-payment-1", "backpack", "Rope")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "guard payment removes selected item")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["Weapons"] = ["Sword"]
    assistant.inventory["SpecialItems"] = ["Map of Vassagonia"]
    quiet(assistant.set_section, 270)
    choice = loss_choice_by_id(assistant, "cave-pack-loss-1")
    assert_equal(choice["Source"], "fallback", "section 270 falls back without Backpack Items")


def test_book5_combat_and_completion() -> None:
    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 24
    quiet(assistant.set_section, 20)
    quiet(assistant.start_section_combat, "20-horseman")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [
        {
            "Round": 1,
            "Roll": 0,
            "Ratio": 0,
            "EnemyLoss": 28,
            "PlayerLoss": 5,
            "LoneWolfReduxLoss": 5,
        }
    ]
    assistant.character["EnduranceCurrent"] = 19
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.character["EnduranceCurrent"], 21, "section 20 restores half combat loss")
    assert_equal(assistant.state["CurrentSection"], 125, "section 20 fast victory route")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 350)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 350 END loss")
    assert_true("Sommerswerd" not in assistant.inventory["SpecialItems"], "Sommerswerd removed")
    assert_true(assistant.automation_flags["book5SommerswerdLost"], "Sommerswerd lost flag set")
    quiet(assistant.set_section, 400)
    assert_true("Sommerswerd" in assistant.inventory["SpecialItems"], "Sommerswerd restored at completion")
    assert_true("Book of the Magnakai" in assistant.inventory["SpecialItems"], "Book of the Magnakai recorded")
    assert_true(5 in assistant.character["CompletedBooks"], "Book 5 completed")
    assert_equal(len(assistant.character["KaiDisciplines"]), 10, "Kai Master final Discipline added")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "Book 5 success ending")


def main() -> int:
    test_book5_confiscation_restore_and_safekeeping()
    test_book5_meals_blood_poisoning_and_loss_choices()
    test_book5_combat_and_completion()
    print("Book 5 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

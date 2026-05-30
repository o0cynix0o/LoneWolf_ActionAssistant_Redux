#!/usr/bin/env python3
"""Smoke-test Book 5 setup, carry-forward, and safekeeping rules."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book5-setup-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book5-setup-last-save.txt"

BOOK4_CHOICES = [
    "dagger",
    "spear",
    "two-potions-of-laumspur",
    "five-special-rations",
    "chainmail-waistcoat",
    "shield",
]
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


def fresh_book4_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book4_character_state(
        name="Book Five Smoke",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=BOOK4_CHOICES,
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
    ]
    assistant.character["CompletedBooks"] = [1, 2, 3]
    assistant.inventory["SpecialItems"] = lonewolf_redux.add_unique_item(
        assistant.inventory["SpecialItems"], "Sommerswerd"
    )
    assistant.inventory["SpecialItems"] = lonewolf_redux.add_unique_item(
        assistant.inventory["SpecialItems"], "Crystal Star Pendant"
    )
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["GoldCrowns"] = 48
    assistant.inventory["Nobles"] = 48
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 4)
    return assistant


def test_book4_to_book5_campaign_setup() -> None:
    assistant = fresh_book4_assistant()
    quiet(
        assistant.continue_completed_book,
        kai_discipline="Animal Kinship",
        book5_gold_roll=9,
        book5_equipment_choices=BOOK5_CHOICES,
        book5_weapon_exchanges=["Dagger"],
        book5_safekeeping_special_items=["Crystal Star Pendant"],
    )

    assert_equal(assistant.character["BookNumber"], 5, "current book")
    assert_equal(assistant.state["CurrentSection"], 1, "current section")
    assert_true(4 in assistant.character["CompletedBooks"], "Book 4 completed")
    assert_true("Animal Kinship" in assistant.character["KaiDisciplines"], "new Kai Discipline")
    assert_equal(len(assistant.character["KaiDisciplines"]), 9, "nine Kai Disciplines at Book 5 start")
    assert_equal(assistant.inventory["GoldCrowns"], 50, "gold cap")
    assert_true("Map of Vassagonia" in assistant.inventory["SpecialItems"], "Book 5 map added")
    assert_true("Sommerswerd" in assistant.inventory["SpecialItems"], "Sommerswerd remains active")
    assert_true("Crystal Star Pendant" not in assistant.inventory["SpecialItems"], "safekept item removed from active inventory")
    assert_true(
        "Crystal Star Pendant" in assistant.automation["Stored"]["safekeepingSpecialItems"],
        "safekept item stored",
    )
    records = assistant.automation["Stored"].get("safekeepingRecords", [])
    assert_true(
        any(
            record.get("Item") == "Crystal Star Pendant"
            and record.get("Place") == "Kai Monastery"
            for record in records
        ),
        "safekeeping place recorded",
    )
    assert_true("Rope" in assistant.inventory["BackpackItems"], "Backpack carries forward")
    assert_true("Potion of Laumspur (+4 END)" in assistant.inventory["BackpackItems"], "Book 5 Laumspur added")
    assert_true("Sword" in assistant.inventory["Weapons"], "Book 5 weapon added")
    assert_equal(assistant.state["CurrentBookStats"]["BookNumber"], 5, "Book 5 stats started")


def test_standalone_book5_creation() -> None:
    state = lonewolf_redux.create_book5_character_state(
        name="Fresh Book Five",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=2,
        endurance_roll=3,
        gold_roll=4,
        weaponskill_roll=5,
        equipment_choices=BOOK5_CHOICES,
    )

    assert_equal(state["Character"]["BookNumber"], 5, "standalone book")
    assert_equal(state["Character"]["CombatSkillCurrent"], 12, "standalone CS")
    assert_equal(state["Character"]["EnduranceCurrent"], 23, "standalone END")
    assert_equal(state["Inventory"]["GoldCrowns"], 14, "standalone gold")
    assert_true("Map of Vassagonia" in state["Inventory"]["SpecialItems"], "standalone map")
    assert_true("Shield" in state["Inventory"]["SpecialItems"], "standalone shield")
    assert_equal(len(state["Inventory"]["BackpackItems"]), 3, "standalone backpack supplies")


def test_book5_setup_validation() -> None:
    try:
        lonewolf_redux.clean_book5_equipment_choices(
            ["dagger", "sword", "spear", "mace", "shield"]
        )
    except ValueError:
        return
    raise AssertionError("Book 5 setup accepted more than four equipment choices")


def main() -> int:
    test_book4_to_book5_campaign_setup()
    test_standalone_book5_creation()
    test_book5_setup_validation()
    print("Book 5 setup smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke-test Book 4 setup and carry-forward rules."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book4-setup-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book4-setup-last-save.txt"


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


def fresh_book3_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book3_character_state(
        name="Book Four Smoke",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=["padded-leather-waistcoat", "axe"],
    )
    assistant.inventory["BackpackItems"].append("Crystal Star Pendant")
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


BOOK4_CHOICES = [
    "dagger",
    "spear",
    "two-potions-of-laumspur",
    "five-special-rations",
    "chainmail-waistcoat",
    "shield",
]


def test_book3_to_book4_campaign_setup() -> None:
    assistant = fresh_book3_assistant()
    assistant.inventory["GoldCrowns"] = 49
    assistant.inventory["Nobles"] = 49
    start_max_endurance = int(assistant.character["EnduranceMax"])
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 3)

    quiet(
        assistant.continue_completed_book,
        kai_discipline="Weaponskill",
        book4_gold_roll=9,
        book4_equipment_choices=BOOK4_CHOICES,
        book4_weapon_exchanges=["Axe"],
    )

    assert_equal(assistant.character["BookNumber"], 4, "current book")
    assert_equal(assistant.state["CurrentSection"], 1, "current section")
    assert_true(3 in assistant.character["CompletedBooks"], "Book 3 completed")
    assert_true("Weaponskill" in assistant.character["KaiDisciplines"], "new Kai Discipline")
    assert_equal(len(assistant.character["KaiDisciplines"]), 6, "six Kai Disciplines")
    assert_equal(assistant.inventory["GoldCrowns"], 50, "gold cap")
    assert_true("Crystal Star Pendant" in assistant.inventory["BackpackItems"], "Backpack item carried")
    assert_equal(len(assistant.inventory["BackpackItems"]), 8, "Backpack carry plus Book 4 supplies fills slots")
    assert_true("Map of the Southlands" in assistant.inventory["SpecialItems"], "Book 4 map added")
    assert_true("Badge of Rank" in assistant.inventory["SpecialItems"], "Badge of Rank added")
    assert_true("Padded Leather Waistcoat" in assistant.inventory["SpecialItems"], "Book 3 armour carried")
    assert_true("Chainmail Waistcoat" in assistant.inventory["SpecialItems"], "Book 4 chainmail added")
    assert_equal(assistant.character["EnduranceMax"], start_max_endurance + 4, "Chainmail stacks with Padded Leather")
    assert_true(assistant.automation_flags["book4BadgeOfRank"], "Badge story flag set")
    assert_equal(assistant.automation_flags["book4WildlandsHuntingSuppressed"], False, "Hunting starts available")
    assert_equal(assistant.state["CurrentBookStats"]["BookNumber"], 4, "Book 4 stats started")


def test_standalone_book4_creation() -> None:
    state = lonewolf_redux.create_book4_character_state(
        name="Fresh Book Four",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=2,
        endurance_roll=3,
        gold_roll=4,
        weaponskill_roll=5,
        equipment_choices=BOOK4_CHOICES,
    )

    assert_equal(state["Character"]["BookNumber"], 4, "standalone book")
    assert_equal(state["Character"]["CombatSkillCurrent"], 12, "standalone CS")
    assert_equal(state["Character"]["EnduranceCurrent"], 27, "standalone END with chainmail")
    assert_equal(state["Inventory"]["GoldCrowns"], 14, "standalone gold")
    assert_equal(state["Inventory"]["Weapons"], ["Dagger", "Spear"], "standalone weapons")
    assert_equal(len(state["Inventory"]["BackpackItems"]), 7, "standalone backpack supplies")
    assert_true("Map of the Southlands" in state["Inventory"]["SpecialItems"], "standalone map")
    assert_true("Badge of Rank" in state["Inventory"]["SpecialItems"], "standalone badge")
    assert_true("Chainmail Waistcoat" in state["Inventory"]["SpecialItems"], "standalone chainmail")
    assert_true("Shield" in state["Inventory"]["SpecialItems"], "standalone shield")


def test_book4_setup_validation() -> None:
    try:
        lonewolf_redux.clean_book4_equipment_choices(["dagger", "spear"])
    except ValueError:
        return
    raise AssertionError("Book 4 setup accepted fewer than six equipment choices")


def main() -> int:
    test_book3_to_book4_campaign_setup()
    test_standalone_book4_creation()
    test_book4_setup_validation()
    print("Book 4 setup smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

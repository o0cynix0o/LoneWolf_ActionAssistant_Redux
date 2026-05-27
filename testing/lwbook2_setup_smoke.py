#!/usr/bin/env python3
"""Smoke-test Book 2 setup and start-state rules."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book2-setup-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book2-setup-last-save.txt"


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Book Two Smoke",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=9,
        starting_find_roll=6,
        weaponskill_roll=5,
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


def test_book1_to_book2_campaign_setup() -> None:
    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 48
    assistant.inventory["Nobles"] = 48
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 1)

    quiet(
        assistant.continue_completed_book,
        kai_discipline="Mindshield",
        book2_gold_roll=9,
        book2_armoury_choices=["two-meals", "shield"],
    )

    assert_equal(assistant.character["BookNumber"], 2, "current book")
    assert_equal(assistant.state["CurrentSection"], 1, "current section")
    assert_true(1 in assistant.character["CompletedBooks"], "Book 1 completed")
    assert_true("Mindshield" in assistant.character["KaiDisciplines"], "new Kai Discipline")
    assert_equal(len(assistant.character["KaiDisciplines"]), 6, "six Kai Disciplines")
    assert_equal(assistant.inventory["GoldCrowns"], 50, "gold cap")
    assert_true("Healing Potion" in assistant.inventory["BackpackItems"], "Book 1 Backpack Item carried")
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), 3, "carried Meal plus two armoury Meals")
    assert_true("Map of Sommerlund" in assistant.inventory["SpecialItems"], "Map retained")
    assert_true("Seal of Hammerdal" in assistant.inventory["SpecialItems"], "Seal added")
    assert_true("Shield" in assistant.inventory["SpecialItems"], "Shield added")
    assert_equal(assistant.state["CurrentBookStats"]["BookNumber"], 2, "Book 2 stats started")
    assert_equal(assistant.state["CurrentBookStats"]["StartingGoldCrowns"], 50, "Book 2 starting gold")


def test_book2_weapon_exchange() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 1)

    quiet(
        assistant.continue_completed_book,
        kai_discipline="Mindshield",
        book2_gold_roll=0,
        book2_armoury_choices=["spear", "broadsword"],
        book2_weapon_exchanges=["Axe", "Sword"],
    )

    assert_equal(assistant.inventory["Weapons"], ["Spear", "Broadsword"], "exchanged weapons")


def test_standalone_book2_creation() -> None:
    state = lonewolf_redux.create_book2_character_state(
        name="Fresh Book Two",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=2,
        endurance_roll=3,
        gold_roll=4,
        weaponskill_roll=5,
        armoury_choices=["sword", "healing-potion"],
    )

    assert_equal(state["Character"]["BookNumber"], 2, "standalone book")
    assert_equal(state["Character"]["CombatSkillCurrent"], 12, "standalone CS")
    assert_equal(state["Character"]["EnduranceCurrent"], 23, "standalone END")
    assert_equal(state["Inventory"]["GoldCrowns"], 14, "standalone gold")
    assert_equal(state["Inventory"]["Weapons"], ["Sword"], "standalone weapon")
    assert_equal(state["Inventory"]["BackpackItems"], ["Healing Potion"], "standalone backpack")
    assert_equal(state["Inventory"]["SpecialItems"], ["Map of Sommerlund", "Seal of Hammerdal"], "standalone specials")
    assert_equal(state["Character"]["CompletedBooks"], [], "no campaign completion")


def main() -> int:
    test_book1_to_book2_campaign_setup()
    test_book2_weapon_exchange()
    test_standalone_book2_creation()
    print("Book 2 setup smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

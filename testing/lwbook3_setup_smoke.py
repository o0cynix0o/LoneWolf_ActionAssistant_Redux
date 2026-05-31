#!/usr/bin/env python3
"""Smoke-test Book 3 setup and start-state rules."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book3-setup-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book3-setup-last-save.txt"


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_book2_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book2_character_state(
        name="Book Three Smoke",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        armoury_choices=["sword", "two-meals"],
    )
    assistant.inventory["BackpackItems"].append("Crystal Star Pendant")
    assistant.inventory["SpecialItems"].append("Sommerswerd")
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


def test_book2_to_book3_campaign_setup() -> None:
    assistant = fresh_book2_assistant()
    assistant.inventory["GoldCrowns"] = 49
    assistant.inventory["Nobles"] = 49
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 2)

    quiet(
        assistant.continue_completed_book,
        kai_discipline="Weaponskill",
        weaponskill_roll=6,
        book3_gold_roll=9,
        book3_equipment_choices=["padded-leather-waistcoat", "special-rations"],
    )

    assert_equal(assistant.character["BookNumber"], 3, "current book")
    assert_equal(assistant.state["CurrentSection"], 1, "current section")
    assert_true(2 in assistant.character["CompletedBooks"], "Book 2 completed")
    assert_true("Weaponskill" in assistant.character["KaiDisciplines"], "new Kai Discipline")
    assert_equal(assistant.character["WeaponskillWeapon"], "Axe", "transition Weaponskill weapon")
    assert_equal(len(assistant.character["KaiDisciplines"]), 6, "six Kai Disciplines")
    assert_equal(assistant.inventory["GoldCrowns"], 50, "gold cap")
    assert_true("Crystal Star Pendant" in assistant.inventory["BackpackItems"], "Backpack item carried")
    assert_true("Meal" in assistant.inventory["BackpackItems"], "Special Rations stored as Meal")
    assert_true("Map of Kalte" in assistant.inventory["SpecialItems"], "Map of Kalte added")
    assert_true("Padded Leather Waistcoat" in assistant.inventory["SpecialItems"], "Padded Leather added")
    assert_true(assistant.automation_flags["book3WinterGear"], "winter gear story flag")
    assert_true(assistant.automation_flags["kalteHuntingSuppressed"], "Kalte Hunting suppression flag")
    assert_equal(assistant.state["CurrentBookStats"]["BookNumber"], 3, "Book 3 stats started")
    assert_equal(assistant.state["CurrentBookStats"]["StartingGoldCrowns"], 50, "Book 3 starting gold")


def test_standalone_book3_creation() -> None:
    state = lonewolf_redux.create_book3_character_state(
        name="Fresh Book Three",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=2,
        endurance_roll=3,
        gold_roll=4,
        weaponskill_roll=5,
        equipment_choices=["axe", "potion-of-laumspur"],
    )

    assert_equal(state["Character"]["BookNumber"], 3, "standalone book")
    assert_equal(state["Character"]["CombatSkillCurrent"], 12, "standalone CS")
    assert_equal(state["Character"]["EnduranceCurrent"], 23, "standalone END")
    assert_equal(state["Inventory"]["GoldCrowns"], 14, "standalone gold")
    assert_equal(state["Inventory"]["Weapons"], ["Axe"], "standalone weapon")
    assert_equal(state["Inventory"]["BackpackItems"], ["Potion of Laumspur (+4 END)"], "standalone backpack")
    assert_equal(state["Inventory"]["SpecialItems"], ["Map of Kalte"], "standalone specials")
    assert_equal(state["Character"]["CompletedBooks"], [], "no campaign completion")
    assert_true(state["Automation"]["Flags"]["book3WinterGear"], "winter gear flag")


def test_book3_repeat_and_item_rules() -> None:
    assistant = fresh_book2_assistant()
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 2)
    quiet(
        assistant.continue_completed_book,
        kai_discipline="Weaponskill",
        book3_gold_roll=0,
        book3_equipment_choices=["padded-leather-waistcoat", "special-rations"],
    )
    start_inventory = lonewolf_redux.json_clone(assistant.inventory)
    start_endurance_max = int(assistant.character["EnduranceMax"])
    quiet(assistant.set_section, 350)
    assert_true(assistant.book_completion_payload().get("Active"), "Book 3 completion screen active")
    assistant.inventory["BackpackItems"] = ["Baknar Oil"]
    quiet(assistant.use_item, "backpack", "Baknar Oil")
    assert_true(assistant.automation_flags["baknarOilApplied"], "Baknar Oil sets flag")
    assistant.inventory["SpecialItems"] = ["Bone Sword"]
    assistant.inventory["Weapons"] = []
    assistant.combat["Active"] = False
    quiet(assistant.start_combat, ["combat", "start", "Practice", "10", "10"])
    assert_equal(assistant.combat["ActiveWeapon"], "Bone Sword", "Bone Sword can be active weapon")
    assert_equal(
        assistant.combat_weapon_modifier_and_notes()[0],
        1,
        "Bone Sword gets Kalte bonus",
    )

    assistant.character["EnduranceCurrent"] = 1
    assistant.inventory["BackpackItems"] = ["Spent"]
    quiet(assistant.repeat_completed_book)
    assert_equal(assistant.state["CurrentSection"], 1, "Book 3 repeat starts at section 1")
    assert_equal(assistant.inventory, start_inventory, "Book 3 repeat restores starting inventory")
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance_max, "Book 3 repeat restores END")
    assert_true(3 in assistant.character["CompletedBooks"], "Book 3 repeat preserves completed-book history")


def main() -> int:
    test_book2_to_book3_campaign_setup()
    test_standalone_book3_creation()
    test_book3_repeat_and_item_rules()
    print("Book 3 setup smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

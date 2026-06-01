#!/usr/bin/env python3
"""Smoke-test Book 3 playable helper data."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book3-playable-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book3-playable-last-save.txt"


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant(
    disciplines: list[str] | None = None,
    equipment_choices: list[str] | None = None,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book3_character_state(
        name="Book Three Pipeline",
        kai_disciplines=disciplines
        or ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=equipment_choices or ["sword", "special-rations"],
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


def route_check_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, check_id: str) -> dict:
    for check in assistant.current_section_flow_payload()["RouteChecks"]:
        if check["Id"] == check_id:
            return check
    raise AssertionError(f"route check {check_id!r} not found")


def test_book3_meals_failure_and_completion() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    quiet(assistant.set_section, 132)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 132 consumes Backpack Meal")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 132)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 132 charges END without Meal")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 61)
    assert_true(assistant.death_active(), "section 61 opens recovery state")
    assert_equal(assistant.automation["DeathState"]["Type"], "Failure", "section 61 is recorded as failure")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 61 does not kill Lone Wolf")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 350)
    assert_true(3 in assistant.character["CompletedBooks"], "section 350 completes Book 3")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "Book 3 success ending")


def test_book3_loot_and_route_checks() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 4)
    quiet(assistant.apply_flow_loot, "bone-sword")
    quiet(assistant.apply_flow_loot, "blue-stone-disc")
    assert_true("Bone Sword" in assistant.inventory["SpecialItems"], "section 4 adds Bone Sword")
    assert_true("Blue Stone Disc" in assistant.inventory["SpecialItems"], "section 4 adds Blue Stone Disc")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 8)
    quiet(assistant.apply_flow_loot, "baknar-oil")
    assert_true("Baknar Oil" in assistant.inventory["BackpackItems"], "section 8 adds Baknar Oil")
    quiet(assistant.use_item, "backpack", "Baknar Oil")
    assert_true(assistant.automation_flags["baknarOilApplied"], "Baknar Oil use sets flag")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Potion of Laumspur (+4 END)"]
    quiet(assistant.set_section, 139)
    matched = route_check_by_id(assistant, "139-red-laumspur")["MatchedOutcome"]
    assert_equal(matched["Route"], 239, "regular Laumspur does not satisfy Red Laumspur")
    assistant.inventory["BackpackItems"] = ["Red Potion of Laumspur"]
    matched = route_check_by_id(assistant, "139-red-laumspur")["MatchedOutcome"]
    assert_equal(matched["Route"], 116, "Red Laumspur route matches")


def test_book3_roll_helpers() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 291)
    flow = assistant.current_section_flow_payload()
    roll = flow["Entry"].get("roll", {})
    assert_equal(roll.get("summary"), "Random next-day hazard at The Rock.", "section 291 roll summary")
    assert_equal(quiet(assistant.roll_current_section, 4)["Route"], 103, "section 291 low roll route")
    assert_equal(quiet(assistant.roll_current_section, 5)["Route"], 220, "section 291 high roll route")


def test_book3_combat_helpers() -> None:
    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"])
    assistant.inventory["SpecialItems"] = ["Sommerswerd"]
    quiet(assistant.set_section, 99)
    quiet(assistant.start_section_combat, "99-helghast")
    assert_true(assistant.combat["EnemyImmune"], "section 99 Helghast immune to Mindblast")
    assert_true(assistant.combat["DoubleEnemyLossWithSommerswerd"], "section 99 doubles Sommerswerd damage")
    base_end = int(assistant.character["EnduranceCurrent"])
    quiet(assistant.combat_round, ["combat", "round", "0"])
    assert_true(
        int(assistant.character["EnduranceCurrent"]) <= base_end - 2,
        "section 99 applies no-Mindshield round loss",
    )

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"])
    assistant.inventory["Weapons"] = ["Sword"]
    quiet(assistant.set_section, 137)
    quiet(assistant.start_section_combat, "137-ice-barbarian-and-doomwolf")
    assert_equal(
        assistant.combat_skill_for_round(),
        int(assistant.character["CombatSkillCurrent"]) + 1,
        "section 137 gives only +1 net Mindblast bonus",
    )

    assistant = fresh_assistant()
    quiet(assistant.set_section, 164)
    quiet(assistant.start_section_combat, "164-akraa-neonor")
    assert_equal(assistant.combat["WinWithinRounds"], 5, "section 164 has five-round timer")
    assert_equal(assistant.combat["WinWithinRoute"], 272, "section 164 fast victory route")
    assert_equal(assistant.combat["TooLateRoute"], 324, "section 164 slow victory route")


def main() -> int:
    test_book3_meals_failure_and_completion()
    test_book3_loot_and_route_checks()
    test_book3_roll_helpers()
    test_book3_combat_helpers()
    print("Book 3 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

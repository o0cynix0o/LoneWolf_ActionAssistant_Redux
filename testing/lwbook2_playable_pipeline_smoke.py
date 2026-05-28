#!/usr/bin/env python3
"""Smoke-test Book 2 playable automation, routes, and combat helpers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book2-playable-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book2-playable-last-save.txt"


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant(
    disciplines: list[str] | None = None,
    armoury_choices: list[str] | None = None,
    weaponskill_roll: int = 5,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book2_character_state(
        name="Book Two Pipeline",
        kai_disciplines=disciplines
        or ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Weaponskill"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=weaponskill_roll,
        armoury_choices=armoury_choices or ["sword", "two-meals"],
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


def assert_matched_route(
    assistant: lonewolf_redux.LoneWolfReduxAssistant,
    check_id: str,
    expected: int | None,
    label: str,
) -> None:
    matched = route_check_by_id(assistant, check_id)["MatchedOutcome"]
    actual = matched["Route"] if matched else None
    assert_equal(actual, expected, label)


def set_combat_history(assistant: lonewolf_redux.LoneWolfReduxAssistant) -> None:
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 2,
            "Outcome": "Victory",
            "EnemyName": "Smoke Test Raider",
            "Rounds": [
                {"PlayerLoss": 3, "EnemyLoss": 4},
                {"PlayerLoss": 1, "EnemyLoss": 6},
            ],
            "RoundCount": 2,
        },
        {
            "BookNumber": 1,
            "Outcome": "Victory",
            "EnemyName": "Ignored Book 1 Fight",
            "Rounds": [{"PlayerLoss": 8, "EnemyLoss": 4}],
            "RoundCount": 1,
        },
    ]


def test_chainmail_loss_and_required_meals() -> None:
    assistant = fresh_assistant(armoury_choices=["chainmail-waistcoat", "two-meals"])
    assistant.character["EnduranceCurrent"] = assistant.character["EnduranceMax"]
    starting_max = assistant.character["EnduranceMax"]
    quiet(assistant.set_section, 78)
    assert_true("Chainmail Waistcoat" not in assistant.inventory["SpecialItems"], "section 78 removes Chainmail")
    assert_equal(assistant.character["EnduranceMax"], starting_max - 4, "section 78 lowers END max")
    assert_equal(assistant.character["Book2Setup"]["ChainmailApplied"], False, "chainmail setup flag cleared")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"])
    assistant.inventory["BackpackItems"] = []
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 284)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 284 ignores Hunting and charges missing Meal")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    quiet(assistant.set_section, 321)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 321 consumes Backpack food")


def test_route_costs_and_pass_checks() -> None:
    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 12
    quiet(assistant.set_section, 75)
    assert_matched_route(assistant, "75-gold-gte-10", 142, "section 75 pass purchase route")
    quiet(assistant.follow_route, 142)
    assert_equal(assistant.inventory["GoldCrowns"], 2, "section 75 route removes 10 Gold")
    assert_true("White Pass" in assistant.inventory["SpecialItems"], "section 75 route adds White Pass")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    assistant.inventory["GoldCrowns"] = 2
    quiet(assistant.set_section, 346)
    quiet(assistant.follow_route, 280)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 346 consumes Meal before Gold")
    assert_equal(assistant.inventory["GoldCrowns"], 2, "section 346 preserves Gold when Meal is used")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["GoldCrowns"] = 2
    quiet(assistant.set_section, 346)
    quiet(assistant.follow_route, 280)
    assert_equal(assistant.inventory["GoldCrowns"], 1, "section 346 pays Gold when no Meal is carried")

    assistant = fresh_assistant()
    assistant.inventory["SpecialItems"] = ["Access Papers", "Seal of Hammerdal"]
    quiet(assistant.set_section, 62)
    assert_matched_route(assistant, "62-documents-or-seal", 126, "section 62 access papers route")

    assistant.inventory["SpecialItems"] = ["Red Pass"]
    quiet(assistant.set_section, 246)
    assert_matched_route(assistant, "246-pass", 202, "section 246 Red Pass route")


def test_section_240_recovers_combat_loss_only() -> None:
    assistant = fresh_assistant()
    max_endurance = int(assistant.character["EnduranceMax"])
    assistant.character["EnduranceCurrent"] = max_endurance - 8
    set_combat_history(assistant)
    quiet(assistant.set_section, 240)
    messages = quiet(assistant.apply_route_actions, 29)
    assert_equal(
        assistant.character["EnduranceCurrent"],
        max_endurance - 6,
        "section 240 without Healing restores half of Book 2 combat END loss",
    )
    assert_true(
        any("combat END loss 4" in message for message in messages),
        "section 240 no-Healing receipt reports combat loss basis",
    )

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"])
    max_endurance = int(assistant.character["EnduranceMax"])
    assistant.character["EnduranceCurrent"] = max_endurance - 8
    set_combat_history(assistant)
    quiet(assistant.set_section, 240)
    quiet(assistant.apply_route_actions, 29)
    assert_equal(
        assistant.character["EnduranceCurrent"],
        max_endurance,
        "section 240 with Healing restores END to maximum",
    )


def test_book2_loot_and_item_effects() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = []
    quiet(assistant.set_section, 55)
    quiet(assistant.apply_flow_loot, "buy-broadsword")
    assert_equal(assistant.inventory["GoldCrowns"], 3, "section 55 Broadsword price")
    assert_equal(assistant.inventory["Weapons"], ["Broadsword"], "section 55 Broadsword loot")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 40)
    assert_equal(assistant.character["EnduranceCurrent"], assistant.character["EnduranceMax"], "section 40 restores END")
    assert_true(
        "Potent Laumspur Potion (+5 END)" in assistant.inventory["BackpackItems"],
        "section 40 adds potent Laumspur potion",
    )
    assistant.character["EnduranceCurrent"] -= 5
    quiet(assistant.use_item, "backpack", "Potent Laumspur")
    assert_equal(assistant.character["EnduranceCurrent"], assistant.character["EnduranceMax"], "potent Laumspur restores 5 END")


def test_book2_combat_helpers() -> None:
    assistant = fresh_assistant(weaponskill_roll=5)
    assistant.inventory["Weapons"] = []
    assistant.inventory["SpecialItems"] = ["Sommerswerd"]
    quiet(assistant.set_section, 5)
    quiet(assistant.start_section_combat, "5-wounded-helghast")
    assert_equal(assistant.combat_skill_for_round(), 24, "Sommerswerd plus Weaponskill Sword gives +10 CS")

    assistant = fresh_assistant(weaponskill_roll=1)
    assistant.inventory["Weapons"] = []
    assistant.inventory["SpecialItems"] = ["Magic Spear"]
    quiet(assistant.set_section, 106)
    quiet(assistant.start_section_combat, "106-helghast")
    assert_equal(assistant.combat_skill_for_round(), 16, "Magic Spear uses Spear Weaponskill only")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"])
    assistant.character["EnduranceCurrent"] = 19
    starting_endurance = assistant.character["EnduranceCurrent"]
    quiet(assistant.set_section, 276)
    quiet(assistant.start_section_combat, "276-arm-wrestling")
    assistant.character["EnduranceCurrent"] = 3
    assistant.combat["EnemyEnduranceCurrent"] = 0
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.character["EnduranceCurrent"], starting_endurance, "arm-wrestling restores pre-contest END")
    assert_equal(assistant.state["CurrentSection"], 305, "arm-wrestling victory route")
    assert_equal(assistant.inventory["GoldCrowns"], 20, "section 305 victory Gold")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"])
    assistant.inventory["SpecialItems"] = []
    quiet(assistant.set_section, 106)
    quiet(assistant.start_section_combat, "106-helghast")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    quiet(assistant.route_after_combat_round)
    assert_true("Magic Spear" in assistant.inventory["SpecialItems"], "section 106 victory adds Magic Spear")
    assert_equal(assistant.state["CurrentSection"], 320, "section 106 victory route")


def test_book2_terminal_and_completion() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 275)
    assert_true(assistant.death_active(), "section 275 registers death")
    assert_equal(assistant.character["EnduranceCurrent"], 0, "terminal death sets END to zero")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 350)
    assert_true(2 in assistant.character["CompletedBooks"], "section 350 completes Book 2")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "Book 2 success ending")


def main() -> int:
    test_chainmail_loss_and_required_meals()
    test_route_costs_and_pass_checks()
    test_section_240_recovers_combat_loss_only()
    test_book2_loot_and_item_effects()
    test_book2_combat_helpers()
    test_book2_terminal_and_completion()
    print("Book 2 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke-test Book 4 playable helper data."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "book4-playable-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book4-playable-last-save.txt"


BOOK4_CHOICES = [
    "dagger",
    "spear",
    "two-potions-of-laumspur",
    "five-special-rations",
    "chainmail-waistcoat",
    "shield",
]


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


def fresh_assistant(
    disciplines: list[str] | None = None,
    equipment_choices: list[str] | None = None,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book4_character_state(
        name="Book Four Pipeline",
        kai_disciplines=disciplines
        or ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mind Over Matter"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=equipment_choices or BOOK4_CHOICES,
    )
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def loss_choice_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, choice_id: str) -> dict:
    for choice in assistant.current_section_flow_payload()["LossChoices"]:
        if choice["Id"] == choice_id:
            return choice
    raise AssertionError(f"loss choice {choice_id!r} not found")


def test_book4_meals_hunting_and_mines() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 126)
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "Hunting preserves Meal before Wildlands")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "Hunting prevents meal END loss")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    quiet(assistant.set_section, 25)
    quiet(assistant.set_section, 141)
    assert_equal(assistant.inventory["BackpackItems"], [], "Wildlands suppresses Hunting and consumes Meal")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 185)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "Mines suppress Hunting and charge END")


def test_book4_loss_and_backpack_replacement() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["Weapons"] = ["Dagger"]
    quiet(assistant.set_section, 22)
    choice = loss_choice_by_id(assistant, "drop-pack-item-or-weapon")
    assert_true(choice["Ready"], "section 22 loss choice ready")
    assert_equal(choice["Source"], "primary", "section 22 prefers Backpack Item")
    quiet(assistant.apply_section_loss, "drop-pack-item-or-weapon", "backpack", "Rope")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "section 22 removes selected Backpack Item")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["Weapons"] = ["Spear"]
    quiet(assistant.set_section, 22)
    choice = loss_choice_by_id(assistant, "drop-pack-item-or-weapon")
    assert_equal(choice["Source"], "fallback", "section 22 falls back to Weapon")
    quiet(assistant.apply_section_loss, "drop-pack-item-or-weapon", "weapon", "Spear")
    assert_equal(assistant.inventory["Weapons"], [], "section 22 removes selected fallback Weapon")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    quiet(assistant.set_section, 94)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 94 discards backpack contents")
    assert_equal(assistant.automation_flags["backpackAvailable"], False, "section 94 backpack unavailable")
    quiet(assistant.set_section, 167)
    assert_equal(assistant.automation_flags["backpackAvailable"], True, "section 167 gives replacement Backpack")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "section 167 adds one Meal to replacement Backpack")


def test_book4_underwater_and_special_combat() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 194)
    quiet(assistant.roll_current_section, 0)
    quiet(assistant.start_section_combat, "194-giant-meresquid")
    assert_equal(assistant.combat["OxygenSafeRounds"], 12, "0 roll plus Mind Over Matter gives 12 safe rounds")
    assert_equal(assistant.combat["VictoryRoute"], 32, "underwater fight victory route")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 333)
    quiet(assistant.start_section_combat, "333-vassagonian-horseman")
    assert_equal(
        assistant.combat["OneRoundComparisonRoutes"],
        {"playerLossGreater": 209, "enemyLossGreater": 220, "equal": 344},
        "section 333 one-round comparison routes",
    )


def test_book4_completion() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 350)
    assert_true(4 in assistant.character["CompletedBooks"], "section 350 completes Book 4")
    assert_true("Dagger of Vashna" in assistant.inventory["SpecialItems"], "section 350 adds Dagger of Vashna")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "Book 4 success ending")


def combat_route_values(value) -> list[int]:
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        routes: list[int] = []
        for item in value:
            routes.extend(combat_route_values(item))
        return routes
    if isinstance(value, dict):
        routes: list[int] = []
        for item in value.values():
            routes.extend(combat_route_values(item))
        return routes
    return []


def test_book4_combat_route_targets_match_source() -> None:
    data = json.loads((ROOT / "data" / "book4-section-flows.json").read_text(encoding="utf-8"))["4"]
    route_keys = {
        "victoryRoute",
        "defeatRoute",
        "evadeRoute",
        "flawlessVictoryRoute",
        "woundedVictoryRoute",
        "playerLossRoute",
        "oneRoundComparisonRoutes",
        "winWithinRoute",
        "tooLateRoute",
        "survivalRoute",
        "roundExceededRoute",
        "victoryChoices",
        "combatRollRoutes",
    }
    for section, entry in data.items():
        if not str(section).isdigit():
            continue
        source_routes = {int(route["Section"]) for route in entry.get("sourceRoutes", []) if "Section" in route}
        for preset in entry.get("combat", []):
            preset_routes: list[int] = []
            for key in route_keys:
                preset_routes.extend(combat_route_values(preset.get(key)))
            unexpected = sorted(set(preset_routes) - source_routes)
            if unexpected:
                raise AssertionError(
                    f"section {section} combat routes not present in source links: {unexpected}; source={sorted(source_routes)}"
                )


def main() -> int:
    test_book4_meals_hunting_and_mines()
    test_book4_loss_and_backpack_replacement()
    test_book4_underwater_and_special_combat()
    test_book4_completion()
    test_book4_combat_route_targets_match_source()
    print("Book 4 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

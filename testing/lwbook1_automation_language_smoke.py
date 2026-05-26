#!/usr/bin/env python3
"""Smoke-test Book 1 automation-language audit helpers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "automation-language-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "automation-language-last-save.txt"
DEFAULT_DISCIPLINES = ["Healing", "Camouflage", "Sixth Sense", "Tracking", "Weaponskill"]


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Automation Language Smoke",
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


def smoke_clear_loot_helpers() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 15)
    quiet(assistant.apply_flow_loot, "15-sword")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Sword"], "section 15 Sword loot")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 346)
    quiet(assistant.apply_flow_loot, "346-spear")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Spear"], "section 346 Spear loot")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 349)
    quiet(assistant.apply_flow_loot, "349-crystal-star-pendant")
    assert_true("Crystal Star Pendant" in assistant.inventory["SpecialItems"], "section 349 Pendant loot")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 193)
    quiet(assistant.apply_flow_loot, "193-scroll")
    assert_true("Scroll" in assistant.inventory["BackpackItems"], "section 193 Scroll Backpack Item")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 255)
    quiet(assistant.apply_flow_loot, "255-princes-sword")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Prince's Sword"], "section 255 Prince's Sword loot")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 267)
    quiet(assistant.apply_flow_loot, "267-message")
    quiet(assistant.apply_flow_loot, "267-dagger")
    assert_true("Message" in assistant.inventory["SpecialItems"], "section 267 Message Special Item")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Dagger"], "section 267 Dagger loot")


def smoke_section_258_gear_loss() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    assistant.inventory["BackpackItems"] = ["Meal", "Laumspur"]
    quiet(assistant.set_section, 258)
    assert_equal(assistant.inventory["Weapons"], [], "section 258 discards Weapons")
    assert_equal(assistant.inventory["BackpackItems"], [], "section 258 discards Backpack Items")
    assert_equal(assistant.inventory["HasBackpack"], False, "section 258 marks Backpack unavailable")


def smoke_section_46_sixth_sense_check() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 46)
    checks = assistant.current_section_flow_payload()["RouteChecks"]
    assert_equal(len(checks), 1, "section 46 route check count")
    assert_equal(checks[0]["MatchedOutcome"]["Route"], 296, "section 46 Sixth Sense route")

    assistant = fresh_assistant(["Healing", "Camouflage", "Hunting", "Tracking", "Weaponskill"])
    quiet(assistant.set_section, 46)
    check = assistant.current_section_flow_payload()["RouteChecks"][0]
    assert_equal(check["MatchedOutcome"], None, "section 46 no Sixth Sense has no matched optional route")


def smoke_route_gold_costs() -> None:
    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 15
    quiet(assistant.set_section, 12)
    quiet(assistant.follow_route, 262)
    assert_equal(assistant.inventory["GoldCrowns"], 5, "section 12 paid route removes 10 Gold Crowns")
    assert_equal(assistant.state["CurrentSection"], 262, "section 12 paid route target")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 15
    quiet(assistant.set_section, 12)
    quiet(assistant.follow_route, 247)
    assert_equal(assistant.inventory["GoldCrowns"], 15, "section 12 unpaid route preserves Gold Crowns")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 5
    quiet(assistant.set_section, 46)
    route = next(route for route in assistant.current_section_flow_payload()["SourceRoutes"] if route["Section"] == 246)
    assert_equal(route["EffectLabel"], "Pay 2 Gold Crowns", "section 46 paid route label")
    quiet(assistant.follow_route, 246)
    assert_equal(assistant.inventory["GoldCrowns"], 3, "section 46 accepted offer removes 2 Gold Crowns")
    assert_equal(assistant.state["CurrentSection"], 246, "section 46 accepted offer target")


def smoke_meal_rulings() -> None:
    assistant = fresh_assistant()
    start_meals = assistant.inventory["BackpackItems"].count("Meal")
    quiet(assistant.set_section, 115)
    quiet(assistant.follow_route, 150)
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), start_meals, "section 115 table Meal does not consume carried Meal")
    assert_equal(assistant.state["CurrentSection"], 150, "section 115 Meal route target")


def main() -> int:
    smoke_clear_loot_helpers()
    smoke_section_258_gear_loss()
    smoke_section_46_sixth_sense_check()
    smoke_route_gold_costs()
    smoke_meal_rulings()
    print("Book 1 automation-language smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

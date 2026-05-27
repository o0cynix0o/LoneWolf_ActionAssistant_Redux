#!/usr/bin/env python3
"""Broader Book 1 route-gauntlet playtest.

The gauntlet follows legal route links through risky Book 1 paths and checks
the assistant state at resource, item, death, and combat-adjacent edges.
"""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "route-gauntlet-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "route-gauntlet-last-save.txt"
DEFAULT_DISCIPLINES = ["Mindblast", "Camouflage", "Sixth Sense", "Tracking", "Healing"]


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant(
    disciplines: list[str] | None = None,
    *,
    combat_skill: int = 35,
    endurance: int = 60,
    gold: int | None = None,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Route Gauntlet",
        kai_disciplines=disciplines or DEFAULT_DISCIPLINES,
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=3,
        starting_find_roll=4,
        weaponskill_roll=6,
    )
    assistant.character["CombatSkillBase"] = combat_skill
    assistant.character["CombatSkillCurrent"] = combat_skill
    assistant.character["EnduranceMax"] = endurance
    assistant.character["EnduranceCurrent"] = endurance
    if gold is not None:
        assistant.inventory["GoldCrowns"] = gold
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


def follow_and_assert(assistant: lonewolf_redux.LoneWolfReduxAssistant, target: int) -> None:
    source = int(assistant.state["CurrentSection"])
    quiet(assistant.follow_route, target)
    assert_equal(assistant.state["CurrentSection"], target, f"legal route {source} -> {target}")


def follow_path(assistant: lonewolf_redux.LoneWolfReduxAssistant, route: list[int]) -> None:
    assert_equal(assistant.state["CurrentSection"], route[0], "route start")
    for target in route[1:]:
        follow_and_assert(assistant, target)


def route_check_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, check_id: str) -> dict[str, Any]:
    for check in assistant.current_section_flow_payload().get("RouteChecks", []):
        if check.get("Id") == check_id:
            return check
    raise AssertionError(f"route check {check_id!r} not found")


def assert_matched_route(assistant: lonewolf_redux.LoneWolfReduxAssistant, check_id: str, route: int | None, label: str) -> None:
    matched = route_check_by_id(assistant, check_id).get("MatchedOutcome")
    assert_equal(matched.get("Route") if matched else None, route, label)


def resolve_section_combat(assistant: lonewolf_redux.LoneWolfReduxAssistant, combat_id: str) -> None:
    quiet(assistant.start_section_combat, combat_id)
    assert_equal(assistant.combat["Active"], True, f"{combat_id} combat active")
    rounds = 0
    while assistant.combat.get("Active") and rounds < 20:
        quiet(assistant.combat_round, ["combat", "round", "9"])
        rounds += 1
    assert_equal(assistant.combat["Active"], False, f"{combat_id} combat resolved")
    assert_true(assistant.state["CombatHistory"], f"{combat_id} archived")


def assert_discarded_gear(assistant: lonewolf_redux.LoneWolfReduxAssistant, label: str) -> None:
    assert_equal(assistant.inventory["Weapons"], [], f"{label} clears Weapons")
    assert_equal(assistant.inventory["BackpackItems"], [], f"{label} clears Backpack Items")
    assert_equal(assistant.inventory["HasBackpack"], False, f"{label} removes Backpack")


def play_paid_ferryman_and_gourgaz_route() -> None:
    assistant = fresh_assistant()
    follow_path(assistant, [1, 141, 56, 222, 252, 70, 157, 167, 264, 97, 255])

    quiet(assistant.apply_flow_loot, "255-princes-sword")
    assert_true("Prince's Sword" in assistant.inventory["Weapons"], "section 255 Prince's Sword loot")
    resolve_section_combat(assistant, "255-gourgaz")
    assert_equal(assistant.state["CurrentSection"], 82, "section 255 Gourgaz victory route")

    start_meals = assistant.inventory["BackpackItems"].count("Meal")
    follow_path(assistant, [82, 235])
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), start_meals - 1, "section 235 consumes Meal without Hunting")
    follow_path(assistant, [235, 32, 176, 126, 46])
    assert_matched_route(assistant, "46-sixth-sense", 296, "section 46 Sixth Sense warning")

    start_gold = assistant.inventory["GoldCrowns"]
    follow_and_assert(assistant, 246)
    assert_equal(assistant.inventory["GoldCrowns"], start_gold - 2, "section 46 paid ferry route cost")
    resolve_section_combat(assistant, "246-drakkar")
    assert_equal(assistant.state["CurrentSection"], 197, "section 246 Drakkar victory route")

    quiet(assistant.apply_flow_loot, "197-drakkar")
    assert_true("Prince's Sword" in assistant.inventory["Weapons"], "section 197 preserves existing weapon choice")
    assert_equal(assistant.inventory["GoldCrowns"], start_gold - 2 + 6, "section 197 Gold Crowns loot")


def play_caravan_fare_and_bodyguard_evasion() -> None:
    assistant = fresh_assistant(gold=15)
    follow_path(assistant, [1, 141, 56, 222, 252, 70, 157, 167, 264, 6, 200, 78, 12])
    assert_matched_route(assistant, "12-gold-gte-10", 262, "section 12 enough Gold Crowns")

    follow_and_assert(assistant, 262)
    assert_equal(assistant.inventory["GoldCrowns"], 5, "section 12 caravan fare cost")
    follow_and_assert(assistant, 191)
    quiet(assistant.start_section_combat, "191-bodyguard")
    assert_equal(assistant.combat["Active"], True, "section 191 Bodyguard combat active")
    assert_equal(assistant.can_evade_combat_now(), True, "section 191 evasion available")
    quiet(assistant.evade_combat, ["combat", "evade", "0"])
    assert_equal(assistant.state["CurrentSection"], 234, "section 191 evasion route")
    assert_equal(assistant.death_active(), True, "section 234 death after evasion")


def play_vordak_gem_failure_and_backlash() -> None:
    route_to_nightmare_door = [1, 141, 56, 222, 252, 70, 157, 167, 264, 6, 200, 168, 64, 188, 303, 237, 265, 142, 102, 284, 71, 242, 9]

    assistant = fresh_assistant()
    follow_path(assistant, route_to_nightmare_door[:-1])
    assert_matched_route(assistant, "242-mindshield", 9, "section 242 no Mindshield route")
    follow_and_assert(assistant, 9)
    assert_matched_route(assistant, "9-vordak-gem", 292, "section 9 no Vordak Gem route")
    follow_and_assert(assistant, 292)
    assert_equal(assistant.death_state()["Type"], "Failure", "section 292 terminal failure")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Vordak Gem")
    follow_path(assistant, route_to_nightmare_door)
    start_endurance = assistant.character["EnduranceCurrent"]
    start_cs = assistant.character["CombatSkillCurrent"]
    assert_matched_route(assistant, "9-vordak-gem", 236, "section 9 Vordak Gem route")
    follow_and_assert(assistant, 236)
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance - 6, "section 236 END backlash")
    assert_equal(assistant.character["CombatSkillCurrent"], start_cs - 1, "section 236 permanent CS backlash")
    assert_true("Vordak Gem" not in assistant.inventory["BackpackItems"], "section 236 removes Vordak Gem")


def play_capture_escape_routes() -> None:
    route_to_capture = [1, 141, 56, 222, 140, 14, 106, 334, 162]

    assistant = fresh_assistant(["Mindblast", "Mind Over Matter", "Camouflage", "Sixth Sense", "Healing"])
    assistant.inventory["BackpackItems"].append("Torch")
    follow_path(assistant, route_to_capture)
    assert_discarded_gear(assistant, "section 162 capture")
    assert_matched_route(assistant, "162-mind-over-matter", 258, "section 162 Mind Over Matter escape")
    follow_and_assert(assistant, 258)
    assert_discarded_gear(assistant, "section 258 escape")

    assistant = fresh_assistant()
    follow_path(assistant, route_to_capture)
    assert_matched_route(assistant, "162-mind-over-matter", 127, "section 162 no Mind Over Matter route")
    follow_and_assert(assistant, 127)
    assert_equal(assistant.death_state()["Type"], "Death", "section 127 terminal death")


def play_explosion_endurance_thresholds() -> None:
    assistant = fresh_assistant(endurance=30)
    quiet(assistant.set_section, 231)
    follow_and_assert(assistant, 203)
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 203 high-END explosion loss")
    assert_matched_route(assistant, "203-end-gte-10", 80, "section 203 high-END route")

    assistant = fresh_assistant(endurance=15)
    quiet(assistant.set_section, 231)
    follow_and_assert(assistant, 203)
    assert_equal(assistant.character["EnduranceCurrent"], 5, "section 203 low-END explosion loss")
    assert_matched_route(assistant, "203-end-gte-10", 344, "section 203 low-END route")


def play_backpack_loss_and_side_loot_routes() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Torch")
    assistant.inventory["Weapons"].append("Sword")
    follow_path(assistant, [1, 141, 56, 222, 252, 70, 157, 167, 264, 6, 200, 168, 64, 188, 303, 237, 265, 142, 135, 223, 175, 182, 174])
    assert_discarded_gear(assistant, "section 174 river loss")

    assistant = fresh_assistant()
    follow_path(assistant, [1, 141, 333, 131, 241, 349])
    quiet(assistant.apply_flow_loot, "349-crystal-star-pendant")
    assert_true("Crystal Star Pendant" in assistant.inventory["SpecialItems"], "section 349 Pendant loot")
    follow_and_assert(assistant, 293)


def main() -> int:
    reset_saves()
    play_paid_ferryman_and_gourgaz_route()
    play_caravan_fare_and_bodyguard_evasion()
    play_vordak_gem_failure_and_backlash()
    play_capture_escape_routes()
    play_explosion_endurance_thresholds()
    play_backpack_loss_and_side_loot_routes()
    print("Book 1 route gauntlet playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

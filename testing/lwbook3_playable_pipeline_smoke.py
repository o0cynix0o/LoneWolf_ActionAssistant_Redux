#!/usr/bin/env python3
"""Smoke-test Book 3 playable helper data."""

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
    quiet(assistant.set_section, 29)
    assert_equal(quiet(assistant.roll_current_section, 0)["Route"], 312, "section 29 roll 0 route")
    assert_equal(quiet(assistant.roll_current_section, 1)["Route"], 226, "section 29 roll 1 route")
    assert_equal(quiet(assistant.roll_current_section, 5)["Route"], 266, "section 29 roll 5 route")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 54)
    result = quiet(assistant.roll_current_section, 2)
    assert_equal(result["Total"], 5, "section 54 Mindblast modifier total")
    assert_equal(result["Route"], 268, "section 54 modified route")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 94)
    result = quiet(assistant.roll_current_section, 0)
    assert_equal(result["Route"], 176, "section 94 survival route")
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 94 survival loses END")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 94)
    quiet(assistant.roll_current_section, 7)
    assert_true(assistant.death_active(), "section 94 fatal roll opens death state")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 258)
    result = quiet(assistant.roll_current_section, 0)
    assert_equal(result["Total"], 8, "section 258 Hunting/Sixth Sense modifier total")
    assert_equal(result["Route"], 63, "section 258 bracelet route")
    assert_equal(assistant.character["EnduranceCurrent"], 12, "section 258 loses END equal to total")

    quiet(assistant.set_section, 291)
    flow = assistant.current_section_flow_payload()
    roll = flow["Entry"].get("roll", {})
    assert_equal(roll.get("summary"), "Random next-day hazard at The Rock.", "section 291 roll summary")
    assert_equal(quiet(assistant.roll_current_section, 4)["Route"], 103, "section 291 low roll route")
    assert_equal(quiet(assistant.roll_current_section, 5)["Route"], 220, "section 291 high roll route")


def test_book3_all_roll_helpers_are_app_safe() -> None:
    data = json.loads((ROOT / "data" / "book3-section-flows.json").read_text(encoding="utf-8"))["3"]
    for section, entry in data.items():
        if not str(section).isdigit() or not isinstance(entry.get("roll"), dict):
            continue
        source_routes = {int(route["Section"]) for route in entry.get("sourceRoutes", []) if "Section" in route}
        for outcome in entry["roll"].get("outcomes", []):
            route = outcome.get("route")
            if route is not None and int(route) not in source_routes:
                raise AssertionError(f"section {section} roll route {route} is not present in source routes")
        for raw in range(10):
            assistant = fresh_assistant()
            quiet(assistant.set_section, int(section))
            result = quiet(assistant.roll_current_section, raw)
            route = result.get("Route")
            if route is not None and int(route) not in source_routes:
                raise AssertionError(f"section {section} raw {raw} produced non-source route {route}")
            if result.get("Ending") in {"death", "failure"}:
                assert_true(assistant.death_active(), f"section {section} raw {raw} records terminal roll")


def test_book3_gold_distraction_helper() -> None:
    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 10
    quiet(assistant.set_section, 152)
    payload = assistant.current_section_flow_payload()["GoldDistraction"]
    assert_true(payload["Available"], "section 152 exposes Gold distraction helper")
    result = quiet(assistant.play_gold_distraction, 3, 2)
    assert_equal(result["Total"], 2, "section 152 distraction uses rolled total")
    assert_equal(assistant.inventory["GoldCrowns"], 7, "section 152 spends thrown Gold on success")
    assert_equal(assistant.state["CurrentSection"], 319, "section 152 success routes to 319")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 10
    quiet(assistant.set_section, 152)
    result = quiet(assistant.play_gold_distraction, 3, 4)
    assert_equal(result["Success"], False, "section 152 failed distraction result")
    assert_equal(assistant.inventory["GoldCrowns"], 7, "section 152 spends thrown Gold on failure")
    assert_equal(assistant.state["CurrentSection"], 181, "section 152 failure routes to 181")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 10
    quiet(assistant.set_section, 152)
    result = quiet(assistant.play_gold_distraction, 10, 0)
    assert_equal(result["Total"], 10, "section 152 treats 0 as 10")
    assert_equal(assistant.state["CurrentSection"], 319, "section 152 ten Gold succeeds on roll 0")


def test_book3_direct_section_helpers() -> None:
    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 18)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 18 loses 3 END")
    assistant.inventory["Weapons"] = ["Sword"]
    quiet(assistant.apply_section_loss, "cyclone-weapon-loss", "weapon", "Sword")
    assert_equal(assistant.inventory["Weapons"], [], "section 18 weapon loss removes chosen weapon")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope", "Potion of Laumspur (+4 END)"]
    quiet(assistant.set_section, 16)
    quiet(assistant.apply_section_loss, "crushed-pack-item-1", "backpack", "Rope")
    quiet(assistant.apply_section_loss, "crushed-pack-item-2", "backpack", "Meal")
    assert_true("Rope" not in assistant.inventory["BackpackItems"], "section 16 removes first crushed item")
    assert_true("Meal" not in assistant.inventory["BackpackItems"], "section 16 removes second crushed item")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    quiet(assistant.set_section, 12)
    quiet(assistant.apply_flow_loot, "food")
    quiet(assistant.apply_flow_loot, "sleeping-furs")
    quiet(assistant.apply_flow_loot, "rope")
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), 2, "section 12 food adds two net Meals")
    assert_true("Sleeping Furs (2 spaces)" in assistant.inventory["BackpackItems"], "section 12 adds sleeping furs")
    assert_true("Rope" in assistant.inventory["BackpackItems"], "section 12 adds rope")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 27)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "section 27 cold loss without Baknar Oil")
    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    assistant.automation_flags["baknarOilApplied"] = True
    quiet(assistant.set_section, 27)
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 27 Baknar Oil prevents cold loss")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 55)
    assert_equal(assistant.character["EnduranceCurrent"], 15, "section 55 loses 5 END")
    assert_equal(assistant.character["CombatSkillBase"], 12, "section 55 permanently lowers base CS")
    assert_equal(assistant.character["CombatSkillCurrent"], 12, "section 55 lowers current CS")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    quiet(assistant.set_section, 49)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 49 stores Backpack gear")
    quiet(assistant.set_section, 212)
    assert_equal(assistant.inventory["BackpackItems"], ["Meal", "Rope"], "section 212 restores Backpack gear")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    quiet(assistant.set_section, 237)
    assert_equal(assistant.inventory["BackpackItems"], [], "section 237 consumes a Backpack Meal")
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 237)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 237 loses END without Meal")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 294)
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "section 294 keeps one Meal when two are required")
    assert_equal(assistant.character["EnduranceCurrent"], 14, "section 294 loses END without two Meals")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 311)
    quiet(assistant.apply_flow_loot, "distilled-alether")
    quiet(assistant.use_item, "backpack", "Potion of Alether")
    assert_equal(assistant.character["CombatSkillCurrent"], 18, "section 311 Alether use adds 4 CS")

    assistant = fresh_assistant()
    assistant.inventory["SpecialItems"] = ["Ornate Silver Key"]
    quiet(assistant.set_section, 303)
    assert_true("Ornate Silver Key" not in assistant.inventory["SpecialItems"], "section 303 consumes Ornate Silver Key")


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


def test_book3_combat_route_targets_match_source() -> None:
    data = json.loads((ROOT / "data" / "book3-section-flows.json").read_text(encoding="utf-8"))["3"]
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


def test_book3_combat_route_semantics() -> None:
    data = json.loads((ROOT / "data" / "book3-section-flows.json").read_text(encoding="utf-8"))["3"]
    expected: dict[str, dict[str, object]] = {
        "14": {"victoryRoute": 309},
        "32": {"victoryRoute": 25, "playerLossRoute": 66},
        "68": {"victoryRoute": 186},
        "78": {"victoryRoute": 245},
        "83": {"victoryRoute": 313, "enemyImmune": True},
        "88": {"victoryRoute": 269, "enemyImmune": True, "playerLossRandomCheck": True},
        "89": {"victoryRoute": 161},
        "99": {"victoryRoute": 230, "enemyImmune": True},
        "103": {"victoryRoute": 305},
        "106": {"victoryRoute": 338, "evadeRoute": 145, "enemyImmune": True},
        "108": {"victoryRoute": 282, "canEvade": True, "evadeAfterRounds": 1},
        "123": {"victoryRoute": 174, "playerLossRoute": 66},
        "137": {"victoryRoute": 28},
        "138": {"victoryRoute": 25, "playerLossRoute": 66, "evadeRoute": 277},
        "147": {"victoryRoute": 84, "playerLossRoute": 66},
        "158": {"oneRoundComparisonRoutes": {"playerLossGreater": 165, "enemyLossGreater": 271, "equal": 337}},
        "161": {"victoryRoute": 210, "enemyImmune": True},
        "164": {"winWithinRounds": 5, "winWithinRoute": 272, "tooLateRoute": 324},
        "180": {"victoryRoute": 70, "playerLossRoute": 129},
        "200": {"winWithinRounds": 7, "winWithinRoute": 272, "tooLateRoute": 324},
        "208": {"winWithinRounds": 4, "winWithinRoute": 4, "tooLateRoute": 81},
        "241": {"victoryRoute": 186, "ignorePlayerLossRounds": 2},
        "259": {"victoryRoute": 151, "playerLossRoute": 129},
        "260": {"victoryRoute": 210, "enemyImmune": True, "ignorePlayerLossRounds": 2},
        "263": {"victoryRoute": 25, "playerLossRoute": 66, "evadeRoute": 277},
        "265": {"victoryRoute": 3, "enemyImmune": True},
        "270": {"victoryRoute": 340},
        "296": {"roundLimit": 3, "survivalRoute": 173, "victoryRoute": 173},
        "304": {"victoryRoute": 20, "enemyImmune": True},
        "343": {"victoryRoute": 28},
    }
    for section, fields in expected.items():
        presets = data[section].get("combat", [])
        if not presets:
            raise AssertionError(f"section {section} expected combat preset")
        preset = presets[0]
        for key, expected_value in fields.items():
            if expected_value is True:
                assert_true(preset.get(key), f"section {section} {key}")
            else:
                assert_equal(preset.get(key), expected_value, f"section {section} {key}")


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
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 83)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "section 83 applies Mindforce loss without Mindshield")
    quiet(assistant.start_section_combat, "83-ice-barbarian-mutants")
    assert_true(assistant.combat["EnemyImmune"], "section 83 Ice Barbarian Mutants immune to Mindblast")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindshield"])
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 83)
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 83 Mindshield prevents Mindforce loss")

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

    assistant = fresh_assistant()
    quiet(assistant.set_section, 147)
    quiet(assistant.start_section_combat, "147-kalkoth")
    assistant.combat["Log"] = [{"PlayerLoss": 1, "EnemyLoss": 0}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 66, "section 147 wounds route immediately to 66")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 147)
    quiet(assistant.start_section_combat, "147-kalkoth")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 28}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 84, "section 147 flawless victory routes to 84")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 158)
    quiet(assistant.start_section_combat, "158-ice-barbarian-scout")
    assistant.combat["Log"] = [{"PlayerLoss": 5, "EnemyLoss": 2}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 165, "section 158 higher player loss routes to 165")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 158)
    quiet(assistant.start_section_combat, "158-ice-barbarian-scout")
    assistant.combat["Log"] = [{"PlayerLoss": 2, "EnemyLoss": 5}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 271, "section 158 higher enemy loss routes to 271")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 158)
    quiet(assistant.start_section_combat, "158-ice-barbarian-scout")
    assistant.combat["Log"] = [{"PlayerLoss": 3, "EnemyLoss": 3}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 337, "section 158 equal loss routes to 337")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"])
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 88)
    quiet(assistant.start_section_combat, "88-javek")
    assistant.automation["Stored"]["combatSpecialRoll"] = 8
    quiet(assistant.combat_round, ["combat", "round", "1"])
    assert_true(assistant.combat["Active"], "section 88 safe venom check continues combat")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 88 bite loss is ignored on safe venom check")
    assert_equal(assistant.combat["Log"][-1]["SpecialRoll"], 8, "section 88 records safe venom roll")

    assistant = fresh_assistant(disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"])
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 88)
    quiet(assistant.start_section_combat, "88-javek")
    assistant.automation["Stored"]["combatSpecialRoll"] = 9
    quiet(assistant.combat_round, ["combat", "round", "1"])
    assert_true(assistant.death_active(), "section 88 fatal venom roll opens death state")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 180)
    quiet(assistant.start_section_combat, "180-kalkoth")
    assistant.character["EnduranceCurrent"] = 20
    assistant.combat["EnemyEnduranceCurrent"] = 4
    quiet(assistant.combat_round, ["combat", "round", "9"])
    assert_true(int(assistant.combat["EnemyEnduranceCurrent"]) <= 1, "section 180 Fenor adds enemy damage")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 180)
    quiet(assistant.start_section_combat, "180-kalkoth")
    assistant.combat["Log"] = [{"PlayerLoss": 1, "EnemyLoss": 0}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 129, "section 180 player loss routes immediately to 129")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 208)
    quiet(assistant.start_section_combat, "208-ice-barbarian")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 30} for _ in range(4)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 4, "section 208 victory within four rounds routes to 4")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 208)
    quiet(assistant.start_section_combat, "208-ice-barbarian")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 6} for _ in range(5)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 81, "section 208 slow victory routes to 81")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 241)
    quiet(assistant.start_section_combat, "241-ice-barbarian")
    quiet(assistant.combat_round, ["combat", "round", "1"])
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 241 ignores first two rounds of END loss")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 296)
    quiet(assistant.start_section_combat, "296-ice-barbarians")
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 0} for _ in range(3)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 173, "section 296 survival after three rounds routes to 173")


def main() -> int:
    test_book3_meals_failure_and_completion()
    test_book3_loot_and_route_checks()
    test_book3_roll_helpers()
    test_book3_all_roll_helpers_are_app_safe()
    test_book3_gold_distraction_helper()
    test_book3_direct_section_helpers()
    test_book3_combat_route_targets_match_source()
    test_book3_combat_route_semantics()
    test_book3_combat_helpers()
    print("Book 3 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

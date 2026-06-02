#!/usr/bin/env python3
"""Smoke-test Book 5 playable helper data."""

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


SAVE_DIR = ROOT / "testing" / "tmp" / "book5-playable-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "book5-playable-last-save.txt"
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


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book5_character_state(
        name="Book Five Pipeline",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        equipment_choices=BOOK5_CHOICES,
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
        "Animal Kinship",
    ]
    assistant.character["CompletedBooks"] = [1, 2, 3, 4]
    assistant.inventory["SpecialItems"] = lonewolf_redux.add_unique_item(
        assistant.inventory["SpecialItems"], "Sommerswerd"
    )
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def loss_choice_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, choice_id: str) -> dict:
    for choice in assistant.current_section_flow_payload()["LossChoices"]:
        if choice["Id"] == choice_id:
            return choice
    raise AssertionError(f"loss choice {choice_id!r} not found")


def route_check_by_id(assistant: lonewolf_redux.LoneWolfReduxAssistant, check_id: str) -> dict:
    for check in assistant.current_section_flow_payload()["RouteChecks"]:
        if check["Id"] == check_id:
            return check
    raise AssertionError(f"route check {check_id!r} not found")


def test_book5_confiscation_restore_and_safekeeping() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Sword", "Dagger"]
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["SpecialItems"] = ["Sommerswerd", "Crystal Star Pendant"]
    assistant.inventory["GoldCrowns"] = 33
    assistant.inventory["Nobles"] = 33
    assistant.automation["Stored"]["safekeepingSpecialItems"] = ["Silver Helm"]

    quiet(assistant.set_section, 10)
    assert_equal(assistant.inventory["Weapons"], [], "weapons confiscated")
    assert_equal(assistant.inventory["BackpackItems"], [], "backpack confiscated")
    assert_equal(assistant.inventory["SpecialItems"], [], "special items confiscated")
    assert_equal(assistant.inventory["GoldCrowns"], 0, "gold confiscated")
    assert_true("Silver Helm" in assistant.automation["Stored"]["safekeepingSpecialItems"], "safekeeping survives confiscation")

    quiet(assistant.set_section, 69)
    assert_equal(assistant.automation["Stored"]["confiscatedEquipment"]["GoldCrowns"], 33, "section 69 does not overwrite stored gold")

    quiet(assistant.set_section, 14)
    assert_true("Sword" in assistant.inventory["Weapons"], "weapon restored")
    assert_true("Rope" in assistant.inventory["BackpackItems"], "backpack restored")
    assert_true("Crystal Star Pendant" in assistant.inventory["SpecialItems"], "special item restored")
    assert_equal(assistant.inventory["GoldCrowns"], 33, "gold restored")


def test_book5_meals_blood_poisoning_and_loss_choices() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope", "Prism"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 137)
    assert_equal(assistant.inventory["BackpackItems"], ["Rope", "Prism"], "city meal consumes Backpack Meal")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "Meal prevents END loss")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Potion of Laumspur (+4 END)"]
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 63)
    assert_true(assistant.automation_flags["book5BloodPoisoningActive"], "blood poisoning starts")
    quiet(assistant.set_section, 102)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "blood poisoning charges next section")
    quiet(assistant.use_item, "backpack", "Potion of Laumspur")
    assert_equal(assistant.character["EnduranceCurrent"], 22, "Laumspur restores END")
    assert_equal(assistant.automation_flags["book5BloodPoisoningActive"], False, "Laumspur cures blood poisoning")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Rope"]
    assistant.inventory["Weapons"] = ["Sword"]
    quiet(assistant.set_section, 19)
    choice = loss_choice_by_id(assistant, "guard-payment-1")
    assert_true(all(item["Item"] != "Meal" for item in choice["Candidates"]), "guard payment excludes Meals")
    quiet(assistant.apply_section_loss, "guard-payment-1", "backpack", "Rope")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "guard payment removes selected item")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["Weapons"] = ["Sword"]
    assistant.inventory["SpecialItems"] = ["Map of Vassagonia"]
    quiet(assistant.set_section, 270)
    choice = loss_choice_by_id(assistant, "cave-pack-loss-1")
    assert_equal(choice["Source"], "fallback", "section 270 falls back without Backpack Items")


def test_book5_combat_and_completion() -> None:
    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 24
    quiet(assistant.set_section, 20)
    quiet(assistant.start_section_combat, "20-horseman")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [
        {
            "Round": 1,
            "Roll": 0,
            "Ratio": 0,
            "EnemyLoss": 28,
            "PlayerLoss": 5,
            "LoneWolfReduxLoss": 5,
        }
    ]
    assistant.character["EnduranceCurrent"] = 19
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.character["EnduranceCurrent"], 21, "section 20 restores half combat loss")
    assert_equal(assistant.state["CurrentSection"], 125, "section 20 fast victory route")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 350)
    assert_equal(assistant.character["EnduranceCurrent"], 17, "section 350 END loss")
    assert_true("Sommerswerd" not in assistant.inventory["SpecialItems"], "Sommerswerd removed")
    assert_true(assistant.automation_flags["book5SommerswerdLost"], "Sommerswerd lost flag set")
    quiet(assistant.set_section, 400)
    assert_true("Sommerswerd" in assistant.inventory["SpecialItems"], "Sommerswerd restored at completion")
    assert_true("Book of the Magnakai" in assistant.inventory["SpecialItems"], "Book of the Magnakai recorded")
    assert_true(5 in assistant.character["CompletedBooks"], "Book 5 completed")
    assert_equal(len(assistant.character["KaiDisciplines"]), 10, "Kai Master final Discipline added")
    assert_equal(assistant.automation["Ending"]["Type"], "success", "Book 5 success ending")


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


def test_book5_combat_route_targets_match_source() -> None:
    data = json.loads((ROOT / "data" / "book5-section-flows.json").read_text(encoding="utf-8"))["5"]
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


def test_book5_combat_route_semantics() -> None:
    data = json.loads((ROOT / "data" / "book5-section-flows.json").read_text(encoding="utf-8"))["5"]
    expected: dict[str, dict[str, object]] = {
        "4": {"ignoreEnemyLossRounds": 1, "winWithinRounds": 4, "winWithinRoute": 165, "roundExceededRoute": 180},
        "12": {"modifier": -2, "enemyImmune": True, "victoryRoute": 95},
        "20": {"winWithinRounds": 3, "winWithinRoute": 125, "roundExceededRoute": 82, "defeatRoute": 161},
        "57": {"victoryRoute": 2},
        "64": {"victoryRoute": 177},
        "91": {"modifier": -4, "winWithinRounds": 4, "winWithinRoute": 65, "roundExceededRoute": 180},
        "110": {"victoryRoute": 40},
        "119": {"ignorePlayerLossRounds": 3, "victoryRoute": 137},
        "123": {"canEvade": True, "evadeRoute": 51, "victoryRoute": 198},
        "159": {"victoryRoute": 52},
        "168": {"winWithinRounds": 3, "winWithinRoute": 101, "roundExceededRoute": 46},
        "178": {"victoryChoices": [52, 140]},
        "190": {"modifier": -2, "victoryRoute": 111},
        "264": {"combat": False},
        "273": {"canEvade": True, "evadeRoute": 238, "victoryRoute": 345},
        "280": {"ignorePlayerLossRounds": 1, "victoryRoute": 213},
        "316": {"victoryRoute": 333},
        "330": {"winWithinRounds": 2, "winWithinRoute": 243, "roundExceededRoute": 394},
        "334": {"canEvade": True, "evadeRoute": 209, "victoryRoute": 310},
        "355": {"enemyImmune": True, "winWithinRounds": 4, "winWithinRoute": 249, "roundExceededRoute": 304},
        "357": {"modifier": -2, "combatRollRoutes": {"1": 293}, "victoryChoices": [207, 224]},
        "361": {"winWithinRounds": 3, "winWithinRoute": 288, "roundExceededRoute": 382},
        "387": {"canEvade": True, "evadeRoute": 205, "victoryRoute": 341},
        "389": {"victoryChoices": [207, 224]},
        "393": {"canEvade": True, "evadeAfterRounds": 3, "evadeRoute": 228, "victoryRoute": 255},
    }
    for section, fields in expected.items():
        presets = data[section].get("combat", [])
        if fields.get("combat") is False:
            assert_equal(presets, [], f"section {section} has no combat preset")
            continue
        if not presets:
            raise AssertionError(f"section {section} expected combat preset")
        preset = presets[0]
        for key, expected_value in fields.items():
            if key == "combat":
                continue
            if expected_value is True:
                assert_true(preset.get(key), f"section {section} {key}")
            else:
                assert_equal(preset.get(key), expected_value, f"section {section} {key}")


def test_book5_semantic_combat_helpers() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 4)
    quiet(assistant.start_section_combat, "4-palace-gaoler")
    quiet(assistant.combat_round, ["combat", "round", "9"])
    assert_true(assistant.combat["Log"][-1]["IgnoredEnemyLoss"] > 0, "section 4 ignores first-round enemy loss")
    assert_equal(assistant.combat["EnemyEnduranceCurrent"], 21, "section 4 enemy END is unchanged in round 1")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 57)
    quiet(assistant.start_section_combat, "57-elix")
    assert_equal(assistant.combat["Modifier"], 0, "section 57 has no Elix modifier without history")
    assistant = fresh_assistant()
    assistant.state["CombatHistory"] = [{"BookNumber": 4, "EnemyName": "Elix", "Outcome": "Victory"}]
    quiet(assistant.set_section, 57)
    quiet(assistant.start_section_combat, "57-elix")
    assert_equal(assistant.combat["Modifier"], 2, "section 57 applies previous Elix modifier")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 64)
    quiet(assistant.start_section_combat, "64-kwaraz")
    assert_equal(assistant.combat["Modifier"], 2, "section 64 adds extra Mindblast bonus")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 20
    assistant.character["KaiDisciplines"] = [item for item in assistant.character["KaiDisciplines"] if item != "Mindshield"]
    quiet(assistant.set_section, 264)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "section 264 Mindblast loses END without Mindshield")
    assert_equal(assistant.flow_combat_entries(), [], "section 264 is a route check, not combat")
    matched = route_check_by_id(assistant, "264-sommerswerd")["MatchedOutcome"]
    assert_equal(matched["Route"], 315, "section 264 Sommerswerd route check")
    assistant.inventory["SpecialItems"] = []
    matched = route_check_by_id(assistant, "264-sommerswerd")["MatchedOutcome"]
    assert_equal(matched["Route"], 299, "section 264 no-Sommerswerd route check")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 330)
    quiet(assistant.start_section_combat, "330-drakkar")
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 0} for _ in range(2)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 394, "section 330 routes away after two unresolved rounds")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 361)
    quiet(assistant.start_section_combat, "361-drakkar")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 10} for _ in range(3)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 288, "section 361 victory within three rounds routes to 288")
    assistant = fresh_assistant()
    quiet(assistant.set_section, 361)
    quiet(assistant.start_section_combat, "361-drakkar")
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 0} for _ in range(3)]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 382, "section 361 routes before a fourth round")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 357)
    quiet(assistant.start_section_combat, "357-platform-sentry")
    quiet(assistant.combat_round, ["combat", "round", "1"])
    assert_equal(assistant.state["CurrentSection"], 293, "section 357 roll 1 fall route")
    assert_true(assistant.death_active(), "section 357 fall route records terminal section")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 393)
    quiet(assistant.start_section_combat, "393-drakkar")
    assert_true(not assistant.can_evade_combat_now(), "section 393 cannot evade before three rounds")
    assistant.combat["Log"] = [{"PlayerLoss": 0, "EnemyLoss": 0} for _ in range(3)]
    assert_true(assistant.can_evade_combat_now(), "section 393 can evade after three rounds")


def test_book5_reviewed_section_helpers() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 46)
    preset = assistant.flow_combat_entries()[0]
    assert_equal(preset["enemy"]["name"], "Vestibule Guard 2", "section 46 digit enemy combat detected")

    assistant = fresh_assistant()
    assistant.character["CombatSkillCurrent"] = 14
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 127)
    result = quiet(assistant.roll_current_section, 4)
    assert_equal(result["Route"], 159, "section 127 successful door charge route")
    assert_equal(assistant.character["EnduranceCurrent"], 20, "section 127 success does not lose END")

    assistant = fresh_assistant()
    assistant.character["CombatSkillCurrent"] = 14
    assistant.character["EnduranceCurrent"] = 20
    quiet(assistant.set_section, 127)
    result = quiet(assistant.roll_current_section, 5)
    assert_equal(result["Route"], 93, "section 127 failed door charge route")
    assert_equal(assistant.character["EnduranceCurrent"], 19, "section 127 failure loses 1 END")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 15
    assistant.state["CombatHistory"] = [{"BookNumber": 5, "Rounds": [{"PlayerLoss": 7}]}]
    quiet(assistant.set_section, 161)
    assert_equal(assistant.character["EnduranceCurrent"], 18, "section 161 restores half combat END loss")

    assistant = fresh_assistant()
    assistant.character["CombatSkillCurrent"] = 17
    quiet(assistant.set_section, 166)
    assert_equal(assistant.character["CombatSkillCurrent"], 14, "section 166 applies Limbdeath CS penalty")
    assert_true(assistant.automation_flags["book5LostUseOfOneArm"], "section 166 sets one-arm flag")
    quiet(assistant.set_section, 166)
    assert_equal(assistant.character["CombatSkillCurrent"], 14, "section 166 does not double-apply CS penalty")
    quiet(assistant.set_section, 2)
    assert_equal(assistant.character["CombatSkillCurrent"], 17, "section 2 restores Limbdeath CS penalty")
    assert_equal(assistant.automation_flags["book5LostUseOfOneArm"], False, "section 2 clears one-arm flag")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 20
    assistant.inventory["Nobles"] = 20
    quiet(assistant.set_section, 248)
    quiet(assistant.follow_route, 328)
    assert_equal(assistant.inventory["GoldCrowns"], 15, "section 248 paid route costs 5 Gold")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 20
    assistant.inventory["Nobles"] = 20
    quiet(assistant.set_section, 265)
    quiet(assistant.follow_route, 397)
    assert_equal(assistant.inventory["GoldCrowns"], 19, "section 265 paid route costs 1 Gold")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 20
    assistant.inventory["Nobles"] = 20
    quiet(assistant.set_section, 276)
    quiet(assistant.follow_route, 326)
    assert_equal(assistant.inventory["GoldCrowns"], 15, "section 276 paid route costs 5 Gold")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 20
    assistant.inventory["Nobles"] = 20
    quiet(assistant.set_section, 362)
    quiet(assistant.follow_route, 237)
    assert_equal(assistant.inventory["GoldCrowns"], 19, "section 362 jala route costs 1 Gold")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 360)
    first = quiet(assistant.roll_current_section, 0)
    assert_equal(first["NextStage"], "second", "section 360 first roll advances to comparison")
    result = quiet(assistant.roll_current_section, 0)
    assert_equal(result["Route"], 226, "section 360 lower second roll route")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 360)
    quiet(assistant.roll_current_section, 0)
    result = quiet(assistant.roll_current_section, 9)
    assert_equal(result["Route"], 297, "section 360 higher second roll route")

    assistant = fresh_assistant()
    quiet(assistant.set_section, 360)
    quiet(assistant.roll_current_section, 0)
    result = quiet(assistant.roll_current_section, 1)
    assert_equal(result["Route"], 334, "section 360 equal second roll route")


def main() -> int:
    test_book5_confiscation_restore_and_safekeeping()
    test_book5_meals_blood_poisoning_and_loss_choices()
    test_book5_combat_and_completion()
    test_book5_combat_route_targets_match_source()
    test_book5_combat_route_semantics()
    test_book5_semantic_combat_helpers()
    test_book5_reviewed_section_helpers()
    print("Book 5 playable pipeline smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

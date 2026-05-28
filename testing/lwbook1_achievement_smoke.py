#!/usr/bin/env python3
"""Smoke-test Book 1 achievement definitions, triggers, and backfill."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "achievement-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "achievement-last-save.txt"
SUCCESS_ROUTE = [
    1,
    141,
    56,
    222,
    252,
    70,
    157,
    30,
    261,
    264,
    6,
    200,
    168,
    64,
    16,
    192,
    171,
    303,
    237,
    265,
    142,
    135,
    223,
    75,
    163,
    321,
    273,
    51,
    288,
    129,
    3,
    196,
    332,
    350,
]


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant(*, reset: bool = True) -> lonewolf_redux.LoneWolfReduxAssistant:
    if reset:
        reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Achievement Smoke",
        kai_disciplines=["Camouflage", "Sixth Sense", "Tracking", "Hunting", "Healing"],
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


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def unlocked_ids(assistant: lonewolf_redux.LoneWolfReduxAssistant) -> set[str]:
    assistant.sync_achievements(save=False)
    return {
        str(entry.get("Id"))
        for entry in lonewolf_redux.as_list(assistant.achievement_state().get("Unlocked"))
        if isinstance(entry, dict)
    }


def assert_unlocked(assistant: lonewolf_redux.LoneWolfReduxAssistant, *ids: str) -> None:
    unlocked = unlocked_ids(assistant)
    missing = [achievement_id for achievement_id in ids if achievement_id not in unlocked]
    assert_equal(missing, [], "missing achievements")


def test_achievement_definitions() -> None:
    assistant = fresh_assistant()
    definitions = assistant.achievement_definitions()
    ids = [str(definition.get("Id") or "") for definition in definitions]

    assert_true(any(achievement_id.startswith("lw1_") for achievement_id in ids), "Book 1 achievement IDs")
    assert_true(any(achievement_id.startswith("lw2_") for achievement_id in ids), "Book 2 achievement IDs")
    assert_true("lw1_complete" in ids, "completion achievement keeps existing ID")
    assert_true("lw1_gourgaz_victory" in ids, "Gourgaz achievement defined")
    assert_true("lw1_crystal_star_pendant" in ids, "Pendant achievement defined")
    assert_true("lw2_complete" in ids, "Book 2 completion achievement defined")
    assert_true("lw2_claim_sommerswerd" in ids, "Sommerswerd achievement defined")
    assert_equal(len(ids), len(set(ids)), "unique achievement IDs")


def test_story_route_unlocks() -> None:
    assistant = fresh_assistant()
    for target in SUCCESS_ROUTE[1:]:
        quiet(assistant.follow_route, target)

    assert_equal(assistant.state["CurrentSection"], 350, "success route final section")
    assert_unlocked(assistant, "lw1_complete", "lw1_reach_holmgard", "lw1_clean_story_route")


def test_combat_and_durable_item_unlocks() -> None:
    assistant = fresh_assistant()
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 1,
            "Section": 255,
            "Outcome": "Victory",
            "EnemyName": "Gourgaz",
            "EnemyCombatSkill": 20,
            "EnemyEnduranceMax": 30,
            "RoundCount": 4,
        }
    ]
    assistant.record_item_seen("Prince's Sword", "weapon")
    assistant.record_item_seen("Crystal Star Pendant", "special")

    assert_unlocked(
        assistant,
        "lw1_first_blood",
        "lw1_gourgaz_victory",
        "lw1_princes_sword",
        "lw1_crystal_star_pendant",
    )


def test_route_failure_and_random_unlocks() -> None:
    assistant = fresh_assistant()

    quiet(assistant.set_section, 46)
    quiet(assistant.follow_route, 246)
    assistant.inventory["GoldCrowns"] = 10
    assistant.inventory["Nobles"] = 10
    quiet(assistant.set_section, 12)
    quiet(assistant.follow_route, 262)

    quiet(assistant.set_section, 236)
    quiet(assistant.set_section, 292)
    quiet(assistant.set_section, 162)
    quiet(assistant.set_section, 258)
    quiet(assistant.set_section, 127)
    quiet(assistant.set_section, 21)
    quiet(assistant.set_section, 189)

    assert_unlocked(
        assistant,
        "lw1_paid_ferry",
        "lw1_caravan_fare",
        "lw1_vordak_gem_backlash",
        "lw1_vordak_gem_failure",
        "lw1_capture_escape",
        "lw1_capture_death",
        "lw1_backpack_lost",
        "lw1_marsh_escape",
    )


def test_summary_backfill_unlocks() -> None:
    assistant = fresh_assistant()
    assistant.character["CompletedBooks"] = [1]
    assistant.state["BookHistory"] = [
        {
            "BookNumber": 1,
            "BookTitle": "Flight from the Dark",
            "VisitedSections": SUCCESS_ROUTE + list(range(2, 76)),
            "UniqueSectionsVisited": 75,
            "Weapons": ["Prince's Sword"],
            "BackpackItems": [],
            "SpecialItems": ["Crystal Star Pendant"],
            "Victories": 1,
            "DeathCount": 1,
        }
    ]

    assert_unlocked(
        assistant,
        "lw1_complete",
        "lw1_reach_holmgard",
        "lw1_clean_story_route",
        "lw1_first_blood",
        "lw1_princes_sword",
        "lw1_crystal_star_pendant",
        "lw1_long_road",
    )


def test_book2_achievement_unlocks() -> None:
    assistant = fresh_assistant()
    assistant.state = lonewolf_redux.create_book2_character_state(
        name="Book 2 Achievement Smoke",
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Weaponskill"],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=5,
        weaponskill_roll=5,
        armoury_choices=["sword", "two-meals"],
    )
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")

    assistant.record_item_seen("Sommerswerd", "special")
    assistant.record_item_seen("Magic Spear", "special")
    assistant.record_item_seen("Red Pass", "special")
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 2,
            "Section": 106,
            "Outcome": "Victory",
            "EnemyName": "Helghast",
            "EnemyCombatSkill": 22,
            "EnemyEnduranceMax": 30,
            "RoundCount": 3,
        }
    ]
    for section in [78, 126, 196, 202, 305, 350]:
        quiet(assistant.set_section, section)
    assistant.character["CompletedBooks"] = [2]
    assistant.state["CurrentBookStats"]["VisitedSections"] = list(range(1, 91))
    assistant.state["CurrentBookStats"]["UniqueSectionsVisited"] = 90

    assert_unlocked(
        assistant,
        "lw2_complete",
        "lw2_reach_hammerdal",
        "lw2_claim_sommerswerd",
        "lw2_magic_spear",
        "lw2_helghast_victory",
        "lw2_arm_wrestling_win",
        "lw2_survive_green_sceptre",
        "lw2_red_pass",
        "lw2_deadly_documents",
        "lw2_long_road",
    )


def main() -> int:
    test_achievement_definitions()
    test_story_route_unlocks()
    test_combat_and_durable_item_unlocks()
    test_route_failure_and_random_unlocks()
    test_summary_backfill_unlocks()
    test_book2_achievement_unlocks()
    print("Book 1 achievement smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

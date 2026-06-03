#!/usr/bin/env python3
"""Smoke-test Book 3-5 achievement definitions and backfill triggers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "achievement-345-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "achievement-345-last-save.txt"
DISCIPLINES = ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Weaponskill"]


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def fresh_assistant(book: int) -> lonewolf_redux.LoneWolfReduxAssistant:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    if book == 3:
        assistant.state = lonewolf_redux.create_book3_character_state(
            name="Book 3 Achievement Smoke",
            kai_disciplines=DISCIPLINES,
            combat_skill_roll=4,
            endurance_roll=6,
            gold_roll=5,
            weaponskill_roll=5,
            equipment_choices=["sword", "special-rations"],
        )
    elif book == 4:
        assistant.state = lonewolf_redux.create_book4_character_state(
            name="Book 4 Achievement Smoke",
            kai_disciplines=DISCIPLINES,
            combat_skill_roll=4,
            endurance_roll=6,
            gold_roll=5,
            weaponskill_roll=5,
            equipment_choices=[
                "warhammer",
                "dagger",
                "two-potions-of-laumspur",
                "five-special-rations",
                "chainmail-waistcoat",
                "shield",
            ],
        )
    elif book == 5:
        assistant.state = lonewolf_redux.create_book5_character_state(
            name="Book 5 Achievement Smoke",
            kai_disciplines=DISCIPLINES,
            combat_skill_roll=4,
            endurance_roll=6,
            gold_roll=5,
            weaponskill_roll=5,
            equipment_choices=["dagger", "two-meals", "chainmail-waistcoat", "shield"],
        )
    else:
        raise ValueError(f"Unsupported book for this smoke: {book}")
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


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


def set_unique_sections(assistant: lonewolf_redux.LoneWolfReduxAssistant, count: int) -> None:
    stats = assistant.state["CurrentBookStats"]
    stats["VisitedSections"] = list(range(1, count + 1))
    stats["SectionsVisited"] = count
    stats["UniqueSectionsVisited"] = count


def test_definition_batch() -> None:
    assistant = fresh_assistant(3)
    ids = {str(definition.get("Id") or "") for definition in assistant.achievement_definitions()}
    expected = {
        "lw3_complete",
        "lw3_capture_vonotar",
        "lw3_mission_failed",
        "lw3_firesphere",
        "lw3_silver_helm",
        "lw3_baknar_oil",
        "lw3_crystal_frostwyrm",
        "lw3_long_road",
        "lw4_complete",
        "lw4_dagger_vashna",
        "lw4_onyx_medallion",
        "lw4_mine_treasure",
        "lw4_barraka_victory",
        "lw4_holy_water",
        "lw4_bad_key",
        "lw4_long_road",
        "lw5_complete",
        "lw5_book_magnakai",
        "lw5_kai_master",
        "lw5_black_sash",
        "lw5_recover_gear",
        "lw5_jewelled_mace",
        "lw5_itikar_rider",
        "lw5_long_road",
    }
    assert_equal(sorted(expected - ids), [], "defined Book 3-5 achievements")


def test_book3_unlocks() -> None:
    assistant = fresh_assistant(3)
    assistant.character["CompletedBooks"] = [3]
    for section in [61, 350]:
        quiet(assistant.set_section, section)
    for item in ["Firesphere", "Silver Helm", "Baknar Oil"]:
        assistant.record_item_seen(item, "special")
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 3,
            "Section": 265,
            "Outcome": "Victory",
            "EnemyName": "Crystal Frostwyrm",
            "EnemyCombatSkill": 15,
            "EnemyEnduranceMax": 30,
            "RoundCount": 3,
        }
    ]
    set_unique_sections(assistant, 90)
    assert_unlocked(
        assistant,
        "lw3_complete",
        "lw3_capture_vonotar",
        "lw3_mission_failed",
        "lw3_firesphere",
        "lw3_silver_helm",
        "lw3_baknar_oil",
        "lw3_crystal_frostwyrm",
        "lw3_long_road",
    )


def test_book4_unlocks() -> None:
    assistant = fresh_assistant(4)
    assistant.character["CompletedBooks"] = [4]
    quiet(assistant.set_section, 302)
    for item in [
        "Dagger of Vashna",
        "Onyx Medallion",
        "Flask of Holy Water",
        "Potion of Alether (+2 CS)",
        "Iron Key",
    ]:
        assistant.record_item_seen(item, "special")
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 4,
            "Section": 325,
            "Outcome": "Victory",
            "EnemyName": "Barraka",
            "EnemyCombatSkill": 25,
            "EnemyEnduranceMax": 29,
            "RoundCount": 5,
        }
    ]
    set_unique_sections(assistant, 90)
    assert_unlocked(
        assistant,
        "lw4_complete",
        "lw4_dagger_vashna",
        "lw4_onyx_medallion",
        "lw4_mine_treasure",
        "lw4_barraka_victory",
        "lw4_holy_water",
        "lw4_bad_key",
        "lw4_long_road",
    )


def test_book5_unlocks() -> None:
    assistant = fresh_assistant(5)
    assistant.character["CompletedBooks"] = [5]
    quiet(assistant.set_section, 14)
    for item in ["Book of the Magnakai", "Black Sash", "Jewelled Mace"]:
        assistant.record_item_seen(item, "special")
    assistant.state["CombatHistory"] = [
        {
            "BookNumber": 5,
            "Section": 240,
            "Outcome": "Victory",
            "EnemyName": "Itikar",
            "EnemyCombatSkill": 17,
            "EnemyEnduranceMax": 30,
            "RoundCount": 4,
        }
    ]
    set_unique_sections(assistant, 100)
    assert_unlocked(
        assistant,
        "lw5_complete",
        "lw5_book_magnakai",
        "lw5_kai_master",
        "lw5_black_sash",
        "lw5_recover_gear",
        "lw5_jewelled_mace",
        "lw5_itikar_rider",
        "lw5_long_road",
    )


def main() -> int:
    test_definition_batch()
    test_book3_unlocks()
    test_book4_unlocks()
    test_book5_unlocks()
    print("Book 3-5 achievement smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Exercise Book 1 branches skipped by the successful route playtest."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "branch-playtest-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "branch-playtest-last-save.txt"
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
    reset: bool = True,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    if reset:
        reset_saves()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Branch Playtest",
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


def follow_and_assert(assistant: lonewolf_redux.LoneWolfReduxAssistant, target: int) -> None:
    source = int(assistant.state["CurrentSection"])
    quiet(assistant.follow_route, target)
    assert_equal(assistant.state["CurrentSection"], target, f"legal route {source} -> {target}")


def follow_path(assistant: lonewolf_redux.LoneWolfReduxAssistant, route: list[int]) -> None:
    assert_equal(assistant.state["CurrentSection"], route[0], "path start")
    for target in route[1:]:
        follow_and_assert(assistant, target)


def assert_illegal_route_blocked(assistant: lonewolf_redux.LoneWolfReduxAssistant, target: int) -> None:
    source = int(assistant.state["CurrentSection"])
    quiet(assistant.follow_route, target)
    assert_equal(assistant.state["CurrentSection"], source, f"illegal route {source} -> {target} blocked")


def play_early_combat_branch() -> None:
    assistant = fresh_assistant()
    follow_path(assistant, [1, 85])
    assert_illegal_route_blocked(assistant, 53)
    follow_and_assert(assistant, 229)

    quiet(assistant.start_section_combat, "229-kraan")
    assert_equal(assistant.combat["Active"], True, "section 229 combat active")
    assert_equal(assistant.combat["EnemyName"], "Kraan", "section 229 enemy")
    assert_equal(assistant.combat["Modifier"], -1, "section 229 dust modifier")
    assert_equal(assistant.combat["VictoryChoices"], [267, 125], "section 229 victory choices")

    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"Round": 1, "PlayerLoss": 0}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.combat["Active"], False, "section 229 combat ended")
    assert_equal(assistant.state["CurrentSection"], 229, "section 229 waits for victory choice")

    follow_and_assert(assistant, 267)


def play_death_and_rewind_branch() -> None:
    assistant = fresh_assistant()
    follow_path(assistant, [1, 275, 74, 281, 311, 47, 322, 17])

    result = assistant.roll_current_section(0)
    assert_equal(result["Route"], 53, "section 17 death roll route")
    follow_and_assert(assistant, 53)
    assert_equal(assistant.death_active(), True, "section 53 death active")

    recovery = assistant.death_recovery_payload()
    assert_equal(recovery["CanRepeat"], False, "entry death cannot repeat")
    assert_equal(recovery["CanRewind"], True, "entry death can rewind")
    assert_equal(recovery["RewindTarget"]["Section"], 17, "death rewind target")

    quiet(assistant.restore_death_checkpoint, "rewind")
    assert_equal(assistant.death_active(), False, "death cleared after rewind")
    assert_equal(assistant.state["CurrentSection"], 17, "rewound to section 17")


def play_inventory_and_stat_branches() -> None:
    assistant = fresh_assistant(["Camouflage", "Sixth Sense", "Tracking", "Healing", "Weaponskill"])
    start_meals = assistant.inventory["BackpackItems"].count("Meal")
    start_endurance = int(assistant.character["EnduranceCurrent"])
    follow_path(assistant, [1, 141, 56, 222, 252, 70, 28, 130])
    assert_equal(assistant.inventory["BackpackItems"].count("Meal"), start_meals - 1, "section 130 consumes Meal")
    assert_equal(assistant.character["EnduranceCurrent"], start_endurance, "section 130 Meal prevents END loss")

    assistant = fresh_assistant()
    start_gold = int(assistant.inventory["GoldCrowns"])
    follow_path(assistant, [1, 275, 74, 281, 311, 324, 33])
    assert_equal(assistant.inventory["GoldCrowns"], start_gold + 3, "section 33 adds Gold Crowns")

    assistant = fresh_assistant()
    assert_true(assistant.inventory["Weapons"], "starting weapon present")
    follow_path(assistant, [1, 275, 74, 281, 311, 47, 322, 17])
    result = assistant.roll_current_section(2)
    assert_equal(result["Route"], 274, "section 17 weapon-loss roll route")
    follow_and_assert(assistant, 274)
    assert_equal(assistant.inventory["Weapons"], [], "section 274 loses Weapons")


def main() -> int:
    play_early_combat_branch()
    play_death_and_rewind_branch()
    play_inventory_and_stat_branches()
    print("Book 1 branch playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

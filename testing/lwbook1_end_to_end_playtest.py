#!/usr/bin/env python3
"""Play a deterministic Book 1 route from section 1 to 350."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "end-to-end-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "end-to-end-last-save.txt"
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
        name="End to End Playtest",
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


def assert_section_303_route_check(assistant: lonewolf_redux.LoneWolfReduxAssistant) -> None:
    payload = assistant.current_section_flow_payload()
    checks = payload.get("RouteChecks", [])
    assert_true(checks, "section 303 route check present")
    first = checks[0]
    assert_equal(first.get("Ready"), True, "section 303 route check ready")
    assert_equal(first.get("MatchedOutcome", {}).get("Route"), 237, "section 303 Camouflage route")


def assert_section_237_roll(assistant: lonewolf_redux.LoneWolfReduxAssistant) -> None:
    result = assistant.roll_current_section(3)
    assert_equal(result["Raw"], 3, "section 237 raw roll")
    assert_equal(result["Route"], 265, "section 237 roll route")
    payload = assistant.current_section_flow_payload()
    assert_equal(payload.get("LastRoll", {}).get("Route"), 265, "section 237 stored last roll")


def save_and_reload(assistant: lonewolf_redux.LoneWolfReduxAssistant, section: int) -> lonewolf_redux.LoneWolfReduxAssistant:
    save_path = SAVE_DIR / "midroute-playtest.json"
    assert_true(assistant.save_game(str(save_path), quiet=True), "mid-route save")

    loaded = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    loaded.last_save_file = LAST_SAVE
    assert_true(loaded.load_game(str(save_path), quiet=True), "mid-route load")
    assert_equal(loaded.state["CurrentSection"], section, "loaded section")
    assert_equal(loaded.character["KaiDisciplines"], assistant.character["KaiDisciplines"], "loaded Kai Disciplines")
    assert_equal(loaded.inventory["BackpackItems"], assistant.inventory["BackpackItems"], "loaded Backpack Items")
    return loaded


def play_success_route() -> None:
    assistant = fresh_assistant()
    assert_equal(assistant.state["CurrentSection"], 1, "starting section")

    for target in SUCCESS_ROUTE[1:]:
        current = int(assistant.state["CurrentSection"])
        if current == 168:
            start_meals = assistant.inventory["BackpackItems"].count("Meal")
        if current == 303:
            assert_section_303_route_check(assistant)
        if current == 237:
            assert_section_237_roll(assistant)
        follow_and_assert(assistant, target)
        if target == 168:
            assistant = save_and_reload(assistant, 168)
        if current == 168:
            assert_equal(
                assistant.inventory["BackpackItems"].count("Meal"),
                start_meals,
                "Hunting preserved Meal at section 168",
            )

    assert_equal(assistant.state["CurrentSection"], 350, "final section")
    assert_true(1 in assistant.character["CompletedBooks"], "Book 1 completion recorded")
    assert_equal(assistant.automation.get("Ending", {}).get("Type"), "success", "success ending")
    assert_equal(assistant.book_completion_payload().get("Active"), True, "completion payload active")


def smoke_death_recovery_checkpoint() -> None:
    assistant = fresh_assistant()
    follow_and_assert(assistant, 141)
    quiet(assistant.set_section, 53)
    assert_equal(assistant.death_active(), True, "section 53 death active")

    recovery = assistant.death_recovery_payload()
    assert_equal(recovery["CanRepeat"], False, "entry death cannot repeat")
    assert_equal(recovery["CanRewind"], True, "entry death can rewind")
    assert_equal(recovery["RewindTarget"]["Section"], 141, "rewind target")

    quiet(assistant.restore_death_checkpoint, "rewind")
    assert_equal(assistant.death_active(), False, "death cleared after rewind")
    assert_equal(assistant.state["CurrentSection"], 141, "rewound section")


def main() -> int:
    play_success_route()
    smoke_death_recovery_checkpoint()
    print("Book 1 end-to-end playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

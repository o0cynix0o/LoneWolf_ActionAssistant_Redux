#!/usr/bin/env python3
"""Smoke-test confirmed Book 1 route checks and random helpers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "route-random-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "route-random-last-save.txt"


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Route Random Smoke",
        kai_disciplines=disciplines
        or ["Camouflage", "Sixth Sense", "Tracking", "Healing", "Weaponskill"],
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


def matched_route(assistant: lonewolf_redux.LoneWolfReduxAssistant, section: int) -> int | None:
    quiet(assistant.set_section, section)
    checks = assistant.current_section_flow_payload().get("RouteChecks", [])
    if not checks:
        raise AssertionError(f"section {section} had no route checks")
    first = checks[0]
    if not first.get("Ready"):
        raise AssertionError(f"section {section} route check not ready: {first.get('BlockedReason')}")
    matched = first.get("MatchedOutcome") or {}
    route = matched.get("Route")
    return int(route) if route is not None else None


def smoke_roll_helpers() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 2)
    result = assistant.roll_current_section(4)
    assert_equal(result["Route"], 343, "section 2 low roll route")
    result = assistant.roll_current_section(8)
    assert_equal(result["Route"], 276, "section 2 high roll route")

    quiet(assistant.set_section, 17)
    assert_equal(assistant.roll_current_section(0)["Route"], 53, "section 17 roll 0 route")
    assert_equal(assistant.roll_current_section(2)["Route"], 274, "section 17 roll 2 route")
    assert_equal(assistant.roll_current_section(5)["Route"], 316, "section 17 roll 5 route")

    quiet(assistant.set_section, 294)
    assert_equal(assistant.roll_current_section(1)["Route"], 230, "section 294 low roll route")
    assert_equal(assistant.roll_current_section(4)["Route"], 190, "section 294 middle roll route")
    assert_equal(assistant.roll_current_section(8)["Route"], 321, "section 294 high roll route")

    quiet(assistant.set_section, 302)
    assert_equal(assistant.roll_current_section(2)["Route"], 110, "section 302 low roll route")
    assert_equal(assistant.roll_current_section(3)["Route"], 285, "section 302 high roll route")


def smoke_power_item_and_stat_route_checks() -> None:
    assistant = fresh_assistant(["Hunting", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    assert_equal(matched_route(assistant, 128), 297, "section 128 Hunting route")

    assistant = fresh_assistant(["Camouflage", "Sixth Sense", "Tracking", "Healing", "Weaponskill"])
    assert_equal(matched_route(assistant, 128), 336, "section 128 no-Hunting route")

    assistant = fresh_assistant(["Mind Over Matter", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    assert_equal(matched_route(assistant, 162), 258, "section 162 Mind Over Matter route")
    assert_equal(assistant.inventory["Weapons"], [], "section 162 automation still applied")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Vordak Gem")
    assert_equal(matched_route(assistant, 9), 236, "section 9 Vordak Gem route")

    assistant = fresh_assistant()
    assert_equal(matched_route(assistant, 9), 292, "section 9 no-Vordak-Gem route")

    assistant = fresh_assistant()
    assistant.inventory["SpecialItems"].append("Silver Key")
    assert_equal(matched_route(assistant, 173), 158, "section 173 Silver Key route")

    assistant = fresh_assistant()
    assert_equal(matched_route(assistant, 173), 259, "section 173 no-Silver-Key route")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 10
    assistant.inventory["Nobles"] = 10
    assert_equal(matched_route(assistant, 12), 262, "section 12 enough Gold Crowns route")

    assistant = fresh_assistant()
    assistant.inventory["GoldCrowns"] = 3
    assistant.inventory["Nobles"] = 3
    assert_equal(matched_route(assistant, 12), 247, "section 12 not enough Gold Crowns route")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 26
    assert_equal(matched_route(assistant, 203), 80, "section 203 END 10 or more route")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] = 12
    assert_equal(matched_route(assistant, 203), 344, "section 203 END less than 10 route")


def main() -> int:
    smoke_roll_helpers()
    smoke_power_item_and_stat_route_checks()
    print("Book 1 route/random smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke-test terminal death, failure, and completion coverage for all onboarded books."""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_ROOT = ROOT / "testing" / "tmp" / "terminal-recovery-saves"
LAST_SAVE_ROOT = ROOT / "testing" / "tmp" / "terminal-recovery-last-save"

BOOK4_CHOICES = [
    "dagger",
    "spear",
    "two-potions-of-laumspur",
    "five-special-rations",
    "chainmail-waistcoat",
    "shield",
]
BOOK5_CHOICES = ["shield", "two-special-rations", "potion-of-laumspur", "sword"]


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


def reset_saves(book: int) -> tuple[Path, Path]:
    save_dir = SAVE_ROOT / f"book{book}"
    last_save = LAST_SAVE_ROOT.with_name(f"{LAST_SAVE_ROOT.name}-book{book}.txt")
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    if last_save.exists():
        last_save.unlink()
    return save_dir, last_save


def book_state_factory(book: int) -> Callable[[], dict[str, Any]]:
    common = {
        "name": "Terminal Smoke",
        "kai_disciplines": ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Weaponskill"],
        "combat_skill_roll": 4,
        "endurance_roll": 6,
        "gold_roll": 5,
        "weaponskill_roll": 5,
    }
    if book == 1:
        return lambda: lonewolf_redux.create_book1_character_state(
            **common,
            starting_find_roll=4,
        )
    if book == 2:
        return lambda: lonewolf_redux.create_book2_character_state(
            **common,
            armoury_choices=["sword", "two-meals"],
        )
    if book == 3:
        return lambda: lonewolf_redux.create_book3_character_state(
            **common,
            equipment_choices=["sword", "special-rations"],
        )
    if book == 4:
        return lambda: lonewolf_redux.create_book4_character_state(
            **common,
            equipment_choices=BOOK4_CHOICES,
        )
    if book == 5:
        return lambda: lonewolf_redux.create_book5_character_state(
            **common,
            equipment_choices=BOOK5_CHOICES,
        )
    raise ValueError(f"Unsupported book {book}")


def fresh_assistant(book: int) -> lonewolf_redux.LoneWolfReduxAssistant:
    save_dir, last_save = reset_saves(book)
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=save_dir, data_dir=ROOT / "data")
    assistant.last_save_file = last_save
    assistant.state = book_state_factory(book)()
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def automation_has_ending(entry: dict[str, Any], ending: str) -> bool:
    for action in entry.get("actions", []):
        if isinstance(action, dict) and action.get("type") == "ending" and action.get("ending") == ending:
            return True
    return False


def terminal_sections(book: int, endings: set[str]) -> list[tuple[int, str]]:
    automations = load_json(ROOT / "data" / f"book{book}-simple-automations.json")[str(book)]
    found: list[tuple[int, str]] = []
    for section, entry in automations.items():
        for ending in endings:
            if automation_has_ending(entry, ending):
                found.append((int(section), ending))
    return sorted(found)


def test_terminal_flow_coverage() -> None:
    expectations = {
        "terminal_death": "death",
        "terminal_failure": "failure",
        "terminal_success": "success",
    }
    for book in range(1, 6):
        flow = load_json(ROOT / "data" / f"book{book}-section-flows.json")[str(book)]
        automations = load_json(ROOT / "data" / f"book{book}-simple-automations.json")[str(book)]
        missing: list[str] = []
        unclassified: list[int] = []
        for section, entry in flow.items():
            if not str(section).isdigit():
                continue
            classes = set(entry.get("classification") or [])
            source_route_count = int(entry.get("sourceRouteCount") or 0)
            if "terminal_unclassified" in classes and int(entry.get("sourceRouteCount") or 0) == 0:
                unclassified.append(int(section))
            for classification, ending in expectations.items():
                if (
                    classification in classes
                    and source_route_count == 0
                    and not automation_has_ending(automations.get(section, {}), ending)
                ):
                    missing.append(f"{section}:{ending}")
        assert_equal(sorted(unclassified), [], f"Book {book} has no unclassified no-route terminals")
        assert_equal(missing, [], f"Book {book} terminal flow sections have ending automation")


def test_terminal_death_and_failure_sections_open_recovery() -> None:
    for book in range(1, 6):
        for section, ending in terminal_sections(book, {"death", "failure"}):
            assistant = fresh_assistant(book)
            quiet(assistant.set_section, section)
            assert_true(assistant.death_active(), f"Book {book} section {section} opens recovery")
            assert_equal(
                assistant.automation["DeathState"]["Type"],
                ending.title(),
                f"Book {book} section {section} ending type",
            )
            recovery = assistant.death_recovery_payload()
            assert_true(
                recovery["CanRepeat"] or recovery["CanRewind"],
                f"Book {book} section {section} exposes repeat or rewind recovery",
            )


def test_terminal_completion_sections_record_success() -> None:
    for book in range(1, 6):
        for section, _ending in terminal_sections(book, {"success"}):
            assistant = fresh_assistant(book)
            quiet(assistant.set_section, section)
            assert_equal(assistant.automation["Ending"]["Type"], "success", f"Book {book} section {section} success")
            assert_true(book in assistant.character["CompletedBooks"], f"Book {book} completion recorded")


def main() -> int:
    test_terminal_flow_coverage()
    test_terminal_death_and_failure_sections_open_recovery()
    test_terminal_completion_sections_record_success()
    print("Lone Wolf terminal recovery smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

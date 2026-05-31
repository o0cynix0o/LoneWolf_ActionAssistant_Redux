#!/usr/bin/env python3
"""Smoke-test Weaponskill assignment and combat bonus behavior."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import app_server  # noqa: E402
import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "weaponskill-saves"
ASSISTANT_HTML = ROOT / "assistant.html"
LAST_SAVE_FILE = ROOT / "data" / "last-save.txt"
CURRENT_POSITION_FILE = ROOT / "current-position.json"


def reset_saves() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


class FileSnapshot:
    def __init__(self, *paths: Path) -> None:
        self.snapshots = {
            path: path.read_bytes() if path.exists() else None
            for path in paths
        }

    def restore(self) -> None:
        for path, content in self.snapshots.items():
            if content is None:
                if path.exists():
                    path.unlink()
                continue
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)


def test_transition_assigns_weaponskill_weapon_and_bonus() -> None:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.state = lonewolf_redux.create_book2_character_state(
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Healing"],
        combat_skill_roll=4,
        endurance_roll=4,
        gold_roll=4,
        weaponskill_roll=0,
        armoury_choices=["sword", "shield"],
    )
    quiet(assistant.set_section, 350)
    quiet(assistant.ensure_book_completed, 2)

    quiet(
        assistant.continue_completed_book,
        kai_discipline="Weaponskill",
        weaponskill_roll=6,
        book3_gold_roll=4,
        book3_equipment_choices=["axe", "potion-of-laumspur"],
    )

    assert_equal(assistant.character["WeaponskillWeapon"], "Axe", "transition Weaponskill weapon")
    quiet(assistant.start_combat, ["combat", "start", "Training Dummy", "10", "10"])
    quiet(assistant.set_combat_weapon, "Axe", save=False)
    modifier, notes = assistant.combat_weapon_modifier_and_notes()
    assert_true("Weaponskill (Axe): +2 CS" in notes, "matching Weaponskill weapon should be noted.")
    assert_equal(
        assistant.combat_skill_for_round(),
        int(assistant.character["CombatSkillCurrent"]) + modifier,
        "round CS includes Weaponskill and other legal equipment bonuses",
    )


def test_missing_weaponskill_repair_helper() -> None:
    reset_saves()
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.state = lonewolf_redux.create_book1_character_state(
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"],
        combat_skill_roll=4,
        endurance_roll=4,
        gold_roll=4,
        starting_find_roll=4,
        weaponskill_roll=4,
    )
    assistant.character["KaiDisciplines"].append("Weaponskill")
    assistant.character["WeaponskillWeapon"] = ""

    quiet(assistant.assign_missing_weaponskill_weapon, 5, save=False)
    assert_equal(assistant.character["WeaponskillWeapon"], "Sword", "repair assigns chosen roll weapon")


def test_api_and_browser_weaponskill_helpers() -> None:
    source = ASSISTANT_HTML.read_text(encoding="utf-8")
    assert_true("name=\"weaponskillRoll\"" in source, "continue form should expose a Weaponskill roll field.")
    assert_true("data-weaponskill-assign" in source, "Disciplines panel should expose missing-weapon repair.")

    app_server.ASSISTANT = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    app_server.ASSISTANT.state = lonewolf_redux.create_book1_character_state(
        kai_disciplines=["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Mindblast"],
        combat_skill_roll=4,
        endurance_roll=4,
        gold_roll=4,
        starting_find_roll=4,
        weaponskill_roll=4,
    )
    app_server.ASSISTANT.character["KaiDisciplines"].append("Weaponskill")
    app_server.ASSISTANT.character["WeaponskillWeapon"] = ""
    output = app_server.handle_action({"action": "assign_weaponskill", "roll": 9})

    assert_true("Broadsword" in output, "API repair action should report assigned weapon.")
    assert_equal(app_server.ASSISTANT.character["WeaponskillWeapon"], "Broadsword", "API repair assigns weapon")


def main() -> int:
    snapshot = FileSnapshot(LAST_SAVE_FILE, CURRENT_POSITION_FILE)
    try:
        test_transition_assigns_weaponskill_weapon_and_bonus()
        test_missing_weaponskill_repair_helper()
        test_api_and_browser_weaponskill_helpers()
    finally:
        snapshot.restore()
    print("Weaponskill smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

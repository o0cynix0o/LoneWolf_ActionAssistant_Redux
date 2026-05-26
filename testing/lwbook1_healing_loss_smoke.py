#!/usr/bin/env python3
"""Smoke-test Book 1 Healing and explicit loss-choice helpers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "healing-loss-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "healing-loss-last-save.txt"


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Healing Loss Smoke",
        kai_disciplines=disciplines or ["Healing", "Camouflage", "Sixth Sense", "Tracking", "Weaponskill"],
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


def smoke_healing_helper() -> None:
    assistant = fresh_assistant()
    quiet(assistant.set_section, 119)
    after_entry = int(assistant.character["EnduranceCurrent"])
    healing = assistant.current_section_flow_payload()["Healing"]
    assert_equal(healing["Ready"], True, "section 119 Healing ready")

    quiet(assistant.apply_healing)
    assert_equal(assistant.character["EnduranceCurrent"], after_entry + 1, "Healing restores 1 END")
    healing = assistant.current_section_flow_payload()["Healing"]
    assert_equal(healing["Applied"], True, "Healing marked applied")

    quiet(assistant.apply_healing)
    assert_equal(assistant.character["EnduranceCurrent"], after_entry + 1, "Healing does not double-apply")

    assistant = fresh_assistant(["Camouflage", "Sixth Sense", "Tracking", "Mindshield", "Weaponskill"])
    assistant.character["EnduranceCurrent"] -= 4
    healing = assistant.current_section_flow_payload()["Healing"]
    assert_equal(healing["Ready"], False, "no Healing discipline blocks helper")

    assistant = fresh_assistant()
    assistant.character["EnduranceCurrent"] -= 4
    quiet(assistant.set_section, 229)
    healing = assistant.current_section_flow_payload()["Healing"]
    assert_equal(healing["Ready"], False, "combat section blocks Healing helper")


def smoke_loss_choice_helpers() -> None:
    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = ["Meal", "Laumspur"]
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    quiet(assistant.set_section, 144)
    choices = assistant.current_section_flow_payload()["LossChoices"]
    assert_equal(len(choices), 1, "section 144 loss choice present")
    assert_equal(choices[0]["Candidates"][0]["Type"], "backpack", "section 144 prefers Backpack Item")

    quiet(assistant.apply_section_loss, "144-stolen-item", "backpack", "Laumspur")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "section 144 removed selected Backpack Item")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Sword"], "section 144 preserved Weapons")

    quiet(assistant.apply_section_loss, "144-stolen-item", "backpack", "Meal")
    assert_equal(assistant.inventory["BackpackItems"], ["Meal"], "section 144 loss does not double-apply")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"] = []
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    quiet(assistant.set_section, 144)
    choices = assistant.current_section_flow_payload()["LossChoices"]
    assert_equal(choices[0]["Candidates"][0]["Type"], "weapon", "section 144 falls back to Weapon")
    quiet(assistant.apply_section_loss, "144-stolen-item", "weapon", "Sword")
    assert_equal(assistant.inventory["Weapons"], ["Axe"], "section 144 removed selected fallback Weapon")

    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    quiet(assistant.set_section, 277)
    choices = assistant.current_section_flow_payload()["LossChoices"]
    assert_equal(choices[0]["Id"], "277-broken-weapon", "section 277 loss choice id")
    quiet(assistant.apply_section_loss, "277-broken-weapon", "weapon", "2")
    assert_equal(assistant.inventory["Weapons"], ["Axe"], "section 277 removed selected Weapon slot")


def main() -> int:
    smoke_healing_helper()
    smoke_loss_choice_helpers()
    print("Book 1 Healing/loss smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

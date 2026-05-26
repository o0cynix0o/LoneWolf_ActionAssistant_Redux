#!/usr/bin/env python3
"""Smoke-test Book 1 player-choice aftermath helpers."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "player-choice-aftermath-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "player-choice-aftermath-last-save.txt"
DEFAULT_DISCIPLINES = ["Healing", "Camouflage", "Sixth Sense", "Tracking", "Weaponskill"]


def fresh_assistant() -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Player Choice Aftermath Smoke",
        kai_disciplines=DEFAULT_DISCIPLINES,
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


def smoke_section_307_weapon_exchange() -> None:
    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = ["Axe", "Sword"]
    quiet(assistant.set_section, 307)

    payload = assistant.current_section_flow_payload()
    choices = payload["LossChoices"]
    assert_equal(len(choices), 1, "section 307 exchange choice present")
    assert_equal(choices[0]["Id"], "307-warhammer-exchange", "section 307 exchange id")
    assert_equal(choices[0]["Replacement"]["Name"], "Warhammer", "section 307 replacement weapon")
    assert_equal([candidate["Item"] for candidate in choices[0]["Candidates"]], ["Axe", "Sword"], "section 307 exchange candidates")

    quiet(assistant.apply_section_loss, "307-warhammer-exchange", "weapon", "2")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Warhammer"], "section 307 exchanges selected Weapon")

    payload = assistant.current_section_flow_payload()
    assert_equal(payload["LossChoices"][0]["Applied"], True, "section 307 exchange marked applied")

    quiet(assistant.apply_section_loss, "307-warhammer-exchange", "weapon", "1")
    assert_equal(assistant.inventory["Weapons"], ["Axe", "Warhammer"], "section 307 exchange does not double-apply")

    assistant = fresh_assistant()
    assistant.inventory["Weapons"] = []
    quiet(assistant.set_section, 307)
    choice = assistant.current_section_flow_payload()["LossChoices"][0]
    assert_equal(choice["Ready"], False, "section 307 exchange blocks without carried Weapon")


def main() -> int:
    smoke_section_307_weapon_exchange()
    print("Book 1 player-choice aftermath smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke-test confirmed Book 1 combat presets and exceptions."""

from __future__ import annotations

import contextlib
import io
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "combat-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "combat-last-save.txt"
DEFAULT_DISCIPLINES = ["Mindblast", "Camouflage", "Sixth Sense", "Tracking", "Healing"]


def fresh_assistant(disciplines: list[str] | None = None) -> lonewolf_redux.LoneWolfReduxAssistant:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()

    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Combat Smoke",
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


def assert_in(member, container, label: str) -> None:
    if member not in container:
        raise AssertionError(f"{label}: {member!r} not found in {container!r}")


def start_section_combat(
    assistant: lonewolf_redux.LoneWolfReduxAssistant, section: int, combat_id: str
) -> None:
    quiet(assistant.set_section, section)
    quiet(assistant.start_section_combat, combat_id)
    assert_equal(assistant.combat["Active"], True, f"section {section} combat active")


def smoke_basic_presets_and_immunity() -> None:
    assistant = fresh_assistant()
    base_cs = int(assistant.character["CombatSkillCurrent"])
    start_section_combat(assistant, 133, "133-winged-serpent")
    assert_equal(assistant.combat["EnemyName"], "Winged Serpent", "section 133 enemy")
    assert_equal(assistant.combat["EnemyCombatSkill"], 16, "section 133 enemy CS")
    assert_equal(assistant.combat["EnemyEnduranceMax"], 18, "section 133 enemy END")
    assert_equal(assistant.combat["EnemyImmune"], True, "section 133 Mindblast immunity")
    assert_equal(assistant.combat_skill_for_round(1), base_cs, "section 133 ignores Mindblast")
    assert_equal(assistant.combat["VictoryRoute"], 266, "section 133 victory route")

    assistant = fresh_assistant()
    start_section_combat(assistant, 136, "136-giaks")
    assert_equal(len(assistant.combat["EnemyQueue"]), 2, "section 136 enemy queue")
    assert_equal(assistant.combat["EnemyName"], "Giak 1", "section 136 first enemy")
    assert_equal(assistant.combat["Modifier"], 1, "section 136 higher-ground modifier")
    assert_equal(assistant.combat["VictoryRoute"], 313, "section 136 victory route")


def smoke_conditional_modifiers() -> None:
    assistant = fresh_assistant()
    start_section_combat(assistant, 29, "29-vordak")
    assert_equal(assistant.combat["Modifier"], -2, "section 29 no-Mindshield penalty")
    assert_in(
        "No Mindshield against Mindforce: -2 CS",
        assistant.combat["AppliedConditionalModifierLabels"],
        "section 29 conditional label",
    )

    assistant = fresh_assistant(["Mindshield", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    start_section_combat(assistant, 29, "29-vordak")
    assert_equal(assistant.combat["Modifier"], 0, "section 29 Mindshield blocks penalty")

    assistant = fresh_assistant()
    start_section_combat(assistant, 170, "170-burrowcrawler")
    assert_equal(assistant.combat["EnemyImmune"], True, "section 170 Mindblast immunity")
    assert_equal(assistant.combat["Modifier"], -3, "section 170 no-Torch penalty")

    assistant = fresh_assistant()
    assistant.inventory["BackpackItems"].append("Torch")
    start_section_combat(assistant, 170, "170-burrowcrawler")
    assert_equal(assistant.combat["Modifier"], 0, "section 170 Torch blocks penalty")


def smoke_timed_and_forced_unarmed() -> None:
    assistant = fresh_assistant()
    start_section_combat(assistant, 283, "283-vordak")
    assert_equal(assistant.combat_timed_modifier_for_round(1), 2, "section 283 first-round bonus")
    assert_equal(assistant.combat_timed_modifier_for_round(2), -2, "section 283 later Mindforce penalty")

    assistant = fresh_assistant(["Mindshield", "Camouflage", "Sixth Sense", "Tracking", "Healing"])
    start_section_combat(assistant, 283, "283-vordak")
    assert_equal(assistant.combat_timed_modifier_for_round(1), 2, "section 283 Mindshield first round")
    assert_equal(assistant.combat_timed_modifier_for_round(2), 0, "section 283 Mindshield later rounds")

    assistant = fresh_assistant()
    base_cs = int(assistant.character["CombatSkillCurrent"])
    start_section_combat(assistant, 260, "260-unarmed-giaks")
    assert_equal(assistant.combat["ForceUnarmed"], True, "section 260 forced unarmed")
    assert_equal(assistant.combat_active_weapon(), "", "section 260 active weapon")
    assert_equal(assistant.combat_weapon_modifier_and_notes()[0], -4, "section 260 no-weapon penalty")
    assert_equal(assistant.combat_skill_for_round(1), base_cs - 4, "section 260 combat skill")


def smoke_routes_and_victory_exceptions() -> None:
    assistant = fresh_assistant()
    start_section_combat(assistant, 339, "339-robber")
    assert_equal(assistant.combat["CanEvade"], True, "section 339 evade available")
    assert_equal(assistant.combat["EvadeRoute"], 7, "section 339 evade route")
    assert_equal(assistant.combat["RoundLimit"], 4, "section 339 round limit")
    assert_equal(assistant.combat["RoundExceededRoute"], 203, "section 339 timeout route")
    assert_equal(assistant.combat["WinWithinRounds"], 4, "section 339 win-within rounds")
    assert_equal(assistant.combat["WinWithinRoute"], 94, "section 339 win-within route")

    assistant = fresh_assistant()
    start_section_combat(assistant, 227, "227-marshviper")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"Round": 1, "PlayerLoss": 0}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 348, "section 227 flawless victory route")

    assistant = fresh_assistant()
    start_section_combat(assistant, 227, "227-marshviper")
    assistant.combat["EnemyEnduranceCurrent"] = 0
    assistant.combat["Log"] = [{"Round": 1, "PlayerLoss": 1}]
    quiet(assistant.route_after_combat_round)
    assert_equal(assistant.state["CurrentSection"], 271, "section 227 wounded victory route")


def main() -> int:
    smoke_basic_presets_and_immunity()
    smoke_conditional_modifiers()
    smoke_timed_and_forced_unarmed()
    smoke_routes_and_victory_exceptions()
    print("Book 1 combat smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

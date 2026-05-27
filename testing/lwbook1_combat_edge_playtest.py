#!/usr/bin/env python3
"""Combat-focused Book 1 edge playtest.

This test exercises every checked-in Book 1 combat preset. It keeps the
assertions mechanical so the committed artifact records section numbers and
data behavior, not book prose.
"""

from __future__ import annotations

import contextlib
import io
import json
import shutil
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


SAVE_DIR = ROOT / "testing" / "tmp" / "combat-edge-saves"
LAST_SAVE = ROOT / "testing" / "tmp" / "combat-edge-last-save.txt"
DEFAULT_DISCIPLINES = ["Mindblast", "Mindshield", "Camouflage", "Sixth Sense", "Healing"]
LOW_POWER_DISCIPLINES = ["Mindshield", "Camouflage", "Sixth Sense", "Tracking", "Healing"]
ROUTE_FIELDS = [
    "victoryRoute",
    "defeatRoute",
    "evadeRoute",
    "flawlessVictoryRoute",
    "woundedVictoryRoute",
    "survivalRoute",
    "roundExceededRoute",
    "winWithinRoute",
    "tooLateRoute",
]


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def assert_equal(actual, expected, label: str) -> None:
    if actual != expected:
        raise AssertionError(f"{label}: expected {expected!r}, got {actual!r}")


def assert_true(value, label: str) -> None:
    if not value:
        raise AssertionError(f"{label}: expected truthy value, got {value!r}")


def load_flow() -> dict[str, Any]:
    return json.loads((ROOT / "data" / "book1-section-flows.json").read_text(encoding="utf-8"))["1"]


def combat_presets(flow: dict[str, Any]) -> list[tuple[int, dict[str, Any], dict[str, Any]]]:
    presets: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    section_items = [(key, value) for key, value in flow.items() if str(key).isdigit()]
    for section_text, entry in sorted(section_items, key=lambda item: int(item[0])):
        for preset in entry.get("combat") or []:
            if isinstance(preset, dict):
                presets.append((int(section_text), entry, preset))
    return presets


def reset_save_dir() -> None:
    if SAVE_DIR.exists():
        shutil.rmtree(SAVE_DIR)
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    if LAST_SAVE.exists():
        LAST_SAVE.unlink()


def fresh_assistant(
    *,
    disciplines: list[str] | None = None,
    combat_skill: int = 40,
    endurance: int = 100,
) -> lonewolf_redux.LoneWolfReduxAssistant:
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=SAVE_DIR, data_dir=ROOT / "data")
    assistant.last_save_file = LAST_SAVE
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Combat Edge Playtest",
        kai_disciplines=disciplines or DEFAULT_DISCIPLINES,
        combat_skill_roll=9,
        endurance_roll=9,
        gold_roll=9,
        starting_find_roll=4,
        weaponskill_roll=6,
    )
    assistant.character["CombatSkillBase"] = combat_skill
    assistant.character["CombatSkillCurrent"] = combat_skill
    assistant.character["EnduranceMax"] = endurance
    assistant.character["EnduranceCurrent"] = endurance
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def preset_enemies(preset: dict[str, Any]) -> list[dict[str, Any]]:
    enemies = preset.get("enemies") if preset.get("enemies") is not None else preset.get("enemy")
    return [enemy for enemy in lonewolf_redux.as_list(enemies) if isinstance(enemy, dict)]


def expected_victory_section(section: int, preset: dict[str, Any]) -> int:
    if preset.get("winWithinRoute"):
        return int(preset["winWithinRoute"])
    if preset.get("flawlessVictoryRoute"):
        return int(preset["flawlessVictoryRoute"])
    if preset.get("victoryRoute"):
        return int(preset["victoryRoute"])
    return section


def smoke_combat_candidate_coverage(flow: dict[str, Any]) -> None:
    combat_class_sections = {
        int(section)
        for section, entry in flow.items()
        if str(section).isdigit()
        if "combat" in lonewolf_redux.as_list(entry.get("classification"))
    }
    preset_sections = {section for section, _, _ in combat_presets(flow)}
    assert_equal(sorted(combat_class_sections - preset_sections), [236], "combat candidates without presets")
    assert_equal(sorted(preset_sections - combat_class_sections), [], "combat presets outside combat candidates")


def smoke_preset_structure(flow: dict[str, Any]) -> None:
    for section, entry, preset in combat_presets(flow):
        source_routes = {int(route["Section"]) for route in entry.get("sourceRoutes") or []}
        enemies = preset_enemies(preset)
        assert_true(enemies, f"section {section} enemy data")
        assert_true(str(preset.get("id") or ""), f"section {section} combat id")
        for enemy in enemies:
            assert_true(str(enemy.get("name") or ""), f"section {section} enemy name")
            assert_true(int(enemy.get("cs") or 0) > 0, f"section {section} enemy CS")
            assert_true(int(enemy.get("endurance") or enemy.get("end") or 0) > 0, f"section {section} enemy END")
        for field in ROUTE_FIELDS:
            route = preset.get(field)
            if route:
                assert_true(int(route) in source_routes, f"section {section} {field} source route")
        for route in preset.get("victoryChoices") or []:
            assert_true(int(route) in source_routes, f"section {section} victory choice source route")


def smoke_all_presets_auto_resolve(flow: dict[str, Any]) -> dict[int, int]:
    rounds_by_section: dict[int, int] = {}
    for section, _, preset in combat_presets(flow):
        assistant = fresh_assistant()
        quiet(assistant.set_section, section)
        quiet(assistant.start_section_combat, str(preset["id"]))
        assert_equal(assistant.combat["Active"], True, f"section {section} combat starts")
        assert_equal(assistant.combat["SectionCombatId"], preset["id"], f"section {section} combat id loaded")
        assert_equal(len(assistant.combat["EnemyQueue"]), len(preset_enemies(preset)), f"section {section} enemy queue")

        rounds = 0
        while assistant.combat.get("Active") and rounds < 20:
            quiet(assistant.combat_round, ["combat", "round", "9"])
            rounds += 1

        assert_equal(assistant.combat["Active"], False, f"section {section} combat resolves")
        assert_equal(len(assistant.state["CombatHistory"]), 1, f"section {section} combat archived")
        assert_equal(assistant.state["CurrentSection"], expected_victory_section(section, preset), f"section {section} victory route")
        rounds_by_section[section] = rounds
    return rounds_by_section


def smoke_evasion_edges(flow: dict[str, Any]) -> None:
    evadable = [(section, preset) for section, _, preset in combat_presets(flow) if preset.get("canEvade")]
    assert_equal([section for section, _ in evadable], [43, 169, 191, 220, 231, 339], "evadable sections")

    for section, preset in evadable:
        assistant = fresh_assistant(disciplines=LOW_POWER_DISCIPLINES, combat_skill=1, endurance=100)
        quiet(assistant.set_section, section)
        quiet(assistant.start_section_combat, str(preset["id"]))
        assistant.combat["EnemyEnduranceMax"] = 999
        assistant.combat["EnemyEnduranceCurrent"] = 999
        required_rounds = int(preset.get("evadeAfterRounds") or 0)
        if required_rounds:
            quiet(assistant.evade_combat, ["combat", "evade", "0"])
            assert_equal(assistant.combat["Active"], True, f"section {section} early evade blocked")

        for _ in range(required_rounds):
            quiet(assistant.combat_round, ["combat", "round", "0"])
            assert_equal(assistant.combat["Active"], True, f"section {section} remains active before evasion")

        assert_equal(assistant.can_evade_combat_now(), True, f"section {section} evade ready")
        quiet(assistant.evade_combat, ["combat", "evade", "0"])
        assert_equal(assistant.combat["Active"], False, f"section {section} evade ends combat")
        assert_equal(assistant.state["CurrentSection"], int(preset["evadeRoute"]), f"section {section} evade route")
        assert_equal(assistant.state["CombatHistory"][-1]["Outcome"], "Evaded", f"section {section} evade archive")


def smoke_round_limit_edges(flow: dict[str, Any]) -> None:
    timeout_sections = [section for section, _, preset in combat_presets(flow) if preset.get("roundExceededRoute")]
    assert_equal(timeout_sections, [231, 339], "round-limit sections")

    for section in timeout_sections:
        preset = next(preset for candidate, _, preset in combat_presets(flow) if candidate == section)
        assistant = fresh_assistant(disciplines=LOW_POWER_DISCIPLINES, combat_skill=1, endurance=100)
        quiet(assistant.set_section, section)
        quiet(assistant.start_section_combat, str(preset["id"]))
        assistant.combat["EnemyEnduranceMax"] = 999
        assistant.combat["EnemyEnduranceCurrent"] = 999
        for _ in range(int(preset["roundLimit"])):
            quiet(assistant.combat_round, ["combat", "round", "0"])
            if not assistant.combat.get("Active"):
                break
        assert_equal(assistant.combat["Active"], False, f"section {section} timeout ends combat")
        assert_equal(assistant.state["CurrentSection"], int(preset["roundExceededRoute"]), f"section {section} timeout route")
        assert_equal(assistant.state["CombatHistory"][-1]["Outcome"], "Timed Out", f"section {section} timeout archive")


def smoke_multi_enemy_edges(rounds_by_section: dict[int, int]) -> None:
    assert_equal(rounds_by_section[112], 2, "section 112 two enemies")
    assert_equal(rounds_by_section[180], 3, "section 180 three enemies")
    assert_equal(rounds_by_section[253], 4, "section 253 four enemies")
    assert_equal(rounds_by_section[260], 2, "section 260 forced-unarmed two enemies")
    assert_equal(rounds_by_section[336], 2, "section 336 two enemies")


def main() -> int:
    reset_save_dir()
    flow = load_flow()
    smoke_combat_candidate_coverage(flow)
    smoke_preset_structure(flow)
    rounds_by_section = smoke_all_presets_auto_resolve(flow)
    smoke_evasion_edges(flow)
    smoke_round_limit_edges(flow)
    smoke_multi_enemy_edges(rounds_by_section)
    print("Book 1 combat edge playtest passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Full section-by-section automation coverage audit for onboarded Lone Wolf books.

The audit intentionally records section numbers, signal categories, coverage types,
and behavior-test status. It does not copy book prose into committed artifacts.
"""

from __future__ import annotations

import argparse
import contextlib
import html
import io
import json
import re
import shutil
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import lonewolf_redux  # noqa: E402


BOOKS = {
    1: {"folder": "01fftd", "max": 350, "title": "Flight from the Dark"},
    2: {"folder": "02fotw", "max": 350, "title": "Fire on the Water"},
    3: {"folder": "03tcok", "max": 350, "title": "The Caverns of Kalte"},
    4: {"folder": "04tcod", "max": 350, "title": "The Chasm of Doom"},
    5: {"folder": "05sots", "max": 400, "title": "Shadow on the Sand"},
}

SAVE_ROOT = ROOT / "testing" / "tmp" / "full-section-audit-saves"
JSON_OUT = ROOT / "testing" / "tmp" / "lw_full_section_audit.json"
REPORT_OUT = ROOT / "testing" / "logs" / "LW_FULL_SECTION_AUDIT.md"

BOOK4_CHOICES = [
    "dagger",
    "spear",
    "two-potions-of-laumspur",
    "five-special-rations",
    "chainmail-waistcoat",
    "shield",
]
BOOK5_CHOICES = ["shield", "two-special-rations", "potion-of-laumspur", "sword"]

TERMINAL_DEATH_TERMS = (
    "you are dead",
    "you die instantly",
    "death is instantaneous",
    "your adventure ends",
    "your mission ends here",
    "your quest ends here",
    "your life ends here",
    "your life and your mission end",
    "your mission and your life end",
    "your life and your quest end",
    "your quest and your life end",
    "your life and all hopes",
    "your life and the hopes",
    "your life and the last hope",
    "your life comes to",
    "failed in your mission",
    "mission has failed",
    "stabbed to death",
    "strangled to death",
    "boiled to death",
    "kill yourself",
    "slit your throat",
)
TERMINAL_FAILURE_TERMS = (
    "failed your mission",
    "impossible to complete your mission",
)


def quiet(callable_obj, *args, **kwargs):
    with contextlib.redirect_stdout(io.StringIO()):
        return callable_obj(*args, **kwargs)


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def maintext_block(source: str) -> str:
    match = re.search(
        r"<div[^>]+class=[\"'][^\"']*\bmaintext\b[^\"']*[\"'][^>]*>(.*?)<p id=\"page-navigation\"",
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if match:
        return match.group(1)
    body = re.search(r"<body[^>]*>(.*?)</body>", source, flags=re.IGNORECASE | re.DOTALL)
    return body.group(1) if body else source


def clean_text(block: str) -> str:
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", block))).strip().lower()


def route_links(block: str) -> list[int]:
    routes: list[int] = []
    for match in re.finditer(r"href=[\"'][^\"']*sect(\d+)\.htm", block, flags=re.IGNORECASE):
        route = int(match.group(1))
        if route not in routes:
            routes.append(route)
    return routes


def source_signals(text: str, section: int, max_section: int) -> set[str]:
    signals: set[str] = set()
    if "combat skill" in text and "endurance" in text and any(term in text for term in ("fight", "combat", "enemy", "creature")):
        signals.add("combat")
    if "combat skill" in text and any(term in text for term in ("add", "deduct", "reduce", "increase", "subtract")):
        signals.add("combat_skill_modifier")
    if "endurance" in text and any(term in text for term in ("restore", "regain", "heal", "recover")):
        signals.add("endurance_gain")
    if "endurance" in text and any(term in text for term in ("lose", "deduct", "reduce")):
        signals.add("endurance_loss")
    if any(term in text for term in ("gold crown", "gold crowns", "nobles")):
        signals.add("gold")
    if any(term in text for term in ("gold crown", "gold crowns", "nobles")) and any(
        term in text for term in ("pay", "cost", "fee", "stake", "bet", "wager")
    ):
        signals.add("gold_cost")
    inventory_context = any(term in text for term in ("backpack", "weapon", "special item", "action chart"))
    if inventory_context and any(term in text for term in ("pick up", "receive", "mark it", "record it", "add it", "take the")):
        signals.add("inventory_gain")
    if inventory_context and any(term in text for term in ("erase", "discard", "lose your", "lose all", "remove", "confiscated", "stolen")):
        signals.add("inventory_loss")
    if re.search(r"\b(required meal|eat (?:a|one|two) meal|use (?:a|one|two) meal|erase (?:a|one|two) meal|deduct .*?endurance.*?meal|special rations)\b", text):
        signals.add("meal")
    if "hunting" in text and any(term in text for term in ("meal", "food", "hunt")):
        signals.add("meal")
    if any(term in text for term in ("random number table", "pick a number", "choose a number")):
        signals.add("random")
    if any(term in text for term in ("if you have", "if you possess", "if you do not", "if you lack", "kai discipline")):
        signals.add("route_check")
    if any(term in text for term in ("safekeeping", "stored gear", "recover your equipment", "return your equipment", "confiscated")):
        signals.add("safekeeping")
    if any(term in text for term in ("complete book", "completed book", "next adventure", "next book", "book of the magnakai")):
        signals.add("book_transition")
    if any(term in text for term in TERMINAL_DEATH_TERMS):
        signals.add("terminal_death")
    if any(term in text for term in TERMINAL_FAILURE_TERMS):
        signals.add("terminal_failure")
    if section == max_section:
        signals.add("terminal_success")
    return signals


def parse_signal_categories(book: int) -> dict[int, set[str]]:
    path = ROOT / "testing" / "logs" / f"LWBOOK{book}_AUTOMATION_LANGUAGE_AUDIT.md"
    categories: dict[int, set[str]] = defaultdict(set)
    if not path.exists():
        return categories
    text = path.read_text(encoding="utf-8")
    in_categories = False
    for raw in text.splitlines():
        line = raw.strip()
        if line == "## Sections By Category":
            in_categories = True
            continue
        if in_categories and line.startswith("## "):
            break
        if not in_categories:
            continue
        match = re.match(r"- ([a-z_]+):\s*(.+)$", line)
        if not match:
            continue
        category = match.group(1)
        for value in re.findall(r"\d+", match.group(2)):
            categories[int(value)].add(category)
    return categories


def parse_review_status(book: int) -> dict[int, dict[str, set[str]]]:
    path = ROOT / "testing" / "logs" / f"LWBOOK{book}_AUTOMATION_LANGUAGE_AUDIT.md"
    status: dict[int, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    if not path.exists():
        return status
    text = path.read_text(encoding="utf-8")
    current = ""
    for raw in text.splitlines():
        line = raw.strip()
        if line == "## Reviewed No Automation":
            current = "reviewed-no-automation"
            continue
        if line == "## Reviewed Covered":
            current = "reviewed-covered"
            continue
        if line.startswith("## "):
            current = ""
        match = re.match(r"- Section (\d+):\s*(.+)$", line)
        if not match:
            continue
        section = int(match.group(1))
        detail = match.group(2)
        if "=" in detail:
            for category, value in re.findall(r"([a-z_]+)=([a-z-]+)", detail):
                status[section][category].add(value)
        elif current:
            for category in [part.strip() for part in detail.split(",") if part.strip()]:
                status[section][category].add(current)
    return status


def flow_coverage(flow: dict[str, Any], simple: dict[str, Any]) -> set[str]:
    coverage: set[str] = set()
    if simple:
        coverage.add("simple")
        for action in simple.get("actions", []):
            if isinstance(action, dict):
                action_type = str(action.get("type") or "")
                coverage.add(f"simple:{action_type}")
                if action_type == "ending":
                    coverage.add(f"ending:{action.get('ending')}")
    if flow.get("roll"):
        coverage.add("roll")
    if flow.get("stagedRoll"):
        coverage.add("stagedRoll")
    if flow.get("cartwheel"):
        coverage.add("cartwheel")
    if flow.get("portholes"):
        coverage.add("portholes")
    if flow.get("goldDistraction"):
        coverage.add("goldDistraction")
    if flow.get("combat"):
        coverage.add("combat")
        if any(isinstance(preset, dict) and preset.get("combatRollRoutes") for preset in flow.get("combat") or []):
            coverage.add("combatRollRoutes")
    if flow.get("routeChecks"):
        coverage.add("routeCheck")
    if flow.get("loot"):
        coverage.add("loot")
    if flow.get("lossChoices"):
        coverage.add("lossChoice")
    if flow.get("sourceRoutes"):
        coverage.add("sourceRoutes")
        for route in flow.get("sourceRoutes") or []:
            if not isinstance(route, dict):
                continue
            actions = [action for action in route.get("Actions", route.get("actions", [])) if isinstance(action, dict)]
            if actions:
                coverage.add("routeAction")
            for action in actions:
                action_type = str(action.get("type") or "")
                if action_type:
                    coverage.add(f"routeAction:{action_type}")
    return coverage


def representative_roll(outcome: dict[str, Any]) -> int:
    if "auditRoll" in outcome:
        return int(outcome["auditRoll"])
    if "values" in outcome and outcome["values"]:
        return int(outcome["values"][0])
    if "value" in outcome:
        return int(outcome["value"])
    if "min" in outcome:
        return int(outcome["min"])
    return 0


def collect_routes(value: Any) -> list[int]:
    if isinstance(value, int):
        return [value]
    if isinstance(value, list):
        routes: list[int] = []
        for item in value:
            routes.extend(collect_routes(item))
        return routes
    if isinstance(value, dict):
        routes: list[int] = []
        for item in value.values():
            routes.extend(collect_routes(item))
        return routes
    return []


def reset_saves(book: int) -> tuple[Path, Path]:
    save_dir = SAVE_ROOT / f"book{book}"
    last_save = SAVE_ROOT / f"last-save-book{book}.txt"
    if save_dir.exists():
        shutil.rmtree(save_dir)
    save_dir.mkdir(parents=True, exist_ok=True)
    if last_save.exists():
        last_save.unlink()
    return save_dir, last_save


def fresh_assistant(book: int) -> lonewolf_redux.LoneWolfReduxAssistant:
    save_dir, last_save = reset_saves(book)
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=save_dir, data_dir=ROOT / "data")
    assistant.last_save_file = last_save
    common = {
        "name": "Full Section Audit",
        "kai_disciplines": ["Camouflage", "Hunting", "Sixth Sense", "Tracking", "Weaponskill"],
        "combat_skill_roll": 4,
        "endurance_roll": 6,
        "gold_roll": 5,
        "weaponskill_roll": 5,
    }
    if book == 1:
        assistant.state = lonewolf_redux.create_book1_character_state(**common, starting_find_roll=4)
    elif book == 2:
        assistant.state = lonewolf_redux.create_book2_character_state(**common, armoury_choices=["sword", "two-meals"])
    elif book == 3:
        assistant.state = lonewolf_redux.create_book3_character_state(**common, equipment_choices=["sword", "special-rations"])
    elif book == 4:
        assistant.state = lonewolf_redux.create_book4_character_state(**common, equipment_choices=BOOK4_CHOICES)
    elif book == 5:
        assistant.state = lonewolf_redux.create_book5_character_state(**common, equipment_choices=BOOK5_CHOICES)
    else:
        raise ValueError(f"Unsupported book {book}")
    assistant.character["KaiDisciplines"] = [
        "Camouflage",
        "Hunting",
        "Sixth Sense",
        "Tracking",
        "Healing",
        "Weaponskill",
        "Mindshield",
        "Mindblast",
        "Animal Kinship",
        "Mind Over Matter",
    ][: max(5, min(10, 5 + max(0, book - 1)))]
    assistant.inventory["GoldCrowns"] = 40
    assistant.inventory["Nobles"] = 40
    assistant.inventory["BackpackItems"] = ["Meal", "Meal", "Rope", "Potion of Laumspur (+4 END)", "Tincture of Graveweed"]
    assistant.inventory["Weapons"] = ["Sword", "Dagger", "Spear"]
    assistant.inventory["SpecialItems"] = lonewolf_redux.add_unique_item(assistant.inventory["SpecialItems"], "Sommerswerd")
    assistant.record_section_visit()
    assistant.save_section_checkpoint("ready")
    return assistant


def behavior_check_section(book: int, section: int, flow: dict[str, Any], simple: dict[str, Any]) -> tuple[list[str], list[str]]:
    passed: list[str] = []
    failed: list[str] = []

    try:
        assistant = fresh_assistant(book)
        quiet(assistant.set_section, section)
        payload = assistant.current_section_flow_payload()
        if simple:
            passed.append("simple-entry")
            for action in simple.get("actions", []):
                if isinstance(action, dict) and action.get("type") == "ending":
                    ending = str(action.get("ending") or "")
                    if ending in {"death", "failure"} and not assistant.death_active():
                        failed.append("simple-ending-recovery")
                    elif ending == "success" and assistant.automation["Ending"].get("Type") != "success":
                        failed.append("simple-ending-success")
                    else:
                        passed.append(f"simple-ending-{ending}")
        if flow.get("routeChecks"):
            if payload.get("RouteChecks") is None:
                failed.append("route-check-payload")
            else:
                passed.append("route-check-payload")
        if flow.get("loot"):
            for option in flow.get("loot", []):
                option_id = str(option.get("id") or "")
                if option_id:
                    probe = fresh_assistant(book)
                    quiet(probe.set_section, section)
                    quiet(probe.apply_flow_loot, option_id)
            passed.append("loot-actions")
        if flow.get("lossChoices"):
            if payload.get("LossChoices") is None:
                failed.append("loss-choice-payload")
            else:
                passed.append("loss-choice-payload")
        for route in flow.get("sourceRoutes") or []:
            if not isinstance(route, dict) or not route.get("Actions", route.get("actions")):
                continue
            target = int(route.get("Section") or 0)
            if not target:
                continue
            probe = fresh_assistant(book)
            quiet(probe.set_section, section)
            quiet(probe.follow_route, target)
        if any(isinstance(route, dict) and route.get("Actions", route.get("actions")) for route in flow.get("sourceRoutes") or []):
            passed.append("route-actions")
    except Exception as exc:  # noqa: BLE001
        failed.append(f"section-open:{type(exc).__name__}:{exc}")

    source_routes = {int(route["Section"]) for route in flow.get("sourceRoutes", []) if isinstance(route, dict) and "Section" in route}
    if flow.get("roll"):
        try:
            for raw in range(10):
                probe = fresh_assistant(book)
                quiet(probe.set_section, section)
                result = quiet(probe.roll_current_section, raw)
                route = result.get("Route")
                if route is not None and int(route) not in source_routes:
                    failed.append(f"roll-route-{raw}->{route}-not-source")
                if result.get("Ending") in {"death", "failure"} and not probe.death_active():
                    failed.append(f"roll-terminal-{raw}-no-recovery")
            passed.append("roll-outcomes")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"roll:{type(exc).__name__}:{exc}")
    if flow.get("stagedRoll"):
        try:
            staged = flow["stagedRoll"]
            stages = [stage for stage in staged.get("stages", []) if isinstance(stage, dict)]
            for stage in stages:
                for outcome in [item for item in stage.get("outcomes", []) if isinstance(item, dict)]:
                    raw = representative_roll(outcome)
                    probe = fresh_assistant(book)
                    quiet(probe.set_section, section)
                    # Drive earlier stages through their first next-stage outcome until the target stage is active.
                    active = probe.current_staged_roll_payload().get("Stage")
                    guard = 0
                    while active and str(active) != str(stage.get("id")) and guard < 10:
                        current_stage = next((item for item in stages if str(item.get("id")) == str(active)), None)
                        if not current_stage:
                            break
                        next_outcome = next(
                            (item for item in current_stage.get("outcomes", []) if isinstance(item, dict) and item.get("nextStage")),
                            current_stage.get("outcomes", [{}])[0],
                        )
                        quiet(probe.roll_current_section, representative_roll(next_outcome))
                        active = probe.current_staged_roll_payload().get("Stage")
                        guard += 1
                    result = quiet(probe.roll_current_section, raw)
                    route = result.get("Route")
                    if route is not None and int(route) not in source_routes:
                        failed.append(f"staged-route-{raw}->{route}-not-source")
                    if result.get("Ending") in {"death", "failure"} and not probe.death_active():
                        failed.append(f"staged-terminal-{raw}-no-recovery")
            passed.append("staged-roll-outcomes")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"staged-roll:{type(exc).__name__}:{exc}")
    if flow.get("cartwheel"):
        try:
            probe = fresh_assistant(book)
            quiet(probe.set_section, section)
            probe.inventory["GoldCrowns"] = 10
            quiet(probe.play_cartwheel, 5, 1, 5)
            passed.append("cartwheel-play")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"cartwheel:{type(exc).__name__}:{exc}")
    if flow.get("portholes"):
        try:
            probe = fresh_assistant(book)
            quiet(probe.set_section, section)
            probe.inventory["GoldCrowns"] = 10
            quiet(probe.play_portholes, 1, 1, 2, 2, 9, 9)
            passed.append("portholes-play")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"portholes:{type(exc).__name__}:{exc}")
    if flow.get("goldDistraction"):
        try:
            probe = fresh_assistant(book)
            quiet(probe.set_section, section)
            probe.inventory["GoldCrowns"] = 10
            quiet(probe.play_gold_distraction, 1, 0)
            passed.append("gold-distraction-play")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"gold-distraction:{type(exc).__name__}:{exc}")
    if flow.get("combat"):
        try:
            for preset in flow.get("combat", []):
                preset_id = str(preset.get("id") or "")
                if not preset_id:
                    continue
                probe = fresh_assistant(book)
                quiet(probe.set_section, section)
                quiet(probe.start_section_combat, preset_id)
                if not probe.combat.get("Active"):
                    failed.append(f"combat-not-active:{preset_id}")
            route_keys = {
                "victoryRoute",
                "defeatRoute",
                "evadeRoute",
                "flawlessVictoryRoute",
                "woundedVictoryRoute",
                "playerLossRoute",
                "oneRoundComparisonRoutes",
                "winWithinRoute",
                "tooLateRoute",
                "survivalRoute",
                "roundExceededRoute",
                "victoryChoices",
                "combatRollRoutes",
            }
            for preset in flow.get("combat", []):
                preset_routes: list[int] = []
                for key in route_keys:
                    preset_routes.extend(collect_routes(preset.get(key)))
                unexpected = sorted(set(preset_routes) - source_routes)
                if unexpected:
                    failed.append(f"combat-routes-not-source:{unexpected}")
            passed.append("combat-start")
        except Exception as exc:  # noqa: BLE001
            failed.append(f"combat:{type(exc).__name__}:{exc}")
    return sorted(set(passed)), sorted(set(failed))


def missing_coverage_for_signals(
    signals: set[str],
    flow: dict[str, Any],
    simple: dict[str, Any],
    coverage: set[str],
    review: dict[str, set[str]],
) -> list[str]:
    missing: list[str] = []
    no_route = int(flow.get("sourceRouteCount") or 0) == 0
    for signal in sorted(signals):
        reviewed_values = review.get(signal, set())
        if any(value in reviewed_values for value in ("reviewed-no-automation", "reviewed-covered", "covered")):
            continue
        if signal == "terminal_death" and no_route and "ending:death" not in coverage:
            missing.append(signal)
        elif signal == "terminal_failure" and no_route and "ending:failure" not in coverage:
            missing.append(signal)
        elif signal == "terminal_success" and no_route and "ending:success" not in coverage:
            missing.append(signal)
        elif signal == "random" and not (coverage & {"roll", "stagedRoll", "cartwheel", "portholes", "goldDistraction", "combatRollRoutes"}):
            missing.append(signal)
        elif signal == "combat" and "combat" not in coverage:
            missing.append(signal)
        elif signal in {"endurance_loss", "endurance_gain", "combat_skill_modifier", "gold", "gold_cost", "inventory_gain", "inventory_loss", "meal", "safekeeping"}:
            if not (coverage & {"simple", "routeAction", "loot", "lossChoice", "routeCheck", "roll", "stagedRoll", "cartwheel", "portholes", "goldDistraction", "combat"}):
                missing.append(signal)
        elif signal == "route_check" and not (coverage & {"routeCheck", "roll", "stagedRoll", "combat", "sourceRoutes"}):
            missing.append(signal)
    return missing


def route_check_targets(flow: dict[str, Any]) -> set[int]:
    targets: set[int] = set()
    for check in flow.get("routeChecks") or []:
        if not isinstance(check, dict):
            continue
        for outcome in check.get("outcomes") or []:
            if isinstance(outcome, dict) and outcome.get("route") is not None:
                targets.add(int(outcome["route"]))
    return targets


def audit() -> dict[str, Any]:
    if SAVE_ROOT.exists():
        shutil.rmtree(SAVE_ROOT)
    SAVE_ROOT.mkdir(parents=True, exist_ok=True)
    result: dict[str, Any] = {
        "generated": date.today().isoformat(),
        "books": {},
        "blockers": [],
        "review": [],
    }
    for book, meta in BOOKS.items():
        flow_data = load_json(ROOT / "data" / f"book{book}-section-flows.json")[str(book)]
        simple_data = load_json(ROOT / "data" / f"book{book}-simple-automations.json")[str(book)]
        review_status = parse_review_status(book)
        category_signals = parse_signal_categories(book)
        book_result: dict[str, Any] = {
            "title": meta["title"],
            "sections": {},
            "summary": {},
        }
        signal_counts: Counter[str] = Counter()
        coverage_counts: Counter[str] = Counter()
        behavior_failures: list[str] = []
        missing_signal_coverage: list[str] = []
        for section in range(1, int(meta["max"]) + 1):
            path = ROOT / "books" / "lw" / str(meta["folder"]) / f"sect{section}.htm"
            if not path.exists():
                result["blockers"].append(f"Book {book} section {section}: source file missing")
                continue
            block = maintext_block(path.read_text(encoding="utf-8", errors="ignore"))
            text = clean_text(block)
            routes = route_links(block)
            flow = flow_data.get(str(section), {})
            simple = simple_data.get(str(section), {})
            signals = set(category_signals.get(section) or source_signals(text, section, int(meta["max"])))
            flow_classes = set(flow.get("classification") or [])
            if "terminal_death" in flow_classes:
                signals.add("terminal_death")
            if "terminal_failure" in flow_classes:
                signals.add("terminal_failure")
            if "terminal_success" in flow_classes:
                signals.add("terminal_success")
            coverage = flow_coverage(flow, simple)
            behavior_passed, behavior_failed = behavior_check_section(book, section, flow, simple)
            missing = missing_coverage_for_signals(
                signals,
                flow,
                simple,
                coverage,
                review_status.get(section, {}),
            )
            signal_counts.update(signals)
            coverage_counts.update(coverage)
            if behavior_failed:
                for item in behavior_failed:
                    behavior_failures.append(f"Book {book} section {section}: {item}")
            if missing:
                for item in missing:
                    missing_signal_coverage.append(f"Book {book} section {section}: {item}")
            if "terminal_unclassified" in set(flow.get("classification") or []) and int(flow.get("sourceRouteCount") or 0) == 0:
                result["blockers"].append(f"Book {book} section {section}: unclassified no-route terminal")
            source_route_set = set(routes)
            flow_route_set = {
                int(route["Section"])
                for route in flow.get("sourceRoutes", [])
                if isinstance(route, dict) and "Section" in route
            }
            extra_routes = flow_route_set - source_route_set
            missing_routes = source_route_set - flow_route_set
            allowed_extra_routes = route_check_targets(flow)
            if missing_routes or (extra_routes - allowed_extra_routes):
                result["blockers"].append(f"Book {book} section {section}: source-route mismatch")
            book_result["sections"][str(section)] = {
                "signals": sorted(signals),
                "coverage": sorted(coverage),
                "behaviorPassed": behavior_passed,
                "behaviorFailed": behavior_failed,
                "missingSignalCoverage": missing,
                "flowClassification": sorted(flow.get("classification") or []),
                "sourceRouteCount": len(routes),
            }
        result["blockers"].extend(behavior_failures)
        result["review"].extend(missing_signal_coverage)
        book_result["summary"] = {
            "sections": int(meta["max"]),
            "signalCounts": dict(sorted(signal_counts.items())),
            "coverageCounts": dict(sorted(coverage_counts.items())),
            "behaviorFailureCount": len(behavior_failures),
            "missingSignalCoverageCount": len(missing_signal_coverage),
        }
        result["books"][str(book)] = book_result
    return result


def write_report(data: dict[str, Any]) -> None:
    lines: list[str] = [
        "# Lone Wolf Full Section Automation Audit",
        "",
        f"Generated: {data['generated']}",
        "",
        "Scope: Books 1-5, one section at a time. This report records section numbers, signal categories, coverage, and behavior-test status only.",
        "",
        "## Summary",
        "",
        f"- Blockers: {len(data['blockers'])}",
        f"- Review items: {len(data['review'])}",
        f"- Detail JSON: `testing/tmp/lw_full_section_audit.json`",
        "",
    ]
    for book, book_data in data["books"].items():
        summary = book_data["summary"]
        lines.extend(
            [
                f"## Book {book}: {book_data['title']}",
                "",
                f"- Sections scanned: {summary['sections']}",
                f"- Behavior failures: {summary['behaviorFailureCount']}",
                f"- Signal coverage review items: {summary['missingSignalCoverageCount']}",
                "- Signal counts: "
                + ", ".join(f"{key}={value}" for key, value in summary["signalCounts"].items()),
                "- Coverage counts: "
                + ", ".join(f"{key}={value}" for key, value in summary["coverageCounts"].items()),
                "",
            ]
        )
    lines.extend(["## Blockers", ""])
    if data["blockers"]:
        lines.extend(f"- {item}" for item in data["blockers"][:300])
        if len(data["blockers"]) > 300:
            lines.append(f"- ... {len(data['blockers']) - 300} more in the JSON detail")
    else:
        lines.append("- none")
    lines.extend(["", "## Review Items", ""])
    if data["review"]:
        lines.extend(f"- {item}" for item in data["review"][:300])
        if len(data["review"]) > 300:
            lines.append(f"- ... {len(data['review']) - 300} more in the JSON detail")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Audit Contract",
            "",
            "- `signals` means source language likely implies automation, a helper, or a no-automation ruling.",
            "- `coverage` means an app data hook exists: simple automation, roll helper, staged roll, mini-game, combat, route check, loot, loss choice, route action, or source route.",
            "- `behaviorPassed` means the helper was exercised in an isolated assistant state without touching the live save.",
            "- `behaviorFailed` is a blocker.",
            "- `missingSignalCoverage` is a review item unless a human ruling says source text only.",
            "",
        ]
    )
    REPORT_OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="Write JSON and Markdown audit artifacts.")
    parser.add_argument("--json", action="store_true", help="Print JSON to stdout.")
    args = parser.parse_args()

    data = audit()
    if args.write:
        JSON_OUT.parent.mkdir(parents=True, exist_ok=True)
        JSON_OUT.write_text(json.dumps(data, indent=2), encoding="utf-8")
        write_report(data)
        print(f"Wrote {JSON_OUT}")
        print(f"Wrote {REPORT_OUT}")
    if args.json:
        print(json.dumps(data, indent=2))
    if data["blockers"]:
        print(f"Full section audit found {len(data['blockers'])} blockers.")
        return 1
    print("Full section audit completed with no blockers.")
    if data["review"]:
        print(f"Review items: {len(data['review'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Build and verify the Book 2 section-flow baseline from local HTML."""

from __future__ import annotations

import argparse
import contextlib
import html
import io
import json
import re
import sys
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_NUMBER = 2
BOOK_TITLE = "Fire on the Water"
BOOK_CODE = "02fotw"
BOOK_DIR = ROOT / "books" / "lw" / BOOK_CODE
DATA_PATH = ROOT / "data" / "book2-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK2_SECTION_FLOW_BASELINE.md"
MAX_SECTION = 350

DISCIPLINES = [
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
]


def combat_enemy(name: str, cs: int, endurance: int) -> dict[str, Any]:
    return {"name": name, "cs": cs, "endurance": endurance}


def roll_range(
    minimum: int,
    maximum: int,
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {"test": "range", "min": minimum, "max": maximum, "route": route, "label": label}
    if actions:
        outcome["actions"] = actions
    return outcome


def roll_values(
    values: list[int],
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {"test": "values", "values": values, "route": route, "label": label}
    if actions:
        outcome["actions"] = actions
    return outcome


def section_roll(
    summary: str,
    outcomes: list[dict[str, Any]],
    modifiers: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    roll: dict[str, Any] = {"summary": summary, "outcomes": outcomes}
    if modifiers:
        roll["modifiers"] = modifiers
    return {"roll": roll}


def route_action(section: int, actions: list[dict[str, Any]], effect_label: str) -> dict[str, Any]:
    return {"Section": section, "actions": actions, "effectLabel": effect_label}


def condition_outcome(
    label: str,
    route: int,
    condition: dict[str, Any] | None,
    test_label: str,
) -> dict[str, Any]:
    outcome = {"label": label, "route": route, "testLabel": test_label}
    if condition:
        outcome["conditions"] = [condition]
    return outcome


def cond_power(power: str) -> dict[str, Any]:
    return {"type": "power", "name": power}


def cond_no_power(power: str) -> dict[str, Any]:
    return {"type": "no_power", "name": power}


def cond_item(item: str, container: str = "special", match: str = "exact") -> dict[str, Any]:
    return {"type": "item", "name": item, "containers": [container], "match": match}


def cond_no_item(item: str, container: str = "special", match: str = "exact") -> dict[str, Any]:
    return {"type": "no_item", "name": item, "containers": [container], "match": match}


def cond_item_history(item: str, container: str = "special", match: str = "exact") -> dict[str, Any]:
    return {"type": "item_history", "name": item, "containers": [container], "match": match}


def cond_any(*conditions: dict[str, Any]) -> dict[str, Any]:
    return {"type": "any", "conditions": list(conditions)}


def route_check(
    check_id: str,
    label: str,
    summary: str,
    outcomes: list[dict[str, Any]],
    formula: dict[str, Any] | None = None,
    requires_automation: bool = False,
) -> dict[str, Any]:
    check: dict[str, Any] = {
        "id": check_id,
        "label": label,
        "summary": summary,
        "outcomes": outcomes,
    }
    if formula:
        check["formula"] = formula
    if requires_automation:
        check["requiresAutomationApplied"] = True
    return {"routeChecks": [check]}


def power_route_check(
    section: int,
    power: str,
    power_route: int,
    no_power_route: int | None = None,
    *,
    label: str | None = None,
    optional: bool = False,
) -> dict[str, Any]:
    outcomes = [
        condition_outcome(f"{power} available", power_route, cond_power(power), f"Has {power}")
    ]
    if no_power_route is not None:
        outcomes.append(
            condition_outcome(
                f"No {power}" if not optional else f"No {power} or decline",
                no_power_route,
                cond_no_power(power),
                f"No {power}",
            )
        )
    return route_check(
        f"{section}-{power.lower().replace(' ', '-')}",
        label or f"{power} route",
        f"Checks whether Lone Wolf has {power}.",
        outcomes,
    )


def item_route_check(
    section: int,
    item: str,
    item_route: int,
    no_item_route: int | None = None,
    *,
    label: str | None = None,
    container: str = "special",
    history: bool = False,
) -> dict[str, Any]:
    item_condition = cond_item_history(item, container) if history else cond_item(item, container)
    outcomes = [condition_outcome(f"{item} available", item_route, item_condition, f"Has {item}")]
    if no_item_route is not None:
        outcomes.append(condition_outcome(f"No {item}", no_item_route, cond_no_item(item, container), f"No {item}"))
    return route_check(
        f"{section}-{normalized_choice_key(item)}",
        label or f"{item} route",
        f"Checks whether Lone Wolf has {item}.",
        outcomes,
    )


def stat_route_check(
    section: int,
    stat: str,
    threshold: int,
    gte_route: int,
    lt_route: int,
    *,
    label: str,
    requires_automation: bool = False,
) -> dict[str, Any]:
    stat_label = "Gold Crowns" if stat == "gold" else stat.upper()
    return route_check(
        f"{section}-{stat}-gte-{threshold}",
        label,
        f"Checks current {stat_label}.",
        [
            {"label": f"{stat_label} {threshold} or more", "test": "gte", "value": threshold, "route": gte_route},
            {"label": f"{stat_label} less than {threshold}", "test": "lt", "value": threshold, "route": lt_route},
        ],
        {"label": stat_label, "terms": [{"stat": stat}]},
        requires_automation=requires_automation,
    )


def normalized_choice_key(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def combined_route_checks(*entries: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for entry in entries:
        checks.extend([check for check in entry.get("routeChecks", []) if isinstance(check, dict)])
    return {"routeChecks": checks}


def loot_option(option_id: str, label: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {"id": option_id, "label": label, "actions": actions}


MANUAL_FLOW_AUDIT: dict[str, dict[str, Any]] = {
    "15": {
        "loot": [
            loot_option("broadsword", "Take Broadsword", [{"type": "add_item", "container": "weapon", "name": "Broadsword"}]),
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("quarterstaff", "Take Quarterstaff", [{"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]),
            loot_option("healing-potion", "Take Healing Potion", [{"type": "add_item", "container": "backpack", "name": "Healing Potion"}]),
            loot_option("food", "Take Food for 3 Meals", [{"type": "add_item", "container": "backpack", "name": "Meal"}] * 3),
            loot_option("gold", "Take 12 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 12}]),
        ]
    },
    "21": {
        "loot": [
            loot_option("card-sharp-dagger", "Take Card Sharp's Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}])
        ]
    },
    "55": {
        "loot": [
            loot_option("buy-broadsword", "Buy Broadsword (12 Gold)", [{"type": "stat", "stat": "gold", "delta": -12}, {"type": "add_item", "container": "weapon", "name": "Broadsword"}])
        ]
    },
    "76": {
        "loot": [
            loot_option("halvorc-gold", "Take 2 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 2}]),
            loot_option("halvorc-dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
        ]
    },
    "91": {
        "loot": [
            loot_option("quarterstaff", "Take Quarterstaff", [{"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]),
            loot_option("blanket", "Take Blanket", [{"type": "add_item", "container": "backpack", "name": "Blanket"}]),
            loot_option("two-meals", "Take Food for 2 Meals", [{"type": "add_item", "container": "backpack", "name": "Meal"}] * 2),
            loot_option("backpack", "Take Backpack", [{"type": "backpack", "available": True}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("rope", "Take 30 Feet of Rope", [{"type": "add_item", "container": "backpack", "name": "30 Feet of Rope"}]),
        ]
    },
    "103": {
        "loot": [
            loot_option("store-meal", "Store the Meal", [{"type": "add_item", "container": "backpack", "name": "Meal"}]),
            loot_option("eat-meal", "Eat the Meal", [{"type": "stat", "stat": "end", "delta": 3}]),
        ]
    },
    "106": {
        "loot": [
            loot_option("magic-spear", "Take the Magic Spear", [{"type": "add_item", "container": "special", "name": "Magic Spear"}])
        ]
    },
    "124": {
        "loot": [
            loot_option("gold", "Take 42 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 42}]),
            loot_option("short-sword", "Take Short Sword", [{"type": "add_item", "container": "weapon", "name": "Short Sword"}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
        ]
    },
    "132": {"loot": [loot_option("spear", "Keep the Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}])]},
    "181": {
        "loot": [
            loot_option("buy-sword", "Buy Sword (4 Gold)", [{"type": "stat", "stat": "gold", "delta": -4}, {"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("buy-dagger", "Buy Dagger (2 Gold)", [{"type": "stat", "stat": "gold", "delta": -2}, {"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("buy-short-sword", "Buy Short Sword (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "weapon", "name": "Short Sword"}]),
            loot_option("buy-warhammer", "Buy Warhammer (6 Gold)", [{"type": "stat", "stat": "gold", "delta": -6}, {"type": "add_item", "container": "weapon", "name": "Warhammer"}]),
            loot_option("buy-spear", "Buy Spear (5 Gold)", [{"type": "stat", "stat": "gold", "delta": -5}, {"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("buy-mace", "Buy Mace (4 Gold)", [{"type": "stat", "stat": "gold", "delta": -4}, {"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("buy-blanket", "Buy Fur Blanket (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "backpack", "name": "Fur Blanket"}]),
            loot_option("buy-backpack", "Buy Backpack (1 Gold)", [{"type": "stat", "stat": "gold", "delta": -1}, {"type": "backpack", "available": True}]),
        ]
    },
    "187": {
        "loot": [
            loot_option("gold", "Take 6 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 6}]),
            loot_option("spear-1", "Take Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("spear-2", "Take second Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("sword-1", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("sword-2", "Take second Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
        ]
    },
    "220": {
        "loot": [
            loot_option("poisoner-purse", "Take 23 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 23}])
        ]
    },
    "235": {
        "loot": [
            loot_option("short-sword", "Take Short Sword", [{"type": "add_item", "container": "weapon", "name": "Short Sword"}])
        ]
    },
    "231": {
        "loot": [
            loot_option("gold", "Take 5 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 5}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("seal", "Recover Seal of Hammerdal", [{"type": "add_item", "container": "special", "name": "Seal of Hammerdal"}]),
        ]
    },
    "260": {"loot": [loot_option("sword", "Accept the Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}])]},
    "262": {
        "loot": [
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("quarterstaff", "Take Quarterstaff", [{"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]),
            loot_option("meal", "Take Food for 1 Meal", [{"type": "add_item", "container": "backpack", "name": "Meal"}]),
            loot_option("gold", "Take 6 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 6}]),
            loot_option("orange-potion", "Take Potion of Orange Liquid", [{"type": "add_item", "container": "backpack", "name": "Potion of Orange Liquid"}]),
        ]
    },
    "266": {
        "loot": [
            loot_option("buy-sword", "Buy Sword (4 Gold)", [{"type": "stat", "stat": "gold", "delta": -4}, {"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("buy-dagger", "Buy Dagger (2 Gold)", [{"type": "stat", "stat": "gold", "delta": -2}, {"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("buy-broadsword", "Buy Broadsword (7 Gold)", [{"type": "stat", "stat": "gold", "delta": -7}, {"type": "add_item", "container": "weapon", "name": "Broadsword"}]),
            loot_option("buy-short-sword", "Buy Short Sword (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "weapon", "name": "Short Sword"}]),
            loot_option("buy-warhammer", "Buy Warhammer (6 Gold)", [{"type": "stat", "stat": "gold", "delta": -6}, {"type": "add_item", "container": "weapon", "name": "Warhammer"}]),
            loot_option("buy-spear", "Buy Spear (5 Gold)", [{"type": "stat", "stat": "gold", "delta": -5}, {"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("buy-mace", "Buy Mace (4 Gold)", [{"type": "stat", "stat": "gold", "delta": -4}, {"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("buy-axe", "Buy Axe (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "weapon", "name": "Axe"}]),
            loot_option("buy-quarterstaff", "Buy Quarterstaff (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]),
        ]
    },
    "274": {
        "loot": [
            loot_option("gold", "Take 6 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 6}]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
        ]
    },
    "283": {
        "loot": [
            loot_option("buy-sword", "Buy Sword (4 Gold)", [{"type": "stat", "stat": "gold", "delta": -4}, {"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("buy-dagger", "Buy Dagger (2 Gold)", [{"type": "stat", "stat": "gold", "delta": -2}, {"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("buy-broadsword", "Buy Broadsword (6 Gold)", [{"type": "stat", "stat": "gold", "delta": -6}, {"type": "add_item", "container": "weapon", "name": "Broadsword"}]),
            loot_option("buy-spear", "Buy Spear (5 Gold)", [{"type": "stat", "stat": "gold", "delta": -5}, {"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("buy-meal", "Buy Fine Food Meal (2 Gold)", [{"type": "stat", "stat": "gold", "delta": -2}, {"type": "add_item", "container": "backpack", "name": "Meal"}]),
            loot_option("buy-gold-ring", "Buy Gold Ring (8 Gold)", [{"type": "stat", "stat": "gold", "delta": -8}, {"type": "add_item", "container": "backpack", "name": "Gold Ring"}]),
            loot_option("buy-blanket", "Buy Fur Blanket (3 Gold)", [{"type": "stat", "stat": "gold", "delta": -3}, {"type": "add_item", "container": "backpack", "name": "Fur Blanket"}]),
            loot_option("buy-backpack", "Buy Backpack (1 Gold)", [{"type": "stat", "stat": "gold", "delta": -1}, {"type": "backpack", "available": True}]),
        ]
    },
    "301": {
        "loot": [
            loot_option("gold", "Take 3 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 3}]),
            loot_option("dagger-1", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("dagger-2", "Take second Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("dagger-3", "Take third Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("short-sword", "Take Short Sword", [{"type": "add_item", "container": "weapon", "name": "Short Sword"}]),
        ]
    },
    "302": {
        "loot": [
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("broadsword", "Take Broadsword", [{"type": "add_item", "container": "weapon", "name": "Broadsword"}]),
            loot_option("quarterstaff", "Take Quarterstaff", [{"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]),
            loot_option("healing-potion", "Take Healing Potion", [{"type": "add_item", "container": "backpack", "name": "Healing Potion"}]),
            loot_option("food", "Take Food for 3 Meals", [{"type": "add_item", "container": "backpack", "name": "Meal"}] * 3),
            loot_option("backpack", "Take Backpack", [{"type": "backpack", "available": True}]),
            loot_option("gold", "Take 12 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 12}]),
        ]
    },
    "327": {
        "loot": [
            loot_option(
                "buy-access-papers",
                "Buy access papers",
                [
                    {"type": "stat", "stat": "gold", "delta": -6},
                    {"type": "add_item", "container": "special", "name": "Access Papers"},
                    {"type": "flag", "key": "hasAccessPapers", "value": True},
                ],
            )
        ]
    },
    "331": {
        "loot": [
            loot_option("gold", "Take 3 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": 3}]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
        ]
    },
}


MANUAL_COMBAT_AUDIT: dict[str, dict[str, Any]] = {
    "5": {"combat": [{"id": "5-wounded-helghast", "label": "Wounded Helghast", "enemy": combat_enemy("Wounded Helghast", 22, 20), "enemyImmune": True, "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 166}]},
    "7": {"combat": [{"id": "7-dorier-ganon", "label": "Dorier and Ganon", "enemy": combat_enemy("Dorier and Ganon", 28, 30), "enemyImmune": True, "timedModifiers": [{"startRound": 1, "endRound": 1, "modifier": 2}], "victoryRoute": 33}]},
    "17": {"combat": [{"id": "17-helghast", "label": "Helghast", "enemy": combat_enemy("Helghast", 22, 30), "enemyImmune": True, "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 166}]},
    "30": {"combat": [{"id": "30-zombie-crew", "label": "Zombie Crew", "enemy": combat_enemy("Zombie Crew", 13, 16), "enemyImmune": True, "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 258}]},
    "34": {"combat": [{"id": "34-giaks", "label": "Giaks", "enemy": combat_enemy("Giaks", 16, 14), "victoryRoute": 345}]},
    "60": {"combat": [{"id": "60-halvorc", "label": "Halvorc", "enemy": combat_enemy("Halvorc", 8, 11), "ignorePlayerLossRounds": 2, "victoryRoute": 76}]},
    "66": {"combat": [{"id": "66-zombie-captain", "label": "Zombie Captain", "enemy": combat_enemy("Zombie Captain", 15, 15), "enemyImmune": True, "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 218}]},
    "85": {"combat": [{"id": "85-viveka", "label": "Viveka", "enemy": combat_enemy("Viveka", 24, 27), "victoryRoute": 124}]},
    "90": {"combat": [{"id": "90-villagers-szalls", "label": "Villagers and Szalls", "enemies": [combat_enemy("Villager 1", 10, 16), combat_enemy("Szall 1", 6, 9), combat_enemy("Villager 2", 11, 14), combat_enemy("Szall 2", 5, 8), combat_enemy("Villager 3", 11, 17)], "canEvade": True, "evadeRoute": 132, "victoryRoute": 274}]},
    "106": {"combat": [{"id": "106-helghast", "label": "Helghast", "enemy": combat_enemy("Helghast", 22, 30), "enemyImmune": True, "preActions": [{"type": "add_item", "container": "special", "name": "Magic Spear"}], "activeWeapon": "Magic Spear", "requiredWeapon": "Magic Spear", "perRoundActions": [{"type": "stat", "stat": "end", "delta": -2, "condition": cond_no_power("Mindshield")}], "afterVictoryActions": [{"type": "add_item", "container": "special", "name": "Magic Spear"}], "victoryRoute": 320}]},
    "110": {"combat": [{"id": "110-watchtower-guard", "label": "Watchtower Guard", "enemy": combat_enemy("Watchtower Guard", 15, 22), "canEvade": True, "evadeRoute": 65, "victoryRoute": 331}]},
    "128": {"combat": [{"id": "128-zombie-crew", "label": "Zombie Crew", "enemy": combat_enemy("Zombie Crew", 13, 19), "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 237}]},
    "131": {"combat": [{"id": "131-street-thieves", "label": "Street Thieves", "enemies": [combat_enemy("Street Thief Leader", 15, 23), combat_enemy("Street Thief 1", 13, 21), combat_enemy("Street Thief 2", 13, 20)], "forceUnarmed": True, "canEvade": True, "evadeRoute": 121, "victoryRoute": 301}]},
    "146": {"combat": [{"id": "146-giaks", "label": "Giaks", "enemy": combat_enemy("Giaks", 15, 15), "victoryRoute": 345}]},
    "157": {"combat": [{"id": "157-watchtower-guard", "label": "Watchtower Guard", "enemy": combat_enemy("Watchtower Guard", 15, 22), "canEvade": True, "evadeRoute": 65, "victoryRoute": 331}]},
    "158": {"combat": [{"id": "158-priest", "label": "Priest", "enemy": combat_enemy("Priest", 16, 23), "victoryRoute": 220}]},
    "162": {"combat": [{"id": "162-knight", "label": "Knight of the White Mountain", "enemy": combat_enemy("Knight of the White Mountain", 20, 27), "canEvade": True, "evadeRoute": 244, "victoryRoute": 302}]},
    "185": {"combat": [{"id": "185-drakkarim", "label": "Drakkarim", "enemies": [combat_enemy("Drakkar 1", 17, 25), combat_enemy("Drakkar 2", 16, 26)], "canEvade": True, "evadeRoute": 286, "victoryRoute": 120}]},
    "237": {"combat": [{"id": "237-helghast", "label": "Helghast", "enemy": combat_enemy("Helghast", 23, 30), "enemyImmune": True, "doubleEnemyLossWithSommerswerd": True, "victoryRoute": 309}]},
    "241": {"combat": [{"id": "241-trickster", "label": "Trickster", "enemy": combat_enemy("Trickster", 17, 25), "victoryRoute": 21}]},
    "268": {"combat": [{"id": "268-harbour-thugs", "label": "Harbour Thugs", "enemy": combat_enemy("Harbour Thugs", 16, 25), "canEvade": True, "evadeAfterRounds": 2, "evadeRoute": 125, "victoryRoute": 333}]},
    "270": {"combat": [{"id": "270-ganon-dorier", "label": "Ganon and Dorier", "enemy": combat_enemy("Ganon and Dorier", 28, 30), "enemyImmune": True, "timedModifiers": [{"startRound": 1, "endRound": 1, "modifier": 2}], "victoryRoute": 33}]},
    "276": {"combat": [{"id": "276-arm-wrestling", "label": "Arm-wrestling sailor", "enemy": combat_enemy("Sailor", 18, 25), "fixedPlayerCombatSkill": "current", "restorePlayerEnduranceAfterCombat": True, "victoryRoute": 305, "defeatRoute": 192, "defeatEnduranceMinimum": 1}]},
    "282": {"combat": [{"id": "282-bridge-guards", "label": "Bridge Guards", "enemies": [combat_enemy("Bridge Guard 1", 16, 24), combat_enemy("Bridge Guard 2", 16, 22)], "victoryRoute": 187}]},
    "296": {"combat": [{"id": "296-town-guard", "label": "Town Guard", "enemies": [combat_enemy("Town Guard Sergeant", 13, 22), combat_enemy("Town Guard Corporal", 12, 20), combat_enemy("Town Guard 1", 11, 19), combat_enemy("Town Guard 2", 11, 19), combat_enemy("Town Guard 3", 10, 18), combat_enemy("Town Guard 4", 10, 17)], "canEvade": True, "evadeRoute": 88, "victoryRoute": 221}]},
    "298": {"combat": [{"id": "298-street-thieves", "label": "Street Thieves", "enemies": [combat_enemy("Street Thief Leader", 15, 23), combat_enemy("Street Thief 1", 13, 21), combat_enemy("Street Thief 2", 13, 20)], "forceUnarmed": True, "canEvade": True, "evadeRoute": 121, "victoryRoute": 301}]},
    "306": {"combat": [{"id": "306-border-guard", "label": "Border Guard", "enemy": combat_enemy("Border Guard", 16, 24), "doubleEnemyLoss": True, "victoryRoute": 35}]},
    "326": {"combat": [{"id": "326-drakkar", "label": "Drakkar", "enemy": combat_enemy("Drakkar", 15, 25), "victoryRoute": 184}]},
    "332": {"combat": [{"id": "332-helghast", "label": "Helghast", "enemy": combat_enemy("Helghast", 21, 30), "enemyImmune": True, "perRoundActions": [{"type": "stat", "stat": "end", "delta": -2, "condition": cond_no_power("Mindshield")}], "canEvade": True, "evadeRoute": 183, "victoryRoute": 92}]},
    "345": {"combat": [{"id": "345-drakkar", "label": "Drakkar", "enemy": combat_enemy("Drakkar", 16, 24), "victoryRoute": 243}]},
    "348": {"combat": [{"id": "348-harbour-thugs", "label": "Harbour Thugs", "enemy": combat_enemy("Harbour Thugs", 16, 25), "canEvade": True, "evadeAfterRounds": 2, "evadeRoute": 125, "victoryRoute": 333}]},
}


MANUAL_ROUTE_AUDIT: dict[str, dict[str, Any]] = {
    "2": power_route_check(2, "Sixth Sense", 42, 168, label="Sixth Sense coach warning"),
    "10": section_roll("Random event on the coach journey.", [roll_range(0, 3, 51, "Coach event"), roll_range(4, 6, 195, "Rymerift toll"), roll_range(7, 9, 339, "Exit tax")]),
    "12": section_roll(
        "Samor wager outcome.",
        [roll_range(0, 3, 58, "Lose the game"), roll_range(4, 6, 167, "Drawn game"), roll_range(7, 11, 329, "Win the game")],
        [{"label": "Sixth Sense", "value": 2, "condition": cond_power("Sixth Sense")}],
    ),
    "21": section_roll(
        "Gold left on the table after the card sharp fight.",
        [
            roll_values([0], 314, "30 Crowns on the table; pay 1 for the room", [{"type": "stat", "stat": "gold", "delta": 29}]),
            *[
                roll_values([value], 314, f"{value * 3} Crowns on the table; pay 1 for the room", [{"type": "stat", "stat": "gold", "delta": value * 3 - 1}])
                for value in range(1, 10)
            ],
        ],
    ),
    "22": section_roll("Random wreckage result.", [roll_range(0, 4, 119, "Wreckage route"), roll_range(5, 9, 341, "Alternative wreckage route")]),
    "23": power_route_check(23, "Animal Kinship", 144, 295, label="Animal Kinship bird route"),
    "25": route_check(
        "25-sixth-sense-or-mind-over-matter",
        "Sixth Sense or Mind Over Matter",
        "Checks whether Lone Wolf has either discipline.",
        [
            condition_outcome("Sixth Sense available", 116, cond_power("Sixth Sense"), "Has Sixth Sense"),
            condition_outcome("Mind Over Matter available", 116, cond_power("Mind Over Matter"), "Has Mind Over Matter"),
            condition_outcome("Neither discipline", 153, cond_any(cond_no_power("Sixth Sense"), cond_no_power("Mind Over Matter")), "No matching discipline"),
        ],
    ),
    "31": section_roll("Random route from Rhygar's garden.", [roll_range(0, 4, 176, "Ride to the gate"), roll_range(5, 9, 254, "Enemy ahead")]),
    "32": {
        "sourceRoutes": [
            route_action(136, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"),
            route_action(238, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"),
        ]
    },
    "35": power_route_check(35, "Tracking", 13, None, label="Tracking fork route"),
    "36": route_check(
        "36-laumspur-or-healing",
        "Poison response",
        "Checks whether Lone Wolf has Laumspur or Healing.",
        [
            condition_outcome("Laumspur available", 145, cond_item("Laumspur", "backpack"), "Has Laumspur"),
            condition_outcome("Healing available", 210, cond_power("Healing"), "Has Healing"),
            condition_outcome("No aid available", 275, cond_any(cond_no_item("Laumspur", "backpack"), cond_no_power("Healing")), "No Laumspur or Healing"),
        ],
    ),
    "37": {"sourceRoutes": [route_action(122, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"), route_action(323, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"), route_action(257, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END")]},
    "39": item_route_check(39, "Ticket to Port Bax", 346, 156, label="Ticket discount route", container="special"),
    "40": power_route_check(40, "Sixth Sense", 97, 242, label="Sixth Sense Hammerdal route"),
    "41": {"sourceRoutes": [route_action(194, [{"type": "stat", "stat": "end", "delta": 1}], "Restore 1 END"), {"Section": 251}]},
    "45": section_roll("Random route after the black staff blast.", [roll_range(0, 7, 311, "Thrown into the undergrowth"), roll_range(8, 9, 159, "Worse fall")]),
    "52": item_route_check(52, "Magic Spear", 338, 234, label="Magic Spear route"),
    "57": section_roll("Random Gold loss at the Rymerift.", [roll_values([0], 282, "Lose 10 Gold Crowns", [{"type": "stat", "stat": "gold", "delta": -10}]), *[roll_values([value], 282, f"Lose {value} Gold Crowns", [{"type": "stat", "stat": "gold", "delta": -value}]) for value in range(1, 10)]]),
    "59": item_route_check(59, "Magic Spear", 332, 311, label="Magic Spear route"),
    "62": route_check(
        "62-documents-or-seal",
        "Documents or Seal",
        "Checks access papers and the Seal of Hammerdal.",
        [
            condition_outcome("Access Papers available", 126, cond_item("Access Papers", "special"), "Has Access Papers"),
            condition_outcome("Seal of Hammerdal available", 263, cond_item("Seal of Hammerdal", "special"), "Has Seal"),
            condition_outcome("Neither available", 318, cond_any(cond_no_item("Access Papers", "special"), cond_no_item("Seal of Hammerdal", "special")), "No papers or Seal"),
        ],
    ),
    "63": power_route_check(63, "Animal Kinship", 264, None, label="Animal Kinship snake route"),
    "64": power_route_check(64, "Sixth Sense", 229, None, label="Sixth Sense wagon route"),
    "70": item_route_check(70, "Crystal Star Pendant", 219, 44, label="Crystal Star Pendant route", history=True),
    "72": {"sourceRoutes": [{"Section": 226}, route_action(56, [{"type": "stat", "stat": "gold", "delta": -2}], "Pay 2 Gold Crowns for a room"), {"Section": 276}]},
    "75": {
        **stat_route_check(75, "gold", 10, 142, 318, label="White Pass fee"),
        "sourceRoutes": [route_action(142, [{"type": "stat", "stat": "gold", "delta": -10}, {"type": "add_item", "container": "special", "name": "White Pass"}], "Buy White Pass"), {"Section": 318}],
    },
    "80": item_route_check(80, "Seal of Hammerdal", 15, 189, label="Seal of Hammerdal proof"),
    "81": section_roll("Random longboat result.", [roll_range(0, 4, 260, "Rescue the fishermen"), roll_range(5, 9, 281, "Sail onward")]),
    "88": power_route_check(88, "Camouflage", 179, None, label="Camouflage escape route"),
    "95": route_check("95-healing-aid", "Healing aid", "Checks Healing, Healing Potion, or Laumspur.", [condition_outcome("Healing available", 239, cond_power("Healing"), "Has Healing"), condition_outcome("Healing Potion available", 239, cond_item("Healing Potion", "backpack"), "Has Healing Potion"), condition_outcome("Laumspur available", 239, cond_item("Laumspur", "backpack"), "Has Laumspur")]),
    "99": section_roll("Random ship sighting.", [roll_range(0, 4, 326, "Pirate ship closes"), roll_range(5, 9, 163, "Sighting passes")]),
    "102": power_route_check(102, "Tracking", 325, None, label="Tracking tunnel route"),
    "105": section_roll("Random rope check.", [roll_range(0, 4, 286, "Rope fails"), roll_range(5, 9, 120, "Rope holds")]),
    "107": power_route_check(107, "Healing", 74, 294, label="Healing survivor route"),
    "108": power_route_check(108, "Sixth Sense", 343, 168, label="Sixth Sense last words route", optional=True),
    "114": section_roll("Random roadside camp result.", [roll_range(0, 3, 206, "Camp route"), roll_range(4, 7, 63, "Snake route"), roll_range(8, 9, 8, "Danger route")]),
    "116": section_roll("Cup game winnings with Sixth Sense.", [*[roll_values([value], 314, f"Win {value + 5} Gold Crowns and pay 1 for the room", [{"type": "stat", "stat": "gold", "delta": value + 4}]) for value in range(10)]]),
    "117": {"sourceRoutes": [route_action(37, [{"type": "stat", "stat": "gold", "delta": -3}], "Pay 3 Gold Crowns for coach seat"), route_action(148, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown for roof passage"), {"Section": 292}]},
    "118": power_route_check(118, "Animal Kinship", 279, None, label="Animal Kinship creature route"),
    "122": {
        **power_route_check(122, "Sixth Sense", 96, None, label="Sixth Sense orange door route"),
        **section_roll("Random orange-door route if Sixth Sense is unavailable.", [roll_range(0, 4, 46, "Orange door danger"), roll_range(5, 9, 112, "Alternative route")]),
    },
    "127": {"sourceRoutes": [route_action(217, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"), route_action(143, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END")]},
    "134": item_route_check(134, "Magic Spear", 38, 304, label="Magic Spear route"),
    "136": {
        **stat_route_check(136, "gold", 20, 10, 238, label="Port Bax coach fare"),
        "sourceRoutes": [route_action(10, [{"type": "stat", "stat": "gold", "delta": -20}, {"type": "add_item", "container": "special", "name": "Ticket to Port Bax"}], "Buy ticket to Port Bax"), {"Section": 238}],
    },
    "148": {"sourceRoutes": [route_action(122, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"), route_action(323, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END"), route_action(257, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or lose 3 END")]},
    "149": item_route_check(149, "Seal of Hammerdal", 223, 250, label="Seal of Hammerdal route"),
    "150": {"sourceRoutes": [route_action(261, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or use Hunting"), route_action(334, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": True}], "Eat a Meal or use Hunting")]},
    "151": section_roll("Random bluff result.", [roll_range(0, 4, 262, "Bluff succeeds"), roll_range(5, 9, 110, "Bluff fails")]),
    "152": section_roll("Random route after leaving Port Bax.", [roll_range(0, 3, 216, "At sea route"), roll_range(4, 6, 49, "At sea route"), roll_range(7, 9, 193, "At sea route")]),
    "160": combined_route_checks(power_route_check(160, "Healing", 16, None, label="Healing proof"), power_route_check(160, "Mindblast", 133, None, label="Mindblast proof"), power_route_check(160, "Weaponskill", 255, None, label="Weaponskill proof"), power_route_check(160, "Animal Kinship", 203, None, label="Animal Kinship proof"), power_route_check(160, "Mind Over Matter", 48, None, label="Mind Over Matter proof")),
    "164": power_route_check(164, "Sixth Sense", 172, None, label="Sixth Sense platform route"),
    "168": {
        **stat_route_check(168, "gold", 1, 314, 25, label="Room cost"),
        "sourceRoutes": [route_action(314, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown for a room"), {"Section": 25}],
    },
    "169": section_roll("Random coach route.", [roll_range(0, 3, 39, "Inn stop"), roll_range(4, 6, 249, "Rymerift route"), roll_range(7, 9, 339, "Exit tax route")]),
    "175": section_roll("Random sea-fog result.", [roll_range(0, 4, 53, "Fire aftermath"), roll_range(5, 9, 209, "Ship route")]),
    "176": power_route_check(176, "Sixth Sense", 322, None, label="Sixth Sense gate route"),
    "179": power_route_check(179, "Camouflage", 82, None, label="Camouflage hay-cart route"),
    "183": section_roll("Random fall in the forest.", [roll_range(0, 8, 311, "Hard fall"), roll_range(9, 9, 159, "Worst fall")]),
    "195": {
        **stat_route_check(195, "gold", 1, 249, 50, label="Rymerift toll"),
        "sourceRoutes": [route_action(249, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown toll"), {"Section": 50}],
    },
    "196": power_route_check(196, "Sixth Sense", 79, 123, label="Sixth Sense Sommerswerd revelation"),
    "197": section_roll("Random falling mast result.", [roll_range(1, 4, 78, "Mast strikes nearby"), roll_range(5, 9, 141, "Thrown into sea"), roll_range(0, 0, 247, "Clean dodge")]),
    "201": section_roll("Random snake strike result.", [roll_range(0, 4, 285, "Snake misses"), roll_range(5, 9, 70, "Snake bites")]),
    "210": section_roll("Random poison struggle.", [roll_range(0, 4, 275, "Poison wins"), roll_range(5, 9, 330, "Survive the poison")]),
    "217": {"sourceRoutes": [route_action(199, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown for directions"), {"Section": 143}]},
    "226": {"sourceRoutes": [route_action(56, [{"type": "stat", "stat": "gold", "delta": -2}], "Pay 2 Gold Crowns for a room"), {"Section": 276}]},
    "232": combined_route_checks(power_route_check(232, "Sixth Sense", 149, None, label="Sixth Sense guard route"), item_route_check(232, "Seal of Hammerdal", 223, None, label="Seal of Hammerdal route")),
    "233": {"sourceRoutes": [route_action(37, [{"type": "stat", "stat": "gold", "delta": -3}], "Pay 3 Gold Crowns for coach seat"), route_action(148, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown for roof passage"), {"Section": 292}]},
    "238": {"sourceRoutes": [route_action(169, [{"type": "weapons", "available": True}], "Recover checked Weapons"), route_action(186, [{"type": "weapons", "available": True}], "Recover checked Weapons")]},
    "239": power_route_check(239, "Camouflage", 77, 28, label="Camouflage Szall route"),
    "240": {"sourceRoutes": [route_action(29, [{"type": "stat", "stat": "end", "mode": "restore_max", "condition": cond_power("Healing")}, {"type": "stat", "stat": "end", "mode": "restore_combat_loss_half_floor", "condition": cond_no_power("Healing")}], "Recover after the fire"), route_action(236, [{"type": "stat", "stat": "end", "mode": "restore_max", "condition": cond_power("Healing")}, {"type": "stat", "stat": "end", "mode": "restore_combat_loss_half_floor", "condition": cond_no_power("Healing")}], "Recover after the fire"), route_action(101, [{"type": "stat", "stat": "end", "mode": "restore_max", "condition": cond_power("Healing")}, {"type": "stat", "stat": "end", "mode": "restore_combat_loss_half_floor", "condition": cond_no_power("Healing")}], "Recover after the fire")]},
    "244": power_route_check(244, "Tracking", 147, None, label="Tracking bridge route"),
    "246": route_check("246-pass", "Harbour pass", "Checks White Pass and Red Pass.", [condition_outcome("White Pass available", 170, cond_item("White Pass"), "Has White Pass"), condition_outcome("Red Pass available", 202, cond_item("Red Pass"), "Has Red Pass"), condition_outcome("No pass", 327, cond_any(cond_no_item("White Pass"), cond_no_item("Red Pass")), "No pass")]),
    "254": power_route_check(254, "Sixth Sense", 344, None, label="Sixth Sense ambush route"),
    "258": power_route_check(258, "Sixth Sense", 272, None, label="Sixth Sense hold route"),
    "265": power_route_check(265, "Tracking", 252, None, label="Tracking city route"),
    "271": power_route_check(271, "Camouflage", 151, None, label="Camouflage password route"),
    "276": power_route_check(276, "Mindblast", 14, None, label="Mindblast arm-wrestling route"),
    "278": section_roll("Random cloak signal result.", [roll_range(0, 6, 41, "Fishing boat sees you"), roll_range(7, 9, 180, "No rescue")]),
    "280": section_roll("Random Wildlands accident.", [roll_range(0, 4, 2, "Accident route"), roll_range(5, 9, 108, "Injury route")]),
    "289": {"sourceRoutes": [route_action(165, [{"type": "stat", "stat": "gold", "delta": 40}, {"type": "remove_item", "containers": ["special"], "name": "Seal of Hammerdal"}], "Sell the Seal of Hammerdal"), {"Section": 186}]},
    "299": item_route_check(299, "Magic Spear", 102, 118, label="Keep Magic Spear route"),
    "300": section_roll("Random departure from Holmgard.", [roll_range(0, 1, 224, "Sea route"), roll_range(2, 3, 316, "Distress ship"), roll_range(4, 5, 81, "Longboat"), roll_range(6, 7, 22, "Wreckage"), roll_range(8, 9, 99, "Pirate ship")]),
    "314": {
        **power_route_check(314, "Hunting", 290, None, label="Hunting poisoned food warning"),
        "sourceRoutes": [{"Section": 290}, {"Section": 36}, route_action(178, [{"type": "meal", "count": 1, "mode": "all_or_loss", "enduranceLoss": 3, "huntingExempt": False}], "Eat a Meal or lose 3 END")],
    },
    "315": power_route_check(315, "Mind Over Matter", 287, None, label="Mind Over Matter lock route"),
    "316": section_roll("Random distress-ship route.", [roll_range(0, 4, 107, "Survivor route"), roll_range(5, 9, 94, "Sail on")]),
    "328": combined_route_checks(item_route_check(328, "Crystal Star Pendant", 113, None, label="Crystal Star Pendant history route", history=True), power_route_check(328, "Tracking", 204, None, label="Tracking staff route")),
    "334": power_route_check(334, "Tracking", 98, None, label="Tracking forest route"),
    "337": {"sourceRoutes": [{"Section": 139}, {"Section": 228}, route_action(171, [{"type": "stat", "stat": "end", "delta": -3}], "Decline fruit and lose 3 END")]},
    "338": {"sourceRoutes": [{"Section": 269}, route_action(349, [{"type": "remove_item", "containers": ["special"], "name": "Magic Spear"}], "Leave the Magic Spear behind")]},
    "339": {
        **stat_route_check(339, "gold", 1, 249, 50, label="Exit tax"),
        "sourceRoutes": [route_action(249, [{"type": "stat", "stat": "gold", "delta": -1}], "Pay 1 Gold Crown exit tax"), {"Section": 50}],
    },
    "342": {"sourceRoutes": [route_action(72, [{"type": "stat", "stat": "gold", "delta": -1}], "Buy ale for 1 Gold Crown"), route_action(56, [{"type": "stat", "stat": "gold", "delta": -2}], "Pay 2 Gold Crowns for a room"), {"Section": 226}]},
    "346": {
        **route_check(
            "346-meal-or-gold",
            "Wildlands Meal",
            "Checks whether Lone Wolf can eat a Meal or pay for one.",
            [
                condition_outcome("Meal available", 280, cond_item("Meal", "backpack"), "Has Meal"),
                {"label": "Gold Crown available", "test": "gte", "value": 1, "route": 280},
                {"label": "No Meal or Gold", "test": "lt", "value": 1, "route": 205},
            ],
            {"label": "Gold Crowns", "terms": [{"stat": "gold"}]},
            requires_automation=True,
        ),
        "sourceRoutes": [route_action(280, [{"type": "meal_or_gold", "count": 1, "goldCost": 1}], "Eat a Meal or pay 1 Gold Crown"), {"Section": 205}],
    },
}


def clean_text(source: str) -> str:
    text = re.sub(r"<[^>]+>", " ", source)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def maintext_block(source: str) -> str:
    match = re.search(
        r"<div\b[^>]*class=[\"'][^\"']*\bmaintext\b[^\"']*[\"'][^>]*>",
        source,
        flags=re.IGNORECASE,
    )
    if not match:
        return source
    end = source.find('<p id="page-navigation"', match.end())
    if end == -1:
        end = source.find("</article>", match.end())
    if end == -1:
        end = len(source)
    return source[match.end() : end]


def unique_routes(block: str) -> list[int]:
    routes: list[int] = []
    for match in re.finditer(r"href=[\"'][^\"']*sect(\d+)\.htm", block, flags=re.IGNORECASE):
        route = int(match.group(1))
        if route not in routes:
            routes.append(route)
    return routes


def add_class(classes: list[str], value: str) -> None:
    if value not in classes:
        classes.append(value)


def classify_section(block: str, routes: list[int], section: int) -> list[str]:
    text = clean_text(block).lower()
    block_lower = block.lower()
    classes: list[str] = []

    if len(routes) > 1:
        add_class(classes, "route_choice")
    elif len(routes) == 1:
        add_class(classes, "single_route")

    if "random number table" in text or "pick a number" in text:
        add_class(classes, "random")
    if 'class="combat"' in block_lower or ("combat skill" in text and "endurance" in text):
        add_class(classes, "combat")
    if "kai discipline" in text or any(discipline.lower() in text for discipline in DISCIPLINES):
        add_class(classes, "kai_discipline_check")
    if "meal" in text or "food" in text:
        add_class(classes, "meal")
    if "gold crown" in text or "gold crowns" in text:
        add_class(classes, "gold")
    if any(term in text for term in ("backpack", "weapon", "special item", "action chart")):
        add_class(classes, "inventory")
    if "endurance" in text and any(term in text for term in ("lose", "deduct", "reduce")):
        add_class(classes, "endurance_loss")
    if "endurance" in text and any(term in text for term in ("restore", "regain", "heal")):
        add_class(classes, "endurance_gain")
    if "combat skill" in text and any(term in text for term in ("add", "deduct", "reduce", "increase")):
        add_class(classes, "combat_skill_modifier")
    if any(term in text for term in ("you are dead", "your adventure ends", "mission has failed")):
        add_class(classes, "terminal_death")
    if section == MAX_SECTION or "the caverns of kalte" in text:
        add_class(classes, "terminal_success")
    if not routes and not any(value.startswith("terminal_") for value in classes):
        add_class(classes, "terminal_unclassified")
    if not classes:
        add_class(classes, "story")
    return classes


def build_graph() -> tuple[dict[str, Any], dict[str, Any]]:
    expected = set(range(1, MAX_SECTION + 1))
    sections: dict[int, dict[str, Any]] = {}
    invalid_links: list[dict[str, int]] = []

    for section in range(1, MAX_SECTION + 1):
        path = BOOK_DIR / f"sect{section}.htm"
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8", errors="ignore")
        block = maintext_block(source)
        routes = unique_routes(block)
        for target in routes:
            if target not in expected:
                invalid_links.append({"section": section, "target": target})
        sections[section] = {
            "auditStatus": "source-link-baseline",
            "classification": classify_section(block, routes, section),
            "sourceRouteCount": len(routes),
            "sourceRoutes": [{"Section": route} for route in routes],
        }

    incoming: dict[int, list[int]] = {section: [] for section in expected}
    for section, entry in sections.items():
        for route in entry["sourceRoutes"]:
            target = int(route["Section"])
            if target in incoming:
                incoming[target].append(section)

    for section, entry in sections.items():
        entry["incomingRouteCount"] = len(incoming.get(section, []))

    for manual_audit in (MANUAL_FLOW_AUDIT, MANUAL_COMBAT_AUDIT, MANUAL_ROUTE_AUDIT):
        for section, override in manual_audit.items():
            if int(section) in sections:
                sections[int(section)].update(override)

    reachable: set[int] = set()
    queue: deque[int] = deque([1])
    while queue:
        section = queue.popleft()
        if section in reachable:
            continue
        reachable.add(section)
        for route in sections.get(section, {}).get("sourceRoutes", []):
            target = int(route["Section"])
            if target in sections and target not in reachable:
                queue.append(target)

    missing_sections = sorted(expected - set(sections))
    unreachable = sorted(expected - reachable)
    terminal_sections = [
        section
        for section, entry in sections.items()
        if int(entry["sourceRouteCount"]) == 0
    ]
    branch_sections = [
        section
        for section, entry in sections.items()
        if int(entry["sourceRouteCount"]) >= 2
    ]
    classified_counts: dict[str, int] = {}
    for entry in sections.values():
        for value in entry["classification"]:
            classified_counts[value] = classified_counts.get(value, 0) + 1

    meta = {
        "schemaVersion": 1,
        "bookNumber": BOOK_NUMBER,
        "title": BOOK_TITLE,
        "source": f"books/lw/{BOOK_CODE}/sect*.htm",
        "generatedBy": "testing/lwbook2_section_flow_audit.py",
        "sectionCount": len(sections),
        "expectedSectionCount": MAX_SECTION,
        "sourceRouteLinkCount": sum(int(entry["sourceRouteCount"]) for entry in sections.values()),
        "branchSectionCount": len(branch_sections),
        "terminalSectionCount": len(terminal_sections),
        "reachableFromSection1Count": len(reachable),
        "invalidSectionLinkCount": len(invalid_links),
        "missingSectionCount": len(missing_sections),
    }

    data: dict[str, Any] = {str(BOOK_NUMBER): {"_meta": meta}}
    for section in range(1, MAX_SECTION + 1):
        if section in sections:
            data[str(BOOK_NUMBER)][str(section)] = sections[section]

    artifact = {
        "meta": meta,
        "missingSections": missing_sections,
        "invalidLinks": invalid_links,
        "unreachableFromSection1": unreachable,
        "terminalSections": terminal_sections,
        "branchSections": branch_sections,
        "classificationCounts": dict(sorted(classified_counts.items())),
        "manualFlowAuditCount": len(MANUAL_FLOW_AUDIT),
        "manualLootAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "loot" in entry),
        "manualCombatAuditCount": len(MANUAL_COMBAT_AUDIT),
        "manualRouteAuditCount": len(MANUAL_ROUTE_AUDIT),
        "manualRollAuditCount": sum(1 for entry in MANUAL_ROUTE_AUDIT.values() if "roll" in entry),
        "manualRouteCheckAuditCount": sum(1 for entry in MANUAL_ROUTE_AUDIT.values() if "routeChecks" in entry),
        "section1Routes": [route["Section"] for route in sections.get(1, {}).get("sourceRoutes", [])],
        "section350Classes": sections.get(350, {}).get("classification", []),
    }
    return data, artifact


def render_report(artifact: dict[str, Any]) -> str:
    meta = artifact["meta"]
    invalid = artifact["invalidLinks"]
    missing = artifact["missingSections"]
    unreachable = artifact["unreachableFromSection1"]
    counts = artifact["classificationCounts"]

    lines = [
        "# LW Book 2 Section Flow Baseline",
        "",
        "Scope: source-link graph for local Project Aon Book 2 section files.",
        "",
        "This report records section numbers, graph counts, and audit classifications only. Do not copy Book 2 prose into committed audit artifacts.",
        "",
        "## Summary",
        "",
        f"- Sections found: {meta['sectionCount']} / {meta['expectedSectionCount']}",
        f"- Source route links: {meta['sourceRouteLinkCount']}",
        f"- Branch sections: {meta['branchSectionCount']}",
        f"- Terminal sections: {meta['terminalSectionCount']}",
        f"- Reachable from section 1: {meta['reachableFromSection1Count']} / {meta['expectedSectionCount']}",
        f"- Missing section files: {meta['missingSectionCount']}",
        f"- Invalid section links: {meta['invalidSectionLinkCount']}",
        "",
        "## Baseline Checks",
        "",
        f"- Section 1 routes: {', '.join(str(item) for item in artifact['section1Routes'])}",
        f"- Section 350 classifications: {', '.join(artifact['section350Classes'])}",
        f"- Missing sections: {', '.join(str(item) for item in missing) if missing else 'none'}",
        f"- Invalid links: {json.dumps(invalid) if invalid else 'none'}",
        f"- Unreachable sections from section 1: {', '.join(str(item) for item in unreachable) if unreachable else 'none'}",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in counts.items():
        lines.append(f"- {key}: {value}")
    lines.extend(
        [
            "",
            "## Data Artifact",
            "",
            "- `data/book2-section-flows.json` now contains one entry for every discovered section.",
            "- `sourceRoutes` is the compact legal-link baseline used by the assistant.",
            "- `classification` is heuristic and remains useful for future review slices.",
            f"- {artifact['manualLootAuditCount']} sections include confirmed optional loot buttons.",
            f"- {artifact['manualCombatAuditCount']} sections include confirmed combat presets.",
            f"- {artifact['manualRollAuditCount']} sections include confirmed roll helpers.",
            f"- {artifact['manualRouteCheckAuditCount']} sections include confirmed route checks.",
            "",
            "## Remaining Risk",
            "",
            "- The automation-language audit currently reports zero uncovered signal categories.",
            "- Broader real-route play may still find helper wording or timing that deserves polish.",
            "- Stake-based gambling sections remain manual because the player chooses the wager.",
        ]
    )
    return "\n".join(lines) + "\n"


def verify_assistant_routes() -> list[str]:
    sys.path.insert(0, str(ROOT))
    import lonewolf_redux  # pylint: disable=import-error,import-outside-toplevel

    save_dir = ROOT / "testing" / "tmp" / "book2-section-flow-saves"
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=save_dir, data_dir=ROOT / "data")
    assistant.last_save_file = ROOT / "testing" / "tmp" / "book2-section-flow-last-save.txt"
    assistant.state = lonewolf_redux.create_book2_character_state(
        name="Book Two Route Smoke",
        kai_disciplines=lonewolf_redux.KAI_DISCIPLINES[:5],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=3,
        weaponskill_roll=6,
        armoury_choices=["sword", "two-meals"],
    )
    assistant.record_section_visit()

    errors: list[str] = []
    flow = assistant.current_section_flow_payload()
    routes = [int(route["Section"]) for route in flow.get("SourceRoutes", [])]
    if routes != [273, 160]:
        errors.append(f"assistant section 1 routes were {routes}")
    route_audit = flow.get("RouteAudit", {})
    if route_audit.get("Status") != "source-link-baseline":
        errors.append(f"assistant route audit status was {route_audit.get('Status')!r}")

    with contextlib.redirect_stdout(io.StringIO()):
        assistant.follow_route(273)
    if int(assistant.state["CurrentSection"]) != 273:
        errors.append("assistant did not follow legal route 1 -> 273")

    with contextlib.redirect_stdout(io.StringIO()):
        assistant.set_section(1)
        assistant.follow_route(2)
    if int(assistant.state["CurrentSection"]) != 1:
        errors.append("assistant allowed illegal route 1 -> 2")
    return errors


def normalized_json(data: dict[str, Any]) -> str:
    return json.dumps(data, indent=2, ensure_ascii=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="write data and report artifacts")
    parser.add_argument("--check", action="store_true", help="verify checked-in data matches local source files")
    args = parser.parse_args(argv)

    if not BOOK_DIR.exists():
        print(f"Book directory not found: {BOOK_DIR}", file=sys.stderr)
        return 2

    data, artifact = build_graph()
    output = normalized_json(data)

    if args.write:
        DATA_PATH.write_text(output, encoding="utf-8")
        REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")
        print(f"Wrote {DATA_PATH}")
        print(f"Wrote {REPORT_PATH}")

    if args.check:
        if not DATA_PATH.exists():
            print(f"Missing {DATA_PATH}", file=sys.stderr)
            return 1
        current = DATA_PATH.read_text(encoding="utf-8")
        if current != output:
            print(f"{DATA_PATH} is out of date. Run this script with --write.", file=sys.stderr)
            return 1
        if artifact["missingSections"] or artifact["invalidLinks"]:
            print("Section source integrity failed.", file=sys.stderr)
            return 1
        if artifact["section1Routes"] != [273, 160]:
            print(f"Unexpected section 1 routes: {artifact['section1Routes']}", file=sys.stderr)
            return 1
        if "terminal_success" not in artifact["section350Classes"]:
            print("Section 350 is not classified as terminal_success.", file=sys.stderr)
            return 1
        assistant_errors = verify_assistant_routes()
        if assistant_errors:
            for error in assistant_errors:
                print(error, file=sys.stderr)
            return 1
        print("Book 2 section-flow baseline check passed.")

    if not args.write and not args.check:
        print(render_report(artifact))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

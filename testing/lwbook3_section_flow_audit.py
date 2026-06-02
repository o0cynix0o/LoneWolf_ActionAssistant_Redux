#!/usr/bin/env python3
"""Build and verify the Book 3 section-flow baseline from local HTML."""

from __future__ import annotations

import argparse
import gzip
import html
import json
import re
import sys
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_NUMBER = 3
BOOK_TITLE = "The Caverns of Kalte"
BOOK_CODE = "03tcok"
BOOK_DIR = ROOT / "books" / "lw" / BOOK_CODE
DATA_PATH = ROOT / "data" / "book3-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK3_SECTION_FLOW_BASELINE.md"
GRAPH_REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK3_ROUTE_GRAPH_CHECK.md"
MAX_SECTION = 350
SVG_GRAPH_URL = f"https://www.projectaon.org/en/svg/lw/{BOOK_CODE}.svgz"


def combat_enemy(name: str, cs: int, endurance: int) -> dict[str, Any]:
    return {"name": name, "cs": cs, "endurance": endurance}


def combat_preset(
    section: int,
    label: str,
    enemies: list[dict[str, Any]] | dict[str, Any],
    **kwargs: Any,
) -> dict[str, Any]:
    preset: dict[str, Any] = {
        "id": f"{section}-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}",
        "label": label,
    }
    if isinstance(enemies, list) and len(enemies) > 1:
        preset["enemies"] = enemies
    elif isinstance(enemies, list):
        preset["enemy"] = enemies[0]
    else:
        preset["enemy"] = enemies
    preset.update(kwargs)
    return preset


def loot_option(option_id: str, label: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {"id": option_id, "label": label, "actions": actions}


def add_items(container: str, name: str, count: int) -> list[dict[str, Any]]:
    return [{"type": "add_item", "container": container, "name": name} for _ in range(count)]


def roll_range(
    minimum: int,
    maximum: int,
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
    ending: str = "",
    cause: str = "",
) -> dict[str, Any]:
    outcome: dict[str, Any] = {"test": "range", "min": minimum, "max": maximum, "label": label}
    if route is not None:
        outcome["route"] = route
    if actions:
        outcome["actions"] = actions
    if ending:
        outcome["ending"] = ending
    if cause:
        outcome["cause"] = cause
    return outcome


def roll_values(
    values: list[int],
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
    ending: str = "",
    cause: str = "",
) -> dict[str, Any]:
    outcome: dict[str, Any] = {"test": "values", "values": values, "label": label}
    if route is not None:
        outcome["route"] = route
    if actions:
        outcome["actions"] = actions
    if ending:
        outcome["ending"] = ending
    if cause:
        outcome["cause"] = cause
    return outcome


def section_roll(
    summary: str,
    outcomes: list[dict[str, Any]],
    modifiers: list[dict[str, Any]] | None = None,
    *,
    zero_as_ten: bool = False,
) -> dict[str, Any]:
    roll: dict[str, Any] = {"summary": summary, "outcomes": outcomes}
    if modifiers:
        roll["modifiers"] = modifiers
    if zero_as_ten:
        roll["zeroAsTen"] = True
    return {"roll": roll}


def cond_power(power: str) -> dict[str, Any]:
    return {"type": "power", "name": power}


def cond_any(*conditions: dict[str, Any]) -> dict[str, Any]:
    return {"type": "any", "conditions": list(conditions)}


def cond_end_lt(value: int) -> dict[str, Any]:
    return {"type": "end_lt", "value": value}


def cond_end_gte(value: int) -> dict[str, Any]:
    return {"type": "end_gte", "value": value}


def cond_flag(key: str, value: Any = True) -> dict[str, Any]:
    return {"type": "flag", "key": key, "value": value}


def cond_no_flag(key: str, value: Any = True) -> dict[str, Any]:
    return {"type": "no_flag", "key": key, "value": value}


def cond_active_weaponskill() -> dict[str, Any]:
    return {"type": "active_weaponskill_weapon"}


def end_delta(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "end", "delta": delta}


def end_loss_from_roll_total() -> dict[str, Any]:
    return {"type": "stat", "stat": "end", "deltaFrom": "roll_total", "multiplier": -1, "maxDelta": 0}


MANUAL_FLOW_AUDIT: dict[str, dict[str, Any]] = {
    "4": {
        "loot": [
            loot_option("bone-sword", "Take Bone Sword", [{"type": "add_item", "container": "special", "name": "Bone Sword"}]),
            loot_option("blue-stone-disc", "Take Blue Stone Disc", [{"type": "add_item", "container": "special", "name": "Blue Stone Disc"}]),
        ]
    },
    "8": {
        "loot": [
            loot_option("baknar-oil", "Take Baknar Oil", [{"type": "add_item", "container": "backpack", "name": "Baknar Oil"}])
        ]
    },
    "12": {
        "loot": [
            loot_option("food", "Take remaining Food for 2 Meals", add_items("backpack", "Meal", 2)),
            loot_option("sleeping-furs", "Take Sleeping Furs", [{"type": "add_item", "container": "backpack", "name": "Sleeping Furs (2 spaces)"}]),
            loot_option("rope", "Take Rope", [{"type": "add_item", "container": "backpack", "name": "Rope"}]),
        ]
    },
    "16": {
        "lossChoices": [
            {
                "id": "crushed-pack-item-1",
                "label": "Discard crushed Backpack Item 1",
                "summary": "Choose the first Backpack Item crushed by the stone door.",
                "containers": ["backpack"],
            },
            {
                "id": "crushed-pack-item-2",
                "label": "Discard crushed Backpack Item 2",
                "summary": "Choose the second Backpack Item crushed by the stone door.",
                "containers": ["backpack"],
            },
        ]
    },
    "18": {
        "lossChoices": [
            {
                "id": "cyclone-weapon-loss",
                "label": "Lose weapon to the cyclone",
                "summary": "Choose the weapon or weapon-like Special Item lost to the ice cyclone.",
                "containers": ["weapon"],
                "fallbackContainers": ["special"],
            }
        ]
    },
    "25": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}])
        ]
    },
    "26": {
        "loot": [
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
        ]
    },
    "29": section_roll(
        "Sledge-rope escape roll.",
        [
            roll_values([0], 312, "Dragged into the crevasse"),
            roll_range(1, 4, 226, "Free your foot"),
            roll_range(5, 9, 266, "Leap clear"),
        ],
    ),
    "38": {
        "loot": [
            loot_option("fur-backpack", "Take fur Backpack if needed", [{"type": "backpack", "available": True}]),
            loot_option("rope", "Take Rope (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Rope (2 spaces)"}]),
        ]
    },
    "54": section_roll(
        "Glass stem handling check.",
        [
            roll_range(0, 4, 250, "Glass stem breaks"),
            roll_range(5, 12, 268, "Glass stem intact"),
        ],
        [
            {
                "label": "Mind Over Matter or Mindblast",
                "value": 3,
                "condition": cond_any(cond_power("Mind Over Matter"), cond_power("Mindblast")),
            }
        ],
    ),
    "59": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}])
        ]
    },
    "73": section_roll(
        "Frozen bridge crack check.",
        [
            roll_range(0, 7, 119, "Bridge gives way"),
            roll_range(8, 9, 136, "Reach the far side"),
        ],
    ),
    "74": section_roll(
        "Hide from the Ice Barbarian.",
        [
            roll_range(0, 4, 48, "Discovered"),
            roll_range(5, 9, 287, "Remain hidden"),
        ],
    ),
    "80": section_roll(
        "Dodge the charging Kalkoth.",
        [
            roll_range(0, 1, 123, "Dive fails"),
            roll_range(2, 9, 59, "Dive clear"),
        ],
    ),
    "84": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}])
        ]
    },
    "86": section_roll(
        "Pick the lock with a weapon.",
        [
            roll_range(0, 7, 47, "Lock resists"),
            roll_range(8, 12, 194, "Lock opens"),
        ],
        [{"label": "Weaponskill with active weapon", "value": 3, "condition": cond_active_weaponskill()}],
    ),
    "88": section_roll(
        "Javek venom check after END loss.",
        [
            roll_range(0, 8, None, "Bite stopped by padded arm"),
            roll_values([9], None, "Javek venom kills Lone Wolf", ending="death", cause="Section 88 Javek venom death."),
        ],
    ),
    "91": {
        "loot": [
            loot_option("baknar-oil", "Take Baknar Oil", [{"type": "add_item", "container": "backpack", "name": "Baknar Oil"}])
        ]
    },
    "94": section_roll(
        "Escape the icy water.",
        [
            roll_range(0, 6, 176, "Drag yourself free", [end_delta(-3)]),
            roll_range(7, 9, None, "Drown in the icy water", ending="death", cause="Section 94 icy-water drowning."),
        ],
    ),
    "96": section_roll(
        "Avoid Kalkoth detection.",
        [
            roll_range(0, 8, 59, "Kalkoth pass by"),
            roll_range(9, 11, 214, "Kalkoth detect you"),
        ],
        [{"label": "Baknar Oil applied", "value": 2, "condition": cond_flag("baknarOilApplied")}],
    ),
    "102": {
        "loot": [
            loot_option("effigy", "Take Effigy", [{"type": "add_item", "container": "special", "name": "Effigy"}])
        ]
    },
    "119": {
        "loot": [
            loot_option("food-1", "Take Food for 1 Meal", add_items("backpack", "Meal", 1)),
            loot_option("food-2", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
            loot_option("food-3", "Take Food for 3 Meals", add_items("backpack", "Meal", 3)),
            loot_option("food-4", "Take Food for 4 Meals", add_items("backpack", "Meal", 4)),
            loot_option("food-5", "Take Food for 5 Meals", add_items("backpack", "Meal", 5)),
            loot_option("sleeping-furs", "Take Sleeping Furs", [{"type": "add_item", "container": "backpack", "name": "Sleeping Furs (2 spaces)"}]),
            loot_option("tent", "Take Tent", [{"type": "add_item", "container": "backpack", "name": "Tent (3 spaces)"}]),
            loot_option("rope", "Take Rope", [{"type": "add_item", "container": "backpack", "name": "Rope (2 spaces)"}]),
        ]
    },
    "134": section_roll(
        "Syem Island night-weather roll.",
        [
            roll_range(0, 3, 57, "First hazard route"),
            roll_range(4, 6, 188, "Middle route"),
            roll_range(7, 9, 331, "Frostbite route"),
        ],
    ),
    "139": {
        "routeChecks": [
            {
                "id": "139-red-laumspur",
                "label": "Red Laumspur check",
                "summary": "Checks whether Lone Wolf has Red Laumspur.",
                "outcomes": [
                    {
                        "label": "Red Laumspur available",
                        "route": 116,
                        "testLabel": "Has Red Laumspur",
                        "conditions": [{"type": "item", "name": "Red", "containers": ["backpack"], "match": "contains"}],
                    },
                    {
                        "label": "No Red Laumspur",
                        "route": 239,
                        "testLabel": "No Red Laumspur",
                        "conditions": [{"type": "no_item", "name": "Red", "containers": ["backpack"], "match": "contains"}],
                    },
                ],
            }
        ]
    },
    "142": section_roll(
        "Collapse the mineral rock.",
        [
            roll_range(0, 5, 284, "Rock seals the cave"),
            roll_range(6, 9, 32, "Kalkoth fight"),
        ],
    ),
    "146": section_roll(
        "Rear-sledge rope escape roll.",
        [
            roll_values([0], 312, "Dragged into the crevasse"),
            roll_range(1, 4, 226, "Free your foot"),
            roll_range(5, 9, 266, "Leap clear"),
        ],
    ),
    "149": section_roll(
        "Avoid the Ice Barbarian scout's blow.",
        [
            roll_range(0, 4, 286, "Scout's blow lands"),
            roll_range(5, 11, 333, "Avoid the blow"),
        ],
        [
            {
                "label": "Tracking, Hunting, or Sixth Sense",
                "value": 2,
                "condition": cond_any(cond_power("Tracking"), cond_power("Hunting"), cond_power("Sixth Sense")),
            }
        ],
    ),
    "152": {
        "goldDistraction": {
            "id": "book3-section152-gold-distraction",
            "label": "Distract the guard with Gold Crowns",
            "summary": "Choose how many Gold Crowns to throw, then roll 0-9. A 0 counts as 10; if the roll total is equal to or less than the thrown Gold Crowns, the guard is distracted.",
            "successRoute": 319,
            "failureRoute": 181,
            "zeroAsTen": True,
        }
    },
    "155": section_roll(
        "Ice staircase descent.",
        [
            roll_range(-2, 2, 248, "Fall on the ice staircase"),
            roll_range(3, 10, 191, "Descend safely"),
        ],
        [
            {"label": "END below 10", "value": -2, "condition": cond_end_lt(10)},
            {"label": "END above 20", "value": 1, "condition": cond_end_gte(21)},
        ],
    ),
    "156": {
        "loot": [
            loot_option("gallowbrush", "Take Potion of Gallowbrush", [{"type": "add_item", "container": "backpack", "name": "Potion of Gallowbrush"}])
        ]
    },
    "167": section_roll(
        "Natural ice bowl night roll.",
        [
            roll_range(0, 6, 85, "Cold night route"),
            roll_range(7, 9, 300, "Alternative night route"),
        ],
    ),
    "179": section_roll(
        "Herb smoke infiltration roll.",
        [
            roll_range(0, 4, 39, "Smoke plan falters"),
            roll_range(5, 9, 296, "Smoke plan works"),
        ],
    ),
    "183": section_roll(
        "Sprint with twisted ankle.",
        [
            roll_range(0, 3, 89, "Too slow"),
            roll_range(4, 11, 215, "Reach the corridor"),
        ],
        [{"label": "Hunting", "value": 2, "condition": cond_power("Hunting")}],
    ),
    "185": section_roll(
        "Visualize the lock mechanism.",
        [
            roll_range(0, 4, 22, "Lock resists"),
            roll_range(5, 11, 326, "Lock opens"),
        ],
        [{"label": "Sixth Sense", "value": 2, "condition": cond_power("Sixth Sense")}],
    ),
    "177": {
        "loot": [
            loot_option("black-graveweed", "Take Potion of Black Graveweed", [{"type": "add_item", "container": "backpack", "name": "Potion of Black Graveweed"}])
        ]
    },
    "194": {
        "loot": [
            loot_option("silver-helm", "Take Silver Helm", [{"type": "add_item", "container": "special", "name": "Silver Helm"}])
        ]
    },
    "211": section_roll(
        "Cyclone escape roll.",
        [
            roll_range(-3, 3, 95, "Cyclone catches you"),
            roll_range(4, 9, 196, "Escape the vortex"),
        ],
        [{"label": "END below 10", "value": -3, "condition": cond_end_lt(10)}],
    ),
    "210": {
        "loot": [
            loot_option("bone-sword", "Take Bone Sword", [{"type": "add_item", "container": "special", "name": "Bone Sword"}]),
            loot_option("gold-bracelet", "Take Gold Bracelet", [{"type": "add_item", "container": "special", "name": "Gold Bracelet"}]),
        ]
    },
    "218": {
        "loot": [
            loot_option("diamond", "Take Diamond", [{"type": "add_item", "container": "special", "name": "Diamond"}])
        ]
    },
    "223": {
        "loot": [
            loot_option("food-1", "Take Food for 1 Meal", add_items("backpack", "Meal", 1)),
            loot_option("food-2", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
            loot_option("food-3", "Take Food for 3 Meals", add_items("backpack", "Meal", 3)),
            loot_option("food-4", "Take Food for 4 Meals", add_items("backpack", "Meal", 4)),
            loot_option("food-5", "Take Food for 5 Meals", add_items("backpack", "Meal", 5)),
            loot_option("tent", "Take Tent", [{"type": "add_item", "container": "backpack", "name": "Tent (3 spaces)"}]),
            loot_option("sleeping-furs", "Take Sleeping Furs", [{"type": "add_item", "container": "backpack", "name": "Sleeping Furs (2 spaces)"}]),
            loot_option("long-rope", "Take Long Rope", [{"type": "add_item", "container": "backpack", "name": "Long Rope (2 spaces)"}]),
        ]
    },
    "232": section_roll(
        "Glacier-wall camp night roll.",
        [
            roll_range(0, 6, 85, "Cold night route"),
            roll_range(7, 9, 300, "Alternative night route"),
        ],
    ),
    "231": {
        "loot": [
            loot_option("gold-bracelet", "Take Gold Bracelet", [{"type": "add_item", "container": "special", "name": "Gold Bracelet"}])
        ]
    },
    "233": {
        "loot": [
            loot_option("distilled-laumspur", "Take Distilled Laumspur", [{"type": "add_item", "container": "backpack", "name": "Potion of Laumspur (+5 END)"}])
        ]
    },
    "258": section_roll(
        "Break Mindshield and discard the Gold Bracelet. 0 counts as 10; lose END equal to the final total before turning to 63.",
        [roll_range(-2, 10, 63, "Bracelet discarded", [end_loss_from_roll_total()])],
        [
            {
                "label": "Hunting or Sixth Sense",
                "value": -2,
                "condition": cond_any(cond_power("Hunting"), cond_power("Sixth Sense")),
            }
        ],
        zero_as_ten=True,
    ),
    "262": section_roll(
        "Hold onto the child.",
        [
            roll_range(0, 6, 320, "Keep hold"),
            roll_range(7, 9, 140, "Lose hold"),
        ],
    ),
    "272": section_roll(
        "Dodge Vonotar's frost blast without the Sommerswerd.",
        [
            roll_range(0, 3, 143, "Frost blast hits"),
            roll_range(4, 9, 58, "Dodge the blast"),
        ],
    ),
    "280": {
        "loot": [
            loot_option("ornate-silver-key", "Take Ornate Silver Key", [{"type": "add_item", "container": "special", "name": "Ornate Silver Key"}])
        ]
    },
    "282": {
        "loot": [
            loot_option("spear", "Take Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("blue-stone-disc", "Take Blue Stone Disc", [{"type": "add_item", "container": "special", "name": "Blue Stone Disc"}]),
        ]
    },
    "283": section_roll(
        "Escape through the closing door.",
        [
            roll_range(0, 4, 53, "Door catches you"),
            roll_range(5, 7, 16, "Squeeze through"),
            roll_range(8, 12, 113, "Clean escape"),
        ],
        [{"label": "Hunting", "value": 3, "condition": cond_power("Hunting")}],
    ),
    "284": section_roll(
        "Cross the ice-floes.",
        [
            roll_range(-2, 3, 94, "Fall into icy water"),
            roll_range(4, 11, 176, "Cross safely"),
        ],
        [
            {"label": "Hunting", "value": 2, "condition": cond_power("Hunting")},
            {"label": "END below 8", "value": -2, "condition": cond_end_lt(8)},
        ],
    ),
    "291": section_roll(
        "Random next-day hazard at The Rock.",
        [
            roll_range(0, 4, 103, "Baknar shelter route"),
            roll_range(5, 9, 220, "Crevasse route"),
        ],
    ),
    "295": {
        "loot": [
            loot_option("firesphere", "Take Firesphere", [{"type": "add_item", "container": "special", "name": "Firesphere"}])
        ]
    },
    "298": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}])
        ]
    },
    "302": section_roll(
        "Crevasse-floor stumble check.",
        [
            roll_range(0, 1, 37, "Bad fall"),
            roll_range(2, 7, 193, "Slow progress"),
            roll_range(8, 11, 243, "Find the way"),
        ],
        [{"label": "Sixth Sense", "value": 2, "condition": cond_power("Sixth Sense")}],
    ),
    "303": {
        "sourceRoutes": [
            {"Section": 127},
            {"Section": 308},
            {"Section": 323},
        ]
    },
    "308": {
        "loot": [
            loot_option("silver-helm", "Take Silver Helm", [{"type": "add_item", "container": "special", "name": "Silver Helm"}])
        ]
    },
    "309": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}]),
            loot_option("firesphere", "Take Firesphere", [{"type": "add_item", "container": "special", "name": "Firesphere"}]),
        ]
    },
    "311": {
        "loot": [
            loot_option("distilled-alether", "Take Distilled Alether", [{"type": "add_item", "container": "backpack", "name": "Potion of Alether (+4 CS)"}])
        ]
    },
    "316": {
        "loot": [
            loot_option("gold-bracelet", "Take Gold Bracelet", [{"type": "add_item", "container": "special", "name": "Gold Bracelet"}])
        ]
    },
    "321": {
        "loot": [
            loot_option("blue-stone-triangle", "Take Blue Stone Triangle", [{"type": "add_item", "container": "special", "name": "Blue Stone Triangle"}])
        ]
    },
    "322": section_roll(
        "Run across the lake ice.",
        [
            roll_range(0, 2, 153, "Ice gives way"),
            roll_range(3, 9, 59, "Reach safety"),
        ],
    ),
    "323": section_roll(
        "Stone-step landing check.",
        [
            roll_range(0, 4, 76, "Lose footing"),
            roll_range(5, 12, 2, "Keep climbing"),
        ],
        [
            {
                "label": "Sixth Sense, Tracking, or Hunting",
                "value": 3,
                "condition": cond_any(cond_power("Sixth Sense"), cond_power("Tracking"), cond_power("Hunting")),
            }
        ],
    ),
    "327": section_roll(
        "Hidden crevasse fall.",
        [
            roll_range(0, 8, 105, "Survive the fall"),
            roll_values([9], 144, "Fatal fall"),
        ],
    ),
    "331": section_roll(
        "Frostbite camp roll.",
        [
            roll_range(0, 4, 62, "Worse route"),
            roll_range(5, 9, 288, "Better route"),
        ],
    ),
    "334": {
        "loot": [
            loot_option("glowing-crystal", "Take Glowing Crystal", [{"type": "add_item", "container": "special", "name": "Glowing Crystal"}])
        ]
    },
    "346": section_roll(
        "Crevasse jump.",
        [
            roll_range(0, 3, 195, "Jump fails"),
            roll_range(4, 11, 232, "Jump succeeds"),
        ],
        [{"label": "Hunting", "value": 2, "condition": cond_power("Hunting")}],
    ),
}


MANUAL_COMBAT_AUDIT: dict[str, dict[str, Any]] = {
    "14": {"combat": [combat_preset(14, "Ice Barbarian", combat_enemy("Ice Barbarian", 15, 14), victoryRoute=309)]},
    "32": {
        "combat": [
            combat_preset(
                32,
                "Kalkoth",
                [
                    combat_enemy("Kalkoth 1", 11, 35),
                    combat_enemy("Kalkoth 2", 10, 32),
                    combat_enemy("Kalkoth 3", 8, 30),
                ],
                victoryRoute=25,
                playerLossRoute=66,
            )
        ]
    },
    "68": {"combat": [combat_preset(68, "Ice Barbarian", combat_enemy("Ice Barbarian", 18, 28), victoryRoute=186)]},
    "78": {"combat": [combat_preset(78, "Baknar", combat_enemy("Baknar", 19, 30), victoryRoute=245)]},
    "83": {
        "combat": [
            combat_preset(
                83,
                "Ice Barbarian Mutants",
                combat_enemy("Ice Barbarian Mutants", 18, 24),
                enemyImmune=True,
                victoryRoute=313,
            )
        ]
    },
    "88": {
        "combat": [
            combat_preset(
                88,
                "Javek",
                combat_enemy("Javek", 15, 15),
                enemyImmune=True,
                playerLossRandomCheck={
                    "summary": "Javek venom check after a bite.",
                    "deathValues": [9],
                    "safeLabel": "Bite stopped by padded arm",
                    "deathCause": "Section 88 Javek venom death.",
                },
                victoryRoute=269,
            )
        ]
    },
    "89": {
        "combat": [
            combat_preset(
                89,
                "Doomwolves",
                [
                    combat_enemy("Doomwolf 1", 15, 24),
                    combat_enemy("Doomwolf 2", 14, 23),
                    combat_enemy("Doomwolf 3", 14, 20),
                ],
                victoryRoute=161,
            )
        ]
    },
    "99": {
        "combat": [
            combat_preset(
                99,
                "Helghast",
                combat_enemy("Helghast", 22, 30),
                enemyImmune=True,
                doubleEnemyLossWithSommerswerd=True,
                perRoundActions=[{"type": "stat", "stat": "end", "delta": -2, "condition": {"type": "no_power", "name": "Mindshield"}}],
                victoryRoute=230,
            )
        ]
    },
    "103": {"combat": [combat_preset(103, "Baknar", combat_enemy("Baknar", 19, 30), victoryRoute=305)]},
    "106": {
        "combat": [
            combat_preset(
                106,
                "Ice Barbarians",
                combat_enemy("Ice Barbarians", 19, 36),
                enemyImmune=True,
                canEvade=True,
                evadeRoute=145,
                victoryRoute=338,
            )
        ]
    },
    "108": {
        "combat": [
            combat_preset(
                108,
                "Ice Barbarian",
                combat_enemy("Ice Barbarian", 16, 24),
                canEvade=True,
                evadeAfterRounds=1,
                victoryRoute=282,
            )
        ]
    },
    "123": {"combat": [combat_preset(123, "Kalkoth", combat_enemy("Kalkoth", 11, 30), victoryRoute=174, playerLossRoute=66)]},
    "137": {
        "combat": [
            combat_preset(
                137,
                "Ice Barbarian and Doomwolf",
                combat_enemy("Ice Barbarian + Doomwolf", 30, 30),
                conditionalModifiers=[{"condition": {"type": "power", "name": "Mindblast"}, "modifier": -1, "label": "Partial Mindblast immunity"}],
                victoryRoute=28,
            )
        ]
    },
    "138": {
        "combat": [
            combat_preset(
                138,
                "Kalkoth",
                [combat_enemy("Kalkoth 1", 11, 35), combat_enemy("Kalkoth 2", 10, 32)],
                canEvade=True,
                evadeRoute=277,
                victoryRoute=25,
                playerLossRoute=66,
            )
        ]
    },
    "147": {"combat": [combat_preset(147, "Kalkoth", combat_enemy("Kalkoth", 10, 28), victoryRoute=84, playerLossRoute=66)]},
    "158": {
        "combat": [
            combat_preset(
                158,
                "Ice Barbarian Scout",
                combat_enemy("Ice Barbarian Scout", 20, 28),
                oneRoundComparisonRoutes={"playerLossGreater": 165, "enemyLossGreater": 271, "equal": 337},
            )
        ]
    },
    "161": {
        "combat": [
            combat_preset(
                161,
                "Ice Barbarian",
                combat_enemy("Ice Barbarian", 17, 29),
                enemyImmune=True,
                victoryRoute=210,
            )
        ]
    },
    "164": {
        "combat": [
            combat_preset(
                164,
                "Akraa'Neonor",
                combat_enemy("Akraa'Neonor", 23, 50),
                doubleEnemyLossWithSommerswerd=True,
                winWithinRounds=5,
                winWithinRoute=272,
                tooLateRoute=324,
            )
        ]
    },
    "180": {
        "combat": [
            combat_preset(
                180,
                "Kalkoth",
                combat_enemy("Kalkoth", 11, 35),
                victoryRoute=70,
                playerLossRoute=129,
                perRoundActions=[{"type": "combat_enemy_damage", "delta": -3, "label": "Fenor's attack"}],
            )
        ]
    },
    "200": {
        "combat": [
            combat_preset(
                200,
                "Akraa'Neonor",
                combat_enemy("Akraa'Neonor", 22, 50),
                doubleEnemyLossWithSommerswerd=True,
                winWithinRounds=7,
                winWithinRoute=272,
                tooLateRoute=324,
            )
        ]
    },
    "208": {
        "combat": [
            combat_preset(
                208,
                "Ice Barbarian",
                combat_enemy("Ice Barbarian", 17, 30),
                winWithinRounds=4,
                winWithinRoute=4,
                tooLateRoute=81,
            )
        ]
    },
    "241": {
        "combat": [
            combat_preset(
                241,
                "Ice Barbarian",
                combat_enemy("Ice Barbarian", 18, 28),
                ignorePlayerLossRounds=2,
                victoryRoute=186,
            )
        ]
    },
    "259": {"combat": [combat_preset(259, "Kalkoth", combat_enemy("Kalkoth", 11, 35), victoryRoute=151, playerLossRoute=129)]},
    "260": {
        "combat": [
            combat_preset(
                260,
                "Ice Barbarian",
                combat_enemy("Ice Barbarian", 17, 29),
                enemyImmune=True,
                ignorePlayerLossRounds=2,
                victoryRoute=210,
            )
        ]
    },
    "263": {
        "combat": [
            combat_preset(
                263,
                "Kalkoth",
                [
                    combat_enemy("Kalkoth 1", 11, 35),
                    combat_enemy("Kalkoth 2", 10, 32),
                    combat_enemy("Kalkoth 3", 8, 30),
                ],
                canEvade=True,
                evadeRoute=277,
                victoryRoute=25,
                playerLossRoute=66,
            )
        ]
    },
    "265": {"combat": [combat_preset(265, "Crystal Frostwyrm", combat_enemy("Crystal Frostwyrm", 15, 30), enemyImmune=True, victoryRoute=3)]},
    "270": {"combat": [combat_preset(270, "Ice Barbarian", combat_enemy("Ice Barbarian", 14, 25), victoryRoute=340)]},
    "296": {
        "combat": [
            combat_preset(
                296,
                "Ice Barbarians",
                combat_enemy("Ice Barbarians", 17, 30),
                roundLimit=3,
                survivalRoute=173,
                victoryRoute=173,
            )
        ]
    },
    "304": {
        "combat": [
            combat_preset(
                304,
                "Helghast",
                combat_enemy("Helghast", 22, 30),
                enemyImmune=True,
                doubleEnemyLossWithSommerswerd=True,
                perRoundActions=[{"type": "stat", "stat": "end", "delta": -2, "condition": {"type": "no_power", "name": "Mindshield"}}],
                victoryRoute=20,
            )
        ]
    },
    "343": {
        "combat": [
            combat_preset(
                343,
                "Cell Guards",
                [
                    combat_enemy("Doomwolf 1", 15, 24),
                    combat_enemy("Doomwolf 2", 14, 23),
                    combat_enemy("Doomwolf 3", 14, 20),
                    combat_enemy("Ice Barbarian", 17, 29),
                ],
                victoryRoute=28,
            )
        ]
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
    classes: list[str] = []

    if len(routes) > 1:
        add_class(classes, "route_choice")
    elif len(routes) == 1:
        add_class(classes, "single_route")
    if "random number table" in text or "pick a number" in text:
        add_class(classes, "random")
    if "kai discipline" in text or "if you have the kai" in text:
        add_class(classes, "kai_discipline_check")
    if any(term in text for term in ("combat skill", "endurance")) and any(
        term in text for term in ("fight", "combat", "enemy", "creature")
    ):
        add_class(classes, "combat")
    if "meal" in text or "food" in text or "hunting" in text:
        add_class(classes, "meal")
    if "gold crown" in text or "gold crowns" in text or "crowns" in text:
        add_class(classes, "gold")
    if any(
        term in text
        for term in (
            "backpack",
            "special item",
            "weapon",
            "action chart",
            "erase",
            "discard",
            "pick up",
            "record",
            "mark",
        )
    ):
        add_class(classes, "inventory")
    if "endurance" in text and any(term in text for term in ("lose", "deduct", "reduce")):
        add_class(classes, "endurance_loss")
    if "endurance" in text and any(term in text for term in ("restore", "regain", "heal")):
        add_class(classes, "endurance_gain")
    if "combat skill" in text and any(term in text for term in ("add", "deduct", "reduce", "increase")):
        add_class(classes, "combat_skill_modifier")
    if any(term in text for term in ("mission has failed", "failed your mission", "impossible to complete your mission")):
        add_class(classes, "terminal_failure")
    if any(
        term in text
        for term in (
            "you are dead",
            "your adventure ends",
            "your life and your mission end",
            "your mission and your life end",
            "your life and your quest come",
            "you slowly bleed to death",
            "you fall to your death",
            "stab you to death",
            "swallows you whole",
            "kill yourself",
            "plummet to your death",
        )
    ):
        add_class(classes, "terminal_death")
    if section == MAX_SECTION:
        add_class(classes, "terminal_success")
    if not routes and not any(value.startswith("terminal_") for value in classes):
        add_class(classes, "terminal_unclassified")
    if not classes:
        add_class(classes, "story")
    return classes


def fetch_svg_graph() -> dict[str, Any]:
    result: dict[str, Any] = {
        "url": SVG_GRAPH_URL,
        "status": None,
        "available": False,
        "nodeCount": 0,
        "edgeCount": 0,
        "edges": [],
        "error": "",
    }
    try:
        request = urllib.request.Request(SVG_GRAPH_URL, headers={"Accept-Encoding": "identity"})
        with urllib.request.urlopen(request, timeout=20) as response:
            result["status"] = getattr(response, "status", None)
            raw = response.read()
        if raw[:2] == b"\x1f\x8b":
            raw = gzip.decompress(raw)
        text = raw.decode("utf-8", errors="ignore")
        titles = [html.unescape(item).strip() for item in re.findall(r"<title>(.*?)</title>", text, re.I | re.S)]
        nodes: set[int] = set()
        edges: set[tuple[int, int]] = set()
        for title in titles:
            if "->" in title:
                source, target = title.split("->", 1)
                if source.isdigit() and target.isdigit():
                    edges.add((int(source), int(target)))
            elif title.isdigit():
                nodes.add(int(title))
        result.update(
            {
                "available": True,
                "nodeCount": len(nodes),
                "edgeCount": len(edges),
                "edges": sorted([list(edge) for edge in edges]),
            }
        )
    except Exception as exc:  # pragma: no cover - network check can fail offline
        result["error"] = str(exc)
    return result


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

    for manual_audit in (MANUAL_FLOW_AUDIT, MANUAL_COMBAT_AUDIT):
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
        section for section, entry in sections.items() if int(entry["sourceRouteCount"]) == 0
    ]
    branch_sections = [
        section for section, entry in sections.items() if int(entry["sourceRouteCount"]) >= 2
    ]
    classified_counts: dict[str, int] = {}
    for entry in sections.values():
        for value in entry["classification"]:
            classified_counts[value] = classified_counts.get(value, 0) + 1

    local_edges = sorted(
        [section, int(route["Section"])]
        for section, entry in sections.items()
        for route in entry["sourceRoutes"]
    )
    svg_graph = fetch_svg_graph()
    svg_edges = {tuple(edge) for edge in svg_graph.get("edges", [])}
    local_edge_set = {tuple(edge) for edge in local_edges}
    graph_check = {
        **svg_graph,
        "localNodeCount": len(sections),
        "localEdgeCount": len(local_edges),
        "svgEdgesNotLocal": sorted([list(edge) for edge in svg_edges - local_edge_set]),
        "localEdgesNotSvg": sorted([list(edge) for edge in local_edge_set - svg_edges]),
    }

    meta = {
        "schemaVersion": 1,
        "bookNumber": BOOK_NUMBER,
        "title": BOOK_TITLE,
        "source": f"books/lw/{BOOK_CODE}/sect*.htm",
        "generatedBy": "testing/lwbook3_section_flow_audit.py",
        "sectionCount": len(sections),
        "expectedSectionCount": MAX_SECTION,
        "sourceRouteLinkCount": sum(int(entry["sourceRouteCount"]) for entry in sections.values()),
        "branchSectionCount": len(branch_sections),
        "terminalSectionCount": len(terminal_sections),
        "reachableFromSection1Count": len(reachable),
        "invalidSectionLinkCount": len(invalid_links),
        "missingSectionCount": len(missing_sections),
        "svgRouteGraphAvailable": bool(svg_graph.get("available")),
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
        "section1Routes": [route["Section"] for route in sections.get(1, {}).get("sourceRoutes", [])],
        "section350Classes": sections.get(350, {}).get("classification", []),
        "routeGraphCheck": graph_check,
        "manualFlowAuditCount": len(MANUAL_FLOW_AUDIT),
        "manualLootAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "loot" in entry),
        "manualCombatAuditCount": len(MANUAL_COMBAT_AUDIT),
        "manualRouteCheckAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "routeChecks" in entry),
    }
    return data, artifact


def render_report(artifact: dict[str, Any]) -> str:
    meta = artifact["meta"]
    counts = artifact["classificationCounts"]
    lines = [
        "# LW Book 3 Section Flow Baseline",
        "",
        "Scope: source-link graph for local Project Aon Book 3 section files.",
        "",
        "This report records section numbers, graph counts, and audit classifications only. Do not copy Book 3 prose into committed audit artifacts.",
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
        f"- Project Aon SVG route graph available: {'yes' if meta['svgRouteGraphAvailable'] else 'no'}",
        f"- Confirmed optional loot/helper sections: {artifact['manualLootAuditCount']}",
        f"- Confirmed combat preset sections: {artifact['manualCombatAuditCount']}",
        f"- Confirmed route-check sections: {artifact['manualRouteCheckAuditCount']}",
        "",
        "## Baseline Checks",
        "",
        f"- Section 1 routes: {', '.join(str(item) for item in artifact['section1Routes'])}",
        f"- Section 350 classifications: {', '.join(artifact['section350Classes'])}",
        f"- Missing sections: {', '.join(str(item) for item in artifact['missingSections']) if artifact['missingSections'] else 'none'}",
        f"- Invalid links: {json.dumps(artifact['invalidLinks']) if artifact['invalidLinks'] else 'none'}",
        f"- Unreachable sections from section 1: {', '.join(str(item) for item in artifact['unreachableFromSection1']) if artifact['unreachableFromSection1'] else 'none'}",
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
            "- `data/book3-section-flows.json` contains one source-link baseline entry for every discovered section.",
            "- `sourceRoutes` is the compact legal-link baseline used for later helper implementation.",
            "- `classification` is heuristic and remains useful for review slices.",
            "",
            "## Remaining Risk",
            "",
            "- This pass is source-link and heuristic classification only.",
            "- Some combat presets and loot helpers are now recorded; random helpers, full route checks, achievements, and lifecycle support are covered by later implementation/testing passes.",
            "- Combat/loot helper coverage is partial and should grow during Book 3 playtesting.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_graph_report(graph: dict[str, Any]) -> str:
    available = bool(graph.get("available"))
    svg_not_local = graph.get("svgEdgesNotLocal", [])
    local_not_svg = graph.get("localEdgesNotSvg", [])
    lines = [
        "# LW Book 3 Route Graph Check",
        "",
        "Scope: optional Project Aon SVG/SVGZ route graph cross-check.",
        "",
        "The local Project Aon HTML files remain the source of truth. The online SVG graph is used only as an external consistency check.",
        "",
        "## Summary",
        "",
        f"- URL: `{graph.get('url')}`",
        f"- HTTP status: {graph.get('status') or 'unavailable'}",
        f"- Available: {'yes' if available else 'no'}",
        f"- Local section nodes: {graph.get('localNodeCount')}",
        f"- Local source edges: {graph.get('localEdgeCount')}",
        f"- SVG section nodes: {graph.get('nodeCount')}",
        f"- SVG edges: {graph.get('edgeCount')}",
        f"- SVG edges missing locally: {len(svg_not_local)}",
        f"- Local edges missing in SVG: {len(local_not_svg)}",
        "",
        "## Differences",
        "",
        f"- SVG edges not local: {json.dumps(svg_not_local[:25]) if svg_not_local else 'none'}",
        f"- Local edges not SVG: {json.dumps(local_not_svg[:25]) if local_not_svg else 'none'}",
    ]
    if graph.get("error"):
        lines.extend(["", "## Error", "", str(graph["error"])])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and report artifacts")
    parser.add_argument("--check", action="store_true", help="check existing artifacts")
    args = parser.parse_args()

    data, artifact = build_graph()
    data_text = json.dumps(data, indent=2) + "\n"
    report_text = render_report(artifact)
    graph_text = render_graph_report(artifact["routeGraphCheck"])

    if args.write:
        DATA_PATH.write_text(data_text, encoding="utf-8")
        REPORT_PATH.write_text(report_text, encoding="utf-8")
        GRAPH_REPORT_PATH.write_text(graph_text, encoding="utf-8")
        print(f"Wrote {DATA_PATH}")
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {GRAPH_REPORT_PATH}")
        return 0

    if args.check:
        failures: list[str] = []
        for path, expected in (
            (DATA_PATH, data_text),
            (REPORT_PATH, report_text),
            (GRAPH_REPORT_PATH, graph_text),
        ):
            if not path.exists():
                failures.append(f"Missing {path}")
            elif path.read_text(encoding="utf-8") != expected:
                failures.append(f"Out of date: {path}")
        if failures:
            for failure in failures:
                print(failure)
            return 1
        print("Book 3 section-flow baseline check passed.")
        return 0

    print(report_text)
    print(graph_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

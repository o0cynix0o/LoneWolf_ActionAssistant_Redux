#!/usr/bin/env python3
"""Build and verify the Book 1 section-flow baseline from local HTML."""

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
BOOK_DIR = ROOT / "books" / "lw" / "01fftd"
DATA_PATH = ROOT / "data" / "book1-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK1_SECTION_FLOW_BASELINE.md"
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


def roll_range(minimum: int, maximum: int, route: int, label: str) -> dict[str, Any]:
    return {"test": "range", "min": minimum, "max": maximum, "route": route, "label": label}


def section_roll(summary: str, outcomes: list[dict[str, Any]]) -> dict[str, Any]:
    return {"roll": {"summary": summary, "outcomes": outcomes}}


def condition_outcome(
    label: str,
    route: int,
    condition: dict[str, Any],
    test_label: str,
) -> dict[str, Any]:
    return {"label": label, "route": route, "conditions": [condition], "testLabel": test_label}


def power_route_check(
    section: int,
    power: str,
    power_route: int,
    no_power_route: int,
    *,
    label: str | None = None,
    optional: bool = False,
    requires_automation: bool = False,
) -> dict[str, Any]:
    no_power_label = f"No {power}" if not optional else f"No {power} or decline"
    return {
        "routeChecks": [
            {
                "id": f"{section}-{power.lower().replace(' ', '-')}",
                "label": label or f"{power} route",
                "summary": f"Checks whether Lone Wolf has {power}.",
                "requiresAutomationApplied": requires_automation,
                "outcomes": [
                    condition_outcome(
                        f"{power} available",
                        power_route,
                        {"type": "power", "name": power},
                        f"Has {power}",
                    ),
                    condition_outcome(
                        no_power_label,
                        no_power_route,
                        {"type": "no_power", "name": power},
                        f"No {power}",
                    ),
                ],
            }
        ]
    }


def item_route_check(
    section: int,
    item: str,
    item_route: int,
    no_item_route: int,
    *,
    label: str | None = None,
    container: str = "backpack",
) -> dict[str, Any]:
    return {
        "routeChecks": [
            {
                "id": f"{section}-{item.lower().replace(' ', '-')}",
                "label": label or f"{item} route",
                "summary": f"Checks whether Lone Wolf has {item}.",
                "outcomes": [
                    condition_outcome(
                        f"{item} available",
                        item_route,
                        {"type": "item", "name": item, "containers": [container], "match": "exact"},
                        f"Has {item}",
                    ),
                    condition_outcome(
                        f"No {item}",
                        no_item_route,
                        {"type": "no_item", "name": item, "containers": [container], "match": "exact"},
                        f"No {item}",
                    ),
                ],
            }
        ]
    }


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
    return {
        "routeChecks": [
            {
                "id": f"{section}-{stat}-gte-{threshold}",
                "label": label,
                "summary": f"Checks current {stat_label}.",
                "requiresAutomationApplied": requires_automation,
                "formula": {"label": stat_label, "terms": [{"stat": stat}]},
                "outcomes": [
                    {"label": f"{stat_label} {threshold} or more", "test": "gte", "value": threshold, "route": gte_route},
                    {"label": f"{stat_label} less than {threshold}", "test": "lt", "value": threshold, "route": lt_route},
                ],
            }
        ]
    }


MANUAL_FLOW_AUDIT: dict[str, dict[str, Any]] = {
    "20": {
        "loot": [
            {
                "id": "20-supplies",
                "label": "Take Backpack, 2 Meals, and Dagger",
                "actions": [
                    {"type": "backpack", "available": True},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "weapon", "name": "Dagger"},
                ],
            }
        ]
    },
    "62": {
        "loot": [
            {
                "id": "62-gold-meals",
                "label": "Take 28 Gold Crowns and 3 Meals",
                "actions": [
                    {"type": "stat", "stat": "gold", "delta": 28},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                ],
            },
            {"id": "62-sword", "label": "Take Sword", "actions": [{"type": "add_item", "container": "weapon", "name": "Sword"}]},
        ]
    },
    "113": {
        "loot": [
            {
                "id": "113-laumspur",
                "label": "Take 2 Laumspur Meals",
                "actions": [
                    {"type": "add_item", "container": "backpack", "name": "Laumspur"},
                    {"type": "add_item", "container": "backpack", "name": "Laumspur"},
                ],
            }
        ]
    },
    "124": {
        "loot": [
            {
                "id": "124-box",
                "label": "Take 15 Gold Crowns and Silver Key",
                "actions": [
                    {"type": "stat", "stat": "gold", "delta": 15},
                    {"type": "add_item", "container": "special", "name": "Silver Key"},
                ],
            }
        ]
    },
    "148": {"loot": [{"id": "148-warhammer", "label": "Take Warhammer", "actions": [{"type": "add_item", "container": "weapon", "name": "Warhammer"}]}]},
    "164": {"loot": [{"id": "164-alether", "label": "Take Potion of Alether", "actions": [{"type": "add_item", "container": "backpack", "name": "Potion of Alether"}]}]},
    "184": {
        "loot": [
            {
                "id": "184-supplies",
                "label": "Take 40 Gold Crowns, Sword, and 4 Meals",
                "actions": [
                    {"type": "stat", "stat": "gold", "delta": 40},
                    {"type": "add_item", "container": "weapon", "name": "Sword"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                    {"type": "add_item", "container": "backpack", "name": "Meal"},
                ],
            }
        ]
    },
    "197": {
        "loot": [
            {
                "id": "197-drakkar",
                "label": "Take Short Sword and 6 Gold Crowns",
                "actions": [
                    {"type": "add_item", "container": "weapon", "name": "Short Sword"},
                    {"type": "stat", "stat": "gold", "delta": 6},
                ],
            }
        ]
    },
    "199": {"loot": [{"id": "199-meal", "label": "Take 1 Meal", "actions": [{"type": "add_item", "container": "backpack", "name": "Meal"}]}]},
    "243": {"loot": [{"id": "243-mace", "label": "Take Mace", "actions": [{"type": "add_item", "container": "weapon", "name": "Mace"}]}]},
    "263": {"loot": [{"id": "263-gold", "label": "Take 3 Gold Crowns", "actions": [{"type": "stat", "stat": "gold", "delta": 3}]}]},
    "290": {"loot": [{"id": "290-quarterstaff", "label": "Take Quarterstaff", "actions": [{"type": "add_item", "container": "weapon", "name": "Quarterstaff"}]}]},
    "291": {
        "loot": [
            {"id": "291-gold", "label": "Take 6 Gold Crowns", "actions": [{"type": "stat", "stat": "gold", "delta": 6}]},
            {"id": "291-spear", "label": "Take Spear", "actions": [{"type": "add_item", "container": "weapon", "name": "Spear"}]},
            {"id": "291-dagger", "label": "Take Dagger", "actions": [{"type": "add_item", "container": "weapon", "name": "Dagger"}]},
        ]
    },
    "305": {"loot": [{"id": "305-spear", "label": "Take Giak Spear", "actions": [{"type": "add_item", "container": "weapon", "name": "Spear"}]}]},
    "307": {
        "loot": [
            {"id": "307-meal", "label": "Take 1 Meal", "actions": [{"type": "add_item", "container": "backpack", "name": "Meal"}]},
            {"id": "307-warhammer", "label": "Take Warhammer", "actions": [{"type": "add_item", "container": "weapon", "name": "Warhammer"}]},
        ]
    },
    "315": {
        "loot": [
            {
                "id": "315-purse",
                "label": "Take 6 Gold Crowns and Perfumed Soap",
                "actions": [
                    {"type": "stat", "stat": "gold", "delta": 6},
                    {"type": "add_item", "container": "backpack", "name": "Tablet of Perfumed Soap"},
                ],
            }
        ]
    },
    "319": {
        "loot": [
            {
                "id": "319-pouch",
                "label": "Take Dagger and 20 Gold Crowns",
                "actions": [
                    {"type": "add_item", "container": "weapon", "name": "Dagger"},
                    {"type": "stat", "stat": "gold", "delta": 20},
                ],
            }
        ]
    },
    "347": {"loot": [{"id": "347-torch", "label": "Take 1 Torch", "actions": [{"type": "add_item", "container": "backpack", "name": "Torch"}]}]},
}


MANUAL_COMBAT_AUDIT: dict[str, dict[str, Any]] = {
    "17": {
        "combat": [
            {
                "id": "17-kraan",
                "label": "Fight the Kraan",
                "enemy": combat_enemy("Kraan", 16, 24),
                "modifier": -1,
                "victoryChoices": [53, 274, 316],
            }
        ]
    },
    "29": {
        "combat": [
            {
                "id": "29-vordak",
                "label": "Fight the Vordak",
                "enemy": combat_enemy("Vordak", 17, 25),
                "conditionalModifiers": [
                    {
                        "label": "No Mindshield against Mindforce",
                        "modifier": -2,
                        "condition": {"type": "no_power", "name": "Mindshield"},
                    }
                ],
                "victoryRoute": 270,
            }
        ]
    },
    "34": {
        "combat": [
            {
                "id": "34-vordak",
                "label": "Fight the Vordak",
                "enemy": combat_enemy("Vordak", 17, 25),
                "conditionalModifiers": [
                    {
                        "label": "No Mindshield against Mindforce",
                        "modifier": -2,
                        "condition": {"type": "no_power", "name": "Mindshield"},
                    }
                ],
                "victoryRoute": 328,
            }
        ]
    },
    "43": {
        "combat": [
            {
                "id": "43-black-bear",
                "label": "Fight the Black Bear",
                "enemy": combat_enemy("Black Bear", 16, 10),
                "canEvade": True,
                "evadeAfterRounds": 3,
                "evadeRoute": 106,
                "victoryRoute": 195,
            }
        ]
    },
    "55": {
        "combat": [
            {
                "id": "55-giak",
                "label": "Fight the surprised Giak",
                "enemy": combat_enemy("Giak", 9, 9),
                "modifier": 4,
                "victoryRoute": 325,
            }
        ]
    },
    "63": {
        "combat": [
            {
                "id": "63-madman",
                "label": "Fight the Madman",
                "enemy": combat_enemy("Madman", 11, 10),
                "victoryRoute": 269,
            }
        ]
    },
    "72": {
        "combat": [
            {
                "id": "72-giak-doomwolf",
                "label": "Fight the Giak and Doomwolf",
                "enemy": combat_enemy("Giak and Doomwolf", 15, 24),
                "victoryRoute": 265,
            }
        ]
    },
    "112": {
        "combat": [
            {
                "id": "112-giaks",
                "label": "Fight the two Giaks",
                "enemies": [combat_enemy("Giak 1", 13, 10), combat_enemy("Giak 2", 12, 10)],
                "victoryChoices": [33, 248],
            }
        ]
    },
    "133": {
        "combat": [
            {
                "id": "133-winged-serpent",
                "label": "Fight the Winged Serpent",
                "enemy": combat_enemy("Winged Serpent", 16, 18),
                "enemyImmune": True,
                "victoryRoute": 266,
            }
        ]
    },
    "136": {
        "combat": [
            {
                "id": "136-giaks",
                "label": "Fight the two Giaks from higher ground",
                "enemies": [combat_enemy("Giak 1", 13, 10), combat_enemy("Giak 2", 12, 10)],
                "modifier": 1,
                "victoryRoute": 313,
            }
        ]
    },
    "138": {
        "combat": [
            {
                "id": "138-giaks",
                "label": "Fight the two Mountain Giaks",
                "enemies": [combat_enemy("Giak 1", 13, 10), combat_enemy("Giak 2", 12, 10)],
                "victoryRoute": 291,
            }
        ]
    },
    "169": {
        "combat": [
            {
                "id": "169-crypt-spawn",
                "label": "Fight the Crypt Spawn",
                "enemy": combat_enemy("Crypt Spawn", 16, 16),
                "canEvade": True,
                "evadeAfterRounds": 1,
                "evadeRoute": 23,
                "victoryRoute": 137,
            }
        ]
    },
    "170": {
        "combat": [
            {
                "id": "170-burrowcrawler",
                "label": "Fight the Burrowcrawler",
                "enemy": combat_enemy("Burrowcrawler", 17, 7),
                "enemyImmune": True,
                "conditionalModifiers": [
                    {
                        "label": "No Torch in Backpack",
                        "modifier": -3,
                        "condition": {
                            "type": "no_item",
                            "name": "Torch",
                            "containers": ["backpack"],
                            "match": "exact",
                        },
                    }
                ],
                "victoryRoute": 319,
            }
        ]
    },
    "180": {
        "combat": [
            {
                "id": "180-bandits",
                "label": "Fight the leader and soldiers",
                "enemies": [
                    combat_enemy("Leader", 15, 22),
                    combat_enemy("Soldier 1", 13, 20),
                    combat_enemy("Soldier 2", 12, 20),
                ],
                "victoryRoute": 62,
            }
        ]
    },
    "191": {
        "combat": [
            {
                "id": "191-bodyguard",
                "label": "Fight the Bodyguard",
                "enemy": combat_enemy("Bodyguard", 11, 21),
                "canEvade": True,
                "evadeRoute": 234,
                "victoryRoute": 24,
            }
        ]
    },
    "208": {
        "combat": [
            {
                "id": "208-giaks",
                "label": "Fight the Giaks",
                "enemy": combat_enemy("Giaks", 15, 13),
                "victoryChoices": [148, 320],
            }
        ]
    },
    "220": {
        "combat": [
            {
                "id": "220-bodyguard",
                "label": "Fight the Bodyguard",
                "enemy": combat_enemy("Bodyguard", 11, 20),
                "canEvade": True,
                "evadeRoute": 234,
                "victoryRoute": 24,
            }
        ]
    },
    "227": {
        "combat": [
            {
                "id": "227-marshviper",
                "label": "Fight the Marshviper",
                "enemy": combat_enemy("Marshviper", 16, 6),
                "woundedVictoryRoute": 271,
                "flawlessVictoryRoute": 348,
            }
        ]
    },
    "229": {
        "combat": [
            {
                "id": "229-kraan",
                "label": "Fight the Kraan in the dust",
                "enemy": combat_enemy("Kraan", 16, 25),
                "modifier": -1,
                "victoryChoices": [267, 125],
            }
        ]
    },
    "231": {
        "combat": [
            {
                "id": "231-robber",
                "label": "Fight the Robber",
                "enemy": combat_enemy("Robber", 13, 20),
                "canEvade": True,
                "evadeAfterRounds": 2,
                "evadeRoute": 7,
                "roundLimit": 4,
                "roundExceededRoute": 203,
                "winWithinRounds": 4,
                "winWithinRoute": 94,
                "tooLateRoute": 203,
            }
        ]
    },
    "246": {
        "combat": [
            {
                "id": "246-drakkar",
                "label": "Fight the Drakkar",
                "enemy": combat_enemy("Drakkar", 15, 23),
                "victoryRoute": 197,
            }
        ]
    },
    "253": {
        "combat": [
            {
                "id": "253-doomwolves",
                "label": "Fight the four Doomwolves",
                "enemies": [
                    combat_enemy("Doomwolf 1", 13, 24),
                    combat_enemy("Doomwolf 2", 14, 23),
                    combat_enemy("Doomwolf 3", 14, 22),
                    combat_enemy("Doomwolf 4", 15, 21),
                ],
                "victoryRoute": 278,
            }
        ]
    },
    "255": {
        "combat": [
            {
                "id": "255-gourgaz",
                "label": "Fight the Gourgaz",
                "enemy": combat_enemy("Gourgaz", 20, 30),
                "enemyImmune": True,
                "victoryRoute": 82,
            }
        ]
    },
    "260": {
        "combat": [
            {
                "id": "260-unarmed-giaks",
                "label": "Fight the Giaks unarmed",
                "enemies": [combat_enemy("Giak 1", 11, 18), combat_enemy("Giak 2", 12, 17)],
                "forceUnarmed": True,
                "victoryRoute": 156,
            }
        ]
    },
    "283": {
        "combat": [
            {
                "id": "283-vordak",
                "label": "Fight the Vordak",
                "enemy": combat_enemy("Vordak", 17, 25),
                "timedModifiers": [
                    {"label": "Surprise attack", "modifier": 2, "startRound": 1, "endRound": 1},
                    {
                        "label": "No Mindshield against Mindforce",
                        "modifier": -2,
                        "startRound": 2,
                        "endRound": 999,
                        "condition": {"type": "no_power", "name": "Mindshield"},
                    },
                ],
                "victoryRoute": 123,
            }
        ]
    },
    "336": {
        "combat": [
            {
                "id": "336-giaks",
                "label": "Fight the two Giaks",
                "enemies": [combat_enemy("Giak 1", 14, 11), combat_enemy("Giak 2", 13, 11)],
                "victoryRoute": 117,
            }
        ]
    },
    "339": {
        "combat": [
            {
                "id": "339-robber",
                "label": "Fight the Robber",
                "enemy": combat_enemy("Robber", 13, 20),
                "canEvade": True,
                "evadeRoute": 7,
                "roundLimit": 4,
                "roundExceededRoute": 203,
                "winWithinRounds": 4,
                "winWithinRoute": 94,
                "tooLateRoute": 203,
            }
        ]
    },
    "340": {
        "combat": [
            {
                "id": "340-giak-doomwolf",
                "label": "Fight the Giak and Doomwolf",
                "enemy": combat_enemy("Giak and Doomwolf", 14, 24),
                "victoryRoute": 193,
            }
        ]
    },
    "342": {
        "combat": [
            {
                "id": "342-vordak",
                "label": "Fight the Vordak",
                "enemy": combat_enemy("Vordak", 18, 26),
                "enemyImmune": True,
                "conditionalModifiers": [
                    {
                        "label": "No Mindshield against Mindforce",
                        "modifier": -2,
                        "condition": {"type": "no_power", "name": "Mindshield"},
                    }
                ],
                "victoryRoute": 123,
            }
        ]
    },
}


MANUAL_ROUTE_AUDIT: dict[str, dict[str, Any]] = {
    "2": section_roll(
        "Random route from the falling branch.",
        [
            roll_range(0, 4, 343, "Bad landing"),
            roll_range(5, 9, 276, "Less severe fall"),
        ],
    ),
    "7": section_roll(
        "Random route while escaping the shop.",
        [
            roll_range(0, 2, 108, "Caught by the crowd"),
            roll_range(3, 9, 25, "Escape through the crowd"),
        ],
    ),
    "9": item_route_check(9, "Vordak Gem", 236, 292, label="Vordak Gem possession"),
    "12": stat_route_check(12, "gold", 10, 262, 247, label="Ferryman fare"),
    "17": section_roll(
        "Random route after killing the Kraan.",
        [
            roll_range(0, 0, 53, "Kraan fall"),
            roll_range(1, 2, 274, "Lose weapons while escaping"),
            roll_range(3, 9, 316, "Clean escape"),
        ],
    ),
    "22": section_roll(
        "Random route after evading the bandits.",
        [
            roll_range(0, 4, 181, "Arrow misses"),
            roll_range(5, 9, 145, "Arrow hits"),
        ],
    ),
    "44": section_roll(
        "Random route after the Kraan attack.",
        [
            roll_range(0, 4, 277, "Weapon broken"),
            roll_range(5, 9, 338, "Weapon survives"),
        ],
    ),
    "49": section_roll(
        "Random route in the shop.",
        [
            roll_range(0, 4, 339, "Robber attacks"),
            roll_range(5, 9, 60, "Fatal trap"),
        ],
    ),
    "52": power_route_check(52, "Animal Kinship", 225, 250, label="Animal Kinship tree route"),
    "88": power_route_check(88, "Healing", 216, 31, label="Healing route", optional=True),
    "89": section_roll(
        "Random route while fleeing the Kraan.",
        [
            roll_range(0, 1, 53, "Fatal fall"),
            roll_range(2, 4, 274, "Lose weapons while escaping"),
            roll_range(5, 9, 316, "Clean escape"),
        ],
    ),
    "105": power_route_check(105, "Animal Kinship", 298, 335, label="Animal Kinship bird route", optional=True),
    "128": power_route_check(128, "Hunting", 297, 336, label="Hunting ambush route"),
    "160": section_roll(
        "Random route while hiding from Giaks.",
        [
            roll_range(0, 4, 286, "Detected"),
            roll_range(5, 9, 10, "Not spotted"),
        ],
    ),
    "162": power_route_check(
        162,
        "Mind Over Matter",
        258,
        127,
        label="Mind Over Matter escape route",
        requires_automation=True,
    ),
    "173": item_route_check(173, "Silver Key", 158, 259, label="Silver Key door route", container="special"),
    "203": stat_route_check(
        203,
        "end",
        10,
        80,
        344,
        label="END after the explosion",
        requires_automation=True,
    ),
    "205": section_roll(
        "Random route while fleeing the disguised Drakkarim.",
        [
            roll_range(0, 4, 181, "Arrow misses"),
            roll_range(5, 9, 145, "Arrow hits"),
        ],
    ),
    "226": section_roll(
        "Random route after the Kraan attack.",
        [
            roll_range(0, 4, 277, "Weapon broken"),
            roll_range(5, 9, 338, "Weapon survives"),
        ],
    ),
    "237": section_roll(
        "Random route while sneaking past the Giaks.",
        [
            roll_range(0, 4, 265, "Pass undetected"),
            roll_range(5, 9, 72, "Detected"),
        ],
    ),
    "242": power_route_check(242, "Mindshield", 166, 9, label="Mindshield psychic route"),
    "275": section_roll(
        "Random route on the left-hand track.",
        [
            roll_range(0, 4, 345, "Lose your footing"),
            roll_range(5, 9, 74, "Keep moving"),
        ],
    ),
    "279": section_roll(
        "Random route inside the cave.",
        [
            roll_range(0, 6, 112, "Giaks enter the cave"),
            roll_range(7, 9, 96, "Cave remains quiet"),
        ],
    ),
    "294": section_roll(
        "Random route after escaping the river.",
        [
            roll_range(0, 2, 230, "Riverbank route"),
            roll_range(3, 6, 190, "Forest route"),
            roll_range(7, 9, 321, "High bank route"),
        ],
    ),
    "302": section_roll(
        "Random route in the forest.",
        [
            roll_range(0, 2, 110, "Encounter ahead"),
            roll_range(3, 9, 285, "Clear path"),
        ],
    ),
    "303": power_route_check(303, "Camouflage", 237, 72, label="Camouflage patrol route"),
    "314": section_roll(
        "Random route into Holmgard.",
        [
            roll_range(0, 6, 341, "Reach the guildhall area"),
            roll_range(7, 9, 98, "Alternative city route"),
        ],
    ),
    "337": section_roll(
        "Random route after opening the gate.",
        [
            roll_range(0, 4, 219, "Discovered"),
            roll_range(5, 9, 317, "Slip through"),
        ],
    ),
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
    if 'class="combat"' in block_lower or "combat skill" in text and "endurance" in text:
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
    if section == MAX_SECTION or "02fotw/title.htm" in block_lower or "fire on the water" in text:
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
        sources = incoming.get(section, [])
        entry["incomingRouteCount"] = len(sources)

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
        "bookNumber": 1,
        "title": "Flight from the Dark",
        "source": "books/lw/01fftd/sect*.htm",
        "generatedBy": "testing/lwbook1_section_flow_audit.py",
        "sectionCount": len(sections),
        "expectedSectionCount": MAX_SECTION,
        "sourceRouteLinkCount": sum(int(entry["sourceRouteCount"]) for entry in sections.values()),
        "branchSectionCount": len(branch_sections),
        "terminalSectionCount": len(terminal_sections),
        "reachableFromSection1Count": len(reachable),
        "invalidSectionLinkCount": len(invalid_links),
        "missingSectionCount": len(missing_sections),
    }

    data: dict[str, Any] = {"1": {"_meta": meta}}
    for section in range(1, MAX_SECTION + 1):
        if section in sections:
            data["1"][str(section)] = sections[section]

    artifact = {
        "meta": meta,
        "missingSections": missing_sections,
        "invalidLinks": invalid_links,
        "unreachableFromSection1": unreachable,
        "terminalSections": terminal_sections,
        "branchSections": branch_sections,
        "classificationCounts": dict(sorted(classified_counts.items())),
        "manualFlowAuditCount": len(MANUAL_FLOW_AUDIT),
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
        "# LW Book 1 Section Flow Baseline",
        "",
        "Scope: source-link graph for local Project Aon Book 1 section files.",
        "",
        "This report records section numbers, graph counts, and audit classifications only. Do not copy Book 1 prose into committed audit artifacts.",
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
            "- `data/book1-section-flows.json` now contains one entry for every discovered section.",
            "- `sourceRoutes` is the compact legal-link baseline used by the assistant.",
            "- `classification` is heuristic and marks candidates for the later human section automation audit.",
            f"- {artifact['manualFlowAuditCount']} sections include confirmed optional loot buttons.",
            f"- {artifact['manualCombatAuditCount']} sections include confirmed combat presets.",
            f"- {artifact['manualRollAuditCount']} sections include confirmed roll helpers.",
            f"- {artifact['manualRouteCheckAuditCount']} sections include confirmed route checks.",
            "",
            "## Remaining Work",
            "",
            "- Continue route-check audit for optional discipline choices and route-specific side effects.",
            "- Expand simple automations only after each additional section effect is confirmed by the audit.",
            "- Continue combat/random audit for multi-roll sections and roll outcomes with immediate item/stat effects.",
        ]
    )
    return "\n".join(lines) + "\n"


def verify_assistant_routes() -> list[str]:
    sys.path.insert(0, str(ROOT))
    import lonewolf_redux  # pylint: disable=import-error,import-outside-toplevel

    save_dir = ROOT / "testing" / "tmp" / "section-flow-saves"
    assistant = lonewolf_redux.LoneWolfReduxAssistant(save_dir=save_dir, data_dir=ROOT / "data")
    assistant.last_save_file = ROOT / "testing" / "tmp" / "section-flow-last-save.txt"
    assistant.state = lonewolf_redux.create_book1_character_state(
        name="Route Smoke",
        kai_disciplines=lonewolf_redux.KAI_DISCIPLINES[:5],
        combat_skill_roll=4,
        endurance_roll=6,
        gold_roll=3,
        starting_find_roll=4,
        weaponskill_roll=6,
    )
    assistant.record_section_visit()

    errors: list[str] = []
    flow = assistant.current_section_flow_payload()
    routes = [int(route["Section"]) for route in flow.get("SourceRoutes", [])]
    if routes != [141, 85, 275]:
        errors.append(f"assistant section 1 routes were {routes}")
    route_audit = flow.get("RouteAudit", {})
    if route_audit.get("Status") != "source-link-baseline":
        errors.append(f"assistant route audit status was {route_audit.get('Status')!r}")

    with contextlib.redirect_stdout(io.StringIO()):
        assistant.follow_route(141)
    if int(assistant.state["CurrentSection"]) != 141:
        errors.append("assistant did not follow legal route 1 -> 141")

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
        if artifact["section1Routes"] != [141, 85, 275]:
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
        print("Book 1 section-flow baseline check passed.")

    if not args.write and not args.check:
        print(render_report(artifact))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

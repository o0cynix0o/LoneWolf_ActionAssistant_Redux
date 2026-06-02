#!/usr/bin/env python3
"""Build and verify the Book 4 section-flow baseline from local HTML."""

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
BOOK_NUMBER = 4
BOOK_TITLE = "The Chasm of Doom"
BOOK_CODE = "04tcod"
BOOK_DIR = ROOT / "books" / "lw" / BOOK_CODE
DATA_PATH = ROOT / "data" / "book4-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK4_SECTION_FLOW_BASELINE.md"
GRAPH_REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK4_ROUTE_GRAPH_CHECK.md"
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


def roll_range(
    minimum: int,
    maximum: int,
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {
        "test": "range",
        "min": minimum,
        "max": maximum,
        "route": route,
        "label": label,
    }
    if actions:
        outcome["actions"] = actions
    return outcome


def roll_values(
    values: list[int],
    route: int | None,
    label: str,
    actions: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    outcome: dict[str, Any] = {
        "test": "values",
        "values": values,
        "route": route,
        "label": label,
    }
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


def route_action(section: int, actions: list[dict[str, Any]], effect_label: str, label: str = "") -> dict[str, Any]:
    route: dict[str, Any] = {"Section": section, "actions": actions, "effectLabel": effect_label}
    if label:
        route["Label"] = label
    return route


def condition_outcome(
    label: str,
    route: int,
    condition: dict[str, Any] | None,
    test_label: str,
    choice_label: str = "",
) -> dict[str, Any]:
    outcome: dict[str, Any] = {"label": label, "route": route, "testLabel": test_label}
    if choice_label:
        outcome["choiceLabel"] = choice_label
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


def cond_any(*conditions: dict[str, Any]) -> dict[str, Any]:
    return {"type": "any", "conditions": list(conditions)}


def cond_all(*conditions: dict[str, Any]) -> dict[str, Any]:
    return {"type": "all", "conditions": list(conditions)}


def cond_rank(rank: str) -> dict[str, Any]:
    return {"type": "kai_rank_gte", "rank": rank}


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


def combined_route_checks(*entries: dict[str, Any]) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    for entry in entries:
        checks.extend([check for check in entry.get("routeChecks", []) if isinstance(check, dict)])
    return {"routeChecks": checks}


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
    match: str = "exact",
) -> dict[str, Any]:
    outcomes = [condition_outcome(f"{item} available", item_route, cond_item(item, container, match), f"Has {item}")]
    if no_item_route is not None:
        outcomes.append(condition_outcome(f"No {item}", no_item_route, cond_no_item(item, container, match), f"No {item}"))
    return route_check(
        f"{section}-{re.sub(r'[^a-z0-9]+', '-', item.lower()).strip('-')}",
        label or f"{item} route",
        f"Checks whether Lone Wolf has {item}.",
        outcomes,
    )


def rank_route_check(section: int, rank: str, rank_route: int, lower_route: int, *, label: str | None = None) -> dict[str, Any]:
    return route_check(
        f"{section}-{rank.lower()}",
        label or f"{rank}+ route",
        f"Checks whether Lone Wolf has reached Kai rank {rank}.",
        [
            condition_outcome(f"{rank} or higher", rank_route, cond_rank(rank), f"{rank}+"),
            condition_outcome(f"Below {rank}", lower_route, {"type": "no_item", "name": "__rank_placeholder__", "containers": ["special"]}, f"Below {rank}"),
        ],
    )


def loot_option(option_id: str, label: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {"id": option_id, "label": label, "actions": actions}


def add_items(container: str, name: str, count: int) -> list[dict[str, Any]]:
    return [{"type": "add_item", "container": container, "name": name} for _ in range(count)]


def gold(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "gold", "delta": delta}


def end(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "end", "delta": delta}


def restore_end(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "end", "delta": delta}


def meal_action(*, hunting_exempt: bool = True, suppressed: bool = False) -> dict[str, Any]:
    action: dict[str, Any] = {
        "type": "meal",
        "count": 1,
        "mode": "all_or_loss",
        "enduranceLoss": 3,
        "huntingExempt": hunting_exempt,
    }
    if suppressed:
        action["huntingSuppressed"] = True
    else:
        action["huntingSuppressedFlags"] = ["book4WildlandsHuntingSuppressed"]
    return action


def simple_item_check(section: int, item: str, yes_route: int, no_route: int, container: str = "special", match: str = "exact") -> dict[str, Any]:
    return item_route_check(section, item, yes_route, no_route, container=container, match=match)


TRACKING_OR_SIXTH_SENSE = cond_any(cond_power("Tracking"), cond_power("Sixth Sense"))
TORCH_AND_TINDERBOX = cond_all(
    cond_item("Torch", "backpack", "exact"),
    cond_item("Tinderbox", "backpack", "exact"),
)
RELIGHT_SOURCE = cond_any(TORCH_AND_TINDERBOX, cond_item("Firesphere", "backpack", "contains"), cond_item("Firesphere", "special", "contains"))
MINING_TOOL = cond_any(cond_item("Pick", "backpack", "contains"), cond_item("Shovel", "backpack", "contains"))


MANUAL_FLOW_AUDIT: dict[str, dict[str, Any]] = {
    "2": {
        "loot": [
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("mace", "Take Mace", [{"type": "add_item", "container": "weapon", "name": "Mace"}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("warhammer", "Take Warhammer", [{"type": "add_item", "container": "weapon", "name": "Warhammer"}]),
            loot_option("gold", "Take 12 Gold Crowns", [gold(12)]),
            loot_option("backpack", "Take Backpack", [{"type": "backpack", "available": True}]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
        ]
    },
    "10": {"loot": [loot_option("onyx-medallion", "Take Onyx Medallion", [{"type": "add_item", "container": "special", "name": "Onyx Medallion"}])]},
    "11": section_roll(
        "Dead-end tunnel return route.",
        [roll_range(0, 4, 97, "Return by one passage"), roll_range(5, 9, 190, "Return by the other passage")],
    ),
    "12": {
        "loot": [
            loot_option("backpack", "Accept replacement Backpack", [{"type": "backpack", "available": True}]),
            loot_option("meals", "Take Food for 3 Meals", add_items("backpack", "Meal", 3)),
            loot_option("rope", "Take Rope", [{"type": "add_item", "container": "backpack", "name": "Rope"}]),
            loot_option("laumspur", "Take Potion of Laumspur", [{"type": "add_item", "container": "backpack", "name": "Potion of Laumspur (+4 END)"}]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("spear", "Take Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}]),
        ]
    },
    "13": section_roll(
        "Troubadour-camp dawn route.",
        [roll_range(0, 4, 171, "Wildlands route"), roll_range(5, 9, 25, "Pass route")],
    ),
    "15": power_route_check(15, "Tracking", 264, 134),
    "21": power_route_check(21, "Tracking", 264, None, optional=True),
    "22": {
        "lossChoices": [
            {
                "id": "drop-pack-item-or-weapon",
                "label": "Lose dropped gear",
                "summary": "Choose one Backpack Item to lose. If none are eligible, choose a Weapon instead.",
                "containers": ["backpack"],
                "fallbackContainers": ["weapon"],
            }
        ]
    },
    "23": simple_item_check(23, "Brass Key", 282, 105, container="special"),
    "24": power_route_check(24, "Healing", 238, None, optional=True),
    "29": combined_route_checks(
        simple_item_check(29, "Firesphere", 168, None, container="backpack", match="contains"),
        simple_item_check(29, "Firesphere", 168, None, container="special", match="contains"),
    ),
    "31": section_roll(
        "White-water rapids check.",
        [roll_range(0, 4, 272, "Survive the rapids"), roll_range(5, 9, 329, "Swept to death")],
    ),
    "35": section_roll(
        "Bridge-guard dash check.",
        [roll_range(0, 7, 147, "Guard turns in time"), roll_range(8, 12, 231, "Clean sprint")],
        [{"label": "Hunting or Guardian+", "value": 3, "condition": cond_any(cond_power("Hunting"), cond_rank("Guardian"))}],
    ),
    "40": combined_route_checks(
        route_check(
            "40-tracking-aspirant",
            "Tracking at Aspirant rank",
            "Checks whether Tracking and Kai rank Aspirant unlock the safer mine route.",
            [
                condition_outcome("Tracking and Aspirant+", 349, cond_all(cond_power("Tracking"), cond_rank("Aspirant")), "Tracking + Aspirant+"),
            ],
        )
    ),
    "43": section_roll(
        "Speed-and-accuracy check.",
        [roll_range(0, 6, 262, "Too slow"), roll_range(7, 13, 111, "Fast enough")],
        [
            {"label": "Mind Over Matter or Weaponskill", "value": 1, "condition": cond_any(cond_power("Mind Over Matter"), cond_power("Weaponskill"))},
            {"label": "Hunting or Sixth Sense", "value": 2, "condition": cond_any(cond_power("Hunting"), cond_power("Sixth Sense"))},
        ],
    ),
    "44": {
        "loot": [
            loot_option("gold", "Take 12 Gold Crowns", [gold(12)]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
        ]
    },
    "50": section_roll(
        "Crossbow patrol charge.",
        [roll_range(0, 6, 184, "Overpowered by the volley"), roll_range(7, 9, 267, "Crossbow bolt hits")],
    ),
    "51": power_route_check(51, "Animal Kinship", 227, None, optional=True),
    "54": route_check(
        "54-healing-warmarn",
        "Healing at Warmarn rank",
        "Checks whether Healing and Kai rank Warmarn avoid the fungi.",
        [
            condition_outcome("Healing and Warmarn+", 4, cond_all(cond_power("Healing"), cond_rank("Warmarn")), "Healing + Warmarn+"),
        ],
    ),
    "57": {"routeChecks": [item_route_check(57, "Scroll", 279, None)["routeChecks"][0]]},
    "59": section_roll(
        "Warhound release route.",
        [roll_range(0, 4, 193, "Warhounds close in"), roll_range(5, 9, 260, "Warhounds overrun the line")],
    ),
    "63": section_roll(
        "Eshnar reply check.",
        [roll_range(0, 4, 259, "Hostile reply"), roll_range(5, 9, 95, "Suspicious but willing to talk")],
    ),
    "67": {
        **section_roll(
            "Disc-ambush escape check.",
            [roll_range(0, 4, 242, "Disc strikes true"), roll_range(5, 8, 263, "Dive for cover"), roll_range(9, 11, 278, "Clean escape")],
            [{"label": "Hunting or Mind Over Matter", "value": 2, "condition": cond_any(cond_power("Hunting"), cond_power("Mind Over Matter"))}],
        ),
        "routeChecks": [
            item_route_check(67, "Sommerswerd", 292, None)["routeChecks"][0],
        ],
    },
    "70": combined_route_checks(
        item_route_check(70, "Onyx Medallion", 305, None),
        route_check(
            "70-camouflage-guardian",
            "Camouflage at Guardian rank",
            "Checks whether Camouflage and Kai rank Guardian can bypass the bandits.",
            [condition_outcome("Camouflage and Guardian+", 49, cond_all(cond_power("Camouflage"), cond_rank("Guardian")), "Camouflage + Guardian+")],
        ),
    ),
    "73": item_route_check(73, "Flask of Holy Water", 283, 325, container="backpack"),
    "75": section_roll(
        "Escape from the melee.",
        [roll_range(0, 5, 192, "Cut down in the doorway"), roll_range(6, 12, 16, "Reach the door")],
        [{"label": "Camouflage", "value": 3, "condition": cond_power("Camouflage")}],
    ),
    "78": {
        "loot": [loot_option("holy-water", "Take Flask of Holy Water", [{"type": "add_item", "container": "backpack", "name": "Flask of Holy Water"}])]
    },
    "79": {
        "loot": [
            loot_option("tinderbox", "Take Tinderbox", [{"type": "add_item", "container": "backpack", "name": "Tinderbox"}]),
            loot_option("torch", "Take one spare Torch", [{"type": "add_item", "container": "backpack", "name": "Torch"}]),
        ]
    },
    "84": {
        "loot": [loot_option("scroll", "Take prophecy Scroll", [{"type": "add_item", "container": "special", "name": "Scroll"}])]
    },
    "87": {"routeChecks": [route_check("87-sixth-sense-or-tracking", "Sixth Sense or Tracking", "Checks whether either route-reading Discipline applies.", [condition_outcome("Sixth Sense or Tracking", 60, TRACKING_OR_SIXTH_SENSE, "Sixth Sense or Tracking")])["routeChecks"][0]]},
    "92": power_route_check(92, "Sixth Sense", 210, None, optional=True),
    "96": section_roll(
        "Meresquid capsize check.",
        [roll_range(0, 4, 47, "Fight in the water"), roll_range(5, 8, 234, "Dragged under"), roll_values([9], 334, "Watery grave")],
    ),
    "102": {
        "loot": [
            loot_option("gold", "Take 12 Gold Crowns", [gold(12)]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
        ]
    },
    "109": {
        "loot": [
            loot_option("gold", "Take 3 Gold Crowns", [gold(3)]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
        ]
    },
    "112": section_roll(
        "Bridge impact survival check.",
        [roll_range(-3, 4, 42, "Fatal impact"), roll_range(5, 12, 303, "Cling to the bridge")],
        [
            {"label": "Current END below 10", "value": -3, "condition": {"type": "end_lt", "value": 10}},
            {"label": "Current END above 20", "value": 3, "condition": {"type": "end_gte", "value": 21}},
        ],
    ),
    "113": rank_route_check(113, "Warmarn", 166, 14),
    "117": {
        **section_roll(
            "Dark-bridge balance check.",
            [roll_range(0, 6, 99, "Fall from the bridge"), roll_range(7, 12, 256, "Cross safely")],
            [{"label": "Sixth Sense or Tracking", "value": 3, "condition": TRACKING_OR_SIXTH_SENSE}],
        ),
        "routeChecks": [
            route_check("117-relight-source", "Torch relight source", "Checks for spare Torch plus Tinderbox, or a Firesphere.", [condition_outcome("Can relight torch", 22, RELIGHT_SOURCE, "Torch+Tinderbox or Firesphere")])["routeChecks"][0],
        ],
    },
    "118": {
        "routeChecks": [
            item_route_check(118, "Iron Key", 308, None, container="special")["routeChecks"][0],
        ],
        "loot": [loot_option("whip", "Take Whip", [{"type": "add_item", "container": "backpack", "name": "Whip"}])],
    },
    "123": {
        "loot": [
            loot_option("tinderbox", "Take Tinderbox", [{"type": "add_item", "container": "backpack", "name": "Tinderbox"}]),
            loot_option("torch", "Take one spare Torch", [{"type": "add_item", "container": "backpack", "name": "Torch"}]),
        ]
    },
    "126": section_roll(
        "Raider's Road dawn route.",
        [roll_range(0, 4, 25, "North Wildlands route"), roll_range(5, 9, 171, "South Wildlands route")],
    ),
    "128": section_roll(
        "Trapdoor escape check.",
        [roll_range(0, 4, 103, "Intercepted"), roll_range(5, 12, 98, "Reach the trapdoor")],
        [{"label": "Hunting", "value": 3, "condition": cond_power("Hunting")}],
    ),
    "136": power_route_check(136, "Healing", 313, 216),
    "152": {
        "loot": [
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("gold", "Take 6 Gold Crowns", [gold(6)]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
            loot_option("brass-key", "Take Brass Key", [{"type": "add_item", "container": "special", "name": "Brass Key"}]),
        ]
    },
    "154": section_roll(
        "Horse loss route check.",
        [roll_range(0, 2, 120, "Short company presses south"), roll_range(3, 9, 51, "Mounted company presses south")],
    ),
    "165": {
        "sourceRoutes": [
            {"Section": 319, "Label": "Accept the host meal"},
            route_action(13, [meal_action(hunting_exempt=False)], "Decline the host meal", "Decline and eat from Backpack"),
        ]
    },
    "167": {
        "loot": [loot_option("shovel", "Keep Shovel (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Shovel (2 spaces)"}])]
    },
    "173": {
        **section_roll(
            "Pillar-smash check.",
            [roll_range(0, 6, 143, "Pillar holds"), roll_range(7, 11, 179, "Pillar falls")],
            [{"label": "Pick or Shovel", "value": 2, "condition": MINING_TOOL}],
        ),
        "routeChecks": [item_route_check(173, "Sommerswerd", 275, None)["routeChecks"][0]],
    },
    "183": section_roll(
        "Crypt password bluff check.",
        [roll_range(0, 6, 198, "Guards see through it"), roll_range(7, 13, 338, "Password works")],
        [{"label": "Camouflage", "value": 4, "condition": cond_power("Camouflage")}],
    ),
    "189": section_roll(
        "Meresquid attack check.",
        [roll_range(0, 4, 234, "Dragged under"), roll_range(5, 9, 47, "Fight in the water")],
    ),
    "194": section_roll("Underwater endurance roll.", [roll_range(0, 9, None, "Set underwater round limit")]),
    "200": combined_route_checks(
        power_route_check(200, "Camouflage", 45, None, optional=True),
    ),
    "207": section_roll(
        "Bow-shot rescue check.",
        [roll_range(0, 4, 336, "Shot misses"), roll_range(5, 11, 218, "Shot saves the soldier")],
        [{"label": "Weaponskill", "value": 2, "condition": cond_power("Weaponskill")}],
    ),
    "209": rank_route_check(209, "Aspirant", 111, 43),
    "211": section_roll(
        "Mounted tactics outcome.",
        [roll_range(0, 4, 51, "Continue with the rangers"), roll_range(5, 9, 120, "Safer onward path")],
    ),
    "212": combined_route_checks(
        power_route_check(212, "Mind Over Matter", 41, 276),
    ),
    "213": {
        "loot": [
            loot_option("pickaxe", "Take Pickaxe (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Pickaxe (2 spaces)"}]),
            loot_option("shovel", "Take Shovel (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Shovel (2 spaces)"}]),
            loot_option("axe", "Take Axe", [{"type": "add_item", "container": "weapon", "name": "Axe"}]),
            loot_option("torch", "Take Torch", [{"type": "add_item", "container": "backpack", "name": "Torch"}]),
            loot_option("tinderbox", "Take Tinderbox", [{"type": "add_item", "container": "backpack", "name": "Tinderbox"}]),
            loot_option("hourglass", "Take Hourglass", [{"type": "add_item", "container": "backpack", "name": "Hourglass"}]),
        ]
    },
    "222": {
        "loot": [loot_option("dval-sword", "Take Captain D'Val's Sword", [{"type": "add_item", "container": "weapon", "name": "Captain D'Val's Sword"}])]
    },
    "224": {"routeChecks": [route_check("224-sixth-sense-or-tracking", "Sixth Sense or Tracking", "Checks whether either route-reading Discipline applies.", [condition_outcome("Sixth Sense or Tracking", 60, TRACKING_OR_SIXTH_SENSE, "Sixth Sense or Tracking")])["routeChecks"][0]]},
    "225": section_roll(
        "Bandit sniper check.",
        [roll_values([0], 181, "Fatal sniper shot"), roll_range(1, 5, 20, "Hit but alive"), roll_range(6, 9, 300, "Reach the defenders")],
    ),
    "230": {
        "loot": [
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("dagger", "Take Dagger", [{"type": "add_item", "container": "weapon", "name": "Dagger"}]),
            loot_option("gold", "Take 9 Gold Crowns", [gold(9)]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
        ]
    },
    "231": {
        "loot": [
            loot_option("gold", "Take 3 Gold Crowns", [gold(3)]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
            loot_option("meal", "Take Food for 1 Meal", [{"type": "add_item", "container": "backpack", "name": "Meal"}]),
        ]
    },
    "234": section_roll("Underwater endurance roll.", [roll_range(0, 9, None, "Set underwater round limit")]),
    "240": section_roll(
        "Waterfall survival check.",
        [roll_range(0, 4, 94, "Discard Backpack after the fall"), roll_range(5, 9, 158, "Concussed and alone")],
    ),
    "244": {"routeChecks": [route_check("244-sixth-sense-or-tracking", "Sixth Sense or Tracking", "Checks whether either route-reading Discipline applies.", [condition_outcome("Sixth Sense or Tracking", 250, TRACKING_OR_SIXTH_SENSE, "Sixth Sense or Tracking")])["routeChecks"][0]]},
    "247": section_roll(
        "Roadside camp dawn route.",
        [roll_range(0, 4, 171, "Wildlands route"), roll_range(5, 9, 25, "Pass route")],
    ),
    "249": section_roll(
        "Bow-shot leadership check.",
        [roll_range(0, 3, 153, "Shot fails"), roll_range(4, 7, 323, "Shot disrupts the leader"), roll_range(8, 11, 39, "Clean shot")],
        [{"label": "Weaponskill", "value": 2, "condition": cond_power("Weaponskill")}],
    ),
    "253": rank_route_check(253, "Warmarn", 72, 135),
    "258": combined_route_checks(
        item_route_check(258, "Onyx Medallion", 305, None),
        route_check(
            "258-camouflage-guardian",
            "Camouflage at Guardian rank",
            "Checks whether Camouflage and Kai rank Guardian can bypass the bandits.",
            [condition_outcome("Camouflage and Guardian+", 49, cond_all(cond_power("Camouflage"), cond_rank("Guardian")), "Camouflage + Guardian+")],
        ),
    ),
    "261": {"loot": [loot_option("meal", "Take Food for 1 Meal", [{"type": "add_item", "container": "backpack", "name": "Meal"}])]},
    "268": {
        "loot": [
            loot_option("gold", "Take 4 Gold Crowns", [gold(4)]),
            loot_option("spear", "Take Spear", [{"type": "add_item", "container": "weapon", "name": "Spear"}]),
            loot_option("broadsword", "Take Broadsword", [{"type": "add_item", "container": "weapon", "name": "Broadsword"}]),
            loot_option("iron-key", "Take Iron Key", [{"type": "add_item", "container": "special", "name": "Iron Key"}]),
            loot_option("brass-key", "Take Brass Key", [{"type": "add_item", "container": "special", "name": "Brass Key"}]),
            loot_option("meals", "Take Food for 2 Meals", add_items("backpack", "Meal", 2)),
            loot_option("laumspur", "Take Red Laumspur Potion", [{"type": "add_item", "container": "backpack", "name": "Potion of Laumspur (+4 END)"}]),
        ]
    },
    "269": {"loot": [loot_option("shovel", "Take Shovel (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Shovel (2 spaces)"}])]},
    "270": combined_route_checks(
        route_check("270-torch-and-tinderbox", "Torch and Tinderbox", "Checks whether a Torch and Tinderbox are available.", [condition_outcome("Torch and Tinderbox", 29, TORCH_AND_TINDERBOX, "Torch + Tinderbox")]),
        item_route_check(270, "Firesphere", 168, None, container="backpack", match="contains"),
        item_route_check(270, "Firesphere", 168, None, container="special", match="contains"),
    ),
    "271": section_roll(
        "Collapsing-bridge check.",
        [roll_range(0, 6, 9, "Bridge drops"), roll_range(7, 11, 104, "Escape the trap")],
        [{"label": "Hunting", "value": 2, "condition": cond_power("Hunting")}],
    ),
    "272": {
        "lossChoices": [
            {
                "id": "rapids-weapon-loss",
                "label": "Lose weapon in the rapids",
                "summary": "Choose the Weapon lost during the river ordeal.",
                "containers": ["weapon"],
            }
        ]
    },
    "274": item_route_check(274, "Flask of Holy Water", 283, 325, container="backpack"),
    "279": {"routeChecks": [item_route_check(279, "Scroll", 327, None)["routeChecks"][0]]},
    "280": {
        "loot": [
            loot_option("gold", "Take 3 Gold Crowns", [gold(3)]),
            loot_option("meal", "Take Food for 1 Meal", [{"type": "add_item", "container": "backpack", "name": "Meal"}]),
            loot_option("sword", "Take Sword", [{"type": "add_item", "container": "weapon", "name": "Sword"}]),
        ]
    },
    "289": rank_route_check(289, "Warmarn", 255, 5),
    "291": power_route_check(291, "Camouflage", 172, None, optional=True),
    "293": power_route_check(293, "Tracking", 18, 150),
    "296": item_route_check(296, "Sommerswerd", 122, 274),
    "301": power_route_check(301, "Animal Kinship", 106, 236),
    "302": {
        "loot": [
            loot_option("laumspur", "Take 2 Potions of Laumspur", add_items("backpack", "Potion of Laumspur (+4 END)", 2)),
            loot_option("alether", "Take Potion of Alether", [{"type": "add_item", "container": "backpack", "name": "Potion of Alether (+2 CS)"}]),
            loot_option("holy-water", "Take Flask of Holy Water", [{"type": "add_item", "container": "backpack", "name": "Flask of Holy Water"}]),
        ]
    },
    "304": section_roll(
        "Meresquid capsize check.",
        [roll_range(0, 4, 47, "Fight in the water"), roll_range(5, 9, 234, "Dragged under")],
    ),
    "309": section_roll(
        "Mine-ramp dash check.",
        [roll_range(0, 7, 138, "Guard notices"), roll_range(8, 13, 244, "Slip past")],
        [{"label": "Camouflage", "value": 4, "condition": cond_power("Camouflage")}],
    ),
    "312": section_roll(
        "Horse loss route check.",
        [roll_range(0, 2, 120, "Short company presses south"), roll_range(3, 9, 51, "Mounted company presses south")],
    ),
    "315": power_route_check(315, "Tracking", 48, None, optional=True),
    "318": {"routeChecks": [item_route_check(318, "Scroll", 279, None)["routeChecks"][0]]},
    "319": section_roll(
        "Troubadour camp dawn route.",
        [roll_range(0, 4, 25, "Pass route"), roll_range(5, 9, 171, "Wildlands route")],
    ),
    "322": {
        "loot": [
            loot_option("pick", "Take Pick (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Pick (2 spaces)"}]),
            loot_option("shovel", "Take Shovel (2 spaces)", [{"type": "add_item", "container": "backpack", "name": "Shovel (2 spaces)"}]),
        ]
    },
    "331": combined_route_checks(
        power_route_check(331, "Mind Over Matter", 41, 276),
    ),
    "335": power_route_check(335, "Camouflage", 35, None, optional=True),
    "343": section_roll(
        "Boat-capsize avoidance check.",
        [roll_range(-2, 6, 194, "Dragged into the water"), roll_range(7, 12, 61, "Avoid the worst of it")],
        [
            {"label": "Current END 20 or higher", "value": 3, "condition": {"type": "end_gte", "value": 20}},
            {"label": "Current END 12 or lower", "value": -2, "condition": {"type": "end_lt", "value": 13}},
        ],
    ),
    "344": rank_route_check(344, "Aspirant", 111, 43),
    "345": section_roll(
        "Horse count route check.",
        [roll_range(0, 6, 51, "Continue with the rangers"), roll_range(7, 9, 120, "Safer onward path")],
    ),
}


MANUAL_COMBAT_AUDIT: dict[str, dict[str, Any]] = {
    "14": {"combat": [combat_preset(14, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 28), canEvade=True, evadeRoute=31, victoryRoute=146)]},
    "26": {"combat": [combat_preset(26, "Stoneworm", combat_enemy("Stoneworm", 15, 38), enemyImmune=True, victoryRoute=321)]},
    "36": {"combat": [combat_preset(36, "Vassagonian Warhound", combat_enemy("Vassagonian Warhound", 17, 25), winWithinRounds=3, winWithinRoute=155, tooLateRoute=277)]},
    "46": {"combat": [combat_preset(46, "Tunnel Fiend", combat_enemy("Tunnel Fiend", 20, 10), victoryRoute=281)]},
    "47": {"combat": [combat_preset(47, "Giant Meresquid", combat_enemy("Giant Meresquid", 16, 37), winWithinRounds=5, winWithinRoute=32, tooLateRoute=340)]},
    "53": {"combat": [combat_preset(53, "Wounded Bandit", combat_enemy("Wounded Bandit", 13, 16), victoryRoute=109)]},
    "56": {"combat": [combat_preset(56, "Wounded Guard", combat_enemy("Wounded Guard", 12, 18), winWithinRounds=3, winWithinRoute=69, tooLateRoute=203)]},
    "62": {"combat": [combat_preset(62, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 24), timedModifiers=[{"startRound": 1, "endRound": 3, "modifier": -2}], victoryRoute=148)]},
    "65": {"combat": [combat_preset(65, "Tunnel Fiends", combat_enemy("Tunnel Fiends", 20, 10), victoryRoute=298)]},
    "77": {"combat": [combat_preset(77, "Vassagonian Captain", combat_enemy("Vassagonian Captain", 22, 28), enemyImmune=True, perRoundActions=[{"type": "stat", "stat": "end", "delta": -1, "condition": cond_no_power("Mindshield")}], canEvade=True, evadeAfterRounds=2, evadeRoute=98, victoryRoute=10)]},
    "88": {"combat": [combat_preset(88, "Stoneworm", combat_enemy("Stoneworm", 15, 38), enemyImmune=True, victoryRoute=321)]},
    "89": {"combat": [combat_preset(89, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 26), victoryRoute=7)]},
    "90": {"combat": [combat_preset(90, "Bandit Horseman", combat_enemy("Bandit Horseman", 17, 24), victoryRoute=249)]},
    "93": {"combat": [combat_preset(93, "Bandit Warrior", combat_enemy("Bandit Warrior", 15, 26), victoryRoute=2)]},
    "108": {"combat": [combat_preset(108, "Tunnel Guard Officer", combat_enemy("Tunnel Guard Officer", 20, 30), canEvade=True, evadeRoute=271, victoryRoute=28)]},
    "114": {"combat": [combat_preset(114, "Bandit Warrior", combat_enemy("Bandit Warrior", 16, 25), victoryRoute=295)]},
    "122": {"combat": [combat_preset(122, "Barraka", combat_enemy("Barraka", 25, 29), enemyImmune=True, conditionalModifiers=[{"condition": cond_no_power("Mindshield"), "modifier": -4, "label": "Mindblast attack"}], victoryRoute=350)]},
    "125": {"combat": [combat_preset(125, "Tunnel Guards", [combat_enemy("Tunnel Guard Leader", 20, 30), combat_enemy("Tunnel Guard 1", 18, 26), combat_enemy("Tunnel Guard 2", 16, 24)], victoryRoute=261)]},
    "133": {"combat": [combat_preset(133, "Bandit Patrol", combat_enemy("Bandit Patrol", 18, 35), canEvade=True, evadeRoute=307, playerLossRoute=17, flawlessVictoryRoute=265)]},
    "138": {"combat": [combat_preset(138, "Drunken Guard", combat_enemy("Drunken Guard", 13, 29), canEvade=True, evadeRoute=81, victoryRoute=152)]},
    "143": {"combat": [combat_preset(143, "Tunnel Guards", [combat_enemy("Tunnel Guard 1", 16, 22), combat_enemy("Tunnel Guard 2", 15, 21)], canEvade=True, evadeRoute=87, victoryRoute=230)]},
    "147": {"combat": [combat_preset(147, "Bridge Guard", combat_enemy("Bridge Guard", 14, 23), ignorePlayerLossRounds=1, victoryRoute=280)]},
    "153": {"combat": [combat_preset(153, "Vassagonian Warrior", combat_enemy("Vassagonian Warrior", 17, 26), timedModifiers=[{"startRound": 1, "endRound": 2, "modifier": -4}], victoryRoute=174)]},
    "169": {"combat": [combat_preset(169, "Bandit Warrior", combat_enemy("Bandit Warrior", 16, 24), victoryRoute=123)]},
    "176": {"combat": [combat_preset(176, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 25), victoryRoute=7)]},
    "186": {"combat": [combat_preset(186, "Vassagonian Warrior", combat_enemy("Vassagonian Warrior", 18, 25), canEvade=True, evadeRoute=66, victoryRoute=243)]},
    "193": {"combat": [combat_preset(193, "Vassagonian Warhounds", combat_enemy("Vassagonian Warhounds", 17, 30), roundLimit=2, survivalRoute=311, victoryRoute=311)]},
    "194": {"combat": [combat_preset(194, "Giant Meresquid", combat_enemy("Giant Meresquid", 16, 37), oxygenSafeRoundsFromRoll=True, oxygenMindOverMatterBonus=2, victoryRoute=32)]},
    "196": {"combat": [combat_preset(196, "Bandit Warrior", combat_enemy("Bandit Warrior", 16, 23), victoryRoute=217)]},
    "198": {"combat": [combat_preset(198, "Crypt Guards", combat_enemy("Crypt Guards", 18, 30), victoryRoute=229)]},
    "202": {"combat": [combat_preset(202, "Bridge Guards", [combat_enemy("Guard 1", 18, 23), combat_enemy("Guard 2", 15, 24), combat_enemy("Guard 3", 15, 21), combat_enemy("Guard 4", 16, 25), combat_enemy("Guard 5", 14, 24), combat_enemy("Guard 6", 14, 22)], canEvade=True, evadeRoute=342, victoryRoute=237)]},
    "208": {"combat": [combat_preset(208, "Tunnel Guards", [combat_enemy("Tunnel Guard 1", 15, 25), combat_enemy("Tunnel Guard 2", 15, 24), combat_enemy("Tunnel Guard 3", 14, 22)], victoryRoute=199)]},
    "233": {"combat": [combat_preset(233, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 26), victoryRoute=312)]},
    "234": {"combat": [combat_preset(234, "Giant Meresquid", combat_enemy("Giant Meresquid", 16, 37), oxygenSafeRoundsFromRoll=True, oxygenMindOverMatterBonus=2, victoryRoute=32)]},
    "260": {"combat": [combat_preset(260, "Vassagonian Warhounds", combat_enemy("Vassagonian Warhounds", 18, 30), roundLimit=3, survivalRoute=311, victoryRoute=311)]},
    "277": {"combat": [combat_preset(277, "Vassagonian Warhounds", combat_enemy("Vassagonian Warhounds", 22, 35), victoryRoute=155)]},
    "284": {"combat": [combat_preset(284, "Bandit Warrior", combat_enemy("Bandit Warrior", 16, 25), canEvade=True, evadeRoute=89, victoryRoute=7)]},
    "285": {"combat": [combat_preset(285, "Guard", combat_enemy("Guard", 16, 28), victoryRoute=71)]},
    "287": {"combat": [combat_preset(287, "Bandit Warrior", combat_enemy("Bandit Warrior", 17, 27), victoryRoute=75)]},
    "299": {"combat": [combat_preset(299, "Bandit Leader", combat_enemy("Bandit Leader", 19, 29), victoryRoute=121)]},
    "308": {"combat": [combat_preset(308, "Elix", combat_enemy("Elix", 17, 30), victoryRoute=127)]},
    "310": {"combat": [combat_preset(310, "Vassagonian Warrior", combat_enemy("Vassagonian Warrior", 18, 25), victoryRoute=24)]},
    "316": {"combat": [combat_preset(316, "Bandit Warrior", combat_enemy("Bandit Warrior", 16, 26), modifier=-2, canEvade=True, evadeRoute=31, victoryRoute=146)]},
    "325": {"combat": [combat_preset(325, "Barraka", combat_enemy("Barraka", 25, 29), enemyImmune=True, victoryRoute=350)]},
    "333": {"combat": [combat_preset(333, "Vassagonian Horseman", combat_enemy("Vassagonian Horseman", 20, 28), oneRoundComparisonRoutes={"playerLossGreater": 209, "enemyLossGreater": 220, "equal": 344})]},
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
            "badge of rank",
            "map of the southlands",
        )
    ):
        add_class(classes, "inventory")
    if "endurance" in text and any(term in text for term in ("lose", "deduct", "reduce")):
        add_class(classes, "endurance_loss")
    if "endurance" in text and any(term in text for term in ("restore", "regain", "heal")):
        add_class(classes, "endurance_gain")
    if "combat skill" in text and any(term in text for term in ("add", "deduct", "reduce", "increase")):
        add_class(classes, "combat_skill_modifier")
    if any(
        term in text
        for term in (
            "you are dead",
            "your adventure ends",
            "mission has failed",
            "your life and your mission end",
            "your mission and your life end",
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
        block = maintext_block(path.read_text(encoding="utf-8", errors="ignore"))
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
        "generatedBy": "testing/lwbook4_section_flow_audit.py",
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
        "manualRollAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "roll" in entry),
        "manualLossChoiceAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "lossChoices" in entry),
    }
    return data, artifact


def render_report(artifact: dict[str, Any]) -> str:
    meta = artifact["meta"]
    counts = artifact["classificationCounts"]
    lines = [
        "# LW Book 4 Section Flow Baseline",
        "",
        "Scope: source-link graph for local Project Aon Book 4 section files.",
        "",
        "This report records section numbers, graph counts, and audit classifications only. Do not copy Book 4 prose into committed audit artifacts.",
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
        f"- Confirmed random-roll helper sections: {artifact['manualRollAuditCount']}",
        f"- Confirmed loss-choice sections: {artifact['manualLossChoiceAuditCount']}",
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
            "- `data/book4-section-flows.json` contains one source-link baseline entry for every discovered section.",
            "- `sourceRoutes` is the compact legal-link baseline used for later helper implementation.",
            "- `classification` is heuristic and remains useful for review slices.",
            "- Book 4 now carries confirmed helpers for setup-sensitive routes, random rolls, combat presets, optional loot, and the section 22 item-loss picker.",
            "",
            "## Remaining Risk",
            "",
            "- This pass still keeps the local Project Aon HTML as the source of truth.",
            "- Combat and loot helper coverage is intentionally practical rather than final; playtesting can add polish where Book 4 wording needs a friendlier helper button.",
            "- Achievements and full lore-guide coverage are separate passes after the first playable Book 4 run.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_graph_report(graph: dict[str, Any]) -> str:
    available = bool(graph.get("available"))
    svg_not_local = graph.get("svgEdgesNotLocal", [])
    local_not_svg = graph.get("localEdgesNotSvg", [])
    lines = [
        "# LW Book 4 Route Graph Check",
        "",
        "Scope: optional Project Aon SVG/SVGZ route graph cross-check.",
        "",
        "The local Project Aon HTML files remain the source of truth. The online SVG graph is used only as an external consistency check.",
        "",
        "## Summary",
        "",
        f"- URL: `{graph.get('url')}`",
        f"- Available: {'yes' if available else 'no'}",
        f"- HTTP status: {graph.get('status') if graph.get('status') is not None else 'n/a'}",
        f"- SVG nodes: {graph.get('nodeCount', 0)}",
        f"- SVG edges: {graph.get('edgeCount', 0)}",
        f"- Local nodes: {graph.get('localNodeCount', 0)}",
        f"- Local source-link edges: {graph.get('localEdgeCount', 0)}",
        f"- SVG edges not in local source links: {len(svg_not_local)}",
        f"- Local source links not in SVG edges: {len(local_not_svg)}",
        "",
        "## Differences",
        "",
        f"- SVG-only edges: {json.dumps(svg_not_local[:80]) if svg_not_local else 'none'}",
        f"- Local-only edges: {json.dumps(local_not_svg[:80]) if local_not_svg else 'none'}",
        "",
    ]
    if graph.get("error"):
        lines.extend(["## Error", "", str(graph.get("error")), ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write data and report artifacts")
    parser.add_argument("--check", action="store_true", help="check existing artifacts")
    args = parser.parse_args()

    data, artifact = build_graph()
    data_text = json.dumps(data, indent=2) + "\n"
    report_text = render_report(artifact)
    graph_report_text = render_graph_report(artifact["routeGraphCheck"])

    if args.write:
        DATA_PATH.write_text(data_text, encoding="utf-8")
        REPORT_PATH.write_text(report_text, encoding="utf-8")
        GRAPH_REPORT_PATH.write_text(graph_report_text, encoding="utf-8")
        print(f"Wrote {DATA_PATH}")
        print(f"Wrote {REPORT_PATH}")
        print(f"Wrote {GRAPH_REPORT_PATH}")
        return 0

    if args.check:
        failures = []
        if not DATA_PATH.exists() or DATA_PATH.read_text(encoding="utf-8") != data_text:
            failures.append(str(DATA_PATH))
        if not REPORT_PATH.exists() or REPORT_PATH.read_text(encoding="utf-8") != report_text:
            failures.append(str(REPORT_PATH))
        if not GRAPH_REPORT_PATH.exists() or GRAPH_REPORT_PATH.read_text(encoding="utf-8") != graph_report_text:
            failures.append(str(GRAPH_REPORT_PATH))
        if failures:
            print("Out of date: " + ", ".join(failures))
            return 1
        print("Book 4 section-flow baseline check passed.")
        return 0

    print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

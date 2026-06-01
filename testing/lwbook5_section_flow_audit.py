#!/usr/bin/env python3
"""Build and verify the Book 5 section-flow baseline from local HTML."""

from __future__ import annotations

import argparse
import gzip
import html
import json
import re
import urllib.request
from collections import deque
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_NUMBER = 5
BOOK_TITLE = "Shadow on the Sand"
BOOK_CODE = "05sots"
BOOK_DIR = ROOT / "books" / "lw" / BOOK_CODE
DATA_PATH = ROOT / "data" / "book5-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK5_SECTION_FLOW_BASELINE.md"
GRAPH_REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK5_ROUTE_GRAPH_CHECK.md"
MAX_SECTION = 400
SVG_GRAPH_URL = f"https://www.projectaon.org/en/svg/lw/{BOOK_CODE}.svgz"


def combat_enemy(name: str, cs: int, endurance: int) -> dict[str, Any]:
    return {"name": name, "cs": cs, "endurance": endurance}


def combat_preset(section: int, label: str, enemy: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
    preset: dict[str, Any] = {
        "id": f"{section}-{re.sub(r'[^a-z0-9]+', '-', label.lower()).strip('-')}",
        "label": label,
        "enemy": enemy,
    }
    preset.update(kwargs)
    return preset


def roll_range(minimum: int, maximum: int, route: int | None, label: str) -> dict[str, Any]:
    return {"test": "range", "min": minimum, "max": maximum, "route": route, "label": label}


def section_roll(summary: str, outcomes: list[dict[str, Any]], modifiers: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    roll: dict[str, Any] = {"summary": summary, "outcomes": outcomes}
    if modifiers:
        roll["modifiers"] = modifiers
    return {"roll": roll}


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


def condition_outcome(label: str, route: int, condition: dict[str, Any], test_label: str) -> dict[str, Any]:
    return {"label": label, "route": route, "conditions": [condition], "testLabel": test_label}


def route_check(check_id: str, label: str, summary: str, outcomes: list[dict[str, Any]], formula: dict[str, Any] | None = None) -> dict[str, Any]:
    check: dict[str, Any] = {"id": check_id, "label": label, "summary": summary, "outcomes": outcomes}
    if formula:
        check["formula"] = formula
    return {"routeChecks": [check]}


def power_route_check(section: int, power: str, yes_route: int, no_route: int | None = None) -> dict[str, Any]:
    outcomes = [condition_outcome(f"{power} available", yes_route, cond_power(power), f"Has {power}")]
    if no_route is not None:
        outcomes.append(condition_outcome(f"No {power}", no_route, cond_no_power(power), f"No {power}"))
    return route_check(
        f"{section}-{power.lower().replace(' ', '-')}",
        f"{power} route",
        f"Checks whether Lone Wolf has {power}.",
        outcomes,
    )


def item_route_check(section: int, item: str, yes_route: int, no_route: int | None = None, *, container: str = "special", match: str = "exact") -> dict[str, Any]:
    outcomes = [condition_outcome(f"{item} available", yes_route, cond_item(item, container, match), f"Has {item}")]
    if no_route is not None:
        outcomes.append(condition_outcome(f"No {item}", no_route, cond_no_item(item, container, match), f"No {item}"))
    return route_check(
        f"{section}-{re.sub(r'[^a-z0-9]+', '-', item.lower()).strip('-')}",
        f"{item} route",
        f"Checks whether Lone Wolf has {item}.",
        outcomes,
    )


def loot_option(option_id: str, label: str, actions: list[dict[str, Any]]) -> dict[str, Any]:
    return {"id": option_id, "label": label, "actions": actions}


def add_items(container: str, name: str, count: int) -> list[dict[str, Any]]:
    return [{"type": "add_item", "container": container, "name": name} for _ in range(count)]


def gold(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "gold", "delta": delta}


def end(delta: int) -> dict[str, Any]:
    return {"type": "stat", "stat": "end", "delta": delta}


def route_action(section: int, actions: list[dict[str, Any]], effect_label: str, label: str = "") -> dict[str, Any]:
    route: dict[str, Any] = {"Section": section, "Actions": actions, "EffectLabel": effect_label}
    if label:
        route["Label"] = label
    return route


TRACKING_OR_SIXTH_SENSE = cond_any(cond_power("Tracking"), cond_power("Sixth Sense"))
TINCTURE_OF_GRAVEWEED = cond_item("Tincture of Graveweed", "backpack", "exact")


MANUAL_FLOW_AUDIT: dict[str, dict[str, Any]] = {
    "3": {"loot": [
        loot_option("gold", "Take 4 Gold Crowns", [gold(4)]),
        loot_option("dagger", "Take Dagger", add_items("weapon", "Dagger", 1)),
        loot_option("sword", "Take Sword", add_items("weapon", "Sword", 1)),
        loot_option("alether", "Take Potion of Alether", add_items("backpack", "Potion of Alether (+2 CS)", 1)),
        loot_option("blowpipe", "Take Blowpipe", add_items("backpack", "Blowpipe", 1)),
        loot_option("sleep-dart", "Take Sleep Dart", add_items("backpack", "Sleep Dart", 1)),
    ]},
    "8": section_roll("Cloeasian lock insight.", [roll_range(0, 9, None, "Choose 67 or 76 after losing 2 END")]),
    "19": {"lossChoices": [
        {"id": "guard-payment-1", "label": "Pay guards item 1", "summary": "Give the guards one non-Meal Backpack Item.", "containers": ["backpack"], "excludeNames": ["Meal"]},
        {"id": "guard-payment-2", "label": "Pay guards item 2", "summary": "Give the guards a second non-Meal Backpack Item.", "containers": ["backpack"], "excludeNames": ["Meal"]},
    ]},
    "31": item_route_check(31, "Tinderbox", 143, 183, container="backpack"),
    "40": {"lossChoices": [{"id": "kwaraz-pack-loss", "label": "Lose Backpack Item", "summary": "Choose one Backpack Item lost in the slime wave.", "containers": ["backpack"]}]},
    "56": section_roll(
        "One-shot Jakan Bow check.",
        [roll_range(0, 3, 7, "Shot fails"), roll_range(4, 11, 28, "Shot succeeds")],
        [{"label": "Weaponskill", "value": 2, "condition": cond_power("Weaponskill")}],
    ),
    "58": {
        "sourceRoutes": [{"Section": 67, "Label": "Correct lock answer"}, {"Section": 98}, {"Section": 156}],
        "routeChecks": route_check("58-cloeasian-lock", "Cloeasian lock", "The confirmed lock answer is section 67.", [condition_outcome("Correct answer", 67, {"type": "end_gte", "value": 0}, "67")])["routeChecks"],
    },
    "67": {"sourceRoutes": [{"Section": 200, "Label": "Leave the arboretum"}, {"Section": 58, "Label": "Backtrack"}], "loot": [loot_option("quarterstaff", "Take Quarterstaff", add_items("weapon", "Quarterstaff", 1))]},
    "111": {"loot": [loot_option("gold", "Take 3 Gold Crowns", [gold(3)]), loot_option("copper-key", "Take Copper Key", add_items("special", "Copper Key", 1))]},
    "118": section_roll(
        "Blowpipe dodge.",
        [roll_range(0, 3, 89, "Needle hits"), roll_range(4, 12, 21, "Dodge the needle")],
        [{"label": "Hunting", "value": 2, "condition": cond_power("Hunting")}, {"label": "Warmarn+", "value": 1, "condition": cond_rank("Warmarn")}],
    ),
    "125": section_roll("Leap to the galley.", [roll_range(0, 3, 50, "Fall short"), roll_range(4, 11, 191, "Reach the oars")], [{"label": "Hunting", "value": 2, "condition": cond_power("Hunting")}]),
    "126": route_check("126-camouflage-hunting", "Camouflage and Hunting", "Checks the stealth route through the north gate.", [condition_outcome("Camouflage and Hunting", 170, cond_all(cond_power("Camouflage"), cond_power("Hunting")), "Camouflage + Hunting")]),
    "128": item_route_check(128, "Rope", 29, None, container="backpack"),
    "130": {"loot": [loot_option("herb-pad", "Take Herb Pad", add_items("special", "Herb Pad", 1))]},
    "131": {"loot": [
        loot_option("silver-comb", "Take Silver Comb", add_items("backpack", "Silver Comb", 1)),
        loot_option("hourglass", "Take Hourglass", add_items("backpack", "Hourglass", 1)),
        loot_option("dagger", "Take Dagger", add_items("weapon", "Dagger", 1)),
        loot_option("laumspur", "Take Laumspur", add_items("backpack", "Potion of Laumspur (+4 END)", 1)),
        loot_option("prism", "Take Prism", add_items("backpack", "Prism", 1)),
        loot_option("meals", "Take Food for 3 Meals", add_items("backpack", "Meal", 3)),
    ]},
    "137": route_check("137-tracking-sixth-sense", "Tracking or Sixth Sense", "Checks which palace entrance is useful.", [condition_outcome("Tracking or Sixth Sense", 37, TRACKING_OR_SIXTH_SENSE, "Tracking or Sixth Sense")]),
    "207": {"loot": [loot_option("gold", "Take 8 Gold Crowns", [gold(8)]), loot_option("brass-whistle", "Take Brass Whistle", add_items("special", "Brass Whistle", 1))]},
    "211": {"loot": [loot_option("kourshah", "Buy Bottle of Kourshah", [gold(-5), {"type": "add_item", "container": "backpack", "name": "Bottle of Kourshah (+4 END)"}])]},
    "239": {
        **section_roll(
            "Silence the Drakkarim sentry.",
            [roll_range(0, 4, 324, "Sentry sounds the alarm"), roll_range(5, 14, 303, "Sentry silenced")],
            [
                {"label": "Hunting, Tracking, and Camouflage", "value": 2, "condition": cond_all(cond_power("Hunting"), cond_power("Tracking"), cond_power("Camouflage"))},
                {"label": "Guardian+", "value": 3, "condition": cond_rank("Guardian")},
            ],
        ),
        "routeChecks": route_check("239-graveweed", "Tincture of Graveweed", "Only Tincture of Graveweed counts here.", [condition_outcome("Use Tincture of Graveweed", 260, TINCTURE_OF_GRAVEWEED, "Tincture of Graveweed")])["routeChecks"],
    },
    "264": item_route_check(264, "Sommerswerd", 315, 299, container="special"),
    "270": {"lossChoices": [
        {"id": "cave-pack-loss-1", "label": "Lose item 1", "summary": "Choose the first Backpack Item lost while fleeing. If none are available, lose a Weapon or Special Item.", "containers": ["backpack"], "fallbackContainers": ["weapon", "special"]},
        {"id": "cave-pack-loss-2", "label": "Lose item 2", "summary": "Choose the second Backpack Item lost while fleeing. If none are available, lose a Weapon or Special Item.", "containers": ["backpack"], "fallbackContainers": ["weapon", "special"]},
    ]},
    "302": section_roll(
        "Bor-brew check.",
        [roll_range(-2, 6, 364, "Bor-brew wins"), roll_range(7, 14, 218, "Hold your drink")],
        [
            {"label": "END below 15", "value": -2, "condition": {"type": "end_lt", "value": 15}},
            {"label": "END above 25", "value": 2, "condition": {"type": "end_gte", "value": 26}},
            {"label": "Savant+", "value": 3, "condition": cond_rank("Savant")},
        ],
    ),
    "331": {"sourceRoutes": [{"Section": 373, "Label": "Solve the map code"}], "routeChecks": route_check("331-map-code", "Map code answer", "The confirmed answer is section 373.", [condition_outcome("Correct answer", 373, {"type": "end_gte", "value": 0}, "373")])["routeChecks"]},
    "350": {"sourceRoutes": [
        route_action(253, [{"type": "flag", "key": "book5SommerswerdLost", "value": True}], "Sommerswerd lost", "Mindshield route"),
        route_action(369, [{"type": "flag", "key": "book5SommerswerdLost", "value": True}], "Sommerswerd lost", "No Mindshield route"),
    ]},
}


MANUAL_COMBAT_AUDIT: dict[str, dict[str, Any]] = {
    "4": {"combat": [combat_preset(4, "Palace Gaoler", combat_enemy("Palace Gaoler", 14, 21), ignoreEnemyLossRounds=1, winWithinRounds=4, winWithinRoute=165, tooLateRoute=180, roundLimit=4, roundExceededRoute=180)]},
    "12": {"combat": [combat_preset(12, "Bloodlug", combat_enemy("Bloodlug", 17, 11), modifier=-2, enemyImmune=True, victoryRoute=95)]},
    "20": {"combat": [combat_preset(20, "Horseman", combat_enemy("Horseman", 21, 28), canEvade=True, evadeRoute=142, winWithinRounds=3, winWithinRoute=125, tooLateRoute=82, roundLimit=3, roundExceededRoute=82, defeatRoute=161, restoreHalfPlayerEnduranceLossAfterCombat=True)]},
    "57": {"combat": [combat_preset(57, "Elix", combat_enemy("Elix", 17, 32), conditionalModifiers=[{"condition": {"type": "fought_enemy", "name": "Elix"}, "modifier": 2, "label": "Previous Elix experience"}], victoryRoute=2)]},
    "64": {"combat": [combat_preset(64, "Kwaraz", combat_enemy("Kwaraz", 20, 30), conditionalModifiers=[{"condition": cond_power("Mindblast"), "modifier": 2, "label": "Kwaraz susceptibility"}], victoryRoute=177)]},
    "91": {"combat": [combat_preset(91, "Palace Gaoler", combat_enemy("Palace Gaoler", 14, 21), modifier=-4, winWithinRounds=4, winWithinRoute=65, tooLateRoute=180, roundLimit=4, roundExceededRoute=180)]},
    "106": {"combat": [combat_preset(106, "Courier", combat_enemy("Courier", 16, 23), timedModifiers=[{"startRound": 1, "endRound": 3, "modifier": -2}], victoryRoute=189)]},
    "110": {"combat": [combat_preset(110, "Kwaraz", combat_enemy("Kwaraz", 19, 30), conditionalModifiers=[{"condition": cond_power("Mindblast"), "modifier": 2, "label": "Kwaraz susceptibility"}], victoryRoute=40)]},
    "119": {"combat": [combat_preset(119, "Palace Gate Guardians", combat_enemy("Palace Gate Guardians", 16, 30), ignorePlayerLossRounds=3, victoryRoute=137)]},
    "123": {"combat": [combat_preset(123, "Sharnazim Underlord", combat_enemy("Sharnazim Underlord", 18, 28), canEvade=True, evadeRoute=51, victoryRoute=198)]},
    "135": {"combat": [combat_preset(135, "Sharnazim Warrior", combat_enemy("Sharnazim Warrior", 17, 22), modifier=-2, restoreHalfPlayerEnduranceLossAfterCombat=True, victoryRoute=130, defeatRoute=161)]},
    "159": {"combat": [combat_preset(159, "Armoury Guard", combat_enemy("Armoury Guard", 16, 22), timedModifiers=[{"startRound": 1, "endRound": 3, "modifier": -2}], victoryRoute=52)]},
    "168": {"combat": [combat_preset(168, "Vestibule Guard", combat_enemy("Vestibule Guard", 15, 23), winWithinRounds=3, winWithinRoute=101, tooLateRoute=46, roundLimit=3, roundExceededRoute=46)]},
    "178": {"combat": [combat_preset(178, "Armoury Guard", combat_enemy("Armoury Guard", 16, 22), victoryChoices=[52, 140])]},
    "190": {"combat": [combat_preset(190, "Hammerfist the Armourer", combat_enemy("Hammerfist the Armourer", 18, 30), modifier=-2, victoryRoute=111)]},
    "194": {"combat": [combat_preset(194, "Yas", combat_enemy("Yas", 14, 28), conditionalModifiers=[{"condition": cond_no_power("Mindshield"), "modifier": -3, "label": "Yas hypnosis"}], victoryRoute=35)]},
    "223": {"combat": [combat_preset(223, "Crypt Spawn", combat_enemy("Crypt Spawn", 24, 40), victoryRoute=353)]},
    "240": {"combat": [combat_preset(240, "Itikar", combat_enemy("Itikar", 17, 30), doubleEnemyLoss=True, victoryRoute=217)]},
    "244": {"combat": [combat_preset(244, "Drakkarim Kraan-rider", combat_enemy("Drakkarim Kraan-rider", 20, 28), oneRoundComparisonRoutes={"playerLossGreater": 347, "enemyLossGreater": 327, "equal": 271})]},
    "253": {"combat": [combat_preset(253, "Dhorgaan", combat_enemy("Dhorgaan", 20, 40), conditionalModifiers=[{"condition": cond_item("Jewelled Mace", "special", "contains"), "modifier": 5, "label": "Jewelled Mace"}], victoryRoute=335)]},
    "273": {"combat": [combat_preset(273, "Drakkarim", combat_enemy("Drakkarim", 18, 35), canEvade=True, evadeRoute=238, victoryRoute=345)]},
    "280": {"combat": [combat_preset(280, "Drakkar", combat_enemy("Drakkar", 18, 25), ignorePlayerLossRounds=1, victoryRoute=213)]},
    "299": {"combat": [combat_preset(299, "Vordak", combat_enemy("Vordak", 17, 25), enemyImmune=True, conditionalModifiers=[{"condition": cond_no_power("Mindshield"), "modifier": -2, "label": "Mindforce attack"}], victoryRoute=203)]},
    "316": {"combat": [combat_preset(316, "Drakkar", combat_enemy("Drakkar", 18, 26), timedModifiers=[{"startRound": 1, "endRound": 3, "modifier": -2}], victoryRoute=333)]},
    "330": {"combat": [combat_preset(330, "Drakkar", combat_enemy("Drakkar", 18, 23), winWithinRounds=2, winWithinRoute=243, tooLateRoute=394, roundLimit=2, roundExceededRoute=394)]},
    "334": {"combat": [combat_preset(334, "Tower Guards", combat_enemy("Tower Guards", 17, 32), canEvade=True, evadeRoute=209, victoryRoute=310)]},
    "353": {"combat": [combat_preset(353, "Darklord Haakon", combat_enemy("Darklord Haakon", 28, 45), conditionalModifiers=[{"condition": cond_no_power("Mindshield"), "modifier": -2, "label": "Mindforce attack"}], victoryRoute=400)]},
    "355": {"combat": [combat_preset(355, "Vordak", combat_enemy("Vordak", 17, 26), enemyImmune=True, conditionalModifiers=[{"condition": cond_no_power("Mindshield"), "modifier": -2, "label": "Mindforce attack"}], winWithinRounds=4, winWithinRoute=249, tooLateRoute=304, roundLimit=4, roundExceededRoute=304)]},
    "357": {"combat": [combat_preset(357, "Platform Sentry", combat_enemy("Platform Sentry", 15, 23), modifier=-2, combatRollRoutes={"1": 293}, victoryChoices=[207, 224])]},
    "361": {"combat": [combat_preset(361, "Drakkar", combat_enemy("Drakkar", 18, 25), winWithinRounds=3, winWithinRoute=288, tooLateRoute=382, roundLimit=3, roundExceededRoute=382)]},
    "370": {"combat": [combat_preset(370, "Itikar", combat_enemy("Itikar", 17, 30), doubleEnemyLoss=True, victoryRoute=217)]},
    "387": {"combat": [combat_preset(387, "Drakkarim", combat_enemy("Drakkarim", 17, 35), canEvade=True, evadeRoute=205, victoryRoute=341)]},
    "389": {"combat": [combat_preset(389, "Sentry", combat_enemy("Sentry", 15, 23), victoryChoices=[207, 224])]},
    "393": {"combat": [combat_preset(393, "Drakkar", combat_enemy("Drakkar", 16, 25), timedModifiers=[{"startRound": 1, "endRound": 1, "modifier": -2}], preActions=[{"type": "stat", "stat": "end", "delta": -2, "condition": cond_no_power("Mindshield")}], canEvade=True, evadeAfterRounds=3, evadeRoute=228, victoryRoute=255)]},
}


def clean_text(source: str) -> str:
    text = re.sub(r"<[^>]+>", " ", source)
    text = html.unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def maintext_block(source: str) -> str:
    match = re.search(r"<div\b[^>]*class=[\"'][^\"']*\bmaintext\b[^\"']*[\"'][^>]*>", source, flags=re.IGNORECASE)
    if not match:
        return source
    end = source.find('<p id="page-navigation"', match.end())
    if end == -1:
        end = source.find("</article>", match.end())
    if end == -1:
        end = len(source)
    return source[match.end():end]


def unique_routes(block: str) -> list[int]:
    routes: list[int] = []
    for match in re.finditer(r"href=[\"'][^\"']*sect(\d+)\.htm", block, flags=re.IGNORECASE):
        route = int(match.group(1))
        if route not in routes:
            routes.append(route)
    return routes


def classify_section(block: str, routes: list[int], section: int) -> list[str]:
    text = clean_text(block).lower()
    classes: list[str] = []
    def add(value: str) -> None:
        if value not in classes:
            classes.append(value)
    if len(routes) > 1:
        add("route_choice")
    elif len(routes) == 1:
        add("single_route")
    if "random number table" in text or "pick a number" in text:
        add("random")
    if "kai discipline" in text:
        add("kai_discipline_check")
    if "combat skill" in text and "endurance" in text and any(term in text for term in ("fight", "combat", "enemy", "creature")):
        add("combat")
    if "meal" in text or "hunting" in text:
        add("meal")
    if "gold crown" in text or "crowns" in text:
        add("gold")
    if any(term in text for term in ("backpack", "special item", "weapon", "action chart", "erase", "mark", "safekeeping")):
        add("inventory")
    if "endurance" in text and any(term in text for term in ("lose", "deduct", "reduce")):
        add("endurance_loss")
    if "endurance" in text and any(term in text for term in ("restore", "regain")):
        add("endurance_gain")
    if "combat skill" in text and any(term in text for term in ("add", "deduct", "reduce")):
        add("combat_skill_modifier")
    if any(
        term in text
        for term in (
            "your life end",
            "your adventure ends",
            "you are dead",
            "your life and the hopes",
            "your life and all hopes",
            "your life and the last hope",
            "your life comes to",
            "boiled to death",
            "oblivion engulfs you",
            "consumed by searing",
        )
    ):
        add("terminal_death")
    if section == MAX_SECTION:
        add("terminal_success")
    if not routes and not any(value.startswith("terminal_") for value in classes):
        add("terminal_unclassified")
    return classes or ["story"]


COMBAT_RE = re.compile(r"([A-Z][A-Za-z' -]+?):\s*COMBAT SKILL\s+(\d+)\s+ENDURANCE\s+(\d+)", re.IGNORECASE)


def infer_combat(section: int, block: str) -> list[dict[str, Any]]:
    text = clean_text(block)
    presets: list[dict[str, Any]] = []
    for match in COMBAT_RE.finditer(text):
        name = re.sub(r"\s+", " ", match.group(1)).strip()
        cs = int(match.group(2))
        endurance = int(match.group(3))
        kwargs: dict[str, Any] = {}
        tail = text[match.end():match.end() + 500]
        win = re.search(r"If you (?:win|successfully reduce).*?turn to (\d+)", tail, re.IGNORECASE)
        lose = re.search(r"If you lose.*?turn to (\d+)", tail, re.IGNORECASE)
        if win:
            kwargs["victoryRoute"] = int(win.group(1))
        if lose:
            kwargs["defeatRoute"] = int(lose.group(1))
        if re.search(r"immune to Mindblast", tail, re.IGNORECASE) or re.search(r"immune to Mindblast", text[max(0, match.start()-300):match.end()+300], re.IGNORECASE):
            kwargs["enemyImmune"] = True
        if re.search(r"cannot evade|impossible to evade|cannot avoid", tail, re.IGNORECASE):
            kwargs["canEvade"] = False
        presets.append(combat_preset(section, name, combat_enemy(name, cs, endurance), **kwargs))
    return presets


def fetch_svg_graph() -> dict[str, Any]:
    result: dict[str, Any] = {"url": SVG_GRAPH_URL, "status": None, "available": False, "nodeCount": 0, "edgeCount": 0, "edges": [], "error": ""}
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
        result.update({"available": True, "nodeCount": len(nodes), "edgeCount": len(edges), "edges": sorted([list(edge) for edge in edges])})
    except Exception as exc:  # pragma: no cover
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
        entry: dict[str, Any] = {
            "auditStatus": "source-link-baseline",
            "classification": classify_section(block, routes, section),
            "sourceRouteCount": len(routes),
            "sourceRoutes": [{"Section": route} for route in routes],
        }
        combat = infer_combat(section, block)
        if combat:
            entry["combat"] = combat
        sections[section] = entry

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
                if "routeChecks" in override and "routeChecks" in sections[int(section)]:
                    sections[int(section)]["routeChecks"] = sections[int(section)]["routeChecks"] + override["routeChecks"]
                    override = {key: value for key, value in override.items() if key != "routeChecks"}
                sections[int(section)].update(override)

    for entry in sections.values():
        entry["sourceRouteCount"] = len(entry.get("sourceRoutes", []))

    incoming = {section: [] for section in expected}
    for section, entry in sections.items():
        for route in entry["sourceRoutes"]:
            target = int(route["Section"])
            if target in incoming:
                incoming[target].append(section)
    for section, entry in sections.items():
        entry["incomingRouteCount"] = len(incoming.get(section, []))

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

    terminal_sections = [section for section, entry in sections.items() if int(entry["sourceRouteCount"]) == 0]
    branch_sections = [section for section, entry in sections.items() if int(entry["sourceRouteCount"]) >= 2]
    counts: dict[str, int] = {}
    for entry in sections.values():
        for value in entry["classification"]:
            counts[value] = counts.get(value, 0) + 1

    local_edges = sorted([section, int(route["Section"])] for section, entry in sections.items() for route in entry["sourceRoutes"])
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
        "generatedBy": "testing/lwbook5_section_flow_audit.py",
        "sectionCount": len(sections),
        "expectedSectionCount": MAX_SECTION,
        "sourceRouteLinkCount": sum(int(entry["sourceRouteCount"]) for entry in sections.values()),
        "branchSectionCount": len(branch_sections),
        "terminalSectionCount": len(terminal_sections),
        "reachableFromSection1Count": len(reachable),
        "invalidSectionLinkCount": len(invalid_links),
        "missingSectionCount": len(sorted(expected - set(sections))),
        "svgRouteGraphAvailable": bool(svg_graph.get("available")),
    }
    data: dict[str, Any] = {str(BOOK_NUMBER): {"_meta": meta}}
    for section in range(1, MAX_SECTION + 1):
        if section in sections:
            data[str(BOOK_NUMBER)][str(section)] = sections[section]
    artifact = {
        "meta": meta,
        "missingSections": sorted(expected - set(sections)),
        "invalidLinks": invalid_links,
        "unreachableFromSection1": sorted(expected - reachable),
        "terminalSections": terminal_sections,
        "branchSections": branch_sections,
        "classificationCounts": dict(sorted(counts.items())),
        "section1Routes": [route["Section"] for route in sections.get(1, {}).get("sourceRoutes", [])],
        "section400Classes": sections.get(400, {}).get("classification", []),
        "routeGraphCheck": graph_check,
        "manualFlowAuditCount": len(MANUAL_FLOW_AUDIT),
        "manualCombatAuditCount": len(MANUAL_COMBAT_AUDIT),
        "manualLootAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "loot" in entry),
        "manualRouteCheckAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "routeChecks" in entry),
        "manualRollAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "roll" in entry),
        "manualLossChoiceAuditCount": sum(1 for entry in MANUAL_FLOW_AUDIT.values() if "lossChoices" in entry),
    }
    return data, artifact


def render_report(artifact: dict[str, Any]) -> str:
    meta = artifact["meta"]
    lines = [
        "# LW Book 5 Section Flow Baseline",
        "",
        "Scope: source-link graph for local Project Aon Book 5 section files.",
        "",
        "This report records section numbers, graph counts, and helper classifications only. It does not reproduce book prose.",
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
        f"- Section 400 classifications: {', '.join(artifact['section400Classes'])}",
        f"- Missing sections: {', '.join(str(item) for item in artifact['missingSections']) if artifact['missingSections'] else 'none'}",
        f"- Invalid links: {json.dumps(artifact['invalidLinks']) if artifact['invalidLinks'] else 'none'}",
        f"- Unreachable sections from section 1: {', '.join(str(item) for item in artifact['unreachableFromSection1']) if artifact['unreachableFromSection1'] else 'none'}",
        "",
        "## Classification Counts",
        "",
    ]
    for key, value in artifact["classificationCounts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend([
        "",
        "## Data Artifact",
        "",
        "- `data/book5-section-flows.json` contains one source-link baseline entry for every discovered section.",
        "- The first helper slice includes safekeeping-aware setup, palace confiscation/restoration, key loot, route checks, random helpers, loss choices, and combat presets.",
        "",
        "## Remaining Risk",
        "",
        "- The local Project Aon HTML remains the source of truth.",
        "- Book 5 is an onboarding helper build until real-route playtesting shakes out button labels, achievements, and optional side-route polish.",
    ])
    return "\n".join(lines) + "\n"


def render_graph_report(graph: dict[str, Any]) -> str:
    lines = [
        "# LW Book 5 Route Graph Check",
        "",
        "Scope: optional Project Aon SVG/SVGZ route graph cross-check.",
        "",
        "The local Project Aon HTML files remain the source of truth. The online SVG graph is used only as a consistency check.",
        "",
        "## Summary",
        "",
        f"- Graph available: {'yes' if graph.get('available') else 'no'}",
        f"- Source URL: {graph.get('url')}",
        f"- HTTP status: {graph.get('status') or 'n/a'}",
        f"- SVG nodes: {graph.get('nodeCount')}",
        f"- SVG edges: {graph.get('edgeCount')}",
        f"- Local nodes: {graph.get('localNodeCount')}",
        f"- Local edges: {graph.get('localEdgeCount')}",
        f"- SVG edges not in local HTML: {len(graph.get('svgEdgesNotLocal') or [])}",
        f"- Local HTML edges not in SVG: {len(graph.get('localEdgesNotSvg') or [])}",
    ]
    if graph.get("error"):
        lines.extend(["", "## Error", "", str(graph["error"])])
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    data, artifact = build_graph()
    expected_json = json.dumps(data, indent=2, sort_keys=True) + "\n"
    report = render_report(artifact)
    graph_report = render_graph_report(artifact["routeGraphCheck"])

    if args.write:
        DATA_PATH.write_text(expected_json, encoding="utf-8")
        REPORT_PATH.write_text(report, encoding="utf-8")
        GRAPH_REPORT_PATH.write_text(graph_report, encoding="utf-8")

    if args.check:
        if not DATA_PATH.exists():
            raise SystemExit(f"Missing {DATA_PATH}")
        current = DATA_PATH.read_text(encoding="utf-8")
        if current != expected_json:
            raise SystemExit(f"{DATA_PATH} is out of date; run this script with --write")

    print(f"Book 5 section flow: {artifact['meta']['sectionCount']} sections, {artifact['meta']['sourceRouteLinkCount']} source links.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

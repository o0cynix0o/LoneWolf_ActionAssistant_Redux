#!/usr/bin/env python3
"""Scan Book 3 sections for automation-likely language."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "books" / "lw" / "03tcok"
FLOW_DATA = ROOT / "data" / "book3-section-flows.json"
SIMPLE_DATA = ROOT / "data" / "book3-simple-automations.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK3_AUTOMATION_LANGUAGE_AUDIT.md"
MAX_SECTION = 350


sys.path.insert(0, str(ROOT / "testing"))
from lwbook3_section_flow_audit import clean_text, maintext_block  # noqa: E402


SIGNALS: dict[str, list[tuple[str, str]]] = {
    "endurance_loss": [
        ("deduct_endurance", r"\bdeduct\b[^.]*\bendurance points?\b|\bendurance points?\b[^.]*\bdeduct\b"),
        ("lose_endurance", r"\blose\b[^.]*\bendurance points?\b|\bendurance points?\b[^.]*\blose\b"),
        ("reduce_endurance", r"\breduce\b[^.]*\bendurance points?\b|\bendurance points?\b[^.]*\breduce\b"),
    ],
    "endurance_gain": [
        ("restore_endurance", r"\brestore\b[^.]*\bendurance\b|\bendurance\b[^.]*\brestore\b"),
        ("regain_endurance", r"\bregain\b[^.]*\bendurance\b|\bendurance\b[^.]*\bregain\b"),
        ("potion_endurance", r"\bpotion\b[^.]*\bendurance\b|\bendurance\b[^.]*\bpotion\b"),
    ],
    "combat_skill_modifier": [
        ("deduct_combat_skill", r"\bdeduct\b[^.]*\bcombat skill\b|\bcombat skill\b[^.]*\bdeduct\b"),
        ("add_combat_skill", r"\badd\b[^.]*\bcombat skill\b|\bcombat skill\b[^.]*\badd\b"),
        ("reduce_combat_skill", r"\breduce\b[^.]*\bcombat skill\b|\bcombat skill\b[^.]*\breduce\b"),
    ],
    "meal": [
        ("meal_required", r"\bmeal\b|\bfood\b|\bhunting\b"),
    ],
    "gold": [
        ("gold_crowns", r"\bgold crowns?\b|\bcrowns?\b"),
    ],
    "gold_cost": [
        ("gold_payment", r"\b(pay|payment|offer|cost|price|bribe|give)\b[^.]*\bgold crowns?\b|\bgold crowns?\b[^.]*\b(pay|payment|offer|cost|price|bribe|give)\b"),
    ],
    "inventory_gain": [
        (
            "may_take_item",
            r"\byou may (take|keep|pick up|add|record|mark)\b[^.]*\b(weapon|sword|dagger|spear|mace|axe|warhammer|quarterstaff|broadsword|bow|potion|meal|gold|crowns?|key|sphere|helm|helmet|map|crystal|jewel|stone|special item|backpack item|item)\b",
        ),
        ("mark_action_chart", r"\b(mark|record)\b[^.]*\baction chart\b"),
        ("backpack_item", r"\bbackpack item\b"),
        ("special_item", r"\bspecial item\b"),
    ],
    "inventory_loss": [
        ("lose_inventory", r"\blose\b[^.]*\b(backpack|weapon|item|equipment|special item|action chart)\b|\b(backpack|weapon|item|equipment|special item|action chart)\b[^.]*\blose\b"),
        ("destroy_inventory", r"\bdestroy(?:ed)?\b[^.]*\b(backpack|weapon|item|equipment|special item)\b|\b(backpack|weapon|item|equipment|special item)\b[^.]*\bdestroy(?:ed)?\b"),
        ("erase_inventory", r"\berase\b[^.]*\b(weapon|backpack|item|special item|action chart)\b"),
        ("discard_inventory", r"\bdiscard\b[^.]*\b(weapon|backpack|item|special item|action chart)\b"),
        ("exchange_weapon", r"\bexchange\b[^.]*\bweapon\b|\bweapon\b[^.]*\bexchange\b"),
    ],
    "random": [
        ("random_number_table", r"\brandom number table\b"),
        ("pick_a_number", r"\bpick a number\b"),
    ],
    "route_check": [
        ("if_possess", r"\bif you (possess|carry)\b|\bif you have (?!picked|chosen|a number|more than|no |no longer)\b"),
        ("if_not_possess", r"\bif you do not (possess|have|carry)\b"),
        ("kai_discipline", r"\bkai discipline\b"),
    ],
    "combat": [
        ("combat_stats", r"\bcombat skill\b[^.]*\bendurance\b|\bendurance\b[^.]*\bcombat skill\b"),
        ("must_fight", r"\bmust fight\b|\bfight (?:them|it|him|her)\b|\benemy\b"),
    ],
    "terminal": [
        ("adventure_ends", r"\badventure ends\b"),
        ("mission_failed", r"\bmission has failed\b"),
        ("you_are_dead", r"\byou are dead\b"),
    ],
    "book_transition": [
        ("next_adventure", r"\bnext adventure\b|\bbook 4\b|\bfuture adventures\b"),
    ],
}


DIRECT_COVERAGE = {
    "endurance_loss": {"simple", "roll", "routeAction"},
    "endurance_gain": {"simple", "loot", "roll", "routeAction"},
    "combat_skill_modifier": {"simple", "combat", "routeAction"},
    "meal": {"simple", "loot", "routeAction"},
    "gold": {"simple", "loot", "routeCheck", "routeAction"},
    "gold_cost": {"routeAction"},
    "inventory_gain": {"simple", "loot", "lossChoice", "routeAction"},
    "inventory_loss": {"simple", "lossChoice", "roll", "routeAction"},
    "random": {"roll", "stagedRoll"},
    "route_check": {"routeCheck"},
    "combat": {"combat"},
    "terminal": {"simple", "stagedRoll", "routeAction"},
    "book_transition": {"simple", "routeAction"},
}


REVIEWED_NO_AUTOMATION: dict[str, set[str]] = {
    "1": {"meal"},
    "5": {"meal"},
    "8": {"meal"},
    "23": {"meal"},
    "41": {"inventory_loss"},
    "52": {"combat"},
    "61": {"meal"},
    "101": {"meal"},
    "112": {"meal"},
    "117": {"meal"},
    "122": {"route_check"},
    "124": {"route_check"},
    "149": {"meal"},
    "167": {"meal"},
    "181": {"gold"},
    "202": {"combat"},
    "207": {"combat"},
    "212": {"meal"},
    "305": {"meal"},
    "318": {"meal"},
    "347": {"meal"},
    "348": {"route_check"},
    "350": {"combat"},
}


REVIEWED_COVERED: dict[str, set[str]] = {
    "29": {"route_check"},
    "32": {"endurance_loss", "route_check"},
    "54": {"route_check"},
    "83": {"endurance_loss", "route_check"},
    "88": {"endurance_loss"},
    "94": {"endurance_loss"},
    "99": {"endurance_loss", "route_check"},
    "123": {"endurance_loss"},
    "132": {"route_check"},
    "137": {"combat_skill_modifier", "route_check"},
    "138": {"endurance_loss"},
    "142": {"combat"},
    "146": {"route_check"},
    "149": {"route_check"},
    "155": {"endurance_loss", "meal"},
    "158": {"endurance_loss"},
    "180": {"endurance_loss"},
    "183": {"meal", "route_check"},
    "185": {"route_check"},
    "211": {"endurance_loss"},
    "232": {"meal"},
    "241": {"endurance_loss"},
    "258": {"endurance_loss", "meal", "route_check", "combat"},
    "259": {"endurance_loss"},
    "260": {"endurance_loss"},
    "263": {"endurance_loss"},
    "262": {"route_check"},
    "272": {"route_check"},
    "283": {"meal", "route_check"},
    "284": {"endurance_loss", "meal", "route_check"},
    "302": {"route_check"},
    "304": {"endurance_loss", "route_check"},
    "323": {"meal", "route_check"},
    "327": {"terminal"},
    "331": {"endurance_loss", "meal", "route_check"},
    "346": {"meal", "route_check"},
}


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def section_text(section: int) -> str:
    source = (BOOK_DIR / f"sect{section}.htm").read_text(encoding="utf-8", errors="ignore")
    return clean_text(maintext_block(source)).lower()


def signal_labels(text: str) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for category, patterns in SIGNALS.items():
        labels = []
        for label, pattern in patterns:
            if re.search(pattern, text, flags=re.IGNORECASE):
                labels.append(label)
        if labels:
            result[category] = labels
    return result


def build_audit() -> dict[str, Any]:
    flow_data = load_json(FLOW_DATA).get("3", {})
    simple_data = load_json(SIMPLE_DATA).get("3", {})
    sections: dict[str, Any] = {}
    signals_by_category: dict[str, list[int]] = defaultdict(list)
    gaps: dict[str, list[int]] = defaultdict(list)
    covered: dict[str, list[int]] = defaultdict(list)
    no_signal_sections: list[int] = []

    for section in range(1, MAX_SECTION + 1):
        signals = signal_labels(section_text(section))
        if not signals:
            no_signal_sections.append(section)
            continue
        entry = flow_data.get(str(section), {})
        simple_entry = simple_data.get(str(section))
        coverage = flow_coverage(entry, simple_entry)
        status: dict[str, str] = {}
        for category in signals:
            signals_by_category[category].append(section)
            if category in REVIEWED_NO_AUTOMATION.get(str(section), set()):
                status[category] = "reviewed-no-automation"
            elif category in REVIEWED_COVERED.get(str(section), set()):
                status[category] = "reviewed-covered"
                covered[category].append(section)
            elif category_covered(category, coverage):
                status[category] = "covered"
                covered[category].append(section)
            else:
                status[category] = "needs-review"
                gaps[category].append(section)
        sections[str(section)] = {
            "signals": signals,
            "classification": entry.get("classification", []),
            "sourceRouteCount": entry.get("sourceRouteCount", 0),
            "coverage": sorted(coverage),
            "status": status,
        }

    return {
        "sectionsScanned": MAX_SECTION,
        "sectionsWithSignals": len(sections),
        "sections": sections,
        "signalsByCategory": dict(sorted(signals_by_category.items())),
        "gaps": {key: values for key, values in sorted(gaps.items())},
        "covered": {key: values for key, values in sorted(covered.items())},
        "noSignalSections": no_signal_sections,
    }


def flow_coverage(entry: dict[str, Any], simple_entry: dict[str, Any] | None) -> set[str]:
    coverage: set[str] = set()
    if simple_entry:
        coverage.add("simple")
    if entry.get("loot"):
        coverage.add("loot")
    if entry.get("lossChoices"):
        coverage.add("lossChoice")
    if entry.get("roll"):
        coverage.add("roll")
    if entry.get("stagedRoll"):
        coverage.add("stagedRoll")
    if entry.get("routeChecks"):
        coverage.add("routeCheck")
    if entry.get("combat"):
        coverage.add("combat")
    for route in entry.get("sourceRoutes", []):
        if isinstance(route, dict) and (route.get("actions") or route.get("Actions")):
            coverage.add("routeAction")
    return coverage


def category_covered(category: str, coverage: set[str]) -> bool:
    return bool(DIRECT_COVERAGE.get(category, set()) & coverage)


def list_line(values: list[int]) -> str:
    return ", ".join(str(value) for value in values) if values else "none"


def render_report(audit: dict[str, Any]) -> str:
    gaps = audit["gaps"]
    lines = [
        "# LW Book 3 Automation Language Audit",
        "",
        "Scope: Book 3 section-by-section scan for automation-likely language.",
        "",
        "This report records signal labels and section numbers only. It intentionally does not copy Book 3 prose.",
        "",
        "## Summary",
        "",
        f"- Sections scanned: {audit['sectionsScanned']}",
        f"- Sections with at least one automation signal: {audit['sectionsWithSignals']}",
        f"- Signal categories with uncovered candidates: {len(gaps)}",
        "",
        "## Signal Categories",
        "",
    ]
    for category, sections in audit["signalsByCategory"].items():
        lines.append(f"- {category}: {len(sections)} sections")
    lines.extend(["", "## Sections By Category", ""])
    for category, sections in audit["signalsByCategory"].items():
        lines.append(f"- {category}: {list_line(sections)}")
    lines.extend(
        [
            "",
            "## Needs Review By Category",
            "",
        ]
    )
    for category in sorted(SIGNALS):
        lines.append(f"- {category}: {list_line(gaps.get(category, []))}")
    lines.extend(
        [
            "",
            "## Reviewed No Automation",
            "",
        ]
    )
    if REVIEWED_NO_AUTOMATION:
        for section in sorted(REVIEWED_NO_AUTOMATION, key=lambda value: int(value)):
            categories = ", ".join(sorted(REVIEWED_NO_AUTOMATION[section]))
            lines.append(f"- Section {section}: {categories}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Reviewed Covered",
            "",
        ]
    )
    if REVIEWED_COVERED:
        for section in sorted(REVIEWED_COVERED, key=lambda value: int(value)):
            categories = ", ".join(sorted(REVIEWED_COVERED[section]))
            lines.append(f"- Section {section}: {categories}")
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            "## Section-By-Section Checklist",
            "",
        ]
    )
    for section in range(1, MAX_SECTION + 1):
        entry = audit["sections"].get(str(section))
        if not entry:
            lines.append(f"- Section {section}: no automation-language signal")
            continue
        statuses = ", ".join(
            f"{category}={status}" for category, status in sorted(entry["status"].items())
        )
        coverage = ", ".join(entry.get("coverage", [])) or "none"
        lines.append(f"- Section {section}: {statuses}; coverage={coverage}")
    lines.extend(
        [
            "",
            "## Review Status",
            "",
            "- `covered` means the section already has a helper matching the signal category.",
            "- `reviewed-covered` means a nearby helper or route outcome already handles the signal.",
            "- `reviewed-no-automation` means the signal is story prose or a route already visible in the book text.",
            "- `needs-review` means the section needs manual audit and likely needs a helper, action, or explicit no-automation ruling.",
            "",
            "## Data Artifact",
            "",
            "- Source route shape is in `data/book3-section-flows.json`.",
            "- Entry effects live in `data/book3-simple-automations.json`.",
            "- This audit is a coverage report only; playable behavior is defined by the data artifacts above.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write report artifact")
    parser.add_argument("--check", action="store_true", help="check existing report")
    args = parser.parse_args()

    audit = build_audit()
    report_text = render_report(audit)

    if args.write:
        REPORT_PATH.write_text(report_text, encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")
        return 0

    if args.check:
        if not REPORT_PATH.exists():
            print(f"Missing {REPORT_PATH}")
            return 1
        if REPORT_PATH.read_text(encoding="utf-8") != report_text:
            print(f"Out of date: {REPORT_PATH}")
            return 1
        print("Book 3 automation-language audit check passed.")
        return 0

    print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

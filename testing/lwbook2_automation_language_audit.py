#!/usr/bin/env python3
"""Scan Book 2 sections for automation-likely language."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "books" / "lw" / "02fotw"
FLOW_DATA = ROOT / "data" / "book2-section-flows.json"
SIMPLE_DATA = ROOT / "data" / "book2-simple-automations.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK2_AUTOMATION_LANGUAGE_AUDIT.md"
MAX_SECTION = 350


sys.path.insert(0, str(ROOT / "testing"))
from lwbook2_section_flow_audit import clean_text, maintext_block  # noqa: E402


SIGNALS: dict[str, list[tuple[str, str]]] = {
    "endurance_loss": [
        ("deduct_endurance", r"\bdeduct\b[^.]*\bendurance points?\b|\bendurance points?\b[^.]*\bdeduct\b"),
        ("lose_endurance", r"\blose\b[^.]*\bendurance points?\b|\bendurance points?\b[^.]*\blose\b"),
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
        ("meal_required", r"\bmeal\b|\bfood\b"),
    ],
    "gold": [
        ("gold_crowns", r"\bgold crowns?\b|\bcrowns?\b"),
    ],
    "gold_cost": [
        ("gold_fee", r"\bfee\b[^.]*\bgold crowns?\b|\bgold crowns?\b[^.]*\bfee\b"),
        ("gold_payment", r"\b(pay|payment|offer|cost|price|give)\b[^.]*\bgold crowns?\b|\bgold crowns?\b[^.]*\b(pay|payment|offer|cost|price|give)\b"),
    ],
    "inventory_gain": [
        (
            "may_take_item",
            r"\byou may (take|keep|pick up|add|record)\b[^.]*\b(weapon|sword|scroll|message|dagger|spear|gem|key|potion|meal|gold|crowns?|torch|warhammer|mace|quarterstaff|tinderbox|pendant|pass|papers|token|shield|special item|backpack item|item)\b",
        ),
        ("mark_action_chart", r"\b(mark|record)\b[^.]*\baction chart\b"),
        ("backpack_item", r"\bbackpack item\b"),
        ("special_item", r"\bspecial item\b"),
    ],
    "inventory_loss": [
        ("lose_inventory", r"\blose\b[^.]*\b(backpack|weapon|item|equipment|special item|action chart)\b|\b(backpack|weapon|item|equipment|special item|action chart)\b[^.]*\blose\b"),
        ("lost_inventory", r"\blost\b[^.]*\b(backpack|weapon|item|equipment|special item|action chart)\b|\b(backpack|weapon|item|equipment|special item|action chart)\b[^.]*\blost\b"),
        ("stolen_inventory", r"\bstolen\b[^.]*\b(backpack|weapon|item|equipment|special item)\b|\b(backpack|weapon|item|equipment|special item)\b[^.]*\bstolen\b"),
        ("erase_inventory", r"\berase\b[^.]*\b(weapon|backpack|item|special item|action chart)\b"),
        ("cross_off_inventory", r"\bcross\b[^.]*\boff\b[^.]*\b(weapon|backpack|item|special item|action chart)\b"),
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
    "terminal": [
        ("adventure_ends", r"\badventure ends\b"),
        ("mission_failed", r"\bmission has failed\b"),
        ("you_are_dead", r"\byou are dead\b"),
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
    "terminal": {"simple", "stagedRoll", "routeAction"},
}


REVIEWED_NO_AUTOMATION: dict[str, set[str]] = {
    "4": {"gold"},
    "14": {"route_check"},
    "36": {"meal"},
    "45": {"gold"},
    "50": {"gold"},
    "53": {"meal"},
    "64": {"meal"},
    "79": {"route_check"},
    "93": {"gold"},
    "97": {"route_check"},
    "101": {"meal"},
    "130": {"gold"},
    "178": {"meal"},
    "203": {"route_check"},
    "204": {"route_check"},
    "222": {"meal"},
    "236": {"meal"},
    "238": {"random", "route_check"},
    "264": {"meal"},
    "276": {"gold_cost"},
    "290": {"meal"},
    "308": {"gold", "random"},
}
REVIEWED_COVERED: dict[str, set[str]] = {
    "12": {"gold", "route_check"},
    "30": {"endurance_loss"},
    "39": {"gold_cost"},
    "57": {"gold"},
    "60": {"endurance_loss"},
    "69": {"route_check"},
    "79": {"combat_skill_modifier"},
    "103": {"route_check"},
    "106": {"route_check"},
    "110": {"route_check"},
    "116": {"gold", "route_check"},
    "128": {"endurance_loss"},
    "150": {"route_check"},
    "157": {"route_check"},
    "165": {"route_check"},
    "199": {"gold"},
    "231": {"route_check"},
    "240": {"route_check"},
    "242": {"combat_skill_modifier", "route_check"},
    "266": {"gold_cost", "route_check"},
    "276": {"endurance_gain"},
    "283": {"route_check"},
    "287": {"route_check"},
    "306": {"endurance_loss"},
    "327": {"gold_cost"},
    "332": {"endurance_loss", "route_check"},
    "337": {"route_check"},
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
    for route in entry.get("sourceRoutes", []):
        if isinstance(route, dict) and route.get("actions"):
            coverage.add("routeAction")
    if entry.get("combat"):
        coverage.add("combat")
    return coverage


def category_covered(category: str, coverage: set[str]) -> bool:
    return bool(DIRECT_COVERAGE.get(category, set()) & coverage)


def build_audit() -> dict[str, Any]:
    flow_data = load_json(FLOW_DATA).get("2", {})
    simple_data = load_json(SIMPLE_DATA).get("2", {})
    sections: dict[str, Any] = {}
    gaps: dict[str, list[int]] = defaultdict(list)
    covered: dict[str, list[int]] = defaultdict(list)

    for section in range(1, MAX_SECTION + 1):
        text = section_text(section)
        signals = signal_labels(text)
        entry = flow_data.get(str(section), {})
        simple_entry = simple_data.get(str(section))
        coverage = flow_coverage(entry, simple_entry)
        category_status: dict[str, str] = {}
        for category in signals:
            if category in REVIEWED_NO_AUTOMATION.get(str(section), set()):
                category_status[category] = "reviewed-no-automation"
            elif category in REVIEWED_COVERED.get(str(section), set()):
                category_status[category] = "reviewed-covered"
                covered[category].append(section)
            elif category_covered(category, coverage):
                category_status[category] = "covered"
                covered[category].append(section)
            else:
                category_status[category] = "needs-review"
                gaps[category].append(section)
        if signals:
            sections[str(section)] = {
                "signals": signals,
                "coverage": sorted(coverage),
                "status": category_status,
            }

    return {
        "sectionsScanned": MAX_SECTION,
        "sectionsWithSignals": len(sections),
        "sections": sections,
        "gaps": {key: values for key, values in sorted(gaps.items())},
        "covered": {key: values for key, values in sorted(covered.items())},
    }


def list_line(values: list[int]) -> str:
    return ", ".join(str(value) for value in values) if values else "none"


def render_report(audit: dict[str, Any]) -> str:
    gaps = audit["gaps"]
    lines = [
        "# LW Book 2 Automation Language Audit",
        "",
        "Date: 2026-05-27",
        "",
        "Scope: Book 2 section-by-section scan for automation-likely language.",
        "",
        "This report records signal labels and section numbers only. It intentionally does not copy Book 2 prose.",
        "",
        "## Summary",
        "",
        f"- Sections scanned: {audit['sectionsScanned']}",
        f"- Sections with automation-language signals: {audit['sectionsWithSignals']}",
        f"- Signal categories with uncovered candidates: {len(gaps)}",
        "",
        "## Needs Review By Category",
        "",
    ]
    for category in sorted(SIGNALS):
        lines.append(f"- {category}: {list_line(gaps.get(category, []))}")
    lines.extend(["", "## Reviewed No Automation", ""])
    if REVIEWED_NO_AUTOMATION:
        for section in sorted(REVIEWED_NO_AUTOMATION, key=lambda value: int(value)):
            categories = ", ".join(sorted(REVIEWED_NO_AUTOMATION[section]))
            lines.append(f"- Section {section}: {categories}")
    else:
        lines.append("- none yet")
    lines.extend(["", "## Reviewed Covered", ""])
    if REVIEWED_COVERED:
        for section in sorted(REVIEWED_COVERED, key=lambda value: int(value)):
            categories = ", ".join(sorted(REVIEWED_COVERED[section]))
            lines.append(f"- Section {section}: {categories}")
    else:
        lines.append("- none yet")
    lines.extend(["", "## Next Review Slice", ""])
    priority_categories = [
        "endurance_loss",
        "endurance_gain",
        "combat_skill_modifier",
        "inventory_loss",
        "inventory_gain",
        "meal",
        "gold_cost",
        "gold",
        "random",
        "route_check",
        "terminal",
    ]
    for category in priority_categories:
        candidates = gaps.get(category, [])
        if candidates:
            lines.append(f"- {category}: review sections {list_line(candidates[:30])}")
    if not any(gaps.get(category, []) for category in priority_categories):
        lines.append("- none")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the markdown report.")
    parser.add_argument("--json", action="store_true", help="Print full audit JSON.")
    args = parser.parse_args()

    audit = build_audit()
    if args.write:
        REPORT_PATH.write_text(render_report(audit), encoding="utf-8")
        print(f"Wrote {REPORT_PATH}")
    elif args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print(render_report(audit))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

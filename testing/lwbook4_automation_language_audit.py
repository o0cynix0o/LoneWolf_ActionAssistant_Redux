#!/usr/bin/env python3
"""Scan Book 4 sections for automation-likely language."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BOOK_DIR = ROOT / "books" / "lw" / "04tcod"
FLOW_DATA = ROOT / "data" / "book4-section-flows.json"
REPORT_PATH = ROOT / "testing" / "logs" / "LWBOOK4_AUTOMATION_LANGUAGE_AUDIT.md"
MAX_SECTION = 350


sys.path.insert(0, str(ROOT / "testing"))
from lwbook4_section_flow_audit import clean_text, maintext_block  # noqa: E402


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
        ("gold_payment", r"\b(pay|payment|offer|cost|price|bribe|give|stake|bet)\b[^.]*\bgold crowns?\b|\bgold crowns?\b[^.]*\b(pay|payment|offer|cost|price|bribe|give|stake|bet)\b"),
    ],
    "inventory_gain": [
        (
            "may_take_item",
            r"\byou may (take|keep|pick up|add|record|mark)\b[^.]*\b(weapon|sword|dagger|spear|mace|axe|warhammer|quarterstaff|broadsword|bow|potion|meal|gold|crowns?|key|stone|jewel|gem|scroll|flask|torch|rope|shield|chainmail|badge|map|special item|backpack item|item)\b",
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
        ("rank_check", r"\bkai rank\b|\bguardian\b|\bwarmarn\b|\bjourneyman\b|\bsavant\b|\bmaster\b"),
    ],
    "combat": [
        ("combat_stats", r"\bcombat skill\b[^.]*\bendurance\b|\bendurance\b[^.]*\bcombat skill\b"),
        ("must_fight", r"\bmust fight\b|\bfight (?:them|it|him|her)\b|\benemy\b"),
        ("immune_mindblast", r"\bimmune to mindblast\b|\bmindblast\b[^.]*\bimmune\b"),
    ],
    "terminal": [
        ("adventure_ends", r"\badventure ends\b"),
        ("mission_failed", r"\bmission has failed\b"),
        ("you_are_dead", r"\byou are dead\b"),
        ("life_mission_end", r"\byour life and your mission end\b|\byour mission and your life end\b"),
    ],
    "book_transition": [
        ("next_adventure", r"\bnext adventure\b|\bbook 5\b|\bfuture adventures\b"),
    ],
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
    flow_data = load_json(FLOW_DATA).get("4", {})
    sections: dict[str, Any] = {}
    signals_by_category: dict[str, list[int]] = defaultdict(list)

    for section in range(1, MAX_SECTION + 1):
        signals = signal_labels(section_text(section))
        if not signals:
            continue
        entry = flow_data.get(str(section), {})
        for category in signals:
            signals_by_category[category].append(section)
        sections[str(section)] = {
            "signals": signals,
            "classification": entry.get("classification", []),
            "sourceRouteCount": entry.get("sourceRouteCount", 0),
            "status": {category: "needs-ledger-review" for category in signals},
        }

    return {
        "sectionsScanned": MAX_SECTION,
        "sectionsWithSignals": len(sections),
        "sections": sections,
        "signalsByCategory": dict(sorted(signals_by_category.items())),
    }


def list_line(values: list[int]) -> str:
    return ", ".join(str(value) for value in values) if values else "none"


def render_report(audit: dict[str, Any]) -> str:
    lines = [
        "# LW Book 4 Automation Language Audit",
        "",
        "Scope: Book 4 section-by-section scan for automation-likely language.",
        "",
        "This report records signal labels and section numbers only. It intentionally does not copy Book 4 prose.",
        "",
        "## Summary",
        "",
        f"- Sections scanned: {audit['sectionsScanned']}",
        f"- Sections with at least one automation signal: {audit['sectionsWithSignals']}",
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
            "## Review Status",
            "",
            "- The first Book 4 implementation slice has converted the confirmed setup rules, route checks, random helpers, loss-choice helpers, simple effects, loot buttons, and combat presets into app data.",
            "- Remaining signals should be reviewed during real-route play and converted into implemented automation, manual helper, reviewed no automation, or queued ambiguity.",
            "",
            "## Data Artifact",
            "",
            "- Source route shape is in `data/book4-section-flows.json`.",
            "- This audit is a planning report only; it does not define playable section behavior.",
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
        print("Book 4 automation-language audit check passed.")
        return 0

    print(report_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

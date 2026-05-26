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
            "",
            "## Remaining Work",
            "",
            "- Confirm route checks that depend on Kai Disciplines, items, END, Gold Crowns, or random digits.",
            "- Add simple automations only after each section effect is confirmed by the audit.",
            "- Audit combat sections for enemy stats, evasion rules, Mindblast immunity, and victory routes.",
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

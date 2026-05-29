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
    if any(term in text for term in ("you are dead", "your adventure ends", "mission has failed")):
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
            "- Combat presets, route checks, random helpers, loot, automations, achievements, and lifecycle support are not implemented yet.",
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

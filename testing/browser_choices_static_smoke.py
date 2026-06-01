#!/usr/bin/env python3
"""Static checks for browser Choices-card grouping."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSISTANT_HTML = ROOT / "assistant.html"


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> int:
    source = ASSISTANT_HTML.read_text(encoding="utf-8")

    assert_true(
        "choiceGroup('Route Effects'" not in source,
        "Choices card must not render a Route Effects group.",
    )
    assert_true(
        "sectionRouteEffectRows" not in source,
        "Route-effect rows should not be wired into the Choices card.",
    )
    assert_true(
        "choiceGroup('Available Checked Routes'" not in source,
        "Choices card must not render checked-route helpers.",
    )
    assert_true(
        "choiceGroup('Loot And Section Items'" in source,
        "Choices card should still show optional loot and section item helpers.",
    )
    assert_true(
        "sectionRouteCheckChoiceRows" not in source,
        "Checked-route rows should not be wired into the Choices card.",
    )
    assert_true(
        "arr(flow.RouteChecks).forEach" in source,
        "Route checks should remain available in the section status receipt.",
    )
    assert_true(
        "choiceGroup('Cartwheel'" in source,
        "Choices card should render the Cartwheel mini-game group when available.",
    )
    assert_true(
        "data-cartwheel-play" in source,
        "Cartwheel mini-game should have a play action button.",
    )
    assert_true(
        "action: 'cartwheel'" in source,
        "Cartwheel mini-game should call the cartwheel action endpoint.",
    )
    assert_true(
        "activeView = 'combat';\n        await action({ action: 'section_combat_start'" in source,
        "Section combat Start should switch directly to the Combat tab after starting the preset.",
    )
    assert_true(
        "activeView = 'combat';\n        manualSectionAdvice('combat presets'" in source,
        "Manual Mode section combat advice should also switch to the Combat tab.",
    )

    print("Browser Choices static smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

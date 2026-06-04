#!/usr/bin/env python3
"""Static checks for shared appearance settings and save-slot UI."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ASSISTANT_HTML = ROOT / "assistant.html"
INDEX_HTML = ROOT / "index.html"
LIBRARY_HTML = ROOT / "library.html"
INSTALL_HTML = ROOT / "install-books.html"
SETTINGS_JS = ROOT / "assets" / "js" / "lw-settings.js"
EARLY_APPEARANCE_JS = ROOT / "assets" / "js" / "lw-appearance-early.js"
APP_SERVER = ROOT / "app_server.py"


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> int:
    assistant = ASSISTANT_HTML.read_text(encoding="utf-8")
    index = INDEX_HTML.read_text(encoding="utf-8")
    library = LIBRARY_HTML.read_text(encoding="utf-8")
    install = INSTALL_HTML.read_text(encoding="utf-8")
    settings = SETTINGS_JS.read_text(encoding="utf-8")
    early = EARLY_APPEARANCE_JS.read_text(encoding="utf-8")
    server = APP_SERVER.read_text(encoding="utf-8")

    for source_name, source in (
        ("assistant.html", assistant),
        ("index.html", index),
        ("library.html", library),
        ("install-books.html", install),
    ):
        assert_true(
            'assets/js/lw-settings.js' in source,
            f"{source_name} should load the shared settings script.",
        )
        assert_true(
            'assets/js/lw-appearance-early.js' in source,
            f"{source_name} should load saved appearance before first paint.",
        )

    for key in (
        "titleBanner",
        "coverArt",
        "theme",
        "readerStyleEnabled",
        "readerTheme",
        "appearanceStorageKeys",
    ):
        assert_true(key in settings, f"lw-settings.js should define {key}.")

    for source_name, source in (
        ("lw-settings.js", settings),
        ("lw-appearance-early.js", early),
    ):
        assert_true("titleBanner: 'title1'" in source, f"{source_name} should default to the classic title banner.")
        assert_true("theme: 'kai-gold'" in source, f"{source_name} should default to classic Kai gold colors.")
        assert_true("coverArt: 'on'" in source, f"{source_name} should show cover art by default.")
        assert_true("readerStyleEnabled: 'off'" in source, f"{source_name} should keep Project Aon reader styling by default.")

    assert_true("Classic Kai Gold" in settings, "default theme should be labeled as the classic first-start look.")
    assert_true(
        ".settings-option.active strong," in settings
        and ".settings-option.active small" in settings
        and "color: var(--lw-bg)" in settings,
        "selected settings cards should keep label and note text readable on the highlight background.",
    )
    assert_true(
        "window.LoneWolfReduxEarlyAppearance" in early and "applyRoot()" in early,
        "early appearance loader should expose and apply first-paint defaults.",
    )

    for theme in (
        "kai-gold",
        "sommerswerd-dawn",
        "durenor-sea",
        "kalte-frost",
        "vassagonian-ruby",
        "wildlands-road",
        "darklord-iron",
    ):
        assert_true(theme in settings, f"lw-settings.js should define the {theme} theme.")

    assert_true("injectReaderTheme" in settings, "shared settings should support reader iframe styling.")
    assert_true("readerBookCss" in settings, "shared settings should use a full reader-page theme helper.")
    for reader_selector in (
        "article,",
        ".maintext,",
        ".frontmatter,",
        ".numbered,",
        ".maintext .combat-results-table th",
        "#license p",
    ):
        assert_true(reader_selector in settings, f"reader themes should style {reader_selector}.")
    assert_true("data-lw-title-banner" in index, "home page should expose the swappable title banner.")
    assert_true("settingsModal" in index, "home page should include the settings modal.")
    assert_true("Kai Series" in index, "home page should label the Kai Series row.")
    assert_true("Magnakai Series" in index, "home page should label the Magnakai Series row.")
    assert_true("reader-panel" in index, "home page Reader tools should live in a dedicated left column.")
    assert_true("grid-template-columns: clamp(260px, 16vw, 340px) minmax(0, 1fr)" in index, "home page should reserve a left column for Reader tools.")
    assert_true("container.style.setProperty('--book-count', seriesBooks.length)" in index, "home page book rows should stay book-only grids.")
    assert_true("const magnakaiBooks" in index, "home page should define Magnakai preview cards.")
    assert_true("The Kingdoms of Terror" in index and "The Masters of Darkness" in index, "home page should preview Books 6-12.")
    assert_true("Coming Soon" in index and "aria-disabled" in index, "Magnakai preview cards should be disabled coming-soon cards.")
    assert_true("clamp(280px, 24vw, 620px)" in index, "home page logo should scale with the viewport.")
    assert_true("footer: '&nbsp;&nbsp;'" in index, "Kai cards should carry a blank footer spacer.")
    assert_true("grid-template-rows: auto auto auto auto" in index, "book cover rows should not stretch from short titles.")
    assert_true("min-height: 2.35em" in index, "book titles should reserve consistent row height.")
    assert_true("border: 1px solid #050807" in index, "home cover art should use only a dark inner outline.")
    assert_true("border-top: 1px solid var(--lw-border" not in index, "home card footers should not draw a divider over cover art.")
    assert_true("border-color: #050807 !important" in settings and "border-color: #050807 !important" in early, "shared themes should preserve the dark cover outline.")
    assert_true(
        "${book.status}" not in index and "Requires local Project Aon book files.</span>" not in index,
        "home book cards should not show internal build/status footer text.",
    )
    assert_true("renderAppearanceSettings" in assistant, "assistant settings should include appearance controls.")
    assert_true("renderSaveSlotRows" in assistant, "assistant should render save slot rows.")
    assert_true("data-slot-save" in assistant, "assistant should support saving to a slot.")
    assert_true("data-slot-load" in assistant, "assistant should support loading from a slot.")
    assert_true("data-slot-clear" in assistant, "assistant should support clearing a slot.")
    assert_true(
        ".quick-panel .dashboard-card > .card-collapse-button" in assistant
        and ".tabs.dashboard-card > .card-collapse-button" in assistant
        and "place-items: center" in assistant,
        "quick/top/tab card controls should use the shared centered round icon button style.",
    )
    assert_true(
        ".top-dashboard .dashboard-card::before" not in assistant
        and "padding-top: 2.05rem" not in assistant,
        "quick/top cards should not use the old floating control chip layout.",
    )
    assert_true("/api/save-slots" in index, "home settings should read save slots from the API.")
    assert_true("SAVE_SLOT_COUNT = 6" in server, "server should define six save slots.")
    assert_true('if action == "save_slot"' in server, "server should support save_slot actions.")
    assert_true('if action == "load_slot"' in server, "server should support load_slot actions.")
    assert_true('if action == "clear_slot"' in server, "server should support clear_slot actions.")

    print("Browser settings static smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

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

    for key in (
        "titleBanner",
        "coverArt",
        "theme",
        "readerStyleEnabled",
        "readerTheme",
        "appearanceStorageKeys",
    ):
        assert_true(key in settings, f"lw-settings.js should define {key}.")

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
    assert_true("data-lw-title-banner" in index, "home page should expose the swappable title banner.")
    assert_true("settingsModal" in index, "home page should include the settings modal.")
    assert_true("renderAppearanceSettings" in assistant, "assistant settings should include appearance controls.")
    assert_true("renderSaveSlotRows" in assistant, "assistant should render save slot rows.")
    assert_true("data-slot-save" in assistant, "assistant should support saving to a slot.")
    assert_true("data-slot-load" in assistant, "assistant should support loading from a slot.")
    assert_true("data-slot-clear" in assistant, "assistant should support clearing a slot.")
    assert_true("/api/save-slots" in index, "home settings should read save slots from the API.")
    assert_true("SAVE_SLOT_COUNT = 6" in server, "server should define six save slots.")
    assert_true('if action == "save_slot"' in server, "server should support save_slot actions.")
    assert_true('if action == "load_slot"' in server, "server should support load_slot actions.")
    assert_true('if action == "clear_slot"' in server, "server should support clear_slot actions.")

    print("Browser settings static smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

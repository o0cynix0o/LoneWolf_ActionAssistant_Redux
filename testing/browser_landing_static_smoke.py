#!/usr/bin/env python3
"""Static checks for landing and library book listings."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"
LIBRARY_HTML = ROOT / "library.html"
COVER_DIR = ROOT / "assets" / "images" / "book-covers"


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> int:
    index_source = INDEX_HTML.read_text(encoding="utf-8")
    library_source = LIBRARY_HTML.read_text(encoding="utf-8")

    for source_name, source in (("index.html", index_source), ("library.html", library_source)):
        assert_true("Flight from the Dark" in source, f"{source_name} should list Book 1.")
        assert_true("Fire on the Water" in source, f"{source_name} should list Book 2.")
        assert_true("The Caverns of Kalte" in source, f"{source_name} should list Book 3.")

    assert_true("'assets/images/book-covers'" in index_source, "index.html should use the local cover art folder.")
    for number in (1, 2, 3):
        assert_true(f"lw{number:02}.jpg" in index_source, f"index.html should show local Book {number} cover art.")
        assert_true(
            f"assets/images/book-covers/lw{number:02}.jpg" in library_source,
            f"library.html should show local Book {number} cover art.",
        )

    for number in range(1, 30):
        assert_true((COVER_DIR / f"lw{number:02}.jpg").exists(), f"local cover art should exist for Book {number}.")

    assert_true("number: 1" in index_source, "index.html should include Book 1 in its card data.")
    assert_true("number: 2" in index_source, "index.html should include Book 2 in its card data.")
    assert_true("number: 3" in index_source, "index.html should include Book 3 in its card data.")
    assert_true("Grand Master Series" in index_source, "index.html should list the Grand Master preview row.")
    assert_true("New Order Series" in index_source, "index.html should list the New Order preview row.")
    assert_true("The Plague Lords of Ruel" in index_source, "index.html should include Book 13.")
    assert_true("The Storms of Chai" in index_source, "index.html should include Book 29.")
    assert_true("lw29.jpg" in index_source, "index.html should use the local Book 29 cover.")
    assert_true("projectaon.org/staff/otoole/Covers" not in index_source, "index.html should not depend on remote cover art.")
    assert_true("footer: 'Coming'" in index_source and "Coming Soon" not in index_source, "index.html should use the short Coming footer.")
    assert_true(
        "assets/images/title-banners/title1.png" in index_source,
        "index.html should include the default local Lone Wolf title banner.",
    )
    assert_true(
        "data-lw-title-banner" in index_source,
        "index.html should let the shared settings script swap title banners.",
    )
    assert_true(
        "assets/js/lw-settings.js" in index_source,
        "index.html should load the shared settings script.",
    )
    assert_true(
        "Settings" in index_source and "settingsModal" in index_source,
        "index.html should expose the settings modal from the Reader panel.",
    )
    assert_true(
        "reader-panel" in index_source
        and "grid-template-columns: clamp(260px, 16vw, 340px) minmax(0, 1fr)" in index_source
        and "container.style.setProperty('--book-count', seriesBooks.length)" in index_source,
        "index.html should keep Reader tools in their own left column while the Kai row stays book-only.",
    )
    assert_true("const loreLines" in index_source, "index.html should rotate the hero lore line.")
    assert_true(
        "assistant.html?book=${book.number}" in index_source,
        "index.html should generate assistant links for book cards.",
    )
    assert_true(
        "<strong>${book.title}</strong>" in index_source
        and "<strong>${book.number}. ${book.title}</strong>" not in index_source,
        "index.html should not repeat the book number before home card titles.",
    )
    assert_true("assistant.html?book=1" in library_source, "library.html should link Book 1 to the assistant.")
    assert_true("assistant.html?book=2" in library_source, "library.html should link Book 2 to the assistant.")
    assert_true("assistant.html?book=3" in library_source, "library.html should link Book 3 to the assistant.")
    assert_true(
        "assets/js/lw-settings.js" in library_source,
        "library.html should load the shared settings script.",
    )

    print("Browser landing static smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

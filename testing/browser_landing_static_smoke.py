#!/usr/bin/env python3
"""Static checks for landing and library book listings."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_HTML = ROOT / "index.html"
LIBRARY_HTML = ROOT / "library.html"


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
        assert_true("LW01_Mongoose_Alberto_Del_Lago" in source, f"{source_name} should show Book 1 cover art.")
        assert_true("LW02_Mongoose_Alberto_Del_Lago" in source, f"{source_name} should show Book 2 cover art.")
        assert_true("LW03_Mongoose_Alberto_Del_Lago" in source, f"{source_name} should show Book 3 cover art.")

    assert_true("number: 1" in index_source, "index.html should include Book 1 in its card data.")
    assert_true("number: 2" in index_source, "index.html should include Book 2 in its card data.")
    assert_true("number: 3" in index_source, "index.html should include Book 3 in its card data.")
    assert_true("lone-wolf-logo.jpg" in index_source, "index.html should include the Lone Wolf logo banner.")
    assert_true("const loreLines" in index_source, "index.html should rotate the hero lore line.")
    assert_true(
        "assistant.html?book=${book.number}" in index_source,
        "index.html should generate assistant links for book cards.",
    )
    assert_true("assistant.html?book=1" in library_source, "library.html should link Book 1 to the assistant.")
    assert_true("assistant.html?book=2" in library_source, "library.html should link Book 2 to the assistant.")
    assert_true("assistant.html?book=3" in library_source, "library.html should link Book 3 to the assistant.")

    print("Browser landing static smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Smoke checks for save slot catalog helpers."""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = ROOT / "testing" / "tmp" / "save-slot-smoke"
sys.path.insert(0, str(ROOT))

import app_server  # noqa: E402


def assert_true(value: bool, label: str) -> None:
    if not value:
        raise AssertionError(label)


def main() -> int:
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)
    TMP_DIR.mkdir(parents=True)

    original_slot_dir = app_server.SAVE_SLOT_DIR
    app_server.SAVE_SLOT_DIR = TMP_DIR
    try:
        slots = app_server.public_save_slots()
        assert_true(len(slots) == 6, "There should be six save slots.")
        assert_true(all(not slot["Occupied"] for slot in slots), "Fresh save slots should be empty.")

        (TMP_DIR / "slot-2.json").write_text(
            json.dumps(
                {
                    "CurrentSection": 75,
                    "Character": {
                        "Name": "Slot Smoke",
                        "BookNumber": 2,
                        "EnduranceCurrent": 17,
                        "EnduranceMax": 24,
                    },
                    "Inventory": {"GoldCrowns": 33},
                }
            ),
            encoding="utf-8",
        )
        slot_two = app_server.save_slot_entry(2)
        assert_true(slot_two["Occupied"], "Slot 2 should be occupied.")
        assert_true(slot_two["Name"] == "Slot Smoke", "Slot 2 should expose the character name.")
        assert_true(slot_two["BookNumber"] == 2, "Slot 2 should expose the book number.")
        assert_true(slot_two["Section"] == 75, "Slot 2 should expose the section.")
        assert_true(slot_two["Endurance"] == "17/24", "Slot 2 should expose endurance.")
        assert_true(slot_two["GoldCrowns"] == 33, "Slot 2 should expose gold.")

        message = app_server.clear_save_slot(2)
        assert_true("Cleared save slot 2" in message, "clear_save_slot should report the cleared slot.")
        assert_true(not (TMP_DIR / "slot-2.json").exists(), "clear_save_slot should remove the slot file.")
    finally:
        app_server.SAVE_SLOT_DIR = original_slot_dir
        shutil.rmtree(TMP_DIR, ignore_errors=True)

    print("Save slots backend smoke passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

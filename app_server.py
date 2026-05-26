#!/usr/bin/env python3
"""HTTP app server for the Lone Wolf web assistant."""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import mimetypes
import os
import sys
import threading
import zipfile
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

import lonewolf_redux


ROOT = Path(__file__).resolve().parent
UI_PREFERENCES_FILE = ROOT / "data" / "ui-preferences.json"
STATE_LOCK = threading.RLock()
ASSISTANT = lonewolf_redux.LoneWolfReduxAssistant(save_dir=ROOT / "saves", data_dir=ROOT / "data")
LAST_OUTPUT = ""

UI_PREFERENCE_KEYS = {
    "lonewolf_redux.top.layout.v1",
    "lonewolf_redux.top.sizes.v1",
    "lonewolf_redux.sheet.layout.v1",
    "lonewolf_redux.sheet.sizes.v1",
}
UI_PREFERENCE_PREFIXES = (
    "lonewolf_redux.cards.layout.",
    "lonewolf_redux.cards.size.",
    "lonewolf_redux.cards.closed.",
    "lonewolf_redux.cards.labels.",
)


def capture_output(func) -> str:
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        func()
    return buffer.getvalue().strip()


def load_last_save() -> None:
    loaded_save = False
    try:
        if ASSISTANT.last_save_file.exists():
            path = ASSISTANT.last_save_file.read_text(encoding="utf-8").strip()
            if path and Path(path).exists():
                ASSISTANT.load_game(path, quiet=True)
                loaded_save = True
    except Exception:
        pass
    if loaded_save:
        return

    try:
        if lonewolf_redux.CURRENT_POSITION_FILE.exists():
            position = json.loads(lonewolf_redux.CURRENT_POSITION_FILE.read_text(encoding="utf-8"))
            book_number = int(position.get("book") or 1)
            section = int(position.get("section") or 1)
            if book_number in lonewolf_redux.BOOKS:
                max_section = lonewolf_redux.BOOKS[book_number]["MaxSection"]
                section = section if 1 <= section <= max_section else 1
                ASSISTANT.character["BookNumber"] = book_number
                ASSISTANT.state["CurrentSection"] = section
                ASSISTANT.record_section_visit()
    except Exception:
        pass


def public_save_entries() -> list[dict]:
    entries = []
    for entry in ASSISTANT.catalog_saves():
        clean = dict(entry)
        clean["Path"] = str(clean["Path"])
        entries.append(clean)
    return entries


def truthy(value) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def is_ui_preference_key(key: str) -> bool:
    return key in UI_PREFERENCE_KEYS or key.startswith(UI_PREFERENCE_PREFIXES)


def load_ui_preferences() -> dict:
    try:
        data = json.loads(UI_PREFERENCES_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"version": 1, "values": {}}
    values = data.get("values") if isinstance(data, dict) else {}
    if not isinstance(values, dict):
        values = {}
    clean = {
        str(key): str(value)
        for key, value in values.items()
        if is_ui_preference_key(str(key)) and len(str(value)) <= 50000
    }
    return {"version": 1, "values": clean}


def save_ui_preferences(payload: dict) -> dict:
    values = payload.get("values") if isinstance(payload, dict) else {}
    if not isinstance(values, dict):
        values = {}
    clean = {
        str(key): str(value)
        for key, value in values.items()
        if is_ui_preference_key(str(key)) and len(str(value)) <= 50000
    }
    data = {"version": 1, "values": clean}
    UI_PREFERENCES_FILE.parent.mkdir(parents=True, exist_ok=True)
    UI_PREFERENCES_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def export_save_bytes() -> tuple[str, bytes]:
    ASSISTANT.sync_achievements(save=False)
    ASSISTANT.write_current_position()
    name = lonewolf_redux.safe_file_name(
        f"{ASSISTANT.character.get('Name') or 'Lone Wolf'}-book{ASSISTANT.character.get('BookNumber') or 1}"
    )
    return f"{name}.json", json.dumps(ASSISTANT.state, indent=2).encode("utf-8")


def backup_saves_bytes() -> tuple[str, bytes]:
    ASSISTANT.save_game(quiet=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(ASSISTANT.save_dir.glob("*.json")):
            archive.write(path, f"saves/{path.name}")
        if UI_PREFERENCES_FILE.exists():
            archive.write(UI_PREFERENCES_FILE, "data/ui-preferences.json")
    return f"LoneWolfRedux-saves-{stamp}.zip", buffer.getvalue()


def import_save_payload(payload: dict) -> str:
    raw = str(payload.get("raw") or "").strip()
    if not raw:
        raise ValueError("No save data supplied.")
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Save import must be a JSON object.")
    imported = lonewolf_redux.normalize_state(data)
    ASSISTANT.state = imported
    ASSISTANT.settings["SavePath"] = ""
    ASSISTANT.record_section_visit()
    ASSISTANT.ensure_current_section_checkpoint()
    ASSISTANT.sync_achievements(save=False)
    ASSISTANT.write_current_position()
    if truthy(payload.get("save", True)):
        ASSISTANT.save_game(quiet=True)
    return (
        f"Imported save for {ASSISTANT.character.get('Name') or 'Lone Wolf'}, "
        f"Book {ASSISTANT.character.get('BookNumber')}, section {ASSISTANT.state.get('CurrentSection')}."
    )


def state_payload(message: str = "", achievement_unlocks: list[dict] | None = None) -> dict:
    new_unlocks = ASSISTANT.sync_achievements(save=False)
    if new_unlocks:
        ASSISTANT.save_game(quiet=True)
    state = json.loads(json.dumps(ASSISTANT.state))
    state["Combat"] = ASSISTANT.combat_status_payload()
    for key in ("LesserMagicks", "HigherMagicks", "WillpowerBase", "WillpowerCurrent"):
        state.get("Character", {}).pop(key, None)
    for key in ("HasHerbPouch", "HerbPouchItems", "Nobles"):
        state.get("Inventory", {}).pop(key, None)
    for key in ("UseStaff", "StaffWillpower"):
        state.get("Combat", {}).pop(key, None)
    for checkpoint in lonewolf_redux.as_list(state.get("Automation", {}).get("SectionCheckpoints")):
        if isinstance(checkpoint, dict):
            checkpoint.pop("Snapshot", None)
    return {
        "books": lonewolf_redux.BOOKS,
        "state": state,
        "sectionFlow": ASSISTANT.current_section_flow_payload(),
        "death": ASSISTANT.death_recovery_payload(),
        "bookComplete": ASSISTANT.book_completion_payload(),
        "achievements": ASSISTANT.achievement_payload(),
        "achievementUnlocks": achievement_unlocks or [],
        "saves": public_save_entries(),
        "uiPreferences": load_ui_preferences(),
        "paths": {
            "SaveDir": str(ASSISTANT.save_dir),
            "DataDir": str(ASSISTANT.data_dir),
            "UiPreferences": str(UI_PREFERENCES_FILE),
        },
        "message": message,
        "lastOutput": LAST_OUTPUT,
    }


def book_files_payload() -> dict:
    books = []
    for number, meta in sorted(lonewolf_redux.BOOKS.items()):
        folder = str(meta.get("Folder") or "")
        root = ROOT / "books" / "lw" / folder
        title_file = root / "title.htm"
        first_section = root / "sect1.htm"
        books.append(
            {
                "BookNumber": number,
                "Title": meta.get("Title"),
                "Folder": folder,
                "Installed": title_file.exists() and first_section.exists(),
                "ExpectedTitleFile": str(title_file),
                "ExpectedFirstSection": str(first_section),
            }
        )
    return {
        "Installed": all(book["Installed"] for book in books),
        "Books": books,
        "InstallGuide": "/install-books.html",
    }


def apply_new_game(payload: dict) -> str:
    name = str(payload.get("name") or "Lone Wolf").strip() or "Lone Wolf"
    disciplines = payload.get("kaiDisciplines")
    if not isinstance(disciplines, list):
        disciplines = lonewolf_redux.KAI_DISCIPLINES[:5]

    ASSISTANT.state = lonewolf_redux.create_book1_character_state(
        name=name,
        kai_disciplines=disciplines,
        section=int(payload.get("section") or 1),
        combat_skill_roll=payload.get("combatSkillRoll"),
        endurance_roll=payload.get("enduranceRoll"),
        gold_roll=payload.get("goldRoll"),
        starting_find_roll=payload.get("startingFindRoll"),
        weaponskill_roll=payload.get("weaponskillRoll"),
    )
    ASSISTANT.record_section_visit()
    ASSISTANT.save_section_checkpoint("ready")
    ASSISTANT.write_current_position()
    ASSISTANT.autosave()
    return f"Created {name}, Book 1."


def handle_action(payload: dict) -> str:
    action = str(payload.get("action") or "").strip()
    if not action:
        return "No action supplied."

    if action == "new":
        return apply_new_game(payload)
    if action == "set_position":
        book = payload.get("book")
        section = int(payload.get("section") or 1)
        if book:
            return capture_output(lambda: ASSISTANT.set_book(int(book), section))
        return capture_output(lambda: ASSISTANT.set_section(section))
    if action == "apply_automation":
        return capture_output(lambda: ASSISTANT.apply_current_section_automation())
    if action == "roll":
        raw = payload.get("raw")
        raw_roll = int(raw) if str(raw or "").strip() else None
        result = ASSISTANT.roll_current_section(raw_roll)
        route = result.get("Route")
        route_text = f" -> section {route}" if route else ""
        messages = [f"Roll {result['Raw']} total {result['Total']}{route_text}"]
        for message in result.get("ActionMessages") or []:
            messages.append(str(message))
        return "\n".join(messages)
    if action == "route":
        return capture_output(lambda: ASSISTANT.follow_route(int(payload.get("section") or 1)))
    if action == "flow_loot":
        return capture_output(lambda: ASSISTANT.apply_flow_loot(str(payload.get("id") or "")))
    if action == "healing":
        return capture_output(lambda: ASSISTANT.apply_healing())
    if action == "section_loss":
        return capture_output(
            lambda: ASSISTANT.apply_section_loss(
                str(payload.get("id") or ""),
                str(payload.get("type") or ""),
                str(payload.get("item") or payload.get("slot") or ""),
            )
        )
    if action == "status_flag":
        return capture_output(lambda: ASSISTANT.set_status_flag(str(payload.get("key") or ""), payload.get("value")))
    if action == "wp_cost":
        return "Book 1 has no action for that stat."
    if action == "section_combat_start":
        return capture_output(lambda: ASSISTANT.start_section_combat(str(payload.get("id") or "")))
    if action == "adjust":
        stat = str(payload.get("stat") or "")
        mode = str(payload.get("mode") or "delta")
        value = int(payload.get("value") or 0)
        token = ["x", "set", str(value)] if mode == "set" else ["x", str(value)]
        if stat == "wp":
            return "Book 1 has no action for that stat."
        if stat == "end":
            return capture_output(lambda: ASSISTANT.adjust_endurance(token))
        if stat == "cs":
            return capture_output(lambda: ASSISTANT.adjust_combat_skill(token))
        if stat in {"gold", "nobles"}:
            return capture_output(lambda: ASSISTANT.adjust_nobles(token))
    if action == "add_item":
        return capture_output(lambda: ASSISTANT.add_item(["add", str(payload.get("type") or ""), str(payload.get("item") or "")]))
    if action == "drop_item":
        return capture_output(lambda: ASSISTANT.drop_item(["drop", str(payload.get("type") or ""), str(payload.get("item") or "")]))
    if action == "use_item":
        return capture_output(lambda: ASSISTANT.use_item(str(payload.get("type") or ""), str(payload.get("item") or "")))
    if action == "karmo_side_effect":
        raw = payload.get("raw")
        raw_roll = int(raw) if str(raw or "").strip() else None
        return capture_output(lambda: ASSISTANT.apply_karmo_side_effect(raw_roll))
    if action == "karmo_finish":
        return capture_output(lambda: ASSISTANT.finish_karmo_potion())
    if action == "death_recovery":
        return capture_output(lambda: ASSISTANT.restore_death_checkpoint(str(payload.get("mode") or "repeat")))
    if action == "meal":
        tokens = ["meal", "missed"] if payload.get("missed") else ["meal"]
        return capture_output(lambda: ASSISTANT.meal_command(tokens))
    if action == "power":
        return capture_output(
            lambda: ASSISTANT.power_command(
                ["power", str(payload.get("mode") or "add"), str(payload.get("name") or "")]
            )
        )
    if action == "note":
        return capture_output(lambda: ASSISTANT.note_command(["note", str(payload.get("text") or "")]))
    if action == "save":
        return capture_output(lambda: ASSISTANT.save_game(str(payload.get("path") or "")))
    if action == "load":
        return capture_output(lambda: ASSISTANT.load_game(str(payload.get("path") or "")))
    if action == "reload_last_save":
        load_last_save()
        return "Reloaded the latest save from disk."
    if action == "import_save":
        return import_save_payload(payload)
    if action == "complete_book":
        def complete() -> None:
            summary = ASSISTANT.ensure_book_completed(save=True)
            print(f"Book {summary['BookNumber']} complete: {summary['BookTitle']}.")
        return capture_output(complete)
    if action == "continue_book":
        return "No later books are enabled in this Book 1 rebuild yet."
    if action == "repeat_book":
        return capture_output(lambda: ASSISTANT.repeat_completed_book())
    if action == "combat_start":
        name = str(payload.get("name") or "Enemy")
        cs = int(payload.get("cs") or 10)
        end = int(payload.get("endurance") or 10)
        def start() -> None:
            ASSISTANT.start_combat(["combat", "start", name, str(cs), str(end)])
            if ASSISTANT.combat.get("Active"):
                if "activeWeapon" in payload:
                    ASSISTANT.set_combat_weapon(str(payload.get("activeWeapon") or ""), save=False)
                ASSISTANT.combat["Modifier"] = int(payload.get("modifier") or 0)
                ASSISTANT.combat["StaffWillpower"] = 0
                ASSISTANT.combat["UseStaff"] = False
                ASSISTANT.combat["CanEvade"] = truthy(payload.get("canEvade"))
                ASSISTANT.combat["EvadeAfterRounds"] = max(0, int(payload.get("evadeAfterRounds") or 0))
                victory_route = payload.get("victoryRoute")
                evade_route = payload.get("evadeRoute")
                ASSISTANT.combat["VictoryRoute"] = int(victory_route) if str(victory_route or "").strip() else None
                ASSISTANT.combat["EvadeRoute"] = int(evade_route) if str(evade_route or "").strip() else None
                ASSISTANT.autosave()
        return capture_output(start)
    if action == "combat_round":
        if "activeWeapon" in payload:
            ASSISTANT.set_combat_weapon(str(payload.get("activeWeapon") or ""), save=False)
        ASSISTANT.combat["UseStaff"] = False
        tokens = ["combat", "evade" if payload.get("evade") else "round"]
        if payload.get("wp"):
            tokens.append(str(payload.get("wp")))
        if payload.get("roll") not in (None, ""):
            tokens.append(str(payload.get("roll")))
        return capture_output(lambda: ASSISTANT.combat_round(tokens, evade=bool(payload.get("evade"))))
    if action == "combat_auto":
        return capture_output(lambda: ASSISTANT.resolve_combat_to_outcome())
    if action == "combat_evade":
        if "activeWeapon" in payload:
            ASSISTANT.set_combat_weapon(str(payload.get("activeWeapon") or ""), save=False)
        ASSISTANT.combat["UseStaff"] = False
        tokens = ["combat", "evade"]
        if payload.get("wp"):
            tokens.append(str(payload.get("wp")))
        if payload.get("roll") not in (None, ""):
            tokens.append(str(payload.get("roll")))
        return capture_output(lambda: ASSISTANT.evade_combat(tokens))
    if action == "combat_weapon":
        return capture_output(lambda: ASSISTANT.set_combat_weapon(str(payload.get("activeWeapon") or "")))
    if action == "combat_stop":
        return capture_output(lambda: ASSISTANT.stop_combat())
    if action == "autosave":
        ASSISTANT.settings["AutoSave"] = True
        ASSISTANT.save_game(quiet=True)
        return "Autosave is always on."

    return f"Unknown action: {action}"


class LoneWolfReduxHandler(BaseHTTPRequestHandler):
    server_version = "LoneWolfReduxHTTP/0.1"

    def log_message(self, format: str, *args) -> None:  # noqa: A003
        return

    def send_json(self, data: dict, status: int = 200) -> None:
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_download(self, filename: str, data: bytes, content_type: str) -> None:
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/api/state":
            with STATE_LOCK:
                self.send_json(state_payload())
            return
        if parsed.path == "/api/saves":
            with STATE_LOCK:
                self.send_json({"saves": public_save_entries()})
            return
        if parsed.path == "/api/ui-preferences":
            with STATE_LOCK:
                self.send_json(load_ui_preferences())
            return
        if parsed.path == "/api/book-files":
            self.send_json(book_files_payload())
            return
        if parsed.path == "/api/export-save":
            with STATE_LOCK:
                filename, data = export_save_bytes()
                self.send_download(filename, data, "application/json; charset=utf-8")
            return
        if parsed.path == "/api/backup-saves":
            with STATE_LOCK:
                filename, data = backup_saves_bytes()
                self.send_download(filename, data, "application/zip")
            return
        self.serve_static(parsed.path)

    def do_POST(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path not in {"/api/action", "/api/ui-preferences"}:
            self.send_json({"error": "Not found"}, HTTPStatus.NOT_FOUND)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8") or "{}")
        except json.JSONDecodeError:
            self.send_json({"error": "Invalid JSON"}, HTTPStatus.BAD_REQUEST)
            return
        if parsed.path == "/api/ui-preferences":
            with STATE_LOCK:
                self.send_json(save_ui_preferences(payload))
            return

        global LAST_OUTPUT
        with STATE_LOCK:
            try:
                action_name = str(payload.get("action") or "").strip()
                before_unlocks = ASSISTANT.achievement_unlocked_ids()
                if action_name == "shutdown":
                    ASSISTANT.save_game(quiet=True)
                    message = "Lone Wolf assistant server is shutting down."
                    LAST_OUTPUT = message
                    self.send_json(state_payload(message=message))
                    threading.Thread(target=self.server.shutdown, daemon=True).start()
                    return
                message = handle_action(payload)
                ASSISTANT.sync_achievements(save=False)
                after_unlocks = [
                    entry
                    for entry in lonewolf_redux.as_list(ASSISTANT.achievement_state().get("Unlocked"))
                    if isinstance(entry, dict) and str(entry.get("Id") or "") not in before_unlocks
                ]
                if after_unlocks:
                    ASSISTANT.save_game(quiet=True)
                if action_name in {"load", "save", "autosave"}:
                    after_unlocks = []
                LAST_OUTPUT = message
                self.send_json(state_payload(message=message, achievement_unlocks=after_unlocks))
            except Exception as exc:
                LAST_OUTPUT = str(exc)
                self.send_json({"error": str(exc), **state_payload(message=str(exc))}, HTTPStatus.BAD_REQUEST)

    def serve_static(self, raw_path: str) -> None:
        relative = unquote(raw_path.lstrip("/")) or "index.html"
        target = (ROOT / relative).resolve()
        try:
            target.relative_to(ROOT)
        except ValueError:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if target.is_dir():
            target = target / "index.html"
        if not target.exists() or not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = mimetypes.guess_type(str(target))[0] or "application/octet-stream"
        data = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> int:
    parser = argparse.ArgumentParser(description="Lone Wolf web app server")
    parser.add_argument("--host", default="localhost")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("LONEWOLF_REDUX_HTTP_PORT", "8797")),
    )
    args = parser.parse_args()

    load_last_save()
    server = ThreadingHTTPServer((args.host, args.port), LoneWolfReduxHandler)
    print(f"Lone Wolf web app: http://{args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

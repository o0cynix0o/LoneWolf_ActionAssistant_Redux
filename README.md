# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is a local browser-based play aid for the *Lone Wolf* gamebooks. We built it to sit beside your own Project Aon book files and take care of the fiddly Action Chart work: character bookkeeping, section support, combat tracking, saves, achievements, and strategy-guide material.

This repository is the clean AA2 rebuild of the earlier Lone Wolf assistant. It uses the proven Grey Star Action Assistant workflow as a project template, but the rules, book data, automation, tests, and player docs are rebuilt around Lone Wolf.

Current status: **Book 1 playable release candidate**

## Book Files Are Not Included

This project does **not** redistribute Project Aon book HTML files. Bring your own standard Project Aon HTML editions for personal use and place them under:

```text
books\lw
```

The current supported local book folder is:

```text
books\lw\01fftd
```

Full walkthrough:

- `docs/INSTALL_PROJECT_AON_BOOKS.md`
- local app page: `http://127.0.0.1:8797/install-books.html`

Project Aon links:

- License: https://www.projectaon.org/en/Main/License
- Flight from the Dark: https://www.projectaon.org/en/Main/FlightFromTheDark
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip

## What It Includes

- Book 1 support for *Flight from the Dark*.
- Book 2 setup/start-state and source-link route support for *Fire on the Water*; section automation is still in the pipeline.
- Split view with the book reader on the left and the assistant on the right, once the Project Aon book files are installed locally.
- Book 1 character creation from the rules:
  - Combat Skill = random digit + 10
  - Endurance = random digit + 20
  - exactly five Kai Disciplines
  - Weaponskill random weapon mapping
  - Axe, Backpack with one Meal, Map of Sommerlund, Gold Crown roll, and monastery-find roll
- Lone Wolf Action Chart fields for Combat Skill, Endurance, Kai Disciplines, Weapons, Backpack Items, Special Items, Meals, and Gold Crowns.
- Book 1 source-link route data from the local `sect*.htm` files.
- Audited section helpers for Meals, Endurance changes, Gold changes, item gain/loss, route checks, random helpers, combat presets, death recovery, book completion, and achievements.
- Expandable notification receipts that explain recent automation, item use, combat, recovery, and achievement changes.
- Save export, save import, and full save backup.
- Persistent card layout and size preferences.
- Three play modes: Auto, Manual, and CLI.
- Player-facing wiki scaffold and Book 1 strategy material.
- Agent handoff docs for continuing the rebuild in a fresh chat.

## Current Limitations

- Book 1 is the first supported book and is being prepared as the first public prerelease package.
- Book 2 can be set up from Book 1 completion or as a fresh Book 2 start, and its source-link section routes are available. Book 2 section automation, combat presets, achievements, and guide material are not playable yet.
- Book 3 and later are not supported yet.
- Later books must be onboarded through `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` before they are treated as playable.

## Quick Start

Install dependencies from the project folder:

```powershell
python -m pip install -r .\requirements.txt
```

Start the app:

```powershell
.\Launch-LoneWolfRedux.ps1
```

Or:

```powershell
python .\launch_lonewolf_redux.py
```

Then open:

```text
http://127.0.0.1:8797/assistant.html
```

Use the local server address. Opening `assistant.html` directly from the file system can break local book paths.

If this is a fresh checkout, open the book install guide first:

```text
http://127.0.0.1:8797/install-books.html
```

## Play Modes

Use the small white dot in the upper-right of the assistant panel to switch modes.

- **Auto Mode** is the normal helper mode. Section effects, section-aware rolls, loot helpers, combat presets, saves, death recovery, and achievements are available.
- **Manual Mode** keeps the sheet, saves, inventory, notes, and achievements, but disables audited section automation. Use it when you want to do the book math yourself.
- **CLI Mode** replaces the normal assistant body with the terminal assistant inside the web page. It uses the same save data as the web GUI.

Default ports:

- Library and web app: `http://127.0.0.1:8797`
- Embedded CLI bridge: `ws://127.0.0.1:8798`

## Basic Play Flow

1. Start the app from PowerShell.
2. Open the assistant page from the local server address.
3. Create or load a Lone Wolf character.
4. Read the book in the left pane.
5. Click book section links normally; the assistant follows your current section.
6. Use the assistant panels for inventory, stats, combat, rolls, notes, saves, and achievements.
7. When Book 1 ends, use the completion screen to review the result. Later-book transitions are future pipeline work.

## Saves And Backups

Use the **Saves** tab for:

- **Export Current Save**: download the current character as JSON.
- **Import Selected Save**: load an exported save into this install.
- **Backup All Saves**: download every local save in one ZIP.

Runtime save data is intentionally local and ignored by git:

- `saves/`
- `current-position.json`
- `data/last-save.txt`
- `data/ui-preferences.json`

## Documentation

Project docs live in `docs/`.

Useful starting points:

- `AGENT.md`
- `docs/AGENT_HANDOFF.md`
- `docs/LONE_WOLF_AA2_WORKFLOW.md`
- `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md`
- `docs/BOOK_AUDIT_WORKFLOW.md`
- `docs/BOOK_SOURCE_MAP.md`
- `docs/INSTALL_PROJECT_AON_BOOKS.md`
- `docs/PUBLIC_RELEASE_CHECKLIST.md`
- `docs/RELEASE_NOTES_V0.1.0-rc1.md`
- `docs/RELEASE_NOTES_PREALPHA.md`

Wiki source pages live in `docs/wiki/` and are mirrored to the GitHub wiki when publishing player-facing docs.

## Testing

Run the Book 1 release checks from the project folder:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
```

The granular Book 1 scripts live under `testing/`, and supporting audit reports live under `testing/logs/`.

## Release Package

Create a release ZIP from the current git commit:

```powershell
.\tools\Make-Release.ps1
```

The ZIP is written to `dist/`. Runtime saves, UI preferences, the local wiki checkout, and local Project Aon book files are not included.

Before publishing a package, run the public release checklist and smoke-test the ZIP from a fresh extracted folder.

## Project Layout

- `assistant.html`: web assistant UI.
- `index.html`: local book library entry page.
- `install-books.html`: local book install guide page.
- `app_server.py`: HTTP server and JSON API for the web assistant.
- `lonewolf_redux.py`: terminal assistant and shared Lone Wolf rules logic.
- `ws_server.py`: WebSocket bridge for embedded CLI mode.
- `launch_lonewolf_redux.py`: Python launcher for the web app and CLI bridge.
- `Launch-LoneWolfRedux.ps1`: Windows convenience launcher.
- `books/`: local book install folder. Project Aon book files go under `books/lw/` but are ignored by git and not included in release ZIPs.
- `data/book1-section-flows.json`: Book 1 route, helper, combat, and roll data.
- `data/book2-section-flows.json`: Book 2 source-link route baseline.
- `data/book1-simple-automations.json`: Book 1 simple section automation data.
- `data/book-route-checks.json`: route-check helper data.
- `data/crt.json`: Combat Results Table.
- `testing/`: route, automation, combat, achievement, and book playtest checks.
- `testing/logs/`: technical audit reports and playtest reports.
- `tools/Make-Release.ps1`: release ZIP builder.

## Notice

This is an unofficial local play aid. It does not redistribute the Lone Wolf books. Users download the Project Aon Internet Editions directly from Project Aon for personal use. See `NOTICE.md`.

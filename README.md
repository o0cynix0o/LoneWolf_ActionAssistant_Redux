# Lone Wolf Action Assistant Redux

Lone Wolf Action Assistant Redux is a local browser-based play aid for the *Lone Wolf* gamebooks. We built it to sit beside your own Project Aon book files and take care of the fiddly Action Chart work: character bookkeeping, section support, combat tracking, saves, achievements, and strategy-guide material.

This repository is the clean AA2 rebuild of the earlier Lone Wolf assistant. It uses the proven Grey Star Action Assistant workflow as a project template, but the rules, book data, automation, tests, and player docs are rebuilt around Lone Wolf.

Current status: **Book 1 playable release candidate; Books 2-5 playable helper/onboarding builds**

## Book Files Are Not Included

This project does **not** redistribute Project Aon book HTML files. Bring your own standard Project Aon HTML editions for personal use and place them under:

```text
books\lw
```

The currently supported local book folders are:

```text
books\lw\01fftd
books\lw\02fotw
books\lw\03tcok
books\lw\04tcod
books\lw\05sots
```

Full walkthrough:

- `docs/INSTALL_PROJECT_AON_BOOKS.md`
- local app page: `http://127.0.0.1:8797/install-books.html`

Project Aon links:

- License: https://www.projectaon.org/en/Main/License
- Flight from the Dark: https://www.projectaon.org/en/Main/FlightFromTheDark
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/01fftd/01fftd.zip
- Fire on the Water: https://www.projectaon.org/en/Main/FireOnTheWater
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/02fotw/02fotw.zip
- The Caverns of Kalte: https://www.projectaon.org/en/Main/TheCavernsOfKalte
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/03tcok/03tcok.zip
- The Chasm of Doom: https://www.projectaon.org/en/Main/TheChasmOfDoom
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/04tcod/04tcod.zip
- Shadow on the Sand: https://www.projectaon.org/en/Main/ShadowOnTheSand
- Standard HTML ZIP: https://www.projectaon.org/en/xhtml/lw/05sots/05sots.zip

## What It Includes

- Book 1 support for *Flight from the Dark*.
- Book 2 support for *Fire on the Water*, including setup, routes, section helpers, combat presets, deaths, completion, and achievements.
- Book 3 support for *The Caverns of Kalte*, including setup, routes, first helper coverage, combat presets, death/failure handling, completion, and repeat-book replay.
- Book 4 support for *The Chasm of Doom*, including setup, routes, first helper coverage, combat presets, death handling, completion, and repeat-book replay.
- Book 5 support for *Shadow on the Sand*, including setup, safekeeping, routes, first helper coverage, combat presets, death/failure handling, completion, and repeat-book replay.
- Split view with the book reader on the left and the assistant on the right, once the Project Aon book files are installed locally.
- Book 1 character creation from the rules:
  - Combat Skill = random digit + 10
  - Endurance = random digit + 20
  - exactly five Kai Disciplines
  - Weaponskill random weapon mapping
  - Axe, Backpack with one Meal, Map of Sommerlund, Gold Crown roll, and monastery-find roll
- Lone Wolf Action Chart fields for Combat Skill, Endurance, Kai Disciplines, Weapons, Backpack Items, Special Items, Meals, and Gold Crowns.
- Book 1 through Book 5 source-link route data from the local `sect*.htm` files.
- Audited section helpers for Meals, Endurance changes, Gold changes, item gain/loss, route checks, random helpers, combat presets, death recovery, book completion, and achievements.
- Campaign carry-forward support, including durable safekeeping for Book 5 and later Special Items stored away from the active Action Chart.
- Expandable notification receipts that explain recent automation, item use, combat, recovery, and achievement changes.
- Save export, save import, and full save backup.
- Persistent card layout and size preferences.
- Three play modes: Auto, Manual, and CLI.
- Player-facing wiki scaffold plus Book 1 and Book 2 strategy material.
- Agent handoff docs for continuing the rebuild in a fresh chat.

## Current Limitations

- Book 1 has had the most table time and remains the first public prerelease target.
- Book 2 has the playable helper set in place, but still needs more real-route time before we package it as a public release.
- Books 3, 4, and 5 are onboarding helper builds. They are ready for playtesting, but still need wider route time, achievement passes, and strategy-guide polish before release packaging.
- Book 6 and later must be onboarded through `docs/LONE_WOLF_BOOK_PIPELINE_WORKFLOW.md` before they are treated as playable.

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
7. When Book 1 ends, use the completion screen to continue into Book 2 or start Book 2 fresh from the new-character flow.

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

Run the release checks from the project folder:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
python .\testing\playtest_book2.py
python .\testing\playtest_book3.py
python .\testing\playtest_book4.py
python .\testing\playtest_book5.py
```

The granular per-book scripts live under `testing/`, and supporting audit reports live under `testing/logs/`.

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
- `data/book2-section-flows.json`: Book 2 route, helper, combat, and roll data.
- `data/book3-section-flows.json`: Book 3 route, helper, combat, and roll data.
- `data/book4-section-flows.json`: Book 4 route, helper, combat, and roll data.
- `data/book5-section-flows.json`: Book 5 route, helper, combat, and roll data.
- `data/book1-simple-automations.json`: Book 1 simple section automation data.
- `data/book2-simple-automations.json`: Book 2 simple section automation data.
- `data/book3-simple-automations.json`: Book 3 simple section automation data.
- `data/book4-simple-automations.json`: Book 4 simple section automation data.
- `data/book5-simple-automations.json`: Book 5 simple section automation data.
- `data/book-route-checks.json`: route-check helper data.
- `data/crt.json`: Combat Results Table.
- `testing/`: route, automation, combat, achievement, and book validation checks.
- `testing/logs/`: technical audit and validation reports.
- `tools/Make-Release.ps1`: release ZIP builder.

## Notice

This is an unofficial local play aid. It does not redistribute the Lone Wolf books. Users download the Project Aon Internet Editions directly from Project Aon for personal use. See `NOTICE.md`.

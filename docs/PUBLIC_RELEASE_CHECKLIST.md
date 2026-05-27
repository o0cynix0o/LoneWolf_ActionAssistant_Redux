# Public Release Checklist

Use this before tagging or uploading a public build.

Current release state: **Book 1 playable local pre-alpha**. Do not package or publish a public release until the manual browser ergonomics pass has been completed and release approval is explicit.

## Clean Start

1. Clone or unzip the project into a fresh folder.
2. Install dependencies:

   ```powershell
   python -m pip install -r .\requirements.txt
   ```

3. Start the app:

   ```powershell
   .\Launch-LoneWolfRedux.ps1
   ```

4. Install the Project Aon book files by following `docs/INSTALL_PROJECT_AON_BOOKS.md`.
5. Open `http://127.0.0.1:8797/assistant.html`.

## Smoke Test

1. Create a new Book 1 character.
2. Confirm the book pane and assistant pane both load.
3. Confirm the character sheet shows Combat Skill, Endurance, Kai Disciplines, Weapons, Backpack Items, Special Items, Meals, and Gold Crowns.
4. Change one card size, close the server, restart it, and confirm the card size sticks.
5. Add and drop a test item.
6. Use Save Now.
7. Export the current save.
8. Backup all saves.
9. Import the exported save and confirm it loads.
10. Play through at least one combat section in the browser.
11. Confirm a death/recovery path and Book 1 completion path behave correctly.

## Automated Checks

Run:

```powershell
python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py
python .\testing\playtest_book1.py
```

Expected result: the Book 1 aggregate playtest reports zero failures.

The aggregate wrapper currently covers the granular Book 1 checks for section flow, simple automation, healing/loss behavior, player-choice aftermath, random/recovery behavior, staged rolls, route/random helpers, combat, branch play, route gauntlet play, end-to-end play, and achievements.

## Manual Browser Pass

Before public release, verify:

- new-character modal behavior
- source-link navigation in the book pane
- assistant follow behavior when clicking section links
- combat start, combat rounds, evasion, victory routing, and defeat handling
- route-check display and route result clarity
- receipt drawer readability
- save/load/export/import/backup workflow
- responsive card layout at ordinary desktop and smaller browser widths
- Book 1 completion screen
- app restart recovery from an existing save

Record the result in `testing/logs/LWBOOK1_PLAYTEST_REPORT.md` or a newer release-readiness log before packaging.

## Package

Create the release ZIP only after release approval:

```powershell
.\tools\Make-Release.ps1
```

The package is written to `dist/`. Runtime files such as saves, current position, UI preferences, the local wiki checkout, and Project Aon book files are not included.

Confirm the package does not include Project Aon book files:

```powershell
git ls-files books/lw
```

Expected result: no output.

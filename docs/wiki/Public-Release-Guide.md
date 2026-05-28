# Public Release Guide

This page is the release-readiness checklist for a fresh install. It is the friendly version of our maintainer checklist: make sure the app starts cleanly, make sure the books are still user-installed, and make sure nothing personal sneaks into the package.

Book 1 is the current release candidate. Keep packaging honest: run the checks, smoke-test a fresh ZIP, and only publish a build that feels good to actually play.

## Start

From the project folder:

```powershell
.\Launch-LoneWolfRedux.ps1
```

Then open:

```text
http://127.0.0.1:8797/assistant.html
```

## Install The Books

The release ZIP must not include Project Aon book files.

Download the standard Lone Wolf HTML ZIPs from Project Aon for personal use, then extract them into `books\lw`.

Use the local guide page:

```text
http://127.0.0.1:8797/install-books.html
```

Or read:

```text
docs\INSTALL_PROJECT_AON_BOOKS.md
```

## Keep Your Progress Safe

The app autosaves during play. You can also use the **Saves** tab for three useful tools:

- **Export Current Save** downloads the current character as one JSON file.
- **Backup All Saves** downloads a ZIP of local save files and UI layout preferences.
- **Import Selected Save** loads a previously exported save JSON into this installation.

Use **Backup All Saves** before moving the app to another folder or computer.

## UI Layouts

Card sizes, card order, and closed cards are stored in `data/ui-preferences.json`. They should survive server restarts.

If the layout gets strange, open **Settings** and use **Reset All Card Layouts**.

## Before Packaging

Before packaging a release:

- record the manual browser run result
- confirm new character flow, saves, imports, route buttons, loot, combat, death recovery, and achievements in the browser
- confirm Book 1 files are not packaged
- confirm personal saves are not packaged
- confirm `books` remains ignored by git

## Package A Release

For maintainers, after release-readiness is confirmed:

```powershell
.\tools\Make-Release.ps1
```

The release ZIP appears in `dist`. It should contain the app and docs, not personal saves and not Project Aon book files.

## Credits Note

Project Aon provides the Lone Wolf Internet Editions from its own site. This assistant is an unofficial local companion for playing those books after the user has downloaded them for personal use.

# Getting Started

This project is the Book 1 release-candidate build of Lone Wolf Action Assistant Redux, with Books 2-5 now available as playable helper builds. We are keeping the app local, practical, and faithful to the book text.

## Requirements

- Python 3
- A modern browser
- The project files from the repository
- Your own Project Aon Book 1 HTML files
- Your own Project Aon Book 2-5 HTML files if you want to continue through the Kai series

Install Python dependencies from the project folder if needed:

```powershell
python -m pip install -r .\requirements.txt
```

## Start The App

From PowerShell:

```powershell
.\Launch-LoneWolfRedux.ps1
```

Or:

```powershell
python .\launch_lonewolf_redux.py
```

Then open the local server page:

```text
http://127.0.0.1:8797/assistant.html
```

## Install The Books

The release ZIP does not include Project Aon book files.

For Book 1, extract the Project Aon standard HTML files here:

```text
books\lw\01fftd
```

For Book 2, use:

```text
books\lw\02fotw
```

For Books 3-5, use:

```text
books\lw\03tcok
books\lw\04tcod
books\lw\05sots
```

The local guide page is:

```text
http://127.0.0.1:8797/install-books.html
```

The repo guide is:

```text
docs\INSTALL_PROJECT_AON_BOOKS.md
```

## Playing Book 1

Start a new Book 1 character from the assistant. The Book 1 sheet supports Combat Skill, Endurance, Kai Disciplines, Weapons, Backpack Items, Special Items, Meals, and Gold Crowns.

Use the assistant buttons when the current section offers them:

- route checks for Kai Discipline, item, Gold, or END branches
- loot buttons for optional items
- roll helpers for random-number sections
- combat presets for audited fights
- death recovery controls when a run ends badly

For practical route advice, see [Book 1 Strategy Guide](Book-1-Strategy-Guide).

## Starting Book 2

Book 2 has setup, checked routes, section helpers, combat presets, death recovery, completion, achievements, and a first strategy guide. You can continue from a completed Book 1 save or create a clearly labeled fresh Book 2 character.

The setup handles the new Kai Discipline, starting Gold with the 50 Crown cap, carry-over inventory from Book 1, the Seal of Hammerdal, the map, and Royal Armoury choices.

We still want more real-route time before calling Book 2 a public release candidate, so please treat it as ready to play and ready to report rough edges.

Books 3, 4, and 5 are playable onboarding helper builds with first-pass achievements and strategy pages. They are ready for real runs, but we still expect normal play to uncover labels, edge cases, and route polish we can improve.

## Choose A Play Mode

Use the small menu in the upper-right of the assistant panel to switch modes.

- **Auto** is the normal helper mode with section effects, roll helpers, loot helpers, combat presets, and achievements.
- **Manual** keeps the sheet and saves, but turns audited helpers into advice-only buttons so you can handle the book math yourself.
- **CLI** opens the terminal assistant inside the web page and uses the same save data.

## Important Browser Note

Use the local server URL. Opening `assistant.html` directly as a file can make the book open but leave the assistant disconnected.

Correct:

```text
http://127.0.0.1:8797/assistant.html
```

Risky:

```text
opening assistant.html directly from the file system
```

## Autosave

The app autosaves state during normal play. That is intentional. It protects the sheet, inventory, route history, combat history, achievements, and notes as you move through the book.

## Moving Saves

Use the **Saves** tab when you need to move or protect your run:

- **Export Current Save** downloads the current character.
- **Backup All Saves** downloads every local save in one ZIP.
- **Import Selected Save** loads an exported save JSON into this installation.

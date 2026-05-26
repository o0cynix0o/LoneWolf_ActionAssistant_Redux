# Agent Handoff: Lone Wolf Action Assistant Redux

This project is a one-time bootstrap from the Grey Star Action Assistant workflow into a new Lone Wolf AA2 repo.

## Start Here

The first playable target is **Book 1: Flight from the Dark**.

Local source:

```text
C:\Scripts\LoneWolf_ActionAssistant_Redux\books\lw\01fftd
```

Do not use Grey Star rules as the source of truth. Grey Star supplied the workflow, cards, receipts, layout system, and testing discipline. Lone Wolf rules must come from the local Project Aon Lone Wolf book files and the original Lone Wolf project.

## What Was Bootstrapped

- Web assistant shell from Grey Star.
- Launcher and local server skeleton.
- Release packaging script.
- Combat Results Table and Kai reference data from the old Lone Wolf project.
- Audit workflow from Grey Star.
- Empty Book 1 audit data placeholders.
- Wiki/docs skeleton.

## Known Scaffold Debt

The first issue pass replaced the visible Book 1 character creation and sheet model. The following debt remains for later passes:

- Grey Star combat exceptions.
- Book 2-4 Grey Star completion assumptions.
- Legacy compatibility code for older Grey Star-derived save fields.
- Book 1 route, section, and combat automation placeholders.

Do not paper over this by renaming labels only. Replace the underlying state and rules.

## First Validation Target

A successful first milestone is:

1. Start the local server.
2. Open `http://localhost:8797/assistant.html`.
3. Book 1 loads from `books\lw\01fftd`.
4. New character creation follows *Flight from the Dark* rules.
5. The sheet has correct Lone Wolf fields.
6. No Magicks/Willpower/Herb Pouch controls are visible.
7. `python -m py_compile app_server.py lonewolf_redux.py launch_lonewolf_redux.py ws_server.py` passes.

Issue #1 changed the default character model to Book 1 Kai rules:

- Combat Skill and Endurance use the Book 1 random digit formulas.
- New characters choose exactly five Kai Disciplines.
- Weaponskill rolls against the Book 1 weapon table.
- Starting gear is Axe, one Meal, Map of Sommerlund, Gold Crowns, plus the monastery-find roll.
- The web sheet now exposes Gold Crowns, Meals, Kai Disciplines, Weapons, Backpack Items, and Special Items.

## GitHub Workflow

Use the repo:

```text
https://github.com/o0cynix0o/LoneWolf_ActionAssistant_Redux
```

For every bug or task that changes behavior:

1. Open a GitHub issue.
2. Implement the fix.
3. Update docs/tests.
4. Commit with `Fixes #<issue>` when appropriate.
5. Push.
6. Package and publish a release only when the app is release-worthy.
7. Verify the issue and release state.

This bootstrap commit is not a public playable release.
